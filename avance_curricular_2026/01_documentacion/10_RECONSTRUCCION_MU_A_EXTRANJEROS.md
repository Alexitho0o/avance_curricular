# Reconstruccion del flujo Matricula Unificada a Estudiantes Extranjeros

Proceso actual: Avance Curricular SIES 2026.

Alcance de esta reconstruccion: busqueda local, inventario, trazabilidad y evaluacion de reutilizacion. No se ejecutaron cruces productivos, no se completaron precargas, no se generaron archivos PES y no se copiaron datos personales a documentacion.

## 1. Que se hizo historicamente

La evidencia local muestra que Estudiantes Extranjeros 2026 reutilizo fuentes y salidas de Matricula Unificada como insumos de identificacion, conciliacion y enriquecimiento. El flujo no fue una aplicacion directa de reglas de Matricula Unificada a Extranjeros, sino una secuencia documentada de lectura, normalizacion, cruces por llaves, resolucion de codigos SIES y matrices de gobernanza por campo.

Los principales hitos reconstruidos estan en:

- `avance_curricular_2026/07_control/RECONSTRUCCION_FLUJO_MU_A_EXTRANJEROS.tsv`
- `avance_curricular_2026/07_control/TRAZABILIDAD_CAMPOS_MU_EXTRANJEROS.tsv`
- `avance_curricular_2026/07_control/INVENTARIO_LLAVES_MU_EXTRANJEROS.tsv`
- `avance_curricular_2026/07_control/INVENTARIO_CODIGO_REUTILIZABLE_MU.tsv`

## 2. Archivos participantes

Fuentes o derivados de Matricula Unificada utilizados como evidencia historica:

- `input/PROMEDIOSDEALUMNOS_7804.xlsx`, hojas `DatosAlumnos`, `Hoja1`, `matriz` y `base_datos`.
- `resultados/archivo_listo_para_sies.xlsx`, especialmente la hoja `ARCHIVO_LISTO_SUBIDA`.
- `resultados/matricula_unificada_2026_control.csv`.
- `resultados/matricula_unificada_2026_pregrado.csv`, como salida regulatoria sin encabezado visible en esta documentacion.
- `resultados/puentes/PUENTE_MU_EXTRANJEROS_CODIGOS_SIES_2026.tsv`.
- `control/catalogos/PUENTE_SIES_COMPILADO.tsv`.
- `DURACION_ESTUDIOS.tsv`.
- `resultados/matricula_avance_curricular_2025_control.csv`, usado como resultado legacy para conciliacion historica, no como norma para Avance 2026.

Artefactos de Estudiantes Extranjeros que documentan o reciben el enriquecimiento:

- `estudiantes_extranjeros_2026/data/interim/BASE_MAESTRA_EXTRANJEROS_REGULARES_2025.csv`.
- `estudiantes_extranjeros_2026/data/interim/BASE_MAESTRA_EXTRANJEROS_REGULARES_2025_CONCILIADA_PRECARGA.csv`.
- `MATRIZ_GOBERNANZA_EXTRANJEROS_2025_V7.csv` y `MATRIZ_GOBERNANZA_EXTRANJEROS_2025_V8 2.csv`.
- `PLANILLA_GESTION_DOCENCIA_EXTRANJEROS_2025.xlsx`.
- Reportes de fase, conciliacion, gobernanza, resolucion de codigos y cierre ICRE068 ubicados en `estudiantes_extranjeros_2026/resultados/reportes/` y `resultados/reportes/`.

## 3. Flujo reconstruido

1. Se leyeron las hojas de `PROMEDIOSDEALUMNOS_7804.xlsx`.
   - `DatosAlumnos` entrego datos persona-carrera, matricula 2025, nacionalidad, ingreso, estado academico y situacion.
   - `Hoja1` entrego historial persona-asignatura con periodo, estado, nota, convalidacion y plan.
   - `matriz` entrego catalogo de carrera/programa con `CODIGO_UNICO`, duraciones y vigencia.
   - `base_datos` entrego una equivalencia parcial entre documento y `CODCLI`.

2. Se construyo una base maestra inicial de Extranjeros.
   - Script principal: `estudiantes_extranjeros_2026/scripts/generar_base_maestra_fase2 2.py`.
   - Evidencia: funciones `read_inputs`, `classify_candidates`, `set_field`, `build_base` y `build_cross_audit`.
   - Resultado documentado: base maestra inicial y auditoria de cruces.

3. Se reutilizo la salida normalizada de Matricula Unificada.
   - Archivo: `resultados/archivo_listo_para_sies.xlsx`.
   - Hoja: `ARCHIVO_LISTO_SUBIDA`.
   - Uso: contraste y enriquecimiento de codigo SIES, ingreso, pais de estudios secundarios cuando existia y campos de trazabilidad.
   - Script: `generar_base_maestra_fase2 2.py`, funcion `read_archivo_listo`.

4. Se resolvio `CODIGO_UNICO`.
   - Primero por `CODCLI` cuando existia codigo final explicito en la salida de Matricula Unificada.
   - Luego por puente `CODCARPR` + jornada y catalogos SIES.
   - Los casos ambiguos quedaron pendientes; no se eligio una primera coincidencia como regla.
   - Scripts: `generar_base_maestra_fase2 2.py`, `resolver_codigos_sies_v6 2.py`, `scripts/cerrar_icre068_extranjeros_v8 2.py`.

5. Se corrigio y concilio el universo.
   - Se comparo precarga oficial, base local y evidencia de matricula/avance 2025.
   - Se generaron auditorias de conciliacion y matrices de gobernanza.
   - En fases intermedias se documento explicitamente que no correspondia generar PES.

6. Se produjo una gobernanza por columna.
   - Cada campo fue registrado con valor bruto, normalizado, fuente, archivo, hoja, columna, regla, estado y observacion.
   - Esta metodologia es reutilizable para Avance Curricular, pero las reglas funcionales de Extranjeros no lo son.

## 4. Informacion copiada o enriquecida

La estructura historica evidencia traslado o enriquecimiento de:

- Llaves y campos de identidad: tipo/documento, DV, `CODCLI`, llave normalizada y equivalencias.
- Campos academicos de control: `CODCARPR`, jornada, modalidad, plan observado, ingreso, matricula 2025, estado academico y situacion.
- Campos de carrera/oferta: `CODIGO_UNICO`, duracion, vigencia de catalogo y codigo SIES final.
- Campos de trazabilidad: fuente, hoja, columna, metodo de cruce, estado, observacion, confianza y pendiente.

No se documentan valores personales reales en este archivo.

## 5. Llaves usadas

- `CODCLI`: llave principal operativa para cruzar `DatosAlumnos`, salidas MU, base maestra y puente. En `DatosAlumnos` la granularidad es persona-carrera y requiere control de duplicados. En `Hoja1` se repite por asignatura.
- `RUT`/documento: llave alternativa y de conciliacion. Requiere normalizacion, DV y control many-to-many, especialmente por personas con mas de una carrera.
- `CODIGO_UNICO`: llave de carrera/programa SIES, incorporada desde matriz, salida MU, puente SIES y decisiones de gobernanza.
- `CODCARPR`/codigo interno de carrera: usada como llave secundaria junto con jornada, plan, sede o modalidad. No basta sola para resolver ambiguedades.
- `PLAN_ESTUDIOS`: campo observado en historial y salidas, pero requiere validacion institucional antes de reutilizarse para Avance 2026.

## 6. Fallback y control de duplicados

El flujo historico uso `CODCLI` como llave preferente y `RUT` normalizado como fallback en algunos procesos. Tambien uso llaves compuestas como `CODCLI + CODCARPR + PLAN_DE_ESTUDIO + COD_SED + JOR + MODALIDAD` para validar el puente MU-Extranjeros.

La evidencia muestra controles relevantes:

- Tests de no duplicidad para el puente MU-Extranjeros.
- Reportes que dejan pendientes cuando hay multiples candidatos.
- Matrices de gobernanza que separan fuente, regla y estado.
- Auditorias que distinguen coincidencia exacta, match por `CODCLI`, match por documento y match por carrera/jornada.

Limitacion importante: algunos scripts historicos contienen `drop_duplicates(..., keep="first")` como tecnica de lookup. Para Avance Curricular eso no puede reutilizarse como resolucion de ambiguedad sin auditoria previa.

## 7. Conflictos y resolucion

Los conflictos documentados se agrupan en:

- Codigos SIES ambiguos o ausentes.
- Diferencias entre precarga, base local y evidencia Matricula/Avance 2025.
- Campos propios de Extranjeros con fuente insuficiente.
- Vigencia, residencia, pais origen y casos institucionales pendientes.

La resolucion valida fue dejar pendientes o documentar decisiones institucionales. No se encontro una regla general reutilizable para completar automaticamente campos de Avance Curricular.

## 8. Productos generados historicamente

Se identificaron como productos del flujo:

- Base maestra de Extranjeros.
- Base conciliada con precarga.
- Auditorias de cruce.
- Resolucion de `CODIGO_UNICO`.
- Matrices de gobernanza V1 a V8.
- Planilla de gestion docente.
- Puentes MU-Extranjeros.
- Reportes de fase, conciliacion, correccion y cierre.

Algunos productos historicos pudieron generar PES dentro del subproyecto Extranjeros. Esta ejecucion no genero ningun PES.

## 9. Pendientes historicos

Persisten como pendientes o advertencias para Avance:

- Confirmar institucionalmente fuentes finales de malla, unidades por ano y unidad de medida.
- Validar llave persona-carrera antes de congelar fuentes.
- Auditar duplicados por `CODCLI`, documento y `CODIGO_UNICO`.
- No reutilizar reglas de nacionalidad, residencia o vigencia de Extranjeros.
- No tratar resultados legacy de Avance 2025 como norma 2026.
- Separar fuente institucional, metodologia de cruce y regla funcional.

## 10. Reutilizacion posible para Avance Curricular

Puede reutilizarse:

- Fuente institucional candidata: `PROMEDIOSDEALUMNOS_7804.xlsx` como insumo parcial de historial, plan observado, matricula y estado.
- Llaves demostradas: `CODCLI`, documento normalizado, `CODCARPR` + jornada y llaves compuestas de puente.
- Codigo/metodologia: lectura controlada de hojas, normalizacion no destructiva, auditoria de llaves, trazabilidad por campo, manifest y validacion de duplicados.
- Catalogos/puentes: `PUENTE_SIES_COMPILADO.tsv`, `DURACION_ESTUDIOS.tsv` y puente MU-Extranjeros solo como contraste o evidencia historica.

No puede reutilizarse automaticamente:

- Reglas MU32.
- Interpretacion de `VIG` o `VIGENCIA` de otros procesos.
- Estados academicos como regla oficial de Avance.
- Reglas de Extranjeros por nacionalidad, residencia o casos individuales.
- Resultados legacy como fuente normativa.
- Unidades calculadas desde cantidad de filas/asignaturas sin validar unidad de medida.

Conclusion: el antecedente MU a Extranjeros existe y esta respaldado documentalmente. Para Avance Curricular 2026 resuelve parcialmente el conocimiento de fuentes, llaves y metodologia, pero no cierra B03.
