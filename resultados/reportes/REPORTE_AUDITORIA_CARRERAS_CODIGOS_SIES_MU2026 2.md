# Auditoría de carreras, planes y combinaciones SIES MU2026

Generado: 2026-06-25T17:20:18

## Respuesta central

La auditoría fue agregada por carrera, plan y combinación académica. No se modificó Matrícula Unificada, Extranjeros V6 ni se generó PES.

## Indicadores

| Indicador | Total | Porcentaje_sobre_combinaciones |
| --- | --- | --- |
| Estudiantes procesados | 34522 |  |
| CODCLI distintos | 4118 |  |
| Carreras internas distintas | 45 |  |
| Planes de estudio distintos | 45 |  |
| Códigos SIES distintos utilizados | 61 |  |
| Combinaciones académicas distintas | 64 | 100.00% |
| Resueltas inequívocamente | 41 | 64.06% |
| Resueltas por regla formal | 5 | 7.81% |
| Resueltas manualmente | 17 | 26.56% |
| Ambiguas no resueltas | 1 | 1.56% |
| Inconsistentes con multicódigo | 0 | 0.00% |
| Posibles errores de asignación | 0 | 0.00% |
| Sin código | 0 | 0.00% |
| Estudiantes potencialmente afectados | 1 |  |

## Métricas separadas

- REPRODUCIBILIDAD_ESTUDIANTES: 100.00%
- CORRECCION_COMBINACIONES: 98.44%

La reproducibilidad por estudiante no equivale a corrección por combinación. La primera mide si se puede reconstruir el código final usado; la segunda exige unicidad, compatibilidad y justificación por combinación académica.

## Riesgo material

Combinaciones con estado de riesgo: 1.

Estudiantes potencialmente afectados: 1.

## Carreras con mayor riesgo

| CODCARPR | carrera | combinaciones_inconsistentes | estudiantes_afectados |
| --- | --- | --- | --- |
| NETMRE | INGENIERIA EN CONECTIVIDAD Y REDES | 0 | 1 |
| IADM | INGENIERIA EN ADMINISTRACION DE EMPRESAS | 0 | 0 |
| ICIB | INGENIERIA EN CIBERSEGURIDAD | 0 | 0 |
| IINF | INGENIERIA EN INFORMATICA | 0 | 0 |
| TAMD | TECNICO EN ADMINISTRACION DE EMPRESAS | 0 | 0 |
| TCIB | TECNICO EN CIBERSEGURIDAD | 0 | 0 |
| TPAS | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | 0 | 0 |
| CICIB | CONTINUIDAD INGENIERIA  CIBERSEGURIDAD | 0 | 0 |
| CICRE | CONTINUIDAD INGENIERIA CONECTIVIDAD Y REDES | 0 | 0 |
| ICRE | INGENIERIA EN CONECTIVIDAD Y REDES | 0 | 0 |

## Recomendación

No rectificar automáticamente desde esta auditoría. Antes de reutilizar la lógica para otros procesos, conviene gobernar las combinaciones ambiguas por tabla puente explícita a nivel `CODCARPR + PLAN_DE_ESTUDIO + COD_SED + JORNADA + MODALIDAD + TIPO_PLAN + DURACION`, y probar que una misma LLAVE_4 no derive en más de un código final.

## Archivos generados

- `resultados/auditorias/UNIVERSO_CARRERAS_CODIGOS_SIES_MU2026.csv`
- `resultados/auditorias/MATRIZ_COMBINACIONES_ACADEMICAS_SIES_MU2026.csv`
- `resultados/auditorias/INCONSISTENCIAS_CODIGO_SIES_POR_COMBINACION_MU2026.csv`
- `resultados/auditorias/IMPACTO_INCONSISTENCIAS_SIES_MU2026.csv`
- `resultados/auditorias/RESUMEN_CARRERAS_RESOLUCION_SIES_MU2026.csv`
- `resultados/auditorias/REVISION_CARRERAS_CODIGOS_SIES_MU2026.xlsx`

Backup: `/Users/alexi/Documents/GitHub/avance_curricular/backups/pre_auditoria_combinaciones_sies_mu2026_20260625_171929`

## Hashes

{
  "universo": "95873bc7e270183168a5e6cf7d07dc8bce46b12beab43b1005a0192c2c5f21dd",
  "matriz": "5cf5042dec3817d227a2d2778f1392fabb96c29a792589d61119319bcdc63e0b",
  "inconsistencias": "2c22de5aa93058f6a84f4ea9886c50ce159daf6ebdc0f92e73f97dd50b5770d7",
  "impacto": "7fbcdbdf678e61cfb40c9f37ec63c0786599c7e88b6b783cf983536fca0e7cae",
  "resumen_carreras": "3989ec116195dbf709a3e9cabd4e3b6f451c11055b03b2a7f1b6d832b7f1ed30",
  "excel": "335a2f96d0362136ad7c4270f577755389b55cacb739e3aa626bf589513ff879"
}
