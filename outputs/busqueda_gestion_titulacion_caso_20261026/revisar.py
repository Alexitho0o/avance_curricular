"""Examina gestiones del caso sin exportar identidades ni texto libre."""
import collections,hashlib,json,unicodedata
from pathlib import Path
import openpyxl
OUT=Path(__file__).resolve().parent
CASES=Path('/Users/alexi/.local/share/ipss/revision_21_ramos_4_expedientes_20261026/DETALLE_CUATRO_CASOS_V2.json')
SOURCE=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/06_INDICADORES_ACADEMICOS_VRA/GESTIONSGE_1703.xlsx')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def norm(v):
 if isinstance(v,float) and v.is_integer():return str(int(v))
 return str(v or '').strip().upper()
cases=json.loads(CASES.read_text());case=next(c for c in cases if any(x['carrera']=='TCRE' for x in c['contextos_v11']))
body=case['RUT'].split('-')[0];targets={norm(x['CODCLI']) for x in case['datosalumnos'] if x['CODCLI']};assert len(targets)==3
before=sha(SOURCE);assert before=='2ac487eb0ac09ac66d2c76afde9e62b9a4265357514d7ee696113d125a8e2401'
w=openpyxl.load_workbook(SOURCE,read_only=True,data_only=True);it=w['Hoja1'].iter_rows(values_only=True);headers=[norm(x) for x in next(it)];ids=[i for i,x in enumerate(headers) if x=='RUT_ALUMNO'];assert len(ids)==2
counts=collections.Counter();flags=collections.Counter()
for row in it:
 vals={norm(v) for v in row}
 if vals & targets:counts['filas_con_codcli_exacto_en_cualquier_celda']+=1
 candidates={norm(row[i]).replace('.','').replace(' ','') for i in ids if i<len(row)}
 valid={str(int(x)) for x in candidates if x.isdigit()}
 if valid!={body}:continue
 counts['filas_cuerpo_rut']+=1
 text=' '.join(str(row[headers.index(k)] or '') for k in ('ASUNTO','OBSERVACION') if k in headers and headers.index(k)<len(row))
 text=''.join(x for x in unicodedata.normalize('NFKD',text.upper()) if not unicodedata.combining(x))
 for tag,terms in {'titulacion':['TITULACION','TITULADO','TITULO'],
                   'plan':['PLAN DE ESTUDIO','ACTUALIZACION DE PLAN','CAMBIO DE PLAN'],
                   'homologacion':['HOMOLOG','CONVALID'],
                   'solicitud':['SOLICIT','CONSULT']}.items():
  if any(term in text for term in terms):flags[tag]+=1
w.close();assert sha(SOURCE)==before
out={'clasificacion':'B registros; C búsqueda; E identidad y atribución',
     'fuente':{'ruta':str(SOURCE),'hoja':'Hoja1','sha256':before},
     'cuenta':dict(counts),'menciones_textuales_por_fila':dict(flags),
     'limites':'Dos campos RUT_ALUMNO contienen cuerpo, sin DV independiente; no se exporta texto. Búsqueda por palabras y valores exactos no acredita decisión formal o ausencia en otras fuentes.'}
payload=json.dumps(out,ensure_ascii=False,indent=2)+'\n'
for c in cases:
 assert c['RUT'].split('-')[0] not in payload
 for x in c['datosalumnos']:assert norm(x['CODCLI']) not in payload
(OUT/'RESULTADO_AGREGADO.json').write_text(payload);print(json.dumps(out,ensure_ascii=False))
