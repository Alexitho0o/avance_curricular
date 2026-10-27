"""Busca etiquetas técnicas en respaldos de SIES sin extraer datos individuales."""
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados')
assert ROOT.is_dir()
globs = ['*.py', '*.js', '*.mjs', '*.sql', '*.ipynb', '*.md', '*.txt']
pattern = 'TRACE_SCORE_CANDIDATO|TRACE_REASONS_CANDIDATO|Res_Tit_Unificada|FAMILIA POR NOMBRE_TITULO|SEM_INGRESO_ACTUAL cercano'
def search(pattern):
    command = ['rg', '--stats', '-i', '--hidden']
    for glob in globs: command += ['-g', glob]
    command += [pattern, str(ROOT)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=45)
    assert result.returncode in (0, 1), result.stderr
    # Las líneas de coincidencia podrían contener información personal: no se exportan.
    lines = result.stdout.splitlines()
    stats = [line for line in lines if any(line.endswith(suffix) for suffix in
             [' matches', ' matched lines', ' files contained matches', ' files searched', ' bytes searched'])]
    return {'patron': pattern, 'exit_code': result.returncode, 'estadisticas': stats,
            'errores': bool(result.stderr), 'contenido_coincidente_exportado': False}

out = {'clasificacion': 'C búsqueda literal; E ausencia fuera de alcance', 'raiz': str(ROOT),
       'extensiones': globs, 'busquedas': [search(pattern), search(r'\b2130\b')],
       'limitaciones': 'No inspecciona Excel, PDF, binarios, archivos comprimidos ni rutas externas a esta raíz. No prueba ausencia de algoritmo con otro nombre o fuera del alcance.'}
(OUT / 'RESULTADO_AGREGADO.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(out, ensure_ascii=False))
