"""Audita secciones por asignatura/período; no adjudica códigos ni altera fuentes."""
from pathlib import Path
import sys,json,collections,datetime,subprocess,re,zipfile,xml.etree.ElementTree as ET,time
from zoneinfo import ZoneInfo
import openpyxl
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256,rut_normalizado
now=datetime.datetime.now(ZoneInfo('America/Santiago'));O=R/'outputs'/('secciones_cinco_jornadas_'+now.strftime('%Y%m%d_%H%M%S'));P=Path.home()/'.local/share/ipss'/O.name
assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
O.mkdir();P.mkdir(mode=0o700);H={}
def val(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
def dump(p,x):
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
 if p.is_relative_to(P):p.chmod(0o600)
def read(p):
 p=Path(p);H[str(p)]=sha256(p);return json.loads(p.read_text())
def identity(x):
 try:return rut_normalizado(val(x))
 except ValueError:return None
def headers(row):
 c=collections.Counter();h=[]
 for x in row:
  k=val(x).upper();c[k]+=1;h.append(k if c[k]==1 else k+'__'+str(c[k]))
 return h
active=read(R/'data/diccionario_sies_seguimiento/activo.json');desc=read(R/active['descriptor']);assert H[str(R/active['descriptor'])]==active['sha256'];H[desc['base_privada']['ruta']]=desc['base_privada']['sha256']
targets=read(Path(desc['base_privada']['ruta']).parent/'CINCO_PENDIENTES.json');persons={r['persona']:r['caso'] for r in targets};cc={r['CODCLI']:r['caso'] for r in targets};focus={(r['caso'],str(r['anio']),str(r['periodo'])) for r in targets};assert len(focus)==5
s=DiccionarioSiesSeguimiento();mu=collections.defaultdict(set)
for person,year,code in s.db.execute('select persona,anio,codigo from mu_anual'):mu[(person,str(year))].add(code)
pre=[json.loads(s.db.execute('select payload from observaciones where id=?',(r['observacion_id'],)).fetchone()[0]) for r in targets];s.close()
ctxfile=Path('/Users/alexi/.local/share/ipss/cierre_14_jornadas_15_20261023_133759/JORNADAS_15_CONTEXTO_COMPLETO.json');ctx=read(ctxfile);ctx=[r for r in ctx if r.get('caso') in persons.values()]
root=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/Indicadores Intermedios Academicos VRA')
paths=[root/n for n in ['INFORME RENDIMIENTO ACADEMICO 27012025.xlsx','INFORME RENDIMIENTO ACADEMICO 27012025-1.xlsx','INFORME RENDIMIENTO ACADEMICO 27012025-2.xlsx','INFORME RENDIMIENTO_ACADEMICO_20261_FINAL2.xlsx','SEGUIMIENTO_ACADEMICO.xlsx','GESTIONSGE_1703.xlsx']]
# Exact schema fields only, never names, addresses or third-party identifiers.
keep=['ANO','PERIODO','RUT','CODIGOCARRERA','REGIMEN','JORNADA','CODIGORAMO','SECCIONRAMO','FECHAINICIO','FECHAFIN','ESTADO_ASIGNATURA','ESTADO','ACTIVIDAD','NOTA']
inventory=[];alltarget=[];groupstats=[];privatepeers=[];notes=[]
def groupkey(d):return tuple(d.get(k,'') for k in ['ANO','PERIODO','CODIGOCARRERA','REGIMEN','CODIGORAMO','SECCIONRAMO'])
for p in paths:
 w=None
 for attempt in range(3):
  try:w=openpyxl.load_workbook(p,read_only=True,data_only=True);break
  except (OSError,zipfile.BadZipFile):
   if attempt<2:time.sleep(1)
 if w is None:inventory.append({'fuente':str(p),'estado':'ILEGIBLE_TRAS_TRES_INTENTOS'});continue
 h=sha256(p);H[str(p)]=h
 with zipfile.ZipFile(p) as z:
  meta={x.tag.split('}')[-1]:x.text for x in ET.fromstring(z.read('docProps/core.xml')) if x.tag.split('}')[-1] in ['created','modified']} if 'docProps/core.xml' in z.namelist() else {}
 for ws in w:
  it=iter(ws.values);hd=headers(next(it));entries=[];coverage=collections.Counter();rawcount=0;badid=0
  if all(k in hd for k in ['ANO','PERIODO','RUT','SECCIONRAMO','CODIGORAMO','JORNADA']):
   for n,row in enumerate(it,2):
    rawcount+=1;d=dict(zip(hd,row));person=identity(d['RUT']);coverage[(val(d['ANO']),val(d['PERIODO']))]+=1
    if person is None:badid+=1;continue
    if val(d.get('CODIGOCARRERA'))!='IINF':continue
    z={k:val(d[k]) for k in keep if k in d};z.update(persona=person,fuente=str(p),hoja=ws.title,fila=n,sha256=h);entries.append(z)
   relevant=[r for r in entries if r['persona'] in persons]
   for r in relevant:r['caso']=persons[r['persona']]
   alltarget+=relevant;fkeys={groupkey(r) for r in relevant if (r['caso'],r['ANO'],r['PERIODO']) in focus}
   for k in sorted(fkeys):
    gr=[r for r in entries if groupkey(r)==k];peer=[r for r in gr if r['persona'] not in persons];privatepeers+=peer
    byperson=collections.defaultdict(set)
    for r in peer:byperson[r['persona']].add(r['JORNADA'])
    # Two concordant annual anchors are only a comparator, not truth per quarter.
    stable=collections.Counter();annual=collections.Counter();stablepeople=[]
    for person in byperson:
     a={c for c in mu[(person,k[0])] if c.startswith('I162S2C1J')};b={c for c in mu[(person,str(int(k[0])+1))] if c.startswith('I162S2C1J')}
     if len(a)==1:annual[next(iter(a))]+=1
     if a==b and len(a)==1:stable[next(iter(a))]+=1;stablepeople.append(person)
    groupstats.append({'fuente':str(p),'hoja':ws.title,'sha256':h,'anio':k[0],'periodo':k[1],'carrera':k[2],'regimen':k[3],'asignatura':k[4],'seccion':k[5],'casos':sorted({r['caso'] for r in gr if 'caso' in r}),'personas_pares':len(byperson),'jornadas_pares_por_persona':dict(collections.Counter('/'.join(sorted(v)) for v in byperson.values())),'codigos_mu_anio_pares':dict(annual),'codigos_pares_dos_anclas_concordantes':dict(stable),'clasificacion':'B/C asociación de compañeros; no adjudicación individual ni equivalencia universal'})
   inventory.append({'fuente':str(p),'hoja':ws.title,'sha256':h,'filas':rawcount,'identidad_invalida':badid,'cobertura': [{'anio':k[0],'periodo':k[1],'filas':n} for k,n in coverage.items()],'filas_foco':len(relevant),'metadata_no_corte':meta})
  elif 'RUT_ALUMNO' in hd and 'OBSERVACION' in hd:
   matched=0
   for n,row in enumerate(it,2):
    d=dict(zip(hd,row));person=identity(d['RUT_ALUMNO'])
    # Some reports repeat RUT, retaining the original header order.
    if person not in persons and 'RUT_ALUMNO__2' in d:person=identity(d['RUT_ALUMNO__2'])
    if person not in persons:continue
    matched+=1
    z={k:val(d[k]) for k in ['ASUNTO','OBSERVACION','CODCARR','FECHA_COMUNICO','FECHA_COMUNICO INGLES','FECHA_COMUNICO ESPANOL','DIA','MES','ANIO','TIPO_COMUNICACION'] if k in d};z.update(caso=persons[person],persona=person,fuente=str(p),hoja=ws.title,fila=n,sha256=h);notes.append(z)
   inventory.append({'fuente':str(p),'hoja':ws.title,'sha256':h,'tipo':'REGISTRO_CONTACTO','coincidencias_foco':matched,'metadata_no_corte':meta})
  else:inventory.append({'fuente':str(p),'hoja':ws.title,'sha256':h,'estado':'ESQUEMA_FUERA_DE_FOCO','encabezados':hd})
 w.close();print(p.name,'leído',flush=True)
# All source row repetitions remain private; public summaries count unique course sections.
summ=[]
for source in paths:
 for c in sorted(set(persons.values())):
  rows=[r for r in alltarget if r['fuente']==str(source) and r['caso']==c]
  keys=sorted({(r['ANO'],r['PERIODO']) for r in rows})
  for year,period in keys:
   q=[r for r in rows if r['ANO']==year and r['PERIODO']==period]
   combo={(r['CODIGORAMO'],r['SECCIONRAMO'],r['JORNADA'],r['FECHAINICIO'],r['FECHAFIN']) for r in q}
   summ.append({'fuente':str(source),'caso':c,'anio':year,'periodo':period,'filas_evaluaciones':len(q),'asignatura_seccion_jornada_fechas_unicas':len(combo),'jornadas':sorted({r['JORNADA'] for r in q}),'secciones':sorted({r['SECCIONRAMO'] for r in q}),'es_foco':(c,year,period) in focus})
dump(P/'DETALLE.json',{'objetivos':targets,'observaciones_antes':pre,'actividad_foco':alltarget,'pares_secciones':privatepeers,'contactos':notes})
dump(O/'INVENTARIO.json',inventory);dump(O/'SECCIONES_PARES.json',groupstats);dump(O/'RESUMEN_ACTIVIDAD.json',summ)
for f,h in H.items():assert sha256(f)==h,f
dump(O/'CONFIG.json',{'privado':str(P),'output':str(O),'fuentes_hashes':H,'edicion':desc['edicion'],'fecha_hora':now.isoformat()})
print(json.dumps({'output':str(O),'actividad':len(alltarget),'grupos':len(groupstats),'notas':len(notes),'resumen':summ},ensure_ascii=False))
