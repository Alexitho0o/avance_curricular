
## Validación controlada CODCLI en base_datos

Fecha: 2026-05-07 11:43:01

### Resultado
Se validó la incorporación/control de CODCLI como columna auxiliar en `base_datos`, sin alterar la lógica estable del flujo.

### Evidencia técnica
- Entorno usado: `.venv` del proyecto `avance_curricular`.
- Python usado: `/Users/alexi/Documents/GitHub/avance_curricular/.venv/bin/python`.
- pip validado: `26.1.1`.
- pandas validado: `3.0.2`.
- Script validado: `codigo_gobernanza_v2.py`.

### Confirmaciones
- `python -m py_compile codigo_gobernanza_v2.py`: OK.
- `python codigo_gobernanza_v2.py`: OK.
- CODCLI detectado en `base_datos`.
- Informados: 3440.
- Vacíos: 707.
- Flujo finalizó con:
  - `matricula_unificada: true`
  - `avance_curricular: true`

### Ubicaciones relevantes en código
- Detección opcional de CODCLI en `base_datos`: líneas aproximadas 2306–2324.
- Depuración provisoria RUT↔CODCLI: líneas aproximadas 2373–2400.

### Regla de gobernanza
CODCLI queda tratado como campo auxiliar/trazable. No debe modificar la lógica oficial de cálculos, cruces, deduplicaciones ni salidas, salvo que se habilite explícitamente una fase posterior de validación.

