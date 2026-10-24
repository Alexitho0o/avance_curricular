#!/usr/bin/env python3
"""Continúa F0 por corte y familia sin V; exporta solo conteos, no identidades."""
import ast,csv,hashlib,json,re,sys
from collections import Counter,defaultdict
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.reconstruir_planes_umas import read_sheet,token
from common.versiones_por_cohorte import clave_grupo
OUT=ROOT/'data/recuperacion_cruce_mrun_umas/20261016'
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def year(v):
    s=token(v);return int(s) if s.isdigit() and 2007<=int(s)<=2026 else None
def birth(v):
    s=token(v)
    for fmt in ('%d-%m-%Y','%Y-%m-%d %H:%M:%S','%Y-%m-%d','%d/%m/%Y','%Y%m'):
        try:
            dt=datetime.strptime(s,fmt)
            return dt.strftime('%Y%m') if 1900<dt.year<=2026 else None
        except ValueError:pass
    return None
def main():
    import pandas as pd
    sm=json.loads((ROOT/'data/continuidad_trayectoria/20261016/fuentes.json').read_text())['umas']['alumnos']
    inventory=list(csv.DictReader((ROOT/'data/versiones_historicas_sies_umas/fase_1_20261015/fuentes.tsv').open(),delimiter='\t'))
    mm=next(r for r in inventory if r['id']=='mrun_MRUN01');mp=Path(mm['path'])
    assert sha(mp)=='510b7d03405398ed29196f750048dea1b07656ba722c1bf12cb3ab427098f0fd'
    assert sha(sm['path'])==sm['sha256']
    sources={str(mp):sha(mp),sm['path']:sm['sha256']}
    gp=ROOT/'data/versiones_por_cohorte/20261016/grupos_existentes.json'
    manifest=json.loads((gp.parent/'manifest.json').read_text());assert sha(gp)==manifest['salidas'][gp.name]
    groups={g['clave']:g for g in json.loads(gp.read_text())};sources[str(gp.relative_to(ROOT))]=sha(gp)
    rp=ROOT/'procesos/caracterizacion/caracterizacion.py';sources[str(rp.relative_to(ROOT))]=sha(rp)
    tree=ast.parse(rp.read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'_clean_str','token_match_rut'}];assert len(nodes)==2
    scope={'pd':pd,'re':re};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(rp),'exec'),scope)
    fields=('RUT','CODCLI','CODCARPR','SEDE','JORNADA','ANOMATRICULA','ANOINGRESO','FECHANACIMIENTO','SEXO','ESTADOACADEMICO','SITUACION')
    da,_=read_sheet(sm['path'],sm['sheet'],fields)
    mr=list(csv.DictReader(mp.open()));index=defaultdict(list)
    for i,r in enumerate(mr):
        ym=birth(r['fec_nac_alu']);sx={'1':'M','2':'F'}.get(r['gen_alu']);y=year(r['cat_periodo'])
        if ym and sx and y and token(r['mrun']):index[y,ym,sx].append(i)
    types={'1':'Plan Regular','2':'Plan Especial','3':'Plan Regular de Continuidad'}
    items=[];steps=defaultdict(Counter);reverse=defaultdict(set);forward=defaultdict(set)
    for row in da:
        y=year(row['ANOMATRICULA'])
        if not y:continue
        person=scope['token_match_rut'](row['RUT']);cid=token(row['CODCLI'])
        ym=birth(row['FECHANACIMIENTO']);sx=token(row['SEXO']).upper()
        key=clave_grupo(token(row['CODCARPR']),token(row['SEDE']),token(row['JORNADA']));g=groups.get(key)
        valid=bool(person and cid and ym and sx in {'M','F'})
        a=index.get((y,ym,sx),[]) if valid else []
        b=[i for i in a if mr[i]['codigo_unico'].rsplit('V',1)[0] in g['familias']] if g else []
        typ={p[1] for p in g['perfiles_duracion_tipo']} if g else set()
        c=[i for i in b if mr[i]['tipo_plan_carr']==types.get(next(iter(typ)))] if len(typ)==1 else b
        for label,rr in [('A_demografia_anio',a),('B_familia_sin_version',b),('C_tipo_si_unanime',c)]:
            n=len({mr[i]['mrun'] for i in rr});status='SIN_DATOS_COMPARABLES' if not valid else ('SIN_GRUPO_CARRERA' if label!='A_demografia_anio' and not g else ('SIN_CANDIDATO' if n==0 else 'CANDIDATO_UNICO' if n==1 else 'VARIOS_CANDIDATOS'))
            steps[label][status]+=1
        ids={mr[i]['mrun'] for i in c}
        forward[y,person].update(ids)
        for m in ids:reverse[y,m].add(person)
        items.append((row,y,person,key,ids,c,valid,g,len(typ)==1))
    aggregate=Counter();status_totals=Counter();code_counts=Counter();cohort_check=Counter()
    for row,y,person,key,ids,rr,valid,g,type_applied in items:
        if not valid:status='SIN_DATOS_COMPARABLES'
        elif not g:status='SIN_GRUPO_CARRERA'
        elif not ids:status='SIN_CANDIDATO'
        elif len(ids)>1:status='VARIOS_CANDIDATOS'
        elif len(reverse[y,next(iter(ids))])>1 or len(forward[y,person])>1:status='UNICO_NO_RECIPROCO'
        else:status='UNICO_RECIPROCO_NO_CERTIFICADO'
        codes=sorted({mr[i]['codigo_unico'] for i in rr})
        code_state='UN_CODIGO_OBSERVADO' if len(codes)==1 else 'VARIOS_CODIGOS' if codes else 'SIN_CODIGO'
        aggregate[(token(row['CODCARPR']),token(row['SEDE']),token(row['JORNADA']),y,token(row['ESTADOACADEMICO']),token(row['SITUACION']),status,code_state,type_applied)]+=1
        status_totals[status]+=1
        if status=='UNICO_RECIPROCO_NO_CERTIFICADO':
            if len(codes)==1:code_counts[(token(row['CODCARPR']),y,codes[0])]+=1
            original=token(row['ANOINGRESO']);actual={mr[i]['anio_ing_carr_act'] for i in rr};orig={mr[i]['anio_ing_carr_ori'] for i in rr}
            cohort_check[('IGUAL_ACTUAL' if original in actual else 'DIFIERE_ACTUAL','IGUAL_ORIGINAL' if original in orig else 'DIFIERE_ORIGINAL')]+=1
    fieldsout=('codcarpr','sede','jornada','anio_observado','estado_umas','situacion_umas','estado_candidatura','codigos_candidatos','tipo_plan_aplicado')
    aggregates=[dict(zip(fieldsout,k),filas=v) for k,v in sorted(aggregate.items(),key=lambda kv:str(kv[0]))]
    res={'fuente_umas_filas':len(da),'fuente_mrun_filas':len(mr),'filas_umas_objetivo':len(items),'etapas':{k:dict(v) for k,v in steps.items()},'reciprocidad':dict(status_totals),'tasa_falsos_enlaces':'NO_ESTIMABLE_SIN_PARES_VALIDADOS','identidades_certificadas':0,'cohortes_entre_candidatos_reciprocos':[{'actual':k[0],'original':k[1],'filas':v} for k,v in sorted(cohort_check.items())]}
    outputs={'resumen.json':res,'candidaturas_por_carrera_estado.json':aggregates,'cilog.json':[r for r in aggregates if r['codcarpr']=='CILOG'],
      'codigos_observados_candidatos_reciprocos.json':[{'codcarpr':k[0],'anio':k[1],'codigo_sies_observado':k[2],'filas_umas_candidatas':v,'asignacion_certificada':False} for k,v in sorted(code_counts.items())]}
    assert sum(status_totals.values())==len(items)
    for p,h in sources.items():assert sha(Path(p) if Path(p).is_absolute() else ROOT/p)==h
    OUT.mkdir(parents=True,exist_ok=True)
    for n,v in outputs.items():(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
    (OUT/'manifest.json').write_text(json.dumps({'fuentes_sha256':sources,'script_sha256':sha(__file__),'salidas_sha256':{n:sha(OUT/n) for n in outputs},'identificadores_exportados':False},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(res,ensure_ascii=False))
if __name__=='__main__':main()
