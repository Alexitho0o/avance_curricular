import json,hashlib,re,sys,csv
from pathlib import Path
from collections import defaultdict,Counter
import openpyxl
R=Path.cwd();O=R/'outputs/retencion_puente_provisional_20261023_v10';T=Path('/tmp/ipss_cohorte_original_20261023');hashes={}
def load(p):hashes[str(p)]=hashlib.sha256(Path(p).read_bytes()).hexdigest();return json.load(open(p))
p=load('/tmp/ipss_revision_63_20261022/payload.json');get=lambda n:next(s['rows'] for s in p if s['name']==n);allunits=get('CONTRASTE_63');v8=load('/tmp/ipss_cruce_historico_20261023/resultados.json');v9=load('/tmp/ipss_validacion_2165_20261023/resultados.json');closed={x[0] for x in v9 if x[44]};focus=[x for x in v8 if x[0] not in closed];assert len(focus)==3094 and len({x[1] for x in focus})==1751
G={(x['codcarpr'],x['sede'],x['jornada']):x for x in load(R/'data/versiones_por_cohorte/20261016/grupos_existentes.json')};M=load(R/'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json');offers=M['oferta_anual'];jm={'1':'D','2':'V','4':'O'};tp={'Plan Regular':'1','Plan Especial':'2','Plan Regular de Continuidad':'3'};val=lambda v:'' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip()
da=defaultdict(list);dasheets=[]
for sh in p:
 if sh['name'].startswith('DA_'):
  for row in sh['rows']:
   d=dict(zip(sh['headers'],row));da[d['REV_RUT_DV'],val(d['CODCLI']),d['CODCARPR'],d['JORNADA']].append(d)
  pp={x[1] for x in focus};hh=sh['headers'];dasheets.append({**sh,'rows':[x for x in sh['rows'] if x[hh.index('REV_RUT_DV')] in pp]})
# Reread only four known MU files; extract dates and reintegration, preserve source locations.
mu=defaultdict(list);sources=sorted({(e[7],e[8]) for e in get('ENLACES_ANUALES')})
for path,sheet in sources:
 hashes[path]=hashlib.sha256(Path(path).read_bytes()).hexdigest();w=openpyxl.load_workbook(path,read_only=True,data_only=True);it=iter(w[sheet].values);hh=next(it)
 for rn,row in enumerate(it,2):
  d=dict(zip(hh,row));old='MC_CODIGO_UNICO' in d;doc=val(d.get('MM_N_DOCUMENTO') if old else d.get('N_DOC'));dv=val(d.get('MM_DV') if old else d.get('DV')).upper()
  if not doc.isdigit() or not re.fullmatch('[0-9K]',dv):continue
  k=str(int(doc))+'-'+dv;year=val(d.get('MC_CAT_PERIODO') if old else d.get('ANIO_INFORMADO')).replace('MAT_','');code=val(d['MC_CODIGO_UNICO']) if old else 'I162S%sC%sJ%sV%s'%tuple(val(d[z]) for z in ['COD_SED','COD_CAR','JOR','VERSION']);actual=val(d.get('MM_ANIO_ACTUAL') if old else d.get('ANIO_ING_ACT'));origin=val(d.get('MM_ANIO_ORIGEN') if old else d.get('ANIO_ING_ORI'));ret=val(d.get('REINCORPORACION')) if not old else '';mu[k].append([year,code,actual,origin,ret,path,sheet,rn,'MM_ANIO_ACTUAL/MM_ANIO_ORIGEN' if old else 'ANIO_ING_ACT/ANIO_ING_ORI/REINCORPORACION'])
 w.close()
def uniqyear(v):
 vv={int(x) for x in v if str(x).isdigit() and 2007<=int(x)<=2026};return next(iter(vv)) if len(vv)==1 else None

def predict(g,year):
 if not g:return [],[],'SIN_GRUPO'
 if year is None:return [],[],'FECHA_AUSENTE_O_MULTIPLE'
 prof={tuple(x) for x in g['perfiles_duracion_tipo']}
 if not prof:return [],[],'SIN_PERFIL'
 rows=[x for x in offers if x['anio']==year and x['codigo_unico'].rsplit('V',1)[0] in g['familias'] and (x['duracion_total'],tp.get(x['tipo_plan_sies'])) in prof]
 new=[x for x in rows if x['vigencia']=='Vigente con estudiantes nuevos'];codes=sorted({x['codigo_unico'] for x in new});return codes,rows,'UNICO' if len(codes)==1 else 'EMPATE_NUEVOS' if codes else 'SIN_OFERTA_NUEVOS_COMPATIBLE'
# retrospective: targets only consulted AFTER prediction. DA and MU cohort sources analyzed separately.
test=defaultdict(Counter);testpeople=defaultdict(lambda:defaultdict(set));examples=Counter();testsrows=[]
for r in allunits:
 if r[10] not in ['CONFIRMA_CODIGO_PROPUESTO_OBSERVADO','DIFIERE_CODIGO_PROPUESTO_OBSERVADO','CODIGO_ANUAL_UNICO_SIN_PROPUESTA_PREVIA']:continue
 k,cli,c,site,j,plan,y,t=r[:8];g=G.get((c,'RE',jm[j]));families=g['familias'] if g else [];es=[e for e in mu[k] if e[0]==y and e[1].rsplit('V',1)[0] in families];ds=da[k,cli,c,jm[j]];types={x[1] for x in g['perfiles_duracion_tipo']} if g else set();typ='REGULAR' if types=={'1'} else 'CONTINUIDAD' if types=={'3'} else 'TIPO_NO_UNICO';reentry='REINCORPORACION_REGISTRADA' if any(e[4].upper() in {'1','S','SI','SÍ','TRUE'} for e in es) else 'SIN_REINCORPORACION_ACREDITADA';dates={'DA_ANOINGRESO':uniqyear([val(d['ANOINGRESO']) for d in ds]),'MU_INGRESO_ACTUAL':uniqyear([e[2] for e in es]),'MU_INGRESO_ORIGEN':uniqyear([e[3] for e in es])}
 for method,year in dates.items():
  if typ=='CONTINUIDAD' and method!='MU_INGRESO_ACTUAL':out='EXCLUIDO_FECHA_NO_PROPIA_CONTINUIDAD';codes=[]
  else:
   codes,oo,status=predict(g,year);out=('ACIERTO' if codes[0]==r[9] else 'ERROR') if len(codes)==1 else status
  test[method,typ][out]+=1;testpeople[method,typ][out].add(k);test[method,reentry][out]+=1
  testsrows.append([k,cli,c,j,plan,y,t,method,year,typ,reentry,'; '.join(codes),r[9],out,'FECHA_PLAN_EFECTIVA_NO_ACREDITADA'])
  if method=='MU_INGRESO_ACTUAL' and out in ['ERROR','ACIERTO']:examples[c,j,y,year,'; '.join(codes),r[9],out]+=1
# Focal application: dates and admission candidates, no automatic temporal carry-over.
results=[];evidence=[];candidate_rows=[];counts=Counter();ag=defaultdict(lambda:[0,set()]);newindex=load('/tmp/ipss_embudo_2317_20261022/evidencias_nuevas.json');ni=defaultdict(list)
for e in newindex:
 if e[4]=='COMPLETO':ni[e[0]].append(e)
manual=load(R/'data/diccionario_sies_umas/20261015/evidencia/caracterizacion_reglas_y_fuentes.json')['equivalencias_manual_fcu2026']['filas'];manual={(d['CODCARPR'],d['SEDE'],d['JORNADA']):d['CODIGO_UNICO_SIES'] for d in manual}
for r in focus:
 rid,k,cli,c,site,j,plan,y,t=r[:9];g=G.get((c,'RE',jm[j]));families=g['familias'] if g else [];es=[e for e in mu[k] if e[1].rsplit('V',1)[0] in families];annual=[e for e in es if e[0]==y];ds=da[k,cli,c,jm[j]];dy=uniqyear([val(d['ANOINGRESO']) for d in ds]);ay=uniqyear([e[2] for e in es]);oy=uniqyear([e[3] for e in es]);types={x[1] for x in g['perfiles_duracion_tipo']} if g else set();cont=types=={'3'};year=ay if cont else dy;label='MU_INGRESO_ACTUAL_OTROS_CORTES_NO_PLAN' if cont else 'DA_ANOINGRESO_CORTE_NO_PLAN';codes,oo,status=predict(g,year);pred=codes[0] if len(codes)==1 else '';direct=[e for e in ni[k] if e[1]=='MATRICULA' and e[2]==y and e[7]==cli and e[8]==c and e[6]==plan];directcodes={e[3] for e in direct};adopt='';state='PROPUESTA_CONDICIONADA_COHORTE_ADMISION' if pred else 'NO_DETERMINABLE_'+status
 if len(directcodes)==1 and (not pred or pred in directcodes):adopt=next(iter(directcodes));state='VINCULO_DOCUMENTAL_EXPLICITO'
 elif y=='2026' and pred and manual.get((c,'RE',jm[j]))==pred:adopt=pred;state='CORRESPONDENCIA_MANUAL_VIGENTE'
 missing='Fecha efectiva de ingreso/asignación a PLAN por CODCLI y antecedente de cambio o permanencia al reingreso'
 if len(codes)>1:missing='Versiones admitían nuevos en misma cohorte/perfil; falta atributo del plan o código individual de ingreso'
 elif not codes:missing='Año propio de carrera o perfil/oferta de admisión de esa cohorte, según estado de cálculo'
 if cont:missing+='; no heredar ingreso técnico ni interpretar MU actual como fecha de plan'
 allnew=sorted({x['codigo_unico'] for x in oo if x['vigencia']=='Vigente con estudiantes nuevos'});onlyold=sorted({x['codigo_unico'] for x in oo if x['vigencia']=='Vigente sin estudiantes nuevos'});retvals=sorted({e[4] for e in es if e[4]});results.append([rid,k,cli,c,site,j,plan,y,t,dy,ay,oy,year,label,cont,'; '.join(codes),'; '.join(onlyold),status,state,adopt,missing,'; '.join(retvals),'NO_ACREDITADO','NO_ACREDITADA',r[27]])
 for e in es:evidence.append([rid,*e])
 for d in ds:evidence.append([rid,val(d['ANOMATRICULA']),'',val(d['ANOINGRESO']),'','',d['REV_FUENTE'],d['REV_HOJA'],d['REV_FILA'],'ANOINGRESO/ANOMATRICULA; corte no acreditado'])
 for x in oo:candidate_rows.append([rid,x['anio'],x['codigo_unico'],x['duracion_total'],x['tipo_plan_sies'],x['modalidad'],x['vigencia'],json.dumps(x['fuente'],ensure_ascii=False)])
 counts[state]+=1;ag[c,j,y,state][0]+=1;ag[c,j,y,state][1].add(k)
accepted={x[0] for x in results if x[19]};unresolved={x[1] for x in results if not x[19]};yes={x[1] for x in results if x[19]};summary={'foco_observaciones':3094,'foco_personas':1751,'estados':dict(counts),'nuevas_resoluciones':len(accepted),'personas_completas':len(yes-unresolved),'personas_parciales':len(yes&unresolved),'pendiente_interno_personas':len(unresolved),'pendiente_interno_observaciones':3094-len(accepted),'universo_personas':5901,'pendiente_documental_personas_previo':1838,'fecha_original_plan_acreditada':0,'cambio_plan_acreditado':0,'oferta_estados':dict(Counter(x['vigencia'] for x in offers)),'pruebas':[{'fecha':k[0],'grupo':k[1],'observaciones':dict(v),'personas_no_aditivas':{a:len(b) for a,b in testpeople[k].items()}} for k,v in test.items()],'ejemplos_validacion':[[list(k),v] for k,v in examples.most_common(12)]}
for n,x in [('resultados.json',results),('evidencias.json',evidence),('candidatos.json',candidate_rows),('retrospectiva_privada.json',testsrows),('DA_foco.json',dasheets)]: (T/n).write_text(json.dumps(x,ensure_ascii=False))
(O/'RESULTADO.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));(O/'FUENTES_HASHES.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2))
with open(O/'DESGLOSE.csv','w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Carrera','Jornada','Ano','Estado','Observaciones','Personas_no_aditivas'])
 for kk,(n,pp) in sorted(ag.items()):w.writerow([*kk,n,len(pp)])
assert len(results)==3094 and all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items());print(json.dumps(summary,ensure_ascii=False))
