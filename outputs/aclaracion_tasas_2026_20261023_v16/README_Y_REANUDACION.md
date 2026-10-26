# V16 · Tasas 2026 de la hoja 18

B/C: se reprodujeron las tres tasas a partir del original auditado y las bases de cálculo vigentes. No se encontró una división incorrecta. V15 había conservado estos resultados como constantes tras la agregación; V16 devuelve fórmulas trazables y hace explícitas las unidades y exclusiones en B91:I97.

| Celda | Población visible | Base efectiva | Numerador | Tasa | Respaldo |
|---|---:|---:|---:|---:|---|
| H11 | 1.471 personas | 1.467 personas elegibles | 1.360 | 92,706203 % | B/C; cuatro titulados excluidos según D existente |
| F12 | 527 personas | 528 matrículas | 462 | 87,5 % | B/C; 528 matrículas menos 66 renuncias |
| H14 | 2.523 personas únicas | 2.519 personas elegibles | 2.290 | 90,909091 % | B/C; mismas cuatro exclusiones D, deduplicación anual |

D: la exclusión NO APLICA de TITULADO / 31 - TITULADO APROBADO ya está declarada en la hoja 21 y las notas originales. Se preservó; este trabajo no la presenta como norma SIES.

E: para transformar el indicador T2 de matrículas en uno de personas hacen falta renuncias individuales. No se infiere esa tasa ni se cambia 528 por 527. Las tres tasas revisadas conservan sus valores. Los otros pendientes de V15 permanecen fuera de este alcance.

## Reproducción y controles

C: ejecutar el script Python `aclarar_tasas_2026_v16_20261023.py prepare`; autoría con `editar_tasas_2026_v16_20261023.mjs <salida> edit`; ensamblar con Python `finish`; verificar dinámica con Node `qa`; abrir el resultado en Excel y registrar QA_EXCEL_NATIVO.json antes de Python `close`. Se usan las dependencias del runtime de Codex y las rutas/hashes de EDICION.json. La fuente individual se lee solo en memoria y solo se persisten agregados.

C: los cambios se limitan a tres fórmulas preexistentes y al nuevo bloque B91:I97. Las otras 53 hojas, 13 gráficos, 35 tablas y estilos mantienen sus bytes originales. Los valores previos y denominadores no cambiaron. Se probaron las dependencias con cambios temporales en memoria, incluido denominador cero. El archivo final abrió en Excel sin aviso de reparación. El primer intento de ensamblaje tenía celdas nuevas fuera de orden; se corrigió y se agregó control estricto de orden y duplicados antes de la entrega.

C: el QA se limita a estas tasas y a la preservación del resto; no equivale a una nueva auditoría funcional de las 54 hojas ni al cierre de pendientes históricos. No se guardó el libro desde Excel: se conservó la estructura del derivado verificado.

## Checkpoint

C: V16 lista para revisión local. Bases, numeradores, denominadores, porcentajes y diccionario conservados. Copia del Escritorio idéntica. Sin commit, push ni publicación de datos personales. Evidencia agregada y hashes en MANIFEST_TASAS_2026_V16.json. Si se cambia a futuro la unidad o la regla de exclusión, será otra decisión explícita y otra versión; no debe aplicarse silenciosamente.
