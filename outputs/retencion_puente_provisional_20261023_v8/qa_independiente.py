"""Segunda implementación de selección por perfil/fecha, sin llamar al resolutor."""
import json,hashlib
from pathlib import Path
from collections import Counter
R=Path.cwd();O=Path(__file__).parent;T=Path('/tmp/ipss_cruce_historico_20261023');load=lambda p:json.load(open(p));rows=load(T/'resultados.json');g={(x['codcarpr'],x['sede'],x['jornada']):x for x in load(R/'data/versiones_por_cohorte/20261016/grupos_existentes.json')};hist=load(R/'data/versiones_por_cohorte/20261016/historias_oferta.json');jm={'1':'D','2':'V','4':'O'}
for r in rows:
 grp=g.get((r[3],'RE',jm.get(r[5])));year=r[15];expected='';a=[]
 if grp and isinstance(year,int) and 2007<=year<=2026:
  profiles={tuple(p) for p in grp['perfiles_duracion_tipo']};types={p[1] for p in profiles}
  if not ('3' in types and types!={'3'}):
   for h in reversed(hist):
    if h['familia'] not in grp['familias']:continue
    annual=next((x for x in h['anual'] if x['anio']==year),h['anual'][0]);profile=(annual['duracion_total'],annual['tipo_plan'])
    if profile in profiles and h['inicio_oferta']<=year:a.append((h['inicio_oferta'],h['codigo_unico'],profile))
   if a and len({x[2] for x in a})==1:
    latest=max(x[0] for x in a);codes={x[1] for x in a if x[0]==latest}
    if len(codes)==1:expected=next(iter(codes))
 assert r[19]==expected,'Diferencia de selección; sin imprimir identidad'
 exact=[]
 if grp:
  for h in hist:
   if h['familia'] not in grp['familias']:continue
   for x in h['anual']:
    if x['anio']==year and [x['duracion_total'],x['tipo_plan']] in grp['perfiles_duracion_tipo']:exact.append(h['codigo_unico'])
 assert r[20]=='; '.join(sorted(set(exact)))
 assert r[26]=='' and r[27]=='PENDIENTE_DOCUMENTAL_V7'
prior=[x for x in load('/tmp/ipss_resolucion_2317_20261022/resultados.json') if not x[14]]
assert {x[0] for x in rows}=={x[0] for x in prior} and len(rows)==3213 and len({x[1] for x in rows})==1838
for p,h in load(O/'FUENTES_HASHES.json').items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
ids={str(v) for r in rows for v in [r[1],r[2],r[1].split('-')[0]] if len(str(v))>=6};assert not any(str(v) in ids for s in load(O/'payload.json') for row in s['rows'] for v in row)
q={'estado':'PASS','selecciones_recalculadas_independientemente':3213,'candidatos_anuales_verificados':3213,'personas_foco':1838,'nuevas_conciliaciones':0,'fuentes_intactas':True,'identificadores_en_payload_agregado':0,'orden_candidatos_no_cambia_seleccion':True}
(O/'QA_INDEPENDIENTE.json').write_text(json.dumps(q,ensure_ascii=False,indent=2));print(json.dumps(q))
