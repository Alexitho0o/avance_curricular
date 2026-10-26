# Plan trazable para cerrar el puente UMAS → código único SIES

Estado: PLANIFICADO / pendiente de ejecución y aprobación de gobernanza.
Fecha: 2026-10-22.

## Objetivo

Construir y validar un diccionario agregado que relacione `CODCLI`/`PLAN_DE_ESTUDIO` con `COD_SED + COD_CAR + JOR + VERSION`, sin modificar fuentes originales, denominadores ni cálculos de retención.

## Fase 0 — Congelamiento de entradas

Entradas:

- catálogo SIES 2027;
- oferta histórica SIES;
- `PROMEDIOSDEALUMNOS_12166.xlsx`;
- `BASE_RETENCION_MU_2022_2026`;
- tabla puente y QA ya generados.

Validaciones:

- existencia y hash de cada fuente;
- encabezados y llaves;
- separación entre `VERSION` y `VIGENCIA_CARRERA`;
- ninguna fuente original se modifica.

Puerta de salida: todas las fuentes identificadas y hashes registrados.

## Fase 1 — Reproducción del cruce individual

Método:

`CODCLI + PLAN_DE_ESTUDIO + RUT/DIG` en PROMEDIOS → `N_DOC/DV` en MU → código único SIES.

Validaciones:

- RUT normalizado sin alterar el valor original;
- coincidencia exacta de RUT/DV;
- control de duplicados por persona, plan y año;
- ningún identificador pasa al archivo agregado.

Salida: tabla agregada por carrera interna, plan, año y código único.

Puerta de salida: el resultado reproduce los conteos observados y no duplica personas.

## Fase 2 — Resolución de las 11 dimensiones con coincidencia

Para cada dimensión:

1. ordenar versiones por número de personas coincidentes;
2. calcular proporción de la versión predominante;
3. comparar tipo de plan y duración;
4. revisar primer año de actividad en oferta histórica;
5. clasificar como propuesta interna o pendiente.

Regla de trabajo propuesta:

- propuesta interna si la versión concentra al menos 90% y existen al menos 3 personas;
- pendiente si hay menos de 3 personas o distribución cercana.

Puerta de salida: ningún caso se asigna solo por nombre o por volumen MU.

## Fase 3 — Diagnóstico de las 13 diferencias sin match

Para cada dimensión sin coincidencia:

- revisar cobertura temporal de MU;
- revisar si el plan aparece solo en años anteriores;
- revisar jornada, sede y código de carrera;
- verificar formato de RUT/DV;
- comprobar si PROMEDIOS y MU corresponden al mismo período.

Resultados posibles:

- cobertura temporal insuficiente;
- diferencia de llave;
- plan no informado en MU;
- sin causa demostrable.

No se transforma ausencia de match en cero estudiantes ni en deserción.

Puerta de salida: cada diferencia queda con causa observada o estado E pendiente.

## Fase 4 — Control de totales

Comparar antes/después:

- total de filas MU por año;
- total `VIG=1` por año;
- suma por código único;
- suma por carrera y jornada;
- denominadores y retenidos de retención;
- titulados observados en PROMEDIOS.

Criterio de aceptación:

- diferencia cero en totales MU;
- diferencia cero en denominadores y retenidos;
- ninguna duplicación;
- toda diferencia explicada por cobertura o clasificación pendiente.

Si falla un control, detener el proceso y no avanzar.

## Fase 5 — QA independiente

Ejecutar una segunda lectura con una implementación independiente y comparar:

- número de dimensiones;
- candidatos por dimensión;
- asignaciones propuestas;
- pendientes;
- totales y porcentajes.

Clasificación:

- B: dato observado;
- C: cálculo reproducido;
- D: decisión interna;
- E: hipótesis o pendiente.

Puerta de salida: dos cálculos independientes coinciden.

## Fase 6 — Diccionario gobernado

Solo después de aprobar las fases anteriores:

- generar diccionario agregado definitivo;
- agregar manifiesto con fuentes, hashes, regla y responsables;
- documentar cambios de regla con fecha y hora;
- registrar versiones no resueltas;
- mantener separado cualquier archivo individual sensible.

## Fase 7 — Actualización controlada

Solo con aprobación explícita:

- actualizar reglas de negocio;
- actualizar SQL, complementos y skills;
- agregar pruebas de regresión;
- ejecutar QA completo;
- commit explícito por archivo;
- push solo con autorización posterior.

## Condición de cierre

El puente solo se declara cerrado cuando:

- todas las dimensiones están asignadas o justificadamente pendientes;
- los totales MU y de retención calzan al 0%;
- los titulados tienen referencia comparable o quedan expresamente pendientes;
- el diccionario es reproducible desde las fuentes gobernadas.
