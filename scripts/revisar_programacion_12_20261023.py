"""Revisión de continuidad por expediente; propuestas sin alterar estados vigentes."""
import collections,datetime,hashlib,io,json,os,re,subprocess,unicodedata,zipfile
from pathlib import Path
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET
import openpyxl
R=Path(__file__).resolve().parents[1];P=Path.home()/'.local/share/ipss'
now=datetime.datetime.now(ZoneInfo('America/Santiago'));stamp=now.strftime('%Y%m%d_%H%M%S')
O=R/'outputs'/('revision_programacion_12_'+stamp);Q=P/('revision_programacion_12_'+stamp)
assert subprocess.run(['git','-C',str(P),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
os.umask(0o077);O.mkdir();Q.mkdir();H={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
def src(p,h=None):
 p=Path(p);a=sha(p);assert h is None or a==h,str(p);H[str(p)]=a;return p
def load(p,h=None):return json.loads(src(p,h).read_text())
def val(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
def canon(x):return re.sub('[^A-Z0-9]','',unicodedata.normalize('NFKD',val(x).upper()).encode('ascii','ignore').decode())
def git():return {k:subprocess.check_output(['git','-C',str(R),*a],text=True).strip() for k,a in [('rama',['branch','--show-current']),('HEAD',['rev-parse','HEAD']),('status',['status','--short'])]}
dump(O/'GIT_ANTES.json',git())
prev=R/'outputs/clasificacion_tcre_siguiente_bloque_20261023_095113';m=load(prev/'MANIFEST.json');expected=m['fuentes_hashes']
a=load(Path(m['privado'])/'PROGRAMACION_24_PREVALIDACION.json',m['privados_hashes']['PROGRAMACION_24_PREVALIDACION.json'])
focus=[x for x in a if x['tipo_evidencia']=='CON_APROBACION_SIN_RECONOCIMIENTO'];assert len(focus)==12
persons={x['observacion']['persona'] for x in focus};labels={p:f'P{i+1:02}' for i,p in enumerate(sorted({x['observacion']['persona'] for x in a}))}
base=load(P/'reproduccion_puente_20261023_004044/OBSERVACIONES_PRIVADAS.json',expected[str(P/'reproduccion_puente_20261023_004044/OBSERVACIONES_PRIVADAS.json')])
contexts=[x for x in base if x['persona'] in persons];owners={x['CODCLI']:x['persona'] for x in contexts};bodymap={p.split('-')[0]:p for p in persons}
assert len(bodymap)==len(persons)
config=load(R/'outputs/historico_rechazo_tcre_20261023_093127/CONFIG.json')
selected=config['fuentes_seleccionadas'];rows=[];inventory=[];errors=[];alerts=[];seen={}
keep={'CODCLI','CODCLI2','CODCARPR','CODCARR','CODCARRERAALUMNO','JORNADA','SEDE','REGIMEN','PLANDEESTUDIO','CODIGOPLANESTUDIO','ANO','PERIODO','ANOMATRICULA','PERIODOMATRICULA','ANOINGRESO','PERIODOINGRESO','FECHAMATRICULA','FECHAFIRMA','CODRAMO','RAMOEQUIV','CODIGOASIGNATURA','CODSECC','SECCION','FECHAINICIO','FECHAFIN','FECHAREPORTE','FECHAMEDICION','ESTADO','ESTADOACADEMICO','SITUACION','DESCRIPCIONESTADO','CONVALIDADO','NOTAFINAL','CODPESTUD'}
for path in selected:
 try:
  p=src(path,expected.get(path));h=H[path]
  if h in seen:inventory.append({'archivo':path,'sha256':h,'estado':'DUPLICADO_BYTES','alias_de':seen[h]});continue
  seen[h]=path;data=p.read_bytes()
  with zipfile.ZipFile(io.BytesIO(data)) as z:
   core=ET.fromstring(z.read('docProps/core.xml')) if 'docProps/core.xml' in z.namelist() else None
   props={k:(core.find('{http://purl.org/dc/terms/}'+k).text if core is not None and core.find('{http://purl.org/dc/terms/}'+k) is not None else None) for k in ['created','modified']}
  w=openpyxl.load_workbook(io.BytesIO(data),read_only=True,data_only=True)
  for ws in w:
   it=iter(ws.values);hh=None
   for rn in range(1,21):
    try:r=next(it)
    except StopIteration:break
    hdr=[canon(v) for v in r]
    if 'RUT' in hdr and ('CODCLI' in hdr or 'CODCLI2' in hdr or 'CODCARPR' in hdr):
     counts=collections.Counter();hh=[]
     for v in hdr:counts[v]+=1;hh.append(v if counts[v]==1 else v+'__'+str(counts[v]))
     break
   if hh is None:
    inventory.append({'archivo':path,'sha256':h,'hoja':ws.title,'estado':'SIN_CABECERA_APLICABLE','docProps':props});continue
   hr=rn;n=found=0
   for rn,r in enumerate(it,hr+1):
    n+=1;d=dict(zip(hh,r));cc=val(d.get('CODCLI') or d.get('CODCLI2'));raw=val(d.get('RUT')).upper().replace('.','').replace(' ','')
    person=owners.get(cc)
    if person:
     body,dv=person.split('-')
     if raw not in {person,body,body+dv}:alerts.append({'archivo':path,'hoja':ws.title,'fila':rn,'motivo':'CODCLI sin RUT concordante'});continue
     method='CODCLI exacto y RUT corroborado'
    else:
     matches=[pp for pp in persons if raw in {pp,pp.replace('-','')}]
     if not matches and raw in bodymap and val(d.get('DIG')).upper()==bodymap[raw].split('-')[1] and Path(path).name.startswith(('PROMEDIOSDEALUMNOS','DATOSDEALUMNOS')):matches=[bodymap[raw]]
     if len(matches)!=1:continue
     person=matches[0];method='RUT y DV exactos; sin imputar CODCLI ausente'
    z={k:val(v) for k,v in d.items() if k.split('__')[0] in keep or any(t in k for t in ['FECHACAMBIO','FECHARECHAZ','FECHAESTADO','FECHASITUACION'])}
    z.update(archivo=path,sha256=h,hoja=ws.title,fila=rn,persona=person,CODCLI=cc,metodo=method);rows.append(z);found+=1
   inventory.append({'archivo':path,'sha256':h,'hoja':ws.title,'fila_encabezado':hr,'encabezados_normalizados':hh,'filas_leidas':n,'filas_foco':found,'docProps':props,'estado':'LEIDO'})
  w.close();print(json.dumps({'archivo':p.name,'filas_foco':sum(x['archivo']==path for x in rows)}),flush=True)
 except Exception as e:errors.append({'archivo':path,'error':str(e)});print(json.dumps({'archivo':Path(path).name,'error':str(e)}),flush=True)
 dump(Q/'FILAS_HISTORICAS.json',rows);dump(O/'INVENTARIO.json',inventory);dump(O/'ERRORES.json',errors)
# Re-read annual base directly for all focal people, all periods; preserve row coordinates.
bp=R/'outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx';src(bp,expected[str(bp)])
w=openpyxl.load_workbook(bp,read_only=True,data_only=True);it=iter(w['BASE_RETENCION_MU'].values);head=next(it);mu=[]
for rn,r in enumerate(it,2):
 d=dict(zip(head,r));person=val(d.get('N_DOC'))+'-'+val(d.get('DV')).upper()
 if person in persons:
  mu.append({'persona':person,'fuente':str(bp),'hoja':'BASE_RETENCION_MU','fila':rn,**{k:val(d.get(k)) for k in ['TIPO_DOC','COD_INST','COD_SED','COD_CAR','JOR','VERSION','ANIO_INFORMADO','ANIO_ING_ORI','SEM_ING_ORI','ANIO_ING_ACT','SEM_ING_ACT','VIG']}})
w.close()
dump(Q/'MU_PERSONAS.json',mu);dump(Q/'FOCO_12.json',focus);dump(Q/'CONTEXTO_OBSERVACIONES.json',contexts);dump(Q/'ETIQUETAS.json',labels);dump(Q/'ALERTAS_IDENTIDAD.json',alerts)
dump(O/'FUENTES_HASHES.json',H);dump(O/'CONFIG.json',{'output':str(O),'privado':str(Q),'anterior':str(prev),'fecha_hora':now.isoformat()})
print(json.dumps({'salida':str(O),'privado':str(Q),'observaciones':len(focus),'personas':len(persons),'filas_historia':len(rows),'filas_mu':len(mu),'errores':len(errors),'alertas':len(alerts)}),flush=True)
