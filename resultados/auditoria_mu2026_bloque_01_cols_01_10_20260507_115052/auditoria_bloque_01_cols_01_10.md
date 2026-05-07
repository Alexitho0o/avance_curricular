# Auditoría MU2026 · Bloque 1 · Columnas 1 a 10

Fecha: 2026-05-07 11:50:52

## Columnas revisadas

TIPO_DOC, N_DOC, DV, PRIMER_APELLIDO, SEGUNDO_APELLIDO, NOMBRE, SEXO, FECH_NAC, NAC, PAIS_EST_SEC

## Resumen de validación

| campo            | regla                                                                                                                |   errores | estado   | detalle                                  |
|:-----------------|:---------------------------------------------------------------------------------------------------------------------|----------:|:---------|:-----------------------------------------|
| TIPO_DOC         | Debe ser R o P                                                                                                       |         0 | OK       | Valores distintos de R/P                 |
| N_DOC            | Obligatorio; para RUT solo números                                                                                   |         0 | OK       | Vacíos o RUT con caracteres no numéricos |
| DV               | Para RUT obligatorio; números 0-9 o K. Para Pasaporte debe estar vacío                                               |         0 | OK       | DV inválido según tipo de documento      |
| PRIMER_APELLIDO  | Obligatorio; letras mayúsculas sin acentos, permite diéresis, Ñ, guión y comilla                                     |         0 | OK       | Formato texto identidad                  |
| SEGUNDO_APELLIDO | Opcional cuando corresponda; si viene informado, letras mayúsculas sin acentos, permite diéresis, Ñ, guión y comilla |         0 | OK       | Formato texto identidad                  |
| NOMBRE           | Obligatorio; letras mayúsculas sin acentos, permite diéresis, Ñ, guión y comilla                                     |         0 | OK       | Formato texto identidad                  |
| SEXO             | Debe ser H, M o NB                                                                                                   |         0 | OK       | Valores fuera de catálogo                |
| FECH_NAC         | Obligatoria en formato dd/mm/aaaa                                                                                    |         0 | OK       | Vacía o formato inválido                 |
| NAC              | Debe ser numérico entre 1 y 197                                                                                      |         0 | OK       | Nacionalidad fuera de rango              |
| PAIS_EST_SEC     | Debe ser numérico entre 1 y 197                                                                                      |         0 | OK       | País estudios secundarios fuera de rango |

## Perfil de columnas

| columna          |   filas |   vacios |   unicos | muestra                                                                                                                               |
|:-----------------|--------:|---------:|---------:|:--------------------------------------------------------------------------------------------------------------------------------------|
| TIPO_DOC         |    3442 |        0 |        1 | R                                                                                                                                     |
| N_DOC            |    3442 |        0 |     3442 | 6997215 | 7033642 | 8074726 | 8458882 | 8677490 | 8713447 | 9023349 | 9124599                                                         |
| DV               |    3442 |        0 |       11 | 2 | 1 | 8 | 9 | 4 | K | 0 | 6                                                                                                         |
| PRIMER_APELLIDO  |    3442 |        0 |     1186 | MUNOZ | CROSS | SOLIS | REYES | ANTEZANA | GARRIDO | PLAZA | ELLIOTT                                                                  |
| SEGUNDO_APELLIDO |    3442 |        5 |     1156 | MAGERKURTH | BROWNE | FERNANDEZ | SANDOVAL | GONZALEZ | OSSES | ESPINDOLA | POULSEN                                                   |
| NOMBRE           |    3442 |        0 |     2767 | PAULINA CRISTINA | MARIA ELENA | GABRIEL ANTONIO | LESLY ANDREA | GABRIEL ALBERTO | LUIS PATRICIO | CARLOS ROBERTO ANTONIO | AXEL IAN |
| SEXO             |    3442 |        0 |        3 | M | H | NB                                                                                                                            |
| FECH_NAC         |    3442 |        0 |     2923 | 23/04/1966 | 14/08/1962 | 10/04/1963 | 08/11/1974 | 28/10/1967 | 23/05/1962 | 11/06/1961 | 20/10/1964                                 |
| NAC              |    3442 |        0 |       11 | 38 | 9 | 142 | 41 | 192 | 78 | 52 | 149                                                                                               |
| PAIS_EST_SEC     |    3442 |        0 |        1 | 38                                                                                                                                    |

## Archivos generados

- `resultados/auditoria_mu2026_bloque_01_cols_01_10_20260507_115052/resumen_validacion_bloque_01_cols_01_10.csv`
- `resultados/auditoria_mu2026_bloque_01_cols_01_10_20260507_115052/perfil_columnas_bloque_01_cols_01_10.csv`
- `resultados/auditoria_mu2026_bloque_01_cols_01_10_20260507_115052/muestra_50_filas_bloque_01_cols_01_10.csv`