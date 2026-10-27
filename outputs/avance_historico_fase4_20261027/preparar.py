"""Prepara entradas privadas y agregados trazables; no modifica fuentes."""
import csv,json,hashlib,subprocess,re
from pathlib import Path
from collections import defaultdict
import pandas as pd
import openpyxl
R=Path(__file__).resolve().parents[2]; O=Path(__file__).parent
P=Path.home()/'.local/share/ipss/avance_historico_fase4_20261027';P.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((R/'outputs/avance_historico_fase3_20261027/MANIFEST.json').read_text()); src=m['fuentes']
for v in src.values():assert sha(v['ruta'])==v['sha256'],v['ruta']
def readcsv(p):
 with Path(p).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f,delimiter=';'))
def norm(v):
 if v is None:return ''
 if isinstance(v,float) and v.is_integer():return str(int(v))
 s=str(v).strip().upper();return '' if s in ('NULL','NAN','NONE') else s
def headers(k,s):
 w=openpyxl.load_workbook(src[k]['ruta'],read_only=True,data_only=True);a=list(next(w[s].values));w.close();return a
def csvsource(k,h):
 b=Path(src[k]['ruta']).read_bytes()
 try:t=b.decode('utf-8-sig')
 except UnicodeDecodeError:t=b.decode('cp1252')
 return [dict(zip(h,r)) for r in csv.reader(t.splitlines(),delimiter=';')]
hc=headers('h112b_excel','03_CARGA_SIES_16769_21C');ha=headers('h114b_excel','04_CSV_CON_TITULOS')
plans=csvsource('h112b_csv',hc);a=csvsource('h113_csv',ha);b=csvsource('h114b_csv',ha)
annual=[]
for i,(x,y) in enumerate(zip(a,b),2):
 assert (x['CODIGO_UNICO'],x['PLAN_ESTUDIOS'])==(y['CODIGO_UNICO'],y['PLAN_ESTUDIOS'])
 annual.append([i-1,x['CODIGO_UNICO'],x['PLAN_ESTUDIOS'],*[x.get(k,'') for k in ['TIPO_DOCUMENTO','NUM_DOCUMENTO','DV']],*[int(x[k]) for k in ['UNIDADES_CURSADAS','UNIDADES_APROBADAS','UNID_CURSADAS_TOTAL','UNID_APROBADAS_TOTAL']],int(y['UNID_APROBADAS_TOTAL']),x['ANIO_INGRESO_CARRERA_ORIGEN'],x['ANIO_INGRESO_CARRERA_ACTUAL'],x['VIGENCIA']])
planrows=[[x['CODIGO_UNICO']+'|'+x['PLAN_ESTUDIOS'],x['CODIGO_UNICO'],x['PLAN_ESTUDIOS'],x['NOMBRE_CARRERA'],int(x['TOTAL_UNIDADES_MEDIDA'])]for x in plans]
# Solo campos necesarios; los nombres personales no se incorporan.
fields=['RUT','DIG','CODCLI','CODCARR','PLAN_DE_ESTUDIO','JORNADA','ANO','PERIODO','CODRAMO','CODSECC','ESTADO','NOTA_FINAL','CONVALIDADO','RAMOEQUIV','NIVEL','REGIMEN']
periods=[];rawmeta={};names=defaultdict(set)
for label in ['prom7804','prom12166']:
 print('Leyendo',label,flush=True)
 f=pd.read_excel(src[label]['ruta'],sheet_name='Hoja1',dtype=str,keep_default_na=False);f.columns=[norm(x) for x in f.columns]
 raw=f[fields].copy();raw.insert(0,'FILA_ORIGEN',range(2,len(raw)+2))
 file=P/(label+'.jsonl')
 with file.open('w') as out:
  for row in raw.itertuples(index=False,name=None):out.write(json.dumps(list(row),ensure_ascii=False)+'\n')
 rawmeta[label]={'ruta':str(file),'filas':len(raw),'columnas':['FILA_ORIGEN']+fields,'sha256':sha(file)}
 for c in fields:f[c]=f[c].map(norm)
 f['_PE']=f.RUT.str.replace(r'[.\s]','',regex=True).str.lstrip('0')+'-'+f.DIG
 if 'CARRERA' in f:
  for c,n in zip(f.CODCARR,f.CARRERA):
   if c and n:names[c].add(str(n).strip())
 f['_AR']=f.ESTADO.isin(['A','R'])
 for k,g in f.groupby(['ANO','PERIODO','CODCARR','PLAN_DE_ESTUDIO','JORNADA'],dropna=False):
  c=g.ESTADO.value_counts().to_dict();periods.append([label,*[v or '(Sin dato)' for v in k],len(g),g._PE.nunique(),len(g[['_PE','CODCLI']].drop_duplicates()),c.get('A',0),c.get('R',0),c.get('E',0),c.get('I',0),int((~g.ESTADO.isin(['A','R','E','I'])).sum())])
 del f,raw
w=openpyxl.load_workbook(src['listado']['ruta'],read_only=True,data_only=True);it=w['BBDD Bruta'].values;hs=[norm(x) for x in next(it)]
cf=['CODCARR','NOMBRE_L','CODPESTUD','NOMPESTUD','CODRAMO','NOMBRE','NIVEL','TIPO','SEDE','REGIMEN']
catalog=[]
for i,row in enumerate(it,2):
 d=dict(zip(hs,row));catalog.append([i]+[str(d.get(k) or '') for k in cf])
w.close()
for row in catalog:
 if row[1] and row[2]:names[row[1]].add(row[2])
careers=sorted({r[3] for r in periods}|{x['carrera_UMAS'] or '(Sin dato)' for x in readcsv(R/'outputs/avance_historico_fase3_20261027/MALLAS_CARRERA_PLAN_JORNADA.csv')})
mallas=[]
for x in readcsv(R/'outputs/avance_historico_fase3_20261027/MALLAS_CARRERA_PLAN_JORNADA.csv'):
 cols=['fuente','carrera_UMAS','plan_UMAS','jornada_UMAS','expediente_plan_jornada','estado_listado','unidades_listadas','denominador_listado_sumado','aprobadas_A_distintas_en_listado','reconocidas_E_I_distintas_en_listado','logradas_A_E_I_distintas_en_listado','aprobadas_A_distintas_fuera_listado','reconocidas_E_I_distintas_fuera_listado','expedientes_con_logros_fuera_listado']
 mallas.append([int(x[c]) if i>=4 and i!=5 and x[c]!='' else (None if i>=6 and x[c]=='' else x[c] or '(Sin dato)') for i,c in enumerate(cols)])
data={'sources':src,'annual':annual,'plans':planrows,'periods':periods,'mallas':mallas,'catalog':catalog,'careers':careers,'names':{c:' / '.join(sorted(names.get(c,set()))) or c for c in careers},'raw':rawmeta,'controls':json.loads((R/'outputs/avance_historico_fase3_20261027/RESULTADOS.json').read_text())}
(P/'inputs.json').write_text(json.dumps(data,ensure_ascii=False))
baseline={'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip(),'git_branch':subprocess.check_output(['git','branch','--show-current'],cwd=R).decode().strip(),'protected':{n:sha(R/n)for n in subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=R).decode().splitlines()if(R/n).is_file()},'sources':{k:{'ruta':v['ruta'],'sha256':v['sha256']}for k,v in src.items()},'reference':{'ruta':str(Path.home()/'Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V24.xlsx'),'sha256':sha(Path.home()/'Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V24.xlsx')},'counts':{'annual':len(annual),'plans':len(planrows),'periods':len(periods),'mallas':len(mallas),'catalog':len(catalog)},'private_inputs_sha256':sha(P/'inputs.json')}
(O/'BASELINE.json').write_text(json.dumps(baseline,ensure_ascii=False,indent=2)+'\n');print(baseline['counts'])
