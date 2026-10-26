from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib,csv,re,datetime,subprocess
import openpyxl
R=Path('/Users/alexi/Documents/GitHub/avance_curricular');P=Path(__file__).resolve().parent
prior=json.loads((R/'outputs/retencion_intermedia_t2_t3/20261021_cambio_carrera_2024/FUENTES.json').read_text())
def txt(v):return '' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip().upper()
def key(v,d=None):
 v=txt(v).replace('.','').replace(' ','')
 if d is None:
  if '-' not in v:return None
  v,d=v.rsplit('-',1)
 return str(int(v))+'-'+txt(d) if v.isdigit() else None
sources=[]
def read(s):
 assert hashlib.sha256(Path(s['ruta']).read_bytes()).hexdigest()==s['sha256'];sources.append(s)
 w=openpyxl.load_workbook(s['ruta'],read_only=True,data_only=True);it=w[s['hoja']].iter_rows(values_only=True);h=[txt(x) for x in next(it)];out=[dict(zip(h,row)) for row in it if any(x is not None for x in row)];w.close();return h,out
_,mu=read(prior[0]);_,umas=read(prior[1]);_,old=read(prior[2]);rawheaders,raw=read(next(s for s in prior if s['ruta'].endswith('/2025/2025.xlsx')))
catp=R/'DURACION_ESTUDIOS.tsv'
with catp.open(encoding='utf-8-sig') as f:cat=list(csv.DictReader(f,delimiter='\t'))
sources.append({'ruta':str(catp),'sha256':hashlib.sha256(catp.read_bytes()).hexdigest()});cc=defaultdict(set)
for r in cat:
 for code in [r['CODCARPR_CANONICO']]+re.split('[;,|]',r['CODCARPR_ALIAS_LIST']):
  if code.strip():cc[txt(code)].add(r['CODIGO_CARRERA'])
mi=defaultdict(list);ui=defaultdict(list);oi=defaultdict(list);allcli=defaultdict(list)
for r in mu:
 if r['ANIO_INFORMADO']==2025:mi[key(r['N_DOC'],r['DV'])].append(r)
for r in umas:ui[key(r['RUT'])].append(r);allcli[txt(r['CODCLI'])].append(r)
for r in old:oi[key(r['RUT'])].append(r)
res=[];allorigcli=set();allpersons=set();targets=[]
for term in [2,3]:
 sr=[r for r in umas if txt(r['ANOINGRESO'])=='2024' and txt(r['PERIODOINGRESO'])==str(term)]
 si=defaultdict(list)
 for r in sr:si[key(r['RUT'])].append(r)
 stats=defaultdict(Counter)
 for k,ss in si.items():
  dest=[r for r in mi[k] if txt(r['ANIO_ING_ORI'])=='2025'];mapped=set().union(*(cc.get(txt(r['CODCARPR']),set()) for r in ss));dcs={txt(r['COD_CAR']) for r in dest}
  if len(mapped)!=1 or mapped!=dcs:continue
  targets.append((term,k,ss,dest));allpersons.add(k)
  origcli={txt(r['CODCLI']) for r in ss};allorigcli|=origcli;stats['numero_CODCLI_ingreso_por_persona'][str(len(origcli))]+=1
  sameprogram=[r for r in ui[k] if cc.get(txt(r['CODCARPR']),set())==mapped]
  spcli={txt(r['CODCLI']) for r in sameprogram}
  stats['numero_CODCLI_misma_carrera_en_11998'][str(len(spcli))]+=1
  stats['renovacion_mismo_CODCLI_2025']['con_fila_2025' if any(txt(r['ANOMATRICULA'])=='2025' and txt(r['CODCLI']) in origcli for r in sameprogram) else 'sin_fila_2025']+=1
  stats['otro_CODCLI_misma_carrera_ingreso2025']['si' if any(txt(r['ANOINGRESO'])=='2025' and txt(r['CODCLI']) not in origcli for r in sameprogram) else 'no']+=1
  stats['ANOMATRICULA_filas_CODCLI_origen'][' / '.join(sorted({txt(r['ANOMATRICULA']) for r in allcli[next(iter(origcli))]}))]+=1
  stats['PERIODOMATRICULA_filas_CODCLI_origen'][' / '.join(sorted({txt(r['PERIODOMATRICULA']) for r in allcli[next(iter(origcli))]}))]+=1
  stats['estado_situacion_CODCLI_origen'][' / '.join(sorted({txt(r['ESTADOACADEMICO'])+'; '+txt(r['SITUACION']) for r in ss}))]+=1
  stats['CODCLI_en_respaldo10246']['mismos_CODCLI' if {txt(r['CODCLI']) for r in oi[k] if txt(r['ANOINGRESO'])=='2024' and txt(r['PERIODOINGRESO'])==str(term)}==origcli else 'difiere']+=1
  stats['mismo_CODCLI_11998_poblacion_personas']['sin_colision_persona' if all({key(r['RUT']) for r in allcli[c]}=={k} for c in origcli) else 'colision']+=1
  stats['CODCLI_origen_anios_ingreso'][' / '.join(sorted({txt(r['ANOINGRESO']) for c in origcli for r in allcli[c]}))]+=1
  stats['CODCLI_origen_periodos_ingreso'][' / '.join(sorted({txt(r['PERIODOINGRESO']) for c in origcli for r in allcli[c]}))]+=1
 res.append({'periodo':term,'personas':sum(stats['numero_CODCLI_ingreso_por_persona'].values()),'conteos':{f:dict(v) for f,v in stats.items()}})
trace=[]
for rel in ['control/campos_ing_trace_long.tsv','resultados/campos_ing_trace_long.tsv','control/for_ing_act_trace_long.tsv','resultados/for_ing_act_trace_long.tsv']:
 p=R/rel
 if not p.exists():continue
 with p.open(encoding='utf-8-sig') as f:
  rd=csv.DictReader(f,delimiter='\t');header=rd.fieldnames;cts=Counter();cli_seen=set()
  for row in rd:
   if txt(row.get('CODCLI')) in allorigcli:
    cli_seen.add(txt(row['CODCLI']))
    cts[tuple((name,txt(row.get(name))) for name in ['ANOINGRESO','PERIODOINGRESO','ANIO_ING_ACT','SEM_ING_ACT','ANIO_ING_ORI','SEM_ING_ORI','ANIO_ING_ORI_REGLA','ANIO_ING_ORI_FUENTE','FOR_ING_ACT'] if name in header)]+=1
 trace.append({'ruta':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'CODCLI_objetivo_encontrados':len(cli_seen),'columnas':header,'conteos':[{'campos':dict(k),'filas':v}for k,v in cts.items()]})
result={'fecha':datetime.datetime.now().astimezone().isoformat(),'fuentes':sources,'grupos':res,'personas_distintas':len(allpersons),'CODCLI_origen_distintos':len(allorigcli),'RAW_MU2025_tiene_CODCLI':'CODCLI' in rawheaders,'trazas_motor':trace,'privacidad':'Sin identificadores individuales en salidas. Identificadores solo en memoria.'}
assert [x['personas'] for x in res]==[41,42]
(P/'RESULTADOS_CODCLI_AGREGADOS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='fuentes'},ensure_ascii=False,indent=2))
