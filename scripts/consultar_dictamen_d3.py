#!/usr/bin/env python3
"""Consulta D3 de lectura; salida 0 no significa asignación acreditada."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from common.consulta_dictamen_d3 import ConsultaD3

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lote',type=Path,required=True);args=p.parse_args(argv)
    try:result=ConsultaD3().consultar_lote(json.loads(args.lote.read_text(encoding='utf-8')))
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print(json.dumps({'estado':'CONSULTA_RECHAZADA','motivo':str(exc)},ensure_ascii=False),file=sys.stderr);return 1
    print(json.dumps(result,ensure_ascii=False,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
