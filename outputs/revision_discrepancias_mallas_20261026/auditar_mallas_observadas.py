"""Inventario agregado exploratorio; no modifica fuentes ni expone identidades."""
import collections, hashlib, json
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
metadata = json.loads((ROOT / 'outputs/qa_promedios_cobertura_20261026/RESULTADOS_AGREGADOS.json').read_text())
source = Path(metadata['fuentes']['v11_12166']['ruta'])
expected = metadata['fuentes']['v11_12166']['sha256']
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''): h.update(chunk)
    return h.hexdigest()
def clean(x):
    if x is None: return ''
    if isinstance(x, (int, float)) and x == int(x): return str(int(x))
    return str(x).strip().upper()
assert sha(source) == expected
wb = openpyxl.load_workbook(source, read_only=True, data_only=True)
rows = wb['Hoja1'].iter_rows(values_only=True)
headers = {clean(x): i for i, x in enumerate(next(rows)) if x is not None}
required = ['RUT','DIG','CODCLI','CODCARR','PLAN_DE_ESTUDIO','CODRAMO','RAMOEQUIV','ASIGNATURA','NIVEL','ANO','PERIODO','ESTADO_ACADEMICO']
assert set(required).issubset(headers)
groups = collections.defaultdict(list)
invalid = collections.Counter()
for row in rows:
    d = {k: clean(row[headers[k]]) for k in required}
    if not all(d[k] for k in ('RUT','DIG','CODCLI','CODCARR','PLAN_DE_ESTUDIO','CODRAMO')):
        invalid['identidad_plan_o_asignatura_incompleta'] += 1
        continue
    rut = d['RUT'].replace('.', '').replace(' ', '').lstrip('0') or '0'
    groups[(rut,d['DIG'],d['CODCLI'],d['CODCARR'],d['PLAN_DE_ESTUDIO'])].append(d)
wb.close()
assert sha(source) == expected
plans = collections.defaultdict(lambda: {'expedientes':set(),'cursos':collections.defaultdict(lambda: {'expedientes':set(),'niveles':set(),'nombres':set(),'equivalentes':set(),'periodos':set()})})
conflicted=0
for (rut, dv, codcli, career, plan), items in groups.items():
    states={d['ESTADO_ACADEMICO'] for d in items if d['ESTADO_ACADEMICO']}
    if 'TITULADO' not in states: continue
    if states != {'TITULADO'}:
        conflicted += 1
        continue
    # Identidad permanece en memoria. Los juegos por curso solo calculan recuentos.
    # CODCLI, carrera y plan distinguen expediente; la persona es el RUT+DV.
    key=(career,plan)
    # Evitar colapsar dos expedientes con CODCLI idéntico y RUT distinto.
    personkey=(rut,dv,codcli)
    plans[key]['expedientes'].add(personkey)
    for d in items:
        c=plans[key]['cursos'][d['CODRAMO']]
        c['expedientes'].add(personkey)
        for field,target in [('NIVEL','niveles'),('ASIGNATURA','nombres'),('RAMOEQUIV','equivalentes')]:
            if d[field]:c[target].add(d[field])
        if d['ANO'] and d['PERIODO']:c['periodos'].add((d['ANO'],d['PERIODO']))
result=[]
for (career,plan),value in sorted(plans.items()):
    courses=[]
    for code,c in sorted(value['cursos'].items()):
        courses.append({'codramo':code,'nombres_observados':sorted(c['nombres']),'ramos_equivalentes_observados':sorted(c['equivalentes']), 'niveles_observados':sorted(c['niveles']),'expedientes_con_asignatura':len(c['expedientes']),'periodos_observados':len(c['periodos']),'estado':'E: evidencia observada; no malla acreditada'})
    result.append({'carrera_umas':career,'plan_de_estudio':plan,'expedientes_titulado_extracto':len(value['expedientes']),'asignaturas_distintas_observadas':len(courses),'asignaturas_con_varios_niveles':sum(len(c['niveles_observados'])>1 for c in courses),'asignaturas':courses})
out={'clasificacion':'B observación; C agrupación; E completitud y titulación efectiva','fuente':{'ruta':str(source),'hoja':'Hoja1','sha256':expected},'metodo':'Agrupar RUT+DV+CODCLI+carrera+plan; seleccionar estado TITULADO del extracto; agrupar asignaturas y niveles observados. No incorpora identidades al resultado.','advertencia':'No demuestra titulación al término del último período, malla completa, requisitos ni cohorte de plan. No infiere asignación SIES; no altera indicadores.','filas_descartadas_llave_incompleta':invalid['identidad_plan_o_asignatura_incompleta'],'expedientes_con_estado_conflictivo_excluidos':conflicted,'planes_carrera_con_evidencia':len(result),'asignaturas_por_plan':sum(len(p['asignaturas']) for p in result),'planes':result}
(OUT/'MALLAS_OBSERVADAS_TITULADO_CANDIDATA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='planes'},ensure_ascii=False))
