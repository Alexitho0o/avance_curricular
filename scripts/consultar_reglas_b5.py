#!/usr/bin/env python3
"""Consulta local del registro B5 verificado; no devuelve equivalencias acreditadas."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from common.reglas_historicas_b5 import consultar,EXTRAS
from scripts.fuentes_ensayo_enlace_conjunto import sha

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entrada',required=True,help='JSON con la clave académica, sin identificadores personales')
    parser.add_argument('--modelo',choices=EXTRAS,default='K0')
    args=parser.parse_args()
    base=ROOT/'data/reglas_historicas_b5/20261016'
    manifest=json.loads((base/'manifest.json').read_text())
    name='reglas_observadas.json'
    if sha(base/name)!=manifest['salidas_sha256'][name]:raise ValueError('Registro B5 alterado')
    engine='common/reglas_historicas_b5.py'
    if sha(ROOT/engine)!=manifest['fuentes_y_codigo_sha256'][engine]:raise ValueError('Regla de consulta alterada')
    entrada=json.loads(Path(args.entrada).read_text())
    print(json.dumps(consultar(json.loads((base/name).read_text()),entrada,args.modelo),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
