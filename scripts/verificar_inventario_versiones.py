#!/usr/bin/env python3
"""Comprueba estructura y huellas del inventario histórico sin leer filas personales.

Solo consulta archivos. No ejecuta el motor SIES, no modifica fuentes y no
recalcula el cruce. Un original ausente declarado no invalida el inventario,
pero nunca se informa como disponible ni verificado.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def verificar(path: Path) -> dict:
    """Devuelve controles de integridad de la instantánea seleccionada."""
    payload = json.loads(path.read_text(encoding='utf-8'))
    sources = payload['sources']
    required = {'id', 'path', 'sha256', 'size', 'availability', 'role',
                'coverage', 'locator', 'key_fields', 'key_status', 'limits'}
    ids = [s['id'] for s in sources]
    errors = []
    if len(ids) != len(set(ids)):
        errors.append('IDs de fuentes duplicados')
    checked = []
    for s in sources:
        missing = sorted(required - s.keys())
        if missing:
            errors.append(f"{s['id']}: faltan campos {missing}")
        p = Path(s['path'])
        if s.get('sha256'):
            if not p.is_file():
                errors.append(f"{s['id']}: bytes inventariados ya no disponibles")
                checked.append({'id': s['id'], 'status': 'ARCHIVO_NO_DISPONIBLE'})
                continue
            with p.open('rb') as stream:
                actual = hashlib.file_digest(stream, 'sha256').hexdigest()
            ok = actual == s['sha256'] and p.stat().st_size == s['size']
            checked.append({'id': s['id'], 'status': 'COINCIDE' if ok else 'CAMBIO'})
            if not ok:
                errors.append(f"{s['id']}: huella o tamaño diferente")
        else:
            checked.append({'id': s['id'], 'status': 'SIN_HUELLA_VERIFICADA'})
            if s.get('availability') == 'BYTES_LEIDOS':
                errors.append(f"{s['id']}: declara lectura sin huella")
    for group in ('joins', 'gaps'):
        for item in payload[group]:
            for source_id in item.get('source_ids', []):
                if source_id not in ids:
                    errors.append(f"{item['id']}: fuente no inventariada {source_id}")
    return {'schema_version': 1, 'inventory': str(path.resolve()),
            'sources': len(sources), 'checks': checked,
            'errors': errors, 'ok': not errors,
            'scope': 'Integridad de metadatos y bytes; no valida equivalencias curriculares ni personas.'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inventario', type=Path)
    args = parser.parse_args()
    result = verificar(args.inventario)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
