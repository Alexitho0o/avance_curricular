# H002k · Activación interna MU 2027

D · Alexi, 29-10-2026. No se genera carga.

| Estado | 2026 | 2027 |
|---|---|---|
| APROBADA_D_2027 | 0 | 13 |
| CONTINUA | 53 | 53 |
| FUERA_ALCANCE | 11 | 21 |
| HISTORICO_SIN_MATRICULA_RECIENTE | 0 | 6 |
| NUEVO_2027_CON_PLAN | 0 | 0 |
| NUEVO_2027_SIN_PLAN_E | 0 | 37 |
| PLAN_HISTORICO_SIN_ALUMNOS_VIGENTES | 0 | 0 |
| SIN_OFERTA_2027 | 4 | 0 |
| VERSION_MULTIPLE_E | 14 | 0 |
| VERSION_MULTIPLE_RESUELTA | 24 | 31 |

## Universo potencial MU 2026 (matrículas, todos los VIG)

{
  "unidad": "MATRICULA",
  "total": 4105,
  "por_via": {
    "ANTIGUO": 3059,
    "REVISION_MANUAL": 1046
  },
  "manual_por_motivo": {
    "ANTIGUO_TIPO_E": 1046
  },
  "cinco_familias_tipo_E": 252,
  "codigos_inconsistentes_conservados": 0
}

Los 252 pertenecen sólo a cinco familias. No confundir el universo potencial con continuidad observada 2027.

## Nuevos simulados: opciones de catálogo

{
  "unidad": "OPCION_PLAN_FAMILIA_CATALOGO",
  "total": 223,
  "revision": 164,
  "motivos": {
    "SIN_VERSION_VIGENTE_PARA_TIPO": 108,
    "NUEVO_TIPO_E": 40,
    "VARIAS_VERSIONES_VIGENTES_MISMO_TIPO": 15,
    "CODIGO_NUEVO_SIN_PLAN": 1
  }
}

37 códigos adicionales sin plan: no personas. No sumar las unidades.

## ADMP/CADMP: control MU 2026

| codcarpr | plan | codigo_unico | VIG | matriculas_MU2026 |
|---|---|---|---|---|
| ADMP | ADMP20251 | I162S2C83J4V1 | 0 | 3 |
| ADMP | ADMP20251 | I162S2C83J4V1 | 1 | 72 |
| ADMP | PLAN_NO_OBSERVADO | I162S2C83J4V1 | 0 | 43 |
| ADMP | PLAN_NO_OBSERVADO | I162S2C83J4V1 | 1 | 12 |
| CADMP | CADMP20251 | I162S2C83J4V2 | 1 | 7 |
| CADMP | PLAN_NO_OBSERVADO | I162S2C83J4V2 | 0 | 1 |
| CADMP | PLAN_NO_OBSERVADO | I162S2C83J4V2 | 1 | 2 |

C83J4V2 tiene 9 VIG 1 de CADMP (7 con plan anual observado, 2 sin él) y 1 VIG 0 sin plan. Las referencias sin plan pasan a revisión; decisión nueva sólo catálogo 2027. Perfil H002j y antecedentes citados con hash.

## Reproducción

`python3 outputs/activacion_codigo_mu2027_20261029/construir.py --check` verifica bytes sin escribir.
Pruebas: `python3 -m unittest discover -s outputs/activacion_codigo_mu2027_20261029 -p 'test_*.py'`.
Detalle de revisión sólo en `~/.local/share/ipss/h002k_20261029/`; no versionado.
