# Validación Reglas Manual Etapa 1 - Docencia 02

Prefinal: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/05_datos_trabajo/PREFINAL_ETAPA1_DOCENCIA02_48_COLUMNAS_CON_ENCABEZADO_20260814_081424_v2.csv
Reglas: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/11_gobernanza/reglas_validacion_etapa1_manual/REGLAS_MANUAL_ETAPA1_OFERTA_ACADEMICA_2027.json

## Resumen

- reglas_fuente: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/11_gobernanza/reglas_validacion_etapa1_manual/REGLAS_MANUAL_ETAPA1_OFERTA_ACADEMICA_2027.json
- prefinal: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/05_datos_trabajo/PREFINAL_ETAPA1_DOCENCIA02_48_COLUMNAS_CON_ENCABEZADO_20260814_081424_v2.csv
- precarga: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/02_precarga_pes/reporte_dinamico_5913_2026-08-12_08:22:23.csv
- total_registros: 103
- total_columnas: 48
- issues_total: 132
- por_severidad: {'BLOQUEANTE': 112, 'REVISION': 20}
- por_regla: {'OA1-008': 6, 'OA1-011': 46, 'OA1-012': 38, 'OA1-018': 22, 'OA1-020': 2, 'OA1-021': 18}
- por_campo: {'ANIO_INICIO': 22, 'FECHA_ADMISION_INICIAL': 46, 'MALLA_CURRICULAR': 1, 'PERFIL_EGRESO': 1, 'VACANTES_PRIMER_SEMESTRE': 2, 'VACANTES_PRIMER_SEMESTRE,VACANTES_SEGUNDO_SEMESTRE,VIGENCIA_CARRERA': 8, 'VACANTES_PRIMER_SEMESTRE,VIGENCIA_CARRERA': 10, 'VACANTES_SEGUNDO_SEMESTRE': 36, 'areas_destino': 6}
- carga_bloqueada: True
- reglas_catalogadas: 21

## Primeros Hallazgos

| Regla | Severidad | Fila | Carrera | Campo | Detalle |
|---|---|---|---|---|---|
| OA1-011 | BLOQUEANTE | 4 | INGENIERIA EN FINANZAS | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 4 | INGENIERIA EN FINANZAS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-018 | BLOQUEANTE | 4 | INGENIERIA EN FINANZAS | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-011 | BLOQUEANTE | 5 | INGENIERIA EN MARKETING DIGITAL | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 5 | INGENIERIA EN MARKETING DIGITAL | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-018 | BLOQUEANTE | 5 | INGENIERIA EN MARKETING DIGITAL | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-011 | BLOQUEANTE | 6 | INGENIERIA EN RECURSOS HUMANOS | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 6 | INGENIERIA EN RECURSOS HUMANOS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-018 | BLOQUEANTE | 6 | INGENIERIA EN RECURSOS HUMANOS | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-011 | BLOQUEANTE | 9 | INGENIERIA EN PREVENCION DE RIESGOS | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 9 | INGENIERIA EN PREVENCION DE RIESGOS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-018 | BLOQUEANTE | 9 | INGENIERIA EN PREVENCION DE RIESGOS | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-011 | BLOQUEANTE | 10 | INGENIERIA EN SEGURIDAD PRIVADA | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 10 | INGENIERIA EN SEGURIDAD PRIVADA | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-018 | BLOQUEANTE | 10 | INGENIERIA EN SEGURIDAD PRIVADA | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-008 | BLOQUEANTE | 25 | TECNICO EN LOGISTICA | areas_destino | TNS no puede asignar más de 5 áreas destino. |
| OA1-011 | BLOQUEANTE | 26 | AUDITORIA | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 26 | AUDITORIA | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-011 | BLOQUEANTE | 27 | INGENIERIA INDUSTRIAL | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 27 | INGENIERIA INDUSTRIAL | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-011 | BLOQUEANTE | 28 | INGENIERIA EN CIENCIA DE DATOS | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 28 | INGENIERIA EN CIENCIA DE DATOS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-011 | BLOQUEANTE | 30 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 30 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-021 | REVISION | 30 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | VACANTES_PRIMER_SEMESTRE,VACANTES_SEGUNDO_SEMESTRE,VIGENCIA_CARRERA | Fila marcada en naranjo por Docencia: requiere confirmación RAP/vacantes online. |
| OA1-011 | BLOQUEANTE | 31 | INGENIERIA EN CIBERSEGURIDAD | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 31 | INGENIERIA EN CIBERSEGURIDAD | VACANTES_SEGUNDO_SEMESTRE | No puede ser nulo cuando VIGENCIA_CARRERA=1. |
| OA1-021 | REVISION | 31 | INGENIERIA EN CIBERSEGURIDAD | VACANTES_PRIMER_SEMESTRE,VACANTES_SEGUNDO_SEMESTRE,VIGENCIA_CARRERA | Fila marcada en naranjo por Docencia: requiere confirmación RAP/vacantes online. |
| OA1-011 | BLOQUEANTE | 32 | INGENIERIA EN INFORMATICA | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 32 | INGENIERIA EN INFORMATICA | VACANTES_SEGUNDO_SEMESTRE | No puede ser nulo cuando VIGENCIA_CARRERA=1. |
| OA1-021 | REVISION | 32 | INGENIERIA EN INFORMATICA | VACANTES_PRIMER_SEMESTRE,VACANTES_SEGUNDO_SEMESTRE,VIGENCIA_CARRERA | Fila marcada en naranjo por Docencia: requiere confirmación RAP/vacantes online. |
| OA1-011 | BLOQUEANTE | 33 | INGENIERIA EN CONECTIVIDAD Y REDES | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 33 | INGENIERIA EN CONECTIVIDAD Y REDES | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-021 | REVISION | 33 | INGENIERIA EN CONECTIVIDAD Y REDES | VACANTES_PRIMER_SEMESTRE,VIGENCIA_CARRERA | Fila marcada en naranjo por Docencia: requiere confirmación RAP/vacantes online. |
| OA1-011 | BLOQUEANTE | 34 | INGENIERIA EN ADMINISTRACION DE EMPRESAS | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 34 | INGENIERIA EN ADMINISTRACION DE EMPRESAS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-021 | REVISION | 34 | INGENIERIA EN ADMINISTRACION DE EMPRESAS | VACANTES_PRIMER_SEMESTRE,VACANTES_SEGUNDO_SEMESTRE,VIGENCIA_CARRERA | Fila marcada en naranjo por Docencia: requiere confirmación RAP/vacantes online. |
| OA1-021 | REVISION | 35 | INGENIERIA EN CONECTIVIDAD Y REDES | VACANTES_PRIMER_SEMESTRE,VIGENCIA_CARRERA | Fila marcada en naranjo por Docencia: requiere confirmación RAP/vacantes online. |
| OA1-011 | BLOQUEANTE | 36 | TECNICO EN CIBERSEGURIDAD | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 36 | TECNICO EN CIBERSEGURIDAD | VACANTES_SEGUNDO_SEMESTRE | No puede ser nulo cuando VIGENCIA_CARRERA=1. |
| OA1-021 | REVISION | 36 | TECNICO EN CIBERSEGURIDAD | VACANTES_PRIMER_SEMESTRE,VACANTES_SEGUNDO_SEMESTRE,VIGENCIA_CARRERA | Fila marcada en naranjo por Docencia: requiere confirmación RAP/vacantes online. |
| OA1-011 | BLOQUEANTE | 37 | TECNICO EN ENFERMERIA | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-011 | BLOQUEANTE | 38 | INGENIERIA EN LOGISTICA | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 38 | INGENIERIA EN LOGISTICA | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-021 | REVISION | 38 | INGENIERIA EN LOGISTICA | VACANTES_PRIMER_SEMESTRE,VACANTES_SEGUNDO_SEMESTRE,VIGENCIA_CARRERA | Fila marcada en naranjo por Docencia: requiere confirmación RAP/vacantes online. |
| OA1-011 | BLOQUEANTE | 39 | TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-018 | BLOQUEANTE | 39 | TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-021 | REVISION | 40 | INGENIERIA EN INFORMATICA | VACANTES_PRIMER_SEMESTRE,VIGENCIA_CARRERA | Fila marcada en naranjo por Docencia: requiere confirmación RAP/vacantes online. |
| OA1-008 | BLOQUEANTE | 41 | TECNICO EN LOGISTICA | areas_destino | TNS no puede asignar más de 5 áreas destino. |
| OA1-011 | BLOQUEANTE | 41 | TECNICO EN LOGISTICA | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 41 | TECNICO EN LOGISTICA | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-021 | REVISION | 41 | TECNICO EN LOGISTICA | VACANTES_PRIMER_SEMESTRE,VACANTES_SEGUNDO_SEMESTRE,VIGENCIA_CARRERA | Fila marcada en naranjo por Docencia: requiere confirmación RAP/vacantes online. |
| OA1-011 | BLOQUEANTE | 42 | ADMINISTRACION PUBLICA | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-008 | BLOQUEANTE | 43 | TECNICO EN ADMINISTRACION DE EMPRESAS | areas_destino | TNS no puede asignar más de 5 áreas destino. |
| OA1-011 | BLOQUEANTE | 43 | TECNICO EN ADMINISTRACION DE EMPRESAS | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 43 | TECNICO EN ADMINISTRACION DE EMPRESAS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-021 | REVISION | 43 | TECNICO EN ADMINISTRACION DE EMPRESAS | VACANTES_PRIMER_SEMESTRE,VACANTES_SEGUNDO_SEMESTRE,VIGENCIA_CARRERA | Fila marcada en naranjo por Docencia: requiere confirmación RAP/vacantes online. |
| OA1-021 | REVISION | 44 | INGENIERIA EN CIBERSEGURIDAD | VACANTES_PRIMER_SEMESTRE,VIGENCIA_CARRERA | Fila marcada en naranjo por Docencia: requiere confirmación RAP/vacantes online. |
| OA1-011 | BLOQUEANTE | 45 | TECNICO EN ENFERMERIA | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 45 | TECNICO EN ENFERMERIA | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-011 | BLOQUEANTE | 46 | INGENIERIA INDUSTRIAL | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-018 | BLOQUEANTE | 46 | INGENIERIA INDUSTRIAL | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-011 | BLOQUEANTE | 47 | INGENIERIA EN MARKETING DIGITAL | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-018 | BLOQUEANTE | 47 | INGENIERIA EN MARKETING DIGITAL | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-011 | BLOQUEANTE | 48 | TECNICO EN MARKETING DIGITAL | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-018 | BLOQUEANTE | 48 | TECNICO EN MARKETING DIGITAL | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-011 | BLOQUEANTE | 49 | AUDITORIA | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-011 | BLOQUEANTE | 50 | CONTABILIDAD GENERAL | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-011 | BLOQUEANTE | 51 | INGENIERIA EN CIENCIA DE DATOS | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 51 | INGENIERIA EN CIENCIA DE DATOS | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-011 | BLOQUEANTE | 52 | TECNICO EN CONECTIVIDAD Y REDES | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 52 | TECNICO EN CONECTIVIDAD Y REDES | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-021 | REVISION | 52 | TECNICO EN CONECTIVIDAD Y REDES | VACANTES_PRIMER_SEMESTRE,VIGENCIA_CARRERA | Fila marcada en naranjo por Docencia: requiere confirmación RAP/vacantes online. |
| OA1-008 | BLOQUEANTE | 55 | TECNICO EN ADMINISTRACION DE EMPRESAS | areas_destino | TNS no puede asignar más de 5 áreas destino. |
| OA1-021 | REVISION | 55 | TECNICO EN ADMINISTRACION DE EMPRESAS | VACANTES_PRIMER_SEMESTRE,VIGENCIA_CARRERA | Fila marcada en naranjo por Docencia: requiere confirmación RAP/vacantes online. |
| OA1-011 | BLOQUEANTE | 56 | TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
| OA1-012 | BLOQUEANTE | 56 | TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA | VACANTES_SEGUNDO_SEMESTRE | Manual indica que vacantes semestrales no pueden ser 0 con vigencia 1. |
| OA1-018 | BLOQUEANTE | 56 | TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA | ANIO_INICIO | No puede ser posterior a 2025 para Vigente Editada. |
| OA1-021 | REVISION | 58 | INGENIERIA EN LOGISTICA | VACANTES_PRIMER_SEMESTRE,VIGENCIA_CARRERA | Fila marcada en naranjo por Docencia: requiere confirmación RAP/vacantes online. |
| OA1-011 | BLOQUEANTE | 59 | TECNICO EN CIENCIA DE DATOS | FECHA_ADMISION_INICIAL | Campo obligatorio cuando VIGENCIA_CARRERA=1. |
