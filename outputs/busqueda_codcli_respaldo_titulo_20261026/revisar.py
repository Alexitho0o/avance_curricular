"""Busca CODCLI del caso en libro auxiliar, sin filtrar previamente por RUT."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
private = Path('/Users/alexi/.local/share/ipss/revision_21_ramos_4_expedientes_20261026/DETALLE_CUATRO_CASOS_V2.json')
prior = json.loads((ROOT / 'outputs/busqueda_respaldos_segunda_carga_20261026/RESULTADO_AGREGADO.json').read_text())
source = Path(prior['libro_auxiliar']['ruta'])
expected = prior['libro_auxiliar']['sha256']

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''): h.update(block)
    return h.hexdigest()

def text(x):
    if isinstance(x, float) and x.is_integer(): return str(int(x))
    return str(x or '').strip().upper()

cases = json.loads(private.read_text())
selected = [c for c in cases if any(x['carrera'] == 'TCRE' for x in c['contextos_v11'])]
assert len(selected) == 1
case = selected[0]
targets = {text(r['CODCLI']) for r in case['datosalumnos'] if r['CODCLI']}
targets.update(text(r['CODCLI']) for r in case['contextos_v11'] if r['CODCLI'])
assert len(targets) == 3
assert sha(source) == expected
w = openpyxl.load_workbook(source, read_only=True, data_only=True)
results = []
for sheet in w:
    it = sheet.iter_rows(values_only=True)
    header = [text(v) for v in next(it)]
    hits = Counter()
    distinct = set()
    n = 0
    for row in it:
        n += 1
        found = {text(v) for v in row if text(v) in targets}
        if not found: continue
        hits['filas_con_codcli_en_cualquier_celda'] += 1
        distinct |= found
        if 'CODCLI' in header and text(row[header.index('CODCLI')]) in targets:
            hits['filas_con_codcli_en_columna_codcli'] += 1
        if any('TITUL' in h for h in header): hits['filas_en_hoja_con_columna_titulacion'] += 1
    results.append({'hoja': sheet.title, 'filas_datos': n, 'columnas': len(header),
                    'contiene_columna_codcli': 'CODCLI' in header,
                    'contiene_columna_plan': any('PLAN' in x for x in header),
                    'contiene_columna_titulo': any('TITUL' in x for x in header),
                    'codcli_objetivo_distintos_localizados': len(distinct), 'conteos': dict(hits)})
w.close()
assert sha(source) == expected
out = {'clasificacion': 'B fuente; C búsqueda exacta; E atribución',
       'fuente': {'ruta': str(source), 'sha256': expected}, 'codcli_objetivo_distintos': len(targets),
       'hojas': results,
       'alcance': 'Todos los valores de las hojas se compararon con tres CODCLI conocidos; sin filtro previo por documento. Coincidencia no acreditaría por sí sola un vínculo del título con plan.',
       'conservacion': 'Fuentes y denominadores intactos. Sin commit ni push.'}
payload = json.dumps(out, ensure_ascii=False, indent=2) + '\n'
assert all(t not in payload for t in targets)
assert all(c['RUT'].split('-')[0] not in payload for c in cases)
(OUT / 'RESULTADO_AGREGADO.json').write_text(payload)
print(json.dumps(out, ensure_ascii=False))
