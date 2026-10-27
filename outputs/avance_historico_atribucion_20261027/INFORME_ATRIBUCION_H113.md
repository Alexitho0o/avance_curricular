# Atribución de actividad académica H113 por expediente y contexto

## Contexto y alcance

[B/C] Proceso: Avance Curricular 2026, datos académicos anuales de 2025 y acumulados hasta 2025. Repositorio avance_curricular, rama feature/ire-2026. Esta auditoría continúa la reconstrucción del cálculo histórico; no es un nuevo cálculo de retención.

[D] Se conserva el universo de 2.371 filas de precarga y se examinan las 489 filas previamente alertadas como multicarrera. No se modifican fuentes, bases, denominadores, motor ni diccionario. No se crea Excel ni se realizan commit o push.

## Resultado ejecutivo

[B/C] Las 489 filas corresponden a 488 personas, 1.032 expedientes persona–CODCLI–carrera y 5.144 contextos únicos consultados. Son unidades diferentes y no deben sumarse. Al usar documento completo y DV, 19 filas dejan de ser multicarrera; 470 conservan actividad en varias carreras. Todas las filas del foco tienen actividad con identidad exacta.

| Resultado de la atribución anual 2025 | Filas H113 | Clasificación |
|---|---:|---|
| Toda la actividad anual A/R tiene el mismo código SIES que la fila objetivo | 173 | B/C, reutiliza respaldo documental o D aprobado |
| Parte de la actividad anual tiene atribución pendiente | 288 | B/C/E |
| Actividad anual con códigos respaldados distintos del objetivo, sin pendiente de código | 1 | B/C/D |
| Sin unidades anuales A/R observadas en la selección exacta | 27 | B/C; no demuestra ausencia de matrícula |
| Total del foco | 489 | B/C |

[E] Las 173 filas confirman la atribución del código para la actividad anual examinada, no una validación completa del cálculo curricular. Aún hay que acreditar la relación entre el nombre de plan UMAS y PLAN_ESTUDIOS numérico de la precarga, y la aplicación de reconocimientos al plan destino. No se adoptaron 173 cierres nuevos del diccionario.

[B/C] En el acumulado: 39 filas tienen toda la actividad atribuida al mismo código; 448 tienen algún contexto pendiente y 2 tienen códigos completos con cambios, sin pendiente de código. Es una partición distinta de la anual.

## Reutilización del diccionario y origen de los pendientes

[B/C/D] Se consultó la edición v11_20261026_86_promedios_integrada: 3.109 contextos devolvieron respaldo documental anual atribuido, 17 correspondencia interna aprobada y 2.018 pendiente. No se asignaron versiones por mayoría, nombre o totales ni se propagaron códigos entre períodos.

[B/C] De los pendientes, 1.578 contextos únicos no se localizaron con la consulta exacta:

| Diagnóstico en el índice vigente | Contextos | Clasificación |
|---|---:|---|
| Persona y CODCLI presentes, pero año/período no indexado | 815 | B/C |
| Persona y CODCLI no indexados conjuntamente | 762 | B/C |
| Año/período y plan presentes, con otra carrera en el índice | 1 | B/C/E |
| Total | 1.578 | B/C |

[E] «No indexado» describe el diccionario consultado, no la ausencia de la persona o de su actividad en las fuentes. Los demás pendientes incluyen falta de evidencia anual aplicable, atribución múltiple, sede histórica, jornada no confirmada por el mapeo y homologación en plan rechazado. RESULTADOS.json conserva el detalle: los motivos contados por referencia de fila H113 no equivalen a contextos únicos ni personas.

## Conciliación matemática del foco

[C] Para aislar el efecto del enlace se mantiene el conteo histórico de filas de asignatura: anual A/R cursadas y A aprobadas; acumulado A/E/I/R cursadas y A/E/I aprobadas. Estas son operaciones reproducidas del código histórico, no nuevas reglas oficiales. Los aportes pueden reutilizar un contexto en más de una fila H113; no son asignaturas únicas institucionales.

| Atribución respecto del código objetivo | Cursadas 2025 | Aprobadas 2025 | Cursadas acumuladas | Aprobadas acumuladas | Clase |
|---|---:|---:|---:|---:|---|
| Mismo código completo | 2.551 | 2.221 | 12.002 | 11.112 | B/C/D |
| Otra versión de la misma familia | 0 | 0 | 181 | 151 | B/C/D |
| Otra familia | 16 | 15 | 2.466 | 2.246 | B/C/D |
| Pendiente de atribución | 1.729 | 1.556 | 7.132 | 6.529 | B/C/E |
| Total con identidad completa | 4.296 | 3.792 | 21.781 | 20.038 | B/C |
| H113 original, mismo foco | 4.425 | 3.899 | 22.291 | 20.515 | B |
| Diferencia del escenario frente a H113 | −129 | −107 | −510 | −477 | C; no aplicada |

[E] Actividad en otra carrera o versión histórica no se descarta automáticamente: podría corresponder a reconocimientos válidos, que necesitan evidencia aplicable al plan destino. Los pendientes no se reemplazan por cero. No se calcula ni corrige una tasa en esta auditoría.

## Fuentes, reproducción y QA

[B/C] MANIFEST.json registra las rutas completas y SHA-256 de PROMEDIOSDEALUMNOS_7804.xlsx (actividad Hoja1), precarga 5809, H113 y H114B; también del mapeo grupos_existentes.json y la edición privada del diccionario. El foco de 489 se reproduce con las cinco hojas y la selección histórica; la atribución exacta usa solo filas de actividad de Hoja1 y documento completo con DV. PARTICION_POR_CODIGO.csv conserva el desglose agregado por código completo.

[C] Reproducción desde la raíz del repositorio:

```sh
python3 outputs/avance_historico_atribucion_20261027/auditar_atribucion.py
```

[B/C] Los 24 controles de QA pasan: hashes, universo, particiones anuales/acumuladas, suma de unidades, consultas únicas, preservación de fuentes y de los cuatro archivos modificados previamente, rama y HEAD. Estado: PASS_AUDITORIA_PARCIAL. No equivale a aprobación de una carga ni a validación completa de todas las reglas curriculares.

[B/C] HEAD antes y después: 262f445828f7e939fac59c3cc76d0bb20a101746. Las salidas solo contienen agregados; los identificadores se procesaron en memoria. No se alteraron decisiones anteriores ni se publicaron datos.

## Reanudación acotada

[C/E] Priorizar los 815 contextos con expediente ya conocido: comprobar si la evidencia anual existente permite indexar ese período con el mismo plan y contexto, sin heredar automáticamente el código. Después revisar los 762 expedientes no indexados y la discrepancia de carrera. Antes de adoptar cambios, separar atribución de código, relación de plan y reconocimientos de asignaturas.

[E] El caso P con 12 unidades sin respaldo reproducido permanece en el informe previo de identidad; no pertenece a este foco y no se repitieron sus búsquedas. No se reabren los títulos ni los reconocimientos individuales ya aprobados.
