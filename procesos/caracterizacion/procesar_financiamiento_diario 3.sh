#!/usr/bin/env bash
set -Eeuo pipefail

REPO_DIR="/Users/alexi/Documents/GitHub/CARACTERIZACIÓN"
DEFAULT_BASE="/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/0_caracterizacion"
TZ_NAME="America/Santiago"

cd "$REPO_DIR"

ANIO="${1:-$(TZ="$TZ_NAME" date +%Y)}"
PERIODO="${2:-2}"
BASE_DIR="${CARACTERIZACION_ARCHIVO_BASE:-$DEFAULT_BASE}"

RUN_DATE="$(TZ="$TZ_NAME" date +%F)"
while true; do
  RUN_TIME="$(TZ="$TZ_NAME" date +%H%M%S)"
  RUN_DIR="$BASE_DIR/$RUN_DATE/${ANIO}_P${PERIODO}_${RUN_TIME}"
  if [[ ! -e "$RUN_DIR" ]]; then
    break
  fi
  sleep 1
done

mkdir -p "$RUN_DIR/01_ENTRADAS" "$RUN_DIR/02_SALIDAS" "$RUN_DIR/03_LOGS" "$RUN_DIR/04_AUDITORIA"

export CARACTERIZACION_RUN_DIR="$RUN_DIR"
export CARACTERIZACION_EXTERNAL_TEE=1

LOG="$RUN_DIR/03_LOGS/run_financiamiento_${ANIO}_P${PERIODO}_${RUN_DATE//-/}_${RUN_TIME}.log"
export CARACTERIZACION_LOG_PATH="$LOG"

set +e
printf "%s\n%s\n3\n\n" "$ANIO" "$PERIODO" |
  SOLO_GENERAR_FCU=0 \
  CARACTERIZACION_SKIP_FCU=1 \
  CARACTERIZACION_STOP_AFTER_FINANCIAMIENTO=1 \
  python3 caracterizacion.py 2>&1 |
  tee "$LOG"
status=${PIPESTATUS[1]}
set -e

entradas_archivadas="$(find "$RUN_DIR/01_ENTRADAS" -type f 2>/dev/null | wc -l | tr -d ' ')"
salidas_generadas="$(find "$RUN_DIR/02_SALIDAS" "$RUN_DIR/04_AUDITORIA" -type f 2>/dev/null | wc -l | tr -d ' ')"

echo "=================================================="
echo "PROCESAMIENTO FINALIZADO"
echo "Estado: $status"
echo "Carpeta: $RUN_DIR"
echo "Log: $LOG"
echo "Entradas archivadas: $entradas_archivadas"
echo "Salidas generadas: $salidas_generadas"
echo "=================================================="

exit "$status"
