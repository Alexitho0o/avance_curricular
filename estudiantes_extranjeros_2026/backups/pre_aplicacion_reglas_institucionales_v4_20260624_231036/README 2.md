# Estudiantes Extranjeros SIES 2026

Subproducto para organizar y diagnosticar la entrega **Estudiantes Extranjeros SIES 2026**, correspondiente a estudiantes con nacionalidad extranjera matriculados o con actividad academica entre el **1 de enero y el 31 de diciembre de 2025**.

## Objetivo

Integrar el proceso al repositorio existente sin crear una linea paralela de trabajo, reutilizando la gobernanza de Matricula Unificada, fuentes de estudiantes, oferta academica, puente SIES y auditorias ya disponibles.

## Entregas normativas

- Extranjeros Regulares 2026, ID de carga 16765: estudiantes extranjeros regulares en programas conducentes o certificables de pregrado, postgrado o postitulo.
- Extranjeros de Intercambio 2026, ID de carga 16764: estudiantes extranjeros en programas o actividades formativas de corta duracion, presenciales en Chile, no orientadas a titulo o grado institucional.

## Alcance de esta ejecucion

Esta fase no genera CSV definitivo para PES. Solo crea diagnostico, inventario, diccionario oficial, matriz de mapeo, brechas, reglas y nominas de gestion.

## Base congelada oficial del proceso

Se incorporo como base cruda oficial congelada el archivo fuente `/Users/alexi/Desktop/BASE EXTRANJEROS.xlsx`, hoja `Hoja1`.

- Filas de datos: 62.
- Columnas: 63.
- Fecha de congelamiento: `2026-06-24T13:14:07-04:00`.
- Hash SHA-256 XLSX original y copia congelada: `89e6bb8071f7f7bf2cff4b4a4d120c92056fe82baba73e8e50c7d1ac50ae6e11`.
- Hash SHA-256 TSV congelado: `da85dd0c453a942a4490f469b75d0418e9054e458a46028f44271ac704518081`.
- Copia XLSX congelada: `data/frozen/BASE_EXTRANJEROS_2025_CONGELADA_ORIGINAL.xlsx`.
- Base TSV congelada: `data/frozen/BASE_EXTRANJEROS_2025_CONGELADA.tsv`.
- Manifiesto: `data/frozen/MANIFIESTO_BASE_EXTRANJEROS_2025_CONGELADA.json`.
- Auditorias: `resultados/auditorias/METADATA_BASE_EXTRANJEROS_CONGELADA.csv`, `resultados/auditorias/DICCIONARIO_BASE_EXTRANJEROS_CONGELADA.csv` y `resultados/auditorias/VALIDACION_BASE_CONGELADA_XLSX_VS_TSV.csv`.

Todos los analisis posteriores deben utilizar `BASE_EXTRANJEROS_2025_CONGELADA.tsv` como fuente base inmutable. El XLSX y el TSV congelados no deben modificarse directamente; cualquier nueva version debe generarse nuevamente mediante `scripts/congelar_base_extranjeros_2025.py` y quedar respaldada.

## Conciliación base congelada 62 vs universo auditado 257

El 2026-06-24 se ejecuto la conciliacion trazable entre la base congelada final de 62 registros y el universo auditado historico de 257 registros. La base congelada no fue modificada y mantuvo el hash SHA-256 `da85dd0c453a942a4490f469b75d0418e9054e458a46028f44271ac704518081`.

- Script reproducible: `scripts/conciliar_base_congelada_62_vs_257.py`.
- Metadata: `resultados/auditorias/METADATA_CONCILIACION_62_VS_257.csv`.
- Mapeo de columnas: `resultados/auditorias/MAPEO_COLUMNAS_BASE_CONGELADA_62.csv`.
- Base normalizada solo para cruce: `data/interim/BASE_EXTRANJEROS_2025_CONGELADA_NORMALIZADA.csv`.
- Conciliacion 62 vs 257: `resultados/auditorias/CONCILIACION_62_CONGELADOS_VS_257.csv`.
- Registros no incluidos: `resultados/auditorias/REGISTROS_257_NO_INCLUIDOS_EN_BASE_62.csv`.
- Conciliacion con precarga PES: `resultados/auditorias/CONCILIACION_62_VS_PRECARGA_PES.csv`.
- Conciliacion con matricula 2025: `resultados/auditorias/CONCILIACION_62_VS_MATRICULA_2025.csv`.
- Base enriquecida derivada con DatosAlumnos: `data/processed/BASE_EXTRANJEROS_2025_CONGELADA_ENRIQUECIDA.csv`.
- Auditoria de nacionalidad: `resultados/auditorias/AUDITORIA_NACIONALIDAD_BASE_CONGELADA_62.csv`.
- Excel trazable: `resultados/auditorias/CONCILIACION_TRAZABLE_BASE_62_VS_UNIVERSO_257.xlsx`.
- Validacion critica: `resultados/auditorias/VALIDACION_CONCILIACION_62_VS_257.csv`.

Resultados principales:

- Base congelada: 62 registros, 62 personas unicas y 62 registros persona-carrera institucionales.
- Universo auditado: 257 registros historicos; 62 vinculados a la base final y 195 no incluidos.
- Coincidencias exactas persona-carrera SIES: 0, porque la base congelada no contiene `CODIGO_UNICO` oficial directo.
- Coincidencias exactas por persona: 43.
- Multiples coincidencias trazables: 19.
- Sin coincidencia contra universo 257: 0.
- Presentes en precarga PES por persona/documento: 50.
- Ausentes en precarga PES: 12.
- Con evidencia de matricula local 2025: 58.
- Sin evidencia local 2025: 4.
- Con linea completa en DatosAlumnos: 62.
- Nacionalidades confirmadas mismo pais: 61.
- Nacionalidades ambiguas: 1.
- Conflictos de nacionalidad: 0.

Motivos de no inclusion en la base final de 62 registros:

- Duplicado tecnico: 12.
- Pendiente carrera: 22.
- Pendiente identidad: 15.
- Solo precarga sin confirmacion: 21.
- Agregado local pendiente: 1.
- No seleccionado en base final: 124.
- Motivo no determinado: 0.

Regla de uso: los 257 registros son antecedentes de auditoria, no el universo final. Todos los analisis posteriores deben usar `data/frozen/BASE_EXTRANJEROS_2025_CONGELADA.tsv` como fuente base inmutable y las salidas de conciliacion solo como trazabilidad y control. Esta fase no genera archivo final de carga PES.

## Cierre de pendientes base congelada 62

El 2026-06-24 se ejecuto el cierre analitico de los pendientes detectados en la conciliacion de la base congelada de 62 registros. La fuente normativa utilizada fue exclusivamente `docs/Instructivo_Estudiantes_Extranjeros_SIES_2026.txt`; no se modifico la base congelada ni se genero archivo final de carga PES.

- Hash TSV congelado validado: `da85dd0c453a942a4490f469b75d0418e9054e458a46028f44271ac704518081`.
- Script reproducible: `scripts/cerrar_pendientes_base_62.py`.
- Universo de pendientes: `resultados/auditorias/UNIVERSO_PENDIENTES_CIERRE_BASE_62.csv`.
- Nacionalidad ambigua: `resultados/auditorias/RESOLUCION_NACIONALIDAD_AMBIGUA_62.csv`.
- Evidencia 2025: `resultados/auditorias/RESOLUCION_4_SIN_EVIDENCIA_2025.csv`.
- Coincidencias multiples: `resultados/auditorias/RESOLUCION_19_COINCIDENCIAS_MULTIPLES.csv` y `resultados/auditorias/CANDIDATOS_19_COINCIDENCIAS_MULTIPLES.csv`.
- No seleccionados: `resultados/auditorias/RESOLUCION_124_NO_SELECCIONADOS.csv`.
- No incluidos finales: `resultados/auditorias/REGISTROS_195_NO_INCLUIDOS_RESUELTOS.csv`.
- Base derivada de cierre: `data/processed/BASE_EXTRANJEROS_2025_CONGELADA_ENRIQUECIDA_CIERRE.csv`.
- Excel trazable: `resultados/auditorias/CIERRE_TRAZABLE_PENDIENTES_BASE_62.xlsx`.
- Validacion: `resultados/auditorias/VALIDACION_CIERRE_PENDIENTES_BASE_62.csv`.
- Reporte: `resultados/reportes/REPORTE_CIERRE_PENDIENTES_BASE_62.md`.

Resultados de cierre:

- Nacionalidad ambigua inicial: 1; decision final: `REQUIERE_CONFIRMACION_INSTITUCIONAL`.
- Sin evidencia local 2025 inicial: 4; 1 caso confirmado por DatosAlumnos y 3 casos con evidencia parcial que requieren confirmacion.
- Coincidencias multiples iniciales: 19; 5 con seleccion unica de alta confianza y 14 pendientes por empate entre candidatos.
- No seleccionados iniciales: 124; todos quedaron desglosados sin reutilizar `NO_SELECCIONADO_EN_BASE_FINAL` como motivo final.
- No incluidos finales: 195; 14 exclusiones confirmadas y 181 pendientes de confirmacion institucional.
- Base 62: 44 registros completamente cerrados y 18 con revision pendiente.

Regla de uso: `BASE_EXTRANJEROS_2025_CONGELADA.tsv` sigue siendo la fuente base inmutable. Los archivos de cierre documentan decisiones, pendientes institucionales y trazabilidad; no reemplazan ni modifican la base congelada.

## Gobernanza columna por columna — Extranjeros Regulares 2025

El 2026-06-24 se genero la arquitectura de gobernanza columna por columna para preparar una futura carga SIES del proceso Estudiantes Extranjeros Regulares 2026, usando exclusivamente el instructivo `docs/Instructivo_Estudiantes_Extranjeros_SIES_2026.txt` como fuente normativa. No se modifico la base congelada y no se genero archivo final PES.

- Estructura oficial: `20260602_97636_Estructura_Extranjeros_Regulares_2025.csv`.
- Hash estructura oficial: `dfa2262abddd3bf2489cdcd6d2e5f4e95863325b8f0de3e407d9f6e0857528c2`.
- Delimitador: `;`; codificacion: `utf-8`; archivo con encabezados sin registros.
- Columnas oficiales detectadas: 20. La plantilla no contiene `CODIGO_IES_NUM`, por lo que no se incorpora como columna oficial gobernada.
- Esquema normativo: `config/ESQUEMA_OFICIAL_EXTRANJEROS_REGULARES_2025.tsv`.
- Diccionario maestro: `config/DICCIONARIO_GOBERNANZA_EXTRANJEROS_2025.tsv`.
- TSV gobernados: `data/governed/columnas_extranjeros_2025/`.
- Catalogos controlados: `data/governed/catalogos/TIPO_DOCUMENTO.tsv`, `data/governed/catalogos/TIPO_RESIDENCIA_ESTUDIANTE.tsv` y `data/governed/catalogos/NACIONALIDAD_SIES.tsv`.
- Matriz maestra: `data/processed/MATRIZ_GOBERNANZA_EXTRANJEROS_2025.csv`.
- Excel trazable: `resultados/auditorias/GOBERNANZA_COLUMNAS_EXTRANJEROS_2025.xlsx`.
- Cobertura por columna: `resultados/auditorias/COBERTURA_GOBERNANZA_COLUMNAS_EXTRANJEROS_2025.csv`.
- Cobertura por registro: `resultados/auditorias/COBERTURA_GOBERNANZA_REGISTROS_62.csv`.
- Validacion: `resultados/auditorias/VALIDACION_GOBERNANZA_COLUMNAS_EXTRANJEROS_2025.csv`.
- Reporte: `resultados/reportes/REPORTE_GOBERNANZA_COLUMNAS_EXTRANJEROS_2025.md`.
- Script reproducible: `scripts/gobernar_columnas_extranjeros_2025.py`.

Estado de aptitud:

- Registros aptos: 0.
- Registros aptos con advertencias: 0.
- Registros no aptos por conflictos: 3.
- Registros pendientes institucionales: 59.
- Registros con carga futura permitida desde esta matriz: 0.

Brechas principales visibles:

- `TIPO_RESIDENCIA_ESTUDIANTE`: 62 pendientes.
- `PAIS_ORIGEN`: 62 pendientes.
- `CODIGO_UNICO`: 26 pendientes, incluidos los empates de coincidencia multiple que no se seleccionan automaticamente.
- `SEXO`: 12 pendientes por no existir equivalencia normativa suficiente desde la codificacion local.
- `PAIS_ESTUDIOS_SECUNDARIOS`: 12 pendientes.
- `VIGENCIA`: 3 pendientes por evidencia 2025 parcial.
- `NACIONALIDAD`: 1 pendiente institucional.

Regla de uso: la matriz y los TSV gobernados son insumos de preparacion y auditoria, no una carga PES. Cualquier futura carga debe nacer de una fase posterior que resuelva o documente formalmente los pendientes institucionales y vuelva a validar la base congelada inmutable.

## Fuentes candidatas detectadas

- `input/PROMEDIOSDEALUMNOS_7804.xlsx`, hoja `DatosAlumnos`: CODCLI, RUT, nombres, sexo, fecha de nacimiento, nacionalidad, carrera, sede, jornada, anio/periodo de matricula e ingreso.
- `resultados/archivo_listo_para_sies.xlsx`, hoja `ARCHIVO_LISTO_SUBIDA`: campos MU normalizados, CODCLI, trazas y codigo SIES final para parte del universo.
- `gobernanza_columnas_mu/`: definiciones y reglas ya documentadas para TIPO_DOC, N_DOC, DV, nombres, sexo, FECH_NAC, NAC, PAIS_EST_SEC, ingreso y VIG.
- `gobernanza_nac.tsv` y `gobernanza_pais_est_sec.tsv`: catalogos de normalizacion existentes.
- `control/catalogos/PUENTE_SIES_COMPILADO.tsv`: puente de CODCARPR/oferta a codigo unico SIES.
- `indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS.*`: oferta/diccionario reutilizable como contraste de programas.

## Claves de cruce propuestas

1. Documento oficial normalizado: tipo documento, NUM_DOCUMENTO y DV.
2. CODCLI mediante equivalencia maestra, sin reemplazar NUM_DOCUMENTO.
3. CODCARPR + jornada + modalidad + version para CODIGO_UNICO.
4. Nombres + fecha de nacimiento solo para diagnostico y nunca para completar automaticamente.

## Campos criticos

No se deben inferir `NACIONALIDAD`, `TIPO_RESIDENCIA_ESTUDIANTE`, `PAIS_DE_ORIGEN` ni `PAIS_ESTUDIOS_SECUNDARIOS`. En esta ejecucion se detectaron 29 extranjeros confirmados por nacionalidad mapeable y 1 caso con nacionalidad no mapeada/por definir.

## Flujo propuesto

1. Validar universo 2025 regular con Docencia/Registro Academico.
2. Obtener fuente institucional de intercambio 2025 si existe.
3. Resolver campos criticos de residencia, origen y estudios secundarios.
4. Confirmar CODIGO_UNICO con puente SIES/oferta y resolver ambiguedades.
5. Ejecutar transformaciones en script separado, con auditoria y sin sobrescribir entregas previas.

## Riesgos

- Ausencia de fuente de intercambio.
- `TIPO_RESIDENCIA_ESTUDIANTE` no existe en fuentes revisadas.
- `PAIS_DE_ORIGEN` es condicional y no debe inferirse.
- `PAIS_ESTUDIOS_SECUNDARIOS` requiere evidencia de secundaria completada, no solo localidad o nacionalidad.
- Hay ambiguedades de codigo unico en puente SIES para algunos programas.
- Una nacionalidad aparece como `Por definir`.

## Actualizacion 2026-06-18 - Precarga PES oficial

Se incorporo formalmente el archivo `Reporte Precarga del Proceso Extranjeros Regulares 2026.csv` como fuente principal del universo inicial del proceso regular SIES 2026. El original se mantuvo intacto y se copio a `data/raw/REPORTE_PRECARGA_EXTRANJEROS_REGULARES_2026_ORIGINAL.csv`.

- Hash SHA-256 del original y de la copia raw: `6d0fe6a9a9357ec6e0efc7e5866c512de5ba708f80a2100c39ee9a283da2bff3`.
- Registros de precarga: 185.
- Personas unicas de precarga: 185.
- Columnas detectadas: 21.
- Delimitador detectado: `;`.
- Codificacion de trabajo: `cp1252` compatible con lectura latina del archivo.
- Diagnostico actualizado: `PRECARGA_OFICIAL_ENCONTRADA`.

La conciliacion compara la precarga con el universo local corregido de matricula efectiva 2025, que contiene 104 registros. El universo conciliado preliminar queda en 257 claves de carga: 185 provenientes de precarga y 72 agregadas desde evidencia local 2025. No se genera archivo CSV definitivo para PES en esta fase.

Resultado principal:

- Coincidencias exactas entre precarga y base local: 32.
- Coincidencias por persona con diferencias de carrera, codigo unico o identidad: 41.
- Registros solo en precarga: 134.
- Registros solo en matricula local 2025: 50.
- Agregados institucionales propuestos: 72.
- Eliminaciones propuestas con vigencia 0: 0.
- Registros que requieren gestion manual: 257.
- Conflictos entre precarga y fuente local: 12.

Pendientes criticos antes de generar la carga final:

- Confirmar evidencia 2025 de los 134 registros que aparecen solo en precarga.
- Resolver tipo de residencia para todos los registros conciliados.
- Completar o confirmar pais de origen cuando corresponda por tipo de residencia.
- Completar pais de estudios secundarios para 72 registros agregados desde fuente local.
- Resolver 32 registros con codigo unico pendiente.
- Revisar 12 conflictos entre datos de precarga y datos locales.

Siguiente paso recomendado: trabajar la planilla `resultados/archivos_gestion/PLANILLA_GESTION_DOCENCIA_EXTRANJEROS_2025_CONCILIADA.xlsx` con Docencia/Registro Academico, confirmar pertenencia al proceso y cerrar brechas criticas antes de producir cualquier archivo final de carga PES.
