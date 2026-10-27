from pathlib import Path
import json,sys,subprocess,tempfile,shutil,sqlite3
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento
O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_g_v19_candidata_20261027';dp=R/'data/diccionario_sies_seguimiento/v19_20261027_candidata_fase_g/descriptor.json'
s=DiccionarioSiesSeguimiento(descriptor=dp);rows=s.db.execute('select * from observaciones order by id').fetchall();ids={x['observacion_id'] for x in json.loads((P/'ADJUDICACIONES_PRIVADAS.json').read_text())};req=[]
for group in ('nuevas','actualizadas','anteriores'):
 n=0
 for r in rows:
  oid,pe,cli,plan,year,period,car,sed,jor,payload=r
  if not ((group=='nuevas' and oid>27148) or (group=='actualizadas' and oid in ids) or (group=='anteriores' and oid<25903 and oid not in ids)):continue
  q=dict(persona=pe,codcli=cli,plan=plan,anio=year,periodo=period,carrera=car,sede=sed,jornada=jor)
  if s.consultar(**q).get('estado')!='REUTILIZABLE':continue
  req.append({'metodo':'consultar','entrada':q});n+=1
  if n==20:break
 assert n==20,(group,n)
answers=[]
for i,f in enumerate(['scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py']):
 out=P/('QA_CONSUMIDOR_V19_ACTIVA_'+str(i)+'.json'); launcher="import sys,runpy;sys.argv=["+repr(str(R/f))+",'--salida-privada',"+repr(str(out))+"];runpy.run_path(sys.argv[0],run_name='__main__')"
 p=subprocess.run([sys.executable,'-c',launcher],input=json.dumps(req),text=True,capture_output=True,cwd=R);assert p.returncode==0,p.stderr
 z=json.loads(out.read_text());assert len(z)==60 and all(y['seguimiento_promedios']['estado']=='DISPONIBLE' for y in z);answers.append(z)
assert answers[0]==answers[1]==answers[2]
with tempfile.TemporaryDirectory(dir=P) as t:
 d=json.loads(dp.read_text());base=Path(t)/'alterada.sqlite';shutil.copyfile(d['base_privada']['ruta'],base)
 with base.open('ab') as f:f.write(b'ALTERACION_QA')
 d['base_privada']['ruta']=str(base);bad=Path(t)/'descriptor.json';bad.write_text(json.dumps(d))
 try:DiccionarioSiesSeguimiento(descriptor=bad);raise AssertionError('Base alterada aceptada')
 except ValueError as e:assert 'alterada' in str(e).lower()
s.close();result={'consumidores':3,'muestra_por_consumidor':60,'grupos':{'nuevas':20,'actualizadas':20,'anteriores':20},'respuestas_identicas':True,'capa_disponible':True,'base_alterada_rechazada':True};(O/'QA_CONSUMIDORES_ACTIVA.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
