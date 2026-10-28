#!/usr/bin/env python3
import argparse, json, pathlib, openpyxl
from common.analisis_desercion.retencion_primer_anio import calcular
ROOT=pathlib.Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description='Prototipo no activo de retención de primer año.')
parser.add_argument('--cohortes', nargs='+', type=int, default=[2022, 2023, 2024])
parser.add_argument('--integracion-intakes-acreditada', action='store_true', help='Declarar que la integración 2025 de 2.º y 3.er intake está acreditada.')
parser.add_argument('--tratamiento-vig-aprobado', action='store_true', help='Declarar que el tratamiento VIG 2025 está aprobado.')
args=parser.parse_args()
src=ROOT/'outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx'
w=openpyxl.load_workbook(src,read_only=True,data_only=True)
s=w['BASE_RETENCION_MU']
headers=list(next(s.iter_rows(values_only=True)))
rows=[dict(zip(headers,v)) for v in s.iter_rows(min_row=2,values_only=True)]
out=calcular(rows, args.cohortes, integracion_intakes_acreditada=args.integracion_intakes_acreditada, tratamiento_vig_aprobado=args.tratamiento_vig_aprobado)
d=ROOT/'outputs/analisis_desercion_fase2'
d.mkdir(parents=True,exist_ok=True)
(d/'RETENCION_PRIMER_ANIO_AGREGADO.json').write_text(json.dumps({'fuente':str(src),'sha256':'19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd','resultados':out},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False))
