#!/usr/bin/env python3
"""QA independiente de serialización, fuentes, reproducción y no interferencia."""
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/paridad_codigo_sies_20261029'
DATA = ROOT / 'data/paridad_codigo_sies/20261029'
MILE = ROOT / 'manifests/milestones/H002-PARIDAD-CODIGO-SIES-2027'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, v):
    p.write_text(json.dumps(v, ensure_ascii=False, sort_keys=True, indent=2) + '\n')


def main():
    baseline = json.loads((OUT / 'ESTADO_INICIAL.json').read_text())
    manifest = json.loads((DATA / 'MANIFEST.json').read_text())
    table = json.loads((DATA / 'TABLA_PARIDAD_2026_2027.json').read_text())
    rows = table['filas']
    records = list(csv.DictReader((DATA / 'TABLA_PARIDAD_2026_2027.csv').open(), delimiter=';'))
    inputs = {x['id']: x for x in manifest['entradas']}
    source_rows = list(csv.reader(io.StringIO((ROOT / inputs['carga_v06']['ruta']).read_text()), delimiter=';'))
    raw_by = {'I162S' + x[0] + 'C' + x[2] + 'J' + x[5] + 'V' + x[6]: x for x in source_rows}
    groups = json.loads((ROOT / inputs['grupos']['ruta']).read_text())
    old = {c for g in groups for c in g['codigos_base']}
    keys = {(x['anio'], x['codigo_unico']) for x in rows}
    controls = {}
    controls['conteos_independientes_106_161'] = Counter(x['anio'] for x in rows) == Counter({2026: 106, 2027: 161})
    controls['267_llaves_unicas'] = len(rows) == len(keys) == len(records) == 267
    controls['universos_originales_completos'] = (
        {x['codigo_unico'] for x in rows if x['anio'] == 2026} == old and
        {x['codigo_unico'] for x in rows if x['anio'] == 2027} == set(raw_by))
    controls['CSV_JSON_mismas_llaves'] = {(int(x['anio']), x['codigo_unico']) for x in records} == keys
    controls['estados_sumados_por_via_independiente'] = all(
        dict(sorted(Counter(x['estado'] for x in rows if x['anio'] == y).items())) ==
        {k: v for k, v in table['conteos_por_anio_estado'][str(y)].items() if v} for y in [2026, 2027])
    controls['atributos_2027_literales_en_48_columnas'] = all(
        x['nombre_carrera'] == raw_by[x['codigo_unico']][3] and
        x['modalidad_codigo'] == raw_by[x['codigo_unico']][4] and
        x['tipo_plan_codigo'] == raw_by[x['codigo_unico']][7] and
        x['duracion_total_semestres'] == raw_by[x['codigo_unico']][11] and
        x['nivel_global_codigo'] == raw_by[x['codigo_unico']][15] and
        x['vigencia_2027'] == raw_by[x['codigo_unico']][47]
        for x in rows if x['anio'] == 2027)
    buckets = defaultdict(list)
    for code, x in raw_by.items():
        if x[47] == '1' and x[15] == '1':
            buckets[(x[0], x[2], x[5], x[4], x[7], x[11])].append(code)
    controls['si_nuevos_version_unica_en_su_perfil_o_E'] = all(
        (x['version_para_nuevos_2027'] == 'E') or
        (x['version_para_nuevos_2027'] == 'sí' and len(buckets[(x['cod_sede'], x['cod_carrera'], x['cod_jornada'],
              x['modalidad_codigo'], x['tipo_plan_codigo'], x['duracion_total_semestres'])]) == 1)
        for x in rows if x['anio'] == 2027 and x['vigencia_2027'] == '1' and x['estado'] != 'FUERA_ALCANCE')
    controls['ninguna_propuesta_promovida'] = all(x['version_para_nuevos_2027'] != 'sí'
        for x in rows if x['estado'] in ('NUEVO_2027_CON_PLAN', 'NUEVO_2027_SIN_PLAN_E'))
    controls['V06_clase_C_confirmacion_usuario_D_no_B'] = table['fuente_2027']['clase'] == 'C'
    controls['hashes_entradas_y_salidas'] = all(sha(ROOT / x['ruta']) == x['sha256'] for x in manifest['entradas']) and all(
        sha(ROOT / p) == h for p, h in manifest['salidas'].items())
    controls['hashes_componentes_auxiliares_H002b'] = all(sha(ROOT / p) == h for p, h in manifest.get('auxiliares_H002b', {}).items())
    milestone = json.loads((MILE / 'REGISTRO.json').read_text())
    controls['registro_hito_apunta_manifest_actual'] = milestone['manifest_sha256'] == sha(DATA / 'MANIFEST.json')

    # Comprobar todos los bytes existentes antes del hito; solo una línea en el índice es excepción.
    changed = []
    for rel, expected in baseline['rastreados'].items():
        p = ROOT / rel
        if not p.is_file() or sha(p) != expected:
            changed.append(rel)
    initial_paths_ok = all((ROOT / x['ruta']).is_file() and sha(ROOT / x['ruta']) == x['sha256']
                           for x in baseline['archivos_no_seguidos'])
    index = ROOT / 'manifests/master/MILESTONE_INDEX.md'
    previous = baseline['indice_hitos_anterior']['contenido']
    suffix = index.read_text()[len(previous):] if index.read_text().startswith(previous) else ''
    exact_index = (index.read_text().startswith(previous) and len(suffix.splitlines()) == 1 and
                   suffix.startswith('| H002-PARIDAD-CODIGO-SIES-2027 |'))
    current_untracked = set(subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')) - {''}
    prior_untracked = {x['ruta'] for x in baseline['archivos_no_seguidos']}
    allowed = ('data/paridad_codigo_sies/20261029/', 'outputs/paridad_codigo_sies_20261029/',
               'manifests/milestones/H002-PARIDAD-CODIGO-SIES-2027/')
    template = 'data/paridad_codigo_sies/PLANTILLA_PLANES_UMAS_2027.tsv'
    unexpected = sorted(x for x in current_untracked - prior_untracked if not x.startswith(allowed) and x != template)
    staged = subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=ROOT, text=True).splitlines()
    stage_ok = all(x.startswith(allowed) or x in (template, 'manifests/master/MILESTONE_INDEX.md') for x in staged)
    status_now = subprocess.check_output(['git', 'status', '--porcelain=v1'], cwd=ROOT, text=True).splitlines()
    same_status = all(x in status_now for x in baseline['entradas_status'])
    pres = {'clase': 'C', 'entradas_ajenas_iniciales': baseline['cantidad_entradas'],
            'archivos_ajenos_iniciales': len(baseline['archivos_no_seguidos']),
            'archivos_ajenos_intactos': initial_paths_ok, 'rastreados_con_cambio': sorted(changed),
            'indice_una_linea_H002': exact_index, 'archivos_nuevos_fuera_alcance': unexpected,
            'rama': subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip(),
            'HEAD': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'index_sin_cambios_ajenos': stage_ok, '24_rutas_mismo_status': same_status}
    controls['preservacion_total_salvo_linea_indice'] = (initial_paths_ok and exact_index and not unexpected and
        changed == ['manifests/master/MILESTONE_INDEX.md'] and pres['HEAD'] == baseline['HEAD'] and
        pres['rama'] == baseline['rama'] and stage_ok and same_status)
    previous_b = OUT / 'ESTADO_ANTES_H002B.json'
    if previous_b.exists():
        pb = json.loads(previous_b.read_text())
        previous_states = {(x['anio'], x['codigo_unico']): x['estado'] for x in pb['estados']}
        changes = [x for x in rows if x['estado'] != previous_states[(x['anio'], x['codigo_unico'])]]
        controls['H002b_solo_6_cambios_aprobados_D'] = len(changes) == 6 and all(
            x['anio'] == 2027 and x['estado'] == 'APROBADA_D_2027' and x['clase'] == 'D' and
            x['decision']['fuente'] == 'Alexi, 29-10-2026' for x in changes)
        controls['43_sin_plan_intactos'] = sorted(pb['43_sin_plan']) == sorted(x['codigo_unico'] for x in rows if x['estado'] == 'NUEVO_2027_SIN_PLAN_E')
        rev = json.loads((OUT / 'REVISION_CASO_A_CASO_12.json').read_text())
        controls['12_mismo_orden_sin_aplicar'] = [(x['numero'], x['grupo']) for x in rev['casos']] == [
            (x['numero'], x['grupo']) for x in pb['orden_12']] and all(not x['aplicada'] and x['decision_Alexi'] == '____' for x in rev['casos'])
        controls['conteos_fichas_sin_doble_periodo'] = all(sum(x['matriculas'] for x in c['matriculas_por_plan_codigo_FOR']) == c['total_MU_vinculado'] for c in rev['casos'])
        controls['matriculas_MU_fuente_intactas'] = rev['totales_MU_sin_modificar'] == {'2024': 1541, '2025': 2371, '2026': 4105}
        controls['planes_multiples_no_forzados'] = all(x['plan_umas'] is None for r in changes for x in r['plan_por_cohorte'] if x['clase'] == 'E')
        from cruzar_planes_2027 import HEADER
        controls['plantilla_solo_encabezado'] = (ROOT / template).read_text() == '\t'.join(HEADER) + '\n'
    patterns = {'rut_con_dv': r'(?<!\w)(?:\d{1,2}\.\d{3}\.\d{3}|\d{7,8})-[0-9Kk](?!\w)',
                'correo': r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b',
                'codcli_individual': r'(?<!\w)(?:19|20)\d{2}[1-5][A-Z]{2,12}\d{3,}(?!\w)'}
    findings = []
    for folder in (DATA, OUT, MILE):
        for path in folder.rglob('*'):
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            text = path.read_text()
            clean = re.sub(r'\b(?:[a-fA-F0-9]{64}|[a-fA-F0-9]{40})\b', 'HASH', text)
            for name, pat in patterns.items():
                if re.search(pat, clean):
                    findings.append({'ruta': str(path.relative_to(ROOT)), 'patron': name})
    controls['escaneo_identificadores_sin_hallazgos'] = not findings
    # Las dos ejecuciones se comparan por SHA de cada salida. No escribir fuera de H002.
    before = {str(p.relative_to(ROOT)): sha(p) for p in DATA.iterdir() if p.is_file()}
    repeat = subprocess.run([sys.executable, '-B', str(OUT / 'construir_paridad.py'), '--verificar'], cwd=ROOT, capture_output=True, text=True)
    controls['reejecucion_mismos_hashes'] = repeat.returncode == 0 and all(sha(ROOT / p) == h for p, h in before.items())
    tests = [subprocess.run([sys.executable, '-B', str(p)], cwd=ROOT, capture_output=True, text=True) for p in sorted(OUT.glob('test_*.py'))]
    n_tests = sum(int(m[1]) for t in tests for m in re.finditer(r'Ran (\d+) tests?', t.stderr))
    controls['todas_pruebas_H002'] = all(t.returncode == 0 for t in tests) and n_tests == 22
    if previous_b.exists():
        paths = [OUT / 'REVISION_CASO_A_CASO_12.json', OUT / 'REVISION_CASO_A_CASO_12.md']
        digests = [sha(p) for p in paths]
        rr = subprocess.run([sys.executable, '-B', str(OUT / 'revisar_casos.py')], cwd=ROOT, capture_output=True, text=True)
        controls['fichas_reproducibles_por_hash'] = rr.returncode == 0 and digests == [sha(p) for p in paths]
    result = {'estado': 'PASS_CON_PENDIENTES_E' if all(controls.values()) else 'FAIL', 'clase': 'C',
              'controles': controls, 'hallazgos_patrones': findings,
              'reproduccion_exit_code': repeat.returncode, 'pruebas_exit_code': [t.returncode for t in tests],
              'pruebas': n_tests, 'preservacion': pres,
              'hashes_entrega': {str(p.relative_to(ROOT)): sha(p) for folder in (DATA, MILE)
                                for p in sorted(folder.iterdir()) if p.is_file()},
              'advertencias': ['La privacidad se comprueba por campos de catálogo y patrones; no certificación universal.',
                              'Las propuestas E siguen sin aprobarse; PASS no certifica equivalencias pendientes.']}
    write(OUT / 'PRESERVACION.json', pres)
    write(OUT / 'VALIDACION_ENTREGA.json', result)
    print(json.dumps({'estado': result['estado'], 'controles': controls, 'hallazgos': findings}, ensure_ascii=False))
    return 0 if all(controls.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
