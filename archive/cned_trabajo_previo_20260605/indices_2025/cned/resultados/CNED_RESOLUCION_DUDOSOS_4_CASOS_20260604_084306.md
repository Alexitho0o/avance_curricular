# CNED Resolucion de Dudosos 4 Casos

## Contexto y fuente

- Fuente principal de oferta: input/PROMEDIOSDEALUMNOS_7804.xlsx, hoja matriz.
- Referencia de existentes: indices_2025/cned/data/listado_referencia_cned.tsv.
- Excel operativo base analizado: /Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_PROGRAMAS_FALTANTES_CREAR_INDICES_DESDE_PROMEDIOS_20260604_082355.xlsx.
- Esta resolucion es no destructiva: no modifica el Excel operativo latest ni el archivo del Escritorio.

## Resultado consolidado

- I162S2C1J4V1: MANTENER_EN_DUDOSOS_REVISAR_MANUAL.
- I162S2C3J1V1: NO_CREAR_YA_CUBIERTO_POR_VERSION_POSTERIOR.
- I162S2C3J2V1: NO_CREAR_YA_CUBIERTO_POR_VERSION_POSTERIOR.
- I162S2C3J4V1: MANTENER_EN_DUDOSOS_REVISAR_MANUAL.

## I162S2C1J4V1

- Nombre carrera: INGENIERIA EN INFORMATICA
- Institucion: IP CIISA
- Sede: CASA CENTRAL (SANTIAGO) (COD_SEDE=2)
- Jornada: 4
- Modalidad: 3
- Tipo plan: 1
- Duracion total: 8
- Nivel global: 1
- Nivel carrera: 2
- Match auxiliar declarado: I162S2C46J4V2

### Evidencia en matriz
- Registro exacto vigente en matriz: SI
- Version posterior estructural detectada: I162S2C1J4V2
- Institucion de la version posterior: IP SAN SEBASTIAN
- Misma estructura fuerte (nombre, sede, jornada, modalidad, tipo plan, duracion, niveles): SI

### Evidencia en referencia
- Existe exacto en referencia para el dudoso: NO
- Existe el match auxiliar declarado en referencia: SI
- Existe la version posterior estructural en referencia: SI
- Candidatos por nombre en referencia: 7

### Comparacion con match auxiliar
- Mismo nombre: NO
- Mismo COD_CARRERA derivado: NO
- Misma jornada: SI
- Misma modalidad: SI
- Mismo tipo de plan: NO
- Misma duracion: NO

### Dictamen recomendado
- Dictamen: MANTENER_EN_DUDOSOS_REVISAR_MANUAL
- Motivo: Registro vigente de IP CIISA con version posterior estructural I162S2C1J4V2 bajo IP SAN SEBASTIAN. La cobertura historica no debe decidirse automaticamente dentro del universo actual de IP SAN SEBASTIAN. La referencia contiene I162S2C1J4V2 pero con descripcion 'Ingeniería en Informática (P.E.)' y tipo 'Programa Especial', mientras matriz lo documenta como 'INGENIERIA EN INFORMATICA' y tipo 'Programa Regular'.
- Accion recomendada sobre el Excel operativo: crear hoja REQUIERE_DECISION_INSTITUCIONAL
- Riesgo si se crea erroneamente: Crear indebidamente un programa historico de IP CIISA dentro del universo actual de IP SAN SEBASTIAN, duplicando o trasladando cobertura sin acuerdo institucional.
- Riesgo si no se crea erroneamente: Omitir un programa historico que la institucion decida mantener o migrar bajo el codigo IES 162 actual.
## I162S2C3J1V1

- Nombre carrera: INGENIERIA EN CONECTIVIDAD Y REDES
- Institucion: IP SAN SEBASTIAN
- Sede: CASA CENTRAL (SANTIAGO) (COD_SEDE=2)
- Jornada: 1
- Modalidad: 1
- Tipo plan: 1
- Duracion total: 8
- Nivel global: 1
- Nivel carrera: 2
- Match auxiliar declarado: I162S2C3J1V2

### Evidencia en matriz
- Registro exacto vigente en matriz: SI
- Version posterior estructural detectada: I162S2C3J1V2
- Institucion de la version posterior: IP SAN SEBASTIAN
- Misma estructura fuerte (nombre, sede, jornada, modalidad, tipo plan, duracion, niveles): SI

### Evidencia en referencia
- Existe exacto en referencia para el dudoso: NO
- Existe el match auxiliar declarado en referencia: SI
- Existe la version posterior estructural en referencia: SI
- Candidatos por nombre en referencia: 5

### Comparacion con match auxiliar
- Mismo nombre: SI
- Mismo COD_CARRERA derivado: SI
- Misma jornada: SI
- Misma modalidad: SI
- Mismo tipo de plan: SI
- Misma duracion: SI

### Dictamen recomendado
- Dictamen: NO_CREAR_YA_CUBIERTO_POR_VERSION_POSTERIOR
- Motivo: Existe version posterior estructural I162S2C3J1V2 con mismo nombre, sede, jornada, modalidad, tipo plan, duracion, nivel global y nivel carrera; ademas dicha version posterior aparece en la referencia CNED/INDICES.
- Accion recomendada sobre el Excel operativo: crear hoja NO_CREAR_CUBIERTO
- Riesgo si se crea erroneamente: Duplicar en INDICES un programa ya cubierto por una version posterior vigente y referenciada.
- Riesgo si no se crea erroneamente: Riesgo bajo; la cobertura posterior ya existe en matriz y en referencia.
## I162S2C3J2V1

- Nombre carrera: INGENIERIA EN CONECTIVIDAD Y REDES
- Institucion: IP SAN SEBASTIAN
- Sede: CASA CENTRAL (SANTIAGO) (COD_SEDE=2)
- Jornada: 2
- Modalidad: 1
- Tipo plan: 1
- Duracion total: 8
- Nivel global: 1
- Nivel carrera: 2
- Match auxiliar declarado: I162S2C3J2V4

### Evidencia en matriz
- Registro exacto vigente en matriz: SI
- Version posterior estructural detectada: I162S2C3J2V4
- Institucion de la version posterior: IP SAN SEBASTIAN
- Misma estructura fuerte (nombre, sede, jornada, modalidad, tipo plan, duracion, niveles): SI

### Evidencia en referencia
- Existe exacto en referencia para el dudoso: NO
- Existe el match auxiliar declarado en referencia: SI
- Existe la version posterior estructural en referencia: SI
- Candidatos por nombre en referencia: 5

### Comparacion con match auxiliar
- Mismo nombre: SI
- Mismo COD_CARRERA derivado: SI
- Misma jornada: SI
- Misma modalidad: SI
- Mismo tipo de plan: SI
- Misma duracion: SI

### Dictamen recomendado
- Dictamen: NO_CREAR_YA_CUBIERTO_POR_VERSION_POSTERIOR
- Motivo: Existe version posterior estructural I162S2C3J2V4 con mismo nombre, sede, jornada, modalidad, tipo plan, duracion, nivel global y nivel carrera; ademas dicha version posterior aparece en la referencia CNED/INDICES.
- Accion recomendada sobre el Excel operativo: crear hoja NO_CREAR_CUBIERTO
- Riesgo si se crea erroneamente: Duplicar en INDICES un programa ya cubierto por una version posterior vigente y referenciada.
- Riesgo si no se crea erroneamente: Riesgo bajo; la cobertura posterior ya existe en matriz y en referencia.
## I162S2C3J4V1

- Nombre carrera: INGENIERIA EN CONECTIVIDAD Y REDES
- Institucion: IP CIISA
- Sede: CASA CENTRAL (SANTIAGO) (COD_SEDE=2)
- Jornada: 4
- Modalidad: 3
- Tipo plan: 1
- Duracion total: 8
- Nivel global: 1
- Nivel carrera: 2
- Match auxiliar declarado: I162S2C3J4V2

### Evidencia en matriz
- Registro exacto vigente en matriz: SI
- Version posterior estructural detectada: I162S2C3J4V2
- Institucion de la version posterior: IP SAN SEBASTIAN
- Misma estructura fuerte (nombre, sede, jornada, modalidad, tipo plan, duracion, niveles): SI

### Evidencia en referencia
- Existe exacto en referencia para el dudoso: NO
- Existe el match auxiliar declarado en referencia: SI
- Existe la version posterior estructural en referencia: SI
- Candidatos por nombre en referencia: 5

### Comparacion con match auxiliar
- Mismo nombre: SI
- Mismo COD_CARRERA derivado: SI
- Misma jornada: SI
- Misma modalidad: SI
- Mismo tipo de plan: SI
- Misma duracion: SI

### Dictamen recomendado
- Dictamen: MANTENER_EN_DUDOSOS_REVISAR_MANUAL
- Motivo: Registro vigente de IP CIISA con version posterior estructural I162S2C3J4V2 bajo IP SAN SEBASTIAN. La cobertura historica no debe decidirse automaticamente dentro del universo actual de IP SAN SEBASTIAN.
- Accion recomendada sobre el Excel operativo: crear hoja REQUIERE_DECISION_INSTITUCIONAL
- Riesgo si se crea erroneamente: Crear indebidamente un programa historico de IP CIISA dentro del universo actual de IP SAN SEBASTIAN, duplicando o trasladando cobertura sin acuerdo institucional.
- Riesgo si no se crea erroneamente: Omitir un programa historico que la institucion decida mantener o migrar bajo el codigo IES 162 actual.

## Tabla consolidada

| CODIGO_UNICO | NOMBRE_CARRERA | NOMBRE_IES | MATCH_AUXILIAR | EXISTE_EXACTO_REFERENCIA | COBERTURA_ESTRUCTURAL | DICTAMEN_RECOMENDADO | ACCION_EXCEL |
| --- | --- | --- | --- | --- | --- | --- | --- |
| I162S2C1J4V1 | INGENIERIA EN INFORMATICA | IP CIISA | I162S2C46J4V2 | NO | SI: I162S2C1J4V2 (cambio de IES) | MANTENER_EN_DUDOSOS_REVISAR_MANUAL | crear hoja REQUIERE_DECISION_INSTITUCIONAL |
| I162S2C3J1V1 | INGENIERIA EN CONECTIVIDAD Y REDES | IP SAN SEBASTIAN | I162S2C3J1V2 | NO | SI: I162S2C3J1V2 | NO_CREAR_YA_CUBIERTO_POR_VERSION_POSTERIOR | crear hoja NO_CREAR_CUBIERTO |
| I162S2C3J2V1 | INGENIERIA EN CONECTIVIDAD Y REDES | IP SAN SEBASTIAN | I162S2C3J2V4 | NO | SI: I162S2C3J2V4 | NO_CREAR_YA_CUBIERTO_POR_VERSION_POSTERIOR | crear hoja NO_CREAR_CUBIERTO |
| I162S2C3J4V1 | INGENIERIA EN CONECTIVIDAD Y REDES | IP CIISA | I162S2C3J4V2 | NO | SI: I162S2C3J4V2 (cambio de IES) | MANTENER_EN_DUDOSOS_REVISAR_MANUAL | crear hoja REQUIERE_DECISION_INSTITUCIONAL |