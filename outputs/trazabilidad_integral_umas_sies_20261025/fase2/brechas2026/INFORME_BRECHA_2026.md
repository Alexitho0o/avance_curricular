# Fase 2/6 · Brecha 2026 y alcance de las fuentes

B/C — La diferencia de226 se reproduce por código completo, no solo en el total. Su causa individual permanece pendiente.

| Universo / criterio | Total | Respaldo |
|---|---:|---|
| MU pregrado: todas las filas |4.105|B: lectura agregada actual|
| MU pregrado: VIG=0 |960|B: lectura agregada actual|
| MU pregrado: VIG=1 |3.145|B: lectura agregada actual|
| MU pregrado: VIG=2 / otros |0 /0|B: lectura agregada actual|
| Publicación: Pregrado |3.371|B:63 códigos|
| Publicación: Postítulo |54|B: tres códigos; fuera de BASE pregrado|
| Publicación total |3.425|C:3.371+54|
| Institucional comparable del cierre de julio |3.199|C:3.145 pregrado+54 posgrado/postítulo de otra fuente|
| Brecha comparable |226|C:3.371−3.145; también3.425−3.199|

C — La fórmula inventariada de julio, `07_PREGRADO_COMPLETO!AM7`, usa `OR(VIG="1",VIG="2")`. La coincidencia con VIG=1 se debe a que VIG=2 es cero en esta base; no cambia la regla histórica.

B/C — El puente de198 filas contiene66 códigos en2026. Todos sus totales de publicación coinciden con el cierre de julio. Los63 códigos pregrado coinciden también en el institucional. Los tres Postítulos son C53J3V1=17, C66J4V1=15 y C70J4V1=22; en julio tienen fuente separada con21 columnas.

C — Al comparar toda la publicación con BASE pregrado surge280=226+54 de distinto alcance. No son54 faltantes nuevos. Al comparar Pregrado publicado con todas las filas MU surge−734=226−960: incluye filas VIG=0 y responde a otra comparación.

## Diferencias que siguen sin causa individual demostrada

B/C — Hay48 códigos pregrado con diferencias:46 positivos suman228; dos negativos suman−2. Los códigos solo publicación son I162S2C77J1V1 (1) e I162S2C87J4V1 (5). Los66 códigos completos están en DETALLE_66_CODIGOS_2026.csv.

B/C/E — Al agrupar por COD_CAR hay27 carreras con brecha neta y cinco con neto cero. Dos de esas cinco ocultan compensaciones:

| Carrera SIES | Código | Diferencia publicación−MU VIG1 | Respaldo |
|---|---|---:|---|
|6|I162S2C6J2V2|+1|B/C|
|6|I162S2C6J4V2|−1|B/C|
|79|I162S2C79J2V1|−1|B/C|
|79|I162S2C79J4V1|+1|B/C|

E — Estos patrones no prueban que una persona cambió de jornada o versión. El manifiesto del30-sep declara causas cerradas por agregación; aquí se conserva la reproducción de los números y se separa esa afirmación causal no acreditada. No se modifica el antecedente.

E — Los hashes de la fuente XLSX de julio y del esquema rector posterior son distintos. Se confirma igualdad de agregados pregrado por código, no igualdad binaria o individual. Publicación agregada no contiene la identidad necesaria para asignar una diferencia a una persona.

## Fuentes y localizadores

- B/C — MU pregrado 2026 contiene4105 filas:3145 VIG1+960 VIG0; VIG2 y otros son0. Fuente: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/trazabilidad_integral_umas_sies_20261025/fase2/conciliacion/DETALLE_CONCILIACION.csv`; `ANIO=2026; suma MU_TOTAL_FILAS/MU_VIG0_FILAS/MU_VIG1_FILAS/MU_VIG2_FILAS`.
- C — El comparador de julio acepta VIG1 o2; como no hay VIG2, coincide con filtrar VIG1. No implica equivalencia universal de ambos criterios. Fuente: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/lectura_independiente_libro_mu2026/20260730_232242/INVENTARIO_FORMULAS.csv`; `07_PREGRADO_COMPLETO!AM7; 11_RESUMEN_POR_CODIGO!L5`.
- B/C — Los66 códigos reproducen publicación de julio;63 pregrado reproducen institucional exactamente. No es solo igualdad del neto226. Fuente: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/lectura_independiente_libro_mu2026/20260730_232242/CRUCE_66_CODIGOS.csv`; `Todas las66 filas comparadas por CODIGO con puente y conciliación actual`.
- B/C — Tres Postítulos suman54; el cierre usa fuente propia de21 columnas. Los ceros en BASE pregrado son ausencia de alcance, no54 estudiantes faltantes. Fuente: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/auditoria_integral_publicacion_vs_pregrado_posgrado_2026/20260730_223007/MANIFEST_AUDITORIA_INTEGRAL_MU2026_PUBLICACION_PREGRADO_POSGRADO_20260730_223007.json`; `fuentes POS_CSV/POS_TIT; CRUCE códigos C53J3V1,C66J4V1,C70J4V1`.
- B/C — 48 códigos pregrado difieren:46 positivos suman228 y2 negativos suman−2; neto226. Fuente: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/lectura_independiente_libro_mu2026/20260730_232242/CRUCE_66_CODIGOS.csv`; `DIFERENCIA; niveles PREGRADO`.
- B/C/E — 27 de32 carreras tienen diferencia neta; cinco neto0, pero C6 yC79 contienen diferencias compensadas. Igualar carrera no acredita cambios personales de jornada/versión. Fuente: `/Users/alexi/Documents/GitHub/avance_curricular/procesos/caracterizacion/gobernanza/sies/TABLA_PUENTE_CSV_BASE_RETENCION_MU.csv`; `ANIO2026; COD_CAR6 y79; agregado por COD_CAR`.
- E — La causa individual de las48 diferencias no queda demostrada por la conciliación. No se puede distribuir personas para forzar los totales. Fuente: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/auditoria_integral_publicacion_vs_pregrado_posgrado_2026/20260730_223007/MANIFEST_AUDITORIA_INTEGRAL_MU2026_PUBLICACION_PREGRADO_POSGRADO_20260730_223007.json`; `pendientes PUBLICACION_AGREGADA_SIN_RUT`.
- E — El manifiesto puente septiembre describe causas cerradas por agregación. Se conservan sus conteos comprobados, pero esa conclusión causal excede la evidencia agregada. No se modifica el manifiesto histórico. Fuente: `/Users/alexi/Documents/GitHub/avance_curricular/procesos/caracterizacion/gobernanza/sies/TABLA_PUENTE_CSV_BASE_RETENCION_MU.manifest.json`; `cierre_carrera_2026_09_30.patrones_encontrados; qa.detalle`.

## QA y límites

C — Se verificaron66 códigos,63 cruces institucionales pregrado, tres Postítulos,32 sumas por carrera y la partición VIG. Se conserva íntegramente cada fuente por hash. No se recalculan tasas de retención ni se alteran denominadores. No se exportan identificadores individuales.
