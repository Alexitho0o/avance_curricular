from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib,csv,re,datetime
import openpyxl
ROOT=Path('/Users/alexi/Documents/GitHub/avance_curricular');P=Path(__file__).resolve().parent
prev=json.loads((ROOT/'outputs/retencion_intermedia_t2_t3/20261021_090522_cobertura/RESULTADOS_AGREGADOS.json').read_text())
def text(v):return '' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip().upper()
def key(v,d=None):
 v=text(v).replace('.','').replace(' ','')
 if d is None:
  if '-' not in v:return None
  v,d=v.rsplit('-',1)
 d=text(d)
 return str(int(v))+'-'+d if re.fullmatch(r'\d+',v) and re.fullmatch('[0-9K]',d) else None
sources=[]
def read(i):
 path=Path(i['ruta']);h=hashlib.sha256(path.read_bytes()).hexdigest();assert h==i['sha256']
 sources.append(i);w=openpyxl.load_workbook(path,read_only=True,data_only=True);it=w[i['hoja']].iter_rows(values_only=True);headers=[text(x) for x in next(it)];rows=[dict(zip(headers,x)) for x in it if any(v is not None for v in x)];w.close();return rows
mu=read(prev['fuentes'][0]);umas=read(prev['fuentes'][1]);older=read(prev['fuentes'][2]);raw25=read(next(s for s in prev['fuentes'] if s['ruta'].endswith('/2025/2025.xlsx')))
idx=defaultdict(list);ix25=defaultdict(list);ui=defaultdict(list)
for r in mu:
 if r['ANIO_INFORMADO']==2025:idx[key(r['N_DOC'],r['DV'])].append(r)
for r in raw25:ix25[key(r['N_DOC'],r['DV'])].append(r)
for r in umas:ui[key(r['RUT'])].append(r)
catpath=ROOT/'DURACION_ESTUDIOS.tsv'
sources.append({'ruta':str(catpath),'sha256':hashlib.sha256(catpath.read_bytes()).hexdigest()})
with catpath.open(encoding='utf-8-sig') as f:cat=list(csv.DictReader(f,delimiter='\t'))
cc=defaultdict(set)
for r in cat:
 for c in [r['CODCARPR_CANONICO']]+re.split('[;,|]',r['CODCARPR_ALIAS_LIST']):
  if c.strip():cc[text(c)].add(r['CODIGO_CARRERA'])
subsets={}
for term in [2,3]:
 sr=[r for r in umas if text(r['ANOINGRESO'])=='2024' and text(r['PERIODOINGRESO'])==str(term)]
 ks={key(r['RUT']) for r in sr};present={k for k in ks if idx.get(k)};target={k for k in present if any(text(r['ANIO_ING_ORI'])=='2025' for r in idx[k])};subsets[term]=target
 trans=Counter();pairs=Counter();foring=Counter();act=Counter();mucodes=Counter();status=Counter();otherorig=Counter();flags=Counter();cadiff=Counter()
 for k in target:
  ss=[r for r in sr if key(r['RUT'])==k];dd=[r for r in idx[k] if text(r['ANIO_ING_ORI'])=='2025'];dr=ix25[k]
  src_codes={text(r['CODCARPR']) for r in ss};dest_codes={text(r['COD_CAR']) for r in dd}
  mapped=set().union(*(cc.get(c,set()) for c in src_codes))
  classification='MISMO_COD_CAR' if len(mapped)==1 and dest_codes==mapped else 'COD_CAR_DISTINTO' if mapped and not(mapped&dest_codes) else 'AMBIGUO_O_SIN_MAPEO'
  status[classification]+=1
  pairs[(' / '.join(sorted(src_codes)),' / '.join(sorted(mapped)),' / '.join(sorted(dest_codes)),classification)]+=1
  trans[(' / '.join(sorted({text(r['NOMBRE_L']) for r in ss})),' / '.join(sorted({text(r['CARRERA']) for r in dr})))]+=1
  foring[' / '.join(sorted({text(r['FOR_ING_ACT']) for r in dd}))]+=1
  act[' / '.join(sorted({text(r['ANIO_ING_ACT'])+':'+text(r['SEM_ING_ACT']) for r in dd}))]+=1
  mucodes[' / '.join(sorted({text(r['COD_CAR']) for r in dd}))]+=1
  for r in ss:
   if text(r['SITUACION']).startswith(('24','27','49')):flags[(text(r['ESTADOACADEMICO']),text(r['SITUACION']))]+=1
  allu=ui[k];allcodes={text(r['CODCARPR']) for r in allu}
  cadiff['VARIOS_CODCARPR' if len(allcodes)>1 else 'UN_CODCARPR']+=1
  otherorig[' / '.join(sorted({text(r['ANOINGRESO'])+':'+text(r['PERIODOINGRESO']) for r in allu}))]+=1
 result={'term':term,'personas_ingreso2024':len(ks),'presentes':len(present),'origen2025':len(target),'comparacion_carrera':dict(status),'pares_codigo':[{'CODCARPR_UMAS':a,'COD_CAR_catalogo':b,'COD_CAR_MU2025':c,'resultado':z,'personas':n}for (a,b,c,z),n in sorted(pairs.items())],'pares_nombre':[{'nombre_UMAS':a,'nombre_RAW_MU2025':b,'personas':n}for(a,b),n in trans.items()],'FOR_ING_ACT_MU':dict(foring),'ANIO_SEM_ING_ACT_MU':dict(act),'mismo_otro_programa_umas':dict(cadiff),'origenes_umas_historia':dict(otherorig),'situaciones_cambio_en_filas_origen':[{'estado':a,'situacion':b,'filas':n}for(a,b),n in flags.items()]}
 (P/f'RESULTADO_T{term}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False))
print('UNION_T2_T3',len(subsets[2]|subsets[3]),'INTERSECCION',len(subsets[2]&subsets[3]))
(P/'FUENTES.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
