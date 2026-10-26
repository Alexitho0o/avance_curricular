# Plan de cierre del diccionario UMAS–SIES

Fecha: 25-10-2026. Proceso: conciliación UMAS–SIES para seguimiento de retención.
Repositorio: avance_curricular. Rama: feature/ire-2026.
HEAD de referencia: 55e3b709afb9483f0ecdd2d166f67229a454a5ef.

**D — Objetivo solicitado:** alcanzar el 100% de cobertura respaldada del código
SIES en el universo fijado, sin cambiar bases, cohortes ni denominadores.
**C — Plan:** primero completar el alcance utilizado por V17, luego el histórico
completo. Este documento planifica el trabajo; no declara ejecutados nuevos cierres.
**E — Límite:** el 100% es una meta, no un resultado garantizado. No se asignará
una versión por completar una cuota. Si las fuentes no distinguen las alternativas,
se registrará exactamente qué campo, evidencia o decisión falta.

## Línea base y medidas

**B/C — Fuente:** MANIFEST.json, QA_ENTREGA.json e insumos de la auditoría de esta
carpeta. Servicio activo v7_20261023_inf35_03_t3. No se reinicia la investigación.

| Alcance | Observaciones | Con código | Pendientes | Combinaciones | Con algún pendiente |
|---|---:|---:|---:|---:|---:|
| Contextos localizados que utiliza V17 | 2.854 | 2.750 | 104 | 26 | 16 |
| Histórico completo 2019–2026 | 24.774 | 21.725 | 3.049 | 93 | 63 |

**C:** combinación = carrera UMAS + plan + sede + jornada. El desglose por año y
período se conserva para decidir cada asignación. Una combinación completa puede
tener versiones diferentes por persona/período; no se convierte en una regla
universal plan→versión. Los dos alcances se reportan separados y no se suman.
Las 104 observaciones son parte del seguimiento, no 104 estudiantes adicionales.

**C:** cobertura interna = (códigos documentales atribuidos + correspondencias
internas aprobadas, sin doble conteo) / observaciones del alcance congelado.
Cobertura documental, personas completas, expedientes y combinaciones completas
se informan por separado. No se mezclan con tasas de retención ni aceptación SIES.
No se exige un envío trimestral inexistente para reconocer correspondencia interna.

**C — Qué cuenta como resuelto:** un código documental atribuible al expediente y
período, o una correspondencia interna expresamente aprobada dentro de su alcance.
Un candidato único, una coincidencia de totales o un pendiente explicado no cuentan
como cierre. Las 104 observaciones pendientes de V17 están incluidas en las 3.049
del histórico; no son universos independientes.

**B/C:** V17 tiene 3.179 orígenes T1 con código. Las 3.520 posiciones de seguimiento
sin contexto localizado no forman parte de los 104 pendientes de código y no son
automáticamente desertores. No se excluirán ni se reclasificarán para mejorar cobertura.

## Fases e hitos

### Fase 1/7 — Fijar el alcance y los controles

- **Hito 1/3 (C):** fijar hashes de edición activa, fuentes y V17; reutilizar QA
  existente. Repetir controles solo si un hash, código o alcance cambió.
- **Hito 2/3 (C):** identificar los 104 pendientes de V17 dentro del histórico y
  registrar observación, expediente, plan y período en área privada. Conservar
  todos los registros, incluidos documentos distintos de RUT y matrículas múltiples.
- **Hito 3/3 (C):** registrar contadores iniciales, reglas aprobadas y consumidores.
  Separar pendientes de código, ausencia de contexto académico y vigencia al cierre.
  Abrir desde este hito la bitácora por lote con edición anterior, fuente/hoja/fila,
  acción, regla, resultado, responsable, fecha/hora y autorización aplicable. La
  fase 5 consolida esta evidencia; no la reconstruye retrospectivamente.

**Salida y aceptación:** checkpoint con universos exactos, sin duplicados ni
registros perdidos. Si cambia un conteo de referencia, detener esa rama y explicarlo
antes de continuar. Ningún dato personal se incorpora al informe público.

### Fase 2/7 — Recuperar lo ya documentado y probar la regla común

- **Hito 1/3 (C):** consultar primero el diccionario v7 y los códigos T1 ya
  documentados, puentes de identidad y equivalencias internas vigentes. No repetir
  búsquedas resueltas ni reconstruir versiones por nombre.
- **Hito 2/3 (C):** reconstruir la secuencia por expediente: identidad, CODCLI,
  carrera, sede, jornada, plan y período. Distinguir contexto original, contexto
  observado después y cambios respaldados. Conservar el código de la cohorte T1.
- **Hito 3/3 (C/E):** probar cualquier criterio complementario contra casos ya
  documentados, ocultando el código objetivo durante la selección y evaluando por
  persona, no por filas repetidas. Una regla que contradiga evidencia documental
  no se aplica en bloque: se limita su alcance o vuelve a investigación.

**Salida y aceptación:** reglas reutilizables con alcance y evidencias; propuestas
separadas de asignaciones adoptadas. La ausencia de cambio registrado no demuestra
por sí sola que el contexto se mantuvo. No se exige el día exacto si fuentes o una
decisión aprobada acreditan el período, pero tampoco se presupone continuidad.

### Fase 3/7 — Resolver el pendiente que afecta a la V17

- **Hito 1/3 (C/E):** revisar las 63 observaciones con jornada candidata distinta:
  contrastar ancla T1, fotos por período, secciones, plan y cambios respaldados.
- **Hito 2/3 (C/E):** revisar las 34 con candidatos en otra carrera/sede/institución:
  atribuir cada matrícula al expediente correcto, sin unir trayectorias por nombre
  ni multiplicar personas en cruces muchos-a-muchos.
- **Hito 3/3 (C/E):** resolver las cinco con versión/plan sin atribuir y las dos sin
  candidato/contexto. El atributo que distingue versiones debe quedar explícito.

**Modo de trabajo C:** lotes de máximo 10 observaciones, agrupadas por el mismo
problema y contexto. Después de cada lote: casos revisados, recuperados documentales,
propuestas internas, cierres autorizados, pendientes y causas. Un bloqueo de un lote
no impide investigar otro independiente. El límite de diez observaciones no recorta
la trayectoria que debe leerse para interpretar cada una.

**Salida y aceptación:** objetivo 2.854/2.854 observaciones respaldadas y 26/26
combinaciones sin observaciones pendientes. Los cierres D nuevos requieren una
aprobación aplicable; pueden aprobarse criterios acotados por lote, no hay que
pedir nuevamente decisiones ya autorizadas. Mientras falte evidencia o aprobación,
el caso sigue E y el objetivo se considera pendiente.

### Fase 4/7 — Extender el cierre al histórico completo

- **Hito 1/3 (C):** actualizar el pendiente residual después de Fase 3 por año,
  familia, plan y período. No sumar los 104 a los 3.049 ni repetir cierres previos.
- **Hito 2/3 (C/E):** revisar los grupos cuyo requisito registrado es asignación
  del plan y continuidad/migración/reingreso (2.650 en la línea base). Usar el
  período de ingreso o cambio acreditado, no el año del nombre del plan ni el año
  observado como sustituto. Evaluar códigos anteriores y posteriores sin
  extrapolación automática.
- **Hito 3/3 (C/E):** completar los restantes requisitos: perfil del programa (202),
  versiones coexistentes (94), grupo (51), fecha pertinente (32), oferta compatible
  (19) y homologación en plan rechazado (1). Estos valores son la línea base y se
  actualizan después de cada cierre sin cambiar el universo.

**Salida y aceptación:** objetivo 24.774/24.774 observaciones respaldadas,
93/93 combinaciones sin pendientes y 5.901 personas sin observaciones abiertas.
Las 2.651 propuestas de candidato único no se convierten automáticamente en cierres.
Si una evidencia no se localiza, registrar fuentes efectivamente consultadas y el
campo o decisión necesario; no repetir indefinidamente la misma búsqueda ni inventar
una asignación para declarar 100%.

### Fase 5/7 — Consolidar una edición única del diccionario

- **Hito 1/3 (C/D):** preparar una edición candidata con los cierres respaldados,
  preservando v7 y todas las decisiones anteriores. No editar una edición congelada.
- **Hito 2/3 (C/D):** registrar por cambio: estado anterior y nuevo, regla, alcance,
  responsable, fecha/hora, aprobación, evidencia y hashes. Mantener código documental
  separado del interno y del propuesto.
- **Hito 3/3 (C):** comprobar que las tres entradas locales consultan el mismo
  descriptor y ofrecen la misma respuesta. La promoción del puntero solo se ejecuta
  con autorización aplicable y QA correcto; hasta entonces es una edición candidata.

**Salida y aceptación:** una única entrada versionada, diferencia completa contra
v7, ninguna asignación nueva sin respaldo y conservación de las observaciones no
incluidas en cada autorización. Se permite consolidar avances parciales sin afirmar
que el objetivo de cobertura ya cerró.

### Fase 6/7 — Probar conservación, reproducción y efecto en el Excel

- **Hito 1/3 (C):** comprobar cardinalidad, unicidad, fuentes y contexto; rechazar
  conflictos, multiplicación de registros y cambios no autorizados. Reejecutar
  las pruebas de consulta y controles temporales afectados.
- **Hito 2/3 (C):** aplicar en una copia de prueba del Excel. Comparar conteos,
  denominadores, tasas y fórmulas con V17. Un cambio de código puede afectar un
  desglose: mostrarlo explícitamente. No modificar reglas de vigencia, elegibilidad
  o tasas para hacer coincidir totales. Si cambia la clasificación de un programa,
  evaluar el efecto aparte antes de adoptar cualquier cambio funcional.
- **Hito 3/3 (C):** verificar integridad del libro, gráficos, tablas, privacidad,
  fuentes privadas accesibles y procedimiento reproducible. Distinguir prueba del
  servicio, recálculo y apertura nativa; no afirmar una prueba no ejecutada.

**Salida y aceptación:** cero cambios inesperados y ninguna regresión sin explicar.
Una diferencia numérica no equivale automáticamente a error, pero debe trazarse y
resolverse antes de promover el cambio. La V17 original permanece intacta.

### Fase 7/7 — Publicar y conectar GitHub, complementos y skills

- **Hito 1/3 (C/E):** preparar y revisar el paquete no personal: código, contratos,
  decisiones agregadas, manifiestos y QA. Mantener bases e identificadores privados
  fuera de Git. Commit/push solo con autorización específica para esta entrega.
- **Hito 2/3 (C/E):** actualizar, dentro de la autorización recibida, el complemento
  remoto y las skills para localizar el mismo puntero. No copiar otra tabla de
  equivalencias que quede desactualizada. Sin acceso local al servicio, declarar
  esa limitación de ejecución.
- **Hito 3/3 (C):** comprobar versión realmente publicada y consumo desde cada
  entrada; comparar respuestas documentales, internas, múltiples y pendientes.
  Registrar procedimiento de actualización, alerta y reversión.

**Salida y aceptación:** publicación y conexiones efectivamente verificadas,
reproducción local con fuentes privadas y cobertura reportada con el mismo universo.
La sincronización puede completarse aunque queden excepciones, pero no se la llama
100% de cobertura. Para cerrar el objetivo global deben cumplirse ambos controles.

## Registro de cada avance

**C:** comenzar con `Fase X/7 · Hito Y/3`, seguido de estado y evidencia.
Registrar entrada/hash, acción, resultado, archivos, contadores antes/después,
regla/aprobación, pendientes y siguiente paso. Una propuesta no reduce el contador
de pendientes hasta contar con el respaldo y autorización correspondientes.

**C — Control por hito:** pendientes iniciales − cierres respaldados y autorizados
+ nuevas incidencias = pendientes finales. Cada cierre debe superar la reconsulta
individual y la conciliación del lote, con cero duplicados y cero cambios fuera
del alcance autorizado. Las nuevas incidencias no alteran el universo congelado:
se registran como reaperturas dentro de él; hallazgos externos se informan aparte.

**C:** cierre final requiere simultáneamente: cobertura interna 100% en los dos
alcances congelados, cero asignaciones ambiguas adoptadas, cero pérdidas/duplicados,
controles de conservación correctos y consumidores sincronizados. El porcentaje
documental y la prueba de aceptación SIES se informan separados, sin prometer que
una correspondencia interna se convierta en evidencia de envío.

**Estado actual B/C:** plan preparado. Auditoría de referencia verificada; fases
de resolución y publicación no ejecutadas en esta entrega. Bases, denominadores,
V17, edición activa y rama conservados. Sin commit ni push.
