# Reintento de 12 fuentes de SIES · 26-10-2026

**[C] Alcance:** se reintentaron los 12 archivos pendientes del barrido por CODCLI, RUT con DV y cuerpo de RUT, con hasta 90 segundos por lectura. En los candidatos se verificaron las coincidencias por filas, con hash antes y después; los identificadores se procesaron solo en memoria. No se modificaron fuentes, bases o denominadores.

| Resultado [C] | Archivos |
|---|---:|
| Leídos | 8 |
| Cabecera inspeccionada: fuente SIES con MRUN sin RUT ni CODCLI | 1 |
| No interpretables como Excel en el reintento | 3 |
| Total | 12 |

**[B/C]** Cuatro de los ocho libros leídos tienen al menos una fila con CODCLI y RUT con DV del caso. Entre ellos hay dos libros de Avance Curricular que contienen la misma clase de respaldo PROMEDIOS, y un libro de trayectorias que contiene eventos calculados. No se suman archivos como personas ni como pruebas independientes.

## Hallazgo de trayectoria

**[B/C]** En `PREGRADO_TRAYECTORIA_CARACTERIZACION_2026_P1_20260512.xlsx`, hoja `CAMBIOS_ACADEMICOS`, SHA-256 `1911c23e5459d578a1b8c12d178d6142ff48a4060984bde181902ab59ba391ca`, los CODCLI y RUT con DV del caso conducen a dos registros: el expediente anterior muestra situación 10, `ELIMINADO` y etiqueta `CAMBIO_PLAN`; el posterior muestra situación 31, `TITULADO` y etiqueta `TITULACION`. En PROMEDIOS, el CODCLI posterior se encuentra asociado al plan `TCRE20241`. La coincidencia por CODCLI entre ambas fuentes está registrada en `outputs/vinculo_trayectoria_codcli_20261026/RESULTADO_AGREGADO.json`.

**[C/E]** El código vigente de `procesos/caracterizacion/caracterizacion.py`, SHA-256 `3e49e7f51973dcfd68db886a9b2f8ec4345b2eb5da0770976fe5d73b8d2ef187`, contiene un mapeo de situación 10/ELIMINADO a `CAMBIO_PLAN` y de 31/TITULADO a `TITULACION`. Es implementación técnica, no una norma SIES; no se comprobó que esta versión exacta generara el libro histórico. La hoja no declara el plan ni una fecha efectiva del evento. Por eso su etiqueta fortalece la evidencia interna del estado del expediente posterior, pero no es un acto de titulación que vincule formalmente título–CODCLI–plan. Los valores año y período no se presentan como fecha del evento.

## Archivos que siguen sin lectura individual

**[B/C/E]** El CSV de matrícula SIES 2023 tiene MRUN y no ofrece columnas RUT ni CODCLI en su cabecera; se inspeccionó solo la estructura. No se intentó reconstruir RUT–MRUN. Dos `reporte_filtrado.xlsx` se observaron con tamaño cero. `subirR.xlsx` volvió a fallar como Excel y una lectura posterior agotó el tiempo; esto no permite identificar la causa. Las rutas exactas se conservan en el resultado privado; no se reemplazaron archivos.

**[E]** La relación interna entre CODCLI posterior, actividad y plan quedó más respaldada; la atribución documental formal del título y la regla de desempate de 2130 siguen pendientes. El examen de cabeceras no descarta una estructura distinta fuera de las primeras 15 filas.

**[C] QA:** `revisar.py` registra conteos y conserva el inventario de fuentes y coincidencias bajo `~/.local/share/ipss/busqueda_tres_llaves_sies_20261026/` con permisos 0600. Las fuentes candidatas validadas por filas se verificaron por hash antes y después. `outputs/vinculo_trayectoria_codcli_20261026/revisar.py` reproduce el contraste del evento y conserva solo agregados. Sin cambios a fuentes, bases, diccionario, tasas ni denominadores; sin commit ni push.
