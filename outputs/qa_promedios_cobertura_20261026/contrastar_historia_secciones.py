"""Busca secciones previas por expediente y ramo para los nueve pares de 2026-3."""
import collections,json,hashlib
from pathlib import Path
import openpyxl
OUT=Path(__file__).parent;d=json.loads((OUT/'DIFERENCIAS_ASIGNATURA_AGREGADO.json').read_text());paths={k:Path(v['ruta']) for k,v in d['fuentes'].items()}
def norm(x):
 if x is None:return ''
 if isinstance(x,(int,float)) and int(x)==x:return str(int(x))
 return str(x).strip().upper()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
data={}
for label,p in paths.items():
 assert sha(p)==d['fuentes'][label]['sha256']; w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=w['Hoja1'].iter_rows(values_only=True);h={norm(x):i for i,x in enumerate(next(it)) if x is not None};s=collections.defaultdict(set)
 for row in it:
  def v(k):return norm(row[h[k]]) if k in h and h[k]<len(row) else ''
  if v('ANO')!='2026' or v('PERIODO') not in ('1','2','3'):continue
  prefix=(v('RUT').replace('.','').lstrip('0') or '0',v('DIG'),v('CODCLI'),v('CODCARR'),v('PLAN_DE_ESTUDIO'),v('CODRAMO'))
  if all(prefix) and v('CODSECC'):s[(v('PERIODO'),prefix)].add(v('CODSECC'))
 w.close();data[label]=s
a=data['respaldo_ampliado'];b=data['v11_12166'];pairs=[]
for key in set(a)&set(b):
 if key[0]=='3' and len(a[key])==len(b[key])==1 and a[key]!=b[key]:pairs.append((key[1],next(iter(a[key])),next(iter(b[key]))))
assert len(pairs)==9
summary={}
for period in ('1','2'):
 c=collections.Counter()
 for prefix,sa,sb in pairs:
  observed=a.get((period,prefix),set())|b.get((period,prefix),set())
  if not observed:c['sin_observacion_del_mismo_ramo']+=1
  elif sa in observed and sb in observed:c['coinciden_ambas_secciones']+=1
  elif sa in observed:c['coincide_con_seccion_respaldo']+=1
  elif sb in observed:c['coincide_con_seccion_v11']+=1
  else:c['otra_seccion']+=1
 summary['2026-'+period]=dict(c)
out={'clasificacion':'B actividad; C cruce; E atribucion por corte','pares_t3':len(pairs),'observaciones_en_periodos_previos':summary,'fuentes_sha256':{k:sha(p) for k,p in paths.items()},'limite':'Un ramo en otro período puede representar otra inscripción; no acredita sección de T3 ni fecha efectiva de cambio. Secciones anteriores observadas en cualquiera de los dos archivos PROMEDIOS.'}
(OUT/'HISTORIA_SECCIONES_AGREGADA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
