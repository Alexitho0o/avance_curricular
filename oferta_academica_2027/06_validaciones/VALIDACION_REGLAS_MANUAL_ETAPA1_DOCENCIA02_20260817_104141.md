# Validación Reglas Manual Etapa 1 - Docencia 02

Prefinal: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/05_datos_trabajo/20260815_Etapa_1_excel_kmg_hoja_validacion.csv
Reglas: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/11_gobernanza/reglas_validacion_etapa1_manual/REGLAS_MANUAL_ETAPA1_OFERTA_ACADEMICA_2027.json

## Resumen

- reglas_fuente: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/11_gobernanza/reglas_validacion_etapa1_manual/REGLAS_MANUAL_ETAPA1_OFERTA_ACADEMICA_2027.json
- prefinal: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/05_datos_trabajo/20260815_Etapa_1_excel_kmg_hoja_validacion.csv
- precarga: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/02_precarga_pes/reporte_dinamico_5913_2026-08-12_08:22:23.csv
- total_registros: 103
- total_columnas: 50
- issues_total: 337
- por_severidad: {'BLOQUEANTE': 317, 'REVISION': 20}
- por_regla: {'OA1-001': 5, 'OA1-002': 103, 'OA1-008': 6, 'OA1-012': 34, 'OA1-014': 103, 'OA1-017': 44, 'OA1-018': 22, 'OA1-020': 2, 'OA1-021': 18}
- por_campo: {'ANIO_INICIO': 22, 'CANTIDAD_BENEFICIO_DFE': 1, 'CANTIDAD_MATRICULA_DFE': 1, 'CODIGO_IES_NUM': 1, 'FECHA_ADMISION_INICIAL': 44, 'MALLA_CURRICULAR': 1, 'NOTAS_ENS_MEDIA': 103, 'PERFIL_EGRESO': 1, 'VACANTES_PRIMER_SEMESTRE,VACANTES_SEGUNDO_SEMESTRE,VIGENCIA_CARRERA': 8, 'VACANTES_PRIMER_SEMESTRE,VIGENCIA_CARRERA': 10, 'VACANTES_SEGUNDO_SEMESTRE': 34, 'VERSION': 103, 'areas_destino': 6, 'estructura': 2}
- carga_bloqueada: True
- reglas_catalogadas: 21

## Primeros Hallazgos

| Regla | Severidad | Fila | Carrera | Campo | Detalle |
|---|---|---|---|---|---|
| OA1-001 | BLOQUEANTE | archivo |  | estructura | El prefinal tiene 50 columnas; debe tener 48. |
| OA1-001 | BLOQUEANTE | archivo |  | CANTIDAD_BENEFICIO_DFE | Columna prohibida presente en archivo de carga Etapa 1. |
| OA1-001 | BLOQUEANTE | archivo |  | CANTIDAD_MATRICULA_DFE | Columna prohibida presente en archivo de carga Etapa 1. |
| OA1-001 | BLOQUEANTE | archivo |  | CODIGO_IES_NUM | Columna prohibida presente en archivo de carga Etapa 1. |
| OA1-001 | BLOQUEANTE | archivo |  | estructura | El orden de columnas no coincide con la precarga sin las 3 columnas excluidas. |
| OA1-002 | BLOQUEANTE | 2 | TECNICO EN PREVENCION DE RIESGOS | VERSION | No coincide con precarga: '1'. |
| OA1-014 | BLOQUEANTE | 2 | TECNICO EN PREVENCION DE RIESGOS | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 3 | TECNICO EN PREVENCION DE RIESGOS | VERSION | No coincide con precarga: '1'. |
| OA1-014 | BLOQUEANTE | 3 | TECNICO EN PREVENCION DE RIESGOS | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 4 | INGENIERIA EN FINANZAS | VERSION | No coincide con precarga: '2'. |
| OA1-012 | BLOQUEANTE | 4 | INGENIERIA EN FINANZAS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-014 | BLOQUEANTE | 4 | INGENIERIA EN FINANZAS | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-017 | BLOQUEANTE | 4 | INGENIERIA EN FINANZAS | FECHA_ADMISION_INICIAL | Formato de fecha no reconocido; usar dd/mm/aaaa o aaaa-mm-dd. |
| OA1-018 | BLOQUEANTE | 4 | INGENIERIA EN FINANZAS | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-002 | BLOQUEANTE | 5 | INGENIERIA EN MARKETING DIGITAL | VERSION | No coincide con precarga: '2'. |
| OA1-012 | BLOQUEANTE | 5 | INGENIERIA EN MARKETING DIGITAL | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-014 | BLOQUEANTE | 5 | INGENIERIA EN MARKETING DIGITAL | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-017 | BLOQUEANTE | 5 | INGENIERIA EN MARKETING DIGITAL | FECHA_ADMISION_INICIAL | Formato de fecha no reconocido; usar dd/mm/aaaa o aaaa-mm-dd. |
| OA1-018 | BLOQUEANTE | 5 | INGENIERIA EN MARKETING DIGITAL | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-002 | BLOQUEANTE | 6 | INGENIERIA EN RECURSOS HUMANOS | VERSION | No coincide con precarga: '2'. |
| OA1-012 | BLOQUEANTE | 6 | INGENIERIA EN RECURSOS HUMANOS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-014 | BLOQUEANTE | 6 | INGENIERIA EN RECURSOS HUMANOS | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-017 | BLOQUEANTE | 6 | INGENIERIA EN RECURSOS HUMANOS | FECHA_ADMISION_INICIAL | Formato de fecha no reconocido; usar dd/mm/aaaa o aaaa-mm-dd. |
| OA1-018 | BLOQUEANTE | 6 | INGENIERIA EN RECURSOS HUMANOS | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-002 | BLOQUEANTE | 7 | TECNICO EN AUTOMATIZACION Y CONTROL INDUSTRIAL | VERSION | No coincide con precarga: '1'. |
| OA1-014 | BLOQUEANTE | 7 | TECNICO EN AUTOMATIZACION Y CONTROL INDUSTRIAL | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 8 | TECNICO EN AUTOMATIZACION Y CONTROL INDUSTRIAL | VERSION | No coincide con precarga: '1'. |
| OA1-014 | BLOQUEANTE | 8 | TECNICO EN AUTOMATIZACION Y CONTROL INDUSTRIAL | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 9 | INGENIERIA EN PREVENCION DE RIESGOS | VERSION | No coincide con precarga: '2'. |
| OA1-012 | BLOQUEANTE | 9 | INGENIERIA EN PREVENCION DE RIESGOS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-014 | BLOQUEANTE | 9 | INGENIERIA EN PREVENCION DE RIESGOS | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-017 | BLOQUEANTE | 9 | INGENIERIA EN PREVENCION DE RIESGOS | FECHA_ADMISION_INICIAL | Formato de fecha no reconocido; usar dd/mm/aaaa o aaaa-mm-dd. |
| OA1-018 | BLOQUEANTE | 9 | INGENIERIA EN PREVENCION DE RIESGOS | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-002 | BLOQUEANTE | 10 | INGENIERIA EN SEGURIDAD PRIVADA | VERSION | No coincide con precarga: '2'. |
| OA1-012 | BLOQUEANTE | 10 | INGENIERIA EN SEGURIDAD PRIVADA | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-014 | BLOQUEANTE | 10 | INGENIERIA EN SEGURIDAD PRIVADA | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-017 | BLOQUEANTE | 10 | INGENIERIA EN SEGURIDAD PRIVADA | FECHA_ADMISION_INICIAL | Formato de fecha no reconocido; usar dd/mm/aaaa o aaaa-mm-dd. |
| OA1-018 | BLOQUEANTE | 10 | INGENIERIA EN SEGURIDAD PRIVADA | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-002 | BLOQUEANTE | 11 | INGENIERIA EN INFORMATICA | VERSION | No coincide con precarga: '1'. |
| OA1-014 | BLOQUEANTE | 11 | INGENIERIA EN INFORMATICA | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 12 | INGENIERIA EN INFORMATICA | VERSION | No coincide con precarga: '2'. |
| OA1-014 | BLOQUEANTE | 12 | INGENIERIA EN INFORMATICA | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 13 | INGENIERIA EN AUTOMATIZACION Y CONTROL INDUSTRIAL | VERSION | No coincide con precarga: '1'. |
| OA1-014 | BLOQUEANTE | 13 | INGENIERIA EN AUTOMATIZACION Y CONTROL INDUSTRIAL | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 14 | INGENIERIA EN AUTOMATIZACION Y CONTROL INDUSTRIAL | VERSION | No coincide con precarga: '1'. |
| OA1-014 | BLOQUEANTE | 14 | INGENIERIA EN AUTOMATIZACION Y CONTROL INDUSTRIAL | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 15 | TECNICO EN PROGRAMACION COMPUTACIONAL | VERSION | No coincide con precarga: '1'. |
| OA1-014 | BLOQUEANTE | 15 | TECNICO EN PROGRAMACION COMPUTACIONAL | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 16 | TECNICO EN PROGRAMACION COMPUTACIONAL | VERSION | No coincide con precarga: '1'. |
| OA1-014 | BLOQUEANTE | 16 | TECNICO EN PROGRAMACION COMPUTACIONAL | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 17 | TECNICO EN PROGRAMACION COMPUTACIONAL | VERSION | No coincide con precarga: '1'. |
| OA1-014 | BLOQUEANTE | 17 | TECNICO EN PROGRAMACION COMPUTACIONAL | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 18 | TECNICO EN ANALISIS DE SISTEMAS | VERSION | No coincide con precarga: '1'. |
| OA1-014 | BLOQUEANTE | 18 | TECNICO EN ANALISIS DE SISTEMAS | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 19 | TECNICO EN ANALISIS DE SISTEMAS | VERSION | No coincide con precarga: '1'. |
| OA1-014 | BLOQUEANTE | 19 | TECNICO EN ANALISIS DE SISTEMAS | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 20 | TECNICO EN ANALISIS DE SISTEMAS | VERSION | No coincide con precarga: '1'. |
| OA1-014 | BLOQUEANTE | 20 | TECNICO EN ANALISIS DE SISTEMAS | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 21 | INGENIERIA EN CONECTIVIDAD Y REDES | VERSION | No coincide con precarga: '1'. |
| OA1-014 | BLOQUEANTE | 21 | INGENIERIA EN CONECTIVIDAD Y REDES | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 22 | TECNICO EN CONTROL INDUSTRIAL | VERSION | No coincide con precarga: '1'. |
| OA1-014 | BLOQUEANTE | 22 | TECNICO EN CONTROL INDUSTRIAL | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 23 | TECNICO EN CONECTIVIDAD Y REDES | VERSION | No coincide con precarga: '1'. |
| OA1-014 | BLOQUEANTE | 23 | TECNICO EN CONECTIVIDAD Y REDES | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 24 | INGENIERIA EN LOGISTICA | VERSION | No coincide con precarga: '1'. |
| OA1-014 | BLOQUEANTE | 24 | INGENIERIA EN LOGISTICA | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 25 | TECNICO EN LOGISTICA | VERSION | No coincide con precarga: '1'. |
| OA1-008 | BLOQUEANTE | 25 | TECNICO EN LOGISTICA | areas_destino | TNS no puede asignar más de 5 áreas destino. |
| OA1-014 | BLOQUEANTE | 25 | TECNICO EN LOGISTICA | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-002 | BLOQUEANTE | 26 | AUDITORIA | VERSION | No coincide con precarga: '2'. |
| OA1-012 | BLOQUEANTE | 26 | AUDITORIA | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-014 | BLOQUEANTE | 26 | AUDITORIA | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-017 | BLOQUEANTE | 26 | AUDITORIA | FECHA_ADMISION_INICIAL | Formato de fecha no reconocido; usar dd/mm/aaaa o aaaa-mm-dd. |
| OA1-002 | BLOQUEANTE | 27 | INGENIERIA INDUSTRIAL | VERSION | No coincide con precarga: '1'. |
| OA1-012 | BLOQUEANTE | 27 | INGENIERIA INDUSTRIAL | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-014 | BLOQUEANTE | 27 | INGENIERIA INDUSTRIAL | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
| OA1-017 | BLOQUEANTE | 27 | INGENIERIA INDUSTRIAL | FECHA_ADMISION_INICIAL | Formato de fecha no reconocido; usar dd/mm/aaaa o aaaa-mm-dd. |
| OA1-002 | BLOQUEANTE | 28 | INGENIERIA EN CIENCIA DE DATOS | VERSION | No coincide con precarga: '2'. |
| OA1-012 | BLOQUEANTE | 28 | INGENIERIA EN CIENCIA DE DATOS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-014 | BLOQUEANTE | 28 | INGENIERIA EN CIENCIA DE DATOS | NOTAS_ENS_MEDIA | Debe ser 1/SI o 2/NO. |
