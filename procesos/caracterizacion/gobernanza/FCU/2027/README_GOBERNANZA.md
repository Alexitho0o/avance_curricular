# FCU 2027: proceso independiente

## Separacion anual

FCU 2026 es una referencia congelada. Se conservan su manual, instrumento, inventarios originales, archivo validado, reglas y auditorias. El trabajo 2027 no modifica, reemplaza ni vuelve a generar esas evidencias.

FCU 2027 es otro proceso, con entradas, versiones de instrumento, reglas de conversion, estructura de carga y salidas propias. El procedimiento operativo validado en 2026 sirve como referencia, no como autorizacion para copiar sus 195 columnas ni sus indices al esquema 2027.

## Procesos y carpetas

Operacion inicial sin respuestas: `docs/gobernanza/MODO_SIN_RESPUESTAS_2027_P1.md` desde la raiz del proyecto. La confirmacion del usuario permite generar listas de participantes, matricula y pendientes desde fuentes administrativas y tokens, sin respuestas ficticias ni resultados financieros. No es una carga oficial FCU. El comando habitual activa este modo solo para 2027 P1/encuesta 141234 y retoma el flujo normal cuando aparecen respuestas.

- `preparacion/`: manuales comparados, fuentes del inventario, origen FCU/institucional, edicion del instrumento, matriz de codigos y decisiones del usuario.
- `carga_pes/`: contrato de datos, fuentes, version del esquema, validacion del adaptador, manifiestos de ejecucion y futura liberacion del archivo para subir.
- `.local/FCU/2027/`: area local ignorada por Git para bases individuales, borradores y QA de registros. Los datos personales no se publican automaticamente como evidencia en GitHub.

## Cadena de trazabilidad

Referencia 2026 congelada -> manual FCU 2027 -> version exacta del instrumento -> codigo de pregunta y subpregunta actuales -> campo PES 2027 -> regla y catalogo -> validacion por estudiante -> totales reconciliados -> CSV identificado por hash -> evidencia de recepcion de la plataforma.

La pregunta y la subpregunta se identifican por codigo y contenido, nunca por posicion heredada. Solo hay dos origenes de preguntas: FCU e INSTITUCIONAL. Los datos administrativos son fuentes de carga, no un tercer origen de preguntas. Las opciones propias de la institucion se conservan o se retiran por decision institucional; no se atribuye ese retiro a SIES.

## Regla de cierre

La adicion `Tengo un emprendimiento formalizado` se gobierna en `preparacion/json/PREGUNTAS_INSTITUCIONALES_2027.json` y `preparacion/docs/EMPRENDIMIENTO_FORMALIZADO_2027.md`. Version3 del2026-10-13: el instrumento recibido y las respuestas prueban una alternativa INSTITUCIONAL AO05 en G02Q95, no una pregunta independiente pendiente. Las cuatro alternativas originales y G02Q20 siguen protegidas. No agrega campos PES ni deriva SIT_LAB. G02Q27 es texto institucional mixto de empresa o emprendimiento, sin confirmar propiedad o nombre propio. Estudios y seguimiento VCM conservan respuesta literal, version, cobertura, acumulado/Hoy y faltantes. Otra opcion elegida no demuestra ausencia de emprendimiento. El auditor y regenerador consumen el registro y no deben restaurar la instruccion anterior.

Preparar el instrumento no equivale a aprobar la carga. Un borrador no equivale al archivo definitivo. La liberacion oficial requiere fuentes y catalogos validados, esquema y formato aprobados, control de consentimientos y cohorte, QA reconciliado y manifiesto del archivo exacto.

Las excepciones y confirmaciones del usuario se mantienen en `preparacion/json/POLITICA_REVISION_FCU_2027.json` y `CONFIRMACIONES_USUARIO_FCU_2027.json`. No se vuelven a pedir ajustes excluidos ni la exportacion para repetir la prueba visual de SQ008.

La identidad de referencia 2026 esta en `carga_pes/json/REFERENCIA_2026_CONGELADA.json`. Se verifica por SHA-256 antes de preparar una salida 2027. No rebasar ese registro automaticamente si aparece una diferencia; investigar y obtener una decision explicita sobre la referencia.

El paquete se gobierna localmente en el proyecto. Publicacion en GitHub y recepcion de PES son estados separados y requieren evidencia propia.
