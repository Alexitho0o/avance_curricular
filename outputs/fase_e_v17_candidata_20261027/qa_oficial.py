from pathlib import Path
import json,sys,subprocess,tempfile,shutil
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R));from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento
from common.seguimiento_promedios_v11 import CapaPromedios as OldLayer
from common.seguimiento_promedios import CapaPromedios as NewLayer
O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_e_v17_candidata_20261027';dp=R/'data/diccionario_sies_seguimiento/v17_20261027_candidata_promedios/descriptor.json';old=DiccionarioSiesSeguimiento.__new__(DiccionarioSiesSeguimiento);import sqlite3; old.edicion='v16_aislada';old.descriptor=json.loads((R/'data/diccionario_sies_seguimiento/v16_20261027_candidata_sedes/descriptor.json').read_text());old.root=R;old.db=sqlite3.connect(Path(old.descriptor['base_privada']['ruta']).as_uri()+'?mode=ro',uri=True);new=DiccionarioSiesSeguimiento(descriptor=dp);before=OldLayer(old);after=NewLayer(new);assert before.problema is None and after.problema is None
rr=old.db.execute('select * from observaciones order by id').fetchall();same=0
for r in rr:
 oid,pe,cli,plan,year,period,car,sed,jor,payload=r;q=dict(persona=pe,codcli=cli,plan=plan,anio=year,periodo=period,carrera=car,sede=sed,jornada=jor);a=old.consultar(**q);b=new.consultar(**q);a.pop('edicion',None);b.pop('edicion',None);assert a==b
 if oid<=25902:assert before.data[oid]==after.data[oid]
 else:assert oid not in before.data and oid in after.data
 same+=1
assert len(after.data)==26930 and len(before.data)==25902
req=[]
for lo,hi in [(1,25902),(25903,26628),(26629,26930)]:
 selected=0
 for r in rr:
  oid,pe,cli,plan,year,period,car,sed,jor,payload=r
  if not lo<=oid<=hi:continue
  q=dict(persona=pe,codcli=cli,plan=plan,anio=year,periodo=period,carrera=car,sede=sed,jornada=jor);z=new.consultar(**q)
  if z.get('estado')!='REUTILIZABLE':continue
  req.append({'metodo':'consultar','entrada':q});selected+=1
  if selected==20:break
 assert selected==20,(lo,selected)
answers=[]
for i,f in enumerate(['scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py']):
 out=P/('QA_OFICIAL_CONSUMIDOR_'+str(i)+'.json');assert not out.exists();launcher="import sys,runpy;from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento as D;orig=D.__init__;D.__init__=lambda self,*a,**kw:orig(self,descriptor="+repr(str(dp))+");sys.argv=["+repr(str(R/f))+",'--salida-privada',"+repr(str(out))+"];runpy.run_path(sys.argv[0],run_name='__main__')";p=subprocess.run([sys.executable,'-c',launcher],input=json.dumps(req),text=True,capture_output=True,cwd=R);assert p.returncode==0,p.stderr;z=json.loads(out.read_text());assert len(z)==60 and all(y['seguimiento_promedios']['estado']=='DISPONIBLE' for y in z);answers.append(z)
assert answers[0]==answers[1]==answers[2]
with tempfile.TemporaryDirectory(dir=P) as t:
 d=json.loads(dp.read_text());base=Path(t)/'alterada.sqlite';shutil.copyfile(d['base_privada']['ruta'],base)
 with base.open('ab') as f:f.write(b'ALTERACION_QA')
 d['base_privada']['ruta']=str(base);bad=Path(t)/'descriptor.json';bad.write_text(json.dumps(d))
 try:DiccionarioSiesSeguimiento(descriptor=bad);raise AssertionError('Base alterada aceptada')
 except ValueError as e:assert 'alterada' in str(e).lower()
res={'consultas_codigos_sin_cambio':same,'capa_anterior_preservada':25902,'capa_agregada':1028,'cobertura_capas':len(after.data),'consumidores':3,'muestra_por_consumidor':60,'muestra_por_grupo':{'anteriores':20,'fase_c':20,'fase_e':20},'respuestas_iguales':True,'capa_disponible_en_muestra':True,'base_alterada_rechazada':True,'limites':'Muestra no exhaustiva; fuentes con cobertura y fechas no certificadas.'};(O/'QA_COMPONENTES_OFICIALES.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps(res));old.close();new.close()
