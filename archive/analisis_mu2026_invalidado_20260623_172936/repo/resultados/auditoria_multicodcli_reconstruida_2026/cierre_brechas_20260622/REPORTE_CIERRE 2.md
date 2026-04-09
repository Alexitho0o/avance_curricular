# Reporte de cierre - brechas auditoria multicodcli reconstruida 2026

Fecha de ejecucion: 2026-06-22T14:01:52

## Alcance

Esta fase usa como insumo los artefactos de la auditoria reconstruida y vuelve a la fuente original solo para evidencia focalizada de matricula/situacion por CODCLI. No modifica bases.

## Conciliacion 4.653 CODCLI

| categoria                 | cantidad |
| ------------------------- | -------- |
| CODCLI_NO_CLASIFICABLE    | 0        |
| CODCLI_SIN_FILA_MU        | 0        |
| DUPLICADO_TECNICO         | 0        |
| HISTORICO_NO_VIGENTE      | 1086     |
| SIN_EVIDENCIA_2026_1      | 0        |
| VIGENCIA_AMBIGUA          | 94       |
| VIGENTE_2026_1_CONFIRMADO | 3427     |
| VIGENTE_PARA_OTRA_OFERTA  | 46       |

Total conciliado: 4653. Diferencia: 0. Los 94 CODCLI faltantes del conteo vigentes+historicos corresponden a `VIGENCIA_AMBIGUA`.

## Unidad real de Casos OK

| indicador_anterior | nombre_no_ambiguo             | unidad              | formula                                                           | fuente_calculo                       | conteo_reportado | conteo_recalculado | doble_conteo_detectado | observacion                                                                                 |
| ------------------ | ----------------------------- | ------------------- | ----------------------------------------------------------------- | ------------------------------------ | ---------------- | ------------------ | ---------------------- | ------------------------------------------------------------------------------------------- |
| casos_OK           | RUT_OK                        | RUT                 | count_distinct(RUT) donde clasificacion_RUT empieza con OK_       | RESUMEN_EJECUTIVO.xlsx / RESUMEN_RUT | 2000             | 2000               | NO                     | El resumen tiene una fila por RUT; no representa filas MU, CODCLI ni filas de trazabilidad. |
| casos_OK           | FILAS_TRAZABILIDAD_CON_RUT_OK | RUT+CODCLI+LLAVE_MU | filas de TRAZABILIDAD_RUT_CODCLI cuyo RUT tiene clasificacion OK_ | TRAZABILIDAD_RUT_CODCLI.xlsx         |                  | 2171               | NO_APLICA              | Este conteo es distinto y no debe llamarse Casos OK.                                        |
| casos_OK           | CODCLI_CON_RUT_OK             | RUT+CODCLI          | CODCLI unicos en RUT con clasificacion OK_                        | TRAZABILIDAD_RUT_CODCLI.xlsx         |                  | 2171               | NO_APLICA              | Unidad auxiliar para evitar confundir RUT con CODCLI.                                       |

## Revisiones criticas

| campo        | suma_categorias | total_inicial | cuadra |
| ------------ | --------------- | ------------- | ------ |
| ANIO_ING_ORI | 462             | 462           | True   |
| COD_CAR      | 36              | 36            | True   |
| JOR          | 3               | 3             | True   |
| MODALIDAD    | 2               | 2             | True   |
| NIV_ACA      | 1126            | 1126          | True   |

Las revisiones manuales reales excluyen diferencias personales menores y trayectorias historicas que no afectan la fila MU.

## 34 RUT con multiples CODCLI vigentes

| clasificacion_final                  | cantidad |
| ------------------------------------ | -------- |
| DOS_CODCLI_MISMA_CARRERA_CONTINUIDAD | 28       |
| DOS_CODCLI_DOS_OFERTAS_PERO_UNA_MU   | 4        |
| REQUIERE_REVISION                    | 2        |

## 6 matches ambiguos

| RUT      | LLAVE_MU                                   | decision_final | motivo_exactitud_ambiguedad                                                       |
| -------- | ------------------------------------------ | -------------- | --------------------------------------------------------------------------------- |
| 12914312 | MU_LINEA_00094|RUT=12914312-6|S2C22M3J4V2  | SIN_MATCH      | COD_CAR MU no coincide con ningun CODCLI vigente exacto.                          |
| 17043569 | MU_LINEA_04072|RUT=17043569-9|S2C114M1J2V1 | SIN_MATCH      | Sede MU no coincide con el CODCLI vigente que respalda carrera/modalidad/jornada. |
| 18974966 | MU_LINEA_02001|RUT=18974966-K|S2C22M3J4V2  | SIN_MATCH      | COD_CAR MU no coincide con ningun CODCLI vigente exacto.                          |
| 18991836 | MU_LINEA_02010|RUT=18991836-4|S2C22M3J4V2  | SIN_MATCH      | COD_CAR MU no coincide con ningun CODCLI vigente exacto.                          |
| 20138827 | MU_LINEA_04074|RUT=20138827-9|S2C91M1J1V1  | SIN_MATCH      | Jornada MU no coincide con el CODCLI vigente disponible.                          |
| 21048839 | MU_LINEA_04075|RUT=21048839-1|S2C115M1J2V1 | SIN_MATCH      | Sede MU no coincide con el CODCLI vigente que respalda carrera/modalidad/jornada. |

## Controles

| control                             | valor |
| ----------------------------------- | ----- |
| CODCLI_totales                      | 4653  |
| CODCLI_vigentes                     | 3473  |
| CODCLI_historicos                   | 1086  |
| CODCLI_ambiguos                     | 94    |
| CODCLI_sin_evidencia                | 0     |
| CODCLI_para_otra_oferta             | 46    |
| CODCLI_duplicados                   | 0     |
| total_conciliado                    | 4653  |
| diferencia_conciliacion             | 0     |
| unidad_real_Casos_OK                | RUT   |
| cantidad_recalculada_Casos_OK       | 2000  |
| revisiones_reales_ANIO_ING_ORI      | 432   |
| revisiones_reales_NIV_ACA           | 1102  |
| revisiones_reales_COD_CAR           | 36    |
| revisiones_reales_MODALIDAD         | 2     |
| revisiones_reales_JOR               | 3     |
| RUT_multivigentes_revisados         | 34    |
| matches_ambiguos_revisados          | 6     |
| matches_resueltos                   | 6     |
| matches_pendientes                  | 0     |
| errores_mezcla_confirmados          | 0     |
| casos_OK_cerrados_RUT               | 2000  |
| revisiones_manuales_reales          | 1575  |
| duplicados_RUT_CODCLI_LLAVE_MU      | 0     |
| revisiones_datos_personales_menores | 0     |
| cambios_automaticos                 | 0     |
