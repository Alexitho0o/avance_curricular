# TVS_BLOQUES

## Rol del documento

`TVS_BLOQUES.md` es la lectura técnica sintética por bloque del proyecto `CARACTERIZACIÓN`.

No es documento rector. Queda subordinado a:
- [MAPA_MAESTRO_CARACTERIZACION.md](./MAPA_MAESTRO_CARACTERIZACION.md)
- [MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA.md](./MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA.md)

Su función es responder rápidamente:
- qué hace cada bloque
- qué consume
- qué produce
- qué riesgo tiene
- qué conviene leer antes de intervenirlo

## Cómo usar esta TVS

### Si la duda es estructural
Ir primero al mapa maestro.

### Si la duda es metodológica o de KPI
Ir primero al mapa KPI/gobernanza.

### Si la duda es técnica por bloque
Usar esta TVS.

## Convenciones de lectura

Cada bloque se resume con:
- propósito
- entradas dominantes
- outputs visibles
- llaves dominantes
- riesgos
- lectura previa recomendada

## Mapa rápido del pipeline

- `B0`: entorno, dependencias y utilidades
- `B1`: matrícula y universos base
- `B2`: LimeSurvey y clasificación de respuesta
- `B3`: Word
- `B4`: pendientes
- `B5`: comunicaciones
- `B6`: categorías especiales
- `B6.bis`: financiamiento/gratuidad derivado de B6
- `B7`: KPI académicos
- `B8`: análisis integral de encuesta
- `B9`: exportación del libro de encuesta
- `B10`: integración final encuesta
- `B10.x`: capa helper transversal compartida; no es bloque funcional autónomo
- `B10.bis`: longitudinal principal de pregrado
- `B10.ter`: posgrado/diplomados
- `B10.quater`: cruce SIES complementario
- `B11`: base analítica integrada absorbida en pregrado
- `B12`: dashboard absorbido en pregrado

## Nota de perímetro técnico

Las familias internas `B8.*`, `B9.*`, `B11.*` y `B12.*` existen realmente en el código como subfases comentadas y estructuradas. Esta TVS no las eleva una por una al mismo nivel que los bloques macro porque la gobernanza suficiente se fija en el bloque principal, sus contratos y sus outputs visibles.

## TVS por bloque

### B0 · Entorno, dependencias y utilidades
- propósito: preparar helpers de lectura, normalización, validación y exportación
- entradas dominantes: variables de entorno, sistema de archivos, dependencias Python
- outputs visibles: `exportar_excel`, `exportar_excel_rico`, validadores y normalizadores
- llaves dominantes: no aplica como nivel analítico de negocio
- riesgo: muy alto, impacto sistémico
- leer antes: mapa maestro + contratos

### B1 · Matrícula y universos base
- propósito: construir vigentes, eliminados, históricos, titulados, conflictos y universos de trabajo
- entradas dominantes: `DATOSDEALUMNOS_*`, `ANIO_ANALISIS`, `PERIODO_ANALISIS`
- outputs visibles: universos operativos, KPI base, conflictos, vigentes y eliminados exportados
- llaves dominantes: `RUT`, `RUT_NORMALIZADO`, `CODCLI`, `REGISTRO`
- riesgo: muy alto
- leer antes: mapa maestro + contratos + guía

### B2 · LimeSurvey
- propósito: cargar inscritos y resultados, clasificar `SI / INCOMPLETO / NO`
- entradas dominantes: tokens y resultados de encuesta
- outputs visibles: `df_inscritos`, `df_resultados`, estados de respuesta
- llaves dominantes: `TOKEN`, `RUT_NORMALIZADO`
- riesgo: alto
- leer antes: mapa maestro + contratos

### B3 · Informe Word
- propósito: producir el informe operativo con categorías, vigentes, eliminados y conflictos
- entradas dominantes: universos de `B1` y respuesta de `B2`
- outputs visibles: `Informe_Categorias_*.docx`
- llaves dominantes: `REGISTRO`
- riesgo: medio
- leer antes: TVS + guía

### B4 · Pendientes
- propósito: base operativa de no respuesta
- entradas dominantes: vigentes y estado de respuesta
- outputs visibles: `Estudiantes_pendientes_*.xlsx`
- llaves dominantes: `RUT`, `TOKEN`, `REGISTRO`
- riesgo: medio
- leer antes: TVS + guía

### B5 · Comunicaciones
- propósito: construir bases de contacto general y por sede, incorporando enriquecimiento operativo de situación laboral cuando la fuente LimeSurvey lo permite
- entradas dominantes: vigentes, respuestas y cruce operativo con resultados
- outputs visibles: `BD_Comunicaciones*.xlsx`
- llaves dominantes: `RUT`, `REGISTRO`
- riesgo: alto por uso operativo
- leer antes: contratos + guía

### B6 · Categorías especiales
- propósito: construir la lista maestra de categorías especiales para vigentes
- entradas dominantes: respuestas vigentes y reglas de categorías
- outputs visibles: `Lista_tokens_categorias_SI_*.xlsx`
- llaves dominantes: `TOKEN`, `RUT`, `REGISTRO`
- riesgo: medio
- leer antes: guía + contratos

### B6.bis · Financiamiento / gratuidad
- propósito: materializar la salida específica de financiamiento/gratuidad desde la base maestra ya consolidada por `B6`
- entradas dominantes: `df_categorias_si_vig`
- outputs visibles: `financiamiento_*.xlsx`
- llaves dominantes: `TOKEN`, `RUT`, `REGISTRO`
- riesgo: medio
- leer antes: contratos + guía

### B7 · KPI académicos
- propósito: construir el libro operativo de KPI e histórico académico
- entradas dominantes: matrícula, históricos y cohortes de comparación
- outputs visibles: `KPI_ACADEMICOS_*.xlsx`
- llaves dominantes: mezcla de `REGISTRO`, `CODCLI`, cohortes agregadas
- riesgo: alto
- leer antes: mapa KPI/gobernanza + guía

### B8 · Análisis integral de encuesta
- propósito: analizar el instrumento LimeSurvey en memoria
- entradas dominantes: resultados de encuesta
- outputs visibles: catálogos, resumen binario, temporalidad, categorías, KPI laborales
- llaves dominantes: `TOKEN`, `REGISTRO`
- riesgo: alto
- leer antes: mapa maestro + mapa KPI/gobernanza
- nota de implementación: el código contiene subfases internas `B8.*`; no se elevan aquí como bloques rectores independientes

### B9 · Exportación del libro de encuesta
- propósito: materializar el resultado de `B8` en `ENCUESTA_CARACTERIZACION`
- entradas dominantes: payload de `B8`
- outputs visibles: libro de encuesta final
- llaves dominantes: `TOKEN`, `REGISTRO`
- riesgo: alto
- leer antes: contratos + guía
- nota de implementación: el código contiene subfases internas `B9.*`; no se elevan aquí como bloques rectores independientes

### B10 · Integración final encuesta
- propósito: orquestar `B8` + `B9` y publicar `ENCUESTA_CARACTERIZACION_*.xlsx`
- entradas dominantes: contexto de `B8`, ruta de salida y wrapper general
- outputs visibles: libro final de encuesta
- llaves dominantes: hereda frente encuesta
- riesgo: medio
- leer antes: manifest + contratos

### B10.bis · Longitudinal principal de pregrado
- propósito: construir la trayectoria maestra de pregrado y sus vistas complementarias
- entradas dominantes: histórico de matrícula y, cuando aplica, encuesta y promedios
- outputs visibles: `PREGRADO_TRAYECTORIA_CARACTERIZACION_*.xlsx`
- llaves dominantes: `CODCLI`, `CODCLI_PERIODO`, `RUT`
- riesgo: muy alto
- leer antes: mapa maestro + mapa KPI/gobernanza + contratos + guía

### B10.ter · Posgrado / diplomados
- propósito: construir el libro analítico separado de posgrado
- entradas dominantes: histórico filtrado de diplomados/posgrado
- outputs visibles: `POSGRADO_DIPLOMADOS_*.xlsx`
- llaves dominantes: `RUT`, `CODCLI`, `CODCLI_PERIODO`
- riesgo: alto
- leer antes: mapa maestro + mapa KPI/gobernanza + guía

### B10.quater · Cruce SIES complementario
- propósito: cruzar el reporte SIES filtrado institucionalmente con las bases históricas internas de pregrado y diplomados, usando SIES como universo base
- entradas dominantes: reporte SIES filtrado, `CRUCE_SIES_BASE_HIST_PREGRADO`, `CRUCE_SIES_BASE_HIST_DIPLOMADOS`
- outputs visibles: `CRUCE_SIES_*.xlsx`
- llaves dominantes: `REGISTRO`, `RUT`, `CODCLI`
- riesgo: alto por dependencia interproyecto y validación externa
- leer antes: mapa maestro + contratos + guía

### B11 · Base analítica integrada absorbida en pregrado
- propósito: integrar matrícula, encuesta y rendimiento al libro de pregrado
- entradas dominantes: vigentes, respuesta, rendimiento y ruta del libro final de pregrado
- outputs visibles: hojas absorbidas de integración y `CTX_B11_B12`
- llaves dominantes: `CODCLI`, `TOKEN`, segmentos agregados
- riesgo: alto
- leer antes: manifest + contratos + guía
- nota de implementación: el código contiene subfases internas `B11.*`; no se elevan aquí como bloques rectores independientes

### B12 · Dashboard absorbido en pregrado
- propósito: anexar el dashboard gráfico del frente integrado al libro final de pregrado
- entradas dominantes: `CTX_B11_B12`, ruta del libro final
- outputs visibles: hojas gráficas absorbidas
- llaves dominantes: agregados ejecutivos
- riesgo: alto
- leer antes: manifest + contratos + guía
- nota de implementación: el código contiene subfases internas `B12.*`; no se elevan aquí como bloques rectores independientes

## Qué documento leer antes de intervenir cada frente

| Frente | Documento rector | Documento técnico |
|---|---|---|
| entradas / layout | mapa maestro | contratos |
| llaves / KPI / naming | mapa KPI/gobernanza | guía |
| encuesta | mapa maestro | TVS + guía |
| pregrado | mapa maestro + mapa KPI/gobernanza | contratos + guía |
| posgrado | mapa maestro + mapa KPI/gobernanza | TVS + guía |
| cruce SIES complementario | mapa maestro + contratos | TVS + guía |
| consolidación final | mapa maestro | manifest + contratos |

## Qué esta TVS no debe duplicar

No debe duplicar:
- la explicación completa de llaves y niveles del mapa KPI/gobernanza
- el layout maestro como si fuera contrato detallado
- el checklist operativo completo de la guía
- la lista exhaustiva de invariantes que ya vive en contratos
