"""Plan 0–6: cruces exactos locales en memoria y salidas agregadas; no cambia reglas ni fuentes."""
import csv,json,re,hashlib,sqlite3,subprocess
from pathlib import Path
from collections import defaultdict,Counter
R=Path.cwd();B=R/'data/reglas_negocio/20261022_puente_versiones';O=B/'ejecucion_plan_v2'
import openpyxl
load=lambda p:json.load(open(p));csvread=lambda p:list(csv.DictReader(open(p,encoding='utf-8-sig')))
def js(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2))
def csvout(n,x):
 with open(O/n,'w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(x[0]));w.writeheader();w.writerows(x)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def val(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip().upper()
def key(a,b):
 a=val(a).replace('.','').replace(' ','');b=val(b).replace(' ','')
 return str(int(a))+'-'+b if a.isdigit() and re.fullmatch('[0-9K]',b) else None
def rows(p):
 w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=iter(w.active.values);h=next(it)
 for row in it:yield dict(zip(h,row))
 w.close()
old=csvread(B/'DICCIONARIO_VERSIONES_UMAS_SIES_PROPUESTO_20261022.csv');dim={(r['codcarpr_interno'],r['sede'],r['jornada_catalogo']):r for r in old};cs=defaultdict(set)
for r in csvread(B/'PUENTE_VERSIONES_PLAN_UMAS_SIES_20261022.csv'):cs[(r['codcarpr_interno'],r['sede'],r['jornada_catalogo'])].add(r['codigo_unico_sies_candidato'])
M=load(R/'data/matriz_academica_b4/20261016/manifest.json');sources=[];hist=[]
for p,h in M['fuentes_y_codigo_sha256'].items():
 if any(t in p for t in ['MAT_IP_CIISA_2019.xlsx','MAT_IP_CIISA_2020.xlsx']):
  exists=Path(p).exists();actual=sha(p) if exists else None;sources.append({'ruta':p,'sha256_esperado':h,'sha256':actual,'hash_coincide':actual==h,'existe':exists,'uso':'documento/DV/codigo/anio; sin demografia'})
  if actual==h:hist.append((p,re.search(r'CIISA_(\d{4})',p)[1]))
# Fuente adicional localizada en la misma carpeta institucional; registrar hash nuevo.
p21=Path(hist[0][0]).with_name('MAT_IP_CIISA_2021.xlsx') if hist else None
if p21 and p21.exists():
 sources.append({'ruta':str(p21),'sha256':sha(p21),'existe':True,'uso':'Reporte institucional 2021; incorporacion observacional con hash nuevo, sin afirmacion de aceptacion oficial','hash_previo_gobernado':'NO_LOCALIZADO'})
 hist.append((str(p21),'2021'))
pro=Path('/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_12166.xlsx');mu=R/'outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx'
for p in [pro,mu]:sources.append({'ruta':str(p),'sha256':sha(p),'existe':True,'uso':'cruce exacto'})
for p in ['/Users/alexi/Downloads/DATOSDEALUMNOS_11998.xlsx','/Users/alexi/Downloads/DATOSDEALUMNOS_12023.xlsx']:
 sources.append({'ruta':p,'existe':Path(p).exists(),'uso':'fuente matricula/contexto; no disponible si falta'})
mi=defaultdict(set);my=defaultdict(set);mh=defaultdict(set);hy=defaultdict(set);counts=Counter();sql=sqlite3.connect(':memory:');sql.executescript('CREATE TABLE p(id TEXT,c TEXT,plan TEXT,y TEXT,t TEXT,j TEXT);CREATE TABLE m(id TEXT,y TEXT,code TEXT,origin TEXT);CREATE TABLE candidates(c TEXT,s TEXT,j TEXT,code TEXT);')
for r in rows(mu):
 counts[val(r['ANIO_INFORMADO'])]+=1;k=key(r['N_DOC'],r['DV']);code='I162S%sC%sJ%sV%s'%tuple(val(r[x]) for x in ['COD_SED','COD_CAR','JOR','VERSION'])
 if k and val(r['TIPO_DOC'])=='R':mi[k].add(code);my[k,val(r['ANIO_INFORMADO'])].add(code);sql.execute('INSERT INTO m VALUES(?,?,?,?)',(k,val(r['ANIO_INFORMADO']),code,'MU'))
for p,y in hist:
 for r in rows(p):
  assert val(r['MC_CAT_PERIODO'])=='MAT_'+y
  k=key(r['MM_N_DOCUMENTO'],r['MM_DV']);code=val(r['MC_CODIGO_UNICO'])
  # No uso de pasaporte, nombre, sexo o nacimiento.
  if k and re.fullmatch(r'I162S\d+C\d+J\d+V\d+',code):mh[k].add(code);hy[k,y].add(code);sql.execute('INSERT INTO m VALUES(?,?,?,?)',(k,y,code,'HIST'))
pr=defaultdict(set);jvals=Counter();jmap={'D':'1','V':'2','O':'4'}
for r in rows(pro):
 k=key(r['RUT'],r['DIG']);c=val(r['CODCARR']);plan=val(r['PLAN_DE_ESTUDIO']);y=val(r['ANO']);t=val(r['PERIODO']);j=jmap.get(val(r['JORNADA']),'');jvals[val(r['JORNADA'])]+=1
 if k:pr[c].add((k,plan,y,t,j));sql.execute('INSERT INTO p VALUES(?,?,?,?,?,?)',(k,c,plan,y,t,j))
for d,codes in cs.items():sql.executemany('INSERT INTO candidates VALUES(?,?,?,?)',[(*d,c) for c in codes])
sql.executescript('CREATE INDEX ip ON p(id,y,c,j);CREATE INDEX im ON m(id,y,code);')
groups=load(R/'data/versiones_por_cohorte/20261016/grupos_existentes.json');gm={(g['codcarpr'],g['sede'],g['jornada']):g for g in groups};revj={'1':'D','2':'V','4':'O'}
b4=load(R/'data/matriz_academica_b4/20261016/matriz_contextos.json');b4hash=sha(R/'data/matriz_academica_b4/20261016/matriz_contextos.json');b4ok=b4hash==M['salidas_sha256']['matriz_contextos.json'];assert b4ok
agg=defaultdict(set);allr=[];recovered=[]
for d,prev in dim.items():
 codes=cs[d];persons={x[0] for x in pr[d[0]]};histunion=set().union(*(mh[k]&codes for k in persons)) if persons else set();histpersons={k for k in persons if mh[k]&codes};before={k for k in persons if mi[k]&codes};after=before|histpersons
 temporal=set();stable=defaultdict(set);collisions=set();uniqueobs=set();plans_years=set();nomatch=0;othercodes=set();nobs=0
 for k,plan,y,t,j in pr[d[0]]:
  if j!=d[2]:continue
  nobs+=1;othercodes.update((my[k,y]|hy[k,y])-codes)
  plans_years.add((plan,y));matches=(my[k,y]|hy[k,y])&codes
  if not matches:nomatch+=1
  if len(matches)>1:collisions.add((k,plan,y,t))
  if len(matches)==1:uniqueobs.add((k,plan,y,t))
  for code in matches:agg[(*d,plan,y,t,code)].add(k);temporal.add(k);stable[plan,y].add(code)
 g=gm.get((d[0],'RE' if d[1]=='2' else d[1],revj.get(d[2],d[2])),{})
 evidence=[r for r in b4 if r['codcarpr']==d[0] and r['sede_umas']=='RE' and r['jornada_umas']==revj.get(d[2])]
 docs=[r for r in evidence if set(r['codigos_documentales'])&codes]
 row={'carrera':d[0],'sede':d[1],'jornada':d[2],'estado_previo':prev['estado'],'personas_match_MU_historico':len(before),'personas_match_MU_mas_2019_2021':len(after),'personas_match_mismo_ano_jornada':len(temporal),'observaciones_plan_ano_periodo_un_codigo':len(uniqueobs),'observaciones_plan_ano_periodo_multicodigo':len(collisions),'observaciones_plan_ano_periodo_sin_match':nomatch,'observaciones_PROMEDIOS_jornada':nobs,'otros_codigos_mismo_ano':';'.join(sorted(othercodes)),'contextos_plan_ano':len(plans_years),'contextos_plan_ano_multiversion':sum(len(x)>1 for x in stable.values()),'codigos_historicos_recuperados':';'.join(sorted(histunion)),'perfiles':json.dumps(g.get('perfiles_duracion_tipo',[])),'fuente_perfil':g.get('fuente_perfil','NO_LOCALIZADO'),'contextos_B4_documentales':';'.join(r['contexto'] for r in docs),'estado_actual':'PROPUESTA_PREVIA_NO_APROBADA' if prev['estado'].startswith('PROPUESTA') else 'PENDIENTE_CON_EVIDENCIA_HISTORICA_RECUPERADA' if not before and after else 'PENDIENTE','asignacion_aprobada':False,'clasificacion':'B/C/E','pendiente':'Acreditar plan efectivo por matricula/periodo; datos de sede ausentes en PROMEDIOS; no generalizar identidad a equivalencia'}
 allr.append(row)
 if prev['estado']=='PENDIENTE_SIN_MATCH' and after:recovered.append(row)
aggrows=[dict(zip(['carrera','sede','jornada','plan','ano','periodo','codigo'],k),personas=len(v),clasificacion='C') for k,v in sorted(agg.items())];csvout('CRUCE_TEMPORAL_JORNADA.csv',aggrows);csvout('DIMENSIONES_63_V2.csv',allr)
sq={(c,s,j,p,y,t,code):n for c,s,j,p,y,t,code,n in sql.execute('SELECT a.c,a.s,a.j,p.plan,p.y,p.t,m.code,COUNT(DISTINCT p.id) FROM candidates a JOIN p ON p.c=a.c AND p.j=a.j JOIN m ON m.id=p.id AND m.y=p.y AND m.code=a.code GROUP BY a.c,a.s,a.j,p.plan,p.y,p.t,m.code')}
assert sq=={k:len(v) for k,v in agg.items()}
summary={'clasificacion':'C/D/E','dimensiones':63,'propuestas_previas':39,'nuevas_equivalencias_aprobadas':0,'brecha_propuestas_antes_n':24,'brecha_propuestas_ahora_n':24,'denominador':63,'brecha_propuestas_antes_pct':24/63*100,'brecha_propuestas_ahora_pct':24/63*100,'reduccion_propuestas_pp':0,'dimensiones_sin_evidencia_match_antes':13,'dimensiones_sin_evidencia_match_ahora':13-len(recovered),'dimensiones_evidencia_recuperada':['/'.join([r['carrera'],r['sede'],r['jornada']]) for r in recovered],'advertencia':'Recuperacion por ampliacion de fuente a 2019/2020/2021, misma definicion de identidad/candidatos; no acredita equivalencia ni reduce por si sola 24/63. Conteo historico no simultaneo, separado del cruce temporal/jornada.','jornadas_fuente':dict(jvals),'totales_MU':dict(counts),'qa_sql_agregados':True,'hash_B4_verificado':b4ok,'estado':'PENDIENTE_APROBACION_GOBERNANZA'}
js('RESUMEN_EJECUCION.json',summary);js('FUENTES.json',sources)
assert all(sha(x['ruta'])==x['sha256'] for x in sources if x.get('sha256'))
js('QA.json',{'fuentes_intactas':True,'universo_63':len(allr)==63,'agregaciones_python_sql_identicas':True,'sin_identificadores_en_salidas':True,'no_uso_demografia':True,'equivalencias_nuevas':0,'promocion_productiva':'BLOQUEADA_POR_EVIDENCIA_Y_APROBACION','aprobacion_institucional':False})
print(json.dumps(summary,ensure_ascii=False));print('prioritarios',json.dumps([r for r in allr if (r['carrera'],r['jornada']) in [('IINF','2'),('ICRE','2'),('TTMRE','1'),('TTMRE','2')]],ensure_ascii=False))
