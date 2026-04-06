# Reporte de Gobernanza — VIG + FECHA_MATRICULA

**Motor**: motor_vig_fecha.py v1.0
**Fecha**: 2026-04-08 04:52:39
**Registros**: 1364
**Dictamen**: ✅ LISTO

---

## 1. Distribución VIG

| VIG | Significado | N | % |
|-----|------------|---|---|
| 0 | Estudiante sin matrícula | 91 | 6.7% |
| 1 | Estudiante con matrícula vigente | 1273 | 93.3% |

## 2. Reglas VIG aplicadas

| Regla | N | % |
|-------|---|---|
| R_VIG_01 | 1273 | 93.3% |
| R_VIG_02 | 90 | 6.6% |
| R_VIG_03 | 1 | 0.1% |

## 3. Cruce ESTADOACADEMICO × VIG

| ESTADOACADEMICO | 0 | 1 |
|---|---|---|
| ELIMINADO | 90 | 0 |
| SUSPENDIDO | 1 | 0 |
| VIGENTE | 0 | 1273 |

## 4. Distribución FECHA_MATRICULA

| Año | N | % |
|-----|---|---|
| 2025 | 572 | 41.9% |
| 2026 | 792 | 58.1% |

## 5. Reglas FECHA_MATRICULA aplicadas

| Regla | N | % |
|-------|---|---|
| R_FM_01 | 1364 | 100.0% |

## 6. Hallazgos

- **[INFO]** V_VIG0_MARCADO_ROJO: 91 registros con VIG=0 (ELIMINADO/SUSPENDIDO) → marcar en rojo en auditoría

---

## Dictamen Final

**✅ LISTO**

- BLOQUEANTES: 0
- WARNINGS: 0
- INFO: 1