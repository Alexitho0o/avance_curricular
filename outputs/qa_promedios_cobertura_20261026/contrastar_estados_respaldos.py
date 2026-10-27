"""Contraste agregado de estados discrepantes con Datos Alumnos; llaves solo en memoria."""
import collections,hashlib,json,re
from pathlib import Path
import openpyxl
OUT=Path(__file__).parent;old=json.loads((OUT/'DIFERENCIAS_ASIGNATURA_AGREGADO.json').read_text());paths={k:Path(v['ruta']) for k,v in old['fuentes'].items()}
sources={'DA_P2':Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/DATOSDEALUMNOS_10246.xlsx'),'DA_P3':Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/DATOSDEALUMNOS_11998.xlsx'),'DA_12159':Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/03_UMAS_DATOSDEALUMNOS/DATOSDEALUMNOS_12159.xlsx')}
def clean(x):
 if x is None:return ''
 if isinstance(x,(int,float)) and x==int(x):return str(int(x))
 return str(x).strip().upper()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def rows(p):
 w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=w['Hoja1'].iter_rows(values_only=True);h={clean(x):i for i,x in enumerate(next(it)) if x is not None}
 for row in it:
  yield lambda k:clean(row[h[k]]) if k in h and h[k]<len(row) else ''
 w.close()
data={}
for lab,path in paths.items():
 assert sha(path)==old['fuentes'][lab]['sha256'];d={}
 for v in rows(path):
  if v('ANO')!='2026' or v('PERIODO') not in ('2','3'):continue
  rut=v('RUT').replace('.','').lstrip('0') or '0';key=(v('PERIODO'),rut,v('DIG'),v('CODCLI'),v('CODCARR'),v('PLAN_DE_ESTUDIO'),v('CODRAMO'),v('CODSECC'));d[key]=v('ESTADO_ACADEMICO')
 data[lab]=d
a=data['respaldo_ampliado'];b=data['v11_12166'];targets=collections.defaultdict(set)
for key in a.keys()&b.keys():
 if a[key]!=b[key]:targets[(key[0],key[1],key[2],key[3])].add((a[key],b[key]))
assert len([x for x in targets if x[0]=='2'])==2 and len([x for x in targets if x[0]=='3'])==1
out={'clasificacion':'B observaciones; C cruce; E fecha de cambio','grupos':{},'fuentes':{},'limite':'Los estados de cada extracción no acreditan fecha de cambio ni estado en cierre.'}
for name,path in sources.items():
 matches=collections.defaultdict(set)
 for v in rows(path):
  doc=v('RUT').replace('.','').replace(' ','');
  if '-' not in doc:continue
  num,dv=doc.split('-',1)
  if not num.isdigit() or not re.fullmatch('[0-9K]',dv):continue
  person=(str(int(num)),dv,v('CODCLI'))
  for target in targets:
   if person==target[1:]:matches[target].add(v('ESTADOACADEMICO'))
 groups=collections.Counter()
 for target in targets:
  pattern=tuple(sorted(matches[target]));groups[(target[0],','.join(pattern) if pattern else 'SIN_COINCIDENCIA')]+=1
 out['grupos'][name]=[{'periodo_diferencia':p,'estado_en_respaldo':s,'expedientes':n} for (p,s),n in sorted(groups.items())];out['fuentes'][name]={'ruta':str(path),'hoja':'Hoja1','sha256':sha(path)}
(OUT/'CONTRASTE_ESTADOS_RESPALDOS_AGREGADO.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
