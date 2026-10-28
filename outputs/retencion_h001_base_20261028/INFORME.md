# Retención de 1er año · base H001 · 28-10-2026

## Fuente y alcance (B/C/E)

Se reprodujo la sección «Same calculation as frozen formulas» de `data/reglas_negocio/mu2027/estudio/auditar_solo_lectura.py`, commit `55e3b709afb9483f0ecdd2d166f67229a454a5ef`, SHA-256 `ba71eea98eebe3627593b613a37897ef6dd4d7b6e39d8a31732771807e0f5f30`. La fuente de datos y catálogo es `outputs/retencion_primer_anio_ipss_162/20260930_000000/RETENCION_PRIMER_ANIO_IPSS_162_DIAGNOSTICO_BRECHAS_20260930.xlsx`, SHA-256 `5f0f7c7f0f238556de374d287bf2931ccc8a93a5489f4c2f2b543befd38c77b3`, hojas `BASE_RETENCION_MU` y `01_CATALOGO_CARRERA`. La auditoría acredita que RAW coincide con la MU consolidada `20260901_142342`. El manifiesto H001 `manifests/milestones/H001-RETENCION-IPSS162/README.md`, mismo commit, SHA-256 `6f1184f40f91d2c0df73fed2296cd11323aa108ce1cb30474bb000b8bdef7c48`, documenta el diagnóstico y sus límites.

La reproducción histórica no activa el componente ni autoriza publicar su resultado como SIES. En cada cohorte, el número de filas elegibles coincidió con el de personas únicas; las identidades permanecieron en memoria y no se exportaron.

## Lógica reproducida (C)

1. Para cada fila, `ANIO_ING_ORI = ANIO_INFORMADO = t`, `SEM_ING_ORI` en 1 o 2 y `VIG` distinto de 0.
2. Componer `I162S{COD_SED}C{COD_CAR}J{JOR}V{VERSION}` y exigir una sola fila de catálogo para `OFE_t` y ese código. Exigir `NIVEL_GLOBAL=Pregrado`, `TIPO_CARRERA=Plan Regular`, `PLAN_ESPECIAL=NO APLICA` y duración de estudios mínima de 4/6/8 semestres según nivel del catálogo. Un nivel no reconocido o sin catálogo único no se incluye.
3. Identificar persona por TIPO_DOC/N_DOC/DV. Excluir si hay más de una matrícula positiva de la misma persona y cohorte de origen en t o si alguna matrícula positiva en t+1 tiene otra cohorte de origen. Esto reproduce la exclusión del diagnóstico, no demuestra automáticamente que el criterio oficial elimine cada caso individual.
4. Retenido: al menos una matrícula en t+1 con `VIG >= 1` y el mismo año y semestre de origen. El código de carrera puede cambiar dentro de IPSS. Candidato no retenido si no hay tal matrícula y no cae en las exclusiones anteriores.

La regla oficial del correo (A) excluye casos específicos con inconsistencias de cohorte de origen y programas especiales. Sus 92 `no_considerar` de 2025 no integran los 1.163 casos. Sin vinculación individual demostrada, no se presume que cada exclusión H001 sea exactamente una exclusión SIES.

## Reproducción y comparación externa (B/C/E)

| Cohorte | H001: retenidos / casos | Tasa H001 | Tasa SIES publicada | Diferencia H001 − SIES |
|---:|---:|---:|---:|---:|
| 2022 | 224 / 305 | 73,44% | 68,95% | +4,49 pp |
| 2023 | 258 / 366 | 70,49% | 70,57% | −0,08 pp |
| 2024 | 326 / 558 | 58,42% | 67,50% | −9,08 pp |
| 2025 | 668 / 1.150 | 58,09% | 58,21% | −0,12 pp |

Las tasas SIES están en `Informe_Retencion_SIES_2026_270702026.xlsx`, hoja `Retención 1er año x IES`, celdas R59:U59, SHA-256 `03897a1604aa656f9ff60e232eda739e29f4912123e5d7127d6551a37957a8a1`; para 2025 el correo contiene 1.163 casos / 677 retenidos, más 92 no considerados fuera de los casos. La suma 2.326 se retira como duplicación del total general.

## Qué se conoce sobre las brechas de 2022 y 2024 (B/C/E)

La fuente pública consultada publica tasas por institución, no las personas ni los totales por código 2022–2024. Tampoco se ha acreditado una llave RUT–MRUN. Por tanto, no es posible identificar qué personas o programas son la causa de la diferencia frente a SIES ni asignar individualmente sus `no_considerar` (E).

Sí se puede comparar **internamente** H001 con el prototipo anterior: en 2022 este último incluye 33 personas adicionales (338 frente a 305); entre sus códigos de ingreso están C46J4V3 con 9 registros y C1J4V2 con 8. En 2024 incluye 144 adicionales (702 frente a 558), de los cuales 60 registros son C3J4V2, 49 C46J4V3 y 29 C1J4V2. Estos conteos son comparación interna, no diferencias oficiales por programa. En H001, 180 de los 232 no retenidos de 2024 no aparecen en el RAW 2025 según la auditoría H001; esa ausencia no identifica la causa oficial de la brecha. El hito conserva la causa de las brechas 2022 y 2024 como E.

## Diferencia 2025 entre prototipo y H001 (C/E)

Las 1.150 personas H001 están dentro de las 1.503 del prototipo anterior; quedan **353 solo en el prototipo**. Una clasificación jerárquica por primera condición de H001 identifica:

- 249 por origen no admitido: 216 tienen `ANIO_ING_ORI=1900` y `SEM_ING_ORI=0`, cuyo significado real no está acreditado; 33 registran un año anterior a 2025. No se interpreta 1900 como ingreso real.
- 104 por controles posteriores: 103 tienen alguna matrícula positiva en 2026 con otro origen y una persona tiene múltiples matrículas positivas en 2025 de la misma cohorte. Son condiciones de exclusión H001; no se afirma que SIES excluiría exactamente a esas personas.

En otra dimensión, no aditiva a la anterior, el catálogo identifica **129 personas en planes de continuidad** y 224 en planes regulares; 353 tienen `PLAN_ESPECIAL=NO APLICA`. Al revisar filas de catálogo para esas personas, hay 129 con duración inferior al mínimo y 225 que cumplen el mínimo; son 354 filas, no 354 personas, por una matrícula adicional. Estas categorías se solapan con las causas por origen y no deben sumarse.

## Control y pendientes

`common/analisis_desercion/h001.py` reproduce H001; `verificar_h001.py` comprueba hash, cuatro pares numerador/denominador, unicidad y conciliación 2025. El cálculo ordinario 2025 requiere declaración explícita de cohorte conciliada con 1.163 ± explicación y tratamiento VIG aprobado. Las banderas no acreditan la evidencia por sí mismas. La función `reproducir_h001` se utiliza aquí únicamente para reproducir el diagnóstico histórico.

Regla `BORRADOR_NO_ACTIVO`. No se cambiaron las bases, fuentes ni sus denominadores. Pendiente: fuente oficial individual o desglose verificable 2022–2024, conciliación de los 13 casos y nueve retenidos agregados de 2025 descritos en H001, validación del tratamiento de VIG y revisión del marcador 1900/0.
