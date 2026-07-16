# Informe H111 - Decision interna NIVEL / periodizacion Carreras 16769

**Dictamen:** BLOQUEADO_TOTAL

Este hito no modifica fuentes originales, no genera CSV final, no genera SIES_READY y no declara carga lista.

## Resumen
| campo | valor |
| --- | --- |
| Proceso | Avance Curricular SIES 2026 |
| Subproyecto | Carreras Avance Curricular 2026 / ID SIES 16769 |
| Ano proceso | 2026 |
| Ano referencia datos | 2025 |
| Estado final | BLOQUEADO_TOTAL |
| Declaracion carga | NO_LISTO_PARA_CARGA |
| CSV final generado | NO |
| SIES_READY generado | NO |
| Fuentes originales modificadas | NO |
| Precarga 5810 filas | 43 |
| Match Oferta/MU por CODIGO_UNICO | 43/43 |
| Carreras con detalle canonico despues de resolver H110+MU | 43/43 |

_Se muestran 12 de 16 filas._

## A. Regla oficial
El instructivo Avance Curricular gobierna Carreras 16769 como estructura de plan, con duracion de estudios en semestres y distribucion anual de unidades. El instructivo no define la columna raw `NIVEL` de los planes canonicos.

| regla | referencia_lineas | interpretacion_operativa | nivel_respaldo |
| --- | --- | --- | --- |
| Orden de carga Carreras antes que Matricula | L9, L14, L31, L32, L34, L35 | Carreras 16769 se prepara antes que Matricula 16768. | A. Regla oficial Avance |
| DURACION_ESTUDIOS | L73, L75, L79, L83, L84, L220 | Duracion de estudios se trata como semestres para validar anios permitidos. | A. Regla oficial Avance |
| TOTAL_UNIDADES_MEDIDA | L326, L621 | Debe corresponder al total entero de unidades informadas para la carrera. | A. Regla oficial Avance |
| UNIDADES_1ER_ANIO a UNIDADES_7MO_ANIO | L34, L42, L48, L49, L96, L100 | Distribucion anual de unidades del plan; no debe exceder la duracion formal. | A. Regla oficial Avance |
| TIPO_UNIDAD_MEDIDA | L319, L612, L613, L625 | Campo de unidad de medida definido por el instructivo; no se deriva desde PROMEDIOS. | A. Regla oficial Avance |
| VIGENCIA | L213, L251, L253, L257, L367, L510 | Debe conservar la regla/codigo del instructivo y la precarga. | A. Regla oficial Avance |
| Semantica de NIVEL en fuente canonica |  | No se puede presentar NIVEL->anio como regla oficial; solo podria ser decision interna si supera validaciones. | E. Pendiente respecto del manual |

## B. Datos observados
- Precarga 5810: 43 carreras.
- Oferta/MU `DURACION_ESTUDIOS.tsv`: match 43/43 por `CODIGO_UNICO` y duracion coincidente con 5810.
- Auditoria SIES/MU: resuelve los tres planes que H110 habia dejado sin enlace estructurado: ADMP20251, CONG20251 y AUDT20251.
- Plan canonico: contiene `CODPESTUD`, `CODRAMO` y `NIVEL`, pero no trae diccionario que convierta `NIVEL` a anio formal SIES.
- PROMEDIOS se usa solo como contraste interno; no es fuente normativa ni estructural para Carreras.

## C. Implementacion tecnica probada
Se simulo `ANIO_SIES = techo(NIVEL / 2)` sobre los planes canonicos, deduplicando unidades por `CODRAMO`, y se valido contra `ANIOS_PERMITIDOS = techo(DURACION_ESTUDIOS / 2)`.

## D. Decision interna
La decision interna de H111 es **no aprobar globalmente** la conversion `ANIO = techo(NIVEL / 2)` para generar H112. Aunque la evidencia MU/Oferta resuelve duracion, tipo de plan y los tres `CODPESTUD` faltantes, la conversion candidata produce unidades fuera de duracion en 42 de 43 carreras.

La evidencia interna si permite cerrar que las tres carreras H110 sin enlace estructurado tienen plan trazable por Oferta/MU, pero eso no basta para reconstruir la distribucion anual.

## E. Pendientes
Queda pendiente una fuente o regla interna distinta que ubique cada unidad del plan en el anio formal SIES sin exceder duracion. No corresponde pasar a H112 mientras esa regla no exista o no supere las validaciones bloqueantes.

## Match 5810 vs Oferta/MU
| CODIGO_UNICO | NOMBRE_CARRERA | DURACION_ESTUDIOS_5810 | DURACION_OFERTA_MU | TIPO_PLAN_CARRERA | FAMILIA_FUNCIONAL | ESTADO_MATCH_OFERTA |
| --- | --- | --- | --- | --- | --- | --- |
| I162S2C91J1V1 | TECNICO EN ENFERMERIA | 5 | 5 | 1 | TECNICA | MATCH_OFERTA_MU |
| I162S2C91J2V1 | TECNICO EN ENFERMERIA | 5 | 5 | 1 | TECNICA | MATCH_OFERTA_MU |
| I162S2C57J1V1 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | 5 | 5 | 1 | TECNICA | MATCH_OFERTA_MU |
| I162S2C57J2V1 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | 5 | 5 | 1 | TECNICA | MATCH_OFERTA_MU |
| I162S2C57J4V1 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | 5 | 5 | 1 | TECNICA | MATCH_OFERTA_MU |
| I162S2C78J2V1 | TECNICO EN ADMINISTRACION DE EMPRESAS | 5 | 5 | 1 | TECNICA | MATCH_OFERTA_MU |
| I162S2C89J4V1 | TECNICO EN CIENCIA DE DATOS | 5 | 5 | 1 | TECNICA | MATCH_OFERTA_MU |
| I162S2C85J4V1 | CONTABILIDAD GENERAL | 5 | 5 | 1 | TECNICA | MATCH_OFERTA_MU |
| I162S2C84J4V1 | TECNICO EN ADMINISTRACION PUBLICA | 5 | 5 | 1 | TECNICA | MATCH_OFERTA_MU |
| I162S2C79J4V1 | TECNICO EN LOGISTICA | 5 | 5 | 1 | TECNICA | MATCH_OFERTA_MU |
| I162S2C79J2V1 | TECNICO EN LOGISTICA | 5 | 5 | 1 | TECNICA | MATCH_OFERTA_MU |
| I162S2C78J4V1 | TECNICO EN ADMINISTRACION DE EMPRESAS | 5 | 5 | 1 | TECNICA | MATCH_OFERTA_MU |

_Se muestran 12 de 43 filas._

## Decision NIVEL a anio
| CODIGO_UNICO | CODPESTUD | NOMBRE_CARRERA | DURACION_ESTUDIOS | NIVEL_MAX | UNIDADES_FUERA_DURACION | DECISION_D | PENDIENTE_E |
| --- | --- | --- | --- | --- | --- | --- | --- |
| I162S2C91J1V1 | TENS20251 | TECNICO EN ENFERMERIA | 5 | 7 | 2 | NO_APROBAR_REGLA_GLOBAL | Se requiere otra fuente/regla interna que ubique unidades por anio sin exceder duracion. |
| I162S2C91J2V1 | TENS20251 | TECNICO EN ENFERMERIA | 5 | 7 | 2 | NO_APROBAR_REGLA_GLOBAL | Se requiere otra fuente/regla interna que ubique unidades por anio sin exceder duracion. |
| I162S2C57J1V1 | TPAS20241 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | 5 | 7 | 2 | NO_APROBAR_REGLA_GLOBAL | Se requiere otra fuente/regla interna que ubique unidades por anio sin exceder duracion. |
| I162S2C57J2V1 | TPAS20241 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | 5 | 7 | 2 | NO_APROBAR_REGLA_GLOBAL | Se requiere otra fuente/regla interna que ubique unidades por anio sin exceder duracion. |
| I162S2C57J4V1 | TPAS20241 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | 5 | 7 | 2 | NO_APROBAR_REGLA_GLOBAL | Se requiere otra fuente/regla interna que ubique unidades por anio sin exceder duracion. |
| I162S2C78J2V1 | TAMD20241 | TECNICO EN ADMINISTRACION DE EMPRESAS | 5 | 7 | 2 | NO_APROBAR_REGLA_GLOBAL | Se requiere otra fuente/regla interna que ubique unidades por anio sin exceder duracion. |
| I162S2C89J4V1 | ICDA20251 | TECNICO EN CIENCIA DE DATOS | 5 | 12 | 22 | NO_APROBAR_REGLA_GLOBAL | Se requiere otra fuente/regla interna que ubique unidades por anio sin exceder duracion. |
| I162S2C85J4V1 | CONG20251 | CONTABILIDAD GENERAL | 5 | 7 | 2 | NO_APROBAR_REGLA_GLOBAL | Se requiere otra fuente/regla interna que ubique unidades por anio sin exceder duracion. |
| I162S2C84J4V1 | TAMD20241 | TECNICO EN ADMINISTRACION PUBLICA | 5 | 7 | 2 | NO_APROBAR_REGLA_GLOBAL | Se requiere otra fuente/regla interna que ubique unidades por anio sin exceder duracion. |
| I162S2C79J4V1 | TLOG20241 | TECNICO EN LOGISTICA | 5 | 7 | 2 | NO_APROBAR_REGLA_GLOBAL | Se requiere otra fuente/regla interna que ubique unidades por anio sin exceder duracion. |
| I162S2C79J2V1 | TLOG20241 | TECNICO EN LOGISTICA | 5 | 7 | 2 | NO_APROBAR_REGLA_GLOBAL | Se requiere otra fuente/regla interna que ubique unidades por anio sin exceder duracion. |
| I162S2C78J4V1 | TAMD20241 | TECNICO EN ADMINISTRACION DE EMPRESAS | 5 | 7 | 2 | NO_APROBAR_REGLA_GLOBAL | Se requiere otra fuente/regla interna que ubique unidades por anio sin exceder duracion. |

_Se muestran 12 de 43 filas._

## Resultado de validaciones
| validacion | esperado | observado | estado |
| --- | --- | --- | --- |
| 43/43 carreras con duracion validada en MU/Oferta | 43 | 43 | OK |
| Duracion 5810 coincide con Oferta/MU | 43 | 43 | OK |
| 43/43 carreras con detalle o justificacion formal | 43 | 43 | OK |
| 3 carreras sin detalle H110 resueltas trazablemente | 3 | 3 | OK |
| NIVEL interpretado trazablemente como semestre para Avance | SI | NO | BLOQUEADO |
| ANIO=techo(NIVEL/2) aprobado como decision interna global | SI | NO | BLOQUEADO |
| Cero carreras con unidades fuera de duracion | 0 | 42 | BLOQUEADO |
| TOTAL_UNIDADES_MEDIDA = suma anios candidato | 43 | 43 | OK |
| Sin PROMEDIOS como norma | SI | SI | OK |
| Sin matricula 5809 como fuente estructural | SI | SI | OK |
| Sin matriz agregada rechazada por SIES como fuente final | SI | SI | OK |
| CSV final generado | NO | NO | OK |

_Se muestran 12 de 13 filas._

## Tres carreras H110
| CODIGO_UNICO | NOMBRE_CARRERA | DURACION_ESTUDIOS_5810 | PLAN_CONCILIACION_H110 | FUNDAMENTO_H110 | EXCEPCION_H110 | PLAN_OFERTA_MU | TIPO_PLAN_CARRERA_MU | DURACION_MU | ESTADO_RESOLUCION_MU | METODOS_USADOS_MU | CODPESTUD_USADO_CANDIDATO | REGISTROS_DETALLE_CANONICO | NIVELES_OBSERVADOS | UNIDADES_FUERA_DURACION_BAJO_TECHO_NIVEL_2 | CATEGORIA | DICTAMEN_CASO | OBSERVACION |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I162S2C83J4V1 | ADMINISTRACION PUBLICA | 8 | ADMP20251 | 69 de 70 personas con plan explícito ADMP20251; 68 personas con coincidencia exacta del CODIGO_UNICO en múltiples fuentes técnicas activas. | Una persona no presentó plan explícito recuperado. No se observó un plan alternativo demostrado para este código. | ADMP20251 | 1 | 8 | RESUELTA_POR_DECISION_MANUAL | REGLA_TIPO_PLAN | ADMP20251 | 49 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 | 14 | RESUELTO_POR_OFERTA_MU_Y_PROMEDIOS | Plan trazable resuelto; distribucion anual sigue bloqueada por regla NIVEL->anio. | Oferta/MU entrega plan y Codigo Unico final; PROMEDIOS queda solo como contraste no normativo. |
| I162S2C85J4V1 | CONTABILIDAD GENERAL | 5 | CONG20251 | 38 de 38 personas con plan explícito CONG20251; coincidencia exacta del CODIGO_UNICO y plan único observado en la fuente institucional. |  | CONG20251 | 1 | 5 | RESUELTA_INEQUIVOCAMENTE |  | CONG20251 | 26 | 1, 2, 3, 4, 5, 6, 7 | 2 | RESUELTO_POR_OFERTA_MU_Y_PROMEDIOS | Plan trazable resuelto; distribucion anual sigue bloqueada por regla NIVEL->anio. | Oferta/MU entrega plan y Codigo Unico final; PROMEDIOS queda solo como contraste no normativo. |
| I162S2C86J4V1 | AUDITORIA | 8 | AUDT20251 | 41 personas asociadas a AUDT20251 en el control; 40 presentan coincidencia exacta del CODIGO_UNICO en múltiples fuentes técnicas activas. | Una persona presenta además IADM20241, pero esa trayectoria está asociada al código I162S2C76J4V1 y no al código de Auditoría evaluado. | AUDT20251 | 1 | 8 | RESUELTA_POR_DECISION_MANUAL | REGLA_TIPO_PLAN | AUDT20251 | 47 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 | 14 | RESUELTO_POR_OFERTA_MU_Y_PROMEDIOS | Plan trazable resuelto; distribucion anual sigue bloqueada por regla NIVEL->anio. | Oferta/MU entrega plan y Codigo Unico final; PROMEDIOS queda solo como contraste no normativo. |

## Carreras compatibles bajo la regla candidata
| CODIGO_UNICO | NOMBRE_CARRERA | CODPESTUD | DURACION_ESTUDIOS | NIVEL_MAX | UNIDADES_FUERA_DURACION |
| --- | --- | --- | --- | --- | --- |
| I162S2C11J2V1 | TECNICO EN AUTOMATIZACION Y CONTROL INDUSTRIAL | TMIRE20171 | 5 | 5 | 0 |

## Carreras con unidades fuera de duracion
| CODIGO_UNICO | NOMBRE_CARRERA | CODPESTUD | DURACION_ESTUDIOS | ANIOS_PERMITIDOS | NIVEL_MAX | UNIDADES_FUERA_DURACION | MOTIVO_ESTADO |
| --- | --- | --- | --- | --- | --- | --- | --- |
| I162S2C91J1V1 | TECNICO EN ENFERMERIA | TENS20251 | 5 | 3 | 7 | 2 | conversion candidata genera unidades fuera de duracion |
| I162S2C91J2V1 | TECNICO EN ENFERMERIA | TENS20251 | 5 | 3 | 7 | 2 | conversion candidata genera unidades fuera de duracion |
| I162S2C57J1V1 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | TPAS20241 | 5 | 3 | 7 | 2 | conversion candidata genera unidades fuera de duracion |
| I162S2C57J2V1 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | TPAS20241 | 5 | 3 | 7 | 2 | conversion candidata genera unidades fuera de duracion |
| I162S2C57J4V1 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | TPAS20241 | 5 | 3 | 7 | 2 | conversion candidata genera unidades fuera de duracion |
| I162S2C78J2V1 | TECNICO EN ADMINISTRACION DE EMPRESAS | TAMD20241 | 5 | 3 | 7 | 2 | conversion candidata genera unidades fuera de duracion |
| I162S2C89J4V1 | TECNICO EN CIENCIA DE DATOS | ICDA20251 | 5 | 3 | 12 | 22 | conversion candidata genera unidades fuera de duracion |
| I162S2C85J4V1 | CONTABILIDAD GENERAL | CONG20251 | 5 | 3 | 7 | 2 | conversion candidata genera unidades fuera de duracion |
| I162S2C84J4V1 | TECNICO EN ADMINISTRACION PUBLICA | TAMD20241 | 5 | 3 | 7 | 2 | conversion candidata genera unidades fuera de duracion |
| I162S2C79J4V1 | TECNICO EN LOGISTICA | TLOG20241 | 5 | 3 | 7 | 2 | conversion candidata genera unidades fuera de duracion |
| I162S2C79J2V1 | TECNICO EN LOGISTICA | TLOG20241 | 5 | 3 | 7 | 2 | conversion candidata genera unidades fuera de duracion |
| I162S2C78J4V1 | TECNICO EN ADMINISTRACION DE EMPRESAS | TAMD20241 | 5 | 3 | 7 | 2 | conversion candidata genera unidades fuera de duracion |
| I162S2C6J4V2 | TECNICO EN CONECTIVIDAD Y REDES | TCRE20241 | 5 | 3 | 7 | 2 | conversion candidata genera unidades fuera de duracion |
| I162S2C6J2V2 | TECNICO EN CONECTIVIDAD Y REDES | TCRE20241 | 5 | 3 | 7 | 2 | conversion candidata genera unidades fuera de duracion |
| I162S2C47J1V1 | TECNICO EN CIBERSEGURIDAD | ICIB20241 | 5 | 3 | 12 | 23 | conversion candidata genera unidades fuera de duracion |
| I162S2C47J2V1 | TECNICO EN CIBERSEGURIDAD | ICIB20241 | 5 | 3 | 12 | 23 | conversion candidata genera unidades fuera de duracion |
| I162S2C6J2V1 | TECNICO EN CONECTIVIDAD Y REDES | TCRE20241 | 5 | 3 | 7 | 2 | conversion candidata genera unidades fuera de duracion |
| I162S2C47J4V1 | TECNICO EN CIBERSEGURIDAD | ICIB20241 | 5 | 3 | 12 | 23 | conversion candidata genera unidades fuera de duracion |
| I162S2C46J1V1 | INGENIERIA EN CIBERSEGURIDAD | ICIB20241 | 8 | 4 | 12 | 14 | conversion candidata genera unidades fuera de duracion |
| I162S2C46J2V1 | INGENIERIA EN CIBERSEGURIDAD | ICIB20241 | 8 | 4 | 12 | 14 | conversion candidata genera unidades fuera de duracion |

_Se muestran 20 de 42 filas._

## Conclusion
Dictamen H111: **BLOQUEADO_TOTAL**. No se habilita generacion de CSV final en H112 con la regla candidata actual.
