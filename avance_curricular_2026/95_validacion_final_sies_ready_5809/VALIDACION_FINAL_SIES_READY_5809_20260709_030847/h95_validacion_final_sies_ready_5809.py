from pathlib import Path
from datetime import datetime
import pandas as pd
import json
import shutil
import hashlib

RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular")
DESKTOP = Path.home() / "Desktop"
ts = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026/95_validacion_final_sies_ready_5809"
    / f"VALIDACION_FINAL_SIES_READY_5809_{ts}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_H95_VALIDACION_FINAL_SIES_READY_5809_{ts}"

SALIDA.mkdir(parents=True, exist_ok=True)
ESCRITORIO.mkdir(parents=True, exist_ok=True)

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

def imprimir(titulo, df):
    print()
    print("=" * 170)
    print(titulo)
    print("=" * 170)
    if df.empty:
        print("(sin datos)")
    else:
        print(df.to_string(index=False))

print("[1/9] Localizando H94D...", flush=True)

H94D = ultimo(
    RAIZ / "avance_curricular_2026/94d_materializacion_5809_entregable_16_21",
    "MATERIALIZACION_5809_ENTREGABLE_16_21_",
)

csv_h94d = H94D / "5809_MATRICULA_AVANCE_CURRICULAR_2026_ENTREGABLE_CANDIDATO.csv"
xlsx_h94d = H94D / "5809_MATRICULA_AVANCE_CURRICULAR_2026_ENTREGABLE_CANDIDATO.xlsx"
aud_h94d = H94D / "AUDITORIA_5809_ENTREGABLE_CANDIDATO_16_21.xlsx"

for p in [csv_h94d, xlsx_h94d, aud_h94d]:
    if not p.exists():
        raise SystemExit(f"BLOQUEO: no existe archivo requerido: {p}")

print(f"   CSV H94D: {csv_h94d}")
print(f"   Excel H94D: {xlsx_h94d}")
print(f"   Auditoría H94D: {aud_h94d}")

print("[2/9] Leyendo CSV candidato sin encabezado...", flush=True)

df = pd.read_csv(
    csv_h94d,
    sep=";",
    header=None,
    dtype=str,
    keep_default_na=False,
    encoding="utf-8-sig",
)

print(f"   Forma leída: {df.shape}")

if df.shape != (2371, 22):
    raise SystemExit(f"BLOQUEO: CSV esperado 2371x22, observado={df.shape}")

cols = [
    "CODIGO_IES_NUM",
    "TIPO_DOCUMENTO",
    "NUM_DOCUMENTO",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRES",
    "SEXO",
    "FECHA_NACIMIENTO",
    "CODIGO_UNICO",
    "PLAN_ESTUDIOS",
    "ANIO_INGRESO_CARRERA_ACTUAL",
    "SEM_INGRESO_CARRERA_ACTUAL",
    "ANIO_INGRESO_CARRERA_ORIGEN",
    "SEM_INGRESO_CARRERA_ORIGEN",
    "CURSO_1ER_SEM",
    "CURSO_2DO_SEM",
    "UNIDADES_CURSADAS",
    "UNIDADES_APROBADAS",
    "UNID_CURSADAS_TOTAL",
    "UNID_APROBADAS_TOTAL",
    "VIGENCIA",
]

df.columns = cols

print("[3/9] Ejecutando validaciones críticas...", flush=True)

validaciones = []

def add(nombre, resultado, observado, esperado, severidad="CRITICA"):
    validaciones.append({
        "VALIDACION": nombre,
        "RESULTADO": resultado,
        "OBSERVADO": observado,
        "ESPERADO": esperado,
        "SEVERIDAD": severidad,
    })

add("Filas", "OK" if len(df) == 2371 else "ERROR", len(df), 2371)
add("Columnas", "OK" if len(df.columns) == 22 else "ERROR", len(df.columns), 22)
add("CSV sin encabezado confirmado por lectura header=None", "OK", "SI", "SI")
add("Separador punto y coma confirmado", "OK", ";", ";")

for c in ["CURSO_1ER_SEM", "CURSO_2DO_SEM"]:
    vals = sorted(set(df[c].astype(str).str.strip()))
    invalidos = [v for v in vals if v not in ["SI", "NO"]]
    add(f"Valores permitidos {c}", "OK" if not invalidos else "ERROR", " | ".join(invalidos), "SI/NO")

for c in ["UNIDADES_CURSADAS", "UNIDADES_APROBADAS", "UNID_CURSADAS_TOTAL", "UNID_APROBADAS_TOTAL"]:
    nums = pd.to_numeric(df[c], errors="coerce")
    nulos = int(nums.isna().sum())
    negativos = int((nums.fillna(0) < 0).sum())
    decimales = int(((nums.fillna(0) % 1) != 0).sum())
    add(f"Numérico {c}", "OK" if nulos == 0 else "ERROR", nulos, 0)
    add(f"Entero {c}", "OK" if decimales == 0 else "ERROR", decimales, 0)
    add(f"No negativo {c}", "OK" if negativos == 0 else "ERROR", negativos, 0)

n19_gt_18 = int((pd.to_numeric(df["UNIDADES_APROBADAS"]) > pd.to_numeric(df["UNIDADES_CURSADAS"])).sum())
n21_gt_20 = int((pd.to_numeric(df["UNID_APROBADAS_TOTAL"]) > pd.to_numeric(df["UNID_CURSADAS_TOTAL"])).sum())
add("UNIDADES_APROBADAS <= UNIDADES_CURSADAS", "OK" if n19_gt_18 == 0 else "ERROR", n19_gt_18, 0)
add("UNID_APROBADAS_TOTAL <= UNID_CURSADAS_TOTAL", "OK" if n21_gt_20 == 0 else "ERROR", n21_gt_20, 0)

n18_gt0_sin_sem = int(
    (
        (pd.to_numeric(df["UNIDADES_CURSADAS"]) > 0)
        & (df["CURSO_1ER_SEM"].eq("NO"))
        & (df["CURSO_2DO_SEM"].eq("NO"))
    ).sum()
)
add("Si UNIDADES_CURSADAS > 0 entonces algún semestre SI", "OK" if n18_gt0_sin_sem == 0 else "ERROR", n18_gt0_sin_sem, 0)

n18_eq0_con_sem = int(
    (
        (pd.to_numeric(df["UNIDADES_CURSADAS"]) == 0)
        & (
            df["CURSO_1ER_SEM"].eq("SI")
            | df["CURSO_2DO_SEM"].eq("SI")
        )
    ).sum()
)
add("Si UNIDADES_CURSADAS = 0 entonces ambos semestres NO", "OK" if n18_eq0_con_sem == 0 else "ERROR", n18_eq0_con_sem, 0)

for c in cols:
    blancos = int(df[c].astype(str).str.strip().eq("").sum())
    sev = "CRITICA" if c in [
        "CODIGO_IES_NUM",
        "TIPO_DOCUMENTO",
        "NUM_DOCUMENTO",
        "CODIGO_UNICO",
        "PLAN_ESTUDIOS",
        "CURSO_1ER_SEM",
        "CURSO_2DO_SEM",
        "UNIDADES_CURSADAS",
        "UNIDADES_APROBADAS",
        "UNID_CURSADAS_TOTAL",
        "UNID_APROBADAS_TOTAL",
        "VIGENCIA",
    ] else "ADVERTENCIA"
    add(f"Blancos {c}", "OK" if blancos == 0 or sev == "ADVERTENCIA" else "ERROR", blancos, 0, sev)

validaciones_df = pd.DataFrame(validaciones)
errores_criticos = validaciones_df[
    validaciones_df["RESULTADO"].eq("ERROR")
    & validaciones_df["SEVERIDAD"].eq("CRITICA")
].copy()

print("[4/9] Construyendo resúmenes...", flush=True)

resumen = pd.DataFrame([
    {"INDICADOR": "Filas", "VALOR": len(df)},
    {"INDICADOR": "Columnas", "VALOR": len(df.columns)},
    {"INDICADOR": "Errores críticos", "VALOR": len(errores_criticos)},
    {"INDICADOR": "Total UNIDADES_CURSADAS", "VALOR": int(pd.to_numeric(df["UNIDADES_CURSADAS"]).sum())},
    {"INDICADOR": "Total UNIDADES_APROBADAS", "VALOR": int(pd.to_numeric(df["UNIDADES_APROBADAS"]).sum())},
    {"INDICADOR": "Total UNID_CURSADAS_TOTAL", "VALOR": int(pd.to_numeric(df["UNID_CURSADAS_TOTAL"]).sum())},
    {"INDICADOR": "Total UNID_APROBADAS_TOTAL", "VALOR": int(pd.to_numeric(df["UNID_APROBADAS_TOTAL"]).sum())},
])

resumen_16_17 = (
    df.groupby(["CURSO_1ER_SEM", "CURSO_2DO_SEM"], dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values("CASOS", ascending=False)
)

resumen_vigencia = (
    df.groupby(["VIGENCIA"], dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values("VIGENCIA")
)

print("[5/9] Determinando dictamen final...", flush=True)

if len(errores_criticos) == 0:
    estado = "VALIDACION_FINAL_OK"
    sies_ready = "SI"
    subida = "SI_CON_REVISION_USUARIO"
    declaracion = "SIES_READY_GENERADO_CONTROLADO"
    dictamen_carga = "APTO_ESTRUCTURALMENTE_PARA_CARGA"
else:
    estado = "VALIDACION_FINAL_CON_BLOQUEOS"
    sies_ready = "NO"
    subida = "NO"
    declaracion = "NO_LISTO_PARA_CARGA"
    dictamen_carga = "NO_APTO_PARA_CARGA"

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "H95 validación final 5809 SIES_READY",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "ENTRADA_H94D": str(csv_h94d),
    "FILAS": len(df),
    "COLUMNAS": len(df.columns),
    "ESTADO": estado,
    "ERRORES_CRITICOS": len(errores_criticos),
    "FUENTES_ORIGINALES_MODIFICADAS": "NO",
    "SIES_READY_GENERADO": sies_ready,
    "SUBIDA_SIES_PERMITIDA": subida,
    "DECLARACION_CARGA": declaracion,
    "DICTAMEN_CARGA": dictamen_carga,
}])

print("[6/9] Escribiendo archivos H95...", flush=True)

csv_ready = SALIDA / "5809_MATRICULA_AVANCE_CURRICULAR_2026_SIES_READY.csv"
xlsx_ready = SALIDA / "5809_MATRICULA_AVANCE_CURRICULAR_2026_SIES_READY_CON_ENCABEZADO.xlsx"
excel_auditoria = SALIDA / "AUDITORIA_VALIDACION_FINAL_SIES_READY_5809.xlsx"
informe_out = SALIDA / "INFORME_VALIDACION_FINAL_SIES_READY_5809.md"
manifest_out = SALIDA / "manifest_validacion_final_sies_ready_5809.json"
script_out = SALIDA / "h95_validacion_final_sies_ready_5809.py"

if len(errores_criticos) == 0:
    shutil.copy2(csv_h94d, csv_ready)

    with pd.ExcelWriter(xlsx_ready, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="5809_SIES_READY_CON_ENCABEZADO", index=False)
        for ws in writer.book.worksheets:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions

with pd.ExcelWriter(excel_auditoria, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    resumen.to_excel(writer, sheet_name="01_RESUMEN", index=False)
    resumen_16_17.to_excel(writer, sheet_name="02_RESUMEN_16_17", index=False)
    resumen_vigencia.to_excel(writer, sheet_name="03_RESUMEN_VIGENCIA", index=False)
    validaciones_df.to_excel(writer, sheet_name="04_VALIDACIONES", index=False)
    errores_criticos.to_excel(writer, sheet_name="05_ERRORES_CRITICOS", index=False)
    pd.DataFrame([
        {"FUENTE": "CSV_H94D", "RUTA": str(csv_h94d), "SHA256": sha256(csv_h94d)},
        {"FUENTE": "XLSX_H94D", "RUTA": str(xlsx_h94d), "SHA256": sha256(xlsx_h94d)},
        {"FUENTE": "AUDITORIA_H94D", "RUTA": str(aud_h94d), "SHA256": sha256(aud_h94d)},
        {"FUENTE": "CSV_SIES_READY", "RUTA": str(csv_ready) if csv_ready.exists() else "", "SHA256": sha256(csv_ready) if csv_ready.exists() else ""},
        {"FUENTE": "XLSX_SIES_READY", "RUTA": str(xlsx_ready) if xlsx_ready.exists() else "", "SHA256": sha256(xlsx_ready) if xlsx_ready.exists() else ""},
    ]).to_excel(writer, sheet_name="06_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "hito": "H95",
        "proceso": "Avance Curricular SIES 2026",
        "subproyecto": "5809 SIES_READY",
        "errores_criticos": len(errores_criticos),
        "sies_ready_generado": sies_ready,
        "subida_sies_permitida": subida,
    }]).to_excel(writer, sheet_name="07_MANIFEST_LEGIBLE", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for column_cells in ws.columns:
            width = max(len(str(cell.value or "")) for cell in column_cells[:1000])
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(width + 2, 12), 120)

informe = f"""# Hito 95 — Validación final 5809 SIES_READY

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular.

## Resultado

- Estado: {estado}
- Filas: {len(df)}
- Columnas: {len(df.columns)}
- Errores críticos: {len(errores_criticos)}
- SIES_READY generado: {sies_ready}
- Subida SIES permitida: {subida}

## Archivos

- CSV entrada H94D: `{csv_h94d}`
- CSV SIES_READY: `{csv_ready if csv_ready.exists() else "NO_GENERADO"}`
- Excel auditoría: `{excel_auditoria}`

## Control

No se modificaron fuentes originales.
"""
informe_out.write_text(informe, encoding="utf-8")

manifest = {
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "H95 validación final 5809 SIES_READY",
    "entrada_h94d": str(csv_h94d),
    "filas": len(df),
    "columnas": len(df.columns),
    "errores_criticos": len(errores_criticos),
    "estado": estado,
    "sies_ready_generado": sies_ready == "SI",
    "subida_sies_permitida": subida,
    "csv_sies_ready": str(csv_ready) if csv_ready.exists() else None,
    "sha256_csv_sies_ready": sha256(csv_ready) if csv_ready.exists() else None,
    "fuentes_originales_modificadas": False,
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h95_validacion_final_sies_ready_5809.py"), script_out)

for archivo in [excel_auditoria, informe_out, manifest_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

if csv_ready.exists():
    shutil.copy2(csv_ready, ESCRITORIO / csv_ready.name)
if xlsx_ready.exists():
    shutil.copy2(xlsx_ready, ESCRITORIO / xlsx_ready.name)

print("[7/9] Validando salidas...", flush=True)

for archivo in [excel_auditoria, informe_out, manifest_out, script_out]:
    if not archivo.exists() or archivo.stat().st_size == 0:
        raise SystemExit(f"BLOQUEO: no se generó correctamente {archivo}")

if len(errores_criticos) == 0:
    if not csv_ready.exists() or csv_ready.stat().st_size == 0:
        raise SystemExit("BLOQUEO: no se generó CSV SIES_READY.")
    reread = pd.read_csv(csv_ready, sep=";", header=None, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    if reread.shape != (2371, 22):
        raise SystemExit(f"BLOQUEO: SIES_READY esperado 2371x22, observado={reread.shape}")

print("[8/9] Mostrando resultado terminal...", flush=True)

print()
print("=" * 170)
print("HITO 95 — VALIDACIÓN FINAL 5809 SIES_READY GENERADA")
print("=" * 170)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 Matrícula Avance Curricular")
print(f"Estado: {estado}")
print(f"Filas: {len(df)}")
print(f"Columnas: {len(df.columns)}")
print(f"Errores críticos: {len(errores_criticos)}")
print(f"SIES_READY generado: {sies_ready}")
print(f"Subida SIES permitida: {subida}")
print("Fuentes originales modificadas: NO")
print(f"Declaración carga: {declaracion}")
print(f"Dictamen carga: {dictamen_carga}")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("RESUMEN", resumen)
imprimir("RESUMEN 16/17", resumen_16_17)
imprimir("VALIDACIONES", validaciones_df)
imprimir("ERRORES CRITICOS", errores_criticos)

print()
print("=" * 170)
print("ARCHIVOS H95")
print("=" * 170)
print(f"CSV SIES_READY: {csv_ready if csv_ready.exists() else 'NO_GENERADO'}")
print(f"Excel SIES_READY: {xlsx_ready if xlsx_ready.exists() else 'NO_GENERADO'}")
print(f"Auditoría: {excel_auditoria}")
print(f"Informe: {informe_out}")
print(f"Manifest: {manifest_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 170)
print("[9/9] Terminado.", flush=True)
