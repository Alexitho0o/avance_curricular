from pathlib import Path
from collections import Counter,defaultdict
import json,re,hashlib,datetime
import openpyxl
import importlib.util
T=Path(__file__).parent
ROOT=Path('/Users/alexi/Documents/GitHub/avance_curricular')
PRE=ROOT/'outputs/retencion_intermedia_t2_t3/20261020_221157/MANIFEST_CONTINUIDAD.json'
prev=json.loads(PRE.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(v):return '' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip().upper()
def key(v,d=None):
    v=text(v).replace('.','').replace(' ','')
    if d is None:
        if '-' not in v:return None
        v,d=v.rsplit('-',1)
    d=text(d)
    return str(int(v))+'-'+d if re.fullmatch(r'\d+',v) and re.fullmatch('[0-9K]',d) else None
def robust(v,d=None):
    v=text(v)
    if d is not None:
        return key(re.sub(r'[^0-9]','',v),re.sub(r'[^0-9K]','',text(d)))
    v=re.sub('[^0-9K]','',v)
    return key(v[:-1],v[-1:]) if len(v)>1 else None
def valid(k):
    if not k:return False
    n,d=k.split('-');r=11-sum(int(c)*(2+i%6) for i,c in enumerate(n[::-1]))%11
    return d==('0' if r==11 else 'K' if r==10 else str(r))
def rows(p,s):
    w=openpyxl.load_workbook(p,read_only=True,data_only=True);z=list(w[s].values);w.close();h=[str(x).strip() for x in z[0]]
    return [dict(zip(h,r),_row=i) for i,r in enumerate(z[1:],2) if any(x is not None for x in r)]
def meta(p,s=None):return {'path':str(p),'sheet':s,'sha256':sha(p),'bytes':p.stat().st_size,'mtime':datetime.datetime.fromtimestamp(p.stat().st_mtime).astimezone().isoformat()}
mu=Path(prev['sources'][0]['path']);mrall=rows(mu,'BASE_RETENCION_MU');mr=[r for r in mrall if text(r['ANIO_INFORMADO'])=='2026'];mi=defaultdict(list);body=defaultdict(list);mirobust=defaultdict(list)
for r in mr:
    if text(r['TIPO_DOC'])=='R':
        k=key(r['N_DOC'],r['DV']);mi[k].append(r);mirobust[robust(r['N_DOC'],r['DV'])].append(r)
        if k:body[k.split('-')[0]].append(r)
up=Path('/Users/alexi/Downloads/DATOSDEALUMNOS_12112.xlsx');ur=rows(up,'Hoja1');ui=defaultdict(list);urob=defaultdict(list)
for r in ur:ui[key(r['RUT'])].append(r);urob[robust(r['RUT'])].append(r)
cohorts={};orows={};sources=[meta(mu,'BASE_RETENCION_MU'),meta(up,'Hoja1')]
for t in [2,3]:
    src=next(x for x in prev['sources'] if x['id']==f'T{t}');p=Path(src['path']);rr=rows(p,src['sheet']);sel=[r for r in rr if text(r['ANOINGRESO'])=='2025' and text(r['PERIODOINGRESO'])==str(t)];idx=defaultdict(list)
    for r in sel:idx[key(r['RUT'])].append(r)
    cohorts[t]=idx;orows[t]=sel;sources.append(meta(p,src['sheet']))
keys=sorted(set(cohorts[2])|set(cohorts[3]));ids={k:f'P{i:04d}' for i,k in enumerate(keys,1)}
assert all(valid(k) for k in keys)
report={};detail=[]
def counts(rs,field):return dict(Counter(text(r.get(field)) for r in rs))
def dates(rs):
    co=Counter()
    for r in rs:
        v=r.get('FECHAMATRICULA')
        if isinstance(v,(datetime.datetime,datetime.date)):co[v.strftime('%Y-%m')]+=1
        else:co[str(v)[:10]]+=1
    return dict(co)
def state_group(rs):
    if not rs:return 'No localizado en UMAS actual'
    r26=[r for r in rs if text(r['ANOMATRICULA'])=='2026']
    if any(text(r['ESTADOACADEMICO'])=='VIGENTE' for r in r26):return 'ANOMATRICULA 2026 y VIGENTE'
    if r26:return 'ANOMATRICULA 2026; sin VIGENTE'
    if any(text(r['ANOMATRICULA'])=='2027' for r in rs):return 'Sin registro 2026; con 2027'
    return 'Solo años de matrícula distintos de 2026/2027'
for t,idx in cohorts.items():
    absent=[k for k in idx if not mi.get(k)]
    assert len(absent)==(142 if t==2 else 74)
    allu=[r for k in absent for r in ui.get(k,[])];u26=[r for r in allu if text(r['ANOMATRICULA'])=='2026'];u26v=[r for r in u26 if text(r['ESTADOACADEMICO'])=='VIGENTE']
    data={'denominator':len(idx),'absent_mu':len(absent),'all_origin_valid_dv':all(valid(k) for k in idx),'new_matches_more_permissive_format':sum(bool(mirobust.get(k)) for k in absent),'same_body_different_dv_mu':sum(bool(body.get(k.split('-')[0])) for k in absent),'found_current_umas':sum(bool(ui.get(k)) for k in absent),'found_current_after_format_only':sum(bool(urob.get(k)) and not ui.get(k) for k in absent),'current_classification_persons':dict(Counter(state_group(ui.get(k,[])) for k in absent)),'current_rows':len(allu),'current_years_rows':counts(allu,'ANOMATRICULA'),'current_states_rows':counts(allu,'ESTADOACADEMICO'),'current_situations_rows':counts(allu,'SITUACION'),'current_2026_terms_rows':counts(u26,'PERIODOMATRICULA'),'current_2026_states_rows':counts(u26,'ESTADOACADEMICO'),'current_2026_vig_terms_rows':counts(u26v,'PERIODOMATRICULA'),'current_2026_vig_enrol_dates':dates(u26v),'current_2026_vig_categories':counts(u26v,'CATEGORIA')}
    # Person distributions deliberately distinct from record distributions.
    for filtername,rs in [('any2026',u26),('vig2026',u26v)]:
        data[filtername+'_persons_by_term_combination']=dict(Counter(' / '.join(sorted({text(r['PERIODOMATRICULA']) for r in rs if key(r['RUT'])==k})) for k in absent if any(key(r['RUT'])==k for r in rs)))
    data['all_cohort_current_2026_vig_persons']=sum(any(text(r['ANOMATRICULA'])=='2026' and text(r['ESTADOACADEMICO'])=='VIGENTE' for r in ui.get(k,[])) for k in idx)
    data['absent_other_mu_years_persons']=dict(Counter(' / '.join(sorted({text(r['ANIO_INFORMADO']) for r in mrall if text(r['TIPO_DOC'])=='R' and key(r['N_DOC'],r['DV'])==k})) or 'Ninguno' for k in absent))
    data['source_orig_states_rows']=counts([r for k in absent for r in idx[k]],'ESTADOACADEMICO')
    data['source_orig_career_rows']=counts([r for k in absent for r in idx[k]],'NOMBRE_L')
    no26=[k for k in absent if not any(text(r['ANOMATRICULA'])=='2026' for r in ui.get(k,[]))]
    data['no2026_current_state_combinations_persons']=dict(Counter(' / '.join(sorted({text(r['ESTADOACADEMICO']) for r in ui.get(k,[])})) for k in no26))
    data['no2026_with_any_VIGENTE_persons']=sum(any(text(r['ESTADOACADEMICO'])=='VIGENTE' for r in ui.get(k,[])) for k in no26)
    data['no2026_VIGENTE_years_rows']=counts([r for k in no26 for r in ui.get(k,[]) if text(r['ESTADOACADEMICO'])=='VIGENTE'],'ANOMATRICULA')
    for k in absent:
        rs=ui.get(k,[]);r26=[r for r in rs if text(r['ANOMATRICULA'])=='2026']
        detail.append({'cohort':f'2025-T{t}','id':ids[k],'source_rows':[r['_row'] for r in idx[k]],'current_rows':[r['_row'] for r in rs],'group':state_group(rs),'matricula_years':sorted({text(r['ANOMATRICULA']) for r in rs}),'current_2026_terms':sorted({text(r['PERIODOMATRICULA']) for r in r26}),'current_states':sorted({text(r['ESTADOACADEMICO']) for r in rs}),'current_situations':sorted({text(r['SITUACION']) for r in rs}),'origin_careers':sorted({text(r['NOMBRE_L']) for r in idx[k]})})
    report[f'2025-T{t}']=data
globalp={'umas_records':len(ur),'umas_valid_rut_unique':len({k for k in ui if k and valid(k)}),'umas_unparseable_rows':len(ui.get(None,[])),'umas_invalid_dv_rows':sum(not valid(key(r['RUT'])) for r in ur),'mu2026_records':len(mr),'mu2026_invalid_key_rows':sum(not valid(key(r['N_DOC'],r['DV'])) for r in mr),'mu2026_doc_types':counts(mr,'TIPO_DOC'),'umas_year_rows':counts(ur,'ANOMATRICULA'),'umas_2026_period_rows':counts([r for r in ur if text(r['ANOMATRICULA'])=='2026'],'PERIODOMATRICULA')}
manifestpath=mu.parent/'MANIFEST_BASE_RETENCION_MU_2022_2026.json';manifest=json.loads(manifestpath.read_text());cp=Path(manifest['esquema_rector']['archivo']);cs=manifest['esquema_rector']['hoja'];can=rows(cp,cs);cols=manifest['esquema_rector']['columnas']
inventorypath=mu.parent/'INVENTARIO_FUENTES_SHA256.json';inventory=json.loads(inventorypath.read_text());canonicalexpected=next(x for x in inventory if x['anio']==2026)['sha256']
builder=ROOT/'scripts/construir_base_retencion_mu_2022_2026.py'
spec=importlib.util.spec_from_file_location('readonly_original_constructor',builder);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
canvals=[[module.typed_value(c,r.get(c)) for c in cols] for r in can]
muvals=[[r.get(c) for c in cols] for r in mr]
changed=Counter()
for a,b in zip(canvals,muvals):
    for c,x,y in zip(cols,a,b):
        if x!=y:changed[c]+=1
cankeys={key(r['N_DOC'],r['DV']) for r in can if text(r['TIPO_DOC'])=='R'}
digestvalues=lambda v:hashlib.sha256(json.dumps(v,ensure_ascii=False,separators=(',',':'),default=str).encode()).hexdigest()
coverage={'canonical_path':str(cp),'canonical_sheet':cs,'canonical_sha256':sha(cp),'inventory_expected_sha256':canonicalexpected,'canonical_hash_matches_inventory':sha(cp)==canonicalexpected,'canonical_rows':len(can),'mu2026_rows':len(mr),'columns_compared':len(cols),'normalized_row_by_row_equal':canvals==muvals,'normalized_canonical_content_hash':digestvalues(canvals),'normalized_base_content_hash':digestvalues(muvals),'different_cells_by_column':dict(changed),'absent_found_directly_in_canonical':{str(t):sum(k in cankeys for k in cohorts[t] if not mi.get(k)) for t in cohorts}}
sources.extend([meta(cp,cs),meta(manifestpath),meta(inventorypath),meta(builder)])
result={'sources':sources,'global':globalp,'cohorts':report,'coverage':coverage,'detail_pseudonymous':detail}
(T/'diagnosis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str))
print(json.dumps({'cohorts':report,'coverage':coverage},ensure_ascii=False,indent=2))
