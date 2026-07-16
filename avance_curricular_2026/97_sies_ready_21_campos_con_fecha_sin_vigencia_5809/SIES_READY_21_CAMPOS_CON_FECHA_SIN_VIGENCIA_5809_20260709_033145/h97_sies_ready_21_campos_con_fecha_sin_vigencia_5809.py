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
    / "avance_curricular_2026/97_sies_ready_21_campos_con_fecha_sin_vigencia_5809"
    / f"SIES_READY_21_CAMPOS_CON_FECHA_SIN_VIGENCIA_5809_{ts}"
)

SALIDA.mkdir(parents=True, exist_ok=True)

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

print("[1/9] Localizando H95 SIES_READY 22 campos...", flush=True)

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
]

print("[2/9] Leyendo CSV H95 22 campos...", flush=True)

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

print("[3/9] Generando estructura 21 campos con FECHA_NACIMIENTO y sin VIGENCIA...", flush=True)

df21 = df22[cols_21].copy()

fecha_original = df21["FECHA_NACIMIENTO"].copy()
fecha = pd.to_datetime(df21["FECHA_NACIMIENTO"], errors="coerce")
fallas_fecha = int(fecha.isna().sum())

if fallas_fecha > 0:
    muestra = df21.loc[fecha.isna(), ["NUM_DOCUMENTO", "FECHA_NACIMIENTO"]].head(30)
    imprimir("BLOQUEO FECHAS NO PARSEABLES", muestra)
    raise SystemExit(f"BLOQUEO: {fallas_fecha} fechas no se pudieron normalizar.")

df21["FECHA_NACIMIENTO"] = fecha.dt.strftime("%Y-%m-%d")

control_fecha = pd.DataFrame({
    "NUM_DOCUMENTO": df21["NUM_DOCUMENTO"],
    "FECHA_NACIMIENTO_ORIGINAL": fecha_original,
    "FECHA_NACIMIENTO_H97": df21["FECHA_NACIMIENTO"],
})

if df21.shape != (2371, 21):
    raise SystemExit(f"BLOQUEO: salida esperada 2371x21, observado={df21.shape}")

print("[4/9] Validando estructura H97...", flush=True)

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
add("FECHA_NACIMIENTO incluida", "OK" if "FECHA_NACIMIENTO" in df21.columns else "ERROR", "INCLUIDA", "INCLUIDA")
add("VIGENCIA excluida", "OK" if "VIGENCIA" not in df21.columns else "ERROR", "NO_INCLUIDA", "NO_INCLUIDA")
add("Primera columna CODIGO_IES_NUM", "OK" if df21.columns[0] == "CODIGO_IES_NUM" else "ERROR", df21.columns[0], "CODIGO_IES_NUM")
add("Última columna UNID_APROBADAS_TOTAL", "OK" if df21.columns[-1] == "UNID_APROBADAS_TOTAL" else "ERROR", df21.columns[-1], "UNID_APROBADAS_TOTAL")
add(
    "Fechas AAAA-MM-DD",
    "OK" if df21["FECHA_NACIMIENTO"].str.match(r"^\d{4}-\d{2}-\d{2}$").all() else "ERROR",
    "VALIDADO",
    "AAAA-MM-DD",
)

for c in ["CURSO_1ER_SEM", "CURSO_2DO_SEM"]:
    vals = sorted(set(df21[c].astype(str).str.strip()))
    invalidos = [v for v in vals if v not in ["SI", "NO"]]
    add(f"Valores permitidos {c}", "OK" if not invalidos else "ERROR", " | ".join(invalidos), "SI/NO")

for c in ["UNIDADES_CURSADAS", "UNIDADES_APROBADAS", "UNID_CURSADAS_TOTAL", "UNID_APROBADAS_TOTAL"]:
    nums = pd.to_numeric(df21[c], errors="coerce")
    nulos = int(nums.isna().sum())
    negativos = int((nums.fillna(0) < 0).sum())
    decimales = int(((nums.fillna(0) % 1) != 0).sum())
    add(f"Numérico {c}", "OK" if nulos == 0 else "ERROR", nulos, 0)
    add(f"Entero {c}", "OK" if decimales == 0 else "ERROR", decimales, 0)
    add(f"No negativo {c}", "OK" if negativos == 0 else "ERROR", negativos, 0)

n19_gt_18 = int((pd.to_numeric(df21["UNIDADES_APROBADAS"]) > pd.to_numeric(df21["UNIDADES_CURSADAS"])).sum())
n21_gt_20 = int((pd.to_numeric(df21["UNID_APROBADAS_TOTAL"]) > pd.to_numeric(df21["UNID_CURSADAS_TOTAL"])).sum())

add("UNIDADES_APROBADAS <= UNIDADES_CURSADAS", "OK" if n19_gt_18 == 0 else "ERROR", n19_gt_18, 0)
add("UNID_APROBADAS_TOTAL <= UNID_CURSADAS_TOTAL", "OK" if n21_gt_20 == 0 else "ERROR", n21_gt_20, 0)

validaciones_df = pd.DataFrame(validaciones)
errores = validaciones_df[validaciones_df["RESULTADO"].eq("ERROR")]

if len(errores) > 0:
    imprimir("ERRORES", errores)
    raise SystemExit("BLOQUEO: validaciones H97 fallaron.")

print("[5/9] Construyendo resúmenes...", flush=True)

resumen = pd.DataFrame([
    {"INDICADOR": "Filas", "VALOR": len(df21)},
    {"INDICADOR": "Columnas", "VALOR": len(df21.columns)},
    {"INDICADOR": "Campo incluido", "VALOR": "FECHA_NACIMIENTO"},
    {"INDICADOR": "Campo excluido", "VALOR": "VIGENCIA"},
    {"INDICADOR": "Formato FECHA_NACIMIENTO", "VALOR": "AAAA-MM-DD"},
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
    "SUBPROYECTO": "H97 estructura 21 campos con fecha sin vigencia 5809 matrícula",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "ID_CARGA": 16768,
    "NOMBRE_CARGA": "Matrícula Avance Curricular 2026",
    "ENTRADA_H95_22_CAMPOS": str(csv_h95),
    "SALIDA_H97_21_CAMPOS": "GENERADA",
    "CAMPO_INCLUIDO": "FECHA_NACIMIENTO",
    "CAMPO_EXCLUIDO": "VIGENCIA",
    "FORMATO_FECHA": "AAAA-MM-DD",
    "FILAS": len(df21),
    "COLUMNAS": len(df21.columns),
    "VALIDACION": "OK",
    "FUENTES_ORIGINALES_MODIFICADAS": "NO",
    "DICTAMEN": "APTO_ESTRUCTURALMENTE_SEGUN_RECHAZO_PLATAFORMA_H96",
}])

print("[6/9] Escribiendo archivos H97 en GitHub...", flush=True)

csv_h97 = SALIDA / "5809_MATRICULA_AVANCE_CURRICULAR_2026_SIES_READY_21_CAMPOS_CON_FECHA_SIN_VIGENCIA.csv"
xlsx_h97 = SALIDA / "5809_MATRICULA_AVANCE_CURRICULAR_2026_SIES_READY_21_CAMPOS_CON_FECHA_SIN_VIGENCIA_CON_ENCABEZADO.xlsx"
auditoria = SALIDA / "AUDITORIA_H97_SIES_READY_21_CAMPOS_CON_FECHA_SIN_VIGENCIA_5809.xlsx"
informe = SALIDA / "INFORME_H97_SIES_READY_21_CAMPOS_CON_FECHA_SIN_VIGENCIA_5809.md"
manifest = SALIDA / "manifest_h97_sies_ready_21_campos_con_fecha_sin_vigencia_5809.json"
script_out = SALIDA / "h97_sies_ready_21_campos_con_fecha_sin_vigencia_5809.py"

df21.to_csv(csv_h97, sep=";", index=False, header=False, encoding="latin1")

with pd.ExcelWriter(xlsx_h97, engine="openpyxl") as writer:
    df21.to_excel(writer, sheet_name="5809_H97_21_CAMPOS", index=False)
    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

with pd.ExcelWriter(auditoria, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    resumen.to_excel(writer, sheet_name="01_RESUMEN", index=False)
    resumen_16_17.to_excel(writer, sheet_name="02_RESUMEN_16_17", index=False)
    validaciones_df.to_excel(writer, sheet_name="03_VALIDACIONES", index=False)
    control_fecha.to_excel(writer, sheet_name="04_CONTROL_FECHA", index=False)
    pd.DataFrame({"COLUMNAS_H97_21_CAMPOS": cols_21}).to_excel(writer, sheet_name="05_ESTRUCTURA_H97", index=False)
    pd.DataFrame({"COLUMNAS_H95_22_CAMPOS": cols_22}).to_excel(writer, sheet_name="06_ESTRUCTURA_ORIGEN_H95", index=False)
    pd.DataFrame([
        {"FUENTE": "CSV_H95_22_CAMPOS", "RUTA": str(csv_h95), "SHA256": sha256(csv_h95)},
        {"FUENTE": "CSV_H97_21_CAMPOS", "RUTA": str(csv_h97), "SHA256": sha256(csv_h97)},
        {"FUENTE": "XLSX_H97_21_CAMPOS", "RUTA": str(xlsx_h97), "SHA256": sha256(xlsx_h97)},
    ]).to_excel(writer, sheet_name="07_FUENTES", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for column_cells in ws.columns:
            width = max(len(str(cell.value or "")) for cell in column_cells[:1000])
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(width + 2, 12), 120)

informe.write_text(
f"""# H97 — SIES_READY 21 campos con FECHA_NACIMIENTO y sin VIGENCIA

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Matrícula Avance Curricular 2026, ID Carga 16768.

## Motivo

La carga H96 demostró que la plataforma sí esperaba `FECHA_NACIMIENTO`, porque al eliminarlo el `CODIGO_UNICO` fue leído como fecha.

## Corrección aplicada

- Se conserva `FECHA_NACIMIENTO`.
- Se excluye `VIGENCIA`.
- Se normaliza `FECHA_NACIMIENTO` a formato `AAAA-MM-DD`.
- Se mantiene CSV sin encabezado y delimitado por punto y coma.

## Resultado

- Filas: {len(df21)}
- Columnas: {len(df21.columns)}
- CSV sin encabezado: SI
- Separador: punto y coma
- Encoding: latin1
- Fuentes originales modificadas: NO

## Archivo a subir

`{csv_h97}`
""",
encoding="utf-8"
)

manifest.write_text(json.dumps({
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "H97 SIES_READY 21 campos con fecha sin vigencia 5809",
    "id_carga": 16768,
    "entrada_h95": str(csv_h95),
    "csv_h97": str(csv_h97),
    "xlsx_h97": str(xlsx_h97),
    "auditoria": str(auditoria),
    "filas": len(df21),
    "columnas": len(df21.columns),
    "campo_incluido": "FECHA_NACIMIENTO",
    "campo_excluido": "VIGENCIA",
    "formato_fecha": "AAAA-MM-DD",
    "sha256_csv_h97": sha256(csv_h97),
    "fuentes_originales_modificadas": False,
}, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h97_sies_ready_21_campos_con_fecha_sin_vigencia_5809.py"), script_out)

print("[7/9] Releyendo CSV H97...", flush=True)

reread = pd.read_csv(csv_h97, sep=";", header=None, dtype=str, keep_default_na=False, encoding="latin1")

if reread.shape != (2371, 21):
    raise SystemExit(f"BLOQUEO: CSV H97 esperado 2371x21, observado={reread.shape}")

print("[8/9] Dejando SOLO el CSV H97 en el Escritorio...", flush=True)

desktop_csv = DESKTOP / "5809_MATRICULA_AVANCE_CURRICULAR_2026_SIES_READY_SUBIR_ID_16768.csv"

if desktop_csv.exists():
    desktop_csv.unlink()

shutil.copy2(csv_h97, desktop_csv)

if not desktop_csv.exists() or desktop_csv.stat().st_size == 0:
    raise SystemExit("BLOQUEO: no se pudo dejar el CSV final en el Escritorio.")

print("[9/9] Resultado final H97", flush=True)

print()
print("=" * 150)
print("H97 — SIES_READY 21 CAMPOS CON FECHA SIN VIGENCIA GENERADO")
print("=" * 150)
print("Proceso: Avance Curricular SIES 2026")
print("ID Carga: 16768")
print("Nombre carga: Matrícula Avance Curricular 2026")
print("Filas: 2371")
print("Columnas: 21")
print("Incluye: FECHA_NACIMIENTO")
print("Excluye: VIGENCIA")
print("Formato fecha: AAAA-MM-DD")
print("CSV: sin encabezado, separador punto y coma, encoding latin1")
print("Fuentes originales modificadas: NO")
print()
print(f"CSV GitHub: {csv_h97}")
print(f"CSV ÚNICO EN ESCRITORIO PARA SUBIR: {desktop_csv}")
print(f"Excel revisión GitHub: {xlsx_h97}")
print(f"Auditoría GitHub: {auditoria}")
print(f"Informe GitHub: {informe}")
print(f"Manifest GitHub: {manifest}")

imprimir("DICTAMEN", dictamen)
imprimir("RESUMEN", resumen)
imprimir("VALIDACIONES", validaciones_df)
