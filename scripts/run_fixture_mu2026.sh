#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="python"
if [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
fi

FIXTURE_SCRIPT="scripts/fixture_validacion_cruzada_mu2026.py"
FIXTURE_DIR="control/fixtures/mu2026_validacion_cruzada"
RESULTS_DIR="$FIXTURE_DIR/resultados"
RESUMEN_JSON="$RESULTS_DIR/resumen_fixture_mu2026.json"
REPORTE_MD="$RESULTS_DIR/reporte_fixture_mu2026.md"

if [[ ! -f "$FIXTURE_SCRIPT" ]]; then
  echo "ERROR: no existe $FIXTURE_SCRIPT"
  exit 1
fi

if [[ ! -d "$FIXTURE_DIR" ]]; then
  echo "ERROR: no existe $FIXTURE_DIR"
  exit 1
fi

echo "== Fixture MU2026 · Validacion cruzada end to end =="
echo "Repo: $ROOT_DIR"
echo "Python: $PYTHON_BIN"

"$PYTHON_BIN" -m py_compile "$FIXTURE_SCRIPT"
"$PYTHON_BIN" "$FIXTURE_SCRIPT"

echo "== Resultados =="
echo "$RESUMEN_JSON"
echo "$REPORTE_MD"

if [[ ! -f "$RESUMEN_JSON" ]]; then
  echo "ERROR: no se genero $RESUMEN_JSON"
  exit 1
fi

DICTAMEN="$($PYTHON_BIN - <<'PY'
import json
from pathlib import Path
p = Path("control/fixtures/mu2026_validacion_cruzada/resultados/resumen_fixture_mu2026.json")
data = json.loads(p.read_text(encoding="utf-8"))
print(str(data.get("dictamen_fixture", "")).strip())
PY
)"

if [[ "$DICTAMEN" != "OK" ]]; then
  echo "ERROR: dictamen_fixture=$DICTAMEN (se requiere OK)"
  exit 1
fi

echo "OK: dictamen_fixture=$DICTAMEN"
