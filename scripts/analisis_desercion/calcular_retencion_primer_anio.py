#!/usr/bin/env python3
import argparse, hashlib, json, pathlib, openpyxl
from common.analisis_desercion.retencion_primer_anio import calcular
ROOT=pathlib.Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description='Prototipo no activo de retención de primer año.')
parser.add_argument('--cohortes', nargs='+', type=int, default=[2022, 2023, 2024])
parser.add_argument('--cohorte-2025-conciliada', action='store_true', help='Declarar cohorte 2025 conciliada con la oficial de 1.163 casos, con diferencias explicadas.')
parser.add_argument('--tratamiento-vig-aprobado', action='store_true', help='Declarar que el tratamiento VIG 2025 está aprobado.')
args=parser.parse_args()
src=ROOT/'outputs/retencion_primer_anio_ipss_162/20260930_000000/RETENCION_PRIMER_ANIO_IPSS_162_DIAGNOSTICO_BRECHAS_20260930.xlsx'
with src.open('rb') as f:
 if hashlib.file_digest(f, 'sha256').hexdigest() != '5f0f7c7f0f238556de374d287bf2931ccc8a93a5489f4c2f2b543befd38c77b3':
  raise ValueError('El diagnóstico H001 no coincide con el hash gobernado.')
w=openpyxl.load_workbook(src,read_only=True,data_only=True)
s=w['BASE_RETENCION_MU']
headers=list(next(s.iter_rows(values_only=True)))
rows=[dict(zip(headers,v)) for v in s.iter_rows(min_row=2,values_only=True)]
cat=w['01_CATALOGO_CARRERA']
ch=list(next(cat.iter_rows(values_only=True)))
catalogo=[dict(zip(ch,v)) for v in cat.iter_rows(min_row=2,values_only=True)]
out=calcular(rows, catalogo, args.cohortes, cohorte_2025_conciliada=args.cohorte_2025_conciliada, tratamiento_vig_aprobado=args.tratamiento_vig_aprobado)
d=ROOT/'outputs/analisis_desercion_h001_borrador'
d.mkdir(parents=True,exist_ok=True)
(d/'RETENCION_PRIMER_ANIO_AGREGADO.json').write_text(json.dumps({'fuente':str(src),'sha256':'5f0f7c7f0f238556de374d287bf2931ccc8a93a5489f4c2f2b543befd38c77b3','estado':'BORRADOR_NO_ACTIVO_DIAGNOSTICO_H001','resultados':out},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False))
