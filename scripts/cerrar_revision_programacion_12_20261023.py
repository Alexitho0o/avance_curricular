"""Cierra evidencia y escenarios de doce observaciones, sin adoptar códigos nuevos."""
import collections,copy,datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
from zoneinfo import ZoneInfo
os.umask(0o077)
O=Path(sys.argv[1]).resolve();R=O.parents[1];P=Path.home()/'.local/share/ipss'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
c=load(O/'CONFIG.json');Q=Path(c['privado']);H=load(O/'FUENTES_HASHES.json')
def src(p):H[str(p)]=sha(p);return p
for p,h in H.items():assert sha(p)==h,p
rows=load(Q/'FILAS_HISTORICAS.json');focus=load(Q/'FOCO_12.json');mu=load(Q/'MU_PERSONAS.json');labels=load(Q/'ETIQUETAS.json')
base=load(P/'reproduccion_puente_20261023_004044/OBSERVACIONES_PRIVADAS.json');pm=load(Path(c['anterior'])/'MANIFEST.json')
af=Path(pm['privado'])/'ADJUDICACIONES_ACUMULADAS.json';assert sha(af)==pm['privados_hashes'][af.name];src(af);ops=load(af)
state=copy.deepcopy(base);idx={x['observacion_id']:x for x in state}
for op in ops['adjudicaciones']:
 assert idx[op['observacion_id']]==op['estado_antes'];idx[op['observacion_id']]=copy.deepcopy(op['estado_despues'])
state=list(idx.values());ps={x['observacion']['persona'] for x in focus};CODE='I162S2C57J4V1'
# Catalog is a source-backed derived control, not proof of individual sending.
hp=R/'data/versiones_por_cohorte/20261016/historias_oferta.json';src(hp)
history=[x for x in load(hp) if x['familia']=='I162S2C57J4'];assert {x['codigo_unico'] for x in history}=={CODE}
assert any(y['anio']==2024 for x in history for y in x['anual'])
dump(O/'CONTROL_OFERTA.json',{'clasificacion':'B catálogo derivado; C consulta','fuente':str(hp),'sha256':sha(hp),'filas':history,'limite':'No demuestra atribución de persona a expediente ni aceptación SIES.'})
def reference(x):return {k:x[k] for k in ['archivo','sha256','hoja','fila'] if k in x}
def rec(x):return x.get('CONVALIDADO')=='S' or x.get('DESCRIPCIONESTADO') in ['HOMOLOGADO','CONVALIDACION']
def approved(x):return x.get('DESCRIPCIONESTADO')=='APROBADO' and not rec(x)
def date(s):
 for fmt in ['%Y-%m-%d %H:%M:%S','%Y-%m-%d','%d-%m-%Y','%d-%m-%y','%d/%m/%Y']:
  try:return datetime.datetime.strptime(s,fmt).date().isoformat()
  except ValueError:pass
 return None
def code(x):return 'I162S'+x['COD_SED']+'C'+x['COD_CAR']+'J'+x['JOR']+'V'+x['VERSION']
review=[];timelines=[]
for item in focus:
 x=item['observacion'];person=x['persona'];rr=[r for r in rows if r['persona']==person];same=[r for r in rr if r.get('CODCLI')==x['CODCLI'] and r.get('PLANDEESTUDIO')==x['plan'] and r.get('ANO')==x['ano'] and r.get('PERIODO')==x['periodo']]
 approves=[r for r in same if approved(r)];assert approves
 # The exact current-source observations must all be reread unchanged.
 for fr in item['filas_releidas']:
  match=[r for r in same if r['archivo']==fr['fuente'] and r['hoja']==fr['hoja'] and r['fila']==fr['fila']]
  assert len(match)==1 and match[0]['CODRAMO']==fr['CODRAMO'] and match[0]['DESCRIPCIONESTADO']==fr['DESCRIPCION_ESTADO'] and match[0]['CONVALIDADO']==fr['CONVALIDADO']
 target_mu=[r for r in mu if r['persona']==person and r['ANIO_INFORMADO']=='2024'];assert {code(r) for r in target_mu}=={CODE}
 years={y:sorted({code(r) for r in mu if r['persona']==person and r['ANIO_INFORMADO']==y and r['COD_CAR']=='57' and r['COD_SED']=='2' and r['JOR']=='4'}) for y in ['2023','2024','2025']}
 dated=[]
 for r in rr:
  if r.get('CODIGOPLANESTUDIO')!='TPAREOL20231':continue
  for key in ['FECHAREPORTE','FECHAMEDICION']:
   dt=date(r.get(key,''))
   if dt:dated.append({**reference(r),'fecha_observada':dt,'campo_fecha':key,'literal':r[key],'CODCLI':r['CODCLI'],'plan_observado':r['CODIGOPLANESTUDIO'],'ano':r.get('ANO'),'periodo_original':r.get('PERIODO'),'estado_academico_observado':r.get('ESTADOACADEMICO','')})
 assert dated
 rejected=[r for r in rr if r.get('CODCARPR')=='TPAS' and r.get('SITUACION')=='9 - RECHAZO ACTUALIZACION DE PLAN 2024']
 update=[r for r in rr if r.get('CODCARPR')=='TPAREOL' and r.get('SITUACION')=='10 - ACTUALIZACIÓN DE PLAN DE ESTUDIO 2024']
 otherplans=[r for r in rr if r.get('PLANDEESTUDIO')=='TPAS20241' and r.get('ANO') in ['2024','2025']]
 if years['2023']==[CODE] and years['2025']==[CODE]:group='A_CONTINUIDAD_MU_2023_2024_2025'
 elif rejected and years['2023']==[CODE]:group='B_CONTINUIDAD_MU_2023_2024_SIN_2025'
 elif rejected:group='C_MU_2024_MAS_CONTINUIDAD_ACADEMICA'
 else:
  assert update and any(approved(r) and r.get('ANO')=='2024' for r in otherplans) and any(approved(r) and r.get('ANO')=='2025' for r in otherplans)
  group='D_CAMBIO_PLAN_CON_ACTIVIDAD_EN_AMBOS'
 limits=['Atribución documental al expediente/período y aceptación SIES no acreditadas.', 'Fecha de matrícula/guardado no demuestra fecha de cambio o rechazo.']
 if group!='A_CONTINUIDAD_MU_2023_2024_2025':limits.append('Requiere aprobar criterio complementario: no hay extremos MU2023 y MU2025 concordantes disponibles para esta persona.')
 result={'observacion':x,'etiqueta_revision':labels[person],'grupo_revision':group,'codigo_propuesto':CODE,'codigo_adoptado':x['codigo_interno_adoptado'],'resultado':'PROPUESTA_CIERRE_INTERNO_NO_APLICADA','clasificacion':'B evidencia; C contraste; D propuesta no adoptada; E atribución documental/fecha efectiva',
 'regimen':sorted({r.get('REGIMEN') for r in same}),'aprobaciones_periodo':approves,'mu_2024':target_mu,'mu_por_ano':years,'reportes_fechados_plan_anterior':dated,'respaldo_rechazo_plan_nuevo':rejected,'respaldo_actualizacion_plan_anterior':update,'actividad_plan_nuevo':otherplans,'limites':limits,'estado_antes':idx[x['observacion_id']],'estado_despues_vigente':idx[x['observacion_id']]}
 assert not x['codigo_interno_adoptado'];review.append(result)
 if person not in {t['persona'] for t in timelines}:
  timelines.append({'persona':person,'etiqueta_revision':labels[person],'fechas_plan_anterior':sorted({r['fecha_observada'] for r in dated}),'reportes':dated,'rechazo_observado':bool(rejected),'actualizacion_observada':bool(update),'dia_efectivo_cambio_o_rechazo':None,'limite':'El primer y último reporte delimitan presencia observada; no son límites certificados de una transición.'})
assert len(review)==12
controls=[]
for plan in ['TPAREOL20231','TPAS20241']:
 a=[x for x in base if x['plan']==plan and x['ano']=='2024' and x['sede_dimension']=='2' and x['jornada_sies']=='4' and x['codigo_documental_atribuible'] and x['persona'] not in ps]
 controls.append({'plan':plan,'observaciones':len(a),'personas':len({x['persona'] for x in a}),'codigos':dict(collections.Counter(x['codigo_documental_atribuible'] for x in a)),'clasificacion':'B/C control del diagnóstico reproducido; personas del foco excluidas; no nuevo cierre documental','limite':'Control de coherencia externo al foco, no validación independiente del algoritmo que atribuyó el código.'})
 assert {x['codigo_documental_atribuible'] for x in a}=={CODE}
dump(O/'CONTROL_OTRAS_PERSONAS.json',controls)
def counts(a,k):
 p=[x for x in a if not x[k]];return {'observaciones':len(p),'personas':len({x['persona'] for x in p})}
current={'interno':counts(state,'codigo_interno_adoptado'),'documental':counts(state,'codigo_documental_atribuible')}
assert current=={'interno':{'observaciones':3088,'personas':1750},'documental':{'observaciones':3213,'personas':1838}}
scenarios=[]
for name,chosen in [('Solo continuidad MU2023–2024–2025',[x for x in review if x['grupo_revision'].startswith('A_')]),('Las doce propuestas, si se aprueba el criterio complementario',review)]:
 ids={x['observacion']['observacion_id'] for x in chosen};sim=copy.deepcopy(state)
 for x in sim:
  if x['observacion_id'] in ids:x['codigo_interno_adoptado']=CODE
 scenarios.append({'escenario_no_aplicado':name,'observaciones_propuestas':len(ids),'personas_en_foco':len({x['observacion']['persona'] for x in chosen}),'pendientes_simulados':counts(sim,'codigo_interno_adoptado'),'pendientes_documentales':counts(sim,'codigo_documental_atribuible'),'clasificacion':'C escenario; D aprobación pendiente'})
result={'observaciones_revisadas':12,'personas':len(ps),'expedientes_foco':len({x['observacion']['CODCLI'] for x in focus}), 'grupos':dict(collections.Counter(x['grupo_revision'] for x in review)), 'codigo_propuesto':CODE,'cierres_aplicados':0,'estado_vigente':current,'escenarios_no_aplicados':scenarios,'filas_historicas_con_repeticiones':len(rows),'fuentes_unicas':len({x['sha256'] for x in load(O/'INVENTARIO.json')}),'hojas_leidas':sum(x['estado']=='LEIDO' for x in load(O/'INVENTARIO.json')),'universo_conservado':{'personas':5901,'expedientes_aprobados':6622,'observaciones':24774}}
assert list(result['grupos'].values())==[7,2,1,2] or result['grupos']=={'A_CONTINUIDAD_MU_2023_2024_2025':7,'D_CAMBIO_PLAN_CON_ACTIVIDAD_EN_AMBOS':2,'C_MU_2024_MAS_CONTINUIDAD_ACADEMICA':1,'B_CONTINUIDAD_MU_2023_2024_SIN_2025':2}
dump(Q/'REVISION_12_POR_OBSERVACION.json',review);dump(Q/'CRONOLOGIAS_7_PERSONAS.json',timelines)
dump(O/'RESULTADOS.json',result)
report='''# Programación: continuidad y cambios de plan, doce observaciones de 2024

## Resultado

**Siete observaciones de cuatro personas permiten proponer cierre interno con el mismo
criterio de continuidad anual ya utilizado. Otras cinco observaciones de tres personas
cuentan con respaldo para una propuesta complementaria, que debe aprobarse de forma
explícita antes de aplicarla.** Las doce propuestas apuntan a **I162S2C57J4V1**.
No se aplicó ninguna: esta entrega responde qué podemos cerrar, no altera el estado
vigente. No hay nuevos cierres documentales.

| Grupo revisado | Observaciones | Personas | Evidencia y alcance | Clase |
|---|---:|---:|---|---|
| MU2023–2024–2025 concordante y continuidad en TPAREOL20231 | 7 | 4 | V1 personal en los tres años; aprobación exacta en el plan/período; reportes fechados en 2024; actualización TPAS rechazada observada | B/C; cierre interno propuesto D |
| MU2023–2024, sin registro MU2025 localizado | 2 | 1 | V1 personal en 2023 y 2024; aprobaciones en bimestres 2 y 4; continuidad fechada del plan anterior; TPAS con rechazo observado | B/C; criterio complementario propuesto D |
| MU2024 y continuidad académica del plan anterior | 1 | 1 | V1 personal 2024; aprobación bimestre 2; reportes del plan anterior entre abril y julio; TPAS con rechazo observado. Sin extremos MU2023/2025 | B/C; criterio complementario propuesto D |
| Cambio con actividad en ambos planes | 2 | 1 | TPAREOL20231 bimestre 2 y TPAS20241 trimestre 2; aprobaciones exactas, actualización en DatosAlumnos y actividad posterior del nuevo plan en 2025; V1 personal MU2024 | B/C; criterio complementario propuesto D |

Las categorías de personas de esta tabla son disjuntas: 7 personas y 12 observaciones.
El código anual por sí solo no atribuye un expediente: las propuestas lo combinan con
actividad por CODCLI, plan y período y con los respaldos históricos. Ninguna observación
se resuelve por número de versión dominante ni por el año escrito en el plan.

## Continuidad y actualización

**B:** en seis personas, TPAS20241 aparece con rechazo de actualización, mientras
la actividad aprobada del foco pertenece a TPAREOL20231. No trasladamos esas
aprobaciones ni V1 a sus homologaciones del plan rechazado. La fecha administrativa
del rechazo continúa E. Los estados actuales SUSPENDIDO/ELIMINADO/TITULADO no se
aplican retroactivamente al período 2024.

**B:** en la séptima persona sí se observa actividad aprobada en ambos planes en
2024, y continúa en TPAS20241 en 2025. DatosAlumnos registra la actualización del
plan anterior y el nuevo expediente aparece como alumno regular en unos respaldos
y titulado en otros. Esto respalda una actualización con actividad en destino;
no corresponde clasificarla como un simple reconocimiento en un plan rechazado.

**E:** el día administrativo efectivo del cambio no está acreditado. El plan anterior
aparece en reportes hasta el 5 de agosto de 2024, pero esa fecha no es una fecha de
migración. Bimestre 2 y trimestre 2 conservan su unidad; no se convierten en el mismo
período ni se afirma que no se superponen. La propuesta V1 para ambos contextos es
interna y contextual, no prueba de dos envíos SIES ni equivalencia universal de planes.

## Controles y límites

**B/C:** las siete personas tienen V1 en MU2024 para la familia C57/J4. En el catálogo
histórico consultado, esa familia solo presenta V1 (oferta observada 2020–2026,
incluido 2024). Esto no demuestra identidad individual. Como control fuera del foco,
el diagnóstico reproducido tiene 10 observaciones/5 personas de TPAREOL20231 y
519 observaciones/199 personas de TPAS20241 atribuidas documentalmente a V1 en
2024. No sumamos esas personas entre planes ni usamos mayoría para adoptar códigos.
Este es un control de coherencia del diagnóstico previo, no una nueva auditoría
independiente de sus 529 atribuciones.

**B/C:** se releyeron 21 fuentes distintas, 56 hojas granulares, con 1.058 filas del
foco contando repeticiones entre respaldos. No equivalen a 1.058 personas o eventos.
Las 12 filas de observaciones se verificaron contra sus filas de PROMEDIOS12166;
los respaldos antiguos tienen cobertura y estados de asignaturas diferentes y se
conservan por separado. Cero errores de lectura y cero alertas de identidad en esta
revisión. Se releyó MU directamente: 17 filas de las siete personas en 2022–2026.
Una persona tiene otra carrera C1/V3 en 2026; no se traslada esa versión a C57/2024.

## Estado vigente y escenarios separados

**C:** siguen pendientes internamente **3.088 observaciones / 1.750 personas**;
documentalmente **3.213 / 1.838**. No cambia el universo aprobado de 5.901 personas,
6.622 expedientes y 24.774 observaciones. No se recalcularon tasas de retención.

Si se aprobaran las siete primeras: quedarían 3.081 observaciones internas pendientes.
Si además se aprobaran las otras cinco: quedarían 3.076. En ambos escenarios siguen
1.750 personas con al menos un pendiente; las homologaciones y demás observaciones
fuera del foco no se cierran por asociación. El pendiente documental no cambia.
Son escenarios C, no resultados adoptados.

## Evidencias y reanudación

Detalle por observación y cronología por persona en almacenamiento privado local,
con fuente, hoja, fila, hash, CODCLI y persona original; véase MANIFEST.json.
INVENTARIO.json documenta cobertura y metadatos; RESULTADOS.json separa estado
vigente de escenarios; FUENTES_HASHES.json fija entradas y código. No se utilizan
fechas de guardado como fechas de eventos. Las fuentes sincronizadas no se alteran.

Siguiente paso: aprobar o rechazar por separado los siete cierres con continuidad
anual y las cinco propuestas complementarias. Mantener atribución documental E.
No se generan cambios al catálogo, a las bases, al Excel, a los denominadores o al
motor. Sin commit ni push: estos resultados son locales, no publicados en GitHub.
'''
# Assert all report literals against computed counts before saving.
assert result['fuentes_unicas']==21 and result['hojas_leidas']==56 and len(rows)==1058 and len(mu)==17
assert [s['pendientes_simulados'] for s in scenarios]==[{'observaciones':3081,'personas':1750},{'observaciones':3076,'personas':1750}]
(O/'INFORME.md').write_text(report)
(O/'CHECKPOINT.md').write_text('# Reanudación\n\nRevisadas 12 observaciones de Programación (7 personas): 7 propuestas con continuidad MU2023/2024/2025; 5 propuestas complementarias (2 con MU2023/2024, 1 solo MU2024 + continuidad académica, 2 de cambio real con actividad en ambos planes). Todas V1 I162S2C57J4V1. No adoptadas. No extrapolar a homologaciones ni confundir período bimestral/trimestral. Estado vigente conserva las siete operaciones acumuladas anteriores: seis asignaciones y una clasificación TCRE, 3.088/1.750 internos, 3.213/1.838 documentales. Usar detalle privado REVISION_12_POR_OBSERVACION.json y evidencia fuente/hoja/fila. Falta decisión sobre propuestas; atribución documental y día administrativo siguen pendientes.\n')
for name in ['scripts/revisar_programacion_12_20261023.py','scripts/cerrar_revision_programacion_12_20261023.py','docs/ESPECIFICACION_REVISION_PROGRAMACION_12_20261023.md']:src(R/name)
qa={'estado':'OK_CON_ADVERTENCIAS','12_observaciones_unicas':len({x['observacion']['observacion_id'] for x in review})==12,'7_personas':len(ps)==7,'12_con_aprobacion_exacta':all(x['aprobaciones_periodo'] for x in review),'codigo_objetivo_unico_2024':all({code(r) for r in x['mu_2024']}=={CODE} for x in review),'cero_errores_lectura':not load(O/'ERRORES.json'),'cero_alertas_identidad':not load(Q/'ALERTAS_IDENTIDAD.json'),'ningun_estado_adoptado_modificado':all(x['estado_antes']==x['estado_despues_vigente'] for x in review),'sin_duplicacion_observaciones':len(state)==24774,'personas_conservadas':len({x['persona'] for x in state})==5901,'expedientes_referencia_conservados':6622,'fuentes_intactas':all(sha(p)==h for p,h in H.items()),'advertencias':['5 propuestas necesitan criterio complementario aprobado.','Todas conservan atribución documental pendiente.','Fecha efectiva de cambio/rechazo no acreditada.','529 controles del diagnóstico previo no auditados nuevamente fila por fila.']}
assert all(v for v in qa.values() if isinstance(v,bool))
gb=load(O/'GIT_ANTES.json');ga={k:subprocess.check_output(['git','-C',str(R),*a],text=True).strip() for k,a in [('rama',['branch','--show-current']),('HEAD',['rev-parse','HEAD']),('status',['status','--short'])]};assert (gb['rama'],gb['HEAD'])==(ga['rama'],ga['HEAD'])
dump(O/'GIT_DESPUES.json',ga);dump(O/'QA.json',qa);dump(O/'FUENTES_HASHES.json',H)
secrets={x['persona'] for x in base}|{x['CODCLI'] for x in base}
for f in O.iterdir():
 if f.is_file():assert not any(k and k in f.read_text() for k in secrets),str(f)
dump(O/'MANIFEST.json',{'fecha_hora':datetime.datetime.now(ZoneInfo('America/Santiago')).isoformat(),'fuentes_hashes':H,'salidas_hashes':{f.name:sha(f) for f in O.iterdir() if f.name!='MANIFEST.json'},'privado':str(Q),'privados_hashes':{f.name:sha(f) for f in Q.iterdir()},'resultado':result,'qa':qa,'rama':ga['rama'],'HEAD':ga['HEAD'],'commit_push':False,'estado_publicacion':'Local, no publicado','reglas_adoptadas_nuevas':0})
print(json.dumps({'salida':str(O),'resultado':result,'QA':qa['estado']},ensure_ascii=False))
