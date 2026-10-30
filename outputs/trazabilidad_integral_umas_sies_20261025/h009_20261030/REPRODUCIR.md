# Reproducir H009

Entradas: V25 con SHA-256 63b55351334616833a2e687fbeb36314a0cbb1538c10b6a891c99f94475adc0a; H006 original 5338543e375ed227e0297ed6ab136e1a67392e94f5969b1dd38b0d537578b03d. Libros privados por argumento; nunca incluirlos en Git.

1. `python3 construir_v26.py --origen "$V25" --salida "$V26_NUEVA" --informes "$SALIDA"`. La salida debe llamarse RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261030_V26.xlsx para reproducir el hash; no sobrescribe.
2. `python3 corregir_resumen_v2.py --origen "$H006" --salida "$H006_V2_NUEVA" --informe "$SALIDA/RESUMEN_V2.json"`.
3. Abrir y recalcular las copias en Excel. Ejecutar los 77 casos de fase5/CASOS_FILTROS.json en bloques de 15. En H009 se agotó el único reintento: no está certificado.
4. `python3 qa_graficos_filtros.py --origen "$V25" --libro "$V26" --config CONFIG_GRAFICOS.json --salida "$QA"`. El modo estructural conserva E si no se adjunta evidencia nativa. `--nativo` exige 77 registros (seleccion, totales, graficos con aux) y cuatro capturas revisadas; un orden, cantidad o total incorrectos falla.
5. `python3 test_graficos_filtros.py`: cero observado, modalidad ausente, desempate y detección de desorden. Guardar/restaurar selección 2379/1476/62,04 %. No tratar esos tests como selección o imagen nativa.

La edición acotada OOXML conserva las estructuras nativas del libro; no reexporta bases ni crea una matriz de cálculo paralela. La copia previa al guardado reproduce el mismo hash; el guardado de Excel se controla por celdas/fórmulas/objetos, no por identidad binaria.
