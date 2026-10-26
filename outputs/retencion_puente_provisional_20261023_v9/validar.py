"""Valida subconjuntos V8 con índices gobernados y planes; privados fuera de Git."""
from pathlib import Path
import json,hashlib,re,csv,ast
from collections import defaultdict,Counter
R=Path.cwd();O=R/'outputs/retencion_puente_provisional_20261023_v9';T=Path('/tmp/ipss_validacion_2165_20261023');hashes={}
def load(p):hashes[str(p)]=hashlib.sha256(Path(p).read_bytes()).hexdigest();return json.load(open(p))
v8=load('/tmp/ipss_cruce_historico_20261023/resultados.json');a=[x for x in v8 if x[20] and len(x[20].split('; '))==1 and x[17]!='TIPO_PLAN_AMBIGUO' and x[15]<=int(x[7]) and x[9]!='CODIGO_UNICO_ATRIBUCION_EXPEDIENTE' and not x[24]];assert len(a)==2165 and sum(x[22] for x in a)==811;people={r[1] for r in a}
p=load('/tmp/ipss_revision_63_20261022/payload.json');get=lambda n:next(s['rows'] for s in p if s['name']==n);new=load('/tmp/ipss_embudo_2317_20261022/evidencias_nuevas.json');plans={x['CODPESTUD']:x for x in load(R/'data/versiones_historicas_sies_umas/fase_4_20261015/catalogo_planes.json')};hist={x['codigo_unico']:x for x in load(R/'data/versiones_por_cohorte/20261016/historias_oferta.json')};idx=defaultdict(list)
# Esquema común: persona,proceso,año,código,plan,CODCLI,carrera,ingreso,fuente,hoja,fila,condición.
for e in get('EVIDENCIAS_SIES'):
 if e[0] in people and e[4]=='COMPLETO':idx[e[0]].append([e[0],e[1],str(e[2]).replace('MAT_',''),e[3],e[6],'','',e[7],e[8],e[9],e[10],e[11]])
for e in new:
 if e[0] in people and e[4]=='COMPLETO':idx[e[0]].append([e[0],e[1],str(e[2]),e[3],e[6],e[7],e[8],'',e[9],e[10],e[11],e[13]])
# Contexto exacto DA y coexistencia; no escoger primera fila.
contexts=defaultdict(list);das=[];jm={'1':'D','2':'V','4':'O'}
for sh in p:
 if sh['name'].startswith('DA_'):
  hh=sh['headers'];rr=[]
  for row in sh['rows']:
   d=dict(zip(hh,row))
   if d['REV_RUT_DV'] not in people:continue
   rr.append(row);contexts[d['REV_RUT_DV'],str(d['CODCLI']),d['CODCARPR'],d['JORNADA']].append(d)
  das.append({**sh,'rows':rr})
peers=defaultdict(set)
for r in get('CONTRASTE_63'):
 if r[0] in people:peers[r[0],r[2],r[6]].add(r[1])
results=[];proof=[];groups=defaultdict(Counter);ag=defaultdict(lambda:[0,set()]);recs=[]
for r in a:
 rid,k,cli,c,site,j,plan,y,t=r[:9];yy=int(y);code=r[19];fam=code.rsplit('V',1)[0];group='811_MU_PERSONAL_OTRO_ANO' if r[22] else '1354_PERFIL_COHORTE';ev=idx[k];same=[e for e in ev if e[1]=='MATRICULA' and e[3]==code];yrs=sorted({int(e[2]) for e in same if e[2].isdigit()});other=[e for e in ev if e[1]=='MATRICULA' and e[3].rsplit('V',1)[0]==fam and e[3]!=code];before=any(z<yy for z in yrs);after=any(z>yy for z in yrs);timing='AMBOS_LADOS' if before and after else 'SOLO_ANTERIOR' if before else 'SOLO_POSTERIOR' if after else 'SIN_MU_CODIGO';annual=[e for e in same if e[2]==y]
 explicit=[e for e in annual if e[5]==cli and e[6]==c and e[4]==plan];exactcodes={e[3] for e in ev if e[1]=='MATRICULA' and e[2]==y and e[5]==cli and e[6]==c and e[4]==plan};pm=plans.get(plan);pc=bool(pm and c in pm['carreras_internas'] and pm['sedes']==['RE']);pv=bool(pm and pm['fecha_vigencia_acreditada']);pcode=pm.get('version_sies_asignada') if pm else None;ds=contexts[k,cli,c,jm[j]];dyears={str(int(d['ANOINGRESO'])) if isinstance(d['ANOINGRESO'],(int,float)) else str(d['ANOINGRESO']).strip() for d in ds};myears={str(e[7]) for e in same if str(e[7]).isdigit()};cohort='COINCIDE' if myears and myears==dyears else 'DIFIERE_O_MULTIPLE' if myears else 'NO_COMPARABLE';offers=[q for q in hist[code]['anual'] if q['anio']==yy];profileok=bool(offers and [offers[0]['duracion_total'],offers[0]['tipo_plan']] in json.loads(r[11]));planliteral=[e for e in ev if e[3]==code and e[4]==plan];coexist=len(peers[k,c,y]);adopt='';tests=['IDENTIDAD_EXACTA','FAMILIA_SIES','CRONOLOGIA_MU','INGRESO_MU_DA','PLAN_CATALOGO','TRAZA_CODCLI_PLAN_ANO','OFERTA_ANO_ACTIVIDAD','EXPEDIENTES_CONCURRENTES'];fails=[]
 if explicit and exactcodes=={code} and not other:
  state='VINCULO_DOCUMENTAL_APLICABLE';adopt=code;condition='Identidad/CODCLI/carrera/plan/año explícitos en matrícula sin alternativas';rule='RELACION_DOCUMENTAL_EXPLICITA_H4_FASEB'
 else:
  if not explicit:fails.append('MU no vincula explícitamente CODCLI+plan+año pendiente')
  if not pc:fails.append('Plan ausente o carrera/sede distinta en catálogo de planes')
  if other:fails.append('Otro código MU de misma familia en índice ampliado')
  if not profileok:fails.append('Perfil propuesto no acreditado en oferta del año de actividad')
  if coexist>1:fails.append('Varios expedientes internos misma carrera/año')
  if cohort=='DIFIERE_O_MULTIPLE':fails.append('Ingreso MU y DA no concordante o múltiple')
  if not pv:fails.append('Fecha efectiva del plan no acreditada')
  state='NO_DETERMINABLE_CON_ALERTA' if (not pc or other or not profileok or coexist>1 or cohort=='DIFIERE_O_MULTIPLE') else 'PROPUESTA_CONDICIONADA'
  condition='; '.join(fails);rule='H4_4_7;RESOLUTOR16OCT_PROPUESTA_NO_ASIGNACION'
 evidence_state='CODIGO_DOCUMENTADO_OTRO_ANO' if same else 'SIN_CORROBORACION_MU_CODIGO';decision='Acreditar enlace temporal expediente/plan o regla interna explícita que permita extrapolación' if same else 'Acreditar perfil individual/fecha efectiva o regla interna explícita de asignación por grupo/cohorte'
 results.append([*r,group,'; '.join(map(str,yrs)),timing,cohort,pc,pv,pcode or '',bool(planliteral),len(other),profileok,coexist,bool(explicit),evidence_state,state,adopt,condition,rule,decision])
 for e in ev:
  if e[3]==code or e in other:proof.append([rid,*e[1:]])
 recs.append([rid,group,'; '.join(tests),state,condition])
 for key,val in [('observaciones',1),('personas_placeholder',0),(state,1),(timing,1),('plan_carrera_sede_concordante',pc),('plan_con_fecha_efectiva',pv),('plan_literal_en_SIES',bool(planliteral)),('otros_codigos_MU',bool(other)),('oferta_perfil_ano_actividad',profileok),('ingreso_MU_DA_'+cohort,1),('coexistencia_expedientes',coexist>1),('vinculo_explicito_aplicable',bool(explicit))]:groups[group][key]+=int(val)
 ag[group,c,j,y,state][0]+=1;ag[group,c,j,y,state][1].add(k)
# Equivalencias manuales vigentes: verificar fuente ejecutable contra snapshot, sin ejecutarla.
manualdata=load(R/'data/diccionario_sies_umas/20261015/evidencia/caracterizacion_reglas_y_fuentes.json')['equivalencias_manual_fcu2026']
source=R/'procesos/caracterizacion/caracterizacion.py';hashes[str(source)]=hashlib.sha256(source.read_bytes()).hexdigest();tree=ast.parse(source.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_fcu2026_manual_equivalencias_cod_car');assignment=next(n for n in fn.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='rows' for t in n.targets));tuples=ast.literal_eval(assignment.value)
manual={(x[1],x[4],x[3]):x[5] for x in tuples};assert manual=={(x['CODCARPR'],x['SEDE'],x['JORNADA']):x['CODIGO_UNICO_SIES'] for x in manualdata['filas']}
internal=set()
for x in results:
 if x[7]=='2026' and x[10]=='MANUAL_FCU2026' and manual.get((x[3],'RE',jm[x[5]]))==x[19] and x[34] and x[39] and not x[38] and x[40]==1:
  x[43]='CORRESPONDENCIA_INTERNA_REGLA_VIGENTE';x[44]=x[19];x[45]='Equivalencia manual FCU2026 exacta vigente; solo correspondencia interna2026, no envío ni plan histórico';x[46]='_fcu2026_manual_equivalencias_cod_car + _fcu2026_apply_manual_equivalencias_fcu_2026';x[47]='No requiere regla nueva para correspondencia interna; conservar envío/plan histórico separados';internal.add(x[0]);proof.append([x[0],'REGLA_INTERNA','2026',x[19],'','','','',str(source),'_fcu2026_manual_equivalencias_cod_car',fn.lineno,'VALIDADO_MANUAL_FCU; clasificación D'])
# Recalcular particiones después de comprobar regla específica; no adoptar propuestas por perfil.
for group in groups:
 for st in ['PROPUESTA_CONDICIONADA','NO_DETERMINABLE_CON_ALERTA','CORRESPONDENCIA_INTERNA_REGLA_VIGENTE','VINCULO_DOCUMENTAL_APLICABLE']:groups[group][st]=sum(x[30]==group and x[43]==st for x in results)
ag=defaultdict(lambda:[0,set()])
for x in results:ag[x[30],x[3],x[5],x[7],x[43]][0]+=1;ag[x[30],x[3],x[5],x[7],x[43]][1].add(x[1])
resolved={x[0] for x in results if x[44]};remain={x[1] for x in v8 if x[0] not in resolved};success={x[1] for x in results if x[44]};states=Counter(x[43] for x in results)
for group,z in groups.items():z.pop('personas_placeholder',None);z['personas']=len({x[1] for x in results if x[30]==group})
summary={'observaciones_validadas':2165,'personas_validadas':len(people),'grupos':dict(groups),'estados':dict(states),'nuevos_vinculos_documentales_aplicables':sum(x[43]=='VINCULO_DOCUMENTAL_APLICABLE' for x in results),'correspondencias_internas_adoptadas_regla_vigente':len(internal),'pendientes_documentales_observaciones':3213,'pendientes_documentales_personas':1838,'personas_completamente_resueltas':len(success-remain),'personas_parcialmente_resueltas':len(success&remain),'pendientes_observaciones':3213-len(resolved),'pendientes_personas':len(remain),'universo_personas':5901,'fuera_foco_intactas':1048,'escenario501_no_aplicado':True}
recs=[[x[0],x[30],'; '.join(tests),x[43],x[45]] for x in results]
for name,x in [('resultados.json',results),('evidencias.json',proof),('pruebas.json',recs),('DA_foco.json',das)]: (T/name).write_text(json.dumps(x,ensure_ascii=False))
(O/'RESULTADO.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));(O/'FUENTES_HASHES.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2))
with open(O/'DESGLOSE.csv','w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Grupo','Carrera','Jornada','Ano','Estado','Observaciones','Personas_no_aditivas'])
 for kk,(n,pp) in sorted(ag.items()):w.writerow([*kk,n,len(pp)])
print(json.dumps(summary,ensure_ascii=False))
