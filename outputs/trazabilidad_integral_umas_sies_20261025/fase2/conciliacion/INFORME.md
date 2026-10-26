# Fase 2/6 · Hitos 2-3 — Conciliación agregada anual

B/C — Unión por año+código SIES completo, 198 filas. Se leen componentes individuales ya existentes en MU; no se asignan versiones con totales. Se reproducen 990/990 celdas numéricas del puente anterior. Sus explicaciones causales no se adoptan.

| Año | Códigos | CSV total | CSV primer año | MU filas | VIG0 | VIG1 | VIG2 | CSV−MU | CSV−VIG1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 27 | 1033 | 249 | 1038 | 5 | 1033 | 0 | -5 | 0 |
| 2023 | 22 | 1161 | 386 | 1145 | 3 | 1142 | 0 | 16 | 19 |
| 2024 | 33 | 1468 | 573 | 1541 | 86 | 1455 | 0 | -73 | 13 |
| 2025 | 50 | 2522 | 1301 | 2371 | 73 | 2298 | 0 | 151 | 224 |
| 2026 | 66 | 3425 | 1753 | 4105 | 960 | 3145 | 0 | -680 | 280 |

B/C — La tabla anterior conserva todos los niveles. Primer año es suma de valores observados; sus celdas vacías permanecen vacías y se contabilizan en el resumen, sin tratarlas como ceros confirmados. El archivo tiene 280.160 filas de datos y 280.161 registros incluyendo encabezado; 58 columnas. Lectura completa Latin-1; CP1252 estricto no admite todos sus bytes.

## Pregrado según el CSV del mismo año

| Año | Códigos | CSV | MU filas | MU VIG1 | Códigos con diferencia VIG1 | Neto | Positivas | Negativas | Absoluta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 26 | 1033 | 1036 | 1033 | 0 | 0 | 0 | 0 | 0 |
| 2023 | 21 | 1142 | 1145 | 1142 | 2 | 0 | 1 | -1 | 2 |
| 2024 | 27 | 1455 | 1535 | 1455 | 0 | 0 | 0 | 0 | 0 |
| 2025 | 43 | 2371 | 2371 | 2298 | 11 | 73 | 73 | 0 | 73 |
| 2026 | 63 | 3371 | 4105 | 3145 | 48 | 226 | 228 | -2 | 230 |

B/C/E — En 2023 el neto pregrado es 0, pero dos códigos difieren (+1 y −1): no son todos concordantes. En 2026 son 48 códigos pregrado con diferencia: 46 presentes en ambas fuentes y 2 solo en CSV; neto 226 y diferencia absoluta 230. Los 54 de Postítulo están separados, fuera del alcance de BASE. Los 6 códigos solo MU (2 matrículas en 2022 y 6 en 2024) conservan nivel no acreditado por el CSV; no se clasifican por semejanza.

C — DETALLE_CONCILIACION.csv conserva campos fuente vacíos cuando un código no existe en una fuente. Las diferencias de unión usan ceros estructurales explícitos, no valores atribuidos a una celda ausente. RESUMEN_ANUAL.csv separa Pregrado, Postítulo y NIVEL_NO_ACREDITADO; presenta diferencias netas, positivas, negativas y absolutas, coincidencias y exclusivos.

B/C — Identidad se cuenta como TIPO_DOC+N_DOC+DV disponible; las personas únicas por código y por año se presentan separadas de las matrículas. No se exporta ninguna identidad.

E — Coincidir al sumar carreras no acredita redistribuciones de versión/jornada ni justifica corregir personas. La causa de cada diferencia sigue pendiente salvo evidencia específica, que este ejercicio no produce. Primer año CSV es una variable separada del total matrícula. Ninguna tasa de retención fue recalculada.

## Fuentes
- B: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx` — SHA-256 `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`.
- B: `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/0 BASES DE DATOS/MATRÍCULA/Matricula_2007_2026_WEB_10_07_2026.csv` — SHA-256 `4c630e05e07312ebd567ed77b0c26c5d0230380deea4fc89a6123b11b7aba154`.
- B: `/Users/alexi/Documents/GitHub/avance_curricular/procesos/caracterizacion/gobernanza/sies/TABLA_PUENTE_CSV_BASE_RETENCION_MU.csv` — SHA-256 `d4f3675d5d63247b0118412f983729cb18924c2971cea1b7d0ef731e6c8e7803`.
- B: `/Users/alexi/Documents/GitHub/avance_curricular/procesos/caracterizacion/gobernanza/sies/TABLA_PUENTE_CSV_BASE_RETENCION_MU.manifest.json` — SHA-256 `c205fed8061bc02ea2623eea8d789ffc1bc1355e41f82bb1298d319bd76b08ad`.

C — Reproducción: ejecutar conciliar_mu_csv.py con --salida apuntando a una carpeta nueva. Fuentes, edición activa, rama y HEAD verificados sin cambios. Sin commit/push.
