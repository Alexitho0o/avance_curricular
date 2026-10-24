#!/usr/bin/env python3
"""Instala la edición H7 idéntica en un consumidor, sin ejecutar sus motores.

Repetir es idempotente. Un archivo diferente bloquea toda la prevalidación.
La edición se fija por el descriptor del cliente; no se actualiza en sitio.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.consulta_sies_historica import DESCRIPTOR, DESCRIPTOR_SHA256, VERSION, digest


def construir_entrega():
    h5 = ROOT / 'data/versiones_historicas_sies_umas/fase_5_20261015'
    h6 = ROOT / 'data/versiones_historicas_sies_umas/fase_6_20261015'
    sources = {'maestro.json': h5 / 'maestro.json', 'manifest_h5.json': h5 / 'manifest.json',
               'resolutor.py': ROOT / 'common/equivalencias_historicas.py',
               'aceptacion_h6.json': h6 / 'aceptacion_h6.json'}
    blobs = {name: path.read_bytes() for name, path in sources.items()}
    descriptor = {'schema_version': 1, 'version': VERSION, 'periodo_objetivo': [2007, 2026],
                  'origen': 'avance_curricular/H5; validación H6',
                  'reglas_efectivas_acreditadas': 0, 'asignacion_individual_habilitada': False,
                  'archivos': {name: {'path': VERSION + '/' + name, 'sha256': digest(raw)}
                               for name, raw in blobs.items()}}
    raw = (json.dumps(descriptor, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()
    if digest(raw) != DESCRIPTOR_SHA256:
        raise ValueError('Las fuentes no corresponden al descriptor H7 gobernado')
    if json.loads(blobs['maestro.json'])['reglas_efectivas'] != []:
        raise ValueError('No se distribuyen reglas nuevas en esta edición')
    base = Path('gobernanza/sies/historico')
    files = {base / VERSION / name: data for name, data in blobs.items()}
    files[base / DESCRIPTOR] = raw
    for name in ('common/consulta_sies_historica.py', 'scripts/consultar_sies_historico.py'):
        files[Path(name)] = (ROOT / name).read_bytes()
    return files


def exportar(destino):
    destino = Path(destino).resolve()
    files = construir_entrega()
    # Revisar todos los destinos antes de crear carpetas o escribir un byte.
    for relative, raw in files.items():
        target = destino / relative
        if target.is_symlink() or not target.resolve().is_relative_to(destino):
            raise ValueError('Destino externo o simbólico: ' + str(relative))
        if target.exists() and (not target.is_file() or target.read_bytes() != raw):
            raise ValueError('Destino existente diferente: ' + str(relative))
        for parent in target.parents:
            if parent == destino.parent:
                break
            if parent.exists() and not parent.is_dir():
                raise ValueError('Carpeta de destino inválida: ' + str(relative))
    for relative, raw in files.items():
        target = destino / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            with target.open('xb') as stream:
                stream.write(raw)
    return {'version': VERSION, 'descriptor_sha256': DESCRIPTOR_SHA256,
            'archivos': {str(p): digest(raw) for p, raw in sorted(files.items())}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destino', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(exportar(args.destino), ensure_ascii=False, sort_keys=True, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'estado': 'EXPORTACION_RECHAZADA', 'motivo': str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
