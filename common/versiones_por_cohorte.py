"""Propone versión por cohorte dentro de una agrupación ya existente."""
import json


def clave_grupo(codcarpr, sede, jornada):
    return json.dumps([codcarpr, sede, jornada], ensure_ascii=False, separators=(',', ':'))


def resolver_cohorte(grupo, historias, *, anoingreso):
    """Separa coincidencia de inicio de la hipótesis de intervalo; no asigna malla."""
    result = {'estado': None, 'codigo_propuesto': None, 'version_propuesta': None,
              'anoingreso': anoingreso, 'candidatos_perfil': [], 'candidatos_fecha': [],
              'descartados_perfil': [], 'habilitada_carga_oficial': False,
              'acredita_codpestud': False, 'nombre_usado_como_filtro': False}
    if type(anoingreso) is not int:
        result['estado'] = 'ANOINGRESO_AUSENTE_O_INVALIDO'
        return result
    if not 2007 <= anoingreso <= 2026:
        result['estado'] = 'FUERA_AMBITO_2007_2026'
        return result
    if not grupo:
        result['estado'] = 'SIN_AGRUPACION_EXISTENTE'
        return result
    if not grupo['perfiles_duracion_tipo']:
        result['estado'] = 'PERFIL_DURACION_NO_DETERMINADO_EN_GRUPO'
        return result
    profiles = {tuple(x) for x in grupo['perfiles_duracion_tipo']}
    for history in historias:
        if history['familia'] not in grupo['familias']:
            continue
        start = history['inicio_oferta']
        annual = next((r for r in history['anual'] if r['anio'] == anoingreso), None)
        reference = annual or history['anual'][0]
        profile = (reference['duracion_total'], reference['tipo_plan'])
        item = {'codigo_unico': history['codigo_unico'], 'inicio_oferta': start,
                'duracion_total': profile[0], 'tipo_plan': profile[1],
                'anio_perfil_comparado': reference['anio'],
                'perfil_del_anio_ingreso': annual is not None,
                'registro_oferta': reference['registro_csv'],
                'inicio_en_limite_cobertura': start == 2010}
        if profile in profiles:
            result['candidatos_perfil'].append(item)
        else:
            result['descartados_perfil'].append(item)
    candidates = result['candidatos_perfil']
    if not candidates:
        result['estado'] = 'SIN_VERSION_DEL_PERFIL_EN_OFERTA'
        return result
    eligible = [r for r in candidates if r['inicio_oferta'] <= anoingreso]
    if not eligible:
        result['estado'] = ('COHORTE_ANTERIOR_COBERTURA_OFERTA' if anoingreso < 2010
                            else 'COHORTE_ANTERIOR_INICIO_OFERTA')
        return result
    # Distintos perfiles internos aún posibles no compiten por fecha entre sí.
    eligible_profiles = {(r['duracion_total'], r['tipo_plan']) for r in eligible}
    if len(eligible_profiles) != 1:
        result['estado'] = 'AMBIGUEDAD_PERFIL_DURACION'
        result['candidatos_fecha'] = sorted(r['codigo_unico'] for r in eligible)
        return result
    latest = max(r['inicio_oferta'] for r in eligible)
    chosen = [r for r in eligible if r['inicio_oferta'] == latest]
    result['candidatos_fecha'] = sorted(r['codigo_unico'] for r in chosen)
    if len(chosen) != 1:
        result['estado'] = 'EMPATE_PRIMERA_OFERTA'
        return result
    row = chosen[0]
    result.update(codigo_propuesto=row['codigo_unico'],
                  version_propuesta=row['codigo_unico'].rsplit('V', 1)[1],
                  inicio_seleccionado=latest,
                  estado='COINCIDENCIA_INICIO' if latest == anoingreso else 'INTERVALO_PROPUESTO',
                  inicio_en_limite_cobertura=row['inicio_en_limite_cobertura'],
                  oferta_observada_anio_ingreso=row['perfil_del_anio_ingreso'])
    return result
