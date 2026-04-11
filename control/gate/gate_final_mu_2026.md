# Gate Final MU 2026

- Fecha: 2026-04-23
- Responsable:
- Decision final: `CONDICIONAL`
- Listo para auditoria: `SI`
- Listo para carga: `NO`
- No listo para carga: `SI`

## Resumen del tablero

- Columnas en `OK` (29): `B N_DOC`, `C DV`, `D PRIMER_APELLIDO`, `E SEGUNDO_APELLIDO`, `F NOMBRE`, `G SEXO`, `H FECH_NAC`, `I NAC`, `J PAIS_EST_SEC`, `K COD_SED`, `L COD_CAR`, `M MODALIDAD`, `N JOR`, `O VERSION`, `P FOR_ING_ACT`, `Q ANIO_ING_ACT`, `R SEM_ING_ACT`, `S ANIO_ING_ORI`, `T SEM_ING_ORI`, `U ASI_INS_ANT`, `V ASI_APR_ANT`, `W PROM_PRI_SEM`, `X PROM_SEG_SEM`, `AA NIV_ACA`, `AB SIT_FON_SOL`, `AC SUS_PRE`, `AD FECHA_MATRICULA`, `AE REINCORPORACION`, `AF VIG`
- Columnas en `Pendiente` (3): `A TIPO_DOC`, `Y ASI_INS_HIS`, `Z ASI_APR_HIS`
- Conteo final: `29 OK / 3 Pendiente`

## Validacion de invariantes

| Invariante | Resultado | Evidencia | Observacion |
|---|---|---|---|
| CSV final sin header | SI | resultados/matricula_unificada_2026_pregrado.csv | Filas finales: 3433 |
| 32 columnas exactas | SI | resultados/matricula_unificada_2026_pregrado.csv | Columnas observadas: 32 |
| Separador `;` | SI | resultados/matricula_unificada_2026_pregrado.csv | Delimitacion contractual vigente |
| `SEXO` valido | SI | resultados/matricula_unificada_2026_pregrado.csv | Distribucion observada: {'H': 2051, 'M': 1380, 'NB': 2} |
| `FOR_ING_ACT` en catálogo `1..11` | SI | resultados/matricula_unificada_2026_pregrado.csv | Distribucion observada: {'1': 2926, '2': 383, '3': 84, '11': 32, '6': 8} |
| Anexo 7 continuidad (`FOR` en `{2,3,4,5,11}` ⇒ ORI != ACT) | SI | resultados/matricula_unificada_2026_pregrado.csv | Filas continuidad evaluadas: 499 |
| Exclusion de `PRIMERA_OPCION` | SI | resultados/archivo_listo_para_sies.xlsx | Filas incluidas con heuristica opaca: 0 |

## Estado por fase

| Fase | Resultado | Riesgo residual | Reporte asociado |
|---|---|---|---|
| FASE 0 | OK | Sin bloqueo residual. | control/evidencias/D_primer_apellido.md + control/evidencias/F_nombre.md + control/evidencias/G_sexo.md + control/evidencias/P_for_ing_act.md |
| FASE 1 | CONDICIONAL | A TIPO_DOC: Anomalía documental activa: 4 filas incluidas presentan `TIPO_DOC=R` con `FOR_ING_ACT=6`, `Q/S=2026` y `VIG=1`; el Cuadro N°5 solo muestra ese patrón de nuevo ingreso extranjero con `TIPO_DOC=P`. | control/reportes/reporte_identidad_mu_2026.json |
| FASE 2 | OK | Sin bloqueo residual. | control/reportes/reporte_sies_oferta_mu_2026.json |
| FASE 3 | OK | Sin bloqueo residual. | control/reportes/reporte_cronologia_mu_2026.json + control/reportes/reporte_niv_fecha_mu_2026.json |
| FASE 4 | CONDICIONAL | Y ASI_INS_HIS: Cobertura historica no plenamente alineada al manual: 2351 filas incluidas quedaron con `ALCANCE_LIMITADO_ANIO_UNICO`, pero `Y ASI_INS_HIS` exige acumulado desde el inicio de la carrera.; Z ASI_APR_HIS: Cobertura historica no plenamente alineada al manual: 2351 filas incluidas quedaron con `ALCANCE_LIMITADO_ANIO_UNICO`, pero `Z ASI_APR_HIS` exige acumulado desde el inicio de la carrera. | control/reportes/reporte_rendimiento_mu_2026.json |
| FASE 5 | OK | Sin bloqueo residual. | control/reportes/reporte_estado_admin_mu_2026.json |

## Bloqueos residuales abiertos

| Bloqueo ID | Campo(s) | Impacto | Mitigacion | Estado |
|---|---|---|---|---|
| BLK-A | A `TIPO_DOC` | Alto | Revisar en fuente de identidad/documento si corresponde `P` o si `FOR_ING_ACT=6` fue asignado indebidamente; no corregir por sobreescritura automática sin respaldo. | Abierto |
| BLK-Y | Y `ASI_INS_HIS` | Alto | Incorporar fuente historica multianual o acto regulatorio explicito que permita usar alcance monoanual. | Abierto |
| BLK-Z | Z `ASI_APR_HIS` | Alto | Incorporar fuente historica multianual o acto regulatorio explicito que permita usar alcance monoanual. | Abierto |

## Condiciones de aprobacion

- `APROBADO`: invariantes conformes, evidencia completa y sin bloqueo critico abierto.
- `CONDICIONAL`: invariantes conformes, evidencia suficiente y backlog residual trazado.
- `RECHAZADO`: ruptura de invariante, evidencia insuficiente o perdida de trazabilidad.

## Firma operativa

- Responsable:
- Fecha: 2026-04-23
- Comentario final: Decision `CONDICIONAL`. CSV e invariantes en verde; el proyecto queda auditable, pero los pendientes residuales impiden declararlo listo para carga.