"""QA independiente: relee filas fuente para códigos adoptados, sin imprimir identidades."""
from pathlib import Path
import json,hashlib,re
from collections import defaultdict
import openpyxl
O=Path(__file__).parent;T=Path('/tmp/ipss_resolucion_2317_20261022');load=lambda p:json.load(open(p));r=load(T/'resultados.json');e=load(T/'evidencias.json');s=load(O/'RESULTADO.json');resolved={x[0]:x for x in r if x[14]};need=defaultdict(lambda:defaultdict(list))
for x in e:
 if x[0] in resolved:need[x[1]][x[3]].append(x)
val=lambda v:'' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip()
def key(a,b):return str(int(val(a).replace('.','')))+'-'+val(b).upper()
verified=set();hashes={}
for path,rows in need.items():
 hashes[path]=hashlib.sha256(Path(path).read_bytes()).hexdigest();w=openpyxl.load_workbook(path,read_only=True,data_only=True)
 for sheet in {x[2] for vv in rows.values() for x in vv}:
  it=iter(w[sheet].values);h=next(it)
  for rn,row in enumerate(it,2):
   if rn not in rows:continue
   d=dict(zip(h,row))
   if 'MC_CODIGO_UNICO' in d:k=key(d['MM_N_DOCUMENTO'],d['MM_DV']);code=val(d['MC_CODIGO_UNICO']);year=val(d['MC_CAT_PERIODO']).replace('MAT_','')
   else:k=key(d['N_DOC'],d['DV']);code='I162S%sC%sJ%sV%s'%tuple(val(d[n]) for n in ['COD_SED','COD_CAR','JOR','VERSION']);year=val(d['ANIO_INFORMADO'])
   for x in rows[rn]:
    if x[2]!=sheet:continue
    v=resolved[x[0]];assert (k,code,year)==(v[1],v[14],v[7]);verified.add(v[0])
 w.close()
assert len(verified)==1760==len(resolved)
pp={x[1] for x in r};blocked={x[1] for x in r if not x[14]};good={x[1] for x in r if x[14]};assert len(pp)==2317 and len(r)==4973 and len(blocked)==1838 and len(good-blocked)==479 and len(good&blocked)==77
# Privacidad de las dos hojas añadidas y ausencia de vínculos al privado.
ids={str(v) for x in r for v in [x[1],x[2],x[1].split('-')[0]] if len(str(v))>=6};p=load(O/'payload.json');assert not any(str(v) in ids for sh in p for row in sh['rows'] for v in row)
f=load(O/'FUENTES_NUEVAS.json');assert hashlib.sha256(Path(f['titulados2025']['ruta']).read_bytes()).hexdigest()==f['titulados2025']['sha256']
for path,h in f['DA_hashes'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h
q={'estado':'PASS','observaciones_fuente_releidas_y_acreditadas':len(verified),'personas_foco':len(pp),'personas_con_pendiente':len(blocked),'personas_totalmente_conciliadas_foco':len(good-blocked),'personas_parciales':len(good&blocked),'identidades_en_agregado_nuevo':0,'hashes_fuentes_adoptadas':hashes,'ninguna_equivalencia_plan_aprobada':True}
(O/'QA_INDEPENDIENTE.json').write_text(json.dumps(q,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in q.items() if k!='hashes_fuentes_adoptadas'}))
