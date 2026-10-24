#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/Users/alexi/Documents/GitHub/CARACTERIZACIÓN"
PYTHON_BIN="/Users/alexi/Documents/GitHub/avance_curricular/.venv/bin/python3"
AC_FILE="${PROJECT_DIR}/integracion_avance_curricular.py"

cd "${PROJECT_DIR}"

set_ac_flag_true() {
  "${PYTHON_BIN}" - "${AC_FILE}" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
txt = path.read_text(encoding="utf-8")
line_false = "ACTIVAR_INTEGRACION_AVANCE_CURRICULAR = False"
line_true = "ACTIVAR_INTEGRACION_AVANCE_CURRICULAR = True"
pat_false = re.compile(r"^ACTIVAR_INTEGRACION_AVANCE_CURRICULAR = False$", re.M)
pat_true = re.compile(r"^ACTIVAR_INTEGRACION_AVANCE_CURRICULAR = True$", re.M)

if pat_false.search(txt):
    txt = pat_false.sub(line_true, txt, count=1)
    path.write_text(txt, encoding="utf-8")
    print("[AC_TEST] Bandera AC activa temporalmente.")
elif pat_true.search(txt):
    print("[AC_TEST][WARN] La bandera AC ya estaba en True.")
else:
    raise SystemExit("[AC_TEST][ERROR] No se encontró la línea exacta de bandera AC para activar.")
PY
}

restore_ac_flag_false() {
  "${PYTHON_BIN}" - "${AC_FILE}" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
txt = path.read_text(encoding="utf-8")
line_false = "ACTIVAR_INTEGRACION_AVANCE_CURRICULAR = False"
pat_false = re.compile(r"^ACTIVAR_INTEGRACION_AVANCE_CURRICULAR = False$", re.M)
pat_true = re.compile(r"^ACTIVAR_INTEGRACION_AVANCE_CURRICULAR = True$", re.M)

if pat_true.search(txt):
    txt = pat_true.sub(line_false, txt, count=1)
    path.write_text(txt, encoding="utf-8")
    print("[AC_TEST] Bandera AC restaurada en False.")
elif pat_false.search(txt):
    print("[AC_TEST] Bandera AC ya estaba en False.")
else:
    print("[AC_TEST][WARN] No se encontró línea exacta de bandera AC al restaurar; revisar manualmente.", file=sys.stderr)
PY
}

compile_project() {
  cd "${PROJECT_DIR}"
  "${PYTHON_BIN}" -m py_compile caracterizacion.py
  "${PYTHON_BIN}" -m py_compile integracion_avance_curricular.py
}

check_flag_false() {
  "${PYTHON_BIN}" - "${AC_FILE}" <<'PY'
from pathlib import Path
import re
import sys

txt = Path(sys.argv[1]).read_text(encoding="utf-8")
if re.search(r"^ACTIVAR_INTEGRACION_AVANCE_CURRICULAR = False$", txt, re.M):
    print("[AC_TEST] BANDERA_RESTAURADA_FALSE: SI")
else:
    raise SystemExit("[AC_TEST][ERROR] BANDERA_RESTAURADA_FALSE: NO")
PY
}

cleanup() {
  local status=$?
  local cleanup_status=0
  trap - EXIT
  set +e

  echo "[AC_TEST] Restaurando bandera AC en False..."
  restore_ac_flag_false || cleanup_status=1

  echo "[AC_TEST] Compilando estado final..."
  compile_project || cleanup_status=1
  check_flag_false || cleanup_status=1

  if [[ ${cleanup_status} -ne 0 && ${status} -eq 0 ]]; then
    status=1
  fi

  if [[ ${status} -eq 0 ]]; then
    echo "[AC_TEST] COMPILACION_FINAL_OK: SI"
    echo "[AC_TEST] OK"
  else
    echo "[AC_TEST][ERROR] Finalizó con estado ${status}"
  fi

  exit "${status}"
}

trap cleanup EXIT

echo "[AC_TEST] Activando integración AC temporalmente..."
set_ac_flag_true

echo "[AC_TEST] Compilando antes de ejecutar..."
compile_project

echo "[AC_TEST] Ejecutando prueba acotada hasta BLOQUE 10.bis..."
AUTO_INSTALL_DEPS=0 \
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

echo "[AC_TEST] Validando Excel generado..."
"${PYTHON_BIN}" - <<'PY'
from pathlib import Path
import pandas as pd
import subprocess

desktop = Path.home() / "Desktop"
archivos = sorted(
    desktop.glob("PREGRADO_TRAYECTORIA_CARACTERIZACION_2026_P1_*.xlsx"),
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)

if not archivos:
    raise SystemExit("[AC_TEST][ERROR] No se encontró archivo PREGRADO_TRAYECTORIA_CARACTERIZACION_2026_P1_*.xlsx")

ruta = archivos[0]
print("[AC_TEST] ARCHIVO_VALIDADO:", ruta)

xls = pd.ExcelFile(ruta)
print("[AC_TEST] HOJAS:", xls.sheet_names)

aud_ok = "AUDITORIA_AVANCE_CURRICULAR" in xls.sheet_names
print("[AC_TEST] AUDITORIA_AVANCE_CURRICULAR_OK:", "SI" if aud_ok else "NO")

cols_esperadas = {
    "_AC_ASI_INS_ANT",
    "_AC_ASI_APR_ANT",
    "_AC_ASI_INS_HIS",
    "_AC_ASI_APR_HIS",
    "_AC_PROM_PRI_SEM",
    "_AC_PROM_SEG_SEM",
    "_AC_NIV_ACA",
    "_AC_NIV_ACA_FUENTE",
}

hallazgos = []
for hoja in xls.sheet_names:
    try:
        df = pd.read_excel(ruta, sheet_name=hoja, nrows=5)
        cols_ac = [str(c) for c in df.columns if str(c).startswith("_AC_")]
        if cols_ac:
            hallazgos.append((hoja, cols_ac))
    except Exception as exc:
        print(f"[AC_TEST][WARN] leyendo hoja {hoja}: {exc}")

trayectoria_ok = False
for hoja, cols in hallazgos:
    if hoja == "TRAYECTORIA_POR_PERIODO":
        trayectoria_ok = cols_esperadas.issubset(set(cols))
        print("[AC_TEST] HOJA_CON_COLUMNAS_AC:", hoja)
        print("[AC_TEST] TOTAL_COLUMNAS_AC:", len(cols))
        print("[AC_TEST] COLUMNAS_AC:", cols)

print("[AC_TEST] INTEGRACION_AC_OK:", "SI" if trayectoria_ok else "NO")

if not aud_ok:
    raise SystemExit("[AC_TEST][ERROR] Falta hoja AUDITORIA_AVANCE_CURRICULAR")

if not trayectoria_ok:
    raise SystemExit("[AC_TEST][ERROR] TRAYECTORIA_POR_PERIODO no contiene todas las columnas _AC_ esperadas")

subprocess.run(["open", str(ruta)], check=False)
PY
