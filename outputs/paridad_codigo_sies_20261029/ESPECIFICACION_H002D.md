# H002d · cuadratura de totales, sin atribución individual

D · Alexi, 29-10-2026. Se conservan H002, H002b y H002c. Nuevos derivados
agregados, sin modificar los catálogos, fuentes, indicadores ni versiones.

## Fuentes y unidades

- B/C: reusar TABLA_PUENTE_CSV_BASE_RETENCION_MU: ANIO+COD_SED+COD_CAR+JOR+VERSION.
  MU total y VIG1 quedan separados. No recalcular denominadores H001.
- B: releer la publicación pública 2007–2026 por su SHA-256 completo. Conservar
  TOTAL MATRÍCULA y TOTAL MATRÍCULA PRIMER AÑO; blanco es no informado, no cero.
- B/C: MRUN por código/año del maestro gobernado; contraste adicional 2026
  contra el agregado publicado en FUENTE_MRUN2026_Y_LIMPIEZA, sin leer identidades.
- B/C/E: PROMEDIOS: CODCLI distintos, carrera/plan/jornada/año y período UMAS
  literal; anual y período 1 separados, extracciones solapadas nunca sumadas.
  La sede del catálogo del plan no acredita la sede histórica individual.
- B/C/E: Datos Alumnos y Permanencia no tienen plan. Vincular CODCLI/carrera
  a un plan único observado en PROMEDIOS del año; múltiples o ausentes son E.
  El estado y jornada actuales no acreditan los de abril de años anteriores.
  Permanencia corresponde a 27-10-2026; no repetirla como foto de 2024/2025.

## Evidencia c y clasificación

La cuadratura se presenta completa con sus deltas. Una diferencia aproximada
no selecciona versión. c sólo propone códigos con igualdad positiva exacta entre
un conteo interno por plan/jornada/año (anual o P1, identificando la ventana) y
TOTAL MATRÍCULA pública del mismo año/código. Para evidencia c se usa la unión
de CODCLI de todos los planes del grupo, no un subtotal aislado de una malla.
Las fotos con planes sin enlace o múltiples permanecen descriptivas y no votan c.
Se excluyen igualdades incompatibles con el perfil de grupo ya gobernado: una
igualdad casual de un expediente no transforma una malla regular en continuidad.
Se requiere también que el puente
MU del código concuerde con la publicación en total o VIG1. Si distintos códigos
coinciden, c es ambigua; no elegir por proximidad, mayoría ni primera fila.
No se equipara número de expedientes con personas sin acreditar su grano.

a y b se reutilizan de H002c. Cada evidencia es una vía, no un voto por archivo.
Dos vías unívocas del mismo código y ninguna que lo contradiga: CALCE_UNICO.
Una vía o candidatos aún ambiguos: CALCE_DEBIL. Vías unívocas incompatibles:
CONFLICTO. Ninguna: SIN_CALCE. Todo es propuesta C/E, no aceptación PES ni
autorización para adjudicar códigos personales. La igualdad agregada no prueba
identidad ni vigencia temporal de una malla.

## Los 43

Dos categorías disjuntas, verificadas contra publicación y puente: ausencia de
matrícula 2007–2026 y MU 2022–2026; o historial positivo con última matrícula.
La observación de vigencia 2 sin matrícula 2024–2026 es una bandera transversal,
no una tercera población que se sume. Según el manual 2027, página 28, vigencia 2
es vigente sin estudiantes nuevos y con antiguos. La ausencia en una publicación
no cambia ni invalida por sí sola una declaración de oferta. Se deja E a Alexi.

QA: hashes, reproducción determinista, pruebas previas y nuevas, controles de
sumas y no interferencia. Sólo archivos nuevos de H002d al commit autorizado.
