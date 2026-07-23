"""Configuración de pytest: añadir rutas de importación."""

import sys
from pathlib import Path

# Añadir el directorio padre (procesos/ire_2026) al path
PROCESOS_DIR = Path(__file__).parent.parent
if str(PROCESOS_DIR) not in sys.path:
    sys.path.insert(0, str(PROCESOS_DIR))
