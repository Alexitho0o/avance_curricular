# Reporte resolución códigos SIES V6

Fecha: 2026-06-25 14:12:14

## Hallazgo
El primer buscador no detectó IINF072 porque buscaba principalmente CODIGO_UNICO; el campo explícito correcto en archivo_listo_para_sies.xlsx es CODIGO_CARRERA_SIES_FINAL.

## Decisiones
| CODCLI       | CODIGO_SIES_FINAL | CLASIFICACION                   | FUENTE                                                                                                                                    | HOJA                 | FILA | CAMPO_FUENTE              | PLAN_DE_ESTUDIO | CARRERA                            | JORNADA_FUENTE | COD_SED | COD_CAR | JOR | VERSION | METODO                    | CONFIANZA            | ESTADO                             | REQUIERE_REVISION | OBSERVACION                                                                  |
| ------------ | ----------------- | ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | -------------------- | ---- | ------------------------- | --------------- | ---------------------------------- | -------------- | ------- | ------- | --- | ------- | ------------------------- | -------------------- | ---------------------------------- | ----------------- | ---------------------------------------------------------------------------- |
| 20251IINF072 | I162S2C1J2V4      | RESUELTO_CODIGO_FINAL_EXPLICITO | /Users/alexi/Documents/GitHub/avance_curricular/resultados/archivo_listo_para_sies.xlsx                                                   | ARCHIVO_LISTO_SUBIDA | 2273 | CODIGO_CARRERA_SIES_FINAL | IINF20241       | INGENIERIA EN INFORMATICA          | V              | 2       | 1       | 2   | 4       | REGLA_COD_CAR_JOR_VERSION | 95%                  | VALIDADO_DESDE_MATRICULA_UNIFICADA | NO                | ESTADO_CARGA_PREGRADO duplicado no invalida el codigo SIES.                  |
| 20251AUDT004 |                   | MULTIPLES_CANDIDATOS            | /Users/alexi/Documents/GitHub/avance_curricular/control/catalogos/PUENTE_SIES_COMPILADO.tsv                                               | TSV                  | 26   | CODIGOS_SIES_POTENCIALES  |                 | AUDITORIA                          | O              |         |         |     |         | AMBIGUO                   | PENDIENTE_GOBERNANZA | PENDIENTE_INSTITUCIONAL            | SI                | No se resuelve: falta distinguir version/jornada o hay multiples candidatos. |
| 20241ICRE068 |                   | MULTIPLES_CANDIDATOS            | /Users/alexi/Documents/GitHub/avance_curricular/control/evidencias/2026-04-04_22-54-11_fix5_recovery_estable/archivo_listo_para_sies.xlsx | ARCHIVO_LISTO_SUBIDA | 228  | CODIGOS_SIES_POTENCIALES  | ICRE20241       | INGENIERIA EN CONECTIVIDAD Y REDES | V              | 2       |         |     |         | PENDIENTE_GOBERNANZA      | 0%                   | PENDIENTE_INSTITUCIONAL            | SI                | No se resuelve: falta distinguir version/jornada o hay multiples candidatos. |

## Advertencias
| CODCLI       | RUT         | NOMBRE                         | ADVERTENCIA    | VARIABLE_AFECTADA | BLOQUEA_CARGA | TIPO              | ACCION_RECOMENDADA                                                          | ESTADO_V6             |
| ------------ | ----------- | ------------------------------ | -------------- | ----------------- | ------------- | ----------------- | --------------------------------------------------------------------------- | --------------------- |
| 20251IADM119 | 100815234-5 | ANDREW TASAMA DEVIA            | TIPO_DOCUMENTO | TIPO_DOCUMENTO    | NO            | SOLO_TRAZABILIDAD | Mantener seguimiento documental; no convertir en error sin nueva evidencia. | APTO_CON_ADVERTENCIAS |
| 20251TLOG037 | 22580082-0  | ANDREA ALEJANDRA CERNA MENDOZA | TIPO_DOCUMENTO | TIPO_DOCUMENTO    | NO            | SOLO_TRAZABILIDAD | Mantener seguimiento documental; no convertir en error sin nueva evidencia. | APTO_CON_ADVERTENCIAS |
| 20251IINF115 | 100659788-9 | LUISA FERNANDA RAMÍREZ GUECHA  | TIPO_DOCUMENTO | TIPO_DOCUMENTO    | NO            | SOLO_TRAZABILIDAD | Mantener seguimiento documental; no convertir en error sin nueva evidencia. | APTO_CON_ADVERTENCIAS |
| 20251TENS004 | 27829890-6  | LUNA DAIAM LINARES OICATA      | TIPO_DOCUMENTO | TIPO_DOCUMENTO    | NO            | SOLO_TRAZABILIDAD | Mantener seguimiento documental; no convertir en error sin nueva evidencia. | APTO_CON_ADVERTENCIAS |
| 20251TLOG067 | 100681501-0 | JUNIA CLEOPHAT CLEOPHAT        | TIPO_DOCUMENTO | TIPO_DOCUMENTO    | NO            | SOLO_TRAZABILIDAD | Mantener seguimiento documental; no convertir en error sin nueva evidencia. | APTO_CON_ADVERTENCIAS |

## Nacionalidad
| CODCLI | RUT | NOMBRE | VALOR_ACTUAL | FUENTE | MOTIVO_PENDIENTE                     |
| ------ | --- | ------ | ------------ | ------ | ------------------------------------ |
|        |     |        |              |        | SIN_PENDIENTES_DE_NACIONALIDAD_EN_V6 |

## Estados V6
| Estado                  | Registros |
| ----------------------- | --------- |
| APTO                    | 54        |
| APTO_CON_ADVERTENCIAS   | 5         |
| PENDIENTE_INSTITUCIONAL | 2         |

## Validación
| CONTROL                                                  | RESULTADO | DETALLE                                                          |
| -------------------------------------------------------- | --------- | ---------------------------------------------------------------- |
| Base 61 intacta                                          | OK        | 386e9895f6534dd4faf031c6b3e2d271118b337c9134df48c81aa92560717097 |
| V5 intacta                                               | OK        | ddadc8d3a7f746b21d9d4c72746a83f8ffeb6f61b0ee13086020b0fbc31f7a19 |
| V6 contiene 61 filas                                     | OK        | 61                                                               |
| Existen 20 TSV V6                                        | OK        | 20                                                               |
| Cada TSV tiene 61 filas                                  | OK        |                                                                  |
| 20251IINF072 tiene I162S2C1J2V4                          | OK        |                                                                  |
| Codigo IINF072 coincide con sede carrera jornada version | OK        |                                                                  |
| 20251AUDT004 solo se completa con evidencia suficiente   | OK        | MULTIPLES_CANDIDATOS                                             |
| 20241ICRE068 solo se completa con evidencia suficiente   | OK        | MULTIPLES_CANDIDATOS                                             |
| No quedan codigos vacios marcados como validados         | OK        |                                                                  |
| No se usa primera coincidencia                           | OK        | AUDT/ICRE permanecen pendientes si hay multiples candidatos.     |
| No se modifican otras variables                          | OK        |                                                                  |
| No se genera PES                                         | OK        | Solo salidas de gobernanza/auditoria V6.                         |
| No existen errores bloqueantes                           | OK        |                                                                  |

## Hashes
| ARCHIVO | HASH                                                             |
| ------- | ---------------------------------------------------------------- |
| BASE61  | 386e9895f6534dd4faf031c6b3e2d271118b337c9134df48c81aa92560717097 |
| V5      | ddadc8d3a7f746b21d9d4c72746a83f8ffeb6f61b0ee13086020b0fbc31f7a19 |
| V6      | a026ca5da08d8245b0c8f60477e448ac5cbd0564d37d57f3fbf6b38b1a6045be |
| SCRIPT  | 475237225d725e2bd7df8ad9d6a484b1d7dc50d1b07419b5876cf9e4924024f8 |

Respaldo: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/backups/pre_resolucion_codigos_sies_v6_20260625_140952`

## Estado Git
```text
?? backups/pre_resolucion_codigos_sies_v6_20260625_140341/
?? backups/pre_resolucion_codigos_sies_v6_20260625_140631/
?? backups/pre_resolucion_codigos_sies_v6_20260625_140952/
?? resultados/reportes/REPORTE_RESOLUCION_CODIGOS_SIES_V6.md
?? scripts/resolver_codigos_sies_v6.py

```