"""Cruza CODCLI exacto con fuentes de plan; no usa RUT ni exporta identificadores."""
import collections
import hashlib
import json
import unicodedata
from pathlib import Path
import openpyxl

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
PRIVATE = Path('/Users/alexi/.local/share/ipss/revision_21_ramos_4_expedientes_20261026/DETALLE_CUATRO_CASOS_V2.json')
cloud = next(p for p in Path('/Users/alexi/Library/CloudStorage').iterdir() if unicodedata.normalize('NFC', p.name)=='OneDrive-InstitutoProfesionalSanSebastián')
base = cloud / '0 BASES DE DATOS'
unified = next(base.glob('*/DATOSDEALUMNOS ORIGEN DE LOS DATOS2025.xlsx'))
prior = json.loads((ROOT/'outputs/busqueda_bitacora_mallas_20261026/RESULTADO_AGREGADO.json').read_text())
prom_meta = json.loads((ROOT/'outputs/revision_21_ramos_4_expedientes_20261026/RESULTADO_AGREGADO.json').read_text())['fuentes']['promedios']

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()
def norm(v):
    if isinstance(v,float) and v.is_integer(): return str(int(v))
    return str(v or '').strip().upper()
def records(path, sheet, header_row):
    w = openpyxl.load_workbook(path, read_only=True, data_only=True)
    it = w[sheet].iter_rows(values_only=True)
    for _ in range(header_row-1): next(it)
    header = [norm(x) for x in next(it)]
    yield header, it
    w.close()

cases = json.loads(PRIVATE.read_text())
case = next(c for c in cases if any(x['carrera']=='TCRE' for x in c['contextos_v11']))
targets = {norm(x['CODCLI']) for x in case['datosalumnos'] if x['CODCLI']}
assert len(targets)==3
digest = sha(unified)
assert digest == '63c5cbc05494e4ac36b97041656ded478cf8deab2f562223e851d1cb2a2ef2f1'
matched = {}
for h,it in records(unified,'BBDD',1):
    assert {'CODCLI','CODCARPR'}.issubset(h)
    for row in it:
        cli = norm(row[h.index('CODCLI')]); career = norm(row[h.index('CODCARPR')])
        if cli in targets:
            assert cli not in matched or matched[cli] == career
            matched[cli] = career
assert sha(unified)==digest and len(matched)==2
sources=[{'ruta':str(unified),'sha256':digest,'hoja':'BBDD','codcli_conocidos':len(targets),'codcli_coincidentes':len(matched)}]

files = [(Path(x['archivo']),x['hoja'],x['fila_encabezado'],x['sha256'], 'CODIGO_PLAN_ESTUDIO') for x in prior['fuentes']]
files.append((Path(prom_meta['ruta']),prom_meta['hoja'],1,prom_meta['sha256'],'PLAN_DE_ESTUDIO'))
for path,sheet,header_row,expected,plan_field in files:
    before=sha(path); assert before==expected
    hits=collections.Counter(); distinct=collections.defaultdict(set); total=0
    for h,it in records(path,sheet,header_row):
        assert 'CODCLI' in h and plan_field in h
        for row in it:
            cli=norm(row[h.index('CODCLI')])
            if cli not in matched: continue
            total+=1;plan=norm(row[h.index(plan_field)]); career=matched[cli]
            period=norm(row[h.index('PERIODO')]) if 'PERIODO' in h else ''
            year=norm(row[h.index('ANO')]) if 'ANO' in h else ''
            hits[(career,plan,year,period)]+=1;distinct[(career,plan)].add(cli)
    assert sha(path)==before
    sources.append({'ruta':str(path),'sha256':before,'hoja':sheet,'fila_encabezado':header_row,
                    'codcli_distintos_con_match':len(set().union(*distinct.values())) if distinct else 0,
                    'filas_coincidentes':total,
                    'pares_carrera_plan':[{'carrera':a,'plan':b,'expedientes':len(v)} for (a,b),v in sorted(distinct.items())],
                    'periodos':[{'carrera':a,'plan':b,'anio':y,'periodo':p,'filas':n} for (a,b,y,p),n in sorted(hits.items())]})

out={'clasificacion':'B fuente; C cruce por CODCLI exacto; E titulo y vigencia',
     'metodo':'Se seleccionan dos CODCLI presentes en BBDD y se cruzan sin condicionar por RUT en todas las filas de las cuatro fuentes de actividad.',
     'fuentes':sources,'limites':['CODCLI exacto documenta coincidencia de expediente; no confirma por sí solo identidad de propietario en cada fuente.',
         'La actividad de asignaturas y un estado académico no son un registro formal de título asignado a un plan.',
         'El periodo de actividad y fecha de reporte no acreditan la fecha efectiva del cambio de plan.',
         'No se comparan ni modifican bases, tasas o denominadores; no se infiere fórmula del puntaje 2130.']}
payload=json.dumps(out,ensure_ascii=False,indent=2)+'\n'
for c in cases:
    assert c['RUT'].split('-')[0] not in payload
    for x in c['datosalumnos']: assert norm(x['CODCLI']) not in payload
(OUT/'RESULTADO_AGREGADO.json').write_text(payload)
print(json.dumps([{'archivo':Path(s['ruta']).name,'codcli_match':s.get('codcli_distintos_con_match',s.get('codcli_coincidentes')),'filas':s.get('filas_coincidentes'),'carrera_plan':s.get('pares_carrera_plan')} for s in sources],ensure_ascii=False))
