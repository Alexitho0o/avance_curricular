# MANIFEST_SUBPROYECTO - IRE 2026

## HITO 1A - Inicializacion del subproyecto

- Proceso: Infraestructura y Recursos Educacionales.
- Subproyecto: IRE 2026.
- Anio proceso: 2026.
- Repositorio base: `/Users/alexi/Documents/GitHub/avance_curricular`.
- Carpeta del subproyecto: `/Users/alexi/Documents/GitHub/avance_curricular/infraestructura_recursos_educacionales_2026`.
- Fecha y hora de ejecucion: `2026-07-09T14:42:29-0400`.

## Objetivo

Crear la estructura base del subproyecto IRE 2026, copiar las fuentes originales desde Descargas hacia la carpeta correcta del repositorio, calcular hash SHA-256, clasificar los archivos, crear manifiesto inicial y dejar registrado el HITO 1A como punto de partida formal.

## Archivos originales incorporados

| Archivo | Origen | Destino |
| --- | --- | --- |
| `20260707_87395_Infraestructura_y_Recursos_Educacionales_2026_SIES_-_Instructivo_2026.txt` | `/Users/alexi/Downloads/20260707_87395_Infraestructura_y_Recursos_Educacionales_2026_SIES_-_Instructivo_2026.txt` | `01_fuentes_oficiales/instructivos/20260707_87395_Infraestructura_y_Recursos_Educacionales_2026_SIES_-_Instructivo_2026.txt` |
| `20260706_89535_Estructura_IRE_ID_16770.csv` | `/Users/alexi/Downloads/20260706_89535_Estructura_IRE_ID_16770.csv` | `01_fuentes_oficiales/estructuras_tecnicas/20260706_89535_Estructura_IRE_ID_16770.csv` |

## Clasificacion de archivos

| Archivo | Clasificacion |
| --- | --- |
| `20260707_87395_Infraestructura_y_Recursos_Educacionales_2026_SIES_-_Instructivo_2026.txt` | instructivo oficial / fuente original / no modificable |
| `20260706_89535_Estructura_IRE_ID_16770.csv` | estructura tecnica oficial / fuente original / no modificable |

## Hash SHA-256

| Archivo | Hash origen | Hash destino | Resultado |
| --- | --- | --- | --- |
| `20260707_87395_Infraestructura_y_Recursos_Educacionales_2026_SIES_-_Instructivo_2026.txt` | `2fa7f09fcdc23b706765e81333ed91e800dcc3423defc34503cb4e7ccb583637` | `2fa7f09fcdc23b706765e81333ed91e800dcc3423defc34503cb4e7ccb583637` | OK |
| `20260706_89535_Estructura_IRE_ID_16770.csv` | `117babcfd945589969f6d508ff9e173214854ac4355df526a61b09de1061deae` | `117babcfd945589969f6d508ff9e173214854ac4355df526a61b09de1061deae` | OK |

## Validaciones realizadas

1. Existe la carpeta del subproyecto.
2. Existen todas las subcarpetas base solicitadas.
3. El instructivo fue copiado a `01_fuentes_oficiales/instructivos/`.
4. La estructura tecnica fue copiada a `01_fuentes_oficiales/estructuras_tecnicas/`.
5. Los nombres destino son identicos a los nombres origen.
6. El hash SHA-256 del origen y destino coincide para cada archivo.
7. El manifiesto JSON existe.
8. El manifiesto MD existe.
9. La bitacora existe.
10. Los criterios de versionado existen.

## Estado final

COMPLETADO.

## Pendientes

- Ejecutar el HITO 1B para inventario tecnico inicial de las fuentes sin interpretar reglas funcionales.

## Proximo hito sugerido

HITO 1B - COMANDO - Inventario tecnico inicial de las fuentes IRE 2026: conteo de filas, columnas, delimitador, codificacion, encabezados y lectura preliminar sin interpretar reglas funcionales.

## HITO 1B - Inventario tecnico inicial de fuentes IRE 2026

### Objetivo

Inventariar tecnicamente las fuentes originales IRE 2026, identificando existencia, tamano, hash, codificacion probable, delimitador, cantidad de filas, cantidad de columnas, encabezados, muestra inicial controlada y estructura basica, sin modificar fuentes, sin interpretar reglas funcionales y sin generar archivos de carga.

### Entradas

- `01_fuentes_oficiales/instructivos/20260707_87395_Infraestructura_y_Recursos_Educacionales_2026_SIES_-_Instructivo_2026.txt`
- `01_fuentes_oficiales/estructuras_tecnicas/20260706_89535_Estructura_IRE_ID_16770.csv`

### Salidas generadas

- `06_validaciones/estructura/HITO_1B_INVENTARIO_TECNICO_FUENTES_IRE_2026_20260709_144958.json`
- `07_resultados/reportes_auditoria/HITO_1B_INVENTARIO_TECNICO_FUENTES_IRE_2026_20260709_144958.md`
- `08_logs/ejecuciones/HITO_1B_LOG_EJECUCION_20260709_144958.txt`

### Resultado tecnico

- Instructivo TXT: 841 lineas, 57624 caracteres, codificacion `utf-8`, hash `2fa7f09fcdc23b706765e81333ed91e800dcc3423defc34503cb4e7ccb583637`.
- Estructura CSV: 1 filas totales, 0 filas de datos, 54 columnas, delimitador `;`, codificacion `utf-8`, hash `117babcfd945589969f6d508ff9e173214854ac4355df526a61b09de1061deae`.
- Encabezados CSV detectados: `TIPO_INFRAESTRUCTURA`, `NOMBRE_IDENTIFICACION`, `COMUNA`, `DIRECCION_INMUEBLE`, `SITUACION_TENENCIA`, `ANIO_INICIO_USO_INMUEBLE`, `USO_EXCLUSIVO`, `PORCENTAJE_USO`, `NOMBRE_INSTITUCION_COMPARTE`, `FECHA_INICIO_TENENCIA`, `FECHA_TERMINO`, `DESCRIPCION_OTRA_TENENCIA`, `FUNCION_DOCENCIA`, `FUNCION_INVESTIGACION`, `FUNCION_EXTENSION`, `FUNCION_ADM_OFICINAS`, `FUNCION_OTRAS`, `DESC_OTRAS_FUNCIONES`, `TOTAL_M2_TERRENO`, `TOTAL_M2_EDIFICADOS`, `TOTAL_SALAS_CLASES`, `CAPACIDAD_SALAS_CLASES`, `TOTAL_M2_SALAS_CLASES`, `TOTAL_AUDITORIOS`, `CAPACIDAD_AUDITORIOS`, `TOTAL_M2_AUDITORIOS`, `TOTAL_LABORATORIOS`, `TOTAL_M2_LABORATORIOS`, `TOTAL_TALLERES`, `TOTAL_M2_TALLERES`, `TOTAL_PC_NB_DISPONIBLE`, `TOTAL_M2_CASINOS_CAFETERIAS`, `TOTAL_M2_AREAS_VERDES`, `UR_DESC_ACTIVIDADES`, `UR_TOTAL_M2_TERRENO`, `UR_TOTAL_M2_CONSTRUIDOS`, `UR_SITUACION_TENENCIA`, `UR_DESC_TENENCIA_OTRA`, `TOTAL_M2_BIBLIOTECA`, `TOTAL_M2_SALAS_LECTURA`, `TOTAL_PROFESIONALES_BIBLIOTECA`, `HORAS_PERSONAL_BIBLIOTECA`, `TOTAL_TITULOS_DISPONIBLES`, `TOTAL_VOLUMENES_DISPONIBLES`, `TOTAL_SUSCRIPCIONES_REVISTAS`, `TOTAL_TITULOS_LIBROS_DIGITALES`, `TOTAL_SUSCRIPCIONES_DIGITALES`, `TOTAL_BASE_DATOS`, `TOTAL_HECTAREAS_PREDIO`, `SISTEMA_GESTION_APRENDIZAJES`, `SISTEMA_VIDEO_CONFERENCIA`, `SISTEMA_APLICACION_EVALUACION`, `DESCRIPCION_PLATAFORMA_VIRTUAL`, `VIGENCIA`.

### Validaciones

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

### Estado

COMPLETADO.

### Pendientes

- Ejecutar HITO 2A para lectura funcional controlada del instructivo oficial IRE 2026.

### Proximo hito sugerido

HITO 2A - PROMPT - Lectura funcional controlada del instructivo oficial IRE 2026: alcance, fecha de referencia, plazo, formato de carga, secciones y reglas oficiales iniciales.

## HITO 2A - Lectura funcional controlada del instructivo oficial IRE 2026

### Objetivo

Leer funcionalmente el instructivo oficial IRE 2026 para extraer, ordenar y documentar reglas oficiales iniciales del proceso, sin transformar datos y sin generar archivo de carga.

### Fuente usada

- `01_fuentes_oficiales/instructivos/20260707_87395_Infraestructura_y_Recursos_Educacionales_2026_SIES_-_Instructivo_2026.txt`
- Hash SHA-256: `2fa7f09fcdc23b706765e81333ed91e800dcc3423defc34503cb4e7ccb583637`

### Salidas generadas

- `07_resultados/reportes_auditoria/HITO_2A_LECTURA_FUNCIONAL_INSTRUCTIVO_IRE_2026_20260709_145724.md`
- `06_validaciones/reglas_funcionales/HITO_2A_REGLAS_FUNCIONALES_INICIALES_IRE_2026_20260709_145724.json`

### Reglas extraidas

- Fecha de referencia de datos: 30 de junio de 2026.
- Plazo de carga: 24 de julio de 2026.
- Plataforma oficial: PES.
- Formato oficial: `.CSV`, sin comprimir, sin restriccion de nombre y sin encabezados para carga.
- Tipos de infraestructura: 1 a 6.
- VIGENCIA: `0` elimina registro cargado; `1` mantiene registro cargado.

### Validaciones derivadas

- Reglas condicionales por `TIPO_INFRAESTRUCTURA`.
- Reglas de fechas de tenencia en formato `AAAA-MM`.
- Reglas de uso exclusivo, uso compartido y porcentaje de uso.
- Reglas numericas y relaciones de consistencia indicadas en Anexo III.

### Contradicciones / observaciones

- Delimitador oficial indicado como coma versus estructura tecnica observada con `;`.
- Tension entre todos los campos deben cargarse y multiples reglas de no completar campos segun tipo.
- Redaccion ambigua de `UR_DESC_TENENCIA_OTRA` en mensaje de error.
- Texto abierto en plataformas versus mensajes de valores A-Z.

### Estado

COMPLETADO_CON_OBSERVACIONES.

### Pendientes

- Extraer diccionario oficial campo a campo desde Anexo I en formato estructurado.
- Comparar el diccionario oficial contra los 54 encabezados del CSV de estructura.
- Resolver delimitador efectivo para archivo candidato de carga: coma indicada oficialmente versus punto y coma observado tecnicamente.
- Definir matriz campo x TIPO_INFRAESTRUCTURA con obligatorio, permitido, prohibido, cero o blanco.
- Confirmar codificacion esperada de PES, porque el instructivo no la indica.
- Confirmar tratamiento operativo de VIGENCIA en primera carga y en cargas acumulativas.
- No generar archivo de carga hasta completar hitos de diccionario, comparacion y validacion.

### Proximo hito sugerido

HITO 2B - COMANDO - Extraccion estructurada del diccionario oficial y comparacion preliminar contra los 54 encabezados del CSV de estructura IRE 2026.

## HITO 2B - Diccionario oficial y comparacion contra estructura CSV IRE 2026

### Objetivo

Construir un diccionario estructurado y auditable de los 54 campos IRE 2026 desde el instructivo oficial y compararlo contra la estructura tecnica CSV, sin modificar fuentes ni generar archivo de carga.

### Fuentes usadas

- `01_fuentes_oficiales/instructivos/20260707_87395_Infraestructura_y_Recursos_Educacionales_2026_SIES_-_Instructivo_2026.txt` (`2fa7f09fcdc23b706765e81333ed91e800dcc3423defc34503cb4e7ccb583637`)
- `01_fuentes_oficiales/estructuras_tecnicas/20260706_89535_Estructura_IRE_ID_16770.csv` (`117babcfd945589969f6d508ff9e173214854ac4355df526a61b09de1061deae`)
- `07_resultados/reportes_auditoria/HITO_2A_LECTURA_FUNCIONAL_INSTRUCTIVO_IRE_2026_20260709_145724.md`
- `06_validaciones/reglas_funcionales/HITO_2A_REGLAS_FUNCIONALES_INICIALES_IRE_2026_20260709_145724.json`

### Salidas generadas

- `03_diccionarios/HITO_2B_DICCIONARIO_OFICIAL_CAMPOS_IRE_2026_20260709_233948.csv`
- `03_diccionarios/HITO_2B_DICCIONARIO_OFICIAL_CAMPOS_IRE_2026_20260709_233948.json`
- `07_resultados/reportes_auditoria/HITO_2B_COMPARACION_DICCIONARIO_VS_ESTRUCTURA_IRE_2026_20260709_233948.md`
- `06_validaciones/estructura/HITO_2B_COMPARACION_CAMPOS_INSTRUCTIVO_VS_CSV_IRE_2026_20260709_233948.csv`
- `08_logs/ejecuciones/HITO_2B_LOG_EJECUCION_20260709_233948.txt`

### Resultado

- Campos CSV y diccionario: 54.
- Coincidencias nominales exactas: 54.
- Campos con respaldo oficial claro y sin contradiccion de campo: 48.
- Campos con observaciones de contradiccion: 6.
- Campos solo CSV: 0.
- Campos solo instructivo: 1 (`CODIGO_INSTITUCION`, mencionado como parte de la clave acumulativa de PES).
- Estado: COMPLETADO_CON_OBSERVACIONES.

### Contradicciones y observaciones

- Coma indicada por el instructivo versus punto y coma observado en la estructura tecnica.
- Todos los campos deben cargarse versus reglas de no completar por tipo.
- Excepcion de `TOTAL_M2_TERRENO` versus exigencia general para tipo 1.
- Condicion ambigua de `UR_DESC_TENENCIA_OTRA`.
- Texto abierto versus letras A-Z en cuatro campos de plataformas virtuales.
- Codificacion de carga no indicada oficialmente.

### Pendientes

- Resolver delimitador y codificacion efectivos mediante respaldo oficial o prueba controlada posterior.
- Confirmar el rol de `CODIGO_INSTITUCION` sin agregarlo por supuesto a la estructura.
- Resolver las contradicciones de terreno, UR y plataformas.
- Construir la matriz exhaustiva campo por tipo en HITO 2C.

### Proximo hito sugerido

HITO 2C - PROMPT - Construccion de matriz funcional campo por tipo de infraestructura y reglas completar / no completar para IRE 2026.

## HITO 2C - Matriz funcional campo por tipo de infraestructura IRE 2026

### Objetivo

Construir una matriz funcional oficial/tecnica para gobernar los 324 cruces entre los 54 campos y los 6 tipos de infraestructura, sin modificar fuentes ni generar archivo de carga.

### Entradas

- `01_fuentes_oficiales/instructivos/20260707_87395_Infraestructura_y_Recursos_Educacionales_2026_SIES_-_Instructivo_2026.txt` (`2fa7f09fcdc23b706765e81333ed91e800dcc3423defc34503cb4e7ccb583637`)
- `01_fuentes_oficiales/estructuras_tecnicas/20260706_89535_Estructura_IRE_ID_16770.csv` (`117babcfd945589969f6d508ff9e173214854ac4355df526a61b09de1061deae`)
- `03_diccionarios/HITO_2B_DICCIONARIO_OFICIAL_CAMPOS_IRE_2026_20260709_233948.csv`
- `03_diccionarios/HITO_2B_DICCIONARIO_OFICIAL_CAMPOS_IRE_2026_20260709_233948.json`
- `07_resultados/reportes_auditoria/HITO_2B_COMPARACION_DICCIONARIO_VS_ESTRUCTURA_IRE_2026_20260709_233948.md`

### Salidas generadas

- `06_validaciones/reglas_funcionales/HITO_2C_MATRIZ_LARGA_CAMPO_TIPO_INFRAESTRUCTURA_IRE_2026_20260709_235255.csv`
- `06_validaciones/reglas_funcionales/HITO_2C_MATRIZ_ANCHA_CAMPO_TIPO_INFRAESTRUCTURA_IRE_2026_20260709_235255.csv`
- `06_validaciones/reglas_funcionales/HITO_2C_PENDIENTES_CONTRADICCIONES_CAMPO_TIPO_IRE_2026_20260709_235255.csv`
- `06_validaciones/reglas_funcionales/HITO_2C_MATRIZ_FUNCIONAL_CAMPO_TIPO_IRE_2026_20260709_235255.json`
- `07_resultados/reportes_auditoria/HITO_2C_REPORTE_MATRIZ_FUNCIONAL_CAMPO_TIPO_IRE_2026_20260709_235255.md`
- `08_logs/ejecuciones/HITO_2C_LOG_EJECUCION_20260709_235255.txt`

### Resultado

- Tipos de infraestructura: 6.
- Campos oficiales: 54.
- Cruces campo/tipo: 324.
- Conteo de estados: `{"COMPLETAR_OBLIGATORIO": 32, "COMPLETAR_CONDICIONAL": 6, "NO_COMPLETAR": 245, "COMPLETAR_SI_APLICA": 5, "SIEMPRE_COMPLETAR": 30, "PENDIENTE_REVISION": 0, "CONTRADICCION": 6, "NO_APLICA": 0}`.
- Pendientes y contradicciones documentados: 11.
- Estado: COMPLETADO_CON_OBSERVACIONES.

### Criterios

- Los cinco campos transversales se clasificaron como `SIEMPRE_COMPLETAR`.
- Los bloques exigidos por tipo se clasificaron como obligatorios, condicionales o si aplica segun respaldo oficial.
- Los bloques excluidos expresamente por Anexo III se clasificaron como `NO_COMPLETAR`.
- Los seis cruces incompatibles heredados de HITO 2B conservaron estado `CONTRADICCION`.
- No se resolvieron por supuesto delimitador, codificacion, blanco versus cero, regla UR, plataformas ni CODIGO_INSTITUCION.

### Proximo hito sugerido

HITO 3A - PROMPT - Diseno de reglas de validacion tecnica y funcional para archivo candidato IRE 2026.

## HITO 3A - Diseno de reglas de validacion tecnica y funcional IRE 2026

### Objetivo

Disenar reglas gobernadas para futuros archivos candidatos IRE 2026, sin validar datos institucionales ni generar archivo de carga.

### Salidas generadas

- `06_validaciones/reglas_funcionales/HITO_3A_REGLAS_VALIDACION_IRE_2026_20260710_000222.csv`
- `06_validaciones/reglas_funcionales/HITO_3A_REGLAS_VALIDACION_IRE_2026_20260710_000222.json`
- `07_resultados/reportes_auditoria/HITO_3A_DISENO_VALIDACIONES_IRE_2026_20260710_000222.md`
- `08_logs/ejecuciones/HITO_3A_LOG_EJECUCION_20260710_000222.txt`

### Resultado

- Total de reglas: 131.
- Reglas por severidad: `{"ADVERTENCIA": 25, "BLOQUEANTE": 87, "INFORMATIVA": 8, "PENDIENTE_CONFIRMACION": 11}`.
- Reglas por estado de implementacion: `{"IMPLEMENTABLE_CON_DECISION_INTERNA": 10, "IMPLEMENTABLE_DIRECTO": 106, "NO_IMPLEMENTAR_AUN": 2, "REQUIERE_CONFIRMACION_OFICIAL": 9, "SOLO_DOCUMENTAR": 4}`.
- Implementables directamente: 106.
- Implementables con decision interna: 10.
- Requieren confirmacion oficial: 9.
- No implementar aun: 2.
- Estado: COMPLETADO_CON_OBSERVACIONES.

### Decisiones

- La matriz HITO 2C gobierna obligatoriedad, condicionalidad y no completitud.
- Los bloqueantes tecnicos no corrigen ni modifican datos.
- Las contradicciones no se activan como bloqueo automatico.
- La llave propuesta es de auditoria y no se declara oficial.
- Delimitador, codificacion, blanco versus cero, UR, plataformas y CODIGO_INSTITUCION siguen pendientes.

### Proximo hito sugerido

HITO 3B - COMANDO - Implementacion del validador tecnico-funcional IRE 2026 basado en matriz HITO 2C y reglas HITO 3A.

## HITO 3B-Z - Cierre documental post-verificacion del validador IRE 2026

### Hito asociado

HITO 3B - Implementacion del validador tecnico-funcional IRE 2026.

### Objetivo

Cerrar documentalmente HITO 3B despues de la interrupcion y dejar trazado que el check inicial fallo por un `--run-id` invalido, no por una falla del validador.

### Evidencia consolidada

- Script, configuracion, README, muestra, resultado CSV, resumen JSON y log: verificados.
- Hash script: `9cdf6b22bbc112f2bbf55f8cbfbf568e9dce42ce79e010c6b441021e18d50ecf`.
- Hash config: `e5cc3bb2bf4729ba026b3a397c2fc3639e7877e131182c24ac8157cf25e0840a`.
- Hash muestra: `f4f21b690b8fa841a1059000f58a9c60f7595ea393983ddfca93f004d94c3f4d`.
- Muestra: 9 filas totales, 8 filas de datos y 54 columnas.
- Prueba principal: 19 hallazgos; 6 bloqueantes, 7 advertencias y 6 pendientes.
- Dictamen de prueba: `NO_APTO_BLOQUEANTES`.

### Incidente y recheck

- El check inicial uso `--run-id DEBUG_NORMAL` y retorno `NO_EVALUABLE` porque el formato exigido es `YYYYMMDD_HHMMSS`.
- Ejecucion normal corregida `20260710_084604`: retorno 0.
- Ejecucion con `--fail-on-blocking` `20260710_084659`: retorno 2.
- Ambas reprodujeron 19 hallazgos y dictamen `NO_APTO_BLOQUEANTES`.
- Dictamen final del recheck: OK.

### Estado final

HITO 3B: COMPLETADO_CON_OBSERVACIONES.

La observacion corresponde a la interrupcion del cierre, el check inicial con parametro invalido y los pendientes funcionales heredados. No se validaron datos institucionales reales ni se genero archivo de carga.

### Archivos de cierre

- `07_resultados/reportes_auditoria/HITO_3B_Z_CIERRE_DOCUMENTAL_VALIDADOR_IRE_2026_20260710_085242.md`
- `08_logs/ejecuciones/HITO_3B_Z_CIERRE_VERIFICACION_VALIDADOR_IRE_2026_20260710_085242.json`

### Proximo hito sugerido

HITO 3C - COMANDO - Prueba del validador contra una fuente institucional o archivo candidato IRE 2026 cuando el usuario incorpore el archivo de datos.
