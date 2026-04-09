# Evaluacion de reutilizacion de Matricula Unificada para Avance Curricular

Proceso actual: Avance Curricular SIES 2026.

Objetivo: evaluar si las fuentes y metodos usados en Matricula Unificada y Estudiantes Extranjeros pueden apoyar los campos pendientes de Avance Curricular 2026. Esta evaluacion no implementa pipelines, no precarga resultados y no genera PES.

## 1. Criterio usado

Se separaron cinco categorias:

- Reutilizacion de fuente: archivo institucional o salida auditada que puede aportar datos.
- Reutilizacion de llave: identificador o llave compuesta con evidencia de uso.
- Reutilizacion de codigo: funcion generica de lectura, normalizacion, auditoria o validacion.
- Reutilizacion de metodologia: trazabilidad, conciliacion, manifest, control de duplicados.
- Reutilizacion de resultado: uso de salidas historicas como evidencia o contraste, no como norma.

La evaluacion detallada esta en:

- `avance_curricular_2026/07_control/FUENTES_REUTILIZABLES_DESDE_MU.tsv`
- `avance_curricular_2026/07_control/EVALUACION_REUTILIZACION_MU_PARA_AVANCE.tsv`
- `avance_curricular_2026/07_control/COBERTURA_FUENTES_MU_PARA_AVANCE.tsv`
- `avance_curricular_2026/07_control/INVENTARIO_LLAVES_MU_EXTRANJEROS.tsv`
- `avance_curricular_2026/07_control/INVENTARIO_CODIGO_REUTILIZABLE_MU.tsv`

## 2. Fuentes evaluadas

### PROMEDIOSDEALUMNOS_7804.xlsx

Estado: encontrada y usada historicamente por Extranjeros.

Hojas:

- `Hoja1`: historial persona-asignatura con `CODCLI`, documento, codigo de carrera, ramo, asignatura, nota, periodo, estado, convalidacion, estado academico y plan observado.
- `DatosAlumnos`: datos persona-carrera con `CODCLI`, documento, carrera interna, matricula, ingreso, estado academico y situacion.
- `matriz`: catalogo carrera/programa con `CODIGO_UNICO`, modalidad, jornada, duracion y vigencia.
- `base_datos`: equivalencia parcial documento/DV/`CODCLI`.

Uso posible para Avance:

- Fuente complementaria para `PLAN_ESTUDIOS`.
- Contraste para `CURSO_1ER_SEM`, `CURSO_2DO_SEM`, unidades cursadas y aprobadas.
- Fuente de llave para `CODCLI`, documento y carrera interna.
- Contraste de vigencia/carrera, no regla final.

Limitaciones:

- Contiene datos personales.
- No contiene una malla curricular oficial ni unidades por ano.
- No demuestra por si sola la unidad de medida exigida por Avance.
- La granularidad de `Hoja1` es asignatura/registro, no unidad curricular oficial validada.
- La interpretacion de aprobacion, convalidacion, homologacion o reconocimiento requiere regla institucional.

### archivo_listo_para_sies.xlsx

Estado: salida derivada de Matricula Unificada, usada por Extranjeros.

Uso posible:

- Contraste de `CODCLI`, documento, plan observado, codigo SIES final, ingreso y campos de trazabilidad.
- Evidencia historica de normalizacion y de `DA_MATCH_MODO`.

Limitaciones:

- Es salida derivada, no fuente primaria.
- Contiene datos personales.
- No debe transformar reglas MU32 en reglas Avance.

### matricula_unificada_2026_control.csv y pregrado

Estado: salidas MU encontradas y usadas como evidencia/contraste.

Uso posible:

- Contraste de identidad, carrera, ingreso y vigencia MU.
- Verificacion de estructura y cobertura de Matricula Unificada.

Limitaciones:

- Campos MU32 no son definiciones Avance.
- El archivo pregrado sin encabezado no debe publicarse ni citar registros.

### Puentes y catalogos SIES

Archivos:

- `resultados/puentes/PUENTE_MU_EXTRANJEROS_CODIGOS_SIES_2026.tsv`
- `control/catalogos/PUENTE_SIES_COMPILADO.tsv`
- `DURACION_ESTUDIOS.tsv`

Uso posible:

- Contraste de `CODIGO_UNICO`.
- Validacion de llaves compuestas.
- Apoyo para carreras, jornada, modalidad, duracion y vigencia de catalogo.

Limitaciones:

- Puente MU-Extranjeros contiene datos personales.
- Duracion no equivale a total de unidades de medida.
- `CODCARPR` solo no resuelve carrera/programa sin jornada, plan, sede o modalidad segun el caso.

### Resultado legacy Avance 2025

Archivo: `resultados/matricula_avance_curricular_2025_control.csv`.

Uso posible:

- Evidencia historica y contraste metodologico.

Limitaciones:

- No es fuente institucional primaria.
- No debe usarse como norma para Avance 2026.

## 3. Cobertura para Carreras

- `PLAN_ESTUDIOS`: cobertura parcial. Hay planes observados en `Hoja1` y salida MU, pero falta catalogo institucional validado.
- `TIPO_UNIDAD_MEDIDA`: no cubierta. Requiere malla o plan oficial.
- `OTRA_UNIDAD_MEDIDA`: no cubierta. Depende de la fuente oficial de unidad.
- `TOTAL_UNIDADES_MEDIDA`: no cubierta. `DURACION_ESTUDIOS` solo aporta duracion, no unidades.
- `UNIDADES_1ER_ANIO` a `UNIDADES_7MO_ANIO`: no cubiertas. `Hoja1` contiene registros de asignatura cursada, no distribucion oficial de malla por ano.
- `VIGENCIA`: cobertura parcial como contraste en `matriz` y `DURACION_ESTUDIOS`, pero la definicion Avance debe validarse.

Conclusion para Carreras: no hay fuente suficiente para cerrar el subproceso. Hay apoyo para codigo, plan y vigencia de catalogo, pero faltan malla y unidades.

## 4. Cobertura para Matricula

- `PLAN_ESTUDIOS`: cobertura parcial desde `Hoja1` y salida MU; requiere reconciliar con `CODIGO_UNICO` y precarga Avance.
- `CURSO_1ER_SEM`: cobertura parcial como contraste desde `Hoja1` por ano/periodo; falta definicion de actividad academica valida para Avance.
- `CURSO_2DO_SEM`: cobertura parcial como contraste desde `Hoja1` por ano/periodo; mismo bloqueo.
- `UNIDADES_CURSADAS`: cobertura parcial; hay asignaturas/registros, pero no unidad oficial validada.
- `UNIDADES_APROBADAS`: cobertura parcial; hay estado, nota y convalidacion, pero aprobacion requiere regla institucional.
- `UNID_CURSADAS_TOTAL`: cobertura parcial; acumulado depende de cobertura historica y unidad.
- `UNID_APROBADAS_TOTAL`: cobertura parcial; acumulado depende de aprobacion y tratamiento de convalidaciones.
- `VIGENCIA`: no apta como fuente directa. La vigencia usada por Extranjeros y `VIG` de MU no se pueden reutilizar automaticamente.

Conclusion para Matricula: hay fuentes candidatas para contraste academico, pero no estan listas para pipeline productivo.

## 5. Llaves

`CODCLI`:

- Fue la llave principal historica para cruces MU a Extranjeros.
- Existe en `DatosAlumnos`, `Hoja1`, salida MU y puente.
- No es unico en `Hoja1` por granularidad asignatura.
- En `DatosAlumnos` requiere revisar duplicados y persona-carrera.

Documento/RUT:

- Fue llave alternativa y de conciliacion.
- Requiere normalizacion y DV.
- Tiene riesgo many-to-many por multiples carreras y casos sin documento nacional.
- No debe publicarse ni documentarse con valores reales.

`CODIGO_UNICO`:

- Existe en `matriz`, salidas o puentes SIES y resultados legacy.
- Fue resuelto por cascada y con pendientes cuando habia ambiguedad.
- Puede apoyar carrera/programa, pero debe validarse contra precarga y fuente institucional 2025.

`PLAN_ESTUDIOS`:

- Existe como campo observado en historial y salida MU.
- No se comprobo como catalogo definitivo.
- Debe validarse antes de completar Avance.

## 6. Codigo y metodologia reutilizable

Reutilizable con adaptacion:

- Lectura de hojas y validacion de columnas.
- Normalizacion no destructiva de llaves.
- Auditoria de cobertura por llave.
- Trazabilidad por campo con fuente/archivo/hoja/columna/regla/estado.
- Control de duplicados por llave compuesta.
- Reportes de pendientes y estados de gobernanza.

No reutilizable directamente:

- Filtros de nacionalidad o residencia.
- Reglas de Extranjeros para vigencia.
- Decisiones institucionales puntuales.
- Generacion PES de Extranjeros.
- Deduplicaciones `first`/`last` como resolucion de ambiguedad.
- Reglas MU32 como definicion Avance.

## 7. Estado de B03

Clasificacion recomendada despues de esta busqueda: `B03_PARCIALMENTE_RESUELTO`.

Motivo:

- Se encontraron fuentes locales y evidencia de uso real en Extranjeros.
- Se identificaron llaves, scripts, auditorias y productos historicos.
- Hay cobertura parcial para plan, codigo, actividad academica observada y contraste de vigencia.
- Siguen faltando fuentes institucionales definitivas para malla, unidad de medida, unidades por ano y reglas Avance de vigencia/aprobacion/convalidacion.

Accion siguiente recomendada: validar llaves antes de congelar fuentes.
