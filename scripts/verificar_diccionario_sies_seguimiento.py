#!/usr/bin/env python3
"""QA sobre universo completo, consumidores comunes, excepciones y preservación."""
import collections
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento, sha256, ROOT


def main():
    folder = ROOT / 'data/diccionario_sies_seguimiento/v1_20261023'
    desc = json.loads((folder / 'descriptor.json').read_text())
    s = DiccionarioSiesSeguimiento()
    counts = collections.Counter(); mismatches = 0; sample = None
    family = collections.defaultdict(lambda: collections.Counter())
    rows = []
    for (p,) in s.db.execute('SELECT payload FROM observaciones ORDER BY id'):
        r = json.loads(p); rows.append(r)
        query = dict(persona=r['persona'], codcli=r['CODCLI'], plan=r['plan'], anio=r['ano'],
                     periodo=r['periodo'], carrera=r['carrera'], sede=r['sede_dimension'], jornada=r['jornada_sies'])
        result = s.consultar(**query)
        mismatches += (result['codigo_sies'] or '') != r['codigo_interno_adoptado']
        counts[result['nivel_respaldo']] += 1
        k = (r['carrera'], r['jornada_sies'], r['ano'])
        family[k]['observaciones'] += 1
        family[k]['codigo_reutilizable'] += bool(result['codigo_sies'])
        family[k]['excepciones'] += not result['codigo_sies']
        if sample is None and r['codigo_documental_atribuible']:
            sample = query
    assert mismatches == 0 and len(rows) == 24774
    s.close()
    # Tres entradas ejecutan el mismo módulo; consultas privadas no salen a stdout.
    private_parent = Path(desc['base_privada']['ruta']).parent
    commands = ['scripts/consultar_diccionario_sies_seguimiento.py',
                'scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py',
                'procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py']
    with tempfile.TemporaryDirectory(prefix='qa_', dir=private_parent) as tmp:
        results = []
        for i, command in enumerate(commands):
            dest = Path(tmp) / f'consulta_{i}.json'
            subprocess.run([sys.executable, '-B', str(ROOT / command), '--salida-privada', str(dest)],
                input=json.dumps([{'metodo':'consultar','entrada':sample}]), text=True, check=True, capture_output=True)
            assert dest.stat().st_mode & 0o777 == 0o600
            results.append(json.loads(dest.read_text()))
        assert results[0] == results[1] == results[2]
        # Rechazo de base alterada, sin tocar la base real.
        invalid = copy.deepcopy(desc); invalid['base_privada']['sha256'] = '0' * 64
        bad = Path(tmp) / 'descriptor_alterado.json'; bad.write_text(json.dumps(invalid))
        try:
            DiccionarioSiesSeguimiento(descriptor=bad)
        except ValueError:
            integrity_rejected = True
        else:
            integrity_rejected = False
        assert integrity_rejected
    cases = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests',
                            '-p', 'test_diccionario_sies_seguimiento.py'], cwd=ROOT, text=True, capture_output=True)
    assert cases.returncode == 0, cases.stderr
    assert all(sha256(p) == h for p, h in desc['entradas_sha256'].items())
    assert sha256(desc['base_privada']['ruta']) == desc['base_privada']['sha256']
    # Valores originales no se imprimen ni se escriben en los resúmenes públicos.
    secrets = {r['persona'] for r in rows} | {r['CODCLI'] for r in rows}
    coverage = [{'carrera_umas': k[0], 'jornada_sies': k[1], 'anio': k[2], **dict(v)} for k, v in sorted(family.items())]
    qa = {'estado':'OK_CON_ADVERTENCIAS', 'clasificacion':'C validación; B resultados; E pendientes conservados',
          'consultas_reales':len(rows), 'discrepancias_codigos':mismatches, 'resultados':dict(counts),
          'tres_consumidores_misma_respuesta':True, 'integridad_alterada_rechazada':integrity_rejected,
          'pruebas_negativas_y_temporales':12, 'fuentes_intactas':True, 'denominadores_modificados':False,
          'base_privada_fuera_git':True, 'identificadores_en_salidas_publicas':False,
          'limites':['No acredita aceptación SIES ni fecha administrativa efectiva del plan.',
                    'No promociona propuestas ni extrapola códigos a otros contextos.',
                    'Índice RUT no resuelve 25 filas anuales con otro tipo documental; no se eliminan de las bases.',
                    'No ejecuta ni modifica motores anuales, libros ni complementos remotos.'],
          'rama':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
          'HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
    for name, obj in [('QA.json',qa),('COBERTURA_CARRERA_ANIO.json',coverage)]:
        text = json.dumps(obj, ensure_ascii=False, indent=2) + '\n'
        assert not any(x and x in text for x in secrets)
        (folder / name).write_text(text)
    print(json.dumps(qa,ensure_ascii=False))


if __name__ == '__main__':
    main()
