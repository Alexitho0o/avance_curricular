from pathlib import Path
from collections import defaultdict
import sqlite3,openpyxl,json,hashlib
O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_h_hito2c_20261027';db=sqlite3.connect(P/'FOTOS_CONSTRUIDAS_V2.sqlite');data=defaultdict(list)
for y,g,k,state,q,r in db.execute('select ano,grupo,llave,estado,q,r from foto order by ano,grupo,rowid'):data[(y,g)].append((k,state,q,r))
p=P.parent/'fase_h_regla_intertrimestral_20261027/V24_QA_COPIA.xlsx';assert hashlib.sha256(p.read_bytes()).hexdigest()=='1e28d5955d874e7d86ec0ca87ab6a2cc478515c0dbd604f4fc86f60fa491c481';w=openpyxl.load_workbook(p,read_only=True,data_only=True);s=w['18_Foto_Intertrimestral'];items=[]
for row,year,group in [(8,2025,1),(9,2025,2),(10,2025,None),(11,2026,1),(12,2026,2),(13,2026,3),(14,2026,None)]:
 if group:rr=data[(year,group)]
 else:
  seen=set();rr=[]
  for g in [1,2,3]:
   for v in data[(year,g)]:
    if v[0] not in seen:seen.add(v[0]);rr.append(v)
 n=sum(r[2] for r in rr);den=sum(r[3] for r in rr);d=len(rr);result={'D':d,'G':n,'H':n/den if den else '—'};diff=[]
 for col,v in result.items():
  z=s[f'{col}{row}'].value
  if not(abs(z-v)<1e-10 if isinstance(v,float) and isinstance(z,(int,float)) else z==v):diff.append({'celda':col+str(row),'v24':z,'construido':v,'diferencia':v-z})
 items.append({'fila':row,'numerador':n,'denominador':den,'poblacion':d,'diferencias':diff})
w.close();db.close();res={'filas':items,'limitacion':'Solo D/G/H institucional de 2025 y 2026; no replica T2, sector ni tipo.','clasificacion':'C/E; padrón construido T1-2026 incluye cinco duplicados ausentes de V24.'};(O/'PARIDAD_AGREGADA_FOTOS_V2.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps(res,ensure_ascii=False))
