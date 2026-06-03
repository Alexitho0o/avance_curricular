# CNED Confirmacion Metodologica Correccion I162S2C3J2V2

Fecha generacion: 2026-06-04T23:19:01

## Archivos auditados
- Operativo corregido: `/Users/alexi/Desktop/CNED_CORRECCION_20_CONFLICTOS_I162S2C3J2V2.xlsx`
- Archivo anterior saneado: `/Users/alexi/Desktop/CNED_ARCHIVO_OPERATIVO_TRABAJO_MANUAL_FINAL_SANEADO.xlsx`
- Auditoria previa 20 conflictos: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_AUDITORIA_20_CONFLICTOS_I162S2C3J2V2_20260604_225344.xlsx`
- Correccion quirurgica aplicada: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_CORRECCION_20_CONFLICTOS_I162S2C3J2V2_20260604_225738.xlsx`

## Artefactos generados
- Excel auditoria final: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_CONFIRMACION_METODOLOGICA_CORRECCION_I162S2C3J2V2_20260604_231857.xlsx`
- Markdown: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_CONFIRMACION_METODOLOGICA_CORRECCION_I162S2C3J2V2_20260604_231857.md`
- CSV auditoria: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_CONFIRMACION_METODOLOGICA_CORRECCION_I162S2C3J2V2_20260604_231857.csv`
- CSV final de carga: NO generado

## Control 79
- PROGRAMAS_FALTANTES_PARA_CREAR: 71
- NO_CREAR_CUBIERTO: 2
- REQUIERE_DECISION_INSTITUCIONAL: 2
- DUDOSOS_REV_MANUAL_RESUELTOS: 4
- DUDOSOS_REV_MANUAL_ACTUALIZADO: 0
- TOTAL_CONTROL: 79

## Confirmacion de fila I162S2C3J2V2
- Fila unica para codigo: True
- Campos resueltos por unanimidad correctos: 15/15
- Conflictos reales remanentes correctos: 5/5
- Metadata match correcta: 4/4
- REVISAR generico en fila: 0
- Conflictos detectados en fila: ANIO_INICIO, DURACION_REGIMEN, REQUISITO_INGRESO, SEMESTRES_RECONOCIDOS, VACANTES_PRIMER_SEMESTRE

## Regla metodologica confirmada
> Cuando no existe match exacto por CODIGO_UNICO_DERIVADO, pero existe familia candidata por sede, carrera, jornada y version cercana, solo se pueden autocompletar campos si todos los candidatos validos entregan exactamente el mismo valor para esa columna. Si los candidatos entregan valores distintos, el campo debe quedar como conflicto real y no debe resolverse por inferencia.

## Campos resueltos por unanimidad
- REGIMEN: `1`
- NOMBRE_TITULO: `INGENIERO EN CONECTIVIDAD Y REDES`
- ACREDITACION: `2`
- AREA_ACTUAL: `10`
- AREA_ADMIN_DERECHO: `0`
- AREA_AGRI_SILVI_PESCA_VET: `0`
- AREA_ARTES_HUMANIDADES: `0`
- AREA_CIENCIAS_NAT_MAT_ESTAD: `0`
- AREA_CS_SOCIAL_PERIODISMO_INFO: `0`
- AREA_EDUCACION: `0`
- AREA_INGE_INDUSTRIA_CONSTRUC: `0`
- AREA_SALUD_BIENESTAR: `0`
- AREA_SERVICIOS: `0`
- AREA_TECNO_INFO_COMUNICA: `0`
- VACANTES_SEGUNDO_SEMESTRE: `0`

## Conflictos reales remanentes
- ANIO_INICIO: `CONFLICTO_REVISAR_ANIO_INICIO_VERSIONES_MULTIPLES_2002_2017_2019`
- DURACION_REGIMEN: `CONFLICTO_REVISAR_DURACION_REGIMEN_VERSIONES_MULTIPLES_4_8`
- REQUISITO_INGRESO: `CONFLICTO_REVISAR_REQUISITO_INGRESO_VERSIONES_MULTIPLES_1_2`
- SEMESTRES_RECONOCIDOS: `CONFLICTO_REVISAR_SEMESTRES_RECONOCIDOS_VERSIONES_MULTIPLES_0_4`
- VACANTES_PRIMER_SEMESTRE: `CONFLICTO_REVISAR_VACANTES_PRIMER_SEMESTRE_VERSIONES_MULTIPLES_0_30`

## Candidatos usados
- I162S2C3J2V1
- I162S2C3J2V3
- I162S2C3J2V4

## Hashes de fuentes
- operativo_corregido: antes `447ab64f72da29a63800698bb335735bfc1d09fe17353e541713f296d9470865` / despues `447ab64f72da29a63800698bb335735bfc1d09fe17353e541713f296d9470865` / intacto `True`
- archivo_anterior_saneado: antes `05269136d6076e12a9941cd7c6d4a982525c140179d79788a2a2fab98640f575` / despues `05269136d6076e12a9941cd7c6d4a982525c140179d79788a2a2fab98640f575` / intacto `True`
- promedios_matriz: antes `3013fed700f871f93379bc93ebf974910f30c7c4320d40bd3d8b8638fad6a5fb` / despues `3013fed700f871f93379bc93ebf974910f30c7c4320d40bd3d8b8638fad6a5fb` / intacto `True`
- diccionario_complementado: antes `6f37fb1b393092fd0db6e3659ff6c2f663e677ffe435f719ce088f03c6152c0e` / despues `6f37fb1b393092fd0db6e3659ff6c2f663e677ffe435f719ce088f03c6152c0e` / intacto `True`
- referencia_indices: antes `ed6a947de6650842eb739e85f5c1be8d77c1d591fe256990abd8cacfddffcde0` / despues `ed6a947de6650842eb739e85f5c1be8d77c1d591fe256990abd8cacfddffcde0` / intacto `True`
- auditoria_20_conflictos: antes `38cdc729904ce8e6bf8349b78242a9b7ab0d11ed9d54208e4910d54777944f6c` / despues `38cdc729904ce8e6bf8349b78242a9b7ab0d11ed9d54208e4910d54777944f6c` / intacto `True`
- correccion_quirurgica: antes `055d6c5af72020a8023dc00112ed8bcc2133f63d330f22fb872ae921fb51f090` / despues `055d6c5af72020a8023dc00112ed8bcc2133f63d330f22fb872ae921fb51f090` / intacto `True`

## Validacion tecnica operativo corregido
- OOXML valido: True
- Abre con openpyxl: True
- Sin formulas: True
- Sin macros: True
- Sin vinculos externos: True
- Sin conexiones: True
- Sin dibujos/graficos: True
- Sin validaciones problematicas: True
- Nombres de hoja <=31: True

## Errores de validacion
- Sin errores.

## DICTAMEN_FINAL: METODOLOGIA_CONFIRMADA_Y_ARTEFACTOS_CREADOS
