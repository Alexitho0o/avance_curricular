"""H002l: regla interna D de código MU 2027; consulta sin generar cargas."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGLA = ROOT / 'data/reglas_negocio/mu2027/REGLA_CODIGO_SIES_MU2027.json'
CODE = re.compile(r'I162S\d+C\d+J\d+V\d+\Z')


def leer_fijado(ref):
    path = Path(ref['ruta']).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ref['sha256']:
        raise ValueError('Fuente alterada: ' + ref['ruta'])
    return json.loads(raw)


def resolver(fila, planes, oferta, antiguos, pendientes):
    """Núcleo puro. Datos/catálogos proporcionados por el adaptador con hashes.

    antiguos: fila fuente MU2026 -> evidencia de esa matrícula y plan observado.
    No usa documento, DV, VIG ni FOR_ING_ACT para elegir versión.
    """
    def manual(motivo):
        return {'codigo': None, 'via': 'REVISION_MANUAL', 'motivo': motivo, 'clase': 'D/E'}
    if fila.get('anio') != 2027:
        return manual('ANIO_FUERA_DE_ALCANCE')
    via = fila.get('via_solicitada')
    if via == 'ANTIGUO':
        ref = fila.get('fila_mu2026')
        if not isinstance(ref, int) or isinstance(ref, bool) or ref not in antiguos:
            return manual('ANTIGUO_1_CODIGO_O_FILA_NO_RESUELTA')
        old = antiguos[ref]
        key = (old.get('codcarpr'), old.get('plan'), old.get('sede_umas'))
        typ = planes.get(key, 'E')
        code = old.get('real')
        if not isinstance(code, str) or not CODE.fullmatch(code):
            return manual('ANTIGUO_1_CODIGO_O_FILA_NO_RESUELTA')
        current = [r for r in oferta if r['codigo_unico'] == code]
        if not current:
            return manual('ANTIGUO_2_CODIGO_SIN_OFERTA_2027')
        if len(current) != 1 or current[0]['vigencia_2027'] not in {'1', '2', '3'}:
            raise ValueError('Oferta no unívoca o vigencia no acreditada')
        if current[0]['vigencia_2027'] == '3':
            return manual('ANTIGUO_3_VIGENCIA_3')
        marks = []
        if typ not in {'1', '3'}:
            marks.append('ANTIGUO_TIPO_E_INFORMATIVO')
        if old.get('plan') in {None, '', 'PLAN_NO_OBSERVADO', 'SIN_ENLACE', 'PLAN_MULTIPLE_E'}:
            marks.append('PLAN_NO_OBSERVADO_INFORMATIVO')
        mismatch = typ in {'1', '3'} and current[0]['tipo_plan_codigo'] != typ
        return {'codigo': code, 'via': 'ANTIGUO',
                'motivo': 'CONSERVA_CODIGO_INCONSISTENTE_D' if mismatch else 'CONSERVA_FILA_MU2026_D',
                'clase': 'D', 'oferta_preparada_C': True,
                'marcas_informativas': marks}
    if via != 'NUEVO':
        return manual('OTRO_REQUIERE_REVISION')
    if fila.get('cohorte') != 2027:
        return manual('COHORTE_NO_NUEVA_2027')
    if fila.get('codigo_solicitado') in pendientes:
        return manual('CODIGO_NUEVO_SIN_PLAN')
    key = (fila.get('codcarpr'), fila.get('plan_umas'), fila.get('sede_umas'))
    typ = planes.get(key, 'E')
    fam = fila.get('familia')
    family_rows = [r for r in oferta if r['codigo_unico'].rsplit('V', 1)[0] == fam]
    if not family_rows:
        return manual('FAMILIA_SIN_OFERTA')
    if all(r['estado'] == 'FUERA_ALCANCE' for r in family_rows):
        return manual('FUERA_ALCANCE')
    if not any(r['vigencia_2027'] == '1' for r in family_rows):
        return {'codigo': None, 'via': 'INFORMATIVO', 'motivo': 'PLAN_SIN_ADMISION_2027',
                'tipo_E': typ not in {'1', '3'}, 'clase': 'D/C', 'oferta_preparada_C': True}
    if typ not in {'1', '3'}:
        return manual('NUEVO_TIPO_E_CON_ADMISION')
    # Familia previamente respaldada; un tipo compatible no crea una equivalencia.
    backed = any(any(c['codcarpr'] == key[0] and c['sede_umas'] == key[2]
                     and key[1] in c.get('planes_catalogados', c.get('planes_umas', []))
                     for c in r.get('candidatos_internos', [])) for r in family_rows)
    # Los planes se indexan en resoluciones_grupo con su clave exacta.
    backed = backed or any(any(g['codcarpr'] == key[0] and g['sede_umas'] == key[2]
                              and key[1] in g['planes_catalogados_candidatos']
                              for g in r.get('resoluciones_grupo', [])) for r in family_rows)
    backed = backed or any(any(d['codcarpr'] == key[0] and d['plan_umas'] == key[1]
                              for d in r.get('correspondencias_aprobadas_H002k', [])) for r in family_rows)
    if not backed:
        return manual('PLAN_FAMILIA_SIN_CORRESPONDENCIA')
    options = {r['codigo_unico'] for r in family_rows if r['vigencia_2027'] == '1'
               and r['tipo_plan_codigo'] == typ and r['estado'] != 'FUERA_ALCANCE'}
    if len(options) > 1:
        return manual('VARIAS_VERSIONES_VIGENTES_MISMO_TIPO')
    if options & set(pendientes):
        return manual('CODIGO_NUEVO_SIN_PLAN')
    if not options:
        return manual('REVISION_REAL_TIPO_SIN_VERSION_EN_FAMILIA_CON_ADMISION')
    return {'codigo': next(iter(options)), 'via': 'NUEVO',
            'motivo': 'VIGENCIA_1_Y_TIPO_PLAN_UNICOS_D', 'clase': 'D/C', 'oferta_preparada_C': True}


def cargar_contexto():
    rule = json.loads(REGLA.read_text())
    if rule['estado'] != 'ACTIVA' or rule['anio_proceso'] != 2027:
        raise ValueError('Regla no activa para MU 2027')
    refs = rule['fuentes']
    plan_rows = leer_fijado(refs['tipo_plan'])['filas']
    plans = {}
    for p in plan_rows:
        key = (p['codcarpr'], p['plan_umas'], p['sede_umas'])
        if key in plans and plans[key] != p['tipo_codigo']:
            raise ValueError('Tipo de plan contradictorio')
        plans[key] = p['tipo_codigo']
    offer = [r for r in leer_fijado(refs['tabla_H002'])['filas'] if r['anio'] == 2027]
    # Valida V06 aun si sus atributos se consumen a través de H002.
    ref = refs['oferta_2027']; path = ROOT / ref['ruta']
    if hashlib.sha256(path.read_bytes()).hexdigest() != ref['sha256']:
        raise ValueError('Oferta preparada alterada')
    rows = [r for r in leer_fijado(refs['prueba_privada_H002j']) if r['anio'] == 2026]
    links = {r['fila_fuente_mu']: r for r in leer_fijado(refs['enlaces_privados_H002g']) if r['anio'] == 2026}
    old = {}
    for r in rows:
        link = links[r['fila_mu']]
        selected = link['seleccion']
        if r['fila_mu'] in old:
            raise ValueError('Referencia de matrícula duplicada')
        old[r['fila_mu']] = {**r, 'sede_umas': selected[2] if selected else None}
    if len(old) != 4105:
        raise ValueError('Universo MU2026 alterado')
    pending = [r['codigo_unico'] for r in offer if r['estado'] == 'NUEVO_2027_SIN_PLAN_E']
    if len(pending) != 37:
        raise ValueError('Pendientes nuevos distintos de 37')
    return plans, offer, old, pending


def asignar_codigo_mu2027(fila):
    """Devuelve código, vía y motivo; revisión interna, nunca un archivo de carga.

    ANTIGUO: anio=2027 y referencia inequívoca fila_mu2026; tipo sólo informativo.
    El llamador acredita la clasificación; OTRO no se convierte en ANTIGUO.
    NUEVO: anio/cohorte=2027, familia SIES y clave exacta codcarpr/plan_umas/sede_umas.
    Las entradas personales y respuestas individuales deben permanecer privadas.
    """
    return resolver(fila, *cargar_contexto())
