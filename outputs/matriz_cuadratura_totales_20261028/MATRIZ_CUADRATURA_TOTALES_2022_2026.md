# Matriz de cuadratura 2022–2026

B/C: datos observados y cálculos; E: pendiente. H001 cuenta filas; validar unicidad antes de llamar personas.

| Año | MU filas | Pregrado + nivel no acreditado | VIG1 / VIG0 pregrado | SIES pregrado + postítulo | Brecha pregrado | H001 candidatos / elegibles (filas) | Titulación carga / SIES t−1 (registros) | Respaldo de código único v20 / solo RUT / no localizado |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2022 | 1038 | 1036 + 2 | 1033 / 3 | 1033 + 0 | 0 | 310 / 305 | 214 / 214 | 897 / 141 / 0 |
| 2023 | 1145 | 1145 + 0 | 1142 / 3 | 1142 + 19 | 0 | 370 / 366 | 283 / 294 | 1085 / 59 / 1 |
| 2024 | 1541 | 1535 + 6 | 1455 / 80 | 1455 + 13 | 0 | 636 / 558 | 346 / 342 | 1211 / 320 / 10 |
| 2025 | 2371 | 2371 + 0 | 2298 / 73 | 2371 + 151 | 73 | 1255 / 1150 | E / 270 | 1659 / 685 / 27 |
| 2026 | 4105 | 4105 + 0 | 3145 / 960 | 3371 + 54 | 226 | No aplica aún / E | 431 / 431 | 1847 / 2258 / 0 |

La última columna conserva la medición anterior denominada respaldo de código único en v20: exige código en v20 pero compara solo su componente C con MU, por lo que no acredita que el código completo coincida. No es la cobertura de carrera ni indica vigencia.

MU 2025: CUADRA contra el total incluido VIG 0 (2.371 = 2.371); causa metodológica E, ver H001 § Cierre a nivel carrera. H001 2026: NO APLICA AÚN; requiere MU 2027.

## Cobertura por familia SIES y CODCARPR de Datos Alumnos

| Año | RUT+DV y carrera candidata | RUT+DV, CODCARPR fuera de candidatos | RUT+DV sin familia mapeada | No localizado | Sin RUT+DV comparable (incluido en no localizado) |
|---|---:|---:|---:|---:|---:|
| 2022 | 1009 | 26 | 3 | 0 | 0 |
| 2023 | 1112 | 32 | 0 | 1 | 0 |
| 2024 | 1517 | 14 | 0 | 10 | 0 |
| 2025 | 2303 | 41 | 0 | 27 | 25 |
| 2026 | 4032 | 0 | 73 | 0 | 0 |

Las equivalencias son candidatos de grupos existentes y relaciones operativas 2026 del maestro. No acreditan plan ni vigencia histórica; una carrera fuera del conjunto puede deberse a cobertura incompleta del catálogo. No localizado incluye documentos no comparables.

### Matrículas en familias sin mapeo — desglose agregado

| Año MU | Familia SIES | Matrículas | Clase |
|---|---|---:|---|
| 2022 | I162S2C35J4 | 3 | B/C; equivalencia E |
| 2026 | I162S3C114J2 | 35 | B/C; equivalencia E |
| 2026 | I162S3C115J2 | 20 | B/C; equivalencia E |
| 2026 | I162S3C91J2 | 18 | B/C; equivalencia E |

El desglose suma 3 matrículas en 2022 y 73 en 2026; los demás años no presentan esta categoría. No se modifica ninguna equivalencia.
En 2026, entre las matrículas sin respaldo v20, 1790 pertenecen a personas sin ninguna observación del diccionario en 2026; no se afirma que la causa sea exclusivamente PROMEDIOS.

## Diferencias de titulación por código (carga menos publicación)

| Proceso | Código SIES | Carga | Publicación | Diferencia | Estado |
|---|---|---:|---:|---:|---|
| 2023 | I162S2C1J4V2 | 2 | 8 | -6 | E |
| 2023 | I162S2C3J4V2 | 9 | 12 | -3 | E |
| 2023 | I162S2C57J2V1 | 14 | 15 | -1 | E |
| 2023 | I162S2C6J2V1 | 3 | 4 | -1 | E |
| 2024 | 162S2C47J1V1 | 1 | 0 | 1 | E |
| 2024 | I162S2C3J4V2 | 67 | 64 | 3 | E |
| 2024 | I162S2C47J1V1 | 7 | 8 | -1 | E |
| 2024 | I162S2C57J2V1 | 11 | 10 | 1 | E |

En 2024 se observó `162S2C47J1V1` sin I y una diferencia inversa para `I162S2C47J1V1`: al normalizar el prefijo únicamente en el derivado se anulan estas dos diferencias por código [B/C]. No demuestra igualdad individual. La diferencia neta del proceso no cambia. El resto permanece E.

| Proceso 2024: código derivado | Carga normalizada | Publicación | Diferencia | Estado |
|---|---:|---:|---:|---|
| I162S2C3J4V2 | 67 | 64 | 3 | E |
| I162S2C57J2V1 | 11 | 10 | 1 | E |

Los motivos H001 se encuentran en el JSON: la clasificación cuenta cada fila una vez por el primer motivo aplicable. La correspondencia entre carga de titulados y período publicado es observada, no norma acreditada. El glosario 2007–2025, pág. 1, describe AÑO como año del proceso, sin establecer aquí el desfase t−1 de cat_periodo; no se presume equivalencia de campos. El respaldo 2024 tiene alcance pendiente. No hay enlace individual RUT–MRUN.

Pendientes:
- Alineación t↔t−1 de titulación observada B; regla escrita no localizada en esta ejecución.
- Inventario de búsquedas de titulación 20261026 revisado: describe scripts, no acredita carga de proceso 2025; carácter final del respaldo 2024 pendiente.
- Titulación y publicación: diferencias por código no explicadas; MRUN no permite enlace por persona.
- DATOSDEALUMNOS_12159 figura en catálogo y descriptor v20 con hash e idéntica copia; no hay fecha de extracción ni evidencia de que sea el extracto más reciente.
- Copia antigua del consolidado cfcf9099… no utilizada; fuente única OneDrive 70758082…

## Titulación frente a matrícula: comparación preliminar por persona

| Proceso | Registros de carga observada | Personas con documento comparable | Presentes en MU t−1 | Presentes en MU t |
|---|---:|---:|---:|---:|
| 2022 | 214 | 214 | 106 | 26 |
| 2023 | 283 | 282 | 130 | 26 |
| 2026 | 431 | 429 | 320 | 42 |
| 2024 | 346 | 345 | 204 | 57 |

B/C: presencias por documento, sin atribución de expediente. MU 2021 procede del respaldo histórico inventariado, separado de la base 142342.
