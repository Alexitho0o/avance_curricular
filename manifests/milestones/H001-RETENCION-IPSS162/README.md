# H001-RETENCION-IPSS162

## Objetivo

Dejar gobernado y trazable el cálculo de retención de primer año de IPSS, código SIES 162, con comparación agregada contra SIES y reconciliación interna granular 2022–2024.

## Alcance

Libro de retención de cohortes 2022–2025, fuentes SIES congeladas, fuente interna previa identificada correctamente como autoría de Alexi Marcelo Burgos Flores, y trazabilidad de hashes, fórmulas y limitaciones metodológicas.

## Entradas

- Base RAW de matrícula unificada informada a SIES 2022–2026.
- Catálogo de duración y elegibilidad de carreras.
- `Informe_Retencion_SIES_2026_270702026.xlsx`, fuente SIES agregada.
- `RETENCION_SIES_IPSS_162_GRANULAR_2025_CORREO_20260909.tsv`, tabla granular entregada por Rodrigo Rolando Meneses.
- `Retencion_ipss_2022_2024_GRANULAR.xlsx`, cálculo interno previo del usuario, no fuente SIES.
- `Informe_Retencion_1er_Anio_Pregrado_2026.pdf`, informe SIES agregado y metodológico.

## Salidas

- `outputs/retencion_primer_anio_ipss_162/20260928_231500/RETENCION_PRIMER_ANIO_IPSS_162_CORREGIDO_20260928_231500.xlsx`.
- Fuentes congeladas en `CARACTERIZACIÓN/gobernanza/sies/RETENCION/`.

## Archivos tocados

- Libro final de retención en `outputs/retencion_primer_anio_ipss_162/20260928_231500/`.
- Fuentes y manifiestos de `CARACTERIZACIÓN/gobernanza/sies/RETENCION/`.
- Este registro de hito.

## Validaciones

- Manifiestos JSON válidos.
- Archivos XLSX gobernados íntegros como ZIP.
- Libro final con 15 hojas.
- Cero errores de fórmula después del recálculo.
- Hash SIES congelado verificado: `168ac8baea6aee65fa8a40dfca5a269993951142c89cb536805f550b1ac3297b`.
- Snapshot SIES equivalente verificado: `03897a1604aa656f9ff60e232eda739e29f4912123e5d7127d6551a37957a8a1`.

## Resultado

**OK**.

## Evidencias

- Libro final anterior: SHA-256 `52ad47d73bf3f6a9bdcb7b0e10bdfa2cfc97ae614376ed2f32b78d8898fb4624` (superada por la versión con diagnóstico incorporado, mismo contenido salvo la sección nueva de la hoja 04).
- Libro actualizado con diagnóstico: `outputs/retencion_primer_anio_ipss_162/20260929_015725/RETENCION_PRIMER_ANIO_IPSS_162_DIAGNOSTICO_20260929_015725.xlsx`; SHA-256 `d6a014da616e7f8307def42bcbc5e54f996d0b29f135b406b18ddfdd9ba62e81`.
- Fuente interna previa: SHA-256 `e85d8c15c9fa2eccb25a376ea352f345ddcec91dbcf8176070b1ae3490c5d946`.
- Informe SIES congelado: SHA-256 `168ac8baea6aee65fa8a40dfca5a269993951142c89cb536805f550b1ac3297b`.
- Diagnóstico de brechas 2022 y 2024: pendiente de adjuntar como archivo independiente; los hallazgos quedan documentados en la sección siguiente.

## Pendientes

- Queda abierto solicitar directamente a SIES el granular 2022–2024 si se desea reemplazar la comparación interna por datos publicados equivalentes a 2025.
- La causa de los 76 casos `VIG=0` de 2024 permanece sin confirmar.
- La diferencia de 61 registros entre la RAW 2022 y la fuente histórica gobernada permanece sin explicación causal confirmada.
- No existe una llave gobernada RUT↔MRUN para ejecutar el cruce individual solicitado.

## Deuda técnica

La comparación granular 2022–2024 es interna, no SIES; está identificada en la hoja `13_CRUCE_GRANULAR_2022_2024`. La fecha exacta de corte al 30 de abril no es verificable para 2022–2023 porque el esquema consolidado no contiene `FECHA_MATRICULA`; se usa `VIG` como proxy.

## Siguiente paso

Solicitar a SIES, si se requiere, el desglose oficial por `CODIGO_UNICO` para las cohortes 2022–2024 y sustituir la comparación interna manteniendo la trazabilidad existente.

## Diagnóstico de brechas 2022 y 2024

### Regla oficial aplicada — clasificación A

El correo de Rodrigo Rolando Meneses (MINEDUC/SIES) a Karla Muñoz Gajardo (IPSS), de 9-sep-2026, define la retención como la permanencia en la misma institución y en la misma generación o cohorte de origen entre un año y el siguiente. La elegibilidad considera programas regulares desde 4 semestres para carreras técnicas, bachillerato, ciclo inicial o plan común; desde 6 semestres para carreras profesionales sin licenciatura; y desde 8 semestres para carreras profesionales con licenciatura o licenciaturas no conducentes a título. Excluye programas especiales, casos específicos con inconsistencias de cohorte de origen y categorías con menos de 10 casos de cohorte. La fecha de referencia es el 30 de abril de cada año.

### VIG=0 en la cohorte 2024 — clasificación B/E

En el RAW `08-05-2024_18-31-54_Matrícula_Pregrado_2024.csv`, filtrando `ANIO_ING_ORI=2024`, `SEM_ING_ORI=1`, `ANIO_INFORMADO=2024` y `VIG=0`, se observaron 76 registros. Los 76 tienen `COD_SED=2`, `FECH_CAR=06-05-2024 15:44`, `NIVEL=1`, `NIVEL 2=NUEVO` y `COD_NIV_GLO=1`. Se concentran en jornada 4/modalidad 3 (54 de 76), pero se distribuyen entre 11 carreras. Ninguno aparece vigente en 2025 con la misma cohorte de origen.

El patrón de lote único y sede única es un dato observado (B). No existe evidencia suficiente para determinar si `VIG=0` refleja una baja real, una exclusión administrativa o un defecto de codificación del lote. La causa queda sin resolver (E).

### Cruce independiente de la cohorte 2022 — clasificación B/E

La RAW 2022 `2022/2022.csv` contiene 1.038 filas y 310 registros con `ANIO_ING_ORI=2022`. La fuente gobernada `CARACTERIZACIÓN/gobernanza/carga_postgrado/datos_sensibles/reporte_matricula_ip_san_sebastian.csv` contiene 20.961 filas. Aplicando `cat_periodo=2022`, `anio_ing_carr_ori=2022`, `sem_ing_carr_ori=1`, `nivel_global=Pregrado` y `tipo_plan_carr=Plan Regular`, se obtienen 249 registros, frente a los 310 candidatos de `BASE_RETENCION_MU`: diferencia de 61 registros, equivalente a 19,7% del universo RAW.

El total sin filtrar de la fuente independiente para `cat_periodo=2022` es 1.033, cercano a las 1.038 filas RAW. Esto descarta que la RAW 2022 esté evidentemente truncada solo por su conteo total, pero no explica la diferencia de 61 candidatos después de los filtros. La diferencia causal queda sin confirmar (E); permanece como hipótesis una diferencia de cobertura o de clasificación del año de cohorte (E).

### Estado de las brechas — clasificación E

La brecha 2022 de aproximadamente +4,49 puntos porcentuales y la brecha 2024 de aproximadamente −9,08 puntos porcentuales permanecen como hipótesis no resueltas (E). Los resultados 2023 y 2025 no aportan evidencia suficiente para explicar esas diferencias.

### Llave de cruce individual — clasificación B/E

La RAW institucional identifica personas mediante `TIPO_DOC + N_DOC + DV`, mientras que el extracto histórico utiliza `mrun`. La revisión de los repositorios gobernados, incluida `gobernanza/trazabilidad_mrun/F0_DIAGNOSTICO_FACTIBILIDAD.md`, no encontró una tabla gobernada RUT↔MRUN que demuestre comparabilidad persona a persona. Un diagnóstico de factibilidad previo (16-sep-2026, sobre el cruce RUT interno U+ ↔ MRUN SIES) encontró que el bloqueo determinístico simple deja como máximo ~50% de la población con un match único confiable, y ese máximo solo aplica a la mitad de las personas evaluadas; concluye que la relación RUT↔MRUN no debe reconstruirse post-hoc. Esto refuerza, sin ser prueba directa sobre esta cohorte, que el cruce individual solicitado no cuenta con una llave gobernada confiable (B). Por tanto, no existe llave de cruce directa; el cruce determinístico individual no es posible con las fuentes actualmente gobernadas (B/E). No se realizó aproximación por nombre, fecha de nacimiento ni sexo.

## Decisión de fuente principal de matrícula por carrera — clasificación D

Desde el 29-sep-2026, la fuente principal para cruces y análisis de matrícula por carrera es `Matricula_2007_2026_WEB_10_07_2026.csv`, registrada en `CARACTERIZACIÓN/gobernanza/sies/MATRICULA_2007_2026.manifest.json`. La decisión se adopta porque el archivo cubre `MAT_2007`–`MAT_2026`, tiene grano institución-carrera-sede-jornada-año y contiene dimensiones adicionales para análisis por carrera. Su validación IPSS código 162 para `MAT_2026` entrega 66 filas y total matrícula 3.425, coincidente con el total de publicación SIES ya gobernado (B).

El archivo es un dataset agregado por carrera, no contiene RUT, MRUN, nombres de estudiantes ni filas individuales (B). El uso como fuente principal es una decisión interna de gobernanza (D). Las columnas que no cuentan todavía con mapeo oficial verificado permanecen pendientes (E) y se detallan en su manifiesto. El CSV original del Desktop no se modifica ni se incorpora al repositorio en esta etapa.

## Tabla puente CSV histórico–BASE_RETENCION_MU — clasificación B/C/E

Se generó `CARACTERIZACIÓN/gobernanza/sies/TABLA_PUENTE_CSV_BASE_RETENCION_MU.csv` y su versión Excel con fórmulas. El cruce cubre IPSS 162 y `MAT_2022`–`MAT_2026`, usando la llave `ANIO + COD_SED + COD_CAR + JOR + VERSION`, derivada del patrón `I{institución}S{sede}C{carrera}J{jornada}V{versión}`. La tabla contiene 198 filas agregadas, no contiene identificadores personales y mantiene visibles las diferencias contra el total de filas y contra `VIG=1` (B/C).

Resumen validado: 2022: unión 27, igual total 23, distinto total 3, igual VIG1 26, distinto VIG1 0, solo BASE 1; 2023: unión 22, igual total 16, distinto total 5, igual VIG1 19, distinto VIG1 2, solo CSV 1 y solo BASE 0 (verificado independientemente por Claude leyendo el archivo generado fila por fila: el aparente conteo previo de 2 códigos solo CSV correspondía a una lectura incorrecta de la columna "distinto VIG1"=2, no a la columna "solo CSV"; no hay discrepancia real); 2024: unión 33, igual total 6, distinto total 21, igual VIG1 27, distinto VIG1 0, solo CSV 1 y solo BASE 5; 2025: unión 50, igual total 43, distinto total 0, igual VIG1 32, distinto VIG1 11, solo CSV 7; 2026: unión 66, igual total 6, distinto total 55, igual VIG1 15, distinto VIG1 46, solo CSV 5 (B).

Los códigos Postítulo aparecen explícitamente como fuera del alcance de `BASE_RETENCION_MU`. Los casos restantes solo CSV o solo BASE no tienen causa verificable en esta etapa y quedan como E. Esta conciliación es distinta de la brecha agregada 226 de publicación SIES versus institucional 2026.

## Cierre a nivel carrera de la tabla puente — clasificación B/C/D/E (2026-09-30)

Instrucción del usuario: "no deben quedar pendientes". Se cerró la conciliación fila-a-fila descrita arriba agregando las 198 filas de `PUENTE` por `(ANIO, COD_CAR)`, excluyendo Postítulo (fuera de alcance de `BASE_RETENCION_MU`, D), en una nueva hoja `RESUMEN_POR_CARRERA` con fórmulas `SUMIFS` vivas (79 combinaciones ANIO+COD_CAR) y su exportación `TABLA_PUENTE_CSV_BASE_RETENCION_MU_RESUMEN_POR_CARRERA.csv`. Resultado, verificado con recálculo independiente en LibreOffice headless y agregación equivalente en Python sobre los datos crudos de `PUENTE` (coincidencia exacta) (B/C):

- **COINCIDE_VIG1 (44 de 79)**: el total CSV coincide exactamente con `BASE_RETENCION_MU` filtrado a `VIG=1`, sumando todas las jornadas/versiones de la carrera. Cubre el 100% de las combinaciones de 2022, 2023 y 2024 (28 de 28), más 11 de 2025 y 5 de 2026. Las diferencias que se observan a nivel de código completo (jornada+versión) dentro de `PUENTE` — incluidos los códigos "solo BASE" y "brecha puntual" antes marcados como causa no verificada — son reclasificación de jornada/versión entre el CSV histórico y `BASE_RETENCION_MU`, no matrícula faltante (B).
- **COINCIDE_TOTAL_2025 (8 de 79, todas en 2025)**: no coinciden contra `VIG=1` pero sí coinciden exactamente contra el total de `BASE_RETENCION_MU` sin filtrar `VIG` (incluye `VIG=0`). Neto agregado 2025 = 73. A diferencia de 2022-2024, el corte informado a SIES en 2025 parece incluir registros `VIG=0` para estas 8 carreras (B). La causa metodológica de esta diferencia entre años no está documentada en las fuentes disponibles del proyecto; queda como E acotada y cuantificada, no como vacío.
- **BRECHA_GOBERNADA_2026 (27 de 79, todas en 2026)**: no coinciden ni contra `VIG=1` ni contra el total BASE. La suma de sus diferencias (226 estudiantes) coincide exactamente con la brecha ya gobernada entre la Publicación SIES 2026 (3.425) y la Base Institucional vigente 2026 (3.199). No es un hallazgo nuevo (D).

El texto `OBSERVACION` de las 53 filas de `PUENTE` que decían "causa no verificada (E)" sin más detalle (45 "brecha", 6 "solo BASE", 2 "solo CSV") fue actualizado para referenciar esta explicación por carrera, sin alterar ningún valor numérico (verificado: 0 diferencias fuera de la columna `OBSERVACION` al comparar la versión anterior y la nueva del CSV, fila por fila). Detalle completo, con fórmulas trazables, en `TABLA_PUENTE_CSV_BASE_RETENCION_MU.manifest.json` (sección `cierre_carrera_2026_09_30`) y en la hoja `RESUMEN_POR_CARRERA` del XLSX.

Única E que permanece, explícita y acotada: la causa metodológica de por qué el corte 2025 incluyó `VIG=0` para 8 carreras y 2022-2024 no. No bloquea el cierre de este artefacto: el patrón está 100% cuantificado (8 carreras, neto 73) y no representa matrícula sin explicar.


## Cierre de la investigación de causas — brechas de retención 2022 y 2024 (2026-09-30)

Instrucción del usuario: agotar las reglas de negocio de retención adicionales del correo y del Manual de Procesos: Matrícula Unificada 2026 antes de aceptar las brechas de +4,49 pp (2022) y -9,08 pp (2024) como sin explicación.

### Reglas complementarias del manual — clasificación B/E

Se identificaron y probaron contra los datos reales dos reglas del manual no implementadas en `02_COHORTE_ELEGIBILIDAD`:

- **NIV_ACA<3** (definición de "estudiante de primer año", exige Nivel Académico menor a 3 semestres): el 100% de los candidatos 2022 (305/305) y 2024 (558/558) ya tiene `NIV_ACA=1`. No hay población que excluir; no explica la brecha.
- **Estudiante transferido** (Cambio Interno=3, Cambio Externo=4, Articulación TNS→Profesional=11 deben excluirse de "primer año" aunque el año de ingreso coincida): el 100% de los candidatos 2022 y 2024 tiene `FOR_ING_ACT=1`. No hay población que excluir; no explica la brecha.

**Corrección registrada:** una primera verificación de esta última regla, dentro de la misma sesión, reportó por error 5 casos `FOR_ING_ACT=3` (2022) y 13 casos `FOR_ING_ACT` en {4,11} (2024). El error fue propio de Claude, no del libro gobernado: el script de verificación usaba un índice desfasado en una fila entre `FILA_RAW` de `02_COHORTE_ELEGIBILIDAD` (que es el número de fila de Excel de `BASE_RETENCION_MU`, no un índice de datos 1-based) y la lista de filas leída en Python. Re-verificado con el índice correcto (0 discrepancias de `ANIO_INFORMADO` al validar la alineación en las 10.200 filas): el hallazgo de transferidos no existe y queda retirado. No se había incorporado a ninguna decisión de gobernanza antes de detectarse el error.

Con esto se agotan las reglas de negocio de retención explícitas del correo SIES y del manual: las tres del correo (duración de programa, exclusión de especiales, inconsistencia de cohorte) ya estaban correctamente implementadas; las dos adicionales del manual están ausentes de la fórmula pero sin efecto material en los datos actuales.

### Cobertura y matching entre años — cruce delegado a Codex, verificado íntegramente por Claude

Descartada la interpretación de reglas como causa, se investigó cobertura/matching de las fuentes RAW entre años. El cruce pesado se delegó a Codex con rutas, hashes y contexto ya gobernado, y Claude verificó cada cifra de forma independiente, trabajando directamente en el dispositivo del usuario y sin exportar identificadores individuales.

**2024 — los 180 casos ausentes de 2025 (de los 232 no retenidos):** verificados exactamente (misma llave `TIPO_DOC+N_DOC+DV`, misma distribución por `COD_CAR/COD_SED/JOR/VERSION/FOR_ING_ACT`, cero diferencias contra el reporte de Codex). Los 180 comparten el lote de carga `FECH_CAR=08-05-2024 18:34` con `NIVEL=1`, `NIVEL 2=NUEVO` y `1eraño=1` en el RAW 2024 — el mismo lote agrupa a 560 de los 636 candidatos totales de la cohorte 2024, por lo que el lote no distingue a los ausentes de los vigentes. Búsqueda directa en la hoja granular del RAW 2025 (2.371 filas), sin pasar por `BASE_RETENCION_MU`: 0 de los 180 encontrados. Esto descarta un error de consolidación RAW→`BASE_RETENCION_MU`: la ausencia es real en el RAW oficial 2025, no un artefacto de proceso interno (B).

**2022 — los 61 registros de diferencia (310 candidatos RAW vs 249 histórico):** verificados exactamente contra RAW 2022 (`2022.csv`, sha256 `08ee0b7973f4a2705b388c73413f2ce5402b849f8c3c09c3843d5c2f8c060a4f`) y la fuente histórica gobernada (`reporte_matricula_ip_san_sebastian.csv`, sha256 `1ae2bf5b1ac47e9ffebc0d4d9040a8fd080b42602fe3176e39b409cad4353de6`). La diferencia se concentra en los códigos de carrera 3 (+40) y 46 (+13), que reúnen 53 de los 61. El RAW 2022 no trae una columna "1eraño" equivalente a la de 2024; trae `COD_NIV_GLO=1` en el 100% de las 1.038 filas (sin valor diagnóstico) y `FECH_CAR` con 10 valores distintos, de los cuales 297/310 candidatos comparten uno solo (B).

### Estado final — clasificación E

Se agotaron dos vías razonables sin forzar explicación: interpretación de reglas de negocio (correo + manual, todas verificadas como implementadas o sin población afectada) y cobertura/matching entre años (acotada con precisión, sin artefacto de proceso encontrado). Ninguna vía explica la magnitud de +4,49 pp (2022) ni -9,08 pp (2024). Ambas brechas se cierran como **E — causa no establecida**, sin ajustar la definición de retención ni las tasas calculadas para acercarlas a la publicación SIES.

Detalle completo, fila por fila con clasificación A/B/C/D/E, en la hoja `11_DIAGNOSTICO_BRECHAS` del libro `outputs/retencion_primer_anio_ipss_162/20260930_000000/RETENCION_PRIMER_ANIO_IPSS_162_DIAGNOSTICO_BRECHAS_20260930.xlsx`, actualizado 2026-09-30; SHA-256 `5f0f7c7f0f238556de374d287bf2931ccc8a93a5489f4c2f2b543befd38c77b3`.

Verificado por: Claude, 2026-09-30, mediante recálculo independiente (LibreOffice headless) en el dispositivo del usuario y comparación fila por fila contra el cruce delegado a Codex.

## Entregable ejecutivo para audiencia no técnica (2026-09-30)

Por solicitud del usuario, se construyó un segundo archivo, separado del diagnóstico técnico, para distribución
a personal de IPSS que no maneja las reglas de negocio de retención: `RETENCION_IPSS_ANALISIS_2022_2026.xlsx`.

**Objetivo y alcance.** Presentar, en lenguaje simple y con gráficos, la definición de retención, el origen de
los datos, la explicación del cruce y los resultados — organizados por **sector IPSS** (no por área SIES/CINE-F,
que el usuario señaló como no reconocible para el personal de IPSS: "no tenemos Ciencias Básicas").

**Fuente de datos.** Extraída y verificada desde `02_COHORTE_ELEGIBILIDAD` y `06_SIES_2025_GRANULAR_OFICIAL` del
libro `RETENCION_PRIMER_ANIO_IPSS_162_DIAGNOSTICO_BRECHAS_20260930.xlsx` (SHA-256
`5f0f7c7f0f238556de374d287bf2931ccc8a93a5489f4c2f2b543befd38c77b3`), tras recálculo con LibreOffice headless.
2.379 candidatos incluidos (cohortes 2022-2025), verificado contra el total ya gobernado. Clasificación C,
derivado de B ya verificado — no es un recálculo independiente de las reglas de elegibilidad, que permanecen
gobernadas exclusivamente en el archivo técnico.

**Sin datos personales.** El archivo ejecutivo no incluye `BASE_RETENCION_MU` ni ningún identificador de
estudiante (nombre, RUT, fecha de nacimiento). Solo contiene conteos agregados por año, carrera y bandera de
retención (1/0). Diseño de privacidad por defecto, consistente con la regla de gobernanza del proyecto.

**Mapeo carrera → sector IPSS (clasificación B-externo).** Sector según la taxonomía propia de IPSS publicada
en ipss.cl ("Sectores de Estudio"), consultada el 2026-09-30 por instrucción explícita del usuario ("buscalo en
la pagina web el ipss.cl"). Las 17 carreras presentes en la cohorte 2022-2025 se verificaron una por una contra
su URL individual en ipss.cl (sin excepciones, sin inferencia por patrón):

| Sector IPSS | Carreras (n=17) |
|---|---|
| Tecnologías | Ing. Informática, Ing. Ciberseguridad, Téc. Ciberseguridad, Ing. Conectividad y Redes, Téc. Conectividad y Redes, Téc. Programación y Análisis de Sistemas, Ing. Ciencia de Datos, Téc. Ciencia de Datos |
| Administración y Comercio | Auditoría, Contabilidad General, Ing. Administración de Empresas, Téc. Administración de Empresas, Ing. Logística, Téc. Logística, Administración Pública, Téc. Administración Pública |
| Salud | Téc. Enfermería |

URLs de verificación por carrera guardadas en la hoja `8_Mapeo_Sector_IPSS` del propio archivo entregable. El
sector "Ingeniería" (4º sector de ipss.cl, 9 carreras) no contiene ninguna carrera presente en la cohorte
2022-2025 — no aplica.

**Hallazgo observado (no un error):** Administración y Comercio solo tiene candidatos desde 2024, y Salud solo
desde 2025 (dato B, visible en la hoja 4 del entregable). Coincide con la apertura progresiva de esos sectores
en la oferta de IPSS (Salud se anuncia como "nueva área" en ipss.cl para 2025).

**Comparación con SIES por sector.** Solo es posible a nivel granular para 2025 (única tabla oficial por carrera
recibida, correo Rodrigo Rolando Meneses 09-09-2026). Brechas 2025: Tecnologías +0,12 pp, Administración y
Comercio -0,39 pp, Salud 0,00 pp — todas menores, sin necesidad de investigación adicional. Para 2022-2024 solo
existe comparación a nivel institucional total (ya cerrada como E — causa no establecida, sección anterior de
este README).

**Estructura del archivo:** Portada; 1-3 explicación (definición SIES, origen de datos, cómo se cruza);
4 Resultados por sector (2 tablas + 2 gráficos de columnas); 5 Evolución 2022-2026 (gráfico de líneas,
nivel institucional); 6 Limitaciones; 7 Glosario; hojas 8-10 de soporte técnico (mapeo de sectores, base
analítica anonimizada, tabla SIES 2025 granular) — todas con fórmulas en vivo (`CONTAR.SI.CONJUNTO`,
`SUMAR.SI.CONJUNTO`, `BUSCARV`), sin valores pegados a mano.

**Entrega.** `outputs/retencion_ipss_analisis_ejecutivo_2022_2026/20260930_000000/RETENCION_IPSS_ANALISIS_2022_2026.xlsx`
(SHA-256 `881761ab72b8834344e8097ab2b789f4755d2b5cfecfcfdf4b3090fc432ef23f`), sin datos personales; excluido de
Git por la regla `*.xlsx` del `.gitignore` del proyecto, igual que el resto de los libros de este hito — la
trazabilidad queda en este README. Copia adicional entregada en el Escritorio del usuario, mismo hash verificado.

Verificado por: Claude, 2026-09-30, mediante recálculo independiente (LibreOffice headless) en el dispositivo
del usuario; 0 errores de fórmula, 0 "SIN MAPEO" en las 2.379 filas de la base analítica y las 36 filas de la
tabla SIES 2025 granular.
