# Diccionario común SIES para seguimiento de expedientes

## Alcance autorizado (D)

Solicitud de Alexi del 2026-10-23: conectar códigos ya documentados y decisiones
internas aprobadas para seguir T1 en T2/T3, concentrando la revisión en las
excepciones de versión. No cambiar fuentes, denominadores ni motores anuales.
Esta integración no autoriza commit, push ni nuevas equivalencias por inferencia.

## Contrato previo a implementación (C)

- Una entrada común desde PROYECTO_IPSS.json; implementación en common/ y
  comandos compartidos. Se justifica ese layout por agent.md y la integración
  vigente. C2 y el puente MU2026 permanecen congelados como antecedentes.
- Materializar las 24.774 observaciones reproducidas, aplicando las 19 operaciones
  acumuladas aprobadas con comprobación exacta de estado anterior. Conservar
  código documental, código interno y propuesta como campos diferentes.
- Identidad + CODCLI + carrera/sede/jornada + plan + año + período identifican el
  contexto. No relacionar por nombre, totales, versión máxima ni año del plan.
- Conservar evidencia anual MU y sus filas. Un código anual atribuible se ofrece
  como respaldo anual, no como prueba de asignación de plan en un trimestre.
- Incorporar la base MU2022–2026 completa como índice anual separado, sin
  convertir sus filas en nuevos integrantes de la cohorte ni denominadores.
- La consulta por contexto reutiliza adjudicaciones exactas y códigos atribuidos;
  si no existe el contexto, tiene varios expedientes/planes/códigos o falta
  identidad, devuelve excepción. Nunca hereda automáticamente otra versión.
- El adaptador T1→T2/T3 conserva código de la cohorte de origen separado del
  código respaldado en la observación destino. Exige períodos explícitos y no
  convierte períodos de PROMEDIOS (incluye 4/5) en trimestres por su número.
- Resultados personales en almacenamiento privado fuera de Git, verificado antes
  de escribir. Repositorio: código, descriptor, hashes, resumen y QA sin personas.
- Atribución documental pendiente y ausencia de comprobante de aceptación SIES
  siguen visibles. La nueva capa es para análisis interno, no archivo de carga.

## Validación

Reproducir 5.901 personas/24.774 observaciones y conservar 3.076 pendientes internos
y 3.213 documentales. La cifra histórica de 6.622 expedientes se conserva como
unidad carrera+CODCLI, verificándola separadamente. Probar conservación de los
códigos anuales y cierres aprobados, conflictos, planes múltiples, períodos no
localizados, no extrapolación temporal, integridad alterada e identidad múltiple.
Revisar todas las consultas reales, con atención a familias con varias versiones.
Verificar paridad de consumidores, hashes antes/después, ausencia de PII en
salidas públicas y que no se modifica el Excel ni el motor MU2026.

## Pendiente que no se oculta (E)

Esta integración no resuelve por sí sola las equivalencias todavía pendientes.
No certifica aceptación SIES ni fecha efectiva del plan. Complementos remotos
deben adoptar este contrato; no se afirma sincronización por existir un archivo.
