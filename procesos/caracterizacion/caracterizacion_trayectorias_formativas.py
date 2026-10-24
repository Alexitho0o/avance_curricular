from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


INVALIDOS = {
    "",
    " ",
    "n/a",
    "na",
    "nan",
    "null",
    "none",
    "-",
    "--",
    ".",
    "s/i",
    "sin info",
}

AFIRMATIVOS = {
    "si",
    "sí",
    "yes",
    "true",
    "1",
    "x",
    "seleccionado",
    "selected",
}

PATRONES_TECNICOS = (
    r"\btecnico\b",
    r"\btecnica\b",
    r"\btns\b",
    r"\bnivel tecnico\b",
)

PATRONES_PROFESIONALES = (
    r"\bingenieria\b",
    r"\bprofesional\b",
    r"\blicenciatura\b",
)

PATRONES_EMTP = (
    r"tecnico profesional",
    r"tecnica profesional",
    r"\bemtp\b",
    r"\bliceo tp\b",
    r"liceo tecnico",
    r"liceo industrial",
    r"liceo comercial",
    r"liceo agricola",
    r"liceo polivalente",
    r"formacion diferenciada tecnico",
)

PATRONES_CFT = (
    r"centro de formacion tecnica",
    r"\bcft\b",
)

PATRONES_DIPLOMADO = (
    r"\bdiplomado\b",
    r"\bdiplomatura\b",
)

PATRONES_TITULADO = (
    r"\btitulado\b",
    r"\btitulada\b",
    r"\btitulo otorgado\b",
    r"\bfinalizado con titulo\b",
)


def _texto(valor: Any) -> str:
    if valor is None:
        return ""
    try:
        if pd.isna(valor):
            return ""
    except Exception:
        pass

    valor = str(valor).strip()
    if valor.lower() in INVALIDOS:
        return ""

    valor = unicodedata.normalize("NFKD", valor)
    valor = "".join(c for c in valor if not unicodedata.combining(c))
    valor = re.sub(r"\s+", " ", valor).strip().lower()
    return valor


def _valido(valor: Any) -> bool:
    return _texto(valor) != ""


def _afirmativo(valor: Any) -> bool:
    return _texto(valor) in {_texto(x) for x in AFIRMATIVOS}


def _coincide(valor: Any, patrones: tuple[str, ...]) -> bool:
    texto = _texto(valor)
    return bool(texto) and any(
        re.search(patron, texto, flags=re.IGNORECASE)
        for patron in patrones
    )


def _normalizar_rut(valor: Any) -> str:
    texto = _texto(valor).upper()
    return re.sub(r"[^0-9K]", "", texto)


def _normalizar_token(valor: Any) -> str:
    return re.sub(r"[^0-9A-Z]", "", _texto(valor).upper())


def _buscar_columna(
    df: pd.DataFrame,
    nombres: tuple[str, ...] = (),
    prefijos: tuple[str, ...] = (),
) -> str | None:
    mapa = {_texto(c): c for c in df.columns}

    for nombre in nombres:
        normalizado = _texto(nombre)
        if normalizado in mapa:
            return mapa[normalizado]

    for columna in df.columns:
        base = _texto(columna)
        for prefijo in prefijos:
            if base.startswith(_texto(prefijo)):
                return columna

    return None


def _serie_texto_combinada(
    df: pd.DataFrame,
    columnas: list[str | None],
) -> pd.Series:
    existentes = [c for c in columnas if c and c in df.columns]

    if not existentes:
        return pd.Series("", index=df.index, dtype="object")

    salida = pd.Series("", index=df.index, dtype="object")
    for columna in existentes:
        valores = df[columna].map(_texto)
        salida = (
            salida.astype(str).str.strip()
            + " "
            + valores.astype(str).str.strip()
        ).str.strip()

    return salida


def _encontrar_dataframes(namespace: dict[str, Any]) -> dict[str, pd.DataFrame]:
    encontrados: dict[str, pd.DataFrame] = {}

    for nombre, valor in namespace.items():
        if isinstance(valor, pd.DataFrame) and not valor.empty:
            encontrados[nombre] = valor

    return encontrados


def _puntuar_df(
    nombre: str,
    df: pd.DataFrame,
    palabras_nombre: tuple[str, ...],
    columnas_requeridas: tuple[str, ...] = (),
) -> int:
    nombre_n = _texto(nombre)
    columnas_n = {_texto(c) for c in df.columns}

    score = sum(
        15 for palabra in palabras_nombre
        if _texto(palabra) in nombre_n
    )

    score += sum(
        4 for columna in columnas_requeridas
        if _texto(columna) in columnas_n
    )

    score += min(len(df) // 100, 25)
    return score


def _seleccionar_df(
    dataframes: dict[str, pd.DataFrame],
    palabras_nombre: tuple[str, ...],
    columnas_requeridas: tuple[str, ...] = (),
    preferir_mayor: bool = False,
) -> tuple[str | None, pd.DataFrame | None]:
    candidatos = []

    for nombre, df in dataframes.items():
        score = _puntuar_df(
            nombre,
            df,
            palabras_nombre,
            columnas_requeridas,
        )
        candidatos.append(
            (
                score,
                len(df) if preferir_mayor else 0,
                nombre,
                df,
            )
        )

    if not candidatos:
        return None, None

    candidatos.sort(key=lambda x: (x[0], x[1]), reverse=True)
    score, _, nombre, df = candidatos[0]

    if score <= 0:
        return None, None

    return nombre, df.copy()


def _buscar_salida(namespace: dict[str, Any]) -> Path:
    candidatos: list[Path] = []

    for nombre, valor in namespace.items():
        if not isinstance(valor, (str, Path)):
            continue

        texto = str(valor)
        if "02_SALIDAS" not in texto:
            continue

        ruta = Path(texto).expanduser()

        partes = list(ruta.parts)
        try:
            pos = partes.index("02_SALIDAS")
        except ValueError:
            continue

        salida = Path(*partes[: pos + 1])
        candidatos.append(salida)

    for ruta in candidatos:
        if ruta.exists() and ruta.is_dir():
            return ruta

    for ruta in candidatos:
        ruta.mkdir(parents=True, exist_ok=True)
        return ruta

    raise RuntimeError(
        "No fue posible localizar la carpeta 02_SALIDAS "
        "desde el namespace del pipeline."
    )


def _cargar_config(root: Path) -> dict[str, Any]:
    ruta = root / "config" / "trayectorias_formativas.json"

    if not ruta.exists():
        return {
            "programas_salida_intermedia": [],
            "codigos_salida_intermedia": [],
            "patrones_emtp_adicionales": [],
            "patrones_cft_adicionales": [],
        }

    with ruta.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def _cargar_dimension_nivel_programa() -> dict[str, str]:
    """
    Carga la dimensión institucional gobernada de programas.

    La fuente maestra se mantiene en avance_curricular. El Bloque 13
    consume un snapshot versionado dentro de gobernanza/sies para evitar
    dependencias operativas entre repositorios durante la ejecución.

    Retorna un mapa CODCARPR/alias -> clasificación institucional:
    TECNICO o PROFESIONAL.

    Los códigos con niveles contradictorios se excluyen del mapa.
    """
    ruta = (
        Path(__file__).resolve().parent
        / "gobernanza"
        / "sies"
        / "DURACION_ESTUDIOS.tsv"
    )

    if not ruta.exists():
        return {}

    try:
        dimension = pd.read_csv(
            ruta,
            sep="\t",
            dtype=object,
            encoding="utf-8-sig",
        )
    except UnicodeDecodeError:
        dimension = pd.read_csv(
            ruta,
            sep="\t",
            dtype=object,
            encoding="latin-1",
        )
    except Exception:
        return {}

    col_nivel = _buscar_columna(
        dimension,
        nombres=("NIVEL_CARRERA",),
    )

    col_canonico = _buscar_columna(
        dimension,
        nombres=(
            "CODCARPR_CANONICO",
            "CODCARPR",
            "COD_CAR",
        ),
    )

    col_alias = _buscar_columna(
        dimension,
        nombres=(
            "CODCARPR_ALIAS_LIST",
            "ALIASES",
        ),
    )

    if not col_nivel:
        return {}

    evidencia: dict[str, set[str]] = {}

    def registrar(codigo: Any, clasificacion: str) -> None:
        codigo_norm = _texto(codigo)

        if not codigo_norm:
            return

        evidencia.setdefault(
            codigo_norm,
            set(),
        ).add(clasificacion)

    for _, fila in dimension.iterrows():
        nivel_num = pd.to_numeric(
            pd.Series([fila.get(col_nivel)]),
            errors="coerce",
        ).iloc[0]

        if pd.isna(nivel_num):
            nivel_txt = _texto(
                fila.get(col_nivel)
            )

            if _coincide(
                nivel_txt,
                PATRONES_TECNICOS,
            ):
                clasificacion = "TECNICO"
            elif _coincide(
                nivel_txt,
                PATRONES_PROFESIONALES,
            ):
                clasificacion = "PROFESIONAL"
            else:
                continue

        elif int(nivel_num) == 1:
            clasificacion = "TECNICO"

        elif int(nivel_num) == 2:
            clasificacion = "PROFESIONAL"

        else:
            continue

        if col_canonico:
            registrar(
                fila.get(col_canonico),
                clasificacion,
            )

        if col_alias:
            aliases = str(
                fila.get(col_alias)
                or ""
            ).split("|")

            for alias in aliases:
                registrar(
                    alias,
                    clasificacion,
                )

    return {
        codigo: next(iter(clasificaciones))
        for codigo, clasificaciones in evidencia.items()
        if len(clasificaciones) == 1
    }


def _clasificar_nivel(df: pd.DataFrame) -> pd.Series:
    """
    Clasifica el nivel institucional del programa.

    Importante:
    NIVEL de Datos de Alumnos representa el nivel académico cursado por
    el estudiante y no el nivel estructural de la carrera. Por esta
    razón, la columna NIVEL no se utiliza en esta función.

    Jerarquía:
    1. NIVEL_CARRERA / NIVEL_GLOBAL / NIVEL_ANALISIS.
    2. Dimensión institucional gobernada por CODCARPR.
    3. Nombre explícito del programa.
    4. TIPO_PLAN_CARRERA.
    5. DURACION_ESTUDIOS.
    """
    col_nombre = _buscar_columna(
        df,
        nombres=(
            "NOMBRE_L",
            "NOMBRE_CARRERA",
            "CARRERA",
            "PROGRAMA",
            "NOMBRE_PROGRAMA",
            "DESCRIPCION",
        ),
    )

    # NIVEL queda excluido deliberadamente porque corresponde al avance
    # académico del estudiante dentro de su programa.
    col_nivel_programa = _buscar_columna(
        df,
        nombres=(
            "NIVEL_CARRERA",
            "NIVEL_GLOBAL",
            "NIVEL_ANALISIS",
            "NIVEL_PROGRAMA",
            "TIPO_PROGRAMA",
        ),
    )

    col_codcarpr = _buscar_columna(
        df,
        nombres=(
            "CODCARPR",
            "CODCARR",
            "COD_CAR",
            "CODIGO_CARRERA",
        ),
    )

    col_tipo_plan = _buscar_columna(
        df,
        nombres=("TIPO_PLAN_CARRERA",),
    )

    col_duracion = _buscar_columna(
        df,
        nombres=("DURACION_ESTUDIOS",),
    )

    resultado = pd.Series(
        "NO_CLASIFICADO",
        index=df.index,
        dtype=object,
    )

    # -----------------------------------------------------------------
    # 1. Nivel institucional explícito del programa
    # -----------------------------------------------------------------
    if col_nivel_programa:
        nivel_num = pd.to_numeric(
            df[col_nivel_programa],
            errors="coerce",
        )

        resultado.loc[
            nivel_num.eq(1)
        ] = "TECNICO"

        resultado.loc[
            nivel_num.eq(2)
        ] = "PROFESIONAL"

        nivel_txt = (
            df[col_nivel_programa]
            .fillna("")
            .map(_texto)
        )

        mascara_pendiente = resultado.eq(
            "NO_CLASIFICADO"
        )

        resultado.loc[
            mascara_pendiente
            & nivel_txt.map(
                lambda x: _coincide(
                    x,
                    PATRONES_TECNICOS,
                )
            )
        ] = "TECNICO"

        mascara_pendiente = resultado.eq(
            "NO_CLASIFICADO"
        )

        resultado.loc[
            mascara_pendiente
            & nivel_txt.map(
                lambda x: _coincide(
                    x,
                    PATRONES_PROFESIONALES,
                )
            )
        ] = "PROFESIONAL"

    # -----------------------------------------------------------------
    # 2. Dimensión institucional gobernada por CODCARPR
    # -----------------------------------------------------------------
    if col_codcarpr:
        mapa_nivel = (
            _cargar_dimension_nivel_programa()
        )

        if mapa_nivel:
            nivel_dimension = (
                df[col_codcarpr]
                .map(_texto)
                .map(mapa_nivel)
            )

            mascara_dimension = (
                resultado.eq("NO_CLASIFICADO")
                & nivel_dimension.notna()
            )

            resultado.loc[
                mascara_dimension
            ] = nivel_dimension.loc[
                mascara_dimension
            ]

    # -----------------------------------------------------------------
    # 3. Nombre explícito del programa
    # -----------------------------------------------------------------
    if col_nombre:
        nombre = (
            df[col_nombre]
            .fillna("")
            .map(_texto)
        )

        mascara_pendiente = resultado.eq(
            "NO_CLASIFICADO"
        )

        resultado.loc[
            mascara_pendiente
            & nombre.map(
                lambda x: _coincide(
                    x,
                    PATRONES_TECNICOS,
                )
            )
        ] = "TECNICO"

        mascara_pendiente = resultado.eq(
            "NO_CLASIFICADO"
        )

        resultado.loc[
            mascara_pendiente
            & nombre.map(
                lambda x: _coincide(
                    x,
                    PATRONES_PROFESIONALES,
                )
            )
        ] = "PROFESIONAL"

    # -----------------------------------------------------------------
    # 4. Tipo institucional de plan
    # -----------------------------------------------------------------
    if col_tipo_plan:
        tipo_plan = pd.to_numeric(
            df[col_tipo_plan],
            errors="coerce",
        )

        resultado.loc[
            resultado.eq("NO_CLASIFICADO")
            & tipo_plan.eq(1)
        ] = "PROFESIONAL"

        # La continuidad tiene precedencia sobre la clasificación
        # profesional base cuando existe evidencia explícita del plan.
        resultado.loc[
            tipo_plan.eq(3)
        ] = "PROFESIONAL_CONTINUIDAD"

    # -----------------------------------------------------------------
    # 5. Duración como último respaldo
    # -----------------------------------------------------------------
    if col_duracion:
        duracion = pd.to_numeric(
            df[col_duracion],
            errors="coerce",
        )

        resultado.loc[
            resultado.eq("NO_CLASIFICADO")
            & duracion.le(5)
        ] = "TECNICO"

        resultado.loc[
            resultado.eq("NO_CLASIFICADO")
            & duracion.ge(7)
        ] = "PROFESIONAL"

    return resultado

def _agregar_llaves(df: pd.DataFrame) -> pd.DataFrame:
    salida = df.copy()

    col_rut = _buscar_columna(
        salida,
        nombres=(
            "RUT",
            "NUM_DOCUMENTO",
            "RUT_NORMALIZADO",
            "RUT_NORMALIZADO_CON_DV",
            "RUT_ALUMNO",
        ),
    )
    col_token = _buscar_columna(
        salida,
        nombres=(
            "token",
            "_token_norm",
            "TOKEN",
            "token. Código de acceso",
        ),
        prefijos=("token.",),
    )
    col_codcli = _buscar_columna(
        salida,
        nombres=(
            "CODCLI",
            "CODCLI_NORMALIZADO",
        ),
    )

    salida["_LLAVE_RUT"] = (
        salida[col_rut].map(_normalizar_rut)
        if col_rut
        else ""
    )
    salida["_LLAVE_TOKEN"] = (
        salida[col_token].map(_normalizar_token)
        if col_token
        else ""
    )
    salida["_LLAVE_CODCLI"] = (
        salida[col_codcli].map(_texto)
        if col_codcli
        else ""
    )

    salida["_LLAVE_PERSONA"] = salida["_LLAVE_RUT"]

    sin_rut = salida["_LLAVE_PERSONA"].eq("")
    salida.loc[sin_rut, "_LLAVE_PERSONA"] = (
        "TOKEN:"
        + salida.loc[sin_rut, "_LLAVE_TOKEN"]
    )

    sin_rut_token = salida["_LLAVE_PERSONA"].isin(
        {"", "TOKEN:"}
    )
    salida.loc[sin_rut_token, "_LLAVE_PERSONA"] = (
        "CODCLI:"
        + salida.loc[sin_rut_token, "_LLAVE_CODCLI"]
    )

    return salida


def _integrar_encuesta(
    vigente: pd.DataFrame,
    encuesta: pd.DataFrame | None,
) -> pd.DataFrame:
    base = vigente.copy()

    base["_EMTP_ENCUESTA"] = False
    base["_EMTP_ENCUESTA_DATO"] = False
    base["_CFT_ENCUESTA"] = False
    base["_CFT_ENCUESTA_DATO"] = False

    if encuesta is None or encuesta.empty:
        return base

    encuesta = _agregar_llaves(encuesta)

    col_emtp = _buscar_columna(
        encuesta,
        prefijos=("G03Q31",),
    )
    col_cft_incompleta = _buscar_columna(
        encuesta,
        prefijos=("G03Q54[SQ003]",),
    )
    col_cft_completa = _buscar_columna(
        encuesta,
        prefijos=("G03Q54[SQ004]",),
    )
    col_institucion = _buscar_columna(
        encuesta,
        prefijos=("G03Q99",),
    )

    temporal = encuesta[
        ["_LLAVE_PERSONA", "_LLAVE_TOKEN"]
    ].copy()

    if col_emtp:
        temporal["_EMTP_ENCUESTA_DATO"] = encuesta[
            col_emtp
        ].map(_valido)
        temporal["_EMTP_ENCUESTA"] = encuesta[
            col_emtp
        ].map(
            lambda x: _coincide(
                x,
                (
                    r"tecnico profesional",
                    r"tecnica profesional",
                    r"\btp\b",
                ),
            )
        )
    else:
        temporal["_EMTP_ENCUESTA_DATO"] = False
        temporal["_EMTP_ENCUESTA"] = False

    flags_cft = pd.Series(False, index=encuesta.index)
    dato_cft = pd.Series(False, index=encuesta.index)

    for columna in (col_cft_incompleta, col_cft_completa):
        if columna:
            flags_cft |= encuesta[columna].map(_afirmativo)
            dato_cft |= encuesta[columna].map(_valido)

    if col_institucion:
        flags_cft |= encuesta[col_institucion].map(
            lambda x: _coincide(x, PATRONES_CFT)
        )
        dato_cft |= encuesta[col_institucion].map(_valido)

    temporal["_CFT_ENCUESTA"] = flags_cft
    temporal["_CFT_ENCUESTA_DATO"] = dato_cft

    temporal = temporal.sort_values(
        by=["_LLAVE_PERSONA", "_LLAVE_TOKEN"]
    ).drop_duplicates(
        subset=["_LLAVE_PERSONA", "_LLAVE_TOKEN"],
        keep="last",
    )

    por_rut = temporal[
        temporal["_LLAVE_PERSONA"].str.startswith(
            ("TOKEN:", "CODCLI:")
        ).eq(False)
    ].drop_duplicates("_LLAVE_PERSONA")

    por_token = temporal[
        temporal["_LLAVE_TOKEN"].ne("")
    ].drop_duplicates("_LLAVE_TOKEN")

    base = base.merge(
        por_rut[
            [
                "_LLAVE_PERSONA",
                "_EMTP_ENCUESTA",
                "_EMTP_ENCUESTA_DATO",
                "_CFT_ENCUESTA",
                "_CFT_ENCUESTA_DATO",
            ]
        ],
        on="_LLAVE_PERSONA",
        how="left",
        suffixes=("", "_RUT"),
    )

    for columna in (
        "_EMTP_ENCUESTA",
        "_EMTP_ENCUESTA_DATO",
        "_CFT_ENCUESTA",
        "_CFT_ENCUESTA_DATO",
    ):
        columna_rut = columna + "_RUT"
        if columna_rut in base.columns:
            base[columna] = base[columna_rut].fillna(
                base[columna]
            )
            base.drop(columns=[columna_rut], inplace=True)

    base = base.merge(
        por_token[
            [
                "_LLAVE_TOKEN",
                "_EMTP_ENCUESTA",
                "_EMTP_ENCUESTA_DATO",
                "_CFT_ENCUESTA",
                "_CFT_ENCUESTA_DATO",
            ]
        ],
        on="_LLAVE_TOKEN",
        how="left",
        suffixes=("", "_TOKEN"),
    )

    for columna in (
        "_EMTP_ENCUESTA",
        "_EMTP_ENCUESTA_DATO",
        "_CFT_ENCUESTA",
        "_CFT_ENCUESTA_DATO",
    ):
        columna_token = columna + "_TOKEN"
        if columna_token in base.columns:
            base[columna] = base[columna].fillna(
                base[columna_token]
            )
            base.drop(columns=[columna_token], inplace=True)

    for columna in (
        "_EMTP_ENCUESTA",
        "_EMTP_ENCUESTA_DATO",
        "_CFT_ENCUESTA",
        "_CFT_ENCUESTA_DATO",
    ):
        base[columna] = base[columna].fillna(False).astype(bool)

    return base


def _crear_kpi(
    codigo: str,
    indicador: str,
    numerador: int | None,
    total_matricula: int,
    casos_con_dato: int | None,
    estado: str,
    fuente: str,
    notas: str,
    denominador_elegible: int | None = None,
) -> dict[str, Any]:
    porcentaje_matricula = (
        numerador / total_matricula
        if numerador is not None and total_matricula
        else np.nan
    )

    porcentaje_con_dato = (
        numerador / casos_con_dato
        if (
            numerador is not None
            and casos_con_dato is not None
            and casos_con_dato > 0
        )
        else np.nan
    )

    cobertura = (
        casos_con_dato / total_matricula
        if (
            casos_con_dato is not None
            and total_matricula > 0
        )
        else np.nan
    )

    porcentaje_elegible = (
        numerador / denominador_elegible
        if (
            numerador is not None
            and denominador_elegible is not None
            and denominador_elegible > 0
        )
        else np.nan
    )

    return {
        "CODIGO_KPI": codigo,
        "INDICADOR": indicador,
        "NUMERADOR": numerador,
        "DENOMINADOR_MATRICULA": total_matricula,
        "PORCENTAJE_MATRICULA": porcentaje_matricula,
        "CASOS_CON_DATO": casos_con_dato,
        "PORCENTAJE_CASOS_CON_DATO": porcentaje_con_dato,
        "COBERTURA_DATO": cobertura,
        "DENOMINADOR_ELEGIBLE": denominador_elegible,
        "PORCENTAJE_ELEGIBLE": porcentaje_elegible,
        "ESTADO_CALCULO": estado,
        "FUENTE": fuente,
        "NOTAS": notas,
    }


def _formatear_excel(ruta: Path) -> None:
    libro = load_workbook(ruta)

    fill_titulo = PatternFill(
        "solid",
        fgColor="1F4E78",
    )
    fill_header = PatternFill(
        "solid",
        fgColor="D9EAF7",
    )
    fill_alerta = PatternFill(
        "solid",
        fgColor="FFF2CC",
    )
    borde = Border(
        bottom=Side(style="thin", color="B7B7B7")
    )

    for hoja in libro.worksheets:
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = hoja.dimensions

        for celda in hoja[1]:
            celda.fill = fill_titulo
            celda.font = Font(
                color="FFFFFF",
                bold=True,
            )
            celda.alignment = Alignment(
                horizontal="center",
                vertical="center",
                wrap_text=True,
            )

        for columna in hoja.columns:
            letra = get_column_letter(columna[0].column)
            largo = max(
                len(str(celda.value))
                if celda.value is not None
                else 0
                for celda in columna[:300]
            )
            hoja.column_dimensions[letra].width = min(
                max(largo + 2, 11),
                45,
            )

        for fila in hoja.iter_rows():
            for celda in fila:
                celda.alignment = Alignment(
                    vertical="top",
                    wrap_text=True,
                )
                celda.border = borde

        encabezados = {
            celda.value: celda.column
            for celda in hoja[1]
        }

        for nombre in (
            "PORCENTAJE_MATRICULA",
            "PORCENTAJE_CASOS_CON_DATO",
            "COBERTURA_DATO",
            "PORCENTAJE_ELEGIBLE",
        ):
            columna = encabezados.get(nombre)
            if columna:
                for fila in range(2, hoja.max_row + 1):
                    hoja.cell(fila, columna).number_format = "0.00%"

        col_estado = encabezados.get("ESTADO_CALCULO")
        if col_estado:
            for fila in range(2, hoja.max_row + 1):
                valor = str(
                    hoja.cell(fila, col_estado).value or ""
                )
                if valor not in {"CALCULADO", "CALCULADO_CON_COBERTURA"}:
                    for celda in hoja[fila]:
                        celda.fill = fill_alerta

    if "RESUMEN_KPI" in libro.sheetnames:
        hoja = libro["RESUMEN_KPI"]
        hoja.sheet_view.showGridLines = False

    libro.save(ruta)


def ejecutar_bloque_13_trayectorias(
    namespace: dict[str, Any],
) -> Path:
    print()
    print("=" * 64)
    print(" BLOQUE 13 · PROVENIENCIA Y TRAYECTORIAS FORMATIVAS")
    print("=" * 64)

    dataframes = _encontrar_dataframes(namespace)

    # El universo del bloque 13 debe provenir exclusivamente del
    # dataframe institucional gobernado de matrícula vigente.
    vigente = namespace.get("df_vigentes")
    nombre_vigente = "df_vigentes"

    if not isinstance(vigente, pd.DataFrame):
        vigente = namespace.get("DF_VIGENTES")
        nombre_vigente = "DF_VIGENTES"

    if not isinstance(vigente, pd.DataFrame):
        raise RuntimeError(
            "BLOQUE 13 no encontró el dataframe institucional "
            "df_vigentes/DF_VIGENTES."
        )

    vigente = vigente.copy()

    if vigente.empty:
        raise RuntimeError(
            "BLOQUE 13 recibió df_vigentes vacío."
        )

    nombre_historico, historico = _seleccionar_df(
        dataframes,
        palabras_nombre=(
            "historico",
            "matricula",
            "sies",
        ),
        columnas_requeridas=(
            "ANOMATRICULA",
            "PERIODOMATRICULA",
            "CODCLI",
            "RUT",
        ),
        preferir_mayor=True,
    )

    nombre_encuesta, encuesta = _seleccionar_df(
        dataframes,
        palabras_nombre=(
            "resultados",
            "encuesta",
            "canonicos",
        ),
        columnas_requeridas=(),
        preferir_mayor=False,
    )

    if encuesta is not None:
        tiene_g03 = any(
            _texto(c).startswith("g03q")
            for c in encuesta.columns
        )
        if not tiene_g03:
            encuesta = None
            nombre_encuesta = None

    if vigente is None:
        raise RuntimeError(
            "BLOQUE 13 no encontró el dataframe de matrícula vigente."
        )

    vigente = _agregar_llaves(vigente)

    # Gobernanza de cardinalidad:
    # cada fila de df_vigentes representa una matrícula institucional.
    # _LLAVE_PERSONA se conserva para cruces y análisis por persona,
    # pero no puede utilizarse para eliminar matrículas.
    vigente = vigente.copy()

    vigente["_NIVEL_PROGRAMA"] = _clasificar_nivel(vigente)

    total_matricula = len(vigente)

    if total_matricula == 0:
        raise RuntimeError(
            "BLOQUE 13 recibió matrícula vigente vacía."
        )

    # Control bloqueante: la cardinalidad usada por el bloque 13 debe
    # coincidir exactamente con el universo institucional df_vigentes.
    universo_institucional = namespace.get("df_vigentes")

    if not isinstance(universo_institucional, pd.DataFrame):
        universo_institucional = namespace.get("DF_VIGENTES")

    if not isinstance(universo_institucional, pd.DataFrame):
        raise RuntimeError(
            "No fue posible validar la cardinalidad institucional "
            "del bloque 13."
        )

    total_institucional = len(
        universo_institucional.drop_duplicates(
            subset=[
                c
                for c in ("CODCLI", "RUT")
                if c in universo_institucional.columns
            ],
            keep="first",
        )
    )

    if total_matricula != total_institucional:
        raise RuntimeError(
            "CARDINALIDAD_INVALIDA_BLOQUE_13: "
            f"calculada={total_matricula} | "
            f"institucional={total_institucional}"
        )

    print(
        "[B13][UNIVERSO] "
        f"fuente={nombre_vigente} | "
        f"filas_institucionales={total_institucional} | "
        f"filas_calculo={total_matricula} | "
        "cardinalidad=OK"
    )

    root = Path(__file__).resolve().parent
    config = _cargar_config(root)

    salida = _buscar_salida(namespace)

    anio = namespace.get("ANIO_ANALISIS", datetime.now().year)
    periodo = namespace.get("PERIODO_ANALISIS", "")
    fecha = datetime.now().strftime("%Y%m%d")

    archivo_salida = salida / (
        f"INDICADORES_TRAYECTORIAS_FORMATIVAS_"
        f"{anio}_P{periodo}_{fecha}.xlsx"
    )

    col_colegio = _buscar_columna(
        vigente,
        nombres=(
            "COLEGIO",
            "NOMBRE_COLEGIO",
            "ESTABLECIMIENTO",
        ),
    )
    col_modalidad = _buscar_columna(
        vigente,
        nombres=(
            "MODALIDAD",
            "TIPO_ENSENANZA",
            "FORMACION_DIFERENCIADA",
        ),
    )
    col_categoria = _buscar_columna(
        vigente,
        nombres=(
            "CATEGORIA",
            "DEPENDENCIA",
            "TIPO_ESTABLECIMIENTO",
        ),
    )
    col_descripcion = _buscar_columna(
        vigente,
        nombres=("DESCRIPCION",),
    )
    col_institucion_previa = _buscar_columna(
        vigente,
        nombres=(
            "NOMBREUNIVERSIDAD",
            "INSTITUCION_ANTERIOR",
            "INSTITUCION_ORIGEN",
        ),
    )
    col_carrera_anterior = _buscar_columna(
        vigente,
        nombres=(
            "CARRERARANTERIOR",
            "CARRERA_ANTERIOR",
        ),
    )

    texto_emtp = _serie_texto_combinada(
        vigente,
        [
            col_colegio,
            col_modalidad,
            col_categoria,
            col_descripcion,
        ],
    )

    patrones_emtp = PATRONES_EMTP + tuple(
        config.get("patrones_emtp_adicionales", [])
    )
    patrones_cft = PATRONES_CFT + tuple(
        config.get("patrones_cft_adicionales", [])
    )

    vigente["_EMTP_ADMIN_DATO"] = texto_emtp.ne("")
    vigente["_EMTP_ADMIN"] = texto_emtp.map(
        lambda x: _coincide(x, patrones_emtp)
    )

    texto_cft = _serie_texto_combinada(
        vigente,
        [
            col_institucion_previa,
            col_carrera_anterior,
        ],
    )
    vigente["_CFT_ADMIN_DATO"] = texto_cft.ne("")
    vigente["_CFT_ADMIN"] = texto_cft.map(
        lambda x: _coincide(x, patrones_cft)
    )

    vigente = _integrar_encuesta(vigente, encuesta)

    vigente["_PROVIENE_EMTP"] = (
        vigente["_EMTP_ADMIN"]
        | vigente["_EMTP_ENCUESTA"]
    )
    vigente["_EMTP_CON_DATO"] = (
        vigente["_EMTP_ADMIN_DATO"]
        | vigente["_EMTP_ENCUESTA_DATO"]
    )
    vigente["_FUENTE_EMTP"] = np.select(
        [
            vigente["_EMTP_ADMIN"]
            & vigente["_EMTP_ENCUESTA"],
            vigente["_EMTP_ADMIN"],
            vigente["_EMTP_ENCUESTA"],
        ],
        [
            "ADMINISTRATIVA_Y_ENCUESTA",
            "ADMINISTRATIVA",
            "ENCUESTA",
        ],
        default="SIN_IDENTIFICACION",
    )

    vigente["_PROVIENE_CFT"] = (
        vigente["_CFT_ADMIN"]
        | vigente["_CFT_ENCUESTA"]
    )
    vigente["_CFT_CON_DATO"] = (
        vigente["_CFT_ADMIN_DATO"]
        | vigente["_CFT_ENCUESTA_DATO"]
    )
    vigente["_FUENTE_CFT"] = np.select(
        [
            vigente["_CFT_ADMIN"]
            & vigente["_CFT_ENCUESTA"],
            vigente["_CFT_ADMIN"],
            vigente["_CFT_ENCUESTA"],
        ],
        [
            "ADMINISTRATIVA_Y_ENCUESTA",
            "ADMINISTRATIVA",
            "ENCUESTA",
        ],
        default="SIN_IDENTIFICACION",
    )

    kpis: list[dict[str, Any]] = []

    n_emtp = int(vigente["_PROVIENE_EMTP"].sum())
    dato_emtp = int(vigente["_EMTP_CON_DATO"].sum())

    kpis.append(
        _crear_kpi(
            "KPI_EMTP",
            "Estudiantes de matrícula vigente provenientes de EMTP",
            n_emtp,
            total_matricula,
            dato_emtp,
            "CALCULADO_CON_COBERTURA",
            "Matrícula administrativa + G03Q31 de encuesta",
            (
                "El porcentaje institucional se calcula sobre toda la "
                "matrícula vigente. También se informa el porcentaje "
                "entre casos con información y la cobertura."
            ),
        )
    )

    n_cft = int(vigente["_PROVIENE_CFT"].sum())
    dato_cft = int(vigente["_CFT_CON_DATO"].sum())

    kpis.append(
        _crear_kpi(
            "KPI_CFT",
            "Estudiantes de matrícula vigente provenientes de CFT",
            n_cft,
            total_matricula,
            dato_cft,
            "CALCULADO_CON_COBERTURA",
            (
                "Institución/carrera anterior + "
                "G03Q54[SQ003], G03Q54[SQ004] y G03Q99"
            ),
            (
                "Se reconoce procedencia CFT cuando existe evidencia "
                "administrativa o declaración de formación técnica "
                "superior previa."
            ),
        )
    )

    profesionales = vigente[
        vigente["_NIVEL_PROGRAMA"].isin(
            {"PROFESIONAL", "PROFESIONAL_CONTINUIDAD"}
        )
    ].copy()

    historial_personas = None

    if historico is not None and not historico.empty:
        historico = _agregar_llaves(historico)
        historico["_NIVEL_PROGRAMA"] = _clasificar_nivel(
            historico
        )

        col_anio = _buscar_columna(
            historico,
            nombres=("ANOMATRICULA", "ANIO", "AÑO"),
        )
        col_periodo = _buscar_columna(
            historico,
            nombres=(
                "PERIODOMATRICULA",
                "PERIODO",
            ),
        )

        historico["_ANIO_ORDEN"] = (
            pd.to_numeric(
                historico[col_anio],
                errors="coerce",
            )
            if col_anio
            else np.nan
        )
        historico["_PERIODO_ORDEN"] = (
            pd.to_numeric(
                historico[col_periodo],
                errors="coerce",
            )
            if col_periodo
            else 0
        )

        historico = historico.sort_values(
            [
                "_LLAVE_PERSONA",
                "_ANIO_ORDEN",
                "_PERIODO_ORDEN",
            ]
        )

        primera = historico.drop_duplicates(
            "_LLAVE_PERSONA",
            keep="first",
        )[
            ["_LLAVE_PERSONA", "_NIVEL_PROGRAMA"]
        ].rename(
            columns={
                "_NIVEL_PROGRAMA": "_NIVEL_PRIMER_INGRESO"
            }
        )

        vigente = vigente.merge(
            primera,
            on="_LLAVE_PERSONA",
            how="left",
        )

        profesional_directo = (
            vigente["_NIVEL_PROGRAMA"].isin(
                {
                    "PROFESIONAL",
                    "PROFESIONAL_CONTINUIDAD",
                }
            )
            & vigente["_NIVEL_PRIMER_INGRESO"].isin(
                {
                    "PROFESIONAL",
                    "PROFESIONAL_CONTINUIDAD",
                }
            )
        )

        n_prof_directo = int(profesional_directo.sum())
        casos_prof_con_historia = int(
            (
                vigente["_NIVEL_PROGRAMA"].isin(
                    {
                        "PROFESIONAL",
                        "PROFESIONAL_CONTINUIDAD",
                    }
                )
                & vigente["_NIVEL_PRIMER_INGRESO"].notna()
            ).sum()
        )

        kpis.append(
            _crear_kpi(
                "KPI_INGRESO_PROF_DIRECTO",
                (
                    "Estudiantes vigentes que ingresaron directamente "
                    "a carreras profesionales"
                ),
                n_prof_directo,
                total_matricula,
                casos_prof_con_historia,
                "CALCULADO_CON_COBERTURA",
                "Secuencia histórica de matrícula institucional",
                (
                    "Ingreso directo significa que el primer programa "
                    "regular observado en el histórico institucional "
                    "fue de nivel profesional."
                ),
                denominador_elegible=len(profesionales),
            )
        )

        secuencias = []
        for llave, grupo in historico.groupby(
            "_LLAVE_PERSONA",
            dropna=False,
        ):
            niveles = [
                x for x in grupo["_NIVEL_PROGRAMA"].tolist()
                if x != "NO_CLASIFICADO"
            ]

            primer_tecnico = next(
                (
                    i for i, nivel in enumerate(niveles)
                    if nivel == "TECNICO"
                ),
                None,
            )

            profesional_posterior = False
            if primer_tecnico is not None:
                profesional_posterior = any(
                    nivel in {
                        "PROFESIONAL",
                        "PROFESIONAL_CONTINUIDAD",
                    }
                    for nivel in niveles[primer_tecnico + 1 :]
                )

            secuencias.append(
                {
                    "_LLAVE_PERSONA": llave,
                    "_INGRESO_TECNICO": (
                        primer_tecnico is not None
                    ),
                    "_TECNICO_A_PROFESIONAL": profesional_posterior,
                }
            )

        historial_personas = pd.DataFrame(secuencias)

        vigente = vigente.merge(
            historial_personas,
            on="_LLAVE_PERSONA",
            how="left",
        )

        vigente["_INGRESO_TECNICO"] = vigente[
            "_INGRESO_TECNICO"
        ].fillna(False)
        vigente["_TECNICO_A_PROFESIONAL"] = vigente[
            "_TECNICO_A_PROFESIONAL"
        ].fillna(False)

        n_tecnico_prof = int(
            vigente["_TECNICO_A_PROFESIONAL"].sum()
        )
        denom_tecnico = int(
            vigente["_INGRESO_TECNICO"].sum()
        )

        kpis.append(
            _crear_kpi(
                "KPI_TECNICO_A_PROFESIONAL",
                (
                    "Estudiantes que ingresaron a carrera técnica y "
                    "posteriormente continuaron en carrera profesional"
                ),
                n_tecnico_prof,
                total_matricula,
                total_matricula,
                "CALCULADO",
                "Secuencia histórica de matrícula institucional",
                (
                    "Se informa porcentaje sobre matrícula vigente y "
                    "porcentaje sobre estudiantes elegibles cuyo primer "
                    "nivel observado fue técnico."
                ),
                denominador_elegible=denom_tecnico,
            )
        )
    else:
        vigente["_NIVEL_PRIMER_INGRESO"] = ""
        vigente["_INGRESO_TECNICO"] = False
        vigente["_TECNICO_A_PROFESIONAL"] = False

        kpis.append(
            _crear_kpi(
                "KPI_INGRESO_PROF_DIRECTO",
                (
                    "Estudiantes vigentes que ingresaron directamente "
                    "a carreras profesionales"
                ),
                None,
                total_matricula,
                None,
                "NO_IMPLEMENTABLE_SIN_HISTORICO",
                "Histórico institucional no localizado",
                "Se requiere histórico multianual por persona.",
                denominador_elegible=len(profesionales),
            )
        )

        kpis.append(
            _crear_kpi(
                "KPI_TECNICO_A_PROFESIONAL",
                (
                    "Estudiantes que ingresaron a carrera técnica y "
                    "posteriormente continuaron en carrera profesional"
                ),
                None,
                total_matricula,
                None,
                "NO_IMPLEMENTABLE_SIN_HISTORICO",
                "Histórico institucional no localizado",
                "Se requiere histórico multianual por persona.",
            )
        )

    col_codigo_programa = _buscar_columna(
        vigente,
        nombres=(
            "CODCARPR",
            "CODIGOCARRERA",
            "CODIGO_UNICO",
            "CODIGO_PROGRAMA",
        ),
    )
    col_nombre_programa = _buscar_columna(
        vigente,
        nombres=(
            "NOMBRE_L",
            "NOMBRE_CARRERA",
            "CARRERA",
            "PROGRAMA",
        ),
    )
    col_salida = _buscar_columna(
        vigente,
        nombres=(
            "TIENE_SALIDA_INTERMEDIA",
            "SALIDA_INTERMEDIA",
            "TITULO_INTERMEDIO",
        ),
    )

    codigos_salida = {
        _texto(x)
        for x in config.get(
            "codigos_salida_intermedia",
            [],
        )
    }
    patrones_salida = tuple(
        config.get(
            "programas_salida_intermedia",
            [],
        )
    )

    vigente["_PROGRAMA_SALIDA_INTERMEDIA"] = False

    if col_salida:
        vigente["_PROGRAMA_SALIDA_INTERMEDIA"] = vigente[
            col_salida
        ].map(_afirmativo)

    if col_codigo_programa and codigos_salida:
        vigente["_PROGRAMA_SALIDA_INTERMEDIA"] |= vigente[
            col_codigo_programa
        ].map(_texto).isin(codigos_salida)

    if col_nombre_programa and patrones_salida:
        vigente["_PROGRAMA_SALIDA_INTERMEDIA"] |= vigente[
            col_nombre_programa
        ].map(
            lambda x: _coincide(x, patrones_salida)
        )

    profesionales_salida = vigente[
        vigente["_NIVEL_PROGRAMA"].isin(
            {"PROFESIONAL", "PROFESIONAL_CONTINUIDAD"}
        )
        & vigente["_PROGRAMA_SALIDA_INTERMEDIA"]
    ].copy()

    salida_configurada = (
        col_salida is not None
        or bool(codigos_salida)
        or bool(patrones_salida)
    )

    if salida_configurada and historico is not None:
        col_estado = _buscar_columna(
            historico,
            nombres=(
                "ESTADOACADEMICO",
                "SITUACION",
                "ESTADO",
                "ESTADO_TITULO",
            ),
        )

        historico["_ES_TITULADO"] = (
            _serie_texto_combinada(
                historico,
                [col_estado],
            ).map(
                lambda x: _coincide(
                    x,
                    PATRONES_TITULADO,
                )
            )
            if col_estado
            else False
        )

        titulados_tecnicos = set(
            historico.loc[
                historico["_ES_TITULADO"]
                & historico["_NIVEL_PROGRAMA"].eq("TECNICO"),
                "_LLAVE_PERSONA",
            ]
        )

        profesionales_salida[
            "_OBTUVO_TITULO_TECNICO"
        ] = profesionales_salida["_LLAVE_PERSONA"].isin(
            titulados_tecnicos
        )

        n_titulo_intermedio = int(
            profesionales_salida[
                "_OBTUVO_TITULO_TECNICO"
            ].sum()
        )
        denom_salida = len(profesionales_salida)

        kpis.append(
            _crear_kpi(
                "KPI_TITULO_TECNICO_SALIDA_INTERMEDIA",
                (
                    "Estudiantes de carreras profesionales con salida "
                    "intermedia que obtuvieron título técnico"
                ),
                n_titulo_intermedio,
                total_matricula,
                denom_salida,
                "CALCULADO",
                (
                    "Mapa institucional de salida intermedia + "
                    "histórico de titulaciones"
                ),
                (
                    "El porcentaje elegible usa como denominador a "
                    "estudiantes vigentes en programas profesionales "
                    "configurados con salida intermedia."
                ),
                denominador_elegible=denom_salida,
            )
        )
    else:
        profesionales_salida[
            "_OBTUVO_TITULO_TECNICO"
        ] = False

        kpis.append(
            _crear_kpi(
                "KPI_TITULO_TECNICO_SALIDA_INTERMEDIA",
                (
                    "Estudiantes de carreras profesionales con salida "
                    "intermedia que obtuvieron título técnico"
                ),
                None,
                total_matricula,
                None,
                "REQUIERE_MAPEO_INSTITUCIONAL",
                "config/trayectorias_formativas.json",
                (
                    "Se deben cargar códigos o patrones oficiales de "
                    "las carreras profesionales que poseen salida "
                    "intermedia. El sistema no los infiere."
                ),
            )
        )

    diplomados_frames = []

    for nombre, df in dataframes.items():
        nombre_n = _texto(nombre)

        if "diplom" in nombre_n or "posgrado" in nombre_n:
            temporal = _agregar_llaves(df.copy())
            temporal["_FUENTE_DF"] = nombre
            diplomados_frames.append(temporal)
            continue

        col_programa = _buscar_columna(
            df,
            nombres=(
                "NOMBRE_L",
                "PROGRAMA",
                "NOMBRE_PROGRAMA",
                "DESCRIPCION",
            ),
        )

        if col_programa:
            mascara = df[col_programa].map(
                lambda x: _coincide(
                    x,
                    PATRONES_DIPLOMADO,
                )
            )
            if mascara.any():
                temporal = _agregar_llaves(
                    df.loc[mascara].copy()
                )
                temporal["_FUENTE_DF"] = nombre
                diplomados_frames.append(temporal)

    if diplomados_frames:
        diplomados = pd.concat(
            diplomados_frames,
            ignore_index=True,
            sort=False,
        ).drop_duplicates(
            subset=["_LLAVE_PERSONA"],
            keep="first",
        )

        internos_vigentes = set(vigente["_LLAVE_PERSONA"])
        titulados_regulares = set()

        if historico is not None:
            col_estado_hist = _buscar_columna(
                historico,
                nombres=(
                    "ESTADOACADEMICO",
                    "SITUACION",
                    "ESTADO",
                ),
            )

            if col_estado_hist:
                estado_hist = historico[
                    col_estado_hist
                ].map(_texto)

                es_titulado = estado_hist.map(
                    lambda x: _coincide(
                        x,
                        PATRONES_TITULADO,
                    )
                )
                es_regular = ~historico[
                    "_NIVEL_PROGRAMA"
                ].eq("NO_CLASIFICADO")

                titulados_regulares = set(
                    historico.loc[
                        es_titulado & es_regular,
                        "_LLAVE_PERSONA",
                    ]
                )

        diplomados["_TIPO_PARTICIPANTE"] = np.where(
            diplomados["_LLAVE_PERSONA"].isin(
                internos_vigentes | titulados_regulares
            ),
            "INTERNO",
            "EXTERNO",
        )

        total_diplomados = len(diplomados)
        internos = int(
            diplomados["_TIPO_PARTICIPANTE"].eq(
                "INTERNO"
            ).sum()
        )
        externos = int(
            diplomados["_TIPO_PARTICIPANTE"].eq(
                "EXTERNO"
            ).sum()
        )

        universo_ampliado = total_matricula + externos

        kpis.append(
            _crear_kpi(
                "KPI_DIPLOMADOS_TOTAL",
                "Participantes matriculados en diplomados",
                total_diplomados,
                universo_ampliado,
                total_diplomados,
                "CALCULADO",
                (
                    "Registros identificados como diplomado/posgrado "
                    "en las fuentes disponibles"
                ),
                (
                    "Porcentaje calculado sobre matrícula regular "
                    "vigente más participantes externos únicos."
                ),
                denominador_elegible=total_diplomados,
            )
        )

        kpis.append(
            _crear_kpi(
                "KPI_DIPLOMADOS_INTERNOS",
                (
                    "Participantes internos matriculados en diplomados"
                ),
                internos,
                universo_ampliado,
                total_diplomados,
                "CALCULADO",
                (
                    "Cruce por persona con matrícula vigente o "
                    "titulación regular IPSS"
                ),
                (
                    "Interno: matrícula regular vigente o evidencia "
                    "de titulación en un programa regular IPSS."
                ),
                denominador_elegible=total_diplomados,
            )
        )

        kpis.append(
            _crear_kpi(
                "KPI_DIPLOMADOS_EXTERNOS",
                (
                    "Participantes externos matriculados en diplomados"
                ),
                externos,
                universo_ampliado,
                total_diplomados,
                "CALCULADO",
                "Complemento de la clasificación de participantes",
                (
                    "Externo: no se encontró matrícula vigente ni "
                    "evidencia de titulación regular IPSS."
                ),
                denominador_elegible=total_diplomados,
            )
        )
    else:
        diplomados = pd.DataFrame(
            columns=[
                "_LLAVE_PERSONA",
                "_TIPO_PARTICIPANTE",
            ]
        )

        for codigo, indicador in (
            (
                "KPI_DIPLOMADOS_TOTAL",
                "Participantes matriculados en diplomados",
            ),
            (
                "KPI_DIPLOMADOS_INTERNOS",
                "Participantes internos matriculados en diplomados",
            ),
            (
                "KPI_DIPLOMADOS_EXTERNOS",
                "Participantes externos matriculados en diplomados",
            ),
        ):
            kpis.append(
                _crear_kpi(
                    codigo,
                    indicador,
                    None,
                    total_matricula,
                    None,
                    "NO_IMPLEMENTABLE_SIN_FUENTE",
                    "Fuente de diplomados no localizada",
                    (
                        "El dataframe de diplomados/posgrado no fue "
                        "encontrado en el namespace del pipeline."
                    ),
                )
            )

    resumen = pd.DataFrame(kpis)

    qa = pd.DataFrame(
        [
            {
                "CONTROL": "MATRICULA_VIGENTE",
                "VALOR": total_matricula,
                "ESTADO": "OK",
                "DETALLE": f"DataFrame seleccionado: {nombre_vigente}",
            },
            {
                "CONTROL": "HISTORICO_INSTITUCIONAL",
                "VALOR": (
                    len(historico)
                    if historico is not None
                    else 0
                ),
                "ESTADO": (
                    "OK"
                    if historico is not None
                    else "NO_LOCALIZADO"
                ),
                "DETALLE": (
                    f"DataFrame seleccionado: {nombre_historico}"
                ),
            },
            {
                "CONTROL": "ENCUESTA",
                "VALOR": (
                    len(encuesta)
                    if encuesta is not None
                    else 0
                ),
                "ESTADO": (
                    "OK"
                    if encuesta is not None
                    else "NO_LOCALIZADA"
                ),
                "DETALLE": (
                    f"DataFrame seleccionado: {nombre_encuesta}"
                ),
            },
            {
                "CONTROL": "COBERTURA_EMTP",
                "VALOR": (
                    dato_emtp / total_matricula
                    if total_matricula
                    else np.nan
                ),
                "ESTADO": (
                    "OK"
                    if dato_emtp == total_matricula
                    else "COBERTURA_PARCIAL"
                ),
                "DETALLE": (
                    f"{dato_emtp} de {total_matricula} "
                    "estudiantes con información utilizable."
                ),
            },
            {
                "CONTROL": "COBERTURA_CFT",
                "VALOR": (
                    dato_cft / total_matricula
                    if total_matricula
                    else np.nan
                ),
                "ESTADO": (
                    "OK"
                    if dato_cft == total_matricula
                    else "COBERTURA_PARCIAL"
                ),
                "DETALLE": (
                    f"{dato_cft} de {total_matricula} "
                    "estudiantes con información utilizable."
                ),
            },
            {
                "CONTROL": "MAPEO_SALIDA_INTERMEDIA",
                "VALOR": int(salida_configurada),
                "ESTADO": (
                    "OK"
                    if salida_configurada
                    else "REQUIERE_MAPEO"
                ),
                "DETALLE": (
                    "Configurar códigos/patrones oficiales en "
                    "config/trayectorias_formativas.json."
                ),
            },
        ]
    )

    definiciones = pd.DataFrame(
        [
            {
                "INDICADOR": "Proveniencia EMTP",
                "DEFINICION_OPERACIONAL": (
                    "Estudiante vigente con evidencia administrativa "
                    "o respuesta de encuesta que identifica enseñanza "
                    "media técnico-profesional."
                ),
                "DENOMINADOR_PRINCIPAL": "Matrícula regular vigente",
                "OBSERVACION": (
                    "La cobertura se informa separadamente."
                ),
            },
            {
                "INDICADOR": "Proveniencia CFT",
                "DEFINICION_OPERACIONAL": (
                    "Estudiante vigente con formación superior previa "
                    "en un Centro de Formación Técnica."
                ),
                "DENOMINADOR_PRINCIPAL": "Matrícula regular vigente",
                "OBSERVACION": (
                    "Usa evidencia administrativa y encuesta."
                ),
            },
            {
                "INDICADOR": "Ingreso profesional directo",
                "DEFINICION_OPERACIONAL": (
                    "El primer programa regular observado en el "
                    "histórico institucional es profesional."
                ),
                "DENOMINADOR_PRINCIPAL": (
                    "Matrícula regular vigente"
                ),
                "OBSERVACION": (
                    "También se informa porcentaje entre estudiantes "
                    "vigentes de carreras profesionales."
                ),
            },
            {
                "INDICADOR": "Título técnico de salida intermedia",
                "DEFINICION_OPERACIONAL": (
                    "Estudiante vigente en carrera profesional "
                    "configurada con salida intermedia y con evidencia "
                    "de título técnico."
                ),
                "DENOMINADOR_PRINCIPAL": (
                    "Estudiantes vigentes en carreras profesionales "
                    "con salida intermedia"
                ),
                "OBSERVACION": (
                    "Requiere mapa institucional explícito."
                ),
            },
            {
                "INDICADOR": "Continuidad técnico-profesional",
                "DEFINICION_OPERACIONAL": (
                    "Persona cuyo primer nivel observado fue técnico "
                    "y que posteriormente registra matrícula "
                    "profesional dentro del IPSS."
                ),
                "DENOMINADOR_PRINCIPAL": (
                    "Matrícula regular vigente"
                ),
                "OBSERVACION": (
                    "También se informa porcentaje entre quienes "
                    "iniciaron en nivel técnico."
                ),
            },
            {
                "INDICADOR": "Diplomados internos",
                "DEFINICION_OPERACIONAL": (
                    "Participantes de diplomados con matrícula vigente "
                    "o titulación en un programa regular IPSS."
                ),
                "DENOMINADOR_PRINCIPAL": (
                    "Total de participantes únicos en diplomados"
                ),
                "OBSERVACION": "",
            },
            {
                "INDICADOR": "Diplomados externos",
                "DEFINICION_OPERACIONAL": (
                    "Participantes de diplomados sin matrícula vigente "
                    "ni titulación regular identificada en IPSS."
                ),
                "DENOMINADOR_PRINCIPAL": (
                    "Total de participantes únicos en diplomados"
                ),
                "OBSERVACION": "",
            },
        ]
    )

    columnas_detalle = [
        c for c in (
            "_LLAVE_PERSONA",
            "_LLAVE_CODCLI",
            "_LLAVE_RUT",
            "_LLAVE_TOKEN",
            col_nombre_programa,
            col_codigo_programa,
            "_NIVEL_PROGRAMA",
            "_NIVEL_PRIMER_INGRESO",
            "_PROVIENE_EMTP",
            "_EMTP_CON_DATO",
            "_FUENTE_EMTP",
            "_PROVIENE_CFT",
            "_CFT_CON_DATO",
            "_FUENTE_CFT",
            "_INGRESO_TECNICO",
            "_TECNICO_A_PROFESIONAL",
            "_PROGRAMA_SALIDA_INTERMEDIA",
        )
        if c and c in vigente.columns
    ]

    detalle = vigente[columnas_detalle].copy()

    with pd.ExcelWriter(
        archivo_salida,
        engine="openpyxl",
    ) as writer:
        resumen.to_excel(
            writer,
            sheet_name="RESUMEN_KPI",
            index=False,
        )
        detalle.to_excel(
            writer,
            sheet_name="DETALLE_MATRICULA",
            index=False,
        )
        detalle[
            detalle["_PROVIENE_EMTP"]
            if "_PROVIENE_EMTP" in detalle.columns
            else pd.Series(False, index=detalle.index)
        ].to_excel(
            writer,
            sheet_name="PROVENIENCIA_EMTP",
            index=False,
        )
        detalle[
            detalle["_PROVIENE_CFT"]
            if "_PROVIENE_CFT" in detalle.columns
            else pd.Series(False, index=detalle.index)
        ].to_excel(
            writer,
            sheet_name="PROVENIENCIA_CFT",
            index=False,
        )
        detalle[
            detalle["_NIVEL_PROGRAMA"].isin(
                {"PROFESIONAL", "PROFESIONAL_CONTINUIDAD"}
            )
            if "_NIVEL_PROGRAMA" in detalle.columns
            else pd.Series(False, index=detalle.index)
        ].to_excel(
            writer,
            sheet_name="INGRESO_PROFESIONAL",
            index=False,
        )
        profesionales_salida.to_excel(
            writer,
            sheet_name="SALIDA_INTERMEDIA",
            index=False,
        )
        detalle[
            detalle["_TECNICO_A_PROFESIONAL"]
            if "_TECNICO_A_PROFESIONAL" in detalle.columns
            else pd.Series(False, index=detalle.index)
        ].to_excel(
            writer,
            sheet_name="TECNICO_A_PROFESIONAL",
            index=False,
        )
        diplomados.to_excel(
            writer,
            sheet_name="DIPLOMADOS",
            index=False,
        )
        qa.to_excel(
            writer,
            sheet_name="QA_COBERTURA",
            index=False,
        )
        definiciones.to_excel(
            writer,
            sheet_name="DEFINICIONES",
            index=False,
        )

    _formatear_excel(archivo_salida)

    print(f"[B13] Matrícula vigente: {total_matricula}")
    print(
        f"[B13] EMTP identificados: {n_emtp} "
        f"| casos con dato: {dato_emtp}"
    )
    print(
        f"[B13] CFT identificados: {n_cft} "
        f"| casos con dato: {dato_cft}"
    )
    print(f"[B13] Archivo generado: {archivo_salida}")
    print(
        "[✔️ OK] BLOQUE 13 - Proveniencia y trayectorias "
        "formativas completado correctamente"
    )

    return archivo_salida
