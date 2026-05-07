# Resumen PES_READY MU2026

Fecha ejecución: 2026-05-08 23:09:00

## Conteo general

- Filas iniciales: 4115
- Filas corregidas: 473
- Filas excluidas: 45
- Filas finales: 4070

## Correcciones por regla

- REGLA_1_SIT_FON_SOL: 0
- REGLA_2_FOR_DIRECTO_ORIGEN: 0
- REGLA_3_FOR_23_ORIGEN_1900: 471
- REGLA_4_FOR_23_ASI_INS_HIS: 10
- REGLA_5_ASI_INS_ANT_CERO: 1
- REGLA_VIG0_NOMINA_FORZADOS: 289
- REGLA_VIG0_NOMINA_YA_CERO: 463

## Exclusiones por motivo

- REGLA_6_RUT_MAYOR_8: 41
- REGLA_7_EDAD_MENOR_15_ACT: 2
- REGLA_7_EDAD_MENOR_15_ORI: 2
- REGLA_8_OFERTA_INEXISTENTE: 0
- REGLA_9_NIV_ACA_GT_DURACION: 1
- REGLA_10_QM_2025: 0
- REGLA_11_EXCLUSION_AUDITADA: 2

## Validaciones finales

- SIT_FON_SOL distinto de 0: 0
- FOR_ING_ACT 1,2,3,6,7,8,9,10 con ANIO_ING_ORI=1900: 0
- FOR_ING_ACT 1,6,7,8,9,10 con ORI != ACT: 0
- FOR_ING_ACT 2 o 3 con ASI_INS_HIS=0: 0
- ASI_APR_HIS > ASI_INS_HIS: 0
- TIPO_DOC=R con N_DOC mayor a 8 dígitos: 0
- FOR_ING_ACT 2 o 3 con año origen = año actual y semestre origen >= actual: 0
- filas con cantidad de campos distinta de 32: 0
- archivo sin encabezado: True
- ruta archivo final resultados: /Users/alexi/Documents/GitHub/avance_curricular/resultados/matricula_unificada_2026_pregrado_PES_READY.csv
- ruta copia Escritorio: /Users/alexi/Desktop/matricula_unificada_2026_pregrado_PARA_SUBIR.csv
- estado copia: OK
- fuente local regla 10: SIN_FUENTE_LOCAL_TRAZABLE

## Verificación de estudiantes excluidos

- CSV verificación: /Users/alexi/Documents/GitHub/avance_curricular/resultados/verificacion_exclusiones_pes_ready_20260508_230900.csv
- Excluidos: 45
  - Edad menor a 15 años respecto de ANIO_ING_ACT: 1
  - Exclusión auditada por control/exclusiones_pes_mu2026.tsv: 2
  - NIV_ACA mayor que duración de carrera: 1
  - RUT tipo R con más de 8 dígitos: 41

## Auditorías

- /Users/alexi/Documents/GitHub/avance_curricular/resultados/auditoria_correcciones_pes_ready_20260508_230900.csv
- /Users/alexi/Documents/GitHub/avance_curricular/resultados/auditoria_exclusiones_pes_ready_20260508_230900.csv