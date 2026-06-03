# Conciliación Oferta Académica 2026 contra CNED/ÍNDICES

## Rutas de entrada

- Operativo seguro: `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO_LIMPIO.xlsx`
- Archivo problemático no usado: `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO.xlsx`
- Bloque OFERTA_RAW_SIN_ENCABEZADOS: pegado en el bloque Python reproducible de esta ejecución.

## Rutas de salida

- Diccionario TSV: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS.tsv`
- Diccionario Excel: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS.xlsx`
- Excel final resultados: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO_LIMPIO_CON_DICCIONARIO_20260604_104613.xlsx`
- Excel final Escritorio: `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO_LIMPIO_CON_DICCIONARIO.xlsx`
- Excel de revisión con encabezados: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_CON_DICCIONARIO_REVISION.xlsx`
- CSV carga sin encabezados: `NO_GENERADO_REQUIERE_CONFIRMACION_COD_CARRERA_EN_BLANCO_PARA_CARGA_NUEVA_TP`

## Hash SHA256

### Entradas antes

- `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO_LIMPIO.xlsx`: `ed363f3e1626b3c1d3a2138ef5eb8580738f687a41fa7b796feae5f61187969b`
- `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO.xlsx`: `c50424cf14580f3d464ba4dc571db2097221652d93aa621f518065b2aeb5dfcc`

### Entradas después

- `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO_LIMPIO.xlsx`: `ed363f3e1626b3c1d3a2138ef5eb8580738f687a41fa7b796feae5f61187969b`
- `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO.xlsx`: `c50424cf14580f3d464ba4dc571db2097221652d93aa621f518065b2aeb5dfcc`

### Salidas

- `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS.tsv`: `c457bab06e30221e72ce21e96ce51361e74becb2df49f0f6657291cf946c4990`
- `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS.xlsx`: `1f4e9bedbc369e05bd5f9dcb0a860f77964598573c4de3cfba65a0a2f6fa851d`
- `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO_LIMPIO_CON_DICCIONARIO_20260604_104613.xlsx`: `037c490b9d5fb62cf44787d4f54498b9cf7cb8ccac31df6bfe4bb09944ac72c0`
- `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_CON_DICCIONARIO_REVISION.xlsx`: `037c490b9d5fb62cf44787d4f54498b9cf7cb8ccac31df6bfe4bb09944ac72c0`
- `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO_LIMPIO_CON_DICCIONARIO.xlsx`: `037c490b9d5fb62cf44787d4f54498b9cf7cb8ccac31df6bfe4bb09944ac72c0`

## Conteos por hoja

- Diccionario Oferta 2026: 124
- PROGRAMAS_FALTANTES_PARA_CREAR: 71
- NO_CREAR_CUBIERTO: 2
- REQUIERE_DECISION_INSTITUCIONAL: 2
- DUDOSOS_REV_MANUAL_RESUELTOS: 4
- DUDOSOS_REV_MANUAL_ACTUALIZADO: 0
- TOTAL_CONTROL: 79

## Matches PROGRAMAS_FALTANTES_PARA_CREAR

- Total matches únicos: 60
- Total matches exactos: 60
- Total matches por clave estructural: 0
- Total matches por nombre/sede/jornada: 0
- Total matches por estructura nombre/modalidad/jornada/tipo/duración/niveles: 0
- Total matches ambiguos: 0
- Total registros sin match: 11

## Registros sin match

| CODIGO_UNICO | MATCH_KEY |
|---|---|
| I162S2C13J1V1 | ||1|||1|1 |
| I162S2C13J2V1 | ||2|||1|1 |
| I162S2C21J1V1 | ||1|||1|2 |
| I162S2C21J2V1 | ||2|||1|2 |
| I162S2C23J1V1 | ||1|||1|2 |
| I162S2C23J2V1 | ||2|||1|2 |
| I162S2C24J1V1 | ||1|||1|1 |
| I162S2C24J2V1 | ||2|||1|1 |
| I162S2C3J2V2 | ||2|||1|2 |
| I162S2C41J2V1 | ||2|||3|5 |
| I162S2C6J4V1 | ||4|||1|1 |

## Causa de registros sin match

| CODIGO_UNICO | Cobertura en diccionario |
|---|---|
| I162S2C13J1V1 | COD_CARRERA 13 ausente en bloque raw |
| I162S2C13J2V1 | COD_CARRERA 13 ausente en bloque raw |
| I162S2C21J1V1 | COD_CARRERA 21 ausente en bloque raw |
| I162S2C21J2V1 | COD_CARRERA 21 ausente en bloque raw |
| I162S2C23J1V1 | COD_CARRERA 23 ausente en bloque raw |
| I162S2C23J2V1 | COD_CARRERA 23 ausente en bloque raw |
| I162S2C24J1V1 | COD_CARRERA 24 ausente en bloque raw |
| I162S2C24J2V1 | COD_CARRERA 24 ausente en bloque raw |
| I162S2C3J2V2 | COD_CARRERA 3 presente, pero no existe combinación exacta; disponibles: I162S2C3J1V1, I162S2C3J1V2, I162S2C3J2V1, I162S2C3J2V3, I162S2C3J2V4, I162S2C3J4V2, I162S2C3J4V3 |
| I162S2C41J2V1 | COD_CARRERA 41 ausente en bloque raw |
| I162S2C6J4V1 | COD_CARRERA 6 presente, pero no existe combinación exacta; disponibles: I162S2C6J1V1, I162S2C6J1V2, I162S2C6J2V1, I162S2C6J2V2, I162S2C6J4V2 |

## Campos completados por diccionario

ANIO_INICIO=60, REGIMEN=60, DURACION_REGIMEN=60, NOMBRE_TITULO=60, ACREDITACION=60, REQUISITO_INGRESO=60, SEMESTRES_RECONOCIDOS=60, AREA_ACTUAL=60, AREA_ADMIN_DERECHO=60, AREA_AGRI_SILVI_PESCA_VET=60, AREA_ARTES_HUMANIDADES=60, AREA_CIENCIAS_NAT_MAT_ESTAD=60, AREA_CS_SOCIAL_PERIODISMO_INFO=60, AREA_EDUCACION=60, AREA_INGE_INDUSTRIA_CONSTRUC=60, AREA_SALUD_BIENESTAR=60, AREA_SERVICIOS=60, AREA_TECNO_INFO_COMUNICA=60, VACANTES_PRIMER_SEMESTRE=60, VACANTES_SEGUNDO_SEMESTRE=60

## Campos que quedan en REVISAR

FECHA_ADMISION_INICIAL, MALLA_CURRICULAR, PERFIL_EGRESO, TEXTO_REQUISITO_INGRESO, LICENCIA_ENS_MEDIA, NOTAS_ENS_MEDIA, PROMEDIO_MIN_ENS_MEDIA, RECONOCIMIENTOS_APREN_PREVIOS, EXPERIENCIA_LABORAL, OTROS_REQUISITOS, MAIL_DIFUSION_CARRERA, FORMATO_VALOR, VALOR_MATRICULA_ANUAL, COSTO_TITULACION, VALOR_CERTIFICADO_DIPLOMA, ARANCEL_ANUAL, VIGENCIA_CARRERA

## Revisión uno a uno de los 79 programas

| HOJA_ORIGEN                     |   ROW_ORIGEN | CODIGO_UNICO   | MATCH_STATUS   | MATCH_METHOD           | MATCH_KEY                                                  |   MATCH_COUNT | MATCH_CODIGO_UNICO_DERIVADO   |
|:--------------------------------|-------------:|:---------------|:---------------|:-----------------------|:-----------------------------------------------------------|--------------:|:------------------------------|
| PROGRAMAS_FALTANTES_PARA_CREAR  |            2 | I162S2C101J4V1 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C101J4V1                                             |             1 | I162S2C101J4V1                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |            3 | I162S2C102J4V1 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C102J4V1                                             |             1 | I162S2C102J4V1                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |            4 | I162S2C103J4V1 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C103J4V1                                             |             1 | I162S2C103J4V1                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |            5 | I162S2C104J4V1 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C104J4V1                                             |             1 | I162S2C104J4V1                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |            6 | I162S2C105J4V1 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C105J4V1                                             |             1 | I162S2C105J4V1                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |            7 | I162S2C10J1V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C10J1V1                                              |             1 | I162S2C10J1V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |            8 | I162S2C10J4V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C10J4V1                                              |             1 | I162S2C10J4V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |            9 | I162S2C111J4V1 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C111J4V1                                             |             1 | I162S2C111J4V1                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           10 | I162S2C111J4V2 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C111J4V2                                             |             1 | I162S2C111J4V2                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           11 | I162S2C112J4V1 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C112J4V1                                             |             1 | I162S2C112J4V1                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           12 | I162S2C112J4V2 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C112J4V2                                             |             1 | I162S2C112J4V2                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           13 | I162S2C113J4V1 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C113J4V1                                             |             1 | I162S2C113J4V1                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           14 | I162S2C113J4V2 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C113J4V2                                             |             1 | I162S2C113J4V2                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           15 | I162S2C114J2V1 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C114J2V1                                             |             1 | I162S2C114J2V1                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           16 | I162S2C115J2V1 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C115J2V1                                             |             1 | I162S2C115J2V1                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           17 | I162S2C116J4V1 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C116J4V1                                             |             1 | I162S2C116J4V1                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           18 | I162S2C117J4V1 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C117J4V1                                             |             1 | I162S2C117J4V1                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           19 | I162S2C118J4V1 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C118J4V1                                             |             1 | I162S2C118J4V1                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           20 | I162S2C119J4V1 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C119J4V1                                             |             1 | I162S2C119J4V1                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           21 | I162S2C124J4V1 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C124J4V1                                             |             1 | I162S2C124J4V1                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           22 | I162S2C124J4V2 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C124J4V2                                             |             1 | I162S2C124J4V2                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           23 | I162S2C125J4V1 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C125J4V1                                             |             1 | I162S2C125J4V1                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           24 | I162S2C125J4V2 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C125J4V2                                             |             1 | I162S2C125J4V2                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           25 | I162S2C13J1V1  | SIN_MATCH      | SIN_MATCH              | ||1|||1|1                                                  |             0 |                               |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           26 | I162S2C13J2V1  | SIN_MATCH      | SIN_MATCH              | ||2|||1|1                                                  |             0 |                               |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           27 | I162S2C1J2V2   | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C1J2V2                                               |             1 | I162S2C1J2V2                  |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           28 | I162S2C1J4V3   | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C1J4V3                                               |             1 | I162S2C1J4V3                  |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           29 | I162S2C21J1V1  | SIN_MATCH      | SIN_MATCH              | ||1|||1|2                                                  |             0 |                               |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           30 | I162S2C21J2V1  | SIN_MATCH      | SIN_MATCH              | ||2|||1|2                                                  |             0 |                               |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           31 | I162S2C23J1V1  | SIN_MATCH      | SIN_MATCH              | ||1|||1|2                                                  |             0 |                               |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           32 | I162S2C23J2V1  | SIN_MATCH      | SIN_MATCH              | ||2|||1|2                                                  |             0 |                               |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           33 | I162S2C24J1V1  | SIN_MATCH      | SIN_MATCH              | ||1|||1|1                                                  |             0 |                               |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           34 | I162S2C24J2V1  | SIN_MATCH      | SIN_MATCH              | ||2|||1|1                                                  |             0 |                               |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           35 | I162S2C2J1V2   | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C2J1V2                                               |             1 | I162S2C2J1V2                  |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           36 | I162S2C2J2V2   | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C2J2V2                                               |             1 | I162S2C2J2V2                  |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           37 | I162S2C2J4V2   | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C2J4V2                                               |             1 | I162S2C2J4V2                  |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           38 | I162S2C35J1V2  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C35J1V2                                              |             1 | I162S2C35J1V2                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           39 | I162S2C35J2V2  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C35J2V2                                              |             1 | I162S2C35J2V2                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           40 | I162S2C35J4V2  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C35J4V2                                              |             1 | I162S2C35J4V2                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           41 | I162S2C3J2V2   | SIN_MATCH      | SIN_MATCH              | ||2|||1|2                                                  |             0 |                               |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           42 | I162S2C40J2V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C40J2V1                                              |             1 | I162S2C40J2V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           43 | I162S2C41J2V1  | SIN_MATCH      | SIN_MATCH              | ||2|||3|5                                                  |             0 |                               |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           44 | I162S2C53J3V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C53J3V1                                              |             1 | I162S2C53J3V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           45 | I162S2C63J4V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C63J4V1                                              |             1 | I162S2C63J4V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           46 | I162S2C64J4V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C64J4V1                                              |             1 | I162S2C64J4V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           47 | I162S2C65J4V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C65J4V1                                              |             1 | I162S2C65J4V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           48 | I162S2C66J4V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C66J4V1                                              |             1 | I162S2C66J4V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           49 | I162S2C67J4V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C67J4V1                                              |             1 | I162S2C67J4V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           50 | I162S2C68J4V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C68J4V1                                              |             1 | I162S2C68J4V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           51 | I162S2C69J4V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C69J4V1                                              |             1 | I162S2C69J4V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           52 | I162S2C6J1V1   | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C6J1V1                                               |             1 | I162S2C6J1V1                  |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           53 | I162S2C6J2V1   | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C6J2V1                                               |             1 | I162S2C6J2V1                  |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           54 | I162S2C6J4V1   | SIN_MATCH      | SIN_MATCH              | ||4|||1|1                                                  |             0 |                               |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           55 | I162S2C70J4V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C70J4V1                                              |             1 | I162S2C70J4V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           56 | I162S2C71J4V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C71J4V1                                              |             1 | I162S2C71J4V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           57 | I162S2C76J4V2  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C76J4V2                                              |             1 | I162S2C76J4V2                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           58 | I162S2C77J4V2  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C77J4V2                                              |             1 | I162S2C77J4V2                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           59 | I162S2C83J4V2  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C83J4V2                                              |             1 | I162S2C83J4V2                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           60 | I162S2C86J4V2  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C86J4V2                                              |             1 | I162S2C86J4V2                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           61 | I162S2C87J4V2  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C87J4V2                                              |             1 | I162S2C87J4V2                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           62 | I162S2C88J4V2  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C88J4V2                                              |             1 | I162S2C88J4V2                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           63 | I162S2C90J2V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C90J2V1                                              |             1 | I162S2C90J2V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           64 | I162S2C90J2V2  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C90J2V2                                              |             1 | I162S2C90J2V2                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           65 | I162S2C95J4V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C95J4V1                                              |             1 | I162S2C95J4V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           66 | I162S2C96J4V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C96J4V1                                              |             1 | I162S2C96J4V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           67 | I162S2C97J4V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C97J4V1                                              |             1 | I162S2C97J4V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           68 | I162S2C98J4V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C98J4V1                                              |             1 | I162S2C98J4V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           69 | I162S2C99J4V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C99J4V1                                              |             1 | I162S2C99J4V1                 |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           70 | I162S3C114J2V1 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S3C114J2V1                                             |             1 | I162S3C114J2V1                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           71 | I162S3C115J2V1 | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S3C115J2V1                                             |             1 | I162S3C115J2V1                |
| PROGRAMAS_FALTANTES_PARA_CREAR  |           72 | I162S3C91J2V1  | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S3C91J2V1                                              |             1 | I162S3C91J2V1                 |
| NO_CREAR_CUBIERTO               |            2 | I162S2C3J1V1   | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C3J1V1                                               |             1 | I162S2C3J1V1                  |
| NO_CREAR_CUBIERTO               |            3 | I162S2C3J2V1   | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C3J2V1                                               |             1 | I162S2C3J2V1                  |
| REQUIERE_DECISION_INSTITUCIONAL |            2 | I162S2C1J4V1   | MATCH_AMBIGUO  | P4_NOMBRE_SEDE_JORNADA | INGENIERIA EN INFORMATICA|CASA CENTRAL SANTIAGO|4          |             2 | I162S2C1J4V2|I162S2C1J4V3     |
| REQUIERE_DECISION_INSTITUCIONAL |            3 | I162S2C3J4V1   | MATCH_AMBIGUO  | P4_NOMBRE_SEDE_JORNADA | INGENIERIA EN CONECTIVIDAD Y REDES|CASA CENTRAL SANTIAGO|4 |             2 | I162S2C3J4V2|I162S2C3J4V3     |
| DUDOSOS_REV_MANUAL_RESUELTOS    |            2 | I162S2C1J4V1   | MATCH_AMBIGUO  | P4_NOMBRE_SEDE_JORNADA | INGENIERIA EN INFORMATICA|CASA CENTRAL SANTIAGO|4          |             2 | I162S2C1J4V2|I162S2C1J4V3     |
| DUDOSOS_REV_MANUAL_RESUELTOS    |            3 | I162S2C3J1V1   | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C3J1V1                                               |             1 | I162S2C3J1V1                  |
| DUDOSOS_REV_MANUAL_RESUELTOS    |            4 | I162S2C3J2V1   | MATCH_UNICO    | P1_CODIGO_UNICO_EXACTO | I162S2C3J2V1                                               |             1 | I162S2C3J2V1                  |
| DUDOSOS_REV_MANUAL_RESUELTOS    |            5 | I162S2C3J4V1   | MATCH_AMBIGUO  | P4_NOMBRE_SEDE_JORNADA | INGENIERIA EN CONECTIVIDAD Y REDES|CASA CENTRAL SANTIAGO|4 |             2 | I162S2C3J4V2|I162S2C3J4V3     |

## Validaciones técnicas

- Raw validado con 34 columnas por fila: OK
- Columnas A:AY creadas: OK
- Columnas AI:AY sin datos inventados: OK
- Archivo operativo seguro intacto por hash: OK
- Archivo problemático no usado e intacto por hash: OK
- Total control 79: OK
- OOXML válido y abre con openpyxl: OK
- Sin fórmulas, macros, vínculos externos, conexiones, dibujos, gráficos ni validaciones: OK
- CSV final de carga no generado por falta de confirmación explícita sobre COD_CARRERA en blanco para Oferta Académica Nueva TP: OK conservador

## Estado Git final

### git status --short

```text
?? indices_2025/cned/resultados/CNED_CONCILIACION_OFERTA_DICCIONARIO_79_PROGRAMAS_20260604_104613.md
```

### git status

```text
On branch clean/pes-ready-final
Your branch and 'origin/clean/pes-ready-final' have diverged,
and have 1 and 1 different commits each, respectively.
  (use "git pull" if you want to integrate the remote branch with yours)

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	indices_2025/cned/resultados/CNED_CONCILIACION_OFERTA_DICCIONARIO_79_PROGRAMAS_20260604_104613.md

nothing added to commit but untracked files present (use "git add" to track)
```

### git branch -vv

```text
backup/antes_limpieza_pes_ready_20260507        e790958 docs: close MU2026 PES_READY validation
  backup/pre-align-clean-pes-ready-final-20260603 8d24713 feat: materialize clean CNED operational artifact
  backup/pre-sync-fix-20260410-avance             d9c0e32 MU2026: agregar auditoría de activación gitignore DURACION
  backup/pre_cierre_pes_ready_20260507_134145     1d07eb8 test: add optional MU2026 cross-validation fixture
  backup/rebase_fallido_pes_ready_20260507        3dd107a chore: remove generated MU2026 audit artifacts
  clean/pes-ready                                 1d07eb8 [origin/main: ahead 1, behind 1] test: add optional MU2026 cross-validation fixture
* clean/pes-ready-final                           ccb0259 [origin/clean/pes-ready-final: ahead 1, behind 1] fix: canonicalize clean CNED materializer script
  fix/fase4-y-z                                   649ba4d [origin/fix/fase4-y-z: behind 6] MU2026 aprobado: gate final 32 OK 0 pendientes
  main                                            3dd107a [origin/main: ahead 4, behind 1] chore: remove generated MU2026 audit artifacts
```

### git log --oneline --left-right HEAD...origin/clean/pes-ready-final

```text
< ccb0259 fix: canonicalize clean CNED materializer script
> 4caf70b fix: canonicalize clean CNED materializer script
```

## Dictamen final

`DICTAMEN_FINAL: ERROR_EN_CONCILIACION_DICCIONARIO_OFERTA`
