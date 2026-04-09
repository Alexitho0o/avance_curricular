# Flujo real de codigo_gobernanza_v2.py

- Rama: `backup/pre-sync-fix-20260410-avance`
- Commit: `6d1c71ff8fcc63a3b9bdd20ff65ca884095ab535`
- Fuente: `/Users/alexi/Documents/GitHub/avance_curricular/codigo_gobernanza_v2.py`
- SHA-256: `40bfd42891e8eb593ebcfa8e3e480328c5174daa4d07526fe1b67f736de63023`
- Líneas: `5,313`
- Funciones totales: `93`
- Funciones semilla exactas: `47`
- Funciones de entrada: `2`
- Funciones seleccionadas para el flujo real: `81`

## Criterio

La selección utiliza solamente:

- referencias exactas a las fuentes y hojas conocidas;
- funciones de entrada;
- ancestros reales en el grafo de llamadas;
- dependencias directas de las funciones semilla.

No utiliza términos generales como `archivo`, `salida`, `código` o `proceso`.

## Revisión

Abrir primero:

1. `01_FLUJO_REAL_FUNCIONES.tsv`
2. `04_GRAFO_FLUJO_REAL.tsv`
3. `02_CODIGO_FLUJO_REAL.txt`

El objetivo es identificar el bloque ya funcional que debe reutilizar Avance Curricular,
sin copiar ni reescribir el monolito completo.
