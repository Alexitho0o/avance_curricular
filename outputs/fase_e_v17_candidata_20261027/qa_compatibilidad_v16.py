from pathlib import Path
import tempfile,subprocess,json,shutil,hashlib,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R));from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
from common.seguimiento_promedios import CapaPromedios
O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_e_v17_candidata_20261027';desc=R/'data/diccionario_sies_seguimiento/v16_20261027_candidata_sedes/descriptor.json';d=json.loads(desc.read_text());meta=R/d['capa_promedios']['metadata'];assert sha256(meta)==d['capa_promedios']['sha256']
with tempfile.TemporaryDirectory(dir=P) as tmp:
 root=Path(tmp);official=['common/diccionario_sies_seguimiento.py','common/seguimiento_promedios_v11.py','common/seguimiento_promedios.py','scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py']
 for f in official:
  dest=root/f;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/f,dest)
 mpath=root/d['capa_promedios']['metadata'];mpath.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(meta,mpath)
 # In isolated test descriptor, pin the updated official files and neutral component; base and v16 metadata remain unchanged.
 d['componentes_sha256']={f:sha256(root/f) for f in official};tp=root/'descriptor.json';tp.write_text(json.dumps(d));s=DiccionarioSiesSeguimiento(root=root,descriptor=tp);layer=CapaPromedios(s);assert layer.problema is None
 rr=s.db.execute('select persona,codcli,plan,anio,periodo,carrera,sede,jornada from observaciones where id<=25902 order by id').fetchall();qs=[]
 for r in rr:
  q=dict(zip(['persona','codcli','plan','anio','periodo','carrera','sede','jornada'],r));z=s.consultar(**q)
  if z['estado']=='REUTILIZABLE' and layer.consultar(z)['estado']=='DISPONIBLE':qs.append(q)
  if len(qs)==60:break
 assert len(qs)==60;s.close();req=json.dumps([{'metodo':'consultar','entrada':q} for q in qs]);answers=[]
 for i,f in enumerate(['scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py']):
  out=P/('QA_COMPAT_V16_'+str(i)+'.json');assert not out.exists();launcher="import sys,runpy;from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento as D;orig=D.__init__;D.__init__=lambda self,*a,**kw:orig(self,root="+repr(str(root))+",descriptor="+repr(str(tp))+");sys.argv=["+repr(str(R/f))+",'--salida-privada',"+repr(str(out))+"];runpy.run_path(sys.argv[0],run_name='__main__')";p=subprocess.run([sys.executable,'-c',launcher],input=req,text=True,cwd=R,capture_output=True);assert p.returncode==0,p.stderr;z=json.loads(out.read_text());assert len(z)==60 and all(x['seguimiento_promedios']['estado']=='DISPONIBLE' for x in z);answers.append(z)
 assert answers[0]==answers[1]==answers[2]
 # Validate original v16 descriptor unaltered in isolation using its committed components.
 for f,expected in json.loads(desc.read_text())['componentes_sha256'].items():
  dest=root/f;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(subprocess.check_output(['git','show','HEAD:'+f],cwd=R));assert sha256(dest)==expected
 original=DiccionarioSiesSeguimiento(root=root,descriptor=desc);original.close()
res={'tres_consumidores':3,'muestra_por_consumidor':60,'misma_respuesta':True,'capa_v16_disponible':True,'formato':'sha256_base_v11','descriptor_prueba_rehash_aislado':True,'descriptor_v16_original_con_componentes_git_valido':True,'limite':'Formato y muestra probados en entorno aislado; el descriptor activo v16 requiere componentes originales hasta activar v17.'};(O/'QA_COMPATIBILIDAD_V16.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps(res,ensure_ascii=False))
