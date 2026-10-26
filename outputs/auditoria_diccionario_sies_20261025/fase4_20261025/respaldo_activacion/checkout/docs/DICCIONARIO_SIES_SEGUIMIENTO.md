# Consulta única UMAS → SIES para seguimiento

## Qué usar desde ahora

**D/C.** Para saber qué código SIES respalda un expediente/persona en un contexto,
el punto de entrada es `PROYECTO_IPSS.json → recursos_comunes →
diccionario_sies_seguimiento`. El descriptor activo fija la edición y su hash.
Todos los nuevos análisis de seguimiento deben usar esta entrada, sin copiar
equivalencias ni reconstruir versiones mediante totales, nombres o el año del plan.

**B/C.** La edición v1 integra el registro reproducido del 23 de octubre y las
19 operaciones aprobadas posteriores: 18 asignaciones y una clasificación sin
versión. No crea nuevos cierres. Incluye evidencia anual completa de la base
MU2022–2026 y evidencia histórica vinculada a las observaciones revisadas.
Conserva la procedencia primaria en el manifiesto de construcción de esa base.

## Qué significa la respuesta

| Resultado | Uso y límite |
|---|---|
| B/C_DOCUMENTAL_ANUAL_ATRIBUIDO | Reutilizar el código anual ya atribuido a la persona/expediente. No prueba aceptación SIES ni día de cambio de plan. |
| D_CORRESPONDENCIA_INTERNA_APROBADA | Reutilizar solo dentro del contexto aprobado. El código documental permanece vacío cuando no está acreditado. |
| E_PENDIENTE | Revisar únicamente esta excepción; no usar propuesta, mayoría, primera fila ni versión máxima. |

**C.** El contexto exige identidad normalizada, CODCLI, plan, año y período.
Carrera/sede/jornada completan la selección cuando sea necesario. La misma
persona puede tener varias matrículas: nunca se elige una por su nombre.
El identificador de observación solo tiene sentido dentro de esta edición.

**C.** `consultar` responde por contexto. `codigos_mu` devuelve los códigos
literales de MU por persona/año y las filas que los respaldan. Si hay varios,
los mantiene: una persona no tiene necesariamente un único código para toda su
historia o para todas sus matrículas simultáneas.

**C.** `seguir_cohorte` exige un código de origen que exista en la MU de la persona
y del año indicado. Para cada T2/T3 devuelve:

- `codigo_cohorte_origen`: clasificación de la cohorte que se sigue, conservada.
- `codigo_contexto_destino`: código respaldado para el expediente/plan/período
  consultado, o vacío con excepción explícita.
- Evidencia, regla, estado documental/interno y cambio de versión observado.

No transforma períodos bimestrales/semestrales en trimestres. La entrada debe
identificar la fuente del vínculo entre corte y período académico. Este servicio
no determina vigencia, deserción, elegibilidad ni calcula tasas o denominadores.

## Qué se conserva

**B/C.** Las observaciones históricas abarcan 2019–2026, con períodos nativos
1–5. No son el denominador de retención T1 y no deben sumarse como estudiantes.
Los 5.901 individuos y 6.622 expedientes carrera+CODCLI describen este universo
histórico, no una cohorte nueva. Las 10.200 filas MU2022–2026 se indexan aparte;
25 con tipo documental distinto de RUT quedan pendientes del adaptador documental
y no se eliminan ni se descuentan de ninguna base o tasa.

**C.** C2 conserva su función de consulta académica histórica; el puente operativo
MU2026 y los catálogos anuales permanecen congelados. No se reemplazan motores de
carga. La capa nueva centraliza la atribución personal para seguimiento, que no
estaba resuelta por una equivalencia genérica de plan.

## Consumidores

Los tres comandos ejecutan el mismo código, leen la misma edición y escriben
resultados individuales exclusivamente fuera de Git:

- `scripts/consultar_diccionario_sies_seguimiento.py`
- `scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py`
- `procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py`

Reciben por entrada estándar una lista JSON de objetos `metodo` y `entrada`.
La opción `--salida-privada` exige un archivo nuevo en carpeta privada existente
fuera de cualquier repositorio. No imprimir RUT/CODCLI en el chat o logs.
La API Python común permite procesar lotes sin volver a leer todos los originales.

**C/E.** Los complementos y skills deben localizar el descriptor por
PROYECTO_IPSS.json y llamar a este consumidor local. Una instantánea copiada no
se considera sincronizada. Esta entrega deja el contrato común disponible; no
afirma instalación o publicación en complementos remotos. Sin acceso local,
deben declarar esa limitación, no inferir una versión.

## Control de cambios y reproducción

**D/C.** Una nueva correspondencia requiere decisión con responsable, fecha/hora,
alcance por observación, evidencia y estados antes/después. No editar una edición
activa: generar otra, verificar conservación, emitir diferencias y luego cambiar
el puntero con autorización. Una consulta rechaza hashes de componentes o base
alterados. Revertir una integración consiste en volver al descriptor anterior;
las fuentes y adjudicaciones originales permanecen intactas.

Constructor: `scripts/construir_diccionario_sies_seguimiento.py`. Se detiene si ya
existe la edición. QA: `scripts/verificar_diccionario_sies_seguimiento.py`; contrasta
las 24.774 consultas, consumidores y controles negativos. Las fuentes privadas
requieren acceso local: GitHub por sí solo no permite reproducir las identidades.

**E.** Integración no equivale a resolución universal: las excepciones existentes
siguen abiertas. Las fechas de asignación de plan y atribuciones documentales que
faltaban siguen pendientes, aunque haya correspondencia interna aprobada.

## Edición v2: cierre de 14 contextos (23-10-2026)

**D/C.** Alexi aprobó los 14 recuperables de la revisión de Informática. La
edición activa `v2_20261023_14` conserva v1 y añade 14 correspondencias internas:
ocho anclas T1 con discrepancia de jornada del contexto actual y seis contextos
con puente explícito pasaporte–RUT. El respaldo documental atribuido no cambia.
La respuesta conserva las dimensiones de consulta originales y advierte la
jornada discrepante en motivo/regla/pendiente; no debe interpretarse que el
código histórico valida la jornada actual.

**B/C.** Dos identidades P se incorporan al índice de consulta por el puente
J/BU/BV de IPSS_Procesamiento. Se preservan documento, fuente y fila originales.
El índice histórico pasa de 12.201 a 12.203 enlaces; las filas de MU2022–2026
siguen siendo 10.200. No se añadieron matrículas a la base. Quedan 23 documentos
no RUT de esa base fuera del adaptador verificado. No se generaliza la conversión.

**C.** QA: 24.774 consultas comparadas, 14 cierres exactos y 24.760 respuestas
inalteradas (salvo identificación de edición). Los tres consumidores consultan
la nueva edición a través del mismo puntero. La decisión, alerta y descriptor
anterior están en `data/diccionario_sies_seguimiento/v2_20261023_14/`.
Sin modificación del Excel ni de los denominadores; sin publicación remota.

## Edición v3: INF35-07/T3-2025 (23-10-2026)

**D/C.** Alexi autorizó I162S2C1J2V4 para INF35-07 en período 3 de 2025,
como correspondencia interna. La edición `v3_20261023_inf35_07` conserva v2,
el índice MU completo y las dimensiones originales. Solo cambia esa observación;
la jornada histórica V del respaldo T3 se distingue del contexto posterior O.
La atribución documental y la aceptación SIES continúan pendientes.
La decisión, alerta y descriptor anterior están junto al descriptor v3.
No se extiende a T2-2025 ni a los catorce destinos que siguen en revisión.

## Edición v4: INF35-12/T2-T3-2026 (23-10-2026)

**D/C.** Alexi aprobó T2 → I162S2C1J4V2 y T3 → I162S2C1J1V2, solo para INF35-12 en 2026. Edición `v4_20261023_inf35_12`: conserva v3 y el ancla T1 J4V2. El contexto original posterior D permanece; T2 reutiliza la jornada O de las fotos anteriores, sin reescribir las fuentes. No se declara fecha efectiva del cambio. Atribución documental y aceptación SIES pendientes. Decisión, alerta, fecha/hora y hashes acompañan al descriptor. Dos cambios autorizados, 24.772 consultas restantes idénticas; índice MU, bases, Excel y denominadores conservados. Sin commit/push.

## Edición v5: siete jornadas aprobadas (23-10-2026)

**D/C.** Alexi aprobó INF35-01/02 T2/T3-2024 J1V2, INF35-07 T2-2025 J2V4 e INF35-11 T2/T3-2026 J4V2. Edición `v5_20261023_siete_jornadas`; conserva v4, anclas T1 y dimensiones originales. Atribución documental y aceptación SIES pendientes. No acredita fecha efectiva del cambio ni regla universal. Decisión, responsable, fecha/hora, evidencia y alerta acompañan el descriptor. Exactamente siete cambios internos y 24.767 consultas idénticas; índice MU, bases, Excel y denominadores conservados. Sin commit/push.

## Edición v6: dos jornadas aprobadas (23-10-2026)

**D/C.** Alexi aprueba INF35-04 T3-2024 e INF35-10 T2-2025 como I162S2C1J2V4. Edición `v6_20261023_dos_jornadas`; conserva v5, anclas T1 y dimensiones originales. **E:** atribución documental y aceptación SIES pendientes. INF35-04 refleja destino observado durante T3, sin afirmar jornada única desde el comienzo; INF35-10 continuidad interna de T2, sin acreditar estado exacto al cierre. Responsable, fecha/hora y alerta acompañan el descriptor. Dos cambios internos y 24.772 consultas idénticas; índice MU, bases, Excel y denominadores conservados. Sin commit/push.

## Edición v7: INF35-03 T3-2024 (23-10-2026)

**D/C.** Alexi aprueba I162S2C1J1V1 exclusivamente para INF35-03 T3-2024 como correspondencia interna por continuidad contextual T3-2024/T1-2025. **E:** invariancia temporal asumida internamente, sin fecha efectiva demostrada; atribución documental pendiente. No extender a T2-2024 ni 2026. Edición `v7_20261023_inf35_03_t3` conserva v6, índice MU, bases, Excel, dimensiones y denominadores. QA: un cambio autorizado y 24.773 consultas conservadas. Responsable, fecha/hora, evidencia y alerta en descriptor. Sin commit/push.
