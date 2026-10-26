# Relación de estados y situaciones UMAS con VIG SIES

**C — Versión 2026-10-20.2.** Especificación de consulta para Matrícula Unificada
2026, vinculada al hito H001-RETENCION-IPSS162. La tabla se construye en el
repositorio contenedor `avance_curricular`, según `PROYECTO_IPSS.json` y el
contrato de unificación del 15-10-2026. No modifica el motor MU2026 congelado.

**D — Encargo vigente:** crear una relación explícita entre los estados y
situaciones de UMAS y los valores 1/2 de SIES, y compartirla en las skills y
complementos. Se mantienen los denominadores aprobados T2=222 y T3=124.
No se recalculan indicadores ni se modifican archivos fuente.

## Qué significa la relación

**A — Manual MU2026, p.31, Anexo 7, Cuadro N°1, AF:**

| VIG | Definición oficial |
|---|---|
| 0 | Estudiante sin matrícula |
| 1 | Estudiante con matrícula vigente |
| 2 | Estudiante egresado con matrícula vigente |

**A — Manual p.7, §2.vi:** el proceso terminal corresponde a quien finalizó
exitosamente el plan y todavía realiza actividades directamente conducentes
al título o grado. **A — Manual p.10:** una suspensión puede informarse con
0, 1 o 2 según la reglamentación institucional. Las etiquetas actuales de
UMAS no demuestran por sí solas estas condiciones en una fecha pasada.

**D/B — Precedencia verificada:** Gate09 C09-01, confirmado por Gate10 el
23-09-2026, descartó las conversiones automáticas desde estados U+ a VIG,
incluidas TITULADO→0 y TITULADO→2. Esta relación conserva esa resolución:
relaciona las etiquetas con las condiciones que deben verificarse, en lugar
de volver a activar las equivalencias descartadas.

## Tabla de decisión explícita

**C — Grano:** una matrícula/programa de una persona, un período y una fecha
de corte. Otra carrera de la misma persona se evalúa separadamente. Las
variables de comprobación de esta sección son conceptos técnicos propuestos;
no se afirma que existan como columnas físicas de UMAS.

| Regla | Condición acreditada para esa matrícula y corte | Resultado | Respaldo |
|---|---|---|---|
| R1 | Matrícula vigente acreditada y categoría académica no terminal acreditada | VIG 1 | A: p.31 AF; C: operacionalización |
| R2 | Matrícula vigente acreditada, plan finalizado y actividades conducentes al título en curso, sin título obtenido al corte | VIG 2 | A: p.7 §2.vi y p.31 AF; D: Gate10 C09-01; C: operacionalización |
| R0 | Condición sin matrícula acreditada al corte | VIG 0 | A: p.31 AF; C: operacionalización |
| RE | Falta matrícula al corte, falta la condición académica que distingue 1/2, hay contradicción temporal o no se identificó la matrícula/programa | Pendiente, VIG vacío | E; C: control de evidencia |

**C — Orden de comprobación:** primero validar proceso/edición y grano; después
resolver contradicciones, matrícula al corte y condición académica. R2 y R1
son excluyentes. Falta de información nunca equivale a R0 ni a R1.
El VIG efectivamente informado en un archivo se conserva como dato B separado
de cualquier reconstrucción C; esta tabla no lo sobrescribe.

## Cómo se relaciona cada grupo UMAS

| Estado/situación UMAS | Relación para VIG 1 | Relación para VIG 2 | Precaución y clasificación |
|---|---|---|---|
| VIGENTE + 1, 20, 38, 49 o 100 | R1 si se demuestra matrícula y condición no terminal al corte | Solo R2 con evidencia terminal independiente | B: pareja observada; C: relación. VIGENTE no basta para R1. |
| EGRESADO + 13 o 14 | Solo si el historial prueba R1 en el corte, aunque el egreso sea posterior | R2 si el egreso y todas las demás condiciones terminales corresponden al corte | C: clasificación interna EGRESADO. E sin matrícula/fechas/actividad terminal. |
| TITULADO + 31 o 42 | R1 si el historial prueba esa condición antes del egreso/título, u otra matrícula evaluada separadamente | R2 si al corte seguía en proceso terminal y el título se obtuvo después | D: no TITULADO→0/2. Título ya obtenido al corte no justifica R2 para ese mismo título. |
| SUSPENDIDO + 2; ELIMINADO + 2 | R1 si reglamento y matrícula del período lo acreditan | R2 si reglamento, matrícula y proceso terminal lo acreditan | A: p.10 permite 0/1/2; E si falta el reglamento aplicable. |
| ELIMINADO + otras situaciones | Solo R1 acreditada al corte; no desde el estado actual | Solo R2 acreditada al corte; no desde el estado actual | C: revisar historial y vigencia efectiva del evento. No inferir matrícula de destino tras cambio ni baja retrospectiva. |
| ELIMINADO + 16 | La etiqueta no autoriza asignación; usar evidencia independiente de R1 | La etiqueta no autoriza asignación; usar evidencia independiente de R2 | B: etiqueta observada; E: significado/catálogo pendiente. No inferir causa disciplinaria individual. |

**B/C — Cobertura:** la [tabla completa](../data/reglas_negocio/20261020_estados_umas/relacion_estados_situaciones.tsv)
conserva las 32 parejas observadas y sus conteos agregados, texto original,
clasificación interna, referencia histórica y condiciones R1/R2/R0/RE.
El mapeo histórico descartado queda en una columna identificada como antecedente,
nunca como salida. Un espacio final en SITUACION se conserva en el literal;
solo se recorta para buscar la pareja técnica.

## Evidencia que debe acompañar la relación

**B/C/E — Disponibilidad documentada en el diccionario v1.0, hoja
05_DICCIONARIO_BETTERSOFT:**

| Hecho necesario | Campo observado o requerimiento gobernado | Situación |
|---|---|---|
| Matrícula/programa identificable | CODCLI; relación con programa y período | Existe; no sustituir por el estado global de una persona |
| Año/período de matrícula | ANOMATRICULA, PERIODOMATRICULA; UP-40 | Existen; no prueban por sí solos vigencia en una fecha |
| Estado y situación | ESTADOACADEMICO, SITUACION; UP-42, fila42 | Existen como fotografía actual |
| Fecha de matrícula del período | FECHAMATRICULA; UP-39 | Temporalidad primera matrícula/renovación por confirmar |
| Historial fechado de situación | UP-43, fila43 | POR_CONFIRMAR; no presente entre las 67 columnas |
| Egreso y título fechados | UP-59/UP-60, filas59/60 | NO_EXISTE en el reporte consultado |
| Historial de matrícula por período | UP-66, fila66 | POR_CONFIRMAR |
| Catálogo institucional documentado | UP-68, fila67 | NO_EXISTE en el diccionario; código16 pendiente |
| Actividad terminal en curso | Condición de Manual p.7 | No se identificó un campo físico confirmado que la pruebe |
| Vigencia conforme al reglamento institucional | Manual p.31 y p.10 | Falta reglamento completo y evidencia aplicable al corte para reconstruirla |

**E — Aplicación individual:** las fuentes disponibles no entregan información
suficiente para asignar un nuevo VIG a las 15.136 filas a partir de estado y
situación. Faltan los hechos temporales y académicos anteriores. La relación
queda documentada y utilizable cuando se acrediten esos hechos; esto no declara
resuelto el VIG de cada estudiante ni convierte los pendientes en ceros.

## Uso común y trazabilidad

**C:** consultar `PROYECTO_IPSS.json → recursos_comunes → estados_umas_vig_sies`.
El [manifiesto](../data/reglas_negocio/20261020_estados_umas/manifest.json)
identifica fuentes, hashes, reglas, QA y alcance. El paquete contiene la tabla
completa, reglas estructuradas y ejemplos sintéticos sin datos personales.

**C/D:** esta definición se usa para MU2026. Avance Curricular, Extranjeros,
Titulaciones y encuestas conservan sus manuales, universos y significado de
VIGENCIA. Compartir los estados UMAS no autoriza compartir las reglas de carga.
Retención/continuidad conserva su definición, denominador y fuente del seguimiento.

**B/D — Fuentes decisivas:** Manual_Matrícula_Unificada_2026.pdf p.7/p.10/p.31;
REPORTE_CIERRE_GATE09_UPLUS_SIES_2026.md §C C09-01 y §E1–3;
DICCIONARIO_MAESTRO_UPLUS_SIES_2026_v1.0.xlsx,
12_GATE09_RESOLUCION fila2, 18_CONFIRMACION_GATE10 fila2 y
06_CATALOGOS_HOMOLOGACIONES J79:K79. Los hashes completos se calculan desde
los archivos y quedan en el manifiesto. El mapa interno de Caracterización es
implementación C, aunque su variable se llame `_MAPA_ESTADO_OFICIAL`.

**C/E — Distribución:** los complementos reciben una instantánea del mismo
paquete y sus hashes. No existe sincronización automática con GitHub; un cambio
de fuentes requiere nueva verificación y actualización. Los recibos remotos se
registran aparte del manifiesto de las reglas.
