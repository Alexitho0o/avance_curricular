# Avance Curricular + Matrícula Unificada

Repositorio productivo para generar salidas de:

- `avance` (control y PES de avance curricular)
- `matricula` (archivo final de matrícula unificada con trazabilidad SIES)
- `ambos` (ejecución conjunta)

Este README documenta el flujo oficial de `codigo.py` y sus artefactos de gobernanza.

## Documentación principal

- [DOCUMENTACION_TECNICA.md](/Users/alexi/Documents/GitHub/avance_curricular/DOCUMENTACION_TECNICA.md): arquitectura, contratos, trazabilidad y reglas de validación.
- [README.md](/Users/alexi/Documents/GitHub/avance_curricular/README.md): operación diaria y mapa de artefactos.

## Inventario de artefactos del repositorio

| Archivo | Rol técnico | Uso operativo |
|---|---|---|
| [codigo.py](/Users/alexi/Documents/GitHub/avance_curricular/codigo.py) | pipeline principal (avance + matrícula + validaciones) | ejecución productiva |
| [catalogo_manual.tsv](/Users/alexi/Documents/GitHub/avance_curricular/catalogo_manual.tsv) | catálogo de traza por carrera/jornada/nombre | matching manual en proceso matrícula |
| [puente_sies.tsv](/Users/alexi/Documents/GitHub/avance_curricular/puente_sies.tsv) | puente de negocio hacia `CODIGO_CARRERA_SIES` | asignación SIES y diagnóstico |
| `matriz_desambiguacion_sies*.tsv` | matriz de resolución de ambiguos `(CODCARPR,JORNADA,VERSION)` | desambiguación en fase operativa SIES |
| [qa_checks.py](/Users/alexi/Documents/GitHub/avance_curricular/qa_checks.py) | chequeos rápidos de contratos y reportes | control posterior a ejecución |
| [REVIEW.md](/Users/alexi/Documents/GitHub/avance_curricular/REVIEW.md) | revisión técnica histórica (contexto Colab) | referencia, no runtime |
| [FASE1_RESUMEN.txt](/Users/alexi/Documents/GitHub/avance_curricular/FASE1_RESUMEN.txt) | bitácora Fase 1 inicial | historial |
| [FASE1_REVISADA_RESUMEN.txt](/Users/alexi/Documents/GitHub/avance_curricular/FASE1_REVISADA_RESUMEN.txt) | resumen Fase 1 revisada | historial |
| [FASE1_REVISADA_COMPLETADA.txt](/Users/alexi/Documents/GitHub/avance_curricular/FASE1_REVISADA_COMPLETADA.txt) | cierre detallado Fase 1 revisada | historial |
| [FASE2_RESUMEN.txt](/Users/alexi/Documents/GitHub/avance_curricular/FASE2_RESUMEN.txt) | bitácora Fase 2 inicial | historial |
| [FASE2_REVISADA_COMPLETADA.txt](/Users/alexi/Documents/GitHub/avance_curricular/FASE2_REVISADA_COMPLETADA.txt) | cierre Fase 2 revisada | historial |
| [FASE3_COMPLETADA.txt](/Users/alexi/Documents/GitHub/avance_curricular/FASE3_COMPLETADA.txt) | cierre Fase 3 y reportes | historial/auditoría |

## Qué documenta cada fase

- Fase 1 (`FASE1_*`): base de desambiguación, primeras coberturas y problemas detectados.
- Fase 2 (`FASE2_*`): expansión de matriz, mejoras de cobertura jornada/versión y consolidación operativa.
- Fase 3 (`FASE3_COMPLETADA.txt`): resolución operativa de ambiguos, métricas de cierre y evidencia de exportación.

Estos archivos son bitácoras de evolución y auditoría. La fuente de verdad de ejecución actual es `codigo.py` más los artefactos TSV vigentes.

## Catálogos y reglas de gobernanza

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
cd /Users/alexi/Documents/GitHub/avance_curricular
python3 -m venv ../.venv
../.venv/bin/python -m pip install -r requirements.txt
```

## Entrada principal

Excel operativo (ejemplo real):

- `/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx`

## Comandos de ejecución (oficiales)

## Comando único (instalar + ejecutar ambos)

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular && python3 -m venv ../.venv && ../.venv/bin/python -m pip install -r requirements.txt && ../.venv/bin/python codigo.py --input "/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx" --output-dir resultados --proceso ambos --catalogo-manual-tsv "/Users/alexi/Documents/GitHub/avance_curricular/catalogo_manual.tsv" --puente-sies-tsv "/Users/alexi/Documents/GitHub/avance_curricular/puente_sies.tsv"
```

## Solo avance

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular
../.venv/bin/python codigo.py --input "/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx" --output-dir resultados --proceso avance
```

## Solo matrícula

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular
../.venv/bin/python codigo.py --input "/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx" --output-dir resultados --proceso matricula
```

## Ambos procesos

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular
../.venv/bin/python codigo.py --input "/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx" --output-dir resultados --proceso ambos
```

## Catálogos explícitos (recomendado)

```bash
../.venv/bin/python codigo.py --input "/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx" --output-dir resultados --proceso matricula --catalogo-manual-tsv "/Users/alexi/Documents/GitHub/avance_curricular/catalogo_manual.tsv" --puente-sies-tsv "/Users/alexi/Documents/GitHub/avance_curricular/puente_sies.tsv"
```

## QA y validación posterior

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular
../.venv/bin/python qa_checks.py
```

Qué valida `qa_checks.py`:

- que README no contenga dumps CSV accidentales;
- contrato exacto de columnas en `*_control.csv`;
- coherencia mínima de `reporte_validacion.json` y `reporte_calidad_semantica.json`.

## Salidas principales en `resultados/`

- `carreras_avance_curricular_2025_control.csv`
- `carreras_avance_curricular_2025_pes_ready.csv`
- `matricula_avance_curricular_2025_control.csv`
- `matricula_avance_curricular_2025_pes_ready.csv`
- `matricula_unificada_2026_control.csv`
- `matricula_unificada_2026_oficial.xlsx`
- `archivo_listo_para_sies.xlsx`
- `reporte_validacion.json`
- `reporte_calidad_semantica.json`
- `reporte_procedencia.csv`

## Qué es `REVIEW.md`

`REVIEW.md` es una revisión técnica histórica del script de origen en Colab. No participa en ejecución ni en validación automática del pipeline actual.

## Problemas frecuentes

## `FileNotFoundError: No se encontró archivo de entrada`

La ruta usada no existe. Reemplaza la ruta de ejemplo por un archivo real.

## `zsh: no such file or directory: ./.venv/bin/python`

En este repo la venv está en el directorio padre (`../.venv/bin/python`).

## `MATCH_SIES_AMBIGUO`

No es error de ejecución: indica ambigüedad de mapeo SIES y requiere revisión/heurística según la matriz vigente.

## Licencia

MIT. Ver [LICENSE](LICENSE).
