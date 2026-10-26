from pathlib import Path
from collections import Counter,defaultdict
import json,re,hashlib,datetime
import openpyxl
T=Path(__file__).parent
ROOT=Path('/Users/alexi/Documents/GitHub/avance_curricular')
OUT=ROOT/'outputs/retencion_intermedia_t2_t3/20261020_221157'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(v):return '' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip().upper()
def key(v,d=None):
    v=text(v).replace('.','').replace(' ','')
    if d is None:
        if '-' not in v:return None
        v,d=v.rsplit('-',1)
    d=text(d)
    return str(int(v))+'-'+d if re.fullmatch(r'\d+',v) and re.fullmatch('[0-9K]',d) else None
def valid(k):
    if not k:return False
    n,d=k.split('-');r=11-sum(int(c)*(2+i%6) for i,c in enumerate(n[::-1]))%11
    return d==('0' if r==11 else 'K' if r==10 else str(r))
def rows(p,s):
    w=openpyxl.load_workbook(p,read_only=True,data_only=True);z=list(w[s].values);w.close()
    h=[str(x).strip() for x in z[0]]
    return [dict(zip(h,r),_row=i) for i,r in enumerate(z[1:],2) if any(x is not None for x in r)]
def source(p,s,rs,id):return {'id':id,'path':str(p),'sheet':s,'sha256':sha(p),'bytes':p.stat().st_size,'mtime':datetime.datetime.fromtimestamp(p.stat().st_mtime).astimezone().isoformat(),'rows':len(rs)}
mu=ROOT/'outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx'
raw=rows(mu,'BASE_RETENCION_MU');mr=[r for r in raw if r['ANIO_INFORMADO']==2026]
idx=defaultdict(list)
for r in mr:
    if text(r['TIPO_DOC'])=='R':idx[key(r['N_DOC'],r['DV'])].append(r)
src=[source(mu,'BASE_RETENCION_MU',raw,'MU')]
src[0].update(rows_2026=len(mr),vig=dict(Counter(text(r['VIG']) for r in mr)))
orig=[];by={};alldata={}
for t,pat,s in [(2,'*T2_2025*','T2_2025'),(3,'*T3_2025*','T3_2025')]:
    p=next(Path('/Users/alexi/Downloads/cierre').glob(pat));rr=rows(p,s);alldata[t]=rr
    selected=[r for r in rr if text(r['ANOINGRESO'])=='2025' and text(r['PERIODOINGRESO'])==str(t)]
    x=source(p,s,rr,f'T{t}');x.update(selected_rows=len(selected),selected_persons=len({key(r['RUT']) for r in selected}),states=dict(Counter(text(r['ESTADOACADEMICO']) for r in selected)))
    src.append(x)
    for r in selected:orig.append((t,r))
    by[t]=defaultdict(list)
    for r in selected:by[t][key(r['RUT'])].append(r)
assert [len(by[t]) for t in (2,3)]==[222,124]
assert all(valid(k) for t in by for k in by[t]),'Invalid source key: stop'
keys=sorted(set(by[2])|set(by[3]));ids={k:f'P{i:04d}' for i,k in enumerate(keys,1)}
origout=[]
for t,r in orig:
    origout.append([f'2025-T{t}',ids[key(r['RUT'])],f'T{t}',r['_row'],r['ANOINGRESO'],r['PERIODOINGRESO'],r['NOMBRE_L'],r.get('CODIGOCARRERA'),r['JORNADA'],r['ESTADOACADEMICO'],r.get('CATEGORIA'),r.get('ANOMATRICULA'),r.get('PERIODOMATRICULA')])
matched=[r for r in mr if text(r['TIPO_DOC'])=='R' and key(r['N_DOC'],r['DV']) in ids]
assert all(valid(key(r['N_DOC'],r['DV'])) for r in matched)
muout=[[ids[key(r['N_DOC'],r['DV'])],r['_row'],r['ANIO_INFORMADO'],r['VIG'],r['COD_SED'],r['COD_CAR'],r['JOR'],r['VERSION'],r['MODALIDAD'],r['ANIO_ING_ORI'],r['SEM_ING_ORI'],r['ANIO_ING_ACT'],r['SEM_ING_ACT'],f"I162S{r['COD_SED']}C{r['COD_CAR']}J{r['JOR']}V{r['VERSION']}"] for r in matched]
people=[];totals={}
for t in (2,3):
    for k,rr in by[t].items():
        careers=sorted({text(r['NOMBRE_L']) for r in rr});cc=careers[0] if len(careers)==1 else 'MÚLTIPLES CARRERAS (PENDIENTE)'
        match=idx.get(k,[]);vig=[r for r in match if r['VIG']==1];zero=[r for r in match if r['VIG']==0]
        people.append({'cohort':f'2025-T{t}','person':ids[k],'career':cc,'careers':' | '.join(careers),'orig_rows':len(rr),'orig_states':' | '.join(sorted({text(r['ESTADOACADEMICO']) for r in rr})),'match':len(match),'vig':len(vig),'zero':len(zero),'continue':int(bool(vig)),'onlyzero':int(bool(match) and len(zero)==len(match)),'absent':int(not match),'origin_discrepancy':int(any(text(r['ANIO_ING_ORI'])!='2025' for r in match)),'multiple_careers':int(len(careers)>1),'in_both':int(k in by[2] and k in by[3])})
    pp=[p for p in people if p['cohort']==f'2025-T{t}']
    totals[f'2025-T{t}']={'students':len(pp),'found':sum(p['match']>0 for p in pp),'continue':sum(p['continue'] for p in pp),'onlyzero':sum(p['onlyzero'] for p in pp),'absent':sum(p['absent'] for p in pp),'origin_discrepancy':sum(p['origin_discrepancy'] for p in pp),'multiple_careers':sum(p['multiple_careers'] for p in pp),'duplicate_source_persons':sum(p['orig_rows']>1 for p in pp)}
later2={key(r['RUT']) for r in alldata[3] if text(r['ANOINGRESO'])=='2025' and text(r['PERIODOINGRESO'])=='2'}
extra={'both_cohorts':len(set(by[2])&set(by[3])),'t2_later_snapshot':len(later2),'t2_later_only':len(later2-set(by[2])),'t2_initial_only':len(set(by[2])-later2),'mu_rows':len(mr),'mu_matched_rows':len(matched),'mu_unknown_vig':dict(Counter(text(r['VIG']) for r in matched if r['VIG'] not in (0,1)))}
manifestpath=mu.parent/'MANIFEST_BASE_RETENCION_MU_2022_2026.json'
manifest=json.loads(manifestpath.read_text())
src.append({'id':'MU_MANIFEST','path':str(manifestpath),'sha256':sha(manifestpath)})
data={'out':str(OUT),'sources':src,'origin':origout,'mu':muout,'people':people,'totals':totals,'additional':extra,'created':datetime.datetime.now().astimezone().isoformat()}
(T/'profile.json').write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str))
print(json.dumps({'totals':totals,'additional':extra,'sources':src},ensure_ascii=False,indent=2))
