# T2-2026: renuncias y escenario por personas

**E — Resultado:** no se localizó una nómina individual que acredite cuáles son las 66
renuncias del resumen T2. No se declara cerrada la tasa por personas. Se conservaron
fuentes, denominadores, reglas y V16. Sin commit ni push.

## Lo comprobado

| Clasificación | Hallazgo | Fuente y ubicación |
|---|---|---|
| B | 528 matrículas/CODCLI y 527 RUT distintos; una persona tiene dos matrículas, en CONG y TAMD. Todas las filas tienen ingreso y matrícula 2026/P2. | T2 congelado, Hoja1, filas2:529; columnas CODCLI, RUT, CODCARPR, ANOMATRICULA, PERIODOMATRICULA, ANOINGRESO, PERIODOINGRESO. |
| B | Las66 renuncias están como constantes agregadas por carrera. No hay estado individual ni bandera de renuncia en la base. | T2, Hoja2!C32:C50; Hoja1 encabezados. |
| B/C | El cálculo actual es 528−66=462 ; 462/528 = 87,50%, unidad matrícula. | T2 Hoja2!B32:D50; V16, 18_Foto_Intertrimestral!F12 y bloque B91:I97. |
| B | La caché de la tabla dinámica solo replica los 19 campos de Hoja1!A1:S529, 528 registros. No aporta nómina de renuncias. | T2,xl/pivotCache/pivotCacheDefinition1.xml. |
| B/E | El manifiesto fundador declara «snapshot; estado individual ausente en la fuente». No remite a una nómina individual adicional. | MANIFEST_RETENCION_FOTO_INTERTRIMESTRAL_20261022.json. |

Los identificadores se usaron únicamente en memoria. No se exportaron nombres,
RUT, CODCLI ni listados individuales. Las rutas completas y SHA-256 de las fuentes
están en `EVIDENCIA_AGREGADA.json → fuentes`.

## Contraste exacto por CODCLI, validando RUT

**B/C:** cada fila localizada tiene un único CODCLI y RUT concordante. No se hicieron
uniones aproximadas ni muchos-a-muchos. Los estados pertenecen a cada respaldo;
no se trasladan a la fecha del cierre T2.

| Respaldo / Hoja1 | VIGENTE | ELIMINADO | SUSPENDIDO | Sin el mismo CODCLI | Total control |
|---|---:|---:|---:|---:|---:|
| DATOSDEALUMNOS_10246 | 520 | 7 | 0 | 1 | 528 |
| DATOSDEALUMNOS_11998 | 463 | 63 | 0 | 2 | 528 |
| DATOSDEALUMNOS_12159 | 462 | 63 | 1 | 2 | 528 |

- **B:** 10246 fue usado el 21-jul-2026 y congelado el 22-jul, según manifiestos.
  **E:** esas fechas no acreditan fecha efectiva de extracción ni estado exacto
  al 13-jul. Referencia: `FUENTES_CONGELADAS_2026_P2.json` y respaldo
  `0_caracterizacion/2026-07-21/2026_P2_161905/04_AUDITORIA/manifest_ejecucion.json`.
- **B:** en 11998 y 12159, los 63 ELIMINADO se descomponen en 56
  `11 - RENUNCIA POST INICIO CLASES`, 3 `23 - RETIRO - RETRACTO` y 4
  `24 - CAMBIO DE CARRERA`. No son 66 renuncias identificadas.
- **B:** en 12159, las dos matrículas sin CODCLI exacto sí tienen RUT localizado
  en otro CODCLI: una en otra carrera y otra en la misma. **E:** no se adjudica a
  esos otros expedientes la condición de renuncia del expediente original.
- **B:** la persona con dos matrículas está VIGENTE en ambas en los tres respaldos.
  **E:** no basta para establecer su pertenencia a las 66 del resumen original.
- **B/C:** 12159 suma 462 VIGENTE, pero sus 66 restantes incluyen 63 ELIMINADO,
  una SUSPENDIDO y dos sin CODCLI exacto. Ese complemento difiere del resumen
  original en 14 de 19 carreras. La coincidencia global no prueba identidad del conjunto.

### Diferencias por carrera: T2 vs. complemento de VIGENTE en 12159

**B/C:** el complemento incluye estados distintos de VIGENTE y CODCLI no localizado;
se muestra solo para auditar el empate de totales. **No se denomina renuncias.**
Las celdas vacías de renuncias se conservan como vacías en la evidencia; para esta
resta se reproducen con valor aritmético 0, como en la fórmula original.

| Carrera | Renuncias T2 | Complemento 12159 | Diferencia |
|---|---:|---:|---:|
| Administración Pública | 2 | 1 | -1 |
| Auditoría | 2 | 1 | -1 |
| Contabilidad General | 2 | 2 | 0 |
| Continuidad Ingeniería Informática | 0* | 0 | 0 |
| Ingeniería en Administración de Empresas | 6 | 4 | -2 |
| Técnico en Administración de Empresas | 4 | 3 | -1 |
| Ingeniería en Ciberseguridad | 0* | 0 | 0 |
| Técnico en Ciberseguridad | 3 | 3 | 0 |
| Ingeniería en Informática | 2 | 4 | +2 |
| Técnico en Programación y Análisis de Sistemas | 0* | 3 | +3 |
| Ingeniería en Logística | 6 | 6 | 0 |
| Técnico en Logística | 3 | 2 | -1 |
| Ingeniería en Marketing Digital | 2 | 0 | -2 |
| Técnico en Marketing Digital | 5 | 4 | -1 |
| Ingeniería en Recursos Humanos | 0* | 1 | +1 |
| Técnico en Recursos Humanos | 0* | 5 | +5 |
| Ingeniería Industrial | 0* | 1 | +1 |
| Técnico en Enfermería | 11 | 12 | +1 |
| Técnico en Enfermería e Instrumentación Quirúrgica | 18 | 14 | -4 |
| **Total** | **66** | **66** | **0** |

\* Celda vacía en el original. Etiquetas con tildes únicamente para presentación;
los textos originales están en la evidencia y no se modificaron las fuentes.

## Escenario separado: personas

**C/E — Supuestos explícitos:** las 66 bajas del resumen son 66 matrículas distintas
pertenecientes a las 528, sin repeticiones ni otros períodos; una persona permanece
si conserva al menos una de sus matrículas. Es la interpretación del resumen actual,
no una nómina individual ya acreditada.

| Clasificación | Condición sobre la única persona duplicada | Personas restantes | Base del escenario | Tasa |
|---|---|---:|---:|---:|
| C/E | Ninguna de sus dos matrículas está entre las 66 | 461 | 527 | 87,4762808% |
| C/E | Una o ambas matrículas están entre las 66 | 462 | 527 | 87,6660342% |

**C:** 462 matrículas pueden representar 461 o 462 personas. Son dos resultados
posibles, no cualquier valor del intervalo. La diferencia es 0,1897533 puntos
porcentuales. El 527 se usa solo como unidad personas del escenario; no sustituye
el 528 ni otro denominador aprobado en el libro.

**E — Pendiente preciso:** vincular `Hoja2!C32:C50` con la lista de CODCLI/RUT que
originó esas 66 renuncias, con su período y criterio. Para elegir entre las dos tasas
también debe acreditarse si alguna de las dos matrículas duplicadas pertenece a esa
lista. Los respaldos consultados no permiten cerrar esa atribución.

## Cobertura de búsqueda y preservación

- **B:** se revisaron todas las hojas T2 y T3 congeladas, incluyendo Hoja2 oculta
  del T3. La hoja oculta no tiene significado documentado, fecha ni estado; no se
  interpretó como lista de renuncias. Base y 2026_3 del T3 contienen ingreso P3, no
  el universo completo de ingresos P2.
- **B:** el inventario histórico de Caracterización registra 62 archivos / 63 hojas,
  sin nombres de renuncias/retractos. El inventario de respaldos MU2025 sí lista
  hojas Retractos_ de abril 2025; no corresponden al cierre 2026/P2.
- **C/E:** la búsqueda por nombres en ambos repositorios y OneDrive, incluyendo
  ocultos/ignorados, no localizó una nómina adicional con esos términos. Esto no
  demuestra ausencia universal de un listado que pudiera tener otro nombre.
- **B/C:** hashes de todas las entradas y ambas copias V16 iguales antes/después;
  las uniones y sumas cierran. `QA.json` conserva el límite de la tasa pendiente.
- **B:** rama `feature/ire-2026`; HEAD antes/después
  `80ca13a5a249a1a2bd53a699f5f73689b1f53040`. No se creó una V17 ni se editó V16.
  Los cambios pendientes anteriores se conservaron. Sin commit/push.

Reproducción: script `scripts/revisar_renuncias_t2_2026_personas_20261023.py`, bajo
la especificación `docs/ESPECIFICACION_RENUNCIAS_T2_2026_PERSONAS_20261023.md`.
Para repetir, elegir una carpeta nueva de salida: el script impide sobrescribir
este resultado. Siguiente acción útil: localizar el respaldo individual del agregado 66;
no repetir búsquedas generales ni sustituirlo por estados actuales.
