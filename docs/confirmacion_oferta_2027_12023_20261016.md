# Confirmación de fuentes y cobertura 2027 P1 — DatosAlumnos 12023

Especificación previa, 2026-10-16. Comprobar las fuentes indicadas en Descargas
y reutilizar el auditor y catálogo anual existentes, sin cambiar equivalencias,
versiones, filtros de elegibilidad ni las entregas D1–D4/MU2026.

El reporte `reporte_dinamico_6047_2026-10-16_10:54:00.csv` tiene SHA-256
`4edfefaabf449b35163fa090ecac39649ecaf6aab10bbe3a4ef7e83a244f8e62`, idéntico al
6047 del 13 de octubre registrado en EVIDENCIA_DIMENSIONES. No se crea otra
copia ni una revisión operativa por cambiar el nombre de descarga.

`DATOSDEALUMNOS_12023.xlsx`, Hoja1, tiene SHA-256
`331f73f352a3df5075126feaadc66566b09d77cb3527220bd185d1c432eb73a4`, idéntico al
extracto gobernado en B4/B5 y usado hasta D4. La auditoría anual anterior usó
11941: no confundir la fuente histórica 12023 con ese corte anterior.

El diagnóstico aplica exactamente ANOMATRICULA=2027 y PERIODOMATRICULA=1,
sin filtros adicionales de estado, firma o primer ingreso. Los resultados son
registros del extracto, no personas únicas ni matrícula institucional oficial.
Se leen seis dimensiones académicas y se guardan solo agregados, estados y
candidatos del resolutor vigente. La modalidad de carrera procede de oferta,
no de MODALIDAD escolar de DatosAlumnos. No se selecciona versión por año de
matrícula, ingreso ni máximo ordinal V.

Comando reutilizado desde el repositorio contenedor:

```sh
python3 procesos/caracterizacion/scripts/gobernanza/auditar_catalogo_sies_2027.py \
  --alumnos /Users/alexi/Downloads/DATOSDEALUMNOS_12023.xlsx \
  --periodo 1 \
  --salida data/catalogos_sies/auditorias/20261016_12023_p1/cobertura.json
```

El resultado se compara con la auditoría 11941 de modalidad_v2. Los casos sin
equivalencia y ambiguos se conservan; no se promueven candidatos nominales.

## Resultado ejecutado

Ambas fuentes tienen antecedentes gobernados. El CSV de Descargas es idéntico
en todos sus bytes al reporte 6047 del 13 de octubre, no solo en los atributos
del cruce. Tiene 161 filas y 51 columnas: las 140 combinaciones del catálogo
anual y 21 diplomados adicionales fuera del universo operativo actual. No hay
nueva oferta por el hecho de descargar el mismo contenido con otra fecha.
El año 2027 procede de la edición gobernada corroborada y de la identificación
del usuario: no de un campo año en el CSV, que no lo contiene.

El catálogo activo sigue siendo `5910_20260907_6047_20261013_modalidad_v2`.
Se reutilizó el auditor del módulo integrado de Caracterización, que consume
el recurso común del repositorio contenedor. No se cambiaron códigos ni reglas.

| Estado del Código Único | 11941, auditoría anterior | 12023, filtro actual |
|---|---:|---:|
| Resuelto | 88 | 114 |
| Ambiguo | 131 | 159 |
| Sin equivalencia | 52 | 73 |
| Total de registros | 271 | 346 |

La diferencia es de 75 registros entre filtros de extractos distintos; no se
interpreta como 75 estudiantes nuevos ni como 75 matrículas elegibles. Se conserva
el filtro solicitado sin añadir ESTADOACADEMICO, CON_FIRMA o ANOINGRESO.

La modalidad de carrera se determina en 273 registros: 65 Presencial y 208
No presencial. Los 159 códigos ambiguos tienen modalidad unánime entre sus
candidatos respaldados; esto no elige una versión. Los otros 73 registros,
agrupados en 18 CODCARPR/sede/jornada, mantienen modalidad no determinada.

Ejemplos ya resueltos en el filtro actual:

| CODCARPR | Sede | Jornada | Código Único | Registros |
|---|---|---|---|---:|
| IIART | RE | O | I162S2C134J4V1 | 7 |
| TIART | RE | O | I162S2C140J4V1 | 4 |
| IOPMI | RE | O | I162S2C135J4V1 | 3 |
| TOPMI | RE | O | I162S2C142J4V1 | 6 |
| PMTEIQ | PTG | V | I162S4C114J2V1 | 4 |

## Dos correspondencias exactas nuevas por incorporar

Se aplicó a los pendientes la misma comparación de nombre normalizado,
sede y jornada que gobierna la revisión 6047. No se eliminó SP ni se cambió
la jornada para producir una coincidencia.

| CODCARPR | Nombre interno literal | Sede/jornada | Candidato exacto único | Registros |
|---|---|---|---|---:|
| COTENS | TECNICO EN ENFERMERIA | CO / D | I162S3C91J1V1 | 1 |
| TCEX | TECNICO EN COMERCIO EXTERIOR | RE / O | I162S2C136J4V1 | 2 |

Estas dos correspondencias no están incorporadas en el catálogo activo. Su
incorporación requiere una nueva revisión con esta evidencia, preservación del
registro anterior y las verificaciones habituales de paridad e integridad.
De aplicarse únicamente estos dos enlaces a este mismo extracto, la cobertura
esperada sería 117 resueltos, 159 ambiguos y 70 sin equivalencia; es un escenario,
no el resultado activo ni una actualización realizada.

Los CODCARPR ADMP, CICDA, COIELECSP, COTCONSSP, COTENS, IMDI y TCEX no estaban
presentes en el filtro 2027 P1 del extracto anterior. Esto describe observación
en ese filtro, no fecha de creación de carreras. Los demás pendientes requieren
seguir las relaciones ya construidas y resolver sede/jornada/plan/versiones con
evidencia; no volver a agrupar todo por nombre.

Este cruce anual permite analizar las matrículas de 2027 P1 bajo el contrato
existente. No resuelve retroactivamente la vigencia de mallas del cierre D4:
año de matrícula y período no determinan por sí solos una versión histórica.

## Evidencia y controles

- [Cobertura completa por dimensión](../data/catalogos_sies/auditorias/20261016_12023_p1/cobertura.json).
- [Huellas, comparación y candidatos nuevos no promovidos](../data/catalogos_sies/auditorias/20261016_12023_p1/comparacion_fuentes.json).
- [Control de preservación](../data/catalogos_sies/auditorias/20261016_12023_p1/control.json).
- [Regla anual vigente](RESOLUCION_MODALIDAD_INDEPENDIENTE_2027.md).

La auditoría comprueba conservación de las columnas fuente y conciliación de
registros. Se verifican los hashes de las fuentes y el catálogo; los 51 archivos
FCU2026 y las referencias protegidas permanecen intactos. No se ejecutó el
pipeline productivo ni se modificaron los Excel del usuario o el diccionario D4.
La evidencia nueva es agregada; no publica identificadores personales.
