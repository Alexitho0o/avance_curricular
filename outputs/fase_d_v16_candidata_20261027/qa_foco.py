from pathlib import Path
from collections import defaultdict
import json,sys,re
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R));p=R/'outputs/avance_historico_atribucion_20261027/auditar_atribucion.py';n={'__file__':str(p)};exec(compile(p.read_text().split("with (OUT/'PARTICION_POR_CODIGO.csv')")[0],str(p),'exec'),n)
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento
old=n['service'];new=DiccionarioSiesSeguimiento(descriptor=R/'data/diccionario_sies_seguimiento/v16_20261027_candidata_sedes/descriptor.json');cache=n['cache'];assert len(cache)==5144
before={};after={};changed=0
for k,v in cache.items():
 pe,cli,plan,car,jor,year,period=k;before[k]=bool(v.get('codigo_sies'));z=new.consultar(persona=pe,codcli=cli,plan=plan,anio=year,periodo=period,carrera=car)
 if z['estado']=='REUTILIZABLE':
  mm=re.fullmatch(r'I\d+S(\d+)C\d+J(\d+)V\d+',z['codigo_sies']);allowed=n['journeys'].get((car,mm[1],jor),set()) if mm else set()
  if not mm or allowed!={mm[2]}:z={'codigo_sies':None}
 after[k]=bool(z.get('codigo_sies'));changed+=before[k]!=after[k]
def stats(d):
 ps=defaultdict(list);ex=defaultdict(list)
 for k,v in d.items():ps[k[0]].append(v);ex[(k[0],k[1],k[3])].append(v)
 return {'contextos_pendientes':sum(not v for v in d.values()),'personas_totalmente_pendientes':sum(not any(x) for x in ps.values()),'expedientes_totalmente_pendientes':sum(not any(x) for x in ex.values()),'personas':len(ps),'expedientes':len(ex)}
a,b=stats(before),stats(after);res={'contextos':len(cache),'v15':a,'v16':b,'contextos_con_cambio_pendiente':changed,'metodo':'Consulta sin sede como consumidor del foco, con control de jornada existente; no altera población.'};(Path(__file__).parent/'QA_FOCO.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps(res,ensure_ascii=False));old.close();new.close()
