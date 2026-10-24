"""Consulta aislada del maestro H5, sin ejecutar ni modificar motores oficiales.

Contrato: docs/fase_5_maestro_equivalencias.md. ``validar_maestro`` comprueba
estructura y coherencia sin IO; ``cargar_maestro`` exige el SHA del manifiesto
y verifica los archivos de evidencia de cada regla acreditada. Las rutas de
evidencia relativas se resuelven desde la carpeta de maestro.json.

``resolver_umas`` devuelve código solo para reglas acreditadas cuyo conjunto
explícito de año/período/régimen contiene la consulta. Una candidatura única
no acredita equivalencia. ``consultar_sies`` consulta exclusivamente oferta
anual, sin afirmar equivalencia UMAS ni asignación individual de una malla.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re


COMPONENTES = ('institucion', 'sede', 'carrera', 'jornada', 'version')
CODIGO = re.compile(r'I(\d+)S(\d+)C(\d+)J(\d+)V(\d+)\Z')
SHA256 = re.compile(r'[0-9a-f]{64}\Z')
TIPOS_EVIDENCIA = {'EQUIVALENCIA_PLAN_SIES', 'AMBITO_TEMPORAL'}
MISSING_TOKENS = {'NULL', 'NONE', 'NAN'}
CONTEXT_FIELDS = ('codcarpr', 'plan_umas', 'sede_umas', 'jornada_umas')
LIST_FIELDS = (
    'oferta_anual', 'mrun_anual', 'universo_sies', 'planes_umas',
    'equivalencias_programa_2026', 'candidatos_plan_sies', 'reglas_efectivas',
)


def _trim(value):
    """Solo padding periférico; no normaliza tildes, mayúsculas ni códigos."""
    return '' if value is None else str(value).strip()


def _required_string(value, label):
    if not isinstance(value, str) or not value.strip() or value.strip().upper() in MISSING_TOKENS:
        raise ValueError(f'{label}: se exige texto no vacío')
    return value.strip()


def _year(value, label):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f'{label}: se exige año entero')
    return value


def _digest(value, label):
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        raise ValueError(f'{label}: SHA-256 inválido')
    return value


def _locator(value, label):
    if isinstance(value, str) and value.strip():
        return
    if isinstance(value, (dict, list)) and value:
        return
    raise ValueError(f'{label}: falta localizador de evidencia')


def _components(code, supplied, label):
    code = _required_string(code, label + '.codigo_unico')
    match = CODIGO.fullmatch(code)
    if not match or match[1] != '162':
        raise ValueError(f'{label}: Código Único SIES inválido o institución distinta')
    expected = dict(zip(COMPONENTES, match.groups()))
    if not isinstance(supplied, dict) or set(supplied) != set(COMPONENTES):
        raise ValueError(f'{label}: componentes SIES incompletos')
    if supplied != expected:
        raise ValueError(f'{label}: componentes SIES contradictorios')
    return expected


def _key(row, period):
    return (*(_trim(row.get(field)) for field in CONTEXT_FIELDS),
            _trim(row.get('nombre_interno')),
            period['anio'], _trim(period['periodo']), _trim(period['regimen']))


def _json_unique(values):
    distinct = {json.dumps(value, ensure_ascii=False, sort_keys=True): value for value in values}
    return [distinct[key] for key in sorted(distinct)]


def validar_maestro(maestro):
    """Rechaza esquemas, reglas o componentes inválidos sin leer archivos.

    Conflictos entre destinos de reglas estructuralmente acreditadas se
    conservan: resolver_umas devuelve CONFLICTO_REGLAS para su clave exacta.
    Varias reglas del mismo destino aportan evidencias acumulables.
    """
    if not isinstance(maestro, dict) or type(maestro.get('schema_version')) is not int or maestro['schema_version'] != 1:
        raise ValueError('Esquema del maestro no admitido')
    if maestro.get('periodo_objetivo') != [2007, 2026]:
        raise ValueError('Ámbito del maestro distinto del contrato 2007–2026')
    for field in LIST_FIELDS:
        if not isinstance(maestro.get(field), list):
            raise ValueError(f'{field}: se exige lista')
    sources = maestro.get('fuentes')
    if not isinstance(sources, dict):
        raise ValueError('fuentes: se exige mapa por identificador')
    for source_id, source in sources.items():
        _required_string(source_id, 'fuente.id')
        if not isinstance(source, dict):
            raise ValueError('Descriptor de fuente inválido')
        _required_string(source.get('path'), 'fuente.path')
        _digest(source.get('sha256'), 'fuente.sha256')

    offers = {}
    for row in maestro['oferta_anual']:
        if not isinstance(row, dict):
            raise ValueError('Fila de oferta inválida')
        year = _year(row.get('anio'), 'oferta.anio')
        if not 2007 <= year <= 2026:
            raise ValueError('Oferta fuera del ámbito del maestro')
        _components(row.get('codigo_unico'), row.get('componentes_sies'), 'oferta')
        code = _trim(row['codigo_unico'])
        if (year, code) in offers:
            raise ValueError('Clave año + Código Único duplicada en oferta')
        for field in ('nombre_carrera', 'tipo_plan_sies'):
            if not isinstance(row.get(field), str):
                raise ValueError(f'oferta.{field}: se exige literal de fuente')
        # MODALIDAD puede estar ausente en publicaciones históricas.
        if row.get('modalidad') is not None and not isinstance(row['modalidad'], str):
            raise ValueError('oferta.modalidad debe ser literal o null')
        if row.get('nombre_oferta_2026') is not None and not isinstance(row['nombre_oferta_2026'], str):
            raise ValueError('nombre_oferta_2026 debe ser literal o null')
        source = row.get('fuente')
        if not isinstance(source, dict) or source.get('id') not in sources:
            raise ValueError('Fuente de oferta no registrada')
        _locator(source.get('localizador'), 'oferta.fuente.localizador')
        offers[(year, code)] = row

    candidate_keys = set()
    for candidate in maestro['candidatos_plan_sies']:
        if not isinstance(candidate, dict):
            raise ValueError('Candidato inválido')
        for field in ('codcarpr', 'nombre_interno', 'plan_umas', 'sede_umas', 'codigo_unico', 'estado'):
            _required_string(candidate.get(field), 'candidato.' + field)
        journey = candidate.get('jornada_umas')
        if journey is not None:
            _required_string(journey, 'candidato.jornada_umas')
        if candidate.get('ambito_candidato') != 2026:
            raise ValueError('Candidato operativo extrapolado fuera de 2026')
        if not isinstance(candidate.get('nombre_plan_catalogo'), list):
            raise ValueError('candidato.nombre_plan_catalogo debe ser lista')
        ids = candidate.get('equivalencias_ids')
        if not isinstance(ids, list) or not ids or any(not isinstance(x, str) or not x.strip() for x in ids):
            raise ValueError('Candidato sin referencias a equivalencias de programa')
        match = CODIGO.fullmatch(_trim(candidate['codigo_unico']))
        if not match or match[1] != '162':
            raise ValueError('Código del candidato inválido')
        if 'componentes_sies' in candidate:
            _components(candidate['codigo_unico'], candidate['componentes_sies'], 'candidato')
        if match[4] == '3' and journey is not None:
            raise ValueError('Jornada SIES 3 del candidato 2026 no tiene jornada UMAS acreditada')
        candidate_key = tuple(_trim(candidate.get(field)) for field in
                              (*CONTEXT_FIELDS, 'nombre_interno', 'codigo_unico'))
        if candidate_key in candidate_keys:
            raise ValueError('Candidato duplicado; agregar procedencia en una relación')
        candidate_keys.add(candidate_key)
        if 'presencia_oferta_2026' in candidate:
            expected = (2026, _trim(candidate['codigo_unico'])) in offers
            if not isinstance(candidate['presencia_oferta_2026'], bool) or candidate['presencia_oferta_2026'] != expected:
                raise ValueError('Presencia anual contradictoria en candidato')

    rule_ids = set()
    for rule in maestro['reglas_efectivas']:
        if not isinstance(rule, dict) or rule.get('estado') != 'ACREDITADA':
            raise ValueError('Una regla efectiva debe estar ACREDITADA')
        rule_id = _required_string(rule.get('id'), 'regla.id')
        if rule_id in rule_ids:
            raise ValueError('Identificador de regla duplicado')
        rule_ids.add(rule_id)
        for field in (*CONTEXT_FIELDS, 'nombre_interno'):
            _required_string(rule.get(field), 'regla.' + field)
        components = _components(rule.get('codigo_unico'), rule.get('componentes_sies'), 'regla')
        periods = rule.get('periodos')
        if not isinstance(periods, list) or not periods:
            raise ValueError('Regla sin períodos explícitos')
        seen_periods = set()
        for period in periods:
            if not isinstance(period, dict):
                raise ValueError('Período de regla inválido')
            year = _year(period.get('anio'), 'regla.periodo.anio')
            _required_string(period.get('periodo'), 'regla.periodo.periodo')
            _required_string(period.get('regimen'), 'regla.periodo.regimen')
            key = _key(rule, period)
            if key in seen_periods:
                raise ValueError('Período duplicado dentro de una regla')
            seen_periods.add(key)
            offered = offers.get((year, _trim(rule['codigo_unico'])))
            if offered is None:
                raise ValueError('Regla sin oferta anual para su período')
            if offered['componentes_sies'] != components:
                raise ValueError('Regla y oferta anual tienen componentes diferentes')
        evidences = rule.get('evidencias')
        if not isinstance(evidences, list) or not evidences:
            raise ValueError('Regla sin evidencia documental')
        kinds = set()
        for evidence in evidences:
            if not isinstance(evidence, dict):
                raise ValueError('Evidencia inválida')
            kinds.add(_required_string(evidence.get('tipo'), 'evidencia.tipo'))
            _required_string(evidence.get('path'), 'evidencia.path')
            _digest(evidence.get('sha256'), 'evidencia.sha256')
            _locator(evidence.get('localizador'), 'evidencia.localizador')
            if not any(source['path'] == evidence['path'] and source['sha256'] == evidence['sha256']
                       for source in sources.values()):
                raise ValueError('Evidencia de regla no registrada en fuentes con la misma ruta y SHA')
        if not TIPOS_EVIDENCIA <= kinds:
            raise ValueError('Regla sin evidencia de equivalencia curricular y ámbito temporal')
    return maestro


def cargar_maestro(path, manifest_path=None):
    """Carga bytes verificados; manifiesto obligatorio, incluso sin reglas.

    El formato aceptado es ``manifest.outputs[nombre_archivo] = sha256``.
    Verifica cada evidencia acreditada desde su ruta explícita. No relee los
    archivos personales originales ni ejecuta pipelines institucionales.
    """
    path = Path(path).resolve()
    manifest_path = Path(manifest_path).resolve() if manifest_path else path.parent / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    expected = manifest.get('outputs', {}).get(path.name)
    _digest(expected, 'manifest.outputs.' + path.name)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('SHA-256 del maestro distinto del manifiesto')
    maestro = validar_maestro(json.loads(raw))
    verified = {}
    for rule in maestro['reglas_efectivas']:
        for evidence in rule['evidencias']:
            source = Path(evidence['path'])
            source = source if source.is_absolute() else path.parent / source
            source = source.resolve()
            expected = evidence['sha256']
            if source not in verified:
                with source.open('rb') as stream:
                    verified[source] = hashlib.file_digest(stream, 'sha256').hexdigest()
            if verified[source] != expected:
                raise ValueError('Fuente de evidencia alterada: ' + str(source))
    return maestro


def _base_result(state, *, anio, **values):
    return {'estado': state, 'anio': anio, 'codigo_unico': None,
            'acredita_asignacion_individual': False, **values}


def _input_year(anio):
    # El año se recibe como entero, sin convertir un texto o booleano en fecha.
    return isinstance(anio, int) and not isinstance(anio, bool)


def resolver_umas(maestro, *, anio=None, periodo=None, regimen=None, codcarpr=None,
                  nombre_interno=None, plan_umas=None, sede_umas=None, jornada_umas=None):
    """Consulta la clave completa; nunca promueve candidatos informativos.

    Año debe ser entero; los otros parámetros son textos exactos tras strip.
    No se transforman jornadas ni sedes internas mediante reglas retrospectivas.
    El nombre obligatorio restringe reglas y candidatos; los nombres del plan
    no constituyen alias alternativos del nombre de la equivalencia.
    Para consumir archivos se debe usar cargar_maestro antes de esta función:
    las funciones sobre diccionarios realizan validación estructural sin IO.
    """
    validar_maestro(maestro)
    inputs = dict(periodo=periodo, regimen=regimen, codcarpr=codcarpr,
                  nombre_interno=nombre_interno, plan_umas=plan_umas,
                  sede_umas=sede_umas, jornada_umas=jornada_umas)
    missing = [field for field, value in inputs.items()
               if not isinstance(value, str) or not value.strip() or value.strip().upper() in MISSING_TOKENS]
    if not _input_year(anio):
        missing.append('anio')
    if missing:
        return _base_result('ENTRADA_INCOMPLETA', anio=anio, campos_faltantes_o_invalidos=sorted(missing))
    inputs = {field: value.strip() for field, value in inputs.items()}
    period = {'anio': anio, 'periodo': inputs['periodo'], 'regimen': inputs['regimen']}
    key = _key(inputs, period)
    base = dict(anio=anio, clave=list(key), nombre_interno=inputs['nombre_interno'])
    if not maestro['periodo_objetivo'][0] <= anio <= maestro['periodo_objetivo'][1]:
        return _base_result('FUERA_AMBITO', **base)
    rules = [rule for rule in maestro['reglas_efectivas']
             if _trim(rule['nombre_interno']) == inputs['nombre_interno']
             and any(_key(rule, p) == key for p in rule['periodos'])]
    destinations = sorted({_trim(rule['codigo_unico']) for rule in rules})
    if len(destinations) > 1:
        return _base_result('CONFLICTO_REGLAS', **base, destinos_en_conflicto=destinations,
                            reglas_ids=sorted(rule['id'] for rule in rules))
    if destinations:
        code = destinations[0]
        offer = next(row for row in maestro['oferta_anual']
                     if row['anio'] == anio and _trim(row['codigo_unico']) == code)
        return _base_result('EQUIVALENCIA_ACREDITADA', **base, codigo_unico=code,
                            oferta_anual=offer, reglas_ids=sorted(rule['id'] for rule in rules),
                            evidencias=_json_unique(e for rule in rules for e in rule['evidencias']))
    context_candidates = [candidate for candidate in maestro['candidatos_plan_sies']
                          if candidate['ambito_candidato'] == anio
                          and all(_trim(candidate.get(field)) == inputs[field] for field in CONTEXT_FIELDS)]
    candidates = [candidate for candidate in context_candidates
                  if _trim(candidate['nombre_interno']) == inputs['nombre_interno']]
    candidates = sorted(candidates, key=lambda row: (_trim(row['codigo_unico']), _trim(row.get('id'))))
    annual_codes = {_trim(row['codigo_unico']) for row in maestro['oferta_anual'] if row['anio'] == anio}
    if not annual_codes:
        return _base_result('SIN_OFERTA_ANUAL', **base, motivo='SIN_COBERTURA_ANUAL', candidatos=candidates)
    if candidates and not any(_trim(row['codigo_unico']) in annual_codes for row in candidates):
        return _base_result('SIN_OFERTA_ANUAL', **base, motivo='CODIGO_NO_OBSERVADO', candidatos=candidates)
    if candidates:
        return _base_result('PENDIENTE_EVIDENCIA', **base, candidatos=candidates)
    if context_candidates:
        return _base_result('SIN_EQUIVALENCIA', **base, candidatos=[],
                            motivo='NOMBRE_INTERNO_NO_COINCIDE',
                            nombres_en_equivalencias=sorted({_trim(row['nombre_interno']) for row in context_candidates}))
    return _base_result('SIN_EQUIVALENCIA', **base, candidatos=[])


def consultar_sies(maestro, *, anio=None, codigo_unico=None):
    """Lee oferta por clave anual exacta; no consulta equivalencias UMAS."""
    validar_maestro(maestro)
    if (not _input_year(anio) or not isinstance(codigo_unico, str) or not codigo_unico.strip()
            or codigo_unico.strip().upper() in MISSING_TOKENS):
        return _base_result('ENTRADA_INCOMPLETA', anio=anio)
    code = codigo_unico.strip()
    if not maestro['periodo_objetivo'][0] <= anio <= maestro['periodo_objetivo'][1]:
        return _base_result('FUERA_AMBITO', anio=anio)
    rows = [row for row in maestro['oferta_anual'] if row['anio'] == anio and _trim(row['codigo_unico']) == code]
    mrun = [row for row in maestro['mrun_anual']
            if _trim(row.get('cat_periodo')) == str(anio) and _trim(row.get('codigo_unico')) == code]
    mrun = _json_unique(mrun)
    if not rows:
        reason = 'CODIGO_NO_OBSERVADO' if any(row['anio'] == anio for row in maestro['oferta_anual']) else 'SIN_COBERTURA_ANUAL'
        return _base_result('SIN_OFERTA_ANUAL', anio=anio, motivo=reason, codigo_consultado=code,
                            observaciones_mrun=mrun)
    return _base_result('OFERTA_ANUAL_LOCALIZADA', anio=anio, codigo_unico=code,
                        acredita_equivalencia_umas=False, oferta_anual=rows[0], observaciones_mrun=mrun)
