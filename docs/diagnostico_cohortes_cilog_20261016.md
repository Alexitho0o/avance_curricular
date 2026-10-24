# Diagnóstico de coexistencia de códigos y trayectorias CILOG

## Contrato previo al análisis

Encargo 2026-10-16: diagnóstico por carreras, con cobertura amplia de CILOG,
sin modificar agrupaciones, equivalencias ni entregas operativas. Se examina
la hipótesis de códigos SIES distintos por cohortes que conviven bajo un mismo
CODCARPR/nombre/jornada. Una nueva oferta anual no implica automáticamente un
nuevo Código Único; se contrastan los códigos efectivamente publicados.

Fuentes: paquete de oferta histórica 2010–2026 ya gobernado, cohortes MRUN H2,
maestro H5 y las mismas ediciones UMAS verificadas en continuidad_trayectoria.
Oferta = año de publicación; MRUN = año de observación y años de ingreso original
/actual; UMAS = expediente, carrera, plan observado y actividad por año. Estos
conceptos se conservan separados. La oferta 2007–2009 no está cubierta.

Se revisan todos los grupos de carrera existentes. Para CILOG se incluyen todas
las filas disponibles de DatosAlumnos y Promedios, separando el corte hasta 2026
de filas posteriores. RUT y CODCLI solo se usan en memoria. Se exportan conteos
por perfiles académicos, sin identificadores personales ni sus hashes.

Se distingue regular de continuidad por el perfil gobernado y duración. Se
busca coexistencia de versiones del mismo tipo de plan; la duración se presenta
para explicar diferencias, sin forzar igualdad si precisamente cambió la malla.
Se conservan ingreso heredado, matrícula del corte, fecha de matrícula y primera
actividad propia como evidencias diferentes. Homologaciones/convalidaciones no
acreditan inicio efectivo. El plan que etiqueta una nota histórica tampoco
acredita automáticamente la fecha de asignación de ese plan.

El enlace individual MRUN–UMAS no está acreditado por las fuentes del maestro:
la comparación agregada de cohortes no se presenta como emparejamiento personal.
No se asignan códigos por último V, nombre parecido o año de extracción.

## Resultados

Se revisaron 132 grupos existentes carrera/sede/jornada. MRUN presenta 65
combinaciones año/familia/tipo de plan con varias versiones, distribuidas en
16 familias ISC J. Son coexistencias, no 65 carreras ni personas. Se conserva
el inventario completo en `data/diagnostico_cohortes_cilog/20261016/carreras.json`.

### CILOG: cobertura completa de la fuente disponible

DatosAlumnos contiene 56 filas CILOG: 49 dentro del corte hasta 2026, con 49
CODCLI distintos y 47 personas normalizadas; siete filas posteriores se separan.
Promedios contiene 305 filas de asignaturas CILOG, todas etiquetadas con el plan
CILOG20241: 177 de 2025 y 128 de 2026. De estas últimas, 16 tienen estado de nota
vacío y no se usan para afirmar actividad aprobada/reprobada. No se observaron
notas CILOG de 2024. El texto 2024 dentro del nombre del plan no acredita inicio.

| ANOINGRESO | ANOMATRICULA | Primera actividad aprobada/reprobada propia | Expedientes | Estado académico literal del corte |
|---|---|---|---:|---|
| 2024 | 2024 | No localizada | 3 | ELIMINADO |
| 2025 | 2025 | 2025 | 6 | 5 VIGENTE y 1 SUSPENDIDO |
| 2025 | 2025 | No localizada | 2 | ELIMINADO |
| 2025 | 2026 | 2025 | 11 | VIGENTE |
| 2026 | 2026 | 2026 | 21 | VIGENTE |
| 2026 | 2026 | No localizada | 6 | ELIMINADO |

La muestra contiene todos los 49 expedientes, no una selección de casos
favorables. Los estados son los del extracto, no una reconstrucción del estado
en cada año. Un estado eliminado actual no prueba por sí solo que nunca existió
matrícula efectiva; la ausencia de notas es ausencia en esta fuente.

Dos trayectorias explican un defecto del mínimo por persona/carrera:

- Un RUT tiene CILOG 2024 eliminado sin notas y otro CODCLI CILOG 2025 vigente,
  con actividad 2025. Arrastrar 2024 al segundo expediente adelanta su observación.
- Otro RUT tiene ILOG y CILOG 2025 eliminados sin notas, y otro CODCLI CILOG 2026
  vigente con actividad 2026. Arrastrar 2025 produce el mismo problema.

Hay cuatro personas con varios expedientes en las fuentes: las dos anteriores,
una con ILOG eliminado y CILOG con actividad 2025, y otra con CILOG eliminado y
CIIND con actividad 2026. No se localizó un técnico IPSS entre esos antecedentes.
Esto no confirma origen externo ni una equivalencia entre ILOG y CILOG.

**Corrección de la interpretación anterior:** el 2024 descrito como «actividad»
en el análisis previo provenía de ANOMATRICULA, no de notas CILOG. El cuarto
caso anterior a oferta surgía al trasladar el mínimo 2024 entre dos CODCLI de
una misma persona. No es evidencia de una malla de continuidad impartida en 2024.

### Oferta y matrícula de Logística

Nombre literal SIES: INGENIERIA EN LOGISTICA; tipo de plan y modalidad separados.

| Código Único | Tipo | Duración total, semestres | Primera oferta | MRUN 2024 | MRUN 2025 | MRUN 2026 |
|---|---|---:|---:|---:|---:|---:|
| I162S2C77J4V1 | Regular | 8 | 2024 | 9 | 62 | 98 |
| I162S2C77J4V2 | Continuidad | 4 | 2025 | 0 | 14 | 32 |

Son filas de matrícula MRUN por corte. El cero indica ausencia observada en la
fuente, no una afirmación sobre todo registro interno posible. En la oferta 2026
CILOG conserva V2: no se observa un nuevo código de continuidad para ese año.
Por tanto, CILOG no ejemplifica dos versiones sucesivas de continuidad.

En MRUN 2026 las 32 filas V2 se dividen en 11 con ingreso a carrera actual 2025
(original 2024) y 21 con ingreso actual 2026 (original 2025). En UMAS hay también
11 expedientes con ANOMATRICULA 2026 y primera actividad propia 2025, y 21 con
primera actividad 2026. Esta coincidencia de distribución es evidencia agregada
compatible, no un enlace individual acreditado. Los campos de ingreso original
de MRUN no deben interpretarse como ANOINGRESO UMAS mediante igualdad automática.

Las transiciones MRUN trazadas en H2 muestran tres personas con J4V1 en 2025 y
J4V2 en 2026, y ocho que conservan J4V2. Son cambios observados de código; no
acreditan su causa (cambio de programa, rectificación o migración). No hay base
para identificar a esas tres personas con los tres expedientes UMAS de 2024.

### Carreras que contrastan la hipótesis

| Carrera y jornada | Corte MRUN | Códigos coexistentes | Hallazgo |
|---|---:|---|---|
| Técnico en Conectividad y Redes, a distancia | 2019 | I162S2C6J4V1 / I162S2C6J4V2 | V1: primera oferta 2017, 25 filas de cohortes actuales 2017–2018. V2: primera oferta 2019, 28 filas de cohorte 2019. Compatible con separación por cohortes. |
| Ingeniería en Informática, continuidad vespertina | 2019 | I162S2C1J2V2 / I162S2C1J2V3 | Primera oferta 2016/2018, duración 5/4 semestres. V2: 27 filas de cohortes actuales hasta 2017; V3: 38 de 2018–2019. Compatible con coexistencia de versiones del mismo tipo de programa. |
| Ingeniería en Informática, diurna | 2026 | I162S2C1J1V1 / I162S2C1J1V2 | V1 tiene 2 filas de cohorte actual 2026; V2 incluye también cohorte 2026. Mismo nombre, jornada, tipo regular y duración 8 semestres: el año de ingreso no basta para decidir. |

La primera oferta 2010 de algunos códigos es límite de cobertura: no demuestra
que no existieran antes. Las coexistencias MRUN por sí solas no acreditan que
ambos códigos correspondan a un único CODCARPR en cada período histórico.

## Implicación para una futura regla, sin activarla

La hipótesis de coexistencia está respaldada, pero la regla «nuevo año = nuevo
Código Único» no lo está. Hay que registrar cada código realmente ofertado, su
primera aparición y su ámbito de admisión, separados de su presencia con alumnos
antiguos. Un nuevo código no demuestra cierre automático de admisión del anterior.

La unidad propuesta para diagnosticar la asignación es el episodio de carrera:
CODCLI + CODCARPR + sede + jornada + modalidad + tipo/duración + plan UMAS
acreditado + período de ingreso efectivo al programa. RUT sirve para reconstruir
antecedentes, no para trasladar automáticamente el año mínimo entre expedientes.
Una vez acreditado el enlace, el código se conserva para ese episodio en cortes
posteriores, salvo cambio documentado de programa/plan o rectificación. La
fecha de cambio debe quedar trazada: MRUN demuestra que hay cambios reales de
código entre cortes y no permite imponer permanencia incondicional.

Para admitir una asignación automática por cohorte es necesario demostrar que,
dentro de ese perfil y período, existe un solo código aplicable. Si los códigos
coexisten para la misma cohorte, se requiere el plan asignado o el antecedente
SIES individual de ese expediente. No escoger el último V ni el inicio más reciente.
La duración actual tampoco debe excluir una malla histórica con otra duración.

El estado eliminado no se usa como filtro universal para borrar historia. Se
separa matrícula administrativa, actividad observada e ingreso efectivo; se
requiere la secuencia histórica antes de decidir qué episodio se materializó.
Este diagnóstico no altera el resolutor ni promueve ninguna equivalencia.

## Reproducción y evidencia

Comando: `python3 scripts/diagnosticar_cohortes_cilog.py`.

Paquete: [resultados agregados](../data/diagnostico_cohortes_cilog/20261016/resumen.json),
[muestra completa agrupada](../data/diagnostico_cohortes_cilog/20261016/cilog_muestra_completa_agrupada.json),
[trayectorias con varios expedientes](../data/diagnostico_cohortes_cilog/20261016/cilog_trayectorias_multiexpediente.json),
[cohortes MRUN Logística](../data/diagnostico_cohortes_cilog/20261016/logistica_cohortes_mrun.json),
[coexistencias del mismo tipo](../data/diagnostico_cohortes_cilog/20261016/coexistencias_mismo_tipo_plan.json)
y [fuentes y hashes](../data/diagnostico_cohortes_cilog/20261016/manifest.json).

Lectura: DatosAlumnos y Promedios, Hoja1, encabezados fila 1 y proyección de campos
académicos documentada en el script. Oferta: paquete derivado de CSV nacional
2010–2026 con registro_csv por fila. MRUN: agregados H2 con registro_ejemplo y
transiciones reconstruidas por identidad en la fase de origen, integridad
verificada. No se ha realizado un nuevo enlace individual MRUN–RUT–CODCLI.

Conservados Excel del usuario y 137 referencias protegidas. Resultados locales
preparados en el repositorio; no implica commit ni publicación en GitHub.
