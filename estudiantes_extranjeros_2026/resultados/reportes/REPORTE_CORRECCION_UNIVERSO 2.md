# Reporte Correccion Universo Extranjeros Regulares 2025

Fecha: 2026-06-18 10:51:06

## Resultado

- Precarga PES: PRECARGA_NO_ENCONTRADA
- Universo reconstruido total auditado: 104
- Base maestra corregida: 104
- Inclusion: {'SI': 102, 'PENDIENTE_CONFIRMACION': 2}
- Por fuente: {'MATRICULA_OFICIAL_2025': 99, 'OTRA_EVIDENCIA_2025': 5}
- Por clasificacion: {'CONFIRMADO_MATRICULA_2025': 98, 'NACIONALIDAD_POR_CONFIRMAR': 2, 'CONFIRMADO_OTRA_EVIDENCIA_2025': 4}
- Comparacion de 30 anteriores: {'CONFIRMADO_MATRICULA_2025': 25, 'CONFIRMADO_OTRA_EVIDENCIA_2025': 4, 'NACIONALIDAD_PENDIENTE': 1}
- Validacion: {'PENDIENTE': 34, 'ADVERTENCIA': 113}
- Respaldo previo: `estudiantes_extranjeros_2026/backups/pre_correccion_universo_20260618_105106`

## Cobertura Base Corregida

| Variable | Total | Completos | Pendientes | Conflictos | No aplica | Cobertura | Accion |
|---|---:|---:|---:|---:|---:|---:|---|
| TIPO_DOCUMENTO | 104 | 104 | 0 | 0 | 0 | 100.0% | Sin accion |
| NUM_DOCUMENTO | 104 | 104 | 0 | 0 | 0 | 100.0% | Sin accion |
| DV | 104 | 104 | 0 | 0 | 0 | 100.0% | Sin accion |
| PRIMER_APELLIDO | 104 | 104 | 0 | 0 | 0 | 100.0% | Sin accion |
| SEGUNDO_APELLIDO | 104 | 101 | 3 | 0 | 0 | 97.1% | Gestionar/confirmar |
| NOMBRES | 104 | 104 | 0 | 0 | 0 | 100.0% | Sin accion |
| SEXO | 104 | 104 | 0 | 0 | 0 | 100.0% | Sin accion |
| FECHA_NACIMIENTO | 104 | 104 | 0 | 0 | 0 | 100.0% | Sin accion |
| NACIONALIDAD | 104 | 102 | 2 | 0 | 0 | 98.1% | Gestionar/confirmar |
| TIPO_RESIDENCIA_ESTUDIANTE | 104 | 0 | 104 | 0 | 0 | 0.0% | Gestionar/confirmar |
| PAIS_DE_ORIGEN | 104 | 0 | 104 | 0 | 0 | 0.0% | Gestionar/confirmar |
| PAIS_ESTUDIOS_SECUNDARIOS | 104 | 0 | 104 | 0 | 0 | 0.0% | Gestionar/confirmar |
| CODIGO_UNICO | 104 | 72 | 0 | 32 | 0 | 69.2% | Gestionar/confirmar |
| ANIO_INGRESO_CARRERA_ACTUAL | 104 | 30 | 74 | 0 | 0 | 28.8% | Gestionar/confirmar |
| SEM_INGRESO_CARRERA_ACTUAL | 104 | 30 | 74 | 0 | 0 | 28.8% | Gestionar/confirmar |
| ANIO_INGRESO_CARRERA_ORIGEN | 104 | 0 | 104 | 0 | 0 | 0.0% | Gestionar/confirmar |
| SEM_INGRESO_CARRERA_ORIGEN | 104 | 0 | 104 | 0 | 0 | 0.0% | Gestionar/confirmar |
| NOMBRE_UNIVERSIDAD_ORIGEN | 104 | 0 | 0 | 0 | 104 | 0.0% | Sin accion |
| PAIS_UNIVERSIDAD_ORIGEN | 104 | 0 | 0 | 0 | 104 | 0.0% | Sin accion |
| VIGENCIA | 104 | 104 | 0 | 0 | 0 | 100.0% | Sin accion |

## Decision

No generar CSV final PES hasta incorporar la precarga oficial o confirmar institucionalmente su ausencia, resolver nacionalidades pendientes, campos criticos y codigos unicos ambiguos.
