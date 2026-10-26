# V16: bases de cálculo de tres tasas 2026

Solicitud: revisar H11, F12 y H14 de `18_Foto_Intertrimestral`, explicar diferencias y corregir la presentación/fórmulas sin cambiar bases ni denominadores. Se conserva V15; no se autoriza commit ni push.

## Evidencia y decisión de implementación

- B/C: el original `RETENCION_IPSS_FINAL_con_Foto_Intertrimestral_20261022_AUDITADO_ENTREGA.xlsx` conserva las fórmulas de estas tres tasas. V15 conserva los resultados como constantes; no se observó un error de división.
- B/C, regla D: H11 usa 1.360/1.467. La población original es 1.471 y se excluyen cuatro `NO APLICA`, todas `TITULADO / 31 - TITULADO APROBADO`. H14 deduplica personas y usa 2.290/2.519 sobre una población original de 2.523; las mismas cuatro exclusiones. Fuente: hoja20 B/C/P/Q/R/T y hoja25 J/K/M; regla en hoja21 B3/B31:E31. No constituye norma SIES nueva.
- B/C: F12 usa 462/528 matrículas. El listado original contiene 528 CODCLI y 527 personas; 66 renuncias agregadas. Fuente: `Matrícula T_2_13_07_2026.xlsx`, Hoja1 y Hoja2 B32:C50; hoja23 C6:F24 del libro. Dividir 462/527 mezclaría unidades.
- C: añadir al final de la hoja18 un bloque visible con población original, exclusiones, base de la tasa, vigentes, tasa y unidad. Reponer fórmulas en las tres celdas; mantener sus resultados. La base T1 elegible se reutiliza de hoja53. La exclusión total única se registra como agregado observado del original, sin identificadores.
- E: no se dispone en este cálculo de renuncias individuales que permitan convertir la tasa de matrículas T2 en una tasa de personas. No se calcula esa alternativa.

## Preservación y QA

No cambiar las columnas de población, numeradores, bases individuales, diccionario, reglas ni tasas fuera de estas tres celdas. Justificación de `scripts/` y `outputs/`: convención operativa de V13–V15, derivado separado y reproducible. Autoría mediante Artifact Tool y extracción mínima de celdas OOXML para preservar las demás partes, tablas, gráficos y estilos. Probar sumas, divisiones y dependencias mediante perturbaciones solo en memoria. Contrastar el agregado con el original; verificar 54 hojas, 13 gráficos, 35 tablas y fuentes por hash. Abrir en Excel nativo sin reparación. Entregar una V16 y copia idéntica en Escritorio, más manifiesto y evidencia agregada locales.
