import os
import subprocess
from pathlib import Path

ROOT = Path("/Users/alexi/Documents/GitHub/CARACTERIZACIÓN")

env = os.environ.copy()
env.update({
    "ANIO_ANALISIS": "2026",
    "PERIODO_ANALISIS": "1",
    "VERBOSIDAD": "2",
    "COHORTES_ANALISIS": "2026",
    "SOLO_GENERAR_FCU": "1",
})

subprocess.run(
    ["python3", "caracterizacion.py"],
    cwd=ROOT,
    env=env,
    check=True,
)
