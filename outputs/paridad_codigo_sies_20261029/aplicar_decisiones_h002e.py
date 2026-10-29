"""Decisiones H002e de catálogo. Conserva la unidad código y asociaciones de plan."""
from copy import deepcopy


def aplicar(rows, groups, decision, evidence, review_evidence, vigentes, offers):
    baseline=deepcopy(rows)
    approvals={x['grupo']:x for x in decision['correspondencias']}
    historic={x['grupo']:x for x in decision['planes_historicos']}
    cad=decision['pendiente_CADMP'];cad_key=cad['grupo']
    selected=set(approvals)|set(historic)|{cad_key}
    if len(approvals)!=5 or len(historic)!=6 or len(selected)!=12:
        raise ValueError('La decisión no tiene las doce combinaciones autorizadas')
    controls={(x['codcarpr'],x['sede'],x['jornada']):x for x in vigentes['grupos']}
    for key in sorted(selected):
        if key not in groups:
            raise ValueError('Grupo de decisión no existe en el catálogo')
        g=deepcopy(groups[key]);g['resolucion_calculada_antes_H002e']=deepcopy(g['resolucion_nuevos_2027'])
        g['decision_H002e']={'id':decision['id'],'fuente':decision['fuente'],'clase':'D','evidencia':evidence}
        if key in approvals:
            d=approvals[key];code=d['codigo_unico']
            if code not in set(g['codigos_previos'])|set(g['codigos_2027_familia']):
                raise ValueError('Código aprobado fuera de las opciones del grupo')
            if d['planes_explicitos'] and not set(d['planes_explicitos'])<=set(g['planes_catalogados_candidatos']):
                raise ValueError('CODPESTUD aprobado no está en los candidatos de la revisión')
            g.update(estado_paridad_2027='APROBADA_D_2027',clase_paridad_2027='D',
                     codigo_sies_aprobado=code,planes_explicitos_aprobados=d['planes_explicitos'],
                     ambito_mallas_cohortes='D: plan explícito de catálogo, no asignación individual' if d['planes_explicitos'] else 'E: ámbito por malla/cohorte no elegido')
            permits=offers[code]['VIGENCIA_CARRERA']=='1'
            g['resolucion_nuevos_2027']={'estado':'D_APROBADA' if permits else 'D_CODIGO_APROBADO_SIN_NUEVOS',
                'seleccion':code if permits else None,'opciones':[code] if permits else [],
                'codigo_catalogo_aprobado':code,'motivo':'Decisión de Alexi; admisión separada y sujeta a vigencia literal de la carga.'}
        elif key in historic:
            d=historic[key];check=controls.get((g['codcarpr'],g['sede_umas'],g['jornada_umas']))
            if check is None or check['vigentes_etiqueta_UMAS']!=0:
                raise ValueError('La foto no respalda cero vigentes UMAS en el grupo')
            g.update(estado_paridad_2027='PLAN_HISTORICO_SIN_ALUMNOS_VIGENTES',clase_paridad_2027='D',
                codigo_sies_aprobado=None,control_foto_Permanencia=deepcopy(check),
                ambiguedad_historica={'clase':'E','codigos_candidatos':sorted(set(g['codigos_previos'])|set(g['codigos_2027_familia'])),
                    'version_asignada':None,'motivo':'Fuera de la necesidad de paridad 2027 por decisión D; no resuelve atribución histórica.'})
            g['resolucion_nuevos_2027']={'estado':'NO_REQUIERE_PARIDAD_2027_D','seleccion':None,'opciones':[],
                'motivo':d['motivo']}
        else:
            g.update(estado_paridad_2027='VERSION_MULTIPLE_E',clase_paridad_2027='E',
                codigo_sies_aprobado=None,indicio_H002e=deepcopy(cad['indicio']))
        groups[key]=g
    historical_codes={x['codigo_unico']:x for x in decision['codigos_historicos']}
    affected=[]
    for row in rows:
        if row['anio']!=2027:
            continue
        related={g['grupo'] for g in row['resoluciones_grupo']} & selected
        if row['codigo_unico'] not in historical_codes and not related:
            continue
        previous_state=row['estado'];row['estado_antes_H002e']=previous_state
        row['decision_H002e']={'id':decision['id'],'fuente':decision['fuente'],'clase':'D',
            'alcance':'Sólo relaciones y grupos citados; no aprobación de todos los alias de la fila.'}
        row['evidencia']+=[deepcopy(evidence),deepcopy(review_evidence)]
        if row['codigo_unico'] in historical_codes:
            row.update(estado='HISTORICO_SIN_MATRICULA_RECIENTE',clase='D',version_para_nuevos_2027='no',
                motivo='Decisión D: C35 histórico sin matrícula reciente; no requiere paridad 2027. No cambia la oferta.',
                ultima_matricula_publica=deepcopy(historical_codes[row['codigo_unico']]['ultima_matricula_publica']))
        else:
            row['resoluciones_grupo']=[deepcopy(groups[g['grupo']]) if g['grupo'] in related else g for g in row['resoluciones_grupo']]
            row['decisiones_por_grupo_H002e']=[{'grupo':key,'estado':groups[key]['estado_paridad_2027'],
                'clase':groups[key]['clase_paridad_2027'],'codigo_sies_aprobado':groups[key].get('codigo_sies_aprobado'),
                'ambiguedad_historica':groups[key].get('ambiguedad_historica'),
                'evidencia':(approvals.get(key) or historic.get(key) or cad)['evidencia']} for key in sorted(related)]
            row['correspondencias_aprobadas_H002e']=[deepcopy(d) for key,d in approvals.items() if key in related and d['codigo_unico']==row['codigo_unico']]
            for internal in row['candidatos_internos']:
                matching=[key for key in related if (groups[key]['codcarpr'],groups[key]['sede_umas'],groups[key]['jornada_umas'])==
                    (internal['codcarpr'],internal['sede_umas'],internal['jornada_umas'])]
                if matching:
                    key=matching[0];g=groups[key]
                    internal['estado_paridad_2027']=g['estado_paridad_2027']
                    internal['clase_paridad_2027']=g['clase_paridad_2027']
                    internal['codigo_sies_aprobado_grupo']=g.get('codigo_sies_aprobado')
                    internal['seleccion_grupo']=deepcopy(g['resolucion_nuevos_2027'])
                    if key in historic:
                        internal['ambiguedad_historica']=deepcopy(g['ambiguedad_historica'])
            if row['correspondencias_aprobadas_H002e']:
                row.update(estado='APROBADA_D_2027',clase='D',
                    motivo='Correspondencia del grupo/plan aprobada por Alexi; otros alias y ámbito histórico conservan su propio respaldo.',
                    estado_plan_por_cohorte='D_PLAN_EXPLICITO_SIN_ATRIBUCION_PERSONAL' if all(d['planes_explicitos'] for d in row['correspondencias_aprobadas_H002e']) else 'E_AMBITO_MALLAS_COHORTES_SEPARADO')
                row['version_para_nuevos_2027']='sí' if row['vigencia_2027']=='1' else 'no'
            elif cad_key in related:
                row.update(estado='VERSION_MULTIPLE_E',indicio_H002e={'clase':'B/C/E',**deepcopy(cad['indicio']),
                    'codigo_candidato_no_aprobado':'I162S2C83J4V2','aprobada':False})
            else:
                unresolved=[g for g in row['resoluciones_grupo'] if g['multiple'] and g['resolucion_nuevos_2027']['estado']=='E']
                all_historical=all(g.get('estado_paridad_2027')=='PLAN_HISTORICO_SIN_ALUMNOS_VIGENTES' for g in row['resoluciones_grupo'])
                if all_historical:
                    row.update(estado='PLAN_HISTORICO_SIN_ALUMNOS_VIGENTES',clase='D')
                elif not unresolved and previous_state=='VERSION_MULTIPLE_E':
                    row.update(estado='VERSION_MULTIPLE_RESUELTA',clase='C/D',
                        motivo='Grupos pendientes aprobados o retirados del alcance 2027; el código conserva otros planes activos. Ambigüedad histórica E separada.')
                    row['version_para_nuevos_2027']='no' if row['vigencia_2027'] in {'2','3'} else 'sí' if any(
                        g['resolucion_nuevos_2027'].get('seleccion')==row['codigo_unico'] for g in row['resoluciones_grupo']) else 'E'
        affected.append((row['anio'],row['codigo_unico']))
    if len(affected)!=20 or len({r['codigo_unico'] for r in rows if r['anio']==2027 and r.get('correspondencias_aprobadas_H002e')})!=5:
        raise ValueError('La decisión debe afectar las veinte filas 2027 asociadas y cinco códigos aprobados')
    prev={(r['anio'],r['codigo_unico']):r for r in baseline}
    if any(r!=prev[(r['anio'],r['codigo_unico'])] for r in rows if (r['anio'],r['codigo_unico']) not in affected):
        raise ValueError('Cambio fuera de filas autorizadas')
    if any(r!=prev[(2027,r['codigo_unico'])] for r in rows if r['anio']==2027 and r['codigo_unico'] in decision['37_pendientes_sin_cambio']):
        raise ValueError('Las 37 filas pendientes deben quedar idénticas')
    return {'filas_afectadas':affected,'aprobadas_5':[x['codigo_unico'] for x in decision['correspondencias']],
        'grupos_historicos_6':sorted(historic),'pendiente_CADMP':cad_key,
        'grupos_fuera_alcance':len(historic),'filas_2026_intactas':all(r==prev[(r['anio'],r['codigo_unico'])] for r in rows if r['anio']==2026)}


def pendientes_md(rows,decisions,decision):
    lines=['# H002 · estado vigente después de H002e','','D · Alexi, 29-10-2026. Unidad tabla: año/código; decisiones de plan conservadas por grupo.','',
        '## Cinco correspondencias aprobadas D','','| Grupo | Plan explícito | Código SIES |','|---|---|---|']
    for d in decision['correspondencias']:
        lines.append('| '+d['codcarpr']+' / '+d['sede']+' / '+d['jornada']+' | '+(', '.join(d['planes_explicitos']) or 'Ámbito de mallas/cohortes separado')+' | '+d['codigo_unico']+' |')
    lines+=['','## Pendiente CADMP','','7 expedientes con actividad, 10 en Permanencia, frente a SIES 2026 V2=9 y V1=94. Indicio E sin aprobación.','',
        '## Seis grupos históricos, sin asignar versión','','IECIRE, IETMRE, NCONRE, NCONREOL, NINFREOL y CNATP: PLAN_HISTORICO_SIN_ALUMNOS_VIGENTES (D). Ambigüedad histórica E conservada. IECIRE tiene un TITULADO en la foto; cero vigentes no equivale a cero filas.','',
        'Los códigos compartidos siguen activos para otros planes. No contar estos seis grupos como seis códigos cerrados.','',
        '## 37 códigos pendientes de planes UMAS','','La lista exacta, con sede/jornada/modalidad, está en PROPUESTA_PLANES_43_v2.md. Sus filas permanecen intactas como NUEVO_2027_SIN_PLAN_E.','',
        '## C35 y oferta','','Seis C35: HISTORICO_SIN_MATRICULA_RECIENTE (D). Las siete observaciones de vigencia 2 se registran en OBSERVACIONES_OFERTA_2027.md; no se cambia la carga.','',
        'Las seis relaciones D de H002b permanecen vigentes. Las propuestas H002b–d son antecedentes congelados; esta decisión no modifica v20 ni atribuye estudiantes.','']
    return '\n'.join(lines)


def observaciones_md(decision):
    source=decision['fuente_43']
    lines=['# Observaciones de oferta 2027','','E · Registro para Alexi, sin modificar la oferta.','',
        'A · Manual Oferta Académica 2027, página 28: VIGENCIA_CARRERA=2 corresponde a vigente sin estudiantes nuevos y con estudiantes antiguos; 3 es no vigente.','',
        'Fuente oficial: oferta_academica_2027/00_fuentes_originales/etapa1_octubre_20261020/Instructivo_Oferta_Academica_2027_CFT_E_IP_DFE.pdf. SHA-256 en FUENTES.json (manual_octubre).','',
        '| Código | Vigencia declarada | Última matrícula pública 2007–2026 | Estado |','|---|---|---|---|']
    for x in decision['observaciones_oferta']:
        last=x['ultima_matricula_publica']
        lines.append('| '+x['codigo_unico']+' | 2 | '+(str(last['anio'])+': '+str(last['matriculas']) if last else 'No observada en la cobertura')+' | E para Alexi |')
    lines+=['','B/C · Evidencia histórica: '+source['ruta']+'; SHA-256 '+source['sha256']+'.',
        'B/C · Cuadratura: CONTROL_TOTALES_H002D.json y FUENTES_H002D.json. La carga V06 y su copia congelada se conservan por hash en FUENTES.json.',
        'La bandera es transversal: seis C35 históricos y un código incluido entre los 37 sin historia de matrícula. No sumar las observaciones como una tercera población.',
        'La ausencia en matrícula pública reciente no prueba cierre ni error de oferta. No se activa una hipótesis ni se pide rectificar a SIES.','']
    return '\n'.join(lines)
