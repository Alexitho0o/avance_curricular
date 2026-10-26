import json,csv,hashlib
from pathlib import Path
from collections import defaultdict,Counter
R=Path.cwd();T=Path('/tmp/ipss_embudo_2317_20261022');O=R/'outputs/auditoria_embudo_2317_20261022';x=json.load(open('/tmp/ipss_revision_63_20261022/payload.json'));get=lambda n:next(s['rows'] for s in x if s['name']==n);states={'CONTRADICCION_O_ATRIBUCION_MULTIPLE','SIN_EVIDENCIA_ANUAL_APLICABLE','CODIGO_ANUAL_SIN_CONTEXTO_DA_EXACTO','DIFIERE_CODIGO_PROPUESTO_OBSERVADO'};units=[r for r in get('CONTRASTE_63') if r[10] in states];foc={r[0] for r in units};nh=defaultdict(list);oh=defaultdict(list)
for e in get('EVIDENCIAS_SIES'):
 if e[0] in foc and e[4]=='COMPLETO':oh[e[0]].append(e)
for e in json.load(open(T/'evidencias_nuevas.json')):
 if e[4]=='COMPLETO':nh[e[0]].append(e)
dims=json.load(open(R/'data/reglas_negocio/20261022_puente_versiones/investigacion_contextual_v3/PRUEBAS_CONTEXTUALES.json'));fam={(r['carrera'],r['jornada']):set(r['familias']) for r in dims};private=[];pcauses=defaultdict(set);ag=defaultdict(list);rec=[];newplan=0
for r in units:
 k,cli,c,site,j,plan,y,t,before,annual,state=r[:11];f=fam[c,j];old=oh[k];new=nh[k];allcodes={e[3] for e in old+new};sameold=[e for e in old if e[3].rsplit('V',1)[0] in f];samenew=[e for e in new if e[3].rsplit('V',1)[0] in f];newannual=[e for e in samenew if e[1]=='MATRICULA' and e[2]==y];newcodes={e[3] for e in newannual};direct=[e for e in newannual if e[7]==cli and e[8]==c and e[6]==plan and plan];newplan+=bool(direct)
 if state=='DIFIERE_CODIGO_PROPUESTO_OBSERVADO':cause='CODIGO_LOCALIZADO_DIFIERE_INFERENCIA';action='Conservar código documental por contexto; revisar versión fija propuesta, no buscar nuevamente identidad.'
 elif state=='CONTRADICCION_O_ATRIBUCION_MULTIPLE':cause='CODIGO_UNICO_ATRIBUCION_EXPEDIENTE';action='Acreditar secuencia CODCLI/periodo y carrera; varios expedientes no prueban varios códigos.'
 elif state=='CODIGO_ANUAL_SIN_CONTEXTO_DA_EXACTO':cause='CODIGO_LOCALIZADO_FALTA_CONTEXTO_DA';action='Fila DA por CODCLI+RUT+CODCARPR+SEDE+JORNADA del expediente.'
 elif newcodes: cause='RECUPERADO_CODIGO_ANUAL_FUENTE_OMITIDA';action='Código localizado en respaldo adicional; conciliar carga/rectificación frente a base anual antes de adoptarlo.';rec.append(r)
 elif sameold or samenew:cause='CODIGO_MISMA_FAMILIA_FILTRO_TEMPORAL';action='Validar periodo acreditado por proceso o historial de matrícula/plan; no exigir igualdad ingenua de año de carga.'
 elif allcodes:cause='CODIGO_OTRA_CARRERA_SEDE_JORNADA';action='Acreditar cambio/traslado y correspondencia de expediente; no trasladar código automáticamente.'
 else:cause='NO_LOCALIZADO_COBERTURA_ACOTADA';action='Fuente individual del periodo/carga faltante o rectificación; agregados no identifican estudiantes.'
 blockers=[]
 if not allcodes:blockers.append('SIN_IDENTIDAD_CON_CODIGO_COMPLETO_EN_FUENTES_LEIDAS')
 if allcodes and not(sameold or samenew):blockers.append('FAMILIA_DIFERENTE')
 if not annual and not newcodes:blockers.append('SIN_MU_ANUAL_MISMA_FAMILIA')
 if state=='CONTRADICCION_O_ATRIBUCION_MULTIPLE':blockers.append('ATRIBUCION_MULTIPLE;no conflicto de código demostrado')
 if state=='CODIGO_ANUAL_SIN_CONTEXTO_DA_EXACTO':blockers.append('DA_NO_CONCORDANTE')
 blockers.append('PLAN_EFECTIVO_NO_ACREDITADO;no filtro para recuperar código')
 classification='RECUPERADO_DOCUMENTALMENTE_CODIGO_NO_PLAN' if cause.startswith('RECUPERADO') else 'DATO_NO_LOCALIZADO_TRAS_COBERTURA_COMPROBADA_ACOTADA' if not allcodes else 'CODIGO_LOCALIZADO_PENDIENTE_ATRIBUCION'
 loc='; '.join(f'{e[9]}#{e[10]}!fila{e[11]}' for e in newannual)
 private.append([k,cli,c,site,j,plan,y,t,state,cause,classification,len(old),len(new),'; '.join(sorted(allcodes)),'; '.join(sorted(newcodes)),bool(direct),'; '.join(blockers),action,loc]);pcauses[k].add(cause);ag[cause,c,y,j].append(r)
# Personas: prioridad explícita. No hay una causa única natural cuando tienen observaciones distintas.
order=['NO_LOCALIZADO_COBERTURA_ACOTADA','CODIGO_OTRA_CARRERA_SEDE_JORNADA','CODIGO_MISMA_FAMILIA_FILTRO_TEMPORAL','CODIGO_UNICO_ATRIBUCION_EXPEDIENTE','CODIGO_LOCALIZADO_FALTA_CONTEXTO_DA','CODIGO_LOCALIZADO_DIFIERE_INFERENCIA','RECUPERADO_CODIGO_ANUAL_FUENTE_OMITIDA'];personprimary={k:next(c for c in order if c in cc) for k,cc in pcauses.items()};pc=Counter(personprimary.values());oc=Counter(r[9] for r in private)
rows=[]
for cause in order:rows.append([cause,oc[cause],len({r[0] for r in private if r[9]==cause}),pc[cause]])
assert sum(oc.values())==4973 and sum(pc.values())==2317
with open(O/'CAUSAS_EXCLUSIVAS.csv','w',encoding='utf-8-sig',newline='') as f:w=csv.writer(f);w.writerow(['causa','observaciones_exclusivas','personas_en_causa_solapables','personas_exclusivas_segun_prioridad']);w.writerows(rows)
with open(O/'CAUSA_CARRERA_ANO_JORNADA.csv','w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['causa','carrera','ano','jornada','personas_solapables','observaciones'])
 for keys,rr in sorted(ag.items()):w.writerow([*keys,len({r[0] for r in rr}),len(rr)])
cov=json.load(open(T/'cobertura.json'));hs=json.load(open(T/'hashes.json'));oldpaths={r[1] for r in get('COBERTURA_SIES')};sourcecount=len(set(hs)|oldpaths)
summary={'personas':2317,'observaciones':4973,'particion':rows,'prioridad_personas':order,'personas_con_multiples_causas':sum(len(v)>1 for v in pcauses.values()),'personas_nuevas_con_codigo_entre_1016':len({k for k in foc if not oh[k] and nh[k]}),'observaciones_codigo_anual_recuperado':len(rec),'personas_codigo_anual_recuperado':len({r[0] for r in rec}),'observaciones_enlace_explicito_nuevo_codcli_carrera_plan_ano':newplan,'fuentes_anteriores':len(oldpaths),'archivos_adicionales_auditados_o_reparseados':len(hs),'archivos_distintos_total':sourcecount,'evidencias_adicionales':sum(len(v) for v in nh.values()),'inaccesibles':sum(r[5] in ['INACCESIBLE','INACCESIBLE_O_ERROR'] for r in cov),'DV_foco_validos':2317,'fuente_aun_no_revisada_atribuible_persona':'No se identificó un archivo individual inaccesible asignable a personas concretas; cobertura acotada, no exhaustividad universal.'}
(O/'EMBUDO_AGREGADO.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));(T/'embudo_privado.json').write_text(json.dumps(private,ensure_ascii=False));(O/'INVENTARIO_DIRIGIDO.json').write_text(json.dumps(cov,ensure_ascii=False,indent=2));(O/'HASHES_FUENTES.json').write_text(json.dumps(hs,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False))
