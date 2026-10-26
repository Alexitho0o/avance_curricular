# Auditoría del embudo de las 2.317 personas

## Resultado verificable
Se limita a las 2.317 personas y 4.973 observaciones pendientes; no se amplía a las otras 3.584 personas. Se reutilizan índices del privado V 3 y se auditan 19 archivos dirigidos: 14 nuevos y 5 reprocesados del conjunto inicial. Total 52 archivos distintos. No hubo inaccesibles. Se añaden 5.292 evidencias con código completo, varias duplicadas/corroborativas; NO son personas nuevas.

Recuperación de las 1.016 personas antes sin código: 0 nuevas. Recuperación de observaciones anuales pendientes: 0. No se declara cierre de plan ni se modifica canon. Esto NO prueba ausencia en toda fuente existente: prueba no localización en cobertura identificada y revisada, que sigue siendo acotada.

## Dónde se pierde el enlace
|Primer punto/causa de observación|Observaciones|Personas con esa causa (solapables)|
|---|---:|---:|
|Código existente distinto de inferencia dominante|1.760|556|
|Código único, atribución de expediente/identidad múltiple|86|22|
|Código anual existente, DA no concordante|15|2|
|Código misma familia, pero otra fecha/proceso|1.472|696|
|Código solo de otra carrera/sede/jornada|261|115|
|Ningún código localizado tras cobertura acotada|1.379|1.016|

Suma de observaciones 4.973. Personas únicas 2.317; 90 tienen más de una causa secundaria. Para una partición exclusiva de personas se aplica prioridad explícita de primer bloqueo: sin código 1.016; otra familia 115; temporal 690; atribución múltiple 15; DA 2; diferencia de inferencia 479. Suma 2.317. Esta prioridad contable no elimina sus otras causas. La clasificación anterior de las 1.821 personas sin anual priorizaba misma familia y daba 696/109/1.016; son las mismas personas, otra prioridad. No interpretar la diferencia de 6 personas como mejora/pérdida.

## Omisiones y correcciones técnicas comprobadas
- A_CURRICULAR_2017_162.xlsx, 2018 y 2019: el lector anterior buscaba NUM_DOCUMENTO/N_DOC y no reconocía RUN ni «Código de la carrera asociado al estudiante». Se incorporan 436 filas del grupo. Encabezado fila 7 acredita actividad académica 2016,2017,2018 respectivamente: se recupera esa semántica concreta sin generalizarla automáticamente a otros años.
- CSV MU 2026 sin encabezados: se incorporan solo después de contrastar el esquema 32 del XLSX SUBIDAS_REALIZADAS_4165 y exigir concordancia exacta identidad+código de todas sus filas. La carga 4070 y complemento 95 son fuentes adicionales, no personas adicionales. Ceros existentes se conservan en los originales; las llaves normalizadas no reemplazan los valores fuente.
- TRAZABILIDAD_DATOSALUMNOS contiene componentes prefijados SIES_/FUENTE_/MATRIZ_. Se incorporan los 405 códigos completos presentes en el grupo; se conserva el rol y la condición de derivado.
- CSV Titulación Unificada 2026: sin encabezados,23 campos. Se usa esquema explícito del CSV de titulación 2022 y se documenta cotejo parcial con XLSX 2026:397/431 filas coinciden en identidad y dos códigos. Se conserva esta limitación y las variantes; no se certifica aceptación ni igualdad entre versiones. Aporta 148 evidencias al grupo, ninguna nueva persona sin código. No se trata la falta de encabezado como ausencia de estudiantes.
- Los archivos «A. C. Matrícula 2024» de la carpeta 2025, con nombre aparentemente individual, contienen tabla de carreras/planes: CODIGO_UNICO,PLAN_ESTUDIOS,duración/unidades, sin RUT/CODCLI. No pueden identificar personas; no se forzó el cruce.
- «TIT_IP_CIISA_2024 …csv» de 470 bytes contiene agregado de carrera, no detalle individual. El XLSX de titulados 2024 y los CSV individuales de 2022/2023 sí estaban incorporados. No se presume que el nombre de archivo garantice contenido ni año de actividad.

## Cobertura realmente comprobada
Matrícula publicada individual 2010–2021 ya incorporada; base gobernada 2022–2026 ya incorporada. Se contrastan ahora originales/enviados 2022,2023,2024,2025, cierres/cargas/complemento 2026 y julio 2026. Titulados: históricos con periodos 2007–2024, extractos 2010–2022, cargas 2022/2023, XLSX 2024 y archivos proceso 2026. No se acredita un archivo individual autónomo de proceso 2025; la precarga histórica y las otras fuentes no garantizan cobertura exhaustiva de ese proceso. Avance: extractos 2017–2022 y cargas 2022–2024/precarga y revisión 2026; se corrigen RUN 2017–2019. Los archivos 2025 inspeccionados son de carreras, no sustituyen detalle individual. Retención agregada/MRUN sin puente exacto no identifica RUT. PROMEDIOS y DA aportan identidad,CODCLI,plan y actividad, pero no inventan código SIES si falta el registro de proceso.

INVENTARIO_DIRIGIDO.json conserva lectura por hoja, filas, coincidencias y límites. HASHES_FUENTES.json fija las fuentes nuevas/reprocesadas; la cobertura inicial consta en el privado V 3/hoja COBERTURA_SIES. Hojas de resumen/dinámicas sin llave no son fuentes individuales. No se declara que se inspeccionó exhaustivamente todo archivo del Mac.

## Identidad, expediente y filtros
Todos los 2.317 RUT/DV del grupo pasan dígito verificador. En fuentes nuevas no apareció el mismo cuerpo con otro DV que explique las 1.016 ausencias. Esto descarta esas variantes en la muestra revisada, no cualquier error imaginable. Ninguna asignación se hizo por nombre,sexo,nacimiento ni totales agregados.

Las 86 alertas tienen UN código anual; el punto de pérdida es atribución, no código contradictorio. Falta secuencia CODCLI/periodo/carrera o puente explícito de matrícula. Los 2 casos DA necesitan fila concordante por CODCLI+RUT+CODCARPR+SEDE+JORNADA; existen 15 observaciones con código anual. Las 556 personas con código distinto requieren revisar la inferencia fija; el código ya está documentado. No se aplica 90% ni muestra mínima al enlace directo.

En las 696 personas con misma familia fuera del año/proceso, el filtro V 6 sí es la igualdad anual MU más tipo de proceso MATRICULA: se recuperó el código histórico pero no se lo presentó como matrícula contemporánea. Otras 1.462 observaciones tienen matrícula misma familia en otra fecha;946 avance y 511 titulados (superpuestos). La evidencia de título puede acreditar titulación/carrera; para extenderla al año de matrícula se necesita regla temporal o historial que lo sostenga. Los encabezados 2017–2019 prueban años académicos 2016–2018, anteriores al foco PR 2019–2026: no rescatan estas ausencias anuales. La validez de la misma traducción para otros archivos permanece por verificar.

El plan vigente no fue filtro para recuperar código. PLAN_DE_ESTUDIO de PR y PLAN_ESTUDIOS del proceso no se igualan por nombre ni se retrotraen automáticamente. docs/fase_4_planes_asignaciones_umas.md puntos 4–7 pide distinguir cortes y asignación efectiva; docs/resultados_fase_b_equivalencias_historicas.md permite una relación documental explícita sin deducir atributos secundarios. Esa regla no obliga a exigir duración ni n 3/90 a un enlace probado. VIG tampoco fue filtro de recuperación. Fuentes derivadas o «Enviados» no se convierten en comprobante individual de aceptación.

## Acciones concretas
1. Código distinto: contrastar versión fija contra el registro observado y resolver por contexto, sin cambiar canon por mayoría.
2. Atribución múltiple: secuencia de matrícula/CODCLI y periodo; no asumir conflicto real por dos expedientes.
3. DA: localizar fila del expediente y su sede/jornada/identidad; no reasignar desde otra carrera.
4. Temporal: documentar periodo representado por cada carga de avance y evento de titulación; aprovechar evidencia exacta para lo que efectivamente acredita.
5. Otra familia: acreditar traslado/cambio de carrera/jornada; no copiar código entre familias.
6. Sin código: recuperar carga/rectificación individual del año y cobertura efectiva, especialmente proceso 2025/2026 y cortes adicionales; aún no hay evidencia que permita atribuirles código. Un total de carrera/año no resuelve su identidad.

## QA, clasificación y límites
Recuperado documentalmente NUEVO en este tramo:0 personas/0 observaciones anuales. Código ya localizado pendiente de atribución:1.301 personas (3.594 observaciones). No localizado después de cobertura comprobada ACOTADA:1.016 personas (1.379 observaciones). Fuente inaccesible atribuible a persona:0 casos demostrados; no equivale a exhaustividad universal. Estos dos grupos de personas son disjuntos.

Los hashes se comprueban antes/después. QA comprueba partición 4.973/2.317 y mantiene el universo fijo sin cambiar denominadores. Los libros finales V 6 y privadoV 3 quedan intactos. Se entrega diagnóstico actualizado agregado y detalle privado del embudo fuera de Git. Sin commit,push,uploads,canon,tasas ni denominadores modificados.
