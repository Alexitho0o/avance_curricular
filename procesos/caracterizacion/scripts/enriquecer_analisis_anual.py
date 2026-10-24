"""Read-only enrichment of annual inputs, independent of the frozen FCU engine."""
import hashlib
import json
from pathlib import Path
import re
import unicodedata

import pandas as pd
from ubicacion_proyecto import recurso_comun

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / 'gobernanza/analisis_anual/2026/v2/politica.json'
QUESTION = re.compile(r'^((?:G\d+Q\d+|Q\d+)(?:\[[^\]]+\])*)(?:\.\s*|\s+|$)')
MODES = {'1': 'Presencial', '2': 'Semipresencial', '3': 'No presencial'}


def norm(value):
    if value is None or pd.isna(value):
        return ''
    value = unicodedata.normalize('NFKD', str(value).strip().upper())
    return ' '.join(''.join(c for c in value if not unicodedata.combining(c)).split())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verified_resource(metadata):
    if metadata['path'] == 'gobernanza/analisis_anual/2026/v2/catalogo_sies.json':
        path = recurso_comun('catalogo_sies_2026')
        if digest(path) != metadata['sha256']:
            raise ValueError('Fuente anual gobernada alterada: catálogo común 2026')
        return path
    path = (ROOT / metadata['path']).resolve()
    if not path.is_relative_to(ROOT.resolve()) or digest(path) != metadata['sha256']:
        raise ValueError(f'Fuente anual gobernada alterada: {metadata["path"]}')
    return path


def load_resources():
    policy = json.loads(POLICY_PATH.read_text(encoding='utf-8'))
    catalog_path = verified_resource(policy['catalogo'])
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    inventory_path = verified_resource(policy['instrumento'])
    if policy['anio'] != 2026 or catalog['anio'] != 2026:
        raise ValueError('El enriquecimiento anual exige fuentes 2026.')
    if len({r['codigo_unico'] for r in catalog['oferta']}) != len(catalog['oferta']):
        raise ValueError('Catalogo anual con codigos duplicados.')
    return policy, catalog, inventory_path


def question_signature(headers):
    pairs = []
    for header in headers:
        match = QUESTION.match(str(header))
        if match:
            pairs.append([match.group(1), str(header)[match.end():].strip()])
    encoded = json.dumps(sorted(pairs), ensure_ascii=False, separators=(',', ':')).encode()
    return len(pairs), hashlib.sha256(encoded).hexdigest()


def shared_inventory(entry, headers, policy, inventory_path):
    if entry['anio'] != policy['anio'] or str(entry['survey_id']) != policy['encuestas'].get(str(entry['periodo'])):
        raise ValueError('Encuesta fuera del instrumento comun autorizado 2026.')
    validate_headers(headers, policy)
    instrument = json.loads(Path(inventory_path).read_text(encoding='utf-8'))['instrument']
    if str(instrument['survey_id']) != policy['encuestas']['2']:
        raise ValueError('Inventario de referencia distinto de 2026 P2.')
    return {q['code']: {**q, 'group': group['text']}
            for group in instrument['groups'] for q in group['questions']}


def validate_headers(headers, policy):
    metadata = policy['instrumento']
    if 'columnas_path' not in metadata:
        valid = question_signature(headers) == (metadata['columnas'], metadata['encabezados_sha256'])
    else:
        path = (ROOT / metadata['columnas_path']).resolve()
        if not path.is_relative_to(ROOT.resolve()):
            raise ValueError('Referencia de columnas fuera del repositorio.')
        expected = json.loads(path.read_text(encoding='utf-8'))
        digest_expected = hashlib.sha256(json.dumps(sorted(expected), ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
        if len(expected) != metadata['columnas'] or digest_expected != metadata['encabezados_sha256']:
            raise ValueError('Referencia de columnas alterada.')
        expected = dict(expected)
        pairs = []
        for header in headers:
            match = QUESTION.match(str(header))
            if match:
                pairs.append((match.group(1), str(header)[match.end():].strip()))
        valid = (len(pairs) == len(expected) and {code for code, _ in pairs} == set(expected)
                 and all(not label or label == expected[code] for code, label in pairs))
    if not valid:
        raise ValueError('Cambio el instrumento 2026: revisar codigos/textos antes de homologar los periodos.')


def resolve_modality(row, catalog):
    code, sede, jornada = (norm(row.get(k)) for k in ('CODCARPR', 'SEDE', 'JORNADA'))
    sede = catalog['sedes_internas'].get(sede, sede)
    jornada = {'D': '1', 'V': '2', 'O': '4'}.get(jornada, jornada)
    if not all((code, sede, jornada)):
        return 'No determinada', 'DATOS_INSUFICIENTES', [], 'DATOS_INSUFICIENTES'
    candidates = [r for r in catalog['oferta'] if r['sede'] == sede and r['jornada'] == jornada
                  and any(norm(a['codcarpr']) == code for a in r['equivalencias'])]
    codes = sorted(r['codigo_unico'] for r in candidates)
    status = 'RESUELTO' if len(codes) == 1 else 'AMBIGUO' if codes else 'SIN_EQUIVALENCIA'
    for candidate in candidates:
        if MODES.get(candidate['modalidad_codigo']) != candidate['modalidad']:
            raise ValueError('Modalidad contradictoria en catalogo anual.')
    modes = {r['modalidad'] for r in candidates}
    if len(modes) == 1:
        return modes.pop(), status, codes, 'CODIGO_UNICO' if len(codes) == 1 else 'COINCIDENCIA_CANDIDATOS'
    return 'No determinada', status, codes, 'MODALIDADES_DIFERENTES' if modes else 'SIN_EQUIVALENCIA'


def apply_modality_policy(row, catalog_result, policy):
    mode, status, codes, rule = catalog_result
    override = policy.get('modalidad_por_jornada', {}).get(norm(row.get('JORNADA')))
    if override:
        if override not in MODES.values():
            raise ValueError('Modalidad institucional no reconocida.')
        return override, status, codes, 'REGLA_INSTITUCIONAL_JORNADA_V'
    return mode, status, codes, rule


def academic_metrics(grades, policy):
    """One observation per documented course attempt, never average semester averages."""
    keys = ['CODCLI', 'CODCARR', 'ANO', 'PERIODO', 'CODRAMO', 'CODSECC']
    required = keys + ['NOTA_FINAL', 'DESCRIPCION_ESTADO', 'CONVALIDADO']
    if missing := set(required) - set(grades):
        raise ValueError(f'Fuente de notas sin columnas requeridas: {sorted(missing)}')
    data = grades[required].copy()
    for column in keys + ['DESCRIPCION_ESTADO', 'CONVALIDADO']:
        data[column] = data[column].map(norm)
    year = pd.to_numeric(data['ANO'], errors='coerce')
    period = pd.to_numeric(data['PERIODO'], errors='coerce')
    rules = policy['notas']
    in_scope = year.eq(rules['anio']) & period.isin(rules['periodos'])
    quality = [['Filas fuente', len(data)], ['Fuera del ano/periodos academicos', int((~in_scope).sum())]]
    data = data[in_scope].copy()
    data['NOTA_FINAL'] = pd.to_numeric(data['NOTA_FINAL'].astype(str).str.replace(',', '.', regex=False), errors='coerce')
    # Normalize numeric year/period keys before testing duplicate attempts.
    data['ANO'] = year[in_scope].astype(int).astype(str)
    data['PERIODO'] = period[in_scope].astype(int).astype(str)
    duplicate = data.duplicated(subset=required)
    quality.append(['Duplicados exactos colapsados', int(duplicate.sum())])
    data = data[~duplicate].copy()
    conflict = data.duplicated(subset=keys, keep=False)
    quality.append(['Filas de intentos contradictorios excluidas', int(conflict.sum())])
    data = data[~conflict].copy()
    transfer = data['DESCRIPCION_ESTADO'].str.contains('CONVALID|HOMOLOG|RECONOC|EQUIV', regex=True)
    transfer |= data['CONVALIDADO'].isin({'S', 'SI', 'Y', 'YES', '1', 'TRUE'})
    valid = (data['NOTA_FINAL'].between(rules['minimo'], rules['maximo']) & ~transfer
             & data['DESCRIPCION_ESTADO'].isin(rules['estados'])
             & data[keys].ne('').all(axis=1))
    quality.append(['Notas sin valor valido, sin clave, transferidas o sin estado final', int((~valid).sum())])
    data = data[valid].copy()
    quality.append(['Notas finales incluidas', len(data)])
    coverage = sorted(data['PERIODO'].unique())
    metrics = {}
    for key, group in data.groupby(['CODCLI', 'CODCARR'], sort=True):
        metrics[key] = {'mean': float(group['NOTA_FINAL'].mean()), 'n': len(group),
                        'periods': ', '.join(sorted(group['PERIODO'].unique()))}
    return metrics, quality, coverage


def enrich_base(base, entry, catalog, policy, metrics):
    if entry['anio'] != 2026:
        raise ValueError('No aplicar enriquecimiento anual 2026 a otro ano.')
    if missing := {'CODCLI', 'CODCARPR', 'SEDE', 'JORNADA', 'CARRERA', 'SECTOR_ACADEMICO'} - set(base):
        raise ValueError(f'Base anual sin claves de enriquecimiento: {sorted(missing)}')
    output = base.copy(deep=True)
    # Excel readers can return string-typed columns; calculated grades are numeric.
    output['PROMEDIO_AC_REFERENCIA'] = pd.to_numeric(output.get('PROMEDIO_AC_REFERENCIA'), errors='coerce')
    audit = []
    for index, row in output.iterrows():
        sector = row['SECTOR_ACADEMICO']
        for alias in policy['sectores']:
            if norm(row['CODCARPR']) == alias['codigo'] and norm(row['CARRERA']) == alias['nombre']:
                if norm(sector) not in {'', 'SIN CLASIFICAR', norm(alias['sector'])}:
                    raise ValueError('Sector previo contradice equivalencia anual autorizada.')
                sector = alias['sector']
        catalog_result = resolve_modality(row, catalog)
        mode, code_status, codes, mode_status = apply_modality_policy(row, catalog_result, policy)
        grade = metrics.get((norm(row['CODCLI']), norm(row['CODCARPR'])))
        previous = pd.to_numeric(row.get('PROMEDIO_AC_REFERENCIA'), errors='coerce')
        output.at[index, 'SECTOR_ACADEMICO'] = sector
        output.at[index, 'MODALIDAD_CARRERA'] = mode
        output.at[index, 'FUENTE_MODALIDAD_ANUAL'] = (
            f'{policy["revision"]}: {mode_status}' if mode_status.startswith('REGLA_INSTITUCIONAL')
            else f'{catalog["version"]}: {mode_status}')
        output.at[index, 'PROMEDIO_AC_REFERENCIA'] = grade['mean'] if grade else None
        audit.append([f'P{entry["periodo"]}', norm(row['CODCLI']), norm(row['CODCARPR']),
                      row['SECTOR_ACADEMICO'], sector, mode, code_status, ', '.join(codes), mode_status,
                      None if pd.isna(previous) else float(previous), grade['mean'] if grade else None,
                      grade['n'] if grade else 0, grade['periods'] if grade else '',
                      'CON_NOTAS_VALIDAS_2026' if grade else 'SIN_NOTAS_VALIDAS_2026_PARA_MATRICULA',
                      catalog_result[0], catalog_result[3],
                      'SI' if mode != catalog_result[0] and catalog_result[0] != 'No determinada' else 'NO'])
    return output, audit
