"""Revisa doce destinos, conserva v4 y propone solo cierres internos acotados."""
from pathlib import Path
import sys,json,csv,collections,datetime,subprocess,zipfile,xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo
import openpyxl
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
from common.catalogos_sies import cargar_catalogo,resolver_catalogo
now=datetime.datetime.now(ZoneInfo('America/Santiago'));O=R/'outputs'/('revision_12_jornadas_'+now.strftime('%Y%m%d_%H%M%S'));P=Path.home()/'.local/share/ipss'/O.name
assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
O.mkdir();P.mkdir(mode=0o700);H={}
def read(p,h=None):
 p=Path(p);actual=sha256(p)
 if h:assert actual==h,str(p)
 H[str(p)]=actual;return json.loads(p.read_text())
def dump(p,x):
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
 if p.is_relative_to(P):p.chmod(0o600)
def private(m,name):return read(Path(m['privado'])/name,m['privados_hashes'][name])
def norm(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
git=lambda *a:subprocess.check_output(['git','-C',str(R),*a],text=True).strip()
g={'rama':git('branch','--show-current'),'HEAD':git('rev-parse','HEAD')}
active=read(R/'data/diccionario_sies_seguimiento/activo.json');desc=read(R/active['descriptor'],active['sha256']);assert desc['edicion']=='v4_20261023_inf35_12'
H[desc['base_privada']['ruta']]=desc['base_privada']['sha256']
m=read(R/'outputs/cierre_inf35_07_jornadas_14_20261023_135630/MANIFEST.json');prev=read(R/'outputs/cierre_14_jornadas_15_20261023_133759/MANIFEST.json')
targets=[r for r in private(m,'JORNADAS_14_PENDIENTES.json') if r['caso']!='INF35-12'];assert len(targets)==12 and len({r['persona'] for r in targets})==7
context=private(prev,'JORNADAS_15_CONTEXTO_COMPLETO.json');cuts=private(m,'FILAS_CORTES_VERIFICADAS.json');cases={r['caso'] for r in targets}
context=[r for r in context if r.get('caso') in cases];cuts=[r for r in cuts if r.get('caso') in cases]
s=DiccionarioSiesSeguimiento();observations=[];mu={}
for t in targets:
 r=json.loads(s.db.execute('select payload from observaciones where id=?',(t['observacion_id'],)).fetchone()[0]);assert not r['codigo_interno_adoptado'] and not r['codigo_documental_atribuible'];assert r['persona']==t['persona'] and r['CODCLI']==t['CODCLI'];observations.append(r)
 mu[t['caso']]=s.codigos_mu(persona=t['persona'],anio=t['anio']);assert t['codigo_T1'] in mu[t['caso']]['codigos']

# Selección explícita de fuentes; la identidad no se imprime ni se publica.
names={'PROMEDIOSDEALUMNOS_2071.xlsx','PROMEDIOSDEALUMNOS_3233.xlsx','DATOSDEALUMNOS_3194.xlsx','DATOSDEALUMNOS_4490.xlsx'}
selected=[r for r in context if Path(r['fuente']).name in names or 'BASE_RETENCION_MATRICULA' in r['fuente'] or (Path(r['fuente']).name.endswith('T3_2025 2.xlsx')) or (r['caso']=='INF35-11' and Path(r['fuente']).name in {'PROMEDIOSDEALUMNOS_7804.xlsx','PROMEDIOSDEALUMNOS_12166.xlsx'})]
selected += [r for r in cuts if r['caso']=='INF35-11' and (r['corte_nominal'].startswith('2026-07') or r['corte_nominal'].startswith('2026-10-02'))]
unique={(r['fuente'],r['hoja'],r['fila']):r for r in selected};selected=list(unique.values());groups=collections.defaultdict(list)
for r in selected:groups[(r['fuente'],r['hoja'])].append(r)
metadata={};count=0
for (path,sheet),rs in groups.items():
 h=sha256(path);assert all(r['sha256']==h for r in rs);H[path]=h
 if path not in metadata:
  with zipfile.ZipFile(path) as z:
   metadata[path]={x.tag.split('}')[-1]:x.text for x in ET.fromstring(z.read('docProps/core.xml')) if x.tag.split('}')[-1] in ['created','modified']} if 'docProps/core.xml' in z.namelist() else {'estado':'sin docProps/core.xml'}
 w=openpyxl.load_workbook(path,read_only=True,data_only=True);it=iter(w[sheet].values)
 for hn,row in enumerate(it,1):
  headers=[norm(x).upper() for x in row]
  if 'CODCLI' in headers or 'ANIO_INFORMADO' in headers:break
  assert hn<5
 wanted={r['fila']:r for r in rs};done=0
 for n,row in enumerate(it,hn+1):
  if n>max(wanted):break
  if n not in wanted:continue
  actual=dict(zip(headers,row));r=wanted[n]
  for k in ['CODCLI','RUT','N_DOC','DV','TIPO_DOC','CODCARPR','CODCARR','JORNADA','PLAN_DE_ESTUDIO','ANO','PERIODO','REGIMEN','SITUACION','ANIO_INFORMADO','COD_SED','COD_CAR','JOR','VERSION','ANIO_ING_ORI','ANIO_ING_ACT']:
   if k in r:assert norm(actual[k])==norm(r[k]),(Path(path).name,n,k)
  count+=1;done+=1
 assert done==len(rs);w.close();print(Path(path).name,sheet,'verificado',flush=True)
assert count==len(selected)

def rows(case,basename,year=None,period=None):
 return [r for r in selected if r['caso']==case and Path(r['fuente']).name==basename and (year is None or str(r.get('ANO'))==str(year)) and (period is None or str(r.get('PERIODO'))==str(period))]
for c in ['INF35-01','INF35-02']:
 for t in [2,3]:assert {r['JORNADA'] for r in rows(c,'PROMEDIOSDEALUMNOS_2071.xlsx',2024,t)}=={'D'}
 assert s.codigos_mu(persona=next(r['persona'] for r in targets if r['caso']==c),anio=2025)['codigos']==['I162S2C1J1V2']
assert {r['JORNADA'] for r in rows('INF35-07','PROMEDIOSDEALUMNOS_3233.xlsx',2025,2)}=={'V'}
t3_07=[r for r in selected if r['caso']=='INF35-07' and 'T3_2025' in r['fuente']];assert len(t3_07)==1 and t3_07[0]['JORNADA']=='V'
inf11=[r for r in cuts if r['caso']=='INF35-11'];assert len(inf11)==6 and {r['JORNADA'] for r in inf11}=={'O'}
for t in [2,3]:
 q=rows('INF35-11','PROMEDIOSDEALUMNOS_12166.xlsx',2026,t);assert q and {r['PLAN_DE_ESTUDIO'] for r in q}=={'IINF20241'} and {r['JORNADA'] for r in q}=={'O'}
catalog=resolver_catalogo(cargar_catalogo(2026),codcarpr='IINF',sede='RE',jornada='O');assert catalog['candidatos']==['I162S2C1J4V2'];H[str(R/'data/catalogos_sies/2026/mu2026_20261013/catalogo.json')]=sha256(R/'data/catalogos_sies/2026/mu2026_20261013/catalogo.json')

reasons={
 'INF35-01':('I162S2C1J1V2','CONTINUIDAD_T1_PROPUESTA','T1-2024 y MU2025 J1V2; PROMEDIOS2071 D en períodos 2/3 de 2024, PROMEDIOS3233 D y foto T3-2025 D.','No acredita jornada histórica de cada clase ni ausencia de cambios intermedios; requiere aprobar continuidad interna acotada.'),
 'INF35-02':('I162S2C1J1V2','CONTINUIDAD_T1_PROPUESTA','T1-2024 y MU2025 J1V2; PROMEDIOS2071 D en períodos 2/3 de 2024. Respaldos posteriores muestran O.','Cambio D→O sin fecha efectiva; la propuesta conserva el ancla 2024 y no retropropaga O. Requiere decisión interna acotada.'),
 'INF35-03':('','PENDIENTE_CAMBIO_Y_VERSION','T1-2024 J2V4; PROMEDIOS2071/3233 D para actividad 2024; MU2025 J1V1 y MU2026 J1V2.','Falta situar V→D en T2/T3 y distinguir J1V1/J1V2. El plan IINF20241 no determina versión única.'),
 'INF35-04':('','PENDIENTE_CAMBIOS_MULTIPLES','T1-2024 J1V2; PROMEDIOS2071 V; MU2025 J2V4; PROMEDIOS3233 y foto T3-2025 D; después O.','No se fecha D→V→D para los períodos de 2024. No elegir T1 o código posterior por conveniencia.'),
 'INF35-07':('I162S2C1J2V4','CONTINUIDAD_T1_PROPUESTA','T1-2025 J2V4; PROMEDIOS3233 V en período 2; foto T3-2025 V y cierre interno T3 aprobado J2V4.','El respaldo no prueba ausencia de cambios intermedios; requiere aprobar continuidad T2 explícitamente. No reutilizar O posterior.'),
 'INF35-10':('','PENDIENTE_PERIODO_CAMBIO','T1-2025 J2V4; PROMEDIOS3233 V en período 2 y DATOS3194 V; DATOS4490 y foto T3-2025 O.','Cambio V→O sin atribución a T2. Metadata de archivo no fecha el acto; falta respaldo temporal comparable dentro de T2.'),
 'INF35-11':('I162S2C1J4V2','DESTINO_O_PROPUESTO','T1-2026 J1V2; respaldo congelado julio y fotos agosto-octubre O, situación 49; plan IINF20241 y actividad períodos 2/3; catálogo 2026 IINF/RE/O resuelve J4V2.','Propuesta interna referida a fotos del seguimiento; congelamiento de julio no acredita el cierre exacto del 13-julio ni el día administrativo del cambio. Documental destino pendiente.')}
summary=[]
for t in targets:
 code,state,proof,pending=reasons[t['caso']]
 summary.append({'caso':t['caso'],'anio':t['anio'],'periodo':int(t['periodo']),'codigo_T1':t['codigo_T1'],'codigo_propuesto_no_adoptado':code or 'Pendiente','resultado':state,'clasificacion':'B evidencia; C propuesta; E atribución y decisión pendientes','evidencia':proof,'pendiente':pending})
assert sum(r['codigo_propuesto_no_adoptado']!='Pendiente' for r in summary)==7
dump(P/'EVIDENCIA_PRIVADA.json',{'objetivos':targets,'observaciones_v4':observations,'filas_primarias_verificadas':selected,'otros_cortes_gobernados':inf11,'mu_por_caso':mu})
dump(O/'RESULTADOS.json',{'observaciones':12,'personas':7,'propuestas_cierre_interno':7,'sin_propuesta_suficiente':5,'cierres_aplicados':0,'edicion_conservada':desc['edicion'],'tabla':summary})
dump(O/'METADATOS_FUENTES.json',{'clasificacion':'B metadata; no fecha de cambio académico','archivos':metadata,'catalogo_2026_O':catalog})
with (O/'TABLA_12_OBSERVACIONES.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(summary[0]),delimiter=';');w.writeheader();w.writerows(summary)
report='''# Revisión de doce destinos por cambio de jornada

**B/C.** Foco: siete personas y doce observaciones todavía pendientes en v4.
No son doce estudiantes nuevos ni un denominador de retención. Se verifica
el código T1, plan IINF20241, identidad y CODCLI contra respaldos gobernados.

**C/E. Resultado:** siete propuestas de cierre interno y cinco sin propuesta
suficientemente respaldada. **Cero adjudicaciones aplicadas**. Las siete requieren
decisión explícita; ninguna se convierte en atribución documental SIES.

| Caso | Períodos | Propuesta | N | Fundamento y límite |
|---|---|---|---:|---|
| INF35-01 | T2/T3-2024 | I162S2C1J1V2 | 2 | Ancla T1 y MU2025 concordantes; respaldos D. Continuidad propuesta, no prueba de cada día. |
| INF35-02 | T2/T3-2024 | I162S2C1J1V2 | 2 | T1/MU2025 y PROMEDIOS2071 D; O aparece en otros respaldos. No retropropagar el cambio. |
| INF35-07 | T2-2025 | I162S2C1J2V4 | 1 | T1 V, actividad período 2 en respaldo V y foto T3 V; T3 ya aprobado. |
| INF35-11 | T2/T3-2026 | I162S2C1J4V2 | 2 | Fotos julio/octubre O y catálogo con candidato único; destino interno propuesto. |
| INF35-03 | T2/T3-2024 | Pendiente | 2 | T1 J2V4, luego D; MU2025 J1V1 y MU2026 J1V2. Falta período y versión. |
| INF35-04 | T2/T3-2024 | Pendiente | 2 | T1 D, respaldo V, otros D y después O; no se ubican los cambios en 2024. |
| INF35-10 | T2-2025 | Pendiente | 1 | T1/actividad T2 en respaldo V, foto T3 O; cambio no ubicado dentro/fuera de T2. |

**B/C.** Para INF35-01/02 se reúnen dos anclas anuales concordantes y
PROMEDIOS2071 con plan y actividad T2/T3-2024 en D. Su core.xml fue creado
el 08-mayo-2025: no es una foto contemporánea de cada trimestre de 2024.
La propuesta acepta continuidad entre las anclas como decisión interna, no
afirma que no haya existido un cambio transitorio. INF35-02 tiene respaldos O
posteriores; no se los usa para reescribir la jornada de 2024.

**B/C.** INF35-07 tiene T2 en PROMEDIOS3233 V y foto T3-2025 V, además de
su ancla T1 J2V4. No se conoce fecha de extracción por core.xml de 3233;
el respaldo es corroboración de plan/período, no una foto exacta de cierre.
El cierre T3 aprobado no se extiende automáticamente a T2.

**B/C.** INF35-11 difiere de INF35-12: pasó de D a O. Las seis fotos revisadas
desde el respaldo congelado en julio hasta octubre conservan O. El catálogo
operativo MU2026 devuelve J4V2 para IINF/RE/O. El plan es IINF20241 y
PROMEDIOS incluye períodos 2/3. Se propone ese destino para el seguimiento;
no se data el acto ni se considera julio21 una fotografía exacta de julio13.

**B/E.** INF35-03/04 no permiten elegir entre el código T1 y los posteriores
sin decidir primero en qué período corresponde cada jornada. INF35-03 además
tiene J1V1 y J1V2 en distintos años con el mismo plan. INF35-10 tiene respaldo
V y posterior O, pero no se ha acreditado el momento efectivo dentro de T2.
La presencia de fechas de creación/modificación en archivos no lo soluciona:
DATOS3194 registra modificación en 2026 y DATOS4490 creación en octubre2025;
no se ordenan eventos académicos por número de reporte o esas marcas.

**C.** TABLA_12_OBSERVACIONES.csv conserva cada observación con propuesta,
evidencia y pendiente. EVIDENCIA_PRIVADA.json conserva llaves, fuentes, hojas,
filas y hashes únicamente fuera de Git. Los identificadores no se publican.
Los respaldos no calculan por sí mismos vigencia, deserción ni nuevas tasas.

**C.** Diccionario v4, bases, denominadores y Excel intactos; sin commit/push.
La revisión no reduce el pendiente vigente: el foco original sigue en 17
reutilizables y 18 pendientes. Si se aprobaran las siete propuestas, ese foco
pasaría a 24 reutilizables y 11 pendientes (cinco de jornada y seis homologaciones).
Es un escenario, no un cierre aplicado. QA de integridad no equivale a prueba
documental del destino. No se impone una regla universal de continuidad.
'''
(O/'INFORME.md').write_text(report)
(O/'CHECKPOINT.md').write_text('C/E: siete propuestas internas (INF35-01/02 T2/T3-2024 J1V2; INF35-07 T2-2025 J2V4; INF35-11 T2/T3-2026 J4V2), cinco destinos sin propuesta suficiente (03/04 dos cada uno y 10 uno). No aplicadas. V4 sigue activa. Esperar aprobación acotada; no confundir propuestas con atribución documental ni modificar denominadores.\n')
for path,h in H.items():assert sha256(path)==h,path
assert g=={'rama':git('branch','--show-current'),'HEAD':git('rev-parse','HEAD')}
for r in observations:assert json.loads(s.db.execute('select payload from observaciones where id=?',(r['observacion_id'],)).fetchone()[0])==r
s.close()
qa={'resultado':'OK_REVISION_CON_LIMITES','observaciones_verificadas':12,'personas':7,'filas_originales_releidas':count,'archivos_originales_releidos':len({r['fuente'] for r in selected}),'propuestas_sin_adoptar':7,'pendientes_sin_propuesta':5,'hash_diccionario_inalterado':True,'fuentes_inalteradas':True,'denominadores_inalterados':True,'git_antes_despues':g,'commit_push':False,'limites':['Fotos posteriores no acreditan jornada de cada clase histórica.','Propuestas internas para aprobación; no cierres documentales.','T2-2026: congelamiento julio21 no acredita foto exacta julio13.']};dump(O/'QA.json',qa)
secrets={r['persona'] for r in targets}|{r['CODCLI'] for r in targets}
for p in O.iterdir():assert not any(x in p.read_text() for x in secrets)
dump(O/'MANIFEST.json',{'fecha_hora':now.isoformat(),'proceso':'Seguimiento intertrimestral IPSS 162','alcance':'12 observaciones por jornada; propuestas sin adoptar','clasificacion':'B/C evidencia y revisión; E decisión/atribución pendiente','fuentes_sha256':H,'salidas_sha256':{p.name:sha256(p) for p in O.iterdir()},'privado':str(P),'privados_hashes':{p.name:sha256(p) for p in P.iterdir()},'codigo_hashes':{str(p.relative_to(R)):sha256(p) for p in [Path(__file__),R/'docs/ESPECIFICACION_REVISION_12_JORNADAS_20261023.md']},'QA':qa})
print(json.dumps({'salida':str(O),'propuestas':7,'pendientes':5,'cierres_aplicados':0,'filas_releidas':count,'manifest_sha256':sha256(O/'MANIFEST.json')},ensure_ascii=False))
