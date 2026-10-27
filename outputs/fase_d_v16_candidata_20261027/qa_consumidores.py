from pathlib import Path
import json,sys,subprocess,tempfile,shutil,os
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R));from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
O=Path(__file__).parent;desc=R/'data/diccionario_sies_seguimiento/v16_20261027_candidata_sedes/descriptor.json';s=DiccionarioSiesSeguimiento(descriptor=desc);items=json.loads((Path.home()/'.local/share/ipss/fase_d_v15_candidata_20261027/NUEVAS_OBSERVACIONES_PRIVADAS.json').read_text());x=items[0];q={k:v for k,v in [('persona',x['persona']),('codcli',x['CODCLI']),('plan',x['plan']),('anio',x['ano']),('periodo',x['periodo']),('carrera',x['carrera']),('sede',x['sede_dimension']),('jornada',x['jornada_sies'])]};s.close();req=json.dumps([{'metodo':'consultar','entrada':q}]);P=Path.home()/'.local/share/ipss/fase_d_v15_302_20261027'; runners=['scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py'];answers=[]
for i,f in enumerate(runners):
 out=P/('test_v16_consumidor_'+str(i)+'.json');assert not out.exists()
 launcher="import sys,runpy;from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento as D;orig=D.__init__;D.__init__=lambda self,*a,**kw:orig(self,descriptor="+repr(str(desc))+");sys.argv=["+repr(str(R/f))+",'--salida-privada',"+repr(str(out))+"];runpy.run_path(sys.argv[0],run_name='__main__')"
 p=subprocess.run([sys.executable,'-c',launcher],input=req,text=True,capture_output=True,cwd=R);assert p.returncode==0,p.stderr;z=json.loads(out.read_text())[0];answers.append((z['codigo_sies'],z['nivel_respaldo'],z['seguimiento_promedios']['estado']))
assert len(set(answers))==1 and answers[0][0]==x['codigo_interno_adoptado']
# Una copia alterada debe ser rechazada; no se modifica base real.
with tempfile.TemporaryDirectory(dir=P) as t:
 d=json.loads(desc.read_text());bad=Path(t)/'alterada.sqlite';shutil.copyfile(d['base_privada']['ruta'],bad)
 with bad.open('ab') as f:f.write(b'ALTERACION_QA')
 d['base_privada']['ruta']=str(bad);bad_desc=Path(t)/'descriptor.json';bad_desc.write_text(json.dumps(d))
 try:DiccionarioSiesSeguimiento(descriptor=bad_desc);raise AssertionError('Base alterada aceptada')
 except ValueError as e:assert 'alterada' in str(e).lower()
res={'tres_consumidores_misma_respuesta':True,'consultas_por_consumidor':1,'capa_promedios_observacion_nueva':answers[0][2],'base_alterada_rechazada':True,'limite':'Prueba de un contexto por consumidor; con inyección de descriptor candidata, sin cambiar activo.'};(O/'QA_CONSUMIDORES_V16.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps(res))
