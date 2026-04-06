#!/usr/bin/env bash
set -euo pipefail

show_help() {
  cat <<'EOF'
Uso:
  INPUT_XLSX="/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx" OUTPUT_DIR="resultados" bash scripts/run_oficial.sh
  bash scripts/run_oficial.sh --help

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

OUTPUT_DIR="${OUTPUT_DIR:-resultados}"

if [[ -z "${INPUT_XLSX:-}" ]]; then
  echo "[MU2026] ERROR: falta INPUT_XLSX." >&2
  echo "[MU2026] Define INPUT_XLSX con la ruta del Excel externo antes de ejecutar." >&2
  show_help >&2
  exit 2
fi

if [[ ! -f "${INPUT_XLSX}" ]]; then
  echo "[MU2026] ERROR: INPUT_XLSX no existe: ${INPUT_XLSX}" >&2
  exit 2
fi

echo "[MU2026] Repo root: ${REPO_ROOT}"
echo "[MU2026] Compilando catálogo canónico SIES (SOURCE_KEY_3)..."
python3 scripts/compile_puente_sies_compilado.py \
  --duracion "DURACION_ESTUDIOS.tsv" \
  --output "control/catalogos/PUENTE_SIES_COMPILADO.tsv" \
  --summary-json "control/reportes/reporte_compilacion_puente_sies.json"

echo "[MU2026] Ejecutando flujo oficial de Matrícula Unificada 2026..."
echo "[MU2026] INPUT_XLSX=${INPUT_XLSX}"
echo "[MU2026] OUTPUT_DIR=${OUTPUT_DIR}"

python3 codigo_gobernanza_v2.py \
  --input "${INPUT_XLSX}" \
  --output-dir "${OUTPUT_DIR}" \
  --proceso matricula \
  --usar-gobernanza-v2 true

echo "[MU2026] Ejecución oficial finalizada."
