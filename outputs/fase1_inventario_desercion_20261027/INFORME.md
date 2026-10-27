# Fase 1 · Inventario ANALISIS_DESERCION_IPSS

## a) Mapa cifra → origen [E/C]

Las hojas 1–17 de V24 no conservan en sus propias celdas una referencia completa y verificable a script, corrida, fuente y hash para cada cifra. La procedencia disponible está separada en `~/.local/share/ipss/procedencia_v24_20261025/` y en los manifiestos de las corridas MU. Por tanto, el mapa exhaustivo por tabla queda **E** hasta reconstruirlo desde los artefactos de procedencia. Los scripts candidatos localizados (C) son `procesos/caracterizacion/EXTRACCION_MATRICULA_SIES _2007_2025/{calcular_retencion.py,analizar_retencion_interna_ipss.py,auditar_y_cruzar_retencion_ipss_162.py,generar_consolidado_retencion.py,generar_consolidado_retencion_completo.py}` y `procesos/caracterizacion/caracterizacion_retencion.py`.

## b) Corridas MU 2022–2026 [B/C]

Las cinco corridas de base tienen salidas distintas: 140919 (`c7a12654…`), 140942 (`1b8ea5ce…`), 141550 (`a9a4e757…`), 142154 con fórmulas (`9ae09564…`) y 142342 (`19cf33ae…`). La corrida 142342 es la base consolidada validada que V24 referencia en el ecosistema de retención; 142154/142351 son derivados con fórmulas, no la misma base byte a byte. Los manifiestos acreditan esquema, fuentes y validaciones, pero no prueban que cada tabla 1–17 de V24 haya sido producida exclusivamente por una corrida.

## c) Duplicaciones [B/C]

La tabla puente `TABLA_PUENTE_CSV_BASE_RETENCION_MU` existe en CARACTERIZACIÓN y en `procesos/caracterizacion` de avance_curricular, con CSV, XLSX y manifiesto. Los scripts de retención también aparecen en ambos repositorios. Para este subproyecto, la copia versionada en `avance_curricular/procesos/caracterizacion` y sus manifiestos gobernados son la referencia técnica; la copia de CARACTERIZACIÓN es antecedente y debe compararse por hash antes de reutilizarla. Se puede reutilizar el código de cálculo/auditoría, pero no declararlo canónico para el indicador nuevo hasta completar la trazabilidad de entradas y salidas.

## d) Vínculo RUT–MRUN [E]

Se localizaron diagnósticos y propuestas de trazabilidad MRUN, pero no una fuente gobernada que demuestre un enlace operativo RUT–MRUN para clasificar destino institucional caso a caso. El componente 3 permanece **E**. No se intentó enlazar por nombre, sexo, fecha de nacimiento ni otros atributos.

## Duplicaciones y límites

Los resultados de V24, las corridas MU y las tablas puente son artefactos relacionados, no una única cadena probada. La Fase 2 debe reutilizar los scripts identificados, registrar sus hashes y reconstruir la procedencia antes de comparar cifras.
