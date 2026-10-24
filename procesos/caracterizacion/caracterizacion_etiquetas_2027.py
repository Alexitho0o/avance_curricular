"""Separate enrollment timing, institutional trajectory and response tracking."""
import json

import pandas as pd

from caracterizacion_pendientes import normalizar_estado_respuesta
import caracterizacion_runtime as rt

POLICY = 'CLARIDAD_CONTROLES_2027_P1-v1'


def matricula_audit_summary(legacy):
    result = dict(legacy)
    result['tipo_control_matricula'] = (
        'COHORTE_Y_VENTANA_MATRICULA' if legacy['usar_ventana'] else 'COHORTE_Y_FECHA_VALIDA')
    mapping = {'de_los_cuales_nuevos':'cumplen_control_matricula',
               'antiguos':'no_cumplen_control_matricula',
               'suma_nuevos_antiguos_sin_clasificar':'suma_control_matricula'}
    for old, new in mapping.items():
        result[new] = result.pop(old)
    return result


def format_matricula_audit(legacy):
    row = matricula_audit_summary(legacy)
    return (
        f'[CONTROL MATRICULA] fila={row["nombre_fila"]} | total={row["total_fila"]} | '
        f'control={row["tipo_control_matricula"]} | '
        f'cumplen_control={row["cumplen_control_matricula"]} | '
        f'no_cumplen_control={row["no_cumplen_control_matricula"]} | '
        f'fuera_ventana={row["conteo_fuera_de_ventana"]} | '
        f'fuera_cohorte={row["conteo_anio_ing_ori_distinto"]} | '
        f'sin_clasificar={row["sin_clasificar"]} | diferencia={row["diferencia_vs_total"]}')


def matricula_audit_tables(summaries, details):
    summary = pd.DataFrame([matricula_audit_summary(row) for row in summaries])
    detail = pd.DataFrame(details).rename(columns={
        'ES_NUEVO_COHORTE_OFICIAL':'CUMPLE_COHORTE_Y_FECHA_VALIDA',
        'ES_NUEVO_EN_VENTANA':'CUMPLE_COHORTE_Y_VENTANA'})
    if 'MOTIVO_CLASIFICACION' in detail:
        detail['MOTIVO_CLASIFICACION'] = detail['MOTIVO_CLASIFICACION'].replace(
            {'ANTIGUO_ANIO_ING_ORI_DISTINTO':'FUERA_COHORTE_ANIO_INGRESO'})
    return summary, detail


def export_matricula_audit(namespace):
    summary, detail = matricula_audit_tables(
        namespace['AUDIT_NUEVOS_RESUMEN'], namespace['AUDIT_NUEVOS_DETALLE'])
    stamp = namespace['FECHA_REFERENCIA_PROCESO'].strftime('%Y%m%d')
    filename = f'AUDITORIA_CONTROL_MATRICULA_2027_P1_{stamp}.xlsx'
    path = rt.output_path(filename, audit=True)
    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        summary.to_excel(writer, sheet_name='Resumen', index=False)
        detail.to_excel(writer, sheet_name='Detalle', index=False)
    print(f'[CONTROL MATRICULA] archivo={path}; no clasifica trayectoria institucional.', flush=True)
    return str(path)


def response_tracking_frames(frame, column='Responden'):
    if column not in frame:
        raise ValueError('Falta el estado canonico de respuesta para el seguimiento.')
    states = frame[column].map(normalizar_estado_respuesta)
    pending_mask = states.isin({'NO','INCOMPLETO',''})
    review_mask = ~states.isin({'SI','NO','INCOMPLETO',''})
    summary = {
        'ELEGIBLES_TOTALES':len(frame),
        'RESPUESTAS_COMPLETAS':int(states.eq('SI').sum()),
        'RESPUESTAS_INCOMPLETAS':int(states.eq('INCOMPLETO').sum()),
        'SIN_RESPUESTA':int(states.isin({'NO',''}).sum()),
        'ESTADOS_POR_REVISAR':int(review_mask.sum()),
        'SEGUIMIENTO_TOTAL':len(frame),
        'PENDIENTES_RESPUESTA':int(pending_mask.sum()),
    }
    if summary['ELEGIBLES_TOTALES'] != (
        summary['RESPUESTAS_COMPLETAS'] + summary['PENDIENTES_RESPUESTA'] + summary['ESTADOS_POR_REVISAR']):
        raise ValueError('No concilian seguimiento, respuestas completas y pendientes.')
    return frame.copy(), frame.loc[pending_mask].copy(), summary


def publish_response_tracking(frame, stamp, write_frame):
    """Reuse each flow's existing Excel exporter without changing the target."""
    tracking, pending, summary = response_tracking_frames(frame)
    outputs = {'seguimiento':write_frame(tracking,
        f'Seguimiento_respuestas_encuesta_2027_P1_{stamp}.xlsx',
        'Seguimiento', 'SEGUIMIENTO TOTAL DE RESPUESTAS 2027 P1')}
    if not pending.empty:
        outputs['pendientes_respuesta'] = write_frame(pending,
            f'Estudiantes_pendientes_respuesta_2027_P1_{stamp}.xlsx',
            'Pendientes respuesta', 'ESTUDIANTES PENDIENTES DE RESPUESTA 2027 P1')
    record = {'policy':POLICY, 'counts':summary, 'outputs':{key:str(path) for key,path in outputs.items()},
              'rule':'Seguimiento conserva todos. Pendientes respuesta incluye NO, INCOMPLETO y vacios; SI queda fuera. Desconocidos quedan en seguimiento para revisar. No es una lista de incorporacion ni envio automatico.',
              'personal_data_included':False}
    path = rt.output_path(f'CONTROL_SEGUIMIENTO_RESPUESTAS_2027_P1_{stamp}.json', audit=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('[SEGUIMIENTO RESPUESTAS] '+ ' | '.join(f'{key}={value}' for key,value in summary.items()), flush=True)
    if summary['ESTADOS_POR_REVISAR']:
        print('[SEGUIMIENTO RESPUESTAS][WARN] Estados desconocidos conservados solo en el control total; revisar antes de contactar.', flush=True)
    return record


def export_response_tracking(namespace):
    def write_frame(frame, filename, sheet, title):
        return namespace['exportar_excel_rico'](frame, filename, hoja=sheet, titulo=title,
            freeze_panes='A2', crear_tabla=True, auto_filtro=True, auto_width=True,
            center_cells=False, columnas_centradas=['RUT','TOKEN','RESPONDEN'],
            columnas_izquierda=['FIRSTNAME','LASTNAME','EMAIL','FONO'],
            columnas_entero=[], columnas_decimal=[], columnas_porcentaje=[],
            columnas_fecha=[], columnas_datetime=[], skip_if_empty=False, uppercase_header=True)
    record = publish_response_tracking(namespace['df_export'], namespace['str_yyyymmdd_scl'](), write_frame)
    namespace['SEGUIMIENTO_RESPUESTAS_2027'] = record
    return record
