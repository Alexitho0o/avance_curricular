# Validación Reglas Manual Etapa 1 - Docencia 02

Prefinal: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/05_datos_trabajo/PREFINAL_ETAPA1_DOCENCIA02_48_COLUMNAS_CON_ENCABEZADO_20260817_110000.csv
Reglas: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/11_gobernanza/reglas_validacion_etapa1_manual/REGLAS_MANUAL_ETAPA1_OFERTA_ACADEMICA_2027.json

## Resumen

- reglas_fuente: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/11_gobernanza/reglas_validacion_etapa1_manual/REGLAS_MANUAL_ETAPA1_OFERTA_ACADEMICA_2027.json
- prefinal: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/05_datos_trabajo/PREFINAL_ETAPA1_DOCENCIA02_48_COLUMNAS_CON_ENCABEZADO_20260817_110000.csv
- precarga: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/02_precarga_pes/reporte_dinamico_5913_2026-08-12_08:22:23.csv
- total_registros: 103
- total_columnas: 48
- issues_total: 108
- por_severidad: {'BLOQUEANTE': 106, 'REVISION': 2}
- por_regla: {'OA1-008': 6, 'OA1-012': 34, 'OA1-017': 44, 'OA1-018': 22, 'OA1-020': 2}
- por_campo: {'ANIO_INICIO': 22, 'FECHA_ADMISION_INICIAL': 44, 'MALLA_CURRICULAR': 1, 'PERFIL_EGRESO': 1, 'VACANTES_SEGUNDO_SEMESTRE': 34, 'areas_destino': 6}
- carga_bloqueada: True
- reglas_catalogadas: 21

## Primeros Hallazgos

| Regla | Severidad | Fila | Carrera | Campo | Detalle |
|---|---|---|---|---|---|
| OA1-012 | BLOQUEANTE | 4 | INGENIERIA EN FINANZAS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 4 | INGENIERIA EN FINANZAS | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-018 | BLOQUEANTE | 4 | INGENIERIA EN FINANZAS | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-012 | BLOQUEANTE | 5 | INGENIERIA EN MARKETING DIGITAL | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 5 | INGENIERIA EN MARKETING DIGITAL | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-018 | BLOQUEANTE | 5 | INGENIERIA EN MARKETING DIGITAL | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-012 | BLOQUEANTE | 6 | INGENIERIA EN RECURSOS HUMANOS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 6 | INGENIERIA EN RECURSOS HUMANOS | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-018 | BLOQUEANTE | 6 | INGENIERIA EN RECURSOS HUMANOS | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-012 | BLOQUEANTE | 9 | INGENIERIA EN PREVENCION DE RIESGOS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 9 | INGENIERIA EN PREVENCION DE RIESGOS | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-018 | BLOQUEANTE | 9 | INGENIERIA EN PREVENCION DE RIESGOS | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-012 | BLOQUEANTE | 10 | INGENIERIA EN SEGURIDAD PRIVADA | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 10 | INGENIERIA EN SEGURIDAD PRIVADA | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-018 | BLOQUEANTE | 10 | INGENIERIA EN SEGURIDAD PRIVADA | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-008 | BLOQUEANTE | 25 | TECNICO EN LOGISTICA | areas_destino | TNS no puede asignar más de 5 áreas destino. |
| OA1-012 | BLOQUEANTE | 26 | AUDITORIA | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 26 | AUDITORIA | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-012 | BLOQUEANTE | 27 | INGENIERIA INDUSTRIAL | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 27 | INGENIERIA INDUSTRIAL | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-012 | BLOQUEANTE | 28 | INGENIERIA EN CIENCIA DE DATOS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 28 | INGENIERIA EN CIENCIA DE DATOS | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-012 | BLOQUEANTE | 30 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 30 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-012 | BLOQUEANTE | 31 | INGENIERIA EN CIBERSEGURIDAD | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 31 | INGENIERIA EN CIBERSEGURIDAD | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-012 | BLOQUEANTE | 32 | INGENIERIA EN INFORMATICA | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 32 | INGENIERIA EN INFORMATICA | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-012 | BLOQUEANTE | 33 | INGENIERIA EN CONECTIVIDAD Y REDES | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 33 | INGENIERIA EN CONECTIVIDAD Y REDES | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-012 | BLOQUEANTE | 34 | INGENIERIA EN ADMINISTRACION DE EMPRESAS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 34 | INGENIERIA EN ADMINISTRACION DE EMPRESAS | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-012 | BLOQUEANTE | 36 | TECNICO EN CIBERSEGURIDAD | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 36 | TECNICO EN CIBERSEGURIDAD | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-017 | BLOQUEANTE | 37 | TECNICO EN ENFERMERIA | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-012 | BLOQUEANTE | 38 | INGENIERIA EN LOGISTICA | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 38 | INGENIERIA EN LOGISTICA | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-017 | BLOQUEANTE | 39 | TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-018 | BLOQUEANTE | 39 | TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-008 | BLOQUEANTE | 41 | TECNICO EN LOGISTICA | areas_destino | TNS no puede asignar más de 5 áreas destino. |
| OA1-012 | BLOQUEANTE | 41 | TECNICO EN LOGISTICA | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 41 | TECNICO EN LOGISTICA | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-017 | BLOQUEANTE | 42 | ADMINISTRACION PUBLICA | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-008 | BLOQUEANTE | 43 | TECNICO EN ADMINISTRACION DE EMPRESAS | areas_destino | TNS no puede asignar más de 5 áreas destino. |
| OA1-012 | BLOQUEANTE | 43 | TECNICO EN ADMINISTRACION DE EMPRESAS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 43 | TECNICO EN ADMINISTRACION DE EMPRESAS | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-012 | BLOQUEANTE | 45 | TECNICO EN ENFERMERIA | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 45 | TECNICO EN ENFERMERIA | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-017 | BLOQUEANTE | 46 | INGENIERIA INDUSTRIAL | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-018 | BLOQUEANTE | 46 | INGENIERIA INDUSTRIAL | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-017 | BLOQUEANTE | 47 | INGENIERIA EN MARKETING DIGITAL | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-018 | BLOQUEANTE | 47 | INGENIERIA EN MARKETING DIGITAL | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-017 | BLOQUEANTE | 48 | TECNICO EN MARKETING DIGITAL | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-018 | BLOQUEANTE | 48 | TECNICO EN MARKETING DIGITAL | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-017 | BLOQUEANTE | 49 | AUDITORIA | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-017 | BLOQUEANTE | 50 | CONTABILIDAD GENERAL | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-012 | BLOQUEANTE | 51 | INGENIERIA EN CIENCIA DE DATOS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 51 | INGENIERIA EN CIENCIA DE DATOS | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-012 | BLOQUEANTE | 52 | TECNICO EN CONECTIVIDAD Y REDES | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 52 | TECNICO EN CONECTIVIDAD Y REDES | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-008 | BLOQUEANTE | 55 | TECNICO EN ADMINISTRACION DE EMPRESAS | areas_destino | TNS no puede asignar más de 5 áreas destino. |
| OA1-012 | BLOQUEANTE | 56 | TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 56 | TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-018 | BLOQUEANTE | 56 | TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-012 | BLOQUEANTE | 59 | TECNICO EN CIENCIA DE DATOS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 59 | TECNICO EN CIENCIA DE DATOS | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-017 | BLOQUEANTE | 61 | INGENIERIA EN RECURSOS HUMANOS | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-018 | BLOQUEANTE | 61 | INGENIERIA EN RECURSOS HUMANOS | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-012 | BLOQUEANTE | 63 | INGENIERIA EN FINANZAS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 63 | INGENIERIA EN FINANZAS | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-018 | BLOQUEANTE | 63 | INGENIERIA EN FINANZAS | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-012 | BLOQUEANTE | 64 | TECNICO EN ADMINISTRACION PUBLICA | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 64 | TECNICO EN ADMINISTRACION PUBLICA | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-017 | BLOQUEANTE | 65 | TECNICO EN RECURSOS HUMANOS | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-018 | BLOQUEANTE | 65 | TECNICO EN RECURSOS HUMANOS | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-012 | BLOQUEANTE | 67 | TECNICO EN FARMACIA | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 67 | TECNICO EN FARMACIA | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
| OA1-018 | BLOQUEANTE | 67 | TECNICO EN FARMACIA | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-012 | BLOQUEANTE | 68 | INGENIERIA EN PREVENCION DE RIESGOS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-017 | BLOQUEANTE | 68 | INGENIERIA EN PREVENCION DE RIESGOS | FECHA_ADMISION_INICIAL | Fuera de rango manual 02/10/2025 a 04/04/2026. |
