"""Audita expedientes alternativos por identidad; detalle solo en almacenamiento privado."""
import collections, hashlib, json, os, re
from pathlib import Path
import openpyxl

ROOT=Path(__file__).resolve().parents[2]
PRIVATE=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026')
source=PRIVATE/'EVALUACION_CIERRE_CO_V1_DETALLE_V2.json'
targets=json.loads(source.read_text())
targets=[t for t in targets if t['diferencia_familia'] and str(t['anio'])=='2025' and any(str(m['anio'])=='2026' and m.get('codigo','').rsplit('V',1)[0] in t['familias_destino'] for m in t['mu_fuente_primaria'])]
assert len(targets)==13 and len({t['persona'] for t in targets})==8
paths=[('DA_P2_2026',Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/DATOSDEALUMNOS_10246.xlsx')),('DA_P3_2026',Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/DATOSDEALUMNOS_11998.xlsx'))]
def txt(x):
 return '' if x is None else str(x).strip().upper()
def rut(row,h):
 s=txt(row[h['RUT']]).replace('.','').replace(' ','')
 if '-' in s: a,b=s.split('-',1)
 else:
  a=s; j=h.get('DIG',h.get('DV')); b=txt(row[j]) if j is not None else ''
 return str(int(a))+'-'+b if re.fullmatch(r'\d+',a) and re.fullmatch(r'[0-9K]',b) else ''
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
identities={t['persona'] for t in targets}; entries=collections.defaultdict(list); files=[]
for name,p in paths:
 w=openpyxl.load_workbook(p,read_only=True,data_only=True); it=w['Hoja1'].iter_rows(values_only=True); h={txt(v):i for i,v in enumerate(next(it))}
 assert {'RUT','CODCLI'}.issubset(h)
 for num,row in enumerate(it,2):
  person=rut(row,h)
  if person not in identities: continue
  def val(k):return txt(row[h[k]]) if k in h and h[k]<len(row) else ''
  entries[(name,person)].append({'fila':num,'codcli':val('CODCLI'),'carrera':val('CODCARPR') or val('CODIGOCARRERA'),'sede':val('SEDE'),'jornada':val('JORNADA'),'estado':val('ESTADOACADEMICO')})
 w.close(); files.append({'fuente':name,'ruta':str(p),'hoja':'Hoja1','sha256':sha(p)})
counts=collections.Counter(); codes=collections.Counter(); individual=[]
for t in targets:
 candidate=sorted({m['codigo'] for m in t['mu_fuente_primaria'] if str(m['anio'])=='2026' and m.get('codigo','').rsplit('V',1)[0] in t['familias_destino']})
 assert len(candidate)==1
 codes[(t['carrera'],str(t['periodo']),candidate[0])]+=1
 d={'contexto':t['pos'],'fuente_T1':t['codigo_T1'],'candidato':candidate[0],'persona':t['persona'],'codcli':t['codcli'],'plan':t['plan'],'periodo':t['periodo'],'respaldos':{}}
 for name,p in paths:
  records=entries[(name,t['persona'])]; clis={r['codcli'] for r in records if r['codcli']}; matches=[r for r in records if r['codcli']==t['codcli']]
  counts[name+'_mismo_codcli']+=bool(matches);counts[name+'_un_solo_codcli_persona']+=len(clis)==1
  counts[name+'_multiples_codcli_persona']+=len(clis)>1
  counts[name+'_misma_carrera_jornada']+=any(r['carrera']==t['carrera'] and r['jornada']=={'1':'D','2':'V','4':'O'}.get(str(t['jornada'])) for r in matches)
  d['respaldos'][name]=records
 individual.append(d)
dest=PRIVATE/'REVISION_TRECE_EXPEDIENTES_DETALLE.json';fd=os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as f:json.dump(individual,f,ensure_ascii=False,indent=2)
out={'clasificacion':'B datos; C cruce; E atribucion documental','contextos':len(targets),'personas':len(identities),'expedientes':len({(t['persona'],t['codcli']) for t in targets}),'grupos':[{'carrera':a,'periodo':b,'codigo_candidato':c,'contextos':n} for (a,b,c),n in sorted(codes.items())],'controles':dict(counts),'fuentes':files,'detalle_privado_sha256':sha(dest),'limite':'Los respaldos 2026 no acreditan por sí mismos la fecha del cambio ni el código documental del periodo 2025.'}
(ROOT/'outputs/v11_fase2_20261026/REVISION_TRECE_EXPEDIENTES_AGREGADO.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False))
