"""Compatibilidad de imports; la implementación H7 vive una sola vez en la raíz."""
from pathlib import Path as _Path
import importlib.util as _util
_root = _Path(__file__).resolve().parents[3]
if not (_root / 'PROYECTO_IPSS.json').is_file():
    raise ValueError('Falta el repositorio contenedor IPSS')
_spec = _util.spec_from_file_location('_ipss_consulta_historica_compartida', _root / 'common/consulta_sies_historica.py')
_runtime = _util.module_from_spec(_spec)
_spec.loader.exec_module(_runtime)
for _name in dir(_runtime):
    if not _name.startswith('_'):
        globals()[_name] = getattr(_runtime, _name)
