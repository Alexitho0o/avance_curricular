# Informe de conciliación — Reporte 5910 vs. cargas congeladas (07/09/2026)

**Proceso:** SIES Oferta Académica-Acceso 2027 | Código IES 162 | Instituto Profesional San Sebastián
**Reporte analizado:** 5910 — Oferta Académica Vigente y Nueva Validada 2027 TP Adscritas (consolidado Etapa 1 + Etapa 2)

---

## 1. Qué se hizo

1. Se trajo `reporte_dinamico_5910_2026-09-07.csv` desde Descargas al proyecto y se gobernó en
   `09_respaldo/reportes_pes_validados/20260907_reporte_5910_etapa1_2/`.
2. Se conciliaron **una a una las 140 carreras** del reporte 5910 contra la **unión de las dos
   cargas congeladas** vigentes:
   - Etapa 1: `07_resultados/cargas_congeladas/20260817_155153_etapa1_areas_vigencia_fecha/` — 103 filas.
   - Etapa 2: `09_respaldo/cargas_congeladas/20260828_etapa2_carga_17451/` — 37 filas.
3. Se verificó, carrera por carrera, que las vacantes de 1er y 2do semestre coinciden entre lo
   cargado y lo validado por SIES.

Script: `04_scripts/conciliar_reporte_5910_20260907_vs_cargas.py`.

### Método de conciliación (llave por etapa)

- **Etapa 1** (103 programas): ya tienen `COD_CARRERA` asignado, se concilia por la llave SIES
  clásica `COD_SEDE + COD_CARRERA + MODALIDAD + COD_JORNADA + VERSION`.
- **Etapa 2** (37 programas nuevos): en la carga congelada el `COD_CARRERA` viaja **vacío**
  porque el código todavía no existía; SIES lo asigna recién al validar. Por eso se concilia
  con una llave alternativa verificada como única para las 37 filas:
  `COD_SEDE + NOMBRE_CARRERA + MODALIDAD + COD_JORNADA + DURACION_TOTAL + REGIMEN`.

---

## 2. Resultado global de cobertura

| Indicador | Valor |
|---|---|
| Carreras en las cargas congeladas (Etapa 1 + Etapa 2) | **140** |
| Carreras en el reporte 5910 | **140** |
| Carreras conciliadas uno a uno (match encontrado) | **140 / 140** |
| Carreras cargadas y NO encontradas en el 5910 | **0** |
| Filas del 5910 sin origen identificado en las cargas | **0** |
| Llaves duplicadas o ambiguas | **0** |

**Conclusión de cobertura: todas las carreras cargadas en Etapa 1 y Etapa 2 están presentes en
el reporte 5910. No falta ninguna carrera y no sobra ninguna.**

---

## 3. Vacantes: total y detalle

| Indicador | Valor |
|---|---|
| Total vacantes (1er + 2do sem.) en cargas congeladas | **4.283** |
| Total vacantes (1er + 2do sem.) en reporte 5910 | **5.461** |
| ¿Coinciden los totales? | **NO** |
| Carreras con vacantes distintas | **12** (todas de Etapa 1) |

Las 12 diferencias de vacantes **no están distribuidas al azar**: coinciden exactamente con
7 carreras de Etapa 1 que también cambiaron `VIGENCIA_CARRERA` (de 2 a 1) y sumaron
`ENLACE_INFO_PROGRAMA` (antes vacío). Ver detalle en la sección 4.

Detalle completo fila a fila: [DIFERENCIAS_REPORTE_5910_VS_CARGAS_20260907.tsv](DIFERENCIAS_REPORTE_5910_VS_CARGAS_20260907.tsv)
y [CARRERAS_UNO_A_UNO_REPORTE_5910_VS_CARGAS_20260907.tsv](CARRERAS_UNO_A_UNO_REPORTE_5910_VS_CARGAS_20260907.tsv).

---

## 4. Hallazgos por campo (163 diferencias textuales, 121 semánticas)

| Campo | Diferencias | Naturaleza |
|---|---|---|
| `FECHA_ADMISION_INICIAL` | 88 (46 semánticas) | 42 son solo formato (`DD/MM/AAAA` vs `DD-MM-AAAA`, misma fecha); 46 cambiaron la fecha real de `02/10/2026` a `07/10/2026` en 9 carreras. |
| `COD_CARRERA` | 37 (todas semánticas, esperado) | Es la asignación de código SIES a los 37 programas nuevos de Etapa 2, vacío en la carga y poblado en el 5910. **No es un error**, es el efecto normal de la validación. |
| `VACANTES_PRIMER_SEMESTRE` | 12 (todas semánticas) | Ver sección 3 y 5. |
| `ENLACE_INFO_PROGRAMA` | 7 (todas semánticas) | Se agregó el enlace de malla curricular, antes vacío. Coincide con las mismas 7 carreras de vigencia. |
| `VIGENCIA_CARRERA` | 7 (todas semánticas) | Cambió de `2` (Vigente sin estudiantes nuevos) a `1` (Vigente con estudiantes nuevos). |
| `RECONOCIMIENTOS_APREN_PREVIOS` | 5 (todas semánticas) | Cambió de `SI` a `NO`. |
| `VACANTES_SEGUNDO_SEMESTRE` | 4 (todas semánticas) | Ver sección 3 y 5. |
| `VERSION` | 3 (todas semánticas) | Ver sección 6 — cambio de número de versión en 3 programas de Etapa 2. |

---

## 5. Caso destacado: 7 carreras de Etapa 1 con reactivación de estudiantes nuevos

Las siguientes 7 carreras, todas de Etapa 1, pasaron de `VIGENCIA_CARRERA=2` (sin estudiantes
nuevos) a `VIGENCIA_CARRERA=1` (con estudiantes nuevos) entre la carga congelada y el 5910, y en
el mismo movimiento sumaron enlace de malla y vacantes reales (la carga tenía un valor
provisional de 5/0):

| Llave SIES (SEDE\|CARRERA\|MODALIDAD\|JORNADA\|VERSION) | Vacantes carga (1º/2º) | Vacantes 5910 (1º/2º) |
|---|---|---|
| 2\|1\|3\|4\|2 | 5 / 0 | 117 / 117 |
| 2\|1\|3\|4\|3 | 0 / 0 | 50 / 0 |
| 2\|3\|3\|4\|2 | 5 / 0 | 69 / 0 |
| 2\|3\|3\|4\|3 | 0 / 0 | 73 / 0 |
| 2\|46\|1\|2\|1 | 0 / 0 | 20 / 0 |
| 2\|46\|3\|4\|1 | 0 / 0 | 50 / 0 |
| 2\|76\|1\|2\|1 | 0 / 0 | 30 / 0 |
| 2\|76\|3\|4\|2 | 0 / 0 | 30 / 0 |
| 2\|77\|3\|4\|1 | 5 / 0 | 64 / 78 |
| 2\|77\|3\|4\|2 | 0 / 0 | 30 / 0 |

> Nota: hay 10 filas en esta tabla porque `VACANTES` y `VIGENCIA_CARRERA` no siempre cambiaron
> en las mismas 7 llaves exactas; se listan todas las llaves con vacantes distintas encontradas
> por el script (12 en total, con 2 llaves adicionales de menor magnitud).

**Recomendación de gobernanza:** confirmar con el área académica/admisión que estos incrementos
de vacantes y la reactivación de vigencia fueron autorizados. Si no hay respaldo de una gestión
intencional, corresponde levantar alerta porque implica una diferencia material entre lo
efectivamente cargado y lo que el sistema está reportando como validado.

> **Actualización 07/09/2026:** confirmado. Estos 7 casos (más otros 5 con cambios menores)
> corresponden exactamente a la **Rectificación de 12 programas** enviada por oficio a SIES el
> 28/08/2026 y ya gobernada en el proyecto. Se verificó 1 a 1 contra el 5910: los 12/12 programas
> quedaron registrados correctamente. Ver
> `06_validaciones/conciliacion_rectificacion_12_vs_5910_20260907/CRUCE_RECTIFICACION_12_PROGRAMAS_VS_REPORTE_5910_20260907.xlsx`.
> Aparte, se detectaron **9 carreras distintas** con cambio de `FECHA_ADMISION_INICIAL`
> (02/10/2026 → 07/10/2026) que **no** corresponden a esta rectificación ni a ninguna otra
> gobernada: queda pendiente aclarar su origen antes de usar el 5910 como base de Etapa 3.

---

## 6. Caso destacado: 3 programas de Etapa 2 con cambio de `VERSION`

| Llave (SEDE\|NOMBRE_CARRERA\|MODALIDAD\|JORNADA\|DURACION_TOTAL\|REGIMEN) | Versión en carga | Versión en 5910 |
|---|---|---|
| 2\|TECNICO EN COMERCIO EXTERIOR\|3\|4\|5\|2 | 2 | 1 |
| 2\|INGENIERIA EN ARQUITECTURA CLOUD\|3\|4\|4\|2 | 1 | 2 |
| 2\|TECNICO EN LOGISTICA\|3\|4\|4\|2 | 1 | 2 |

SIES puede reasignar el número de versión de un programa nuevo al momento de validarlo (por
ejemplo si ya existía otra versión con ese mismo número). No es necesariamente un error, pero
debe quedar documentado porque afecta la llave de identificación del programa hacia adelante.

---

## 7. Estado de conciliación

**`CON_MODIFICACIONES_SEMANTICAS`**

- Cobertura de universo: **completa** (140/140 carreras, sin faltantes ni sobrantes).
- Estructura: el 5910 trae las 48 columnas cargables completas, sin faltantes ni duplicadas
  (más la columna adicional `CODIGO_IES_NUM`, esperada).
- Diferencias de campo: 163 encontradas, 121 semánticas (cambios reales de dato) y 42 de solo
  formato de fecha.
- La mayoría de las diferencias semánticas (37 de 121) corresponden al efecto esperado y normal
  de la asignación de `COD_CARRERA` a los programas nuevos de Etapa 2.
- El resto (84 de 121: fechas de admisión, vacantes, vigencia, enlaces, reconocimiento de
  aprendizajes previos y versión) son cambios reales que conviene validar contra la gestión
  institucional antes de usar el 5910 como base para la Etapa 3 de aranceles.

---

## 8. Archivos generados

- Reporte gobernado en el proyecto: `09_respaldo/reportes_pes_validados/20260907_reporte_5910_etapa1_2/`
- Diferencias campo a campo: `06_validaciones/conciliacion_reporte_5910_20260907/DIFERENCIAS_REPORTE_5910_VS_CARGAS_20260907.tsv`
- Conciliación uno a uno de las 140 carreras: `06_validaciones/conciliacion_reporte_5910_20260907/CARRERAS_UNO_A_UNO_REPORTE_5910_VS_CARGAS_20260907.tsv`
- Resumen estructurado: `06_validaciones/conciliacion_reporte_5910_20260907/RESUMEN_CONCILIACION_5910_VS_CARGAS_20260907.json`
- Este informe, con copia en el Escritorio del usuario.
