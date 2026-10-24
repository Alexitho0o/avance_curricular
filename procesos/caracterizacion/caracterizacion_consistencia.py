"""Primitivas auditables de consistencia para el flujo de caracterización.

Este módulo es deliberadamente independiente de los runners. Proporciona:

* una conciliación bipartita entre matrícula y tokens que conserva cada fila
  física de ambas fuentes;
* un validador acumulable de identidades KPI; y
* la semántica institucional del indicador de eliminados cuya fecha de
  matrícula pertenece a una ventana.

La unidad de la conciliación no mezcla personas, tokens y filas físicas: es un
``componente canónico`` del grafo que conecta la llave del estudiante con el
token. Las filas de origen se conservan como nodos propios, incluso cuando sus
llaves son nulas, para poder reconstruir exactamente ambas entradas.

Precedencia de categorías (la primera regla aplicable gana):

1. ``Conflicto de matrícula``: el componente no identifica de forma unívoca
   una fila vigente (llave de estudiante nula, más de una fila de matrícula,
   más de una llave de estudiante o más de un token de matrícula).
2. ``Token duplicado``: un token válido aparece en más de una fila física de
   la fuente de tokens, sin conflicto de matrícula de mayor precedencia.
3. ``Vigente con token``: existe una fila de matrícula unívoca y su token
   aparece en la fuente de tokens.
4. ``Vigente sin token``: existe una fila de matrícula unívoca, pero no hay
   token coincidente en la fuente de tokens.
5. ``Token sin matrícula``: el componente solo contiene filas de tokens.

Cada componente recibe exactamente una de estas cinco categorías. Los nulos
de la fuente de tokens no se agrupan artificialmente: cada fila nula conserva
su propio componente y queda auditada como ``Token sin matrícula``.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from numbers import Number
from typing import Any

import pandas as pd


CATEGORIA_VIGENTE_CON_TOKEN = "Vigente con token"
CATEGORIA_VIGENTE_SIN_TOKEN = "Vigente sin token"
CATEGORIA_TOKEN_SIN_MATRICULA = "Token sin matrícula"
CATEGORIA_TOKEN_DUPLICADO = "Token duplicado"
CATEGORIA_CONFLICTO_MATRICULA = "Conflicto de matrícula"

PRECEDENCIA_CATEGORIAS = (
    CATEGORIA_CONFLICTO_MATRICULA,
    CATEGORIA_TOKEN_DUPLICADO,
    CATEGORIA_VIGENTE_CON_TOKEN,
    CATEGORIA_VIGENTE_SIN_TOKEN,
    CATEGORIA_TOKEN_SIN_MATRICULA,
)

CATEGORIAS_CONCILIACION = frozenset(PRECEDENCIA_CATEGORIAS)

LEYENDA_ELIMINADOS_MATRICULA_VENTANA = (
    "Estudiantes actualmente eliminados cuya fecha de matrícula pertenece "
    "a la ventana evaluada."
)
ADVERTENCIA_ELIMINADOS_MATRICULA_VENTANA = "NO_ES_FECHA_ELIMINACION"


Normalizador = Callable[[Any], Any]


def normalizar_identificador(valor: Any) -> str | None:
    """Normaliza una llave de forma conservadora y convierte nulos en ``None``.

    Es el normalizador predeterminado. Los consumidores pueden inyectar uno
    institucional para CODCLI, RUT o token. El resultado final siempre se
    convierte a texto no vacío para que sea una llave estable del grafo.
    """

    if _es_nulo(valor):
        return None
    texto = str(valor).strip()
    if not texto or texto.casefold() in {"nan", "nat", "none", "<na>"}:
        return None
    return texto.casefold()


def _es_nulo(valor: Any) -> bool:
    if valor is None:
        return True
    try:
        resultado = pd.isna(valor)
    except (TypeError, ValueError):
        return False
    return isinstance(resultado, bool) and resultado


def _normalizar(valor: Any, normalizador: Normalizador) -> str | None:
    if _es_nulo(valor):
        return None
    normalizado = normalizador(valor)
    if _es_nulo(normalizado):
        return None
    texto = str(normalizado).strip()
    if not texto or texto.casefold() in {"nan", "nat", "none", "<na>"}:
        return None
    return texto


class _UnionFind:
    """Union-find mínimo para construir componentes de forma determinista."""

    def __init__(self) -> None:
        self.parent: dict[tuple[str, Any], tuple[str, Any]] = {}
        self.rank: dict[tuple[str, Any], int] = {}

    def add(self, node: tuple[str, Any]) -> None:
        if node not in self.parent:
            self.parent[node] = node
            self.rank[node] = 0

    def find(self, node: tuple[str, Any]) -> tuple[str, Any]:
        parent = self.parent[node]
        if parent != node:
            self.parent[node] = self.find(parent)
        return self.parent[node]

    def union(self, left: tuple[str, Any], right: tuple[str, Any]) -> None:
        self.add(left)
        self.add(right)
        root_left = self.find(left)
        root_right = self.find(right)
        if root_left == root_right:
            return
        rank_left = self.rank[root_left]
        rank_right = self.rank[root_right]
        if rank_left < rank_right:
            root_left, root_right = root_right, root_left
        self.parent[root_right] = root_left
        if rank_left == rank_right:
            self.rank[root_left] += 1


@dataclass(frozen=True)
class ResultadoConciliacionMatriculaTokens:
    """Resultado tabular de la conciliación.

    ``detalle`` contiene una fila por componente canónico. ``auditoria``
    contiene una fila por fila física de origen y permite reconstruir las dos
    fuentes sin depender de que sus índices sean únicos. ``resumen`` expone
    las pruebas de reconstrucción y las métricas de la unión canónica.
    """

    detalle: pd.DataFrame
    resumen: pd.DataFrame
    auditoria: pd.DataFrame


def _validar_columnas(
    df: pd.DataFrame,
    columnas: tuple[str, ...],
    *,
    fuente: str,
) -> None:
    faltantes = [columna for columna in columnas if columna not in df.columns]
    if faltantes:
        raise KeyError(
            f"{fuente}: faltan columnas requeridas: {', '.join(faltantes)}"
        )


def conciliar_matricula_tokens(
    matricula: pd.DataFrame,
    tokens: pd.DataFrame,
    *,
    columna_llave_estudiante: str = "CODCLI",
    columna_token_matricula: str = "token",
    columna_token_fuente: str = "token",
    normalizador: Normalizador | None = None,
    normalizador_llave_estudiante: Normalizador | None = None,
    normalizador_token: Normalizador | None = None,
) -> ResultadoConciliacionMatriculaTokens:
    """Concilia matrícula y tokens sin descartar ni multiplicar filas.

    Las columnas y normalizadores son parametrizables. ``normalizador`` actúa
    como valor común; los normalizadores específicos, cuando se proporcionan,
    tienen precedencia sobre él.
    """

    if not isinstance(matricula, pd.DataFrame) or not isinstance(tokens, pd.DataFrame):
        raise TypeError("matricula y tokens deben ser pandas.DataFrame")
    _validar_columnas(
        matricula,
        (columna_llave_estudiante, columna_token_matricula),
        fuente="matricula",
    )
    _validar_columnas(tokens, (columna_token_fuente,), fuente="tokens")

    normalizador_comun = normalizador or normalizar_identificador
    normalizador_estudiante = normalizador_llave_estudiante or normalizador_comun
    normalizador_tokens = normalizador_token or normalizador_comun

    union = _UnionFind()
    registros_matricula: list[dict[str, Any]] = []
    registros_tokens: list[dict[str, Any]] = []
    cantidad_aristas = 0

    for posicion, (indice, fila) in enumerate(matricula.iterrows()):
        nodo_fila = ("fila_matricula", posicion)
        union.add(nodo_fila)
        llave_original = fila[columna_llave_estudiante]
        token_original = fila[columna_token_matricula]
        llave = _normalizar(llave_original, normalizador_estudiante)
        token = _normalizar(token_original, normalizador_tokens)
        if llave is not None:
            union.union(nodo_fila, ("estudiante", llave))
            cantidad_aristas += 1
        if token is not None:
            union.union(nodo_fila, ("token", token))
            cantidad_aristas += 1
        registros_matricula.append(
            {
                "fuente": "MATRICULA",
                "fila_origen": f"MATRICULA:{posicion:09d}",
                "posicion_origen": posicion,
                "indice_origen": indice,
                "nodo_fila": nodo_fila,
                "llave_estudiante_original": llave_original,
                "llave_estudiante_normalizada": llave,
                "token_original": token_original,
                "token_normalizado": token,
                "llave_estudiante_nula": llave is None,
                "token_nulo": token is None,
            }
        )

    for posicion, (indice, fila) in enumerate(tokens.iterrows()):
        nodo_fila = ("fila_tokens", posicion)
        union.add(nodo_fila)
        token_original = fila[columna_token_fuente]
        token = _normalizar(token_original, normalizador_tokens)
        if token is not None:
            union.union(nodo_fila, ("token", token))
            cantidad_aristas += 1
        registros_tokens.append(
            {
                "fuente": "TOKENS",
                "fila_origen": f"TOKENS:{posicion:09d}",
                "posicion_origen": posicion,
                "indice_origen": indice,
                "nodo_fila": nodo_fila,
                "llave_estudiante_original": None,
                "llave_estudiante_normalizada": None,
                "token_original": token_original,
                "token_normalizado": token,
                "llave_estudiante_nula": None,
                "token_nulo": token is None,
            }
        )

    nodos_por_raiz: dict[tuple[str, Any], list[tuple[str, Any]]] = defaultdict(list)
    for nodo in union.parent:
        nodos_por_raiz[union.find(nodo)].append(nodo)

    registros_por_raiz_m: dict[tuple[str, Any], list[dict[str, Any]]] = defaultdict(list)
    registros_por_raiz_t: dict[tuple[str, Any], list[dict[str, Any]]] = defaultdict(list)
    for registro in registros_matricula:
        registros_por_raiz_m[union.find(registro["nodo_fila"])].append(registro)
    for registro in registros_tokens:
        registros_por_raiz_t[union.find(registro["nodo_fila"])].append(registro)

    infinito = len(matricula) + len(tokens) + 1

    def clave_orden(raiz: tuple[str, Any]) -> tuple[int, int, str]:
        posiciones_m = [
            registro["posicion_origen"] for registro in registros_por_raiz_m[raiz]
        ]
        posiciones_t = [
            registro["posicion_origen"] for registro in registros_por_raiz_t[raiz]
        ]
        return (
            min(posiciones_m, default=infinito),
            min(posiciones_t, default=infinito),
            repr(sorted(nodos_por_raiz[raiz], key=repr)),
        )

    raices_ordenadas = sorted(nodos_por_raiz, key=clave_orden)
    componente_por_raiz = {
        raiz: f"COMPONENTE:{numero:09d}"
        for numero, raiz in enumerate(raices_ordenadas, start=1)
    }

    detalle_registros: list[dict[str, Any]] = []
    categoria_por_raiz: dict[tuple[str, Any], str] = {}

    for raiz in raices_ordenadas:
        filas_m = registros_por_raiz_m[raiz]
        filas_t = registros_por_raiz_t[raiz]
        llaves_estudiante = sorted(
            {
                registro["llave_estudiante_normalizada"]
                for registro in filas_m
                if registro["llave_estudiante_normalizada"] is not None
            }
        )
        tokens_matricula = sorted(
            {
                registro["token_normalizado"]
                for registro in filas_m
                if registro["token_normalizado"] is not None
            }
        )
        tokens_fuente = sorted(
            {
                registro["token_normalizado"]
                for registro in filas_t
                if registro["token_normalizado"] is not None
            }
        )
        tokens_componente = sorted(set(tokens_matricula) | set(tokens_fuente))
        conteo_estudiantes = Counter(
            registro["llave_estudiante_normalizada"]
            for registro in filas_m
            if registro["llave_estudiante_normalizada"] is not None
        )
        conteo_tokens_fuente = Counter(
            registro["token_normalizado"]
            for registro in filas_t
            if registro["token_normalizado"] is not None
        )

        tiene_matricula = bool(filas_m)
        tiene_token_fuente = bool(filas_t)
        tiene_llave_matricula_nula = any(
            registro["llave_estudiante_normalizada"] is None for registro in filas_m
        )
        conflicto_matricula = tiene_matricula and (
            tiene_llave_matricula_nula
            or len(filas_m) > 1
            or len(llaves_estudiante) != 1
            or len(tokens_matricula) > 1
            or any(cantidad > 1 for cantidad in conteo_estudiantes.values())
        )
        token_duplicado = any(
            cantidad > 1 for cantidad in conteo_tokens_fuente.values()
        )
        tokens_coincidentes = sorted(set(tokens_matricula) & set(tokens_fuente))

        if conflicto_matricula:
            categoria = CATEGORIA_CONFLICTO_MATRICULA
            razon = (
                "El componente no representa una fila de matrícula unívoca: "
                "llave nula, filas repetidas o asociaciones múltiples."
            )
        elif token_duplicado:
            categoria = CATEGORIA_TOKEN_DUPLICADO
            razon = (
                "Un token válido aparece en más de una fila física de la "
                "fuente de tokens."
            )
        elif tiene_matricula and tokens_coincidentes:
            categoria = CATEGORIA_VIGENTE_CON_TOKEN
            razon = "La matrícula unívoca tiene un token presente en la fuente de tokens."
        elif tiene_matricula:
            categoria = CATEGORIA_VIGENTE_SIN_TOKEN
            razon = "La matrícula unívoca no tiene token coincidente en la fuente."
        else:
            categoria = CATEGORIA_TOKEN_SIN_MATRICULA
            razon = "El componente contiene tokens, pero ninguna fila de matrícula."

        categoria_por_raiz[raiz] = categoria
        detalle_registros.append(
            {
                "componente_id": componente_por_raiz[raiz],
                "unidad_analisis": (
                    "Componente canónico conectado entre llave estudiante y token"
                ),
                "categoria": categoria,
                "precedencia_categoria": PRECEDENCIA_CATEGORIAS.index(categoria) + 1,
                "razon_categoria": razon,
                "filas_matricula_origen": tuple(
                    registro["fila_origen"] for registro in filas_m
                ),
                "filas_tokens_origen": tuple(
                    registro["fila_origen"] for registro in filas_t
                ),
                "posiciones_matricula_origen": tuple(
                    registro["posicion_origen"] for registro in filas_m
                ),
                "posiciones_tokens_origen": tuple(
                    registro["posicion_origen"] for registro in filas_t
                ),
                "indices_matricula_origen": tuple(
                    registro["indice_origen"] for registro in filas_m
                ),
                "indices_tokens_origen": tuple(
                    registro["indice_origen"] for registro in filas_t
                ),
                "cantidad_filas_matricula": len(filas_m),
                "cantidad_filas_tokens": len(filas_t),
                "llaves_estudiante": tuple(llaves_estudiante),
                "tokens_matricula": tuple(tokens_matricula),
                "tokens_fuente": tuple(tokens_fuente),
                "tokens_union_canonica": tuple(tokens_componente),
                "tokens_coincidentes": tuple(tokens_coincidentes),
                "llaves_nulas_matricula": sum(
                    registro["llave_estudiante_normalizada"] is None
                    for registro in filas_m
                ),
                "tokens_nulos_matricula": sum(
                    registro["token_normalizado"] is None for registro in filas_m
                ),
                "tokens_nulos_fuente": sum(
                    registro["token_normalizado"] is None for registro in filas_t
                ),
                "conflicto_matricula": conflicto_matricula,
                "token_duplicado": token_duplicado,
                "tiene_matricula": tiene_matricula,
                "tiene_token_fuente": tiene_token_fuente,
            }
        )

    auditoria_registros: list[dict[str, Any]] = []
    for registro in [*registros_matricula, *registros_tokens]:
        raiz = union.find(registro["nodo_fila"])
        auditoria_registros.append(
            {
                key: value
                for key, value in registro.items()
                if key != "nodo_fila"
            }
            | {
                "componente_id": componente_por_raiz[raiz],
                "categoria": categoria_por_raiz[raiz],
                "fila_origen_asignada_una_vez": True,
            }
        )

    columnas_detalle = [
        "componente_id",
        "unidad_analisis",
        "categoria",
        "precedencia_categoria",
        "razon_categoria",
        "filas_matricula_origen",
        "filas_tokens_origen",
        "posiciones_matricula_origen",
        "posiciones_tokens_origen",
        "indices_matricula_origen",
        "indices_tokens_origen",
        "cantidad_filas_matricula",
        "cantidad_filas_tokens",
        "llaves_estudiante",
        "tokens_matricula",
        "tokens_fuente",
        "tokens_union_canonica",
        "tokens_coincidentes",
        "llaves_nulas_matricula",
        "tokens_nulos_matricula",
        "tokens_nulos_fuente",
        "conflicto_matricula",
        "token_duplicado",
        "tiene_matricula",
        "tiene_token_fuente",
    ]
    columnas_auditoria = [
        "fuente",
        "fila_origen",
        "posicion_origen",
        "indice_origen",
        "llave_estudiante_original",
        "llave_estudiante_normalizada",
        "token_original",
        "token_normalizado",
        "llave_estudiante_nula",
        "token_nulo",
        "componente_id",
        "categoria",
        "fila_origen_asignada_una_vez",
    ]
    detalle = pd.DataFrame(detalle_registros, columns=columnas_detalle)
    auditoria = pd.DataFrame(auditoria_registros, columns=columnas_auditoria)

    filas_m_reconstruidas = int((auditoria["fuente"] == "MATRICULA").sum())
    filas_t_reconstruidas = int((auditoria["fuente"] == "TOKENS").sum())
    estudiantes_validos = {
        registro["llave_estudiante_normalizada"]
        for registro in registros_matricula
        if registro["llave_estudiante_normalizada"] is not None
    }
    tokens_validos_matricula = {
        registro["token_normalizado"]
        for registro in registros_matricula
        if registro["token_normalizado"] is not None
    }
    tokens_validos_fuente = {
        registro["token_normalizado"]
        for registro in registros_tokens
        if registro["token_normalizado"] is not None
    }
    tokens_union = tokens_validos_matricula | tokens_validos_fuente

    resumen_registros: list[dict[str, Any]] = []

    def agregar_metrica(
        metrica: str,
        valor: int,
        *,
        esperado: int | None = None,
        observacion: str = "",
    ) -> None:
        diferencia = None if esperado is None else valor - esperado
        resumen_registros.append(
            {
                "metrica": metrica,
                "valor": valor,
                "valor_esperado": esperado,
                "diferencia": diferencia,
                "resultado": (
                    "INFORMATIVO"
                    if esperado is None
                    else ("OK" if diferencia == 0 else "ERROR")
                ),
                "observacion": observacion,
            }
        )

    agregar_metrica("filas_matricula_origen", len(matricula))
    agregar_metrica(
        "filas_matricula_reconstruidas",
        filas_m_reconstruidas,
        esperado=len(matricula),
        observacion="Cada fila física debe aparecer exactamente una vez en auditoría.",
    )
    agregar_metrica("filas_tokens_origen", len(tokens))
    agregar_metrica(
        "filas_tokens_reconstruidas",
        filas_t_reconstruidas,
        esperado=len(tokens),
        observacion="Cada fila física debe aparecer exactamente una vez en auditoría.",
    )
    agregar_metrica("componentes_union_canonica", len(detalle))
    agregar_metrica("nodos_estudiante_canonicos", len(estudiantes_validos))
    agregar_metrica("nodos_token_canonicos", len(tokens_union))
    agregar_metrica(
        "nodos_identificador_union_canonica",
        len(estudiantes_validos) + len(tokens_union),
    )
    agregar_metrica("nodos_fila_origen", len(matricula) + len(tokens))
    agregar_metrica("nodos_grafo_union_canonica", len(union.parent))
    agregar_metrica("aristas_grafo_union_canonica", cantidad_aristas)
    agregar_metrica("tokens_unicos_validos_matricula", len(tokens_validos_matricula))
    agregar_metrica("tokens_unicos_validos_fuente", len(tokens_validos_fuente))
    agregar_metrica("tokens_unicos_union_canonica", len(tokens_union))
    agregar_metrica(
        "filas_matricula_llave_estudiante_nula",
        sum(registro["llave_estudiante_nula"] for registro in registros_matricula),
    )
    agregar_metrica(
        "filas_matricula_token_nulo",
        sum(registro["token_nulo"] for registro in registros_matricula),
    )
    agregar_metrica(
        "filas_tokens_token_nulo",
        sum(registro["token_nulo"] for registro in registros_tokens),
    )
    for categoria in PRECEDENCIA_CATEGORIAS:
        agregar_metrica(
            f"componentes_categoria::{categoria}",
            int((detalle["categoria"] == categoria).sum()),
        )

    resumen = pd.DataFrame(
        resumen_registros,
        columns=[
            "metrica",
            "valor",
            "valor_esperado",
            "diferencia",
            "resultado",
            "observacion",
        ],
    )

    _validar_resultado_conciliacion(
        detalle=detalle,
        auditoria=auditoria,
        filas_matricula=len(matricula),
        filas_tokens=len(tokens),
    )
    return ResultadoConciliacionMatriculaTokens(
        detalle=detalle,
        resumen=resumen,
        auditoria=auditoria,
    )


def _validar_resultado_conciliacion(
    *,
    detalle: pd.DataFrame,
    auditoria: pd.DataFrame,
    filas_matricula: int,
    filas_tokens: int,
) -> None:
    if not detalle["componente_id"].is_unique:
        raise AssertionError("Los componentes canónicos no son únicos")
    if not detalle["categoria"].isin(CATEGORIAS_CONCILIACION).all():
        raise AssertionError("Existe un componente sin categoría gobernada")
    if detalle["categoria"].isna().any():
        raise AssertionError("Existe un componente sin categoría")
    if not auditoria["fila_origen"].is_unique:
        raise AssertionError("Una fila de origen fue asignada más de una vez")
    conteo_m = int((auditoria["fuente"] == "MATRICULA").sum())
    conteo_t = int((auditoria["fuente"] == "TOKENS").sum())
    if conteo_m != filas_matricula:
        raise AssertionError(
            f"Matrícula no reconstruida: origen={filas_matricula}, auditoría={conteo_m}"
        )
    if conteo_t != filas_tokens:
        raise AssertionError(
            f"Tokens no reconstruidos: origen={filas_tokens}, auditoría={conteo_t}"
        )
    componentes_auditados = set(auditoria["componente_id"])
    componentes_detalle = set(detalle["componente_id"])
    if componentes_auditados != componentes_detalle:
        raise AssertionError("Detalle y auditoría no contienen los mismos componentes")


class ErrorParticionKPI(ValueError):
    """Error bloqueante que conserva la auditoría de la partición fallida."""

    def __init__(self, mensaje: str, auditoria: pd.DataFrame) -> None:
        super().__init__(mensaje)
        self.auditoria = auditoria


COLUMNAS_AUDITORIA_KPI = (
    "registro_id",
    "ejecucion",
    "salida",
    "hoja",
    "identidad",
    "unidad",
    "llave",
    "tipo_registro",
    "componente",
    "origen_componente",
    "valor",
    "total",
    "suma_componentes_declarados",
    "diferencia_inicial",
    "suma_componentes_validada",
    "diferencia_final",
    "resultado",
    "explicacion",
)


def _a_decimal(valor: Number, *, nombre: str) -> Decimal:
    if isinstance(valor, bool) or not isinstance(valor, Number):
        raise TypeError(f"{nombre} debe ser numérico")
    try:
        decimal = Decimal(str(valor))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{nombre} no es un número finito") from exc
    if not decimal.is_finite():
        raise ValueError(f"{nombre} no es un número finito")
    if decimal < 0:
        raise ValueError(f"{nombre} no puede ser negativo")
    return decimal


def _numero_a_salida(valor: Decimal) -> int | float:
    if valor == valor.to_integral_value():
        return int(valor)
    return float(valor)


def validar_particion_kpi(
    *,
    total: Number,
    componentes: Mapping[str, Number],
    ejecucion: str = "",
    salida: str = "",
    hoja: str = "",
    identidad: str = "",
    unidad: str = "",
    llave: str = "",
    explicacion_residual: str | None = None,
    nombre_residual: str = "OTROS",
    tolerancia: Number = 0,
    registro_id: str = "PARTICION:000000001",
) -> pd.DataFrame:
    """Valida una identidad KPI y devuelve su auditoría tabular.

    Si falta una parte positiva, incorpora ``OTROS`` de forma explícita. Si la
    suma excede el total, levanta :class:`ErrorParticionKPI`; la excepción
    conserva en ``auditoria`` el registro que explica el solapamiento.
    """

    if not isinstance(componentes, Mapping):
        raise TypeError("componentes debe ser un Mapping")
    total_decimal = _a_decimal(total, nombre="total")
    tolerancia_decimal = _a_decimal(tolerancia, nombre="tolerancia")
    componentes_decimales: list[tuple[str, Decimal]] = []
    for nombre, valor in componentes.items():
        nombre_limpio = str(nombre).strip()
        if not nombre_limpio:
            raise ValueError("Los nombres de componentes no pueden estar vacíos")
        componentes_decimales.append(
            (nombre_limpio, _a_decimal(valor, nombre=f"componente {nombre_limpio}"))
        )

    suma_declarada = sum(
        (valor for _, valor in componentes_decimales), start=Decimal("0")
    )
    diferencia_inicial = total_decimal - suma_declarada
    resultado = "OK"
    explicacion = "La suma de componentes coincide con el total."
    componentes_validados = [
        (nombre, valor, "DECLARADO") for nombre, valor in componentes_decimales
    ]

    if diferencia_inicial > tolerancia_decimal:
        if any(nombre == nombre_residual for nombre, _ in componentes_decimales):
            raise ValueError(
                f"El componente reservado {nombre_residual!r} ya fue declarado; "
                "no es posible agregar el residual automático."
            )
        componentes_validados.append(
            (nombre_residual, diferencia_inicial, "RESIDUAL_AUTOMATICO")
        )
        resultado = "OK_CON_OTROS"
        explicacion = explicacion_residual or (
            "Diferencia positiva entre el total y los componentes declarados; "
            f"se incorpora la categoría residual explícita {nombre_residual}."
        )
    elif diferencia_inicial < -tolerancia_decimal:
        resultado = "ERROR_SOLAPAMIENTO"
        explicacion = (
            "La suma de componentes excede el total; existe solapamiento o "
            "una inconsistencia de universo."
        )

    suma_validada = sum(
        (valor for _, valor, _ in componentes_validados), start=Decimal("0")
    )
    diferencia_final = total_decimal - suma_validada
    if abs(diferencia_final) <= tolerancia_decimal:
        diferencia_final = Decimal("0")

    base = {
        "registro_id": registro_id,
        "ejecucion": ejecucion,
        "salida": salida,
        "hoja": hoja,
        "identidad": identidad,
        "unidad": unidad,
        "llave": llave,
        "total": _numero_a_salida(total_decimal),
        "suma_componentes_declarados": _numero_a_salida(suma_declarada),
        "diferencia_inicial": _numero_a_salida(diferencia_inicial),
        "suma_componentes_validada": _numero_a_salida(suma_validada),
        "diferencia_final": _numero_a_salida(diferencia_final),
        "resultado": resultado,
        "explicacion": explicacion,
    }
    filas = [
        base
        | {
            "tipo_registro": "COMPONENTE",
            "componente": nombre,
            "origen_componente": origen,
            "valor": _numero_a_salida(valor),
        }
        for nombre, valor, origen in componentes_validados
    ]
    filas.append(
        base
        | {
            "tipo_registro": "RESUMEN",
            "componente": "TOTAL",
            "origen_componente": "TOTAL_OFICIAL",
            "valor": _numero_a_salida(total_decimal),
        }
    )
    auditoria = pd.DataFrame(filas, columns=COLUMNAS_AUDITORIA_KPI)

    if resultado == "ERROR_SOLAPAMIENTO":
        raise ErrorParticionKPI(
            (
                f"Partición KPI inconsistente: total={_numero_a_salida(total_decimal)}, "
                f"componentes={_numero_a_salida(suma_declarada)}, "
                f"diferencia={_numero_a_salida(diferencia_inicial)}"
            ),
            auditoria,
        )
    return auditoria


@dataclass
class RegistroParticionesKPI:
    """Registro acumulable de validaciones KPI, incluidas las fallidas."""

    _registros: list[pd.DataFrame] = field(default_factory=list, init=False)
    _secuencia: int = field(default=0, init=False)

    def registrar(
        self,
        *,
        total: Number,
        componentes: Mapping[str, Number],
        **contexto: Any,
    ) -> pd.DataFrame:
        self._secuencia += 1
        contexto = dict(contexto)
        contexto.setdefault("registro_id", f"PARTICION:{self._secuencia:09d}")
        try:
            auditoria = validar_particion_kpi(
                total=total,
                componentes=componentes,
                **contexto,
            )
        except ErrorParticionKPI as exc:
            self._registros.append(exc.auditoria.copy())
            raise
        self._registros.append(auditoria.copy())
        return auditoria

    def to_frame(self) -> pd.DataFrame:
        if not self._registros:
            return pd.DataFrame(columns=COLUMNAS_AUDITORIA_KPI)
        return pd.concat(self._registros, ignore_index=True)

    @property
    def auditoria(self) -> pd.DataFrame:
        return self.to_frame()

    def limpiar(self) -> None:
        self._registros.clear()
        self._secuencia = 0


@dataclass(frozen=True)
class SemanticaEliminadosMatriculaVentana:
    """Descripción auditable del indicador, sin atribuir fecha de eliminación."""

    columna_fecha: str = "FECHAMATRICULA"
    fecha_inicio: Any = None
    fecha_fin: Any = None
    leyenda: str = LEYENDA_ELIMINADOS_MATRICULA_VENTANA
    advertencia: str = ADVERTENCIA_ELIMINADOS_MATRICULA_VENTANA

    def como_registro(self) -> dict[str, Any]:
        return {
            "indicador": "ACTUALMENTE_ELIMINADOS_MATRICULA_EN_VENTANA",
            "leyenda": self.leyenda,
            "advertencia": self.advertencia,
            "columna_fecha": self.columna_fecha,
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
            "criterio": (
                "Estado actual eliminado y fecha de matrícula dentro de la "
                "ventana evaluada."
            ),
        }


def describir_eliminados_matricula_ventana(
    *,
    columna_fecha: str = "FECHAMATRICULA",
    fecha_inicio: Any = None,
    fecha_fin: Any = None,
) -> pd.DataFrame:
    """Devuelve una fila lista para incorporar a una auditoría de ejecución."""

    semantica = SemanticaEliminadosMatriculaVentana(
        columna_fecha=columna_fecha,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )
    return pd.DataFrame([semantica.como_registro()])


__all__ = [
    "ADVERTENCIA_ELIMINADOS_MATRICULA_VENTANA",
    "CATEGORIAS_CONCILIACION",
    "CATEGORIA_CONFLICTO_MATRICULA",
    "CATEGORIA_TOKEN_DUPLICADO",
    "CATEGORIA_TOKEN_SIN_MATRICULA",
    "CATEGORIA_VIGENTE_CON_TOKEN",
    "CATEGORIA_VIGENTE_SIN_TOKEN",
    "COLUMNAS_AUDITORIA_KPI",
    "ErrorParticionKPI",
    "LEYENDA_ELIMINADOS_MATRICULA_VENTANA",
    "PRECEDENCIA_CATEGORIAS",
    "RegistroParticionesKPI",
    "ResultadoConciliacionMatriculaTokens",
    "SemanticaEliminadosMatriculaVentana",
    "conciliar_matricula_tokens",
    "describir_eliminados_matricula_ventana",
    "normalizar_identificador",
    "validar_particion_kpi",
]
