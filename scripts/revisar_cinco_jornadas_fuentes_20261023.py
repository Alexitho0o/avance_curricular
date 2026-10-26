"""Amplía los cinco pendientes con respaldos 2024 inventariados; no adjudica."""
from pathlib import Path
import sys,json,datetime,collections,subprocess
from zoneinfo import ZoneInfo
import openpyxl
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import sha256,rut_normalizado
now=datetime.datetime.now(ZoneInfo('America/Santiago'));O=R/'outputs'/('revision_cinco_jornadas_'+now.strftime('%Y%m%d_%H%M%S'));P=Path.home()/'.local/share/ipss'/O.name
assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
O.mkdir();P.mkdir(mode=0o700);H={}
def read(p):
 p=Path(p);H[str(p)]=sha256(p);return json.loads(p.read_text())
def dump(p,x):
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
 if p.is_relative_to(P):p.chmod(0o600)
def val(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
A=R/'data/diccionario_sies_seguimiento/activo.json';active=read(A);desc=read(R/active['descriptor']);assert desc['edicion']=='v5_20261023_siete_jornadas';H[desc['base_privada']['ruta']]=desc['base_privada']['sha256']
targets=read(Path(desc['base_privada']['ruta']).parent/'CINCO_PENDIENTES.json');assert len(targets)==5
owners={r['CODCLI']:r['persona'] for r in targets};labels={r['CODCLI']:r['caso'] for r in targets}
person_labels={r['persona']:r['caso'] for r in targets}
inventory=read(R/'outputs/retencion_intermedia_t2_t3/20261021_093412_git_onedrive_mu2025/INVENTARIO_ONEDRIVE.json')
paths=[Path(x['ruta']) for x in inventory['archivos'] if 'RESPALDO SIES ENVIADO POR CARLOS' in x['ruta'] and '/2025/' not in x['ruta'] and 'DATOS DE ALUMNOS' in Path(x['ruta']).name.upper()]
assert len(paths)==6
found=[];inv=[]
for p in paths:
 h=sha256(p);H[str(p)]=h;w=openpyxl.load_workbook(p,read_only=True,data_only=True);items=[]
 for ws in w:
  it=iter(ws.values);headers=None
  for hn,row in enumerate(it,1):
   hh=[val(x).upper() for x in row]
   if 'RUT' in hh and 'CODCARPR' in hh and 'JORNADA' in hh:
    counts=collections.Counter();headers=[]
    for name in hh:
     counts[name]+=1;headers.append(name if counts[name]==1 else name+'__'+str(counts[name]))
    break
   if hn>=8:break
  if headers is None:items.append({'hoja':ws.title,'estado':'SIN_ESQUEMA_RUT_CODCARPR_JORNADA_EN_8_FILAS'});continue
  nmatch=0
  for n,row in enumerate(it,hn+1):
   d=dict(zip(headers,row));cc=val(d.get('CODCLI'))
   raw=val(d.get('RUT'))
   if '-' not in raw and d.get('DIG') is not None:raw+='-'+val(d['DIG'])
   if '-' not in raw and d.get('DV') is not None:raw+='-'+val(d['DV'])
   try:person=rut_normalizado(raw)
   except ValueError:continue
   if person not in person_labels:continue
   keep=['CODCLI','RUT','DIG','DV','CODCARPR','CODCARR','CODIGOCARRERA','JORNADA','SEDE','PLAN_DE_ESTUDIO','ANOINGRESO','PERIODOINGRESO','ANOMATRICULA','PERIODOMATRICULA','FECHAMATRICULA','FECHAFIRMA','SITUACION','ESTADOACADEMICO','COD CARRERA SIES','JORNADA__2','VERSION','COD_IES','COD_SED','COD_CAR','JOR','CODIGO UNICO','CODIGO UNICO__2','N_DOC']
   rr={k:val(d[k]) for k in keep if k in d};rr.update(caso=person_labels[person],fuente=str(p),hoja=ws.title,fila=n,sha256=h,metodo='RUT exacto con DV; CODCLI no presente en este esquema; carrera y jornada conservadas sin adjudicar');found.append(rr);nmatch+=1
  items.append({'hoja':ws.title,'encabezado':hn,'filas_foco':nmatch})
 w.close();inv.append({'fuente':str(p),'sha256':h,'hojas':items,'fecha_nombre_no_corte_acreditado':p.name});print(p.name,items,flush=True)
prior=read(R/'outputs/cierre_14_jornadas_15_20261023_133759/MANIFEST.json');cp=Path(prior['privado'])/'JORNADAS_15_CONTEXTO_COMPLETO.json';assert sha256(cp)==prior['privados_hashes'][cp.name];ctx=read(cp)
ctx=[r for r in ctx if r.get('caso') in labels.values()]
# Fechas de actividad explícitas: son fechas de asignatura, no de cambios personales.
activity=[r for r in ctx if r.get('FECHAINICIO') and r.get('FECHAFIN')]
group=collections.Counter((r['caso'],r.get('ANO'),r.get('PERIODO'),r.get('FECHAINICIO'),r.get('FECHAFIN'),r.get('FECHA MEDICION'),r.get('CODIGO_PLAN_ESTUDIO'),r.get('SECCION')) for r in activity)
summary=[{'caso':k[0],'anio':k[1],'periodo':k[2],'inicio_asignatura':k[3],'fin_asignatura':k[4],'fecha_medicion':k[5],'plan':k[6],'seccion':k[7],'filas':n,'clasificacion':'B actividad; E jornada no acreditada por sección'} for k,n in group.items()]
dump(P/'EVIDENCIA_ADICIONAL.json',{'objetivos':targets,'filas_respaldos_2024':found,'actividad_previa':activity})
dump(O/'INVENTARIO.json',inv);dump(O/'ACTIVIDAD_AGREGADA.json',summary);dump(O/'CONFIG.json',{'privado':str(P),'output':str(O),'edicion':desc['edicion'],'fuentes_hashes':H})
for f,h in H.items():assert sha256(f)==h
print(json.dumps({'output':str(O),'filas':len(found),'jornadas':[{ 'caso':c,'valores':dict(collections.Counter(r.get('JORNADA') for r in found if r['caso']==c))} for c in sorted(set(labels.values()))]},ensure_ascii=False))

# Contraste puntual de fechas y estados en los originales; no ordenar cambios por
# número de reporte ni convertir fechas de matrícula en fechas de cambio.
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento
import csv
names={'DATOSDEALUMNOS_4094.xlsx','DATOSDEALUMNOS_4490.xlsx','DATOSDEALUMNOS_4649.xlsx','PROMEDIOSDEALUMNOS_3233.xlsx','PROMEDIOSDEALUMNOS_2071.xlsx'}
selected=[r for r in ctx if Path(r['fuente']).name in names or ('T3_2025' in Path(r['fuente']).name and r['caso']=='INF35-10') or ('PRUEBA CUMPLIMIENTO' in r['fuente'] and r['hoja']=='DATOS CRUDOS U+ 19-11-2024')]
selected=list({(r['fuente'],r['hoja'],r['fila']):r for r in selected}.values())
groups=collections.defaultdict(list)
for r in selected:groups[(r['fuente'],r['hoja'])].append(r)
verified=0
for (path,sheet),rs in groups.items():
 h=sha256(path);assert all(r['sha256']==h for r in rs);H[path]=h
 w=openpyxl.load_workbook(path,read_only=True,data_only=True);it=iter(w[sheet].values)
 for hn,row in enumerate(it,1):
  hh=[val(x).upper() for x in row]
  if 'CODCLI' in hh:break
  assert hn<5
 counts=collections.Counter();headers=[]
 for k in hh:
  counts[k]+=1;headers.append(k if counts[k]==1 else k+'__'+str(counts[k]))
 wanted={r['fila']:r for r in rs};done=0
 for n,row in enumerate(it,hn+1):
  if n>max(wanted):break
  if n not in wanted:continue
  actual=dict(zip(headers,row));old=wanted[n]
  for k in ['CODCLI','RUT','CODCARPR','CODCARR','JORNADA','PLAN_DE_ESTUDIO','ANO','PERIODO','CODIGO_PLAN_ESTUDIO','FECHAINICIO','FECHAFIN','FECHA MEDICION','SECCION','FECHAMATRICULA','FECHAFIRMA','SITUACION','ESTADOACADEMICO']:
   if k in old:assert val(actual[k])==val(old[k]),(Path(path).name,n,k)
  done+=1;verified+=1
 assert done==len(rs);w.close()
 print(Path(path).name,sheet,'contraste OK',flush=True)
assert verified==len(selected)
# Confirmar las anclas y el estado pendiente con la edición activa.
s=DiccionarioSiesSeguimiento();unchanged=[]
for t in targets:
 row=json.loads(s.db.execute('select payload from observaciones where id=?',(t['observacion_id'],)).fetchone()[0]);assert not row['codigo_interno_adoptado'] and not row['codigo_documental_atribuible'];unchanged.append(row)
 assert t['codigo_T1'] in s.codigos_mu(persona=t['persona'],anio=t['anio'])['codigos']
s.close()
assert len(found)==22 and len({r['caso'] for r in found})==2
assert {r['JORNADA'] for r in found if r['caso']=='INF35-03'}=={'V'}
assert {r['JORNADA'] for r in found if r['caso']=='INF35-04'}=={'D'}
for c,code in [('INF35-03','I162S2C1J2V4'),('INF35-04','I162S2C1J1V2')]:
 assert {r['CODIGO UNICO'] for r in found if r['caso']==c and r.get('CODIGO UNICO')}=={code}
checks10=[r for r in selected if r['caso']=='INF35-10' and Path(r['fuente']).name in {'DATOSDEALUMNOS_4094.xlsx','DATOSDEALUMNOS_4490.xlsx','DATOSDEALUMNOS_4649.xlsx'}]
assert len(checks10)==3
assert {val(r['FECHAMATRICULA']) for r in checks10}=={'24-01-2025'}
assert {val(r['FECHAFIRMA']) for r in checks10}=={'24-01-2025'}
assert {r['JORNADA'] for r in checks10}=={'V','O'}
reasons={
 'INF35-03':('Los respaldos de preparación MU2024 confirman IINF/V y J2V4 en T1. Actividad T3 con plan IINF20241 y sección 1; PROMEDIOS2071/3233 muestran D. MU2025 J1V1 y MU2026 J1V2.','Falta atribuir V→D al período y distinguir V1/V2 en el destino D. Sección 1 no equivale por sí sola a jornada D.'),
 'INF35-04':('Los respaldos de preparación MU2024 confirman IINF/D y J1V2 en T1. Actividad T3 con plan IINF20241 y sección 20; PROMEDIOS2071 V y PROMEDIOS3233 D. MU2025 J2V4.','Falta atribuir D/V a T2 y T3-2024. Sección 20 no prueba jornada V sin una correspondencia documentada.'),
 'INF35-10':('DATOS4094 V; DATOS4490/4649 O y situación 49. Los tres conservan FECHAMATRICULA y FECHAFIRMA 24-01-2025. PROMEDIOS3233 muestra V para actividad T2; foto T3 O.','Las fechas de matrícula/firma no distinguen el cambio V→O. Falta evidencia de la jornada aplicable en T2-2025; no se infiere de la fecha del archivo.')}
result=[]
for t in targets:
 evidence,pending=reasons[t['caso']]
 refs=[{k:r[k] for k in ['fuente','hoja','fila','sha256']} for r in found+selected if r['caso']==t['caso']]
 result.append({'caso':t['caso'],'anio':t['anio'],'periodo':int(t['periodo']),'codigo_T1':t['codigo_T1'],'codigo_destino':'Pendiente','hallazgo':evidence,'pendiente':pending,'clasificacion':'B evidencia observada; E atribución por período no resuelta','referencias':refs})
dump(P/'EVIDENCIA_FINAL.json',{'observaciones_v5_inalteradas':unchanged,'filas_originales_contrastadas':selected,'filas_preparacion_2024':found})
dump(O/'RESULTADOS.json',{'observaciones':5,'personas':3,'cierres_adicionales':0,'edicion_conservada':desc['edicion'],'resultados':result})
with (O/'TABLA_CINCO.csv').open('w',newline='') as f:
 keys=[k for k in result[0] if k!='referencias'];wr=csv.DictWriter(f,fieldnames=keys,delimiter=';');wr.writeheader();wr.writerows({k:r[k] for k in keys} for r in result)
report='''# Cinco destinos pendientes después de los siete cierres aprobados

**D/C.** Los siete cierres aprobados están aplicados en `v5_20261023_siete_jornadas`.
Este diagnóstico revisa otras cinco observaciones de tres personas, sin nuevas adjudicaciones.
La atribución documental de los cierres internos sigue pendiente. No cambia tasas ni denominadores.

| Caso | Destinos pendientes | Código T1 observado (B) | Hallazgo adicional (B) | Qué falta (E) |
|---|---|---|---|---|
| INF35-03 | T2 y T3-2024 (2) | I162S2C1J2V4 | Se confirma V en los respaldos de preparación 2024; 14 filas entre hojas y copias, no 14 matrículas distintas. | Situar el paso a D por período y distinguir J1V1/J1V2. |
| INF35-04 | T2 y T3-2024 (2) | I162S2C1J1V2 | Se confirma D en los respaldos de preparación 2024; 8 filas entre hojas y copias, no 8 matrículas distintas. | Situar los cambios D/V: los respaldos de promedios discrepan para la actividad histórica. |
| INF35-10 | T2-2025 (1) | I162S2C1J2V4 | DATOS4094 V y DATOS4490/4649 O conservan la misma fecha de matrícula/firma, 24-01-2025. | Determinar si el cambio a O ya regía en T2; las fechas comunes no lo resuelven. |

**B/C. Confirmación del origen 2024.** Se revisaron seis libros de preparación de MU2024,
con 22 filas coincidentes por RUT exacto con DV y contexto IINF. No contienen CODCLI
en el esquema seleccionado: no se inventó esa llave ni se eligió expediente por nombre.
Se conservaron encabezados duplicados separadamente, porque JORNADA UMAS y la
columna posterior JORNADA SIES no son el mismo campo. En DATOS598, filas 1011/926,
y DATOS293, hoja SIES Final, filas 860/775, los componentes y códigos son
respectivamente J2V4 para INF35-03 y J1V2 para INF35-04. Coinciden con el ancla
MU2024 ya documentada. Esto refuerza el origen T1; no acredita el destino T2/T3.
El nombre «SIES Final» no acredita por sí solo envío ni aceptación en plataforma.

**B/E. Actividad fechada no equivale a jornada histórica.** En PRUEBA CUMPLIMIENTO
INGRESO CALIFICACIONES T3_2024.xlsx, hoja DATOS CRUDOS U+ 19-11-2024, hay dos filas
para INF35-03 (1866–1867) y cuatro para INF35-04 (1971–1974), plan IINF20241,
período 3, inicio de asignatura 14-10-2024, fin 04-01-2025 y medición 19-11-2024.
Las secciones son 1 y 20 respectivamente; esa hoja no contiene JORNADA.
Sin equivalencia documentada sección-asignatura-período↔jornada no se transforma
ese número en J1 o J2. Fechas de asignatura no son fechas de cambio de plan/jornada.
PROMEDIOS2071/3233 conservan actividad del período pero no acreditan por sí solos
la vigencia histórica de la jornada que acompaña al reporte.

**B/E. Fechas del tercer caso.** Para INF35-10 se releen DATOS4094, DATOS4490,
DATOS4649, PROMEDIOS3233 y la foto T3-2025. Matrícula/firma permanecen en enero
mientras cambia la jornada V/O y aparece situación 49. Por tanto esas fechas
no identifican el acto del cambio. T1 V y T3 O delimitan los contextos observados,
pero no adjudican T2. No se ordenan eventos por número de reporte, ni se
retropropaga el estado de la foto T3 a T2.

**C. Trazabilidad.** RESULTADOS.json contiene por observación las referencias
archivo/hoja/fila/hash. INVENTARIO.json distingue esquemas leídos y hojas que
no cumplen el esquema buscado; no dice que estas últimas carezcan de personas.
La primera exploración exigía CODCLI y no encontraba estos respaldos: se corrigió
el lector para RUT exacto + contexto de carrera. Los ensayos anteriores sin
manifiesto son exploratorios y no sustituyen este diagnóstico.

**C/E. Resultado:** cero cierres adicionales; permanecen cinco destinos por
jornada y, fuera de este foco, seis homologaciones. El foco original de 35 queda
en 24 reutilizables y 11 pendientes. No se fuerza una versión ni se convierte
una ausencia de evidencia en deserción. Bases, denominadores, Excel y diccionario
v5 permanecen iguales durante esta revisión. Sin commit ni push.
'''
(O/'INFORME.md').write_text(report)
(O/'CHECKPOINT.md').write_text('D/C: v5 activo con siete cierres aprobados aplicados; atribución documental pendiente. B/E: revisión adicional confirma T1 de INF35-03/04 pero no destino; INF35-10 conserva fecha matrícula/firma a pesar de V/O. Continúan 03/04 T2/T3-2024 y 10 T2-2025 (cinco observaciones, tres personas). No nuevas propuestas adoptadas. Siguiente evidencia precisa: jornada aplicable por período o equivalencia fechada de sección/plan, y V1/V2 destino de 03; no es necesario el día exacto si se acredita el período. No modificar denominadores.\n')
for f,h in H.items():assert sha256(f)==h,f
G={'rama':subprocess.check_output(['git','-C',str(R),'branch','--show-current'],text=True).strip(),'HEAD':subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()}
assert G=={'rama':'feature/ire-2026','HEAD':'80ca13a5a249a1a2bd53a699f5f73689b1f53040'}
qa={'resultado':'OK_INTEGRIDAD_CON_CINCO_PENDIENTES_E','fuentes_adicionales_2024':6,'filas_coincidentes_en_copias_y_hojas_2024':22,'personas_en_ellas':2,'filas_previas_releidas':verified,'archivos_previos_releidos':len({r['fuente'] for r in selected}),'observaciones_foco':5,'personas_foco':3,'cierres_nuevos':0,'fuentes_diccionario_y_denominadores_inalterados':True,'git_antes_despues':G,'commit_push':False,'limite':'QA de integridad no resuelve atribución histórica de jornada.'}
dump(O/'QA.json',qa)
secrets=set(owners)|set(owners.values())
for f in O.iterdir():assert not any(x in f.read_text() for x in secrets),f.name
manifest={'fecha_hora':now.isoformat(),'proceso':'Seguimiento intertrimestral IPSS 162','alcance':'Cinco destinos por cambio de jornada después de siete cierres internos aprobados','clasificacion':'B/C revisión; E atribución temporal pendiente; no nuevas decisiones D','fuentes_sha256':H,'salidas_sha256':{p.name:sha256(p) for p in O.iterdir()},'privado':str(P),'privados_hashes':{p.name:sha256(p) for p in P.iterdir()},'codigo_sha256':{str(Path(__file__).relative_to(R)):sha256(__file__)},'QA':qa}
dump(O/'MANIFEST.json',manifest)
print(json.dumps({'output':str(O),'manifest_sha256':sha256(O/'MANIFEST.json'),'QA':qa},ensure_ascii=False))
