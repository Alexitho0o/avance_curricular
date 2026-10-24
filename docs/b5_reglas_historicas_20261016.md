# B5 — Reglas históricas y validación

Especificación previa, 2026-10-16. B4 construyó evidencia, no equivalencias
activas. B5 produce un registro separado de reglas internas observadas y un
resolvedor que devuelve estado, candidatos y evidencia. No modifica H5 ni activa
asignaciones en los consumidores. El Excel se revisará en C1.

## Hipótesis fijadas antes de medir

K0: clave B4 completa (carrera, sede, jornada, año observado, ingreso original,
primera observación disponible en carrera, conjunto de planes observados).
K1: K0 + PERIODOINGRESO UMAS.
K2: K0 + ANOMATRICULA y PERIODOMATRICULA UMAS.
K3: K0 + los tres campos adicionales.
Son valores literales, no semestres SIES ni períodos académicos de las notas.
Ninguna clave usa nacimiento, sexo, documento, CODCLI ni versión de destino.
No extrapolar una clave exacta a otro año. Falta de plan queda explícita y no
significa cualquier plan. No completar un campo requerido ausente.

Analizar por separado, solo como explicación de los 16 contextos múltiples,
semestre original y año/semestre actual del reporte SIES. Estos campos no se
incorporan como entradas UMAS si no hay una transformación acreditada. Que una
partición elimine contradicciones no demuestra una regla: puede aislar personas.

## Evidencia y validación reservada

Construir etiquetas desde reportes institucionales unidos por documento y
familia preexistente, descartando atribución ambigua a varios programas UMAS.
No usar la identidad MRUN propuesta para construir etiquetas ni elegir claves.
Registros con varios códigos reportados siguen ambiguos; no elegir uno.
Deduplicar persona/año/clave/código para que notas repetidas no sean más evidencia.

Separar personas determinísticamente: SHA-256 de semilla fija y documento en
memoria, 20 % reservado. Una persona queda siempre del mismo lado entre años y
carreras. Aprender reglas solo en construcción; contrastar solo en reserva.
Publicar las cuatro hipótesis, sin seleccionar la mejor sobre la reserva y
presentarla luego como validación independiente. Evaluar también transporte
2018–2020→2022 quitando año de la clave, como ensayo separado; jamás habilitar
esa extrapolación con los resultados del modelo exacto.

Los reportes históricos no constituyen certificación curricular. La separación
por persona evita repetición individual, pero sigue compartiendo fuente
institucional. Cada regla debe exponer personas de construcción, años, reserva,
conflictos, oferta anual y estado; ningún umbral arbitrario la certifica.

## Estados y contrato

ENTRADA_INCOMPLETA: falta un campo obligatorio; PLAN_NO_OBSERVADO es marcador
explícito aceptado, no comodín.
SIN_REGLA_OBSERVADA: clave no vista en construcción.
CONFLICTO_CONSTRUCCION: varios códigos en la misma clave de construcción.
SIN_OFERTA_ANUAL: destino observado sin oferta para ese año.
CONTRADICCION_EN_RESERVA: al menos un destino reservado contradice la regla.
OBSERVADA_SIN_RESERVA: destino único sin contraste de otra persona reservada.
CORROBORADA_EN_RESERVA: destino único y coincidencias reservadas, sin desacuerdos.

El resolvedor devuelve siempre estado y candidato(s); nunca codigo_acreditado ni
habilitación productiva. El registro H5 mantiene cero reglas efectivas. Una
regla observada es un resultado útil gobernado, no una equivalencia formal.
Cierre B5: registro completo, métricas de cobertura/reserva, explicación de los
16 contextos, casos trazables sin personas, pruebas y preservación. Las brechas
se trasladan a la entrega como estados, sin exigir una tabla oficial RUT–MRUN.

## Control temporal añadido durante el diagnóstico

Se detectó ANOMATRICULA 2022 en un contexto observado de 2019. Las variantes
K2/K3 conservan sus métricas descriptivas, pero sus reglas se marcan
DATO_POSTERIOR_AL_CONTEXTO cuando dependen de matrícula posterior. La separación
estadística en un extracto actual no acredita una regla disponible para la fecha
histórica. Este control no elige una hipótesis por su rendimiento en reserva.

## Resultado de B5

Se construyeron etiquetas académicas desde 3.116 observaciones, usando documento
y familia de carrera de los reportes institucionales. Se separaron 1.876 personas
para construcción y 474 para reserva; ninguna aparece en ambos grupos. Son
personas distintas del conjunto documental disponible, no una nueva medición de
los mismos 500 casos del piloto anterior. La reserva produce 620 consultas
persona/clave/código: una persona puede aportar varias carreras o años.

No se utilizó el enlace MRUN propuesto para decidir el código de entrenamiento.
La capa demográfica sigue gobernando ese enlace inferido; el reporte unido por
documento aporta aquí una evidencia académica distinta, con sus propios límites.
No se sustituye ningún dato demográfico ni se presenta una identidad como certificada.

### Comparación de las cuatro claves

| Clave | Reglas de construcción | Consultas reservadas coincidentes | Contradictorias | Con clave conflictiva | Sin regla |
|---|---:|---:|---:|---:|---:|
| K0: contexto B4 | 424 | 560 | 1 | 17 | 42 |
| K1: K0 + período de ingreso UMAS | 467 | 553 | 1 | 16 | 50 |
| K2: K0 + año/período de matrícula UMAS | 704 | 521 | 2 | 11 | 86 |
| K3: K0 + los tres campos | 754 | 508 | 2 | 11 | 99 |

No hubo consultas reservadas con clave incompleta en este conjunto. Las cifras
son consultas deduplicadas dentro de cada modelo, no estudiantes distintos ni
versiones de malla. Más claves no implica mejor regla: al fragmentar el contexto
aparecen más combinaciones sin respaldo de otra persona. No se eligió un modelo
para producción ni se reutilizó la reserva para declarar validada esa elección.
Las cifras K2/K3 son descriptivas y conservan casos con datos posteriores; estos
se señalan en el estado de cada regla, no quedan habilitados.

### Registro base K0 para la nueva entrega

Las 424 reglas observadas de K0 se distribuyen en:

- **197 corroboradas en reserva:** mismo destino en construcción y otras
  personas reservadas, sin contradicción en esa clave.
- **211 observadas sin reserva:** falta contraste de otra persona reservada.
- **15 con conflicto en construcción:** más de un destino para la misma clave.
- **Una contradictoria en reserva:** la unicidad de construcción no se sostuvo.

Las 197 corroboradas involucran 42 códigos SIES distintos. De ellas, 156 incluyen
plan(es) observado(s) y 41 no tienen plan observado. Estas últimas describen una
relación de programa/contexto, no una equivalencia de malla. En las 156 restantes,
la etiqueta de plan de PROMEDIOS tampoco acredita por sí sola su vigencia efectiva.
Todos los estados y soportes están disponibles para C1; no se presentan las 197
como equivalencias formales ni como vigencias universales.

### Los 16 contextos con versiones múltiples

- PERIODOINGRESO UMAS por sí solo: no elimina la multiplicidad en ninguno.
- ANOMATRICULA + PERIODOMATRICULA: separa cuatro contextos.
- Los tres campos UMAS: separan cinco; once continúan múltiples.
- Semestre original SIES por sí solo: no separa ninguno.
- Año/semestre de ingreso actual SIES: separa uno.
- Los cuatro atributos de ingreso SIES: separan dos.

Estas particiones son descriptivas: algunas crean grupos de una sola persona.
No acreditan una regla robusta y los campos del reporte no se transfieren a
UMAS sin transformación documentada. El detalle conserva tamaño de los grupos
y multiplicidad, sin datos identificatorios.

**Ejemplo IECIRE, RE, D, 2019, ingreso original 2018, plan IECIRE20191
(B4-00362):** tres personas tienen dos códigos. Sus campos de ingreso SIES no
separan los destinos. Los datos actuales de matrícula UMAS sí forman dos grupos:
ANOMATRICULA 2019/período 1 aparece con I162S2C1J1V2 y ANOMATRICULA
2022/período 1 con I162S2C1J1V1. El segundo usa información posterior a 2019;
no constituye una regla histórica válida por ese solo resultado. El primero
solo tiene una persona de construcción y ninguna de reserva.

### Por qué el año permanece en la clave

El ensayo separado de transporte 2018–2020→2022 quitó el año observado de K0.
Obtuvo 152 coincidencias, 59 contradicciones, seis consultas con conflicto y 720
sin regla, sobre 937 consultas de 2022. Por tanto, no se autoriza extender una
relación observada de un año a otro. Este ensayo temporal puede repetir personas
entre años: no se confunde con la reserva disjunta por persona del ensayo principal.
Los otros modelos también presentan contradicciones, registradas en el resumen.

### Ejemplos de consulta gobernada

B5-K0-0003: IECIRE / RE / D / 2018 / ingreso original 2018 / primera
observación 2018 / PLAN_NO_OBSERVADO. Dos personas de construcción y una de
reserva aportan I162S2C1J1V1. Estado CORROBORADA_EN_RESERVA; no acredita malla.

B5-K0-0353: TPCREOL / RE / O / 2020 / ingreso original 2020 / primera
observación 2020 / plan TPCREOL. Tres personas de construcción aportan
I162S2C2J4V1, pero una de reserva contradice la propuesta. Se devuelve
CONTRADICCION_EN_RESERVA y no se habilita resolución automática.

El consumidor recibe estado, candidatos e identificador de regla, nunca un
código acreditado por defecto. Una clave desconocida o de otro año devuelve
SIN_REGLA_OBSERVADA. No hay búsqueda aproximada ni selección de versión mayor.

## Entrega y cierre

B5 queda ejecutado como registro de reglas internas observadas, resolvedor y
validación con excepciones. La resolución total de equivalencias permanece
abierta; no se declara terminada la fase B en su sentido de acreditación plena.
El siguiente hito es **C1**, que puede entregar los resultados con sus estados:
corroborados, observados sin reserva, conflictivos y sin evidencia, conservando
las carreras y sectores editados. No necesita ocultar pendientes para avanzar.

Se conserva el maestro H5 sin cambios y cero reglas formales promovidas. B5 es
un recurso separado, versionado y consultable. Las 137 referencias congeladas,
el Excel y todas las salidas B4 conservan sus hashes. Cinco pruebas verifican
clave anual, campos requeridos, conflictos/reserva, dato posterior y consulta
sin habilitación automática. Las fuentes personales permanecen externas y se
verifican por hash; no se exportaron identificadores ni hashes personales.

```sh
python3 -m unittest discover -s tests -p test_reglas_historicas_b5.py
python3 scripts/evaluar_reglas_historicas_b5.py
python3 scripts/consultar_reglas_b5.py --entrada entrada_academica.json --modelo K0
```

`entrada_academica.json` contiene uno de los objetos `entrada` de los ejemplos;
no lleva RUT/CODCLI/MRUN. El éxito de ejecución del comando no significa que el
estado sea corroborado: el consumidor debe leer el estado devuelto.

[Resumen y métricas](../data/reglas_historicas_b5/20261016/resumen.json),
[registro de reglas](../data/reglas_historicas_b5/20261016/reglas_observadas.json),
[diagnóstico de los 16 contextos](../data/reglas_historicas_b5/20261016/diagnostico_16_contextos.json),
[ejemplos](../data/reglas_historicas_b5/20261016/ejemplos_consulta.json).
