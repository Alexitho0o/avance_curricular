# Validación externa de retención de 1er año IPSS 162 · 28-10-2026

## Fuentes y alcance

- **SIES 2025 (B):** `0 BASES DE DATOS/RETENCION/Informe_Retencion_SIES_2025.xlsx`, hoja `Retención 1er año x IES`, bloque IP, encabezado fila 44, institución código 162 en A63/B63; cohortes 2022/2023/2024 en R63/S63/T63. SHA-256 `e5b21fd4194725ed57a21c7e6511aa90c58cdab298d97a51ccf430861638f82d`.
- **SIES 2026 (B):** `0 BASES DE DATOS/RETENCION/Informe_Retencion_SIES_2026_270702026.xlsx`, misma hoja, encabezado fila 42, IPSS 162 en A59/B59; cohortes 2022–2025 en R59:U59. SHA-256 `03897a1604aa656f9ff60e232eda739e29f4912123e5d7127d6551a37957a8a1`. Las tasas 2022–2024 coinciden en ambas ediciones.
- **Correo SIES 2025 (B):** `procesos/caracterizacion/gobernanza/sies/RETENCION/RETENCION_SIES_IPSS_162_GRANULAR_2025_CORREO_20260909.tsv`, SHA-256 `1e1e4872c8aa54ba97c1c4749d1fa509e13a4c11f498e933c9efddbb92b24c61`, 36 códigos y una fila `Total general`; manifiesto y correo del 09-09-2026 acompañan su procedencia y definición (A). Se verificó suma de los códigos contra la fila total.
- **PDF 2026:** `RETENCION/Informe-de-Retención-de-1er-Año-de-Pregrado-2026.pdf`, SHA-256 catalogado `8397404b4f6640ec0ad45e085da45b736e4e9862713271e0af0b8eef5bb601f4`. El índice documental local describe un informe agregado del sistema; la búsqueda textual de la transcripción no localizó IPSS. No se atribuyen sus agregados nacionales a la institución. El PDF 2025 no se localizó en la carpeta consultada; sí su libro de tablas. El PDF 2026 aparece erróneamente bajo institucionales en el catálogo; pendiente reclasificarlo con su auditoría de totales (E).

Los libros por institución publican **tasas**, no tamaño de cohorte ni número de retenidos en esa hoja; no se deducen cantidades desde las tasas. No se encontró allí retención pública por código de carrera IPSS 2022–2024. El archivo granular `Retencion_ipss_2022_2024_GRANULAR.xlsx` es un cálculo interno previo, según su manifiesto: su coincidencia es consistencia interna, no validación externa.

## Comparación institucional (B/C/E)

Las variantes usan los agregados de `outputs/retencion_discriminacion_codigo_20261028/analizar.py`, reproducidos de MU 142342 y no leen la publicación para construir el cálculo. A: al menos una matrícula VIG=1 en t+1. B: presencia con cualquier VIG en t+1. Ambas usan personas únicas por cohorte, pero no verifican cohorte de origen en t+1 ni todas las exclusiones oficiales. Diferencia = tasa variante − tasa SIES, en puntos porcentuales (pp).

| Cohorte | SIES tasa | SIES casos / retenidos | Base interna | Variante A | Brecha A | Variante B | Brecha B |
|---:|---:|---|---:|---:|---:|---:|---:|
| 2022 | 68,95% | No publicados en esta hoja | 338 | 250 / 338 = 73,96% | +5,01 pp | 250 / 338 = 73,96% | +5,01 pp |
| 2023 | 70,57% | No publicados en esta hoja | 512 | 393 / 512 = 76,76% | +6,19 pp | 395 / 512 = 77,15% | +6,58 pp |
| 2024 | 67,50% | No publicados en esta hoja | 702 | 448 / 702 = 63,82% | −3,68 pp | 500 / 702 = 71,23% | +3,73 pp |
| 2025 | 58,21% | 1.163 / 677, correo; 92 no considerar fuera de casos | Pendiente | No calculada | — | No calculada | — |

El correo 2025 coincide con la tasa U59 del libro SIES 2026 (`677/1163`). Los 92 `no_considerar` no son parte de los 1.163. El valor previamente informado de 2.326 casos y 1.354 retenidos fue un error: sumó las filas por código más la fila `Total general`. Queda retirado.

## Conclusión y bloqueo

Ninguna variante reproduce las tasas oficiales 2022–2024. La menor brecha absoluta cambia según cohorte y no justifica elegir una regla por año. Persisten E: diferencias de elegibilidad, duración, programas especiales, corte y cohorte de origen; no se atribuyen causas sin evidencia.

La cohorte 2025 oficial sigue pendiente de conciliación. El bloqueo actualizado requiere declarar explícitamente **ambas** condiciones: cohorte conciliada con los 1.163 casos oficiales, explicando cualquier diferencia, y aprobación del tratamiento de VIG. Las banderas no prueban por sí mismas esas condiciones. La reproducción histórica H001 se registra aparte en `outputs/retencion_h001_base_20261028/INFORME.md`. Los VIG=0 de 2026 se conservan, sin revertirse ni contarse automáticamente como retenidos para una publicación oficial.

Regla: `BORRADOR_NO_ACTIVO`. No se modificaron fuentes ni denominadores. `verificar.py` verifica hashes, localizadores, tasas y total granular del correo; la comparación numérica se apoya en el cálculo agregado reproducible de la prueba por código. El cotejo en línea no se realizó por instrucciones del proyecto; las cifras provienen de las copias locales catalogadas.
