#!/usr/bin/env python3
"""Ejecuta un comando explícito en su módulo, sin reinterpretar sus argumentos."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--listar', action='store_true')
    parser.add_argument('modulo', nargs='?')
    parser.add_argument('comando', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    config = json.loads((ROOT / 'PROYECTO_IPSS.json').read_text())
    if args.listar:
        print(json.dumps(config['modulos'], ensure_ascii=False, indent=2))
        return 0
    if args.modulo not in config['modulos']:
        parser.error('Indique un módulo registrado y un comando explícito')
    command = args.comando[1:] if args.comando[:1] == ['--'] else args.comando
    if not command:
        parser.error('Falta comando; no se ejecuta un proceso por defecto')
    directory = (ROOT / config['modulos'][args.modulo]['path']).resolve()
    if not directory.is_relative_to(ROOT):
        raise ValueError('Módulo fuera del repositorio')
    return subprocess.run(command, cwd=directory).returncode


if __name__ == '__main__':
    raise SystemExit(main())
