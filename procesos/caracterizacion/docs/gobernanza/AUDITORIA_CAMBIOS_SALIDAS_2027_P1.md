# Auditoria de cambios de salidas 2027 P1

Corte de auditoria: 2026-10-13. Alcance: actualizaciones recientes del reporte,
archivos operativos y manifiesto 2027 P1. No es una certificacion exhaustiva de
todas las funciones historicas ni del archivo de carga PES.

## Evidencia y atribucion

HEAD observado: 6ebd694e9fa254667e42dc02c9598909eeea8fbe, rama main.
El codigo congelado caracterizacion.py, tanto en HEAD como en disco, exporta
Actualmente_eliminados_matricula_en_ventana sin condicion. exportar_excel tiene
skip_if_empty=False por defecto. No se encontro en esas versiones una regla de
omision para este nombre concreto. No atribuir su perdida a una actualizacion
particular sin evidencia. La nueva instruccion del usuario exige omitirlo con cero.

El adaptador 2027 ejecuta la correccion en memoria sin modificar el archivo
congelado. Se preservan las auditorias con cero casos; solo se omite el detalle
operativo vacio. La prueba positiva comprueba que el archivo se genera con casos.

## Comparacion de comportamientos

| Elemento | Hallazgo entre versiones disponibles | Estado vigente |
| --- | --- | --- |
| Eliminados en ventana sin casos | Exportacion incondicional heredada, presente en HEAD y en la corrida 132949 | Corregido: OMITIDO_SIN_CASOS, sin archivo operativo |
| Apertura de correo aceptada | El generador inicial 2027 sustituyo la apertura historica | Recuperada con cifras y alcance 2027 |
| Opciones con cero y columna temporal | La simplificacion inicial filtro ceros y retiro el desglose | Recuperadas; Acumulado/Hoy usa envio de encuesta por decision vigente |
| Codigos de seguimiento | El adaptador inicialmente reutilizaba categorias 2026 | Instrumento 141234 version 20261009; retiradas no se convierten en ceros |
| Financiamiento | La referencia incluia una repeticion; el proceso simplificado no conservaba todo el seguimiento | Once alternativas una vez en Word y Excel, con conteos verificables |
| Emprendimiento VCM | Registro inicial pedia pregunta independiente pendiente pese a AO05 observado | G02Q95/AO05 separado para VCM; no inferir SIT_LAB |
| Destino de Excel de trabajo | La separacion inicial envio todos los XLSX a 05_ANALISIS | Excepciones explicitas en 02_SALIDAS; controles internos permanecen separados |
| Patagonia | Word reconocia PTG pero comunicaciones lo convertia a OTRA y solo exportaba dos sedes | General mas tres sedes; PTG/PATAGONIA conservado |
| Total Patagonia en manifiesto | El control independiente lo registraba, pero collect_totals no tenia df_bd_ptg | Agregado filas_patagonia al manifiesto |
| Salidas omitidas en manifiesto | El manifiesto inventariaba archivos existentes; no explicaba las omisiones | Decisiones condicionales con regla, casos, estado y motivo |
| Todos los elegibles y pendientes | La lista historica tenia nombre ambiguo y mezclaba completos con pendientes | Dos archivos diferenciados; SI no entra en pendientes |

Fuentes de comparacion: .local/restauracion_seguimiento_20261013/antes contiene
copias previas del adaptador, generadores y ruteo. Sus ANTES.json y VALIDACION_FINAL
registran hashes y cotejos. .local/comunicaciones_sedes_20261013/ANTES.json y
VALIDACION.json conservan la evidencia de los cinco archivos y Patagonia.
Estos expedientes son privados, ignorados por Git; no publicar datos de estudiantes.

Los cambios de destino, la separacion del Word interno, las exclusiones por
trayectoria y la sustitucion de la metrica temporal antigua por fecha de envio
son decisiones documentadas, no eliminaciones inadvertidas de archivos o respuestas.
Las preguntas retiradas del instrumento 2027 tampoco se deben recrear solo para
reproducir una tabla 2026. El proceso 2026 permanece congelado.

## Lo que dice y no dice el manifiesto

La corrida 132949, copia Escritorio 133041, declara estado OK y codigo 0,
11 salidas operativas, 21 archivos de auditoria y 6 de analisis. Registra 262
elegibles, 14 respuestas completas, 1 incompleta, 247 sin respuesta y 25 CSV diarios.
La conciliacion de tres sedes se encontraba en CONTROL_COMUNICACIONES_SEDES;
filas_patagonia no estaba en los totales del manifiesto principal. Las dimensiones
de los XLSX eran null: solo CSV tenia conteo de filas en ese inventario.

Un estado OK y hashes prueban finalizacion e identidad, no que todos los
comportamientos anteriores se hayan conservado. La correccion registra las
decisiones de eliminados en ventana y de comunicaciones: GENERADO o
OMITIDO_SIN_CASOS, cantidad de casos, columnas, motivo y ruta. La presencia del
archivo debe coincidir con la decision o el registro bloquea la ejecucion.
El resumen de ejecucion reproduce esas decisiones. Para los demas XLSX no se
inventa un conteo de filas: algunos incluyen titulos, varias hojas y resumenes.

Los informes de resumen pueden conservar ceros medidos y hojas de respaldo.
No se cambio globalmente el default skip_if_empty ni se eliminaron retrospectivamente
archivos vacios. Consolidado de eliminados y financiamiento mantienen su contrato;
no extender una regla de detalle a otro informe sin una decision explicita.

## Gobernanza local y Git

Estado observado antes de la publicacion autorizada del 2026-10-13:

El manifiesto de ejecucion no sustituye el registro de cambios ni un commit.
En esta auditoria el adaptador, varios generadores 2027 y las politicas nuevas
siguen sin seguimiento en Git, aunque existen en el proyecto y se ejecutan.
No afirmar que estan publicados en GitHub. El ultimo HEAD no contiene estas
versiones locales y no se realizo commit ni push con esta tarea.

La carga PES sigue fuera del cierre diario; RAZ_INT_6 tiene un cruce no univoco
pendiente. No se omitio su control ni se reconstruyo una respuesta para pasarlo.
No es una nueva perdida atribuida al cambio de carpetas o al archivo vacio.

Pruebas nuevas: tests/test_salidas_condicionales_2027.py. Incluyen cero casos,
casos presentes, archivo inesperado con cero, falta de archivo con casos,
total incoherente, total Patagonia y contrato 2026 sin cambios.

## Validacion de la correccion

Corrida 2027_P1_134757, copia Escritorio Caracterizacion_2026-10-13_2027_P1_134848:
codigo 0. El Excel de eliminados en ventana no existe en OneDrive ni en la copia.
El manifiesto registra OMITIDO_SIN_CASOS, filas 0, motivo CERO_CASOS_EN_EL_CORTE
y la regla GENERAR_SOLO_CON_CASOS. Tambien contiene filas_patagonia = 7.

Hay 10 entregas operativas, 21 archivos de auditoria y 6 de analisis interno.
Las otras cifras de negocio coinciden exactamente con la corrida previa.
Se verificaron las celdas de los 24 libros restantes y el contenido de ambos
Word, sin diferencias. Los CSV conservan sus hashes. Los 43 archivos anteriores
y las 51 referencias congeladas de 2026 siguen intactos.

Pasaron 140 pruebas focalizadas. La evidencia privada esta en
.local/auditoria_cambios_salidas_20261013/VALIDACION.json. Este registro permanece
local; no se realizo commit ni push ni se modificaron los manifiestos historicos.

## Publicacion posterior autorizada

El usuario autorizo actualizar GitHub despues de esta auditoria. El codigo y las
reglas se publicaron en main mediante el commit
756c6f17dc42ab9c2d6d19f9425a95f065142d26, cuya identidad se verifico en la API de
GitHub. La evidencia de publicacion y el inventario exacto del paquete estan en
PUBLICACION_GITHUB_2027_P1_20261013.json. Las menciones anteriores a cambios locales
conservan el estado historico observado; ya no describen el estado del codigo.

La copia limpia del paquete paso 140 pruebas operativas y 16 de lectura/seleccion
LimeSurvey, y verifico las 51 referencias congeladas. Las bases, respuestas,
participantes y QA individuales nuevos no forman parte de esta publicacion.
Publicar el codigo no libera la carga PES ni resuelve automaticamente RAZ_INT_6.
