#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import csv
import hashlib
import json
import re
import unicodedata

import pandas as pd


RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular").resolve()

BASE_GOB = (
    RAIZ
    / "avance_curricular_2026"
    / "06_gobernanza_columnas_5809"
    / "GOBERNANZA_COLUMNAS_5809_20260703_231812"
)

FUENTE_5809 = (
    RAIZ
    / "avance_curricular_2026"
    / "00_fuentes_congeladas"
    / "CARGA_CONGELADA_20260626_005826"
    / "originales"
    / "5809_Precarga Matrícula Avance Curricular 2026.csv"
)

FUENTE_PROMEDIOS = (
    RAIZ
    / "avance_curricular_2026"
    / "00_fuentes_congeladas"
    / "CARGA_CONGELADA_20260626_005826"
    / "originales"
    / "PROMEDIOSDEALUMNOS_7804.xlsx"
)

MATRIZ_GOB = BASE_GOB / "09_MATRIZ_MAESTRA_GOBERNANZA_5809.xlsx"
MANUAL_GOB = BASE_GOB / "10_MANUAL_GOBERNADO_5809_AVANCE_CURRICULAR_2026.md"
BLOQUEOS = BASE_GOB / "14_EXPEDIENTE_BLOQUEOS_FINAL.xlsx"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026"
    / "06_gobernanza_columnas_5809"
    / f"MAPEO_PROMEDIOS_7804_PRUEBA_16_19_{timestamp}"
)

RESULTADOS = SALIDA / "02_RESULTADOS"
AUDITORIA = SALIDA / "03_AUDITORIA"
REPORTES = SALIDA / "04_REPORTES"

for carpeta in [RESULTADOS, AUDITORIA, REPORTES]:
    carpeta.mkdir(parents=True, exist_ok=True)


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def detectar_csv(path):
    raw = path.read_bytes()

    for enc in ["utf-8-sig", "utf-8", "cp1252", "latin1"]:
        try:
            texto = raw.decode(enc)
            encoding = enc
            break
        except UnicodeDecodeError:
            continue
    else:
        raise RuntimeError(f"No se pudo detectar codificación: {path}")

    try:
        dialecto = csv.Sniffer().sniff(
            texto[:10000],
            delimiters=[";", ",", "\t", "|"],
        )
        delimitador = dialecto.delimiter
    except Exception:
        delimitador = ";"

    return encoding, delimitador


def norm_texto(valor):
    texto = str(valor or "").strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^A-Z0-9]+", "_", texto)
    return texto.strip("_")


def normalizar_rut(valor):
    texto = str(valor or "").strip().upper()
    texto = texto.replace(".", "").replace("-", "")
    texto = re.sub(r"[^0-9K]", "", texto)

    if texto.endswith("0") and len(texto) > 8:
        # No se altera como regla. Solo se conserva normalización literal.
        pass

    return texto


def normalizar_codcli(valor):
    return str(valor or "").strip().upper()


def buscar_columna(cols, candidatos):
    mapa = {norm_texto(c): c for c in cols}

    for cand in candidatos:
        cand_norm = norm_texto(cand)
        if cand_norm in mapa:
            return mapa[cand_norm]

    # búsqueda contiene
    for col in cols:
        col_norm = norm_texto(col)
        for cand in candidatos:
            cand_norm = norm_texto(cand)
            if cand_norm and cand_norm in col_norm:
                return col

    return None


def clasificar_columna(nombre):
    n = norm_texto(nombre)
    grupos = []

    if any(t in n for t in ["CODCLI", "COD_ALUM", "CODIGO_ALUM", "CLIENTE"]):
        grupos.append("CODCLI")

    if any(t in n for t in ["RUT", "NUM_DOCUMENTO", "DOCUMENTO", "DNI", "PASAPORTE"]):
        grupos.append("RUT_DOCUMENTO")

    if any(t in n for t in ["CODCARPR", "CODCARR", "COD_CARR", "CARRERA", "CODIGO_CARRERA"]):
        grupos.append("CARRERA")

    if any(t in n for t in ["PLAN", "MALLA", "CODPESTUD"]):
        grupos.append("PLAN_MALLA")

    if any(t in n for t in ["ANIO", "ANO", "AÑO", "PERIODO"]):
        grupos.append("ANIO_PERIODO")

    if any(t in n for t in ["SEMESTRE", "SEM"]):
        grupos.append("SEMESTRE")

    if any(t in n for t in ["NIVEL", "CURSO"]):
        grupos.append("CURSO_NIVEL")

    if any(t in n for t in ["ASIGNATURA", "RAMO", "ACTIVIDAD", "MODULO"]):
        grupos.append("ASIGNATURA")

    if any(t in n for t in ["CREDIT", "UNIDAD", "HORAS", "SCT"]):
        grupos.append("UNIDADES")

    if any(t in n for t in ["SITUACION", "ESTADO", "APROB", "REPROB", "NOTA"]):
        grupos.append("ESTADO_APROBACION")

    if any(t in n for t in ["CONVALID", "HOMOLOG", "RECONOC"]):
        grupos.append("CONVALIDACION")

    return " | ".join(grupos) if grupos else "OTRA"


for ruta in [FUENTE_5809, FUENTE_PROMEDIOS, MATRIZ_GOB, MANUAL_GOB, BLOQUEOS]:
    if not ruta.exists():
        raise SystemExit(f"No existe fuente requerida: {ruta}")


encoding_5809, sep_5809 = detectar_csv(FUENTE_5809)

df_5809 = pd.read_csv(
    FUENTE_5809,
    sep=sep_5809,
    encoding=encoding_5809,
    dtype=str,
    keep_default_na=False,
    header=0,
    engine="python",
)

df_5809["_RUT_5809_NORM"] = (
    df_5809["NUM_DOCUMENTO"].astype(str).map(normalizar_rut)
    + df_5809["DV"].astype(str).map(normalizar_rut)
)

df_5809["_DOC_5809_NORM"] = df_5809["NUM_DOCUMENTO"].astype(str).map(normalizar_rut)


xls = pd.ExcelFile(FUENTE_PROMEDIOS, engine="openpyxl")

inventario = []
columnas_todas = []

for hoja in xls.sheet_names:
    dfh = pd.read_excel(
        FUENTE_PROMEDIOS,
        sheet_name=hoja,
        dtype=str,
        keep_default_na=False,
        engine="openpyxl",
    )

    cols = list(dfh.columns)

    tipos = {}
    for col in cols:
        tipo = clasificar_columna(col)
        tipos.setdefault(tipo, []).append(col)

        columnas_todas.append({
            "HOJA": hoja,
            "COLUMNA": col,
            "TIPO_DETECTADO": tipo,
            "NO_VACIOS": int(dfh[col].astype(str).str.strip().ne("").sum()),
            "VALORES_UNICOS": int(dfh[col].astype(str).nunique(dropna=False)),
            "MUESTRA": " | ".join(dfh[col].astype(str).head(8).tolist()),
        })

    score = 0
    score += 3 if any("CODCLI" in k for k in tipos) else 0
    score += 2 if any("RUT_DOCUMENTO" in k for k in tipos) else 0
    score += 2 if any("CARRERA" in k for k in tipos) else 0
    score += 2 if any("ANIO_PERIODO" in k for k in tipos) else 0
    score += 2 if any("SEMESTRE" in k for k in tipos) else 0
    score += 2 if any("CURSO_NIVEL" in k for k in tipos) else 0
    score += 3 if any("UNIDADES" in k for k in tipos) else 0
    score += 3 if any("ESTADO_APROBACION" in k for k in tipos) else 0
    score += 1 if any("CONVALIDACION" in k for k in tipos) else 0

    inventario.append({
        "HOJA": hoja,
        "FILAS": len(dfh),
        "COLUMNAS": len(dfh.columns),
        "SCORE_UTILIDAD_16_19": score,
        "COLUMNAS_CODCLI": " | ".join(tipos.get("CODCLI", [])),
        "COLUMNAS_RUT_DOCUMENTO": " | ".join(tipos.get("RUT_DOCUMENTO", [])),
        "COLUMNAS_CARRERA": " | ".join(tipos.get("CARRERA", [])),
        "COLUMNAS_PLAN_MALLA": " | ".join(tipos.get("PLAN_MALLA", [])),
        "COLUMNAS_ANIO_PERIODO": " | ".join(tipos.get("ANIO_PERIODO", [])),
        "COLUMNAS_SEMESTRE": " | ".join(tipos.get("SEMESTRE", [])),
        "COLUMNAS_CURSO_NIVEL": " | ".join(tipos.get("CURSO_NIVEL", [])),
        "COLUMNAS_ASIGNATURA": " | ".join(tipos.get("ASIGNATURA", [])),
        "COLUMNAS_UNIDADES": " | ".join(tipos.get("UNIDADES", [])),
        "COLUMNAS_ESTADO_APROBACION": " | ".join(tipos.get("ESTADO_APROBACION", [])),
        "COLUMNAS_CONVALIDACION": " | ".join(tipos.get("CONVALIDACION", [])),
    })

inventario_df = pd.DataFrame(inventario).sort_values(
    ["SCORE_UTILIDAD_16_19", "FILAS"],
    ascending=False,
)

columnas_todas_df = pd.DataFrame(columnas_todas)


# -------------------------------------------------------------------
# Hoja1 como fuente de prueba.
# -------------------------------------------------------------------

if "Hoja1" not in xls.sheet_names:
    raise SystemExit("No existe Hoja1 en PROMEDIOSDEALUMNOS_7804.xlsx")

hoja_prueba = "Hoja1"

df_hoja1 = pd.read_excel(
    FUENTE_PROMEDIOS,
    sheet_name=hoja_prueba,
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

cols = list(df_hoja1.columns)

col_codcli = buscar_columna(cols, ["CODCLI", "COD_ALUMNO", "CODIGO_ALUMNO"])
col_rut = buscar_columna(cols, ["RUT", "NUM_DOCUMENTO", "DOCUMENTO"])
col_dv = buscar_columna(cols, ["DV"])
col_carrera = buscar_columna(cols, ["CODCARPR", "CODCARR", "COD_CARRERA", "CARRERA"])
col_anio = buscar_columna(cols, ["ANIO", "AÑO", "ANO", "PERIODO_ANIO"])
col_sem = buscar_columna(cols, ["SEMESTRE", "SEM", "PERIODO_SEM"])
col_nivel = buscar_columna(cols, ["NIVEL", "CURSO"])
col_unidades = buscar_columna(cols, ["UNIDADES", "CREDITOS", "CREDITOS_ASIGNATURA", "HORAS", "SCT"])
col_estado = buscar_columna(cols, ["SITUACION", "ESTADO", "ESTADO_ASIGNATURA", "SITUACION_FINAL"])
col_aprob = buscar_columna(cols, ["APROBADA", "APROBACION", "APRUEBA"])
col_conval = buscar_columna(cols, ["CONVALIDACION", "CONVALIDADA", "HOMOLOGACION", "RECONOCIMIENTO"])
col_asig = buscar_columna(cols, ["ASIGNATURA", "RAMO", "ACTIVIDAD", "MODULO"])


# Normalizaciones.
if col_codcli:
    df_hoja1["_CODCLI_NORM"] = df_hoja1[col_codcli].map(normalizar_codcli)
else:
    df_hoja1["_CODCLI_NORM"] = ""

if col_rut:
    df_hoja1["_RUT_HOJA1_NORM"] = df_hoja1[col_rut].map(normalizar_rut)
else:
    df_hoja1["_RUT_HOJA1_NORM"] = ""

if col_dv and col_rut:
    df_hoja1["_RUT_HOJA1_CON_DV_NORM"] = (
        df_hoja1[col_rut].map(normalizar_rut)
        + df_hoja1[col_dv].map(normalizar_rut)
    )
else:
    df_hoja1["_RUT_HOJA1_CON_DV_NORM"] = df_hoja1["_RUT_HOJA1_NORM"]


# Seleccionar muestra de 15 casos con match por RUT o por CODCLI si existe mapeo.
# Primero intentamos por RUT completo y documento.
docs_hoja1 = set(df_hoja1["_RUT_HOJA1_NORM"])
docs_hoja1_dv = set(df_hoja1["_RUT_HOJA1_CON_DV_NORM"])

df_5809["_MATCH_HOJA1_DOC"] = df_5809["_DOC_5809_NORM"].isin(docs_hoja1)
df_5809["_MATCH_HOJA1_RUT_DV"] = df_5809["_RUT_5809_NORM"].isin(docs_hoja1_dv)

muestra_15 = df_5809[
    df_5809["_MATCH_HOJA1_DOC"] | df_5809["_MATCH_HOJA1_RUT_DV"]
].head(15).copy()

if muestra_15.empty:
    # Si no matchea por RUT, tomar 15 de 5809 igual para mostrar que falta mapeo.
    muestra_15 = df_5809.head(15).copy()
    modo_muestra = "SIN_MATCH_RUT_TOMA_PRIMEROS_15_5809"
else:
    modo_muestra = "MATCH_RUT_O_DOCUMENTO_HOJA1"


# Cruce de muestra.
cruces = []

for _, alumno in muestra_15.iterrows():
    doc = alumno["_DOC_5809_NORM"]
    rut_dv = alumno["_RUT_5809_NORM"]

    det = df_hoja1[
        df_hoja1["_RUT_HOJA1_NORM"].eq(doc)
        | df_hoja1["_RUT_HOJA1_CON_DV_NORM"].eq(rut_dv)
    ].copy()

    if det.empty and col_codcli:
        # No existe CODCLI en 5809; queda pendiente si no hay mapeo.
        pass

    total_det = len(det)

    # Filtrar año 2025 si existe columna año/período.
    det_2025 = det.copy()

    if col_anio:
        det_2025 = det_2025[
            det_2025[col_anio].astype(str).str.contains("2025", na=False)
        ].copy()

    # Semestres.
    det_s1 = det_2025.copy()
    det_s2 = det_2025.copy()

    if col_sem:
        det_s1 = det_2025[
            det_2025[col_sem].astype(str).str.strip().isin(["1", "01", "I"])
        ].copy()

        det_s2 = det_2025[
            det_2025[col_sem].astype(str).str.strip().isin(["2", "02", "II"])
        ].copy()

    # Curso semestre: máximo NIVEL observado del período/semestre como prueba técnica,
    # no como regla final.
    curso_s1 = ""
    curso_s2 = ""

    if col_nivel:
        niv_s1 = pd.to_numeric(det_s1[col_nivel], errors="coerce")
        niv_s2 = pd.to_numeric(det_s2[col_nivel], errors="coerce")

        if niv_s1.notna().any():
            curso_s1 = str(int(niv_s1.max()))

        if niv_s2.notna().any():
            curso_s2 = str(int(niv_s2.max()))

    # Unidades cursadas/aprobadas: suma unidades si existe columna.
    unidades_cursadas = ""
    unidades_aprobadas = ""

    if col_unidades:
        unidades_num = pd.to_numeric(det_2025[col_unidades], errors="coerce").fillna(0)
        unidades_cursadas = float(unidades_num.sum())

        if col_estado or col_aprob:
            col_estado_real = col_estado or col_aprob
            estado_norm = det_2025[col_estado_real].astype(str).map(norm_texto)

            mask_aprob = estado_norm.str.contains("APROB", na=False)

            unidades_aprobadas = float(
                pd.to_numeric(
                    det_2025.loc[mask_aprob, col_unidades],
                    errors="coerce",
                ).fillna(0).sum()
            )

    cruces.append({
        "TIPO_DOCUMENTO": alumno.get("TIPO_DOCUMENTO", ""),
        "NUM_DOCUMENTO": alumno.get("NUM_DOCUMENTO", ""),
        "DV": alumno.get("DV", ""),
        "RUT_5809_NORM": rut_dv,
        "DOC_5809_NORM": doc,
        "CODIGO_UNICO": alumno.get("CODIGO_UNICO", ""),
        "PLAN_ESTUDIOS": alumno.get("PLAN_ESTUDIOS", ""),
        "REGISTROS_HOJA1_MATCH_TOTAL": total_det,
        "REGISTROS_HOJA1_2025": len(det_2025),
        "REGISTROS_HOJA1_2025_S1": len(det_s1),
        "REGISTROS_HOJA1_2025_S2": len(det_s2),
        "CURSO_1ER_SEM_PRUEBA": curso_s1,
        "CURSO_2DO_SEM_PRUEBA": curso_s2,
        "UNIDADES_CURSADAS_PRUEBA": unidades_cursadas,
        "UNIDADES_APROBADAS_PRUEBA": unidades_aprobadas,
        "ESTADO_PRUEBA": (
            "CALCULO_PARCIAL_POSIBLE"
            if total_det > 0 and (col_nivel or col_unidades)
            else "SIN_MATCH_O_COLUMNAS_INSUFICIENTES"
        ),
    })

prueba_15_df = pd.DataFrame(cruces)


# Evaluación de factibilidad por columna.
factibilidad = []

def tiene(col):
    return "SI" if col else "NO"

for campo in ["CURSO_1ER_SEM", "CURSO_2DO_SEM"]:
    ok = bool(col_nivel and (col_anio or col_sem))
    factibilidad.append({
        "CAMPO_5809": campo,
        "HOJA_PRUEBA": hoja_prueba,
        "COLUMNAS_REQUERIDAS": "RUT/CODCLI + NIVEL + ANIO/PERIODO + SEMESTRE",
        "COLUMNAS_DETECTADAS": json.dumps({
            "RUT": col_rut or "",
            "CODCLI": col_codcli or "",
            "NIVEL": col_nivel or "",
            "ANIO": col_anio or "",
            "SEMESTRE": col_sem or "",
        }, ensure_ascii=False),
        "FACTIBILIDAD": (
            "POSIBLE_PARA_PRUEBA_CONTROLADA"
            if ok else "BLOQUEADO_COLUMNAS_MINIMAS"
        ),
        "OBSERVACION": (
            "Se puede probar cálculo de curso por semestre, sujeto a regla oficial/manual."
            if ok else "Falta ANIO/SEMESTRE o NIVEL para separar curso semestral."
        ),
    })

for campo in ["UNIDADES_CURSADAS", "UNIDADES_APROBADAS"]:
    ok = bool(col_unidades and (col_anio or col_sem))
    ok_aprob = bool(ok and (col_estado or col_aprob))
    factibilidad.append({
        "CAMPO_5809": campo,
        "HOJA_PRUEBA": hoja_prueba,
        "COLUMNAS_REQUERIDAS": "RUT/CODCLI + ANIO/PERIODO + SEMESTRE + UNIDADES + ESTADO/APROBACION",
        "COLUMNAS_DETECTADAS": json.dumps({
            "RUT": col_rut or "",
            "CODCLI": col_codcli or "",
            "ANIO": col_anio or "",
            "SEMESTRE": col_sem or "",
            "UNIDADES": col_unidades or "",
            "ESTADO": col_estado or col_aprob or "",
        }, ensure_ascii=False),
        "FACTIBILIDAD": (
            "POSIBLE_PARA_PRUEBA_CONTROLADA"
            if ok_aprob else "BLOQUEADO_COLUMNAS_MINIMAS"
        ),
        "OBSERVACION": (
            "Se puede probar suma de unidades cursadas/aprobadas, sujeto a regla oficial/manual."
            if ok_aprob else "Falta unidad/crédito, período o estado de aprobación."
        ),
    })

factibilidad_df = pd.DataFrame(factibilidad)


validaciones = pd.DataFrame([
    {
        "VALIDACION": "PROMEDIOS_MAPEADO_TODAS_HOJAS",
        "RESULTADO": "OK",
        "DETALLE": " | ".join(xls.sheet_names),
    },
    {
        "VALIDACION": "HOJA1_EXISTE",
        "RESULTADO": "OK",
        "DETALLE": len(df_hoja1),
    },
    {
        "VALIDACION": "HOJA1_CODCLI_DETECTADO",
        "RESULTADO": "OK" if col_codcli else "REVISAR",
        "DETALLE": col_codcli or "NO_DETECTADO",
    },
    {
        "VALIDACION": "HOJA1_RUT_DETECTADO",
        "RESULTADO": "OK" if col_rut else "REVISAR",
        "DETALLE": col_rut or "NO_DETECTADO",
    },
    {
        "VALIDACION": "HOJA1_ANIO_DETECTADO",
        "RESULTADO": "OK" if col_anio else "REVISAR",
        "DETALLE": col_anio or "NO_DETECTADO",
    },
    {
        "VALIDACION": "HOJA1_SEMESTRE_DETECTADO",
        "RESULTADO": "OK" if col_sem else "REVISAR",
        "DETALLE": col_sem or "NO_DETECTADO",
    },
    {
        "VALIDACION": "HOJA1_NIVEL_DETECTADO",
        "RESULTADO": "OK" if col_nivel else "REVISAR",
        "DETALLE": col_nivel or "NO_DETECTADO",
    },
    {
        "VALIDACION": "HOJA1_UNIDADES_DETECTADAS",
        "RESULTADO": "OK" if col_unidades else "REVISAR",
        "DETALLE": col_unidades or "NO_DETECTADO",
    },
    {
        "VALIDACION": "HOJA1_ESTADO_APROBACION_DETECTADO",
        "RESULTADO": "OK" if (col_estado or col_aprob) else "REVISAR",
        "DETALLE": col_estado or col_aprob or "NO_DETECTADO",
    },
    {
        "VALIDACION": "MUESTRA_15_GENERADA",
        "RESULTADO": "OK" if len(prueba_15_df) == 15 else "REVISAR",
        "DETALLE": f"{len(prueba_15_df)} / {modo_muestra}",
    },
    {
        "VALIDACION": "CSV_CARGA_GENERADO",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
    {
        "VALIDACION": "SIES_READY_GENERADO",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
    {
        "VALIDACION": "FUENTES_ORIGINALES_MODIFICADAS",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
])


fuentes = pd.DataFrame([
    {"FUENTE": "PRECARGA_5809", "RUTA": str(FUENTE_5809), "SHA256": sha256(FUENTE_5809)},
    {"FUENTE": "PROMEDIOSDEALUMNOS_7804", "RUTA": str(FUENTE_PROMEDIOS), "SHA256": sha256(FUENTE_PROMEDIOS)},
    {"FUENTE": "MATRIZ_GOBERNANZA_5809", "RUTA": str(MATRIZ_GOB), "SHA256": sha256(MATRIZ_GOB)},
    {"FUENTE": "MANUAL_GOBERNADO_5809", "RUTA": str(MANUAL_GOB), "SHA256": sha256(MANUAL_GOB)},
    {"FUENTE": "EXPEDIENTE_BLOQUEOS", "RUTA": str(BLOQUEOS), "SHA256": sha256(BLOQUEOS)},
])


inventario_df.to_csv(RESULTADOS / "01_MAPEO_HOJAS_PROMEDIOS_7804.tsv", sep="\t", index=False)
columnas_todas_df.to_csv(RESULTADOS / "02_MAPEO_COLUMNAS_PROMEDIOS_7804.tsv", sep="\t", index=False)
factibilidad_df.to_csv(RESULTADOS / "03_FACTIBILIDAD_HOJA1_COLUMNAS_16_19.tsv", sep="\t", index=False)
prueba_15_df.to_csv(RESULTADOS / "04_PRUEBA_15_RUT_CODCLI_HOJA1.tsv", sep="\t", index=False)
validaciones.to_csv(RESULTADOS / "05_VALIDACIONES_MAPEO_PRUEBA.tsv", sep="\t", index=False)
fuentes.to_csv(AUDITORIA / "FUENTES_MAPEO_PROMEDIOS_7804.tsv", sep="\t", index=False)

excel = RESULTADOS / "MAPEO_PROMEDIOS_7804_PRUEBA_16_19.xlsx"

with pd.ExcelWriter(excel, engine="openpyxl") as writer:
    inventario_df.to_excel(writer, sheet_name="MAPEO_HOJAS", index=False)
    columnas_todas_df.to_excel(writer, sheet_name="MAPEO_COLUMNAS", index=False)
    factibilidad_df.to_excel(writer, sheet_name="FACTIBILIDAD_HOJA1", index=False)
    prueba_15_df.to_excel(writer, sheet_name="PRUEBA_15", index=False)
    validaciones.to_excel(writer, sheet_name="VALIDACIONES", index=False)
    fuentes.to_excel(writer, sheet_name="FUENTES", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

        for col in ws.columns:
            letra = col[0].column_letter
            ancho = max(len(str(cell.value or "")) for cell in col[:2000])
            ws.column_dimensions[letra].width = min(max(ancho + 2, 12), 70)


if factibilidad_df["FACTIBILIDAD"].eq("POSIBLE_PARA_PRUEBA_CONTROLADA").all():
    estado = "HOJA1_CONTIENE_COLUMNAS_MINIMAS_PARA_PRUEBA_16_19"
elif factibilidad_df["FACTIBILIDAD"].eq("POSIBLE_PARA_PRUEBA_CONTROLADA").any():
    estado = "HOJA1_CONTIENE_COLUMNAS_PARCIALES_PARA_PRUEBA_16_19"
else:
    estado = "HOJA1_NO_CONTIENE_COLUMNAS_MINIMAS_16_19"


informe = REPORTES / "INFORME_MAPEO_PROMEDIOS_7804_PRUEBA_16_19.md"

informe.write_text(
f"""# Mapeo PROMEDIOSDEALUMNOS_7804 y prueba columnas 16-19

## Contexto

Proceso: Avance Curricular SIES 2026  
Subproyecto: Matrícula 5809  
Año de referencia: 2025  

## Objetivo

Mapear todas las hojas de `PROMEDIOSDEALUMNOS_7804.xlsx` y probar `Hoja1` como fuente para construir:

- `CURSO_1ER_SEM`
- `CURSO_2DO_SEM`
- `UNIDADES_CURSADAS`
- `UNIDADES_APROBADAS`

## Estado

**{estado}**

## Hoja1 — columnas detectadas

- CODCLI: `{col_codcli or 'NO_DETECTADO'}`
- RUT/documento: `{col_rut or 'NO_DETECTADO'}`
- Carrera: `{col_carrera or 'NO_DETECTADO'}`
- Año/período: `{col_anio or 'NO_DETECTADO'}`
- Semestre: `{col_sem or 'NO_DETECTADO'}`
- Nivel/curso: `{col_nivel or 'NO_DETECTADO'}`
- Asignatura: `{col_asig or 'NO_DETECTADO'}`
- Unidades/créditos: `{col_unidades or 'NO_DETECTADO'}`
- Estado/aprobación: `{col_estado or col_aprob or 'NO_DETECTADO'}`
- Convalidación: `{col_conval or 'NO_DETECTADO'}`

## Validación

Esta fase no genera archivo de carga ni modifica fuentes.  
Solo produce mapeo y prueba sobre 15 RUT/CODCLI.

## Archivos

- Excel: `{excel}`
- Carpeta: `{SALIDA}`
""",
    encoding="utf-8",
)


manifest = SALIDA / "manifest_mapeo_promedios_7804_prueba_16_19.json"

manifest.write_text(
    json.dumps(
        {
            "fecha": datetime.now().isoformat(),
            "proceso": "Avance Curricular SIES 2026",
            "subproyecto": "Matrícula 5809",
            "anio_referencia": 2025,
            "estado": estado,
            "hojas_mapeadas": xls.sheet_names,
            "hoja_prueba": hoja_prueba,
            "registros_prueba": len(prueba_15_df),
            "csv_carga_generado": False,
            "sies_ready_generado": False,
            "fuentes_originales_modificadas": False,
            "excel": str(excel),
            "informe": str(informe),
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)


print()
print("=" * 120)
print("MAPEO PROMEDIOSDEALUMNOS_7804 — PRUEBA COLUMNAS 16-19")
print("=" * 120)
print(f"Archivo: {FUENTE_PROMEDIOS}")
print(f"Hojas mapeadas: {' | '.join(xls.sheet_names)}")
print(f"Hoja prueba: {hoja_prueba}")
print(f"Estado: {estado}")
print("CSV de carga generado: NO")
print("SIES_READY generado: NO")
print("Fuentes originales modificadas: NO")
print()
print("COLUMNAS DETECTADAS EN HOJA1")
print("-" * 120)
print(f"CODCLI: {col_codcli or 'NO_DETECTADO'}")
print(f"RUT/documento: {col_rut or 'NO_DETECTADO'}")
print(f"Carrera: {col_carrera or 'NO_DETECTADO'}")
print(f"Año/período: {col_anio or 'NO_DETECTADO'}")
print(f"Semestre: {col_sem or 'NO_DETECTADO'}")
print(f"Nivel/curso: {col_nivel or 'NO_DETECTADO'}")
print(f"Asignatura: {col_asig or 'NO_DETECTADO'}")
print(f"Unidades/créditos: {col_unidades or 'NO_DETECTADO'}")
print(f"Estado/aprobación: {col_estado or col_aprob or 'NO_DETECTADO'}")
print(f"Convalidación: {col_conval or 'NO_DETECTADO'}")
print()
print("FACTIBILIDAD")
print("-" * 120)
print(factibilidad_df.to_string(index=False))
print()
print("PRUEBA 15 RUT/CODCLI")
print("-" * 120)
print(prueba_15_df.to_string(index=False))
print()
print("VALIDACIONES")
print("-" * 120)
print(validaciones.to_string(index=False))
print()
print("=" * 120)
print("ARCHIVOS GENERADOS")
print("=" * 120)
print(f"Excel: {excel}")
print(f"Informe: {informe}")
print(f"Carpeta: {SALIDA}")
print("=" * 120)
