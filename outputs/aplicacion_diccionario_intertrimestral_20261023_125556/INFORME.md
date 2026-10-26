# Aplicación del diccionario al Excel intertrimestral

## Alcance y resultados

- B/C: códigos de origen MU/T1 comprobados para las 3.179 filas persona–año del libro vigente: 558 (2024), 1.150 (2025), 1.471 (2026). No se altera ningún denominador.
- C: se aplicó la consulta canónica a 5.320 observaciones de esas personas en el mismo año: 5.088 documentales, 2 internas aprobadas y 230 pendientes. Cada observación conserva expediente, plan y período nativo; no son nuevos estudiantes.
- B/C: el grupo T1 contiene 825 registros en familias con múltiples versiones históricas documentadas. Sus códigos de origen están confirmados. En el seguimiento hay 1.927 observaciones documentales, 2 internas aprobadas y 80 pendientes; otros 19 registros T1 no tienen contexto localizado en el diccionario.
- E: los 80 pendientes se separan en 71 de otra familia, 6 de la misma familia y 3 de familia no determinada. No se traslada automáticamente el código T1 a otra carrera/jornada o plan. Las dos correspondencias internas mantienen pendiente su atribución documental.

| Carrera T1 (foco múltiples versiones) | B/C documental | D interno aprobado | E pendiente |
|---|---:|---:|---:|
| Ingeniería en Ciberseguridad | 592 | 0 | 21 |
| Ingeniería en Conectividad y Redes | 424 | 2 | 17 |
| Ingeniería en Informática | 755 | 0 | 35 |
| Técnico en Conectividad y Redes | 156 | 0 | 7 |

## Uso del libro

- Hoja 52: resumen de la aplicación y controles matemáticos.
- Hoja 53: códigos SIES de origen completos; filtrar «Varias versiones en evidencias» = Sí.
- Hoja 54: año, período nativo, carrera, plan, código de origen, código del contexto, respaldo y candidatos no adoptados. Filtrar «Origen con varias versiones» = Sí y «Respaldo» = E Pendiente para revisar las excepciones.
- B/C: se reutilizó el puente explícito de 20 documentos P; no se derivó RUT desde pasaporte.

## Validación y límites

- C: 105 grupos / 4.473 filas de la hoja 20 original reproducen exactamente el agregado V11.
- C: 86 fórmulas nuevas con caché y 86 comprobaciones aritméticas independientes correctas. Sin errores de celda en hojas nuevas. ZIP/XML y dos tablas nuevas validados.
- C: 51 hojas originales, 13 gráficos y 33 tablas originales idénticos byte a byte. Fuentes y diccionario sin cambios.
- E: no se probó apertura en Excel nativo. Se recalculó solamente el suplemento con Artifact Tool. Las tasas históricas conservadas no se recertifican mediante esta revisión de códigos.
- E: período nativo PROMEDIOS no se declara equivalente a corte T2/T3. Presencia de CODCLI en foto T3 se observa aparte y no atribuye una versión por sí sola.
- E: 939 registros persona–año T1 no tienen contexto localizado en el diccionario. Mantienen su código MU de origen; no se consideran desertores.
- D: grupos de ingreso T2/T3 existentes preservados, no reclasificados en esta aplicación enfocada al seguimiento de T1.

## Entrega

/Users/alexi/Desktop/RETENCION_IPSS_DICCIONARIO_APLICADO_20261023_V12.xlsx
SHA-256: `e7f797b5de9a6e9748cd250e9931947dbc8469f65d01f5a488c765e0009676fe`

Rutas, fuentes, auditoría privada local y hashes en MANIFEST_APLICACION.json. Sin identificadores individuales agregados al Excel. Sin commit ni push.
