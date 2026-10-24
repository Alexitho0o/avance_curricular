"""Contratos de ubicación y ejecución del repositorio único."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class UnificacionTests(unittest.TestCase):
    def test_recursos_funcionan_en_otra_ubicacion(self):
        """Una copia aislada no puede depender del antiguo repo ni de su ruta."""
        files = [
            'PROYECTO_IPSS.json', 'common/consulta_sies_historica.py',
            'procesos/caracterizacion/ubicacion_proyecto.py',
            'procesos/caracterizacion/common/consulta_sies_historica.py',
            'procesos/caracterizacion/caracterizacion_catalogo_sies_2027.py',
        ]
        for family, name in [('historico', 'ACTIVO_2007_2026.json'),
                             ('anual', 'ACTIVO_2027.json')]:
            prefix = 'gobernanza/sies/' + family + '/'
            descriptor = json.loads((ROOT / (prefix + name)).read_text())
            files.append(prefix + name)
            files.extend(prefix + meta['path'] for meta in descriptor['archivos'].values())
        with tempfile.TemporaryDirectory(dir=ROOT / 'data/unificacion_proyectos/20261015') as temporary:
            target = Path(temporary)
            for relative in files:
                destination = target / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, destination)
            probe = """import sys,json
sys.path.insert(0,sys.argv[1])
from common.consulta_sies_historica import ConsultaHistorica,DIRECTORY as HISTORICO
from caracterizacion_catalogo_sies_2027 import load_package,DIRECTORY as ANUAL
historico=ConsultaHistorica()
historico.consultar_sies(anio=2026,codigo_unico='I162S2C77J4V2')
catalogo,descriptor,resolver=load_package()
print(json.dumps({'historico':str(HISTORICO),'anual':str(ANUAL),'anio':catalogo['anio']}))
"""
            result = subprocess.run(
                [sys.executable, '-I', '-c', probe, str(target / 'procesos/caracterizacion')],
                cwd=target, capture_output=True, text=True, check=True)
            actual = json.loads(result.stdout)
            self.assertEqual(actual['anio'], 2027)
            for key in ('historico', 'anual'):
                self.assertTrue(Path(actual[key]).is_relative_to(target))

    def test_ejecutor_conserva_directorio_y_argumentos(self):
        literal = 'argumento con espacios; $HOME'
        probe = 'import os,sys,json;print(json.dumps([os.getcwd(),sys.argv[1]]))'
        result = subprocess.run(
            [sys.executable, str(ROOT / 'scripts/proceso_ipss.py'), 'caracterizacion',
             '--', sys.executable, '-c', probe, literal],
            cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout),
                         [str(ROOT / 'procesos/caracterizacion'), literal])

    def test_ejecutor_rechaza_modulo_no_registrado(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / 'scripts/proceso_ipss.py'), '../otro',
             '--', sys.executable, '-c', 'print("NO_EJECUTAR")'],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('NO_EJECUTAR', result.stdout)


if __name__ == '__main__':
    unittest.main()
