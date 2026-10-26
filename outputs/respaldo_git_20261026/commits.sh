#!/usr/bin/env bash
# Respaldo gobernado en Git · Fase 1/5 · 26-10-2026
# Uso (desde cualquier carpeta):
#   bash commits.sh --revisar                 # solo muestra qué haría; no cambia nada
#   bash commits.sh --ejecutar                # crea los 7 commits locales (sin push)
#   bash commits.sh --ejecutar --sin-historicos   # omite el commit G (822 resultados del 21–24 oct)
set -euo pipefail
REPO="$HOME/Documents/GitHub/avance_curricular"
DIR="$REPO/outputs/respaldo_git_20261026"
MODO="${1:-}"; SIN_G="${2:-}"
cd "$REPO"

[[ "$(git branch --show-current)" == "feature/ire-2026" ]] || { echo "ALTO: rama distinta de feature/ire-2026"; exit 1; }
[[ "$(git rev-parse --short HEAD)" == "8e2fb85" ]] || { echo "ALTO: HEAD distinto de 8e2fb85"; exit 1; }
git diff --cached --quiet || { echo "ALTO: ya hay cambios preparados (staged); no se mezclan"; exit 1; }
ls .git/*.lock >/dev/null 2>&1 && { echo "ALTO: hay archivos .lock en .git"; exit 1; }

# macOS trae bash 3.2 (sin arreglos asociativos): mensajes vía case
msg() {
  case "$1" in
    A) printf '%s' "diccionario SIES: activa v9 (21 correspondencias internas V3), errata de rutas y catálogo de fuentes

D: Alexi aprobó integrar las 21 correspondencias de V5 hoja 1 y promover v9.
C: 24.774 consultas vs v8, exactamente 21 cambian (E→D); tres consumidores iguales.
Agrega recursos_comunes.catalogo_fuentes en PROYECTO_IPSS.json." ;;
    B) printf '%s' "auditoría y conciliación UMAS–SIES 24–26 oct: decisiones A, v9, regla T1, procedencia y consolidación

D: opción A (99 pendientes de código; 149 excepciones al ancla T1; 143 de V5 retirado).
D: regla de herencia T1 estricta solo como control (933/933, 0 diferencias).
B/C: procedencia de 127 fuentes; CSV SIES 2007–2026 verificado (IPSS 2026 = 3.425).
C: consolidación de bases en OneDrive con catálogo de hashes. Salidas agregadas, sin identificadores." ;;
    C) printf '%s' "scripts y procesos de retención intermedia, conciliación y diccionario (21–26 oct)" ;;
    D) printf '%s' "datos y reglas de negocio gobernados (estados UMAS, MU 2027, reglas)" ;;
    E) printf '%s' "documentación y especificaciones de revisiones del diccionario" ;;
    F) printf '%s' "oferta académica 2027: fuentes, validaciones, maquetas y entrega etapas 1–2" ;;
    G) printf '%s' "resultados históricos de retención y revisiones 21–24 oct (agregados, sin identificadores)" ;;
  esac
}

total=0
for T in A B C D E F G; do
  [[ "$T" == "G" && "$SIN_G" == "--sin-historicos" ]] && { echo "G omitido por --sin-historicos"; continue; }
  LISTA="$DIR/lista_$T.nul"
  n=$(tr -cd '\0' < "$LISTA" | wc -c | tr -d ' ')
  total=$((total+n))
  if [[ "$MODO" == "--ejecutar" ]]; then
    git add --pathspec-from-file="$LISTA" --pathspec-file-nul
    git diff --cached --quiet && { echo "commit $T: nada nuevo que respaldar"; continue; }
    git commit -q -m "$(msg "$T")" && echo "commit $T: $n archivos → $(git rev-parse --short HEAD)"
  else
    echo "[revisión] commit $T: $n archivos — $(msg "$T" | head -1)"
  fi
done
echo "archivos en commits: $total"
if [[ "$MODO" == "--ejecutar" ]]; then
  echo "--- últimos commits"; git log --oneline -8
  echo "--- cambios que quedan sin commit: $(git status --porcelain | wc -l | tr -d ' ')"
  echo "Sin push. Para publicar: git push origin feature/ire-2026"
fi
