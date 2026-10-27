from pathlib import Path
from collections import defaultdict
import json,sys,re
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R));p=R/'outputs/avance_historico_atribucion_20261027/auditar_atribucion.py';n={'__file__':str(p)};exec(compile(p.read_text().split("with (OUT/'PARTICION_POR_CODIGO.csv')")[0],str(p),'exec'),n)
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento
old=n['service'];new=DiccionarioSiesSeguimiento(descriptor=R/'data/diccionario_sies_seguimiento/v18_20261027_candidata_fase_f/descriptor.json');cache=n['cache'];assert len(cache)==5144
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
a,b=stats(before),stats(after)
private=json.loads((Path.home()/'.local/share/ipss/fase_f_hito1_20261027/DETALLE_PRIVADO.json').read_text())
known={(x['persona'],x['codcli'],x['plan'],x['carrera'],x['jornada'],str(x['anio']),str(x['periodo'])) for x in private}
missing={k for k,v in before.items() if not v and k not in known}
assert len(missing)==8, len(missing)
parallel_before={k:v for k,v in before.items() if k not in missing};parallel_after={k:v for k,v in after.items() if k not in missing}
res={'contextos':len(cache),'v17':a,'v18':b,'contextos_con_cambio_pendiente':changed,'paralelo_excluye_ocho_contextos_diplomados':{'contextos':len(parallel_before),'v17':stats(parallel_before),'v18':stats(parallel_after)},'metodo':'Misma consulta de foco y control de jornada; exclusión paralela de los ocho pendientes omitidos del Hito 1.'}
(Path(__file__).parent/'QA_FOCO.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps(res,ensure_ascii=False));old.close();new.close()
