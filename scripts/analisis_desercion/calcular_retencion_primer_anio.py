#!/usr/bin/env python3
import argparse, hashlib, json, pathlib, openpyxl
from common.analisis_desercion.retencion_primer_anio import calcular, agrupar_h001
ROOT=pathlib.Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description='Indicador interno H001 de retención de primer año.')
parser.add_argument('--cohortes', nargs='+', type=int, default=[2022, 2023, 2024, 2025])
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
map_path=ROOT/'analisis_desercion_ipss/reglas/MAPEO_SECTOR_IPSS_H001.json'
mapping=json.loads(map_path.read_text(encoding='utf-8'))
out=calcular(rows, catalogo, args.cohortes)
groups=agrupar_h001(rows, catalogo, mapping['mapeo_por_cod_car'], args.cohortes)
for total, visible in zip(out,groups['institucional']):
 if total['denominador']>=10:
  assert (total['denominador'],total['retenidos']) == (visible['casos'],visible['retenidos'])
d=ROOT/'outputs/retencion_primer_anio_h001_activo_20261028'
d.mkdir(parents=True,exist_ok=True)
payload={'rotulo':'Indicador interno alineado con la definición oficial SIES; no es la tasa oficial',
         'estado':'ACTIVA_INTERNA','unidad':'persona por cohorte','umbral_publicacion':10,
         'fuente_diagnostico':str(src),'fuente_sha256':'5f0f7c7f0f238556de374d287bf2931ccc8a93a5489f4c2f2b543befd38c77b3',
         'mapeo_carreras_sha256':hashlib.sha256(map_path.read_bytes()).hexdigest(),
         'fuente_mapeo':mapping['origen'],'grupos':groups}
output=d/'RETENCION_PRIMER_ANIO_AGREGADO.json'
content=json.dumps(payload,ensure_ascii=False,indent=2)+'\n'
if output.exists() and output.read_text(encoding='utf-8') != content:
 raise FileExistsError('La salida ya existe y difiere; no se sobrescribe.')
output.write_text(content,encoding='utf-8')
print(json.dumps({'institucional':groups['institucional'],'sectores':len(groups['sector']),'carreras':len(groups['carrera'])},ensure_ascii=False))
