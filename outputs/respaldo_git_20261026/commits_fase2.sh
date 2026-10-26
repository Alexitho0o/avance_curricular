#!/usr/bin/env bash
# Respaldo gobernado en Git · Fase 2/5 (v10) · 26-10-2026
#   bash commits_fase2.sh --revisar     # solo muestra
#   bash commits_fase2.sh --ejecutar    # 2 commits locales, sin push
set -euo pipefail
REPO="$HOME/Documents/GitHub/avance_curricular"; DIR="$REPO/outputs/respaldo_git_20261026"; MODO="${1:-}"
cd "$REPO"
[[ "$(git branch --show-current)" == "feature/ire-2026" ]] || { echo "ALTO: rama distinta"; exit 1; }
[[ "$(git rev-parse --short HEAD)" == "68ab3f9" ]] || { echo "ALTO: HEAD distinto de 68ab3f9"; exit 1; }
git diff --cached --quiet || { echo "ALTO: hay cambios preparados"; exit 1; }
ls .git/*.lock >/dev/null 2>&1 && { echo "ALTO: hay .lock en .git"; exit 1; }
msg() {
  case "$1" in
    H) printf '%s' "diccionario SIES: activa v10 (27 contextos T2/T3 2025 respaldados por la MU 2026)

D: Alexi aprobó la decisión corregida (31 → 27) con control obligatorio de año de ingreso a la carrera.
C: 24.774 consultas vs v9, exactamente 27 cambian (E→D); tres consumidores iguales; control T1 sin diferencias.
Descriptor con rutas del Mac (corrige la errata de v9). Pendientes del seguimiento 78 → 51." ;;
    I) printf '%s' "fase 2: clasificación y propuesta de los 78 pendientes, candidata v10, procedencia y copia de la base v10

C: clasificación (A jornada 47, B cambio de carrera 28, C sin MU 3); cargas SIES 2025 sin código del nuevo contexto;
MU 2026 respalda 41; diagnóstico D2 y control de ingreso; salidas agregadas, sin identificadores." ;;
  esac
}
total=0
for T in H I; do
  L="$DIR/lista_$T.nul"; n=$(tr -cd '\0' < "$L" | wc -c | tr -d ' '); total=$((total+n))
  if [[ "$MODO" == "--ejecutar" ]]; then
    git add --pathspec-from-file="$L" --pathspec-file-nul
    git diff --cached --quiet && { echo "commit $T: nada nuevo"; continue; }
    git commit -q -m "$(msg "$T")" && echo "commit $T: $n archivos → $(git rev-parse --short HEAD)"
  else
    echo "[revisión] commit $T: $n archivos — $(msg "$T" | head -1)"
  fi
done
echo "archivos en commits: $total"
if [[ "$MODO" == "--ejecutar" ]]; then
  git log --oneline -4; echo "--- cambios que quedan sin commit: $(git status --porcelain | wc -l | tr -d ' ')"
  echo "Sin push. Para publicar: git push origin feature/ire-2026"
fi
