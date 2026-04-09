# Correccion final de completitud y validacion PES

Estado final: BLOQUEADO_POR_NACIONALIDAD_INCOMPLETA
Archivo final revisado: /Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/ejecuciones/RECONSTRUCCION_FINAL_EXTRANJEROS_2025_20260625_235455/09_PES/EXTRANJEROS_REGULARES_2025_FINAL_PES_HOJA2.csv
Hash archivo final revisado: 235edaf7363466d8cec6420c00ac8eb56067f3ddd3e82736e33670d2131670b2
Nacionalidades encontradas: 103
Nacionalidades mapeadas al Anexo III: 103
Nacionalidades aplicadas: 0
Nacionalidades no aplicadas por codigo 38: 103
Conflictos: 0
TIPO_RESIDENCIA vacios: 185
PAIS_DE_ORIGEN vacios: 185
Controles ejecutados: 3700
Cambios no gobernados: 0
Errores bloqueantes: 104
VIGENCIA 0: 24
VIGENCIA 1: 161
PES READY: NO_GENERADO

## Resultado por columna

| POSICION | COLUMNA | FILAS | VACIOS | NO_VACIOS | VALORES_UNICOS | COINCIDENCIAS_CON_PRECARGA | DIFERENCIAS | CAMBIOS_GOBERNADOS | TRANSFORMACIONES_TECNICAS | CAMBIOS_NO_GOBERNADOS | ERRORES_DOMINIO | ERRORES_OBLIGATORIEDAD | RESULTADO |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | TIPO_DOCUMENTO | 185 | 0 | 185 | 2 | 185 | 0 | 0 | 0 | 0 | 0 | 0 | OK |
| 2 | NUM_DOCUMENTO | 185 | 0 | 185 | 185 | 185 | 0 | 0 | 0 | 0 | 0 | 0 | OK |
| 3 | DV | 185 | 25 | 160 | 12 | 185 | 0 | 0 | 0 | 0 | 0 | 0 | OK |
| 4 | PRIMER_APELLIDO | 185 | 0 | 185 | 158 | 185 | 0 | 0 | 0 | 0 | 0 | 0 | OK |
| 5 | SEGUNDO_APELLIDO | 185 | 11 | 174 | 141 | 185 | 0 | 0 | 0 | 0 | 0 | 0 | OK |
| 6 | NOMBRES | 185 | 0 | 185 | 183 | 185 | 0 | 0 | 0 | 0 | 0 | 0 | OK |
| 7 | SEXO | 185 | 0 | 185 | 2 | 185 | 0 | 0 | 0 | 0 | 0 | 0 | OK |
| 8 | FECHA_NACIMIENTO | 185 | 0 | 185 | 183 | 185 | 0 | 0 | 0 | 0 | 0 | 0 | OK |
| 9 | NACIONALIDAD | 185 | 104 | 81 | 11 | 185 | 0 | 0 | 0 | 0 | 0 | 104 | ERROR |
| 10 | TIPO_RESIDENCIA_ESTUDIANTE | 185 | 185 | 0 | 1 | 185 | 0 | 0 | 0 | 0 | 0 | 0 | OK |
| 11 | PAIS_DE_ORIGEN | 185 | 185 | 0 | 1 | 185 | 0 | 0 | 0 | 0 | 0 | 0 | OK |
| 12 | PAIS_ESTUDIOS_SECUNDARIOS | 185 | 0 | 185 | 11 | 185 | 0 | 0 | 0 | 0 | 0 | 0 | OK |
| 13 | CODIGO_UNICO | 185 | 0 | 185 | 39 | 185 | 0 | 0 | 0 | 0 | 0 | 0 | OK |
| 14 | ANIO_INGRESO_CARRERA_ACTUAL | 185 | 0 | 185 | 5 | 185 | 0 | 0 | 0 | 0 | 0 | 0 | OK |
| 15 | SEM_INGRESO_CARRERA_ACTUAL | 185 | 0 | 185 | 2 | 185 | 0 | 0 | 0 | 0 | 0 | 0 | OK |
| 16 | ANIO_INGRESO_CARRERA_ORIGEN | 185 | 0 | 185 | 7 | 185 | 0 | 0 | 0 | 0 | 0 | 0 | OK |
| 17 | SEM_INGRESO_CARRERA_ORIGEN | 185 | 0 | 185 | 3 | 185 | 0 | 0 | 0 | 0 | 0 | 0 | OK |
| 18 | NOMBRE_UNIVERSIDAD_ORIGEN | 185 | 185 | 0 | 1 | 185 | 0 | 0 | 0 | 0 | 0 | 0 | OK |
| 19 | PAIS_UNIVERSIDAD_ORIGEN | 185 | 185 | 0 | 1 | 185 | 0 | 0 | 0 | 0 | 0 | 0 | OK |
| 20 | VIGENCIA | 185 | 0 | 185 | 2 | 161 | 24 | 24 | 0 | 0 | 0 | 0 | OK |
