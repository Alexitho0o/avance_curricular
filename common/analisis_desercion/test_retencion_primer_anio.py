from .retencion_primer_anio import calcular, calcular_presencia_preliminar, documento, agrupar_h001
from .h001 import reproducir_h001


def test_dv_cero():
    assert documento('R', 12345678, 0) == ('R', '12345678', '0')


def test_2025_h001_desbloqueada():
    result = calcular([], [], cohortes=[2025])
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


def test_desglose_suprime_grupo_pequeno_y_exige_sector():
    base = {'TIPO_DOC':'R','N_DOC':123,'DV':0,'ANIO_INFORMADO':2024,'ANIO_ING_ORI':2024,'SEM_ING_ORI':1,
            'COD_SED':2,'COD_CAR':1,'JOR':4,'VERSION':2,'VIG':1}
    cat = {'ANO':'OFE_2024','CODIGO_UNICO':'I162S2C1J4V2','NIVEL_GLOBAL':'Pregrado','TIPO_CARRERA':'Plan Regular',
           'PLAN_ESPECIAL':'NO APLICA','NIVEL_CARRERA':'Técnico de Nivel Superior','DURACION_ESTUDIOS':4}
    results = agrupar_h001([base], [cat], {'1':['Carrera','Sector']}, [2024])
    assert results['carrera'][0]['estado'] == 'SUPRIMIDO_UMBRAL'
    assert results['carrera'][0]['casos'] is None and results['carrera'][0]['retenidos'] is None
    try:
        agrupar_h001([base], [cat], {}, [2024])
    except ValueError as exc:
        assert 'Falta mapeo' in str(exc)
    else:
        raise AssertionError('Un código sin sector no se debe clasificar por suposición')
