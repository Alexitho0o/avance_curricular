# HITO 2B - Diccionario oficial y comparacion contra estructura CSV IRE 2026

## 1. Identificacion

- Proceso: Infraestructura y Recursos Educacionales.
- Subproyecto: IRE 2026.
- Ano proceso: 2026.
- Fecha referencia datos: 30 de junio de 2026.
- Fuente oficial: `01_fuentes_oficiales/instructivos/20260707_87395_Infraestructura_y_Recursos_Educacionales_2026_SIES_-_Instructivo_2026.txt`.
- Estructura tecnica: `01_fuentes_oficiales/estructuras_tecnicas/20260706_89535_Estructura_IRE_ID_16770.csv`.
- Hash instructivo: `2fa7f09fcdc23b706765e81333ed91e800dcc3423defc34503cb4e7ccb583637`.
- Hash estructura: `117babcfd945589969f6d508ff9e173214854ac4355df526a61b09de1061deae`.
- Nivel de respaldo: ALTO para coincidencia nominal y contenido del Anexo I; ALTO_CON_OBSERVACION en contradicciones expresas.

## 2. Objetivo del hito

Construir un diccionario estructurado y auditable de los 54 campos IRE 2026, extraido del instructivo oficial y comparado con la estructura tecnica CSV, sin modificar fuentes ni generar archivo de carga.

## 3. Entradas utilizadas

- `01_fuentes_oficiales/instructivos/20260707_87395_Infraestructura_y_Recursos_Educacionales_2026_SIES_-_Instructivo_2026.txt`
- `01_fuentes_oficiales/estructuras_tecnicas/20260706_89535_Estructura_IRE_ID_16770.csv`
- `07_resultados/reportes_auditoria/HITO_2A_LECTURA_FUNCIONAL_INSTRUCTIVO_IRE_2026_20260709_145724.md`
- `06_validaciones/reglas_funcionales/HITO_2A_REGLAS_FUNCIONALES_INICIALES_IRE_2026_20260709_145724.json`

## 4. Resumen ejecutivo

- Campos CSV detectados: 54.
- Campos con respaldo oficial claro y sin contradiccion de campo: 48.
- Campos con observaciones de contradiccion: 6.
- Campos solo CSV: 0.
- Campos solo instructivo: 1 (`CODIGO_INSTITUCION`, variable de clave acumulativa, no campo formal del Anexo I).
- Coincidencias nominales exactas instructivo/CSV: 54.
- Estado: COMPLETADO_CON_OBSERVACIONES.

## 5. Diccionario por bloques funcionales

Los bloques son una clasificacion tecnica de trabajo; el instructivo organiza secciones equivalentes, pero no define estos nombres normalizados.

| N_ORDEN | COLUMNA_CSV | BLOQUE_FUNCIONAL | DESCRIPCION_OFICIAL_RESUMIDA | OBLIGATORIEDAD | CONDICION | VALORES | ESTADO_CAMPO |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | TIPO_INFRAESTRUCTURA | IDENTIFICACION_INFRAESTRUCTURA | Tipo de infraestructura y recursos educacionales con que se identifica el registro informado. | OBLIGATORIO | Determina los restantes campos que corresponde completar. | 1, 2, 3, 4, 5 o 6 | OK_OFICIAL_Y_CSV |
| 2 | NOMBRE_IDENTIFICACION | IDENTIFICACION_INFRAESTRUCTURA | Nombre con que la institucion identifica el inmueble, recurso educacional, biblioteca o predio informado. | OBLIGATORIO | Para tipo 4 se asigna a biblioteca digital o, si no existe, casa central; para tipo 6, sede central o administrativa principal. | Letras mayusculas A-Z sin acentos y numeros | OK_OFICIAL_Y_CSV |
| 3 | COMUNA | UBICACION | Comuna en que se encuentra el inmueble informado. | OBLIGATORIO | Para tipos 4 y 6 se usa la ubicacion institucional indicada por el instructivo. | Letras mayusculas A-Z sin acentos | OK_OFICIAL_Y_CSV |
| 4 | DIRECCION_INMUEBLE | UBICACION | Nombre de calle y numeracion completa de la ubicacion fisica del inmueble informado. | OBLIGATORIO | Para tipos 4 y 6 se usa la ubicacion institucional indicada por el instructivo. | Letras mayusculas A-Z sin acentos y numeros | OK_OFICIAL_Y_CSV |
| 5 | SITUACION_TENENCIA | TENENCIA_USO | Figura bajo la cual la institucion mantiene posesion o tenencia del inmueble de uso permanente. | CONDICIONAL_OBLIGATORIO | Solo para inmuebles de uso permanente. | 1 a 6 | OK_OFICIAL_Y_CSV |
| 6 | ANIO_INICIO_USO_INMUEBLE | TENENCIA_USO | Ano en que la institucion comenzo a utilizar el inmueble informado. | CONDICIONAL_OBLIGATORIO | Solo para inmuebles de uso permanente. | 1800 a 2026 | OK_OFICIAL_Y_CSV |
| 7 | USO_EXCLUSIVO | TENENCIA_USO | Indica si el inmueble es de uso exclusivo de la institucion o compartido con otra institucion. | CONDICIONAL_OBLIGATORIO | Solo para inmuebles de uso permanente. | 1 o 2 | OK_OFICIAL_Y_CSV |
| 8 | PORCENTAJE_USO | TENENCIA_USO | Estimacion del porcentaje de uso del inmueble por la institucion; los porcentajes de todas las instituciones suman 100%. | CONDICIONAL_OBLIGATORIO | Aplica a inmueble de uso permanente compartido. | 1 a 99 | OK_OFICIAL_Y_CSV |
| 9 | NOMBRE_INSTITUCION_COMPARTE | TENENCIA_USO | Nombre de la o las instituciones con las que se comparte el inmueble. | CONDICIONAL_OBLIGATORIO | Aplica a inmueble de uso permanente compartido. | Letras mayusculas A-Z | OK_OFICIAL_Y_CSV |
| 10 | FECHA_INICIO_TENENCIA | TENENCIA_USO | Fecha de inicio de arriendo, comodato, usufructo, leasing o leaseback segun contrato. | CONDICIONAL_OBLIGATORIO | Para inmuebles de uso permanente no propios, SITUACION_TENENCIA 2,3,4,5 o 6. | Fecha valida anterior a julio de 2026 | OK_OFICIAL_Y_CSV |
| 11 | FECHA_TERMINO | TENENCIA_USO | Fecha de expiracion del arriendo, comodato, usufructo, leasing o leaseback segun contrato. | CONDICIONAL_OBLIGATORIO | Se exige para SITUACION_TENENCIA 2,3,4 y 5; el instructivo no explicita exigencia para 6. | Fecha valida posterior a mayo de 2026 | OK_OFICIAL_Y_CSV |
| 12 | DESCRIPCION_OTRA_TENENCIA | TENENCIA_USO | Explicacion clara de la situacion de tenencia informada como Otra. | CONDICIONAL_OBLIGATORIO | Solo cuando SITUACION_TENENCIA=6 en inmueble de uso permanente. | Letras mayusculas A-Z sin acentos | OK_OFICIAL_Y_CSV |
| 13 | FUNCION_DOCENCIA | FUNCIONES_INMUEBLE | Inmueble destinado a actividades directamente relacionadas con ensenanza-aprendizaje. | CONDICIONAL | Para tipo 1 debe marcarse al menos una funcion principal. | X cuando corresponda | OK_OFICIAL_Y_CSV |
| 14 | FUNCION_INVESTIGACION | FUNCIONES_INMUEBLE | Inmueble destinado a actividades relacionadas con investigacion academica. | CONDICIONAL | Para tipo 1 debe marcarse al menos una funcion principal. | X cuando corresponda | OK_OFICIAL_Y_CSV |
| 15 | FUNCION_EXTENSION | FUNCIONES_INMUEBLE | Inmueble destinado a actividades de extension artistica, cultural, formativa u otras. | CONDICIONAL | Para tipo 1 debe marcarse al menos una funcion principal. | X cuando corresponda | OK_OFICIAL_Y_CSV |
| 16 | FUNCION_ADM_OFICINAS | FUNCIONES_INMUEBLE | Inmueble destinado a actividades de administracion o gestion institucional. | CONDICIONAL | Para tipo 1 debe marcarse al menos una funcion principal. | X cuando corresponda | OK_OFICIAL_Y_CSV |
| 17 | FUNCION_OTRAS | FUNCIONES_INMUEBLE | Inmueble destinado a actividades distintas de las categorias anteriores. | CONDICIONAL | Para tipo 1 debe marcarse al menos una funcion principal. | X cuando corresponda | OK_OFICIAL_Y_CSV |
| 18 | DESC_OTRAS_FUNCIONES | FUNCIONES_INMUEBLE | Breve descripcion de otras funciones desarrolladas en el inmueble. | CONDICIONAL_OBLIGATORIO | Vinculado bidireccionalmente con FUNCION_OTRAS. | Letras mayusculas A-Z sin acentos | OK_OFICIAL_Y_CSV |
| 19 | TOTAL_M2_TERRENO | SUPERFICIE_GENERAL | Total de metros cuadrados de terreno del inmueble informado. | CONDICIONAL_CONTRADICTORIO | Caracteristica de inmueble de uso permanente. | Numero no negativo; maximo un decimal | CONTRADICCION |
| 20 | TOTAL_M2_EDIFICADOS | SUPERFICIE_GENERAL | Total de metros cuadrados edificados del inmueble. | CONDICIONAL_OBLIGATORIO | Caracteristica de inmueble de uso permanente. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 21 | TOTAL_SALAS_CLASES | SALAS_AUDITORIOS_LABORATORIOS_TALLERES | Suma de salas de clases, excluidos talleres, laboratorios y auditorios. | CONDICIONAL_OBLIGATORIO | Caracteristica de inmueble de uso permanente. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 22 | CAPACIDAD_SALAS_CLASES | SALAS_AUDITORIOS_LABORATORIOS_TALLERES | Suma de capacidades de estudiantes de las salas, medida por pupitres o sillas disponibles simultaneamente. | CONDICIONAL_OBLIGATORIO | Caracteristica de inmueble de uso permanente. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 23 | TOTAL_M2_SALAS_CLASES | SALAS_AUDITORIOS_LABORATORIOS_TALLERES | Suma de metros cuadrados de todas las salas de clases. | CONDICIONAL_OBLIGATORIO | Caracteristica de inmueble de uso permanente. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 24 | TOTAL_AUDITORIOS | SALAS_AUDITORIOS_LABORATORIOS_TALLERES | Suma de auditorios disponibles en el inmueble. | CONDICIONAL_OBLIGATORIO | Caracteristica de inmueble de uso permanente. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 25 | CAPACIDAD_AUDITORIOS | SALAS_AUDITORIOS_LABORATORIOS_TALLERES | Suma de asistentes sentados que admiten todos los auditorios. | CONDICIONAL_OBLIGATORIO | Caracteristica de inmueble de uso permanente. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 26 | TOTAL_M2_AUDITORIOS | SALAS_AUDITORIOS_LABORATORIOS_TALLERES | Suma de metros cuadrados de todos los auditorios. | CONDICIONAL_OBLIGATORIO | Caracteristica de inmueble de uso permanente. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 27 | TOTAL_LABORATORIOS | SALAS_AUDITORIOS_LABORATORIOS_TALLERES | Suma de laboratorios del inmueble. | CONDICIONAL_OBLIGATORIO | Caracteristica de inmueble de uso permanente. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 28 | TOTAL_M2_LABORATORIOS | SALAS_AUDITORIOS_LABORATORIOS_TALLERES | Suma de metros cuadrados de laboratorios. | CONDICIONAL_OBLIGATORIO | Caracteristica de inmueble de uso permanente. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 29 | TOTAL_TALLERES | SALAS_AUDITORIOS_LABORATORIOS_TALLERES | Suma de talleres del inmueble. | CONDICIONAL_OBLIGATORIO | Caracteristica de inmueble de uso permanente. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 30 | TOTAL_M2_TALLERES | SALAS_AUDITORIOS_LABORATORIOS_TALLERES | Suma de metros cuadrados de talleres. | CONDICIONAL_OBLIGATORIO | Caracteristica de inmueble de uso permanente. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 31 | TOTAL_PC_NB_DISPONIBLE | EQUIPAMIENTO_COMPUTACIONAL | Suma de computadores PC y notebooks disponibles para estudiantes. | CONDICIONAL_OBLIGATORIO | Caracteristica de inmueble de uso permanente. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 32 | TOTAL_M2_CASINOS_CAFETERIAS | CASINOS_AREAS_VERDES | Suma de metros cuadrados de casinos, patios de comida y cafeterias dentro del inmueble. | CONDICIONAL_OBLIGATORIO | Caracteristica de inmueble de uso permanente. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 33 | TOTAL_M2_AREAS_VERDES | CASINOS_AREAS_VERDES | Suma de metros cuadrados de areas verdes y de esparcimiento del inmueble. | CONDICIONAL_OBLIGATORIO | Caracteristica de inmueble de uso permanente. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 34 | UR_DESC_ACTIVIDADES | USO_RESTRINGIDO_PREDIO | Especificacion de las principales actividades o funciones desarrolladas en el inmueble de uso restringido. | CONDICIONAL_OBLIGATORIO | Caracteristica de inmueble de uso restringido. | Letras mayusculas A-Z sin acentos y numeros | OK_OFICIAL_Y_CSV |
| 35 | UR_TOTAL_M2_TERRENO | USO_RESTRINGIDO_PREDIO | Metros cuadrados de terreno del inmueble de uso restringido; si corresponde a predio, se informa en hectareas. | CONDICIONAL_OBLIGATORIO | Caracteristica de inmueble de uso restringido. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 36 | UR_TOTAL_M2_CONSTRUIDOS | USO_RESTRINGIDO_PREDIO | Metros cuadrados edificados del inmueble de uso restringido; el Anexo I senala que eventualmente en predios puede quedar en blanco. | CONDICIONAL_OBLIGATORIO | Caracteristica de inmueble de uso restringido. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 37 | UR_SITUACION_TENENCIA | USO_RESTRINGIDO_PREDIO | Indica si el inmueble de uso restringido es arrendado o se usa bajo otra figura. | CONDICIONAL_OBLIGATORIO | Caracteristica de inmueble de uso restringido. | 1 o 2 | OK_OFICIAL_Y_CSV |
| 38 | UR_DESC_TENENCIA_OTRA | USO_RESTRINGIDO_PREDIO | Explicacion de la figura bajo la cual la institucion usa el inmueble de uso restringido cuando la tenencia es Otra. | CONDICIONAL_AMBIGUO | Caracteristica de inmueble de uso restringido cuando UR_SITUACION_TENENCIA=2. | Letras mayusculas A-Z sin acentos y numeros | CONTRADICCION |
| 39 | TOTAL_M2_BIBLIOTECA | BIBLIOTECA | Suma de metros cuadrados construidos de la biblioteca. | CONDICIONAL_OBLIGATORIO | Caracteristica de biblioteca. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 40 | TOTAL_M2_SALAS_LECTURA | BIBLIOTECA | Total de metros cuadrados de salas de lectura de la biblioteca. | CONDICIONAL_OBLIGATORIO | Caracteristica de biblioteca. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 41 | TOTAL_PROFESIONALES_BIBLIOTECA | BIBLIOTECA | Numero de profesionales bibliotecarios o similares contratados para gestion o atencion. | CONDICIONAL_OBLIGATORIO | Caracteristica de biblioteca. | Numero entero no negativo | OK_OFICIAL_Y_CSV |
| 42 | HORAS_PERSONAL_BIBLIOTECA | BIBLIOTECA | Suma de horas semanales contratadas de profesionales de biblioteca, prorrateadas cuando atienden varias bibliotecas. | CONDICIONAL_OBLIGATORIO | Caracteristica de biblioteca. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 43 | TOTAL_TITULOS_DISPONIBLES | BIBLIOTECA | Suma de titulos fisicos disponibles en la coleccion de la biblioteca. | CONDICIONAL_OBLIGATORIO | Caracteristica de biblioteca. | Numero entero no negativo | OK_OFICIAL_Y_CSV |
| 44 | TOTAL_VOLUMENES_DISPONIBLES | BIBLIOTECA | Suma de volumenes fisicos disponibles en la coleccion de la biblioteca. | CONDICIONAL_OBLIGATORIO | Caracteristica de biblioteca. | Numero entero no negativo | OK_OFICIAL_Y_CSV |
| 45 | TOTAL_SUSCRIPCIONES_REVISTAS | BIBLIOTECA | Numero de suscripciones o canjes a revistas fisicas de la biblioteca. | CONDICIONAL_OBLIGATORIO | Caracteristica de biblioteca. | Numero entero no negativo | OK_OFICIAL_Y_CSV |
| 46 | TOTAL_TITULOS_LIBROS_DIGITALES | RECURSOS_BIBLIOGRAFICOS_DIGITALES | Numero total de titulos de libros digitales o electronicos completos incorporados a la coleccion. | CONDICIONAL_OBLIGATORIO | Caracteristica de libros y bases digitales. | Numero entero no negativo | OK_OFICIAL_Y_CSV |
| 47 | TOTAL_SUSCRIPCIONES_DIGITALES | RECURSOS_BIBLIOGRAFICOS_DIGITALES | Numero de suscripciones o canjes a revistas electronicas. | CONDICIONAL_OBLIGATORIO | Caracteristica de libros y bases digitales. | Numero entero no negativo | OK_OFICIAL_Y_CSV |
| 48 | TOTAL_BASE_DATOS | RECURSOS_BIBLIOGRAFICOS_DIGITALES | Numero de suscripciones de acceso a bases de datos especializadas. | CONDICIONAL_OBLIGATORIO | Caracteristica de libros y bases digitales. | Numero entero no negativo | OK_OFICIAL_Y_CSV |
| 49 | TOTAL_HECTAREAS_PREDIO | USO_RESTRINGIDO_PREDIO | Numero total de hectareas del predio informado. | CONDICIONAL_OBLIGATORIO | Informacion de predios. | Numero no negativo; maximo un decimal | OK_OFICIAL_Y_CSV |
| 50 | SISTEMA_GESTION_APRENDIZAJES | PLATAFORMAS_VIRTUALES | Identificacion del software LMS o LCMS usado para gestionar procesos de formacion educativa en linea. | CONDICIONAL_OBLIGATORIO | Informacion institucional de plataformas virtuales en una unica linea. | Anexo I: texto abierto; Anexo III: puede contener letras A-Z | CONTRADICCION |
| 51 | SISTEMA_VIDEO_CONFERENCIA | PLATAFORMAS_VIRTUALES | Identificacion del software de videoconferencia usado para clases en linea. | CONDICIONAL_OBLIGATORIO | Informacion institucional de plataformas virtuales en una unica linea. | Anexo I: texto abierto; Anexo III: puede contener letras A-Z | CONTRADICCION |
| 52 | SISTEMA_APLICACION_EVALUACION | PLATAFORMAS_VIRTUALES | Software o sistema usado para aplicar y evaluar examenes o pruebas en linea. | CONDICIONAL_OBLIGATORIO | Informacion institucional de plataformas virtuales en una unica linea. | Anexo I: texto abierto; Anexo III: puede contener letras A-Z | CONTRADICCION |
| 53 | DESCRIPCION_PLATAFORMA_VIRTUAL | PLATAFORMAS_VIRTUALES | Explicacion sobre la forma de uso de la plataforma virtual, especialmente si se usa mas de un sistema. | CONDICIONAL_OBLIGATORIO | Informacion institucional de plataformas virtuales en una unica linea. | Anexo I: texto abierto; Anexo III: puede contener letras A-Z | CONTRADICCION |
| 54 | VIGENCIA | VIGENCIA | Variable usada para mantener o eliminar un registro cargado. | OBLIGATORIO | Aplica a todos los tipos y no puede quedar vacio. | 0 o 1 | OK_OFICIAL_Y_CSV |

## 6. Comparacion instructivo vs CSV

| Estado | Cantidad | Alcance |
| --- | ---: | --- |
| `OK_OFICIAL_Y_CSV` | 48 | Coincidencia exacta y regla oficial utilizable. |
| `OK_CSV_SIN_DETALLE_OFICIAL_COMPLETO` | 0 | Ninguno. |
| `SOLO_CSV` | 0 | Ninguno. |
| `SOLO_INSTRUCTIVO` | 1 | CODIGO_INSTITUCION, mencionado solo como parte de la clave acumulativa de PES. |
| `CONTRADICCION` | 6 | TOTAL_M2_TERRENO, UR_DESC_TENENCIA_OTRA y cuatro campos de plataformas virtuales. |
| `PENDIENTE_REVISION` | 0 | Ninguno como estado exclusivo; los pendientes globales se detallan en secciones 9 y 10. |

La matriz CSV contiene 55 entradas: 54 coincidencias campo a campo y una variable solo mencionada en el instructivo. `CODIGO_INSTITUCION` no se incorpora al diccionario de carga porque no figura en el Anexo I ni en la estructura tecnica.

## 7. Reglas por tipo de infraestructura

Esta matriz es preliminar y debe convertirse en una matriz exhaustiva campo por tipo en HITO 2C.

| TIPO_INFRAESTRUCTURA | SIGNIFICADO | CAMPOS_QUE_APLICAN | CAMPOS_QUE_NO_APLICAN | PENDIENTES |
| ---: | --- | --- | --- | --- |
| 1 | Inmuebles de Uso Permanente | TIPO_INFRAESTRUCTURA, NOMBRE_IDENTIFICACION, COMUNA, DIRECCION_INMUEBLE; SITUACION_TENENCIA a DESC_OTRAS_FUNCIONES; TOTAL_M2_TERRENO a TOTAL_M2_AREAS_VERDES; VIGENCIA | UR_DESC_ACTIVIDADES a UR_DESC_TENENCIA_OTRA; TOTAL_M2_BIBLIOTECA a DESCRIPCION_PLATAFORMA_VIRTUAL | Precisar excepcion de TOTAL_M2_TERRENO para departamentos, oficinas o plantas. |
| 2 | Inmuebles de Uso Restringido | TIPO_INFRAESTRUCTURA, NOMBRE_IDENTIFICACION, COMUNA, DIRECCION_INMUEBLE; UR_DESC_ACTIVIDADES a UR_DESC_TENENCIA_OTRA; VIGENCIA | Bloques de uso permanente, funciones, caracteristicas del inmueble, biblioteca, libros y bases digitales, predios y plataformas virtuales | Confirmar condicion correcta de UR_DESC_TENENCIA_OTRA. |
| 3 | Caracteristicas de Biblioteca | TIPO_INFRAESTRUCTURA, NOMBRE_IDENTIFICACION, COMUNA, DIRECCION_INMUEBLE; TOTAL_M2_BIBLIOTECA a TOTAL_SUSCRIPCIONES_REVISTAS; VIGENCIA | Bloques de uso permanente, uso restringido, libros y bases digitales, predios y plataformas virtuales | Ninguno adicional identificado en este hito. |
| 4 | Caracteristicas de Libros y Bases Digitales | TIPO_INFRAESTRUCTURA, NOMBRE_IDENTIFICACION, COMUNA, DIRECCION_INMUEBLE; TOTAL_TITULOS_LIBROS_DIGITALES a TOTAL_BASE_DATOS; VIGENCIA | Bloques de uso permanente, uso restringido, biblioteca fisica, predios y plataformas virtuales | Ninguno adicional identificado en este hito. |
| 5 | Predios | TIPO_INFRAESTRUCTURA, NOMBRE_IDENTIFICACION, COMUNA, DIRECCION_INMUEBLE; TOTAL_HECTAREAS_PREDIO; VIGENCIA | Bloques de uso permanente, uso restringido, biblioteca, libros y bases digitales y plataformas virtuales | Ninguno adicional identificado en este hito. |
| 6 | Plataformas Virtuales | TIPO_INFRAESTRUCTURA, NOMBRE_IDENTIFICACION, COMUNA, DIRECCION_INMUEBLE; SISTEMA_GESTION_APRENDIZAJES a DESCRIPCION_PLATAFORMA_VIRTUAL; VIGENCIA | Bloques de uso permanente, uso restringido, biblioteca, libros y bases digitales y predios | Confirmar caracteres permitidos frente a texto abierto del Anexo I. |

## 8. Reglas de vigencia

- `VIGENCIA` es obligatorio para todos los registros y tipos de infraestructura.
- Valor `0`: eliminar un registro cargado.
- Valor `1`: mantener un registro cargado.
- La carga es acumulativa: la combinacion Codigo de Institucion, Tipo de Infraestructura, Nombre de Identificacion, Comuna y Direccion del Inmueble reemplaza el resto de los datos si vuelve a cargarse.
- Queda pendiente confirmar el tratamiento operativo de `VIGENCIA` en una primera carga.

## 9. Contradicciones detectadas

1. El instructivo exige CSV delimitado por comas, mientras la estructura tecnica original observada usa punto y coma.
2. El instructivo dice que todos los campos deben cargarse, pero tambien ordena no completar bloques o campos segun TIPO_INFRAESTRUCTURA.
3. TOTAL_M2_TERRENO se exige para tipo 1 en Anexo III, pero la definicion permite omitirlo en departamentos, oficinas o plantas dentro de un edificio.
4. UR_DESC_TENENCIA_OTRA se condiciona en Anexo III a que el propio campo sea igual a 2, aunque es un campo descriptivo; no se corrige por supuesto.
5. Los cuatro campos de plataformas se definen como texto abierto en Anexo I, mientras Anexo III solo explicita letras A-Z.
6. La codificacion del archivo de carga no esta indicada oficialmente.

## 10. Validaciones derivadas

### Validaciones oficiales directas

- Los 54 nombres y su orden deben coincidir exactamente con la estructura tecnica.
- `TIPO_INFRAESTRUCTURA` pertenece a 1..6 y determina los bloques permitidos.
- Nombre, comuna y direccion son obligatorios; `VIGENCIA` no puede quedar vacio y pertenece a {0,1}.
- Fechas de tenencia usan `AAAA-MM`; inicio debe ser anterior a julio de 2026 y termino posterior a mayo de 2026 cuando corresponda.
- Para tipo 1 debe existir al menos una funcion principal; las funciones se marcan con `X`.
- `TOTAL_M2_SALAS_CLASES <= TOTAL_M2_EDIFICADOS`, `TOTAL_M2_SALAS_LECTURA <= TOTAL_M2_BIBLIOTECA` y `TOTAL_TITULOS_DISPONIBLES <= TOTAL_VOLUMENES_DISPONIBLES`.

### Validaciones tecnicas sugeridas

- Validar tipos, dominios, formatos, precision decimal y dependencias condicionales usando este diccionario como metadato versionado.
- Validar por separado presencia de columna y presencia de valor para no confundir todos los campos deben cargarse con no completar campos no aplicables.
- Mantener sin automatizar las seis contradicciones de campo hasta su resolucion documentada.

### Validaciones pendientes

- Resolver el delimitador efectivo de carga mediante antecedente oficial o prueba controlada posterior; no asumir coma ni punto y coma.
- Confirmar la codificacion aceptada por PES.
- Confirmar si CODIGO_INSTITUCION es metadato inyectado por PES o un campo omitido de la estructura descargada; no agregarlo al CSV sin respaldo.
- Resolver la excepcion de TOTAL_M2_TERRENO para departamentos, oficinas o plantas.
- Confirmar que la condicion correcta de UR_DESC_TENENCIA_OTRA es UR_SITUACION_TENENCIA=2.
- Precisar el conjunto real de caracteres admitidos en campos de plataformas virtuales.
- Construir en HITO 2C la matriz exhaustiva campo por tipo con estados completar, no completar, cero, blanco y condicional.

## 11. Archivos generados

- `03_diccionarios/HITO_2B_DICCIONARIO_OFICIAL_CAMPOS_IRE_2026_20260709_233948.csv`
- `03_diccionarios/HITO_2B_DICCIONARIO_OFICIAL_CAMPOS_IRE_2026_20260709_233948.json`
- `07_resultados/reportes_auditoria/HITO_2B_COMPARACION_DICCIONARIO_VS_ESTRUCTURA_IRE_2026_20260709_233948.md`
- `06_validaciones/estructura/HITO_2B_COMPARACION_CAMPOS_INSTRUCTIVO_VS_CSV_IRE_2026_20260709_233948.csv`
- `08_logs/ejecuciones/HITO_2B_LOG_EJECUCION_20260709_233948.txt`

## 12. Dictamen del hito

- Estado HITO 2B: COMPLETADO_CON_OBSERVACIONES.
- Quedo consolidado el diccionario de los 54 campos, con coincidencia nominal exacta contra el CSV y trazabilidad de lineas.
- Quedaron explicitas seis contradicciones de campo, dos contradicciones globales y la ausencia de codificacion oficial.
- No debe asumirse el delimitador efectivo de carga, la codificacion PES, la correccion de la regla UR ni la incorporacion de CODIGO_INSTITUCION al archivo.
- No se modificaron fuentes originales ni se genero archivo de carga.

## 13. Proximo hito sugerido

HITO 2C - PROMPT - Construccion de matriz funcional campo por tipo de infraestructura y reglas completar / no completar para IRE 2026.
