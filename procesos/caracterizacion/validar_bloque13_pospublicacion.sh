#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'
ROOT="$(
    cd "$(
        dirname "${BASH_SOURCE[0]}"
    )" &&
    pwd
)"
cd "$ROOT"
if [ -x "$ROOT/.venv/bin/python" ]; then
    PYTHON="$ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="$(command -v python3)"
else
    echo "ERROR: no se encontró Python." >&2
    exit 1
fi
exec "$PYTHON" \
    "$ROOT/scripts/validacion/validar_bloque13_pospublicacion.py" \
    --repo "$ROOT" \
    "$@"
