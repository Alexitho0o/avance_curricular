"""Cálculo preliminar reproducible de Retención de 1er año."""
from collections import defaultdict
def documento(tipo_doc,n_doc,dv):
    return ("" if tipo_doc is None else str(tipo_doc).strip().upper(), "" if n_doc is None else str(n_doc).strip(), "" if dv is None else str(dv).strip().upper())
def calcular(rows,cohortes=range(2022,2026)):
    by=defaultdict(list)
    for r in rows: by[(documento(r.get('TIPO_DOC'),r.get('N_DOC'),r.get('DV')),int(r['ANIO_INFORMADO']))].append(r)
    out=[]
    for y in cohortes:
        base={k for (k,a),rs in by.items() if a==y and any(r.get('VIG')==1 and int(r.get('ANIO_ING_ACT',-1))==y for r in rs)}
        # Regla SIES: permanece si está presente en la MU de t+1 de IPSS.
        # VIG describe el registro, pero no es un filtro adicional de retención.
        ret={k for k in base if by.get((k,y+1),[])}
        out.append({'cohorte':y,'denominador':len(base),'retenidos':len(ret),'tasa':len(ret)/len(base) if base else None})
    return out
