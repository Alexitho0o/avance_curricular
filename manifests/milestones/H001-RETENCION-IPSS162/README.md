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
