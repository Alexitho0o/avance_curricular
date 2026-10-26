from pathlib import Path
from collections import Counter,defaultdict
import json,re,hashlib,datetime,importlib.util,subprocess
import openpyxl
ROOT=Path('/Users/alexi/Documents/GitHub/avance_curricular');CAR=Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN');OUT=Path(__file__).resolve().parent
BASE=ROOT/'outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def txt(v):return '' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip().upper()
def key(v,d=None):
 v=txt(v).replace('.','').replace(' ','')
 if d is None:
  if '-' not in v:return None
  v,d=v.rsplit('-',1)
 d=txt(d)
 return str(int(v))+'-'+d if re.fullmatch(r'\d+',v) and re.fullmatch('[0-9K]',d) else None
def valid(k):
 if not k:return False
 n,d=k.split('-');r=11-sum(int(c)*(2+i%6) for i,c in enumerate(n[::-1]))%11
 return d==('0' if r==11 else 'K' if r==10 else str(r))
def loose(v,d=None):
 if d is not None:return key(re.sub('[^0-9]','',txt(v)),re.sub('[^0-9K]','',txt(d)))
 v=re.sub('[^0-9K]','',txt(v));return key(v[:-1],v[-1:]) if len(v)>1 else None
def read(p,s):
 w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=w[s].iter_rows(values_only=True);h=[txt(x) for x in next(it)];rr=[dict(zip(h,r)) for r in it if any(x is not None for x in r)];w.close();return h,rr
sources=[]
def source(p,s,expected=None):
 h=sha(p)
 if expected:assert h==expected,(p,'hash distinto')
 sources.append({'ruta':str(p),'hoja':s,'sha256':h});return read(p,s)[1]
mup=BASE/'BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx'
mu=source(mup,'BASE_RETENCION_MU','19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd')
mi={y:defaultdict(list) for y in [2025,2026]};body={y:defaultdict(list) for y in mi};lm={y:defaultdict(list) for y in mi}
for r in mu:
 y=r['ANIO_INFORMADO']
 if y in mi and txt(r['TIPO_DOC'])=='R':
  k=key(r['N_DOC'],r['DV']);mi[y][k].append(r);lm[y][loose(r['N_DOC'],r['DV'])].append(r)
  if k:body[y][k.split('-')[0]].append(r)
up=CAR/'.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/DATOSDEALUMNOS_11998.xlsx'
ur=source(up,'Hoja1','5d2df5e7998a4ec903e12d51b25114e8f1ff36da57cecaf623e90398b0828f35');ui=defaultdict(list)
for r in ur:ui[key(r['RUT'])].append(r)
old=source(CAR/'.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/DATOSDEALUMNOS_10246.xlsx','Hoja1','b175d63bd9e3280c5757fb0d7292e45fb594d8f076e277f2e06bad2b15e9d869')
t2=source(Path('/Users/alexi/Downloads/cierre/Matrícula T2_2025 2.xlsx'),'T2_2025','ed5de007202df0780bb3396ad88307f4096d7c8b729005486a20d1123096d5b3')
t3=source(Path('/Users/alexi/Downloads/cierre/Matrícula T3_2025 2.xlsx'),'T3_2025','68a1cd54ee48c1e6a679c1dbb3999e12d491543e9425e81f3d0508fefdc8d6cc')
def parse_date(v):
 if isinstance(v,datetime.datetime):return v.date()
 if isinstance(v,datetime.date):return v
 for fmt in ['%d-%m-%Y','%d/%m/%Y','%Y-%m-%d','%d-%m-%Y %H:%M:%S']:
  try:return datetime.datetime.strptime(str(v).strip(),fmt).date()
  except ValueError:pass
 return None
def analyze(rows,y,t,label):
 sel=[r for r in rows if txt(r.get('ANOINGRESO'))==str(y) and txt(r.get('PERIODOINGRESO'))==str(t)]
 ks={key(r['RUT']) for r in sel if valid(key(r['RUT']))};follow=y+1
 found={k for k in ks if mi[follow].get(k)};absent=ks-found
 vg=Counter(' / '.join(sorted({txt(r['VIG']) for r in mi[follow][k]})) for k in found)
 statuses=Counter();origin_states=Counter();late=Counter();sem=Counter();ori=Counter()
 for k in absent:
  later=[r for r in ui[k] if txt(r['ANOMATRICULA'])==str(follow)]
  if not ui[k]:cl='Sin match en DatosAlumnos_11998'
  elif not later:cl=f'Sin fila ANOMATRICULA={follow} en DatosAlumnos_11998'
  elif any(txt(r['ESTADOACADEMICO'])=='VIGENTE' for r in later):cl=f'Con fila {follow} y estado VIGENTE observado'
  else:cl=f'Con fila {follow}; sin estado VIGENTE observado'
  statuses[cl]+=1
  origin_states[' / '.join(sorted({txt(r['ESTADOACADEMICO']) for r in sel if key(r['RUT'])==k}))]+=1
  if later:
   ds=[parse_date(r['FECHAMATRICULA']) for r in later]
   if all(d and d>datetime.date(follow,4,30) for d in ds):late['todas_fechas_matricula_posteriores_30abril']+=1
   elif any(d and d<=datetime.date(follow,4,30) for d in ds):late['alguna_fecha_matricula_hasta_30abril']+=1
   else:late['fechas_no_concluyentes']+=1
 for k in found:
  sem[' / '.join(sorted({txt(r['SEM_ING_ORI']) for r in mi[follow][k]}))]+=1
  ori[' / '.join(sorted({txt(r['ANIO_ING_ORI']) for r in mi[follow][k]}))]+=1
 out={'fuente':label,'ingreso':y,'periodo':t,'mu':follow,'registros_origen':len(sel),'personas_RUT_valido':len(ks),'filas_llave_invalida':sum(not valid(key(r['RUT'])) for r in sel),'repeticiones_persona':len(sel)-sum(not valid(key(r['RUT'])) for r in sel)-len(ks),'presentes':len(found),'con_alguna_VIG1':sum(any(txt(r['VIG'])=='1' for r in mi[follow][k]) for k in found),'solo_VIG0':sum(all(txt(r['VIG'])=='0' for r in mi[follow][k]) for k in found),'ausentes':len(absent),'VIG_observados_personas':dict(vg),'ausentes_rescatados_por_formato':sum(bool(lm[follow].get(k)) for k in absent),'ausentes_mismo_cuerpo_otro_DV':sum(bool(body[follow].get(k.split('-')[0])) for k in absent),'contexto_ausentes_en_11998':dict(statuses),'estados_origen_ausentes_personas':dict(origin_states),'fechas_ausentes_con_matricula_siguiente':dict(late),'sem_origen_MU_personas':dict(sem),'anio_origen_MU_personas':dict(ori)}
 assert len(ks)==len(found)+len(absent)
 return out
results=[analyze(ur,y,t,'DATOSDEALUMNOS_11998') for y in [2024,2025] for t in [1,2,3]]
sensitivity=[analyze(old,y,t,'DATOSDEALUMNOS_10246') for y in [2024,2025] for t in [1,2,3]]
fixed=[analyze(t2,2025,2,'Archivo T2_2025; denominador aprobado'),analyze(t3,2025,3,'Archivo T3_2025; denominador aprobado')]
assert [r['personas_RUT_valido'] for r in fixed]==[222,124]
assert [r['presentes'] for r in fixed]==[80,50]
secondary=[analyze(t3,2024,t,'T3_2025; ingresos 2024 observados') for t in [1,2,3]]
modulepath=ROOT/'scripts/construir_base_retencion_mu_2022_2026.py'
spec=importlib.util.spec_from_file_location('constructor_lectura',modulepath);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
inv=json.loads((BASE/'INVENTARIO_FUENTES_SHA256.json').read_text());manifest=json.loads((BASE/'MANIFEST_BASE_RETENCION_MU_2022_2026.json').read_text());cols=manifest['esquema_rector']['columnas'];checks=[]
for y in [2025,2026]:
 item=next(x for x in inv if x['anio']==y);f=Path(item['archivo']);sheet=mod.SELECTED_SOURCES[y]['sheet']
 try:
  rr=source(f,sheet,item['sha256']);vals=[[mod.typed_value(c,r.get(mod.DEMONSTRABLE_ALIASES.get(y,{}).get(c,c))) for c in cols] for r in rr]
  consolidated=[[r[c] for c in cols] for r in mu if r['ANIO_INFORMADO']==y]
  checks.append({'anio':y,'filas_original':len(rr),'filas_consolidado':len(consolidated),'contenido_32_columnas_identico':vals==consolidated,'diferencias_por_columna':dict(Counter(c for a,b in zip(vals,consolidated) for c,x,z in zip(cols,a,b) if x!=z))})
 except Exception as ex:checks.append({'anio':y,'pendiente_lectura':str(ex)})
result={'clasificacion':'B/C conteos; E causa no acreditada','fecha':datetime.datetime.now().astimezone().isoformat(),'fuentes':sources,'tabla_11998':results,'contraste_10246':sensitivity,'denominadores_fijos':fixed,'contraste_T3_2025_ingresos2024':secondary,'verificacion_consolidacion':checks,'denominadores_retencion_sin_cambios':[558,1150,222,124],'limites':['11998 y 10246 son extracciones observadas, no inventarios completos acreditados del ingreso histórico.','No equiparar período de ingreso UMAS con semestre SIES.','Una misma persona puede aparecer en más de un grupo de ingreso; no sumar grupos como personas únicas globales.','Estados posteriores describen la extracción; no prueban el motivo de ausencia ni vigencia al corte previo.','Manual MU2025 no localizado en repositorios/proyecto en búsqueda por nombre. No trasladar MU2026 como norma de 2025.'],'privacidad':'Solo agregados guardados. Identificadores únicamente en memoria; sin archivos individuales.'}
(OUT/'RESULTADOS_AGREGADOS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'tabla':[{k:r[k] for k in ['ingreso','periodo','personas_RUT_valido','presentes','con_alguna_VIG1','solo_VIG0','ausentes','filas_llave_invalida']} for r in results],'fijos':fixed,'consolidacion':checks},ensure_ascii=False,indent=2))
