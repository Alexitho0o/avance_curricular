# Ejecución Oficial MU 2026

- Fecha de congelamiento: 2026-04-01
- Baseline congelada de referencia: `CONDICIONAL`
- Alcance: Matrícula Unificada Pregrado 2026

## Unica forma oficial de ejecutar

Se congela una sola forma oficial de ejecución, portable y orientada a ejecutarse desde la raíz del repo:

```bash
make run-oficial INPUT_XLSX="/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx"
```

Para ejecutar y validar en una sola secuencia desde el mismo entrypoint autoservido:

```bash
make run-and-validate-oficial INPUT_XLSX="/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx"
```

Equivalente subyacente:

```bash
cd /ruta/al/repo/avance_curricular
export INPUT_XLSX="/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx"
export OUTPUT_DIR="resultados"
python3 codigo_gobernanza_v2.py --input "$INPUT_XLSX" --output-dir "$OUTPUT_DIR" --proceso matricula --usar-gobernanza-v2 true
```

## Por que esta es la forma oficial

- Es la ruta que reproduce el flujo regulatorio vigente de MU Pregrado 2026.
- Queda autoservida y versionada dentro del repo vía `Makefile` y `scripts/`.
- Genera exactamente los dos artefactos contractuales vigentes: workbook auditable y CSV regulatorio final.
- Reproduce la corrida de referencia validada el `2026-04-01`.
- Desplaza al runtime histórico archivado en `archive/legacy_runtime/codigo.py` y a `--proceso ambos` a estado legacy/histórico para este caso de uso.

## Prerequisitos

- Ejecutar desde la raíz del repo.
- `python3` disponible en el equipo.
- Dependencias instaladas para `python3` según [requirements.txt](/Users/alexi/Documents/GitHub/avance_curricular/requirements.txt).
- `INPUT_XLSX` debe apuntar a un Excel externo válido; no se congela una ruta personal como única forma de operar.
- Catálogos vigentes disponibles en la raíz del repo:
  - [catalogo_manual.tsv](/Users/alexi/Documents/GitHub/avance_curricular/catalogo_manual.tsv)
  - [puente_sies.tsv](/Users/alexi/Documents/GitHub/avance_curricular/puente_sies.tsv)
  - [gobernanza_nac.tsv](/Users/alexi/Documents/GitHub/avance_curricular/gobernanza_nac.tsv)
  - [gobernanza_pais_est_sec.tsv](/Users/alexi/Documents/GitHub/avance_curricular/gobernanza_pais_est_sec.tsv)
  - [gobernanza_sede.tsv](/Users/alexi/Documents/GitHub/avance_curricular/gobernanza_sede.tsv)
  - [gobernanza_for_ing_act.tsv](/Users/alexi/Documents/GitHub/avance_curricular/gobernanza_for_ing_act.tsv)

## Convención oficial de rutas

- `INPUT_XLSX`: parámetro variable, externo al repo.
- `OUTPUT_DIR`: relativo a la raíz del repo; valor oficial recomendado `resultados`.
- `control/`: relativo a la raíz del repo.

## Artefactos esperados al terminar

- [archivo_listo_para_sies.xlsx](/Users/alexi/Documents/GitHub/avance_curricular/resultados/archivo_listo_para_sies.xlsx)
- [matricula_unificada_2026_pregrado.csv](/Users/alexi/Documents/GitHub/avance_curricular/resultados/matricula_unificada_2026_pregrado.csv)

## Resultado esperado mínimo

- workbook con hoja `ARCHIVO_LISTO_SUBIDA`
- CSV final sin header, con `32` columnas y delimitador `;`
- `FOR_ING_ACT` exportado desde resolución trazable, sin sobreescritura fija a `1`
- distribución final verificable en `resultados/reporte_for_ing_act.json`
- dictamen vigente verificable en `control/gate/gate_final_mu_2026.md`

Las métricas congeladas del baseline `2026-04-01` se preservan en `control/reportes/resultado_corrida_referencia_mu_2026.md` como contraste histórico.

## Salidas que no deben usarse como corrida oficial

- `archive/legacy_runtime/codigo.py --proceso matricula`
- `archive/legacy_runtime/codigo.py --proceso ambos`
- cualquier ejecución que escriba o consuma como artefacto final `matricula_unificada_2026_oficial.xlsx`
