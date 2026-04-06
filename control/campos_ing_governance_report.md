# Reporte Gobernanza — Campos ING (Q, R, S, T)

**Fecha generación:** 2026-04-08 04:38:06
**Total registros:** 1364
**Dictamen:** ⚠️ LISTO CON OBSERVACIONES

## 1. ANIO_ING_ACT (Campo Q)

| Año | Conteo |
|-----|--------|
| 2017 | 1 |
| 2022 | 4 |
| 2023 | 12 |
| 2024 | 48 |
| 2025 | 202 |
| 2026 | 1097 |

**Reglas aplicadas:**

| Regla | Conteo |
|-------|--------|
| R_ACT_01 | 1364 |

## 2. SEM_ING_ACT (Campo R)

| Semestre | Conteo |
|----------|--------|
| 1 | 1360 |
| 2 | 4 |

**Reglas aplicadas:**

| Regla | Conteo |
|-------|--------|
| R_SEM_01 | 1360 |
| R_SEM_02 | 4 |

## 3. ANIO_ING_ORI (Campo S)

| Año | Conteo |
|-----|--------|
| 1900 | 97 |
| 2017 | 1 |
| 2019 | 4 |
| 2020 | 2 |
| 2021 | 6 |
| 2022 | 10 |
| 2023 | 21 |
| 2024 | 51 |
| 2025 | 168 |
| 2026 | 1004 |

**Reglas aplicadas:**

| Regla | Conteo |
|-------|--------|
| R_ORI_A01 | 1171 |
| R_ORI_A04 | 97 |
| R_ORI_A05 | 59 |
| R_ORI_A02 | 37 |

## 4. SEM_ING_ORI (Campo T)

| Semestre | Conteo |
|----------|--------|
| 0 | 97 |
| 1 | 1222 |
| 2 | 45 |

**Reglas aplicadas:**

| Regla | Conteo |
|-------|--------|
| R_ORI_S01 | 1171 |
| R_ORI_S02 | 97 |
| R_ORI_S05 | 59 |
| R_ORI_S03 | 36 |
| R_ORI_S04 | 1 |

## 5. Coherencia FOR_ING_ACT × ORI

| FOR | n | ANIO_ORI=1900 | ANIO_ORI≠1900 |
|-----|---|---------------|---------------|
| 1 | 1171 | 0 | 1171 |
| 2 | 97 | 97 | 0 |
| 3 | 59 | 0 | 59 |
| 11 | 37 | 0 | 37 |

## 6. Hallazgos

- **[WARNING]** V_COHERENCIA_FOR_NO1: 58 registros FOR≠1 donde ANIO_ACT ≤ ANIO_ORI (esperado ACT > ORI)

---
*Generado por motor_campos_ing.py — 2026-04-08 04:38:06*