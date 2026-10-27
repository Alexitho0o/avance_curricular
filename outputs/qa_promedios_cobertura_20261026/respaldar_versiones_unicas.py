"""Conserva versiones únicas en privado y OneDrive antes de mover originales a Papelera."""
import datetime,hashlib,json,os,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent;DESK=Path.home()/'Desktop'
LOCAL=ROOT/'.local_restricted/archivos_retencion_20261026';REMOTE=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/08_HISTORICO_RETENCION/20261026_provisionales')
TRASH=Path.home()/'.Trash'/('IPSS_versiones_20261026_'+datetime.datetime.now().strftime('%H%M%S'))
names=['RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V18_CANDIDATA.xlsx','RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V19_TRAZABLE.xlsx','RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V22.xlsx','RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V23.xlsx']
if subprocess.run(['git','check-ignore','-q',str(LOCAL/'prueba.xlsx')],cwd=ROOT).returncode!=0:raise SystemExit('Respaldo local no excluido de Git')
if not REMOTE.is_dir():raise SystemExit('Respaldo OneDrive no disponible')
LOCAL.mkdir(parents=True,exist_ok=True,mode=0o700)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
items=[]
for name in names:
 src=DESK/name
 if not src.is_file() or (DESK/('~$'+name)).exists():raise SystemExit('Falta o está abierto: '+name)
 digest=sha(src);loc=LOCAL/name;rem=REMOTE/name
 for dst in (loc,rem):
  if dst.exists() and sha(dst)!=digest:raise SystemExit('Destino distinto: '+str(dst))
  if not dst.exists():shutil.copy2(src,dst)
  if sha(dst)!=digest:raise SystemExit('Copia no coincide: '+str(dst))
 items.append({'origen':str(src),'respaldo_local_ignorado':str(loc),'onedrive':str(rem),'sha256':digest})
log=OUT/'LIMPIEZA_VERSIONES_UNICAS_20261026.json';record={'clasificacion':'D autorización; C copia verificada y papelera','fecha':datetime.datetime.now().astimezone().isoformat(),'estado':'RESPALDOS_VERIFICADOS','sync_remoto_onedrive':'NO_VERIFICADO','items':items,'reubicaciones':[]};log.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');TRASH.mkdir(mode=0o700)
for x in items:
 src=Path(x['origen']);dst=TRASH/src.name
 if dst.exists() or any(sha(Path(x[k]))!=x['sha256'] for k in ('origen','respaldo_local_ignorado','onedrive')):raise SystemExit('Copias cambiaron: '+src.name)
 os.rename(src,dst);assert sha(dst)==x['sha256'];record['reubicaciones'].append({'origen':str(src),'papelera':str(dst),'sha256':x['sha256']});log.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
record['estado']='MOVIDOS_A_PAPELERA';log.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'copias_a_papelera':len(items),'respaldo_privado':str(LOCAL),'respaldo_onedrive':str(REMOTE),'papelera':str(TRASH),'sync_remoto':'NO_VERIFICADO'},ensure_ascii=False))
