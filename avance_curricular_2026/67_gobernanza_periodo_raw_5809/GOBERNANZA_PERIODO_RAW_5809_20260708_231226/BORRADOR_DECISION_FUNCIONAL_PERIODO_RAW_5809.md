# Borrador decision funcional PERIODO raw 5809

Proceso: Avance Curricular SIES 2026
Subproyecto: Gobernanza PERIODO raw para columnas 16, 17 y 18 del archivo 5809 Matricula Avance Curricular
Ano proceso: 2026
Ano referencia datos: 2025
Declaracion carga: NO_LISTO_PARA_CARGA

Estimadas/os,

Se solicita validacion funcional especifica sobre el significado institucional del campo PERIODO raw observado en PROMEDIOS para su eventual uso en el archivo 5809 Matricula Avance Curricular, columnas 16, 17 y 18.

Esta solicitud no implica carga, no modifica fuentes originales, no corrige datos, no genera SIES_READY y no recalcula columnas 20-21.

## Preguntas a validar

1. Confirmar el significado institucional de PERIODO raw 1, 2, 3, 4 y 5 en PROMEDIOS.
2. Confirmar si PERIODO 1 corresponde a primer semestre para Avance Curricular 5809.
3. Confirmar si PERIODO 2 corresponde a segundo semestre para Avance Curricular 5809.
4. Confirmar si PERIODO 3 corresponde a segundo semestre, periodo especial, recuperacion, verano u otro significado.
5. Confirmar si PERIODO 4 y PERIODO 5 deben contarse en UNIDADES_CURSADAS anual 2025.
6. Confirmar si PERIODO 4 y PERIODO 5 deben afectar CURSO_1ER_SEM o CURSO_2DO_SEM.
7. Confirmar si los 17 casos PERIODO_NO_1_2 deben mantenerse como 5809 o corregirse en un hito posterior.
8. Confirmar que la decision aplica solo a Avance Curricular 5809 columnas 16-18 y no a Matricula Unificada ni a columnas 20-21.

## Evidencia resumida

- PROMEDIOS 2025 contiene PERIODO 1,2,3,4 y 5.
- Hito 55 detecto 17 casos con causa principal PERIODO_NO_1_2.
- Hito 64 bloqueo el uso automatico de PERIODO 2/3=segundo semestre.
- Hito 66 mantuvo bloqueados los 17 casos hasta gobernanza especifica.
- La simulacion documental del hito 67 muestra que mantener 5809 calza 17/17, pero requiere decision funcional para ser cierre valido.

Resultado esperado:

- Definir tratamiento por PERIODO raw 1,2,3,4,5.
- Autorizar o bloquear su uso en columnas 16, 17 y 18.
- Indicar si los 17 casos se mantienen sin cambio o deben pasar a correccion posterior gobernada.
