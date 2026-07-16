from pathlib import Path
from datetime import datetime
import pandas as pd
import json
import shutil
import hashlib
import re
import unicodedata

RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular")
DESKTOP = Path.home() / "Desktop"
ts = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026/91_diagnostico_columnas_20_21_acumuladas_5809"
    / f"DIAGNOSTICO_COLUMNAS_20_21_ACUMULADAS_5809_{ts}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_H91_DIAGNOSTICO_COLUMNAS_20_21_ACUMULADAS_5809_{ts}"

SALIDA.mkdir(parents=True, exist_ok=True)
ESCRITORIO.mkdir(parents=True, exist_ok=True)

def norm_txt(x):
    x = "" if pd.isna(x) else str(x)
    x = unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode("ascii")
    x = x.upper().strip()
    x = re.sub(r"\s+", " ", x)
    return x

def norm_col(x):
    x = norm_txt(x)
    x = re.sub(r"[^A-Z0-9]+", "_", x)
    return re.sub(r"_+", "_", x).strip("_")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def encontrar_fuente(patterns, obligatorio=True):
    out = []
    for pat in patterns:
        out.extend(RAIZ.glob(pat))
    out = [p for p in out if p.exists() and not p.name.startswith("~$")]
    if not out:
        if obligatorio:
            raise SystemExit(f"BLOQUEO: no se encontró fuente con patrones {patterns}")
        return None
    return sorted(out, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def ultimo(base, prefijo, obligatorio=True):
    if not base.exists():
        if obligatorio:
            raise SystemExit(f"BLOQUEO: no existe carpeta {base}")
        return None
    dirs = sorted(
        [p for p in base.glob(prefijo + "*") if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not dirs:
        if obligatorio:
            raise SystemExit(f"BLOQUEO: no se encontró {prefijo} en {base}")
        return None
    return dirs[0]

def primer_excel(carpeta):
    excels = sorted(
        [p for p in carpeta.glob("*.xlsx") if not p.name.startswith("~$")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not excels:
        raise SystemExit(f"BLOQUEO: no hay Excel en {carpeta}")
    return excels[0]

def leer_csv_auto(path):
    for enc in ["utf-8-sig", "latin1"]:
        for sep in [";", ","]:
            try:
                df = pd.read_csv(path, sep=sep, encoding=enc, dtype=str, keep_default_na=False)
                if len(df.columns) > 1:
                    print(f"   Leyendo CSV {path.name} encoding={enc} sep='{sep}' filas={len(df)} cols={len(df.columns)}")
                    return df, enc, sep
            except Exception:
                pass
    raise SystemExit(f"BLOQUEO: no se pudo leer CSV {path}")

def buscar_hoja(xlsx, patrones):
    xls = pd.ExcelFile(xlsx, engine="openpyxl")
    hojas = {h: norm_col(h) for h in xls.sheet_names}
    for patron in patrones:
        pn = norm_col(patron)
        for h, hn in hojas.items():
            if pn == hn or pn in hn:
                return h
    return None

def leer_excel(xlsx, patrones, obligatorio=True):
    h = buscar_hoja(xlsx, patrones)
    if h is None:
        if obligatorio:
            xls = pd.ExcelFile(xlsx, engine="openpyxl")
            raise SystemExit(f"BLOQUEO: no se encontró hoja {patrones} en {xlsx}. Hojas: {xls.sheet_names}")
        return pd.DataFrame()
    print(f"   Leyendo {xlsx.name} :: {h}")
    return pd.read_excel(xlsx, sheet_name=h, dtype=str, keep_default_na=False, engine="openpyxl")

def col(df, nombres):
    mapa = {norm_col(c): c for c in df.columns}
    for n in nombres:
        nn = norm_col(n)
        if nn in mapa:
            return mapa[nn]
    for n in nombres:
        nn = norm_col(n)
        for k, v in mapa.items():
            if nn in k:
                return v
    return None

def doc_norm(x):
    s = str(x or "").upper().strip()
    s = s.replace(".", "").replace("-", "")
    s = re.sub(r"[^0-9K]", "", s)
    if len(s) > 1 and s[-1] in "0123456789K":
        return s[:-1]
    return s

def to_num(x):
    try:
        s = str(x).replace(",", ".").strip()
        if s == "":
            return None
        return float(s)
    except Exception:
        return None

def imprimir(titulo, df, n=None):
    print()
    print("=" * 170)
    print(titulo)
    print("=" * 170)
    if df.empty:
        print("(sin datos)")
        return
    if n is None:
        print(df.to_string(index=False))
    else:
        print(df.head(n).to_string(index=False))
        if len(df) > n:
            print(f"... mostrando {n} de {len(df)} filas")

print("[1/11] Localizando fuentes base y H90...", flush=True)

PRECARGA_5809 = encontrar_fuente([
    "avance_curricular_2026/00_fuentes_congeladas/**/5809_Precarga Matrícula Avance Curricular 2026.csv",
    "avance_curricular_2026/**/5809_Precarga Matrícula Avance Curricular 2026.csv",
])

PROM = encontrar_fuente([
    "avance_curricular_2026/25_actualizacion_fuente_promedios/**/PROMEDIOSDEALUMNOS_7804_ACTUALIZADO_*.xlsx",
    "avance_curricular_2026/**/PROMEDIOSDEALUMNOS_7804_ACTUALIZADO_*.xlsx",
])

MAPEO = encontrar_fuente([
    "avance_curricular_2026/**/MAPEO_IDENTIDAD_CODCLI.xlsx",
])

INSTRUCTIVO = encontrar_fuente([
    "avance_curricular_2026/00_fuentes_congeladas/**/Instructivo_Avance Curricular SIES - 2026.txt",
    "avance_curricular_2026/**/Instructivo_Avance Curricular SIES - 2026.txt",
], obligatorio=False)

H90 = ultimo(
    RAIZ / "avance_curricular_2026/90_consolidado_final_16_19_post_h89_5809",
    "CONSOLIDADO_FINAL_16_19_POST_H89_5809_",
    obligatorio=False,
)
EX90 = primer_excel(H90) if H90 else None

print(f"   5809: {PRECARGA_5809}")
print(f"   PROMEDIOS: {PROM}")
print(f"   MAPEO: {MAPEO}")
print(f"   INSTRUCTIVO: {INSTRUCTIVO}")
print(f"   H90: {EX90}")

print("[2/11] Leyendo 5809, MAPEO, PROMEDIOS...", flush=True)

df5809, enc5809, sep5809 = leer_csv_auto(PRECARGA_5809)
dfmap = leer_excel(MAPEO, ["MAPEO"])

prom_parts = []
xls = pd.ExcelFile(PROM, engine="openpyxl")
for h in xls.sheet_names:
    tmp = pd.read_excel(PROM, sheet_name=h, dtype=str, keep_default_na=False, engine="openpyxl")
    tmp["_HOJA_PROMEDIOS"] = h
    prom_parts.append(tmp)
prom = pd.concat(prom_parts, ignore_index=True, sort=False)
print(f"   PROMEDIOS consolidado filas={len(prom)} columnas={len(prom.columns)}")

h90_dictamen = leer_excel(EX90, ["00_DICTAMEN_GLOBAL"], obligatorio=False) if EX90 else pd.DataFrame()

print("[3/11] Detectando columnas obligatorias 20-21...", flush=True)

# 5809
c_doc = col(df5809, ["NUM_DOCUMENTO", "RUT"])
c_c20 = col(df5809, ["UNID_CURSADAS_TOTAL"])
c_c21 = col(df5809, ["UNID_APROBADAS_TOTAL"])
c_codunico = col(df5809, ["CODIGO_UNICO"])
c_plan = col(df5809, ["PLAN_ESTUDIOS"])
c_vig = col(df5809, ["VIGENCIA"])

faltan = []
for nombre, c in [
    ("NUM_DOCUMENTO", c_doc),
    ("UNID_CURSADAS_TOTAL", c_c20),
    ("UNID_APROBADAS_TOTAL", c_c21),
]:
    if not c:
        faltan.append(nombre)
if faltan:
    raise SystemExit(f"BLOQUEO: 5809 no tiene columnas requeridas {faltan}")

df5809["_FILA_KEY"] = [str(i + 1) for i in range(len(df5809))]
df5809["_DOC_NORM"] = df5809[c_doc].map(doc_norm)
df5809["_20_ORIG_NUM"] = pd.to_numeric(df5809[c_c20], errors="coerce")
df5809["_21_ORIG_NUM"] = pd.to_numeric(df5809[c_c21], errors="coerce")

# PROMEDIOS
cp_codcli = col(prom, ["CODCLI"])
cp_rut = col(prom, ["RUT"])
cp_ano = col(prom, ["ANO", "ANIO", "AÑO"])
cp_estado = col(prom, ["ESTADO"])
cp_periodo = col(prom, ["PERIODO"])
cp_estado_acad = col(prom, ["ESTADO_ACADEMICO", "ESTADOACADEMICO"])
cp_nivel = col(prom, ["NIVEL"])
cp_ramo = col(prom, ["CODRAMO", "ASIGNATURA", "COD_ASIGNATURA"])
cp_nota = col(prom, ["NOTA_FINAL"])

for nombre, c in [
    ("CODCLI", cp_codcli),
    ("RUT", cp_rut),
    ("ANO", cp_ano),
    ("ESTADO", cp_estado),
]:
    if not c:
        raise SystemExit(f"BLOQUEO: PROMEDIOS no tiene columna {nombre}")

prom["_CODCLI_NORM"] = prom[cp_codcli].astype(str).str.strip()
prom["_DOC_NORM"] = prom[cp_rut].map(doc_norm)
prom["_ANO_NUM"] = pd.to_numeric(prom[cp_ano].astype(str).str.extract(r"(\d{4})", expand=False), errors="coerce")
prom["_ESTADO_NORM"] = prom[cp_estado].map(norm_txt)
prom["_PERIODO_NUM"] = prom[cp_periodo].map(to_num) if cp_periodo else None
prom["_ESTADO_ACAD_NORM"] = prom[cp_estado_acad].map(norm_txt) if cp_estado_acad else ""

# MAPEO
cm_doc = col(dfmap, ["NUM_DOCUMENTO", "RUT", "NUMERO_DOCUMENTO"])
cm_codcli = col(dfmap, ["CODCLI", "CODCLI_LISTA"])
if cm_doc:
    dfmap["_DOC_NORM"] = dfmap[cm_doc].map(doc_norm)
if cm_codcli:
    dfmap["_CODCLI_NORM"] = dfmap[cm_codcli].astype(str).str.strip()

print("[4/11] Buscando respaldo textual en instructivo para acumulado...", flush=True)

extractos = []
if INSTRUCTIVO and INSTRUCTIVO.exists():
    txt = INSTRUCTIVO.read_text(encoding="utf-8", errors="ignore")
    lineas = txt.splitlines()
    patrones = [
        "UNID_CURSADAS_TOTAL",
        "UNID_APROBADAS_TOTAL",
        "acumul",
        "total",
        "aprobadas total",
        "cursadas total",
    ]
    for i, linea in enumerate(lineas, start=1):
        lnorm = norm_txt(linea)
        if any(norm_txt(p) in lnorm for p in patrones):
            desde = max(1, i - 2)
            hasta = min(len(lineas), i + 2)
            extractos.append({
                "LINEA": i,
                "TEXTO": linea,
                "CONTEXTO": "\n".join(lineas[desde-1:hasta]),
            })
extractos_df = pd.DataFrame(extractos[:200])

print("[5/11] Calculando diagnóstico acumulado con escenarios técnicos...", flush=True)

resultados = []
evidencias_muestra = []

for _, r in df5809.iterrows():
    fila = r["_FILA_KEY"]
    doc = r["_DOC_NORM"]

    map_doc = dfmap[dfmap["_DOC_NORM"] == doc] if cm_doc and doc else pd.DataFrame()
    codcli_candidates = set()
    if not map_doc.empty and "_CODCLI_NORM" in map_doc.columns:
        codcli_candidates.update([x for x in map_doc["_CODCLI_NORM"].astype(str) if x.strip()])

    prom_doc = prom[prom["_DOC_NORM"] == doc] if doc else pd.DataFrame()
    if not prom_doc.empty:
        codcli_candidates.update([x for x in prom_doc["_CODCLI_NORM"].astype(str) if x.strip()])

    prom_base = prom[prom["_CODCLI_NORM"].isin(codcli_candidates)] if codcli_candidates else prom_doc
    prom_hasta_2025 = prom_base[prom_base["_ANO_NUM"].notna() & (prom_base["_ANO_NUM"] <= 2025)].copy()
    prom_2025 = prom_base[prom_base["_ANO_NUM"].eq(2025)].copy() if not prom_base.empty else pd.DataFrame()

    # Escenarios técnicos; no son carga.
    cursadas_ar = prom_hasta_2025[prom_hasta_2025["_ESTADO_NORM"].isin(["A", "R"])]
    aprobadas_a = prom_hasta_2025[prom_hasta_2025["_ESTADO_NORM"].eq("A")]

    cursadas_aeir = prom_hasta_2025[prom_hasta_2025["_ESTADO_NORM"].isin(["A", "E", "I", "R"])]
    aprobadas_aei = prom_hasta_2025[prom_hasta_2025["_ESTADO_NORM"].isin(["A", "E", "I"])]

    estados = sorted(set([x for x in prom_hasta_2025["_ESTADO_NORM"].astype(str) if x])) if not prom_hasta_2025.empty else []
    estados_acad = sorted(set([x for x in prom_base["_ESTADO_ACAD_NORM"].astype(str) if x])) if not prom_base.empty else []
    anos = sorted(set([str(int(x)) for x in prom_base["_ANO_NUM"].dropna().tolist()])) if not prom_base.empty else []

    c20_orig = r["_20_ORIG_NUM"]
    c21_orig = r["_21_ORIG_NUM"]

    calc20_ar = len(cursadas_ar)
    calc21_a = len(aprobadas_a)
    calc20_aeir = len(cursadas_aeir)
    calc21_aei = len(aprobadas_aei)

    estado_diag = "NO_EVALUADO"
    if pd.isna(c20_orig) or pd.isna(c21_orig):
        estado_diag = "VALOR_ORIGINAL_NO_NUMERICO"
    elif len(prom_base) == 0:
        estado_diag = "SIN_EVIDENCIA_PROMEDIOS"
    elif len(prom_hasta_2025) == 0:
        estado_diag = "SIN_REGISTROS_HASTA_2025"
    elif int(c20_orig) == calc20_ar and int(c21_orig) == calc21_a:
        estado_diag = "CALZA_ESCENARIO_A_R_Y_A"
    elif int(c20_orig) == calc20_aeir and int(c21_orig) == calc21_aei:
        estado_diag = "CALZA_ESCENARIO_A_E_I_R_Y_A_E_I"
    else:
        estado_diag = "DIFERENCIA_ACUMULADO"

    resultados.append({
        "FILA_KEY": fila,
        "NUM_DOCUMENTO": r[c_doc],
        "DOC_NORM": doc,
        "CODIGO_UNICO": r[c_codunico] if c_codunico else "",
        "PLAN_ESTUDIOS": r[c_plan] if c_plan else "",
        "VIGENCIA": r[c_vig] if c_vig else "",
        "CODCLI_CANDIDATOS": " | ".join(sorted(codcli_candidates)),
        "ANOS_PROMEDIOS": " | ".join(anos),
        "ESTADOS_ACAD_OBSERVADOS": " | ".join(estados_acad),
        "ESTADOS_HASTA_2025": " | ".join(estados),
        "FILAS_PROM_BASE": len(prom_base),
        "FILAS_PROM_HASTA_2025": len(prom_hasta_2025),
        "FILAS_PROM_2025": len(prom_2025),
        "20_ORIGINAL_UNID_CURSADAS_TOTAL": c20_orig,
        "21_ORIGINAL_UNID_APROBADAS_TOTAL": c21_orig,
        "20_ESCENARIO_A_R": calc20_ar,
        "21_ESCENARIO_A": calc21_a,
        "20_ESCENARIO_A_E_I_R": calc20_aeir,
        "21_ESCENARIO_A_E_I": calc21_aei,
        "DIF_20_VS_A_R": None if pd.isna(c20_orig) else int(c20_orig) - calc20_ar,
        "DIF_21_VS_A": None if pd.isna(c21_orig) else int(c21_orig) - calc21_a,
        "DIF_20_VS_A_E_I_R": None if pd.isna(c20_orig) else int(c20_orig) - calc20_aeir,
        "DIF_21_VS_A_E_I": None if pd.isna(c21_orig) else int(c21_orig) - calc21_aei,
        "ESTADO_DIAGNOSTICO_20_21": estado_diag,
        "CORRECCION_APLICADA": "NO",
        "GENERA_CARGA": "NO",
    })

    if estado_diag == "DIFERENCIA_ACUMULADO" and len(evidencias_muestra) < 300:
        tmp = prom_hasta_2025.head(20).copy()
        tmp["_FILA_KEY_5809"] = fila
        evidencias_muestra.append(tmp)

diag = pd.DataFrame(resultados)
evidencia_muestra = pd.concat(evidencias_muestra, ignore_index=True, sort=False) if evidencias_muestra else pd.DataFrame()

print("[6/11] Construyendo resúmenes...", flush=True)

resumen_estado = (
    diag.groupby("ESTADO_DIAGNOSTICO_20_21", dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values("CASOS", ascending=False)
)

resumen_vigencia = (
    diag.groupby(["VIGENCIA", "ESTADO_DIAGNOSTICO_20_21"], dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values(["VIGENCIA", "CASOS"], ascending=[True, False])
)

resumen_integridad = pd.DataFrame([
    {"CONTROL": "Filas 5809", "VALOR": len(df5809)},
    {"CONTROL": "Columnas 5809", "VALOR": len(df5809.columns) - 5},
    {"CONTROL": "Columna 20 detectada", "VALOR": c_c20},
    {"CONTROL": "Columna 21 detectada", "VALOR": c_c21},
    {"CONTROL": "Valores 20 no numéricos", "VALOR": int(df5809["_20_ORIG_NUM"].isna().sum())},
    {"CONTROL": "Valores 21 no numéricos", "VALOR": int(df5809["_21_ORIG_NUM"].isna().sum())},
    {"CONTROL": "Filas sin evidencia PROMEDIOS", "VALOR": int((diag["ESTADO_DIAGNOSTICO_20_21"] == "SIN_EVIDENCIA_PROMEDIOS").sum())},
    {"CONTROL": "Diferencias acumulado", "VALOR": int((diag["ESTADO_DIAGNOSTICO_20_21"] == "DIFERENCIA_ACUMULADO").sum())},
])

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "H91 diagnóstico columnas 20-21 acumuladas archivo 5809",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "ARCHIVO": "5809 Matrícula Avance Curricular",
    "COLUMNAS": "20-21",
    "COLUMNA_20": c_c20,
    "COLUMNA_21": c_c21,
    "FILAS_ANALIZADAS": len(df5809),
    "ESTADO": "DIAGNOSTICO_INICIAL_20_21_GENERADO",
    "FUENTES_ORIGINALES_MODIFICADAS": "NO",
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "SIES_READY_GENERADO": "NO",
    "SUBIDA_SIES_PERMITIDA": "NO",
    "16_19_ESTADO": "CERRADAS_DOCUMENTALMENTE_EN_H90",
    "20_21_ESTADO": "ABIERTO_EN_DIAGNOSTICO",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
    "DICTAMEN_CARGA": "NO_APTO_PARA_CARGA",
}])

control = pd.DataFrame([
    {"CONTROL": "Proceso identificado", "RESULTADO": "OK", "OBSERVADO": "Avance Curricular SIES 2026"},
    {"CONTROL": "Subproyecto identificado", "RESULTADO": "OK", "OBSERVADO": "5809 columnas 20-21"},
    {"CONTROL": "16-19 separado", "RESULTADO": "OK", "OBSERVADO": "H90 cerrado documentalmente"},
    {"CONTROL": "20-21 abierto separado", "RESULTADO": "OK", "OBSERVADO": "H91 diagnóstico"},
    {"CONTROL": "Filas analizadas", "RESULTADO": "OK", "OBSERVADO": len(df5809)},
    {"CONTROL": "Correcciones aplicadas", "RESULTADO": "NO", "OBSERVADO": "NO"},
    {"CONTROL": "Archivo carga generado", "RESULTADO": "NO", "OBSERVADO": "NO"},
    {"CONTROL": "SIES_READY generado", "RESULTADO": "NO", "OBSERVADO": "NO"},
])

print("[7/11] Redactando informe...", flush=True)

informe = f"""# Hito 91 — Diagnóstico columnas 20-21 acumuladas

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular, columnas 20-21.

## Columnas

- 20: {c_c20}
- 21: {c_c21}

## Alcance

Este hito abre el frente acumulado separado de columnas 16-19.

Las columnas 16-19 quedaron cerradas documentalmente en H90.
Las columnas 20-21 se diagnostican en H91 y no se corrigen en este hito.

## Resultado

- Filas analizadas: {len(df5809)}
- Correcciones aplicadas: NO
- Archivo de carga generado: NO
- SIES_READY generado: NO

## Escenarios técnicos calculados

Se calcularon escenarios observados desde PROMEDIOS hasta 2025:

1. Cursadas A/R y aprobadas A.
2. Cursadas A/E/I/R y aprobadas A/E/I.

Estos escenarios son diagnóstico técnico. No constituyen regla oficial por sí mismos.

## Control

No se modifican fuentes originales.
No se genera carga.
No se declara SIES_READY.
"""

print("[8/11] Escribiendo productos H91...", flush=True)

excel_out = SALIDA / "DIAGNOSTICO_COLUMNAS_20_21_ACUMULADAS_5809.xlsx"
informe_out = SALIDA / "INFORME_DIAGNOSTICO_COLUMNAS_20_21_ACUMULADAS_5809.md"
manifest_out = SALIDA / "manifest_diagnostico_columnas_20_21_acumuladas_5809.json"
script_out = SALIDA / "h91_diagnostico_columnas_20_21_acumuladas.py"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    resumen_estado.to_excel(writer, sheet_name="01_RESUMEN_ESTADO", index=False)
    resumen_vigencia.to_excel(writer, sheet_name="02_RESUMEN_VIGENCIA", index=False)
    resumen_integridad.to_excel(writer, sheet_name="03_CONTROLES_INTEGRIDAD", index=False)
    diag.to_excel(writer, sheet_name="04_DIAGNOSTICO_20_21", index=False)
    evidencia_muestra.to_excel(writer, sheet_name="05_MUESTRA_EVIDENCIA", index=False)
    extractos_df.to_excel(writer, sheet_name="06_EXTRACTOS_INSTRUCTIVO", index=False)
    control.to_excel(writer, sheet_name="07_CONTROL", index=False)
    pd.DataFrame([
        {"FUENTE": "5809", "RUTA": str(PRECARGA_5809), "SHA256": sha256(PRECARGA_5809), "ENCODING": enc5809, "SEPARADOR": sep5809},
        {"FUENTE": "PROMEDIOS", "RUTA": str(PROM), "SHA256": sha256(PROM)},
        {"FUENTE": "MAPEO", "RUTA": str(MAPEO), "SHA256": sha256(MAPEO)},
        {"FUENTE": "INSTRUCTIVO", "RUTA": str(INSTRUCTIVO), "SHA256": sha256(INSTRUCTIVO) if INSTRUCTIVO else ""},
        {"FUENTE": "H90", "RUTA": str(H90), "EXCEL": str(EX90), "SHA256": sha256(EX90) if EX90 else ""},
    ]).to_excel(writer, sheet_name="08_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "hito": 91,
        "proceso": "Avance Curricular SIES 2026",
        "subproyecto": "5809 columnas 20-21 acumuladas",
        "filas_analizadas": len(df5809),
        "correcciones_aplicadas": "NO",
        "archivo_carga_generado": "NO",
        "sies_ready_generado": "NO",
        "subida_sies_permitida": "NO",
    }]).to_excel(writer, sheet_name="09_MANIFEST_LEGIBLE", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for column_cells in ws.columns:
            width = max(len(str(cell.value or "")) for cell in column_cells[:1000])
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(width + 2, 12), 120)

informe_out.write_text(informe, encoding="utf-8")

manifest = {
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "H91 diagnóstico columnas 20-21 acumuladas 5809",
    "hito": 91,
    "filas_analizadas": len(df5809),
    "columnas": ["20", "21"],
    "columna_20": c_c20,
    "columna_21": c_c21,
    "fuentes_originales_modificadas": False,
    "correcciones_aplicadas": False,
    "archivo_carga_generado": False,
    "sies_ready_generado": False,
    "subida_sies_permitida": False,
    "excel_salida": str(excel_out),
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h91_diagnostico_columnas_20_21_acumuladas.py"), script_out)

for archivo in [excel_out, informe_out, manifest_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[9/11] Validando productos...", flush=True)

for archivo in [excel_out, informe_out, manifest_out, script_out]:
    if not archivo.exists() or archivo.stat().st_size == 0:
        raise SystemExit(f"BLOQUEO: no se generó correctamente {archivo}")

print("[10/11] Mostrando resultado terminal...", flush=True)

print()
print("=" * 170)
print("HITO 91 — DIAGNÓSTICO COLUMNAS 20-21 ACUMULADAS GENERADO")
print("=" * 170)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 columnas 20-21 acumuladas")
print(f"Filas analizadas: {len(df5809)}")
print(f"Columna 20: {c_c20}")
print(f"Columna 21: {c_c21}")
print("16-19 estado: CERRADAS_DOCUMENTALMENTE_EN_H90")
print("20-21 estado: ABIERTO_EN_DIAGNOSTICO")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("SIES_READY generado: NO")
print("Subida SIES permitida: NO")
print("Declaración carga: NO_LISTO_PARA_CARGA")
print("Dictamen carga: NO_APTO_PARA_CARGA")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("RESUMEN ESTADO 20-21", resumen_estado)
imprimir("CONTROLES INTEGRIDAD", resumen_integridad)
imprimir("CONTROL", control)
imprimir("MUESTRA DIAGNOSTICO 20-21", diag, 30)

print()
print("=" * 170)
print("ARCHIVOS H91")
print("=" * 170)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Manifest: {manifest_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 170)
print("[11/11] Terminado.", flush=True)
