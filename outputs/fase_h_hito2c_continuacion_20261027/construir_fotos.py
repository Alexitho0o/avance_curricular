"""Foto hacia adelante; entrada privada derivada del padrón previo y fuentes congeladas."""
from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib,sqlite3,openpyxl,glob,unicodedata,os
R=Path(__file__).resolve().parents[2];O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_h_hito2c_20261027';src=P/'UNIVERSO_CONSTRUIDO.sqlite';out=P/'FOTOS_CONSTRUIDAS.sqlite';assert not out.exists();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rp=R/'data/reglas_negocio/mu2027/versiones/20261021_v1/reglas.json';assert sha(rp)=='5ffa47d537f3ae81cd470ae9c1c9ed75cafb4adb4eb38e980d45fd21a272714e';rules=json.loads(rp.read_text())['equivalencias'];normalize=lambda v:'' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip().upper();pairs={(normalize(x['estado_umas']),normalize(x['situacion_umas'])):normalize(x['resultado']) for x in rules};assert len(pairs)==32
pri={'1':1,'NO APLICA':2,'PENDIENTE':3,'0':4};label={1:'VIG 1',2:'NO APLICA',3:'PENDIENTE',4:'VIG 0',5:'SIN REGLA',6:'Sin foto'}
def body(x):
 s=normalize(x).replace('.','').replace(' ','').split('-')[0];return str(int(s)) if s.isdigit() else s
xs=[Path(p) for p in glob.glob('/Users/alexi/Downloads/cierre/*.xlsx') if unicodedata.normalize('NFC',Path(p).name)=='Matrícula T3_2025 2.xlsx'];assert len(xs)==1
p25=xs[0];p26=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/03_UMAS_DATOSDEALUMNOS/DATOSDEALUMNOS_12159.xlsx');sources=[(2025,p25,'T3_2025','68a1cd54ee48c1e6a679c1dbb3999e12d491543e9425e81f3d0508fefdc8d6cc'),(2026,p26,'Hoja1','a0638483420324bcb2bba8bcbea426ca0a2be6162d1c8879569b507f409bdfc9')];photos=defaultdict(list)
for year,p,sh,h in sources:
 assert sha(p)==h;w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=w[sh].iter_rows(values_only=True);hd={normalize(z):i for i,z in enumerate(next(it)) if z is not None}
 for rn,row in enumerate(it,2):
  def get(k):return row[hd[k]] if k in hd and hd[k]<len(row) else None
  key=body(get('RUT'));ing=normalize(get('ANOINGRESO'));pair=(normalize(get('ESTADOACADEMICO')),normalize(get('SITUACION')));value=pairs.get(pair);priority=pri.get(value,5)
  if key and ing.isdigit():photos[(year,key,ing)].append((priority,rn,pair))
 w.close();assert sha(p)==h
orig=sqlite3.connect(src);rr=orig.execute('select ano,grupo,llave,documento,origen,hoja,fila,carrera,payload from origen order by ano,grupo,fila').fetchall();arr={}
for path,sh in {(r[4],r[5]) for r in rr if r[1]==3}:
 w=openpyxl.load_workbook(path,read_only=True,data_only=True);it=w[sh].iter_rows(values_only=True);hd={normalize(v):i for i,v in enumerate(next(it)) if v is not None};idx=hd['ANOINGRESO'];arr[(path,sh)]={rn:normalize(row[idx]) for rn,row in enumerate(it,2)};w.close()
os.umask(0o077);db=sqlite3.connect(out);db.execute('create table foto(ano integer,grupo integer,llave text,ingreso text,prioridad integer,estado text,q integer,r integer,fuentes text,primary key(ano,grupo,llave))');stats=Counter()
for year,group,key,doc,path,sh,rn,car,payload in rr:
 ing=arr[(path,sh)][rn] if group==3 else str(year);entries=photos.get((year,key,ing),[]) if year in (2025,2026) else [];priority=min([x[0] for x in entries],default=6);state=label[priority];q=int(priority==1);r=int(priority not in (2,3,6));stats[(year,group,state)]+=1;db.execute('insert into foto values(?,?,?,?,?,?,?,?,?)',(year,group,key,ing,priority,state,q,r,json.dumps(entries,ensure_ascii=False)))
db.commit();db.close();orig.close();res={'observaciones':len(rr),'por_estado':[{'ano':k[0],'grupo':k[1],'estado':k[2],'n':v} for k,v in sorted(stats.items())],'fuentes':[{'ruta':str(p),'hoja':sh,'sha256':h} for _,p,sh,h in sources],'reglas_sha256':sha(rp),'salida_privada':{'ruta':str(out),'sha256':sha(out)},'limites':['Padrón preliminar contiene 5 personas adicionales de 2026.','La selección entre matrículas con un mismo RUT y prioridad conserva alternativas; no adjudica CODCLI.','Situaciones no previstas se clasifican SIN REGLA.','La ausencia en foto no acredita deserción.']};(O/'FOTOS_CONSTRUIDAS.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'observaciones':len(rr),'estados':res['por_estado']},ensure_ascii=False))
