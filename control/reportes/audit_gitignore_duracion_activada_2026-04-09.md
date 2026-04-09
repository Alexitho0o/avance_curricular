# Auditoria Gitignore DURACION activada (MU 2026)

Fecha: 2026-04-09  
Repositorio: `avance_curricular`

## 1) Objetivo

Activar versionado de `DURACION_ESTUDIOS.tsv` sin permitir tracking de TSV generados en `resultados/` ni backups en `control/backups/`, preservando validación MU 2026 en verde.

## 2) Fragmento final de `.gitignore` (ultimas lineas)

```gitignore
# Ignore Python cache and environment files
__pycache__/
*.py[cod]
*.egg-info/

# Ignore large data files
*.xlsx
*.xls
*.csv
*.tsv
resultados/**/*.tsv
control/backups/**/*.tsv
!DURACION_ESTUDIOS.tsv
!catalogo_manual.tsv
!gobernanza_nac.tsv
!gobernanza_pais_est_sec.tsv
!gobernanza_sede.tsv
!gobernanza_niveles.tsv
!gobernanza_for_ing_act.tsv
!gobernanza_columnas_mu/
!gobernanza_columnas_mu/*.tsv
!control/tablero_mu_2026.tsv
!control/reportes/reporte_fech_nac.tsv
!control/reportes/reporte_nac_pais_sec.tsv
!control/reportes/sies_pendientes.tsv
!control/reportes/resumen_historico_mu_2026.csv
!control/reportes/inventario_limpieza_mu_2026.tsv
!control/pendientes/backlog_residual_mu_2026.tsv
!archive/
!archive/**/
!archive/**/*.md
!archive/**/*.json
!archive/**/*.txt
!archive/**/*.log
!archive/**/*.py
!archive/**/*.csv
!archive/**/*.tsv
!archive/**/*.xlsx
*.parquet
*.zip
*.tar.gz
*.pkl
*.joblib

# Track matrix files
!matriz_desambiguacion_sies_final.tsv

# General OS files
.DS_Store
```

## 3) Pruebas de ignore

### 3.1 `git check-ignore -v DURACION_ESTUDIOS.tsv`

```text
(sin salida)
EXIT_CHECK_IGNORE_V:1
```

Resultado: `DURACION_ESTUDIOS.tsv` **no está ignorado**.

### 3.2 Confirmación de reglas de bloqueo para TSV no canónicos

```text
.gitignore:11:resultados/**/*.tsv  resultados/__prueba_ignore__.tsv
EXIT_RES_TEST:0

.gitignore:12:control/backups/**/*.tsv  control/backups/__prueba_ignore__.tsv
EXIT_BAK_TEST:0
```

Resultado: TSV en `resultados/` y `control/backups/` **se mantienen ignorados**.

## 4) Activación en git (tracking)

### 4.1 Estado en staging antes de commit

```text
M  .gitignore
A  DURACION_ESTUDIOS.tsv
D  control/backups/puente_sies_eliminado_2026-04-09.tsv
A  control/reportes/huella_DURACION_ESTUDIOS.tsv.txt
```

### 4.2 Commit aplicado

```text
commit: b78fdb0
mensaje: MU2026: activar versionado de DURACION_ESTUDIOS.tsv (no ignorado) + huella
```

## 5) Huella de auditoría

Archivo: `control/reportes/huella_DURACION_ESTUDIOS.tsv.txt`

```text
$ wc -l DURACION_ESTUDIOS.tsv
155 DURACION_ESTUDIOS.tsv

$ sha256sum DURACION_ESTUDIOS.tsv
701025451acf2f84078cf185d6ae0be0d8483d37e3b3e9483f70070397aebc6e  DURACION_ESTUDIOS.tsv
```

## 6) Validación operativa MU 2026

Comandos ejecutados:

```bash
make compile-sies
make validate-oficial OUTPUT_DIR=resultados
```

Resultado `make compile-sies`: **OK**

- `override_rows = 0`
- `total_source_keys = 161`
- `source_keys_unicos = 91`
- `source_keys_ambiguos = 70`
- Evidencia: `control/reportes/reporte_compilacion_puente_sies.json`

Resultado `make validate-oficial OUTPUT_DIR=resultados`: **OK**

- `qa_checks_ok`
- `resultados/auditoria_maestra.md`: `Dictamen: LISTO PARA ENTREGA`

## 7) Salida de `git status` (post-validación)

```text
 M resultados/auditoria_maestra.md
```

Nota: este cambio proviene de la ejecución de validación oficial (`auditoria_maestra.py`).

## Dictamen final

**LISTO**

`DURACION_ESTUDIOS.tsv` quedó activado para versionado y auditado, manteniendo ignorados los TSV de `resultados/` y `control/backups/`, sin romper el flujo MU 2026 ni el contrato MU32.
