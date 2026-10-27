"""Resguarda entregas históricas duplicadas y las mueve a Papelera reversiblemente."""
import datetime,hashlib,json,os,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent;DESK=Path.home()/'Desktop'
DEST=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/08_HISTORICO_RETENCION/20261026_provisionales')
TRASH=Path.home()/'.Trash'/('IPSS_entregas_20261026_'+datetime.datetime.now().strftime('%H%M%S'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
entries=[
 ('RETENCION_INTERMEDIA_IPSS_REVISION_20261021_133221.xlsx','retencion_intermedia_t2_t3/20261021_133221'),
 ('RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261024_V17.xlsx','pendientes_entrega_20261024_v17'),
 ('RETENCION_IPSS_DICCIONARIO_APLICADO_20261023_V12.xlsx','aplicacion_diccionario_intertrimestral_20261023_125556'),
 ('RETENCION_IPSS_PUENTE_REPRODUCIDO_20261023_V11.xlsx','reproduccion_puente_20261023_004044'),
 ('RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261023_V16.xlsx','aclaracion_tasas_2026_20261023_v16'),
 ('RETENCION_INTERMEDIA_IPSS_PRESENCIAS_Y_PENDIENTES_20261021_085902.xlsx','retencion_intermedia_t2_t3/20261021_085902'),
 ('REVISION_RETENCION_INTERMEDIA_IPSS_2024_2025_20261021.xlsx','retencion_intermedia_t2_t3/20261021_013430'),
 ('RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261023_V15.xlsx','correccion_proxy_t3_2025_20261023_v15'),
 ('RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261023_V14.xlsx','correccion_proxy_t2_2025_20261023_v14'),
 ('RETENCION_INTERMEDIA_IPSS_ESCENARIO_80_20261021_100654.xlsx','retencion_intermedia_t2_t3/20261021_100654'),
 ('RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261023_V13.xlsx','seguimiento_t1_hasta_2026_20261023_v13'),
 ('RETENCION_INTERMEDIA_IPSS_MAQUETA_T1_20261021_153436.xlsx','retencion_intermedia_t2_t3/20261021_153436')]
if not DEST.is_dir():raise SystemExit('No existe respaldo OneDrive esperado')
items=[]
for name,folder in entries:
 p=DESK/name;ref=ROOT/'outputs'/folder/name
 if not p.is_file() or not ref.is_file() or sha(p)!=sha(ref):raise SystemExit('No hay copia coincidente para '+name)
 if (DESK/('~$'+name)).exists():raise SystemExit('Archivo abierto: '+name)
 dst=DEST/name;digest=sha(ref)
 if dst.exists() and sha(dst)!=digest:raise SystemExit('Destino diferente: '+name)
 if not dst.exists():shutil.copy2(ref,dst)
 assert sha(dst)==digest;items.append({'origen':str(p),'proyecto':str(ref),'onedrive':str(dst),'sha256':digest})
log=OUT/'LIMPIEZA_ENTREGAS_DUPLICADAS_20261026.json';record={'clasificacion':'D autorización; C respaldo y papelera','fecha':datetime.datetime.now().astimezone().isoformat(),'estado':'RESPALDOS_VERIFICADOS','sync_remoto_onedrive':'NO_VERIFICADO','items':items,'reubicaciones':[]};log.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');TRASH.mkdir(mode=0o700)
for x in items:
 p=Path(x['origen']);t=TRASH/p.name
 if t.exists() or sha(p)!=x['sha256'] or sha(Path(x['proyecto']))!=x['sha256'] or sha(Path(x['onedrive']))!=x['sha256']:raise SystemExit('Copias cambiaron: '+p.name)
 os.rename(p,t);assert sha(t)==x['sha256'];record['reubicaciones'].append({'origen':str(p),'papelera':str(t),'sha256':x['sha256']});log.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
record['estado']='MOVIDOS_A_PAPELERA';log.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'copias_a_papelera':len(items),'respaldo_onedrive':str(DEST),'papelera':str(TRASH),'sync_remoto':'NO_VERIFICADO'},ensure_ascii=False))
