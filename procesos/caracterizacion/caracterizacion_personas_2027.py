"""Separate survey people from eligible enrollment rows, only for 2027 P1.

No enrollment is selected as a primary career. Distinct values remain visible;
the untouched enrollment table is the authoritative source for career analysis.
"""
import pandas as pd

POLICY = 'PERSONAS_MATRICULAS_2027_P1-v1'


def _values(series):
    return sorted({str(v).strip() for v in series if pd.notna(v) and str(v).strip()})


def person_view(enrollments, columns, email_validator):
    if 'TOKEN' not in enrollments or enrollments['TOKEN'].fillna('').eq('').any():
        raise ValueError('Falta una clave RUT valida para construir personas.')
    rows, indices = [], []
    for token, group in enrollments.groupby('TOKEN', sort=False):
        row = {}
        for column in group.columns:
            values = group[column].drop_duplicates()
            row[column] = values.iloc[0] if len(values) == 1 else ' | '.join(_values(group[column]))
        # RUT is an identity, never a concatenation of its formatted variants.
        row[columns['RUT']] = sorted(_values(group[columns['RUT']]))[0]
        dates = group['FECHAMATRICULA_DT'].dropna()
        first_date = min(dates) if len(dates) else pd.NaT
        row['FECHAMATRICULA_DT'] = first_date
        if len(group) > 1:
            row[columns['FECHAMATRICULA']] = first_date.strftime('%d-%m-%Y') if pd.notna(first_date) else ''
        valid = email_validator(group[columns['MAILINST']])
        emails = _values(group.loc[valid, columns['MAILINST']].str.strip().str.lower())
        row['CONFLICTO_CORREO_INSTITUCIONAL'] = len(emails) > 1
        if len(group) > 1:
            row[columns['MAILINST']] = (emails[0] if len(emails) == 1 else
                                       ('' if len(emails) > 1 else ' | '.join(_values(group[columns['MAILINST']]))))
        row['MATRICULAS_ELEGIBLES_RUT'] = len(group)
        row['FILAS_FUENTE_MATRICULA'] = ' | '.join(str(int(i) + 2) for i in sorted(group.index))
        row['FECHAS_MATRICULA_ORIGINALES'] = ' | '.join(_values(group[columns['FECHAMATRICULA']]))
        row['MAIL_INST_ORIGINALES'] = ' | '.join(_values(group[columns['MAILINST']]))
        phone_column = columns.get('FONOACTUAL')
        phones = _values(group[phone_column]) if phone_column else []
        row['FONOACTUAL_ORIGINALES'] = ' | '.join(phones)
        # Legacy phone cleaning removes separators; never concatenate two phones.
        if phone_column and len(phones) > 1:
            row[phone_column] = ''
        row['POLITICA_UNIDAD_PERSONA'] = POLICY
        rows.append(row)
        indices.append(group.index.min())
    extra = ['CONFLICTO_CORREO_INSTITUCIONAL','MATRICULAS_ELEGIBLES_RUT','FILAS_FUENTE_MATRICULA',
             'FECHAS_MATRICULA_ORIGINALES','MAIL_INST_ORIGINALES','FONOACTUAL_ORIGINALES','POLITICA_UNIDAD_PERSONA']
    result = pd.DataFrame(rows, index=indices, columns=list(enrollments.columns) +
                          [name for name in extra if name not in enrollments])
    result.attrs = enrollments.attrs.copy()
    result['CONFLICTO_CORREO_INSTITUCIONAL'] = result['CONFLICTO_CORREO_INSTITUCIONAL'].astype(bool)
    result['MATRICULAS_ELEGIBLES_RUT'] = result['MATRICULAS_ELEGIBLES_RUT'].astype(int)
    if not result['TOKEN'].is_unique or result['MATRICULAS_ELEGIBLES_RUT'].sum() != len(enrollments):
        raise ValueError('No concilian personas y matriculas elegibles.')
    return result


def publish_multiple_enrollments(plan):
    import caracterizacion_runtime as rt
    repeated = plan.eligible.loc[plan.eligible['MATRICULAS_ELEGIBLES_RUT'].gt(1)]
    detail = plan.eligible_enrollments.loc[plan.eligible_enrollments['TOKEN'].isin(repeated['TOKEN'])].copy()
    detail['FILA_EXCEL_FUENTE'] = detail.index + 2
    detail['EN_LIMESURVEY'] = detail['TOKEN'].isin(plan.current_tokens)
    name = f'Conflictos_tokens_duplicados_vigentes_2027_P1_{plan.today:%Y%m%d}.xlsx'
    path = rt.output_path(name, audit=False)
    if not detail.empty:
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            detail.to_excel(writer, sheet_name='Conflictos_Vigentes', index=False)
            repeated.to_excel(writer, sheet_name='Personas', index=False)
            pd.DataFrame(list(plan.counts.items()), columns=['Concepto','Total']).to_excel(writer, sheet_name='Conciliacion', index=False)
            pd.DataFrame({'Regla':[
                POLICY, 'Una persona por TOKEN; todas las matriculas elegibles se conservan.',
                'El nombre historico del archivo no significa tokens duplicados en LimeSurvey.',
                'Sin carrera principal: valores distintos separados por |.',
                'Fecha operativa: la menor fecha valida entre matriculas elegibles.',
                'Correo: un unico Mail_Inst valido; varios distintos dejan solo a esa persona pendiente.',
                'Filas fuente: numero de fila Excel, incluida la cabecera.',
            ]}).to_excel(writer, sheet_name='Reglas', index=False)
            for sheet in writer.sheets.values():
                sheet.freeze_panes = 'A2'
                sheet.auto_filter.ref = sheet.dimensions
                for col in sheet.columns:
                    sheet.column_dimensions[col[0].column_letter].width = min(50,max(16,len(str(col[0].value))+2))
    if rt.ACTIVE_CONTEXT is not None:
        rt.record_conditional_output(path, rows=len(detail), columns=len(detail.columns),
            purpose='Seguimiento de RUT con varias matriculas elegibles; personas contadas una sola vez.')
    print(f'[MULTIMATRICULA] personas={len(plan.eligible)} | matriculas={len(plan.eligible_enrollments)} | '
          f'RUT con varias matriculas={len(repeated)} | filas seguimiento={len(detail)} | '
          + (f'archivo={path}' if len(detail) else 'OMITIDO_SIN_CASOS'), flush=True)
    return str(path) if len(detail) else None
