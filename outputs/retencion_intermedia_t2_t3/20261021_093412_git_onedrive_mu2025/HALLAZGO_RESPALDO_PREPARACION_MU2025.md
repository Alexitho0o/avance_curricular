# MU2025: búsqueda histórica y reconstrucción del tratamiento de ingresos T2/T3-2024

Fecha: 2026-10-21T09:46:53.435999-03:00. Hito relacionado: H001-RETENCION-IPSS162. Proceso MU2025; ingresos UMAS 2024-T2/T3. Diagnóstico agregado sin modificaciones a fuentes.

## Hallazgo principal

**B/C.** Se localizó en OneDrive el respaldo de preparación de MU2025, IPSS_Procesamiento.xlsx, que permite observar la reclasificación de 50 de las 83 personas entre sus hojas. Otras 30 están marcadas Corrección y tres tienen otra matrícula CODCLI de ingreso 2025 en la misma carrera. Los tres grupos son excluyentes y suman 83.

**E.** No se encontró un script o consulta de preparación MU2025 con traza de ejecución vinculada al archivo de envío. El respaldo sí conserva datos y marcas del tratamiento aplicado. No conserva una fórmula de asignación del año, una autorización o una bitácora que demuestre quién, cuándo y por qué decidió reclasificarlo. No se atribuye responsabilidad desde metadatos, rutas o nombres de hojas.

## Qué se pudo reconstruir de los 83 CODCLI

| Grupo | T2-2024 | T3-2024 | Total | Evidencia | Clasificación |
|---|---:|---:|---:|---|---|
| Marca 2+3 Ingreso | 40 | 10 | 50 | En Carga_Completa (2), actual y origen 2024, NIVEL Antiguo; en Carga_Completa (3), actual y origen 2025, NIVEL Nuevo. | B/C |
| Marca Corrección | 0 | 30 | 30 | Los mismos 30 están en 2 y 3er Intake.xlsx, Detalle1, con ANOINGRESO=2024/PERIODOINGRESO=3. En las hojas de carga ya figuran con actual y origen 2025. | B/C |
| Sin marca Arreglo; existe otro CODCLI de ingreso 2025 en igual carrera | 1 | 2 | 3 | DatosAlumnos contiene la matrícula de origen 2024 y otra de ingreso 2025. En el libro de preparación aparecen como Nuevo/2025. | B/C |
| Total | 41 | 42 | 83 | Población idéntica al diagnóstico previo de misma carrera. | B/C |

**B/C.** La relación de 50 cambios se comprobó fila a fila en memoria mediante persona + COD_CAR, con una única fila por persona/carrera en cada hoja comparada. Los códigos de matrícula CODCLI de origen se mantuvieron desde DatosAlumnos. No se usó el nombre de persona, sexo ni fecha de nacimiento para buscar coincidencias. Las salidas conservan únicamente agregados.

**B.** En IPSS_Procesamiento.xlsx las columnas S=ANIO_ING_ACT, U=ANIO_ING_ORI, AQ=Nivel y AV=Arreglo guardan los valores descritos. La secuencia es una comparación de versiones guardadas en hojas: no se dispone de una bitácora que certifique la cronología de sus ediciones.

**B.** Las 83 personas permanecen con actual/origen 2025 en Final a carga y en la descarga de lo cargado 08-05-2025_22-26-22_Matrícula_P. En esa descarga, la hoja 2do y 3er Ingreso contiene a las mismas 83 con ingreso UMAS 2024-T2/T3. Es evidencia del contraste dentro del mismo respaldo, no una asignación nueva creada por este diagnóstico.

**E.** Los tres casos con otro CODCLI de ingreso 2025 son una diferencia relevante frente al cruce solo por persona. Como las tablas de preparación y descarga no contienen CODCLI, no se afirma que esa otra matrícula sea necesariamente la que originó la fila SIES. El enlace definitivo requiere el puente matrícula→fila enviada que no está conservado.

## Tratamiento observado frente a regla programática

**B/C.** El tratamiento visible de los 50 casos fue cambiar tanto el año actual como el de origen de 2024 a 2025 y la etiqueta Antiguo a Nuevo, manteniendo la marca 2+3 Ingreso. En los 30 marcados Corrección el respaldo permite localizar la clasificación 2025 y el listado anterior 2024, pero no el paso exacto que cambió el año. Esto acota la brecha documental respecto del diagnóstico previo, donde solo se conocía el resultado final.

**E.** No se generaliza esta observación como regla universal de todos los T2/T3, ni se la presenta como decisión interna vigente o aprobada (D). No se demuestra una equivalencia normativa trimestre→semestre ni que deba cambiarse el año calendario de ingreso.

**B.** Los años en estas hojas son valores guardados; las columnas de ingreso no contienen fórmulas que efectúen la conversión. Sí se conserva la fórmula de clasificación de primer año, por ejemplo AR8 en Carga_Completa (3): IF(AND(U8=2025,S8=2025),"Primer año","Antiguo"). Esa fórmula lee años ya asignados; no produce el cambio de 2024 a 2025.

**B/E.** 2025_carga conserva una fórmula de búsqueda FOR_ING_ACT con referencia #REF!, mientras las hojas finales guardan FOR_ING_ACT=1 para los 83. El error heredado de esa búsqueda no prueba la causa del cambio de año; no se recalculó ni reparó el respaldo.

## Historial Git revisado

**C.** Se leyeron objetos de todas las referencias locales disponibles (ramas, respaldos, referencias remotas almacenadas, etiquetas y stash), incluyendo archivos ya eliminados de la rama actual. Se buscaron scripts/consultas y documentos relacionados con ANIO_ING_ORI, ANOINGRESO, MU2025, 2025.xlsx y el nombre de exportación de mayo. No se cambió de rama ni se restauró contenido histórico en el checkout. No se consultó Internet.

| Repositorio | Commits alcanzables en referencias locales | Versiones de texto inspeccionadas | Coincidencias de origen/MU2025 | Clasificación |
|---|---:|---:|---:|---|
| avance_curricular | 242 | 1262 | 169 | B/C |
| CARACTERIZACIÓN | 66 | 2565 | 29 | B/C |

**C/E.** Las reglas de copia de ingreso actual a origen encontradas pertenecen a las implementaciones MU2026 y a sus versiones anteriores. No se localizó una versión generadora MU2025 con vínculo verificable al hash del archivo 2025.xlsx. La búsqueda de asignaciones literales del campo de origen a 2025 en los scripts históricos relevantes no tuvo resultados. Esto no descarta una operación manual o un generador externo no conservado. El alcance es el historial alcanzable por las referencias disponibles, no objetos huérfanos ni revisiones remotas no descargadas.

## Respaldo de OneDrive revisado

**B/C.** Se inventariaron recursivamente 1.308 archivos en las raíces seleccionadas del proceso y sus respaldos; cero errores de lectura de metadatos. Se identificaron 150 archivos de código por extensión; las rutas pertenecen a otros procesos o versiones 2026, sin un generador específico MU2025 identificado. Se inspeccionaron 26 libros XLSX de la carpeta 2025/Matricula y descendientes, sin errores de lectura. Se contrastaron las hojas pertinentes de seis libros con las 83 personas. No se copiaron bases de estudiantes al repositorio.

Raíces inventariadas:
- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/0 BASES DE DATOS/MATRÍCULA UNIFICADA`
- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/0 BASES DE DATOS/MATRÍCULA`
- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/0 BASES DE DATOS/_DERIVADOS_GOBERNADOS`
- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/2025`
- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/Modificación datos historicos`
- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/2026`
- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/Matricula`
- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES`

**B.** En los 26 libros inspeccionados no se encontraron objetos de conexiones, queryTables, DataMashup/customXML ni VBA. Algunos mantienen enlaces a otros Excel. IPSS_Procesamiento.xlsx enlaza PROMEDIOSDEALUMNOS_2071.xlsx; 2 y 3er Intake.xlsx enlaza DATOSDEALUMNOS_1758_CRUDO_10_04_2025.xlsx y un respaldo Matrícula_Pregrado_2024.xlsx. Los enlaces no contienen una consulta de asignación de origen. No se da por probado que esos destinos externos hayan sido accesibles o actualizados cuando se preparó la carga.

## Manual MU2025 y evidencia de carga localizados

**A.** Manual_Matrícula_Unificada_2025.pdf, página 6, apartado 3: distingue el año calendario de ingreso al programa actual del año calendario de ingreso a primer año del programa de origen. Página 7: para cambio interno se separan ingreso actual y origen y se utiliza FOR_ING_ACT=3. El manual 2025 ya está accesible en el respaldo consultado; se cierra en esta nueva versión la limitación de búsqueda normativa del reporte previo.

**E.** Las secciones revisadas no entregan una instrucción que justifique trasladar automáticamente estos ingresos 2024-T2/T3 a origen 2025. Las marcas operativas del Excel no sustituyen esa justificación. No se emite una rectificación ni se recalcula retención.

**B.** Carga proceso de matrícula 2025.pptx contiene una captura de PES: carga completada, 2025-05-08 22:23:44, 2.371 registros procesados de 2.371, con número de proceso en la URL 14923. El conteo coincide con la base MU2025 gobernada. La captura no identifica el hash del CSV ni los CODCLI y no demuestra identidad registro a registro por sí sola. La mención de SQL en ese registro corresponde al procesamiento/validación PES; no expone una consulta institucional que cambie la cohorte.

## Pendiente que permanece

**E.** Se identifica dónde se observa la reclasificación de 50 casos y la marca de corrección de otros 30; no se recuperó el código o la instrucción que autorizó el tratamiento. Falta la regla de preparación de MU2025 y su bitácora (responsable, fecha/hora, criterio, CODCLI/filas afectadas). Para los tres con otra matrícula falta el enlace a la matrícula exacta enviada. No se fabrican esas evidencias.

## Fuentes principales y hashes

- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/2025/Matricula/2 y 3er Intake.xlsx` — SHA-256 `0fa5983f2f8f574477a7d3ec34b892502ef51321e43d03534146bd0d4b2acf56`.
- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/2025/Matricula/SIES/06-05-2025/IPSS_Procesamiento.xlsx` — SHA-256 `e2984ccdf22ecf35c46e1f77275fdd12cda47bd2d77a523860e2cd2cf90127f4`.
- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/2025/Matricula/SIES/06-05-2025/BD Carga/Descarga de lo cargado_08-05-2025_22-26-22_Matrícula_Pregrado_2025.xlsx` — SHA-256 `21e1cfa96df6bb9b53ef99e7f6010a6db9e86ec7042b296fa254d965715b6392`.
- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/2025/Matricula/Manual_Matrícula_Unificada_2025.pdf` — SHA-256 `8cf7babc0e030a56dbb13df182195b8db047080ad467b537663a8c7af4000903`.
- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/2025/Matricula/SIES/06-05-2025/BD Carga/Carga proceso de matrícula 2025.pptx` — SHA-256 `2c92703ce892fe1485a8efd49fbf89fc9948a8c827667678dc461cf7075a5303`.
- `/Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx` — SHA-256 `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`.
- `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/DATOSDEALUMNOS_11998.xlsx` — SHA-256 `5d2df5e7998a4ec903e12d51b25114e8f1ff36da57cecaf623e90398b0828f35`.
- `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/DATOSDEALUMNOS_10246.xlsx` — SHA-256 `b175d63bd9e3280c5757fb0d7292e45fb594d8f076e277f2e06bad2b15e9d869`.
- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2025/2025.xlsx` — SHA-256 `9ceb4f3e15111a4d968410fcb799d56bd349a6e91a9d473d5a9cceedaab15062`.
- `/Users/alexi/Documents/GitHub/avance_curricular/DURACION_ESTUDIOS.tsv` — SHA-256 `701025451acf2f84078cf185d6ae0be0d8483d37e3b3e9483f70070397aebc6e`.

## QA y checkpoint

**C.** Controles OK: 40+10=50 con cambio 2024→2025 entre hojas; 30 marcados Corrección coinciden exactamente con los 30 de ingreso 2024-T3 en Detalle1; tres sin marca tienen otro CODCLI de ingreso 2025; grupos excluyentes, 50+30+3=83. Una fila por persona/carrera en cada hoja comparada. Hashes de fuentes originales y respaldos revalidados sin cambios. Los resultados almacenados son agregados y no incluyen RUT, CODCLI, MRUN, nombres de personas ni fechas de nacimiento. No se emitió un dictamen de carga ni una aprobación normativa.

**D.** Denominadores 558/1.150 y 222/124 intactos. Sin modificaciones al Excel, BASE_RETENCION_MU o fuentes. Sin commit/push. Solo derivados locales de este diagnóstico y una imagen extraída de la captura de PES en carpeta restringida ignorada por Git.

**B/C.** `/Users/alexi/Documents/GitHub/avance_curricular`: rama `feature/ire-2026`, HEAD antes/después `80ca13a5a249a1a2bd53a699f5f73689b1f53040`.

**B/C.** `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN`: rama `main`, HEAD antes/después `aba337784ccde0537fc21b2977b351170ed335e8`.
