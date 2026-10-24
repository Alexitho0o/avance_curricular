
--- Página 1 ---
Esquema de Registro Matrícula de Educación Superior 2007-2025 por estudiante.
Bases públicas con MRUN
Unidad Responsable : Servicio de Información de Educación Superior (SIES)
Estandarización : Unidad de Estadísticas
Centro de Estudios
Ministerio de Educación
Fuente de la información : Servicio de Información de Educación Superior (SIES)
Número de observaciones por año
Año Número de observaciones
2025 1.455.639
2024 1.386.099
2023 1.341.448
2022 1.304.147
2021 1.294.701
2020 1.220.898
2019 1.268.483
2018 1.262.334
2017 1.248.293
2016 1.247.178
2015 1.233.043
2014 1.215.130
2013 1.184.371
2012 1.124.233
2011 1.066.343
2010 982.620
2009 891.719
2008 819.797
2007 776.838
1 | 8
--- Página 2 ---
Variables
El listado de variables que contienen las bases de datos descritas se detalla a continuación.
Nombre Tipo Descripción Valores
CAT_PERIODO Numérico Año del proceso
Código único de carrera o programa,
CODIGO_UNICO Cadena considerando institución, sede, carrera,
jornada y versión
MRUN Cadena Máscara del RUN del matriculado
1: Hombre
GEN_ALU Numérico Sexo del matriculado
2: Mujer
Fecha de nacimiento del matriculado
FEC_NAC_ALU Numérico 190001: valor por defecto (sin información)
(AAAAMM)
-Entre 15 y 19 años
-Entre 20 y 24 años
-Entre 25 y 29 años
Rango de edad al que pertenece la edad del
RANGO_EDAD Cadena -Entre 30 y 34 años
matriculado
-Entre 35 y 39 años
-40 y más años
-Sin Información
9995: Sin información
9998: otro programa dentro de la misma
ANIO_ING_CARR_ORI Numérico Año de ingreso a primer año institución
9999 o 1900: otro programa desde otra
institución
Semestre en que el estudiante se matricula al
SEM_ING_CARR_ORI Cadena
primer año de la carrera
9995: Sin información
9998: otro programa dentro de la misma
ANIO_ING_CARR_ACT Numérico Año de ingreso a la carrera
institución
9999: otro programa desde otra institución
Semestre del año en que el matriculado
SEM_ING_CARR_ACT Cadena
ingresó a la carrera
- Centros de Formación Técnica
Clasificación según categoría más amplia de
TIPO_INST_1 Cadena - Institutos Profesionales
instituciones de Educación Superior
- Universidades
Clasificación según categoría de institución - Centros de Formación Técnica
que distingue Universidades del Consejo de - Institutos Profesionales
TIPO_INST_2 Cadena
Rectores y Universidades Privadas que no son - Universidades CRUCH
del CRUCH - Universidades Privadas
- Centros de Formación Técnica
- Institutos Profesionales
Clasificación de la institución que distingue - Universidades Estatales CRUCH
TIPO_INST_3 Cadena categoría más amplia de instituciones y - Universidades Privadas
diferencia Universidades en Privada o Estatal - Universidades Privadas CRUCH
- Centros de Formación Técnica Estatal
- Universidades (* Carrera en Convenio)1
COD_INST Numérico Código de institución de educación superior
NOMB_INST Cadena Nombre completo de la institución
1 Corresponde a estudiantes que fueron reubicados debido a que la institución de educ. sup. En la que estaban, cerró
2 | 8
--- Página 3 ---
Nombre Tipo Descripción Valores
Código de la sede en que se imparte la
COD_SEDE Numérico
carrera o programa
NOMB_SEDE Cadena Nombre de la sede
Código de la carrera o programa que se
COD_CARRERA
imparte
NOMB_CARRERA Cadena Nombre completo de la carrera o programa
- Presencial
- Semipresencial
MODALIDAD Cadena Modo como se imparte la carrera o programa
- No presencial
- En blanco: Sin información
- Diurno
- Vespertino
Jornada en que se imparte la carrera o
JORNADA Cadena - Semipresencial
programa
- A distancia
- Otro
Versión de la carrera o programa, la que
VERSION Cadena refleja diferencias de una carrera con otra
conservando igual nombre
- Plan regular
Distinción dada por el tipo plan que posee la
TIPO_PLAN_CARR Cadena - Plan especial
carrera o programa
- Plan regular de continuidad
Duración de la carrera informada en número
DUR_ESTUDIO_CARR Numérico de semestres, sin incluir proceso de titulación
cuando está fuera del plan de estudios
Duración normal estimada en número de
semestres, del proceso de titulación que
DUR_PROCESO_TIT Numérico
deben realizar los estudiantes para obtener
el título o grado de la carrera o programa
Duración teórica o formal en semestres de la
carrera o programa, desde el momento en
DUR_TOTAL_CARR Numérico que un estudiante ingresa al primer año de la
carrera hasta que obtiene el título o grado
terminal de la misma
Región donde se ubica la sede en la cual se
REGION_SEDE Cadena
imparte la carrera
Nombre de la provincia en que se imparte la
PROVINCIA_SEDE Cadena
carrera
Comuna donde se ubica la sede en la cual se
COMUNA_SEDE Cadena
imparte la carrera
Clasificación del nivel global al que - Pregrado
NIVEL_GLOBAL Cadena pertenecen los estudios de la carrera o - Postgrado
programa - Postítulo
Clasificación del nivel específico 1 al que
NIVEL_CARRERA_1 Cadena pertenecen los estudios de la carrera o Ver Anexo I
programa
- Carreras Técnicas
Clasificación del nivel específico 2 al que - Carreras Profesionales
NIVEL_CARRERA_2 Cadena pertenecen los estudios de la carrera o - Postítulo
programa - Magister
- Doctorado
3 | 8
--- Página 4 ---
Nombre Tipo Descripción Valores
Requisito específico para ingresar a
REQUISITO_INGRESO Cadena
determinada carrera o programa
-Vigente con Alumnos Nuevos
VIGENCIA_CARRERA Cadena Tipo de vigencia de la carrera o programa -Vigente sin Alumnos Nuevos
-No Vigente
Valor en pesos que el estudiante debe pagar
VALOR_MATRICULA Cadena
para hacer efectiva su matrícula
VALOR_ARANCEL Cadena Arancel anual de la carrera o programa
Código DEMRE de la carrera o programa, solo
CODIGO_DEMRE Cadena para instituciones adscritas al Sistema Único
de Admisión SUA
- Administración y Comercio
- Agropecuaria
- Arte y Arquitectura
- Ciencias Básicas
- Ciencias Sociales
Categorización CINE-UNESCO de la carrera o
AREA_CONOCIMIENTO Cadena - Derecho
programa
- Educación
- Humanidades
- Salud
- Tecnología
- Sin área definida
Corresponde al nombre del Grupo Amplio
establecido por UNESCO en la clasificación
CINE_F_97_AREA Cadena
CINE-F de 1997, siendo utilizado por la OCDE
hasta el 2016
Corresponde a la categorización de subárea
establecido por UNESCO en la clasificación
CINE_F_97_SUBAREA Cadena
CINE-F de 1997, siendo utilizado por la OCDE
hasta el 2016.
AREA_CARRERA_GENERICA Cadena Categorización SIES de la carrera o programa
Corresponde al código de categorización de
subárea establecido por UNESCO en la
CINE_F_13_AREA Cadena
clasificación CINE-F definido el año 2013 y
siendo usado por la OCDE desde el año 2016.
Corresponde a la categorización de subárea
establecido por UNESCO en la clasificación
CINE_F_13_SUBAREA Cadena
CINE-F definido el año 2013 y siendo usado
por la OCDE desde el año 2016.
Situación de acreditación de la carrera o
programa informada por la institución al 30
- ACREDITADA
de abril del año del proceso. Para las
ACREDITADA_CARR Cadena - NO ACREDITADA
instituciones que no informan, se verifica con
- En blanco: SIN INFORMACIÓN
lo informado en proceso de Oferta
Académica.
- ACREDITADA
Situación acreditación de institución al 30 de
ACREDITADA_INST Cadena - NO ACREDITADA
abril del año en proceso
- en blanco: SIN INFORMACIÓN
Fecha de inicio y término de la acreditación
ACRE_INST_DESDE_HASTA Cadena
institucional
Número de años por la que fue acreditada la
ACRE_INST_ANIO Numérico
institución
4 | 8
--- Página 5 ---
Nombre Tipo Descripción Valores
Monto total que se cobra a los estudiantes
COSTO_PROCESO_TITULACION Cadena egresados de la carrera por concepto de
proceso de titulación
Monto que deben cancelar los estudiantes de
COSTO_OBTENCION_TITULO_D
Cadena la carrera o programa por obtener el diploma
IPLOMA
y certificado del respectivo diploma
Observaciones sobre lo que incluye el costo
COSTO_TIT_EXPLICACION_OBS del proceso de titulación, o cualquier
Cadena
ERVACION especificación para explicar o aclarar
respecto de dicho cobro
1- Ingreso Directo (regular)
2- Continuidad desde plan común o
Bachillerato.
3- Cambio Interno
4- Cambio Externo
5- Ingreso por Reconocimiento de
Aprendizajes Previos (RAP)
6- Ingreso especial para estudiantes
FORMA_DE_INGRESO Cadena Forma de ingreso a la carrera
extranjeros
7- Ingreso a través de PACE
8- Ingreso a través de programas de
inclusión
9- Ingreso por características especiales
10- Otras formas de Ingreso
11- Articulación de TNS a carrera
profesional
5 | 8
--- Página 6 ---
A continuación, se muestran las variables que están contenidas en las bases de datos según el año.
2018
Nombre 2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 -
2024
CAT_PERIODO Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
CODIGO_UNICO Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
MRUN Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
GEN_ALU Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
FEC_NAC_ALU Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
RANGO_EDAD Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
ANIO_ING_CARR_ORI Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
SEM_ING_CARR_ORI Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
ANIO_ING_CARR_ACT Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
SEM_ING_CARR_ACT Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
TIPO_INST_1 Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
TIPO_INST_2 Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
TIPO_INST_3 Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
COD_INST Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
NOMB_INST Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
COD_SEDE Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
NOMB_SEDE Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
COD_CARRERA Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
NOMB_CARRERA Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
MODALIDAD No No No No Sí Sí Sí Sí Sí Sí Sí Sí
JORNADA Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
VERSION Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
TIPO_PLAN_CARR Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
DUR_ESTUDIO_CARR Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
DUR_PROCESO_TIT Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
DUR_TOTAL_CARR Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
REGION_SEDE Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
PROVINCIA_SEDE Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
COMUNA_SEDE Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
NIVEL_GLOBAL Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
NIVEL_CARRERA_1 Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
NIVEL_CARRERA_2 Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
REQUISITO_INGRESO No No No No No No No No Sí Sí Sí Sí
VIGENCIA_CARRERA No No No No No No No No Sí Sí Sí Sí
VALOR_MATRICULA Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
VALOR_ARANCEL Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
CODIGO_DEMRE Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
AREA_CONOCIMIENTO Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
CINE_F_97_AREA Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
6 | 8
--- Página 7 ---
2018
Nombre 2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 -
2024
CINE_F_97_SUBAREA Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
AREA_CARRERA_GENERICA Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
CINE_F_13_AREA Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
CINE_F_13_SUBAREA Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
ACREDITADA_CARR Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
ACREDITADA_INST Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí Sí
ACRE_INST_DESDE_HASTA Sí Sí No No Sí Sí Sí Sí Sí Sí Sí Sí
ACRE_INST_ANIO Sí Sí No No Sí Sí Sí Sí Sí Sí Sí Sí
COSTO_PROCESO_TITULACION No No No No No Sí Sí Sí Sí Sí Sí Sí
COSTO_OBTENCION_TITULO_DIPLOMA No No No No No Sí Sí Sí Sí Sí Sí Sí
COSTO_TIT_EXPLICACION_OBSERVACION No No No No No Sí Sí Sí Sí Sí Sí No
FORMA_DE_INGRESO No No No No No No No No No No No Sí
7 | 8
--- Página 8 ---
ANEXO I
NIVEL CARRERA 1
BACHILLERATO, CICLO INICIAL O PLAN COMÚN
DIPLOMADO (superior a un semestre)
DOCTORADO
ESPECIALIDAD MÉDICA U ODONTOLÓGICA
LICENCIATURA NO CONDUCENTE A TÍTULO
MAGISTER
POSTÍTULO
PROFESIONAL CON LICENCIATURA PREVIA
PROFESIONAL SIN LICENCIATURA PREVIA
TÉCNICO DE NIVEL SUPERIOR
Volver al inicio
8 | 8