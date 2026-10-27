# Titulación: búsqueda de documentos y alcance temporal · 26-10-2026

**[C] Contexto:** Titulación Unificada 2026, título observado en 2025, caso TTMRE/TCRE con varios expedientes. Revisión de lectura sin alterar bases, diccionario, tasas o denominadores.

## Resultado nuevo

**[B/C]** Se inspeccionaron 116 archivos candidatos: 84 PDF, 28 DOCX y cuatro XLSX. Se leyeron 100 contenidos distintos y se identificaron 16 duplicados exactos por SHA-256. No se encontraron coincidencias del caso en el texto o valores examinados mediante CODCLI exacto, documento con DV o cuerpo de documento. Los 100 archivos leídos conservaron su hash. Estos resultados no suman personas ni acreditan una búsqueda exhaustiva de toda la documentación institucional.

**[E] Límite:** 22 archivos tienen alguna página o componente sin texto extraíble; en DOCX puede tratarse de encabezados o pies vacíos. No se ejecutó OCR general. Un certificado escaneado se revisó visualmente y corresponde a otra institución, no al registro IPSS buscado. El método no descarta información en imágenes, formatos no incluidos, archivos externos o representaciones no reconocidas de los identificadores.

## Comparación de respaldos de titulados

| Fuente y hoja [B] | Filas no vacías, excluida cabecera [C] | Mayor valor de FECHA [B] | Coincidencias documento + DV del caso [C] | CODCLI / plan en cabecera [B] |
|---|---:|---|---:|---|
| TITULADOS_3280.xlsx · Hoja1 | 3.348 | 2025-05-29 | 0 | No / No |
| TITULADOS_3280 (1).xlsx · Hoja1 | 3.348 | 2025-05-29 | 0 | No / No |
| TITULADOS_3280 1.xlsx · BBDD | 3.348 | 2025-05-29 | 0 | No / No |

**[B]** En `Informe de Titulados 2025_vf.xlsx`, Hoja1, fila 107, la coincidencia exacta por `NUM_DOCUMENTO` y `DV` registra `FECHA_OBT_TIT_GRA=2025-07-24`. SHA-256: `676e6451eed59dae08d4cbcf99188932e0a2b586f9c3eb46f4b597721743f236`.

**[C/E]** La fecha del título del caso es posterior al mayor valor de FECHA observado en los tres respaldos. Por ello esas copias no aportan el registro posterior necesario. El máximo observado no es fecha de exportación ni demuestra la causa exacta de la ausencia. Los tres libros tienen diferencias de estructura/valores; no se trataron como duplicados exactos. La copia `(1)` contiene un error cacheado `#REF!` en el campo FECHA, que se conserva y no afecta al máximo calculado sobre fechas válidas.

**[B/C]** El catálogo institucional de reportes V001 describe `TITULADOS / View_titulados`, plataforma UMASNET, origen documentado `MT_ALUMNO`. Es una referencia de localización, no prueba de acceso al sistema ni de vínculo individual. Los tres respaldos examinados no ofrecen las columnas CODCLI y plan requeridas. No se declara que una nueva exportación del mismo reporte las vaya a incluir automáticamente.

## Evidencia que sigue faltando

**[E]** El acto o registro de otorgamiento correspondiente al título de julio de 2025, vinculado al CODCLI y al plan; alternativamente, documentos que encadenen ese acto con el expediente y su plan de forma verificable. Las evidencias anteriores de actividad y estado apoyan el expediente posterior, pero no sustituyen esa atribución formal. No se recuperó una nueva regla del puntaje 2130.

**[C] Reanudación:** priorizar el respaldo institucional que sustentó la fila de Docencia y registros de titulación que incluyan julio de 2025. No repetir las tres copias 3280 como si acreditaran un nuevo período. Si un respaldo carece de CODCLI o plan, buscar su vínculo documental; no asignarlo por primera coincidencia de RUT.

## Trazabilidad

**[C]** `revisar.py` reproduce el barrido y guarda inventario en `~/.local/share/ipss/busqueda_documentos_titulo_20261026/INVENTARIO.json` con permisos restringidos. `RESULTADO_AGREGADO.json` registra alcance y límites. `comparar_reportes.py` reproduce el contraste por campos exactos y verifica hashes antes/después; `COMPARACION_REPORTES.json` contiene los hashes y resultados sin identificadores individuales. Los scripts se ejecutaron con el Python suministrado por Codex. No hubo recálculo ni modificación de Excel.

**[C]** Sin commit ni push. Se conservaron los cambios previos del repositorio.
