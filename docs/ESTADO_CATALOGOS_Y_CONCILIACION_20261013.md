# Estado verificado al 13-10-2026

Estado inicial conservado. La [revision posterior del reporte 6047](REVISION_EQUIVALENCIAS_6047_20261013.md)
completo 17 de las 52 equivalencias iniciales y habilito el analisis interno de
Caracterizacion 2027. Sus resultados sustituyen la cobertura y pendientes de
equivalencias de este documento, no la conciliacion de matricula 2026.

## Oferta y modalidad

| Control | 2026 | 2027 |
|---|---:|---:|
| Codigos unicos de oferta | 137 | 140 |
| Codigos con alguna equivalencia CODCARPR | 103 | 88 |
| Codigos sin equivalencia CODCARPR | 34 | 52 |

Los codigos representan combinaciones de sede, carrera, jornada y version, no
140 carreras distintas ni 52 estudiantes sin modalidad. La fuente 2027 tiene
modalidad explicita para sus 140 codigos: presencial 60, semipresencial 18 y
no presencial 62. Por sede: Santiago 123, Concepcion 13, Patagonia 4.

Los 52 pendientes se separan en **37 codigos nuevos de 2027** y **15 codigos
que ya estaban en 2026 sin equivalencia interna**. Hay 103 codigos comunes entre
ofertas, pero solo 88 tienen equivalencias heredables. Los 34 codigos presentes
en 2026 y ausentes de 2027 se conservan en el historico.

Evidencia por codigo, nombre, sede, jornada, version y origen de la brecha:
[CONCILIACION_OFERTA_2026_2027.json](../data/catalogos_sies/CONCILIACION_OFERTA_2026_2027.json).

La oferta adjunta de enlaces contiene 14 codigos, no el universo de 140. El
catalogo usa el reporte validado 5910 del 07-09-2026; no se presenta como
reporte final 5909 ni como certificacion de etapa 3.

## Matricula 2026

Recuento directo de fuentes, sin correr ni modificar el pipeline:

| Universo | Consolidado institucional comparable | Publicacion SIES aportada | Diferencia |
|---|---:|---:|---:|
| Pregrado | 3145 | 3371 | 226 |
| Postitulo | 54 | 54 | 0 |
| Total comparado | 3199 | 3425 | 226 |

Pregrado: 4105 registros historicos = 960 VIG=0 + 3145 VIG=1 + 0 VIG=2.
Los 3145 registros comparables corresponden a 3111 personas distintas.
La diferencia de 226 matriculas **no equivale a una lista demostrada de 226
personas faltantes**. No se prueba la causa ni la cadena completa de cargas
aceptadas. La celda de posgrado vacia se conserva como null, no como cero observado.

Fuente publicada: hoja `Listado de instituciones 2026`, IPSS 162, `B67:F67`.
Las fuentes y sus SHA-256, distribuciones y reglas estan en
[CONCILIACION_MATRICULA_2026.json](../data/catalogos_sies/auditorias/20261013/CONCILIACION_MATRICULA_2026.json).
El glosario adjunto corresponde a 2025; no se adopta como manual 2026.

## Protecciones y limites

- 31 pruebas focalizadas aprobadas con `python3 -m unittest discover -s tests -v`:
  aislamiento anual, sedes, jornadas 3/4, versiones ambiguas, fuentes alteradas,
  inmutabilidad, regeneracion repetible, esquemas y conteos de matricula/personas.
  `git diff --check` sin observaciones. No sustituye una prueba del consumidor real.
- Cinco referencias MU2026 verificadas por SHA-256 antes y despues: catalogo
  DURACION, puente compilado, motor, comando oficial y reglas de sede.
- No se ejecutaron matricula completa, cargas PES ni Caracterizacion.
- No se cambiaron fuentes, entregas congeladas ni registros de estudiantes.
- No se modifico el proyecto CARACTERIZACION ni se activo el nuevo resolutor alli.
- Catalogos y auditoria son locales, preparados para revision Git; esta tarea
  no realizo commit ni push. Los originales ignorados por Git siguen siendo
  dependencias locales de regeneracion, no respaldos demostrados en GitHub.
- Los 88 codigos con equivalencia no garantizan que todo CODCARPR se resuelva:
  una consulta ambigua queda sin modalidad hasta desambiguar con evidencia.

## Lo que falta

1. Completar en `data/catalogos_sies/equivalencias_2027.json` las 52 equivalencias
   que efectivamente correspondan, con codigo interno, nombre, sede/jornada/version
   contenidos en el codigo SIES y evidencia verificable. No asignar por semejanza.
2. Publicar una revision del catalogo sin reemplazar los snapshots existentes.
3. Integrar el resolutor anual en el consumidor solicitado y comprobar cobertura
   sobre su universo real. No usar el campo MODALIDAD escolar de DatosAlumnos.
4. Conciliar los 226 registros de diferencia con la cadena de cargas aceptadas,
   sin sumar cargas parciales ni alterar historicos para forzar igualdad.
