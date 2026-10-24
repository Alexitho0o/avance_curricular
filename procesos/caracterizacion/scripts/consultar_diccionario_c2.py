#!/usr/bin/env python3
"""Entrada de Caracterización al diccionario común del repositorio integrado."""
from pathlib import Path
import runpy
if __name__=='__main__':
    runpy.run_path(str(Path(__file__).resolve().parents[3]/'scripts/consultar_diccionario_c2.py'),run_name='__main__')
