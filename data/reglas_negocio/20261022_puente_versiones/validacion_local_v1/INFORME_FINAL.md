# Auditoría del puente UMAS–SIES, 2026-10-22

**NO CERRADO — PENDIENTE_APROBACION_GOBERNANZA.**

C/E: Las 39 propuestas previas se conservan como antecedentes. No son 39 equivalencias aprobadas. Hay 11 pendientes múltiples/baja cobertura y 13 sin match en los candidatos, total 63. No se promovió ninguna dimensión.

| Fase | Estado | Evidencia o pendiente |
|---|---|---|
|0|COMPLETA|Fuentes y derivados inventariados con SHA-256; cobertura y llaves documentadas.|
|1|EJECUTADA; PUERTA CON OBSERVACIONES|Cruce local exacto; 2 diferencias frente al derivado anterior con causa aún no acreditada.|
|2|EJECUTADA; 11 PENDIENTES|Ninguna supera simultáneamente las condiciones; faltan atributos UMAS acreditados.|
|3|EJECUTADA; 13 PENDIENTES|9 dimensiones con cobertura temporal fuera de MU; 4 sin evidencia suficiente.|
|4|PARCIAL; PROMOCIÓN DETENIDA|Cero diferencia MU y conservación de hashes. Retención conservada, pero conciliación semántica puente/denominadores/retenidos/tasas no acreditada.|
|5|QA COMPUTACIONAL PASS; GOBERNANZA BLOQUEADA|Segunda lectura y SQL coinciden en conteos, duplicados y agregados; no acredita equivalencias.|
|6|BLOQUEADA|No se genera diccionario definitivo porque faltan controles semánticos y acreditación de planes.|
|7|PREPARADA; NO APLICADA|Borradores de reglas, SQL, complementos, skills, regresión y bitácora.|

## Resultados de las 11 dimensiones (C/E)

| Carrera | Jornada | Personas | Predominio | Resultado |
|---|---:|---:|---:|---|
|ICRE|2|22|88.0000%|PENDIENTE|
|IINF|1|49|83.6364%|PENDIENTE|
|IINF|2|56|87.0968%|PENDIENTE|
|NCONRE|2|2|100.0000%|PENDIENTE|
|NINFREOL|4|1|100.0000%|PENDIENTE|
|TCRE|1|1|100.0000%|PENDIENTE|
|TCRE|2|11|78.5714%|PENDIENTE|
|TPCRE|1|1|100.0000%|PENDIENTE|
|TPCREOL|4|1|100.0000%|PENDIENTE|
|TTMRE|1|6|55.5556%|PENDIENTE|
|TTMRE|2|25|75.0000%|PENDIENTE|

Los porcentajes usan incidencias persona–código, con personas únicas y multicódigo separadas en el CSV. Cinco dimensiones tienen menos de tres personas y seis quedan bajo 90%. Tipo y duración de la malla UMAS no están acreditados por estas fuentes.

## Diagnóstico de las 13 dimensiones (B/C/E)

| Carrera | Jornada | Años PROMEDIOS | Causa |
|---|---:|---|---|
|ICRE|1|2023;2024;2025;2026|ausencia de evidencia|
|IETMRE|1|2019;2020;2021;2022;2023;2024;2025|ausencia de evidencia|
|NAUTRE|2|2019;2020;2021|cobertura temporal|
|NECIRE|2|2019;2020|cobertura temporal|
|NETMRE|2|2019|cobertura temporal|
|NETMRE|4|2019|cobertura temporal|
|NICCRE|2|2019;2020;2021|cobertura temporal|
|NICCREOL|4|2020;2021|cobertura temporal|
|NICIRE|2|2019|cobertura temporal|
|NINFRE|2|2019;2020;2021|cobertura temporal|
|NITMRE|2|2019|cobertura temporal|
|TPCRE|2|2019;2020;2021;2022|ausencia de evidencia|
|TPCRE|4|2019;2020;2021;2022|ausencia de evidencia|

La cobertura se observa por carrera interna; PROMEDIOS no aporta sede. No se atribuye automáticamente a una jornada a partir de la identidad. Los códigos candidatos fijan sede, carrera, jornada y versión de cada dimensión. MU no informa plan. Los respaldos gobernados prueban actividad, no equivalencia acreditada. No hay diferencias de formato RUT/DV demostradas como causa de estas 13 dimensiones.

## Controles (C)

| Año | Total MU | VIG=1 | Diferencia antes/después |
|---|---:|---:|---:|
|2022|1038|1033|0|
|2023|1145|1142|0|
|2024|1541|1455|0|
|2025|2371|2298|0|
|2026|4105|3145|0|

También se controlaron código único, carrera, sede y jornada en FASE4_TOTALES_Y_BRECHAS.csv. VIG=1 y total MU son universos distintos: su diferencia no es un error de conservación.

El cruce temporal tiene 8.469 incidencias persona/carrera/plan/año/periodo sin match del mismo año; no son 8.469 personas distintas. Se eliminaron 38.802 repeticiones del grano desde filas de asignaturas, sin modificar fuentes. Ningún CODCLI+plan se vincula a más de un RUT en PROMEDIOS.

Las diferencias previas están en IECIRE S2/J4 y IECIREOL S2/J4: para V2, 23→22 y 243→241. La prueba adicional incluyendo documentos P no reproduce los conteos antiguos. La causa sigue pendiente de revisar el método original y su deduplicación. No se interpreta como pérdida de matrícula.

E: No se recalcularon tasas ni denominadores. Se verificó conservación de los 61 resultados JSON/CSV existentes de retención; esto no acredita una conciliación semántica con el puente. Titulados observados se informan por persona y año de observación académica, no como año oficial de titulación.

## QA independiente (C/E)

Python con conjuntos y una segunda lectura con SQLite coinciden exactamente en distribuciones, agregados por plan/año/periodo, duplicados y controles MU. Las fuentes conservan sus hashes. 63 dimensiones y 141 pares dimensión/candidato. QA computacional PASS; promoción BLOQUEADA. La segunda implementación comparte el lector XLSX, pero usa otro normalizador y motor de agregación.

## Pendientes exactos

- Acreditar tipo y duración de cada plan UMAS, sin inferirlos del nombre, nivel máximo o versión.
- Validar temporalidad, sede/jornada del plan y correspondencia exclusiva de cada matrícula; un RUT puede aparecer en varias carreras/versiones.
- Resolver los dos desajustes de conteo con el método original y evidencia institucional; no aceptar P como RUT.
- Aportar MU histórica comparable para las nueve dimensiones fuera de 2022–2026 y evidencia para las otras cuatro.
- Conciliar denominadores, retenidos y tasas por su universo vigente antes de promover.
- Designar responsable de gobernanza y aprobar expresamente la nueva regla.

## Preservación y archivos

No se modificaron originales, BASE_RETENCION_MU, denominadores ni tasas. No hubo commit, push, cambio de rama ni carga a servicios externos. Cambios preexistentes preservados. Cruces individuales solo en memoria local; salidas agregadas.

Inventario con rutas y SHA-256: SHA256_ENTREGABLES.json. Fuentes: FASE0_FUENTES.json. Estados Git: GIT_ANTES.json y GIT_DESPUES.json. Tabla de 63: TABLA_63_DIMENSIONES.csv. Borradores: FASE7_CAMBIOS_PREPARADOS.md y SQL_BORRADOR.sql.
