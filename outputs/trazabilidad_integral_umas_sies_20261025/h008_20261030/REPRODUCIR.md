# Reproducción H008

C · Ensamblado incremental reproducido en un directorio privado aislado: V24 + fuentes fijadas en CONFIG.json. Las dos salidas previas al recálculo son idénticas byte a byte (REPRODUCCION_AISLADA.json). Excel cambia metadatos, serialización y cachés al recalcular: QA_NATIVO_V25.json comprueba fórmulas y constantes, y 6740 resultados numéricos frente a la copia QA de V24, sin diferencias.

No equivale a reproducción integral desde fuentes crudas: R19 conserva pendientes de proxies y desgloses. La Fase 6 integral queda E, no cerrada.

Variables del entorno: H008_PRIVATE (directorio privado), H008_OUTPUT (archivo nuevo), H008_PYTHON, H008_NODE y H008_NODE_MODULES (dependencias locales). CONFIG.json conserva rutas y SHA-256, nunca se publica. FUENTES_H008.json y FUENTES_FOTOS_H008.json documentan las huellas sin datos individuales.

```sh
"$H008_PYTHON" outputs/trazabilidad_integral_umas_sies_20261025/h008_20261030/reproducir_seguimiento.py   --config "$H008_PRIVATE/CONFIG.json" --privado "$H008_PRIVATE/ejecucion_nueva"   --salida "$H008_OUTPUT" --informes "$H008_PRIVATE/ejecucion_nueva/informes"   --node "$H008_NODE" --node-modules "$H008_NODE_MODULES"
```

La salida no debe existir: el comando se detiene antes de sobrescribir. Ejecutar qa_h008.py antes del recálculo para el control estructural y de objetos OOXML. Después, abrir y recalcular esa copia en Excel, guardar y comparar valores con la copia nativa. El control de igualdad binaria de gráficos es previo al guardado nativo, que puede reserializarlos. Nunca abrir ni guardar V24 como salida.

Los cinco constructores históricos solicitados ya estaban en Git (CONSTRUCTORES_PREVIOS.json). No se vuelven a agregar como si fueran nuevos ni se alteran sus manifiestos históricos. Los productores H008 leen rutas privadas por argumento/configuración; H007 permanece como antecedente gobernado.
