# Cierre PES_READY · Matrícula Unificada 2026

Fecha: 2026-05-07

El pipeline de Matrícula Unificada 2026 quedó ajustado para generar una versión PES_READY del archivo de carga.

## Resultado validado

- Archivo final en Escritorio: `/Users/alexi/Desktop/matricula_unificada_2026_pregrado_PARA_SUBIR.csv`
- Filas finales: 3402
- Columnas por fila: 32
- Encabezado: no
- Separador: punto y coma `;`
- Comparación contra archivo que pasó PES: sin diferencias por N_DOC

## Criterio aplicado

El archivo bruto `resultados/matricula_unificada_2026_pregrado.csv` se mantiene intacto.  
La versión depurada `matricula_unificada_2026_pregrado_PES_READY.csv` aplica correcciones y exclusiones auditadas para evitar rechazos PES observados.

## Exclusiones auditadas residuales

Se mantuvieron exclusiones por N_DOC+DV cuando no existía fuente local trazable para corregir sin inventar datos.

## Estado

El archivo PES_READY automático replica el criterio del archivo que logró carga completada en PES.
