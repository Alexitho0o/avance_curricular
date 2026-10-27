# Fase 1 · Recuperación de Avance Curricular para el análisis histórico

## Resultado y alcance

**[B/C] Se recuperó la cadena H112A → H112B → H113 → H114B y se reprodujeron 49 controles, todos PASS.** La reproducción comienza en el detalle de asignaturas H112A y en el CSV H113. **[E] No es todavía una reproducción integral desde las fuentes primarias PROMEDIOS ni una acreditación de aceptación final PES.** Por eso el estado es `PASS_CONTROLES_PARCIALES`, no PASS integral. La Fase 2 no comenzó.

**[D]** Se ejecutó únicamente la fase 1 pedida por Alexi: sin nuevo Excel, sin cambios a originales, bases, denominadores, motor anual o diccionario, y sin commit ni push.

**[B/C]** Contexto: IPSS 162; proceso Avance Curricular SIES 2026, datos académicos 2025. Los 2.371 registros precargados de este proceso son un universo distinto del de retención; no se reemplaza ningún denominador de retención con esta cifra.

## Hito 1/3 · Cadena y precedencia

| Clase | Fuente | Papel y estado comprobado |
|---|---|---|
| A | Instructivo Avance Curricular SIES 2026, pp. 2, 4–6 | Anual 2025 y acumulado hasta cierre 2025; avance respecto de la carrera informada en matrícula 2025; unidad coherente con su plan. |
| B/C/D | H112A, carpeta 20260709_114429, hojas 05/06/10 y script | 1.711 filas de unidades curriculares; distribución interna de niveles en años. |
| B/C/D | H112B, Carreras 16769 | 43 filas, 21 columnas. 11 campos de precarga conservados; unidad 1 y distribución de H112A. |
| B | Informe H112D recuperado de Git 3067c97 | Registra carga completa 43/43 y estado «En Validación de Datos»; no aceptación final. |
| B/C | H113, Matrícula 16768 | 2.371 filas, 21 columnas, 43 combinaciones código único + plan. Estado «PARA_PRUEBA_SIES». |
| B/C | H114B, 10-07-2026 | Corrección posterior de aprobadas acumuladas. Estado «PARA_PRUEBA_PES». Es la última transformación localizada en esta revisión. |
| E | Cierre final en PES | No se localizó constancia que permita cambiar «prueba/validación» por «aceptado definitivamente». |

**[B/C]** Los manifiestos históricos se leyeron mediante `git show`, sin restaurar ni activar código. Sus rutas, commit completo y hashes están en `MANIFEST_FASE1.json`. Las fuentes locales están en OneDrive, bajo `Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Avance Curricular/2026`. El manifiesto registra la ruta absoluta exacta de cada entrada.

## Hito 2/3 · Conciliación reproducida

| Clase | Control | Respaldado | Reproducido | Diferencia |
|---|---|---:|---:|---:|
| B/C | Carreras / planes de carga | 43 | 43 | 0 |
| B/C | Registros matrícula | 2.371 | 2.371 | 0 |
| B/C | Registros con carrera-plan localizado | 2.371 | 2.371 | 0 |
| B/C | Registros corregidos por H114B | 247 | 247 | 0 |
| B/C | Combinaciones afectadas por H114B | 20 | 20 | 0 |
| B/C | Diferencias contra transformación H114B | 0 | 0 | 0 |
| B/C | Cambios en las otras 20 columnas | 0 | 0 | 0 |

**[B/C]** Los CSV H112B y H113 coinciden con los SHA-256 de sus manifiestos históricos. Los CSV H112B y H114B coinciden con sus hojas de revisión, comparando las celdas después de normalizar representaciones numéricas. Entre H113 y H114B se comprobó la igualdad exacta de las demás columnas y del orden de las llaves. No se escribieron registros personales en las salidas.

| Clase | Unidades, no personas | H113 | H114B | Cambio histórico |
|---|---|---:|---:|---:|
| B/C | Cursadas durante 2025 | 21.389 | 21.389 | 0 |
| B/C | Aprobadas durante 2025 | 17.628 | 17.628 | 0 |
| B/C | Cursadas acumuladas | 47.205 | 47.205 | 0 |
| B/C | Aprobadas acumuladas | 41.627 | 38.235 | −3.392 |

**[C]** La auditoría repite, sin aplicarla a otra población, la fórmula histórica:

`aprobadas_total_H114B = mínimo(aprobadas_total_H113; unidades_del_plan_H112B; cursadas_total_H113)`.

**[A/C/E]** El instructivo (p. 5 y estructura de aprobadas acumuladas, p. 14) establece el total del plan como referencia y una tolerancia del 25% por encima. El límite estricto al 100% observado en H114B es una implementación histórica; esta auditoría no acredita que sea obligatorio truncar así cada conteo ni que las 3.392 unidades reducidas fueran todas duplicadas o inválidas. La causa académica de cada reducción no fue reconstruida aquí. Deben mantenerse separados el conteo primario y la transformación de carga al extender el análisis.

**[C/D]** La periodización de mallas recuperada calcula `grupo = techo(nivel_máximo / años_permitidos)` y ubica cada unidad en `mínimo(años_permitidos; máximo(1; techo(nivel / grupo)))`. Se reprodujeron la hoja 06, los siete conteos anuales de la hoja 10 y su traspaso a H112B sin diferencias. Esto distribuye unidades de malla: **no prueba que un estudiante completó un nivel ni convierte automáticamente PERIODO 1–5 de UMAS en trimestres o semestres**.

**[A]** El indicador de avance se refiere a aprobaciones respecto del total del plan (p. 4, letra g). No debe confundirse con aprobadas/cursadas. Las convalidaciones o reconocimientos no entran automáticamente en aprobadas anuales, pero sí pueden entrar en el acumulado de la carrera conforme al instructivo (p. 5, letras i–j).

**[C]** `CONCILIACION_43_CARRERA_PLAN.csv` conserva los conteos de ambas versiones y su diferencia por código completo y plan. Su campo de avance agregado divide aprobadas acumuladas por la suma de las unidades de plan correspondientes a cada registro (96.104 unidades como denominador sumado), no por la suma de 43 mallas distintas. Es un resumen calculado para auditoría, no una nueva tasa oficial institucional ni de retención.

## Hito 3/3 · Entrega, límites y reanudación

**[B/C]** Entregados: script de lectura, resultados JSON, 43 filas agregadas, QA, manifiesto con hashes, especificación y estado Git. Los hashes de las ocho fuentes se comprobaron antes y después de la ejecución y no cambiaron.

**[E] Pendiente concreto de reproducción primaria:** el manifiesto H113 apunta a `5809_MATRICULA_AVANCE_CURRICULAR_2026_FINAL_SUBIR_SIES_ID_16768_21C.csv` como entrada validada. H113 regenera/formatea esa entrada y valida su dependencia con Carreras; no documenta allí el conteo completo desde PROMEDIOS. Deben recuperarse la cadena efectiva que produjo ese archivo, sus reglas y las resoluciones posteriores al paquete «2320 calculados / 51 pendientes». Los respaldos históricos de esa cadena sí aparecen inventariados en Git; no se declara que estén perdidos, ni que el motor haya quedado demostrado por validar solamente la salida.

**[B/E]** El supuesto script H112B archivado en Git es una nota que remite a `/tmp/h112b_generar_desde_hoja_10.py`, no un ejecutable recuperado. Para esta auditoría se reconstruyó independientemente la transformación descrita y se contrastó con el resultado. El script H112A completo sí está disponible y se leyó, sin ejecutar sus escrituras productivas.

**[C] Siguiente acción acotada:** recuperar el origen del conteo H113 y conciliarlo con sus 2.371 filas, reutilizando las 43 mallas ya comprobadas. Revisar solamente diferencias y reglas primarias, sin repetir el diccionario UMAS–SIES ni rehacer las búsquedas de títulos cerradas. Hasta entonces no marcar reproducción integral ni extender al histórico como si todas las reglas fueran A.

**[D]** Los tres análisis futuros permanecen separados: avance SIES anual, seguimiento T1/T2/T3 y aprobadas/reconocidas aplicables frente a la malla. La extensión histórica será interna; no acreditará cargas SIES de años no comprobados.

## Repetir los controles [C]

Desde el repositorio:

```sh
python3 outputs/avance_historico_fase1_20261027/reproducir_controles.py
```

**[C]** Requiere Python 3, openpyxl y acceso de lectura a las ocho rutas del manifiesto. Escribe únicamente las salidas agregadas de esta auditoría. No ejecuta scripts productivos, cambios Git ni cargas externas.
