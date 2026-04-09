# Lógica de selección de versiones SIES en Matrícula Unificada

Generado: 2026-06-25T14:30:41

## Hallazgo técnico

La lógica programada no usa una regla global simple de primera o última coincidencia.
El flujo usa `DURACION_ESTUDIOS.tsv` como dimensión canónica, registra candidatos en
`CODIGOS_SIES_POTENCIALES`, intenta resolver ambigüedades mediante tablas/puentes
y reglas de desambiguación, y deja `PENDIENTE_GOBERNANZA` cuando no existe una
selección trazable. La QA bloquea `PRIMERA_OPCION` en registros incluidos.

## Evidencia extraída

- `codigo_gobernanza_v2.py:26` (fuente_dimension_oferta): `# FUENTE ÚNICA GOBERNANZA SIES: DURACION_ESTUDIOS.tsv`
- `codigo_gobernanza_v2.py:55` (fuente_dimension_oferta): `Path(__file__).with_name("DURACION_ESTUDIOS.tsv"),`
- `codigo_gobernanza_v2.py:56` (fuente_dimension_oferta): `Path.cwd() / "DURACION_ESTUDIOS.tsv",`
- `codigo_gobernanza_v2.py:70` (fuente_dimension_oferta): `"""Construye matriz (CODCARPR, JORNADA, VERSION)->SIES desde DURACION_ESTUDIOS.tsv."""`
- `codigo_gobernanza_v2.py:74` (fuente_dimension_oferta): `print("⚠️  DURACION_ESTUDIOS.tsv no disponible para construir matriz SIES")`
- `codigo_gobernanza_v2.py:88` (fuente_dimension_oferta): `val = (getattr(row, "CODIGO_UNICO", ""), "100%", "AUTO_DURACION_ESTUDIOS")`
- `codigo_gobernanza_v2.py:95` (fuente_dimension_oferta): `print(f"⚠️  Conflictos en matriz auto desde DURACION_ESTUDIOS: {conflictos} (se conserva primera ocurrencia)")`
- `codigo_gobernanza_v2.py:96` (fuente_dimension_oferta): `print(f"✅ Matriz SIES auto construida desde DURACION_ESTUDIOS: {len(matriz_dict)} llaves")`
- `codigo_gobernanza_v2.py:100` (fuente_dimension_oferta): `# Cargar matriz al iniciar desde DURACION_ESTUDIOS.tsv`
- `codigo_gobernanza_v2.py:119` (fuente_dimension_oferta): `"DURACION_ESTUDIOS", "DURACION_TITULACION", "DURACION_TOTAL", "NIVEL_CARRERA", "TIPO_UNIDAD_MEDIDA",`
- `codigo_gobernanza_v2.py:1385` (pendiente_gobernanza): `# --- Sección 1: PENDIENTE_GOBERNANZA (ambiguos sin resolver) ---`
- `codigo_gobernanza_v2.py:1386` (pendiente_gobernanza): `pend = archivo_subida[archivo_subida.get("SIES_RESOLUCION_HEURISTICA", pd.Series()) == "PENDIENTE_GOBERNANZA"]`
- `codigo_gobernanza_v2.py:1397` (pendiente_gobernanza): `"SECCION": "PENDIENTE_GOBERNANZA",`
- `codigo_gobernanza_v2.py:1918` (fuente_dimension_oferta): `CODIGO_UNICO, MODALIDAD, JORNADA, DURACION_ESTUDIOS, TIPO_PLAN_CARRERA, NIVEL_CARRERA.`
- `codigo_gobernanza_v2.py:1921` (fuente_dimension_oferta): `required_cols = {"CODIGO_UNICO", "MODALIDAD", "JORNADA", "DURACION_ESTUDIOS"}`
- `codigo_gobernanza_v2.py:1963` (fuente_dimension_oferta): `base_usecols = ["CODIGO_UNICO", "MODALIDAD", "JORNADA", "DURACION_ESTUDIOS", "VIGENCIA"]`
- `codigo_gobernanza_v2.py:1982` (fuente_dimension_oferta): `# ── Fallback: DURACION_ESTUDIOS.tsv como dimensión oferta ────────────────`
- `codigo_gobernanza_v2.py:1984` (fuente_dimension_oferta): `Path(__file__).with_name("DURACION_ESTUDIOS.tsv"),`
- `codigo_gobernanza_v2.py:1985` (fuente_dimension_oferta): `Path.cwd() / "DURACION_ESTUDIOS.tsv",`
- `codigo_gobernanza_v2.py:1994` (fuente_dimension_oferta): `for nc in ["MODALIDAD", "JORNADA", "DURACION_ESTUDIOS", "VIGENCIA",`
- `codigo_gobernanza_v2.py:2000` (fuente_dimension_oferta): `dim["OFERTA_SOURCE_SHEET"] = "DURACION_ESTUDIOS_TSV"`
- `codigo_gobernanza_v2.py:2005` (fuente_dimension_oferta): `return pd.DataFrame(columns=["CODIGO_UNICO", "MODALIDAD", "JORNADA", "DURACION_ESTUDIOS", "VIGENCIA"])`
- `codigo_gobernanza_v2.py:2064` (fuente_dimension_oferta): `"""Genera catálogo manual y puente SIES desde DURACION_ESTUDIOS.tsv."""`
- `codigo_gobernanza_v2.py:2071` (fuente_dimension_oferta): `print("⚠️  DURACION_ESTUDIOS sin columnas mínimas para construir puente/catálogo")`
- `codigo_gobernanza_v2.py:2104` (fuente_dimension_oferta): `print(f"✅ Catálogo/puente auto desde DURACION_ESTUDIOS: catalogo={len(cat_manual)} puente={len(puente)}")`
- `codigo_gobernanza_v2.py:2581` (fuente_dimension_oferta): `manual_source = catalogo_manual_tsv_path or "auto:DURACION_ESTUDIOS.tsv"`
- `codigo_gobernanza_v2.py:3460` (fuente_dimension_oferta): `# Fuente base manual: se reconstruye desde DURACION_ESTUDIOS para trazabilidad`
- `codigo_gobernanza_v2.py:3543` (resolucion_manual): `"GRUPO_TRAZA": "GRUPO_TRAZA_MANUAL",`
- `codigo_gobernanza_v2.py:3544` (resolucion_manual): `"FAMILIA_TRAZA": "FAMILIA_TRAZA_MANUAL",`
- `codigo_gobernanza_v2.py:3552` (resolucion_manual): `{True: "MATCH_MANUAL", False: "SIN_MATCH_MANUAL"}`
- `codigo_gobernanza_v2.py:3555` (resolucion_manual): `archivo_subida["GRUPO_TRAZA_MANUAL"] = pd.NA`
- `codigo_gobernanza_v2.py:3556` (resolucion_manual): `archivo_subida["FAMILIA_TRAZA_MANUAL"] = pd.NA`
- `codigo_gobernanza_v2.py:3692` (resolucion_manual): `archivo_subida["GRUPO_TRAZA"] = archivo_subida["GRUPO_TRAZA_PUENTE"].combine_first(archivo_subida["GRUPO_TRAZA_MANUAL"])`
- `codigo_gobernanza_v2.py:3912` (fuente_dimension_oferta): `oferta_duracion = archivo_subida[FINAL_SIES_CODE_COL].map(oferta_idx["DURACION_ESTUDIOS"].to_dict())`
- `codigo_gobernanza_v2.py:3942` (fuente_dimension_oferta): `# ── Fallback COD_CAR: mapeo NOMBRE_CARRERA → CODIGO_CARRERA vía DURACION_ESTUDIOS ──`
- `codigo_gobernanza_v2.py:3961` (fuente_dimension_oferta): `# ── Fallback VERSION: cuando COD_CAR+JOR están, usar la versión máxima de DURACION_ESTUDIOS ──`
- `codigo_gobernanza_v2.py:3977` (fuente_dimension_oferta): `print(f"    ↳ VERSION fallback DURACION_ESTUDIOS max: {int(_filled_ver.sum())} filas")`
- `codigo_gobernanza_v2.py:3982` (fuente_dimension_oferta): `archivo_subida["DURACION_ESTUDIOS_REF"] = pd.to_numeric(oferta_duracion, errors="coerce").astype("Int64")`
- `codigo_gobernanza_v2.py:4029` (fuente_dimension_oferta): `cod_car_source.loc[_fb_nombre_mask] = "DURACION_ESTUDIOS_NOMBRE"`

## Interpretación diagnóstica

- `DURACION_ESTUDIOS.tsv` aporta la oferta, duración, tipo de plan, jornada, sede,
  carrera y versión.
- `PUENTE_SIES_COMPILADO.tsv` conserva llaves por jornada, CODCARPR y nombre,
  candidatos potenciales, estado de resolución y columnas de condición por año cuando existen.
- `_resolver_ambiguedades_sies_heuristica` evita `PRIMERA_OPCION`; si no puede resolver,
  marca `PENDIENTE_GOBERNANZA`.
- `REGLA_COD_CAR_JOR_VERSION` resuelve cuando la fila trae combinación compatible
  de carrera, jornada y versión.
- Las decisiones manuales o de puente pueden coexistir con reglas heurísticas.
