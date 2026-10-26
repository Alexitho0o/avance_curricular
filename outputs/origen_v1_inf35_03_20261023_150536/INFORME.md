# Origen de V1 — INF35-03

Proceso: seguimiento intertrimestral IPSS 162. Objetivo T3-2024, plan IINF20241; contraste con preparación MU2025. Repositorio avance_curricular, feature/ire-2026. Diagnóstico B/C/E; no nueva decisión D ni regla oficial A.

## Conclusión

**B/C.** La procedencia observable de V1 llega hasta `IPSS_Procesamiento.xlsx`, hoja `Precarga`, celda **Q1023**. Contiene el número **1**, sin fórmula, comentario ni hipervínculo de celda. No se localizó en los respaldos examinados la regla que asignó esa versión al expediente. El nombre «Precarga» no demuestra por sí solo quién generó ese dato ni una aceptación oficial.

**E.** No se puede confirmar que V1 correspondiera al plan en T3-2024. La observación sigue pendiente; no se la convirtió en V2 ni se declaró errónea la V1 enviada en 2025. Se distingue procedencia técnica localizable de causa o validez académica de la asignación.

## Cadena documental observada

| Contexto/fuente | Localizador | Dato | Clase |
|---|---|---|---|
| Respaldo Matrícula_Pregrado_2024.xlsx | Intake 1, fila 415; hoja de matrícula, fila 482 | J2V4, ingreso 2024; el respaldo conserva matrícula anual | B |
| IPSS_Procesamiento.xlsx | Precarga, P1023/Q1023 | J1/V1, valores guardados; FECH_CAR=16-abr-2025 | B |
| Mismo libro | Carga_Completa, fila 1025; Carga_Completa (2)/(3), fila 1030 | J1V1 conservado | B |
| Mismo libro | Final a carga, fila 1003 | J1V1 conservado | B |
| IPSS2025.xlsx | Hoja1, fila 1003, N/O | J1/V1 | B |
| Descarga de lo cargado_08-05-2025_22-26-22_Matrícula_Pregrado_2025.xlsx | Hoja granular, fila 1018, P/Q | J1/V1; FECH_CAR=08-may-2025 | B |
| Código anual personal MU2026, índice gobernado | mu_anual, identidad exacta, año 2026 | J1V2 | B/C |

**C/E.** La coincidencia entre estas hojas reconstruye dónde se conserva el valor; no acredita el orden temporal exacto de cada edición ni que unas fueran copiadas directamente de otras. FECH_CAR, creación/modificación del XLSX y fecha de matrícula no se usan como fecha efectiva de cambio de plan.

## Qué aportaron los otros respaldos

**B.** Se inspeccionaron 17 libros de preparación MU2025: 32 filas relacionadas con la misma persona, repetidas entre hojas y libros. Los registros UMAS cotejados muestran IINF y jornada D, pero no incorporan una equivalencia que asigne V1 al plan IINF20241. `2025-2.xlsx`, Hoja1, fila 497, conserva el CODCLI del expediente: permite confirmar identidad/expediente, pero no contiene código SIES ni versión en esa fila.

**B.** La hoja `Mapa` de IPSS_Procesamiento relaciona Informática con el componente carrera **1** (filas 12 y 17). Ese 1 es COD_CAR; no es una regla VERSION=1. La columna de VERSION examinada no apunta a ese mapa. Los vínculos externos del libro apuntan a PROMEDIOS2071; no se encontró conexión, queryTable ni VBA en ese libro que genere la versión. La ausencia de esos objetos no descarta operaciones manuales o un generador externo no conservado.

**B/C.** Se revisaron además el XLSX de matrícula incremental denominado 02-01-2025 y su CSV de 820 filas (32 columnas, sin encabezados; orden contrastado con la hoja 1 del XLSX). La persona no aparece con RUT+DV exacto en ninguno. Esta ausencia no demuestra retiro ni resuelve T3. El CSV 2024 de la misma carpeta y el respaldo 2024 enlazado desde ese libro conservan J2V4.

**B/C.** Los registros de PROMEDIOS ya extraídos con el mismo CODCLI conservan el plan IINF20241 durante T3-2024 y en períodos 2025. Las exportaciones registran jornadas distintas sobre la misma historia académica; esas jornadas no se convierten en un historial administrativo retroactivo. La continuidad del código de plan no permite por sí sola fechar qué versión SIES se utilizó antes de la matrícula anual 2025.

## Contraste de oferta

**B.** El catálogo histórico gobernado contiene en 2024 y 2025 tanto J1V1 como J1V2, ambas presenciales, regulares y de ocho semestres. V1 figura «Vigente sin estudiantes nuevos» y V2 «Vigente con estudiantes nuevos». Fuente: maestro de oferta, hoja original `in`, filas 82339/82340 para 2024 y 54243/54244 para 2025; copia exacta en AMPLIACION.json.

**E.** Esas etiquetas no deciden por sí solas la asignación de una persona que cambió de jornada. No se interpreta «sin nuevos» como eliminación de estudiantes antiguos; tampoco como autorización para trasladar V1 a cualquier plan. No hay una regla leída que establezca IINF20241 + D = V1 para este contexto.

## Resultado y siguiente evidencia

**E.** Para resolver esta observación falta la asignación efectiva a J1V1/J1V2 durante T3-2024, o una equivalencia temporal interna expresamente aprobada para ese expediente y plan. La revisión acota la búsqueda: el dato V1 ya llega como literal a Precarga!Q1023; no nace del cálculo de retención, del cruce por RUT actual ni de la tabla Mapa. No se atribuye autoría a personas desde nombres de carpetas o metadatos.

**C.** QA: fuentes/Excel/base anual/diccionario v6 conservan sus hashes; identidad exacta; detalle privado fuera de Git; no se hacen adjudicaciones. Permanecen tres observaciones por jornada pendientes en el foco anterior, incluida INF35-03 T3-2024. Bases y denominadores intactos. Sin commit/push.
