# Discriminación de VIG por código · 28-10-2026

## Fuente, alcance y cautela

La referencia pedida, `procesos/caracterizacion/gobernanza/sies/RETENCION/Retencion_ipss_2022_2024_GRANULAR.xlsx`, hoja `Matriz Retencion Carrera`, es un **cálculo interno previo**, no una publicación oficial SIES: así lo establece su manifiesto (B). Por tanto, la comparación no verifica la regla frente a SIES. Su SHA-256 es `e85d8c15c9fa2eccb25a376ea352f345ddcec91dbcf8176070b1ae3490c5d946`.

La base individual de trabajo es `outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx`, hoja `BASE_RETENCION_MU`, SHA-256 `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd` (B). La unidad es persona por cohorte y código de la matrícula de ingreso, usando TIPO_DOC/N_DOC/DV, sin exportar identidades. Base: año informado = año de ingreso actual = cohorte y VIG=1. Seguimiento: presencia de la persona en la base del año siguiente, en cualquier carrera; la variante A exige alguna matrícula VIG=1 y la B acepta cualquier VIG (C). Ninguna de las dos verifica todavía que se conserve la cohorte de origen en t+1 (E).

Se compara simultáneamente el denominador y el numerador con las columnas `Tamano de Cohorte` y `Estudiantes Retenidos Institucional`. Ausencia de código no se convierte en cero. El archivo `paridad_por_codigo.csv` contiene el detalle agregado, sin identificadores.

## Resultado (C)

| Cohorte | Solo A | Solo B | Ambas | Ninguna | Sin cohorte MU | Personas VIG=0 en códigos solo A | Personas VIG=0 en códigos solo B |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 0 | 0 | 17 | 0 | 0 | 0 | 0 |
| 2023 | 2 | 0 | 7 | 0 | 1 | 2 | 0 |
| 2024 | 0 | 10 | 11 | 3 | 1 | 0 | 52 |

Para cada cohorte no hay personas en más de un código de ingreso dentro del universo extraído. Las diferencias A→B corresponden efectivamente a VIG=0 sin otra matrícula VIG=1 observada en t+1; no se encontró otro estado entre esas diferencias. Hay 25 filas de 2022–2025 con llave personal incompleta; no se incluyeron y su impacto por cohorte debe revisarse (E). No se detectaron códigos incompletos en las filas de cohorte con llave válida.

En 2023 los códigos `I162S2C1J4V2` e `I162S2C46J2V1` coinciden solo con A (una persona VIG=0 en cada uno). En 2024 diez códigos coinciden solo con B, con 52 personas en total. Tres códigos no coinciden con ninguna variante y `I162S2C53J3V1` está en la referencia sin cohorte MU identificada: su denominador de referencia es 19 en 2023 y 13 en 2024. Para 2024 los tres códigos con diferencia de numerador concentran cinco retenidos adicionales de referencia: 2 + 2 + 1.

## Interpretación y decisión pendiente (C/E)

El ajuste es **mixto**: A es el mejor ajuste en dos códigos de 2023 y B en diez de 2024. Como la referencia es interna, ninguna variante queda validada como regla oficial ni se justifica adoptar reglas diferentes por año. El motivo de las diferencias es E; la prueba de versiones previa no basta para explicar el registro individual y requiere revisión de sus llaves y fechas antes de reutilizarla.

La definición oficial (A) sigue siendo permanencia matriculada en la misma institución y cohorte de origen en t+1. El prototipo existente usa presencia con cualquier VIG (C), no verifica aún la cohorte de origen, y no debe presentarse como reproducción demostrada de SIES.

Para la cohorte 2025 (D/E), **no calcular ni publicar todavía**. Las filas VIG=0 de la MU 2026, incluidos los controles institucionales de nómina auditados, se preservan sin revertir y no se cuentan automáticamente como retenidas; se requiere acreditar el tratamiento de matrícula y cohorte de origen, integrar el universo de ingresos y conciliar con una fuente oficial. Las 960 son filas de un envío, no 960 personas necesariamente afectadas de la cohorte. El prototipo actual no impide calcular 2025: ejecutar su opción por defecto produciría una cifra no autorizada para uso; queda pendiente añadir un bloqueo antes de su uso operativo.

## QA (C)

Los dos SHA-256 fueron verificados al inicio de `analizar.py`; se comprobaron llaves incompletas, códigos incompletos, duplicados de referencia, solapamiento entre códigos, y estados distintos de cero en la diferencia A→B. No se alteraron fuentes, bases, denominadores ni la regla activa. Se recomienda comparar después contra una fuente SIES auténtica por código, documentando el universo y el tratamiento de cohorte de origen.
