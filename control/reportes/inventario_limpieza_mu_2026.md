# Inventario de Limpieza MU 2026

- Fecha de auditoría: 2026-04-01
- Regla aplicada: si existe duda, clasificar como `ARCHIVE`, no como `DELETE`
- Estado del proyecto preservado: `CONDICIONAL`, `27 OK / 5 Pendiente`

## Ejecución aplicada

- El material `ARCHIVE` fue movido al árbol [archive/](/Users/alexi/Documents/GitHub/avance_curricular/archive), separado del camino operativo principal.
- `resultados/` quedó reducido a los dos artefactos vigentes de la corrida oficial.
- `__pycache__/` fue eliminado como `DELETE` inequívoco.

## KEEP

| Ruta o patrón | Clasificación | Motivo | Riesgo de borrarlo | Acción recomendada |
|---|---|---|---|---|
| `codigo_gobernanza_v2.py` | `KEEP` | Pipeline oficial congelado de MU Pregrado 2026 | Alto | Mantener como ejecutable oficial |
| `qa_checks.py` | `KEEP` | Validación oficial congelada y gate final | Alto | Mantener y versionar cualquier ajuste documental |
| `requirements.txt` | `KEEP` | Reproducibilidad del entorno | Medio-Alto | Mantener sincronizado con el entorno usado |
| `Manual_Matrícula_Unificada_2026.pdf` | `KEEP` | Fuente normativa primaria del proyecto | Alto | Mantener como referencia normativa |
| `catalogo_manual.tsv`, `puente_sies.tsv`, `matriz_desambiguacion_sies_final.tsv` | `KEEP` | Insumos operativos del matching SIES | Alto | Mantener vigentes y versionados |
| `gobernanza_nac.tsv`, `gobernanza_pais_est_sec.tsv`, `gobernanza_sede.tsv`, `gobernanza_for_ing_act.tsv` | `KEEP` | Catálogos consumidos o resueltos por el flujo oficial | Alto | Mantener vigentes y versionados |
| `gobernanza_columnas_mu/` | `KEEP` | Trazabilidad probatoria por columna | Alto | Mantener completo |
| `generar_gobernanza_columnas_mu.py` | `KEEP` | Permite regenerar evidencia por columna si hay reapertura controlada | Medio | Mantener como utilitario trazable |
| `control/tablero_mu_2026.tsv`, `control/gate/gate_final_mu_2026.md`, `control/pendientes/backlog_residual_mu_2026.tsv` | `KEEP` | Núcleo probatorio del estado final | Alto | Mantener como fuente de verdad del cierre |
| `control/evidencias/` | `KEEP` | Expedientes auditable por columna | Alto | Mantener íntegro |
| `control/reportes/reporte_*.json`, `control/reportes/reporte_fase_*`, `control/reportes/resumen_ejecutivo_mu_2026.md`, `control/reportes/matriz_bloqueos_residuales_mu_2026.md`, `control/reportes/decision_operativa_mu_2026.md`, `control/reportes/ejecucion_oficial_mu_2026.md`, `control/reportes/validacion_oficial_mu_2026.md`, `control/reportes/resultado_corrida_referencia_mu_2026.md` | `KEEP` | Evidencia operativa, ejecutiva y de reproducibilidad | Alto | Mantener como paquete oficial |
| `resultados/archivo_listo_para_sies.xlsx` | `KEEP` | Artefacto oficial de auditoría de la corrida vigente | Alto | Mantener como workbook oficial |
| `resultados/matricula_unificada_2026_pregrado.csv` | `KEEP` | Artefacto regulatorio final vigente | Alto | Mantener como CSV oficial |
| `README.md`, `DOCUMENTACION_TECNICA.md`, `control/README.md` | `KEEP` | Documentación operativa que fija el uso oficial | Medio-Alto | Mantener alineada al flujo congelado |

## ARCHIVE

| Ruta o patrón | Clasificación | Motivo | Riesgo de borrarlo | Acción recomendada |
|---|---|---|---|---|
| `codigo.py` | `ARCHIVE` | Pipeline legacy con valor histórico, pero no oficial para MU 2026 | Medio | Movido a `archive/legacy_runtime/` |
| `DECISION_FOR_ING_ACT_2026-03-31.txt`, `DECISION_GOBERNANZA_COLUMNAS_MU_2026-03-31.txt` | `ARCHIVE` | Decisiones históricas ya absorbidas por `control/` | Bajo-Medio | Movidos a `archive/contexto_historico/decisiones/` |
| `FASE1_*.txt`, `FASE2_*.txt`, `FASE3_COMPLETADA.txt` | `ARCHIVE` | Bitácoras históricas de evolución | Bajo-Medio | Movidos a `archive/contexto_historico/fases/` |
| `REVIEW.md`, `reporte_eccurydp_investigacion.txt` | `ARCHIVE` | Contexto técnico/hallazgos históricos, no runtime | Bajo | Movidos a `archive/contexto_historico/tecnico/` |
| `control/fases/*.md` | `ARCHIVE` | Guías de ejecución por fase ya cerradas; útiles solo si hay reapertura controlada | Bajo-Medio | Movidas a `archive/control_historico/fases/` |
| `control/reportes/plantilla_reporte_fase.md`, `control/evidencias/_plantilla_evidencia_columna.md` | `ARCHIVE` | Plantillas reemplazadas por evidencia real, pero útiles si hay reapertura | Bajo | Movidas a `archive/control_historico/plantillas/` |
| `resultados/reporte_fech_nac.tsv`, `resultados/reporte_nac_pais_sec.tsv`, `control/reportes/sies_pendientes.tsv`, `control/reportes/resumen_historico_mu_2026.csv` | `ARCHIVE` | Reportes auxiliares valiosos para trazabilidad, no necesarios para la operación diaria | Medio | Conservar como anexos probatorios |
| `resultados/carreras_avance_curricular_2025_*.csv`, `resultados/matricula_avance_curricular_2025_*.csv`, `resultados/matricula_unificada_2026_control.csv`, `resultados/matricula_unificada_2026_oficial.xlsx`, `resultados/reporte_validacion.json`, `resultados/reporte_calidad_semantica.json`, `resultados/reporte_procedencia.csv`, `resultados/sies_ambiguedad_diagnostico.csv`, `resultados/sies_codcarr_sin_mapeo.csv` | `ARCHIVE` | Salidas legacy o de soporte de otros flujos; pueden inducir a usar el camino equivocado si se dejan como “actuales” | Medio-Alto | Movidos a `archive/resultados_legacy/` |
| `resultados/FASE3_REPORTES_TRAZABILIDAD.xlsx`, `resultados/fase2_2_comparacion_politicas.md`, `resultados/fase3_validacion_sample1000.md`, `resultados/revision_gobernanza_exhaustiva_2026-03-31.md` | `ARCHIVE` | Evidencia intermedia de remediación, ya superada por el paquete final | Bajo-Medio | Movidos a `archive/resultados_remediacion/` |
| `resultados/auditoria_manual_20260331*`, `resultados/for_ing_fix/`, `resultados/stress20/`, `resultados_audit_codigo_py/`, `resultados_audit_v2/` | `ARCHIVE` | Ensayos, auditorías y corridas de diagnóstico con valor histórico/probatorio, pero no necesarias para operar el flujo congelado | Medio | Movidos a `archive/resultados_diagnostico/` |

## DELETE

| Ruta o patrón | Clasificación | Motivo | Riesgo de borrarlo | Acción recomendada |
|---|---|---|---|---|
| `__pycache__/` | `DELETE` | Basura de ejecución local sin valor operativo ni probatorio | Bajo | Eliminado en esta etapa |

## Regla práctica posterior a este inventario

1. No borrar nada del bloque `ARCHIVE` antes de moverlo a una ubicación explícita de histórico.
2. Mantener `KEEP` en ubicación actual.
3. Ejecutar `DELETE` solo en la etapa de limpieza aprobada y documentada.
