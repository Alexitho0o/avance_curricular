"""Evaluación B de evidencias; no promueve candidatos a equivalencias H5."""
from collections import defaultdict
import json

CLAVE = ('codcarpr', 'plan_umas', 'sede_umas', 'jornada_umas', 'nombre_interno')
UNIDADES_SIES = {'1': 'SEMESTRAL', '2': 'TRIMESTRAL', '3': 'ANUAL', '4': 'BIMESTRAL'}
CAMPOS_MRUN = {
    'Nombre Carrera': 'nomb_carrera', 'Jornada': 'jornada', 'Modalidad': 'modalidad',
    'Tipo Carrera': 'tipo_plan_carr', 'Duración Estudios': 'dur_estudio_carr',
    'Duración Total': 'dur_total_carr',
}


def clave_contexto(row):
    return json.dumps([row.get(k) for k in CLAVE], ensure_ascii=False, separators=(',', ':'))


def comparar_literal(left, right):
    missing = (None, '', 'NULL')
    if left in missing or right in missing:
        return 'DESCONOCIDO'
    return 'IGUAL' if left == right else 'DIFERENTE'


def conciliar_oferta_mrun(ofertas, matriculas):
    """Conserva la unión de claves; no suma matrículas ni imputa perfiles ausentes."""
    offer_index = {}
    mrun_index = defaultdict(list)
    for row in ofertas:
        key = (row['anio'], row['codigo_unico'])
        if key in offer_index:
            raise ValueError('Oferta repetida por año/código')
        offer_index[key] = row
    for number, row in enumerate(matriculas, 1):
        mrun_index[(int(row['cat_periodo']), row['codigo_unico'])].append((number, row))
    result = []
    for year, code in sorted(offer_index.keys() | mrun_index.keys()):
        offer = offer_index.get((year, code))
        records = mrun_index.get((year, code), [])
        fields = {}
        if offer and records:
            for formal, internal in CAMPOS_MRUN.items():
                value = offer['campos_originales'][formal]
                comparisons = [{'fila_mrun_h5': n, 'valor_mrun': row[internal],
                                'estado': comparar_literal(value, row[internal])}
                               for n, row in records]
                states = {r['estado'] for r in comparisons}
                state = ('DIFERENTE' if 'DIFERENTE' in states else
                         'DESCONOCIDO' if 'DESCONOCIDO' in states else 'IGUAL')
                fields[formal] = {'valor_oferta': value, 'estado': state, 'comparaciones': comparisons}
        result.append({'anio': year, 'codigo_unico': code,
                       'presencia': 'AMBAS' if offer and records else 'SOLO_OFERTA' if offer else 'SOLO_MRUN',
                       'registro_csv_oferta': offer['registro_csv'] if offer else None,
                       'filas_mrun_h5': [n for n, _ in records], 'campos': fields,
                       'diferencias': [k for k, v in fields.items() if v['estado'] == 'DIFERENTE']})
    return result


def evaluar_candidato(candidate, plan, observaciones, oferta, inicio, mapas):
    """Describe condiciones observadas, sin inferir atributos UMAS no documentados."""
    if candidate['ambito_candidato'] != 2026:
        raise ValueError('El mapa de candidatos solo acredita lectura 2026')
    if oferta and (oferta['anio'] != 2026 or oferta['codigo_unico'] != candidate['codigo_unico']):
        raise ValueError('Perfil SIES de otro código o año')
    rows = [r for r in observaciones if r['PLAN_DE_ESTUDIO'] == candidate['plan_umas']
            and r['CODCARR'] == candidate['codcarpr'] and r['JORNADA'] == candidate['jornada_umas']]
    annual = [r for r in rows if r['ANO'] == '2026']
    years = sorted({int(r['ANO']) for r in rows if r['ANO'].isdigit() and 2007 <= int(r['ANO']) <= 2026})
    regimes = sorted({r['REGIMEN'] for r in annual if r['REGIMEN'] not in ('', 'NULL')})
    formal = oferta['campos_originales'] if oferta else {}
    sede = mapas['sedes'].get(candidate['sede_umas'])
    jornada = mapas['jornadas'].get(candidate['jornada_umas'])
    names = plan['nombres_carrera'] if plan else []
    name_state = ('SIN_CATALOGO_PLAN' if not plan else 'IGUAL_LITERAL'
                  if candidate['nombre_interno'] in names else 'DIFERENTE_SIN_ALIAS')
    levels = plan['niveles_observados'] if plan else []
    regime_sies = UNIDADES_SIES.get(formal.get('Régimen'))
    regime_state = ('DESCONOCIDO' if not regime_sies or not regimes else
                    'MULTIPLES_REGIMENES_OBSERVADOS' if len(regimes) != 1 else
                    comparar_literal(regimes[0], regime_sies))
    gaps = ['B-EQ-01', 'B-TEMP-01', 'B-PERFIL-01', 'B-DUR-01', 'B-MAPAS-01']
    if name_state != 'IGUAL_LITERAL':
        gaps.append('B-NOMBRE-01')
    if not oferta:
        gaps.append('B-OFERTA-01')
    return {
        'id_candidato_h5': candidate['id'], 'clave_umas': clave_contexto(candidate),
        **{k: candidate.get(k) for k in CLAVE}, 'codigo_unico': candidate['codigo_unico'],
        'ambito_candidato': 2026, 'estado': 'CANDIDATA_PENDIENTE_EVIDENCIA',
        'habilitada_para_resolver': False,
        'identidad_2026': {
            'sede': comparar_literal(sede, candidate['componentes_sies']['sede']),
            'jornada': comparar_literal(jornada, candidate['componentes_sies']['jornada']),
            'nombre_interno_catalogo': name_state, 'nombres_catalogo': names,
            'mapa_historico_acreditado': False,
        },
        'perfil_sies_2026': {k: formal.get(k) for k in (
            'Nombre Carrera', 'Modalidad', 'Tipo Carrera', 'Nivel Carrera',
            'Régimen', 'Duración formal del Régimen', 'Duración Estudios', 'Duración Total')},
        'perfil_umas': {'niveles_observados': levels, 'regimenes_observados_2026': regimes,
                        'tipo_plan': None, 'modalidad_programa': None, 'nivel_programa': None,
                        'sede_observacion_notas': 'NO_CONTENIDA_EN_FUENTE',
                        'filas_observaciones_h4': [r['fila_tsv'] for r in rows]},
        'comparacion_perfil': {'regimen_2026': regime_state,
                               'duracion': 'NO_COMPARABLE_SIN_DEFINICION_NIVEL_Y_CONVERSION',
                               'tipo_plan': 'DESCONOCIDO', 'modalidad': 'DESCONOCIDO',
                               'nivel_programa': 'DESCONOCIDO'},
        'cronologia': {'inicio_oferta_codigo': inicio['anio_inicio_diccionario'],
                      'anios_actividad_observada': years,
                      'actividad_anterior_a_primera_oferta': bool(years and inicio['anio_inicio_diccionario']
                                                               and years[0] < inicio['anio_inicio_diccionario']),
                      'vigencia_equivalencia': None, 'asignacion_individual_acreditada': False},
        'fuentes': {'candidato': candidate['id'], 'catalogo_plan': candidate['plan_umas'],
                    'registro_csv_2026': oferta['registro_csv'] if oferta else None,
                    'equivalencias_programa': candidate['equivalencias_ids']},
        'brechas': gaps,
    }
