from pathlib import Path
from collections import Counter
import sqlite3,openpyxl,json,hashlib,os
P=Path.home()/'.local/share/ipss/fase_h_hito2c_20261027';O=Path(__file__).parent;p=P.parent/'fase_h_regla_intertrimestral_20261027/V24_QA_COPIA.xlsx';assert hashlib.sha256(p.read_bytes()).hexdigest()=='1e28d5955d874e7d86ec0ca87ab6a2cc478515c0dbd604f4fc86f60fa491c481';d=sqlite3.connect(P/'FOTOS_CONSTRUIDAS_V2.sqlite');made={(y,g,k):(state,q,r) for y,g,k,state,q,r in d.execute('select ano,grupo,llave,estado,q,r from foto')};w=openpyxl.load_workbook(p,read_only=True,data_only=True);c=Counter();difs=[]
for rn,row in enumerate(w['20_Foto_BBDD'].iter_rows(min_row=6,max_row=4478,values_only=True),6):
 y,g,k=row[1],row[2],row[8]
 if k is None:continue
 try:k=str(int(k))
 except (ValueError,TypeError):k=str(k).strip()
 v=made.get((y,g,k))
 if v is None:c[(y,g,'SIN_PERTENENCIA')]+=1;continue
 c[(y,g,'COMPARADAS')]+=1
 for col,i,actual in [('P',15,v[0]),('Q',16,v[1]),('R',17,v[2])]:
  if row[i]!=actual:c[(y,g,'DIF_'+col)]+=1;difs.append((rn,y,g,k,col,str(row[i]),str(actual)))
w.close();d.close();q=sqlite3.connect(P/'DIFERENCIAS_FOTO_V2.sqlite');q.execute('create table dif(fila integer,ano integer,grupo integer,llave text,campo text,v24 text,calculado text)');q.executemany('insert into dif values(?,?,?,?,?,?,?)',difs);q.commit();q.close();out=[]
for y,g in sorted({(x[0],x[1]) for x in c}):
 n=c[(y,g,'COMPARADAS')];dd={f:c[(y,g,'DIF_'+f)] for f in 'PQR'};out.append({'ano':y,'grupo':g,'comparadas':n,'campos_diferentes':dd,'max_porcentaje':100*max(dd.values())/n if n else None})
result={'campos':'P/Q/R','tabla':out,'limite_superado':any(x['max_porcentaje'] is not None and x['max_porcentaje']>1 for x in out),'detalle_privado':str(P/'DIFERENCIAS_FOTO_V2.sqlite')};(O/'PARIDAD_FOTOS_V2.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
