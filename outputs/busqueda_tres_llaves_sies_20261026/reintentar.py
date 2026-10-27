"""Reintenta fuentes de matrícula y avance que agotaron tiempo; no exporta nombres."""
import concurrent.futures,json,os,subprocess,sys,unicodedata,collections
from pathlib import Path
OUT=Path(__file__).resolve().parent
PRIVATE=Path('/Users/alexi/.local/share/ipss/busqueda_tres_llaves_sies_20261026')
items=json.loads((PRIVATE/'INVENTARIO_PRIVADO.json').read_text())
def relevant(item):
 if item.get('error')!='Timeout':return False
 p=Path(item['ruta']); parts=p.parts
 if 'Enviados' not in parts:return False
 label=unicodedata.normalize('NFC',parts[parts.index('Enviados')+1])
 return label in {'Avance Curricular','Matrícula Unificada'}
items=[x for x in items if relevant(x)]
def one(item):
 try:
  p=subprocess.run([sys.executable,str(OUT/'buscar.py'),'--uno',item['ruta']],capture_output=True,text=True,timeout=35)
  r=json.loads(p.stdout) if p.returncode==0 else {'error':'Subproceso'}
 except subprocess.TimeoutExpired:r={'error':'Timeout'}
 except (OSError,ValueError):r={'error':'RespuestaInvalida'}
 return {'ruta':item['ruta'],**r}
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:r=list(pool.map(one,items))
path=PRIVATE/'REINTENTO_PRIVADO.json';fd=os.open(path,os.O_CREAT|os.O_WRONLY|os.O_TRUNC,0o600)
with os.fdopen(fd,'w') as f:json.dump(r,f,ensure_ascii=False,indent=2)
c=collections.Counter()
for x in r:
 c['reintentados']+=1
 if x.get('error'):c['error_'+x['error']]+=1
 else:
  c['leidos']+=1
  for k in ['codcli','rut_y_dv_juntos','rut_sin_dv']:
   if x[k]:c['candidatos_'+k]+=1
out={'clasificacion':'C reintento literal; E acceso o coincidencia de fila','conteos':dict(c),'detalle_privado':str(path),'limites':'Resultados a nivel de archivo, no fila; no se comprueban hashes anteriores ni se modifica la fuente.'}
(OUT/'RESUMEN_REINTENTO.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
