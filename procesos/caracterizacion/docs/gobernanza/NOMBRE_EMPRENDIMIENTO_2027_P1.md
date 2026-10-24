# Semantica del nombre de empresa o emprendimiento, 2027 P1

Decision y verificacion: 2026-10-13. Alcance: seguimiento de opciones y VCM de
encuesta 141234. No cambia el instrumento ni las respuestas originales.

## Fuentes y origen

Manual de Aplicacion de la FCU 2027 en plataformas propias, paginas PDF 21-22,
pregunta P17: "¿Que opcion describe mejor tu situacion laboral actual?". Solicita
una sola respuesta: No trabajo actualmente; Trabajo a tiempo completo; Trabajo a
tiempo parcial; Trabajo esporadicamente o en pololos. El manual no pide nombre de
empresa o emprendimiento. Su variable oficial es SIT_LAB, valores 1 a 4.
PDF SHA-256: 01761a360a6607e2ab263135b3c115999b9b161cc264d4f15ea7aa48a5270af7.
Texto versionado: gobernanza/FCU/2027/preparacion/evidencias/Manual_de_Aplicacion_FCU_2027.txt.

Instrumento: gobernanza/instrumentos_limesurvey/2027/P1/141234_20261009_406d959cedfd,
inventory.json y fuentes/limesurvey_group_644.lsg, preservados segun su manifiesto.
Origen institucional de G02Q27 y G01Q25: inventario y question_origins() del auditor.
Grupo de todos los codigos siguientes: ANTECEDENTES FAMILIARES Y SOCIOECONOMICOS.

| Codigo / posicion | Pregunta y respuestas de nuestra implementacion | Alcance |
| --- | --- | --- |
| G02Q95 / 18 | Situacion laboral actual. AO01: trabajo relacionado con carrera; AO02: trabajo no relacionado; AO03: busca trabajo; AO04: no piensa trabajar; AO05: Tengo un emprendimiento formalizado | Bloque adaptado vinculado a P17, con extension institucional AO05; no reclasificar toda la pregunta ni inferir SIT_LAB desde AO05 |
| G02Q20 / 19 | Situacion laboral. AO03: tiempo completo; AO04: tiempo parcial; AO05: esporadicamente o pololos | Detalle de la adaptacion para SIT_LAB, visible solo para G02Q95 AO01/AO02; AO05 de este codigo tiene otro significado |
| G01Q25 / 24 | En esta ocupacion trabajas como... AO02: empleado sector privado; AO03: empleado sector publico; AO04: emprendedor, menos de 10 trabajadores; AO05: empleador | Institucional. No acredita formalizacion ni propiedad de un nombre declarado |
| G02Q27 / 26 | ¿En qué empresa trabajas o como se llama tu emprendimiento? | Institucional. Texto corto libre, sin opciones ni subpreguntas. Puede ser empresa empleadora o emprendimiento |

G02Q21 (horas), G02Q22 (contrato), G02Q23 (cargo), G01Q24 (ingreso), G01Q25
(ocupacion), G01Q26 (rubro) y G02Q27 se habilitan solo con G02Q95 AO01/AO02
en esta exportacion. No atribuir esos detalles a AO05 por cercania entre preguntas.

## Causa y correccion

compute_followup() copiaba G02Q27 a NOMBRE_EMPRENDIMIENTO en todas las filas de
detalle, sin comprobar que el texto nombrara un emprendimiento propio. Incluso
un nombre de empleador podia aparecer bajo esa etiqueta en categorias.
Ademas, el respaldo Respuestas fuente omitía G02Q27, dificultando la trazabilidad.

La etiqueta se sustituye por EMPRESA_O_EMPRENDIMIENTO_DECLARADO, conservando el
texto exacto. ESTADO_NOMBRE_EMPRENDIMIENTO distingue:

- NO_CONFIRMADO_PREGUNTA_MIXTA: hay respuesta, sin atribuir propiedad ni tipo.
- SIN_RESPUESTA_G02Q27: columna presente sin respuesta valida, sin inferir negativa.
- COLUMNA_AUSENTE: falta la columna, distinguible de un vacio individual.

Respuestas fuente conserva G02Q27. El control JSON conserva enunciado, codigo,
origen, relevancia observada, campo resultante y conteos de estados VCM.
Los totales Acumulado/Hoy, la seleccion de AO05 y los contactos no cambian.
No usar nombre administrativo de empresa como respaldo ni inferir formalizacion
desde G01Q25/AO04, el rubro, el cargo o una palabra de la respuesta abierta.

## Limite del formulario actual

Relevancia observada de G02Q27:
`((G02Q95.NAOK == "AO01" or G02Q95.NAOK == "AO02"))`.
Excluye AO05. Es un filtro funcional, no la excepcion de revision que evita pedir
relevancia vacia igual a 1. La exportacion no acredita el recorrido efectivo de
cada participante. No afirmar que el estudiante se nego a dar el nombre.

Para medir exclusivamente un nombre de emprendimiento a futuro hace falta una
pregunta institucional de nombre inequívoco habilitada para AO05, o una nueva
version documentada del enunciado/filtro. No se crea ni modifica ninguna pregunta
en esta correccion. Los textos ya recogidos conservan su significado original.

## Evidencia de los datos

results-survey141234.xlsx leido el 2026-10-13: 15 respuestas, 2 seleccionan
emprendimiento formalizado; ambas tienen G02Q27 vacio. Hay 12 respuestas G02Q27
en otros registros. Esto confirma el error de etiqueta y la falta del dato para
VCM, pero no prueba que los nombres de esos otros registros sean emprendimientos.
SHA-256 de resultados: dbeb187be26e41ffe964e2a8e8dc0917d7aa54d7e544740320b19a26665b8668.
Datos individuales y pruebas sobre fuentes reales quedan en .local, sin publicarlos.

Pruebas de regresion: tests/test_seguimiento_opciones_2027.py. Version vigente de
la politica: SEGUIMIENTO_OPCIONES_2027_P1-v2; registro institucional version3.
Las referencias FCU 2026 y las corridas anteriores se conservan.

## Validacion de la correccion

Ejecucion real 2027_P1_143606, codigo 0; copia de entrega
Caracterizacion_2026-10-13_2027_P1_143654. Los dos Excel de categorias y VCM
contienen la etiqueta literal y su estado. Se cotejaron 1.689 celdas con sus
modelos y las respuestas originales. Ambas hojas de detalle fueron revisadas
visualmente en las columnas modificadas; no se detectaron errores de formula.

Los 33 conteos de seguimiento y todos los totales del manifiesto son identicos
a 2027_P1_134757. Hay 2 casos VCM con SIN_RESPUESTA_G02Q27. Los otros 22 libros,
el contenido de ambos Word y los CSV permanecen iguales. Las 42 piezas de la
corrida previa y las 51 referencias congeladas FCU 2026 conservan sus hashes.
Pasaron 60 pruebas focalizadas, incluidas 6 regresiones nuevas sobre esta brecha.
La ejecucion completa tambien conserva la omision del archivo de eliminados
sin casos y la salida de comunicaciones Patagonia.

Evidencia privada: .local/auditoria_nombre_emprendimiento_20261013/VALIDACION.json.
Esta correccion del reporte no declara resuelta la captura del nombre en el
formulario ni libera PES 2027. La exportacion original queda intacta.
