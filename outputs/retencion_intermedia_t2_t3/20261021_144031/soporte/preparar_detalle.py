"""Read-only exact joins. Personal payload is written ONLY to verified ignored private storage."""
from pathlib import Path
from collections import defaultdict, Counter
import contextlib, io, json, hashlib, datetime, subprocess, zipfile, re, os
from lxml import etree as E

R=Path('/Users/alexi/Documents/GitHub/avance_curricular')
O=R/'outputs/retencion_intermedia_t2_t3/20261021_144031'
P=R/'.local_restricted/retencion_intermedia/20261021_144031'
OLD=R/'outputs/retencion_intermedia_t2_t3/20261021_133221'
os.umask(0o077)
for name in ['payload.json','DETALLE_PRIVADO_RETENCION_INTERMEDIA_20261021_144031.xlsx']:
 assert subprocess.run(['git','check-ignore','-q',str(P/name)],cwd=R).returncode==0
assert not subprocess.check_output(['git','ls-files',str(P)],cwd=R,text=True).strip()
assert (P.stat().st_mode & 0o777)==0o700
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prior=json.loads((OLD/'REVISION_LLAVES.json').read_text())
sources=[]
def source(p,sheet,expected=None,context=''):
 p=Path(p);h=sha(p)
 if expected:assert h==expected,('hash_discrepante',p.name)
 existing=next((s for s in sources if s['path']==str(p) and s['sheet']==sheet),None)
 if existing:return existing['id']
 sid='F'+str(len(sources)+1).zfill(3)
 sources.append(dict(id=sid,path=str(p),sheet=sheet,sha256=h,bytes=p.stat().st_size,context=context,clasificacion='B/C',mtime=datetime.datetime.fromtimestamp(p.stat().st_mtime).astimezone().isoformat()))
 return sid
script=R/'outputs/retencion_intermedia_t2_t3/20261020_215248/profile.py'
assert sha(script)=='39b64cfea7773f269a10ba9576f1945f79e35e0f69a681913a173a2b279c0d88'
g={'__file__':str(script)}
with contextlib.redirect_stdout(io.StringIO()):exec(compile(script.read_text().split('specs=',1)[0],str(script),'exec'),g)
txt,key=g['txt'],g['key']
def literal(v):
 if v is None:return ''
 if isinstance(v,float) and v.is_integer():return str(int(v))
 return str(v)
def canon(v):return txt(v).replace('.','').replace(' ','')
raw,base=g['raw'],g['base']
inc=[b for b in base if b['engine']['ESTADO_FINAL']=='INCLUIDO']
assert Counter(b['raw']['ANIO_INFORMADO'] for b in inc)=={2024:558,2025:1150}
rawsid=source(g['rawpath'],'BASE_RETENCION_MU','19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd','Base anual institucional; selección elegible histórica sin alterar motor')
source(g['engpath'],'02_COHORTE_ELEGIBILIDAD / 01_CATALOGO_CARRERA','5f0f7c7f0f238556de374d287bf2931ccc8a93a5489f4c2f2b543befd38c77b3','Lógica congelada evaluada en memoria, clasificación C')
targets={txt(b['raw']['N_DOC']):b for b in inc if b['raw']['ANIO_INFORMADO']==2025 and not b['key']}
assert len(targets)==20
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
KEEP={'TIPO_DOC','N_DOC','DV','RUT','CODCLI','CODCARPR','CODIGOCARRERA','NOMBRE_L','ANOMATRICULA','PERIODOMATRICULA','ANOINGRESO','PERIODOINGRESO','ESTADOACADEMICO','SITUACION','SEDE','JORNADA','NIVEL','FECHAMATRICULA','FECH_CAR','FECHATITULO','FECHA_TITULACION','FECHAEGRESO','FECHA_EGRESO'}
def read_xlsx(path,selected,predicate=lambda r:True,require_ids=False):
 """Preserve literal stored ID text and exact Excel row; dates retain Excel number format provenance."""
 out=[];meta=[]
 with zipfile.ZipFile(path) as z:
  ss=[]
  if 'xl/sharedStrings.xml' in z.namelist():
   for _,el in E.iterparse(z.open('xl/sharedStrings.xml'),events=('end',),tag=NS+'si'):
    ss.append(''.join(el.itertext()));el.clear()
  wb=E.fromstring(z.read('xl/workbook.xml'))
  rel=E.fromstring(z.read('xl/_rels/workbook.xml.rels'))
  rels={x.get('Id'):x.get('Target') for x in rel}
  for sheet in wb.find(NS+'sheets'):
   name=sheet.get('name')
   if selected is not None and name not in selected:continue
   target=rels[sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
   xml=target.lstrip('/') if target.startswith('/') else 'xl/'+target
   headers=None;n=0
   for _,el in E.iterparse(z.open(xml),events=('end',),tag=NS+'row'):
    row={}
    for c in el:
     col=re.sub(r'\d','',c.get('r',''));v=c.find(NS+'v');t=c.get('t')
     if t=='inlineStr':v0=c.find(NS+'is');value=''.join(v0.itertext()) if v0 is not None else ''
     elif v is None:value=''
     elif t=='s':value=ss[int(v.text)]
     else:value=v.text or ''
     row[col]=value
    if headers is None:
     hh={k:txt(v) for k,v in row.items()}
     if ('RUT' in hh.values() and (not require_ids or 'CODCLI' in hh.values())):
      headers=hh;hr=int(el.get('r'));kept={k:v for k,v in hh.items() if v in KEEP}
     elif int(el.get('r'))>=10:break
    elif any(row.values()):
     n+=1;dd={headers[k]:v for k,v in row.items() if k in kept}
     dd['_row']=int(el.get('r'));dd['_sheet']=name
     if predicate(dd):out.append(dd)
    el.clear()
   if headers:meta.append({'sheet':name,'rows':n,'header_row':hr,'columns':[v for v in headers.values() if v in KEEP]})
 return out,meta
prep=next(s for s in prior['fuentes_base'] if Path(s['ruta']).name=='IPSS_Procesamiento.xlsx')
prepsid=source(prep['ruta'],'2025_carga',prep['sha256'],'Correspondencia explícita J=RUT, BU=N_DOC, BV=DV')
prep_rows,_=read_xlsx(prep['ruta'],['2025_carga'],lambda r:txt(r.get('N_DOC')) in targets)
aliases={d:{canon(r.get('RUT')) for r in prep_rows if txt(r.get('N_DOC'))==d and canon(r.get('RUT'))} for d in targets}
assert all(len(aa)==1 for aa in aliases.values()) and len(set.union(*aliases.values()))==20
allaliases=set.union(*aliases.values())
snapshots={};snapids={}
for label in ['10246','11998','12112']:
 s=next(s for s in prior['fuentes_base'] if Path(s['ruta']).name==f'DATOSDEALUMNOS_{label}.xlsx')
 sid=source(s['ruta'],'Hoja1',s['sha256'],'Fotografía institucional '+label+'; fecha efectiva del estado no acreditada')
 rows,meta=read_xlsx(s['ruta'],['Hoja1'],lambda r:canon(r.get('RUT')) in allaliases,True)
 snapshots[label]=rows;snapids[label]=sid
cli={d:{txt(r['CODCLI']) for rows in snapshots.values() for r in rows if canon(r.get('RUT')) in aliases[d] and txt(r.get('CODCLI'))} for d in targets}
assert sum(bool(cc) for cc in cli.values())==18 and len(set.union(*cli.values()))==19
allcli=set.union(*cli.values())
assert all(sum(c in cc for cc in cli.values())==1 for c in allcli)
# Read the same snapshots again by verified CODCLI, retaining a changed document and all enrolments.
for label in snapshots:
 s=next(s for s in sources if s['id']==snapids[label])
 snapshots[label],_=read_xlsx(s['path'],['Hoja1'],lambda r:txt(r.get('CODCLI')) in allcli or canon(r.get('RUT')) in allaliases,True)
links={d:set(aliases[d]) for d in targets}
for rows in snapshots.values():
 for d,cc in cli.items():
  links[d]|={canon(r.get('RUT')) for r in rows if txt(r.get('CODCLI')) in cc and canon(r.get('RUT'))}
assert all(sum(a in aa for aa in links.values())==1 for a in set.union(*links.values()))
def matches(d,r):return txt(r.get('CODCLI')) in cli[d] or canon(r.get('RUT')) in links[d]
focus14={d for d in targets if any(matches(d,r) and txt(r.get('ESTADOACADEMICO'))=='VIGENTE' for r in snapshots['12112'])}
assert len(focus14)==14
pids={b['raw']['_row']:f"C{b['raw']['ANIO_INFORMADO']}_{i+1:04d}" for i,b in enumerate(inc)}
targetids={d:pids[b['raw']['_row']] for d,b in targets.items()}
people=[]
for b in inc:
 r,e=b['raw'],b['engine'];d=txt(r['N_DOC']);known=cli.get(d,set()) if r['TIPO_DOC']=='P' else set()
 people.append([pids[r['_row']],r['ANIO_INFORMADO'],literal(r['TIPO_DOC']),literal(r['N_DOC']),literal(r['DV']),r['_row'],e['CODIGO_UNICO'],e['NOMBRE_CARRERA'],literal(r['COD_SED']),literal(r['COD_CAR']),literal(r['JOR']),literal(r['VERSION']),r['ANIO_ING_ORI'],r['SEM_ING_ORI'],literal(r['VIG']),' / '.join(sorted(known)),'Documento+DV exactos' if b['key'] else 'Puente explícito y CODCLI' if known else 'Pendiente CODCLI','B/C; denominador D'])
identity=[]
for d,b in targets.items():
 pr=[r for r in prep_rows if txt(r.get('N_DOC'))==d];cc=sorted(cli[d]);r=b['raw']
 identity.append([targetids[d],2025,literal(r['TIPO_DOC']),literal(r['N_DOC']),literal(r['DV']),literal(pr[0].get('RUT')),' / '.join(sorted({literal(z['_row']) for z in pr})),cc[0] if cc else 'Pendiente',cc[1] if len(cc)>1 else '',len(cc),'Identificado' if cc else 'Pendiente',b['engine']['NOMBRE_CARRERA'],1 if d in focus14 else 0,prepsid,'2025_carga!J / BU / BV','B/C; tipo documental definitivo E'])
closure_rows=[];control=[]
specs=[('2025-T2','*T2_2025*','T2_2025',2024,'ed5de007202df0780bb3396ad88307f4096d7c8b729005486a20d1123096d5b3'),('2025-T3','*T3_2025*','T3_2025',2024,'68a1cd54ee48c1e6a679c1dbb3999e12d491543e9425e81f3d0508fefdc8d6cc'),('2026-T2','*13_07*','Hoja1',2025,'7926a9cabcc67ed19abb50459132fd74ebb323bff9f5cb53e9116378c21a6769'),('2026-T3','*02_10*','Base',2025,'de4e73ee7d27779cdc531c6816f745d412e1021cbd61e4fceb8ab0459cbda4ae')]
for close,pat,sheet,y,h in specs:
 paths=list(Path('/Users/alexi/Downloads/cierre').glob(pat));assert len(paths)==1
 sid=source(paths[0],sheet,h,'Listado parcial de cierre '+close+'; no numerador acreditado')
 rr,meta=read_xlsx(paths[0],[sheet]);found=set();vig=set();nm=0
 idx=defaultdict(list);ci=defaultdict(list)
 for r in rr:
  kk=key(r.get('RUT'))
  if kk:idx[kk].append(r)
  ci[txt(r.get('CODCLI'))].append(r)
 for b in inc:
  if b['raw']['ANIO_INFORMADO']!=y:continue
  pid=pids[b['raw']['_row']];d=txt(b['raw']['N_DOC'])
  rows=idx.get(b['key'],[]) if b['key'] else [r for r in rr if any(txt(r.get('CODCLI'))==c for c in cli.get(d,set())) or canon(r.get('RUT')) in links.get(d,set())]
  if rows:found.add(pid)
  for r in rows:
   state=literal(r.get('ESTADOACADEMICO')) or 'Sin campo';nm+=1
   if state=='VIGENTE':vig.add(pid)
   closure_rows.append([pid,y,close,literal(r.get('RUT')),literal(r.get('CODCLI')),literal(r.get('CODCARPR',r.get('CODIGOCARRERA'))),literal(r.get('NOMBRE_L')),literal(r.get('ANOMATRICULA')),literal(r.get('PERIODOMATRICULA')),literal(r.get('ANOINGRESO')),literal(r.get('PERIODOINGRESO')),state,literal(r.get('FECHAMATRICULA')),sid,sheet,r['_row'],'Documento+DV exactos' if b['key'] else 'Puente explícito / CODCLI','B/C; cobertura y fecha E'])
 control.append({'cohort':y,'closure':close,'denominator':sum(b['raw']['ANIO_INFORMADO']==y for b in inc),'found':len(found),'vigente':len(vig) if 'ESTADOACADEMICO' in meta[0]['columns'] else None,'rows':nm,'rate':'Pendiente E'})
assert [x['found'] for x in control]==[1,325,2,0]
assert [x['vigente'] for x in control]==[1,317,None,0]
observations=[];focuscontrols=[]
def add_obs(label,sid,rr,nominal=''):
 for d in targets:
  for r in rr:
   if not matches(d,r):continue
   method='CODCLI exacto' if txt(r.get('CODCLI')) in cli[d] else 'RUT explícito exacto'
   observations.append([targetids[d],label,literal(r.get('RUT')),literal(r.get('CODCLI')),literal(r.get('CODCARPR',r.get('CODIGOCARRERA'))),literal(r.get('NOMBRE_L')),literal(r.get('ANOMATRICULA')),literal(r.get('PERIODOMATRICULA')),literal(r.get('ANOINGRESO')),literal(r.get('PERIODOINGRESO')),literal(r.get('ESTADOACADEMICO')) or 'Sin campo',literal(r.get('SITUACION')),literal(r.get('SEDE')),literal(r.get('JORNADA')),literal(r.get('NIVEL')),literal(r.get('FECHAMATRICULA')),literal(r.get('FECH_CAR')),literal(r.get('FECHATITULO',r.get('FECHA_TITULACION'))),literal(r.get('FECHAEGRESO',r.get('FECHA_EGRESO'))),sid,r['_sheet'],r['_row'],nominal,method,1 if d in focus14 else 0,'B/C; fecha efectiva de estado E'])
for label,rr in snapshots.items():
 add_obs(label,snapids[label],rr)
 ff=[r for d in focus14 for r in rr if matches(d,r)]
 vv=sum(any(matches(d,r) and txt(r.get('ESTADOACADEMICO'))=='VIGENTE' for r in rr) for d in focus14)
 assert len(ff)==15 and vv==(13 if label=='10246' else 14)
 focuscontrols.append({'source':label,'people':14,'rows':len(ff),'any_vigente':vv})
additional_controls=[]
for n,s in enumerate(prior['fuentes_adicionales']):
 sid=source(s['ruta'],'Todas las hojas con RUT+CODCLI',s['sha256'],s['contexto'])
 rr,meta=read_xlsx(s['ruta'],None,lambda r:txt(r.get('CODCLI')) in allcli or canon(r.get('RUT')) in set.union(*links.values()),True)
 nominal=s['contexto'].replace('Base Maestra corte nominal ','') if s['contexto'].startswith('Base Maestra') else ''
 add_obs('MASTER_'+nominal if nominal else Path(s['ruta']).stem,sid,rr,nominal)
 new_missing={d for d in targets if not cli[d] and any(canon(r.get('RUT')) in links[d] and txt(r.get('CODCLI')) for r in rr)}
 assert not new_missing
 if meta:
  found=sum(any(matches(d,r) for r in rr) for d in targets)
  vv=sum(any(matches(d,r) and txt(r.get('ESTADOACADEMICO'))=='VIGENTE' for r in rr) for d in focus14)
  assert found==s['personas_20_encontradas'] and vv==s['personas_14_alguna_VIGENTE']
 additional_controls.append({'source':sid,'comparable':bool(meta),'rows_matched':len(rr),'nominal':nominal,'new_keys':0})
 if n%10==0:print('Fuentes adicionales verificadas',n+1,flush=True)
# Existing historical 2025-2 carries all enrolments, unlike grades rows (not an enrolment register).
hist=next(s for s in prior['fuentes_base'] if Path(s['ruta']).name=='2025-2.xlsx')
sid=source(hist['ruta'],'Detalle1 / Hoja1',hist['sha256'],'Preparación 2025; conservar filas y hojas sin deduplicar matrículas entre fuentes')
rr,_=read_xlsx(hist['ruta'],['Detalle1','Hoja1'],lambda r:txt(r.get('CODCLI')) in allcli or canon(r.get('RUT')) in set.union(*links.values()),True)
add_obs('RESPALDO_2025_2',sid,rr)
# Preserve annual observations for the 20, with original document fields and no inferred VIG.
annual=[]
for d in targets:
 for r in raw:
  direct=txt(r['TIPO_DOC'])=='P' and txt(r['N_DOC'])==d
  rk=canon(literal(r['N_DOC'])+'-'+literal(r['DV']))
  if not direct and rk not in links[d]:continue
  annual.append([targetids[d],r['ANIO_INFORMADO'],literal(r['TIPO_DOC']),literal(r['N_DOC']),literal(r['DV']),literal(r['COD_SED']),literal(r['COD_CAR']),literal(r['JOR']),literal(r['VERSION']),r['ANIO_ING_ORI'],r['SEM_ING_ORI'],literal(r['VIG']),r['_row'],rawsid,'Documento P original exacto' if direct else 'Puente documental observado','B/C; matrícula anual, no cierre T2/T3'])
payload={'created':datetime.datetime.now().astimezone().isoformat(),'people':people,'identity':identity,'closures':closure_rows,'observations':observations,'annual20':annual,'sources':sources,'control':control,'focus_controls':focuscontrols,'additional_controls':additional_controls,'private_path':str(P),'aggregate_path':str(OLD/'RETENCION_INTERMEDIA_IPSS_REVISION_20261021_133221.xlsx')}
(P/'payload.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
public={'created':payload['created'],'denominators':[558,1150,222,124],'closures':control,'identity20':{'persons':20,'identified':18,'pending':2,'CODCLI':19,'focus':14},'focus':focuscontrols,'sources_verified':len(sources),'additional_sources':len(additional_controls),'comparable_additional':sum(x['comparable'] for x in additional_controls),'private_rows':{k:len(payload[k]) for k in ['people','identity','closures','observations','annual20']},'sources':sources,'privacy':'Individual payload and workbook only in verified .local_restricted; no names/birthdates/sex/fuzzy matching; no external transfer.'}
(O/'VERIFICACION_AGREGADA.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in public.items() if k!='sources'},ensure_ascii=False,indent=2))
