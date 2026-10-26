# Comprobación de las 20 personas sin llave comparable

Fecha: 2026-10-21T11:54:38.469662-03:00. Proceso: retención intermedia IPSS 162; cohorte 2025; observaciones T2/T3 2026.

**B/C. Resultado:** se recuperó CODCLI para 18 personas. Diecisiete tienen un CODCLI observado y una tiene dos (19 CODCLI distintos). No se eligió una matrícula para descartar la otra. Dos personas siguen sin CODCLI identificado en los respaldos revisados.

**B/C. Causa del aviso:** las 20 filas MU2025 están informadas con TIPO_DOC=P y DV vacío. El cruce anterior solo construyó llave de listado para TIPO_DOC=R. La falta de llave no era evidencia de ausencia ni de deserción.

**B/C. Puente verificable:** IPSS_Procesamiento.xlsx, hoja 2025_carga, conserva RUT (J), N_DOC (BU) y DV (BV) en la misma fila. Se observaron 20 correspondencias unívocas N_DOC–identificador UMAS. Ese identificador permite recuperar CODCLI en los respaldos; el seguimiento posterior se hace por CODCLI exacto. No se usaron nombres, fecha de nacimiento ni sexo.

**B/C. Aporte de CODCLI:** en DatosAlumnos_12112, 17 personas se encuentran con el identificador del respaldo 2025 y una adicional se recupera por el mismo CODCLI con otro identificador documental observado. No se infiere por semejanza.

## Resultado por carrera (B/C)

| Carrera | Personas revisadas | Con CODCLI identificado | Sin CODCLI identificado |
|---|---:|---:|---:|
| INGENIERIA EN ADMINISTRACION DE EMPRESAS | 1 | 1 | 0 |
| INGENIERIA EN INFORMATICA | 4 | 3 | 1 |
| TECNICO EN ADMINISTRACION DE EMPRESAS | 2 | 2 | 0 |
| TECNICO EN ENFERMERIA | 9 | 9 | 0 |
| TECNICO EN LOGISTICA | 1 | 1 | 0 |
| TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | 3 | 2 | 1 |

## Qué demuestra sobre los cierres (B/C/E)

| Listado recibido | Personas buscables por CODCLI | Encontradas | No localizadas entre buscables | Sin CODCLI para buscar |
|---|---:|---:|---:|---:|
| T2_2026 | 18 | 0 | 18 | 2 |
| T3_2026 | 18 | 0 | 18 | 2 |

**B/E.** En la extracción DatosAlumnos_12112, 14 de las 18 personas identificadas tienen alguna matrícula con estado VIGENTE, tres figuran solo ELIMINADO y una SUSPENDIDO. De las 14 con alguna vigente, una tiene además otra matrícula ELIMINADO. Son estados observados en esa extracción; no equivalen a vigencia acreditada al cierre T2/T3 ni a una tasa de retención.

**B/C/E.** En MU2026 no se encontró fila para las 20 personas mediante los identificadores documentados de este cruce. Esa observación anual se mantiene separada de los cierres T2/T3 y no acredita deserción ni su causa.

**D.** No se modificaron el Excel, las bases, numeradores ni denominadores actuales: 558 / 1.150 y, en el ejercicio separado, 222 / 124. No se crearon salidas con identificadores individuales. Sin commit/push.

## Pendientes (E)

- CODCLI de una persona de Ingeniería en Informática y una de Técnico en Programación y Análisis de Sistemas no identificado en los respaldos revisados.
- Acreditar completitud, fecha efectiva y estados al cierre T2/T3; cero coincidencias entre los 18 buscables no acredita deserción.
- La clasificación P y la correspondencia institucional observada no acreditan que un identificador temporal sea RUN oficial.

## Fuentes verificadas (B/C)

| Fuente / hoja | Ruta | SHA-256 |
|---|---|---|
| BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx / BASE_RETENCION_MU | /Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx | 19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd |
| RETENCION_PRIMER_ANIO_IPSS_162_DIAGNOSTICO_BRECHAS_20260930.xlsx / 02_COHORTE_ELEGIBILIDAD / 01_CATALOGO_CARRERA | /Users/alexi/Documents/GitHub/avance_curricular/outputs/retencion_primer_anio_ipss_162/20260930_000000/RETENCION_PRIMER_ANIO_IPSS_162_DIAGNOSTICO_BRECHAS_20260930.xlsx | 5f0f7c7f0f238556de374d287bf2931ccc8a93a5489f4c2f2b543befd38c77b3 |
| IPSS_Procesamiento.xlsx / 2025_carga!J (RUT), BU (N_DOC), BV (DV) | /Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/2025/Matricula/SIES/06-05-2025/IPSS_Procesamiento.xlsx | e2984ccdf22ecf35c46e1f77275fdd12cda47bd2d77a523860e2cd2cf90127f4 |
| DATOSDEALUMNOS_11998.xlsx / Hoja1 | /Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/DATOSDEALUMNOS_11998.xlsx | 5d2df5e7998a4ec903e12d51b25114e8f1ff36da57cecaf623e90398b0828f35 |
| DATOSDEALUMNOS_10246.xlsx / Hoja1 | /Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/DATOSDEALUMNOS_10246.xlsx | b175d63bd9e3280c5757fb0d7292e45fb594d8f076e277f2e06bad2b15e9d869 |
| DATOSDEALUMNOS_12112.xlsx / Hoja1 | /Users/alexi/Desktop/Caracterizacion_2026-10-20_2027_P1_082504/01_ENTRADAS/DATOSDEALUMNOS_12112.xlsx | fdd47d99b934479f39d8db6d00eceb40714d3b8c7baa1e3a89a9288b2b8bc471 |
| 2025-2.xlsx / Detalle1 / Hoja1 | /Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/2025/Matricula/SIES/2025-2.xlsx | 63a38e07b8b24d796cd2104abb1a63129f09b4b88e291c640f9e0f9e116fb78b |
| PROMEDIOSDEALUMNOS_2071.xlsx / Hoja1 | /Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/2025/Matricula/SIES/06-05-2025/PROMEDIOSDEALUMNOS_2071.xlsx | 348d1807381e545425c0f204c7321172a522718dec829dd9a60bf5dd07e45ef1 |
| Matrícula T_2_13_07_2026.xlsx / Hoja1 | /Users/alexi/Downloads/cierre/Matrícula T_2_13_07_2026.xlsx | 7926a9cabcc67ed19abb50459132fd74ebb323bff9f5cb53e9116378c21a6769 |
| Matrícula_T3_02_10_2026.xlsx / Base | /Users/alexi/Downloads/cierre/Matrícula_T3_02_10_2026.xlsx | de4e73ee7d27779cdc531c6816f745d412e1021cbd61e4fceb8ab0459cbda4ae |

La copia 12112 se localizó en el respaldo del Escritorio. Su SHA-256 coincide con el registrado para la antigua ruta de Downloads. Los hashes de todas las fuentes se comprobaron antes y después de leerlas. Los resultados completos y el QA están en RESULTADOS_AGREGADOS.json y MANIFEST_DIAGNOSTICO.json.
