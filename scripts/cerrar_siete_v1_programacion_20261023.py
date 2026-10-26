"""Siete cierres autorizados; cinco propuestas complementarias no adoptadas."""
import collections,copy,datetime,hashlib,json,os,subprocess
from pathlib import Path
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1];P=Path.home()/'.local/share/ipss'
now=datetime.datetime.now(ZoneInfo('America/Santiago'));stamp=now.strftime('%Y%m%d_%H%M%S')
O=R/'outputs'/('cierre_siete_v1_programacion_'+stamp);Q=P/('cierre_siete_v1_programacion_'+stamp)
assert subprocess.run(['git','-C',str(P),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
os.umask(0o077);O.mkdir();Q.mkdir(mode=0o700);H={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def src(p,h=None):
 p=Path(p);p=p if p.is_absolute() else R/p;a=sha(p);assert h is None or a==h,str(p);H[str(p)]=a;return p

def load(p,h=None):return json.loads(src(p,h).read_text())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
def git():return {k:subprocess.check_output(['git','-C',str(R),*args],text=True).strip() for k,args in [('rama',['branch','--show-current']),('HEAD',['rev-parse','HEAD']),('remotos',['remote','-v']),('status',['status','--short'])]}
def apply(rows,changes):
 r=copy.deepcopy(rows);idx={x['observacion_id']:x for x in r};assert len(idx)==len(r)
 for op in changes:
  x=idx[op['observacion_id']]
  if x==op['estado_despues']:continue
  if x!=op['estado_antes']:raise ValueError('Estado anterior incompatible')
  x.clear();x.update(copy.deepcopy(op['estado_despues']))
 return r

def counts(rows,key):
 a=[x for x in rows if not x[key]];return {'observaciones':len(a),'personas':len({x['persona'] for x in a})}

gb=git();dump(O/'GIT_ANTES.json',gb)
prev=R/'outputs/revision_programacion_12_20261023_095818';pm=load(prev/'MANIFEST.json')
for p,h in pm['fuentes_hashes'].items():src(p,h)
for p,h in pm['salidas_hashes'].items():src(prev/p,h)
for p,h in pm['privados_hashes'].items():src(Path(pm['privado'])/p,h)
review=load(Path(pm['privado'])/'REVISION_12_POR_OBSERVACION.json',pm['privados_hashes']['REVISION_12_POR_OBSERVACION.json'])
prior=R/'outputs/clasificacion_tcre_siguiente_bloque_20261023_095113';cm=load(prior/'MANIFEST.json')
old=load(Path(cm['privado'])/'ADJUDICACIONES_ACUMULADAS.json',cm['privados_hashes']['ADJUDICACIONES_ACUMULADAS.json'])
bp=P/'reproduccion_puente_20261023_004044/OBSERVACIONES_PRIVADAS.json';base=load(bp,H[str(bp)])
before=apply(base,old['adjudicaciones']);idx={x['observacion_id']:x for x in before}
strong=[x for x in review if x['grupo_revision']=='A_CONTINUIDAD_MU_2023_2024_2025'];five=[x for x in review if x not in strong]
assert len(strong)==7 and len({x['observacion']['persona'] for x in strong})==4 and len(five)==5
CODE='I162S2C57J4V1';rid='PROGRAMACION_SIETE_V1_CONTINUIDAD_20261023'
decision={'regla_id':rid,'responsable_decision':'Alexi','ejecutor':'Codex','fecha_hora':now.isoformat(),'clasificacion':'D decisión aprobada; B respaldo; C aplicación; E atribución documental',
 'autorizacion_textual':'Cierra las siete observaciones como V1 por correspondencia interna y revisa qué criterio complementario permitiría resolver las otras cinco, dejando pendiente la atribución documental, sin cambiar las bases ni los denominadores.',
 'alcance':'Siete observaciones de cuatro personas del grupo A de la revisión 20261023_095818; TPAREOL20231/2024.',
 'codigo_interno_adoptado':CODE,'criterio':'Continuidad personal MU2023–2024–2025 V1, aprobación exacta y reportes históricos del plan; no atribuir las homologaciones del plan rechazado.',
 'antecedente':str(prev/'MANIFEST.json'),'sha256_antecedente':H[str(prev/'MANIFEST.json')],
 'alerta':'No es equivalencia universal del plan ni prueba de envío/aceptación SIES. No aplicar las cinco propuestas complementarias sin autorización.',
 'reversion':'Omitir únicamente estas siete adjudicaciones; conservar las siete operaciones anteriores.'}
changes=[]
for x in strong:
 o=x['observacion'];b=idx[o['observacion_id']];assert b==x['estado_antes'] and not b['codigo_interno_adoptado']
 assert all(x['mu_por_ano'][year]==[CODE] for year in ['2023','2024','2025']) and x['aprobaciones_periodo']
 y=copy.deepcopy(b);y.update(codigo_interno_adoptado=CODE,estado_interno='CORRESPONDENCIA_INTERNA_APROBADA',regla=rid,clasificacion='D correspondencia interna aprobada; B evidencia; C aplicación; E atribución documental',requisito_pendiente='Atribución documental al expediente/período pendiente. Código interno aprobado solo para esta observación; no acredita envío ni aceptación SIES ni fecha administrativa exacta.')
 changes.append({'observacion_id':o['observacion_id'],'estado_antes':b,'estado_despues':y,'regla_id':rid})
after=apply(before,changes)
assert counts(before,'codigo_interno_adoptado')=={'observaciones':3088,'personas':1750}
assert counts(after,'codigo_interno_adoptado')=={'observaciones':3081,'personas':1750}
assert counts(after,'codigo_documental_atribuible')=={'observaciones':3213,'personas':1838}
# Separate proposed criterion: focal evidence, not an automatic new equivalence.
def nonrecognition_approved(r):return r.get('DESCRIPCIONESTADO')=='APROBADO' and r.get('CONVALIDADO')!='S'
def mu_code(r):return 'I162S'+r['COD_SED']+'C'+r['COD_CAR']+'J'+r['JOR']+'V'+r['VERSION']
cat=load(prev/'CONTROL_OFERTA.json',pm['salidas_hashes']['CONTROL_OFERTA.json'])
catcodes={r['codigo_unico'] for r in cat['filas'] if any(y['anio']==2024 for y in r['anual'])}

def evaluate(z):
 o=z['observacion'];p=o['persona'];cc=o['CODCLI'];plan=o['plan'];year=o['ano'];period=o['periodo']
 ar=[r for r in z['aprobaciones_periodo'] if r['persona']==p and r.get('CODCLI')==cc and r.get('PLANDEESTUDIO')==plan and r.get('ANO')==year and r.get('PERIODO')==period and nonrecognition_approved(r)]
 mr=[r for r in z['mu_2024'] if r['persona']==p and r['ANIO_INFORMADO']==year and r['COD_SED']==o['sede_dimension'] and r['JOR']==o['jornada_sies']]
 direct=[r for r in z['reportes_fechados_plan_anterior'] if r['CODCLI']==cc and r['plan_observado']==plan and r['ano']==year and r['periodo_original']==period]
 new=z['actividad_plan_nuevo'];new24=[r for r in new if r['persona']==p and r.get('PLANDEESTUDIO')=='TPAS20241' and r.get('ANO')=='2024' and nonrecognition_approved(r)];new25=[r for r in new if r['persona']==p and r.get('PLANDEESTUDIO')=='TPAS20241' and r.get('ANO')=='2025' and nonrecognition_approved(r)]
 rejection=z['respaldo_rechazo_plan_nuevo'];updates=z['respaldo_actualizacion_plan_anterior']
 if z['grupo_revision']=='D_CAMBIO_PLAN_CON_ACTIVIDAD_EN_AMBOS':
  route='ACTUALIZACION_CON_ACTIVIDAD_EN_ORIGEN_Y_DESTINO'
  pair=[other for other in five if other['observacion']['persona']==p and other['observacion']['plan']=='TPAREOL20231']
  previous=bool(pair and any(nonrecognition_approved(r) for r in pair[0]['aprobaciones_periodo']))
  temporal=bool(updates and previous and new24 and new25 and not rejection and (direct or plan=='TPAS20241'))
 else:
  route='CONTINUIDAD_PLAN_ANTERIOR_CON_REPORTE_FECHADO'
  temporal=bool(direct and rejection and not new24)
 gates={'identidad_plan_periodo_aprobacion':bool(ar),'codigo_personal_unico_ano_objetivo':bool(mr) and {mu_code(r) for r in mr}=={CODE},'catalogo_2024_compatible':CODE in catcodes,'respaldo_contextual_sin_trasladar_fechas_entre_planes':temporal,'regimen_conservado':{r.get('REGIMEN') for r in ar}==set(z['regimen'])}
 return {'via':route,'controles':gates,'cumple_criterio_propuesto':all(gates.values()),'aprobaciones_exactas':ar,'mu_personal_ano_objetivo':mr,'reportes_fechados_del_plan_objetivo':direct,'evidencia_actualizacion':updates,'evidencia_rechazo_plan_nuevo':rejection,'actividad_nuevo_2024':new24,'actividad_nuevo_2025':new25,'limite':'Propuesta D acotada, no aplicada; no reemplaza atribución documental ni fecha administrativa. No generalizar a ausentes, reconocimientos o códigos contradictorios.'}
assess=[]
for z in five:
 v=evaluate(z);assert v['cumple_criterio_propuesto']
 assess.append({'observacion':z['observacion'],'criterio_evaluado':v,'codigo_propuesto':CODE,'codigo_adoptado':'','estado_antes':idx[z['observacion']['observacion_id']],'estado_despues_vigente':idx[z['observacion']['observacion_id']]})
criterion={'id':'PROPUESTA_PROGRAMACION_CODIGO_ANUAL_ACTIVIDAD_PLAN_20261023','estado':'PROPUESTA_NO_APROBADA_NO_APLICADA','clasificacion':'D propuesta; B evidencia; C evaluación; E atribución documental y fecha efectiva',
 'alcance':'Cinco observaciones de tres personas revisadas, Programación 2024, sin equivalencia universal.',
 'condiciones':['Identidad exacta y CODCLI corroborado, aprobación no homologada/convalidada en plan/año/período exactos.', 'Código único personal de MU2024 en familia y contexto compatibles, sin variante contradictoria localizada; catálogo anual compatible.', 'Conservar régimen académico: bimestre y trimestre no son intercambiables.', 'Plan anterior: reporte fechado del propio plan/período, continuidad aprobada y rechazo observado del nuevo; no trasladar reconocimiento del nuevo al antiguo.', 'Actualización: actividad aprobada de ambos planes por separado, actualización observada del anterior y actividad del nuevo en 2024 y 2025; no usar fecha de matrícula como fecha de cambio.', 'Registrar código como correspondencia interna acotada; dejar atribución documental y día efectivo pendientes.'],
 'diferencia_con_criterio_anterior':'El respaldo contextual sustituye la exigencia de matrícula en ambos años adyacentes; no se imputa una MU2025 ausente.',
 'riesgos':['Código anual no identifica CODCLI o plan por sí solo.','Los respaldos de estados no acreditan el día de transición.','Único candidato en catálogo no prueba envío individual.','Una observación de actividad no es una matrícula adicional ni cambia denominadores.'],
 'resultado_revision':{'observaciones_que_cumplen':5,'personas':3,'codigo_propuesto':CODE,'cierres_aplicados':0}}
# Negative controls target method mechanics, not empirical accuracy.
tests=[]
for name,fn in [('sin_aprobacion',lambda z:z.update(aprobaciones_periodo=[])),('sin_MU_objetivo',lambda z:z.update(mu_2024=[])),('solo_homologaciones',lambda z:[r.update(CONVALIDADO='S',DESCRIPCIONESTADO='HOMOLOGADO') for r in z['aprobaciones_periodo']]),('periodo_equivocado',lambda z:z['observacion'].update(periodo='99')),('codigo_anual_distinto',lambda z:[r.update(VERSION='99') for r in z['mu_2024']]),('regimen_equivocado',lambda z:z.update(regimen=['NO_ACREDITADO']))]:
 for original in five:
  z=copy.deepcopy(original);fn(z);tests.append({'prueba':name,'rechazado':not evaluate(z)['cumple_criterio_propuesto']})
for original in five:
 z=copy.deepcopy(original)
 if z['grupo_revision']=='D_CAMBIO_PLAN_CON_ACTIVIDAD_EN_AMBOS':z['respaldo_actualizacion_plan_anterior']=[]
 else:z['reportes_fechados_plan_anterior']=[]
 tests.append({'prueba':'sin_respaldo_contextual','rechazado':not evaluate(z)['cumple_criterio_propuesto']})
assert all(t['rechazado'] for t in tests)
# Hypothetical only; no new adopted state for the five.
sim=copy.deepcopy(after);ids={z['observacion']['observacion_id'] for z in five}
for x in sim:
 if x['observacion_id'] in ids:x['codigo_interno_adoptado']=CODE
scenario=counts(sim,'codigo_interno_adoptado');assert scenario=={'observaciones':3076,'personas':1750}
allowed={'codigo_interno_adoptado','estado_interno','regla','clasificacion','requisito_pendiente'}
qa={'estado':'OK_CON_ADVERTENCIAS','siete_cambios_exactos':sum(a!=b for a,b in zip(before,after))==7,'solo_campos_internos_autorizados':all({k for k in a if a[k]!=b[k]}<=allowed for a,b in zip(before,after)), 'documental_intacto':all(a['codigo_documental_atribuible']==b['codigo_documental_atribuible'] and a['estado_documental']==b['estado_documental'] for a,b in zip(before,after)), 'idempotencia':apply(after,changes)==after,'cinco_no_modificadas':all(next(x for x in after if x['observacion_id']==oid)==idx[oid] for oid in ids),'universo_intacto':len(after)==24774 and len({x['persona'] for x in after})==5901,'controles_negativos':{'cantidad':len(tests),'rechazados':sum(t['rechazado'] for t in tests),'limite':'Pruebas de controles técnicos; no estiman precisión empírica ni validan equivalencia universal.'},'advertencias':['Cinco correspondencias propuestas pendientes de aprobación.','Atribución documental y fechas administrativas exactas siguen pendientes.']}
bad=copy.deepcopy(before);next(x for x in bad if x['observacion_id']==changes[0]['observacion_id'])['estado_interno']='ESTADO_INCOMPATIBLE'
try:apply(bad,changes)
except ValueError:qa['estado_incompatible_rechazado']=True
else:qa['estado_incompatible_rechazado']=False
assert all(v for v in qa.values() if isinstance(v,bool))
dump(Q/'ADJUDICACIONES_SIETE_V1.json',{'decision':decision,'adjudicaciones':changes})
dump(Q/'ADJUDICACIONES_ACUMULADAS.json',{'orden_aplicacion':old['orden_aplicacion']+[rid],'adjudicaciones':old['adjudicaciones']+changes})
dump(Q/'SIETE_DESPUES.json',[x['estado_despues'] for x in changes]);dump(Q/'CINCO_CRITERIO_COMPLEMENTARIO.json',assess)
dump(O/'DECISION_APROBADA.json',decision);dump(O/'CRITERIO_COMPLEMENTARIO_PROPUESTO.json',criterion);dump(O/'PRUEBAS_CONTROLES.json',tests)
result={'clasificacion':'D cierre interno; B evidencia; C conteos; E atribución documental','cierres_internos_aplicados':7,'personas_del_cierre':4,'codigo':CODE,'antes':counts(before,'codigo_interno_adoptado'),'despues':counts(after,'codigo_interno_adoptado'),'documental':counts(after,'codigo_documental_atribuible'),'cinco_propuestas_no_aplicadas':{'observaciones':5,'personas':3,'vias':dict(collections.Counter(x['criterio_evaluado']['via'] for x in assess))},'escenario_si_se_aprueban_las_cinco':scenario,'universo_conservado':{'personas':5901,'expedientes_aprobados':6622,'observaciones':24774},'operaciones_acumuladas':14,'asignaciones_acumuladas':13,'clasificaciones_sin_version_acumuladas':1}
dump(O/'RESULTADOS.json',result)
(O/'INFORME.md').write_text('''# Programación: siete cierres V1 y criterio para cinco pendientes

## Cierre autorizado — D, respaldado por B y registrado como C

Se aplicaron **siete cierres internos de cuatro personas**, TPAREOL20231/2024,
como **I162S2C57J4V1**. Corresponden exclusivamente a las observaciones con
continuidad personal MU2023–2024–2025, aprobación del plan/período y reportes
históricos revisados. La atribución documental continúa pendiente E: no se
acredita envío/aceptación SIES ni equivalencia universal del plan.

Pendientes internos: **3.088 → 3.081 observaciones**, todavía **1.750 personas**.
Documentales: **3.213 observaciones / 1.838 personas**, sin cambios. Las personas
del cierre conservan otros pendientes; no se cuenta como resuelta una persona
por cerrar solo algunas de sus observaciones.

## Criterio complementario propuesto — D, no aprobado ni aplicado

Para las cinco restantes proponemos usar **código personal de MU2024 + actividad
aprobada exacta de CODCLI/plan/período + respaldo histórico de continuidad o
actualización**, sin exigir una MU posterior no localizada. La ausencia de una
persona en MU2025 no invalida por sí misma su actividad y código en 2024.

| Observaciones | Personas | Evidencia particular B/C | Evaluación |
|---|---:|---|---|
| 2, TPAREOL20231, bimestres 2 y 4 de 2024 | 1 | V1 en MU2023 y MU2024; aprobación exacta; reportes del propio plan/período del 8–9 de julio y 5 de noviembre de 2024; actualización TPAS rechazada observada | Cumplen propuesta; no se imputa MU2025 |
| 1, TPAREOL20231, bimestre 2 de 2024 | 1 | V1 en MU2024; aprobación exacta y reportes del propio plan/período del 8–9 de julio; rechazo observado del nuevo plan | Cumple propuesta; no se inventan extremos MU2023/2025 |
| 2, TPAREOL20231 bimestre 2 y TPAS20241 trimestre 2 de 2024 | 1 | V1 personal MU2024; aprobación en cada plan; actualización del anterior registrada en DatosAlumnos; actividad aprobada del nuevo en 2024 y 2025 | Cumplen propuesta de correspondencia contextual en ambos planes; día administrativo pendiente |

Las cinco conservan código adoptado vacío y atribución documental pendiente.
Para cada observación se verificaron aprobación no homologada/convalidada, identidad,
plan, año, período, régimen, código anual personal y evidencia contextual. Las tres
del plan anterior tienen aprobaciones en tres respaldos distintos; las dos de la
actualización, en cuatro. No se suman esas copias como estudiantes o eventos nuevos.

**Límites E:** el reporte fechado del plan anterior no se atribuye al plan nuevo.
La aprobación en TPAS20241 procede de PROMEDIOS, no de un supuesto reporte fechado
TPAS. Bimestre 2 y trimestre 2 no son equivalentes ni prueban una transición sin
solapamiento. FECHAMATRICULA y metadatos de guardado no dan el día del cambio o
rechazo. No se trasladan estados actuales hacia 2024. La evidencia permite proponer
una correspondencia interna por contexto; no afirmar que cada expediente fue enviado
con ese código en ese período ni que se titulara en una fecha determinada.

La propuesta es acotada a estas cinco observaciones; no resuelve otras homologaciones,
planes rechazados ni ausencias. El catálogo es un control de compatibilidad, no prueba
individual. Los controles previos sobre otras personas son de coherencia del diagnóstico,
no validación independiente de precisión ni motivo para una asignación por mayoría.

## Efecto eventual — C, escenario no aplicado

Si se aprueban las cinco propuestas, los pendientes internos pasarían de **3.081 a
3.076 observaciones**, con **1.750 personas** todavía pendientes. Los documentales
seguirían en **3.213 / 1.838**. No cambia ningún denominador ni tasa de retención.

## QA, archivos y reanudación

QA **OK_CON_ADVERTENCIAS**: siete cambios internos exactos, cero documentales,
cinco estados pendientes conservados, idempotencia, rechazo de estado incompatible
y 35 controles negativos del criterio propuesto. Estas pruebas verifican controles
técnicos; no miden precisión estadística de la equivalencia. Se verifican hashes
de las entradas anteriores y su conservación después de ejecutar.

Universo conservado: 5.901 personas, 6.622 expedientes aprobados y 24.774 observaciones.
Los originales, libros, bases, motor anual y denominadores no se modifican.
DECISION_APROBADA.json registra responsable Alexi, autorización textual, fecha/hora,
alerta de alcance y reversión. CRITERIO_COMPLEMENTARIO_PROPUESTO.json separa las
cinco de lo aprobado. Detalle privado por observación y catorce operaciones acumuladas
(trece asignaciones más clasificación TCRE) en la ruta del MANIFEST.json.

Siguiente paso: decisión sobre las cinco propuestas. Mantener atribución documental E.
Estado local reproducible; sin commit/push, sin publicación GitHub. Rama y HEAD
se conservan y quedan registrados antes/después.
''')
(O/'CHECKPOINT.md').write_text('# Reanudación\n\nAplicados siete cierres V1 de Programación por autorización de Alexi. Estado vigente: 3.081 observaciones / 1.750 personas pendientes internas; 3.213 / 1.838 documentales. Reconstruir desde base privada 20261023_004044 y ADJUDICACIONES_ACUMULADAS.json de esta ejecución (14 operaciones; 13 asignaciones + clasificación TCRE). Otras cinco de tres personas cumplen criterio complementario propuesto, no aprobado ni aplicado; consultar CINCO_CRITERIO_COMPLEMENTARIO.json privado. No confundir fechas del plan anterior con nuevo ni períodos bimestrales/trimestrales. Con eventual aprobación, 3.076/1.750 internos; documental intacto. Sin commit/push ni modificaciones a bases o denominadores.\n')
for p in [Path(__file__),R/'docs/ESPECIFICACION_CIERRE_SIETE_V1_PROGRAMACION_20261023.md']:src(p)
qa['fuentes_intactas']=all(sha(p)==h for p,h in H.items());assert qa['fuentes_intactas']
qa['privados_0600']=all((f.stat().st_mode & 0o077)==0 for f in Q.iterdir());assert qa['privados_0600']
ga=git();assert (gb['rama'],gb['HEAD'])==(ga['rama'],ga['HEAD']);dump(O/'GIT_DESPUES.json',ga);dump(O/'QA.json',qa);dump(O/'FUENTES_HASHES.json',H)
secrets={x['persona'] for x in base}|{x['CODCLI'] for x in base}
for f in O.iterdir():assert not any(k and k in f.read_text() for k in secrets),str(f)
dump(O/'MANIFEST.json',{'fecha_hora':now.isoformat(),'fuentes_hashes':H,'salidas_hashes':{f.name:sha(f) for f in O.iterdir()},'privado':str(Q),'privados_hashes':{f.name:sha(f) for f in Q.iterdir()},'resultado':result,'qa':qa,'rama':ga['rama'],'HEAD':ga['HEAD'],'commit_push':False,'estado_publicacion':'Local no publicado'})
print(json.dumps({'salida':str(O),'privado':str(Q),'resultado':result,'QA':qa['estado']},ensure_ascii=False))
