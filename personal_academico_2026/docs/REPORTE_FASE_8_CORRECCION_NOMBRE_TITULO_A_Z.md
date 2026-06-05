# Reporte Fase 8 - Correccion NOMBRE_TITULO_O_GRADO A-Z

## Objetivo
Aplicar una regla especifica de exportacion para que `NOMBRE_TITULO_O_GRADO` contenga solo letras mayusculas `A-Z` y espacios simples, segun rechazo PES/SIES.

## Regla Incorporada
- Funcion: `normalizar_solo_letras_az_pes(valor)`.
- Campo aplicado: `NOMBRE_TITULO_O_GRADO`.
- Reemplaza cualquier caracter distinto de `A-Z` por espacio.
- Quita tildes y convierte `Ñ` a `N`.
- No modifica la base general original.

## Resultado
- Archivo repo: personal_academico_2026/resultados/personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO.csv
- Archivo Escritorio: /Users/alexi/Desktop/personal_academico_en_institucion_2026_PES_READY.csv
- Filas exportadas: 181
- Titulos corregidos: 81
- Auditoria transformaciones: personal_academico_2026/auditorias/exportacion_controlada/auditoria_transformaciones_pes_fase7_20260612_005154.csv
- Auditoria exclusiones: personal_academico_2026/auditorias/exportacion_controlada/auditoria_exclusiones_pes_fase7_20260612_005154.csv

La correccion queda en codigo y auditoria; no se hizo parche manual sobre el CSV final.
