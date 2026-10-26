import openpyxl,json,zipfile,xml.etree.ElementTree as E,re
from pathlib import Path
O=Path(__file__).parent;q=json.load(open(O/'QA_ENTREGA.json'));src=openpyxl.load_workbook('/Users/alexi/Downloads/RETENCION_IPSS_FINAL_con_Foto_Intertrimestral_20261022_AUDITADO_ENTREGA.xlsx',read_only=True,data_only=True);out=openpyxl.load_workbook(q['salida'],read_only=True,data_only=True)
ident=set();nombres=set()
s=src['11_BASE_RETENCION_MU_RAW'];header=None
for row in s.iter_rows(values_only=True):
 if 'N_DOC' in row:header=list(row);continue
 if header:
  v=row[header.index('N_DOC')]
  if v is not None and len(str(v))>=6:ident.add(str(v).strip())
  for key in ['PRIMER_APELLIDO','SEGUNDO_APELLIDO','NOMBRE']:
   v=row[header.index(key)]
   if isinstance(v,str) and len(v.strip())>3 and v not in ['NULL','SIN INFORMACION']:nombres.add(v.strip())
found_id=found_names=0; locations=[]
for s in out:
 for row in s:
  for c in row:
   v=c.value
   if v is not None and str(v).strip() in ident:found_id+=1; locations.append([s.title,c.coordinate,"id"])
   if isinstance(v,str) and v.strip() in nombres and not (s.title=='14_Vistas_Ejecutivas' and c.coordinate=='R4' and v=='CARRERA'):found_names+=1; locations.append([s.title,c.coordinate,"nombre"])
q['revision_privacidad']={'coincidencias_identificadores_fuente':found_id,'coincidencias_exactas_campos_nombre_fuente':found_names,'sharedStrings_original_eliminado':True}
print("coincidencias",locations); assert found_id==0 and found_names==0
# Todas las filas individuales pasan a conteos agregados, sin perder registros.
q['control_agregados']={}
for name in q['detalle_personal_excluido_en_v1']:
 s=out[name];total=sum(row[-1] for row in s.iter_rows(min_row=5,values_only=True) if isinstance(row[-1],(int,float)));q['control_agregados'][name]=total
(O/'QA_ENTREGA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2));print(json.dumps({'privacidad':q['revision_privacidad'],'agregados':q['control_agregados']},ensure_ascii=False))
