#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/alexi/Documents/GitHub/avance_curricular"
PY="/Users/alexi/Documents/GitHub/.venv/bin/python"
INPUT="/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx"
OUT="${ROOT}/resultados"

cd "$ROOT"

# Respaldo de seguridad de DURACION antes del loop.
mkdir -p control/backups
cp -f DURACION_ESTUDIOS.tsv "control/backups/DURACION_ESTUDIOS_backup_pre_loop_$(date +%Y-%m-%d_%H-%M-%S).tsv"

for i in 1 2 3 4 5; do
  echo "============================================================"
  echo "ITERACION $i"
  echo "============================================================"

  "$PY" scripts/remediar_duracion_desde_sin_match.py \
    --duracion DURACION_ESTUDIOS.tsv \
    --excel resultados/archivo_listo_para_sies.xlsx \
    --output-plan "control/reportes/plan_remediacion_duracion_desde_sin_match_iter${i}_auto.tsv"

  "$PY" scripts/auditoria_maestra.py \
    --ejecutar-pipeline \
    --input "$INPUT" \
    --output-dir "$OUT" \
    --anio 2026 \
    --sem 1 >/tmp/audit_iter_${i}.log 2>&1 || true

  tail -30 /tmp/audit_iter_${i}.log || true

  METRICAS=$("$PY" - << 'PY'
import pandas as pd

df = pd.read_excel('resultados/archivo_listo_para_sies.xlsx', sheet_name='ARCHIVO_LISTO_SUBIDA')
sin = df[df['COD_CAR'].isna()]
sin_match = sin[sin['SIES_MATCH_STATUS'] == 'SIN_MATCH_SIES']
print(f"COD_CAR_OK={df['COD_CAR'].notna().sum()} COD_CAR_NULL={len(sin)} SIN_MATCH_SIES={len(sin_match)}")
PY
)
  echo "$METRICAS"

  # Criterio de paro pragmático: sin match por debajo de 1000.
  if echo "$METRICAS" | grep -q 'SIN_MATCH_SIES='; then
    N=$(echo "$METRICAS" | sed -E 's/.*SIN_MATCH_SIES=([0-9]+).*/\1/')
    if [ "$N" -lt 1000 ]; then
      echo "Paro temprano: SIN_MATCH_SIES < 1000"
      break
    fi
  fi

done
