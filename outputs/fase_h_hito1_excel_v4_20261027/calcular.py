from pathlib import Path
from collections import defaultdict,Counter
import json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R));p=R/'outputs/avance_historico_atribucion_20261027/auditar_atribucion.py';n={'__file__':str(p)};exec(compile(p.read_text().split("with (OUT/'PARTICION_POR_CODIGO.csv')")[0],str(p),'exec'),n)
P=Path.home()/'.local/share/ipss';rows=json.load(open(P/'fase_f_hito1_20261027/DETALLE_PRIVADO.json'));g=json.load(open(P/'fase_g_hito1_20261027/DETALLE_PRIVADO.json'));mapping={}
def key(x):return tuple(str(x[z]) for z in ['persona','codcli','plan','carrera','jornada','anio','periodo'])
for x in rows:mapping[key(x)]=x
for x in g:
 k=key(x) if 'jornada' in x else None
 # G rows omit jornada; match full source by remaining identifying fields
 if k is None:
  hits=[kk for kk in mapping if kk[0:4]==tuple(str(x[z]) for z in ['persona','codcli','plan','carrera']) and kk[5:]==(str(x['anio']),str(x['periodo']))];assert len(hits)==1;k=hits[0]
 mapping[k]['g_sin_mu_siguiente']='SIN_MU_ANIO_SIGUIENTE_EN_FUENTES_REVISADAS' in x['faltantes']
groups=defaultdict(lambda:{'contextos':0,'personas':set(),'expedientes':set()});unrecognized=0
for k,v in n['cache'].items():
 if v.get('codigo_sies'):continue
 x=mapping.get(k)
 if not x:label='Diplomados: motivo no desglosado (8)'
 else:
  mu=x['mu']
  if mu=='SOLO_OTRO_EXPEDIENTE':label='Solo otro expediente en MU'
  elif mu=='SIN_MU_PERSONA_ANIO_EN_INDICE_Y_RESPALDOS_REVISADOS' and x.get('g_sin_mu_siguiente'):label='Sin MU del año ni siguiente en fuentes revisadas'
  elif mu=='COMPARTIDAS_SIN_DESAMBIGUAR':label='Familias compartidas sin desambiguar'
  else:label='Otros pendientes con motivo registrado'
 g=groups[label];g['contextos']+=1;g['personas'].add(k[0]);g['expedientes'].add((k[0],k[1],k[3]))
assert sum(x['contextos'] for x in groups.values())==545
out=[{'motivo':k,'contextos':v['contextos'],'expedientes':len(v['expedientes']),'personas':len(v['personas'])} for k,v in groups.items()];(Path(__file__).parent/'MOTIVOS_AGREGADOS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False));n['service'].close()
