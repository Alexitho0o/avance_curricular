# CNED / ÍNDICES - Aplicación Metodología Columna Por Columna 20260604_122517

**DICTAMEN_FINAL: METODOLOGIA_APLICADA_CON_CONFLICTOS_CONTROLADOS**

Se aplicó `AUDITORIA_CELDAS_71` como fuente principal de instrucciones celda a celda. No se recalculó libremente la metodología y no se generó CSV final de carga sin encabezados.

## Archivos De Entrada
- excel_operativo_base: `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO_LIMPIO_CON_DICCIONARIO_RECONCILIADO.xlsx`
  - SHA256 antes: `5b3989d80aeef13798f9369eccd28767257b72f92317b6bac9b2f73e02d1e172`
  - SHA256 después: `5b3989d80aeef13798f9369eccd28767257b72f92317b6bac9b2f73e02d1e172`
  - Intacto: `SI`
- metodologia_columna_por_columna: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_COLUMNA_POR_COLUMNA_20260604_121448.xlsx`
  - SHA256 antes: `f5e43bcb22dadd0d6c581e6121b6ffe9a3af08105f1b1b91e6ba1f41838f14de`
  - SHA256 después: `f5e43bcb22dadd0d6c581e6121b6ffe9a3af08105f1b1b91e6ba1f41838f14de`
  - Intacto: `SI`
- diccionario_complementado_tsv: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS_COMPLEMENTADO_20260604_110722.tsv`
  - SHA256 antes: `6f37fb1b393092fd0db6e3659ff6c2f663e677ffe435f719ce088f03c6152c0e`
  - SHA256 después: `6f37fb1b393092fd0db6e3659ff6c2f663e677ffe435f719ce088f03c6152c0e`
  - Intacto: `SI`
- promedios_matriz: `/Users/alexi/Documents/GitHub/avance_curricular/input/PROMEDIOSDEALUMNOS_7804.xlsx`
  - SHA256 antes: `3013fed700f871f93379bc93ebf974910f30c7c4320d40bd3d8b8638fad6a5fb`
  - SHA256 después: `3013fed700f871f93379bc93ebf974910f30c7c4320d40bd3d8b8638fad6a5fb`
  - Intacto: `SI`
- referencia_indices: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/data/listado_referencia_cned.tsv`
  - SHA256 antes: `ed6a947de6650842eb739e85f5c1be8d77c1d591fe256990abd8cacfddffcde0`
  - SHA256 después: `ed6a947de6650842eb739e85f5c1be8d77c1d591fe256990abd8cacfddffcde0`
  - Intacto: `SI`

## Archivos Generados
- Excel enriquecido resultados: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_PROGRAMAS_FALTANTES_APLICA_METODOLOGIA_COLUMNAS_20260604_122517.xlsx`
- Excel enriquecido Escritorio: `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_APLICA_METODOLOGIA_COLUMNAS.xlsx`
- CSV auditoría de aplicación: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_APLICACION_METODOLOGIA_COLUMNAS_20260604_122517.csv`
- Markdown: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_APLICACION_METODOLOGIA_COLUMNAS_20260604_122517.md`

## Conteos De Control
- PROGRAMAS_FALTANTES_PARA_CREAR: `71`
- NO_CREAR_CUBIERTO: `2`
- REQUIERE_DECISION_INSTITUCIONAL: `2`
- DUDOSOS_REV_MANUAL_RESUELTOS: `4`
- DUDOSOS_REV_MANUAL_ACTUALIZADO: `0`
- Total control: `79`

## Acciones Metodológicas Originales
- COMPLETAR: `143`
- CONFLICTO_REVISAR: `9`
- DEJAR_REVISAR: `2300`
- MANTENER: `3579`
- REEMPLAZAR: `75`

## Acciones Aplicadas Efectivas
- COMPLETAR: `139`
- CONFLICTO_REVISAR: `9`
- DEJAR_REVISAR: `2300`
- DEJAR_REVISAR_REGLA_ESPECIAL_R3_CONF_NO_ALTA: `4`
- MANTENER: `3579`
- REEMPLAZAR: `75`

## Cambios Reales En Celdas
- COMPLETAR: `139`
- CONFLICTO_REVISAR: `9`
- DEJAR_REVISAR: `21`
- DEJAR_REVISAR_REGLA_ESPECIAL_R3_CONF_NO_ALTA: `3`
- REEMPLAZAR: `75`
- Total cambios reales: `247`
- Celdas revisar efectivas: `2304`
- Conflictos aislados: `9`

## Validación Dos Casos Especiales

- `I162S2C6J4V1`: R3 estructural fuerte. Se aplicaron solo completitudes con confianza ALTA; 4 instrucciones COMPLETAR con confianza MEDIA fueron dejadas como REVISAR por regla especial.
- `I162S2C3J2V2`: R4 auxiliar ambiguo. No se completaron campos críticos; 9 celdas quedaron como CONFLICTO_REVISAR y solo se reemplazaron controles técnicos de match.

## Validación Técnica Excel

### Resultados
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
- HOJAS: `['RESUMEN_EJECUTIVO', 'PROGRAMAS_FALTANTES_PARA_CREAR', 'NO_CREAR_CUBIERTO', 'REQUIERE_DECISION_INSTITUCIONAL', 'DUDOSOS_REV_MANUAL_RESUELTOS', 'DUDOSOS_REV_MANUAL_ACTUALIZADO', 'DICCIONARIO_OFERTA_2026', 'MATCH_PROGRAMAS_VS_DICCIONARIO', 'AUDITORIA_COMPLETITUD', 'AUDITORIA_79_REGISTROS', 'CONTROL_TECNICO', 'AUDITORIA_APLICACION', 'CAMBIOS_APLICADOS', 'CELDAS_REVISAR', 'CONFLICTOS_REVISAR', 'CONTROL_TECNICO_APLICACION']`

### Escritorio
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
- HOJAS: `['RESUMEN_EJECUTIVO', 'PROGRAMAS_FALTANTES_PARA_CREAR', 'NO_CREAR_CUBIERTO', 'REQUIERE_DECISION_INSTITUCIONAL', 'DUDOSOS_REV_MANUAL_RESUELTOS', 'DUDOSOS_REV_MANUAL_ACTUALIZADO', 'DICCIONARIO_OFERTA_2026', 'MATCH_PROGRAMAS_VS_DICCIONARIO', 'AUDITORIA_COMPLETITUD', 'AUDITORIA_79_REGISTROS', 'CONTROL_TECNICO', 'AUDITORIA_APLICACION', 'CAMBIOS_APLICADOS', 'CELDAS_REVISAR', 'CONFLICTOS_REVISAR', 'CONTROL_TECNICO_APLICACION']`

## CSV De Carga

- CSV final sin encabezados generado: `NO`
- Nuevos archivos detectados con patrón `*CARGA_SIN_ENCABEZADOS*.csv`: `0`

## Observación Conservadora

Los campos sin fuente explícita, con mapeo no oficial o afectados por R4 ambiguo quedaron como REVISAR o CONFLICTO_REVISAR. No se inventaron equivalencias ni valores.
