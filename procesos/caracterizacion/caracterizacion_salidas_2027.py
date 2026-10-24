"""Case-dependent operational delivery without touching the frozen reference."""
import caracterizacion_runtime as rt


def publish_eliminated_window(namespace):
    context = rt.get_context()
    if (context.anio,context.periodo) != (2027,1):
        raise ValueError('La salida condicional de eliminados es exclusiva de 2027 P1.')
    frame = namespace['df_actualmente_eliminados_matriculados_en_ventana']
    cases = len(frame)
    if cases != namespace['n_actualmente_eliminados_matriculados_en_ventana']:
        raise ValueError('El detalle de eliminados en ventana no concilia con su total.')
    name = f'Actualmente_eliminados_matricula_en_ventana_2027_P1_{namespace["hoy_str"]}.xlsx'
    purpose = 'Eliminados actuales cuya FECHAMATRICULA pertenece a la ventana; no es fecha de eliminacion.'
    temporal = (f'ventana={namespace["desde_b3"]} a {namespace["hasta_b3"]} | '
                'fuente=FECHAMATRICULA | advertencia=NO_ES_FECHA_ELIMINACION')
    if cases:
        target = rt.output_path(name,audit=False)
        namespace['exportar_excel'](frame,str(target),skip_if_empty=True)
        rt.record_conditional_output(target,rows=cases,columns=len(frame.columns),purpose=purpose)
        namespace['ruta_eliminados_matricula_ventana'] = str(target)
        print(f'[ELIMINADOS EN VENTANA] Archivo generado: {name} | casos={cases} | {temporal}',flush=True)
    else:
        rt.record_conditional_output(context.output_dir/name,rows=0,columns=len(frame.columns),purpose=purpose)
        namespace['ruta_eliminados_matricula_ventana'] = None
        print(f'[ELIMINADOS EN VENTANA] OMITIDO_SIN_CASOS: {name} | casos=0 | {temporal}',flush=True)
    namespace['nombre_eliminados_matricula_ventana'] = name
    return namespace['ruta_eliminados_matricula_ventana']
