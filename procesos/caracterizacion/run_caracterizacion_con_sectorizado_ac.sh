#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/Users/alexi/Documents/GitHub/CARACTERIZACIÓN"
PYTHON="/Users/alexi/Documents/GitHub/avance_curricular/.venv/bin/python3"
AC_FILE="${PROJECT_DIR}/integracion_avance_curricular.py"

cd "$PROJECT_DIR"

restore_ac_flag() {
  echo "[SECTORIZADO_AC_TEST] Restaurando bandera AC en False..."
  "$PYTHON" - <<'PY'
from pathlib import Path
p = Path("integracion_avance_curricular.py")
txt = p.read_text(encoding="utf-8")
if "ACTIVAR_INTEGRACION_AVANCE_CURRICULAR = True" in txt:
    txt = txt.replace("ACTIVAR_INTEGRACION_AVANCE_CURRICULAR = True", "ACTIVAR_INTEGRACION_AVANCE_CURRICULAR = False", 1)
p.write_text(txt, encoding="utf-8")
PY
}

trap restore_ac_flag EXIT

echo "[SECTORIZADO_AC_TEST] Estado inicial bandera AC:"
"$PYTHON" - <<'PY'
from pathlib import Path
import ast
p = Path("integracion_avance_curricular.py")
tree = ast.parse(p.read_text(encoding="utf-8"))
for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "ACTIVAR_INTEGRACION_AVANCE_CURRICULAR":
                print(f"LINEA={node.lineno} VALOR={ast.literal_eval(node.value)}")
PY

echo "[SECTORIZADO_AC_TEST] Activando integración AC temporalmente..."
"$PYTHON" - <<'PY'
from pathlib import Path
p = Path("integracion_avance_curricular.py")
txt = p.read_text(encoding="utf-8")
needle = "ACTIVAR_INTEGRACION_AVANCE_CURRICULAR = False"
if needle not in txt:
    raise SystemExit("[SECTORIZADO_AC_TEST][ERROR] No se encontró asignación False para activar.")
txt = txt.replace(needle, "ACTIVAR_INTEGRACION_AVANCE_CURRICULAR = True", 1)
p.write_text(txt, encoding="utf-8")
PY

echo "[SECTORIZADO_AC_TEST] Compilando scripts..."
"$PYTHON" -m py_compile caracterizacion.py
"$PYTHON" -m py_compile integracion_avance_curricular.py
"$PYTHON" -m py_compile analisis_sectorizado_encuesta_ac.py

echo "[SECTORIZADO_AC_TEST] Ejecutando caracterizacion.py con corte después de BLOQUE 10.bis..."
ANIO_ANALISIS=2026 \
PERIODO_ANALISIS=1 \
VERBOSIDAD=2 \
COHORTE_TXT=2026 \
RUTA_MATRICULA="/Users/alexi/Downloads/DATOSDEALUMNOS_8551.xlsx" \
RUTA_INSCRITOS="/Users/alexi/Downloads/tokens_923565.csv" \
RUTA_RESULTADOS="/Users/alexi/Downloads/results-survey923565.xlsx" \
RUTA_PROMEDIOS="/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx" \
CARACTERIZACION_SKIP_FCU=1 \
CARACTERIZACION_ACTIVAR_SECTORIZADO_AC=1 \
CARACTERIZACION_STOP_AFTER_10BIS=1 \
"$PYTHON" caracterizacion.py

echo "[SECTORIZADO_AC_TEST] Validando último archivo sectorizado AC..."
"$PYTHON" - <<'PY'
from pathlib import Path
import ast
import pandas as pd
from openpyxl import load_workbook

desktop = Path.home() / "Desktop"
archivos = sorted(
    desktop.glob("ENCUESTA_CARACTERIZACION_2026_P1_*_ANALISIS_SECTORIZADO_AC*.xlsx"),
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)
if not archivos:
    raise SystemExit("[SECTORIZADO_AC_TEST][ERROR] No se encontró archivo sectorizado AC.")
archivo = archivos[0]
print("[SECTORIZADO_AC_TEST] ARCHIVO_FINAL:", archivo)

xls = pd.ExcelFile(archivo)
wb = load_workbook(archivo, read_only=False)
base = pd.read_excel(archivo, sheet_name="BASE_SECTORIZADA")
cols_ac = [c for c in base.columns if str(c).startswith("_AC_")]
dist = base["SECTOR_ACADEMICO"].value_counts().to_dict()

assert xls.sheet_names[0] == "PANEL_SECTORIZADO_EJECUTIVO", "P1 falla: panel no es primera hoja"
panel = wb["PANEL_SECTORIZADO_EJECUTIVO"]
assert panel.max_row > 20, "P1 falla: panel vacío"

values = [str(c.value) for row in panel.iter_rows() for c in row if c.value is not None]
assert any("Ranking de focos críticos" in v for v in values), "P2 falla: no existe ranking de focos críticos"

rank_row = None
for row in panel.iter_rows():
    for cell in row:
        if cell.value == "Ranking de focos críticos":
            rank_row = cell.row
            break
    if rank_row:
        break
assert rank_row is not None, "P2 falla: no se ubicó ranking"
header_row = rank_row + 1
headers = {str(panel.cell(header_row, c).value): c for c in range(1, panel.max_column + 1) if panel.cell(header_row, c).value}
rate_col = headers.get("TASA_RESPUESTA_PCT")
assert rate_col, "P2 falla: ranking sin TASA_RESPUESTA_PCT"
rates = []
for r in range(header_row + 1, panel.max_row + 1):
    first = panel.cell(r, 1).value
    if first == "Matriz sector × jornada × nuevo/antiguo":
        break
    val = panel.cell(r, rate_col).value
    if isinstance(val, (int, float)):
        rates.append(float(val))
assert rates and rates == sorted(rates), "P2 falla: focos críticos no están ordenados por menor tasa"

assert "MATRIZ_SECTOR_JORNADA_NA" in xls.sheet_names, "P3 falla: falta matriz"
matriz = pd.read_excel(archivo, sheet_name="MATRIZ_SECTOR_JORNADA_NA")
assert not matriz.empty, "P3 falla: matriz vacía"

for h in ["PANEL_SECTORIZADO_EJECUTIVO", "SECTOR_JORNADA_NA", "CARRERA_JORNADA_NA", "BASE_SECTORIZADA"]:
    ws = wb[h]
    fills = [str(c.fill.fgColor.rgb or c.fill.fgColor.indexed or c.fill.fgColor.type) for c in ws[1]]
    assert ws.freeze_panes is not None and bool(ws.auto_filter.ref) and any(v not in ("00000000", "0", "None", "rgb") for v in fills), f"P4 falla formato {h}"

assert len(xls.sheet_names) == 42, f"P5 falla total hojas: {len(xls.sheet_names)}"
for h in ["BASE_SECTORIZADA", "AUDITORIA_CRUCE_AC", "AUDITORIA_SECTORES", "AUDITORIA_GRANULARIDAD"]:
    assert h in xls.sheet_names, f"P5 falla falta {h}"

nan_text = []
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and cell.value.strip().lower() == "nan":
                nan_text.append((ws.title, cell.coordinate))
                break
        if nan_text:
            break
    if nan_text:
        break
assert not nan_text, f"P6 falla NaN textual visible: {nan_text[:3]}"

assert str(panel["A1"].value).startswith("Panel Ejecutivo Sectorizado"), "P7 falla diagnóstico inicial no está en panel"

assert len(base) == 4051, f"BASE_SECTORIZADA filas inesperadas: {len(base)}"
assert len(cols_ac) == 8, f"Columnas AC inesperadas: {cols_ac}"
assert dist.get("Tecnología") == 2019, dist
assert dist.get("Administración y Comercio") == 1421, dist
assert dist.get("Salud") == 611, dist
assert int(base["SECTOR_ACADEMICO"].eq("Sin clasificar").sum()) == 0
tpc = base[base["CARRERA_NORMALIZADA"].eq("TECNICO EN PROGRAMACION COMPUTACIONAL")]
assert not tpc.empty and set(tpc["SECTOR_ACADEMICO"]) == {"Tecnología"}

tree = ast.parse(Path("integracion_avance_curricular.py").read_text(encoding="utf-8"))
valor = None
for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "ACTIVAR_INTEGRACION_AVANCE_CURRICULAR":
                valor = ast.literal_eval(node.value)
assert valor is True, "Durante la ejecución la bandera debería estar temporalmente activa."

print("VALIDACION_7_PUNTOS_SECTORIZADO_AC_OK: SI")
print("VALIDACION_AUTOMATICA_SECTORIZADO_AC_OK: SI")
Path("/tmp/sectorizado_ac_ultimo.txt").write_text(str(archivo), encoding="utf-8")
PY

ARCHIVO_FINAL="$(cat /tmp/sectorizado_ac_ultimo.txt)"
open "$ARCHIVO_FINAL"

restore_ac_flag
trap - EXIT

echo "[SECTORIZADO_AC_TEST] Validando bandera restaurada..."
"$PYTHON" - <<'PY'
from pathlib import Path
import ast
tree = ast.parse(Path("integracion_avance_curricular.py").read_text(encoding="utf-8"))
valor = None
for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "ACTIVAR_INTEGRACION_AVANCE_CURRICULAR":
                valor = ast.literal_eval(node.value)
print("BANDERA_RESTAURADA_FALSE:", "SI" if valor is False else "NO")
if valor is not False:
    raise SystemExit("[SECTORIZADO_AC_TEST][ERROR] La bandera no quedó en False.")
PY

echo "VALIDACION_AUTOMATICA_SECTORIZADO_AC_OK: SI"
