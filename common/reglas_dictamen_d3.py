"""Condiciones deterministas D3; evidencia analítica sin acreditación de mallas."""
import json
TIPOS={'Plan Regular':'1','Plan Regular de Continuidad':'3'}

def clave_contexto(c):
    return json.dumps([c['codcarpr'],c['sede_umas'],c['jornada_umas'],c['anio_observado'],
        c['ingreso_original_declarado'],c['primer_anio_observado_en_carrera'],c['planes_observados'] or ['PLAN_NO_OBSERVADO']],ensure_ascii=False,separators=(',',':'))

def vigencia_anual(oferta):
    if oferta is None:return 'SIN_OFERTA_ANUAL'
    v=oferta.get('vigencia','').lower()
    if 'sin estudiantes nuevos' in v:return 'SOLO_ANTIGUOS'
    if 'con estudiantes nuevos' in v:return 'ADMITE_NUEVOS'
    return 'VIGENCIA_NO_INTERPRETADA'

def evaluar_contexto(c, reglas, expediente, ofertas, grupo):
    obs=sorted(set(c['codigos_documentales'])|set(c['codigos_mrun_propuestos']))
    states={r['estado'] for r in reglas}
    causes=['INGRESO_EPISODIO_NO_ACREDITADO','SEDE_JORNADA_HISTORICAS_NO_ACREDITADAS']
    applied=['D3-01','D3-02','D3-06']
    if c['estado'] in ('MULTIPLES_DESTINOS','CONTRADICCION_ENTRE_EVIDENCIAS') or states & {'CONFLICTO_CONSTRUCCION','CONTRADICCION_EN_RESERVA'}:
        status='ABSTENCION_CONFLICTO';causes.append('DESTINOS_INCOMPATIBLES_EN_CONTEXTO');applied.append('D3-04')
    elif c['codigos_asignacion_ambigua']:
        status='ABSTENCION_AMBIGUEDAD';causes.append('ATRIBUCION_NO_UNIVOCA');applied.append('D3-04')
    elif not obs:
        status='SIN_EVIDENCIA_ATRIBUIBLE';causes.append('SIN_DESTINO_OBSERVADO');applied.append('D3-05')
    elif 'CORROBORADA_EN_RESERVA' in states:
        status='USO_ANALITICO_CORROBORADO';applied.append('D3-07')
    elif 'OBSERVADA_SIN_RESERVA' in states:
        status='OBSERVACION_SIN_CONTRASTE';causes.append('SIN_CONTRASTE_RESERVADO');applied.append('D3-07')
    else:
        status='EVIDENCIA_SIN_REGLA_K0';causes.append('SIN_REGLA_BASE_CONTRASTADA');applied.append('D3-05')
    if not c['planes_observados']:causes.append('SIN_PLAN_OBSERVADO')
    else:causes.append('VIGENCIA_MALLA_NO_ACREDITADA')
    if expediente:
        applied.append('D3-03')
        if expediente['observaciones_persona_estrato_ingreso_en_solo_antiguos']:
            causes.append('DISCREPANCIA_ADMISION_DOCUMENTADA_EN_SUBCONJUNTO')
        if expediente['personas_sin_reporte_atribuible']:causes.append('CONTRASTE_DOCUMENTAL_PARCIAL')
    profiles={tuple(p) for p in grupo['perfiles_duracion_tipo']} if grupo else set()
    comparisons=[]
    for code in sorted(set(obs)|set(c['codigos_candidatos_h5'])|set(c['codigos_asignacion_ambigua'])):
        offer=ofertas.get((c['anio_observado'],code))
        compatible=None if not offer or not profiles else (offer['duracion_total'],TIPOS.get(offer['tipo_plan_sies'])) in profiles
        comparisons.append({'codigo':code,'oferta_anio_observado':offer,'vigencia':vigencia_anual(offer),
            'compatible_perfil_referencia':compatible,'ambito_perfil_referencia':2026,
            'es_destino_observado':code in obs,'no_acredita_vigencia_historica_perfil':True})
    if profiles:applied.append('D3-08')
    return {'contexto':c['contexto'],'clave':clave_contexto(c),'estado':status,'reglas_aplicadas':sorted(set(applied)),
        'alcance':'PROGRAMA_CONTEXTO' if not c['planes_observados'] else 'CONTEXTO_CON_PLAN_OBSERVADO_SIN_VIGENCIA_ACREDITADA',
        'codigos_observados':obs,'codigos_ambiguos':c['codigos_asignacion_ambigua'],
        'candidatos_h5_ambito_2026':c['codigos_candidatos_h5'],'reglas_k0':[r['id'] for r in reglas],
        'causas_abstencion_asignacion':sorted(set(causes)),'comparacion_oferta_perfil':comparisons,
        'expediente_d2':expediente['contexto'] if expediente else None,'codigo_asignado':None,'habilitada_para_resolver':False}

def control_variante(estado):
    if estado=='DATO_POSTERIOR_AL_CONTEXTO':return 'ABSTENCION_DATO_POSTERIOR'
    if estado in ('CONFLICTO_CONSTRUCCION','CONTRADICCION_EN_RESERVA'):return 'ABSTENCION_CONFLICTO_VARIANTE'
    return 'SIN_HABILITACION_PRODUCTIVA'
