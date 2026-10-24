# Prueba de enlaces históricos con al menos 500 personas

## Diseño previo a resultados

Solicitud: comprobar correspondencias MRUN–UMAS para al menos 500 personas de
años anteriores a 2023, usando evidencia independiente del bloqueo que produjo
la candidatura. No seleccionar solo coincidencias exitosas ni forzar totales.

Se conservan las agrupaciones carrera/sede/jornada y las fuentes congeladas. Se
localizaron reportes institucionales MAT_IP_CIISA 2018–2022 con N_DOCUMENTO y DV,
Código Único, nacimiento, sexo e ingresos. Estos aportan enlace documental a UMAS
por documento, pero no contienen MRUN. Su ubicación en Publicados no demuestra
por sí sola una certificación ministerial de cada fila. Se conservan hashes y
esquemas, sin copiar documentos personales ni exportar identidades.

Población de prueba: personas UMAS con matrícula observada 2018–2022 y documento
presente en un reporte institucional del mismo año. Selección reproducible,
estratificada por año, una persona una vez; 500 personas antes de ver resultados.
El ancla es el año más reciente elegible y un expediente ordenado de forma fija.
La selección no usa éxito de enlace, vigencia, versión ni coincidencia de cohortes.
Este diseño representa el subconjunto documentable, no todo UMAS ni todo MRUN.

1. Proponer candidatos con año, nacimiento AAAAMM, sexo y familia ISCJ existente,
   sin V ni ingreso, conservando tipo si el grupo es unánime.
2. Contrastar, por documento, con el reporte institucional del mismo año. Reservar
   Código Único completo y cuatro campos de ingreso original/actual y semestre
   para validación; no usarlos para escoger la candidatura inicial.
3. Construir correspondencias de registro completas reporte–MRUN por año,
   nacimiento, sexo, Código Único y cuatro campos de ingreso, controlando
   unicidad por persona en ambos lados. Esa correspondencia es evidencia
   documental indirecta, no tabla oficial RUT–MRUN.
4. Contrastar en otros años 2018–2022 que no generaron la propuesta. Comprobar
   si el mismo documento del reporte recupera el mismo MRUN con perfil completo.
   Esto es evidencia longitudinal de registros distintos, sin reutilizar el ancla
   como validación temporal. Reportar contradicción y ausencia por separado.
5. Controles negativos: comparar candidatos iniciales alternativos contra los
   campos reservados. Su rechazo mide discriminación entre alternativas, no
   una tasa de falsos enlaces poblacional ni verdad de identidad.

Ningún procedimiento probabilístico ni asignación productiva. La tasa esperada
de falsos enlaces sigue no estimable sin correspondencia de identidad oficial.
Estados de salida distinguen candidato inicial, respaldo documental, respaldo
en otro año, ambigüedad, contradicción y ausencia. Solo se exportan casos con
número de ensayo, atributos académicos y resultados; sin RUT/MRUN/CODCLI, fechas
individuales, hashes personales o nombres de estudiantes.

## Fuentes efectivamente utilizadas

Se utilizaron MAT_IP_CIISA_2018.xlsx (1.088 filas, hoja MAT_2018),
MAT_IP_CIISA_2019.xlsx (1.112 filas, MAT_2019), MAT_IP_CIISA_2020.xlsx
(985 filas, MAT_2020) y la carga enviada 2022/2022.csv (1.038 filas).
Los reportes MAT_IP_CIISA de 2021 y 2022 no pudieron abrirse como libros XLSX
con el lector disponible; no se usaron ni se reconstruyeron. En 2022 se utilizó
el CSV enviado, cuya aceptación final no está acreditada por este ensayo.

Los reportes codifican sexo H/M (hombre/mujer), normalizado a M/F de UMAS y
1/2 del esquema MRUN. MC_CAT_PERIODO contiene MAT_AAAA; la fecha de los XLSX
se lee como fecha completa y la del CSV 2022 como DD/MM/AAAA H:MM. Se proyecta
AAAAMM sin día para comparar con MRUN. Se preservan los cuatro campos de ingreso
como etiquetas; los centinelas no se convierten en cohortes ordinarias. Cinco
filas de los reportes tienen una firma incompleta: tres de 2019 y dos de 2020.
Se mantienen explícitas, sin rellenarlas. Todos los archivos se verificaron por
SHA-256 antes y después. No se copiaron reportes con información personal al repo.

## Muestra y resultados

Se identificaron 1.829 personas elegibles documentables. Se seleccionaron 500
personas distintas, 125 por cada año 2018, 2019, 2020 y 2022, correspondientes a
32 códigos de carrera UMAS. Selección fija antes de evaluar éxito, con una
persona una vez, entre quienes figuran en UMAS y en un reporte del mismo año.
No se está midiendo cobertura de toda la población histórica ni precisión general.

| Año ancla | Personas evaluadas | Referencia documental unívoca y recíproca | No resueltas |
|---|---:|---:|---:|
| 2018 | 125 | 120 | 5 |
| 2019 | 125 | 115 | 10 |
| 2020 | 125 | 117 | 8 |
| 2022 | 125 | 100 | 25 |
| Total | 500 | 452 | 48 |

Las 452 correspondencias se apoyan en documento con DV para UMAS–reporte y en
firma completa de registro para reporte–MRUN, con control de unicidad en ambas
direcciones por año. Son correspondencias documentales indirectas, no una tabla
ministerial que contenga juntos RUT y MRUN. Entre ellas, 237 recuperan el mismo
MRUN en al menos otro año anterior a 2023 usando otro registro del reporte de
esa persona; ninguna de esas 237 presenta un MRUN distinto en los otros años
resueltos. Las otras 215 no tienen segundo año resuelto disponible. No se usan
nacimiento y sexo repetidos como supuesta evidencia nueva aislada.

De las 48 no resueltas, 29 tienen ambigüedad o falta de reciprocidad y 19 no
encuentran coincidencia completa (estas últimas pertenecen al CSV enviado 2022).
Una diferencia entre enviado y publicado no se interpreta como error de identidad
sin comprobar rectificaciones o ediciones. Ausencia de prueba no es prueba de error.

### Auditoría del bloqueo anterior

| Resultado de propuesta inicial frente al reporte | Personas |
|---|---:|
| Candidato único respaldado por reporte | 291 |
| Varios candidatos; reporte permite distinguir uno | 70 |
| Reporte identifica un candidato que el bloqueo no incluyó | 80 |
| Propuesta incompatible con la correspondencia del reporte | 11 |
| Referencia sin resolución suficiente | 48 |
| Total | 500 |

Las 312 propuestas inicialmente únicas se reparten en 291 respaldadas,
10 que contradicen la referencia y 11 que permanecen sin referencia resuelta.
No se puede tratar la unicidad como garantía de identidad. De las 101 propuestas
múltiples, 70 se distinguen mediante el reporte, una no contiene el candidato de
referencia y 30 carecen de referencia suficiente.

En los 91 casos en que el candidato documental no estaba en el bloqueo, se
identificaron 36 sin agrupación UMAS, 39 excluidos por tipo de plan del grupo,
8 por familia y 8 por diferencias demográficas. Esta auditoría preserva las
agrupaciones: señala dónde se requiere contexto histórico, sin rehacerlas por
nombre ni aplicar automáticamente el perfil actual a todo el pasado.

El contraste de campos reservados elimina 93 alternativas iniciales en casos
con referencia unívoca. Este conteo es consecuencia del control de compatibilidad;
no es una muestra independiente de negativos verdaderos y no estima falsos enlaces.

### Ejemplos del ensayo, sin identidades

- ENSAYO-002: TTMRE, vespertina, 2019. Candidato único concordante con
  I162S2C6J2V1 en el reporte y con el mismo MRUN en otro registro de 2018.
- ENSAYO-010: NCONRE, vespertina, 2019. Tres candidatos iniciales; el reporte
  por documento distingue I162S2C3J2V3 y el registro de 2018 recupera el mismo MRUN.
- ENSAYO-011: NICCRE, vespertina, 2020. El filtro de tipo no daba candidato;
  el reporte aporta I162S2C46J2V3 y existe respaldo del mismo MRUN en 2019.
- ENSAYO-234: NETMRE, vespertina, 2019. La propuesta única bajo
  I162S2C3J2V1 contradice el reporte I162S2C3J2V2. El MRUN de la propuesta
  tampoco coincide con el recuperado desde el reporte de 2018. El enlace
  documental corregido sí es consistente entre años; no se atribuye un cambio
  de MRUN a la persona por un candidato inicial incorrecto.

## Qué permite afirmar la prueba

Sí existe una vía para avanzar desde una coincidencia demográfica hacia una
correspondencia respaldada documentalmente. El estado recomendado separa:
- RESPALDO_DOCUMENTAL_Y_LONGITUDINAL: 237 personas.
- RESPALDO_DOCUMENTAL_UN_ANIO: 215 personas.
- PENDIENTE: 48 personas.

Estos estados no son certificación ministerial de identidad. No hay referencia
oficial RUT–MRUN explícita ni tasa de error poblacional acreditada. La prueba
permite una asignación analítica trazable de distinto nivel de evidencia si se
adopta ese contrato, pero no justifica declarar resueltos automáticamente los 500
ni activar el motor productivo. En esta tarea no se activó ni persistió un puente
nominal de identidades.

MRUN se vincula a persona/RUT; el RUT puede tener varios CODCLI. El reporte
histórico acredita código por persona/año, pero su atribución a un expediente
específico exige carrera, período y trayectoria. Los 486 casos con un único código
reportado y 14 con dos códigos no deben convertirse en una relación universal
persona–carrera uno a uno. Para gobernar la carrera SIES histórica, estos reportes
aportan además una vía directa documento→Código Único sin tener que identificar
primero el MRUN; se conserva la distinción persona, expediente y plan.

## Entrega y controles

[500 casos sin identificadores](../data/prueba_500_enlaces_historicos/20261016/casos_500_sin_identificadores.json),
[resumen](../data/prueba_500_enlaces_historicos/20261016/resumen.json),
[fuentes y hashes](../data/prueba_500_enlaces_historicos/20261016/manifest.json).

Reproducción: `python3 scripts/probar_500_enlaces_historicos.py`.
No se modificaron fuentes, Excel ni 137 referencias protegidas. Los resultados
están en el repositorio local, sin commit ni publicación remota.
