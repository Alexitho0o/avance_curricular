"""Revisión dirigida y no destructiva de cronologías de 374 personas.

Separa año documentado MU, período de actividad UMAS y vigencia efectiva del plan.
No actualiza equivalencias, bases, denominadores ni libros anteriores.
"""
import csv,json,hashlib,re,datetime,subprocess,os,itertools
from pathlib import Path
from collections import defaultdict,Counter
import openpyxl
R=Path(__file__).resolve().parents[1];B=R/'outputs/reproduccion_puente_20261023_004044'
BM=json.load(open(B/'MANIFEST.json'));BP=Path(BM['privado'])
stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S');O=R/'outputs'/('trayectorias_374_'+stamp);P=Path.home()/'.local/share/ipss'/('trayectorias_374_'+stamp)
assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
os.umask(0o077);P.mkdir();O.mkdir()
HASH={};INV=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def source(p,expected=None):
 p=Path(p);h=sha(p);assert expected is None or h==expected,str(p);HASH[str(p)]=h;return p
def load(p,h=None):return json.loads(source(p,h).read_text())
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2,default=str))
def outcsv(p,rs):
 if not rs:return
 fields=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fields,delimiter=';');w.writeheader()
  for r in rs:w.writerow({k:json.dumps(v,ensure_ascii=False,default=str) if isinstance(v,(list,tuple,dict)) else v for k,v in r.items()})
def val(v):return '' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip()
def norm(a,b=None):
 a=val(a).upper().replace('.','').replace(' ','');s=a if b is None else a+'-'+val(b).upper()
 if not re.fullmatch(r'\d+-[0-9K]',s):return None
 a,b=s.split('-');return str(int(a))+'-'+b
def date(v):
 if isinstance(v,datetime.datetime):return v.date().isoformat()
 if isinstance(v,datetime.date):return v.isoformat()
 s=val(v)
 if not s:return None
 for fmt in ['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d','%Y-%m-%d %H:%M:%S','%d/%m/%Y %H:%M:%S','%d-%m-%Y %H:%M:%S','%d-%m-%Y %H:%M','%d/%m/%Y %H:%M','%Y%m%d','%d%m%Y']:
  try:return datetime.datetime.strptime(s,fmt).date().isoformat()
  except ValueError:pass
 return None
def read(p,s='Hoja1',h=None):
 p=source(p,h);w=openpyxl.load_workbook(p,read_only=True,data_only=True);ws=w[s];it=iter(ws.values);head=next(it);n=0
 for rn,v in enumerate(it,2):n+=1;yield rn,dict(zip(head,v))
 INV.append({'archivo':str(p),'sha256':HASH[str(p)],'hoja':s,'filas_leidas':n,'encabezados':list(head),'corte_efectivo':'NO_ACREDITADO_POR_NOMBRE_O_DOCPROPS'})
 w.close()
def git():return {str(p):{k:subprocess.check_output(['git','-C',str(p),*a],text=True).strip() for k,a in [('rama',['branch','--show-current']),('head',['rev-parse','HEAD']),('status',['status','--short'])]} for p in [R,R.parent/'CARACTERIZACIÓN',R.parent/'IPSS_Procesos_SIES']}
beforegit=git();dump(O/'GIT_ANTES.json',beforegit)
traj=load(BP/'TRAYECTORIAS_MULTIPLES_PERSONA_FAMILIA.json',BM['salidas_privadas_hashes']['TRAYECTORIAS_MULTIPLES_PERSONA_FAMILIA.json'])
allobs=load(BP/'OBSERVACIONES_PRIVADAS.json',BM['salidas_privadas_hashes']['OBSERVACIONES_PRIVADAS.json'])
people={x['persona'] for x in traj};relations={(x['persona'],x['familia']) for x in traj};assert len(people)==374 and len(relations)==377
obs=[x for x in allobs if x['persona'] in people];G=load(R/'data/versiones_por_cohorte/20261016/grupos_existentes.json')
families={(g['codcarpr'],g['jornada']):g['familias'] for g in G};jmap={'D':'1','V':'2','O':'4'};rev={v:k for k,v in jmap.items()}
dims=load(R/'data/reglas_negocio/20261022_puente_versiones/investigacion_contextual_v3/PRUEBAS_CONTEXTUALES.json')
families_evid={(x['carrera'],rev[x['jornada']]):x['familias'] for x in dims}
f4=load(R/'data/versiones_historicas_sies_umas/fase_4_20261015/fuentes.json')['sources']
relocations=[]
for tag in ['promedios','alumnos']:
 original=Path(f4[tag]['path'])
 actual=sha(original) if original.exists() else None
 if actual!=f4[tag]['sha256']:
  backup=Path('/Users/alexi/Desktop/Caracterizacion_anual_2026_20261015_130336_379868/03_RESPALDOS/P1/01_ENTRADAS')/original.name
  source(backup,f4[tag]['sha256'])
  relocations.append({'fuente_original':str(original),'hash_actual_original':actual,'hash_esperado':f4[tag]['sha256'],'respaldo_usado':str(backup),'estado':'RESPALDO_IDENTICO_VERIFICADO'})
  f4[tag]['path']=str(backup)
dump(O/'RELOCALIZACION_FUENTES.json',relocations)
source(B/'MANIFEST.json');source(R/'docs/fase_4_planes_asignaciones_umas.md');source(R/'common/continuidad_trayectoria.py')
print('Fase 1/4 · Hito 3/3 — Universo 374/377 verificado; relectura de fuentes temporales',flush=True)
pr=[];prindex=defaultdict(list)
for tag,path,h in [('12166','/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_12166.xlsx',BM['fuentes_hashes']['/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_12166.xlsx']),('7804',f4['promedios']['path'],f4['promedios']['sha256'])]:
 for rn,d in read(path,h=h):
  k=norm(d.get('RUT'),d.get('DIG'))
  if k not in people:continue
  z={q:val(d.get(q)) for q in ['CODCLI','CODCARR','PLAN_DE_ESTUDIO','ANO','PERIODO','JORNADA','REGIMEN','RAMOEQUIV','CODRAMO','CODSECC','ESTADO','DESCRIPCION_ESTADO','CONVALIDADO','RUT','DIG']}
  z.update(persona=k,archivo=path,hoja='Hoja1',fila=rn,reporte=tag)
  z['reconocimiento']=z['CONVALIDADO'].upper()=='S' or any(t in z['DESCRIPCION_ESTADO'].upper() for t in ['CONVALID','HOMOLOG'])
  pr.append(z);prindex[tag,k,z['CODCLI'],z['CODCARR']].append(z)
 print('PROMEDIOS '+tag+' leído; filas del foco '+str(sum(x['reporte']==tag for x in pr)),flush=True)
da=[];dindex=defaultdict(list)
for tag,path,h in [('12159','/Users/alexi/Downloads/DATOSDEALUMNOS_12159.xlsx',BM['fuentes_hashes']['/Users/alexi/Downloads/DATOSDEALUMNOS_12159.xlsx']),('11248','/Users/alexi/Downloads/2025/DATOSDEALUMNOS_11248.xlsx',BM['fuentes_hashes']['/Users/alexi/Downloads/2025/DATOSDEALUMNOS_11248.xlsx']),('11998',f4['alumnos']['path'],f4['alumnos']['sha256'])]:
 for rn,d in read(path,h=h):
  k=norm(d.get('RUT'))
  if k not in people:continue
  z={q:val(d.get(q)) for q in ['CODCLI','CODCARPR','SEDE','JORNADA','ANOMATRICULA','PERIODOMATRICULA','ANOINGRESO','PERIODOINGRESO','FECHAMATRICULA','FECHAFIRMA']}
  z.update(persona=k,archivo=path,hoja='Hoja1',fila=rn,reporte=tag,fecha_matricula_iso=date(d.get('FECHAMATRICULA')),fecha_firma_iso=date(d.get('FECHAFIRMA')))
  da.append(z);dindex[k,z['CODCLI'],z['CODCARPR']].append(z)
ev=next(x['rows'] for x in load(BP/'reanudacion/antecedentes_minimos.json') if x['name']=='EVIDENCIAS_SIES')
mus=sorted({(r[8],r[9]) for r in ev if r[1]=='MATRICULA' and ('MAT_IP_CIISA_' in r[8] or 'BASE_RETENCION_MATRICULA' in r[8])})
mu=[];muindex=defaultdict(list)
for path,sh in mus:
 for rn,d in read(path,sh,h=BM['fuentes_hashes'].get(path)):
  historic='MC_CODIGO_UNICO' in d
  k=norm(d.get('MM_N_DOCUMENTO') if historic else d.get('N_DOC'),d.get('MM_DV') if historic else d.get('DV'))
  if k not in people:continue
  code=val(d.get('MC_CODIGO_UNICO')) if historic else 'I162S%sC%sJ%sV%s'%tuple(val(d.get(q)) for q in ['COD_SED','COD_CAR','JOR','VERSION'])
  if not re.fullmatch('I162S[0-9]+C[0-9]+J[0-9]+V[0-9]+',code):continue
  y=val(d.get('MC_CAT_PERIODO') if historic else d.get('ANIO_INFORMADO')).replace('MAT_','')
  z={'persona':k,'ano':y,'codigo':code,'familia':code.rsplit('V',1)[0],'archivo':path,'hoja':sh,'fila':rn,
    'ingreso_actual':val(d.get('MM_ANIO_ACTUAL') if historic else d.get('ANIO_ING_ACT')),'sem_ingreso_actual':val(d.get('MM_SEM_ACTUAL') if historic else d.get('SEM_ING_ACT')),
    'ingreso_origen':val(d.get('MM_ANIO_ORIGEN') if historic else d.get('ANIO_ING_ORI')),'sem_ingreso_origen':val(d.get('MM_SEM_ORIGEN') if historic else d.get('SEM_ING_ORI')),
    'fecha_matricula_original':val(d.get('FECHA_MATRICULA')),'fecha_matricula_iso':date(d.get('FECHA_MATRICULA')),'reincorporacion':val(d.get('REINCORPORACION'))}
  mu.append(z);muindex[k,z['familia'],y].append(z)
print('Fase 2/4 · Hito 2/3 — Fuentes releídas; comparar planes, fechas y secuencias',flush=True)
# Matched subject/year/period units allow comparisons without assuming report chronology.
unit=defaultdict(lambda:defaultdict(list))
for x in pr:
 key=tuple(x[k] for k in ['persona','CODCLI','CODCARR','JORNADA','ANO','PERIODO','CODRAMO'])
 unit[key][x['reporte']].append(x)
comparisons=[]
for key,v in unit.items():
 if len(v)<2:continue
 a=sorted({x['PLAN_DE_ESTUDIO'] for x in v['7804']});b=sorted({x['PLAN_DE_ESTUDIO'] for x in v['12166']})
 comparisons.append({'persona':key[0],'CODCLI':key[1],'carrera':key[2],'ano':key[4],'periodo':key[5],'asignatura':key[6],
  'planes_7804':a,'planes_12166':b,'estado':'IGUAL' if a==b else 'DISTINTO_ENTRE_REPORTES','localizadores':[[x['archivo'],x['hoja'],x['fila']] for vv in v.values() for x in vv]})
segments=[];segidx={};relationrows=[];pairs=[]
for tr in traj:
 person,fam=tr['persona'],tr['familia'];segs=[]
 for s in tr['expedientes_planes']:
  cli,c,p=s['CODCLI'],s['carrera'],s['plan'];praw=[x for x in prindex['12166',person,cli,c] if x['PLAN_DE_ESTUDIO']==p and x['ANO'].isdigit() and x['PERIODO'].isdigit() and jmap.get(x['JORNADA'])==fam.rsplit('J',1)[1]]
  periods=sorted({(int(x['ANO']),int(x['PERIODO'])) for x in praw});direct=sorted({(int(x['ANO']),int(x['PERIODO'])) for x in praw if not x['reconocimiento']})
  ds=[x for x in dindex[person,cli,c] if x['SEDE']=='RE' and jmap.get(x['JORNADA'])==fam.rsplit('J',1)[1]]
  years=sorted({str(y) for y,t in periods});ymu={y:sorted({m['codigo'] for m in muindex[person,fam,y]}) for y in years}
  new={'persona':person,'familia':fam,'CODCLI':cli,'carrera':c,'plan':p,'regimenes':sorted({x['REGIMEN'] for x in praw}),
   'periodos_observados':periods,'periodos_sin_marca_reconocimiento':direct,'filas_asignatura':len(praw),'filas_reconocimiento':sum(x['reconocimiento'] for x in praw),
   'contextos_DA':ds,'codigos_MU_por_ano':ymu,'clasificacion':'B/C; E vigencia efectiva plan'}
  segs.append(new);segments.append(new);segidx[person,fam,cli,c,p]=new
 for a,b in itertools.combinations(segs,2):
  ya={y for y,t in a['periodos_observados']};yb={y for y,t in b['periodos_observados']}
  same=len(a['regimenes'])==len(b['regimenes'])==1 and a['regimenes']==b['regimenes']
  both=set(map(tuple,a['periodos_observados']))&set(map(tuple,b['periodos_observados'])) if same else set()
  bothdirect=set(map(tuple,a['periodos_sin_marca_reconocimiento']))&set(map(tuple,b['periodos_sin_marca_reconocimiento'])) if same else set()
  state='ANIOS_DISJUNTOS' if not ya&yb else 'PERIODOS_SOLAPADOS' if both else 'MISMO_ANIO_PERIODOS_DISTINTOS' if same else 'REGIMENES_NO_COMPARABLES'
  pairs.append({'persona':person,'familia':fam,'expediente_a':[a['CODCLI'],a['carrera'],a['plan']],'expediente_b':[b['CODCLI'],b['carrera'],b['plan']],
   'estado':state,'anios_comunes':sorted(ya&yb),'periodos_comunes':sorted(both),'periodos_comunes_sin_reconocimiento':sorted(bothdirect),
   'limite':'Secuencia/solapamiento observado; no acto ni fecha efectiva de migración'})
 yearly={y:sorted({m['codigo'] for m in muindex[person,fam,y]}) for y in sorted({m['ano'] for m in mu if m['persona']==person and m['familia']==fam})}
 codes={c for v in yearly.values() for c in v}
 multi=any(len(v)>1 for v in yearly.values())
 rstate='VARIAS_VERSIONES_MISMO_ANIO' if multi else 'CAMBIO_CODIGO_ENTRE_ANIOS_OBSERVADOS' if len(codes)>1 else 'UN_CODIGO_EN_ANIOS_OBSERVADOS' if codes else 'SIN_CODIGO_MU_LOCALIZADO'
 relationrows.append({'persona':person,'familia':fam,'expedientes_planes':len(segs),'codigos_por_ano':yearly,'estado_versiones':rstate,'codigos':sorted(codes)})
# Date match is explicitly diagnostic. Matching a renewal date does not prove plan inception.
newobs=[];date_tests=Counter();dated_proposals=[]
for x in obs:
 fams=families_evid.get((x['carrera'],rev.get(x['jornada_sies'])),[]);foc=[f for f in fams if (x['persona'],f) in relations]
 evidence=[m for f in fams for m in muindex[x['persona'],f,x['ano']]];codes=sorted({m['codigo'] for m in evidence})
 assert codes==x['codigos_anuales_documentados']
 ds=[d for d in dindex[x['persona'],x['CODCLI'],x['carrera']] if d['SEDE']=='RE' and jmap.get(d['JORNADA'])==x['jornada_sies']]
 matches=[]
 for m in evidence:
  if not m['fecha_matricula_iso']:continue
  for d in ds:
   if d['fecha_matricula_iso']==m['fecha_matricula_iso']:
    peers={ (dd['CODCLI'],dd['CODCARPR']) for dd in da if dd['persona']==x['persona'] and dd['SEDE']=='RE' and jmap.get(dd['JORNADA'])==x['jornada_sies'] and m['familia'] in families_evid.get((dd['CODCARPR'],dd['JORNADA']),[]) and dd['fecha_matricula_iso']==m['fecha_matricula_iso']}
    matches.append({'codigo':m['codigo'],'fecha':m['fecha_matricula_iso'],'expedientes_con_misma_fecha':len(peers),'MU':[m['archivo'],m['hoja'],m['fila']],'DA':[d['archivo'],d['hoja'],d['fila']]})
 unique=sorted({m['codigo'] for m in matches if m['expedientes_con_misma_fecha']==1})
 if unique:
  if x['codigo_documental_atribuible']:date_tests['COINCIDE_DOCUMENTADO' if unique==[x['codigo_documental_atribuible']] else 'DIFIERE_DOCUMENTADO']+=1
  else:date_tests['CANDIDATO_SIN_ATRIBUCION_PREVIA']+=1;dated_proposals.append(x['observacion_id'])
 cat='DOCUMENTADO_ANUAL_ATRIBUIBLE' if x['codigo_documental_atribuible'] else 'EQUIVALENCIA_INTERNA_VIGENTE' if x['codigo_interno_adoptado'] else 'CODIGO_ANUAL_UNICO_ATRIBUCION_PENDIENTE' if len(codes)==1 else 'VARIOS_CODIGOS_ANUALES' if len(codes)>1 else 'SIN_CODIGO_ANUAL'
 xx={k:x[k] for k in ['observacion_id','persona','CODCLI','carrera','sede_dimension','jornada_sies','plan','ano','periodo','codigo_documental_atribuible','codigo_interno_adoptado','codigo_propuesto','estado_documental','estado_interno']}
 xx.update(en_relaciones_multiples=bool(foc),familias=fams,codigos_anuales=codes,estado_revision=cat,evidencias_MU=evidence,contextos_DA=ds,
   coincidencias_fecha=matches,candidatos_por_fecha_exclusiva=unique,codigo_nuevo_adoptado='',
   alcance='Código documentado al nivel anual; no acredita versión asignada en cada período UMAS ni fecha efectiva del plan',
   fecha_efectiva_plan='PENDIENTE',fuentes_promedios=x['fuentes_promedios'],clasificacion='B/C; D si equivalencia vigente; E fecha efectiva')
 newobs.append(xx)
change_da=[]
for key,ds in dindex.items():
 for field in ['ANOINGRESO','PERIODOINGRESO','FECHAMATRICULA','ANOMATRICULA','PERIODOMATRICULA']:
  vals={x[field] for x in ds if x[field]}
  if len(vals)>1:change_da.append({'persona':key[0],'CODCLI':key[1],'carrera':key[2],'campo':field,'valores':sorted(vals),'localizadores':[[x['archivo'],x['hoja'],x['fila'],x[field]] for x in ds],'clasificacion':'B diferencia entre reportes; E orden temporal no acreditado'})
print('Fase 3/4 · Hito 3/3 — Códigos anuales separados de hipótesis temporales; escribir resultados',flush=True)
for name,data in [('OBSERVACIONES_REVISADAS',newobs),('SEGMENTOS_EXPEDIENTE_PLAN',segments),('RELACIONES_PERSONA_FAMILIA',relationrows),('PARES_TRAYECTORIA',pairs),('COMPARACION_PROMEDIOS',comparisons),('DIFERENCIAS_FECHAS_DA',change_da)]:
 dump(P/(name+'.json'),data);outcsv(P/(name+'.csv'),data)
summary={'universo':{'personas':len(people),'relaciones_persona_familia':len(relations),'observaciones_personas_foco':len(obs),'observaciones_en_relaciones_multiples':sum(x['en_relaciones_multiples'] for x in newobs),
 'expedientes_planes_relaciones':len(segments),'pares_expedientes_planes':len(pairs)},
 'versiones_por_relacion':dict(Counter(x['estado_versiones'] for x in relationrows)),
 'patrones_pares':dict(Counter(x['estado'] for x in pairs)),
 'pares_solapados_sin_reconocimiento':sum(bool(x['periodos_comunes_sin_reconocimiento']) for x in pairs),
 'observaciones_por_estado':dict(Counter(x['estado_revision'] for x in newobs)),
 'comparacion_promedios':{'unidades_comparables':len(comparisons),'estados':dict(Counter(x['estado'] for x in comparisons)),'personas_con_plan_distinto':len({x['persona'] for x in comparisons if x['estado']!='IGUAL'})},
 'fechas_DA':{'diferencias_por_campo':dict(Counter(x['campo'] for x in change_da)),'personas_con_diferencia':len({x['persona'] for x in change_da})},
 'fechas_MU':{'filas_foco':len(mu),'fecha_interpretable':sum(bool(x['fecha_matricula_iso']) for x in mu),'fecha_no_vacia_no_interpretable':sum(bool(x['fecha_matricula_original']) and not x['fecha_matricula_iso'] for x in mu)},
 'coincidencias_fecha_exclusiva':dict(date_tests),'propuestas_fecha_observacion_ids_privadas':len(dated_proposals),
 'nuevos_codigos_adoptados':sum(bool(x['codigo_nuevo_adoptado']) for x in newobs),
 'clasificacion':'B/C resultados; E migración e intervalo efectivo; D reglas vigentes preservadas'}
agg=[]
for fam in sorted({x['familia'] for x in relationrows}):
 xs=[x for x in relationrows if x['familia']==fam];ps=[x for x in pairs if x['familia']==fam]
 agg.append({'familia':fam,'personas_en_familia':len(xs),**dict(Counter(x['estado_versiones'] for x in xs)),**dict(Counter(x['estado'] for x in ps)),'clasificacion':'B/C; E causalidad'})
outcsv(O/'RESUMEN_POR_FAMILIA.csv',agg);dump(O/'RESULTADOS.json',summary);outcsv(O/'INVENTARIO_FUENTES.csv',INV)
assert len({x['observacion_id'] for x in newobs})==len(obs)
assert all(sha(p)==h for p,h in HASH.items())
aftergit=git();assert all(aftergit[p]['head']==b['head'] and aftergit[p]['rama']==b['rama'] for p,b in beforegit.items());dump(O/'GIT_DESPUES.json',aftergit)
dump(O/'FUENTES_HASHES.json',HASH)
dump(O/'MANIFEST.json',{'fecha':stamp,'privado':str(P),'fuentes':HASH,'script':str(Path(__file__)),'script_sha256':sha(__file__),'universo':summary['universo'],'canon_modificado':False,'denominadores_modificados':False,'commit':False,'push':False,
 'salidas_privadas_hashes':{p.name:sha(p) for p in P.iterdir() if p.is_file()},'QA':'OK_CON_PENDIENTES_TEMPORALES'})
print(json.dumps({'output':str(O),'privado':str(P),'resultados':summary},ensure_ascii=False),flush=True)
