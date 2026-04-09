# Diagnóstico estructura 9 — 5810 / matriz / Hoja1 — corregido

Proceso: Avance Curricular SIES 2026  
Subproyecto: Matrícula 5809 / columnas 16-21  
Año de referencia: 2025  

Este diagnóstico identifica la evidencia disponible para conectar CODIGO_UNICO SIES con carrera institucional. No genera carga ni modifica fuentes originales.

## Resumen

| METRICA                        | VALOR   |
|:-------------------------------|:--------|
| CASOS_9                        | 9       |
| SIES_CARRERAS_DISTINTAS_9      | 5       |
| MATCH_5810_CODIGO_UNICO        | 5       |
| MATCH_5810_SIES_CARRERA        | 19      |
| MATCH_MATRIZ_CODIGO_UNICO      | 5       |
| MATCH_MATRIZ_SIES_CARRERA      | 31      |
| FILAS_HOJA1_9_HASTA_2025       | 161     |
| CSV_CARGA_GENERADO             | NO      |
| SIES_READY_GENERADO            | NO      |
| FUENTES_ORIGINALES_MODIFICADAS | NO      |

## Diagnóstico de columnas

| FUENTE           |   FILAS |   COLUMNAS | COLUMNAS_RELEVANTES                                                                                                                                                                                                                                                                                     | TIENE_CODIGO_UNICO   |
|:-----------------|--------:|-----------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------|
| 5810             |      43 |         22 | CODIGO_IES_NUM | CODIGO_UNICO | PLAN_ESTUDIOS | NOMBRE_SEDE | NOMBRE_CARRERA | JORNADA | VERSION | DURACION_ESTUDIOS | DURACION_TITULACION | DURACION_TOTAL | NIVEL_CARRERA | TIPO_UNIDAD_MEDIDA | VIGENCIA                                                                                             | SI                   |
| PROMEDIOS_matriz |     139 |         19 | CODIGO_IES_NUM | CODIGO_UNICO | NOMBRE_IES | COD_SEDE | NOMBRE_SEDE | NOMBRE_CARRERA | MODALIDAD | JORNADA | TIPO_PLAN_CARRERA | CARACT_PLAN_ESPECIAL | DURACION_ESTUDIOS | DURACION_TITULACION | DURACION_TOTAL | COMUNA_SEDE | PROVINCIA_SEDE | REGION_SEDE | NIVEL_GLOBAL | NIVEL_CARRERA | VIGENCIA | SI                   |
| Hoja1_9          |     161 |         28 | CODCLI | RUT | DIG | CODCARR | CODRAMO | ASIGNATURA | ANO | PERIODO | ESTADO | DESCRIPCION_ESTADO | CONVALIDADO | NIVEL | ESTADO_ACADEMICO                                                                                                                                                              | NO                   |

## Archivo

- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/06_gobernanza_columnas_5809/DIAGNOSTICO_ESTRUCTURA_9_5810_MATRIZ_HOJA1_CORREGIDO_20260704_010252/02_RESULTADOS/DIAGNOSTICO_ESTRUCTURA_9_5810_MATRIZ_HOJA1_CORREGIDO.xlsx`
- Carpeta: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/06_gobernanza_columnas_5809/DIAGNOSTICO_ESTRUCTURA_9_5810_MATRIZ_HOJA1_CORREGIDO_20260704_010252`
