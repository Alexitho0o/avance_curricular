#!/usr/bin/env python3
"""Construye o consulta propuestas de versión sin rehacer el puente de carreras."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.versiones_por_cohorte import clave_grupo, resolver_cohorte

OUT = ROOT / 'data/versiones_por_cohorte/20261016'
BASE = 'data/diccionario_sies_umas/20261015/evidencia/'
TIPOS = {'Plan Regular': '1', 'Plan Especial': '2', 'Plan Regular de Continuidad': '3'}


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def construir():
    inputs = {}
    def read(name, expected=None):
        raw = (ROOT / name).read_bytes()
        if expected and sha(raw) != expected:
            raise ValueError('Fuente alterada: ' + name)
        inputs[name] = sha(raw)
        return raw
    master = json.loads(read('data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json',
                            '2ef459251e91ecebe5370402e3d2ea25341aeecbfb3ca54eca210cc347c392a5'))
    alumnado = json.loads(read(BASE + 'ejemplos_umas.json'))
    previous = json.loads(read(BASE + 'caracterizacion_reglas_y_fuentes.json'))
    duracion = list(csv.DictReader(io.StringIO(read('DURACION_ESTUDIOS.tsv',
                               master['fuentes']['duracion']['sha256']).decode()), delimiter='\t'))
    b = 'data/versiones_historicas_sies_umas/fase_b_20261015/'
    bm = json.loads(read(b + 'manifest.json'))
    offer = json.loads(read(b + 'perfiles_sies_anuales.json', bm['salidas']['perfiles_sies_anuales.json']))
    by_code = defaultdict(list)
    for number, row in enumerate(duracion, 2):
        by_code[row['CODIGO_UNICO']].append((number, row))
    groups = {}
    for row in master['equivalencias_programa_2026']:
        key = clave_grupo(row['codcarpr'], row['sede_umas'], row['jornada_umas'])
        g = groups.setdefault(key, {'clave': key, 'codcarpr': row['codcarpr'], 'sede': row['sede_umas'],
                                   'jornada': row['jornada_umas'], 'equivalencias_h5': [],
                                   'codigos_base': set(), 'familias': set()})
        g['equivalencias_h5'].append(row['id'])
        g['codigos_base'].add(row['codigo_unico'])
        g['familias'].add(row['codigo_unico'].rsplit('V', 1)[0])
    manual = defaultdict(list)
    for row in previous['equivalencias_manual_fcu2026']['filas']:
        manual[clave_grupo(row['CODCARPR'], row['SEDE'], row['JORNADA'])].append(row['CODIGO_UNICO_SIES'])
    for key, g in groups.items():
        evidence = []
        method = 'MANUAL_FCU2026' if key in manual else 'CODCARPR_CANONICO'
        codes = manual.get(key, g['codigos_base'])
        for code in sorted(codes):
            for number, row in by_code[code]:
                if key in manual or row['CODCARPR_CANONICO'] == g['codcarpr']:
                    evidence.append({'codigo_unico': code, 'fila_duracion': number,
                                     'duracion_total': row['DURACION_TOTAL'], 'tipo_plan': row['TIPO_PLAN_CARRERA']})
        if not evidence:
            all_rows = [(number, row) for code in g['codigos_base'] for number, row in by_code[code]]
            profiles = {(r['DURACION_TOTAL'], r['TIPO_PLAN_CARRERA']) for _, r in all_rows}
            if len(profiles) == 1:
                method = 'PERFIL_UNANIME_GRUPO_EXISTENTE'
                evidence = [{'codigo_unico': row['CODIGO_UNICO'], 'fila_duracion': number,
                             'duracion_total': row['DURACION_TOTAL'], 'tipo_plan': row['TIPO_PLAN_CARRERA']}
                            for number, row in sorted(all_rows, key=lambda x: x[0])]
            else:
                method = 'PERFIL_NO_UNIVOCO'
        g['perfiles_duracion_tipo'] = sorted({(r['duracion_total'], r['tipo_plan']) for r in evidence
                                             if r['duracion_total'] and r['tipo_plan']})
        g['fuente_perfil'] = method
        g['evidencia_perfil'] = evidence
        g['codigos_base'] = sorted(g['codigos_base'])
        g['familias'] = sorted(g['familias'])
        g['equivalencias_h5'].sort()
    histories = {}
    for row in sorted(offer, key=lambda r: (r['codigo_unico'], r['anio'])):
        code = row['codigo_unico']; raw = row['campos_originales']
        h = histories.setdefault(code, {'codigo_unico': code, 'familia': code.rsplit('V', 1)[0],
                                        'inicio_oferta': row['anio'], 'anual': []})
        h['anual'].append({'anio': row['anio'], 'duracion_total': raw['Duración Total'],
                          'tipo_plan': TIPOS.get(raw['Tipo Carrera']), 'nombre_sies': raw['Nombre Carrera'],
                          'modalidad': raw['Modalidad'], 'registro_csv': row['registro_csv']})
    histories = [histories[k] for k in sorted(histories)]
    mrun = {(int(r['cat_periodo']), r['codigo_unico']) for r in master['mrun_anual']}
    results = []
    for number, row in enumerate(alumnado['combinaciones_unicas'], 1):
        key = clave_grupo(row['CODCARPR'], row['SEDE'], row['JORNADA'])
        raw_year = str(row['ANOINGRESO'])
        year = int(raw_year) if raw_year.isdigit() else None
        resolution = resolver_cohorte(groups.get(key), histories, anoingreso=year)
        results.append({'combinacion_fuente': number, 'fila_datosalumnos': row['fila_fuente'],
                        'clave_grupo': key, 'datos_alumnos': {k:row[k] for k in (
                            'CODCARPR', 'NOMBRE_L', 'SEDE', 'JORNADA', 'ANOMATRICULA', 'ANOINGRESO', 'PERIODOINGRESO')},
                        'resolucion': resolution,
                        'mrun_codigo_en_anio_ingreso': ((year, resolution['codigo_propuesto']) in mrun)
                        if resolution['codigo_propuesto'] else None})
    coverage = []
    for code in sorted(r['codigo_unico'] for r in master['universo_sies']):
        linked = [g['clave'] for g in groups.values() if code.rsplit('V', 1)[0] in g['familias']]
        coverage.append({'codigo_unico': code, 'grupos_existentes': sorted(linked),
                         'estado': 'EN_FAMILIA_EXISTENTE' if linked else 'SIN_GRUPO_PREVIO',
                         'combinaciones_propuestas': [r['combinacion_fuente'] for r in results
                                                      if r['resolucion']['codigo_propuesto'] == code]})
    summary = {'fecha': '2026-10-16', 'equivalencias_previas_preservadas': len(master['equivalencias_programa_2026']),
               'grupos_existentes': len(groups), 'perfiles_por_fuente': dict(Counter(g['fuente_perfil'] for g in groups.values())),
               'combinaciones_datosalumnos': len(results), 'codigos_sies_preservados': len(coverage),
               'estados': dict(Counter(r['resolucion']['estado'] for r in results)),
               'registros_personales_exportados': False, 'motor_oficial_modificado': False,
               'criterio_anoingreso': 'Cohorte de carrera de DatosAlumnos; no año de matrícula ni de notas',
               'nombre_es_filtro': False, 'intervalo_es_hipotesis_explicita': True,
               'fuente_datosalumnos': alumnado['fuente']}
    outputs = {'grupos_existentes.json': sorted(groups.values(), key=lambda g:g['clave']),
               'historias_oferta.json': histories, 'resultados_cohortes.json': results,
               'cobertura_codigos.json': coverage, 'resumen.json': summary}
    for file in ('common/versiones_por_cohorte.py','scripts/versiones_por_cohorte.py',
                 'docs/versiones_por_cohorte_20261016.md'):
        read(file)
    for name, digest in inputs.items():
        if sha((ROOT / name).read_bytes()) != digest:
            raise ValueError('Fuente cambió durante ejecución: ' + name)
    outputs['manifest.json'] = {'entradas': inputs, 'salidas': {k:sha(encode(v)) for k,v in outputs.items()},
                                'regla_interna': 'COHORTE_OFERTA_DURACION_20261016',
                                'equivalencia_malla_individual_acreditada': False}
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verificar', action='store_true')
    parser.add_argument('--codcarpr'); parser.add_argument('--sede'); parser.add_argument('--jornada')
    parser.add_argument('--anoingreso', type=int)
    args = parser.parse_args()
    if any(x is not None for x in (args.codcarpr,args.sede,args.jornada,args.anoingreso)):
        if not all(x is not None for x in (args.codcarpr,args.sede,args.jornada,args.anoingreso)):
            parser.error('Consulta requiere CODCARPR, sede, jornada y ANOINGRESO')
        manifest = json.loads((OUT/'manifest.json').read_text())
        data = {}
        for file in ('grupos_existentes.json','historias_oferta.json'):
            raw = (OUT/file).read_bytes()
            if sha(raw) != manifest['salidas'][file]:
                raise ValueError('Paquete de consulta alterado')
            data[file] = json.loads(raw)
        key = clave_grupo(args.codcarpr,args.sede,args.jornada)
        group = next((g for g in data['grupos_existentes.json'] if g['clave']==key),None)
        result = resolver_cohorte(group,data['historias_oferta.json'],anoingreso=args.anoingreso)
        print(json.dumps(result,ensure_ascii=False,indent=2)); return
    outputs = construir()
    for name,value in outputs.items():
        path = OUT/name
        if path.exists() and path.read_bytes()!=encode(value):
            raise ValueError('Salida distinta; generar una nueva edición: '+name)
        if args.verificar and not path.exists():
            raise ValueError('Falta salida: '+name)
    if not args.verificar:
        OUT.mkdir(parents=True,exist_ok=True)
        for name,value in outputs.items(): (OUT/name).write_bytes(encode(value))
    print(json.dumps({k:v for k,v in outputs['resumen.json'].items() if k!='fuente_datosalumnos'},ensure_ascii=False))


if __name__=='__main__':
    main()
