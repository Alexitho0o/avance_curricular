# Recuperación del cálculo primario H113 · 27-10-2026

## Contexto y resultado

[B/C] Proceso Avance Curricular SIES 2026, actividad académica de 2025 y acumulada hasta 2025. Universo fijo: 2.371 registros de precarga, no personas necesariamente distintas ni el denominador de retención. Esta continuación de Fase 1 recupera el conteo primario y no crea el Excel histórico.

[B/C] Se recuperó H94D del commit 3067c97 y se reprodujo en memoria su selección de PROMEDIOS, omitiendo explícitamente un mapeo externo no localizado. Coinciden las seis columnas académicas de **2.370/2.371 registros**. Hay **un registro distinto en las seis columnas**. El QA es parcial, no PASS integral.

[D] Se conservan fuentes, bases, denominadores, motor anual, diccionario y decisiones anteriores. No se aplicaron correcciones, no se creó Excel y no se hizo commit/push.

## Hito 1/3 · Cadena recuperada

[B/C] El script completo es `avance_curricular_2026/94d_materializacion_5809_entregable_16_21/MATERIALIZACION_5809_ENTREGABLE_16_21_20260709_030447/h94d_materializar_5809_entregable_16_21.py`, recuperado por lectura de Git. Las rutas y hashes de H77/H93/H94D/H95/H99 están en MANIFEST_ORIGEN_H113.json. No se ejecutaron los scripts históricos: algunos tienen escrituras o borrados fuera de esta auditoría.

[B/C] PROMEDIOSDEALUMNOS_7804.xlsx, copia consolidada de OneDrive, conserva el SHA-256 registrado para la fuente histórica: `83a0ba72b21d25dd0d151b75fb0182a1f55bbe3f5efba06d088c994067262fca`. Se leyeron todas sus hojas: Hoja1 129.493 filas; DatosAlumnos 13.707; Matricula_2025 14.055; matriz 139; base_datos 72. Son filas de distinta naturaleza, no un total de personas sumable.

[C] H94D selecciona por documento normalizado y amplía por CODCLI; concatena y elimina filas idénticas. En el conteo no restringe explícitamente la actividad a CODCARR o PLAN_DE_ESTUDIO del registro de precarga. El marcador de hoja participa en la eliminación de duplicados.

| Clase | Campo | Implementación recuperada H94D |
|---|---|---|
| C/D | CURSO_1ER_SEM | SI si hay actividad A/R en 2025 y período 1 o 5. |
| C/D | CURSO_2DO_SEM | SI si hay actividad A/R en 2025 y período 2, 3, 4 o 6. |
| C/D | UNIDADES_CURSADAS | Número de filas A/R en 2025. |
| C/D | UNIDADES_APROBADAS | Número de filas A en 2025. |
| C/D | UNID_CURSADAS_TOTAL | Número de filas A/E/I/R con año hasta 2025. |
| C/D | UNID_APROBADAS_TOTAL | Número de filas A/E/I con año hasta 2025. |

[C/D] Esta tabla describe lo ejecutado históricamente; no convierte la selección de estados ni la equivalencia de períodos en reglas oficiales universales. H93 documenta la decisión interna sobre E/I. Se cuentan filas después de la eliminación indicada, no asignaturas distintas por código.

[A/E] El instructivo 2026, pp. 4–5, exige referir el avance a la carrera informada y separar anual/acumulado. La correspondencia normativa de cada fila debe comprobarse además de reproducir el código. Véase la cita y alcance en el informe anterior `outputs/avance_historico_fase1_20261027/INFORME_FASE1.md`. No se acreditó aceptación final PES.

## Hito 2/3 · Conciliación y alertas

| Clase | Unidades académicas | H113 | Reproducción sin mapeo externo | Diferencia reproducción − H113 |
|---|---|---:|---:|---:|
| B/C | Cursadas 2025 | 21.389 | 21.377 | −12 |
| B/C | Aprobadas 2025 | 17.628 | 17.616 | −12 |
| B/C | Cursadas acumuladas | 47.205 | 47.193 | −12 |
| B/C | Aprobadas acumuladas | 41.627 | 41.615 | −12 |

[B/C] La diferencia está en una fila de I162S2C1J2V4, PLAN_ESTUDIOS=1: H113 tiene SI/SI y 12/12/12/12; la reproducción sin el mapeo no encuentra filas fuente. Sus ceros son un resultado técnico del lector, **no prueba de falta de actividad académica**. No se cambió H113.

[E] Falta localizar `MAPEO_IDENTIDAD_CODCLI.xlsx`, esperado SHA-256 `ed50755cd8d56270d79e5c422dfad88434082692cf865368faca6caf1af619b7`. Ruta histórica: `avance_curricular_2026/05_cierre_integral/CIERRE_AVANCE_CURRICULAR_20260703_125157/04_CONCILIACION_MATRICULA/PREPARACION_MATRICULA_20260703_141254/02_IDENTIFICADORES/MAPEO_IDENTIDAD_CODCLI.xlsx`. No apareció por nombre en el repositorio, almacenamiento privado IPSS y OneDrive revisados. Eso no demuestra ausencia en archivos comprimidos u otros respaldos. Tampoco prueba todavía que este mapeo explique las 12 unidades.

| Clase | Alerta observada | Conteo | Interpretación |
|---|---|---:|---|
| B/C | Llaves normalizadas con identidades de precarga diferentes | 7 grupos / 14 filas | La función elimina el último carácter del cuerpo documental. |
| B/C/E | Filas con actividad de varios cuerpos documentales seleccionados | 27 | Revisar colisiones o enlaces; no equivalen automáticamente a 27 errores. |
| B/C/E | Filas con varios CODCLI en actividad seleccionada | 492 | Debe atribuirse actividad al expediente y contexto. |
| B/C/E | Filas con varias carreras / varios planes seleccionados | 489 / 489 | Categorías solapadas; no sumarlas. |
| B/C/E | Filas con aprobación repetida CODCLI + plan + CODRAMO | 9 | Diez repeticiones; pueden requerir revisar equivalencia o repetición válida. |
| B/C/E | Filas sin ninguna fuente seleccionada | 7 | Seis reproducen el cero de H113; una es la diferencia descrita. |

[B/C] NUM_DOCUMENTO contiene solo dígitos en las 2.371 filas de precarga, con DV separado no vacío en 2.346. En Hoja1, las 129.493 filas tienen RUT de solo dígitos y DIG separado. H94D aplica `doc_norm` eliminando igualmente el último carácter (líneas 116–122), y al seleccionar no usa el DV. La unión por documento/CODCLI se ejecuta en las líneas 289–313; los conteos en 337–345. Las alertas se recalcularon sobre los archivos, sin publicar identidades.

[E] No se cuantificó aquí el impacto académico correcto de esas alertas. Igualar H113 puede reproducir una selección equivocada; modificarla sin atribución comprobada tampoco sería válido. Las 489 filas multicarrera no son 489 personas necesariamente diferentes ni 489 errores confirmados.

## Hito 3/3 · QA, trazabilidad y siguiente paso

[B/C] CONTROLES_INTEGRIDAD aprobados: 17. Fuentes antes/después, rama, HEAD y cuatro archivos previamente modificados permanecen iguales. La conciliación primaria sigue pendiente por una fila y por las alertas de atribución. El proceso de auditoría terminó correctamente; las salidas contienen únicamente metodología y agregados, sin RUT, nombres ni CODCLI individuales.

[C] Reproducción desde la raíz del repositorio:

```sh
python3 outputs/avance_historico_origen_h113_20261027/reproducir_origen.py
```

[C] Requiere pandas, openpyxl y acceso a las cuatro fuentes registradas. Reproduce una auditoría acotada sin el mapeo externo; no es un motor de carga ni modifica bases. Las llaves individuales se procesan solo en memoria. Las salidas persistentes incluyen una conciliación por código y plan, resultados, QA y manifiesto con hashes.

[C/E] Checkpoint: revisar primero el enlace faltante de una fila y las colisiones documentales; después atribuir únicamente los expedientes multicarrera afectados, reutilizando el diccionario y las decisiones ya aprobadas. Comparar el resultado como escenario separado contra H113/H114B; no reemplazar el histórico. No repetir mallas ni búsquedas de titulados cerradas. La extensión histórica y el Excel continúan pendientes de esta validación.

[D] Se mantienen separados los futuros análisis: avance anual conforme al proceso SIES, seguimiento T1/T2/T3 y aprobadas/reconocidas aplicables frente a la malla. Sin cambios de denominadores.

[B/C] Rama: feature/ire-2026. HEAD antes y después: `262f445828f7e939fac59c3cc76d0bb20a101746`. Resultados locales sin commit/push; no se afirma publicación en GitHub.
