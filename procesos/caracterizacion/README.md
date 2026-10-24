# CARACTERIZACIÓN

## Propósito

`caracterizacion.py` es el pipeline central del proyecto. Integra matrícula, LimeSurvey, categorías especiales, KPI académicos, analítica longitudinal de pregrado, frente separado de posgrado/diplomados y un frente analítico complementario de cruce con SIES, además de los libros finales consolidados y las salidas operativas vigentes.

Este `README.md` ya no es solo una presentación general. Su función es ser la puerta de entrada práctica al proyecto y el nodo de navegación hacia la documentación rectora.

La [consulta histórica SIES–UMAS 2007–2026](./docs/gobernanza/CONSULTA_HISTORICA_SIES_UMAS.md)
comparte el maestro y resolvedor de avance_curricular mediante un paquete local
verificado. Conserva las equivalencias pendientes y dispone de API y comando
independientes; no reemplaza los procesos operativos anuales.

## Estado operativo actual del entrypoint

El entrypoint previsto del proyecto sigue siendo `run_caracterizacion_fijo.sh`.

Los comandos vigentes para financiamiento 2027 P1 y analisis completo 2026 P1/P2/P3 en Mac y Windows estan en [docs/gobernanza/COMANDOS_MAC_WINDOWS.md](./docs/gobernanza/COMANDOS_MAC_WINDOWS.md). El anual se invoca con `bash ./procesar_analisis_anual.sh 2026` y valida fuentes independientes para los tres periodos antes de ejecutarlos.

El libro anual incorpora seis paneles enlazados a sus tablas de calculo, sin retirar las salidas originales por periodo. Contrato de filtros, formatos, trazabilidad y entrega visible: [Dashboard anual 2026](./docs/gobernanza/DASHBOARD_ANUAL_2026.md).

Las reglas vigentes del reporte diario 2027 P1 y sus cambios estan en [AUDITORIA_CAMBIOS_SALIDAS_2027_P1.md](./docs/gobernanza/AUDITORIA_CAMBIOS_SALIDAS_2027_P1.md). Incluyen Acumulado/Hoy por fecha de envio, seguimiento VCM G02Q95/AO05, comunicaciones para tres sedes, destino de archivos y omision de detalles sin casos. La publicacion de este codigo no equivale a liberar la carga PES 2027; su mapeo integral sigue pendiente. Las bases, respuestas, participantes y QA individuales permanecen fuera de la publicacion.

Publicacion autorizada y verificada en GitHub el 2026-10-13: [manifiesto de publicacion](./docs/gobernanza/PUBLICACION_GITHUB_2027_P1_20261013.json). Identifica el commit del codigo, los hashes del paquete, las validaciones y lo que permanece fuera del cierre.

El bloqueo Mail_Inst de 2027 P1 del 2026-10-13 tiene causa de origen: un elegible sin correo institucional. Por autorizacion posterior, el correo ausente queda pendiente individual y ya no bloquea la ejecucion. Los CSV solo incluyen casos listos. Desde la decision posterior, el estado y Excel se conservan en05_ANALISIS, separados del Word de correo; el objetivo se acota a primer ingreso institucional tras revisar el historico completo. Politica vigente: [POLITICA_INCORPORACION_CORREO_2027_P1.md](./docs/gobernanza/POLITICA_INCORPORACION_CORREO_2027_P1.md). Evidencia y pruebas: [INCIDENTE_MAIL_INST_2027_P1_20261013.md](./docs/gobernanza/INCIDENTE_MAIL_INST_2027_P1_20261013.md).

Para generar el Excel de preguntas, subpreguntas y opciones desde exportaciones LSG/LSS, usar `scripts/exportar_instrumento_limesurvey.py`. Comandos para 2026, 2027 y 2028 y reglas de versionado: [docs/gobernanza/INVENTARIO_INSTRUMENTO_LIMESURVEY.md](./docs/gobernanza/INVENTARIO_INSTRUMENTO_LIMESURVEY.md).

Si `caracterizacion.py` presenta un error de sintaxis o no compila, el estado del sistema debe considerarse operativamente degradado. En ese caso:

- la arquitectura y la gobernanza documental siguen siendo válidas como referencia estructural;
- el README no debe leerse como garantía de ejecución exitosa del flujo completo;
- cualquier afirmación de operación no interactiva debe entenderse como objetivo del proyecto, no como certificación del estado actual, hasta que el script principal vuelva a compilar.

## Documentos rectores

### 1. Base estructural del sistema
- [MAPA_MAESTRO_CARACTERIZACION.md](./MAPA_MAESTRO_CARACTERIZACION.md)

Este documento manda cuando la pregunta es:
- qué hace el sistema en su estado real
- cuáles son sus entradas, salidas y bloques
- qué invariantes operativos ya no deben redescubrirse
- cuál es el layout conocido de matrícula
- qué libros finales siguen vigentes

### 2. Base de gobernanza KPI y niveles de análisis
- [MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA.md](./MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA.md)

Este documento manda cuando la pregunta es:
- qué significa realmente un KPI
- a qué nivel analítico trabaja una hoja
- cuándo usar `RUT`, `CODCLI`, `CODCLI_PERIODO` o `REGISTRO`
- cómo debe nombrarse una hoja o indicador
- cómo evitar ambigüedad metodológica

### 3. Auditoría de universo matrícula/encuesta
- [AUDITORIA_UNIVERSO.md](./AUDITORIA_UNIVERSO.md)

Este documento manda cuando la pregunta es:
- por qué cambia el universo entre matrícula, LimeSurvey y KPI
- qué filtros o merges eliminaron registros
- cómo rastrear los `CODCLI` de control
- qué parámetros activan exclusiones de diplomados, firma o año de ingreso

### 4. Gobernanza de pendientes LimeSurvey
- [docs/gobernanza/H045_GOBERNANZA_PENDIENTES_LIMESURVEY.md](./docs/gobernanza/H045_GOBERNANZA_PENDIENTES_LIMESURVEY.md)

Este documento manda cuando la pregunta es:
- qué diferencia el CSV acumulado del CSV diario;
- qué archivo debe cargarse a LimeSurvey;
- cómo se clasifican matrículas tardías y rezagados;
- por qué `ANOINGRESO` debe coincidir con el año analizado para autorizar la encuesta.

### 5. Gobernanza de financiamiento
- [docs/gobernanza/H046_GOBERNANZA_FINANCIAMIENTO_G01Q19.md](./docs/gobernanza/H046_GOBERNANZA_FINANCIAMIENTO_G01Q19.md)

Este documento gobierna las 11 alternativas multiselección de `G01Q19`, su
conteo en el Word y su detalle en `Lista_tokens_categorias_SI_*.xlsx` y
`financiamiento_*.xlsx`.

## Estado real vigente del sistema

## Integración AC desde PROMEDIOSDEALUMNOS

La integración AC está desactivada por defecto y se prueba de forma acotada con:

```bash
./run_ac_integracion_test.sh
```

Cuando se activa en modo seguro, genera columnas `_AC_` en `TRAYECTORIA_POR_PERIODO` y una hoja de auditoría llamada `AUDITORIA_AVANCE_CURRICULAR` dentro de `PREGRADO_TRAYECTORIA_CARACTERIZACION_*`.

Detalles técnicos, guardrails y checklist operativo: [docs/INTEGRACION_AVANCE_CURRICULAR_AC.md](./docs/INTEGRACION_AVANCE_CURRICULAR_AC.md).

### Libros analíticos finales
- `PREGRADO_TRAYECTORIA_CARACTERIZACION_*.xlsx`
- `POSGRADO_DIPLOMADOS_*.xlsx`
- `ENCUESTA_CARACTERIZACION_*.xlsx`

### Salidas operativas vigentes
- `Informe_Categorias_*.docx`
- `Estudiantes_pendientes_*.xlsx`
- `BD_Comunicaciones_*.xlsx`
- `BD_Comunicaciones_Santiago_*.xlsx`
- `BD_Comunicaciones_Concepcion_*.xlsx`
- `Lista_tokens_categorias_SI_*.xlsx`
- `financiamiento_*.xlsx`
- `KPI_ACADEMICOS_*.xlsx`
- `Conflictos_tokens_duplicados_vigentes_*.xlsx`
- `Estudiantes_matriculados_Periodo_*.xlsx`
- `Consolidado_eliminados_reporte_*.xlsx`

### Salida analítica complementaria real
- `CRUCE_SIES_*.xlsx`

### Regla de estado
El proyecto debe entenderse hoy como un sistema consolidado en tres libros analíticos finales. Los estados históricos intermedios del pipeline sirven como contexto, no como objetivo de reimplementación.

## Entradas principales

### Parámetros operativos
- `ANIO_ANALISIS`
- `PERIODO_ANALISIS`
- `VERBOSIDAD`
- cohorte opcional por `ANOINGRESO` para análisis generales; obligatoria e igual a
  `ANIO_ANALISIS` para cualquier incorporación a LimeSurvey, según H045

### Fuentes de datos
- `DATOSDEALUMNOS_*`
- `tokens_923565*`
- `results-survey923565*`
- `PROMEDIOSDEALUMNOS_*`

### Operación actual
- el wrapper `run_caracterizacion_fijo.sh` recibe año, período y verbosidad
- prioriza autodetección de fuentes desde `~/Downloads`
- evita selector manual cuando encuentra las rutas
- soporta operación no interactiva cuando `caracterizacion.py` compila correctamente
- imprime tiempo total al final

## Frentes funcionales del proyecto

### Operativo
Vigentes, eliminados, conflictos, pendientes, comunicaciones, categorías especiales, financiamiento, Word.

### Encuesta pura
Catálogo, resumen, respuestas, duplicados, temporalidad, categorías y participación laboral dentro de `ENCUESTA_CARACTERIZACION`.

### Pregrado longitudinal
Trayectoria principal gobernada por `CODCLI`, cohorte, continuidad complementaria por `RUT`, estados, rendimiento, base integrada y dashboard absorbido en `PREGRADO_TRAYECTORIA_CARACTERIZACION`.

### Posgrado / diplomados
Frente separado gobernado principalmente por `RUT`, con trazabilidad de `CODCLI`, dentro de `POSGRADO_DIPLOMADOS`.

### Cruce SIES complementario
Frente analítico complementario gobernado con SIES como universo base, trazabilidad por `RUT` y apoyo interno desde las bases históricas producidas por pregrado y diplomados.

## Arquitectura documental final

### Documento de entrada
- `README.md`: navegación general, estado actual y guía rápida de lectura.

### Documento rector estructural
- `MAPA_MAESTRO_CARACTERIZACION.md`: fuente oficial de verdad estructural del sistema, bloques, layout, entradas, salidas troncales y salidas complementarias reales.

### Documento rector metodológico
- `MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA.md`: niveles de análisis, gobernanza KPI, naming y reglas semánticas.

### Índice estructurado del sistema
- `MANIFEST_BLOQUES.yaml`: índice estructurado de bloques, outputs, dependencias, riesgos y documentos asociados.

### Lectura técnica por bloque
- `TVS_BLOQUES.md`: lectura técnica rápida de cada bloque y de su perímetro de intervención.

### Reglas duras
- `CONTRATOS_INVARIANTES.md`: layout, llaves, contratos entre bloques, invariantes y reglas no negociables.

### Manual de intervención
- `GUIA_INTERVENCION_SEGURA.md`: protocolo operativo para intervenir bloques, contratos y consolidación sin perder trazabilidad.

## Tabla de navegación documental

| Si quieres… | Lee primero | Complementa con |
|---|---|---|
| entender el proyecto completo | `MAPA_MAESTRO_CARACTERIZACION.md` | `README.md` |
| entender niveles de análisis y KPI | `MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA.md` | `CONTRATOS_INVARIANTES.md` |
| ubicar bloques, entradas y salidas | `MANIFEST_BLOQUES.yaml` | `TVS_BLOQUES.md` |
| intervenir un bloque específico | `TVS_BLOQUES.md` | `GUIA_INTERVENCION_SEGURA.md` |
| tocar llaves o granularidad | `MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA.md` | `CONTRATOS_INVARIANTES.md` |
| tocar layout de matrícula | `MAPA_MAESTRO_CARACTERIZACION.md` | `CONTRATOS_INVARIANTES.md` |
| tocar pregrado longitudinal | `MAPA_MAESTRO_CARACTERIZACION.md` | `TVS_BLOQUES.md`, `CONTRATOS_INVARIANTES.md`, `GUIA_INTERVENCION_SEGURA.md` |
| tocar posgrado | `MAPA_MAESTRO_CARACTERIZACION.md` | `TVS_BLOQUES.md`, `MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA.md` |
| tocar encuesta pura | `MAPA_MAESTRO_CARACTERIZACION.md` | `TVS_BLOQUES.md`, `GUIA_INTERVENCION_SEGURA.md` |
| tocar pendientes o carga LimeSurvey | `docs/gobernanza/H045_GOBERNANZA_PENDIENTES_LIMESURVEY.md` | `CONTRATOS_INVARIANTES.md`, `AUDITORIA_UNIVERSO.md` |
| tocar exportaciones, dashboards o consolidación | `MANIFEST_BLOQUES.yaml` | `CONTRATOS_INVARIANTES.md`, `GUIA_INTERVENCION_SEGURA.md` |
| tocar naming visible o KPI | `MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA.md` | `GUIA_INTERVENCION_SEGURA.md` |

## Tabla de mantenibilidad futura

| Tipo de cambio | Leer antes de tocar | Validar después |
|---|---|---|
| layout matrícula | mapa maestro + contratos | índices, universos, salidas operativas y analíticas |
| llaves analíticas | mapa KPI/gobernanza + contratos | niveles declarados, cruces, naming y KPI |
| categorías especiales | TVS + contratos | Word, listas y consistencia `B6 -> B6.bis` |
| financiamiento focalizado | mapa maestro + contratos + TVS | `financiamiento_*.xlsx` como derivado explícito de `B6.bis` |
| encuesta | mapa maestro + TVS + guía | `ENCUESTA_CARACTERIZACION` y contrato `B8 -> B9 -> B10` |
| longitudinal pregrado | mapa maestro + TVS + contratos + guía | cohorte, continuidad, estados, dashboard y consolidación |
| posgrado | mapa maestro + TVS + mapa KPI | libro posgrado, niveles y trazabilidad de `CODCLI` |
| cruce SIES complementario | mapa maestro + contratos + TVS + guía | `CRUCE_SIES_*`, universo base SIES y dependencia `B10.bis + B10.ter -> B10.quater` |
| KPI o naming | mapa KPI/gobernanza + guía | consistencia cruzada por nivel analítico |
| dashboard | manifest + guía | ubicaciones, títulos, gráficos y no regresión |
| consolidación final | mapa maestro + manifest + contratos | tres libros finales troncales y salidas complementarias correctamente clasificadas |

## Tabla de frentes / documentos rectores y técnicos

| Frente | Documento rector | Documento técnico |
|---|---|---|
| entradas / layout | mapa maestro | contratos |
| llaves / KPI / naming | mapa KPI/gobernanza | guía |
| encuesta | mapa maestro | TVS + guía |
| pregrado | mapa maestro + mapa KPI/gobernanza | contratos + guía |
| posgrado | mapa maestro + mapa KPI/gobernanza | TVS + guía |
| cruce SIES complementario | mapa maestro + contratos | TVS + guía |
| consolidación final | mapa maestro | manifest + contratos |

## Gobernanza mínima de niveles analíticos

- `RUT`: identidad de persona
- `CODCLI`: trayectoria académica específica
- `CODCLI_PERIODO`: trayectoria observada en un año/período
- `REGISTRO`: fila operativa no consolidada

La definición formal y las reglas de uso viven en `MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA.md`. El `README` solo actúa como recordatorio de entrada.

## Qué no debe volver a pasar

- releer todo `caracterizacion.py` antes de cualquier cambio
- reconstruir desde cero el layout de matrícula
- volver a discutir el estado real del sistema como si los libros finales no estuvieran consolidados
- mezclar `RUT` y `CODCLI` sin declarar nivel de análisis
- duplicar gobernanza KPI en todos los documentos

## Uso recomendado de esta arquitectura documental

1. partir por este `README`
2. ir al mapa maestro estructural
3. validar nivel analítico en el mapa KPI/gobernanza
4. recién después bajar al manifest, TVS, contratos o guía según el cambio concreto

## Estructura operativa de raíz

- La raíz del proyecto conserva solo entrypoints y documentos de gobernanza.
- `backups/` agrupa respaldos históricos del script principal y no forma parte del flujo vigente.
- `diagnosticos/` agrupa utilidades de revisión puntual y no debe confundirse con entrypoints del pipeline.
- `docs/` concentra documentación auxiliar no rectora.
- `cuarentena_revision_manual/` contiene artefactos dudosos o vacíos pendientes de confirmación manual; no deben tratarse como bloques funcionales ni como parte del flujo activo.
- `archive/` conserva artefactos históricos.

## Exploración visual interna con PyGWalker

- PyGWalker se integra como herramienta interna para analistas técnicos.
- No reemplaza el Excel final institucional ni modifica reportes existentes.
- Permite explorar visualmente hojas tabulares del Excel detectado y generar respaldo HTML/reporte técnico de exploración.
- Ejecución desde terminal:
	- `cd "/Users/alexi/Documents/GitHub/CARACTERIZACIÓN"`
	- `python explorador_pygwalker.py`
- Carpeta de salida de exploración: `outputs/pygwalker/`.
- La apertura interactiva depende de entorno compatible (notebook/VS Code interactive); no se activa automáticamente en flujo productivo.
