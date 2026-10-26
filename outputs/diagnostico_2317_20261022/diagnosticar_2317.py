import json,csv,hashlib
from pathlib import Path
from collections import defaultdict,Counter
R=Path.cwd();O=R/'outputs/diagnostico_2317_20261022';P=Path('/tmp/ipss_revision_63_20261022/payload.json');x=json.load(open(P));old=json.load(open('/tmp/ipss_revision_privada_20261022/payload_v2.json'));get=lambda a,n:next(s for s in a if s['name']==n)
u=get(x,'CONTRASTE_63')['rows'];e=get(x,'EVIDENCIAS_SIES')['rows'];labels={'CONTRADICCION_O_ATRIBUCION_MULTIPLE':'a_alternativas','SIN_EVIDENCIA_ANUAL_APLICABLE':'b_sin_anual','CODIGO_ANUAL_SIN_CONTEXTO_DA_EXACTO':'c_sin_DA','DIFIERE_CODIGO_PROPUESTO_OBSERVADO':'e_difiere_propuesta'};focus=[r for r in u if r[10] in labels];assert len(focus)==4973 and len({r[0] for r in focus})==2317
names=defaultdict(set)
for sn in ['DA_12159','DA_11248']:
 s=get(x,sn)
 for row in s['rows']:
  d=dict(zip(s['headers'],row));names[str(d['CODCARPR'])].add(str(d['NOMBRE_L']))
def aggregate(rows,keys):
 groups=defaultdict(list)
 for r in rows:groups[tuple(r[i] for i in keys)].append(r)
 out=[]
 for key,rr in sorted(groups.items()):out.append(list(key)+[len({r[0] for r in rr}),len({(r[2],r[1]) for r in rr}),len(rr)])
 return out
def save(name,headers,rows):
 with open(O/name,'w',encoding='utf-8-sig',newline='') as f:w=csv.writer(f);w.writerow(headers);w.writerows(rows)
byc=aggregate(focus,[2]);byj=aggregate(focus,[4]);byy=aggregate(focus,[6]);detail=aggregate(focus,[2,6,4]);byc=[r[:1]+[' / '.join(sorted(names[r[0]]))]+r[1:] for r in byc];detail=[r[:1]+[' / '.join(sorted(names[r[0]]))]+r[1:] for r in detail]
save('POR_CARRERA.csv',['carrera','nombre','personas','expedientes','observaciones'],byc);save('POR_ANO.csv',['ano','personas','expedientes','observaciones'],byy);save('POR_JORNADA.csv',['jornada','personas','expedientes','observaciones'],byj);save('CARRERA_ANO_JORNADA.csv',['carrera','nombre','ano','jornada','personas','expedientes','observaciones'],detail)
cat=[]
for state,label in labels.items():
 rr=[r for r in focus if r[10]==state];cat.append([label,len({r[0] for r in rr}),len({(r[2],r[1]) for r in rr}),len(rr)])
save('CATEGORIAS.csv',['categoria','personas','expedientes','observaciones'],cat)
# Partición disjunta de observaciones sin anual; para personas prioridad misma familia > otra familia > ninguna.
b=[r for r in focus if r[10]=='SIN_EVIDENCIA_ANUAL_APLICABLE'];sub=defaultdict(list)
for r in b:sub['MISMA_FAMILIA_OTRO_ANO_PROCESO' if r[12] else 'SOLO_OTRA_FAMILIA' if r[11] else 'SIN_CODIGO_NINGUNA_FUENTE'].append(r)
pclasses={};personb=defaultdict(list)
for r in b:personb[r[0]].append(r)
for k,rr in personb.items():pclasses[k]='MISMA_FAMILIA_OTRO_ANO_PROCESO' if any(r[12] for r in rr) else 'SOLO_OTRA_FAMILIA' if any(r[11] for r in rr) else 'SIN_CODIGO_NINGUNA_FUENTE'
subrows=[[k,len(v),len({r[0] for r in v}),sum(z==k for z in pclasses.values())] for k,v in sub.items()];save('CAUSAS_SIN_ANUAL.csv',['causa','observaciones','personas_en_causa_solapables','personas_particion_priorizada'],subrows)
# Identificación de solapamientos y multicararrera dentro del universo focalizado.
pc=defaultdict(set);py=defaultdict(set);pj=defaultdict(set)
for r in focus:pc[r[0]].add(r[2]);py[r[0]].add(r[6]);pj[r[0]].add(r[4])
# Comparación estricta de los mismos 504 y 508 expedientes.
oldp=get(old,'PERSONAS_504')['rows'];p504={r[0] for r in oldp};hits=defaultdict(set)
for r in e:
 if r[4]=='COMPLETO':hits[r[0]].add(r[3])
exactsets=all(hits[r[0]]==set(r[3].split('; ')) if r[3] else not hits[r[0]] for r in oldp)
oldexp=get(old,'APLICABILIDAD_EXPEDIENTE')['rows'];dims=json.load(open(R/'data/reglas_negocio/20261022_puente_versiones/investigacion_contextual_v3/PRUEBAS_CONTEXTUALES.json'));fam={r['carrera']+'/J'+r['jornada']:set(r['familias']) for r in dims};expcompare=[]
for r in oldexp:
 now={c for c in hits[r[0]] if c.rsplit('V',1)[0] in fam[r[2]]};was=set(r[6].split('; ')) if r[6] else set();expcompare.append(now==was)
oldobs=get(old,'OBSERVACIONES')['rows'];current={(r[0],r[1],r[2]+'/J'+r[4],r[5],r[6],r[7]):r for r in u};cmp=Counter()
for r in oldobs:
 if r[1] not in p504:continue
 k=(r[1],r[2],r[0],r[3],r[4],r[5]);now=current.get(k);was=set(r[7].split('; ')) if r[7] else set();after=set(now[9].split('; ')) if now and now[9] else set();cmp['observaciones_comparadas']+=1;cmp['conjuntos_iguales']+=was==after;cmp['antes_con_codigo']+=bool(was);cmp['ahora_con_codigo']+=bool(after)
prior=[r for r in u if r[8]];priorstats={'personas':len({r[0] for r in prior}),'expedientes':len({(r[2],r[1]) for r in prior}),'observaciones':len(prior),'resultados':dict(Counter(r[10] for r in prior))}
contr=[r for r in focus if r[10]=='CONTRADICCION_O_ATRIBUCION_MULTIPLE'];contypes=Counter('VARIOS_CODIGOS_ANUALES' if len(r[9].split('; '))>1 else 'UN_CODIGO_PERO_ATRIBUCION_MULTIPLE_IDENTIDAD_EXPEDIENTE' for r in contr)
# Fuentes y años no se vuelven a buscar; contar coincidencias históricas sobre índices V3.
flags=Counter();bfam={r[0]:[] for r in b}
for r in b:
 if r[12]:
  matched=[v for v in e if v[0]==r[0] and v[4]=='COMPLETO' and v[3].rsplit('V',1)[0] in fam[r[2]+'/J'+r[4]]]
  flags['observaciones_con_matricula_otra_fecha']+=any(v[1]=='MATRICULA' for v in matched)
  flags['observaciones_con_avance']+=any(v[1]=='AVANCE_CURRICULAR' for v in matched)
  flags['observaciones_con_titulados']+=any(v[1]=='TITULADOS' for v in matched)
q={'universo_personas':5901,'foco_personas':2317,'foco_observaciones':4973,'categorias':cat,'sin_anual_particion':subrows,'sin_anual_presencia_procesos_no_sumable':dict(flags),'personas_multicarrera_foco':sum(len(v)>1 for v in pc.values()),'personas_multiano_foco':sum(len(v)>1 for v in py.values()),'personas_multijornada_foco':sum(len(v)>1 for v in pj.values()),'contradicciones_desglose':dict(contypes),'comparacion_504':{'personas':504,'antes_con_codigo':497,'ahora_con_codigo':sum(bool(hits[k]) for k in p504),'conjunto_codigos_identico':exactsets,'expedientes':508,'antes_misma_familia':500,'ahora_misma_familia':sum(bool({c for c in hits[r[0]] if c.rsplit('V',1)[0] in fam[r[2]]}) for r in oldexp),'conjuntos_familia_identicos':all(expcompare),'observaciones':dict(cmp)},'propuestas_previas_39':priorstats,'principales_carreras':sorted(byc,key=lambda r:r[-3],reverse=True)[:10],'por_ano':byy,'por_jornada':byj}
assert sum(r[1] for r in subrows)==3112 and sum(r[3] for r in subrows)==1821
assert exactsets and all(expcompare) and cmp['observaciones_comparadas']==cmp['conjuntos_iguales']
(O/'DIAGNOSTICO.json').write_text(json.dumps(q,ensure_ascii=False,indent=2));print(json.dumps(q,ensure_ascii=False))
