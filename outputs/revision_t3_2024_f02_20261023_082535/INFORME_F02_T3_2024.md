# Respaldo T3-2024 recuperado: revisión de la persona F02

**Resultado:** se resolvió el acceso al respaldo y se confirmó el plan observado de F02 en T3-2024. No se acreditó la fecha administrativa exacta de cambio de plan. Se conserva el registro del plan anterior y no se modifican las bases, versiones adoptadas ni denominadores.

Proceso: conciliación histórica UMAS–SIES del puente de retención IPSS 162. Referencia: matrícula y actividad académica de 2024. No es recálculo de retención ni aplicación de reglas MU2027. No hay una regla A nueva: B identifica datos, C identifica el cruce, D conserva la decisión de no alterar indicadores y E mantiene lo no demostrado.

## 1. Respaldo íntegro y disponible — B/C

`PRUEBA CUMPLIMIENTO INGRESO CALIFICACIONES T3_2024.xlsx`: 1.253.761 bytes. SHA-256 recalculado:

`97c0fc4fbe4dd9a24be611d0960f4ad6c1559db907a9d86d12a039bc89110fa6`

Coincide con el hash anterior. Se leyeron íntegramente sus tres hojas:

| Hoja | Lectura | Uso |
|---|---:|---|
| RESUMEN | 63 filas no vacías en un rango de 160×13 | Resumen inspeccionado; no llave individual |
| DATOS CRUDOS U+ 19-11-2024 | 4.155 registros, 27 columnas | CODCLI + cuerpo de RUT corroborado; plan y fechas |
| ERRORES | 3 registros, 25 columnas | Ninguno corresponde a las 16 personas del foco |

Los RUT de estudiantes se corroboraron con sus CODCLI; el campo DIG del docente no se utilizó. Se localizaron 43 filas de 12 personas del foco anterior, sin nuevos expedientes no reconocidos. Las 43 reproducen observaciones del maestro en los campos contrastados (expediente, plan, carrera, año/período, asignatura, sección, fechas y estados). No se cuentan como 43 evidencias independientes nuevas ni se afirma identidad total de ambos libros.

## 2. Qué confirma para F02 — B/C

- Seis asignaturas bajo **IINF20241**, ANO=2024 y PERIODO=3.
- FECHA MEDICION = **19-11-2024**.
- FECHAINICIO = **14-10-2024** y FECHAFIN = **04-01-2025** para las seis asignaturas. Son fechas de asignaturas, no de cambio de plan.
- Las seis observaciones coinciden con las ya leídas en `CUMPLIMIENTO INGRESO CALIFICACIONES.xlsx`, hoja `MASTER INGRESO 2024`. El respaldo confirma lo observado, pero no agrega una fecha anterior.
- La primera FECHA REPORTE localizada con IINF20241 sigue siendo **27-05-2024**, en el maestro. Esto confirma que el reporte lo vincula al plan nuevo en esa fecha; no demuestra que el cambio ocurriera exactamente ese día.

## 3. Por qué no se debe borrar el plan anterior — B/C

Se releyeron cinco rutas de PROMEDIOS, incluyendo dos copias idénticas de PROMEDIOS7804. El expediente anterior conserva **una asignatura** en 2024-2, régimen **BIMESTRAL**, plan **IECIREOL20211**:

`AS101IECIREOL — HABILIDADES PARA EL APRENDIZAJE DIGITAL`, APROBADO, nota 4,3, sin marca de convalidación en esas filas.

Está en PROMEDIOS7804, Hoja1 fila 24336, y PROMEDIOS12166, Hoja1 fila 27236. Son dos observaciones de una misma asignatura; las dos rutas con el mismo hash de PROMEDIOS7804 no se cuentan dos veces. No se infiere la fecha del evento a partir del corte o del nombre de estos archivos.

La presencia de esa asignatura impide sustituir automáticamente todos los registros de 2024 por IINF20241. Tampoco autoriza convertir el período bimestral 2 en el trimestre 2 del plan nuevo.

## 4. Cronología comprobable y límite

| Fecha/período | Observación | Clasificación y límite |
|---|---|---|
| 22-04-2024 | FECHAMATRICULA del expediente IECIREOL | B/C; no acredita fin del plan anterior |
| 24-04-2024 | FECHAMATRICULA del expediente IINF | B/C; no acredita por sí sola una migración |
| 27-05-2024 | Primera FECHA REPORTE localizada con IINF20241 | B/C; primera observación fechada localizada del plan nuevo |
| 2024-2 bimestral | Una asignatura aprobada bajo IECIREOL20211 | B; no consta día de asignación/cierre del plan |
| 19-11-2024 | Seis asignaturas del período 3 bajo IINF20241 | B/C; confirmación del respaldo T3 |
| Día efectivo del cambio | No consta en los campos leídos | E; no se elige 24-abril ni 27-mayo como fecha de migración |

Las dos fechas de matrícula están declaradas para expedientes distintos, no constituyen por sí solas un intervalo de cambio de plan. La semántica histórica de FECHAMATRICULA y el linaje temporal de PLAN_DE_ESTUDIO siguen limitados por el contrato gobernado; ver `docs/fase_4_planes_asignaciones_umas.md`, sección “Qué se sabe de la vigencia”.

**Conclusión:** puede confirmarse **IINF20241 como plan observado en el respaldo T3**, y desde la fecha declarada de reporte 27-mayo en el maestro. No puede confirmarse el día exacto en que dejó IECIREOL20211 ni trasladar automáticamente una versión SIES a todos los períodos. MU2024 conserva su código anual documentado **I162S2C1J4V2**; no se demostró un cambio adicional de versión SIES por este hallazgo.

## 5. Preservación, QA y reanudación

**D:** se conservan 5.901 personas, 6.622 expedientes y 24.774 observaciones. No se reducen pendientes globales por llamar “resuelta” a una corroboración parcial. Ninguna fuente, base, tasa ni código adoptado fue modificado.

**C:** QA técnico OK: lectura de las tres hojas, identidad corroborada, cero alertas de cruce, seis filas F02 contrastadas con maestro, dos observaciones de una sola asignatura antigua, hashes de entradas y de la entrega anterior conservados. **E:** la fecha efectiva sigue pendiente documental; QA técnico no la convierte en confirmación funcional.

Detalle restringido y localizadores fuente/hoja/fila: carpeta privada indicada en MANIFEST.json, especialmente F02_T3_DETALLE.csv, F02_PROMEDIOS_RELECTURA.json y F02_CRONOLOGIA_FUENTES.json. Los datos personales permanecen fuera de Git. El respaldo original no se mueve ni sobrescribe.

Reanudación precisa: si se localiza un registro de asignación/migración con CODCLI, plan anterior/nuevo y fecha efectiva, contrastarlo con esta secuencia. El error de lectura T3 está resuelto; no volver a solicitar ese archivo ni confundirlo con la evidencia administrativa que aún falta. No es necesario repetir los 16 cruces ni la búsqueda completa de versiones.

Sin commit, push, merge, PR ni cargas externas. Rama feature/ire-2026, HEAD 80ca13a5a249a1a2bd53a699f5f73689b1f53040 antes y después.
