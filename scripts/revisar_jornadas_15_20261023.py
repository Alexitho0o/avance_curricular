"""Relee snapshots históricos para 15 contextos; no adjudica códigos adicionales."""
from pathlib import Path
import json,sys,collections,datetime,os,unicodedata,zipfile
import openpyxl
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import sha256,rut_normalizado
O=sorted((R/'outputs').glob('cierre_14_jornadas_15_*/CONFIG.json'))[-1].parent;config=json.loads((O/'CONFIG.json').read_text());P=Path(config['privado']);old=json.loads((R/'data/diccionario_sies_seguimiento/v1_20261023/descriptor.json').read_text());prev=R/'outputs/revision_35_informatica_20261023_130829';pm=json.loads((prev/'MANIFEST.json').read_text());pr=Path(pm['privado']);rs=json.loads((pr/'REVISION_OBSERVACIONES.json').read_text());focus=[x for x in rs if x['resultado_revision']=='E_CAMBIO_JORNADA_SIN_PERIODO'];assert len(focus)==15
owners={x['CODCLI']:x['persona'] for x in focus};labels={x['persona']:x['caso'] for x in focus};people=set(labels)
def dump(p,x):
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
 if p.is_relative_to(P):os.chmod(p,0o600)
def val(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
def norm(x):
 try:return rut_normalizado(x)
 except (ValueError,TypeError):return None
sources={p:h for p,h in old['entradas_sha256'].items() if Path(p).name.startswith('DATOSDEALUMNOS') and p not in pm['fuentes']}
# Gobernados como fotografías de cierre; no asumir día por nombre.
photo=json.loads((R/'procesos/retencion_intermedia_t2_t3/MANIFEST_RETENCION_FOTO_INTERTRIMESTRAL_20261022.json').read_text())
for x in photo['fuentes']:
 if x.get('sha256') and 'Corte T' in x['rol']:sources[x['ruta']]=x['sha256']
files=[];inventory=[];seen=set();H={};oldrows=json.loads((pr/'FILAS_RELEIDAS.json').read_text());alerts=[]
for path,expected in sources.items():
 if expected in seen:continue
 p=Path(path)
 if not p.exists():
  # Misma carpeta/cierre y normalización Unicode, sin seleccionar por fecha.
  candidates=[f for base in [p.parent,p.parent/'cierre',R/'procesos/retencion_intermedia_t2_t3'] if base.exists() for f in base.rglob('*.xlsx') if unicodedata.normalize('NFC',f.name)==unicodedata.normalize('NFC',p.name)]
  matches=[f for f in candidates if sha256(f)==expected]
  if matches:p=matches[0]
 try:
  h=sha256(p);assert h==expected;H[str(p)]=h;seen.add(h);w=openpyxl.load_workbook(p,read_only=True,data_only=True)
  for ws in w:
   it=iter(ws.values);header=None;hr=0
   for rn,row in enumerate(it,1):
    hh=[val(x).upper() for x in row]
    if 'CODCLI' in hh and ('RUT' in hh or 'RUT ALUMNO' in hh):header=hh;hr=rn;break
    if rn>=10:break
   if header is None:
    inventory.append({'archivo':str(p),'hoja':ws.title,'estado':'SIN_LLAVE_CODCLI_RUT_EN_10_FILAS','created':str(w.properties.created),'modified':str(w.properties.modified),'sha256':h});continue
   n=0;nc=0
   for rn,row in enumerate(it,hr+1):
    d=dict(zip(header,row));cc=val(d.get('CODCLI'));raw=val(d.get('RUT',d.get('RUT ALUMNO')));dv=val(d.get('DIG',d.get('DV')));person=norm(raw if '-' in raw else raw+'-'+dv)
    if cc in owners and person is None and raw.replace('.','').replace(' ','')==owners[cc].split('-')[0]:person=owners[cc]
    if person not in people and cc not in owners:continue
    if cc in owners and person!=owners[cc]:alerts.append({'fuente':str(p),'hoja':ws.title,'fila':rn,'motivo':'identidad no corroborada'});continue
    keep=['CODCLI','RUT','DIG','DV','CODCARPR','CODCARR','CODCARRERA','CODPESTUD','PLAN_DE_ESTUDIO','PLAN_ESTUDIOS','JORNADA','SEDE','ANOINGRESO','PERIODOINGRESO','ANOMATRICULA','PERIODOMATRICULA','FECHAMATRICULA','FECHAFIRMA','ESTADOACADEMICO','ESTADO_ACADEMICO','SITUACION','ANO','PERIODO']
    z={k:val(d[k]) for k in keep if k in d};z.update(persona=person,caso=labels[person],fuente=str(p),hoja=ws.title,fila=rn,sha256=h,coincide_codcli=cc in owners);files.append(z);n+=1;nc+=cc in owners
   inventory.append({'archivo':str(p),'hoja':ws.title,'estado':'LEIDO','encabezados':header,'filas_foco_persona':n,'filas_codcli_exacto':nc,'created':str(w.properties.created),'modified':str(w.properties.modified),'sha256':h,'advertencia_fechas':'Metadatos técnicos no acreditan corte ni fecha efectiva de cambio'})
  w.close();print(p.name,'leído',flush=True)
 except OSError as e:inventory.append({'archivo':str(p),'estado':'NO_LEIDO','error':str(e)})
rows=[r for r in oldrows if r['persona'] in people]+files
dump(P/'RESPALDOS_JORNADA_RELEIDOS.json',files);dump(P/'JORNADAS_15_CONTEXTO_COMPLETO.json',rows);dump(P/'ALERTAS_IDENTIDAD_HISTORICO.json',alerts);dump(O/'INVENTARIO_HISTORICO_JORNADA.json',inventory);dump(O/'FUENTES_HISTORICO_HASHES.json',H)
print(json.dumps({'nuevas_filas_foco':len(files),'fuentes_hash':len(H),'alertas':len(alerts),'no_leidas':sum(x['estado']=='NO_LEIDO' for x in inventory),'output':str(O)},ensure_ascii=False))
