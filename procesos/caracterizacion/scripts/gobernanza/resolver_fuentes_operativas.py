"""Resolve period-specific operational inputs without running characterization."""
import argparse
import json
import os
from pathlib import Path
import re
import shlex
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from caracterizacion_archivos import validate_input_file

PROFILE = ROOT / 'docs/gobernanza/COMANDOS_OPERATIVOS.json'
SOURCE_VARS = ('RUTA_MATRICULA', 'RUTA_INSCRITOS', 'RUTA_RESULTADOS', 'RUTA_PROMEDIOS')
RESULT_SUFFIXES = {'.xlsx', '.xlsm'}


def survey_id(path, role):
    prefix = 'tokens_' if role == 'RUTA_INSCRITOS' else 'results-survey'
    match = re.match(re.escape(prefix) + r'(\d+)(?!\d)', Path(path).name, re.I)
    return match[1] if match else None


def latest(directory, prefix, suffixes):
    files = [p for p in directory.iterdir() if p.is_file() and p.name.startswith(prefix)
             and p.suffix.lower() in suffixes] if directory.is_dir() else []
    return max(files, key=lambda p: (p.stat().st_mtime_ns, p.name)) if files else None


def resolve_sources(directory, *, expected_survey=None, environ=None, require_promedios=True, allow_empty_results=False):
    environ = os.environ if environ is None else environ
    directory = Path(directory).expanduser()
    sources = {var: Path(environ[var]).expanduser() for var in SOURCE_VARS if environ.get(var, '').strip()}
    for var, prefix in [('RUTA_MATRICULA', 'DATOSDEALUMNOS_'), ('RUTA_PROMEDIOS', 'PROMEDIOSDEALUMNOS_')]:
        if var not in sources:
            candidate = latest(directory, prefix, {'.xlsx', '.xls', '.csv'})
            if candidate:
                sources[var] = candidate
    selected_ids = {survey_id(sources[var], var) for var in ('RUTA_INSCRITOS', 'RUTA_RESULTADOS') if var in sources}
    if None in selected_ids or len(selected_ids) > 1:
        raise ValueError('Tokens y resultados deben identificar la misma encuesta en sus nombres.')
    wanted = expected_survey or next(iter(selected_ids), None)
    if expected_survey and selected_ids and selected_ids != {expected_survey}:
        raise ValueError(f'La encuesta requerida es {expected_survey}; hay una ruta explicita de otra encuesta.')
    if wanted is None:
        token_ids = {survey_id(p, 'RUTA_INSCRITOS') for p in directory.glob('tokens_*.csv')}
        result_ids = {survey_id(p, 'RUTA_RESULTADOS') for p in directory.glob('results-survey*') if p.suffix.lower() in RESULT_SUFFIXES}
        pairs = (token_ids & result_ids) - {None}
        if len(pairs) != 1:
            raise ValueError(f'{directory}: se requiere una pareja tokens/resultados de una sola encuesta; encontradas {len(pairs)}.')
        wanted = next(iter(pairs))
    for var, prefix, suffixes in [('RUTA_INSCRITOS', 'tokens_', {'.csv'}),
                                  ('RUTA_RESULTADOS', 'results-survey', RESULT_SUFFIXES)]:
        if var not in sources:
            candidates = [p for p in directory.glob(prefix + '*') if p.is_file()
                          and p.suffix.lower() in suffixes and survey_id(p, var) == wanted]
            if candidates:
                sources[var] = max(candidates, key=lambda p: (p.stat().st_mtime_ns, p.name))
    required = SOURCE_VARS if require_promedios else SOURCE_VARS[:3]
    missing = [var for var in required if var not in sources]
    if missing:
        raise ValueError(f'{directory}: faltan {", ".join(missing)}; encuesta requerida {wanted}.')
    for var, file in sources.items():
        if not file.is_file():
            raise ValueError(f'{var}: archivo no encontrado: {file}')
        if var in ('RUTA_INSCRITOS', 'RUTA_RESULTADOS') and survey_id(file, var) != wanted:
            raise ValueError(f'{var}: encuesta incompatible con {wanted}.')
        allowed = {'.csv'} if var == 'RUTA_INSCRITOS' else RESULT_SUFFIXES if var == 'RUTA_RESULTADOS' else {'.xlsx', '.xls', '.csv'}
        if file.suffix.lower() not in allowed:
            raise ValueError(f'{var}: tipo de archivo no admitido: {file.suffix}')
        if not (allow_empty_results and var == 'RUTA_RESULTADOS' and file.stat().st_size == 0):
            validate_input_file(file)
    return wanted, {var: str(file.resolve()) for var, file in sources.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--anio', type=int, required=True)
    parser.add_argument('--periodo', type=int, required=True)
    args = parser.parse_args()
    profile = json.loads(PROFILE.read_text())['financiamiento']
    if (args.anio, args.periodo) != (profile['anio'], profile['periodo']):
        parser.error('Este perfil corresponde exclusivamente a financiamiento 2027 P1.')
    directory = os.environ.get('CARACTERIZACION_INPUT_DIR', str(Path.home() / 'Downloads'))
    try:
        selected, sources = resolve_sources(directory, expected_survey=profile['survey_id'], require_promedios=False,
                                           allow_empty_results=profile.get('allow_response_free_operations', False))
        print(f'[FUENTES] Perfil: {args.anio} P{args.periodo}; encuesta: {selected}')
        for var, file in sources.items():
            print(f'[FUENTES] {var}: {Path(file).name}')
        results = Path(sources['RUTA_RESULTADOS'])
        empty_results = results.stat().st_size == 0
        if not empty_results and profile.get('allow_response_free_operations'):
            from caracterizacion_limesurvey import read_input_frame
            empty_results = read_input_frame(results).empty
        if empty_results:
            if not profile.get('allow_response_free_operations'):
                raise ValueError('Los resultados estan vacios y no hay un modo sin respuestas autorizado.')
            from caracterizacion_limesurvey import inspect_tokens_file, read_input_frame
            from caracterizacion_sin_respuestas import validate_no_responses
            inspect_tokens_file(sources['RUTA_INSCRITOS'])
            validate_no_responses(read_input_frame(sources['RUTA_INSCRITOS']))
        else:
            from caracterizacion_incorporacion import build_plan
            from caracterizacion_sin_respuestas import shared_operational_rules
            from caracterizacion_limesurvey import read_input_frame
            from caracterizacion_runtime import now_scl
            plan = build_plan(read_input_frame(sources['RUTA_MATRICULA']), read_input_frame(sources['RUTA_INSCRITOS']),
                              args.anio, args.periodo, now_scl().date(), shared_operational_rules())
            print(f'[CORREOS] elegibles={len(plan.eligible)}; con token={plan.counts["VIGENTES_CON_TOKEN"]}; '
                  f'por incorporar={len(plan.missing)}; correos validos={len(plan.ready)}; '
                  f'pendientes de correo={len(plan.pending_email)}')
            print(f'[MULTIMATRICULA] personas={len(plan.eligible)}; matriculas={plan.counts["MATRICULAS_ELEGIBLES"]}; '
                  f'RUT con varias matriculas={plan.counts["RUT_MULTIMATRICULA"]}. '
                  'Se conservan en seguimiento; no bloquean la ejecucion.')
            if not plan.pending_email.empty:
                print('[CORREOS][ADVERTENCIA] Los casos sin Mail_Inst valido quedan en seguimiento; la ejecucion continua.')
    except ValueError as error:
        print(f'[FUENTES][BLOQUEO] {error}')
        return 3
    for var, file in sources.items():
        print(f'export {var}={shlex.quote(file)}')
    print(f'export CARACTERIZACION_RESULTADOS_SIN_RESPUESTAS={int(empty_results)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
