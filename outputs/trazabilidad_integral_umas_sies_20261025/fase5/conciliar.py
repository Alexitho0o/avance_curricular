"""Audita la copia recalculada por Excel; solo lectura, salidas agregadas."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from collections import Counter,defaultdict
from functools import lru_cache
import json,hashlib,re,math,fnmatch
from openpyxl.formula.translate import Translator
OUT=Path(__file__).resolve().parent
PRIVATE=Path('/Users/alexi/.local/share/ipss/trazabilidad_integral_fase5_20261025')
SOURCE=Path('/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V19_TRAZABLE.xlsx')
NATIVE=PRIVATE/'RETENCION_IPSS_V19_PRUEBA_EXCEL_FASE5.xlsx'
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def save(name,x):(OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
class Book:
 def __init__(self,p):
  self.z=ZipFile(p);self.ss=[''.join(x.itertext()) for x in E.fromstring(self.z.read('xl/sharedStrings.xml'))] if 'xl/sharedStrings.xml' in self.z.namelist() else []
  self.names=[s.get('name') for s in E.fromstring(self.z.read('xl/workbook.xml')).find('s:sheets',NS)];self.data={};self.formulas={}
  for i,name in enumerate(self.names,1):
   vals={};fs={};masters={};followers=[]
   root=E.fromstring(self.z.read(f'xl/worksheets/sheet{i}.xml'))
   for c in root.findall('s:sheetData/s:row/s:c',NS):
    ref=c.get('r');v=c.find('s:v',NS);inline=c.find('s:is',NS);t=c.get('t');x=None
    if inline is not None:x=''.join(inline.itertext())
    elif v is not None and v.text is not None:
     x=self.ss[int(v.text)] if t=='s' else v.text
     if t not in ['s','str','e']:
      try:x=float(x);x=int(x) if x.is_integer() else x
      except ValueError:pass
    vals[ref]=x
    f=c.find('s:f',NS)
    if f is not None:
     if f.text:fs[ref]=f.text
     if f.get('t')=='shared':
      if f.text:masters[f.get('si')]=(ref,f.text)
      else:followers.append((ref,f.get('si')))
   for ref,si in followers:
    if si in masters:
     origin,formula=masters[si];fs[ref]=Translator('='+formula,origin=origin).translate_formula(ref)[1:]
   self.data[name]=vals;self.formulas[name]=fs
 def v(self,s,c):return self.data[s].get(c.replace('$',''))
 def arg(self,s,a):
  a=a.strip()
  if a.startswith('"') and a.endswith('"'):return a[1:-1].replace('""','"')
  try:return float(a)
  except ValueError:pass
  m=re.fullmatch(r"(?:'([^']+)'!)?(\$?[A-Z]+\$?\d+)",a)
  if m:return self.v(m[1] or s,m[2])
  raise ValueError(a)
 @lru_cache(None)
 def rng(self,s,a):
  m=re.fullmatch(r"(?:'([^']+)'!)?(\$?([A-Z]+)\$?(\d+)):(\$?([A-Z]+)\$?(\d+))",a)
  if not m or m[3]!=m[6]:raise ValueError(a)
  return [self.v(m[1] or s,f'{m[3]}{r}') for r in range(int(m[4]),int(m[7])+1)]
def eq(a,b):
 if a in [None,''] and b in [None,'']:return True
 if isinstance(a,(float,int)) and isinstance(b,(float,int)):return math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-10)
 return a==b
b=Book(SOURCE);e=Book(NATIVE)
assert sha(SOURCE)=='daae975e42698dfb63bb3877e63bd8b7bdc499c50da05092d21772038ef457ee'
changes=[];constants=[];formula_missing=[]
for s in b.names:
 for c,v in b.data[s].items():
  if not eq(v,e.v(s,c)):
   # Individual values remain private: public log only location and whether numeric.
   changes.append({'hoja':s,'celda':c,'formula':c in b.formulas[s],'numerica':isinstance(v,(int,float))})
  if c not in b.formulas[s] and not eq(v,e.v(s,c)):constants.append({'hoja':s,'celda':c})
 for c in b.formulas[s]:
  if c not in e.formulas[s]:formula_missing.append({'hoja':s,'celda':c})

def splitargs(t):
 out=[];q=False;depth=0;start=0
 for i,c in enumerate(t):
  if c=='"':q=not q
  if not q:
   if c=='(':depth+=1
   if c==')':depth-=1
   if c==',' and depth==0:out.append(t[start:i]);start=i+1
 out.append(t[start:]);return out

def matches(v,crit):
 if crit is None:crit=0
 if isinstance(crit,str):
  m=re.match(r'^(<>|>=|<=|>|<|=)(.*)$',crit)
  if m:
   op,c=m.groups()
   try:c=float(c)
   except ValueError:pass
   if op=='<>':return not matches(v,c)
   if op=='=':return matches(v,c)
   try:return {'>':lambda:v>c,'<':lambda:v<c,'>=':lambda:v>=c,'<=':lambda:v<=c}[op]()
   except TypeError:return False
  if isinstance(v,str):return fnmatch.fnmatchcase(v.lower(),crit.lower())
  try:return v==float(crit)
  except ValueError:return False
 return v==crit
checks=[];skips=Counter()
# Independent aggregation: evaluate simple COUNTIFS/SUMIFS directly over rows.
for s in e.names:
 if s.startswith(('9_','11_','20_','24_','25_','56_')):continue
 for c,f in e.formulas[s].items():
  m=re.fullmatch(r'(COUNTIFS|SUMIFS)\((.*)\)',f)
  if not m:continue
  try:
   args=splitargs(m[2]);sumvalues=None
   if m[1]=='SUMIFS':sumvalues=e.rng(s,args.pop(0))
   arrays=[e.rng(s,args[i]) for i in range(0,len(args),2)]
   criteria=[e.arg(s,args[i]) for i in range(1,len(args),2)]
   idx=[k for k,row in enumerate(zip(*arrays)) if all(matches(v,crit) for v,crit in zip(row,criteria))]
   expected=len(idx) if sumvalues is None else sum(sumvalues[k] for k in idx if isinstance(sumvalues[k],(int,float)))
   checks.append({'hoja':s,'celda':c,'esperado':expected,'excel':e.v(s,c),'coincide':eq(expected,e.v(s,c))})
  except (ValueError,IndexError,TypeError):skips[s]+=1
annual=[]
for r in range(7,2386):
 s='9_Base_Analitica_Detalle';annual.append({k:e.v(s,f'{col}{r}') for k,col in {'cohorte':'B','carrera':'C','sector':'E','retenido':'F','sexo':'M','modalidad':'O','jornada':'Q','edad':'T','codigo':'X'}.items()})
cohortes=sorted({x['cohorte'] for x in annual});controls=[]
for y in cohortes:
 rows=[x for x in annual if x['cohorte']==y];controls.append({'cohorte':y,'estudiantes':len(rows),'retenidos':sum(x['retenido'] for x in rows)})
# 15 cohort selections × all sectors, plus each career under its own sector.
cases=[]
choices=[e.v('14_Vistas_Ejecutivas',f'BL{r}') for r in range(2,17)]
sectors=['Todos']+sorted({x['sector'] for x in annual})
for choice in choices:
 years=cohortes if choice=='Acumulado 2022-2025' else [y for y in cohortes if str(y) in choice]
 for sector in sectors:
  rows=[x for x in annual if x['cohorte'] in years and (sector=='Todos' or x['sector']==sector)]
  cases.append({'cohorte':choice,'sector':sector,'carrera':'Todas','n':len(rows),'retenidos':sum(x['retenido'] for x in rows)})
for career in sorted({x['carrera'] for x in annual}):
 rows=[x for x in annual if x['carrera']==career];sector=rows[0]['sector'];cases.append({'cohorte':'Acumulado 2022-2025','sector':sector,'carrera':career,'n':len(rows),'retenidos':sum(x['retenido'] for x in rows)})
save('CASOS_FILTROS.json',cases)
save('CONCILIACION_PRE_FILTROS.json',{'clase':'B/C/E','sha256_v19':sha(SOURCE),'sha256_copia_nativa':sha(NATIVE),'cambios_cache':changes,'cambios_constantes':constants,'formulas_perdidas':formula_missing,'agregaciones_comprobadas':len(checks),'diferencias_agregaciones':[x for x in checks if not x['coincide']],'patrones_no_evaluados':dict(skips),'cohortes':controls,'casos_filtros':len(cases),'limite':'Prueba independiente de agregaciones desde detalle. No sustituye evidencia del estado a una fecha ni acredita aceptación SIES.'})
save('CONTROLES_AGREGACION.json',checks)
print(json.dumps({'cambios_cache':len(changes),'cambios_constantes':len(constants),'formulas_perdidas':len(formula_missing),'agregaciones':len(checks),'diferencias':sum(not x['coincide'] for x in checks),'filtros':len(cases),'cohortes':controls},ensure_ascii=False))
