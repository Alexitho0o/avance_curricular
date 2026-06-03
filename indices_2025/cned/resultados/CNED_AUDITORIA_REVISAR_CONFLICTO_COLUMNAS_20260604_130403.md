# CNED / ÍNDICES - Auditoría REVISAR / CONFLICTO por Columnas 20260604_130403

**DICTAMEN_FINAL: EXISTEN_REVISAR_COMPLETABLES_CON_FUENTE**

Esta auditoría es no destructiva. No crea Excel operativo final ni CSV final sin encabezados; solo revisa si los `REVISAR`, vacíos y `CONFLICTO_REVISAR` del archivo aplicado están justificados o tienen fuente disponible.

## Insumos
- excel_aplicado: `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_APLICA_METODOLOGIA_COLUMNAS.xlsx`
  - SHA256 antes: `c334dafff689132c698c1e2194b018f865529429f4fa857af2a115be62e123a4`
  - SHA256 después: `c334dafff689132c698c1e2194b018f865529429f4fa857af2a115be62e123a4`
  - Intacto: `SI`
- promedios: `/Users/alexi/Documents/GitHub/avance_curricular/input/PROMEDIOSDEALUMNOS_7804.xlsx`
  - SHA256 antes: `3013fed700f871f93379bc93ebf974910f30c7c4320d40bd3d8b8638fad6a5fb`
  - SHA256 después: `3013fed700f871f93379bc93ebf974910f30c7c4320d40bd3d8b8638fad6a5fb`
  - Intacto: `SI`
- diccionario: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS_COMPLEMENTADO_20260604_110722.tsv`
  - SHA256 antes: `6f37fb1b393092fd0db6e3659ff6c2f663e677ffe435f719ce088f03c6152c0e`
  - SHA256 después: `6f37fb1b393092fd0db6e3659ff6c2f663e677ffe435f719ce088f03c6152c0e`
  - Intacto: `SI`
- metodologia: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_COLUMNA_POR_COLUMNA_20260604_121448.xlsx`
  - SHA256 antes: `f5e43bcb22dadd0d6c581e6121b6ffe9a3af08105f1b1b91e6ba1f41838f14de`
  - SHA256 después: `f5e43bcb22dadd0d6c581e6121b6ffe9a3af08105f1b1b91e6ba1f41838f14de`
  - Intacto: `SI`
- referencia_indices: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/data/listado_referencia_cned.tsv`
  - SHA256 antes: `ed6a947de6650842eb739e85f5c1be8d77c1d591fe256990abd8cacfddffcde0`
  - SHA256 después: `ed6a947de6650842eb739e85f5c1be8d77c1d591fe256990abd8cacfddffcde0`
  - Intacto: `SI`
- excel_reconciliado_contexto: `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO_LIMPIO_CON_DICCIONARIO_RECONCILIADO.xlsx`
  - SHA256 antes: `5b3989d80aeef13798f9369eccd28767257b72f92317b6bac9b2f73e02d1e172`
  - SHA256 después: `5b3989d80aeef13798f9369eccd28767257b72f92317b6bac9b2f73e02d1e172`
  - Intacto: `SI`
- excel_operativo_seguro_previo: `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO_LIMPIO.xlsx`
  - SHA256 antes: `ed363f3e1626b3c1d3a2138ef5eb8580738f687a41fa7b796feae5f61187969b`
  - SHA256 después: `ed363f3e1626b3c1d3a2138ef5eb8580738f687a41fa7b796feae5f61187969b`
  - Intacto: `SI`

## Totales
- Columnas auditadas: `86`
- Celdas auditadas: `6106`
- REVISAR: `2304`
- Vacíos: `0`
- CONFLICTO_REVISAR: `9`
- Columnas completables o revisables con fuente/regla: `0`
- Columnas no completables/no formulario: `72`
- Conflictos registrados: `51`

## Dictámenes Por Celda
- COMPLETABLE_POR_REGLA_CONDICIONAL: `187`
- CONFLICTO_REQUIERE_DECISION: `44`
- NO_APLICA_AL_FORMULARIO_FINAL: `1`
- REVISAR_CORRECTO_SIN_FUENTE: `2081`

## Dictámenes Por Columna
- CONFLICTO_REQUIERE_DECISION: `44`
- MANTENER_VALOR_EXISTENTE: `14`
- NO_APLICA_AL_FORMULARIO_FINAL: `11`
- REVISAR_CORRECTO_SIN_FUENTE: `17`

## Columnas Con Segunda Pasada Posible

## Columnas Que Deben Mantener Revisión O No Son Formulario
- `Sede`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=0, CONFLICTO=1; observación: Pendientes observados: REVISAR=0, VACIOS=0, CONFLICTO=1.
- `Tipo de Carrera`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=0, CONFLICTO=1; observación: Pendientes observados: REVISAR=0, VACIOS=0, CONFLICTO=1.
- `Nombre`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=0, CONFLICTO=1; observación: Pendientes observados: REVISAR=0, VACIOS=0, CONFLICTO=1.
- `Mención o Especialidad`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0.
- `Año de inicio de Actividades`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=11, CONFLICTO=0; observación: Pendientes observados: REVISAR=11, VACIOS=0, CONFLICTO=0. Se contrasta contra ANIO_INICIO; quedan casos sin fuente y R3/R4 especiales.
- `Campus`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=3, CONFLICTO=1; observación: Pendientes observados: REVISAR=3, VACIOS=0, CONFLICTO=1.
- `Horario`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=1, CONFLICTO=1; observación: Pendientes observados: REVISAR=1, VACIOS=0, CONFLICTO=1.
- `Estado`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=0, CONFLICTO=1; observación: Pendientes observados: REVISAR=0, VACIOS=0, CONFLICTO=1.
- `Tipo Programa`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=0, CONFLICTO=1; observación: Pendientes observados: REVISAR=0, VACIOS=0, CONFLICTO=1.
- `Detalle del Tipo de Programa (especiales)`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=14, CONFLICTO=0; observación: Pendientes observados: REVISAR=14, VACIOS=0, CONFLICTO=0.
- `Modalidad del Programa`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=2, CONFLICTO=1; observación: Pendientes observados: REVISAR=2, VACIOS=0, CONFLICTO=1.
- `Área del Conocimiento`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0. Existe código técnico en diccionario, pero puede requerir validación de formato/etiqueta de formulario.
- `Sub Área`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0. No hay tabla oficial de equivalencia de área/subárea/carrera genérica.
- `Carrera Genérica`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0. No hay tabla oficial de equivalencia de área/subárea/carrera genérica.
- `Título que otorga el programa`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=10, CONFLICTO=0; observación: Pendientes observados: REVISAR=10, VACIOS=0, CONFLICTO=0.
- `Grado Académico que otorga el programa`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0.
- `Dependencia`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0.
- `Régimen`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0. Existe código técnico en diccionario, pero puede requerir validación de formato/etiqueta de formulario.
- `Duración del programa en Semestres`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=0, CONFLICTO=1; observación: Pendientes observados: REVISAR=0, VACIOS=0, CONFLICTO=1. Se contrasta contra DURACION_TOTAL de matriz; R4 ambiguo queda aislado.
- `Ingreso Directo`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0. Existe código técnico en diccionario, pero puede requerir validación de formato/etiqueta de formulario.
- `Ingreso desde un plan Común`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0.
- `Ingreso desde Bachillerato`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0.
- `Otro Tipo de Ingreso`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0.
- `Ingreso otro`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0.
- `ANIO_INICIO`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=11, CONFLICTO=0; observación: Pendientes observados: REVISAR=11, VACIOS=0, CONFLICTO=0.
- `REGIMEN`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=10, CONFLICTO=0; observación: Pendientes observados: REVISAR=10, VACIOS=0, CONFLICTO=0.
- `DURACION_REGIMEN`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=10, CONFLICTO=0; observación: Pendientes observados: REVISAR=10, VACIOS=0, CONFLICTO=0.
- `NOMBRE_TITULO`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=10, CONFLICTO=0; observación: Pendientes observados: REVISAR=10, VACIOS=0, CONFLICTO=0.
- `ACREDITACION`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=10, CONFLICTO=0; observación: Pendientes observados: REVISAR=10, VACIOS=0, CONFLICTO=0.
- `REQUISITO_INGRESO`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=10, CONFLICTO=0; observación: Pendientes observados: REVISAR=10, VACIOS=0, CONFLICTO=0.
- `SEMESTRES_RECONOCIDOS`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=10, CONFLICTO=0; observación: Pendientes observados: REVISAR=10, VACIOS=0, CONFLICTO=0.
- `AREA_ACTUAL`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=10, CONFLICTO=0; observación: Pendientes observados: REVISAR=10, VACIOS=0, CONFLICTO=0.
- `AREA_ADMIN_DERECHO`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=10, CONFLICTO=0; observación: Pendientes observados: REVISAR=10, VACIOS=0, CONFLICTO=0.
- `AREA_AGRI_SILVI_PESCA_VET`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=10, CONFLICTO=0; observación: Pendientes observados: REVISAR=10, VACIOS=0, CONFLICTO=0.
- `AREA_ARTES_HUMANIDADES`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=10, CONFLICTO=0; observación: Pendientes observados: REVISAR=10, VACIOS=0, CONFLICTO=0.
- `AREA_CIENCIAS_NAT_MAT_ESTAD`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=10, CONFLICTO=0; observación: Pendientes observados: REVISAR=10, VACIOS=0, CONFLICTO=0.
- `AREA_CS_SOCIAL_PERIODISMO_INFO`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=10, CONFLICTO=0; observación: Pendientes observados: REVISAR=10, VACIOS=0, CONFLICTO=0.
- `AREA_EDUCACION`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=10, CONFLICTO=0; observación: Pendientes observados: REVISAR=10, VACIOS=0, CONFLICTO=0.
- `AREA_INGE_INDUSTRIA_CONSTRUC`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=10, CONFLICTO=0; observación: Pendientes observados: REVISAR=10, VACIOS=0, CONFLICTO=0.
- `AREA_SALUD_BIENESTAR`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=10, CONFLICTO=0; observación: Pendientes observados: REVISAR=10, VACIOS=0, CONFLICTO=0.
- `AREA_SERVICIOS`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=10, CONFLICTO=0; observación: Pendientes observados: REVISAR=10, VACIOS=0, CONFLICTO=0.
- `AREA_TECNO_INFO_COMUNICA`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=10, CONFLICTO=0; observación: Pendientes observados: REVISAR=10, VACIOS=0, CONFLICTO=0.
- `VACANTES_PRIMER_SEMESTRE`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=11, CONFLICTO=0; observación: Pendientes observados: REVISAR=11, VACIOS=0, CONFLICTO=0.
- `VACANTES_SEGUNDO_SEMESTRE`: `CONFLICTO_REQUIERE_DECISION`; REVISAR=11, CONFLICTO=0; observación: Pendientes observados: REVISAR=11, VACIOS=0, CONFLICTO=0.
- `FECHA_ADMISION_INICIAL`: `REVISAR_CORRECTO_SIN_FUENTE`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0. No hay fuente documental/arancelaria en matriz/diccionario.
- `MALLA_CURRICULAR`: `REVISAR_CORRECTO_SIN_FUENTE`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0. No hay fuente documental/arancelaria en matriz/diccionario.
- `PERFIL_EGRESO`: `REVISAR_CORRECTO_SIN_FUENTE`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0. No hay fuente documental/arancelaria en matriz/diccionario.
- `TEXTO_REQUISITO_INGRESO`: `REVISAR_CORRECTO_SIN_FUENTE`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0.
- `LICENCIA_ENS_MEDIA`: `REVISAR_CORRECTO_SIN_FUENTE`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0.
- `NOTAS_ENS_MEDIA`: `REVISAR_CORRECTO_SIN_FUENTE`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0.
- `PROMEDIO_MIN_ENS_MEDIA`: `REVISAR_CORRECTO_SIN_FUENTE`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0.
- `RECONOCIMIENTOS_APREN_PREVIOS`: `REVISAR_CORRECTO_SIN_FUENTE`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0.
- `EXPERIENCIA_LABORAL`: `REVISAR_CORRECTO_SIN_FUENTE`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0.
- `OTROS_REQUISITOS`: `REVISAR_CORRECTO_SIN_FUENTE`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0.
- `MAIL_DIFUSION_CARRERA`: `REVISAR_CORRECTO_SIN_FUENTE`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0. No hay fuente documental/arancelaria en matriz/diccionario.
- `FORMATO_VALOR`: `REVISAR_CORRECTO_SIN_FUENTE`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0. No hay fuente documental/arancelaria en matriz/diccionario.
- `VALOR_MATRICULA_ANUAL`: `REVISAR_CORRECTO_SIN_FUENTE`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0. No hay fuente documental/arancelaria en matriz/diccionario.
- `COSTO_TITULACION`: `REVISAR_CORRECTO_SIN_FUENTE`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0. No hay fuente documental/arancelaria en matriz/diccionario.
- `VALOR_CERTIFICADO_DIPLOMA`: `REVISAR_CORRECTO_SIN_FUENTE`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0. No hay fuente documental/arancelaria en matriz/diccionario.
- `ARANCEL_ANUAL`: `REVISAR_CORRECTO_SIN_FUENTE`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0. No hay fuente documental/arancelaria en matriz/diccionario.
- `VIGENCIA_CARRERA`: `REVISAR_CORRECTO_SIN_FUENTE`; REVISAR=71, CONFLICTO=0; observación: Pendientes observados: REVISAR=71, VACIOS=0, CONFLICTO=0.
- `MATCH_CODIGO_UNICO_DERIVADO`: `NO_APLICA_AL_FORMULARIO_FINAL`; REVISAR=1, CONFLICTO=0; observación: Pendientes observados: REVISAR=1, VACIOS=0, CONFLICTO=0.

## Casos Especiales

- `I162S2C6J4V1`: R3 estructural fuerte, pero al auditar REVISAR remanentes se clasifica como regla condicional para campos sensibles como `ANIO_INICIO` y vacantes; no se recomienda autocompletar sin revisión específica.
- `I162S2C3J2V2`: R4 auxiliar ambiguo. Los `CONFLICTO_REVISAR` son metodológicamente correctos hasta decisión, porque los candidatos cambian versión, tipo de plan, duración y otros campos críticos.

## Artefactos
- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_AUDITORIA_REVISAR_CONFLICTO_COLUMNAS_20260604_130403.xlsx`
- Markdown: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_AUDITORIA_REVISAR_CONFLICTO_COLUMNAS_20260604_130403.md`
- CSV auditoría celdas: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_AUDITORIA_REVISAR_CONFLICTO_COLUMNAS_20260604_130403.csv`

## Validación Técnica Del Excel Generado
- ZIP_OOXML_VALIDO: `True`
- ABRE_OPENPYXL: `True`
- MACROS: `False`
- FORMULAS: `False`
- FORMULAS_TOTAL: `0`
- VINCULOS_EXTERNOS: `False`
- CONEXIONES: `False`
- DIBUJOS: `False`
- GRAFICOS: `False`
- VALIDACIONES_DATOS: `False`
- HOJAS_MAYOR_31: `False`
- HOJAS: `['RESUMEN', 'AUDITORIA_COLUMNAS', 'AUDITORIA_CELDAS_REVISAR', 'COLUMNAS_COMPLETABLES', 'COLUMNAS_NO_COMPLETABLES', 'CONFLICTOS', 'CONTROL_TECNICO']`

## Restricciones
- CSV final sin encabezados generado: `NO`
- Excel operativo final generado: `NO`
- Archivos fuente modificados: `NO`
