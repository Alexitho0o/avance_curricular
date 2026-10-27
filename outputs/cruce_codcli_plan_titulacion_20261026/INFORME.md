# Cruce por CODCLI entre expedientes y planes · 26-10-2026

**[C] Método.** Se tomaron los dos CODCLI del caso que aparecen en `DATOSDEALUMNOS ORIGEN DE LOS DATOS2025.xlsx`, hoja `BBDD`, y se buscaron por igualdad exacta en cuatro respaldos de actividad, sin exigir coincidencia de RUT. Los códigos individuales se trataron solo en memoria. La coincidencia de CODCLI identifica el mismo valor de expediente en las fuentes; por sí sola no verifica de forma independiente a su propietario **[E]**.

| Fuente [B] | Resultado de la búsqueda por CODCLI [B/C] |
|---|---|
| `PROMEDIOSDEALUMNOS_12166.xlsx`, `Hoja1` | Ambos CODCLI: expediente de `TTMRE` con plan `TTMRE20211`, actividad 2022–2023; expediente de `TCRE` con plan `TCRE20241`, actividad 2024. En total se localizaron 17 filas de asignaturas, no 17 personas. |
| `CUMPLIMIENTO INGRESO CALIFICACIONES.xlsx`, `MASTER INGRESO 2024` | CODCLI del expediente `TCRE` con plan `TCRE20241`, en los períodos nativos 1, 2 y 3 de 2024. |
| `PRUEBA CUMPLIMIENTO INGRESO CALIFICACIONES T3_2024.xlsx`, `DATOS CRUDOS U+ 19-11-2024` | El mismo CODCLI y plan `TCRE20241`, período 3 de 2024. |
| `Cumplimiento Ingreso de Notas.xlsx`, `Hoja1` | El mismo CODCLI y plan `TCRE20241`, período 3 de 2024. |

**[B/C]** Los respaldos pueden repetir asignaturas y proceden de información institucional relacionada; no se suman como estudiantes ni se presentan necesariamente como fuentes independientes. `RESULTADO_AGREGADO.json` registra por fuente el número de filas y los períodos, junto con rutas y hashes.

**[E] Alcance de la confirmación.** El cruce confirma qué plan aparece en los registros de actividad asociados a cada CODCLI. El título revisado en la carga no declara CODCLI ni plan, y el código SIES es compartido por ambos expedientes; por tanto, la coincidencia de CODCLI con actividad no demuestra por sí sola cuál plan quedó formalmente vinculado al título. Tampoco acredita la fecha efectiva de cambio de plan. El origen y desempate del puntaje 2130 siguen pendientes.

**[C] QA y conservación.** `revisar.py` verifica los hashes antes y después, busca CODCLI sin filtro previo de RUT y evita escribir los identificadores personales en la salida agregada. Se conservaron fuentes, bases, diccionario, tasas y denominadores. Sin commit ni push.
