# Revisión de 22 grupos conflictivos y seis errores

Proceso: correspondencia UMAS/SIES por expediente y año, con aplicación al seguimiento de retención IPSS162. Años observados de los grupos: 2019–2025. Revisión local del 23 de octubre de 2026. No cambia fuentes, bases, códigos adoptados, denominadores ni Excel.

## Resultado y alcance

**B/C:** Se reprodujeron los 22 grupos K2 y los seis errores K3_min3. Los grupos contienen 637 contextos anuales documentados, 586 personas distintas y 1.744 observaciones nativas. Son grupos con varios códigos ya conocidos; no equivalen a 22 carreras sin código. Los contextos pendientes del universo ampliado se presentan aparte en la tabla CSV y no se convierten en resueltos por esta revisión.

**B/C:** En siete grupos el ingreso MU separa todas las versiones observadas: G06, G07, G15, G16, G20, G21 y G22. El ingreso del corte DatosAlumnos lo hace en seis, excluyendo G15. El primer año observado de actividad separa solo G07 y G20; el período de ingreso no separa por sí solo ninguno. No se encontró una combinación temporal suficiente en los otros 15 grupos con los campos probados.

**B/E:** En G02, G06 y G09 las versiones tienen perfiles distintos de duración/tipo: regular de ocho semestres frente a continuidad de cuatro. Esa consulta usa el código SIES ya conocido: sirve para describir la diferencia, pero sería circular usarla para adivinar el código sin respaldo independiente del plan UMAS. G18 se separa por CATEGORIA del corte actual de DatosAlumnos; G16/G21 por combinación de categoría, vía, situación y estado actuales. No acreditan qué categoría regía históricamente.

**B/C:** Se observaron 70 contextos con versión distinta de la última evidencia anual anterior bajo el mismo contexto actual de persona, CODCLI, carrera, plan, sede y jornada. En 50 se pasa de C3/J4/V1 en 2021 a V2 en 2022. Esto obliga a conservar la dimensión temporal del diccionario. No demuestra por sí solo la fecha efectiva de una migración ni que el plan observado actualmente fuera el plan vigente entonces.

**E:** Una separación perfecta en esta muestra no es una regla general ni un cierre nuevo. Hay grupos con una sola persona minoritaria y fechas de ingreso que no ordenan las versiones de forma creciente. No se adoptó ninguna regla adicional.

## Los 22 grupos

Cada fila: B/C = distribución y cruce observados; E = causa o generalización no acreditada. Todos pertenecen a institución 162, sede 2. Los nombres UMAS/planes se conservan literalmente. La tabla completa con códigos únicos, conteos y relación con el Excel está en `TABLA_22_GRUPOS.csv`; las distribuciones exactas están en `GRUPOS_22_VARIABLES.json` y `CAMPOS_DA_22.json`.

| Grupo | Año · plan · jornada | Códigos documentados (contextos) | Qué distingue / qué falta | Clas. |
| --- | --- | --- | --- | --- |
| G01 | 2022 · IETMREOL20211 · J4 | I162S2C3J4V1: 3  /  I162S2C3J4V2: 132 | Ingreso no separa todo: 2021 todavía contiene V1 y V2. 50 contextos documentan V1 en 2021 y V2 en 2022. | B/C; E |
| G02 | 2024 · IECSREOL20211 · J4 | I162S2C46J4V1: 1  /  I162S2C46J4V3: 61 | Perfiles diferentes: V1 continuidad 4 semestres y V3 regular 8. NIV_ACA separa E01 dentro de K3; no valida todo el grupo. | B/C; E |
| G03 | 2020 · IETMRE20191 · J2 | I162S2C3J2V1: 4  /  I162S2C3J2V4: 28 | Años de ingreso 2015/2018 comparten versiones; un cambio anual V1→V4 observado. | B/C; E |
| G04 | 2021 · IETMRE20191 · J2 | I162S2C3J2V1: 1  /  I162S2C3J2V4: 12 | Ingreso 2018 compartido; un cambio anual V1→V4 observado. | B/C; E |
| G05 | 2019 · IECIRE20191 · J2 | I162S2C1J2V1: 3  /  I162S2C1J2V4: 21 | Ingreso 2018 compartido; no se localiza variable suficiente. | B/C; E |
| G06 | 2024 · IINF20241 · J4 | I162S2C1J4V2: 132  /  I162S2C1J4V3: 1 | MU origen 2019 distingue V3; 2021–2024 V2. V3 continuidad 4 y V2 regular 8 semestres. | B/C; E |
| G07 | 2021 · IECIREOL20201 · J4 | I162S2C1J4V1: 10  /  I162S2C1J4V2: 1 | Ingreso 2019 V2; 2020 V1. Primer año observado de actividad también separa. | B/C; E |
| G08 | 2022 · IECIREOL20201 · J4 | I162S2C1J4V1: 1  /  I162S2C1J4V2: 9 | Ingreso 2020 compartido. Siete contextos cambian V1→V2 de 2021 a 2022; E02 conserva V1 hasta 2022. | B/C; E |
| G09 | 2021 · IETMRE20211 · J2 | I162S2C3J2V1: 30  /  I162S2C3J2V3: 1 | V3 continuidad 4 semestres frente a V1 regular 8; ingreso 2019 compartido. Revisar atribución entre expedientes. | B/C; E |
| G10 | 2025 · IINF20241 · J1 | I162S2C1J1V1: 5  /  I162S2C1J1V2: 18 | Ingresos 2024/2025 comparten versiones. E04 documenta V2→V1→V2 en 2024–2026. | B/C; E |
| G11 | 2019 · IETMRE20191 · J2 | I162S2C3J2V1: 3  /  I162S2C3J2V4: 17 | Ingreso 2018 compartido; no se localiza variable suficiente. | B/C; E |
| G12 | 2019 · TPCRE20191 · J2 | I162S2C2J2V1: 3  /  I162S2C2J2V2: 34 | Ingresos 2016/2018 comparten versiones; ambos perfiles regulares de 5 semestres. | B/C; E |
| G13 | 2025 · IINF20241 · J2 | I162S2C1J2V1: 7  /  I162S2C1J2V4: 13 | Ingresos 2024/2025 compartidos; cuatro contextos documentan V4→V1 de 2024 a 2025. | B/C; E |
| G14 | 2025 · ICRE20241 · J2 | I162S2C3J2V1: 3  /  I162S2C3J2V4: 8 | Ingreso 2025 compartido; no se localiza variable suficiente. | B/C; E |
| G15 | 2020 · TPCREOL · J4 | I162S2C2J4V1: 3  /  I162S2C2J4V2: 1 | MU origen 2016 distingue V2 y 2018 V1. DA asigna ingreso 2020 a todos; E05 solo homologaciones/convalidaciones. | B/C; E |
| G16 | 2019 · TTMRE20191 · J1 | I162S2C6J1V1: 1  /  I162S2C6J1V2: 12 | Ingreso 2014 V1 y 2019 V2; la combinación de estados actuales también separa descriptivamente. | B/C; E |
| G17 | 2019 · TPCRE20191 · J1 | I162S2C2J1V1: 3  /  I162S2C2J1V2: 17 | Ingreso 2018 compartido; no se localiza variable suficiente. | B/C; E |
| G18 | 2023 · TTMRE20211 · J2 | I162S2C6J2V1: 2  /  I162S2C6J2V2: 4 | Ingreso 2022 compartido; CATEGORIA actual separa, sin prueba histórica. Tres contextos V1→V2 de 2022 a 2023. | B/C; E |
| G19 | 2025 · TCRE20241 · J2 | I162S2C6J2V1: 2  /  I162S2C6J2V2: 5 | Todos ingreso 2025; no se localiza variable suficiente. | B/C; E |
| G20 | 2020 · IECIRE20191 · J1 | I162S2C1J1V1: 3  /  I162S2C1J1V2: 2 | Ingreso separa descriptivamente, pero no sigue orden creciente de versión: 2017/18 V1; 2015/19 V2. | B/C; E |
| G21 | 2020 · TTMRE20191 · J1 | I162S2C6J1V1: 1  /  I162S2C6J1V2: 12 | Ingreso separa sin orden creciente: 2017 V1; 2014/19/20 V2. Estados actuales combinados también separan. | B/C; E |
| G22 | 2019 · IECIRE20191 · J1 | I162S2C1J1V1: 1  /  I162S2C1J1V2: 6 | Ingreso 2015 V1; 2018/19 V2, separación descriptiva. | B/C; E |

## Seis errores experimentales

**B/C:** Se reprodujo el mismo conjunto de seis errores con cinco particiones que separan personas entre entrenamiento y prueba. Cada error corresponde a la única persona de su versión dentro del grupo K3. Al ocultarla, el grupo de entrenamiento solo conoce la otra versión. Una variable adicional que la aísle puede producir abstención; no aprende automáticamente su versión con el soporte mínimo de tres personas. Estos seis códigos ya estaban documentados: no son seis pendientes recuperados ni prueba de seis envíos incorrectos.

| Caso | Año · plan · jornada | Documentado → predicho (no aplicado) | Resultado | Clas. |
| --- | --- | --- | --- | --- |
| E01 | 2024 · IECSREOL20211 · J4 | I162S2C46J4V1 → I162S2C46J4V3 | MU 2024 registra NIV_ACA=4; las otras 29 personas del grupo tienen niveles 5–7. Forma de ingreso 11 y origen 1900 también existen en V3: no distinguen. El mismo CODCLI, plan y jornada tienen V3 en 2023 y V1 en 2024. | B/C; E causa |
| E02 | 2022 · IECIREOL20201 · J4 | I162S2C1J4V1 → I162S2C1J4V2 | Origen e ingreso actual MU 2020 coinciden con DA 2020. El mismo CODCLI, plan y jornada documentan V1 en 2020–2022 y V2 en 2023. Ingreso, período de ingreso, vía de admisión y estado se solapan con el grupo V2. | B/C; E causa |
| E03 | 2022 · IETMREOL20211 · J4 | I162S2C3J4V1 → I162S2C3J4V2 | MU 2022 conserva ingreso actual y origen 2018; DatosAlumnos declara 2022. Las 66 personas V2 del mismo grupo tienen ingreso actual y origen 2019, 2020 o 2022. Otra matrícula de esta persona aparece en J2 en 2020–2021; después aparece en J4V1 en 2022 y J4V2 en 2023. | B/C; E causa |
| E04 | 2025 · IINF20241 · J1 | I162S2C1J1V1 → I162S2C1J1V2 | El mismo CODCLI, plan IINF20241 y jornada 1 tienen V2 en 2024, V1 en 2025 y V2 en 2026. Año y semestre de ingreso, forma de ingreso, modalidad y vigencia no separan a la persona de las ocho con V2 del grupo K3. | B/C; E causa |
| E05 | 2020 · TPCREOL · J4 | I162S2C2J4V2 → I162S2C2J4V1 | MU 2020 documenta origen e ingreso actual 2016, frente al origen 2018 de las otras tres personas V1. DatosAlumnos indica ingreso 2020 para todas. La persona V2 tiene MM_SEM_SUSPENSION=2 y las demás 0; las evidencias PROMEDIOS 2020 conservadas contienen solo convalidación y homologación. | B/C; E causa |
| E06 | 2021 · IETMRE20211 · J2 | I162S2C3J2V3 → I162S2C3J2V1 | MU 2021 documenta Plan Regular de Continuidad y duración de cuatro semestres para V3; las otras 30 personas V1 tienen Plan Regular y ocho semestres. La persona aparece en NCONRE en 2020 con otro CODCLI y V3; después en IETMRE20211 en 2021, y en IETMREOL/J4 con otro CODCLI en 2022. El origen 2019 también aparece en tres personas V1, por lo que no separa por sí solo. | B/C; E causa |

**B:** Los cuatro códigos procedentes de la base consolidada se contrastaron con los RAW: E01, CSV2024 fila354; E02, CSV2022 fila197; E03, CSV2022 fila666; E04, hoja granular2025 fila867. Coinciden. E05/E06 se leyeron en MAT_2020 fila887 y MAT_2021 fila349. No se detectó error de consolidación en esos cuatro códigos; tampoco se acredita por ello aceptación regulatoria o la causa de la asignación. Fuentes, hojas, filas, hashes y controles de identidad están en `ERRORES_6.json` y los archivos QA adicionales.

## Alcance concreto en el Excel

**B/C:** Se revisó `RETENCION_IPSS_DICCIONARIO_APLICADO_20261023_V12.xlsx`, 54 hojas, y su original individual. Los 105 grupos agregados reproducen las 4.473 filas del original. Cinco de los 22 grupos intersectan T1 del mismo año y la misma familia de carrera/sede/jornada:

| Grupo | Contexto | Personas T1 | Observaciones | Pendientes de código actuales | Clas. |
| --- | --- | --- | --- | --- | --- |
| G06 | IINF20241 · 2024 · J4 | 84 | 206 | 0 | B/C |
| G10 | IINF20241 · 2025 · J1 | 14 | 35 | 0 | B/C |
| G13 | IINF20241 · 2025 · J2 | 9 | 24 | 0 | B/C |
| G14 | ICRE20241 · 2025 · J2 | 9 | 25 | 0 | B/C |
| G19 | TCRE20241 · 2025 · J2 | 7 | 14 | 0 | B/C |
| Total sin duplicar |  | 123 | 304 | 0 | B/C |

**B/C:** Las 304 observaciones se distribuyen en 123 del período nativo1, 95 del2 y 86 del3: las181 del2/3 ya tienen código reutilizable. Estos períodos nativos no prueban por sí solos vigencia en la fecha exacta de un cierre. G06 tiene otras22 observaciones de personas T1 en otra familia; se conservaron separadas. En hoja9 anual aparece además G01/IETMREOL20211/J4/2022: 60 personas y224 observaciones, sin pendiente de código. No se suman personas entre años como si fueran una cohorte.

**B/C:** E04 sí pertenece a una trayectoria del Excel: cohorte2024, origen C1/J1/V2, seguida en MU2025, donde consta C1/J1/V1. Los otros cinco errores no aparecen en las cohortes analíticas revisadas de hoja9 ni en los grupos T1 de hoja20. Ninguno de los seis pertenece al T1 del mismo año del error ni a los grupos exactos de nuevos ingresos T2/T3. Se distinguió el rol de origen del rol de seguimiento anual siguiente.

**B/C:** En el diagnóstico anual, `02_COHORTE_ELEGIBILIDAD!W2` sigue tipo documental, documento, DV, año siguiente, año/semestre de origen y VIG≥1. No exige igualdad de versión, carrera o jornada. `Z2=IF(AND(Y2=1,W2>0),1,0)`. Por ello el destino V1/V2 de E04 no cambia por sí solo su indicador retenido. La versión de origen sí participa en el catálogo y elegibilidad inicial: no corresponde generalizar que la versión nunca importa.

**B/C:** El Excel V12 contiene cero fórmulas en hojas18/19/20: son agregados congelados. El original conserva178/487/63.036 fórmulas respectivamente. Hoja26 conserva1.847 fórmulas. Las hojas revisadas no consultan las nuevas hojas52–54 del diccionario. La integración actual es diagnóstica: cerrar una correspondencia no actualiza automáticamente las tasas. No se demostró un error de tasa causado por los seis errores de predicción, que nunca fueron aplicados.

**B/E, controles adicionales:** En los grupos nuevos T2/T3 se verificaron1.294 filas con sus fuentes;56 tienen año/período de ingreso literal diferente de su etiqueta de grupo heredada. Ninguna intersecta exactamente los22 grupos. La hoja18 original muestra1.471 personas paraT1-2026, mientras su tasaH11 divide por1.467 evaluables medianteR=1. Son diferencias de alcance ya existentes, conservadas sin corregir; no causadas por las versiones investigadas. Por eso esta revisión no recertifica todas las tasas ni todos los denominadores del libro.

## Decisión técnica y reanudación

**C, propuesta no aplicada:** Mantener el código individual documentado como referencia del año y expediente. Las variables temporales/perfil se usan para detectar excepciones y contrastar candidatos; no sustituyen esa referencia. Reutilizar T1 en seguimiento interno exige conservar persona, expediente y contexto, comprobando cambios de plan/jornada y fechas disponibles.

**E:** El trabajo siguiente más acotado es localizar las decisiones/transformaciones anuales de las transiciones agrupadas (especialmente las50 C3/J4 de2021→2022 y la oscilación E04 de2024→2026), en vez de volver a inferir el código de cada persona desde cero. Separadamente, la futura actualización del Excel debe conectar explícitamente el diccionario a su lógica y auditar las56 etiquetas y la población evaluable, sin alterar silenciosamente los denominadores. Ninguna de esas modificaciones se ejecutó aquí.

## Evidencia y controles

**B/C:** `MANIFEST.json` registra fuentes, hashes, archivos y scripts. `QA.json` verifica la reproducción, integridad de fuentes, denominadores conservados, ausencia de identificadores en los agregados y estado de Git. `TRAZA_FORMULAS.json` conserva las fórmulas observadas y las celdas exactas. `CHECKPOINT.md` deja el punto de reanudación. Los scripts se conservan bajo `scripts/conflictos_22_20261023/`, junto a los scripts principal y de cierre. Sin commit, push ni cambios al canon.
