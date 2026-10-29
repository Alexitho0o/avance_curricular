"""Aprobaciones D de catálogo; la selección de malla conserva su propia clase."""
from collections import defaultdict


def aplicar_aprobaciones(rows, decision, master, cohortes, evidencia):
    approved = {r['codigo_unico']: r for r in decision['correspondencias']}
    affected = []
    for row in rows:
        if row['anio'] != 2027 or row['codigo_unico'] not in approved:
            continue
        rec = approved[row['codigo_unico']]
        if row['estado'] != 'NUEVO_2027_CON_PLAN' or sorted(row['codcarpr']) != sorted(rec['codcarpr']):
            raise ValueError('La decisión no coincide con la propuesta previa de catálogo')
        row['estado_anterior_H002'] = row['estado']
        row['estado'] = 'APROBADA_D_2027'
        row['clase'] = 'D'
        row['decision'] = {'id': decision['id'], 'fuente': decision['fuente'],
                           'alcance': decision['alcance'], 'clase': 'D'}
        row['evidencia'].append(evidencia)
        row['motivo'] = 'Correspondencia código SIES–CODCARPR aprobada; plan/cohorte y atribución individual se mantienen separados.'
        row['plan_por_cohorte'] = []
        for internal in row['candidatos_internos']:
            career = internal['codcarpr']
            plans = sorted(set(internal['plan_umas']))
            observed = defaultdict(set)
            for result in cohortes:
                d = result['datos_alumnos']
                if (str(d['CODCARPR']).strip(), str(d['SEDE']).strip(), str(d['JORNADA']).strip()) != (
                    career, internal['sede_umas'], internal['jornada_umas']):
                    continue
                raw = str(d['ANOINGRESO']).strip()
                if raw.isdigit() and 2007 <= int(raw) <= 2027:
                    code = result['resolucion'].get('codigo_propuesto')
                    observed[int(raw)].add(code if code is not None else 'E_SIN_CODIGO_PROPUESTO')
            for year in sorted(set(observed) | {2027}):
                # No usar año incrustado ni actividad como si fuese ámbito de cohorte.
                temporal = {r['plan_umas'] for r in master['reglas_efectivas']
                    if r.get('codcarpr') == career and r.get('codigo_unico') == row['codigo_unico']
                    and r.get('sede_umas') == internal['sede_umas']
                    and r.get('jornada_umas') == internal['jornada_umas']
                    and any(str(p.get('anio')) == str(year) for p in r.get('periodos', []))}
                if len(temporal) == 1:
                    selected, state, cl = next(iter(temporal)), 'PLAN_UNICO_CON_AMBITO_EXPLICITO', 'C'
                elif len(plans) == 1:
                    selected, state, cl = plans[0], 'CANDIDATO_UNICO_DE_CATALOGO_NO_ATRIBUCION_PERSONAL', 'C'
                else:
                    selected, state, cl = None, 'E_PLAN_NO_UNICO_POR_COHORTE', 'E'
                row['plan_por_cohorte'].append({'codcarpr': career, 'cohorte': year,
                    'codigo_sies_catalogo_2027': row['codigo_unico'], 'plan_umas': selected,
                    'planes_candidatos': plans, 'estado': state, 'clase': cl,
                    'codigos_ensayo_historico_cohorte': sorted(observed.get(year, set())),
                    'limite': 'Ensayo histórico de códigos no selecciona CODPESTUD. Código aprobado solo para catálogo 2027; no se adjudican matrículas ni cohortes previas.'})
        row['estado_plan_por_cohorte'] = ('E_PLANES_NO_UNICOS' if any(x['clase'] == 'E' for x in row['plan_por_cohorte'])
                                         else 'C_CATALOGO_UNICO_NO_ATRIBUCION_PERSONAL')
        row['version_para_nuevos_2027'] = 'sí' if row['vigencia_2027'] == '1' else 'no'
        affected.append(row['codigo_unico'])
    if set(affected) != set(approved) or len(affected) != 6:
        raise ValueError('La aprobación debe afectar exactamente seis filas 2027')
    return affected
