from pathlib import Path
import sys,json,subprocess
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R));from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento
from common.seguimiento_promedios import CapaPromedios
O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_e_v17_candidata_20261027';s=DiccionarioSiesSeguimiento();assert s.edicion=='v17_20261027_candidata_promedios';layer=CapaPromedios(s);assert layer.problema is None;rr=s.db.execute('select * from observaciones order by id').fetchall();req=[]
for lo,hi in [(1,25902),(25903,26628),(26629,26930)]:
 selected=0
 for r in rr:
  oid,pe,cli,plan,year,period,car,sed,jor,payload=r
  if not lo<=oid<=hi:continue
  q=dict(persona=pe,codcli=cli,plan=plan,anio=year,periodo=period,carrera=car,sede=sed,jornada=jor);z=s.consultar(**q)
  if z.get('estado')!='REUTILIZABLE':continue
  req.append({'metodo':'consultar','entrada':q});selected+=1
  if selected==20:break
 assert selected==20
answers=[]
for i,f in enumerate(['scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py']):
 out=P/('QA_REAL_'+str(i)+'.json');assert not out.exists();p=subprocess.run([sys.executable,str(R/f),'--salida-privada',str(out)],input=json.dumps(req),text=True,capture_output=True,cwd=R);assert p.returncode==0,p.stderr;z=json.loads(out.read_text());assert len(z)==60 and all(y['seguimiento_promedios']['estado']=='DISPONIBLE' for y in z);answers.append(z)
assert answers[0]==answers[1]==answers[2];res={'edicion':s.edicion,'puntero_real':True,'muestra_por_grupo':{'anteriores':20,'fase_c':20,'fase_e':20},'consumidores':3,'consultas_totales':180,'respuestas_iguales':True,'capa_disponible':True};(O/'QA_CONSUMIDORES_ACTIVO.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps(res));s.close()
