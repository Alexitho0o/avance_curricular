# H002l · Depuración y cierre

D · Alexi, 29-10-2026. Implementación C; evidencia B/C; pendientes E.

```json
{
  "antiguos": {
    "unidad": "MATRICULAS_POTENCIALES_MU2026",
    "total": 4105,
    "revision_H002k": 1046,
    "revision_H002l": 0,
    "por_motivo": {
      "ANTIGUO_1_CODIGO_O_FILA_NO_RESUELTA": 0,
      "ANTIGUO_2_CODIGO_SIN_OFERTA_2027": 0,
      "ANTIGUO_3_VIGENCIA_3": 0
    },
    "conservan_codigo": 4105,
    "tipo_E_informativo": 1046
  },
  "nuevos": {
    "unidad": "OPCIONES_PLAN_FAMILIA_CATALOGO_NO_PERSONAS",
    "total": 223,
    "asignacion": 59,
    "revision_real": 34,
    "informativos": 130,
    "revision_por_motivo": {
      "NUEVO_TIPO_E_CON_ADMISION": 17,
      "REVISION_REAL_TIPO_SIN_VERSION_EN_FAMILIA_CON_ADMISION": 1,
      "VARIAS_VERSIONES_VIGENTES_MISMO_TIPO": 15,
      "CODIGO_NUEVO_SIN_PLAN": 1
    },
    "de_108": {
      "PLAN_SIN_ADMISION_2027": 107,
      "REVISION_REAL": 1
    },
    "de_40_tipo_E": {
      "familia_admite": 17,
      "familia_no_admite": 23
    }
  },
  "codigos_sin_plan": {
    "unidad": "CODIGO_CATALOGO_NO_PERSONAS",
    "total": 37,
    "solapamiento": "El código sin plan de las opciones nuevas está incluido en los 37; no sumar unidades."
  }
}
```

Los cuatro SIN_OFERTA_2027 de H002 son antecedentes de catálogo: no hay filas MU2026 con esos códigos en el universo potencial. No se inventan matrículas para ellos.

La revisión real de nuevos mantiene las cinco familias ambiguas y los 37 códigos sin plan; estos no se suman a opciones de catálogo.

## Transiciones de motivos nuevos

| antes | ahora | opciones |
|---|---|---|
| CODIGO_NUEVO_SIN_PLAN | CODIGO_NUEVO_SIN_PLAN | 1 |
| NUEVO_TIPO_E | NUEVO_TIPO_E_CON_ADMISION | 17 |
| NUEVO_TIPO_E | PLAN_SIN_ADMISION_2027 | 23 |
| SIN_VERSION_VIGENTE_PARA_TIPO | PLAN_SIN_ADMISION_2027 | 107 |
| SIN_VERSION_VIGENTE_PARA_TIPO | REVISION_REAL_TIPO_SIN_VERSION_EN_FAMILIA_CON_ADMISION | 1 |
| VARIAS_VERSIONES_VIGENTES_MISMO_TIPO | VARIAS_VERSIONES_VIGENTES_MISMO_TIPO | 15 |
| VIGENCIA_1_Y_TIPO_PLAN_UNICOS_D | VIGENCIA_1_Y_TIPO_PLAN_UNICOS_D | 59 |

Reproducción: `python3 outputs/depuracion_codigo_mu2027_20261029/construir.py --check`. Las salidas H002k se reproducen en su commit congelado, con su función anterior.
