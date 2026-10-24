"""Policy authorized 2026-10-13: email holds a student, never the whole run.

Shared by both 2027 P1 modes. Every plan is rebuilt from current matrícula and
current tokens; generated files are not evidence of actual incorporation.
"""
from dataclasses import dataclass, field
from datetime import date
import json

import pandas as pd
from caracterizacion_sin_respuestas import (eligible_students, institutional_email_valid,
    token_import_frame, TOKEN_COLUMNS, write_private_email_audit, InstitutionalEmailError)
from caracterizacion_universo import normalizar_programa, mascara_programas_excluidos
from caracterizacion_estado_kpi import mascara_titulado_kpi
from caracterizacion_limesurvey_policy import clasificar_pendiente_limesurvey
import caracterizacion_runtime as runtrace

POLICY = 'INCORPORACION_2027_P1_CORREO_PENDIENTE-v1'


@dataclass
class IncorporationPlan:
    eligible: pd.DataFrame
    missing: pd.DataFrame
    ready: pd.DataFrame
    pending_email: pd.DataFrame
    daily: pd.DataFrame
    backlog: pd.DataFrame
    temporal: pd.DataFrame
    signature: pd.DataFrame
    counts: dict
    columns: dict
    today: date
    window: tuple
    trajectory_detail: pd.DataFrame = field(default_factory=pd.DataFrame)
    trajectory_evidence: pd.DataFrame = field(default_factory=pd.DataFrame)
    trajectory_summary: dict = field(default_factory=dict)
    current_tokens: tuple = ()
    eligible_enrollments: pd.DataFrame = field(default_factory=pd.DataFrame)


def build_plan(matricula, tokens, year, period, today, rules):
    if (year, period) != (2027, 1):
        raise ValueError('La politica de correo pendiente es exclusiva de 2027 P1.')
    eligible, counts, columns = eligible_students(matricula, year, period, rules)
    if 'MAILINST' not in columns:
        raise ValueError('Falta la columna Mail_Inst en la estructura de matricula.')
    from caracterizacion_personas_2027 import person_view
    enrollments = eligible.copy()
    eligible = person_view(enrollments, columns, institutional_email_valid)
    if 'token' not in tokens:
        raise ValueError('Falta la columna token en participantes.')
    keys = tokens['token'].map(rules['token_match_rut'])
    if keys.eq('').any() or keys.duplicated().any():
        raise ValueError('Hay tokens vacios o repetidos en participantes.')
    eligible['EN_LIMESURVEY'] = eligible['TOKEN'].isin(set(keys))
    eligible['Responden'] = 'NO'  # Response-free consumers only; normal pipeline retains its own response state.
    start, end = rules['ventana_habil_scl'](today)
    eligible['CORREO_INSTITUCIONAL_VALIDO'] = institutional_email_valid(eligible[columns['MAILINST']])
    raw = eligible[columns['MAILINST']].fillna('').astype(str).str.strip()
    eligible['ESTADO_CORREO'] = 'VALIDO'
    eligible.loc[~eligible['CORREO_INSTITUCIONAL_VALIDO'], 'ESTADO_CORREO'] = 'INVALIDO'
    eligible.loc[raw.eq(''), 'ESTADO_CORREO'] = 'AUSENTE'
    eligible.loc[eligible['CONFLICTO_CORREO_INSTITUCIONAL'], 'ESTADO_CORREO'] = 'CONFLICTO_ENTRE_MATRICULAS'
    classifications = [clasificar_pendiente_limesurvey(value if pd.notna(value) else None, ano_ingreso=year, anio_objetivo=year,
        ventana_inicio=start, ventana_fin=end) for value in eligible['FECHAMATRICULA_DT']]
    eligible['CLASIFICACION_LIMESURVEY'] = [item.categoria for item in classifications]
    eligible['EN_VENTANA_DIARIA'] = [item.en_ventana for item in classifications]
    eligible['ES_REZAGADO'] = [item.es_rezagado for item in classifications]
    eligible['PENDIENTE_CORREO_INSTITUCIONAL'] = ~eligible['CORREO_INSTITUCIONAL_VALIDO']
    eligible['PENDIENTE_FECHA'] = ~(eligible['EN_VENTANA_DIARIA'] | eligible['ES_REZAGADO'])
    eligible['FECHA_EJECUCION'] = today
    eligible['BRECHA_DIAS'] = eligible['FECHAMATRICULA_DT'].map(lambda value: (today-value).days if pd.notna(value) else pd.NA)
    eligible['FUENTE_EMAIL_LIMESURVEY'] = 'Mail_Inst'
    eligible['EMAIL_PARA_LIMESURVEY'] = raw.where(eligible['CORREO_INSTITUCIONAL_VALIDO'], '')
    eligible['ESTADO_INCORPORACION'] = 'PENDIENTE_FECHA'
    closed = eligible['EN_VENTANA_DIARIA'] | eligible['ES_REZAGADO']
    eligible.loc[closed & eligible['CORREO_INSTITUCIONAL_VALIDO'], 'ESTADO_INCORPORACION'] = 'LISTO_PARA_INCORPORAR'
    eligible.loc[~eligible['CORREO_INSTITUCIONAL_VALIDO'], 'ESTADO_INCORPORACION'] = 'PENDIENTE_CORREO_INSTITUCIONAL'
    eligible.loc[eligible['EN_LIMESURVEY'], 'ESTADO_INCORPORACION'] = 'YA_INCORPORADO_EN_TOKENS'
    eligible['MOTIVO_PENDIENTE'] = eligible['ESTADO_INCORPORACION'].map({
        'LISTO_PARA_INCORPORAR':'CORREO_VALIDO_Y_FECHA_HABILITADA',
        'PENDIENTE_CORREO_INSTITUCIONAL':'MAIL_INST_AUSENTE_O_INVALIDO',
        'PENDIENTE_FECHA':'FECHA_NO_CERRADA_O_INVALIDA', 'YA_INCORPORADO_EN_TOKENS':''})
    eligible.loc[eligible['CONFLICTO_CORREO_INSTITUCIONAL'] & ~eligible['EN_LIMESURVEY'],
                 'MOTIVO_PENDIENTE'] = 'VARIOS_MAIL_INST_VALIDOS_DISTINTOS'
    missing = eligible.loc[~eligible['EN_LIMESURVEY']].copy()
    ready = missing.loc[missing['CORREO_INSTITUCIONAL_VALIDO']].copy()
    pending_email = missing.loc[~missing['CORREO_INSTITUCIONAL_VALIDO']].copy()
    daily = ready.loc[ready['EN_VENTANA_DIARIA']].copy()
    backlog = ready.loc[ready['ES_REZAGADO']].copy()
    temporal = ready.loc[~(ready['EN_VENTANA_DIARIA'] | ready['ES_REZAGADO'])].copy()

    def col(key):
        return matricula[columns[key]]
    signature_mask = (pd.to_numeric(col('ANOMATRICULA'), errors='coerce').eq(year)
        & pd.to_numeric(col('PERIODOMATRICULA'), errors='coerce').eq(period)
        & pd.to_numeric(col('ANOINGRESO'), errors='coerce').eq(year)
        & col('ESTADOACADEMICO').map(normalizar_programa).eq('VIGENTE')
        & ~mascara_titulado_kpi(col('ESTADOACADEMICO'), col('SITUACION'))
        & ~mascara_programas_excluidos(col('NOMBREL'), catalogo_exclusion=rules['DIPLOMADOS_EXCLUIR'])
        & ~col('RUT').map(rules['token_match_rut']).isin({rules['token_match_rut'](v) for v in rules['TOKENS_JEFATURA_EXCLUIR']})
        & ~col('CONFIRMA').map(normalizar_programa).eq('SI'))
    signature = matricula.loc[signature_mask].copy()
    signature['TOKEN'] = signature[columns['RUT']].map(rules['token_match_rut'])
    if signature['TOKEN'].eq('').any():
        raise ValueError('La matricula pendiente de firma contiene RUT sin clave.')
    signature['EN_UNIVERSO_ELEGIBLE'] = signature['TOKEN'].isin(set(eligible['TOKEN']))
    signature['PENDIENTE_FIRMA'] = True
    signature['CORREO_INSTITUCIONAL_VALIDO'] = institutional_email_valid(signature[columns['MAILINST']])
    signature['PENDIENTE_CORREO_INSTITUCIONAL'] = ~signature['CORREO_INSTITUCIONAL_VALIDO']
    signature['MOTIVO_PENDIENTE'] = 'FIRMA_PENDIENTE_NO_ELEGIBLE_PARA_INCORPORACION'
    signature['FECHA_EJECUCION'] = today
    dates = pd.to_datetime(signature[columns['FECHAMATRICULA']], format='mixed', dayfirst=True, errors='coerce').dt.date
    signature['BRECHA_DIAS'] = dates.map(lambda value: (today-value).days if pd.notna(value) else pd.NA)
    signature_raw = signature[columns['MAILINST']].fillna('').astype(str).str.strip()
    signature['ESTADO_CORREO'] = signature_raw.map(lambda value: 'AUSENTE' if not value else 'INVALIDO')
    signature.loc[signature['CORREO_INSTITUCIONAL_VALIDO'], 'ESTADO_CORREO'] = 'VALIDO'
    unique_signature = signature.drop_duplicates('TOKEN')
    outside = unique_signature.loc[~unique_signature['EN_UNIVERSO_ELEGIBLE']]
    counts.update(VIGENTES_ELEGIBLES=len(eligible), PARTICIPANTES_LIMESURVEY=len(tokens),
        MATRICULAS_ELEGIBLES=len(enrollments), RUT_MULTIMATRICULA=int(eligible['MATRICULAS_ELEGIBLES_RUT'].gt(1).sum()),
        FILAS_MULTIMATRICULA=int(eligible.loc[eligible['MATRICULAS_ELEGIBLES_RUT'].gt(1),'MATRICULAS_ELEGIBLES_RUT'].sum()),
        FILAS_ADICIONALES_POR_RUT=len(enrollments)-len(eligible),
        VIGENTES_CON_TOKEN=int(eligible['EN_LIMESURVEY'].sum()), VIGENTES_SIN_TOKEN=len(missing),
        CORREOS_VALIDOS_INCORPORACION=len(ready), PENDIENTES_CORREO_INSTITUCIONAL=len(pending_email),
        PENDIENTES_CONFLICTO_CORREO=int(pending_email['CONFLICTO_CORREO_INSTITUCIONAL'].sum()),
        LISTOS_PARA_INCORPORAR=len(daily)+len(backlog), NUEVOS_DIARIOS=len(daily), NUEVOS_REZAGADOS=len(backlog),
        PENDIENTES_FECHA_NO_CERRADA_O_INVALIDA=len(temporal),
        PENDIENTES_FIRMA_PERSONAS=len(unique_signature), PENDIENTES_FIRMA_FUERA_ELEGIBLES=len(outside),
        PENDIENTES_FIRMA_TAMBIEN_ELEGIBLES=int(unique_signature['EN_UNIVERSO_ELEGIBLE'].sum()),
        PENDIENTES_FIRMA_Y_CORREO=int(outside['PENDIENTE_CORREO_INSTITUCIONAL'].sum()))
    assert len(missing) == len(pending_email) + len(daily) + len(backlog) + len(temporal)
    assert len(eligible) == counts['VIGENTES_CON_TOKEN'] + len(missing)
    assert not set(daily['TOKEN']) & set(backlog['TOKEN'])
    from caracterizacion_trayectorias_2027 import classify_trajectories
    detail, summary, evidence = classify_trajectories(matricula, year, period)
    detail['CANDIDATO_FILTROS_OPERATIVOS'] = detail.index.isin(eligible.attrs.get('candidate_indices_before_trajectory',[]))
    return IncorporationPlan(eligible, missing, ready, pending_email, daily, backlog, temporal, signature,
                            counts, columns, today, (start,end), detail, evidence, summary, tuple(sorted(keys)), enrollments)


def incorporation_paragraphs(plan):
    c = plan.counts
    email_pending = c['PENDIENTES_CORREO_INSTITUCIONAL']
    pending_phrase = (f'{email_pending} permanece pendiente' if email_pending == 1
                      else f'{email_pending} permanecen pendientes')
    records_phrase = f'{c["VIGENTES_SIN_FIRMA"]} ' + ('registro' if c['VIGENTES_SIN_FIRMA'] == 1 else 'registros')
    people_phrase = f'{c["PENDIENTES_FIRMA_PERSONAS"]} ' + ('persona única' if c['PENDIENTES_FIRMA_PERSONAS'] == 1 else 'personas únicas')
    paragraphs = [
        f'De los {c["VIGENTES_SIN_TOKEN"]} estudiantes elegibles aún no incorporados a LimeSurvey, '
        f'{c["CORREOS_VALIDOS_INCORPORACION"]} cuentan con correo institucional válido; '
        f'{c["LISTOS_PARA_INCORPORAR"]} están disponibles para incorporación según la ventana temporal. '
        f'{pending_phrase} por correo institucional ausente, inválido o contradictorio entre matrículas. '
        'Estos casos se revisarán nuevamente en la siguiente ejecución.',
        f'CSV diario: {len(plan.daily)}. CSV acumulado: {len(plan.backlog)}. '
        f'Con correo válido y fecha posterior al corte o inválida: {len(plan.temporal)}. '
        f'Ventana cerrada: {plan.window[0]:%d-%m-%Y} al {plan.window[1]:%d-%m-%Y}; se excluye el día de ejecución.',
        f'Pendientes de firma: {records_phrase} de matrícula, {people_phrase}; '
        f'{c["PENDIENTES_FIRMA_FUERA_ELEGIBLES"]} fuera del universo elegible para incorporación. '
        f'De estas últimas, {c["PENDIENTES_FIRMA_Y_CORREO"]} también presentan correo ausente o inválido. '
        f'{c["PENDIENTES_FIRMA_TAMBIEN_ELEGIBLES"]} personas tienen además otra matrícula elegible. '
        'Los motivos simultáneos se conservan como indicadores; no se suman a los pendientes elegibles ni se cuentan dos veces.',
        f'Matrícula fuente del período: {c["MATRICULA_PERIODO"]} registros; '
        f'{c["EXCLUIDOS_UNICOS_PERIODO"]} excluidos únicos tras aplicar los filtros. '
        'La tabla de matrícula del informe utiliza el universo depurado, que ya excluye firma pendiente. '
        f'Conciliación: {c["VIGENTES_ELEGIBLES"]} elegibles = {c["VIGENTES_CON_TOKEN"]} con token + '
        f'{c["VIGENTES_SIN_TOKEN"]} sin token. Los sin token se distribuyen en '
        f'{len(plan.daily)} diarios + {len(plan.backlog)} acumulados + {len(plan.pending_email)} pendientes de correo + '
        f'{len(plan.temporal)} pendientes de fecha. Los archivos generados no acreditan incorporación: '
        'se comprueba la presencia en los tokens actuales en cada ejecución.'
    ]
    return paragraphs


def add_word_section(doc, plan):
    from docx.shared import RGBColor, Pt
    heading = doc.add_heading('Estado de incorporación a LimeSurvey', level=1)
    for run in heading.runs:
        run.font.color.rgb = RGBColor(0, 0, 0)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
    for paragraph in incorporation_paragraphs(plan):
        doc.add_paragraph(paragraph)


def finish_word_2027(doc, plan):
    """Retired mixed-document API; fail on attempts to restore the old policy."""
    raise ValueError('El estado de incorporacion pertenece a 05_ANALISIS; usar los builders separados de reportes 2027.')


def publish_plan(plan, matricula, sources):
    """Write importable CSVs and a separate workbook for all pending states."""
    stamp = plan.today.strftime('%Y%m%d')
    suffix = f'2027_P1_{stamp}'
    names = {'daily':f'+ Nuevos inscritos hoy_{suffix}.csv',
             'backlog':f'+ Nuevos inscritos acumulados no incorporados a LimeSurvey_{suffix}.csv'}
    outputs = {}
    from caracterizacion_personas_2027 import publish_multiple_enrollments
    multiple = publish_multiple_enrollments(plan)
    if multiple:
        outputs['multiple_enrollments'] = multiple
    for key, frame in [('daily',plan.daily),('backlog',plan.backlog)]:
        if not frame.empty:
            imported = token_import_frame(frame, plan.columns)
            if imported.token.eq('').any() or imported.token.duplicated().any():
                raise ValueError('Tokens vacios o duplicados en el CSV de incorporacion.')
            target = runtrace.output_path(names[key])
            imported.to_csv(target, index=False, encoding='utf-8-sig')
            outputs[key] = str(target)
    # Preserve the established accumulated Excel name when it has older pending records.
    # This tracking workbook may contain non-importable cases; the CSV never does.
    if not plan.missing.empty or not plan.signature.empty:
        older = bool(plan.missing['ES_REZAGADO'].any())
        filename = (f'+ Nuevos inscritos acumulados no incorporados a LimeSurvey_{suffix}.xlsx' if older
                    else f'Seguimiento_incorporacion_LimeSurvey_{suffix}.xlsx')
        target = runtrace.analysis_path(filename)
        selected = [key for key in ['CODCLI','RUT','NOMBRE','NOMBREL','ANOMATRICULA','PERIODOMATRICULA',
                    'ANOINGRESO','FECHAMATRICULA','CONFIRMA','MAILINST'] if key in plan.columns]
        original = [plan.columns[key] for key in selected]
        derived = ['TOKEN','EN_LIMESURVEY','ESTADO_CORREO','CORREO_INSTITUCIONAL_VALIDO',
            'ESTADO_INCORPORACION','MOTIVO_PENDIENTE','PENDIENTE_CORREO_INSTITUCIONAL','PENDIENTE_FECHA','CLASIFICACION_LIMESURVEY','EN_VENTANA_DIARIA',
            'ES_REZAGADO','FECHA_EJECUCION','BRECHA_DIAS','EMAIL_PARA_LIMESURVEY','FUENTE_EMAIL_LIMESURVEY',
            'MATRICULAS_ELEGIBLES_RUT','FILAS_FUENTE_MATRICULA','FECHAS_MATRICULA_ORIGINALES',
            'MAIL_INST_ORIGINALES','FONOACTUAL_ORIGINALES','CONFLICTO_CORREO_INSTITUCIONAL']
        tracking = plan.missing[original + derived].copy()
        with pd.ExcelWriter(target, engine='openpyxl') as writer:
            tracking.to_excel(writer, sheet_name='Pendientes LimeSurvey', index=False)
            if not plan.signature.empty:
                extra = ['TOKEN','PENDIENTE_FIRMA','PENDIENTE_CORREO_INSTITUCIONAL','EN_UNIVERSO_ELEGIBLE',
                         'ESTADO_CORREO','MOTIVO_PENDIENTE','FECHA_EJECUCION','BRECHA_DIAS']
                plan.signature[original + extra].to_excel(writer, sheet_name='Pendientes firma', index=False)
            pd.DataFrame(list(plan.counts.items()), columns=['Concepto','Total']).to_excel(writer, sheet_name='Conciliacion', index=False)
            for sheet in writer.sheets.values():
                sheet.freeze_panes = 'A2'
                sheet.auto_filter.ref = sheet.dimensions
                for column in sheet.columns:
                    name = str(column[0].value or '')
                    sheet.column_dimensions[column[0].column_letter].width = min(48, max(16, len(name)+2))
        outputs['tracking'] = str(target)
    if not plan.pending_email.empty:
        error = InstitutionalEmailError(plan.pending_email, plan.columns, 'correo pendiente; no exportable')
        outputs['private_email_audit'] = str(write_private_email_audit(error, matricula, sources, plan.counts))
        print(f'[CORREOS][ADVERTENCIA] {len(plan.pending_email)} pendientes de correo; la ejecucion continua.', flush=True)
    state = {'policy':POLICY,'counts':plan.counts,'window':list(map(str,plan.window)),
             'email_source':'Mail_Inst','personal_email_fallback_allowed':False,'outputs':outputs}
    path = runtrace.output_path(f'ESTADO_INCORPORACION_{suffix}.json', audit=True)
    path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for key,value in plan.counts.items():
        print(f'[INCORPORACION] {key}={value}', flush=True)
    return outputs
