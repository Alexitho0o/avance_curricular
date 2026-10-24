"""Reconstrucción pura del catálogo UMAS (contrato H4, fase_4_planes_asignaciones_umas).

API: ``build_catalog(rows)`` recibe diccionarios con los nombres literales del
listado de planes y ``_fila`` (número entero de fila Excel). No lee archivos,
no modifica la entrada y no escribe salidas. Devuelve cuatro objetos JSON:
``catalogo_planes`` y ``estructura_asignaturas`` (listas),
``comparaciones_planes`` (lista) y ``resumen`` (diccionario).

Las claves de comparación solo eliminan espacios exteriores. Los valores
originales se conservan en ``atributos_origen`` y ``filas_expansion``. Un grupo
es CODPESTUD/CODRAMO/NIVEL; las filas de requisitos y equivalencias no son
asignaturas adicionales. RamoEquiv puede expresar PLAN/RAMO: ambos componentes
se conservan y validan literalmente contra el catálogo, sin convertir esa
referencia en una homologación estudiantil. Ninguna salida asigna VERSION SIES,
vigencia curricular, fecha de aprobación o sucesión histórica entre planes.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
import hashlib
import json


COURSE_FIELDS = (
    'NOMBRE', 'REGIMEN', 'TIPO', 'SESIONES', 'PORC_NOTA_PRES',
    'PORC_NOTA_EXam', 'CREDITO', 'Clase', 'ORDENRAMO',
    'HOR_TEO', 'HOR_PRAC', 'HOR_AYUD',
)
PLAN_FIELDS = ('Codcarr', 'Nombre_L', 'NOMPESTUD', 'Sede')
EXPANSION_FIELDS = (
    'Orden', 'RamoEquiv', 'DescRamoEquiv', 'RamoReq', 'DescRamoReq',
    'RegimenReq', 'TipoReq', 'SesionesReq', 'SIGLA', 'NroLinea',
)


def literal_key(value):
    """Normaliza exclusivamente padding de extracción, sin interpretar códigos."""
    return '' if value is None else str(value).strip()


def _packed(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _unique_raw(values):
    """Conserva incluso la distinción de origen entre None, vacío y espacios."""
    distinct = {_packed(value): value for value in values}
    return [distinct[key] for key in sorted(distinct)]


def _normalized_values(rows, field):
    return sorted({literal_key(row.get(field)) for row in rows})


def _role(row):
    equiv, req = (literal_key(row.get(field)) for field in ('RamoEquiv', 'RamoReq'))
    if not equiv and not req:
        return 'BASE'
    if equiv.endswith(':') or req.endswith(':'):
        return 'ENCABEZADO_RELACION'
    if equiv and not req:
        return 'DETALLE_EQUIVALENCIA'
    if req and not equiv:
        return 'DETALLE_REQUISITO'
    return 'RELACION_MIXTA_NO_INTERPRETADA'


def _relation_details(rows, kind, course_index):
    """Agrupa referencias literales y conserva diferencias de descripción."""
    field = 'RamoEquiv' if kind == 'equivalencia' else 'RamoReq'
    desc = 'DescRamoEquiv' if kind == 'equivalencia' else 'DescRamoReq'
    by_literal = defaultdict(list)
    for row in rows:
        code = literal_key(row.get(field))
        if code and not code.endswith(':'):
            by_literal[code].append(row)
    result = []
    for code, source_rows in sorted(by_literal.items()):
        item = {
            'literal': code,
            'valores_literales_origen': _unique_raw(row.get(field) for row in source_rows),
            'descripciones_origen': _unique_raw(row.get(desc) for row in source_rows),
            'filas_fuente': sorted(row['_fila'] for row in source_rows),
        }
        if kind == 'equivalencia':
            parts = code.split('/')
            if len(parts) == 2 and all(parts):
                # No quitar espacios interiores: forman parte de la referencia.
                plan, ramo = parts
                item.update(plan_destino=plan, ramo_destino=ramo)
                item['estado_destino'] = (
                    'PLAN_NO_OBSERVADO' if plan not in course_index else
                    'RAMO_NO_OBSERVADO_EN_PLAN' if ramo not in course_index[plan] else
                    'REFERENCIA_OBSERVADA'
                )
            else:
                item.update(plan_destino=None, ramo_destino=None,
                            estado_destino='FORMATO_NO_DESGLOSADO')
        else:
            plan = literal_key(source_rows[0].get('CODPESTUD'))
            item.update(plan_destino=plan, ramo_destino=code)
            item['estado_destino'] = (
                'REFERENCIA_OBSERVADA' if code in course_index.get(plan, set()) else
                'RAMO_NO_OBSERVADO_EN_PLAN'
            )
            item['atributos_requisito_origen'] = {
                field: _unique_raw(row.get(field) for row in source_rows)
                for field in ('RegimenReq', 'TipoReq', 'SesionesReq')
            }
        result.append(item)
    return result


def build_catalog(rows):
    """Agrupa estructuras conservando contradicciones y devuelve evidencia H4.

    Cada plan conserva listas de carreras/sedes: ``estado_contexto`` solo es
    ``UNICO`` si ambas tienen un único valor no vacío. Solo esos planes se
    comparan entre sí dentro de la misma carrera y sede. Un atributo vacío se
    conserva y una combinación vacío/no vacío permanece visible como conflicto.
    Los identificadores incompletos se agrupan pero quedan marcados; no se
    fabrican claves, fechas ni equivalencias para completarlos.
    """
    rows = list(rows)
    for row in rows:
        if not isinstance(row.get('_fila'), int) or isinstance(row['_fila'], bool):
            raise ValueError('Cada fila del catálogo necesita _fila entero')
        if any(field not in row for field in ('CODPESTUD', 'CODRAMO', 'NIVEL')):
            raise ValueError('Faltan columnas de la clave plan/ramo/nivel')
    if len({row['_fila'] for row in rows}) != len(rows):
        raise ValueError('Localizadores _fila duplicados en el catálogo')
    rows = sorted(rows, key=lambda row: row['_fila'])
    by_group, by_plan = defaultdict(list), defaultdict(list)
    course_index = defaultdict(set)
    for row in rows:
        key = tuple(literal_key(row[field]) for field in ('CODPESTUD', 'CODRAMO', 'NIVEL'))
        by_group[key].append(row)
        by_plan[key[0]].append(row)
        if key[0] and key[1]:
            course_index[key[0]].add(key[1])

    structures, structures_by_plan = [], defaultdict(list)
    roles = Counter()
    all_fields = sorted({field for row in rows for field in row if not field.startswith('_')})
    for (plan, ramo, level), group in sorted(by_group.items()):
        normalized_attrs = {field: _normalized_values(group, field) for field in COURSE_FIELDS}
        conflicts = {field: values for field, values in normalized_attrs.items() if len(values) > 1}
        expansion = []
        for row in group:
            role = _role(row)
            roles[role] += 1
            expansion.append({'fila': row['_fila'], 'rol': role,
                              **{field: row.get(field) for field in EXPANSION_FIELDS}})
        structure = {
            'CODPESTUD': plan, 'CODRAMO': ramo, 'NIVEL': level,
            'estado_clave': 'COMPLETA' if plan and ramo and level else 'INCOMPLETA',
            'atributos_origen': {
                field: _unique_raw(row.get(field) for row in group) for field in all_fields
            },
            'atributos_curso_comparacion': normalized_attrs,
            'conflictos_atributos_curso': conflicts,
            'filas_fuente': [row['_fila'] for row in group],
            'filas_expandidas': len(group),
            'filas_base': [row['_fila'] for row in group if _role(row) == 'BASE'],
            'filas_expansion': expansion,
            'encabezados_relaciones': [item for item in expansion if item['rol'] == 'ENCABEZADO_RELACION'],
            'equivalencias_detalle': _relation_details(group, 'equivalencia', course_index),
            'requisitos_detalle': _relation_details(group, 'requisito', course_index),
        }
        structures.append(structure)
        structures_by_plan[plan].append(structure)

    catalog, family_plans = [], defaultdict(list)
    fingerprints = {}
    for plan, group in sorted(by_plan.items()):
        attrs = {field: _normalized_values(group, field) for field in PLAN_FIELDS}
        context_unique = all(len(attrs[field]) == 1 and attrs[field][0]
                             for field in ('Codcarr', 'Sede'))
        plan_structures = structures_by_plan[plan]
        keys = {(item['CODRAMO'], item['NIVEL']) for item in plan_structures}
        academic_structure = [
            {'CODRAMO': item['CODRAMO'], 'NIVEL': item['NIVEL'],
             'atributos': item['atributos_curso_comparacion']}
            for item in plan_structures
        ]
        with_relations = [
            {**base,
             'equivalencias': [{key: relation[key] for key in ('literal', 'descripciones_origen')}
                              for relation in item['equivalencias_detalle']],
             'requisitos': [{key: relation[key] for key in
                            ('literal', 'descripciones_origen', 'atributos_requisito_origen')}
                           for relation in item['requisitos_detalle']]}
            for base, item in zip(academic_structure, plan_structures)
        ]
        fingerprints[plan] = {
            'claves': keys, 'atributos': _packed(academic_structure),
            'con_relaciones': _packed(with_relations),
        }
        item = {
            'CODPESTUD': plan,
            'carreras_internas': attrs['Codcarr'], 'sedes': attrs['Sede'],
            'nombres_carrera': attrs['Nombre_L'], 'nombres_plan': attrs['NOMPESTUD'],
            'atributos_origen': {field: _unique_raw(row.get(field) for row in group)
                                 for field in ('CODPESTUD', *PLAN_FIELDS)},
            'estado_contexto': 'UNICO' if context_unique and plan else 'INCOMPLETO_O_MULTIPLE',
            'filas_fuente': [row['_fila'] for row in group], 'filas_expandidas': len(group),
            'ramos_niveles': len(keys),
            'ramos_distintos': len({ramo for ramo, _ in keys}),
            'niveles_observados': sorted({level for _, level in keys}),
            'grupos_con_conflicto_atributo_curso': sum(bool(x['conflictos_atributos_curso']) for x in plan_structures),
            'sha256_conjunto_ramo_nivel': hashlib.sha256(_packed(sorted(keys)).encode()).hexdigest(),
            'sha256_atributos_curso': hashlib.sha256(_packed(academic_structure).encode()).hexdigest(),
            'sha256_estructura_con_relaciones': hashlib.sha256(_packed(with_relations).encode()).hexdigest(),
            'fecha_vigencia_acreditada': None,
            'version_sies_asignada': None,
        }
        catalog.append(item)
        if item['estado_contexto'] == 'UNICO':
            family_plans[(attrs['Codcarr'][0], attrs['Sede'][0])].append(plan)

    comparisons = []
    for (career, campus), plans in sorted(family_plans.items()):
        for first, second in combinations(sorted(plans), 2):
            left, right = fingerprints[first], fingerprints[second]
            a, b = left['claves'], right['claves']
            comparisons.append({
                'carrera_interna': career, 'sede': campus, 'plan_a': first, 'plan_b': second,
                'mismos_ramos_niveles': a == b,
                'mismos_atributos_curso': left['atributos'] == right['atributos'],
                'misma_estructura_con_relaciones': left['con_relaciones'] == right['con_relaciones'],
                'ramos_niveles_comunes': len(a & b), 'solo_plan_a': len(a - b), 'solo_plan_b': len(b - a),
                'sucesion_temporal_acreditada': False,
            })

    eq_status = Counter(rel['estado_destino'] for item in structures for rel in item['equivalencias_detalle'])
    req_status = Counter(rel['estado_destino'] for item in structures for rel in item['requisitos_detalle'])
    summary = {
        'filas_catalogo': len(rows), 'planes': len(catalog),
        'carreras_internas': len({literal_key(row.get('Codcarr')) for row in rows}),
        'pares_carrera_sede': len({(literal_key(row.get('Codcarr')), literal_key(row.get('Sede'))) for row in rows}),
        'sedes': sorted({literal_key(row.get('Sede')) for row in rows}),
        'asignaturas_plan_ramo_nivel': len(structures),
        'grupos_expandidos': sum(item['filas_expandidas'] > 1 for item in structures),
        'exceso_filas_sobre_grano': len(rows) - len(structures),
        'roles_filas': dict(sorted(roles.items())),
        'filas_conciliadas': sum(item['filas_expandidas'] for item in structures) == len(rows),
        'grupos_con_base_distinta_de_una': sum(len(item['filas_base']) != 1 for item in structures),
        'grupos_con_clave_incompleta': sum(item['estado_clave'] != 'COMPLETA' for item in structures),
        'grupos_con_conflicto_atributo_curso': sum(bool(item['conflictos_atributos_curso']) for item in structures),
        'planes_con_contexto_incompleto_o_multiple': sum(item['estado_contexto'] != 'UNICO' for item in catalog),
        'equivalencias_estado_destino': dict(sorted(eq_status.items())),
        'requisitos_estado_destino': dict(sorted(req_status.items())),
        'pares_comparados_misma_carrera_sede': len(comparisons),
        'pares_mismos_ramos_niveles': sum(item['mismos_ramos_niveles'] for item in comparisons),
        'pares_mismos_atributos_curso': sum(item['mismos_atributos_curso'] for item in comparisons),
        'pares_misma_estructura_con_relaciones': sum(item['misma_estructura_con_relaciones'] for item in comparisons),
    }
    return {'catalogo_planes': catalog, 'estructura_asignaturas': structures,
            'comparaciones_planes': comparisons, 'resumen': summary}
