"""Consolida únicamente resultados agregados y referencias de esta auditoría."""
import json
import shutil
from pathlib import Path

OUT = Path(__file__).resolve().parent
DATA = OUT/'insumos'
DATA.mkdir(exist_ok=True)
AGENT = Path('/tmp/auditoria_diccionario_20261025_agent')
for name in ['resumen','combinaciones','combinaciones_periodo','carreras','anios','motivos','requisitos','nombres_catalogo']:
    shutil.copy2(AGENT/(name+'.json'), DATA/(name+'.json'))
shutil.copy2('/tmp/auditoria_diccionario_20261025_capas.json', DATA/'capas.json')
shutil.copy2('/tmp/auditoria_diccionario_20261025_gobierno.json', DATA/'gobierno.json')

# Se conserva el procedimiento de solo lectura con salidas persistentes agregadas.
script = (AGENT/'audit.py').read_text()
script = script.replace("O=Path('/tmp/auditoria_diccionario_20261025_agent'); O.mkdir(exist_ok=True)",
                        "O=Path(__file__).resolve().parent/'insumos'; O.mkdir(exist_ok=True)")
(OUT/'auditar_cobertura.py').write_text(script)
script = Path('/tmp/auditar_capas_diccionario_20261025.py').read_text()
script = script.replace("Path('/tmp/auditoria_diccionario_20261025_capas.json').write_text",
                        "(Path(__file__).resolve().parent/'insumos/capas.json').write_text")
(OUT/'auditar_capas.py').write_text(script)

summary = json.loads((DATA/'resumen.json').read_text())
capas = json.loads((DATA/'capas.json').read_text())
combos = json.loads((DATA/'combinaciones.json').read_text())
assert sum(r['observaciones'] for r in combos) == 24774
assert sum(r['pendientes'] for r in combos) == 3049
assert sum(r['pendientes']>0 for r in combos) == 63
assert sum(r['observaciones'] for r in capas['v17']['combinaciones_contextuales']) == 2854
assert sum(r['pendientes'] for r in capas['v17']['combinaciones_contextuales']) == 104
print(json.dumps({'agregados_preservados':True,'combinaciones_historico':len(combos),
                  'combinaciones_v17':len(capas['v17']['combinaciones_contextuales'])}))
