# Auditoría metodológica columnas 16–21 — 2.320 calculados / 51 pendientes — Planes RE+CO — NO CARGA

Proceso: Avance Curricular SIES 2026  
Subproyecto: Matrícula 5809 / columnas 16–21  
Año referencia: 2025  

Esta auditoría confirma si la metodología aplicada a columnas 16–21 respeta el flujo: 5809 → 5810/planes RE+CO → Hoja1 → cálculo → Matricula_2025 como evidencia auxiliar. No genera CSV de carga ni SIES_READY.

## Resumen general

| METRICA                                           | VALOR   |
|:--------------------------------------------------|:--------|
| TOTAL_5809                                        | 2371    |
| CALCULADOS_NO_CARGA                               | 2320    |
| PENDIENTES_NO_CARGA                               | 51      |
| ERRORES_VALIDACION_16_21                          | 0       |
| ERRORES_TRAZABILIDAD                              | 2224    |
| CALCULADOS_CON_CODCARR_USADO                      | 2320    |
| ERRORES_PLANES_RECO_EN_CODCARR_USADO              | 0       |
| CONFIRMACION_22_MULTICARRERA                      | 22      |
| CONFIRMACION_22_MATCH_RUT_Y_CODCLI_MATRICULA_2025 | 22      |
| PENDIENTES_51                                     | 51      |
| CSV_CARGA_GENERADO                                | NO      |
| SIES_READY_GENERADO                               | NO      |
| FUENTES_ORIGINALES_MODIFICADAS                    | NO      |

## Validaciones

| VALIDACION                     | RESULTADO   | DETALLE   |
|:-------------------------------|:------------|:----------|
| TOTAL_5809                     | OK          | 2371      |
| CALCULADOS_NO_CARGA            | OK          | 2320      |
| PENDIENTES_NO_CARGA            | OK          | 51        |
| VALORES_16_21                  | OK          | 0         |
| TRAZABILIDAD_CALCULADOS        | REVISAR     | 2224      |
| PLANES_RECO_CARGADO            | OK          | 22876     |
| PLANES_RECO_CODCARR_USADO      | OK          | 0         |
| CONFIRMACION_22_MATRICULA_2025 | OK          | 22        |
| CSV_CARGA_GENERADO             | OK          | NO        |
| SIES_READY_GENERADO            | OK          | NO        |
| FUENTES_ORIGINALES_MODIFICADAS | OK          | NO        |

## Resumen Planes RE+CO con CODCARR usado

| PLANES_RESULTADO                   |    N |
|:-----------------------------------|-----:|
| MATCH_CODCARR_Y_NOMBRE_PLANES_RECO | 2320 |

## Resumen 51 pendientes

| ESTADO_CALCULO                          | DICTAMEN_FINAL_PENDIENTE                                            | REQUERIMIENTO_PARA_RESOLVER                                                                                                         |   N |
|:----------------------------------------|:--------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------|----:|
| BLOQUEADO_SIN_MATCH_HOJA1               | PENDIENTE_CONFIRMADO_SIN_HISTORIAL_HOJA1_Y_SIN_MATCH_MATRICULA_2025 | Requiere fuente académica alternativa o nueva extracción con historial por ramo. Matricula_2025 no entrega match por RUT ni CODCLI. |  49 |
| BLOQUEADO_MULTICARRERA_SIN_TRAZABILIDAD | PENDIENTE_CONFIRMADO_MULTICARRERA_SIN_EQUIVALENCIA_DOCUMENTADA      | Requiere equivalencia documentada para seleccionar CODCARR válido. No corresponde decidir por supuesto.                             |   1 |
| BLOQUEADO_SIN_REGISTROS_HASTA_2025      | PENDIENTE_CONFIRMADO_SIN_REGISTROS_HASTA_2025                       | Requiere evidencia académica con ANO <= 2025. No corresponde usar registros posteriores.                                            |   1 |

## Archivo

- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/06_gobernanza_columnas_5809/AUDITORIA_METODOLOGICA_COLUMNAS_16_21_2320_51_PLANES_RECO_20260704_130432/02_RESULTADOS/AUDITORIA_METODOLOGICA_COLUMNAS_16_21_2320_51_PLANES_RECO_NO_CARGA.xlsx`
- Carpeta: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/06_gobernanza_columnas_5809/AUDITORIA_METODOLOGICA_COLUMNAS_16_21_2320_51_PLANES_RECO_20260704_130432`
