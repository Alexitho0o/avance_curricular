# Fase 3 - Validacion muestra 1000 CODCLI (NIV_ACA)

Fecha: 2026-03-31

## Configuracion
- input: `/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx`
- oferta_duracion: `/Users/alexi/Downloads/1668382 Captura IES Incremental5320 Oferta Académica Titulados5319 Titulados Histórico.xlsx`
- sample_codcli: `1000`
- sample_seed: `42`
- periodo_policy: `map_3_to_2`

## Resultado clasificacion
- confirmado_1_a_1: 595 (59.5%)
- requiere_revision_manual: 395 (39.5%)
- sin_insumos_suficientes: 10 (1.0%)

## Criterio de aprobacion (propuesto)
- confirmado_1_a_1 >= 55%
- sin_insumos_suficientes <= 10%
- requiere_revision_manual <= 45%
- resultado: APROBADO

## Validacion por criterio
- confirmado_ok: True
- sin_insumos_ok: True
- manual_ok: True

## Top motivos (revision manual)
- nivel_observado_no_coherente_con_nivel_esperado: 346
- nivel_observado_supera_duracion: 192
- duracion_carrera_ambigua: 36
- conflicto_anio_codcli_vs_anioingreso: 31
- nivel_esperado_supera_duracion: 17
- conflicto_carrera_hoja1_vs_datos_alumnos: 15

## Top motivos (sin insumos)
- sin_duracion_carrera: 10

## Clasificacion por ESTADOACADEMICO

| ESTADOACADEMICO | confirmado_1_a_1 | requiere_revision_manual | sin_insumos_suficientes |
|---|---:|---:|---:|
| EGRESADO | 2 | 0 | 0 |
| ELIMINADO | 67 | 15 | 0 |
| NA | 0 | 15 | 0 |
| SUSPENDIDO | 26 | 8 | 0 |
| TITULADO | 0 | 104 | 0 |
| VIGENTE | 500 | 253 | 10 |

## Observacion sobre estados/situaciones
- Se detectaron estados del catalogo operativo: VIGENTE, ELIMINADO, TITULADO, SUSPENDIDO, EGRESADO.
- La regla actual de NIV_ACA aun no diferencia por estado academico; eso queda como siguiente mejora opcional.