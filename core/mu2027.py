#!/usr/bin/env python3
"""Entrada MU2027 para verificar, consultar y versionar reglas internas VIG."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import control_reglas_mu2027 as c


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--registro', type=Path, default=c.REGISTRO)
    sub = p.add_subparsers(dest='operacion', required=True)
    v = sub.add_parser('verificar')
    v.add_argument('--carga-sies', action='store_true')
    q = sub.add_parser('consultar')
    q.add_argument('--estado', required=True)
    q.add_argument('--situacion', required=True)
    for s in (v, q):
        s.add_argument('--version')
        s.add_argument('--manifest-sha256')
    r = sub.add_parser('registrar')
    r.add_argument('--version', required=True)
    r.add_argument('--reglas', required=True, type=Path)
    r.add_argument('--autorizacion', required=True, type=Path)
    r.add_argument('--ejecutor', required=True)
    r.add_argument('--anterior-sha256')
    e = sub.add_parser('ejecucion')
    e.add_argument('--destino', required=True, type=Path)
    e.add_argument('--entrada', required=True, action='append')
    e.add_argument('--salida', required=True, action='append')
    e.add_argument('--responsable', required=True)
    e.add_argument('--parametros', required=True, type=Path)
    e.add_argument('--version', required=True)
    e.add_argument('--manifest-sha256', required=True)
    a = p.parse_args()
    try:
        if a.operacion == 'verificar':
            _, m, h = c.verificar(a.registro, a.version, a.manifest_sha256, a.carga_sies)
            out = {'resultado': 'OK_REVISION_INTERNA', 'version': m['version'], 'manifest_sha256': h}
        elif a.operacion == 'consultar':
            out = c.consultar(a.estado, a.situacion, a.registro, a.version, a.manifest_sha256)
        elif a.operacion == 'registrar':
            out = c.registrar(a.registro, a.version, c.leer(a.reglas), c.leer(a.autorizacion), a.ejecutor, a.anterior_sha256)
        else:
            out = c.ejecucion(a.destino, a.entrada, a.salida, a.responsable, c.leer(a.parametros),
                              a.registro, a.version, a.manifest_sha256)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    except c.Bloqueo as e:
        print('BLOQUEADO: ' + str(e), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
