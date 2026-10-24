"""Publish the 2027 P1 communication and internal evidence in distinct folders."""
from datetime import date
import json
import os
from pathlib import Path

import pandas as pd
from caracterizacion_financiamiento import CODIGOS_FINANCIAMIENTO_G01Q19, DETALLES_FINANCIAMIENTO_G01Q19
from caracterizacion_sedes_2027 import sede_distribution, CATALOG
import caracterizacion_runtime as rt

ROOT = Path(__file__).resolve().parent
REFERENCE = Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/0_caracterizacion/2026-07-15/2026_P2_172021_HITO4C_OK/02_SALIDAS/Informe_Categorias_2026_P2_20260715.docx')
REFERENCE_SHA256 = '9f520a6b5f984b93c0c3eb6772d245eb5263c2aa1b2b125832170b3ce9380453'


def cutoff_date():
    value = os.environ.get('FECHA_REFERENCIA_PROCESO', '').strip()
    return date.fromisoformat(value) if value else rt.now_scl().date()


def build_context(plan, namespace=None, *, responses_available=False, reference_path=None):
    ns = namespace or {}
    target = ns.get('df_vigentes', plan.eligible)
    if set(target.get('_token_match', target.get('TOKEN', pd.Series(dtype=str)))) != set(plan.eligible['TOKEN']):
        raise ValueError('El informe no comparte el universo objetivo del plan de incorporacion.')
    if len(target) != len(plan.eligible) or not plan.eligible['TOKEN'].is_unique:
        raise ValueError('El informe debe contar una sola vez cada RUT.')
    states = target.get('Responden', pd.Series('NO', index=target.index)).fillna('NO').astype(str).str.upper()
    participation = {'eligible':len(target),'complete':int(states.eq('SI').sum()),
        'incomplete':int(states.eq('INCOMPLETO').sum()),'not_started':int(states.eq('NO').sum())}
    if sum(participation[key] for key in ['complete','incomplete','not_started']) != len(target):
        raise ValueError('Estado de respuesta desconocido en el universo del informe.')
    if not responses_available:
        participation.update(complete=0,incomplete=0,not_started=len(target))
    jornada_column = plan.columns.get('JORNADA')
    jornadas = target[jornada_column].fillna('').astype(str).str.strip().str.upper() if jornada_column else pd.Series('SIN_DATO',index=target.index)
    labels = {'O':'Online','V':'Vespertina','D':'Diurna','':'Sin dato','SIN_DATO':'Sin dato'}
    distributions = [{'jornada':labels.get(key,key),'total':int(total)} for key,total in sorted(jornadas.value_counts().items())]
    sedes = sede_distribution(target, plan.columns.get('SEDE','SEDE'))
    from caracterizacion_seguimiento_opciones_2027 import prepare_followup
    followup = prepare_followup(ns,plan,responses_available)
    categories, financing = [], []
    for metric in followup['metrics']:
        item = {'categoria':metric['category'],'codigo':metric['column'],'detalle':metric['label'],
                'total':metric['total'],'today':metric['today'],'state':metric['state'],
                'question':metric['question'],'answer_code':metric['answer_code']}
        (financing if metric['category']=='Financiamiento' else categories).append(item)
    detail = plan.trajectory_detail
    excluded_keys = set(detail.loc[detail['TIENE_TRAYECTORIA_PREVIA'] & detail['CANDIDATO_FILTROS_OPERATIVOS'],'TOKEN'])
    # Restrict the antecedent summary to candidates that passed pre-existing filters.
    before_keys = set(plan.eligible['TOKEN']) | excluded_keys
    evidence = plan.trajectory_evidence
    prior_keys = excluded_keys - set(plan.eligible['TOKEN'])
    summary = []
    if not evidence.empty:
        valid = evidence.loc[evidence['ANTECEDENTE_VALIDO'] & evidence['TOKEN'].isin(prior_keys)]
        for label,group in valid.groupby('CLASIFICACION_ANTECEDENTE'):
            summary.append({'clasificacion':str(label),'total':int(group['TOKEN'].nunique())})
    trajectory = {'candidates_before':len(before_keys),
        'first_entry':len(plan.eligible),'prior_trajectory':len(prior_keys),
        'technical_duplicates':int(plan.trajectory_summary.get('DUPLICADOS_TECNICOS_ANTECEDENTES',0)),
        'registered_excluded':len(prior_keys & set(plan.current_tokens)),
        'unregistered_excluded':len(prior_keys - set(plan.current_tokens))}
    context = {'year':2027,'period':1,'cutoff':plan.today,'counts':plan.counts,'window':plan.window,
        'participation':participation,'jornadas':distributions,'sedes':sedes,'categories':categories,
        'financing':financing,'source_flags':{'responses_available':responses_available},
        'trajectory':trajectory,'trajectory_summary':summary,
        'daily_response_rule':followup['date_rule'],'monitoring_policy':'SEGUIMIENTO_OPCIONES_2027_P1-v1'}
    historical_responses = ns.get('RESPUESTAS_HISTORICAS_2027',pd.DataFrame())
    if responses_available and not historical_responses.empty:
        response_states = historical_responses.set_index('_token_norm')['estado_respuesta'].to_dict()
        before_states = pd.Series(sorted(before_keys),dtype=str).map(response_states).fillna('NO')
        context['participation_before'] = {'eligible':len(before_keys),'complete':int(before_states.eq('SI').sum()),
            'incomplete':int(before_states.eq('INCOMPLETO').sum()),'not_started':int(before_states.eq('NO').sum())}
    context['sources'] = {key.replace('RUTA_','').title():value for key,value in os.environ.items()
                          if key in ('RUTA_MATRICULA','RUTA_INSCRITOS','RUTA_RESULTADOS')}
    reference = Path(reference_path or os.environ.get('CARACTERIZACION_PLANTILLA_CORREO', str(REFERENCE)))
    if not reference.is_file():
        raise ValueError(f'No existe la referencia gobernada de estilo: {reference}')
    if reference_path is None and rt.sha256_file(reference) != REFERENCE_SHA256:
        raise ValueError('Cambio la referencia de estilo; no sustituirla silenciosamente.')
    context['reference_path'] = str(reference)
    return context


def publish_trajectory_analysis(plan):
    from caracterizacion_catalogo_sies_2027 import enrich_frame
    name = f'Trayectorias_institucionales_2027_P1_{plan.today:%Y%m%d}.xlsx'
    target = rt.analysis_path(name)
    detail = plan.trajectory_detail.copy()
    detail['EN_UNIVERSO_OBJETIVO'] = detail.index.isin(plan.eligible_enrollments.index)
    detail['PERSONA_EN_UNIVERSO_OBJETIVO'] = detail['TOKEN'].isin(set(plan.eligible['TOKEN']))
    detail['EN_TOKENS_ACTUALES'] = detail['TOKEN'].isin(set(plan.current_tokens))
    detail, sies_audit = enrich_frame(detail, anio=2027, periodo=1)
    # A token can exist for a previous-trajectory case too: the caller adds its current inventory below.
    with pd.ExcelWriter(target,engine='openpyxl') as writer:
        detail.to_excel(writer,sheet_name='Matricula periodo',index=False)
        if not plan.trajectory_evidence.empty:
            plan.trajectory_evidence.to_excel(writer,sheet_name='Antecedentes',index=False)
        pd.DataFrame(list(plan.trajectory_summary.items()),columns=['Concepto','Valor']).to_excel(writer,sheet_name='Resumen',index=False)
        coverage = [('Codigo SIES', state, count) for state,count in sies_audit['estados_codigo_sies'].items()]
        coverage += [('Modalidad', state, count) for state,count in sies_audit['estados_modalidad'].items()]
        pd.DataFrame(coverage, columns=['Control','Estado','Registros']).to_excel(writer,sheet_name='Cobertura SIES',index=False)
        for sheet in writer.sheets.values():
            sheet.freeze_panes='A2'
            sheet.auto_filter.ref=sheet.dimensions
    audit_path = rt.output_path(f'AUDITORIA_CATALOGO_SIES_2027_P1_{plan.today:%Y%m%d}.json', audit=True)
    audit_path.write_text(json.dumps(sies_audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'[CATALOGO SIES 2027] Registros={len(detail)} | codigo_sies={sies_audit["estados_codigo_sies"]} | '
          f'modalidad={sies_audit["estados_modalidad"]} | '
          f'version={sies_audit["version"]}. Sin cambios de elegibilidad.', flush=True)
    return str(target)


def publish_reports(plan, namespace=None, *, responses_available=False, reference_path=None):
    from caracterizacion_reportes_2027 import build_email_report, build_internal_report, extract_ordered_document, ordered_document_text
    context = build_context(plan,namespace,responses_available=responses_available,reference_path=reference_path)
    suffix=f'2027_P1_{plan.today:%Y%m%d}'
    email=build_email_report(context)
    internal=build_internal_report(context,plan)
    email_path=rt.output_path(f'Informe_Categorias_{suffix}.docx',audit=False)
    internal_path=rt.analysis_path(f'Estado_incorporacion_LimeSurvey_{suffix}.docx')
    email.save(email_path); internal.save(internal_path)
    trajectory_path=publish_trajectory_analysis(plan)
    extraction={'communication':extract_ordered_document(email),'internal':extract_ordered_document(internal)}
    extraction_path=rt.output_path(f'EXTRACCION_WORDS_{suffix}.json',audit=True)
    extraction_path.write_text(json.dumps(extraction,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for role,doc in [('CORREO',email),('INTERNO',internal)]:
        rt.output_path(f'CONTENIDO_WORD_{role}_{suffix}.txt',audit=True).write_text(ordered_document_text(doc)+'\n',encoding='utf-8')
    previous = plan.counts['CANDIDATOS_ANTES_TRAYECTORIA']
    identities = {
        'candidates_partition':{'left':previous,'right':len(plan.eligible_enrollments)+plan.counts['EXCLUIDOS_TRAYECTORIA_PREVIA']},
        'enrollments_people':{'left':len(plan.eligible_enrollments),'right':len(plan.eligible)+plan.counts['FILAS_ADICIONALES_POR_RUT']},
        'target_tokens':{'left':len(plan.eligible),'right':plan.counts['VIGENTES_CON_TOKEN']+len(plan.missing)},
        'missing_email':{'left':len(plan.missing),'right':len(plan.ready)+len(plan.pending_email)},
        'valid_email_dates':{'left':len(plan.ready),'right':len(plan.daily)+len(plan.backlog)+len(plan.temporal)},
        'response_states':{'left':len(plan.eligible),'right':sum(context['participation'][key] for key in ['complete','incomplete','not_started'])},
        'sedes':{'left':len(plan.eligible),'right':sum(row['total'] for row in context['sedes'])},
        'jornadas':{'left':len(plan.eligible),'right':sum(row['total'] for row in context['jornadas'])}}
    for check in identities.values():
        check['ok']=check['left']==check['right']
    if not all(check['ok'] for check in identities.values()):
        raise ValueError('Fallo una conciliacion agregada del informe.')
    aggregate={'policy':'COMUNICACION_ANALISIS_AUDITORIA_2027_P1-v1','year':2027,'period':1,
        'cutoff':str(plan.today),'window':list(map(str,plan.window)),'counts':plan.counts,
        'trajectory':context['trajectory'],'trajectory_antecedents_non_additive':context['trajectory_summary'],
        'participation':context['participation'],'participation_before':context.get('participation_before'), 'jornadas':context['jornadas'],'sedes':context['sedes'],
        'financing':context['financing'] if responses_available else [],'categories':context['categories'],
        'checks':identities,'personal_data_included':False,
        'daily_response_rule':context['daily_response_rule'],'monitoring_policy':context['monitoring_policy'],
        'sede_catalog':{'path':str(CATALOG),'sha256':rt.sha256_file(CATALOG)},
        'style_reference':{'path':context['reference_path'],'sha256':rt.sha256_file(Path(context['reference_path']))},
        'outputs':{'email_word':str(email_path),'internal_word':str(internal_path),'trajectory_excel':trajectory_path}}
    path=rt.output_path(f'CONCILIACION_AGREGADA_{suffix}.json',audit=True)
    path.write_text(json.dumps(aggregate,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'[REPORTES 2027] Correo: {email_path}; analisis interno: {internal_path}',flush=True)
    return str(email_path),str(internal_path),str(path)
