Fase 4/4 · Hito 3/3 — entrega local con pendientes E

# Retención intermedia IPSS 162

Fecha/hora de cierre documental: 2026-10-21T15:02:21.734855-03:00.

B/C: se verificó y reutilizó el cierre local de las 13:32, que ya tenía manifiesto, bitácora, prompt y QA. No se ejecutó finalize.py porque habría sobrescrito ese cierre. Los tres temporales indicados existen, pero la evidencia persistente es la autoridad de reanudación. La ampliación de esta entrega es el Excel privado completo, separado del agregado.

## Archivos

- B: agregado conservado: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/retencion_intermedia_t2_t3/20261021_133221/RETENCION_INTERMEDIA_IPSS_REVISION_20261021_133221.xlsx`.
- B: copia idéntica de Escritorio: `/Users/alexi/Desktop/RETENCION_INTERMEDIA_IPSS_REVISION_20261021_133221.xlsx`.
- B: SHA-256 agregado y Escritorio: `66e7cc11a0206793504e4eb275d8585e070413067df6f20b9fde234d3daaa54c`.
- B/C: detalle privado: `/Users/alexi/Documents/GitHub/avance_curricular/.local_restricted/retencion_intermedia/20261021_144031/DETALLE_PRIVADO_RETENCION_INTERMEDIA_20261021_144031.xlsx`.
- B: SHA-256 detalle privado: `a099965d65e9c31d1852bd405819c21a761fc2cba5f069eaa76e7c758a947db3`.
- C: el detalle está en `.local_restricted`, excluido por `.gitignore:76` antes de escribir. Directorios 0700 y archivos 0600. No se copió al Escritorio ni se envió a servicios externos.

## Cuatro cierres

| Cohorte D | Cierre | Denominador C/D | Presencias B/C | VIGENTE observado B/C | Filas coincidentes B/C | Tasa E |
|---|---|---:|---:|---|---:|---|
| 2024 | 2025-T2 | 558 | 1 | 1 | 1 | Pendiente |
| 2024 | 2025-T3 | 558 | 325 | 317 | 328 | Pendiente |
| 2025 | 2026-T2 | 1.150 | 2 | Sin campo | 2 | Pendiente |
| 2025 | 2026-T3 | 1.150 | 0 en listado parcial | 0 en listado parcial | 0 | Pendiente |

E: las presencias no son tasas ni prueban deserción cuando no hay match. Faltan cobertura, fecha efectiva del estado y regla intermedia. B/C: 325 personas explican 328 filas por matrículas múltiples; se conservan las filas, se cuenta una vez a cada persona.

## Veinte personas y grupo de catorce

B/C: 20 = 18 con CODCLI + 2 pendientes. Hay 19 CODCLI: 17 personas con uno y una con dos. El detalle conserva originales como texto, incluidos documentos P, DV vacíos y correspondencia explícita de IPSS_Procesamiento / 2025_carga, J=RUT, BU=N_DOC, BV=DV. Las dos personas sin CODCLI conservan sus identificadores originales. No se infiere un RUN oficial desde el puente observado (E).

B/C: se releyeron 64 fuentes adicionales por hash: 60 comparables por RUT/CODCLI y cuatro sin esa pareja; cero correspondencias nuevas. Se conservan los 58 respaldos nominales de Base Maestra. B/C: los tres respaldos principales tienen 15 matrículas de 14 personas; 13 con alguna VIGENTE en 10246 y 14 en 11998/12112. E: ninguna fotografía certifica el estado en el cierre.

C: el libro privado contiene siete hojas: Resumen_privado, Cohortes_MU (1.708 personas), Identidad_20 (20 personas), Cierres_observados (331 filas coincidentes), Matriculas_20 (1.213 observaciones de las personas objetivo, entre archivos/hojas; no 1.213 personas), MU_anual_20 (20 filas anuales encontradas) y Fuentes (75 registros archivo/hoja). Se conservaron todas las matrículas observadas, no una matrícula escogida por persona. Las fórmulas cuentan personas desde la cohorte y filas desde las observaciones. Cada cruce conserva fuente, hoja, fila y método.

B/C: el cierre anterior verificó 1.130 personas por documento + 18 por puente = 1.148 localizadas en los respaldos; se cita como control previo, no se usa como numerador de un cierre. D: ninguna de las 20 se añade de nuevo a 1.150.

## Reglas auditadas y propuesta sin ejecutar

A: la definición SIES anual sigue el correo congelado del 09-sep-2026, misma institución y cohorte de origen, duración mínima regular 4/6/8, exclusión de especiales y ciertas inconsistencias, publicación desde 10 casos y referencia 30-abril. No se extiende automáticamente a un indicador intermedio interno.

C: `procesos/caracterizacion/caracterizacion_retencion.py`, líneas 18–20 y 169–245, SHA-256 `29dae4561a9969c6c87cd14350ed79a2f2aa78a0f82a72491cb7d6a130a9ee79`: el componente opcional excluye TITULADO en base; reconoce VIGENTE/SUSPENDIDO en destino. TITULADO/EGRESADO en destino puede quedar NO_RETENIDO, sin evaluar fecha del título. Se auditó implementación; no se modificó ni activó una regla distinta.

D/E: la propuesta solicitada distingue titulación acreditada del programa seguido de falta de rematrícula cuando se debía continuar. Requiere decisión aprobada y fecha/programa del título. Se mantienen separados duración formal, nivel esperado, nivel observado, avance curricular, egreso, título intermedio, título del programa y matrícula en otra carrera. No se infiere título por duración cumplida. Conservar cohorte original y calcular otra población elegible serían decisiones distintas.

D/C: seguimiento anual separado intacto: 74/222 = 33,33% y 48/124 = 38,71%. No son las cuatro tasas intermedias. Escenario_80, colores, tablas, filtros y fórmulas del agregado quedan idénticos por conservación byte a byte.

## QA

C: 42 controles independientes aprobados; 12866 fórmulas nuevas con caché, cero errores de fórmula y cero cachés faltantes. ZIP íntegro, siete hojas, seis tablas con filtros, identificadores almacenados como texto, entradas contrastadas celda a celda contra la extracción privada, conteos conciliados, 75 fuentes con hashes intactos, Git sin cambios adicionales atribuibles a esta tarea. Las siete hojas se revisaron visualmente con identificadores enmascarados solo en las vistas; el archivo final conserva los identificadores reales.

C: prueba de sensibilidad sobre una persona identificada y un estado de cierre: los conteos responden, el denominador permanece y la tasa sigue pendiente; restauración comprobada, sin reexportar datos de prueba. El QA inicial detectó filtros desactivados en el exportador y se corrigió antes de esta validación. No se considera aprobada esa primera prueba fallida. También se corrigió la vista de control para que el enmascaramiento no alterara los conteos mostrados.

C/E: Artifact Tool local; no se certifica apertura/reparación ni cálculo nativo en Microsoft Excel. La suite general anterior estaba limitada por unidecode ausente; estas pruebas no la sustituyen ni declaran aprobada toda la suite.

## Pendientes exactos

- E: falta correspondencia institucional explícita CODCLI para dos personas: Ingeniería en Informática y Técnico en Programación y Análisis de Sistemas. Mantienen documento de origen y denominador.
- E: acreditar universo completo, filtros del extractor y fecha efectiva del estado para 2025-T2, 2025-T3, 2026-T2 y 2026-T3. El listado 2026-T2 no informa ESTADOACADEMICO.
- D/E: aprobar regla intermedia propia para término de estudios/titulación, con programa seguido y fecha acreditada. No se cambia motor ni denominadores.
- E: distinguir fecha de matrícula, fecha nominal de extracción y fecha efectiva de estado. La primera observación en un respaldo no acredita un cierre pasado.
- C/E: recálculo local con Artifact Tool, sin certificación en Microsoft Excel nativo. El antecedente de suite general sigue limitado por unidecode; no se presenta como suite integral aprobada.

## Git y preservación

B: avance_curricular, `feature/ire-2026`, HEAD antes/después `80ca13a5a249a1a2bd53a699f5f73689b1f53040`. CARACTERIZACIÓN, `main`, HEAD antes/después `aba337784ccde0537fc21b2977b351170ed335e8`. Se verificaron remotos y estado pendiente. Los cambios previos ajenos se preservaron, sin stage, commit, push, merge, PR ni cambio de rama.

D: fuentes originales, bases, motor anual y denominadores 558/1.150/222/124 preservados. Cierre técnico/documental de esta ampliación completado; las tasas y dos llaves siguen abiertas como E.
