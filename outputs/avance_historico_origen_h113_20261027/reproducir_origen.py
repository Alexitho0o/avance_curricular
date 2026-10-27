"""Reproducción acotada H94D: sin escrituras individuales ni ejecución del motor.
El mapeo externo no localizado se deja explícito; no se inventan CODCLI.
"""
from pathlib import Path
import subprocess, hashlib, json, csv, re, unicodedata
from datetime import datetime, timezone
from collections import Counter, defaultdict
import pandas as pd
REPO=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
OD=next(Path('/Users/alexi/Library/CloudStorage').glob('OneDrive-InstitutoProfesionalSanSebasti*'))
P=OD/'Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Avance Curricular/2026'
SRC={
 'promedios':OD/'IPSS_CONCILIACION_UMAS_SIES_BASES/04_UMAS_PROMEDIOSDEALUMNOS/PROMEDIOSDEALUMNOS_7804.xlsx',
 'precarga':P/'5809_Precarga Matrícula Avance Curricular 2026.csv',
 'h113':P/'AVANCE_CURRICULAR_2026_SALIDAS_20260704_221542/5809_MATRICULA_AVANCE_CURRICULAR_2026_SUBIR_SIES_ID_16768_FINAL_H113_REGENERADO.csv',
 'h114b':P/'5809_MATRICULA_AVANCE_CURRICULAR_2026_SUBIR_SIES_ID_16768_H114B_CORREGIDO_PLAN.csv',
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO).decode().rstrip('\n')
def dump(n,o):(OUT/n).write_text(json.dumps(o,ensure_ascii=False,indent=2,default=str)+'\n')
def normtxt(x):return re.sub(r'\s+',' ',unicodedata.normalize('NFKD',str(x)).encode('ascii','ignore').decode().upper().strip())
def legacy_doc(x):
 s=re.sub(r'[^0-9K]','',str(x or '').upper().strip().replace('.','').replace('-',''))
 return s[:-1] if len(s)>1 and s[-1] in '0123456789K' else s
cols=['TIPO_DOCUMENTO','NUM_DOCUMENTO','DV','PRIMER_APELLIDO','SEGUNDO_APELLIDO','NOMBRES','SEXO','FECHA_NACIMIENTO','CODIGO_UNICO','PLAN_ESTUDIOS','ANIO_INGRESO_CARRERA_ACTUAL','SEM_INGRESO_CARRERA_ACTUAL','ANIO_INGRESO_CARRERA_ORIGEN','SEM_INGRESO_CARRERA_ORIGEN','CURSO_1ER_SEM','CURSO_2DO_SEM','UNIDADES_CURSADAS','UNIDADES_APROBADAS','UNID_CURSADAS_TOTAL','UNID_APROBADAS_TOTAL','VIGENCIA']
measures=cols[14:20]
def read_nohead(p):return pd.read_csv(p,sep=';',header=None,names=cols,dtype=str,keep_default_na=False,encoding='latin1')
checks=[]
def check(n,e,v):checks.append(dict(control=n,esperado=e,observado=v,estado='PASS' if e==v else 'FAIL',clasificacion='B/C'))
start={'branch':git('branch','--show-current'),'head':git('rev-parse','HEAD'),'status':git('status','--short').splitlines()}
tracked=[l[3:] for l in start['status'] if not l.startswith('??')]
protected={f:sha(REPO/f) for f in tracked if (REPO/f).is_file()}
sources={k:dict(ruta=str(v),sha256=sha(v),bytes=v.stat().st_size) for k,v in SRC.items()}
check('Hash PROMEDIOS fuente H51','83a0ba72b21d25dd0d151b75fb0182a1f55bbe3f5efba06d088c994067262fca',sources['promedios']['sha256'])
check('Hash H113','54a7cbbb6b30784835b9d0a3df9e842285edb6249cbbd53ae54b6d4e82b8aab3',sources['h113']['sha256'])
frames=pd.read_excel(SRC['promedios'],sheet_name=None,dtype=str,keep_default_na=False,engine='openpyxl')
print('PROMEDIOS leído', {k:len(v) for k,v in frames.items()},flush=True)
parts=[]
for name,frame in frames.items():
 f=frame.copy();f['_HOJA_PROMEDIOS']=name;parts.append(f)
prom=pd.concat(parts,ignore_index=True,sort=False)
prom['_CODCLI_NORM']=prom['CODCLI'].astype(str).str.strip()
prom['_DOC_NORM']=prom['RUT'].map(legacy_doc)
prom['_ANO_NUM']=pd.to_numeric(prom['ANO'].astype(str).str.extract(r'(\d{4})',expand=False),errors='coerce')
prom['_PERIODO_NUM']=pd.to_numeric(prom['PERIODO'].astype(str).str.replace(',','.'),errors='coerce')
prom['_ESTADO_NORM']=prom['ESTADO'].map(normtxt)
prom['_ESTADO_ACAD_NORM']=prom['ESTADO_ACADEMICO'].map(normtxt)
# Igual a drop_duplicates posterior a concatenar documentos y CODCLI en H94D.
prom=prom.drop_duplicates().reset_index(drop=True)
bydoc={k:list(v) for k,v in prom.groupby('_DOC_NORM').groups.items()}
bycli={k:list(v) for k,v in prom.groupby('_CODCLI_NORM').groups.items()}
target=read_nohead(SRC['h113']); corrected=read_nohead(SRC['h114b'])
raw=pd.read_csv(SRC['precarga'],sep=';',encoding='latin1',dtype=str,keep_default_na=False)
check('Filas precarga',2371,len(raw));check('Filas H113',2371,len(target))
keycols=['TIPO_DOCUMENTO','NUM_DOCUMENTO','DV','CODIGO_UNICO','PLAN_ESTUDIOS']
check('Llaves precarga/H113 en orden',True,raw[keycols].values.tolist()==target[keycols].values.tolist())
check('Llaves individuales sin duplicados',0,int(target.duplicated(keycols).sum()))
# Mismo algoritmo histórico, únicamente sin el mapeo externo faltante.
def calculate(ix):
 s=prom.loc[ix];ann=s[s['_ANO_NUM'].eq(2025)];hist=s[s['_ANO_NUM'].le(2025)]
 ar=ann[ann['_ESTADO_NORM'].isin(['A','R'])];a=ann[ann['_ESTADO_NORM'].eq('A')]
 pers=set(ar['_PERIODO_NUM'].dropna())
 return ['SI' if pers & {1,5} else 'NO','SI' if pers & {2,3,4,6} else 'NO',str(len(ar)),str(len(a)),str(hist['_ESTADO_NORM'].isin(['A','E','I','R']).sum()),str(hist['_ESTADO_NORM'].isin(['A','E','I']).sum())]
comparison=[]; group=defaultdict(lambda:dict(registros=0,coinciden_seis=0,diferencias_seis=0,campos_distintos=0))
diffcounts=Counter(); input_doc_groups=defaultdict(set); source_collisions={}
for row in target.to_dict('records'):
 input_doc_groups[legacy_doc(row['NUM_DOCUMENTO'])].add((row['TIPO_DOCUMENTO'],row['NUM_DOCUMENTO'],row['DV']))
collisions={k:v for k,v in input_doc_groups.items() if len(v)>1}
multicli=multicareer=multiplan=source_repeat_approval=base_empty=collision_rows=0
sums_calc=Counter();sums_target=Counter(); exact_all=0; total_approval_repeats=0
no_career_filter_units=0; details=[]; distinct_bodies_rows=0; unmatched_aggregate=[]
for row in target.to_dict('records'):
 doc=legacy_doc(row['NUM_DOCUMENTO']);ix=set(bydoc.get(doc,[])) if doc else set()
 candidates=set(prom.loc[list(ix),'_CODCLI_NORM']) if ix else set()
 for cli in candidates:
  if cli.strip():ix.update(bycli.get(cli,[]))
 ix=sorted(ix); calc=calculate(ix);expected=[row[c] for c in measures]
 diffs=[c for c,x,y in zip(measures,calc,expected) if x!=y]
 exact_all+=not diffs;diffcounts.update(diffs)
 k=(row['CODIGO_UNICO'],row['PLAN_ESTUDIOS']);g=group[k];g['registros']+=1;g['coinciden_seis']+=not diffs;g['diferencias_seis']+=bool(diffs);g['campos_distintos']+=len(diffs)
 for c,x,y in zip(measures[2:],calc[2:],expected[2:]):sums_calc[c]+=int(x);sums_target[c]+=int(y)
 hist=prom.loc[ix];hist=hist[hist['_ANO_NUM'].le(2025) & hist['_ESTADO_NORM'].isin(['A','E','I','R'])]
 bodies={re.sub(r'[^0-9K]','',str(v).upper()) for v in hist['RUT'].dropna() if str(v).strip()}
 distinct_bodies_rows+=int(len(bodies)>1)
 if diffs:
  unmatched_aggregate.append({'codigo_unico':row['CODIGO_UNICO'],'plan_estudios':row['PLAN_ESTUDIOS'],'valores_reproducidos':dict(zip(measures,calc)),'valores_h113':dict(zip(measures,expected)),'filas_fuente_seleccionada':len(ix),'clasificacion':'B/C/E'})
 careers={v for v in hist['CODCARR'].dropna().astype(str) if v and v!='nan'}
 plans={v for v in hist['PLAN_DE_ESTUDIO'].dropna().astype(str) if v and v!='nan'}
 clis={v for v in hist['_CODCLI_NORM'].dropna().astype(str) if v and v!='nan'}
 multicli+=len(clis)>1;multicareer+=len(careers)>1;multiplan+=len(plans)>1;base_empty+=not ix;collision_rows+=doc in collisions
 approved=hist[hist['_ESTADO_NORM'].isin(['A','E','I'])]
 repeated=approved.duplicated(['_CODCLI_NORM','PLAN_DE_ESTUDIO','CODRAMO']).sum()
 source_repeat_approval+=int(repeated>0);total_approval_repeats+=int(repeated)
 details.append({'diffs':diffs,'legacy_doc':doc,'source_ix':ix})
comparison=[dict(codigo_unico=k[0],plan_estudios=k[1],**v,clasificacion='B/C') for k,v in group.items()]
with (OUT/'CONCILIACION_PRIMARIA_POR_PLAN.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(comparison[0]));w.writeheader();w.writerows(comparison)
results={'clasificacion':'B/C/E','universo_fijo':len(target),'origen_algoritmo':'H94D commit 3067c97','mapeo_externo_recuperado':False,'hojas_promedios':{k:len(v) for k,v in frames.items()},'registros_coinciden_seis_columnas':exact_all,'registros_diferentes':len(target)-exact_all,'diferencias_por_columna':dict(diffcounts),'sumas_reproducidas_sin_mapeo':dict(sums_calc),'sumas_h113':dict(sums_target),'alertas_de_atribucion':{'grupos_clave_legacy_con_mas_de_una_identidad_precarga':len(collisions),'filas_precarga_en_esos_grupos':collision_rows,'filas_precarga_con_varios_codcli_en_actividad_seleccionada':multicli,'filas_precarga_con_varias_carreras_en_actividad_seleccionada':multicareer,'filas_precarga_con_varios_planes_en_actividad_seleccionada':multiplan,'filas_precarga_sin_fuente_seleccionada':base_empty,'filas_precarga_con_aprobacion_repetida_codcli_plan_codramo':source_repeat_approval,'repeticiones_aprobadas_contadas_en_precarga':total_approval_repeats},'advertencias':['Coincidir con H113 reproduce una implementación; no acredita por sí solo atribución correcta al programa ni validez académica.','La prueba omite el mapeo externo no localizado; no se declara ejecución íntegra del script histórico.','Alertas multicarrera y repetición requieren contexto; no equivalen automáticamente a errores.']}
results['diferencia_pendiente_agregada']=unmatched_aggregate
results['alertas_de_atribucion']['filas_precarga_con_varios_cuerpos_documentales_en_actividad_seleccionada']=distinct_bodies_rows
results['perfil_documental']={'precarga_documento_solo_digitos':int(target['NUM_DOCUMENTO'].str.fullmatch(r'[0-9]+').sum()),'precarga_dv_separado_no_vacio':int(target['DV'].str.strip().ne('').sum()),'hoja1_rut_solo_digitos':int(frames['Hoja1']['RUT'].str.fullmatch(r'[0-9]+').sum()),'hoja1_dig_separado_no_vacio':int(frames['Hoja1']['DIG'].str.strip().ne('').sum())}
check('Conciliacion universo reproducido',len(target),exact_all+sum(g['diferencias_seis'] for g in group.values()))
# Evidencia Git, sin ejecutar/copy fuentes que puedan tener datos personales.
paths=git('ls-tree','-r','--name-only','3067c97','avance_curricular_2026').splitlines();evidence=[]
for p in paths:
 if any('/'+x in p for x in ['93_','94d_','95_','99_archivo','77_']) and p.endswith(('.py','.json')):
  bs=subprocess.check_output(['git','show','3067c97:'+p],cwd=REPO)
  evidence.append({'commit':git('rev-parse','3067c97'),'ruta':p,'sha256':hashlib.sha256(bs).hexdigest()})
for k,p in SRC.items():check('Fuente conservada '+k,sources[k]['sha256'],sha(p))
for f,h in protected.items():check('Cambio ajeno conservado '+f,h,sha(REPO/f))
check('HEAD conservado',start['head'],git('rev-parse','HEAD'))
check('Rama conservada',start['branch'],git('branch','--show-current'))
dump('RESULTADOS_PRIMARIOS.json',results)
dump('QA.json',{'estado':'PARCIAL_CON_ALERTAS_DE_ATRIBUCION','controles_integridad':checks,'coincidencia_no_es_validacion_funcional':True,'conciliacion_primaria':{'estado':'PENDIENTE','registros_diferentes':len(target)-exact_all,'mapeo_externo_recuperado':False}})
dump('MANIFEST_ORIGEN_H113.json',{'fecha':datetime.now(timezone.utc).isoformat(),'clasificacion':'B/C/D/E','fuentes':sources,'evidencia_git':evidence,'script':{'ruta':str(Path(__file__).resolve()),'sha256':sha(Path(__file__))},'salidas':{n:sha(OUT/n) for n in ['RESULTADOS_PRIMARIOS.json','QA.json','CONCILIACION_PRIMARIA_POR_PLAN.csv']},'git_antes':start,'git_despues':{'branch':git('branch','--show-current'),'head':git('rev-parse','HEAD'),'status':git('status','--short').splitlines()},'commit':False,'push':False,'escritura_datos_individuales':False,'limite':'Sin mapeo externo; solo reproducción acotada en memoria, salida agregada.'})
print(json.dumps(results,ensure_ascii=False,indent=2))
