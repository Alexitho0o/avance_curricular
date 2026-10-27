"""Respalda y mueve a Papelera copias provisionales verificadas por SHA-256."""
import datetime,hashlib,json,os,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
ONEDRIVE=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES')
ARCHIVE=ONEDRIVE/'08_HISTORICO_RETENCION/20261026_provisionales'
TRASH=Path.home()/'.Trash'/('IPSS_provisionales_20261026_'+datetime.datetime.now().strftime('%H%M%S'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
items=[]
for n in range(1,11):
 date='20261022' if n<=7 else '20261023';suffix='' if n==1 else '_V'+str(n);name='RETENCION_IPSS_PROVISIONAL_PUENTE_'+date+suffix+'.xlsx';dirname='retencion_puente_provisional_'+date+('' if n==1 else '_v'+str(n));reference=ROOT/'outputs'/dirname/name
 if not reference.is_file():raise SystemExit('Referencia de proyecto no disponible: '+name)
 digest=sha(reference);copies=[Path.home()/root/name for root in ('Desktop','Downloads')]
 if any(not p.is_file() or sha(p)!=digest for p in copies):raise SystemExit('Copias no son idénticas: '+name)
 items.append({'archivo':name,'sha256':digest,'proyecto':str(reference),'copias_origen':[str(x) for x in copies]})
if not ONEDRIVE.is_dir():raise SystemExit('Carpeta destino no disponible')
ARCHIVE.mkdir(parents=True,exist_ok=True)
for x in items:
 dst=ARCHIVE/x['archivo'];src=Path(x['proyecto'])
 if dst.exists():
  if sha(dst)!=x['sha256']:raise SystemExit('Archivo de destino distinto: '+dst.name)
 else:shutil.copy2(src,dst)
 if sha(dst)!=x['sha256']:raise SystemExit('Copia no verificada: '+dst.name)
 x['copia_onedrive']=str(dst)
log=OUT/'LIMPIEZA_PROVISIONALES_20261026.json';record={'clasificacion':'D autorización de limpieza; C copias y movimiento','fecha':datetime.datetime.now().astimezone().isoformat(),'estado':'RESPALDOS_VERIFICADOS','sync_remoto_onedrive':'NO_VERIFICADO','items':items,'reubicaciones':[],'pendientes':'Sin cambios a libros activos, fuentes originales o denominadores.'};log.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
TRASH.mkdir(mode=0o700)
for x in items:
 for srcstr in x['copias_origen']:
  src=Path(srcstr);dst=TRASH/(src.parent.name+'__'+src.name)
  if dst.exists() or sha(src)!=x['sha256'] or sha(Path(x['proyecto']))!=x['sha256'] or sha(Path(x['copia_onedrive']))!=x['sha256']:raise SystemExit('Estado cambió; detener antes de mover: '+src.name)
  os.rename(src,dst);assert sha(dst)==x['sha256'];record['reubicaciones'].append({'origen':str(src),'papelera':str(dst),'sha256':x['sha256']});log.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
record['estado']='MOVIDOS_A_PAPELERA';log.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'versiones':len(items),'copias_a_papelera':len(record['reubicaciones']),'respaldo_onedrive':str(ARCHIVE),'papelera':str(TRASH),'sincronizacion_remota':'NO_VERIFICADA'},ensure_ascii=False))
