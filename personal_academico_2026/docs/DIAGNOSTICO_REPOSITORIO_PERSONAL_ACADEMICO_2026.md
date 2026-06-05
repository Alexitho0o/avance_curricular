# Diagnostico Del Repositorio Para Personal Academico SIES 2026

Fecha de diagnostico: 2026-06-08.

## 1. Estructura General

El repositorio `avance_curricular` contiene flujos regulatorios y de auditoria ya estabilizados. La estructura principal observada es:

| Ruta | Rol observado |
|---|---|
| `scripts/` | Scripts operativos de Matricula Unificada 2026 y validaciones asociadas. |
| `control/` | Gobernanza, evidencias, reportes, catalogos y gate de MU2026. |
| `resultados/` | Salidas reales, auditorias y ejecuciones historicas de MU2026/PES_READY. |
| `cned/` | Modulo separado para cargas CNED, con `data`, `docs`, `scripts`, `tests` y `resultados`. |
| `indices_2025/` | Trabajo de indices/CNED 2025. |
| `docs/` | Documentacion general del repositorio. |
| `data/` | Soporte documental, catalogos y resultados auxiliares. |
| `core/` | Estructura objetivo o transicional, no runtime oficial actual segun README. |
| `src/` | Utilidades Python auxiliares. |
| `tools/` | Herramientas puntuales de auditoria. |
| `archive/` | Historicos, respaldos y material legacy. No debe usarse como fuente final. |
| `backup_estable_2026/` | Respaldos estables. No debe tocarse para este modulo. |

## 2. Scripts Principales Existentes

Scripts y comandos relevantes detectados:

| Ruta | Uso observado |
|---|---|
| `Makefile` | Targets oficiales MU2026: `compile-sies`, `run-oficial`, `validate-oficial`, `run-and-validate-oficial`. |
| `scripts/run_oficial.sh` | Ejecucion oficial MU2026. |
| `scripts/validate_oficial.sh` | Validacion oficial MU2026. |
| `scripts/run_and_validate_oficial.sh` | Ejecucion y validacion MU2026. |
| `scripts/compile_puente_sies_compilado.py` | Compilacion de catalogo puente SIES para MU2026. |
| `scripts/auditoria_maestra.py` | Auditoria maestra MU2026. |
| `scripts/motor_for_ing_act.py` | Motor gobernado para `FOR_ING_ACT` de MU2026. |
| `scripts/motor_campos_ing.py` | Motor de campos de ingreso MU2026. |
| `scripts/motor_vig_fecha.py` | Motor de vigencia y fecha de matricula MU2026. |
| `cned/scripts/run_cned.sh` | Orquestacion CNED. |
| `cned/scripts/generar_archivo_cned.py` | Generacion CNED. |
| `cned/scripts/validar_cned.py` | Validacion CNED. |
| `cned/scripts/check_no_tocar_mu2026.py` | Control de no intervencion sobre MU2026 desde CNED. |

## 3. Carpetas De Resultados Existentes

Carpetas de salidas detectadas:

- `resultados/`
- `resultados/SUBIDA/`
- `resultados/audits/`
- `resultados/run_*`
- `resultados/auditoria_*`
- `control/reportes/`
- `control/evidencias/`
- `cned/resultados/archivos_subida/`
- `cned/resultados/auditorias/`
- `cned/resultados/reportes/`
- `diagnosticos/mu2026_postgrado/`
- `data/resultados/`
- `archive/resultados_*`

Estas rutas no deben usarse como destino del nuevo proceso para evitar sobrescrituras o mezcla de evidencia.

## 4. Modulos O Utilidades SIES Reutilizables

Existen patrones reutilizables solo como referencia arquitectonica:

- Separacion por modulo, como `cned/`.
- Carpeta de control y auditoria con evidencia por campo, como `control/evidencias/`.
- Validaciones previas y gate documental, como `control/gate/`.
- Scripts de ejecucion y validacion separados, como `run_oficial.sh` y `validate_oficial.sh`.
- Compilacion/auditoria con reportes JSON y Markdown.

No se recomienda reutilizar directamente motores MU2026 para Personal Academico en esta fase. Sus reglas pertenecen a Matricula Unificada y no constituyen fuente normativa para Personal Academico SIES 2026.

## 5. Archivos Que No Deben Tocarse

Para esta intervencion se consideran protegidos:

- `Makefile`
- `README.md`
- `agent.md`
- `scripts/`
- `core/`
- `src/`
- `tools/`
- `control/`
- `resultados/`
- `cned/`
- `indices_2025/`
- `archive/`
- `backup_estable_2026/`
- `data/resultados/`
- `docs/` globales del repositorio
- Los tres insumos oficiales ubicados en la raiz del repo, salvo lectura y copia fiel a `personal_academico_2026/insumos/`.

## 6. Ubicacion Mas Segura

La ubicacion mas segura para el nuevo modulo es:

```text
personal_academico_2026/
```

Motivos:

- Es una carpeta nueva, aislada y trazable.
- No se superpone con `scripts/`, `control/`, `resultados/` ni `cned/`.
- Permite separar insumos, scripts, resultados, auditorias y bitacoras.
- Replica el criterio de modulo independiente ya usado por `cned/`.

## 7. Riesgos Detectados

| Riesgo | Mitigacion inicial |
|---|---|
| Mezcla con outputs MU2026 en `resultados/`. | Usar solo `personal_academico_2026/resultados/`. |
| Uso accidental de historicos en `archive/`. | Documentar prohibicion y no leer `archive/` como fuente final. |
| Reutilizacion indebida de reglas MU2026. | Tratar utilidades existentes solo como referencia tecnica, no normativa. |
| Nombres de archivos con acentos en composicion Unicode NFD. | Registrar nombre local y forma NFC en diagnostico de insumos. |
| Tension entre estructura CSV con `;` e instructivo que menciona CSV delimitado por comas. | Marcar como pendiente de confirmacion antes de exportar. |
| Instructivo extraido desde PDF con tabla textual imperfecta. | No atribuir obligatoriedad dudosa sin evidencia clara. |
| Cargas PES acumulativas por tipo y numero de documento. | Exigir auditoria previa y control de duplicados antes de carga futura. |

## 8. Confirmacion De No Alteracion

La creacion del modulo se puede realizar sin alterar flujos previos porque:

- No requiere modificar scripts oficiales existentes.
- No requiere cambiar dependencias.
- No requiere tocar `Makefile`.
- No requiere escribir en `resultados/`, `control/`, `cned/` ni `archive/`.
- Los insumos oficiales ya estan disponibles en la raiz del repositorio y se copian sin modificacion a `personal_academico_2026/insumos/`.
