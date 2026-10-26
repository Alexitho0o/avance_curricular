#!/usr/bin/env python3
"""Consumidor intertrimestral del único servicio de códigos; no duplica reglas."""
from pathlib import Path
import runpy
if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).resolve().parents[1] / 'consultar_diccionario_sies_seguimiento.py'), run_name='__main__')
