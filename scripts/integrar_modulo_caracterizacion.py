#!/usr/bin/env python3
"""Incorpora una instantánea del árbol de trabajo sin modificar el origen.

Contrato: docs/unificacion_proyectos_y_reglas_negocio_20261015.md.
Solo archivos seguidos por Git y no ignorados; conserva cambios sin commit.
No copia .git ni publica, no ejecuta procesos operativos, no sobrescribe destinos.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def snapshot(root):
    entries = [x for x in git(root, 'ls-files', '--stage', '-z').decode().split('\0') if x]
    index = {}
    for entry in entries:
        metadata, name = entry.split('\t', 1)
        mode, oid, stage = metadata.split()
        if stage != '0' or mode not in ('100644', '100755'):
            raise ValueError('Entrada de Git requiere revisión explícita: ' + name)
        index[name] = (mode, oid)
    tracked = set(index)
    changed = set(git(root, 'diff', '--name-only', '-z').decode().split('\0')) - {''}
    extra = set(git(root, 'ls-files', '--others', '--exclude-standard', '-z').decode().rstrip('\0').split('\0')) - {''}
    # Los archivos históricos pueden ser placeholders de iCloud. Para los que
    # Git acredita sin cambios usamos su objeto del índice, sin esperar hidratación.
    names = sorted(tracked - changed)
    result = subprocess.run(['git', '-C', str(root), 'cat-file', '--batch'],
                            input=('\n'.join(index[n][1] for n in names) + '\n').encode(),
                            capture_output=True, check=True).stdout
    contents = {}; cursor = 0
    for name in names:
        end = result.index(b'\n', cursor)
        oid, kind, size = result[cursor:end].decode().split()
        if kind != 'blob':
            raise ValueError('Objeto Git no es archivo: ' + name)
        size = int(size); cursor = end + 1
        contents[name] = result[cursor:cursor + size]; cursor += size + 1
    files = {}
    for relative in sorted(tracked | extra):
        p = root / relative
        if p.is_symlink():
            raise ValueError('Enlace requiere revisión explícita: ' + relative)
        if not p.exists():
            continue  # A deleted tracked file must remain deleted in the snapshot.
        if not p.is_file() or not p.resolve().is_relative_to(root):
            raise ValueError('Archivo fuera del origen: ' + relative)
        if relative not in contents:
            contents[relative] = p.read_bytes()
        files[relative] = {'sha256': hashlib.sha256(contents[relative]).hexdigest(),
                           'bytes': len(contents[relative]), 'mode': p.stat().st_mode & 0o777,
                           'tracked': relative in tracked,
                           'read_from': 'git_index' if relative in names else 'working_tree'}
    return {'head': git(root, 'rev-parse', 'HEAD').decode().strip(),
            'status': git(root, 'status', '--porcelain=v1').decode(),
            'files': files, 'tracked_deleted': sorted(p for p in tracked if not (root / p).exists())}, contents


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origen', type=Path, required=True)
    args = parser.parse_args()
    source = args.origen.resolve()
    destination = ROOT / 'procesos/caracterizacion'
    evidence = ROOT / 'data/unificacion_proyectos/20261015'
    if destination.exists() or (evidence / 'importacion.json').exists():
        raise FileExistsError('La instantánea ya existe; no se sobrescribe.')
    before, contents = snapshot(source)
    for relative, meta in before['files'].items():
        dest = destination / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(contents[relative]); dest.chmod(meta['mode'])
        if hashlib.sha256(dest.read_bytes()).hexdigest() != meta['sha256']:
            raise ValueError('Origen cambió durante copia: ' + relative)
    after, _ = snapshot(source)
    evidence.mkdir(parents=True, exist_ok=True)
    result = {**before, 'source': str(source), 'destination': 'procesos/caracterizacion',
              'source_unchanged_during_copy': before == after,
              'scope': 'Tracked and nonignored untracked working tree files; no .git, ignored local sources or environments',
              'git_history_merged': False, 'original_repository_deleted': False,
              'remote_published': False}
    (evidence / 'importacion.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    if before != after:
        raise ValueError('El origen cambió concurrentemente. Instantánea requiere revisión.')
    print(json.dumps({'files': len(before['files']), 'bytes': sum(x['bytes'] for x in before['files'].values()),
                      'source_unchanged': True, 'head': before['head']}))


if __name__ == '__main__':
    main()
