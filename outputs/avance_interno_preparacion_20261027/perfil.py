from pathlib import Path
from collections import defaultdict,Counter
import openpyxl,json,hashlib
r=next(Path('/Users/alexi/Library/CloudStorage').glob('OneDrive-InstitutoProfesionalSanSebasti*'))
f=r/'IPSS_CONCILIACION_UMAS_SIES_BASES'; da=next(f.rglob('DATOSDEALUMNOS_12159.xlsx')); pr=next(f.rglob('PROMEDIOSDEALUMNOS_12166.xlsx')); ma=next((r/'Datos DAI (RAW) - 1.1 Datos crudos'/'1.2.1 Datos Institucionales').rglob('Listado_Planes_estudio_Sedes RE+CO.xlsx'))
def n(v):
 if v is None:return ''
 if isinstance(v,(int,float)) and v==int(v):return str(int(v))
 return str(v).strip().upper()
def sh(p):
 h=hashlib.sha256()
 with p.open('rb') as z:
  for b in iter(lambda:z.read(1048576),b''):h.update(b)
 return h.hexdigest()
def rows(p,s):
 w=openpyxl.load_workbook(p,read_only=True,data_only=True); it=w[s].values; hs=[n(v) for v in next(it)]
 for i,row in enumerate(it,2):yield i,{k:row[j] if j<len(row) else None for j,k in enumerate(hs) if k}
 w.close()
da_map=defaultdict(list)
for i,x in rows(da,'Hoja1'):
 if n(x.get('CODCLI')):da_map[n(x['CODCLI'])].append(x)
pl=defaultdict(set)
for i,x in rows(ma,'BBDD Bruta'):
 if all(n(x.get(t)) for t in ('CODCARR','CODPESTUD','CODRAMO')):pl[(n(x['CODCARR']),n(x['CODPESTUD']))].add(n(x['CODRAMO']))
by=defaultdict(lambda:{'plans':set(),'persons':set(),'status':set(),'years':set(),'nlevels':set(),'raw':0})
status=Counter();years=Counter();no_doc=0
for i,x in rows(pr,'Hoja1'):
 code=n(x.get('CODCLI'))
 if not code:continue
 obj=by[code]; obj['raw']+=1; obj['plans'].add((n(x.get('CODCARR')),n(x.get('PLAN_DE_ESTUDIO'))));obj['persons'].add((n(x.get('RUT')),n(x.get('DIG'))));obj['years'].add(n(x.get('ANO')));obj['nlevels'].add(n(x.get('NIVEL')));status[n(x.get('ESTADO'))]+=1;years[n(x.get('ANO'))]+=1
stat=Counter()
for cod,v in by.items():
 ds=da_map.get(cod,[])
 stat['expedientes']+=1
 if not ds:stat['sin_codcli_datos_alumnos']+=1;continue
 persons={x[0] for x in v['persons'] if x[0]}; rawr={n(x.get('RUT')).replace('.','').split('-')[0] for x in ds}
 if not persons&rawr:stat['codcli_sin_rut_coincidente']+=1;continue
 daok=[x for x in ds if n(x.get('RUT')).replace('.','').split('-')[0] in persons]
 for label,fields in [('cohorte',('ANOINGRESO',)),('sede',('SEDE',)),('jornada',('JORNADA',)),('carrera',('CODCARPR',))]:
  vals={tuple(n(x.get(f)) for f in fields) for x in daok}
  if len(vals)==1 and all(vals.pop()):stat[label+'_unica']+=1
  else:stat[label+'_pendiente']+=1
 if len(v['plans'])==1 and all(next(iter(v['plans']))):
  stat['plan_unico_promedios']+=1
  if next(iter(v['plans'])) in pl:stat['plan_en_listado']+=1
  else:stat['plan_sin_listado']+=1
 else:stat['varios_o_sin_plan']+=1
report={'fuentes':{p.name:{'ruta':str(p),'sha256':sh(p)} for p in (da,pr,ma)},'conteos_expedientes':dict(stat),'estados_ramos':dict(status),'anos_observados':dict(sorted(years.items())),'metodo':'CODCLI exacto y cuerpo RUT; se muestran conflictos de metadatos, sin validar DV ni completitud; plan fuente PROMEDIOS no equivale a logro o SIES; duplicados no sumados'}
print(json.dumps(report,ensure_ascii=False,indent=2))
