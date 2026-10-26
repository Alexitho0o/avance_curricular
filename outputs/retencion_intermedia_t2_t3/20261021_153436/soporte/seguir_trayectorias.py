"""Exact longitudinal observations; all individual work stays in ignored private storage."""
from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib,datetime,contextlib,io,ast,subprocess,os,re,zipfile
import openpyxl
from lxml import etree as E
R=Path('/Users/alexi/Documents/GitHub/avance_curricular');O=R/'outputs/retencion_intermedia_t2_t3/20261021_153436';P=R/'.local_restricted/retencion_intermedia/20261021_153436'
T=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/0 BASES DE DATOS/RETENCION/RETENCION_IPSS_FINAL_REVISADO_20261005.xlsx')
os.umask(0o077)
assert subprocess.run(['git','check-ignore','-q',str(P/'datos.json')],cwd=R).returncode==0
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(T)=='5b64030011ad64f742a95ad72a91cc326ad918afaea46ea989496d2e8c44f899'
prior=json.loads((R/'.local_restricted/retencion_intermedia/20261021_144031/payload.json').read_text())
prof=R/'outputs/retencion_intermedia_t2_t3/20261020_215248/profile.py';g={'__file__':str(prof)}
with contextlib.redirect_stdout(io.StringIO()):exec(compile(prof.read_text().split('specs=',1)[0],str(prof),'exec'),g)
txt,key=g['txt'],g['key'];base=[b for b in g['base'] if b['engine']['ESTADO_FINAL']=='INCLUIDO']
assert Counter(b['raw']['ANIO_INFORMADO'] for b in base)=={2024:558,2025:1150}
pid={b['raw']['_row']:f"C{b['raw']['ANIO_INFORMADO']}_{i+1:04d}" for i,b in enumerate(base)}
byid={pid[b['raw']['_row']]:b for b in base};ids=defaultdict(set);cli=defaultdict(set);pending=set();foreign={}
for b in base:
 pp=pid[b['raw']['_row']]
 if b['key']:ids[b['key']].add(pp)
 else:foreign[txt(b['raw']['N_DOC'])]=pp
for rr in prior['identity']:
 pp=rr[0];assert pp in byid
 kk=key(rr[5])
 if kk:ids[kk].add(pp)
 for c in rr[7:9]:
  if c and c!='Pendiente':cli[c].add(pp)
 if rr[10]=='Pendiente':pending.add(pp)
assert len(pending)==2
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
KEEP={'RUT','CODCLI','CODCARPR','CODIGOCARRERA','NOMBRE_L','ANOMATRICULA','PERIODOMATRICULA','ANOINGRESO','PERIODOINGRESO','ESTADOACADEMICO','SITUACION','SEDE','JORNADA','NIVEL','FECHAMATRICULA','FECH_CAR','FECHATITULO','FECHA_TITULACION','FECHAEGRESO','FECHA_EGRESO','N_DOC','DV','TIPO_DOC'}
def literal(v):
 if v is None:return ''
 if isinstance(v,float) and v.is_integer():return str(int(v))
 return str(v)
def canon(v):return txt(v).replace('.','').replace(' ','')
tree=ast.parse((R/'outputs/retencion_intermedia_t2_t3/20261021_144031/soporte/preparar_detalle.py').read_text())
fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='read_xlsx')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'lector_congelado','exec'))
sources=[];obs={};seen=[];conflicts=[]
def src(path,sheet,h,context):
 path=Path(path);assert sha(path)==h,('hash',path.name)
 sid='F'+str(len(sources)+1).zfill(3)
 sources.append({'id':sid,'path':str(path),'sheet':sheet,'sha256':h,'context':context,'bytes':path.stat().st_size})
 return sid
def ingest(sid,rows,nominal=''):
 matched=set()
 for rr in rows:
  kk=key(rr.get('RUT'));people=ids.get(kk,set())|cli.get(txt(rr.get('CODCLI')),set())
  if not people:continue
  # Different cohorts can share an identity; reject a conflicting identifier, never pick a name match.
  identities={(literal(byid[pp]['raw']['TIPO_DOC']),literal(byid[pp]['raw']['N_DOC']),literal(byid[pp]['raw']['DV'])) for pp in people}
  if len(identities)>1:conflicts.append({'source':sid,'row':rr['_row'],'people':len(people)});continue
  cc=txt(rr.get('CODCLI'))
  if cc:cli[cc]|=people
  if kk:ids[kk]|=people
  try:y=int(float(rr.get('ANOMATRICULA','')));term=int(float(rr.get('PERIODOMATRICULA','')))
  except (ValueError,TypeError):continue
  if y not in (2024,2025,2026) or term not in (1,2,3):continue
  for pp in people:
   b=byid[pp];cohort=b['raw']['ANIO_INFORMADO']
   if y<cohort:continue
   # Keep states as observed at extraction, independently of matriculation year/period.
   fields=(pp,y,term,literal(rr.get('RUT')),cc,literal(rr.get('CODCARPR',rr.get('CODIGOCARRERA'))),literal(rr.get('NOMBRE_L')),literal(rr.get('ESTADOACADEMICO')) or 'Sin campo',literal(rr.get('SITUACION')),literal(rr.get('FECHAMATRICULA')),literal(rr.get('NIVEL')),literal(rr.get('SEDE')),literal(rr.get('JORNADA')),literal(rr.get('FECH_CAR')),literal(rr.get('FECHATITULO',rr.get('FECHA_TITULACION'))),literal(rr.get('FECHAEGRESO',rr.get('FECHA_EGRESO'))))
   if fields not in obs:obs[fields]=[]
   obs[fields].append({'source':sid,'sheet':rr['_sheet'],'row':rr['_row'],'nominal':nominal});matched.add(pp)
 return len(matched)
inv=json.loads((R/'outputs/retencion_intermedia_t2_t3/20261021_133221/REVISION_LLAVES.json').read_text())
main=[s for label in ['10246','11998','12112'] for s in inv['fuentes_base'] if Path(s['ruta']).name==f'DATOSDEALUMNOS_{label}.xlsx']
more=[s for s in inv['fuentes_adicionales'] if s['hojas']]
files=[]
for s in main:
 files.append((s['ruta'],['Hoja1'],s['sha256'],'Respaldo UMAS; estado efectivo de cierre no acreditado',''))
for s in more:
 nominal=s['contexto'].replace('Base Maestra corte nominal ','') if s['contexto'].startswith('Base Maestra') else ''
 files.append((s['ruta'],None,s['sha256'],s['contexto'],nominal))
for sp in json.loads((R/'outputs/retencion_intermedia_t2_t3/20261021_133221/CONTEOS_REPRODUCIDOS.json').read_text())['closures']:
 pp=Path(sp['source']);h=next(s['sha256_before'] for s in json.loads((R/'outputs/retencion_intermedia_t2_t3/20261021_133221/CONTEOS_REPRODUCIDOS.json').read_text())['sources'] if s['path']==str(pp))
 files.append((str(pp),[sp['sheet']],h,'Listado parcial '+sp['closure'],''))
# Initial exact-document pass also recovers multiple CODCLI for the entire approved cohorts.
for n,(path,sheets,h,context,nominal) in enumerate(files):
 sid=src(path,' / '.join(sheets) if sheets else 'Hojas con RUT+CODCLI',h,context)
 rr,meta=read_xlsx(path,sheets,lambda r:bool(ids.get(key(r.get('RUT')))) or bool(cli.get(txt(r.get('CODCLI')))),True)
 ingest(sid,rr,nominal);seen.append((sid,path,sheets,nominal))
 if n%12==0:print('Fuentes de trayectoria verificadas',n+1,flush=True)
assert not conflicts,'Llave individual contradictoria; detener antes de producir resultados'
# Complete the pass for changed document/CODCLI links discovered later, without retaining duplicate support references.
for sid,path,sheets,nominal in seen:
 rr,_=read_xlsx(path,sheets,lambda r:bool(ids.get(key(r.get('RUT')))) or bool(cli.get(txt(r.get('CODCLI')))),True)
 ingest(sid,rr,nominal)
for k,ss in obs.items():obs[k]=list({(x['source'],x['sheet'],x['row']):x for x in ss}.values())
for path,sheet,h,ctx in [(g['rawpath'],'BASE_RETENCION_MU','19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd','Matrícula anual informada a SIES; no se transforma en cierre T2/T3'),(g['engpath'],'02_COHORTE_ELEGIBILIDAD / 01_CATALOGO_CARRERA','5f0f7c7f0f238556de374d287bf2931ccc8a93a5489f4c2f2b543befd38c77b3','Selección anual congelada')]:src(path,sheet,h,ctx)
tw=openpyxl.load_workbook(T,data_only=True,read_only=True)
sector={str(code):(name,sec) for name,sec,code in tw['8_Mapeo_Sector_IPSS'].iter_rows(min_row=6,max_row=22,min_col=2,max_col=4,values_only=True)};tw.close()
by_person=defaultdict(list)
for fields,support in obs.items():by_person[fields[0]].append((fields,support))
rawindex=defaultdict(list)
for rr in g['raw']:rawindex[(rr['TIPO_DOC'],rr['N_DOC'],rr['DV'])].append(rr)
grouped={};persons=[];timeline=Counter();latest=Counter();annualcontrols=Counter();observedout=[]
for fields,support in obs.items():
 observedout.append(list(fields)+['; '.join(f"{s['source']}!{s['sheet']}:{s['row']}" for s in support),' / '.join(sorted({s['nominal'] for s in support if s['nominal']})),len(support),'B/C; estado de extracción, no fecha de cierre E'])
for pp,b in byid.items():
 rr=b['raw'];y=rr['ANIO_INFORMADO'];code=str(rr['COD_CAR']);career,sec=sector[code]
 birth=literal(rr.get('FECH_NAC'));byear=None
 for fmt in ['%d/%m/%Y','%Y-%m-%d','%d-%m-%Y']:
  try:byear=datetime.datetime.strptime(birth[:10],fmt).year;break
  except ValueError:pass
 age=y-byear if byear is not None else None
 band='SIN DATO' if age is None else 'Menos de 20' if age<20 else '20-24' if age<25 else '25-29' if age<30 else '30-39' if age<40 else '40+'
 mod,jor=literal(rr['MODALIDAD']),literal(rr['JOR']);jornada={'1':'Presencial-Diurno','2':'Presencial-Vespertino','4':'Virtual'}.get(jor,'No mapeado')
 matches=by_person[pp];periods={(f[1],f[2]) for f,ss in matches};nextyear=y+1
 t2=int((nextyear,2) in periods);t3=int((nextyear,3) in periods)
 v2=int(any(f[1]==nextyear and f[2]==2 and f[7]=='VIGENTE' for f,ss in matches));v3=int(any(f[1]==nextyear and f[2]==3 and f[7]=='VIGENTE' for f,ss in matches))
 ann=int(b['engine']['SIGUIENTE_MISMA_COHORTE']>0)
 annualcontrols[y]+=ann
 last=max(periods) if periods else None
 lastlabel=f'{last[0]}-T{last[1]}' if last else 'Sin período UMAS localizado'
 states=' / '.join(sorted({f[7] for f,ss in matches if last and (f[1],f[2])==last}))
 timeline[(y,'T2')]+=t2;timeline[(y,'T3')]+=t3;latest[(y,lastlabel)]+=1
 # Aggregate by dimensions only, never by identity; counts support SUMIFS rather than row counts.
 dims=(y,b['engine']['CODIGO_UNICO'],career,b['engine']['AREA_DEL_CONOCIMIENTO'],sec,literal(rr['SEXO']),mod,jor,jornada,band,code,literal(rr['COD_SED']),literal(rr['VERSION']))
 if dims not in grouped:grouped[dims]=[0]*10
 acc=grouped[dims];acc[0]+=1;acc[1]+=ann;acc[2]+=t2;acc[3]+=t3;acc[4]+=v2;acc[5]+=v3
 acc[6]+=int(pp in pending);acc[7]+=int(last is not None);acc[8]+=int('TITULADO' in states);acc[9]+=int('EGRESADO' in states)
 p_cids=sorted(c for c,owners in cli.items() if pp in owners)
 presence=[int((yy,tt) in periods) for yy,tt in [(2024,1),(2024,2),(2024,3),(2025,1),(2025,2),(2025,3),(2026,1),(2026,2),(2026,3)]]
 persons.append([pp,y,literal(rr['TIPO_DOC']),literal(rr['N_DOC']),literal(rr['DV']),' / '.join(p_cids) if p_cids else 'Pendiente',career,b['engine']['CODIGO_UNICO'],sec,rr['SEM_ING_ORI'],ann,t2,t3,v2,v3,lastlabel,states,len(matches),int(pp in pending),*presence,'B/C; última matrícula observada, no avance curricular acreditado'])
assert annualcontrols=={2024:326,2025:668},annualcontrols
assert sum(x[0] for x in grouped.values())==1708
assert sum(int(bool([p for p in cli.values() if pp in p])) for pp in pending)==0
agg=[list(k)+v for k,v in sorted(grouped.items())]
public={'created':datetime.datetime.now().astimezone().isoformat(),'template':str(T),'template_sha256':sha(T),'groups':agg,'sources':sources,'control':{str(y):{'denominator':sum(p[1]==y for p in persons),'T1':annualcontrols[y],'T2_records_observed':timeline[(y,'T2')],'T3_records_observed':timeline[(y,'T3')]} for y in [2024,2025]},'last_period_counts':[{'cohort':y,'last_period':lab,'people':n,'class':'B/C; límite de fuentes'} for (y,lab),n in sorted(latest.items())],'observations_unique':len(observedout),'identifiers_public':False,'metric_definition':'C: T2/T3 = personas con matrícula de ese año y período en fuentes verificadas / cohorte fija. NO acredita estado efectivo al cierre ni tasa oficial; formal permanece E. T1 conserva motor anual C.','no_commit_push':True}
(O/'MODELO_AGREGADO.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n')
(P/'datos.json').write_text(json.dumps({'persons':persons,'observations':observedout,'sources':sources,'control':public['control'],'last_period_counts':public['last_period_counts'],'created':public['created']},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:public[k] for k in ['control','observations_unique','last_period_counts']},ensure_ascii=False,indent=2))
