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
    / "avance_curricular_2026/99_archivo_final_subir_sies_5809"
    / f"ARCHIVO_FINAL_SUBIR_SIES_5809_{ts}"
)
SALIDA.mkdir(parents=True, exist_ok=True)

H95 = RAIZ / "avance_curricular_2026/95_validacion_final_sies_ready_5809/VALIDACION_FINAL_SIES_READY_5809_20260709_030847/5809_MATRICULA_AVANCE_CURRICULAR_2026_SIES_READY.csv"

if not H95.exists():
    raise SystemExit(f"BLOQUEO: no existe H95: {H95}")

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

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

df = pd.read_csv(
    H95,
    sep=";",
    header=None,
    names=cols,
    dtype=str,
    keep_default_na=False,
    encoding="utf-8-sig",
)

if df.shape != (2371, 22):
    raise SystemExit(f"BLOQUEO: esperado 2371x22, observado {df.shape}")

# Normalizar fecha sin eliminar columna.
fecha = pd.to_datetime(df["FECHA_NACIMIENTO"], errors="coerce")
if fecha.isna().sum() > 0:
    raise SystemExit(f"BLOQUEO: fechas inválidas: {int(fecha.isna().sum())}")

df["FECHA_NACIMIENTO"] = fecha.dt.strftime("%Y-%m-%d")

# Validaciones críticas.
errores = []

if df.shape != (2371, 22):
    errores.append(f"Estructura incorrecta: {df.shape}")

if list(df.columns) != cols:
    errores.append("Orden de columnas incorrecto")

if "VIGENCIA" not in df.columns:
    errores.append("Falta VIGENCIA")

if "FECHA_NACIMIENTO" not in df.columns:
    errores.append("Falta FECHA_NACIMIENTO")

if not df["FECHA_NACIMIENTO"].str.match(r"^\d{4}-\d{2}-\d{2}$").all():
    errores.append("FECHA_NACIMIENTO no está en formato AAAA-MM-DD")

for c in ["CURSO_1ER_SEM", "CURSO_2DO_SEM"]:
    invalidos = sorted(set(df[c]) - {"SI", "NO"})
    if invalidos:
        errores.append(f"{c} inválidos: {invalidos}")

for c in ["UNIDADES_CURSADAS", "UNIDADES_APROBADAS", "UNID_CURSADAS_TOTAL", "UNID_APROBADAS_TOTAL"]:
    nums = pd.to_numeric(df[c], errors="coerce")
    if nums.isna().sum() > 0:
        errores.append(f"{c} no numérico")
    if (nums < 0).sum() > 0:
        errores.append(f"{c} negativo")
    if ((nums % 1) != 0).sum() > 0:
        errores.append(f"{c} no entero")

if (pd.to_numeric(df["UNIDADES_APROBADAS"]) > pd.to_numeric(df["UNIDADES_CURSADAS"])).sum() > 0:
    errores.append("UNIDADES_APROBADAS > UNIDADES_CURSADAS")

if (pd.to_numeric(df["UNID_APROBADAS_TOTAL"]) > pd.to_numeric(df["UNID_CURSADAS_TOTAL"])).sum() > 0:
    errores.append("UNID_APROBADAS_TOTAL > UNID_CURSADAS_TOTAL")

if errores:
    print("\n".join(errores))
    raise SystemExit("BLOQUEO: no se generó archivo final.")

csv_final = SALIDA / "5809_MATRICULA_AVANCE_CURRICULAR_2026_FINAL_SUBIR_SIES.csv"
xlsx_revision = SALIDA / "5809_MATRICULA_AVANCE_CURRICULAR_2026_FINAL_SUBIR_SIES_CON_ENCABEZADO.xlsx"
manifest = SALIDA / "manifest_h99_archivo_final_subir_sies_5809.json"
script_out = SALIDA / "h99_archivo_final_subir_sies_5809.py"

df.to_csv(csv_final, sep=";", index=False, header=False, encoding="latin1")

with pd.ExcelWriter(xlsx_revision, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="5809_FINAL_22_CAMPOS", index=False)
    ws = writer.book["5809_FINAL_22_CAMPOS"]
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

manifest.write_text(json.dumps({
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "5809 Matrícula Avance Curricular",
    "id_carga": 16768,
    "archivo_base": str(H95),
    "archivo_final_github": str(csv_final),
    "archivo_final_escritorio": str(DESKTOP / "5809_MATRICULA_AVANCE_CURRICULAR_2026_FINAL_SUBIR_SIES.csv"),
    "filas": len(df),
    "columnas": len(df.columns),
    "incluye_fecha_nacimiento": True,
    "incluye_vigencia": True,
    "formato_fecha": "AAAA-MM-DD",
    "csv_sin_encabezado": True,
    "separador": ";",
    "encoding": "latin1",
    "sha256_csv_final": sha256(csv_final),
    "fuentes_originales_modificadas": False,
}, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h99_archivo_final_subir_sies_5809.py"), script_out)

# Limpiar avisos/CSV anteriores del Escritorio del mismo proceso.
for p in DESKTOP.glob("*5809*"):
    if p.is_file():
        p.unlink()

desktop_csv = DESKTOP / "5809_MATRICULA_AVANCE_CURRICULAR_2026_FINAL_SUBIR_SIES.csv"
shutil.copy2(csv_final, desktop_csv)

print("=" * 140)
print("H99 — ARCHIVO FINAL LISTO PARA SUBIR A SIES")
print("=" * 140)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 Matrícula Avance Curricular")
print("ID Carga: 16768")
print("Filas: 2371")
print("Columnas: 22")
print("Incluye FECHA_NACIMIENTO: SI")
print("Incluye VIGENCIA: SI")
print("Fecha: AAAA-MM-DD")
print("CSV: sin encabezado, separador punto y coma, encoding latin1")
print("Fuentes originales modificadas: NO")
print()
print(f"ARCHIVO PARA SUBIR:")
print(desktop_csv)
print()
print(f"Respaldo GitHub:")
print(csv_final)
print("=" * 140)
