#!/usr/bin/env bash
set -Eeuo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_BIN="${CARACTERIZACION_PYTHON:-}"
if [[ -z "$PY_BIN" ]]; then
  for candidate in python3 python py; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; assert sys.version_info >= (3, 10)' >/dev/null 2>&1; then
      PY_BIN="$candidate"
      break
    fi
  done
fi
if [[ -z "$PY_BIN" ]]; then
  echo 'No se encontro Python 3.10 o superior. Define CARACTERIZACION_PYTHON con su ruta.' >&2
  exit 3
fi
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
if command -v cygpath >/dev/null 2>&1; then
  export CARACTERIZACION_BASH="$(cygpath -w "$BASH")"
else
  export CARACTERIZACION_BASH="$BASH"
fi
exec "$PY_BIN" "$REPO_DIR/scripts/ejecutar_analisis_anual.py" "$@"
