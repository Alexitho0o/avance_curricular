# CNED / ÍNDICES - Metodología Columna Por Columna 20260604_121448

**DICTAMEN_FINAL: METODOLOGIA_DETECTA_CAMPOS_AUTOCOMPLETABLES_PENDIENTES**

Ejecución metodológica únicamente. No se generó Excel operativo final, no se escribió en Escritorio y no se creó CSV de carga sin encabezados.

## Corrección De Control

Este artefacto corrige el intermedio `20260604_121212`: excluye la columna auxiliar interna `_NOMBRE_NORM`, que no pertenece a `PROGRAMAS_FALTANTES_PARA_CREAR`. La auditoría final queda sobre 86 columnas reales y 6106 celdas.

## Insumos
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

## Validación Operativo
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
- HOJAS: `['RESUMEN_EJECUTIVO', 'PROGRAMAS_FALTANTES_PARA_CREAR', 'NO_CREAR_CUBIERTO', 'REQUIERE_DECISION_INSTITUCIONAL', 'DUDOSOS_REV_MANUAL_RESUELTOS', 'DUDOSOS_REV_MANUAL_ACTUALIZADO', 'DICCIONARIO_OFERTA_2026', 'MATCH_PROGRAMAS_VS_DICCIONARIO', 'AUDITORIA_COMPLETITUD', 'AUDITORIA_79_REGISTROS', 'CONTROL_TECNICO']`

## Conteos De Control
- PROGRAMAS_FALTANTES_PARA_CREAR: `71`
- NO_CREAR_CUBIERTO: `2`
- REQUIERE_DECISION_INSTITUCIONAL: `2`
- DUDOSOS_REV_MANUAL_RESUELTOS: `4`
- DUDOSOS_REV_MANUAL_ACTUALIZADO: `0`
- Total control: `79`

## Match Metodológico
- MATCH_R1_CODIGO_UNICO_DERIVADO: `69`
- MATCH_R3_ESTRUCTURAL_FUERTE: `1`
- MATCH_R4_AUXILIAR_AMBIGUO: `1`
- Ambiguos: `1` (I162S2C3J2V2)
- Sin match absoluto: `0`

## Auditoría Celda A Celda
- Registros: `71`
- Columnas: `86`
- Celdas auditadas: `6106`
- COMPLETAR: `143`
- CONFLICTO_REVISAR: `9`
- DEJAR_REVISAR: `2300`
- MANTENER: `3579`
- REEMPLAZAR: `75`
- Celdas con completitud pendiente detectada: `143`

## Columnas
- 100% autocompletables o mantenibles: `24`
- Parcialmente autocompletables: `33`
- No autocompletables con bases actuales: `29`

### No Autocompletables Con Bases Actuales
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

## Dos Pendientes
### I162S2C6J4V1
- Método: `MATCH_R3_ESTRUCTURAL_FUERTE`
- Estado: `MATCH_UNICO`
- Candidatos: `I162S2C6J4V2`
- COMPLETAR: `23`
- MANTENER: `31`
- REEMPLAZAR: `3`
- DEJAR_REVISAR: `29`
- CONFLICTO_REVISAR: `0`
### I162S2C3J2V2
- Método: `MATCH_R4_AUXILIAR_AMBIGUO`
- Estado: `MATCH_AMBIGUO`
- Candidatos: `I162S2C3J2V1;I162S2C3J2V3;I162S2C3J2V4`
- COMPLETAR: `0`
- MANTENER: `21`
- REEMPLAZAR: `3`
- DEJAR_REVISAR: `53`
- CONFLICTO_REVISAR: `9`

## Artefactos
- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_COLUMNA_POR_COLUMNA_20260604_121448.xlsx`
- CSV: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_COLUMNA_POR_COLUMNA_20260604_121448.csv`
- Markdown: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_COLUMNA_POR_COLUMNA_20260604_121448.md`

## Validación Artefacto Excel
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
- ABRE_OPENPYXL: `True`
- HOJAS_ESPERADAS_OK: `True`

Regla conservadora: sin fuente explícita o mapeo local validado, el campo queda REVISAR con motivo documentado.
