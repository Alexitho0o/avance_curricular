# H008 · Seguimiento T1–T3 V25 sobre v20

Fecha 30-10-2026. Base Git `54f465d0a26b35d068b8c313487ad9c5702ec22b`. Estado **CANDIDATA_CON_LIMITES; Hito 2 y Fase 6 no cerrados**. Sin commit ni push. R19 permanece BORRADOR_NO_ACTIVO; R20, H001, fuentes y v20 no cambian.

## Hito 1 · Inventario cerrado

D · Alexi: las fotos representan el cierre del período 2 o 3, sin exigir un día calendario. No se atribuye fecha histórica a partir del nombre de un archivo.

B/C · Las seis combinaciones quedan inventariadas: cuatro halladas (dos ya usadas en R19 y con C4=0) y dos parciales, ambas T2-2025. De C4=1414, 681 tienen foto disponible y 733 quedan con fuente parcial. Disponibilidad no significa matrícula vigente. Evidencia: INVENTARIO_FOTOS_H008.json/.md. La fuente 10246 congelada de P2-2026 contiene 14204 filas y localiza 1471/1471 documentos del padrón T1; el listado de 528 ingresos T2 no la sustituye.

E · Falta la foto completa de cierre T2-2025. SOLICITUD_FOTOS_UMAS.md es sólo borrador, no enviado. No se pide reconstruir historia desde un estado actual.

## Hito 2 · V25 generada y recalculada; límite de QA explícito

B/C · Libro privado: `/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261030_V25.xlsx`. SHA-256 `63b55351334616833a2e687fbeb36314a0cbb1538c10b6a891c99f94475adc0a`. V24 conserva su hash `bfeba67628107f460cad69c5db119a6245782142bd5b65ab435b0cd116bca2db`.

B/C · Se integraron 1135 posiciones C1 y 1136 contextos v20 (una posición tiene dos). De esos contextos, 108 llevan correspondencia interna D ya aprobada y 1028 siguen E en v20. No son 1135 códigos adjudicados nuevos. Respaldo de contexto, código documental, correspondencia interna y expediente T1 quedan separados. Evidencia: INTEGRACION_C1.json.

B/C · Las fotos completas se incorporan a la vista en AP:AT, con fuente y cierre académico. FOTOS_INTEGRADAS.json informa los estados por cohorte/período. No reemplazan silenciosamente los proxies de R19. Las tasas principales conservan 1360/1467, 2290/2519 y 462/528, diferencias 0/0 y 0,00 pp; COMPARACION_V24_V25.json/.md incluye los valores por cohorte.

C · ZIP/XML íntegros; 13/13 controles estructurales; 37 tablas y 13 gráficos conservados, estilos centrados horizontal/vertical. Recálculo y guardado en Excel: 0 errores, 6740 resultados numéricos comparables sin diferencias y ninguna fórmula o constante anterior modificada. Se revisaron los 13 gráficos; se conservaron las limitaciones visuales heredadas (categorías alternadas en carrera/modalidad y etiquetas reducidas en hoja16), sin modificar series. El render nuevo del complemento es RESUMEN_COMPLEMENTO_V20.png.

C · Control adicional sobre el archivo guardado: 138226 fórmulas con resultado numérico de todo el libro coinciden con la copia QA de V24, incluidas hojas de base y auxiliares; no se confunden con 6740 resultados de presentación. Las celdas con contenido siguen centradas y las referencias de las series y todos los autofiltros previos permanecen; la vista de seguimiento tiene su filtro ampliado a AT. La guía de hojas ya carecía de autofiltro. Excel omitió 21 celdas XML vacías, sin valor ni fórmula; no hubo pérdida de contenido. Evidencia: QA_GUARDADO_NATIVO.json.

E · Los 77 casos pasan la regresión independiente. Una copia privada adicional con escenarios nativos fue rechazada por orden de celdas; no se aceptó su reparación. El constructor quedó corregido, pero no se certifica su ejecución. Excel dejó de responder en esa prueba auxiliar y la conexión siguió agotando el tiempo de espera; no se cerró por la fuerza. **No declarar 77 interacciones nativas ni QA total aprobado.** V25 sí abrió sin reparación y quedó guardada antes de esa prueba adicional. Evidencias: QA_ESTRUCTURAL_PRE_EXCEL.json, FILTROS_77_REGRESION.json y QA_NATIVO_V25.json.

## Hito 3 · Propuesta lista, no aplicada

C/E · PROPUESTA_ADJUDICACION_99.md/.json conserva 95 candidatos únicos (63 jornada distinta y 32 sin enlace T1) y cuatro IINF20241 con alternativas. Incluye opciones por código, evidencia, límites y decisión aprobar/rechazar/pedir evidencia. Una adjudicación exclusiva de código no cambia las tasas de la hoja18: 0,00 pp; no implica nueva vigencia. No se aplicó ninguna herencia.

## Hito 4 · Sin fuente nueva

B/C · La publicación 10-07-2026 y el MRUN H2 tienen los hashes ya gobernados. R09 sigue CERRADA_DOCUMENTADA, causa E. No se reconstruyó ningún vínculo personal ni se repitió el conteo. Evidencia: CONTROL_FUENTES_MRUN.json.

## Hito 5 · Reproducción incremental, no integral cruda

C · Un comando parametrizado produjo una copia aislada idéntica byte a byte antes del recálculo: `dad3945aa3115f229934849daf2506400905f7596bc3722b1de1444bf5d4c99c`. El guardado nativo cambia cachés y serialización; se comprueba contenido por separado. REPRODUCIR.md documenta el comando y CONSTRUCTORES_PREVIOS.json acredita que los constructores antiguos solicitados ya estaban versionados.

E · La Fase 6 integral sigue pendiente: reproducir R19 desde fuentes crudas y resolver su paridad de proxies/desgloses no se sustituye con V24 como entrada. Se conserva esa dependencia visible; no se declara cerrada.

## Decisiones y reanudación

1. Validar la candidata V25 sólo después de completar los 77 escenarios nativos pendientes. Las cifras R19 no se activan por este trabajo.
2. Aprobar/rechazar/pedir evidencia para los grupos de los 99; cuatro siguen con más de una opción.
3. Aprobar o ajustar el borrador de solicitud T2-2025 antes de cualquier envío.
4. La Fase 6 requiere completar reproducción cruda gobernada; no abrir nuevas inferencias para forzar el cierre.

Archivos tocados: LISTA_PUBLICACION_H008.json/.md. Los 25 cambios preexistentes quedan intactos y fuera del stage; detalles personales e intermedios, sólo privados. El libro no se incluye en la publicación propuesta.
