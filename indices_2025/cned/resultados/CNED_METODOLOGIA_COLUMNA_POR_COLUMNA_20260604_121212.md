# CNED / ÍNDICES - Metodología Columna Por Columna 20260604_121212

## Dictamen

**DICTAMEN_FINAL: METODOLOGIA_DETECTA_CAMPOS_AUTOCOMPLETABLES_PENDIENTES**

Esta ejecución no generó Excel operativo final, no escribió en Escritorio y no creó CSV sin encabezados. La salida es exclusivamente metodológica y de auditoría.

## Archivos Leídos

- excel_operativo: `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO_LIMPIO_CON_DICCIONARIO_RECONCILIADO.xlsx`
  - SHA256 antes: `5b3989d80aeef13798f9369eccd28767257b72f92317b6bac9b2f73e02d1e172`
  - SHA256 después: `5b3989d80aeef13798f9369eccd28767257b72f92317b6bac9b2f73e02d1e172`
  - Intacto: `SI`
- promedios_matriz: `/Users/alexi/Documents/GitHub/avance_curricular/input/PROMEDIOSDEALUMNOS_7804.xlsx`
  - SHA256 antes: `3013fed700f871f93379bc93ebf974910f30c7c4320d40bd3d8b8638fad6a5fb`
  - SHA256 después: `3013fed700f871f93379bc93ebf974910f30c7c4320d40bd3d8b8638fad6a5fb`
  - Intacto: `SI`
- diccionario_complementado_tsv: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS_COMPLEMENTADO_20260604_110722.tsv`
  - SHA256 antes: `6f37fb1b393092fd0db6e3659ff6c2f663e677ffe435f719ce088f03c6152c0e`
  - SHA256 después: `6f37fb1b393092fd0db6e3659ff6c2f663e677ffe435f719ce088f03c6152c0e`
  - Intacto: `SI`
- referencia_indices: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/data/listado_referencia_cned.tsv`
  - SHA256 antes: `ed6a947de6650842eb739e85f5c1be8d77c1d591fe256990abd8cacfddffcde0`
  - SHA256 después: `ed6a947de6650842eb739e85f5c1be8d77c1d591fe256990abd8cacfddffcde0`
  - Intacto: `SI`
- metodologia_match_previa: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_MATCH_OFERTA_20260604_115408.xlsx`
  - SHA256 antes: `dbc001b45b6ab23d8ab7b40b71fbef8d77a357e158ba896211c033c060adaffe`
  - SHA256 después: `dbc001b45b6ab23d8ab7b40b71fbef8d77a357e158ba896211c033c060adaffe`
  - Intacto: `SI`

## Validación Inicial

- Excel operativo OOXML válido: `True`
- Fórmulas: `False` (0)
- Macros: `False`
- Vínculos externos: `False`
- Conexiones: `False`
- Dibujos: `False`
- Gráficos: `False`
- Validaciones de datos: `False`
- Hojas requeridas presentes: `True`
- Control 79: `79`

## Conteos

- PROGRAMAS_FALTANTES_PARA_CREAR: `71`
- NO_CREAR_CUBIERTO: `2`
- REQUIERE_DECISION_INSTITUCIONAL: `2`
- DUDOSOS_REV_MANUAL_RESUELTOS: `4`
- DUDOSOS_REV_MANUAL_ACTUALIZADO: `0`
- Total control: `79`
- Columnas auditadas en PROGRAMAS_FALTANTES_PARA_CREAR: `87`
- Celdas auditadas: `6177`

## Match Metodológico

- MATCH_R1_CODIGO_UNICO_DERIVADO: `69`
- MATCH_R3_ESTRUCTURAL_FUERTE: `1`
- MATCH_R4_AUXILIAR_AMBIGUO: `1`
- Ambiguos: `1` (I162S2C3J2V2)
- Sin match absoluto: `0`

## Completitud Por Celdas

- COMPLETAR: `143`
- CONFLICTO_REVISAR: `9`
- DEJAR_REVISAR: `2300`
- MANTENER: `3650`
- REEMPLAZAR: `75`
- Celdas con completitud pendiente detectada: `143`

## Columnas

- 100% autocompletables o mantenibles: `25`
- Parcialmente autocompletables: `33`
- No autocompletables con bases actuales: `29`

### Columnas 100% autocompletables o mantenibles

- `CODIGO_UNICO`
- `CODIGO_IES_NUM`
- `COD_SEDE`
- `COD_CARRERA_DERIVADO`
- `JORNADA`
- `VERSION_DERIVADA`
- `NOMBRE_CARRERA_ORIGINAL`
- `NOMBRE_CARRERA_NORMALIZADO`
- `MODALIDAD_ORIGINAL`
- `TIPO_PLAN_CARRERA_ORIGINAL`
- `CARACT_PLAN_ESPECIAL_ORIGINAL`
- `NIVEL_GLOBAL`
- `NIVEL_CARRERA`
- `VIGENCIA`
- `ESTADO_CRUCE_INDICES`
- `MOTIVO_ESTADO_CRUCE`
- `FUENTE`
- `REVISADO_MANUALMENTE`
- `OBSERVACION_AUDITORIA`
- `Observaciones`
- `MATCH_STATUS`
- `MATCH_METHOD`
- `MATCH_KEY`
- `MATCH_COUNT`
- `_NOMBRE_NORM`

### Columnas parcialmente autocompletables

- `Sede`
- `Tipo de Carrera`
- `Nombre`
- `Año de inicio de Actividades`
- `Campus`
- `Horario`
- `Estado`
- `Tipo Programa`
- `Detalle del Tipo de Programa (especiales)`
- `Modalidad del Programa`
- `Título que otorga el programa`
- `Duración del programa en Semestres`
- `ANIO_INICIO`
- `REGIMEN`
- `DURACION_REGIMEN`
- `NOMBRE_TITULO`
- `ACREDITACION`
- `REQUISITO_INGRESO`
- `SEMESTRES_RECONOCIDOS`
- `AREA_ACTUAL`
- `AREA_ADMIN_DERECHO`
- `AREA_AGRI_SILVI_PESCA_VET`
- `AREA_ARTES_HUMANIDADES`
- `AREA_CIENCIAS_NAT_MAT_ESTAD`
- `AREA_CS_SOCIAL_PERIODISMO_INFO`
- `AREA_EDUCACION`
- `AREA_INGE_INDUSTRIA_CONSTRUC`
- `AREA_SALUD_BIENESTAR`
- `AREA_SERVICIOS`
- `AREA_TECNO_INFO_COMUNICA`
- `VACANTES_PRIMER_SEMESTRE`
- `VACANTES_SEGUNDO_SEMESTRE`
- `MATCH_CODIGO_UNICO_DERIVADO`

### Columnas no autocompletables con bases actuales

- `Mención o Especialidad`
- `Área del Conocimiento`
- `Sub Área`
- `Carrera Genérica`
- `Grado Académico que otorga el programa`
- `Dependencia`
- `Régimen`
- `Ingreso Directo`
- `Ingreso desde un plan Común`
- `Ingreso desde Bachillerato`
- `Otro Tipo de Ingreso`
- `Ingreso otro`
- `FECHA_ADMISION_INICIAL`
- `MALLA_CURRICULAR`
- `PERFIL_EGRESO`
- `TEXTO_REQUISITO_INGRESO`
- `LICENCIA_ENS_MEDIA`
- `NOTAS_ENS_MEDIA`
- `PROMEDIO_MIN_ENS_MEDIA`
- `RECONOCIMIENTOS_APREN_PREVIOS`
- `EXPERIENCIA_LABORAL`
- `OTROS_REQUISITOS`
- `MAIL_DIFUSION_CARRERA`
- `FORMATO_VALOR`
- `VALOR_MATRICULA_ANUAL`
- `COSTO_TITULACION`
- `VALOR_CERTIFICADO_DIPLOMA`
- `ARANCEL_ANUAL`
- `VIGENCIA_CARRERA`

## Validación Especial De Los 2 Pendientes

### I162S2C6J4V1

- Método: `MATCH_R3_ESTRUCTURAL_FUERTE`
- Estado: `MATCH_UNICO`
- Confianza de match: `ALTA`
- Candidatos: `I162S2C6J4V2`
- Completar: `23`
- Mantener: `32`
- Reemplazar metodológicamente: `3`
- Dejar revisar: `29`
- Conflicto revisar: `0`
- Observación: R3 valida estructura fuerte contra versión distinta; campos estructurales son seguros desde matriz, campos de oferta/version sensibles quedan trazados con advertencia.

### I162S2C3J2V2

- Método: `MATCH_R4_AUXILIAR_AMBIGUO`
- Estado: `MATCH_AMBIGUO`
- Confianza de match: `BAJA`
- Candidatos: `I162S2C3J2V1;I162S2C3J2V3;I162S2C3J2V4`
- Completar: `0`
- Mantener: `22`
- Reemplazar metodológicamente: `3`
- Dejar revisar: `53`
- Conflicto revisar: `9`
- Observación: R4 es auxiliar y ambiguo; los candidatos cambian versión, tipo de plan, duración y otros campos críticos, por lo que no habilita completitud plena automática.

## Conflictos

- Conflictos matriz/diccionario en candidato único: `0`
- Filas totales de conflicto/ambigüedad auditadas: `7`

## Artefactos

- Excel metodológico: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_COLUMNA_POR_COLUMNA_20260604_121212.xlsx`
- CSV auditoría celda a celda: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_COLUMNA_POR_COLUMNA_20260604_121212.csv`
- Markdown: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_COLUMNA_POR_COLUMNA_20260604_121212.md`

## Validación Del Artefacto Excel

- ZIP_OOXML_VALIDO: `True`
- MACROS: `False`
- FORMULAS: `False`
- FORMULAS_TOTAL: `0`
- VINCULOS_EXTERNOS: `False`
- CONEXIONES: `False`
- DIBUJOS: `False`
- GRAFICOS: `False`
- VALIDACIONES_DATOS: `False`
- HOJAS_MAYOR_31: `False`
- HOJAS: `['RESUMEN', 'METODOLOGIA_COLUMNAS', 'AUDITORIA_CELDAS_71', 'CAMPOS_AUTOCOMPLETABLES', 'CAMPOS_REVISAR', 'CONFLICTOS_FUENTE', 'REVISION_2_PENDIENTES', 'MATCH_METODOLOGICO', 'CONTROL_TECNICO']`
- HOJAS_ESPERADAS_OK: `True`
- ABRE_OPENPYXL: `True`

## Regla Conservadora

Si una columna no tiene fuente explícita o mapeo local validado, se mantiene como REVISAR. Si hay código técnico pero falta tabla oficial para etiqueta de formulario, la auditoría lo registra como evidencia disponible, pero no lo promueve a completitud final.

