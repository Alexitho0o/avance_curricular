from pathlib import Path
from datetime import datetime
import pandas as pd
import shutil
import hashlib
import json

RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular")
DESKTOP = Path.home() / "Desktop"
ts = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026/96_sies_ready_21_campos_5809"
    / f"SIES_READY_21_CAMPOS_5809_{ts}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_H96_SIES_READY_21_CAMPOS_5809_{ts}"

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
    print("=" * 150)
    print(titulo)
    print("=" * 150)
    if df.empty:
        print("(sin datos)")
    else:
        print(df.to_string(index=False))

print("[1/8] Localizando H95 SIES_READY 22 campos...", flush=True)

H95 = ultimo(
    RAIZ / "avance_curricular_2026/95_validacion_final_sies_ready_5809",
    "VALIDACION_FINAL_SIES_READY_5809_",
)

csv_h95 = H95 / "5809_MATRICULA_AVANCE_CURRICULAR_2026_SIES_READY.csv"

if not csv_h95.exists():
    raise SystemExit(f"BLOQUEO: no existe CSV H95: {csv_h95}")

print(f"   Entrada H95: {csv_h95}")

cols_22 = [
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

cols_21 = [
    "CODIGO_IES_NUM",
    "TIPO_DOCUMENTO",
    "NUM_DOCUMENTO",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRES",
    "SEXO",
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

print("[2/8] Leyendo CSV H95...", flush=True)

df22 = pd.read_csv(
    csv_h95,
    sep=";",
    header=None,
    names=cols_22,
    dtype=str,
    keep_default_na=False,
    encoding="utf-8-sig",
)

if df22.shape != (2371, 22):
    raise SystemExit(f"BLOQUEO: H95 esperado 2371x22, observado={df22.shape}")

print("[3/8] Generando estructura 21 campos, eliminando FECHA_NACIMIENTO...", flush=True)

df21 = df22[cols_21].copy()

if df21.shape != (2371, 21):
    raise SystemExit(f"BLOQUEO: salida esperada 2371x21, observado={df21.shape}")

print("[4/8] Validando estructura de 21 campos...", flush=True)

validaciones = []

def add(nombre, resultado, observado, esperado):
    validaciones.append({
        "VALIDACION": nombre,
        "RESULTADO": resultado,
        "OBSERVADO": observado,
        "ESPERADO": esperado,
    })

add("Filas", "OK" if len(df21) == 2371 else "ERROR", len(df21), 2371)
add("Columnas", "OK" if len(df21.columns) == 21 else "ERROR", len(df21.columns), 21)
add("FECHA_NACIMIENTO excluida", "OK" if "FECHA_NACIMIENTO" not in df21.columns else "ERROR", "NO_INCLUIDA", "NO_INCLUIDA")
add("Primera columna CODIGO_IES_NUM", "OK" if df21.columns[0] == "CODIGO_IES_NUM" else "ERROR", df21.columns[0], "CODIGO_IES_NUM")
add("Última columna VIGENCIA", "OK" if df21.columns[-1] == "VIGENCIA" else "ERROR", df21.columns[-1], "VIGENCIA")

for c in ["CURSO_1ER_SEM", "CURSO_2DO_SEM"]:
    vals = sorted(set(df21[c].astype(str).str.strip()))
    invalidos = [v for v in vals if v not in ["SI", "NO"]]
    add(f"Valores permitidos {c}", "OK" if not invalidos else "ERROR", " | ".join(invalidos), "SI/NO")

for c in ["UNIDADES_CURSADAS", "UNIDADES_APROBADAS", "UNID_CURSADAS_TOTAL", "UNID_APROBADAS_TOTAL"]:
    nums = pd.to_numeric(df21[c], errors="coerce")
    nulos = int(nums.isna().sum())
    negativos = int((nums.fillna(0) < 0).sum())
    add(f"Numérico {c}", "OK" if nulos == 0 else "ERROR", nulos, 0)
    add(f"No negativo {c}", "OK" if negativos == 0 else "ERROR", negativos, 0)

n19_gt_18 = int((pd.to_numeric(df21["UNIDADES_APROBADAS"]) > pd.to_numeric(df21["UNIDADES_CURSADAS"])).sum())
n21_gt_20 = int((pd.to_numeric(df21["UNID_APROBADAS_TOTAL"]) > pd.to_numeric(df21["UNID_CURSADAS_TOTAL"])).sum())

add("UNIDADES_APROBADAS <= UNIDADES_CURSADAS", "OK" if n19_gt_18 == 0 else "ERROR", n19_gt_18, 0)
add("UNID_APROBADAS_TOTAL <= UNID_CURSADAS_TOTAL", "OK" if n21_gt_20 == 0 else "ERROR", n21_gt_20, 0)

validaciones_df = pd.DataFrame(validaciones)
errores = validaciones_df[validaciones_df["RESULTADO"].eq("ERROR")]

if len(errores) > 0:
    imprimir("ERRORES", errores)
    raise SystemExit("BLOQUEO: validaciones H96 fallaron.")

print("[5/8] Construyendo resúmenes...", flush=True)

resumen = pd.DataFrame([
    {"INDICADOR": "Filas", "VALOR": len(df21)},
    {"INDICADOR": "Columnas", "VALOR": len(df21.columns)},
    {"INDICADOR": "Campo eliminado", "VALOR": "FECHA_NACIMIENTO"},
    {"INDICADOR": "Total UNIDADES_CURSADAS", "VALOR": int(pd.to_numeric(df21["UNIDADES_CURSADAS"]).sum())},
    {"INDICADOR": "Total UNIDADES_APROBADAS", "VALOR": int(pd.to_numeric(df21["UNIDADES_APROBADAS"]).sum())},
    {"INDICADOR": "Total UNID_CURSADAS_TOTAL", "VALOR": int(pd.to_numeric(df21["UNID_CURSADAS_TOTAL"]).sum())},
    {"INDICADOR": "Total UNID_APROBADAS_TOTAL", "VALOR": int(pd.to_numeric(df21["UNID_APROBADAS_TOTAL"]).sum())},
])

resumen_16_17 = (
    df21.groupby(["CURSO_1ER_SEM", "CURSO_2DO_SEM"], dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values("CASOS", ascending=False)
)

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "H96 ajuste estructura 21 campos 5809 matrícula",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "ID_CARGA": 16768,
    "NOMBRE_CARGA": "Matrícula Avance Curricular 2026",
    "ENTRADA_H95_22_CAMPOS": str(csv_h95),
    "SALIDA_H96_21_CAMPOS": "GENERADA",
    "CAMPO_EXCLUIDO": "FECHA_NACIMIENTO",
    "FILAS": len(df21),
    "COLUMNAS": len(df21.columns),
    "VALIDACION": "OK",
    "FUENTES_ORIGINALES_MODIFICADAS": "NO",
    "DICTAMEN": "APTO_ESTRUCTURALMENTE_SEGUN_ERROR_PLATAFORMA_21_CAMPOS",
}])

print("[6/8] Escribiendo archivos H96...", flush=True)

csv_h96 = SALIDA / "5809_MATRICULA_AVANCE_CURRICULAR_2026_SIES_READY_21_CAMPOS.csv"
xlsx_h96 = SALIDA / "5809_MATRICULA_AVANCE_CURRICULAR_2026_SIES_READY_21_CAMPOS_CON_ENCABEZADO.xlsx"
auditoria = SALIDA / "AUDITORIA_H96_SIES_READY_21_CAMPOS_5809.xlsx"
informe = SALIDA / "INFORME_H96_SIES_READY_21_CAMPOS_5809.md"
manifest = SALIDA / "manifest_h96_sies_ready_21_campos_5809.json"
script_out = SALIDA / "h96_sies_ready_21_campos_5809.py"

# CSV de carga: sin encabezado, separador punto y coma, encoding latin1 para mantener consistencia con precarga original.
df21.to_csv(csv_h96, sep=";", index=False, header=False, encoding="latin1")

with pd.ExcelWriter(xlsx_h96, engine="openpyxl") as writer:
    df21.to_excel(writer, sheet_name="5809_21_CAMPOS", index=False)
    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

with pd.ExcelWriter(auditoria, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    resumen.to_excel(writer, sheet_name="01_RESUMEN", index=False)
    resumen_16_17.to_excel(writer, sheet_name="02_RESUMEN_16_17", index=False)
    validaciones_df.to_excel(writer, sheet_name="03_VALIDACIONES", index=False)
    pd.DataFrame({"COLUMNAS_21_CAMPOS": cols_21}).to_excel(writer, sheet_name="04_ESTRUCTURA_21", index=False)
    pd.DataFrame({"COLUMNAS_H95_22_CAMPOS": cols_22}).to_excel(writer, sheet_name="05_ESTRUCTURA_ORIGEN_22", index=False)
    pd.DataFrame([
        {"FUENTE": "CSV_H95_22_CAMPOS", "RUTA": str(csv_h95), "SHA256": sha256(csv_h95)},
        {"FUENTE": "CSV_H96_21_CAMPOS", "RUTA": str(csv_h96), "SHA256": sha256(csv_h96)},
        {"FUENTE": "XLSX_H96_21_CAMPOS", "RUTA": str(xlsx_h96), "SHA256": sha256(xlsx_h96)},
    ]).to_excel(writer, sheet_name="06_FUENTES", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for column_cells in ws.columns:
            width = max(len(str(cell.value or "")) for cell in column_cells[:1000])
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(width + 2, 12), 120)

informe.write_text(
f"""# H96 — SIES_READY 21 campos 5809

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Matrícula Avance Curricular 2026, ID Carga 16768.

## Motivo

La plataforma rechazó el archivo anterior porque contenía 22 campos y la estructura esperada reportada por la plataforma es de 21 campos.

## Corrección aplicada

Se excluyó `FECHA_NACIMIENTO` y se mantuvieron los demás campos, incluyendo `VIGENCIA` como último campo.

## Resultado

- Filas: {len(df21)}
- Columnas: {len(df21.columns)}
- CSV sin encabezado: SI
- Separador: punto y coma
- Encoding: latin1
- Fuentes originales modificadas: NO

## Archivo a subir

`{csv_h96}`
""",
encoding="utf-8"
)

manifest.write_text(json.dumps({
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "H96 SIES_READY 21 campos 5809",
    "id_carga": 16768,
    "entrada_h95": str(csv_h95),
    "csv_h96": str(csv_h96),
    "xlsx_h96": str(xlsx_h96),
    "auditoria": str(auditoria),
    "filas": len(df21),
    "columnas": len(df21.columns),
    "campo_excluido": "FECHA_NACIMIENTO",
    "sha256_csv_h96": sha256(csv_h96),
    "fuentes_originales_modificadas": False,
}, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h96_sies_ready_21_campos_5809.py"), script_out)

for p in [csv_h96, xlsx_h96, auditoria, informe, manifest, script_out]:
    shutil.copy2(p, ESCRITORIO / p.name)

print("[7/8] Releyendo CSV H96...", flush=True)

reread = pd.read_csv(csv_h96, sep=";", header=None, dtype=str, keep_default_na=False, encoding="latin1")

if reread.shape != (2371, 21):
    raise SystemExit(f"BLOQUEO: CSV H96 esperado 2371x21, observado={reread.shape}")

print("[8/8] Resultado final H96", flush=True)

print()
print("=" * 150)
print("H96 — SIES_READY 21 CAMPOS 5809 GENERADO")
print("=" * 150)
print("Proceso: Avance Curricular SIES 2026")
print("ID Carga: 16768")
print("Nombre carga: Matrícula Avance Curricular 2026")
print("Filas: 2371")
print("Columnas: 21")
print("Campo excluido: FECHA_NACIMIENTO")
print("CSV: sin encabezado, separador punto y coma, encoding latin1")
print("Fuentes originales modificadas: NO")
print("Dictamen: APTO_ESTRUCTURALMENTE_SEGUN_ERROR_PLATAFORMA_21_CAMPOS")
print()
print(f"CSV a subir: {csv_h96}")
print(f"Excel revisión: {xlsx_h96}")
print(f"Auditoría: {auditoria}")
print(f"Carpeta escritorio: {ESCRITORIO}")

imprimir("DICTAMEN", dictamen)
imprimir("RESUMEN", resumen)
imprimir("VALIDACIONES", validaciones_df)
