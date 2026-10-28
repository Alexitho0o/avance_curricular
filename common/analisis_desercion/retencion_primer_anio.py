"""Cálculo preliminar reproducible de Retención de 1er año."""
from collections import defaultdict
from .h001 import reproducir_h001
def documento(tipo_doc,n_doc,dv):
    return ("" if tipo_doc is None else str(tipo_doc).strip().upper(), "" if n_doc is None else str(n_doc).strip(), "" if dv is None else str(dv).strip().upper())
def calcular(rows, catalogo, cohortes=range(2022, 2025), *, cohorte_2025_conciliada=False, tratamiento_vig_aprobado=False):
    cohortes = tuple(cohortes)
    if 2025 in cohortes and not (cohorte_2025_conciliada and tratamiento_vig_aprobado):
        raise ValueError('Cohorte 2025 bloqueada: se requiere cohorte conciliada con la oficial (1.163 ± explicación) y tratamiento de VIG aprobado.')
    eligible = reproducir_h001(rows, catalogo, cohortes)
    out = []
    for y in cohortes:
        cases = eligible.get(y, [])
        persons = [documento(r['TIPO_DOC'], r['N_DOC'], r['DV']) for r, _ in cases]
        if len(set(persons)) != len(persons):
            raise ValueError(f'H001 produce matrículas duplicadas por persona en cohorte {y}; revisar antes de calcular.')
        n = len(cases)
        retained = sum(ret for _, ret in cases)
        out.append({'cohorte': y, 'denominador': n, 'retenidos': retained, 'tasa': retained / n if n else None})
    return out


def calcular_presencia_preliminar(rows, cohortes=range(2022, 2025)):
    """Prototipo anterior; no usar para publicación ni cohorte 2025."""
    cohortes = tuple(cohortes)
    if 2025 in cohortes:
        raise ValueError('Cohorte 2025 bloqueada en el prototipo de presencia.')
    by=defaultdict(list)
    for r in rows: by[(documento(r.get('TIPO_DOC'),r.get('N_DOC'),r.get('DV')),int(r['ANIO_INFORMADO']))].append(r)
    out=[]
    for y in cohortes:
        base={k for (k,a),rs in by.items() if a==y and any(r.get('VIG')==1 and int(r.get('ANIO_ING_ACT',-1))==y for r in rs)}
        # Prototipo C: presencia con cualquier VIG; no acreditado como regla SIES.
        ret={k for k in base if by.get((k,y+1),[])}
        out.append({'cohorte':y,'denominador':len(base),'retenidos':len(ret),'tasa':len(ret)/len(base) if base else None})
    return out
