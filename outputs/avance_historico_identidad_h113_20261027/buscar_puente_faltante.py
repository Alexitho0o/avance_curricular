"""Búsqueda exacta de documento P en respaldos acotados; salida sin identidad."""
from pathlib import Path
import json,re,hashlib
import openpyxl,pandas as pd
OUT=Path(__file__).parent
old=json.loads((OUT/'MANIFEST.json').read_text())
src=old['fuentes'];target=pd.read_csv(src['h113']['ruta'],header=None,sep=';',dtype=str,encoding='latin1',keep_default_na=False)
focus=target[(target[0]=='P')&(target[8]=='I162S2C1J2V4')&(target[14]=='SI')&(target[15]=='SI')&target[[16,17,18,19]].eq('12').all(axis=1)]
assert len(focus)==1, 'Seleccion no unica: requiere volver a la reproduccion'
doc=focus.iloc[0,1]
def norm(x):
 if x is None:return ''
 if isinstance(x,float) and x.is_integer():return str(int(x))
 return re.sub(r'[.\s]','',str(x)).upper()
base=Path(src['h113']['ruta']).parent
paths=[Path(src['puente_mu']['ruta']),base/'EXCEL_MAESTRO_KPI_TRAZABILIDAD_COMPLETO_AVANCE_CURRICULAR_2026.xlsx',base/'5809_MATRICULA_AVANCE_CURRICULAR_2026.xlsx']
out=[]
for path in paths:
 if not path.exists():continue
 digest=hashlib.sha256(path.read_bytes()).hexdigest()
 wb=openpyxl.load_workbook(path,read_only=True,data_only=True)
 res={'ruta':str(path),'sha256':digest,'hojas':[]}
 for sh in wb:
  headers=None;counts={};companions=set();total=0
  for i,row in enumerate(sh.iter_rows(values_only=True),1):
   if headers is None and any(str(x).strip().upper() in ['RUT','N_DOC','NUM_DOCUMENTO','CODCLI'] for x in row):headers=row
   matches=[k for k,x in enumerate(row) if norm(x)==norm(doc)]
   if matches:
    total+=1
    for k in matches:
     label=str(headers[k]) if headers and k<len(headers) else 'sin encabezado localizado'
     counts[label]=counts.get(label,0)+1
    if headers:
     companions.update(str(h) for h in headers if h is not None and any(t in str(h).upper() for t in ['CODCLI','PLAN','RUT','DOC','DV']))
  if total:res['hojas'].append({'hoja':sh.title,'filas_con_documento_exacto':total,'columnas_con_coincidencia':counts,'columnas_contextuales_disponibles':sorted(companions)})
 wb.close();res['hash_intacto']=digest==hashlib.sha256(path.read_bytes()).hexdigest();out.append(res)
 print(json.dumps(res,ensure_ascii=False),flush=True)
(OUT/'BUSQUEDA_PUENTE_FALTANTE.json').write_text(json.dumps({'clase':'B/C/E','criterio':'Documento exacto; sin busqueda por nombre ni semejanza; no adopta enlaces','fuentes':out},ensure_ascii=False,indent=2)+'\n')
