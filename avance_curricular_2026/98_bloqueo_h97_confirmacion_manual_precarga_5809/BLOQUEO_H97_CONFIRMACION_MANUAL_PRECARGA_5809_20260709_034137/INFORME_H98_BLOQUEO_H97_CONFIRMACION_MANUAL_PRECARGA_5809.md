# H98 — Bloqueo H97 y confirmación de estructura oficial 5809

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

5809 Matrícula Avance Curricular, ID Carga 16768.

## Dictamen

Se descarta H97 como archivo de carga porque excluye `VIGENCIA`.

## Fundamento

La fuente superior del proceso es el instructivo oficial. La precarga original 5809 contiene 22 columnas, incluyendo `FECHA_NACIMIENTO` y `VIGENCIA`.

## Resultado técnico

- Precarga original filas: 2371
- Precarga original columnas: 22
- H95 filas: 2371
- H95 columnas: 22
- Diferencias en campos precargados 1-15 + VIGENCIA entre precarga y H95: 0
- H97 en Escritorio: ELIMINADO_DEL_ESCRITORIO_Y_RESPALDADO_EN_H98

## Conclusión

No corresponde eliminar `VIGENCIA` para adaptar la carga. Debe prevalecer la estructura oficial/precarga de 22 campos. La inconsistencia debe tratarse como problema de estructura activa de plataforma, plantilla o selección de carga, no como modificación del archivo oficial.

## Archivo recomendado para defensa técnica

`/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/95_validacion_final_sies_ready_5809/VALIDACION_FINAL_SIES_READY_5809_20260709_030847/5809_MATRICULA_AVANCE_CURRICULAR_2026_SIES_READY.csv`

## Archivo no recomendado

H97 queda descartado por exclusión de `VIGENCIA`.
