"""Operational 2027 lists for a survey whose absence of responses is confirmed."""
import ast
import csv
from datetime import date, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import unicodedata
import uuid
from typing import Tuple

import pandas as pd
import caracterizacion_runtime as runtrace
from caracterizacion_estado_kpi import mascara_titulado_kpi
from caracterizacion_limesurvey import inspect_tokens_file, read_input_frame
from caracterizacion_limesurvey_policy import clasificar_pendiente_limesurvey
from caracterizacion_universo import mascara_programas_excluidos, normalizar_programa

ROOT = Path(__file__).resolve().parent
TOKEN_COLUMNS = ['tid', 'firstname', 'lastname', 'email', 'emailstatus', 'token', 'language',
                 'validfrom', 'validuntil', 'invited', 'reminded', 'remindercount', 'completed', 'usesleft']


class InstitutionalEmailError(ValueError):
    """Blocking contact error; student details are kept out of the terminal."""
    def __init__(self, students, columns, reason):
        self.students = students.copy()
        self.columns = columns
        super().__init__(f'{len(students)} estudiantes sin Mail_Inst valido ({reason}). '
                         'No sustituir por MAIL personal. Corregir Mail_Inst en la fuente de matricula.')


def institutional_email_valid(values):
    """Validate the source field, trimming edges without repairing addresses."""
    clean = values.fillna('').astype(str).str.strip()
    syntax = clean.str.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', na=False)
    invisible = clean.map(lambda value: any(unicodedata.category(c).startswith('C') for c in value)).astype(bool)
    return syntax & ~invisible


def write_private_email_audit(error, matricula, sources, counts):
    """Persist identifiers only under Git-ignored .local, never in public governance."""
    directory = ROOT / '.local/auditoria_correos' / uuid.uuid4().hex
    directory.mkdir(parents=True, mode=0o700)
    columns = error.columns
    keys = matricula[columns['RUT']].map(shared_operational_rules()['token_match_rut'])
    fields = ['CODCLI', 'RUT', 'ANOMATRICULA', 'PERIODOMATRICULA', 'ANOINGRESO',
              'FECHAMATRICULA', 'ESTADOACADEMICO', 'SITUACION', 'CONFIRMA', 'NOMBREL', 'MAILINST']
    records = []
    for index, student in error.students.iterrows():
        peers = matricula.loc[keys.eq(student['TOKEN'])]
        rows = []
        for peer_index, peer in peers.iterrows():
            raw = peer[columns['MAILINST']] if 'MAILINST' in columns else None
            rows.append({
                'dataframe_index':int(peer_index),
                'excel_row':int(peer_index) + 2 if Path(sources['RUTA_MATRICULA']).suffix.lower() in {'.xlsx', '.xlsm', '.xls'} else None,
                'fields':{columns[key]:None if pd.isna(peer[columns[key]]) else str(peer[columns[key]])
                          for key in fields if key in columns},
                'mail_inst_is_null':bool(pd.isna(raw)), 'mail_inst_repr':repr(raw),
                'mail_inst_codepoints':[] if pd.isna(raw) else [f'U+{ord(char):04X}' for char in str(raw)],
                'mail_inst_valid':bool(institutional_email_valid(pd.Series([raw])).iloc[0]),
            })
        records.append({'blocked_dataframe_index':int(index), 'token':student['TOKEN'],
                        'estado_correo':student.get('ESTADO_CORREO', 'INVALIDO'),
                        'motivo_pendiente':student.get('MOTIVO_PENDIENTE', 'MAIL_INST_AUSENTE_O_INVALIDO'),
                        'same_student_source_rows':rows,
                        'valid_mail_inst_in_other_row':any(row['mail_inst_valid'] for row in rows)})
    audit = directory / 'REGISTROS_BLOQUEADOS_PRIVADO.json'
    audit.write_text(json.dumps({'records':records}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    audit.chmod(0o600)
    manifest = {'status':'PENDIENTE_CORREO_NO_EXPORTABLE', 'policy':'INCORPORACION_2027_P1_CORREO_PENDIENTE-v1', 'counts':counts,
                'email_source':'Mail_Inst', 'personal_email_fallback_allowed':False,
                'mail_inst_column':columns.get('MAILINST'),
                'sources':{var:{'path':file, 'sha256':hashlib.sha256(Path(file).read_bytes()).hexdigest()}
                           for var, file in sources.items()}, 'private_audit':str(audit)}
    manifest_path = directory / 'MANIFIESTO_DIAGNOSTICO.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    manifest_path.chmod(0o600)
    return audit


def shared_operational_rules():
    """Load only existing pure helpers and literals, without running the pipeline."""
    names = {'_clean_str', 'token_match_rut', 'cargar_feriados_chile',
             'es_dia_no_laborable_scl', 'ventana_habil_scl'}
    constants = {'TOKENS_JEFATURA_EXCLUIR', 'DIPLOMADOS_EXCLUIR'}
    tree = ast.parse((ROOT / 'caracterizacion.py').read_text())
    context = {'pd':pd, 're':re, 'csv':csv, 'Path':Path, 'date':date, 'timedelta':timedelta, 'Tuple':Tuple}
    functions = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            functions.append(node)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in constants:
                    context[target.id] = ast.literal_eval(node.value)
    if {f.name for f in functions} != names or not constants.issubset(context):
        raise ValueError('No se encontraron todas las reglas operativas existentes.')
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(ROOT / 'caracterizacion.py'), 'exec'), context)
    context['FERIADOS_CHILE_CSV'] = Path(os.environ.get('CARACTERIZACION_FERIADOS_CSV',
        str(ROOT / 'docs/gobernanza/FERIADOS_CHILE_2026_2040.csv')))
    context['FERIADOS_CHILE'] = context['cargar_feriados_chile']()
    return context


def validate_no_responses(tokens, historical_respondents=0):
    if 'completed' not in tokens.columns:
        raise ValueError('No existe completed en los participantes para comprobar el estado sin respuestas.')
    values = tokens['completed'].fillna('').astype(str).str.strip().str.upper()
    if not values.isin(['', 'N', 'NO', '0', 'FALSE']).all():
        raise ValueError('Los participantes registran respuestas completadas; no aplicar modo sin respuestas.')
    if historical_respondents > 0:
        raise ValueError('Existen respondientes historicos; no sustituir sus resultados por cero respuestas.')


def eligible_students(matricula, year, period, rules):
    frame = matricula.copy()
    normalized = {re.sub(r'[^A-Z0-9]', '', normalizar_programa(c)):c for c in frame.columns}
    required = ['CODCLI','RUT','NOMBREL','ANOMATRICULA','PERIODOMATRICULA','ANOINGRESO',
                'FECHAMATRICULA','ESTADOACADEMICO','SITUACION','CONFIRMA']
    if any(name not in normalized for name in required):
        raise ValueError('Faltan columnas de matricula: ' + ', '.join(n for n in required if n not in normalized))
    def col(name):
        return frame[normalized[name]]
    def number(name):
        return pd.to_numeric(col(name), errors='coerce')
    in_period = number('ANOMATRICULA').eq(year) & number('PERIODOMATRICULA').eq(period)
    target_year = number('ANOINGRESO').eq(year)
    signed = col('CONFIRMA').map(normalizar_programa).eq('SI')
    current = col('ESTADOACADEMICO').map(normalizar_programa).eq('VIGENTE')
    graduate = mascara_titulado_kpi(col('ESTADOACADEMICO'), col('SITUACION'))
    program = mascara_programas_excluidos(col('NOMBREL'), catalogo_exclusion=rules['DIPLOMADOS_EXCLUIR'])
    keys = col('RUT').map(rules['token_match_rut'])
    admin = keys.isin({rules['token_match_rut'](v) for v in rules['TOKENS_JEFATURA_EXCLUIR']})
    eligible_before_trajectory = in_period & target_year & signed & current & ~graduate & ~program & ~admin
    from caracterizacion_trayectorias_2027 import classify_trajectories
    trajectory_detail, trajectory_summary, _ = classify_trajectories(matricula, year, period)
    previous = trajectory_detail['TIENE_TRAYECTORIA_PREVIA'].reindex(frame.index, fill_value=False).astype(bool)
    eligible_mask = eligible_before_trajectory & ~previous
    frame['TIENE_TRAYECTORIA_PREVIA'] = previous
    frame['PRIMER_INGRESO_INSTITUCIONAL'] = trajectory_detail['PRIMER_INGRESO_INSTITUCIONAL'].reindex(frame.index, fill_value=False).astype(bool)
    frame['TOKEN'] = keys
    frame['FECHAMATRICULA_DT'] = pd.to_datetime(col('FECHAMATRICULA'), format='mixed', dayfirst=True, errors='coerce').dt.date
    eligible = frame.loc[eligible_mask].copy()
    eligible.attrs['candidate_indices_before_trajectory'] = frame.index[eligible_before_trajectory].tolist()
    if eligible['TOKEN'].eq('').any():
        raise ValueError('La matricula elegible contiene RUT sin clave; revisar la fuente.')
    counts = {
        'CANDIDATOS_ANTES_TRAYECTORIA':int(eligible_before_trajectory.sum()),
        'EXCLUIDOS_TRAYECTORIA_PREVIA':int((eligible_before_trajectory & previous).sum()),
        'TRAYECTORIA_PREVIA_PERSONAS_PERIODO':trajectory_summary['TRAYECTORIA_PREVIA_PERSONAS'],
        'REGISTROS_FUENTE':len(frame),
        'FUERA_ANO_PERIODO':int((~in_period).sum()),
        'MATRICULA_PERIODO':int(in_period.sum()),
        'EXCLUIDOS_UNICOS_PERIODO':int((in_period & ~eligible_mask).sum()),
        'ELIMINADOS_PERIODO':int((in_period & col('ESTADOACADEMICO').map(normalizar_programa).eq('ELIMINADO')).sum()),
        'VIGENTES_SIN_FIRMA':int((in_period & target_year & current & ~graduate & ~program & ~admin & ~signed).sum()),
        'EXCLUIDOS_ANO_INGRESO':int((in_period & ~target_year).sum()),
        'EXCLUIDOS_SIN_FIRMA':int((in_period & ~signed).sum()),
        'EXCLUIDOS_ESTADO_SITUACION':int((in_period & (~current | graduate)).sum()),
        'EXCLUIDOS_PROGRAMA':int((in_period & program).sum()),
        'EXCLUIDOS_ADMIN':int((in_period & admin).sum())
    }
    return eligible, counts, normalized


def build_lists(matricula, tokens, year, period, today, rules):
    from caracterizacion_incorporacion import build_plan
    plan = build_plan(matricula, tokens, year, period, today, rules)
    counts = {**plan.counts, 'RESPUESTAS_COMPLETAS':0, 'SIN_RESPUESTA':len(plan.eligible)}
    residual = pd.concat([plan.pending_email, plan.temporal]).sort_index()
    return plan.eligible, plan.daily, plan.backlog, residual, counts, plan.window, plan.columns


def token_import_frame(students, columns):
    result = pd.DataFrame('', index=students.index, columns=TOKEN_COLUMNS)
    def values(key):
        return students[columns[key]].fillna('').astype(str).str.strip() if key in columns else pd.Series('', index=students.index)
    result['firstname'] = values('NOMBRES')
    fallback_name = result['firstname'].eq('')
    result.loc[fallback_name, 'firstname'] = values('NOMBRE').loc[fallback_name]
    result['lastname'] = (values('APELLIDOPATERNO') + ' ' + values('APELLIDOMATERNO')).str.strip()
    if 'MAILINST' not in columns:
        raise InstitutionalEmailError(students, columns, 'falta la columna Mail_Inst')
    result['email'] = values('MAILINST')
    invalid = ~institutional_email_valid(result['email'])
    if invalid.any():
        raise InstitutionalEmailError(students.loc[invalid], columns, 'vacio o formato invalido')
    result['token'] = students['TOKEN']
    result['emailstatus'], result['language'], result['completed'], result['usesleft'] = 'OK', 'es', 'N', '1'
    return result


def write_excel(frame, filename, sheet='Estudiantes'):
    output = runtrace.output_path(filename)
    frame.to_excel(output, sheet_name=sheet, index=False, engine='openpyxl')
    return output


def enrollment_email_summary(counts, students, columns, today, window):
    lines = [
        f'Asunto: Reporte de matrícula y caracterización 2027 P1 - {today.strftime("%d-%m-%Y")}',
        '', 'Estimados/as:', '',
        f'Adjunto el reporte de matrícula correspondiente al período 2027 P1, con corte al {today.strftime("%d-%m-%Y")}.',
        '', 'Resumen de matrícula:',
        f'- Registros del período: {counts["MATRICULA_PERIODO"]}.',
        f'- Estudiantes vigentes elegibles, de ingreso 2027 y con firma: {counts["VIGENTES_ELEGIBLES"]}.',
        f'- Registros eliminados: {counts["ELIMINADOS_PERIODO"]}.',
        f'- Vigentes pendientes de firma: {counts["VIGENTES_SIN_FIRMA"]}.',
        '', 'Distribución de los vigentes por jornada:'
    ]
    if 'JORNADA' in columns:
        raw = students[columns['JORNADA']].map(normalizar_programa).value_counts().to_dict()
        labels = {'O':'Online', 'V':'Vespertina', 'D':'Diurna'}
        lines.extend(f'- {labels.get(key,key)}: {int(value)}.' for key, value in sorted(raw.items()))
    ready = counts['NUEVOS_DIARIOS'] + counts['NUEVOS_REZAGADOS']
    lines.extend([
        '', 'Incorporación a LimeSurvey:',
        f'- Ventana diaria cerrada del {window[0].strftime("%d-%m-%Y")} al {window[1].strftime("%d-%m-%Y")}: {counts["NUEVOS_DIARIOS"]} estudiantes.',
        f'- Matrículas anteriores a esa ventana: {counts["NUEVOS_REZAGADOS"]} estudiantes.',
        f'- Total identificado para incorporar mediante ambos CSV: {ready} estudiantes.',
        f'- Fechas posteriores al corte o inválidas, conservadas para revisión/siguiente corte: {counts["PENDIENTES_FECHA_NO_CERRADA_O_INVALIDA"]}.',
        '', 'Los CSV de incorporación utilizan exclusivamente los correos institucionales de Mail_Inst. El Excel conserva el detalle de los estudiantes y las fechas de matrícula.',
        '', 'Saludos cordiales.'
    ])
    return '\n'.join(lines) + '\n'


def main():
    year, period = int(os.environ['ANIO_ANALISIS']), int(os.environ['PERIODO_ANALISIS'])
    if (year, period) != (2027, 1) or os.environ.get('CARACTERIZACION_RESULTADOS_SIN_RESPUESTAS') != '1':
        raise ValueError('El modo operativo sin respuestas esta gobernado para 2027 P1.')
    ctx = runtrace.prepare_run_context(year, period, external_tee=True)
    try:
        historical = runtrace.historical_max_respondents(year, period, current_run_dir=ctx.run_dir)
        token_path = os.environ['RUTA_INSCRITOS']
        if inspect_tokens_file(token_path).name_id != '141234':
            raise ValueError('Los participantes no corresponden a la encuesta gobernada 141234.')
        tokens = read_input_frame(token_path)
        validate_no_responses(tokens, historical)
        runtrace.archive_input(token_path, 'inscritos_limesurvey')
        runtrace.archive_input(os.environ['RUTA_MATRICULA'], 'matricula_oficial')
        results_path = os.environ.get('RUTA_RESULTADOS')
        if results_path and Path(results_path).is_file():
            if Path(results_path).stat().st_size > 0 and not read_input_frame(results_path).empty:
                raise ValueError('El archivo ya contiene respuestas; ejecutar el flujo normal.')
            runtrace.archive_input(results_path, 'resultados_vacios_confirmados')
        from caracterizacion_comunicacion_2027 import cutoff_date
        today = cutoff_date()
        rules = shared_operational_rules()
        matricula = read_input_frame(os.environ['RUTA_MATRICULA'])
        from caracterizacion_incorporacion import build_plan, publish_plan
        try:
            from docx import Document
        except ImportError:
            sys.path.insert(0, str(ROOT / '.deps_local' / f'py{sys.version_info.major}.{sys.version_info.minor}'))
            from docx import Document
        plan = build_plan(matricula, tokens, year, period, today, rules)
        eligible, counts, window, columns = plan.eligible, plan.counts, plan.window, plan.columns
        counts.update(RESPUESTAS_COMPLETAS=0, SIN_RESPUESTA=len(eligible))
        stamp = today.strftime('%Y%m%d')
        write_excel(tokens, f'Lista_participantes_LimeSurvey_{year}_P{period}_{stamp}.xlsx', 'Participantes')
        write_excel(plan.eligible_enrollments, f'Estudiantes_matriculados_Periodo_{year}_P{period}_{stamp}.xlsx')
        from caracterizacion_etiquetas_2027 import publish_response_tracking
        qa = publish_response_tracking(eligible, stamp,
            lambda frame, filename, sheet, title: write_excel(frame, filename, sheet))
        outputs = publish_plan(plan, matricula, {key:os.environ[key] for key in
            ('RUTA_MATRICULA','RUTA_INSCRITOS','RUTA_RESULTADOS') if os.environ.get(key)})
        from caracterizacion_comunicacion_2027 import publish_reports
        email_word, internal_word, aggregate = publish_reports(plan,responses_available=False)
        state = {'state':'SIN_RESPUESTAS_CONFIRMADAS', 'authority':'Confirmacion del usuario y participantes sin completed',
                 'year':year, 'period':period, 'survey_id':'141234', 'responses_available':False,
                 'financial_analysis_available':False, 'counts':counts, 'response_tracking':qa, 'incorporation_outputs':outputs,
                 'window':{'start':str(window[0]),'end':str(window[1])},
                 'filter_source':{'path':str(ROOT / 'caracterizacion.py'),'sha256':runtrace.sha256_file(ROOT / 'caracterizacion.py')}}
        state['participant_email_source'] = 'Mail_Inst'
        state['personal_email_fallback_allowed'] = False
        from caracterizacion_reportes_2027 import ordered_document_text
        runtrace.output_path(f'Correo_resumen_matricula_{year}_P{period}_{stamp}.txt', audit=False).write_text(
            ordered_document_text(email_word)+'\n', encoding='utf-8')
        runtrace.output_path(f'ESTADO_ENCUESTA_{year}_P{period}_{stamp}.json', audit=True).write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n')
        for key, value in counts.items():
            print(f'[SIN RESPUESTAS] {key}={value}', flush=True)
        print('[SIN RESPUESTAS] Listas operativas generadas. Financiamiento: SIN DATOS DE RESPUESTAS.', flush=True)
        runtrace.finalize({'n_respondientes':0, 'total_matriculados':len(eligible)}, code=0)
        return 0
    except Exception as error:
        runtrace.finalize(code=1, error=str(error))
        raise


if __name__ == '__main__':
    sys.exit(main())
