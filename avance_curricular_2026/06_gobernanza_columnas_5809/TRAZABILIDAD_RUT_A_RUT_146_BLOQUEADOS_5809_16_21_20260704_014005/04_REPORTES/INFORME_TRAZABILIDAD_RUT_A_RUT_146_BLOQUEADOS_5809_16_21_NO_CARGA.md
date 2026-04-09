# Trazabilidad rut a rut — 146 bloqueados 5809 columnas 16–21 — NO CARGA

Proceso: Avance Curricular SIES 2026  
Subproyecto: Matrícula 5809 / columnas 16–21  
Año de referencia: 2025  

Este expediente confirma los RUT, CODIGO_UNICO, carrera SIES, cruces 5810/matriz, Hoja1 y DatosAlumnos para cada uno de los 146 pendientes vigentes. No genera CSV de carga ni SIES_READY.

## Resumen general

| METRICA                                 | VALOR   |
|:----------------------------------------|:--------|
| TOTAL_5809                              | 2371    |
| CALCULADOS_NO_CARGA                     | 2225    |
| BLOQUEADOS_TRAZADOS                     | 146     |
| BLOQUEADO_SIN_MATCH_HOJA1               | 140     |
| BLOQUEADO_SIN_REGISTROS_HASTA_2025      | 5       |
| BLOQUEADO_MULTICARRERA_SIN_TRAZABILIDAD | 1       |
| CON_MATCH_5810_EXACTO                   | 146     |
| CON_MATCH_MATRIZ_EXACTO                 | 146     |
| CON_MATCH_HOJA1_TOTAL                   | 6       |
| CON_MATCH_HOJA1_HASTA_2025              | 1       |
| CON_MATCH_DATOSALUMNOS                  | 121     |
| CSV_CARGA_GENERADO                      | NO      |
| SIES_READY_GENERADO                     | NO      |
| FUENTES_ORIGINALES_MODIFICADAS          | NO      |

## Resumen rechazo

| ESTADO_CALCULO                          | PUNTO_RECHAZO                                                                     | ACCION_SIGUIENTE                                                               |   N |
|:----------------------------------------|:----------------------------------------------------------------------------------|:-------------------------------------------------------------------------------|----:|
| BLOQUEADO_MULTICARRERA_SIN_TRAZABILIDAD | RECHAZA_EN_DECISION_CARRERA: múltiples CODCARR y no hay equivalencia documentada. | Documentar equivalencia de carrera para ID 70 antes de calcular.               |   1 |
| BLOQUEADO_SIN_MATCH_HOJA1               | RECHAZA_EN_HOJA1: RUT no aparece en Hoja1.                                        | Buscar fuente académica por ramo equivalente a Hoja1 para este RUT.            | 140 |
| BLOQUEADO_SIN_REGISTROS_HASTA_2025      | RECHAZA_EN_ANIO_REFERENCIA: existe historial, pero no hay registros hasta 2025.   | Confirmar si existe historial académico 2025 o anterior en fuente alternativa. |   5 |

## Archivo

- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/06_gobernanza_columnas_5809/TRAZABILIDAD_RUT_A_RUT_146_BLOQUEADOS_5809_16_21_20260704_014005/02_RESULTADOS/TRAZABILIDAD_RUT_A_RUT_146_BLOQUEADOS_5809_16_21_NO_CARGA.xlsx`
- Carpeta: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/06_gobernanza_columnas_5809/TRAZABILIDAD_RUT_A_RUT_146_BLOQUEADOS_5809_16_21_20260704_014005`
