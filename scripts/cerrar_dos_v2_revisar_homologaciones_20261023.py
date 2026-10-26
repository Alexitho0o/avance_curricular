"""Cierre interno acotado autorizado; revisión exacta de reconocimientos, sin alterar fuentes."""
import copy
import datetime
import hashlib
import json
import os
import subprocess
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo

import openpyxl

R = Path(__file__).resolve().parents[1]
P = Path.home() / '.local/share/ipss'
now = datetime.datetime.now(ZoneInfo('America/Santiago'))
stamp = now.strftime('%Y%m%d_%H%M%S')
O = R / 'outputs' / ('cierre_dos_v2_homologaciones_' + stamp)
Q = P / ('cierre_dos_v2_homologaciones_' + stamp)
assert subprocess.run(['git', '-C', str(P), 'rev-parse', '--show-toplevel'], capture_output=True).returncode != 0
os.umask(0o077)
O.mkdir(); Q.mkdir(mode=0o700)
H = {}

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def source(p, expected=None):
    p = Path(p); h = sha(p)
    assert expected is None or h == expected, 'Hash no coincide: ' + str(p)
    H[str(p)] = h
    return p

def load(p, expected=None):
    return json.loads(source(p, expected).read_text())

def dump(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + '\n')

def git():
    return {k: subprocess.check_output(['git', '-C', str(R), *args], text=True).strip()
            for k, args in [('rama', ['branch', '--show-current']), ('HEAD', ['rev-parse', 'HEAD']),
                            ('remotos', ['remote', '-v']), ('status', ['status', '--short'])]}

def val(v):
    return '' if v is None else str(int(v)) if isinstance(v, float) and v.is_integer() else str(v).strip()

def identity(n, dv):
    n = val(n).replace('.', ''); dv = val(dv).upper()
    return str(int(n)) + '-' + dv if n.isdigit() else ''

def apply(rows, changes):
    result = copy.deepcopy(rows); index = {x['observacion_id']: x for x in result}
    assert len(index) == len(result)
    for c in changes:
        x = index[c['observacion_id']]
        if x == c['estado_despues']:
            continue
        if x != c['estado_antes']:
            raise ValueError('Estado anterior incompatible')
        x.clear(); x.update(copy.deepcopy(c['estado_despues']))
    return result

def counts(rows, field):
    pending = [x for x in rows if not x[field]]
    return {'observaciones': len(pending), 'personas': len({x['persona'] for x in pending})}

gb = git(); dump(O / 'GIT_ANTES.json', gb)
trial = R / 'outputs/escenario_criterio_f02_v2_v3_20261023_090316'
tm = load(trial / 'MANIFEST.json')
for name, h in tm['fuentes_hashes'].items():
    source(name, h)
for name, h in tm['salidas_hashes'].items():
    source(trial / name, h)
candidate_path = Path(tm['privado']) / 'CANDIDATOS_REVISADOS.json'
candidates = load(candidate_path, tm['privados_hashes'][candidate_path.name])
bm = load(R / 'outputs/reproduccion_puente_20261023_004044/MANIFEST.json')
obs = load(Path(bm['privado']) / 'OBSERVACIONES_PRIVADAS.json', bm['salidas_privadas_hashes']['OBSERVACIONES_PRIVADAS.json'])
cm = load(R / 'outputs/cierre_f02_iinf_aprobado_20261023_085725/MANIFEST.json')
old = load(Path(cm['privado']) / 'ADJUDICACIONES_ACUMULADAS_F02.json', cm['privados_hashes']['ADJUDICACIONES_ACUMULADAS_F02.json'])
before = apply(obs, old['adjudicaciones'])
assert counts(before, 'codigo_interno_adoptado') == {'observaciones': 3090, 'personas': 1750}
strong = [z for z in candidates if z['estado'] == 'CANDIDATO_INTERNO_CON_ACTIVIDAD']
conditional = [z for z in candidates if z['estado'] == 'CONDICIONADO_SOLO_RECONOCIMIENTO']
assert len(strong) == 2 and len(conditional) == 1
third = conditional[0]['observacion']; person = third['persona']; code = 'I162S2C6J4V2'
assert {z['observacion']['persona'] for z in candidates} == {person}
assert {(z['observacion']['plan'], z['observacion']['ano'], z['observacion']['periodo']) for z in strong} == {('TTMREOL20231', '2024', '3'), ('TTMREOL20231', '2024', '5')}
assert all(z['codigo_candidato'] == code for z in candidates)

# Reread all academic records for this identity, preserving only necessary fields.
pr = source('/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_12166.xlsx', bm['fuentes_hashes']['/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_12166.xlsx'])
w = openpyxl.load_workbook(pr, read_only=True, data_only=True)
it = iter(w['Hoja1'].values); head = next(it); records = []
fields = ['CODCLI','RUT','DIG','CODCARR','JORNADA','REGIMEN','RAMOEQUIV','CODRAMO',
          'NOTA_FINAL','ANO','PERIODO','ESTADO','DESCRIPCION_ESTADO','CONVALIDADO','NIVEL',
          'ESTADO_ACADEMICO','PLAN_DE_ESTUDIO']
for rn, row in enumerate(it, 2):
    d = dict(zip(head, row))
    if identity(d.get('RUT'), d.get('DIG')) == person:
        records.append({'fuente': str(pr), 'hoja': 'Hoja1', 'fila': rn,
                        **{k: val(d.get(k)) for k in fields}})
w.close()
for z in candidates:
    x = z['observacion']
    found = [r for r in records if all(r[k] == x[v] for k,v in [('CODCLI','CODCLI'),('CODCARR','carrera'),('PLAN_DE_ESTUDIO','plan'),('ANO','ano'),('PERIODO','periodo')])]
    assert {r['fila'] for r in found} == {e['fila'] for e in x['fuentes_promedios']}
    if z in strong:
        assert len(found) == 1 and found[0]['DESCRIPCION_ESTADO'] == 'APROBADO' and found[0]['CONVALIDADO'] != 'S'
recognized = [r for r in records if r['CODCLI'] == third['CODCLI']]
assert len(recognized) == 5 and all(r['DESCRIPCION_ESTADO'] == 'HOMOLOGADO' and r['CONVALIDADO'] == 'S' and r['ANO']=='2024' and r['PERIODO']=='1' for r in recognized)
links = []
for r in recognized:
    # Exact course-code relation, not a semantic match; origin remains a candidate.
    options = [s for s in records if s['CODCLI'] != r['CODCLI'] and s['CODRAMO'] == r['RAMOEQUIV']
               and s['DESCRIPCION_ESTADO'] == 'APROBADO' and int(s['ANO']) < int(r['ANO'])]
    links.append({'reconocimiento':r, 'antecedentes_codigo_ramo_exacto':options,
                  'notas_coinciden':bool(options) and all(s['NOTA_FINAL']==r['NOTA_FINAL'] for s in options),
                  'limite':'Coincidencia observada; no acredita acto administrativo de homologación ni versión SIES destino.'})

# Resolve relocated DA by exact hash, not filename similarity.
old_da = '/Users/alexi/Downloads/DATOSDEALUMNOS_12159.xlsx'
da = source('/Users/alexi/Desktop/Caracterizacion_2026-10-22_2027_P1_084218/01_ENTRADAS/DATOSDEALUMNOS_12159.xlsx', bm['fuentes_hashes'][old_da])
w = openpyxl.load_workbook(da, read_only=True, data_only=True)
it = iter(w['Hoja1'].values); head = next(it); da_found = []
for rn,row in enumerate(it,2):
    d = dict(zip(head,row))
    if val(d.get('CODCLI')) == third['CODCLI']:
        assert val(d.get('RUT')).replace('.','').upper() == person
        da_found.append({'fuente':str(da),'localizador_anterior':old_da,'hoja':'Hoja1','fila':rn,
            **{k:val(d.get(k)) for k in ['CODCLI','RUT','CODCARPR','SEDE','JORNADA','ANOMATRICULA','PERIODOMATRICULA','ANOINGRESO','PERIODOINGRESO','FECHAMATRICULA','ESTADOACADEMICO','SITUACION']}})
w.close()
assert len(da_found)==1 and da_found[0]['CODCARPR']=='TCRE' and da_found[0]['SEDE']=='RE' and da_found[0]['JORNADA']=='O'
assert da_found[0]['SITUACION']=='9 - RECHAZO ACTUALIZACION DE PLAN 2024' and da_found[0]['ESTADOACADEMICO']=='ELIMINADO'
decision = {'regla_id':'DOS_TTMREOL20231_2024_B3_B5_V2_APROBADOS_20261023',
 'clasificacion':'D autorización; B evidencia; C aplicación; E documental',
 'responsable_decision':'Alexi','ejecutor':'Codex','fecha_hora':now.isoformat(),
 'autorizacion_textual':'Cierra las dos observaciones con actividad corroborada como V2 por correspondencia interna y revisa si las homologaciones permiten cerrar la tercera. Deja pendiente la atribución documental, sin cambiar las bases ni los denominadores.',
 'alcance':'Dos observaciones de una persona, TTMREOL20231/2024/bimestres 3 y 5',
 'codigo_interno_adoptado':code,'numero_cierres':2,
 'criterio':'Misma persona/familia con V2 único en MU2023, MU2024 y MU2025; actividad aprobada del CODCLI y plan en cada período; oferta anual compatible.',
 'tercera':'TCRE20241/2024/1 continúa pendiente; solo homologaciones y situación de rechazo de actualización del plan. No se acredita equivalencia SIES del expediente destino ni fecha efectiva.',
 'alerta':'Cambio acotado autorizado. No generalizar a otras personas o planes ni interpretar como envío/aceptación SIES.',
 'antecedente':str(trial/'MANIFEST.json'),'sha256_antecedente':sha(trial/'MANIFEST.json'),
 'reversion':'Omitir las dos nuevas adjudicaciones, conservar las cuatro F02 previas. Estados antes/después privados.',
 'consumidores':'Solo capa diagnóstica local; motor anual, bases, tasas y denominadores intactos.'}
changes=[]; idx={x['observacion_id']:x for x in before}
for z in strong:
    x=z['observacion']; assert idx[x['observacion_id']]==x and not x['codigo_interno_adoptado'] and not x['codigo_documental_atribuible']
    y=copy.deepcopy(x)
    y.update(codigo_interno_adoptado=code,estado_interno='RESUELTO_INTERNO_CONTINUIDAD_CONTEXTUAL_APROBADA',regla=decision['regla_id'],clasificacion='B/C/D; E atribución documental y fecha administrativa')
    changes.append({'observacion_id':x['observacion_id'],'estado_antes':x,'estado_despues':y,'regla_id':decision['regla_id']})
after=apply(before,changes)
result={'clasificacion':'C conteos del diccionario, no tasas de retención',
 'interno_antes':counts(before,'codigo_interno_adoptado'),'interno_despues':counts(after,'codigo_interno_adoptado'),
 'documental_antes':counts(before,'codigo_documental_atribuible'),'documental_despues':counts(after,'codigo_documental_atribuible'),
 'cierres_internos_nuevos':2,'personas_parcialmente_resueltas_nuevas':1,'personas_completamente_resueltas_nuevas':0,
 'tercera_observacion':'PENDIENTE','homologaciones':5,
 'homologaciones_con_antecedente_exacto_previo':sum(bool(l['antecedentes_codigo_ramo_exacto']) for l in links),
 'homologaciones_con_nota_coincidente':sum(l['notas_coinciden'] for l in links),
 'universo_conservado':{'personas':5901,'expedientes_aprobados':6622,'observaciones':24774},'tasas_retencion_modificadas':False}
assert result['interno_despues']=={'observaciones':3088,'personas':1750}
assert result['documental_antes']==result['documental_despues']=={'observaciones':3213,'personas':1838}
ids={c['observacion_id'] for c in changes}; allowed={'codigo_interno_adoptado','estado_interno','regla','clasificacion'}
qa={'estado':'OK_CON_ADVERTENCIAS',
 'exactamente_dos_observaciones':{a['observacion_id'] for a,b in zip(before,after) if a!=b}==ids,
 'solo_campos_internos':all({k for k in a if a[k]!=b[k]}<=allowed for a,b in zip(before,after)),
 'tercera_intacta':next(x for x in after if x['observacion_id']==third['observacion_id'])==third,
 'universo_conservado':len(after)==24774 and len({x['persona'] for x in after})==5901,
 'cierre_F02_conservado':all(next(x for x in after if x['observacion_id']==c['observacion_id'])==c['estado_despues'] for c in old['adjudicaciones']),
 'idempotencia':apply(after,changes)==after,'privado_fuera_git':True,
 'advertencias':'Atribución documental pendiente; tercera sin cierre interno. Estado DA sin fecha de rechazo; no extrapolarlo como estado histórico del trimestre.'}
bad=copy.deepcopy(before);next(x for x in bad if x['observacion_id'] in ids)['codigo_interno_adoptado']='INCOMPATIBLE'
try: apply(bad,changes)
except ValueError: qa['estado_incompatible_rechazado']=True
else: qa['estado_incompatible_rechazado']=False
assert all(v for v in qa.values() if isinstance(v,bool))
dump(Q/'ADJUDICACIONES_DOS_APROBADAS.json',{'decision':decision,'adjudicaciones':changes})
dump(Q/'ADJUDICACIONES_ACUMULADAS.json',{'orden_aplicacion':old['orden_aplicacion']+[decision['regla_id']], 'adjudicaciones':old['adjudicaciones']+changes})
dump(Q/'OBSERVACIONES_PERSONA_DESPUES.json',[x for x in after if x['persona']==person])
dump(Q/'REVISION_HOMOLOGACIONES.json',{'observacion':third,'filas_promedios_persona':records,'enlaces':links,'datos_alumnos':da_found,'resultado':'PENDIENTE_INTERNO_Y_DOCUMENTAL','fecha_hora':now.isoformat()})
source(__file__);source(R/'docs/ESPECIFICACION_CIERRE_DOS_V2_Y_HOMOLOGACIONES_20261023.md')
qa['fuentes_intactas']=all(sha(p)==h for p,h in H.items());assert qa['fuentes_intactas']
dump(O/'DECISION_APROBADA.json',decision);dump(O/'RESULTADOS.json',result);dump(O/'QA.json',qa)
report=f'''# Dos cierres V2 autorizados y revisión de homologaciones

Proceso: correspondencia interna UMAS/SIES; observaciones académicas 2024.
Decisión D de Alexi; ejecución C, {now.isoformat()}.

| Plan / período | Resultado | Respaldo |
|---|---|---|
| TTMREOL20231 / 2024 bimestre 3 | I162S2C6J4V2 adoptado internamente | B actividad aprobada; C/D aplicación autorizada |
| TTMREOL20231 / 2024 bimestre 5 | I162S2C6J4V2 adoptado internamente | B actividad aprobada; C/D aplicación autorizada |
| TCRE20241 / 2024 trimestre 1 | Pendiente; V2 sigue candidato, no adoptado | B homologaciones y rechazo de actualización; E atribución |

Las tres observaciones pertenecen a una persona. No se suman matrículas como
personas ni se confunden bimestres y trimestres. Atribución documental pendiente
en las tres; ninguno de estos cierres acredita envío o aceptación SIES.

## Homologaciones: qué prueban y qué no — B/C/E

Se releyeron todas las filas de PROMEDIOS de esa identidad. El expediente TCRE
solo presenta cinco filas HOMOLOGADO, CONVALIDADO=S, plan TCRE20241, año 2024,
período 1. Las cinco tienen ESTADO_ACADEMICO=ELIMINADO en ese reporte.
RAMOEQUIV y CODRAMO relacionan códigos de asignaturas: en
{result['homologaciones_con_antecedente_exacto_previo']} de las cinco se localizó un ramo previamente aprobado
de la misma persona con código exacto; en {result['homologaciones_con_nota_coincidente']} coincidió también la nota.
El detalle conserva alternativas y localizadores, sin deducir por prefijos de ramo
la carrera o versión SIES. No es una equivalencia universal de planes.

La copia de DATOSDEALUMNOS_12159 recuperada en el Escritorio tiene el mismo
SHA-256 que el original del manifiesto, antes referenciado en Descargas.
En Hoja1, fila 7179, el expediente TCRE figura ELIMINADO y
**9 - RECHAZO ACTUALIZACION DE PLAN 2024**. Declara matrícula 2024/período 1 y
fecha de matrícula 05-02-2024. Esta fecha no es fecha de rechazo ni fecha efectiva
de migración; no se dispone de historia fechada de esa transición.

La persona conserva V2 único en MU2023, MU2024 y MU2025, pero eso no atribuye
por sí solo el código al expediente TCRE. Las homologaciones prueban registros
de reconocimiento en el plan destino; no bastan para afirmar que ese cambio
quedó efectivo, especialmente ante la situación explícita de rechazo. No se
las convierte en cursado ni en retención. La tercera observación sigue E.
Falta evidencia de efectividad del plan para ese expediente/período o una decisión
interna explícita para clasificar también reconocimientos de cambios rechazados.
No se presume rechazo vigente durante todo 2024 ni se elimina la observación.

## Conteos posteriores — C

- Pendientes internos: 3.090 → **3.088 observaciones**, **1.750 personas**, sin cambio.
- Una persona parcialmente resuelta; ninguna persona completamente resuelta nueva.
- Documentales: **3.213 observaciones / 1.838 personas**, intactos.
- Universo aprobado: 5.901 personas, 6.622 expedientes y 24.774 observaciones.
- Bases, libros, tasas y denominadores de retención sin cambios.

## Aplicación, QA y reanudación

Los dos cierres están materializados en la capa diagnóstica local privada;
no son solo una simulación. Cargar la base fijada por hash y superponer
ADJUDICACIONES_ACUMULADAS.json (cuatro decisiones F02 previas más estas dos),
verificando estado_antes. Repetición idempotente; estado incompatible rechazado.
Para revertir solo este cierre, omitir las dos adjudicaciones nuevas.

QA OK_CON_ADVERTENCIAS: exactamente dos cambios de campos internos; tercer
registro, documental, fuentes y F02 intactos. Identificadores fuera de Git.
Advertencias: atribución documental y tercera observación pendientes.
Registro local reproducible, no publicado en GitHub. Sin commit/push.
'''
(O/'INFORME_CIERRE.md').write_text(report)
(O/'CHECKPOINT.md').write_text('# Reanudación\n\nCierre interno autorizado de dos observaciones TTMREOL20231/2024/B3 y B5 como V2 aplicado en capa local. Usar ADJUDICACIONES_ACUMULADAS.json privada para reconstruir cuatro F02 previas + dos nuevas. Contadores 3.088 observaciones / 1.750 personas internas pendientes; documental 3.213 / 1.838. TCRE20241/2024/1 sigue pendiente: homologaciones y situación 9 rechazo actualización; no acredita efectividad del cambio. No modificar fuentes, denominadores o motor. No generalizar. Sin commit/push.\n')
ga=git();assert all(gb[k]==ga[k] for k in ['rama','HEAD','remotos']);dump(O/'GIT_DESPUES.json',ga)
dump(O/'FUENTES_HASHES.json',H)
secrets={x['persona'] for x in obs}|{x['CODCLI'] for x in obs}
for f in O.iterdir():
    s=f.read_text();assert not any(k and k in s for k in secrets),'Identificador en salida compartible'
dump(O/'MANIFEST.json',{'fecha_hora':now.isoformat(),'fuentes_hashes':H,
 'salidas_hashes':{f.name:sha(f) for f in O.iterdir()},'privado':str(Q),
 'privados_hashes':{f.name:sha(f) for f in Q.iterdir()},'resultado':result,'qa':qa,
 'decision':decision['regla_id'],'rama':ga['rama'],'HEAD':ga['HEAD'],
 'cierres_aplicados':2,'tercera_aplicada':False,'commit_push':False,'estado_publicacion':'Local no publicado'})
print(json.dumps({'salida':str(O),'resultado':result,'QA':qa['estado']},ensure_ascii=False))
