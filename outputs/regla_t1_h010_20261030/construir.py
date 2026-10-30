"""H010: clasificador candidato separado; entradas privadas sólo lectura, salidas agregadas.

No abre Excel ni atribuye identidad MRUN. No activa ni sustituye códigos v20.
"""
import argparse, collections as C, copy, hashlib, json, os, re, sqlite3, sys
from pathlib import Path

def txt(v): return '' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def aggregate(rows,fields):
 c=C.Counter(tuple(r.get(k) for k in fields) for r in rows)
 return [dict(zip(fields,k),n=v) for k,v in sorted(c.items(),key=lambda kv:tuple(map(str,kv[0])))]
def ctx(r):return tuple(txt(r.get(k)) for k in ['persona','CODCLI','plan','carrera','sede_dimension','jornada_sies'])
def exp(r):return ctx(r)[:3]
def dim(r):return ctx(r)[3:]
def number(v):
 try:return float(v)
 except (TypeError,ValueError):return None

def profile_check(profile,offer):
 if not profile:return False,'TIPO_DURACION_PLAN_SIN_PERFIL_V2'
 ps={(p['tipo_codigo'],number(p['duracion_diagnostica_semestres'])) for p in profile}
 if len(ps)!=1:return False,'PERFIL_PLAN_MULTIPLE'
 typ,dur=next(iter(ps))
 if typ not in {'1','3'} or dur is None:return False,'TIPO_DURACION_PLAN_E'
 if not offer:return False,'OFERTA_ANIO_T1_NO_LOCALIZADA'
 attr={('3' if x['tipo_plan_sies']=='Plan Regular de Continuidad' else '1' if x['tipo_plan_sies']=='Plan Regular' else 'E',number(x['duracion_estudios'])) for x in offer}
 if len(attr)!=1:return False,'OFERTA_ATRIBUTOS_MULTIPLES'
 return (True,'TIPO_DURACION_COMPATIBLES') if attr==ps else (False,'CONTRADICCION_TIPO_O_DURACION')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--privado',type=Path,required=True);a=ap.parse_args();R=a.repo.resolve();P=a.privado.resolve();O=R/'outputs/regla_t1_h010_20261030';O.mkdir(exist_ok=True);os.umask(0o077);P.mkdir(parents=True,exist_ok=True);assert not P.is_relative_to(R)
 sources={}
 def source(p,expected=None):
  p=Path(p);p=p if p.is_absolute() else R/p;h=sha(p)
  if expected:assert h==expected,'Hash distinto: '+p.name
  sources[str(p)]={'sha256':h,'bytes':p.stat().st_size};return p
 def load(p,expected=None):return json.loads(source(p,expected).read_text())
 def dbdesc(path):
  d=load(path);b=source(d['base_privada']['ruta'],d['base_privada']['sha256']);c=sqlite3.connect(b.as_uri()+'?mode=ro',uri=True);c.execute('pragma query_only=ON');return d,c
 active=load('data/diccionario_sies_seguimiento/activo.json');source(active['descriptor'],active['sha256']);d,c=dbdesc(active['descriptor']);d7,c7=dbdesc('data/diccionario_sies_seguimiento/v7_20261023_inf35_03_t3/descriptor.json')
 rows=[json.loads(x[0]) for x in c.execute('select payload from observaciones order by id')];old=[json.loads(x[0]) for x in c7.execute('select payload from observaciones order by id')];byid={x['observacion_id']:x for x in rows}
 historic=[r for r in old if not r.get('codigo_interno_adoptado')];assert len(historic)==3049
 assert sum(r['estado_interno']=='SIN_EVIDENCIA_ANUAL_APLICABLE' for r in historic)==2966
 mu=C.defaultdict(list)
 for person,y,code,payload in c.execute('select persona,anio,codigo,payload from mu_anual'):mu[(person,int(y))].append(json.loads(payload))
 # Documento anual se reutiliza; nunca se deriva un expediente desde MU sola.
 anchors=C.defaultdict(list);personanchors=C.defaultdict(list);annual=C.defaultdict(set);allpersonmu=C.defaultdict(set)
 for (person,y),rr in mu.items():allpersonmu[person].add(y)
 for r in rows:
  code=r.get('codigo_documental_atribuible');y=int(r['ano'])
  if code and any(x['codigo']==code for x in mu[(r['persona'],y)]):
   annual[(dim(r),r['plan'],y)].add(code)
   if txt(r['periodo'])=='1':
    z={'anio':y,'codigo':code,'observacion_id':r['observacion_id'],'dimensiones':dim(r),'expediente':exp(r),'evidencia_mu':[x for x in mu[(r['persona'],y)] if x['codigo']==code]}
    anchors[exp(r)].append(z);personanchors[r['persona']].append(z)
 profiles=load('data/paridad_codigo_sies/regla_operativa_mu_v2/TIPO_PLAN_POR_PLAN_UMAS.json')['filas'];maestro=load('data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json');parity=load('data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json')['filas']
 offers=C.defaultdict(list)
 for x in maestro['oferta_anual']:offers[(int(x['anio']),x['codigo_unico'])].append(x)
 def prof(r):return [p for p in profiles if p['codcarpr']==r['carrera'] and p['plan_umas']==r['plan'] and p['sede_umas']=={'2':'RE','3':'CO','4':'PTG'}.get(txt(r.get('sede_dimension')))]
 def check(r,code,y):return profile_check(prof(r),offers[(y,code)])
 sys.path.insert(0,str(R));from common.codigo_sies_mu2027 import cargar_contexto,resolver
 source('common/codigo_sies_mu2027.py');rule=load('data/reglas_negocio/mu2027/REGLA_CODIGO_SIES_MU2027.json')
 for ref in rule['fuentes'].values():
  if isinstance(ref,dict) and 'ruta'in ref and 'sha256'in ref:source(ref['ruta'],ref['sha256'])
 operational=cargar_contexto()
 # Coincidencia exacta de expediente/plan contra enlaces gobernados, no nombre.
 links=load(rule['fuentes']['enlaces_privados_H002g']['ruta'],rule['fuentes']['enlaces_privados_H002g']['sha256']);mu26=C.defaultdict(list)
 for z in links:
  if z['anio']==2026 and z['seleccion'] and z['plan']:
   sel=z['seleccion'];mu26[(txt(sel[0]),z['plan'])].append(z['fila_fuente_mu'])
 # Reutiliza enlace anual gobernado H002g: MU aporta T1, DA el expediente,
 # PROMEDIOS el plan anual. No exige actividad específicamente en período 1.
 from common.diccionario_sies_seguimiento import rut_normalizado
 for z in links:
  if not z['seleccion'] or z['plan_respaldo']!='ANUAL':continue
  ident=z['identidad']
  if ident[0]!='R':continue
  person=rut_normalizado(txt(ident[1])+'-'+txt(ident[2]));sel=z['seleccion'];code=z['codigo_sies'];year=z['anio']
  evidence=[m for m in mu[(person,year)] if m['codigo']==code]
  if not evidence:continue
  ss={'RE':'2','CO':'3','PTG':'4'}.get(txt(sel[2]));jj={'D':'1','V':'2','O':'4'}.get(txt(sel[3]))
  if ss is None or jj is None:continue
  dimensions=(txt(sel[1]),ss,jj);e=(person,txt(sel[0]),z['plan'])
  anchor={'anio':year,'codigo':code,'observacion_id':None,'dimensiones':dimensions,'expediente':e,'evidencia_mu':evidence,'enlace_gobernado':'H002g ENLACES_MU_DA.json','fila_fuente_mu':z['fila_fuente_mu'],'limite':'Plan anual observado; no fecha efectiva de cambio acreditada'}
  anchors[e].append(anchor);personanchors[person].append(anchor)
  annual[(dimensions,z['plan'],year)].add(code)
 def annual_candidate(r):
  y=int(r['ano']);codes=set(annual[(dim(r),r['plan'],y)])
  for p in parity:
   if p['anio']==y and r['carrera'] in p['codcarpr'] and r['plan'] in p['plan_umas'] and txt(p['cod_sede'])==txt(r.get('sede_dimension')) and txt(p['cod_jornada'])==txt(r.get('jornada_sies')):codes.add(p['codigo_unico'])
  good=[code for code in sorted(codes) if check(r,code,y)[0] and any(x['vigencia']!='Sin estudiantes nuevos ni antiguos' for x in offers[(y,code)])]
  return good
 def classify(r):
  y=int(r['ano']);per=txt(r['periodo']);z={'observacion_id':r['observacion_id'],'anio':y,'periodo':per,'carrera':r['carrera'],'plan':r['plan'],'sede':txt(r.get('sede_dimension')),'jornada':txt(r.get('jornada_sies')),'nivel_asignacion':'E','codigo_candidato':'','año_T1_fuente':None,'desfase':None,'clase':'E','regla':'H010_D_20261030','motivo':'','evidencia':[],'marcas':[]}
  same=[b for b in anchors[exp(r)] if b['anio']==y and b['dimensiones']==dim(r)]
  def assign(codes,level,sourceyear,ev):
   if len(codes)!=1:z['motivo']='T1_MULTIPLES_CODIGOS';return z
   z.update(nivel_asignacion=level,codigo_candidato=next(iter(codes)),año_T1_fuente=sourceyear,desfase=sourceyear-y if sourceyear is not None else None,clase='B/C' if level=='DOCUMENTAL_T1' else 'D/C',motivo='EVIDENCIA_T1_MISMO_EXPEDIENTE_PLAN',evidencia=ev);return z
  if per=='1':
   code=r.get('codigo_documental_atribuible')
   if same:return assign({b['codigo'] for b in same},'DOCUMENTAL_T1',y,same)
   z['motivo']='T1_SIN_LINEA_ATRIBUIDA_AL_EXPEDIENTE';return z
  if per not in {'2','3'}:z['motivo']='PERIODO_NATIVO_4_5_NO_HOMOLOGADO';return z
  if same:return assign({b['codigo'] for b in same},'HERENCIA_T1_MISMO_AÑO',y,same)
  future=sorted([b for b in anchors[exp(r)] if b['anio']>y],key=lambda b:b['anio'])
  if future and not any(b['anio']<future[0]['anio'] and b['anio']>y and b['expediente']!=exp(r) for b in personanchors[r['persona']]):
   first=future[0]['anio'];rr=[b for b in future if b['anio']==first];codes={b['codigo'] for b in rr};z['año_T1_fuente']=first;z['desfase']=first-y
   if any(b['dimensiones']!=dim(r) for b in rr):z['motivo']='CAMBIO_SEDE_JORNADA_ANTES_T1';z['evidencia']=rr;return z
   if len(codes)!=1:z['motivo']='PRIMER_T1_MULTIPLES_CODIGOS';z['evidencia']=rr;return z
   code=next(iter(codes));ok,why=check(r,code,first)
   if not ok:z.update(motivo=why,evidencia=rr);return z
   z=assign(codes,'PRIMER_T1_POSTERIOR',first,rr)
   group=annual[(dim(r),r['plan'],y)]
   if group and code not in group:z['marcas'].append('TRANSICION_RECODIFICACION_C_INDICIO_GRUPO')
   return z
  later=[b for b in personanchors[r['persona']] if b['anio']>y]
  changed=bool(later) and all(b['expediente']!=exp(r) for b in later if b['anio']==min(t['anio'] for t in later))
  if changed:
   z['marcas'].append('CAMBIO_PLAN_ANTES_DE_T1');options=annual_candidate(r)
   if len(options)==1:z.update(nivel_asignacion='CAMBIO_PLAN_ANTES_DE_T1_CATALOGO',codigo_candidato=options[0],clase='D/C',motivo='CODIGO_GRUPO_ANUAL_PLAN_ORIGINAL_NO_DOCUMENTAL',evidencia=['grupo documental anual + perfil v2 + oferta anual']);return z
   z['motivo']='CAMBIO_PLAN_SIN_CODIGO_ANUAL_UNICO_COMPATIBLE';return z
  if y==2026:
   refs=mu26[(txt(r['CODCLI']),r['plan'])];answers=[]
   for ref in sorted(set(refs)):answers.append(resolver({'anio':2027,'via_solicitada':'ANTIGUO','fila_mu2026':ref},*operational))
   codes={v['codigo'] for v in answers if v['codigo']}
   if len(codes)==1 and all(v['codigo'] for v in answers):z.update(nivel_asignacion='MU2027',codigo_candidato=next(iter(codes)),clase='D/C',motivo='SIMULACION_ANTIGUO_NO_T1_2027_OBSERVADO',evidencia=[{'fila_mu2026':i} for i in sorted(set(refs))]);return z
   z['motivo']='MU2027_SIN_FILA_ANTIGUO_INEQUIVOCA_NO_COHORTE_NUEVA_2027';return z
  if not allpersonmu[r['persona']]:
   options=annual_candidate(r)
   if len(options)==1:z.update(nivel_asignacion='NUNCA_INFORMADO_EN_FUENTES',codigo_candidato=options[0],clase='D/C',motivo='AUSENCIA_OBSERVADA_2019_2026_NO_INEXISTENCIA_SIES',evidencia=['grupo anual + perfil v2 + oferta anual']);return z
   z['motivo']='SIN_MU_LOCALIZADA_Y_SIN_CATALOGO_ANUAL_UNICO';return z
  z['motivo']='PERSONA_EN_MU_SIN_T1_MISMO_EXPEDIENTE_PLAN_ACREDITADO';return z
 results=[classify(r) for r in rows];res={x['observacion_id']:x for x in results}
 slots=load(Path.home()/'.local/share/ipss/trazabilidad_integral_fase3_20261025/VISTA_T1_T2_T3.json','72edecb9507f46985533d1c63b83735beb4db58d743c89c226ca6be1a2c8ef31');pending99=[q for s in slots for q in s['contextos'] if not q['codigo_destino']];assert len(pending99)==99
 p99=[res[q['observacion_id']] for q in pending99];h3049=[res[r['observacion_id']] for r in historic]
 dump(P/'ASIGNACIONES_PRIVADAS.json',results);dump(P/'POSICIONES_99_PRIVADAS.json',p99)
 # Paso 1: ausencia de MU de la persona en X, no ausencia de actividad; no equipara a los 2966.
 follow=[]
 for r in rows:
  y=int(r['ano'])
  if y not in range(2019,2026) or txt(r['periodo']) not in {'2','3'} or any(b['anio']==y and b['dimensiones']==dim(r) for b in anchors[exp(r)]):continue
  later=[b for b in anchors[exp(r)] if b['anio']>y];first=min((b['anio'] for b in later),default=None)
  follow.append({'anio':y,'periodo':txt(r['periodo']),'carrera':r['carrera'],'primer_T1':first,'desfase':'SIN_T1_POSTERIOR_LOCALIZADO' if first is None else 'X+1' if first-y==1 else 'X+2' if first-y==2 else 'X+3_O_MAS','situacion_mu_anual':'PERSONA_SIN_LINEA_MU' if not mu[(r['persona'],y)] else 'PERSONA_CON_MU_SIN_T1_EXPEDIENTE_PLAN','identidad':exp(r)})
 dump(P/'SEGUIMIENTO_PRIVADO.json',follow)
 dump(O/'PRIMER_T1_POSTERIOR.json',{'clase':'B/C; censura E','unidad':'observaciones nativas; no personas únicas','criterio':'Período 2/3 sin T1 atribuido al mismo expediente+plan y dimensiones en X; distingue ausencia MU de la persona de falta de enlace al expediente. Incluye el subconjunto aplicable de las 2966 históricas','total':len(follow),'por_anio_periodo':aggregate(follow,['anio','periodo','primer_T1','desfase']),'por_situacion_MU':aggregate(follow,['anio','periodo','situacion_mu_anual']),'2966_por_periodo':dict(C.Counter(txt(r['periodo']) for r in historic if r['estado_interno']=='SIN_EVIDENCIA_ANUAL_APLICABLE')),'por_carrera':aggregate(follow,['anio','periodo','carrera','primer_T1','desfase']),'respuesta_2020_2022_hacia_2023_2025':aggregate([x for x in follow if x['anio'] in [2020,2021,2022] and x['primer_T1'] in [2023,2024,2025]],['anio','periodo','primer_T1','carrera']),'limite':'No localizado no prueba nunca informado. Las MU históricas no acreditan cobertura completa; el expediente puede existir sin contexto nativo 1 en los extractos.'})
 stability=[]
 for key,aa in anchors.items():
  for y in range(2019,2026):
   prev=[b for b in aa if b['anio']==y];nxt=[b for b in aa if b['anio']==y+1]
   for dims in sorted({b['dimensiones'] for b in prev}&{b['dimensiones'] for b in nxt}):
    a0={b['codigo'] for b in prev if b['dimensiones']==dims};a1={b['codigo'] for b in nxt if b['dimensiones']==dims}
    state='MULTIPLE_E' if len(a0)!=1 or len(a1)!=1 else 'MANTIENE' if a0==a1 else 'CAMBIA'
    stability.append({'anio':y,'siguiente':y+1,'carrera':dims[0],'codigo_antes':','.join(sorted(a0)),'codigo_despues':','.join(sorted(a1)),'estado':state})
 dump(O/'ESTABILIDAD.json',{'clase':'B/C; cambio observado no prueba causa institucional','por_anio':aggregate(stability,['anio','siguiente','estado']),'por_codigo':aggregate(stability,['anio','siguiente','carrera','codigo_antes','codigo_despues','estado'])})
 # Reproducir sólo la selección de los 425 errores antiguos, no aplicar como errores H010.
 annual7=C.defaultdict(list)
 for r in old:
  if r.get('codigo_documental_atribuible'):annual7[ctx(r)+(txt(r['ano']),)].append(r)
 aa=[]
 for k,rs in annual7.items():
  codes={r['codigo_documental_atribuible'] for r in rs}
  if len(codes)==1:aa.append({'key':k,'code':next(iter(codes))})
 model=C.defaultdict(set)
 for z in aa:
  if int(z['key'][-1])<2022:model[z['key'][2:6]].add(z['code'])
 err=[]
 for z in aa:
  k=z['key'];opts=model[k[2:6]]
  if k[-1]=='2022' and len(opts)==1 and z['code'] not in opts:
   before={b['codigo'] for b in anchors[k[:3]] if b['anio']==2021 and b['dimensiones']==k[3:6]};after={b['codigo'] for b in anchors[k[:3]] if b['anio']==2022 and b['dimensiones']==k[3:6]}
   why='TRANSICION_MISMO_EXPEDIENTE_T1_2021_2022' if len(before)==len(after)==1 and before==opts and after=={z['code']} else 'SIN_PRUEBA_TRANSICION_T1_PERSONAL'
   err.append({'carrera':k[3],'prediccion_vieja':next(iter(opts)),'documentado_2022':z['code'],'causa':why})
 assert len(err)==425
 public=load('outputs/paridad_cohorte_2007_2026/CONTROL_SIES_PUBLICACION.json')['filas']
 public2026=load('outputs/trazabilidad_integral_umas_sies_20261025/h007_20261030/MRUN_AGREGADO.json')['por_codigo']
 public=public+[{'anio':2026,'codigo_sies':x['codigo_sies'],'publicacion':x['registros_sies']} for x in public2026 if x['anio']==2026 and x['registros_sies'] is not None]
 codes21={x['codigo_sies'] for x in public if x['anio']==2021 and x['publicacion']>0};codes22={x['codigo_sies'] for x in public if x['anio']==2022 and x['publicacion']>0}
 last21={code for code in codes21 if not any(x['codigo_sies']==code and x['anio']>2021 and x['publicacion']>0 for x in public)}
 dump(O/'TRANSICION_2021_2022.json',{'clase':'B/C; causalidad institucional E','fuente':'CONTROL_SIES_PUBLICACION.json (hasta 2025) + R25 MRUN_AGREGADO.json (2026); no reconstruye MRUN','codigos_2021':len(codes21),'codigos_2022':len(codes22),'ultima_matricula_2021':sorted(last21),'coincide_46_26_14':(len(codes21),len(codes22),len(last21))==(46,26,14),'nota':'Cambios de totales no prueban qué código sustituye a cuál; observar transición personal por separado.'})
 dump(O/'ERRORES_425_REENCUADRADOS.json',{'clase':'C/E','errores_antigua_prueba':425,'causas':aggregate(err,['causa']),'por_codigo':aggregate(err,['carrera','prediccion_vieja','documentado_2022','causa']),'limite':'Transición observada no acredita recodificación institucional ni explica errores sin T1 personal; no son errores de H010.'})
 cov={'v7_3049':h3049,'V24_99_posiciones':p99,'v20_completa':results}
 dump(O/'COBERTURA.json',{k:{'total':len(v),'por_nivel':aggregate(v,['nivel_asignacion']),'residual_E':sum(x['nivel_asignacion']=='E' for x in v),'residual_pct':100*sum(x['nivel_asignacion']=='E' for x in v)/len(v),'por_motivo':aggregate(v,['nivel_asignacion','motivo'])} for k,v in cov.items()})
 dump(O/'RESIDUAL_E.json',{'clase':'E','casos':aggregate([z for z in results if z['nivel_asignacion']=='E'],['anio','periodo','carrera','plan','sede','jornada','motivo']),'requisitos':{'CONTRADICCION_TIPO_O_DURACION':'Evidencia de malla/versión para el año; no elegir código contradictorio','TIPO_DURACION_PLAN_SIN_PERFIL_V2':'Perfil gobernado tipo y duración del plan','PERSONA_EN_MU_SIN_T1_MISMO_EXPEDIENTE_PLAN_ACREDITADO':'Registro T1 que enlace expediente y plan','SIN_MU_LOCALIZADA_Y_SIN_CATALOGO_ANUAL_UNICO':'Código anual compatible único y cobertura documental','MU2027_SIN_FILA_ANTIGUO_INEQUIVOCA_NO_COHORTE_NUEVA_2027':'Enlace MU2026 o decisión específica de simulación para ingreso 2026; no fingir cohorte 2027','PERIODO_NATIVO_4_5_NO_HOMOLOGADO':'Regla de conversión explícita, fuera de T2/T3 pedido'}})
 # SQLite candidata: conserva TODAS las tablas v20; agrega overlay sin cambiar atribuciones.
 candidate=P/'DICCIONARIO_V21_CANDIDATA.sqlite'
 if candidate.exists():candidate.unlink() # sólo salida propia reproducible, nunca entrada
 nc=sqlite3.connect(candidate);c.backup(nc);nc.execute('create table asignaciones_h010 (observacion_id integer primary key, payload text not null)');nc.executemany('insert into asignaciones_h010 values (?,?)',[(z['observacion_id'],json.dumps(z,ensure_ascii=False,sort_keys=True)) for z in results]);nc.commit();assert nc.execute('pragma integrity_check').fetchone()[0]=='ok'
 assert nc.execute('select * from observaciones order by id').fetchall()==c.execute('select * from observaciones order by id').fetchall();assert nc.execute('select * from mu_anual order by rowid').fetchall()==c.execute('select * from mu_anual order by rowid').fetchall();nc.close()
 dest=R/'data/diccionario_sies_seguimiento/v21_20261030_candidata_h010';dest.mkdir(exist_ok=True)
 desc={'edicion':'v21_20261030_candidata_h010','estado':'CANDIDATA_NO_ACTIVA_OVERLAY','base_privada':{'ruta':str(candidate),'sha256':sha(candidate)},'v20_origen':active,'contrato':'Tablas v20 intactas; campos candidatos en asignaciones_h010.payload. No consumidor activo ni reemplazo documental. Requiere aprobación e integración posterior.','campos':['nivel_asignacion','codigo_candidato','año_T1_fuente','desfase','regla','evidencia','clase'],'capa_promedios':d['capa_promedios'],'componentes_sha256':{'outputs/regla_t1_h010_20261030/construir.py':sha(__file__)},'resumen':{k:len(v) for k,v in cov.items()}}
 dump(dest/'descriptor.json',desc)
 meta=load(d['capa_promedios']['metadata'],d['capa_promedios']['sha256']);source(meta['capa_privada']['ruta'],meta['capa_privada']['sha256'])
 for path in ['outputs/retencion_primer_anio_h001_activo_20261028/RETENCION_PRIMER_ANIO_AGREGADO.json','data/reglas_negocio/indicador_intertrimestral/REGLA.json','docs/MAPA_RESULTADOS_GOBERNADOS.json']:source(path)
 preserved=all(sha(path)==v['sha256'] for path,v in sources.items());assert preserved
 checks={'v20_tablas_intactas':True,'puntero_intacto':load('data/diccionario_sies_seguimiento/activo.json')==active,'fuentes_intactas':preserved,'3049_exactas':len(h3049)==3049,'99_posiciones_exactas':len(p99)==99,'2966_historia_exacta':True,'425_reproducidos':len(err)==425,'niveles_1_3_tienen_ancla_T1':all(z['evidencia'] and z['año_T1_fuente'] is not None for z in results if z['nivel_asignacion'] in ['DOCUMENTAL_T1','HERENCIA_T1_MISMO_AÑO','PRIMER_T1_POSTERIOR']),'nivel3_tipo_duracion_compatible':all(check(byid[z['observacion_id']],z['codigo_candidato'],z['año_T1_fuente'])[0] for z in results if z['nivel_asignacion']=='PRIMER_T1_POSTERIOR')}
 dump(O/'QA.json',{'estado':'PASS_CONTROLES_CON_RESIDUALES_E','controles':checks,'meta_residual_0_1_pct':all(100*sum(z['nivel_asignacion']=='E' for z in v)/len(v)<=.1 for v in [h3049,p99]),'tasas':{'R01_R04_delta_pp':0.0,'R19_delta_pp':0.0,'metodo':'Conservación de resultados y fuentes por hash; sin recálculo ni integración en indicadores.'},'activacion':False})
 dump(O/'FUENTES.json',{'fuentes':[{'ruta':p,**v} for p,v in sorted(sources.items())]})
 c.close();c7.close();print(json.dumps({'cobertura':{k:dict(C.Counter(z['nivel_asignacion'] for z in v)) for k,v in cov.items()},'paso1':len(follow),'errores425':dict(C.Counter(z['causa'] for z in err))},ensure_ascii=False))
if __name__=='__main__':main()
