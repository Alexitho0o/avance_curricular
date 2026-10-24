#!/usr/bin/env python3
"""Consulta común C2. Salida 0: consulta ejecutada, nunca acreditación de candidatos."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from common.diccionario_c2 import DiccionarioC2

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lote',type=Path,required=True,help='Lista JSON de {modelo, entrada}, solo datos académicos')
    args=parser.parse_args(argv)
    try:
        result=DiccionarioC2().consultar_lote(json.loads(args.lote.read_text(encoding='utf-8')))
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print(json.dumps({'estado':'CONSULTA_RECHAZADA','motivo':str(exc)},ensure_ascii=False),file=sys.stderr)
        return 1
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    return 0
if __name__=='__main__':raise SystemExit(main())
