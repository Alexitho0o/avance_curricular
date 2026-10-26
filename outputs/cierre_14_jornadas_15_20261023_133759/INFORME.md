# Cierre de 14 correspondencias y revisión de 15 jornadas

**D/C. Aplicados los 14 cierres autorizados** en la edición común `v2_20261023_14`: ocho anclas T1 con contexto histórico explícito y seis correspondencias por puente pasaporte–RUT. Se conserva v1, la decisión del usuario, fecha/hora, responsable Alexi, alerta de cambio y operaciones antes/después. Son correspondencias internas aprobadas; el campo documental y la aceptación SIES no se alteraron.

**C.** Las 35 observaciones del foco quedan en **14 reutilizables y 21 pendientes**. Dos enlaces de identidad P–RUT se añadieron al índice de consulta, conservando sus documentos originales; no se añadieron matrículas a las fuentes. Los tres consumidores locales usan el mismo puntero activo. No se afirma actualización de complementos remotos.

## Revisión adicional de T2/T3

**B/C.** Se contrastaron 15 observaciones de ocho personas contra 15 archivos adicionales: once respaldos de DatosAlumnos y las cuatro fotografías T2/T3 aportadas. Se recuperaron 33 filas del foco; cero conflictos de identidad. Los respaldos releídos se registran por hash, hoja y fila en el detalle privado. El inventario conserva también hojas sin llave individual; no se confunden tablas resumen con bases completas.

| Resultado | Observaciones | Clasificación |
|---|---:|---|
| Propuesta adicional respaldada: I162S2C1J2V4 para T3-2025 | 1 | B foto; C enlace; E adopción pendiente |
| Sin período de cambio inequívocamente acreditado | 14 | E |
| Total revisado; ninguno de estos 15 aplicado en este cierre | 15 | C |

**B/C. INF35-07:** MU2025 documenta I162S2C1J2V4; la hoja `T3_2025` del archivo Matrícula T3_2025 2.xlsx conserva jornada V para el mismo RUT y CODCLI. PROMEDIOS acredita el plan IINF20241 y actividad en período 3. Esto permite proponer reutilización interna de **J2V4 en T3-2025**, sin necesitar el día exacto de cambio. Los respaldos posteriores muestran O. No prueba envío SIES en T3 ni se extiende automáticamente a T2. La propuesta quedó sin aplicar: la autorización de cierre era para los 14 anteriores.

**B.** Siete de las ocho personas tienen `49 - CAMBIO DE JORNADA` en al menos un respaldo. Esto corrobora la existencia de una marca administrativa de cambio; no determina cuándo fue efectivo ni que sea el único cambio ocurrido. La octava tiene otras situaciones, no marca 49 en la cobertura revisada.

**B/E. INF35-10:** DA_4094 y DA_3194 registran V; DA_4490, DA_4649 y la foto T3-2025 registran O con marca 49. En todos se conserva FECHAMATRICULA=24-01-2025. Esa fecha no puede usarse como fecha de cambio: permanece igual pese a cambiar jornada/situación. Se ubicó el cambio entre respaldos, pero no permite adjudicar el T2-2025 pendiente. No se infiere la cronología por el número del archivo.

**B/E.** Los otros casos conservan desacuerdos de jornada entre MU, reportes históricos y reportes actuales. En algunos, el mismo plan IINF20241 aparece con D, V u O en distintas exportaciones. El nombre del plan no decide por sí solo versión ni jornada histórica. Los respaldos 2024 de notas confirman actividad/plan/fechas de cursos, pero no el código SIES o la fecha efectiva de migración de jornada.

**B/E.** Los archivos T2 aportados y T3-2026 no añaden coincidencias individuales para este foco; se revisaron las hojas con llaves. Esa ausencia se limita a esos listados y no acredita deserción. Las seis homologaciones TPAS fuera del foco de jornadas continúan pendientes y no fueron reclasificadas.

Ver `RESUMEN_JORNADAS_15.csv` para las ocho trayectorias, códigos T1 y respaldo por caso. Los identificadores y filas originales están únicamente en la carpeta privada declarada por el manifiesto.

## QA y conservación

**C.** 24.774 consultas comparadas entre v1/v2: exactamente 14 cierres; 24.760 respuestas restantes idénticas, salvo identificación de edición. Las dimensiones y códigos documentales originales no cambiaron. Tres consumidores locales: 35/35 respuestas iguales. Doce pruebas sintéticas correctas. Las consultas del foco siguen con 14 reutilizables y 21 pendientes. Las fuentes y el Excel V12 conservan sus hashes.

**C/E. QA OK_CON_ADVERTENCIAS:** las advertencias son la atribución documental pendiente y los destinos sin período acreditado; no hay un fallo de integridad abierto. Dos intentos de preparación se detuvieron antes de promover el puntero por controles del script (alcance del índice histórico y tipo textual de período); quedaron separados como intentos no promovidos. El intento final superó los controles completos antes de activar v2.

**D/C.** Bases, fórmulas, denominadores, tasas y Excel no modificados. Rama feature/ire-2026 y HEAD 80ca13a5a249a1a2bd53a699f5f73689b1f53040 conservados. Sin commit ni push.

**E. Reanudación:** valorar la propuesta acotada INF35-07/T3-2025 como correspondencia interna. Para los otros catorce destinos falta un registro de jornada aplicable al cierre/período, o un intervalo de cambio respaldado; no una nueva fórmula ni una equivalencia universal del plan. La versión de origen T1 permanece disponible para seguir la cohorte.
