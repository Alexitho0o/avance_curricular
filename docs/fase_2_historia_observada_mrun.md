# Fase 2 — Historia observada de programas y versiones en MRUN

Autorización del usuario: continuar la fase 2 el 2026-10-15.
Institución 162, años de observación 2007–2026. El inventario de fase 1 fija
las fuentes y sus límites; esta fase trabaja sobre el CSV MRUN allí verificado.

## Contrato H2

Reconstruir cronología de códigos y versiones informados, cohortes originales
y actuales, coexistencias y cambios observados entre años. Cada resultado
conserva fuente, huella y localizadores; se separan los hechos de cualquier
interpretación curricular. No se decide todavía el plan UMAS de una persona.

La observación es una matrícula informada: `mrun + cat_periodo + codigo_unico`
cuando los campos están completos. MRUN se usa solo en memoria para conectar
registros dentro de la misma instantánea. Las cuatro filas sin MRUN permanecen
en cobertura de programas y se excluyen únicamente del enlace individual.
No se exportan identificadores MRUN, RUT, CODCLI ni sustitutos cifrados.

Familia SIES moderna: `institución + sede + carrera + jornada`. VERSION se
conserva como valor informado. Los códigos heredados que no permiten esta
descomposición se mantienen por su clave literal, sin componentes inventados.
La modalidad, tipo de plan, duración y nombre son atributos observados, no
reemplazos de la identidad ni pruebas automáticas de equivalencia curricular.

## Reglas del análisis

1. Ordenar años de observación. Primera/última aparición significa únicamente
   primera/última aparición en esta fuente; no inicio/cierre de vigencia.
2. Conservar años y semestres de ingreso original y actual por separado.
   Distinguir vacíos, valores especiales y valores fuera del dominio esperado;
   no rellenar con el año observado ni con el sufijo de un código de plan.
3. Identificar coexistencia de V por familia y año, y grupos donde los mismos
   atributos/cohortes dejan más de una versión. Para los contraejemplos de
   suficiencia exigir cohortes completas, cronológicas y semestres 1/2; analizar
   vacíos, sentinelas y valores fuera de dominio por separado. Esto evidencia insuficiencia
   de esos criterios; no demuestra por sí solo un error del registro.
4. Comparar años observados consecutivos de la misma máscara. Una brecha entre
   años se registra como ausencia de observación; no abandono o reingreso.
   Si hay varias matrículas en alguno de esos años, conservar conjuntos de
   códigos: no formar pares arbitrarios ni inferir cuál reemplazó a cuál.
5. Para años con una sola matrícula a cada lado, clasificar cambio de versión
   dentro de familia, cambio de carrera/sede/jornada o código heredado. Un
   cambio informado no acredita causa, homologación ni migración curricular.
6. Registrar cambios de cohortes o atributos bajo el mismo código como hechos
   a contrastar; no corregirlos automáticamente. No extrapolar normativa 2026
   como validación definitiva de todas las ediciones históricas.

## Entregables y verificación

Salida en `data/versiones_historicas_sies_umas/fase_2_20261015/`: historia por
código y año, grupos de cohortes, coexistencias, cambios agregados, excepciones
y resumen con metodología. Los ejemplos incluyen únicamente dimensiones
académicas y número de registro fuente. Los conteos de observaciones, máscaras,
programas y eventos se identifican explícitamente y nunca se suman entre sí.

El script auxiliar no importa ni ejecuta motores oficiales, no escribe fuentes
ni el Excel previo y exige SHA-256 esperado. Se comprobarán preservación de
filas, unicidad de claves completas, cobertura de todos los códigos, conciliación
de transiciones, reproducibilidad de las salidas y casos sintéticos de ausencia
de identidad, años no contiguos, matrícula simultánea y códigos heredados.
H2 acredita la reconstrucción observada y sus excepciones, no la verdad de una
malla ni el cierre del maestro de equivalencias previsto para la fase 5.

## Cierre H2: 2026-10-15

Se reconstruyó el archivo fijado por SHA-256
`510b7d03405398ed29196f750048dea1b07656ba722c1bf12cb3ab427098f0fd`.
Hay 24.386 observaciones de matrícula, 106 códigos y 75 familias modernas.
Los dos códigos heredados permanecen sin descomponer. Las 24.382 claves
individuales completas son únicas; las cuatro filas sin MRUN se mantienen
en las tablas de programas y cohortes. No se exportaron las máscaras.

El archivo físico no estaba ordenado por año: el bloque 2007 aparece después
de 2025. La reconstrucción ordena por `cat_periodo` y conserva el localizador
original. No toma la posición física como secuencia histórica.

### Evidencia para gobernar las versiones

- 21 familias tienen varias versiones en el período; hay 83 grupos familia-año
  con versiones coexistentes. Coexistencia de programas no significa doble
  matrícula de una misma persona.
- Hay 66 grupos que mantienen varias versiones aun igualando familia, año
  observado, modalidad, tipo de plan, ambos años y semestres de ingreso,
  duraciones de estudio/titulación/total, nombre y jornada literales. Se
  exigieron cohortes completas, cronológicas y no especiales; los desconocidos
  se analizaron aparte. Esos criterios son insuficientes para determinar V.
- Se compararon 12.936 pares de años observados dentro de una misma máscara:
  11.922 consecutivos y 1.014 con años intermedios sin observación. Las 181
  situaciones máscara-año con varios programas se preservaron como conjuntos;
  no se fabricó una correspondencia entre sus matrículas.
- En pares de años consecutivos con una matrícula por extremo, hubo 631 cambios
  solo de versión dentro de la misma familia: 553 aumentos y 78 descensos. Son
  cambios de código informado, sin causa académica demostrada. No prueban una
  secuencia creciente de renovación de malla.
- Las familias `I162S2C22J4` e `I162S2C90J2` aparecen por primera vez en este
  MRUN con V2 en 2026. Esto no autoriza inventar una V1 anterior ni negar que
  exista en oferta.

### Ejemplos académicos reproducibles

Los nombres de esta tabla conservan el nombre informado en MRUN para el caso;
la modalidad/jornada y el tipo de plan son dimensiones separadas.

| Caso | Hecho observado | Consecuencia para el cruce |
|---|---|---|
| INGENIERIA EN INFORMATICA, `I162S2C1J1`, 2019 | V1 y V2; ambas con ingreso original/actual 2018-S1, presencial, diurna, regular y duraciones 8/0/8. Registros 10891 y 11439. | Ni ambas cohortes ni duración distinguen la versión; hace falta evidencia adicional de asignación de plan. |
| INGENIERIA EN LOGISTICA, `I162S2C77J4` | Primera observación V1 en 2024, regular 8 semestres; V2 en 2025, continuidad 4. Registros 16477 y 17951. | La diferencia observada incluye tipo de plan y duración; no asumir reemplazo temporal de V1 por V2. |
| INGENIERIA EN CIBERSEGURIDAD, `I162S2C46J2`, 2019 | V1 regular 8, V2 continuidad 5 y V3 continuidad 4, las tres observadas en 2019. Registros 10898, 10943 y 10945. | El mismo año admite variantes simultáneas. Año de ingreso/inicio no es un ordinal de malla. |
| NATUROPATIA, `I162S2C90J2` | Primera observación MRUN 2026: V2 regular 8 semestres. Registro 21174. | Primera versión observada no equivale a primera versión creada; contrastar oferta en fase 3. |

Un mismo código también puede presentar atributos distintos entre observaciones.
La tabla anual conserva esos valores y las transiciones indican cuáles cambian,
incluidos nombre y vigencia. No se rotula automáticamente como cambio de malla.

### Entrega y comprobaciones

- [Resumen](../data/versiones_historicas_sies_umas/fase_2_20261015/resumen.json) y
  [historia por código](../data/versiones_historicas_sies_umas/fase_2_20261015/historia_codigos.json).
- [Historia anual](../data/versiones_historicas_sies_umas/fase_2_20261015/historia_codigo_anio.tsv) y
  [cohortes observadas](../data/versiones_historicas_sies_umas/fase_2_20261015/cohortes_observadas.tsv).
- [Coexistencias](../data/versiones_historicas_sies_umas/fase_2_20261015/coexistencias.json),
  [criterios insuficientes](../data/versiones_historicas_sies_umas/fase_2_20261015/criterios_insuficientes.json) y
  [transiciones](../data/versiones_historicas_sies_umas/fase_2_20261015/transiciones_observadas.tsv).
- [Ejemplos](../data/versiones_historicas_sies_umas/fase_2_20261015/ejemplos_academicos.json),
  [excepciones](../data/versiones_historicas_sies_umas/fase_2_20261015/excepciones.json) y
  [validación](../data/versiones_historicas_sies_umas/fase_2_20261015/qa_fase2.json).

Pasaron ocho pruebas sintéticas de decisiones históricas. Se conciliaron todas
las filas y transiciones; una revisión independiente coincidió en coexistencias,
claves, cambios de versión y los 66 grupos de cohortes completas. Esa revisión
también describe 67 grupos si incluye un grupo con cohorte no completa; su
denominador es distinto y no se confunde con el filtro del script.
Una segunda ejecución produjo los 11 archivos generados idénticos byte por byte.
La fuente conserva su hash. No se modificaron motores, puentes ni libros Excel.
El control de cierre registra dos referencias documentales de Caracterización
actualizadas durante el trabajo, leídas nuevamente y sin impacto en el CSV MRUN
o este análisis. Se preservan sus huellas anteriores en el inventario H1 y las
posteriores en `control_fuentes_al_cierre.json`.

### Reproducción

Script auxiliar: `scripts/reconstruir_historia_mrun.py`. Exige fuente y huella
explícitas; rechaza sobrescribir una salida diferente. No usa fuentes 2027.
`FUENTE_MRUN` en el siguiente ejemplo representa la ruta del CSV inventariado.

```bash
python3 scripts/reconstruir_historia_mrun.py --fuente "$FUENTE_MRUN" --sha256 510b7d03405398ed29196f750048dea1b07656ba722c1bf12cb3ab427098f0fd --salida /ruta/nueva/fase_2
python3 -m unittest discover -s tests -p test_historia_mrun.py -v
```

La fase 2 confirma qué códigos y versiones se informaron y cuándo. La fase 3
debe contrastar la oferta histórica, incluidos códigos sin matrícula. La fase 4
debe acreditar el plan y su asignación temporal en UMAS. Hasta entonces las
ambigüedades siguen abiertas; no se promueve una regla nueva al diccionario.
