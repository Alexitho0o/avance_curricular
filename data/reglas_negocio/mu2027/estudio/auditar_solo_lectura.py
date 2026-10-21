from pathlib import Path
import csv,json,hashlib,zipfile,io,collections,importlib.util
import openpyxl
R=Path('/Users/alexi/Documents/GitHub/avance_curricular'); O=Path(__file__).parent;result={};sources=[]
def s(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
def key(r):return (s(r['TIPO_DOC']),s(r['N_DOC']),s(r['DV']).upper())
def uk(r):
 v=s(r['RUT']).replace('.','').replace(' ','').upper(); n,d=v.rsplit('-',1);return ('R',str(int(n)),d)
def meta(p,expected=None):
 h=hashlib.sha256(p.read_bytes()).hexdigest();sources.append({'path':str(p),'sha256':h,'expected':expected,'hash_ok':h==expected if expected else None});return h
def rows(p,sheet):
 w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=w[sheet].values;hdr=[s(x) for x in next(it)];rr=[dict(zip(hdr,r)) for r in it if any(x is not None for x in r)];w.close();return rr
def cnt(rr,c):return dict(collections.Counter(s(x[c]) for x in rr))
def summary(rr):return {'registros':len(rr),'personas':len({key(x) for x in rr}),'VIG':cnt(rr,'VIG')}
m=list(csv.DictReader((R/'requerimiento_bettersoft_uplus_2026/01_fuentes_oficiales/MANIFIESTO_FUENTES_GATE09.tsv').open(),delimiter='\t'))
cols='TIPO_DOC N_DOC DV PRIMER_APELLIDO SEGUNDO_APELLIDO NOMBRE SEXO FECH_NAC NAC PAIS_EST_SEC COD_SED COD_CAR MODALIDAD JOR VERSION FOR_ING_ACT ANIO_ING_ACT SEM_ING_ACT ANIO_ING_ORI SEM_ING_ORI ASI_INS_ANT ASI_APR_ANT PROM_PRI_SEM PROM_SEG_SEM ASI_INS_HIS ASI_APR_HIS NIV_ACA SIT_FON_SOL SUS_PRE FECHA_MATRICULA REINCORPORACION VIG'.split()
pes=[];result['envios']={}
for v in m:
 if v['proceso']=='matricula_unificada_2026' and '_orig.zip' in v['archivo']:
  p=R/v['ruta_destino'];meta(p,v['sha256_destino'])
  with zipfile.ZipFile(p) as z:
   data=z.read(z.namelist()[0]);text=data.decode('utf-8-sig')
  rr=[dict(zip(cols,r)) for r in csv.reader(io.StringIO(text),delimiter=';') if len(r)==32];pes+=rr;result['envios'][p.name]=summary(rr)
v=next(x for x in m if '7804' in x['archivo']);p=Path(v['ruta_origen']);meta(p,v['sha256_origen']);u=rows(p,'DatosAlumnos');ui=collections.defaultdict(list)
for r in u:ui[uk(r)].append(r)
basepath=R/'outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx';meta(basepath,'19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd');base=rows(basepath,'BASE_RETENCION_MU');b26=[r for r in base if s(r['ANIO_INFORMADO'])=='2026'];result['base_por_anio']={str(y):summary([r for r in base if s(r['ANIO_INFORMADO'])==str(y)]) for y in range(2022,2027)}
pi=collections.defaultdict(list);bi=collections.defaultdict(list)
for r in pes:pi[key(r)].append(r)
for r in b26:bi[key(r)].append(r)
titkeys={k for k,rs in ui.items() if any(s(r['ESTADOACADEMICO'])=='TITULADO' for r in rs)}
solotit={k for k,rs in ui.items() if {s(r['ESTADOACADEMICO']) for r in rs}=={'TITULADO'}}
result['titulados']={'filas_snapshot':sum(s(r['ESTADOACADEMICO'])=='TITULADO' for r in u),'personas_snapshot':len(titkeys),'pes_con_historial_titulado':summary([r for r in pes if key(r) in titkeys]),'pes_solo_titulado':summary([r for r in pes if key(r) in solotit]),'base2026_con_historial_titulado':summary([r for r in b26 if key(r) in titkeys]),'base2026_solo_titulado':summary([r for r in b26 if key(r) in solotit])}
# Exact person plus single 2026 UMAS row: no career or period inference.
match=[];amb=0;missing=0
for r in pes:
 ur=[x for x in ui.get(key(r),[]) if s(x['ANOMATRICULA'])=='2026']
 if len(ur)==1:match.append((r,ur[0]))
 elif ur:amb+=1
 else:missing+=1
result['match_persona_unica_UMAS2026']={'filas_match':len(match),'ambiguas':amb,'sin_fila_umas2026':missing,'estado_vig':[{'estado':a,'VIG':b,'filas':n} for (a,b),n in sorted(collections.Counter((s(u['ESTADOACADEMICO']),s(p['VIG'])) for p,u in match).items())]}
# Compare annual record keys including original cohort; no alteration.
fields=['TIPO_DOC','N_DOC','DV','COD_SED','COD_CAR','MODALIDAD','JOR','VERSION','ANIO_ING_ACT','SEM_ING_ACT','ANIO_ING_ORI','SEM_ING_ORI']
def rk(r):return tuple(s(r[c]) for c in fields)
pmap=collections.defaultdict(list);bmap=collections.defaultdict(list)
for r in pes:pmap[rk(r)].append(r)
for r in b26:bmap[rk(r)].append(r)
common=pmap.keys()&bmap.keys();un=[k for k in common if len(pmap[k])==len(bmap[k])==1];dif=[k for k in un if s(pmap[k][0]['VIG'])!=s(bmap[k][0]['VIG'])]
result['comparacion_pes_base']={'llave':fields,'coincidencias_univocas':len(un),'claves_comunes_no_univocas':len(common)-len(un),'vig_diferente':len(dif),'solo_pes_registros':sum(len(pmap[k]) for k in pmap.keys()-bmap.keys()),'solo_base_registros':sum(len(bmap[k]) for k in bmap.keys()-pmap.keys()),'solo_pes_personas':len(pi.keys()-bi.keys()),'solo_base_personas':len(bi.keys()-pi.keys()),'personas_vig_positivo_diferente':sum(any(s(r['VIG']) in ('1','2') for r in pi.get(k,[]))!=any(s(r['VIG']) in ('1','2') for r in bi.get(k,[])) for k in pi.keys()|bi.keys())}
# Approved T2/T3 cohorts, unchanged denominators, compare sources diagnostically.
prev=json.loads((R/'outputs/retencion_intermedia_t2_t3/20261020_221157/MANIFEST_CONTINUIDAD.json').read_text());result['T2_T3']={}
for t in (2,3):
 v=next(x for x in prev['fuentes'] if x['id']==f'T{t}');p=Path(v['path']);meta(p,v['sha256']);rr=rows(p,v['sheet']);ks={uk(r) for r in rr if s(r['ANOINGRESO'])=='2025' and s(r['PERIODOINGRESO'])==str(t)}
 def counts(index):return {'encontrados':sum(k in index for k in ks),'vig1':sum(any(s(r['VIG'])=='1' for r in index.get(k,[])) for k in ks),'solo_vig0':sum(k in index and all(s(r['VIG'])=='0' for r in index[k]) for k in ks),'ausentes':sum(k not in index for k in ks)}
 result['T2_T3'][str(t)]={'denominador':len(ks),'base':counts(bi),'pes':counts(pi),'con_historial_titulado_snapshot_mayo':len(ks&titkeys),'solo_vig0_base_con_historial_titulado':sum(k in titkeys and k in bi and all(s(r['VIG'])=='0' for r in bi[k]) for k in ks),'solo_vig0_base_estados_2026_snapshot':dict(collections.Counter(' / '.join(sorted({s(r['ESTADOACADEMICO']) for r in ui.get(k,[]) if s(r['ANOMATRICULA'])=='2026'})) or 'SIN FILA UMAS2026' for k in ks if k in bi and all(s(r['VIG'])=='0' for r in bi[k])))}
result['fuentes']=sources
(O/'resultado.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='fuentes'},ensure_ascii=False,indent=2))
# Read-only verification of original VIG versus consolidated VIG, using existing normalizer only.
sp=importlib.util.spec_from_file_location('constructor_readonly',R/'scripts/construir_base_retencion_mu_2022_2026.py');mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
inv=json.loads((basepath.parent/'INVENTARIO_FUENTES_SHA256.json').read_text());result['fuentes_anuales_vig']={}
for y,spec in mod.SELECTED_SOURCES.items():
 p=spec['path'];exp=next(x['sha256'] for x in inv if x['anio']==y);meta(p,exp)
 if spec['kind']=='csv_with_header':hdr,rr,notes=mod.read_csv(p)
 else:hdr,rr,notes=mod.read_xlsx_sheet(p,spec['sheet'])
 hmap={mod.normalize_header(h):i for i,h in enumerate(hdr)};ci=hmap.get('VIG',hmap.get('VIGENCIA'));original=[mod.typed_value('VIG',r[ci]) for r in rr if any(r) and not mod.has_header_like(r,cols)]
 bb=[r for r in base if s(r['ANIO_INFORMADO'])==str(y)]
 result['fuentes_anuales_vig'][str(y)]={'filas_origen':len(original),'filas_base':len(bb),'vig_identico_fila_a_fila':original==[r['VIG'] for r in bb],'cambios_vig':sum(a!=r['VIG'] for a,r in zip(original,bb)),'columna_origen':hdr[ci]}
# Same calculation as frozen formulas, in memory only. The workbook has no cached results.
diag=R/'outputs/retencion_primer_anio_ipss_162/20260930_000000/RETENCION_PRIMER_ANIO_IPSS_162_DIAGNOSTICO_BRECHAS_20260930.xlsx';meta(diag)
db=rows(diag,'BASE_RETENCION_MU');cat=rows(diag,'01_CATALOGO_CARRERA');result['raw_diagnostico_igual_base']=db==base
ci=collections.defaultdict(list)
for r in cat:ci[s(r['ANO'])+'|'+s(r['CODIGO_UNICO'])].append(r)
bidx=collections.defaultdict(list)
for r in db:bidx[(s(r['ANIO_INFORMADO']),key(r))].append(r)
def pos(r):return float(s(r['VIG']) or -1)>=1
def cohort(r):return (s(r['ANIO_ING_ORI']),s(r['SEM_ING_ORI']))
def same(rs,r):return [x for x in rs if cohort(x)==cohort(r)]
elig=collections.defaultdict(list);result['anual_control']={};result['anual_con_titulo_snapshot_mayo']={}
for r in db:
 y=int(r['ANIO_INFORMADO']);co=cohort(r)
 if y not in range(2022,2026) or co[0]!=str(y) or co[1] not in ('1','2') or s(r['VIG'])=='0':continue
 cu=f'I162S{s(r["COD_SED"])}C{s(r["COD_CAR"])}J{s(r["JOR"])}V{s(r["VERSION"])}';cc=ci['OFE_'+str(y)+'|'+cu]
 if len(cc)!=1:continue
 c=cc[0];minimum={'Técnico de Nivel Superior':4,'Profesional Sin Licenciatura':6,'Profesional Con Licenciatura':8,'Licenciatura no conducente a título':8}.get(s(c['NIVEL_CARRERA']))
 if s(c['NIVEL_GLOBAL'])!='Pregrado' or s(c['TIPO_CARRERA'])!='Plan Regular' or s(c['PLAN_ESPECIAL'])!='NO APLICA' or minimum is None or float(c['DURACION_ESTUDIOS'])<minimum:continue
 active=[x for x in bidx[(str(y),key(r))] if pos(x) and cohort(x)==co]
 nxt=[x for x in bidx[(str(y+1),key(r))] if pos(x)];ns=same(nxt,r)
 if len(active)>1 or len(nxt)>len(ns):continue
 elig[y].append((r,bool(ns)))
for y,rs in elig.items():
 result['anual_control'][str(y)]={'denominador':len(rs),'retenidos':sum(t for r,t in rs),'tasa':sum(t for r,t in rs)/len(rs)}
 tagged=[(r,t) for r,t in rs if key(r) in titkeys]
 result['anual_con_titulo_snapshot_mayo'][str(y)]={'personas_con_historial_titulo_mayo2026':len({key(r) for r,t in tagged}),'retenidos':sum(t for r,t in tagged),'no_retenidos':sum(not t for r,t in tagged),'nota':'Estado en mayo2026 no acredita estado histórico al corte; NO errores confirmados.'}
expected={2022:(305,224),2023:(366,258),2024:(558,326),2025:(1150,668)}
result['qa_anual']=all((len(elig[y]),sum(t for r,t in elig[y]))==v for y,v in expected.items())
changedkeys={k for k in pi.keys()|bi.keys() if any(pos(r) for r in pi.get(k,[]))!=any(pos(r) for r in bi.get(k,[]))}
y25=elig[2025];result['sensibilidad_pes_sin_modificar_denominador']={'denominador_fijo':len(y25),'retenidos_base':sum(t for r,t in y25),'retenidos_en_pes_misma_cohorte':sum(bool(same([x for x in pi.get(key(r),[]) if pos(x)],r)) for r,t in y25),'cambio_individual_marca_retenido':sum(bool(same([x for x in pi.get(key(r),[]) if pos(x)],r))!=t for r,t in y25),'cinco_personas_cambio_vig_en_cohorte2025':sum(key(r) in changedkeys for r,t in y25),'nota':'Comparación diagnóstica a denominador fijo; no sustituye base ni resultados oficiales.'}
result['cinco_personas_distribucion']={'base_vig1':sum(any(pos(r) for r in bi[k]) for k in changedkeys),'pes_vig1':sum(any(pos(r) for r in pi[k]) for k in changedkeys),'cohortes_origen_base':dict(collections.Counter('|'.join(cohort(r)) for k in changedkeys for r in bi[k])),'con_historial_titulado':len(changedkeys & titkeys)}
result['fuentes']=sources
(O/'resultado.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in result.items() if k in ['fuentes_anuales_vig','raw_diagnostico_igual_base','anual_control','qa_anual','sensibilidad_pes_sin_modificar_denominador','cinco_personas_distribucion','anual_con_titulo_snapshot_mayo']},ensure_ascii=False,indent=2))
zkeys={key(r) for r in pes if s(r['VIG'])=='0' and key(r) in titkeys}
result['cinco_vig0_con_historial_titulado']={'personas':len(zkeys),'estado_2026_snapshot_por_persona':dict(collections.Counter(' / '.join(sorted({s(r['ESTADOACADEMICO']) for r in ui[k] if s(r['ANOMATRICULA'])=='2026'})) or 'SIN FILA UMAS2026' for k in zkeys)),'cohorte_origen_en_pes':dict(collections.Counter('|'.join(cohort(r)) for r in pes if key(r) in zkeys)),'incluidos_retencion_anual_2025':sum(key(r) in zkeys for r,t in elig[2025]),'titulados_sin_otro_estado':len(zkeys&solotit)}
# Group cross-table reports unique people as well as rows.
result['match_persona_unica_UMAS2026']['personas']=len({key(p) for p,u in match})
for a in result['match_persona_unica_UMAS2026']['estado_vig']:
 a['personas']=len({key(p) for p,u in match if s(u['ESTADOACADEMICO'])==a['estado'] and s(p['VIG'])==a['VIG']})
result['fuentes']=sources
assert all(x['hash_ok'] is not False for x in sources)
assert result['qa_anual'] and result['raw_diagnostico_igual_base']
(O/'resultado.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result['cinco_vig0_con_historial_titulado'],ensure_ascii=False,indent=2))
discord={key(p) for p,u in match if s(u['ESTADOACADEMICO'])=='VIGENTE' and s(p['VIG'])=='0'}
result['vigente_umas_con_vig0_pes']={'personas':len(discord),'periodomatricula_snapshot':dict(collections.Counter(s(u['PERIODOMATRICULA']) for p,u in match if key(p) in discord)),'situacion_snapshot':dict(collections.Counter(s(u['SITUACION']) for p,u in match if key(p) in discord)),'incluidos_retencion2025':sum(key(r) in discord for r,t in elig[2025]),'no_retenidos_retencion2025':sum(key(r) in discord and not t for r,t in elig[2025]),'nota':'Discrepancia de etiquetas entre fuentes; no prueba error de VIG al 30 de abril.'}
result['fuentes']=sources
(O/'resultado.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result['vigente_umas_con_vig0_pes'],ensure_ascii=False,indent=2))
# Evidence adjacent to actual uploaded originals, read-only.
folder=Path(next(x['ruta_origen'] for x in m if '08-05-2026_23' in x['archivo'])).parent
proc=next(p for p in folder.iterdir() if p.is_dir() and p.name.startswith('procesamiento'))
def csvrows(p,header=True):
 meta(p)
 raw=p.read_bytes()
 for enc in ('utf-8-sig','latin-1'):
  try:txt=raw.decode(enc);break
  except UnicodeDecodeError:pass
 sep=csv.Sniffer().sniff(txt[:20000],delimiters=';,\t')
 return list(csv.DictReader(io.StringIO(txt),dialect=sep)) if header else [dict(zip(cols,rr)) for rr in csv.reader(io.StringIO(txt),dialect=sep)]
ar=csvrows(proc/'auditoria_ruts_forzados_vigencia_0.csv');ac=csvrows(proc/'auditoria_vigencia_0_codcli_mu2026_20260508_230520.csv');corr=csvrows(proc/'auditoria_correcciones_pes_ready_20260508_230900.csv')
forced_rut={('R',s(r['N_DOC']),s(r['DV']).upper()) for r in ar if r['ACCION']=='FORZADO_A_VIG_0'}
ci_u=collections.defaultdict(list)
for r in u:ci_u[s(r['CODCLI'])].append(r)
forced_cod_records=[r for r in ac if s(r['VIG_ANTES'])=='1'];forced_cod=set();miss=0;ambig=0
for r in forced_cod_records:
 ks={uk(x) for x in ci_u.get(s(r['CODCLI']),[])}
 if len(ks)==1:forced_cod.update(ks)
 elif ks:ambig+=1
 else:miss+=1
result['auditoria_nominas']={'por_rut':{'filas':len(ar),'acciones':cnt(ar,'ACCION'),'personas_cambiadas_1_a_0':len(forced_rut)},'por_codcli':{'filas':len(ac),'vig_antes':cnt(ac,'VIG_ANTES'),'motivos':cnt(ac,'MOTIVO'),'personas_cambiadas_identificadas':len(forced_cod),'codcli_sin_match':miss,'codcli_ambiguos':ambig,'anio_periodo':dict(collections.Counter(s(r['ANIO'])+'|'+s(r['PERIODO']) for r in ac))},'personas_solapadas_entre_nominas':len(forced_rut&forced_cod),'personas_union_cambios':len(forced_rut|forced_cod),'reglas_correcciones':cnt(corr,'rule_id')}
changed_manual=forced_rut|forced_cod
result['impacto_nominas']={}
for name,ks in [('RUT',forced_rut),('CODCLI',forced_cod),('UNION',changed_manual)]:
 found=ks&pi.keys();ret25={key(r) for r,t in elig[2025]};no25={key(r) for r,t in elig[2025] if not t}
 result['impacto_nominas'][name]={'personas':len(ks),'en_pes':len(found),'solo_vig0_pes':sum(all(s(r['VIG'])=='0' for r in pi[k]) for k in found),'con_alguna_vig1_pes':sum(any(s(r['VIG'])=='1' for r in pi[k]) for k in found),'en_base2026':len(ks&bi.keys()),'con_historial_titulado':len(ks&titkeys),'en_retencion_anual2025':len(ks&ret25),'no_retenidos_anual2025':len(ks&no25),'con_misma_cohorte_en_base2026_no_retenidos':sum(any(cohort(x)==cohort(r) for x in bi.get(key(r),[])) for r,t in elig[2025] if key(r) in ks and not t)}
 for t in (2,3):
  v=next(x for x in prev['fuentes'] if x['id']==f'T{t}');rr=rows(Path(v['path']),v['sheet']);tk={uk(r) for r in rr if s(r['ANOINGRESO'])=='2025' and s(r['PERIODOINGRESO'])==str(t)};result['impacto_nominas'][name][f'T{t}_personas']=len(ks&tk)
# Check actual submitted text against archived final CSV content, normalize only representation.
def recordsig(rr):return collections.Counter(tuple(s(r[c]) for c in cols) for r in rr)
actual=csvrows(folder/'matricula_unificada_2026_pregrado_PARA_SUBIR.csv',False);pesready=csvrows(proc/'matricula_unificada_2026_pregrado_PES_READY.csv',False)
first=[r for r in pes[:4070]]
result['cadena_archivo_subido']={'para_subir_igual_orig':recordsig(actual)==recordsig(first),'pes_ready_igual_orig':recordsig(pesready)==recordsig(first),'rows_para_subir':len(actual),'rows_pes_ready':len(pesready)}
tracepath=folder/'MU2026_CIERRE_AUDITORIA_SUBIDAS_REALIZADAS_4165_TRAZABILIDAD.xlsx';meta(tracepath);tr=rows(tracepath,'TRAZABILIDAD_DATOSALUMNOS');ts=rows(tracepath,'SUBIDAS_REALIZADAS_4165')
result['cadena_archivo_subido']['cierre_4165_igual_orig']=recordsig(ts)==recordsig(pes)
result['trazabilidad_envio']={'estado_trazabilidad':cnt(tr,'ESTADO_TRAZABILIDAD'),'regla_consolidacion':cnt(tr,'REGLA_CONSOLIDACION_APLICADA'),'motivo_inclusion':cnt(tr,'MOTIVO_INCLUSION'),'fuente_vig':cnt(tr,'FUENTE_VIG')}
result['fuentes']=sources
(O/'resultado.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({k:result[k] for k in ['auditoria_nominas','impacto_nominas','cadena_archivo_subido','trazabilidad_envio']},ensure_ascii=False,indent=2))
import subprocess
commit='77bdc686ca66fabfe9ef8e6402027aa989b49e5a'
blob=subprocess.check_output(['git','show',commit+':control/vigencia_0_codcli_mu2026.tsv'],cwd=R)
gitcontrol=list(csv.DictReader(io.StringIO(blob.decode()),delimiter='\t'))
result['control_git']={'commit':commit,'path':'control/vigencia_0_codcli_mu2026.tsv','sha256_blob':hashlib.sha256(blob).hexdigest(),'filas':len(gitcontrol),'codcli_identicos_auditoria':{s(r['CODCLI']) for r in gitcontrol}=={s(r['CODCLI']) for r in ac},'motivos':cnt(gitcontrol,'MOTIVO'),'nomina_rut_no_encontrada_en_commit':subprocess.run(['git','cat-file','-e',commit+':patches/mu2026/vig0_nomina_institucional.tsv'],cwd=R,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode!=0}
for pp in [proc/'reporte_matricula.json',proc/'resumen_pes_ready_20260508_230900.md',folder/'KPI_Matricula_Unificada_2026.xlsx']:meta(pp)
result['fuentes']=sources
result['qa']={'hashes_de_fuentes_esperados_coinciden':all(x['hash_ok'] is not False for x in sources),'fuentes_sin_cambios_al_cierre':all(hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256'] for x in sources),'control_git_494_coincide':result['control_git']['codcli_identicos_auditoria'],'auditorias_personas_cambio_sin_solapamiento':len(forced_rut&forced_cod)==0,'balance_737':len(changed_manual)==737 and result['impacto_nominas']['UNION']['solo_vig0_pes']+result['impacto_nominas']['UNION']['con_alguna_vig1_pes']+len(changed_manual-pi.keys())==737,'reproduce_retencion_anual':result['qa_anual'],'cadenas_final_csv_orig':all(result['cadena_archivo_subido'][k] for k in ['para_subir_igual_orig','pes_ready_igual_orig','cierre_4165_igual_orig'])}
assert all(result['qa'].values())
(O/'resultado.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result['qa']))
