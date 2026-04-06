#!/usr/bin/env bash
set -euo pipefail

ANIO="${1:-2026}"
SEM="${2:-1}"
INPUT="${3:-/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx}"
OUT="${4:-resultados}"

cd /Users/alexi/Documents/GitHub/avance_curricular
source /Users/alexi/Documents/GitHub/CV_ALEXI/.venv/bin/activate

mkdir -p "$OUT" "$OUT/SUBIDA"

printf "%s\n%s\n" "$ANIO" "$SEM" | python codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true --input "$INPUT" --output-dir "$OUT"

python3 scripts/marcar_alertas_codcar.py

open -a "Microsoft Excel" "$OUT/archivo_listo_para_sies.xlsx"

cp "$OUT/matricula_unificada_2026_pregrado.csv" "$OUT/SUBIDA/matricula_unificada_${ANIO}_S${SEM}_$(date +%Y%m%d_%H%M%S).csv"

echo "OK -> Excel abierto con filas rojas y CSV copiado en $OUT/SUBIDA/"
