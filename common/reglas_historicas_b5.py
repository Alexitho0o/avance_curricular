"""Consulta de reglas internas observadas, sin equivalencias acreditadas."""
import json
BASE=('codcarpr','sede','jornada','anio','ingreso_original','primera_observacion','planes')
EXTRAS={'K0':(), 'K1':('periodo_ingreso',), 'K2':('anomatricula','periodo_matricula'),
        'K3':('periodo_ingreso','anomatricula','periodo_matricula')}


def clave(row, modelo, temporal=False):
    fields=tuple(f for f in BASE if not (temporal and f=='anio'))+EXTRAS[modelo]
    if any(row.get(f) is None or row.get(f)=='' or row.get(f)==[] for f in fields):return None
    return json.dumps([row[f] for f in fields],ensure_ascii=False,separators=(',',':'))


def estado(codes, oferta, aciertos, errores, dato_posterior=False):
    if dato_posterior:return 'DATO_POSTERIOR_AL_CONTEXTO'
    if len(codes)>1:return 'CONFLICTO_CONSTRUCCION'
    if not codes:return 'SIN_REGLA_OBSERVADA'
    if not oferta:return 'SIN_OFERTA_ANUAL'
    if errores:return 'CONTRADICCION_EN_RESERVA'
    return 'CORROBORADA_EN_RESERVA' if aciertos else 'OBSERVADA_SIN_RESERVA'


def consultar(registro, entrada, modelo='K0'):
    k=clave(entrada,modelo)
    if k is None:return {'estado':'ENTRADA_INCOMPLETA','candidatos':[],'habilitada_para_resolver':False}
    r=next((r for r in registro if r['modelo']==modelo and r['clave']==k),None)
    if not r:return {'estado':'SIN_REGLA_OBSERVADA','candidatos':[],'habilitada_para_resolver':False}
    return {'estado':r['estado'],'candidatos':r['codigos_construccion'],'regla':r['id'],'habilitada_para_resolver':False}
