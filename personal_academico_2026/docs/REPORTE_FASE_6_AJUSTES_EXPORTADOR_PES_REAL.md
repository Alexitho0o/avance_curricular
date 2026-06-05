# Reporte Fase 6 - Ajustes Exportador PES Real

## Errores Observados En PES/SIES
- CSV con coma fue leido como 1 campo; para esta carga PES/SIES acepto separador punto y coma.
- Fechas `YYYY-MM-DD` fueron rechazadas; PES acepto fechas en `DD-MM-AAAA`.
- Reporte PES mostro problemas de codificacion con tildes.
- `COMUNA_MAYOR_FUNCION` vacia fue rechazada.
- Persisten rechazos por valores no disponibles en campos estructurados y horas con decimales largos.

## Ajustes Incorporados Al Codigo
- Delimitador final configurable y por defecto `punto_coma`.
- Encoding de salida configurable y por defecto `cp1252`.
- Fechas PES en `DD-MM-AAAA`.
- Normalizacion tecnica de exportacion: mayusculas, sin tildes, sin espacios dobles y sin separadores internos conflictivos.
- Completar `COMUNA_MAYOR_FUNCION` desde `COMUNA_PRINCIPAL_PROGRAMA` solo en exportacion.
- Modo explicito `--excluir-registros-no-cargables true`.
- Horas numericas a maximo 2 decimales.

## Base General
La base general original no fue modificada. Las transformaciones son solo de exportacion.

## Exclusiones
Las exclusiones se aplican solo si se usa `--excluir-registros-no-cargables true`.
- FECHA_OBT_TIT_O_GRADO=VALOR_NO_CARGABLE: 7
- NIVEL_FORMACION_ACADEMICO=VALOR_NO_CARGABLE: 5
- PAIS_OBTENCION_TIT_O_GRADO=VALOR_NO_CARGABLE: 7

## Archivo Generado
- Salida modulo: personal_academico_2026/resultados/personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO.csv
- Copia Escritorio: /Users/alexi/Desktop/personal_academico_en_institucion_2026_PES_READY.csv
- Filas exportadas: 181
- Filas excluidas: 8
- Delimitador: punto_coma
- Encoding: cp1252
- Encabezado: NO

## Auditorias
- Transformaciones: personal_academico_2026/auditorias/exportacion_controlada/auditoria_transformaciones_pes_fase7_20260612_005154.csv
- Exclusiones: personal_academico_2026/auditorias/exportacion_controlada/auditoria_exclusiones_pes_fase7_20260612_005154.csv

Advertencia: no se deben hacer correcciones manuales directas sobre el CSV final sin reflejarlas en codigo y auditoria.
