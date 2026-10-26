import csv
import hashlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '04_scripts'))
from preparar_etapa1_octubre_20261020 import FIELDS

SOURCE = ROOT / '07_resultados/borradores_prueba_no_oficiales/etapa1_octubre_20261020/PRUEBA_PES_OFERTA_2027_ETAPA1_17467_20261020_V04_SIN_SALTO_FINAL.csv'
rows = list(csv.reader(io.StringIO(SOURCE.read_text(encoding='utf-8')), delimiter=';', strict=True))
assert len(rows) == 161 and all(len(r) == 48 for r in rows)
blank = ['VACANTES_PRIMER_SEMESTRE', 'VACANTES_SEGUNDO_SEMESTRE', 'VALOR_MATRICULA_ANUAL', 'COSTO_TITULACION', 'VALOR_CERTIFICADO_DIPLOMA', 'ARANCEL_ANUAL', 'VIGENCIA_CARRERA']
typed = set(blank[:-1] + ['ANIO_INICIO'])
matrix = []
diplomas = []
for i, row in enumerate(rows, 2):
    is_diploma = row[FIELDS.index('COD_NIVEL_GLOBAL')] == '3' and row[FIELDS.index('COD_NIVEL_CARRERA')] == '5'
    if is_diploma:
        diplomas.append(i)
    record = []
    for field, value in zip(FIELDS, row):
        if is_diploma and field in blank:
            record.append(None)
        elif not value:
            record.append(None)
        elif field in typed:
            assert value.isdigit()
            record.append(int(value))
        else:
            record.append(value)
    matrix.append(record)
assert len(diplomas) == 21
data = {'source': str(SOURCE), 'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(), 'headers': FIELDS, 'rows': matrix, 'diploma_rows': diplomas, 'blank_fields': blank}
Path(__file__).with_name('input.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print('Preparados 161 registros, 48 columnas y 147 celdas de captura vacias en 21 diplomados.')
