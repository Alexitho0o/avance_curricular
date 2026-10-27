from pathlib import Path
from collections import defaultdict,Counter
import openpyxl,json,sqlite3,hashlib
O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_h_hito2c_20261027';book=P.parent/'fase_h_regla_intertrimestral_20261027/V24_QA_COPIA.xlsx';assert hashlib.sha256(book.read_bytes()).hexdigest()=='1e28d5955d874e7d86ec0ca87ab6a2cc478515c0dbd604f4fc86f60fa491c481';db=sqlite3.connect(P/'UNIVERSO_CONSTRUIDO.sqlite');made={(y,g,k):doc for y,g,k,doc in db.execute('select ano,grupo,llave,documento from origen')};w=openpyxl.load_workbook(book,read_only=True,data_only=True);counts=Counter();detail=[]
for rn,row in enumerate(w['20_Foto_BBDD'].iter_rows(min_row=6,max_row=4478,values_only=True),6):
 y,g,doc,k=row[1],row[2],row[4],row[8]
 if k is None:counts[(y,g,'SIN_LLAVE_V24')]+=1;continue
 try:k=str(int(k))
 except (ValueError,TypeError):k=str(k).strip()
 prev=made.get((y,g,k));counts[(y,g,'COMPARADAS')]+=1
 def norm(v):return '' if v is None else str(v).upper().strip().replace('.','').replace(' ','')
 if prev is None or norm(prev)!=norm(doc):counts[(y,g,'DIFERENTES')]+=1;detail.append((rn,y,g,k,norm(prev),norm(doc)))
w.close();out=P/'DIFERENCIAS_DOCUMENTOS.sqlite';assert not out.exists();q=sqlite3.connect(out);q.execute('create table diferencias(fila integer,ano integer,grupo integer,llave text,construido text,v24 text)');q.executemany('insert into diferencias values(?,?,?,?,?,?)',detail);q.commit();q.close();groups=[]
for y,g in sorted({(a,b) for a,b,c in counts}):
 n=counts[(y,g,'COMPARADAS')];d=counts[(y,g,'DIFERENTES')];groups.append({'ano':y,'grupo':g,'comparadas':n,'diferentes':d,'porcentaje':100*d/n if n else None,'sin_llave_v24':counts[(y,g,'SIN_LLAVE_V24')]})
res={'campo':'documento original E (texto y DV)','tabla':groups,'umbral_superado':any(x['porcentaje'] is not None and x['porcentaje']>1 for x in groups),'limite':'Solo documento, no paridad de todos los campos. Selección de un registro ante duplicidad aún no está respaldada.'};(O/'PARIDAD_DOCUMENTOS.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps(res,ensure_ascii=False))
