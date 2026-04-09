# Reporte busqueda final pendientes V3

Fecha: 2026-06-24T19:57:21
V3 creada: SI

## Fuentes inspeccionadas
Archivos inventariados: 1351

## Evidencias
Aceptadas: 71
Rechazadas/no suficientes: 110

## Mejora por variable
| COLUMNA                     | VALIDADOS_V2 | VALIDADOS_V3 | PENDIENTES_V2 | PENDIENTES_V3 | CONFLICTOS_V2 | CONFLICTOS_V3 | MEJORA | FUENTE_NUEVA                                                                                                                                                                                                                                                                  | OBSERVACION                  |
| --------------------------- | ------------ | ------------ | ------------- | ------------- | ------------- | ------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| NACIONALIDAD                | 61           | 61           | 1             | 1             | 0             | 0             | 0      |                                                                                                                                                                                                                                                                               | Sin mejora valida adicional. |
| TIPO_RESIDENCIA_ESTUDIANTE  | 0            | 0            | 62            | 62            | 0             | 0             | 0      |                                                                                                                                                                                                                                                                               | Sin mejora valida adicional. |
| PAIS_ORIGEN                 | 0            | 62           | 62            | 0             | 0             | 0             | 62     | /Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/docs/Instructivo_Estudiantes_Extranjeros_SIES_2026.txt                                                                                                                                           | V3 creada con mejoras.       |
| PAIS_ESTUDIOS_SECUNDARIOS   | 50           | 50           | 12            | 12            | 0             | 0             | 0      |                                                                                                                                                                                                                                                                               | Sin mejora valida adicional. |
| CODIGO_UNICO                | 45           | 51           | 17            | 11            | 0             | 0             | 6      | /Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/RESOLUCION_CODIGO_UNICO.csv | /Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/CANDIDATOS_19_COINCIDENCIAS_MULTIPLES.csv | V3 creada con mejoras.       |
| ANIO_INGRESO_CARRERA_ORIGEN | 50           | 50           | 12            | 12            | 0             | 0             | 0      |                                                                                                                                                                                                                                                                               | Sin mejora valida adicional. |
| SEM_INGRESO_CARRERA_ORIGEN  | 50           | 50           | 12            | 12            | 0             | 0             | 0      |                                                                                                                                                                                                                                                                               | Sin mejora valida adicional. |
| VIGENCIA                    | 59           | 62           | 3             | 0             | 0             | 0             | 3      | /Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/AUDITORIA_VIGENCIA_2025_CORREGIDA.csv                                                                                                                                      | V3 creada con mejoras.       |

## Estado global registros
| ESTADO                  | REGISTROS |
| ----------------------- | --------- |
| PENDIENTE_INSTITUCIONAL | 62        |

## Pendientes finales
| VARIABLE                    | PENDIENTES |
| --------------------------- | ---------- |
| NACIONALIDAD                | 1          |
| TIPO_RESIDENCIA_ESTUDIANTE  | 62         |
| PAIS_ORIGEN                 | 0          |
| PAIS_ESTUDIOS_SECUNDARIOS   | 12         |
| CODIGO_UNICO                | 11         |
| ANIO_INGRESO_CARRERA_ORIGEN | 12         |
| SEM_INGRESO_CARRERA_ORIGEN  | 12         |
| VIGENCIA                    | 0          |

## Limitaciones
- No se encontro residencia explicita; no se infirio desde domicilio, RUT, nacionalidad o documento.
- No se encontro pais explicito de estudios secundarios para los 12 pendientes.
- No se encontro nacionalidad explicita para el valor Por definir.
- Ingreso de carrera de origen queda pendiente si la fuente estructurada no trae anio/semestre de origen.

## Hashes
{
  "BASE_CONGELADA_TSV": "da85dd0c453a942a4490f469b75d0418e9054e458a46028f44271ac704518081",
  "MATRIZ_V2": "be7d568c1cfff4efb635c62f3d9f12f302641a8c9bea09d269fb083e0c29b913",
  "MATRIZ_V3": "54876c75ae412e372657726c64c520d7c50c18d742f3c36827c222c5ce45d70c",
  "SCRIPT": "60fd4430c6c2efa7747fc846a7281d8994e97d3043f49e4a642f5879bbe67649",
  "NOMINA_GESTION": "61cb7efc55600773dc75a935f3677e7224e5fba8d462fe78edcb711a6c4ed696",
  "VALIDACION": "8fcc5e2bf13de2d306fc85fa18734a4618723f9c41b32835acf63881b21a0b0b"
}

Respaldo: /Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/backups/pre_busqueda_final_pendientes_v3_20260624_195634

## Estado git
```
?? estudiantes_extranjeros_2026/backups/pre_busqueda_final_pendientes_v3_20260624_194419/
?? estudiantes_extranjeros_2026/backups/pre_busqueda_final_pendientes_v3_20260624_195035/
?? estudiantes_extranjeros_2026/backups/pre_busqueda_final_pendientes_v3_20260624_195236/
?? estudiantes_extranjeros_2026/backups/pre_busqueda_final_pendientes_v3_20260624_195330/
?? estudiantes_extranjeros_2026/backups/pre_busqueda_final_pendientes_v3_20260624_195435/
?? estudiantes_extranjeros_2026/backups/pre_busqueda_final_pendientes_v3_20260624_195634/
?? estudiantes_extranjeros_2026/resultados/reportes/REPORTE_BUSQUEDA_FINAL_PENDIENTES_V3.md
?? estudiantes_extranjeros_2026/scripts/buscar_y_resolver_pendientes_extranjeros_v3.py
```
