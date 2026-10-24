#!/usr/bin/env python3
"""QA de cierre D4: integridad, cobertura, preservación C1 y cachés XLSX (solo lectura)."""
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/cierre_d4/20261016'


def load(p):
    return json.loads(Path(p).read_text())


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    payload = load(BASE / 'libro_d4.json')
    matrix = load(BASE / 'matriz_resultados.json')
    agenda = load(BASE / 'agenda.json')
    hypotheses = load(BASE / 'hipotesis.json')
    d3 = load(ROOT / 'data/validacion_d3/20261016/dictamenes.json')
    inventory = {(x['universo'], x['id']): x for x in load(ROOT / 'data/cierre_d1/20261016/inventario.json')}
    assert len(hypotheses) == 9 and len(agenda) == 18
    aids = {a['id_agenda'] for a in agenda}
    assert all(a['responsable_designado'] is None for a in agenda)
    memberships = {(e['universo'], e['id'], a['id_agenda']) for a in agenda for e in a['elementos']}
    counts = {}
    for key, universe, idfield, expected in [('contextos', 'CONTEXTO', 'contexto', 1986), ('codigos_sies', 'CODIGO_SIES', 'id', 141), ('planes_umas', 'PLAN_UMAS', 'id', 236)]:
        rows = matrix['universos'][key]
        assert len(rows) == expected and len({r[idfield] for r in rows}) == expected
        for r, original in zip(rows, d3[key]):
            assert {k: v for k, v in r.items() if k != 'cierre_d4'} == original
            assert r['codigo_asignado'] is None and r['habilitada_para_resolver'] is False
            references = r['cierre_d4']['agenda']
            assert references and set(references) <= aids
            assert set(references) == {'D4-' + c for c in inventory[(universe, r[idfield])]['causas_pendientes']}
            assert all((universe, r[idfield], a) in memberships for a in references)
        counts[key] = len(rows)
    assert matrix['incidencias_cilog_d3'] == d3['incidencias_cilog']
    protected = load(ROOT / 'data/unificacion_proyectos/20261015/control_preservacion_final.json')['referencias_sha256']
    for p, digest in protected.items():
        assert sha(ROOT / p) == digest, p
    frozen_packages = ['data/diccionario_c1/20261016/entrega.json', 'data/consumo_comun_c2/20261016/qa.json', 'data/cierre_d2/20261016/manifest_cierre.json', 'data/validacion_d3/20261016/entrega.json']
    for f in frozen_packages + ['data/cierre_d4/20261016/fuentes.json']:
        for p, digest in load(ROOT / f)['archivos_sha256'].items():
            assert sha(ROOT / p) == digest, (f, p)
    c1 = load(ROOT / frozen_packages[0])
    assert sha(c1['original_preservado']) == c1['fuente_sha256'], 'Excel original cambiado'
    src = openpyxl.load_workbook(payload['source'], data_only=False)
    out = openpyxl.load_workbook(payload['output'], data_only=False)
    cached = openpyxl.load_workbook(payload['output'], data_only=True)
    assert out.sheetnames[:len(src.sheetnames)] == src.sheetnames
    assert len(out.sheetnames) == 21
    checked, formats, scroll = 0, Counter(), []
    for s in src:
        t = out[s.title]
        for row in s:
            for c in row:
                if c.value is None:
                    continue
                checked += 1
                o = t[c.coordinate]
                assert c.value == o.value, (s.title, c.coordinate, c.value, o.value)
                for attr in ('font', 'fill', 'alignment', 'number_format', 'border', 'protection'):
                    if str(getattr(c, attr)) != str(getattr(o, attr)):
                        formats[attr] += 1
        assert not formats, (s.title, dict(formats))
        assert s.merged_cells == t.merged_cells, (s.title, 'combinaciones')
        assert s.auto_filter == t.auto_filter, (s.title, 'filtro')
        assert s.data_validations == t.data_validations, (s.title, 'validaciones')
        assert set(s.tables) == set(t.tables), (s.title, 'tablas')
        for k in s.tables:
            assert s.tables[k].ref == t.tables[k].ref and s.tables[k].autoFilter == t.tables[k].autoFilter
        ap, bp = s.sheet_view.pane, t.sheet_view.pane
        assert (ap is None) == (bp is None)
        if ap:
            assert (ap.xSplit, ap.ySplit, ap.state) == (bp.xSplit, bp.ySplit, bp.state)
            if ap.topLeftCell != bp.topLeftCell:
                scroll.append(s.title)
        for dims in ('row_dimensions', 'column_dimensions'):
            x, y = getattr(s, dims), getattr(t, dims)
            assert {k for k, v in x.items() if v.hidden} == {k for k, v in y.items() if v.hidden}
    newchecked = 0
    for info in payload['sheets']:
        s = out[info['name']]
        assert [s.cell(5, j+1).value for j in range(len(info['headers']))] == info['headers']
        for i, row in enumerate(info['rows'], 6):
            for j, value in enumerate(row, 1):
                actual = s.cell(i, j).value
                assert (None if actual == '' else actual) == (None if value == '' else value), (s.title, i, j)
                newchecked += 1
    # Compare the copied 2026 attributes against the original code-indexed sheet.
    dic = src['Diccionario SIES']
    sectors = {dic.cell(i, 1).value: [dic.cell(i, j).value for j in [2, 3, 10, 11, 12, 19, 20, 21]] for i in range(6, 147)}
    code_sheet = out['Códigos D3']
    for i in range(6, 147):
        code = code_sheet.cell(i, 1).value
        assert [code_sheet.cell(i, j).value for j in range(2, 10)] == sectors[code], ('atributos', code)
    errors = [(s.title, c.coordinate, c.value) for s in cached for row in s for c in row if c.data_type == 'e']
    assert not errors, errors[:10]
    q = cached['Cierre D4']
    assert q['B10'].value == 'USO_ANALITICO_CORROBORADO'
    assert q['B27'].value == 1986
    summary = load(ROOT / 'data/validacion_d3/20261016/resumen.json')
    for i, state in enumerate(summary['dictamen_contextos'], 21):
        assert q[f'A{i}'].value == state and q[f'B{i}'].value == summary['dictamen_contextos'][state]
    assert cached['Consulta B5']['B20'].value == 'CORROBORADA_EN_RESERVA'
    assert [cached['Consulta B5'][f'B{i}'].value for i in range(35, 39)] == [197, 211, 15, 1]
    formulas = load(BASE / 'qa_formulas.json')
    assert len(formulas['consultas']) == 6 and formulas['fronteras'] == 2
    frozen = subprocess.run([sys.executable, 'scripts/gobernanza/verificar_separacion_fcu.py'], cwd=ROOT / 'procesos/caracterizacion', capture_output=True, text=True)
    assert frozen.returncode == 0, frozen.stderr
    # Reproduction of JSON tables without touching any earlier package.
    generated = ['hipotesis.json', 'agenda.json', 'matriz_resultados.json', 'ejemplos.json', 'libro_d4.json', 'fuentes.json']
    before = {p: sha(BASE / p) for p in generated}
    run = subprocess.run([sys.executable, 'scripts/preparar_cierre_d4.py'], cwd=ROOT, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert before == {p: sha(BASE / p) for p in generated}, 'Reproducción JSON'
    qa = {'estado': 'VERIFICADO', 'universos': counts, 'hipotesis': len(hypotheses), 'categorias_agenda': len(agenda), 'todos_los_elementos_con_agenda': True,
          'registros_d3_preservados_integros': sum(counts.values()), 'hojas': len(out.sheetnames), 'celdas_c1_preservadas': checked, 'celdas_d4_verificadas': newchecked,
          'codigos_con_nombres_modalidad_sectores_preservados': len(sectors), 'diferencias_formato_c1': dict(formats), 'viewport_reiniciado_sin_cambiar_paneles': scroll,
          'tablas_filtros_validaciones_paneles_conservados': True, 'errores_excel_en_cache': errors, 'consultas_estado': 6, 'consultas_frontera': 2,
          'fuente_usuario_preservada': True, 'paquetes_anteriores_preservados': frozen_packages, 'referencias_protegidas': len(protected), 'fcu': json.loads(frozen.stdout),
          'reproduccion_json_identica': len(generated), 'recalculo_nativo_excel_verificado': False, 'validacion_independiente_nueva': False, 'asignaciones_activadas': 0,
          'sha256_excel': sha(payload['output'])}
    (BASE / 'qa.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
