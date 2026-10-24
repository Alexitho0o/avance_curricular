#!/usr/bin/env python3
"""Carga congelada del ensayo previo para evaluación separada del enlace conjunto.

Reutiliza su selección y referencia sin modificar el script histórico ni salidas.
Las referencias se entregan solo al evaluador, nunca al algoritmo de enlace.
"""
import csv,hashlib,io,json,os,re,sys
from collections import Counter,defaultdict,deque
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.reconstruir_planes_umas import read_sheet,token
from scripts.diagnosticar_candidatos_mrun_umas import birth,sha,year
from common.versiones_por_cohorte import clave_grupo
OUT=ROOT/'data/prueba_500_enlaces_historicos/20261016'
YEARS={2018,2019,2020,2022}
def doc(v,dv=None):
    s=token(v).replace('.','').replace(' ','').upper()
    if dv is not None:s=s+'-'+token(dv).upper()
    return s if re.fullmatch(r'\d{6,9}-[0-9K]',s) else None
def dateym(v):
    a=birth(v)
    if a:return a
    for fmt in ('%d%m%Y','%Y%m%d','%d-%m-%Y %H:%M:%S','%d/%m/%Y %H:%M'):
        try:
            dt=datetime.strptime(token(v),fmt)
            return dt.strftime('%Y%m') if 1900<dt.year<=2026 else None
        except ValueError:pass
    return None
def signature(r):
    vals=(r['year'],r['birth'],r['sex'],r['code'],r['ori'],r['semori'],r['act'],r['semact'])
    return vals if all(v is not None and v!='' for v in vals) else None
def cargar_ensayo():
    sm=json.loads((ROOT/'data/continuidad_trayectoria/20261016/fuentes.json').read_text())['umas']['alumnos']
    inv=list(csv.DictReader((ROOT/'data/versiones_historicas_sies_umas/fase_1_20261015/fuentes.tsv').open(),delimiter='\t'))
    mp=Path(next(r['path'] for r in inv if r['id']=='mrun_MRUN01'))
    assert sha(mp)=='510b7d03405398ed29196f750048dea1b07656ba722c1bf12cb3ab427098f0fd'
    original_source = dict(sm)
    # Edición explícita: no cambiar de extracto según disponibilidad de rutas.
    sm = dict(sm, path='/Users/alexi/Downloads/DATOSDEALUMNOS_12023.xlsx', sha256='331f73f352a3df5075126feaadc66566b09d77cb3527220bd185d1c432eb73a4')
    assert sha(sm['path'])==sm['sha256']
    sources={str(mp):sha(mp),sm['path']:sm['sha256']}
    base=next(p for p in Path('/Users/alexi/Library/CloudStorage').iterdir() if p.name.startswith('OneDrive-InstitutoProfesional'))
    paths={}
    for root,dirs,files in os.walk(base):
        dirs[:]=[d for d in dirs if d not in {'.git','node_modules','.venv','venv'}]
        for f in files:
            if f in {f'MAT_IP_CIISA_{y}.xlsx' for y in (2018,2019,2020)} and '/Publicados/' in root:
                paths[int(re.search(r'20\d{2}',f)[0])]=Path(root)/f
            if f=='2022.csv' and '/Enviados/' in root and Path(root).name=='2022':paths[2022]=Path(root)/f
    assert set(paths)==YEARS,paths
    references=[];refmeta=[]
    for y,p in sorted(paths.items()):
        sources[str(p)]=sha(p)
        if y==2022:
            raw=p.read_bytes()
            try:txt=raw.decode('utf-8-sig');encoding='utf-8-sig'
            except UnicodeDecodeError:txt=raw.decode('latin1');encoding='latin1'
            rows=list(csv.DictReader(io.StringIO(txt),delimiter=';'))
            for r in rows:
                references.append({'year':y,'person':doc(r['N_DOC'],r['DV']),'birth':dateym(r['FECH_NAC']),'sex':{'H':'M','M':'F'}.get(token(r['SEXO'])),
                    'code':f"I{token(r['COD_IES'])}S{token(r['COD_SED'])}C{token(r['COD_CAR'])}J{token(r['JOR'])}V{token(r['VERSION'])}",
                    'ori':token(r['ANIO_ING_ORI']),'semori':token(r['SEM_ING_ORI']),'act':token(r['ANIO_ING_ACT']),'semact':token(r['SEM_ING_ACT'])})
            refmeta.append({'year':y,'path':str(p),'rows':len(rows),'format':'CSV enviado; no aceptación acreditada','encoding':encoding})
        else:
            fields=('MC_CAT_PERIODO','MM_N_DOCUMENTO','MM_DV','MM_SEXO','MM_FECHA_NACIMIENTO','MM_ANIO_ORIGEN','MM_SEM_ORIGEN','MM_ANIO_ACTUAL','MM_SEM_ACTUAL','MC_CODIGO_UNICO')
            rows,meta=read_sheet(p,f'MAT_{y}',fields)
            for r in rows:
                assert token(r['MC_CAT_PERIODO'])==f'MAT_{y}'
                references.append({'year':y,'person':doc(r['MM_N_DOCUMENTO'],r['MM_DV']),'birth':dateym(r['MM_FECHA_NACIMIENTO']),
                    'sex':{'H':'M','M':'F'}.get(token(r['MM_SEXO'])),'code':token(r['MC_CODIGO_UNICO']),
                    'ori':token(r['MM_ANIO_ORIGEN']),'semori':token(r['MM_SEM_ORIGEN']),'act':token(r['MM_ANIO_ACTUAL']),'semact':token(r['MM_SEM_ACTUAL'])})
            refmeta.append({'year':y,'path':str(p),'rows':len(rows),'sheet':f'MAT_{y}','format':'Reporte institucional con documento y Código Único'})
    reference_quality={str(y):dict(Counter(('COMPLETO' if signature(r) and r['person'] else 'INCOMPLETO') for r in references if r['year']==y)) for y in YEARS}
    refs=defaultdict(list);refindex=defaultdict(set)
    for r in references:
        if r['person']:
            refs[r['year'],r['person']].append(r)
            if signature(r):refindex[signature(r)].add(r['person'])
    mr=[];baseidx=defaultdict(list);fullidx=defaultdict(set);rawmr=list(csv.DictReader(mp.open()))
    for r in rawmr:
        y=year(r['cat_periodo'])
        if y not in YEARS:continue
        rr={'year':y,'birth':dateym(r['fec_nac_alu']),'sex':{'1':'M','2':'F'}.get(r['gen_alu']),'code':r['codigo_unico'],
          'ori':r['anio_ing_carr_ori'],'semori':r['sem_ing_carr_ori'],'act':r['anio_ing_carr_act'],'semact':r['sem_ing_carr_act'],
          'mrun':token(r['mrun']),'type':r['tipo_plan_carr']}
        mr.append(rr)
        if rr['birth'] and rr['sex'] and rr['mrun']:baseidx[y,rr['birth'],rr['sex']].append(rr)
        sig=signature(rr)
        if sig and rr['mrun']:fullidx[sig].add(rr['mrun'])
    # Evidencia documental indirecta: unicidad completa y recíproca por año.
    fwd=defaultdict(set);rev=defaultdict(set)
    for sig,people in refindex.items():
        mids=fullidx.get(sig,set())
        for person in people:fwd[sig[0],person].update(mids)
        for mid in mids:rev[sig[0],mid].update(people)
    adjudicated={}
    for (y,person),mids in fwd.items():
        if len(mids)==1:
            mid=next(iter(mids))
            if len(rev[y,mid])==1:adjudicated[y,person]=mid
    gp=ROOT/'data/versiones_por_cohorte/20261016/grupos_existentes.json';sources[str(gp.relative_to(ROOT))]=sha(gp)
    gm=json.loads((gp.parent/'manifest.json').read_text());assert sha(gp)==gm['salidas'][gp.name]
    groups={g['clave']:g for g in json.loads(gp.read_text())}
    fields=('RUT','CODCLI','CODCARPR','SEDE','JORNADA','ANOMATRICULA','ANOINGRESO','FECHANACIMIENTO','SEXO','ESTADOACADEMICO','SITUACION')
    da,_=read_sheet(sm['path'],sm['sheet'],fields);eligible=defaultdict(list)
    for r in da:
        y=year(r['ANOMATRICULA']);person=doc(r['RUT'])
        if y in YEARS and person and (y,person) in refs:eligible[person].append(r)
    # Selección ANTES de generar candidaturas/evaluar resultados de estas personas.
    buckets=defaultdict(list)
    rank=lambda person:hashlib.sha256(('ensayo500-20261016|'+person).encode()).hexdigest()
    anchors={}
    for person,rr in eligible.items():
        rr.sort(key=lambda r:(-int(r['ANOMATRICULA']),token(r['CODCARPR']),token(r['SEDE']),token(r['JORNADA']),token(r['CODCLI'])))
        anchors[person]=rr[0];buckets[int(rr[0]['ANOMATRICULA'])].append(person)
    queues={y:deque(sorted(pp,key=rank)) for y,pp in buckets.items()};sample=[]
    while len(sample)<500 and any(queues.values()):
        for y in sorted(queues):
            if queues[y] and len(sample)<500:sample.append(queues[y].popleft())
    assert len(sample)==500,f'Solo {len(sample)} personas documentables'
    assert len(set(sample))==500
    return locals()
