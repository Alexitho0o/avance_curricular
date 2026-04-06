# README Audit de Cruces MU 2026

Fecha de auditoría: 2026-04-09  
Repositorio: `avance_curricular`  
Auditor: Agente Avance Curricular (MU 2026)

## Fuentes auditadas

- `README.md`
- `cruces_proyecto.tsv`
- `codigo_gobernanza_v2.py`
- `qa_checks.py`
- `scripts/auditoria_maestra.py`

## Tabla de correspondencia README vs cruces críticos

| Item crítico | Estado | Tipo brecha | Evidencia (ruta) | Impacto | Recomendación |
|---|---|---|---|---|---|
| README declara `cruces_proyecto.tsv` como mapa de linaje auditable | OK | — | `README.md` (sección "Mapa de cruces del pipeline"), `cruces_proyecto.tsv` | Alto (trazabilidad) | Mantener como referencia obligatoria en revisiones de PR |
| Cruce SIES central (`SOURCE_KEY_3`) referenciado (L2447 en mapa) | PARCIAL | DOCUMENTACION_INCORRECTA | `README.md` (sección cruces críticos), `cruces_proyecto.tsv` L2447, `codigo_gobernanza_v2.py` L2664, L2578-L2617 | Alto (asignación SIES) | Actualizar `cruces_proyecto.tsv`: el cruce central ya consume `control/catalogos/PUENTE_SIES_COMPILADO.tsv` y no base directa `puente_sies.tsv` |
| Enriquecimiento Oferta (`L2589+` en mapa) documentado | OK | — | `README.md` (sección cruces críticos), `cruces_proyecto.tsv` L2589-L2594, `codigo_gobernanza_v2.py` L2827-L2834 | Alto (MODALIDAD/JOR/DURACION/COD_CAR) | Mantener; actualizar líneas del mapa en próxima sincronización |
| Enriquecimiento Duración (`L3138+` en mapa) documentado | OK | — | `README.md` (sección cruces críticos), `cruces_proyecto.tsv` L3138-L3152, `codigo_gobernanza_v2.py` L3453-L3480 | Alto (DURACION/NOMBRE/TITULACION/TOTAL) | Mantener; actualizar líneas del mapa en próxima sincronización |
| Cruce DatosAlumnos por CODCLI + fallback RUT + `combine_first` documentado | OK | — | `README.md` (L1716/L1735/L1747), `cruces_proyecto.tsv` L1716/L1735/L1747, `codigo_gobernanza_v2.py` L1861, L1880-L1883, L1892 | Alto (identidad y estado administrativo) | Mantener como cruce bloqueante de regresión |
| QA y auditoría (`qa_checks.py` + `scripts/auditoria_maestra.py`) documentados | OK | — | `README.md` secciones 7 y 8, `qa_checks.py` L1727+, `scripts/auditoria_maestra.py` | Alto (gate de entrega) | Mantener ejecución dual QA + Auditoría en validación oficial |
| Distinción oficial vs legacy/archivo | OK | — | `README.md` secciones 1, 5, 10 | Alto (gobernanza documental) | Mantener separación; no usar `archive/` en flujo oficial |

## Brechas detectadas (clasificación solicitada)

- `CRUCE_NO_DOCUMENTADO`: **0**
- `DOCUMENTACION_INCORRECTA`: **1**
  - `cruces_proyecto.tsv` describe el cruce central SIES como puente base `puente_sies.tsv`; el código actual ya consume catálogo compilado canónico (`control/catalogos/PUENTE_SIES_COMPILADO.tsv`).
- `DOCUMENTACION_LEGACY`: **0** (README distingue explícitamente `archive/` y backups como no oficiales)

## Verificación de preservación de cruces críticos tras cambios

Resultado: **PASS**

Cruces verificados en código actual:

- SIES central por `SOURCE_KEY_3`: `codigo_gobernanza_v2.py` L2664.
- Bloqueo nuevas combinaciones SIES no catalogadas: `codigo_gobernanza_v2.py` L2712-L2727.
- DatosAlumnos CODCLI: `codigo_gobernanza_v2.py` L1861.
- DatosAlumnos fallback RUT: `codigo_gobernanza_v2.py` L1880-L1883.
- DatosAlumnos cascada `combine_first`: `codigo_gobernanza_v2.py` L1892.
- Oferta por `CODIGO_UNICO`: `codigo_gobernanza_v2.py` L2827-L2834.
- Duración por `CODIGO_UNICO` + fallback `COD_CAR`: `codigo_gobernanza_v2.py` L3466-L3480.

## Evidencia de consolidación catálogo SIES (un solo lugar)

- Catálogo canónico compilado: `control/catalogos/PUENTE_SIES_COMPILADO.tsv`.
- Script compilador: `scripts/compile_puente_sies_compilado.py`.
- Resumen de compilación: `control/reportes/reporte_compilacion_puente_sies.json`.

Resumen actual compilado:

- `total_source_keys`: 157
- `source_keys_unicos`: 87
- `source_keys_ambiguos`: 70
- `cobertura_llaves_unicas_pct`: 55.41

Control de unicidad ejecutado:

- `SOURCE_KEY_3` duplicadas en compilado: 0 (PASS).

Cobertura operacional observada en último `resultados/archivo_listo_para_sies.xlsx`:

- `% llaves resueltas (compilado)`: `55.41%` (87 de 157).
- `# ambiguas (compilado)`: `70`.
- `# nuevas bloqueantes (run vigente, no diplomado SIN_MATCH_SIES)`: `1`.

## QA ejecutado (evidencia)

1. `OUTPUT_DIR=resultados bash scripts/validate_oficial.sh`  
   Resultado: validación oficial completa (QA + Auditoría) exitosa.
2. `python3 qa_checks.py --output-dir resultados --fase6-control-dir control`  
   Resultado: `qa_checks_ok`.
3. `python3 scripts/auditoria_maestra.py --solo-validar --output-dir resultados`  
   Resultado: `DICTAMEN: LISTO PARA ENTREGA`.
4. `INPUT_XLSX=/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx OUTPUT_DIR=resultados/run_oficial_compilado_2026-04-09 bash scripts/run_oficial.sh`  
   Resultado: **FAIL bloqueante esperado** por `SIN_MATCH_SIES` no diplomado (1 combinación nueva), con evidencia en `resultados/run_oficial_compilado_2026-04-09/sies_combinaciones_nuevas_bloqueantes.tsv`.

## Dictamen final

El `README.md` queda **alineado operativamente** con los cruces críticos y la gobernanza MU 2026, incorporando explícitamente el mapa `cruces_proyecto.tsv` y el catálogo SIES compilado canónico.  

Pendiente de sincronización documental menor: actualizar `cruces_proyecto.tsv` para reflejar la nueva fuente canónica del cruce central SIES y refrescar números de línea tras refactor.  

Estado operativo posterior al endurecimiento: la corrida oficial con input congelado queda correctamente **bloqueada** hasta catalogar la combinación `V|CICRE|CONTINUIDAD INGENIERIA CONECTIVIDAD Y REDES`.
