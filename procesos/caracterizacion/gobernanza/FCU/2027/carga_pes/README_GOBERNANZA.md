# FCU_CARGA_PES_2027

## Estado

Proceso independiente en preparacion. La carga oficial no esta liberada. No se ha creado ni subido un CSV oficial 2027.

## Referencias controladas

- `json/REFERENCIA_2026_CONGELADA.json`: comprobacion de archivos historicos y codigo de referencia, sin modificar 2026.
- `json/CONTRATO_CARGA_PES_2027.json`: etapas, fuentes, limites de reutilizacion, verificaciones y criterio de liberacion.
- `../preparacion/json/ESPECIFICACION_PES_2027.json`: esquema de 172 campos y correspondencias actuales.
- `../preparacion/evidencias/Matriz_FCU_2027_GUIA_TRAZABLE_20261007.xlsx`: historia y codigos actuales con origen FCU/institucional.
- `../preparacion/json/MANIFIESTO_CONCILIACION_PES_20261007.json`: artefactos de preparacion, hashes y pruebas.

El inventario de origen 2026 se conserva como evidencia historica. Las rectificaciones de correspondencia detectadas durante la preparacion 2027 se documentan en Cruces; no se reescribe el inventario original ni se reabre la carga 2026.

## Reutilizacion del proceso de subida

Se heredan el orden operativo y los controles probados en el cierre 2026: conciliar universo, verificar fuentes, convertir respuestas, aplicar reglas condicionales, auditar datos, comprobar archivo fisico, identificarlo por hash y conservar la recepcion de plataforma.

El archivo de referencia 2026 tiene 1371 filas, 195 campos, separador punto y coma, sin encabezado y sin salto de linea final. Estas caracteristicas describen el cierre 2026; no establecen automaticamente los parametros definitivos 2027. El borrador 2027 actual usa los 172 campos identificados y el separador del manual 2027. Antes de subir se debe aprobar explicitamente el perfil de formato y resolver las discrepancias de letras de columnas de ese manual.

## Entradas y reglas

El registro vigente `../preparacion/json/PREGUNTAS_INSTITUCIONALES_2027.json` version3 identifica emprendimiento formalizado como alternativa institucional AO05 de G02Q95. Sustituye la instruccion inicial de pregunta nueva independiente. AO05 no aporta SIT_LAB ni agrega columnas PES. G02Q27 es una pregunta institucional mixta sobre empresa o emprendimiento y tampoco tiene campo oficial PES; su respuesta no confirma un nombre propio. El adaptador conserva los controles laborales y rechaza mapeos oficiales desde AO05. Las respuestas literales se conservan para estudios propios; su ausencia no excluye estudiantes. Ver `../preparacion/docs/EMPRENDIMIENTO_FORMALIZADO_2027.md`.

Las respuestas deben pertenecer a la version de encuesta identificada, no al instrumento 2026 con codigos reutilizados. Las fuentes administrativas se cruzan por identificador validado; no se deduce el DV desde el token, no se usa CODCLI como RUT ni un codigo interno de carrera como codigo SIES.

La cohorte es ingreso y matricula 2027, periodo dinamico 1, 2 o 3, con elegibilidad procedente del diccionario institucional gobernado. No se incluyen ingresos 2025 o 2026 ni se inventa una nueva definicion de vigente en este adaptador.

Cada campo debe tener fuente, codigo literal si corresponde, valor de origen, conversion, catalogo y QA. Los trece campos de fuente de carga y los ocho casos de catalogo/equivalencia deben validarse como datos, no mediante nuevas preguntas automaticas.

## Ejecuciones y salida

El adaptador es `scripts/fcu_pes_2027.py`. Revisa la referencia congelada y bloquea escrituras dentro de 2026. No importa ni ejecuta `caracterizacion.py` ni los scripts productivos de cierre 2026.

Las ejecuciones de registros deben guardarse localmente, preferentemente en `.local/FCU/2027/<fecha>/P<periodo>/<ejecucion>/`. El QA distingue faltantes, valores fuera de catalogo, contradicciones, consentimiento, cohorte y duplicados de documento. Cada archivo debe identificarse por version de fuentes, parametros, conteos, nombre y hash.

El adaptador bloquea salidas individuales en carpetas publicables del repositorio: deben estar ignoradas por Git o en un espacio externo. La gobernanza publica conserva contratos, reglas, hashes y resultados agregados, no publica automaticamente datos personales.

No sobrescribir archivos finales ni reusar un archivo anterior cuando la ejecucion nueva falla. La presencia de un borrador no autoriza su envio. Las salidas actuales se denominan BORRADOR y no hay una opcion para liberarlas como oficiales en el adaptador.

## Criterios de liberacion

1. Referencia 2026 integra y fuentes 2027 versionadas.
2. Correspondencia completa de campos, codigos y respuestas aprobada.
3. Fuentes administrativas, catalogos y reglas condicionales validados.
4. Universo y consentimientos reconciliados, sin estudiantes duplicados ni descartes silenciosos.
5. QA y validacion fisica satisfactorios con formato PES 2027 aprobado.
6. Archivo final conservado con hash, parametros y manifiesto de ejecucion.
7. Autorizacion de subida y posterior constancia de recepcion de plataforma.

Cumplir las etapas de preparacion no permite afirmar que el archivo fue aceptado por PES.
