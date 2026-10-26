# Resultado de la auditoría del diccionario UMAS–SIES

**B/C.** Auditoría del 25-10-2026 del servicio personal
`v7_20261023_inf35_03_t3`, rama `feature/ire-2026`.
El código T1 documentado se conserva. No se reasignaron versiones ni se
modificaron fuentes, motores, cohortes o denominadores.

## Respuesta ejecutiva

**B/C/D.** En los contextos localizados del seguimiento que alimenta las hojas
52–54 de V17 se reproducen 2.750 códigos de 2.854 observaciones: 96,36%.
Son 2.737 documentales anuales y 13 correspondencias internas aprobadas.
Las 104 pendientes corresponden a 58 personas y afectan 16 de 26 combinaciones
de carrera UMAS + plan + sede + jornada, en 12 códigos de carrera UMAS.
Al separar año/período existen 86 grupos, 42 con alguna observación pendiente.

**B/C/E.** El subconjunto de origen multiversión tiene 1.053 de 1.077
observaciones con código (97,77%), 24 pendientes, 16 personas afectadas y ocho
combinaciones sin año/período con pendientes. Está incluido en el total anterior.
Los pendientes se distinguen por origen y contexto posterior; no se atribuyen
automáticamente a una versión de la carrera de origen.

**B/C.** El histórico completo abarca 2019–2026, períodos nativos 1–5:
21.561 observaciones documentales + 164 solo internas = 21.725 de 24.774
(87,69%). Quedan 3.049 observaciones, 1.746 personas con algún pendiente.
De las 93 combinaciones: 30 completas, 59 parciales y cuatro sin resolver.
Los 63 grupos con pendientes actuales no son las 63 dimensiones de la prueba
histórica de dominancia, que tenía otra definición y población.

**B/C/E.** Una combinación completa significa todas sus observaciones revisadas
con código, no una equivalencia universal plan–versión. Existen 17 combinaciones
con varios códigos dentro del mismo año/período. Tres de ellas están completas:
se resuelven por persona y contexto, no seleccionando una versión para todo el grupo.

## Lo que falta

**B/C/E.** En V17: 63 observaciones tienen jornada candidata distinta del origen;
34, candidatos en otra carrera/sede/institución; cinco, familia de origen presente
sin atribución de versión/plan; dos, sin candidato/contexto de familia atribuido.
La diferencia de jornada es una excepción que investigar, no prueba automática
de error en la fuente.

**B/C/E.** En el histórico, el principal requisito registrado es acreditar la
asignación del plan al período y la continuidad, migración o reingreso: 2.650
observaciones. Los restantes requisitos suman 399. Hay 2.651 candidatos únicos
calculados no adoptados, uno de ellos una homologación en plan rechazado.
No se exige por esta auditoría un día exacto cuando una decisión contextual
acotada puede resolver el período; la decisión requiere autorización y evidencia.

**B/E.** El índice MU2022–2026 del servicio conserva 10.177 enlaces de 10.200 filas:
23 filas con tipo documental distinto de RUT no están resueltas por su adaptador.
No se eliminan de las bases ni se restan de denominadores. Esta limitación del
índice no se suma como si fueran 23 observaciones adicionales a las 3.049.

**B/E.** Aceptación SIES figura como no acreditada en este servicio. No significa
rechazo ni demuestra que los envíos no existieran: se distingue código observado
en las fuentes de prueba de envío/aceptación. Tampoco ausencia de contexto académico
equivale a deserción. La V17 conserva resultados históricos en hojas 30–51.

## GitHub, complemento y skills

**B.** HEAD local y remoto verificados: `55e3b709afb9483f0ecdd2d166f67229a454a5ef`.
El servicio personal v7, sus consumidores, documentación y versiones existen
localmente sin seguimiento Git. Su clave de `PROYECTO_IPSS.json` está en cambios
pendientes. No corresponde afirmar que el servicio v7 ya esté publicado.

**B/C.** C2_20261016 sí está publicado, pero declara
`asignacion_productiva=false`; es una capa distinta. El adaptador local del módulo
Caracterización consulta el mismo servicio. No se debe crear otra copia del diccionario.

**B/E.** El complemento remoto Análisis institucional de Alexi v1.1.3, del
21-10-2026, fue verificado mediante su paquete: 1.317 archivos de texto, sin
referencias al servicio v7. Las skills relevantes tampoco acreditan conexión
automática. Los complementos GPT heredados se revisaron en caché; su remoto actual
no fue comprobado. Una búsqueda manual eventual no acredita sincronización común.

## Validación y reproducción

**C.** Se ejecutaron 24.774 consultas históricas y 2.854 consultas de V17 sin
diferencias; tres consumidores dieron la misma respuesta en ejemplos documental,
interno y pendiente. Pasaron 12 pruebas sintéticas. Coinciden los hashes de las
79 entradas fijadas en el descriptor y de la base privada y componentes activos.

**C.** El nuevo Excel tiene cinco hojas, cuatro tablas con filtro y 551 fórmulas
con caché. Se comprobó propagación de un cambio de entrada al resumen y se restauró.
Recálculo en Artifact Tool, lectura independiente del XLSX con openpyxl, validación
ZIP/XML, tablas y sumas. No se realizó apertura nativa en Microsoft Excel. Estas
pruebas verifican reproducción y aritmética; no resuelven las dudas documentales.

Procedimiento local, con dependencias suministradas por Codex:

1. `auditar_cobertura.py`: lee el diccionario activo, verifica consultas y genera
   únicamente agregados en `insumos/`.
2. `auditar_capas.py`: lee C2 y V17, reconsulta contextos y genera `insumos/capas.json`.
3. `verificar_consulta.py`: contrasta consumidores, pruebas y hashes sin alterar fuentes.
4. `build.mjs`: crea el Excel desde los agregados usando `@oai/artifact-tool`.
   Vincular temporalmente `node_modules` al runtime indicado por
   `load_workspace_dependencies`; no copiar dependencias al repositorio.
5. `validar_entrega.py`: revisa archivo guardado y privacidad, genera QA/manifiesto
   y verifica la copia del Escritorio.

La auditoría remota de complementos es evidencia puntual en `insumos/gobierno.json`;
para actualizarla se debe volver a consultar el conector, no asumir vigencia por la caché.
Las fuentes privadas siguen siendo necesarias localmente para reproducir el cruce;
el informe no las incluye ni las publica.

**B/C.** La V17 conserva SHA-256
`8b461d53f75ac26e2e38aa46d0aae921736d21ac2a64034cfd26c08495756a52`.
Los hashes de la nueva entrega están en `MANIFEST.json` y `QA_ENTREGA.json`.
Se preservaron los tres cambios de trabajo previos. No se hizo commit ni push.

## Checkpoint

**E.** Quedan tres tareas diferentes: resolver excepciones de contexto, incorporar
el servicio y su contrato no personal a GitHub con autorización, y conectar los
complementos/skills al puntero común con prueba de consumo. Ninguna se declara
ejecutada por este informe. No hay cambios nuevos de reglas o equivalencias.
