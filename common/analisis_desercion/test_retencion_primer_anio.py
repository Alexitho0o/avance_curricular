from .retencion_primer_anio import calcular, calcular_presencia_preliminar, documento
from .h001 import reproducir_h001


def test_dv_cero():
    assert documento('R', 12345678, 0) == ('R', '12345678', '0')


def test_2025_bloqueada_sin_dos_acreditaciones():
    for opts in ({}, {'cohorte_2025_conciliada': True}, {'tratamiento_vig_aprobado': True}):
        try:
            calcular([], [], cohortes=[2025], **opts)
        except ValueError as exc:
            assert 'Cohorte 2025 bloqueada' in str(exc)
        else:
            raise AssertionError('Debe requerir ambas acreditaciones')
    result = calcular([], [], cohortes=[2025], cohorte_2025_conciliada=True, tratamiento_vig_aprobado=True)
    assert result[0]['denominador'] == 0


def test_h001_misma_cohorte_y_vig_positivo():
    row = {'TIPO_DOC':'R','N_DOC':123,'DV':0,'ANIO_INFORMADO':2024,'ANIO_ING_ORI':2024,'SEM_ING_ORI':1,
           'COD_SED':2,'COD_CAR':1,'JOR':4,'VERSION':2,'VIG':1}
    cat = {'ANO':'OFE_2024','CODIGO_UNICO':'I162S2C1J4V2','NIVEL_GLOBAL':'Pregrado','TIPO_CARRERA':'Plan Regular',
           'PLAN_ESPECIAL':'NO APLICA','NIVEL_CARRERA':'Técnico de Nivel Superior','DURACION_ESTUDIOS':4}
    next_row = dict(row, ANIO_INFORMADO=2025, VIG=0)
    assert reproducir_h001([row, next_row], [cat], [2024])[2024][0][1] is False
    next_row['VIG'] = 1
    assert reproducir_h001([row, next_row], [cat], [2024])[2024][0][1] is True
    next_row['ANIO_ING_ORI'] = 2025
    assert not reproducir_h001([row, next_row], [cat], [2024]).get(2024)


def test_2025_prototipo_presence_bloqueado():
    try:
        calcular_presencia_preliminar([], [2025])
    except ValueError:
        return
    raise AssertionError('El prototipo de presencia no debe calcular 2025')
