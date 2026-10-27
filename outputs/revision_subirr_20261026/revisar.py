"""Inspecciona subirR.xlsx por estructura y tres llaves sin exportar datos personales."""
import collections,hashlib,json,re,zipfile
from pathlib import Path
import openpyxl

OUT=Path(__file__).resolve().parent
SOURCE=Path('/Users/alexi/Downloads/subirR.xlsx')
CASES=Path('/Users/alexi/.local/share/ipss/revision_21_ramos_4_expedientes_20261026/DETALLE_CUATRO_CASOS_V2.json')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def norm(v):
 if isinstance(v,float) and v.is_integer():return str(int(v))
 return str(v or '').strip().upper()
cases=json.loads(CASES.read_text());case=next(c for c in cases if any(z['carrera']=='TCRE' for z in c['contextos_v11']))
codes={norm(x['CODCLI']) for x in case['datosalumnos'] if x['CODCLI']};assert len(codes)==3
body,dv=case['RUT'].split('-');body=str(int(body));dv=dv.upper();before=sha(SOURCE)
assert zipfile.is_zipfile(SOURCE)
w=openpyxl.load_workbook(SOURCE,read_only=True,data_only=False);sheet_data=[]
for s in w:
 counts=collections.Counter();columns=[];row_count=0
 for row in s.iter_rows(values_only=True):
  row_count+=1
  if row_count==1:columns=[norm(v) for v in row]
  for cell in row:
   v=norm(cell);clean=v.replace('.','').replace(' ','')
   if v in codes:counts['celdas_codcli_exacto']+=1
   if clean==body or (clean.isdigit() and str(int(clean))==body):counts['celdas_cuerpo_rut']+=1
   if clean==body+'-'+dv:counts['celdas_rut_dv_juntos']+=1
 sheet_data.append({'hoja':s.title,'filas_leidas':row_count,'columnas':s.max_column,
                    'campos_codcli':[x for x in columns if 'CODCLI' in x],
                    'campos_doc':[x for x in columns if x in {'RUT','N_DOC','NUM_DOCUMENTO','DV','DIG'}],
                    'campos_plan':[x for x in columns if 'PLAN' in x],
                    'campos_titulo':[x for x in columns if 'TITULO' in x or 'TITULACION' in x or 'TITULACIÓN' in x],
                    'coincidencias':dict(counts)})
w.close()
cache_counts=collections.Counter()
w=openpyxl.load_workbook(SOURCE,read_only=True,data_only=True)
for s in w:
 for row in s.iter_rows(values_only=True):
  for cell in row:
   v=norm(cell);clean=v.replace('.','').replace(' ','')
   if v in codes:cache_counts['celdas_codcli_exacto']+=1
   if clean==body or (clean.isdigit() and str(int(clean))==body):cache_counts['celdas_cuerpo_rut']+=1
   if clean==body+'-'+dv:cache_counts['celdas_rut_dv_juntos']+=1
w.close();assert sha(SOURCE)==before
out={'clasificacion':'B libro de oferta; C búsqueda; E vínculo', 'fuente':{'ruta':str(SOURCE),'sha256':before},
     'hojas':sheet_data, 'busqueda_en_valores_cache':dict(cache_counts),
     'metodo':'Tres CODCLI exactos y valores exactos de RUT con y sin DV buscados en celdas de todas las hojas, tanto fórmulas como valores cacheados; no se emparejan valores en columnas no identificadas.',
     'limites':'Título o tipo de plan en oferta describen un programa; no acreditan titulación individual o plan UMAS. Valores con un formato distinto pueden no coincidir. Sin modificar fuentes, bases ni denominadores.'}
payload=json.dumps(out,ensure_ascii=False,indent=2)+'\n'
for c in cases:
 assert c['RUT'].split('-')[0] not in payload
 for x in c['datosalumnos']:assert norm(x['CODCLI']) not in payload
(OUT/'RESULTADO_AGREGADO.json').write_text(payload)
print(json.dumps({'sha256':before,'hojas':len(sheet_data),'coincidencias':dict(sum((collections.Counter(x['coincidencias']) for x in sheet_data),collections.Counter())),'campos_codcli':sum(len(x['campos_codcli']) for x in sheet_data),'campos_documento':sum(len(x['campos_doc']) for x in sheet_data)},ensure_ascii=False))
