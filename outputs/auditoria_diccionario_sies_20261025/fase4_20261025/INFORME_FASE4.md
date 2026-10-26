# Fase4 — paquete preparado; publicación pendiente

C — Hito1 completado: paquete explícito de 23 archivos para Git y siete para el complemento institucional 1.1.4. Código, descriptores y QA sin identificadores individuales. Excel y SQLite no incluidos. Dos claves previas ajenas de PROYECTO_IPSS permanecen fuera del paquete y no se modifican en el checkout.

B/C — Hito2 preparado: tres consumidores del paquete aislado leen v8_20261025_ocho_p y coinciden en las ocho recuperaciones. Pasan las 12 pruebas existentes. Producto real sigue en v7. El complemento remoto leído sigue en 1.1.3 (pluginrel_6ad8ac3a43ac8191ac0b2d173b4e9130). Se conserva identidad, permisos, defaultPrompt y todas las habilidades no modificadas. Overlay propuesto, no subido. Skill local preparada desde su propia fuente sin sobreescribir diferencias locales.

E — Hito3 pendiente: activar/publicar exige autorización específica, según PLAN_CIERRE_100_POR_CIENTO.md fase4/hito2. Después debe releerse el release publicado y ejecutarse prueba de consumo de la instalación real. No declarar esta fase completada solo por preparar archivos.

## Alcance exacto a aprobar (D pendiente)

1. Promover v8 local con respaldo de puntero y alerta con responsable, fecha/hora y autorización; mantener las bases privadas.
2. Commit y push exclusivamente de los 23 archivos enumerados en PAQUETE_PUBLICACION.json, usando el contenido preparado; conservar todos los cambios ajenos. La incorporación de PROYECTO_IPSS debe aislar solo la clave diccionario_sies_seguimiento, no sus otras dos claves pendientes.
3. Instalar el añadido de consulta en la skill local y publicar el overlay 1.1.4 del complemento Análisis institucional de Alexi, usando expected_release_id. Si el remoto cambió, detener y rebasar el parche antes de subir.
4. Verificar lectura posterior, versión efectiva y consumidores. No publicar Excel, SQLite, operaciones individuales ni salidas de consultas.

C — Para revisar: git_candidato/ contiene los archivos finales propuestos; PLUGIN_CAMBIOS.diff muestra el cambio remoto; skill_local_candidata/ conserva la propuesta local. No editar cachés instaladas ni copiar equivalencias. Las instrucciones consultan siempre PROYECTO_IPSS y su puntero verificado.

E — Los GPT heredados DATOS ALUMNOS KPI, Gestor Académico y Experto Matrícula no se actualizan mediante un ID supuesto ni desde su caché: falta fuente editable verificada. El complemento institucional y sus dos skills pertinentes sí tienen propuesta concreta. La publicación del contrato no equivale a conectividad remota con datos privados.

B/C — HEAD local/remoto comprobado 55e3b709afb9483f0ecdd2d166f67229a454a5ef. Sin commit/push, sin cambio de puntero, Excel, bases ni denominadores. La cobertura candidata permanece 3.041 pendientes históricos y 99 contextos del Excel; no es 100%.

## Ejecución autorizada — 2026-10-25T14:22:54.713460-03:00

D — Alexi autorizó el alcance preparado con «si». Se conservan arriba los antecedentes previos a la autorización.

B/C — Edición v8 activada, tres consumidores comprobados, 12 pruebas correctas. Commit `8e2fb85bb8703758d6878681c9e2a29016e60c63` publicado en feature/ire-2026 y remoto idéntico. Solo los 23 archivos previstos; sin Excel, SQLite ni identificadores individuales. Los cambios ajenos siguen pendientes y conservados.

B/C — Complemento 1.1.4 publicado y siete archivos releídos. La primera comparación literal del manifiesto generado detectó escapes Unicode distintos; la comparación JSON confirmó contenido equivalente antes del push. Skill local instalada desde su propia fuente.

E — No se acredita recarga automática en conversaciones abiertas ni conectividad remota a datos privados. Tres GPT heredados siguen fuera de esta actualización. Cobertura pendiente: 3.041 observaciones históricas, 99 contextos Excel, de los cuales el foco multiversión conserva sus 24 pendientes. No se modificaron tasas, bases, denominadores ni los libros V17/V18.

Evidencias: RECIBO_PUBLICACION.json, QA_ACTIVACION.json, QA_PUBLICACION.json, PLUGIN_PUBLICADO.json.
