# Seguimiento del Excel con código T1 documentado

## Alcance autorizado

D: solicitud de Alexi del 23-10-2026. Retomar el Excel de retención intertrimestral
usando el código MU/T1 de origen; revisar únicamente excepciones de carrera,
jornada o plan. No modificar bases, cohortes, denominadores ni el diccionario.
Sin commit, push, publicación ni datos individuales nuevos en Git.

## Entradas y conservación

B: versión V12 en outputs/aplicacion_diccionario_intertrimestral_20261023_125556/,
descriptor activo v7 y evidencias privadas enlazadas por su manifiesto. El respaldo
AUDITADO_ENTREGA conserva los indicadores individuales de las fotos. Los archivos
se verifican por hash y permanecen intactos.

C: generar V13 conservando las hojas 1–51 y sus objetos exactamente. Actualizar
las hojas existentes 52–54, sus dos tablas, fórmulas y notas. No crear otra
auditoría histórica ni nuevos cierres de versión. Conservar las 3.179 filas T1
(558, 1.150 y 1.471), distinguiendo la población de los denominadores particulares
ya existentes. Los 1.294 ingresos T2/T3 quedan preservados fuera de esta aplicación.

## Seguimiento y excepciones

C: código de origen y código de destino son campos distintos. El primero no se
vacía por una duda del segundo. Consultar la entrada común del proyecto y fijar
edición/hash; reaplicar solo decisiones ya aprobadas, sin elegir por totales,
primera fila, versión máxima o año del plan. Respaldo documental, aprobación
interna y pendiente permanecen separados.

B/C: el libro vigente usa actividad 2025-2/3 para la fila 2024, actividad 2025-2
y foto T3-2025 para 2025, actividad 2026-2 y foto T3-2026 para 2026. Mantener y
rotular año de origen y de observación. Un período nativo de PROMEDIOS no acredita
por sí mismo una foto de matrícula al cierre.

C/E: desglosar los indicadores existentes por código T1 solamente si se reproduce
su numerador, denominador y población desde las fuentes. Una discrepancia no se
corrige ni se encubre; el desglose afectado queda pendiente. La ausencia de
contexto no prueba deserción. Diferencias de dimensiones entre respaldos no
acreditan por sí solas la fecha efectiva de un cambio.

## QA y entrega

C: contrastar valores y fórmulas con agregación independiente; comprobar totales,
ausencia de doble conteo dentro de cada población, decisiones v7, negativos y
pendientes. Validar XML, tablas/filtros, fórmulas con resultados y conservación
de las partes no autorizadas. Revisar visualmente las tres hojas modificadas.
Copias idénticas en outputs y Escritorio, manifiesto y punto de reanudación.
Identificadores disponibles únicamente en evidencia local privada fuera de Git.
