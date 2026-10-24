#!/usr/bin/env bash
set -Eeuo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TZ_NAME="America/Santiago"
export PYTHONIOENCODING="utf-8"
export PYTHONUTF8=1

resolve_python_windows() {
  # El "python"/"python3" del PATH puede ser el stub roto de Microsoft Store
  # (no ejecuta nada, solo abre la Store) si la terminal es anterior a la
  # instalación real de Python o si el usuario aún no la tiene instalada.
  # Se prueba primero el PATH y, si falla, se buscan instalaciones conocidas
  # de python.org bajo el perfil del usuario, sin depender de reabrir la shell.
  for cand in python python3 py; do
    if command -v "$cand" >/dev/null 2>&1 && "$cand" -c "" >/dev/null 2>&1; then
      echo "$cand"
      return 0
    fi
  done
  local userprofile_u
  userprofile_u="$(cygpath -u "$USERPROFILE")"
  local found
  found="$(find "$userprofile_u/AppData/Local/Programs/Python" -maxdepth 1 -iname "python.exe" 2>/dev/null | sort -V | tail -n1)"
  if [[ -z "$found" ]]; then
    found="$(find "$userprofile_u/AppData/Local/Programs/Python" -mindepth 2 -maxdepth 2 -iname "python.exe" 2>/dev/null | sort -V | tail -n1)"
  fi
  if [[ -n "$found" ]]; then
    echo "$found"
    return 0
  fi
  return 1
}

case "$(uname -s)" in
  Darwin)
    DEFAULT_BASE="/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/0_caracterizacion"
    DEFAULT_DESKTOP_BASE="/Users/alexi/Desktop"
    PYTHON_BIN="python3"
    ;;
  MINGW*|MSYS*|CYGWIN*)
    DEFAULT_BASE="$(cygpath -u "$USERPROFILE")/OneDrive - Instituto Profesional San Sebastián/0_caracterizacion"
    # El Escritorio puede estar redirigido por OneDrive (Copia de seguridad de
    # carpetas conocidas), por lo que no siempre vive en $USERPROFILE/Desktop.
    # Se consulta la carpeta real vía PowerShell en lugar de asumir la ruta.
    WIN_DESKTOP_RAW="$(powershell.exe -NoProfile -Command '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; [Environment]::GetFolderPath("Desktop")' 2>/dev/null | tr -d '\r')"
    if [[ -n "$WIN_DESKTOP_RAW" ]]; then
      DEFAULT_DESKTOP_BASE="$(cygpath -u "$WIN_DESKTOP_RAW")"
    fi
    if [[ -z "$DEFAULT_DESKTOP_BASE" || ! -d "$DEFAULT_DESKTOP_BASE" ]]; then
      DEFAULT_DESKTOP_BASE="$(cygpath -u "$USERPROFILE")/Desktop"
    fi
    if ! PYTHON_BIN="$(resolve_python_windows)"; then
      echo "No se encontró una instalación real de Python (el 'python'/'python3' del PATH es el stub de Microsoft Store)." >&2
      echo "Instala Python desde https://www.python.org/downloads/ o con 'winget install -e --id Python.Python.3.12' y vuelve a intentar." >&2
      exit 1
    fi
    ;;
  *)
    echo "Sistema operativo no soportado: $(uname -s)" >&2
    exit 1
    ;;
esac

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
export CARACTERIZACION_DESKTOP_BASE="${CARACTERIZACION_DESKTOP_BASE:-$DEFAULT_DESKTOP_BASE}"

LOG="$RUN_DIR/03_LOGS/run_financiamiento_${ANIO}_P${PERIODO}_${RUN_DATE//-/}_${RUN_TIME}.log"
export CARACTERIZACION_LOG_PATH="$LOG"

# [H044][FUENTES] Fuentes congeladas y deterministicas, exclusivo 2026 P2.
# Para cualquier otro año/periodo el comportamiento historico (seleccion
# automatica desde Downloads via RUTA_MATRICULA/RUTA_INSCRITOS/RUTA_RESULTADOS
# o auto-deteccion) se mantiene sin cambios.
if [[ "$ANIO" == "2026" && "$PERIODO" == "2" ]]; then
  RESOLVER_FUENTES_P2="$REPO_DIR/scripts/gobernanza/resolver_fuentes_congeladas_2026_p2.py"
  set +e
  FUENTES_OUT="$("$PYTHON_BIN" "$RESOLVER_FUENTES_P2" 2>&1)"
  FUENTES_STATUS=$?
  set -e
  printf '%s\n' "$FUENTES_OUT" | tee -a "$LOG"
  if [[ $FUENTES_STATUS -ne 0 ]]; then
    echo "=================================================="
    echo "PROCESAMIENTO DETENIDO: fuentes congeladas 2026 P2 no validadas"
    echo "=================================================="
    exit "$FUENTES_STATUS"
  fi
  eval "$(printf '%s\n' "$FUENTES_OUT" | grep '^export ')"
  if [[ "${CARACTERIZACION_PREFLIGHT_FUENTES:-0}" == "1" ]]; then
    echo "PREFLIGHT=OK"
    exit 0
  fi
fi

if [[ "$ANIO" == "2027" && "$PERIODO" == "1" ]]; then
  set +e
  FUENTES_OUT="$("$PYTHON_BIN" "$REPO_DIR/scripts/gobernanza/resolver_fuentes_operativas.py" --anio 2027 --periodo 1 2>&1)"
  FUENTES_STATUS=$?
  set -e
  printf '%s\n' "$FUENTES_OUT" | tee -a "$LOG"
  if [[ $FUENTES_STATUS -ne 0 ]]; then
    exit "$FUENTES_STATUS"
  fi
  eval "$(printf '%s\n' "$FUENTES_OUT" | grep '^export ')"
  if [[ "${CARACTERIZACION_PREFLIGHT_FUENTES:-0}" == "1" ]]; then
    echo 'PREFLIGHT=OK'
    exit 0
  fi
  export ANIO_ANALISIS="$ANIO" PERIODO_ANALISIS="$PERIODO" COHORTES_ANALISIS="$ANIO"
fi

emit_pipeline_input() {
  if [[ "$ANIO" == "2027" && "$PERIODO" == "1" ]]; then
    return 0
  fi
  printf "%s\n%s\n3\n\n" "$ANIO" "$PERIODO"
}

set +e
PIPELINE_SCRIPT="caracterizacion.py"
if [[ "$ANIO" == "2027" && "$PERIODO" == "1" && "${CARACTERIZACION_RESULTADOS_SIN_RESPUESTAS:-0}" == "1" ]]; then
  PIPELINE_SCRIPT="caracterizacion_sin_respuestas.py"
elif [[ "$ANIO" == "2027" && "$PERIODO" == "1" ]]; then
  PIPELINE_SCRIPT="caracterizacion_financiamiento_2027.py"
fi
emit_pipeline_input |
  SOLO_GENERAR_FCU=0 \
  CARACTERIZACION_SKIP_FCU=1 \
  CARACTERIZACION_FILTRAR_ANO_INGRESO=1 \
  CARACTERIZACION_STOP_AFTER_FINANCIAMIENTO=1 \
  "$PYTHON_BIN" "$PIPELINE_SCRIPT" 2>&1 |
  tee -a "$LOG"
status=${PIPESTATUS[1]}
set -e

entradas_archivadas="$(find "$RUN_DIR/01_ENTRADAS" -type f 2>/dev/null | wc -l | tr -d ' ')"
salidas_generadas="$(find "$RUN_DIR/02_SALIDAS" -type f 2>/dev/null | wc -l | tr -d ' ')"
auditorias_generadas="$(find "$RUN_DIR/04_AUDITORIA" -type f 2>/dev/null | wc -l | tr -d ' ')"
analisis_generados="0"
if [[ "$ANIO" == "2027" && "$PERIODO" == "1" ]]; then
  analisis_generados="$(find "$RUN_DIR/05_ANALISIS" -type f 2>/dev/null | wc -l | tr -d ' ')"
fi

# [DIAGNOSTICO] Detalle de archivos/carpetas en OneDrive y en la copia de Escritorio,
# para poder ver de un vistazo cuantas carpetas quedaron generadas por esta corrida
# y detectar si la copia al Escritorio no se genera o queda duplicada.
MANIFEST="$RUN_DIR/04_AUDITORIA/manifest_ejecucion.json"
DESKTOP_BASE="$CARACTERIZACION_DESKTOP_BASE"
DESKTOP_DIR=""
COPIA_ESTADO="NO_APLICA"
if [[ -f "$MANIFEST" ]] && command -v jq >/dev/null 2>&1; then
  DESKTOP_DIR="$(jq -r '.directorio_escritorio // empty' "$MANIFEST" 2>/dev/null)"
  COPIA_ESTADO="$(jq -r '.copia_escritorio_estado // "NO_APLICA"' "$MANIFEST" 2>/dev/null)"
fi

onedrive_archivos="$(find "$RUN_DIR" -type f 2>/dev/null | wc -l | tr -d ' ')"
onedrive_carpetas="$(find "$RUN_DIR" -type d 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')"

if [[ -n "$DESKTOP_DIR" && -d "$DESKTOP_DIR" ]]; then
  desktop_archivos="$(find "$DESKTOP_DIR" -type f 2>/dev/null | wc -l | tr -d ' ')"
  desktop_carpetas="$(find "$DESKTOP_DIR" -type d 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')"
else
  desktop_archivos="0"
  desktop_carpetas="0"
fi

corridas_hoy_onedrive="$(find "$BASE_DIR/$RUN_DATE" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')"
copias_totales_escritorio="$(find "$DESKTOP_BASE" -mindepth 1 -maxdepth 1 -type d -name "Caracterizacion_*" 2>/dev/null | wc -l | tr -d ' ')"

echo "=================================================="
if [[ "$status" == "0" ]]; then
  echo "PROCESAMIENTO FINALIZADO CORRECTAMENTE"
else
  echo "PROCESAMIENTO INTERRUMPIDO POR ERROR"
fi
echo "Estado: $status"
echo "Carpeta OneDrive: $RUN_DIR"
echo "  Archivos: $onedrive_archivos | Subcarpetas: $onedrive_carpetas"
echo "Copia Escritorio: ${DESKTOP_DIR:-(no generada)} (estado: $COPIA_ESTADO)"
echo "  Archivos: $desktop_archivos | Subcarpetas: $desktop_carpetas"
echo "Log: $LOG"
echo "Entradas archivadas: $entradas_archivadas"
echo "Informes y salidas operativas: $salidas_generadas"
echo "Archivos de auditoria: $auditorias_generadas"
if [[ "$ANIO" == "2027" && "$PERIODO" == "1" ]]; then
  echo "Archivos de analisis interno (05_ANALISIS): $analisis_generados"
fi
echo "--------------------------------------------------"
echo "Corridas registradas hoy en OneDrive ($RUN_DATE): $corridas_hoy_onedrive"
echo "Copias 'Caracterizacion_*' totales en Escritorio (todas las fechas): $copias_totales_escritorio"
echo "=================================================="

exit "$status"
