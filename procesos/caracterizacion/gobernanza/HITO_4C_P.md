# HITO 4C-P — Separación definitiva entre Caracterización, Histórico SIES y Análisis Longitudinal

Fecha de cierre: 2026-07-15
Rama: `main`
HEAD inicial y final: `2c35809bf3fc7e2ad05c9dd159881434f04bbe32`

## Diagnóstico técnico

La línea base del 4B-P tenía tres dominios todavía mezclados:

1. `BLOQUE 10.quater` trataba SIES como fuente dinámica de cruce y conservaba lógica/hojas de comparación individual.
2. El pipeline normal importaba y ejecutaba retención longitudinal desde `BLOQUE 7`.
3. `BLOQUE 10.bis` exportaba continuidad y retención anual dentro del libro normal de Caracterización.

Durante la regresión 4C-P también apareció un defecto puntual en Sectorizado AC: el universo vigente se pasaba al subprocess como pickle y `pd.read_pickle()` fallaba por incompatibilidad de serialización. Se corrigió sin cambiar la lógica sectorizada: el snapshot oficial ahora se entrega como Excel tabular estable.

## Arquitectura antes/después

Antes:

```text
Caracterización
  ├─ recalculaba/consumía SIES como cruce operativo
  ├─ podía intentar lógica individual contra SIES
  ├─ calculaba retención en Bloque 7
  └─ exportaba continuidad/retención en Bloque 10.bis
```

Después:

```text
CARACTERIZACION
  ↓ usa
SIES VERSIONADA
  ↓ NO RECONSTRUIDA
  ↓ NO DINÁMICA

LONGITUDINAL
  → caracterizacion_longitudinal.py
  → opt-in: CARACTERIZACION_EJECUTAR_LONGITUDINAL=1
```

## Solución implementada

- SIES quedó materializado como repositorio histórico versionado:
  - `gobernanza/sies/HISTORICO_SIES_MANIFEST.json`
  - `gobernanza/sies/HISTORICO_SIES_AGREGADOS.csv`
- Versión utilizada: `SIES_2007_2025_v1`.
- El pipeline normal solo lee el manifest y los agregados SIES; no reconstruye la fuente cruda.
- `BLOQUE 10.quater` ahora genera salidas agregadas por año/programa/jornada/sede/modalidad/tipo de plan.
- Se eliminaron del 10.quater las hojas de cruce individual y auditorías de identificación individual.
- Retención longitudinal quedó desacoplada:
  - punto de entrada: `caracterizacion_longitudinal.py`;
  - opt-in: `CARACTERIZACION_EJECUTAR_LONGITUDINAL=1`;
  - por defecto: `NO_EJECUTADO_EN_CARACTERIZACION`.
- `BLOQUE 10.bis` conserva la base académica necesaria para Caracterización/Sectorizado AC, pero no exporta hojas normales de continuidad/retención cuando el opt-in está apagado.
- El manifest de ejecución ahora registra:
  - arquitectura SIES;
  - versión SIES utilizada;
  - `reconstruida_en_pipeline=false`;
  - `dinamica=false`;
  - nivel agregado.
- Sectorizado AC dejó de recibir `universo_vigente.pkl`; ahora recibe `universo_vigente.xlsx`.

## Resultados de regresión final

Ruta:

`/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/0_caracterizacion/2026-07-15/2026_P2_172021_HITO4C_OK`

Manifest:

- estado: `OK`
- código salida: `0`
- pipeline completo: `SI`
- último bloque: `BLOQUE 12`
- modo corte: `NINGUNO`
- SIES versión utilizada: `SIES_2007_2025_v1`

Conteos principales:

- vigentes oficiales: 627
- respuesta completa: 285
- respuesta incompleta: 2
- no respuesta: 340
- Sectorizado AC: 627 filas, 0 duplicados CODCLI
- AC con datos: 506
- AC sin datos: 121
- SIES fuente: 20.961 registros
- SIES agregado: 406 filas programa-año

Validaciones post-run:

- `FutureWarning`: no detectado
- `Traceback`: no detectado
- `[SECTORIZADO_AC] [ERROR]`: no detectado
- `[B10quater][ERROR]`: no detectado
- hojas SIES prohibidas ausentes: `CRUCE_SIES_PERSONA_ANIO`, `AUDITORIA_RUT_COMUNES`, `SIES_SIN_MATCH`
- hojas longitudinales normales ausentes en B10.bis: `CONTINUIDAD_RUT`, `KPI_CONTINUIDAD_RUT`, `RETENCION_ANUAL_*`
- hoja de control presente: `LONGITUDINAL_NO_EJECUTADO`

## Pruebas ejecutadas

- `python3 -m py_compile ...`
- `PYTHONPATH="../avance_curricular/.venv/lib/python3.13/site-packages" ../clima_laboral_2026/.venv/bin/python -m pytest -q`
  - resultado: 180 passed, 96 subtests passed
- `python3 scripts/auditar_hito_4c_p.py --json-out gobernanza/HITO_4C_P_auditoria.json`
  - resultado: OK
- `bash -n` sobre scripts `.sh`
  - resultado: OK
- `git diff --check`
  - resultado: OK

## Archivos modificados o nuevos

- `analisis_sectorizado_encuesta_ac.py`
- `caracterizacion.py`
- `caracterizacion_runtime.py`
- `caracterizacion_retencion.py`
- `caracterizacion_longitudinal.py`
- `caracterizacion_sies_historico.py`
- `gobernanza/sies/HISTORICO_SIES_MANIFEST.json`
- `gobernanza/sies/HISTORICO_SIES_AGREGADOS.csv`
- `scripts/auditar_hito_4c_p.py`
- `tests/test_hito4c_separacion_dominios.py`
- `tests/test_caracterizacion_runtime.py`
- `gobernanza/HITO_4C_P_auditoria.json`

## Hashes SHA-256 principales

- `analisis_sectorizado_encuesta_ac.py`: `a23636794a4fb3000dc18c16c7d8de067eb3fcd5956e1a4829a9135bd6ee1c59`
- `caracterizacion.py`: `16c2be56c7029b230ea91d7b280ce45e5156d32dac38f2536c77535eea38af28`
- `caracterizacion_runtime.py`: `2032b3124323a0908b4841b768760ae29d8b4d90b0759089a6c74d45980d9de6`
- `caracterizacion_sies_historico.py`: `1aa524f4f1f68a6c0cac37e5ca3ef7311367b068661f4f4548bb9f26d97bdeb4`
- `gobernanza/sies/HISTORICO_SIES_MANIFEST.json`: `241e3c688e519725ef2893ba5ba71f3a7798c8e427b7bd6bf438fc3485ab31f6`
- `gobernanza/sies/HISTORICO_SIES_AGREGADOS.csv`: `ce150371224daadbef430041b4a60d34427a3158f6ccd9fe9c5d2df17b31a848`
- `scripts/auditar_hito_4c_p.py`: `38a577673f6ee4beb0dad25ae9dcdb9f9201e8fb033a32508a0293229d908613`

## Limitaciones y compatibilidad

- La Caracterización normal sigue usando antecedentes académicos internos cuando son necesarios para AC/Sectorizado, pero ya no exporta continuidad ni retención como productos longitudinales normales.
- Si se requiere retención, continuidad o seguimiento, debe ejecutarse explícitamente por el módulo longitudinal o con `CARACTERIZACION_EJECUTAR_LONGITUDINAL=1`.
- El histórico SIES solo debe actualizarse mediante acción explícita cuando exista nueva versión oficial.
- No se ejecutó `git add`, `commit`, `push`, `pull`, `merge`, `rebase`, `reset` ni `clean`.

## Dictamen

HITO 4C-P: RESUELTO
