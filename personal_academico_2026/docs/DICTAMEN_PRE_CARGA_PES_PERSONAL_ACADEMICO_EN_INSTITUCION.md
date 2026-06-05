# Dictamen Pre-Carga PES - Personal Academico en la Institucion

## Resumen Ejecutivo
El archivo preliminar fue cruzado contra la estructura oficial en institucion y contra la ultima auditoria del validador. La estructura de 34 columnas coincide en cantidad, nombres y orden. Sin embargo, existe al menos un error critico vigente, por lo que el archivo no esta listo para subir.

## Fuentes Revisadas
- Instructivo oficial: personal_academico_2026/insumos/Personal Académico SIES - Instructivo 2026.txt
- Estructura oficial En Institucion: personal_academico_2026/insumos/20260421_57181_20260420_Estructura_Personal_Académico_en_Institución_2026.csv
- Estructura oficial Fuera Institucion: personal_academico_2026/insumos/20260421_84406_20260420_Estructura_Personal_Académico_Fuera_Institución_2026.csv
- Base revisada: personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv
- Auditoria validador usada: personal_academico_2026/auditorias/auditoria_validacion_en_institucion_base_general_personal_academico_en_institucion_20260611_233537.csv

## Datos de Ejecucion
- Fecha/hora: 2026-06-11T23:35:37
- Rama: feature/personal-academico-base-preliminar-2026
- Total columnas oficiales: 34
- Total columnas base: 34
- Resultado cruce de nombres: COINCIDE
- Resultado cruce de orden: COINCIDE
- Resultado cantidad de columnas: COINCIDE
- Total filas: 190
- Estado general del archivo: NO_LISTO_REQUIERE_CORRECCION

## Tabla Columna Por Columna
| # | Columna oficial | Columna base | Estado | Errores | Advertencias | Accion requerida |
|---:|---|---|---|---:|---:|---|
| 1 | `TIPO_DOCUMENTO` | `TIPO_DOCUMENTO` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 2 | `NUM_DOCUMENTO` | `NUM_DOCUMENTO` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 3 | `DV` | `DV` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 4 | `PRIMER_APELLIDO` | `PRIMER_APELLIDO` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 5 | `SEGUNDO_APELLIDO` | `SEGUNDO_APELLIDO` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 6 | `NOMBRES` | `NOMBRES` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 7 | `SEXO` | `SEXO` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 8 | `FECHA_NACIMIENTO` | `FECHA_NACIMIENTO` | LISTA_CON_ADVERTENCIAS | 0 | 190 | Revisar advertencias antes de exportacion controlada. |
| 9 | `NACIONALIDAD` | `NACIONALIDAD` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 10 | `NIVEL_FORMACION_ACADEMICO` | `NIVEL_FORMACION_ACADEMICO` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 11 | `NOMBRE_TITULO_O_GRADO` | `NOMBRE_TITULO_O_GRADO` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 12 | `NOMBRE_INSTITUCION_OBT_TITULO` | `NOMBRE_INSTITUCION_OBT_TITULO` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 13 | `PAIS_OBTENCION_TIT_O_GRADO` | `PAIS_OBTENCION_TIT_O_GRADO` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 14 | `FECHA_OBT_TIT_O_GRADO` | `FECHA_OBT_TIT_O_GRADO` | REQUIERE_CORRECCION | 1 | 189 | Corregir errores criticos antes de exportar. |
| 15 | `NIVEL_FORMACION_ESPECIALIDAD` | `NIVEL_FORMACION_ESPECIALIDAD` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 16 | `TIPO_ESPECIALIDAD` | `TIPO_ESPECIALIDAD` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 17 | `NOMBRE_ESPECIALIDAD` | `NOMBRE_ESPECIALIDAD` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 18 | `NOMBRE_INST_OBT_ESPECIALIDAD` | `NOMBRE_INST_OBT_ESPECIALIDAD` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 19 | `PAIS_OBTENCION_ESPECIALIDAD` | `PAIS_OBTENCION_ESPECIALIDAD` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 20 | `FECHA_OBTENCION_ESPECIALIDAD` | `FECHA_OBTENCION_ESPECIALIDAD` | LISTA_CON_ADVERTENCIAS | 0 | 190 | Revisar advertencias antes de exportacion controlada. |
| 21 | `PRINCIPAL_CARGO_ACADEMICO` | `PRINCIPAL_CARGO_ACADEMICO` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 22 | `CARGO_NORMALIZADO` | `CARGO_NORMALIZADO` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 23 | `NIVEL_SUPERIOR_ADSCRIPCION` | `NIVEL_SUPERIOR_ADSCRIPCION` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 24 | `NIVEL_SECUNDARIO_ADSCRIPCION` | `NIVEL_SECUNDARIO_ADSCRIPCION` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 25 | `COMUNA_MAYOR_FUNCION` | `COMUNA_MAYOR_FUNCION` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 26 | `NOMBRE_PRINCIPAL_PROGRAMA` | `NOMBRE_PRINCIPAL_PROGRAMA` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 27 | `TOTAL_HORAS_PRINCIPAL_PROGRAMA` | `TOTAL_HORAS_PRINCIPAL_PROGRAMA` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 28 | `COMUNA_PRINCIPAL_PROGRAMA` | `COMUNA_PRINCIPAL_PROGRAMA` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 29 | `NUM_HORAS_PLANTA` | `NUM_HORAS_PLANTA` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 30 | `NUM_HORAS_CONTRATA` | `NUM_HORAS_CONTRATA` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 31 | `NUM_HORAS_HONORARIOS` | `NUM_HORAS_HONORARIOS` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 32 | `JERARQUIA_ACADEMICA` | `JERARQUIA_ACADEMICA` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 33 | `JERARQUIA_ACADEMICA_OCDE` | `JERARQUIA_ACADEMICA_OCDE` | LISTA | 0 | 0 | Sin hallazgos para la columna. |
| 34 | `VIGENCIA` | `VIGENCIA` | LISTA | 0 | 0 | Sin hallazgos para la columna. |

## Errores Que Impiden Carga
- Fila 20: `FECHA_OBT_TIT_O_GRADO` = `2027-11-29`; fecha_futura - Fecha futura respecto a 2026-06-11.

Caso vigente destacado:
- `FECHA_OBT_TIT_O_GRADO = 2027-11-29`, fila 20, `fecha_futura`.

## Advertencias Que Requieren Revision
- fecha_no_disponible: 197
- fecha_tolerancia_iso: 372

## Conclusion
NO LISTO PARA SUBIR.

No se genero PES_READY.

No se modifico la base.

No se corrigio ningun dato sin respaldo.

El cruce fue contra la estructura oficial y el instructivo del modulo.
