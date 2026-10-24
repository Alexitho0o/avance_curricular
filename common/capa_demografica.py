"""Calidad demográfica: no corrige ni decide identidad por semejanza."""
from scripts.fuentes_ensayo_enlace_conjunto import dateym, token

SEXOS = {'UMAS': {'M':'HOMBRE','F':'MUJER'}, 'MRUN':{'1':'HOMBRE','2':'MUJER'},
         'REPORTE':{'H':'HOMBRE','M':'MUJER'}}


def sexo(value, fuente):
    value=token(value).upper()
    if not value:return None,'SIN_DATO'
    result=SEXOS[fuente].get(value)
    return result, 'VALIDO' if result else 'NO_HOMOLOGADO'


def nacimiento(value):
    value=token(value)
    if not value or value=='190001':return None,'SIN_DATO'
    result=dateym(value)
    return result,'VALIDO' if result else 'INVALIDO'


def comparar(left, right):
    """Conjuntos de valores válidos. Multiplicidad implica conflicto interno."""
    left=set(left)-{None,''};right=set(right)-{None,''}
    if len(left)>1 or len(right)>1:return 'CONFLICTO_INTERNO'
    if not left and not right:return 'SIN_DATO_AMBOS'
    if not left:return 'SIN_DATO_UMAS'
    if not right:return 'SIN_DATO_REPORTE'
    return 'COINCIDE' if left==right else 'CONTRADICE'


def puerta(interna_ok, estados_documentales=None):
    if not interna_ok:return 'RETENIDO_CALIDAD_INTERNA'
    if estados_documentales is None:return 'SIN_CONTRASTE_DOCUMENTAL'
    if any(s in {'CONTRADICE','CONFLICTO_INTERNO'} for s in estados_documentales):return 'RETENIDO_CONTRADICCION_DOCUMENTAL'
    if all(s=='COINCIDE' for s in estados_documentales):return 'COINCIDENCIA_DOCUMENTAL'
    return 'CONTRASTE_DOCUMENTAL_INCOMPLETO'
