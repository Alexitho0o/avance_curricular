"""Run the complete 2026 analysis for P1, P2 and P3 after validating all inputs."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/gobernanza'))
from resolver_fuentes_operativas import PROFILE, SOURCE_VARS, latest, resolve_sources
from verificar_separacion_fcu import assert_frozen_reference


def verify_annual_instrument(headers):
    import enriquecer_analisis_anual as enrichment
    policy, _, _ = enrichment.load_resources()
    enrichment.validate_headers(headers, policy)


def validate_survey_sources(sources):
    from caracterizacion_limesurvey import LimeSurveySelectionError, select_latest_limesurvey_pair
    from consolidar_analisis_anual import question_column

    results = Path(sources['RUTA_RESULTADOS'])
    export_hint = ('Volver a exportar los resultados desde LimeSurvey en Excel con '
                   'encabezados "Codigo de pregunta y texto de pregunta", incluyendo id, '
                   'submitdate y token. No reconstruir codigos por posicion ni desde otro periodo.')
    try:
        pair = select_latest_limesurvey_pair(results.parent, tokens_path=sources['RUTA_INSCRITOS'],
                                            results_path=results)
    except LimeSurveySelectionError as error:
        detail = str(error)
        if 'sin columnas de respuesta/encuesta' in detail:
            detail += '. ' + export_hint
        raise ValueError(f'Validacion de contenido LimeSurvey: {detail}') from error
    headers = [column.lower().split('.')[0].strip() for column in pair.results.columns]
    missing = [name for name in ('id', 'submitdate', 'token') if headers.count(name) != 1]
    questions = sum(question_column(column) is not None for column in pair.results.columns)
    if missing or not questions:
        detail = ', '.join(missing + (['codigos de preguntas'] if not questions else []))
        raise ValueError(f'{results.name}: encabezados ausentes o ambiguos: {detail}. {export_hint}')
    if pair.evaluation.key_kind != 'token':
        raise ValueError(f'{results.name}: el anual requiere cruce por token, no por otra clave.')
    verify_annual_instrument(pair.results.columns)
    return {'tokens_rows': pair.tokens.rows, 'results_rows': pair.results.rows,
            'question_columns': questions, 'matched_tokens': pair.evaluation.coincidencias,
            'coverage_pct': pair.evaluation.cobertura_pct}


def build_plan(year, environ=None):
    environ = os.environ if environ is None else environ
    profile = json.loads(PROFILE.read_text())['analisis_anual']
    if year != profile['anio']:
        raise ValueError('Este comando anual esta gobernado para 2026 P1/P2/P3.')
    base = Path(environ.get('CARACTERIZACION_FUENTES_ANUAL') or Path.home() / profile['input_default']).expanduser()
    plan, errors = [], []
    for period in profile['periodos']:
        try:
            env = {var: environ.get(f'{var}_P{period}', '') for var in SOURCE_VARS}
            period_directory = environ.get(f'CARACTERIZACION_INPUT_DIR_P{period}')
            directory = Path(period_directory or base).expanduser()
            survey_directory = base / profile['survey_subdirectory']
            if not period_directory and survey_directory.exists():
                if not survey_directory.is_dir():
                    raise ValueError(f'La ruta de encuestas no es una carpeta: {survey_directory}')
                directory = survey_directory
                # Only surveys move into the dedicated folder; administrative sources stay at the root.
                for var, prefix in [('RUTA_MATRICULA', 'DATOSDEALUMNOS_'),
                                    ('RUTA_PROMEDIOS', 'PROMEDIOSDEALUMNOS_')]:
                    if not env[var].strip():
                        candidate = latest(base, prefix, {'.xlsx', '.xls', '.csv'})
                        if candidate is None:
                            raise ValueError(f'{base}: falta {var}; debe estar fuera de {survey_directory.name}.')
                        env[var] = str(candidate)
            expected_survey = profile['survey_ids'][str(period)]
            selected, sources = resolve_sources(directory, expected_survey=expected_survey, environ=env)
            validation = validate_survey_sources(sources)
            mode = profile['source_policy']
            plan.append({'anio': year, 'periodo': period, 'survey_id': selected, 'mode': mode,
                         'sources': sources, 'source_validation': validation})
        except (ValueError, OSError) as error:
            errors.append(f'P{period}: {error}')
    if errors:
        raise ValueError('\n'.join(errors))
    if len({entry['survey_id'] for entry in plan}) != len(plan):
        raise ValueError('Los periodos requieren encuestas independientes; se detecto una encuesta reutilizada.')
    return plan


def child_environment(entry, environ, run_dir):
    env = {key: value for key, value in environ.items() if key not in SOURCE_VARS}
    env.update(entry['sources'])
    env.update(ANIO_ANALISIS=str(entry['anio']), PERIODO_ANALISIS=str(entry['periodo']),
               COHORTES_ANALISIS=str(entry['anio']), VERBOSIDAD='1',
               CARACTERIZACION_EXCLUIR_DIPLOMADOS='1', CARACTERIZACION_EXCLUIR_SIN_FIRMA='1',
               CARACTERIZACION_FILTRAR_ANO_INGRESO='1', SOLO_GENERAR_FCU='0',
               CARACTERIZACION_SKIP_FCU='0', CARACTERIZACION_FAST_FCU_ONLY='0',
               CARACTERIZACION_STOP_AFTER_FINANCIAMIENTO='0', STOP_AFTER_FINANCIAMIENTO='0',
               CARACTERIZACION_STOP_AFTER_10BIS='0', CARACTERIZACION_RUN_DIR=str(run_dir),
               CARACTERIZACION_EXTERNAL_TEE='1', CARACTERIZACION_PYTHON=sys.executable.replace('\\', '/'),
               CARACTERIZACION_SECTORIZADO_AC_STRICT='1',
               CARACTERIZACION_DESKTOP_BASE=str(run_dir.parent / '_copias_periodos'),
               PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
    return env


def snapshot_sources(entry, run_dir):
    directory = run_dir / '01_ENTRADAS'
    directory.mkdir()
    if len({Path(file).name for file in entry['sources'].values()}) != len(entry['sources']):
        raise ValueError('Los roles de entrada tienen nombres repetidos y no pueden archivarse de forma independiente.')
    snapshots = {}
    for var, source in entry['sources'].items():
        target = directory / Path(source).name
        shutil.copy2(source, target)
        if hashlib.sha256(target.read_bytes()).hexdigest() != entry['source_hashes'][var]:
            raise ValueError(f'La fuente {var} cambio desde la validacion inicial; detener para conservar la trazabilidad.')
        snapshots[var] = str(target)
    entry['snapshot_sources'] = snapshots
    return {**entry, 'sources': snapshots}


def recovery_manifest(directory, year):
    """Resume only completed periods from their archived inputs, never today's Downloads."""
    directory = Path(directory).expanduser().resolve()
    manifest = json.loads((directory/'manifest_analisis_anual.json').read_text())
    if year != 2026 or manifest.get('anio') != year:
        raise ValueError('La recuperacion anual solo admite el mismo corte 2026.')
    runs, plan = manifest.get('runs', []), manifest.get('plan', [])
    if (len(runs) != 3 or {r.get('periodo') for r in runs} != {1,2,3}
            or any(r.get('status') != 0 for r in runs)):
        raise ValueError('Reanudar requiere P1/P2/P3 terminados con codigo 0.')
    expected_ids = {1:'923565',2:'443299',3:'967488'}
    if (len(plan) != 3 or {e.get('periodo') for e in plan} != {1,2,3}
            or any(e.get('anio') != year or str(e.get('survey_id')) != expected_ids[e['periodo']] for e in plan)):
        raise ValueError('Plan de recuperacion incompatible con las encuestas 2026.')
    for entry in plan:
        snapshots = entry.get('snapshot_sources', {})
        if set(snapshots) != set(SOURCE_VARS):
            raise ValueError('Faltan entradas archivadas para reanudar sin consultar Descargas.')
        for role, file in snapshots.items():
            archived = Path(file).resolve()
            if not archived.is_relative_to(directory/f'P{entry["periodo"]}'/'01_ENTRADAS'):
                raise ValueError('La entrada de recuperacion no pertenece al periodo archivado.')
            if hashlib.sha256(archived.read_bytes()).hexdigest() != entry.get('source_hashes', {}).get(role):
                raise ValueError(f'Entrada archivada alterada: P{entry["periodo"]} {role}')
    prepared = directory/'modelo_anual_privado.json'
    if prepared.is_file():
        payload = json.loads(prepared.read_text())
        sources = next(t for t in payload['audit'] if t['name']=='Fuentes')
        for row in sources['rows']:
            if row[2] == 'BASE_SECTORIZADA':
                base = Path(row[3]).resolve()
                if not base.is_relative_to(directory) or hashlib.sha256(base.read_bytes()).hexdigest() != row[4]:
                    raise ValueError('La base sectorizada cambio desde la consolidacion original.')
    return manifest


def delivery_inventory(directory):
    files = sorted(p for p in directory.rglob('*') if p.is_file())
    outputs = [p.relative_to(directory).as_posix() for p in files
               if p.relative_to(directory).parts[0] == '02_SALIDAS']
    audit_books = [p.relative_to(directory).as_posix() for p in files
                   if p.relative_to(directory).parts[0] == '04_AUDITORIA' and p.suffix.lower() == '.xlsx']
    return {'salidas': outputs, 'excel_auditoria': audit_books,
            'salidas_por_periodo': {f'P{period}': sum(name.startswith(f'02_SALIDAS/P{period}/') for name in outputs)
                                    for period in (1, 2, 3)},
            'archivos_respaldo': sum(p.relative_to(directory).parts[0] == '03_RESPALDOS' for p in files)}


def delivery_report(target, inventory):
    lines = ['ENTREGA ANUAL VERIFICADA', f'Carpeta final: {target}',
             f'Archivos en 02_SALIDAS: {len(inventory["salidas"])}',
             f'Excel de auditoria: {len(inventory["excel_auditoria"])}',
             f'Archivos conservados en 03_RESPALDOS: {inventory["archivos_respaldo"]}',
             'Los respaldos incluyen entradas y logs; no son nuevas salidas de analisis.']
    lines.extend(f'{period}: {count} archivos en 02_SALIDAS/{period}'
                 for period, count in inventory['salidas_por_periodo'].items())
    lines.append('ARCHIVOS DE ENTREGA (rutas relativas a la carpeta final):')
    lines.extend(f'  {name}' for name in inventory['salidas'] + inventory['excel_auditoria'])
    return '\n'.join(lines) + '\n'


def period_console_line(line):
    # The unchanged legacy runner calls its staging copy "Escritorio".
    return line.replace('Copia Escritorio:', 'Copia interna de etapa (no es la entrega final):')


def ensure_delivery_visible(directory):
    """Remove inherited Finder invisibility on the new delivery only, preserving data."""
    if sys.platform != 'darwin':
        return {'platform':sys.platform, 'status':'NO_APLICA_FINDER'}
    changed = 0
    paths = [directory, *directory.rglob('*')]
    for path in paths:
        if path.is_symlink():
            raise ValueError(f'La entrega no admite enlaces externos: {path.name}')
        flags = path.stat().st_flags
        if flags & stat.UF_HIDDEN:
            os.chflags(path, flags & ~stat.UF_HIDDEN)
            changed += 1
        # CPython exposes getxattr on Linux, not on all macOS builds.
        probe = subprocess.run(['/usr/bin/xattr','-px','com.apple.FinderInfo',str(path)],
                               text=True,capture_output=True)
        if probe.returncode and 'No such xattr' not in probe.stderr:
            raise ValueError(f'No se pudo verificar FinderInfo: {path.name}: {probe.stderr}')
        info = bytes.fromhex(probe.stdout) if probe.returncode == 0 else b''
        if len(info) >= 10 and int.from_bytes(info[8:10], 'big') & 0x4000:
            visible = int.from_bytes(info[8:10], 'big') & ~0x4000
            updated=info[:8]+visible.to_bytes(2,'big')+info[10:]
            subprocess.run(['/usr/bin/xattr','-wx','com.apple.FinderInfo',updated.hex(),str(path)],check=True,capture_output=True)
            probe = subprocess.run(['/usr/bin/xattr','-px','com.apple.FinderInfo',str(path)],check=True,text=True,capture_output=True)
            info=bytes.fromhex(probe.stdout)
            changed += 1
        if path.stat().st_flags & stat.UF_HIDDEN:
            raise ValueError(f'No se pudo hacer visible {path.name}')
        if info and int.from_bytes(info[8:10],'big') & 0x4000:
            raise ValueError(f'Finder conserva oculto {path.name}')
    return {'platform':'darwin','status':'VISIBLE_VERIFICADO','paths_checked':len(paths),'attributes_cleared':changed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('anio', type=int, nargs='?', default=2026)
    parser.add_argument('--solo-validar', action='store_true')
    parser.add_argument('--reanudar-consolidacion', type=Path,
                        help='Carpeta de una corrida con los tres periodos terminados; no repite sus analisis.')
    args = parser.parse_args()
    try:
        assert_frozen_reference()
        previous = recovery_manifest(args.reanudar_consolidacion, args.anio) if args.reanudar_consolidacion else None
        plan = previous['plan'] if previous else build_plan(args.anio)
    except (ValueError, OSError) as error:
        print(f'[ANUAL][BLOQUEO]\n{error}', file=sys.stderr)
        return 3
    for entry in plan:
        source_mode = 'RECUPERACION_ENTRADAS_ARCHIVADAS' if previous else entry['mode']
        print(f'[ANUAL] {entry["anio"]} P{entry["periodo"]}: encuesta {entry["survey_id"]}; {source_mode}')
        for var, file in entry['snapshot_sources' if previous else 'sources'].items():
            print(f'[ANUAL][P{entry["periodo"]}] {var}: {file}')
        if validation := entry.get('source_validation'):
            print(f'[ANUAL][P{entry["periodo"]}] Contenido LimeSurvey OK: '
                  f'tokens={validation["tokens_rows"]}; respuestas={validation["results_rows"]}; '
                  f'columnas de preguntas={validation["question_columns"]}; '
                  f'coincidencias={validation["matched_tokens"]}; cobertura={validation["coverage_pct"]}%')
    unique_sources = {file for entry in plan for file in entry['sources'].values()}
    print(f'[ANUAL] Entradas distintas: {len(unique_sources)}. Nuevo analisis; no reemplaza el cierre FCU 2026.')
    if args.solo_validar:
        print('[ANUAL] PREFLIGHT=OK; no se ejecuto el analisis.')
        return 0
    from consolidar_analisis_anual import POLICY, consolidate, renderer_runtime, sha
    try:
        renderer_runtime()
    except ValueError as error:
        print(f'[ANUAL][BLOQUEO] {error}', file=sys.stderr)
        return 3
    run_id = datetime.now(ZoneInfo('America/Santiago')).strftime('%Y%m%d_%H%M%S_%f')
    base = ROOT / '.local/analisis_anual' / str(args.anio) / run_id
    base.mkdir(parents=True, exist_ok=False)
    manifest = {'anio':args.anio, 'periodos':[1,2,3], 'state':'EN_EJECUCION', 'plan':plan, 'runs':[]}
    if previous:
        manifest.update(runs=previous['runs'], recovery_of=str(args.reanudar_consolidacion.resolve()),
                        previous_state=previous.get('state'), previous_error=previous.get('error'))
        print('[ANUAL] Recuperacion: se reutilizan P1/P2/P3 y sus entradas archivadas; no se ejecutan nuevamente.', flush=True)
    for entry in ([] if previous else plan):
        for var, file in entry['sources'].items():
            entry.setdefault('source_hashes', {})[var] = hashlib.sha256(Path(file).read_bytes()).hexdigest()
    manifest_path = base / 'manifest_analisis_anual.json'
    def save():
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    save()
    for entry in ([] if previous else plan):
        period = entry['periodo']
        run_dir = base / f'P{period}'
        run_dir.mkdir()
        try:
            execution_entry = snapshot_sources(entry, run_dir)
        except (ValueError, OSError) as error:
            manifest['state'] = 'INTERRUMPIDO_FUENTES'
            manifest['error'] = str(error)
            save()
            print(f'[ANUAL][BLOQUEO] {error}', file=sys.stderr)
            return 3
        env = child_environment(execution_entry, os.environ, run_dir)
        log = run_dir / f'analisis_2026_P{period}.log'
        env['CARACTERIZACION_LOG_PATH'] = str(log)
        command = [os.environ.get('CARACTERIZACION_BASH', 'bash'), str(ROOT / 'run_caracterizacion_fijo.sh'), str(args.anio), str(period), '1']
        print(f'[ANUAL] Inicio P{period}; carpeta: {run_dir}', flush=True)
        with log.open('w', encoding='utf-8') as stream:
            process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       text=True, encoding='utf-8', errors='replace')
            for line in process.stdout:
                print(period_console_line(line), end='', flush=True)
                stream.write(line)
            status = process.wait()
        manifest['runs'].append({'periodo':period, 'status':status, 'directory':str(run_dir), 'log':str(log)})
        if status:
            manifest['state'] = 'INTERRUMPIDO'
            save()
            print(f'[ANUAL] P{period} fallo; no se ejecutan los periodos siguientes.', file=sys.stderr)
            return status
        assert_frozen_reference()
        save()
    manifest['state'] = 'CONSOLIDANDO'
    save()
    try:
        if previous:
            delivery = consolidate(plan, args.reanudar_consolidacion.resolve(), output_base=base)
        else:
            delivery = consolidate(plan, base)
        assert_frozen_reference()
        desktop = Path(os.environ.get('CARACTERIZACION_DESKTOP_BASE') or Path.home()/'Desktop').expanduser().resolve()
        target = desktop / f'Caracterizacion_anual_{args.anio}_{run_id}'
        inventory = delivery_inventory(delivery)
        report = delivery_report(target, inventory)
        (delivery/'SALIDAS_GENERADAS.txt').write_text(report, encoding='utf-8')
        # Publish only after both workbooks and all source/period backups exist.
        temporary = target.with_name(target.name + '.incompleto')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(delivery, temporary)
        visibility = ensure_delivery_visible(temporary)
        expected = {str(p.relative_to(delivery)): sha(p) for p in delivery.rglob('*') if p.is_file()}
        actual = {str(p.relative_to(temporary)): sha(p) for p in temporary.rglob('*') if p.is_file()}
        if expected != actual:
            raise ValueError('La copia anual no coincide con los archivos generados.')
        manifest.update(state='PUBLICANDO', delivery=str(target), outputs=expected,
                        policy=POLICY, delivery_inventory=inventory, visibility=visibility)
        save()
        temporary.rename(target)
        if any(not (target/name).is_file() or sha(target/name) != digest for name, digest in expected.items()):
            raise ValueError('La entrega final no esta completa en el destino; no declarar copia correcta.')
        manifest.update(state='COMPLETO_ANUAL_INTEGRADO')
        save()
        shutil.copy2(manifest_path, target/'04_AUDITORIA'/manifest_path.name)
        ensure_delivery_visible(target)
        if sha(manifest_path) != sha(target/'04_AUDITORIA'/manifest_path.name):
            raise ValueError('El manifiesto final no coincide con su copia.')
    except Exception as error:
        manifest.update(state='ERROR_CONSOLIDACION', error=str(error))
        save()
        print(f'[ANUAL][BLOQUEO] Se conservan los períodos, pero no se declara completo el anual: {error}', file=sys.stderr)
        return 3
    location = 'ESCRITORIO' if desktop == (Path.home()/'Desktop').resolve() else 'DESTINO CONFIGURADO (CARACTERIZACION_DESKTOP_BASE)'
    print(f'[ANUAL][COPIA {location}: OK] {target}')
    print(f'[ANUAL] Integridad SHA-256: {len(expected)} archivos verificados y manifiesto copiado.')
    print(report, end='')
    print(f'[ANUAL] Listado guardado: {target / "SALIDAS_GENERADAS.txt"}')
    print(f'[ANUAL] Manifiesto: {manifest_path}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
