#!/usr/bin/env python3
"""Auditoria agregada del cruce SIES; no ejecuta el proceso de Caracterizacion."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from caracterizacion_catalogo_sies_2027 import enrich_frame


def auditar(source, periodo):
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    fields = ['CODCARPR','NOMBRE_L','SEDE','JORNADA','ANOMATRICULA','PERIODOMATRICULA']
    frame = pd.read_excel(source, sheet_name='Hoja1', usecols=fields, dtype=str, keep_default_na=False)
    target = frame.loc[pd.to_numeric(frame.ANOMATRICULA, errors='coerce').eq(2027)
                       & pd.to_numeric(frame.PERIODOMATRICULA, errors='coerce').eq(periodo)]
    enriched, summary = enrich_frame(target, anio=2027, periodo=periodo)
    pd.testing.assert_frame_equal(target, enriched[target.columns])
    if hashlib.sha256(source.read_bytes()).hexdigest() != digest:
        raise ValueError('La fuente cambio durante la lectura')
    grouped = enriched.groupby(['CODCARPR','NOMBRE_L','SEDE','JORNADA','ESTADO_CRUCE_SIES','ESTADO_CODIGO_SIES','ESTADO_MODALIDAD',
                                'CODIGO_UNICO_SIES','MODALIDAD_CARRERA','CANDIDATOS_SIES'], dropna=False).size()
    summary.update(fuente={'archivo':source.name, 'sha256':digest, 'hoja':'Hoja1', 'columnas':fields},
                   alcance='Registros con ANOMATRICULA=2027 y PERIODOMATRICULA seleccionado; sin filtros de firma, estado ni primer ingreso; no equivale al universo elegible',
                   dimensiones=grouped.rename('registros').reset_index().to_dict('records'),
                   originales_conservados=True)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--alumnos', type=Path, required=True)
    parser.add_argument('--periodo', type=int, choices=[1,2,3], required=True)
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    report = auditar(args.alumnos, args.periodo)
    raw = (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)+'\n').encode('utf-8')
    if args.salida.exists() and args.salida.read_bytes() != raw:
        raise ValueError('No sobrescribir una auditoria anterior diferente')
    if not args.salida.exists():
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        with args.salida.open('xb') as stream:
            stream.write(raw)
    print(json.dumps({'registros':report['registros'],'estados_codigo_sies':report['estados_codigo_sies'],
                      'estados_modalidad':report['estados_modalidad'],'modalidades':report['modalidades'],
                      'conciliacion':report['conciliacion_registros']}))
