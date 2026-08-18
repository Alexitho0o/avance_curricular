# Reporte de pendientes - Etapa 2 Oferta Academica Nueva TP Adscritas (20260827)

Estado: **NO CARGAR A SIES**

Este directorio contiene el reporte de pendientes generado tras la primera ejecucion del
proceso de ingesta, gobernanza, perfilamiento, conciliacion y validacion del archivo
institucional "Oferta 2027 Etapa2_prueba_1.xlsx" (propuesta preliminar, NO archivo definitivo).

## Contenido

- REPORTE_PENDIENTES_ETAPA2_OFERTA_NUEVA_2027_20260827.xlsx: Excel de revision para Docencia
  (hojas: Resumen, Detalle de hallazgos, Registros (todos), Reglas aplicadas). Bloqueantes en rojo,
  revisiones manuales en amarillo. Conserva todos los 50 registros y sus 49 columnas originales.
- MANIFIESTO_RESULTADOS_ETAPA2_20260827.tsv: SHA-256 de todos los archivos generados en esta ejecucion.

## Fuentes de las demas salidas de esta ejecucion (no duplicadas aqui)

- Perfilamiento tecnico: ../../06_validaciones/PERFIL_ENTREGA_ETAPA2_20260827_etapa2_entrega01.*
- Contrato de columnas (Fase 3): ../../11_gobernanza/REGLAS_MANUAL_ETAPA2_OFERTA_NUEVA_2027_20260827.*
- Conciliacion vs reporte 5912 (Fase 4): ../../06_validaciones/CONCILIACION_ETAPA2_VS_REPORTE_5912_20260827.*
- Validacion completa (Fase 5): ../../06_validaciones/VALIDACION_COMPLETA_ETAPA2_20260827.*
- Copia gobernada del archivo original: ../../03_fuentes_institucionales/entregas_docencia/20260827_etapa2_entrega_01/

## Motivo de NO CARGAR

- 50 de 50 registros (100%) tienen al menos un hallazgo BLOQUEANTE.
- 18 de 50 registros coinciden EXACTAMENTE con un registro ya vigente en la Oferta Validada (reporte 5912): posible duplicado.
- Estructura oficial de Etapa 2 clasificada como FUENTE_INSTITUCIONAL_PENDIENTE_DE_CONFIRMACION_ESTRUCTURAL (no existe archivo de estructura oficial descargado independientemente de PES; el archivo tiene una columna adicional "SECTOR IPSS" ajena a la estructura documentada).
- Contradicciones internas no resueltas en el propio instructivo: tratamiento de VERSION, rango de fechas aplicable a 2027 (FECHA_ADMISION_INICIAL / ANIO_INICIO), y estatus de MALLA_CURRICULAR / PERFIL_EGRESO.

No se genera archivo prefinal (Fase 7) ni CSV final (Fase 8) en esta ejecucion.
