# Retención de 1er año · VIG por proceso · 28-10-2026

## Qué se comparó (C)

`analizar.py` reproduce H001 desde el libro de diagnóstico y compara, **sobre la misma cohorte elegible H001 y con igual año y semestre de origen en t+1**, dos alternativas: al menos un registro de t+1 con VIG positivo (`>=1`) y al menos un registro de t+1 con cualquier VIG. Las exclusiones H001 se mantienen fijas en ambas. La segunda es una sensibilidad, no una redefinición de la cohorte ni una tasa SIES. La referencia SIES es la tasa institucional del libro oficial 2026, hoja `Retención 1er año x IES`, R59:U59, SHA-256 `03897a1604aa656f9ff60e232eda739e29f4912123e5d7127d6551a37957a8a1`.

| Cohorte | H001 casos | Positivo: retenidos / tasa | Cualquier VIG: retenidos / tasa | Personas adicionales | Tasa SIES | Brecha positiva / cualquier VIG, pp |
|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 305 | 224 / 73,44% | 224 / 73,44% | 0 | 68,95% | +4,49 / +4,49 |
| 2023 | 366 | 258 / 70,49% | 260 / 71,04% | 2 | 70,57% | −0,08 / +0,47 |
| 2024 | 558 | 326 / 58,42% | 378 / 67,74% | 52 | 67,50% | −9,08 / +0,24 |
| 2025 | 1.150 | 668 / 58,09% | 1.066 / 92,70% | 398 | 58,21% | −0,12 / +34,48 |

La comparación 2025 es únicamente una sensibilidad histórica H001 con denominador fijo, no la cohorte oficial; 1.163 es el denominador del correo SIES. La proximidad de una tasa agregada no demuestra igualdad de personas ni causa.

## Significado documental de VIG (A/B/D/E)

El `Manual_Matrícula_Unificada_2026.pdf` (SHA-256 `3626600782798fbb5afa4100975eeffd2155b4912a112f63cee42f9741a82990`), página 37, define 0: estudiante sin matrícula; 1: estudiante con matrícula vigente; 2: estudiante egresado con matrícula vigente. En páginas 17–18 indica que un registro cargado con 0 no se cuenta en matrícula total ni para beneficios. Se consultó la transcripción local `manual_matrícula_unificada.txt`, SHA-256 `ce2dda6e32df94012679718e6e20f58a97fcf4ddf7038be5046d5d17238a67c9` (A, documento MU 2026). No se encontró un manual MU anual 2023, 2024 o 2025 en las fuentes del proyecto, la carpeta SIES enviada y los repositorios buscados; su definición anual queda E, sin afirmar inexistencia universal.

La auditoría `data/reglas_negocio/mu2027/estudio/AUDITORIA_VIG_ENVIOS_RETENCION.md` (SHA-256 `7ccfc88001e7e36ef3299d52dc5f7d6448bce63b995da1aa400634e465774f00`) documenta controles internos de nómina en la preparación MU 2026 y 960 **filas** VIG=0 en un envío; el fundamento académico individual queda pendiente (D/E). También registra cero cambios VIG fila a fila entre fuentes anuales seleccionadas y MU consolidada. El puente de matrícula agregada observa que ocho carreras de 2025 coinciden con el total de MU, incluyendo 73 registros VIG=0, pero esa coincidencia agregada no identifica personas ni prueba que SIES las incluyera individualmente.

**Conclusión:** está documentado un uso institucional de VIG=0 en MU 2026; no existe aquí evidencia suficiente para determinar si la diferencia 2025–2026 proviene de un cambio de definición SIES, de las nóminas u otra causa. La cercanía de la sensibilidad 2024 tampoco acredita cuál fue la regla oficial (E).

**Propuesta de tratamiento por proceso, sin activar:** MU 2026 interpreta el VIG según su manual y conserva las decisiones de carga (A/D); H001 aplica VIG positivo y misma cohorte de origen como cálculo interno reproducido (C); para retención oficial SIES y MU 2023–2025 la aplicación operativa y sus excepciones quedan E hasta disponer de instrucciones o una conciliación oficial adecuada. No trasladar automáticamente la regla de otro proceso o año.

## Cohorte 2022 y MU 2023 (B/C/E)

La MU 2023 seleccionada en el inventario de `20260901_142342` es `.../Matrícula Unificada/2023/2023.csv`, SHA-256 `cf13147baa2d0a10ad021e867362b593a95337259889b18b483d8710a4b90e35`; la auditoría informa 1.145 filas y VIG idéntico fila a fila entre esa fuente y la consolidada. El inventario no acredita por sí mismo que esta sea la versión final aceptada para la publicación SIES, ni el corte individual al 30 de abril (E).

H001 identifica 305 personas de cohorte 2022, 224 retenidas y 81 no retenidas. Las 81 no tienen ningún registro 2023 en la base seleccionada; por ello permitir cualquier VIG mantiene 224/305 y no explica +4,49 pp. H001 exige origen 2022 con semestre 1/2, catálogo anual único, pregrado regular no especial y duración mínima 4/6/8; excluye duplicidad activa y contradicción de origen. Frente al prototipo anterior de 338 personas, hay 33 solo en el prototipo: 31 por origen no admitido como primera condición y 2 por duplicidad o inconsistencia. Esto explica diferencias entre implementaciones internas, no las diferencias de población respecto de SIES.

El hito H001 registra que los 305 cumplen `NIV_ACA=1` y `FOR_ING_ACT=1`; sus análisis previos de duración, exclusiones y cobertura no establecieron la causa de la brecha. La publicación consultada no entrega las personas ni el denominador oficial por institución; falta fuente individual compatible o desglose oficial y trazabilidad RUT–MRUN para asignar causalidad. Brecha **E**, no error demostrado de SIES ni de la matrícula individual.

## Nóminas 2026: escenario H001 (B/C/E)

`data/reglas_negocio/mu2027/estudio/RESULTADOS_AGREGADOS.json` (SHA-256 `003c55b57e2aa476a8bd6d9223ec46d4155f59f7311d0183eea24c795226cff0`) identifica **291 personas de las nóminas dentro de las 1.150 de H001 2025**, todas no retenidas en el diagnóstico; **276** tienen en MU 2026 al menos una matrícula con la misma cohorte de origen y VIG=0. En un escenario hipotético, si solo esas 276 se considerasen retenidas y nada más cambiara: `(668+276)/1.150 = 944/1.150 = 82,09%`, +24,00 pp frente a 58,09%. Es un cálculo H001 con denominador interno fijo, **no una tasa oficial ni una corrección propuesta**.

No se puede calcular legítimamente su efecto sobre la tasa oficial de 677/1.163 sin acreditar qué personas de esa cohorte oficial coinciden con los 276 y sus categorías SIES. No se suma 276 al numerador oficial por suposición. Falta la trazabilidad individual y el fundamento de las nóminas (E). Tampoco corresponde contar automáticamente las 960 filas VIG=0 como personas de esta cohorte.

## QA

Script reproducible con verificación SHA de libro H001 y resultados agregados de auditoría; cuatro denominadores fijos y regla de origen verificados. No se exportan identificadores, no se modifican fuentes ni denominadores. El componente continúa `BORRADOR_NO_ACTIVO`. Se recomienda validar una norma o comunicación oficial aplicable por año y el tratamiento de casos 2022 antes de activar una regla de retención.
