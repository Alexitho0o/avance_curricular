#!/usr/bin/env python3
"""Consumidor de Caracterización: misma edición, mismas reglas, sin copias."""
from pathlib import Path
import runpy
if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).resolve().parents[3] / 'scripts/consultar_diccionario_sies_seguimiento.py'), run_name='__main__')
