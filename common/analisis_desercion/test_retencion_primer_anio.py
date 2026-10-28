from .retencion_primer_anio import documento,calcular
def test_dv_cero(): assert documento('R',12345678,0)==('R','12345678','0')
def test_persona_una_vez():
 rows=[{'TIPO_DOC':'R','N_DOC':1,'DV':'0','ANIO_INFORMADO':2022,'ANIO_ING_ACT':2022,'VIG':1},{'TIPO_DOC':'R','N_DOC':1,'DV':'0','ANIO_INFORMADO':2023,'ANIO_ING_ACT':2022,'VIG':1}]
 assert calcular(rows)[0]['denominador']==1 and calcular(rows)[0]['retenidos']==1
def test_presencia_t_mas_1_con_cualquier_vig():
 rows=[{'TIPO_DOC':'R','N_DOC':2,'DV':'0','ANIO_INFORMADO':2022,'ANIO_ING_ACT':2022,'VIG':1},{'TIPO_DOC':'R','N_DOC':2,'DV':'0','ANIO_INFORMADO':2023,'ANIO_ING_ACT':2022,'VIG':0}]
 assert calcular(rows)[0]['retenidos']==1
