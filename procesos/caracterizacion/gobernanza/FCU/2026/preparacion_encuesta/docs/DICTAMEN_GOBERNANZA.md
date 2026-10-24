# Dictamen de gobernanza - FCU_ANALISIS_ENCUESTA

## Dictamen

**GOBERNANZA_COMPLETA_ANALISIS_ENCUESTA**

## Estado

COMPLETO

## Fundamento

Preguntas no FCU; uso interno; exclusión de KPIs oficiales FCU; relación con LimeSurvey/SEP_TODAS.

## Evidencias copiadas

| archivo |
| --- |
| AUDITORIA_PREGUNTAS_NO_FCU_ENCUESTA_2026.xlsx |
| Manual_de_Aplicacion_FCU_2026.txt |

## Acción recomendada

Mantener preguntas no FCU y sustentabilidad como análisis interno, fuera de KPI oficial FCU.

## Riesgos

Uso indebido si se mezclan variables internas con KPI oficial.

## Versionamiento recomendado

Versionar en Git los documentos, TSV, JSON, hashes y dictámenes. Respaldar en nube las evidencias pesadas o sensibles cuando la política documental lo requiera.

FASE 5 TERMINADA: SÍ.

---

## Addendum 2026-10-01 — Reapertura: derivado incorporado

**Archivo incorporado:** `Resumen_clasificacion_preguntas_FCU_2026.xlsx`
**SHA-256:** `803efdeec6e2668a4bd527e9e896d7bc69be0b02fb04381da76ca1c49e18ad3d`
**Origen:** `/Users/alexi/Desktop/Resumen_clasificacion_preguntas_FCU_2026.xlsx`

**Motivo de reapertura (D — decisión interna):** el archivo declara en su propia hoja `Resumen` que su base es "auditoría gobernada de preguntas no FCU y Manual de Aplicación FCU 2026", es decir, las dos evidencias que este paquete ya gobierna (`AUDITORIA_PREGUNTAS_NO_FCU_ENCUESTA_2026.xlsx` y `Manual_de_Aplicacion_FCU_2026.txt`). Se trata de un derivado del mismo proceso, no de un proceso nuevo, por lo que se incorpora aquí en lugar de abrir un paquete distinto.

**Contenido del derivado:** 5 hojas (`Resumen`, `Institucionales`, `Manual FCU`, `Criterio y fuentes`, `Opciones 2026`) con conteos de preguntas oficiales FCU 2026 (73 numeradas, 45 principales P1–P45, 28 subpreguntas con código decimal, 22 condicionadas, 6 componentes de domicilio P12.1–P12.6, 46 preguntas institucionales adicionales) y una sección de "Clasificación corregida" que excluye los consentimientos `G00Q91`–`G00Q94` del total institucional (son preguntas oficiales del Ministerio de Educación) y precisa que 21 de las 28 subpreguntas decimales se activan por una respuesta previa, más `P29` como condicionada sin código decimal.

**Clasificación de la afirmación:** las cifras anteriores son **C/E** (implementación técnica del propio archivo / hipótesis a conciliar), no **A** (definición de glosario) ni **B** confirmado por este asistente — no se ha cruzado fila por fila contra las dos evidencias base en esta sesión.

**Estado del dictamen:** se mantiene `GOBERNANZA_COMPLETA_ANALISIS_ENCUESTA` / `COMPLETO` para el alcance original (preguntas no FCU y sustentabilidad). La incorporación del derivado no cambia ese alcance; se registra como ampliación documental del mismo paquete.

**Pendiente:** conciliación cruzada de las cifras del derivado contra `AUDITORIA_PREGUNTAS_NO_FCU_ENCUESTA_2026.xlsx` y `Manual_de_Aplicacion_FCU_2026.txt` antes de usarlas como cifra oficial en cualquier reporte o BI.

---

## Addendum 2026-10-02 — Renombre de carpeta (convención año/periodo)

Esta carpeta se renombró de `FCU/2026/analisis_encuesta` a `FCU/2026/preparacion_encuesta` mediante `git mv` (historia preservada). Motivo: la clasificación del instrumento de encuesta (preguntas oficiales vs. institucionales, sustentabilidad) no está atada a un período numerado específico — aplica transversalmente a los análisis de los 3 períodos de 2026 — por lo que no corresponde nombrarla `1`, `2` o `3`.

**Nota de reclasificación:** el derivado `Resumen_clasificacion_preguntas_FCU_2026.xlsx`, incorporado aquí el 2026-10-01, se retira de este paquete en este mismo addendum porque corresponde al trabajo de actualización de la FCU 2027, no a la definición del instrumento 2026. Ver el addendum de reversión más abajo y `FCU/2027/preparacion` para su nueva ubicación.
