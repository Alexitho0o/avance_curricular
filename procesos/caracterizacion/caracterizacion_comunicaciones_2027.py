"""Communications sede partition for the independent 2027 P1 process."""
import json
from pathlib import Path

import pandas as pd

import caracterizacion_runtime as rt
from caracterizacion_sedes_2027 import communication_sede
from caracterizacion_seguimiento_opciones_2027 import export_artifact_workbook

ROOT = Path(__file__).resolve().parent
POLICY = 'ENTREGAS_COMUNICACIONES_TRES_SEDES_2027_P1-v1'
SEDE_FILES = {'SANTIAGO':'Santiago', 'CONCEPCION':'Concepcion', 'PATAGONIA':'Patagonia'}


def normalize_communications(frame, raw_sedes):
    if not frame.index.equals(raw_sedes.index):
        raise ValueError('La columna SEDE fuente no se alinea con comunicaciones.')
    result = frame.copy()
    result['SEDE'] = raw_sedes.map(communication_sede)
    return result


def partition_communications(frame):
    required = {'token', 'SEDE', 'NUEVO'}
    if not required.issubset(frame.columns):
        raise ValueError('Faltan token, SEDE o NUEVO en comunicaciones.')
    keys = frame['token'].fillna('').astype(str).str.strip()
    if keys.eq('').any() or keys.duplicated().any():
        raise ValueError('La base general de comunicaciones debe tener un token unico por persona.')
    partitions = {sede:frame.loc[frame['SEDE'].eq(sede)].copy() for sede in SEDE_FILES}
    unknown = frame.loc[~frame['SEDE'].isin(SEDE_FILES)].copy()
    total = sum(len(part) for part in partitions.values()) + len(unknown)
    if total != len(frame):
        raise ValueError('Las sedes de comunicaciones no concilian con la base general.')
    return partitions, unknown


def patagonia_payload(frame, *, year, period, source):
    if not frame['SEDE'].eq('PATAGONIA').all():
        raise ValueError('El archivo Patagonia contiene otra sede.')
    # Match the existing BD schema, including the distinct personal/institutional emails.
    headers = [str(c).upper() if c != 'Email' else 'EMAIL__2' for c in frame.columns]
    if len(set(headers)) != len(headers):
        raise ValueError('Encabezados ambiguos en comunicaciones.')
    return {'title':f'BD COMUNICACIONES PATAGONIA {year} P{period}',
            'headers':headers, 'rows':json.loads(frame.to_json(orient='values',force_ascii=False)),
            'widths':[27,28,24,41,51,13,11,12,10,60,16],
            'source':source, 'policy':POLICY}


def publish_communications(namespace):
    context = rt.get_context()
    if (context.anio, context.periodo) != (2027,1):
        raise ValueError('Comunicaciones de tres sedes es exclusivo de 2027 P1.')
    frame = namespace['df_bd_export']
    partitions, unknown = partition_communications(frame)
    stamp = namespace['str_yyyymmdd_scl']()
    outputs = {}
    namespace['df_bd_total'] = frame.copy()
    for sede, variable in [('SANTIAGO','df_bd_stgo'),('CONCEPCION','df_bd_conce'),('PATAGONIA','df_bd_ptg')]:
        namespace[variable] = partitions[sede]
    exports = [('GENERAL', frame)] + list(partitions.items())
    for sede, subset in exports:
        label = '' if sede == 'GENERAL' else SEDE_FILES[sede] + '_'
        name = f'BD_Comunicaciones_{label}2027_P1_{stamp}.xlsx'
        purpose = 'Base general de comunicaciones.' if sede == 'GENERAL' else f'Comunicaciones de {sede}.'
        if subset.empty:
            rt.record_conditional_output(context.output_dir/name,rows=0,columns=len(subset.columns),purpose=purpose)
            print(f'[COMUNICACIONES] No se genera {name}: 0 personas.',flush=True)
            continue
        if sede == 'PATAGONIA':
            evidence = ROOT/'.local/comunicaciones_2027'/context.run_dir.name
            payload = patagonia_payload(subset,year=2027,period=1,
                                        source=Path(namespace['ruta_matricula']).name)
            output = rt.output_path(name,audit=False)
            outputs[sede] = export_artifact_workbook(payload,output,evidence,
                builder_name='exportar_comunicaciones_sede_2027.mjs')
        else:
            title = 'BD COMUNICACIONES' + ('' if sede == 'GENERAL' else ' '+sede) + ' 2027 P1'
            namespace['_exportar_bd_comunicaciones'](subset,name,title)
            outputs[sede] = str(context.output_dir/name)
        rt.record_conditional_output(outputs[sede],rows=len(subset),columns=len(subset.columns),purpose=purpose)
        print(f'[COMUNICACIONES] Archivo: {name} | personas={len(subset)}',flush=True)
    control = {'policy':POLICY,'general':len(frame),
               'sedes':{sede:len(part) for sede,part in partitions.items()},
               'codigos_no_gobernados':{str(k):int(v) for k,v in unknown.SEDE.value_counts().items()},
               'sin_sede_gobernada':len(unknown), 'diferencia':0,
               'personal_data_included':False,'outputs':outputs}
    audit = rt.output_path(f'CONTROL_COMUNICACIONES_SEDES_2027_P1_{stamp}.json',audit=True)
    audit.write_text(json.dumps(control,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('[COMUNICACIONES][CONCILIACION] '
          f'general={len(frame)} | Santiago={len(partitions["SANTIAGO"])} | '
          f'Concepcion={len(partitions["CONCEPCION"])} | Patagonia={len(partitions["PATAGONIA"])} | '
          f'sede_por_revisar={len(unknown)} | diferencia=0',flush=True)
    namespace['COMUNICACIONES_SEDES_2027'] = control
    namespace['log_avance']('BLOQUE 5 - comunicaciones general, Santiago, Concepcion y Patagonia en 02_SALIDAS')
    return outputs
