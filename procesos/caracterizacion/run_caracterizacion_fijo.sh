#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOWNLOADS_DIR="${CARACTERIZACION_INPUT_DIR:-$HOME/Downloads}"

find_latest() {
  local prefix="$1"
  "$PY_BIN" - "$DOWNLOADS_DIR" "$prefix" <<'PY'
from pathlib import Path
import sys
base = Path(sys.argv[1]).expanduser()
prefix = sys.argv[2]
if not base.exists():
    print("")
    raise SystemExit(0)
candidates = [p for p in base.iterdir() if p.is_file() and p.name.startswith(prefix)]
candidates.sort(key=lambda p: (p.stat().st_mtime, p.name), reverse=True)
print(str(candidates[0].resolve()) if candidates else "")
PY
}

if [[ -n "${CARACTERIZACION_PYTHON:-}" ]]; then
  PY_BIN="$CARACTERIZACION_PYTHON"
elif command -v python3.13 >/dev/null 2>&1; then
  PY_BIN="python3.13"
else
  PY_BIN="python3"
fi

default_periodo() {
  local month
  month="$(date +%m)"
  if ((10#$month >= 7)); then
    printf "2"
  else
    printf "1"
  fi
}

ANIO_ANALISIS="${1:-${ANIO_ANALISIS:-$(date +%Y)}}"
PERIODO_ANALISIS="${2:-${PERIODO_ANALISIS:-$(default_periodo)}}"
VERBOSIDAD="${3:-${VERBOSIDAD:-2}}"

RUTA_MATRICULA="${RUTA_MATRICULA:-$(find_latest 'DATOSDEALUMNOS_')}"
RUTA_RESULTADOS="${RUTA_RESULTADOS:-$(find_latest 'results-survey923565')}"
RUTA_INSCRITOS="${RUTA_INSCRITOS:-$(find_latest 'tokens_923565')}"
RUTA_PROMEDIOS="${RUTA_PROMEDIOS:-$(find_latest 'PROMEDIOSDEALUMNOS_')}"

export ANIO_ANALISIS
export PERIODO_ANALISIS
export VERBOSIDAD
export RUTA_MATRICULA
export RUTA_RESULTADOS
export RUTA_INSCRITOS
export RUTA_PROMEDIOS

format_elapsed() {
  local total_seconds="$1"
  local hours=$((total_seconds / 3600))
  local minutes=$(((total_seconds % 3600) / 60))
  local seconds=$((total_seconds % 60))
  printf "%02d:%02d:%02d" "$hours" "$minutes" "$seconds"
}

START_TS="$(date +%s)"

if "$PY_BIN" "$SCRIPT_DIR/caracterizacion.py"; then
  END_TS="$(date +%s)"
  ELAPSED_TS=$((END_TS - START_TS))
  printf '\n[TIEMPO TOTAL] Ejecución completada en %s\n' "$(format_elapsed "$ELAPSED_TS")"
else
  EXIT_CODE=$?
  END_TS="$(date +%s)"
  ELAPSED_TS=$((END_TS - START_TS))
  printf '\n[TIEMPO TOTAL] Ejecución interrumpida tras %s\n' "$(format_elapsed "$ELAPSED_TS")"
  exit "$EXIT_CODE"
fi
