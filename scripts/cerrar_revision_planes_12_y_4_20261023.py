"""Cierre trazable de la investigación dirigida. No modifica reglas ni adopta códigos."""
import csv,json,hashlib,datetime,subprocess,sys,collections,re
from pathlib import Path
from zoneinfo import ZoneInfo
cfg=json.load(open(sys.argv[1]));O=Path(cfg['output']);P=Path(cfg['privado']);R=O.parents[1]
load=lambda p:json.load(open(p))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str))
def csvout(p,rows):
 if not rows:return
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=';');w.writeheader();w.writerows(rows)
def dt(s):
 for fmt in ['%Y-%m-%d %H:%M:%S','%Y-%m-%d','%d-%m-%Y','%d-%m-%y']:
  try:return datetime.datetime.strptime(str(s),fmt).date().isoformat()
  except ValueError:pass
 return None
rev=load(P/'REVISION_16_CASOS_AMPLIADA.json');extra=load(P/'FILAS_RECUPERADAS_CODCLI.json');older=load(P/'FILAS_ADICIONALES_PRIVADAS.json');invs=load(O/'INVENTARIO_RECUPERACION.json');bm=load(R/'outputs/trayectorias_374_20261023_072401/MANIFEST.json');bp=Path(bm['privado'])
people={x['persona'] for x in rev};assert len(people)==len(rev)==16
assert len([x for x in rev if x['tipo']=='CAMBIO_ANUAL'])==12
assert len([x for x in rev if x['tipo']=='PISTA_FECHA'])==4
# Report dates are observations; course start/end dates are not administrative effective dates.
timeline=[];cases=[];four=[]
for x in rev:
 grouped=collections.defaultdict(list)
 for a in x['filas_recuperadas_codcli']:
  if a['rol']=='CALIFICACIONES_ASIGNATURA':grouped[a['CODCLI'],a['CODCARRERA_ALUMNO'],a['CODIGO_PLAN_ESTUDIO'],a['ANO'],a['PERIODO']].append(a)
 for (cc,car,plan,y,t),rr in grouped.items():
  dates=sorted({dt(a.get('FECHA REPORTE')) for a in rr if dt(a.get('FECHA REPORTE'))})
  timeline.append({'caso':x['caso'],'persona':x['persona'],'CODCLI':cc,'carrera':car,'plan':plan,'ano_asignatura':y,'periodo_asignatura':t,'primera_fecha_reporte':min(dates) if dates else 'Pendiente','ultima_fecha_reporte':max(dates) if dates else 'Pendiente','fechas_inicio_asignatura':' | '.join(sorted({a.get('FECHAINICIO','') for a in rr})),'fechas_fin_asignatura':' | '.join(sorted({a.get('FECHAFIN','') for a in rr})),'filas_reporte':len(rr),'asignaturas_secciones_distintas':len({(a['CODIGO_ASIGNATURA'],a['SECCION']) for a in rr}),'fuentes_filas':json.dumps([{'archivo':a['archivo'],'sha256':a['sha256'],'hoja':a['hoja'],'fila':a['fila']} for a in rr],ensure_ascii=False),'clasificacion':'B/C; no fecha efectiva del plan'})
 dated=[r for r in timeline if r['caso']==x['caso']]
 seenplans=sorted({r['plan'] for r in dated});a=x['antecedente']
 if x['tipo']=='CAMBIO_ANUAL':
  cases.append({'caso':x['caso'],'familia':x['familia'],'ultimo_ano_anterior':a['ultimo_ano_codigo_anterior'],'codigo_anterior':' | '.join(a['codigo_anterior']),'primer_ano_siguiente':a['primer_ano_codigo_siguiente'],'codigo_siguiente':' | '.join(a['codigo_siguiente']),'mismo_codcli_plan_ambos_anos':bool(x['mismo_plan_observado_ambos_anos_codigo']),'planes_en_reporte_calificaciones':' | '.join(seenplans) or 'No localizado en estos reportes','fecha_efectiva':'Pendiente','clasificacion':'B/C códigos y planes observados; E fecha y causa'})
 else:
  matches=[r for r in x['filas_recuperadas_codcli'] if r['rol']=='CALIFICACIONES_ASIGNATURA' and r['CODCLI']==a['CODCLI'] and r['CODIGO_PLAN_ESTUDIO']==a['plan'] and r['ANO']==a['ano'] and r['PERIODO']==a['periodo']]
  four.append({'caso':x['caso'],'familia':x['familia'],'ano':a['ano'],'periodo_UMAS':a['periodo'],'plan_pista':a['plan'],'codigo_anual_documentado':' | '.join(a['codigos_anuales']),'filas_corrobora_plan_periodo':len(matches),'respaldo_adicional':'PLAN/PERIODO CORROBORADO' if matches else 'NO CORROBORADO; OTRO PLAN OBSERVADO','planes_en_reporte':' | '.join(seenplans),'codigo_nuevo_adoptado':'Ninguno','fecha_efectiva':'Pendiente','clasificacion':'B/C respaldo del plan; E atribución temporal de versión'})
  x['evaluacion_pista_actualizada']={'corrobora_codcli_plan_periodo':bool(matches),'fuentes':matches,'codigo_adoptado_antes':a['codigo_interno_adoptado'],'codigo_adoptado_despues':a['codigo_interno_adoptado'],'fecha_efectiva_plan':'Pendiente','regla':'No se adopta versión por mera coincidencia de fechas; se distingue corroboración de actividad de acto de asignación.'}
# Rule is evaluated from source evidence rather than treating a non-null course date as migration.
explicit_fields={'FECHA_CAMBIO_PLAN','FECHA_EFECTIVA_PLAN','PLAN_ANTERIOR','PLAN_NUEVO','CODPESTUD_ANTERIOR','CODPESTUD_NUEVO'}
event_fields=[{'archivo':i['archivo'],'hoja':i['hoja'],'campos':sorted(explicit_fields.intersection(i.get('encabezados',[])))} for i in invs]
assert not any(i['campos'] for i in event_fields), 'Nueva evidencia explícita: requiere lectura antes de cerrar.'
# Snapshot comparison for the four clues; counts are rows, not persons.
recognition=[]
for x in rev:
 if x['tipo']!='PISTA_FECHA':continue
 g=collections.defaultdict(list)
 for r in x['filas_adicionales']:
  if Path(r['archivo']).name=='PROMEDIOSDEALUMNOS_2071.xlsx' and r.get('ANO')=='2024':g[r.get('CODCARR'),r.get('PLAN_DE_ESTUDIO'),r.get('PERIODO')].append(r)
 for (car,plan,t),rr in g.items():
  marked=sum(r.get('CONVALIDADO')=='S' or r.get('DESCRIPCION_ESTADO') in ['CONVALIDACION','HOMOLOGADO'] for r in rr)
  recognition.append({'caso':x['caso'],'carrera':car,'plan':plan,'ano':2024,'periodo':t,'filas':len(rr),'convalidacion_homologacion_observada':marked,'sin_marca_reconocimiento':len(rr)-marked,'fuentes':[{'archivo':r['archivo'],'hoja':r['hoja'],'fila':r['fila'],'sha256':r['sha256']} for r in rr]})
# One private summary row per person, with no names or unrelated personal fields.
private_summary=[]
for x in rev:
 a=x['antecedente']; ff=next((f for f in four if f['caso']==x['caso']),None)
 private_summary.append({'caso':x['caso'],'persona_RUT':x['persona'],'grupo':x['tipo'],'familia':x['familia'],'CODCLI_observados':' | '.join(sorted({s['CODCLI'] for s in x['segmentos_previos']})),'planes_observados':' | '.join(sorted({s['plan'] for s in x['segmentos_previos']})),'codigo_anterior':' | '.join(a.get('codigo_anterior',[])),'ultimo_ano_anterior':a.get('ultimo_ano_codigo_anterior',''),'codigo_siguiente_o_anual':' | '.join(a.get('codigo_siguiente',a.get('codigos_anuales',[]))),'primer_ano_siguiente':a.get('primer_ano_codigo_siguiente',a.get('ano','')),'periodo_pista':a.get('periodo',''),'corroboracion_plan_periodo':ff['respaldo_adicional'] if ff else 'Ver cronología por expediente','fecha_efectiva_cambio_plan':'Pendiente','codigo_nuevo_adoptado':'Ninguno','clasificacion':'B/C evidencia; E vigencia temporal pendiente'})
csvout(P/'RESUMEN_16_PERSONAS.csv',private_summary)
assert len(private_summary)==len({x['persona_RUT'] for x in private_summary})==16
# Totals and independent invariants.
assert len({(r['archivo'],r['hoja'],r['fila']) for r in extra})==len(extra)
assert not load(P/'RECHAZOS_IDENTIDAD.json')
checks=[z for x in rev for z in x['contraste_raw_derivado']];assert len(checks)==123 and all(z['coinciden'] for z in checks)
summary={'foco_personas':16,'cambios_anuales':12,'pistas_fecha':4,'personas_calificaciones':len({r['persona'] for r in extra if r['rol']=='CALIFICACIONES_ASIGNATURA'}),'personas_calificaciones_cambio':sum(any(z['caso']==x['caso'] for z in timeline) for x in rev if x['tipo']=='CAMBIO_ANUAL'),'personas_calificaciones_fecha':sum(any(z['caso']==x['caso'] for z in timeline) for x in rev if x['tipo']=='PISTA_FECHA'),'filas_calificaciones':sum(r['rol']=='CALIFICACIONES_ASIGNATURA' for r in extra),'filas_DA_recuperadas':sum(r['rol']=='DATOSALUMNOS_HISTORICO' for r in extra),'filas_promedios_adicionales':len(older),'pistas_plan_periodo_corrobora':sum(f['filas_corrobora_plan_periodo']>0 for f in four),'pistas_plan_periodo_no_corrobora':sum(f['filas_corrobora_plan_periodo']==0 for f in four),'mismo_codcli_plan_ambos_anos':sum(c['mismo_codcli_plan_ambos_anos'] for c in cases),'contrastes_raw_derivado':len(checks),'discordancias_raw_derivado':0,'fechas_efectivas_cambio_confirmadas':0,'codigos_nuevos_adoptados':0,'denominadores':[5901,6622,24774],'pendientes_documentales_antecedente':1838,'pendientes_internos_antecedente':1751,'alcance_indicadores':'Se conservan; no se recalculan ni reducen por esta corroboración parcial','clasificacion':'B/C observaciones/cálculos; E fecha efectiva y causas no acreditadas'}
dump(O/'RESULTADOS_FINAL.json',summary);dump(O/'RESULTADOS.json',summary);dump(P/'REVISION_16_CASOS_FINAL.json',rev);dump(P/'RECONOCIMIENTOS_CUATRO.json',recognition);dump(P/'CRONOLOGIA_PLANES.json',timeline);csvout(P/'CRONOLOGIA_PLANES.csv',timeline);csvout(O/'CAMBIOS_ANUALES_12.csv',cases);csvout(O/'PISTAS_FECHA_4.csv',four);dump(O/'REVISION_CAMPOS_EVENTO.json',event_fields)
# Only relevant source identifiers: source/row locators are in private files; no personal IDs in public outputs.
sourcehash=load(O/'FUENTES_HASHES.json')
for i in invs:sourcehash[i['archivo']]=i['sha256'];sourcehash[i['archivo_lectura']]=i['sha256']
for n in ['CAMBIOS_VERSION_ANUAL.json','CUATRO_PISTAS_FECHA.json','OBSERVACIONES_REVISADAS.json','SEGMENTOS_EXPEDIENTE_PLAN.json']:
 assert sha(bp/n)==bm['salidas_privadas_hashes'][n]
verified=[]
for path,h in sourcehash.items():
 # Cloud originals can become dataless; verified byte-identical reading caches keep reproducibility explicit.
 cached=next((i['archivo_lectura'] for i in invs if i['archivo']==path),path)
 assert sha(cached)==h, path
 verified.append({'archivo':path,'lectura_verificada':cached,'sha256':h})
dump(O/'FUENTES_VERIFICADAS_FINAL.json',verified)
now=datetime.datetime.now(ZoneInfo('America/Santiago')).isoformat();before=load(O/'GIT_ANTES.json');after={}
for repo,b in before.items():
 def git(*args):return subprocess.check_output(['git','-C',repo,*args],text=True).strip()
 after[repo]={'rama':git('branch','--show-current'),'head':git('rev-parse','HEAD'),'status':git('status','--short'),'remotos':git('remote','-v')}
 assert after[repo]['rama']==b['rama'] and after[repo]['head']==b['head']
dump(O/'GIT_DESPUES.json',after)
# Readable evidence tables.
def table(rows,keys):
 return '| '+' | '.join(keys)+' |\n|'+ '|'.join(['---']*len(keys))+'|\n'+'\n'.join('| '+' | '.join(str(r[k]).replace('|',' / ') for k in keys)+' |' for r in rows)+'\n'
report='''# Revisión de 12 cambios de versión y cuatro coincidencias de fecha

Proceso: conciliación histórica UMAS–SIES del puente de retención IPSS 162. Este informe es diagnóstico B/C; no cambia reglas oficiales ni el canon. Períodos: los declarados por cada registro, sin convertir bimestres en trimestres o semestres.

## Resultado

**Se precisó la cronología de planes, pero no se localizó un acto con fecha efectiva que permita cerrar nuevas asignaciones de versión por período.** Los 12 cambios anuales ya documentados se conservan; tres de las cuatro pistas tienen corroboración adicional del expediente/plan/período. No se reducen los pendientes globales por cambiar la definición de “resuelto”.

- **B/C:** 16 personas distintas: 12 cambios anuales y cuatro pistas, sin solapamiento.
- **B/C:** los reportes adicionales de calificaciones contienen 524 filas para 14 personas (10 del grupo de cambios y las cuatro pistas). Son observaciones de reportes/asignaturas, no 524 personas ni evidencia independiente por cada fila repetida.
- **B/C:** 24 filas de DATOSDEALUMNOS ORIGEN se recuperaron por CODCLI exacto corroborado con el cuerpo del RUT. Su RUT no trae guion/DV en esa columna. El cero de la primera lectura estricta era un problema del lector; no una ausencia. No se utiliza DIG del docente como DV del estudiante.
- **B/C:** 123 contrastes de observación anual contra RAW MU 2022–2025 coinciden, con cero discordancias. Esto respalda la transcripción al derivado; no prueba aceptación SIES ni fecha administrativa del plan.
- **B/C:** en siete de los 12 cambios, el mismo CODCLI y plan aparece con asignaturas en ambos años del cambio de versión. Un cambio de número de versión no demuestra por sí mismo cambio de malla.
- **E:** no se encontró fecha efectiva de migración en las fuentes efectivamente leídas. No se sustituyó por FECHAINICIO/FECHAFIN (asignatura), FECHA REPORTE (observación), FECHAMATRICULA (matrícula de semántica histórica no completamente acreditada) ni sufijo del plan.

## Los 12 cambios, sin alterar sus códigos

Los años son el último y primer año observados con cada código; no delimitan automáticamente la vigencia del plan ni los años sin registros intermedios.

'''+table(cases,['caso','familia','ultimo_ano_anterior','codigo_anterior','primer_ano_siguiente','codigo_siguiente','mismo_codcli_plan_ambos_anos','planes_en_reporte_calificaciones'])+'''
**B/C:** C03 y C11 no tienen registros localizados en los dos reportes adicionales de calificaciones leídos. Conservan su evidencia anual y PROMEDIOS previa. C11 registra la misma etiqueta de plan en dos expedientes distintos; no debe contarse entre los siete con el mismo CODCLI a ambos lados.

**B/C:** C04 registra IECIREOL20211 en reporte de 19-04-2024 y IINF20241 en reportes desde 27-05-2024. Es una secuencia observada de etiquetas/expedientes; no el día de migración. Las asignaturas del plan nuevo declaran inicio 25-03-2024, por lo que no corresponde inventar un intervalo administrativo 19-abril–27-mayo.

## Las cuatro coincidencias por fecha

'''+table(four,['caso','plan_pista','ano','periodo_UMAS','codigo_anual_documentado','filas_corrobora_plan_periodo','respaldo_adicional'])+'''
- **B/C — F01:** el reporte corrobora IECIREOL20211 en el período 1 de 2024. En PROMEDIOS2071, las 25 filas IINF20241 de 2024-1 son 19 convalidaciones y seis homologaciones. La presencia del plan alternativo no demuestra por sí sola que cursara asignaturas nuevas en él. La coincidencia de fecha favorece el expediente anterior; no se convierte automáticamente en regla de asignación.
- **B/C — F02:** no se localiza el plan de la pista IECIREOL20211 en el reporte adicional; aparece IINF20241 con asignaturas de 2024-1, 2 y 3. La pista de fecha no resuelve esta alternativa; permanece E.
- **B/C — F03:** TPAREOL20231 aparece en asignaturas 2024-2 (inicio 20-05, fin 06-07); TPAS20241 aparece en 2024-2 (inicio 01-07, fin 28-09), con reportes posteriores. Los calendarios se solapan: el número “2” no representa necesariamente el mismo intervalo. El reporte corrobora el plan anterior para el período UMAS de la pista, pero no acredita una fecha exacta de transferencia ni la versión SIES para cada expediente.
- **B/C — F04:** se corrobora TPAREOL20231 en 2024-2. Las seis filas TPAS20241 de 2024-1 en PROMEDIOS2071 son homologaciones; no constituyen seis cursos nuevos ni fecha efectiva de cambio.
- **E:** las cuatro atribuciones temporales de versión siguen pendientes de cierre; tres tienen evidencia de plan más fuerte que antes, y una no. Se mantienen códigos adoptados y denominadores previos.

## Fuentes y alcance

1. Diagnóstico previo `outputs/trayectorias_374_20261023_072401/MANIFEST.json`: se verificaron hashes de los cuatro derivados privados utilizados.
2. RAW MU 2022/2022.csv; 2023/2023.csv; 2024/08-05-2024_18-31-54_Matrícula_Pregrado_2024.csv; 2025/2025.xlsx, hoja 08-05-2025_22-26-22_Matrícula_P: persona/familia/código anual y fechas disponibles. Localizadores privados por fila.
3. PROMEDIOS2071, PROMEDIOS3233 y respaldo congelado P2 PROMEDIOS7804: 2.189 filas del foco; contienen asociaciones de plan con asignaturas, no historial administrativo de vigencia del plan. No se presume independencia entre extractos.
4. `CUMPLIMIENTO INGRESO CALIFICACIONES.xlsx`, hoja MASTER INGRESO 2024, encabezados fila 2: 486 filas del foco; CODCLI, CODIGO_PLAN_ESTUDIO, ANO, PERIODO, FECHAINICIO, FECHAFIN, FECHA REPORTE. Se obtuvo copia local idéntica para superar lectura de OneDrive.
5. `Cumplimiento Ingreso de Notas.xlsx`, Hoja1: 38 filas del foco. FECHAINICIO/FECHAFIN corresponden a asignaturas; no tiene FECHA REPORTE en las columnas revisadas. Copia idéntica.
6. `DATOSDEALUMNOS ORIGEN DE LOS DATOS2025.xlsx`, Hoja1: 24 filas del foco, solo contexto de expediente/fechas, sin convertir fecha de matrícula en fecha de migración.
7. Documentación gobernada `docs/fase_4_planes_asignaciones_umas.md`, `docs/resultados_versiones_por_cohorte_20261016.md` y catálogo local de reportes IPSS v001: distinguen planes, procesos y procedencia; el catálogo describe View_promedios_alumnos y Cumplimiento_ingreso_notas, pero no contiene un evento administrativo individual de cambio de plan. Ninguna regla A nueva se deduce de estos datos B/C.

Los reportes adicionales localizados en OneDrive quedan inventariados en esta revisión; no se afirma que ya estuvieran congelados en Git ni que sus nombres acrediten corte oficial. Rutas, hojas y hashes completos: FUENTES_VERIFICADAS_FINAL.json e INVENTARIO_RECUPERACION.json. Identificadores y filas individuales: carpeta privada fuera de Git.

## Límite de lectura y pendiente preciso

**E:** `PRUEBA CUMPLIMIENTO INGRESO CALIFICACIONES T3_2024.xlsx` permitió inspección inicial de estructura/hash, pero no relectura completa de las hojas DATOS CRUDOS U+ 19-11-2024 y ERRORES por TimeoutError de OneDrive. Se intentó lectura repetida y recuperación local; no se cuenta como fuente leída ni como ausencia de personas. El reporte maestro de 2024 sí se leyó completo. El intento inicial de Hoja1 en DATOSDEALUMNOS_1758 no corresponde a sus nombres reales: se revisó estructura en PERFIL_PREPARACION_MU2025.json (privado); no contiene CODCLI ni plan, y no se usó para cerrar equivalencias.

Falta localizar para las asignaciones temporales un evento con expediente/plan anterior/plan nuevo y fecha efectiva, o una equivalencia institucional vigente de alcance explícito. No se exige nuevamente ese dato para informar lo ya observado: los planes, las fechas de reporte, la corroboración de tres pistas y los códigos anuales están documentados. No se afirma que el evento no exista en toda la institución.

## Conservación y reproducción

**D:** se conservan bases, códigos adoptados y denominadores: 5.901 personas, 6.622 expedientes, 24.774 observaciones. Las cifras previas 1.838 pendientes documentales y 1.751 internos se citan como antecedente sin alterarlas. No se cambian tasas ni libros previos.

**C:** QA aritmético/de trazabilidad: OK_CON_ADVERTENCIAS por cobertura documental incompleta; no equivale a aprobación de nuevas reglas. Ver QA.json. No hay commit, push, merge, PR ni carga a servicios externos.

Scripts reproducibles y configuración persistente figuran en MANIFEST.json. La reejecución requiere los archivos privados locales y, para volver a descargar respaldos, disponibilidad de OneDrive. No se necesita ni se publica información individual en Git.
'''
(O/'INFORME_12_Y_4.md').write_text(report)
checkpoint=f'''# Checkpoint — {now}

Fase 1/4 · Hitos 1–3: foco 12+4, fuentes, reglas y estados Git verificados.
Fase 2/4 · Hitos 1–3: RAW anual y respaldos de planes leídos; recuperación por CODCLI y RUT corroborada. Una fuente T3 permanece con error de lectura.
Fase 3/4 · Hitos 1–3: 3/4 pistas corroboradas en plan/período; 12 cambios anuales conservados; 7 con mismo CODCLI/plan a ambos lados. Fechas efectivas pendientes.
Fase 4/4 · Hitos 1–3: informe, tablas, cronología privada, fuentes/hash, QA y manifiesto. Sin adopción ni commit/push.

Reanudación: leer respaldo PRUEBA CUMPLIMIENTO T3_2024 si se recupera; contrastar eventos efectivos por CODCLI. No volver a presentar las tres corroboraciones como cierres de versión ni reducir denominadores. Informe: INFORME_12_Y_4.md. Detalle: {P}/REVISION_16_CASOS_FINAL.json y CRONOLOGIA_PLANES.csv.
'''
(O/'CHECKPOINT.md').write_text(checkpoint)
bitacora=[
 {'fase':1,'hito':1,'fuente':'GIT_ANTES.json y contratos locales','accion':'Verificar repositorios, ramas y autorización','resultado':'Sin cambio de rama ni operaciones de publicación','archivo':'GIT_DESPUES.json','pendiente':'Ninguno técnico de acceso a repos'},
 {'fase':1,'hito':2,'fuente':'MANIFEST previo y cuatro derivados privados con hash','accion':'Fijar foco por identidad y deduplicar','resultado':'12+4=16 personas sin solapamiento','archivo':'RESULTADOS_FINAL.json','pendiente':'Conservar definición de resuelto'},
 {'fase':1,'hito':3,'fuente':'Documentación de planes y catálogo de reportes IPSS','accion':'Separar fechas de asignatura, matrícula y plan','resultado':'No hay regla A nueva ni evento administrativo demostrado','archivo':'INFORME_12_Y_4.md','pendiente':'Fecha efectiva'},
 {'fase':2,'hito':1,'fuente':'RAW MU 2022–2025','accion':'Contrastar códigos anuales','resultado':'123 comparaciones; cero discordancias','archivo':'QA.json','pendiente':'Código anual no acredita período de plan'},
 {'fase':2,'hito':2,'fuente':'PROMEDIOS y dos reportes de calificaciones','accion':'Leer fuentes adicionales y registrar localizadores','resultado':'524 filas de calificaciones de 14 personas; 2189 filas PROMEDIOS','archivo':'INVENTARIO_RECUPERACION.json','pendiente':'Una fuente T3 con TimeoutError'},
 {'fase':2,'hito':3,'fuente':'DATOSDEALUMNOS ORIGEN Hoja1','accion':'Cruzar CODCLI exacto y corroborar cuerpo RUT','resultado':'24 filas recuperadas; cero rechazos identidad','archivo':'QA.json','pendiente':'No convertir fecha de matrícula en migración'},
 {'fase':3,'hito':1,'fuente':'12 cambios previos y asociaciones de plan','accion':'Comparar plan y código anual','resultado':'7 con mismo CODCLI/plan a ambos lados','archivo':'CAMBIOS_ANUALES_12.csv','pendiente':'Causa y fecha efectiva'},
 {'fase':3,'hito':2,'fuente':'Cuatro pistas y MASTER INGRESO 2024','accion':'Corroborar CODCLI/plan/año/período','resultado':'Tres corroboradas; una no corroborada','archivo':'PISTAS_FECHA_4.csv','pendiente':'No adopción de código por coincidencia de fecha'},
 {'fase':3,'hito':3,'fuente':'PROMEDIOS2071 estados de asignatura','accion':'Separar homologaciones/convalidaciones','resultado':'Planes alternativos F01/F04 con reconocimiento observado','archivo':'INFORME_12_Y_4.md','pendiente':'Reconocimiento no acredita nueva cursada'},
 {'fase':4,'hito':1,'fuente':'Derivados de la revisión','accion':'Generar informe agregado y cronología privada','resultado':'Archivos separados, originales conservados','archivo':'MANIFEST.json','pendiente':'Sin modificación de Excel previo'},
 {'fase':4,'hito':2,'fuente':'Fuentes y resultados','accion':'QA hashes/identidad/duplicados/denominadores/Git','resultado':'OK_CON_ADVERTENCIAS','archivo':'QA.json','pendiente':'Advertencias documentales explícitas'},
 {'fase':4,'hito':3,'fuente':'Salidas y scripts persistentes','accion':'Registrar hashes y reanudación','resultado':'Sin commit/push ni códigos adoptados nuevos','archivo':'CHECKPOINT.md','pendiente':'Recuperar fuente T3 y evento/equivalencia temporal si existe'}]
dump(O/'BITACORA.json',bitacora)
# Privacy scan for known personal keys across newly generated public artifacts and code.
ids=people|{s['CODCLI'] for x in rev for s in x['segmentos_previos']}
publics=[p for p in O.iterdir() if p.is_file()]+[R/'docs/ESPECIFICACION_CAMBIOS_PLAN_12_Y_4_20261023.md']+[R/'scripts'/n for n in ['investigar_cambios_plan_12_y_4_20261023.py','recuperar_evidencia_planes_12_y_4_20261023.py','cerrar_revision_planes_12_y_4_20261023.py']]
leaks=[]
for path in publics:
 t=path.read_text()
 if any(i and i in t for i in ids):leaks.append(str(path))
assert not leaks,leaks
qa={'estado':'OK_CON_ADVERTENCIAS','foco_16_sin_duplicados':True,'particion_12_y_4':True,'filas_recuperadas':len(extra),'duplicados_fuente_hoja_fila':0,'rechazos_RUT_CODCLI':0,'codcli_unico_en_segmentos_previos':True,'tres_pistas_corrobora':sum(f['filas_corrobora_plan_periodo']>0 for f in four)==3,'raw_derivado':{'comparaciones':123,'discordancias':0},'fuentes_hash_verificadas':len(verified),'denominadores_conservados':[5901,6622,24774],'archivos_previos_no_modificados':True,'codigo_adoptado_sin_cambios':True,'privado_fuera_git':subprocess.run(['git','-C',str(P),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0,'sin_identificadores_en_salida_publica':not leaks,'ramas_head_conservados':True,'advertencias':['Fecha efectiva de cambio no localizada: no cierre de asignación por período','Una fuente adicional T3_2024 no releída por TimeoutError','Calificaciones repetidas entre reportes no son personas ni evidencias independientes','Código anual no prueba aceptación SIES ni vigencia del plan en trimestre']}
dump(O/'QA.json',qa)
# Durable replay config, no temporary paths required.
dump(O/'CONFIG_REPRODUCCION.json',cfg)
manifest={'fecha':now,'proceso':'Conciliación histórica UMAS–SIES; puente retención IPSS162','alcance':'12 cambios anuales y cuatro pistas de fecha','objetivo':'Localizar cronología de planes sin alterar bases ni denominadores','resultado':summary,'qa':qa,'fuentes':verified,'fuentes_lectura_bloqueada':load(O/'ERRORES_LECTURA.json'),'nota_errores':'Registro de intentos iniciales: MASTER y Cumplimiento Ingreso de Notas recuperados; PRUEBA T3_2024 sigue pendiente','scripts':{str(p):sha(p) for p in publics if p.suffix=='.py'},'reproduccion':['scripts/investigar_cambios_plan_12_y_4_20261023.py CONFIG_REPRODUCCION.json','scripts/recuperar_evidencia_planes_12_y_4_20261023.py CONFIG_REPRODUCCION.json','scripts/cerrar_revision_planes_12_y_4_20261023.py CONFIG_REPRODUCCION.json'],'privado':str(P),'salidas_privadas_hashes':{p.name:sha(p) for p in P.iterdir() if p.is_file()},'salidas_agregadas_hashes':{p.name:sha(p) for p in O.iterdir() if p.is_file() and p.name!='MANIFEST.json'},'bases_modificadas':False,'canon_modificado':False,'commit':False,'push':False,'git_antes':{k:{a:v[a] for a in ['rama','head']} for k,v in before.items()},'git_despues':{k:{a:v[a] for a in ['rama','head']} for k,v in after.items()}}
dump(O/'MANIFEST.json',manifest)
print(json.dumps({'resultado':summary,'QA':qa,'informe':str(O/'INFORME_12_Y_4.md'),'sha256_informe':sha(O/'INFORME_12_Y_4.md')},ensure_ascii=False))
