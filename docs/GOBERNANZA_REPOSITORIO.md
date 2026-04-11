# Gobernanza del Repositorio — avance_curricular

## 1. Estado operativo actual

El repositorio `avance_curricular` se encuentra validado funcionalmente.  
El flujo oficial de ejecución y validación corre correctamente con input real y deja artefactos consistentes.

## 2. Flujo oficial

### Scripts oficiales
- `scripts/run_oficial.sh`
- `scripts/validate_oficial.sh`
- `scripts/run_and_validate_oficial.sh`

### Motores oficiales
- `codigo_gobernanza_v2.py`
- `qa_checks.py`
- `scripts/auditoria_maestra.py`
- `scripts/compile_puente_sies_compilado.py`

### Comandos oficiales
- `make run-oficial`
- `make validate-oficial`
- `make run-and-validate-oficial`

## 3. Rutas y su estatus

| Ruta | Estatus | Rol |
|---|---|---|
| `scripts/` | Oficial | Orquestación y utilitarios del pipeline |
| `resultados/` | Oficial | Salidas reales de ejecución y validación |
| `control/` | Oficial | Control, trazabilidad y evidencia |
| `control/catalogos/` | Oficial | Catálogo canónico compilado |
| `control/reportes/` | Oficial | Reportería técnica y evidencia operativa |
| `docs/` | Documental | Marco normativo y documentación técnica |
| `archive/` | Histórica | Respaldo y contexto histórico |
| `patches/` | Soporte | Parches específicos auditables |
| `data/` | Soporte | Datos y referencias documentales |
| `data/resultados/` | Ambigua / Documental | Marcadores de migración, no runtime oficial actual |
| `core/` | En transición / Ambigua | Estructura objetivo declarada, no runtime real actual |

## 4. Artefactos oficiales de ejecución

Los siguientes artefactos forman parte del flujo oficial actual:

- `resultados/archivo_listo_para_sies.xlsx`
- `resultados/matricula_unificada_2026_pregrado.csv`
- `resultados/auditoria_maestra.md`
- `control/catalogos/PUENTE_SIES_COMPILADO.tsv`
- `control/reportes/reporte_compilacion_puente_sies.json`

## 5. Clasificación de scripts

### Oficiales
- `scripts/run_oficial.sh`
- `scripts/validate_oficial.sh`
- `scripts/run_and_validate_oficial.sh`
- `codigo_gobernanza_v2.py`
- `qa_checks.py`
- `scripts/auditoria_maestra.py`
- `scripts/compile_puente_sies_compilado.py`

### Auxiliares
- `scripts/run_loop_remediacion_codcli.sh`

### Legacy
- `scripts/run_mu_operativo.sh`

### Exploratorios
- `scripts/_test_for_ing_act.py`
- `scripts/_test_for_ing_act_v2.py`

### Tests de validación
- `scripts/test_for_ing_act.py`
- `scripts/test_campos_ing.py`
- `scripts/test_vig_fecha.py`

## 6. Ambigüedades actuales

1. La ruta oficial de outputs en ejecución real es `resultados/`, mientras que `data/resultados/` contiene marcadores documentales.
2. La estructura `core/` aparece como objetivo futuro, pero el runtime real sigue operando desde la raíz del repositorio.
3. Conviven scripts oficiales con scripts legacy y exploratorios de nombres cercanos.
4. `resultados/` mezcla salidas oficiales vigentes con snapshots históricos.
5. Existen archivos marcador “original movido...” en rutas activas, lo que puede inducir a error.

## 7. Decisión operativa vigente

Hasta nueva documentación explícita, se establece lo siguiente:

- La ruta runtime oficial de outputs es `resultados/`.
- El flujo oficial se ejecuta mediante `make run-oficial`, `make validate-oficial` y `make run-and-validate-oficial`.
- `data/resultados/` no debe interpretarse como ruta activa de outputs.
- `core/` no debe interpretarse como fuente runtime oficial mientras no se formalice su migración.
- Los scripts legacy y exploratorios no deben usarse como flujo estándar.

## 8. Pendientes humanos

- Definir si el runtime oficial permanecerá en raíz o migrará formalmente a `core/`.
- Definir el estatus final de `data/resultados/`.
- Aprobar clasificación final de scripts legacy y exploratorios.
- Definir política de retención de snapshots históricos en `resultados/run_*`.

