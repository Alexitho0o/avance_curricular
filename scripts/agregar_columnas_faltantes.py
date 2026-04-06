import pandas as pd
from pathlib import Path

# Ruta al archivo Excel
EXCEL_PATH = "archive/resultados_diagnostico/for_ing_fix/archivo_listo_para_sies.xlsx"

# Columnas requeridas
COLUMNAS_REQUERIDAS = ["VIG_ESPERADO_DA", "FLAG_INCONSISTENCIA_VIG"]

# Leer el archivo Excel
excel_path = Path(EXCEL_PATH).resolve()
if not excel_path.exists():
    print(f"ERROR: El archivo {EXCEL_PATH} no existe.")
    exit(1)

# Cargar las hojas necesarias
xls = pd.ExcelFile(excel_path)
if "ARCHIVO_LISTO_SUBIDA" not in xls.sheet_names:
    print("ERROR: La hoja 'ARCHIVO_LISTO_SUBIDA' no existe en el archivo Excel.")
    exit(1)

# Leer la hoja ARCHIVO_LISTO_SUBIDA
df = pd.read_excel(xls, sheet_name="ARCHIVO_LISTO_SUBIDA")

# Agregar columnas faltantes
for columna in COLUMNAS_REQUERIDAS:
    if columna not in df.columns:
        df[columna] = 0  # Valor predeterminado: 0
        print(f"Columna '{columna}' agregada con valor predeterminado 0.")

# Guardar el archivo actualizado
output_path = excel_path.parent / "archivo_listo_para_sies_actualizado.xlsx"
df.to_excel(output_path, index=False, sheet_name="ARCHIVO_LISTO_SUBIDA")
print(f"Archivo actualizado guardado en: {output_path}")