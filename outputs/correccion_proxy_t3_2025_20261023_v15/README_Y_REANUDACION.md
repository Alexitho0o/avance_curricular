# V15 · Auxiliar PROMEDIOS T3-2025

- **D — Alcance aprobado:** seguimiento interno por actividad del período y estado VIGENTE en PROMEDIOS. La fecha exacta histórica del estado no es un requisito pendiente de este indicador. No modifica la definición oficial de retención SIES.
- **B/C — Resultado:** 535 personas R + 11 personas P = 546; 546/1.150 = 47,4782608696 %. Presencia con cualquier estado: 582 R + 14 P = 596. Denominador: 1.130 R + 20 P = 1.150.
- **C — Identidad:** RUT y DV completos; documentos P vinculados solo mediante correspondencia explícita IPSS_Procesamiento/2025_carga, columnas J, BU, BV. Se cuentan personas una sola vez. No se exige código SIES de destino para este auxiliar.
- **B/C — Conservación:** T2-2025 sigue en 611/1.150; foto de matrícula T3 sigue en 1.023/1.150. Diccionario, bases originales y denominadores no cambian.
- **E — Límite de reconstrucción:** el constructor antiguo insertaba 535 como valor literal; no se recuperó su algoritmo original. La nueva reproducción sí verifica 535 R y 11 P, sin atribuir al script antiguo una condición no observada.

## Dónde mirar en el Excel

- Hoja 26, fila 1853: auxiliar T3 corregido, con fórmulas de suma y tasa.
- Hoja 26, filas 1857–1861: desglose R/P, denominadores, presencias, vigentes y total con fórmulas.
- Hojas 18, 28 y 52: notas de alcance actualizadas. La foto T3 de la hoja 18 se conserva.

## Reparación y QA

**B/C:** el registro nativo de V14 señala reparación en estilos. V15 retira únicamente tres extensiones de estilos que referenciaban un componente ausente. Conserva los 315 estilos, 22 formatos diferenciales, 54 hojas, 13 gráficos y 35 tablas. Los gráficos y tablas son idénticos byte a byte a V14; 50 hojas también lo son.

**B/C:** V15 abrió en Excel para Mac sin pedir recuperación. Se verificó visualmente el bloque R/P y 47,48 %. QA estructural: 43 celdas autorizadas; QA independiente: 20 controles; QA dinámico: 10 controles en memoria, alterando y restituyendo la entrada P para comprobar sumas y tasas sin tocar el archivo final. No hubo cambios celulares ajenos a la lista autorizada.

`QA_ESTRUCTURAL_CALCULOS.json` y `evidencia/QA_ESTILOS.json` son los registros anteriores a la apertura nativa; su pendiente queda cubierto por `QA_EXCEL_NATIVO.json`. `RESULTADO_AGREGADO.json` conserva la reproducción previa a aplicar los cambios; el estado final es este cierre y su manifiesto.

## Reproducción y reanudación

**C:** scripts persistentes: `scripts/recalcular_proxy_t3_2025_v15_20261023.py` reproduce el cruce agregado; `scripts/ensamblar_proxy_t3_v15_20261023.py` prepara la lista de ediciones y ensambla el paquete; `scripts/editar_proxy_t3_v15_20261023.mjs` aplica y recalcula con Artifact Tool; `scripts/reparar_estilos_v15_20261023.py` genera el parche mínimo de estilos. Sus rutas y hashes, y los de fuentes y evidencias, quedan en el manifiesto. Los ensambladores usan la carpeta V15 y rechazan sobrescribir el resultado: para otra ejecución se debe versionar la salida y conservar esta entrega.

**D/E — Próximo paso:** revisión del usuario sobre esta V15. Este alcance no reabre la asignación de versiones SIES ni convierte actividad académica en una foto oficial de matrícula. No queda pendiente la fecha exacta del estado para aceptar este cálculo interno. La documentación no prueba envío o aceptación SIES.

**B/C — Git:** rama feature/ire-2026, HEAD 80ca13a5a249a1a2bd53a699f5f73689b1f53040 antes y después. Cambios locales; sin staging, commit ni push. Copia idéntica en Escritorio; fuentes originales verificadas por hash.
