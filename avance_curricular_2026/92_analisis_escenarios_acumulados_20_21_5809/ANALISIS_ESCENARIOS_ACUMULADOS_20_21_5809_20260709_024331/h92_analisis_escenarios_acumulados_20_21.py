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
    / "avance_curricular_2026/92_analisis_escenarios_acumulados_20_21_5809"
    / f"ANALISIS_ESCENARIOS_ACUMULADOS_20_21_5809_{ts}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_H92_ANALISIS_ESCENARIOS_ACUMULADOS_20_21_5809_{ts}"

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

def ultimo(base, prefijo):
    dirs = sorted(
        [p for p in base.glob(prefijo + "*") if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not dirs:
        raise SystemExit(f"BLOQUEO: no se encontró {prefijo} en {base}")
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

def buscar_hoja(xlsx, patrones):
    xls = pd.ExcelFile(xlsx, engine="openpyxl")
    hojas = {h: norm_col(h) for h in xls.sheet_names}
    for patron in patrones:
        pn = norm_col(patron)
        for h, hn in hojas.items():
            if pn == hn or pn in hn:
                return h
    return None

def leer_excel(xlsx, patrones):
    h = buscar_hoja(xlsx, patrones)
    if h is None:
        xls = pd.ExcelFile(xlsx, engine="openpyxl")
        raise SystemExit(f"BLOQUEO: no se encontró hoja {patrones} en {xlsx}. Hojas: {xls.sheet_names}")
    print(f"   Leyendo {xlsx.name} :: {h}", flush=True)
    return pd.read_excel(xlsx, sheet_name=h, dtype=str, keep_default_na=False, engine="openpyxl")

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

print("[1/10] Localizando H91...", flush=True)

H91 = ultimo(
    RAIZ / "avance_curricular_2026/91_diagnostico_columnas_20_21_acumuladas_5809",
    "DIAGNOSTICO_COLUMNAS_20_21_ACUMULADAS_5809_",
)
EX91 = primer_excel(H91)

print(f"   H91: {EX91}")

print("[2/10] Leyendo diagnóstico H91...", flush=True)

h91_dictamen = leer_excel(EX91, ["00_DICTAMEN_GLOBAL"])
h91_resumen_estado = leer_excel(EX91, ["01_RESUMEN_ESTADO"])
h91_integridad = leer_excel(EX91, ["03_CONTROLES_INTEGRIDAD"])
diag = leer_excel(EX91, ["04_DIAGNOSTICO_20_21"])
extractos = leer_excel(EX91, ["06_EXTRACTOS_INSTRUCTIVO"])
control_h91 = leer_excel(EX91, ["07_CONTROL"])

if len(diag) != 2371:
    raise SystemExit(f"BLOQUEO: se esperaban 2371 filas en diagnóstico H91, observado={len(diag)}")

print("[3/10] Normalizando columnas numéricas de escenarios...", flush=True)

cols_num = [
    "FILAS_PROM_BASE",
    "FILAS_PROM_HASTA_2025",
    "FILAS_PROM_2025",
    "20_ESCENARIO_A_R",
    "21_ESCENARIO_A",
    "20_ESCENARIO_A_E_I_R",
    "21_ESCENARIO_A_E_I",
]

for c in cols_num:
    if c not in diag.columns:
        raise SystemExit(f"BLOQUEO: falta columna {c} en H91.")
    diag[c] = pd.to_numeric(diag[c], errors="coerce").fillna(0).astype(int)

print("[4/10] Calculando impacto entre escenarios...", flush=True)

diag["DIF_20_EI_EN_CURSADAS"] = diag["20_ESCENARIO_A_E_I_R"] - diag["20_ESCENARIO_A_R"]
diag["DIF_21_EI_EN_APROBADAS"] = diag["21_ESCENARIO_A_E_I"] - diag["21_ESCENARIO_A"]

diag["TIENE_EI_IMPACTO_20"] = diag["DIF_20_EI_EN_CURSADAS"].gt(0).map({True: "SI", False: "NO"})
diag["TIENE_EI_IMPACTO_21"] = diag["DIF_21_EI_EN_APROBADAS"].gt(0).map({True: "SI", False: "NO"})
diag["TIENE_EI_IMPACTO_TOTAL"] = (
    diag["DIF_20_EI_EN_CURSADAS"].gt(0) | diag["DIF_21_EI_EN_APROBADAS"].gt(0)
).map({True: "SI", False: "NO"})

diag["ESCENARIO_A_R_A_20_21"] = (
    diag["20_ESCENARIO_A_R"].astype(str) + " / " + diag["21_ESCENARIO_A"].astype(str)
)
diag["ESCENARIO_AEIR_AEI_20_21"] = (
    diag["20_ESCENARIO_A_E_I_R"].astype(str) + " / " + diag["21_ESCENARIO_A_E_I"].astype(str)
)

def clasificar(row):
    if row["FILAS_PROM_HASTA_2025"] == 0:
        return "SIN_REGISTROS_HASTA_2025"
    if row["TIENE_EI_IMPACTO_TOTAL"] == "NO":
        return "SIN_IMPACTO_EI_AMBOS_ESCENARIOS_IGUALES"
    if row["DIF_20_EI_EN_CURSADAS"] > 0 and row["DIF_21_EI_EN_APROBADAS"] > 0:
        return "IMPACTO_EI_EN_20_Y_21"
    if row["DIF_20_EI_EN_CURSADAS"] > 0:
        return "IMPACTO_EI_SOLO_EN_20"
    if row["DIF_21_EI_EN_APROBADAS"] > 0:
        return "IMPACTO_EI_SOLO_EN_21"
    return "REVISION"

diag["CLASIFICACION_IMPACTO_ESCENARIOS"] = diag.apply(clasificar, axis=1)

print("[5/10] Construyendo resúmenes de impacto...", flush=True)

resumen_impacto = (
    diag.groupby("CLASIFICACION_IMPACTO_ESCENARIOS", dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values("CASOS", ascending=False)
)

resumen_ei = pd.DataFrame([
    {
        "INDICADOR": "Total filas analizadas",
        "VALOR": len(diag),
    },
    {
        "INDICADOR": "Filas con impacto E/I en 20 o 21",
        "VALOR": int((diag["TIENE_EI_IMPACTO_TOTAL"] == "SI").sum()),
    },
    {
        "INDICADOR": "Filas sin impacto E/I",
        "VALOR": int((diag["TIENE_EI_IMPACTO_TOTAL"] == "NO").sum()),
    },
    {
        "INDICADOR": "Diferencia total 20 por incluir E/I",
        "VALOR": int(diag["DIF_20_EI_EN_CURSADAS"].sum()),
    },
    {
        "INDICADOR": "Diferencia total 21 por incluir E/I",
        "VALOR": int(diag["DIF_21_EI_EN_APROBADAS"].sum()),
    },
    {
        "INDICADOR": "Total 20 escenario A/R",
        "VALOR": int(diag["20_ESCENARIO_A_R"].sum()),
    },
    {
        "INDICADOR": "Total 21 escenario A",
        "VALOR": int(diag["21_ESCENARIO_A"].sum()),
    },
    {
        "INDICADOR": "Total 20 escenario A/E/I/R",
        "VALOR": int(diag["20_ESCENARIO_A_E_I_R"].sum()),
    },
    {
        "INDICADOR": "Total 21 escenario A/E/I",
        "VALOR": int(diag["21_ESCENARIO_A_E_I"].sum()),
    },
])

resumen_por_vigencia = (
    diag.groupby(["VIGENCIA", "CLASIFICACION_IMPACTO_ESCENARIOS"], dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values(["VIGENCIA", "CASOS"], ascending=[True, False])
)

muestra_impacto = diag[diag["TIENE_EI_IMPACTO_TOTAL"].eq("SI")].copy()
muestra_sin_impacto = diag[diag["TIENE_EI_IMPACTO_TOTAL"].eq("NO")].copy()

print("[6/10] Proponiendo criterio candidato sin aplicar corrección...", flush=True)

criterio_candidato = pd.DataFrame([
    {
        "ESCENARIO": "ESCENARIO_1_A_R_Y_A",
        "COLUMNA_20": "A/R hasta 2025",
        "COLUMNA_21": "A hasta 2025",
        "VENTAJA": "Conserva lógica anual usada en 16-19 para aprobadas solo A.",
        "RIESGO": "Podría excluir convalidaciones/homologaciones acumuladas si el instructivo las permite en total acumulado.",
        "DICTAMEN": "CANDIDATO_CONSERVADOR",
        "NIVEL_RESPALDO": "B_DATO_OBSERVADO_D_DECISION_PENDIENTE",
    },
    {
        "ESCENARIO": "ESCENARIO_2_A_E_I_R_Y_A_E_I",
        "COLUMNA_20": "A/E/I/R hasta 2025",
        "COLUMNA_21": "A/E/I hasta 2025",
        "VENTAJA": "Reconoce E/I en trayectoria acumulada.",
        "RIESGO": "No debe aplicarse si el instructivo no respalda incluir E/I en acumulado.",
        "DICTAMEN": "CANDIDATO_AMPLIADO_REQUIERE_VALIDACION_FUNCIONAL",
        "NIVEL_RESPALDO": "B_DATO_OBSERVADO_D_DECISION_PENDIENTE",
    },
])

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "H92 análisis escenarios acumulados 20-21 archivo 5809",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "FILAS_ANALIZADAS": len(diag),
    "ESCENARIOS_COMPARADOS": "A/R-A versus A/E/I/R-A/E/I",
    "FILAS_CON_IMPACTO_EI": int((diag["TIENE_EI_IMPACTO_TOTAL"] == "SI").sum()),
    "FILAS_SIN_IMPACTO_EI": int((diag["TIENE_EI_IMPACTO_TOTAL"] == "NO").sum()),
    "DIF_TOTAL_20_POR_EI": int(diag["DIF_20_EI_EN_CURSADAS"].sum()),
    "DIF_TOTAL_21_POR_EI": int(diag["DIF_21_EI_EN_APROBADAS"].sum()),
    "CRITERIO_DEFINITIVO_APLICADO": "NO",
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "SIES_READY_GENERADO": "NO",
    "SUBIDA_SIES_PERMITIDA": "NO",
    "16_19_ESTADO": "CERRADAS_DOCUMENTALMENTE_EN_H90",
    "20_21_ESTADO": "ESCENARIOS_ANALIZADOS_PENDIENTE_DECISION",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
    "DICTAMEN_CARGA": "NO_APTO_PARA_CARGA",
}])

control = pd.DataFrame([
    {"CONTROL": "Filas H91 leídas", "RESULTADO": "OK", "OBSERVADO": len(diag), "ESPERADO": 2371},
    {"CONTROL": "Escenario A/R-A calculado", "RESULTADO": "OK", "OBSERVADO": "SI", "ESPERADO": "SI"},
    {"CONTROL": "Escenario A/E/I/R-A/E/I calculado", "RESULTADO": "OK", "OBSERVADO": "SI", "ESPERADO": "SI"},
    {"CONTROL": "Criterio definitivo aplicado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "Correcciones aplicadas", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "Archivo carga generado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "SIES_READY generado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
])

print("[7/10] Redactando informe H92...", flush=True)

informe = f"""# Hito 92 — Análisis de escenarios acumulados 20-21

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular, columnas 20-21 acumuladas.

## Objetivo

Comparar escenarios técnicos para las columnas acumuladas 20-21, sin aplicar corrección ni generar carga.

## Escenarios comparados

### Escenario 1: A/R y A

- Columna 20: registros acumulados hasta 2025 con estado A o R.
- Columna 21: registros acumulados hasta 2025 con estado A.

### Escenario 2: A/E/I/R y A/E/I

- Columna 20: registros acumulados hasta 2025 con estado A, E, I o R.
- Columna 21: registros acumulados hasta 2025 con estado A, E o I.

## Resultado de impacto

- Filas analizadas: {len(diag)}
- Filas con impacto por incluir E/I: {int((diag["TIENE_EI_IMPACTO_TOTAL"] == "SI").sum())}
- Filas sin impacto por E/I: {int((diag["TIENE_EI_IMPACTO_TOTAL"] == "NO").sum())}
- Diferencia total columna 20 por incluir E/I: {int(diag["DIF_20_EI_EN_CURSADAS"].sum())}
- Diferencia total columna 21 por incluir E/I: {int(diag["DIF_21_EI_EN_APROBADAS"].sum())}

## Control

No se define criterio definitivo en este hito.
No se modifican fuentes originales.
No se genera archivo de carga.
No se genera SIES_READY.

## Pendiente

Definir si acumulado 20-21 debe usar el criterio conservador A/R-A o el criterio ampliado A/E/I/R-A/E/I.
"""

print("[8/10] Escribiendo productos H92...", flush=True)

excel_out = SALIDA / "ANALISIS_ESCENARIOS_ACUMULADOS_20_21_5809.xlsx"
informe_out = SALIDA / "INFORME_ANALISIS_ESCENARIOS_ACUMULADOS_20_21_5809.md"
manifest_out = SALIDA / "manifest_analisis_escenarios_acumulados_20_21_5809.json"
script_out = SALIDA / "h92_analisis_escenarios_acumulados_20_21.py"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    resumen_ei.to_excel(writer, sheet_name="01_RESUMEN_IMPACTO_EI", index=False)
    resumen_impacto.to_excel(writer, sheet_name="02_RESUMEN_CLASIFICACION", index=False)
    resumen_por_vigencia.to_excel(writer, sheet_name="03_RESUMEN_VIGENCIA", index=False)
    criterio_candidato.to_excel(writer, sheet_name="04_CRITERIOS_CANDIDATOS", index=False)
    diag.to_excel(writer, sheet_name="05_ANALISIS_ESCENARIOS", index=False)
    muestra_impacto.head(500).to_excel(writer, sheet_name="06_MUESTRA_CON_IMPACTO_EI", index=False)
    muestra_sin_impacto.head(500).to_excel(writer, sheet_name="07_MUESTRA_SIN_IMPACTO_EI", index=False)
    extractos.to_excel(writer, sheet_name="08_EXTRACTOS_INSTRUCTIVO", index=False)
    control.to_excel(writer, sheet_name="09_CONTROL", index=False)
    pd.DataFrame([
        {"FUENTE": "H91", "RUTA": str(H91), "EXCEL": str(EX91), "SHA256": sha256(EX91)},
    ]).to_excel(writer, sheet_name="10_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "hito": 92,
        "proceso": "Avance Curricular SIES 2026",
        "subproyecto": "5809 columnas 20-21 acumuladas",
        "filas_analizadas": len(diag),
        "filas_con_impacto_ei": int((diag["TIENE_EI_IMPACTO_TOTAL"] == "SI").sum()),
        "filas_sin_impacto_ei": int((diag["TIENE_EI_IMPACTO_TOTAL"] == "NO").sum()),
        "dif_total_20_por_ei": int(diag["DIF_20_EI_EN_CURSADAS"].sum()),
        "dif_total_21_por_ei": int(diag["DIF_21_EI_EN_APROBADAS"].sum()),
        "criterio_definitivo_aplicado": "NO",
        "correcciones_aplicadas": "NO",
        "archivo_carga_generado": "NO",
        "sies_ready_generado": "NO",
    }]).to_excel(writer, sheet_name="11_MANIFEST_LEGIBLE", index=False)

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
    "subproyecto": "H92 análisis escenarios acumulados 20-21 5809",
    "hito": 92,
    "filas_analizadas": len(diag),
    "filas_con_impacto_ei": int((diag["TIENE_EI_IMPACTO_TOTAL"] == "SI").sum()),
    "filas_sin_impacto_ei": int((diag["TIENE_EI_IMPACTO_TOTAL"] == "NO").sum()),
    "dif_total_20_por_ei": int(diag["DIF_20_EI_EN_CURSADAS"].sum()),
    "dif_total_21_por_ei": int(diag["DIF_21_EI_EN_APROBADAS"].sum()),
    "criterio_definitivo_aplicado": False,
    "correcciones_aplicadas": False,
    "archivo_carga_generado": False,
    "sies_ready_generado": False,
    "subida_sies_permitida": False,
    "excel_salida": str(excel_out),
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h92_analisis_escenarios_acumulados_20_21.py"), script_out)

for archivo in [excel_out, informe_out, manifest_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[9/10] Validando productos y mostrando resultado...", flush=True)

for archivo in [excel_out, informe_out, manifest_out, script_out]:
    if not archivo.exists() or archivo.stat().st_size == 0:
        raise SystemExit(f"BLOQUEO: no se generó correctamente {archivo}")

print()
print("=" * 170)
print("HITO 92 — ANÁLISIS ESCENARIOS ACUMULADOS 20-21 GENERADO")
print("=" * 170)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 columnas 20-21 acumuladas")
print(f"Filas analizadas: {len(diag)}")
print("Escenarios comparados: A/R-A versus A/E/I/R-A/E/I")
print(f"Filas con impacto E/I: {int((diag['TIENE_EI_IMPACTO_TOTAL'] == 'SI').sum())}")
print(f"Filas sin impacto E/I: {int((diag['TIENE_EI_IMPACTO_TOTAL'] == 'NO').sum())}")
print(f"Diferencia total 20 por E/I: {int(diag['DIF_20_EI_EN_CURSADAS'].sum())}")
print(f"Diferencia total 21 por E/I: {int(diag['DIF_21_EI_EN_APROBADAS'].sum())}")
print("Criterio definitivo aplicado: NO")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("SIES_READY generado: NO")
print("Subida SIES permitida: NO")
print("Declaración carga: NO_LISTO_PARA_CARGA")
print("Dictamen carga: NO_APTO_PARA_CARGA")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("RESUMEN IMPACTO E/I", resumen_ei)
imprimir("RESUMEN CLASIFICACION", resumen_impacto)
imprimir("CRITERIOS CANDIDATOS", criterio_candidato)
imprimir("CONTROL", control)
imprimir("MUESTRA CON IMPACTO E/I", muestra_impacto, 30)

print()
print("=" * 170)
print("ARCHIVOS H92")
print("=" * 170)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Manifest: {manifest_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 170)
print("[10/10] Terminado.", flush=True)
