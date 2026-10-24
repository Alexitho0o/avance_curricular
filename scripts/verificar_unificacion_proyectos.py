#!/usr/bin/env python3
"""Comprueba incorporación, fuentes comunes y paridad sin ejecutar pipelines."""
from pathlib import Path
import csv
import hashlib
import importlib.util
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / 'procesos/caracterizacion'
OUT = ROOT / 'data/unificacion_proyectos/20261015'
sys.path.insert(0, str(ROOT))
from common.consulta_sies_historica import ConsultaHistorica

EXPECTED_CHANGES = {'.gitignore', 'AGENTS.md', 'common/consulta_sies_historica.py',
                    'caracterizacion_catalogo_sies_2027.py', 'scripts/enriquecer_analisis_anual.py'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    imported = json.loads((OUT / 'importacion.json').read_text())
    changed = []; missing = []; same = 0
    for relative, old in imported['files'].items():
        p = MODULE / relative
        if not p.is_file():
            missing.append(relative)
        elif sha(p) == old['sha256']:
            same += 1
        else:
            changed.append({'path': relative, 'antes': old['sha256'], 'despues': sha(p)})
    unexpected = sorted({r['path'] for r in changed} - EXPECTED_CHANGES)
    if missing or unexpected:
        raise ValueError(f'Pérdida/cambio no justificado: {missing}, {unexpected}')
    raw = ('\0'.join('procesos/caracterizacion/' + p for p in imported['files']) + '\0').encode()
    ignored = subprocess.run(['git', 'check-ignore', '--no-index', '--stdin', '-z'], cwd=ROOT,
                             input=raw, capture_output=True).stdout.decode().split('\0')
    ignored = [x for x in ignored if x]
    if ignored:
        raise ValueError('Archivos incorporados ignorados por Git: ' + str(ignored))
    spec = importlib.util.spec_from_file_location('cliente_modulo_integrado', MODULE/'common/consulta_sies_historica.py')
    runtime = importlib.util.module_from_spec(spec); spec.loader.exec_module(runtime)
    a, b = ConsultaHistorica(), runtime.ConsultaHistorica()
    assert runtime.DIRECTORY == ROOT/'gobernanza/sies/historico'
    assert a.trazabilidad() == b.trazabilidad()
    totals = {}; responses = hashlib.sha256()
    h6 = ROOT/'data/versiones_historicas_sies_umas/fase_6_20261015'
    for kind, file in [('UMAS', 'consultas_umas.tsv'), ('SIES', 'consultas_sies_anuales.tsv')]:
        count = 0
        with (h6/file).open(newline='') as stream:
            for row in csv.DictReader(stream, delimiter='\t'):
                params = {'anio': int(row['anio'])}
                if kind == 'UMAS':
                    params.update({k: row[k] for k in ('periodo','regimen','codcarpr','nombre_interno','plan_umas','sede_umas','jornada_umas')})
                    left, right = a.consultar_umas(**params), b.consultar_umas(**params)
                else:
                    params['codigo_unico'] = row['codigo_unico']
                    left, right = a.consultar_sies(**params), b.consultar_sies(**params)
                if left != right:
                    raise ValueError('La unificación altera una consulta: ' + str(params))
                responses.update(json.dumps(left, sort_keys=True, ensure_ascii=False).encode()); count += 1
        totals[kind] = count
    frozen = subprocess.run([sys.executable,'scripts/gobernanza/verificar_separacion_fcu.py'],
                            cwd=MODULE, capture_output=True, text=True, check=True)
    frozen = json.loads(frozen.stdout)
    probe = """import sys,json
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from caracterizacion_catalogo_sies_2027 import DIRECTORY,load_package
from scripts.enriquecer_analisis_anual import load_resources,verified_resource
c,d,r=load_package();p,c26,i=load_resources()
print(json.dumps({'anual2027':str(DIRECTORY),'anual2026':str(verified_resource(p['catalogo'])),'codigos2027':len(c['oferta']),'anio2026':c26['anio']}))
"""
    shared = json.loads(subprocess.run([sys.executable,'-I','-c',probe,str(MODULE)],
                       cwd=ROOT, capture_output=True, text=True, check=True).stdout)
    assert shared['anual2027'] == str(ROOT/'gobernanza/sies/anual')
    assert shared['anual2026'] == str(ROOT/'data/catalogos_sies/2026/mu2026_20261013/catalogo.json')
    result = {'estado':'VERIFICADO_SIN_PIPELINES_REALES', 'archivos_incorporados':len(imported['files']),
              'archivos_identicos':same, 'cambios_integracion':changed, 'archivos_faltantes':missing,
              'archivos_incorporados_ignorados_git':ignored, 'consultas_iguales':totals,
              'huella_respuestas':responses.hexdigest(), 'referencias_congeladas_fcu':frozen,
              'recursos_comunes':shared, 'historico_compartido':str(runtime.DIRECTORY.relative_to(ROOT)),
              'pipeline_real_ejecutado':False,'historia_git_fusionada':False,'publicado_remoto':False}
    (OUT/'qa_integracion.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('cambios_integracion','recursos_comunes')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
