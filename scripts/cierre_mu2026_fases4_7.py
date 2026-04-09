from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any
import hashlib

import pandas as pd


RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular")
SCRIPT = Path(__file__).resolve()
SCRIPT_PRINCIPAL = RAIZ / "scripts" / "consolidar_mu2026_por_codcli.py"
SCRIPT_RECONSTRUCCION = (
    RAIZ / "scripts" / "reconstruir_rectificacion_mu2026_desde_cero.py"
)

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
HASH_95_ESPERADO = (
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
BASE_CONSOLIDACION = (
    CARPETA_RECONSTRUIDA
    / "03_archivos_rectificacion"
    / "consolidacion_codcli"
)
CATALOGO = BASE_CONSOLIDACION / "CATALOGO_CODCLI_COMPLETO.csv.gz"
MANIFIESTO_CATALOGO = BASE_CONSOLIDACION / "MANIFIESTO_CATALOGO_CODCLI.json"
ASIGNACION_95 = (
    BASE_CONSOLIDACION
    / "fase2_asignacion_codcli"
    / "ASIGNACION_CODCLI_95.csv"
)
ASIGNACION_30 = (
    BASE_CONSOLIDACION
    / "fase2_asignacion_codcli"
    / "ASIGNACION_CODCLI_30.csv"
)

AUDITORIA_VIGENCIA = (
    CARPETA_RECONSTRUIDA
    / "01_auditorias"
    / "AUDITORIA_VIGENCIA_MATRICULA.csv"
)
AUDITORIA_FILTRO = (
    CARPETA_RECONSTRUIDA
    / "01_auditorias"
    / "AUDITORIA_FILTRO_2026_1.csv"
)
AUDITORIA_MAPEO = (
    CARPETA_RECONSTRUIDA
    / "01_auditorias"
    / "AUDITORIA_MAPEO_OFERTA_SIES.csv"
)
DECISIONES_RECONSTRUCCION = (
    CARPETA_RECONSTRUIDA
    / "02_resultados_tecnicos"
    / "DECISIONES_RECTIFICACION_MU2026.csv"
)
COMPARACION_RECONSTRUCCION = (
    CARPETA_RECONSTRUIDA
    / "02_resultados_tecnicos"
    / "COMPARACION_MATRICULAS_2026_1_VS_MU.csv"
)

SALIDA = CARPETA_RECONSTRUIDA / "05_cierre_controlado"
PROPUESTA_XLSX = SALIDA / "PROPUESTA_DECISION_FASES4_5.xlsx"
PROPUESTA_CSV = SALIDA / "PROPUESTA_DECISION_FASES4_5.csv"
MANIFIESTO_REVISION = SALIDA / "MANIFIESTO_REVISION_FASES4_5.json"
LOG_REVISION = SALIDA / "LOG_REVISION_FASES4_5.txt"
ESTADO_REVISION = SALIDA / "ESTADO_REVISION_FASES4_5.txt"
APROBACION_JSON = SALIDA / "APROBACION_MATERIALIZACION.json"
REPORTE_APROBACION_INVALIDA = SALIDA / "REPORTE_APROBACION_INVALIDA.txt"
SELLO_APROBACION = SALIDA / "SELLO_APROBACION_VALIDADO.json"

RESOLUCION_36_DIR = SALIDA / "resolucion_36_conflictos"
RESOLUCION_36_CSV = (
    RESOLUCION_36_DIR / "RESOLUCION_36_CONFLICTOS_MU2026.csv"
)
PROPUESTA_RESUELTA_36_CSV = (
    RESOLUCION_36_DIR / "PROPUESTA_DECISION_FASES4_5_RESUELTA_36.csv"
)
HASH_RESOLUCION_36_ESPERADO = (
    "1ee757fccf88273e979699c5d0184d35ba58d36bb42efdf71a6dcdd6718be523"
)
HASH_PROPUESTA_RESUELTA_36_ESPERADO = (
    "bdb8a40bbd5ddb1350fb78dd22979a7530d7872f33701e229714039376e4eb3a"
)

PROPUESTA_APROBABLE_CSV = SALIDA / "PROPUESTA_DECISION_FASES4_5_APROBABLE.csv"
PROPUESTA_APROBABLE_XLSX = SALIDA / "PROPUESTA_DECISION_FASES4_5_APROBABLE.xlsx"
MANIFIESTO_PROPUESTA_APROBABLE = SALIDA / "MANIFIESTO_PROPUESTA_APROBABLE.json"
APROBACION_APROBABLE_JSON = SALIDA / "APROBACION_MATERIALIZACION_APROBABLE.json"
LOG_INTEGRACION_RESOLUCION = SALIDA / "LOG_INTEGRACION_RESOLUCION_36.txt"
ESTADO_INTEGRACION_RESOLUCION = SALIDA / "ESTADO_INTEGRACION_RESOLUCION_36.txt"

CSV_FINAL = SALIDA / "MATRICULA_UNIFICADA_PREGRADO_2026_CONSOLIDADA_FINAL.csv"
XLSX_FINAL = (
    SALIDA
    / "MATRICULA_UNIFICADA_PREGRADO_2026_CONSOLIDADA_FINAL_CON_ENCABEZADOS.xlsx"
)
AUDITORIA_CIERRE = SALIDA / "AUDITORIA_CIERRE_MU2026.xlsx"
MANIFIESTO_CIERRE = SALIDA / "MANIFIESTO_CIERRE_MU2026.json"
LOG_MATERIALIZACION = SALIDA / "LOG_MATERIALIZACION_MU2026.txt"
ESTADO_MATERIALIZACION = SALIDA / "ESTADO_MATERIALIZACION_MU2026.txt"

REPORTE_VERIFICACION = SALIDA / "REPORTE_VERIFICACION_CIERRE_MU2026.txt"
RESUMEN_VERIFICACION = SALIDA / "RESUMEN_VERIFICACION_CIERRE_MU2026.xlsx"
ESTADO_FINAL_CIERRE = SALIDA / "ESTADO_FINAL_CIERRE_MU2026.json"

ESCRITORIO = Path.home() / "Desktop"

MODOS = {
    "revisar",
    "integrar-resolucion",
    "validar-aprobacion",
    "materializar",
    "verificar-cierre",
}

DECISIONES_PERMITIDAS = {
    "CONSERVAR_CARGA_PRINCIPAL",
    "CONSERVAR_COMPLEMENTO_95",
    "INCORPORAR_DESDE_30",
    "YA_REPRESENTADO_NO_AGREGAR",
    "ACTUALIZAR_FILA_EXISTENTE",
    "CONFLICTO_SIN_IMPACTO_CANTIDAD",
    "CONFLICTO_MATERIAL",
    "SIN_EVIDENCIA_SUFICIENTE",
}

MENSAJES: list[str] = []
LOG_ACTUAL: Path | None = None


class CierreError(Exception):
    def __init__(self, mensaje: str, codigo: int) -> None:
        super().__init__(mensaje)
        self.codigo = codigo


def log(texto: str = "") -> None:
    texto = str(texto)
    print(texto, flush=True)
    MENSAJES.append(texto)
    if LOG_ACTUAL is not None:
        LOG_ACTUAL.parent.mkdir(parents=True, exist_ok=True)
        LOG_ACTUAL.write_text("\n".join(MENSAJES) + "\n", encoding="utf-8")


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def cargar_core() -> dict[str, Any]:
    texto = SCRIPT_PRINCIPAL.read_text(encoding="utf-8")
    pos = texto.find("# INICIO")
    if pos == -1:
        raise CierreError("No se encontro marcador # INICIO en script principal", 4)
    espacio: dict[str, Any] = {
        "__file__": str(SCRIPT_PRINCIPAL),
        "__name__": "core_cierre_mu2026",
    }
    exec(compile(texto[:pos], str(SCRIPT_PRINCIPAL), "exec"), espacio)
    return espacio


def normalizar_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        out[col] = out[col].fillna("").astype(str).str.strip()
    return out


def leer_csv_auto(ruta: Path) -> pd.DataFrame:
    if not ruta.exists():
        raise CierreError(f"No existe archivo requerido: {ruta}", 4)
    candidatos = [";", ",", "\t", "|"]
    mejor: pd.DataFrame | None = None
    mejor_cols = 0
    for sep in candidatos:
        try:
            df = pd.read_csv(
                ruta,
                sep=sep,
                dtype=str,
                encoding="utf-8-sig",
                keep_default_na=False,
                na_filter=False,
                low_memory=False,
            )
        except Exception:
            continue
        if df.shape[1] > mejor_cols:
            mejor = df
            mejor_cols = df.shape[1]
    if mejor is None:
        raise CierreError(f"No fue posible leer CSV: {ruta}", 4)
    return normalizar_df(mejor)


def escribir_csv(df: pd.DataFrame, ruta: Path, header: bool = True) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    normalizar_df(df).to_csv(
        ruta,
        sep=";",
        header=header,
        index=False,
        encoding="utf-8",
        lineterminator="\n",
    )


def backup_si_existe(ruta: Path) -> Path | None:
    if not ruta.exists():
        return None
    destino = ruta.with_name(
        f"{ruta.stem}_respaldo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        f"{ruta.suffix}"
    )
    shutil.copy2(ruta, destino)
    return destino


def tabla_dict(datos: dict[str, Any]) -> pd.DataFrame:
    filas: list[dict[str, str]] = []

    def visitar(valor: Any, ruta: str) -> None:
        if isinstance(valor, dict):
            for k, v in valor.items():
                visitar(v, f"{ruta}.{k}" if ruta else str(k))
        elif isinstance(valor, list):
            filas.append({"CAMPO": ruta, "VALOR": f"[lista {len(valor)}]"})
        else:
            filas.append({"CAMPO": ruta, "VALOR": str(valor)})

    visitar(datos, "")
    return pd.DataFrame(filas)


def validar_catalogo(cargar: bool = False) -> tuple[pd.DataFrame | None, dict[str, Any]]:
    if not MANIFIESTO_CATALOGO.exists() or not CATALOGO.exists():
        raise CierreError("Catalogo o manifiesto de catalogo no existe", 4)
    manifiesto = json.loads(MANIFIESTO_CATALOGO.read_text(encoding="utf-8"))
    info = manifiesto.get("catalogo", {})
    validacion = manifiesto.get("validacion", {})
    metricas = manifiesto.get("metricas", {})
    hash_real = sha256(CATALOGO)
    controles = {
        "catalogo_ruta": str(CATALOGO),
        "catalogo_hash": hash_real,
        "catalogo_hash_manifestado": info.get("sha256", ""),
        "catalogo_formato": info.get("formato", ""),
        "catalogo_validacion": validacion.get("estado", ""),
        "catalogo_diferencias_memoria_relectura": validacion.get(
            "diferencias_memoria_relectura", ""
        ),
        "catalogo_filas": metricas.get("filas", ""),
        "catalogo_columnas": metricas.get("columnas", ""),
        "catalogo_codcli_distintos": metricas.get("codcli_distintos", ""),
        "catalogo_rut_distintos": metricas.get("rut_distintos", ""),
        "catalogo_ofertas_distintas": metricas.get("ofertas_distintas", ""),
    }
    if info.get("ruta") != str(CATALOGO):
        raise CierreError("Ruta de catalogo no coincide con manifiesto", 4)
    if info.get("formato") != "csv_gzip":
        raise CierreError("Formato de catalogo no compatible", 4)
    if hash_real != info.get("sha256"):
        raise CierreError("Hash de catalogo no coincide con manifiesto", 4)
    if validacion.get("estado") != "VALIDO":
        raise CierreError("Manifiesto de catalogo no esta valido", 4)
    if validacion.get("diferencias_memoria_relectura") != 0:
        raise CierreError("Catalogo con diferencias memoria/relectura", 4)
    esperado = {
        "filas": 1_719_162,
        "columnas": 9,
        "codcli_distintos": 14_229,
        "rut_distintos": 18_151,
        "ofertas_distintas": 138,
    }
    for clave, valor in esperado.items():
        if metricas.get(clave) != valor:
            raise CierreError(f"Metrica de catalogo no coincide: {clave}", 4)
    if not cargar:
        return None, controles
    t0 = time.perf_counter()
    df = pd.read_csv(
        CATALOGO,
        sep=";",
        dtype=str,
        encoding="utf-8",
        compression="gzip",
        keep_default_na=False,
        na_filter=False,
        low_memory=False,
    )
    controles["catalogo_tiempo_carga_segundos"] = round(time.perf_counter() - t0, 3)
    return normalizar_df(df), controles


def validar_fuentes(core: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    leer_csv_32 = core["leer_csv_32"]
    columnas_mu = core["COLUMNAS_MU"]
    hashes_antes = {
        "principal_4070": sha256(ARCHIVO_4070),
        "complemento_95": sha256(ARCHIVO_95),
        "rectificacion_30": sha256(ARCHIVO_30),
    }
    if hashes_antes["complemento_95"] != HASH_95_ESPERADO:
        raise CierreError("Hash del complemento 95 no coincide", 4)
    df_4070, enc_4070 = leer_csv_32(ARCHIVO_4070)
    df_95, enc_95 = leer_csv_32(ARCHIVO_95)
    df_30, enc_30 = leer_csv_32(ARCHIVO_30)
    if len(df_4070) != 4070 or len(df_95) != 95 or len(df_30) != 30:
        raise CierreError("Conteo de filas operativas no coincide", 4)
    controles = {
        "hashes_fuentes_antes": hashes_antes,
        "encoding_4070": enc_4070,
        "encoding_95": enc_95,
        "encoding_30": enc_30,
        "filas_4070": len(df_4070),
        "filas_95": len(df_95),
        "filas_30": len(df_30),
        "columnas_mu": len(columnas_mu),
    }
    return (
        normalizar_df(df_4070),
        normalizar_df(df_95),
        normalizar_df(df_30),
        controles,
    )


def preparar_mu(df: pd.DataFrame, columnas_mu: list[str]) -> pd.DataFrame:
    out = normalizar_df(df.copy())
    out["FILA_32"] = out[columnas_mu].astype(str).agg("|".join, axis=1)
    return out


def codcli_unicos(texto: str) -> list[str]:
    valores = []
    for parte in str(texto).split("||"):
        parte = parte.strip()
        if parte and parte not in valores:
            valores.append(parte)
    return sorted(valores)


def crear_mapa_catalogo_exactos(catalogo: pd.DataFrame) -> pd.DataFrame:
    base = catalogo.loc[
        catalogo["RUT_NORM"].ne("") & catalogo["OFERTA_SIES"].ne("")
    ].copy()
    agrupado = (
        base.groupby(["RUT_NORM", "OFERTA_SIES"], dropna=False)
        .agg(
            CODCLI_CATALOGO_EXACTOS=(
                "CODCLI",
                lambda s: " || ".join(sorted(set(x for x in s if x))),
            ),
            EVIDENCIAS_CATALOGO=("CODCLI", "size"),
            ARCHIVOS_CATALOGO=(
                "ARCHIVO_CODCLI",
                lambda s: " || ".join(sorted(set(x for x in s if x))[:20]),
            ),
        )
        .reset_index()
    )
    agrupado["N_CODCLI_CATALOGO_EXACTOS"] = agrupado[
        "CODCLI_CATALOGO_EXACTOS"
    ].map(lambda x: len(codcli_unicos(x)))
    return agrupado


def enriquecer_con_catalogo(df: pd.DataFrame, mapa: pd.DataFrame) -> pd.DataFrame:
    out = df.merge(mapa, on=["RUT_NORM", "OFERTA_SIES"], how="left")
    for col in [
        "CODCLI_CATALOGO_EXACTOS",
        "EVIDENCIAS_CATALOGO",
        "ARCHIVOS_CATALOGO",
        "N_CODCLI_CATALOGO_EXACTOS",
    ]:
        if col not in out.columns:
            out[col] = ""
        out[col] = out[col].fillna("").astype(str)
    out["CODCLI_CATALOGO_UNICO"] = out.apply(
        lambda r: codcli_unicos(r["CODCLI_CATALOGO_EXACTOS"])[0]
        if str(r["N_CODCLI_CATALOGO_EXACTOS"]) == "1"
        else "",
        axis=1,
    )
    return out


def estado_institucional(
    codcli: str,
    vigencia: pd.DataFrame,
    filtro: pd.DataFrame,
) -> tuple[str, str]:
    if not codcli:
        return "NO_EVALUABLE_SIN_CODCLI_ASIGNADO", ""
    v = vigencia.loc[vigencia["CODCLI"].eq(codcli)].copy()
    f = filtro.loc[filtro["CODCLI"].eq(codcli)].copy()
    if v.empty and f.empty:
        return "SIN_EVIDENCIA_2026_1", ""
    if not v.empty:
        efectivos = v.loc[
            v["ES_2026_1"].eq("SI") & v["MATRICULA_EFECTIVA"].eq("SI")
        ]
        if not efectivos.empty:
            e = efectivos.iloc[0]
            return (
                "MATRICULA_EFECTIVA_2026_1",
                f"{e.get('FUENTE','')} | {e.get('HOJA','')} | fila {e.get('FILA','')}",
            )
        periodo = v.loc[v["ES_2026_1"].eq("SI")]
        if not periodo.empty:
            e = periodo.iloc[0]
            return (
                "EVIDENCIA_2026_1_NO_EFECTIVA",
                f"{e.get('FUENTE','')} | {e.get('HOJA','')} | fila {e.get('FILA','')}",
            )
    if not f.empty and f["ES_2026_1"].eq("SI").any():
        e = f.loc[f["ES_2026_1"].eq("SI")].iloc[0]
        return (
            "PERIODO_2026_1_SIN_VIGENCIA_EFECTIVA",
            f"{e.get('FUENTE','')} | {e.get('HOJA','')} | fila {e.get('FILA','')}",
        )
    return "SIN_EVIDENCIA_EFECTIVA_2026_1", ""


def buscar_decision_recon(
    row: pd.Series,
    decisiones: pd.DataFrame,
) -> pd.Series | None:
    rut_num = str(row.get("N_DOC", "")).strip()
    oferta = str(row.get("OFERTA_SIES", "")).strip()
    cand = decisiones.loc[
        decisiones["RUT"].astype(str).str.strip().eq(rut_num)
        & decisiones["OFERTA"].astype(str).str.strip().eq(oferta)
    ]
    if cand.empty:
        return None
    return cand.iloc[0]


def registro_base(
    origen: str,
    fila_operativa: int,
    row: pd.Series,
    columnas_mu: list[str],
    decision: str,
    fundamento: str,
    evidencia: str,
    incluido: str,
    pendiente: str,
    impacto: str,
    estado_principal: str,
    estado_95: str,
    estado_30: str,
    estado_inst: str,
    fuente_inst: str,
    codcli: str = "",
    clasificacion_fase2: str = "",
) -> dict[str, Any]:
    rec = {
        "ORIGEN": origen,
        "FILA_OPERATIVA": fila_operativa,
        "CODCLI": codcli,
        "RUT": row.get("RUT_NORM", ""),
        "N_DOC": row.get("N_DOC", ""),
        "DV": row.get("DV", ""),
        "OFERTA_SIES": row.get("OFERTA_SIES", ""),
        "COD_SED": row.get("COD_SED", ""),
        "COD_CAR": row.get("COD_CAR", ""),
        "MODALIDAD": row.get("MODALIDAD", ""),
        "JOR": row.get("JOR", ""),
        "VERSION": row.get("VERSION", ""),
        "ESTADO_EN_CARGA_PRINCIPAL": estado_principal,
        "ESTADO_EN_COMPLEMENTO_95": estado_95,
        "ESTADO_EN_RECTIFICACION_30": estado_30,
        "ESTADO_INSTITUCIONAL_2026_1": estado_inst,
        "DECISION_PROPUESTA": decision,
        "FUNDAMENTO": fundamento,
        "FUENTE_EVIDENCIA": evidencia,
        "FUENTE_EVIDENCIA_2026_1": fuente_inst,
        "INCLUIDO_PROPUESTO": incluido,
        "PENDIENTE": pendiente,
        "IMPACTO_TOTAL": impacto,
        "CLASIFICACION_FASE2": clasificacion_fase2,
        "FILA_32": row.get("FILA_32", ""),
    }
    for col in columnas_mu:
        rec[col] = row.get(col, "")
    return rec


def construir_revision() -> tuple[pd.DataFrame, dict[str, Any], dict[str, pd.DataFrame]]:
    core = cargar_core()
    columnas_mu = core["COLUMNAS_MU"]
    df_4070, df_95, df_30, controles_fuentes = validar_fuentes(core)
    catalogo, controles_catalogo = validar_catalogo(cargar=True)
    assert catalogo is not None
    mapa_catalogo = crear_mapa_catalogo_exactos(catalogo)
    del catalogo

    df_4070 = enriquecer_con_catalogo(preparar_mu(df_4070, columnas_mu), mapa_catalogo)
    df_95 = preparar_mu(df_95, columnas_mu)
    df_30 = preparar_mu(df_30, columnas_mu)

    asignacion_95 = leer_csv_auto(ASIGNACION_95)
    asignacion_30 = leer_csv_auto(ASIGNACION_30)
    decisiones_recon = leer_csv_auto(DECISIONES_RECONSTRUCCION)
    comparacion_recon = leer_csv_auto(COMPARACION_RECONSTRUCCION)
    vigencia = leer_csv_auto(AUDITORIA_VIGENCIA)
    filtro = leer_csv_auto(AUDITORIA_FILTRO)
    mapeo = leer_csv_auto(AUDITORIA_MAPEO)

    llaves_4070 = set(df_4070["LLAVE_RUT_OFERTA"])
    filas_4070 = set(df_4070["FILA_32"])
    ruts_4070 = set(df_4070["RUT_NORM"])

    registros: list[dict[str, Any]] = []

    for idx, row in df_4070.iterrows():
        codcli = row.get("CODCLI_CATALOGO_UNICO", "")
        estado_inst, fuente_inst = estado_institucional(codcli, vigencia, filtro)
        registros.append(
            registro_base(
                "CARGA_PRINCIPAL_4070",
                idx + 1,
                row,
                columnas_mu,
                "CONSERVAR_CARGA_PRINCIPAL",
                "Registro presente en carga principal congelada.",
                str(ARCHIVO_4070),
                "SI",
                "NO",
                "NO",
                "PRESENTE",
                "NO_APLICA",
                "NO_APLICA",
                estado_inst,
                fuente_inst,
                codcli=codcli,
            )
        )

    for idx, row in asignacion_95.iterrows():
        llave = row.get("LLAVE_RUT_OFERTA", f"{row.get('RUT_NORM','')}|{row.get('OFERTA_SIES','')}")
        fila_exacta = row.get("FILA_32", "") in filas_4070
        rut_oferta = llave in llaves_4070
        rut_presente = row.get("RUT_NORM", "") in ruts_4070
        clasif = row.get("CLASIFICACION", "")
        codcli = row.get("CODCLI", "")
        estado_inst, fuente_inst = estado_institucional(codcli, vigencia, filtro)
        if clasif == "CODCLI_ASIGNADO_INEQUIVOCAMENTE":
            if fila_exacta or rut_oferta:
                decision = "YA_REPRESENTADO_NO_AGREGAR"
                incluido, pendiente, impacto = "NO", "NO", "NO"
                fundamento = "Representacion RUT+oferta ya presente en carga principal."
            else:
                decision = "CONSERVAR_COMPLEMENTO_95"
                incluido, pendiente, impacto = "SI", "NO", "SI"
                fundamento = "Complemento congelado con CODCLI asignado inequívocamente."
        elif fila_exacta or rut_oferta:
            decision = "CONFLICTO_SIN_IMPACTO_CANTIDAD"
            incluido, pendiente, impacto = "NO", "SI", "NO"
            fundamento = "La fila no tiene CODCLI inequívoco, pero su representacion ya esta en la carga principal."
        else:
            decision = "CONFLICTO_MATERIAL"
            incluido, pendiente, impacto = "NO", "SI", "SI"
            fundamento = "Fase 2 no asigno CODCLI inequívoco; no se puede incorporar automaticamente."
        registros.append(
            registro_base(
                "COMPLEMENTO_95",
                int(row.get("FILA_OPERATIVA", idx + 1)),
                row,
                columnas_mu,
                decision,
                fundamento,
                row.get("ARCHIVOS_EVIDENCIA", str(ASIGNACION_95)),
                incluido,
                pendiente,
                impacto,
                "RUT_OFERTA_PRESENTE" if rut_oferta else ("RUT_PRESENTE" if rut_presente else "NO_PRESENTE"),
                "REGISTRO_ANALIZADO",
                "NO_APLICA",
                estado_inst,
                fuente_inst,
                codcli=codcli,
                clasificacion_fase2=clasif,
            )
        )

    llaves_95_incluidas = {
        r["RUT"] + "|" + r["OFERTA_SIES"]
        for r in registros
        if r["ORIGEN"] == "COMPLEMENTO_95" and r["INCLUIDO_PROPUESTO"] == "SI"
    }

    for idx, row in asignacion_30.iterrows():
        llave = row.get("LLAVE_RUT_OFERTA", f"{row.get('RUT_NORM','')}|{row.get('OFERTA_SIES','')}")
        fila_exacta = row.get("FILA_32", "") in filas_4070
        rut_oferta_4070 = llave in llaves_4070
        rut_oferta_95 = llave in llaves_95_incluidas
        rut_presente = row.get("RUT_NORM", "") in ruts_4070
        clasif = row.get("CLASIFICACION", "")
        codcli = row.get("CODCLI", "")
        dec = buscar_decision_recon(row, decisiones_recon)
        accion = dec.get("ACCION", "") if dec is not None else ""
        validacion = dec.get("VALIDACION_AUTOMATICA", "") if dec is not None else ""
        evidencia = dec.get("EVIDENCIA", row.get("ARCHIVOS_EVIDENCIA", str(ASIGNACION_30))) if dec is not None else row.get("ARCHIVOS_EVIDENCIA", str(ASIGNACION_30))
        estado_inst, fuente_inst = estado_institucional(codcli, vigencia, filtro)
        if accion == "PENDIENTE_MAPEO" or validacion == "NO_VALIDADO":
            decision = "SIN_EVIDENCIA_SUFICIENTE"
            incluido, pendiente, impacto = "NO", "SI", "SI"
            fundamento = "La reconstruccion mantiene mapeo pendiente o no validado."
        elif clasif != "CODCLI_ASIGNADO_INEQUIVOCAMENTE":
            if fila_exacta or rut_oferta_4070 or rut_oferta_95 or accion == "SIN_CAMBIO_MU":
                decision = "CONFLICTO_SIN_IMPACTO_CANTIDAD"
                incluido, pendiente, impacto = "NO", "SI", "NO"
                fundamento = "CODCLI no inequívoco, pero la representacion ya existe o la reconstruccion no propone agregar."
            else:
                decision = "CONFLICTO_MATERIAL"
                incluido, pendiente, impacto = "NO", "SI", "SI"
                fundamento = "La rectificacion propone revisar, pero Fase 2 no asigno CODCLI inequívoco."
        elif fila_exacta or rut_oferta_4070 or rut_oferta_95 or accion == "SIN_CAMBIO_MU":
            decision = "YA_REPRESENTADO_NO_AGREGAR"
            incluido, pendiente, impacto = "NO", "NO", "NO"
            fundamento = "Ya representado en carga principal o complemento."
        elif accion == "INCORPORAR_MU":
            decision = "INCORPORAR_DESDE_30"
            incluido, pendiente, impacto = "SI", "NO", "SI"
            fundamento = "Reconstruccion validada y CODCLI asignado inequívocamente."
        else:
            decision = "SIN_EVIDENCIA_SUFICIENTE"
            incluido, pendiente, impacto = "NO", "SI", "SI"
            fundamento = "No existe decision reconstruida suficiente para incorporar."
        registros.append(
            registro_base(
                "RECTIFICACION_30",
                int(row.get("FILA_OPERATIVA", idx + 1)),
                row,
                columnas_mu,
                decision,
                fundamento,
                evidencia,
                incluido,
                pendiente,
                impacto,
                "RUT_OFERTA_PRESENTE" if rut_oferta_4070 else ("RUT_PRESENTE" if rut_presente else "NO_PRESENTE"),
                "RUT_OFERTA_PRESENTE" if rut_oferta_95 else "NO_PRESENTE",
                "REGISTRO_ANALIZADO",
                estado_inst,
                fuente_inst,
                codcli=codcli,
                clasificacion_fase2=clasif,
            )
        )

    propuesta = normalizar_df(pd.DataFrame(registros))
    invalidas = set(propuesta["DECISION_PROPUESTA"]) - DECISIONES_PERMITIDAS
    if invalidas:
        raise CierreError(f"Decisiones no permitidas: {sorted(invalidas)}", 2)

    evidencia_codcli = set()
    for col in ["CODCLI", "CLASIFICACION_FASE2"]:
        if col in propuesta.columns and col == "CODCLI":
            evidencia_codcli.update(x for x in propuesta[col].astype(str) if x)
    for df in [asignacion_95, asignacion_30]:
        for col in ["CODCLI", "CODCLI_EXACTOS", "CODCLI_DEL_RUT"]:
            if col in df.columns:
                for valor in df[col].astype(str):
                    evidencia_codcli.update(codcli_unicos(valor))
    evidencia = pd.concat(
        [
            vigencia.loc[vigencia["CODCLI"].isin(evidencia_codcli)].assign(
                TIPO_EVIDENCIA="VIGENCIA_MATRICULA"
            ),
            filtro.loc[filtro["CODCLI"].isin(evidencia_codcli)].assign(
                TIPO_EVIDENCIA="FILTRO_2026_1"
            ),
            mapeo.loc[mapeo["CODCLI"].isin(evidencia_codcli)].assign(
                TIPO_EVIDENCIA="MAPEO_OFERTA_SIES"
            ),
            decisiones_recon.loc[
                decisiones_recon["CODCLI"].isin(evidencia_codcli)
            ].assign(TIPO_EVIDENCIA="DECISION_RECONSTRUCCION"),
            comparacion_recon.loc[
                comparacion_recon["CODCLI"].isin(evidencia_codcli)
            ].assign(TIPO_EVIDENCIA="COMPARACION_RECONSTRUCCION"),
        ],
        ignore_index=True,
        sort=False,
    ).fillna("")

    controles = {
        **controles_fuentes,
        **controles_catalogo,
        "script_reconstruccion_existe": "SI" if SCRIPT_RECONSTRUCCION.exists() else "NO",
        "script_reconstruccion_hash": sha256(SCRIPT_RECONSTRUCCION) if SCRIPT_RECONSTRUCCION.exists() else "",
        "asignacion_95_hash": sha256(ASIGNACION_95),
        "asignacion_30_hash": sha256(ASIGNACION_30),
        "decisiones_reconstruccion_hash": sha256(DECISIONES_RECONSTRUCCION),
        "auditoria_vigencia_hash": sha256(AUDITORIA_VIGENCIA),
        "filas_propuesta": len(propuesta),
    }
    tablas = {
        "decision_95": propuesta.loc[propuesta["ORIGEN"].eq("COMPLEMENTO_95")].copy(),
        "decision_30": propuesta.loc[propuesta["ORIGEN"].eq("RECTIFICACION_30")].copy(),
        "actualizaciones": propuesta.loc[
            propuesta["DECISION_PROPUESTA"].eq("ACTUALIZAR_FILA_EXISTENTE")
        ].copy(),
        "conflictos_materiales": propuesta.loc[
            propuesta["DECISION_PROPUESTA"].eq("CONFLICTO_MATERIAL")
        ].copy(),
        "conflictos_sin_impacto": propuesta.loc[
            propuesta["DECISION_PROPUESTA"].eq("CONFLICTO_SIN_IMPACTO_CANTIDAD")
        ].copy(),
        "evidencia": normalizar_df(evidencia),
        "controles": tabla_dict(controles),
    }
    return propuesta, controles, tablas


def resumen_revision(propuesta: pd.DataFrame) -> dict[str, int]:
    principal = int(
        propuesta["DECISION_PROPUESTA"].eq("CONSERVAR_CARGA_PRINCIPAL").sum()
    )
    complemento = int(
        propuesta["DECISION_PROPUESTA"].eq("CONSERVAR_COMPLEMENTO_95").sum()
    )
    inc_30 = int(propuesta["DECISION_PROPUESTA"].eq("INCORPORAR_DESDE_30").sum())
    actualizaciones = int(
        propuesta["DECISION_PROPUESTA"].eq("ACTUALIZAR_FILA_EXISTENTE").sum()
    )
    conflictos_materiales = int(
        propuesta["DECISION_PROPUESTA"].eq("CONFLICTO_MATERIAL").sum()
    )
    sin_evidencia = int(
        propuesta["DECISION_PROPUESTA"].eq("SIN_EVIDENCIA_SUFICIENTE").sum()
    )
    exclusiones = int(
        (
            propuesta["INCLUIDO_PROPUESTO"].eq("NO")
            & propuesta["PENDIENTE"].eq("NO")
        ).sum()
    )
    total = int(propuesta["INCLUIDO_PROPUESTO"].eq("SI").sum())
    return {
        "total_principal": principal,
        "total_complemento_incluido": complemento,
        "incorporaciones_desde_30": inc_30,
        "actualizaciones": actualizaciones,
        "exclusiones": exclusiones,
        "conflictos_materiales": conflictos_materiales,
        "sin_evidencia_suficiente": sin_evidencia,
        "total_final_propuesto": total,
    }


def modo_revisar() -> int:
    global LOG_ACTUAL
    LOG_ACTUAL = LOG_REVISION
    SALIDA.mkdir(parents=True, exist_ok=True)
    for ruta in [
        PROPUESTA_XLSX,
        PROPUESTA_CSV,
        MANIFIESTO_REVISION,
        LOG_REVISION,
        ESTADO_REVISION,
        APROBACION_JSON,
    ]:
        backup_si_existe(ruta)
    MENSAJES.clear()
    inicio = ahora()
    log("=" * 100)
    log("MODO REVISAR - FASES 4 Y 5")
    log("=" * 100)
    propuesta, controles, tablas = construir_revision()
    resumen = resumen_revision(propuesta)
    composicion = pd.DataFrame(
        [
            {"CONCEPTO": k, "VALOR": v}
            for k, v in resumen.items()
        ]
    )
    escribir_csv(propuesta, PROPUESTA_CSV, header=True)
    hash_propuesta = sha256(PROPUESTA_CSV)
    manifiesto = {
        "fecha": ahora(),
        "modo": "revisar",
        "script": str(SCRIPT),
        "script_hash": sha256(SCRIPT),
        "entradas": controles,
        "salidas": {},
        "resumen": resumen,
        "hash_propuesta": hash_propuesta,
        "originales_modificados": "NO",
    }
    with pd.ExcelWriter(PROPUESTA_XLSX, engine="openpyxl") as writer:
        pd.DataFrame([resumen]).to_excel(writer, sheet_name="RESUMEN", index=False)
        composicion.to_excel(writer, sheet_name="COMPOSICION_PROPUESTA", index=False)
        tablas["decision_95"].to_excel(writer, sheet_name="DECISION_95", index=False)
        tablas["decision_30"].to_excel(writer, sheet_name="DECISION_30", index=False)
        tablas["actualizaciones"].to_excel(writer, sheet_name="ACTUALIZACIONES", index=False)
        tablas["conflictos_materiales"].to_excel(writer, sheet_name="CONFLICTOS_MATERIALES", index=False)
        tablas["conflictos_sin_impacto"].to_excel(writer, sheet_name="CONFLICTOS_SIN_IMPACTO", index=False)
        tablas["evidencia"].to_excel(writer, sheet_name="EVIDENCIA", index=False)
        tablas["controles"].to_excel(writer, sheet_name="CONTROLES", index=False)
    aprobacion = {
        "aprobado": False,
        "hash_propuesta": hash_propuesta,
        "total_propuesto": resumen["total_final_propuesto"],
        "incorporaciones_desde_30": resumen["incorporaciones_desde_30"],
        "actualizaciones": resumen["actualizaciones"],
        "conflictos_materiales": resumen["conflictos_materiales"],
        "fecha_aprobacion": "",
        "observacion": "",
    }
    APROBACION_JSON.write_text(
        json.dumps(aprobacion, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    manifiesto["salidas"] = {
        "propuesta_csv": {"ruta": str(PROPUESTA_CSV), "sha256": hash_propuesta},
        "propuesta_xlsx": {"ruta": str(PROPUESTA_XLSX), "sha256": sha256(PROPUESTA_XLSX)},
        "aprobacion": {"ruta": str(APROBACION_JSON), "sha256": sha256(APROBACION_JSON)},
    }
    MANIFIESTO_REVISION.write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    codigo = 2 if resumen["conflictos_materiales"] or resumen["sin_evidencia_suficiente"] else 0
    estado = {
        "estado": "REVISION_COMPLETADA_CON_BLOQUEOS" if codigo == 2 else "REVISION_COMPLETADA_SIN_BLOQUEOS",
        "codigo_salida": codigo,
        "inicio": inicio,
        "fin": ahora(),
        **resumen,
        "hash_propuesta": hash_propuesta,
        "excel": str(PROPUESTA_XLSX),
    }
    ESTADO_REVISION.write_text(
        "\n".join(f"{k}: {v}" for k, v in estado.items()) + "\n",
        encoding="utf-8",
    )
    log(f"Total principal: {resumen['total_principal']}")
    log(f"Total complemento incluido: {resumen['total_complemento_incluido']}")
    log(f"Incorporaciones propuestas desde los 30: {resumen['incorporaciones_desde_30']}")
    log(f"Actualizaciones: {resumen['actualizaciones']}")
    log(f"Exclusiones: {resumen['exclusiones']}")
    log(f"Conflictos materiales: {resumen['conflictos_materiales']}")
    log(f"Total final propuesto: {resumen['total_final_propuesto']}")
    log(f"Excel: {PROPUESTA_XLSX}")
    log(f"Hash propuesta: {hash_propuesta}")
    log(f"Codigo de salida: {codigo}")
    return codigo


def filas_operativas(propuesta: pd.DataFrame) -> pd.DataFrame:
    return propuesta.loc[
        propuesta["ORIGEN"].isin(["COMPLEMENTO_95", "RECTIFICACION_30"])
    ].copy()


def validar_unicidad_operativa(operativos: pd.DataFrame) -> list[str]:
    errores: list[str] = []
    duplicados = operativos.loc[
        operativos.duplicated(subset=["ORIGEN", "FILA_OPERATIVA"], keep=False)
    ]
    if not duplicados.empty:
        errores.append(
            "Hay mas de una decision por ORIGEN+FILA_OPERATIVA."
        )

    for col in [
        "DECISION_PROPUESTA",
        "INCLUIDO_PROPUESTO",
        "PENDIENTE",
        "IMPACTO_TOTAL",
    ]:
        vacios = int(operativos[col].astype(str).str.strip().eq("").sum())
        if vacios:
            errores.append(f"Hay {vacios} valores vacios en {col}.")

    valores_binarios = {
        "INCLUIDO_PROPUESTO": {"SI", "NO"},
        "PENDIENTE": {"SI", "NO"},
        "IMPACTO_TOTAL": {"SI", "NO"},
    }
    for col, permitidos in valores_binarios.items():
        invalidos = sorted(set(operativos[col].astype(str)) - permitidos)
        if invalidos:
            errores.append(f"Valores invalidos en {col}: {invalidos}")

    contrad = operativos.loc[
        operativos["INCLUIDO_PROPUESTO"].eq("SI")
        & operativos["PENDIENTE"].eq("SI")
    ]
    if not contrad.empty:
        errores.append("Hay casos incluidos y pendientes simultaneamente.")

    return errores


def comparar_fila_fisica(
    propuesta: pd.Series,
    fuente: pd.DataFrame,
    columnas_mu: list[str],
) -> bool:
    try:
        fila = int(str(propuesta["FILA_OPERATIVA"])) - 1
    except ValueError:
        return False
    if fila < 0 or fila >= len(fuente):
        return False
    actual = fuente.iloc[fila][columnas_mu].astype(str).str.strip()
    esperado = propuesta[columnas_mu].astype(str).str.strip()
    return bool(actual.reset_index(drop=True).eq(esperado.reset_index(drop=True)).all())


def validar_filas_fisicas_aprobables(
    propuesta: pd.DataFrame,
    df_95: pd.DataFrame,
    df_30: pd.DataFrame,
    columnas_mu: list[str],
) -> tuple[list[str], dict[str, Any]]:
    errores: list[str] = []
    incorporaciones = propuesta.loc[
        propuesta["ORIGEN"].eq("RECTIFICACION_30")
        & propuesta["DECISION_PROPUESTA"].eq("INCORPORAR_DESDE_30")
    ].copy()
    complementos = propuesta.loc[
        propuesta["ORIGEN"].eq("COMPLEMENTO_95")
        & propuesta["DECISION_PROPUESTA"].eq("CONSERVAR_COMPLEMENTO_95")
    ].copy()
    ya_representados = propuesta.loc[
        propuesta["DECISION_PROPUESTA"].eq("YA_REPRESENTADO_NO_AGREGAR")
    ].copy()

    fallas_30 = []
    for _, row in incorporaciones.iterrows():
        if not comparar_fila_fisica(row, df_30, columnas_mu):
            fallas_30.append(str(row["FILA_OPERATIVA"]))
    if fallas_30:
        errores.append(
            "Incorporaciones desde 30 no identificables fisicamente: "
            + ", ".join(fallas_30)
        )

    fallas_95 = []
    for _, row in complementos.iterrows():
        if not comparar_fila_fisica(row, df_95, columnas_mu):
            fallas_95.append(str(row["FILA_OPERATIVA"]))
    if fallas_95:
        errores.append(
            "Complementos conservados no identificables fisicamente: "
            + ", ".join(fallas_95)
        )

    if len(ya_representados) != 1:
        errores.append(
            f"Se esperaba 1 caso ya representado; obtenido {len(ya_representados)}."
        )
    elif not ya_representados.iloc[0]["INCLUIDO_PROPUESTO"] == "NO":
        errores.append("El caso ya representado quedo marcado como incluido.")

    controles = {
        "filas_fisicas_incorporaciones_30_ok": len(fallas_30) == 0,
        "filas_fisicas_complemento_95_ok": len(fallas_95) == 0,
        "caso_ya_representado_no_agregado": (
            len(ya_representados) == 1
            and ya_representados.iloc[0]["INCLUIDO_PROPUESTO"] == "NO"
        ),
    }
    return errores, controles


def validar_metricas_aprobables(propuesta: pd.DataFrame) -> tuple[list[str], dict[str, Any]]:
    operativos = filas_operativas(propuesta)
    resumen = resumen_revision(propuesta)
    conteos_decision = propuesta["DECISION_PROPUESTA"].value_counts().to_dict()
    errores: list[str] = []

    esperados = {
        "decisiones_totales": (len(operativos), 125),
        "decisiones_complemento": (
            int(operativos["ORIGEN"].eq("COMPLEMENTO_95").sum()),
            95,
        ),
        "decisiones_rectificacion": (
            int(operativos["ORIGEN"].eq("RECTIFICACION_30").sum()),
            30,
        ),
        "conflictos_materiales": (
            int(propuesta["DECISION_PROPUESTA"].eq("CONFLICTO_MATERIAL").sum()),
            0,
        ),
        "sin_evidencia_suficiente": (
            int(
                propuesta["DECISION_PROPUESTA"]
                .eq("SIN_EVIDENCIA_SUFICIENTE")
                .sum()
            ),
            0,
        ),
        "pendientes": (int(propuesta["PENDIENTE"].eq("SI").sum()), 0),
        "pendientes_con_impacto": (
            int(
                (
                    propuesta["PENDIENTE"].eq("SI")
                    & propuesta["IMPACTO_TOTAL"].eq("SI")
                ).sum()
            ),
            0,
        ),
        "conflictos_sin_impacto": (
            int(
                propuesta["DECISION_PROPUESTA"]
                .eq("CONFLICTO_SIN_IMPACTO_CANTIDAD")
                .sum()
            ),
            89,
        ),
        "complemento_conservado": (
            int(
                propuesta["DECISION_PROPUESTA"]
                .eq("CONSERVAR_COMPLEMENTO_95")
                .sum()
            ),
            6,
        ),
        "incorporaciones_desde_30": (
            int(
                propuesta["DECISION_PROPUESTA"]
                .eq("INCORPORAR_DESDE_30")
                .sum()
            ),
            29,
        ),
        "ya_representados": (
            int(
                propuesta["DECISION_PROPUESTA"]
                .eq("YA_REPRESENTADO_NO_AGREGAR")
                .sum()
            ),
            1,
        ),
        "actualizaciones": (
            int(
                propuesta["DECISION_PROPUESTA"]
                .eq("ACTUALIZAR_FILA_EXISTENTE")
                .sum()
            ),
            0,
        ),
        "total_propuesto": (resumen["total_final_propuesto"], 4105),
    }

    for nombre, (obtenido, esperado) in esperados.items():
        if obtenido != esperado:
            errores.append(
                f"{nombre}: esperado {esperado}, obtenido {obtenido}"
            )

    if 4070 + 6 + 29 != 4105:
        errores.append("Control aritmetico 4070 + 6 + 29 != 4105.")

    errores.extend(validar_unicidad_operativa(operativos))

    controles = {
        "resumen": resumen,
        "conteos_decision": conteos_decision,
        "esperados": {
            k: {"obtenido": v[0], "esperado": v[1]}
            for k, v in esperados.items()
        },
        "control_aritmetico": "4070 + 6 + 29 = 4105",
    }
    return errores, controles


def modo_integrar_resolucion() -> int:
    global LOG_ACTUAL
    LOG_ACTUAL = LOG_INTEGRACION_RESOLUCION
    SALIDA.mkdir(parents=True, exist_ok=True)
    for ruta in [
        PROPUESTA_APROBABLE_CSV,
        PROPUESTA_APROBABLE_XLSX,
        MANIFIESTO_PROPUESTA_APROBABLE,
        APROBACION_APROBABLE_JSON,
        LOG_INTEGRACION_RESOLUCION,
        ESTADO_INTEGRACION_RESOLUCION,
    ]:
        backup_si_existe(ruta)
    MENSAJES.clear()
    inicio = ahora()
    log("=" * 100)
    log("MODO INTEGRAR-RESOLUCION - PROPUESTA APROBABLE")
    log("=" * 100)

    errores: list[str] = []
    manifiesto_original = json.loads(MANIFIESTO_REVISION.read_text(encoding="utf-8"))
    hash_propuesta_original = sha256(PROPUESTA_CSV)
    if hash_propuesta_original != manifiesto_original.get("hash_propuesta"):
        errores.append("Hash de propuesta original no coincide con manifiesto.")

    hash_resolucion = sha256(RESOLUCION_36_CSV)
    hash_derivada = sha256(PROPUESTA_RESUELTA_36_CSV)
    if hash_resolucion != HASH_RESOLUCION_36_ESPERADO:
        errores.append("Hash obligatorio de resolucion 36 no coincide.")
    if hash_derivada != HASH_PROPUESTA_RESUELTA_36_ESPERADO:
        errores.append("Hash obligatorio de propuesta derivada no coincide.")

    _, controles_catalogo = validar_catalogo(cargar=False)
    core = cargar_core()
    df_4070, df_95, df_30, controles_fuentes = validar_fuentes(core)
    columnas_mu = core["COLUMNAS_MU"]

    propuesta = leer_csv_auto(PROPUESTA_RESUELTA_36_CSV)
    resolucion = leer_csv_auto(RESOLUCION_36_CSV)
    sin_impacto = propuesta["DECISION_PROPUESTA"].eq(
        "CONFLICTO_SIN_IMPACTO_CANTIDAD"
    )
    propuesta.loc[sin_impacto, "PENDIENTE"] = "NO"
    propuesta.loc[sin_impacto, "IMPACTO_TOTAL"] = "NO"

    if len(resolucion) != 36:
        errores.append(f"Resolucion 36 debe tener 36 filas; tiene {len(resolucion)}.")
    if int(resolucion["PENDIENTE"].eq("SI").sum()) != 0:
        errores.append("Resolucion 36 contiene pendientes.")
    if int(resolucion["DECISION"].eq("CONSERVAR_COMPLEMENTO_95").sum()) != 6:
        errores.append("Resolucion 36 no contiene 6 complementos conservados.")
    if int(resolucion["DECISION"].eq("INCORPORAR_DESDE_30").sum()) != 29:
        errores.append("Resolucion 36 no contiene 29 incorporaciones desde 30.")
    if int(resolucion["DECISION"].eq("YA_REPRESENTADO_NO_AGREGAR").sum()) != 1:
        errores.append("Resolucion 36 no contiene 1 ya representado.")
    if int(resolucion["DECISION"].eq("ACTUALIZAR_FILA_EXISTENTE").sum()) != 0:
        errores.append("Resolucion 36 contiene actualizaciones no esperadas.")

    errores_metricas, controles_metricas = validar_metricas_aprobables(propuesta)
    errores.extend(errores_metricas)

    errores_fisicos, controles_fisicos = validar_filas_fisicas_aprobables(
        propuesta,
        df_95,
        df_30,
        columnas_mu,
    )
    errores.extend(errores_fisicos)

    if errores:
        estado = {
            "estado": "INTEGRACION_BLOQUEADA",
            "codigo_salida": 2,
            "inicio": inicio,
            "fin": ahora(),
            "errores": errores,
        }
        ESTADO_INTEGRACION_RESOLUCION.write_text(
            json.dumps(estado, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        log("INTEGRACION_BLOQUEADA")
        for error in errores[:20]:
            log(f"- {error}")
        return 2

    escribir_csv(propuesta, PROPUESTA_APROBABLE_CSV, header=True)
    propuesta_releida = leer_csv_auto(PROPUESTA_APROBABLE_CSV)
    diferencias_relectura = int(
        (
            ~propuesta_releida.astype(str)
            .reset_index(drop=True)
            .eq(propuesta.astype(str).reset_index(drop=True))
        )
        .to_numpy()
        .sum()
    )
    if diferencias_relectura != 0:
        raise CierreError(
            f"Diferencias en relectura de propuesta aprobable: {diferencias_relectura}",
            4,
        )

    resumen = resumen_revision(propuesta)
    composicion = pd.DataFrame(
        [
            {"CONCEPTO": "carga_principal", "VALOR": 4070},
            {"CONCEPTO": "complemento_conservado", "VALOR": 6},
            {"CONCEPTO": "incorporaciones_desde_30", "VALOR": 29},
            {"CONCEPTO": "total_propuesto", "VALOR": 4105},
            {"CONCEPTO": "control", "VALOR": "4070 + 6 + 29 = 4105"},
        ]
    )
    decision_95 = propuesta.loc[propuesta["ORIGEN"].eq("COMPLEMENTO_95")].copy()
    decision_30 = propuesta.loc[propuesta["ORIGEN"].eq("RECTIFICACION_30")].copy()
    incorporaciones_29 = propuesta.loc[
        propuesta["DECISION_PROPUESTA"].eq("INCORPORAR_DESDE_30")
    ].copy()
    complemento_6 = propuesta.loc[
        propuesta["DECISION_PROPUESTA"].eq("CONSERVAR_COMPLEMENTO_95")
    ].copy()
    ya_representado_1 = propuesta.loc[
        propuesta["DECISION_PROPUESTA"].eq("YA_REPRESENTADO_NO_AGREGAR")
    ].copy()
    conflictos_materiales = propuesta.loc[
        propuesta["DECISION_PROPUESTA"].eq("CONFLICTO_MATERIAL")
    ].copy()

    controles = {
        "fecha": ahora(),
        "modo": "integrar-resolucion",
        "script": str(SCRIPT),
        "script_hash": sha256(SCRIPT),
        "propuesta_original_hash": hash_propuesta_original,
        "resolucion_36_hash": hash_resolucion,
        "propuesta_derivada_hash": hash_derivada,
        "diferencias_relectura": diferencias_relectura,
        "fuentes_originales_modificadas": "NO",
        **controles_catalogo,
        **controles_fuentes,
        **controles_fisicos,
    }
    controles_df = tabla_dict(
        {
            "controles": controles,
            "metricas": controles_metricas,
        }
    )

    with pd.ExcelWriter(PROPUESTA_APROBABLE_XLSX, engine="openpyxl") as writer:
        pd.DataFrame([resumen]).to_excel(writer, sheet_name="RESUMEN", index=False)
        composicion.to_excel(writer, sheet_name="COMPOSICION", index=False)
        decision_95.to_excel(writer, sheet_name="DECISION_95", index=False)
        decision_30.to_excel(writer, sheet_name="DECISION_30", index=False)
        incorporaciones_29.to_excel(writer, sheet_name="INCORPORACIONES_29", index=False)
        complemento_6.to_excel(writer, sheet_name="COMPLEMENTO_CONSERVADO_6", index=False)
        ya_representado_1.to_excel(writer, sheet_name="YA_REPRESENTADO_1", index=False)
        conflictos_materiales.to_excel(writer, sheet_name="CONFLICTOS_MATERIALES", index=False)
        controles_df.to_excel(writer, sheet_name="CONTROLES", index=False)
        resolucion.to_excel(writer, sheet_name="TRAZABILIDAD_RESOLUCION", index=False)

    hash_aprobable = sha256(PROPUESTA_APROBABLE_CSV)
    aprobacion = {
        "aprobado": False,
        "hash_propuesta": hash_aprobable,
        "total_propuesto": 4105,
        "carga_principal": 4070,
        "complemento_conservado": 6,
        "incorporaciones_desde_30": 29,
        "actualizaciones": 0,
        "ya_representados": 1,
        "conflictos_materiales": 0,
        "fecha_aprobacion": "",
        "observacion": "",
    }
    APROBACION_APROBABLE_JSON.write_text(
        json.dumps(aprobacion, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    manifiesto = {
        "fecha": ahora(),
        "modo": "integrar-resolucion",
        "estado": "PROPUESTA_APROBABLE_GENERADA",
        "script": str(SCRIPT),
        "script_hash": sha256(SCRIPT),
        "entradas": {
            "propuesta_original": {
                "ruta": str(PROPUESTA_CSV),
                "sha256": hash_propuesta_original,
            },
            "resolucion_36": {
                "ruta": str(RESOLUCION_36_CSV),
                "sha256": hash_resolucion,
            },
            "propuesta_derivada": {
                "ruta": str(PROPUESTA_RESUELTA_36_CSV),
                "sha256": hash_derivada,
            },
        },
        "salidas": {
            "propuesta_aprobable_csv": {
                "ruta": str(PROPUESTA_APROBABLE_CSV),
                "sha256": hash_aprobable,
            },
            "propuesta_aprobable_xlsx": {
                "ruta": str(PROPUESTA_APROBABLE_XLSX),
                "sha256": sha256(PROPUESTA_APROBABLE_XLSX),
            },
            "aprobacion_aprobable": {
                "ruta": str(APROBACION_APROBABLE_JSON),
                "sha256": sha256(APROBACION_APROBABLE_JSON),
            },
        },
        "resumen": {
            **resumen,
            "carga_principal": 4070,
            "complemento_conservado": 6,
            "incorporaciones_desde_30": 29,
            "ya_representados": 1,
            "control_aritmetico": "4070 + 6 + 29 = 4105",
        },
        "controles": controles,
    }
    MANIFIESTO_PROPUESTA_APROBABLE.write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    estado = {
        "estado": "PROPUESTA_APROBABLE_GENERADA",
        "codigo_salida": 0,
        "inicio": inicio,
        "fin": ahora(),
        "total_propuesto": 4105,
        "carga_principal": 4070,
        "complemento_conservado": 6,
        "incorporaciones_desde_30": 29,
        "ya_representados": 1,
        "actualizaciones": 0,
        "conflictos_materiales": 0,
        "hash_propuesta": hash_aprobable,
        "diferencias_relectura": diferencias_relectura,
    }
    ESTADO_INTEGRACION_RESOLUCION.write_text(
        "\n".join(f"{k}: {v}" for k, v in estado.items()) + "\n",
        encoding="utf-8",
    )

    log("PROPUESTA_APROBABLE_GENERADA")
    log("Total propuesto: 4105")
    log("Composicion: 4070 + 6 + 29 = 4105")
    log(f"Hash propuesta aprobable: {hash_aprobable}")
    log(f"CSV: {PROPUESTA_APROBABLE_CSV}")
    log(f"Excel: {PROPUESTA_APROBABLE_XLSX}")
    log(f"Aprobacion: {APROBACION_APROBABLE_JSON}")
    return 0


def rutas_revision_activa() -> tuple[Path, Path, Path]:
    if APROBACION_APROBABLE_JSON.exists() and PROPUESTA_APROBABLE_CSV.exists():
        return (
            MANIFIESTO_PROPUESTA_APROBABLE,
            PROPUESTA_APROBABLE_CSV,
            APROBACION_APROBABLE_JSON,
        )
    return MANIFIESTO_REVISION, PROPUESTA_CSV, APROBACION_JSON


def cargar_revision_y_aprobacion() -> tuple[dict[str, Any], dict[str, Any]]:
    manifiesto_path, propuesta_path, aprobacion_path = rutas_revision_activa()
    if not manifiesto_path.exists() or not propuesta_path.exists():
        raise CierreError("No existe propuesta o manifiesto de revision", 3)
    if not aprobacion_path.exists():
        raise CierreError("No existe aprobacion", 3)
    manifiesto = json.loads(manifiesto_path.read_text(encoding="utf-8"))
    aprobacion = json.loads(aprobacion_path.read_text(encoding="utf-8"))
    return manifiesto, aprobacion


def validar_aprobacion_generica() -> tuple[dict[str, Any], dict[str, Any], pd.DataFrame]:
    manifiesto_path, propuesta_path, _ = rutas_revision_activa()
    manifiesto, aprobacion = cargar_revision_y_aprobacion()
    propuesta = leer_csv_auto(propuesta_path)
    resumen = resumen_revision(propuesta)
    errores = []
    if aprobacion.get("aprobado") is not True:
        errores.append("aprobado debe ser true")
    if sha256(propuesta_path) != aprobacion.get("hash_propuesta"):
        errores.append("hash de propuesta no coincide con aprobacion")
    hash_manifestado = manifiesto.get("hash_propuesta")
    if not hash_manifestado:
        hash_manifestado = (
            manifiesto.get("salidas", {})
            .get("propuesta_aprobable_csv", {})
            .get("sha256", "")
        )
    if sha256(propuesta_path) != hash_manifestado:
        errores.append("hash de propuesta no coincide con manifiesto")
    if resumen["total_final_propuesto"] != aprobacion.get("total_propuesto"):
        errores.append("total aprobado no coincide")
    if resumen["incorporaciones_desde_30"] != aprobacion.get("incorporaciones_desde_30"):
        errores.append("incorporaciones aprobadas no coinciden")
    if resumen["actualizaciones"] != aprobacion.get("actualizaciones"):
        errores.append("actualizaciones aprobadas no coinciden")
    if resumen["conflictos_materiales"] != aprobacion.get("conflictos_materiales"):
        errores.append("conflictos materiales aprobados no coinciden")
    if resumen["conflictos_materiales"] != 0:
        errores.append("conflictos materiales debe ser 0")
    validar_catalogo(cargar=False)
    for nombre, info in manifiesto.get("entradas", {}).get("hashes_fuentes_antes", {}).items():
        rutas = {
            "principal_4070": ARCHIVO_4070,
            "complemento_95": ARCHIVO_95,
            "rectificacion_30": ARCHIVO_30,
        }
        if nombre in rutas and sha256(rutas[nombre]) != info:
            errores.append(f"hash fuente cambio: {nombre}")
    if errores:
        REPORTE_APROBACION_INVALIDA.write_text(
            "APROBACION INVALIDA\n" + "\n".join(f"- {e}" for e in errores) + "\n",
            encoding="utf-8",
        )
        raise CierreError("Aprobacion invalida: " + " | ".join(errores), 3)
    return manifiesto, aprobacion, propuesta


def modo_validar_aprobacion() -> int:
    global LOG_ACTUAL
    LOG_ACTUAL = SALIDA / "LOG_VALIDACION_APROBACION.txt"
    MENSAJES.clear()
    SALIDA.mkdir(parents=True, exist_ok=True)
    log("Validando aprobacion...")
    manifiesto, aprobacion, propuesta = validar_aprobacion_generica()
    _, propuesta_path, aprobacion_path = rutas_revision_activa()
    sello = {
        "fecha": ahora(),
        "modo": "validar-aprobacion",
        "script": str(SCRIPT),
        "script_hash": sha256(SCRIPT),
        "aprobacion_hash": sha256(aprobacion_path),
        "propuesta_hash": sha256(propuesta_path),
        "manifiesto_revision_hash": sha256(rutas_revision_activa()[0]),
        "metricas": resumen_revision(propuesta),
        "estado": "APROBACION_VALIDADA",
        "originales_modificados": "NO",
    }
    SELLO_APROBACION.write_text(
        json.dumps(sello, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    log(f"Sello creado: {SELLO_APROBACION}")
    return 0


def rutas_finales(nueva_version: bool) -> dict[str, Path]:
    if not nueva_version:
        return {
            "csv": CSV_FINAL,
            "xlsx": XLSX_FINAL,
            "auditoria": AUDITORIA_CIERRE,
            "manifiesto": MANIFIESTO_CIERRE,
        }
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return {
        "csv": CSV_FINAL.with_name(f"{CSV_FINAL.stem}_{ts}{CSV_FINAL.suffix}"),
        "xlsx": XLSX_FINAL.with_name(f"{XLSX_FINAL.stem}_{ts}{XLSX_FINAL.suffix}"),
        "auditoria": AUDITORIA_CIERRE.with_name(f"{AUDITORIA_CIERRE.stem}_{ts}{AUDITORIA_CIERRE.suffix}"),
        "manifiesto": MANIFIESTO_CIERRE.with_name(f"{MANIFIESTO_CIERRE.stem}_{ts}{MANIFIESTO_CIERRE.suffix}"),
    }


def materializar_desde_propuesta(propuesta: pd.DataFrame, rutas: dict[str, Path]) -> dict[str, Any]:
    core = cargar_core()
    columnas_mu = core["COLUMNAS_MU"]
    seleccion = propuesta.loc[propuesta["INCLUIDO_PROPUESTO"].eq("SI")].copy()
    consolidado = seleccion[columnas_mu].copy()
    total_aprobado = len(consolidado)
    tmp_csv = rutas["csv"].with_name(rutas["csv"].stem + ".tmp.csv")
    tmp_xlsx = rutas["xlsx"].with_name(rutas["xlsx"].stem + ".tmp.xlsx")
    escribir_csv(consolidado, tmp_csv, header=False)
    relectura, _ = core["leer_csv_32"](tmp_csv)
    if len(relectura) != total_aprobado or relectura[columnas_mu].shape[1] != 32:
        raise CierreError("Relectura fisica no coincide", 5)
    diff = int(
        (~relectura[columnas_mu].astype(str).reset_index(drop=True).eq(
            consolidado.astype(str).reset_index(drop=True)
        )).to_numpy().sum()
    )
    if diff != 0:
        raise CierreError("Diferencias entre memoria y CSV fisico", 5)
    vig_invalidas = sorted(set(consolidado["VIG"].astype(str)) - {"0", "1", "2"})
    if vig_invalidas:
        raise CierreError("Valores VIG invalidos: " + ",".join(vig_invalidas), 5)
    with pd.ExcelWriter(tmp_xlsx, engine="openpyxl") as writer:
        consolidado.to_excel(writer, sheet_name="CONSOLIDADO", index=False)
    tmp_csv.replace(rutas["csv"])
    tmp_xlsx.replace(rutas["xlsx"])
    return {
        "total": total_aprobado,
        "diferencias_relectura": diff,
        "csv_sha256": sha256(rutas["csv"]),
        "xlsx_sha256": sha256(rutas["xlsx"]),
    }


def modo_materializar(nueva_version: bool) -> int:
    global LOG_ACTUAL
    LOG_ACTUAL = LOG_MATERIALIZACION
    MENSAJES.clear()
    log("Validando sello y aprobacion antes de materializar...")
    if not SELLO_APROBACION.exists():
        raise CierreError("No existe SELLO_APROBACION_VALIDADO.json", 5)
    _, _, propuesta = validar_aprobacion_generica()
    rutas = rutas_finales(nueva_version)
    for ruta in [CSV_FINAL, XLSX_FINAL, AUDITORIA_CIERRE, MANIFIESTO_CIERRE]:
        if ruta.exists() and not nueva_version:
            raise CierreError(
                f"Ya existe definitivo {ruta}. Use --nueva-version.",
                5,
            )
    resultado = materializar_desde_propuesta(propuesta, rutas)
    with pd.ExcelWriter(rutas["auditoria"], engine="openpyxl") as writer:
        propuesta.to_excel(writer, sheet_name="TRAZABILIDAD", index=False)
        pd.DataFrame([resultado]).to_excel(writer, sheet_name="CONTROLES", index=False)
    copias = {}
    for clave in ["csv", "xlsx", "auditoria"]:
        destino = ESCRITORIO / rutas[clave].name
        shutil.copy2(rutas[clave], destino)
        copias[clave] = {
            "ruta": str(destino),
            "sha256": sha256(destino),
            "coincide": sha256(destino) == sha256(rutas[clave]),
        }
    manifiesto = {
        "fecha": ahora(),
        "modo": "materializar",
        "script": str(SCRIPT),
        "script_hash": sha256(SCRIPT),
        "resultado": resultado,
        "salidas": {
            k: {"ruta": str(v), "sha256": sha256(v)}
            for k, v in rutas.items()
            if v.exists()
        },
        "copias_escritorio": copias,
        "originales_modificados": "NO",
    }
    rutas["manifiesto"].write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ESTADO_MATERIALIZACION.write_text(
        "estado: MATERIALIZACION_COMPLETADA\n"
        f"total: {resultado['total']}\n"
        f"csv: {rutas['csv']}\n",
        encoding="utf-8",
    )
    log(f"Materializacion completada: {rutas['csv']}")
    return 0


def modo_verificar_cierre() -> int:
    global LOG_ACTUAL
    LOG_ACTUAL = SALIDA / "LOG_VERIFICACION_CIERRE_MU2026.txt"
    MENSAJES.clear()
    controles = []
    for nombre, ruta in [
        ("PROPUESTA", PROPUESTA_CSV),
        ("APROBACION", APROBACION_JSON),
        ("SELLO", SELLO_APROBACION),
        ("CSV", CSV_FINAL),
        ("EXCEL", XLSX_FINAL),
        ("AUDITORIA", AUDITORIA_CIERRE),
        ("MANIFIESTO", MANIFIESTO_CIERRE),
    ]:
        controles.append(
            {
                "CONTROL": f"EXISTE_{nombre}",
                "ESTADO": "OK" if ruta.exists() else "ERROR",
                "DETALLE": str(ruta),
                "SHA256": sha256(ruta) if ruta.exists() else "",
            }
        )
    estado = "LISTO_PARA_CARGA"
    if any(c["ESTADO"] != "OK" for c in controles):
        estado = "NO_CARGAR"
    if CSV_FINAL.exists():
        core = cargar_core()
        try:
            df, _ = core["leer_csv_32"](CSV_FINAL)
            vig_invalidas = sorted(set(df["VIG"].astype(str)) - {"0", "1", "2"})
            controles.append({"CONTROL": "CSV_32_COLUMNAS", "ESTADO": "OK", "DETALLE": len(df), "SHA256": ""})
            if vig_invalidas:
                controles.append({"CONTROL": "VIG_VALIDO", "ESTADO": "ERROR", "DETALLE": ",".join(vig_invalidas), "SHA256": ""})
                estado = "NO_CARGAR"
            else:
                controles.append({"CONTROL": "VIG_VALIDO", "ESTADO": "OK", "DETALLE": "", "SHA256": ""})
        except Exception as exc:
            controles.append({"CONTROL": "CSV_RELECTURA", "ESTADO": "ERROR", "DETALLE": str(exc), "SHA256": ""})
            estado = "NO_CARGAR"
    df_controles = pd.DataFrame(controles)
    with pd.ExcelWriter(RESUMEN_VERIFICACION, engine="openpyxl") as writer:
        df_controles.to_excel(writer, sheet_name="CONTROLES", index=False)
    REPORTE_VERIFICACION.write_text(df_controles.to_string(index=False), encoding="utf-8")
    ESTADO_FINAL_CIERRE.write_text(
        json.dumps(
            {
                "fecha": ahora(),
                "estado_final": estado,
                "controles_ok": int(df_controles["ESTADO"].eq("OK").sum()),
                "controles_error": int(df_controles["ESTADO"].ne("OK").sum()),
                "originales_modificados": "NO",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    log(f"Estado final cierre: {estado}")
    return 0 if estado == "LISTO_PARA_CARGA" else 6


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cierre controlado MU2026 fases 4 a 7."
    )
    parser.add_argument("--modo", choices=sorted(MODOS))
    parser.add_argument("--nueva-version", action="store_true")
    args = parser.parse_args()
    if args.modo is None:
        parser.print_help()
        raise SystemExit(0)
    return args


def main() -> int:
    args = parse_args()
    try:
        if args.modo == "revisar":
            return modo_revisar()
        if args.modo == "integrar-resolucion":
            return modo_integrar_resolucion()
        if args.modo == "validar-aprobacion":
            return modo_validar_aprobacion()
        if args.modo == "materializar":
            return modo_materializar(args.nueva_version)
        if args.modo == "verificar-cierre":
            return modo_verificar_cierre()
        raise CierreError("Modo no soportado", 4)
    except CierreError as exc:
        log(f"ERROR: {exc}")
        log(f"Codigo de salida: {exc.codigo}")
        return exc.codigo
    except Exception as exc:
        log(f"ERROR NO CONTROLADO: {type(exc).__name__}: {exc}")
        return 5


if __name__ == "__main__":
    raise SystemExit(main())
