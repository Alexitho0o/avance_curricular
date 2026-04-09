from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
import hashlib
import json

import pandas as pd


RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular")
SCRIPT = Path(__file__).resolve()
SCRIPT_PRINCIPAL = RAIZ / "scripts" / "consolidar_mu2026_por_codcli.py"

BASE_RECON = (
    RAIZ
    / "resultados"
    / "auditoria_multicodcli_mu2026_reconstruida_desde_cero"
)
BASE_CIERRE = BASE_RECON / "05_cierre_controlado"
SALIDA = BASE_CIERRE / "resolucion_36_conflictos"

PROPUESTA_CSV = BASE_CIERRE / "PROPUESTA_DECISION_FASES4_5.csv"
PROPUESTA_XLSX = BASE_CIERRE / "PROPUESTA_DECISION_FASES4_5.xlsx"
MANIFIESTO_REVISION = BASE_CIERRE / "MANIFIESTO_REVISION_FASES4_5.json"

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
ARCHIVO_30 = (
    BASE_RECON
    / "03_archivos_rectificacion"
    / "RECTIFICACION_MU2026_RECONSTRUIDA_DESDE_CERO.csv"
)

ASIGNACION_95 = (
    BASE_RECON
    / "03_archivos_rectificacion"
    / "consolidacion_codcli"
    / "fase2_asignacion_codcli"
    / "ASIGNACION_CODCLI_95.csv"
)
ASIGNACION_30 = (
    BASE_RECON
    / "03_archivos_rectificacion"
    / "consolidacion_codcli"
    / "fase2_asignacion_codcli"
    / "ASIGNACION_CODCLI_30.csv"
)

DECISIONES_RECON = (
    BASE_RECON / "02_resultados_tecnicos" / "DECISIONES_RECTIFICACION_MU2026.csv"
)
AUDITORIA_VIG = (
    BASE_RECON / "01_auditorias" / "AUDITORIA_VIGENCIA_MATRICULA.csv"
)
AUDITORIA_FILTRO = (
    BASE_RECON / "01_auditorias" / "AUDITORIA_FILTRO_2026_1.csv"
)
AUDITORIA_MAPEO = (
    BASE_RECON / "01_auditorias" / "AUDITORIA_MAPEO_OFERTA_SIES.csv"
)

COMP_AUD_32 = (
    RAIZ
    / "control"
    / "auditoria_mu2026_punto0_complemento95"
    / "archivos_congelados"
    / "complemento_95"
    / "04_auditoria_32_campos_complemento_95.csv"
)
COMP_VIG_DA = (
    RAIZ
    / "control"
    / "auditoria_mu2026_punto0_complemento95"
    / "archivos_congelados"
    / "complemento_95"
    / "02_auditoria_vigencia_datosalumnos.csv"
)
COMP_CONFIRMACION = (
    RAIZ
    / "control"
    / "auditoria_mu2026_punto0_complemento95"
    / "archivos_congelados"
    / "auditorias_previas"
    / "auditoria_confirmacion_vigencia_real_95_codcli.csv"
)

RESOLUCION_XLSX = SALIDA / "RESOLUCION_36_CONFLICTOS_MU2026.xlsx"
RESOLUCION_CSV = SALIDA / "RESOLUCION_36_CONFLICTOS_MU2026.csv"
RESUMEN_JSON = SALIDA / "RESUMEN_RESOLUCION_36_CONFLICTOS.json"
LOG_TXT = SALIDA / "LOG_RESOLUCION_36_CONFLICTOS.txt"
ESTADO_TXT = SALIDA / "ESTADO_RESOLUCION_36_CONFLICTOS.txt"
PROPUESTA_DERIVADA_CSV = (
    SALIDA / "PROPUESTA_DECISION_FASES4_5_RESUELTA_36.csv"
)
PROPUESTA_DERIVADA_XLSX = (
    SALIDA / "PROPUESTA_DECISION_FASES4_5_RESUELTA_36.xlsx"
)

CLASIFICACIONES_PERMITIDAS = {
    "CONSERVAR_COMPLEMENTO_95",
    "INCORPORAR_DESDE_30",
    "YA_REPRESENTADO_NO_AGREGAR",
    "ACTUALIZAR_FILA_EXISTENTE",
    "CONFLICTO_SIN_IMPACTO_CANTIDAD",
    "CONFLICTO_MATERIAL_NO_RESUELTO",
    "SIN_EVIDENCIA_SUFICIENTE",
}

MENSAJES: list[str] = []


def log(texto: str = "") -> None:
    texto = str(texto)
    print(texto, flush=True)
    MENSAJES.append(texto)
    SALIDA.mkdir(parents=True, exist_ok=True)
    LOG_TXT.write_text("\n".join(MENSAJES) + "\n", encoding="utf-8")


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def normalizar_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        out[col] = out[col].fillna("").astype(str).str.strip()
    return out


def leer_csv(ruta: Path, sep: str = ";") -> pd.DataFrame:
    return normalizar_df(
        pd.read_csv(
            ruta,
            sep=sep,
            dtype=str,
            encoding="utf-8-sig",
            keep_default_na=False,
            na_filter=False,
            low_memory=False,
        )
    )


def escribir_csv(df: pd.DataFrame, ruta: Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    normalizar_df(df).to_csv(
        ruta,
        sep=";",
        index=False,
        encoding="utf-8",
        lineterminator="\n",
    )


def cargar_core() -> dict[str, Any]:
    texto = SCRIPT_PRINCIPAL.read_text(encoding="utf-8")
    pos = texto.find("# INICIO")
    if pos == -1:
        raise RuntimeError("No se encontro marcador # INICIO en script principal.")
    espacio: dict[str, Any] = {
        "__file__": str(SCRIPT_PRINCIPAL),
        "__name__": "core_resolver_36_mu2026",
    }
    exec(compile(texto[:pos], str(SCRIPT_PRINCIPAL), "exec"), espacio)
    return espacio


def lista_codcli(texto: str) -> list[str]:
    valores = []
    for parte in str(texto).split("||"):
        parte = parte.strip()
        if parte and parte not in valores:
            valores.append(parte)
    return sorted(valores)


def unir(valores: list[str]) -> str:
    return " || ".join([v for v in valores if v])


def fila_operativa(df: pd.DataFrame, fila: str) -> pd.Series | None:
    sub = df.loc[df["FILA_OPERATIVA"].astype(str).eq(str(fila))]
    if sub.empty:
        return None
    return sub.iloc[0]


def estado_presencia(
    rut: str,
    oferta: str,
    llaves: set[str],
    ruts: set[str],
) -> str:
    llave = f"{rut}|{oferta}"
    if llave in llaves:
        return "RUT_OFERTA_PRESENTE"
    if rut in ruts:
        return "RUT_PRESENTE_OFERTA_AUSENTE"
    return "NO_PRESENTE"


def evidencia_vigencia_rectificacion(
    codcli: str,
    oferta: str,
    vig: pd.DataFrame,
    mapeo: pd.DataFrame,
) -> tuple[bool, str, pd.DataFrame]:
    ev_vig = vig.loc[
        vig["CODCLI"].eq(codcli)
        & vig["ES_2026_1"].eq("SI")
        & vig["MATRICULA_EFECTIVA"].eq("SI")
    ].copy()
    ev_map = mapeo.loc[
        mapeo["CODCLI"].eq(codcli)
        & mapeo["ESTADO_MAPEO"].eq("MAPEO_DEMOSTRADO")
        & mapeo["LLAVE_OFERTA_SIES"].eq(oferta)
    ].copy()
    ok = not ev_vig.empty and not ev_map.empty
    partes = []
    if not ev_vig.empty:
        r = ev_vig.iloc[0]
        partes.append(
            "AUDITORIA_VIGENCIA_MATRICULA: "
            f"CODCLI={codcli}; ES_2026_1=SI; "
            f"MATRICULA_EFECTIVA=SI; FUENTE={r.get('FUENTE','')}; "
            f"HOJA={r.get('HOJA','')}; FILA={r.get('FILA','')}"
        )
    if not ev_map.empty:
        r = ev_map.iloc[0]
        partes.append(
            "AUDITORIA_MAPEO_OFERTA_SIES: "
            f"OFERTA={oferta}; ESTADO_MAPEO=MAPEO_DEMOSTRADO; "
            f"EVIDENCIA={r.get('EVIDENCIA_MAPEO','')}"
        )
    evidencia = pd.concat(
        [
            ev_vig.assign(TIPO_EVIDENCIA="RECTIFICACION_VIGENCIA_2026_1"),
            ev_map.assign(TIPO_EVIDENCIA="RECTIFICACION_MAPEO_OFERTA"),
        ],
        ignore_index=True,
        sort=False,
    ).fillna("")
    return ok, " | ".join(partes), evidencia


def evidencia_vigencia_complemento(
    codcli: str,
    rut: str,
    comp_vig: pd.DataFrame,
    comp_confirm: pd.DataFrame,
) -> tuple[bool, str, pd.DataFrame]:
    ev_da = comp_vig.loc[
        comp_vig["CODCLI"].eq(codcli)
        & comp_vig["RUT"].eq(rut)
        & comp_vig["ANOMATRICULA"].eq("2026")
        & comp_vig["PERIODOMATRICULA"].eq("1")
        & comp_vig["ESTADOACADEMICO"].str.upper().eq("VIGENTE")
    ].copy()
    ev_conf = comp_confirm.loc[
        comp_confirm["CODCLI"].eq(codcli)
        & comp_confirm["RUT_DV"].eq(rut)
        & comp_confirm["ANOMATRICULA"].eq("2026")
        & comp_confirm["PERIODOMATRICULA"].eq("1")
        & comp_confirm["ESTADO_AUDITORIA"].eq("CONFIRMADO_VIGENTE_2026_1")
    ].copy()
    ok = not ev_da.empty and not ev_conf.empty
    partes = []
    if not ev_da.empty:
        r = ev_da.iloc[0]
        partes.append(
            "02_auditoria_vigencia_datosalumnos: "
            f"CODCLI={codcli}; RUT={rut}; "
            f"ANOMATRICULA={r.get('ANOMATRICULA','')}; "
            f"PERIODOMATRICULA={r.get('PERIODOMATRICULA','')}; "
            f"ESTADOACADEMICO={r.get('ESTADOACADEMICO','')}"
        )
    if not ev_conf.empty:
        r = ev_conf.iloc[0]
        partes.append(
            "auditoria_confirmacion_vigencia_real_95_codcli: "
            f"ESTADO_AUDITORIA={r.get('ESTADO_AUDITORIA','')}; "
            f"DECISION_CARGA={r.get('DECISION_CARGA','')}"
        )
    evidencia = pd.concat(
        [
            ev_da.assign(TIPO_EVIDENCIA="COMPLEMENTO_DATOSALUMNOS_2026_1"),
            ev_conf.assign(TIPO_EVIDENCIA="COMPLEMENTO_CONFIRMACION_2026_1"),
        ],
        ignore_index=True,
        sort=False,
    ).fillna("")
    return ok, " | ".join(partes), evidencia


def construir_resolucion() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    core = cargar_core()
    leer_csv_32 = core["leer_csv_32"]

    propuesta = leer_csv(PROPUESTA_CSV, sep=";")
    conflictos = propuesta.loc[
        propuesta["DECISION_PROPUESTA"].eq("CONFLICTO_MATERIAL")
    ].copy()
    if len(conflictos) != 36:
        raise RuntimeError(f"Se esperaban 36 conflictos; encontrados {len(conflictos)}.")

    df_4070, _ = leer_csv_32(ARCHIVO_4070)
    df_95, _ = leer_csv_32(ARCHIVO_95)
    df_30, _ = leer_csv_32(ARCHIVO_30)

    llaves_4070 = set(df_4070["LLAVE_RUT_OFERTA"])
    ruts_4070 = set(df_4070["RUT_NORM"])
    llaves_95 = set(df_95["LLAVE_RUT_OFERTA"])
    ruts_95 = set(df_95["RUT_NORM"])
    llaves_30 = set(df_30["LLAVE_RUT_OFERTA"])
    ruts_30 = set(df_30["RUT_NORM"])

    fase2_95 = leer_csv(ASIGNACION_95, sep=";")
    fase2_30 = leer_csv(ASIGNACION_30, sep=";")
    decisiones = leer_csv(DECISIONES_RECON, sep=",")
    vig = leer_csv(AUDITORIA_VIG, sep=",")
    mapeo = leer_csv(AUDITORIA_MAPEO, sep=",")
    filtro = leer_csv(AUDITORIA_FILTRO, sep=",")
    comp_aud = leer_csv(COMP_AUD_32, sep=",")
    comp_vig = leer_csv(COMP_VIG_DA, sep=",")
    comp_conf = leer_csv(COMP_CONFIRMACION, sep=",")
    comp_conf.columns = [c.replace("\ufeff", "") for c in comp_conf.columns]

    resoluciones: list[dict[str, Any]] = []
    evidencias: list[pd.DataFrame] = []

    # Primero resolver complemento para que la rectificacion pueda detectar
    # representacion ya conservada dentro de los 36.
    complementos_conservados: dict[tuple[str, str, str], dict[str, Any]] = {}

    for _, caso in conflictos.loc[conflictos["ORIGEN"].eq("COMPLEMENTO_95")].iterrows():
        fila = str(caso["FILA_OPERATIVA"])
        fase2 = fila_operativa(fase2_95, fila)
        candidatos = []
        if fase2 is not None:
            candidatos = lista_codcli(fase2.get("CODCLI_EXACTOS", ""))
            for cod in lista_codcli(fase2.get("CODCLI_DEL_RUT", "")):
                if cod not in candidatos:
                    candidatos.append(cod)

        aud = comp_aud.loc[
            comp_aud["N_DOC"].eq(caso["N_DOC"])
            & comp_aud["DV"].eq(caso["DV"])
            & comp_aud["COD_SED"].eq(caso["COD_SED"])
            & comp_aud["COD_CAR"].eq(caso["COD_CAR"])
            & comp_aud["MODALIDAD"].eq(caso["MODALIDAD"])
            & comp_aud["JOR"].eq(caso["JOR"])
            & comp_aud["VERSION"].eq(caso["VERSION"])
        ].copy()
        codcli_resuelto = aud.iloc[0]["CODCLI"] if len(aud) == 1 else ""
        if codcli_resuelto and codcli_resuelto not in candidatos:
            candidatos.insert(0, codcli_resuelto)

        ok_vig, texto_vig, ev = evidencia_vigencia_complemento(
            codcli_resuelto,
            caso["RUT"],
            comp_vig,
            comp_conf,
        )
        if not ev.empty:
            ev = ev.assign(
                ORIGEN_CONFLICTO="COMPLEMENTO_95",
                FILA_OPERATIVA=fila,
                CODCLI_RESUELTO=codcli_resuelto,
            )
            evidencias.append(ev)

        if len(aud) == 1 and ok_vig:
            decision = "CONSERVAR_COMPLEMENTO_95"
            incluido = "SI"
            pendiente = "NO"
            impacto = "SI"
            fundamento = (
                "CODCLI definido por auditoria 32 campos del complemento congelado "
                "y confirmado con ANOMATRICULA=2026, PERIODOMATRICULA=1."
            )
            complementos_conservados[
                (caso["RUT"], caso["OFERTA_SIES"], codcli_resuelto)
            ] = {
                "fila": fila,
                "codcli": codcli_resuelto,
            }
        else:
            decision = "CONFLICTO_MATERIAL_NO_RESUELTO"
            incluido = "NO"
            pendiente = "SI"
            impacto = "SI"
            fundamento = "No fue posible demostrar CODCLI unico y vigencia 2026-1."

        resoluciones.append(
            {
                "ORIGEN": "COMPLEMENTO_95",
                "FILA_OPERATIVA": fila,
                "RUT": caso["RUT"],
                "CODCLI_CANDIDATOS": unir(candidatos),
                "CODCLI_RESUELTO": codcli_resuelto,
                "OFERTA_OPERATIVA": caso["OFERTA_SIES"],
                "EVIDENCIA_2026_1": texto_vig,
                "PRESENCIA_CARGA_PRINCIPAL": estado_presencia(
                    caso["RUT"], caso["OFERTA_SIES"], llaves_4070, ruts_4070
                ),
                "PRESENCIA_COMPLEMENTO": "REGISTRO_CONFLICTO_36_COMPLEMENTO",
                "PRESENCIA_RECTIFICACION": estado_presencia(
                    caso["RUT"], caso["OFERTA_SIES"], llaves_30, ruts_30
                ),
                "DECISION": decision,
                "FUNDAMENTO": fundamento,
                "FUENTE": f"{COMP_AUD_32} | {COMP_VIG_DA} | {COMP_CONFIRMACION}",
                "INCLUIDO": incluido,
                "IMPACTO_EN_TOTAL": impacto,
                "PENDIENTE": pendiente,
                "CLASIFICACION_ORIGINAL": caso["DECISION_PROPUESTA"],
                "CLASIFICACION_FASE2": caso.get("CLASIFICACION_FASE2", ""),
            }
        )

    for _, caso in conflictos.loc[conflictos["ORIGEN"].eq("RECTIFICACION_30")].iterrows():
        fila = str(caso["FILA_OPERATIVA"])
        fase2 = fila_operativa(fase2_30, fila)
        candidatos = []
        if fase2 is not None:
            candidatos = lista_codcli(fase2.get("CODCLI_EXACTOS", ""))
            for cod in lista_codcli(fase2.get("CODCLI_DEL_RUT", "")):
                if cod not in candidatos:
                    candidatos.append(cod)

        dec = decisiones.loc[
            decisiones["RUT"].eq(caso["N_DOC"])
            & decisiones["OFERTA"].eq(caso["OFERTA_SIES"])
            & decisiones["ACCION"].eq("INCORPORAR_MU")
            & decisiones["VALIDACION_AUTOMATICA"].eq("VALIDADO")
        ].copy()
        codcli_resuelto = dec.iloc[0]["CODCLI"] if len(dec) == 1 else ""
        if codcli_resuelto and codcli_resuelto not in candidatos:
            candidatos.insert(0, codcli_resuelto)

        ok_vig, texto_vig, ev = evidencia_vigencia_rectificacion(
            codcli_resuelto,
            caso["OFERTA_SIES"],
            vig,
            mapeo,
        )
        if not ev.empty:
            ev = ev.assign(
                ORIGEN_CONFLICTO="RECTIFICACION_30",
                FILA_OPERATIVA=fila,
                CODCLI_RESUELTO=codcli_resuelto,
            )
            evidencias.append(ev)

        clave = (caso["RUT"], caso["OFERTA_SIES"], codcli_resuelto)
        if clave in complementos_conservados:
            decision = "YA_REPRESENTADO_NO_AGREGAR"
            incluido = "NO"
            pendiente = "NO"
            impacto = "NO"
            fundamento = (
                "Mismo CODCLI + RUT + oferta ya conservado desde complemento 95 "
                f"fila {complementos_conservados[clave]['fila']}."
            )
        elif len(dec) == 1 and ok_vig:
            decision = "INCORPORAR_DESDE_30"
            incluido = "SI"
            pendiente = "NO"
            impacto = "SI"
            fundamento = (
                "Decision reconstruida validada, matrícula efectiva 2026-1 "
                "y mapeo de oferta SIES demostrado."
            )
        else:
            decision = "CONFLICTO_MATERIAL_NO_RESUELTO"
            incluido = "NO"
            pendiente = "SI"
            impacto = "SI"
            fundamento = "No existe decision reconstruida validada con evidencia 2026-1 suficiente."

        fuente_dec = ""
        if len(dec) == 1:
            fuente_dec = (
                f"{DECISIONES_RECON}: {dec.iloc[0].get('EVIDENCIA','')} | "
                f"{dec.iloc[0].get('ARCHIVO_FUENTE','')} | "
                f"{dec.iloc[0].get('HOJA','')} | fila {dec.iloc[0].get('FILA','')}"
            )

        resoluciones.append(
            {
                "ORIGEN": "RECTIFICACION_30",
                "FILA_OPERATIVA": fila,
                "RUT": caso["RUT"],
                "CODCLI_CANDIDATOS": unir(candidatos),
                "CODCLI_RESUELTO": codcli_resuelto,
                "OFERTA_OPERATIVA": caso["OFERTA_SIES"],
                "EVIDENCIA_2026_1": texto_vig,
                "PRESENCIA_CARGA_PRINCIPAL": estado_presencia(
                    caso["RUT"], caso["OFERTA_SIES"], llaves_4070, ruts_4070
                ),
                "PRESENCIA_COMPLEMENTO": estado_presencia(
                    caso["RUT"], caso["OFERTA_SIES"], llaves_95, ruts_95
                ),
                "PRESENCIA_RECTIFICACION": "REGISTRO_CONFLICTO_36_RECTIFICACION",
                "DECISION": decision,
                "FUNDAMENTO": fundamento,
                "FUENTE": fuente_dec,
                "INCLUIDO": incluido,
                "IMPACTO_EN_TOTAL": impacto,
                "PENDIENTE": pendiente,
                "CLASIFICACION_ORIGINAL": caso["DECISION_PROPUESTA"],
                "CLASIFICACION_FASE2": caso.get("CLASIFICACION_FASE2", ""),
            }
        )

    resolucion = normalizar_df(pd.DataFrame(resoluciones))
    invalidas = set(resolucion["DECISION"]) - CLASIFICACIONES_PERMITIDAS
    if invalidas:
        raise RuntimeError(f"Clasificaciones no permitidas: {sorted(invalidas)}")

    evidencia = (
        normalizar_df(pd.concat(evidencias, ignore_index=True, sort=False))
        if evidencias
        else pd.DataFrame()
    )

    controles = {
        "fecha": ahora(),
        "script": str(SCRIPT),
        "script_sha256": sha256(SCRIPT),
        "propuesta_csv": str(PROPUESTA_CSV),
        "propuesta_csv_sha256": sha256(PROPUESTA_CSV),
        "propuesta_xlsx_sha256": sha256(PROPUESTA_XLSX),
        "manifiesto_revision_sha256": sha256(MANIFIESTO_REVISION),
        "carga_principal_sha256": sha256(ARCHIVO_4070),
        "complemento_95_sha256": sha256(ARCHIVO_95),
        "rectificacion_30_sha256": sha256(ARCHIVO_30),
        "asignacion_95_sha256": sha256(ASIGNACION_95),
        "asignacion_30_sha256": sha256(ASIGNACION_30),
        "decisiones_reconstruccion_sha256": sha256(DECISIONES_RECON),
        "auditoria_vigencia_sha256": sha256(AUDITORIA_VIG),
        "auditoria_mapeo_sha256": sha256(AUDITORIA_MAPEO),
        "conflictos_analizados": len(resolucion),
        "originales_modificados": "NO",
    }
    return resolucion, evidencia, controles


def actualizar_propuesta_derivada(resolucion: pd.DataFrame) -> tuple[Path | None, Path | None]:
    if resolucion["PENDIENTE"].eq("SI").any():
        return None, None

    propuesta = leer_csv(PROPUESTA_CSV, sep=";")
    for _, res in resolucion.iterrows():
        mask = (
            propuesta["ORIGEN"].eq(res["ORIGEN"])
            & propuesta["FILA_OPERATIVA"].astype(str).eq(str(res["FILA_OPERATIVA"]))
            & propuesta["DECISION_PROPUESTA"].eq("CONFLICTO_MATERIAL")
        )
        propuesta.loc[mask, "DECISION_PROPUESTA"] = res["DECISION"]
        propuesta.loc[mask, "CODCLI"] = res["CODCLI_RESUELTO"]
        propuesta.loc[mask, "FUNDAMENTO"] = res["FUNDAMENTO"]
        propuesta.loc[mask, "FUENTE_EVIDENCIA"] = res["FUENTE"]
        propuesta.loc[mask, "INCLUIDO_PROPUESTO"] = res["INCLUIDO"]
        propuesta.loc[mask, "PENDIENTE"] = res["PENDIENTE"]
        propuesta.loc[mask, "IMPACTO_TOTAL"] = res["IMPACTO_EN_TOTAL"]
        propuesta.loc[mask, "ESTADO_INSTITUCIONAL_2026_1"] = (
            "RESUELTO_CON_EVIDENCIA_2026_1"
        )

    escribir_csv(propuesta, PROPUESTA_DERIVADA_CSV)
    with pd.ExcelWriter(PROPUESTA_DERIVADA_XLSX, engine="openpyxl") as writer:
        propuesta.to_excel(writer, sheet_name="PROPUESTA_RESUELTA", index=False)
        pd.DataFrame(
            propuesta.groupby(["ORIGEN", "DECISION_PROPUESTA"], dropna=False)
            .size()
            .reset_index(name="N")
        ).to_excel(writer, sheet_name="RESUMEN", index=False)
    return PROPUESTA_DERIVADA_CSV, PROPUESTA_DERIVADA_XLSX


def main() -> int:
    SALIDA.mkdir(parents=True, exist_ok=True)
    MENSAJES.clear()
    log("Resolviendo exclusivamente 36 conflictos materiales MU2026...")
    resolucion, evidencia, controles = construir_resolucion()

    pendientes = resolucion.loc[resolucion["PENDIENTE"].eq("SI")].copy()
    resueltos = resolucion.loc[resolucion["PENDIENTE"].eq("NO")].copy()
    impacto = (
        resolucion.groupby(["DECISION", "INCLUIDO", "IMPACTO_EN_TOTAL"], dropna=False)
        .size()
        .reset_index(name="CASOS")
        .sort_values(["DECISION", "INCLUIDO", "IMPACTO_EN_TOTAL"])
    )

    propuesta_der_csv, propuesta_der_xlsx = actualizar_propuesta_derivada(resolucion)

    resumen = {
        "fecha": ahora(),
        "conflictos_analizados": int(len(resolucion)),
        "conflictos_resueltos": int(len(resueltos)),
        "conflictos_pendientes": int(len(pendientes)),
        "incorporaciones_desde_30": int(
            resolucion["DECISION"].eq("INCORPORAR_DESDE_30").sum()
        ),
        "complemento_95_conservado": int(
            resolucion["DECISION"].eq("CONSERVAR_COMPLEMENTO_95").sum()
        ),
        "casos_ya_representados": int(
            resolucion["DECISION"].eq("YA_REPRESENTADO_NO_AGREGAR").sum()
        ),
        "actualizaciones": int(
            resolucion["DECISION"].eq("ACTUALIZAR_FILA_EXISTENTE").sum()
        ),
        "total_revisado_propuesto": 4070
        + int(resolucion["INCLUIDO"].eq("SI").sum()),
        "propuesta_derivada_csv": str(propuesta_der_csv or ""),
        "propuesta_derivada_xlsx": str(propuesta_der_xlsx or ""),
        "originales_modificados": "NO",
    }

    escribir_csv(resolucion, RESOLUCION_CSV)
    controles_df = pd.DataFrame(
        [{"CONTROL": k, "VALOR": v} for k, v in controles.items()]
    )
    resumen_df = pd.DataFrame([resumen])

    with pd.ExcelWriter(RESOLUCION_XLSX, engine="openpyxl") as writer:
        resumen_df.to_excel(writer, sheet_name="RESUMEN", index=False)
        resueltos.to_excel(writer, sheet_name="CASOS_RESUELTOS", index=False)
        pendientes.to_excel(writer, sheet_name="CASOS_PENDIENTES", index=False)
        evidencia.to_excel(writer, sheet_name="EVIDENCIA_2026_1", index=False)
        impacto.to_excel(writer, sheet_name="IMPACTO_EN_TOTAL", index=False)
        controles_df.to_excel(writer, sheet_name="CONTROLES", index=False)

    hashes = {
        "RESOLUCION_36_CONFLICTOS_MU2026.xlsx": sha256(RESOLUCION_XLSX),
        "RESOLUCION_36_CONFLICTOS_MU2026.csv": sha256(RESOLUCION_CSV),
        "LOG_RESOLUCION_36_CONFLICTOS.txt": sha256(LOG_TXT),
    }
    if propuesta_der_csv:
        hashes[propuesta_der_csv.name] = sha256(propuesta_der_csv)
    if propuesta_der_xlsx:
        hashes[propuesta_der_xlsx.name] = sha256(propuesta_der_xlsx)

    resumen["hashes"] = hashes
    RESUMEN_JSON.write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    hashes["RESUMEN_RESOLUCION_36_CONFLICTOS.json"] = sha256(RESUMEN_JSON)
    resumen["hashes"] = hashes
    RESUMEN_JSON.write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    estado = {
        "estado": "RESOLUCION_COMPLETA"
        if resumen["conflictos_pendientes"] == 0
        else "RESOLUCION_CON_PENDIENTES",
        **resumen,
    }
    ESTADO_TXT.write_text(
        "\n".join(f"{k}: {v}" for k, v in estado.items() if k != "hashes")
        + "\n",
        encoding="utf-8",
    )

    log(f"Conflictos analizados: {resumen['conflictos_analizados']}")
    log(f"Conflictos resueltos: {resumen['conflictos_resueltos']}")
    log(f"Conflictos pendientes: {resumen['conflictos_pendientes']}")
    log(f"Incorporaciones desde los 30: {resumen['incorporaciones_desde_30']}")
    log(f"Complemento 95 conservado: {resumen['complemento_95_conservado']}")
    log(f"Casos ya representados: {resumen['casos_ya_representados']}")
    log(f"Actualizaciones: {resumen['actualizaciones']}")
    log(f"Total revisado propuesto: {resumen['total_revisado_propuesto']}")
    log(f"Salida Excel: {RESOLUCION_XLSX}")
    log(f"Salida CSV: {RESOLUCION_CSV}")
    return 0 if resumen["conflictos_pendientes"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
