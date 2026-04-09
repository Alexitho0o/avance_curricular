# Informe auditoría trazabilidad corregida columnas 16-21 — 2320/51 — NO CARGA

## Contexto

Proceso: Avance Curricular SIES 2026.  
Subproyecto: Matrícula 5809 / columnas 16-21.  
Base auditada: expediente final 2.320 calculados / 51 pendientes / NO CARGA.

## Corrección metodológica aplicada

La auditoría anterior informó 2.224 errores de trazabilidad porque exigió a calculados base campos finos como `FUENTE_CALCULO_16_21`, `HOJA_CALCULO_16_21`, `METODO_FILTRO_CARRERA` y `CODCLI_USADOS` con el mismo nivel requerido para casos calculados con fuentes nuevas o decisiones multicarrera.

La auditoría corregida separa los tipos de trazabilidad:

- Calculados base por flujo gobernado: se validan por estado, valores 16-21, CODIGO_UNICO, CODCARR_USADO y Planes RE+CO.
- Calculados con PROMEDIOS Descargas o congelado: además requieren fuente/hoja, años hasta 2025 y registros filtrados positivos cuando el campo existe.
- Multicarrera/decisión interna técnica: requieren CODCARR, CODCLI o propuesta, método/respaldo y Planes RE+CO.
- Multicarrera confirmados: requieren confirmación Matricula_2025 con MATCH_RUT_Y_CODCLI.
- Pendientes 51: no se les exige trazabilidad de cálculo; se conserva dictamen y requerimiento.

## Resultado general

- TOTAL_5809: 2371
- CALCULADOS_NO_CARGA: 2320
- PENDIENTES_NO_CARGA: 51
- ERRORES_VALIDACION_16_21: 0
- ERRORES_TRAZABILIDAD_CORREGIDA: 0
- ERRORES_PLANES_RECO: 0
- CONFIRMACION_22_OK: 22
- CSV_CARGA_GENERADO: NO
- SIES_READY_GENERADO: NO
- FUENTES_ORIGINALES_MODIFICADAS: NO

## Planes RE+CO

La validación corregida cuenta como error solo la ausencia de CODCARR en Planes RE+CO. Diferencias textuales entre nombre 5810 y nombre asociado al CODCARR usado se reportan como observación, no como error de cálculo, porque el CODCARR usado existe en Planes RE+CO.

## Carga

No se generó archivo de carga, no se generó SIES_READY y no se modificaron valores de columnas 16-21.
