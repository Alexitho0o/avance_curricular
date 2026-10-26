from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib,datetime,contextlib,io,re,subprocess,openpyxl

with contextlib.redirect_stdout(io.StringIO()):
 exec(compile(Path(__file__).resolve().with_name('seleccion_y_exploracion.py').read_text(),'exploracion_solo_memoria','exec'))
R=Path('/Users/alexi/Documents/GitHub/avance_curricular')
stamp=datetime.datetime.now().astimezone().strftime('%Y%m%d_%H%M%S')
OUT=R/'outputs/retencion_intermedia_t2_t3'/f'{stamp}_llaves_20_codcli'
sources=[]
def source(p,s,expected=None):
 p=Path(p);h=digest(p)
 if expected:assert h==expected,(p,'hash cambió')
 if not any(x['ruta']==str(p) and x['hoja']==s for x in sources):sources.append({'ruta':str(p),'hoja':s,'sha256':h,'clasificacion':'B fuente institucional / C derivado técnico'})
def canonical(v):return txt(v).replace('.','').replace(' ','')
source(rawpath,'BASE_RETENCION_MU','19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd')
source(engpath,'02_COHORTE_ELEGIBILIDAD / 01_CATALOGO_CARRERA','5f0f7c7f0f238556de374d287bf2931ccc8a93a5489f4c2f2b543befd38c77b3')
source(pp,'2025_carga!J (RUT), BU (N_DOC), BV (DV)','e2984ccdf22ecf35c46e1f77275fdd12cda47bd2d77a523860e2cd2cf90127f4')
population={txt(b['raw']['N_DOC']):b for b in targets};assert len(population)==20
aliases={}
for doc in population:
 ar={canonical(r.get('RUT')) for r in prepidx.get(doc,[]) if canonical(r.get('RUT'))}
 assert len(ar)==1,('alias no unívoco',len(ar))
 aliases[doc]=ar
assert len(set.union(*aliases.values()))==20
snapshots={}
for sid,p,h in files:
 source(p,'Hoja1',h);snapshots[sid]=ums[sid]
allsets=dict(snapshots)
def read_key_sheets(p,expected,sheets):
 source(p,' / '.join(sheets),expected)
 w=openpyxl.load_workbook(p,read_only=True,data_only=True)
 out=[];meta=[]
 for name in sheets:
  it=w[name].iter_rows(values_only=True);header=None;hr=None
  for i,row in enumerate(it,1):
   hh=[txt(v) for v in row]
   if 'CODCLI' in hh and 'RUT' in hh:header=hh;hr=i;break
   if i>=8:break
  if header is None:continue
  n=0
  for i,row in enumerate(it,hr+1):
   if any(v is not None for v in row):out.append(dict(zip(header,row)));n+=1
  meta.append({'hoja':name,'filas':n,'encabezado':hr,'CODCLI':True,'RUT':True})
 w.close();return out,meta
recent,rmeta=read_key_sheets(Path('/Users/alexi/Desktop/Caracterizacion_2026-10-20_2027_P1_082504/01_ENTRADAS/DATOSDEALUMNOS_12112.xlsx'),'fdd47d99b934479f39d8db6d00eceb40714d3b8c7baa1e3a89a9288b2b8bc471',['Hoja1'])
allsets['12112']=recent
inv=json.loads((R/'outputs/retencion_intermedia_t2_t3/20261021_093412_git_onedrive_mu2025/RESPALDOS_XLSX_INSPECCION.json').read_text())
oldspec=next(x for x in inv if Path(x['ruta']).name=='2025-2.xlsx')
hist,hm=read_key_sheets(Path(oldspec['ruta']),oldspec['sha256'],['Detalle1','Hoja1']);allsets['respaldo_2025_2']=hist
def direct_cli_sets(datasets):
 out={doc:set() for doc in population}
 for rows in datasets.values():
  ri=defaultdict(list)
  for r in rows:ri[canonical(r.get('RUT'))].append(r)
  for doc,aa in aliases.items():
   for a in aa:
    out[doc]|={txt(r['CODCLI']) for r in ri.get(a,[]) if txt(r.get('CODCLI'))}
 return out
cli=direct_cli_sets(allsets)
extra_meta=[]
if any(not cc for cc in cli.values()):
 gs=next(x for x in inv if Path(x['ruta']).name=='PROMEDIOSDEALUMNOS_2071.xlsx')
 grade,gm=read_key_sheets(Path(gs['ruta']),gs['sha256'],['Hoja1'])
 allsets['promedios_2071']=grade;extra_meta=gm;cli=direct_cli_sets(allsets)
cid_people=defaultdict(set)
for doc,cc in cli.items():
 for c in cc:cid_people[c].add(doc)
assert all(len(dd)==1 for dd in cid_people.values()),'CODCLI pertenece a dos objetivos'
observations={}
links={doc:set(aa) for doc,aa in aliases.items()}
for sid,rows in allsets.items():
 ci=defaultdict(list);ri=defaultdict(list)
 for r in rows:
  if txt(r.get('CODCLI')):ci[txt(r['CODCLI'])].append(r)
  ri[canonical(r.get('RUT'))].append(r)
 summary=Counter();observed={};state_counts=Counter();year_counts=Counter()
 for doc,cc in cli.items():
  direct=[r for aa in aliases[doc] for r in ri.get(aa,[])]
  found=[r for c in cc for r in ci.get(c,[])]
  collision=any(len({canonical(r.get('RUT')) for r in ci.get(c,[])})>1 for c in cc if ci.get(c))
  summary['personas_con_RUT_preparacion_exacto']+=bool(direct)
  summary['personas_con_CODCLI']+=bool(found)
  summary['personas_recuperadas_solo_CODCLI']+=bool(found) and not bool(direct)
  summary['personas_sin_CODCLI_en_fuente']+=not bool(found)
  summary['personas_CODCLI_ambiguo_dentro_de_fuente']+=collision
  observed[doc]={'found':found,'direct':direct,'collision':collision}
  if found:
   state_counts[' / '.join(sorted({txt(r.get('ESTADOACADEMICO','NO DISPONIBLE'))for r in found}))]+=1
   year_counts[' / '.join(sorted({txt(r.get('ANOMATRICULA','NO DISPONIBLE'))for r in found}))]+=1
  if found and not collision:links[doc]|={canonical(r.get('RUT')) for r in found if canonical(r.get('RUT'))}
 observations[sid]={'resumen':dict(summary),'personas':observed,'estados_UMAS_por_persona':dict(state_counts),'anios_matricula_por_persona':dict(year_counts)}
assert all(v['resumen']['personas_CODCLI_ambiguo_dentro_de_fuente']==0 for v in observations.values())
li=defaultdict(set)
for doc,aa in links.items():
 for a in aa:li[a].add(doc)
assert all(len(dd)==1 for dd in li.values()),'RUT observado se cruza con dos objetivos'
by_career=defaultdict(Counter)
for doc,t in population.items():
 ca=t['engine']['NOMBRE_CARRERA'];d=by_career[ca];d['personas']=d.get('personas',0)+1
 d['CODCLI_identificado']+=bool(cli[doc]);d['CODCLI_unico']+=len(cli[doc])==1;d['varios_CODCLI']+=len(cli[doc])>1
 for sid in ['11998','10246','12112']:
  ob=observations[sid]['personas'][doc]
  d[f'con_CODCLI_{sid}']+=bool(ob['found']);d[f'recuperado_solo_CODCLI_{sid}']+=bool(ob['found']) and not bool(ob['direct'])
closures=[]
ms=json.loads((R/'outputs/retencion_intermedia_t2_t3/20261020_215248/MANIFEST_REVISION.json').read_text())
for sp in ms['fuentes']:
 if sp.get('id') not in ['T2_2026','T3_2026']:continue
 p=Path(sp['path']);source(p,sp['sheet'],sp['sha256'])
 w=openpyxl.load_workbook(p,read_only=True,data_only=True);rr=records(w[sp['sheet']]);w.close()
 hh=set(rr[0]) if rr else set();hascli='CODCLI'in hh;counts=Counter();matched=set();states=Counter()
 for doc,cc in cli.items():
  found=[r for r in rr if txt(r.get('CODCLI'))in cc] if hascli else [r for r in rr if canonical(r.get('RUT'))in links[doc]]
  if found:
   matched.add(doc)
   if 'ESTADOACADEMICO'in hh:states[' / '.join(sorted({txt(r.get('ESTADOACADEMICO'))for r in found}))]+=1
   else:states['SIN_CAMPO_ESTADOACADEMICO']+=1
 searchable=sum(bool(cc)for cc in cli.values()) if hascli else 20
 closures.append({'fuente':sp['id'],'llave':'CODCLI exacto con puente documental explícito' if hascli else 'RUT exacto documentado por CODCLI, fuente sin CODCLI','tiene_CODCLI':hascli,'personas_con_llave_para_buscar':searchable,'personas_de_20_encontradas':len(matched),'no_localizadas_entre_personas_con_llave':searchable-len(matched),'sin_CODCLI_para_buscar':20-searchable,'estados_UMAS_observados':dict(states),'clasificacion':'B/C presencia; E fecha/cobertura del cierre no acreditadas'})
# MU2026 is not a closing T2/T3. Keep this diagnostic explicitly separate.
mu26=[]
for doc in population:
 aliases26=links[doc]
 found=[r for r in raw if r['ANIO_INFORMADO']==2026 and (canonical(txt(r['N_DOC'])+'-'+txt(r['DV'])) in aliases26 or (txt(r['TIPO_DOC'])=='P' and txt(r['N_DOC'])==doc))]
 mu26.append((doc,found))
mu26summary={'personas_de_20_con_fila_MU2026':sum(bool(rows)for doc,rows in mu26),'con_alguna_VIG1':sum(any(r['VIG']==1 for r in rows)for doc,rows in mu26),'solo_VIG0':sum(bool(rows)and all(r['VIG']==0 for r in rows)for doc,rows in mu26),'sin_fila_MU2026_por_identificadores_documentados':sum(not rows for doc,rows in mu26),'clasificacion':'B/C observación anual; no se actualizan N_RETENIDO ni denominadores'}
result={'fecha':datetime.datetime.now().astimezone().isoformat(),'proceso':'Retención intermedia IPSS162','cohorte':2025,'cierres_observados':['2026-T2','2026-T3'],'clasificacion':'B datos observados; C cruce técnico exacto; D preservación; E corte/cobertura y equivalencia normativa de documento no resueltos','fuentes':sources,'seleccion':{'personas':20,'TIPO_DOC':{'P':20},'DV_vacio':20,'N_DOC_numerico_9_digitos':20,'estado_motor':'INCLUIDO','origen':2025,'regla_anterior':'La llave de los listados se construyó solo para TIPO_DOC=R. Para P se dejó sin llave, no como ausencia.'},'puente_documental':{'fuente':'IPSS_Procesamiento.xlsx / 2025_carga','campos':['RUT (J)','N_DOC (BU)','DV (BV)'],'N_DOC_objetivo_con_RUT_explicito_unico':len(aliases),'RUT_documentados_distintos':len(set.union(*aliases.values())),'transformacion_C':'Se lee la correspondencia RUT↔N_DOC existente en la misma fila; no se deduce desde nombres, fecha de nacimiento o sexo, ni se convierte un pasaporte por una función inventada. Luego se recupera CODCLI por RUT exacto en fuentes UMAS y se sigue ese CODCLI conservando todas sus matrículas.','alcance_E':'Correspondencia observada de la preparación institucional 2025; no certifica que un RUT temporal sea un RUN oficial ni autoriza cambiar el documento informado a SIES.'},'CODCLI_identificado_personas':sum(bool(cc) for cc in cli.values()),'sin_CODCLI_identificado':sum(not cc for cc in cli.values()),'numero_CODCLI_por_persona':dict(Counter(str(len(cc))for cc in cli.values())),'CODCLI_distintos':len(cid_people),'fuentes_por_CODCLI':{sid:v['resumen']for sid,v in observations.items()},'programas':[{'carrera':ca,**dict(v),'clasificacion':'B/C'}for ca,v in sorted(by_career.items())],'metadatos_respaldo_2025_2':hm,'metadatos_promedios':extra_meta,'cierres_parciales':closures,'MU2026_separado':mu26summary,'denominadores_actuales_intactos':[558,1150,222,124],'calculo_retencion_modificado':False,'Excel_modificado':False,'datos_individuales_guardados':False,'sin_interpretacion_desercion':True,'pendientes_E':['Acreditar completitud y fecha de estado de los listados de cierre T2/T3','Validar el tipo/documento definitivo sin convertir el puente observado en una regla normativa','Los documentos no localizados en una fuente no se interpretan como deserción'],'git':{'rama':subprocess.check_output(['git','-C',str(R),'branch','--show-current'],text=True).strip(),'HEAD':subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(),'commit':False,'push':False}}
result['estados_y_anios_UMAS']={sid:{'estados_observados':v['estados_UMAS_por_persona'],'anios_matricula_observados':v['anios_matricula_por_persona']}for sid,v in observations.items()}
assert sum(r['personas']for r in result['programas'])==20
assert result['puente_documental']['N_DOC_objetivo_con_RUT_explicito_unico']==20
for src in sources:assert digest(Path(src['ruta']))==src['sha256']
OUT.mkdir()
(OUT/'RESULTADOS_AGREGADOS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k not in ['fuentes','programas']},ensure_ascii=False,indent=2))
print('OUT',OUT)
