"""Construcción hacia adelante de universos, previa a leer V24."""
from pathlib import Path
from collections import Counter
import json,hashlib,glob,unicodedata,openpyxl,sqlite3,os,re
O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_h_hito2c_20261027';os.umask(0o077);P.mkdir(parents=True,exist_ok=True,mode=0o700);target=P/'UNIVERSO_CONSTRUIDO.sqlite';assert not target.exists()
def find(n):
 xs=[Path(p) for p in glob.glob('/Users/alexi/Downloads/cierre/*.xlsx') if unicodedata.normalize('NFC',Path(p).name)==n];assert len(xs)==1;return xs[0]
maqueta=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/0 BASES DE DATOS/RETENCION/RETENCION_IPSS_FINAL_REVISADO_20261005.xlsx');sources={'maqueta':(maqueta,'5b64030011ad64f742a95ad72a91cc326ad918afaea46ea989496d2e8c44f899'),'t2_2025':(find('Matrícula T2_2025 2.xlsx'),'ed5de007202df0780bb3396ad88307f4096d7c8b729005486a20d1123096d5b3'),'t2_2026':(find('Matrícula T_2_13_07_2026.xlsx'),'7926a9cabcc67ed19abb50459132fd74ebb323bff9f5cb53e9116378c21a6769'),'t3_2026':(find('Matrícula_T3_02_10_2026.xlsx'),'de4e73ee7d27779cdc531c6816f745d412e1021cbd61e4fceb8ab0459cbda4ae')};sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in sources.values():assert sha(p)==h

def val(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip().upper()
def body(x):
 s=val(x).replace('.','').replace(' ','').split('-')[0];return str(int(s)) if s.isdigit() else s

db=sqlite3.connect(target);db.execute('create table origen(ano integer,grupo integer,llave text,documento text,origen text,hoja text,fila integer, carrera text, payload text, primary key(ano,grupo,llave))');counts=Counter();duplicates=Counter()
def add(ano,grupo,doc,path,sh,rn,car,payload):
 key=body(doc)
 if not key:counts['sin_llave']+=1;return
 try:db.execute('insert into origen values(?,?,?,?,?,?,?,?,?)',(ano,grupo,key,val(doc),str(path),sh,rn,val(car),json.dumps(payload,ensure_ascii=False)));counts[(ano,grupo)]+=1
 except sqlite3.IntegrityError:duplicates[(ano,grupo)]+=1
w=openpyxl.load_workbook(maqueta,read_only=True,data_only=True);s=w['9_Base_Analitica_Detalle']
for rn,r in enumerate(s.iter_rows(min_row=7,values_only=True),7):
 if r[1] in (2024,2025):
  doc=val(r[7])+('-'+val(r[8]) if val(r[8]) else '');add(r[1],1,doc,maqueta,s.title,rn,r[2],{'tipo_doc':val(r[6]),'codigo_sies':val(r[23])})
s=w['11_BASE_RETENCION_MU_RAW'];it=s.iter_rows(min_row=4,values_only=True);hd={val(x):i for i,x in enumerate(next(it)) if x is not None}
for rn,r in enumerate(it,5):
 def get(k):return r[hd[k]] if k in hd else None
 if val(get('ANIO_INFORMADO'))=='2026' and val(get('ANIO_ING_ORI'))=='2026' and val(get('SEM_ING_ORI'))=='1' and val(get('VIG'))=='1':
  doc=val(get('N_DOC'))+('-'+val(get('DV')) if val(get('DV')) else '');add(2026,1,doc,maqueta,s.title,rn,get('COD_CAR'),{'tipo_doc':val(get('TIPO_DOC'))})
w.close()
for key,year,group,sh in [('t2_2025',2025,2,'Hoja1'),('t2_2026',2026,2,'Hoja1'),('t3_2026',2026,3,'Base')]:
 path=sources[key][0];w=openpyxl.load_workbook(path,read_only=True,data_only=True);it=w[sh].iter_rows(values_only=True);hd={val(x):i for i,x in enumerate(next(it)) if x is not None}
 for rn,r in enumerate(it,2):
  def get(k):return r[hd[k]] if k in hd and hd[k]<len(r) else None
  add(year,group,get('RUT'),path,sh,rn,get('CODCARPR'),{'codcli':val(get('CODCLI')),'nombre_carrera':val(get('NOMBRE_L'))})
 w.close()
db.commit();db.close();result={'conteos_por_grupo':[{'ano':k[0],'grupo':k[1],'personas':v,'duplicados_llave_corporal':duplicates[k]} for k,v in sorted(counts.items()) if isinstance(k,tuple)],'sin_llave':counts['sin_llave'],'fuentes':{k:{'ruta':str(p),'sha256':h} for k,(p,h) in sources.items()},'salida_privada':{'ruta':str(target),'sha256':sha(target)},'limites':['La llave corporal RUT se reproduce como hipótesis técnica; no demuestra identidad de documentos P ni resuelve colisiones DV.','Selección de planes, periodos y categorías reproduce la interpretación preliminar y requiere control de membresía.','Todavía no se calculan estados, fotos ni denominadores de tasas.']};(O/'UNIVERSO_AGREGADO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result['conteos_por_grupo'],ensure_ascii=False))
