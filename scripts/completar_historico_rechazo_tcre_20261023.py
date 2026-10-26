"""Completa hojas sin CODCLI y cierra cronología sin modificar adjudicaciones."""
import collections,datetime,hashlib,io,json,re,subprocess,sys,unicodedata,zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo
import openpyxl
O=Path(sys.argv[1]);R=O.parents[1]
load=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
def val(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
def canon(x):return re.sub('[^A-Z0-9]','',unicodedata.normalize('NFKD',val(x).upper()).encode('ascii','ignore').decode())
def date(s):
 for fmt in ['%Y-%m-%d %H:%M:%S','%Y-%m-%d','%d-%m-%Y','%d-%m-%y','%d/%m/%Y']:
  try:return datetime.datetime.strptime(s,fmt).date().isoformat()
  except ValueError:pass
 return None
c=load(O/'CONFIG.json');Q=Path(c['privado']);H=load(O/'FUENTES_HASHES.json');inv=load(O/'INVENTARIO.json');rows=load(Q/'FILAS_HISTORICAS_PRIVADAS.json')
pm=load(Path(c['anterior'])/'MANIFEST.json');third=load(Path(pm['privado'])/'REVISION_HOMOLOGACIONES.json')['observacion'];person=third['persona'];body,dv=person.split('-')
extra=[];extra_inv=[]
groups=collections.defaultdict(list)
for x in inv:groups[x['archivo']].append(x)
for path,items in groups.items():
 data=Path(path).read_bytes();assert hashlib.sha256(data).hexdigest()==H[path]
 with zipfile.ZipFile(io.BytesIO(data)) as zz:
  core=ET.fromstring(zz.read('docProps/core.xml')) if 'docProps/core.xml' in zz.namelist() else None
  props={k:(core.find('{http://purl.org/dc/terms/}'+k).text if core is not None and core.find('{http://purl.org/dc/terms/}'+k) is not None else None) for k in ['created','modified']}
  props['limite']='Valores explícitos de core.xml. Ausencia=null; no representan fecha efectiva de corte, matrícula o rechazo.'
 for x in items:
  if x.get('docProps') is not None:x['docProps']=props
 missing=[x for x in items if x['estado'].startswith('SIN_CABECERA') and 'DATOSDEALUMNOS' in Path(path).name]
 if not missing:continue
 w=openpyxl.load_workbook(io.BytesIO(data),read_only=True,data_only=True)
 for x in missing:
  it=iter(w[x['hoja']].values);hh=None
  for rn in range(1,21):
   try:r=next(it)
   except StopIteration:break
   hdr=[canon(v) for v in r]
   if 'RUT' in hdr and 'CODCARPR' in hdr and 'ESTADOACADEMICO' in hdr:
    counts=collections.Counter();hh=[]
    for v in hdr:counts[v]+=1;hh.append(v if counts[v]==1 else v+'__'+str(counts[v]))
    break
  if hh is None:continue
  hr=rn;n=found=0
  for rn,r in enumerate(it,hr+1):
   n+=1;d=dict(zip(hh,r));rut=val(d.get('RUT')).upper().replace('.','').replace(' ','')
   if rut not in [person,body+dv]:continue
   keep=['CODCLI','CODCLI2','CODCARPR','ANOMATRICULA','PERIODOMATRICULA','ANOINGRESO','PERIODOINGRESO','FECHAMATRICULA','JORNADA','ESTADOACADEMICO','SITUACION','FECHAFIRMA','SEDE']
   z={k:val(d.get(k)) for k in keep if k in d};z.update(archivo=path,sha256=H[path],hoja=x['hoja'],fila=rn,persona=person,metodo='RUT completo exacto; sin imputar CODCLI ausente')
   extra.append(z);found+=1
  extra_inv.append({'archivo':path,'sha256':H[path],'hoja':x['hoja'],'fila_encabezado':hr,'encabezados_normalizados':hh,'filas_leidas':n,'filas_persona':found,'estado':'LEIDO_RUT_COMPLETO','docProps':props})
 w.close()
rows+=extra;dump(O/'INVENTARIO.json',inv);dump(O/'INVENTARIO_COMPLEMENTARIO.json',extra_inv);dump(Q/'FILAS_COMPLEMENTARIAS_SIN_CODCLI.json',extra);dump(Q/'FILAS_HISTORICAS_CONSOLIDADAS.json',rows)
# Normalize dates preserving literals; report repeated events only once.
timeline=[]
for x in rows:
 if x.get('CODIGOPLANESTUDIO')=='TTMREOL20231':
  key='FECHAREPORTE' if x.get('FECHAREPORTE') else 'FECHAMEDICION'
  d=date(x.get(key,''))
  if d:timeline.append({'fecha_observada':d,'campo_fecha':key,'literal':x[key],'plan':'TTMREOL20231','periodo':x.get('PERIODO'),'estado':x.get('ESTADOACADEMICO',''),'asignatura':x.get('CODIGOASIGNATURA'),'archivo':x['archivo'],'hoja':x['hoja'],'fila':x['fila'],'limite':'Fecha de reporte/medición, no fecha de rechazo.'})
timeline.sort(key=lambda x:x['fecha_observada'])
reject=[x for x in rows if x.get('SITUACION')=='9 - RECHAZO ACTUALIZACION DE PLAN 2024' and x.get('CODCARPR')=='TCRE']
assert reject and timeline and all(x['persona']==person for x in rows)
source_props={x['archivo']:x['docProps'] for x in inv if x.get('docProps')}
reject_meta=sorted([{'archivo':p,'fecha_guardado':source_props[p]['modified'],'limite':'Metadato del libro, no fecha del rechazo ni corte certificado.'} for p in {x['archivo'] for x in reject} if source_props.get(p,{}).get('modified')],key=lambda x:x['fecha_guardado'])
pr=[x for x in rows if x.get('PLANDEESTUDIO')=='TTMREOL20231' and x.get('DESCRIPCIONESTADO')=='APROBADO']
pr_summary=[]
for path in sorted({x['archivo'] for x in pr}):
 a=[x for x in pr if x['archivo']==path]
 for year in ['2024','2025']:
  yy=[x for x in a if x.get('ANO')==year]
  if yy:pr_summary.append({'archivo':path,'ano':year,'filas':len(yy),'asignaturas_distintas':len({(x['CODRAMO'],x['PERIODO']) for x in yy}),'periodos':sorted({x['PERIODO'] for x in yy}),'regimenes':sorted({x.get('REGIMEN','') for x in yy})})
hom=[x for x in rows if x.get('PLANDEESTUDIO')=='TCRE20241']
assert hom and all(x.get('DESCRIPCIONESTADO')=='HOMOLOGADO' and x.get('CONVALIDADO')=='S' for x in hom)
hom_summary=[{'archivo':path,'filas':sum(x['archivo']==path for x in hom),'ano_periodo':sorted({(x['ANO'],x['PERIODO']) for x in hom if x['archivo']==path})} for path in sorted({x['archivo'] for x in hom})]
dump(Q/'CRONOLOGIA_PLAN_ANTERIOR.json',timeline);dump(Q/'RECHAZO_RESPALDOS.json',reject)
dump(O/'CONTINUIDAD_POR_RESPALDO.json',pr_summary);dump(O/'HOMOLOGACIONES_POR_RESPALDO.json',hom_summary);dump(O/'METADATOS_RESPALDOS_RECHAZO.json',reject_meta)
summary={'clasificacion':'B observaciones; C cruces; E fecha y atribución documental',
 'fuentes_unicas':len({x['sha256'] for x in inv}),'hojas_granulares_leidas':sum(x['estado']=='LEIDO' for x in inv)+len(extra_inv),
 'filas_persona_con_repeticiones':len(rows),'fechas_reporte_plan_anterior':sorted({x['fecha_observada'] for x in timeline}),
 'plan_anterior_observado_desde':timeline[0]['fecha_observada'],'plan_anterior_ultimo_reporte_fechado':timeline[-1]['fecha_observada'],
 'fuentes_con_rechazo':len({x['sha256'] for x in reject}),'fecha_efectiva_rechazo':None,
 'fecha_corte_rechazo_certificada':None,'primera_fecha_guardado_explicita_en_fuentes_con_rechazo':reject_meta[0]['fecha_guardado'] if reject_meta else None,
 'continuidad_plan_anterior_2024_2025':True,'TCRE_observado_solo_homologaciones':True,
 'tercera_observacion':'PENDIENTE_VERSION_INTERNA_Y_ATRIBUCION_DOCUMENTAL',
 'nuevas_adjudicaciones':0,'pendientes_internos':{'observaciones':3088,'personas':1750},
 'pendientes_documentales':{'observaciones':3213,'personas':1838},'universo':[5901,6622,24774]}
dump(O/'RESULTADOS.json',summary)
print(json.dumps({'salida':str(O),'resultado':summary,'aprobaciones':pr_summary,'homologaciones':hom_summary},ensure_ascii=False),flush=True)
