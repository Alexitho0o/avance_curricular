#!/usr/bin/env python3
"""Reproduce inicios por código y cambios de régimen sin cambiar equivalencias."""
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.reglas_negocio import inicio_codigo_oferta

OUT = ROOT / 'data/reglas_negocio/20261015'


def read_source(metadata):
    path = ROOT / metadata['path']
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != metadata['sha256']:
        raise ValueError('Fuente comprimida alterada')
    decoded = gzip.decompress(raw)
    if hashlib.sha256(decoded).hexdigest() != metadata['original_sha256']:
        raise ValueError('Los bytes originales no se recuperan íntegros')
    return csv.DictReader(io.StringIO(decoded.decode('latin1'), newline=''), delimiter=';')


def write_identical_or_new(name, obj):
    path = OUT / name
    content = json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + '\n'
    if path.exists() and path.read_text() != content:
        raise ValueError('Salida previa distinta: ' + name)
    path.write_text(content)


def main():
    sources = json.loads((OUT / 'fuentes.json').read_text())
    offers = []; old = {}; total = 0
    for n, row in enumerate(read_source(sources['oferta_csv_nacional']), 2):
        total += 1
        if None in row or len(row) != 69 or any(v is None for v in row.values()):
            raise ValueError('Fila nacional incompleta')
        if row['Código IES'] == '162':
            offers.append({'anio': int(row['Año'][4:]), 'codigo_unico': row['Código Único'], 'registro_csv': n})
            if row['Año'] == 'OFE_2026':
                old[row['Código Único']] = row
    if total != 395719 or len(offers) != 747:
        raise ValueError('Universo distinto de la edición auditada')
    maestro = json.loads((ROOT / 'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json').read_text())
    starts = [inicio_codigo_oferta(offers, r['codigo_unico']) for r in maestro['universo_sies']]
    new = {}; changes = []
    for n, row in enumerate(read_source(sources['reporte_5910_2027']), 2):
        key = f"I{row['CODIGO_IES_NUM']}S{row['COD_SEDE']}C{row['COD_CARRERA']}J{row['COD_JORNADA']}V{row['VERSION']}"
        if key in new:
            raise ValueError('Código repetido en reporte 5910')
        new[key] = row
        previous = old.get(key)
        if previous and previous['Régimen'] != row['REGIMEN']:
            changes.append({'codigo_unico': key, 'nombre': row['NOMBRE_CARRERA'], 'registro_reporte_5910': n,
                            'regimen': [previous['Régimen'], row['REGIMEN']],
                            'duracion_regimen': [previous['Duración formal del Régimen'], row['DURACION_REGIMEN']],
                            'duracion_estudios': [previous['Duración Estudios'], row['DURACION_ESTUDIOS']],
                            'duracion_total': [previous['Duración Total'], row['DURACION_TOTAL']]})
    report = {'codigos_comunes': len(old.keys() & new.keys()), 'cambios_regimen_mismo_codigo': len(changes),
              'cambios': changes, 'fuentes': ['oferta_csv_nacional', 'reporte_5910_2027'],
              'formula_conversion_inferida': False}
    assert len(new) == 140 and report['codigos_comunes'] == 103 and len(changes) == 34
    assert all(x['regimen'] == ['1', '2'] and len(set(x['duracion_estudios'])) == 1
               and len(set(x['duracion_total'])) == 1 for x in changes)
    write_identical_or_new('inicios_por_codigo.json', {'regla': 'INT-OFERTA-INICIO-001', 'codigos': starts})
    write_identical_or_new('comparacion_regimen_2026_2027.json', report)
    print(json.dumps({'filas_nacionales': total, 'filas_ipss': len(offers), 'codigos_diccionario': len(starts),
                      'codigos_con_inicio_oferta': sum(x['anio_inicio_diccionario'] is not None for x in starts),
                      'cambios_regimen_mismo_codigo': len(changes)}))


if __name__ == '__main__':
    main()
