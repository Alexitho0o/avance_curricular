"""Aplica exclusivamente las tres adjudicaciones internas autorizadas de F02."""
import copy, datetime, hashlib, json, os, subprocess
from pathlib import Path
from zoneinfo import ZoneInfo

R=Path(__file__).resolve().parents[1];P=Path.home()/'.local/share/ipss'
now=datetime.datetime.now(ZoneInfo('America/Santiago'));stamp=now.strftime('%Y%m%d_%H%M%S')
O=R/'outputs'/('cierre_f02_iinf_aprobado_'+stamp);Q=P/('cierre_f02_iinf_aprobado_'+stamp)
assert subprocess.run(['git','-C',str(P),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
os.umask(0o077);O.mkdir();Q.mkdir(mode=0o700);H={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def source(p,h=None):
 p=Path(p);actual=sha(p);assert h is None or actual==h,'Hash incompatible: '+str(p);H[str(p)]=actual;return p
def load(p,h=None):return json.loads(source(p,h).read_text())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def git():return {k:subprocess.check_output(['git','-C',str(R),*a],text=True).strip() for k,a in [('rama',['branch','--show-current']),('HEAD',['rev-parse','HEAD']),('remotos',['remote','-v']),('status',['status','--short'])]}
beforegit=git();dump(O/'GIT_ANTES.json',beforegit)
prior=R/'outputs/cierre_interno_f02_20261023_084246'
review=R/'outputs/contraste_f02_iinf_20261023_084727'
pm=load(prior/'MANIFEST.json');rm=load(review/'MANIFEST.json')
for folder,m in [(prior,pm),(review,rm)]:
 for name,h in m['salidas_hashes'].items():source(folder/name,h)
 for name,h in m['privados_hashes'].items():source(Path(m['privado'])/name,h)
 for name,h in m['fuentes_hashes'].items():source(name,h)
baseline_path=P/'reproduccion_puente_20261023_004044/OBSERVACIONES_PRIVADAS.json'
obs=load(baseline_path,H[str(baseline_path)])
old=load(Path(pm['privado'])/'ADJUDICACION_INTERNA.json')
proposal=load(Path(rm['privado'])/'PROPUESTA_F02_TRES_PERIODOS.json')
person=old['persona'];code='I162S2C1J4V2'

def apply(rows, changes):
 out=copy.deepcopy(rows);idx={x['observacion_id']:x for x in out}
 assert len(idx)==len(out)
 for c in changes:
  actual=idx[c['observacion_id']]
  if actual==c['estado_despues']:continue
  if actual!=c['estado_antes']:raise ValueError('Estado anterior incompatible; no aplicar decisión')
  actual.clear();actual.update(copy.deepcopy(c['estado_despues']))
 return out

before=apply(obs,[old]);targets={x['observacion_id'] for x in proposal['observaciones']}
chosen=[x for x in before if x['observacion_id'] in targets]
assert len(chosen)==3 and {x['periodo'] for x in chosen}=={'1','2','3'}
assert all(x['persona']==person and x['plan']=='IINF20241' and x['ano']=='2024' and not x['codigo_interno_adoptado'] and not x['codigo_documental_atribuible'] for x in chosen)
decision={'regla_id':'F02_IINF20241_2024_T1_T2_T3_V2_APROBADA_20261023',
 'clasificacion':'D decisión autorizada; B evidencia; C aplicación; E atribución documental',
 'responsable_decision':'Alexi','ejecutor':'Codex','fecha_hora':now.isoformat(),
 'autorizacion_textual':'Apruebo ese criterio para F02. Cierra las tres observaciones como V2 por correspondencia interna, dejando pendiente la atribución documental, y registra la decisión sin cambiar las bases ni los denominadores.',
 'alcance':'Solo F02, IINF20241, 2024/T1, T2 y T3', 'codigo_interno_adoptado':code,
 'criterio':'Continuidad contextual de la misma persona/familia: V2 en MU2023 y MU2025, corroborada por MU2024 y actividad del plan en los tres períodos.',
 'limites':'No equivalencia universal IINF20241, no fecha exacta del cambio, no atribución documental por expediente ni envío/aceptación SIES.',
 'alerta':'Nueva decisión interna acotada autorizada. No propagar automáticamente a otras personas, períodos ni consumidores.',
 'antecedente':str(review/'MANIFEST.json'),'sha256_antecedente':H[str(review/'MANIFEST.json')],
 'cierre_anterior':str(prior/'MANIFEST.json'),'sha256_cierre_anterior':H[str(prior/'MANIFEST.json')],
 'reversion':'Omitir estas tres adjudicaciones y conservar la anterior de IECIREOL20211. Estado antes/después completo en el detalle privado.',
 'consumo':'Capa local de adjudicación reproducible; no modificación de las bases ni del motor anual.'}
changes=[]
for x in chosen:
 y=copy.deepcopy(x)
 y.update(codigo_interno_adoptado=code,estado_interno='RESUELTO_INTERNO_CONTINUIDAD_CONTEXTUAL_F02_APROBADA',regla=decision['regla_id'],clasificacion='B/C/D; E atribución documental por expediente y fecha administrativa')
 changes.append({'observacion_id':x['observacion_id'],'estado_antes':copy.deepcopy(x),'estado_despues':y,'regla_id':decision['regla_id']})
after=apply(before,changes)
def counts(rows,field):
 z=[x for x in rows if not x[field]];return {'observaciones':len(z),'personas':len({x['persona'] for x in z})}
def casecounts(rows):
 z=[x for x in rows if x['persona']==person]
 return {'observaciones':len(z),'pendientes_internos':sum(not x['codigo_interno_adoptado'] for x in z),'pendientes_documentales':sum(not x['codigo_documental_atribuible'] for x in z)}
result={'clasificacion':'C cálculo del diagnóstico; no tasa de retención','F02_antes':casecounts(before),'F02_despues':casecounts(after),
 'interno_antes':counts(before,'codigo_interno_adoptado'),'interno_despues':counts(after,'codigo_interno_adoptado'),
 'documental_antes':counts(before,'codigo_documental_atribuible'),'documental_despues':counts(after,'codigo_documental_atribuible'),
 'universo_referencia_conservado':{'personas':5901,'expedientes_aprobados':6622,'observaciones':24774},'tasas_retencion_recalculadas':False}
assert result['interno_antes']=={'observaciones':3093,'personas':1751}
assert result['interno_despues']=={'observaciones':3090,'personas':1750}
assert result['documental_antes']==result['documental_despues']=={'observaciones':3213,'personas':1838}
assert result['F02_despues']=={'observaciones':9,'pendientes_internos':0,'pendientes_documentales':4}
assert apply(after,changes)==after
bad=copy.deepcopy(before);next(x for x in bad if x['observacion_id'] in targets)['codigo_interno_adoptado']='INCOMPATIBLE'
try:apply(bad,changes)
except ValueError:rejection=True
else:rejection=False
doc_fields=['codigo_documental_atribuible','estado_documental','aceptacion_SIES','plan_efectivo_periodo','fecha_efectiva_plan']
qa={'estado':'OK_CON_ADVERTENCIAS','tres_cambios_exactos':{a['observacion_id'] for a,b in zip(before,after) if a!=b}==targets,
 'documental_y_fecha_sin_cambios':all(all(a[k]==b[k] for k in doc_fields) for a,b in zip(before,after)),
 'universo_inalterado':len(before)==len(after)==24774 and len({x['persona'] for x in after})==5901,
 'repeticion_idempotente':apply(after,changes)==after,'estado_incompatible_rechazado':rejection,
 'cierre_anterior_conservado':next(x for x in after if x['observacion_id']==old['observacion_id'])==old['estado_despues'],
 'F02_cerrado_solo_internamente':casecounts(after)=={'observaciones':9,'pendientes_internos':0,'pendientes_documentales':4},
 'privado_fuera_git':True,'advertencia':'Cuatro atribuciones documentales de F02 y fecha administrativa pendientes; no equivalencia universal.'}
assert all(v for v in qa.values() if isinstance(v,bool))
dump(Q/'ADJUDICACIONES_TRES_APROBADAS.json',{'decision':decision,'adjudicaciones':changes})
dump(Q/'ADJUDICACIONES_ACUMULADAS_F02.json',{'orden_aplicacion':[old['regla_id'],decision['regla_id']],'adjudicaciones':[old,*changes]})
dump(Q/'F02_OBSERVACIONES_CIERRE_INTERNO.json',[x for x in after if x['persona']==person])
source(__file__);source(R/'docs/ESPECIFICACION_CIERRE_F02_IINF_APROBADO_20261023.md')
qa['entradas_intactas']=all(sha(p)==h for p,h in H.items());assert qa['entradas_intactas']
dump(O/'DECISION_APROBADA.json',decision);dump(O/'RESULTADOS.json',result);dump(O/'QA.json',qa);dump(O/'FUENTES_HASHES.json',H)
report=f'''# F02: cierre interno completo aprobado

Decisión D de Alexi, registrada {now.isoformat()}; ejecución C por Codex.

| Plan y período | Código interno adoptado | Atribución documental |
|---|---|---|
| IINF20241 · 2024/T1 | I162S2C1J4V2 | Pendiente E |
| IINF20241 · 2024/T2 | I162S2C1J4V2 | Pendiente E |
| IINF20241 · 2024/T3 | I162S2C1J4V2 | Pendiente E |

Se aplica el criterio contextual aprobado exclusivamente a F02. La evidencia B
es su V2 anual antes/durante/después de 2024 y la actividad observada del plan.
La correspondencia interna C/D no acredita por sí sola la asignación documental
al nuevo expediente ni fecha administrativa del cambio. No se generaliza.

## Resultado C

- F02: nueve observaciones resueltas internamente; cero pendientes internos.
- Tres cierres nuevos, sumados al anterior autorizado de IECIREOL20211/2024/2
  y a cinco observaciones 2023 ya resueltas. No contar cuatro cierres nuevos.
- Pendientes internos globales: 3.093 → 3.090 observaciones y 1.751 → 1.750 personas.
- Documentales: 3.213 observaciones / 1.838 personas, sin cambios. F02 conserva
  cuatro atribuciones documentales pendientes.
- Universo aprobado conservado: 5.901 personas / 6.622 expedientes / 24.774
  observaciones. No se cambian tasas, bases, libros ni denominadores.

## Registro, aplicación y reversión

DECISION_APROBADA.json registra autorización textual, responsable, fecha/hora,
criterio, alcance, alerta, hashes antecedentes y reversión. Los localizadores
individuales y estados antes/después están únicamente en el detalle privado.

La adjudicación se aplicó en memoria al diagnóstico y quedó materializada en
F02_OBSERVACIONES_CIERRE_INTERNO.json. Para reproducir el estado, cargar la base
diagnóstica fijada por hash y superponer ADJUDICACIONES_ACUMULADAS_F02.json por
observacion_id, comprobando estado_antes y conservando el documental. La
repetición es idempotente y rechaza un estado incompatible. El motor anual no
consume automáticamente esta decisión; no se actualizan catálogos ni fuentes.

QA OK_CON_ADVERTENCIAS: tres cambios internos exactos, ningún cambio ajeno o
documental, cierre anterior conservado, entradas intactas y conteos verificados.
La advertencia corresponde a los pendientes documentales, no a un fallo de
aplicación. Fecha exacta del cambio sigue E.

Sin commit/push. Rama y HEAD conservados; ver GIT_ANTES.json y GIT_DESPUES.json.
'''
(O/'INFORME_CIERRE.md').write_text(report)
(O/'CHECKPOINT.md').write_text('# Reanudación F02\n\nEstado vigente local: cierre interno completo aprobado. Tres nuevas adjudicaciones IINF20241/2024/T1–T3; conservar la anterior IECIREOL20211/2024/2. No reabrir la decisión por falta del día administrativo. Documental continúa pendiente: cuatro observaciones. No extender criterio a otras personas. Usar MANIFEST.json y ADJUDICACIONES_ACUMULADAS_F02.json del detalle privado para reproducir. Sin commit/push.\n')
aftergit=git();assert all(beforegit[k]==aftergit[k] for k in ['rama','HEAD','remotos']);dump(O/'GIT_DESPUES.json',aftergit)
secrets={x['persona'] for x in obs}|{x['CODCLI'] for x in obs}
for p in O.iterdir():
 s=p.read_text();assert not any(k and k in s for k in secrets),'Identificador en salida compartible'
dump(O/'MANIFEST.json',{'fecha_hora':now.isoformat(),'clasificacion':'B/C/D; E documental','decision':decision['regla_id'],
 'fuentes_hashes':H,'salidas_hashes':{p.name:sha(p) for p in O.iterdir()},'privado':str(Q),
 'privados_hashes':{p.name:sha(p) for p in Q.iterdir()},'resultado':result,'qa':qa,'rama':aftergit['rama'],'HEAD':aftergit['HEAD'],
 'commit_push':False,'estado_publicacion':'Local, no publicado en GitHub'})
print(json.dumps({'salida':str(O),'privado':str(Q),'resultado':result,'QA':qa['estado']},ensure_ascii=False))
