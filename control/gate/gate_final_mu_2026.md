# Gate Final MU 2026

- Fecha: 2026-04-01
- Responsable:
- Decision final: `APROBADO`
- Listo para auditoria: `SI`
- Listo para carga: `SI`
- No listo para carga: `NO`

## Resumen del tablero

- Columnas en `OK` (32): `A TIPO_DOC`, `B N_DOC`, `C DV`, `D PRIMER_APELLIDO`, `E SEGUNDO_APELLIDO`, `F NOMBRE`, `G SEXO`, `H FECH_NAC`, `I NAC`, `J PAIS_EST_SEC`, `K COD_SED`, `L COD_CAR`, `M MODALIDAD`, `N JOR`, `O VERSION`, `P FOR_ING_ACT`, `Q ANIO_ING_ACT`, `R SEM_ING_ACT`, `S ANIO_ING_ORI`, `T SEM_ING_ORI`, `U ASI_INS_ANT`, `V ASI_APR_ANT`, `W PROM_PRI_SEM`, `X PROM_SEG_SEM`, `Y ASI_INS_HIS`, `Z ASI_APR_HIS`, `AA NIV_ACA`, `AB SIT_FON_SOL`, `AC SUS_PRE`, `AD FECHA_MATRICULA`, `AE REINCORPORACION`, `AF VIG`
- Columnas en `Pendiente` (0): 
- Conteo final: `32 OK / 0 Pendiente`

## Validacion de invariantes

| Invariante | Resultado | Evidencia | Observacion |
|---|---|---|---|
| CSV final sin header | SI | resultados/matricula_unificada_2026_pregrado.csv | Filas finales: 1131 |
| 32 columnas exactas | SI | resultados/matricula_unificada_2026_pregrado.csv | Columnas observadas: 32 |
| Separador `;` | SI | resultados/matricula_unificada_2026_pregrado.csv | Delimitacion contractual vigente |
| `SEXO` valido | SI | resultados/matricula_unificada_2026_pregrado.csv | Distribucion observada: {'M': 595, 'H': 536} |
| `FOR_ING_ACT` en catálogo `1..11` | SI | resultados/matricula_unificada_2026_pregrado.csv | Distribucion observada: {'1': 1131} |
| Anexo 7 continuidad (`FOR` en `{2,3,4,5,11}` ⇒ ORI != ACT) | SI | resultados/matricula_unificada_2026_pregrado.csv | Filas continuidad evaluadas: 0 |
| Exclusion de `PRIMERA_OPCION` | SI | resultados/archivo_listo_para_sies.xlsx | Filas incluidas con heuristica opaca: 0 |

## Estado por fase

| Fase | Resultado | Riesgo residual | Reporte asociado |
|---|---|---|---|
| FASE 0 | OK | Sin bloqueo residual. | control/evidencias/D_primer_apellido.md + control/evidencias/F_nombre.md + control/evidencias/G_sexo.md + control/evidencias/P_for_ing_act.md |
| FASE 1 | OK | Sin bloqueo residual. | control/reportes/reporte_identidad_mu_2026.json |
| FASE 2 | OK | Sin bloqueo residual. | control/reportes/reporte_sies_oferta_mu_2026.json |
| FASE 3 | OK | Sin bloqueo residual. | control/reportes/reporte_cronologia_mu_2026.json + control/reportes/reporte_niv_fecha_mu_2026.json |
| FASE 4 | OK | Sin bloqueo residual. | control/reportes/reporte_rendimiento_mu_2026.json |
| FASE 5 | OK | Sin bloqueo residual. | control/reportes/reporte_estado_admin_mu_2026.json |

## Bloqueos residuales abiertos

| Bloqueo ID | Campo(s) | Impacto | Mitigacion | Estado |
|---|---|---|---|---|

## Condiciones de aprobacion

- `APROBADO`: invariantes conformes, evidencia completa y sin bloqueo critico abierto.
- `CONDICIONAL`: invariantes conformes, evidencia suficiente y backlog residual trazado.
- `RECHAZADO`: ruptura de invariante, evidencia insuficiente o perdida de trazabilidad.

## Firma operativa

- Responsable:
- Fecha: 2026-04-01
- Comentario final: Decision `APROBADO`. CSV e invariantes en verde sin pendientes residuales.