# Entrega V17 · 24-oct-2026

D: publicación autorizada exclusivamente de esta entrega agregada.
B/C: QA_Y_MANIFEST.json conserva la evidencia previa a publicación; su frase
«sin commit ni push» describe ese momento. PUBLICACION.json registra este paso.

La V17 agrega 55_Pendientes_entrega; las 54 hojas anteriores, fórmulas,
13 gráficos, 35 tablas, bases agregadas y denominadores permanecen intactos.
E: las 66 renuncias siguen pendientes de respaldo individual. No se presenta
la entrega como conciliación completa ni como aceptación de SIES.

## Reproducción de esta ampliación
C: los scripts conservan las rutas de la ejecución original. Se requiere la
V16 local cuyo hash está en QA_Y_MANIFEST.json y el runtime Artifact Tool.
Preparar /tmp/retencion_v17 con acceso a @oai/artifact-tool, ejecutar build.mjs
y luego assemble.py con Python y lxml/openpyxl (solo lectura de verificación).
El ensamblador rechaza sobrescribir la salida o la copia del Escritorio; para
reproducir, usar rutas de salida nuevas en una copia de los scripts. No ejecutar
sobre fuentes ni entregas existentes. Esto reproduce la ampliación, no toda
la historia de cálculos de V16. Las fuentes individuales no se publican.

C: commit preparado sobre la base remota para excluir tres commits locales
previos. No se hace merge, reset ni cambio de rama del checkout del usuario.
