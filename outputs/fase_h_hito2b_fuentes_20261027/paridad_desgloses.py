from pathlib import Path
import openpyxl,json,hashlib
O=Path(__file__).parent;p=Path.home()/'.local/share/ipss/fase_h_regla_intertrimestral_20261027/V24_QA_COPIA.xlsx';assert hashlib.sha256(p.read_bytes()).hexdigest()=='1e28d5955d874e7d86ec0ca87ab6a2cc478515c0dbd604f4fc86f60fa491c481';w=openpyxl.load_workbook(p,read_only=True,data_only=True);rows=list(w['20_Foto_BBDD'].iter_rows(min_row=6,max_row=4478,values_only=True));s=w['18_Foto_Intertrimestral'];out=[]
for start,field,label,flag in [(18,10,'Administración y Comercio',20),(29,10,'Tecnologías',20),(40,10,'Salud',20),(51,11,'Técnico de Nivel Superior',21),(62,11,'Profesional sin licenciatura',21)]:
 for offset,(year,group) in enumerate([(2024,1),(2025,1),(2025,2),(2025,None),(2026,1),(2026,2),(2026,3),(2026,None)]):
  rn=start+offset;data=[r for r in rows if r[1]==year and r[field]==label and (r[2]==group if group else r[flag]==1)];expected={'D':len(data)}
  if rn not in (18,29,40,51,62):
   n=sum(r[16]==1 for r in data);den=sum(r[17]==1 for r in data);expected['G']=n;expected['H']=n/den if den else '—'
  else:expected['G']='Sin foto';expected['H']='—'
  dif=[]
  for col,v in expected.items():
   e=s[f'{col}{rn}'].value
   if not (abs(v-e)<1e-10 if isinstance(v,float) and isinstance(e,(int,float)) else e==v):dif.append({'celda':f'{col}{rn}','esperado':e,'reproducido':v})
  out.append({'fila':rn,'celdas':len(expected),'diferencias':dif})
w.close();result={'ambito':'D,G,H sectores y tipos; basada en cachés de 20, no fuentes originales','celdas':sum(r['celdas'] for r in out),'diferencias':sum(len(r['diferencias']) for r in out),'filas':out};(O/'PARIDAD_DESGLOSES_PARCIAL.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'celdas':result['celdas'],'diferencias':result['diferencias'],'detalles':[r for r in out if r['diferencias']]},ensure_ascii=False))
