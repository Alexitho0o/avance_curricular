# Artefactos versionables Personal Academico 2026

Fecha/hora: 2026-06-12T15:41:00

Este documento clasifica artefactos para un cierre Git controlado. No ejecuta staging ni commit.

## Grupo 1 - Versionar siempre
Archivos fuente, scripts, documentacion, reportes y bitacoras:

- `personal_academico_2026/README.md`
- `personal_academico_2026/INSTRUCCIONES_PERSONAL_ACADEMICO_2026.md`
- `personal_academico_2026/docs/*.md`
- `personal_academico_2026/bitacoras/**/*.md`
- `personal_academico_2026/scripts/*.py`
- `personal_academico_2026/catalogos/*`
- `personal_academico_2026/tests/**/*.csv`
- `personal_academico_2026/tests/**/*.py`
- `personal_academico_2026/insumos/*.csv`
- `personal_academico_2026/insumos/*.txt`
- `personal_academico_2026/insumos/historicos/*`, si existen ahi los historicos.

## Grupo 2 - Versionar con git add -f por trazabilidad del cierre
Aunque `.gitignore` pueda ignorarlos, estos artefactos respaldan la carga y el analisis:

- `personal_academico_2026/resultados/Personal_Academico_2026_RESPALDO_CARGA_Y_KPI.xlsx`
- `personal_academico_2026/resultados/VALIDACION_EXCEL_RESPALDO_CARGA_Y_KPI.txt`
- `personal_academico_2026/resultados/personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO.csv`
- `personal_academico_2026/auditorias/**/*.csv`
- `personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv`
- `personal_academico_2026/data/base_general/candidatos_exportacion/*.tsv`
- `personal_academico_2026/control_correcciones/*.tsv`

## Grupo 3 - No versionar salvo decision explicita
Backups, copias temporales o archivos duplicados:

- `personal_academico_2026/resultados/backups/*`
- `/Users/alexi/Desktop/*`
- `/Users/alexi/Desktop/backups_personal_academico_2026/*`
- Archivos temporales de Excel como `~$*.xlsx`
- Cualquier copia duplicada no reproducible.

## Comando sugerido de revision

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular
git status --short
git status --ignored --short personal_academico_2026
```

## Comando sugerido para staging controlado

No ejecutar automaticamente; revisar antes.

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular
git add \
personal_academico_2026/scripts/generar_respaldo_carga_kpi_personal_academico_2026.py \
personal_academico_2026/docs/ \
personal_academico_2026/bitacoras/ \
personal_academico_2026/catalogos/ \
personal_academico_2026/README.md \
personal_academico_2026/INSTRUCCIONES_PERSONAL_ACADEMICO_2026.md
git add -f \
personal_academico_2026/resultados/Personal_Academico_2026_RESPALDO_CARGA_Y_KPI.xlsx \
personal_academico_2026/resultados/VALIDACION_EXCEL_RESPALDO_CARGA_Y_KPI.txt \
personal_academico_2026/resultados/personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO.csv \
personal_academico_2026/auditorias/ \
personal_academico_2026/data/base_general/ \
personal_academico_2026/control_correcciones/
```

## Excluir backups del staging si se agregan por error

```bash
git restore --staged personal_academico_2026/resultados/backups/ 2>/dev/null || true
```

## Propuesta de commit

No ejecutar todavia.

```bash
git commit -m "Cierra carga PES Personal Académico 2026 con respaldo KPI e histórico SIES"
```
