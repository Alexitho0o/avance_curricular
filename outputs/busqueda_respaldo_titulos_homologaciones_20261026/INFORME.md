# Búsqueda adicional de titulación y homologaciones · 26-10-2026

## Cuatro títulos

**[B/C]** Se leyó `Informe de Titulados 2025_vf.xlsx`, hoja `Hoja1`, informe institucional de Docencia con SHA-256 `676e6451eed59dae08d4cbcf99188932e0a2b586f9c3eb46f4b597721743f236`. Por tipo de documento R, número y DV se localizaron las cuatro personas. En sus cuatro registros `COD_SIES_OBT_TIT` está vacío y el archivo no contiene columnas CODCLI ni PLAN_DE_ESTUDIO. La fuente no identifica el plan formal ni prueba aceptación en SIES **[E]**. La copia enriquecida de Titulación Unificada revisada anteriormente sí posee códigos y una traza calculada, pero esa traza no convierte el informe de Docencia en un vínculo declarado de plan.

**[C]** Se revisaron cinco derivados privados previamente generados para cambios de plan (`CRONOLOGIA_PLANES`, `REVISION_16_CASOS_FINAL`, `FILAS_ADICIONALES_PRIVADAS`, `FILAS_RECUPERADAS_CODCLI` y `FOCO_PRIVADO`): no se localizaron los CODCLI de estos cuatro casos en esos archivos. La revisión es una búsqueda literal en esos cinco archivos, no una prueba de ausencia en todo el historial.

**[E]** Los cuatro casos continúan pendientes de una declaración título–CODCLI–plan o evento de migración documentado. La actividad de 2024 en los planes posteriores, detectada antes, permanece como respaldo contextual; no se reemplaza la traza anterior ni se determina un plan final.

## 21 ramos

**[B/C]** En el catálogo `estructura_asignaturas.json` se buscó cada uno de los 21 códigos en ambos extremos de todas las relaciones explícitas `RamoEquiv`, sin limitar la búsqueda al plan original. Para **19 códigos** hay referencias en otros planes. Para `AS31TPAREOL` en `IECIREOL20211` y `AS21TTMRE` en `TTMRE20211` no se encontró una referencia en ese conjunto de relaciones.

**[E]** Esas 19 referencias son evidencia de relaciones declaradas para otros contextos; no prueban homologación en el plan pendiente ni autorización por estudiante. No se aplicó transitividad automática, no se fusionaron códigos y no se cerraron los 21. Los reportes de actividad de 2024 ya identificaron los códigos de tres de estos ramos, también en otros planes; tampoco acreditan homologación individual.

La lista completa de relaciones, planes de origen/destino y filas de la fuente se conserva en `RESULTADO_AGREGADO.json`, sin identificadores de estudiante.

## Control

- `analizar.py` reproduce el contraste y comprueba el SHA-256 del informe docente. `RESULTADO_AGREGADO.json` registra fuentes y hashes.
- Sin cambios en bases, diccionario activo, denominadores, tasas ni archivos originales. Sin commit ni push.
