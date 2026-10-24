# Instrumentos LimeSurvey por ano y periodo

Este archivo neutral conserva cuestionarios originales. No reemplaza la carga PES,
no contiene respuestas de estudiantes y no modifica el cierre FCU 2026.

## Versiones registradas

| Ano | Periodo | Encuesta | Estado | Preguntas |
| --- | --- | --- | --- | --- |
| 2026 | 1 | Sin fuentes recibidas | PENDIENTE_FUENTES | No determinadas |
| 2026 | 2 | 443299 | INVENTARIO_ARCHIVADO | 103 |
| 2027 | 1 | 141234 | INVENTARIO_ARCHIVADO | 91 |

Registro operativo: [REGISTRO.json](REGISTRO.json). Las carpetas de version contienen
`fuentes/`, `inventory.json`, `excel/`, `versiones_codigo/`, `previews/` y
`manifest.json`. Cada fichero del paquete tiene SHA-256; las rutas son relativas
para recuperar el contenido en Mac o Windows sin depender de Descargas/Escritorio.

## Reproduccion

Usar `scripts/exportar_instrumento_limesurvey.py --anio <ano> --periodo <periodo>
--entrada <carpeta_fuentes> --salida <nuevo_excel> --registrar` desde el repositorio.
Las dependencias de construccion son Python estandar y Artifact Tool en Node;
configurar LIMESURVEY_NODE y LIMESURVEY_NODE_MODULES si el runtime tiene otra ruta.
La salida --solo-json no necesita Node. Comandos y detalles en
[la guia de inventarios](../../docs/gobernanza/INVENTARIO_INSTRUMENTO_LIMESURVEY.md).

Los Excel tienen Preguntas y Detalle, en el orden del instrumento, sin colores.
No se inventan respuestas en campos abiertos. Origen del elemento identifica
XML o tipo nativo de LimeSurvey, no una clasificacion FCU/institucional.

## Comparaciones futuras

Identificar cada elemento por ano, periodo, encuesta, grupo, pregunta y opcion o
subpregunta. Un mismo codigo entre anos no demuestra igual significado. Conservar
los enunciados, opciones, tipos y orden originales. Los futuros cruces y reglas
de equivalencia deben guardarse por separado y nunca modificar estos snapshots.
No inferir FCU/institucional por presencia o ausencia en una version del instrumento.
2026 P1 debe incorporarse a partir de sus propios LSG/LSS cuando el usuario los aporte.

No confundir archivos de cuestionario con resultados de la encuesta. Revisar datos
personales/secretos antes de publicar futuras exportaciones. Registro local no
equivale a commit ni a publicacion en GitHub: comprobar los tres estados.
