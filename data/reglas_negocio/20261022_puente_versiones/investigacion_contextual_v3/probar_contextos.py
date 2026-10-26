"""Pruebas de hipótesis locales. Proyección privada en memoria; salida exclusivamente agregada."""
import json,csv,re,hashlib,sqlite3
from pathlib import Path
from collections import defaultdict,Counter
import openpyxl
R=Path.cwd();B=R/'data/reglas_negocio/20261022_puente_versiones';O=B/'investigacion_contextual_v3';E=B/'ejecucion_plan_v2'
def load(p):return json.load(open(p))
def cv(p):return list(csv.DictReader(open(p,encoding='utf-8-sig')))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def val(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip().upper()
def doc(a,b=None):
 t=val(a).replace('.','').replace(' ','')+('-'+val(b) if b is not None else '')
 if not re.fullmatch(r'\d+-[0-9K]',t):return None
 a,b=t.split('-');return str(int(a))+'-'+b

def xl(p):
 w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=iter(w.active.values);h=next(it)
 for r in it:yield dict(zip(h,r))
 w.close()
old=cv(B/'DICCIONARIO_VERSIONES_UMAS_SIES_PROPUESTO_20261022.csv');dims={(x['codcarpr_interno'],x['sede'],x['jornada_catalogo']):x for x in old};cand=defaultdict(set)
for x in cv(B/'PUENTE_VERSIONES_PLAN_UMAS_SIES_20261022.csv'):cand[x['codcarpr_interno'],x['sede'],x['jornada_catalogo']].add(x['codigo_unico_sies_candidato'])
groups=load(R/'data/versiones_por_cohorte/20261016/grupos_existentes.json');gm={(g['codcarpr'],g['sede'],g['jornada']):g for g in groups};jmap={'D':'1','V':'2','O':'4'};revj={v:k for k,v in jmap.items()}
plans=load(R/'data/versiones_historicas_sies_umas/fase_4_20261015/catalogo_planes.json');pm={x['CODPESTUD']:x for x in plans};master=load(R/'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json');offers={(str(x['anio']),x['codigo_unico']):x for x in master['oferta_anual']}
sources=[];refs=defaultdict(list)
for s in load(E/'FUENTES.json'):
 if 'MAT_IP_CIISA_' not in s['ruta'] and 'BASE_RETENCION_MATRICULA_UNIFICADA' not in s['ruta']:continue
 assert sha(s['ruta'])==s['sha256'];sources.append(s);historic='MAT_IP_CIISA' in s['ruta']
 for x in xl(s['ruta']):
  if historic:
   k=doc(x['MM_N_DOCUMENTO'],x['MM_DV']);y=val(x['MC_CAT_PERIODO']).replace('MAT_','');code=val(x['MC_CODIGO_UNICO']);act=val(x['MM_ANIO_ACTUAL']);ori=val(x['MM_ANIO_ORIGEN']);sem=val(x['MM_SEM_ACTUAL'])
  else:
   if val(x['TIPO_DOC'])!='R':continue
   k=doc(x['N_DOC'],x['DV']);y=val(x['ANIO_INFORMADO']);code='I162S%sC%sJ%sV%s'%tuple(val(x[t]) for t in ['COD_SED','COD_CAR','JOR','VERSION']);act=val(x['ANIO_ING_ACT']);ori=val(x['ANIO_ING_ORI']);sem=val(x['SEM_ING_ACT'])
  if k:refs[k,y].append((code,act,ori,sem))
DA=Path('/Users/alexi/Downloads/DATOSDEALUMNOS_12159.xlsx');sources.append({'ruta':str(DA),'sha256':sha(DA),'uso':'nuevo corte explicito, no sustituye 11998/12023 historicos'})
da=defaultdict(set)
for x in xl(DA):
 k=doc(x['RUT']);da[val(x['CODCLI']),val(x['CODCARPR'])].add((k,val(x['SEDE']),jmap.get(val(x['JORNADA']),''),val(x['ANOINGRESO']),val(x['ANOMATRICULA'])))
PRO=Path('/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_12166.xlsx');sources.append({'ruta':str(PRO),'sha256':sha(PRO)})
pr=defaultdict(set);raw=Counter();invalid=0
for x in xl(PRO):
 k=doc(x['RUT'],x['DIG']);j=jmap.get(val(x['JORNADA']),'');c=val(x['CODCARR']);raw[c,j]+=1
 if not k:invalid+=1;continue
 pr[c,j].add((k,val(x['CODCLI']),val(x['PLAN_DE_ESTUDIO']),val(x['ANO']),val(x['PERIODO'])))
# Índice de posibles atribuciones por persona/año/familia: evita reutilizar un código en varias matrículas.
attributions=defaultdict(set);cli_ids=defaultdict(set)
for (c,j),units in pr.items():
 g=gm.get((c,'RE',revj.get(j)),{});fam=set(g.get('familias',[]))
 for k,cli,p,y,t in units:
  cli_ids[cli].add(k)
  for family in fam:attributions[k,y,family].add((c,cli))
result=[];context_rows=[]
for d,prior in dims.items():
 g=gm.get((d[0],'RE' if d[1]=='2' else d[1],revj.get(d[2])),{});families=set(g.get('familias',[])) or {x.rsplit('V',1)[0] for x in cand[d]};units=pr[d[0],d[2]];persons={u[0] for u in units};stats=Counter();basecontexts=defaultdict(set);cohortcontexts=defaultdict(set);codescount=defaultdict(set);missing=Counter();tuples=[]
 for k,cli,plan,y,t in units:
  matches=[r for r in refs[k,y] if r[0].rsplit('V',1)[0] in families];codes={r[0] for r in matches};raw_codes={r[0] for r in refs[k,y]};known=da.get((cli,d[0]),set());identity={r for r in known if r[0]==k};sites={r[1] for r in identity};journeys={r[2] for r in identity};planinfo=pm.get(plan,{})
  stats['CODCLI_varias_identidades']+=len(cli_ids[cli])>1;stats['DA_varias_identidades']+=len({r[0] for r in known})>1
  stats['identidad_DA_presente']+=bool(identity);stats['sede_DA_exacta']+=sites=={'RE'};stats['jornada_DA_coincide']+=journeys=={d[2]};stats['conflicto_DA_identidad']+=bool(known and not identity);stats['multisede_DA']+=len(sites)>1
  # Catálogo de plan solo acredita contexto estático, nunca vigencia histórica individual.
  stats['plan_catalogado']+=bool(planinfo);stats['plan_carrera_sede_catalogada']+=d[0] in planinfo.get('carreras_internas',[]) and planinfo.get('sedes')==['RE']
  if not codes:stats['sin_match']+=1;missing[y]+=1
  elif len(codes)>1:stats['multicodigo_persona']+=1
  else:
   stats['un_codigo']+=1;code=next(iter(codes));stats['atribucion_varios_programas_expedientes']+=len(attributions[k,y,code.rsplit('V',1)[0]])>1;codescount[code].add(k);stats['fuera_candidatos_2027']+=code not in cand[d];o=offers.get((y,code));stats['oferta_anual_presente']+=bool(o)
   actuals={r[1] for r in matches};origins={r[2] for r in matches};stats['cohorte_actual_distinta_observacion']+=any(a!=y for a in actuals);stats['cohorte_actual_no_unica']+=len(actuals)>1
   basecontexts[plan,y,t].add(code)
   for a in actuals:cohortcontexts[plan,y,t,a].add(code)
   # Información agregada para auditar relaciones; no persona ni CODCLI persistidos.
   for a in actuals:tuples.append((plan,y,t,a,code,k))
  stats['match_solo_otra_familia']+=bool(raw_codes and not codes)
 ctxt=defaultdict(set)
 for p,y,t,a,c,k in tuples:ctxt[p,y,t,a,c].add(k)
 for (p,y,t,a,c),people in sorted(ctxt.items()):context_rows.append({'carrera':d[0],'sede':d[1],'jornada':d[2],'plan':p,'ano_observacion':y,'periodo_observacion':t,'ano_ingreso_actual_MU':a,'codigo':c,'personas':len(people),'clasificacion':'C; contexto anual observado, no vigencia de plan'})
 complete=bool(units) and stats['un_codigo']==len(units) and stats['oferta_anual_presente']==len(units)
 result.append({'carrera':d[0],'sede':d[1],'jornada':d[2],'estado_previo':prior['estado'],'observaciones':len(units),'personas':len(persons),'estadisticas':dict(stats),'anios_sin_match':dict(missing),'codigos_personas':{c:len(k) for c,k in codescount.items()},'contextos_plan_ano_periodo_multiversion':sum(len(x)>1 for x in basecontexts.values()),'contextos_mas_cohorte_multiversion':sum(len(x)>1 for x in cohortcontexts.values()),'perfil_previo':g.get('perfiles_duracion_tipo',[]),'familias':sorted(families),'completo_observacional_anual':complete,'completo_con_contexto_DA_y_catalogo':complete and stats['sede_DA_exacta']==len(units) and stats['plan_carrera_sede_catalogada']==len(units) and stats['conflicto_DA_identidad']==0 and stats['CODCLI_varias_identidades']==0 and stats['DA_varias_identidades']==0 and stats['atribucion_varios_programas_expedientes']==0 and stats['jornada_DA_coincide']==len(units),'limite':'DA12159 es corte; no certifica sede/jornada historicas. PROMEDIOS plan reportado no prueba vigencia individual.'})
(O/'PRUEBAS_CONTEXTUALES.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));(O/'FUENTES.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2))
with open(O/'CONTEXTOS_OBSERVADOS.csv','w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(context_rows[0]));w.writeheader();w.writerows(context_rows)
assert all(sha(s['ruta'])==s['sha256'] for s in sources)
print(json.dumps({'dimensiones':len(result),'completos_anuales':[r['carrera']+'/J'+r['jornada'] for r in result if r['completo_observacional_anual']],'completos_mas_DA_catalogo':[r['carrera']+'/J'+r['jornada'] for r in result if r['completo_con_contexto_DA_y_catalogo']],'invalidas':invalid},ensure_ascii=False))
for r in result:
 if not r['estado_previo'].startswith('PROPUESTA'):print(json.dumps(r,ensure_ascii=False))
