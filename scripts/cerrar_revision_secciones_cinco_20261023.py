"""Finaliza revisión de secciones con evidencia fechada; no modifica el diccionario."""
from pathlib import Path
import json,sys,collections,subprocess,datetime,csv
from zoneinfo import ZoneInfo
import openpyxl
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
O=Path(sys.argv[1]);cfg=json.loads((O/'CONFIG.json').read_text());P=Path(cfg['privado']);H=dict(cfg['fuentes_hashes'])
assert subprocess.run(['git','-C',str(P),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
assert not (O/'MANIFEST.json').exists()
def val(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
def dump(p,x):
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
 if p.is_relative_to(P):p.chmod(0o600)
def read(p):
 p=Path(p);H[str(p)]=sha256(p);return json.loads(p.read_text())
a=read(P/'DETALLE.json');targets=a['objetivos'];bycase={r['caso']:r for r in targets}
s=DiccionarioSiesSeguimiento();bodies=collections.defaultdict(set)
for (person,) in s.db.execute('select distinct persona from observaciones union select distinct persona from mu_anual'):bodies[person.split('-')[0]].add(person)
for r in targets:assert bodies[r['persona'].split('-')[0]]=={r['persona']}
# RUT_ALUMNO in these two reports is the body only. No DV is fabricated.
root=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/Indicadores Intermedios Academicos VRA')
source=root/'GESTIONSGE_1703.xlsx';H[str(source)]=sha256(source)
w=openpyxl.load_workbook(source,read_only=True,data_only=True);it=iter(w['Hoja1'].values);headers=list(next(it));contacts=[]
for n,row in enumerate(it,2):
 if n not in [12428,12436,12427]:continue
 d=dict(zip(headers,row));assert val(d['RUT_ALUMNO'])==bycase['INF35-04']['persona'].split('-')[0];assert d['CODCARR']=='IINF'
 # Only records directly relevant to journey; no other personal contact notes retained.
 contacts.append({'caso':'INF35-04','persona':bycase['INF35-04']['persona'],'fuente':str(source),'hoja':'Hoja1','fila':n,'sha256':H[str(source)],'fecha_comunico':val(d['FECHA_COMUNICO']),'asunto':d['Asunto'],'observacion':d['OBSERVACION'],'carrera':d['CODCARR'],'metodo':'RUT_ALUMNO sin DV exacto + IINF; cuerpo único entre identidades del diccionario; DV no informado por la fuente'})
w.close();assert len(contacts)==3
assert 'diurna' in next(r['observacion'] for r in contacts if r['fila']==12436).lower()
assert 'cambio de ornada' in next(r['observacion'] for r in contacts if r['fila']==12427).lower()
# Reread PROMEDIOS rows to verify the explicit CODRAMO/RAMOEQUIV bridge.
context=read('/Users/alexi/.local/share/ipss/cierre_14_jornadas_15_20261023_133759/JORNADAS_15_CONTEXTO_COMPLETO.json')
focus={(r['caso'],str(r['anio']),str(r['periodo'])) for r in targets}
pr=[r for r in context if (r.get('caso'),r.get('ANO'),r.get('PERIODO')) in focus and Path(r['fuente']).name in {'PROMEDIOSDEALUMNOS_2071.xlsx','PROMEDIOSDEALUMNOS_3233.xlsx'}]
g=collections.defaultdict(list)
for r in pr:g[(r['fuente'],r['hoja'])].append(r)
for (path,sheet),rr in g.items():
 h=sha256(path);assert all(r['sha256']==h for r in rr);H[path]=h
 w=openpyxl.load_workbook(path,read_only=True,data_only=True);it=iter(w[sheet].values);hd=[val(x).upper() for x in next(it)];want={r['fila']:r for r in rr};done=0
 for n,row in enumerate(it,2):
  if n>max(want):break
  if n not in want:continue
  actual=dict(zip(hd,row));old=want[n]
  for k in ['CODCLI','RUT','CODCARR','PLAN_DE_ESTUDIO','ANO','PERIODO','CODRAMO','RAMOEQUIV','CODSECC','JORNADA']:
   if k in old:assert val(actual[k])==val(old[k]),(Path(path).name,n,k)
  done+=1
 assert done==len(want);w.close()
# Exact RUT + recorded course or RAMOEQUIV + section + period; no name similarity.
mainname='INFORME RENDIMIENTO ACADEMICO 27012025.xlsx'
rows=[r for r in a['actividad_foco'] if Path(r['fuente']).name==mainname and (r['caso'],r['ANO'],r['PERIODO']) in focus]
bridge=[]
for r in rows:
 matches=[q for q in pr if q['caso']==r['caso'] and q['ANO']==r['ANO'] and q['PERIODO']==r['PERIODO'] and q.get('CODSECC')==r['SECCIONRAMO'] and r['CODIGORAMO'] in [q.get('CODRAMO'),q.get('RAMOEQUIV')]]
 bridge.append({'rendimiento':r,'coincidencias_promedios':matches,'planes':sorted({q['PLAN_DE_ESTUDIO'] for q in matches})})
assert all(x['planes'] in [[],['IINF20241']] for x in bridge)
# The one additional D-section row for INF35-04 is retained, not silently discarded.
unmatched=[x for x in bridge if not x['coincidencias_promedios']]
assert len(unmatched)==1 and unmatched[0]['rendimiento']['caso']=='INF35-04' and unmatched[0]['rendimiento']['PERIODO']=='3' and unmatched[0]['rendimiento']['SECCIONRAMO']=='1'
mu={c:{str(y):s.codigos_mu(persona=r['persona'],anio=y)['codigos'] for y in [2024,2025,2026]} for c,r in bycase.items()}
assert mu['INF35-03']['2025']==['I162S2C1J1V1'] and mu['INF35-03']['2026']==['I162S2C1J1V2']
assert mu['INF35-04']['2024']==['I162S2C1J1V2'] and mu['INF35-04']['2025']==['I162S2C1J2V4']
assert mu['INF35-10']['2025']==['I162S2C1J2V4'] and mu['INF35-10']['2026']==['I162S2C1J4V2']
for old in a['observaciones_antes']:assert json.loads(s.db.execute('select payload from observaciones where id=?',(old['observacion_id'],)).fetchone()[0])==old
s.close()
stats=read(O/'SECCIONES_PARES.json');stats=[x for x in stats if Path(x['fuente']).name==mainname]
# Preserve peers as separate people within each group, never sum across subjects.
class_summary=[]
for t in targets:
 q=[r for r in rows if (r['caso'],r['ANO'],r['PERIODO'])==(t['caso'],str(t['anio']),str(t['periodo']))]
 classes=sorted({(r['CODIGORAMO'],r['SECCIONRAMO'],r['JORNADA'],r['FECHAINICIO'],r['FECHAFIN']) for r in q})
 class_summary.append({'caso':t['caso'],'anio':t['anio'],'periodo':int(t['periodo']),'evaluaciones':len(q),'asignatura_seccion_fechas':len(classes),'clases':[{'asignatura':k[0],'seccion':k[1],'jornada_reporte':k[2],'inicio':k[3],'fin':k[4]} for k in classes]})
assert [r['asignatura_seccion_fechas'] for r in class_summary]==[4,2,3,5,4]
result=[
 {'caso':'INF35-03','anio':2024,'periodo':2,'codigo_T1':'I162S2C1J2V4','codigo_propuesto':'Pendiente','estado':'E_JORNADA_MIXTA_Y_VERSION_NO_ATRIBUIDA','evidencia':'Cuatro asignaturas: secciones 20,2,1,1. AT101PCOM/20 tiene tres pares V/J2V4; otras secciones incluyen D y O. No se ordena el cambio por fecha: todas comparten inicio/fin.','pendiente':'Situar jornada administrativa en T2 y resolver J1V1/J1V2; no elegir versión por compañeros.'},
 {'caso':'INF35-03','anio':2024,'periodo':3,'codigo_T1':'I162S2C1J2V4','codigo_propuesto':'Pendiente','estado':'C_JORNADA_D_RESPALDADA_E_VERSION','evidencia':'Dos asignaturas sección 1; pares D (3 y 13), ambos grupos con código MU2024 J1V2. La persona tiene J1V1 en MU2025 y J1V2 en MU2026.','pendiente':'La actividad apoya D en T3, pero el código de compañeros no resuelve la versión individual V1/V2.'},
 {'caso':'INF35-04','anio':2024,'periodo':2,'codigo_T1':'I162S2C1J1V2','codigo_propuesto':'Pendiente','estado':'E_CONTINUIDAD_D_NO_CONFIRMADA','evidencia':'Tres asignaturas en secciones 51,1,1; pares D/O. Propuesta diurna el 08-octubre y cambio reportado en noviembre.','pendiente':'J1V2 es candidato por continuidad T1, pero propuesta diurna no acredita matrícula efectiva ni descarta cambios previos; no se promueve.'},
 {'caso':'INF35-04','anio':2024,'periodo':3,'codigo_T1':'I162S2C1J1V2','codigo_propuesto':'I162S2C1J2V4','estado':'C_PROPUESTA_INTERNA_PARA_APROBACION','evidencia':'Contacto 13-nov-2024 informa cambio de jornada; cuatro asignaturas sección 20 en respaldo T3 del 19-nov, corroboradas por plan/CODCLI. Pares V/J2V4; MU2025 personal J2V4. Se conserva una evaluación adicional en sección 1.','pendiente':'Aprobar correspondencia interna al destino observado de T3; atribución documental SIES y día exacto pendientes; no afirmar que todo T3 se cursó en V.'},
 {'caso':'INF35-10','anio':2025,'periodo':2,'codigo_T1':'I162S2C1J2V4','codigo_propuesto':'I162S2C1J2V4','estado':'C_PROPUESTA_INTERNA_PARA_APROBACION','evidencia':'Cuatro asignaturas sección 20 (30-jun a 21-sep-2025), reporte y PROMEDIOS3233 V; pares de todas las secciones V. Reutiliza código personal T1 J2V4; foto T3 posterior O.','pendiente':'Aprobar continuidad interna T2 respaldada por actividad; no se acredita día exacto del cambio ni que toda matrícula al cierre fuera V. Atribución documental pendiente.'}
]
for r in result:r['clasificacion']='B hechos observados; C contraste/propuesta; E límites; no decisión D nueva'
# Catalog context only: no inference from order of version or year.
master=read(R/'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json')
of=[x for x in master['oferta_anual'] if x['anio'] in [2024,2025] and x['codigo_unico'].startswith('I162S2C1J')]
dump(O/'OFERTA_CONTEXTO.json',of)
dump(P/'EVIDENCIA_REVISION.json',{'contactos_relevantes':contacts,'promedios_releidos':pr,'puente_actividad_plan':bridge,'anclas_mu':mu,'objetivos':targets})
dump(O/'RESULTADOS.json',{'observaciones':5,'personas':3,'propuestas_internas_no_aplicadas':2,'sin_propuesta_concluyente':3,'cierres_aplicados':0,'tabla':result})
dump(O/'CLASES_POR_PERIODO.json',class_summary)
with (O/'TABLA_CINCO.csv').open('w',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=list(result[0]),delimiter=';');wr.writeheader();wr.writerows(result)
# Public citations retain source/row/hash without identities or private narratives.
refs=[]
for i,r in enumerate(rows):refs.append({k:r[k] for k in ['caso','fuente','hoja','fila','sha256','ANO','PERIODO','CODIGORAMO','SECCIONRAMO']})
for r in contacts:refs.append({k:r[k] for k in ['caso','fuente','hoja','fila','sha256','fecha_comunico']})
for r in pr:refs.append({k:r[k] for k in ['caso','fuente','hoja','fila','sha256','ANO','PERIODO']})
dump(O/'REFERENCIAS.json',refs)
# The three section snapshots are controls, not independent replications or extra persons.
report='''# Secciones y cambios de jornada: cinco observaciones

**Proceso:** seguimiento intertrimestral interno IPSS 162; T2/T3-2024 (INF35-03/04) y T2-2025 (INF35-10). Diccionario activo v5. **C:** revisión sin adjudicaciones ni modificación de bases, Excel o denominadores.

**Resultado C/E:** dos propuestas de correspondencia interna con evidencia adicional; tres observaciones sin versión concluyente. Ninguna propuesta está aplicada ni equivale a atribución documental SIES. No se requiere conocer el día exacto para proponer un contexto de destino; sí distinguir evidencia del período y datos retrospectivos.

| Caso | Período | Asignatura-sección (B) | Resultado (C/E) |
|---|---|---:|---|
| INF35-03 | T2-2024 | 4: secciones 20, 2, 1, 1 | Actividad en grupos distintos. Jornada administrativa y versión pendientes. |
| INF35-03 | T3-2024 | 2: sección 1 | Actividad coherente con D; versión V1/V2 pendiente. |
| INF35-04 | T2-2024 | 3: secciones 51, 1, 1 | J1V2 es candidato de continuidad T1, pero no se confirma administrativamente T2. |
| INF35-04 | T3-2024 | 5 combinaciones: 4 en sección 20 y 1 evaluación adicional en sección 1 | Propuesta interna de destino I162S2C1J2V4, sin borrar la fila adicional. |
| INF35-10 | T2-2025 | 4: sección 20 | Propuesta de continuidad interna I162S2C1J2V4. |

## Evidencia nueva — B y límites E

**INF35-04.** GESTIONSGE_1703.xlsx, Hoja1: fila 12436 (08-oct-2024) registra envío de propuesta de ramos diurna; fila 12427 (13-nov-2024) consigna que el estudiante informó un cambio de jornada y recibió prórroga para cuatro asignaturas. Esto acredita un relato fechado del cambio, no el acto administrativo ni su día. La propuesta diurna anterior no es matrícula confirmada. La fila 12428 (04-abr-2024) ya menciona clases presenciales y online: cursar un ramo en otra modalidad no demuestra por sí solo cambio de jornada administrativa.

El respaldo PRUEBA CUMPLIMIENTO INGRESO CALIFICACIONES T3_2024.xlsx, DATOS CRUDOS U+ 19-11-2024, filas 1971–1974, sitúa cuatro asignaturas del mismo CODCLI/plan en sección 20. Se contrasta con el informe de rendimiento: AS100PCOM, AS101PCOM, IF105IINF e IF106IINF. Excluidas las tres personas del foco, esas secciones tienen respectivamente 6, 6, 10 y 9 compañeros, todos con jornada V en el reporte y código MU2024 J2V4. No se suman esos conteos porque las personas se repiten entre asignaturas. MU2025 documenta J2V4 para la propia persona. La convergencia respalda **proponer** J2V4 para el destino de seguimiento T3, no para todo el trimestre desde su inicio. Se preserva una evaluación R, nota 1, de AS100PCOM/sección 1; no se inventa su cancelación ni se elimina.

**INF35-10.** El informe completo contiene siete evaluaciones de cuatro asignaturas T2-2025, sección 20, con inicio 30-jun y fin 21-sep-2025. Coinciden con cuatro registros de PROMEDIOS3233 por identidad, período, sección y CODRAMO/RAMOEQUIV explícito, plan IINF20241. Todas muestran V. Los grupos tienen 6, 4, 10 y 10 compañeros V, excluidas las tres personas del foco. Sus códigos SIES no son uniformes (hay V1 y V4, además de códigos anuales de otra jornada); por eso no se toma la versión de la mayoría. Se reutiliza el **código personal T1 J2V4** como propuesta de continuidad interna T2. La foto T3 y MU2026 muestran O/J4V2 posteriormente; la fecha exacta del cambio permanece pendiente. Las asignaturas figuran abiertas: no certifican por sí solas matrícula vigente al cierre de T2.

**INF35-03.** T2 tiene AT101PCOM/sección20 con tres pares V/J2V4 y otras asignaturas en secciones1/2 con pares D u O. Todas comparten el rango 01-jul a 28-sep-2024: no se puede ordenarlas como antes/después de un cambio. En T3, AS100PCOM/1 e IF106IINF/1 reúnen 3 y 13 pares D/J1V2; esto apoya la jornada D de su actividad. Pero MU2025 documenta J1V1 para la propia persona y MU2026 J1V2. No se reemplaza esa ambigüedad individual con el código mayoritario de sus compañeros. Ambos períodos siguen pendientes de versión.

**INF35-04 T2.** Las tres asignaturas de julio-septiembre aparecen en grupos D/O; la combinación de clases no fija por sí sola la jornada administrativa. T1 J1V2 y la propuesta diurna de octubre apoyan ese candidato, pero no bastan para afirmar que no existieron cambios intermedios. Se conserva pendiente, sin extender automáticamente la propuesta de T3 hacia atrás.

## Cómo se verificó — C

Se leyeron seis libros adicionales. El principal para este contraste es INFORME RENDIMIENTO ACADEMICO 27012025.xlsx porque su contenido cubre los cinco destinos, incluyendo T2-2025; el nombre no se usó como fecha de corte. Las variantes -1, -2 y 20261_FINAL2 contienen actividad histórica solapada y no se cuentan como confirmaciones independientes. Sus diferencias de cobertura constan en INVENTARIO.json. SEGUIMIENTO_ACADEMICO tiene una jornada distinta para la misma actividad T1-2025 de INF35-04 (V frente a D en otro reporte), por lo que JORNADA no se trata como historia inmutable por asignatura.

El cruce de rendimiento usa RUT exacto con DV, carrera IINF, año, período, asignatura y sección. Su enlace al expediente y plan se corrobora con CODCLI y CODRAMO/RAMOEQUIV de PROMEDIOS; no se unieron nombres similares de asignaturas. RUT_ALUMNO en GESTIONSGE contiene solo el cuerpo: se cotejó exactamente con el cuerpo de la identidad conocida, comprobando unicidad en el diccionario y carrera IINF; el DV ausente no se fabricó. Se conserva esa limitación de identificación en la evidencia privada.

Las 16+8+12+17+7 filas del foco en rendimiento son 60 evaluaciones, no 60 estudiantes. Representan 18 combinaciones asignatura-sección, de las que 17 coinciden con PROMEDIOS; la combinación restante es la fila adicional de INF35-04. Los grupos de comparación excluyen las tres identidades del foco y cuentan personas distintas dentro de cada grupo. Las anclas anuales concordantes de compañeros son corroboración, no verdad administrativa de cada trimestre. No se interpreta sección 1/20/51/99 como un catálogo universal de jornadas o versiones.

## Cierre de revisión

**C:** cero adjudicaciones. V5 conserva siete cierres anteriores, 24 reutilizables y 11 pendientes del foco original de 35. Si se aprueban las dos propuestas de este informe, serían 26 reutilizables y 9 pendientes (tres de jornada, seis homologaciones); es escenario, no estado aplicado. Atribución documental y aceptación SIES siguen separadas. Fuentes, bases, denominadores, libro y motor anual intactos. Sin commit ni push.

Fuentes, hojas, filas y hashes: REFERENCIAS.json, CONFIG.json y MANIFEST.json. Grupos detallados: SECCIONES_PARES.json. El relato individual mínimo, el puente y llaves quedan solo en la carpeta privada indicada por el manifiesto.
'''
assert len(rows)==60 and len(bridge)-len(unmatched)==59
(O/'INFORME.md').write_text(report)
(O/'CHECKPOINT.md').write_text('C/E: revisión finalizada; no aplicada. Proponer INF35-04 T3-2024 I162S2C1J2V4 (cambio reportado en noviembre + secciones/plan + MU2025) e INF35-10 T2-2025 I162S2C1J2V4 (T1 + cuatro asignaturas V). Pendientes: INF35-03 T2/T3-2024 versión V1/V2; INF35-04 T2-2024 jornada administrativa. Conservar v5 y esperar aprobación acotada; no extrapolar sección ni código de compañeros.\n')
for f,h in H.items():assert sha256(f)==h,f
G={'rama':subprocess.check_output(['git','-C',str(R),'branch','--show-current'],text=True).strip(),'HEAD':subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()}
assert G=={'rama':'feature/ire-2026','HEAD':'80ca13a5a249a1a2bd53a699f5f73689b1f53040'}
qa={'resultado':'OK_TECNICO_CON_LIMITES_E','observaciones':5,'personas':3,'evaluaciones_foco':60,'asignatura_seccion':18,'evaluaciones_con_puente_promedios':59,'fila_adicional_preservada':1,'filas_promedios_releidas':len(pr),'contactos_relevantes_verificados':3,'foco_excluido_de_pares':True,'conteo_por_persona_dentro_de_grupo':True,'propuestas':2,'pendientes_sin_propuesta_concluyente':3,'adjudicaciones':0,'diccionario_fuentes_denominadores_preservados':True,'git_antes_despues':G,'commit_push':False,'limites':['JORNADA de reporte no es una historia administrativa por período.','Sección no asigna versión.','Gestión de contacto conserva RUT sin DV y relato del estudiante.','No se acreditan cierres exactos ni tasas nuevas.']}
dump(O/'QA.json',qa)
secret={r['persona'] for r in targets}|{r['CODCLI'] for r in targets}|{r['persona'].split('-')[0] for r in targets}
for p in O.iterdir():assert not any(x in p.read_text() for x in secret),p.name
manifest={'fecha_hora':datetime.datetime.now(ZoneInfo('America/Santiago')).isoformat(),'proceso':'Seguimiento intertrimestral IPSS 162','clasificacion':'B fuentes; C contraste/propuestas; E atribución pendiente; sin nueva D','fuentes_sha256':H,'salidas_sha256':{p.name:sha256(p) for p in O.iterdir()},'privado':str(P),'privados_hashes':{p.name:sha256(p) for p in P.iterdir()},'codigo_sha256':{str(p.relative_to(R)):sha256(p) for p in [Path(__file__),R/'scripts/revisar_secciones_cinco_jornadas_20261023.py',R/'docs/ESPECIFICACION_SECCIONES_CINCO_JORNADAS_20261023.md']},'QA':qa}
dump(O/'MANIFEST.json',manifest)
print(json.dumps({'salida':str(O),'manifest_sha256':sha256(O/'MANIFEST.json'),'QA':qa},ensure_ascii=False))
