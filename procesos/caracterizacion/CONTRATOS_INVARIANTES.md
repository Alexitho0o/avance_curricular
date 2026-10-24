# CONTRATOS_INVARIANTES

## Rol del documento

`CONTRATOS_INVARIANTES.md` es la capa dura del proyecto `CARACTERIZACIÓN`.

No es documento rector primario. Queda subordinado a:
- [MAPA_MAESTRO_CARACTERIZACION.md](./MAPA_MAESTRO_CARACTERIZACION.md)
- [MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA.md](./MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA.md)

Su función es fijar las reglas que no deben romperse aunque cambie la implementación.

## Qué tipo de contratos vive aquí

- contratos de entrada
- contratos de salida
- contratos de forma
- contratos entre bloques
- invariantes operativos
- invariantes metodológicos no negociables

## Invariantes globales

### Salidas finales
- los libros analíticos finales son tres y solo tres:
  - `PREGRADO_TRAYECTORIA_CARACTERIZACION_*.xlsx`
  - `POSGRADO_DIPLOMADOS_*.xlsx`
  - `ENCUESTA_CARACTERIZACION_*.xlsx`

### Salida analítica complementaria controlada

Además de los tres libros analíticos finales troncales, el sistema reconoce una salida analítica complementaria real:

- `CRUCE_SIES_*.xlsx`

Regla dura:

- `CRUCE_SIES_*.xlsx` debe quedar gobernado estructuralmente y contractualmente;
- `CRUCE_SIES_*.xlsx` no debe reinterpretarse como cuarto libro final troncal;
- la existencia de esta salida no modifica la regla de que los tres libros analíticos finales vigentes siguen siendo:
  - `PREGRADO_TRAYECTORIA_CARACTERIZACION_*.xlsx`
  - `POSGRADO_DIPLOMADOS_*.xlsx`
  - `ENCUESTA_CARACTERIZACION_*.xlsx`

### Separación metodológica
- encuesta pura separada de pregrado longitudinal
- pregrado longitudinal principal gobernado por `CODCLI`
- continuidad personal y transiciones relevantes gobernadas por `RUT`
- posgrado/diplomados separado del frente principal de pregrado
- diplomados excluidos del libro longitudinal principal de pregrado

### Gobernanza de niveles
La definición formal vive en el mapa KPI/gobernanza, pero aquí se vuelve regla dura:
- `RUT` no sustituye a `CODCLI`
- `CODCLI` no sustituye a `RUT`
- `CODCLI_PERIODO` no debe documentarse como si fuera `REGISTRO`
- `REGISTRO` no debe interpretarse como persona o trayectoria consolidada

### Excel y campos sensibles
- `RUT`, `RUT_NORMALIZADO`, `CODCLI`, `ANIO`, `ANOINGRESO`, `ORDEN_TEMPORAL` y campos equivalentes sensibles deben seguir protegidos para exportación Excel

## Contratos estructurales críticos

### Layout de matrícula
- el layout posicional conocido del archivo de matrícula es contrato duro
- cualquier cambio en índices debe actualizar validación y consumidores posteriores
- `NIVEL` en `BH` es parte del contrato vigente

### Normalización de llaves
- `_token_norm` y `token_match_rut` sostienen el cruce encuesta ↔ matrícula
- `rut_original` y `RUT_NORMALIZADO` deben seguir coexistiendo con roles distintos
- no introducir una segunda cadena de normalización paralela

### Contrato de incorporación a LimeSurvey

La especificación detallada vive en
[H045_GOBERNANZA_PENDIENTES_LIMESURVEY.md](./docs/gobernanza/H045_GOBERNANZA_PENDIENTES_LIMESURVEY.md).

Reglas duras:

- la población objetivo exige `ANOINGRESO == ANIO_ANALISIS`;
- el acumulado se define como población objetivo vigente del período sin token LimeSurvey;
- el CSV acumulado es la fuente autorizada para cargar la totalidad de pendientes;
- el CSV diario es una vista del acumulado filtrada exclusivamente por `FECHAMATRICULA` y ventana hábil;
- los años de ingreso distintos no se encuestan y deben quedar en una auditoría separada de no objetivo;
- todo pendiente de la población objetivo anterior a la ventana debe quedar clasificado como rezagado;
- diario, rezagados y otros fuera de ventana deben reconciliar exactamente con el acumulado;
- el período 1, 2 o 3 es dinámico y se gobierna con `PERIODOMATRICULA == PERIODO_ANALISIS`;
- cualquier cambio de estas reglas exige actualizar la función compartida, las pruebas y H045 en el mismo cambio.

### Contrato `B6 -> B6.bis`

`B6` construye la base maestra de categorías especiales vigentes y produce:

- `df_categorias_si_vig`
- `Lista_tokens_categorias_SI_*.xlsx`

`B6.bis` depende de esa base ya consolidada y produce:

- `financiamiento_*.xlsx`

Reglas duras:

- `B6.bis` no recalcula categorías especiales;
- `B6.bis` filtra y materializa desde `df_categorias_si_vig` las 11 alternativas afirmativas de `G01Q19`;
- `G01Q19` es multiselección: una persona puede producir varias filas y el total del archivo representa selecciones, no estudiantes únicos;
- Word, `Lista_tokens_categorias_SI_*.xlsx` y `financiamiento_*.xlsx` deben compartir el contrato definido en `caracterizacion_financiamiento.py`;
- la ejecución debe bloquearse si el instrumento no contiene exactamente `G01Q19[SQ002]` a `G01Q19[SQ012]` o si aparece una subpregunta no gobernada;
- `G01Q19Time` es metadato de temporización y nunca puede incorporarse como alternativa;
- cualquier cambio de esquema, naming o semántica en `df_categorias_si_vig` debe validarse explícitamente contra `B6.bis`;
- `financiamiento_*.xlsx` debe quedar trazado como salida propia de `B6.bis`, no como detalle implícito absorbido en `B6`.

### Contrato `B8 -> B9`
- `B8` construye el payload analítico de encuesta
- `B9` lo materializa como libro final
- `ENCUESTA_CARACTERIZACION_*.xlsx` depende de ese contrato explícito

### Contrato `B10.bis -> B11 -> B12`
- `B10.bis` define el contenedor maestro de pregrado
- `B11` agrega base analítica integrada dentro del mismo workbook
- `B12` agrega dashboard dentro del mismo workbook
- no deben reaparecer libros analíticos redundantes separados

### Contrato `B10.ter`
- `POSGRADO_DIPLOMADOS_*.xlsx` es libro autónomo
- no debe contaminar ni ser absorbido por pregrado

### Contrato `B10.bis + B10.ter -> B10.quater`

`B10.quater` existe como bloque real del flujo y construye `CRUCE_SIES_*.xlsx`.

Entradas contractuales mínimas:

- base histórica interna de pregrado producida por `B10.bis`
- base histórica interna de diplomados/posgrado producida por `B10.ter`
- reporte SIES filtrado institucionalmente

Reglas duras:

- `B10.quater` usa SIES como universo base;
- las bases internas se usan para enriquecimiento, contraste y trazabilidad, no para reemplazar el universo base del cruce;
- `B10.quater` no debe ejecutarse inventando bases o resolviendo faltantes sin respaldo;
- si falta el reporte SIES filtrado, el bloque puede omitirse, pero esa omisión debe ser explícita y no silenciosamente reinterpretada como éxito funcional del frente.

Artefactos contractuales de entrada desde el flujo interno:

- `CRUCE_SIES_BASE_HIST_PREGRADO`
- `CRUCE_SIES_BASE_HIST_DIPLOMADOS`

Artefactos contractuales de salida:

- `CRUCE_SIES_*.xlsx`
- `RUTA_CRUCE_SIES_ANALITICO`
- `NOMBRE_CRUCE_SIES_ANALITICO`

### Contrato de entrada externa `Subproyecto SIES -> B10.quater`

`B10.quater` depende de un reporte SIES filtrado institucionalmente, producido fuera del flujo principal de `caracterizacion.py`.

Archivo esperado:

- `reporte_matricula_ip_san_sebastian.csv`

Ubicación esperada:

- `EXTRACCION_MATRICULA_SIES*/salida/`

Reglas duras:

- el archivo debe tratarse como insumo externo controlado;
- la inexistencia del archivo no debe resolverse forzando un cruce sin respaldo;
- cualquier cambio en nombre, ubicación o estructura del reporte SIES debe reflejarse en la capa documental y en el código del bloque `B10.quater`;
- la ruta canónica del insumo debe quedar establecida documentalmente, aunque el código mantenga lógica de fallback por compatibilidad.

## Contratos de interpretación

### Cohorte
- usar `COHORTE` solo cuando existe base seguida hacia destino u observación posterior
- no usar `CORTE` si la tabla expresa cohorte

### Retención
- no confundir retención con vigencia simple del mismo período
- la lectura de retención debe respetar la metodología del bloque que la calcula

### Estado
- diferenciar explícitamente histórico, cohorte, destino, final o actual cuando corresponda
- no confundir `ULTIMO_ESTADO_HISTORICO` con resultado de cohorte

## Dependencias críticas entre bloques

- `B0` habilita todo el pipeline
- `B1` alimenta `B3`, `B4`, `B5`, `B6`, `B7`, `B10.bis`
- `B2` alimenta `B3`, `B4`, `B5`, `B6`, `B8`, `B10`
- `B6.bis` depende explícitamente de `B6`
- `B8` produce el contrato de entrada que consume `B9`
- `B10` orquesta `B8 -> B9`
- `B10.x` actúa como capa helper transversal para `B10.bis`, `B10.ter`, `B10.quater`, `B11` y `B12`
- `B10.bis` produce la base histórica interna de pregrado que habilita `B10.quater` y además habilita `B11` y `B12`
- `B10.ter` produce la base histórica interna de diplomados/posgrado que habilita `B10.quater`
- `B10.quater` depende de `B10.bis`, `B10.ter` y del reporte SIES filtrado externo
- `B11` depende de `B10.bis`
- `B12` depende de `B11`

Regla dura:

- una dependencia transversal no debe ocultarse si cambia contratos, inputs, outputs o trazabilidad entre bloques;
- por eso `B10.x` no se gobierna como bloque funcional autónomo, pero sí debe declararse cuando impacta el encadenamiento real del flujo.

## Qué validar si se rompe un contrato

### Si se toca layout o lectura de matrícula
- revisar mapa maestro
- revisar contratos de layout
- revisar `B1`, `B10.bis`, `B10.ter`, `B11`

### Si se tocan llaves analíticas
- revisar mapa KPI/gobernanza
- revisar contratos de normalización
- revisar pregrado, posgrado y encuesta según el nivel implicado

### Si se toca consolidación de libros
- revisar contratos `B8 -> B9` y `B10.bis -> B11 -> B12`
- validar que sigan existiendo exactamente tres libros analíticos finales

## Qué este documento no debe duplicar

No debe duplicar:
- la presentación general del proyecto
- la navegación documental completa del `README`
- la lectura descriptiva por bloque de la TVS
- la guía operativa paso a paso de intervención
