#!/usr/bin/env python3
"""Consulta histórica integrada H7; no ejecuta pipelines ni modifica Excel.

Salida 0: todas las consultas localizan oferta o equivalencia acreditada.
Salida 2: al menos una consulta pendiente, incompleta o fuera de ámbito.
Salida 1: error de contrato/integridad/lectura. Resultado JSON en stdout.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.consulta_sies_historica import ConsultaHistorica


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--lote', type=Path, help='JSON: lista de {tipo, parametros} académicos')
    modes.add_argument('--codigo-unico')
    modes.add_argument('--codcarpr')
    parser.add_argument('--anio', type=int)
    for name in ('periodo', 'regimen', 'nombre-interno', 'plan-umas', 'sede-umas', 'jornada-umas'):
        parser.add_argument('--' + name)
    args = parser.parse_args(argv)
    umas = {key: getattr(args, key) for key in
            ('periodo', 'regimen', 'nombre_interno', 'plan_umas', 'sede_umas', 'jornada_umas')}
    if args.lote and (args.anio is not None or any(v is not None for v in umas.values())):
        parser.error('--lote no admite parámetros de consulta individual')
    if not args.lote and args.anio is None:
        parser.error('Se exige --anio explícito')
    if args.codigo_unico is not None and any(v is not None for v in umas.values()):
        parser.error('Código Único no combina parámetros UMAS')
    try:
        if args.lote:
            queries = json.loads(args.lote.read_text(encoding='utf-8'))
        elif args.codigo_unico is not None:
            queries = [{'tipo': 'SIES', 'parametros': {'anio': args.anio, 'codigo_unico': args.codigo_unico}}]
        else:
            queries = [{'tipo': 'UMAS', 'parametros': dict(umas, anio=args.anio, codcarpr=args.codcarpr)}]
        result = ConsultaHistorica().consultar_lote(queries)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({'estado': 'CARGA_RECHAZADA', 'motivo': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if all(r['resultado']['estado'] in {'OFERTA_ANUAL_LOCALIZADA', 'EQUIVALENCIA_ACREDITADA'}
                    for r in result['consultas']) else 2


if __name__ == '__main__':
    raise SystemExit(main())
