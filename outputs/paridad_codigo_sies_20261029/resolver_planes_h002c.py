#!/usr/bin/env python3
"""H002c: perfiles de catálogo y propuestas; lecturas privadas sin identidades."""
from collections import Counter, defaultdict
import ast
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento


def txt(v):
    if v is None:
        return ''
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def norm(v):
    return ''.join(c for c in unicodedata.normalize('NFKD', txt(v).upper()) if not unicodedata.combining(c))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()


def load(rel):
    return json.loads((ROOT / rel).read_text())


def dump(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, indent=2) + '\n'


def write_same(path, content, verify=False):
    if path.exists():
        if path.read_text() != content:
            raise ValueError('Salida distinta; conservar y revisar: ' + path.name)
    elif verify:
        raise ValueError('Salida ausente: ' + path.name)
    else:
        path.write_text(content)


def rows(path, sheet):
    import openpyxl
    w = openpyxl.load_workbook(path, read_only=True, data_only=True)
    it = w[sheet].iter_rows(values_only=True)
    header = [txt(v) for v in next(it)]
    try:
        for i, vals in enumerate(it, 2):
            yield i, dict(zip(header, vals))
    finally:
        w.close()


def read_sources():
    cat = load('data/catalogo_fuentes/CATALOGO_FUENTES.json')
    mallas = load('data/diccionario_umas/COMPROBACION_MALLAS.json')
    registry = OUT / 'FUENTES_H002C.json'
    if registry.exists():
        sources = json.loads(registry.read_text())
    else:
        sources = []
        for key in ('listado', 'h112b_excel', 'h112b_csv', 'manual'):
            x = mallas['fuentes'][key]
            sources.append({'id': key, 'ruta': x['ruta'], 'sha256': x['sha256'],
                            'clase': 'A' if key == 'manual' else 'B', 'proceso': 'Avance Curricular 2026; datos 2025; catálogo institucional sin vigencia universal'})
        for entry in cat['catalogo']:
            if entry['archivo'] in {'PROMEDIOSDEALUMNOS_7804.xlsx', 'PROMEDIOSDEALUMNOS_12166.xlsx',
                                    'PROMEDIOSDEALUMNOS_3233.xlsx', 'PROMEDIOSDEALUMNOS_2071.xlsx', 'Permanencia.xlsx'}:
                sources.append({'id': entry['archivo'], 'ruta': entry['ruta_consolidada'],
                                'sha256': entry['sha256'], 'clase': 'B', 'datos_personales': True})
        rels = ['data/catalogo_fuentes/CATALOGO_FUENTES.json', 'data/catalogo_datos/CATALOGO_DATOS_IPSS.json',
            'data/diccionario_umas/COMPROBACION_MALLAS.json', 'data/diccionario_umas/DICCIONARIO_UMAS.json',
            'data/diccionario_umas/EQUIVALENCIAS_UMAS.json', 'DURACION_ESTUDIOS.tsv',
            'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json',
            'data/versiones_por_cohorte/20261028/grupos_existentes.json',
            'data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json',
            'outputs/paridad_codigo_sies_20261029/DECISIONES_PENDIENTES.json',
            'outputs/paridad_codigo_sies_20261029/REVISION_CASO_A_CASO_12.json',
            'docs/SEGUIMIENTO_RUT_Y_CONVERSION_PERIODOS_20261023.md', 'codigo_gobernanza_v2.py',
            'docs/unificacion_proyectos_y_reglas_negocio_20261015.md',
            'outputs/revision_discrepancias_mallas_20261026/CONTRASTE_PLANES_AGREGADO.json',
            'outputs/conciliacion_mallas_vigencia_20261026/REVISION_AGREGADA.json',
            'data/diccionario_sies_seguimiento/activo.json']
        for rel in rels:
            sources.append({'id': rel, 'ruta': str(ROOT / rel), 'sha256': sha(ROOT / rel), 'clase': 'B/C/D'})
        active = load('data/diccionario_sies_seguimiento/activo.json')
        desc = load(active['descriptor'])
        sources.extend([{'id': 'descriptor_v20', 'ruta': str(ROOT / active['descriptor']), 'sha256': active['sha256'], 'clase': 'C/D'},
                        {'id': 'base_v20', 'ruta': desc['base_privada']['ruta'], 'sha256': desc['base_privada']['sha256'], 'clase': 'B/C/D', 'datos_personales': True}])
    for x in sources:
        if sha(x['ruta']) != x['sha256']:
            raise ValueError('Fuente alterada: ' + x['id'])
    return sources, cat, mallas


def dimension(code):
    m = re.fullmatch(r'I162S(\d+)C(\d+)J(\d+)V(\d+)', code)
    if not m:
        raise ValueError('Código de catálogo inválido')
    return m.groups()


def state(a, b):
    a, b = set(a), set(b)
    if a and b and not a & b:
        return 'CONFLICTO'
    if len(a) == len(b) == 1 and a == b:
        return 'CALCE_UNICO'
    if a or b:
        return 'CALCE_DEBIL'
    return 'SIN_CALCE'


def numeric(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def compare_durations(profile):
    result=[]
    for f in profile['perfil_formal_H112B']:
        for c in profile['conversion_si_regimen_PROMEDIOS']:
            value=c['semestres_calculados']
            result.append({'regimen_PROMEDIOS':c['regimen'], 'conversion_diagnostica_semestres':value,
                'duracion_estudios_H112B_semestres':f['semestres'], 'tipo_plan_H112B':f['tipo_plan_codigo'],
                'estado':'NO_COMPARABLE' if value is None else 'COINCIDE' if value==numeric(f['semestres']) else 'DIFIERE',
                'clase':'C: contraste diagnóstico; conversión de NIV_ACA no certifica duración curricular'})
    return result


def build():
    sources, cat, comparison = read_sources()
    src = {x['id']: x for x in sources}
    def source(key):
        return Path(src[key]['ruta'])
    master = load('data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json')
    groups = load('data/versiones_por_cohorte/20261028/grupos_existentes.json')
    with (ROOT/'DURACION_ESTUDIOS.tsv').open() as f:
        duration_rows = list(csv.DictReader(f, delimiter='\t'))
    table = load('data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json')['filas']
    table_by = {x['codigo_unico']: x for x in table if x['anio'] == 2027}
    pending = load('outputs/paridad_codigo_sies_20261029/DECISIONES_PENDIENTES.json')
    cases = pending['version_multiple_E_por_grupo']
    prior = load('outputs/paridad_codigo_sies_20261029/REVISION_CASO_A_CASO_12.json')
    old_cases = {x['numero']: x for x in prior['casos']}
    # Sólo campos de catálogo; nunca RUT, CODCLI, nombres/contactos de personas.
    listing = defaultdict(list)
    for i, row in rows(source('listado'), 'BBDD Bruta'):
        car, plan, site = (txt(row.get(k)) for k in ('Codcarr', 'CODPESTUD', 'Sede'))
        if car and plan and txt(row.get('CODRAMO')):
            listing[(car, plan, site)].append({'fila': i, 'ramo': txt(row.get('CODRAMO')),
                'nivel': numeric(row.get('NIVEL')), 'regimen': txt(row.get('REGIMEN')), 'tipo': txt(row.get('TIPO')),
                'nombre_carrera': txt(row.get('Nombre_L'))})
    print('Listado leído: perfiles de plan', len(listing), flush=True)
    # H112B vincula explícitamente plan con duración y tipo. Sigue siendo candidata.
    h112 = defaultdict(list)
    for i, row in rows(source('h112b_excel'), '02_H112A_HOJA10'):
        h112[txt(row['CODPESTUD'])].append({'fila': i, 'codigo_sies': txt(row['CODIGO_UNICO']),
            'duracion_estudios_semestres': txt(row['DURACION_ESTUDIOS']), 'tipo_plan_codigo': txt(row['TIPO_PLAN_CARRERA']),
            'total_ramos': numeric(row['TOTAL_UNIDADES_MEDIDA']), 'nivel_max_declarado': txt(row['NIVEL_MAX_PLAN']),
            'metodo': txt(row['METODO_SELECCIONADO']), 'estado': txt(row['ESTADO_FILA']),
            'clase': 'B/C/D: candidata H112B; no acredita aceptación PES ni vigencia 2027'})
    # Capturar únicamente dimensiones y conteos; cada extracción se conserva separada.
    prom = defaultdict(Counter)
    names_prom = defaultdict(set)
    source_counts = {}
    for key in ['PROMEDIOSDEALUMNOS_7804.xlsx', 'PROMEDIOSDEALUMNOS_12166.xlsx',
                'PROMEDIOSDEALUMNOS_3233.xlsx', 'PROMEDIOSDEALUMNOS_2071.xlsx']:
        n = 0
        for i, row in rows(source(key), 'Hoja1'):
            car, plan = txt(row.get('CODCARR')), txt(row.get('PLAN_DE_ESTUDIO'))
            if not car or not plan or plan.upper() in {'NULL', 'NONE', 'NAN'}:
                continue
            jour, regime = norm(row.get('JORNADA')), norm(row.get('REGIMEN'))
            prom[(car, plan)][(key, jour, regime)] += 1
            names_prom[(car, plan)].add(norm(row.get('CARRERA')))
            n += 1
        source_counts[key] = n
        print('PROMEDIOS leído:', key, n, 'filas con carrera/plan; no sumar extracciones', flush=True)
    permanence = Counter()
    for i, row in rows(source('Permanencia.xlsx'), 'Worksheet'):
        car, site = txt(row.get('CARRERA_ALUM')), txt(row.get('COD_SEDE'))
        jour, name = norm(row.get('JORNADA')), norm(row.get('NOMBRE_CARRERA'))
        total = txt(row.get('TOTAL_RAMOS_MALLA'))
        if car:
            permanence[(car, site, jour, name, total)] += 1
    # Sólo SQL agregado: no extraer identidades. Documentales y D nunca se mezclan.
    svc = DiccionarioSiesSeguimiento(root=ROOT)
    docs, internals, accept = [], [], Counter()
    for kind, field in [('documental', 'codigo_documental_atribuible'), ('D_interno', 'codigo_interno_adoptado')]:
        sql = f'''SELECT carrera,plan,sede,jornada,anio,json_extract(payload,'$.{field}'),
                json_extract(payload,'$.aceptacion_SIES'),COUNT(*) FROM observaciones
                WHERE CAST(anio AS INTEGER) BETWEEN 2024 AND 2026
                AND json_extract(payload,'$.{field}') IS NOT NULL
                AND json_extract(payload,'$.{field}') != '' GROUP BY 1,2,3,4,5,6,7'''
        for car, plan, site, jour, year, code, acceptance, count in svc.db.execute(sql):
            item = {'codcarpr': txt(car), 'plan': txt(plan), 'sede': txt(site), 'jornada': txt(jour),
                'anio': txt(year), 'codigo_sies': code, 'aceptacion_SIES': acceptance,
                'observaciones_contexto': count, 'clase': 'B/C_DOCUMENTAL_ANUAL' if kind == 'documental' else 'D_INTERNO'}
            (docs if kind == 'documental' else internals).append(item)
            if kind == 'documental':
                accept[txt(acceptance)] += count
    svc.close()
    print('v20 agregado; estados de aceptación:', dict(accept), flush=True)
    group_index = defaultdict(list)
    for g in groups:
        group_index[g['codcarpr']].append(g)
    # Reusar el mapa de conversión ya gobernado, extraído sin ejecutar el motor MU.
    tree = ast.parse((ROOT / 'codigo_gobernanza_v2.py').read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_trimester_level_to_semester')
    level_map = ast.literal_eval(next(n.value for n in fn.body if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == 'map_eq' for t in n.targets)))
    def convert(level, regime):
        if level is None:
            return None
        n = int(level)
        if 'TRIM' in norm(regime):
            return level_map.get(n, (2*n+2)//3 if n > 12 else None)
        if norm(regime) in {'SEMESTRAL', 'SEMESTRE'}:
            return level
        return None
    profiles = []
    for (car, plan, site), rr in sorted(listing.items()):
        levels = [x['nivel'] for x in rr if x['nivel'] is not None]
        maxlevel = max(levels) if levels else None
        regimes = sorted({x['regimen'] for x in rr})
        pr = [{'fuente': k[0], 'jornada': k[1], 'regimen': k[2], 'filas_asignaturas': v}
              for k, v in sorted(prom.get((car, plan), {}).items())]
        by_reg = sorted({k['regimen'] for k in pr})
        gp = [g for g in group_index[car] if g['sede'] == site]
        linked = h112.get(plan, [])
        formal = sorted({(x['duracion_estudios_semestres'], x['tipo_plan_codigo']) for x in linked})
        perms = [{'sede_reportada': s, 'jornada': j, 'total_ramos': t, 'expedientes': n}
                 for (c, s, j, name, t), n in sorted(permanence.items()) if c == car]
        # No inventar vigencia ni convertir S a TRIM por tener 6/12 niveles.
        issues = []
        if any(x in {'S','A'} for x in regimes):
            issues.append('REGIMEN usa abreviaturas S/A; no se acreditó catálogo de esas abreviaturas. Duración por ese campo queda E, sin asumir semestres.')
        if any('TRIM' in x for x in by_reg) and regimes == ['S']:
            issues.append('REGIMEN listado=S y actividad PROMEDIOS=TRIMESTRAL: no sustituir silenciosamente la unidad del nivel.')
        if set(x['tipo'] for x in rr) & {'Obl', 'OPC'}:
            issues.append('TIPO es de asignatura (Obl/OPC), no regular/continuidad.')
        candidate_duration = convert(maxlevel, regimes[0]) if len(regimes) == 1 else None
        if formal and candidate_duration is not None and any(numeric(d) != candidate_duration for d, t in formal):
            issues.append('Nivel máximo interpretado con REGIMEN del listado difiere de duración formal H112B. Nivel no acredita duración por sí solo.')
        profiles.append({'codcarpr': car, 'CODPESTUD': plan, 'sede_umas': site,
            'nombres_catalogo': sorted({x['nombre_carrera'] for x in rr}), 'filas_listado': len(rr),
            'ramos_distintos': len({x['ramo'] for x in rr}), 'nivel_maximo': maxlevel, 'REGIMEN': regimes,
            'TIPO_asignatura': sorted({x['tipo'] for x in rr}),
            'duracion_calculada_segun_regimen_listado': candidate_duration,
            'estado_duracion_calculada': 'C: cálculo condicionado, no duración formal acreditada',
            'conversion_si_regimen_PROMEDIOS': [{'regimen': x, 'semestres_calculados': convert(maxlevel, x)} for x in by_reg],
            'perfil_formal_H112B': [{'semestres': d, 'tipo_plan_codigo': t} for d, t in formal],
            'respaldo_H112B': linked,
            'perfiles_grupo_gobernado': [{'jornada': g['jornada'], 'perfiles': g['perfiles_duracion_tipo'],
                                        'codigos': g['codigos_base']} for g in gp],
            'PROMEDIOS': pr, 'Permanencia_sin_plan': perms,
            'contraste_ramos_5810': [{'codigo_sies': x['codigo_sies'], 'total_5810': x['total_ramos'],
                'diferencia_listado_menos_5810': len({a['ramo'] for a in rr}) - x['total_ramos'] if x['total_ramos'] is not None else None} for x in linked],
            'contraste_ramos_Permanencia': [{'total': x['total_ramos'], 'diferencia': numeric(x['total_ramos']) - len({a['ramo'] for a in rr})
                if numeric(x['total_ramos']) is not None else None, 'expedientes': x['expedientes'], 'limite': 'por carrera; no acredita plan individual'} for x in perms],
            'primera_fila_listado': min(x['fila'] for x in rr), 'incidencias': issues})
    for profile in profiles:
        profile['contraste_duracion_5810']=compare_durations(profile)
    profby = {(x['codcarpr'], x['CODPESTUD'], x['sede_umas']): x for x in profiles}
    all_pairs = set(prom) | {(c, p) for c, p, s in listing}
    # Relación entre carreras sólo si comparten C de SIES en la gobernanza existente.
    hyp = []
    for profile in profiles:
        car, plan, site = profile['codcarpr'], profile['CODPESTUD'], profile['sede_umas']
        if not car.startswith('C'):
            continue
        families = {dimension(code)[1] for g in group_index[car] for code in g['codigos_base']}
        peers = [p for p in profiles if not p['codcarpr'].startswith('C') and p['sede_umas'] == site and families &
            {dimension(code)[1] for g in group_index[p['codcarpr']] for code in g['codigos_base']}]
        fm = profile['perfil_formal_H112B']
        group_profiles = {tuple(v) for g in profile['perfiles_grupo_gobernado'] for v in g['perfiles']}
        supported = (any(x['semestres'] == '4' and x['tipo_plan_codigo'] == '3' for x in fm) or group_profiles == {('4', '3')})
        contradiction = bool(fm and not any(x['semestres'] == '4' and x['tipo_plan_codigo'] == '3' for x in fm))
        if car.startswith('CO'):
            status = 'FUERA_HIPOTESIS_CO_SEDE' if site == 'CO' else 'RECHAZADA_GENERALIZACION'
        elif contradiction:
            status = 'RECHAZADA'
        else:
            status = 'PARCIAL' if supported else 'SIN_RESPALDO_DE_TIPO_Y_DURACION'
        hyp.append({'codcarpr': car, 'plan': plan, 'sede': site, 'estado': status,
            'nivel_maximo': profile['nivel_maximo'], 'REGIMEN': profile['REGIMEN'],
            'perfil_H112B': fm, 'perfil_grupo': [list(x) for x in sorted(group_profiles)],
            'pares_regulares_gobernados': [{'codcarpr': p['codcarpr'], 'plan': p['CODPESTUD'],
                'nivel_maximo': p['nivel_maximo'], 'perfil_H112B': p['perfil_formal_H112B']} for p in peers],
            'motivo': 'El prefijo no constituye regla. Se evalúa evidencia de tipo/duración y la incidencia de régimen por plan.'})

    def plan_checks(car, plan, site, jour, options):
        profile = profby.get((car, plan, site))
        findings = []
        docrows = [x for x in docs if x['codcarpr'] == car and x['plan'] == plan and x['sede'] == {'RE':'2','CO':'3','PTG':'4'}.get(site) and
                   x['jornada'] == {'D':'1','V':'2','O':'4'}.get(jour)]
        doc_codes = {x['codigo_sies'] for x in docrows}
        a = set()
        for option in options:
            code = option['codigo_unico']; s, c, j, v = dimension(code)
            formal = profile['perfil_formal_H112B'] if profile else []
            # El grupo no acredita por sí solo perfil curricular; mostrarlo como apoyo.
            durations = {x['semestres'] for x in formal}
            types = {x['tipo_plan_codigo'] for x in formal}
            eq = [z for z in master['candidatos_plan_sies'] if z['codcarpr'] == car and z['plan_umas'] == plan and
                  z['sede_umas'] == site and z['jornada_umas'] == jour and z['codigo_unico'] == code]
            exact_doc = code in doc_codes
            same_family = [x for x in docrows if dimension(x['codigo_sies'])[:3] == (s, c, j)]
            # Modalidad: desde la oferta del código explícitamente vinculado, no inferir de jornada.
            modal_evidence = any(x['codigo_sies'] in table_by and table_by[x['codigo_sies']]['modalidad_codigo'] == option['modalidad_codigo'] for x in same_family)
            group_context = any(g['sede'] == site and g['jornada'] == jour and
                any(dimension(q)[:3] == (s, c, j) for q in g['codigos_base']) for g in group_index[car])
            journey_observed = any(k[1] == jour for k in prom.get((car, plan), {}))
            checks = {'plan_en_listado': profile is not None,
                'sede': s == {'RE':'2','CO':'3','PTG':'4'}.get(site),
                'jornada': j == {'D':'1','V':'2','O':'4'}.get(jour) and (journey_observed or bool(same_family)),
                'familia_respaldada': group_context or bool(eq) or bool(same_family),
                'duracion_estudios': bool(durations) and durations == {txt(option['duracion_estudios_semestres'])},
                'tipo_plan': bool(types) and types == {txt(option['tipo_plan_codigo'])},
                'modalidad': modal_evidence}
            if all(checks.values()):
                a.add(code)
            findings.append({'codigo_unico': code, 'controles_perfil_a': checks,
                'atributos_sies': {k: option[k] for k in ['cod_sede','cod_jornada','modalidad_codigo','tipo_plan_codigo','duracion_estudios_semestres','duracion_total_semestres','vigencia_2027']},
                'codigo_documental_b': exact_doc, 'atributos_sin_respaldo_o_distintos': [k for k,vv in checks.items() if not vv],
                'candidatura_maestro_no_adjudicada': bool(eq)})
        targetcodes = {x['codigo_unico'] for x in options}
        b = doc_codes & targetcodes
        return {'codcarpr': car, 'plan': plan, 'sede': site, 'jornada': jour, 'perfil_listado': profile,
            'codigos_perfil_a': sorted(a), 'codigos_documentales_b': sorted(b),
            'documentales_otras_opciones': sorted(doc_codes - targetcodes), 'observaciones_documentales': docrows,
            'correspondencias_D_separadas': [x for x in internals if x['codcarpr'] == car and x['plan'] == plan and
                x['sede'] == {'RE':'2','CO':'3','PTG':'4'}.get(site) and x['jornada'] == {'D':'1','V':'2','O':'4'}.get(jour)],
            'por_opcion': findings, 'clasificacion': state(a,b)}

    # Duración estudios se lee del campo explícito 2027; no confundir con total.
    cfg = load('data/paridad_codigo_sies/20261029/FUENTES.json')
    csource = next(x for x in cfg['fuentes'] if x['id'] == 'carga_v06')
    if sha(ROOT/csource['ruta']) != csource['sha256']:
        raise ValueError('V06 alterada')
    with (ROOT/csource['ruta']).open() as f:
        raw = list(csv.reader(f, delimiter=';'))
    for vals in raw:
        code = 'I162S'+vals[0]+'C'+vals[2]+'J'+vals[5]+'V'+vals[6]
        table_by[code] = dict(table_by[code], duracion_estudios_semestres=vals[9], duracion_total_semestres=vals[11])
    resolved = []
    for case in cases:
        codes = sorted(set(case['codigos_previos'] + case['codigos_2027_familia']))
        options = [table_by[c] for c in codes if c in table_by]
        # También conservar opciones históricas ausentes en 2027 con atributos H002.
        absent = [c for c in codes if c not in table_by]
        checks = [plan_checks(case['codcarpr'], p, case['sede_umas'], case['jornada_umas'], options)
                  for p in case['planes_catalogados_candidatos']]
        a = set().union(*(set(x['codigos_perfil_a']) for x in checks)) if checks else set()
        b = set().union(*(set(x['codigos_documentales_b']) for x in checks)) if checks else set()
        st = state(a,b)
        if st == 'CALCE_UNICO' and not any(x['clasificacion']=='CALCE_UNICO' for x in checks):
            st = 'CALCE_DEBIL'
        if any(x['clasificacion']=='CONFLICTO' for x in checks):
            st = 'CONFLICTO'
        admission_note = ('El código concordante está vigente sin nuevos en 2027: no resuelve la versión de admisión 2027.'
            if st == 'CALCE_UNICO' and all(table_by[q]['vigencia_2027'] != '1' for q in a & b) else
            'La comparación no autoriza asignar personas ni elegir versión de admisión automáticamente.')
        resolved.append({'numero_original': case['numero'], 'grupo': case['grupo'], 'codcarpr':case['codcarpr'],
            'sede':case['sede_umas'],'jornada':case['jornada_umas'], 'clasificacion': st,
            'opciones_perfil_a': sorted(a), 'opciones_documentales_b': sorted(b),
            'opciones_historicas_sin_oferta_2027': absent,
            'planes': checks, 'opciones_SIES': [dict(x, duracion_estudios_2027=table_by[x['codigo_unico']]['duracion_estudios_semestres'])
                for x in old_cases[case['numero']]['opciones_SIES'] if x['codigo_unico'] in table_by],
            'decision_Alexi': '____', 'aplicada': False,
            'admision_2027': admission_note,
            'motivo': 'Se exige perfil formal del plan, sede/jornada observadas, modalidad explícita y código documental concordante; D no reemplaza b.'})
    # Candidatos por familia ya gobernada; nombres exactos sólo para descubrimiento.
    new43 = []
    for target in pending['nuevo_2027_sin_plan_E']:
        s,c,j,v = dimension(target['codigo_unico'])
        candidates = set()
        known_alias = {g['codcarpr'] for g in groups if any(dimension(code)[:2] == (s,c) for code in g['codigos_base'])}
        known_alias |= {x['codcarpr'] for x in master['candidatos_plan_sies'] if dimension(x['codigo_unico'])[:2] == (s,c)}
        for (car,plan,site), rr in listing.items():
            if car in known_alias or any(norm(x['nombre_carrera']) == norm(target['nombre_carrera']) for x in rr):
                candidates.add((car,plan,site))
        for (car,plan), names in names_prom.items():
            if car in known_alias or norm(target['nombre_carrera']) in names:
                sites = {site for cc,pp,site in listing if cc==car and pp==plan}
                sites |= {x['sede_umas'] for x in master['candidatos_plan_sies'] if x['codcarpr']==car and x['plan_umas']==plan}
                for site in sites:
                    candidates.add((car,plan,site))
        site_target = {'2':'RE','3':'CO','4':'PTG'}.get(s)
        other_sites = sorted(candidates - {x for x in candidates if x[2] == site_target})
        candidates = {x for x in candidates if x[2] == site_target}
        perms = [{'codcarpr':car,'sede':site,'jornada':jour,'total_ramos':total,'expedientes':n}
                 for (car,site,jour,name,total),n in sorted(permanence.items()) if car in known_alias or name == norm(target['nombre_carrera'])]
        matches = []
        for car,plan,site in sorted(candidates):
            # La jornada del objetivo debe tener respaldo; no se inventa J3 para O.
            jour = {'1':'D','2':'V','4':'O'}.get(j, 'J3_SIN_EQUIVALENCIA_UMAS_GOBERNADA')
            matches.append(plan_checks(car,plan,site,jour,[table_by[target['codigo_unico']]]))
        a = {code for x in matches for code in x['codigos_perfil_a']}
        b = {code for x in matches for code in x['codigos_documentales_b']}
        # Un código con varias mallas compatibles se conserva como débil, no plan único.
        st = state(a,b)
        if st == 'CALCE_UNICO' and sum(x['clasificacion']=='CALCE_UNICO' for x in matches) != 1:
            st = 'CALCE_DEBIL'
        has_plans = bool(candidates)
        historical_family = any(dimension(x['CODIGO_UNICO'])[:2] == (s,c) for x in duration_rows)
        grp = 'A' if has_plans or historical_family else 'B'
        new43.append({'codigo_unico':target['codigo_unico'],'nombre_carrera':target['nombre_carrera'],
            'grupo':grp,'clasificacion':st,'planes_candidatos':matches,
            'planes_otras_sedes_no_transferidos': [{'codcarpr':c,'plan':p,'sede':ss} for c,p,ss in other_sites],
            'alias_gobernados': sorted(known_alias),'presencia_Permanencia_sin_plan':perms,
            'familia_en_catalogo_historico_2026': historical_family,
            'ausencia_plan_en_listado_y_PROMEDIOS_examinados':not has_plans,
            'alcance_grupo_B': 'No localizado en estas fuentes; Permanencia no trae plan. No prueba inexistencia en UMAS.',
            'decision_Alexi':'____','aplicada':False,
            'motivo': 'Comparación por atributos; el nombre sólo descubre candidatos. Plan de otra sede no cubre el objetivo.' if has_plans else
                      'Sin plan identificable en listado/PROMEDIOS; revisar carrera en Permanencia sin asignarle una malla.'})
    order={'CALCE_UNICO':0,'CALCE_DEBIL':1,'CONFLICTO':2,'SIN_CALCE':3}
    resolved.sort(key=lambda x:(order[x['clasificacion']],x['numero_original']))
    new43.sort(key=lambda x:(order[x['clasificacion']],x['codigo_unico']))
    limits = [
        'Listado de planes del proceso AC 2026, no un catálogo certificado de admisión 2027.',
        'TIPO=Obl/OPC no clasifica regular/continuidad. REGIMEN=S puede discrepar con actividad trimestral; no cambiarlo.',
        'La conversión NIV_ACA es administrativa: el cálculo del nivel de ramo es diagnóstico C y no sustituye duración formal.',
        'H112B se declara candidata y no acredita aceptación PES; sus códigos y planes presentan cruces que deben conservarse.',
        'v20 declara aceptación_SIES NO_ACREDITADA en sus documentales: no afirmar cargas aceptadas. Evidencia b es documental anual atribuida.',
        'Conteos v20 son observaciones/contextos por período, no personas ni matrículas únicas; no sumarlos con PROMEDIOS ni Permanencia.',
        'Permanencia es foto 2026-10-27 sin plan; no permite confirmar ausencia de una malla ni vigencia histórica.',
        'PROMEDIOS son extractos solapados y con límites conocidos; ausencia no acredita inexistencia en UMAS.',
        'No se transfiere una versión nueva 2027 desde un código documental anterior. No se aplica ninguna propuesta.']
    profile_result={'clase':'B/C/E','fuentes':sources,'reglas_y_limites':limits,'perfiles':profiles,
        'hipotesis_prefijo_C': {'resultado':'PARCIAL: perfiles compatibles en varios programas; RECHAZADA como regla universal de prefijo',
            'casos':hyp, 'conteos':dict(Counter(x['estado'] for x in hyp))},
        'observaciones_v20_por_plan_codigo_anio':docs,'correspondencias_D_separadas':internals,
        'aceptacion_documentales_v20':dict(accept),'filas_PROMEDIOS_por_extraccion':source_counts}
    review={'hito':'H002c','clase':'C/E','ninguna_propuesta_aplicada':True,'limites':limits,
            'conteos':dict(Counter(x['clasificacion'] for x in resolved)),'casos':resolved}
    proposal={'hito':'H002c','clase':'C/E','ninguna_propuesta_aplicada':True,'limites':limits,
              'conteos_grupo_clase': {g:dict(Counter(x['clasificacion'] for x in new43 if x['grupo']==g)) for g in ['A','B']},'casos':new43}
    listed_sha=src['listado']['sha256']
    registered=any(x['sha256']==listed_sha for x in cat['catalogo'])
    addon={'clase':'B','tipo':'ANEXO_ADITIVO_CATALOGO_H002C','catalogo_original':'data/catalogo_fuentes/CATALOGO_FUENTES.json',
        'catalogo_original_modificado':False,'listado_ya_en_catalogo_central':registered,
        'fuentes_registradas_H002c':[dict(src['listado'], hoja='BBDD Bruta', encabezado=['Codcarr','Nombre_L','CODPESTUD','CODRAMO','NOMBRE','REGIMEN','TIPO','NIVEL','Sede'],
          datos_personales=False, origen='Archivo institucional entregado por Alexi; relectura completa de catálogo',
          alcance='AC 2026; no acredita vigencia de todos los planes ni admisión 2027')],
        'motivo':'Registrar fuente B sin modificar los hashes de entrada y resultados congelados de H002.'}
    # Verificar nuevamente integridad después de todas las lecturas.
    for x in sources:
        if sha(x['ruta']) != x['sha256']:
            raise ValueError('Fuente cambió durante lectura: '+x['id'])
    return sources,profile_result,review,proposal,addon


def render_review(v):
    lines=['# H002c · revisión de doce combinaciones, versión 2','','C/E · Propuestas sin aplicar; se conserva la revisión v1.','',
        'Evidencia (a): perfil explícito de malla y dimensiones. Evidencia (b): documental anual v20; aceptación SIES no acreditada. D internas separadas.','']
    for x in v['casos']:
        lines += [f"## Caso {x['numero_original']}. {x['codcarpr']} / {x['sede']} / {x['jornada']} — {x['clasificacion']}",'',
          'Perfil (a): '+(', '.join(x['opciones_perfil_a']) or 'sin opción completa'),
          'Documental (b): '+(', '.join(x['opciones_documentales_b']) or 'sin código de estas opciones'),'',
          '| Plan | Nivel / régimen | Perfil H112B semestres / tipo | a | b | Resultado |', '|---|---|---|---|---|---|']
        for p in x['planes']:
            pr=p['perfil_listado'];f=pr['perfil_formal_H112B'] if pr else []
            lines.append('| '+p['plan']+' | '+(str(pr['nivel_maximo'])+' / '+','.join(pr['REGIMEN']) if pr else 'no localizado')+' | '+str(f)+' | '+', '.join(p['codigos_perfil_a'])+' | '+', '.join(p['codigos_documentales_b'])+' | '+p['clasificacion']+' |')
            for q in p['por_opcion']:
                lines.append('- '+q['codigo_unico']+': '+('; '.join(q['atributos_sin_respaldo_o_distintos']) or 'perfil completo compatible')+'.')
        lines += ['', 'Opciones SIES (duración estudios y total separadas):', '']
        for o in x['opciones_SIES']:
            lines.append('- '+o['codigo_unico']+': estudios '+str(o['duracion_estudios_2027'])+'; total '+str(o['duracion_semestres'])+'; '+o['tipo_plan']+'; vigencia '+str(o['vigencia_2027'])+'; inicio observado '+str(o['inicio_oferta_observado'])+'.')
        lines += ['', 'Conteos documentales por plan, código y año (unidad: observaciones/contextos v20):','']
        for p in x['planes']:
            for d in p['observaciones_documentales']:
                lines.append('- '+p['plan']+' · '+d['anio']+' · '+d['codigo_sies']+': '+str(d['observaciones_contexto'])+'; '+str(d['aceptacion_SIES'])+'.')
        lines += ['',x['motivo'],'',x['admision_2027'],'','Decisión Alexi: ____','']
    lines += ['## Límites y fuentes','','Ver FUENTES_H002C.json, PERFIL_PLANES_H002C.json y CATALOGO_FUENTES_H002C.json.','',*['- '+x for x in v['limites']]]
    return '\n'.join(lines)+'\n'


def render43(v):
    lines=['# H002c · propuesta de planes para los 43 códigos','','C/E · Ninguna propuesta aplicada. El grupo B significa no localizado en fuentes examinadas, no inexistencia en UMAS.','']
    for x in v['casos']:
        lines += ['## '+x['codigo_unico']+' — '+x['nombre_carrera'],'',
                  'Grupo '+x['grupo']+' · '+x['clasificacion'], '',x['motivo'],'',
                  '| CODCARPR | Plan | Sede / jornada examinada | Perfil a | Documental b | Estado |','|---|---|---|---|---|---|']
        for p in x['planes_candidatos']:
            lines.append('| '+p['codcarpr']+' | '+p['plan']+' | '+p['sede']+'/'+p['jornada']+' | '+', '.join(p['codigos_perfil_a'])+' | '+', '.join(p['codigos_documentales_b'])+' | '+p['clasificacion']+' |')
            failed=sorted({k for q in p['por_opcion'] for k in q['atributos_sin_respaldo_o_distintos']})
            lines.append('- Controles faltantes/distintos: '+', '.join(failed)+'.')
        if not x['planes_candidatos']:
            lines.append('| — | No localizado | — | — | — | SIN_CALCE |')
        if x['presencia_Permanencia_sin_plan']:
            lines += ['', 'Permanencia registra carrera, pero no plan (no permite asignar CODPESTUD):',
                      *['- '+p['codcarpr']+' / sede '+p['sede']+' / jornada '+p['jornada']+': '+str(p['expedientes'])+' expedientes; total de ramos '+p['total_ramos']+'.' for p in x['presencia_Permanencia_sin_plan']]]
        lines += ['', 'Decisión Alexi: ____','']
    lines += ['## Límites','','Ver PERFIL_PLANES_H002C.json y FUENTES_H002C.json.','',*['- '+x for x in v['limites']]]
    return '\n'.join(lines)+'\n'


def render_profiles(v):
    lines=['# H002c · perfiles de planes y prueba del prefijo C','','B/C/E · Catálogo institucional, no asignación personal ni admisión 2027.','',
        'El listado tiene REGIMEN S/A y TIPO Obl/OPC. No se acreditó el significado de S/A con un catálogo de origen. No se asumen semestres; TIPO no es tipo de plan SIES.',
        'La conversión mostrada según el régimen explícito de PROMEDIOS es un diagnóstico administrativo C. La duración de H112B se conserva separada, con su estado candidato.', '',
        '## Hipótesis del prefijo C','',v['hipotesis_prefijo_C']['resultado'],'',
        '| CODCARPR | Plan | Sede | Nivel máximo | Estado | Perfil H112B | Perfil de grupo |', '|---|---|---|---:|---|---|---|']
    for x in v['hipotesis_prefijo_C']['casos']:
        lines.append('| '+x['codcarpr']+' | '+x['plan']+' | '+x['sede']+' | '+str(x['nivel_maximo'])+' | '+x['estado']+' | '+str(x['perfil_H112B'])+' | '+str(x['perfil_grupo'])+' |')
    lines += ['', 'CONG es Contabilidad General en RE: no toda palabra que comienza por CO identifica sede. COTEIQ/COTENS/COTFAR/COPCOM se observan en sede CO; no son continuidad por ese prefijo. CRPYA/CRPYB son excepciones sin perfil profesional 4/8 acreditado.', '',
        '## Catálogo por plan','','| CODCARPR | Plan | Sede | Ramos distintos | Máximo nivel | REGIMEN listado | Conversión condicionada PROMEDIOS | Semestres/tipo H112B |',
        '|---|---|---|---:|---:|---|---|---|']
    for x in v['perfiles']:
        lines.append('| '+x['codcarpr']+' | '+x['CODPESTUD']+' | '+x['sede_umas']+' | '+str(x['ramos_distintos'])+' | '+str(x['nivel_maximo'])+' | '+','.join(x['REGIMEN'])+' | '+str(x['conversion_si_regimen_PROMEDIOS'])+' | '+str(x['perfil_formal_H112B'])+' |')
    lines += ['', 'El JSON complementario conserva filas de origen, totales de 5810, diferencias de ramos, conteos de Permanencia y todas las incidencias por plan. No sumar extracciones PROMEDIOS solapadas.', '',
              '## Fuentes','','Ruta y SHA-256 completos en FUENTES_H002C.json. El listado no estaba en el catálogo central: queda registrado B en CATALOGO_FUENTES_H002C.json como anexo aditivo, preservando los hashes de H002.', '',
              *['- '+x for x in v['reglas_y_limites']]]
    return '\n'.join(lines)+'\n'


def main():
    verify='--verificar' in sys.argv
    sources,p,r,n,a=build()
    outputs={'FUENTES_H002C.json':dump(sources),'CATALOGO_FUENTES_H002C.json':dump(a),
        'PERFIL_PLANES_H002C.json':dump(p),'PERFIL_PLANES_H002C.md':render_profiles(p),'REVISION_CASO_A_CASO_12_v2.json':dump(r),
        'REVISION_CASO_A_CASO_12_v2.md':render_review(r),'PROPUESTA_PLANES_43.json':dump(n),'PROPUESTA_PLANES_43.md':render43(n)}
    # Primero comparar todos, luego escribir sólo los nuevos.
    for name,content in outputs.items():
        if (OUT/name).exists() and (OUT/name).read_text()!=content:
            raise ValueError('Salida existente distinta: '+name)
    for name,content in outputs.items():
        write_same(OUT/name,content,verify)
    manifest={'hito':'H002c','clase':'C','HEAD_base':'76830cfebe259b59989f47b0da221ee7a206d1e2',
        'fuentes':sources,'componentes':{str((OUT/name).relative_to(ROOT)):sha(OUT/name) for name in
            ['resolver_planes_h002c.py','qa_h002c.py','test_h002c.py','ESPECIFICACION_H002C.md']},
        'salidas':{name:hashlib.sha256(text.encode()).hexdigest() for name,text in outputs.items()},
        'sin_aplicar':True,'clasificacion_12':r['conteos'],'clasificacion_43':n['conteos_grupo_clase']}
    write_same(OUT/'MANIFEST_H002C.json',dump(manifest),verify)
    print(dump({'perfiles':len(p['perfiles']),'hipotesis_C':p['hipotesis_prefijo_C']['conteos'],
                '12':r['conteos'],'43':n['conteos_grupo_clase'],'reproduccion':verify}))


if __name__=='__main__':
    main()
