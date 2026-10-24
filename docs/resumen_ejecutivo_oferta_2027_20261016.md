# Resumen ejecutivo anual y preparación de planes 2027

Especificación previa. El usuario solicita una primera hoja ejecutiva en el
diccionario final y columnas preparadas para 2027, aclarando que los Códigos
Únicos definitivos todavía no están disponibles. Crear una edición separada
de D4, preservando sus 21 hojas, sectores y fórmulas; no promover equivalencias.

La serie histórica utilizará la oferta nacional completa preservada en el
proyecto (CSV 2010–2026), filtrada por institución 162 y contrastada con la
historia H3. Los años 2007–2009 mostrarán ausencia de cobertura, nunca cero.
Se distingue total de códigos de cada año, primera aparición observada,
entradas/salidas frente al año anterior y variación neta. El año 2010 es base
observada, no prueba creación de todos sus códigos ese año.

2027 se presenta como escenario esperado derivado de los cinco componentes del
6047, no como códigos definitivos confirmados. La columna de código confirmado
queda vacía. La clave compuesta provisional se conserva en otra columna para
trazabilidad. Incluir los 161 registros, separando pregrado y diplomados para
mantener denominadores comparables con 2026. No equiparar código, carrera,
tipo de plan y malla UMAS.

La preparación UMAS utilizará las dimensiones agregadas del filtro matrícula
2027/período 1 de 12023. Preparar código SIES confirmado, CODPESTUD, versión de
malla, vigencia y respaldo como pendientes. No extrapolar planes históricos a
2027 ni interpretar el año de matrícula como ingreso. Los 236 planes históricos
permanecen en sus hojas originales; si falta dato para contar mallas 2027 se
mostrará «Por confirmar», no un número inventado.

Se autoriza el cambio de orden para situar Resumen ejecutivo primero. Autoría
con Artifact Tool, tablas y fórmulas trazables, gráfico de evolución, revisión
visual y QA de preservación/conciliación. Paquete aislado en
`data/resumen_oferta_2027/20261016`; entrega en `outputs/diccionario_ejecutivo_2027_20261016`.

## Resultado y significado de los conteos

La oferta publicada de 2026 contiene 124 códigos distintos: 103 de pregrado
y 21 de postítulo/diplomados. El escenario 6047 para 2027 contiene 161 claves
compuestas distintas: 140 de pregrado y los mismos 21 diplomados. Se esperan
37 claves adicionales, sin ausencias frente a 2026: aumento neto de 29,84 %
en el universo completo y 35,92 % en pregrado. Las 37 también son nuevas frente
a toda la historia de oferta 2010–2026 disponible; no solo frente a 2026.

Estas son combinaciones de institución, sede, carrera, jornada y versión.
No son 37 nombres de carrera ni 37 mallas. El escenario conserva la estructura
propuesta del reporte, sujeto a confirmación definitiva de SIES. Las columnas
«Código Único confirmado 2027» permanecen vacías, por indicación del usuario.

Las combinaciones de pregrado esperadas se distribuyen en 118 de plan regular
y 22 de continuidad. Los 21 diplomados se muestran separados. El catálogo UMAS
histórico conserva 236 planes, pero el extracto 12023 no contiene CODPESTUD.
Los 346 registros del filtro 2027 P1 representan 67 CODCARPR y 72 dimensiones
de carrera/sede/jornada, no 72 mallas acreditadas. Por eso el total de mallas
2027 aparece «Por confirmar», con cero planes documentados en las columnas nuevas.

La serie institucional tiene 747 filas código-año, verificadas contra las claves
históricas H3, y la preparación agrega 161 filas esperadas para 2027. Se incluye
todo el universo de oferta, sin filtrar estudiantes activos ni excluir oferta
sin nuevos ingresos. Los primeros años sin fuente (2007–2009) no se rellenan.
El cálculo de primera aparición conserva el límite inferior 2010 y se distingue
del cambio neto de oferta, que puede ser negativo.

## Uso de la nueva edición

La primera hoja, activa al abrir, es **Resumen ejecutivo**. Las 21 hojas D4
siguen a continuación sin cambiar sus datos ni sus contratos. Se agregan también
Serie oferta, Preparación oferta 2027 y Preparación UMAS 2027, para un total de
25 hojas. El resumen tiene indicadores, serie anual, gráfico, composición por
tipo de plan y explicación de la proyección.

Las columnas amarillas permiten registrar futuras confirmaciones. La clave
compuesta del 6047 está separada del código confirmado; candidatos del catálogo
previo no se convierten en confirmaciones. Plan, versión de malla, vigencia y
respaldo se completan solo con evidencia. Los contadores deduplican códigos y
planes dentro de las filas de preparación existentes y excluyen blancos.
Si un contexto requiere varias mallas, se debe ampliar el detalle y sus rangos
en una nueva edición, sin escribir una lista de planes como si fuera un único ID.

Las tablas no acreditan una relación uno a uno entre Código Único y malla.
Los planes históricos no se asignan automáticamente a estudiantes 2027 ni se
extrapola la primera observación como fecha de ingreso.

## Fuentes y reproducción

La serie usa el CSV nacional completo comprimido en
`data/reglas_negocio/20261015/fuentes/`, y coincide en las 747 claves con H3.
Para 2027 se leyó íntegro el 6047 al inicio: 161 filas y 51 columnas, SHA-256
`4edfefaabf449b35163fa090ecac39649ecaf6aab10bbe3a4ef7e83a244f8e62`, coincidente
con la fuente gobernada del 13 de octubre.

Antes de guardar una copia íntegra nueva, el CSV y su ZIP dejaron de estar en
las rutas de Descargas utilizadas; tampoco se localizaron por su nombre en la
búsqueda posterior en OneDrive. No se presupone la causa. Se conservaron las
161 filas y las 14 columnas necesarias para este resumen, retenidas en la
preparación inicial, en `fuentes/oferta_2027_dimensiones.json`. Este derivado
permite reproducir los resultados, pero **no es un respaldo de las 51 columnas**.
La copia íntegra del 6047 queda pendiente de volver a disponer del mismo archivo;
no se reconstruyen sus otras columnas ni se reemplaza por una edición diferente.

Preparación: `python3 scripts/preparar_resumen_oferta_2027.py`.
Autoría: `node data/resumen_oferta_2027/20261016/autor/generar_ejecutivo.mjs`,
con la dependencia Artifact Tool configurada. El modo `--preview` solo inspecciona D4.
Orden y QA: `python3 scripts/verificar_resumen_oferta_2027.py --ordenar`.
El orden se aplica únicamente a metadatos OOXML porque la superficie documentada
de autoría consultada no expone la operación de mover una hoja. Se conserva
la asociación de nombres locales y se selecciona el resumen al abrir.

La preparación no necesita Descargas: consume el derivado de oferta, la fuente
histórica y la auditoría agregada 12023 ya preservados. Esto no equivale a
portabilidad de los microdatos ni a publicación en GitHub. No se modifican el
catálogo anual activo, las equivalencias ni los archivos fuente del usuario.

## Validación final

Resumen ejecutivo es la primera hoja y la activa al abrir. Las 25 hojas incluyen
las 21 anteriores conservadas. Se compararon 154.513 celdas D4 con sus fórmulas
y formatos, y 22.501 celdas de las nuevas tablas; se conservaron tablas, filtros,
validaciones y paneles. Los atributos y sectores del diccionario previo siguen
intactos dentro de esa comparación completa.

Se comprobaron las 18 filas anuales con cobertura (2010–2027), indicadores
124/161/+37, composición 118/22/21, 236 planes históricos y contadores confirmados
en cero. Se probaron entradas repetidas y blancos; los valores de prueba se
retiraron antes de exportar. No hay errores de fórmula detectados en la caché.
Se revisaron visualmente el resumen, gráfico y hojas nuevas; no se comprobó
recálculo en Excel nativo. La preparación y el manifiesto se reprodujeron
idénticos usando solo archivos del proyecto.

Las 137 referencias protegidas y los 35 archivos de la entrega D4 mantienen
sus huellas. Evidencias: `data/resumen_oferta_2027/20261016/qa.json`,
`qa_formulas.json` y `entrega.json`. La nueva edición se entrega separada,
sin sobrescribir D4 ni publicar cambios en remoto.
