"""Indicador interno de retención de primer año con lógica H001."""
from collections import defaultdict
from .h001 import reproducir_h001, normalizar
def documento(tipo_doc,n_doc,dv):
    return ("" if tipo_doc is None else str(tipo_doc).strip().upper(), "" if n_doc is None else str(n_doc).strip(), "" if dv is None else str(dv).strip().upper())
def calcular(rows, catalogo, cohortes=range(2022, 2026)):
    cohortes = tuple(cohortes)
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


def agrupar_h001(rows, catalogo, mapa_carreras, cohortes=range(2022, 2026), umbral=10):
    """Desglose por persona/cohorte; suprime grupos inferiores al umbral."""
    if umbral < 1:
        raise ValueError('El umbral debe ser positivo')
    eligible = reproducir_h001(rows, catalogo, cohortes)
    result = {'institucional': [], 'sector': [], 'carrera': []}
    for year in cohortes:
        cases = eligible.get(year, [])
        persons = [documento(r['TIPO_DOC'], r['N_DOC'], r['DV']) for r, _ in cases]
        if len(set(persons)) != len(persons):
            raise ValueError(f'Hay más de una matrícula elegible por persona en {year}')
        groups_sector = defaultdict(list)
        groups_carrera = defaultdict(list)
        for row, retained in cases:
            code = normalizar(row['COD_CAR'])
            if code not in mapa_carreras:
                raise ValueError(f'Falta mapeo de sector para COD_CAR {code} en {year}')
            name, sector = mapa_carreras[code]
            groups_sector[sector].append(retained)
            groups_carrera[(code, name, sector)].append(retained)
        def publish(values):
            n = len(values)
            if n < umbral:
                return {'casos': None, 'retenidos': None, 'tasa': None, 'estado': 'SUPRIMIDO_UMBRAL'}
            retained = sum(values)
            return {'casos': n, 'retenidos': retained, 'tasa': retained / n, 'estado': 'PUBLICABLE'}
        all_retained = [x[1] for x in cases]
        result['institucional'].append({'cohorte': year, **publish(all_retained)})
        for sector, values in sorted(groups_sector.items()):
            result['sector'].append({'cohorte': year, 'sector': sector, **publish(values)})
        for (code, name, sector), values in sorted(groups_carrera.items()):
            result['carrera'].append({'cohorte': year, 'cod_car': code, 'carrera': name, 'sector': sector, **publish(values)})
        assert sum(map(len, groups_sector.values())) == len(cases) == sum(map(len, groups_carrera.values()))
        assert sum(sum(v) for v in groups_sector.values()) == sum(all_retained) == sum(sum(v) for v in groups_carrera.values())
    return result


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
