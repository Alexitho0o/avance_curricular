# Recuperación íntegra de la oferta 6047

## Corrección y alcance

El 16 de octubre de 2026 se indicó que la descarga 6047 era idéntica a la del
13 de octubre «ya incorporada». La igualdad de SHA-256 era correcta, pero esa
frase confundió incorporación de catálogo y evidencia parcial con respaldo
íntegro del archivo. El usuario eliminó la descarga basándose en esa información.
El error fue de verificación y comunicación del asistente.

Esta intervención recupera el CSV completo desde la Papelera, conserva sus bytes
mediante compresión gzip reversible dentro del proyecto y registra procedencia,
columnas y controles. No sustituye la fuente por una reconstrucción de las
14 columnas utilizadas por el resumen ejecutivo.

## Procedimiento y criterios de aceptación

1. Leer el CSV de la Papelera sin mover ni eliminar el original.
2. Comprobar la huella registrada para ambas descargas:
   `4edfefaabf449b35163fa090ecac39649ecaf6aab10bbe3a4ef7e83a244f8e62`.
3. Comprobar también el miembro CSV del ZIP recuperable.
4. Guardar todos los bytes en
   `data/recuperacion_oferta_6047/20261016/reporte_dinamico_6047_20261016.csv.gz`.
5. Verificar descompresión idéntica, 47.617 bytes, 161 registros, 51 columnas
   y coincidencia de las 14 columnas ya utilizadas en el resumen ejecutivo.
6. Registrar los resultados en `recuperacion.json` del mismo directorio.

Los manifiestos de entregas anteriores conservan el estado de respaldo observado
al emitirse. Esta adenda documenta su resolución posterior; no se reescriben
manifiestos congelados ni se modifican cifras, catálogos o códigos confirmados.

La copia queda dentro del árbol local del proyecto, apta para seguimiento Git.
Esto no equivale a un commit ni a un respaldo publicado en GitHub.

## Evidencia

- [CSV íntegro comprimido](../data/recuperacion_oferta_6047/20261016/reporte_dinamico_6047_20261016.csv.gz).
- [Registro de recuperación y validación](../data/recuperacion_oferta_6047/20261016/recuperacion.json).
- [Entrega ejecutiva previa](resumen_ejecutivo_oferta_2027_20261016.md).
