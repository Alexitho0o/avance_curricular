#!/usr/bin/env python3
"""Consulta H5 con maestro/manifiesto explícitos; no ejecuta matrícula.

Salida 0: oferta anual localizada o equivalencia acreditada (estados distintos).
Salida 2: entrada incompleta, pendiente, conflicto, fuera de ámbito o sin dato.
Salida 1: archivo, SHA, esquema o regla inválidos. Todo resultado es JSON.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.equivalencias_historicas import cargar_maestro, consultar_sies, resolver_umas


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--maestro', required=True, type=Path)
    parser.add_argument('--manifest', type=Path, help='Por defecto manifest.json junto al maestro')
    parser.add_argument('--anio', required=True, type=int)
    query = parser.add_mutually_exclusive_group(required=True)
    query.add_argument('--codigo-unico', help='Consulta únicamente oferta SIES del año')
    query.add_argument('--codcarpr', help='Consulta equivalencia UMAS con todos sus criterios')
    parser.add_argument('--nombre-interno')
    parser.add_argument('--plan-umas')
    parser.add_argument('--sede-umas')
    parser.add_argument('--jornada-umas')
    parser.add_argument('--periodo', help='Literal de período UMAS, sin conversión a semestre SIES')
    parser.add_argument('--regimen', help='Literal de régimen UMAS')
    args = parser.parse_args(argv)
    if args.codigo_unico is not None and any(value is not None for value in
            (args.nombre_interno, args.plan_umas, args.sede_umas, args.jornada_umas, args.periodo, args.regimen)):
        parser.error('La consulta por Código Único no combina parámetros UMAS')
    try:
        maestro = cargar_maestro(args.maestro, args.manifest)
        if args.codigo_unico is not None:
            result = consultar_sies(maestro, anio=args.anio, codigo_unico=args.codigo_unico)
        else:
            result = resolver_umas(
                maestro, anio=args.anio, periodo=args.periodo, regimen=args.regimen,
                codcarpr=args.codcarpr, nombre_interno=args.nombre_interno,
                plan_umas=args.plan_umas, sede_umas=args.sede_umas, jornada_umas=args.jornada_umas,
            )
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({'estado': 'CARGA_RECHAZADA', 'motivo': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result['estado'] in {'OFERTA_ANUAL_LOCALIZADA', 'EQUIVALENCIA_ACREDITADA'} else 2


if __name__ == '__main__':
    raise SystemExit(main())
