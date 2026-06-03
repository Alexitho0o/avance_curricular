# CNED Correccion Criticos Post BLOQUE 12

Fecha: 2026-06-04T19:50:20

## Archivos
- Base intacta: `/Users/alexi/Desktop/CNED_BLOQUE_12_4_COLUMNAS_CIERRE_FINAL.xlsx`
- Auditoria referencia: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_AUDITORIA_GLOBAL_FINAL_POST_BLOQUE_12_20260604_194325.xlsx`
- Salida resultados: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_CORRECCION_CRITICOS_POST_BLOQUE_12_20260604_195013.xlsx`
- Salida Escritorio: `/Users/alexi/Desktop/CNED_CORRECCION_CRITICOS_POST_BLOQUE_12.xlsx`
- CSV final: NO generado

## Control 79
- PROGRAMAS_FALTANTES_PARA_CREAR: 71
- NO_CREAR_CUBIERTO: 2
- REQUIERE_DECISION_INSTITUCIONAL: 2
- DUDOSOS_REV_MANUAL_RESUELTOS: 4
- DUDOSOS_REV_MANUAL_ACTUALIZADO: 0
- TOTAL_CONTROL: 79

## Acciones
- Total celdas auditadas: 355
- COMPLETAR: 5
- MANTENER: 339
- REEMPLAZAR: 0
- DEJAR_REVISAR: 9
- CONFLICTO_REVISAR: 2
- Conflictos remanentes: 2
- REVISAR generico remanente: 0

## Cambios efectivos
- I162S2C13J1V1 / Año de inicio de Actividades: `REVISAR` -> `REVISAR_ANIO_INICIO_SIN_FUENTE` (SIN_FUENTE_DIRECTA)
- I162S2C13J2V1 / Año de inicio de Actividades: `REVISAR` -> `REVISAR_ANIO_INICIO_SIN_FUENTE` (SIN_FUENTE_DIRECTA)
- I162S2C21J1V1 / Año de inicio de Actividades: `REVISAR` -> `REVISAR_ANIO_INICIO_SIN_FUENTE` (SIN_FUENTE_DIRECTA)
- I162S2C21J2V1 / Año de inicio de Actividades: `REVISAR` -> `REVISAR_ANIO_INICIO_SIN_FUENTE` (SIN_FUENTE_DIRECTA)
- I162S2C23J1V1 / Año de inicio de Actividades: `REVISAR` -> `REVISAR_ANIO_INICIO_SIN_FUENTE` (SIN_FUENTE_DIRECTA)
- I162S2C23J2V1 / Año de inicio de Actividades: `REVISAR` -> `REVISAR_ANIO_INICIO_SIN_FUENTE` (SIN_FUENTE_DIRECTA)
- I162S2C24J1V1 / Año de inicio de Actividades: `REVISAR` -> `REVISAR_ANIO_INICIO_SIN_FUENTE` (SIN_FUENTE_DIRECTA)
- I162S2C24J2V1 / Año de inicio de Actividades: `REVISAR` -> `REVISAR_ANIO_INICIO_SIN_FUENTE` (SIN_FUENTE_DIRECTA)
- I162S2C3J2V2 / Sede: `CONFLICTO_REVISAR` -> `Santiago` (COD_SEDE/NOMBRE_SEDE)
- I162S2C3J2V2 / Tipo de Carrera: `CONFLICTO_REVISAR` -> `Profesional` (NIVEL_CARRERA/NOMBRE_CARRERA)
- I162S2C3J2V2 / Nombre: `CONFLICTO_REVISAR` -> `INGENIERIA EN CONECTIVIDAD Y REDES` (PROMEDIOS_MATRIZ.NOMBRE_CARRERA)
- I162S2C3J2V2 / Duración del programa en Semestres: `CONFLICTO_REVISAR_DURACION_MATCH_AMBIGUO` -> `5` (PROMEDIOS_MATRIZ.DURACION_TOTAL)
- I162S2C3J2V2 / Año de inicio de Actividades: `REVISAR` -> `CONFLICTO_REVISAR_ANIO_INICIO` (MATCH_R4_AUXILIAR_AMBIGUO)
- I162S2C40J2V1 / Tipo de Carrera: `Diplomado` -> `CONFLICTO_REVISAR_TIPO_CARRERA` (NIVEL_CARRERA/NOMBRE_CARRERA)
- I162S2C41J2V1 / Año de inicio de Actividades: `REVISAR` -> `REVISAR_ANIO_INICIO_SIN_FUENTE` (SIN_FUENTE_DIRECTA)
- I162S2C6J4V1 / Año de inicio de Actividades: `REVISAR` -> `2019` (FUENTE_MATCH_R3:I162S2C6J4V2.ANIO_INICIO)

## Conteo por columna
- Año de inicio de Actividades: COMPLETAR: 1, CONFLICTO_REVISAR: 1, DEJAR_REVISAR: 9, MANTENER: 60
- Duración del programa en Semestres: COMPLETAR: 1, CONFLICTO_REVISAR: 0, DEJAR_REVISAR: 0, MANTENER: 70
- Nombre: COMPLETAR: 1, CONFLICTO_REVISAR: 0, DEJAR_REVISAR: 0, MANTENER: 70
- Sede: COMPLETAR: 1, CONFLICTO_REVISAR: 0, DEJAR_REVISAR: 0, MANTENER: 70
- Tipo de Carrera: COMPLETAR: 1, CONFLICTO_REVISAR: 1, DEJAR_REVISAR: 0, MANTENER: 69

## Conflictos remanentes controlados
- I162S2C40J2V1 / Tipo de Carrera: `CONFLICTO_REVISAR_TIPO_CARRERA`
- I162S2C3J2V2 / Año de inicio de Actividades: `CONFLICTO_REVISAR_ANIO_INICIO`

## Hashes de insumos
- base: antes `93379ef349c6dbf2e0d8223a4fb7d1263954d93f8f3aef620afe86c2a2e65a47` / despues `93379ef349c6dbf2e0d8223a4fb7d1263954d93f8f3aef620afe86c2a2e65a47` / intacto `True`
- auditoria_global: antes `75a206952b009b5aaaac53bcaba5bdc9e29553ac942991b1f03e7f411ccf9953` / despues `75a206952b009b5aaaac53bcaba5bdc9e29553ac942991b1f03e7f411ccf9953` / intacto `True`
- promedios: antes `3013fed700f871f93379bc93ebf974910f30c7c4320d40bd3d8b8638fad6a5fb` / despues `3013fed700f871f93379bc93ebf974910f30c7c4320d40bd3d8b8638fad6a5fb` / intacto `True`
- diccionario_complementado: antes `6f37fb1b393092fd0db6e3659ff6c2f663e677ffe435f719ce088f03c6152c0e` / despues `6f37fb1b393092fd0db6e3659ff6c2f663e677ffe435f719ce088f03c6152c0e` / intacto `True`

## Validacion tecnica
- OOXML valido resultados: True
- OOXML valido escritorio: True
- Sin formulas, macros, vinculos externos, conexiones, dibujos, graficos ni validaciones problematicas: SI
- Nombres de hoja <=31: SI

## DICTAMEN_FINAL: CRITICOS_RESUELTOS_CON_CONFLICTOS_CONTROLADOS
