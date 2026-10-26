"""Relee evidencia de 35 contextos; no adopta códigos ni modifica el diccionario."""
from pathlib import Path
import json,sys,collections,datetime,subprocess,os,re
import openpyxl
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256,rut_normalizado
stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S');O=R/'outputs'/('revision_35_informatica_'+stamp);P=Path.home()/'.local/share/ipss'/O.name
assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
O.mkdir();P.mkdir(mode=0o700);os.chmod(P,0o700);H={}
def dump(p,x):
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str));
 if p.is_relative_to(P):os.chmod(p,0o600)
def load(p,expected=None):
 p=Path(p);h=sha256(p);assert expected is None or h==expected;H[str(p)]=h;return json.loads(p.read_text())
def val(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
def norm(x):
 try:return rut_normalizado(x)
 except ValueError:return None
A=R/'outputs/aplicacion_diccionario_intertrimestral_20261023_125556';am=load(A/'MANIFEST_APLICACION.json');ap=Path(am['privado']);allr=load(ap/'CONSULTAS_EXACTAS.json',am['auditoria_privada_hashes']['CONSULTAS_EXACTAS.json']);targets=[x for x in allr if x['estado']=='E Pendiente' and x['familia'].startswith('I162S2C1J')];assert len(targets)==35
s=DiccionarioSiesSeguimiento();dbrows=[json.loads(x[0]) for x in s.db.execute('select payload from observaciones')];people={x['persona'] for x in targets};assert len(people)==12
labels={};groups=collections.defaultdict(list)
for x in targets:groups[x['persona'],x['codcli']].append(x)
for i,key in enumerate(groups,1):labels[key[0]]='INF35-%02d'%i
owners=collections.defaultdict(set)
for r in dbrows:owners[r['CODCLI']].add(r['persona'])
known={cc:next(iter(ps)) for cc,ps in owners.items() if len(ps)==1 and next(iter(ps)) in people}
assert all(owners[x['codcli']]=={x['persona']} for x in targets)
for x in targets:
 q=s.consultar(persona=x['persona'],codcli=x['codcli'],plan=x['plan'],anio=x['anio'],periodo=x['periodo_nativo'],carrera=x['carrera_umas'],sede=x['evidencia']['sede_dimension'],jornada=x['evidencia']['jornada_sies']);assert q['estado']=='EXCEPCION'
dump(P/'SELECCION_35.json',targets);dump(P/'OBSERVACIONES_12_PERSONAS.json',[x for x in dbrows if x['persona'] in people]);dump(P/'CASOS.json',[{'caso':labels[k[0]],'persona':k[0],'CODCLI':k[1],'n':len(v)} for k,v in groups.items()])
# Sources already governed in previous analyses; same-content copies are read once.
previous=load(R/'outputs/trayectorias_374_20261023_072401/MANIFEST.json');t3=load(R/'outputs/revision_t3_2024_f02_20261023_082535/FUENTES_HASHES.json');hs={}
for p,h in previous['fuentes'].items():
 if Path(p).name in ['DATOSDEALUMNOS_12159.xlsx','DATOSDEALUMNOS_11248.xlsx','DATOSDEALUMNOS_11998.xlsx','PROMEDIOSDEALUMNOS_12166.xlsx','PROMEDIOSDEALUMNOS_7804.xlsx']:hs[p]=h
for p,h in t3.items():
 if Path(p).name.startswith(('PROMEDIOSDEALUMNOS','PRUEBA CUMPLIMIENTO')):hs[p]=h
prof=load(Path.home()/'.local/share/ipss/cambios_plan_12_y_4_20261023_080207/PERFIL_FUENTES_ADICIONALES.json')
for x in prof:
 if Path(x['path']).name in ['DATOSDEALUMNOS ORIGEN DE LOS DATOS2025.xlsx','CUMPLIMIENTO INGRESO CALIFICACIONES.xlsx','Cumplimiento Ingreso de Notas.xlsx']:hs[x['path']]=x['sha256']
# MU and identity bridge from the applied workbook manifest.
for p,h in am['fuentes'].items():
 if Path(p).name.startswith('BASE_RETENCION_MATRICULA') or Path(p).name=='IPSS_Procesamiento.xlsx':hs[p]=h
rows=[];inventory=[];readhash=set();bad=[]
for path,expected in hs.items():
 if expected in readhash:continue
 p=Path(path)
 try:
  h=sha256(p);assert h==expected;H[path]=h;readhash.add(h)
  w=openpyxl.load_workbook(p,read_only=True,data_only=True)
  for ws in w:
   it=iter(ws.values);heads=None;hr=0
   for rn,rr in enumerate(it,1):
    hh=[val(v).upper() for v in rr]
    if ('CODCLI' in hh and 'RUT' in hh) or ('N_DOC' in hh and 'ANIO_INFORMADO' in hh):heads=hh;hr=rn;break
    if rn>=5:break
   if heads is None:continue
   names=[];cc=collections.Counter()
   for k in heads:cc[k]+=1;names.append(k if cc[k]==1 else k+'__'+str(cc[k]))
   count=found=0
   for rn,rr in enumerate(it,hr+1):
    count+=1;d=dict(zip(names,rr));cod=val(d.get('CODCLI'));raw=val(d.get('RUT'));dv=val(d.get('DIG',d.get('DV')));person=norm(raw if '-' in raw else raw+'-'+dv)
    if person not in people and cod in known and raw.replace('.','').replace(' ','')==known[cod].split('-')[0]:person=known[cod]
    if 'ANIO_INFORMADO' in d:
     person=norm(val(d.get('N_DOC'))+'-'+val(d.get('DV')))
     if person not in people:
      matches=[x for x in targets if x['anio']==int(d.get('ANIO_INFORMADO') or 0) and x['tipo_doc']==val(d.get('TIPO_DOC')) and val(x['documento_original']).rstrip('-')==val(d.get('N_DOC'))]
      if matches:assert len({x['persona'] for x in matches})==1;person=matches[0]['persona']
    if person not in people:continue
    if cod in known and known[cod]!=person:bad.append({'fuente':path,'hoja':ws.title,'fila':rn,'motivo':'CODCLI y persona discordantes'});continue
    fields=['CODCLI','RUT','DIG','N_DOC','DV','TIPO_DOC','CODCARPR','CODCARR','CODCARRERA_ALUMNO','SEDE','JORNADA','REGIMEN','PLAN_DE_ESTUDIO','CODIGO_PLAN_ESTUDIO','CODPESTUD','PLAN_ESTUDIOS','ANO','PERIODO','PERIODO__2','ANOMATRICULA','PERIODOMATRICULA','ANOINGRESO','PERIODOINGRESO','FECHAMATRICULA','FECHAFIRMA','FECHAINICIO','FECHAFIN','FECHA REPORTE','FECHA MEDICION','ESTADO','ESTADO_ACADEMICO','ESTADOACADEMICO','SITUACION','CODRAMO','RAMOEQUIV','CODIGO_ASIGNATURA','CODSECC','SECCION','NOTA_FINAL','DESCRIPCION_ESTADO','CONVALIDADO','NIVEL','ANIO_INFORMADO','COD_SED','COD_CAR','JOR','VERSION','ANIO_ING_ORI','SEM_ING_ORI','ANIO_ING_ACT','SEM_ING_ACT','VIG']
    z={k:val(d[k]) for k in fields if k in d};z.update(persona=person,caso=labels[person],fuente=path,hoja=ws.title,fila=rn,sha256=h);rows.append(z);found+=1
   inventory.append({'fuente':path,'sha256':h,'hoja':ws.title,'encabezados':names,'fila_encabezado':hr,'filas_leidas':count,'filas_foco':found})
  w.close();print(p.name,'leído',flush=True)
 except OSError as e:inventory.append({'fuente':path,'estado':'BLOQUEADO_LECTURA','error':str(e)})
assert not bad
dump(P/'FILAS_RELEIDAS.json',rows);dump(O/'INVENTARIO.json',inventory);dump(O/'FUENTES_HASHES.json',H);dump(O/'CONTROL.json',{'seleccion':35,'personas':12,'expedientes':12,'filas_recuperadas':len(rows),'rechazos_identidad':len(bad),'fuentes_con_lectura':len(readhash),'sin_adopcion':True})
dump(O/'CONFIG.json',{'output':str(O),'privado':str(P),'anterior':str(A)})
s.close();print(json.dumps({'output':str(O),'privado':str(P),'filas':len(rows)},ensure_ascii=False))
