# Arquitectura reutilizable de codigo_gobernanza_v2.py

## Contexto

- Proceso objetivo: Avance Curricular SIES 2026
- Repositorio: `/Users/alexi/Documents/GitHub/avance_curricular`
- Rama: `backup/pre-sync-fix-20260410-avance`
- Commit: `493bdf43b4f10af01e276d0f730a5fbef2ee94fb`
- Fuente: `/Users/alexi/Documents/GitHub/avance_curricular/codigo_gobernanza_v2.py`
- SHA-256: `40bfd42891e8eb593ebcfa8e3e480328c5174daa4d07526fe1b67f736de63023`
- Total de líneas: `5,313`
- Análisis anterior: `ANALISIS_DIRIGIDO_20260626_145436`

## Resultado

- Funciones totales: 93
- Funciones relevantes previas: 65
- Funciones con referencias fuertes: 46
- Funciones núcleo seleccionadas: 63

## Clasificación preliminar

{
  "TRANSVERSAL_CANDIDATA": 60,
  "REQUIERE_REVISION": 1,
  "ESPECIFICA_MATRICULA_UNIFICADA": 2
}

## Archivos principales

1. `01_FUNCIONES_NUCLEO.tsv`
   Índice de funciones seleccionadas, llamadas y clasificación preliminar.

2. `02_CUERPOS_FUNCIONES_NUCLEO.txt`
   Código completo solamente de las funciones núcleo.

3. `03_GRAFO_LLAMADAS.tsv`
   Relaciones entre funciones.

4. `04_REFERENCIAS_FLUJO_EXISTENTE.tsv`
   Referencias a PROMEDIOSDEALUMNOS, hojas, llaves, catálogos y salidas.

5. `05_SELECCION_PROCESO.tsv`
   Líneas relacionadas con selección de proceso.

6. `06_RESUMEN_ARQUITECTURA.json`
   Resumen técnico.

## Próxima decisión

No modificar todavía `codigo_gobernanza_v2.py`.

Revisar en este orden:

1. `05_SELECCION_PROCESO.tsv`
2. `04_REFERENCIAS_FLUJO_EXISTENTE.tsv`
3. `01_FUNCIONES_NUCLEO.tsv`
4. `02_CUERPOS_FUNCIONES_NUCLEO.txt`

El objetivo es determinar si Avance Curricular debe:

- agregarse como nuevo modo controlado en el monolito; o
- implementarse como adaptador externo que importe funciones existentes.

La elección debe basarse en el acoplamiento real observado, no en supuestos.
