#!/usr/bin/env python3
"""H002: catálogo anual agregado, aislado de personas y motores de carga.

Entradas fijadas en FUENTES.json. Solo escribe en los dos destinos H002;
--verificar comprueba bytes sin sobrescribirlos. No consulta bases personales.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
DATA = 'data/paridad_codigo_sies/20261029'
OUT = 'outputs/paridad_codigo_sies_20261029'
CODE = re.compile(r'I162S(\d+)C(\d+)J(\d+)V(\d+)\Z')
MOD = {'1': 'Presencial', '2': 'Semipresencial', '3': 'No presencial'}
TIPO = {'1': 'Plan Regular', '2': 'Plan Especial', '3': 'Plan Regular de Continuidad'}
JORNADAS = {'D': '1', 'V': '2', 'O': '4'}
ESTADOS = ['CONTINUA', 'VERSION_MULTIPLE_RESUELTA', 'VERSION_MULTIPLE_E',
           'NUEVO_2027_CON_PLAN', 'APROBADA_D_2027', 'NUEVO_2027_SIN_PLAN_E', 'SIN_OFERTA_2027', 'FUERA_ALCANCE']
ESTADOS += ['PLAN_HISTORICO_SIN_ALUMNOS_VIGENTES', 'HISTORICO_SIN_MATRICULA_RECIENTE']


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()


def norm(value):
    text = unicodedata.normalize('NFD', str(value)).upper()
    return ' '.join(''.join(c for c in text if unicodedata.category(c) != 'Mn').split())


def componentes(code):
    m = CODE.fullmatch(code)
    if not m:
        raise ValueError('Código SIES de catálogo inválido: ' + code)
    return dict(zip(('cod_sede', 'cod_carrera', 'cod_jornada', 'version'), m.groups()))


def codigo(row):
    code = 'I162S{COD_SEDE}C{COD_CARRERA}J{COD_JORNADA}V{VERSION}'.format(**row)
    componentes(code)
    return code


def indexar_oferta(rows):
    out = {}
    for row in rows:
        code = codigo(row)
        if code in out:
            raise ValueError('Código duplicado en oferta: ' + code)
        out[code] = row
    return out


def perfil(row):
    return str(row.get('DURACION_TOTAL', '')), str(row.get('COD_TIPO_PLAN_CARRERA', ''))


def fuera(row):
    return (row.get('COD_NIVEL_GLOBAL') not in ('', None, '1') or
            any(w in norm(row.get('NOMBRE_CARRERA', '')) for w in
                ('DIPLOMADO', 'POSTITULO', 'POSTGRADO', 'EDUCACION CONTINUA', 'CURSOS Y DIPLOMADOS')))


def seleccionar(grupo, ofertas, perfil_interno, modalidades):
    """Selecciona un catálogo de nuevos; jamás V máxima ni continuidad por prefijo."""
    family_rows = [(c, x) for c, x in ofertas.items()
                   if c.rsplit('V', 1)[0] in grupo['familias'] and not fuera(x)]
    activos = [(c, x) for c, x in family_rows if x['VIGENCIA_CARRERA'] == '1']
    options = [c for c, _ in activos]
    if not activos:
        return {'estado': 'SIN_NUEVOS' if family_rows else 'SIN_OFERTA', 'seleccion': None,
                'opciones': [], 'motivo': 'No hay vigencia 1 en la familia; no es prueba de cierre.'}
    site = {'RE': '2', 'CO': '3', 'PTG': '4'}.get(grupo['sede'])
    jornada = JORNADAS.get(grupo['jornada'])
    if any(componentes(c)['cod_sede'] != site or componentes(c)['cod_jornada'] != jornada
           for c, _ in activos):
        return {'estado': 'E', 'seleccion': None, 'opciones': options,
                'motivo': 'Sede o jornada del grupo no concuerda con el código; no transferir J3/J4.'}
    if len(perfil_interno) != 1:
        return {'estado': 'E', 'seleccion': None, 'opciones': options,
                'motivo': 'Perfil interno de duración/tipo ausente o múltiple; no elegir por nombre o V.'}
    candidatos = [(c, x) for c, x in activos if perfil(x) in perfil_interno]
    if modalidades:
        candidatos = [(c, x) for c, x in candidatos if x['MODALIDAD'] in modalidades]
    if len(candidatos) != 1:
        return {'estado': 'E', 'seleccion': None, 'opciones': options,
                'compatibles_perfil': [c for c, _ in candidatos],
                'motivo': 'Ninguna o varias versiones compatibles; revisar perfil/malla y ámbito.'}
    chosen = candidatos[0][0]
    if chosen not in grupo['codigos_base']:
        return {'estado': 'E', 'seleccion': None, 'opciones': [chosen],
                'motivo': 'Versión fuera de los vínculos previos; requiere aprobación D de nueva correspondencia.'}
    return {'estado': 'UNICA', 'seleccion': chosen, 'opciones': [chosen],
            'motivo': 'Una vigencia 1 compatible con familia, perfil y modalidad respaldados.'}


def construir(root=ROOT):
    root = Path(root)
    config_raw = (root / DATA / 'FUENTES.json').read_bytes()
    config = json.loads(config_raw)
    refs = {e['id']: e for e in config['fuentes']}
    raw = {}
    def fuente_fijada(rec):
        p = root / rec['ruta']
        # Esta edición de H002 congela la instantánea v20 por hash.
        # El puntero operativo avanza independientemente del catálogo histórico.
        if rec['ruta'] == 'data/diccionario_sies_seguimiento/activo.json':
            p = root / 'data/diccionario_sies_seguimiento/archivo_v20_h013/activo.json'
        return p

    for id, rec in refs.items():
        p = fuente_fijada(rec)
        if not p.resolve().is_relative_to(root.resolve()):
            raise ValueError('Fuente fuera del repositorio')
        raw[id] = p.read_bytes()
        if sha(raw[id]) != rec['sha256']:
            raise ValueError('Fuente alterada: ' + rec['ruta'])

    def evidence(id, loc=''):
        e = refs[id]
        return {'ruta': e['ruta'], 'sha256': e['sha256'], 'clase': e['clase'], 'localizador': loc}

    groups = json.loads(raw['grupos'])
    master = json.loads(raw['maestro'])
    histories = {h['codigo_unico']: h for h in json.loads(raw['historias'])}
    cohortes = json.loads(raw['cohortes'])
    cobertura = json.loads(raw['cobertura'])
    cat27 = json.loads(raw['catalogo27'])
    assert sha(raw['evidencia27']) == cat27['revision_equivalencias']['sha256']
    assert sha(raw['duracion']) == master['fuentes']['duracion']['sha256']
    assert sha(raw['carga_v06']) == sha(raw['copia_congelada'])
    assert sha(raw['carga_v06']) == json.loads(raw['aceptacion_usuario'])['sha256_csv']
    durations = list(csv.DictReader(io.StringIO(raw['duracion'].decode('utf-8-sig')), delimiter='\t'))
    initial = list(csv.DictReader(io.StringIO(raw['precarga5913'].decode('utf-8-sig')), delimiter=';'))
    columns = [c for c in initial[0] if c not in
               ('CODIGO_IES_NUM', 'CANTIDAD_MATRICULA_DFE', 'CANTIDAD_BENEFICIO_DFE')]
    assert len(columns) == 48
    matrix = list(csv.reader(io.StringIO(raw['carga_v06'].decode('utf-8-sig')), delimiter=';'))
    assert all(len(r) == 48 for r in matrix)
    offers = indexar_oferta([dict(zip(columns, line), fila=str(i)) for i, line in enumerate(matrix, 1)])
    precarga = indexar_oferta(initial)
    old_codes = set(c for g in groups for c in g['codigos_base'])
    assert len(groups) == 135 and len(old_codes) == 106 and len(offers) == 161
    assert sum(len(g['codigos_base']) > 1 for g in groups) == 52
    dur_by = defaultdict(list)
    for i, row in enumerate(durations, 2):
        dur_by[row['CODIGO_UNICO']].append((i, row))

    def old_offer(code):
        annual = [x for x in master['oferta_anual'] if x['anio'] == 2026 and x['codigo_unico'] == code]
        if annual:
            x = annual[0]
            modes = {norm(v): k for k, v in MOD.items()}
            types = {norm(v): k for k, v in TIPO.items()}
            return {'NOMBRE_CARRERA': x['nombre_carrera'], 'MODALIDAD': modes.get(norm(x['modalidad_literal']), ''),
                    'COD_NIVEL_GLOBAL': '1' if norm(x['nivel_global']) == 'PREGRADO' else '3',
                    'COD_TIPO_PLAN_CARRERA': types.get(norm(x['tipo_plan_sies']), ''),
                    'DURACION_TOTAL': x['duracion_total'], 'DURACION_ESTUDIOS': x['duracion_estudios'],
                    'VIGENCIA_CARRERA': '', '_fuente': 'maestro', '_localizador':
                    'oferta_anual[anio=2026,codigo_unico=' + code + '] ' + str(x['fuente']),
                    '_calidad': 'OFERTA_ANUAL_2026_OBSERVADA'}
        if code in precarga:
            return dict(precarga[code], _fuente='precarga5913', _localizador=code,
                        _calidad='PRECARGA_INICIAL_2026_PROCESO_OFERTA_2027')
        if dur_by[code]:
            line, x = dur_by[code][0]
            return {'NOMBRE_CARRERA': x['NOMBRE_CARRERA'], 'MODALIDAD': x['MODALIDAD'],
                    'COD_NIVEL_GLOBAL': x['NIVEL_GLOBAL'], 'COD_TIPO_PLAN_CARRERA': x['TIPO_PLAN_CARRERA'],
                    'DURACION_TOTAL': x['DURACION_TOTAL'], 'DURACION_ESTUDIOS': x['DURACION_ESTUDIOS'],
                    'VIGENCIA_CARRERA': x['VIGENCIA'], '_fuente': 'duracion',
                    '_localizador': 'fila ' + str(line), '_calidad': 'SOLO_CATALOGO_OPERATIVO_NO_OFERTA_ANUAL_2026'}
        raise ValueError('Código 2026 sin atributos ni fallback explícito: ' + code)

    old = {code: old_offer(code) for code in sorted(old_codes)}
    by_code_group = defaultdict(list)
    by_group = {}
    plans_by = defaultdict(list)
    for plan in master['planes_umas']:
        for ctx in plan['contextos_catalogo']:
            plans_by[(ctx['Codcarr'], ctx['Sede'])].append(plan)
    h5_by = defaultdict(list)
    for x in master['candidatos_plan_sies']:
        h5_by[(x['codcarpr'], x['sede_umas'], x['jornada_umas'], x['codigo_unico'])].append(x)

    def plan_list(g, code=None):
        vals = h5_by[(g['codcarpr'], g['sede'], g['jornada'], code)] if code else []
        return sorted({x['plan_umas'] for x in vals} or
                      {x['CODPESTUD'] for x in plans_by[(g['codcarpr'], g['sede'])]})

    for i, g in enumerate(groups):
        profiles = {tuple(p) for p in g['perfiles_duracion_tipo']}
        method = g['fuente_perfil']
        if not profiles and len(g['codigos_base']) == 1:
            profiles = {perfil(old[g['codigos_base'][0]])}
            method = 'ATRIBUTOS_DEL_UNICO_CODIGO_PREVIO; NO_CERTIFICA_MALLA'
        modalities = {old[c]['MODALIDAD'] for c in g['codigos_base']
                      if not profiles or perfil(old[c]) in profiles} - {''}
        sel = seleccionar(g, offers, profiles, modalities)
        related = [c for c in offers if c.rsplit('V', 1)[0] in g['familias']]
        # La multiplicidad se registra por grupo, incluidas versiones nuevas del mismo programa.
        multiple = len(set(g['codigos_base']) | set(related)) > 1
        historical = Counter(x['resolucion']['estado'] for x in cohortes if x['clave_grupo'] == g['clave'])
        by_group[g['clave']] = {'grupo': g['clave'], 'codcarpr': g['codcarpr'], 'sede_umas': g['sede'],
             'jornada_umas': g['jornada'], 'planes_catalogados_candidatos': plan_list(g),
             'perfiles': sorted(profiles), 'fuente_perfil': method, 'modalidades': sorted(modalities),
             'codigos_previos': g['codigos_base'], 'codigos_2027_familia': sorted(related),
             'multiple': multiple, 'resolucion_nuevos_2027': sel,
             'ensayo_cohortes_estados': dict(sorted(historical.items())),
             'limite_historial': 'Ensayo C/E; no asignación de plan ni vigencia para ingreso 2027.',
             'evidencia': [evidence('grupos', 'índice ' + str(i)), evidence('historias'),
                           evidence('cohortes', 'clave_grupo=' + g['clave'])]}
        for c in g['codigos_base']:
            by_code_group[c].append(g)

    cat_by = {x['codigo_unico']: x for x in cat27['oferta']}

    def candidates(code, attrs, year):
        out = []
        for g in by_code_group[code]:
            gg = by_group[g['clave']]
            out.append({'codcarpr': g['codcarpr'], 'sede_umas': g['sede'], 'jornada_umas': g['jornada'],
                'plan_umas': plan_list(g, code), 'origen': 'GRUPO_PREVIO_EXACTO',
                'perfil_compatible': perfil(attrs) in {tuple(x) for x in gg['perfiles']},
                'duracion_tipo_perfil': gg['perfiles'], 'fuente_perfil': gg['fuente_perfil'],
                'estado_plan': 'CANDIDATO_CATALOGO_NO_EQUIVALENCIA_CURRICULAR_INDIVIDUAL',
                'evidencia': [evidence('grupos', g['clave']), evidence('maestro', 'planes_umas/contextos_catalogo')],
                'seleccion_grupo': gg['resolucion_nuevos_2027']})
        if year != 2027 or code in old_codes:
            return out
        # Reutilizar las relaciones explícitas ya gobernadas; no buscar por semejanza.
        prior = cat_by.get(code)
        if not prior:
            return out
        for e in prior['equivalencias']:
            internal_site = next((k for k, v in cat27['sedes_internas'].items() if v == prior['sede']), None)
            internal_j = next((k for k, v in JORNADAS.items() if v == prior['jornada']), None)
            dims = (prior['sede'] == componentes(code)['cod_sede'] and prior['jornada'] == componentes(code)['cod_jornada'])
            same = (prior['duracion_total'], prior['plan'], prior['modalidad_codigo']) == (
                attrs['DURACION_TOTAL'], attrs['COD_TIPO_PLAN_CARRERA'], attrs['MODALIDAD'])
            named = norm(e['nombre_interno']) == norm(attrs['NOMBRE_CARRERA'])
            p = plans_by[(e['codcarpr'], internal_site)]
            plans = sorted({x['CODPESTUD'] for x in p if any(norm(n) == norm(attrs['NOMBRE_CARRERA'])
                           for n in x['nombres_internos_catalogo'])})
            out.append({'codcarpr': e['codcarpr'], 'sede_umas': internal_site, 'jornada_umas': internal_j,
                'plan_umas': plans, 'origen': 'EQUIVALENCIA_EXPLICITA_CATALOGO_2027',
                'perfil_compatible': bool(dims and same and named and internal_site and internal_j),
                'duracion_tipo_perfil': [[prior['duracion_total'], prior['plan']]],
                'fuente_perfil': 'ATRIBUTOS_DE_EQUIVALENCIA_EXPLICITA_2027_NO_DURACION_CURRICULAR_INDEPENDIENTE',
                'estado_plan': 'PROPUESTA_E_REQUIERE_APROBACION_D' if plans else 'CODCARPR_RESPALDADO_SIN_PLAN_CATALOGADO',
                'evidencia': [evidence('catalogo27', 'oferta[codigo_unico=' + code + '].equivalencias'),
                             evidence('evidencia27', e.get('localizador', '')),
                             evidence('maestro', 'planes_umas[CODPESTUD=' + ','.join(plans) + ']')],
                'limite': 'Perfil formal del código en relación explícita. No acredita malla ni asignación temporal de cada plan.'})
        return out

    rows = []
    for year, universe in [(2026, old), (2027, offers)]:
        for code, attrs in sorted(universe.items()):
            future = offers.get(code)
            internals = candidates(code, attrs, year)
            resolutions = [by_group[g['clave']] for g in by_code_group[code]]
            ambiguous = [g for g in resolutions if g['multiple'] and g['resolucion_nuevos_2027']['estado'] == 'E']
            resolved = [g for g in resolutions if g['multiple'] and g['resolucion_nuevos_2027']['estado'] == 'UNICA']
            proposal = [c for c in internals if c['perfil_compatible'] and c['plan_umas']]
            if fuera(attrs):
                state, reason = 'FUERA_ALCANCE', 'Diplomado/postítulo/educación continua; exclusión D conservada.'
            elif not future:
                state, reason = 'SIN_OFERTA_2027', 'Ausente en V06. Sin prueba de cierre; no extrapolar vigencia.'
            elif year == 2027 and code not in old_codes:
                state = 'NUEVO_2027_CON_PLAN' if proposal else 'NUEVO_2027_SIN_PLAN_E'
                reason = ('Propuesta respaldada de catálogo y planes; requiere aprobación D, no se activa.' if proposal else
                          'Sin plan candidato suficientemente respaldado; una coincidencia nominal o otra jornada no basta.')
            elif ambiguous:
                state, reason = 'VERSION_MULTIPLE_E', 'Algún grupo interno vinculado conserva opciones/perfil sin resolver.'
            elif resolved:
                state, reason = 'VERSION_MULTIPLE_RESUELTA', 'Selección única para nuevos en grupos con perfil respaldado; ver asociaciones.'
            else:
                state, reason = 'CONTINUA', 'Mismo código presente en ambos catálogos; no certifica malla ni asignación individual.'
            vig = future['VIGENCIA_CARRERA'] if future else None
            if state == 'FUERA_ALCANCE' or vig in ('2', '3'):
                new = 'no'
            elif vig != '1' or state in ('VERSION_MULTIPLE_E', 'NUEVO_2027_CON_PLAN', 'NUEVO_2027_SIN_PLAN_E'):
                new = 'E'
            else:
                new = 'sí' if any(g['resolucion_nuevos_2027'].get('seleccion') == code for g in resolutions) else 'E'
            ev = [evidence('carga_v06', 'fila ' + future['fila'])] if future else []
            if year == 2026:
                ev.append(evidence(attrs['_fuente'], attrs['_localizador']))
            ev += [evidence('manual_octubre', 'páginas 22 y 28'), evidence('grupos', code)]
            if code in histories:
                ev.append(evidence('historias', 'codigo_unico=' + code))
            comp = componentes(code)
            rows.append({'anio': year, 'codigo_unico': code, **comp,
                'modalidad': MOD.get(attrs['MODALIDAD'], 'E'), 'modalidad_codigo': attrs['MODALIDAD'],
                'nivel_global': 'Pregrado' if attrs['COD_NIVEL_GLOBAL'] == '1' else 'Postítulo/otro',
                'nivel_global_codigo': attrs['COD_NIVEL_GLOBAL'],
                'tipo_plan': TIPO.get(attrs['COD_TIPO_PLAN_CARRERA'], 'E'),
                'tipo_plan_codigo': attrs['COD_TIPO_PLAN_CARRERA'], 'duracion_total_semestres': attrs['DURACION_TOTAL'],
                'nombre_carrera': attrs['NOMBRE_CARRERA'],
                'codcarpr': sorted({c['codcarpr'] for c in internals}),
                'sede_umas': sorted({c['sede_umas'] for c in internals if c['sede_umas']}),
                'jornada_umas': sorted({c['jornada_umas'] for c in internals if c['jornada_umas']}),
                'plan_umas': sorted({p for c in internals for p in c['plan_umas']}),
                'version_umas': None, 'version_umas_nota': 'No hay campo independiente acreditado; no descomponer el año de CODPESTUD.',
                'vigencia_2027': vig, 'vigencia_2027_texto': config['reglas_oficiales']['VIGENCIA_CARRERA']['dominio'].get(vig, 'E'),
                'admite_nuevos_segun_carga_2027': vig == '1', 'version_para_nuevos_2027': new,
                'estado': state, 'clase': 'C/D' if state == 'FUERA_ALCANCE' else 'C/E' if state in
                    ('VERSION_MULTIPLE_E', 'NUEVO_2027_CON_PLAN', 'NUEVO_2027_SIN_PLAN_E', 'SIN_OFERTA_2027') else 'C',
                'clase_atributos_2027': 'C; aceptación comunicada D, no comprobante técnico PES',
                'motivo': reason, 'atributos_2026_fuente': attrs.get('_calidad') if year == 2026 else None,
                'inicio_historia_oferta': histories.get(code, {}).get('inicio_oferta'),
                'candidatos_internos': internals, 'resoluciones_grupo': resolutions,
                'codigos_2027_misma_familia': sorted(c for c in offers if c.rsplit('V', 1)[0] == code.rsplit('V', 1)[0]),
                'evidencia': ev})

    approved_codes = []
    if 'decisiones_aprobadas' in raw:
        from aplicar_decisiones import aplicar_aprobaciones
        approved_codes = aplicar_aprobaciones(rows, json.loads(raw['decisiones_aprobadas']), master, cohortes,
                                              evidence('decisiones_aprobadas'))
    application_e = None
    decision_e = None
    if 'decisiones_aprobadas_v2' in raw:
        from aplicar_decisiones_h002e import aplicar
        decision_e = json.loads(raw['decisiones_aprobadas_v2'])
        application_e = aplicar(rows, by_group, decision_e, evidence('decisiones_aprobadas_v2'),
                               evidence('revision_h002d'), json.loads(raw['control_vigentes_h002e']), offers)
    # Listas por grupo/código, no personas. Las opciones incorporan atributos contrastables.
    def option(code):
        x = offers[code]
        return {'codigo_unico': code, 'tipo_plan': TIPO.get(x['COD_TIPO_PLAN_CARRERA']),
                'duracion_total': x['DURACION_TOTAL'], 'modalidad': MOD.get(x['MODALIDAD']),
                'vigencia_2027': x['VIGENCIA_CARRERA'], 'evidencia': evidence('carga_v06', 'fila ' + x['fila'])}
    pending_groups = []
    for key, g in sorted(by_group.items()):
        if not g['multiple'] or g['resolucion_nuevos_2027']['estado'] != 'E':
            continue
        relevant = [c for c in g['codigos_previos'] if not fuera(old[c])]
        if not relevant:
            continue
        pending_groups.append(dict(g, numero=len(pending_groups) + 1,
            opciones_detalle=[option(c) for c in g['resolucion_nuevos_2027']['opciones']],
            decision_solicitada='Acreditar perfil/plan y ámbito de la combinación. No elegir V por ordinal.'))
    proposals = [dict(r, numero=i) for i, r in enumerate(
        [r for r in rows if r['anio'] == 2027 and r['estado'] == 'NUEVO_2027_CON_PLAN'], 1)]
    decisions = {'version_multiple_E_por_grupo': pending_groups, 'nuevo_2027_con_plan': proposals,
        'nuevo_2027_sin_plan_E': [r for r in rows if r['anio'] == 2027 and r['estado'] == 'NUEVO_2027_SIN_PLAN_E'],
        'sin_oferta_2027': [r for r in rows if r['anio'] == 2026 and r['estado'] == 'SIN_OFERTA_2027'],
        'correspondencias_aprobadas_D': approved_codes,
        'requiere_aprobacion_D': bool(proposals), 'doce_y_43_no_aprobadas': True}
    if application_e:
        decisions.update(correspondencias_aprobadas_D=approved_codes + application_e['aprobadas_5'],
            correspondencias_plan_aprobadas_H002e=decision_e['correspondencias'],
            planes_historicos_2027=[by_group[k] for k in application_e['grupos_historicos_6']],
            codigos_historicos_sin_matricula_reciente=decision_e['codigos_historicos'],
            requiere_aprobacion_D=bool(proposals or pending_groups),doce_y_43_no_aprobadas=False,
            estado_vigente='H002e: 5 relaciones D; 6 grupos históricos D; CADMP y 37 códigos pendientes',
            observaciones_oferta='OBSERVACIONES_OFERTA_2027.md')
    counts = {str(year): {s: sum(r['anio'] == year and r['estado'] == s for r in rows) for s in ESTADOS}
              for year in (2026, 2027)}
    unique = {(r['anio'], r['codigo_unico']) for r in rows}
    qa = {'estado': 'PASS_CON_PENDIENTES_E', 'clase': 'C', 'controles': {
        '161_codigos_2027_una_vez': {r['codigo_unico'] for r in rows if r['anio'] == 2027} == set(offers),
        '106_codigos_2026_una_vez': {r['codigo_unico'] for r in rows if r['anio'] == 2026} == old_codes,
        'sin_duplicados_anio_codigo': len(unique) == len(rows) == 267,
        'suma_estados': all(sum(counts[str(y)].values()) == n for y, n in [(2026, 106), (2027, 161)]),
        'nuevos_2027_si_o_E': all(r['version_para_nuevos_2027'] in ('sí', 'E') for r in rows
            if r['anio'] == 2027 and r['admite_nuevos_segun_carga_2027'] and r['estado'] != 'FUERA_ALCANCE'),
        'vigencia_2_no_nuevos': all(r['version_para_nuevos_2027'] == 'no' for r in rows if r['vigencia_2027'] == '2'),
        'selecciones_unicas_con_perfil': all(len(g['resolucion_nuevos_2027']['opciones']) == 1 and len(g['perfiles']) == 1
            for g in by_group.values() if g['resolucion_nuevos_2027']['estado'] == 'UNICA'),
        'propuestas_con_equivalencia_dimensiones_perfil_y_plan': all(any(c['perfil_compatible'] and c['plan_umas']
            and c['origen'] == 'EQUIVALENCIA_EXPLICITA_CATALOGO_2027' for c in r['candidatos_internos']) for r in proposals),
        'solo_seis_correspondencias_D_autorizadas': len(approved_codes) in (0, 6), 'copia_congelada_igual_V06': True,
        'fuentes_fijadas_y_sin_alteracion': all(sha(fuente_fijada(x).read_bytes()) == x['sha256'] for x in refs.values()),
        'catalogo_no_usa_personas': True}, 'filas': len(rows), 'por_anio_estado': counts,
        'grupos': len(groups), 'grupos_previos_multiversion': 52,
        'grupos_version_multiple_E': len(pending_groups), 'codigos_fuera_grupos_2026': len(set(offers) - old_codes),
        'nuevos_con_PLAN_pendientes_D': len(proposals), 'cobertura_codigos_historicos_leidos': len(cobertura),
        'aceptacion_PES': config['criterio_aceptacion'],
        'advertencias': ['V06 no es descarga validada 6048; no hay comprobante técnico.',
            'H5 acredita candidatos, no mallas ni atribuciones individuales.',
            'Nuevos significa sin grupo interno 2026, no carrera creada en 2027.',
            'El perfil de equivalencias explícitas 2027 no es medición curricular independiente.',
            'Ausencia en oferta no demuestra cierre.', 'La conservación de fuentes no equivale a publicar cambios en Git.']}
    if application_e:
        qa['controles'].update(H002e_solo_20_filas_2027_autorizadas=len(application_e['filas_afectadas'])==20,
            H002e_2026_intacto=application_e['filas_2026_intactas'],
            H002e_11_codigos_D=len([r for r in rows if r['anio']==2027 and r['estado']=='APROBADA_D_2027'])==11,
            H002e_6_grupos_historicos_sin_version=sum(g.get('estado_paridad_2027')=='PLAN_HISTORICO_SIN_ALUMNOS_VIGENTES' and
                g['ambiguedad_historica']['version_asignada'] is None for g in by_group.values())==6,
            H002e_CADMP_unico_grupo_E=len(pending_groups)==1 and pending_groups[0]['codcarpr']=='CADMP',
            H002e_37_pendientes=len(decisions['nuevo_2027_sin_plan_E'])==37,
            H002e_6_C35=sum(r['anio']==2027 and r['estado']=='HISTORICO_SIN_MATRICULA_RECIENTE' for r in rows)==6)
        qa['aplicacion_H002e']=application_e
        qa['grupos_historicos_D']=6
        qa['advertencias'] += ['Seis grupos históricos no equivalen a seis códigos cerrados: los códigos compartidos conservan sus planes activos.',
            'Mallas/cohortes sin ámbito explícito conservan E; no se atribuyen personas.',
            'Reproducción de H002b–d: checkout aislado del commit de origen; no cambiar sus manifiestos congelados.']
    if not all(qa['controles'].values()):
        raise ValueError('QA bloqueante: ' + str(qa['controles']))
    payload = {'hito': config['hito'], 'fecha': config['fecha'], 'unidad': 'CODIGO_SIES_ANIO_CATALOGO_NO_PERSONAS',
        'fuente_2027': {'ruta': refs['carga_v06']['ruta'], 'sha256': refs['carga_v06']['sha256'],
                        'clase': 'C', 'aceptacion': config['criterio_aceptacion']},
        'conteos_por_anio_estado': counts, 'filas': rows}
    csvout = io.StringIO(newline='')
    fields = list(dict.fromkeys(k for row in rows for k in row))
    w = csv.DictWriter(csvout, fieldnames=fields, delimiter=';', lineterminator='\n')
    w.writeheader()
    for r in rows:
        w.writerow({k: json.dumps(v, ensure_ascii=False, sort_keys=True) if isinstance(v, (list, dict)) else
                    '' if v is None else str(v) for k, v in r.items()})
    readback = list(csv.DictReader(io.StringIO(csvout.getvalue()), delimiter=';'))
    qa['controles']['CSV_y_JSON_mismas_267_llaves'] = (
        {(int(r['anio']), r['codigo_unico']) for r in readback} == unique and len(readback) == 267)
    qa['controles']['conteo_independiente_por_anio'] = (
        Counter(int(r['anio']) for r in readback) == Counter({2026: 106, 2027: 161}))
    previous_path = root / OUT / 'ESTADO_ANTES_H002B.json'
    if previous_path.is_file() and not application_e:
        previous = {(x['anio'], x['codigo_unico']): x['estado'] for x in json.loads(previous_path.read_text())['estados']}
        changes = [(r['anio'], r['codigo_unico']) for r in rows if r['estado'] != previous[(r['anio'], r['codigo_unico'])]]
        qa['controles']['seis_D_y_resto_estados_intactos'] = (
            len(changes) == 6 and set(changes) == {(2027, c) for c in approved_codes})
        qa['aprobadas_D_2027'] = len(approved_codes)
    elif application_e:
        qa['aprobadas_D_2027'] = len(approved_codes) + len(application_e['aprobadas_5'])
    clean = re.sub(r'\b[a-fA-F0-9]{40}(?:[a-fA-F0-9]{24})?\b', 'HASH', encode(payload).decode())
    private = [r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b',
               r'(?<!\w)(?:\d{1,2}\.\d{3}\.\d{3}|\d{7,8})-[0-9Kk](?!\w)',
               r'(?<!\w)(?:19|20)\d{2}[1-5][A-Z]{2,12}\d{3,}(?!\w)']
    qa['controles']['sin_patrones_identificadores_en_tabla'] = not any(re.search(p, clean) for p in private)
    if not all(qa['controles'].values()):
        raise ValueError('QA de serialización/privacidad bloqueante')
    md = ['# H002 · decisiones de catálogo pendientes', '',
          'Sin personas. H002b aprobó seis correspondencias código–CODCARPR; las doce y las 43 no se aprobaron.', '',
          '## VERSION_MULTIPLE_E: combinaciones internas', '']
    for g in pending_groups:
        md += [str(g['numero']) + '. **' + g['codcarpr'] + ' / ' + g['sede_umas'] + ' / ' + g['jornada_umas'] + '**. '
               + g['resolucion_nuevos_2027']['motivo'],
               '   Perfil respaldado: ' + str(g['perfiles']) + '. Planes candidatos: ' + ', '.join(g['planes_catalogados_candidatos']) + '.',
               '   Opciones vigencia 1: ' + '; '.join(x['codigo_unico'] + ' (' + x['tipo_plan'] + ', ' + x['duracion_total'] + ' sem.)'
                   for x in g['opciones_detalle']) + '.',
               '   Evidencia: ' + refs['grupos']['ruta'] + ' SHA-256 ' + refs['grupos']['sha256'] + '; V06 ' + refs['carga_v06']['sha256'] + '.', '']
    md += ['## NUEVO_2027_CON_PLAN: aprobación D requerida', '']
    for r in proposals:
        md += [str(r['numero']) + '. **' + r['codigo_unico'] + '** · ' + r['nombre_carrera'] + '.',
               '   Opciones internas: ' + ', '.join(r['codcarpr']) + '; planes: ' + ', '.join(r['plan_umas']) + '.',
               '   ' + r['tipo_plan'] + ', ' + r['duracion_total_semestres'] + ' semestres, ' + r['modalidad'] + '.',
               '   Evidencia: catálogo explícito 2027 ' + refs['catalogo27']['sha256'] + '; H5 ' + refs['maestro']['sha256'] + '.', '']
    md += ['## Seis correspondencias aprobadas D · H002b', '',
           'La decisión vive en data/paridad_codigo_sies/20261029/DECISIONES_APROBADAS.json. '
           'Los planes múltiples por cohorte conservan E dentro de APROBADA_D_2027.', '']
    for r in rows:
        if r['estado'] == 'APROBADA_D_2027':
            md.append('- ' + r['codigo_unico'] + ' → ' + '/'.join(r['codcarpr']) + ': ' + r['estado_plan_por_cohorte'])
    md.append('')
    for title, subset in [('NUEVO_2027_SIN_PLAN_E', decisions['nuevo_2027_sin_plan_E']), ('SIN_OFERTA_2027', decisions['sin_oferta_2027'])]:
        md += ['## ' + title, '', '| Código | Nombre | CODCARPR ya respaldado | Motivo |', '|---|---|---|---|']
        for r in subset:
            md.append('| ' + r['codigo_unico'] + ' | ' + r['nombre_carrera'] + ' | ' + ', '.join(r['codcarpr']) + ' | ' + r['motivo'] + ' |')
        md += ['']
    if application_e:
        from aplicar_decisiones_h002e import pendientes_md
        md = pendientes_md(rows, decisions, decision_e).splitlines()
    outputs = {DATA + '/TABLA_PARIDAD_2026_2027.json': encode(payload), DATA + '/TABLA_PARIDAD_2026_2027.csv': csvout.getvalue().encode(),
        OUT + '/DECISIONES_PENDIENTES.json': encode(decisions), OUT + '/DECISIONES_PENDIENTES.md': '\n'.join(md).encode(),
        OUT + '/QA.json': encode(qa), OUT + '/RESOLUCIONES_POR_GRUPO.json': encode(sorted(by_group.values(), key=lambda g: g['grupo']))}
    if application_e:
        from aplicar_decisiones_h002e import observaciones_md
        states = ['| Estado | 2026 | 2027 |', '|---|---:|---:|']
        states += ['| ' + s + ' | ' + str(counts['2026'][s]) + ' | ' + str(counts['2027'][s]) + ' |' for s in ESTADOS
                   if counts['2026'][s] or counts['2027'][s]]
        readme = raw['readme_h002e'].decode().replace('{{CONTEOS_ESTADOS}}', '\n'.join(states))
        outputs[DATA + '/README.md'] = readme.encode()
        outputs[OUT + '/OBSERVACIONES_OFERTA_2027.md'] = observaciones_md(decision_e).encode()
    outputs[DATA + '/MANIFEST.json'] = encode({'hito': config['hito'], 'fecha': config['fecha'],
        'commit_contexto': config['commit_contexto'], 'entradas': config['fuentes'],
        'configuracion': {'ruta': DATA + '/FUENTES.json', 'sha256': sha(config_raw)},
        'generador': {'ruta': OUT + '/construir_paridad.py', 'sha256': sha(Path(__file__).read_bytes())},
        'componente_decisiones': {'ruta': OUT + '/aplicar_decisiones.py',
                                  'sha256': sha((root / OUT / 'aplicar_decisiones.py').read_bytes())},
        'auxiliares_H002b': {name: sha((root / name).read_bytes()) for name in (
            OUT + '/revisar_casos.py', OUT + '/cruzar_planes_2027.py', OUT + '/test_h002b.py',
            'data/paridad_codigo_sies/PLANTILLA_PLANES_UMAS_2027.tsv') if (root / name).is_file()},
        'especificacion': {'ruta': DATA + '/README.md', 'sha256': sha(outputs.get(DATA + '/README.md', (root / DATA / 'README.md').read_bytes()))},
        'aplicacion_H002e': {'base': config.get('activacion_H002e'),
            'componente': {'ruta': OUT + '/aplicar_decisiones_h002e.py', 'sha256': sha((root / OUT / 'aplicar_decisiones_h002e.py').read_bytes())}}
            if application_e else None,
        'auxiliares_H002e': {OUT + '/' + name: sha((root / OUT / name).read_bytes()) for name in
            ('test_h002e.py', 'qa_h002e.py', 'ESPECIFICACION_H002E.md', 'CONTROL_VIGENTES_H002E.json')}
            if application_e else {},
        'salidas': {p: sha(b) for p, b in sorted(outputs.items())},
        'reglas_oficiales': config['reglas_oficiales'], 'datos_personales': False, 'atribuciones_personales_modificadas': False})
    if application_e:
        milestone_rel = 'manifests/milestones/H002-PARIDAD-CODIGO-SIES-2027/REGISTRO.json'
        register = json.loads((root / milestone_rel).read_text())
        register['manifest_sha256'] = sha(outputs[DATA + '/MANIFEST.json'])
        register.update(actualizacion='H002e',estado='CATALOGO_CON_11_RELACIONES_D_Y_PENDIENTES_EXPLICITOS',
            conteos=counts,correspondencias_aprobadas_D=11,decision=DATA + '/DECISIONES_APROBADAS_v2.json',
            doce_combinaciones_sin_aplicar=False,**{'43_sin_plan_sin_resolver':False},
            pendientes_sin_plan=37,QA_entrega=OUT + '/QA_H002E.json',
            fichas=OUT + '/REVISION_CASO_A_CASO_12_v3.md',
            commit_base_aplicacion_H002e=config['activacion_H002e']['HEAD_base'],
            publicacion='Verificar el commit que contiene el registro y la referencia remota; el archivo no acredita por sí solo push.')
        register.pop('commit_realizado',None)
        register.pop('push_realizado',None)
        register['aplicacion_H002e'] = {'decision': DATA + '/DECISIONES_APROBADAS_v2.json',
            'fuente': decision_e['fuente'], 'aprobaciones_nuevas': 5, 'grupos_historicos': 6,
            'codigos_C35_historicos': 6, 'pendientes': 'CADMP y 37 códigos',
            'ambito': 'Catálogo 2027; 2026 intacto; no modifica v20 ni oferta.'}
        outputs[milestone_rel] = encode(register)
        milestone_readme = 'manifests/milestones/H002-PARIDAD-CODIGO-SIES-2027/README.md'
        text = (root / milestone_readme).read_text()
        marker = '## Estado vigente H002e'
        if marker in text:
            text = text[:text.index(marker)].rstrip() + '\n\n'
        else:
            text = text.rstrip() + '\n\n'
        text += (marker + '\n\nD · Alexi, 29-10-2026. Esta sección reemplaza los estados pendientes de los antecedentes anteriores: '
                 '11 códigos con relaciones D (6 previas + 5 nuevas), 6 grupos históricos con ambigüedad E sin versión, '
                 '6 códigos C35 históricos. Pendientes: CADMP y 37 códigos sin planes. Las 106 filas 2026 se conservan. '
                 'Los códigos compartidos no se cierran por retirar un plan.\n\n'
                 'Decisión: DECISIONES_APROBADAS_v2.json. QA vigente: QA_H002E.json; QA.json es el control del constructor. '
                 'Los informes H002b–d se conservan y se reproducen en checkout aislado del commit de origen. '
                 'Observaciones de oferta: OBSERVACIONES_OFERTA_2027.md; no se modifica PES ni v20.\n')
        outputs[milestone_readme] = text.encode()
    return outputs, qa


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--verificar', action='store_true', help='Verifica bytes de todas las salidas, sin escritura')
    ap.add_argument('--aplicar-h002e', action='store_true', help='Sustituye sólo salidas autorizadas desde el HEAD/huellas previos H002e')
    args = ap.parse_args()
    outputs, qa = construir()
    baseline = None
    if args.aplicar_h002e:
        import subprocess
        if args.verificar or not qa.get('aplicacion_H002e'):
            raise ValueError('Promoción H002e requiere decisiones activas y no acepta --verificar')
        baseline = json.loads((ROOT / OUT / 'ESTADO_INICIAL_H002E.json').read_text())
        if subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() != baseline['HEAD']:
            raise ValueError('HEAD distinto del autorizado para aplicar H002e')
    for rel, raw in outputs.items():
        p = ROOT / rel
        if args.verificar:
            if not p.is_file() or p.read_bytes() != raw:
                raise ValueError('Salida no reproducible: ' + rel)
        elif p.exists() and p.read_bytes() != raw:
            if not baseline or sha(p.read_bytes()) != baseline['protegidos'].get(rel):
                raise ValueError('Salida existente distinta del respaldo autorizado: ' + rel)
    if not args.verificar:
        for rel, raw in outputs.items():
            p = ROOT / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            if not p.exists() or baseline is not None:
                p.write_bytes(raw)
    print(json.dumps({'estado': qa['estado'], 'filas': qa['filas'], 'conteos': qa['por_anio_estado'],
                      'grupos_E': qa['grupos_version_multiple_E'], 'reproduccion': args.verificar}, ensure_ascii=False))


if __name__ == '__main__':
    main()
