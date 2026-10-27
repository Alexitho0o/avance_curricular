"""Reintenta fuentes no leídas; reserva los detalles de coincidencias individualizadas."""
import collections,concurrent.futures,csv,json,os,subprocess,sys,unicodedata
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
PRIVATE=Path('/Users/alexi/.local/share/ipss/busqueda_tres_llaves_sies_20261026')
initial=json.loads((PRIVATE/'INVENTARIO_PRIVADO.json').read_text())
retry={x['ruta']:x for x in json.loads((PRIVATE/'REINTENTO_PRIVADO.json').read_text())}
pending=[retry.get(x['ruta'],x) for x in initial if 'error' in x and 'error' in retry.get(x['ruta'],x)]
assert len(pending)==12

def one(item):
 path=Path(item['ruta']); name=unicodedata.normalize('NFC',path.name)
 if name=='Matrícula_Ed_Superior_2023_PUBL_MRUN.csv':
  try:
   with path.open('r',encoding='utf-8-sig',newline='') as f:fields=[x.strip().upper() for x in next(csv.reader(f,delimiter=';'))]
   return {'ruta':str(path),'estado':'estructura_mrun','contiene_mrun':'MRUN' in fields,
           'contiene_rut':'RUT' in fields,'contiene_codcli':'CODCLI' in fields,
           'limite':'Sin llave RUT o CODCLI; no se cruza MRUN con RUT ni se leyeron filas.'}
  except Exception as e:return {'ruta':str(path),'error':type(e).__name__}
 try:
  proc=subprocess.run([sys.executable,str(ROOT/'outputs/busqueda_tres_llaves_sies_20261026/buscar.py'),'--uno',str(path)],capture_output=True,text=True,timeout=90)
  found=json.loads(proc.stdout) if proc.returncode==0 else {'error':'Subproceso'}
 except subprocess.TimeoutExpired:found={'error':'Timeout'}
 except (OSError,ValueError):found={'error':'RespuestaInvalida'}
 if 'error' not in found and any(found.get(k) for k in ['codcli','rut_y_dv_juntos','rut_sin_dv']):
  try:
   v=subprocess.run([sys.executable,str(ROOT/'outputs/validacion_filas_tres_llaves_sies_20261026/validar.py'),'--uno',str(path),found['sha256']],capture_output=True,text=True,timeout=90)
   found['validacion_filas']=json.loads(v.stdout) if v.returncode==0 else {'error':'Subproceso'}
  except subprocess.TimeoutExpired:found['validacion_filas']={'error':'Timeout'}
  except (OSError,ValueError):found['validacion_filas']={'error':'RespuestaInvalida'}
 return {'ruta':str(path),**found}

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:res=list(pool.map(one,pending))
p=PRIVATE/'REINTENTO_12_PRIVADO.json';fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
with os.fdopen(fd,'w') as f:json.dump(res,f,ensure_ascii=False,indent=2)
c=collections.Counter()
for r in res:
 c['archivos']+=1
 if r.get('error'):c['error_'+r['error']]+=1;continue
 if r.get('estado')=='estructura_mrun':c['solo_estructura_mrun']+=1;continue
 c['leidos']+=1
 for k in ['codcli','rut_y_dv_juntos','rut_sin_dv']:
  if r.get(k):c['candidatos_'+k]+=1
 if 'validacion_filas' in r:
  v=r['validacion_filas']
  if v.get('error'):c['validacion_error_'+v['error']]+=1
  else:
   c['validados_filas']+=1
   for k in ['filas_codcli','filas_rut_dv','filas_cuerpo_sin_dv']:
    if any(s['conteos'].get(k,0) for s in v.get('hojas_con_match',[])):c['archivos_con_'+k]+=1
   for s in v.get('hojas_con_match',[]):
    fields=s['campos']
    if fields.get('campos_codcli') and fields.get('campos_plan') and fields.get('campos_titulo'):c['hojas_titulo_codcli_plan']+=1
summary={'clasificacion':'B fuente; C verificación; E atribución y no leídos',
         'conteos':dict(c),'detalle_privado':str(p),
         'limites':'CSV MRUN solo se revisó estructuralmente, sin cruzar RUT–MRUN; se descartan macros/formatos no soportados; coincidencias entre archivos pueden duplicarse. Los timeouts no acreditan su causa.'}
(OUT/'RESUMEN_AGREGADO.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False))
