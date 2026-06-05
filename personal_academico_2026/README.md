# Personal Academico SIES 2026

Modulo inicial para preparar, validar y documentar el proceso de carga PES/SIES 2026 de Personal Academico, separado de los flujos ya estabilizados de Avance Curricular, Matricula Unificada 2026, CNED y otros procesos del repositorio.

## Objetivo

Dejar una base conservadora y trazable para construir, en fases posteriores, los archivos oficiales de carga de:

- Personal Academico en la Institucion.
- Personal Academico Fuera de la Institucion.

En esta primera intervencion no se generan archivos finales de carga, no se implementa el pipeline completo y no se modifican scripts existentes.

## Alcance

Este modulo cubre por ahora:

- Diagnostico del repositorio y de riesgos de convivencia con flujos previos.
- Resguardo local de las tres fuentes oficiales del proceso.
- Documentacion inicial del modulo.
- Diccionario tecnico preliminar de columnas oficiales.
- Validaciones minimas esperadas antes de cualquier exportacion futura.

Queda fuera de esta fase:

- Lectura de bases institucionales de personal.
- Normalizacion de datos.
- Construccion de catalogos institucionales.
- Exportacion de CSV finales.
- Cargas en PES.
- Cambios sobre Matricula Unificada, Avance Curricular, CNED o pipelines historicos.

## Fuentes Oficiales

El modulo debe basarse exclusivamente en estas fuentes oficiales conservadas en `insumos/`:

| Fuente | Uso |
|---|---|
| `20260421_57181_20260420_Estructura_Personal_Académico_en_Institución_2026.csv` | Estructura oficial para Personal Academico en la Institucion. |
| `20260421_84406_20260420_Estructura_Personal_Académico_Fuera_Institución_2026.csv` | Estructura oficial para Personal Academico Fuera de la Institucion. |
| `Personal Académico SIES - Instructivo 2026.txt` | Instructivo normativo del proceso Personal Academico SIES 2026. |

Nota de trazabilidad: los nombres locales pueden verse con acentos en composicion Unicode NFD en macOS. La forma NFC coincide con los nombres oficiales indicados por el proyecto.

## Archivos Finales Esperados

En fases posteriores se deberian producir, solo despues de auditoria previa:

- Un CSV valido para la carga PES/SIES de Personal Academico en la Institucion.
- Un CSV valido para la carga PES/SIES de Personal Academico Fuera de la Institucion, si aplica.
- Reportes de auditoria que demuestren estructura, columnas, orden, reglas de formato y ausencia de indices o columnas auxiliares.

Los nombres finales aun no se fijan en esta fase porque el instructivo indica que PES no restringe el nombre del archivo, y porque aun no existe una decision operativa documentada para nombrado institucional.

## Reglas De Seguridad

- No modificar scripts oficiales existentes.
- No reutilizar `archive/` como fuente final.
- No sobrescribir resultados historicos.
- No mover, renombrar ni eliminar archivos existentes.
- No crear dependencias nuevas sin justificacion documentada.
- No inventar campos, codigos ni reglas.
- Mantener el orden exacto de columnas de las estructuras oficiales.
- No agregar columnas auxiliares a archivos finales.
- No exportar indices.
- No producir archivos finales sin auditoria previa.

## Estructura Del Modulo

```text
personal_academico_2026/
  README.md
  INSTRUCCIONES_PERSONAL_ACADEMICO_2026.md
  docs/
  insumos/
  catalogos/
  scripts/
  tests/
  resultados/
  auditorias/
  bitacoras/
```

Uso previsto:

| Carpeta | Uso |
|---|---|
| `docs/` | Diagnosticos, diccionario tecnico y documentacion normativa. |
| `insumos/` | Fuentes oficiales y, en fases futuras, insumos originales controlados. |
| `catalogos/` | Catalogos derivados o confirmados, solo cuando exista fuente explicita. |
| `scripts/` | Scripts futuros del modulo. Deben ser autocontenidos y no alterar otros flujos. |
| `tests/` | Pruebas unitarias o de validacion estructural futuras. |
| `resultados/` | Salidas candidatas, nunca sobrescritas sin versionado o timestamp. |
| `auditorias/` | Evidencia de validaciones y dictamen antes de exportar. |
| `bitacoras/` | Registro de decisiones, pendientes y ejecuciones. |

## Fases De Trabajo

1. Diagnosticar el repositorio sin modificar flujos existentes.
2. Analizar las tres fuentes oficiales y documentar columnas, reglas y pendientes.
3. Crear estructura base aislada del modulo.
4. Redactar documentacion e instrucciones de no intervencion.
5. Preparar diccionario preliminar y validaciones minimas.
6. En una fase posterior, implementar lectura, validacion, normalizacion y exportacion con auditoria previa.

## Criterios De No Intervencion

Este modulo no debe importar ni modificar directamente:

- `scripts/`
- `core/`
- `src/`
- `control/`
- `resultados/`
- `cned/`
- `indices_2025/`
- `archive/`
- `data/resultados/`

Cualquier reutilizacion futura de utilidades existentes debe quedar documentada como decision tecnica, con pruebas de que no altera salidas ni invariantes de otros procesos.

## Scripts Disponibles

Estado actual: validador base creado y exportador controlado bloqueado por seguridad.

| Script | Uso |
|---|---|
| `scripts/config_personal_academico_2026.py` | Configuracion centralizada de rutas, nombres oficiales, columnas y parametros de exportacion. |
| `scripts/validaciones_personal_academico_2026.py` | Funciones pequenas de normalizacion, estructura, fechas, horas, duplicados y reporte auditable. |
| `scripts/validar_archivo_personal_academico_2026.py` | CLI para validar archivos de trabajo y generar auditoria en `auditorias/`. |
| `scripts/exportar_personal_academico_2026.py` | Exportador controlado. No genera archivo final salvo autorizacion explicita y estructura valida. |

Ejemplo de validacion:

```bash
python personal_academico_2026/scripts/validar_archivo_personal_academico_2026.py \
  --tipo en_institucion \
  --input personal_academico_2026/tests/fixtures/en_institucion_valido_minimo.csv
```

Ejemplo de exportador bloqueado:

```bash
python personal_academico_2026/scripts/exportar_personal_academico_2026.py \
  --tipo en_institucion \
  --input personal_academico_2026/tests/fixtures/en_institucion_valido_minimo.csv \
  --output personal_academico_2026/resultados/personal_academico_en_institucion_2026_PES_READY.csv
```

Pruebas:

```bash
python -m pytest personal_academico_2026/tests/
```

Nota: si `pytest` no esta disponible en el entorno local, no instalar dependencias globales sin justificacion; las pruebas quedan preparadas para ejecutarse cuando exista esa herramienta.
