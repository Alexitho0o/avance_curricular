"""Source closure labels, enrolment period and observation date are distinct observed variables."""
from pathlib import Path
from collections import defaultdict,Counter
import json,re,datetime,ast,contextlib,io,openpyxl
R=Path('/Users/alexi/Documents/GitHub/avance_curricular');O=R/'outputs/retencion_intermedia_t2_t3/20261021_153436';P=R/'.local_restricted/retencion_intermedia/20261021_153436'
pub=json.loads((O/'MODELO_AGREGADO.json').read_text());d=json.loads((P/'datos.json').read_text())
prof=R/'outputs/retencion_intermedia_t2_t3/20261020_215248/profile.py';g={'__file__':str(prof)}
with contextlib.redirect_stdout(io.StringIO()):exec(compile(prof.read_text().split('specs=',1)[0],str(prof),'exec'),g)
raw={r['_row']:r for r in g['raw']};base=[b for b in g['base'] if b['engine']['ESTADO_FINAL']=='INCLUIDO'];byid={f"C{b['raw']['ANIO_INFORMADO']}_{i+1:04d}":b for i,b in enumerate(base)}
context={s['id']:s['context'] for s in d['sources']};closes={s['context'].replace('Listado parcial ',''):s['id'] for s in d['sources'] if s['context'].startswith('Listado parcial ')}
latest=max((s for s in d['sources'] if s['context'].startswith('Base Maestra corte nominal ')),key=lambda s:s['context'])
ident=defaultdict(set)
for pp,b in byid.items():
 if b['key']:ident[b['key']].add(pp)
previous=json.loads((R/'.local_restricted/retencion_intermedia/20261021_144031/payload.json').read_text())
for row in previous['identity']:
 kk=g['key'](row[5])
 if kk:ident[kk].add(row[0])
# T2-2025 has RUT but no CODCLI; an exact-document join remains valid. Do not reject its schema.
existing_refs={ref for row in d['observations'] for ref in row[16].split('; ')}
for source in d['sources']:
 if not source['context'].startswith('Listado parcial '):continue
 ww=openpyxl.load_workbook(source['path'],read_only=True,data_only=True)
 sheet=source['sheet'];rr=g['records'](ww[sheet]);ww.close()
 for row in rr:
  ref=f"{source['id']}!{sheet}:{row['_row']}"
  if ref in existing_refs:continue
  for pp in ident.get(g['key'](row.get('RUT')),set()):
   literal=lambda v:'' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v)
   vals=[pp,int(row['ANOMATRICULA']),int(row['PERIODOMATRICULA']),literal(row.get('RUT')),literal(row.get('CODCLI')),literal(row.get('CODCARPR',row.get('CODIGOCARRERA'))),literal(row.get('NOMBRE_L')),literal(row.get('ESTADOACADEMICO')) or 'Sin campo',literal(row.get('SITUACION')),literal(row.get('FECHAMATRICULA')),literal(row.get('NIVEL')),literal(row.get('SEDE')),literal(row.get('JORNADA')),literal(row.get('FECH_CAR')),literal(row.get('FECHATITULO',row.get('FECHA_TITULACION'))),literal(row.get('FECHAEGRESO',row.get('FECHA_EGRESO'))),ref,'',1,'B/C; estado de extracción, no fecha de cierre E']
   d['observations'].append(vals)
  existing_refs.add(ref)
idx=defaultdict(list)
for row in d['observations']:idx[row[0]].append(row)
def rowids(row):return set(re.findall(r'\bF\d{3}\b',row[16]))
sets={close:{r[0] for r in d['observations'] if sid in rowids(r)} for close,sid in closes.items()}
counts=[sum(p[0] in sets[close] and p[1]==year for p in d['persons']) for close,year in [('2025-T2',2024),('2025-T3',2024),('2026-T2',2025),('2026-T3',2025)]]
assert counts==[1,325,2,0],counts
groups={tuple(r[:13]):[0]*14 for r in pub['groups']};groupids={k:'G'+str(i+1).zfill(4) for i,k in enumerate(groups)}
cohort=defaultdict(Counter);date=latest['context'].replace('Base Maestra corte nominal ','');semantics=[]
for p in d['persons']:
 del p[29:]
 pp,y=p[:2];rr=byid[pp]['raw'];rows=idx[pp];t2=f'{y+1}-T2';t3=f'{y+1}-T3'
 a=[r for r in rows if closes[t2] in rowids(r)];b=[r for r in rows if closes[t3] in rowids(r)];last=[r for r in rows if latest['id'] in rowids(r)]
 periods={(r[1],r[2]) for r in rows};lp=max(periods) if periods else None
 p[15]=f'{lp[0]}-T{lp[1]}' if lp else 'Sin período UMAS localizado';p[16]=' / '.join(sorted({r[7] for r in rows if lp and (r[1],r[2])==lp}));p[17]=len(rows)
 p[19:28]=[int((yy,tt) in periods) for yy,tt in [(2024,1),(2024,2),(2024,3),(2025,1),(2025,2),(2025,3),(2026,1),(2026,2),(2026,3)]]
 p[11]=int(bool(a));p[12]=int(bool(b));p[13]=int(any(r[7]=='VIGENTE' for r in a)) if y==2024 else 'Sin campo';p[14]=int(any(r[7]=='VIGENTE' for r in b))
 keys=[k for k in groups if k[0]==y and k[1]==p[7] and k[5]==str(rr['SEXO']) and k[6]==str(rr['MODALIDAD']) and k[7]==str(rr['JOR'])]
 birth=str(rr.get('FECH_NAC',''));year=None
 for fmt in ['%d/%m/%Y','%Y-%m-%d','%d-%m-%Y']:
  try:year=datetime.datetime.strptime(birth[:10],fmt).year;break
  except ValueError:pass
 age=y-year if year else None;band='SIN DATO' if age is None else 'Menos de 20' if age<20 else '20-24' if age<25 else '25-29' if age<30 else '30-39' if age<40 else '40+'
 keys=[k for k in keys if k[9]==band];assert len(keys)==1
 k=keys[0];z=groups[k];laststates=' / '.join(sorted({r[7] for r in last})) if last else 'No localizado en último respaldo'
 nominal=[v for r in rows for v in r[17].split(' / ') if v];vignom=[v for r in rows if r[7]=='VIGENTE' for v in r[17].split(' / ') if v]
 currentvig=int(any(r[1]==2026 and r[7]=='VIGENTE' for r in last))
 p.extend([groupids[k],*[int(pp in sets[close]) for close in ['2025-T2','2025-T3','2026-T2','2026-T3']],int(bool(last)),currentvig,laststates,date,max(nominal) if nominal else 'Sin fecha nominal',max(vignom) if vignom else 'Sin VIGENTE en respaldo nominal'])
 for i,val in enumerate([1,p[10],p[11],p[12],p[13] if isinstance(p[13],int) else 0,p[14],p[18],int(p[17]>0),int('TITULADO' in p[16]),int('EGRESADO' in p[16]),int(bool(last)),currentvig,int(any(r[7]=='TITULADO' for r in last)),int(any(r[7]=='EGRESADO' for r in last))]):z[i]+=val
 cohort[y].update({'denominator':1,'T1':p[10],'T2_records_observed':p[11],'T3_records_observed':p[12],'latest_snapshot_found':int(bool(last)),'latest_snapshot_any_VIGENTE':int(any(r[7]=='VIGENTE' for r in last)),'latest_snapshot_2026_VIGENTE':currentvig})
pub['groups']=[list(k)+z for k,z in groups.items()];pub['group_ids']=[groupids[k] for k in groups];pub['control']={str(y):dict(v) for y,v in cohort.items()};d['control']=pub['control']
pub['observations_unique']=len(d['observations'])
pub['latest_snapshot']={**latest,'date_nominal':date,'class':'B; fecha nominal de extracción, no estado efectivo de cierre'}
pub['period_semantics']={'clasificacion':'B/C/E','evidence':'2025-T3 contiene 325 personas de cohorte 2024 aunque la mayoría conserva PERIODOMATRICULA=1. No interpretar ese campo como último período cursado.','closure_counts':counts,'rule_C':'Presencia en T2/T3 usa pertenencia a listado de cierre, no PERIODOMATRICULA. Última matrícula declarada y última observación nominal se muestran separadas.','formal_rate':'Pendiente E'}
pub['metric_definition']='C/E: T2/T3 = presencia en listado parcial correspondiente / cohorte fija. Último respaldo = ANOMATRICULA 2026 y VIGENTE observada en extracción nominal, no tasa de cierre. T1 conserva cálculo anual. Última matrícula declarada no es último período cursado. No se clasifica deserción.'
period_counts=Counter((p[1],p[15])for p in d['persons'])
pub['last_period_counts']=[{'cohort':y,'last_period':lab,'people':n,'clasificacion':'B/C; matrícula declarada, no último período cursado'}for(y,lab),n in sorted(period_counts.items())]
d['last_period_counts']=pub['last_period_counts']
d['latest_snapshot']=pub['latest_snapshot'];d['period_semantics']=pub['period_semantics'];d['groups']=pub['groups'];d['group_ids']=pub['group_ids']
(P/'datos.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');(O/'MODELO_AGREGADO.json').write_text(json.dumps(pub,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'control':pub['control'],'latest_snapshot_nominal':date,'unique_observations':len(d['observations']),'groups':len(groups),'period_semantics':pub['period_semantics']},ensure_ascii=False,indent=2))
