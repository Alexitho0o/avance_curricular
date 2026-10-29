#!/usr/bin/env python3
"""H002h: cohortes derivadas y diagnóstico agregado; no adjudica ni modifica fuentes."""
import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DATA = ROOT / 'data/paridad_codigo_sies/cohorte_2007_2026_v2'
PRIVATE = Path.home() / '.local/share/ipss/h002h_20261029'
sys.path.insert(0, str(ROOT / 'outputs/paridad_cohorte_2007_2026'))
from construir_cohortes import (sha, js, read, txt, number, ident, umas_ident,
                               family, selected, sheet_rows, codigo, cohort,
                               solve, csvbytes)


def derive_cohort(row, first):
    """La vía c sólo deriva año; nunca inventa un semestre."""
    year = int(row['cat_periodo'])
    for via, suffix in [('a', 'act'), ('b', 'ori')]:
        cy, sem = cohort(row['anio_ing_carr_' + suffix], row['sem_ing_carr_' + suffix], year)
        if cy is not None:
            return cy, sem, via
    if first is not None and first >= 2008:
        return first, 'NO_OBSERVADO', 'c'
    if first == 2007:
        return None, 'NO_OBSERVADO', 'censurada'
    return None, 'NO_OBSERVADO', 'sin_identificador'


def partition(rows, attribute):
    """Cobertura y univocidad, sin usar mayoría ni ignorar las excepciones."""
    codes = defaultdict(set)
    known = 0
    unknown = 0
    for r in rows:
        value = r[attribute]
        if value in ('', 'SIN_DATO', 'NO_ACREDITADO_E', 'NO_COMPROBABLE_E'):
            unknown += r['matriculas']
        else:
            codes[value].add(r['codigo_sies'])
            known += r['matriculas']
    conflicts = {k: sorted(v) for k, v in codes.items() if len(v) > 1}
    deterministic = bool(codes) and not conflicts and len({c for v in codes.values() for c in v}) > 1
    explained = deterministic and unknown == 0
    informative = sum(r['matriculas'] for r in rows if r[attribute] in codes and len(codes[r[attribute]]) == 1)
    return {'explicado': explained, 'conocidas': known, 'sin_dato': unknown,
            'determinista_conocido': deterministic, 'conflictos': conflicts,
            'filas_con_valor_univoco': informative,
            'regla_observada': {k: sorted(v) for k, v in sorted(codes.items())}}


def split_classification(rows):
    form = partition(rows, 'forma_ingreso')
    title = partition(rows, 'tecnico_previo_titulado')
    if form['explicado']:
        state = 'EXPLICADO_POR_FORMA_INGRESO'
    elif title['explicado']:
        state = 'EXPLICADO_POR_ARTICULACION'
    elif form['filas_con_valor_univoco'] or title['filas_con_valor_univoco']:
        state = 'PARCIAL'
    else:
        state = 'NO_EXPLICADO'
    return state, form, title


def fixed_allowed(state, plans, flags, censored):
    return (state == 'CUADRA_EXACTO' and bool(plans) and not censored
            and all(v == 'PERFIL_FORMAL_COMPATIBLE' for v in flags.values())
            and all('PLAN_NO_OBSERVADO' not in k and 'PLAN_MULTIPLE' not in k for k in plans))


def build():
    sources = read(OUT / 'FUENTES.json')
    for entry in sources:
        if sha(entry['ruta']) != entry['sha256']:
            raise ValueError('Fuente alterada: ' + entry['id'])
    src = {e['id']: Path(e['ruta']) for e in sources}
    old_hist = read(src['outputs/paridad_cohorte_2007_2026/CUADRATURA_2007_2021.json'])['cohortes']
    old_validation = read(src['outputs/paridad_cohorte_2007_2026/VALIDACION_95_H002_v2.json'])['codigos']
    old_rules = read(src['data/paridad_codigo_sies/cohorte_2007_2026/REGLAS_VERSION_POR_COHORTE.json'])['reglas']
    detail = read(src['enlaces_h002g_privados'])
    # Dato personal proyectado en memoria. No se seleccionan nacimiento ni nombres.
    fields = ['cat_periodo', 'codigo_unico', 'mrun', 'anio_ing_carr_act', 'sem_ing_carr_act',
              'anio_ing_carr_ori', 'sem_ing_carr_ori', 'tipo_plan_carr', 'dur_total_carr',
              'forma_ingreso', 'nivel_global']
    with src['sies_individual'].open(encoding='utf-8-sig') as f:
        micro = [{k: r[k] for k in fields} for r in csv.DictReader(f)]
    first = {}
    trajectories = defaultdict(lambda: defaultdict(set))
    for r in micro:
        if r['mrun']:
            key = (r['mrun'], family(r['codigo_unico']))
            y = int(r['cat_periodo'])
            first[key] = min(y, first.get(key, y))
            trajectories[key][y].add(r['codigo_unico'])
    matrix = Counter()
    ways = defaultdict(Counter)
    profiles = defaultdict(set)
    new = defaultdict(Counter)
    forms = defaultdict(Counter)
    mc = Counter()
    censored = Counter()
    sies_split_counts = Counter()
    entrants = defaultdict(set)
    for r in micro:
        y = int(r['cat_periodo']); c = r['codigo_unico']; f = family(c)
        cy, sem, via = derive_cohort(r, first.get((r['mrun'], f)))
        ways[y][via] += 1; mc[y, c] += 1
        matrix[y, c, cy, sem, via, txt(r['anio_ing_carr_ori']), txt(r['sem_ing_carr_ori'])] += 1
        profiles[y, c].add((txt(r['dur_total_carr']), '3' if r['tipo_plan_carr'] == 'Plan Regular de Continuidad' else '1'))
        if via == 'censurada': censored[y, f] += 1
        form = txt(r['forma_ingreso']) or 'SIN_DATO'
        sies_split_counts[f, cy, sem, y, c, form, via] += 1
        if cy == y and r['nivel_global'] == 'Pregrado':
            new[y, f][c] += 1; forms[y, c][form] += 1
            if r['mrun']: entrants[y, f, c].add(r['mrun'])
    public = {}; public_first = Counter(); technical_codes = set()
    with src['Matricula_2007_2026_WEB_10_07_2026.csv'].open(encoding='latin1') as f:
        for r in csv.DictReader(f, delimiter=';'):
            if r['CÓDIGO DE INSTITUCIÓN'] != '162': continue
            y = int(r['AÑO'].removeprefix('MAT_')); c = r['CÓDIGO CARRERA']
            public[y, c] = int(r['TOTAL MATRÍCULA'])
            if r['NIVEL GLOBAL'] == 'Pregrado': public_first[y] += number(r['TOTAL MATRÍCULA PRIMER AÑO']) or 0
            # Clasificación técnica textual de la publicación, no prefijo CODCARPR.
            if any('Técnico de Nivel Superior' == txt(v) for v in r.values()): technical_codes.add(c)
    controls = [{'anio': y, 'codigo_sies': c, 'registro': mc[y, c], 'publicacion': public.get((y, c), 0),
                 'diferencia': mc[y, c] - public.get((y, c), 0)}
                for y, c in sorted(set(mc) | {k for k in public if k[0] <= 2025})]
    assert all(r['diferencia'] == 0 for r in controls)
    print('Control SIES completo: cero diferencias', flush=True)
    # Perfiles y grupos congelados; no se descubren equivalencias por nombre.
    groups = read(src['data/versiones_por_cohorte/20261028/grupos_existentes.json'])
    master = read(src['data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json'])
    fam = defaultdict(set)
    for g in groups:
        for f in g['familias']: fam[f].add((g['codcarpr'], g['sede'], g['jornada']))
    for g in master['equivalencias_programa_2026']:
        fam[family(g['codigo_unico'])].add((g['codcarpr'], g['sede_umas'], g['jornada_umas']))
    formal = defaultdict(set)
    for p in read(src['outputs/paridad_codigo_sies_20261029/PERFIL_PLANES_H002C.json'])['perfiles']:
        for v in p['perfil_formal_H112B']:
            formal[p['codcarpr'], p['CODPESTUD']].add((txt(v['semestres']), txt(v['tipo_plan_codigo'])))
    # Leer sólo el mayor extracto para indicadores de cobertura y evidencia de expediente.
    da = defaultdict(list); internal_all = defaultdict(set); da_exact = defaultdict(list)
    df = ['CODCLI', 'CODCARPR', 'SEDE', 'JORNADA', 'RUT', 'ANOINGRESO', 'PERIODOINGRESO',
          'ESTADOACADEMICO', 'SITUACION', 'ANOMATRICULA', 'FECHAMATRICULA']
    for line, r in sheet_rows(src['DATOSDEALUMNOS_12159.xlsx'], 'Hoja1', df):
        pe = umas_ident(r); iy = number(r['ANOINGRESO'])
        if iy and r['CODCLI']: internal_all[iy].add(r['CODCLI'])
        if pe:
            da[pe].append(r); da_exact[pe, r['CODCLI']].append(r)
    # PES contiene título por persona y código, no expediente. Vincular sólo con
    # un expediente DA compatible único, de la familia técnica documentada.
    titles = defaultdict(list)
    with src['PES_5319'].open(encoding='latin1') as f:
        for r in csv.DictReader(f, delimiter=';'):
            pe = ident(r['TIPO_DOCUMENTO'], r['NUM_DOCUMENTO'], r['DV'])
            ty = number(r['AÑO_TITULACION']); code = r['COD_UNICO_OBT_TIT']
            if not code.startswith('I'): code = 'I' + code
            if pe and ty and code in technical_codes:
                candidates = {d['CODCLI'] for d in da[pe] if (d['CODCARPR'], d['SEDE'], d['JORNADA']) in fam[family(code)]}
                if len(candidates) == 1:
                    titles[pe].append((next(iter(candidates)), ty))
    def articulation(pe, cli, cy):
        if not cy: return 'NO_COMPROBABLE_E'
        for old_cli, ty in titles[pe]:
            if old_cli != cli and ty < cy and any(number(d['ANOINGRESO']) is not None and number(d['ANOINGRESO']) < cy for d in da_exact[pe, old_cli]):
                return 'SI'
        return 'NO_ACREDITADO_E'
    # Historia: mismos conteos internos H002g, nuevo lado SIES derivado.
    old_by = {(r['anio'], r['familia']): r for r in old_hist}
    hist = []; fixed = []; historical_rows = []; causes = Counter(); annual = []
    hist_keys = sorted(set(old_by) | {k for k in new if 2007 <= k[0] <= 2021})
    for y, f in hist_keys:
        old = old_by.get((y, f), {})
        ints = old.get('interno_ingreso_anio', {}); target = dict(new[y, f]); compat = {}; flags = {}
        for k in ints:
            ca, pl, _, _ = k.split('|'); pf = formal[ca, pl]
            compat[k] = [c for c in sorted(target) if not pf or pf & profiles[y, c]]
            flags[k] = 'PERFIL_FORMAL_COMPATIBLE' if pf else 'PERFIL_NO_ACREDITADO'
        state, solutions, size = solve(ints, target, compat)
        fix = fixed_allowed(state, ints, flags, censored[y, f])
        c_count = sum(n for (yy, cc, cy, ss, v, oy, os), n in matrix.items() if yy == y and cy == y and family(cc) == f and v == 'c')
        second = sum(n for (yy, cc, cy, ss, v, oy, os), n in matrix.items() if yy == y and cy == y and family(cc) == f and ss == '2')
        carriers = {x[0] for x in fam[f]}
        migration = set()
        for pe, rows in da.items():
            for d in rows:
                if d['CODCARPR'] not in carriers or number(d['ANOINGRESO']) != y: continue
                if any(o['CODCLI'] != d['CODCLI'] and o['CODCARPR'] in carriers and number(o['ANOINGRESO']) is not None and number(o['ANOINGRESO']) < y for o in rows):
                    migration.add(d['CODCLI'])
        indicators = {
            'cohorte_via_c_matriculas': c_count,
            'segundo_semestre_sies_matriculas': second,
            'expedientes_nuevos_con_otro_previo_misma_familia': len(migration),
            'diferencia_interno_menos_sies': sum(ints.values()) - sum(target.values()),
            'ingreso_despues_30_abril': 'E: sin fecha de primer ingreso; FECHAMATRICULA de foto no acredita corte histórico',
            'integridad_extracto_interno': 'E: foto 12159 no certifica expedientes de cohortes históricas',
            'familia_con_equivalencia_gobernada': bool(fam[f]),
            'cambio_plan': 'E: otro expediente anterior es indicio, no bitácora de migración',
            'forma_ingreso': 'E: no hay vía UMAS histórica homologada por plan; se conserva distribución SIES sin desempate supuesto'}
        probable = []
        if c_count: probable.append('COHORTE_PRIMERA_OBSERVACION')
        if migration: probable.append('POSIBLE_CAMBIO_PLAN_EXPEDIENTE_POSTERIOR')
        if second: probable.append('SEGUNDO_SEMESTRE_OBSERVADO')
        probable.append('COBERTURA_INTERNA_NO_CERTIFICADA' if fam[f] else 'FAMILIA_SIN_EQUIVALENCIA_GOBERNADA')
        if state == 'NO_CUADRA': causes.update(probable)
        rec = {'anio': y, 'familia': f, 'estado_antes': old.get('estado', 'NO_COMPARADO'),
               'estado': state, 'sies_cohorte_derivada': target, 'interno_ingreso_anio': ints,
               'periodos_umas': old.get('periodos_umas', {}), 'formas_sies': {c: dict(sorted(forms[y, c].items())) for c in target},
               'candidatos_por_plan': compat, 'perfiles': flags, 'asignaciones': solutions,
               'combinaciones_evaluables': size, 'cohorte_censurada_filas': censored[y, f],
               'fijacion': 'FIJADA_C' if fix else 'NO_FIJADA_E', 'causas_probables_E': probable if state == 'NO_CUADRA' else [],
               'indicadores_causa': indicators, 'clase': 'C/E',
               'alcance': 'familia × año; semestres SIES y períodos UMAS separados; igualdad no prueba identidad'}
        hist.append(rec)
        if fix:
            for k, c in solutions[0]['asignacion'].items():
                fixed.append({'anio_cohorte': y, 'familia': f, 'plan_contexto': k, 'codigo_fijado': c, 'estado': 'FIJADA_C'})
        for k, n in ints.items():
            historical_rows.append({'anio': y, 'familia': f, 'plan_contexto': k, 'expedientes': n,
                                    'codigos_candidatos': compat[k], 'estado': state, 'fijacion': rec['fijacion']})
    carry = Counter()
    for fix in fixed:
        y, f, c = fix['anio_cohorte'], fix['familia'], fix['codigo_fijado']
        for pseudonym in entrants[y, f, c]:
            for later, codes in trajectories[pseudonym, f].items():
                if later <= y: continue
                status = 'MANTIENE' if codes == {c} else 'CAMBIO_DE_CODIGO'
                carry[y, f, fix['plan_contexto'], c, later, '|'.join(sorted(codes)), status] += 1
    carry_rows = [dict(zip(['cohorte', 'familia', 'plan_contexto', 'codigo_fijado', 'anio_observado', 'codigos_observados', 'estado'], k), matriculas=n)
                  for k, n in sorted(carry.items())]
    # Descartar MRUN: sólo se conservan contadores y distribuciones agregadas.
    del micro, first, trajectories, entrants
    for y in range(2007, 2022):
        hh = [r for r in hist if r['anio'] == y]
        annual.append({'anio': y, 'interno_total_expedientes_anoingreso': len(internal_all[y]),
                       'interno_familias_mapeadas': sum(sum(r['interno_ingreso_anio'].values()) for r in hh),
                       'sies_cohorte_derivada_ingresa_en_anio': sum(sum(r['sies_cohorte_derivada'].values()) for r in hh),
                       'sies_primer_anio_publicado': public_first[y],
                       'nota': 'Universos separados; ingreso derivado no equivale automáticamente al indicador público de primer año'})
    print('Cuadratura histórica terminada; identidades SIES descartadas', flush=True)
    # Enlaces exactamente H002g. Cada fila privada debe coincidir con la MU original.
    detail_by = {r['fila_fuente_mu']: r for r in detail}
    mu_path = next(p for k, p in src.items() if k.startswith('BASE_RETENCION_MATRICULA'))
    mfields = ['ANIO_INFORMADO','TIPO_DOC','N_DOC','DV','COD_SED','COD_CAR','JOR','VERSION','VIG','ANIO_ING_ACT','SEM_ING_ACT','FOR_ING_ACT']
    mu_counts = Counter(); personal = []; observed_plans = defaultdict(lambda: defaultdict(set)); mu_total = Counter()
    for line, r in sheet_rows(mu_path, 'BASE_RETENCION_MU', mfields):
        prior = detail_by[line]; y = number(r['ANIO_INFORMADO']); c = codigo(r); pe = ident(r['TIPO_DOC'], r['N_DOC'], r['DV'])
        assert prior['anio'] == y and prior['codigo_sies'] == c and prior['identidad'] == (list(pe) if pe else None)
        assert prior['incluida'] == selected(y, r['VIG'])
        mu_total[y, c, prior['incluida']] += 1
        if not prior['incluida'] or not prior['seleccion']: continue
        cli, ca, s, j, iy, period = prior['seleccion']; cy, sem = prior['cohorte_sies']; pl = prior['plan']
        title = articulation(pe, cli, cy)
        form = txt(r['FOR_ING_ACT']) or 'SIN_DATO'
        mu_counts[family(c), ca, pl, s, j, cy, sem, y, c, form, title] += 1
        observed_plans[cli, family(c), cy, sem][y].add(pl)
        personal.append({'fila_mu': line, 'anio': y, 'codigo_sies': c, 'forma': form, 'articulacion_acreditada': title})
    assert len(detail_by) == sum(mu_total.values()) == 10200
    PRIVATE.mkdir(parents=True, exist_ok=True); PRIVATE.chmod(0o700)
    private_file = PRIVATE/'CONTROLES_FILAS_MU.json'; private_file.write_text(js(personal)); private_file.chmod(0o600)
    # No publica fila original ni identificadores: sólo grupos y conteos.
    mu_rows = [dict(zip(['familia','codcarpr','plan_umas','sede_umas','jornada_umas','cohorte_anio','cohorte_semestre','anio','codigo_sies','forma_ingreso','tecnico_previo_titulado'], k), matriculas=n)
               for k, n in sorted(mu_counts.items(), key=lambda x: str(x[0]))]
    sies_rows = [dict(zip(['familia','cohorte_anio','cohorte_semestre','anio','codigo_sies','forma_ingreso','via_cohorte'], k),
                      tecnico_previo_titulado='NO_COMPROBABLE_E', plan_umas='NO_ENLAZADO_A_IDENTIDAD_INTERNA', matriculas=n)
                 for k, n in sorted(sies_split_counts.items(), key=lambda x: str(x[0]))]
    splits = []; mu_groups = defaultdict(list); sies_groups = defaultdict(list)
    for r in mu_rows: mu_groups[tuple(r[k] for k in ['familia','codcarpr','plan_umas','sede_umas','jornada_umas','cohorte_anio','cohorte_semestre'])].append(r)
    for r in sies_rows:
        if r['cohorte_anio'] is not None: sies_groups[r['familia'], r['cohorte_anio'], r['cohorte_semestre']].append(r)
    for source, gg in [('MU', mu_groups), ('SIES', sies_groups)]:
        for key, rows in sorted(gg.items(), key=lambda x: str(x[0])):
            if len({r['codigo_sies'] for r in rows}) < 2: continue
            state, form_diag, art_diag = split_classification(rows)
            splits.append({'origen': source, 'grupo': list(key), 'familia': key[0], 'estado': state,
                           'matriculas_anuales': sum(r['matriculas'] for r in rows), 'version_por_forma': form_diag,
                           'version_por_articulacion': art_diag, 'tabla': rows,
                           'limite': 'Asociación descriptiva dentro de la cohorte, no causalidad ni asignación. SIES no tiene plan UMAS ni vínculo con título interno.'})
    # Candidatas a nivel familia+cohorte+forma: detectar conflictos entre planes también.
    candidate_counts = defaultdict(Counter); candidate_groups = defaultdict(set)
    for r in mu_rows:
        if r['cohorte_anio'] is None or r['forma_ingreso'] == 'SIN_DATO': continue
        key = (r['familia'],r['cohorte_anio'],r['cohorte_semestre'],r['forma_ingreso'])
        candidate_counts[key][r['codigo_sies']] += r['matriculas']; candidate_groups[key].add(r['plan_umas'])
    previous = defaultdict(set)
    for r in read(src['data/versiones_por_cohorte/20261016/resultados_cohortes.json']):
        c = r['resolucion'].get('codigo_propuesto'); d = r['datos_alumnos']
        if c: previous[family(c), number(d['ANOINGRESO'])].add(c)
    candidates = []
    split_keys = {(r['familia'],r['grupo'][-2],r['grupo'][-1]) for r in splits if r['origen']=='MU'}
    for key, counts in sorted(candidate_counts.items(), key=lambda x: str(x[0])):
        f, cy, sem, form = key
        if (f,cy,sem) not in split_keys: continue
        old = previous[f,cy]
        candidates.append({'origen':'MU','grupo_explicado_completo':False,'familia':f,'cohorte_anio':cy,'cohorte_semestre':sem,'forma_ingreso':form,
                           'codigos_matriculas_anuales':dict(sorted(counts.items())), 'planes_observados':sorted(candidate_groups[key]),
                           'estado':'CANDIDATA_LOCAL_SIN_EXCEPCIONES_OBSERVADAS' if len(counts)==1 else 'CON_EXCEPCIONES_E',
                           'contraste_20261016':'SIN_REGLA_PREVIA_POR_FORMA' if not old else 'COMPATIBLE_CON_CANDIDATOS_PREVIOS' if set(counts)<=old else 'DIFIERE_CANDIDATOS_PREVIOS',
                           'codigos_previos':sorted(old), 'clase':'C/E', 'activa':False,
                           'limite':'Sólo MU observada y cohortes expresas; no extrapola a otro ingreso, año o plan'})
    # Dos universos independientes: la regla SIES no adjudica un plan UMAS.
    for split in splits:
        if split['origen'] != 'SIES' or split['estado'] != 'EXPLICADO_POR_FORMA_INGRESO':
            continue
        f, cy, sem = split['grupo']
        old = previous[f, cy]
        for form, codes in split['version_por_forma']['regla_observada'].items():
            counts = Counter()
            for row in split['tabla']:
                if row['forma_ingreso'] == form:
                    counts[row['codigo_sies']] += row['matriculas']
            candidates.append({'origen':'SIES','grupo_explicado_completo':True,
                               'familia':f,'cohorte_anio':cy,'cohorte_semestre':sem,'forma_ingreso':form,
                               'codigos_matriculas_anuales':dict(sorted(counts.items())),
                               'planes_observados':[], 'estado':'CANDIDATA_LOCAL_SIN_EXCEPCIONES_OBSERVADAS',
                               'contraste_20261016':'SIN_REGLA_PREVIA_POR_FORMA' if not old else 'COMPATIBLE_CON_CANDIDATOS_PREVIOS' if set(counts)<=old else 'DIFIERE_CANDIDATOS_PREVIOS',
                               'codigos_previos':sorted(old),'clase':'C/E','activa':False,
                               'limite':'Sólo familia/cohorte SIES observada; no identifica plan UMAS ni define otra cohorte'})
    plan_changes = Counter()
    for (_,f,cy,sem), years in observed_plans.items():
        ordered = sorted(years)
        for a,b in zip(ordered,ordered[1:]):
            pa={p for p in years[a] if p not in ('PLAN_NO_OBSERVADO','PLAN_MULTIPLE_E')}
            pb={p for p in years[b] if p not in ('PLAN_NO_OBSERVADO','PLAN_MULTIPLE_E')}
            if pa and pb and pa!=pb: plan_changes[f,cy,sem] += 1
    # Diagnóstico exactamente de los veinte códigos, causas coexistentes visibles.
    diagnostics = []
    split_index = {tuple(r['grupo']):r for r in splits if r['origen']=='MU'}
    table = read(src['data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json'])['filas']
    h002 = {r['codigo_unico']:r for r in table if r['anio']==2027}
    for old in old_validation:
        if old['estado']!='CONTRADICE': continue
        c=old['codigo_sies']; tt=h002[c]
        rr=[r for r in mu_rows if r['codigo_sies']==c and r['anio']<=2025]
        plans_count=Counter(); outside_count=Counter(); matching=[]
        for r in rr:
            if r['plan_umas'] not in ('PLAN_NO_OBSERVADO','PLAN_MULTIPLE_E'):
                plans_count[r['plan_umas']]+=r['matriculas']
                if r['plan_umas'] not in tt['plan_umas']:outside_count[r['plan_umas']]+=r['matriculas']
        for conflict in old['cohortes_con_reparto']:
            k=tuple(conflict[x] for x in ['familia','codcarpr','plan_umas','sede_umas','jornada_umas','cohorte_anio','cohorte_semestre'])
            if k in split_index: matching.append(split_index[k])
        form_explained=bool(matching) and all(r['estado']=='EXPLICADO_POR_FORMA_INGRESO' for r in matching)
        changed=sum(plan_changes[r['familia'],r['grupo'][-2],r['grupo'][-1]] for r in matching)
        # Compartir código es observado, pero no prueba la causa de un reparto.
        shared=len(plans_count)>1
        if form_explained:
            cause='VERSION_POR_FORMA_INGRESO'; proposal='MANTENER_CON_REGLA_CANDIDATA_POR_FORMA'
        elif shared and outside_count:
            cause='VARIOS_PLANES_UN_CODIGO'; proposal='AMPLIAR_CANDIDATOS_PARA_REVISION_SIN_ASIGNAR_VERSION'
        elif changed:
            cause='CAMBIO_DE_PLAN'; proposal='MANTENER_PROVISIONAL; verificar migración, sin corregir carga'
        else:
            cause='SIN_EXPLICACION'; proposal='MANTENER_PROVISIONAL; no corregir sin evidencia'
        diagnostics.append({'codigo_sies':c,'causa_principal':cause,'propuesta':proposal,
                            'planes_H002':tt['plan_umas'],'planes_observados_matriculas_anuales':dict(sorted(plans_count.items())),
                            'planes_adicionales_matriculas_anuales':dict(sorted(outside_count.items())),
                            'repartos_originales':len(old['cohortes_con_reparto']),
                            'repartos_diagnosticados':dict(Counter(r['estado'] for r in matching)),
                            'todos_repartos_explicados_por_forma':form_explained,
                            'causa_reparto': 'VERSION_POR_FORMA_INGRESO' if form_explained else 'SIN_EXPLICACION_DEMOSTRADA',
                            'version_por_cohorte': 'NO_EXPLICA: los repartos originales ocurren dentro de la misma cohorte',
                            'posible_error_carga': 'E: no hay rectificación o bitácora que demuestre error',
                            'cambio_plan_observado_transiciones_familia_cohorte':changed,
                            'cohortes': [{'grupo':r['grupo'],'estado':r['estado'],'matriculas':r['matriculas_anuales'],'conflictos_forma':r['version_por_forma']['conflictos']} for r in matching],
                            'clase':'C/E','decision_alexi':'',
                            'limite':'Diagnóstico no autoriza modificación; compartir código o observar otro plan no demuestra error ni migración causal del reparto.'})
    assert len(diagnostics)==20
    # Lotes sólo de cuestiones abiertas. Una familia/tipo por entrada, sin filas personales.
    problems=defaultdict(list)
    for r in hist:
        if r['estado'] in ('AMBIGUA','NO_CUADRA'): problems[r['familia'],r['estado']].append({'anio':r['anio'],'sies':sum(r['sies_cohorte_derivada'].values()),'interno':sum(r['interno_ingreso_anio'].values()),'causas_E':r['causas_probables_E']})
    for r in splits:
        if r['estado'] in ('PARCIAL','NO_EXPLICADO'):problems[r['familia'],'REPARTO_'+r['origen']].append({'grupo':r['grupo'],'estado':r['estado'],'matriculas_anuales':r['matriculas_anuales'],'conflictos_forma':r['version_por_forma']['conflictos']})
    for r in diagnostics:problems[family(r['codigo_sies']),'H002_PROPUESTA'].append(r)
    for r in carry_rows:
        if r['estado']=='CAMBIO_DE_CODIGO':problems[r['familia'],'CAMBIO_ARRASTRE'].append(r)
    problems['I162S2C83J4','ADMP_CADMP_PENDIENTE_ALEXI'].append({'estado':'PENDIENTE_D; no aprobado en H002h'})
    first_family={}
    for y,c in public:
        if public[y,c]:first_family[family(c)]=min(y,first_family.get(family(c),y))
    ordered=sorted(problems,key=lambda k:(first_family.get(k[0],9999),k[0],k[1]));cars=[]
    for f,_ in ordered:
        car=re.sub(r'J\d+$','',f)
        if car not in cars:cars.append(car)
    lots=[{'lote':cars.index(re.sub(r'J\d+$','',f))//5+1,'familia':f,'problema':p,'evidencia':problems[f,p],
           'propuesta':'Revisar evidencia agregada y aprobar sólo el alcance acreditado; conservar E sin corregir H002 ni cargas.', 'decision_alexi':''} for f,p in ordered]
    way_rows=[{'anio':y, **{v:ways[y][v] for v in ['a','b','c','censurada','sin_identificador']}, 'total':sum(ways[y].values())} for y in sorted(ways)]
    sies_matrix=[dict(zip(['anio','codigo_sies','cohorte_anio','cohorte_semestre','via_cohorte','origen_anio_observado','origen_semestre_observado'],k),matriculas=n) for k,n in sorted(matrix.items(),key=lambda x:str(x[0]))]
    summary={'clases':'D método Alexi; B fuentes; C derivación; E causalidad o respaldo insuficiente; ninguna nueva norma A',
             'cohortes_vias':way_rows,'sies_filas':sum(mc.values()),'control_publico_diferencias':sum(r['diferencia']!=0 for r in controls),
             'historia_antes':dict(Counter(r['estado'] for r in old_hist)),'historia_ahora':dict(Counter(r['estado'] for r in hist)),
             'historia_unidad':'familia × año de ingreso; no se inventa semestre UMAS histórico',
             'historia_mismo_universo':dict(Counter(r['estado'] for r in hist if r['estado_antes']!='NO_COMPARADO')),
             'historia_casos_nuevos':dict(Counter(r['estado'] for r in hist if r['estado_antes']=='NO_COMPARADO')),
             'transicion_151_no_cuadra':dict(Counter(r['estado'] for r in hist if r['estado_antes']=='NO_CUADRA')),
             'asignaciones_fijadas':len(fixed),
             'arrastre':dict(Counter({s:sum(r['matriculas'] for r in carry_rows if r['estado']==s) for s in ['MANTIENE','CAMBIO_DE_CODIGO']})),
             'causas_residuales_no_excluyentes':dict(causes),'totales_ingreso_por_anio':annual,
             'repartos':{s:dict(Counter(r['estado'] for r in splits if r['origen']==s)) for s in ['MU','SIES']},
             'candidatas':dict(Counter(r['estado'] for r in candidates)),
             'candidatas_por_origen':{s:dict(Counter(r['estado'] for r in candidates if r['origen']==s)) for s in ['SIES','MU']},
             'diagnostico_20':dict(Counter(r['causa_principal'] for r in diagnostics)),
             'lotes':max((r['lote'] for r in lots),default=0),'decisiones':len(lots),
             'articulacion_MU':dict(Counter({s:sum(r['matriculas'] for r in mu_rows if r['tecnico_previo_titulado']==s) for s in ['SI','NO_ACREDITADO_E','NO_COMPROBABLE_E']})),
             'codigo_tecnico_clasificado_publicacion':len(technical_codes),
             'ADMP_CADMP':'PENDIENTE_ALEXI; ninguna aprobación',
             'causalidad_limites':['Primera observación no prueba ingreso real','Origen no equivale a carrera actual: sustitución D explícita','No se acredita fecha de ingreso respecto al corte con la última matrícula','Título sin año previo o expediente único no acredita articulación','SIES no se enlaza con MU; comparación de formas en universos separados']}
    objects={DATA/'MATRIZ_PARIDAD_COHORTE.json':{'SIES':sies_matrix,'MU':mu_rows,'HISTORICO':historical_rows},
             DATA/'REGLAS_CANDIDATAS.json':{'reglas':candidates,'activa':False},DATA/'CUADRATURA_COHORTES.json':{'cohortes':hist,'fijadas':fixed,'arrastre':carry_rows},
             OUT/'COHORTES_DERIVADAS.json':{'filas':way_rows},OUT/'REPARTOS_FORMA_INGRESO.json':{'grupos':splits},
             OUT/'DIAGNOSTICO_20.json':{'codigos':diagnostics},OUT/'CONTROL_SIES_PUBLICACION.json':{'filas':controls},
             OUT/'LOTES_REVISION_v3.json':{'lotes':lots},OUT/'RESULTADOS.json':summary}
    files={p:js(v) for p,v in objects.items()}
    # CSV separados por unidad; no unir conteos SIES y MU como personas.
    files[DATA/'MATRIZ_SIES_COHORTE.csv']=csvbytes(sies_matrix)
    files[DATA/'MATRIZ_MU_COHORTE_FORMA.csv']=csvbytes(mu_rows)
    files[DATA/'REGLAS_CANDIDATAS.csv']=csvbytes(candidates)
    lines=['# H002h · cohorte derivada y diagnóstico','',
           'D · Método aprobado por Alexi, 29-10-2026. B/C/E · Resultados descriptivos, sin activar reglas ni modificar H002/H002g.',
           '', '## Vías de cohorte SIES','', '| Año | a actual | b origen | c primera observación | Censurada | Sin identificador | Total |','|---|---:|---:|---:|---:|---:|---:|']
    for r in way_rows:lines.append('| '+' | '.join(str(r[k]) for k in ['anio','a','b','c','censurada','sin_identificador','total'])+' |')
    lines+=['','La vía c sólo estima el año. La vía b conserva el ingreso de origen como sustitución explícita D, sin certificar que sea ingreso a la carrera actual. Censurada no se interpreta como ingreso 2007.',
            '', '## Historia 2007–2021','',f"Antes: {summary['historia_antes']}. Ahora: {summary['historia_ahora']}. Fijadas C: {len(fixed)}.",
            f"Mismo universo H002g: {summary['historia_mismo_universo']}. Nuevas comparaciones: {summary['historia_casos_nuevos']}. De los 151 NO_CUADRA originales: {summary['transicion_151_no_cuadra']}.",
            'La unidad comparable con H002g es familia × año; períodos internos literales y semestre SIES están desglosados en los JSON. Perfil o plan ausente impide fijar.',
            '', '| Año | Interno total ingreso | Interno familias mapeadas | SIES ingreso derivado | SIES primer año publicado |','|---|---:|---:|---:|---:|']
    for r in annual:lines.append('| '+' | '.join(str(r[k]) for k in ['anio','interno_total_expedientes_anoingreso','interno_familias_mapeadas','sies_cohorte_derivada_ingresa_en_anio','sies_primer_anio_publicado'])+' |')
    lines+=['',f"Causas probables E (no excluyentes, unidad familia-año): {dict(causes)}.",
            'Cada NO_CUADRA conserva conteos de vía c, semestre 2 y expedientes posteriores; ninguna diferencia prueba por sí sola migración, corte o integridad del extracto.',
            '', '## Repartos y candidatas','',f"MU: {summary['repartos']['MU']}. SIES: {summary['repartos']['SIES']}.",
            f"Candidatas por familia/cohorte/forma (componentes, no grupos completos): {summary['candidatas_por_origen']}.",
            'MU: los tramos unívocos sólo explican parte de repartos con excepciones; no hay grupo MU completamente explicado. SIES: las dos separaciones completas quedan como candidatas locales, sin plan UMAS ni activación.',
            f"Título técnico previo acreditado / no acreditado: {summary['articulacion_MU']}. NO_ACREDITADO_E no significa que no exista título.",
            'Gobernanza: gobernanza_for_ing_act.tsv de la raíz (el archivo de data/ es un puntero textual); control/config_for_ing_act.json y reporte de auditoría. Se conservan valores originales, sin derivar FOR nuevamente. Las descripciones 2026 no se convierten en normativa histórica.',
            'EXPLICADO significa separación descriptiva sin excepciones dentro del grupo observado. SIES no incluye plan UMAS; sus grupos son familia/cohorte y no se enlazan a personas internas.',
            '', '## Las veinte contradicciones','', '| Código | Causa principal | Planes observados (matrículas-año) | Repartos diagnosticados | Propuesta |','|---|---|---|---|---|']
    for r in diagnostics:lines.append(f"| {r['codigo_sies']} | {r['causa_principal']} | {r['planes_observados_matriculas_anuales']} | {r['repartos_diagnosticados']} | {r['propuesta']} |")
    lines+=['','VERSION_POR_COHORTE no explica un reparto que ya está dentro de la misma cohorte. No hay causa CAMBIO_DE_PLAN ni POSIBLE_ERROR_DE_CARGA demostrada para adjudicarla a los códigos. Compartir código y repartir una cohorte son fenómenos distintos; el diagnóstico muestra ambos. No hay error de carga demostrado. No se aplica ninguna ampliación ni corrección.',
            '', f"Revisión: {summary['lotes']} lotes y {summary['decisiones']} decisiones familia/problema. ADMP/CADMP sigue pendiente de Alexi.",
            '', '## Trazabilidad y límites','',
            'FUENTES.json y MANIFEST.json fijan rutas y hashes. Los enlaces H002g se reutilizan íntegros, cotejados línea a línea con identidad/código/selección de la base MU; no se modifica su detalle privado. Los códigos y totales SIES originales no cambian. MRUN sólo en memoria; sin nacimiento ni enlace RUT–MRUN.',
            'QA separado: hashes, sumas, reproducción byte a byte, pruebas y privacidad; fuentes, bases, denominadores, tasas y 24 cambios ajenos preservados.']
    files[OUT/'INFORME.md']='\n'.join(lines)+'\n'
    lines=['# H002h · lotes de revisión v3','','Una decisión por familia y problema; máximo cinco carreras por lote. Los indicadores de causa son hipótesis E, salvo evidencia explícita.','']
    for r in lots:
        lines += [f"## Lote {r['lote']} · {r['familia']} · {r['problema']}",'']
        for e in r['evidencia']:lines.append('- '+json.dumps(e,ensure_ascii=False,sort_keys=True))
        lines += ['', 'Propuesta: '+r['propuesta'],'','Decisión Alexi: ____','']
    lines += ['## SIN_ENLACE','', 'Se conserva el resumen H002g, sin líneas de decisión individuales. No se modificó ningún enlace.']
    files[OUT/'LOTES_REVISION_v3.md']='\n'.join(lines)+'\n'
    files[DATA/'README.md']='''# H002h · paridad por cohorte v2\n\nD · Alexi, 29-10-2026. Sustitución derivada y trazable: actual válido, origen válido, primera observación de la misma familia desde 2008, o censura 2007. Primera observación no prueba ingreso real ni semestre. Las fuentes originales y H002g no se modifican.\n\nC · Matriz con orígenes separados SIES, MU e histórico. No sumar esos orígenes ni tratar matrículas-año como personas. La cuadratura anual conserva períodos UMAS sin inventar equivalencia histórica. FIJADA_C requiere asignación exacta única, plan observado, perfil compatible y ausencia de censura; sólo fija la propuesta de catálogo anual.\n\nC/E · Repartos por forma y título previo: clasificaciones descriptivas en cada universo. No hay enlace MRUN–RUT. SI de título previo requiere persona exacta, código de nivel técnico según publicación, expediente compatible único y año de título anterior al ingreso. NO_ACREDITADO no prueba ausencia. Forma 11 o estado actual no basta.\n\nCandidatas no activas, intervalos observados sin extrapolación. Compartir código no prueba la causa de un reparto ni error de carga. Las causas residuales se conservan como E cuando falta cronología o cobertura. ADMP/CADMP pendiente de Alexi.\n\nReproducción: python3 outputs/paridad_cohorte_2007_2026_v2/construir_h002h.py --verificar. QA: qa_h002h.py --reproducir. Fuentes y scripts fijados en MANIFEST; salida privada sólo en ~/.local/share/ipss/h002h_20261029/.\n'''
    files={p:('\n'.join(x.rstrip() for x in t.splitlines()).rstrip()+'\n' if p.suffix=='.md' else t) for p,t in files.items()}
    manifest={'fuentes':sources,'salidas':{str(p.relative_to(ROOT)):hashlib.sha256(t.encode()).hexdigest() for p,t in files.items()},
              'scripts':{str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),OUT/'qa_h002h.py',OUT/'test_h002h.py']},
              'especificacion_sha256':sha(OUT/'ESPECIFICACION.md'),'baseline_sha256':sha(OUT/'ESTADO_INICIAL.json'),
              'clase':'B/C/D/E','activa':False,'adjudicacion_personal':False}
    files[DATA/'MANIFEST.json']=js(manifest)
    return files, summary


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--verificar',action='store_true');a=ap.parse_args()
    files,summary=build()
    if a.verificar:
        bad=[str(p.relative_to(ROOT)) for p,t in files.items() if not p.exists() or p.read_bytes()!=t.encode()]
        if bad:raise SystemExit('Reproducción distinta: '+str(bad))
    else:
        for p,t in files.items():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t)
    print(js({k:summary[k] for k in ['historia_antes','historia_ahora','asignaciones_fijadas','repartos','candidatas','diagnostico_20','lotes','decisiones']}))

if __name__=='__main__':main()
