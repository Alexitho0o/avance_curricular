import json,hashlib
from pathlib import Path
from collections import Counter
R=Path.cwd();O=Path(__file__).parent;T=Path('/tmp/ipss_cohorte_original_20261023');load=lambda p:json.load(open(p));src=R/'data/versiones_historicas_sies_umas/fase_b_20261015/perfiles_sies_anuales.json';p=load(src);d={(x['anio'],x['codigo_unico']):x for x in p};r=load(T/'retrospectiva_privada.json');groups={(g['codcarpr'],g['sede'],g['jornada']):g for g in load(R/'data/versiones_por_cohorte/20261016/grupos_existentes.json')};jm={'1':'D','2':'V','4':'O'};tp={'Plan Regular':'1','Plan Especial':'2','Plan Regular de Continuidad':'3'};counts=Counter()
def positive(x):
 try:return float(x.replace(',','.'))>0
 except:return False
for x in r:
 if x[7]!='MU_INGRESO_ACTUAL' or x[9]!='REGULAR':continue
 g=groups[x[2],'RE',jm[x[3]]];cs=[]
 for z in p:
  q=z['campos_originales']
  if z['anio']==x[8] and z['codigo_unico'].rsplit('V',1)[0] in g['familias'] and [q['Duración Total'],tp.get(q['Tipo Carrera'])] in g['perfiles_duracion_tipo'] and q['Vigencia']=='Vigente con estudiantes nuevos' and any(positive(q[t]) for t in ['Vacantes Semestre Uno','Vacantes Semestre Dos']):cs.append(z['codigo_unico'])
 out='ACIERTO' if len(cs)==1 and cs[0]==x[12] else 'ERROR' if len(cs)==1 else 'EMPATE' if len(cs)>1 else 'SIN_CANDIDATO';counts[out]+=1
cand=load(T/'candidatos.json');extended=[]
for x in cand:
 z=d[x[1],x[2]];q=z['campos_originales'];extended.append(x+[q['Año Inicio'],q['Vacantes Semestre Uno'],q['Vacantes Semestre Dos'],q['Requisito Ingreso'],q['Semestres reconocidos'],z['registro_csv']])
(T/'candidatos_ampliados.json').write_text(json.dumps(extended,ensure_ascii=False));q={'fuente':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'prueba_regular_MU_actual_nuevos_mas_vacantes_positivas':dict(counts),'uso':'Prueba de sensibilidad, no regla de asignacion ni ausencia de matricula por vacantes0','ejemplo_C3J4_2022':[{'codigo':code,'registro_csv':d[2022,code]['registro_csv'],'campos':{k:d[2022,code]['campos_originales'][k] for k in ['Año Inicio','Vigencia','Vacantes Semestre Uno','Vacantes Semestre Dos','Requisito Ingreso','Semestres reconocidos']}} for code in ['I162S2C3J4V1','I162S2C3J4V2']]};(O/'VACANTES.json').write_text(json.dumps(q,ensure_ascii=False,indent=2));print(json.dumps(q))
