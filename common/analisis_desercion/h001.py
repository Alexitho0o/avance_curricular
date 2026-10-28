"""Reproducción histórica H001; no acredita una tasa oficial SIES.

Fuente: data/reglas_negocio/mu2027/estudio/auditar_solo_lectura.py,
commit 55e3b709afb9483f0ecdd2d166f67229a454a5ef,
SHA-256 ba71eea98eebe3627593b613a37897ef6dd4d7b6e39d8a31732771807e0f5f30.
Fuente del catálogo: hoja 01_CATALOGO_CARRERA del diagnóstico H001
SHA-256 5f0f7c7f0f238556de374d287bf2931ccc8a93a5489f4c2f2b543befd38c77b3.
"""
from collections import defaultdict


def normalizar(valor):
    if valor is None:
        return ''
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    return str(valor).strip()


def llave(row):
    return (normalizar(row['TIPO_DOC']), normalizar(row['N_DOC']), normalizar(row['DV']).upper())


def origen(row):
    return (normalizar(row['ANIO_ING_ORI']), normalizar(row['SEM_ING_ORI']))


def positivo(row):
    return float(normalizar(row['VIG']) or -1) >= 1


def codigo(row):
    return 'I162S{}C{}J{}V{}'.format(*(normalizar(row[c]) for c in ('COD_SED', 'COD_CAR', 'JOR', 'VERSION')))


def reproducir_h001(rows, catalogo, cohortes=range(2022, 2026)):
    """Reproduce el control histórico para sus fuentes congeladas.

    El resultado cuenta filas elegibles, como la auditoría; el llamador debe
    validar si hay duplicación personal antes de llamarlas personas únicas.
    Devuelve filas en memoria para conciliación privada y nunca las escribe.
    """
    years = set(cohortes)
    by_person = defaultdict(list)
    by_program = defaultdict(list)
    for row in rows:
        by_person[(normalizar(row['ANIO_INFORMADO']), llave(row))].append(row)
    for row in catalogo:
        by_program[(normalizar(row['ANO']), normalizar(row['CODIGO_UNICO']))].append(row)
    minimums = {'Técnico de Nivel Superior': 4, 'Profesional Sin Licenciatura': 6,
                'Profesional Con Licenciatura': 8, 'Licenciatura no conducente a título': 8}
    eligible = defaultdict(list)
    for row in rows:
        year = int(row['ANIO_INFORMADO'])
        cohort = origen(row)
        if year not in years or cohort[0] != str(year) or cohort[1] not in ('1', '2') or normalizar(row['VIG']) == '0':
            continue
        candidates = by_program[('OFE_' + str(year), codigo(row))]
        if len(candidates) != 1:
            continue
        program = candidates[0]
        minimum = minimums.get(normalizar(program['NIVEL_CARRERA']))
        if (normalizar(program['NIVEL_GLOBAL']) != 'Pregrado' or
            normalizar(program['TIPO_CARRERA']) != 'Plan Regular' or
            normalizar(program['PLAN_ESPECIAL']) != 'NO APLICA' or minimum is None or
            float(program['DURACION_ESTUDIOS']) < minimum):
            continue
        current = [x for x in by_person[(str(year), llave(row))] if positivo(x) and origen(x) == cohort]
        following = [x for x in by_person[(str(year + 1), llave(row))] if positivo(x)]
        matching = [x for x in following if origen(x) == cohort]
        if len(current) > 1 or len(following) > len(matching):
            continue
        eligible[year].append((row, bool(matching)))
    return dict(eligible)
