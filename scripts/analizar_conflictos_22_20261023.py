"""Revisa grupos anuales conflictivos; no adjudica códigos ni modifica fuentes."""
from pathlib import Path
import sys,json,collections,hashlib,csv,itertools,subprocess,datetime
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
O=R/'outputs/conflictos_22_errores_6_20261023_161400';prior=R/'outputs/auditoria_metodos_puente_20261023_155309'
load=lambda p:json.loads(Path(p).read_text())
def dump(n,o): (O/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
s=DiccionarioSiesSeguimiento()
assert s.edicion=='v7_20261023_inf35_03_t3'
assert sha256(s.descriptor['base_privada']['ruta'])=='625b9b9d449906b38be23b7c8ad6c7f4a762f43eab9f52f0bc71fe50a5cdb38e'
rows=[json.loads(x[0]) for x in s.db.execute('select payload from observaciones')];s.close()
fields=['ano','carrera','sede_dimension','jornada_sies','plan']
def key(r):return tuple(str(r[k]) for k in fields)
def akey(r):return (r['persona'],r['CODCLI'],*key(r))
def one(xs):
 vals={str(x).strip() for x in xs if x is not None and str(x).strip() not in ('','None')}
 return next(iter(vals)) if len(vals)==1 else 'MULTIPLE' if vals else 'AUSENTE'
def validyear(x):return str(x) if str(x).isdigit() and 1950<=int(str(x))<=2027 else 'AUSENTE_O_INVALIDO'
pg=[r for r in load(prior/'GRUPOS_MULTICODIGO.json') if r['llave']=='K2_mas_plan'];gids={tuple(r['variables'][k] for k in ['ano','carrera','sede','jornada','plan']):f'G{i:02d}' for i,r in enumerate(pg,1)}
annual=collections.defaultdict(list);traj=collections.defaultdict(list)
for r in rows:
 traj[(r['persona'],r['CODCLI'],r['carrera'])].append(r)
 if r['codigo_documental_atribuible']:annual[akey(r)].append(r)
obs=[]
for ak,rr in annual.items():
 if key(rr[0]) not in gids:continue
 r=rr[0];codes={x['codigo_documental_atribuible'] for x in rr};assert len(codes)==1
 history=traj[r['persona'],r['CODCLI'],r['carrera']];yr=int(r['ano']);sameplan=[x for x in history if x['plan']==r['plan']]
 das=list({(x['fuente'],x['hoja'],x['fila']):x for z in rr for x in z['contextos_DA']}.values())
 mus=list({(x['fuente'],x['hoja'],x['fila']):x for z in rr for x in z['evidencias_matricula'] if x['codigo']==next(iter(codes))}.values())
 feature={}
 for field in ['ANOINGRESO','PERIODOINGRESO','ANOMATRICULA','PERIODOMATRICULA']:
  feature['DA_'+field]=one(x.get(field) for x in das)
 for name,field in [('MU_INGRESO_ACTUAL','ingreso_actual'),('MU_INGRESO_ORIGEN','ingreso_origen'),('MU_REINCORPORACION','reincorporacion')]:feature[name]=one(x.get(field) for x in mus)
 for name in ['DA_ANOINGRESO','DA_ANOMATRICULA','MU_INGRESO_ACTUAL','MU_INGRESO_ORIGEN']:feature[name]=validyear(feature[name])
 feature['PRIMER_ANIO_ACTIVIDAD_EXPEDIENTE']=str(min(int(x['ano']) for x in history))
 feature['PRIMER_ANIO_ACTIVIDAD_PLAN']=str(min(int(x['ano']) for x in sameplan))
 feature['N_PLANES_DISTINTOS_ANTERIORES']=str(len({x['plan'] for x in history if int(x['ano'])<yr and x['plan']!=r['plan']}))
 feature['PLAN_DISTINTO_ANTES']='SI' if feature['N_PLANES_DISTINTOS_ANTERIORES']!='0' else 'NO'
 actividad=[f for z in rr for f in z['fuentes_promedios']]
 feature['SOLO_HOMOLOGACIONES_ANIO']='AUSENTE' if not actividad else 'SI' if all(f.get('estado_ramo') in ('CONVALIDACION','HOMOLOGADO') for f in actividad) else 'NO'
 feature['INGRESO_DA_VS_MU_ORIGEN']='IGUAL' if feature['DA_ANOINGRESO']==feature['MU_INGRESO_ORIGEN'] and feature['DA_ANOINGRESO']!='AUSENTE_O_INVALIDO' else 'DISTINTO' if all(feature[x]!='AUSENTE_O_INVALIDO' for x in ['DA_ANOINGRESO','MU_INGRESO_ORIGEN']) else 'NO_COMPARABLE'
 obs.append({'grupo':gids[key(r)],'key':key(r),'persona':r['persona'],'codigo':next(iter(codes)),'features':feature,'n_obs':len(rr),'mus':mus,'das':das,'rr':rr})
assert len(obs)==637 and len({x['persona'] for x in obs})==586
bad={'AUSENTE','MULTIPLE','AUSENTE_O_INVALIDO','NO_COMPARABLE'}
def partition(rr,fs):
 g=collections.defaultdict(list);missing=0
 for x in rr:
  vals=tuple(x['features'][f] for f in fs)
  if any(v in bad for v in vals):missing+=1;continue
  g[vals].append(x)
 mixed=sum(len({x['codigo'] for x in gr})>1 for gr in g.values())
 unit=sum(len({x['persona'] for x in gr})==1 for gr in g.values())
 return {'variables':fs,'sin_dato':missing,'subgrupos':len(g),'subgrupos_multicodigo':mixed,'subgrupos_una_persona':unit,'separa_todos_observados':missing==0 and mixed==0,'min_personas_por_subgrupo':min((len({x['persona'] for x in gr}) for gr in g.values()),default=0),'distribucion':[{'valores':dict(zip(fs,k)),'personas_por_codigo':{co:len({x['persona'] for x in gr if x['codigo']==co}) for co in sorted({x['codigo'] for x in gr})}} for k,gr in sorted(g.items())]}
features=list(obs[0]['features']);out=[];hist=load(R/'data/versiones_por_cohorte/20261016/historias_oferta.json');hidx={x['codigo_unico']:x for x in hist}
for group in sorted(set(gids.values())):
 rr=[x for x in obs if x['grupo']==group];assert rr
 tests=[partition(rr,[f]) for f in features]
 pairnames=[['DA_ANOINGRESO','DA_PERIODOINGRESO'],['DA_ANOINGRESO','PRIMER_ANIO_ACTIVIDAD_PLAN'],['DA_ANOINGRESO','PLAN_DISTINTO_ANTES'],['MU_INGRESO_ORIGEN','MU_INGRESO_ACTUAL']]
 tests += [partition(rr,f) for f in pairnames]
 codes=sorted({x['codigo'] for x in rr});yr=int(rr[0]['key'][0]);profiles=[]
 for c in codes:
  h=hidx.get(c,{});same=[x for x in h.get('anual',[]) if x['anio']==yr]
  profiles.append({'codigo':c,'inicio_oferta_observado':h.get('inicio_oferta'),'perfiles_del_anio':same,'personas':len({x['persona'] for x in rr if x['codigo']==c})})
 out.append({'grupo':group,'variables_grupo':dict(zip(fields,rr[0]['key'])),'contextos_anuales':len(rr),'personas':len({x['persona'] for x in rr}),'observaciones':sum(x['n_obs'] for x in rr),'codigos_personas':{c:len({x['persona'] for x in rr if x['codigo']==c}) for c in codes},'variables_separan_completo':[t['variables'] for t in tests if t['separa_todos_observados']],'perfiles_sies':profiles,'pruebas_variables':tests,'clasificacion':'B/C observado; E relación causal y aplicabilidad general no acreditadas'})
# Cambios anuales en el mismo expediente/plan/jornada: observados, no fecha efectiva.
contexts=collections.defaultdict(list)
for ak,gr in annual.items():
 r=gr[0];codes={z['codigo_documental_atribuible'] for z in gr}
 if len(codes)==1:contexts[(r['persona'],r['CODCLI'],r['plan'],r['carrera'],r['sede_dimension'],r['jornada_sies'])].append((int(r['ano']),next(iter(codes))))
for g in out:
 rr=[x for x in obs if x['grupo']==g['grupo']];counts=collections.Counter();changes=collections.Counter()
 for x in rr:
  r=x['rr'][0];h=contexts[(r['persona'],r['CODCLI'],r['plan'],r['carrera'],r['sede_dimension'],r['jornada_sies'])];prior=sorted((y,c) for y,c in h if y<int(r['ano']))
  if not prior:counts['sin_ancla_anterior_mismo_contexto']+=1
  elif prior[-1][1]==x['codigo']:counts['misma_version_que_ultima_ancla_anual']+=1
  else:
   counts['version_distinta_ultima_ancla_anual']+=1;changes[(prior[-1][0],prior[-1][1],int(r['ano']),x['codigo'])]+=1
 g['transiciones_mismo_contexto']={'conteos':dict(counts),'cambios':[{'anio_previo':k[0],'codigo_previo':k[1],'anio_grupo':k[2],'codigo_grupo':k[3],'contextos':v} for k,v in sorted(changes.items())],'limite':'Mismo contexto del extracto actual; no acredita fecha efectiva ni que ese plan fuera vigente históricamente.'}
dump('GRUPOS_22_VARIABLES.json',out)
receipts={}
for x in obs:
 for e in x['mus']+x['das']:
  receipts.setdefault(e['fuente'],set()).add(e['hoja'])
dump('FUENTES_REFERENCIADAS.json',[{'ruta_declarada':k,'hojas':sorted(v),'estado':'Referencia en evidencia privada; lectura original adicional para seis errores se registra aparte'} for k,v in receipts.items()])
summary={'grupos':len(out),'contextos_anuales':len(obs),'personas_distintas':len({x['persona'] for x in obs}),'observaciones':sum(x['n_obs'] for x in obs),'con_algun_discriminante_descriptivo':sum(bool(x['variables_separan_completo']) for x in out),'grupos_por_variable_separadora':{f:sum(any(t['variables']==[f] and t['separa_todos_observados'] for t in x['pruebas_variables']) for x in out) for f in features},'sin_adjudicaciones':True,'limite':'Partición descriptiva no valida predicción; variables MU están en fuente que ya documenta código, no solución independiente para ausentes.'}
dump('RESUMEN_VARIABLES.json',summary)
print(json.dumps(summary,ensure_ascii=False))
for x in out: print(x['grupo'],x['variables_grupo'],x['codigos_personas'],x['variables_separan_completo'])
