"""Validación separada de cifras congeladas, períodos UMAS y pertenencia curricular."""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction
from decimal import Decimal, localcontext
from datetime import datetime,timezone
import csv,json,hashlib,subprocess,re
import pandas as pd
import openpyxl
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT).decode().strip()
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def writecsv(n,rows):
 with (OUT/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=';');w.writeheader();w.writerows(rows)
def norm(x):
 if x is None:return ''
 if isinstance(x,float) and x.is_integer():return str(int(x))
 s=str(x).strip().upper();return '' if s in ('NULL','NAN','NONE') else s
checks=[]
def ck(n,e,o):
 checks.append({'control':n,'esperado':e,'observado':o,'clase':'B/C','estado':'PASS' if e==o else 'FAIL'})
start={'rama':git('branch','--show-current'),'head':git('rev-parse','HEAD')}
protected={p:sha(ROOT/p) for p in git('diff','--name-only','HEAD').splitlines() if (ROOT/p).is_file()}
prior_paths=['outputs/avance_historico_fase1_20261027/MANIFEST_FASE1.json','outputs/avance_historico_fase1_20261027/RESULTADOS.json','outputs/avance_historico_identidad_h113_20261027/RESULTADOS.json','outputs/avance_historico_fase2_candidata_644_20261027/MANIFEST.json','outputs/avance_historico_fase2_candidata_644_20261027/RESULTADOS.json','outputs/cierre_interno_iinf_reconocimientos_20261026/DECISION_Y_REGISTRO.json','outputs/avance_interno_preparacion_20261027/COBERTURA_AGREGADA.json']
priors={p:sha(ROOT/p) for p in prior_paths}
m=json.loads((ROOT/prior_paths[0]).read_text());sources=m['fuentes'].copy()
prof=json.loads((ROOT/prior_paths[-1]).read_text())['fuentes']
for label,name in [('prom12166','PROMEDIOSDEALUMNOS_12166.xlsx'),('listado','Listado_Planes_estudio_Sedes RE+CO.xlsx')]:sources[label]=prof[name]
old=json.loads((ROOT/'outputs/avance_historico_origen_h113_20261027/MANIFEST_ORIGEN_H113.json').read_text());sources['prom7804']=old['fuentes']['promedios']
for k,v in sources.items():ck('Hash entrada '+k,v['sha256'],sha(v['ruta']))
assert all(c['estado']=='PASS' for c in checks)
active=ROOT/'data/diccionario_sies_seguimiento/activo.json';active_hash=sha(active);a=json.loads(active.read_text());d=json.loads((ROOT/a['descriptor']).read_text());db=d['base_privada']
ck('Base vigente hash',db['sha256'],sha(db['ruta']))
# Hito 3.1: reutilizar salidas anuales, sin regenerar los cálculos heredados.
def heads(label,sheet):
 w=openpyxl.load_workbook(sources[label]['ruta'],read_only=True,data_only=True);h=next(w[sheet].values);w.close();return list(h)
ch=heads('h112b_excel','03_CARGA_SIES_16769_21C');sh=heads('h114b_excel','04_CSV_CON_TITULOS')
def csvread(label,hs):
 raw=Path(sources[label]['ruta']).read_bytes()
 try:text=raw.decode('utf-8-sig')
 except UnicodeDecodeError:text=raw.decode('cp1252')
 rows=list(csv.reader(text.splitlines(),delimiter=';'));assert all(len(r)==len(hs) for r in rows)
 return [dict(zip(hs,r)) for r in rows]
careers=csvread('h112b_csv',ch);h113=csvread('h113_csv',sh);h114=csvread('h114b_csv',sh)
key=lambda r:(r['CODIGO_UNICO'],r['PLAN_ESTUDIOS'])
cm={key(r):r for r in careers}; ck('43 planes',43,len(cm));ck('2371 filas precarga',2371,len(h113));ck('2371 filas H114B',2371,len(h114))
metrics=['UNIDADES_CURSADAS','UNIDADES_APROBADAS','UNID_CURSADAS_TOTAL','UNID_APROBADAS_TOTAL']
annual={};ratioerrors=0;numeric_errors=Counter();flags=Counter()
for r,s in zip(h113,h114):
 assert key(r)==key(s) and key(r) in cm
 k=key(r);n=int(cm[k]['TOTAL_UNIDADES_MEDIDA'])
 z=annual.setdefault(k,{'codigo_sies':k[0],'plan_sies':k[1],'carrera':cm[k]['NOMBRE_CARRERA'],'registros':0,'unidades_plan':n,'denominador_plan_sumado':0,'cursadas_anual':0,'aprobadas_anual':0,'cursadas_acumuladas':0,'aprobadas_acumuladas_H113':0,'aprobadas_acumuladas_H114B':0,'H113_sobre_plan':0,'H113_sobre_125pct_plan':0,'H114B_sobre_125pct_plan':0})
 z['registros']+=1;z['denominador_plan_sumado']+=n
 for f,c in [('cursadas_anual',metrics[0]),('aprobadas_anual',metrics[1]),('cursadas_acumuladas',metrics[2]),('aprobadas_acumuladas_H113',metrics[3])]:z[f]+=int(r[c])
 z['aprobadas_acumuladas_H114B']+=int(s[metrics[3]])
 for version,x in [('H113',r),('H114B',s)]:
  vals=[int(x[c]) for c in metrics]
  numeric_errors[version+'_negativos']+=sum(v<0 for v in vals)
  numeric_errors[version+'_aprobadas_anual_sobre_cursadas']+=vals[1]>vals[0]
  numeric_errors[version+'_aprobadas_acum_sobre_cursadas']+=vals[3]>vals[2]
  flags[version+'_sobre_plan']+=vals[3]>n;flags[version+'_sobre_125pct_plan']+=4*vals[3]>5*n
 z['H113_sobre_plan']+=int(r[metrics[3]])>n;z['H113_sobre_125pct_plan']+=4*int(r[metrics[3]])>5*n;z['H114B_sobre_125pct_plan']+=4*int(s[metrics[3]])>5*n
for z in annual.values():
 for name,num,den in [('aprobacion_anual_observada','aprobadas_anual','cursadas_anual'),('avance_acumulado_H113_observado','aprobadas_acumuladas_H113','denominador_plan_sumado'),('avance_acumulado_H114B_observado','aprobadas_acumuladas_H114B','denominador_plan_sumado')]:
  z[name]=float(Fraction(z[num],z[den])) if z[den] else None
  if z[den]:ratioerrors+=abs(Decimal(str(z[name]))-Decimal(z[num])/Decimal(z[den]))>Decimal('1e-14')
 z['clasificacion']='B/C';z['estado']='REPRODUCCION_CONGELADA_NO_CERTIFICA_VALIDEZ_DE_ATRIBUCION'
ck('Dos métodos cocientes',0,ratioerrors);ck('Controles aritméticos negativos/orden',0,sum(numeric_errors.values()))
writecsv('ANUAL_43_CODIGOS_PLAN.csv',list(annual.values()))
totals={col:sum(z[col] for z in annual.values()) for col in ['registros','denominador_plan_sumado','cursadas_anual','aprobadas_anual','cursadas_acumuladas','aprobadas_acumuladas_H113','aprobadas_acumuladas_H114B']}
ck('Control totales congelados',[2371,96104,21389,17628,47205,41627,38235],list(totals.values()))
# Hito 3.3: catálogo de asignaturas, manteniendo diferencias de sede.
w=openpyxl.load_workbook(sources['listado']['ruta'],read_only=True,data_only=True);it=w['BBDD Bruta'].values;headers=[norm(x) for x in next(it)]
plans=defaultdict(lambda:defaultdict(set));levels=defaultdict(lambda:defaultdict(set));types=Counter()
for row in it:
 r={h:norm(v) for h,v in zip(headers,row)};k=(r['CODCARR'],r['CODPESTUD']);code=r['CODRAMO']
 if not all(k) or not code:continue
 plans[k][r['SEDE']].add(code);levels[k][code].add(r['NIVEL']);types[r['TIPO']]+=1
w.close()
resolved={k:next(iter(ss.values())) for k,ss in plans.items() if len({tuple(sorted(v)) for v in ss.values()})==1}
# Hitos 3.2 y 3.3: extraer por separado; nunca unir fotografías ni inferir vigencia histórica.
period_rows=[];plan_rows=[];source_stats={};levels_rows=[];identifiers=set()
for label in ['prom7804','prom12166']:
 print('Leyendo '+label,flush=True)
 f=pd.read_excel(sources[label]['ruta'],sheet_name='Hoja1',dtype=str,keep_default_na=False)
 f.columns=[norm(x) for x in f.columns]
 req=['RUT','DIG','CODCLI','CODCARR','PLAN_DE_ESTUDIO','JORNADA','ANO','PERIODO','CODRAMO','CODSECC','ESTADO','NOTA_FINAL','CONVALIDADO','RAMOEQUIV','NIVEL','REGIMEN']
 assert set(req)<=set(f.columns)
 f=f[req].copy()
 for c in req:f[c]=f[c].map(norm)
 f['_BODY']=f['RUT'].str.replace(r'[.\s]','',regex=True).str.lstrip('0');f['_DV']=f['DIG']
 f['_VALID']=f['_BODY'].str.fullmatch(r'\d+')&f['_DV'].str.fullmatch(r'[0-9K]')&f['CODCLI'].ne('')
 valid=f[f['_VALID']].copy();valid['_PE']=valid['_BODY']+'-'+valid['_DV']
 identifiers.update(valid['_PE']);identifiers.update(valid['_BODY']);identifiers.update(valid['CODCLI'])
 # Permite contrastar duplicados de evento sin alterar la fila RAW ni adoptar nuevo motor.
 cols=['_PE','CODCLI','CODCARR','PLAN_DE_ESTUDIO','JORNADA','ANO','PERIODO','CODRAMO','CODSECC','ESTADO','NOTA_FINAL','CONVALIDADO','RAMOEQUIV','NIVEL','REGIMEN']
 events=valid.drop_duplicates(cols).copy()
 # Guardar también estados no reconocidos/blancos; no transformarlos en reprobar/no retenido.
 raw_per={k:len(g) for k,g in valid.groupby(['ANO','PERIODO'],dropna=False)}
 for (year,per),g in events.groupby(['ANO','PERIODO'],dropna=False):
  c=Counter(g['ESTADO']);active_events=g[g['ESTADO'].isin(['A','R'])]
  period_rows.append({'fuente':label,'ano_UMAS':year,'periodo_UMAS':per,'filas_RAW_identidad_comparable':raw_per[(year,per)],'eventos_unicos_observados':len(g),'personas_observadas':g['_PE'].nunique(),'expedientes_observados':len(g[['_PE','CODCLI']].drop_duplicates()),'eventos_A':c['A'],'eventos_R':c['R'],'eventos_E':c['E'],'eventos_I':c['I'],'eventos_otro_o_sin_resultado':sum(n for k,n in c.items() if k not in ('A','R','E','I')),'personas_con_resultado_A_R':active_events['_PE'].nunique(),'clasificacion':'B/C','lectura':'ACTIVIDAD_NO_RETENCION_NI_ESTADO_HISTORICO'})
 ck('Eventos por período '+label,len(events),sum(x['eventos_unicos_observados'] for x in period_rows if x['fuente']==label))
 # Perfil del último conjunto observado por expediente-plan-jornada, no plan obligatorio certificado.
 aggregate={};exp_status=Counter();statusmulti=0
 for (pe,cli,car,pl,jor),g in events.groupby(['_PE','CODCLI','CODCARR','PLAN_DE_ESTUDIO','JORNADA'],dropna=False):
  pk=(car,pl);codes=resolved.get(pk)
  st='LISTADO_EXACTO_DISPONIBLE_VIGENCIA_PENDIENTE' if codes else 'PLAN_CON_SEDES_DIFERENTES' if pk in plans else 'PLAN_NO_LOCALIZADO'
  exp_status[st]+=1
  z=aggregate.setdefault((car,pl,jor),{'fuente':label,'carrera_UMAS':car,'plan_UMAS':pl,'jornada_UMAS':jor,'expediente_plan_jornada':0,'estado_listado':st,'unidades_listadas':len(codes) if codes else None,'denominador_listado_sumado':0 if codes else None,'aprobadas_A_distintas_en_listado':0,'reconocidas_E_I_distintas_en_listado':0,'logradas_A_E_I_distintas_en_listado':0,'aprobadas_A_distintas_fuera_listado':0,'reconocidas_E_I_distintas_fuera_listado':0,'expedientes_con_logros_fuera_listado':0,'ratio_observado_contra_listado':None,'avance_historico_validado':None,'clasificacion':'B/C/E','pendiente':'VIGENCIA_COMPLETITUD_PLAN_Y_EQUIVALENCIAS; NO_ES_NUEVA_TASA_SIES'})
  z['expediente_plan_jornada']+=1
  approved=set(g.loc[g['ESTADO']=='A','CODRAMO'])-{''};recognized=set(g.loc[g['ESTADO'].isin(['E','I']),'CODRAMO'])-{''}
  if codes:
   z['denominador_listado_sumado']+=len(codes);z['aprobadas_A_distintas_en_listado']+=len(approved&codes);z['reconocidas_E_I_distintas_en_listado']+=len(recognized&codes);z['logradas_A_E_I_distintas_en_listado']+=len((approved|recognized)&codes)
   z['aprobadas_A_distintas_fuera_listado']+=len(approved-codes);z['reconocidas_E_I_distintas_fuera_listado']+=len(recognized-codes);z['expedientes_con_logros_fuera_listado']+=bool((approved|recognized)-codes)
  else:
   # Desconocido no es cero: no clasificar pertenencia cuando no hay malla resoluble.
   for field in ['aprobadas_A_distintas_en_listado','reconocidas_E_I_distintas_en_listado','logradas_A_E_I_distintas_en_listado','aprobadas_A_distintas_fuera_listado','reconocidas_E_I_distintas_fuera_listado','expedientes_con_logros_fuera_listado']:z[field]=None
 for z in aggregate.values():
  if z['denominador_listado_sumado']:
   z['ratio_observado_contra_listado']=float(Fraction(z['logradas_A_E_I_distintas_en_listado'],z['denominador_listado_sumado']))
   assert 0<=z['ratio_observado_contra_listado']<=1
 plan_rows.extend(aggregate.values())
 # Nivel de ramo: contraste exacto de valor, no nivel completado ni calendario.
 lc=Counter()
 for (car,pl,ramo,level),g in events.groupby(['CODCARR','PLAN_DE_ESTUDIO','CODRAMO','NIVEL'],dropna=False):
  choices=levels.get((car,pl),{}).get(ramo,set())
  state='NIVEL_COINCIDE_LISTADO' if level and choices=={level} else 'NIVEL_ENTRE_VARIOS_DEL_LISTADO' if level and level in choices else 'NIVEL_DIFIERE_LISTADO' if choices and level else 'SIN_NIVEL_O_RAMO_EN_LISTADO'
  lc[state]+=len(g)
 source_stats[label]={'filas_RAW':len(f),'filas_identidad_comparable':len(valid),'filas_sin_llave_documental_completa':len(f)-len(valid),'eventos_despues_deduplicacion_diagnostica':len(events),'repeticiones_exactas_evento':len(valid)-len(events),'eventos_sin_ano_o_periodo':int((events['ANO'].eq('')|events['PERIODO'].eq('')).sum()),'personas_observadas':events['_PE'].nunique(),'expedientes_persona_codcli':len(events[['_PE','CODCLI']].drop_duplicates()),'expediente_plan_jornada':sum(exp_status.values()),'estados_listado':dict(exp_status),'niveles_comparacion_eventos':dict(lc),'anos_observados':sorted(events['ANO'].unique()),'periodos_observados':sorted(events['PERIODO'].unique()),'limite':'Extractos separados; cobertura completa no certificada. Ningún estado actual se retroproyecta.'}
 ck('Partición filas RAW '+label,len(f),len(valid)+source_stats[label]['filas_sin_llave_documental_completa'])
 ck('Partición nivel eventos '+label,len(events),sum(lc.values()))
 ck('Partición expediente-plan-jornada '+label,sum(exp_status.values()),sum(z['expediente_plan_jornada'] for z in aggregate.values()))
 print(json.dumps({label:source_stats[label]},ensure_ascii=False),flush=True)
writecsv('PERIODOS_UMAS_OBSERVADOS.csv',period_rows);writecsv('MALLAS_CARRERA_PLAN_JORNADA.csv',plan_rows)
# Fórmulas de referencia, bases y decisión pendiente explícitas.
formulas=[
 {'indicador':'Aprobación anual observada','formula':'SUMA(aprobadas_anuales)/SUMA(cursadas_anuales)','unidad':'Unidades; no retención','clase':'C','condicion':'Mismo universo/unidad/carrera; denominador cero => Pendiente'},
 {'indicador':'Avance acumulado respecto plan','formula':'SUMA(aprobadas_acumuladas_aplicables)/SUMA(unidades_plan_por_registro)','unidad':'Unidades del plan','clase':'A definición p4g; C agregación','condicion':'No promediar tasas simples; confirmar plan, año, atribución y reconocimientos'},
 {'indicador':'Actividad por período','formula':'Conteo distinto persona+CODCLI con resultado A/R en ANO+PERIODO','unidad':'Expedientes observados','clase':'C','condicion':'No equivale a matrícula vigente ni abandono; no convertir PERIODO sin tabla aplicable'},
 {'indicador':'Aprobaciones frente al listado','formula':'CARDINAL((CODRAMO_A UNION CODRAMO_E_I) INTERSECCION ramos_listados)/CARDINAL(ramos_listados)','unidad':'Asignaturas distintas por expediente-plan','clase':'C/E','condicion':'Diagnóstico, no indicador final: no homologar por nombre; malla desconocida => Pendiente'},
 {'indicador':'Nivel curricular','formula':'Comparar NIVEL del ramo contra NIVEL del mismo CODRAMO en carrera+plan','unidad':'Nivel asignado a ramo','clase':'B/C','condicion':'No equivale a nivel completado ni a trimestre'},
 {'indicador':'Transformación H114B','formula':'MIN(aprobadas_acumuladas_H113; total_plan; cursadas_acumuladas_H113)','unidad':'Unidades','clase':'C histórica','condicion':'Solo reproducción histórica; no aplicar un límite100% universal como si fuera A'}]
dump('FORMULAS_Y_ALCANCE.json',formulas)
result={'clase':'B/C/E','fase':3,'hitos':{'3.1':'VALIDACION_MATEMATICA_CONGELADA; ATRIBUCION_INTEGRAL_PENDIENTE','3.2':'PERFIL_POR_PERIODO_LITERAL_COMPLETADO; COBERTURA_Y_CALENDARIO_PENDIENTES','3.3':'PERTENENCIA_EXACTA_A_LISTADO_CALCULADA; VIGENCIA_Y_EQUIVALENCIAS_PENDIENTES'},'candidata_644_aplicada':False,'totales_congelados':totals,'cocientes_observados':{'aprobacion_anual':totals['aprobadas_anual']/totals['cursadas_anual'],'avance_acumulado_H113':totals['aprobadas_acumuladas_H113']/totals['denominador_plan_sumado'],'avance_acumulado_H114B':totals['aprobadas_acumuladas_H114B']/totals['denominador_plan_sumado']},'alertas_limite_plan':dict(flags),'errores_aritmeticos':dict(numeric_errors),'extractos_internos_separados':source_stats,'listado':{'carrera_plan':len(plans),'sin_divergencia_de_ramos_entre_sedes':len(resolved),'con_divergencia_de_ramos_entre_sedes':len(plans)-len(resolved),'tipos_filas':dict(types)},'filas_tabla_mallas':len(plan_rows),'limite':'No hay nueva tasa oficial ni avance final aprobado; el listado no certifica vigencia/completitud histórica. Los estados A/E/I/R son códigos observados de resultado, no VIG.'}
dump('RESULTADOS.json',result)
for k,v in sources.items():ck('Fuente preservada '+k,v['sha256'],sha(v['ruta']))
for p,hsh in priors.items():ck('Auditoría previa preservada '+p,hsh,sha(ROOT/p))
for p,hsh in protected.items():ck('Cambio previo preservado '+p,hsh,sha(ROOT/p))
ck('Diccionario preservado',db['sha256'],sha(db['ruta']));ck('Activo preservado',active_hash,sha(active));ck('HEAD preservado',start['head'],git('rev-parse','HEAD'));ck('Rama preservada',start['rama'],git('branch','--show-current'))
pattern=re.compile(r'(?<![A-Za-z0-9])(?:'+'|'.join(re.escape(x) for x in sorted(identifiers,key=len,reverse=True) if len(x)>=5)+r')(?![A-Za-z0-9])')
public=[OUT/n for n in ['ANUAL_43_CODIGOS_PLAN.csv','PERIODOS_UMAS_OBSERVADOS.csv','MALLAS_CARRERA_PLAN_JORNADA.csv','FORMULAS_Y_ALCANCE.json','RESULTADOS.json']]
ck('Identificadores en archivos agregados',[],[p.name for p in public if pattern.search(p.read_text())])
status='PASS_CALCULOS_CON_PENDIENTES' if all(x['estado']=='PASS' for x in checks) else 'FAIL'
dump('QA.json',{'estado':status,'controles':checks,'limite':'PASS de cálculos y preservación; no cierre integral, asignación nueva ni autorización de carga.'})
dump('CHECKPOINT.json',{'fase':3,'estado':status,'fase4_autorizada_por_este_QA':False,'proximo':'Decidir alcance de versión provisional o cerrar atribución/plan. No repetir controles congelados. Los644 siguen pendientes de aprobación; no condicionan el perfil interno, sí la atribución SIES correspondiente.','bloqueos':['Atribución integral pendiente y 644 no activados','Vigencia/completitud histórica de mallas y equivalencias generales','Calendario de períodos UMAS aplicable; no convertir automáticamente','Cobertura de extractos no certificada, especialmente12166','Caso P sin puente completo y27 discrepancias de identidad previamente documentadas']})
dump('MANIFEST.json',{'fecha_utc':datetime.now(timezone.utc).isoformat(),'proceso':'Avance curricular histórico IPSS162','fuentes':sources,'auditorias_reutilizadas':priors,'manual_aplicable':'SIES2026 datos2025; pp2-6; extensión histórica interna C','diccionario':{'edicion':d['edicion'],'base_sha256':db['sha256'],'activo_sha256':active_hash},'git_antes':start,'git_despues':{'rama':git('branch','--show-current'),'head':git('rev-parse','HEAD')},'salidas':{p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='MANIFEST.json'},'especificacion_sha256':sha(ROOT/'docs/ESPECIFICACION_AVANCE_HISTORICO_FASE3_20261027.md'),'commit':False,'push':False,'fuentes_denominadores_inalterados':True,'datos_individuales_exportados':False})
print(json.dumps({'qa':status,'controles':len(checks),'totales':totals,'ratios':result['cocientes_observados'],'alertas':dict(flags)},ensure_ascii=False,indent=2))
if status=='FAIL':raise SystemExit(1)
