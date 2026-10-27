"""Auditoría de 815 contextos: solo lectura, sin nuevas adjudicaciones."""
from pathlib import Path
import json, hashlib, sys, subprocess, re, csv
from collections import Counter,defaultdict
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).parent
prior=ROOT/'outputs/avance_historico_atribucion_20261027/auditar_atribucion.py'
# Reutilizar extracción del foco validado sin ejecutar sus escrituras.
ns={'__file__':str(prior)}
exec(compile(prior.read_text().split('# Query once per exact context.')[0],str(prior),'exec'),ns)
for k in ['t','h','focus','strict','body','clean','service','groups','sha','git','checks','ck','src','manifest','protected','start','active','activehash','group_path']:
 globals()[k]=ns[k]
byexp=defaultdict(list);owners=defaultdict(set)
for pe,cli,pl,an,per,ca,se,jo,pa in service.db.execute('select persona,codcli,plan,anio,periodo,carrera,sede,jornada,payload from observaciones'):
 byexp[(pe,cli)].append(json.loads(pa));owners[cli].add(pe)
mapraw=defaultdict(set)
for g in groups:
 for fam in g['familias']:mapraw[(g['codcarpr'],g['jornada'])].add(fam)
contexts={}; refs=defaultdict(set)
for i in focus:
 r=t.loc[i]
 if r[0]!='R' or not r[2]:continue
 selected=h.loc[strict.get((body(r[1]),body(r[2])),[])]
 for ctx,g in selected.groupby(['CODCLI','PLAN_DE_ESTUDIO','CODCARR','JORNADA','_ANO_NUM','_PERIODO_NUM'],dropna=False):
  cli,plan,car,jo,year,per=ctx
  if not (str(year).replace('.','',1).isdigit() and str(per).replace('.','',1).isdigit()):continue
  key=(body(r[1])+'-'+body(r[2]),clean(cli),clean(plan),clean(car),clean(jo),str(int(year)),str(int(per)))
  refs[key].add(i)
  if key in contexts:continue
  pe,cli,pl,ca,jo,an,period=key
  indexed=byexp.get((pe,cli),[])
  if not indexed or any(str(x['ano'])==an and str(x['periodo'])==period for x in indexed):continue
  val=service.consultar(persona=pe,codcli=cli,plan=pl,anio=an,periodo=period,carrera=ca)
  if val.get('motivo')!='CONTEXTO_NO_LOCALIZADO':continue
  contexts[key]={'activity_rows':len(g),'approved':int(g['_ESTADO_NORM'].isin(['A','E','I']).sum()),'annual2025':int(an=='2025')*int(g['_ESTADO_NORM'].isin(['A','R']).sum())}
ck('Foco 815 reproducido',815,len(contexts))
if len(contexts)!=815:raise ValueError('Discrepancia de foco: detener')
print('Foco 815 reproducido; contrastando contexto anual',flush=True)
states=Counter();years=defaultdict(Counter);careers=defaultdict(Counter);codes=Counter();people=defaultdict(set);exps=defaultdict(set);diagnostics=Counter();source_refs=defaultdict(set);candidates=[]
for key,activity in contexts.items():
 pe,cli,pl,ca,jo,an,period=key; indexed=byexp[(pe,cli)];families=mapraw.get((ca,jo),set())
 all_year=[x for x in indexed if str(x['ano'])==an]
 # Sede UMAS RE / CO o componente numérico; se coteja contra la familia gobernada.
 def fam_of(x):
  code=x.get('codigo_documental_atribuible') or x.get('codigo_interno_adoptado') or ''
  return code.rsplit('V',1)[0] if code else ''
 def reusable(x):
  a=x.get('codigo_documental_atribuible') or '';b=x.get('codigo_interno_adoptado') or ''
  return bool(a or b) and not(a and b and a!=b)
 exact=[x for x in all_year if x['plan']==pl and x['carrera']==ca and fam_of(x) in families and reusable(x)]
 exactcodes={x.get('codigo_documental_atribuible') or x.get('codigo_interno_adoptado') for x in exact}
 mu=service.codigos_mu(persona=pe,anio=an); matching=[e for e in mu['evidencias'] if e['codigo'].rsplit('V',1)[0] in families]; mucodes={e['codigo'] for e in matching}
 otherplans={x['plan'] for x in all_year if x['carrera']==ca and x['plan']!=pl}
 samecode_othercli=bool(mucodes and any(x['carrera']==ca and (x.get('codigo_documental_atribuible') or x.get('codigo_interno_adoptado')) in mucodes for (p,c),rr in byexp.items() if p==pe and c!=cli for x in rr if str(x['ano'])==an))
 if not families:state='SIN_FAMILIA_GOBERNADA_PARA_JORNADA'
 elif len(owners[cli])>1:state='CODCLI_MULTIPLES_IDENTIDADES'
 elif len(exactcodes)==1 and mucodes==exactcodes and not otherplans and not samecode_othercli:
  state='CANDIDATO_MISMO_ANIO_PLAN_CARRERA_JORNADA_Y_MU';codes[next(iter(exactcodes))]+=1
 elif len(exactcodes)==1 and mucodes==exactcodes:
  state='COINCIDENCIA_ANUAL_CON_PLAN_O_EXPEDIENTE_ALTERNATIVO'
 elif exactcodes:state='CONTEXTO_ANUAL_CON_CODIGO_NO_UNIVOCO_EN_MU'
 elif len(mucodes)==1:state='MU_ANUAL_UNICA_SIN_CONTEXTO_CONCORDANTE_DEL_ANIO'
 elif len(mucodes)>1:state='MULTIPLES_VERSIONES_MU_ANUAL'
 elif mu['codigos']:state='MU_ANUAL_SOLO_OTRA_FAMILIA'
 else:state='SIN_MU_DEL_ANIO_EN_INDICE'
 states[state]+=1;years[an][state]+=1;careers[ca+' / '+jo][state]+=1;people[state].add(pe);exps[state].add((pe,cli,ca))
 diagnostics['con_otro_plan_misma_carrera_anio']+=bool(otherplans);diagnostics['con_otro_codcli_mismo_codigo_anio']+=samecode_othercli
 for e in matching:source_refs[e['fuente']].add((e['hoja'],e['fila']))
 candidates.append({'key':key,'state':state,'codes':sorted(exactcodes),'mu_codes':sorted(mucodes),'exact':exact,'mu':matching,'activity':activity})
ck('Particion contextos',815,sum(states.values()))
result={'clase':'B/C/E','contextos':815,'personas':len({k[0] for k in contexts}),'expedientes_persona_codcli_carrera':len({(k[0],k[1],k[3]) for k in contexts}),'filas_h113_afectadas':len(set().union(*(refs[k] for k in contexts))),'estados':dict(states),'por_anio':dict(years),'por_carrera_jornada':dict(careers),'codigos_candidatos':dict(codes),'personas_por_estado_no_sumables':{k:len(v) for k,v in people.items()},'diagnosticos_no_aditivos':dict(diagnostics),'fuentes_mu_referenciadas':{k:{'referencias_hoja_fila':len(v)} for k,v in source_refs.items()},'aplicado':False,'limite':'Candidatos del mismo año no acreditan por sí solos continuidad temporal del plan ni PLAN_ESTUDIOS curricular; no son cierres.'}
# Solo agregados se exportan. Datos de personas permanecen en memoria.
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
dump('RESULTADOS_PRELIMINARES.json',result)
print(json.dumps({k:v for k,v in result.items() if k not in ['por_carrera_jornada','por_anio','fuentes_mu_referenciadas']},ensure_ascii=False,indent=2),flush=True)
# El paso de verificación primaria se carga separadamente, sin persistir identidades.
verifier=OUT/'verificar_evidencia.py'
if verifier.exists():exec(compile(verifier.read_text(),str(verifier),'exec'))
for k,p in src.items():ck('Fuente preservada '+k,manifest['fuentes'][k]['sha256'],sha(p))
for f,v in protected.items():ck('Cambio previo preservado '+f,v,sha(ROOT/f))
ck('Diccionario privado preservado',service.descriptor['base_privada']['sha256'],sha(Path(service.descriptor['base_privada']['ruta'])))
ck('Puntero preservado',activehash,sha(active));ck('HEAD preservado',start['head'],git('rev-parse','HEAD'));ck('Rama preservada',start['rama'],git('branch','--show-current'))
service.close()
dump('QA.json',{'estado':'PASS_AUDITORIA_PARCIAL' if all(x['estado']=='PASS' for x in checks) else 'FAIL','controles':checks})
dump('MANIFEST.json',{'fecha_utc':datetime.now(timezone.utc).isoformat(),'fuentes':manifest['fuentes'],'diccionario':{'edicion':service.edicion,'base_sha256':service.descriptor['base_privada']['sha256']},'lector_reutilizado':{'ruta':str(prior),'sha256':sha(prior)},'script_sha256':sha(__file__),'git_antes':start,'git_despues':{'head':git('rev-parse','HEAD'),'rama':git('branch','--show-current')},'salidas':{p.name:sha(p) for p in OUT.glob('*.json') if p.name!='MANIFEST.json'},'sin_identificadores':True,'sin_commit_push':True,'sin_mutaciones':True})
