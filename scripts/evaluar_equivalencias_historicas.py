#!/usr/bin/env python3
"""Reproduce fase B desde fuentes gobernadas, sin promover reglas ni tocar Excel."""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.equivalencias_historicas import validar_maestro
from common.evaluacion_equivalencias import conciliar_oferta_mrun, evaluar_candidato
from common.reglas_negocio import inicio_codigo_oferta

HIST = ROOT / 'data/versiones_historicas_sies_umas'
OUT = HIST / 'fase_b_20261015'
MASTER_SHA = '2ef459251e91ecebe5370402e3d2ea25341aeecbfb3ca54eca210cc347c392a5'
CSV_SHA = 'f3e2222dbdc710226fe86f71f543916781af5744117e52b03ddf8551552fcded'
ATTRIBUTES = ('Nombre Carrera', 'Modalidad', 'Tipo Carrera', 'Nivel Carrera',
              'Duración Estudios', 'Duración Total', 'Régimen', 'Duración formal del Régimen')
BRECHAS = {
    'B-EQ-01': 'Tabla o resolución que vincule explícitamente CODCARPR + CODPESTUD + sede + jornada con Código Único. Un alias de programa sin plan no basta.',
    'B-TEMP-01': 'Años/períodos efectivos de la equivalencia plan–SIES. Para asignación individual, además historial de plan por matrícula o linaje SQL que acredite su temporalidad.',
    'B-PERFIL-01': 'Catálogo UMAS con tipo de plan, modalidad del programa y nivel, junto con definiciones. No inferirlos del nombre, prefijo o MODALIDAD escolar.',
    'B-DUR-01': 'Definición de NIVEL y duración del plan UMAS; regla por proceso/edición para convertir a duración formal, incluyendo precisión y redondeo.',
    'B-MAPAS-01': 'Vigencia histórica de correspondencias de sede y jornada; los mapas H5 están limitados a candidatos 2026.',
    'B-NOMBRE-01': 'Alias documentado entre nombre del candidato y nombre interno del plan. Conservar ambos literales mientras se revisa.',
    'B-OFERTA-01': 'Oferta del código y año faltantes, o evidencia de la relación aplicable sin oferta observada. No completar por otro año.',
    'B-SIN-CANDIDATO': 'Relación de programa/plan no cubierta por candidatos H5; requiere evidencia explícita y no coincidencia nominal automática.',
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(obj):
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()


def build():
    inputs = {}

    def read(relative, expected=None):
        path = ROOT / relative
        raw = path.read_bytes()
        actual = digest(raw)
        if expected is not None and actual != expected:
            raise ValueError('Fuente alterada: ' + relative)
        inputs[relative] = {'sha256': actual, 'bytes': len(raw)}
        return raw

    master = validar_maestro(json.loads(read('data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json', MASTER_SHA)))
    sources = master['fuentes']
    base4 = 'data/versiones_historicas_sies_umas/fase_4_20261015/'
    plans = json.loads(read(base4 + 'catalogo_planes.json', sources['catalogo_planes']['sha256']))
    observations = list(csv.DictReader(io.StringIO(read(base4 + 'observaciones_plan_periodo.tsv',
                                                        sources['observaciones_planes']['sha256']).decode()), delimiter='\t'))
    for n, row in enumerate(observations, 2):
        row['fila_tsv'] = n
    temporal = json.loads(read(base4 + 'evidencia_temporal.json', sources['evidencia_temporal']['sha256']))
    raw = gzip.decompress(read('data/reglas_negocio/20261015/fuentes/Oferta_Academica_2010_al_2026_SIES_12_01_2026_WEB_E.csv.gz'))
    if digest(raw) != CSV_SHA:
        raise ValueError('Oferta nacional original alterada')
    reader = csv.DictReader(io.StringIO(raw.decode('latin1'), newline=''), delimiter=';')
    offers = []
    national = 0
    national_keys = set()
    for n, row in enumerate(reader, 2):
        national += 1
        if len(row) != 69 or None in row or any(x is None for x in row.values()):
            raise ValueError('Fila nacional incompleta')
        key = (row['Año'], row['Código Único'])
        if key in national_keys:
            raise ValueError('Clave nacional repetida')
        national_keys.add(key)
        if row['Código IES'] == '162':
            offers.append({'anio': int(row['Año'][4:]), 'codigo_unico': row['Código Único'],
                           'registro_csv': n, 'campos_originales': row})
    if national != 395719 or len(offers) != 747:
        raise ValueError('Universo de oferta distinto')
    offers.sort(key=lambda x: (x['codigo_unico'], x['anio']))
    offer_index = {(r['anio'], r['codigo_unico']): r for r in offers}
    if set(offer_index) != {(r['anio'], r['codigo_unico']) for r in master['oferta_anual']}:
        raise ValueError('Universo institucional difiere de H5')
    starts = {r['codigo_unico']: inicio_codigo_oferta(offers, r['codigo_unico']) for r in master['universo_sies']}
    plan_index = {r['CODPESTUD']: r for r in plans}
    if len(plan_index) != len(plans):
        raise ValueError('Plan duplicado en catálogo')
    evaluated = [evaluar_candidato(c, plan_index.get(c['plan_umas']), observations,
                                   offer_index.get((2026, c['codigo_unico'])), starts[c['codigo_unico']],
                                   master['mapas_lectura_candidato_2026']) for c in master['candidatos_plan_sies']]
    evaluated.sort(key=lambda r: r['id_candidato_h5'])
    by_code, by_plan, by_context = defaultdict(list), defaultdict(list), defaultdict(list)
    for row in evaluated:
        by_code[row['codigo_unico']].append(row)
        by_plan[row['plan_umas']].append(row)
        by_context[row['clave_umas']].append(row)
    coverage_sies = []
    for row in sorted(master['universo_sies'], key=lambda r: r['codigo_unico']):
        code = row['codigo_unico']
        candidates = by_code[code]
        coverage_sies.append({'codigo_unico': code, 'inicio': starts[code],
                              'nombre_literal_oferta_2026': row['nombre_literal_oferta_2026'],
                              'anios_mrun': row['anios_mrun'],
                              'candidatos_h5': [r['id_candidato_h5'] for r in candidates],
                              'planes_candidatos': sorted({r['plan_umas'] for r in candidates}),
                              'estado': 'CANDIDATOS_PENDIENTES' if candidates else 'SIN_CANDIDATOS',
                              'brechas': sorted({b for r in candidates for b in r['brechas']}) if candidates else ['B-SIN-CANDIDATO'],
                              'equivalencias_acreditadas': []})
    coverage_plans = []
    for row in sorted(master['planes_umas'], key=lambda r: r['CODPESTUD']):
        plan = row['CODPESTUD']
        candidates = by_plan[plan]
        coverage_plans.append({'plan_umas': plan, 'presencia': row['presencia'],
                               'candidatos_h5': [r['id_candidato_h5'] for r in candidates],
                               'codigos_candidatos': sorted({r['codigo_unico'] for r in candidates}),
                               'estado': 'CANDIDATOS_PENDIENTES' if candidates else 'SIN_CANDIDATOS',
                               'brechas': sorted({b for r in candidates for b in r['brechas']}) if candidates else ['B-SIN-CANDIDATO'],
                               'equivalencias_acreditadas': []})
    reconciliation = conciliar_oferta_mrun(offers, master['mrun_anual'])
    histories = defaultdict(list)
    for row in offers:
        histories[row['codigo_unico']].append(row)
    changes = []
    for code, history in sorted(histories.items()):
        for previous, current in zip(history, history[1:]):
            changed = {k: [previous['campos_originales'][k], current['campos_originales'][k]]
                       for k in ATTRIBUTES if previous['campos_originales'][k] != current['campos_originales'][k]}
            if changed:
                changes.append({'codigo_unico': code, 'anios_observados': [previous['anio'], current['anio']],
                                'registros_csv': [previous['registro_csv'], current['registro_csv']],
                                'cambios': changed, 'causa': 'NO_ACREDITADA'})
    contexts = [{'clave_umas': key, 'codigos_candidatos': sorted({r['codigo_unico'] for r in rows}),
                 'candidatos_h5': [r['id_candidato_h5'] for r in rows],
                 'estado': 'UNICO_NO_ACREDITADO' if len({r['codigo_unico'] for r in rows}) == 1 else 'MULTIPLES_NO_ACREDITADOS',
                 'codigo_asignado': None} for key, rows in sorted(by_context.items())]
    summary = {'estado': 'EVALUACION_REPRODUCIBLE_CON_BRECHAS', 'candidatos_evaluados': len(evaluated),
               'codigos_sies': len(coverage_sies), 'planes_umas': len(coverage_plans),
               'sies_sin_candidatos': sum(not r['candidatos_h5'] for r in coverage_sies),
               'planes_sin_candidatos': sum(not r['candidatos_h5'] for r in coverage_plans),
               'contextos': dict(Counter(r['estado'] for r in contexts)),
               'nombre_interno_vs_catalogo': dict(Counter(r['identidad_2026']['nombre_interno_catalogo'] for r in evaluated)),
               'regimen_2026': dict(Counter(r['comparacion_perfil']['regimen_2026'] for r in evaluated)),
               'actividad_anterior_a_oferta': sum(r['cronologia']['actividad_anterior_a_primera_oferta'] for r in evaluated),
               'presencia_oferta_mrun': dict(Counter(r['presencia'] for r in reconciliation)),
               'claves_oferta_mrun_con_diferencias': sum(bool(r['diferencias']) for r in reconciliation),
               'diferencias_por_campo': dict(Counter(k for r in reconciliation for k in r['diferencias'])),
               'transiciones_observadas_con_cambios': len(changes),
               'reglas_efectivas_nuevas': 0, 'asignacion_automatica_habilitada': False,
               'filas_csv_nacional': national, 'filas_oferta_ipss': len(offers)}
    if (summary['codigos_sies'], summary['planes_umas'], summary['candidatos_evaluados']) != (141, 236, 513):
        raise ValueError('Universo H5 no conciliado')
    outputs = {
        'perfiles_sies_anuales.json': offers, 'evaluacion_candidatos.json': evaluated,
        'conciliacion_oferta_mrun.json': reconciliation, 'cambios_atributos_codigo.json': changes,
        'cobertura_sies.json': coverage_sies, 'cobertura_umas.json': coverage_plans,
        'contextos_busqueda.json': contexts,
        'brechas.json': {'definiciones': BRECHAS, 'fuentes_temporales_por_localizar': temporal['candidate_sources'],
                         'alcance_busqueda': 'Fuentes gobernadas H4/H5 y documentación local consultada; no se acredita acceso a SQL UMAS.',
                         'equivalencia_programa_no_es_asignacion_individual': True},
        'resumen.json': summary,
    }
    for relative in ('common/evaluacion_equivalencias.py', 'common/reglas_negocio.py',
                     'common/equivalencias_historicas.py', 'scripts/evaluar_equivalencias_historicas.py',
                     'docs/fase_b_evaluacion_equivalencias_historicas.md'):
        read(relative)
    # Comparar de nuevo las huellas al cierre; no congelar una lectura concurrente distinta.
    for relative, meta in inputs.items():
        if digest((ROOT / relative).read_bytes()) != meta['sha256']:
            raise ValueError('Fuente cambió durante evaluación: ' + relative)
    outputs['manifest.json'] = {'fase': 'B', 'fecha': '2026-10-15', 'entradas': inputs,
                                'oferta_original_sha256': CSV_SHA,
                                'salidas': {name: digest(encode(value)) for name, value in outputs.items()},
                                'modifica_h5': False, 'modifica_excel': False,
                                'contiene_identificadores_personales': False}
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verificar', action='store_true', help='Reproduce y compara sin escribir')
    args = parser.parse_args()
    outputs = build()
    for name, value in outputs.items():
        path = OUT / name
        content = encode(value)
        if path.exists() and path.read_bytes() != content:
            raise ValueError('Salida existente distinta: ' + name)
        if args.verificar and not path.exists():
            raise ValueError('Falta salida para verificar: ' + name)
    if not args.verificar:
        OUT.mkdir(parents=True, exist_ok=True)
        for name, value in outputs.items():
            (OUT / name).write_bytes(encode(value))
    print(json.dumps({'verificacion_sin_escritura': args.verificar, **outputs['resumen.json']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
