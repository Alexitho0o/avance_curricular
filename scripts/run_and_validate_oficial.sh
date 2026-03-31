#!/usr/bin/env bash
set -euo pipefail

show_help() {
  cat <<'EOF'
Uso:
  INPUT_XLSX="/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx" OUTPUT_DIR="resultados" bash scripts/run_and_validate_oficial.sh
  bash scripts/run_and_validate_oficial.sh --help

Variables:
  INPUT_XLSX  Ruta al Excel externo de entrada. Obligatoria.
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

export OUTPUT_DIR="${OUTPUT_DIR:-resultados}"

if [[ -n "${INPUT_XLSX:-}" ]]; then
  export INPUT_XLSX
fi

echo "[MU2026] Ejecutando secuencia oficial: run + validate"
"${SCRIPT_DIR}/run_oficial.sh"
"${SCRIPT_DIR}/validate_oficial.sh"
echo "[MU2026] Secuencia oficial finalizada."
