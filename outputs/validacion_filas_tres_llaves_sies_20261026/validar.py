"""Valida en filas los candidatos del barrido; no escribe identificadores personales."""
import collections,csv,hashlib,json,os,re,subprocess,sys,unicodedata
from pathlib import Path
import openpyxl

OUT=Path(__file__).resolve().parent
PRIVATE=Path('/Users/alexi/.local/share/ipss/busqueda_tres_llaves_sies_20261026')
CASE=Path('/Users/alexi/.local/share/ipss/revision_21_ramos_4_expedientes_20261026/DETALLE_CUATRO_CASOS_V2.json')
def norm(v):
 if isinstance(v,float) and v.is_integer():return str(int(v))
 return str(v or '').strip().upper()
def clean(v):return norm(v).replace('.','').replace(' ','')
case=next(x for x in json.loads(CASE.read_text()) if any(y['carrera']=='TCRE' for y in x['contextos_v11']))
codes={norm(x['CODCLI']) for x in case['datosalumnos'] if x['CODCLI']}; assert len(codes)==3
body,dv=case['RUT'].split('-');body=str(int(body));dv=dv.upper()
docnames={'RUT','RUT2','RUT3','N_DOC','N_DOC2','N_DOC_2','NUM_DOCUMENTO','NUMERO_DOCUMENTO','RUT_ALUMNO','RUT_NORMALIZADO','RUT_ALU','RUT_ESTUDIANTE'}
dvnames={'DV','DIG','DIGITO','D_V','DV_ALU','DIG_VERIFICADOR','DIGITO_VERIFICADOR'}
plannames={'PLAN_DE_ESTUDIO','PLAN_DE_ESTUDIOS','PLAN_ESTUDIOS','PLAN_ESTUDIO','CODIGO_PLAN_ESTUDIO','PLAN'}
titlenames={'TITULO','NOMBRE_TITULO','NOMBRE_TITULO_OBTENIDO','FECHA_OBT_TIT_GRA','FECHA_TITULACION','FECHA_OBTENCION_TITULO','COD_SIES_OBT_TIT'}

def analyze_sheet(iterator):
 header=None; counts=collections.Counter(); shapes={}; rows=0
 for row in iterator:
  rows+=1; vals=[norm(v) for v in row]
  vset=set(vals)
  if rows<=15 and (vset & (docnames|{'CODCLI','CODCLI2'})):
   header=vals
   shapes={'campos_codcli':sum(v in {'CODCLI','CODCLI2'} for v in vals),'campos_documento':sum(v in docnames for v in vals),
           'campos_dv':sum(v in dvnames for v in vals),'campos_plan':sum(v in plannames for v in vals),'campos_titulo':sum(v in titlenames for v in vals)}
   continue
  if not header:continue
  exactcodes={v for v in vals if v in codes}
  docs=[clean(v) for i,v in enumerate(row) if i<len(header) and header[i] in docnames]
  dvs=[clean(v) for i,v in enumerate(row) if i<len(header) and header[i] in dvnames]
  hasbody=False; hasfull=False
  for raw in docs:
   pieces=raw.split('-'); rbody=pieces[0]
   if rbody.isdigit() and str(int(rbody))==body:
    hasbody=True
    if (len(pieces)==2 and pieces[1]==dv) or (len(pieces)==1 and dv in dvs):hasfull=True
  if exactcodes:counts['filas_codcli']+=1
  if hasbody:counts['filas_cuerpo_rut']+=1
  if hasfull:counts['filas_rut_dv']+=1
  if hasbody and not hasfull:counts['filas_cuerpo_sin_dv']+=1
  if exactcodes and hasfull:counts['filas_codcli_y_rut_dv']+=1
  if exactcodes and hasbody and not hasfull:counts['filas_codcli_y_cuerpo_sin_dv']+=1
 return {'filas_examinadas':rows,'cabecera_detectada':bool(header),'campos':shapes,'conteos':dict(counts)}

def inspect(path):
 found=[]
 if path.suffix.lower() in {'.xlsx','.xlsm'}:
  w=openpyxl.load_workbook(path,read_only=True,data_only=True)
  for sheet in w:
   result=analyze_sheet(sheet.iter_rows(values_only=True))
   if any(result['conteos'].values()):found.append({'hoja':sheet.title,**result})
  w.close()
 else:
  for encoding in ['utf-8-sig','cp1252']:
   try:
    with path.open('r',encoding=encoding,newline='') as f:
     line=f.readline(65536);sep=max([',',';','\t'],key=line.count);f.seek(0)
     result=analyze_sheet(csv.reader(f,delimiter=sep))
    break
   except UnicodeDecodeError:continue
  else:raise UnicodeError('encoding')
  if any(result['conteos'].values()):found.append({'hoja':'CSV/TSV',**result})
 return {'hojas_con_match':found}

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()

if len(sys.argv)==4 and sys.argv[1]=='--uno':
 try:
  path=Path(sys.argv[2]);expected=sys.argv[3]
  assert sha(path)==expected
  result=inspect(path)
  assert sha(path)==expected
  result['hash_antes_despues_coincide']=True
  print(json.dumps(result,ensure_ascii=False))
 except Exception as e:print(json.dumps({'error':type(e).__name__}))
 sys.exit(0)

inventory=json.loads((PRIVATE/'INVENTARIO_PRIVADO.json').read_text())
retry=PRIVATE/'REINTENTO_PRIVADO.json'
if retry.exists():
 inventory.extend(x for x in json.loads(retry.read_text()) if not x.get('error'))
files=[x for x in inventory if any(x.get(k) for k in ('codcli','rut_y_dv_juntos','rut_sin_dv'))]
def one(x):
 try:
  p=subprocess.run([sys.executable,__file__,'--uno',x['ruta'],x['sha256']],capture_output=True,text=True,timeout=45)
  data=json.loads(p.stdout) if p.returncode==0 else {'error':'Subproceso'}
 except subprocess.TimeoutExpired:data={'error':'Timeout'}
 except (OSError,ValueError):data={'error':'RespuestaInvalida'}
 return {'ruta':x['ruta'],'sha256_barrido':x['sha256'],**data}
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: results=list(pool.map(one,files))
PRIVATE.mkdir(parents=True,mode=0o700,exist_ok=True)
dest=PRIVATE/'VALIDACION_FILAS_PRIVADA.json';fd=os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
with os.fdopen(fd,'w') as f:json.dump(results,f,ensure_ascii=False,indent=2)
counts=collections.Counter()
for r in results:
 counts['archivos_candidatos']+=1
 if 'error' in r:counts['error_'+r['error']]+=1;continue
 counts['archivos_leidos']+=1
 for key in ['filas_codcli','filas_rut_dv','filas_cuerpo_rut','filas_cuerpo_sin_dv','filas_codcli_y_rut_dv','filas_codcli_y_cuerpo_sin_dv']:
  if any(s['conteos'].get(key,0) for s in r['hojas_con_match']):counts['archivos_con_'+key]+=1
 for s in r['hojas_con_match']:
  if s['campos'].get('campos_codcli') and s['campos'].get('campos_plan') and s['campos'].get('campos_titulo'):counts['hojas_con_las_tres_columnas_y_match']+=1
out={'clasificacion':'B datos; C cruce exacto; E atribución', 'conteos':dict(counts),
     'detalle_privado':str(dest), 'limites':'Las cabeceras se detectan solo en primeras 15 filas. Se procesan solo candidatos de barrido literal; celdas con fórmulas sin caché, documentos con otro formato y archivos no leídos pueden perderse. Conteos por archivo no son personas ni hechos independientes.'}
(OUT/'RESUMEN_AGREGADO.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
