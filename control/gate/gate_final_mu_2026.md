# Gate Final MU 2026

- Fecha: 2026-04-01
- Responsable:
- Decision final: `CONDICIONAL`
- Listo para auditoria: `SI`
- Listo para carga: `NO`
- No listo para carga: `SI`

## Resumen del tablero

- Columnas en `OK` (27): `A TIPO_DOC`, `B N_DOC`, `C DV`, `D PRIMER_APELLIDO`, `E SEGUNDO_APELLIDO`, `F NOMBRE`, `G SEXO`, `H FECH_NAC`, `I NAC`, `J PAIS_EST_SEC`, `K COD_SED`, `L COD_CAR`, `M MODALIDAD`, `N JOR`, `O VERSION`, `P FOR_ING_ACT`, `Q ANIO_ING_ACT`, `R SEM_ING_ACT`, `S ANIO_ING_ORI`, `T SEM_ING_ORI`, `U ASI_INS_ANT`, `V ASI_APR_ANT`, `W PROM_PRI_SEM`, `X PROM_SEG_SEM`, `AA NIV_ACA`, `AD FECHA_MATRICULA`, `AF VIG`
- Columnas en `Pendiente` (5): `Y ASI_INS_HIS`, `Z ASI_APR_HIS`, `AB SIT_FON_SOL`, `AC SUS_PRE`, `AE REINCORPORACION`
- Conteo final: `27 OK / 5 Pendiente`

## Validacion de invariantes

| Invariante | Resultado | Evidencia | Observacion |
|---|---|---|---|
| CSV final sin header | SI | resultados/matricula_unificada_2026_pregrado.csv | Filas finales: 1736 |
| 32 columnas exactas | SI | resultados/matricula_unificada_2026_pregrado.csv | Columnas observadas: 32 |
| Separador `;` | SI | resultados/matricula_unificada_2026_pregrado.csv | Delimitacion contractual vigente |
| `SEXO` valido | SI | resultados/matricula_unificada_2026_pregrado.csv | Distribucion observada: {'H': 1305, 'M': 428, 'NB': 3} |
| `FOR_ING_ACT = 1` | SI | resultados/matricula_unificada_2026_pregrado.csv | Distribucion observada: {'1': 1736} |
| Exclusion de `PRIMERA_OPCION` | SI | resultados/archivo_listo_para_sies.xlsx | Filas incluidas con heuristica opaca: 0 |

## Estado por fase

| Fase | Resultado | Riesgo residual | Reporte asociado |
|---|---|---|---|
| FASE 0 | OK | Sin bloqueo residual. | control/evidencias/D_primer_apellido.md + control/evidencias/F_nombre.md + control/evidencias/G_sexo.md + control/evidencias/P_for_ing_act.md |
| FASE 1 | OK | Sin bloqueo residual. | control/reportes/reporte_identidad_mu_2026.json |
| FASE 2 | OK | Sin bloqueo residual. | control/reportes/reporte_sies_oferta_mu_2026.json |
| FASE 3 | OK | Sin bloqueo residual. | control/reportes/reporte_cronologia_mu_2026.json + control/reportes/reporte_niv_fecha_mu_2026.json |
| FASE 4 | CONDICIONAL | Y ASI_INS_HIS: Alcance historico efectivo disponible en Hoja1 = solo ANO 2025; no existe profundidad multianual para sostener un acumulado historico defendible; Z ASI_APR_HIS: Alcance historico efectivo disponible en Hoja1 = solo ANO 2025; no existe profundidad multianual para sostener un acumulado historico defendible | control/reportes/reporte_rendimiento_mu_2026.json |
| FASE 5 | CONDICIONAL | AB SIT_FON_SOL: No existe fuente real por fila incluida; `SIT_FON_SOL` queda en fallback explicito `0` para `1.736/1.736` filas incluidas; AC SUS_PRE: No existe fuente real por fila incluida; `SUS_PRE` queda en fallback explicito `0` para `1.736/1.736` filas incluidas; AE REINCORPORACION: La derivacion desde `DA_SITUACION = 38 - ...` no cierra la condicion temporal del manual; `16/18` filas con `REINCORPORACION = 1` caen en `PERIODOMATRICULA = 1` y no en ultimo tramo observado | control/reportes/reporte_estado_admin_mu_2026.json |

## Bloqueos residuales abiertos

| Bloqueo ID | Campo(s) | Impacto | Mitigacion | Estado |
|---|---|---|---|---|
| BLK-Y | Y `ASI_INS_HIS` | Alto | Conseguir fuente multianual o acto regulatorio explicito que autorice usar alcance disponible como historico acumulado | Abierto |
| BLK-Z | Z `ASI_APR_HIS` | Alto | Conseguir fuente multianual o acto regulatorio explicito que autorice usar alcance disponible como historico acumulado | Abierto |
| BLK-AB | AB `SIT_FON_SOL` | Medio-Alto | Conseguir fuente institucional o regla formal auditable que distinga `0/1/2` por fila incluida | Abierto |
| BLK-AC | AC `SUS_PRE` | Medio-Alto | Conseguir fuente institucional o regla formal auditable que cuantifique suspensiones previas por fila incluida | Abierto |
| BLK-AE | AE `REINCORPORACION` | Alto | Cerrar una regla temporal institucional verificable o agregar fuente que identifique la ultima carga valida del periodo | Abierto |

## Condiciones de aprobacion

- `APROBADO`: invariantes conformes, evidencia completa y sin bloqueo critico abierto.
- `CONDICIONAL`: invariantes conformes, evidencia suficiente y backlog residual trazado.
- `RECHAZADO`: ruptura de invariante, evidencia insuficiente o perdida de trazabilidad.

## Firma operativa

- Responsable:
- Fecha: 2026-04-01
- Comentario final: Decision `CONDICIONAL`. CSV e invariantes en verde; el proyecto queda auditable, pero los pendientes residuales impiden declararlo listo para carga.