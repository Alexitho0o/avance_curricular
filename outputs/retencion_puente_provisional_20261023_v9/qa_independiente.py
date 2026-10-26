import json,hashlib,ast
from pathlib import Path
from collections import Counter
R=Path.cwd();O=Path(__file__).parent;T=Path('/tmp/ipss_validacion_2165_20261023');load=lambda p:json.load(open(p));r=load(T/'resultados.json');v8=load('/tmp/ipss_cruce_historico_20261023/resultados.json');a=[x for x in v8 if x[20] and len(x[20].split('; '))==1 and x[17]!='TIPO_PLAN_AMBIGUO' and x[15]<=int(x[7]) and x[9]!='CODIGO_UNICO_ATRIBUCION_EXPEDIENTE' and not x[24]]
assert {x[0] for x in a}=={x[0] for x in r} and len(r)==2165
jm={'1':'D','2':'V','4':'O'};m=load(R/'data/diccionario_sies_umas/20261015/evidencia/caracterizacion_reglas_y_fuentes.json')['equivalencias_manual_fcu2026']['filas'];manual={(x['CODCARPR'],x['SEDE'],x['JORNADA']):x['CODIGO_UNICO_SIES'] for x in m};adopt=[]
for x in r:
 valid=x[7]=='2026' and manual.get((x[3],'RE',jm[x[5]]))==x[19] and x[34] and x[39] and x[40]==1 and not x[38]
 assert bool(x[44])==valid
 if valid:assert x[44]==manual[x[3],'RE',jm[x[5]]] and x[43]=='CORRESPONDENCIA_INTERNA_REGLA_VIGENTE';adopt.append(x)
 assert x[31]=='; '.join(map(str,sorted(set(int(z) for z in x[31].split('; ') if z))))
 if x[30]=='811_MU_PERSONAL_OTRO_ANO':
  years=[int(y) for y in x[31].split('; ')];before=any(y<int(x[7]) for y in years);after=any(y>int(x[7]) for y in years);assert x[32]==('AMBOS_LADOS' if before and after else 'SOLO_ANTERIOR' if before else 'SOLO_POSTERIOR');assert int(x[7]) not in years
 assert not x[35] and not x[41]
ids={x[0] for x in adopt};rem={x[1] for x in v8 if x[0] not in ids};ap={x[1] for x in adopt};assert len(adopt)==119 and len(ap)==88 and len(ap-rem)==87 and len(ap&rem)==1 and len(rem)==1751
for p,h in load(O/'FUENTES_HASHES.json').items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
q={'estado':'PASS','observaciones':2165,'grupos':dict(Counter(x[30] for x in r)),'regla_manual_2026_verificada':119,'personas_regla':88,'completas_internas':87,'parciales_internas':1,'pendiente_interno_personas':1751,'pendiente_documental_personas':1838,'fuentes_intactas':True,'canon_modificado':False}
(O/'QA_INDEPENDIENTE.json').write_text(json.dumps(q,ensure_ascii=False,indent=2));print(json.dumps(q))
