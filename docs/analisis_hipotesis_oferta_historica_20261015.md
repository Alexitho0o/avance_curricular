# Hipótesis de origen y versiones: oferta histórica, MRUN y UMAS

Fecha de revisión: 2026-10-15. Este documento conserva el diagnóstico inicial.
Su estado de implementación y las precisiones posteriores se encuentran en
[Unificación y reglas de negocio](unificacion_proyectos_y_reglas_negocio_20261015.md).
Las referencias siguientes a trabajo futuro describen ese momento anterior.

**Precisión del usuario y actualización:** para este diccionario, inicio significa
primera oferta del Código Único completo, aunque no tenga matrícula. No se
reemplaza esta regla interna por Año Inicio formal ni por la primera matrícula.
Logística regular V1 inicia en la oferta disponible en 2024; continuidad V2,
en 2025: se calculan por separado. La regla ya se ejecutó para los 141 códigos,
con oferta localizada para 139 y sin atribuir años a los dos restantes. El CSV
nacional íntegro y los manuales están conservados dentro del proyecto.

En el diagnóstico inicial no se modificaron Excel, maestro H5, reglas ni
consumidores. Después, con autorización del usuario para un solo repositorio,
se incorporó Caracterización como módulo y se centralizaron sus recursos SIES.
El Excel, H5 y las equivalencias efectivas siguen intactos. No se publicó en remoto.

## Dictamen

La oferta histórica permite reconstruir la primera observación de cada Código
Único, sus atributos anuales y las versiones sin matrícula MRUN. Es una evidencia
necesaria para discriminar candidatos. No acredita por sí sola la creación de
cada malla UMAS ni una correspondencia entre el ordinal SIES y las sucesivas
mallas internas. La hipótesis temporal aislada no es suficiente; es viable
continuar con una hipótesis compuesta por identidad, perfil académico, cronología
y evidencia de equivalencia del plan.

El glosario, página 2, define Versión como diferenciación por contenidos o
atributos entre programas de igual nombre, sede y jornada; incluye duración,
arancel y plan especial como ejemplos. No define una secuencia de reemplazo
curricular. Año Inicio refiere al inicio de actividades académicas con ingreso
de estudiantes de la carrera/programa en la sede. Mantener separadas estas fechas:

- Año Inicio declarado, por fila y edición de oferta.
- Primer año observado de oferta del Código Único.
- Primer año observado de matrícula MRUN del Código Único.
- Primer año de actividad UMAS que acompaña la etiqueta de plan en el reporte.
- Inicio efectivo acreditado de la malla y de su equivalencia SIES, si existe.

El mínimo de las observaciones disponibles no es automáticamente la fecha de
creación. MRUN acredita matrícula observada, no todas las ofertas ni todas las
asignaciones históricas de malla. Tampoco se puede usar el año incrustado en
CODPESTUD como fecha efectiva sin documentación de su significado.

## Lectura de las fuentes solicitadas

Se recorrió el CSV completo, con `csv.reader`, delimitador `;`, sin filtro previo
de institución, verificando el ancho de cada fila y la unicidad de Año/Código Único.
Se utilizaron valores textuales. La decodificación Windows-1252 estricta falla por
el byte 0x90; Latin-1 permitió una lectura reversible de todos los bytes, sin
reemplazarlos. No se afirma que Latin-1 sea la codificación declarada por el emisor.
Se detectaron 55 bytes del rango C1: 0x96 (7), 0x86 (8), 0x90 (39) y 0x84 (1).
La futura extracción debe preservarlos y señalar su tratamiento; no sanearlos
silenciosamente ni usar `errors=ignore`.

| Fuente | Resultado de lectura |
|---|---|
| CSV `Oferta_Academica_2010_al_2026_SIES_12_01_2026_WEB_E.csv` | 260.681.549 bytes; 395.719 registros; 69 columnas; 220 códigos IES; 2010–2026; cero claves Año/Código Único duplicadas |
| Subconjunto IES 162 del CSV | 747 registros; 139 códigos; 51.543 celdas cotejadas con H3, todas iguales; ninguna clave institucional exclusiva de una edición |
| XLSX histórico H3 `Oferta_Academica_2010_al_2026_SIES_05_06_2026_WEB_E.xlsx` | La auditoría H3 registra 396.003 filas nacionales; 747 de IES 162 |
| Glosario solicitado | Se leyeron las seis páginas; mismo SHA-256 que el PDF ya conservado en el proyecto; tabla de página 6 totaliza 396.003 |

El CSV tiene 29.627 registros de 2026; el glosario/XLSX H3, 29.911: diferencia
neta de 284. Los conteos 2010–2025 coinciden con la tabla del glosario. Esto no
prueba que las únicas diferencias nacionales sean 284 altas: no se hizo aquí
comparación de todas las celdas nacionales entre CSV y XLSX. Sí se compararon
íntegramente las 747 filas y 69 campos de IPSS con el extracto H3, previamente
verificado contra el original XLSX. El nombre del archivo no se usa como prueba
independiente de fecha de corte. Ambas ediciones se deben conservar diferenciadas.

La fase 3 ya había construido la historia institucional. Este CSV no agrega
fechas ni atributos distintos para IPSS. La mejora pendiente está en su uso para
discriminar candidatos UMAS y en la portabilidad íntegra de las fuentes.

Huellas verificadas:

- CSV solicitado: `f3e2222dbdc710226fe86f71f543916781af5744117e52b03ddf8551552fcded`.
- PDF solicitado y copia del proyecto: `ea7d518b719aa2d494e5a10c77b9144d25496440999fbfe4feec9bd090f7c046`.
- Extracto IPSS H3: `c3bc04a39816792c144e846c74da723b2c842627d5724141e1802a82407f455a`.
- Excel editado por Alexi, leído en esta revisión: `f6431d9bf571a4db0769cf8f4d5b90eee95413477406ddf9a328e657a85298dd`.

Procedencia externa del CSV/PDF: carpeta `0 BASES DE DATOS/OFERTA ACADÉMICA`
del OneDrive institucional indicado por el usuario. La fase A debe eliminar
esa dependencia de ejecución; registrar procedencia no equivale a empaquetar
los datos ni a respaldarlos en GitHub.

## Cambios de sector del usuario

Comparación por Código Único de `Diccionario SIES`, filas 6–146, contra
`data/versiones_historicas_sies_umas/fase_8_20261015/libro.json`:

- 63 códigos cambiaron Sector IPSS 2026 (S) y Estado sector (T).
- Los 63 estados nuevos dicen `ACTUALIZADO POR ALEXI`.
- 61 sectores anteriores se conservan; 124 códigos tienen sector y 17 no.
- No hay cambios en las otras 20 columnas de datos de esta hoja.
- Distribución actual: Tecnología 64; Administración y Comercio 30; Salud 9;
  EDUCACIÓN CONTINUA 21; sin sector 17.
- Evidencia sector (U) no fue rellenada en las 63 incorporaciones. La nueva
  edición debe registrar como procedencia la edición del usuario y su celda;
  no atribuir esas clasificaciones a una fuente SIES ni sobrescribirlas.

El alcance de esta comparación son las 22 columnas de la tabla Diccionario
SIES, no una certificación de todas las hojas o fórmulas del archivo editado.
Sector es un atributo gobernado de clasificación; no demuestra equivalencia
curricular y no debe usarse para elegir entre versiones.

## Pruebas de la hipótesis

Sobre las 747 observaciones IPSS: 100 familias institución/sede/carrera/jornada;
31 presentan varias versiones; 167 combinaciones familia/año tienen versiones
coexistentes; 10 familias ya tienen varias versiones en su primer año observado.
En 12 familias al menos dos códigos comparten el mismo año de primera oferta.
Ocho códigos ya estaban presentes al inicio de la cobertura de oferta, 2010.
En cinco códigos cambia Año Inicio entre valores no nulos/no cero. Se conservan
esas declaraciones anuales en lugar de escoger una fecha arbitraria.

### Ejemplos comprobados

Los nombres de la siguiente tabla son literales de oferta; tipo de plan,
jornada, modalidad y versión son atributos separados.

| Nombre | Evidencia SIES y MRUN | Evidencia UMAS y consecuencia |
|---|---|---|
| INGENIERIA EN LOGISTICA | I162S2C77J4V1: primera oferta/MRUN 2024, regular de 8 semestres. I162S2C77J4V2: primera oferta/MRUN 2025, continuidad de 4 semestres. Ambos declaran Año Inicio 2024. | ILOG20241 tiene 12 niveles y actividad 2024–2026; CILOG20241 tiene 6 niveles y actividad 2025–2026. Los reportes indican TRIMESTRAL para ambos. El perfil apoya ILOG→V1 y CILOG→V2, pero el año 2024 en ambas etiquetas no discrimina y la oferta informa régimen semestral. Documentar la equivalencia de duración/régimen antes de convertirla en regla. |
| NATUROPATIA | I162S2C90J2V1: oferta desde 2025, continuidad, 4 semestres, sin observación MRUN. V2: oferta/MRUN desde 2026, regular, 8 semestres/12 trimestres. | NATP20251 tiene 12 niveles y actividad TRIMESTRAL observada en 2026. El perfil es compatible con V2. Usar “2025” del identificador como inicio y elegir V1 sería un salto no respaldado. La correspondencia es una hipótesis fuerte de perfil, aún no equivalencia certificada. |
| INGENIERIA EN CIBERSEGURIDAD | I162S2C46J2V1/V2/V3 aparecen en oferta y MRUN desde 2019; duraciones de estudios 8/5/4 semestres; V1 regular y V2/V3 continuidad. Los tres declaran inicio 2019. | Ordenar por año no separa estas versiones; se necesitan tipo de plan, duración y evidencia del plan interno. V2 debe mantenerse aunque no esté en la oferta 2026. |
| TECNICO EN ANALISIS DE SISTEMAS | I162S2C35J4V1 informa 5 semestres en 2017–2018 y 6 desde 2019, conservando V1. V2 aparece en 2019 con 6. MRUN observa ambas desde 2019 durante años coexistentes. | ASREOL y TASREOL20191 son planes diferentes del catálogo; no tienen candidatos de plan para esta familia en H5. Su vinculación histórica requiere ampliar la evidencia del puente, no inventar una nueva versión por cada cambio de duración. |

Localizadores del CSV (número de registro lógico contando encabezado como 1;
no necesariamente línea física): Logística 2026, 26338–26339; Naturopatía 2026,
26357–26358, y 2025, 54161; Ciberseguridad 2019, 206466–206468; Análisis de
Sistemas V1, 249927 (2017), 228975 (2018), 206452 (2019).

No se asignaron códigos a partir de estos ejemplos. En particular, número de
niveles no se convierte automáticamente en semestres: en el catálogo el régimen
de asignatura es S incluso para los planes cuyo reporte informa TRIMESTRAL.
El significado y las unidades de cada campo deben quedar documentados.

### Prueba exploratoria de usar únicamente la cronología

Se agruparon las 513 relaciones H5 por CODCARPR, plan, sede, jornada y nombre
interno: 293 grupos, incluido uno con jornada ausente que H8 no permite consultar
como clave completa. De ellos, 192 tienen años de actividad y 105 son ambiguos.
Como experimento, se retuvieron candidatos cuya primera oferta no fuera posterior
a la primera actividad UMAS. De los 105 ambiguos, 101 siguieron ambiguos, tres
quedaron con un candidato y uno sin ninguno. En todos los 192 grupos hubo seis
sin candidato tras ese filtro. Los 101 sin año de actividad no se evaluaron.

Este experimento no es una regla válida ni acredita tres resoluciones: usa el
puente de candidatos 2026 fuera de su ámbito temporal, y la etiqueta del plan en
PROMEDIOS no acredita asignación efectiva en cada año de actividad. Precisamente
sirve para demostrar que aun aceptando esos supuestos la fecha no resuelve la
mayoría. No se aplicó ningún descarte al maestro.

También se compararon 15 atributos académicos de oferta 2026 dentro de cada
familia: nombre, modalidad, tipo de carrera, plan especial, tres duraciones,
régimen, duración formal del régimen, título, grado, dos niveles, requisito de
ingreso y semestres reconocidos. Doce familias contienen versiones con perfiles
iguales en esos campos. Sus años declarados difieren; falta acreditar con qué
malla UMAS y vigencia corresponde cada perfil. La combinación de fechas y
atributos ayuda, pero la fuente SIES no contiene CODPESTUD.

H5 incluye 141 códigos y 236 planes internos; 38 códigos no tienen relación
candidata de plan y 87 planes no tienen candidato SIES. Conservarlos en el
universo. El número de códigos/mallas no obliga a una biyección: una versión
SIES puede requerir varias asociaciones internas documentadas. MRUN 2007–2009
y los dos identificadores heredados de 2008 no obtienen cobertura de oferta por
añadir un archivo que comienza en 2010.

## Plan propuesto: tres fases adicionales

Las fases A–C complementan H1–H8; no reinician ni renumeran el trabajo anterior.
No se ejecutan como parte de este diagnóstico.

### Fase A — Fuentes completas y cronología gobernada

**A1. Preservación íntegra.** Incorporar al proyecto el CSV nacional completo,
con sus 395.719 registros y 69 columnas, encabezados, vacíos, orden y valores
originales. Conservar también el original XLSX de H3 como otra edición, sin
sustituirlo por el CSV. Para el CSV de 260 MB, usar contenedor comprimido sin
pérdida o almacenamiento versionado apropiado, comprobando SHA-256 al recuperar
los bytes originales. Evitar depender de Downloads/OneDrive/rutas personales.

Conservar el PDF completo existente y extraer las seis páginas íntegramente;
gobernar las 69 columnas con tipos, significado, unidades, dominio, disponibilidad
anual y localizador documental. No tratar vacío histórico como cero ni como
"no aplica". La selección IPSS y las proyecciones analíticas serán derivados
adicionales; nunca reemplazarán la fuente nacional completa. Comparar las
ediciones nacionales sin suponer que una diferencia de conteos identifica las
únicas filas cambiadas. Validar campos y totales por edición de forma explícita.

**A2. Edición del usuario.** Capturar el Excel actual con su huella y extraer la
tabla sector/estado por Código Único, conservando literalmente las 63 decisiones
de Alexi, sus celdas y procedencia. Validar los 141 identificadores y registrar
los 17 sectores pendientes sin rellenarlos por semejanza.

**A3. Cronología.** Extender la historia H3 con las fechas separadas definidas
arriba, coexistencias, períodos sin observación y conflictos de Año Inicio.
Conservar versiones sin oferta 2026 o sin matrícula, y estados de cobertura
limitada para 2007–2009. No cerrar una versión por la aparición de otra.

**Aceptación A:** recuperación byte a byte de fuentes completas; todas las
filas/columnas conciliadas; 747 observaciones y 139 códigos de oferta IPSS
reproducidos; 141 códigos históricos conservados; cambios de sector preservados;
rutas de ejecución relativas; confirmar qué activos están seguidos por Git y
qué activos están publicados remotamente. Un hash solo no acredita respaldo.

### Fase B — Equivalencias por perfil y vigencia acreditada

**B1. Claves y unidades.** Mantener la familia SIES ya reconstruida. Vincular
Código Único y componentes exactos con año de oferta/MRUN. En UMAS conservar
CODCARPR + CODPESTUD + sede + jornada + nombre interno, con año, período y régimen
del contexto consultado. Documentar equivalencias de sede/jornada/modalidad y
unidades de duración; MODALIDAD escolar de DatosAlumnos no es modalidad SIES.
Usar claves estructuradas o concatenación escapada para evitar colisiones.

**B2. Discriminación.** Dentro de cada familia contrastar plan regular/continuidad,
duración, régimen, requisitos de ingreso, semestres reconocidos, título y
estructura de malla. Un dato ausente en cualquiera de las fuentes queda como
desconocido; no se deduce por prefijo, sufijo, nombre parecido o posición de fila.
Separar estructura académica compatible de una equivalencia temporal acreditada.
Conservar nombres SIES 2026 literales, con modalidad y tipo de plan aparte.

**B3. Cierre de evidencia.** Buscar primero en las fuentes gobernadas y reportes
ya disponibles la relación plan↔código y su vigencia. Para los casos que no se
puedan demostrar, identificar el documento o extracción faltante: catálogo
institucional de planes por oferta, resolución/tabla de equivalencias o historial
de asignación por período. La fuente SIES por sí sola no puede aportar CODPESTUD.
Generar relaciones con evidencia, intervalo y estado: acreditada, candidata,
contradictoria o sin evidencia. Si el alcance permite varias mallas por SIES,
guardar todas; la consulta inversa puede devolver una lista documentada.

**Aceptación B:** cada uno de los 141 códigos y los 236 planes tiene un estado
explícito, evidencia o brecha concreta. Una regla habilitada debe producir una
sola versión por clave UMAS completa y período, sin contradicciones ni intervalos
superpuestos. Medir cobertura real; no declarar 100% asociado por rellenar
candidatos. Los cuatro ejemplos y los perfiles indistinguibles deben probarse.
Si falta evidencia no se habilita ese caso; se conserva para investigación.

### Fase C — Publicación del diccionario y consumo reproducible

**C1. Nueva edición.** Crear una revisión del maestro y de las reglas; preservar
H5/H7/H8 para comparación. Regenerar el Excel con cronología, perfil, asociación,
evidencia y estado, manteniendo los sectores de Alexi. La persona consulta
criterios y recibe la misma respuesta; no elige manualmente versión ni candidato.

**C2. Integración y regresión.** Publicar el mismo contrato de consulta para
avance_curricular y CARACTERIZACIÓN. Verificar paridad, claves históricas,
coexistencia, continuidad, oferta sin matrícula, planes sin actividad, conflictos
de nombres/unidades y períodos sin fuente. Mantener el ámbito anual explícito y
MU2026 congelado. No trasladar una regla 2026 a todo el histórico.

**C3. Entrega portable.** Probar generación/consulta desde una copia limpia del
proyecto, sin las rutas originales del PC. Validar fuentes por hash, fórmulas y
valores del Excel, incluyendo cálculo nativo cuando esté disponible. Confirmar
seguimiento y respaldo remoto de los activos completos y del glosario antes de
declarar portabilidad total. La distribución tendrá documentación, fuentes,
reglas, resultados, pruebas y manifiestos de la misma edición.

**Aceptación C:** iguales entradas producen iguales respuestas en ambos
consumidores; toda asociación publicada tiene evidencia; no se pierden versiones
históricas ni decisiones de sector; las fuentes completas pueden recuperarse;
se reportan por separado asociaciones acreditadas y brechas pendientes.

## Referencias internas de la revisión

- [H3, historia de oferta](fase_3_oferta_historica_sies.md).
- [H4, estructura y límites temporales UMAS](fase_4_planes_asignaciones_umas.md).
- [H5, maestro](fase_5_maestro_equivalencias.md).
- [H8, Excel y control](fase_8_excel_diccionario_gobernado.md).
- `data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json`.
- `data/versiones_historicas_sies_umas/fase_4_20261015/catalogo_planes.json`.
- `data/versiones_historicas_sies_umas/fase_4_20261015/estructura_asignaturas.json`.
- `data/versiones_historicas_sies_umas/fase_6_20261015/consultas_umas.tsv`.
- `oferta_academica_2027/06_validaciones/historico_comparativo_sies_162/REGISTROS_HISTORICO_SIES_162_20260817_161944.tsv`.
- PDF completo: `oferta_academica_2027/01_fuentes_oficiales/historico_comparativo_sies_162/20260817_161807_sies_historico_2010_2026/Glosario_Oferta_Academica_2010_al_2026_SIES_WEB_EE-1.pdf`.
