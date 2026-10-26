from pathlib import Path
import json,sys,collections,os,datetime,subprocess,csv
import openpyxl
R=Path('/Users/alexi/Documents/GitHub/avance_curricular');sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import sha256,rut_normalizado
O=R/'outputs/revision_35_informatica_20261023_130829';P=Path.home()/'.local/share/ipss'/O.name
read=lambda p:json.loads(p.read_text())
def dump(p,v):
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2,default=str))
 if p.is_relative_to(P):os.chmod(p,0o600)
rows=read(P/'FILAS_RELEIDAS.json');cs=read(P/'CASOS.json');ts=read(P/'SELECCION_35.json');hs=read(O/'FUENTES_HASHES.json');inv=read(O/'INVENTARIO.json')
# Recuperar la copia idéntica del respaldo que ya no está en Descargas.
old='/Users/alexi/Downloads/DATOSDEALUMNOS_12159.xlsx'
p=Path('/Users/alexi/Desktop/Caracterizacion_2026-10-22_2027_P1_084218/01_ENTRADAS/DATOSDEALUMNOS_12159.xlsx');h=sha256(p);assert h=='a0638483420324bcb2bba8bcbea426ca0a2be6162d1c8879569b507f409bdfc9';hs[str(p)]=h
rows=[r for r in rows if r['fuente']!=str(p)];inv=[r for r in inv if r['fuente']!=str(p)]
w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=iter(w['Hoja1'].values);head=list(next(it));owners={c['persona']:c for c in cs};found=0
for rn,rr in enumerate(it,2):
 d=dict(zip(head,rr))
 try:person=rut_normalizado(d.get('RUT'))
 except (ValueError,TypeError):continue
 if person not in owners:continue
 keep=['CODCLI','RUT','CODCARPR','ANOINGRESO','PERIODOINGRESO','ANOMATRICULA','PERIODOMATRICULA','FECHAMATRICULA','FECHAFIRMA','JORNADA','SEDE','ESTADOACADEMICO','SITUACION']
 z={k:str(d.get(k,'')) for k in keep};z.update(persona=person,caso=owners[person]['caso'],fuente=str(p),hoja='Hoja1',fila=rn,sha256=h);rows.append(z);found+=1
w.close();assert found==14
for x in inv:
 if x['fuente']==old:x.update(estado='RESUELTO_COPIA_IDENTICA',copia=str(p),sha256=h)
inv.append({'fuente':str(p),'hoja':'Hoja1','sha256':h,'filas_foco':found,'origen':'copia de idéntico contenido; no inferir fecha de corte del nombre'})
# Releer el puente explícito: J RUT, BU N_DOC, BV DV. Verificar unicidad global.
bp=Path(next(k for k in hs if Path(k).name=='IPSS_Procesamiento.xlsx'));assert sha256(bp)==hs[str(bp)]
w=openpyxl.load_workbook(bp,read_only=True,data_only=True);bridge=collections.defaultdict(set);br=collections.defaultdict(list)
for rn,rr in enumerate(w['2025_carga'].values,1):
 if rn==1 or len(rr)<74 or rr[72] is None:continue
 try:person=rut_normalizado(rr[9])
 except (ValueError,TypeError):continue
 doc=str(rr[72]);bridge[doc].add(person)
 if person in owners:br[person].append({'fuente':str(bp),'hoja':'2025_carga','fila':rn,'sha256':hs[str(bp)],'RUT':str(rr[9]),'N_DOC':doc,'DV':str(rr[73]),'columnas':'J, BU, BV'})
w.close()
res=[];case_summary=[]
def code(r):return 'I162S%sC%sJ%sV%s'%tuple(r[k] for k in ['COD_SED','COD_CAR','JOR','VERSION'])
def ref(r):return {k:r[k] for k in ['fuente','hoja','fila','sha256']}
for c in cs:
 person,cc=c['persona'],c['CODCLI'];tt=[t for t in ts if t['persona']==person and t['codcli']==cc];year=tt[0]['anio'];rr=[r for r in rows if r['persona']==person]
 mu=[r for r in rr if r.get('ANIO_INFORMADO')==str(year)];codes={code(r) for r in mu};assert len(codes)==1;orig=next(iter(codes))
 pr=[r for r in rr if r.get('CODCLI')==cc and r.get('ANO')==str(year) and r['fuente'].endswith('PROMEDIOSDEALUMNOS_12166.xlsx')]
 plans={r.get('PLAN_DE_ESTUDIO') for r in pr};assert plans=={tt[0]['plan']}
 courses=collections.defaultdict(set)
 for r in rr:
  if r.get('CODCLI')==cc and r.get('ANO')==str(year) and r.get('PLAN_DE_ESTUDIO')==tt[0]['plan']:courses[Path(r['fuente']).name].add(r.get('JORNADA',''))
 if c['caso'] in ['INF35-08','INF35-09']:
  assert {r['TIPO_DOC'] for r in mu}=={'P'}
  assert all(bridge[str(t['documento_original'])]=={person} for t in tt)
  assert all(js=={'D'} for js in courses.values())
  assert orig=='I162S2C1J1V2'
 for t in tt:
  per=t['periodo_nativo'];acts=[r for r in pr if r.get('PERIODO')==str(per)];assert acts
  if t['plan']=='TPAS20241':
   assert all(r.get('ESTADO')=='I' and r.get('CONVALIDADO')=='S' for r in acts)
   state='E_HOMOLOGACIONES_OTRA_CARRERA';candidate='';reason='La cohorte de origen es Informática; la observación es TPAS20241. Solo se observan homologaciones I/S del año 2024 en ese contexto. No trasladar el código de Informática ni retrotraer automáticamente el código posterior de Programación.'
  elif c['caso'] in ['INF35-08','INF35-09']:
   state='BC_RECUPERABLE_PUENTE_EXPLICITO';candidate=orig;reason='Identidad enlazada de forma unívoca por J/BU/BV; MU2025 documenta código único. El mismo CODCLI y plan tienen jornada D y actividad aprobada en los tres períodos. Reutilización anual para seguimiento interno; no acredita envío SIES T2/T3.'
  elif str(per)=='1':
   state='BC_ANCLA_T1_RECUPERABLE';candidate=orig;reason='El propio T1 tiene un código literal único en MU del año y un único expediente IINF observado. Se conserva como ancla histórica; el contexto de jornada actual discrepa. No equivale a validar la jornada actual ni a extender este código a T2/T3.'
  else:
   state='E_CAMBIO_JORNADA_SIN_PERIODO';candidate='';reason='Plan IINF20241 observado, pero diferentes respaldos atribuyen jornadas distintas al mismo CODCLI, incluso a asignaturas de los mismos períodos. Falta intervalo efectivo del cambio para adjudicar el código de destino. El código de cohorte T1 sigue confirmado.'
  res.append({'caso':c['caso'],'persona':person,'CODCLI':cc,'plan':t['plan'],'anio':year,'periodo_nativo':per,'estado_antes':'E Pendiente','resultado_revision':state,'codigo_origen_documentado':orig,'codigo_recuperable':candidate,'codigo_adoptado':'','razon':reason,'fuentes_mu':[ref(r) for r in mu],'fuentes_actividad':[ref(r) for r in acts],'puente_identidad':br.get(person,[]) if c['caso'] in ['INF35-08','INF35-09'] else [],'jornadas_por_respaldo':{k:sorted(v) for k,v in courses.items()},'original_consulta':t})
 case_summary.append({'caso':c['caso'],'anio':year,'plan':t['plan'],'observaciones':len(tt),'codigo_origen_documentado':orig,'jornadas_por_respaldo':{k:sorted(v) for k,v in courses.items()},'mu_por_anio':{a:sorted({code(r) for r in rr if r.get('ANIO_INFORMADO')==a}) for a in sorted({r['ANIO_INFORMADO'] for r in rr if 'ANIO_INFORMADO' in r})}})
targetkeys={(t['codcli'],str(t['anio'])) for t in ts}
regimens={r['REGIMEN'] for r in rows if (r.get('CODCLI'),r.get('ANO')) in targetkeys and 'REGIMEN' in r}
assert regimens=={'TRIMESTRAL'}
counts=collections.Counter(x['resultado_revision'] for x in res);assert counts=={'BC_ANCLA_T1_RECUPERABLE':8,'BC_RECUPERABLE_PUENTE_EXPLICITO':6,'E_CAMBIO_JORNADA_SIN_PERIODO':15,'E_HOMOLOGACIONES_OTRA_CARRERA':6};assert len(res)==35
# Todo es un diagnóstico: los 35 registros siguen intactos en la edición activa.
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento
s=DiccionarioSiesSeguimiento()
for t in ts:
 q=s.consultar(persona=t['persona'],codcli=t['codcli'],plan=t['plan'],anio=t['anio'],periodo=t['periodo_nativo'],carrera=t['carrera_umas'],sede=t['evidencia']['sede_dimension'],jornada=t['evidencia']['jornada_sies']);assert q['estado']=='EXCEPCION'
s.close()
for f,h in hs.items():assert sha256(Path(f))==h
book=Path('/Users/alexi/Desktop/RETENCION_IPSS_DICCIONARIO_APLICADO_20261023_V12.xlsx');assert sha256(book)=='e7f797b5de9a6e9748cd250e9931947dbc8469f65d01f5a488c765e0009676fe'
head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip();branch=subprocess.check_output(['git','-C',str(R),'branch','--show-current'],text=True).strip();assert head=='80ca13a5a249a1a2bd53a699f5f73689b1f53040';assert branch=='feature/ire-2026'
dump(P/'FILAS_RELEIDAS.json',rows);dump(P/'REVISION_OBSERVACIONES.json',res);dump(P/'TRAYECTORIAS_CASOS.json',case_summary);dump(O/'INVENTARIO.json',inv);dump(O/'FUENTES_HASHES.json',hs)
summary={'clasificacion':'B/C; causas no acreditadas E','observaciones':35,'personas':12,'expedientes_objetivo':12,'recuperables_para_revision':14,'anclas_T1_con_discrepancia_contexto':8,'puente_pasaporte_RUT':6,'pendientes_destino':21,'cambio_jornada_sin_periodo':15,'homologaciones_otra_carrera':6,'cierres_aplicados':0,'personas_con_todas_observaciones_recuperables':2,'personas_parcialmente_recuperables':8,'personas_sin_observaciones_destino_recuperables':2,'estados':dict(counts)}
dump(O/'RESULTADOS_AGREGADOS.json',summary)
dump(O/'CONTROL.json',{'seleccion':35,'personas':12,'expedientes':12,'filas_recuperadas':len(rows),'rechazos_identidad':0,'fuentes_xlsx_leidas':len({r['sha256'] for r in rows})+1,'sin_adopcion':True,'copia_12159_verificada':True})
agg=collections.Counter((x['anio'],x['resultado_revision'],x['codigo_recuperable'] or 'Pendiente') for x in res)
with (O/'RESUMEN_CODIGOS.csv').open('w',newline='') as f:
 cw=csv.writer(f,delimiter=';');cw.writerow(['Año','Resultado revisión','Código recuperable','Observaciones','Clasificación'])
 for (y,st,co),n in sorted(agg.items()):cw.writerow([y,st,co,n,'E' if st.startswith('E_') else 'B/C'])
qa={'resultado':'OK_CON_ADVERTENCIAS','seleccion_35_exacta':True,'periodos_nativos_regimen_trimestral_verificado':True,'personas_12':True,'balance_14_mas_21':True,'identidad_codcli_sin_conflictos':True,'puente_P_univoco_dos_personas':True,'misma_jornada_D_tres_periodos_dos_personas':True,'fuentes_reverificadas':len(hs),'fuente_ausente_recuperada_copia_identica':str(p),'excel_V12_hash_conservado':sha256(book),'diccionario_35_consultas_sigue_pendiente':True,'denominadores_no_recalculados_ni_modificados':True,'originales_no_modificados':True,'advertencias':['14 resultados recuperables propuestos; no se aplicó una nueva edición del diccionario.','8 anclas T1 requieren conservar contexto histórico y registrar discrepancia de jornada actual.','La reutilización anual en T2/T3 no prueba envío ni aceptación SIES de esos períodos.','21 contextos de destino continúan sin asignación.','No se revisaron tasas ni vigencia; este trabajo solo revisa códigos y contexto.'],'rama':branch,'HEAD_antes':head,'HEAD_despues':head,'commit_push':False}
dump(O/'QA.json',qa)
report='''# Revisión de los 35 pendientes de Informática

Proceso: retención intertrimestral IPSS 162. Contextos académicos 2024–2026; revisión 23-10-2026. Diccionario común v1 y aplicación V12, sin modificación.

**B/C. Resultado: 14 observaciones recuperables para revisión y 21 pendientes de código de destino. Son 35 observaciones de 12 personas y 12 expedientes objetivo, no 35 estudiantes. No se aplicaron cierres.**

| Resultado | Observaciones | Personas del grupo | Respaldo |
|---|---:|---:|---|
| Ancla T1 documentada, contexto actual de jornada discrepante | 8 | 8 | B/C |
| Código recuperable por puente explícito pasaporte–RUT | 6 | 2 | B/C |
| T2/T3 con cambio de jornada sin período efectivo acreditado | 15 | 8 | E para adjudicación de destino; B para discrepancia observada |
| Homologaciones TPAS20241 de personas cuya cohorte origen es Informática | 6 | 2 | B para filas; E para atribución histórica al destino |

**C.** Las personas de las filas 1 y 3 son las mismas: no se suman. Dos personas tienen todas sus observaciones recuperables (6); ocho solo el ancla T1 (8 recuperables y 15 pendientes); dos mantienen sus seis contextos TPAS pendientes. Total: 2+8+2=12 personas; 8+6+15+6=35 observaciones.

## Lo que sí se puede reutilizar

**B/C.** Dos personas de MU2025 están informadas con tipo documental P. La relación explícita de `IPSS_Procesamiento.xlsx`, hoja `2025_carga`, columnas J (RUT), BU (N_DOC) y BV (DV), enlaza inequívocamente su documento con el RUT observado en UMAS. Se releyó la tabla y se comprobó unicidad global del enlace. MU2025 registra **I162S2C1J1V2**. En PROMEDIOS, el mismo CODCLI mantiene IINF20241, jornada D y asignaturas aprobadas en períodos 1, 2 y 3. Es posible reutilizar ese código anual en las seis observaciones de seguimiento interno. No es evidencia de un envío SIES trimestral. El adaptador documental del diccionario excluía estos P; el código ya existía en la fuente.

**B/C.** Otras ocho observaciones son del propio período 1. El código literal de MU existe, y se encontró un único expediente IINF para cada persona en los respaldos releídos. Se recuperan como **anclas T1**, registrando en paralelo la discrepancia de jornada del contexto actual. No se valida por ello el código de destino T2/T3. Sus códigos se detallan en `RESUMEN_CODIGOS.csv`.

## Qué impide completar las demás

**B/E.** En ocho personas, los respaldos de PROMEDIOS muestran distintas jornadas para el mismo CODCLI y el mismo plan IINF20241, incluso al repetir asignaturas del mismo año/período. No se encontró un cambio de nombre de plan que explique por sí solo el cambio de código. Está comprobada la variación entre respaldos; no está acreditada la fecha o el período efectivo de cada cambio. Quince observaciones T2/T3 quedan pendientes de adjudicación de destino. No se exige el día exacto: bastaría un respaldo que delimite de forma inequívoca qué jornada/versión regía en cada período. Los datos releídos no lo delimitan.

**B.** Ejemplos de secuencias literales MU: J1V2→J1V2→J4V2 (2024, 2025, 2026); J2V4→J1V1→J1V2; J1V2→J2V4 (2024, 2025). Todas dentro de I162S2C1. Estas secuencias no autorizan transportar el código 2026 hacia 2024 ni asignar a todo IINF20241 una misma versión.

**B/E.** Seis de los 35 contextos pertenecen a TPAS20241, aunque las personas ingresaron al seguimiento desde Informática. En PROMEDIOS_12166 sus diez filas académicas 2024 son I/CONVALIDADO=S, distribuidas en tres períodos por persona. MU2024 conserva I162S2C1J4V2; el código de Programación I162S2C57J4V1 aparece después: en 2026 para una persona, en 2025 para la otra. No acreditan matrícula TPAS en cada período 2024 ni permiten asignar retrospectivamente el código posterior. No son seis ambigüedades entre V2/V3 de Informática.

## Fuentes y trazabilidad

**B/C.** Se releyeron MU2022–2026, el puente IPSS_Procesamiento, PROMEDIOS_2071, _3233, _7804 y _12166; DATOSDEALUMNOS_11248, _11998 y _12159; DATOSDEALUMNOS ORIGEN DE LOS DATOS2025; y tres respaldos de calificaciones 2024. Los reportes de calificaciones incorporan fechas internas de reporte 2024 y de inicio/fin de cursos. No contienen por sí mismos código SIES completo ni fecha de migración de jornada.

**B.** DATOSDEALUMNOS_12159 ya no estaba en Descargas. Se recuperó su copia del Escritorio, con el mismo SHA-256 gobernado a0638483420324bcb2bba8bcbea426ca0a2be6162d1c8879569b507f409bdfc9. No quedó un bloqueo de lectura sin resolver. No se usa la fecha de carpeta como fecha efectiva de matrícula.

**C.** `INVENTARIO.json` identifica archivo, hoja, encabezados, filas y hash; `FUENTES_HASHES.json` fija las fuentes. El detalle privado registra cada observación, consulta original, fuente/hoja/fila/hash, código de origen, resultado recuperable y motivo pendiente. Ningún identificador individual se incluye en este informe o en el CSV agregado.

## QA y reanudación

**C. QA OK_CON_ADVERTENCIAS.** Selección 35/35, doce identidades y doce expedientes objetivo; sin conflictos de identidad detectados; balance 14+21; puente de dos personas unívoco; copia faltante recuperada por hash. Fuentes verificadas de nuevo al cierre; Excel V12 conserva su hash. Las 35 consultas de la edición activa siguen pendientes: este informe no simula que los cierres ya se aplicaron.

**D/C.** Se mantienen bases, denominadores, fórmulas, tasas, Excel y edición activa del diccionario. Sin commit ni push. Rama feature/ire-2026; HEAD 80ca13a5a249a1a2bd53a699f5f73689b1f53040 antes/después.

**E. Siguiente paso:** revisar/adoptar por alcance los 14 resultados recuperables en una nueva edición: seis mediante el adaptador documental y ocho como anclas T1 con discrepancia histórica explícita. Conservar pendientes los quince destinos de jornada y las seis homologaciones TPAS. No extrapolar a los otros años ni al universo histórico. Para las tasas, el código de cohorte T1 ya documentado se conserva; los códigos de destino pendientes no convierten a nadie en desertor ni alteran denominadores.
'''
(O/'INFORME_REVISION.md').write_text(report)
(O/'CHECKPOINT.md').write_text('B/C: revisión completada de 35 observaciones, 12 personas. 14 recuperables (8 anclas T1 y 6 por puente P–RUT); 21 destinos pendientes (15 jornada, 6 homologaciones TPAS).\nD/C: sin adopción de nueva edición, sin cambios a bases/Excel/denominadores, sin commit/push.\nE: siguiente paso es decidir la incorporación acotada de los 14; conservar las 21 excepciones con sus motivos. Detalle y hashes en MANIFEST.json e INFORME_REVISION.md.\n')
files=[O/'CONTROL.json',O/'CHECKPOINT.md',O/'RESULTADOS_AGREGADOS.json',O/'RESUMEN_CODIGOS.csv',O/'QA.json',O/'INFORME_REVISION.md',O/'INVENTARIO.json',O/'FUENTES_HASHES.json']
manifest={'fecha':datetime.datetime.now().astimezone().isoformat(),'tipo':'auditoria_propuesta_no_aplicada','proceso':'retencion_intertrimestral','alcance':'35 observaciones 12 personas Informática origen; 29 IINF y 6 TPAS destino','fuentes':hs,'salidas':{str(f):sha256(f) for f in files},'privado':str(P),'privado_hashes':{f.name:sha256(f) for f in P.glob('*.json')},'scripts':['scripts/revisar_35_informatica_20261023.py','scripts/finalizar_revision_35_informatica_20261023.py'],'codigo_hashes':{str(f.relative_to(R)):sha256(f) for f in [R/'scripts/revisar_35_informatica_20261023.py',R/'scripts/finalizar_revision_35_informatica_20261023.py',R/'docs/ESPECIFICACION_REVISION_35_INFORMATICA_20261023.md']},'especificacion':'docs/ESPECIFICACION_REVISION_35_INFORMATICA_20261023.md','resultado':summary,'git':{'rama':branch,'HEAD_antes':head,'HEAD_despues':head,'commit':False,'push':False},'pendiente':'Adopción de resultados revisados; 21 contextos de destino sin resolver; no alterar denominadores.'}
dump(O/'MANIFEST.json',manifest)
print(json.dumps(summary,ensure_ascii=False));print('QA',qa['resultado']);print(O/'INFORME_REVISION.md')
