# Contextos H113 con expediente conocido y período no indexado

## Resultado ejecutivo

[B/C] Se reprodujeron los **815 contextos** señalados en la auditoría anterior. Afectan a **341 personas**, **477 expedientes persona–CODCLI–carrera** y **342 filas H113**. El universo de precarga permanece en **2.371 filas**, y el foco original de revisión en **489 filas**. Los contextos no equivalen a estudiantes ni a denominadores de retención.

[B/C] **644 contextos tienen coincidencia concordante**: mismo RUT con DV, CODCLI, plan UMAS, carrera y jornada que un contexto ya respaldado del mismo año, y un único código coincidente en MU de ese año. Representan **316 personas y 375 expedientes**; no deben sumarse con los conteos de los demás grupos porque pueden solaparse.

[C/E] Son candidatos a ampliar el índice del diccionario, no nuevas atribuciones aprobadas. La comprobación no trasladó códigos desde años anteriores o posteriores, no modificó decisiones D y no certifica aceptación SIES ni la fecha efectiva del plan. No se aplicaron asignaciones.

| Resultado excluyente | Contextos | Clasificación |
|---|---:|---|
| Coincidencia de contexto anual y código MU, verificada en fuente | 644 | B/C; extensión de período propuesta C/E |
| Código MU anual único en la familia, sin contexto concordante del mismo año | 107 | B/C/E |
| MU del año solo presenta otra familia respecto de carrera/jornada buscadas | 23 | B/C/E |
| Sin MU del año en el índice revisado | 38 | E; no significa ausencia universal |
| Jornada sin familia en el mapeo utilizado | 3 | E |
| **Total** | **815** | **B/C** |

[B/C] Los **171 restantes** no cumplen la coincidencia completa. Se mantienen separados de los otros pendientes detectados en la auditoría anterior: este análisis solo revisa el bloque de 815.

## Qué se comprobó y qué no

[C] Se reutilizó la extracción del foco de la auditoría anterior y el consumidor común de la edición **v11_20261026_86_promedios_integrada**. El análisis agrupó actividad de Hoja1 de PROMEDIOS 7804 por identidad completa, CODCLI, plan, carrera, jornada, año y período. Se consultó el diccionario sin escribir en él.

[B/C] Para los 644 candidatos no se observaron otros planes, carreras o jornadas en las filas académicas anuales A/E/I/R del mismo expediente en PROMEDIOS 7804, ni otro plan de la carrera en el índice anual, ni otro CODCLI de la persona con ese código atribuido en el año dentro del índice. La afirmación queda limitada a esas fuentes y filtros; no demuestra que nunca existió una migración.

[E] PROMEDIOS aporta plan y jornada, pero no acredita por sí solo sede histórica ni fecha efectiva de un cambio. El componente de sede procede del código MU y del contexto ya atribuido, junto con el mapeo gobernado. Por eso la coincidencia es evidencia para una propuesta de extensión contextual, no prueba independiente de la sede en cada fecha.

[E] PLAN_ESTUDIOS numérico de la precarga SIES y PLAN_DE_ESTUDIO UMAS no son intercambiables. Sigue pendiente acreditar su relación para validar completamente el cálculo curricular. Tener el mismo código SIES tampoco autoriza a incorporar automáticamente reconocimientos de otras carreras al plan destino.

## Verificación contra archivos fuente

[B/C] Se releyeron **550 referencias distintas de hoja/fila** en cuatro archivos y se comprobaron **751 enlaces** de identidad, año y código completo. **Cero diferencias finales** entre el índice y las filas fuente. La base 2022–2026 es derivada: su procedencia primaria se conserva en MANIFEST_BASE_RETENCION_MU_2022_2026.json; no se presenta como prueba de aceptación ministerial.

| Fuente | Referencias distintas | Clasificación |
|---|---:|---|
| BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx, BASE_RETENCION_MU | 514 | B/C |
| MAT_IP_CIISA_2021.xlsx, MAT_2021 | 20 | B/C |
| MAT_IP_CIISA_2020.xlsx, MAT_2020 | 11 | B/C |
| MAT_IP_CIISA_2019.xlsx, MAT_2019 | 5 | B/C |
| **Total** | **550** | **B/C** |

[C] El primer verificador produjo 66 diferencias técnicas porque comparó MAT_2019/MAT_2020/MAT_2021 con el año numérico del índice. Se corrigió únicamente el lector de auditoría para reutilizar la normalización ya existente en scripts/reproducir_puente_20261023.py:138. La relectura dejó cero diferencias. Se conservan QA_LECTOR_INICIAL.json e INCIDENCIA_LECTOR.json; no se corrigieron datos fuente para hacer coincidir los resultados.

## Distribución de los 644 candidatos

| Año académico | Contextos candidatos | Clase |
|---|---:|---|
| 2019 | 6 | B/C/E |
| 2020 | 23 | B/C/E |
| 2021 | 37 | B/C/E |
| 2022 | 93 | B/C/E |
| 2023 | 303 | B/C/E |
| 2024 | 73 | B/C/E |
| 2025 | 109 | B/C/E |
| **Total** | **644** | **B/C/E** |

[B/C] Estos contextos reúnen 1.386 filas de actividad en la selección utilizada. Dentro de 2025 son 203 filas A/R. No son 1.386 estudiantes ni un denominador nuevo. El desglose por código completo está en CANDIDATOS_POR_CODIGO.csv.

[B/C] Los 815 contextos conservan los períodos UMAS originales: 1=160; 2=166; 3=172; 4=256; 5=61. No se renombraron como trimestres ni se aplicó una conversión de calendario.

## QA, preservación y reanudación

[B/C] **34 controles correctos; PASS_AUDITORIA_PARCIAL**. Se validan foco, partición, hashes, referencias fuente y preservación del diccionario privado, fuentes, cuatro cambios ajenos preexistentes, rama y HEAD. No es certificación completa del avance curricular ni de una carga SIES.

[B/C] Rama feature/ire-2026; HEAD antes/después **262f445828f7e939fac59c3cc76d0bb20a101746**. Sin cambios a bases, denominadores, motor, diccionario o archivos originales. Sin Excel nuevo, commit, push ni publicaciones. Las salidas son agregadas y los identificadores solo se procesaron en memoria.

[C/E] El siguiente paso acotado es evaluar la ampliación del índice para los 644 candidatos con este alcance exacto, sin cambiar el nivel de respaldo ni presentarlos como un envío acreditado. Para los 171 restantes, priorizar los 107 con código anual único: falta el enlace de contexto del mismo año, no volver a buscar sus códigos desde cero. No reabrir los cierres de títulos ni las homologaciones individuales aprobadas.

[C] Reproducción desde la raíz del repositorio:

```sh
python3 outputs/avance_historico_periodos_815_20261027/revisar_periodos.py
```

[C] El comando recalcula resultados, verificación y QA. El informe resume esos resultados. MANIFEST.json y VERIFICACION_FUENTES_Y_CONTEXTO.json registran rutas completas y SHA-256, incluyendo el lector previo reutilizado y las cuatro fuentes MU.
