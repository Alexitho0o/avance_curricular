# CNED / ÍNDICES - Auditoría REVISAR / CONFLICTO por Columnas 20260604_130607

**DICTAMEN_FINAL: EXISTEN_REVISAR_COMPLETABLES_CON_FUENTE**

Auditoría no destructiva sobre el Excel aplicado. Este artefacto supera el intermedio `20260604_130403` porque corrige la prioridad del dictamen por columna: una columna puede ser completable parcialmente aunque una celda R4 permanezca en conflicto.

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
- auditoria_intermedia_superada: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_AUDITORIA_REVISAR_CONFLICTO_COLUMNAS_20260604_130403.xlsx`
  - SHA256 antes: `5079db088e8dfefa90681d30b6ee7edf412db0b3a5de18dc71cb3a8403ee2ca2`
  - SHA256 después: `5079db088e8dfefa90681d30b6ee7edf412db0b3a5de18dc71cb3a8403ee2ca2`
  - Intacto: `SI`

## Totales
- Columnas auditadas: `86`
- Celdas auditadas: `6106`
- REVISAR: `2304`
- Vacíos: `0`
- CONFLICTO_REVISAR: `9`
- Columnas completables: `7`
- Columnas no completables/no formulario: `65`
- Conflictos registrados: `51`

## Dictámenes Por Celda
- COMPLETABLE_POR_REGLA_CONDICIONAL: `187`
- CONFLICTO_REQUIERE_DECISION: `44`
- NO_APLICA_AL_FORMULARIO_FINAL: `1`
- REVISAR_CORRECTO_SIN_FUENTE: `2081`

## Dictámenes Por Columna
- COMPLETABLE_POR_REGLA_CONDICIONAL: `7`
- CONFLICTO_REQUIERE_DECISION: `37`
- MANTENER_VALOR_EXISTENTE: `14`
- NO_APLICA_AL_FORMULARIO_FINAL: `11`
- REVISAR_CORRECTO_SIN_FUENTE: `17`

## Columnas Con Segunda Pasada Posible
- `Año de inicio de Actividades`: `COMPLETABLE_POR_REGLA_CONDICIONAL`; REVISAR=11; CONFLICTO=0; regla: Segunda pasada posible solo con regla condicional/mapeo documentado; excluir R4 ambiguo.
- `Área del Conocimiento`: `COMPLETABLE_POR_REGLA_CONDICIONAL`; REVISAR=71; CONFLICTO=0; regla: Segunda pasada posible solo con regla condicional/mapeo documentado; excluir R4 ambiguo.
- `Régimen`: `COMPLETABLE_POR_REGLA_CONDICIONAL`; REVISAR=71; CONFLICTO=0; regla: Segunda pasada posible solo con regla condicional/mapeo documentado; excluir R4 ambiguo.
- `Ingreso Directo`: `COMPLETABLE_POR_REGLA_CONDICIONAL`; REVISAR=71; CONFLICTO=0; regla: Segunda pasada posible solo con regla condicional/mapeo documentado; excluir R4 ambiguo.
- `ANIO_INICIO`: `COMPLETABLE_POR_REGLA_CONDICIONAL`; REVISAR=11; CONFLICTO=0; regla: Segunda pasada posible solo con regla condicional/mapeo documentado; excluir R4 ambiguo.
- `VACANTES_PRIMER_SEMESTRE`: `COMPLETABLE_POR_REGLA_CONDICIONAL`; REVISAR=11; CONFLICTO=0; regla: Segunda pasada posible solo con regla condicional/mapeo documentado; excluir R4 ambiguo.
- `VACANTES_SEGUNDO_SEMESTRE`: `COMPLETABLE_POR_REGLA_CONDICIONAL`; REVISAR=11; CONFLICTO=0; regla: Segunda pasada posible solo con regla condicional/mapeo documentado; excluir R4 ambiguo.

## Casos Especiales
- `I162S2C6J4V1`: R3 se mantiene como regla condicional para campos sensibles remanentes; no aplicar automáticamente sin revisión específica.
- `I162S2C3J2V2`: R4 ambiguo; sus conflictos siguen correctamente aislados.

## Artefactos
- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_AUDITORIA_REVISAR_CONFLICTO_COLUMNAS_20260604_130607.xlsx`
- Markdown: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_AUDITORIA_REVISAR_CONFLICTO_COLUMNAS_20260604_130607.md`
- CSV auditoría celdas: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_AUDITORIA_REVISAR_CONFLICTO_COLUMNAS_20260604_130607.csv`

## Validación Técnica
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

- CSV final sin encabezados generado: `NO`
- Excel operativo final generado: `NO`
- Archivos fuente modificados: `NO`