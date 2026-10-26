"""Comprueba referencias de ambas alternativas en PROMEDIOS sin publicar identidades."""
import collections,hashlib,json,re
from pathlib import Path
import openpyxl
P=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026');OUT=Path(__file__).parent
BASE=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/04_UMAS_PROMEDIOSDEALUMNOS')
amb=json.loads((P/'ADJUDICACIONES_13_2025_Y_ALTERNATIVAS.json').read_text())['alternativas']; assert len(amb)==2
index=collections.defaultdict(list)
for a in amb:
 for file,rows in a['fuentes_promedios'].items():
  for row in rows:index[(file,int(row))].append(a)
def clean(x):return '' if x is None else str(x).strip().upper()
def identity(n,d):
 n=clean(n).replace('.','').replace(' ','');d=clean(d)
 return str(int(n))+'-'+d if re.fullmatch(r'\d+',n) and re.fullmatch(r'[0-9K]',d) else None
results=[]; errors=0
for file in sorted({k[0] for k in index}):
 p=BASE/file;sha=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):sha.update(b)
 w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=w['Hoja1'].iter_rows(values_only=True);h={clean(v):i for i,v in enumerate(next(it))};checked=0
 for num,row in enumerate(it,2):
  for a in index.get((file,num),[]):
   def g(k):return clean(row[h[k]]) if k in h and h[k]<len(row) else ''
   ok=(identity(g('RUT'),g('DIG'))==a['persona'] and g('CODCLI')==a['CODCLI'] and g('PLAN_DE_ESTUDIO')==a['plan'] and g('CODCARR')==a['carrera'] and g('ANO')==a['ano'] and g('PERIODO')==a['periodo'] and g('JORNADA')=={'1':'D','2':'V'}[a['jornada_sies']]);checked+=1;errors+=not ok
 w.close(); expected=sum(len(v) for (f,_),v in index.items() if f==file);assert checked==expected
 results.append({'ruta':str(p),'hoja':'Hoja1','sha256':sha.hexdigest(),'referencias':checked})
assert not errors
out={'clasificacion':'B observaciones; C verificacion','alternativas':len(amb),'referencias_verificadas':sum(x['referencias'] for x in results),'errores':errors,'fuentes':results,'limite':'Actividad y jornada informada en asignaturas; no acreditan vigencia de cierre ni deciden el cambio de jornada.'}
(OUT/'QA_FUENTES_JORNADAS_AMBIGUAS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
