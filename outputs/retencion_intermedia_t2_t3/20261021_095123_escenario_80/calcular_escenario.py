from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib,openpyxl,datetime,copy
P=Path(__file__).resolve().parent;R=Path('/Users/alexi/Documents/GitHub/avance_curricular')
# Exact population from the previous diagnostic, entirely in memory. No prior output is rewritten.
prior=R/'outputs/retencion_intermedia_t2_t3/20261021_093412_git_onedrive_mu2025'
pre=(prior/'reconstruir_pasos.py').read_text().split('ct=collections.Counter();')[0]
task_file=__file__;__file__=str(prior/'reconstruir_pasos.py')
exec(compile(pre,'poblacion83_solo_memoria','exec'));__file__=task_file;P=Path(__file__).resolve().parent
marks={k:stages['Final a carga'][k]['ARREGLO'] for k in persons}
selected={k for k,v in marks.items()if v in ['2+3 INGRESO','CORRECCIÓN']};assert len(selected)==80
classlabels={k:marks[k]for k in selected}
def st(x):return ''if x is None else str(int(x))if isinstance(x,float)and x.is_integer()else str(x).strip()
def person(r):return (st(r['TIPO_DOC']),st(r['N_DOC']),st(r['DV']).upper())
def rutstr(r):return key(r['N_DOC'],r['DV'])if st(r['TIPO_DOC'])=='R'else None
def coh(r):return(st(r['ANIO_ING_ORI']),st(r['SEM_ING_ORI']))
def positive(r):return float(st(r['VIG']) or '-1')>=1
sources=json.loads((R/'outputs/retencion_intermedia_t2_t3/20261021_cambio_carrera_2024/FUENTES.json').read_text())+[{'ruta':spec['ruta'],'sha256':spec['sha256'],'hoja':'Final a carga / Carga_Completa (2) / Carga_Completa (3)'}]
def meta(path,sheet=None):
 p=Path(path);sources.append({'ruta':str(p),'hoja':sheet,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
def rows(path,sheet):
 w=openpyxl.load_workbook(path,read_only=True,data_only=True);it=w[sheet].iter_rows(values_only=True);hdr=[st(v)for v in next(it)];rr=[dict(zip(hdr,r))for r in it if any(x is not None for x in r)];w.close();return rr
diag=R/'outputs/retencion_primer_anio_ipss_162/20260930_000000/RETENCION_PRIMER_ANIO_IPSS_162_DIAGNOSTICO_BRECHAS_20260930.xlsx';meta(diag,'BASE_RETENCION_MU / 01_CATALOGO_CARRERA / 02_COHORTE_ELEGIBILIDAD')
raw=rows(diag,'BASE_RETENCION_MU');catalog=rows(diag,'01_CATALOGO_CARRERA');assert raw==mu
catidx=defaultdict(list)
for r in catalog:catidx[st(r['ANO'])+'|'+st(r['CODIGO_UNICO'])].append(r)
def calculate(data):
 idx=defaultdict(list)
 for i,r in enumerate(data):idx[(int(r['ANIO_INFORMADO']),person(r))].append(r)
 out=[]
 for i,r in enumerate(data):
  y=int(r['ANIO_INFORMADO']);co=coh(r);cu=f'I162S{st(r["COD_SED"])}C{st(r["COD_CAR"])}J{st(r["JOR"])}V{st(r["VERSION"])}';cs=catidx['OFE_'+str(y)+'|'+cu];cat=cs[0]if len(cs)==1 else None
  state='FUERA_COHORTE';nxt=[];ns=[]
  if 2022<=y<=2025 and co[0]==str(y) and co[1]in['1','2']:
   if st(r['VIG'])=='0':state='VIGENCIA_0'
   elif len(cs)!=1:state='CATALOGO_NO_UNIVOCO'
   elif st(cat['NIVEL_GLOBAL'])!='Pregrado':state='OTRO_NIVEL'
   elif st(cat['TIPO_CARRERA'])!='Plan Regular':state='PLAN_NO_REGULAR'
   elif st(cat['PLAN_ESPECIAL'])!='NO APLICA':state='PLAN_ESPECIAL'
   else:
    minimum={'Técnico de Nivel Superior':4,'Profesional Sin Licenciatura':6,'Profesional Con Licenciatura':8,'Licenciatura no conducente a título':8}.get(st(cat['NIVEL_CARRERA']))
    if minimum is None:state='CATEGORIA_PENDIENTE'
    elif float(cat['DURACION_ESTUDIOS'])<minimum:state='DURACION_INSUFICIENTE'
    else:
     active=[x for x in idx[(y,person(r))]if positive(x)and coh(x)==co];nxt=[x for x in idx[(y+1,person(r))]if positive(x)];ns=[x for x in nxt if coh(x)==co]
     state='DUPLICADO_PERSONA_COHORTE'if len(active)>1 else'COHORTE_INCONSISTENTE'if len(nxt)>len(ns)else'INCLUIDO'
  out.append({'indice':i,'estado':state,'N':int(state=='INCLUIDO'),'R':int(state=='INCLUIDO'and bool(ns)),'cu':cu,'carrera':st(cat['NOMBRE_CARRERA'])if cat else'CATALOGO_PENDIENTE'})
 return out
basecalc=calculate(raw)
def totals(data,calc,y):
 rs=[z for z,r in zip(calc,data)if int(r['ANIO_INFORMADO'])==y];n=sum(z['N']for z in rs);ret=sum(z['R']for z in rs)
 return {'cohorte':y,'N':n,'R':ret,'tasa':ret/n if n else None}
expected={2022:(305,224),2023:(366,258),2024:(558,326),2025:(1150,668)}
for y,(n,ret)in expected.items():
 t=totals(raw,basecalc,y);assert(t['N'],t['R'])==(n,ret),(y,t)
# Diagnostic counterfactual only: in-memory restoration of year ACT/ORI for the identified MU2025 row.
sim=[dict(r)for r in raw];affected=[]
for i,r in enumerate(sim):
 k=rutstr(r)
 if int(r['ANIO_INFORMADO'])==2025 and k in selected:
  assert st(r['ANIO_ING_ORI'])==st(r['ANIO_ING_ACT'])=='2025'
  assert st(r['COD_CAR'])in{st(v['COD_CAR'])for v in persons[k]['dest']}
  r['ANIO_ING_ACT']=2024;r['ANIO_ING_ORI']=2024;affected.append(i)
assert len(affected)==80
simcalc=calculate(sim)
mu26=defaultdict(list);mu24=defaultdict(list)
for r in raw:
 if int(r['ANIO_INFORMADO'])==2026:mu26[rutstr(r)].append(r)
 if int(r['ANIO_INFORMADO'])==2024:mu24[rutstr(r)].append(r)
ct=Counter();breakdown=Counter();statect=Counter();current_contrib={};missingcohort=Counter()
for i in affected:
 r=raw[i];k=rutstr(r);nxt=mu26[k];vig1=any(st(x['VIG'])=='1'for x in nxt);positive_=any(positive(x)for x in nxt)
 presence='AUSENTE_MU2026'if not nxt else'CON_VIG1'if vig1 else'CON_VIG2_SIN_VIG1'if positive_ else'SOLO_VIG0'
 origins=' / '.join(sorted({st(x['ANIO_ING_ORI'])+':'+st(x['SEM_ING_ORI'])for x in nxt}))or'SIN_REGISTRO'
 label=classlabels[k];term=persons[k]['term'];b=basecalc[i]
 ct[presence]+=1;statect[b['estado']]+=1
 breakdown[(label,term,presence,b['estado'],b['R'],origins)]+=1
 if mu24[k]:missingcohort['CON_FILA_MU2024']+=1
 else:missingcohort['SIN_FILA_MU2024']+=1
currentN=sum(basecalc[i]['N']for i in affected);currentR=sum(basecalc[i]['R']for i in affected)
summary=[]
for y in [2024,2025]:
 t=totals(raw,basecalc,y);q=totals(sim,simcalc,y)
 fixed_indices=[i for i,r in enumerate(raw) if int(r['ANIO_INFORMADO'])==y and basecalc[i]['N']==1]
 fixed_ret=sum(simcalc[i]['R'] for i in fixed_indices)
 summary.append({'cohorte':y,'actual_C':t,'escenario_E_C':q,'delta_N_simulado':q['N']-t['N'],'delta_R_simulado':q['R']-t['R'],'delta_pp':100*(q['tasa']-t['tasa']),'sensibilidad_numerador_a_denominador_fijo':{'N_actual_fijo':t['N'],'R_sobre_poblacion_actual_fija':fixed_ret,'tasa_poblacion_actual_fija':fixed_ret/t['N'],'delta_pp':100*(fixed_ret-t['R'])/t['N'],'advertencia':'Seguimiento de la misma población actualmente incluida; los nuevos elegibles hipotéticos se muestran solo en escenario separado.'}})
# Program-level aggregate changes; no individual keys stored.
program=defaultdict(lambda:{'personas_reclasificadas':0,'N_actual':0,'R_actual':0,'N_escenario':0,'R_escenario':0,'VIG1_MU2026':0,'VIG0_MU2026':0,'ausente_MU2026':0})
for i in affected:
 r=raw[i];k=rutstr(r);b=basecalc[i];q=simcalc[i];z=program[(b['cu'],b['carrera'])]
 z['personas_reclasificadas']+=1;z['N_actual']+=b['N'];z['R_actual']+=b['R'];z['N_escenario']+=q['N'];z['R_escenario']+=q['R'];nxt=mu26[k]
 if any(st(x['VIG'])=='1'for x in nxt):z['VIG1_MU2026']+=1
 elif nxt:z['VIG0_MU2026']+=1
 else:z['ausente_MU2026']+=1
changes24=Counter((basecalc[i]['estado'],simcalc[i]['estado'],basecalc[i]['N'],simcalc[i]['N'],basecalc[i]['R'],simcalc[i]['R'])for i,r in enumerate(raw)if int(r['ANIO_INFORMADO'])==2024 and(basecalc[i]['N'],basecalc[i]['R'])!=(simcalc[i]['N'],simcalc[i]['R']))
res={'transiciones_calculo_2024':[{'estado_actual':a,'estado_escenario':b,'N_actual':n0,'N_escenario':n1,'R_actual':r0,'R_escenario':r1,'filas':n}for(a,b,n0,n1,r0,r1),n in changes24.items()],'fecha':datetime.datetime.now().astimezone().isoformat(),'clasificacion':'B observaciones; C cálculo; E escenario hipotético no aplicado; D denominadores actuales preservados','poblacion':80,'marcas':dict(Counter(classlabels.values())),'cruce_MU2026':dict(ct),'presencia_MU2024':dict(missingcohort),'estado_actual_2025':dict(statect),'aporte_actual_2025':{'N':currentN,'R':currentR,'no_retenidos_incluidos':currentN-currentR},'resultados':summary,'desglose':[{'marca':m,'periodo_2024':t,'MU2026':p,'estado_calculo_actual':e,'N_RETENIDO_actual':r,'origenes_MU2026':o,'personas':n}for(m,t,p,e,r,o),n in sorted(breakdown.items())],'por_programa':[{'codigo_unico':cu,'carrera':name,**v}for(cu,name),v in sorted(program.items())],'fuentes':sources,'supuesto_escenario_E':'Solo en memoria, restaurar ANIO_ING_ACT y ANIO_ING_ORI a 2024 en las 80 filas MU2025; conservar semestres informados, VIG, programas, MU2024 y MU2026 y lógica de cálculo. Los denominadores simulados no sustituyen los actuales. No agregar estudiantes sin fila MU2024.','QA':{'base_formula_reproducida':True,'control_actual_2024':[558,326],'control_actual_2025':[1150,668],'registros_modificados_solo_memoria':80,'conteos_grupo_cierran':sum(ct.values())==80,'fuentes_originales_sin_escritura':True,'archivos_individuales_generados':False}}
(P/'RESULTADOS_ESCENARIO_AGREGADOS.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in res.items()if k not in ['fuentes','por_programa','desglose']},ensure_ascii=False,indent=2))
wb.close()
