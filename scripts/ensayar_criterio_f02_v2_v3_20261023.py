"""Ensayo agregado y privado, sin adoptar versiones ni modificar bases."""
import copy,csv,datetime,hashlib,json,os,re,subprocess
from collections import Counter,defaultdict
from pathlib import Path
from zoneinfo import ZoneInfo
import openpyxl
R=Path(__file__).resolve().parents[1];P=Path.home()/'.local/share/ipss'
now=datetime.datetime.now(ZoneInfo('America/Santiago'));stamp=now.strftime('%Y%m%d_%H%M%S')
O=R/'outputs'/('escenario_criterio_f02_v2_v3_'+stamp);Q=P/('escenario_criterio_f02_v2_v3_'+stamp)
assert subprocess.run(['git','-C',str(P),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
os.umask(0o077);O.mkdir();Q.mkdir();H={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def src(p,h=None):
 p=Path(p);actual=sha(p);assert h is None or actual==h,str(p);H[str(p)]=actual;return p
def load(p,h=None):return json.loads(src(p,h).read_text())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
def val(v):return '' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip()
def norm(n,d):
 n=val(n).replace('.','').strip();d=val(d).upper();return str(int(n))+'-'+d if n.isdigit() and len(d)==1 and d in '0123456789K' else ''
def git():return {k:subprocess.check_output(['git','-C',str(R),*a],text=True).strip() for k,a in [('rama',['branch','--show-current']),('HEAD',['rev-parse','HEAD']),('status',['status','--short'])]}
gb=git();dump(O/'GIT_ANTES.json',gb)
bm=load(R/'outputs/reproduccion_puente_20261023_004044/MANIFEST.json');bp=Path(bm['privado'])
obs=load(bp/'OBSERVACIONES_PRIVADAS.json',bm['salidas_privadas_hashes']['OBSERVACIONES_PRIVADAS.json'])
cm=load(R/'outputs/cierre_f02_iinf_aprobado_20261023_085725/MANIFEST.json');cp=Path(cm['privado'])
overlay=load(cp/'ADJUDICACIONES_ACUMULADAS_F02.json',cm['privados_hashes']['ADJUDICACIONES_ACUMULADAS_F02.json'])
idx={x['observacion_id']:x for x in obs}
for x in overlay['adjudicaciones']:
 assert idx[x['observacion_id']]==x['estado_antes'];idx[x['observacion_id']]=copy.deepcopy(x['estado_despues'])
obs=list(idx.values());baseline=copy.deepcopy(obs)
pending=[x for x in obs if not x['codigo_interno_adoptado']]
assert len(pending)==3090 and len({x['persona'] for x in pending})==1750
people={x['persona'] for x in obs}
dim=load(R/'data/reglas_negocio/20261022_puente_versiones/investigacion_contextual_v3/PRUEBAS_CONTEXTUALES.json')
families={(x['carrera'],x['jornada']):x['familias'] for x in dim}
ante=load(bp/'reanudacion/antecedentes_minimos.json')
ev=next(x['rows'] for x in ante if x['name']=='EVIDENCIAS_SIES')
sources=sorted({(x[8],x[9]) for x in ev if x[1]=='MATRICULA' and ('BASE_RETENCION_MATRICULA' in x[8] or re.search(r'MAT_IP_CIISA_(2018|2019|2020|2021)\.xlsx$',x[8]))})
mu=[];mi=defaultdict(set);ml=defaultdict(list);inventory=[]
for path,sheet in sources:
 assert path in bm['fuentes_hashes'],'Falta hash gobernado '+path
 src(path,bm['fuentes_hashes'][path]);w=openpyxl.load_workbook(path,read_only=True,data_only=True);it=iter(w[sheet].values);headers=next(it);n=0
 for rn,row in enumerate(it,2):
  n+=1;d=dict(zip(headers,row));old='MC_CODIGO_UNICO' in d
  person=norm(d.get('MM_N_DOCUMENTO') if old else d.get('N_DOC'),d.get('MM_DV') if old else d.get('DV'))
  if person not in people:continue
  code=val(d.get('MC_CODIGO_UNICO')) if old else 'I162S%sC%sJ%sV%s'%tuple(val(d.get(k)) for k in ['COD_SED','COD_CAR','JOR','VERSION'])
  if not re.fullmatch(r'I162S\d+C\d+J\d+V\d+',code):continue
  year=val(d.get('MC_CAT_PERIODO') if old else d.get('ANIO_INFORMADO')).replace('MAT_','');family=code.rsplit('V',1)[0]
  z={'persona':person,'ano':year,'codigo':code,'familia':family,'fuente':path,'hoja':sheet,'fila':rn}
  mu.append(z);mi[person,year,family].add(code);ml[person,year,family].append(z)
 w.close();inventory.append({'fuente':path,'hoja':sheet,'filas_leidas':n,'sha256':H[path]})
 print('MU leída:',Path(path).name,flush=True)
dump(Q/'EVIDENCIAS_MU.json',mu)
def predict(person,year,family):
 a=mi[person,str(int(year)-1),family];b=mi[person,str(int(year)+1),family]
 return next(iter(a)) if len(a)==len(b)==1 and a==b else ''
tests=[];units=defaultdict(set)
for x in obs:
 c=x['codigo_documental_atribuible']
 if c:units[x['persona'],x['ano'],c.rsplit('V',1)[0]].add(c)
for (person,year,family),truth in sorted(units.items()):
 pred=predict(person,year,family)
 state='ABSTENCION' if not pred else 'OTRA_VERSION' if not pred.endswith(('V2','V3')) else 'COINCIDE' if truth=={pred} else 'DIFIERE'
 tests.append({'persona':person,'ano':year,'familia':family,'prediccion_sin_ano_objetivo':pred,'objetivo_documental':sorted(truth),'estado':state})
dump(Q/'RETROSPECTIVA.json',tests)
records=[];candidates=[]
for x in pending:
 fs=families.get((x['carrera'],x['jornada_sies']),[]);y=x['ano'];family=fs[0] if len(fs)==1 else '';pred=predict(x['persona'],y,family) if family else ''
 state='FAMILIA_NO_UNICA' if not family else 'EXTREMOS_NO_CONCORDANTES' if not pred else 'OTRA_VERSION' if not pred.endswith(('V2','V3')) else 'ANIO_OBJETIVO_NO_CORROBORA' if mi[x['persona'],y,family]!={pred} else 'SIN_CONTEXTO_DA' if not x['contextos_DA'] else 'PRESELECCION'
 z={'observacion':x,'familia':family,'codigo_candidato':pred,'estado':state,'codigo_adoptado':''}
 if state=='PRESELECCION':
  z['evidencias_anuales']=[e for yy in [str(int(y)-1),y,str(int(y)+1)] for e in ml[x['persona'],yy,family]];candidates.append(z)
 records.append(z)
# Relectura exacta de filas fuente de actividad; no vinculación por nombres.
requests=defaultdict(list)
for z in candidates:
 x=z['observacion']
 for e in x['fuentes_promedios']:requests[e['fuente'],e['hoja']].append((e['fila'],z,e))
for (path,sheet),req in requests.items():
 src(path,bm['fuentes_hashes'][path]);lookup=defaultdict(list)
 for rn,z,e in req:lookup[int(rn)].append((z,e))
 w=openpyxl.load_workbook(path,read_only=True,data_only=True);it=iter(w[sheet].values);head=next(it);found=set()
 for rn,row in enumerate(it,2):
  if rn not in lookup:continue
  d=dict(zip(head,row));found.add(rn)
  for z,e in lookup[rn]:
   x=z['observacion'];assert norm(d.get('RUT'),d.get('DIG'))==x['persona']
   assert all(val(d.get(k))==v for k,v in [('CODCLI',x['CODCLI']),('CODCARR',x['carrera']),('PLAN_DE_ESTUDIO',x['plan']),('ANO',x['ano']),('PERIODO',x['periodo'])])
   assert {'D':'1','V':'2','O':'4'}[val(d['JORNADA'])]==x['jornada_sies']
   status=val(d.get('DESCRIPCION_ESTADO'));recognized=val(d.get('CONVALIDADO')).upper()=='S' or any(s in status.upper() for s in ['HOMOLOG','CONVALID'])
   z.setdefault('actividad_releida',[]).append({'fuente':path,'hoja':sheet,'fila':rn,'regimen':val(d.get('REGIMEN')),'asignatura':val(d.get('CODRAMO')),'estado':status,'reconocimiento':recognized,'nota':val(d.get('NOTA_FINAL'))})
 w.close();assert found==set(lookup)
for z in candidates:
 rows=z['actividad_releida'];z['estado']='CANDIDATO_INTERNO_CON_ACTIVIDAD' if any(not r['reconocimiento'] for r in rows) else 'CONDICIONADO_SOLO_RECONOCIMIENTO'
 # DA debe corresponder al expediente; no exige que la fecha exacta sea del período.
 x=z['observacion'];assert all(d['CODCLI']==x['CODCLI'] and d['CODCARPR']==x['carrera'] and {'D':'1','V':'2','O':'4'}[d['JORNADA']]==x['jornada_sies'] and d['SEDE']=='RE' for d in x['contextos_DA'])
master=load(R/'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json')
for z in candidates:
 z['oferta_anio']=[d for d in master['oferta_anual'] if d['codigo_unico']==z['codigo_candidato'] and str(d['anio'])==z['observacion']['ano']]
 if not z['oferta_anio']:z['estado']='PENDIENTE_OFERTA_ANUAL'
def scenario(selected):
 ids={z['observacion']['observacion_id'] for z in selected};ps={z['observacion']['persona'] for z in selected};left=[x for x in pending if x['observacion_id'] not in ids];lp={x['persona'] for x in left}
 return {'observaciones_candidatas':len(ids),'personas_afectadas':len(ps),'personas_cierre_completo':len(ps-lp),'personas_cierre_parcial':len(ps&lp),'pendientes_observaciones_simuladas':len(left),'pendientes_personas_simuladas':len(lp),'aplicado':False}
strong=[z for z in candidates if z['estado']=='CANDIDATO_INTERNO_CON_ACTIVIDAD'];conditional=[z for z in candidates if z['estado']=='CONDICIONADO_SOLO_RECONOCIMIENTO']
summary={'clasificacion':'B fuentes; C ensayo; E candidatos no aprobados','base_actual':{'observaciones_pendientes':3090,'personas_pendientes':1750},'embudo_observaciones':dict(Counter(z['estado'] for z in records)),
 'escenario_actividad':scenario(strong),'escenario_incluyendo_condicionadas':scenario(strong+conditional),'versiones_candidatas':dict(Counter(z['codigo_candidato'].rsplit('V',1)[1] for z in candidates)),
 'retrospectiva':{'unidades_persona_ano_familia':len(tests),'personas_distintas':len({x['persona'] for x in tests}),'resultados':dict(Counter(x['estado'] for x in tests)),'familias_con_diferencias':dict(Counter(x['familia'] for x in tests if x['estado']=='DIFIERE'))},
 'cobertura_mu':sorted({x['ano'] for x in mu}),'limite':'Sin MU2027 disponible en las entradas; no extrapolar pendientes 2026. Concordancia anual no es atribución documental por período.'}
summary['tabla_candidatos']=[{'carrera':z['observacion']['carrera'],'plan':z['observacion']['plan'],'ano':z['observacion']['ano'],'periodo':z['observacion']['periodo'],'regimen':sorted({a['regimen'] for a in z['actividad_releida']}),'codigo_candidato':z['codigo_candidato'],'estado':z['estado'],'filas_actividad':len(z['actividad_releida']),'filas_solo_reconocimiento':sum(a['reconocimiento'] for a in z['actividad_releida']),'nombre_oferta':sorted({a['nombre_carrera'] for a in z['oferta_anio']}),'clasificacion':'B/C; E adopción pendiente'} for z in candidates]
summary['validacion_familias_candidatas']={f:dict(Counter(t['estado'] for t in tests if t['familia']==f)) for f in {z['familia'] for z in candidates}}
dump(Q/'EVALUACION_TODOS_PENDIENTES.json',records);dump(Q/'CANDIDATOS_REVISADOS.json',candidates)
dump(O/'RESULTADOS.json',summary);dump(O/'INVENTARIO_MU.json',inventory)
source_code=src(__file__);src(R/'docs/ESPECIFICACION_ESCENARIO_CRITERIO_F02_V2_V3_20261023.md')
qa={'estado':'OK_CON_ADVERTENCIAS','sin_adopcion':obs==baseline,'todas_pendientes_evaluadas':len(records)==3090,'particion_embudo':sum(summary['embudo_observaciones'].values())==3090,'lectura_exacta_periodos':all(z.get('actividad_releida') for z in candidates),'F02_excluido_de_nuevos_candidatos':not any(z['observacion']['persona']==overlay['adjudicaciones'][0]['persona'] for z in candidates),'fuentes_intactas':all(sha(p)==h for p,h in H.items()),'privado_fuera_git':True,'advertencia':'Ensayo no aplicado; reconocimiento sin cursado separado; una discrepancia retrospectiva impide automatización universal.'}
assert all(v for v in qa.values() if isinstance(v,bool));dump(O/'QA.json',qa);dump(O/'FUENTES_HASHES.json',H)
ga=git();assert gb['rama']==ga['rama'] and gb['HEAD']==ga['HEAD'];dump(O/'GIT_DESPUES.json',ga)
dump(O/'MANIFEST.json',{'fecha_hora':now.isoformat(),'privado':str(Q),'fuentes_hashes':H,'salidas_hashes':{p.name:sha(p) for p in O.iterdir()},'privados_hashes':{p.name:sha(p) for p in Q.iterdir()},'resultado':summary,'qa':qa,'aplicado':False,'commit_push':False})
print(json.dumps({'salida':str(O),'resultado':summary},ensure_ascii=False))
