#!/usr/bin/env python3
"""Diagnóstico agregado por carrera y cobertura completa CILOG; no asigna códigos."""
import ast
from collections import Counter,defaultdict
import csv,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.reconstruir_planes_umas import read_sheet,token
from common.versiones_por_cohorte import clave_grupo
OUT=ROOT/'data/diagnostico_cohortes_cilog/20261016'
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
def year(v):
    s=token(v)
    return int(s) if s.isdigit() and 2007<=int(s)<=2026 else None
def compact(c,fields):
    return [dict(zip(fields,k),cantidad=v) for k,v in sorted(c.items(),key=lambda kv:str(kv[0]))]
def main():
    import pandas as pd
    sources=load('data/continuidad_trayectoria/20261016/fuentes.json')['umas']
    tracked={}
    for k,v in sources.items():
        assert sha(v['path'])==v['sha256'],k
        tracked[v['path']]=v['sha256']
    groups=load('data/versiones_por_cohorte/20261016/grupos_existentes.json')
    histories=load('data/versiones_por_cohorte/20261016/historias_oferta.json')
    master=load('data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json')
    assert sha(ROOT/'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json')=='2ef459251e91ecebe5370402e3d2ea25341aeecbfb3ca54eca210cc347c392a5'
    package=load('data/versiones_por_cohorte/20261016/manifest.json')
    for n in ['grupos_existentes.json','historias_oferta.json']:
        p=ROOT/'data/versiones_por_cohorte/20261016'/n
        assert sha(p)==package['salidas'][n];tracked[str(p.relative_to(ROOT))]=sha(p)
    cp=ROOT/'data/versiones_historicas_sies_umas/fase_2_20261015/cohortes_observadas.tsv'
    assert sha(cp)==load('data/versiones_historicas_sies_umas/fase_2_20261015/manifest.json')['outputs'][cp.name]
    tracked[str(cp.relative_to(ROOT))]=sha(cp)
    cohorts=list(csv.DictReader(cp.open(),delimiter='\t'))
    rp=ROOT/'procesos/caracterizacion/caracterizacion.py'
    tree=ast.parse(rp.read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'_clean_str','token_match_rut'}]
    assert len(nodes)==2
    scope={'pd':pd,'re':re};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(rp),'exec'),scope)
    normalize=scope['token_match_rut']
    fields=('RUT','CODCLI','CODCARPR','NOMBRE_L','SEDE','JORNADA','ANOINGRESO','PERIODOINGRESO','ANOMATRICULA','PERIODOMATRICULA','FECHAMATRICULA','VIASDEADMISION','ESTADOACADEMICO')
    da,_=read_sheet(sources['alumnos']['path'],sources['alumnos']['sheet'],fields)
    fields2=('CODCLI','CODCARR','CARRERA','JORNADA','REGIMEN','ANO','PERIODO','PLAN_DE_ESTUDIO','DESCRIPCION_ESTADO','CONVALIDADO','NIVEL')
    prom,_=read_sheet(sources['promedios']['path'],sources['promedios']['sheet'],fields2)
    academic=defaultdict(list);by_person=defaultdict(list);owners=defaultdict(set)
    for r in da:
        r['_persona']=normalize(r['RUT'])
        if r['_persona']:by_person[r['_persona']].append(r)
        if token(r['CODCLI']) and r['_persona']:owners[token(r['CODCLI'])].add(r['_persona'])
    for r in prom:
        if token(r['CODCLI']) and token(r['CODCARR']):academic[token(r['CODCLI']),token(r['CODCARR'])].append(r)
    def valid(r):return token(r['DESCRIPCION_ESTADO']).upper() in {'APROBADO','REPROBADO'} and token(r['CONVALIDADO']).upper() not in {'S','SI','SÍ','1','TRUE'} and year(r['ANO']) is not None
    by_group=defaultdict(list)
    for r in da:by_group[clave_grupo(token(r['CODCARPR']),token(r['SEDE']),token(r['JORNADA']))].append(r)
    summary=[]
    for g in groups:
        rows=by_group[g['clave']];target=[r for r in rows if year(r['ANOMATRICULA'])]
        hh=[h for h in histories if h['familia'] in g['familias']]
        types={p[1] for p in g['perfiles_duracion_tipo']}
        relevant=[h for h in hh if any(a['tipo_plan'] in types for a in h['anual'])]
        summary.append({'codcarpr':g['codcarpr'],'sede':g['sede'],'jornada':g['jornada'],'nombres_umas':sorted({token(r['NOMBRE_L']) for r in rows}),
          'perfiles':g['perfiles_duracion_tipo'],'filas_umas_hasta_2026':len(target),'codcli_distintos_hasta_2026':len({token(r['CODCLI']) for r in target if token(r['CODCLI'])}),
          'ofertas_mismo_tipo_plan':[{'codigo_unico':h['codigo_unico'],'inicio':h['inicio_oferta'],'perfiles':sorted({(a['duracion_total'],a['tipo_plan']) for a in h['anual']})} for h in relevant],
          'advertencia':'Tipo de plan común no acredita equivalencia histórica por sí solo.'})
    cilog=[r for r in da if token(r['CODCARPR'])=='CILOG'];target=[r for r in cilog if year(r['ANOMATRICULA'])]
    sample=Counter();activity=Counter();sample_cases=defaultdict(set);owncodes={token(r['CODCLI']) for r in target}
    for r in target:
        cid=token(r['CODCLI']);obs=academic[cid,'CILOG'];usable=[x for x in obs if valid(x)]
        ay=sorted({year(x['ANO']) for x in usable});plans=sorted({token(x['PLAN_DE_ESTUDIO']) for x in obs if token(x['PLAN_DE_ESTUDIO'])})
        other=sorted({token(x['CODCARPR']) for x in by_person[r['_persona']] if token(x['CODCLI'])!=cid and token(x['CODCARPR'])!='CILOG'}) if r['_persona'] and len(owners[cid])==1 else []
        date=token(r['FECHAMATRICULA']);date_year=re.search(r'(?:19|20)\d{2}',date)
        k=(token(r['SEDE']),token(r['JORNADA']),token(r['ANOINGRESO']),token(r['ANOMATRICULA']),date_year.group() if date_year else '',ay[0] if ay else None,','.join(map(str,ay)),','.join(plans),','.join(other),token(r['VIASDEADMISION']))
        sample[k]+=1;sample_cases[k].add(cid)
    samples=compact(sample,['sede','jornada','anoingreso','anomatricula','anio_fecha_matricula','primera_actividad_propia','anios_actividad_propia','planes_reportados','otras_carreras_otro_codcli','via_admision'])
    for row,(_,ids) in zip(samples,sorted(sample_cases.items(),key=lambda kv:str(kv[0]))):row['codcli_distintos']=len(ids)
    for r in prom:
        if token(r['CODCARR'])=='CILOG':
            k=(token(r['ANO']),token(r['PERIODO']),token(r['PLAN_DE_ESTUDIO']),token(r['DESCRIPCION_ESTADO']),token(r['CONVALIDADO']),token(r['NIVEL']),token(r['CODCLI']) in owncodes)
            activity[k]+=1
    trajectory_patterns=Counter()
    for person in sorted({r['_persona'] for r in target if r['_persona']}):
        rr=by_person[person]
        if len({token(r['CODCLI']) for r in rr})<2:continue
        detail=[]
        for r in rr:
            cid=token(r['CODCLI']);career=token(r['CODCARPR'])
            obs=academic[cid,career];usable=[x for x in obs if valid(x)]
            detail.append({'carrera':career,'ingreso':token(r['ANOINGRESO']),'matricula':token(r['ANOMATRICULA']),
              'estado_academico_literal':token(r['ESTADOACADEMICO']),
              'actividad_observada':sorted({year(x['ANO']) for x in usable}),
              'planes':sorted({token(x['PLAN_DE_ESTUDIO']) for x in obs if token(x['PLAN_DE_ESTUDIO'])})})
        trajectory_patterns[json.dumps(sorted(detail,key=lambda x:json.dumps(x,sort_keys=True)),ensure_ascii=False,sort_keys=True)]+=1
    trajectories=[{'expedientes':json.loads(k),'personas':v} for k,v in sorted(trajectory_patterns.items())]
    tp=ROOT/'data/versiones_historicas_sies_umas/fase_2_20261015/transiciones_observadas.tsv'
    assert sha(tp)==load('data/versiones_historicas_sies_umas/fase_2_20261015/manifest.json')['outputs'][tp.name]
    tracked[str(tp.relative_to(ROOT))]=sha(tp)
    transitions=[r for r in csv.DictReader(tp.open(),delimiter='\t') if 'C77J' in r['codigos_anteriores'] or 'C77J' in r['codigos_siguientes']]
    cilog_cohorts=[r for r in cohorts if r['codigo_unico'].startswith('I162S2C77')]
    annual=[r for r in master['mrun_anual'] if r['cod_carrera']=='77']
    # Coexistencia real en el mismo corte y familia: conserva tipo, duración y cohortes.
    fam_year=defaultdict(list)
    for r in cohorts:
        m=re.fullmatch(r'(I\d+S\d+C\d+J\d+)V\d+',r['codigo_unico'])
        if m:fam_year[r['cat_periodo'],m[1],r['tipo_plan_carr']].append(r)
    coexist=[]
    for (y,fam,typ),rr in sorted(fam_year.items()):
        codes=sorted({r['codigo_unico'] for r in rr})
        if len(codes)<2:continue
        starts={h['codigo_unico']:h['inicio_oferta'] for h in histories if h['codigo_unico'] in codes}
        coexist.append({'anio_observacion':y,'familia':fam,'tipo_plan':typ,'codigos':codes,'inicios_oferta':starts,
          'detalle':[{'codigo':c,'duraciones':sorted({r['dur_total_carr'] for r in rr if r['codigo_unico']==c}),
          'nombre':sorted({r['nomb_carrera'] for r in rr if r['codigo_unico']==c}),
          'cohortes_actuales':sorted({r['anio_ing_carr_act'] for r in rr if r['codigo_unico']==c}),
          'cohortes_originales':sorted({r['anio_ing_carr_ori'] for r in rr if r['codigo_unico']==c}),
          'filas_mrun':sum(int(r['filas_matricula']) for r in rr if r['codigo_unico']==c)} for c in codes]})
    res={'filas_cilog_datosalumnos_todas':len(cilog),'filas_cilog_hasta_2026':len(target),'codcli_cilog_hasta_2026':len(owncodes),
      'personas_cilog_hasta_2026':len({r['_persona'] for r in target if r['_persona']}),'filas_cilog_fuera_corte':len(cilog)-len(target),
      'filas_promedios_cilog':sum(activity.values()),'estratos_muestra':len(samples),'muestra':'Todas las filas CILOG disponibles, agrupadas sin identidades.',
      'grupos_carrera_revisados':len(summary),'coexistencias_mismo_tipo_plan':len(coexist),'enlace_individual_mrun_umas':'NO_ACREDITADO',
      'anoingreso_cilog':dict(Counter(token(r['ANOINGRESO']) for r in target)),
      'primera_actividad_propia_cilog':dict(sum((Counter({str(s['primera_actividad_propia']):s['cantidad']}) for s in samples),Counter())),
      'estados_academicos_cilog':dict(Counter(token(r['ESTADOACADEMICO']) for r in target)),
      'personas_con_varios_expedientes':sum(trajectory_patterns.values())}
    state_counts=Counter((token(r['ANOINGRESO']),token(r['ANOMATRICULA']),token(r['ESTADOACADEMICO']),bool([x for x in academic[token(r['CODCLI']),'CILOG'] if valid(x)])) for r in target)
    outputs={'cilog_estados_por_cohorte.json':compact(state_counts,['anoingreso','anomatricula','estado_literal','actividad_propia_observada']),'cilog_trayectorias_multiexpediente.json':trajectories,'logistica_transiciones_mrun.json':transitions,'resumen.json':res,'carreras.json':summary,'cilog_muestra_completa_agrupada.json':samples,
      'cilog_actividad_por_plan_periodo.json':compact(activity,['anio','periodo','plan','estado','convalidado','nivel','codcli_en_datosalumnos_hasta_2026']),
      'logistica_cohortes_mrun.json':cilog_cohorts,'logistica_anual_mrun.json':annual,
      'logistica_oferta.json':[h for h in histories if h['familia'].startswith('I162S2C77J')],
      'coexistencias_mismo_tipo_plan.json':coexist}
    for p,h in tracked.items():assert sha(Path(p) if Path(p).is_absolute() else ROOT/p)==h,p
    OUT.mkdir(parents=True,exist_ok=True)
    for name,obj in outputs.items():
        raw=json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n';p=OUT/name
        p.write_text(raw)
    tracked['data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json']=sha(ROOT/'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json')
    tracked[str(rp.relative_to(ROOT))]=sha(rp)
    (OUT/'manifest.json').write_text(json.dumps({'fuentes_sha256':tracked,'script_sha256':sha(__file__),'salidas_sha256':{n:sha(OUT/n) for n in outputs},'identificadores_exportados':False},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(res,ensure_ascii=False))
if __name__=='__main__':main()
