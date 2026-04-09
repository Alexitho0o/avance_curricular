# Reporte reglas institucionales Extranjeros V4

Fecha: 2026-06-24T23:16:36

## Estado
Ejecucion detenida. No se genera V4 final ni copias al Escritorio.

## Motivo
La regla institucional de ingreso de origen produce un valor que incumple la restriccion del instructivo: el anio de origen no puede superar el anio de ingreso de carrera actual.

## Filas bloqueantes
| FILA_BASE_CONGELADA | CODCLI       | DOCUMENTO | ANOINGRESO_BASE | ANIO_INGRESO_ACTUAL | ANIO_ORIGEN_V3 | ANIO_ORIGEN_V4 | PERIODOINGRESO_BASE | SEM_INGRESO_ACTUAL | SEM_ORIGEN_V3 | SEM_ORIGEN_V4 | VALIDACION_ANIO                 | VALIDACION_SEMESTRE | REGLA                                      | ESTADO         | ES_BLOQUEANTE |
| ------------------- | ------------ | --------- | --------------- | ------------------- | -------------- | -------------- | ------------------- | ------------------ | ------------- | ------------- | ------------------------------- | ------------------- | ------------------------------------------ | -------------- | ------------- |
| 18                  | 20251ICDA037 | 26089199  | 2025            | 2024                | 2024           | 2025           | 1                   | 1                  | 1             | 1             | ERROR_ANIO_ORIGEN_SUPERA_ACTUAL | OK                  | INGRESO_ORIGEN_IGUAL_INGRESO_INSTITUCIONAL | VALOR_INVALIDO | SI            |

## Validacion
| CONTROL                             | RESULTADO | DETALLE                                                                                                                      |
| ----------------------------------- | --------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Base congelada intacta              | OK        | da85dd0c453a942a4490f469b75d0418e9054e458a46028f44271ac704518081                                                             |
| V3 intacta                          | OK        | 54876c75ae412e372657726c64c520d7c50c18d742f3c36827c222c5ce45d70c                                                             |
| Ingreso origen cumple restricciones | ERROR     | fila 18 CODCLI 20251ICDA037: ANOINGRESO_BASE=2025, ANIO_INGRESO_ACTUAL=2024, VALIDACION_ANIO=ERROR_ANIO_ORIGEN_SUPERA_ACTUAL |
| V4 final generada                   | ERROR     | Detenida por VALOR_INVALIDO en ingreso de carrera de origen.                                                                 |
| No se genera archivo final PES      | OK        | Ejecucion detenida antes de cualquier salida PES.                                                                            |

Respaldo: /Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/backups/pre_aplicacion_reglas_institucionales_v4_20260624_231635

## Estado git
```
?? estudiantes_extranjeros_2026/backups/pre_aplicacion_reglas_institucionales_v4_20260624_231036/
?? estudiantes_extranjeros_2026/backups/pre_aplicacion_reglas_institucionales_v4_20260624_231505/
?? estudiantes_extranjeros_2026/backups/pre_aplicacion_reglas_institucionales_v4_20260624_231635/
?? estudiantes_extranjeros_2026/scripts/aplicar_reglas_institucionales_extranjeros_v4.py
```
