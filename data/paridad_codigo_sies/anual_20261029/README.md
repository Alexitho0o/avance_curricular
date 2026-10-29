# H002f · especificación previa a la implementación

D · Alexi, 29-10-2026. Catálogo anual 2007–2026 y contraste de H002 2027; sin adjudicar personas ni modificar H002/v20. Las identidades solo existen en memoria o en ~/.local/share/ipss/h002f_20261029/.

B/C · Reutilizar puente por año y código completo. 2022–2024 VIG=1, 2025 todos (precarga AC2026), 2026 VIG=1 como contraste. Se verifica cada código; cierre institucional no implica igualdad por versión. Postítulo fuera de base MU separado. No se normaliza un código por semejanza.

C · Identidad exacta por tipo, documento y DV, conservando cero. RUT UMAS completo o RUT+DIG; no fabricar DV. Familia del catálogo previo, sin elegir versión por totales. Actividad PROMEDIOS del año, CODCLI único, plan único, jornada explícita. Sede de Datos Alumnos concordante con sede de catálogo; si falta fecha histórica queda limitación visible. No usar estado actual como estado pasado. Conflictos de identidad, carrera, sede, jornada, varios expedientes o planes quedan SIN_ENLACE con motivo.

C/E · CUADRA_UNICO exige un solo código observado del grupo plan/sede/jornada/año y total MU seleccionado igual al publicado para ese código; si no cuadra, se añade UNICO_SIN_CUADRATURA para no forzar uno de los tres estados pedidos. REPARTIDO conserva todos los códigos. La suma cuenta matrículas MU, no personas ni filas de asignaturas. Publicación sin fila MU se lista en el control por código, sin inventar una matrícula.

C/E · Antes de 2022, comparar actividad anual de expedientes distintos (unión de extractos, no suma) por candidato de catálogo frente a matrícula publicada. Es comparación entre universos distintos, nunca prueba de identidad o aprobación de versión. Sin actividad observada no afirmar inexistencia. ANOINGRESO y última ANOMATRICULA no rellenan años intermedios. Primer año observado no equivale a inicio oficial ni garantiza cobertura desde la creación.

D · Los 37 sin historia permanecen E hasta MU de primer ingreso; no se piden planes nuevos a UMAS. La nueva regla se registra en el repositorio de reglas con alcance D/C, no norma SIES.

QA · Preservación de entradas por hash y 24 ajenos; matriz conserva todas las filas MU y separa incluidas/excluidas VIG; igualdad por código calculada independientemente; identidad y ambigüedad con pruebas sintéticas; 95 resultados de catálogo; reproducción determinista; privacidad sin identificadores.

## Reproducción

Ejecutar `python3 outputs/paridad_anual_20261029/construir_anual.py --verificar` desde el repositorio con las fuentes locales de FUENTES.json. Verifica hashes y reproduce todas las salidas; las identidades solo se escriben en el directorio privado.

## Estados y unidades

CUADRA_UNICO / REPARTIDO / SIN_ENLACE: enlace anual MU; UNICO_SIN_CUADRATURA evita confirmar código con total diferente. FUERA_SELECCION_VIG conserva filas no incluidas. Antes de 2022: CUADRA_TOTAL / APROXIMA (±10 %) / NO_CUADRA son contrastes C/E de expedientes con actividad versus matrículas, no asignación. Las filas de comparación histórica repiten el total público por candidato y NO son sumables. Los conteos MU incluidos/excluidos sí son aditivos por código y año. Los totales SIES repetidos en la matriz se consultan una vez en CONTROL_POR_CODIGO_ANIO.json.

## Los 37 códigos sin historia

D · Alexi, 29-10-2026: se revisan con este motor cuando exista MU 2027 (o MU del año de su primer ingreso), por código y total y con enlace de plan inequívoco. No se solicitan a UMAS. Hasta entonces conservan NUEVO_2027_SIN_PLAN_E. Un total coincidente sin enlace no cierra la identidad del plan. No se modifica H002 en este encargo.
