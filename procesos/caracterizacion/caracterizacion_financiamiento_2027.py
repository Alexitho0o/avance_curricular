"""2027 P1 adapter over the byte-identical frozen 2026 reference.

Exact, checked anchors adapt incorporation, reports and labels in memory.
A changed reference/anchor is a structural blocking error.
"""
import hashlib
import json
import os
from pathlib import Path
import sys

from caracterizacion_incorporacion import build_plan, publish_plan, POLICY
from caracterizacion_comunicacion_2027 import cutoff_date
from caracterizacion_sin_respuestas import shared_operational_rules
import caracterizacion_runtime as runtrace

ROOT = Path(__file__).resolve().parent


def filter_characterization_master(namespace):
    from caracterizacion_trayectorias_2027 import classify_trajectories
    detail, summary, evidence = classify_trajectories(namespace['df_matricula'],2027,1)
    master = namespace['df_universo_maestro']
    previous = detail['TIENE_TRAYECTORIA_PREVIA'].reindex(master.index,fill_value=False).astype(bool)
    filtered = master.loc[~previous].copy()
    namespace['TRAYECTORIAS_2027_ANTES'] = master.copy()
    namespace['TRAYECTORIAS_2027_DETALLE'] = detail
    namespace['TRAYECTORIAS_2027_EVIDENCIA'] = evidence
    namespace['AUDITORIA_UNIVERSO'].registrar_etapa('primer_ingreso_institucional_2027',master,filtered,
        key_cols=[master.columns[namespace['IDX_CODCLI']],master.columns[namespace['IDX_RUT']]],
        motivo='Histórico completo: excluye antecedente válido anterior en otra carrera; conserva matrícula en análisis.')
    print(f'[TRAYECTORIA 2027] maestro antes={len(master)}; después={len(filtered)}; excluidos={int(previous.sum())}',flush=True)
    return filtered


def publish_communication(namespace):
    from caracterizacion_comunicacion_2027 import publish_reports
    path,internal,aggregate = publish_reports(namespace['INCORPORACION_PLAN'],namespace,responses_available=True)
    namespace['INFORME_INTERNO_2027'] = internal
    namespace['CONCILIACION_AGREGADA_2027'] = aggregate
    return path


def prepare_incorporation(namespace):
    plan = namespace.get('INCORPORACION_PLAN')
    if plan is None:
        plan = build_plan(namespace['df_matricula'], namespace['df_inscritos'], 2027, 1,
                          cutoff_date(), shared_operational_rules())
    actual = set(namespace['df_vigentes']['_token_match'])
    if actual != set(plan.eligible['TOKEN']) or len(namespace['df_vigentes']) != len(plan.eligible):
        raise ValueError('La elegibilidad del adaptador no concilia con el universo vigente del pipeline.')
    namespace['INCORPORACION_PLAN'] = plan
    return plan


def prepare_person_universe(namespace):
    from caracterizacion_personas_2027 import person_view
    from caracterizacion_sin_respuestas import institutional_email_valid
    rules = shared_operational_rules()
    plan = build_plan(namespace['df_matricula'], namespace['df_inscritos'], 2027, 1, cutoff_date(), rules)
    enrollments = namespace['df_vigentes'].copy()
    enrollments['TOKEN'] = enrollments[plan.columns['RUT']].map(rules['token_match_rut'])
    if enrollments['TOKEN'].value_counts().to_dict() != plan.eligible_enrollments['TOKEN'].value_counts().to_dict():
        raise ValueError('No concilian las matriculas elegibles del adaptador y del plan 2027.')
    people = person_view(enrollments, plan.columns, institutional_email_valid)
    namespace['df_matriculas_elegibles_2027'] = enrollments
    namespace['INCORPORACION_PLAN'] = plan
    namespace['n_conflictos_tokens_vigentes'] = plan.counts['RUT_MULTIMATRICULA']
    namespace['n_conflictos_filas_vigentes'] = plan.counts['FILAS_MULTIMATRICULA']
    return people


def publish_incorporation(namespace):
    plan = namespace['INCORPORACION_PLAN']
    if namespace['FECHA_REFERENCIA_PROCESO'] != plan.today or (
        namespace['VENTANA_INICIO_INFORME'], namespace['VENTANA_FIN_INFORME']) != plan.window:
        raise ValueError('La fecha/ventana del adaptador no concilia con el informe Word.')
    sources = {key:os.environ[key] for key in ('RUTA_MATRICULA','RUTA_INSCRITOS','RUTA_RESULTADOS')}
    outputs = publish_plan(plan, namespace['df_matricula'], sources)
    namespace['INCORPORACION_OUTPUTS'] = outputs
    candidates = namespace['df_nuevos_validos']
    daily = candidates.loc[candidates['token'].isin(set(plan.daily['TOKEN']))].copy()
    backlog = candidates.loc[candidates['token'].isin(set(plan.backlog['TOKEN']))].copy()
    namespace.update(
        df_nuevos_ventana_habil=daily, df_nuevos_acumulados_pendientes=backlog,
        df_nuevos_rezagados_limesurvey=backlog,
        n_nuevos=len(daily), n_nuevos_ventana_habil=len(daily), n_nuevos_acumulados=len(backlog),
        n_nuevos_pendientes_total=len(plan.missing), n_nuevos_rezagados_limesurvey=len(backlog),
        n_nuevos_otros_fuera_ventana_limesurvey=len(plan.temporal),
        max_dias_rezago_limesurvey=int(plan.backlog['BRECHA_DIAS'].max()) if not plan.backlog.empty else 0,
        nombre_nuevos_hoy=Path(outputs['daily']).name if 'daily' in outputs else 'NO_GENERADO_SIN_LISTOS',
        nombre_csv_nuevos_acumulados=Path(outputs['backlog']).name if 'backlog' in outputs else 'NO_GENERADO_SIN_LISTOS')


def adapted_source(source):
    """Fail closed on drift; do not mutate the reference file on disk."""
    replacements = [
        ('CONCILIACION_MATRICULA_TOKENS = conciliar_matricula_tokens(\n',
         'from caracterizacion_financiamiento_2027 import prepare_person_universe\n'
         'df_vigentes = prepare_person_universe(globals())\n'
         'CONCILIACION_MATRICULA_TOKENS = conciliar_matricula_tokens(\n'),
        ('columna_llave_estudiante=df_vigentes.columns[IDX_CODCLI],',
         'columna_llave_estudiante="TOKEN",'),
        ('df_word_base_oficial = _preparar_base_matricula_informe_word()',
         'df_word_base_oficial = df_vigentes.copy()'),
        ('_df_resultados_canonicos_conciliacion = df_resultados.copy()',
         '_df_resultados_canonicos_conciliacion = df_resultados.copy()\n'
         'RESPUESTAS_HISTORICAS_2027 = _df_resultados_canonicos_conciliacion.copy()'),
        ('df_nuevos["email"] = inst.where(inst.ne(""), pers)', 'df_nuevos["email"] = inst'),
        ('df_nuevos_validos = df_nuevos[~mascara_token_vacio].copy()',
         'from caracterizacion_financiamiento_2027 import prepare_incorporation, publish_incorporation\n'
         'INCORPORACION_PLAN = prepare_incorporation(globals())\n'
         '_ready_tokens_2027 = set(INCORPORACION_PLAN.daily["TOKEN"]) | set(INCORPORACION_PLAN.backlog["TOKEN"])\n'
         'df_nuevos_validos = df_nuevos.loc[df_nuevos["token"].isin(_ready_tokens_2027)].copy()'),
        ('df_universo_maestro = df_periodo_base[~mask_excluir_operativo].copy()',
         'df_universo_maestro = df_periodo_base[~mask_excluir_operativo].copy()\n'
         'from caracterizacion_financiamiento_2027 import filter_characterization_master\n'
         'df_universo_maestro = filter_characterization_master(globals())')]
    for original, replacement in replacements:
        if source.count(original) != 1:
            raise ValueError('Ancla de integracion 2027 inexistente o ambigua; revisar estructura del pipeline.')
        source = source.replace(original, replacement)
    start, end = '# 1.4 Conflictos internos\n', '# 1.5 Exportación vigentes + consolidado único de eliminados\n'
    if source.count(start) != 1 or source.count(end) != 1 or source.index(start) >= source.index(end):
        raise ValueError('Anclas de seguimiento multimatricula inexistentes o ambiguas.')
    source = (source[:source.index(start)] +
              '# 1.4 Seguimiento multimatricula publicado por el plan comun 2027.\n\n' + source[source.index(end):])
    start = 'nombre_eliminados_matricula_ventana = (\n'
    end = 'n_nuevos = int(len(df_nuevos_export)) if ('
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError('Anclas de eliminados en ventana inexistentes o ambiguas.')
    begin, finish = source.index(start), source.index(end)
    if begin >= finish:
        raise ValueError('Orden de anclas de eliminados en ventana invalido.')
    source = (source[:begin] + 'from caracterizacion_salidas_2027 import publish_eliminated_window\n'
        'publish_eliminated_window(globals())\n\n' + source[finish:])
    start = 'n_nuevos = int(len(df_nuevos_export)) if ('
    end = 'n_eliminados_totales = int(len(df_eliminados_reporte_total))'
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError('Anclas de exportacion 2027 inexistentes o ambiguas.')
    begin, finish = source.index(start), source.index(end)
    if begin >= finish:
        raise ValueError('Orden de anclas de exportacion 2027 invalido.')
    source = source[:begin] + 'publish_incorporation(globals())\n\n' + source[finish:]
    word_begin = 'doc = Document()\n\nintro = build_resumen_word_context('
    word_end = 'nombre_word = os.path.basename(ruta_word)'
    if source.count(word_begin)!=1 or source.count(word_end)!=1:
        raise ValueError('Anclas del Word 2027 inexistentes o ambiguas.')
    begin,finish = source.index(word_begin),source.index(word_end)
    source = (source[:begin] + 'from caracterizacion_financiamiento_2027 import publish_communication\n'
            'ruta_word = publish_communication(globals())\n' + source[finish:])
    blocks = [
        ('    print(\n        "[AUDIT INFORME_CATEGORIAS NUEVOS] "\n', '    if diferencia != 0:\n',
         '    from caracterizacion_etiquetas_2027 import format_matricula_audit\n'
         '    print(format_matricula_audit(resumen), flush=True)\n'),
        ('def _exportar_auditoria_de_los_cuales_nuevos() -> str:\n', 'def _contar_afirmativos(',
         'def _exportar_auditoria_de_los_cuales_nuevos() -> str:\n'
         '    from caracterizacion_etiquetas_2027 import export_matricula_audit\n'
         '    return export_matricula_audit(globals())\n\n'),
        ('print(\n    "[AUDIT B4 PENDIENTES] "\n', 'def _segmentar_nombre_fallback(', ''),
        ('nombre_export = f"Estudiantes_pendientes_{ANIO_ANALISIS}',
         '# ==========================================================\n# BLOQUE 5',
         'from caracterizacion_etiquetas_2027 import export_response_tracking\n'
         'export_response_tracking(globals())\n'
         'log_avance("Bloque 4 - seguimiento total y pendientes reales de respuesta separados")\n\n')]
    for start, end, replacement in blocks:
        if source.count(start) != 1 or source.count(end) != 1:
            raise ValueError('Ancla de etiquetas 2027 inexistente o ambigua.')
        begin, finish = source.index(start), source.index(end)
        if begin >= finish:
            raise ValueError('Orden de anclas de etiquetas 2027 invalido.')
        source = source[:begin] + replacement + source[finish:]
    messages = [
        ('[AUDIT INFORME_CATEGORIAS NUEVOS]', '[CONTROL MATRICULA]'),
        ('[ℹ️] Nuevos inscritos acumulados detectados:', '[INCORPORACION] Listos antes de separar diario/acumulado:'),
        ('pendientes de exportación acumulada; el CSV diario se filtra por ventana',
         'no es el total del CSV acumulado; la separacion por ventana se informa al publicar'),
        ('[🧹] Total excluidos (únicos):', '[FILTROS BASE] Excluidos por programa/admin/participante/firma/cohorte (sin trayectoria):')]
    for old, new in messages:
        if old not in source:
            raise ValueError('Ancla de mensaje 2027 inexistente.')
        source = source.replace(old, new)
    financing_audit = ('"Tabla 3.bis - TOTAL SELECCIONES FINANCIAMIENTO",\n'
                       '    _df_fin_audit,\n    usar_ventana=True,')
    if source.count(financing_audit) != 1:
        raise ValueError('Ancla del control acumulado de financiamiento inexistente o ambigua.')
    source = source.replace(financing_audit, financing_audit.replace('usar_ventana=True', 'usar_ventana=False'))
    start = '# 5.5 Normalización final de sede para exportación\n'
    end = '# 5.6 Helper de exportación\n'
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError('Anclas de sede de comunicaciones inexistentes o ambiguas.')
    begin, finish = source.index(start), source.index(end)
    source = (source[:begin] + '# 5.5 Sede desde la columna fuente gobernada\n'
        'from caracterizacion_comunicaciones_2027 import normalize_communications\n'
        'df_bd_export = normalize_communications(df_bd_export,\n'
        '    df_bd[INCORPORACION_PLAN.columns["SEDE"]])\n\n' + source[finish:])
    start = '# 5.7 Exportaciones\n'
    end = '# BLOQUE 6 · LISTA DETALLADA DE CATEGORÍAS “SÍ” (SOLO VIGENTES) (LOCAL)\n'
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError('Anclas de exportacion de comunicaciones inexistentes o ambiguas.')
    begin, finish = source.index(start), source.index(end)
    source = (source[:begin] + '# 5.7 Comunicaciones general y tres sedes\n'
        'from caracterizacion_comunicaciones_2027 import publish_communications\n'
        'publish_communications(globals())\n\n' + source[finish:])
    # Bind the current questionnaire once, before either category consumer.
    start = 'CODIGOS_CATEGORIAS_ESPECIALES = {\n'
    end = '# Helpers canónicos de categorías/encuestas viven en BLOQUE 0 (sección 0.11):'
    begin, finish = source.index(start), source.index(end)
    source = (source[:begin] +
        'from caracterizacion_seguimiento_opciones_2027 import active_category_codes, positive_mask\n'
        'CODIGOS_CATEGORIAS_ESPECIALES, FRIENDLY_DETALLE = active_category_codes()\n\n' + source[finish:])
    start = 'def _mask_afirmativos_categoria(colname: str, serie: pd.Series, codigo: str) -> pd.Series:\n'
    end = '# 3.1/3.2 Conteos\n'
    if source.count(start)!=1 or source.count(end)!=1:
        raise ValueError('Ancla de categorias 2027 inexistente o ambigua.')
    begin, finish = source.index(start), source.index(end)
    source = source[:begin] + start + '    return positive_mask(serie, codigo)\n\n' + source[finish:]
    start = '# BLOQUE 6 · LISTA DETALLADA DE CATEGORÍAS “SÍ” (SOLO VIGENTES) (LOCAL)\n'
    end = '# BLOQUE 6.bis · Excel INDEPENDIENTE `financiamiento`\n'
    if source.count(start)!=1 or source.count(end)!=1:
        raise ValueError('Ancla del seguimiento Excel 2027 inexistente o ambigua.')
    begin, finish = source.index(start), source.index(end)
    source = (source[:begin] +
        '# BLOQUE 6 - Seguimiento de opciones desde respuestas canonicas\n'
        'from caracterizacion_seguimiento_opciones_2027 import publish_followup\n'
        'publish_followup(globals())\n\n' + source[finish:])
    begin = source.index(end)
    finish = source.index('if _env_flag("CARACTERIZACION_STOP_AFTER_FINANCIAMIENTO", False):',begin)
    source = source[:begin] + source[begin:finish].replace('"NUEVO"','"RESPONDIO_HOY"') + source[finish:]
    return source


def main():
    if (os.environ.get('ANIO_ANALISIS'), os.environ.get('PERIODO_ANALISIS')) != ('2027','1'):
        raise ValueError('El adaptador es exclusivo de 2027 P1.')
    sys.path.insert(0, str(ROOT / 'scripts/gobernanza'))
    from verificar_separacion_fcu import assert_frozen_reference
    assert_frozen_reference()
    path = ROOT / 'caracterizacion.py'
    original = path.read_text(encoding='utf-8')
    source = adapted_source(original)
    audit = Path(os.environ['CARACTERIZACION_RUN_DIR']) / '04_AUDITORIA/ADAPTADOR_2027.json'
    audit.write_text(json.dumps({'policy':POLICY, 'reference':str(path),
        'reference_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'adapter_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'effective_source_sha256':hashlib.sha256(source.encode()).hexdigest(),
        'reference_modified':False,
        'module_hashes':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in
            ('caracterizacion_incorporacion.py','caracterizacion_trayectorias_2027.py','caracterizacion_reportes_2027.py',
             'caracterizacion_comunicacion_2027.py','caracterizacion_sedes_2027.py','caracterizacion_runtime.py',
             'caracterizacion_etiquetas_2027.py','caracterizacion_seguimiento_opciones_2027.py',
             'caracterizacion_comunicaciones_2027.py','caracterizacion_salidas_2027.py','caracterizacion_personas_2027.py',
             'scripts/exportar_comunicaciones_sede_2027.mjs')}}, indent=2)+'\n')
    namespace = {'__name__':'__main__','__file__':str(path)}
    exec(compile(source, str(path), 'exec'), namespace)


if __name__ == '__main__':
    main()
