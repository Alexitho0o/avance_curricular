# Revisión de discrepancias y mallas observadas · 26-10-2026

## Alcance

Retención intertrimestral IPSS 162 y avance curricular institucional; actividad 2026 en períodos nativos 2 y 3 y exploración histórica de mallas a partir de PROMEDIOS 12166. No se alteraron bases, diccionario, reglas de vigencia, tasas ni denominadores. A/B/C/D/E separan norma, observación, cálculo, decisión interna e información pendiente.

## Discrepancias

- **[B/C] Notas:** en T3-2026 las mismas 653 llaves académicas tienen nota vacía en el respaldo ampliado y cero en 12166; abarcan 585 personas. Los campos de estado de asignatura están vacíos. Las fotografías consultadas no traen la nota. Es posible mostrar ambos valores y aplicar la prioridad operativa de Alexi a PROMEDIOS, sin convertir vacío en cero ni declarar aprobación o reprobación. La corrección y su causa permanecen **E**. Estas llaves no son las mismas unidades que las 529 observaciones v11 con alerta.
- **[B/C] Secciones:** nueve pares T3-2026 identifican el mismo expediente, plan y asignatura en secciones distintas; las fotografías revisadas no contienen `CODSECC`. Se conservan ambas secciones con procedencia; no existe evidencia suficiente para determinar cuál corresponde al cierre ni el motivo del cambio **[E]**. Ocho observaciones v11 llevan alerta: no equivalen a nueve pares.
- **[B/C/D] Estados:** para dos expedientes de T2 el respaldo PROMEDIOS dice VIGENTE y 12166 SUSPENDIDO; la foto T2 carece de columna de estado. Para un expediente T3, la foto dice VIGENTE y 12166 ELIMINADO. Según el criterio interno autorizado, puede exponerse el estado del extracto 12166 como preferido para seguimiento, junto al estado de la foto. La fecha de cambio y el estado efectivo en el cierre siguen **E**; no se reescribe el pasado.
- **[E]** La fecha y cobertura completas de 12166 no están certificadas. La prioridad operativa no demuestra cuál valor es correcto para cada cierre.

Fuentes y cifras: [revisión detallada previa](../qa_promedios_cobertura_20261026/INFORME_RECONSTRUCCION_FOTOS_T1_T2_T3.md), [diferencias por llave](../qa_promedios_cobertura_20261026/INFORME_DIFERENCIAS_ASIGNATURA.md) y [metadata de la capa integrada](../qa_promedios_cobertura_20261026/RESULTADO_CAPA_V11_PROMEDIOS_INTEGRADA.json). Las alertas ya se muestran en los tres consumidores; no se adjudicó una causa sin evidencia.

## Niveles y malla

- **[C]** La conversión gobernada del nivel administrativo trimestral a `NIV_ACA` se aplica bajo condiciones de régimen; no transforma automáticamente el `NIVEL` de una asignatura en avance aprobado ni convierte todo período académico en trimestre. Ver [seguimiento y conversión](../../docs/SEGUIMIENTO_RUT_Y_CONVERSION_PERIODOS_20261023.md).
- **[B]** `Listado_Planes_estudio_Sedes RE+CO.xlsx`, hoja `BBDD Bruta`, incluye `Codcarr`, `Nombre_L`, `CODPESTUD`, `CODRAMO`, `NOMBRE`, `REGIMEN`, `TIPO` y `NIVEL`. Su SHA-256 es `fb3a6847dca0745a197867090a9d7d12e8bb7e53e6b421f96826ea0c5657d049`. Ruta completa en [contraste](CONTRASTE_PLANES_AGREGADO.json). Es un listado institucional; no se ha acreditado aquí su vigencia para todos los años ni que esté completo para cada plan **[E]**.
- **[B/C]** En PROMEDIOS 12166 se identificaron **75 combinaciones carrera–plan** con actividad de expedientes cuyo estado del extracto es TITULADO; se observaron **975 combinaciones plan–asignatura**. El estado del extracto no demuestra la fecha efectiva del título ni que el alumno completó la malla bajo ese plan **[E]**.
- **[B/C]** Al contrastar carrera, plan y código de asignatura contra el listado, **73 de 75 planes** tienen llave en ambos; **950 asignaturas por plan** tienen el mismo nivel único. Hay **22 asignaturas observadas fuera del listado** en esos planes y **1.303 asignaturas listadas no observadas** en los expedientes seleccionados. Las categorías cuentan combinaciones plan–asignatura, no personas. Las dos llaves de carrera–plan sin coincidencia son `NITMRE/NCONRE` y `TTMREOL/TPCPASO`; no se fuerza una equivalencia **[E]**.
- **[B/C]** Ejemplo `CIINF/CIINF20241`: el listado contiene 23 asignaturas; seis se observan en expedientes seleccionados y sus seis niveles coinciden; 17 no se observaron. Esto no prueba que falten en la carrera ni que el listado esté equivocado.
- **[E]** El inventario es una candidata descriptiva, no un diccionario definitivo de mallas. Faltan versión y vigencia del plan, comprobación de título/egreso, equivalencias de asignaturas y convalidaciones, y acreditación de cobertura por expediente. La duración de oferta no sustituye la malla ni asigna automáticamente un código SIES.

## Salidas y reproducción

- [Mallas observadas candidatas](MALLAS_OBSERVADAS_TITULADO_CANDIDATA.json): sin RUT, CODCLI ni nombres de personas; conserva asignaturas y niveles observados.
- [Contraste de planes](CONTRASTE_PLANES_AGREGADO.json): conteos y procedencia del listado.
- [Constructor exploratorio](auditar_mallas_observadas.py) y [contraste reproducible](contrastar_planes.py): comprueban los hashes de las fuentes. No modifican los originales.
- No se cambió la v11 ni sus denominadores en esta revisión. No se realizó commit ni push.
