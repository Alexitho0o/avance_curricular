# MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA

## Rol rector

Este documento es la referencia rectora de gobernanza KPI, semántica analítica y niveles de análisis del proyecto `CARACTERIZACIÓN`.

Su función es fijar cómo debe interpretarse cualquier hoja, KPI, tabla, dashboard o indicador antes de tocar nombres, fórmulas, agregaciones o lecturas ejecutivas.

## Jerarquía conceptual

### Documento estructural rector
- `MAPA_MAESTRO_CARACTERIZACION.md`

### Documento rector de KPI y niveles
- este documento

### Documentos subordinados
- `README.md`
- `MANIFEST_BLOQUES.yaml`
- `TVS_BLOQUES.md`
- `CONTRATOS_INVARIANTES.md`
- `GUIA_INTERVENCION_SEGURA.md`

## Niveles de análisis obligatorios

### `RUT`
Identidad transversal de la persona.

Usar cuando:
- se sigue a la misma persona a través del tiempo
- la persona puede tener más de una trayectoria
- interesa continuidad, cambio, reingreso o movilidad personal

No usar cuando:
- la unidad real es una trayectoria específica
- el KPI mide permanencia o resultado de un programa concreto

### `CODCLI`
Trayectoria académica o programa específico del estudiante.

Usar cuando:
- se mide cohorte, permanencia, retención o desenlace de una trayectoria
- interesa una matrícula/programa particular
- el cambio de carrera o plan no debe colapsarse a persona

### `CODCLI_PERIODO`
Trayectoria observada en un año/período concreto.

Usar cuando:
- el estado depende del período
- se trabaja con longitudinal fino por observación temporal
- la fila representa trayectoria + año + período

### `REGISTRO`
Fila operativa no consolidada.

Usar cuando:
- la hoja es soporte detallado o trazabilidad operativa
- todavía no existe agregación por persona ni por trayectoria
- la unidad sigue siendo la fila exportada

## Reglas críticas de interpretación

Para el instrumento 2027, `Tengo un emprendimiento formalizado` es la alternativa institucional AO05 de G02Q95, confirmada en la exportacion y registrada en `gobernanza/FCU/2027/preparacion/json/PREGUNTAS_INSTITUCIONALES_2027.json` version 3. No es una pregunta independiente pendiente. Conservar las cuatro alternativas originales y G02Q20. Analizar AO05 como variable institucional separada, sin alterar SIT_LAB oficial, convertir faltantes en No ni reconstruir respuestas de otros anos. G02Q27 es texto institucional mixto de empresa o emprendimiento y no confirma NOMBRE_EMPRENDIMIENTO; conservar respuesta literal y estado. Reglas completas: `gobernanza/FCU/2027/preparacion/docs/EMPRENDIMIENTO_FORMALIZADO_2027.md`.

- no usar “persona” como alias ambiguo de una hoja `RUT` sin decirlo explícitamente
- no usar “alumno” como alias ambiguo de una hoja `CODCLI`
- no usar “registro” si en realidad ya existe consolidación por `CODCLI_PERIODO`
- no usar “cohorte” si la tabla solo expresa un corte puntual y no una base seguida hacia destino
- no usar “retención” como sinónimo de “vigente” sin especificar la metodología

## Relación esperada entre frente y nivel analítico

### Encuesta pura
- dominante: `TOKEN`
- cruces auxiliares: `RUT` o `RUT_NORMALIZADO` cuando corresponda

### Pregrado longitudinal principal
- dominante: `CODCLI`
- detalle fino: `CODCLI_PERIODO`
- continuidad personal complementaria: `RUT`

### Posgrado / diplomados
- dominante: `RUT`
- trazabilidad adicional: `CODCLI`
- detalle histórico: `CODCLI_PERIODO` o `REGISTRO` según la tabla

### Operativo
- dominante: `REGISTRO`, `TOKEN` o `RUT` según la salida

## Ficha estándar obligatoria para cualquier KPI o hoja crítica

Toda hoja o KPI relevante debe poder describirse con esta ficha:

- **Archivo**
- **Hoja**
- **Nombre visible**
- **Nombre técnico**
- **Descripción**
- **Nivel de análisis**
- **Unidad analítica**
- **Llave dominante**
- **Universo**
- **Exclusiones**
- **Columnas de entrada**
- **Columnas de salida**
- **Fórmula o lógica**
- **Interpretación**
- **Limitaciones**
- **Dependencias**
- **Validaciones mínimas**

## Reglas de naming metodológico

### Para hojas
- el nombre visible debe declarar el fenómeno y no el artefacto interno
- si una hoja es KPI, debe poder leerse sin conocer el código
- si una hoja es de cohorte, debe decir `COHORTE`
- si una hoja es histórica, debe decir `HISTORICO`, `ANUAL`, `POR_ANIO` o equivalente claro
- si una hoja es de persona, trayectoria o período, debe dejarlo inferible o explícito

### Para columnas
- conteos: `TOTAL_*`, `CONTEO_*`, `*_UNICOS`
- porcentajes o tasas: `*_PCT`, `TASA_*_PCT`
- banderas: `ES_*`, `TIENE_*`, `FUE_*`, `CONDICION_*`, `RESULTADO_*`
- clasificaciones: `CATEGORIA_*`, `TRAMO_*`, `NIVEL_*`, `ESTADO_*`
- temporalidad: diferenciar `ANIO_COHORTE`, `ANIO_DESTINO`, `ANIO`, `PERIODO`
- estados: diferenciar `HISTORICO`, `COHORTE`, `DESTINO`, `FINAL`, `ACTUAL` cuando corresponda

## Marco de lectura por nivel analítico

| Nivel | Unidad real | Pregunta que responde |
|---|---|---|
| `RUT` | persona | ¿qué pasó con la persona a través del tiempo? |
| `CODCLI` | trayectoria | ¿qué pasó con esa trayectoria académica específica? |
| `CODCLI_PERIODO` | trayectoria por período | ¿qué estado tenía esa trayectoria en ese período? |
| `REGISTRO` | fila operativa | ¿qué dice la fila exportada sin consolidar? |

## Regla de coherencia KPI

El mismo fenómeno no debe cambiar de significado entre hojas.

Ejemplos:
- `RETENCION` debe significar lo mismo en todas las hojas del mismo frente
- `COHORTE` no debe mezclarse con `CORTE` si la tabla sigue una base hacia un destino
- `ESTADO_FINAL` no debe confundirse con `ULTIMO_ESTADO_HISTORICO`
- `PERSONA` no debe aparecer donde el agrupamiento real es `CODCLI`

## Qué documentos deben obedecer esta gobernanza

- `README.md`: debe remitir aquí para lectura de niveles de análisis y KPI
- `MANIFEST_BLOQUES.yaml`: debe declarar llaves dominantes y documentos asociados
- `TVS_BLOQUES.md`: debe respetar esta clasificación en su lectura por bloque
- `CONTRATOS_INVARIANTES.md`: debe tratar estas definiciones como reglas duras
- `GUIA_INTERVENCION_SEGURA.md`: debe usar este documento para cualquier cambio de KPI, naming o niveles analíticos

## Qué no debe volver a pasar

- reconstruir desde cero si una hoja es por `RUT` o por `CODCLI`
- usar naming híbrido técnico-metodológico sin criterio
- cambiar la lectura de una métrica por conveniencia visual
- mezclar continuidad personal con retención de trayectoria
- llamar “persona” a cualquier agregado sin declarar el nivel analítico real
