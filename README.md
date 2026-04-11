
# Avance Curricular — Estructura, Uso y SDD

Repositorio estandarizado bajo Spec-Driven Development (SDD) para la gestión, validación y auditoría de datos curriculares y salida regulatoria MU 2026 Pregrado.

## Estructura del Repositorio

- **scripts/**
  - Orquestación oficial del pipeline y utilitarios operativos.
- **resultados/**
  - Salidas reales de ejecución y validación.
- **control/**
  - Catálogos compilados, reportes técnicos, evidencia y trazabilidad.
- **docs/**
  - Documentación técnica, manuales, especificaciones y gobernanza.
- **data/**
  - Soporte documental y referencias; no es la ruta runtime principal de outputs.
- **archive/**
  - Históricos y respaldos.
- **core/**
  - Estructura objetivo o transicional; no corresponde al runtime oficial actual.

## Ejemplo de Flujo de Trabajo

### Opción A (recomendada): Makefile
```bash
cd /ruta/al/repo/avance_curricular
make run-oficial INPUT_XLSX="/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx"
make validate-oficial
```
Ejecución + validación en una sola secuencia:
```bash
make run-and-validate-oficial INPUT_XLSX="/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx"
```
Ayuda:
```bash
make help
```

### Opción B (manual, equivalente)
```bash
cd /ruta/al/repo/avance_curricular
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export INPUT_XLSX="/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx"
export OUTPUT_DIR="resultados"
python3 codigo_gobernanza_v2.py \
  --input "$INPUT_XLSX" \
  --output-dir "$OUTPUT_DIR" \
  --proceso matricula \
  --usar-gobernanza-v2 true

python3 qa_checks.py --output-dir "$OUTPUT_DIR" --fase6-control-dir "control"
```

## Buenas Prácticas y SDD
- Toda nueva funcionalidad debe estar precedida por una especificación en `docs/`.
- Usar snake_case o kebab-case para archivos y carpetas.
- Documentar scripts y módulos con docstrings y comentarios claros.
- Mantener la trazabilidad de cambios relevantes en `docs/` o `agent.md`.
- Los cambios deben ser atómicos y fácilmente reversibles.
- Priorizar la legibilidad y mantenibilidad para humanos y agentes.

## Artefactos Oficiales y Advertencias

| Artefacto | Estado | Uso operativo |
|---|---|---|
| `DURACION_ESTUDIOS.tsv` | EXISTE | Fuente canónica para matriz SIES y dimensión de oferta |
| `control/catalogos/PUENTE_SIES_COMPILADO.tsv` | EXISTE | Fuente canónica única de cruce SIES por SOURCE_KEY_3 |
| `resultados/archivo_listo_para_sies.xlsx` | EXISTE | Auditoría y trazabilidad |
| `resultados/matricula_unificada_2026_pregrado.csv` | EXISTE | Carga regulatoria (MU32, 32 columnas, sin header) |
| `resultados/reporte_matricula.json` | EXISTE | Métrica de corrida |
| `resultados/auditoria_maestra.md` | EXISTE | Dictamen QA integral |

**No usar como salida regulatoria final:**
- Cualquier salida en `archive/` o en subcarpetas históricas de `resultados/`
- Archivos legacy: `matricula_unificada_2026_oficial.xlsx`, `MU2026_regulatorio.csv`, etc.

## Referencias y Documentación
- Ver `docs/DOCUMENTACION_TECNICA.md` para detalles de integración, reglas de negocio y ejemplos avanzados.
- Reglas para agentes de IA: ver `agent.md`.

---
Última actualización: 2026-04-10
Responsable: Arquitectura Técnica

### Trazabilidad complementaria

- Gobernanza por columna: `gobernanza_columnas_mu/` + `_INDICE_COLUMNAS.tsv`.
- Auditoria integral: `scripts/auditoria_maestra.py`.
- Mapa de cruces del pipeline: `cruces_proyecto.tsv`.

### Cruces criticos verificados (fuente: cruces_proyecto.tsv)

- Cruce SIES central por `SOURCE_KEY_3`: `codigo_gobernanza_v2.py` L2447 (merge `archivo_subida` × `bridge_exact`).
- Enriquecimiento OfertaAcademica: `codigo_gobernanza_v2.py` L2589+ (indice por `CODIGO_UNICO` y lookups de MODALIDAD/JOR/DURACION/COD_CAR).
- Enriquecimiento Duracion: `codigo_gobernanza_v2.py` L3138+ (lookup por `CODIGO_UNICO`) y L3147+ (fallback por `COD_CAR`).
- Match DatosAlumnos: `codigo_gobernanza_v2.py` L1716 (CODCLI), L1735 (fallback RUT), L1747 (`combine_first` de campos DA).
- QA de salida y gate: `qa_checks.py` + `scripts/auditoria_maestra.py`.

### Mapa de cruces del pipeline (linaje auditable)

Archivo de referencia:

- `cruces_proyecto.tsv`

Rol operativo:

- Inventario auditable de cruces/transformaciones en `codigo_gobernanza_v2.py`.
- Registra por evento estos campos: `Archivo | Línea | Tipo | Descripción | Left | Right | Columnas clave | Contexto pipeline`.
- Incluye operaciones de cruce como `merge`, `map`, `combine_first`, `concat` y cargas `_load`.

Uso recomendado:

1. Validar que el README refleje cruces reales, sin pasos inventados.
2. Auditar que refactorizaciones no eliminen cruces criticos (SIES, DatosAlumnos, Oferta, Duracion, QA).
3. Alinear gobernanza documental con la ejecucion oficial congelada MU 2026.

## 4) Flujo oficial de ejecucion (reproducible)

### Opcion A (recomendada): `make`

```bash
cd /ruta/al/repo/avance_curricular
make run-oficial INPUT_XLSX="/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx"
make validate-oficial
```

Ejecucion + validacion en una sola secuencia:

```bash
cd /ruta/al/repo/avance_curricular
make run-and-validate-oficial INPUT_XLSX="/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx"
```

Ayuda:

```bash
make help
```

La corrida oficial compila primero el catálogo canónico SIES en:

- `control/catalogos/PUENTE_SIES_COMPILADO.tsv`

### Opcion B (equivalente directo)

```bash
cd /ruta/al/repo/avance_curricular
export INPUT_XLSX="/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx"
export OUTPUT_DIR="resultados"
python3 scripts/compile_puente_sies_compilado.py \
  --duracion "DURACION_ESTUDIOS.tsv" \
  --output "control/catalogos/PUENTE_SIES_COMPILADO.tsv"

python3 codigo_gobernanza_v2.py \
  --input "$INPUT_XLSX" \
  --output-dir "$OUTPUT_DIR" \
  --proceso matricula \
  --usar-gobernanza-v2 true

python3 qa_checks.py --output-dir "$OUTPUT_DIR" --fase6-control-dir "control"
```

## 5) Artefactos de salida (que usar y que NO usar)

### Oficiales para MU 2026 Pregrado

- `resultados/archivo_listo_para_sies.xlsx` (auditoria y trazabilidad)
- `resultados/matricula_unificada_2026_pregrado.csv` (carga regulatoria)
- `resultados/reporte_matricula.json` (metrica de corrida)
- `resultados/auditoria_maestra.md` (dictamen QA integral)

### Contrato MU32 (no negociable)

- Archivo: `matricula_unificada_2026_pregrado.csv`
- Delimitador: `;`
- Header: **NO**
- Columnas: **32 exactas**

Orden contractual MU32:

```text
TIPO_DOC;N_DOC;DV;PRIMER_APELLIDO;SEGUNDO_APELLIDO;NOMBRE;SEXO;FECH_NAC;NAC;PAIS_EST_SEC;COD_SED;COD_CAR;MODALIDAD;JOR;VERSION;FOR_ING_ACT;ANIO_ING_ACT;SEM_ING_ACT;ANIO_ING_ORI;SEM_ING_ORI;ASI_INS_ANT;ASI_APR_ANT;PROM_PRI_SEM;PROM_SEG_SEM;ASI_INS_HIS;ASI_APR_HIS;NIV_ACA;SIT_FON_SOL;SUS_PRE;FECHA_MATRICULA;REINCORPORACION;VIG
```

### No usar como salida regulatoria final

- `resultados/matricula_unificada_2026_oficial.xlsx`
- `resultados/MU2026_regulatorio.csv`
- Cualquier salida en `archive/` o en subcarpetas historicas de `resultados/`

## 6) Catalogos y gobernanza

### Catalogos criticos

| Artefacto | Estado | Uso operativo |
|---|---|---|
| `DURACION_ESTUDIOS.tsv` | EXISTE | Fuente canonica para matriz SIES y dimension de oferta |
| `control/catalogos/PUENTE_SIES_COMPILADO.tsv` | EXISTE | **Fuente canónica única de cruce SIES por SOURCE_KEY_3** |
| `puente_sies.tsv` | **NO ENCONTRADO (retirado del flujo oficial)** | Eliminado como dependencia operativa; respaldo en `control/backups/puente_sies_eliminado_2026-04-09.tsv` |
| `catalogo_manual.tsv` | **NO ENCONTRADO** | Override manual opcional; si se requiere, debe versionarse en raiz |
| `matriz_desambiguacion_sies_final.tsv` | **NO ENCONTRADO** | No es consumido como archivo canonico en v2 actual |
| `resultados/backup_pre_remediacion/matriz_desambiguacion_sies_final_pre_remediacion.tsv` | EXISTE (legacy) | Evidencia historica, no canonica |
| `gobernanza_nac.tsv` | EXISTE | Gobernanza `NAC` |
| `gobernanza_pais_est_sec.tsv` | EXISTE | Gobernanza `PAIS_EST_SEC` |
| `gobernanza_sede.tsv` | EXISTE | Gobernanza `COD_SED` |
| `gobernanza_for_ing_act.tsv` | EXISTE | Gobernanza documental `FOR_ING_ACT` |
| `gobernanza_columnas_mu/_INDICE_COLUMNAS.tsv` | EXISTE | Indice de gobernanza de 32 columnas |

### Regla operativa de bloqueo

Si aparece combinacion nueva sin resolucion trazable (por ejemplo `AMBIGUO_SIES`, `SIN_MATCH_SIES`, `PENDIENTE_GOBERNANZA` o exclusion por falta de match DA), la corrida **no se considera cerrada para entrega**.

Adicionalmente, para operación oficial MU 2026:

- Si existe `SIN_MATCH_SIES` en no-diplomados, el pipeline marca bloqueo y falla ejecución.
- Se exporta evidencia de bloqueo en `resultados/sies_combinaciones_nuevas_bloqueantes.tsv`.

Accion obligatoria:

1. Actualizar `DURACION_ESTUDIOS.tsv` (canónico operativo).
2. Regenerar `control/catalogos/PUENTE_SIES_COMPILADO.tsv`.
3. Re-ejecutar flujo oficial.
4. Re-validar con `qa_checks.py` y `auditoria_maestra.py`.

## 7) QA y validacion

### Validacion oficial

```bash
cd /ruta/al/repo/avance_curricular
make validate-oficial
```

Equivalente (mismo orden del script oficial):

```bash
python3 qa_checks.py --output-dir resultados --fase6-control-dir control
python3 scripts/auditoria_maestra.py --solo-validar --output-dir resultados
```

### Auditoria maestra

Solo validar outputs existentes:

```bash
python3 scripts/auditoria_maestra.py --solo-validar --output-dir resultados
```

Ejecutar pipeline + validar:

```bash
python3 scripts/auditoria_maestra.py --ejecutar-pipeline --output-dir resultados --input "/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx"
```

### Invariantes MU auditadas

- CSV final sin header y con `;`.
- 32 columnas exactas.
- `FOR_ING_ACT = 1` en CSV final.
- Coherencia `ASI_APR_ANT <= ASI_INS_ANT` y `ASI_APR_HIS <= ASI_INS_HIS`.
- Rangos de `PROM_*` en `0` o `100..700`.
- Regla bloqueante: `VIG = 0` implica `PROM_PRI_SEM = 0`, `PROM_SEG_SEM = 0`, `ASI_INS_HIS = 0`, `ASI_APR_HIS = 0`.

## 8) Fuentes canonicas y duplicados

### Fuentes canonicas propuestas

- Ejecucion oficial: `codigo_gobernanza_v2.py` via `make run-oficial`.
- Validacion oficial: `qa_checks.py` + `scripts/auditoria_maestra.py`.
- Catalogo base SIES: `DURACION_ESTUDIOS.tsv` (raiz).
- Catálogo canónico de cruce SIES: `control/catalogos/PUENTE_SIES_COMPILADO.tsv`.
- Overrides SIES: **no operativos en MU 2026** (flujo oficial compila solo desde `DURACION_ESTUDIOS.tsv`).
- Gobernanza de columnas: `gobernanza_columnas_mu/`.
- Outputs oficiales: `resultados/archivo_listo_para_sies.xlsx` y `resultados/matricula_unificada_2026_pregrado.csv`.

### Duplicados relevantes detectados

#### `DURACION_ESTUDIOS` (mismo proposito)

| Ruta | Tamano (bytes) | Filas (wc -l) | Modificado |
|---|---:|---:|---|
| `DURACION_ESTUDIOS.tsv` | 36720 | 152 | 2026-04-09 06:45:29 |
| `control/backups/DURACION_ESTUDIOS_bak_2026-04-08_20-30-47.tsv` | 38196 | 157 | 2026-04-08 20:30:47 |
| `control/backups/DURACION_ESTUDIOS_backup_pre_gob_codcarpr_2026-04-08_00-27-42.tsv` | 32877 | 140 | 2026-04-08 00:27:42 |
| `control/backups/DURACION_ESTUDIOS_backup_pre_loop_codcli_2026-04-08_00-42-09.tsv` | 32877 | 140 | 2026-04-08 00:42:09 |

Canonico recomendado: `DURACION_ESTUDIOS.tsv` en raiz.

#### `tablero` y `backlog` (control vigente vs backup)

| Ruta | Tamano (bytes) | Filas (wc -l) | Modificado |
|---|---:|---:|---|
| `control/tablero_mu_2026.tsv` | 10514 | 33 | 2026-04-08 19:45:18 |
| `backup_estable_2026/control/tablero_mu_2026.tsv` | 12001 | 33 | 2026-04-03 21:48:51 |
| `control/pendientes/backlog_residual_mu_2026.tsv` | 1 | 1 | 2026-04-08 19:45:23 |
| `backup_estable_2026/control/pendientes/backlog_residual_mu_2026.tsv` | 2090 | 3 | 2026-04-03 21:48:51 |

Canonico recomendado: `control/` vigente. `backup_estable_2026/` debe tratarse como snapshot historico.

### Politica de consolidacion

- Debe existir un solo `DURACION_ESTUDIOS.tsv` operativo en raiz.
- Los backups en `control/backups/` son **NO operativos** (solo evidencia histórica).
- Toda actualizacion de catalogo exige nueva corrida + validacion oficial.

## 9) Troubleshooting

### `FileNotFoundError: No se encontro archivo de entrada`

- Verifica `INPUT_XLSX` y permisos de lectura.
- Ejecuta desde la raiz del repo.

### `AMBIGUO_SIES` o `SIN_MATCH_SIES`

- Revisar hojas de auditoria en `archivo_listo_para_sies.xlsx` (`SIN_MATCH_SIES`, `RESUMEN_EJECUTIVO`).
- Corregir `DURACION_ESTUDIOS.tsv` y recompilar.
- Resolver desde `DURACION_ESTUDIOS.tsv` y recompilar; no usar overrides en el flujo oficial MU 2026.

### `SIN_MATCH_DA` (operativamente `EXCLUIDO_SIN_MATCH_DATOS_ALUMNOS`)

- Revisar hoja `SIN_MATCH_DATOS_ALUMNOS` del workbook.
- Corregir identificacion en DatosAlumnos o ajustar gobernanza correspondiente.

### `catalogo_manual.tsv` NO ENCONTRADO

- Es opcional en v2 (override).
- Si se requiere override manual, crear y versionar `catalogo_manual.tsv` en raiz con columnas esperadas por el pipeline.

## 10) Licencia y notas

- Licencia: [MIT](LICENSE).
- `archive/` contiene material historico y legacy; no forma parte del camino oficial de ejecucion/validacion MU 2026.
- Para operacion diaria, usar solo comandos de la seccion 4 y validaciones de la seccion 7.

---

## Gobernanza operativa del repositorio

La referencia vigente de gobernanza del repositorio se documenta en:

- `docs/GOBERNANZA_REPOSITORIO.md`

### Resumen operativo vigente

- La ruta runtime oficial de outputs es `resultados/`.
- El flujo oficial se ejecuta mediante:
  - `make run-oficial`
  - `make validate-oficial`
  - `make run-and-validate-oficial`
- Los scripts oficiales son:
  - `scripts/run_oficial.sh`
  - `scripts/validate_oficial.sh`
  - `scripts/run_and_validate_oficial.sh`
- Los motores oficiales son:
  - `codigo_gobernanza_v2.py`
  - `qa_checks.py`
  - `scripts/auditoria_maestra.py`
  - `scripts/compile_puente_sies_compilado.py`

### Importante

- `data/resultados/` no debe interpretarse como ruta activa de outputs.
- `core/` no debe interpretarse como fuente runtime oficial mientras no se formalice su migración.
- Los scripts legacy o exploratorios no deben usarse como flujo estándar.

