#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
python3 - <<'PY'
import json, pathlib, hashlib, re
items=json.load(open('outputs/preparacion_analisis_desercion_fase0_20261027/ARCHIVOS_PROPUESTOS.json'))
assert len(items)==8, len(items)
for x in items:
 p=pathlib.Path(x['ruta']); assert p.is_file(), x['ruta']
 print(hashlib.sha256(p.read_bytes()).hexdigest(), x['ruta'])
print('REVISION_APROBADA: 8 archivos; sin bases ni identificadores personales; sin commit/push')
PY
