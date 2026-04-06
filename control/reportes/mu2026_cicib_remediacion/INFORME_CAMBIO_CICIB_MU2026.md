# Informe de Cambio SIES MU 2026 (CICIB)

## 1) Alcance y supuesto operativo

- No se recibió `CODCLI_LIST` ni `RUT_LIST` explícitos en esta ejecución.
- Universo auditado: todas las filas de `ARCHIVO_LISTO_SUBIDA` que cumplen reglas A-E por `(NOMBRE_CARRERA_FUENTE normalizado, JORNADA_FUENTE)`.
- Input utilizado: `/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx`

## 2) Artefactos detectados (Paso 0)

- `puente_sies.tsv`: **creado/intervenido** en raíz del repo.
- `matriz_desambiguacion_sies_final.tsv`: **no existe** en raíz.
- `catalogo_manual.tsv`: **no existe** en raíz.
- Baseline ANTES guardado en:
  - `control/reportes/mu2026_cicib_remediacion/archivo_listo_para_sies_ANTES.xlsx`

## 3) Cambio persistente aplicado

### 3.1 Override de puente SIES (persistente)

Se creó `puente_sies.tsv` con 5 reglas oficiales:

- A) `INGENIERIA EN CIBERSEGURIDAD` + `D` -> `I162S2C46J1V1`
- B) `INGENIERIA EN CIBERSEGURIDAD` + `V` -> `I162S2C46J2V1`
- C) `CONTINUIDAD INGENIERIA  CIBERSEGURIDAD` + `V` -> `I162S2C46J2V3`
- D) `CONTINUIDAD INGENIERIA  CIBERSEGURIDAD` + `O` -> `I162S2C46J4V1`
- E) `INGENIERIA EN CIBERSEGURIDAD` + `O` -> `I162S2C46J4V3`

### 3.2 Ajuste de pipeline para persistencia real

Archivo: `codigo_gobernanza_v2.py`

- Se mantuvo la base desde `DURACION_ESTUDIOS.tsv`.
- Se agregó aplicación de override desde `puente_sies.tsv`/`catalogo_manual.tsv` (si existen), por llave exacta `SOURCE_KEY_3`.
- Resultado: el cambio en TSV queda persistente entre corridas futuras sin modificar contrato MU32/CSV.

## 4) Re-ejecución oficial (Paso 4)

Comando ejecutado:

```bash
python3 codigo_gobernanza_v2.py \
  --input "/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx" \
  --output-dir resultados \
  --proceso matricula \
  --usar-gobernanza-v2 true
```

Artefactos generados:

- `resultados/archivo_listo_para_sies.xlsx`
- `resultados/matricula_unificada_2026_pregrado.csv`

## 5) Auditoría antes/después (Paso 5)

Resumen:

- `codcli_entregados`: 120
- `codcli_encontrados`: 120
- `codcli_no_encontrados`: 0
- `filas_universo_intervenido`: 1387
- `cambiados`: 206
- `ya_correctos`: 1181
- `fallidos`: 0
- `ambiguedad_post`: 0

Diagnóstico ANTES (causa raíz):

- `OK`: 1181
- `MATCH_AMBIGUO`: 190
- `PROBLEMA_LLAVE`: 16

Cambios efectivos por regla:

- A: 0 cambios (ya correcto)
- B: 0 cambios (ya correcto)
- C: 16 cambios
- D: 190 cambios
- E: 0 cambios (ya correcto)

Consistencia post (universo cambiado C+D):

- `SIES_MATCH_STATUS = MATCH_SIES` en 206/206 filas.
- `JOR` coherente con código esperado: 206/206 (sin mismatch).
- `MODALIDAD` no nula en 206/206.

## 6) Evidencia reproducible (Paso 6)

- Diagnóstico ANTES:
  - `control/reportes/mu2026_cicib_remediacion/DIAGNOSTICO_ANTES_CICIB.tsv`
- Evidencia antes/después:
  - `control/reportes/mu2026_cicib_remediacion/EVIDENCIA_CAMBIO_CICIB.tsv`
- Auditoría por RUT:
  - `control/reportes/mu2026_cicib_remediacion/AUDITORIA_RUT_CICIB.tsv`
- Resumen JSON:
  - `control/reportes/mu2026_cicib_remediacion/RESUMEN_CICIB.json`

## 7) Diff textual solicitado

### 7.1 puente_sies.tsv

```diff
diff --git a/Users/alexi/Documents/GitHub/avance_curricular/puente_sies.tsv b/Users/alexi/Documents/GitHub/avance_curricular/puente_sies.tsv
new file mode 100644
index 0000000..4ea05e2
--- /dev/null
+++ b/Users/alexi/Documents/GitHub/avance_curricular/puente_sies.tsv
@@ -0,0 +1,6 @@
+GRUPO_TRAZA	JORNADA	CODCARPR	NOMBRE_L	CODIGO_CARRERA_SIES	REGLA_APLICADA	RAZON_GOBERNANZA
+MU2026_CICIB	D	ICIB	INGENIERIA EN CIBERSEGURIDAD	I162S2C46J1V1	A	Resolucion dirigida por gobernanza MU 2026 (CICIB)
+MU2026_CICIB	V	ICIB	INGENIERIA EN CIBERSEGURIDAD	I162S2C46J2V1	B	Resolucion dirigida por gobernanza MU 2026 (CICIB)
+MU2026_CICIB	V	CICIB	CONTINUIDAD INGENIERIA  CIBERSEGURIDAD	I162S2C46J2V3	C	Resolucion dirigida por gobernanza MU 2026 (CICIB)
+MU2026_CICIB	O	CICIB	CONTINUIDAD INGENIERIA  CIBERSEGURIDAD	I162S2C46J4V1	D	Resolucion dirigida por gobernanza MU 2026 (CICIB)
+MU2026_CICIB	O	ICIB	INGENIERIA EN CIBERSEGURIDAD	I162S2C46J4V3	E	Resolucion dirigida por gobernanza MU 2026 (CICIB)
```

### 7.2 matriz_desambiguacion_sies_final.tsv

- No aplica en esta intervención (archivo no existe en raíz y no quedó ambigüedad pendiente en el universo intervenido).

## 8) Dictamen final

**DICTAMEN: `LISTO PARA ENTREGA`**

Condiciones verificadas:

- Sin `FAIL` en universo intervenido.
- Sin `AMBIGUO_SIES` post-cambio en universo intervenido.
- Cambio persistente en catálogo (`puente_sies.tsv`) y aplicado en corrida oficial.
- Sin modificación de estructura MU32 ni del CSV regulatorio.
