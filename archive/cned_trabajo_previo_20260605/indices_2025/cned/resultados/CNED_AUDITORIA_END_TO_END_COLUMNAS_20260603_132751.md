# CNED — Auditoría end to end por columna del artefacto operativo limpio

## Dictamen
CNED_DOCUMENTO_CREADO_Y_AUDITADO_POR_COLUMNA_SIN_ERRORES

## Baseline Git
- Rama: clean/pes-ready-final
- HEAD local: 4caf70b
- HEAD remoto: 4caf70b
- Estado limpio en Fase 0: sí
- Estado Git antes de crear este informe: sí
- Commit del script canónico: 4caf70b fix: canonicalize clean CNED materializer script

## Archivos auditados
- Script canónico: indices_2025/cned/scripts/06_materializar_artefacto_operativo_cned_limpio.py
- Excel oficial 110249: indices_2025/cned/resultados/CNED_ARTEFACTO_OPERATIVO_LIMPIO_20260603_110249.xlsx
- Último Excel generado: indices_2025/cned/resultados/CNED_ARTEFACTO_OPERATIVO_LIMPIO_20260603_132333.xlsx
- CSV operativo: indices_2025/cned/data/BASE_CNED_LIMPIA_OPERATIVA.csv
- TSV manual: indices_2025/cned/data/DATOS_VALIDACION_CNED_TSV_NUEVO_MANUAL.tsv
- Último Markdown generado por el script: indices_2025/cned/resultados/CNED_ARTEFACTO_OPERATIVO_LIMPIO_20260603_132333.md

## Resultado de ejecución
- Compilación del script: OK
- Ejecución del script: OK
- Creó Excel: sí
- Creó Markdown: sí
- Mantuvo CSV operativo: sí
- Dictamen impreso por el script: BASE_CNED_LIMPIA_LISTA_PARA_USO_OPERATIVO

## Auditoría por hoja
- RESUMEN_LIMPIEZA: oficial 61 filas / 4 columnas; latest 61 filas / 4 columnas.
- BASE_CNED_LIMPIA: oficial 59 filas / 26 columnas; latest 59 filas / 26 columnas.
- SIN_CODIGO_SIES: oficial 7 filas / 64 columnas; latest 7 filas / 64 columnas.
- DUPLICADOS_CNED: oficial 1 filas / 4 columnas; latest 1 filas / 4 columnas.

## Auditoría por columna de BASE_CNED_LIMPIA
| Columna | Vacíos | Únicos | Obligatoria | Resultado |
|---|---:|---:|---|---|
| Año | 0 | 7 | Sí | OK |
| Cód. Institución | 0 | 1 | Sí | OK |
| Nombre Institución | 0 | 1 | Sí | OK |
| Nombre de la Sede | 0 | 1 | Sí | OK |
| Comuna donde se imparte la carrera o programa | 0 | 1 | Sí | OK |
| Cód. Carrera | 0 | 59 | Sí | OK |
| Carrera Genérica | 0 | 21 | Sí | OK |
| Nombre Programa | 0 | 30 | Sí | OK |
| Horario | 0 | 3 | Sí | OK |
| Tipo Programa | 0 | 2 | Sí | OK |
| Tipo Carrera | 0 | 2 | Sí | OK |
| IngresoDirecto | 0 | 2 | Sí | OK |
| Año Inicio Actividades | 0 | 12 | Sí | OK |
| Duración (en semestres) | 0 | 4 | Sí | OK |
| Cód. Campus | 17 | 2 | No | REVISAR |
| Cód. Sede | 0 | 1 | Sí | OK |
| Título | 0 | 33 | Sí | OK |
| Código SIES | 0 | 57 | Sí | OK |
| Pregrado/Posgrado | 0 | 1 | Sí | OK |
| COD_SED_DERIVADO | 0 | 1 | Sí | OK |
| COD_CAR_DERIVADO | 0 | 23 | Sí | OK |
| JOR_DERIVADA | 0 | 3 | Sí | OK |
| VERSION_DERIVADA | 0 | 4 | Sí | OK |
| CLAVE_OPERATIVA | 0 | 59 | Sí | OK |
| VALIDACION_CODIGO_UNICO | 0 | 1 | Sí | OK |
| VALIDACION_COD_CARRERA | 0 | 1 | Sí | OK |

## Validaciones de negocio
- Código SIES: 59 con formato válido; 0 inválidos.
- Derivados desde Código SIES: {'COD_SED_DERIVADO': 0, 'COD_CAR_DERIVADO': 0, 'JOR_DERIVADA': 0, 'VERSION_DERIVADA': 0}
- CLAVE_OPERATIVA: 59 únicas.
- Horario vs JOR: 0 errores.
- Pregrado/Posgrado: {'Pregrado': 59}
- VALIDACION_CODIGO_UNICO: {'OK': 59}
- VALIDACION_COD_CARRERA: {'REVISAR_COD_CARRERA': 59}
- SIN_CODIGO_SIES: 7 filas; Código SIES vacíos = 7; MOTIVO_REVISION = {'SIN_CODIGO_SIES': 7}
- DUPLICADOS_CNED: 1 filas de trazabilidad.

## Comparaciones cruzadas
- CSV vs Excel: OK
- Excel oficial vs Excel generado: OK
- TSV manual no usado: OK

## Riesgos residuales
- VALIDACION_COD_CARRERA es advertencia no bloqueante porque Cód. Carrera CNED y COD_CAR_DERIVADO son códigos de naturaleza distinta.
- El TSV manual sigue con 0 filas y no debe usarse como insumo automático.
- Los Markdown timestamped generados en runtime pueden quedar como residuos locales si no están ignorados.

## Cierre
- No se detectaron cambios versionados sobre artefactos de pregrado ni PES_READY: sí.
- TSV manual no actualizado durante esta corrida: sí.
- No se mezcló SIN_CODIGO_SIES con BASE_CNED_LIMPIA: sí.
- La base operativa queda lista para uso controlado: sí.
