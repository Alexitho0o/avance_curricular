"""Recursos comunes del repositorio único; sin búsqueda de otro proyecto."""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def recurso_comun(nombre):
    config = json.loads((RAIZ / 'PROYECTO_IPSS.json').read_text(encoding='utf-8'))
    if config['schema_version'] != 1:
        raise ValueError('Contrato de proyecto incompatible')
    relative = Path(config['recursos_comunes'][nombre])
    path = (RAIZ / relative).resolve()
    if relative.is_absolute() or not path.is_relative_to(RAIZ) or not path.exists():
        raise ValueError('Recurso común ausente o fuera del repositorio: ' + nombre)
    return path
