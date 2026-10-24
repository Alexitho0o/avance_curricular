#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/Users/alexi/Documents/GitHub/CARACTERIZACIÓN"
PYTHON_BIN="/Users/alexi/Documents/GitHub/avance_curricular/.venv/bin/python3"
DESKTOP_DIR="$HOME/Desktop"

echo ""
echo "===== CONSOLIDADO_RUT · BLOQUE 10.bis ====="
echo "[INFO] Proyecto: ${PROJECT_DIR}"
echo "[INFO] Python: ${PYTHON_BIN}"

cd "$PROJECT_DIR"

echo ""
echo "[1/5] Compilando fuentes críticas..."
"${PYTHON_BIN}" -m py_compile caracterizacion.py
"${PYTHON_BIN}" -m py_compile integracion_avance_curricular.py
echo "[OK] Compilación previa completada."

echo ""
echo "[2/5] Ejecutando flujo acotado hasta BLOQUE 10.bis..."
echo "[INFO] Flags modo rápido: SOLO_GENERAR_FCU=0 | CARACTERIZACION_FAST_FCU_ONLY=0 | CARACTERIZACION_SKIP_FCU=1 | CARACTERIZACION_STOP_AFTER_10BIS=1"
AUTO_INSTALL_DEPS=0 \
SOLO_GENERAR_FCU=0 \
CARACTERIZACION_FAST_FCU_ONLY=0 \
ANIO_ANALISIS=2026 \
PERIODO_ANALISIS=1 \
VERBOSIDAD=2 \
COHORTE_TXT=2026 \
RUTA_MATRICULA="/Users/alexi/Downloads/DATOSDEALUMNOS_8551.xlsx" \
RUTA_INSCRITOS="/Users/alexi/Downloads/tokens_923565.csv" \
RUTA_RESULTADOS="/Users/alexi/Downloads/results-survey923565.xlsx" \
RUTA_PROMEDIOS="/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx" \
CARACTERIZACION_SKIP_FCU=1 \
CARACTERIZACION_STOP_AFTER_10BIS=1 \
"${PYTHON_BIN}" caracterizacion.py

echo ""
echo "[3/5] Buscando el último Excel PREGRADO_TRAYECTORIA_CARACTERIZACION_2026_P1_*.xlsx..."
ARCHIVO_GENERADO="$(${PYTHON_BIN} - <<'PY'
from pathlib import Path

pattern = "PREGRADO_TRAYECTORIA_CARACTERIZACION_2026_P1_*.xlsx"
bases = [
    Path.home() / "Desktop",
    Path("/Users/alexi/Documents/GitHub/CARACTERIZACIÓN"),
    Path("/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/output"),
    Path("/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/outputs"),
]

candidates = []
seen = set()
for base in bases:
    if not base.exists():
        continue
    for path in base.glob(pattern):
        resolved = str(path.resolve())
        if resolved in seen:
            continue
        seen.add(resolved)
        candidates.append(path.resolve())

candidates.sort(key=lambda p: (p.stat().st_mtime, p.name), reverse=True)
print(str(candidates[0]) if candidates else "")
PY
)"

if [[ -z "$ARCHIVO_GENERADO" || ! -f "$ARCHIVO_GENERADO" ]]; then
  echo "[ERROR] No se encontró un archivo generado con el patrón requerido."
  exit 1
fi
echo "[OK] Archivo generado: ${ARCHIVO_GENERADO}"

echo ""
echo "[4/5] Validando hoja CONSOLIDADO_RUT..."
ARCHIVO_VALIDACION="$ARCHIVO_GENERADO" "${PYTHON_BIN}" -c '
from pathlib import Path
import os
import pandas as pd
import time
from zipfile import BadZipFile
from openpyxl import load_workbook

archivo = Path(os.environ["ARCHIVO_VALIDACION"]).resolve()
hoja_objetivo = "CONSOLIDADO_RUT"
base_cols = [
    "RUT",
    "DV",
    "TOKEN",
    "NOMBRE_COMPLETO",
    "SEXO",
    "CORREO_PERSONAL",
    "CORREO_INSTITUCIONAL",
    "CARRERA",
    "COD_CARRERA",
    "JORNADA",
    "SEDE",
    "ESTADO_ACADEMICO",
    "MATRICULA",
    "INSCRITO_LIMESURVEY",
    "RESPONDIO_ENCUESTA",
    "ESTADO_PARTICIPACION",
    "FUENTE_DATOS",
    "OBSERVACION_CRUCE",
]

ultimo_error = None
wb = None
df = None
for intento in range(1, 7):
    try:
        wb = load_workbook(archivo, read_only=True, data_only=False)
        df = pd.read_excel(archivo, sheet_name=hoja_objetivo, dtype=str, engine="openpyxl")
        break
    except (BadZipFile, OSError, ValueError) as exc:
        ultimo_error = exc
        if intento == 6:
            raise
        print(f"[INFO] Reintento {intento}/6: archivo aún no disponible para lectura completa ({exc}).")
        time.sleep(2)

hojas = wb.sheetnames
hojas_txt = ", ".join(hojas)
print(f"[INFO] Hojas disponibles: {hojas_txt}")
if hoja_objetivo not in hojas:
    raise SystemExit(f"[ERROR] El libro no contiene la hoja {hoja_objetivo}.")

if df.empty:
    raise SystemExit("[ERROR] CONSOLIDADO_RUT no contiene filas.")
if not ({"RUT", "TOKEN"} & set(df.columns)):
    raise SystemExit("[ERROR] CONSOLIDADO_RUT no contiene columna RUT ni TOKEN.")
if "SEXO" not in df.columns:
    raise SystemExit("[ERROR] CONSOLIDADO_RUT no contiene columna SEXO.")
if "RESPONDIO_ENCUESTA" not in df.columns:
    raise SystemExit("[ERROR] CONSOLIDADO_RUT no contiene columna RESPONDIO_ENCUESTA.")

survey_cols = [col for col in df.columns if col not in base_cols]
if not survey_cols:
    raise SystemExit("[ERROR] CONSOLIDADO_RUT no contiene columnas de encuesta anexadas.")

if all(col in df.columns for col in base_cols):
    idx_ultima_base = max(df.columns.get_loc(col) for col in base_cols)
    idx_primera_encuesta = min(df.columns.get_loc(col) for col in survey_cols)
    if idx_primera_encuesta <= idx_ultima_base:
        raise SystemExit("[ERROR] Las columnas de encuesta no quedaron anexadas a la derecha de las columnas base.")

print(f"[INFO] Filas de CONSOLIDADO_RUT: {len(df)}")
print(f"[INFO] Columnas totales: {len(df.columns)}")
print(f"[INFO] Cantidad de columnas de encuesta: {len(survey_cols)}")
primeras_cols = ", ".join(str(col) for col in survey_cols[:8])
print(f"[INFO] Primeras columnas de encuesta: {primeras_cols}")
print("[OK] Validación de CONSOLIDADO_RUT completada.")
'

ARCHIVO_FINAL="$ARCHIVO_GENERADO"
if [[ "$(dirname "$ARCHIVO_GENERADO")" != "$DESKTOP_DIR" ]]; then
  cp -f "$ARCHIVO_GENERADO" "$DESKTOP_DIR/"
  ARCHIVO_FINAL="$DESKTOP_DIR/$(basename "$ARCHIVO_GENERADO")"
  echo "[OK] Copia al Escritorio: ${ARCHIVO_FINAL}"
else
  echo "[OK] Archivo ya disponible en Escritorio: ${ARCHIVO_FINAL}"
fi

echo ""
echo "[5/5] Apertura automática del Excel..."
open "$ARCHIVO_FINAL"
echo "[OK] Apertura automática solicitada para: ${ARCHIVO_FINAL}"
echo "===== FIN CONSOLIDADO_RUT · BLOQUE 10.bis ====="