# Recuperación y continuación del diagnóstico MRUN–UMAS

## Especificación previa

El análisis original se localizó en CARACTERIZACIÓN/gobernanza/trazabilidad_mrun,
con fecha 2026-09-16. Sus cuatro archivos son idénticos a las copias importadas
bajo procesos/caracterizacion. No modificar ni reejecutar sus rutas absolutas:
usa otro corte UMAS y criterios que ya requieren revisión.

Continuación autorizada por el usuario: diagnóstico determinístico de candidatos,
con agregados por carrera y corte, sin certificar ni persistir relaciones RUT–MRUN.
No se aplica técnica probabilística. La tasa esperada de falsos enlaces no puede
estimarse sin pares de identidad validados; no se presenta unicidad como precisión.
El alcance mantiene la separación entre diagnóstico y asignación del manifiesto
histórico. La autorización actual permite avanzar con el diagnóstico solicitado.

Fuentes: UMAS DATOSDEALUMNOS_11998 de hash ya verificado; MRUN 2007–2026 de H2;
agrupaciones carrera/sede/jornada existentes. Manual ER MRUN 2007–2026 página 2:
GEN_ALU 1=Hombre, 2=Mujer; FEC_NAC_ALU AAAAMM, 190001 sin información. Los códigos
9995/9998/9999 y 1900 no se convierten en cohortes ordinarias. No usar día de
nacimiento inexistente ni inferir sexo desconocido. Edad por tramo no añade
independencia al nacimiento. El mapeo UMAS M/F conserva su significado interno.

Bloqueos: (A) mismo año observado + nacimiento AAAAMM + sexo; (B) añadir familia
ISCJ de las agrupaciones existentes, dejando V libre; (C) añadir tipo de programa
solo si el perfil existente es unánime. No se exige Código Único ni se filtra por
primera oferta, duración actual o vigencia para obtener el resultado que buscamos.
Los ingresos se contrastan después, no se toma el mínimo por persona. No elegir
carrera actual por el máximo ANOINGRESO. No usar nombres para rehacer equivalencias.

Unidad objetivo: fila/expediente UMAS con ANOMATRICULA entre 2007 y 2026. Su año
es corte observado, no ingreso efectivo. El extracto no reconstruye todas las
matrículas históricas de esa persona. Vacíos no se enlazan. Unicidad significa
un candidato MRUN dentro del corte y perfil, no identidad acreditada. Se calcula
además reciprocidad entre personas por año: varios CODCLI de un mismo RUT no
se convierten automáticamente en varias personas. Se informa ambigüedad de
código cuando un único MRUN tiene varios códigos compatibles en el mismo año.

RUT, MRUN, CODCLI y nacimiento solo permanecen en memoria. Las salidas no incluyen
identificadores, hashes personales ni fechas individuales. Estados UMAS son del
extracto, no del día histórico de carga SIES. Sin candidato no prueba exclusión
correcta, ni igualdad de totales acredita identidad. No se modifican congelados.

## Antecedente recuperado y qué se conserva

[Diagnóstico F0 original integrado](../procesos/caracterizacion/gobernanza/trazabilidad_mrun/F0_DIAGNOSTICO_FACTIBILIDAD.md)
y [script original](../procesos/caracterizacion/gobernanza/trazabilidad_mrun/scripts/f0_diagnostico_factibilidad.py).
La copia integrada y el original CARACTERIZACIÓN conservan los mismos cuatro
archivos, registrados por SHA-256 en antecedente_recuperado.json.

F0 describió 12.539 personas del corte UMAS de septiembre. El bloqueo demográfico
con mínimo de ingreso produjo 3.184 candidatos únicos; al exigir carrera con
Código Único resuelto, el subconjunto fue 6.629 personas y 3.338 candidatos únicos.
Estas cifras pertenecen al informe histórico, no se reprodujo ese corte. La frase
antigua «match único confiable» no acredita precisión: no hubo identidad validada.

No se reutiliza el mínimo de ingreso por persona, la selección de carrera actual
por mayor ANOINGRESO ni el Código Único completo como filtro. Se reutilizan el
propósito diagnóstico, el nacimiento AAAAMM, sexo y las agrupaciones institucionales.
El esquema oficial MRUN 2007–2026 confirma ahora la codificación de sexo que antes
estaba pendiente. Se preservó el PDF completo y la extracción de sus nueve páginas.

## Continuación ejecutada

Fuentes leídas: 15.045 filas UMAS y 24.386 filas MRUN. Se evaluaron 14.726 filas
UMAS con ANOMATRICULA entre 2007 y 2026; 319 filas posteriores quedaron fuera.
Los resultados son por expediente/fila, no personas únicas. No se comparan como
una mejora porcentual directa contra F0, porque cambian corte, unidad y filtros.

| Resultado después de año, nacimiento, sexo, familia y tipo cuando es unánime | Filas UMAS |
|---|---:|
| Un candidato único y recíproco por persona/año, no certificado | 6.098 |
| Un candidato por fila, pero no recíproco en ambas direcciones | 962 |
| Varios candidatos MRUN | 3.006 |
| Sin candidato | 3.703 |
| Sin agrupación de carrera disponible | 944 |
| Sin datos comparables suficientes | 13 |
| Total | 14.726 |

Reciprocidad: el MRUN candidato no corresponde a varios RUT y el RUT no conserva
varios MRUN candidatos en ese año al considerar todos sus expedientes. No prueba
identidad; los errores de datos y las coincidencias fortuitas siguen sin tasa
estimable. Ningún vínculo fue certificado ni exportado como identidad.

Se contrasta ANOINGRESO después del bloqueo. Entre las 6.098 filas con candidato
recíproco, 4.329 coinciden tanto con ingreso original como actual, 875 solo con
original, 691 solo con actual y 203 con ninguno. Son comparaciones candidatas,
no razones para modificar los años de las fuentes.

## CILOG

| Año de matrícula UMAS | Único y recíproco, no certificado | Varios candidatos | Sin candidato | Total |
|---|---:|---:|---:|---:|
| 2024 | 0 | 0 | 3 | 3 |
| 2025 | 6 | 0 | 2 | 8 |
| 2026 | 24 | 8 | 6 | 38 |
| Total | 30 | 8 | 11 | 49 |

Los once sin candidato figuran eliminados en el extracto UMAS. Esto es una
asociación observada, no prueba universal de que todos los eliminados se excluyan
de SIES. Los seis candidatos de 2025 incluyen cinco vigentes y un suspendido;
los 32 expedientes de 2026 con candidatos están vigentes (31 alumno regular y
una reincorporación).

Las ocho ambigüedades de persona en 2026 tienen un solo Código Único entre sus
candidatos: la duda de identidad no implica necesariamente duda de programa.
Los 24 candidatos recíprocos de 2026 y los seis de 2025 presentan
I162S2C77J4V2. La presencia de un único código es evidencia condicionada a la
agrupación y al tipo de plan ya gobernados, no una validación independiente de
ese perfil ni una autorización de asignación automática. No se utiliza el total
32 para forzar correspondencias ni se elimina una fila para cuadrar cifras.

## Ubicación y reproducción

Punto de entrada del antecedente: procesos/caracterizacion/gobernanza/trazabilidad_mrun.
Continuación: `python3 scripts/diagnosticar_candidatos_mrun_umas.py`.
Recursos registrados en PROYECTO_IPSS.json; no existe un nuevo proyecto paralelo.

[Resumen](../data/recuperacion_cruce_mrun_umas/20261016/resumen.json),
[conteos por carrera y situación](../data/recuperacion_cruce_mrun_umas/20261016/candidaturas_por_carrera_estado.json),
[CILOG](../data/recuperacion_cruce_mrun_umas/20261016/cilog.json),
[esquema oficial completo](../data/recuperacion_cruce_mrun_umas/20261016/ER_Matricula_Educacion_Superior_2007_2026_PUBL_MRUN.pdf).

Se conserva el Excel del usuario y las 137 referencias protegidas. La continuación
está preparada localmente en el repositorio, sin commit ni publicación remota.
