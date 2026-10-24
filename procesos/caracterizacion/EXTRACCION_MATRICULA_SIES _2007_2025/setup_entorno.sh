#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "Proyecto: $PROJECT_DIR"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[ERROR] No se encontró el intérprete: $PYTHON_BIN" >&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "[INFO] Creando entorno virtual en $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
else
  echo "[INFO] Reutilizando entorno virtual existente: $VENV_DIR"
fi

VENV_PY="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

echo "[INFO] Actualizando pip"
"$VENV_PY" -m pip install --upgrade pip

if [ -f "$PROJECT_DIR/requirements-dev.txt" ]; then
  echo "[INFO] Instalando dependencias desde requirements-dev.txt"
  "$VENV_PIP" install -r "$PROJECT_DIR/requirements-dev.txt"
elif [ -f "$PROJECT_DIR/requirements.txt" ]; then
  echo "[INFO] Instalando dependencias desde requirements.txt"
  "$VENV_PIP" install -r "$PROJECT_DIR/requirements.txt"
else
  echo "[ERROR] No existe requirements.txt ni requirements-dev.txt en $PROJECT_DIR" >&2
  exit 1
fi

echo "[INFO] Verificando imports mínimos"
"$VENV_PY" - <<'PY'
import importlib.util
mods = ["pandas", "openpyxl"]
missing = [m for m in mods if importlib.util.find_spec(m) is None]
if missing:
    raise SystemExit(f"Faltan módulos: {', '.join(missing)}")
print("Imports OK:", ", ".join(mods))
PY

echo "[OK] Entorno listo"
echo "source \"$VENV_DIR/bin/activate\""
