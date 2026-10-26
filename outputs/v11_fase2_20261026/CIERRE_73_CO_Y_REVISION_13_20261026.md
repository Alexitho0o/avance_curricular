# Candidata v11: decisión de Concepción y revisión de 2025

- **D:** Alexi aprobó el 26-10-2026 73 correspondencias internas de Concepción V1; el alcance específico y sus límites constan en `DECISION_73_CO_V1_20261026.md`. No implica aprobación de otras observaciones ni acreditación de envío SIES para T2/T3.
- **B/C:** En la candidata hay 41 contextos COTEIQ (`I162S3C114J2V1`), 21 COTFAR (`I162S3C115J2V1`) y 11 COTENS (`I162S3C91J2V1`): 26 de T2 y 47 de T3, correspondientes a 51 personas y 51 expedientes. El soporte y los hashes previos están en `EVALUACION_CIERRE_CO_V1_AGREGADO_V2.json`.
- **C:** Se generó una copia privada nueva del SQLite candidato; se contrastaron las 25.900 filas, los componentes de identidad y las 12.207 filas de matrícula anual. Solo 73 payloads cambian y solo en los campos autorizados; integridad SQLite correcta. La candidata previa y el puntero activo no se alteraron. Ver `QA_CIERRE_73_CO.json`.
- **C:** Tres consumidores devolvieron respuestas iguales en tres consultas de prueba, incluyendo una decisión CO; 12 pruebas unitarias existentes pasaron. No se trata de una prueba exhaustiva de todos los consumidores ni de QA integral de activación.
- **E:** La candidata permanece no activa; siguen pendientes los demás controles de QA, las dos llaves ambiguas y la conciliación integral de posiciones. La atribución documental al trimestre, aceptación SIES y vigencia al cierre no se infieren de esta decisión.

## Trece contextos de 2025

- **B/C:** Son 13 contextos, 8 personas y 8 expedientes: TENS 5 en T2 y 2 en T3; TPAS 3 en T2 y 3 en T3. No son 13 personas.
- **B/C:** Los 13 tienen un código MU2026 único de la familia observada, ingreso actual no posterior a 2025, un plan observado en los archivos evaluados y oferta del código en 2025. Ver `EVALUACION_TRECE_MU2026_AGREGADO.json`.
- **B/C:** En cada uno de los dos respaldos de Datos Alumnos 2026 se observan el mismo CODCLI, carrera y jornada de destino; cada persona tiene un único CODCLI en cada respaldo revisado. Esta unicidad se limita a esos respaldos y no acredita ausencia de otros expedientes en otras fuentes. Ver `REVISION_TRECE_EXPEDIENTES_AGREGADO.json`.
- **E:** Los respaldos 2026 y el código anual posterior no demuestran por sí solos el código documental asignado al expediente en el trimestre de 2025 ni la fecha efectiva del cambio. La decisión v10 aprobó 27 casos concretos; no se extiende automáticamente. Los 13 permanecen pendientes y constituyen posibles correspondencias internas a evaluar dentro de un criterio autorizado.
- **E:** Para atribución documental al contexto faltaría una fuente individual fechada de 2025 que una identidad y expediente/plan con la carrera, sede, jornada y versión SIES, o documentación equivalente del cambio. No se presupone que la fuente exista.

La revisión no modifica fuentes, denominadores o bases originales; no activa el diccionario ni realiza commit o push. Los detalles individuales permanecen bajo `~/.local/share/ipss/v11_fase2_20261026/`.
