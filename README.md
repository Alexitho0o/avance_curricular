# Avance Curricular + Matrícula Unificada

Repositorio productivo para generar salidas de:

- `avance` (control y PES de avance curricular)
- `matricula` (archivo final de matrícula unificada con trazabilidad SIES)
- `ambos` (ejecución conjunta)

Este README documenta el flujo operativo oficial vigente y referencia el material legacy archivado bajo `archive/`.

## Estado operativo actual

Para **Matrícula Unificada 2026 - Pregrado**, el flujo operativo oficial es:

- `codigo_gobernanza_v2.py` con `--proceso matricula --usar-gobernanza-v2 true`
- invocado con `python3` como intérprete oficial congelado en este equipo

Para este proceso:

- el **artefacto de auditoría** es `archivo_listo_para_sies.xlsx`
- el **artefacto regulatorio de carga** es `matricula_unificada_2026_pregrado.csv`
- el archivo de carga objetivo es **CSV**, **sin encabezado**, con **`;`** como delimitador

El flujo legacy histórico quedó archivado bajo `archive/` y no debe usarse como salida regulatoria final de MU Pregrado 2026.

## Congelamiento oficial MU 2026

La fuente de verdad operativa congelada para ejecución, validación y resultado esperado quedó documentada en:

- [ejecucion_oficial_mu_2026.md](/Users/alexi/Documents/GitHub/avance_curricular/control/reportes/ejecucion_oficial_mu_2026.md)
- [validacion_oficial_mu_2026.md](/Users/alexi/Documents/GitHub/avance_curricular/control/reportes/validacion_oficial_mu_2026.md)
- [resultado_corrida_referencia_mu_2026.md](/Users/alexi/Documents/GitHub/avance_curricular/control/reportes/resultado_corrida_referencia_mu_2026.md)

Para el estado final congelado del proyecto:

- decisión vigente: `CONDICIONAL`
- listo para auditoría: `SI`
- listo para carga: `NO`
- tablero vigente: `27 OK / 5 Pendiente`

## Documentación principal

- [DOCUMENTACION_TECNICA.md](/Users/alexi/Documents/GitHub/avance_curricular/DOCUMENTACION_TECNICA.md): arquitectura, contratos, trazabilidad y reglas de validación.
- [README.md](/Users/alexi/Documents/GitHub/avance_curricular/README.md): operación diaria y mapa de artefactos.

## Inventario de artefactos del repositorio

| Archivo | Rol técnico | Uso operativo |
|---|---|---|
| [codigo_gobernanza_v2.py](/Users/alexi/Documents/GitHub/avance_curricular/codigo_gobernanza_v2.py) | pipeline extendido con gobernanza v2 (flag + catálogos externos) | ejecución controlada v2 |
| [catalogo_manual.tsv](/Users/alexi/Documents/GitHub/avance_curricular/catalogo_manual.tsv) | catálogo de traza por carrera/jornada/nombre | matching manual en proceso matrícula |
| [puente_sies.tsv](/Users/alexi/Documents/GitHub/avance_curricular/puente_sies.tsv) | puente de negocio hacia `CODIGO_CARRERA_SIES` | asignación SIES y diagnóstico |
| [gobernanza_sede.tsv](/Users/alexi/Documents/GitHub/avance_curricular/gobernanza_sede.tsv) | tabla maestra de sede (`SEDE` -> `COD_SED`) | gobernanza v2 de `COD_SED` |
| [gobernanza_nac.tsv](/Users/alexi/Documents/GitHub/avance_curricular/gobernanza_nac.tsv) | tabla maestra de nacionalidad -> código NAC | gobernanza v2 de `NAC` |
| [gobernanza_pais_est_sec.tsv](/Users/alexi/Documents/GitHub/avance_curricular/gobernanza_pais_est_sec.tsv) | tabla maestra localidad escolar -> país | gobernanza v2 de `PAIS_EST_SEC` |
| [gobernanza_niveles.tsv](/Users/alexi/Documents/GitHub/avance_curricular/gobernanza_niveles.tsv) | catálogo maestro `NIVEL_GLOBAL`/`NIVEL_CARRERA` del Manual | gobernanza documental para clasificación académica |
| [gobernanza_for_ing_act.tsv](/Users/alexi/Documents/GitHub/avance_curricular/gobernanza_for_ing_act.tsv) | catálogo formal de `FOR_ING_ACT` (1..11) según Manual 2026 | gobernanza documental de forma de ingreso |
| [generar_gobernanza_columnas_mu.py](/Users/alexi/Documents/GitHub/avance_curricular/generar_gobernanza_columnas_mu.py) | generador de TSV por columna MU (32/32) | trazabilidad columna a columna contra Cuadro N°1 |
| `gobernanza_columnas_mu/*.tsv` | un TSV por cada columna de matrícula pregrado | gobernanza detallada por campo de salida |
| `matriz_desambiguacion_sies*.tsv` | matriz de resolución de ambiguos `(CODCARPR,JORNADA,VERSION)` | desambiguación en fase operativa SIES |
| [qa_checks.py](/Users/alexi/Documents/GitHub/avance_curricular/qa_checks.py) | chequeos rápidos de contratos y reportes | control posterior a ejecución |
| [archive/](/Users/alexi/Documents/GitHub/avance_curricular/archive) | material legacy, bitácoras históricas y resultados archivados | contexto/historial, fuera del camino operativo principal |

## Qué documenta cada fase

- Fase 1, Fase 2 y Fase 3: bitácoras históricas archivadas en `archive/contexto_historico/fases/`.

Estos archivos son bitácoras de evolución y auditoría.

## Catálogos y reglas de gobernanza

### Gobernanza por columna (Cuadro N°1)

Se mantiene un set de **32 TSV (uno por columna de salida MU)** en:

- `gobernanza_columnas_mu/`
- índice: `gobernanza_columnas_mu/_INDICE_COLUMNAS.tsv`

Generación/reconstrucción:

```bash
cd /ruta/al/repo/avance_curricular
python3 generar_gobernanza_columnas_mu.py
```

El generador deja cada columna con:

- definición de manual (`Anexo 7, Cuadro N°1`)
- fuente automática principal/secundaria en el proyecto
- regla implementada en `codigo_gobernanza_v2.py`
- validación aplicada
- fallback operativo
- condición de revisión manual

## 1) `catalogo_manual.tsv`

Columnas esperadas:

- `GRUPO_TRAZA`
- `JORNADA`
- `CODCARPR`
- `NOMBRE_L`
- `ANOINGRESO`

Uso:

- clasificación manual de llave de negocio en el matching de matrícula.

## 2) `puente_sies.tsv`

Columnas esperadas:

- `GRUPO_TRAZA`
- `JORNADA`
- `CODCARPR`
- `NOMBRE_L`
- `CODIGO_CARRERA_SIES`

Uso:

- puente principal para asignación de código SIES y detección de ambiguos.

## 3) Campos críticos del Manual 2026 (Anexo 7)

Referencia: `20260106_36454_Manual_Matrícula_Unificada_2026.pdf` (Cuadro N°1).

- `ASI_INS_ANT` y `ASI_APR_ANT`: rango `0..99` y coherencia `APR <= INS`.
- `PROM_PRI_SEM` y `PROM_SEG_SEM`: `0` o `100..700`.
- `ASI_INS_HIS` y `ASI_APR_HIS`: `0..200` y coherencia `APR <= INS`.
- `NIV_ACA`: obligatorio y `>=1`.
- `SIT_FON_SOL`: catálogo `0/1/2`.
- `SUS_PRE`: rango `0..99`.
- `VIG`: catálogo `0/1/2`.

## Requisitos

- Python 3.9+
- `pandas`
- `numpy`
- `openpyxl`

## Instalación

```bash
cd /ruta/al/repo/avance_curricular
python3 -m pip install -r requirements.txt
```

## Entrada principal

Excel operativo:

- archivo externo al repo, informado vía `INPUT_XLSX`

## Flujo oficial MU Pregrado 2026

El flujo oficial de Matrícula Unificada Pregrado 2026 se ejecuta en `codigo_gobernanza_v2.py`:

Atajo autoservido recomendado desde la raíz del repo:

```bash
make run-oficial INPUT_XLSX="/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx"
```

```bash
cd /ruta/al/repo/avance_curricular
export INPUT_XLSX="/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx"
export OUTPUT_DIR="resultados"
python3 codigo_gobernanza_v2.py --input "$INPUT_XLSX" --output-dir "$OUTPUT_DIR" --proceso matricula --usar-gobernanza-v2 true
```

Este flujo genera dos artefactos distintos:

| Artefacto | Rol | Uso |
|---|---|---|
| `archivo_listo_para_sies.xlsx` | auditoría y trazabilidad | revisión operativa, diagnóstico y exclusiones |
| `matricula_unificada_2026_pregrado.csv` | carga regulatoria final | archivo para carga MU Pregrado 2026 |

Con `--usar-gobernanza-v2 true` se agrega hoja `SIN_MATCH_DATOS_ALUMNOS` en `archivo_listo_para_sies.xlsx` para revisión manual de `CODCLI` no encontrados en `DatosAlumnos`.

Con gobernanza v2, el lookup en `DatosAlumnos` usa prioridad:

1. `CODCLI` contra `CODCLI`
2. fallback `RUT+DV` contra `RUT+DV`

y deja trazabilidad en `ARCHIVO_LISTO_SUBIDA`:

- `DA_MATCH_MODO`
- `NAC_STATUS`
- `PAIS_EST_SEC_STATUS`
- `COD_SED_STATUS`

## Catálogos de gobernanza (opcional por CLI)

Si no informas rutas, se buscan por defecto en la carpeta del repo:

- `gobernanza_nac.tsv`
- `gobernanza_pais_est_sec.tsv`
- `gobernanza_sede.tsv`
- `gobernanza_niveles.tsv` (catálogo de referencia documental; no se consume por CLI en v2 actual)

El comando oficial no necesita rutas absolutas para catálogos, porque estos se resuelven por defecto desde la raíz del repo. Si necesitas forzarlos explícitamente:

```bash
cd /ruta/al/repo/avance_curricular
export INPUT_XLSX="/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx"
export OUTPUT_DIR="resultados"
python3 codigo_gobernanza_v2.py --input "$INPUT_XLSX" --output-dir "$OUTPUT_DIR" --proceso matricula --usar-gobernanza-v2 true --gob-nac-tsv "gobernanza_nac.tsv" --gob-pais-est-sec-tsv "gobernanza_pais_est_sec.tsv" --gob-sede-tsv "gobernanza_sede.tsv"
```

## QA y validación posterior

Atajo autoservido recomendado desde la raíz del repo:

```bash
make validate-oficial
```

```bash
cd /ruta/al/repo/avance_curricular
export OUTPUT_DIR="resultados"
python3 qa_checks.py --output-dir "$OUTPUT_DIR" --fase6-control-dir "control"
```

Para ejecutar y validar en una sola secuencia:

```bash
make run-and-validate-oficial INPUT_XLSX="/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx"
```

Ayuda mínima de uso:

```bash
make help
```

Qué valida `qa_checks.py`:

- que README no contenga dumps CSV accidentales;
- estructura física del `matricula_unificada_2026_pregrado.csv`;
- invariantes globales vigentes;
- y, con `--fase6-control-dir`, refresca el gate final y el backlog residual en `control/`.

## Salidas principales en `resultados/`

- `archivo_listo_para_sies.xlsx`
- `matricula_unificada_2026_pregrado.csv`

## Material legacy archivado

El material histórico, los comandos legacy y las bitácoras de remediación ya no viven en el camino operativo principal. Quedaron agrupados bajo [archive/](/Users/alexi/Documents/GitHub/avance_curricular/archive) para conservar trazabilidad sin inducir a ejecutar el flujo equivocado.

## Problemas frecuentes

## `FileNotFoundError: No se encontró archivo de entrada`

La ruta usada no existe. Reemplaza la ruta de ejemplo por un archivo real.

## `zsh: no such file or directory: ./.venv/bin/python`

En este repo la venv está en el directorio padre (`../.venv/bin/python`).

## `MATCH_SIES_AMBIGUO`

No es error de ejecución: indica ambigüedad de mapeo SIES y requiere revisión/heurística según la matriz vigente.

## Licencia

MIT. Ver [LICENSE](LICENSE).
