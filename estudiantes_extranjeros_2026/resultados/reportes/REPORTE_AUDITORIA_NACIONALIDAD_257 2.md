# Reporte Auditoría Trazable Nacionalidad — 257 Registros
Generado: 2026-06-23 14:14:36

## Archivos generados
- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/AUDITORIA_TRAZABLE_NACIONALIDAD_257.xlsx`
- Inspección: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/INSPECCION_PROMEDIOS_ALUMNOS_DATOS_PERSONALES.csv`
- Auditoría generación: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/AUDITORIA_GENERACION_EXCEL_NACIONALIDAD_257.csv`

## Hoja de datos personales identificada
| Campo | Valor |
|---|---|
| Nombre de la hoja | DatosAlumnos |
| Filas de datos | 13,707 |
| Columnas originales | 74 |
| Columna NACIONALIDAD existe | SÍ (texto, no código) |
| Columna PAIS_DE_ORIGEN existe | NO |
| Columna PAIS_ESTUDIOS_SECUNDARIOS existe | NO |

## Confirmación de 257 registros
- Registros en universo depurado: **257** ✓

## TABLA 1 — NACIONALIDAD

| Estado | Registros |
|---|---:|
| SIES y DatosAlumnos coinciden | 54 |
| SIES con dato / DatosAlumnos vacío | 5 |
| SIES vacío / DatosAlumnos con dato | 182 |
| Ambas fuentes vacías | 1 |
| Conflicto entre fuentes | 15 |
| Código Chile 38 | 0 |
| Código inválido | 0 |
| **Total** | **257** |

## TABLA 2 — PRIORITARIOS

| Prioridad | Registros | Motivo principal |
|---|---:|---|
| Prioridad 1 | 16 | Ambas fuentes sin dato / conflicto Chile-extranjero / código inválido |
| Prioridad 2 | 187 | Una fuente sin dato / Chile detectado en una fuente |
| Prioridad 3 | 0 | Diferencias menores o sin prioridad activa |

## TABLA 3 — DISPONIBILIDAD DE DATOS EN DatosAlumnos

| Campo | Existe como columna | Registros con dato | Registros vacíos |
|---|---|---:|---:|
| Nacionalidad | SÍ (texto) | 251 | 6 |
| País de origen | NO | 0 | 13707 |
| País estudios secundarios | NO | 0 | 13707 |
| Correo institucional (Mail_Inst) | SÍ | — | — |
| Correo personal (MAIL) | SÍ | — | — |
| Teléfono (FONOACTUAL) | SÍ | — | — |
| Dirección (DIRECCIONACTUAL) | SÍ | — | — |

## Hashes de integridad
| Archivo | Hash SHA-256 (16 chars) |
|---|---|
| UNIVERSO_DEPURADO | 9c78b2640f1dbec6 |
| PRECARGA_SIES_ORIGINAL | 6d0fe6a9a9357ec6 |
| PROMEDIOSDEALUMNOS | 3013fed700f871f9 |
| MATRICULA_CONTROL | 9e4cdaf0f3fbd900 |
| EXCEL_AUDITORIA (salida) | b7701bf5a3c2a038 |

## Notas normativas críticas
- **EL RUT NO DEFINE LA NACIONALIDAD.**
- La NACIONALIDAD SOLO PUEDE CONFIRMARSE MEDIANTE EL CAMPO NACIONALIDAD O UNA FUENTE INSTITUCIONAL OFICIAL.
- En DatosAlumnos, CIUDADCOLEGIO y COMUNACOLEGIO NO son equivalentes a país de estudios secundarios.
- PAIS_DE_ORIGEN y PAIS_ESTUDIOS_SECUNDARIOS no existen como columnas en DatosAlumnos.
