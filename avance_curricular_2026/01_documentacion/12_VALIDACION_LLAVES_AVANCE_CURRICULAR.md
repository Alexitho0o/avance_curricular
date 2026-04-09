# Validacion de llaves Avance Curricular 2026

Proceso: Avance Curricular SIES 2026.

Alcance: validacion tecnica local de llaves candidatas antes de congelar nuevas fuentes, completar precargas o ejecutar cruces productivos. No se generaron PES, no se modificaron fuentes originales y no se copiaron valores personales a artefactos versionables.

## 1. Fuentes analizadas

Se analizaron 13 fuentes locales:

- Precarga Matricula congelada: 2.371 filas.
- Precarga Carreras congelada: 43 filas.
- Derivados TSV congelados de `PROMEDIOSDEALUMNOS_7804.xlsx`: `Hoja1`, `DatosAlumnos`, `matriz`, `base_datos`.
- `resultados/archivo_listo_para_sies.xlsx`, hoja `ARCHIVO_LISTO_SUBIDA`.
- `resultados/matricula_unificada_2026_control.csv`.
- `resultados/puentes/PUENTE_MU_EXTRANJEROS_CODIGOS_SIES_2026.tsv`.
- `control/catalogos/PUENTE_SIES_COMPILADO.tsv`.
- `DURACION_ESTUDIOS.tsv`.
- Resultados legacy Avance 2025, solo como antecedente tecnico.

La definicion tecnica de llaves quedo en `avance_curricular_2026/04_configuracion/DEFINICION_LLAVES_AVANCE_CURRICULAR.tsv`.

## 2. Granularidades

Granularidades observadas:

- `PERSONA`: documento o equivalencia persona.
- `PERSONA_CARRERA`: una persona asociada a una carrera o programa.
- `PERSONA_CARRERA_PLAN`: persona, carrera y plan observado.
- `PERSONA_ASIGNATURA_PERIODO`: historial academico por asignatura y periodo.
- `CARRERA_PLAN`: carrera o programa SIES con plan.
- `CARRERA_JORNADA`: codigo interno con jornada.
- `CARRERA_SEDE_JORNADA_VERSION`: combinacion ampliada de programa.
- `CATALOGO` o `AGREGADO`: fuentes de puente o resumen.

Dato observado: `Hoja1` no puede evaluarse como persona unica porque su granularidad es persona-asignatura-periodo.

## 3. Resultado CODCLI

Dato observado:

- `CODCLI` existe en `Hoja1`, `DatosAlumnos`, `base_datos`, `archivo_listo_para_sies.xlsx` y puente MU-Extranjeros.
- En `Hoja1`: 41.106 filas, 5.174 `CODCLI` unicos y 35.932 repeticiones esperables por asignatura/periodo.
- En `DatosAlumnos`: 13.706 no nulos, 13.704 unicos y 2 repeticiones.
- En puente MU-Extranjeros: 4.117 no nulos y 4.117 unicos.

Validacion tecnica:

- No representa universalmente una persona en todas las fuentes.
- En `Hoja1` funciona como llave auxiliar de historial, no como llave principal.
- En `DatosAlumnos` requiere revisar duplicados antes de usarlo como persona-carrera.
- La precarga Matricula no trae `CODCLI`, por lo que no puede ser llave directa con esa precarga.

Decision interna:

- `CODCLI` queda como llave auxiliar y de auditoria.
- No queda validada como llave principal de Avance Curricular.

Pendiente:

- Resolver el puente entre precarga Matricula y `CODCLI` sin elegir filas arbitrarias.

## 4. Resultado documentos y RUT

Dato observado:

- La precarga Matricula tiene tipo de documento, numero y DV.
- `Hoja1` tiene `RUT` y digito.
- `DatosAlumnos` tiene `RUT`, pero no tipo/DV separados.
- Algunas fuentes derivadas tienen documento completo y otras solo cuerpo del documento.

Validacion tecnica:

- El cruce Precarga Matricula contra `DatosAlumnos` por numero normalizado cubre 99,75% de filas, pero presenta riesgo alto por multiplicidad y falta de DV/tipo en `DatosAlumnos`.
- El cruce Precarga Matricula contra `Hoja1` por documento cubre 94,77%, pero expande a 27.751 filas si se cruza sin carrera/plan.
- RUN y documentos no RUN se separaron solo de forma auxiliar; no se aplico algoritmo RUN a pasaportes.

Decision interna:

- Documento/RUT queda como fallback o contraste.
- No debe usarse solo para persona-carrera.

Pendiente:

- Validar documento completo con fuente que conserve tipo, numero, DV y carrera/programa.

## 5. Resultado CODIGO_UNICO

Dato observado:

- Precarga Carreras: 43 codigos completos.
- Precarga Matricula: 2.371 filas con 43 codigos unicos.
- `matriz`: 139 codigos unicos.
- `DURACION_ESTUDIOS.tsv`: 137 codigos unicos.
- `PUENTE_SIES_COMPILADO.tsv`: 61 codigos finales unicos observados.

Validacion tecnica:

- Precarga Carreras cruza 100,00% con `matriz` por `CODIGO_UNICO`, sin expansion.
- Precarga Carreras cruza 100,00% con `DURACION_ESTUDIOS`, pero con factor de expansion 1,2326 por duplicidad del catalogo.
- Los 43 codigos de Carreras estan en `matriz` y `DURACION_ESTUDIOS`; 27 aparecen en `PUENTE_SIES_COMPILADO`.

Decision interna:

- `CODIGO_UNICO` es llave principal parcial para catalogos de carrera.
- No basta para resolver unidades, plan o matricula individual.

Pendiente:

- Controlar duplicidad en catalogos antes de congelar o usar como fuente operativa.

## 6. Resultado CODCARPR y puente SIES

Dato observado:

- `CODCARPR` existe en `DatosAlumnos`, puente MU-Extranjeros y puente SIES.
- `CODCARR` existe en `Hoja1` como codigo interno observado.
- `CODCARPR` solo puede mapear a multiples codigos SIES.

Validacion tecnica:

- `CODCARPR` solo tiene riesgo alto: hasta 3 codigos SIES por llave en fuentes puente.
- `CODCARPR + JORNADA` mejora la precision en `archivo_listo`, puente MU-Extranjeros y `PUENTE_SIES_COMPILADO`.
- `CODCARPR + JORNADA + SEDE + MODALIDAD + VERSION` no debe elegirse automaticamente si los componentes faltan o son derivados.

Decision interna:

- Llave recomendada de puente: `CODCARPR + JORNADA` como auxiliar, con control de cobertura y fuente.
- `CODCARPR` solo no es apta.

Pendiente:

- Validar si sede, modalidad y version aportan precision real sin reducir cobertura.

## 7. Resultado PLAN_ESTUDIOS

Dato observado:

- Precargas 2026 tienen un unico valor de `PLAN_ESTUDIOS`.
- `Hoja1` observa 72 planes.
- `archivo_listo_para_sies.xlsx` observa 45 planes.
- Puente MU-Extranjeros observa 46 planes.

Validacion tecnica:

- El plan precargado parece correlativo o valor precargado, pero no se demostro como catalogo institucional.
- En fuentes MU hay multiples planes por codigo y multiples codigos por plan.
- No se valido que `PLAN_ESTUDIOS` equivalga a version, cohorte, tipo de plan o catalogo final.

Decision interna:

- `PLAN_ESTUDIOS` no queda apto para asignacion definitiva.
- Puede usarse solo como dato observado y contraste.

Pendiente:

- Obtener o validar catalogo institucional de planes.

## 8. Cardinalidades y cruces

Cruces de auditoria:

- A1 Precarga Matricula vs `DatosAlumnos`, documento normalizado: cobertura 99,75%, factor 1,3138, riesgo alto.
- B1 Precarga Matricula vs `Hoja1`, documento normalizado: cobertura 94,77%, factor 11,7043, riesgo alto.
- C1 Precarga Carreras vs `matriz`, `CODIGO_UNICO`: cobertura 100,00%, factor 1,0000, riesgo bajo.
- D1 Precarga Carreras vs `DURACION_ESTUDIOS`, `CODIGO_UNICO`: cobertura 100,00%, factor 1,2326, riesgo alto.
- E1 Precarga Matricula vs `archivo_listo`, documento + codigo: cobertura 65,08%, factor 8,3437, riesgo alto.
- F1 `DatosAlumnos` vs puente MU-Extranjeros, `CODCLI + CODCARPR`: cobertura 30,04%, sin expansion.
- F2 `Hoja1` vs puente MU-Extranjeros, `CODCLI + CODCARPR + PLAN`: cobertura 83,82%, sin expansion por calculo agregado, pero granularidad asignatura requiere resumen previo.

No se materializaron cruces productivos. Los calculos son cardinalidades agregadas de auditoria.

## 9. Casos many-to-many

Se detectaron 5 casos resumen en `CASOS_MANY_TO_MANY_RESUMEN.tsv`.

Causas principales:

- Llave insuficiente por documento solo.
- Fuente con granularidad distinta, especialmente `Hoja1`.
- Catalogo de duracion con mas de una fila por codigo.
- Multiples candidatos en salida derivada de MU.

Resolucion ejecutada: NO.

Accion requerida: resolver cardinalidad antes de cualquier congelamiento adicional o pipeline.

## 10. Cobertura Carreras

Dato observado:

- 43 de 43 codigos estan en `matriz`.
- 43 de 43 codigos estan en `DURACION_ESTUDIOS`.
- 27 de 43 codigos estan en `PUENTE_SIES_COMPILADO`.
- 13 codigos tienen multiples `CODCARPR` observados.
- 37 codigos tienen multiples planes observados.
- No hay cobertura de unidad de medida, total de unidades ni distribucion anual desde una fuente institucional validada.

Decision interna:

- Las llaves de catalogo estan parcialmente validadas.
- Las fuentes no cubren malla ni unidades.

## 11. Cobertura Matricula

Dato observado:

- 2.371 filas en precarga Matricula.
- 13 filas tienen match unico con `archivo_listo` por documento + codigo.
- 1.783 filas tienen match unico contra `DatosAlumnos` por documento normalizado, pero sin DV/tipo completo.
- 2.247 filas tienen historial observable en `Hoja1` por documento.
- 1.362 filas tienen convalidacion identificable en `Hoja1`.
- 124 filas quedan sin fuente suficiente en la auditoria combinada.

Decision interna:

- Hay buena cobertura de contraste, pero no una llave segura de persona-carrera-plan.
- No se puede completar Matricula productivamente.

## 12. Llaves aptas, parciales y no aptas

Aptas solo para auditoria:

- `CODIGO_UNICO` entre Precarga Carreras y `matriz`.

Parciales:

- `CODIGO_UNICO` contra `DURACION_ESTUDIOS`.
- `CODCARPR + JORNADA` como puente auxiliar.
- `CODCLI + CODCARPR` para contraste con puente MU-Extranjeros.
- Documento normalizado como fallback.

No aptas como llave principal:

- Documento solo.
- `CODCLI` solo.
- `CODCARPR` solo.
- `PLAN_ESTUDIOS` solo.
- `Hoja1` por documento sin carrera/plan.

## 13. Fuentes candidatas a congelar

Podrian evaluarse para congelamiento controlado posterior:

- `DURACION_ESTUDIOS.tsv`, como catalogo parcial de duracion y codigo.
- `PUENTE_SIES_COMPILADO.tsv`, como puente parcial.

Ya congelada:

- `PROMEDIOSDEALUMNOS_7804.xlsx`, con uso parcial y restricciones por datos personales.

No deben congelarse como fuente oficial:

- `archivo_listo_para_sies.xlsx`, por ser salida derivada con datos personales.
- Puente MU-Extranjeros, por ser derivado de otro proceso y contener datos personales.
- Resultados legacy y PES_READY historicos.
- Matrices de Extranjeros como fuente Avance.

## 14. Bloqueos

Bloqueos vigentes:

- Many-to-many abiertos.
- `PLAN_ESTUDIOS` sin significado institucional validado.
- Malla/unidades por ano no encontradas.
- Vigencia Avance no validada.
- Precarga Matricula sin `CODCLI`.
- `Hoja1` sin `CODIGO_UNICO`.

## 15. Siguiente accion

Decision interna de esta fase: `B03_LLAVES_PARCIALMENTE_VALIDADAS`.

Siguiente accion recomendada: resolver casos many-to-many antes de congelar fuentes nuevas.
