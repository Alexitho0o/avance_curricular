# Diccionario Tecnico Preliminar Personal Academico SIES 2026

Este diccionario usa exclusivamente las dos estructuras CSV oficiales y el instructivo 2026 conservados en `../insumos/`.

## A. Personal Academico En La Institucion

- Fuente de estructura: `20260421_57181_20260420_Estructura_Personal_Académico_en_Institución_2026.csv`.
- Cantidad de campos: 34.
- Delimitador observado en la estructura oficial: `;`.
- Fuente complementaria: Instructivo 2026, Anexo I, ID 16761.

| Orden | Campo oficial | Observacion preliminar |
|---:|---|---|
| 1 | `TIPO_DOCUMENTO` | Identificacion. Valores `R` o `P` segun instructivo. |
| 2 | `NUM_DOCUMENTO` | Identificacion. Numero de RUT o pasaporte; sin puntos, comas ni guiones segun instructivo. |
| 3 | `DV` | Identificacion. Condicional segun tipo de documento; nulo para pasaporte segun mensajes de error. |
| 4 | `PRIMER_APELLIDO` | Dato personal. Texto en mayusculas y sin acentos segun instructivo. |
| 5 | `SEGUNDO_APELLIDO` | Dato personal. Texto en mayusculas y sin acentos segun instructivo. |
| 6 | `NOMBRES` | Dato personal. Texto en mayusculas y sin acentos segun instructivo. |
| 7 | `SEXO` | Dato personal. Valores `M`, `H`, `NB`. |
| 8 | `FECHA_NACIMIENTO` | Dato personal. Formato `DD-MM-AAAA`. |
| 9 | `NACIONALIDAD` | Codigo de pais segun tabla de paises del instructivo. |
| 10 | `NIVEL_FORMACION_ACADEMICO` | Formacion. Codigos 1 a 8 segun instructivo. |
| 11 | `NOMBRE_TITULO_O_GRADO` | Formacion. Nombre del titulo o grado superior informado. |
| 12 | `NOMBRE_INSTITUCION_OBT_TITULO` | Formacion. Institucion donde obtuvo titulo o grado. |
| 13 | `PAIS_OBTENCION_TIT_O_GRADO` | Formacion. Codigo de pais segun tabla de paises. |
| 14 | `FECHA_OBT_TIT_O_GRADO` | Formacion. Formato `DD-MM-AAAA`; no posterior al 31-05-2026 segun instructivo. |
| 15 | `NIVEL_FORMACION_ESPECIALIDAD` | Especialidad. Aplica cuando corresponde; codigos 1 a 2 segun instructivo. |
| 16 | `TIPO_ESPECIALIDAD` | Especialidad. Pendiente por tension entre anexos y mensajes de error. |
| 17 | `NOMBRE_ESPECIALIDAD` | Especialidad. Texto en mayusculas y sin acentos cuando aplique. |
| 18 | `NOMBRE_INST_OBT_ESPECIALIDAD` | Especialidad. Institucion donde obtuvo especialidad. |
| 19 | `PAIS_OBTENCION_ESPECIALIDAD` | Especialidad. Codigo de pais segun tabla de paises. |
| 20 | `FECHA_OBTENCION_ESPECIALIDAD` | Especialidad. Formato `DD-MM-AAAA`; no posterior al 31-05-2026 segun instructivo. |
| 21 | `PRINCIPAL_CARGO_ACADEMICO` | Cargo. Nombre principal del empleo o funcion dentro de la institucion. |
| 22 | `CARGO_NORMALIZADO` | Cargo. Codigos 1 a 11 segun instructivo. |
| 23 | `NIVEL_SUPERIOR_ADSCRIPCION` | Adscripcion. Unidad superior institucional. |
| 24 | `NIVEL_SECUNDARIO_ADSCRIPCION` | Adscripcion. Unidad de dependencia mas directa. |
| 25 | `COMUNA_MAYOR_FUNCION` | Territorio. Comuna donde realiza mayor parte de funcion academica. |
| 26 | `NOMBRE_PRINCIPAL_PROGRAMA` | Programa principal. Carrera o programa asociado a mayor dedicacion o actividad principal. |
| 27 | `TOTAL_HORAS_PRINCIPAL_PROGRAMA` | Horas del programa principal. Maximo 56 horas; decimales con coma y dos decimales. |
| 28 | `COMUNA_PRINCIPAL_PROGRAMA` | Comuna donde se ubica el programa principal. |
| 29 | `NUM_HORAS_PLANTA` | Horas cronologicas semanales por planta o contrato indefinido. |
| 30 | `NUM_HORAS_CONTRATA` | Horas cronologicas semanales por contrata o plazo fijo. |
| 31 | `NUM_HORAS_HONORARIOS` | Horas cronologicas semanales por honorarios. |
| 32 | `JERARQUIA_ACADEMICA` | Jerarquia institucional definida por la institucion; `No aplica` si no existe carrera academica. |
| 33 | `JERARQUIA_ACADEMICA_OCDE` | Clasificacion OCDE. Codigos 1 a 5 segun instructivo. |
| 34 | `VIGENCIA` | Vigencia. `0` eliminar registro, `1` mantener registro. |

Advertencias de estructura:

- El archivo oficial de estructura contiene encabezado, pero el instructivo indica eliminar encabezados antes de subir a PES.
- El delimitador observado en la estructura es `;`; el instructivo menciona CSV delimitado por comas. Queda pendiente de confirmacion para exportacion final.
- No deben agregarse columnas auxiliares.
- No debe exportarse indice.
- El orden de columnas debe conservarse exactamente.

## B. Personal Academico Fuera De La Institucion

- Fuente de estructura: `20260421_84406_20260420_Estructura_Personal_Académico_Fuera_Institución_2026.csv`.
- Cantidad de campos: 27.
- Delimitador observado en la estructura oficial: `;`.
- Fuente complementaria: Instructivo 2026, Anexo II, ID 16760.

| Orden | Campo oficial | Observacion preliminar |
|---:|---|---|
| 1 | `TIPO_DOCUMENTO` | Identificacion. Valores `R` o `P` segun instructivo. |
| 2 | `NUM_DOCUMENTO` | Identificacion. Numero de RUT o pasaporte; sin puntos, comas ni guiones segun instructivo. |
| 3 | `DV` | Identificacion. Condicional segun tipo de documento; nulo para pasaporte segun mensajes de error. |
| 4 | `PRIMER_APELLIDO` | Dato personal. Texto en mayusculas y sin acentos segun instructivo. |
| 5 | `SEGUNDO_APELLIDO` | Dato personal. Texto en mayusculas y sin acentos segun instructivo. |
| 6 | `NOMBRES` | Dato personal. Texto en mayusculas y sin acentos segun instructivo. |
| 7 | `SEXO` | Dato personal. Valores `M`, `H`, `NB`. |
| 8 | `FECHA_NACIMIENTO` | Dato personal. Formato `DD-MM-AAAA`. |
| 9 | `NACIONALIDAD` | Codigo de pais segun tabla de paises del instructivo. |
| 10 | `NIVEL_FORMACION_ACADEMICO` | Formacion. Codigos 1 a 8 segun instructivo. |
| 11 | `NOMBRE_TITULO_O_GRADO` | Formacion. Nombre del titulo o grado superior informado. |
| 12 | `NOMBRE_INSTITUCION_OBT_TITULO` | Formacion. Institucion donde obtuvo titulo o grado. |
| 13 | `PAIS_OBTENCION_TIT_O_GRADO` | Formacion. Codigo de pais segun tabla de paises. |
| 14 | `FECHA_OBT_TIT_O_GRADO` | Formacion. Formato `DD-MM-AAAA`; no posterior al 31-05-2026 segun instructivo. |
| 15 | `NIVEL_FORMACION_ESPECIALIDAD` | Especialidad. Aplica cuando corresponde; codigos 1 a 2 segun instructivo. |
| 16 | `TIPO_ESPECIALIDAD` | Especialidad. Pendiente por tension entre anexos y mensajes de error. |
| 17 | `NOMBRE_ESPECIALIDAD` | Especialidad. Texto en mayusculas y sin acentos cuando aplique. |
| 18 | `NOMBRE_INST_OBT_ESPECIALIDAD` | Especialidad. Institucion donde obtuvo especialidad. |
| 19 | `PAIS_OBTENCION_ESPECIALIDAD` | Especialidad. Codigo de pais segun tabla de paises. |
| 20 | `FECHA_OBTENCION_ESPECIALIDAD` | Especialidad. Formato `DD-MM-AAAA`; no posterior al 31-05-2026 segun instructivo. |
| 21 | `TOTAL_HORAS_CONTRATADAS` | Horas contratadas antes de comision fuera de la institucion. Maximo 56 horas. |
| 22 | `MOTIVO_COMISION_FUERA_IES` | Motivo de comision. Codigos indicados por instructivo. |
| 23 | `NOMBRE_PROGRAMA_DE_ESTUDIOS` | Campo de comision de estudios; aplica solo a academicos en comision de estudios segun instructivo. |
| 24 | `INSTITUCION_PROGRAMA_ESTUDIOS` | Institucion donde realiza estudios, cuando aplique. |
| 25 | `PAIS_PROGRAMA_ESTUDIOS` | Pais donde realiza estudios, cuando aplique. |
| 26 | `FECHA_INICIO_PROGRAMA_ESTUDIOS` | Fecha de inicio de estudios, cuando aplique. |
| 27 | `VIGENCIA` | Vigencia. `0` eliminar registro, `1` mantener registro. |

Advertencias de estructura:

- El archivo oficial de estructura contiene encabezado, pero el instructivo indica eliminar encabezados antes de subir a PES.
- El delimitador observado en la estructura es `;`; el instructivo menciona CSV delimitado por comas. Queda pendiente de confirmacion para exportacion final.
- Los campos 23 a 26 son especificos para comision de estudios; la implementacion futura debe confirmar el disparador exacto antes de aplicar regla estricta.
- No deben agregarse columnas auxiliares.
- No debe exportarse indice.
- El orden de columnas debe conservarse exactamente.

## Validaciones Minimas Esperadas Antes De Exportar

Leyenda:

- `Normativa explicita`: respaldada directamente por estructura oficial o instructivo.
- `Validacion tecnica preventiva`: control recomendado para evitar errores, sin tratarlo como regla normativa si la fuente no lo explicita.
- `Pendiente de confirmacion`: punto con tension o falta de explicitacion.

### Validaciones Estructurales

| Validacion | Clasificacion |
|---|---|
| Cantidad exacta de columnas: 34 para en institucion y 27 para fuera de institucion. | Normativa explicita por estructuras CSV. |
| Orden exacto de columnas segun estructuras oficiales. | Normativa explicita por estructuras CSV. |
| Nombres oficiales de columnas sin variantes. | Normativa explicita por estructuras CSV. |
| Ausencia de columnas adicionales. | Validacion tecnica preventiva derivada de estructura exacta. |
| Ausencia de indice exportado. | Validacion tecnica preventiva. |
| Control de encabezado: estructura con encabezado versus archivo de carga sin encabezado. | Normativa explicita para carga PES, pendiente de implementacion operacional. |
| Delimitador CSV segun estructura oficial y decision confirmada. | Pendiente de confirmacion por tension `;` versus "delimitado por comas". |

### Validaciones De Identificacion

| Validacion | Clasificacion |
|---|---|
| `TIPO_DOCUMENTO` en `R` o `P`. | Normativa explicita. |
| `NUM_DOCUMENTO` sin puntos, comas ni guiones. | Normativa explicita. |
| `NUM_DOCUMENTO` numerico cuando `TIPO_DOCUMENTO` es `R`. | Normativa explicita. |
| `NUM_DOCUMENTO` no comienza con `0`. | Normativa explicita por mensajes de error. |
| `DV` nulo cuando `TIPO_DOCUMENTO` es `P`. | Normativa explicita por mensajes de error. |
| `DV` de `0` a `9` o `K` cuando `TIPO_DOCUMENTO` es `R`. | Normativa explicita. |
| Validacion de coherencia RUT-DV. | Normativa explicita por mensajes de error. |
| Duplicados por combinacion `TIPO_DOCUMENTO` + `NUM_DOCUMENTO`. | Normativa explicita por unicidad y carga acumulativa. |
| Una sola aparicion del academico cuando corresponda. | Normativa explicita. |

### Validaciones Personales

| Validacion | Clasificacion |
|---|---|
| `PRIMER_APELLIDO`, `SEGUNDO_APELLIDO` y `NOMBRES` en mayusculas segun instructivo. | Normativa explicita. |
| Sin espacios iniciales, finales ni dobles espacios en nombres/apellidos. | Normativa explicita por mensajes de error. |
| `SEXO` en `M`, `H`, `NB`. | Normativa explicita. |
| `FECHA_NACIMIENTO` con formato `DD-MM-AAAA`. | Normativa explicita. |
| `FECHA_NACIMIENTO` entre 01-01-1900 y 31-05-2008. | Normativa explicita por mensajes de error. |
| `NACIONALIDAD` entre 1 y 197 segun tabla de paises. | Normativa explicita. |
| Paises de obtencion/programa entre 1 y 197 cuando correspondan. | Normativa explicita. |

### Validaciones Academicas Y Laborales

| Validacion | Clasificacion |
|---|---|
| `NIVEL_FORMACION_ACADEMICO` en codigos 1 a 8. | Normativa explicita. |
| `NOMBRE_TITULO_O_GRADO` informado y en formato textual permitido. | Normativa explicita. |
| `FECHA_OBT_TIT_O_GRADO` con formato `DD-MM-AAAA` y no posterior al 31-05-2026. | Normativa explicita. |
| `NOMBRE_INSTITUCION_OBT_TITULO` no vacio. | Normativa explicita por mensajes de error. |
| `NIVEL_FORMACION_ESPECIALIDAD` en codigos 1 a 2 cuando aplique. | Normativa explicita. |
| Coherencia de especialidad: si se informa nombre, institucion, pais o fecha, completar nivel de especialidad. | Normativa explicita por mensajes de error. |
| `TIPO_ESPECIALIDAD` validado solo despues de resolver inconsistencia 1-5 versus 1-4. | Pendiente de confirmacion. |
| `CARGO_NORMALIZADO` en codigos 1 a 11 para en institucion. | Normativa explicita. |
| `PRINCIPAL_CARGO_ACADEMICO` no blanco para en institucion. | Normativa explicita. |
| Horas individuales numericas y no superiores a 56. | Normativa explicita. |
| Suma `NUM_HORAS_PLANTA` + `NUM_HORAS_CONTRATA` + `NUM_HORAS_HONORARIOS` no superior a 56 y mayor a 0 para en institucion. | Normativa explicita por mensajes de error. |
| Completar horas planta/contrata/honorarios con `0` si no corresponden. | Normativa explicita por mensajes de error. |
| `JERARQUIA_ACADEMICA` textual en mayusculas y sin espacios indebidos. | Normativa explicita. |
| `JERARQUIA_ACADEMICA_OCDE` en codigos 1 a 5. | Normativa explicita. |
| `VIGENCIA` en `0` o `1`. | Normativa explicita. |
| `TOTAL_HORAS_CONTRATADAS` no superior a 56 para fuera de institucion. | Normativa explicita. |
| `MOTIVO_COMISION_FUERA_IES` con codigos indicados por instructivo. | Normativa explicita. |
| Campos de programa de estudios solo cuando aplique comision de estudios. | Normativa explicita en alcance, pendiente de implementacion exacta. |

### Validaciones De Texto

| Validacion | Clasificacion |
|---|---|
| Mayusculas en campos textuales indicados por instructivo. | Normativa explicita. |
| Sin tildes en campos donde el instructivo pide letras A-Z sin acentos. | Normativa explicita. |
| Sin espacios dobles. | Normativa explicita por mensajes de error. |
| Sin espacios iniciales ni finales. | Normativa explicita por mensajes de error. |
| Sin abreviaciones en nombres/apellidos. | Normativa explicita. |
| Sin caracteres innecesarios fuera de los aceptados por mensajes de error. | Validacion tecnica preventiva. |

## Confirmacion Tecnica Fase 2

| Estructura | Columnas oficiales confirmadas | Separador observado | Estado delimitador de salida |
|---|---:|---|---|
| Personal Academico en la Institucion | 34 | `;` | **PENDIENTE DE CONFIRMACION**; parametrizado en scripts. |
| Personal Academico Fuera de la Institucion | 27 | `;` | **PENDIENTE DE CONFIRMACION**; parametrizado en scripts. |

La lectura de las estructuras con coma produce una sola columna. Por tanto, para validacion de estructura observada se usa `;`; para exportacion final el delimitador queda parametrizado y debe respaldarse con auditoria antes de liberar un archivo PES/SIES.
