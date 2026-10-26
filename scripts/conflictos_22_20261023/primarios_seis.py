from pathlib import Path
from openpyxl import load_workbook
import csv,json,hashlib,collections,unicodedata
P=Path('/Users/alexi/.local/share/ipss/analisis_conflictos_22_20261023');E=json.loads((P/'ERRORES6_DETALLE.json').read_text());base=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada')
def val(x):return str(x if x is not None else '').strip().removesuffix('.0')
refs={2022:base/'2022/2022.csv',2024:next((base/'2024').glob('08-05-2024*csv')),2025:base/'2025/2025.xlsx'}
loaded={};out=[]
for year,p in refs.items():
 if p.suffix=='.csv':
  raw=p.read_bytes()
  for enc in ['utf-8-sig','latin-1']:
   try:text=raw.decode(enc);break
   except UnicodeDecodeError:pass
  rr=list(csv.reader(text.splitlines(),delimiter=';'));h=rr[0];rows=rr[1:];sh='CSV'
 else:
  w=load_workbook(p,read_only=True,data_only=True);sh='08-05-2025_22-26-22_Matrícula_P';rows=list(w[sh].values);h=rows[0];rows=rows[1:];w.close()
 loaded[year]=(p,sh,h,rows)
for e in E:
 year=int(e['ano'])
 if year not in loaded:continue
 p,sh,h,rows=loaded[year];orig=e['obs'][0]['evidencias_matricula'][0];cand=[]
 for i,vs in enumerate(rows,2):
  d=dict(zip(h,vs))
  if val(d.get('N_DOC'))==val(orig['documento_original']) and val(d.get('DV')).upper()==val(orig['dv_original']).upper() and ('TIPO_DOC' not in d or not val(orig.get('tipo_doc_original')) or val(d['TIPO_DOC']).upper()==val(orig['tipo_doc_original']).upper()):
   code='I162S'+val(d.get('COD_SED'))+'C'+val(d.get('COD_CAR'))+'J'+val(d.get('JOR'))+'V'+val(d.get('VERSION'))
   safe=['COD_SED','COD_CAR','JOR','VERSION','ANIO_ING_ACT','SEM_ING_ACT','ANIO_ING_ORI','SEM_ING_ORI','FOR_ING_ACT','FECH_CAR','NIVEL','NIVEL 2','NIVEL_1','NIVEL_2','CONTINUIDAD','CARRERA','VIG','VIGENCIA']
   cand.append({'fila':i,'codigo':code,'tipo_doc_verificado':('TIPO_DOC' in d and bool(val(orig.get('tipo_doc_original')))),'limite_tipo_doc':('Columna TIPO_DOC ausente' if 'TIPO_DOC' not in d else 'Tipo original ausente' if not val(orig.get('tipo_doc_original')) else None),'campos':{k:val(d.get(k)) for k in safe if k in d}})
 out.append({'id':e['id'],'ruta':str(p),'hoja':sh,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'coincidencias_identidad':cand,'codigo_objetivo_reproducido':any(d['codigo']==e['codigo'] for d in cand)})
Path('/tmp/errores6_primarios_agregados.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False,indent=2))
