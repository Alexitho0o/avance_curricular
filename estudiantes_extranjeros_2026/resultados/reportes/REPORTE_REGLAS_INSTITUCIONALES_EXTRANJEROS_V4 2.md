# Reporte reglas institucionales Extranjeros V4

Fecha: 2026-06-25T11:51:42

## Decisiones aplicadas
- TIPO_RESIDENCIA_ESTUDIANTE = 0 para los 62 registros.
- PAIS_ORIGEN permanece vacio para los 62 registros.
- ANIO/SEM ingreso carrera origen provienen de ANOINGRESO/PERIODOINGRESO.
- PAIS_ESTUDIOS_SECUNDARIOS se completo solo con catalogo territorial y catalogo SIES.

## Comparacion V3/V4
| COLUMNA                     | VALIDADOS_V3 | VALIDADOS_V4 | PENDIENTES_V3 | PENDIENTES_V4 | CONFLICTOS_V3 | CONFLICTOS_V4 | REGISTROS_MODIFICADOS | REGLA_APLICADA                             | MEJORA_NETA |
| --------------------------- | ------------ | ------------ | ------------- | ------------- | ------------- | ------------- | --------------------- | ------------------------------------------ | ----------- |
| TIPO_RESIDENCIA_ESTUDIANTE  | 0            | 62           | 62            | 0             | 0             | 0             | 62                    | SIN_INFORMACION_DE_RESIDENCIA_ASIGNAR_0    | 62          |
| PAIS_ORIGEN                 | 62           | 62           | 0             | 0             | 0             | 0             | 62                    | RESIDENCIA_0_NO_COMPLETAR_PAIS_ORIGEN      | 0           |
| PAIS_ESTUDIOS_SECUNDARIOS   | 50           | 62           | 12            | 0             | 0             | 0             | 12                    | VALIDACION_GEOGRAFICA_CONTROLADA           | 12          |
| ANIO_INGRESO_CARRERA_ORIGEN | 50           | 61           | 12            | 1             | 0             | 0             | 62                    | INGRESO_ORIGEN_IGUAL_INGRESO_INSTITUCIONAL | 11          |
| SEM_INGRESO_CARRERA_ORIGEN  | 50           | 61           | 12            | 1             | 0             | 0             | 62                    | INGRESO_ORIGEN_IGUAL_INGRESO_INSTITUCIONAL | 11          |

## Pais estudios secundarios
| CLASIFICACION             | REGISTROS |
| ------------------------- | --------- |
| MANTENIDO_DESDE_V3        | 50        |
| VALIDADO_CHILE_POR_COMUNA | 12        |

## Pendientes restantes
| VARIABLE                    | PENDIENTES |
| --------------------------- | ---------- |
| CODIGO_UNICO                | 11         |
| NACIONALIDAD                | 1          |
| ANIO_INGRESO_CARRERA_ORIGEN | 1          |
| SEM_INGRESO_CARRERA_ORIGEN  | 1          |

## Validacion
| CONTROL                                                       | RESULTADO               | DETALLE                                                                                       |
| ------------------------------------------------------------- | ----------------------- | --------------------------------------------------------------------------------------------- |
| Base congelada intacta                                        | OK                      | da85dd0c453a942a4490f469b75d0418e9054e458a46028f44271ac704518081                              |
| Hash correcto                                                 | OK                      | da85dd0c453a942a4490f469b75d0418e9054e458a46028f44271ac704518081                              |
| V3 intacta                                                    | OK                      | 54876c75ae412e372657726c64c520d7c50c18d742f3c36827c222c5ce45d70c                              |
| V4 contiene 62 filas                                          | OK                      | 62                                                                                            |
| Existen 20 TSV V4                                             | OK                      | 20                                                                                            |
| Cada TSV contiene 62 filas                                    | OK                      |                                                                                               |
| Residencia es 0 en las 62 filas                               | OK                      |                                                                                               |
| Pais origen esta vacio en las 62 filas                        | OK                      |                                                                                               |
| Anio origen proviene de ANOINGRESO                            | OK                      | Aplica a registros validados; pendientes quedan vacios.                                       |
| Semestre origen proviene de PERIODOINGRESO                    | OK                      | Aplica a registros validados; pendientes quedan vacios.                                       |
| Anio origen cumple rango                                      | OK                      | Registros pendientes no cargan valor invalido.                                                |
| COHERENCIA_ANIO_INGRESO_ORIGEN                                | PENDIENTE_INSTITUCIONAL | 1 registro presenta año base de origen mayor que año actual y fue dejado vacío para revisión. |
| Semestre origen es 1 o 2                                      | OK                      | Registros pendientes no cargan valor invalido.                                                |
| No existe semestre 0 con anio distinto de 1900                | OK                      |                                                                                               |
| No existe valor invalido marcado como validado                | OK                      |                                                                                               |
| Pais estudios secundarios con evidencia geografica controlada | OK                      |                                                                                               |
| No se infiere pais desde nacionalidad                         | OK                      | Regla usa catalogo territorial o valores V3.                                                  |
| No se modifica campo validado sin justificacion               | OK                      | Cambios V4 limitados a reglas institucionales autorizadas.                                    |
| No se multiplican filas                                       | OK                      |                                                                                               |
| No existen errores de Excel                                   | OK                      | Archivos xlsx creados con openpyxl.                                                           |
| No se genera archivo final PES                                | OK                      | No se escriben archivos PES_READY/carga final.                                                |

## Copias Escritorio
| ARCHIVO                                             | EXISTE | HASH_COINCIDE |
| --------------------------------------------------- | ------ | ------------- |
| MATRIZ_GOBERNANZA_EXTRANJEROS_2025_V4.csv           | SI     | SI            |
| REVISION_REGLAS_INSTITUCIONALES_EXTRANJEROS_V4.xlsx | SI     | SI            |
| NOMINA_PENDIENTES_EXTRANJEROS_2025_V4.xlsx          | SI     | SI            |
| COMPARACION_GOBERNANZA_V3_VS_V4.csv                 | SI     | SI            |
| VALIDACION_REGLAS_INSTITUCIONALES_V4.csv            | SI     | SI            |
| REPORTE_REGLAS_INSTITUCIONALES_EXTRANJEROS_V4.md    | SI     | SI            |
| RESOLUCION_CASO_18_INGRESO_ORIGEN_V4.csv            | SI     | SI            |

## Hashes
```json
{
  "BASE_CONGELADA": "da85dd0c453a942a4490f469b75d0418e9054e458a46028f44271ac704518081",
  "MATRIZ_V3": "54876c75ae412e372657726c64c520d7c50c18d742f3c36827c222c5ce45d70c",
  "MATRIZ_V4": "b961f40f073e740cd507fe3f2ddc92b8258a5a264acc16e6daa6ee5a9eae1b00",
  "CATALOGO_PAISES": "179386695cb2144b9ab3c0b675fc79f26259dfeb6c5fea13681b033e5611007a",
  "CATALOGO_TERRITORIAL": "10c1c05146c99fa6358c4cebd68f231be3e93770b1ef787f1db7320f562028d9",
  "SCRIPT": "d5a6d2fcc87e3d46e779ecfe23f06a3ad05c1edaec90776720d5d2afd24059fb",
  "RESOLUCION_CASO_18": "9ce7cee18a53ee77b0ee1cb851bb052409f8de45b0d15468e49ff4cd20ddc1f4",
  "REPORTE": "8ee89f5cd3e90c08da73b357de7ea55e58b52ed60bc49ab13111adb71402d254",
  "VALIDACION": "04d61e14f17b6dd7fa907840aa9fa7c2106ffb0b54bcebb9093c867a2fb19122"
}
```

Respaldo: /Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/backups/pre_aplicacion_reglas_institucionales_v4_20260625_115140

## Estado git
```
M estudiantes_extranjeros_2026/resultados/reportes/REPORTE_REGLAS_INSTITUCIONALES_EXTRANJEROS_V4.md
 M estudiantes_extranjeros_2026/scripts/aplicar_reglas_institucionales_extranjeros_v4.py
?? estudiantes_extranjeros_2026/backups/pre_aplicacion_reglas_institucionales_v4_20260625_115018/
?? estudiantes_extranjeros_2026/backups/pre_aplicacion_reglas_institucionales_v4_20260625_115140/
```
