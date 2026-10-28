#!/usr/bin/env python3
import json, pathlib, openpyxl
from common.analisis_desercion.retencion_primer_anio import calcular
ROOT=pathlib.Path(__file__).resolve().parents[2]
src=ROOT/'outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx'
w=openpyxl.load_workbook(src,read_only=True,data_only=True)
s=w['BASE_RETENCION_MU']
headers=list(next(s.iter_rows(values_only=True)))
rows=[dict(zip(headers,v)) for v in s.iter_rows(min_row=2,values_only=True)]
out=calcular(rows)
d=ROOT/'outputs/analisis_desercion_fase2'
d.mkdir(parents=True,exist_ok=True)
(d/'RETENCION_PRIMER_ANIO_AGREGADO.json').write_text(json.dumps({'fuente':str(src),'sha256':'19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd','resultados':out},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False))
