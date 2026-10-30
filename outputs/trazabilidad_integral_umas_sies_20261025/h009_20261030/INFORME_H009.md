# H009 · corrección de gráficos con límite de QA nativo

Estado: CANDIDATA_CON_QA_NATIVO_E. Se cumple la parada autorizada por fallo del único reintento; no se declara cierre 77/77.

## Resultados

- D: orden SIES para comparación y tasa total ponderada para Presencial/A distancia; ver DECISION_ORDEN.md. No se añadió una serie total.
- B/C: V26 en el Escritorio, SHA-256 `d7e68859cdba52a636e562a9cd287f8114afbc0fb97f0840dfc9284fb2a43a51`. Diez gráficos corregidos: ocho en hoja 14 y dos comparativos en hoja 16; trece conservados. 37 tablas y filtros conservados. 244190 valores originales iguales; cero cambios de fórmulas/constantes originales y cero errores inesperados. NA() intencional únicamente en auxiliares ausentes. Todos los estilos con contenido centrados.
- C: reproducción previa a Excel idéntica `4e0cb85dad11c3c2b34794685093cbebc0c7659a95ba79b9c52ff204ba20dbb5`; cuatro tests PASS. Fuente: QA_H009.json, REPRODUCCION_H009.json.
- B/E: apertura inicial sin reparación y guardado nativo correctos; lectura inicial 2379/1476/62,04 %. Bloque 1 (casos 1–15) agotó respuesta; último caso visible 4, Tecnologías, 1766/1162. Cierre normal sin guardar selecciones. Único reintento falló en reapertura previa al caso 1. Cero de 77 certificados en esta ejecución; las 77 regresiones independientes H008 siguen PASS y no sustituyen el control. Faltan prueba visual completa y cuatro capturas; no se fabricaron. Bloqueos conservados: ~$RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V21.xlsx, ~$RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V20.xlsx.
- B: R20 no tiene gráficos ni selectores de validación; tablas con autofiltro, sin auxiliares gráficos de relleno. Original 70baf95a… intacto, sin copia v2 innecesaria.
- B/C/E: H006 sí tenía tres gráficos de selectores con rangos fijos. Copia `RESUMEN_CRUCE_SIES_UMAS_20261030_v2.xlsx` en ENTREGA_RETENCION_20261031, hash `91c83b45eebf17d00ba2cd874af3e825fb1acfbd71313b09a034d0177bfbd27a` igual a privada. 67424 celdas originales idénticas; cuatro gráficos conservados, tres corregidos. La serie histórica no conectada a selectores conserva cronología. QA nativo E; no reemplaza original.
- D/C: reglas 1.3.11, commit `7ce327cc063cf3bb9ebbf6a22013264206bf1396`; validar PASS_CON_PENDIENTES_E (cero errores, advertencias históricas). Dos skills Codex sincronizadas con respaldo privado y hashes iguales; dos variantes Claude regeneradas, sin instalación Claude.

## H008 y límites conservados

H008 publicado por separado en `5d6c840253db871149221b754e0aeca7fdf201ea`: QA estructural repetido 13/13 y privacidad PASS, 41 rutas explícitas. R19 continúa BORRADOR; no se adjudican los 99, no se reabre R09 ni se certifica reproducción cruda integral. H001, R20, v20, bases y denominadores intactos.

## Pendiente exacto / reapertura

Con Excel estable: bloque 1 desde caso 1, luego bloques 2–6; años, sectores, jornadas y diez combinaciones; cuatro capturas de gráficos agregados; mismo control sobre H006 v2. Sin nueva iteración en este turno. V26 y H006 v2 permanecen candidatas; no se publican los XLSX.

Archivos autorizados H009: los enumerados en LISTA_PUBLICACION_H009.json; sólo esta carpeta, PLAN_FASES_HITOS.md y los dos mapas. Los 25 cambios ajenos se cotejan por estado y hash en QA_PUBLICACION_H009.json.
