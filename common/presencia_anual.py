"""Reglas de evidencia académica anual, sin interpolación de matrícula."""
from scripts.fuentes_ensayo_enlace_conjunto import doc, token, year


def evaluar_nota(row, alumnos):
    """Clasifica una nota; alumnos contiene solo igual CODCLI y carrera."""
    y = year(row.get('ANO'))
    if y is None: return 'ANIO_NO_COMPARABLE', None
    if token(row.get('CONVALIDADO')).upper() in {'S','SI','SÍ','1','TRUE'}:
        return 'CONVALIDACION', None
    if token(row.get('DESCRIPCION_ESTADO')).upper() not in {'APROBADO','REPROBADO'}:
        return 'SIN_RESULTADO_ACADEMICO', None
    if not alumnos: return 'SIN_EXPEDIENTE_MISMA_CARRERA', None
    person = doc(row.get('RUT')) or doc(row.get('RUT'), row.get('DIG'))
    people = {doc(r.get('RUT')) for r in alumnos}
    if not person or None in people: return 'DOCUMENTO_NO_COMPARABLE', None
    if people != {person}: return 'CONFLICTO_DOCUMENTO', None
    return 'ACTIVIDAD_VERIFICADA', y
