# Dos cierres V2 autorizados y revisión de homologaciones

Proceso: correspondencia interna UMAS/SIES; observaciones académicas 2024.
Decisión D de Alexi; ejecución C, 2026-10-23T09:15:09.484175-03:00.

| Plan / período | Resultado | Respaldo |
|---|---|---|
| TTMREOL20231 / 2024 bimestre 3 | I162S2C6J4V2 adoptado internamente | B actividad aprobada; C/D aplicación autorizada |
| TTMREOL20231 / 2024 bimestre 5 | I162S2C6J4V2 adoptado internamente | B actividad aprobada; C/D aplicación autorizada |
| TCRE20241 / 2024 trimestre 1 | Pendiente; V2 sigue candidato, no adoptado | B homologaciones y rechazo de actualización; E atribución |

Las tres observaciones pertenecen a una persona. No se suman matrículas como
personas ni se confunden bimestres y trimestres. Atribución documental pendiente
en las tres; ninguno de estos cierres acredita envío o aceptación SIES.

## Homologaciones: qué prueban y qué no — B/C/E

Se releyeron todas las filas de PROMEDIOS de esa identidad. El expediente TCRE
solo presenta cinco filas HOMOLOGADO, CONVALIDADO=S, plan TCRE20241, año 2024,
período 1. Las cinco tienen ESTADO_ACADEMICO=ELIMINADO en ese reporte.
RAMOEQUIV y CODRAMO relacionan códigos de asignaturas: en
3 de las cinco se localizó un ramo previamente aprobado
de la misma persona con código exacto; en 3 coincidió también la nota.
El detalle conserva alternativas y localizadores, sin deducir por prefijos de ramo
la carrera o versión SIES. No es una equivalencia universal de planes.

La copia de DATOSDEALUMNOS_12159 recuperada en el Escritorio tiene el mismo
SHA-256 que el original del manifiesto, antes referenciado en Descargas.
En Hoja1, fila 7179, el expediente TCRE figura ELIMINADO y
**9 - RECHAZO ACTUALIZACION DE PLAN 2024**. Declara matrícula 2024/período 1 y
fecha de matrícula 05-02-2024. Esta fecha no es fecha de rechazo ni fecha efectiva
de migración; no se dispone de historia fechada de esa transición.

La persona conserva V2 único en MU2023, MU2024 y MU2025, pero eso no atribuye
por sí solo el código al expediente TCRE. Las homologaciones prueban registros
de reconocimiento en el plan destino; no bastan para afirmar que ese cambio
quedó efectivo, especialmente ante la situación explícita de rechazo. No se
las convierte en cursado ni en retención. La tercera observación sigue E.
Falta evidencia de efectividad del plan para ese expediente/período o una decisión
interna explícita para clasificar también reconocimientos de cambios rechazados.
No se presume rechazo vigente durante todo 2024 ni se elimina la observación.

## Conteos posteriores — C

- Pendientes internos: 3.090 → **3.088 observaciones**, **1.750 personas**, sin cambio.
- Una persona parcialmente resuelta; ninguna persona completamente resuelta nueva.
- Documentales: **3.213 observaciones / 1.838 personas**, intactos.
- Universo aprobado: 5.901 personas, 6.622 expedientes y 24.774 observaciones.
- Bases, libros, tasas y denominadores de retención sin cambios.

## Aplicación, QA y reanudación

Los dos cierres están materializados en la capa diagnóstica local privada;
no son solo una simulación. Cargar la base fijada por hash y superponer
ADJUDICACIONES_ACUMULADAS.json (cuatro decisiones F02 previas más estas dos),
verificando estado_antes. Repetición idempotente; estado incompatible rechazado.
Para revertir solo este cierre, omitir las dos adjudicaciones nuevas.

QA OK_CON_ADVERTENCIAS: exactamente dos cambios de campos internos; tercer
registro, documental, fuentes y F02 intactos. Identificadores fuera de Git.
Advertencias: atribución documental y tercera observación pendientes.
Registro local reproducible, no publicado en GitHub. Sin commit/push.
