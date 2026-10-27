"""Inspecciona la estructura interna de dos respaldos XLSX sin extraer filas personales."""
import hashlib
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
prior = Path('/Users/alexi/.local/share/ipss/busqueda_desempate_titulacion_20261026/RESULTADO_SIN_IDENTIFICADORES.json')
sources = json.loads(prior.read_text())['fuentes'][1:3]

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()

results = []
for source in sources:
    path = Path(source['ruta'])
    before = sha(path)
    assert before == source['sha256']
    data = {'ruta': str(path), 'sha256': before, 'custom_xml': [], 'pivot_cache': [], 'otros_componentes': []}
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        data['otros_componentes'] = [n for n in names if n.startswith(('xl/embeddings/', 'xl/externalLinks/', 'xl/queryTables/')) or n.endswith(('vbaProject.bin', 'connections.xml'))]
        for name in names:
            if name.startswith('customXml/item') and name.endswith('.xml'):
                raw = archive.read(name)
                root = ET.fromstring(raw)
                terms = ['TRACE_SCORE_CANDIDATO', 'TRACE_REASONS_CANDIDATO', '2130', 'CODCLI', 'PLAN_DE_ESTUDIO', 'desempate']
                data['custom_xml'].append({'componente': name, 'raiz': root.tag, 'bytes': len(raw),
                                           'terminos_en_bytes': [term for term in terms if term.encode('utf-8') in raw]})
            if name.startswith('xl/pivotCache/pivotCacheDefinition') and name.endswith('.xml'):
                root = ET.fromstring(archive.read(name))
                fields = [node.get('name') for node in root.iter() if node.tag.endswith('}cacheField')]
                data['pivot_cache'].append({'componente': name, 'campos': fields,
                                            'campos_codcli_plan': [x for x in fields if x and ('CODCLI' in x.upper() or 'PLAN' in x.upper())]})
    assert sha(path) == before
    results.append(data)

payload = {'clasificacion': 'B componentes; C inspección estructural; E evidencia no recuperada',
           'fuentes': results, 'limites': 'No se inspeccionaron registros personales de la tabla dinámica; búsqueda literal acotada a componentes indicados. No prueba ausencia en otros archivos.'}
(OUT / 'RESULTADO_AGREGADO.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
print(json.dumps([{'archivo': Path(x['ruta']).name, 'custom_xml': len(x['custom_xml']),
                   'pivot': len(x['pivot_cache']), 'otros_componentes': len(x['otros_componentes']),
                   'terminos': sum(len(y['terminos_en_bytes']) for y in x['custom_xml']),
                   'campos_codcli_plan': [p['campos_codcli_plan'] for p in x['pivot_cache']]} for x in results], ensure_ascii=False))
