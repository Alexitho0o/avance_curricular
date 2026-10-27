from pathlib import Path
from collections import defaultdict
import json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R));p=R/'outputs/avance_historico_atribucion_20261027/auditar_atribucion.py';n={'__file__':str(p)};exec(compile(p.read_text().split("with (OUT/'PARTICION_POR_CODIGO.csv')")[0],str(p),'exec'),n)
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento
old=n['service'];new=DiccionarioSiesSeguimiento(descriptor=R/'data/diccionario_sies_seguimiento/v15_20261027_candidata_302/descriptor.json');cache=n['cache'];assert len(cache)==5144
cases=json.loads((Path.home()/'.local/share/ipss/fase_d_v15_candidata_20261027/NUEVAS_OBSERVACIONES_PRIVADAS.json').read_text());lookup={(x['persona'],x['CODCLI'],x['plan'],x['carrera'],x['ano'],x['periodo']):x for x in cases};before={};after={}
for k,v in cache.items():
 pe,cli,plan,car,jor,year,period=k;before[k]=bool(v.get('codigo_sies'));item=lookup.get((pe,cli,plan,car,year,period));after[k]=before[k]
 if item:
  z=new.consultar(persona=pe,codcli=cli,plan=plan,anio=year,periodo=period,carrera=car,sede=item['sede_dimension'],jornada=item['jornada_sies']);after[k]=bool(z.get('codigo_sies'))
def stats(d):
 persons=defaultdict(list);exps=defaultdict(list)
 for k,v in d.items():persons[k[0]].append(v);exps[(k[0],k[1],k[3])].append(v)
 return {'contextos_pendientes':sum(not v for v in d.values()),'personas_totalmente_pendientes':sum(not any(v) for v in persons.values()),'expedientes_totalmente_pendientes':sum(not any(v) for v in exps.values()),'personas':len(persons),'expedientes':len(exps)}
a=stats(before);b=stats(after);res={'contextos_foco':len(cache),'antes':a,'despues':b,'contextos_cambiados':sum(before[k]!=after[k] for k in before),'metodo':'Reutiliza clasificación validada v14 y solo actualiza 302 contextos aprobados; la pertenencia al foco no cambia.'};(Path(__file__).parent/'QA_FOCO.json').write_text(json.dumps(res,indent=2,ensure_ascii=False)+'\n');print(json.dumps(res,ensure_ascii=False));old.close();new.close()
