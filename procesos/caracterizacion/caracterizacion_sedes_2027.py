"""Complete 2027 sede coverage from the catalog confirmed by the user."""
import json
from pathlib import Path
import pandas as pd
from caracterizacion_universo import normalizar_programa

CATALOG = Path(__file__).resolve().parent/'docs/gobernanza/CATALOGO_SEDES_2027.json'


def communication_sede(value, catalog=None):
    mapping = json.loads(CATALOG.read_text(encoding='utf-8'))['sedes'] if catalog is None else catalog
    code = normalizar_programa(value)
    if code in mapping:
        return normalizar_programa(mapping[code]['nombre'])
    return code or 'SIN_CODIGO'


def sede_distribution(students, column='SEDE', catalog=None):
    mapping = (json.loads(CATALOG.read_text(encoding='utf-8'))['sedes'] if catalog is None else catalog)
    raw = students[column] if column in students else pd.Series('',index=students.index)
    codes = raw.fillna('').map(normalizar_programa).replace('', 'SIN_CODIGO')
    result = []
    for code,total in sorted(codes.value_counts().items()):
        label = mapping.get(code)
        result.append({'codigo':code, 'nombre':label['nombre'] if label else f'{code} (codigo no gobernado)',
                       'tipo':label['tipo'] if label else 'POR_REVISAR', 'known':bool(label), 'total':int(total)})
    if sum(row['total'] for row in result) != len(students):
        raise ValueError('El desglose de sedes no concilia con su universo.')
    return result
