"""Verifica evidencias existentes sin recalcular ni sobrescribir auditorías previas."""
from pathlib import Path
import hashlib,json,subprocess,datetime
R=Path(__file__).resolve().parents[2];O=Path(__file__).parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=R,text=True).strip()
start={'rama':git('branch','--show-current'),'head':git('rev-parse','HEAD')}
protected={f:sha(R/f) for f in git('diff','--name-only').splitlines() if (R/f).is_file()}
files=['avance_historico_fase1_20261027/MANIFEST_FASE1.json','avance_historico_origen_h113_20261027/MANIFEST_ORIGEN_H113.json','avance_historico_identidad_h113_20261027/MANIFEST.json','avance_historico_atribucion_20261027/MANIFEST.json','avance_historico_periodos_815_20261027/MANIFEST.json']
checks=[];seen=set();manifests=[];sources={}
def test(kind,loc,expected,actual):checks.append({'clase':'B/C','tipo':kind,'referencia':loc,'esperado':expected,'observado':actual,'estado':'PASS' if expected==actual else 'FAIL'})
def verify(kind,path,expected):
 path=Path(path);path=path if path.is_absolute() else R/path
 key=(str(path),expected)
 if key in seen:return
 seen.add(key)
 try:actual=sha(path)
 except OSError as e:actual=type(e).__name__
 test(kind,str(path),expected,actual)
for relative in files:
 p=R/'outputs'/relative;m=json.loads(p.read_text());manifests.append({'ruta':str(p),'sha256':sha(p)})
 for val in m.get('fuentes',{}).values():
  sources[val['ruta']]=val['sha256'];verify('fuente',val['ruta'],val['sha256'])
 for name,h in m.get('salidas',{}).items():verify('salida',p.parent/name,h)
 for x in m.get('evidencia_git',[]):
  k=(x['commit'],x['ruta'],x['sha256'])
  if k in seen:continue
  seen.add(k);actual=hashlib.sha256(subprocess.check_output(['git','show',x['commit']+':'+x['ruta']],cwd=R)).hexdigest();test('evidencia_git',x['commit']+':'+x['ruta'],x['sha256'],actual)
 if isinstance(m.get('script'),dict):verify('script',m['script']['ruta'],m['script']['sha256'])
 if isinstance(m.get('especificacion'),dict):verify('especificacion',m['especificacion']['ruta'],m['especificacion']['sha256'])
 for f,h in m.get('archivos_codigo',{}).items():verify('codigo',f,h)
 for f,v in m.get('fuentes_mu_verificadas',{}).items():sources[f]=v['sha256'];verify('fuente_mu',f,v['sha256'])
for f,h in protected.items():test('cambio_preexistente_preservado',f,h,sha(R/f))
test('rama','Git',start['rama'],git('branch','--show-current'));test('HEAD','Git',start['head'],git('rev-parse','HEAD'))
result={'fecha_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'estado':'PASS_INTEGRIDAD_EVIDENCIA' if all(x['estado']=='PASS' for x in checks) else 'BLOQUEADO','alcance':'Verificación de evidencia existente; no nueva ejecución integral del motor ni aceptación PES.','controles':checks,'fuentes_distintas':len(sources),'manifiestos':manifests,'git_antes':start,'git_despues':{'rama':git('branch','--show-current'),'head':git('rev-parse','HEAD')},'sin_commit_push':True}
(O/'QA_CIERRE_PLAN_FASE1.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'estado':result['estado'],'controles':len(checks),'fuentes_distintas':len(sources),'fallos':[c for c in checks if c['estado']!='PASS']},ensure_ascii=False,indent=2))
