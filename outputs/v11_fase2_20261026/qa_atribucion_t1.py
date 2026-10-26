"""Audita trazabilidad de contextos v11 sin divulgar identidades ni cambiar bases."""
import collections, hashlib, json, os, re, sqlite3
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).parent
PRIVATE=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026')
BASES=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES')
VISTA=Path('/Users/alexi/.local/share/ipss/trazabilidad_integral_fase3_20261025/VISTA_T1_T2_T3.json')
SRC=[BASES/'04_UMAS_PROMEDIOSDEALUMNOS'/f'PROMEDIOSDEALUMNOS_{n}.xlsx' for n in (7804,12166,3233)]
DA=BASES/'03_UMAS_DATOSDEALUMNOS/DATOSDEALUMNOS_12159.xlsx'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def clean(v):
 s=str('' if v is None else v).strip().upper();return '' if s in ('NONE','NULL','NAN') else s
def norm(v,d=None):
 s=clean(v).replace('.','').replace(' ','')
 if d is None:
  if '-' not in s:return None
  s,d=s.split('-',1)
 d=clean(d)
 return str(int(s))+'-'+d if re.fullmatch(r'\d+',s) and re.fullmatch(r'[0-9K]',d) else None
def key(x):return (x['persona'],x['CODCLI'],x['plan'],str(x['anio']),str(x['periodo']),x['carrera'],x['sede_umas_actual'],str(x['jornada_sies']))
def get(row,h,k):
 i=h.get(k);return clean(row[i]) if i is not None and i<len(row) else ''
def reader(p):
 wb=openpyxl.load_workbook(p,read_only=True,data_only=True);ws=wb['Hoja1'];it=ws.iter_rows(values_only=True);h={clean(v):i for i,v in enumerate(next(it))}
 for n,row in enumerate(it,2):yield n,h,row
 wb.close()
def family(s):
 m=re.fullmatch(r'(I\d+S\d+C\d+J\d+)V\d+',str(s or ''));return m.group(1) if m else ''
ledger=ROOT/'outputs/v11_fase2_20261026/RESULTADOS_INDICE.json';srcmeta=json.loads(ledger.read_text())
for p in SRC+[DA]:
 if sha(p)!=srcmeta['fuentes_sha256'][p.name]:raise ValueError('Fuente cambió: '+p.name)
if sha(VISTA)!=srcmeta['vista_sha256']:raise ValueError('Vista cambió')
descriptor=json.loads((OUT/'DESCRIPTOR_CANDIDATA.json').read_text()); dbpath=Path(descriptor['base_privada']['ruta'])
if sha(dbpath)!=descriptor['base_privada']['sha256']:raise ValueError('Candidata cambió')
active=json.loads((ROOT/'data/diccionario_sies_seguimiento/activo.json').read_text());d10=json.loads((ROOT/active['descriptor']).read_text());p10=Path(d10['base_privada']['ruta'])
if sha(p10)!=d10['base_privada']['sha256']:raise ValueError('V10 cambió')
db10=sqlite3.connect(p10.as_uri()+'?mode=ro',uri=True);db11=sqlite3.connect(dbpath.as_uri()+'?mode=ro',uri=True)
oldmax=db10.execute('select max(id) from observaciones').fetchone()[0]
new=[json.loads(r[0]) for r in db11.execute('select payload from observaciones where id>?',(oldmax,))]
candidates=json.loads((PRIVATE/'CONTEXTOS_CANDIDATOS.json').read_text()); candidates_by={key(x):x for x in candidates};
normnew={(x['persona'],x['CODCLI'],x['plan'],str(x['ano']),str(x['periodo']),x['carrera'],x['sede_dimension'],str(x['jornada_sies'])):x for x in new}
assert len(normnew)==len(new)==1126 and all(k in candidates_by for k in normnew)
prefix=collections.defaultdict(list)
for k in candidates_by:prefix[k[:5]].append(k)
amb=[keys for keys in prefix.values() if len(keys)>1 and not any(k in normnew for k in keys)]
assert sum(map(len,amb))==2
pending=[x for x in json.loads(VISTA.read_text()) if not x['contextos']]; positions=collections.defaultdict(list)
for i,x in enumerate(pending):
 if x.get('tipo_doc')=='R':positions[(x['persona'],str(x['anio_observado']),str(x['periodo_nativo']))].append((i,x))
needed=collections.defaultdict(dict)
for k,c in candidates_by.items():
 for f,nums in c['fuentes_filas'].items():
  for n in nums:needed[f].setdefault(int(n),[]).append(k)
baseline=collections.defaultdict(set);mu=collections.defaultdict(set)
for pe,an,cod,payload in db10.execute('select persona,anio,codigo,payload from mu_anual'):
 mu[(pe,str(an))].add(cod)
for pe,cli,pl,an,per,payload in db10.execute('select persona,codcli,plan,anio,periodo,payload from observaciones where periodo="1"'):
 x=json.loads(payload);doc=x.get('codigo_documental_atribuible') or '';internal=x.get('codigo_interno_adoptado') or '';code='' if doc and internal and doc!=internal else doc or internal;baseline[(pe,cli,str(an))].add((pl,x.get('carrera',''),code))
oldpers={r[0] for r in db10.execute('select distinct persona from observaciones')}; oldexp={(r[0],r[1]) for r in db10.execute('select distinct persona,codcli from observaciones')}
newpers={x['persona'] for x in new}; newexp={(x['persona'],x['CODCLI']) for x in new}
people_current=collections.defaultdict(set);wantcli={x['CODCLI'] for x in new};wanted_people={x['persona'] for x in new}
for i,h,r in reader(DA):
 cli=get(r,h,'CODCLI');pe=norm(get(r,h,'RUT'))
 if cli in wantcli and pe:people_current[cli].add((pe,get(r,h,'SEDE'),get(r,h,'CODCARPR')))
origin_activity=collections.defaultdict(set); checks=collections.Counter();ref_ok=collections.Counter();ref_failed=collections.Counter()
origin_years={(x['persona'],str(p['anio_origen']),x['CODCLI']) for x in new for _,p in positions.get((x['persona'],str(x['ano']),str(x['periodo'])),[])}
for path in SRC:
 for i,h,r in reader(path):
  pe=norm(get(r,h,'RUT'),get(r,h,'DIG'));cli=get(r,h,'CODCLI');an=get(r,h,'ANO');per=get(r,h,'PERIODO');pl=get(r,h,'PLAN_DE_ESTUDIO');car=get(r,h,'CODCARR');jor=get(r,h,'JORNADA')
  if per=='1' and (pe,an,cli) in origin_years:origin_activity[(pe,an,cli)].add((pl,car,jor,path.name,i))
  for k in needed[path.name].get(i,[]):
   c=candidates_by[k]; expect=(c['persona'],c['CODCLI'],c['plan'],c['anio'],c['periodo'],c['carrera']);actual=(pe,cli,pl,an,per,car)
   m={'1':'D','2':'V','4':'O'}; ok=expect==actual and m.get(str(c['jornada_sies']))==jor
   (ref_ok if ok else ref_failed)[path.name]+=1
 assert set(needed[path.name]).issubset(set(range(2,i+1)))
detail=[];cat=collections.Counter();sede=collections.Counter();fam=collections.Counter();criterios=collections.Counter()
for k,x in normnew.items():
 links=positions.get((x['persona'],str(x['ano']),str(x['periodo'])),[])
 if not links:checks['sin_posicion']+=1;continue
 for slot,p in links:
  y=str(p['anio_origen']);b=baseline.get((x['persona'],x['CODCLI'],y),set()); activity=origin_activity.get((x['persona'],y,x['CODCLI']),set()); code=p['codigo_origen_T1']; documented=code in mu.get((x['persona'],y),set())
  aligned=[a for a in b if a[2]==code];same_plan=any(a[0]==x['plan'] for a in aligned);same_career=any(a[1]==x['carrera'] for a in aligned)
  if len(links)>1:status='MULTIPLES_ORIGENES_T1_MISMA_POSICION'
  elif aligned and same_plan and same_career:status='MISMO_CODCLI_PLAN_CARRERA_CODIGO_T1_EN_V10'
  elif aligned:status='MISMO_CODCLI_CODIGO_T1_CAMBIO_O_PLAN_AMBIGUO'
  elif b:status='MISMO_CODCLI_T1_SIN_CODIGO_ORIGEN_ATRIBUIDO'
  elif activity:status='MISMO_CODCLI_T1_EN_PROMEDIOS_SIN_ATRIBUCION_CODIGO'
  else:status='SIN_CODCLI_T1_EN_FUENTES_REVISADAS'
  c=candidates_by[k];da=people_current.get(x['CODCLI'],set());seat=any(z[0]==x['persona'] and z[1]==x['sede_dimension'] for z in da)
  period1_same_plan_career=any(a[0]==x['plan'] and a[1]==x['carrera'] for a in activity)
  period1_same_journey=any(a[0]==x['plan'] and a[1]==x['carrera'] and a[2]=={'1':'D','2':'V','4':'O'}.get(str(x['jornada_sies'])) for a in activity)
  criterios['codigo_T1_en_MU_persona' if documented else 'codigo_T1_no_en_MU_persona']+=1
  criterios['mismo_CODCLI_plan_carrera_T1' if period1_same_plan_career else 'sin_CODCLI_plan_carrera_T1']+=1
  criterios['mismo_CODCLI_plan_carrera_jornada_T1' if period1_same_journey else 'sin_CODCLI_plan_carrera_jornada_T1']+=1
  if not seat:checks['sede_da_no_reproducida']+=1
  cat[status]+=1;sede[x['sede_dimension']]+=1;fam['familia_origen_en_candidatas' if family(code) in c['familias_candidatas'] else 'familia_origen_distinta_o_no_atribuible']+=1
  detail.append({'posicion_indice':slot,'observacion_id':x['observacion_id'],'persona':x['persona'],'CODCLI':x['CODCLI'],'estado_analisis_T1':status,'codigo_T1_en_MU_persona':documented,'plan_y_carrera_T1_corroborados':bool(aligned and same_plan and same_career),'fuentes_actividad_T1':[{'fuente':a[3],'fila':a[4]} for a in sorted(activity)],'origenes_posibles':len(links)})
amb_summary=[]
for group in amb:
 rr=[candidates_by[k] for k in group];amb_summary.append({'numero_contextos':len(group),'carreras':sorted(set(z['carrera'] for z in rr)),'sedes':sorted(set(z['sede_umas_actual'] for z in rr)),'jornadas':sorted(set(z['jornada_sies'] for z in rr)),'familias':sorted({f for z in rr for f in z['familias_candidatas']}),'anio':rr[0]['anio'],'periodo':rr[0]['periodo'],'fuentes':sorted({p for z in rr for p in z['fuentes_filas']}),'clasificacion':'E: llave sin dimensiones no identifica una sola observación; conservar ambas alternativas'})
allpersons={r[0] for r in db11.execute('select distinct persona from observaciones')};allexp={(r[0],r[1]) for r in db11.execute('select distinct persona,codcli from observaciones')}
oldexp_career={(r[0],r[1],r[2]) for r in db10.execute('select distinct persona,codcli,carrera from observaciones')};allexp_career={(r[0],r[1],r[2]) for r in db11.execute('select distinct persona,codcli,carrera from observaciones')}
tot={'v10_observaciones':db10.execute('select count(*) from observaciones').fetchone()[0],'v11_observaciones':db11.execute('select count(*) from observaciones').fetchone()[0],'v10_personas':len(oldpers),'v11_personas':len(allpersons),'personas_nuevas':len(newpers-oldpers),'personas_existentes_con_contextos':len(newpers&oldpers),'v10_expedientes_persona_codcli':len(oldexp),'v11_expedientes_persona_codcli':len(allexp),'expedientes_nuevos':len(newexp-oldexp),'expedientes_existentes_con_contextos':len(newexp&oldexp)}
tot.update({'v10_expedientes_persona_codcli_carrera':len(oldexp_career),'v11_expedientes_persona_codcli_carrera':len(allexp_career),'expedientes_persona_codcli_carrera_nuevos':len(allexp_career-oldexp_career)})
db10.close();db11.close()
if len(detail)!=1126 or ref_failed or checks:status='FALLIDO_O_ALERTA'
else:status='EVIDENCIA_DE_FILAS_VERIFICADA_ATRIBUCION_PENDIENTE'
out={'estado':status,'contextos_nuevos':len(new),'vinculos_posicion':len(detail),'recuento_T1':dict(cat),'criterios_T1_no_excluyentes':dict(criterios),'familia_T1_vs_candidata':dict(fam),'sede_actual':dict(sede),'referencias_fila_ok':dict(ref_ok),'referencias_fila_no_coinciden':dict(ref_failed),'alertas':dict(checks),'llaves_ambiguas':amb_summary,'totales':tot,'fuentes_sha256':srcmeta['fuentes_sha256'],'vista_sha256':sha(VISTA),'base_v10_sha256':sha(p10),'base_v11_sha256':sha(dbpath),'nota':'Vínculo personal no prueba identidad de expediente ni sede histórica. Códigos T1 requieren atribución por CODCLI y período. Sin asignaciones nuevas.'}
p=PRIVATE/'QA_ATRIBUCION_T1_DETALLE_V3.json'
fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w') as f:json.dump(detail,f,ensure_ascii=False)
(OUT/'QA_ATRIBUCION_T1_AGREGADO_V3.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False))
