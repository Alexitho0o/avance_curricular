# HITO 1B - Inventario tecnico inicial de fuentes IRE 2026

- Fecha y hora de ejecucion: `2026-07-09T14:49:58-0400`
- Proceso: Infraestructura y Recursos Educacionales
- Subproyecto: IRE 2026
- Estado: **COMPLETADO**

## Objetivo

Inventariar tecnicamente las fuentes originales IRE 2026, identificando existencia, tamano, hash, codificacion probable, delimitador, cantidad de filas, cantidad de columnas, encabezados, muestra inicial controlada y estructura basica, sin modificar fuentes, sin interpretar reglas funcionales y sin generar archivos de carga.

## Entradas

| Fuente | Ruta relativa | Existe | Hash SHA-256 |
| --- | --- | --- | --- |
| Instructivo TXT | `01_fuentes_oficiales/instructivos/20260707_87395_Infraestructura_y_Recursos_Educacionales_2026_SIES_-_Instructivo_2026.txt` | True | `2fa7f09fcdc23b706765e81333ed91e800dcc3423defc34503cb4e7ccb583637` |
| Estructura CSV | `01_fuentes_oficiales/estructuras_tecnicas/20260706_89535_Estructura_IRE_ID_16770.csv` | True | `117babcfd945589969f6d508ff9e173214854ac4355df526a61b09de1061deae` |

## Resultado tecnico - Instructivo TXT

- Tamano bytes: 58603
- Fecha modificacion: `2026-07-09T14:33:06-0400`
- Codificacion usada para lectura: `utf-8`
- Lectura exitosa: True
- Cantidad de lineas: 841
- Cantidad de caracteres: 57624
- Presencia de texto legible: True
- Posible titulo detectado: `--- Página 1 ---`
- BOM UTF-8: False
- Nota: No se interpretan reglas funcionales en este hito.

### Muestra controlada - Primeras 30 lineas

```text

--- Página 1 ---
Subsecretaría de Educación Superior 1
Instructivo Proceso Año 2026 – Infraestructura y Recursos Educacionales
INSTRUCTIVO PARA EL PROCESO 2026
DE RECOLECCIÓN DE DATOS SOBRE
INFRAESTRUCTURA Y RECURSOS
EDUCACIONALES
1
--- Página 2 ---
Subsecretaría de Educación Superior 2
Instructivo Proceso Año 2026 – Infraestructura y Recursos Educacionales
1. Sobre el alcance de la solicitud de información.
La Subsecretaría de Educación Superior recaba información sobre infraestructura y recursos
educacionales de las instituciones de educación superior, donde el principal objetivo del proceso de
recolección de datos es la generación de información estadística e indicadores de interés para el sistema
de educación superior.
Las instituciones de educación superior deberán informar sobre 2 aspectos principales:
• La Infraestructura de la institución: que considera la individualización de todos los inmuebles,
locales y dependencias, así como de los predios y similares, que utiliza y donde desarrolla sus
actividades la institución, con detalle de su ubicación, situación de tenencia y características de
estos.
• Los Recursos Educacionales con que cuenta la institución. Se deberá informar el número de
laboratorios, talleres y computadores que posee la institución para sus estudiantes, así como la
dotación y características de las bibliotecas y colecciones que tiene disponible.
Es fundamental que la institución informe todos los inmuebles, locales y recintos donde desarrollaba sus
actividades, así como los recursos educacionales ligados a dichos inmuebles.
IMPORTANTE
La información que debe informarse en este proceso corresponde a la infraestructura que se encontraba
utilizando la institución al 30 de junio de 2026, y los recursos educacionales que poseía la institución a esa
```

## Resultado tecnico - Estructura CSV

- Tamano bytes: 1169
- Fecha modificacion: `2026-07-09T11:27:46-0400`
- Codificacion usada para lectura: `utf-8`
- Lectura exitosa: True
- Delimitador detectado: `;`
- Filas totales: 1
- Filas de datos: 0
- Columnas: 54
- Encabezados detectados: True
- Nombres de columnas: `TIPO_INFRAESTRUCTURA`, `NOMBRE_IDENTIFICACION`, `COMUNA`, `DIRECCION_INMUEBLE`, `SITUACION_TENENCIA`, `ANIO_INICIO_USO_INMUEBLE`, `USO_EXCLUSIVO`, `PORCENTAJE_USO`, `NOMBRE_INSTITUCION_COMPARTE`, `FECHA_INICIO_TENENCIA`, `FECHA_TERMINO`, `DESCRIPCION_OTRA_TENENCIA`, `FUNCION_DOCENCIA`, `FUNCION_INVESTIGACION`, `FUNCION_EXTENSION`, `FUNCION_ADM_OFICINAS`, `FUNCION_OTRAS`, `DESC_OTRAS_FUNCIONES`, `TOTAL_M2_TERRENO`, `TOTAL_M2_EDIFICADOS`, `TOTAL_SALAS_CLASES`, `CAPACIDAD_SALAS_CLASES`, `TOTAL_M2_SALAS_CLASES`, `TOTAL_AUDITORIOS`, `CAPACIDAD_AUDITORIOS`, `TOTAL_M2_AUDITORIOS`, `TOTAL_LABORATORIOS`, `TOTAL_M2_LABORATORIOS`, `TOTAL_TALLERES`, `TOTAL_M2_TALLERES`, `TOTAL_PC_NB_DISPONIBLE`, `TOTAL_M2_CASINOS_CAFETERIAS`, `TOTAL_M2_AREAS_VERDES`, `UR_DESC_ACTIVIDADES`, `UR_TOTAL_M2_TERRENO`, `UR_TOTAL_M2_CONSTRUIDOS`, `UR_SITUACION_TENENCIA`, `UR_DESC_TENENCIA_OTRA`, `TOTAL_M2_BIBLIOTECA`, `TOTAL_M2_SALAS_LECTURA`, `TOTAL_PROFESIONALES_BIBLIOTECA`, `HORAS_PERSONAL_BIBLIOTECA`, `TOTAL_TITULOS_DISPONIBLES`, `TOTAL_VOLUMENES_DISPONIBLES`, `TOTAL_SUSCRIPCIONES_REVISTAS`, `TOTAL_TITULOS_LIBROS_DIGITALES`, `TOTAL_SUSCRIPCIONES_DIGITALES`, `TOTAL_BASE_DATOS`, `TOTAL_HECTAREAS_PREDIO`, `SISTEMA_GESTION_APRENDIZAJES`, `SISTEMA_VIDEO_CONFERENCIA`, `SISTEMA_APLICACION_EVALUACION`, `DESCRIPCION_PLATAFORMA_VIRTUAL`, `VIGENCIA`
- Columnas con encabezado vacio: []
- Columnas sin valores en datos: []
- Filas completamente vacias: []
- Duplicados de encabezado: []
- Consistencia de cantidad de columnas por fila: True
- BOM UTF-8: False
- Caracter de reemplazo presente: False
- NUL presente: False

### Muestra controlada - Primeras 5 filas

```text
['TIPO_INFRAESTRUCTURA', 'NOMBRE_IDENTIFICACION', 'COMUNA', 'DIRECCION_INMUEBLE', 'SITUACION_TENENCIA', 'ANIO_INICIO_USO_INMUEBLE', 'USO_EXCLUSIVO', 'PORCENTAJE_USO', 'NOMBRE_INSTITUCION_COMPARTE', 'FECHA_INICIO_TENENCIA', 'FECHA_TERMINO', 'DESCRIPCION_OTRA_TENENCIA', 'FUNCION_DOCENCIA', 'FUNCION_INVESTIGACION', 'FUNCION_EXTENSION', 'FUNCION_ADM_OFICINAS', 'FUNCION_OTRAS', 'DESC_OTRAS_FUNCIONES', 'TOTAL_M2_TERRENO', 'TOTAL_M2_EDIFICADOS', 'TOTAL_SALAS_CLASES', 'CAPACIDAD_SALAS_CLASES', 'TOTAL_M2_SALAS_CLASES', 'TOTAL_AUDITORIOS', 'CAPACIDAD_AUDITORIOS', 'TOTAL_M2_AUDITORIOS', 'TOTAL_LABORATORIOS', 'TOTAL_M2_LABORATORIOS', 'TOTAL_TALLERES', 'TOTAL_M2_TALLERES', 'TOTAL_PC_NB_DISPONIBLE', 'TOTAL_M2_CASINOS_CAFETERIAS', 'TOTAL_M2_AREAS_VERDES', 'UR_DESC_ACTIVIDADES', 'UR_TOTAL_M2_TERRENO', 'UR_TOTAL_M2_CONSTRUIDOS', 'UR_SITUACION_TENENCIA', 'UR_DESC_TENENCIA_OTRA', 'TOTAL_M2_BIBLIOTECA', 'TOTAL_M2_SALAS_LECTURA', 'TOTAL_PROFESIONALES_BIBLIOTECA', 'HORAS_PERSONAL_BIBLIOTECA', 'TOTAL_TITULOS_DISPONIBLES', 'TOTAL_VOLUMENES_DISPONIBLES', 'TOTAL_SUSCRIPCIONES_REVISTAS', 'TOTAL_TITULOS_LIBROS_DIGITALES', 'TOTAL_SUSCRIPCIONES_DIGITALES', 'TOTAL_BASE_DATOS', 'TOTAL_HECTAREAS_PREDIO', 'SISTEMA_GESTION_APRENDIZAJES', 'SISTEMA_VIDEO_CONFERENCIA', 'SISTEMA_APLICACION_EVALUACION', 'DESCRIPCION_PLATAFORMA_VIRTUAL', 'VIGENCIA']
```

## Salidas generadas

- `06_validaciones/estructura/HITO_1B_INVENTARIO_TECNICO_FUENTES_IRE_2026_20260709_144958.json`
- `07_resultados/reportes_auditoria/HITO_1B_INVENTARIO_TECNICO_FUENTES_IRE_2026_20260709_144958.md`
- `08_logs/ejecuciones/HITO_1B_LOG_EJECUCION_20260709_144958.txt`

## Validaciones

- Verificacion de existencia de ambas fuentes originales esperadas.
- Calculo de tamano, fecha de modificacion y hash SHA-256.
- Lectura en modo solo lectura para deteccion de codificacion probable.
- Conteo tecnico de lineas y caracteres del instructivo TXT.
- Extraccion de muestra controlada de primeras 30 lineas del instructivo TXT.
- Deteccion de delimitador del CSV.
- Conteo de filas y columnas del CSV.
- Lectura de encabezados del CSV.
- Extraccion de muestra controlada de primeras 5 filas del CSV.
- Revision tecnica de columnas vacias, filas vacias, duplicados de encabezado, BOM y caracteres problematicos.
- Revision de consistencia de cantidad de columnas por fila.

## Pendientes

- Ejecutar HITO 2A para lectura funcional controlada del instructivo oficial IRE 2026.

## Proximo hito sugerido

HITO 2A - PROMPT - Lectura funcional controlada del instructivo oficial IRE 2026: alcance, fecha de referencia, plazo, formato de carga, secciones y reglas oficiales iniciales.
