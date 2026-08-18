# Alerta — Conciliación por clave inválida

## Estado

- Estado: CONCILIACION_INVALIDA_POR_ESTRUCTURA.
- Fecha de identificación: 20260817_171923.
- Archivo resumen afectado: oferta_academica_2027/11_gobernanza/historico_oferta_academica/RESUMEN_CONCILIACION_POR_CLAVE_SIES_162_20260817_171649.tsv.
- Archivo detalle afectado: oferta_academica_2027/11_gobernanza/historico_oferta_academica/DETALLE_CONCILIACION_POR_CLAVE_SIES_162_20260817_171649.tsv.

## Motivo

La homologación de columnas entre el histórico comparativo SIES y las fuentes internas no fue válida.

Evidencia:

- Las claves del histórico aparecen con COD_SEDE y COD_CARRERA vacíos.
- Se obtuvieron cero claves compartidas en todos los períodos.
- El resultado contradice diagnósticos anteriores que sí detectaron solapamiento.
- Por lo tanto, los conteos SOLO_SIES y SOLO_INTERNO de esta ejecución no representan discrepancias de negocio.

## Regla

Estos archivos no deben utilizarse para:

- declarar carreras faltantes;
- declarar diferencias reales de oferta;
- corregir fuentes;
- generar KPI históricos;
- modificar la matriz de precedencia.

## Acción requerida

Rehacer la conciliación desde las fuentes originales, utilizando una homologación explícita de columnas y verificando antes:

1. que COD_SEDE y COD_CARRERA estén llenos;
2. que la cantidad de claves únicas sea razonable;
3. que la clave relajada produzca coincidencias;
4. que los conteos coincidan con los diagnósticos previos antes de emitir alertas.

## Estado de las alertas reales

Se mantienen provisionalmente solo las diferencias agregadas ya gobernadas:

- OFE_2023: SIES 70 versus interno 77.
- OFE_2024: SIES 77 versus interno 76.
- OFE_2026: SIES 124 versus interno 89.

Estas diferencias siguen pendientes de una conciliación válida por clave.
