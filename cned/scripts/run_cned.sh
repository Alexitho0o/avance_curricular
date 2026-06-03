#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}"

PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"
if [[ ! -x "${PYTHON_BIN}" ]]; then
  PYTHON_BIN="python"
fi

mkdir -p cned/resultados/reportes
LOG_PATH="cned/resultados/reportes/run_cned_$(date +%Y%m%d_%H%M%S).log"

{
  echo "======================================================================"
  echo "RUN CNED - EJECUCION BASE"
  echo "======================================================================"
  echo "Repo: ${REPO_ROOT}"
  echo "Nota: ejecucion base sin insumos CNED cargados."
  echo
  echo "[1/3] Auditoria"
  "${PYTHON_BIN}" cned/scripts/auditar_cned.py
  echo
  echo "[2/3] Validacion"
  "${PYTHON_BIN}" cned/scripts/validar_cned.py
  echo
  echo "[3/3] Generacion"
  "${PYTHON_BIN}" cned/scripts/generar_archivo_cned.py
  echo
  echo "RUN CNED finalizado correctamente como ejecucion base."
} 2>&1 | tee "${LOG_PATH}"

echo "Log: ${LOG_PATH}"
