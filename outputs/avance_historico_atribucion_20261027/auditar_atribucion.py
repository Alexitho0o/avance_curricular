"""Atribución contextual de las 489 alertas H113; solo agregados y lectura."""
from pathlib import Path
import json,re,sys,hashlib,subprocess,csv
from collections import Counter,defaultdict
from datetime import datetime,timezone
import pandas as pd
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
OLD=ROOT/'outputs/avance_historico_origen_h113_20261027'
manifest=json.loads((OLD/'MANIFEST_ORIGEN_H113.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT).decode().strip()
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def clean(x):
 if pd.isna(x):return ''
 s=str(x).strip().upper();return '' if s in ('NAN','NONE','NULL') else s
def body(x):return re.sub(r'[.\s]','',clean(x))
def legacy(x):
 s=re.sub('[^0-9K]','',str(x).upper().replace('.','').replace('-','').strip())
 return s[:-1] if len(s)>1 else s
checks=[]
def ck(n,a,b):checks.append({'control':n,'esperado':a,'observado':b,'estado':'PASS' if a==b else 'FAIL','clase':'B/C'})
start={'head':git('rev-parse','HEAD'),'rama':git('branch','--show-current')}
protected={x:sha(ROOT/x) for x in git('diff','--name-only','HEAD').splitlines() if (ROOT/x).is_file()}
src={k:Path(v['ruta']) for k,v in manifest['fuentes'].items()}
for k,p in src.items():ck('Fuente hash '+k,manifest['fuentes'][k]['sha256'],sha(p))
frames=pd.read_excel(src['promedios'],sheet_name=None,dtype=str,keep_default_na=False)
print('Fuentes leidas; procesamiento individual solo en memoria',flush=True)
parts=[]
for name,f in frames.items():
 f=f.copy();f['_HOJA_PROMEDIOS']=name;parts.append(f)
prom=pd.concat(parts,ignore_index=True,sort=False)
prom['_CODCLI_NORM']=prom['CODCLI'].astype(str).str.strip();prom['_DOC_NORM']=prom['RUT'].map(legacy)
prom['_ANO_NUM']=pd.to_numeric(prom['ANO'].astype(str).str.extract(r'(\d{4})',expand=False),errors='coerce')
prom['_PERIODO_NUM']=pd.to_numeric(prom['PERIODO'].astype(str).str.replace(',','.'),errors='coerce')
prom['_ESTADO_NORM']=prom['ESTADO'].map(clean)
prom=prom.drop_duplicates().reset_index(drop=True)
bydoc={k:set(v) for k,v in prom.groupby('_DOC_NORM').groups.items()};bycli={k:set(v) for k,v in prom.groupby('_CODCLI_NORM').groups.items()}
t=pd.read_csv(src['h113'],sep=';',header=None,dtype=str,keep_default_na=False,encoding='latin1')
focus=[]
for i,row in t.iterrows():
 ix=set(bydoc.get(legacy(row[1]),[]))
 for cli in set(prom.loc[list(ix),'_CODCLI_NORM']):
  if cli and cli!='nan':ix|=bycli.get(cli,set())
 h=prom.loc[sorted(ix)];h=h[h['_ANO_NUM'].le(2025)&h['_ESTADO_NORM'].isin(['A','E','I','R'])]
 careers={clean(x) for x in h['CODCARR']}-{''}
 if len(careers)>1:focus.append(i)
ck('Foco multicarrera previo',489,len(focus));ck('Universo intacto',2371,len(t))
# Only actual subject rows and exact document/DV; no further expansion by CODCLI.
h=prom[prom['_HOJA_PROMEDIOS'].eq('Hoja1') & prom['_ANO_NUM'].le(2025)&prom['_ESTADO_NORM'].isin(['A','E','I','R'])].copy()
h['_BODY']=h['RUT'].map(body);h['_DV']=h['DIG'].map(body)
strict={k:list(v) for k,v in h.groupby(['_BODY','_DV']).groups.items()}
sys.path.insert(0,str(ROOT))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento
service=DiccionarioSiesSeguimiento()
active=ROOT/'data/diccionario_sies_seguimiento/activo.json';activehash=sha(active)
group_path=ROOT/'data/versiones_por_cohorte/20261016/grupos_existentes.json'
groups=json.loads(group_path.read_text());journeys=defaultdict(set)
for g in groups:
 for fam in g['familias']:
  mm=re.fullmatch(r'I\d+S(\d+)C\d+J(\d+)',fam)
  if mm:journeys[(g['codcarpr'],mm[1],g['jornada'])].add(mm[2])
# Query once per exact context. API owns code/edition/ambiguity decisions.
cache={}; absent_reasons=Counter(); absent_years=Counter(); levels=Counter(); reasons=Counter();source_contexts=set();personset=set();expedients=set()
metrics=['cursadas_2025','aprobadas_2025','cursadas_acumuladas','aprobadas_acumuladas']
buckets=['MISMO_CODIGO','OTRA_VERSION_MISMA_FAMILIA','OTRA_FAMILIA','PENDIENTE']
aggregate={b:[0]*4 for b in buckets};percode=defaultdict(lambda:{b:[0]*4 for b in buckets})
annual_status=Counter();row_status=Counter();known_other=0;no_exact=0;still_multi=0;legacy_sum=[0]*4;exact_sum=[0]*4;rows=[]
for i in focus:
 r=t.loc[i];code=r[8];family=code.rsplit('V',1)[0]
 for k in range(4):legacy_sum[k]+=int(r[16+k])
 selected=h.loc[strict.get((body(r[1]),body(r[2])),[])] if r[0]=='R' and r[2] else h.iloc[:0]
 if selected.empty:no_exact+=1
 careers=set(selected['CODCARR'].map(clean))-{''};still_multi+=int(len(careers)>1)
 rb={b:[0]*4 for b in buckets};rs=Counter();units=Counter()
 for ctx,g in selected.groupby(['CODCLI','PLAN_DE_ESTUDIO','CODCARR','JORNADA','_ANO_NUM','_PERIODO_NUM'],dropna=False):
  cli,plan,career,jour,year,period=ctx
  if pd.isna(year) or pd.isna(period) or float(period)!=int(period):
   state='PENDIENTE';reason='CONTEXTO_INCOMPLETO';found=None
  else:
   identity=body(r[1])+'-'+body(r[2]);year=str(int(year));period=str(int(period))
   key=(identity,clean(cli),clean(plan),clean(career),clean(jour),year,period)
   source_contexts.add(key);personset.add(identity);expedients.add((identity,clean(cli),clean(career)))
   if key not in cache:
    val=service.consultar(persona=identity,codcli=clean(cli),plan=clean(plan),anio=year,periodo=period,carrera=clean(career))
    if val['estado']=='REUTILIZABLE':
     evidence=val['evidencia'];mm=re.fullmatch(r'I\d+S(\d+)C\d+J(\d+)V\d+',val['codigo_sies'])
     allowed=journeys.get((clean(career),mm[1],clean(jour)),set()) if mm else set()
     if allowed!={mm[2]}:val={'estado':'EXCEPCION','motivo':'JORNADA_RAW_NO_CONFIRMADA_EN_MAPEO','codigo_sies':None}
    if val.get('motivo')=='CONTEXTO_NO_LOCALIZADO':
     indexed=service.db.execute('SELECT plan,anio,periodo,carrera FROM observaciones WHERE persona=? AND codcli=?',(identity,clean(cli))).fetchall()
     sameperiod=[v for v in indexed if v[1]==year and v[2]==period]
     sameplan=[v for v in sameperiod if v[0]==clean(plan)]
     cause='EXPEDIENTE_NO_INDEXADO' if not indexed else 'PERIODO_NO_INDEXADO' if not sameperiod else 'PLAN_DISTINTO_EN_INDICE' if not sameplan else 'CARRERA_DISTINTA_EN_INDICE'
     absent_reasons[cause]+=1;absent_years[year]+=1
    levels[val.get('nivel_respaldo','E_PENDIENTE')]+=1
    cache[key]=val
   val=cache[key];found=val.get('codigo_sies');reason=val.get('motivo','SIN_MOTIVO')
   state='MISMO_CODIGO' if found==code else ('OTRA_VERSION_MISMA_FAMILIA' if found and found.rsplit('V',1)[0]==family else 'OTRA_FAMILIA' if found else 'PENDIENTE')
  annual=g[g['_ANO_NUM'].eq(2025)]
  nums=[int(annual['_ESTADO_NORM'].isin(['A','R']).sum()),int(annual['_ESTADO_NORM'].eq('A').sum()),len(g),int(g['_ESTADO_NORM'].isin(['A','E','I']).sum())]
  rb[state]=[a+b for a,b in zip(rb[state],nums)];rs[state]+=1
  if state=='PENDIENTE':reasons[reason]+=1
 for b in buckets:
  aggregate[b]=[x+y for x,y in zip(aggregate[b],rb[b])];percode[code][b]=[x+y for x,y in zip(percode[code][b],rb[b])]
 total=[sum(rb[b][k] for b in buckets) for k in range(4)];exact_sum=[a+b for a,b in zip(exact_sum,total)]
 if total[0]==0:ast='SIN_UNIDADES_ANUALES_A_R_OBSERVADAS'
 elif rb['PENDIENTE'][0]>0:ast='CON_ATRIBUCION_ANUAL_PENDIENTE'
 elif rb['OTRA_FAMILIA'][0]+rb['OTRA_VERSION_MISMA_FAMILIA'][0]>0:ast='CODIGOS_ANUALES_RESPALDADOS_DISTINTOS'
 else:ast='TODO_ANUAL_MISMO_CODIGO'
 annual_status[ast]+=1
 if not total[2]:status='SIN_ACTIVIDAD_EXACTA'
 elif rb['PENDIENTE'][2]>0:status='CON_CONTEXTO_PENDIENTE'
 elif rb['OTRA_FAMILIA'][2]+rb['OTRA_VERSION_MISMA_FAMILIA'][2]>0:status='CODIGOS_COMPLETOS_CON_CAMBIOS'
 else:status='TODO_MISMO_CODIGO'
 row_status[status]+=1
 known_other+=int(rb['OTRA_FAMILIA'][2]>0)
 rows.append({'codigo_unico':code,'estado_anual':ast,'estado_acumulado':status})
ck('Particion filas anual',len(focus),sum(annual_status.values()));ck('Particion filas acumulado',len(focus),sum(row_status.values()))
ck('Contextos unicos y consultas',len(source_contexts),len(cache))
for k in range(4):ck('Particion unidades '+metrics[k],exact_sum[k],sum(aggregate[b][k] for b in buckets))
result={'clase':'B/C/D/E','universo_total':2371,'filas_foco':len(focus),'filas_aun_multicarrera_con_identidad_exacta':still_multi,'filas_sin_actividad_exacta':no_exact,'personas_con_actividad_exacta':len(personset),'expedientes_persona_codcli_carrera':len(expedients),'contextos_unicos_consultados':len(source_contexts),'filas_con_actividad_de_otra_familia_respaldada':known_other,'estados_anuales_filas':dict(annual_status),'estados_acumulados_filas':dict(row_status),'unidades_H113_foco':dict(zip(metrics,legacy_sum)),'unidades_identidad_exacta_foco':dict(zip(metrics,exact_sum)),'particion_unidades_por_atribucion':{b:dict(zip(metrics,v)) for b,v in aggregate.items()},'motivos_pendientes_consulta_por_fila_precarga':dict(reasons),'diagnostico_contextos_unicos_no_localizados':{'causas':dict(absent_reasons),'anios':dict(absent_years)},'niveles_respaldo_contextos_unicos':dict(levels),'edicion_diccionario':service.edicion,'escenario_adoptado':False,'limites':['PLAN_ESTUDIOS SIES numerico no equivale al nombre de plan UMAS. Coincidencia de codigo no cierra ese enlace.','Otra familia/version histórica no excluye reconocimiento valido; requiere equivalencia aplicable al plan destino.','Unidades son aportes a filas H113; pueden reutilizar contextos. No son personas ni asignaturas únicas institucionales.','No se calculan tasas; no se adopta correccion ni se cambia denominador.']}
with (OUT/'PARTICION_POR_CODIGO.csv').open('w',newline='') as f:
 fields=['codigo_sies','atribucion',*metrics,'clase'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for code,bs in sorted(percode.items()):
  for b,nums in bs.items():w.writerow({'codigo_sies':code,'atribucion':b,**dict(zip(metrics,nums)),'clase':'B/C/E'})
dump('RESULTADOS.json',result)
service.close()
for k,p in src.items():ck('Fuente intacta '+k,manifest['fuentes'][k]['sha256'],sha(p))
for f,v in protected.items():ck('Cambio ajeno intacto '+f,v,sha(ROOT/f))
ck('Puntero diccionario intacto',activehash,sha(active));ck('HEAD intacto',start['head'],git('rev-parse','HEAD'))
ck('Rama intacta',start['rama'],git('branch','--show-current'))
dump('QA.json',{'estado':'PASS_AUDITORIA_PARCIAL' if all(x['estado']=='PASS' for x in checks) else 'FAIL','controles':checks})
dump('MANIFEST.json',{'fecha_utc':datetime.now(timezone.utc).isoformat(),'fuentes':manifest['fuentes'],'script_sha256':sha(__file__),'mapeo_jornada':{'ruta':str(group_path),'sha256':sha(group_path)},'diccionario':{'edicion':service.edicion,'base_sha256':service.descriptor['base_privada']['sha256'],'puntero_sha256':activehash},'salidas':{n:sha(OUT/n) for n in ['RESULTADOS.json','PARTICION_POR_CODIGO.csv','QA.json']},'git_antes':start,'git_despues':{'head':git('rev-parse','HEAD'),'rama':git('branch','--show-current')},'commit':False,'push':False,'identificadores_exportados':False})
print(json.dumps(result,ensure_ascii=False,indent=2))
