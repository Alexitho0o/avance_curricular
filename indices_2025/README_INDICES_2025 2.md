# INDICES 2025

Subproyecto aislado para diagnosticar y preparar validadores futuros a partir del
Manual INDICES 2025. Esta carpeta no modifica flujos existentes de Matrícula
Unificada, SIES, avance curricular ni artefactos ya consolidados.

## Objetivo

Construir una base técnica inicial para INDICES 2025, comenzando por la FASE 0:
diagnóstico estructural del manual oficial, detección de secciones, cargas CSV,
tablas, reglas explícitas y riesgos técnicos para fases posteriores.

## Fuente oficial utilizada

- Manual original localizado en Descargas:
  `/Users/alexi/Downloads/Manual_INDICES_2025.txt`
- Copia usada dentro del repositorio:
  `indices_2025/docs/Manual_INDICES_2025.txt`

El archivo original solo fue copiado. No fue movido ni modificado.

## Estructura de carpetas

```text
indices_2025/
├── docs/
├── config/
├── scripts/
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── resultados/
│   ├── reportes_validacion/
│   ├── diccionarios/
│   └── logs/
└── README_INDICES_2025.md
```

## Cómo ejecutar FASE 0

Desde la raíz del repositorio:

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular
python3 indices_2025/scripts/00_diagnostico_manual_indices.py
```

El script lee exclusivamente:

```text
indices_2025/docs/Manual_INDICES_2025.txt
```

## Archivos producidos

- `indices_2025/resultados/reportes_validacion/FASE0_DIAGNOSTICO_MANUAL_INDICES_2025.md`
- `indices_2025/resultados/diccionarios/fase0_indice_secciones_manual.json`
- `indices_2025/resultados/diccionarios/fase0_reglas_detectadas_manual.json`
- `indices_2025/resultados/logs/fase0_diagnostico_manual_indices.log`

## Qué NO modifica

- No modifica archivos fuera de `indices_2025/`.
- No altera flujos de Matrícula Unificada.
- No altera flujos SIES.
- No altera scripts ni resultados existentes de avance curricular.
- No crea commits.
- No usa internet ni conocimiento externo.

## Próxima fase sugerida

FASE 1 — Construcción del diccionario técnico programable INDICES 2025,
comenzando por el CSV de Evolución de Carreras, detectado como carga estructurada
prioritaria en el manual.

## FASE 1 — Diccionario técnico CSV Evolución de Carreras

Objetivo: transformar la Tabla 25 del manual, correspondiente al CSV Evolución
de Carreras, en un diccionario técnico preliminar y auditable para preparar
validadores posteriores.

Script generado:

```text
indices_2025/scripts/01_diccionario_evolucion_carreras.py
```

Cómo ejecutar:

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular
python3 indices_2025/scripts/01_diccionario_evolucion_carreras.py
```

Archivos de salida:

- `indices_2025/resultados/diccionarios/diccionario_evolucion_carreras.csv`
- `indices_2025/resultados/diccionarios/diccionario_evolucion_carreras.xlsx`
- `indices_2025/resultados/diccionarios/diccionario_evolucion_carreras.json`
- `indices_2025/config/reglas_csv_evolucion_carreras.yaml`
- `indices_2025/resultados/reportes_validacion/FASE1_DICCIONARIO_EVOLUCION_CARRERAS.md`
- `indices_2025/resultados/logs/fase1_diccionario_evolucion_carreras.log`

Advertencias:

- La Tabla 25 está fragmentada por la extracción del manual a texto.
- Algunos nombres de campos fueron reconstruidos desde saltos de línea del manual.
- Los campos marcados con `requiere_revision_manual = sí` no deben usarse como
  reglas bloqueantes sin revisión.
- La obligatoriedad no aparece como columna explícita en la Tabla 25; queda como
  `no informado`.
- No se modifica nada fuera de `indices_2025/`.

Próxima fase sugerida: FASE 2 — Construcción del validador automático del CSV
Evolución de Carreras usando el diccionario técnico generado en FASE 1, con las
filas ambiguas como controles no bloqueantes hasta confirmarlas.

## FASE 2 — Arquitectura robusta de esqueletos

Objetivo: dejar preparada la arquitectura completa del subproyecto INDICES 2025
para desarrollo incremental posterior. Esta fase crea catálogos, scripts,
configuraciones, diccionarios, plantillas, fixtures y auditoría en modo
esqueleto. Aún no valida datos reales.

Estructura ampliada:

```text
indices_2025/
├── docs/
├── config/
│   ├── procesos/
│   ├── reglas/
│   └── catalogos/
├── scripts/
│   ├── core/
│   ├── procesos/
│   ├── validadores/
│   └── utilidades/
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── fixtures/
├── resultados/
│   ├── reportes_validacion/
│   ├── diccionarios/
│   ├── logs/
│   ├── plantillas_salida/
│   └── auditoria/
└── README_INDICES_2025.md
```

Scripts creados:

- `indices_2025/scripts/core/indices_core.py`
- `indices_2025/scripts/indices_pipeline.py`
- `indices_2025/scripts/02_diagnostico_arquitectura_indices.py`
- `indices_2025/scripts/procesos/NN_proceso_<id_proceso>.py`

Configs creadas:

- `indices_2025/config/procesos/procesos_indices_2025.json`
- `indices_2025/config/procesos/procesos_indices_2025.csv`
- `indices_2025/config/reglas/reglas_<id_proceso>.yaml`

Plantillas generadas:

- `indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_<id_proceso>.md`
- `indices_2025/resultados/plantillas_salida/plantilla_salida_<id_proceso>.xlsx`
- `indices_2025/data/fixtures/fixture_<id_proceso>.csv`
- `indices_2025/resultados/diccionarios/diccionario_<id_proceso>_esqueleto.json`

Cómo listar procesos:

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular
python3 indices_2025/scripts/indices_pipeline.py --listar-procesos
```

Cómo crear o refrescar esqueletos:

```bash
python3 indices_2025/scripts/indices_pipeline.py --crear-esqueletos
```

Cómo ejecutar diagnóstico:

```bash
python3 indices_2025/scripts/indices_pipeline.py --diagnostico
python3 indices_2025/scripts/02_diagnostico_arquitectura_indices.py
```

Archivos globales de auditoría:

- `indices_2025/resultados/auditoria/ESTADO_PROYECTO_INDICES_2025.md`
- `indices_2025/resultados/auditoria/BITACORA_DECISIONES_INDICES_2025.md`
- `indices_2025/resultados/auditoria/estado_arquitectura_indices_2025.json`
- `indices_2025/resultados/reportes_validacion/FASE2_DIAGNOSTICO_ARQUITECTURA_INDICES_2025.md`

Cómo continuar hacia FASE 3:

FASE 3 debe implementar el primer validador funcional, comenzando por el CSV
Evolución de Carreras, usando el diccionario técnico de FASE 1 y la arquitectura
de esqueletos de FASE 2. Las reglas ambiguas deben mantenerse como no
bloqueantes hasta revisión manual.

Advertencia: esta fase solo prepara arquitectura. No ejecuta validaciones
funcionales sobre datos reales ni completa reglas no informadas en el manual.

## FASE 3 — Validador funcional CSV Evolución de Carreras

Objetivo: implementar el primer validador funcional real del subproyecto,
limitado al proceso `evolucion_carreras`, usando el diccionario técnico de FASE 1
y la arquitectura de FASE 2.

Script principal:

```text
indices_2025/scripts/procesos/17_proceso_evolucion_carreras.py
```

Comandos disponibles:

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular
python3 indices_2025/scripts/procesos/17_proceso_evolucion_carreras.py --diagnostico
python3 indices_2025/scripts/procesos/17_proceso_evolucion_carreras.py --crear-plantilla
python3 indices_2025/scripts/procesos/17_proceso_evolucion_carreras.py
python3 indices_2025/scripts/procesos/17_proceso_evolucion_carreras.py --input indices_2025/data/raw/archivo.csv
python3 indices_2025/scripts/indices_pipeline.py --validar evolucion_carreras
```

Entradas esperadas:

- Diccionario FASE 1:
  `indices_2025/resultados/diccionarios/diccionario_evolucion_carreras.json`
- YAML preliminar:
  `indices_2025/config/reglas_csv_evolucion_carreras.yaml`
- CSV real opcional:
  `indices_2025/data/raw/*.csv`

Salidas generadas:

- `indices_2025/resultados/reportes_validacion/FASE3_VALIDACION_EVOLUCION_CARRERAS.md`
- `indices_2025/resultados/reportes_validacion/validacion_evolucion_carreras.xlsx`
- `indices_2025/resultados/reportes_validacion/validacion_evolucion_carreras.json`
- `indices_2025/resultados/logs/fase3_validacion_evolucion_carreras.log`
- `indices_2025/data/fixtures/plantilla_evolucion_carreras.csv`

Criterios de severidad:

- `ERROR_BLOQUEANTE`: regla explícita, programable sin ambigüedad y con confianza alta.
- `ADVERTENCIA`: regla preliminar, confianza media/baja, ausencia de CSV real o dependencia no resuelta no bloqueante.
- `REVISION_MANUAL`: campos marcados como revisión manual, dependencia de catálogo externo o ambigüedad de extracción.

Limitaciones:

- No corrige datos automáticamente.
- No sobrescribe archivos de entrada.
- No valida catálogos externos CNED/SIES todavía.
- Si no existe CSV real, genera reporte de estado `SIN_CSV_REAL`.
- Los otros procesos INDICES permanecen como esqueletos.

Próxima fase sugerida: FASE 4 — Revisión del resultado del validador de
Evolución de Carreras y decisión sobre correcciones, catálogos externos o
implementación del siguiente proceso INDICES.
