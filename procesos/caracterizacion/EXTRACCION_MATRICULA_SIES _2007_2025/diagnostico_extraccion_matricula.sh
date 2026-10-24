#!/usr/bin/env bash
# Diagnóstico inicial y ejecución controlada del subproyecto
# EXTRACCION_MATRICULA_SIES_2007_2025
# Compatible con macOS/Linux. Diseñado como paso previo al parche del Python.

set -euo pipefail

DEFAULT_PROJECT_DIR="/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/EXTRACCION_MATRICULA_SIES _2007_2025"
PROJECT_DIR="${1:-${PROJECT_DIR_OVERRIDE:-$DEFAULT_PROJECT_DIR}}"

SCRIPT_NAME="codigo_extraccion_matricula.py"
DATA_DIR_NAME="datos"
LOG_DIR_NAME="logs"

log() {
  printf '%s\n' "$*"
}

fail() {
  printf '[ERROR] %s\n' "$*" >&2
  exit 1
}

timestamp() {
  date '+%Y%m%d_%H%M%S'
}

human_size() {
  local bytes="$1"
  if [ "$bytes" -lt 1024 ]; then
    printf '%s B' "$bytes"
  elif [ "$bytes" -lt 1048576 ]; then
    awk -v b="$bytes" 'BEGIN { printf "%.2f KiB", b / 1024 }'
  elif [ "$bytes" -lt 1073741824 ]; then
    awk -v b="$bytes" 'BEGIN { printf "%.2f MiB", b / 1048576 }'
  else
    awk -v b="$bytes" 'BEGIN { printf "%.2f GiB", b / 1073741824 }'
  fi
}

resolve_python() {
  local project_venv="$PROJECT_DIR/.venv/bin/python"
  local repo_venv="/Users/alexi/Documents/GitHub/.venv/bin/python"

  if [ -x "$project_venv" ]; then
    printf '%s\n' "$project_venv"
    return 0
  fi

  if [ -x "$repo_venv" ]; then
    printf '%s\n' "$repo_venv"
    return 0
  fi

  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi

  return 1
}

log "======================================================================"
log "DIAGNÓSTICO INICIAL · EXTRACCION_MATRICULA_SIES_2007_2025"
log "======================================================================"
log "Proyecto: $PROJECT_DIR"

[ -d "$PROJECT_DIR" ] || fail "No existe el directorio del proyecto: $PROJECT_DIR"

SCRIPT_PATH="$PROJECT_DIR/$SCRIPT_NAME"
[ -f "$SCRIPT_PATH" ] || fail "No existe el script principal: $SCRIPT_PATH"

DATA_DIR="$PROJECT_DIR/$DATA_DIR_NAME"
[ -d "$DATA_DIR" ] || fail "No existe la carpeta de datos: $DATA_DIR"

LOG_DIR="$PROJECT_DIR/$LOG_DIR_NAME"
mkdir -p "$LOG_DIR"

PYTHON_BIN="$(resolve_python)" || fail "No se encontró un intérprete Python utilizable (.venv del proyecto, .venv del repositorio o python3)."

RUN_TS="$(timestamp)"
LOG_FILE="$LOG_DIR/diagnostico_extraccion_matricula_${RUN_TS}.log"

log "Script principal : $SCRIPT_PATH"
log "Carpeta de datos : $DATA_DIR"
log "Carpeta de logs  : $LOG_DIR"
log "Python detectado : $PYTHON_BIN"
log "Log de ejecución : $LOG_FILE"
log "----------------------------------------------------------------------"

CSV_LIST="$(find "$DATA_DIR" -type f \( -name '*.csv' -o -name '*.CSV' \) -print | LC_ALL=C sort)"

if [ -z "$CSV_LIST" ]; then
  fail "No se encontraron archivos CSV dentro de $DATA_DIR"
fi

CSV_COUNT="$(printf '%s\n' "$CSV_LIST" | wc -l | tr -d ' ')"

log "CSV detectados: $CSV_COUNT"
log "Listado de archivos:"
while IFS= read -r csv_file; do
  [ -n "$csv_file" ] || continue
  log "  - $(basename "$csv_file")"
done <<EOF2
$CSV_LIST
EOF2

log "----------------------------------------------------------------------"
log "PREVIEW DE ARCHIVOS"
log "----------------------------------------------------------------------"

while IFS= read -r csv_file; do
  [ -n "$csv_file" ] || continue

  file_name="$(basename "$csv_file")"
  byte_size="$(wc -c < "$csv_file" | tr -d ' ')"
  pretty_size="$(human_size "$byte_size")"

  log "[ARCHIVO] $file_name"
  log "  Ruta   : $csv_file"
  log "  Tamaño : $byte_size bytes ($pretty_size)"
  log "  Primeras 3 líneas crudas:"

  if [ -s "$csv_file" ]; then
    sed -n '1,3p' "$csv_file" | while IFS= read -r line; do
      printf '    %s\n' "$line"
    done
  else
    log "    [archivo vacío]"
  fi

  log "----------------------------------------------------------------------"
done <<EOF3
$CSV_LIST
EOF3

log "EJECUCIÓN CONTROLADA DEL SCRIPT PRINCIPAL"
log "----------------------------------------------------------------------"
log "La salida completa se guardará en:"
log "  $LOG_FILE"
log "----------------------------------------------------------------------"

set +e
(
  cd "$PROJECT_DIR"
  "$PYTHON_BIN" "$SCRIPT_PATH"
) 2>&1 | tee "$LOG_FILE"
PY_EXIT=${PIPESTATUS[0]}
set -e

log "----------------------------------------------------------------------"
if [ "$PY_EXIT" -eq 0 ]; then
  log "[OK] La ejecución del script finalizó sin error."
else
  log "[WARNING] El script principal terminó con error."
  log "[WARNING] Código de salida: $PY_EXIT"
fi

log "Log final: $LOG_FILE"
log "Diagnóstico inicial completado."

exit "$PY_EXIT"
