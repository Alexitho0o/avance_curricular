# Recuperación PES-ready Posgrado/Postítulo MU2026

## Resultado
Se localizó el archivo original PES-ready sin encabezados en el historial Git local del proyecto.

- Archivo: `matricula_unificada_2026_postgrado_postitulo.csv`
- Ruta original: `git:4f1108c:resultados/matricula_unificada_2026_postgrado_postitulo.csv`
- Clasificación: `ARCHIVO_ORIGINAL_PES_READY_LOCALIZADO`
- Ruta gobernada: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/congelados_matricula_unificada_2026/posgrado_postitulo/20260730_172147/matricula_unificada_2026_postgrado_postitulo.csv`
- Hash SHA-256: `a0dbff084d6b448d3443bbd68c5efd45c77b499e5ef91bb145dc8ba0d9b80111`

## Tabla de candidatos
| Archivo candidato | Ruta | Filas | Campos | Encabezado | Delimitador | Codificación | SHA-256 | Evidencia | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| matricula_unificada_2026_postgrado_postitulo.csv | git:4f1108c:resultados/matricula_unificada_2026_postgrado_postitulo.csv (blob 3e44d69adc25cab16958c4317d16306b0e9eab20) | 54 | 21 | NO | ; | utf-8 | a0dbff084d6b448d3443bbd68c5efd45c77b499e5ef91bb145dc8ba0d9b80111 | Reporte generación preliminar y cierre posterior; archivo PES-ready sin encabezado. | SELECCIONADO_PES_READY |
| matricula_unificada_2026_postgrado_postitulo_CON_TITULOS.csv | git:4f1108c:resultados/matricula_unificada_2026_postgrado_postitulo_CON_TITULOS.csv (blob 1c1d4833b5dc5637b0c1670b5823c8aab4683f93) | 55 | 21 | SI | ; | utf-8-sig | 0cd4c6343dbd886e259db5f86ecff70a08840d2b556bc398543711b66a94608a | Archivo con títulos de 54 registros usado como referencia de contenido. | ARCHIVO_CON_TITULOS |
| matricula_unificada_2026_postgrado_postitulo_CON_TITULOS_bkp_20260521_213650.csv | git:4f1108c:resultados/matricula_unificada_2026_postgrado_postitulo_CON_TITULOS_bkp_20260521_213650.csv (blob bfb4b20f1b9ef27ef31f3b12a02969d8a63f6631) | 56 | 21 | SI | ; | utf-8-sig | 660da697b4c0a0e4e4c8855b05e2419a6b3871242ce395dbf27fcd3a179e2ae6 | Respaldo con títulos previo a exclusión final; contiene 55 registros más encabezado. | ARCHIVO_CON_TITULOS |
| matricula_unificada_2026_postgrado_postitulo_PES_READY_FOR_ING_ACT_MODALIDAD_JOR_CORREGIDO_bkp_20260521_213650.csv | git:4f1108c:resultados/matricula_unificada_2026_postgrado_postitulo_PES_READY_FOR_ING_ACT_MODALIDAD_JOR_CORREGIDO_bkp_20260521_213650.csv (blob 78d8f47c9a8774567e8bd8c9722e6dc39bb543d5) | 55 | 21 | NO | ; | utf-8 | 40d8bdb97623be58ec9af66651e681ee397802143681bbbfb9268d5fe23103ca | Respaldo PES-ready corregido antes de excluir registro bloqueado; 55 filas. | SUPERADO |
| matricula_unificada_2026_postgrado_postitulo_CONTROL_FINAL.csv | git:4f1108c:resultados/matricula_unificada_2026_postgrado_postitulo_CONTROL_FINAL.csv (blob 285ad4aa94ee88026efa19a36b3daec6c788ed30) | 56 | 32 | NO | , | utf-8-sig | ec07e354f5617b65fd1b873f17323573ee085df3dd0cbdea65d1a7b92aa7aafc | Control final con columnas de auditoría; no es archivo de carga PES-ready. | NO_CORRESPONDE |
| reconciliacion_66_a_54_postgrado.csv | git:4f1108c:resultados/reconciliacion_66_a_54_postgrado.csv (blob 162a103919fb12c27af99f749e3c54776d3424ad) | 67 | 29 | NO | , | utf-8-sig | 42ae52a7ea64fd17e8345fbe26fa0b9e68432d73e9c301e31aa04e30a7529192 | Reconciliación 66 a 54; evidencia derivada, no archivo de carga. | NO_CORRESPONDE |

## Comparación con archivo con títulos
| Validación | Resultado |
| --- | --- |
| Filas archivo con títulos, sin contar encabezado | 54 |
| Filas archivo PES-ready | 54 |
| Campos por fila | 21 |
| Mismo orden de filas | SI |
| Mismo orden de columnas | SI |
| Valores idénticos | SI |
| Diferencias encontradas | 0 |
| Hash del archivo con títulos | `0cd4c6343dbd886e259db5f86ecff70a08840d2b556bc398543711b66a94608a` |
| Hash del archivo sin títulos | `a0dbff084d6b448d3443bbd68c5efd45c77b499e5ef91bb145dc8ba0d9b80111` |

## Evidencia de cierre
- `generacion_pes_postgrado_postitulo_20260508_090807.md` declara el PES-ready sin encabezado, delimitado por punto y coma.
- `resumen_cierre_rut_invalido_postgrado_20260521_213650` documenta `filas_pes_ready_despues=54`, exclusión del registro bloqueado y `copia_escritorio=OK`.
- `reconciliacion_66_a_54_postgrado_20260521_215748` documenta `incluidos_pes_ready=54` y reconciliación matemática verdadera.

## Archivos actualizados
- Excel integral con PES-ready: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/comparaciones_publicacion2026_integrales/20260730_172147/COMPARACION_INTEGRAL_PUBLICACION2026_VS_CONGELADOS_PREGRADO_POSGRADO_2026_CON_PES_READY_20260730_172147.xlsx`
- Manifest: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/comparaciones_publicacion2026_integrales/20260730_172147/MANIFEST_COMPARACION_INTEGRAL_PUBLICACION2026_PREGRADO_POSGRADO_CON_PES_READY_20260730_172147.json`

## Estado del pendiente
`PES_READY_POSGRADO_NO_MATERIALIZADO` -> `RESUELTO_ARCHIVO_ORIGINAL_LOCALIZADO`.
