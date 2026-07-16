# HITO 2A - Lectura funcional controlada del instructivo oficial IRE 2026

## 1. Identificacion del proceso

- Proceso: Infraestructura y Recursos Educacionales.
- Subproyecto: IRE 2026.
- Año del proceso: 2026.
- Año o fecha de referencia de datos: 30 de junio de 2026.
- Fuente oficial: `01_fuentes_oficiales/instructivos/20260707_87395_Infraestructura_y_Recursos_Educacionales_2026_SIES_-_Instructivo_2026.txt`.
- Hash SHA-256: `2fa7f09fcdc23b706765e81333ed91e800dcc3423defc34503cb4e7ccb583637`.
- Nivel de respaldo: Fuente oficial local incorporada en HITO 1A, con hash verificado en HITO 1B y nuevamente en HITO 2A.

## 2. Alcance oficial del proceso

### Que debe informarse

- Todos los inmuebles, locales y dependencias utilizados por la institucion para sus actividades.
- Predios y similares usados por la institucion.
- Recursos educacionales ligados a dichos inmuebles.
- Laboratorios, talleres y computadores disponibles para estudiantes.
- Bibliotecas, colecciones fisicas, libros digitales, suscripciones digitales y bases de datos.
- Plataformas virtuales institucionales para aprendizaje, videoconferencia y evaluacion online.

### Que no queda claro

- No queda definido en el instructivo un inventario institucional de registros esperados; debera construirse o contrastarse con fuentes internas posteriores.
- No queda resuelta la diferencia entre CSV delimitado por comas indicado en el instructivo y estructura tecnica observada con `;`.
- No se indica codificacion requerida para el archivo CSV.

### Que debe confirmarse despues

- Extraer diccionario oficial campo a campo desde Anexo I en formato estructurado.
- Comparar el diccionario oficial contra los 54 encabezados del CSV de estructura.
- Resolver delimitador efectivo para archivo candidato de carga: coma indicada oficialmente versus punto y coma observado tecnicamente.
- Definir matriz campo x TIPO_INFRAESTRUCTURA con obligatorio, permitido, prohibido, cero o blanco.
- Confirmar codificacion esperada de PES, porque el instructivo no la indica.
- Confirmar tratamiento operativo de VIGENCIA en primera carga y en cargas acumulativas.

## 3. Temporalidad y fechas relevantes

- Fecha de referencia de los datos: 30 de junio de 2026. Clasificacion: A. REGLA OFICIAL.
- Plazo de carga: 24 de julio de 2026. Clasificacion: A. REGLA OFICIAL.
- Año de proceso: 2026. Clasificacion: A. REGLA OFICIAL.
- Año de datos: 2026, con corte al 30 de junio de 2026. Clasificacion: A. REGLA OFICIAL.
- Fechas asociadas a tenencia: `FECHA_INICIO_TENENCIA` y `FECHA_TERMINO` usan formato `AAAA-MM`; inicio debe ser previa a julio de 2026 y termino posterior a mayo de 2026. Clasificacion: A. REGLA OFICIAL.
- Esta fecha no corresponde a la fecha de ejecucion del hito, que fue `2026-07-09T14:57:24-0400`. Clasificacion: C. DATO OBSERVADO.

## 4. Plataforma y formato de carga

- Plataforma: Plataforma de Educacion Superior (PES), `http://pes.mineduc.cl`. Clasificacion: A. REGLA OFICIAL.
- Formato: `.CSV`, sin comprimir. Clasificacion: A. REGLA OFICIAL.
- Delimitador: el instructivo indica CSV delimitado por comas. Clasificacion: A. REGLA OFICIAL.
- Encabezado: el archivo de carga debe ir sin encabezados o nombres de columnas. Clasificacion: A. REGLA OFICIAL.
- Codificacion: no indicada por el instructivo. Clasificacion: F. HIPOTESIS O PENDIENTE.
- Restriccion de nombre: no hay restriccion de nombre de archivo. Clasificacion: A. REGLA OFICIAL.
- ID de carga: 16770. Clasificacion: A. REGLA OFICIAL.
- Antecedente tecnico: la estructura CSV observada en HITO 1B tiene 54 columnas, 1 fila de encabezados, 0 filas de datos y delimitador `;`. Clasificacion: B. ESTRUCTURA TECNICA / C. DATO OBSERVADO.

## 5. Universo a informar

### Incluidos

- Todos los inmuebles, locales y dependencias utilizados por la institucion para sus actividades.
- Predios y similares usados por la institucion.
- Recursos educacionales ligados a dichos inmuebles.
- Laboratorios, talleres y computadores disponibles para estudiantes.
- Bibliotecas, colecciones fisicas, libros digitales, suscripciones digitales y bases de datos.
- Plataformas virtuales institucionales para aprendizaje, videoconferencia y evaluacion online.

### Exclusiones explicitas

- Inmuebles que la institucion posee pero no utiliza para actividades propias.
- Sitios eriazos, terrenos para futuras construcciones, inmuebles arrendados a terceros o usados por terceros, cuando no se usan para actividades propias.
- Espacios de areas verdes excluyen casinos, cafeterias, patios de comida, predios, cultivos, canchas y campos deportivos.

### Casos especiales

- Predios agricolas o forestales, campos experimentales, parcelas, sitios, fundos o similares se informan con TIPO_INFRAESTRUCTURA = 5, no como inmueble permanente codigo 1.
- Plataformas virtuales se esperan como informacion institucional en una unica linea referida a sede central o administrativa principal.
- Libros y bases digitales se asignan a biblioteca digital; si no existe, usar datos de casa central.

### Pendientes

- No se identifica en este hito una lista institucional de sedes o registros a declarar; debe cruzarse en hitos posteriores con fuentes institucionales.

## 6. Definiciones oficiales

- **Inmuebles**: Bienes raices usados por la institucion para actividades propias: edificaciones, construcciones, terrenos, predios y similares. Inmuebles no usados para actividades propias no se informan. Fuente: Seccion 3.1.a, lineas 61-65. Clasificacion: A. REGLA OFICIAL
- **Inmuebles de Uso Permanente**: Inmuebles usados o disponibles permanentemente, todos los dias y horarios, sin necesidad de solicitar permiso a un tercero. Fuente: Seccion 3.1.b, lineas 66-70. Clasificacion: A. REGLA OFICIAL
- **Inmuebles de Uso Restringido**: Inmuebles no propios a los que se accede solo algunos dias u horarios para actividades especificas, servicios o actividades academicas puntuales. Fuente: Seccion 3.1.c, lineas 71-77. Clasificacion: A. REGLA OFICIAL
- **Nombre o identificacion**: Nombre con que la institucion identifica inmuebles, bibliotecas o predios; cada inmueble, biblioteca o predio informado debe contar con nombre de identificacion. Fuente: Seccion 3.1.d, lineas 78-84. Clasificacion: A. REGLA OFICIAL
- **Direccion**: Nombre de calle y numeracion de la ubicacion fisica; construcciones en una misma direccion y misma situacion de tenencia se informan en una sola fila. Fuente: Seccion 3.1.e, lineas 89-97. Clasificacion: A. REGLA OFICIAL
- **Situacion de tenencia**: Figura bajo la cual la institucion mantiene posesion o uso del inmueble: propietario, arrendatario, comodatario, usufructuario, leasing o leaseback u otro. Fuente: Seccion 3.1.f, lineas 98-101. Clasificacion: A. REGLA OFICIAL
- **Laboratorios**: Espacios equipados y destinados a experimentos, pruebas e investigacion por estudiantes y/o academicos. Fuente: Seccion 3.1.g, lineas 102-103. Clasificacion: A. REGLA OFICIAL
- **Talleres**: Espacios destinados principalmente a actividades practicas o desarrollo de habilidades, principalmente de estudiantes. Fuente: Seccion 3.1.h, lineas 104-105. Clasificacion: A. REGLA OFICIAL
- **Biblioteca**: Espacio fisico con coleccion de material de informacion, servicios, personal, equipos y programas para usuarios de la institucion; si hay mas de una biblioteca, cada una se informa en fila distinta. Fuente: Seccion 3.1.i, lineas 106-112. Clasificacion: A. REGLA OFICIAL
- **Metros cuadrados de terreno**: Total de metros cuadrados de terrenos donde se encuentran los inmuebles informados; en departamentos, oficinas o plantas dentro de un edificio no es necesario informar este dato. Fuente: Seccion 3.1.j, lineas 113-116. Clasificacion: A. REGLA OFICIAL
- **Metros cuadrados construidos**: Total de metros cuadrados edificados; en salas, bibliotecas, auditorios, talleres y laboratorios se informan metros cuadrados utiles. Fuente: Seccion 3.1.k, lineas 117-119. Clasificacion: A. REGLA OFICIAL
- **Uso exclusivo**: Indica si el inmueble es usado exclusivamente por la institucion o compartido con otra institucion u organizacion. Fuente: Seccion 3.1.n, lineas 133-137. Clasificacion: A. REGLA OFICIAL
- **Porcentaje de uso**: Aplica solo a inmuebles compartidos; estima el porcentaje de disponibilidad total usado por la institucion. Fuente: Seccion 3.1.o, lineas 138-140. Clasificacion: A. REGLA OFICIAL
- **Funciones de inmuebles**: Caracterizacion de actividades principales; puede informarse mas de una funcion: Docencia, Investigacion, Extension, Administracion y Otras. Fuente: Seccion 3.1.p, lineas 141-146. Clasificacion: A. REGLA OFICIAL
- **Sistemas virtuales**: Incluye sistema de gestion de aprendizajes, software de videoconferencia y sistemas de supervision de evaluaciones online. Fuente: Seccion 3.1.q-s, lineas 147-158. Clasificacion: A. REGLA OFICIAL

## 7. Campos, bloques y logica funcional

La estructura tecnica observada en HITO 1B contiene 54 encabezados. La siguiente organizacion por bloques es una propuesta tecnica de trabajo y no debe tratarse como regla oficial salvo donde el instructivo define expresamente campos o secciones. Clasificacion: E. DECISION INTERNA.

- **Identificacion de infraestructura**: `TIPO_INFRAESTRUCTURA`, `NOMBRE_IDENTIFICACION`
- **Ubicacion**: `COMUNA`, `DIRECCION_INMUEBLE`
- **Tenencia y uso**: `SITUACION_TENENCIA`, `ANIO_INICIO_USO_INMUEBLE`, `USO_EXCLUSIVO`, `PORCENTAJE_USO`, `NOMBRE_INSTITUCION_COMPARTE`, `FECHA_INICIO_TENENCIA`, `FECHA_TERMINO`, `DESCRIPCION_OTRA_TENENCIA`
- **Funciones**: `FUNCION_DOCENCIA`, `FUNCION_INVESTIGACION`, `FUNCION_EXTENSION`, `FUNCION_ADM_OFICINAS`, `FUNCION_OTRAS`, `DESC_OTRAS_FUNCIONES`
- **Superficie general**: `TOTAL_M2_TERRENO`, `TOTAL_M2_EDIFICADOS`
- **Salas, auditorios, laboratorios y talleres**: `TOTAL_SALAS_CLASES`, `CAPACIDAD_SALAS_CLASES`, `TOTAL_M2_SALAS_CLASES`, `TOTAL_AUDITORIOS`, `CAPACIDAD_AUDITORIOS`, `TOTAL_M2_AUDITORIOS`, `TOTAL_LABORATORIOS`, `TOTAL_M2_LABORATORIOS`, `TOTAL_TALLERES`, `TOTAL_M2_TALLERES`
- **Equipamiento computacional**: `TOTAL_PC_NB_DISPONIBLE`
- **Casinos, cafeterias y areas verdes**: `TOTAL_M2_CASINOS_CAFETERIAS`, `TOTAL_M2_AREAS_VERDES`
- **Unidad rural o predio, si corresponde**: `UR_DESC_ACTIVIDADES`, `UR_TOTAL_M2_TERRENO`, `UR_TOTAL_M2_CONSTRUIDOS`, `UR_SITUACION_TENENCIA`, `UR_DESC_TENENCIA_OTRA`, `TOTAL_HECTAREAS_PREDIO`
- **Biblioteca**: `TOTAL_M2_BIBLIOTECA`, `TOTAL_M2_SALAS_LECTURA`, `TOTAL_PROFESIONALES_BIBLIOTECA`, `HORAS_PERSONAL_BIBLIOTECA`
- **Recursos bibliograficos y digitales**: `TOTAL_TITULOS_DISPONIBLES`, `TOTAL_VOLUMENES_DISPONIBLES`, `TOTAL_SUSCRIPCIONES_REVISTAS`, `TOTAL_TITULOS_LIBROS_DIGITALES`, `TOTAL_SUSCRIPCIONES_DIGITALES`, `TOTAL_BASE_DATOS`
- **Plataformas virtuales**: `SISTEMA_GESTION_APRENDIZAJES`, `SISTEMA_VIDEO_CONFERENCIA`, `SISTEMA_APLICACION_EVALUACION`, `DESCRIPCION_PLATAFORMA_VIRTUAL`
- **Vigencia**: `VIGENCIA`

### Encabezados observados en estructura tecnica

| N | Campo |
| --- | --- |
| 1 | `TIPO_INFRAESTRUCTURA` |
| 2 | `NOMBRE_IDENTIFICACION` |
| 3 | `COMUNA` |
| 4 | `DIRECCION_INMUEBLE` |
| 5 | `SITUACION_TENENCIA` |
| 6 | `ANIO_INICIO_USO_INMUEBLE` |
| 7 | `USO_EXCLUSIVO` |
| 8 | `PORCENTAJE_USO` |
| 9 | `NOMBRE_INSTITUCION_COMPARTE` |
| 10 | `FECHA_INICIO_TENENCIA` |
| 11 | `FECHA_TERMINO` |
| 12 | `DESCRIPCION_OTRA_TENENCIA` |
| 13 | `FUNCION_DOCENCIA` |
| 14 | `FUNCION_INVESTIGACION` |
| 15 | `FUNCION_EXTENSION` |
| 16 | `FUNCION_ADM_OFICINAS` |
| 17 | `FUNCION_OTRAS` |
| 18 | `DESC_OTRAS_FUNCIONES` |
| 19 | `TOTAL_M2_TERRENO` |
| 20 | `TOTAL_M2_EDIFICADOS` |
| 21 | `TOTAL_SALAS_CLASES` |
| 22 | `CAPACIDAD_SALAS_CLASES` |
| 23 | `TOTAL_M2_SALAS_CLASES` |
| 24 | `TOTAL_AUDITORIOS` |
| 25 | `CAPACIDAD_AUDITORIOS` |
| 26 | `TOTAL_M2_AUDITORIOS` |
| 27 | `TOTAL_LABORATORIOS` |
| 28 | `TOTAL_M2_LABORATORIOS` |
| 29 | `TOTAL_TALLERES` |
| 30 | `TOTAL_M2_TALLERES` |
| 31 | `TOTAL_PC_NB_DISPONIBLE` |
| 32 | `TOTAL_M2_CASINOS_CAFETERIAS` |
| 33 | `TOTAL_M2_AREAS_VERDES` |
| 34 | `UR_DESC_ACTIVIDADES` |
| 35 | `UR_TOTAL_M2_TERRENO` |
| 36 | `UR_TOTAL_M2_CONSTRUIDOS` |
| 37 | `UR_SITUACION_TENENCIA` |
| 38 | `UR_DESC_TENENCIA_OTRA` |
| 39 | `TOTAL_M2_BIBLIOTECA` |
| 40 | `TOTAL_M2_SALAS_LECTURA` |
| 41 | `TOTAL_PROFESIONALES_BIBLIOTECA` |
| 42 | `HORAS_PERSONAL_BIBLIOTECA` |
| 43 | `TOTAL_TITULOS_DISPONIBLES` |
| 44 | `TOTAL_VOLUMENES_DISPONIBLES` |
| 45 | `TOTAL_SUSCRIPCIONES_REVISTAS` |
| 46 | `TOTAL_TITULOS_LIBROS_DIGITALES` |
| 47 | `TOTAL_SUSCRIPCIONES_DIGITALES` |
| 48 | `TOTAL_BASE_DATOS` |
| 49 | `TOTAL_HECTAREAS_PREDIO` |
| 50 | `SISTEMA_GESTION_APRENDIZAJES` |
| 51 | `SISTEMA_VIDEO_CONFERENCIA` |
| 52 | `SISTEMA_APLICACION_EVALUACION` |
| 53 | `DESCRIPCION_PLATAFORMA_VIRTUAL` |
| 54 | `VIGENCIA` |

## 8. Reglas oficiales por campo o grupo de campos

### TIPO_INFRAESTRUCTURA

- Clasificacion: A. REGLA OFICIAL
- Regla oficial: Usar numeros del 1 al 6. Es obligatorio.
- Fuente/seccion: Anexo I, lineas 252-263; Anexo III, lineas 740 y 815.
- Tipo de dato o formato: Numero entero
- Valores permitidos: {"1": "Inmuebles de Uso Permanente", "2": "Inmuebles de Uso Restringido", "3": "Caracteristicas de Biblioteca", "4": "Caracteristicas de Libros y Bases Digitales", "5": "Predios", "6": "Plataformas Virtuales"}
- Obligatoriedad: Obligatorio
- Condicion: Todos los registros
- Pendiente: Sin pendiente especifico en esta lectura.

### NOMBRE_IDENTIFICACION, COMUNA, DIRECCION_INMUEBLE

- Clasificacion: A. REGLA OFICIAL
- Regla oficial: Deben completarse para inmuebles, bibliotecas y predios; usar mayusculas sin acentos y sin abreviaciones, con numeros permitidos en nombre/direccion.
- Fuente/seccion: Seccion 3.1.d-e; Anexo I, lineas 264-280.
- Tipo de dato o formato: Texto en mayusculas; direccion y nombre admiten numeros
- Valores permitidos: Letras A-Z; numeros donde aplica
- Obligatoriedad: Obligatorio segun instructivo
- Condicion: Todos los registros informados requieren identificacion y ubicacion; plataformas virtuales refieren sede central o administrativa principal.
- Pendiente: Validar si PES exige comuna/direccion para todos los tipos con igual regla tecnica.

### SITUACION_TENENCIA

- Clasificacion: A. REGLA OFICIAL
- Regla oficial: Para inmuebles de uso permanente debe completarse; acepta 1 Propio, 2 Arrendado, 3 En Comodato, 4 En Usufructo, 5 Leasing o LeaseBack, 6 Otro.
- Fuente/seccion: Anexo I, lineas 288-295; Anexo III, lineas 756, 771, 772.
- Tipo de dato o formato: Numero entero
- Valores permitidos: [1, 2, 3, 4, 5, 6]
- Obligatoriedad: Condicional
- Condicion: Completar cuando TIPO_INFRAESTRUCTURA = 1; no completar para tipos 2, 3, 4 y 5 segun mensajes de error.
- Pendiente: Sin pendiente especifico en esta lectura.

### ANIO_INICIO_USO_INMUEBLE

- Clasificacion: A. REGLA OFICIAL
- Regla oficial: Año en que la institucion comenzo a usar el inmueble; formato AAAA; valores permitidos desde 1800 a 2026.
- Fuente/seccion: Anexo I, lineas 296-299; Anexo III, lineas 757, 774-781, 825.
- Tipo de dato o formato: Numero en formato AAAA
- Valores permitidos: 1800 a 2026
- Obligatoriedad: Condicional
- Condicion: Completar cuando TIPO_INFRAESTRUCTURA = 1; no completar para tipos 2, 3, 4 y 5.
- Pendiente: No se explicita regla para tipo 6 en mensajes revisados.

### USO_EXCLUSIVO, PORCENTAJE_USO, NOMBRE_INSTITUCION_COMPARTE

- Clasificacion: A. REGLA OFICIAL
- Regla oficial: USO_EXCLUSIVO acepta 1 uso exclusivo y 2 uso compartido. Si es compartido se completa PORCENTAJE_USO y NOMBRE_INSTITUCION_COMPARTE; si es exclusivo no se completan esos campos.
- Fuente/seccion: Seccion 3.1.n-o; Anexo I, lineas 300-313; Anexo III, lineas 750-753 y 758.
- Tipo de dato o formato: USO_EXCLUSIVO numero 1 o 2; PORCENTAJE_USO numero entero; nombre en mayusculas
- Valores permitidos: USO_EXCLUSIVO 1 o 2; PORCENTAJE_USO 1 a 99 segun mensaje de valores permitidos
- Obligatoriedad: Condicional
- Condicion: USO_EXCLUSIVO para tipo 1; porcentaje y nombre solo si USO_EXCLUSIVO = 2.
- Pendiente: Confirmar tratamiento de porcentaje 100 en PES, dado mensaje de valores 1 a 99.

### FECHA_INICIO_TENENCIA, FECHA_TERMINO, DESCRIPCION_OTRA_TENENCIA

- Clasificacion: A. REGLA OFICIAL
- Regla oficial: Fechas de tenencia usan formato AAAA-MM. FECHA_INICIO_TENENCIA es obligatoria para situacion 2, 3, 4, 5 o 6. FECHA_TERMINO se exige para arriendo, comodato, usufructo y leasing; no se completa para propio. DESCRIPCION_OTRA_TENENCIA se completa solo cuando situacion es Otro.
- Fuente/seccion: Anexo I, lineas 321-335; Anexo III, lineas 667-724, 783-789, 831-832.
- Tipo de dato o formato: Fecha AAAA-MM; texto mayusculas sin acentos para descripcion
- Valores permitidos: Fechas validas; inicio previa a julio 2026; termino posterior a mayo 2026
- Obligatoriedad: Condicional
- Condicion: Segun SITUACION_TENENCIA
- Pendiente: No se identifica regla explicita de FECHA_INICIO_TENENCIA para situacion 2 salvo mensaje general 2-6.

### FUNCION_* y DESC_OTRAS_FUNCIONES

- Clasificacion: A. REGLA OFICIAL
- Regla oficial: Para inmuebles tipo 1 debe completarse al menos una funcion principal. Cada funcion se marca con X si corresponde. DESC_OTRAS_FUNCIONES y FUNCION_OTRAS se requieren mutuamente cuando se usa la opcion Otras.
- Fuente/seccion: Seccion 3.1.p; Anexo I, lineas 336-365; Anexo III, lineas 679, 725-727, 754-755, 790-791.
- Tipo de dato o formato: Marca X; descripcion texto mayusculas sin acentos
- Valores permitidos: X cuando corresponde
- Obligatoriedad: Condicional
- Condicion: Aplica a inmuebles tipo 1; no completar para tipos 2, 3, 4, 5 segun mensajes.
- Pendiente: Sin pendiente especifico en esta lectura.

### Caracteristicas de inmueble tipo 1

- Clasificacion: A. REGLA OFICIAL
- Regla oficial: Para TIPO_INFRAESTRUCTURA = 1 se deben completar superficies, salas, capacidades, auditorios, laboratorios, talleres, computadores, casinos/cafeterias y areas verdes. Si no existen algunos recursos, completar con 0.
- Fuente/seccion: Seccion 4, lineas 183-190; Anexo I, lineas 366-421; Anexo III, lineas 642-655, 799, 829-830.
- Tipo de dato o formato: Numerico; maximo un decimal en varios campos
- Valores permitidos: Numeros; relaciones TOTAL_M2_SALAS_CLASES <= TOTAL_M2_EDIFICADOS
- Obligatoriedad: Condicional
- Condicion: Completar para tipo 1; no completar para otros tipos segun mensajes.
- Pendiente: Confirmar si todos los campos numericos aceptan decimal o algunos deben ser enteros en PES.

### Caracteristicas de inmueble de uso restringido tipo 2

- Clasificacion: A. REGLA OFICIAL
- Regla oficial: Para TIPO_INFRAESTRUCTURA = 2 se completan descripcion de actividades, metros de terreno, metros construidos y situacion de tenencia restringida; no se completan bloques de inmueble permanente, libros/bases digitales, predios, plataformas, biblioteca ni funciones principales.
- Fuente/seccion: Seccion 4, lineas 196-201; Anexo I, lineas 429-456; Anexo III, lineas 656-666, 728, 759-775, 809-817.
- Tipo de dato o formato: Texto mayusculas; numeros con maximo un decimal; UR_SITUACION_TENENCIA numero 1 o 2
- Valores permitidos: UR_SITUACION_TENENCIA: 1 Arrendado, 2 Otra
- Obligatoriedad: Condicional
- Condicion: Completar para tipo 2; UR_DESC_TENENCIA_OTRA si UR_SITUACION_TENENCIA = 2.
- Pendiente: El mensaje dice completar UR_DESC_TENENCIA_OTRA cuando UR_DESC_TENENCIA_OTRA es igual a 2; se interpreta como referencia probable a UR_SITUACION_TENENCIA, pero queda pendiente por redaccion.

### Bibliotecas tipo 3

- Clasificacion: A. REGLA OFICIAL
- Regla oficial: Cada biblioteca se informa en fila distinta con metros cuadrados, salas de lectura, profesionales, horas, titulos, volumenes y suscripciones a revistas fisicas.
- Fuente/seccion: Seccion 3.1.i; seccion 4, lineas 202-209; Anexo I, lineas 457-489; Anexo III, lineas 669-674, 702-712, 717, 729-730, 776-778, 808-821.
- Tipo de dato o formato: Numerico; algunos maximo un decimal; titulos/volumenes/suscripciones enteros
- Valores permitidos: TOTAL_M2_SALAS_LECTURA <= TOTAL_M2_BIBLIOTECA; TOTAL_TITULOS_DISPONIBLES <= TOTAL_VOLUMENES_DISPONIBLES
- Obligatoriedad: Condicional
- Condicion: Completar para tipo 3; no completar bloques incompatibles.
- Pendiente: Sin pendiente especifico en esta lectura.

### Libros y bases digitales tipo 4

- Clasificacion: A. REGLA OFICIAL
- Regla oficial: Informar libros digitales completos, suscripciones a revistas digitales y bases de datos especializadas; asignar a biblioteca digital o, si no existe, a casa central.
- Fuente/seccion: Seccion 4, lineas 214-223; Anexo I, lineas 490-502; Anexo III, lineas 663-678, 713-716, 731-736, 779-782, 822-823.
- Tipo de dato o formato: Numerico entero
- Valores permitidos: Numeros
- Obligatoriedad: Condicional
- Condicion: Completar para tipo 4; no completar bloques incompatibles.
- Pendiente: TOTAL_SUSCRIPCIONES_DIGITALES aparece como requerido en mensajes; confirmar si puede ser 0 cuando no exista.

### Predios tipo 5

- Clasificacion: A. REGLA OFICIAL
- Regla oficial: Predios agricolas, forestales, campos experimentales, parcelas, sitios, fundos o similares se informan con tipo 5, incluyendo hectareas.
- Fuente/seccion: Seccion 4, lineas 191-195 y 224-231; Anexo I, lineas 503-506; Anexo III, lineas 695-701, 718-719, 734, 738-739, 761-763, 772, 824.
- Tipo de dato o formato: Numerico; hectareas maximo un decimal
- Valores permitidos: Numeros
- Obligatoriedad: Condicional
- Condicion: Completar TOTAL_HECTAREAS_PREDIO para tipo 5; no completar bloques incompatibles.
- Pendiente: Sin pendiente especifico en esta lectura.

### Plataformas virtuales tipo 6

- Clasificacion: A. REGLA OFICIAL
- Regla oficial: Informar en una unica linea institucional los sistemas de gestion de aprendizajes, videoconferencia, aplicacion/evaluacion y descripcion de plataforma virtual.
- Fuente/seccion: Seccion 4, lineas 232-241; Anexo I, lineas 514-538; Anexo III, lineas 653, 686-688, 794-807.
- Tipo de dato o formato: Texto abierto; descripcion largo 1000
- Valores permitidos: Letras A-Z segun mensajes de error; texto abierto en Anexo I
- Obligatoriedad: Condicional
- Condicion: Completar para tipo 6; no completar bloques incompatibles.
- Pendiente: Hay tension entre texto abierto y mensajes de valores A-Z; validar caracteres permitidos antes de carga.

### VIGENCIA

- Clasificacion: A. REGLA OFICIAL
- Regla oficial: Variable para mantener o eliminar registros cargados. 0 elimina, 1 mantiene. No puede quedar vacio.
- Fuente/seccion: Anexo I, lineas 539-543; Anexo III, lineas 733 y 793.
- Tipo de dato o formato: Numero entero
- Valores permitidos: [0, 1]
- Obligatoriedad: Obligatorio
- Condicion: Todos los registros
- Pendiente: Debe confirmarse en hito posterior como se usa en una primera carga sin registros previos.


## 9. Reglas de vigencia

- Campo: `VIGENCIA`.
- Significado: Variable utilizada para mantener o eliminar un registro cargado.
- Valores permitidos: `0` = eliminar registro cargado; `1` = mantener registro cargado.
- Efecto funcional: controla eliminacion o mantencion de registros cargados.
- Obligatorio: si; no puede quedar vacio.
- Si mantiene, elimina, activa o desactiva registros: la fuente oficial indica mantener o eliminar registros cargados. No usa los terminos activar/desactivar.
- Si aplica solo a este proceso: el instructivo lo define para IRE 2026; no se debe asumir aplicacion a otros procesos. Clasificacion: F. HIPOTESIS O PENDIENTE.
- Pendiente: confirmar tratamiento operacional en primera carga y en cargas acumulativas posteriores.

## 10. Reglas de validacion inicial

### Validaciones oficiales

- Verificar TIPO_INFRAESTRUCTURA en valores 1,2,3,4,5,6.
- Verificar fecha de referencia de datos al 30 de junio de 2026 en fuentes institucionales posteriores.
- Cargar archivo CSV sin encabezados en PES.
- Validar VIGENCIA obligatorio con valores 0 o 1.
- Validar reglas condicionales por TIPO_INFRAESTRUCTURA segun Anexo III.
- Validar fechas de tenencia en formato AAAA-MM y contra referencia junio 2026.
- Validar que para uso compartido se completen porcentaje y nombre de institucion, y para uso exclusivo no se completen.
- Validar relaciones numericas: TOTAL_M2_SALAS_CLASES <= TOTAL_M2_EDIFICADOS, TOTAL_M2_SALAS_LECTURA <= TOTAL_M2_BIBLIOTECA, TOTAL_TITULOS_DISPONIBLES <= TOTAL_VOLUMENES_DISPONIBLES.

### Validaciones tecnicas sugeridas

- Construir diccionario estructurado desde Anexo I y compararlo contra los 54 encabezados del CSV. Clasificacion: D. IMPLEMENTACION TECNICA
- Crear validador de columnas obligatorias, condicionales y prohibidas por tipo antes de generar cualquier carga. Clasificacion: D. IMPLEMENTACION TECNICA
- Normalizar mayusculas, acentos y abreviaciones solo en derivados de trabajo, nunca en fuentes originales. Clasificacion: D. IMPLEMENTACION TECNICA
- Validar delimitador real de salida contra PES antes de carga por diferencia coma versus punto y coma. Clasificacion: D. IMPLEMENTACION TECNICA

### Validaciones pendientes

- Codificacion de archivo no indicada por instructivo.
- Confirmar delimitador efectivo aceptado por PES para la institucion.
- Confirmar tratamiento de campos que deben cargarse con 0 versus campos que no se deben completar.
- Confirmar si plataformas virtuales aceptan caracteres distintos de A-Z pese a estar definidas como texto abierto.

## 11. Contradicciones o vacios

- **Diferencia formato-delimitador**: El instructivo indica CSV delimitado por comas, mientras la estructura tecnica observada en HITO 1B trae encabezados separados por punto y coma (;). Impacto: Debe resolverse antes de generar archivo candidato de carga. Fuente: Instructivo lineas 37-39 y 557-561; CSV estructura HITO 1B. Clasificacion: B. ESTRUCTURA TECNICA / F. HIPOTESIS O PENDIENTE
- **Tension todos los campos versus no completar**: El instructivo indica que todos los campos deben ser cargados, pero Anexo III contiene multiples reglas donde ciertos bloques no deben completarse para determinados tipos. Impacto: Se debe traducir en regla tecnica: columnas presentes siempre, valores 0/blanco segun tipo y campo, pendiente de formalizacion. Fuente: Anexo I lineas 246-248; Anexo III lineas 656-688 y otras. Clasificacion: A. REGLA OFICIAL / F. HIPOTESIS O PENDIENTE
- **Redaccion posiblemente erronea**: El mensaje indica completar UR_DESC_TENENCIA_OTRA cuando UR_DESC_TENENCIA_OTRA es igual a 2; parece referirse a UR_SITUACION_TENENCIA = 2, pero no se corrige por supuesto. Impacto: Pendiente de validacion o prueba contra PES. Fuente: Anexo III, linea 769. Clasificacion: A. REGLA OFICIAL / F. HIPOTESIS O PENDIENTE
- **Texto abierto versus valores A-Z**: Anexo I define campos de plataformas virtuales como texto abierto, pero mensajes de error mencionan que algunos campos pueden contener letras A-Z. Impacto: No asumir caracteres permitidos hasta validar contra estructura PES o prueba de carga. Fuente: Anexo I lineas 514-538; Anexo III lineas 796-807. Clasificacion: A. REGLA OFICIAL / F. HIPOTESIS O PENDIENTE

## 12. Dictamen del hito

- Estado HITO 2A: COMPLETADO_CON_OBSERVACIONES.
- Quedo respaldado oficialmente: proceso, fecha de referencia, plazo, medio oficial PES, formato CSV, carga sin encabezados, tipos de infraestructura, definiciones principales, reglas por grupos de campos y reglas de vigencia.
- Queda pendiente: delimitador efectivo, codificacion, matriz detallada por campo y tipo, comparacion formal con los 54 encabezados, y resolucion de vacios/contradicciones antes de generar archivo de carga.
- No debe asumirse: que reglas de otros procesos aplican a IRE, que el CSV final debe usar `;` solo por la estructura tecnica, que la codificacion sea una especifica, ni que los vacios puedan completarse sin fuente o decision posterior documentada.

## 13. Proximo hito sugerido

HITO 2B - COMANDO - Extraccion estructurada del diccionario oficial y comparacion preliminar contra los 54 encabezados del CSV de estructura IRE 2026.
