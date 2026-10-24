# MAPA_MAESTRO_CARACTERIZACION

## Rol rector

Este documento es la referencia estructural principal del proyecto `CARACTERIZACIÓN`.

Su función es fijar el estado real del sistema, su arquitectura por bloques, las entradas y salidas vigentes, las llaves analíticas conocidas y los invariantes operativos que no deben redescubrirse en cada sesión.

No reemplaza la documentación especializada. La ordena.

## Estado real vigente del sistema

El estado rector actual del proyecto es el estado consolidado del pipeline, no el estado histórico intermedio.

### Libros analíticos finales vigentes
- `PREGRADO_TRAYECTORIA_CARACTERIZACION_*.xlsx`
- `POSGRADO_DIPLOMADOS_*.xlsx`
- `ENCUESTA_CARACTERIZACION_*.xlsx`

### Salidas operativas que siguen vigentes
- `Informe_Categorias_*.docx`
- `Estudiantes_pendientes_*.xlsx`
- `BD_Comunicaciones_*.xlsx`
- `BD_Comunicaciones_Santiago_*.xlsx`
- `BD_Comunicaciones_Concepcion_*.xlsx`
- `Lista_tokens_categorias_SI_*.xlsx`
- `financiamiento_*.xlsx` (`BLOQUE 6.bis`, derivado explícito de `BLOQUE 6`)
- `KPI_ACADEMICOS_*.xlsx`
- `Conflictos_tokens_duplicados_vigentes_*.xlsx`
- `Estudiantes_matriculados_Periodo_*.xlsx`
- `Consolidado_eliminados_reporte_*.xlsx`

### Salidas analíticas complementarias reales
- `CRUCE_SIES_*.xlsx`

`CRUCE_SIES_*.xlsx` debe tratarse como salida analítica complementaria real del sistema. No forma parte del set de tres libros analíticos finales troncales, pero sí debe quedar gobernado estructuralmente y contractualmente porque existe en el flujo implementado.

### Regla crítica de estado
El sistema ya no debe tratarse como un proyecto que exporta `ANALITICA_AVANZADA_*.xlsx` y `DASHBOARD_ANALITICA_AVANZADA_*.xlsx` como libros finales separados. Ese estado quedó absorbido dentro del libro final de pregrado.

## Entradas principales del sistema

### Parámetros operativos
- `ANIO_ANALISIS`
- `PERIODO_ANALISIS`
- `VERBOSIDAD`
- cohorte opcional por `ANOINGRESO`

### Fuentes principales
- matrícula oficial `DATOSDEALUMNOS_*`
- tokens LimeSurvey `tokens_923565*`
- resultados LimeSurvey `results-survey923565*`
- promedios académicos `PROMEDIOSDEALUMNOS_*` cuando existen

### Comportamiento operativo consolidado
- el wrapper `run_caracterizacion_fijo.sh` resuelve año, período y verbosidad
- el wrapper prioriza autodetección desde `~/Downloads`
- el flujo principal ya soporta operación no interactiva
- el tiempo total de ejecución se reporta al final

### Estado operativo actual del entrypoint

El wrapper `run_caracterizacion_fijo.sh` sigue siendo el entrypoint operativo previsto del proyecto.

Sin embargo, si `caracterizacion.py` presenta un error de sintaxis o no compila, el estado del sistema debe considerarse operativamente degradado. En ese caso:

- la arquitectura declarada en este mapa sigue siendo la referencia estructural válida;
- la documentación no debe presentar el flujo como plenamente operativo;
- cualquier afirmación de ejecución no interactiva debe entenderse como objetivo del proyecto, no como garantía del estado actual.

Mientras persista un error activo de compilación del script principal, este documento fija la estructura real implementada, pero no debe leerse como certificación de operatividad completa.

## Layout fijo conocido de matrícula

El archivo de matrícula mantiene dependencia posicional. Este layout ya no debe redescubrirse.

| Índice | Campo |
|---:|---|
| 1 | `CODCLI` |
| 2 | `CODCARPR` |
| 3 | `NOMBRE_L` |
| 4 | `ANOMATRICULA` |
| 5 | `PERIODOMATRICULA` |
| 6 | `ANOINGRESO` |
| 7 | `PERIODOINGRESO` |
| 8 | `FECHAMATRICULA` |
| 9 | `JORNADA` |
| 10 | `RUT` |
| 11 | `NOMBRE` |
| 12 | `SEXO` |
| 22 | `FONOACTUAL` |
| 23 | `MAIL` |
| 24 | `Mail_Inst` |
| 56 | `ESTADOACADEMICO` |
| 57 | `SITUACION` |
| 59 | `NIVEL` |
| 61 | `CON_FIRMA` |
| 63 | `SEDE` |

## Arquitectura funcional por bloques

### `BLOQUE 0`
Infraestructura común: entorno, lectura, normalización, validación de archivos y exportación Excel.

### `BLOQUE 1`
Construcción del universo base de matrícula, vigentes, eliminados, históricos, titulados y conflictos.

### `BLOQUE 2`
Carga de LimeSurvey, clasificación `SI / INCOMPLETO / NO` y preparación del frente encuesta.

### `BLOQUE 3`
Informe Word y articulación de categorías especiales.

### `BLOQUE 4`
Pendientes operativos.

### `BLOQUE 5`
Bases de comunicaciones, incluyendo enriquecimiento operativo de contactabilidad y situación laboral cuando la información está disponible en el flujo.

### `BLOQUE 6`
Lista maestra de categorías especiales para vigentes.

### `BLOQUE 6.bis`
Salida focalizada de financiamiento/gratuidad derivada explícitamente de `BLOQUE 6`. No recalcula categorías: filtra y materializa el subconjunto de financiamiento desde la base ya consolidada de categorías especiales.

### `BLOQUE 7`
KPI académicos operativos e históricos.

### `BLOQUE 8`
Análisis integral del instrumento LimeSurvey.

### `BLOQUE 9`
Exportación enriquecida del libro de encuesta.

### `BLOQUE 10`
Orquestación final del frente encuesta.

### `BLOQUE 10.x`
Capa helper transversal compartida por `BLOQUE 10.bis`, `BLOQUE 10.ter`, `BLOQUE 10.quater`, `BLOQUE 11` y `BLOQUE 12`.

No se gobierna como bloque funcional autónomo. Se declara únicamente como dependencia técnica compartida porque concentra normalización de estados, integración de promedios, blindaje de columnas sensibles en Excel y postprocesamiento visual de salidas.

### `BLOQUE 10.bis`
Frente longitudinal maestro de pregrado.

### `BLOQUE 10.ter`
Frente separado de posgrado y diplomados.

### `BLOQUE 10.quater`
Cruce analítico complementario con SIES. Usa como universo base el reporte SIES filtrado institucionalmente y lo enriquece con las bases históricas internas producidas por `BLOQUE 10.bis` y `BLOQUE 10.ter`.

### `BLOQUE 11`
Base analítica integrada matrícula + encuesta + rendimiento absorbida en pregrado.

### `BLOQUE 12`
Dashboard gráfico absorbido en pregrado.

## Nota de granularidad

Las familias internas `B8.*`, `B9.*`, `B11.*` y `B12.*` existen realmente en el código como subfases comentadas y estructuradas. No se elevan aquí una por una al mismo nivel que los bloques macro porque su gobernanza suficiente se resuelve a nivel de bloque principal, contrato interbloque y documentación técnica de lectura rápida.

## Llaves analíticas conocidas

La definición formal de niveles vive en `MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA.md`. Este mapa maestro solo fija el inventario y la separación práctica.

- `TOKEN`: inscripción y respuesta de encuesta
- `RUT`: identidad transversal de persona
- `RUT_NORMALIZADO`: llave controlada de cruce
- `CODCLI`: trayectoria académica principal
- `CODCLI_PERIODO`: trayectoria observada en un año/período específico
- `REGISTRO`: fila operativa no consolidada

## Invariantes operativos que no deben redescubrirse

- pregrado longitudinal principal gobernado por `CODCLI`
- continuidad y transiciones personales relevantes gobernadas por `RUT`, con trazabilidad de `CODCLI`
- posgrado/diplomados gobernado por `RUT`, con trazabilidad de `CODCLI`
- encuesta pura separada del frente longitudinal
- diplomados excluidos del libro principal de pregrado
- `BLOQUE 6.bis` depende explícitamente de `BLOQUE 6` y materializa `financiamiento_*.xlsx` sin recalcular la base de categorías
- `BLOQUE 10.quater` depende explícitamente de `BLOQUE 10.bis` y `BLOQUE 10.ter`
- `BLOQUE 10.quater` usa SIES como universo base y las bases internas solo como enriquecimiento y contraste
- `CRUCE_SIES_*.xlsx` es salida analítica complementaria real, no uno de los tres libros finales troncales
- `BLOQUE 10.x` existe como dependencia técnica compartida y no debe reinterpretarse como frente funcional autónomo
- tratamiento de cohorte ya corregido
- tratamiento de titulados en cohorte ya corregido
- `NIVEL_COHORTE` y `NIVEL_DESTINO` ya incorporados en pregrado
- columnas sensibles de Excel ya blindadas como texto cuando corresponde

## Qué documento manda para cada pregunta

- estructura general del sistema: este documento
- gobernanza KPI, niveles y naming metodológico: `MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA.md`
- navegación general del proyecto: `README.md`
- índice estructurado por bloque: `MANIFEST_BLOQUES.yaml`
- lectura técnica por bloque: `TVS_BLOQUES.md`
- reglas duras e invariantes: `CONTRATOS_INVARIANTES.md`
- guía de cambio seguro: `GUIA_INTERVENCION_SEGURA.md`

## Qué no debe duplicarse

No corresponde volver a repartir en todos los documentos:
- el layout completo de matrícula como si fuera un descubrimiento nuevo
- la lista de libros finales como si siguiera abierta
- la discusión sobre `RUT` versus `CODCLI` sin remitir al mapa KPI/gobernanza
- el estado histórico intermedio del proyecto como si siguiera vigente

## Criterio de uso futuro

Antes de tocar código o documentación:
1. partir por este mapa maestro
2. verificar el nivel analítico en el mapa KPI/gobernanza
3. recién después bajar al manifest, TVS, contratos o guía según el tipo de cambio
