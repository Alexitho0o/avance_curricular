# Búsqueda en respaldos históricos adicionales · 26-10-2026

## Alcance

**[B/C]** Se revisaron dos respaldos del proyecto no contrastados específicamente para estos cuatro casos y 21 ramos: `auditoria_plan_estudios_alumno_completa.tsv` (2.587 filas) y `03_fuente_Hoja1.csv` (292 filas), ambos bajo `archive/cleanup/cutoff_2026-04-15/moved 3/resultados/`. Rutas exactas y SHA-256 en `RESULTADO_AGREGADO.json`. No se consideran registros de actividad equivalentes a un acto de titulación u homologación.

## Título, CODCLI y plan

**[B/C]** El cruce literal de CODCLI de los cuatro casos con la auditoría de planes encontró **tres personas**: los tres expedientes posteriores aparecen como carrera `IINF`, plan `IINF20241`, con año de ingreso actual 2022 y estado heredado de auditoría `MATCH_SIES`. Este último es un resultado técnico histórico; no es comprobante de aceptación ni declara que el título pertenezca a ese plan. La cuarta persona no se localizó en esta auditoría; no se infiere ausencia en otras fuentes **[E]**.

**[E]** El archivo no contiene la fecha ni el vínculo formal título–CODCLI–plan. La asociación refuerza el dato de plan ya observado, pero las cuatro atribuciones de título continúan pendientes. El informe de Docencia y la traza calculada se revisaron previamente; no se modificaron.

## 21 ramos

**[B/C]** En la muestra histórica de 292 filas se encontró uno de los 21 códigos: `AS31TPAREOL`, con `RAMOEQUIV=AS31TPAREOL`, estado de asignatura `A` y plan observado `TPAREOL20211`. La discrepancia a resolver corresponde al plan `IECIREOL20211`. La actividad en el otro plan no acredita una homologación al plan pendiente **[E]**.

**[E]** Los otros 20 códigos no se localizaron en esta muestra; esto no prueba ausencia en todo el histórico. No se añadió ninguna equivalencia a las 19 referencias de otros planes ya documentadas ni se cerraron los 21 ramos.

## Reproducción y conservación

`revisar_archivo_historico.py` ejecuta los cruces en memoria, verifica hashes antes y después de la lectura y genera `RESULTADO_AGREGADO.json` sin identificadores personales. No se cambiaron fuentes, bases, diccionario, denominadores ni tasas. No se hizo commit ni push.
