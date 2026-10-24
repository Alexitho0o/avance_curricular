# Resultado: versión por cohorte y duración

**Actualización del 2026-10-16:** para continuidad, ANOINGRESO puede conservar el
año del técnico. Las propuestas siguientes son el ensayo anterior a esa regla;
no consumirlas como asignaciones actuales de continuidad. Usar
`common.continuidad_trayectoria.resolver_version_trayectoria`, que requiere fecha
propia de la carrera y registra si está confirmada o solo observada. Véase
[regla y resultados](continuidad_trayectoria_20261016.md).

Fecha: 2026-10-16. Se aplica la corrección del usuario: conservar el cruce de
carreras y completar la versión, sin exigir coincidencia entre nombres internos
y formales. Las diferencias nominales de fase B no bloquean este procedimiento.

## Base conservada y regla aplicada

Se preservaron las 257 equivalencias de programa H5, reunidas en sus 132 claves
CODCARPR/sede/jornada existentes. No se borró ni se volvió a construir el puente.
Los nombres se conservan como atributos, no como filtros. La búsqueda consulta
las versiones históricas de la misma familia I/S/C/J, incluidas las ausentes en
el catálogo actual; no añade familias por semejanza nominal.

La duración total y el tipo de plan se recuperan de la gobernanza anterior:
7 grupos con equivalencia manual explícita FCU2026, 49 con CODCARPR_CANONICO y
59 con perfil unánime en sus candidatos. En 17 grupos no queda un perfil unívoco.
Las equivalencias manuales se usan para conservar el perfil del programa, no
para imponer retrospectivamente su versión 2026 a todos los años.

Ejemplos de perfiles recuperados: ILOG = regular, 8 semestres totales;
CILOG = continuidad, 4; NATP = regular, 8, mediante la equivalencia manual
existente con I162S2C90J2V2. El valor de duración procede del catálogo SIES
gobernado del puente, no de una columna de duración en DatosAlumnos, que no existe
en ese extracto. No se convirtió NIVEL ni se inventó una fórmula trimestral.

La búsqueda utiliza **ANOINGRESO**, conservando PERIODOINGRESO. ANOMATRICULA solo
describe la observación. Las 1.825 combinaciones provienen de la proyección
académica de DATOSDEALUMNOS_11998 ya conservada y trazada; no son 1.825 personas.
Se mantienen todas, incluidas las ajenas al período 2007–2026. La fuente original
y su hash figuran en resumen.json; no se requiere el archivo de Descargas para
reproducir esta consulta de combinaciones.

Orden fijo de la regla:

1. Recuperar el grupo existente por CODCARPR, sede y jornada.
2. Conservar versiones del perfil de duración total y tipo de plan gobernado.
3. Calcular primera oferta por Código Único completo.
4. Comparar esa fecha con ANOINGRESO. Si hay un único código cuyo inicio coincide,
   informar COINCIDENCIA_INICIO.
5. Para cohortes posteriores, evaluar separadamente INTERVALO_PROPUESTO: último
   inicio de oferta no posterior a la cohorte, dentro del mismo perfil. Esta es
   una hipótesis explícita de sucesión, no prueba del cierre de la versión previa.
6. Empates, perfiles múltiples, ingreso anterior a oferta y grupos ausentes
   permanecen identificados; no elegir número V máximo ni cambiar de programa.

## Cobertura del ensayo

| Resultado por combinación académica | Cantidad |
|---|---:|
| Coincidencia exacta de año inicial de oferta con ANOINGRESO | 240 |
| Propuesta por intervalo de inicio dentro del mismo perfil | 969 |
| Perfil de duración no determinado en el grupo previo | 287 |
| Sin agrupación existente para CODCARPR/sede/jornada | 146 |
| Fuera de 2007–2026 | 102 |
| Cohorte anterior al inicio de cobertura de oferta | 46 |
| Cohorte anterior a primera oferta del perfil | 21 |
| Más de un perfil de duración posible | 14 |
| **Total conservado** | **1.825** |

Las 1.209 propuestas tienen oferta observada para su propio año de ingreso.
En 1.154 hay también MRUN del código en ese año; en 55 no. La ausencia de MRUN
no elimina una oferta ni valida/invalida por sí sola la propuesta UMAS. En 407
propuestas el código aparece desde el límite de cobertura 2010: se conserva esa
advertencia, sin afirmar que no existiera oferta anterior.

Las propuestas no acreditan la malla CODPESTUD individual ni una migración.
Tampoco actualizan los archivos oficiales. El campo codigo_propuesto y el estado
explican qué produjo la regla; no se presentan como equivalencias documentales
nuevas ni como validación independiente de las agrupaciones heredadas.

## Ejemplos reales y excepción temporal

| Entrada | Resultado |
|---|---|
| ILOG / RE / O / ANOINGRESO 2024 | I162S2C77J4V1, regular, 8 semestres; coincidencia con primera oferta 2024. |
| ILOG / RE / O / ANOINGRESO 2025 | V1 bajo la hipótesis de intervalo. No toma V2 por ser posterior: V2 corresponde a continuidad de 4 semestres. |
| CILOG / RE / O / ANOINGRESO 2025 | I162S2C77J4V2, continuidad, 4 semestres; coincidencia con primera oferta 2025, aunque ANOMATRICULA sea 2026. |
| NATP / RE / V / ANOINGRESO 2026 | I162S2C90J2V2, regular, 8 semestres; coincidencia con primera oferta 2026. No toma V1 de continuidad por el año del identificador del plan. |
| CILOG / RE / O / ANOINGRESO 2024 | Sin propuesta temporal: el perfil de continuidad inicia en oferta en 2025. No se reasigna al programa regular para conseguir coincidencia. |
| NATP / RE / V / ANOINGRESO 2025 | Sin propuesta temporal: el perfil regular aparece en oferta en 2026. Se conserva la diferencia entre fuentes. |

Las dos últimas entradas sí están en las combinaciones de DatosAlumnos. Su causa
no está determinada: no se afirma que sean errores, traslados o datos migrados.
La hipótesis es útil para ordenar propuestas, pero no explica por sí sola esas
excepciones. Las 21 combinaciones con cohorte anterior quedan localizadas por
fila del archivo original, sin exportar identidades.

## Uso, trazabilidad y validación

Consulta desde el repositorio:

```sh
python3 scripts/versiones_por_cohorte.py --codcarpr CILOG --sede RE --jornada O --anoingreso 2025
python3 scripts/versiones_por_cohorte.py --verificar
```

Pasaron 13 pruebas focalizadas: nombres independientes, duración regular y
continuidad, ANOINGRESO distinto de matrícula, empates, cronología frente a V,
unidades, cobertura histórica y preservación íntegra de las equivalencias y
combinaciones. La reconstrucción reprodujo los mismos bytes. No se modificó el
Excel, H5, los catálogos congelados ni los motores operativos.

- [Especificación previa](versiones_por_cohorte_20261016.md).
- [Grupos heredados y evidencia de duración](../data/versiones_por_cohorte/20261016/grupos_existentes.json).
- [Resultados por combinación académica](../data/versiones_por_cohorte/20261016/resultados_cohortes.json).
- [Cobertura de los 141 códigos](../data/versiones_por_cohorte/20261016/cobertura_codigos.json).
- [Resumen y fuente DatosAlumnos](../data/versiones_por_cohorte/20261016/resumen.json).
- [Manifiesto de integridad](../data/versiones_por_cohorte/20261016/manifest.json).

El recurso está registrado en PROYECTO_IPSS.json como versiones_por_cohorte.
La regla puede consultarse de forma idéntica desde ambos procesos, sin rehacer
agrupaciones en cada búsqueda. Quedan por resolver los perfiles no unívocos y
las excepciones de cohorte; la hipótesis de intervalo permanece explícitamente
separada de las coincidencias de inicio.
