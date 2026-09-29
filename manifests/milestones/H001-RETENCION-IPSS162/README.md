# H001-RETENCION-IPSS162

## Objetivo

Dejar gobernado y trazable el cálculo de retención de primer año de IPSS, código SIES 162, con comparación agregada contra SIES y reconciliación interna granular 2022–2024.

## Alcance

Libro de retención de cohortes 2022–2025, fuentes SIES congeladas, fuente interna previa identificada correctamente como autoría de Alexi Marcelo Burgos Flores, y trazabilidad de hashes, fórmulas y limitaciones metodológicas.

## Entradas

- Base RAW de matrícula unificada informada a SIES 2022–2026.
- Catálogo de duración y elegibilidad de carreras.
- `Informe_Retencion_SIES_2026_270702026.xlsx`, fuente SIES agregada.
- `RETENCION_SIES_IPSS_162_GRANULAR_2025_CORREO_20260909.tsv`, tabla granular entregada por Rodrigo Rolando Meneses.
- `Retencion_ipss_2022_2024_GRANULAR.xlsx`, cálculo interno previo del usuario, no fuente SIES.
- `Informe_Retencion_1er_Anio_Pregrado_2026.pdf`, informe SIES agregado y metodológico.

## Salidas

- `outputs/retencion_primer_anio_ipss_162/20260928_231500/RETENCION_PRIMER_ANIO_IPSS_162_CORREGIDO_20260928_231500.xlsx`.
- Fuentes congeladas en `CARACTERIZACIÓN/gobernanza/sies/RETENCION/`.

## Archivos tocados

- Libro final de retención en `outputs/retencion_primer_anio_ipss_162/20260928_231500/`.
- Fuentes y manifiestos de `CARACTERIZACIÓN/gobernanza/sies/RETENCION/`.
- Este registro de hito.

## Validaciones

- Manifiestos JSON válidos.
- Archivos XLSX gobernados íntegros como ZIP.
- Libro final con 15 hojas.
- Cero errores de fórmula después del recálculo.
- Hash SIES congelado verificado: `168ac8baea6aee65fa8a40dfca5a269993951142c89cb536805f550b1ac3297b`.
- Snapshot SIES equivalente verificado: `03897a1604aa656f9ff60e232eda739e29f4912123e5d7127d6551a37957a8a1`.

## Resultado

**OK**.

## Evidencias

- Libro final: SHA-256 `52ad47d73bf3f6a9bdcb7b0e10bdfa2cfc97ae614376ed2f32b78d8898fb4624`.
- Fuente interna previa: SHA-256 `e85d8c15c9fa2eccb25a376ea352f345ddcec91dbcf8176070b1ae3490c5d946`.
- Informe SIES congelado: SHA-256 `168ac8baea6aee65fa8a40dfca5a269993951142c89cb536805f550b1ac3297b`.

## Pendientes

No hay pendientes críticos. Queda abierto solicitar directamente a SIES el granular 2022–2024 si se desea reemplazar la comparación interna por datos publicados equivalentes a 2025.

## Deuda técnica

La comparación granular 2022–2024 es interna, no SIES; está identificada en la hoja `13_CRUCE_GRANULAR_2022_2024`. La fecha exacta de corte al 30 de abril no es verificable para 2022–2023 porque el esquema consolidado no contiene `FECHA_MATRICULA`; se usa `VIG` como proxy.

## Siguiente paso

Solicitar a SIES, si se requiere, el desglose oficial por `CODIGO_UNICO` para las cohortes 2022–2024 y sustituir la comparación interna manteniendo la trazabilidad existente.
