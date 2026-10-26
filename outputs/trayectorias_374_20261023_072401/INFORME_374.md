# Fechas y versiones de las 374 personas — revisión dirigida

**B/C.** Se revisaron las 374 personas y 377 relaciones persona–familia de la entrega anterior. El foco contiene 3.320 observaciones del universo fijo de 24.774; 3.162 pertenecen a las relaciones múltiples seleccionadas y 158 corresponden a otros contextos de las mismas personas. No se cambiaron bases, códigos adoptados, reglas ni denominadores. No hubo commit/push.

## Qué versión se puede confirmar

| Estado de las observaciones del foco | Cantidad | Alcance |
|---|---:|---|
| Código MU anual atribuible al expediente | 2.942 | B/C: código anual documentado; no prueba automáticamente cada trimestre de plan |
| Código anual único, expediente todavía ambiguo | 83 | B código; E atribución |
| Sin código anual localizado | 295 | E; no equivale a ausencia universal |
| Total | 3.320 | C |

Por persona (categorías excluyentes): **251** tienen todas sus observaciones con código anual atribuible, **116** están parcialmente cubiertas y **7** no tienen observación atribuida. Total 374. No son nuevos cierres: reproducen el estado documental anterior dentro del foco. Los indicadores globales siguen en 1.838 personas pendientes documentales y 1.751 internas. La temporalidad efectiva del plan es una pregunta adicional, no una redefinición de esos indicadores.

**B/C.** En las 377 relaciones: 360 muestran un código único a través de los años documentados, 12 un cambio entre años y cinco no tienen código MU localizado. Ninguna muestra dos códigos distintos en el mismo año dentro de la evidencia MU revisada. Una persona aparece en más de una familia en tres relaciones adicionales; no sumar familias como personas únicas.

| Familia SIES | Personas en familia | Un código observado | Cambio entre años | Sin código |
|---|---:|---:|---:|---:|
| I162S2C1J1 | 1 | 1 | 0 | 0 |
| I162S2C1J2 | 7 | 6 | 1 | 0 |
| I162S2C1J4 | 56 | 53 | 3 | 0 |
| I162S2C3J2 | 3 | 2 | 1 | 0 |
| I162S2C3J4 | 66 | 62 | 2 | 2 |
| I162S2C46J4 | 70 | 65 | 3 | 2 |
| I162S2C47J4 | 44 | 44 | 0 | 0 |
| I162S2C57J4 | 104 | 103 | 0 | 1 |
| I162S2C6J2 | 2 | 1 | 1 | 0 |
| I162S2C6J4 | 24 | 23 | 1 | 0 |

El archivo VERSIONES_POR_PERIODO_AGREGADAS.csv muestra carrera, jornada, etiqueta de plan, año/período UMAS y código **anual** documentado, sin identificadores. El registro privado conserva los localizadores de las filas fuente y el estado de cada observación. No se rellena un código anual ausente con el de otro año.

## Fechas y cambios de plan

**B/C.** Se reconstruyeron 756 combinaciones expediente–plan dentro de las relaciones y 381 pares. Hay 357 pares con años de actividad disjuntos; 20 coinciden en un año pero usan regímenes no comparables; dos comparten períodos del mismo régimen; dos tienen períodos distintos dentro del mismo año y régimen. Los dos solapamientos persisten al separar convalidaciones/homologaciones. «Sin marca de reconocimiento» describe el reporte, no acredita asistencia o matrícula vigente.

**B.** Los segmentos contienen 369 regímenes bimestrales, 368 trimestrales y 19 semestrales. No se equipara período 1 bimestral con trimestre 1, ni período UMAS con semestre SIES sin una regla documentada. **E:** secuencia observada o ausencia de solapamiento no prueba la fecha efectiva de migración.

**B/C.** Se compararon 7.930 unidades de asignatura/año/período/expediente presentes tanto en PROMEDIOS 7804 como en 12166: las 7.930 mantienen el mismo conjunto de etiquetas de plan. Se leyeron 17.599 y 8.109 filas de asignaturas del foco, respectivamente; diferencia de cobertura no se interpreta como bajas. Esta comparación no revela cambios de etiqueta entre esos reportes, pero tampoco demuestra que nunca hubiese un cambio previo o que la etiqueta corresponda históricamente a cada nota.

**B.** En 752 de los 756 segmentos se encuentran contextos concordantes en los tres DATOSDEALUMNOS; cuatro no tienen contexto exacto de expediente/carrera/sede/jornada localizado. Entre los contextos disponibles no se encontraron diferencias en ANOINGRESO, PERIODOINGRESO, FECHAMATRICULA, ANOMATRICULA ni PERIODOMATRICULA. Sus cortes efectivos de extracción no están acreditados, por lo que no se ordenan como una secuencia fechada solo por el nombre del archivo.

**B.** La matrícula MU del foco tiene 1.255 filas: 777 con fecha de matrícula interpretable y ninguna fecha no vacía pendiente de interpretación. Los años históricos y 2022–2023 carecen de ese campo en las fuentes leídas. Fecha de matrícula/renovación, fecha de firma, ingreso declarado, actividad académica y asignación efectiva de plan se mantienen separados.

## Las 12 trayectorias donde cambia el código

**B/C.** Los cambios se conservan con último año observado del código anterior, primer año observado del siguiente y años intermedios sin evidencia. Diez cruzan el tramo de fuentes históricas publicadas hasta 2021 frente a la base derivada desde 2022; dos ocurren dentro de la base 2022–2026. Esto describe procedencia, no demuestra que el cambio se deba a la fuente ni que sea un error.

El detalle agregado está en CAMBIOS_VERSION_ANUAL_AGREGADOS.csv; CAMBIOS_VERSION_ANUAL.json/CSV privado identifica cada trayectoria y conserva sus evidencias. **E:** el intervalo entre dos observaciones no es una fecha efectiva de cambio. No se renumera V1/V2/V3 ni se traslada el código posterior hacia atrás.

## Cuatro pistas adicionales de atribución por fecha

**B/C.** Cuatro observaciones de cuatro personas, antes ambiguas entre expedientes de la misma familia, tienen una fecha de matrícula MU que coincide exclusivamente con un expediente en los tres DATOSDEALUMNOS:

| Carrera interna | Año | Código MU coincidente | Observaciones |
|---|---:|---|---:|
| IECIREOL | 2024 | I162S2C1J4V2 | 2 |
| TPAREOL | 2024 | I162S2C57J4V1 | 2 |

Las fechas, filas y alternativas están en CUATRO_PISTAS_FECHA.csv privado. La coincidencia respalda qué matrícula interna puede estar asociada a la fila MU; **no acredita la vigencia del plan en todas las actividades de ese año**. Esos casos tienen también expedientes IINF o TPAS con régimen trimestral; los expedientes coincidentes son bimestrales. No se fuerza una correspondencia entre sus períodos.

**C. Control:** la coincidencia de fecha exclusiva también aparece en 185 observaciones ya atribuibles, correspondientes a 95 personas y 98 filas MU. Todas concuerdan con su código documentado. No son 185 pruebas independientes: se repiten personas y fuentes. **E/D:** usar esta pista como regla nueva de cierre requiere formalizar su alcance; aquí se registra, no se adopta ni cambia el estado vigente.

## Fuentes, recuperación y evidencia faltante

Se utilizaron PROMEDIOS 12166 y el respaldo idéntico del 7804, DATOSDEALUMNOS 12159/11248 y respaldo del 11998, matrícula histórica MAT 2010–2021, BASE_RETENCION_MU 2022–2026, mapas de familias vigentes y la documentación de planes/temporalidad. Se preservan fuente/hoja/fila y hashes.

**B.** PROMEDIOS 7804 en Descargas tiene hash distinto al manifiesto; DATOSDEALUMNOS 11998 ya no está en esa ruta. Se recuperaron ambos desde el respaldo Caracterizacion_anual_2026_20261015_130336_379868, con hashes exactamente iguales a los gobernados. RELOCALIZACION_FUENTES.json documenta las sustituciones de ubicación, sin alterar ni reemplazar los originales.

**E.** Falta evidencia con CODCLI/carrera/plan anterior/nuevo y fecha efectiva (o matrícula/plan/período con esa semántica acreditada), además del linaje de PLAN_DE_ESTUDIO del reporte. La documentación gobernada identifica RA_CARGA_RASTRO y registro de asignaturas como candidatos, pero no acredita que los extractos disponibles contengan esa historia. La búsqueda dirigida por nombres en los repositorios, Descargas y Escritorio no localizó un extracto identificado de esos eventos; no se afirma inexistencia universal. No se completa el vacío con el sufijo del plan ni con totales.

## QA y preservación

Distribuciones: 360+12+5=377; 2.942+83+295=3.320; 251+116+7=374; 357+20+2+2=381. Todas las observaciones conservan los códigos documentales e internos anteriores; cero duplicaciones por unión. Hashes de fuentes conservados, Git sin cambio de rama o HEAD. El detalle individual permanece fuera de Git en /Users/alexi/.local/share/ipss/trayectorias_374_20261023_072401; el repositorio solo contiene código, documentación y agregados.

No se modificó ningún Excel anterior ni sus gráficos, tablas, tasas o denominadores. Esta entrega es un diagnóstico dirigido con CSV/JSON reproducibles. No confundir QA técnico correcto con cierre de la asignación histórica. El estudio identifica los códigos anuales que sí se pueden respaldar y deja delimitados los 83 casos de atribución y las 295 ausencias de evidencia anual, junto con cuatro pistas nuevas revisables.
