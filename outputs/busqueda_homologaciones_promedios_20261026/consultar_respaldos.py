"""Revisa ramos y campos de reconocimiento, separando cada extracción UMAS."""
import collections,hashlib,json
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
folder=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/04_UMAS_PROMEDIOSDEALUMNOS')
targets={(x['carrera'],x['plan_revisado'],x['ramo']) for x in json.loads((ROOT/'outputs/busqueda_respaldo_titulos_homologaciones_20261026/RESULTADO_AGREGADO.json').read_text())['ramos']}
assert len(targets)==21
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def s(x):
 if x is None:return ''
 if isinstance(x,(int,float)) and x==int(x):return str(int(x))
 return str(x).strip().upper()
sources=[];results=[]
for name in ('PROMEDIOSDEALUMNOS_7804.xlsx','PROMEDIOSDEALUMNOS_3233.xlsx','PROMEDIOSDEALUMNOS_2071.xlsx'):
 p=folder/name;hsh=sha(p);w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=w['Hoja1'].iter_rows(values_only=True);h={s(v):i for i,v in enumerate(next(it)) if v is not None}
 fields=('CODCARR','PLAN_DE_ESTUDIO','CODRAMO','ANO','PERIODO','ESTADO','DESCRIPCION_ESTADO','CONVALIDADO','RAMOEQUIV')
 assert set(fields).issubset(h);counts=collections.Counter();other=collections.Counter()
 for row in it:
  def get(k):return s(row[h[k]]) if h[k]<len(row) else ''
  career,plan,code=(get(k) for k in ('CODCARR','PLAN_DE_ESTUDIO','CODRAMO'))
  if (career,plan,code) in targets:counts[(career,plan,code,get('ANO'),get('PERIODO'),get('ESTADO'),get('DESCRIPCION_ESTADO'),get('CONVALIDADO'),get('RAMOEQUIV'))]+=1
  elif code in {z[2] for z in targets}:other[(career,plan,code)]+=1
 w.close();assert sha(p)==hsh
 sources.append({'ruta':str(p),'hoja':'Hoja1','sha256':hsh,'filas_objetivo':sum(counts.values()),'ramos_objetivo':len({(x[0],x[1],x[2]) for x in counts}),'ramos_otro_plan':len({x[2] for x in other})})
 results.extend({'fuente':name,'carrera':ca,'plan':p,'ramo':c,'ano':y,'periodo':per,'estado_ramo':e,'descripcion_estado':d,'convalidado':conv,'ramo_equivalente':eq,'filas':n} for (ca,p,c,y,per,e,d,conv,eq),n in sorted(counts.items()))
out={'clasificacion':'B observaciones; C filtrado; E homologación aplicable','fuentes':sources,'resultados_exactos':results,'limites':'Filas no equivalen a personas; extracciones se solapan y no deben sumarse. Campo de reconocimiento describe cada fila y no acredita homologación general, fecha de cambio o vigencia del plan.','ramos_objetivo':21}
(OUT/'RESULTADO_AGREGADO.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'fuentes':[{'archivo':Path(x['ruta']).name,'ramos_objetivo':x['ramos_objetivo'],'filas_objetivo':x['filas_objetivo'],'ramos_otro_plan':x['ramos_otro_plan']} for x in sources]},ensure_ascii=False))
