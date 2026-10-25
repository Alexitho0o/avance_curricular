#!/usr/bin/env python3
"""Entrada común. JSON por stdin; respuesta individual solo a archivo privado."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento, ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--salida-privada', type=Path, required=True)
    args = parser.parse_args()
    output = args.salida_privada.expanduser().resolve()
    if not output.parent.is_dir() or output.is_relative_to(ROOT) or output.exists():
        raise ValueError('Se requiere archivo nuevo en carpeta privada existente fuera del repositorio')
    if subprocess.run(['git', '-C', str(output.parent), 'rev-parse', '--show-toplevel'], capture_output=True).returncode == 0:
        raise ValueError('Salida dentro de Git')
    requests = json.load(sys.stdin)
    if not isinstance(requests, list):
        raise ValueError('Entrada debe ser lista de consultas')
    service = DiccionarioSiesSeguimiento()
    result = []
    try:
        for item in requests:
            method = item['metodo']
            if method not in ('consultar', 'codigos_mu', 'seguir_cohorte'):
                raise ValueError('Método fuera del contrato')
            result.append(getattr(service, method)(**item['entrada']))
    finally:
        service.close()
    with os.fdopen(os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps({'consultas': len(result), 'salida_privada': str(output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
