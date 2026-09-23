# Changelog de columnas Bettersoft: v0.9.1 → v1.0

Fecha: 2026-09-23. Base: `DICCIONARIO_MAESTRO_UPLUS_SIES_2026_v0.9.1_GATE09.xlsx`. La v1.0 no cambia reglas funcionales ni prioridades de campos.

## Conteos

| Versión | Filas del diccionario | Solicitadas a Bettersoft | P1 | P2 | P3 | P4 | No calcular en U+ |
|---|---|---|---|---|---|---|---|
| v0.9 | 61 | 61 | 25 | 23 | 8 | 5 | 0 |
| v0.9.1 (Gate 09) | 66 | 48 | 18 | 19 | 8 | 3 | 18 |
| v1.0 (Gate 10) | 66 | 48 | 18 | 19 | 8 | 3 | 18 |

Los cambios de v0.9 a v0.9.1 están en `REPORTE_CIERRE_GATE09_UPLUS_SIES_2026.md` (sección F).

## Cambios v0.9.1 → v1.0

| CAMPO | ATRIBUTO | V0.9.1 | V1.0 | CLASE | MOTIVO |
|---|---|---|---|---|---|
| UP-10 SEXO_UPLUS | ESTADO | OBSERVADO M/F; PENDIENTE S | OBSERVADO M/F; S = PENDIENTE_CATALOGO_OFICIAL_UPLUS (UP-68) | PENDIENTE_BETTERSOFT | Fase 10.3: pendiente residual explícito vinculado a UP-68; no se infiere significado |
| UP-32 PERIODO_INGRESO_UPLUS | ESTADO | 1/2 OBSERVADO; 3 PENDIENTE | 1/2 OBSERVADO; 3 = PENDIENTE_CATALOGO_OFICIAL_UPLUS (UP-68) | PENDIENTE_BETTERSOFT | Fase 10.3: pendiente residual explícito vinculado a UP-68; no se infiere significado |
| UP-68 CATALOGOS_UPLUS_DOCUMENTADOS | ESTADO | PENDIENTE_DATO_UPLUS | PENDIENTE_DATO_UPLUS; incluye PR-01 (SEXO = S) y PR-02 (PERÍODO = 3) | PENDIENTE_BETTERSOFT | Fase 10.3: pendiente residual explícito vinculado a UP-68; no se infiere significado |
| BR-07 (brecha) | CAMBIO SOLICITADO | Exponer tipo de documento U+ y su código SIES (R/P); separar NUM_DOCUMENTO y DV. | Exponer el tipo de documento registrado en U+ (UP-03) y separar número y dígito verificador. | MODIFICADO | INCONSISTENCIA_INTER_ARTEFACTOS: pedía el código SIES R/P, que el diccionario Gate 09 marca NO_CALCULAR (UP-04) |
| BR-10 (brecha) | CAMBIO SOLICITADO | Registrar país de nacionalidad con catálogo de países y exponer código SIES 1-197 además del texto. | Registrar la nacionalidad con un catálogo de países en U+ y entregar el valor registrado (UP-14). | MODIFICADO | INCONSISTENCIA_INTER_ARTEFACTOS: pedía el código SIES 1-197, que el diccionario Gate 09 marca NO_CALCULAR (UP-15) |
| BR-15 (brecha) | CAMBIO SOLICITADO | Entregar nivel a la fecha de corte, régimen del plan y nivel en semestres; documentar el valor 20. | Entregar el nivel registrado en U+ a la fecha de corte y el régimen del plan (UP-41, UP-30); documentar el valor 20 en el catálogo (UP-68). | MODIFICADO | INCONSISTENCIA_INTER_ARTEFACTOS: pedía el nivel en semestres, que Gate 09 asigna a la institución |
| BR-20 (brecha) | CAMBIO SOLICITADO | Exponer estado civil con catálogo FCU, dirección desagregada y código de comuna/región oficial. | Entregar estado civil y comuna tal como están en U+ (UP-19, UP-21) y la dirección desagregada (UP-20). | MODIFICADO | INCONSISTENCIA_INTER_ARTEFACTOS: pedía códigos FCU, que Gate 09 dejó como homologación institucional |
| BR-23 (brecha) | PRIORIDAD | P4 | P2 | RECLASIFICADO | Alineación con UP-59/UP-60 (P2 en Gate 09); no es una nueva decisión de prioridad |
| BR-23 (brecha) | CAMBIO SOLICITADO | Fechas de egreso y titulación suben a P2: se requieren para identificar egresados con matrícula vigente en Matrícula Unificada. | Registrar la fecha de egreso y la fecha de titulación de cada matrícula (UP-59, UP-60). | MODIFICADO | INCONSISTENCIA_INTER_ARTEFACTOS: la brecha seguía en P4 aunque Gate 09 subió UP-59 y UP-60 a P2 |

**SIN_CAMBIO:** 63 filas del diccionario (UP-01, UP-02, UP-03, UP-04, UP-05, UP-06, UP-07, UP-08, UP-09, UP-11, UP-13, UP-14, UP-15, UP-16, UP-17, UP-18, UP-19, UP-20, UP-21, UP-22, UP-23, UP-24, UP-25, UP-26, UP-27, UP-28, UP-29, UP-30, UP-31, UP-33, UP-34, UP-35, UP-36, UP-37, UP-38, UP-39, UP-40, UP-41, UP-42, UP-43, UP-44, UP-45, UP-46, UP-47, UP-48, UP-49, UP-50, UP-51, UP-52, UP-53, UP-54, UP-55, UP-56, UP-57, UP-58, UP-59, UP-60, UP-61, UP-62, UP-63, UP-64, UP-65, UP-66).

Clases usadas: SIN_CAMBIO, MODIFICADO, RECLASIFICADO, PENDIENTE_BETTERSOFT. No hay campos NUEVOS ni ELIMINADOS en v1.0.
