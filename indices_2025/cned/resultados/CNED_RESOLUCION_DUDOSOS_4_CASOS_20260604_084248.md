# CNED Resolucion de Dudosos - 4 Casos

## Contexto

- Fuente principal de oferta: input/PROMEDIOSDEALUMNOS_7804.xlsx, hoja matriz.
- Fuente de referencia existente: indices_2025/cned/data/listado_referencia_cned.tsv.
- Artefacto operativo usado como origen de dudosos: indices_2025/cned/resultados/CNED_PROGRAMAS_FALTANTES_CREAR_INDICES_DESDE_PROMEDIOS_20260604_082355.xlsx.
- Archivo del Escritorio preservado sin modificacion: /Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES.xlsx.

## Dictamen ejecutivo

- Casos cubiertos por version posterior: 2
- Casos que quedan en dudosos por decision institucional: 2
- Casos para crear como programa nuevo: 0

## I162S2C1J4V1 - INGENIERIA EN INFORMATICA

- Codigo dudoso: I162S2C1J4V1
- Nombre carrera: INGENIERIA EN INFORMATICA
- Institucion: IP CIISA
- Sede: CASA CENTRAL (SANTIAGO)
- Jornada: 4
- Modalidad: 3
- Tipo plan: 1
- Duracion: 8
- Nivel global: 1
- Nivel carrera: 2
- Match auxiliar declarado: I162S2C46J4V2
- Evidencia en matriz:
  - Registro exacto en matriz: I162S2C1J4V1 | IES=IP CIISA | sede=CASA CENTRAL (SANTIAGO) | jornada=4 | modalidad=3 | tipo_plan=1 | duracion=8 | nivel_global=1 | nivel_carrera=2 | vigencia=1
  - Version posterior estructural detectada: I162S2C1J4V2
- Evidencia en referencia:
  - Existe exacto en referencia para el codigo dudoso: NO
  - Existe el match auxiliar declarado en referencia: SI
  - Existe en referencia la version posterior estructural: SI
- Comparacion con match auxiliar:
  - Match auxiliar declarado: I162S2C46J4V2
  - Mismo nombre con match auxiliar: NO
  - Mismo COD_CARRERA derivado con match auxiliar: NO
  - Misma jornada con match auxiliar: SI
  - Misma modalidad con match auxiliar: SI
  - Mismo tipo plan con match auxiliar: NO
  - Misma duracion con match auxiliar: NO
- Dictamen recomendado: MANTENER_EN_DUDOSOS_REVISAR_MANUAL
- Motivo del dictamen: Caso historico de IP CIISA en matriz. Se detecta version posterior estructural I162S2C1J4V2 bajo IP SAN SEBASTIAN. La regla institucional exige no decidir automaticamente la cobertura de programas historicos CIISA bajo el codigo IES 162 actual. El match auxiliar declarado I162S2C46J4V2 no cubre el caso porque corresponde a INGENIERIA EN CIBERSEGURIDAD, con otro COD_CARRERA, otro tipo de plan y otra duracion. Ademas, la referencia del candidato estructural presenta observaciones: nombre_referencia_no_coincide_exactamente_con_matriz; tipo_programa_referencia_difiere_de_tipo_plan_matriz.
- Accion recomendada sobre el Excel operativo: crear hoja REQUIERE_DECISION_INSTITUCIONAL
- Riesgo si se crea erroneamente: Crear bajo el universo actual un programa historico CIISA sin decision institucional podria duplicar o asignar mal la cobertura bajo IP SAN SEBASTIAN.
- Riesgo si no se crea erroneamente: Si institucionalmente correspondia homologar o migrar la continuidad CIISA -> IP SAN SEBASTIAN, no crear podria dejar una brecha de trazabilidad o cobertura.

## I162S2C3J1V1 - INGENIERIA EN CONECTIVIDAD Y REDES

- Codigo dudoso: I162S2C3J1V1
- Nombre carrera: INGENIERIA EN CONECTIVIDAD Y REDES
- Institucion: IP SAN SEBASTIAN
- Sede: CASA CENTRAL (SANTIAGO)
- Jornada: 1
- Modalidad: 1
- Tipo plan: 1
- Duracion: 8
- Nivel global: 1
- Nivel carrera: 2
- Match auxiliar declarado: I162S2C3J1V2
- Evidencia en matriz:
  - Registro exacto en matriz: I162S2C3J1V1 | IES=IP SAN SEBASTIAN | sede=CASA CENTRAL (SANTIAGO) | jornada=1 | modalidad=1 | tipo_plan=1 | duracion=8 | nivel_global=1 | nivel_carrera=2 | vigencia=1
  - Version posterior estructural detectada: I162S2C3J1V2
- Evidencia en referencia:
  - Existe exacto en referencia para el codigo dudoso: NO
  - Existe el match auxiliar declarado en referencia: SI
  - Existe en referencia la version posterior estructural: SI
- Comparacion con match auxiliar:
  - Match auxiliar declarado: I162S2C3J1V2
  - Mismo nombre con match auxiliar: SI
  - Mismo COD_CARRERA derivado con match auxiliar: SI
  - Misma jornada con match auxiliar: SI
  - Misma modalidad con match auxiliar: SI
  - Mismo tipo plan con match auxiliar: SI
  - Misma duracion con match auxiliar: SI
- Dictamen recomendado: NO_CREAR_YA_CUBIERTO_POR_VERSION_POSTERIOR
- Motivo del dictamen: Existe version posterior estructural I162S2C3J1V2 con mismo nombre, misma sede, misma jornada, misma modalidad, mismo tipo de plan, misma duracion y mismos niveles. La version posterior aparece en matriz y en referencia; por regla 2, el caso queda cubierto por version posterior.
- Accion recomendada sobre el Excel operativo: crear hoja NO_CREAR_CUBIERTO
- Riesgo si se crea erroneamente: Duplicar un programa ya cubierto por una version posterior vigente y presente en INDICES/CNED.
- Riesgo si no se crea erroneamente: Perder trazabilidad historica de V1, aunque la oferta operativa ya queda cubierta por la version posterior.

## I162S2C3J2V1 - INGENIERIA EN CONECTIVIDAD Y REDES

- Codigo dudoso: I162S2C3J2V1
- Nombre carrera: INGENIERIA EN CONECTIVIDAD Y REDES
- Institucion: IP SAN SEBASTIAN
- Sede: CASA CENTRAL (SANTIAGO)
- Jornada: 2
- Modalidad: 1
- Tipo plan: 1
- Duracion: 8
- Nivel global: 1
- Nivel carrera: 2
- Match auxiliar declarado: I162S2C3J2V4
- Evidencia en matriz:
  - Registro exacto en matriz: I162S2C3J2V1 | IES=IP SAN SEBASTIAN | sede=CASA CENTRAL (SANTIAGO) | jornada=2 | modalidad=1 | tipo_plan=1 | duracion=8 | nivel_global=1 | nivel_carrera=2 | vigencia=1
  - Version posterior estructural detectada: I162S2C3J2V4
- Evidencia en referencia:
  - Existe exacto en referencia para el codigo dudoso: NO
  - Existe el match auxiliar declarado en referencia: SI
  - Existe en referencia la version posterior estructural: SI
- Comparacion con match auxiliar:
  - Match auxiliar declarado: I162S2C3J2V4
  - Mismo nombre con match auxiliar: SI
  - Mismo COD_CARRERA derivado con match auxiliar: SI
  - Misma jornada con match auxiliar: SI
  - Misma modalidad con match auxiliar: SI
  - Mismo tipo plan con match auxiliar: SI
  - Misma duracion con match auxiliar: SI
- Dictamen recomendado: NO_CREAR_YA_CUBIERTO_POR_VERSION_POSTERIOR
- Motivo del dictamen: Existe version posterior estructural I162S2C3J2V4 con mismo nombre, misma sede, misma jornada, misma modalidad, mismo tipo de plan, misma duracion y mismos niveles. La version posterior aparece en matriz y en referencia; por regla 2, el caso queda cubierto por version posterior. Observaciones no bloqueantes de referencia: modalidad_referencia_vacia.
- Accion recomendada sobre el Excel operativo: crear hoja NO_CREAR_CUBIERTO
- Riesgo si se crea erroneamente: Duplicar un programa ya cubierto por una version posterior vigente y presente en INDICES/CNED.
- Riesgo si no se crea erroneamente: Perder trazabilidad historica de V1, aunque la oferta operativa ya queda cubierta por la version posterior.

## I162S2C3J4V1 - INGENIERIA EN CONECTIVIDAD Y REDES

- Codigo dudoso: I162S2C3J4V1
- Nombre carrera: INGENIERIA EN CONECTIVIDAD Y REDES
- Institucion: IP CIISA
- Sede: CASA CENTRAL (SANTIAGO)
- Jornada: 4
- Modalidad: 3
- Tipo plan: 1
- Duracion: 8
- Nivel global: 1
- Nivel carrera: 2
- Match auxiliar declarado: I162S2C3J4V2
- Evidencia en matriz:
  - Registro exacto en matriz: I162S2C3J4V1 | IES=IP CIISA | sede=CASA CENTRAL (SANTIAGO) | jornada=4 | modalidad=3 | tipo_plan=1 | duracion=8 | nivel_global=1 | nivel_carrera=2 | vigencia=1
  - Version posterior estructural detectada: I162S2C3J4V2
- Evidencia en referencia:
  - Existe exacto en referencia para el codigo dudoso: NO
  - Existe el match auxiliar declarado en referencia: SI
  - Existe en referencia la version posterior estructural: SI
- Comparacion con match auxiliar:
  - Match auxiliar declarado: I162S2C3J4V2
  - Mismo nombre con match auxiliar: SI
  - Mismo COD_CARRERA derivado con match auxiliar: SI
  - Misma jornada con match auxiliar: SI
  - Misma modalidad con match auxiliar: SI
  - Mismo tipo plan con match auxiliar: SI
  - Misma duracion con match auxiliar: SI
- Dictamen recomendado: MANTENER_EN_DUDOSOS_REVISAR_MANUAL
- Motivo del dictamen: Caso historico de IP CIISA en matriz. Se detecta version posterior estructural I162S2C3J4V2 bajo IP SAN SEBASTIAN. La regla institucional exige no decidir automaticamente la cobertura de programas historicos CIISA bajo el codigo IES 162 actual.
- Accion recomendada sobre el Excel operativo: crear hoja REQUIERE_DECISION_INSTITUCIONAL
- Riesgo si se crea erroneamente: Crear bajo el universo actual un programa historico CIISA sin decision institucional podria duplicar o asignar mal la cobertura bajo IP SAN SEBASTIAN.
- Riesgo si no se crea erroneamente: Si institucionalmente correspondia homologar o migrar la continuidad CIISA -> IP SAN SEBASTIAN, no crear podria dejar una brecha de trazabilidad o cobertura.

## Tabla consolidada

| CODIGO_UNICO | NOMBRE_CARRERA | NOMBRE_IES | MATCH_AUXILIAR | EXISTE_EXACTO_REFERENCIA | COBERTURA_ESTRUCTURAL | DICTAMEN_RECOMENDADO | ACCION_EXCEL |
| --- | --- | --- | --- | --- | --- | --- | --- |
| I162S2C1J4V1 | INGENIERIA EN INFORMATICA | IP CIISA | I162S2C46J4V2 | NO | SI: I162S2C1J4V2; mismo_ies=NO; existe_en_referencia=SI; observaciones=nombre_referencia_no_coincide_exactamente_con_matriz; tipo_programa_referencia_difiere_de_tipo_plan_matriz | MANTENER_EN_DUDOSOS_REVISAR_MANUAL | crear hoja REQUIERE_DECISION_INSTITUCIONAL |
| I162S2C3J1V1 | INGENIERIA EN CONECTIVIDAD Y REDES | IP SAN SEBASTIAN | I162S2C3J1V2 | NO | SI: I162S2C3J1V2; mismo_ies=SI; existe_en_referencia=SI | NO_CREAR_YA_CUBIERTO_POR_VERSION_POSTERIOR | crear hoja NO_CREAR_CUBIERTO |
| I162S2C3J2V1 | INGENIERIA EN CONECTIVIDAD Y REDES | IP SAN SEBASTIAN | I162S2C3J2V4 | NO | SI: I162S2C3J2V4; mismo_ies=SI; existe_en_referencia=SI; observaciones=modalidad_referencia_vacia | NO_CREAR_YA_CUBIERTO_POR_VERSION_POSTERIOR | crear hoja NO_CREAR_CUBIERTO |
| I162S2C3J4V1 | INGENIERIA EN CONECTIVIDAD Y REDES | IP CIISA | I162S2C3J4V2 | NO | SI: I162S2C3J4V2; mismo_ies=NO; existe_en_referencia=SI | MANTENER_EN_DUDOSOS_REVISAR_MANUAL | crear hoja REQUIERE_DECISION_INSTITUCIONAL |
