# Gobernanza integral inputs, columnas y transformaciones 5809

Proceso: **Avance Curricular SIES 2026**
Subproyecto: **Gobernanza integral de inputs, raw, columnas, llaves, diccionarios, transformaciones y trazabilidad para archivo 5809 Matrícula Avance Curricular**
Año proceso: **2026**
Año referencia datos: **2025**
Declaración carga: **NO_LISTO_PARA_CARGA**

## Dictamen global

| Proceso                     | Subproyecto                                                                      | Anio proceso | Anio referencia datos | Estado de carga     | Dictamen global                                                                  | Fuentes originales modificadas | Total fuentes inventariadas | Total hojas inventariadas | Total columnas inventariadas | Total columnas gobernadas | Total columnas no gobernadas | Total llaves gobernadas | Total diccionarios detectados | Total transformaciones permitidas | Total bloqueos | Proximo paso permitido                                                           |
| --------------------------- | -------------------------------------------------------------------------------- | ------------ | --------------------- | ------------------- | -------------------------------------------------------------------------------- | ------------------------------ | --------------------------- | ------------------------- | ---------------------------- | ------------------------- | ---------------------------- | ----------------------- | ----------------------------- | --------------------------------- | -------------- | -------------------------------------------------------------------------------- |
| Avance Curricular SIES 2026 | Gobernanza integral de inputs, raw, columnas, llaves, diccionarios, transform... | 2026         | 2025                  | NO_LISTO_PARA_CARGA | Gobernanza generada. No se autoriza carga ni recalculo definitivo hasta cerra... | NO                             | 7                           | 23                        | 524                          | 61                        | 463                          | 7                       | 12                            | 10                                | 6              | Revisar 16_BLOQUEOS_ACTUALES, validar E/I/NULL y cerrar acumulados 20-21; no ... |

## Hallazgos principales

- Se inventariaron las fuentes, hojas y columnas principales antes de usar columnas para cálculo.
- Se detectó y documentó el diccionario `ESTADO` / `DESCRIPCION_ESTADO` de PROMEDIOS.
- `N_CODCLI` queda bloqueado como CODCLI académico; `CODCLI_LISTA` queda documentado como columna correcta de mapeo.
- Las columnas anuales 16-19 se separan de las acumuladas 20-21.
- Paso 48 queda descartado como inferencia para estados; paso 50 reemplaza esa base técnica.
- El expediente no genera carga, no declara listo y no modifica fuentes originales.

## Incidentes metodológicos

| ID_INCIDENTE | Descripcion                                                                | Fecha      | Paso donde ocurrio                                  | Causa raiz                                                                       | Impacto                                                           | Correccion                                                                       | Prevencion                                            | Estado                  |
| ------------ | -------------------------------------------------------------------------- | ---------- | --------------------------------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------------- | ----------------------- |
| INC01        | Uso incorrecto de N_CODCLI como si fuera CODCLI academico.                 | 2026-07-08 | Flujo anterior de conciliacion/calculo.             | Confusion entre conteo de CODCLI y llave academica.                              | Riesgo de cruzar registros academicos inexistentes o equivocados. | Bloquear N_CODCLI y documentar CODCLI_LISTA como columna correcta.               | Checklist pre-calculo y prohibicion explicita.        | CORREGIDO_EN_GOBERNANZA |
| INC02        | Inferencia innecesaria de A/E/I/R pese a existir diccionario en PROMEDIOS. | 2026-07-08 | Paso 48 / inferencia previa de estados.             | No se inspecciono diccionario ESTADO/DESCRIPCION_ESTADO antes de interpretar ... | Clasificacion de aprobadas quedo metodologicamente debil.         | Usar diccionario observado: A APROBADO, E CONVALIDACION, I HOMOLOGADO, R REPR... | Detectar diccionarios antes de cualquier inferencia.  | CORREGIDO_COMO_LECCION  |
| INC03        | Riesgo de sumar todos los CODCLI del RUT sin filtrar por programa.         | 2026-07-08 | Cruce RUT-CODCLI.                                   | RUT puede tener multiples CODCLI/programas.                                      | Unidades de otra carrera pueden contaminar 16-21.                 | Gobernar llave RUT + CODIGO_UNICO + PLAN_ESTUDIOS y CODCLI_LISTA filtrado.       | Validacion de cardinalidad por programa.              | VIGENTE_COMO_RIESGO     |
| INC04        | Riesgo de confundir estado academico con avance academico.                 | 2026-07-08 | Lectura de campos ESTADO_ACADEMICO/ESTADOACADEMICO. | Campos de situacion academica no son equivalentes a resultados por ramo.         | Podria forzar unidades cero o vigencia sin regla.                 | Bloquear uso de estado academico para calcular unidades.                         | Separar catalogos de auditoria de formulas de avance. | VIGENTE_COMO_RIESGO     |
| INC05        | Riesgo de mezclar año proceso 2026 con datos academicos 2025.              | 2026-07-08 | Filtros temporales.                                 | Proceso SIES 2026 usa año referencia datos 2025.                                 | Conteos anuales incorrectos.                                      | Documentar ANO=2025 para 16-19 y cierre academico 2025 para 20-21.               | Checklist de año/periodo antes de calculo.            | VIGENTE_COMO_RIESGO     |

## Bloqueos actuales

| ID_BLOQUEO | Bloqueo                                               | Casos     | Fuente                                           | Requisito para resolver                                                         | Responsable sugerido               | Puede resolverse automaticamente | Riesgo                                       |
| ---------- | ----------------------------------------------------- | --------- | ------------------------------------------------ | ------------------------------------------------------------------------------- | ---------------------------------- | -------------------------------- | -------------------------------------------- |
| B01        | 423 pendientes 16-19 con diccionario estado PROMEDIOS | 423       | Paso 50 / hoja 00_DICTAMEN y 06_PENDIENTES_16_19 | Resolver diferencias y criterios E/I/NULL/programa antes de definitivo.         | Equipo funcional academico + datos | NO                               | Alto: no puede declararse listo.             |
| B02        | 223 diferencia solo aprobadas 19                      | 223       | Paso 50                                          | Cerrar tratamiento de aprobadas, convalidaciones, homologaciones y NULL/blanco. | Equipo funcional academico         | NO                               | Alto: afecta UNIDADES_APROBADAS.             |
| B03        | 71 diferencia 16-18 o múltiple                        | 71        | Paso 50                                          | Validar periodo, ramos, duplicados o mapeo programa.                            | Datos + funcional                  | NO                               | Medio/alto: afecta presencia y cursadas.     |
| B04        | 122 sin registros 2025 para CODCLI_LISTA              | 122       | Paso 50                                          | Revisar CODCLI_LISTA, programa 2025 y cobertura PROMEDIOS.                      | Datos institucionales              | NO                               | Alto: ausencia de evidencia anual.           |
| B05        | 7 bloqueo sin CODCLI_LISTA                            | 7         | MAPEO_IDENTIDAD_CODCLI / Paso 50                 | Completar o resolver identidad academica antes de calcular.                     | Datos institucionales              | NO                               | Alto: sin llave academica.                   |
| B06        | 20-21 acumulado pendiente/no cerrado                  | PENDIENTE | Gobernanza columnas 20-21                        | Definir fuente historica completa, regla acumulada y limite por plan.           | Equipo funcional academico + datos | NO                               | Alto: separacion anual/acumulado no cerrada. |

## Equivalencias de hojas Excel

Excel limita los nombres de hoja a 31 caracteres. Cuando un nombre solicitado excede ese límite, el contenido obligatorio se conserva en una hoja física abreviada y esta equivalencia queda en el manifest.

| Nombre solicitado                         | Nombre fisico Excel             |
| ----------------------------------------- | ------------------------------- |
| 00_DICTAMEN_GLOBAL                        | 00_DICTAMEN_GLOBAL              |
| 01_FUENTES_INVENTARIO                     | 01_FUENTES_INVENTARIO           |
| 02_HOJAS_INVENTARIO                       | 02_HOJAS_INVENTARIO             |
| 03_COLUMNAS_INVENTARIO                    | 03_COLUMNAS_INVENTARIO          |
| 04_DICCIONARIOS_DETECTADOS                | 04_DICCIONARIOS_DETECTADOS      |
| 05_DICCIONARIO_ESTADO_PROMEDIOS           | 05_DICCIONARIO_ESTADO_PROMEDIOS |
| 06_LLAVES_GOBERNADAS                      | 06_LLAVES_GOBERNADAS            |
| 07_MAPEO_5809_COLUMNAS_OFICIALES          | 07_MAPEO_5809_COLS_OFICIALES    |
| 08_GOBERNANZA_COLUMNAS_16_19              | 08_GOBERNANZA_COLUMNAS_16_19    |
| 09_GOBERNANZA_COLUMNAS_20_21              | 09_GOBERNANZA_COLUMNAS_20_21    |
| 10_FLUJO_RAW_A_PROCESADO                  | 10_FLUJO_RAW_A_PROCESADO        |
| 11_TRANSFORMACIONES_AUTORIZADAS           | 11_TRANSFORMACIONES_AUTORIZ     |
| 12_TRANSFORMACIONES_PROHIBIDAS            | 12_TRANSFORMACIONES_PROHIBIDAS  |
| 13_VALIDACIONES_OBLIGATORIAS_PRE_CALCULO  | 13_VALIDACIONES_PRE_CALCULO     |
| 14_VALIDACIONES_OBLIGATORIAS_POST_CALCULO | 14_VALIDACIONES_POST_CALCULO    |
| 15_INCIDENTES_METODOLOGICOS               | 15_INCIDENTES_METODOLOGICOS     |
| 16_BLOQUEOS_ACTUALES                      | 16_BLOQUEOS_ACTUALES            |
| 17_REGLAS_DE_REANUDACION                  | 17_REGLAS_DE_REANUDACION        |
| 18_RESUMEN_EJECUTIVO                      | 18_RESUMEN_EJECUTIVO            |
| 19_FUENTES                                | 19_FUENTES                      |
| 20_MANIFEST_LEGIBLE                       | 20_MANIFEST_LEGIBLE             |

## Qué sigue pendiente

- Revisar la hoja `16_BLOQUEOS_ACTUALES` antes de cualquier cálculo.
- Confirmar tratamiento funcional de convalidación (`E`), homologación (`I`) y `NULL/blanco` por campo.
- Cerrar regla y fuente de acumulados 20-21.
- Solo después de cerrar gobernanza, autorizar un cálculo controlado no definitivo; la carga final sigue prohibida.

## Archivos

- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/51_gobernanza_integral_inputs_columnas_transformaciones_5809/GOBERNANZA_INTEGRAL_5809_20260708_144544/GOBERNANZA_INTEGRAL_INPUTS_COLUMNAS_TRANSFORMACIONES_5809.xlsx`
- Informe: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/51_gobernanza_integral_inputs_columnas_transformaciones_5809/GOBERNANZA_INTEGRAL_5809_20260708_144544/INFORME_GOBERNANZA_INTEGRAL_INPUTS_COLUMNAS_TRANSFORMACIONES_5809.md`
- Manifest: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/51_gobernanza_integral_inputs_columnas_transformaciones_5809/GOBERNANZA_INTEGRAL_5809_20260708_144544/manifest_gobernanza_integral_5809.json`
- Script: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/51_gobernanza_integral_inputs_columnas_transformaciones_5809/GOBERNANZA_INTEGRAL_5809_20260708_144544/gobernanza_integral_5809.py`
- Carpeta escritorio: `/Users/alexi/Desktop/AVANCE_CURRICULAR_2026_GOBERNANZA_INTEGRAL_5809_20260708_144544`
