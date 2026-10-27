from pathlib import Path
from collections import defaultdict
import openpyxl,json,sqlite3,hashlib,os
O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_h_hito2c_20261027';book=P.parent/'fase_h_regla_intertrimestral_20261027/V24_QA_COPIA.xlsx';assert hashlib.sha256(book.read_bytes()).hexdigest()=='1e28d5955d874e7d86ec0ca87ab6a2cc478515c0dbd604f4fc86f60fa491c481';db=sqlite3.connect(P/'UNIVERSO_CONSTRUIDO.sqlite');groups=defaultdict(set)
for y,g,k in db.execute('select ano,grupo,llave from origen'):groups[(y,g)].add(k)
w=openpyxl.load_workbook(book,read_only=True,data_only=True);v=defaultdict(set)
for row in w['20_Foto_BBDD'].iter_rows(min_row=6,max_row=4478,values_only=True):
 y,g,k=row[1],row[2],row[8]
 if k is not None:
  try:k=str(int(k))
  except (ValueError,TypeError):k=str(k).strip()
  v[(y,g)].add(k)
w.close();result=[];changes=[]
for group in sorted(set(v)|set(groups)):
 a=groups[group];b=v[group];extra=a-b;missing=b-a;den=max(len(b),1);result.append({'ano':group[0],'grupo':group[1],'construido':len(a),'v24':len(b),'solo_construido':len(extra),'solo_v24':len(missing),'diferencias':len(extra)+len(missing),'porcentaje_sobre_v24':100*(len(extra)+len(missing))/den});changes += [(group[0],group[1],'SOLO_CONSTRUIDO',k) for k in extra]+[(group[0],group[1],'SOLO_V24',k) for k in missing]
out=P/'DIFERENCIAS_UNIVERSO.sqlite';assert not out.exists();q=sqlite3.connect(out);q.execute('create table diferencias (ano integer,grupo integer,estado text,llave text)');q.executemany('insert into diferencias values(?,?,?,?)',changes);q.commit();q.close();r={'tabla':result,'total_diferencias':len(changes),'detalle_privado':str(out),'limite_1_porciento_superado':any(x['porcentaje_sobre_v24']>1 for x in result),'ambiguedades':['Comparación por cuerpo de documento, no prueba identidad documental ni diferencia de DV.','Cualquier coincidencia de cuerpo entre personas distintas requiere revisión.'],'qa':'SOLO_UNIVERSO_NO_PARIDAD_CAMPOS_NI_AGREGADOS'};(O/'PARIDAD_UNIVERSO.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False))
