from pathlib import Path
import hashlib,json,subprocess,shutil,datetime,sys
R=Path('/Users/alexi/Documents/GitHub/avance_curricular'); O=R/'outputs/auditoria_diccionario_sies_20261025/fase4_20261025';G=O/'git_candidato';B=O/'respaldo_activacion';B.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(R),*args],text=True).strip()
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
p=json.loads((O/'PAQUETE_PUBLICACION.json').read_text());assert git('branch','--show-current')=='feature/ire-2026';assert git('rev-parse','HEAD')=='55e3b709afb9483f0ecdd2d166f67229a454a5ef';assert not git('diff','--cached','--name-only')
for f,h in p['git_archivos'].items():assert sha(G/f)==h,f
assert sha(Path(p['plugin']['archivo']))==p['plugin']['sha256']
assert sha(Path(p['skill_local']['ruta_original']))==p['skill_local']['sha256_previo']
assert sha(R/'data/diccionario_sies_seguimiento/activo.json')=='a041fa4d8c1cd25006959fc2b05089eab396f9b684cb35c942e7263343890497'
# Preserve working state, including unrelated files, without printing individual contents.
files=git('ls-files','--modified','--others','--exclude-standard','-z').split('\0')
others={f:sha(R/f) for f in files if f and f not in p['git_archivos'] and not f.startswith('outputs/auditoria_diccionario_sies_20261025/') and (R/f).is_file() and not (R/f).is_symlink()}
wr(B/'otros_hashes.json',others)
for f in p['git_archivos']:
 if (R/f).is_file():
  dst=B/'checkout'/f;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/f,dst)
shutil.copy2(O/'PAQUETE_PUBLICACION.json',B/'PAQUETE_PREVIO.json')
alert='data/diccionario_sies_seguimiento/v8_20261025_ocho_p/ALERTA_PROMOCION.json';a=json.loads((G/alert).read_text());a.update(clasificacion='D autorización; C ejecución',estado='PROMOCION_AUTORIZADA_Y_APLICADA',responsable_aprobacion='Alexi, usuario de este chat',fecha_aprobacion=datetime.datetime.now().astimezone().isoformat(),autorizacion='Respuesta explícita «si» al alcance de fase4: activar v8, commit/push de 23 archivos y actualizar complemento/skill.',responsable_ejecucion='Codex');wr(G/alert,a)
for f in p['git_archivos']:
 if f=='PROYECTO_IPSS.json':continue
 dst=R/f;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(G/f,dst)
# PROYECTO already contains pointer entry; preserve the two unrelated keys locally.
cur=json.loads((R/'PROYECTO_IPSS.json').read_text());target=json.loads((G/'PROYECTO_IPSS.json').read_text());assert cur['recursos_comunes']['diccionario_sies_seguimiento']==target['recursos_comunes']['diccionario_sies_seguimiento']
# All staged paths explicit. Stage project blob from approved candidate without touching working copy.
subprocess.run(['git','-C',str(R),'add','--',*[f for f in p['git_archivos'] if f!='PROYECTO_IPSS.json']],check=True)
blob=git('hash-object','-w',str(G/'PROYECTO_IPSS.json'));subprocess.run(['git','-C',str(R),'update-index','--add','--cacheinfo','100644',blob,'PROYECTO_IPSS.json'],check=True)
assert set(git('diff','--cached','--name-only').splitlines())==set(p['git_archivos'])
local=Path(p['skill_local']['ruta_original']);shutil.copy2(local,B/'SKILL_ANTES.md');shutil.copy2(Path(p['skill_local']['candidata']),local)
ref=Path(p['skill_local']['referencia_destino']);ref.parent.mkdir(parents=True,exist_ok=True)
if ref.exists():shutil.copy2(ref,B/'REFERENCIA_ANTES.md')
shutil.copy2(O/'skill_local_candidata/diccionario-sies-seguimiento.md',ref)
for f,h in others.items():assert sha(R/f)==h,f
wr(O/'ACTIVACION_AUTORIZADA.json',{'fecha':a['fecha_aprobacion'],'clasificacion':'D/C','HEAD_antes':git('rev-parse','HEAD'),'archivos':{f:sha(G/f) for f in p['git_archivos']},'otros_archivos_preservados':len(others),'skill_instalada':str(local),'commit_push':'pendiente QA activo'})
print(json.dumps({'activado':'v8_20261025_ocho_p','staged':len(p['git_archivos']),'otros_archivos_preservados':len(others),'skill_instalada':True}))
