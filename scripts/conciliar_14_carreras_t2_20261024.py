"""Explica diferencias T2 mediante trayectorias CODCLI; exporta solo agregados.

No asigna renuncias, no cambia tasas y no escribe identificadores individuales.
"""
import csv
import importlib.util
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
PRIOR = ROOT / 'outputs/renuncias_t2_2026_personas_20261023/EVIDENCIA_AGREGADA.json'
OUT = ROOT / 'outputs/conciliacion_14_carreras_t2_20261024'
spec = importlib.util.spec_from_file_location('prev', ROOT / 'scripts/revisar_renuncias_t2_2026_personas_20261023.py')
prev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prev)
n = prev.norm


def counts(items):
    return dict(Counter(items))


def pair(row):
    return (n(row['ESTADOACADEMICO']), n(row['SITUACION'])) if row else ('NO_LOCALIZADO_POR_CODCLI', '')


def serial_transitions(counter):
    return [{'estados': list(k), 'matriculas': v} for k, v in sorted(counter.items())]


def main():
    if OUT.exists():
        raise SystemExit('Salida existente: no sobrescribir.')
    evidence = json.loads(PRIOR.read_text())
    sources = {key: Path(v['ruta']) for key, v in evidence['fuentes'].items()}
    for key, path in sources.items():
        assert prev.digest(path) == evidence['fuentes'][key]['sha256'], key
    git_before = {'rama': prev.git('branch', '--show-current'), 'head': prev.git('rev-parse', 'HEAD')}
    protected = {ROOT / x: prev.digest(ROOT / x) for x in ['agent.md', 'PROYECTO_IPSS.json', 'docs/README.md']}
    original = prev.rows(sources['T2'])
    assert len(original) == 528 and len({n(r['RUT']) for r in original}) == 527
    assert len({n(r['CODCLI']) for r in original}) == 528
    source_keys = ['DA10246', 'DA11998', 'DA12159']
    indices, rut_indices = {}, {}
    for key in source_keys:
        indices[key], rut_indices[key] = defaultdict(list), defaultdict(list)
        for row in prev.rows(sources[key]):
            indices[key][n(row['CODCLI'])].append(row)
            rut_indices[key][n(row['RUT'])].append(row)
    prior_careers = evidence['contrastes']['DA12159']['por_carrera']
    focus = {r['carrera'] for r in prior_careers if r['diferencia_complemento_vs_renuncias'] != 0}
    assert len(focus) == 14
    records = []
    match_control = {key: Counter() for key in source_keys}
    alternatives = []
    comparison_columns = ['RUT', 'CODCARPR', 'ANOMATRICULA', 'PERIODOMATRICULA']
    for row in original:
        snapshots = []
        for key in source_keys:
            found = indices[key][n(row['CODCLI'])]
            match_control[key][str(len(found))] += 1
            assert len(found) <= 1
            target = found[0] if found else None
            if target:
                assert all(n(row[c]) == n(target[c]) for c in comparison_columns)
            else:
                candidates = rut_indices[key][n(row['RUT'])]
                for other in candidates:
                    alternatives.append({'fuente': key, 'carrera_origen': n(row['CODCARPR']),
                        'carrera_otro_codcli': n(other['CODCARPR']),
                        'periodo_origen': n(row['PERIODOMATRICULA']),
                        'periodo_otro_codcli': n(other['PERIODOMATRICULA']),
                        'anio_otro_codcli': n(other['ANOMATRICULA']),
                        'jornada_concordante': n(row['JORNADA']) == n(other['JORNADA']),
                        'fecha_matricula_concordante': n(row['FECHAMATRICULA']) == n(other['FECHAMATRICULA']),
                        'estado_otro_codcli': pair(other)[0], 'situacion_otro_codcli': pair(other)[1],
                        'fecha_firma_disponible': bool(other.get('FECHAFIRMA')),
                        'clase': 'B; E atribución al expediente original no demostrada'})
            snapshots.append(target)
        records.append({'carrera': row['NOMBRE_L'], 'codigo_carrera': n(row['CODCARPR']),
            'pairs': [pair(s) for s in snapshots], 'snapshots': snapshots})

    transitions = Counter(tuple(p[0] for p in r['pairs']) for r in records)
    rows_summary = []
    for prior in prior_careers:
        career = prior['carrera']
        group = [r for r in records if r['carrera'] == career]
        final = Counter(r['pairs'][2][0] for r in group)
        final_situ = Counter(r['pairs'][2][1] for r in group)
        v_to_e = Counter(r['pairs'][1][1] for r in group
                         if r['pairs'][0][0] == 'VIGENTE' and r['pairs'][1][0] == 'ELIMINADO')
        complement = len(group) - final['VIGENTE']
        assert complement == prior['complemento_vigente_incluye_no_localizados']
        row = {'clasificacion': 'B/C', 'carrera': career,
            'codigos_carrera': ', '.join(sorted({r['codigo_carrera'] for r in group})),
            'matriculas_originales': len(group), 'renuncias_resumen': prior['renuncias_calculo'],
            'renuncias_celda_vacia': prior['renuncias_celda'] is None,
            'no_vigentes_o_no_localizados_10246': sum(r['pairs'][0][0] != 'VIGENTE' for r in group),
            'no_vigentes_o_no_localizados_11998': sum(r['pairs'][1][0] != 'VIGENTE' for r in group),
            'eliminados_12159': final['ELIMINADO'], 'suspendidos_12159': final['SUSPENDIDO'],
            'codcli_no_localizados_12159': final['NO_LOCALIZADO_POR_CODCLI'],
            'vigentes_12159': final['VIGENTE'], 'complemento_12159': complement,
            'diferencia_vs_resumen': complement - prior['renuncias_calculo'],
            'pasan_vigente_eliminado': sum(v_to_e.values()),
            'nueva_situacion11': sum(v for k, v in v_to_e.items() if k.startswith('11 -')),
            'nueva_situacion23': sum(v for k, v in v_to_e.items() if k.startswith('23 -')),
            'nueva_situacion24': sum(v for k, v in v_to_e.items() if k.startswith('24 -')),
            'pasan_vigente_ausente': sum(r['pairs'][0][0] == 'VIGENTE' and r['pairs'][1][0] == 'NO_LOCALIZADO_POR_CODCLI' for r in group),
            'pasan_vigente_suspendido': sum(r['pairs'][1][0] == 'VIGENTE' and r['pairs'][2][0] == 'SUSPENDIDO' for r in group),
            'vigentes_situacion38_12159': sum(r['pairs'][2] == ('VIGENTE', '38 - REINCORPORACION DE ACTIVIDADES') for r in group),
            'es_carrera_discordante': career in focus}
        assert row['pasan_vigente_eliminado'] == row['nueva_situacion11'] + row['nueva_situacion23'] + row['nueva_situacion24']
        row['situaciones_finales'] = dict(final_situ)
        row['transiciones'] = serial_transitions(Counter(tuple(p[0] for p in r['pairs']) for r in group))
        rows_summary.append(row)
    focus_rows = [r for r in rows_summary if r['es_carrera_discordante']]
    total_cols = ['matriculas_originales', 'renuncias_resumen', 'eliminados_12159', 'suspendidos_12159',
        'codcli_no_localizados_12159', 'vigentes_12159', 'complemento_12159', 'diferencia_vs_resumen',
        'pasan_vigente_eliminado', 'nueva_situacion11', 'nueva_situacion23', 'nueva_situacion24',
        'pasan_vigente_ausente', 'pasan_vigente_suspendido']
    totals = {scope: {c: sum(r[c] for r in data) for c in total_cols}
              for scope, data in [('19_carreras', rows_summary), ('14_carreras', focus_rows)]}
    assert totals['19_carreras']['renuncias_resumen'] == totals['19_carreras']['complemento_12159'] == 66
    assert totals['19_carreras']['pasan_vigente_eliminado'] == 56
    assert totals['14_carreras']['pasan_vigente_eliminado'] == 47
    assert sum(r['diferencia_vs_resumen'] for r in focus_rows if r['diferencia_vs_resumen'] > 0) == 13
    assert sum(r['diferencia_vs_resumen'] for r in focus_rows if r['diferencia_vs_resumen'] < 0) == -13
    assert len([r for r in focus_rows if r['diferencia_vs_resumen'] > 0]) == 6
    result = {'fecha': datetime.now(ZoneInfo('America/Santiago')).isoformat(),
        'proceso': 'Seguimiento interno IPSS162, ingresos 2026/P2',
        'universo_inmutable': {'matriculas': 528, 'personas': 527, 'renuncias_agregadas': 66},
        'clasificacion': 'B datos; C cruces/cálculos; E atribución a nómina original',
        'cruce': {'metodo': 'CODCLI exacto; concordancia RUT+CODCARPR+ANOMATRICULA+PERIODOMATRICULA',
                  'cardinalidad': {k: dict(v) for k, v in match_control.items()},
                  'discordancias_identidad_contexto': 0},
        'transiciones_528': serial_transitions(transitions), 'totales': totals,
        'carreras': rows_summary, 'alternativas_sin_atribucion': alternatives,
        'limites': ['Los cambios son observados entre respaldos, no fechas efectivas acreditadas.',
                   'Otro CODCLI del mismo RUT no reemplaza ni determina el estado del expediente original.',
                   'No existe lista identificable del agregado66 en las fuentes revisadas.',
                   '26 es suma de diferencias absolutas de conteos por carrera, no personas identificadas.'],
        'fuentes': evidence['fuentes']}
    for k, p in sources.items():
        assert prev.digest(p) == evidence['fuentes'][k]['sha256']
    assert all(prev.digest(p) == h for p, h in protected.items())
    assert prev.git('rev-parse', 'HEAD') == git_before['head']
    OUT.mkdir(parents=True)
    (OUT/'EVIDENCIA_AGREGADA.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    fields = [k for k in rows_summary[0] if k not in ['situaciones_finales', 'transiciones']]
    with (OUT/'COMPARACION_19_CARRERAS.csv').open('w', newline='', encoding='utf-8-sig') as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter=';', extrasaction='ignore')
        writer.writeheader(); writer.writerows(rows_summary)
    qa = {'controles': {'fuentes_hash_antes_despues': 'OK', 'reproduce_14_de_19': 'OK',
        'universo_528_matriculas_527_personas': 'OK', 'cruce_unico_sin_discordancias': 'OK',
        'conciliacion_transiciones_528': 'OK', 'suma_carreras_y_compensacion_13_menos_13': 'OK',
        'V16_y_originales_intactos': 'OK', 'cambios_previos_conservados': 'OK'},
        'tasa_por_personas_cierre_T2': 'PENDIENTE; no se adjudica nómina66',
        'datos_individuales_exportados': False, 'git_antes_despues': git_before, 'commit_push': False}
    (OUT/'QA.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'salida': str(OUT), 'totales': totals, 'transiciones': result['transiciones_528'],
                      'filas_resumen14': focus_rows}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
