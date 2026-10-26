"""Experimento anual con abstención y validación por persona; no adjudica códigos."""
from pathlib import Path
import sys,json,datetime,hashlib,collections,math,subprocess
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
now=datetime.datetime.now(ZoneInfo('America/Santiago'));O=R/'outputs'/('auditoria_metodos_puente_'+now.strftime('%Y%m%d_%H%M%S'));O.mkdir()
read=lambda p:json.loads(Path(p).read_text())
def dump(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
git=lambda *a:subprocess.check_output(['git','-C',str(R),*a],text=True).strip()
A=R/'data/diccionario_sies_seguimiento/activo.json';ah=sha256(A);active=read(A);s=DiccionarioSiesSeguimiento();assert s.edicion=='v7_20261023_inf35_03_t3';dh=s.descriptor['base_privada']['sha256'];dbpath=s.descriptor['base_privada']['ruta'];head=git('rev-parse','HEAD');branch=git('branch','--show-current');rs=[json.loads(x[0]) for x in s.db.execute('select payload from observaciones')];s.close()
assert len(rs)==24774
# Una etiqueta anual por contexto; los períodos no multiplican los casos de prueba.
def annualkey(r):return tuple(str(r[k]) for k in ['persona','CODCLI','plan','carrera','sede_dimension','jornada_sies','ano'])
groups=collections.defaultdict(list)
for r in rs:
 if r['codigo_documental_atribuible']:groups[annualkey(r)].append(r)
annual=[];conflicts=0;ingresso_multi=0
for key,gr in groups.items():
 codes={r['codigo_documental_atribuible'] for r in gr}
 if len(codes)!=1:conflicts+=1;continue
 ingresos={str(r['fechas_declaradas'].get('DA_ANOINGRESO') or '') for r in gr};ingresso_multi+=len(ingresos)>1
 r=gr[0];annual.append({'persona':r['persona'],'CODCLI':r['CODCLI'],'plan':r['plan'],'carrera':r['carrera'],'sede':r['sede_dimension'],'jornada':r['jornada_sies'],'ano':str(r['ano']),'ingreso_DA':next(iter(ingresos)) if len(ingresos)==1 else '', 'codigo':next(iter(codes)),'fold':int(hashlib.sha256(r['persona'].encode()).hexdigest()[:16],16)%5,'periodos':len(gr)})
fields={'K1_carrera_sede_jornada_anio':['carrera','sede','jornada','ano'],'K2_mas_plan':['carrera','sede','jornada','ano','plan'],'K3_mas_ingreso_DA':['carrera','sede','jornada','ano','plan','ingreso_DA'],'K4_plan_ingreso_sin_anio':['carrera','sede','jornada','plan','ingreso_DA']}
def kfun(r,fs):return tuple(str(r.get(k) or '') for k in fs)
def build(rows,fs):
 m=collections.defaultdict(lambda:collections.defaultdict(set))
 for r in rows:
  k=kfun(r,fs)
  if '' not in k:m[k][r['codigo']].add(r['persona'])
 return m
def select(m,r,fs,minimum=1):
 k=kfun(r,fs)
 if '' in k:return None,'VARIABLE_AUSENTE'
 c=m.get(k,{})
 if not c:return None,'SIN_GRUPO_ENTRENADO'
 if len(c)>1:return None,'MULTIPLES_CODIGOS'
 if len(next(iter(c.values())))<minimum:return None,'SOPORTE_INSUFICIENTE'
 return next(iter(c)),'EMITIDO'
def met(recs):
 n=len(recs);sel=[r for r in recs if r['pred']];ok=sum(r['pred']==r['codigo'] for r in sel);err=len(sel)-ok
 return {'universo':n,'personas':len({r['persona'] for r in recs}),'emitidos':len(sel),'correctos':ok,'errores':err,'abstenciones':n-len(sel),'cobertura_pct':100*len(sel)/n if n else None,'precision_emitidos_pct':100*ok/len(sel) if sel else None,'error_total_pct':100*err/n if n else None,'personas_con_error':len({r['persona'] for r in sel if r['pred']!=r['codigo']}),'motivos_abstencion':dict(collections.Counter(r['reason'] for r in recs if not r['pred']))}
familycodes=collections.defaultdict(set)
for r in annual:familycodes[r['codigo'].split('V')[0]].add(r['codigo'])
multifamilies={f for f,v in familycodes.items() if len(v)>1}
cv={};ident=[];conflictgroups=[];cv_records={}
for name,fs in fields.items():
 full=build(annual,fs);mixed={k:v for k,v in full.items() if len(v)>1}
 rows_mixed=[r for r in annual if kfun(r,fs) in mixed]
 ent=0
 for k,v in full.items():
  counts=[len(z) for z in v.values()];nn=sum(counts);ent+=nn*(-sum(c/nn*math.log2(c/nn) for c in counts))
 totalvotes=sum(sum(len(z) for z in v.values()) for v in full.values())
 ident.append({'llave':name,'grupos':len(full),'grupos_multicodigo':len(mixed),'contextos_en_grupos_multicodigo':len(rows_mixed),'personas_en_grupos_multicodigo':len({r['persona'] for r in rows_mixed}),'entropia_condicional_bits':ent/totalvotes if totalvotes else None,'nota':'Descriptivo código completo; votos persona/código por grupo, no independencia estadística'})
 for k,v in mixed.items():conflictgroups.append({'llave':name,'variables':dict(zip(fs,k)),'codigos_y_personas':{c:len(p) for c,p in v.items()},'clasificacion':'B/C conflicto observado; no resuelto'})
 for minimum in [1,3]:
  results=[]
  for fold in range(5):
   train=[r for r in annual if r['fold']!=fold];test=[r for r in annual if r['fold']==fold];assert not ({r['persona'] for r in train}&{r['persona'] for r in test});model=build(train,fs)
   for r in test:
    pred,reason=select(model,r,fs,minimum);results.append(dict(r,pred=pred,reason=reason))
  key=name+'_min'+str(minimum);folds=[met([r for r in results if r['fold']==fold]) for fold in range(5)]
  cv[key]={'global':met(results),'por_particion':folds,'por_anio':{y:met([r for r in results if r['ano']==y]) for y in sorted({r['ano'] for r in results})},'familias_multiversion':met([r for r in results if r['codigo'].split('V')[0] in multifamilies]),'nota':'Prueba anual entre personas, no versión de T2/T3; etiquetas heredadas de atribución documental anual.'};cv_records[key]=results
# Exactamente el mismo conjunto de control; ventaja de plan sobre base solo en intersección de emitidos.
comparisons=[]
base={annualkey(r):r for r in rs if False} # no se escribe identidad
for minnum in [1,3]:
 rr1=cv_records['K1_carrera_sede_jornada_anio_min'+str(minnum)];rr2=cv_records['K2_mas_plan_min'+str(minnum)];assert [(r['persona'],r['CODCLI'],r['ano'],r['plan']) for r in rr1]==[(r['persona'],r['CODCLI'],r['ano'],r['plan']) for r in rr2]
 shared=[(a,b) for a,b in zip(rr1,rr2) if a['pred'] and b['pred']];comparisons.append({'min_personas':minnum,'emitidos_por_ambos':len(shared),'errores_sin_plan':sum(a['pred']!=a['codigo'] for a,b in shared),'errores_con_plan':sum(b['pred']!=b['codigo'] for a,b in shared),'advertencia':'No comparar solo precisión condicionada sin cobertura.'})
# Predicción temporal: solo años previos, nunca observar la etiqueta del año objetivo.
forward={}
for name,fs in [('T_plan',['carrera','sede','jornada','plan']),('T_plan_ingreso',['carrera','sede','jornada','plan','ingreso_DA'])]:
 results=[]
 for year in sorted({r['ano'] for r in annual}):
  model=build([r for r in annual if int(r['ano'])<int(year)],fs)
  for r in [r for r in annual if r['ano']==year]:
   pred,reason=select(model,r,fs);results.append(dict(r,pred=pred,reason=reason))
 forward[name]={'global':met(results),'por_anio':{y:met([r for r in results if r['ano']==y]) for y in sorted({r['ano'] for r in results})},'nota':'Puede usar historia previa de misma persona; prueba separada de cinco particiones por persona.'}
# Continuidad del expediente: ocultar año objetivo completo; usar solo anclas del mismo contexto.
ctxfields=['persona','CODCLI','plan','carrera','sede','jornada'];context=collections.defaultdict(list)
for r in annual:context[kfun(r,ctxfields)].append(r)
continuity={}
for mode in ['solo_anteriores','cualquier_otro_anio','anclas_a_ambos_lados']:
 results=[]
 for r in annual:
  other=[z for z in context[kfun(r,ctxfields)] if z['ano']!=r['ano']]
  if mode=='solo_anteriores':other=[z for z in other if int(z['ano'])<int(r['ano'])]
  if mode=='anclas_a_ambos_lados' and not (any(int(z['ano'])<int(r['ano']) for z in other) and any(int(z['ano'])>int(r['ano']) for z in other)):other=[]
  codes={z['codigo'] for z in other};pred=next(iter(codes)) if len(codes)==1 else None;reason='EMITIDO' if pred else 'SIN_ANCLA' if not codes else 'ANCLAS_DISCORDANTES';results.append(dict(r,pred=pred,reason=reason))
 continuity[mode]=met(results)
# Inventario de alcance. Los candidatos pendientes son predicciones, no cierres.
byyear=[]
for year in sorted({r['ano'] for r in rs}):
 q=[r for r in rs if r['ano']==year];byyear.append({'ano':year,'observaciones':len(q),'documentales':sum(bool(r['codigo_documental_atribuible']) for r in q),'solo_internas':sum(bool(r['codigo_interno_adoptado']) and not r['codigo_documental_atribuible'] for r in q),'pendientes':sum(not r['codigo_interno_adoptado'] for r in q)})
status=collections.Counter(r['estado_interno'] for r in rs if not r['codigo_interno_adoptado'])
people=collections.defaultdict(list)
for r in rs:people[r['persona']].append(r)
peopleparts={}
for field,label in [('codigo_documental_atribuible','documental'),('codigo_interno_adoptado','interno')]:
 peopleparts[label]={'sin_pendientes':sum(all(r[field] for r in gr) for gr in people.values()),'parciales':sum(any(r[field] for r in gr) and not all(r[field] for r in gr) for gr in people.values()),'ninguna_resuelta':sum(not any(r[field] for r in gr) for gr in people.values())}
pending=[]
for r in rs:
 if not r['codigo_interno_adoptado']:pending.append({'persona':r['persona'],'CODCLI':r['CODCLI'],'plan':r['plan'],'carrera':r['carrera'],'sede':r['sede_dimension'],'jornada':r['jornada_sies'],'ano':str(r['ano']),'ingreso_DA':str(r['fechas_declaradas'].get('DA_ANOINGRESO') or '')})
reach={}
for name,fs in fields.items():
 # Excluir siempre la persona para no presentar su propia etiqueta como regla de grupo.
 codes=[]
 for fold in range(5):
  model=build([r for r in annual if r['fold']!=fold],fs)
  for r in pending:
   if int(hashlib.sha256(r['persona'].encode()).hexdigest()[:16],16)%5!=fold:continue
   pred,reason=select(model,r,fs,3);codes.append(dict(r,pred=pred,reason=reason))
 reach[name]={'observaciones_con_candidato':sum(bool(r['pred']) for r in codes),'personas_con_candidato':len({r['persona'] for r in codes if r['pred']}),'sin_candidato':sum(not r['pred'] for r in codes),'motivos':dict(collections.Counter(r['reason'] for r in codes if not r['pred'])),'aplicado':False,'clasificacion':'C propuesta experimental; E no verificada en pendientes; no es reducción de pendientes'}
# Ejemplo de identificabilidad: dos personas sin atributo discriminante, dos versiones 1/1.
from itertools import product
solutions=[z for z in product(['V1','V2'],repeat=2) if z.count('V1')==1 and z.count('V2')==1];assert len(solutions)==2
summary={'edicion':s.edicion,'universo_observaciones':len(rs),'personas':len(people),'expedientes_carrera_codcli':len({(r['carrera'],r['CODCLI']) for r in rs}),'documental':sum(bool(r['codigo_documental_atribuible']) for r in rs),'solo_interno':sum(bool(r['codigo_interno_adoptado']) and not r['codigo_documental_atribuible'] for r in rs),'pendientes':len(pending),'personas_categorias_excluyentes':peopleparts,'por_anio':byyear,'pendientes_por_estado':dict(status),'control_anual_deduplicado':{'contextos':len(annual),'personas':len({r['persona'] for r in annual}),'grupos_con_etiquetas_conflictivas_excluidos':conflicts,'ingresos_DA_multiples':ingresso_multi},'alcance':'Etiqueta documental anual atribuida, no verdad trimestral independiente; no afirma aceptación SIES ni vigencia','ejemplo_totales_sintetico':{'totales':{'V1':1,'V2':1},'soluciones':solutions,'conclusion':'La misma conciliación de totales permite dos asignaciones personales diferentes.'}}
dump('RESUMEN.json',summary);dump('IDENTIFICABILIDAD.json',ident);dump('GRUPOS_MULTICODIGO.json',conflictgroups);dump('VALIDACION_POR_PERSONA.json',cv);dump('COMPARACION_PAREADA.json',comparisons);dump('VALIDACION_TEMPORAL.json',forward);dump('CONTINUIDAD_EXPEDIENTE.json',continuity);dump('ALCANCE_EXPERIMENTAL_PENDIENTES.json',reach)
assert sha256(A)==ah and sha256(dbpath)==dh and git('rev-parse','HEAD')==head and git('branch','--show-current')==branch
for p in O.iterdir():
 text=p.read_text();assert not any(r['persona'] in text or r['CODCLI'] in text for r in rs)
qa={'resultado':'OK_EXPERIMENTO_NO_APLICADO','observaciones_originales':24774,'universo_control_anual':len(annual),'particiones_persona_sin_solapamiento':True,'documental_no_usado_como_etiqueta_trimestral':True,'diccionario_bases_denominadores_intactos':True,'commit_push':False,'git':{'rama':branch,'HEAD':head}};dump('QA.json',qa)
dump('MANIFEST.json',{'fecha_hora':now.isoformat(),'entradas':{'puntero_sha256':ah,'descriptor':active,'base_privada_sha256':dh,'base_privada_ruta':dbpath},'salidas_sha256':{p.name:sha256(p) for p in O.iterdir()},'codigo_sha256':{str(Path(__file__).relative_to(R)):sha256(__file__),'docs/ESPECIFICACION_AUDITORIA_METODOS_PUENTE_20261023.md':sha256(R/'docs/ESPECIFICACION_AUDITORIA_METODOS_PUENTE_20261023.md')},'QA':qa})
print(json.dumps({'output':str(O),'resumen':summary,'validacion':{k:v['global'] for k,v in cv.items()},'continuidad':continuity,'identificabilidad':ident},ensure_ascii=False))
