# Reglas Manual Etapa 1 Oferta Académica 2027

Fuente: Instructivo_Oferta_Academica-Acceso_CFT-IP 2027.txt

| ID | Severidad | Categoría | Validación | Líneas | Regla |
|---|---|---|---|---|---|
| OA1-001 | BLOQUEANTE | estructura | estructura_48_columnas_sin_campos_excluidos | 523-525, 545-548 | Antes de cargar se debe eliminar código de institución, cantidad matrícula DFE y cantidad beneficio DFE; CSV sin encabezados al cargar. |
| OA1-002 | BLOQUEANTE | estructura | no_agregar_programas_y_mantener_programas_presentados | 541-548 | Solo se deben cargar programas de pregrado presentados en vigencia inicial; no agregar programas nuevos o faltantes. |
| OA1-003 | BLOQUEANTE | estructura | solo_campos_modificables_pueden_cambiar | 568-607 | La oferta vigente TP adscritas no podrá modificarse excepto en las columnas permitidas. |
| OA1-004 | BLOQUEANTE | dominio | cod_nivel_global_pregrado_y_nivel_carrera_0_4 | 1867, 1938-1941 | COD_NIVEL_GLOBAL considera valor 1: Pregrado; COD_NIVEL_CARRERA puede ser 0, 1, 2, 3 o 4. |
| OA1-005 | BLOQUEANTE | dominio | modalidad_jornada_compatibles | 1773-1779, 1872-1877 | Jornada y modalidad deben ser compatibles: diurna/vespertina no pueden ser no presencial; a distancia exige no presencial; no presencial exige a distancia. |
| OA1-006 | BLOQUEANTE | dominio | dominios_numericos_basicos | 1936-1947, 1958-1959, 1979, 2006-2010 | Campos de catálogo deben respetar valores permitidos descritos por el instructivo. |
| OA1-007 | BLOQUEANTE | areas | area_actual_y_destino_valores | 1917-1930 | AREA_ACTUAL considera valores 1 a 10; áreas de destino consideran 0 o 1. |
| OA1-008 | BLOQUEANTE | areas | reglas_area_por_nivel_carrera | 1810-1866 | Para nivel 1 el área destino debe incluir el área actual y no superar 5 áreas; para nivel 2 y 4 las áreas destino deben ser 0; nivel 3 exige Educación=1 y resto 0. |
| OA1-009 | BLOQUEANTE | plan | plan_regular_semestres_reconocidos_cero | 1868-1869 | Cuando COD_TIPO_PLAN_CARRERA es 1 Plan Regular, SEMESTRES_RECONOCIDOS debe ser 0. |
| OA1-010 | BLOQUEANTE | duraciones | duraciones_coherentes | 1721-1733, 1742-1748, 1870-1871, 1983-1990 | Duraciones deben ser coherentes: total >= estudios, estudios + titulación >= total, estudios <=14 y duraciones dentro de rango. |
| OA1-011 | BLOQUEANTE | vigencia | vigencia_1_obligatorios | 1878-1902 | Cuando VIGENCIA_CARRERA es 1 se deben completar campos obligatorios de admisión, requisitos, mail y valores. |
| OA1-012 | BLOQUEANTE | vigencia | vigencia_1_vacantes_no_cero | 1878 | Cuando la vigencia es 1, las vacantes semestrales no pueden ser 0. |
| OA1-013 | BLOQUEANTE | vigencia | vigencia_2_fecha_vacia_y_vacantes_cero | 1903-1906 | Cuando VIGENCIA_CARRERA es 2, FECHA_ADMISION_INICIAL no se debe completar y las vacantes deben ser 0. |
| OA1-014 | BLOQUEANTE | notas | notas_promedio_coherentes | 1907-1913, 1953, 2007 | Si NOTAS_ENS_MEDIA es NO, PROMEDIO_MIN_ENS_MEDIA debe ser 0; si es SI, debe completarse y estar entre 4,00 y 7,00. |
| OA1-015 | BLOQUEANTE | formato | mail_y_url_validos | 949-951, 1915 | El enlace debe ser completo; debe ingresar un mail correcto. |
| OA1-016 | BLOQUEANTE | valores | valores_monetarios_no_negativos_o_menos_uno | 1916, 1946, 1977-1978 | Arancel y valor matrícula deben ser >=0 o -1; costo titulación y certificado/diploma deben ser >=0. |
| OA1-017 | BLOQUEANTE | fechas | fecha_admision_inicial_rango | 1992-2004 | FECHA_ADMISION_INICIAL no puede ser anterior al 02/10/2025 ni posterior al 03/04/2026 o 04/04/2026 según regla extraída. |
| OA1-018 | BLOQUEANTE | anio_inicio | anio_inicio_no_posterior_2025 | 1931-1932 | ANIO_INICIO no puede ser posterior a 2025 para Oferta Académica Vigente Editada. |
| OA1-019 | BLOQUEANTE | beneficios | programas_protegidos_no_vigencia_3 | 553-567, 1735-1741 | No eliminar programas protegidos por matrícula o beneficio DFE; si no resulta posible dar de baja, usar vigencia 2. |
| OA1-020 | REVISION | estructura | campos_malla_perfil_mencionados_no_presentes_en_estructura_48 | 1895, 1897, estructura PES 20260810_34992 | El bloque de errores menciona MALLA_CURRICULAR y PERFIL_EGRESO, pero la estructura PES Etapa 1 Vigente Editada descargada tiene 48 columnas y no contiene esos campos. |
| OA1-021 | REVISION | correo_docencia | revision_naranjo_rap_vacantes_online | Nota gobernanza Entrega Docencia 02 | Correo de Docencia deja en naranjo carreras en actualización; RAP/vacantes online quedan pendientes de confirmación. |
