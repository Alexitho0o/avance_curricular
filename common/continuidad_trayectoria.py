"""Regla interna: ANOINGRESO heredado no fija el ingreso a continuidad."""
from collections import defaultdict


def resolver_version_trayectoria(grupo, historias, *, anoingreso,
                                anio_inicio_carrera=None, fecha_confirmada=False):
    """Continuidad nunca usa ANOINGRESO como sustituto del ingreso a esa carrera."""
    from common.versiones_por_cohorte import resolver_cohorte
    tipos = {p[1] for p in grupo['perfiles_duracion_tipo']} if grupo else set()
    if '3' in tipos and tipos != {'3'}:
        return {'estado':'TIPO_PLAN_AMBIGUO','codigo_propuesto':None,
                'habilitada_carga_oficial':False}
    continuidad = tipos == {'3'}
    year = anio_inicio_carrera if continuidad else anoingreso
    if continuidad and year is None:
        return {'estado':'REQUIERE_INICIO_EN_CARRERA_CONTINUIDAD','codigo_propuesto':None,
                'anoingreso_original':anoingreso,'anoingreso_usado_para_version':False,
                'habilitada_carga_oficial':False}
    result = resolver_cohorte(grupo,historias,anoingreso=year)
    result['anoingreso_original'] = anoingreso
    result['anoingreso_usado_para_version'] = not continuidad
    result['fuente_fecha_version'] = ('INGRESO_CARRERA_CONFIRMADO' if fecha_confirmada else
                                     'PRIMERA_OBSERVACION_CARRERA') if continuidad else 'ANOINGRESO_UMAS'
    return result


def evaluar_trayectorias(registros):
    """Identidades solo en memoria; el consumidor publica únicamente agregados."""
    people = defaultdict(list)
    owners = defaultdict(set)
    for r in registros:
        if r['persona'] and r['codcli']:
            people[r['persona']].append(r)
            owners[r['codcli']].add(r['persona'])
    result = []
    for r in registros:
        if not r['continuidad']:
            continue
        out = {'indice': r['indice'], 'origen': None, 'primer_anio_observado_carrera': None,
               'anio_ingreso_efectivo_confirmado': None, 'anoingreso_original': r['anoingreso'],
               'anoingreso_usado_para_version': False, 'ingreso_externo_confirmado': False,
               'cantidad_codcli_tecnicos': 0, 'cantidad_codcli_misma_carrera': 0}
        if not r['persona'] or not r['codcli']:
            out['origen'] = 'IDENTIDAD_INSUFICIENTE'
        elif len(owners[r['codcli']]) != 1:
            out['origen'] = 'CONFLICTO_IDENTIDAD_CODCLI'
        else:
            peers = [p for p in people[r['persona']] if len(owners[p['codcli']]) == 1]
            same = [p for p in peers if p['carrera'] == r['carrera'] and p['continuidad']]
            observed = sorted({year for p in same for year in p['anios_observados']})
            first = min(observed) if observed else None
            out['primer_anio_observado_carrera'] = first
            out['cantidad_codcli_misma_carrera'] = len({p['codcli'] for p in same})
            technical = [p for p in peers if p['codcli'] != r['codcli']
                         and p['carrera'] != r['carrera'] and p['tecnico']]
            out['cantidad_codcli_tecnicos'] = len({p['codcli'] for p in technical})
            earlier = any(first is not None and any(y < first for y in p['anios_observados']) for p in technical)
            out['origen'] = ('TECNICO_IPSS_OBSERVADO_ANTERIOR' if earlier else
                             'TECNICO_IPSS_TEMPORALIDAD_PENDIENTE' if technical else
                             'SIN_TECNICO_INTERNO_LOCALIZADO')
        out['estado_fecha'] = ('PRIMERA_OBSERVACION_NO_INGRESO_CONFIRMADO'
                              if out['primer_anio_observado_carrera'] is not None else 'SIN_FECHA_CARRERA_OBSERVADA')
        result.append(out)
    return result
