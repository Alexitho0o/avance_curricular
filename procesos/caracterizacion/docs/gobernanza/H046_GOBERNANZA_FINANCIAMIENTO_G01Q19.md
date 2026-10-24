# H046 - Gobernanza de financiamiento G01Q19

## Proposito

Gobernar de forma unica la pregunta multiseleccion `G01Q19` en el informe
Word, la lista de categorias y el Excel independiente de financiamiento.

## Alternativas obligatorias

El instrumento debe contener exactamente:

1. `G01Q19[SQ002]` - Ingresos propios.
2. `G01Q19[SQ003]` - Ingresos de mi padre o madre.
3. `G01Q19[SQ004]` - Ingresos de otros familiares.
4. `G01Q19[SQ005]` - Ingresos de otras personas.
5. `G01Q19[SQ006]` - Gratuidad.
6. `G01Q19[SQ007]` - Otras becas del Estado.
7. `G01Q19[SQ008]` - Becas externas.
8. `G01Q19[SQ009]` - Credito con Aval del Estado (CAE).
9. `G01Q19[SQ010]` - Credito bancario o similares.
10. `G01Q19[SQ011]` - Mi empleador o empresa.
11. `G01Q19[SQ012]` - Beca institucional (IPSS).

`G01Q19Time` es un metadato de temporizacion y queda excluido.

## Unidad de conteo

La pregunta permite seleccionar mas de una alternativa. Por tanto:

```text
FILA_DETALLE = ESTUDIANTE + ALTERNATIVA_RESPONDIDA_SI
TOTAL_SELECCIONES = SUMA(FILAS_DETALLE)
ESTUDIANTES_UNICOS = NUNIQUE(RUT)
```

`TOTAL_SELECCIONES` puede ser mayor que `ESTUDIANTES_UNICOS`. No deben
presentarse ambos conceptos como equivalentes.

## Salidas gobernadas

- `Informe_Categorias_*.docx`: una fila por alternativa, mas total de
  selecciones.
- `Lista_tokens_categorias_SI_*.xlsx`: incorpora las respuestas afirmativas
  de las 11 alternativas dentro de la categoria `Financiamiento`.
- `financiamiento_*.xlsx`: detalle largo de estudiantes vigentes, con una
  fila por alternativa afirmativa.

## Controles bloqueantes

1. Deben detectarse las 11 alternativas antes de construir el Word y el Excel.
2. Una alternativa faltante o una nueva alternativa no gobernada detiene la
   ejecucion con el detalle de codigos.
3. Ningun codigo distinto de los 11 autorizados puede llegar al Excel.
4. La suma de filas agrupadas por codigo debe coincidir con las filas del
   Excel de financiamiento.
5. El terminal debe informar selecciones totales, estudiantes unicos y total
   por cada codigo, incluyendo ceros.

## Fuente de verdad

La lista y los textos viven en `caracterizacion_financiamiento.py`. No deben
crearse listas paralelas en los bloques Word o Excel.
