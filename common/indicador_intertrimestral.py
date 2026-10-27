"""Primitivas para indicador intertrimestral; no infiere vigencia o cobertura."""
from decimal import Decimal
import re

def normalizar_documento(cuerpo,dv):
    b='' if cuerpo is None else str(cuerpo).strip().replace('.','')
    d='' if dv is None else str(dv).strip().upper()
    if not re.fullmatch(r'\d+',b) or not re.fullmatch(r'[0-9K]',d):return None
    return f'{int(b)}-{d}'

def ratio(numerador,denominador):
    if denominador is None or denominador<=0:return None
    return Decimal(numerador)/Decimal(denominador)

def agregar(personas,excluir_diplomados=True):
    """Una identidad por grupo; no aplica precedencia frente a registros conflictivos."""
    vistos={}
    for p in personas:
        key=p['persona']
        if excluir_diplomados and p.get('diplomado') is True:continue
        if key in vistos and vistos[key] != p['estado']:raise ValueError('Estado conflictivo: requiere decisión por persona')
        vistos[key]=p['estado']
    return {'numerador':sum(s=='VIG 1' for s in vistos.values()),'denominador':sum(s not in ('NO APLICA','PENDIENTE') for s in vistos.values())}

def ponderar(pares):
    return ratio(sum(n for n,d in pares),sum(d for n,d in pares))

def documento_comparable(valor):
    """Comparación textual de referencias; no valida DV ni identidad personal."""
    if valor is None:return ''
    if isinstance(valor,float) and valor.is_integer():valor=int(valor)
    return str(valor).strip().upper().replace('.','').replace(' ','')
