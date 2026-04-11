#!/usr/bin/env bash
set -euo pipefail

show_help() {
  cat <<'EOF'
Uso:
  OUTPUT_DIR="resultados" bash scripts/validate_oficial.sh
  bash scripts/validate_oficial.sh --help

Variables:
  OUTPUT_DIR  Directorio de salida relativo o absoluto. Default: resultados
EOF
}

case "${1:-}" in
  -h|--help)
    show_help
    exit 0
    ;;
esac

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

OUTPUT_DIR="${OUTPUT_DIR:-resultados}"
CSV_PATH="${OUTPUT_DIR}/matricula_unificada_2026_pregrado.csv"
XLSX_PATH="${OUTPUT_DIR}/archivo_listo_para_sies.xlsx"

if [[ ! -f "${CSV_PATH}" || ! -f "${XLSX_PATH}" ]]; then
  echo "[MU2026] ERROR: faltan artefactos oficiales en ${OUTPUT_DIR}." >&2
  echo "[MU2026] Se esperaba encontrar:" >&2
  echo "[MU2026]   - ${XLSX_PATH}" >&2
  echo "[MU2026]   - ${CSV_PATH}" >&2
  echo "[MU2026] Ejecuta primero el flujo oficial." >&2
  exit 2
fi

echo "[MU2026] Repo root: ${REPO_ROOT}"
echo "[MU2026] Ejecutando validación oficial..."
echo "[MU2026] OUTPUT_DIR=${OUTPUT_DIR}"

python3 qa_checks.py \
  --output-dir "${OUTPUT_DIR}" \
  --fase3-control-dir "control" \
  --fase6-control-dir "control"

python3 scripts/auditoria_maestra.py \
  --solo-validar \
  --output-dir "${OUTPUT_DIR}"

echo "[MU2026] Validación oficial finalizada."
