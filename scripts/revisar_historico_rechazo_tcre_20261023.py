"""Relee respaldos de una persona; conserva estados y fechas sin inferir eventos."""
import collections,datetime,hashlib,io,json,os,re,subprocess,time,unicodedata,zipfile
from pathlib import Path
from zoneinfo import ZoneInfo
import openpyxl
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1];P=Path.home()/'.local/share/ipss'
now=datetime.datetime.now(ZoneInfo('America/Santiago'));stamp=now.strftime('%Y%m%d_%H%M%S')
O=R/'outputs'/('historico_rechazo_tcre_'+stamp);Q=P/('historico_rechazo_tcre_'+stamp)
assert subprocess.run(['git','-C',str(P),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
os.umask(0o077);O.mkdir();Q.mkdir();H={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
def load(p):
 H[str(p)]=sha(p);return json.loads(Path(p).read_text())
def git():return {k:subprocess.check_output(['git','-C',str(R),*a],text=True).strip() for k,a in [('rama',['branch','--show-current']),('HEAD',['rev-parse','HEAD']),('status',['status','--short'])]}
def val(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
def canon(x):return re.sub(r'[^A-Z0-9]','',unicodedata.normalize('NFKD',val(x).upper()).encode('ascii','ignore').decode())
gb=git();dump(O/'GIT_ANTES.json',gb)
prev=R/'outputs/cierre_dos_v2_homologaciones_20261023_091509';pm=load(prev/'MANIFEST.json')
f=Path(pm['privado'])/'REVISION_HOMOLOGACIONES.json';assert sha(f)==pm['privados_hashes'][f.name];case=load(f)
person=case['observacion']['persona'];body,dv=person.split('-');codclis={r['CODCLI'] for r in case['filas_promedios_persona']}
listfile=P/'cambios_plan_12_y_4_20261023_080207/INVENTARIO_ONEDRIVE_RUTAS.txt';H[str(listfile)]=sha(listfile)
paths=listfile.read_text().splitlines()
names={'DATOSDEALUMNOS_367_.xlsx','DATOSDEALUMNOS_1758_CRUDO_10_04_2025.xlsx',
 'DATOSDEALUMNOS_1758_CRUDO_10_04_2025_FINAL_SIES.xlsx','DATOSDEALUMNOS_1758_CRUDO_10_04_2025_FINAL.xlsx',
 'DATOSDEALUMNOS_2176.xlsx','DATOSDEALUMNOS_3194.xlsx','DATOSDEALUMNOS_4490.xlsx','DATOSDEALUMNOS_4649.xlsx',
 'DATOSDEALUMNOS_4094.xlsx','DATOSDEALUMNOS.xlsx','DATOSDEALUMNOS ORIGEN DE LOS DATOS2025.xlsx',
 'CUMPLIMIENTO INGRESO CALIFICACIONES.xlsx','PRUEBA CUMPLIMIENTO INGRESO CALIFICACIONES T3_2024.xlsx',
 'Cumplimiento Ingreso de Notas.xlsx','PROMEDIOSDEALUMNOS_2071.xlsx','PROMEDIOSDEALUMNOS_3233.xlsx'}
selected=sorted({s for s in paths if Path(s).name in names})
selected += [str(Path.home()/'Downloads/2025/DATOSDEALUMNOS_11248.xlsx'),
 str(Path.home()/'Desktop/Caracterizacion_2026-10-22_2027_P1_084218/01_ENTRADAS/DATOSDEALUMNOS_12159.xlsx'),
 str(Path.home()/'Downloads/PROMEDIOSDEALUMNOS_12166.xlsx'),
 str(R.parent/'CARACTERIZACIÓN/.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/PROMEDIOSDEALUMNOS_7804.xlsx')]
expected={}
for manifest in [R/'outputs/reproduccion_puente_20261023_004044/MANIFEST.json', R/'outputs/cambios_plan_12_y_4_20261023_080207/MANIFEST.json',R/'outputs/revision_t3_2024_f02_20261023_082535/MANIFEST.json', prev/'MANIFEST.json']:
 m=load(manifest);expected.update(m.get('fuentes_hashes',{}))
known={};inventory=[];rows=[];errors=[];alerts=[]
keep={'CODCLI','CODCARPR','CODCARR','CODCARRERAALUMNO','JORNADA','SEDE','REGIMEN','PLANDEESTUDIO','CODIGOPLANESTUDIO','ANO','PERIODO','ANOMATRICULA','PERIODOMATRICULA','ANOINGRESO','PERIODOINGRESO','FECHAMATRICULA','FECHAFIRMA','CODRAMO','RAMOEQUIV','CODIGOASIGNATURA','CODSECC','SECCION','FECHAINICIO','FECHAFIN','FECHAREPORTE','FECHAMEDICION','ESTADO','ESTADOACADEMICO','SITUACION','DESCRIPCIONESTADO','CONVALIDADO','NOTAFINAL'}
for path in selected:
 try:
  p=Path(path)
  for attempt in range(2):
   try:data=p.read_bytes();break
   except OSError:
    if attempt:raise
    time.sleep(2)
  h=hashlib.sha256(data).hexdigest();H[path]=h
  assert path not in expected or h==expected[path], 'Hash distinto a respaldo previo'
  if h in known:
   inventory.append({'archivo':path,'sha256':h,'estado':'DUPLICADO_BYTES','alias_de':known[h]});continue
  known[h]=path;w=openpyxl.load_workbook(io.BytesIO(data),read_only=True,data_only=True)
  # openpyxl supplies current timestamps when fields are absent: read XML directly.
  with zipfile.ZipFile(io.BytesIO(data)) as zz:
   core=ET.fromstring(zz.read('docProps/core.xml')) if 'docProps/core.xml' in zz.namelist() else None
   props={k:(core.find('{http://purl.org/dc/terms/}'+k).text if core is not None and core.find('{http://purl.org/dc/terms/}'+k) is not None else None) for k in ['created','modified']}
  props['limite']='Metadatos XML explícitos de creación/guardado; no fecha certificada del corte ni del rechazo. Ausencia = null.'
  for ws in w:
   it=iter(ws.values);headers=None;hr=None;prefix=[]
   for rn in range(1,21):
    try:rr=next(it)
    except StopIteration:break
    hh=[canon(v) for v in rr]
    if 'CODCLI' in hh and 'RUT' in hh:
     headers=hh;hr=rn;break
   if headers is None:
    inventory.append({'archivo':path,'sha256':h,'hoja':ws.title,'estado':'SIN_CABECERA_CODCLI_RUT_PRIMERAS_20_FILAS','docProps':props});continue
   counts=collections.Counter();hh=[]
   for v in headers:counts[v]+=1;hh.append(v if counts[v]==1 else v+'__'+str(counts[v]))
   n=found=0
   for rn,rr in enumerate(it,hr+1):
    n+=1;d=dict(zip(hh,rr));cc=val(d.get('CODCLI'));raw=val(d.get('RUT')).upper().replace('.','').replace(' ','')
    # DIG may belong to the teacher in course reports. Exact CODCLI corroborates body-only RUT.
    same_rut=raw in {person,body,body+dv};known_cc=cc in codclis
    if not same_rut and not known_cc:continue
    if not same_rut:
     alerts.append({'archivo':path,'hoja':ws.title,'fila':rn,'motivo':'CODCLI encontrado sin RUT concordante'});continue
    if not known_cc and raw==body:
     dd=val(d.get('DIG')).upper()
     if dd!=dv:alerts.append({'archivo':path,'hoja':ws.title,'fila':rn,'motivo':'RUT cuerpo sin CODCLI conocido ni DV corroborado'});continue
    z={k:val(v) for k,v in d.items() if k.split('__')[0] in keep or any(t in k for t in ['FECHACAMBIO','FECHARECHAZ','FECHAESTADO','FECHASITUACION'])}
    z.update(archivo=path,sha256=h,hoja=ws.title,fila=rn,persona=person,CODCLI=cc,metodo='CODCLI exacto + RUT corroborado' if known_cc else 'RUT exacto con DV')
    rows.append(z);found+=1
   inventory.append({'archivo':path,'sha256':h,'hoja':ws.title,'fila_encabezado':hr,'encabezados_normalizados':hh,'filas_leidas':n,'filas_persona':found,'docProps':props,'estado':'LEIDO'})
  w.close();print(json.dumps({'archivo':p.name,'filas_persona':sum(x['archivo']==path for x in rows)}),flush=True)
 except Exception as e:
  errors.append({'archivo':path,'error':str(e)});print(json.dumps({'archivo':Path(path).name,'error':str(e)}),flush=True)
 dump(Q/'FILAS_HISTORICAS_PRIVADAS.json',rows);dump(O/'INVENTARIO.json',inventory);dump(O/'ERRORES_LECTURA.json',errors)
dump(Q/'ALERTAS_IDENTIDAD.json',alerts);dump(O/'FUENTES_HASHES.json',H)
dump(O/'CONFIG.json',{'output':str(O),'privado':str(Q),'anterior':str(prev),'fuentes_seleccionadas':selected,'fecha_hora':now.isoformat()})
summary={'archivos_unicos_leidos':len(known),'hojas_leidas':sum(x['estado']=='LEIDO' for x in inventory),'filas_persona':len(rows),'alertas_identidad':len(alerts),'errores':len(errors),'codigos_nuevos_adoptados':0}
dump(O/'RESULTADOS_LECTURA.json',summary)
print(json.dumps({'salida':str(O),'privado':str(Q),'resultado':summary},ensure_ascii=False),flush=True)
