#!/usr/bin/env python3
"""Prueba de enlace global, totales y cohorte; referencia documental solo al evaluar."""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.fuentes_ensayo_enlace_conjunto import cargar_ensayo, doc, dateym, token, year, sha, YEARS
from common.versiones_por_cohorte import clave_grupo
from common.enlace_conjunto import solve
OUT = ROOT/'data/hipotesis_enlace_conjunto/20261016'


def build_graphs(da, mr, groups):
    """No acepta referencias documentales ni su resolución de identidad."""
    index = defaultdict(list)
    for r in mr:
        if r['birth'] and r['sex'] and r['mrun']:
            index[r['year'], r['birth'], r['sex']].append(r)
    graphs = {v: {y: defaultdict(set) for y in YEARS} for v in ('base','cohorte_original')}
    rows_by_person = defaultdict(list)
    control = {side: defaultdict(set) for side in ('umas','mrun')}
    demographics = {side: defaultdict(set) for side in ('umas','mrun')}
    quality = Counter()
    for r in mr:
        key = (r['year'], r['code'].rsplit('V',1)[0], r['ori'], r['sex'] or 'NO_COMPARABLE')
        control['mrun'][key].add(r['mrun'])
        demographics['mrun'][key+(r['birth'],)].add(r['mrun'])
    for r in da:
        y, p = year(r['ANOMATRICULA']), doc(r['RUT'])
        if y not in YEARS: continue
        if not p:
            quality['filas_sin_documento_normalizable'] += 1
            continue
        rows_by_person[y,p].append(r)
        for v in graphs: graphs[v][y][p]
        g = groups.get(clave_grupo(token(r['CODCARPR']), token(r['SEDE']), token(r['JORNADA'])))
        if not g:
            quality['filas_sin_grupo'] += 1
            continue
        sx, birth = token(r['SEXO']).upper(), dateym(r['FECHANACIMIENTO'])
        ori = token(r['ANOINGRESO'])
        if len(g['familias']) != 1: quality['filas_familia_multiple'] += 1
        for fam in g['familias']:
            key = (y, fam, ori, sx if sx in {'M','F'} else 'NO_COMPARABLE')
            control['umas'][key].add(p)
            demographics['umas'][key+(birth,)].add(p)
        if sx not in {'M','F'} or not birth:
            quality['filas_demografia_no_comparable'] += 1
            continue
        for c in index.get((y,birth,sx),[]):
            if c['code'].rsplit('V',1)[0] not in g['familias']: continue
            graphs['base'][y][p].add(c['mrun'])
            # Marcadores SIES no se convierten en años. No compara ingreso actual.
            uy, my = year(ori), year(c['ori'])
            if uy is None or my is None or uy == my:
                graphs['cohorte_original'][y][p].add(c['mrun'])
    panels = []
    for k in sorted(control['umas'].keys() | control['mrun'].keys()):
        a, b = len(control['umas'][k]), len(control['mrun'][k])
        dk = {kk for side in demographics.values() for kk in side if kk[:4] == k}
        panels.append(dict(zip(('anio','familia_sin_version','ingreso_original_declarado','sexo_normalizado'),k),
                           personas_umas=a, personas_mrun=b, diferencia=a-b,
                           total_igual=a==b,
                           distribucion_nacimiento_igual=all(len(demographics['umas'][kk])==len(demographics['mrun'][kk]) for kk in dk)))
    return graphs, rows_by_person, panels, dict(quality)


def main():
    d = cargar_ensayo()
    graphs, personrows, panels, quality = build_graphs(d['da'], d['mr'], d['groups'])
    solutions, summaries, components_out = {}, {}, []
    for variant, annual in graphs.items():
        forced_all, stats = {}, Counter()
        for y, graph in sorted(annual.items()):
            forced, components = solve(graph)
            forced_all.update({(y,p):m for p,m in forced.items()})
            reverse = Counter(m for ids in graph.values() for m in ids)
            reciprocal = {p:next(iter(ids)) for p,ids in graph.items() if len(ids)==1 and reverse[next(iter(ids))]==1}
            stats.update({'personas_anio_umas':len(graph), 'sin_candidato':sum(not ids for ids in graph.values()),
                          'candidato_unico_local':sum(len(ids)==1 for ids in graph.values()),
                          'unico_reciproco':len(reciprocal), 'forzado_condicional':len(forced),
                          'resuelto_adicional_por_asignacion_conjunta':len(set(forced)-set(reciprocal)),
                          'maximo_pares':sum(c['maximo_pares'] for c in components)})
            for c in components: components_out.append(dict(variante=variant, anio=y, **c))
        solutions[variant] = forced_all
        summaries[variant] = dict(stats)
    cases = []
    mr_codes = defaultdict(set)
    for r in d['mr']: mr_codes[r['year'],r['mrun']].add(r['code'])
    evaluation = {v:Counter() for v in graphs}
    for n,p in enumerate(d['sample'],1):
        anchor = d['anchors'][p]; y = int(anchor['ANOMATRICULA'])
        target = d['adjudicated'].get((y,p))
        result = {'caso':f'ENSAYO-{n:03d}', 'anio_ancla':y, 'codcarpr':token(anchor['CODCARPR']), 'variantes':{}}
        for v in graphs:
            ids = graphs[v][y][p]; chosen = solutions[v].get((y,p))
            if not chosen: status = 'SIN_ENLACE_FORZADO'
            elif not target: status = 'ENLACE_SIN_REFERENCIA_UNIVOCA'
            elif chosen == target: status = 'CONCUERDA_CON_REFERENCIA'
            else: status = 'CONTRADICE_REFERENCIA'
            evaluation[v][status] += 1
            result['variantes'][v] = {'candidatos_persona_anio':len(ids), 'enlace_forzado_condicional':bool(chosen), 'evaluacion':status, 'codigos_sies_del_candidato':sorted(mr_codes.get((y,chosen),set())), 'codigos_referencia_reservada':sorted(mr_codes.get((y,target),set()))}
        cases.append(result)
    assert len(cases)==500 and len(d['sample'])==len(set(d['sample']))
    previous = json.loads((ROOT/'data/prueba_500_enlaces_historicos/20261016/casos_500_sin_identificadores.json').read_text())
    academic_sample_equal = [(r['caso'],r['anio_ancla'],r['codcarpr']) for r in cases] == [(r['caso'],r['anio_ancla'],r['codcarpr']) for r in previous]
    annual_totals = []
    for y in sorted(YEARS):
        rr = [r for r in d['mr'] if r['year']==y]
        ur = [r for (yy,p),rows in personrows.items() if yy==y for r in rows]
        annual_totals.append({'anio':y,'personas_umas':len(graphs['base'][y]),'filas_umas':len(ur),
                              'personas_mrun':len({r['mrun'] for r in rr}), 'filas_mrun':len(rr)})
    # Estabilidad entre años es control interno, no una referencia independiente.
    longitudinal = {}
    for v, solution in solutions.items():
        histories = defaultdict(list)
        for (y,p),m in solution.items(): histories[p].append(m)
        longitudinal[v] = dict(Counter('MISMO_MRUN' if len(set(ids))==1 else 'MRUN_DISTINTO' for ids in histories.values() if len(ids)>1))
    summary = {'muestra_personas':500, 'estratos_muestra':dict(Counter(r['anio_ancla'] for r in cases)), 'referencias_resueltas_muestra':sum((int(d['anchors'][p]['ANOMATRICULA']),p) in d['adjudicated'] for p in d['sample']), 'fuente_umas_original':d['original_source'], 'fuente_umas_utilizada':d['sm'], 'coincidencia_metadatos_muestra_previa':academic_sample_equal, 'mismas_identidades_500_acreditadas':False, 'anios':sorted(YEARS), 'totales_por_anio':annual_totals,
               'universos_no_acreditados_como_equivalentes':True, 'resultados':summaries,
               'evaluacion_500':{v:dict(c) for v,c in evaluation.items()},
               'control_longitudinal_interno':longitudinal, 'calidad_umas':quality,
               'paneles_cohorte_sexo_familia':len(panels),
               'paneles_totales_iguales':sum(p['total_igual'] for p in panels),
               'paneles_totales_y_distribucion_nacimiento_iguales':sum(p['total_igual'] and p['distribucion_nacimiento_igual'] for p in panels),
               'estado':'HIPOTESIS_DIAGNOSTICA_NO_ACTIVADA',
               'alcance':'Máxima cardinalidad condicional; referencia documental indirecta, no identidad oficial. Sin filtro de tipo actual. Familias con varias carreras no acreditan separación de continuidad.'}
    for path,h in d['sources'].items(): assert sha(Path(path) if Path(path).is_absolute() else ROOT/path)==h
    preservation = json.loads((ROOT/'data/unificacion_proyectos/20261015/control_preservacion_final.json').read_text())
    refs = preservation['referencias_sha256']
    for p,h in refs.items(): assert sha(ROOT/p)==h, p
    delivery = json.loads((ROOT/'data/versiones_historicas_sies_umas/fase_8_20261015/entrega.json').read_text())
    assert sha(delivery['archivo'])=='f6431d9bf571a4db0769cf8f4d5b90eee95413477406ddf9a328e657a85298dd'
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = {'resumen.json':summary, 'casos_500.json':cases, 'totales_cohortes.json':panels, 'componentes.json':components_out,
               'qa.json':{'muestra_500_personas_distintas':True, 'misma_regla_seleccion':True, 'coincidencia_metadatos_muestra_previa':academic_sample_equal,'referencias_preservadas':len(refs),'excel_usuario_intacto':True,'identificadores_exportados':False}}
    for name,value in outputs.items(): (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    sources = dict(d['sources'])
    for p in ('scripts/diagnosticar_enlace_conjunto.py','scripts/fuentes_ensayo_enlace_conjunto.py','common/enlace_conjunto.py','tests/test_enlace_conjunto.py'):
        sources[p] = sha(ROOT/p)
    (OUT/'manifest.json').write_text(json.dumps({'fuentes_y_codigo_sha256':sources,'salidas_sha256':{name:sha(OUT/name) for name in outputs}},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__ == '__main__': main()
