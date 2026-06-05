# Diagnostico De Insumos Oficiales Personal Academico SIES 2026

Fecha de diagnostico: 2026-06-08.

## Fuentes Localizadas

Las tres fuentes oficiales fueron localizadas en la raiz del repositorio y copiadas sin modificacion a `personal_academico_2026/insumos/`.

| Fuente | Forma NFC del nombre oficial | SHA-256 |
|---|---|---|
| `20260421_57181_20260420_Estructura_Personal_Académico_en_Institución_2026.csv` | `20260421_57181_20260420_Estructura_Personal_Académico_en_Institución_2026.csv` | `0759079bc3753faa6bd6ca3fc7f9a1053231778211cec3c0c0a216e6f70fed30` |
| `20260421_84406_20260420_Estructura_Personal_Académico_Fuera_Institución_2026.csv` | `20260421_84406_20260420_Estructura_Personal_Académico_Fuera_Institución_2026.csv` | `fdb6bba763bb348373773509e0b1032d76df151b67569eef0c5853bca9bbd94f` |
| `Personal Académico SIES - Instructivo 2026.txt` | `Personal Académico SIES - Instructivo 2026.txt` | `06379693c3f5234f418aa1305803b875a70f529f452cc0dda7a0a423a7de7baf` |

Nota: macOS muestra los acentos con composicion Unicode NFD en los nombres locales. La forma NFC coincide con los nombres oficiales indicados por el proyecto.

## 1. Archivo De Estructura En Institucion

Nombre local:

```text
20260421_57181_20260420_Estructura_Personal_Académico_en_Institución_2026.csv
```

Nombre oficial en forma NFC:

```text
20260421_57181_20260420_Estructura_Personal_Académico_en_Institución_2026.csv
```

- Cantidad exacta de campos: 34.
- Delimitador observado en el CSV de estructura: `;`.
- Filas observadas: 1 fila de encabezados oficiales.
- Fuente normativa complementaria: Instructivo, Anexo I, carga academicos en la institucion, ID 16761.

Orden exacto de columnas:

| Orden | Campo oficial |
|---:|---|
| 1 | `TIPO_DOCUMENTO` |
| 2 | `NUM_DOCUMENTO` |
| 3 | `DV` |
| 4 | `PRIMER_APELLIDO` |
| 5 | `SEGUNDO_APELLIDO` |
| 6 | `NOMBRES` |
| 7 | `SEXO` |
| 8 | `FECHA_NACIMIENTO` |
| 9 | `NACIONALIDAD` |
| 10 | `NIVEL_FORMACION_ACADEMICO` |
| 11 | `NOMBRE_TITULO_O_GRADO` |
| 12 | `NOMBRE_INSTITUCION_OBT_TITULO` |
| 13 | `PAIS_OBTENCION_TIT_O_GRADO` |
| 14 | `FECHA_OBT_TIT_O_GRADO` |
| 15 | `NIVEL_FORMACION_ESPECIALIDAD` |
| 16 | `TIPO_ESPECIALIDAD` |
| 17 | `NOMBRE_ESPECIALIDAD` |
| 18 | `NOMBRE_INST_OBT_ESPECIALIDAD` |
| 19 | `PAIS_OBTENCION_ESPECIALIDAD` |
| 20 | `FECHA_OBTENCION_ESPECIALIDAD` |
| 21 | `PRINCIPAL_CARGO_ACADEMICO` |
| 22 | `CARGO_NORMALIZADO` |
| 23 | `NIVEL_SUPERIOR_ADSCRIPCION` |
| 24 | `NIVEL_SECUNDARIO_ADSCRIPCION` |
| 25 | `COMUNA_MAYOR_FUNCION` |
| 26 | `NOMBRE_PRINCIPAL_PROGRAMA` |
| 27 | `TOTAL_HORAS_PRINCIPAL_PROGRAMA` |
| 28 | `COMUNA_PRINCIPAL_PROGRAMA` |
| 29 | `NUM_HORAS_PLANTA` |
| 30 | `NUM_HORAS_CONTRATA` |
| 31 | `NUM_HORAS_HONORARIOS` |
| 32 | `JERARQUIA_ACADEMICA` |
| 33 | `JERARQUIA_ACADEMICA_OCDE` |
| 34 | `VIGENCIA` |

Campos con obligatoriedad explicitamente visible en el Anexo I o en mensajes de error del instructivo:

- `TIPO_DOCUMENTO`
- `NUM_DOCUMENTO`
- `NOMBRES`
- `SEXO`
- `FECHA_NACIMIENTO`
- `NACIONALIDAD`
- `NIVEL_FORMACION_ACADEMICO`
- `NOMBRE_TITULO_O_GRADO`
- `FECHA_OBT_TIT_O_GRADO`
- `PRINCIPAL_CARGO_ACADEMICO`
- `CARGO_NORMALIZADO`
- `COMUNA_MAYOR_FUNCION`
- `COMUNA_PRINCIPAL_PROGRAMA`
- `NUM_HORAS_PLANTA`
- `NUM_HORAS_CONTRATA`
- `NUM_HORAS_HONORARIOS`
- `JERARQUIA_ACADEMICA`
- `JERARQUIA_ACADEMICA_OCDE`
- `VIGENCIA`
- `NOMBRE_INSTITUCION_OBT_TITULO`, por mensaje de error que indica que no puede estar vacio.

Observacion conservadora: el instructivo tambien indica que se deben cargar todos los campos, obligatorios y no obligatorios. Por tanto, aun cuando un campo no figure como obligatorio, debe estar presente en la estructura.

## 2. Archivo De Estructura Fuera De Institucion

Nombre local:

```text
20260421_84406_20260420_Estructura_Personal_Académico_Fuera_Institución_2026.csv
```

Nombre oficial en forma NFC:

```text
20260421_84406_20260420_Estructura_Personal_Académico_Fuera_Institución_2026.csv
```

- Cantidad exacta de campos: 27.
- Delimitador observado en el CSV de estructura: `;`.
- Filas observadas: 1 fila de encabezados oficiales.
- Fuente normativa complementaria: Instructivo, Anexo II, carga academicos fuera de la institucion, ID 16760.

Orden exacto de columnas:

| Orden | Campo oficial |
|---:|---|
| 1 | `TIPO_DOCUMENTO` |
| 2 | `NUM_DOCUMENTO` |
| 3 | `DV` |
| 4 | `PRIMER_APELLIDO` |
| 5 | `SEGUNDO_APELLIDO` |
| 6 | `NOMBRES` |
| 7 | `SEXO` |
| 8 | `FECHA_NACIMIENTO` |
| 9 | `NACIONALIDAD` |
| 10 | `NIVEL_FORMACION_ACADEMICO` |
| 11 | `NOMBRE_TITULO_O_GRADO` |
| 12 | `NOMBRE_INSTITUCION_OBT_TITULO` |
| 13 | `PAIS_OBTENCION_TIT_O_GRADO` |
| 14 | `FECHA_OBT_TIT_O_GRADO` |
| 15 | `NIVEL_FORMACION_ESPECIALIDAD` |
| 16 | `TIPO_ESPECIALIDAD` |
| 17 | `NOMBRE_ESPECIALIDAD` |
| 18 | `NOMBRE_INST_OBT_ESPECIALIDAD` |
| 19 | `PAIS_OBTENCION_ESPECIALIDAD` |
| 20 | `FECHA_OBTENCION_ESPECIALIDAD` |
| 21 | `TOTAL_HORAS_CONTRATADAS` |
| 22 | `MOTIVO_COMISION_FUERA_IES` |
| 23 | `NOMBRE_PROGRAMA_DE_ESTUDIOS` |
| 24 | `INSTITUCION_PROGRAMA_ESTUDIOS` |
| 25 | `PAIS_PROGRAMA_ESTUDIOS` |
| 26 | `FECHA_INICIO_PROGRAMA_ESTUDIOS` |
| 27 | `VIGENCIA` |

Campos con obligatoriedad explicitamente visible en el Anexo II:

- `TIPO_DOCUMENTO`
- `NUM_DOCUMENTO`
- `PRIMER_APELLIDO`
- `NOMBRES`
- `SEXO`
- `FECHA_NACIMIENTO`
- `NACIONALIDAD`
- `NIVEL_FORMACION_ACADEMICO`
- `NOMBRE_TITULO_O_GRADO`
- `NOMBRE_INSTITUCION_OBT_TITULO`
- `PAIS_OBTENCION_TIT_O_GRADO`
- `FECHA_OBT_TIT_O_GRADO`
- `VIGENCIA`

Observacion conservadora: el instructivo tambien indica que se deben cargar todos los campos, obligatorios y no obligatorios. Por tanto, aun cuando un campo no figure como obligatorio, debe estar presente en la estructura.

## 3. Reglas Explicitas De Formato

Reglas respaldadas por el instructivo:

- `TIPO_DOCUMENTO`: valores `R` para RUT y `P` para Pasaporte; usar letra mayuscula.
- `NUM_DOCUMENTO`: usar solo numeros para RUT; no usar puntos, comas ni guiones; no debe comenzar con `0`.
- `DV`: para `R`, usar `0` a `9` o `K`; para `P`, debe ser nulo.
- Apellidos, nombres, cargos, instituciones, comunas, programas y jerarquia: usar letras mayusculas de la A a la Z sin acentos, con restricciones de espacios iniciales, finales y dobles espacios segun mensajes de error.
- `SEXO`: valores `M`, `H`, `NB`.
- Fechas: formato `DD-MM-AAAA`.
- `NACIONALIDAD`, pais de obtencion y pais de programa: codigos numericos de la tabla de paises, rango 1 a 197.
- `NIVEL_FORMACION_ACADEMICO`: codigos 1 a 8.
- `NIVEL_FORMACION_ESPECIALIDAD`: codigos 1 a 2 cuando corresponda.
- `TIPO_ESPECIALIDAD`: el Anexo I/II muestra categorias de especialidad; existe una inconsistencia pendiente indicada mas abajo.
- Horas: usar numeros; maximo 56 horas semanales; para horas decimales usar coma y dos decimales.
- `CARGO_NORMALIZADO`: codigos 1 a 11.
- `JERARQUIA_ACADEMICA_OCDE`: codigos 1 a 5.
- `VIGENCIA`: `0` para eliminar registro y `1` para mantener/considerar registro.
- Las fechas de obtencion de titulo/grado y especialidad no deben ser posteriores al 31-05-2026.
- `FECHA_NACIMIENTO` no puede ser menor al 01-01-1900 ni mayor al 31-05-2008, segun mensajes de error.

## 4. Reglas Explicitas De Carga

Reglas respaldadas por el instructivo:

- La carga se realiza en PES, no por correo electronico.
- El archivo debe cargarse en formato CSV y sin comprimir.
- El nombre del archivo no tiene restriccion indicada por el instructivo.
- El plazo de carga indicado es 12 de junio de 2026.
- Para carga efectiva, el instructivo indica eliminar encabezados antes de subir el archivo.
- Todos los campos deben ser cargados.
- Las cargas son acumulativas.
- La carga usa combinacion entre `TIPO_DOCUMENTO` y `NUM_DOCUMENTO`; si se sube mas de una vez la combinacion, el sistema reemplaza el resto de la informacion del registro.
- Si el historial queda con errores de datos, la informacion no se carga y debe corregirse y subirse nuevamente hasta resultado finalizado.

## 5. Diferencias Entre Ambos Archivos

| Aspecto | En Institucion | Fuera De Institucion |
|---|---|---|
| ID de carga PES | 16761 | 16760 |
| Cantidad de campos | 34 | 27 |
| Campos compartidos | 1 a 20 y `VIGENCIA` | 1 a 20 y `VIGENCIA` |
| Campos distintivos | Cargo, cargo normalizado, adscripcion, comuna, programa principal, horas por tipo de contrato, jerarquia institucional y OCDE. | Total de horas contratadas antes de comision, motivo de comision fuera de IES y campos de programa de estudios. |
| Situacion reportada | Academicos contratados que realizan actividades academicas en la institucion al momento de informar. | Academicos contratados o de planta que estan en comision de servicio o permiso especial fuera de la institucion. |

## 6. Advertencias Normativas

- Debe informarse todo el personal academico con contrato vigente con la institucion durante mayo de 2026.
- Cada academico debe informarse solo una vez para evitar duplicidades.
- Para una misma persona deben consolidarse funciones y horas en una unica fila cuando corresponda.
- Las horas son cronologicas semanales y no pueden exceder 56 horas semanales en la institucion.
- Si un contrato esta en horas mensuales, el instructivo indica dividir por 4,3 y aproximar a enteros para calcular promedio semanal.
- Personal profesional/administrativo con docencia directa debe clasificarse con cargo normalizado 10 y solo informar horas de docencia directa; el instructivo advierte que 23 o mas horas no corresponde a esa categoria.
- Los titulos y grados informados deben haber sido obtenidos hasta el 31 de mayo de 2026.
- Las especialidades/subespecialidades deben informarse en su seccion correspondiente cuando apliquen.

## 7. Pendientes Por No Explicitacion O Tension Normativa

- Delimitador final: las estructuras oficiales observadas usan `;`, pero el instructivo menciona CSV delimitado por comas. No se debe exportar archivo final sin decision confirmada.
- Encabezado: las estructuras oficiales traen encabezados, pero el instructivo indica eliminar encabezados antes de subir. Debe distinguirse validacion de plantilla versus exportacion final PES.
- `TIPO_ESPECIALIDAD`: los anexos muestran cinco categorias, incluyendo Enfermeria; los mensajes de error indican valores de 1 a 4. Debe confirmarse antes de validar estrictamente.
- Obligatoriedad de algunos campos: la extraccion textual del PDF puede desplazar "Campo obligatorio". Solo se documentan como obligatorios los casos visibles con claridad o mensajes de error explicitos.
- No existe aun fuente institucional de datos de personal ni reglas de transformacion desde sistemas internos.
- No se ha construido catalogo de paises en `catalogos/`; el instructivo contiene la tabla, pero esta fase no materializa catalogos.
- No se han definido nombres finales institucionales de los CSV.
- No se han creado scripts de lectura, normalizacion, validacion ni exportacion.
