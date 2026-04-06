# Auditoría de Catálogos SIES MU 2026

Fecha: 2026-04-09
Repositorio: `avance_curricular`

## 1) Inventario DURACION_ESTUDIOS* (ruta, filas, fecha, hash)

| Ruta | Filas | Modificado | SHA256 |
|---|---:|---|---|
| `DURACION_ESTUDIOS.tsv` | 152 | 2026-04-09 06:45:29 | `2bdee14379d0687afd1d247edbf35c908e7ddb8a64587b5b5c8f2aa4ddec5fc7` |
| `control/backups/DURACION_ESTUDIOS_backup_pre_gob_codcarpr_2026-04-08_00-27-42.tsv` | 140 | 2026-04-08 00:27:42 | `d3f85f8d9c7bcfefec6e0be05737f5b5643d5caba9a8cebc52a61d5145c0c43b` |
| `control/backups/DURACION_ESTUDIOS_backup_pre_loop_codcli_2026-04-08_00-42-09.tsv` | 140 | 2026-04-08 00:42:09 | `d3f85f8d9c7bcfefec6e0be05737f5b5643d5caba9a8cebc52a61d5145c0c43b` |
| `control/backups/DURACION_ESTUDIOS_bak_2026-04-08_20-30-47.tsv` | 157 | 2026-04-08 20:30:47 | `e6cf71f50124f2734e60fcf1edaf92acacbe387f770e24655603066b0cff4e62` |

Declaración canónica: **`DURACION_ESTUDIOS.tsv` en raíz es el único operativo**.  
Backups movidos a `control/backups/` y marcados como NO operativos.

Verificación runtime sin `.bak`:

`SIN_REFERENCIAS_RUNTIME_A_BAK`

## 2) Comparación diferencial `DURACION_ESTUDIOS.tsv` vs `.bak`

| Métrica | DURACION_ESTUDIOS.tsv | DURACION_ESTUDIOS_bak_2026-04-08_20-30-47.tsv |
|---|---:|---:|
| Filas totales | 151 | 156 |
| `CODIGO_UNICO` únicos | 137 | 139 |
| `% UNICO` (`CODCARPR_RESOLUCION_ESTADO`) | 43.71% | 41.67% |
| `% AMBIGUO` (`CODCARPR_RESOLUCION_ESTADO`) | 28.48% | 31.41% |
| Conteo UNICO | 66 | 65 |
| Conteo AMBIGUO | 43 | 49 |

### Carrera crítica 46 (CICIB/ICIB)

- Estado en canónico `.tsv`: {'UNICO': 5}
- Estado en `.bak`: {'AMBIGUO': 6, 'UNICO': 4}
- Evidencia de degradación: el `.bak` incrementa AMBIGUO en C46 y agrega códigos no presentes en canónico.

| CODIGO_UNICO C46 | ESTADO_TSV | ESTADO_BAK |
|---|---|---|
| `I162S2C46J1V1` | `UNICO` | `AMBIGUO` |
| `I162S2C46J2V1` | `UNICO` | `AMBIGUO` |
| `I162S2C46J2V2` | `nan` | `AMBIGUO` |
| `I162S2C46J2V3` | `UNICO` | `AMBIGUO` |
| `I162S2C46J4V1` | `UNICO` | `AMBIGUO` |
| `I162S2C46J4V2` | `nan` | `UNICO` |
| `I162S2C46J4V3` | `UNICO` | `UNICO` |

Dictamen Fase 2: **CANÓNICO = `DURACION_ESTUDIOS.tsv`**. `.bak` queda archivado.

## 3) Compilación catálogo único runtime (`PUENTE_SIES_COMPILADO.tsv`)

- Script: `scripts/compile_puente_sies_compilado.py`
- Output: `control/catalogos/PUENTE_SIES_COMPILADO.tsv`
- Runtime único de cruce SIES central confirmado en pipeline.

| Métrica compilado | Valor |
|---|---:|
| `base_rows` | 251 |
| `override_rows` | 2 |
| `total_source_keys` | 157 |
| `source_keys_unicos` | 87 |
| `source_keys_ambiguos` | 70 |
| `source_keys_bloqueantes` | 70 |
| `source_keys_pendiente_gobernanza` | 21 |
| `cobertura_llaves_unicas_pct` | 55.41 |

Validaciones bloqueantes del compilado:

- Unicidad `SOURCE_KEY_3`: PASS (duplicados=0).
- Llaves ambiguas observadas en universo real quedan marcadas como `PENDIENTE_GOBERNANZA` (columna `GOBERNANZA_STATUS`).

## 4) Limpieza de `puente_sies.tsv` (override mínimo)

- Filas evaluadas: 5
- Filas necesarias: 2
- Filas no necesarias movidas a backup: 3

Filas **necesarias** mantenidas en `puente_sies.tsv`:

| SOURCE_KEY_3 | CODIGO_CARRERA_SIES | CAUSA |
|---|---|---|
| `V|CICIB|CONTINUIDAD INGENIERIA CIBERSEGURIDAD` | `I162S2C46J2V3` | `BLOQUEANTE` |
| `O|CICIB|CONTINUIDAD INGENIERIA CIBERSEGURIDAD` | `I162S2C46J4V1` | `BLOQUEANTE` |

Filas no necesarias archivadas en `control/backups/puente_sies_no_usado_2026-04-09.tsv`:

| SOURCE_KEY_3 | CODIGO_CARRERA_SIES | CAUSA |
|---|---|---|
| `D|ICIB|INGENIERIA EN CIBERSEGURIDAD` | `I162S2C46J1V1` | `NO_OBSERVADA` |
| `V|ICIB|INGENIERIA EN CIBERSEGURIDAD` | `I162S2C46J2V1` | `NO_OBSERVADA` |
| `O|ICIB|INGENIERIA EN CIBERSEGURIDAD` | `I162S2C46J4V3` | `NO_OBSERVADA` |

## 5) Alineación documental (README + cruces_proyecto.tsv)

- README referencia explícita `cruces_proyecto.tsv`: **SI**
- Entrada de cruce central SIES (L2447) en `cruces_proyecto.tsv`: `bridge_exact (control/catalogos/PUENTE_SIES_COMPILADO.tsv)`
- Resultado: trazabilidad del origen compilado actualizada (sin dependencia base de `puente_sies.tsv`).

## 6) Ejecución y QA

- `make compile-sies` ejecutado OK.
- `make validate-oficial OUTPUT_DIR=resultados` ejecutado OK (`qa_checks` + `auditoria_maestra`).
- `make run-and-validate-oficial INPUT_XLSX="/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx" OUTPUT_DIR="resultados/run_and_validate_oficial_2026-04-09_catalogos_minimo"` ejecutado con bloqueo esperado por combinación nueva.

### Llaves nuevas bloqueantes detectadas

Archivo evidencia principal: `resultados/run_and_validate_oficial_2026-04-09_catalogos_minimo/sies_combinaciones_nuevas_bloqueantes.tsv`

| SOURCE_KEY_3 | CODCARPR_NORM | NOMBRE_CARRERA_FUENTE | JORNADA_FUENTE | DIAG |
|---|---|---|---|---|
| `V|CICRE|CONTINUIDAD INGENIERIA CONECTIVIDAD Y REDES` | `CICRE` | `CONTINUIDAD INGENIERIA CONECTIVIDAD Y REDES` | `V` | `PROBABLE_PROBLEMA_JORNADA_SIES` |

Archivos bloqueantes encontrados en `resultados/*/sies_combinaciones_nuevas_bloqueantes.tsv`:

| Archivo | # Llaves |
|---|---:|
| `resultados/run_and_validate_oficial_2026-04-09_catalogos/sies_combinaciones_nuevas_bloqueantes.tsv` | 3 |
| `resultados/run_and_validate_oficial_2026-04-09_catalogos_minimo/sies_combinaciones_nuevas_bloqueantes.tsv` | 1 |
| `resultados/run_oficial_compilado_2026-04-09/sies_combinaciones_nuevas_bloqueantes.tsv` | 1 |

## Dictamen final

**NO LISTO**

Motivo bloqueante vigente: existe al menos una combinación nueva no catalogada en corrida oficial mínima (`V|CICRE|CONTINUIDAD INGENIERIA CONECTIVIDAD Y REDES`).
Se mantiene política correcta de bloqueo + evidencia exportada, por lo que la gobernanza está operativa pero la entrega queda detenida hasta catalogar la llave.