# Diagnóstico Bloque 16-19 — Fuente académica

## Contexto

Proceso: Avance Curricular SIES 2026  
Subproyecto: Matrícula 5809  
Año de referencia: 2025  

Columnas revisadas:

16. CURSO_1ER_SEM  
17. CURSO_2DO_SEM  
18. UNIDADES_CURSADAS  
19. UNIDADES_APROBADAS  

## Resultado

Estado del bloque: **BLOQUEADO_FUENTE_INSUFICIENTE**

La precarga 5809 trae estas columnas vacías, por lo que no se conservan como dato completo.  
A diferencia de las columnas 1-15, estas columnas requieren construcción desde fuente académica, trayectoria, período 2025 y validación funcional.

## Fuente académica candidata

Fuente: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/PROMEDIOSDEALUMNOS_7804.xlsx`  
Hoja candidata: `DatosAlumnos`

Columnas detectadas:

- CODCLI: `CODCLI`
- Documento/RUT: `RUT`
- Código único: `NO_DETECTADO`
- Carrera/plan: `CODCARPR`
- Año: `NO_DETECTADO`
- Semestre: `NO_DETECTADO`
- Nivel/curso: `NIVEL`
- Unidades/créditos: `NO_DETECTADO`
- Estado/aprobación: `SITUACION`
- Convalidación: `NO_DETECTADO`

## Diagnóstico por columna

|   ORDEN_COLUMNA | CAMPO_5809         | ESTADO_GOBERNANZA    | TIPO_CAMPO                      | BLOQUEO_GOBERNANZA    |   REGISTROS_TOTAL |   NO_VACIOS_PRECARGA |   VACIOS_PRECARGA | FUENTE_CANDIDATA                                                                                                                                                     | HOJA_CANDIDATA   | FUENTE_MINIMA_REQUERIDA                                        | COLUMNAS_DETECTADAS                                                                                 | COLUMNAS_MINIMAS_DETECTADAS   | ESTADO_FACTIBILIDAD           | ACCION_SIGUIENTE                      | BLOQUEA_ARCHIVO_FINAL   |
|----------------:|:-------------------|:---------------------|:--------------------------------|:----------------------|------------------:|---------------------:|------------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|:---------------------------------------------------------------|:----------------------------------------------------------------------------------------------------|:------------------------------|:------------------------------|:--------------------------------------|:------------------------|
|              16 | CURSO_1ER_SEM      | BLOQUEADO_POR_FUENTE | ACADEMICO_SEMESTRAL_OBLIGATORIO | BLOQUEO_FUENTE_AVANCE |              2371 |                    0 |              2371 | /Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/PROMEDIOSDEALUMNOS_7804.xlsx | DatosAlumnos     | nivel/curso + año/semestre + trayectoria                       | {"CURSO_NIVEL": "NIVEL", "ANIO": "", "SEMESTRE": ""}                                                | NO                            | BLOQUEADO_FUENTE_INSUFICIENTE | NO_COMPLETAR_SOLICITAR_FUENTE_O_REGLA | SI                      |
|              17 | CURSO_2DO_SEM      | BLOQUEADO_POR_FUENTE | ACADEMICO_SEMESTRAL_OBLIGATORIO | BLOQUEO_FUENTE_AVANCE |              2371 |                    0 |              2371 | /Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/PROMEDIOSDEALUMNOS_7804.xlsx | DatosAlumnos     | nivel/curso + año/semestre + trayectoria                       | {"CURSO_NIVEL": "NIVEL", "ANIO": "", "SEMESTRE": ""}                                                | NO                            | BLOQUEADO_FUENTE_INSUFICIENTE | NO_COMPLETAR_SOLICITAR_FUENTE_O_REGLA | SI                      |
|              18 | UNIDADES_CURSADAS  | BLOQUEADO_POR_FUENTE | ACADEMICO_ANUAL_OBLIGATORIO     | BLOQUEO_FUENTE_AVANCE |              2371 |                    0 |              2371 | /Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/PROMEDIOSDEALUMNOS_7804.xlsx | DatosAlumnos     | unidades/créditos + estado aprobación + año 2025 + trayectoria | {"UNIDADES": "", "ESTADO_APROBACION": "SITUACION", "ANIO": "", "SEMESTRE": "", "CONVALIDACION": ""} | NO                            | BLOQUEADO_FUENTE_INSUFICIENTE | NO_COMPLETAR_SOLICITAR_FUENTE_O_REGLA | SI                      |
|              19 | UNIDADES_APROBADAS | BLOQUEADO_POR_FUENTE | ACADEMICO_ANUAL_OBLIGATORIO     | BLOQUEO_FUENTE_AVANCE |              2371 |                    0 |              2371 | /Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/PROMEDIOSDEALUMNOS_7804.xlsx | DatosAlumnos     | unidades/créditos + estado aprobación + año 2025 + trayectoria | {"UNIDADES": "", "ESTADO_APROBACION": "SITUACION", "ANIO": "", "SEMESTRE": "", "CONVALIDACION": ""} | NO                            | BLOQUEADO_FUENTE_INSUFICIENTE | NO_COMPLETAR_SOLICITAR_FUENTE_O_REGLA | SI                      |

## Validaciones

| VALIDACION                                    | RESULTADO    | DETALLE                                                                |
|:----------------------------------------------|:-------------|:-----------------------------------------------------------------------|
| REGISTROS_5809                                | OK           | 2371                                                                   |
| COLUMNAS_16_19_EXISTEN                        | OK           | CURSO_1ER_SEM | CURSO_2DO_SEM | UNIDADES_CURSADAS | UNIDADES_APROBADAS |
| COLUMNAS_16_19_VACIAS_EN_PRECARGA             | OK           | La precarga no alimenta estos campos; requieren fuente académica.      |
| FUENTE_ACADEMICA_LEIDA                        | OK           | PROMEDIOSDEALUMNOS_7804.xlsx / hoja candidata: DatosAlumnos            |
| LLAVE_DOCUMENTO_DETECTADA_EN_FUENTE_ACADEMICA | OK           | RUT                                                                    |
| CODCLI_DETECTADO_EN_FUENTE_ACADEMICA          | OK           | CODCLI                                                                 |
| CURSO_NIVEL_DETECTADO                         | OK           | NIVEL                                                                  |
| UNIDADES_DETECTADAS                           | REVISAR      | NO_DETECTADO                                                           |
| ESTADO_APROBACION_DETECTADO                   | OK           | SITUACION                                                              |
| PERIODO_DETECTADO                             | REVISAR      | ANIO=; SEM=                                                            |
| CONVALIDACION_DETECTADA                       | NO_DETECTADO |                                                                        |
| CSV_CARGA_GENERADO                            | OK           | NO                                                                     |
| SIES_READY_GENERADO                           | OK           | NO                                                                     |
| FUENTES_ORIGINALES_MODIFICADAS                | OK           | NO                                                                     |

## Conclusión

Esta fase no completa valores.  
Solo confirma si existe fuente candidata para probar la construcción de las columnas 16-19.  
Si el estado queda como `FUENTE_CANDIDATA_DETECTADA_REQUIERE_PRUEBA`, la siguiente fase debe ejecutar una prueba controlada de cálculo sobre una muestra, sin generar archivo de carga.

## Archivos

- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/06_gobernanza_columnas_5809/DIAGNOSTICO_BLOQUE_16_19_FUENTE_ACADEMICA_20260703_233723/02_RESULTADOS/DIAGNOSTICO_BLOQUE_16_19_FUENTE_ACADEMICA.xlsx`
- Carpeta: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/06_gobernanza_columnas_5809/DIAGNOSTICO_BLOQUE_16_19_FUENTE_ACADEMICA_20260703_233723`
