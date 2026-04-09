# Reporte gobernanza columna por columna Extranjeros Regulares 2025

Fecha: 2026-06-24T18:01:33

## Estructura oficial

- Archivo: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/20260602_97636_Estructura_Extranjeros_Regulares_2025.csv`
- Hash SHA-256: `dfa2262abddd3bf2489cdcd6d2e5f4e95863325b8f0de3e407d9f6e0857528c2`
- Delimitador: `;`
- Codificacion: `utf-8`
- Columnas oficiales: 20
- Orden: 1. TIPO_DOCUMENTO; 2. NUM_DOCUMENTO; 3. DV; 4. PRIMER_APELLIDO; 5. SEGUNDO_APELLIDO; 6. NOMBRES; 7. SEXO; 8. FECHA_NACIMIENTO; 9. NACIONALIDAD; 10. TIPO_RESIDENCIA_ESTUDIANTE; 11. PAIS_ORIGEN; 12. PAIS_ESTUDIOS_SECUNDARIOS; 13. CODIGO_UNICO; 14. ANIO_INGRESO_CARRERA_ACTUAL; 15. SEM_INGRESO_CARRERA_ACTUAL; 16. ANIO_INGRESO_CARRERA_ORIGEN; 17. SEM_INGRESO_CARRERA_ORIGEN; 18. NOMBRE_UNIVERSIDAD_ORIGEN; 19. PAIS_UNIVERSIDAD_ORIGEN; 20. VIGENCIA

## Aptitud de registros

- APTO: 0
- APTO_CON_ADVERTENCIAS: 0
- NO_APTO_DATOS_FALTANTES: 0
- NO_APTO_CONFLICTOS: 3
- PENDIENTE_INSTITUCIONAL: 59

## Principales brechas por columna

- TIPO_RESIDENCIA_ESTUDIANTE: pendientes 62, conflictos 0, invalidos 0, cobertura 0.00%.
- PAIS_ORIGEN: pendientes 62, conflictos 0, invalidos 0, cobertura 0.00%.
- CODIGO_UNICO: pendientes 26, conflictos 0, invalidos 0, cobertura 58.06%.
- ANIO_INGRESO_CARRERA_ORIGEN: pendientes 14, conflictos 0, invalidos 0, cobertura 77.42%.
- SEXO: pendientes 12, conflictos 0, invalidos 0, cobertura 80.65%.
- PAIS_ESTUDIOS_SECUNDARIOS: pendientes 12, conflictos 0, invalidos 0, cobertura 80.65%.
- SEM_INGRESO_CARRERA_ORIGEN: pendientes 12, conflictos 0, invalidos 0, cobertura 80.65%.
- TIPO_DOCUMENTO: pendientes 0, conflictos 3, invalidos 0, cobertura 95.16%.

## Pendientes institucionales visibles

- Nacionalidad pendiente: 1
- Vigencia/evidencia 2025 pendiente: 3
- Codigo unico pendiente: 26
- Pais origen pendiente: 62
- Pais estudios secundarios pendiente: 12

## Archivos creados

- Esquema: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/config/ESQUEMA_OFICIAL_EXTRANJEROS_REGULARES_2025.tsv`
- Diccionario: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/config/DICCIONARIO_GOBERNANZA_EXTRANJEROS_2025.tsv`
- TSV gobernados: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/data/governed/columnas_extranjeros_2025`
- Catalogos: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/data/governed/catalogos/TIPO_DOCUMENTO.tsv`, `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/data/governed/catalogos/TIPO_RESIDENCIA_ESTUDIANTE.tsv`, `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/data/governed/catalogos/NACIONALIDAD_SIES.tsv`
- Matriz: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/data/processed/MATRIZ_GOBERNANZA_EXTRANJEROS_2025.csv`
- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/GOBERNANZA_COLUMNAS_EXTRANJEROS_2025.xlsx`
- Cobertura columnas: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/COBERTURA_GOBERNANZA_COLUMNAS_EXTRANJEROS_2025.csv`
- Cobertura registros: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/COBERTURA_GOBERNANZA_REGISTROS_62.csv`
- Validacion: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/VALIDACION_GOBERNANZA_COLUMNAS_EXTRANJEROS_2025.csv`

## Hashes

- estructura: `dfa2262abddd3bf2489cdcd6d2e5f4e95863325b8f0de3e407d9f6e0857528c2`
- frozen_tsv: `da85dd0c453a942a4490f469b75d0418e9054e458a46028f44271ac704518081`
- matriz: `8ccaea1955492a46638c44cacb469d45e7eae5638b60bf224c3cb80f70a8e16b`
- excel: `3bf443a89f744afea4e59859942d44f156c95385ffb759df373b78604633c073`
- validacion: `89501de5e6e8a607a2280bb0573dc6eb6c0cf1b10ed00ebba9e9148741c0a7e2`

## Respaldo

`/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/backups/pre_gobernanza_columnas_extranjeros_20260624_180126`

## Validacion

- TSV congelado mantiene hash original: OK
- Base congelada mantiene 62 filas: OK
- Estructura oficial fue leida sin modificar: OK
- Esquema mantiene orden exacto oficial: OK
- Existe un TSV por cada columna oficial: OK
- Cada TSV gobernado contiene exactamente 62 filas: OK
- No existen duplicados de FILA_BASE_CONGELADA: OK
- No se eliminan columnas originales: OK
- No se completa nacionalidad desde RUT: OK
- Codigo 38 se identifica como Chile: OK
- No se infiere pais de origen: OK
- No se infiere pais de estudios secundarios: OK
- Ano informado corresponde a 2025: OK
- Vigencia no se define desde matricula 2026: OK
- No se selecciona automaticamente la primera coincidencia: OK
- Los 18 registros pendientes permanecen visibles: OK
- Los 14 empates de coincidencia permanecen visibles: OK
- Caso de nacionalidad pendiente permanece visible: OK
- Tres casos de evidencia parcial permanecen visibles: OK
- Matriz de gobernanza contiene 62 filas: OK
- Ningun registro pendiente queda marcado como APTO: OK
- No existen errores Excel: OK
- No se genera archivo final PES: OK

## Estado git

```
M README.md
?? backups/pre_gobernanza_columnas_extranjeros_20260624_174927/MANIFIESTO_RESPALDO_PRE_GOBERNANZA_COLUMNAS.sha256
?? backups/pre_gobernanza_columnas_extranjeros_20260624_174927/README.md
?? backups/pre_gobernanza_columnas_extranjeros_20260624_174927/scripts/cerrar_pendientes_base_62.py
?? backups/pre_gobernanza_columnas_extranjeros_20260624_174927/scripts/conciliar_base_congelada_62_vs_257.py
?? backups/pre_gobernanza_columnas_extranjeros_20260624_175958/README.md
?? backups/pre_gobernanza_columnas_extranjeros_20260624_175958/scripts/gobernar_columnas_extranjeros_2025.py
?? backups/pre_gobernanza_columnas_extranjeros_20260624_180026/README.md
?? backups/pre_gobernanza_columnas_extranjeros_20260624_180026/scripts/gobernar_columnas_extranjeros_2025.py
?? backups/pre_gobernanza_columnas_extranjeros_20260624_180126/README.md
?? backups/pre_gobernanza_columnas_extranjeros_20260624_180126/resultados/reportes/REPORTE_GOBERNANZA_COLUMNAS_EXTRANJEROS_2025.md
?? backups/pre_gobernanza_columnas_extranjeros_20260624_180126/scripts/gobernar_columnas_extranjeros_2025.py
?? resultados/reportes/REPORTE_GOBERNANZA_COLUMNAS_EXTRANJEROS_2025.md
?? scripts/gobernar_columnas_extranjeros_2025.py
```
