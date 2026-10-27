# Búsqueda de eventos de plan, titulación y homologación · 26-10-2026

## Alcance y método

**[B/C]** Se consultaron los inventarios y respaldos gobernados del proyecto y se leyeron tres reportes institucionales de actividad de 2024: `CUMPLIMIENTO INGRESO CALIFICACIONES.xlsx` / `MASTER INGRESO 2024`; `PRUEBA CUMPLIMIENTO INGRESO CALIFICACIONES T3_2024.xlsx` / `DATOS CRUDOS U+ 19-11-2024`; y `Cumplimiento Ingreso de Notas.xlsx` / `Hoja1`. Rutas y SHA-256 en `RESULTADO_AGREGADO.json`. Se contrastó con las cuatro personas del estudio anterior y los 21 ramos pendientes.

**[C/E]** El vínculo de los cuatro casos usó CODCLI exacto con propietario único en la v11 y cuerpo de RUT igual. Estos reportes no corroboran el DV del estudiante de manera independiente. Los reportes pueden repetir filas; las repeticiones no son personas ni eventos adicionales.

## Cuatro personas

**[B/C]** Se localizaron filas de las cuatro personas en los reportes: las tres de Informática bajo `IINF20241` y la de Conectividad bajo `TCRE20241`. En las filas localizadas el campo de estado académico muestra `VIGENTE`. En el respaldo con fecha de reporte se observan registros entre el 27-05-2024 y el 19-11-2024; son fechas de observación y no fechas del evento de cambio.

**[B/C]** Esta evidencia refuerza que los cuatro expedientes posteriores tenían actividad en 2024, además de lo ya observado en PROMEDIOS y Datos Alumnos. La traza de titulación había elegido el expediente anterior. Los reportes académicos no registran el vínculo formal entre título y plan ni el acto administrativo de migración. No se localizó una bitácora con fecha efectiva de cambio o rechazo en los respaldos revisados **[E]**.

**[E]** Quedan los cuatro títulos sin atribución formal de plan. El plan posterior es una propuesta interna sustentada en actividad y estado, no una confirmación del plan formal del título. Para resolver documentalmente se requiere un registro de titulación que incorpore CODCLI y plan, o una bitácora formal de cambio con fecha efectiva y enlace al expediente.

## 21 ramos

**[B/C]** En los reportes de 2024 se localizaron tres códigos de ramo: `AG206IETMREOL`, `AG302IETMREOL` y `AS31TPAREOL`. Las filas encontradas los asocian a otros planes; la relación por archivo y plan está en `RESULTADO_AGREGADO.json`. Para los otros 18 no se localizaron filas en estos tres reportes. Ausencia en esta cobertura no demuestra que no se impartieran ni que no exista una homologación **[E]**.

**[E]** Las filas de actividad no documentan que esos ramos se homologaran en los planes en discrepancia. Los 21 permanecen pendientes de respaldo de equivalencia aplicable, conservando las coincidencias nominales y `RAMOEQUIV` del estudio anterior como pistas. La relación explícita del ramo 22 no se generaliza.

## Reproducibilidad y conservación

- `revisar_reportes_2024.py` verifica hashes y consulta la base v11 en modo lectura; `RESULTADO_AGREGADO.json` conserva solo datos agregados y las rutas de evidencia.
- El detalle de los cuatro expedientes queda fuera de Git con permisos 0600, en la ruta privada incluida en el resultado.
- No se cambiaron bases, el diccionario activo, denominadores o tasas. No se hizo commit ni push.
