from __future__ import annotations

from datetime import datetime
from pathlib import Path
import gc
import hashlib
import json
import time

import pandas as pd


RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular")
SCRIPT_PRINCIPAL = RAIZ / "scripts" / "consolidar_mu2026_por_codcli.py"

ARCHIVO_4070 = (
    RAIZ
    / "control"
    / "punto_0_carga_principal_mu2026"
    / "archivos_congelados"
    / "PARA_SUBIR_DESKTOP__matricula_unificada_2026_pregrado_PARA_SUBIR.csv"
)

ARCHIVO_95 = (
    RAIZ
    / "control"
    / "auditoria_mu2026_punto0_complemento95"
    / "archivos_congelados"
    / "complemento_95"
    / "matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv"
)

HASH_ARCHIVO_95_ESPERADO = (
    "9a6bc998c19282da421d6e9aa51606d94"
    "d886a87bcf958f74efb40109be62c6d"
)

CARPETA_RECONSTRUIDA = (
    RAIZ
    / "resultados"
    / "auditoria_multicodcli_mu2026_reconstruida_desde_cero"
)

ARCHIVO_30 = (
    CARPETA_RECONSTRUIDA
    / "03_archivos_rectificacion"
    / "RECTIFICACION_MU2026_RECONSTRUIDA_DESDE_CERO.csv"
)

SALIDA_BASE = (
    CARPETA_RECONSTRUIDA
    / "03_archivos_rectificacion"
    / "consolidacion_codcli"
)

CATALOGO_CODCLI = SALIDA_BASE / "CATALOGO_CODCLI_COMPLETO.csv.gz"
MANIFIESTO_CATALOGO = SALIDA_BASE / "MANIFIESTO_CATALOGO_CODCLI.json"
INVENTARIO_CATALOGO = SALIDA_BASE / "INVENTARIO_FUENTES_CATALOGO_CODCLI.csv"

SALIDA_FASE2 = SALIDA_BASE / "fase2_asignacion_codcli"
ASIGNACION_95 = SALIDA_FASE2 / "ASIGNACION_CODCLI_95.csv"
ASIGNACION_30 = SALIDA_FASE2 / "ASIGNACION_CODCLI_30.csv"
EXCEL_CONFLICTOS = SALIDA_FASE2 / "CONFLICTOS_ASIGNACION_CODCLI_FASE2.xlsx"
EXCEL_RESUMEN = SALIDA_FASE2 / "RESUMEN_ASIGNACION_CODCLI_FASE2.xlsx"
MANIFIESTO_FASE2 = SALIDA_FASE2 / "MANIFIESTO_FASE2_ASIGNACION_CODCLI.json"
LOG_FASE2 = SALIDA_FASE2 / "LOG_FASE2_ASIGNACION_CODCLI.txt"
ESTADO_FASE2 = SALIDA_FASE2 / "ESTADO_FASE2_ASIGNACION_CODCLI.txt"

HASH_CATALOGO_ESPERADO = (
    "a604e9d044363ef5e314e0ddd42590bbdb4fb9581e145ac9d8b9f913a7e22ec7"
)

METRICAS_CATALOGO_ESPERADAS = {
    "filas": 1_719_162,
    "columnas": 9,
    "codcli_distintos": 14_229,
    "rut_distintos": 18_151,
    "ofertas_distintas": 138,
}

COLUMNAS_REQUERIDAS_CATALOGO = [
    "CODCLI",
    "RUT_NORM",
    "OFERTA_SIES",
    "ARCHIVO_CODCLI",
    "HOJA_CODCLI",
    "FILA_CODCLI",
    "COLUMNA_CODCLI",
    "COLUMNA_RUT",
    "COLUMNA_OFERTA",
]

CLASIFICACIONES = [
    "CODCLI_ASIGNADO_INEQUIVOCAMENTE",
    "MAS_DE_UN_CODCLI_MISMO_RUT_OFERTA",
    "CODCLI_UNICO_POR_RUT_PERO_OFERTA_DISTINTA",
    "VARIOS_CODCLI_POR_RUT_SIN_OFERTA_EXACTA",
    "SIN_CODCLI_EN_CATALOGO",
    "CONFLICTO_DE_FUENTE",
]

MAX_FILAS_EXCEL = 1_048_576
MENSAJES_LOG: list[str] = []


def log(texto: str = "") -> None:
    texto = str(texto)
    print(texto, flush=True)
    MENSAJES_LOG.append(texto)
    try:
        SALIDA_FASE2.mkdir(parents=True, exist_ok=True)
        LOG_FASE2.write_text(
            "\n".join(MENSAJES_LOG) + "\n",
            encoding="utf-8",
        )
    except Exception:
        pass


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def cargar_nucleo_script_principal() -> dict:
    texto = SCRIPT_PRINCIPAL.read_text(encoding="utf-8")
    posicion = texto.find("# INICIO")
    if posicion == -1:
        raise RuntimeError(
            "No se encontro el marcador '# INICIO' en el script principal."
        )

    espacio: dict = {
        "__file__": str(SCRIPT_PRINCIPAL),
        "__name__": "fase2_core_consolidar_mu2026",
    }
    exec(compile(texto[:posicion], str(SCRIPT_PRINCIPAL), "exec"), espacio)
    return espacio


def escribir_estado(datos: dict) -> None:
    SALIDA_FASE2.mkdir(parents=True, exist_ok=True)
    ESTADO_FASE2.write_text(
        "\n".join(f"{clave}: {valor}" for clave, valor in datos.items())
        + "\n",
        encoding="utf-8",
    )


def guardar_bloqueo(motivo: str, detalles: dict | None = None) -> None:
    datos = {
        "estado": "FASE2_BLOQUEADA",
        "motivo": motivo,
        "fin": datetime.now().isoformat(timespec="seconds"),
    }
    if detalles:
        datos.update({f"detalle_{k}": v for k, v in detalles.items()})
    escribir_estado(datos)
    raise RuntimeError(motivo)


def normalizar_df_texto(df: pd.DataFrame) -> pd.DataFrame:
    salida = df.copy()
    for columna in salida.columns:
        salida[columna] = (
            salida[columna]
            .fillna("")
            .astype(str)
            .str.strip()
        )
    return salida


def leer_csv_salida(ruta: Path) -> pd.DataFrame:
    return pd.read_csv(
        ruta,
        sep=";",
        dtype=str,
        encoding="utf-8",
        keep_default_na=False,
        na_filter=False,
        low_memory=False,
    )


def escribir_csv_salida(df: pd.DataFrame, ruta: Path) -> None:
    normalizar_df_texto(df).to_csv(
        ruta,
        sep=";",
        index=False,
        encoding="utf-8",
        lineterminator="\n",
    )


def diferencias_dataframe(a: pd.DataFrame, b: pd.DataFrame) -> int:
    a_norm = normalizar_df_texto(a)
    b_norm = normalizar_df_texto(b)
    if list(a_norm.columns) != list(b_norm.columns) or a_norm.shape != b_norm.shape:
        return -1
    return int((a_norm.ne(b_norm)).to_numpy().sum())


def validar_sin_encabezado_y_delimitador(ruta: Path, columnas_mu: list[str]) -> None:
    primera_linea = ruta.read_text(encoding="utf-8-sig", errors="replace").splitlines()[0]
    partes = primera_linea.split(";")

    if len(partes) != 32:
        guardar_bloqueo(
            "FUENTE_OPERATIVA_SIN_32_COLUMNAS_POR_DELIMITADOR",
            {"ruta": str(ruta), "columnas_detectadas": len(partes)},
        )

    if [parte.strip() for parte in partes] == columnas_mu:
        guardar_bloqueo(
            "FUENTE_OPERATIVA_CON_ENCABEZADO_DETECTADO",
            {"ruta": str(ruta)},
        )


def metricas_catalogo(df: pd.DataFrame) -> dict:
    return {
        "filas": int(len(df)),
        "columnas": int(df.shape[1]),
        "codcli_distintos": int(df["CODCLI"].nunique()),
        "rut_distintos": int(
            df.loc[df["RUT_NORM"].ne(""), "RUT_NORM"].nunique()
        ),
        "ofertas_distintas": int(
            df.loc[df["OFERTA_SIES"].ne(""), "OFERTA_SIES"].nunique()
        ),
    }


def validar_y_cargar_catalogo() -> tuple[pd.DataFrame, dict, float]:
    if not MANIFIESTO_CATALOGO.exists():
        guardar_bloqueo("MANIFIESTO_CATALOGO_NO_EXISTE")

    if not CATALOGO_CODCLI.exists():
        guardar_bloqueo("CATALOGO_CODCLI_NO_EXISTE")

    try:
        manifiesto = json.loads(
            MANIFIESTO_CATALOGO.read_text(encoding="utf-8")
        )
    except Exception as exc:
        guardar_bloqueo(
            "MANIFIESTO_CATALOGO_ILEGIBLE",
            {"error": f"{type(exc).__name__}: {exc}"},
        )

    catalogo_info = manifiesto.get("catalogo", {})
    validacion = manifiesto.get("validacion", {})
    metricas_manifiesto = manifiesto.get("metricas", {})

    if catalogo_info.get("ruta") != str(CATALOGO_CODCLI):
        guardar_bloqueo(
            "RUTA_CATALOGO_NO_COINCIDE_CON_MANIFIESTO",
            {"ruta_manifestada": catalogo_info.get("ruta", "")},
        )

    if catalogo_info.get("formato") != "csv_gzip":
        guardar_bloqueo(
            "FORMATO_CATALOGO_NO_COMPATIBLE",
            {"formato": catalogo_info.get("formato", "")},
        )

    hash_real = sha256(CATALOGO_CODCLI)
    if hash_real != catalogo_info.get("sha256"):
        guardar_bloqueo(
            "HASH_CATALOGO_NO_COINCIDE_CON_MANIFIESTO",
            {
                "hash_real": hash_real,
                "hash_manifiesto": catalogo_info.get("sha256", ""),
            },
        )

    if hash_real != HASH_CATALOGO_ESPERADO:
        guardar_bloqueo(
            "HASH_CATALOGO_NO_COINCIDE_CON_ESPERADO_FASE2",
            {"hash_real": hash_real},
        )

    if validacion.get("estado") != "VALIDO":
        guardar_bloqueo(
            "MANIFIESTO_CATALOGO_NO_VALIDO",
            {"estado": validacion.get("estado", "")},
        )

    if validacion.get("diferencias_memoria_relectura") != 0:
        guardar_bloqueo(
            "CATALOGO_CON_DIFERENCIAS_MEMORIA_RELECTURA",
            {
                "diferencias": validacion.get(
                    "diferencias_memoria_relectura", ""
                )
            },
        )

    for clave, valor in METRICAS_CATALOGO_ESPERADAS.items():
        if metricas_manifiesto.get(clave) != valor:
            guardar_bloqueo(
                "METRICA_MANIFIESTO_CATALOGO_NO_COINCIDE",
                {
                    "metrica": clave,
                    "esperado": valor,
                    "obtenido": metricas_manifiesto.get(clave),
                },
            )

    log("Cargando catalogo persistido desde csv.gz...")
    inicio = time.perf_counter()
    catalogo = pd.read_csv(
        CATALOGO_CODCLI,
        sep=";",
        dtype=str,
        encoding="utf-8",
        compression="gzip",
        keep_default_na=False,
        na_filter=False,
        low_memory=False,
    )
    tiempo_carga = round(time.perf_counter() - inicio, 3)
    catalogo = normalizar_df_texto(catalogo)

    faltantes = [
        columna
        for columna in COLUMNAS_REQUERIDAS_CATALOGO
        if columna not in catalogo.columns
    ]
    if faltantes:
        guardar_bloqueo(
            "CATALOGO_SIN_COLUMNAS_REQUERIDAS",
            {"columnas_faltantes": ",".join(faltantes)},
        )

    metricas_reales = metricas_catalogo(catalogo)
    for clave, valor in METRICAS_CATALOGO_ESPERADAS.items():
        if metricas_reales.get(clave) != valor:
            guardar_bloqueo(
                "METRICA_REAL_CATALOGO_NO_COINCIDE",
                {
                    "metrica": clave,
                    "esperado": valor,
                    "obtenido": metricas_reales.get(clave),
                },
            )

    return catalogo, manifiesto, tiempo_carga


def validar_fuentes_operativas(core: dict) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    columnas_mu = core["COLUMNAS_MU"]
    leer_csv_32 = core["leer_csv_32"]

    hashes_antes = {
        "carga_principal_4070": sha256(ARCHIVO_4070),
        "complemento_95": sha256(ARCHIVO_95),
        "rectificacion_30": sha256(ARCHIVO_30),
    }

    if hashes_antes["complemento_95"] != HASH_ARCHIVO_95_ESPERADO:
        guardar_bloqueo(
            "HASH_COMPLEMENTO_95_NO_COINCIDE",
            {
                "esperado": HASH_ARCHIVO_95_ESPERADO,
                "obtenido": hashes_antes["complemento_95"],
            },
        )

    validar_sin_encabezado_y_delimitador(ARCHIVO_95, columnas_mu)
    validar_sin_encabezado_y_delimitador(ARCHIVO_30, columnas_mu)

    df_95, encoding_95 = leer_csv_32(ARCHIVO_95)
    df_30, encoding_30 = leer_csv_32(ARCHIVO_30)

    if len(df_95) != 95:
        guardar_bloqueo(
            "COMPLEMENTO_95_NO_TIENE_95_FILAS",
            {"filas": len(df_95)},
        )

    if len(df_30) != 30:
        guardar_bloqueo(
            "RECTIFICACION_30_NO_TIENE_30_FILAS",
            {"filas": len(df_30)},
        )

    if len(columnas_mu) != 32:
        guardar_bloqueo(
            "CONFIGURACION_MU_NO_TIENE_32_COLUMNAS",
            {"columnas": len(columnas_mu)},
        )

    controles = {
        "hashes_antes": hashes_antes,
        "encoding_95": encoding_95,
        "encoding_30": encoding_30,
        "filas_95": len(df_95),
        "filas_30": len(df_30),
        "columnas_mu": len(columnas_mu),
    }

    return df_95, df_30, controles


def lista_unica(serie: pd.Series) -> list[str]:
    return sorted(
        {
            str(valor).strip()
            for valor in serie.fillna("").astype(str)
            if str(valor).strip()
        }
    )


def unir_valores(valores: list[str]) -> str:
    return " || ".join(valores)


def evidencia_detalle(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "cantidad_evidencias": 0,
            "archivos": "",
            "hojas": "",
            "filas": "",
        }

    return {
        "cantidad_evidencias": int(len(df)),
        "archivos": unir_valores(lista_unica(df["ARCHIVO_CODCLI"])),
        "hojas": unir_valores(lista_unica(df["HOJA_CODCLI"])),
        "filas": unir_valores(lista_unica(df["FILA_CODCLI"])),
    }


def conflicto_fuente_codcli(
    catalogo: pd.DataFrame,
    codcli: str,
    rut_operativo: str,
    oferta_operativa: str,
) -> tuple[bool, str]:
    evidencia = catalogo.loc[catalogo["CODCLI"].eq(codcli)].copy()
    if evidencia.empty:
        return False, ""

    ruts = lista_unica(evidencia.loc[evidencia["RUT_NORM"].ne(""), "RUT_NORM"])
    ofertas = lista_unica(
        evidencia.loc[evidencia["OFERTA_SIES"].ne(""), "OFERTA_SIES"]
    )

    ruts_incompatibles = [rut for rut in ruts if rut != rut_operativo]
    ofertas_incompatibles = [
        oferta for oferta in ofertas if oferta != oferta_operativa
    ]

    if ruts_incompatibles or ofertas_incompatibles:
        detalle = (
            f"CODCLI={codcli}; "
            f"RUTS_CATALOGO={unir_valores(ruts)}; "
            f"OFERTAS_CATALOGO={unir_valores(ofertas)}"
        )
        return True, detalle

    return False, ""


def clasificar_fila(
    fila: pd.Series,
    indice: int,
    catalogo: pd.DataFrame,
    origen: str,
    columnas_mu: list[str],
) -> dict:
    rut = str(fila["RUT_NORM"]).strip()
    oferta = str(fila["OFERTA_SIES"]).strip()

    candidatos_exactos = catalogo.loc[
        catalogo["RUT_NORM"].eq(rut) & catalogo["OFERTA_SIES"].eq(oferta)
    ].copy()

    codcli_exactos = lista_unica(candidatos_exactos["CODCLI"])

    candidatos_rut = catalogo.loc[catalogo["RUT_NORM"].eq(rut)].copy()
    codcli_rut = lista_unica(candidatos_rut["CODCLI"])
    ofertas_rut = lista_unica(candidatos_rut["OFERTA_SIES"])

    evidencia_base = candidatos_exactos
    if evidencia_base.empty and not candidatos_rut.empty:
        evidencia_base = candidatos_rut

    detalle_evidencia = evidencia_detalle(evidencia_base)

    clasificacion = ""
    codcli_asignado = ""
    metodo = ""
    asignado = "NO"
    conflicto_fuente = ""

    if len(codcli_exactos) == 1:
        codcli_candidato = codcli_exactos[0]
        hay_conflicto_fuente, conflicto_fuente = conflicto_fuente_codcli(
            catalogo,
            codcli_candidato,
            rut,
            oferta,
        )

        if hay_conflicto_fuente:
            clasificacion = "CONFLICTO_DE_FUENTE"
        else:
            clasificacion = "CODCLI_ASIGNADO_INEQUIVOCAMENTE"
            codcli_asignado = codcli_candidato
            metodo = "RUT_NORM_MAS_OFERTA_SIES_EXACTA"
            asignado = "SI"

    elif len(codcli_exactos) > 1:
        clasificacion = "MAS_DE_UN_CODCLI_MISMO_RUT_OFERTA"

    elif len(codcli_rut) == 1:
        clasificacion = "CODCLI_UNICO_POR_RUT_PERO_OFERTA_DISTINTA"
        hay_conflicto_fuente, conflicto_fuente = conflicto_fuente_codcli(
            catalogo,
            codcli_rut[0],
            rut,
            oferta,
        )
        if hay_conflicto_fuente:
            clasificacion = "CONFLICTO_DE_FUENTE"

    elif len(codcli_rut) > 1:
        clasificacion = "VARIOS_CODCLI_POR_RUT_SIN_OFERTA_EXACTA"

    else:
        clasificacion = "SIN_CODCLI_EN_CATALOGO"

    registro = {
        "ORIGEN_OPERATIVO": origen,
        "FILA_OPERATIVA": str(indice + 1),
        "CLASIFICACION": clasificacion,
        "ASIGNADO": asignado,
        "CODCLI": codcli_asignado,
        "RUT_NORM": rut,
        "OFERTA_SIES": oferta,
        "METODO_ASIGNACION": metodo,
        "CANTIDAD_EVIDENCIAS": str(detalle_evidencia["cantidad_evidencias"]),
        "CANTIDAD_EVIDENCIAS_EXACTAS": str(len(candidatos_exactos)),
        "CANTIDAD_EVIDENCIAS_RUT": str(len(candidatos_rut)),
        "CODCLI_EXACTOS": unir_valores(codcli_exactos),
        "CODCLI_DEL_RUT": unir_valores(codcli_rut),
        "OFERTAS_DEL_RUT_EN_CATALOGO": unir_valores(ofertas_rut),
        "ARCHIVOS_EVIDENCIA": detalle_evidencia["archivos"],
        "HOJAS_EVIDENCIA": detalle_evidencia["hojas"],
        "FILAS_EVIDENCIA": detalle_evidencia["filas"],
        "CONFLICTO_FUENTE_DETALLE": conflicto_fuente,
    }

    for columna in columnas_mu:
        registro[columna] = str(fila[columna]).strip()

    return registro


def asignar_operativo(
    operativo: pd.DataFrame,
    catalogo: pd.DataFrame,
    origen: str,
    columnas_mu: list[str],
) -> pd.DataFrame:
    registros = [
        clasificar_fila(fila, indice, catalogo, origen, columnas_mu)
        for indice, fila in operativo.iterrows()
    ]
    return normalizar_df_texto(pd.DataFrame(registros))


def resumen_clasificacion(df: pd.DataFrame, origen: str) -> pd.DataFrame:
    total = len(df)
    conteos = df["CLASIFICACION"].value_counts().to_dict()
    asignados = int(
        conteos.get("CODCLI_ASIGNADO_INEQUIVOCAMENTE", 0)
    )
    pendientes = total - asignados

    fila = {
        "ORIGEN_OPERATIVO": origen,
        "FILAS_OPERATIVAS": total,
        "CODCLI_ASIGNADOS_INEQUIVOCAMENTE": asignados,
        "MAS_DE_UN_CODCLI_MISMO_RUT_OFERTA": int(
            conteos.get("MAS_DE_UN_CODCLI_MISMO_RUT_OFERTA", 0)
        ),
        "CODCLI_UNICO_POR_RUT_PERO_OFERTA_DISTINTA": int(
            conteos.get("CODCLI_UNICO_POR_RUT_PERO_OFERTA_DISTINTA", 0)
        ),
        "VARIOS_CODCLI_POR_RUT_SIN_OFERTA_EXACTA": int(
            conteos.get("VARIOS_CODCLI_POR_RUT_SIN_OFERTA_EXACTA", 0)
        ),
        "SIN_CODCLI_EN_CATALOGO": int(
            conteos.get("SIN_CODCLI_EN_CATALOGO", 0)
        ),
        "CONFLICTO_DE_FUENTE": int(
            conteos.get("CONFLICTO_DE_FUENTE", 0)
        ),
        "PORCENTAJE_ASIGNADO": round((asignados / total) * 100, 4)
        if total
        else 0,
        "PORCENTAJE_PENDIENTE": round((pendientes / total) * 100, 4)
        if total
        else 0,
    }

    return pd.DataFrame([fila])


def validar_asignaciones(
    asignados_95: pd.DataFrame,
    asignados_30: pd.DataFrame,
) -> dict:
    controles = {}

    controles["filas_asignacion_95"] = len(asignados_95)
    controles["filas_asignacion_30"] = len(asignados_30)

    if len(asignados_95) != 95:
        guardar_bloqueo(
            "ASIGNACION_95_NO_TIENE_95_FILAS",
            {"filas": len(asignados_95)},
        )

    if len(asignados_30) != 30:
        guardar_bloqueo(
            "ASIGNACION_30_NO_TIENE_30_FILAS",
            {"filas": len(asignados_30)},
        )

    for nombre, df, total_esperado in [
        ("COMPLEMENTO_95", asignados_95, 95),
        ("RECTIFICACION_30", asignados_30, 30),
    ]:
        clasificaciones_invalidas = sorted(
            set(df["CLASIFICACION"]) - set(CLASIFICACIONES)
        )
        if clasificaciones_invalidas:
            guardar_bloqueo(
                "CLASIFICACION_INVALIDA",
                {
                    "origen": nombre,
                    "clasificaciones": " || ".join(clasificaciones_invalidas),
                },
            )

        suma = int(df["CLASIFICACION"].value_counts().sum())
        if suma != total_esperado:
            guardar_bloqueo(
                "SUMA_CLASIFICACIONES_NO_COINCIDE",
                {"origen": nombre, "suma": suma, "esperado": total_esperado},
            )

        asignadas = df.loc[
            df["CLASIFICACION"].eq("CODCLI_ASIGNADO_INEQUIVOCAMENTE")
        ]
        if not asignadas["CODCLI"].astype(str).str.strip().ne("").all():
            guardar_bloqueo(
                "FILA_ASIGNADA_SIN_CODCLI",
                {"origen": nombre},
            )

        conflictivas = df.loc[
            ~df["CLASIFICACION"].eq("CODCLI_ASIGNADO_INEQUIVOCAMENTE")
        ]
        if conflictivas["CODCLI"].astype(str).str.strip().ne("").any():
            guardar_bloqueo(
                "FILA_CONFLICTIVA_CON_CODCLI_ASIGNADO",
                {"origen": nombre},
            )

        controles[f"suma_clasificaciones_{nombre}"] = suma
        controles[f"clasificaciones_invalidas_{nombre}"] = ""

    return controles


def construir_catalogo_relevante(
    catalogo: pd.DataFrame,
    df_95: pd.DataFrame,
    df_30: pd.DataFrame,
    asignados_95: pd.DataFrame,
    asignados_30: pd.DataFrame,
) -> pd.DataFrame:
    ruts = set(df_95["RUT_NORM"].astype(str)) | set(df_30["RUT_NORM"].astype(str))
    ofertas = set(df_95["OFERTA_SIES"].astype(str)) | set(
        df_30["OFERTA_SIES"].astype(str)
    )
    codcli: set[str] = set()

    for df in [asignados_95, asignados_30]:
        for columna in ["CODCLI", "CODCLI_EXACTOS", "CODCLI_DEL_RUT"]:
            for valor in df[columna].astype(str):
                for parte in valor.split("||"):
                    parte = parte.strip()
                    if parte:
                        codcli.add(parte)

    ruts.discard("")
    ofertas.discard("")
    codcli.discard("")

    relevante = catalogo.loc[
        catalogo["RUT_NORM"].isin(ruts)
        | catalogo["OFERTA_SIES"].isin(ofertas)
        | catalogo["CODCLI"].isin(codcli)
    ].copy()

    return normalizar_df_texto(relevante)


def fuentes_evidencia(catalogo_relevante: pd.DataFrame) -> pd.DataFrame:
    if catalogo_relevante.empty:
        return pd.DataFrame(
            columns=[
                "ARCHIVO_CODCLI",
                "HOJA_CODCLI",
                "EVIDENCIAS",
                "CODCLI_DISTINTOS",
                "RUT_DISTINTOS",
                "OFERTAS_DISTINTAS",
            ]
        )

    return (
        catalogo_relevante.groupby(
            ["ARCHIVO_CODCLI", "HOJA_CODCLI"],
            dropna=False,
        )
        .agg(
            EVIDENCIAS=("CODCLI", "size"),
            CODCLI_DISTINTOS=("CODCLI", "nunique"),
            RUT_DISTINTOS=("RUT_NORM", "nunique"),
            OFERTAS_DISTINTAS=("OFERTA_SIES", "nunique"),
        )
        .reset_index()
        .sort_values(["EVIDENCIAS", "ARCHIVO_CODCLI"], ascending=[False, True])
    )


def escribir_hoja_segura(
    writer: pd.ExcelWriter,
    df: pd.DataFrame,
    nombre_hoja: str,
    referencia: Path,
) -> None:
    if len(df) <= MAX_FILAS_EXCEL:
        df.to_excel(writer, sheet_name=nombre_hoja, index=False)
        return

    ruta_externa = referencia.with_name(f"{nombre_hoja}.csv")
    escribir_csv_salida(df, ruta_externa)
    pd.DataFrame(
        [
            {
                "HOJA": nombre_hoja,
                "FILAS": len(df),
                "RESULTADO": "NO_ESCRITA_SUPERA_LIMITE_EXCEL",
                "REFERENCIA": str(ruta_externa),
            }
        ]
    ).to_excel(writer, sheet_name=nombre_hoja, index=False)


def controles_a_dataframe(controles: dict) -> pd.DataFrame:
    return pd.DataFrame(
        [{"CONTROL": clave, "VALOR": valor} for clave, valor in controles.items()]
    )


def hashes_salidas(rutas: list[Path]) -> dict:
    return {
        ruta.name: {
            "ruta": str(ruta),
            "sha256": sha256(ruta),
            "bytes": int(ruta.stat().st_size),
        }
        for ruta in rutas
        if ruta.exists()
    }


def main() -> int:
    inicio_total = time.perf_counter()
    inicio_iso = datetime.now().isoformat(timespec="seconds")

    SALIDA_FASE2.mkdir(parents=True, exist_ok=True)
    if LOG_FASE2.exists():
        LOG_FASE2.unlink()

    log("=" * 100)
    log("FASE 2 - ASIGNACION CODCLI 95 Y 30")
    log("=" * 100)
    log(f"Inicio: {inicio_iso}")
    log(f"Repositorio: {RAIZ}")

    core = cargar_nucleo_script_principal()
    columnas_mu = core["COLUMNAS_MU"]

    catalogo, manifiesto_catalogo, tiempo_carga_catalogo = (
        validar_y_cargar_catalogo()
    )
    log("Catalogo validado contra manifiesto.")
    log(f"Tiempo carga catalogo segundos: {tiempo_carga_catalogo}")

    df_95, df_30, controles_fuentes = validar_fuentes_operativas(core)
    log("Fuentes operativas 95 y 30 validadas.")

    log("Asignando CODCLI al complemento de 95...")
    t_asignacion = time.perf_counter()
    asignados_95 = asignar_operativo(
        df_95,
        catalogo,
        "COMPLEMENTO_95",
        columnas_mu,
    )

    log("Asignando CODCLI a la rectificacion de 30...")
    asignados_30 = asignar_operativo(
        df_30,
        catalogo,
        "RECTIFICACION_30",
        columnas_mu,
    )
    tiempo_asignacion = round(time.perf_counter() - t_asignacion, 3)

    controles_asignacion = validar_asignaciones(asignados_95, asignados_30)

    resumen_95 = resumen_clasificacion(asignados_95, "COMPLEMENTO_95")
    resumen_30 = resumen_clasificacion(asignados_30, "RECTIFICACION_30")
    resumen = pd.concat([resumen_95, resumen_30], ignore_index=True)
    resumen["TIEMPO_CARGA_CATALOGO_SEGUNDOS"] = tiempo_carga_catalogo
    resumen["TIEMPO_ASIGNACION_SEGUNDOS"] = tiempo_asignacion

    conflictos_95 = asignados_95.loc[
        ~asignados_95["CLASIFICACION"].eq("CODCLI_ASIGNADO_INEQUIVOCAMENTE")
    ].copy()
    conflictos_30 = asignados_30.loc[
        ~asignados_30["CLASIFICACION"].eq("CODCLI_ASIGNADO_INEQUIVOCAMENTE")
    ].copy()

    catalogo_relevante = construir_catalogo_relevante(
        catalogo,
        df_95,
        df_30,
        asignados_95,
        asignados_30,
    )
    fuentes = fuentes_evidencia(catalogo_relevante)

    log("Guardando salidas CSV de asignacion...")
    escribir_csv_salida(asignados_95, ASIGNACION_95)
    escribir_csv_salida(asignados_30, ASIGNACION_30)

    relectura_95 = leer_csv_salida(ASIGNACION_95)
    relectura_30 = leer_csv_salida(ASIGNACION_30)
    diferencias_95 = diferencias_dataframe(asignados_95, relectura_95)
    diferencias_30 = diferencias_dataframe(asignados_30, relectura_30)

    if diferencias_95 != 0 or diferencias_30 != 0:
        guardar_bloqueo(
            "DIFERENCIAS_RELECTURA_CSV_ASIGNACION",
            {
                "diferencias_95": diferencias_95,
                "diferencias_30": diferencias_30,
            },
        )

    hashes_despues = {
        "carga_principal_4070": sha256(ARCHIVO_4070),
        "complemento_95": sha256(ARCHIVO_95),
        "rectificacion_30": sha256(ARCHIVO_30),
    }
    fuentes_originales_modificadas = (
        controles_fuentes["hashes_antes"] != hashes_despues
    )

    if fuentes_originales_modificadas:
        guardar_bloqueo(
            "FUENTES_ORIGINALES_MODIFICADAS",
            {"hashes_despues": hashes_despues},
        )

    controles = {
        **controles_fuentes,
        **controles_asignacion,
        "hashes_despues": hashes_despues,
        "fuentes_originales_modificadas": "NO",
        "filas_catalogo_relevante": len(catalogo_relevante),
        "filas_fuentes_evidencia": len(fuentes),
        "diferencias_relectura_95": diferencias_95,
        "diferencias_relectura_30": diferencias_30,
        "tiempo_carga_catalogo_segundos": tiempo_carga_catalogo,
        "tiempo_asignacion_segundos": tiempo_asignacion,
    }
    controles_df = controles_a_dataframe(controles)

    log("Guardando Excel de conflictos y resumen...")
    with pd.ExcelWriter(EXCEL_CONFLICTOS, engine="openpyxl") as writer:
        resumen.to_excel(writer, sheet_name="RESUMEN", index=False)
        conflictos_95.to_excel(writer, sheet_name="CONFLICTOS_95", index=False)
        conflictos_30.to_excel(writer, sheet_name="CONFLICTOS_30", index=False)
        escribir_hoja_segura(
            writer,
            catalogo_relevante,
            "CATALOGO_RELEVANTE",
            EXCEL_CONFLICTOS,
        )
        fuentes.to_excel(writer, sheet_name="FUENTES_EVIDENCIA", index=False)
        controles_df.to_excel(writer, sheet_name="CONTROLES", index=False)

    with pd.ExcelWriter(EXCEL_RESUMEN, engine="openpyxl") as writer:
        resumen.to_excel(writer, sheet_name="RESUMEN", index=False)
        controles_df.to_excel(writer, sheet_name="CONTROLES", index=False)
        asignados_95.to_excel(writer, sheet_name="ASIGNACION_95", index=False)
        asignados_30.to_excel(writer, sheet_name="ASIGNACION_30", index=False)

    total_conflictos = len(conflictos_95) + len(conflictos_30)
    estado_final = (
        "FASE2_COMPLETADA_CON_CONFLICTOS"
        if total_conflictos
        else "FASE2_COMPLETADA_SIN_CONFLICTOS"
    )

    salidas_sin_manifiesto = [
        ASIGNACION_95,
        ASIGNACION_30,
        EXCEL_CONFLICTOS,
        EXCEL_RESUMEN,
        LOG_FASE2,
        ESTADO_FASE2,
    ]

    manifiesto = {
        "fase": "FASE2_ASIGNACION_CODCLI_95_30",
        "inicio": inicio_iso,
        "fin": datetime.now().isoformat(timespec="seconds"),
        "estado": estado_final,
        "reglas": {
            "llave_asignacion": "RUT_NORM + OFERTA_SIES exacta",
            "unidad_principal": "CODCLI",
            "no_reconstruir_catalogo": True,
            "no_comparar_30_vs_95": True,
            "no_comparar_con_4070": True,
            "no_generar_csv_final": True,
        },
        "catalogo": {
            "ruta": str(CATALOGO_CODCLI),
            "sha256": sha256(CATALOGO_CODCLI),
            "filas": METRICAS_CATALOGO_ESPERADAS["filas"],
            "columnas": METRICAS_CATALOGO_ESPERADAS["columnas"],
            "codcli_distintos": METRICAS_CATALOGO_ESPERADAS[
                "codcli_distintos"
            ],
            "rut_distintos": METRICAS_CATALOGO_ESPERADAS["rut_distintos"],
            "ofertas_distintas": METRICAS_CATALOGO_ESPERADAS[
                "ofertas_distintas"
            ],
            "manifiesto_estado": manifiesto_catalogo["validacion"]["estado"],
            "diferencias_memoria_relectura_fase1": manifiesto_catalogo[
                "validacion"
            ]["diferencias_memoria_relectura"],
        },
        "resumen": resumen.to_dict(orient="records"),
        "controles": controles,
        "conflictos": {
            "total": total_conflictos,
            "complemento_95": len(conflictos_95),
            "rectificacion_30": len(conflictos_30),
        },
        "salidas": hashes_salidas(salidas_sin_manifiesto),
    }

    MANIFIESTO_FASE2.write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    salidas = salidas_sin_manifiesto + [MANIFIESTO_FASE2]
    hashes = hashes_salidas(salidas)

    estado = {
        "estado": estado_final,
        "filas_asignacion_95": len(asignados_95),
        "filas_asignacion_30": len(asignados_30),
        "conflictos_total": total_conflictos,
        "conflictos_95": len(conflictos_95),
        "conflictos_30": len(conflictos_30),
        "tiempo_carga_catalogo_segundos": tiempo_carga_catalogo,
        "tiempo_asignacion_segundos": tiempo_asignacion,
        "diferencias_relectura_95": diferencias_95,
        "diferencias_relectura_30": diferencias_30,
        "fuentes_originales_modificadas": "NO",
        "manifiesto_sha256": hashes[MANIFIESTO_FASE2.name]["sha256"],
        "fin": datetime.now().isoformat(timespec="seconds"),
    }
    escribir_estado(estado)

    log("=" * 100)
    log("RESUMEN FASE 2")
    log("=" * 100)
    log(resumen.to_string(index=False))
    log(f"Conflictos totales: {total_conflictos}")

    if total_conflictos:
        muestra = pd.concat(
            [conflictos_95, conflictos_30],
            ignore_index=True,
        ).head(20)
        columnas_muestra = [
            "ORIGEN_OPERATIVO",
            "FILA_OPERATIVA",
            "CLASIFICACION",
            "RUT_NORM",
            "OFERTA_SIES",
            "CODCLI_EXACTOS",
            "CODCLI_DEL_RUT",
        ]
        log("Primeros conflictos (maximo 20):")
        log(muestra[columnas_muestra].to_string(index=False))

    log(f"Estado final: {estado_final}")
    log(f"Tiempo total segundos: {round(time.perf_counter() - inicio_total, 3)}")

    del catalogo
    gc.collect()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        log("=" * 100)
        log("FASE 2 CON ERROR O BLOQUEO")
        log("=" * 100)
        log(f"{type(exc).__name__}: {exc}")
        escribir_estado(
            {
                "estado": "FASE2_CON_ERROR_O_BLOQUEO",
                "error_tipo": type(exc).__name__,
                "error": str(exc),
                "fin": datetime.now().isoformat(timespec="seconds"),
            }
        )
        raise
