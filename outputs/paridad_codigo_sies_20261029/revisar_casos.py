#!/usr/bin/env python3
"""Doce fichas C/E: MU observada y puente v20 solo lectura, salida agregada.

No ejecuta el motor de admisión ni adjudica códigos o planes. Las filas MU no
vinculadas permanecen como cobertura familiar, nunca se atribuyen a un CODCARPR.
"""
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/paridad_codigo_sies_20261029'
DATA = ROOT / 'data/paridad_codigo_sies/20261029'
sys.path.insert(0, str(ROOT))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento, rut_normalizado


def text(value):
    if value is None:
        return ''
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def filehash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def identidad(row):
    if text(row['TIPO_DOC']).upper() != 'R' or row['N_DOC'] is None or row['DV'] is None:
        return None
    try:
        return rut_normalizado(text(row['N_DOC']) + '-' + text(row['DV']).upper())
    except ValueError:
        return None


def vinculo_unico(candidates):
    keys = {(cli, plan) for cli, plan, level in candidates}
    if len(keys) != 1:
        return None
    cli, plan = next(iter(keys))
    level = 'B/C_DOCUMENTAL_ANUAL' if any(x[2] == 'B/C_DOCUMENTAL_ANUAL' for x in candidates) else 'D_CORRESPONDENCIA_INTERNA'
    return plan, level


def construir():
    import openpyxl
    cfg = json.loads((DATA / 'FUENTES.json').read_text())
    src = {r['id']: r for r in cfg['fuentes']}
    for r in src.values():
        if filehash(ROOT / r['ruta']) != r['sha256']:
            raise ValueError('Fuente de catálogo alterada: ' + r['id'])
    catalog = json.loads((ROOT / src['catalogo_fuentes']['ruta']).read_text())
    wanted = '19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd'
    entries = [x for x in catalog['catalogo'] if x['sha256'] == wanted]
    if len(entries) != 1:
        raise ValueError('MU 142342 no es única en catálogo')
    mu_path = Path(entries[0]['ruta_consolidada'])
    if filehash(mu_path) != wanted:
        raise ValueError('MU original alterada')
    cases = json.loads((OUT / 'DECISIONES_PENDIENTES.json').read_text())['version_multiple_E_por_grupo']
    original_groups = {g['clave']: g for g in json.loads((ROOT / src['grupos']['ruta']).read_text())}
    baseline = json.loads((OUT / 'ESTADO_ANTES_H002B.json').read_text())
    if [(r['numero'], r['grupo']) for r in cases] != [(r['numero'], r['grupo']) for r in baseline['orden_12']]:
        raise ValueError('Cambió el orden de las doce combinaciones')
    table = json.loads((DATA / 'TABLA_PARIDAD_2026_2027.json').read_text())['filas']
    by = {(r['anio'], r['codigo_unico']): r for r in table}
    master = json.loads((ROOT / src['maestro']['ruta']).read_text())
    histories = {r['codigo_unico']: r for r in json.loads((ROOT / src['historias']['ruta']).read_text())}
    labels = {r['FOR_ING_ACT']: r['DESCRIPCION_MANUAL'] for r in csv.DictReader(
        (ROOT / src['gob_for_ing']['ruta']).open(), delimiter='\t')}
    # Conservar el campo enviado; las reglas/derivaciones de admisión no seleccionan versión.
    svc = DiccionarioSiesSeguimiento(root=ROOT)
    private_hash = svc.descriptor['base_privada']['sha256']
    indexed_entry = [e for e in catalog['catalogo_privadas'] if e['sha256'] == private_hash]
    if len(indexed_entry) != 1:
        raise ValueError('v20 no está catalogada de forma única')
    career_set = {x['codcarpr'] for x in cases}
    idx = defaultdict(list)
    other_dims = Counter()
    sql = '''SELECT persona,anio,carrera,sede,jornada,plan,codcli,
             json_extract(payload,'$.codigo_documental_atribuible'),
             json_extract(payload,'$.codigo_interno_adoptado')
             FROM observaciones WHERE CAST(anio AS INT) BETWEEN 2024 AND 2026'''
    for person, year, career, site, jour, plan, cli, doc, internal in svc.db.execute(sql):
        if career not in career_set:
            continue
        other_dims[(career, text(year), text(site), text(jour))] += 1
        if doc and internal and doc != internal:
            continue
        code = doc if doc else internal
        if not code or not plan:
            continue
        key = (person, text(year), career, text(site), text(jour), code)
        idx[key].append((cli, plan, 'B/C_DOCUMENTAL_ANUAL' if doc else 'D_CORRESPONDENCIA_INTERNA'))
    w = openpyxl.load_workbook(mu_path, read_only=True, data_only=True)
    it = w['BASE_RETENCION_MU'].iter_rows(values_only=True)
    header = next(it)
    keep = [k for k in header if k in {'ANIO_INFORMADO', 'TIPO_DOC', 'N_DOC', 'DV', 'COD_SED', 'COD_CAR',
            'JOR', 'VERSION', 'FOR_ING_ACT', 'ANIO_ING_ACT', 'VIG'}]
    positions = [header.index(k) for k in keep]
    mu = []
    for values in it:
        year = text(values[header.index('ANIO_INFORMADO')])
        if year not in ('2024', '2025', '2026'):
            continue
        row = {k: values[pos] for k, pos in zip(keep, positions)}
        row['codigo'] = 'I162S' + text(row['COD_SED']) + 'C' + text(row['COD_CAR']) + 'J' + text(row['JOR']) + 'V' + text(row['VERSION'])
        row['persona'] = identidad(row)
        mu.append(row)
    w.close()
    totals = Counter(text(r['ANIO_INFORMADO']) for r in mu)
    if totals != Counter({'2024': 1541, '2025': 2371, '2026': 4105}):
        raise ValueError('Universo MU inesperado, no ajustar denominador')
    source_evidence = {'MU': {'ruta': str(mu_path), 'sha256': wanted, 'hoja': 'BASE_RETENCION_MU',
        'catalogo': src['catalogo_fuentes']['ruta'], 'clase': 'B'},
        'v20': {'descriptor': src['v20_descriptor']['ruta'], 'sha256_descriptor': src['v20_descriptor']['sha256'],
                'base_privada_catalogada': indexed_entry[0]['ruta_consolidada'], 'sha256_base': private_hash,
                'modo': 'SOLO_LECTURA; no adjudicaciones nuevas', 'clase': 'C/D'},
        'FOR_ING_ACT': {'ruta': src['gob_for_ing']['ruta'], 'sha256': src['gob_for_ing']['sha256'],
                       'regla': 'Leer el valor informado; no derivarlo de nuevo ni elegir versión por vía.', 'clase': 'B/C'},
        'motor': {'ruta': src['for_ing_runtime']['ruta'], 'sha256': src['for_ing_runtime']['sha256'],
                  'localizador': '_load_for_ing_act_catalog, _resolve_for_ing_act_row',
                  'no_ejecutado': True, 'clase': 'C'}}
    cases_out = []
    for case in cases:
        families = {c.rsplit('V', 1)[0] for c in case['codigos_previos'] + case['codigos_2027_familia']}
        agg, coverage = Counter(), Counter()
        observed_codes = Counter()
        group_site = {'RE': '2', 'CO': '3', 'PTG': '4'}.get(case['sede_umas'])
        group_j = {'D': '1', 'V': '2', 'O': '4'}.get(case['jornada_umas'])
        for row in mu:
            code = row['codigo']
            if code.rsplit('V', 1)[0] not in families:
                continue
            year = text(row['ANIO_INFORMADO'])
            if row['persona'] is None:
                coverage[(year, 'E_DOCUMENTO_NO_COMPARABLE')] += 1
                continue
            candidates = idx.get((row['persona'], year, case['codcarpr'], group_site, group_j, code), [])
            keys = {(cli, plan) for cli, plan, level in candidates}
            if len(keys) != 1:
                coverage[(year, 'E_PLAN_EXPEDIENTE_MULTIPLE' if keys else 'E_SIN_ENLACE_DE_ESTA_COMBINACION')] += 1
                continue
            plan, level = vinculo_unico(candidates)
            form = text(row['FOR_ING_ACT'])
            agg[(year, plan, code, form, level, text(row['VIG']), text(row['ANIO_ING_ACT']))] += 1
            coverage[(year, 'VINCULO_OBSERVADO_UNICO')] += 1
            observed_codes[code] += 1
        options = []
        for code in sorted(set(case['codigos_previos']) | set(case['codigos_2027_familia'])):
            row = by.get((2027, code), by.get((2026, code)))
            history = histories.get(code, {})
            options.append({'codigo_unico': code, 'version': row['version'], 'nombre': row['nombre_carrera'],
                'tipo_plan': row['tipo_plan'], 'tipo_plan_codigo': row['tipo_plan_codigo'],
                'duracion_semestres': row['duracion_total_semestres'], 'vigencia_2027': row['vigencia_2027'],
                'inicio_oferta_observado': history.get('inicio_oferta'),
                'anio_inicio_declarado_2027': None, 'evidencia': row['evidencia'],
                'matriculas_MU_con_plan_vinculado': observed_codes[code]})
        # El inicio declarado es un atributo distinto del primer año observado.
        import io
        fields = [c for c in next(csv.reader(io.StringIO((ROOT / src['precarga5913']['ruta']).read_text()), delimiter=';'))
                  if c not in ('CODIGO_IES_NUM', 'CANTIDAD_MATRICULA_DFE', 'CANTIDAD_BENEFICIO_DFE')]
        all27 = list(csv.DictReader(io.StringIO((ROOT / src['carga_v06']['ruta']).read_text()), fieldnames=fields, delimiter=';'))
        declared = {'I162S'+r['COD_SEDE']+'C'+r['COD_CARRERA']+'J'+r['COD_JORNADA']+'V'+r['VERSION']: r['ANIO_INICIO'] for r in all27}
        for option in options:
            option['anio_inicio_declarado_2027'] = declared.get(option['codigo_unico'])
        plan_details = []
        for plan in case['planes_catalogados_candidatos']:
            plan_details.append({'plan_umas': plan, 'perfiles_codcarpr_gobernados': case['perfiles'],
                'duracion_semestres_malla_acreditada': None, 'tipo_plan_malla_acreditado': None,
                'duracion_tipo_confirmados_para_esta_malla': False,
                'fuente_perfil': case['fuente_perfil'],
                'estado': 'E_SIN_PERFIL_CURRICULAR_UNICO' if len(case['perfiles']) != 1 else 'C_PERFIL_DEL_GRUPO_NO_CERTIFICA_MALLA',
                'evidencia_DURACION_ESTUDIOS': original_groups[case['grupo']]['evidencia_perfil'],
                'evidencia': case['evidencia'] + [{'ruta': src['duracion']['ruta'], 'sha256': src['duracion']['sha256'],
                                                'localizador': 'filas de evidencia_perfil del grupo'}]})
        counts = [{'anio_MU': int(k[0]), 'plan_umas_observado': k[1], 'codigo_SIES_informado': k[2],
                   'FOR_ING_ACT': k[3], 'descripcion_via_gobernada_2026': labels.get(k[3], 'E_SIN_ETIQUETA_GOBERNADA'),
                   'respaldo_enlace': k[4], 'VIG_MU': k[5], 'cohorte_ingreso_actual_MU': k[6],
                   'matriculas': n} for k, n in sorted(agg.items())]
        coverage_rows = [{'anio_MU': int(y), 'estado': state, 'matriculas_familia': n} for (y, state), n in sorted(coverage.items())]
        contradictions = []
        observed = sorted(c for c, n in observed_codes.items() if n)
        if not observed:
            strength, proposal = 'SIN EVIDENCIA', 'Sin propuesta: no existe enlace MU–plan único de esta combinación.'
        elif len(observed) > 1:
            strength, proposal = 'DÉBIL', 'Revisar por plan y cohorte; no hay una opción global única.'
            contradictions.append('Las matrículas enlazadas documentan más de un código; no elegir por mayoría ni FOR_ING_ACT.')
        else:
            chosen = next(o for o in options if o['codigo_unico'] == observed[0])
            concordant = [chosen['duracion_semestres'], chosen['tipo_plan_codigo']] in case['perfiles']
            strength = 'FUERTE' if concordant and len(case['perfiles']) == 1 and chosen['vigencia_2027'] == '1' else 'DÉBIL'
            proposal = 'Referencia respaldada en MU: ' + observed[0] + '; solo propuesta C/E para Alexi.'
            if not concordant or len(case['perfiles']) != 1:
                contradictions.append('El perfil interno está ausente/múltiple o no coincide; el enlace observado no certifica duración curricular.')
            if chosen['vigencia_2027'] != '1':
                contradictions.append('El código observado no admite nuevos en la carga 2027; no trasladarlo a una versión nueva.')
        if len(families) > 1:
            contradictions.append('El grupo previo contiene varias familias C: no tratarlo como una misma carrera por nombre.')
        if any(x['estado'].startswith('E_') for x in coverage_rows):
            contradictions.append('Existe cobertura familiar sin enlace de plan de esta combinación; no atribuirla al alias ni sumarla como evidencia a favor.')
        cases_out.append({'numero': case['numero'], 'grupo': case['grupo'], 'codcarpr': case['codcarpr'],
            'sede_umas': case['sede_umas'], 'jornada_umas': case['jornada_umas'], 'estado_H002': 'VERSION_MULTIPLE_E',
            'opciones_SIES': options, 'planes_UMAS': plan_details, 'matriculas_por_plan_codigo_FOR': counts,
            'cobertura_familiar_no_atribuible_al_alias': coverage_rows,
            'contextos_v20_otras_dimensiones_no_utilizados': [
                {'anio': int(y), 'sede_SIES': s, 'jornada_SIES': j, 'contextos_no_matriculas': n}
                for (career, y, s, j), n in sorted(other_dims.items())
                if career == case['codcarpr'] and (s, j) != (group_site, group_j)],
            'total_MU_vinculado': sum(agg.values()), 'propuesta': proposal, 'fuerza': strength,
            'contradicciones_y_limites': contradictions,
            'fuentes': source_evidence, 'decision_Alexi': '____', 'aplicada': False})
    svc.close()
    if filehash(mu_path) != wanted or filehash(Path(indexed_entry[0]['ruta_origen'])) != private_hash:
        raise ValueError('Fuente privada cambió durante la lectura')
    return {'hito': 'H002b', 'clase': 'C/E', 'unidad': 'MATRICULAS_MU_FILAS; no personas ni filas de asignaturas',
        'regla_conteo': 'Todas las filas MU 2024–2026, incluido VIG 0. Cada fila cuenta a lo sumo una vez dentro de cada caso si el enlace exacto es único.',
        'no_sumar_casos': 'Las familias pueden repetirse entre alias/casos: no sumar sus conteos entre fichas.',
        'metodo_vinculo': 'Identidad con DV exacto + año + código MU literal + CODCARPR/sede/jornada v20; expediente y plan únicos entre contextos. B/C documental y D internos separados; sin enlace E.',
        'limitacion_plan': 'Plan observado en los respaldos del contexto; no certifica por sí solo vigencia histórica curricular.',
        'FOR_ING_ACT': 'Solo estratifica el valor informado. No se adopta versión según vía de ingreso; el catálogo manual 1..11 no se sustituye por restricciones del motor exploratorio antiguo.',
        'motor_exploratorio': {'reglas_y_traza_no_localizadas': ['control/for_ing_act_rules.tsv', 'control/for_ing_act_trace_long.tsv'],
            'no_ejecutado': True, 'contraste': 'config de abril restringe vías; evidencia P del runtime conserva 1..11 y documenta código 6. No se rederiva FOR ni se modifica el motor.'},
        'fuentes': source_evidence, 'totales_MU_sin_modificar': dict(totals), 'casos': cases_out}


def render(result):
    lines = ['# H002b · revisión caso a caso de doce combinaciones', '',
        'C/E: las doce siguen pendientes. No se aplica ninguna propuesta. Fuentes personales en memoria; salida solo agregada.', '',
        result['metodo_vinculo'], '', result['limitacion_plan'], '', result['FOR_ING_ACT'], '',
        result['no_sumar_casos'], '', 'Los conteos sin enlace son cobertura de familia, no matrículas acreditadas de ese alias.', '']
    for case in result['casos']:
        lines += ['## ' + str(case['numero']) + '. ' + case['codcarpr'] + ' / ' + case['sede_umas'] + ' / ' + case['jornada_umas'], '',
            '| Opción SIES | V | Tipo | Semestres | Vigencia 2027 | Primera oferta observada | Inicio declarado 2027 |',
            '|---|---|---|---:|---|---|---|']
        for x in case['opciones_SIES']:
            lines.append('| ' + x['codigo_unico'] + ' | ' + x['version'] + ' | ' + x['tipo_plan'] + ' | ' + x['duracion_semestres'] +
                ' | ' + str(x['vigencia_2027']) + ' | ' + str(x['inicio_oferta_observado']) + ' | ' + str(x['anio_inicio_declarado_2027']) + ' |')
        lines += ['', '### Planes UMAS candidatos', '', '| Plan | Perfiles duración total/tipo del grupo | Respaldo |', '|---|---|---|']
        for x in case['planes_UMAS']:
            lines.append('| ' + x['plan_umas'] + ' | ' + str(x['perfiles_codcarpr_gobernados']) + ' | ' + x['estado'] + ' |')
        if not case['planes_UMAS']:
            lines.append('| E: sin plan catalogado | E | No se inventa una malla |')
        lines += ['', 'El perfil del grupo procede de DURACION_ESTUDIOS y la gobernanza existente; no se adjudica automáticamente a todas sus mallas.', '',
            '### Matrículas MU vinculadas (B/C/D)', '',
            '| Año MU | Plan observado | Código informado | FOR_ING_ACT | Respaldo | VIG | Cohorte MU | Matrículas |',
            '|---|---|---|---|---|---|---|---:|']
        for x in case['matriculas_por_plan_codigo_FOR']:
            lines.append('| ' + ' | '.join(str(x[k]) for k in ('anio_MU', 'plan_umas_observado', 'codigo_SIES_informado', 'FOR_ING_ACT',
                         'respaldo_enlace', 'VIG_MU', 'cohorte_ingreso_actual_MU', 'matriculas')) + ' |')
        if not case['matriculas_por_plan_codigo_FOR']:
            lines.append('| — | E: sin enlace único | — | — | No determinado | — | — | 0 vinculadas |')
        if case['contextos_v20_otras_dimensiones_no_utilizados']:
            lines += ['', 'Contextos v20 de otras dimensiones, descartados (no son conteos de matrículas MU):', '']
            for x in case['contextos_v20_otras_dimensiones_no_utilizados']:
                lines.append('- Año ' + str(x['anio']) + ', sede ' + x['sede_SIES'] + ', jornada ' + x['jornada_SIES'] +
                             ': ' + str(x['contextos_no_matriculas']) + ' contextos. No se transfieren al caso.')
        lines += ['', '### Cobertura de la familia (no atribuir al alias)', '', '| Año | Estado de enlace | Filas MU |', '|---|---|---:|']
        for x in case['cobertura_familiar_no_atribuible_al_alias']:
            lines.append('| ' + str(x['anio_MU']) + ' | ' + x['estado'] + ' | ' + str(x['matriculas_familia']) + ' |')
        lines += ['', '**Propuesta (' + case['fuerza'] + '):** ' + case['propuesta'], '',
                  *['- ' + s for s in case['contradicciones_y_limites']], '',
                  'Evidencia: MU ' + result['fuentes']['MU']['sha256'] + '; v20 ' + result['fuentes']['v20']['sha256_base'] +
                  '; gobernanza FOR ' + result['fuentes']['FOR_ING_ACT']['sha256'] + '. Rutas completas en el JSON.', '',
                  'Decisión Alexi: ____', '']
    return '\n'.join(lines)


def main():
    result = construir()
    blob = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + '\n'
    from construir_paridad import sha
    text_md = render(result)
    # No publicar coincidencias de patrones personales; no incluir los valores detectados.
    for text_out in (blob, text_md):
        clean = re.sub(r'\b(?:[a-fA-F0-9]{64}|[a-fA-F0-9]{40})\b', 'HASH', text_out)
        if re.search(r'(?<!\w)(?:\d{1,2}\.\d{3}\.\d{3}|\d{7,8})-[0-9Kk](?!\w)', clean):
            raise ValueError('Posible identificador en salida: detenerse sin publicar valores')
    outputs = {OUT / 'REVISION_CASO_A_CASO_12.json': blob, OUT / 'REVISION_CASO_A_CASO_12.md': text_md}
    for path, value in outputs.items():
        if path.exists() and path.read_text() != value:
            raise ValueError('Salida existente distinta: conservar decisiones y generar nueva edición')
    for path, value in outputs.items():
        if not path.exists():
            path.write_text(value)
    print(json.dumps({'casos': 12, 'propuestas': [{'numero': x['numero'], 'codcarpr': x['codcarpr'],
          'fuerza': x['fuerza'], 'propuesta': x['propuesta'], 'matriculas_vinculadas': x['total_MU_vinculado']} for x in result['casos']],
          'ninguna_aplicada': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
