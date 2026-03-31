from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

from codigo import CARRERAS_AC_COLUMNS, MATRICULA_AC_COLUMNS, MATRICULA_UNIFICADA_COLUMNS


def check_readme_no_csv_dump() -> None:
    lines = Path('README.md').read_text(encoding='utf-8').splitlines()
    bad = [ln for ln in lines if ln.count(',') >= 8 and not ln.strip().startswith('`')]
    if bad:
        raise AssertionError(f'README parece contener dump CSV: {bad[:2]}')


def check_outputs() -> None:
    out = Path('resultados')
    mu = pd.read_csv(out/'matricula_unificada_2026_control.csv')
    ca = pd.read_csv(out/'carreras_avance_curricular_2025_control.csv')
    ma = pd.read_csv(out/'matricula_avance_curricular_2025_control.csv')
    assert mu.columns.tolist() == MATRICULA_UNIFICADA_COLUMNS
    assert ca.columns.tolist() == CARRERAS_AC_COLUMNS
    assert ma.columns.tolist() == MATRICULA_AC_COLUMNS

    rep = json.loads((out/'reporte_validacion.json').read_text(encoding='utf-8'))
    # No permitir apto si hay blockers
    blockers_mu = any(i['severity'] == 'BLOCKER' and i['area'] == 'matricula_unificada' for i in rep['issues'])
    if blockers_mu:
        assert rep['apto_oficial']['matricula_unificada'] is False

    quality = json.loads((out/'reporte_calidad_semantica.json').read_text(encoding='utf-8'))
    assert 'matricula_ac' in quality and 'carreras_ac' in quality and 'matricula_unificada' in quality


if __name__ == '__main__':
    check_readme_no_csv_dump()
    check_outputs()
    print('qa_checks_ok')
