# Integración AC — Avance Curricular desde PROMEDIOSDEALUMNOS

## Estado

Operativa, desactivada por defecto, no bloqueante.

## Fases completadas

- OK FASE 1
- OK FASE 2
- OK FASE 3
- OK FASE 4
- OK FASE 5
- OK FASE 6B
- OK FASE 7B
- OK FASE 8B
- OK FASE 9B
- OK FASE 10B
- OK FASE 11B
- OK AJUSTE PYLANCE

## Propósito

La integración AC incorpora métricas académicas provenientes de `PROMEDIOSDEALUMNOS_7804.xlsx` al archivo longitudinal `PREGRADO_TRAYECTORIA_CARACTERIZACION_*`.

La integración no reemplaza cálculos productivos existentes. Solo enriquece la hoja longitudinal de pregrado cuando la bandera explícita está activa.

## Fuente de datos

- Archivo: `/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx`
- Hoja principal: `Hoja1`
- Hoja auxiliar: `DatosAlumnos`
- Llave principal: `CODCLI`
- Llave alternativa disponible: `RUT + CODCARR`

## Módulos relacionados

- `integracion_avance_curricular.py`
- `caracterizacion.py`
- `run_ac_integracion_test.sh`

## Punto de integración

El hook se ejecuta dentro de:

`BLOQUE 10.bis · TRAYECTORIA LONGITUDINAL ACADÉMICA-ENCUESTA`

La integración se aplica antes de exportar el archivo:

`PREGRADO_TRAYECTORIA_CARACTERIZACION_*`

## Archivo de salida

`PREGRADO_TRAYECTORIA_CARACTERIZACION_YYYY_PX_YYYYMMDD.xlsx`

## Hoja enriquecida

`TRAYECTORIA_POR_PERIODO`

## Hoja de auditoría

`AUDITORIA_AVANCE_CURRICULAR`

Esta hoja se crea solo cuando la integración AC está activa y existen columnas `_AC_` incorporadas en `TRAYECTORIA_POR_PERIODO`.

## Columnas generadas

| Columna | Significado | Fuente |
|---|---|---|
| `_AC_ASI_INS_ANT` | Asignaturas inscritas/cursadas del año académico de referencia | Hoja1 |
| `_AC_ASI_APR_ANT` | Asignaturas aprobadas del año académico de referencia | Hoja1 |
| `_AC_ASI_INS_HIS` | Asignaturas registradas en histórico disponible | Hoja1 |
| `_AC_ASI_APR_HIS` | Asignaturas aprobadas/homologadas/convalidadas/reconocidas en histórico disponible | Hoja1 |
| `_AC_PROM_PRI_SEM` | Promedio del primer semestre del año de referencia | Hoja1 |
| `_AC_PROM_SEG_SEM` | Promedio del segundo semestre operacional del año de referencia | Hoja1 |
| `_AC_NIV_ACA` | Nivel académico priorizando DatosAlumnos.NIVEL | DatosAlumnos / Hoja1 |
| `_AC_NIV_ACA_FUENTE` | Fuente usada para NIV_ACA | Motor AC |

## Reglas de cálculo resumidas

- `PERIODO=3` puede operar como segundo semestre.
- `NIV_ACA` prioriza `DatosAlumnos.NIVEL` y usa `Hoja1.NIVEL` como fallback.
- Para análisis 2026, el año académico de referencia se resolvió como `2025`.
- La integración es no bloqueante: si falla la carga, el cálculo o el enriquecimiento, el flujo conserva `df_tray` sin columnas AC y continúa.

## Modo seguro de prueba

```bash
cd "/Users/alexi/Documents/GitHub/CARACTERIZACIÓN"
./run_ac_integracion_test.sh
```

## Qué hace el script

- Activa temporalmente AC.
- Compila `caracterizacion.py` e `integracion_avance_curricular.py`.
- Ejecuta el flujo solo hasta `BLOQUE 10.bis`.
- Omite FCU con `CARACTERIZACION_SKIP_FCU=1`.
- Corta después de 10.bis con `CARACTERIZACION_STOP_AFTER_10BIS=1`.
- Valida el Excel generado.
- Abre el Excel.
- Restaura la bandera `ACTIVAR_INTEGRACION_AVANCE_CURRICULAR` a `False`.
- Compila nuevamente al final.

## Validaciones esperadas

- `AUDITORIA_AVANCE_CURRICULAR_OK: SI`
- `INTEGRACION_AC_OK: SI`
- `HOJA_CON_COLUMNAS_AC: TRAYECTORIA_POR_PERIODO`
- `TOTAL_COLUMNAS_AC: 8`
- `BANDERA_RESTAURADA_FALSE: SI`
- `COMPILACION_FINAL_OK: SI`

## Guardrails

- No tocar FCU.
- No tocar LimeSurvey.
- No tocar PyGWalker.
- No tocar dashboards.
- No ejecutar sin corte si solo se está probando AC.
- No dejar la bandera en `True`.
- No editar manualmente el Excel fuente.
- No importar ni ejecutar `codigo_gobernanza_v2.py`.
- No cambiar nombres de hojas existentes.
- No cambiar cálculos existentes.
- No usar el CSV MU posicional como fuente principal de esta integración.

## Pylance / VS Code

El intérprete del workspace debe ser:

`/Users/alexi/Documents/GitHub/avance_curricular/.venv/bin/python3`

`.vscode/settings.json` ya fue configurado para ese intérprete y para resolver paths locales del proyecto principal y del proyecto fuente.

## Checklist de verificación rápida

```bash
cd "/Users/alexi/Documents/GitHub/CARACTERIZACIÓN"

grep -n "ACTIVAR_INTEGRACION_AVANCE_CURRICULAR" integracion_avance_curricular.py | head

/Users/alexi/Documents/GitHub/avance_curricular/.venv/bin/python3 -m py_compile caracterizacion.py

/Users/alexi/Documents/GitHub/avance_curricular/.venv/bin/python3 -m py_compile integracion_avance_curricular.py

bash -n run_ac_integracion_test.sh
```

La línea de bandera debe mostrar:

`ACTIVAR_INTEGRACION_AVANCE_CURRICULAR = False`

## Último estado validado

- Archivo generado en prueba: `/Users/alexi/Desktop/PREGRADO_TRAYECTORIA_CARACTERIZACION_2026_P1_20260505.xlsx`
- Filas enriquecidas: `5016/13207`
- Columnas `_AC_`: `8`
- Alcance: `MULTIANUAL`
- Año referencia: `2025`
- Hoja enriquecida: `TRAYECTORIA_POR_PERIODO`
- Hoja de auditoría: `AUDITORIA_AVANCE_CURRICULAR`

