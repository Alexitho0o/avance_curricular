# H005c · Coherencia de tipo de plan SIES–UMAS

30-10-2026 · Rama feature/ire-2026 · base 430c7d4. Sin commit ni push. Se parte de H005; no se reconstruyen enlaces, paridades ni bases.

## Entrega y alcance

- Libro: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/excel_resumen_cruce_20261030/RESUMEN_CRUCE_SIES_UMAS_20261030.xlsx`.
- Copia idéntica: `/Users/alexi/Desktop/ENTREGA_RETENCION_20261031/RESUMEN_CRUCE_SIES_UMAS_20261030.xlsx`.
- SHA-256: `95550f580ad0c44e464f5a142d46f2d25ad6cfb4740104405222d09984f135be`.
- Cinco hojas, 26 tablas con autofiltro, paneles congelados y un gráfico editable de columnas agrupadas. Arial disponible; sustitución de Montserrat declarada.
- Se conservan las 25.318 comprobaciones de H005, localizadas por bloque/registro/campo después de renumerar hojas. El control vigente totaliza 34.960 comprobaciones. Fuera de los bloques reclasificados se conservan los valores de H005b.

## Oferta y matrícula

| Medida | Total | 2026 | Fuente |
| --- | ---: | ---: | --- |
| EN_OFERTA (vigencia 1 o 2; 2010–2026) | 139 | 124 | MAESTRO/oferta_anual |
| CON_MATRICULA (matrícula positiva; 2007–2026) | 106 | 66 | PUBLICA |

EN_OFERTA: 117 códigos de pregrado y 22 de postítulo; coincide con la referencia. CON_MATRICULA histórica: 98 pregrado y 8 postítulo/otro. No se confunden ambos universos. La oferta incluye versiones sin alumnos, códigos solo para antiguos y diplomados sin matrícula. Oferta 2007–2009 queda E, no cero.

Hay 9 códigos presentes únicamente en oferta histórica, fuera de los 169 del detalle H005. Están en el nuevo detalle completo de 139 códigos de oferta (hoja 2, A200); no se altera el universo previo ni se crean paridades. `n.a.` en una vigencia anual significa no observado en esa extracción, no cierre.

## Versiones y cambios de atributos

| Clasificación de 21 familias | Historia conocida 2007–2026 | Última observación de cada código |
| --- | ---: | ---: |
| VERSIONES_POR_DURACION_O_TIPO | 17 | 11 |
| VERSIONES_ATRIBUTOS_IDENTICOS | 4 | 10 |

La clasificación principal conserva todos los valores conocidos; los vacíos no se consideran cambios. La segunda columna de contraste usa solo la última observación y no reemplaza la historia. Las duraciones del detalle indican su año de referencia.

Diferencia con 15/6 de Claude: C1J4 y C3J4 contienen V3 de continuidad de cuatro semestres y versiones regulares de ocho; por tanto no son familias de atributos idénticos. Las cuatro idénticas son: I162S2C2J4, I162S2C35J1, I162S2C35J2, I162S2C6J4.

Nueve códigos cambian atributos entre años (coincide con la referencia): I162S2C1J1V1, I162S2C1J2V1, I162S2C2J1V1, I162S2C2J2V1, I162S2C35J4V1, I162S2C3J1V1, I162S2C3J2V1, I162S2C6J1V1, I162S2C6J2V1. El detalle de valores y años está en ATRIBUTOS_VERSIONES_H005B.json y en la hoja 3, S12. C35J4V1 pasa de cinco a seis semestres.

Criterio A: Instructivo Oferta Académica–Acceso CFT-IP 2027, líneas 240–248 y 2333–2337, exige nueva versión ante cambio de duración, tipo, nivel o modalidad. Su aplicación retrospectiva no acredita por sí sola un error de una carga histórica; el dato observado es B y su causa permanece E.

## Coherencia de tipo por año (H005c)

Se reutilizan las matrículas-año enlazadas de MATRIZ_PARIDAD_COHORTE, origen MU_DATOS_ALUMNOS. El tipo de cada plan procede del catálogo v2; el tipo de la versión informada procede de MAESTRO/oferta_anual del mismo código y año. No se usa el código esperado de H002j para decidir si el tipo informado es correcto. No se recalculan enlaces, paridades ni trayectorias individuales.

A: criterio de versiones del instructivo citado. B: tipos y conteos observados. C: contraste de catálogos. E: plan sin tipo determinado o no observado. La etiqueta ERROR_DE_CARGA_SEGUN_MANUAL expresa el cruce de tipo; no modifica ni certifica retrospectivamente la carga.

| Año | CORRECTO_SEGUN_MANUAL | ERROR_DE_CARGA_SEGUN_MANUAL | NO_EVALUABLE | Matrículas MU enlazadas |
| --- | ---: | ---: | ---: | ---: |
| 2022 | 812 | 0 | 176 | 988 |
| 2023 | 929 | 0 | 177 | 1106 |
| 2024 | 1129 | 133 | 111 | 1373 |
| 2025 | 1929 | 171 | 124 | 2224 |
| 2026 | 2908 | 0 | 215 | 3123 |

Cada fila suma exactamente las matrículas enlazadas del año. La tabla completa REGULAR/CONTINUIDAD/E/SIN_PLAN × REGULAR/CONTINUIDAD está en COHERENCIA_TIPO_H005C.json y en la hoja 5, AO67. Los cruces por plan y código están en AU55.

2024: 131 continuidad→regular (CICRE 59, CICIB 44, CIINF 28) y 2 regular→continuidad. 2025: 171 continuidad→regular (CICRE 71, CICIB 54, CIINF 42, CILOG 3, CIADM 1). 2026: cero cruces de tipo entre planes evaluables.

En 2024–2025 los planes de continuidad CICRE, CICIB y CIINF aparecen informados en códigos regulares. En 2026, sus planes observados están íntegramente en versiones de continuidad; un registro CICRE sin plan observado permanece NO_EVALUABLE. Los cambios hacia continuidad son compatibles con correcciones de tipo, no con nuevas inconsistencias. La comparación agregada no prueba por sí sola el traslado individual. CICIB utiliza V3 regular→V1 de continuidad; no se generaliza V2→V3 a todas las familias.

## Reclasificación del universo original de 253

Se conservan los 34 grupos y las 253 matrículas-año de H002m. Son un subconjunto diagnóstico distinto del universo anual completo, que presenta 304 cruces de tipo. La etiqueta anterior queda en una columna de trazabilidad; CLASIFICACION_253_H005B.json se conserva intacto como antecedente superado.

| Estado corregido | Matrículas-año |
| --- | ---: |
| CORRECTO_TRASLADO_A_CONTINUIDAD | 210 |
| VERSION_POR_PLAN_O_ANIO | 36 |
| ERROR_DE_CARGA_SEGUN_MANUAL | 5 |
| NO_EVALUABLE | 2 |
| Total | 253 |

Los 210 antes SIN_EXPLICACION tienen tipo de continuidad concordante. Otros 10 regulares se confirman con oferta_anual, aunque faltara una fila pública comparativa en H005b. Dos casos antes VERSION_POR_PLAN_O_ANIO pasan a NO_EVALUABLE: IECIREOL20201 e IECIREOL, tipo E en v2. Así, 28 + 10 − 2 = 36. VERSION_POR_PLAN_O_ANIO es una etiqueta descriptiva del reparto regular/regular; no acredita su causa individual. No queda SIN_EXPLICACION como estado vigente.

## QA

- PASS: 34.960 comprobaciones, cero diferencias no autorizadas. Las 25.318 originales de H005 siguen sin diferencias. De las 34.510 de H005b, se conservan 34.294 y se revisan explícitamente 216 controles de clasificación.
- Comparación completa de celdas: 166 celdas modificadas y 473 añadidas. Cada celda modificada figura con coordenada, valor anterior y nuevo en CAMBIOS_CELDAS_H005C.md/.json, incluidas las diferencias de resultado en fórmulas cuyo texto no cambió. Solo cambia el bloque autorizado de clasificación; no hay diferencias fuera de él.
- 113 fórmulas recalculadas con LibreOffice, cero errores. Tablas y gráfico preservados.
- Apertura final en Microsoft Excel: cinco hojas, sin aviso de reparación; cierre sin guardar.
- Revisión visual de los nuevos PNG de resumen, tipos, cruces y trazabilidad: legibles y con formato chileno.
- Privacidad: solo catálogos y conteos; escaneo de celdas y archivos textuales sin identificadores personales ni contactos.
- Reproducción idéntica del modelo, controles y agregados; 20 fuentes verificadas por SHA-256.
- 24 cambios ajenos y 5.016 archivos preexistentes conservados. H002, v20, regla activa, fuentes y bases intactos. R21 actualizada; demás resultados del mapa intactos.
- Libro y copia del Escritorio idénticos por SHA-256. Sin commit ni push.

## PNG

- Resumen de coherencia anual: `renders/5_Cruce_SIES_UMAS_6.png`.
- Tabla por tipos: `renders/5_Cruce_SIES_UMAS_7.png`.
- Cruces por plan y código: `renders/5_Cruce_SIES_UMAS_8.png`.
- Reclasificación de 253: `renders/5_Cruce_SIES_UMAS_5.png`.
- Trazabilidad anterior/nueva: `renders/5_Cruce_SIES_UMAS_9.png`.

## Fuentes por hash

| ID | Ruta | SHA-256 | Clase |
| --- | --- | --- | --- |
| PUBLICA | /Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/publicacion_fechafirma_20261022/gobernanza/sies/Matricula_2007_2026_WEB_10_07_2026.csv | 4c630e05e07312ebd567ed77b0c26c5d0230380deea4fc89a6123b11b7aba154 | B |
| H002 | /Users/alexi/Documents/GitHub/avance_curricular/data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json | 0ed5e17b1a452c85ab25b08ef0e65cdfc7258fd920d0f4dd40c60c9c4eb71063 | C/D |
| MAESTRO | /Users/alexi/Documents/GitHub/avance_curricular/data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json | 2ef459251e91ecebe5370402e3d2ea25341aeecbfb3ca54eca210cc347c392a5 | B/C/E |
| MATRIZ | /Users/alexi/Documents/GitHub/avance_curricular/data/paridad_codigo_sies/cohorte_2007_2026/MATRIZ_PARIDAD_COHORTE.csv | 44c2c12a37a0f8d552e8a4b93759d09cc4a66babe996218c72d2a64962a481fe | B/C/E |
| RESULTADOS | /Users/alexi/Documents/GitHub/avance_curricular/outputs/paridad_cohorte_2007_2026/RESULTADOS.json | ee11647f6a2a6e00696334f0a2cbc2ed41034aa93f137ab6ad217862dde645d4 | B/C |
| CONTROL_SIES | /Users/alexi/Documents/GitHub/avance_curricular/outputs/paridad_cohorte_2007_2026/CONTROL_SIES_PUBLICACION.json | da1adb185e4294e41dcb4a8b93d3e0be8cb2eaf08f7f96bca8ad39f0263ad40e | B/C |
| PRIMER_ANIO | /Users/alexi/Documents/GitHub/avance_curricular/data/paridad_codigo_sies/cohorte_2007_2026/PRIMER_ANIO_POR_FAMILIA.csv | 3b2f1020f3800db6840c4b99951a092ac265f1f9f94fe4a4f4752c5e80807ef4 | B/C |
| TIPOS_V2 | /Users/alexi/Documents/GitHub/avance_curricular/data/paridad_codigo_sies/regla_operativa_mu_v2/TIPO_PLAN_POR_PLAN_UMAS.csv | 065716db537fe9f67935235df293802005f33d5f7eb60a6f85d9b67c12a84e95 | C |
| TIPOS_V3 | /Users/alexi/Documents/GitHub/avance_curricular/data/paridad_codigo_sies/regla_operativa_mu_v3/TIPO_PLAN_POR_PLAN_UMAS_v3.csv | 4e33b83fd1079545a17dd7508694fee82ad438e025438ca02743ac209dbcc0cc | C/E CANDIDATO |
| PERFILES | /Users/alexi/Documents/GitHub/avance_curricular/outputs/paridad_codigo_sies_20261029/PERFIL_PLANES_H002C.json | 56bdc927d8098319fce1ddb5c82c4fe6bf39988666ecf9328036bc108810bcd9 | B/C/E |
| DICCIONARIO_UMAS | /Users/alexi/Documents/GitHub/avance_curricular/data/diccionario_umas/DICCIONARIO_UMAS.json | f05ac03aa8ca0ec6cf5f754cbaacebac630b2a3346ff592d7ee0b181b82e8811 | B/C/E |
| MALLAS | /Users/alexi/Documents/GitHub/avance_curricular/data/diccionario_umas/COMPROBACION_MALLAS.json | 2d13dd9123f839343f4ff6b41ce931e7c72a54a90a81390197fed379c92cdc0c | B/C/E |
| REGLA | /Users/alexi/Documents/GitHub/avance_curricular/data/reglas_negocio/mu2027/REGLA_CODIGO_SIES_MU2027.json | 197fe68f1a7a24ab6a7ed844e4cefbdcf8774d655acc33ad49886aaadc8b90f2 | D ACTIVA |
| CIERRE | /Users/alexi/Documents/GitHub/avance_curricular/data/paridad_codigo_sies/cierre_historico_2007_2021/README.md | cddd0f2dad9abe85dd5bf64b284030129dba341e55a7e38f5f846d7352242645 | D/E |
| TECHO | /Users/alexi/Documents/GitHub/avance_curricular/manifests/milestones/H002-PARIDAD-CODIGO-SIES-2027/TECHO_ALCANZADO.md | 60528910ee02f96e18ece8e064d4a0b1fe2f2341f5cbc5393d7144de355dd872 | D/E |
| PALETA | /Users/alexi/Documents/GitHub/CARACTERIZACIÓN/gobernanza/marca/paleta_ipss_2026.json | eaf142973cb8b28b4919cd156612587b0d811f94c3e3c41a4f480a1ef4828c26 | A/C |
| LISTADO_AC | /Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Avance Curricular/2026/Listado_Planes_estudio_Sedes RE+CO.xlsx | fb3a6847dca0745a197867090a9d7d12e8bb7e53e6b421f96826ea0c5657d049 | B; solo hash, perfiles agregados reutilizados |
| DIAG253 | /Users/alexi/Documents/GitHub/avance_curricular/outputs/regla_operativa_mu_v3_20261029/DIAGNOSTICO_253.json | 9c4f4e8b8be749dd57641a02d6c1d6c4271d08b61a6f0445f17df659bcb3d06d | C/E |
| MANUAL_OFERTA2027 | /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/01_fuentes_oficiales/Instructivo_Oferta_Academica-Acceso_CFT-IP 2027.txt | 27095d34a42c37f23a875f925204fc99d03e53fa9011d66480167f834b790c7e | A |
| LIMITES_VERSION | /Users/alexi/Documents/GitHub/avance_curricular/docs/unificacion_proyectos_y_reglas_negocio_20261015.md | ef7d47f940f46045fc1c179642fd76807b8f3c876f03b1c1bc680271434a3d53 | A/C/E |
