"""Paridad parcial V24 sobre fotografía calculada: no reproduce fuentes crudas."""
from pathlib import Path
import argparse,hashlib,json,openpyxl,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R));from common.indicador_intertrimestral import ratio
ap=argparse.ArgumentParser();ap.add_argument('--copia-privada',required=True);ap.add_argument('--sha256',required=True);a=ap.parse_args();p=Path(a.copia_privada);h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==a.sha256
w=openpyxl.load_workbook(p,read_only=True,data_only=True);ws=w['20_Foto_BBDD'];rows=list(ws.iter_rows(min_row=6,max_row=4478,max_col=22,values_only=True));foto=w['18_Foto_Intertrimestral'];proxy=w['26_Avance_Curricular_Resumen'];ren=w['23_Foto_Renuncias_T2_2026'];out=[]
for rr,year,group in [(7,2024,1),(8,2025,1),(9,2025,2),(10,2025,None),(11,2026,1),(12,2026,2),(13,2026,3),(14,2026,None)]:
 data=[r for r in rows if r[1]==year and (r[2]==group if group else r[19]==1)];d=len(data);m={'D':d}
 if rr in (7,8,11):
  n=proxy[f'E{ {7:1850,8:1852,11:1854}[rr]}'].value;m['E']=n;m['F']=float(ratio(n,d))
 elif rr==9:
  n=sum(r[12]=='VIG 1' for r in data);base=sum(r[12] not in ('NO APLICA','PENDIENTE') for r in data);m['E']=n;m['F']=float(ratio(n,base))
 elif rr==12:
  n=sum((ren.cell(i,6).value or 0) for i in range(6,25));base=sum((ren.cell(i,3).value or 0) for i in range(6,25));m['E']=n;m['F']=float(ratio(n,base))
 elif rr==13:m.update(E='No aplica',F='—')
 else:m.update(E='Sin foto completa',F='—')
 if rr==7:
  n=proxy['E1851'].value;m['G']=n;m['H']=float(ratio(n,d))
 else:
  n=sum(r[16]==1 for r in data);base=sum(r[17]==1 for r in data);m['G']=n;m['H']=float(ratio(n,base)) if base else '—'
 actual={col:foto[f'{col}{rr}'].value for col in m};fail=[c for c in m if not (abs(actual[c]-m[c])<1e-10 if isinstance(m[c],float) and isinstance(actual[c],(int,float)) else actual[c]==m[c])];out.append({'fila':rr,'calculado':m,'excel':actual,'diferencias':fail})
w.close();result={'fuente_copia_sha256':h,'ambito':'Hoja 18 institucional D:H; lectura de indicadores cacheados hoja 20/26/23, no reproducción desde RAW','celdas':sum(len(z['calculado']) for z in out),'diferencias':sum(len(z['diferencias']) for z in out),'filas':out,'paridad_completa':False};print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(1 if result['diferencias'] else 0)
