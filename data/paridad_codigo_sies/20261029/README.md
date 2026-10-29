# H002 · Paridad de catálogo UMAS–SIES, 2026 y 2027

Estado vigente: H002e, decisiones D de Alexi del 29-10-2026. Oferta Académica
2027 ejecutada en 2026; catálogo por año/código completo, sin personas ni retención.
106 filas de grupos 2026 y 161 de la carga V06 para 2027. Las filas 2026 quedan
idénticas al antecedente 2969b63; las decisiones actuales tienen ámbito 2027.

## Fuentes y clases

FUENTES.json fija rutas y SHA-256. La V06 es carga preparada C con confirmación
de aceptación D; no descarga PES ni comprobante técnico B. Su copia congelada
se contrasta por hash. Manual de octubre: versión/tipo, página 22; vigencia,
página 28. La extracción TXT anterior tiene páginas 23/29: no intercambiarlas.
A definición oficial; B observación; C cálculo; D decisión interna; E pendiente.

DECISIONES_APROBADAS.json conserva las seis aprobaciones H002b.
DECISIONES_APROBADAS_v2.json añade cinco relaciones y las decisiones H002e,
con responsable, fecha y evidencia REVISION_CASO_A_CASO_12_v3. No reescribe
la decisión anterior. Permanencia se usa sólo como foto 27-10-2026; no como VIG SIES.

## Unidad y asociaciones

Una fila es un código/año, no un plan ni un estudiante. Un código puede tener
varios CODCARPR y mallas. Las listas planas son índices, nunca producto cartesiano.
La aprobación D sólo cubre el grupo/plan citado en correspondencias_aprobadas_H002e;
no aprueba todos los otros alias o candidatos de esa fila. Mallas y cohortes sin
ámbito único conservan E. No elegir año del plan, V mayor, nombre o vía de ingreso.
Modalidad viene de oferta, no de escolaridad ni jornada. J3 y J4 son distintas.
RE/CO se consultan con gobernanza; PTG sólo en el ámbito 2027 documentado.

## Estados vigentes

- APROBADA_D_2027: seis códigos H002b y cinco relaciones H002e. Código aprobado
  de catálogo; no asignación individual ni temporal automática de todas las mallas.
- PLAN_HISTORICO_SIN_ALUMNOS_VIGENTES: seis **grupos** (IECIRE, IETMRE, NCONRE,
  NCONREOL, NINFREOL, CNATP), clase D, registrados en resoluciones por grupo.
  La ambigüedad histórica E y candidatos se conservan, sin asignar versión.
  No convertir todos sus códigos compartidos en históricos: otros planes los usan.
- HISTORICO_SIN_MATRICULA_RECIENTE: seis códigos C35, D; no requieren paridad 2027.
- VERSION_MULTIPLE_E: CADMP, pendiente en dos filas de código; indicio 7–10
  expedientes frente a 9 en V2 y 94 en V1, sin aprobación.
- NUEVO_2027_SIN_PLAN_E: 37 filas intactas, clasificadas en H002d como códigos sin
  historia de matrícula pública 2007–2026 ni MU 2022–2026. Pendientes de planes UMAS.
  No equivale necesariamente a 37 carreras nuevas ni a primera aparición en oferta.
- VERSION_MULTIPLE_RESUELTA: los grupos relevantes tienen selección calculada o
  decisión D/retirada de alcance 2027. Conservar las asociaciones y E históricas.
- CONTINUA: presencia del mismo código, no acreditación de todas sus mallas.
- SIN_OFERTA_2027: ausencia de V06, sin prueba de cierre.
- FUERA_ALCANCE: diplomados, postítulos y educación continua. Pregrado de
  continuidad no se excluye por prefijo. NUEVO_2027_CON_PLAN queda como estado de
  propuesta histórica; no hay filas pendientes con ese estado después de H002b.

Vigencia 2 no admite nuevos y no significa cerrada. TAMD V1 está aprobado, pero
sin nuevos; no autoriza V2. La correspondencia y la admisión se mantienen separadas.
OBSERVACIONES_OFERTA_2027.md registra siete vigencias 2 sin matrícula reciente (E),
sin modificar la oferta. IECIRE tiene una fila TITULADO; cero vigentes no es cero filas.

## Conteos de filas por estado

| Estado | 2026 | 2027 |
|---|---:|---:|
| CONTINUA | 53 | 53 |
| VERSION_MULTIPLE_RESUELTA | 24 | 31 |
| VERSION_MULTIPLE_E | 14 | 2 |
| APROBADA_D_2027 | 0 | 11 |
| NUEVO_2027_SIN_PLAN_E | 0 | 37 |
| SIN_OFERTA_2027 | 4 | 0 |
| FUERA_ALCANCE | 11 | 21 |
| HISTORICO_SIN_MATRICULA_RECIENTE | 0 | 6 |

Los seis estados de grupos históricos se cuentan aparte de las filas por código.

## Reproducción, controles y antecedentes

El constructor aplica las decisiones a partir de fuentes fijadas. CSV UTF-8 con
separador punto y coma; asociaciones serializadas como JSON. El JSON y CSV deben
coincidir. MANIFEST.json registra entradas, código, decisiones, plantilla y salidas.

`python3 -B outputs/paridad_codigo_sies_20261029/construir_paridad.py --verificar`
comprueba los mismos bytes sin escribir. La primera sustitución autorizada utiliza
`--aplicar-h002e`, exige HEAD/huellas previos y sólo permite sus salidas declaradas.
No borra ni modifica fuentes. QA_H002E.json comprueba 106/161, filas/campos autorizados,
37 sin cambios, seis grupos históricos sin versión, 24 cambios ajenos, privacidad y pruebas.

REVISION_CASO_A_CASO_12 (v1, v2, v3) y PROPUESTA_PLANES_43 (v1, v2) son antecedentes
congelados. Para reproducirlos, usar checkout aislado de 2969b63 o el commit de su
manifiesto y sus componentes. No retocar sus hashes para aparentar compatibilidad
con la tabla vigente. El pedido anterior de un listado nuevo general está superado:
se reutilizaron los respaldos; la solicitud vigente a UMAS es la lista exacta de 37.

No se cambia v20, oferta, bases, denominadores, tasas ni se habilita una carga PES.
