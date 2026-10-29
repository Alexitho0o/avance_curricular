#!/usr/bin/env python3
"""Propone candidatos dimensionales; nunca cambia la tabla H002 ni aprueba filas."""
import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/paridad_codigo_sies_20261029'
HEADER = ['CODCARPR', 'CODIGO_PLAN', 'NOMBRE_PLAN', 'SEDE', 'JORNADA', 'MODALIDAD',
          'DURACION_SEMESTRES', 'TIPO_PLAN', 'ADMITE_NUEVOS_2027']


def norm(text):
    s = unicodedata.normalize('NFD', str(text)).upper()
    return ' '.join(''.join(c for c in s if unicodedata.category(c) != 'Mn').split())


def parse(raw):
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')), delimiter='\t')
    if reader.fieldnames != HEADER:
        raise ValueError('Encabezado incorrecto: debe coincidir exactamente con la plantilla TSV de nueve columnas')
    rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError('Cantidad de campos distinta de nueve')
    if any(not row['CODCARPR'].strip() or not row['CODIGO_PLAN'].strip() for row in rows):
        raise ValueError('CODCARPR y CODIGO_PLAN son obligatorios')
    seen = set()
    for row in rows:
        key = tuple(row[k].strip() for k in ('CODCARPR', 'CODIGO_PLAN', 'SEDE', 'JORNADA'))
        if key in seen:
            raise ValueError('Plan/contexto duplicado; no elegir primera fila')
        seen.add(key)
    return rows


def dimensiones(row):
    site = {'RE': '2', 'CO': '3', 'PTG': '4', '2': '2', '3': '3', '4': '4'}.get(norm(row['SEDE']))
    jour = {'D': '1', 'V': '2', 'O': '4', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5'}.get(norm(row['JORNADA']))
    mod = {'1': '1', 'PRESENCIAL': '1', '2': '2', 'SEMIPRESENCIAL': '2', '3': '3', 'NO PRESENCIAL': '3'}.get(norm(row['MODALIDAD']))
    kind = {'1': '1', 'PLAN REGULAR': '1', '2': '2', 'PLAN ESPECIAL': '2',
            '3': '3', 'PLAN REGULAR DE CONTINUIDAD': '3'}.get(norm(row['TIPO_PLAN']))
    dur = row['DURACION_SEMESTRES'].strip()
    duration = str(int(dur)) if dur.isdigit() and int(dur) > 0 else None
    return (site, jour, mod, duration, kind)


def proponer(plans, targets):
    proposals = []
    for target in targets:
        wanted = (target['cod_sede'], target['cod_jornada'], target['modalidad_codigo'],
                  target['duracion_total_semestres'], target['tipo_plan_codigo'])
        candidates = []
        for row in plans:
            dims = dimensiones(row)
            if None in dims or dims != wanted:
                continue
            admission = norm(row['ADMITE_NUEVOS_2027'])
            candidates.append({'CODCARPR': row['CODCARPR'], 'CODIGO_PLAN': row['CODIGO_PLAN'],
                'NOMBRE_PLAN': row['NOMBRE_PLAN'], 'dimensiones_coinciden': True,
                'apoyo_nombre': 'IGUAL_NORMALIZADO' if norm(row['NOMBRE_PLAN']) == norm(target['nombre_carrera']) else 'NOMBRE_DISTINTO_REVISAR',
                'admite_nuevos_2027_declarado': row['ADMITE_NUEVOS_2027'],
                'admision_concordante': (admission in ('SI', '1') and target['vigencia_2027'] == '1') or
                                        (admission in ('NO', '0') and target['vigencia_2027'] in ('2', '3')),
                'clase': 'E_PROPUESTA_NO_APROBADA'})
        proposals.append({'codigo_unico': target['codigo_unico'], 'nombre_SIES': target['nombre_carrera'],
            'candidatos': candidates, 'estado': 'SIN_CANDIDATOS_E' if not candidates else 'PROPUESTA_DIMENSIONAL_E',
            'eleccion_automatica': False, 'tabla_H002_modificada': False})
    return proposals


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('listado', type=Path)
    ap.add_argument('--salida', type=Path, required=True, help='Nuevo JSON separado dentro de outputs H002')
    args = ap.parse_args()
    dest = args.salida.resolve()
    if not dest.is_relative_to(OUT.resolve()) or dest.exists() or dest.suffix != '.json':
        ap.error('La propuesta debe ser un JSON nuevo dentro de outputs H002; no sobrescribir tabla ni archivo existente')
    raw = args.listado.read_bytes()
    rows = parse(raw)
    if not rows:
        ap.error('El listado contiene solo encabezados; no hay planes oficiales para cruzar')
    table_path = ROOT / 'data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json'
    table_raw = table_path.read_bytes()
    targets = [r for r in json.loads(table_raw)['filas'] if r['anio'] == 2027 and r['estado'] == 'NUEVO_2027_SIN_PLAN_E']
    if len(targets) != 43:
        raise ValueError('El universo pendiente cambió: revisar antes de cruzar')
    proposal = {'clase': 'C/E', 'listado_sha256': hashlib.sha256(raw).hexdigest(),
        'tabla_fuente_sha256': hashlib.sha256(table_raw).hexdigest(),
        'criterio': 'Sede+jornada+modalidad+duración+tipo exactos; nombre solo como apoyo, sin aprobar ni asignar personas.',
        'filas_listado': len(rows), 'codigos_pendientes': 43, 'propuestas': proponer(rows, targets),
        'supuestos': 'Letras D/V/O y RE/CO/PTG según catálogo; cifras de jornada/modalidad/tipo deben ser códigos SIES expresamente declarados en el listado.',
        'no_ejecuta_cargas': True}
    blob = json.dumps(proposal, ensure_ascii=False, sort_keys=True, indent=2) + '\n'
    clean = re.sub(r'\b[a-fA-F0-9]{64}\b', 'HASH', blob)
    for pattern in [r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b',
                    r'(?<!\w)(?:\d{1,2}\.\d{3}\.\d{3}|\d{7,8})-[0-9Kk](?!\w)',
                    r'(?<!\w)(?:19|20)\d{2}[1-5][A-Z]{2,12}\d{3,}(?!\w)']:
        if re.search(pattern, clean):
            raise ValueError('Posible identificador en propuesta; no escribir salida')
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(blob)
    if table_path.read_bytes() != table_raw:
        raise ValueError('La tabla cambió durante la lectura')
    print(json.dumps({'propuesta': str(dest), 'codigos': 43, 'tabla_modificada': False}))


if __name__ == '__main__':
    main()
