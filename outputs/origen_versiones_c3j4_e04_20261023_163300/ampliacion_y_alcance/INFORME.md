# Alcance del seguimiento y antecedente de versiones — 23 de octubre de 2026

Proceso: Matrícula Unificada / retención intertrimestral IPSS 162. Subproyecto: diccionario UMAS–SIES. Auditoría histórica puntual: C3/J4 2021–2022 y E04 MU2025. Libro examinado: seguimiento 2024–2026; no incorpora 2027. Clasificaciones: A oficial, B observado, C cálculo, D decisión interna, E pendiente.

## Respuesta a la duda de alcance

**B/C.** Se estaban presentando conjuntamente tres universos diferentes: códigos de origen T1 del libro, contextos académicos localizados para su seguimiento y una prueba experimental de predicción histórica. Sus porcentajes no son comparables ni representan tasas de retención.

| Medición | Numerador / denominador | Resultado | Respaldo |
|---|---:|---:|---|
| Filas T1 del libro con código MU de origen documentado | 3.179 / 3.179 | 100 % | B/C |
| Contextos localizados, consulta actual v7: documental o interno aprobado | (5.088 + 29) / 5.320 | 96,18 % | B/C para documental y cálculo; D para 29 aprobaciones |
| Subconjunto anterior con varias versiones históricas | (1.927 + 29) / 2.009 | 97,36 % | B/C/D |
| Cobertura de prueba de predicción histórica | 7.670 / 8.354 | 91,81 % | C; experimento, no código adoptado |

**B/C.** Las 3.179 filas T1 corresponden a 3.142 personas distintas: 558 filas de 2024, 1.150 de 2025 y 1.471 de 2026. No constituyen un denominador único de retención. Las hojas 52–54 del Excel todavía contienen v1 (5.088 documentales, dos internos, 230 pendientes: 95,68 %); la consulta v7 de este informe no modificó el libro.

**B/C/E.** Los 203 contextos pendientes de v7 se distribuyen en 189 asociados a otra familia carrera/sede/jornada, ocho a la misma familia y seis sin familia determinada. Esta comparación no demuestra por sí sola un cambio efectivo: el contexto puede proceder de un respaldo posterior. Entre los contextos de familias con múltiples versiones quedan 53 pendientes. No son 203 ni 53 estudiantes necesariamente distintos.

**B/C/E.** Además hay 939 filas T1 sin contexto localizado en esta aplicación: 65 de 2024, 283 de 2025 y 591 de 2026. Conservan su código MU de origen. No forman parte del denominador 5.320 y no se clasifican como desertores o como personas sin código SIES. Los 1.294 registros de ingresos T2/T3 del libro (222 de 2025-T2, 527 de 2026-T2 y 545 de 2026-T3) no fueron reclasificados en esta aplicación; no se les atribuye el 96,18 %.

**B/C.** El libro llega a 2026; el alcance solicitado de seguimiento llega a T3-2026. Los períodos de las observaciones auditadas son nativos de PROMEDIOS: no se convierten automáticamente en trimestres ni certifican una foto de cierre. El diccionario histórico 2019–2026, con períodos nativos 1–5, es un universo adicional.

## Código del programa y registro individual

**A.** El Instructivo Oferta Académica 2026, página 7, define el código unificado como identificador del programa compuesto por institución, sede, carrera, jornada y versión. Fuente: `/Users/alexi/Documents/GitHub/avance_curricular/data/reglas_negocio/20261015/fuentes/20251125_85582_Instructivo_Oferta_Academica_2026_CFT_E_IP_DFE.pdf`. SHA-256: `af8289f9292848fa16d2939ad730b8105c9d4605904a6af3974fc00ec9febbe2`.

**C.** De esta definición se desprende que el ingreso de una persona nueva no crea por sí mismo un código nuevo. Se separan: existencia del programa/version en oferta; equivalencia interna entre expediente UMAS y ese programa; y registro individual documentado en MU. Contar con los dos primeros no demuestra el tercero. Los totales agregados controlan la conciliación, pero no distinguen por sí solos qué persona corresponde a cada versión cuando hay varias distribuciones posibles.

**D/C.** El contrato vigente del diccionario conserva `codigo_cohorte_origen` y consulta por separado `codigo_contexto_destino`. Por ello, seguir T1 no exige reconstruir otra vez un código de origen que ya está documentado. Las excepciones de destino y la evidencia de continuidad/vigencia deben mantenerse separadas. No se adopta una regla nueva ni se promete cobertura universal.

## Búsqueda solicitada: C3/J4 antes del lote de mayo de 2022

**B/C.** Se revisaron 17 correos, cuatro libros adicionales y un inventario local de 9.565 rutas. No se localizó una consulta o decisión acreditada anterior al lote 06/05/2022 16:14 que asignara V2.

**B.** Una comunicación de 2024 informa rectificaciones históricas realizadas según la entrega formal adjunta. El adjunto incluye exactamente 24 de las 50 personas foco con cambios de ANIO_ING_ORI (2021→1900, literal observado) y FOR_ING_ACT (1→4), sin corregir VERSION. Las 50 aparecen con V1 en 2021 y V2 en 2022. Los rechazos y la referencia a 53/58 corresponden a intercambios anteriores, no se equipararon al foco ni al resultado final.

**E.** Sigue sin localizarse la regla generadora de V2. El antecedente de 2024 no acredita cuál consulta asignó esa versión en 2022, ni la aceptación individual de cada fila adjunta. Este pendiente causal no borra los códigos anuales observados.

## Búsqueda solicitada: E04 antes de Precarga MU2025

**B/C.** IPSSreset.csv, fila 948, conserva V1/VIG=0; IPSS2025.csv, fila 1001, conserva V1/VIG=1. Su orden respecto a Precarga no quedó acreditado. GESTIONSGE contiene cuatro comunicaciones de 2024 concordantes por cuerpo RUT y carrera, sin DV/CODCLI: no mencionan versión ni cambio de plan. Una captura registra una carga de 2.371 filas completada el 08/05/2025, sin identificar la decisión individual de versión ni el hash del CSV.

**B/C/E.** El inventario acotado cubrió 347 archivos del respaldo Carlos y 19 de VRA, incluyendo 16 cuerpos MSG pertinentes. No se localizó la consulta o decisión anterior al lote del 16/04/2025. No se infiere cronología del nombre reset ni de los totales. El código V1 observado sigue siendo evidencia; su causa de asignación continúa pendiente.

## Precisión sobre denominadores existentes

**B/C.** `18_Foto_Intertrimestral!D11` cuenta 1.471 filas T1-2026; `H11` usa 1.360/1.467 porque exige `20_Foto_BBDD!R=1`. Las cuatro filas excluidas tienen NO APLICA y ELIMINADO/TITULADO y sí poseen código MU. Es la fórmula ya existente, no un cambio de este informe ni una nueva aprobación funcional. No se confunde esta diferencia con cuatro códigos faltantes.

## QA, conservación y reanudación

**C.** Comprobación de integridad: 35 fuentes/componentes revalidados por SHA-256; 9 controles correctos. Se conserva el libro, base anual, diccionario v7, puntero y descriptor. No se crean ni publican identificadores individuales. Los resultados JSON son agregados con localizadores de evidencia. No se actualizó ninguna equivalencia, tasa ni denominador.

**B/C.** Rama `feature/ire-2026`; HEAD antes/después `80ca13a5a249a1a2bd53a699f5f73689b1f53040`. Sin commit, push, merge, PR ni staging. Los cambios previos del repositorio permanecen ajenos a esta entrega.

**E.** La causa de las dos asignaciones históricas no quedó resuelta en la cobertura revisada. No se extiende esta ausencia a plataformas o archivos no examinados. La siguiente revisión operativa debe distinguir las excepciones de destino del seguimiento, los contextos no localizados y las bases de cierre, sin exigir cerrar toda la auditoría histórica para reutilizar códigos T1 ya documentados.

Evidencias detalladas: `cobertura_excel_alcance_20261023.json`, `c3j4_antecedente_ampliacion_20261023.json`, `e04_antecedente_ampliacion_20261023.json`. Los hashes de fuentes y salidas están en `MANIFEST.json`.
