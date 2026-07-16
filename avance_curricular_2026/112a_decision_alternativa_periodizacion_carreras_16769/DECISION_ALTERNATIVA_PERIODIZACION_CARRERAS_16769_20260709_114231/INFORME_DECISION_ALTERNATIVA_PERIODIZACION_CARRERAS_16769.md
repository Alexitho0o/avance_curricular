# Informe H112A - Decision alternativa periodizacion Carreras 16769

**Dictamen:** APTO_PARA_GENERAR_CSV_H112B

Este hito no genera CSV final, no genera SIES_READY y no modifica fuentes originales.

## Resumen
| campo | valor |
| --- | --- |
| Proceso | Avance Curricular SIES 2026 |
| Subproyecto | Carreras Avance Curricular 2026 / ID SIES 16769 |
| Ano proceso | 2026 |
| Ano referencia datos | 2025 |
| Estado H112A | APTO_PARA_GENERAR_CSV_H112B |
| Declaracion carga | NO_LISTO_PARA_CARGA |
| CSV final generado | NO |
| SIES_READY generado | NO |
| Fuentes originales modificadas | NO |
| Metodo seleccionado | METODO_A_GRUPOS_NIVELES |
| Regla seleccionada | NIVEL como orden curricular observado; grupo=techo(NIVEL_MAX_PLAN/ANIOS_PERMITIDOS); ANIO=techo(NIVEL/grupo) capado a ANIOS_PERMITIDOS. |
| Fuente explicita usable directo | 29/43 |

_Se muestran 12 de 17 filas._

## Separacion de respaldo
- A. Regla oficial: el manual Avance exige consistencia entre duracion y distribucion anual, pero no define `NIVEL`.
- B. Dato observado: Oferta/MU valida duracion 43/43; planes canonicos entregan detalle de unidades; mallas/PDF entregan periodizacion explicita parcial.
- C. Implementacion tecnica: se simulan fuente explicita directa, Metodo A y Metodo B sin aplicar carga.
- D. Decision interna: se selecciona Metodo A como regla candidata para H112B.
- E. Pendiente: generar CSV final solo en H112B con controles de carga, no en este hito.

## Metodo seleccionado
Se selecciona `METODO_A_GRUPOS_NIVELES`: `NIVEL` no se trata como semestre directo. Se usa como orden curricular observado; se calcula `grupo = techo(NIVEL_MAX_PLAN / ANIOS_PERMITIDOS)` y `ANIO_SIES = techo(NIVEL / grupo)`, limitado entre 1 y `ANIOS_PERMITIDOS`.

La seleccion no se basa solo en que pase validaciones tecnicas. La fuente explicita de mallas/PDF no resuelve 43/43 como carga directa, pero muestra periodizacion por `TRIMESTRE` y `ANIO_CURRICULAR`; el Metodo A conserva el orden y reproduce esos cortes cuando la fuente explicita es compatible.

## Comparacion de metodos
| METODO | CARRERAS_CON_DISTRIBUCION | CARRERAS_FUERA_DURACION | CARRERAS_CON_ANIOS_VACIOS_DENTRO_DURACION | TOTAL_UNIDADES | DIFERENCIAS_CON_OTRO_METODO | RESPALDO_FUNCIONAL | DICTAMEN | MOTIVO |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| METODO_A_GRUPOS_NIVELES | 43 | 0 | 0 | 1711 |  | D. Decision interna candidata | SELECCIONADO | Metodo A preserva orden relativo y reproduce cortes observados de periodizacion por trimestres cuando la fuente explicita es usable. |
| METODO_B_ESCALA_PROPORCIONAL | 43 | 0 | 0 | 1711 |  | D. Decision interna candidata | NO_SELECCIONADO | Metodo B pasa validaciones, pero distribuye por escala proporcional y en planes de 7 niveles se aleja del corte observado 1-3,4-6,7. |
| FUENTE_EXPLICITA_ANIO_CURRICULAR | 38 | 9 | 5 | 1516 |  | B/C. Dato observado de mallas/PDF conciliados | NO_USAR_DIRECTO | No resuelve directo 43/43: faltan carreras y algunas exceden duracion formal. |

## Validaciones bloqueantes
| validacion | esperado | observado | estado |
| --- | --- | --- | --- |
| 43/43 carreras con duracion validada | 43 | 43 | OK |
| 43/43 carreras con familia funcional o tipo plan | 43 | 43 | OK |
| 43/43 carreras con distribucion candidata | 43 | 43 | OK |
| 0 carreras sin detalle o sin resolucion trazable | 0 | 0 | OK |
| 0 unidades fuera de duracion | 0 | 0 | OK |
| TOTAL_UNIDADES_MEDIDA = suma anios en 43/43 | 43 | 43 | OK |
| UNIDADES_1ER_ANIO a UNIDADES_7MO_ANIO enteros >= 0 | 43 | 43 | OK |
| Anios superiores a techo(DURACION/2) en cero | 43 | 43 | OK |
| CODIGO_UNICO + PLAN_ESTUDIOS sin duplicados | 0 | 0 | OK |
| No usar H106 como fuente final | SI | SI | OK |
| No usar PROMEDIOS como norma | SI | SI | OK |
| No usar matricula 5809 como estructura Carreras | SI | SI | OK |
| Decision interna registrada como D | SI | SI | OK |
| Error SIES anterior eliminado | 43 | 43 | OK |
| CSV final generado | NO | NO | OK |
| SIES_READY generado | NO | NO | OK |

## Tres carreras trazadas desde H111
| CODIGO_UNICO | NOMBRE_CARRERA | PLAN_OFERTA_MU | CODPESTUD_FINAL | CATEGORIA_H112A | TOTAL_UNIDADES_MEDIDA | ANIOS_PERMITIDOS | UNIDADES_FUERA_DURACION | ESTADO | OBSERVACION |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I162S2C83J4V1 | ADMINISTRACION PUBLICA | ADMP20251 | ADMP20251 | RESUELTO_POR_CODPESTUD | 49 | 4 | 0 | RESUELTO_TRAZABLE | H111 resolvio plan por Oferta/MU; H112A distribuye con Metodo A sobre detalle canonico del CODPESTUD. |
| I162S2C85J4V1 | CONTABILIDAD GENERAL | CONG20251 | CONG20251 | RESUELTO_POR_CODPESTUD | 26 | 3 | 0 | RESUELTO_TRAZABLE | H111 resolvio plan por Oferta/MU; H112A distribuye con Metodo A sobre detalle canonico del CODPESTUD. |
| I162S2C86J4V1 | AUDITORIA | AUDT20251 | AUDT20251 | RESUELTO_POR_CODPESTUD | 47 | 4 | 0 | RESUELTO_TRAZABLE | H111 resolvio plan por Oferta/MU; H112A distribuye con Metodo A sobre detalle canonico del CODPESTUD. |

## Distribucion candidata final
| CODIGO_UNICO | NOMBRE_CARRERA | DURACION_ESTUDIOS | ANIOS_PERMITIDOS | TOTAL_UNIDADES_MEDIDA | UNIDADES_1ER_ANIO | UNIDADES_2DO_ANIO | UNIDADES_3ER_ANIO | UNIDADES_4TO_ANIO | UNIDADES_5TO_ANIO | UNIDADES_6TO_ANIO | UNIDADES_7MO_ANIO | UNIDADES_FUERA_DURACION | ESTADO_FILA |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I162S2C11J2V1 |  | 5 | 3 | 27 | 12 | 12 | 3 | 0 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C1J1V1 |  | 8 | 4 | 48 | 12 | 12 | 14 | 10 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C1J1V2 |  | 8 | 4 | 48 | 12 | 12 | 14 | 10 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C1J2V1 |  | 8 | 4 | 48 | 12 | 12 | 14 | 10 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C1J2V4 |  | 8 | 4 | 48 | 12 | 12 | 14 | 10 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C1J4V2 |  | 8 | 4 | 48 | 12 | 12 | 14 | 10 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C1J4V3 |  | 4 | 2 | 48 | 24 | 24 | 0 | 0 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C3J2V1 |  | 8 | 4 | 47 | 12 | 12 | 13 | 10 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C3J2V4 |  | 8 | 4 | 47 | 12 | 12 | 13 | 10 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C3J4V2 |  | 8 | 4 | 47 | 12 | 12 | 13 | 10 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C3J4V3 |  | 4 | 2 | 47 | 24 | 23 | 0 | 0 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C46J1V1 |  | 8 | 4 | 47 | 12 | 12 | 13 | 10 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C46J2V1 |  | 8 | 4 | 47 | 12 | 12 | 13 | 10 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C46J4V1 |  | 4 | 2 | 47 | 24 | 23 | 0 | 0 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C46J4V3 |  | 8 | 4 | 47 | 12 | 12 | 13 | 10 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C47J1V1 |  | 5 | 3 | 47 | 16 | 17 | 14 | 0 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C47J2V1 |  | 5 | 3 | 47 | 16 | 17 | 14 | 0 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C47J4V1 |  | 5 | 3 | 47 | 16 | 17 | 14 | 0 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C57J1V1 |  | 5 | 3 | 26 | 12 | 12 | 2 | 0 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |
| I162S2C57J2V1 |  | 5 | 3 | 26 | 12 | 12 | 2 | 0 | 0 | 0 | 0 | 0 | APTA_CANDIDATA |

_Se muestran 20 de 43 filas._

## Siguiente paso
Si el responsable del proceso acepta este dictamen interno, el siguiente hito es H112B para generar el CSV final controlado. H112A no genera carga.
