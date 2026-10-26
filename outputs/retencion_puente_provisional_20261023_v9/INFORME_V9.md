# V9 — Validación separada autorizada

## Resultado
Se validaron2165 observaciones de1348 personas:811 observaciones/402 personas con código personal MU de otra fecha y1354/950 sin esa corroboración. Cuatro personas aparecen en ambos grupos; no sumar950+402. Las otras1048 observaciones pendientes V8 no se tocaron.

119 observaciones de88 personas quedan reconocidas como CORRESPONDENCIA_INTERNA_REGLA_VIGENTE. Se trata de una equivalencia manual existente para2026, no de aprobación nueva, código efectivamente informado ni vigencia histórica del plan.87 personas quedan completamente conciliadas internamente y1 parcialmente. Pendiente interno:3094 observaciones,1751/5901 personas (29,67%). Pendiente documental:3213 observaciones,1838/5901 personas (31,15%), sin cambios. Se conservan cierres V7. No se aplicó escenario501. La brecha24/63 de dimensiones no se recalifica.

## Hallazgo dirigido de regla vigente
La tabla _fcu2026_manual_equivalencias_cod_car y la aplicación _fcu2026_apply_manual_equivalencias_fcu_2026 de procesos/caracterizacion/caracterizacion.py contienen equivalencias exactas por CODIGO_INTERNO/CODCARPR/JORNADA_NORM/SEDE_NORM y las marcan VALIDADO_MANUAL_FCU. Se verificó su contenido por AST contra el snapshot gobernado16oct, sin ejecutar el módulo ni modificarlo. No compara nombres. Las119 coinciden en2026, código, carrera, sede, jornada, contexto de plan y oferta; no se extienden a años previos ni se acredita plan efectivo.
IMDI:99 observaciones, I162S2C112J4V1; IRHU:14, I162S2C113J4V1; NATP:3, I162S2C90J2V2; ISEP:2, I162S2C125J4V1; IFIN:1, I162S2C111J4V1. Todas proceden del grupo1354. El cero universal deV8 no había distinguido estas equivalencias explícitas de los perfiles inferidos. Se corrige la clasificación del derivado, no el canon.

## Grupo811: qué acredita la MU
768 observaciones tienen el código solo en años posteriores al periodo pendiente;41 solo anteriores;2 a ambos lados. No hay código MU del año pendiente ni enlace explícito CODCLI+plan+año en los índices nuevos y anteriores.684 tienen año de ingreso MU/DA concordante: quedan propuestas condicionadas a aplicación temporal.127 observaciones de85 personas tienen ingreso distinto o múltiple y se clasifican NO_DETERMINABLE_CON_ALERTA. Las alertas se concentran en TPAS39,ICIB33,TCIB13,IINF12,IADM10,ICRE9,TCRE4,TPAREOL3 y otros4 registros. No se presume error de ninguna fuente.
No se encontraron códigos MU alternativos de la misma familia en el índice ampliado para este subconjunto, ni coexistencia de otro expediente de la misma carrera/año. Estos controles negativos no prueban continuidad del plan en un hueco temporal.

## Grupo1354: perfil frente a evidencia individual
119 reconocidas por regla manual vigente;1235 quedan propuestas condicionadas. Perfil canónico:758; perfil unánime del grupo:477; manual:119. En las1354 no se encontró corroboración MU personal del código propuesto, ni plan literal que documente aplicación al periodo en SIES. Ello no impide reconocer la regla interna manual; sí impide afirmar envío individual.

## Qué está comprobado en ambos grupos
Todos los2165 planes están catalogados con carrera/sede concordantes; todos tienen el perfil ofrecido en el año de actividad. Ningún registro del catálogo aporta fecha efectiva ni versión SIES individual acreditada. Perfil de duración/tipo procede del grupo gobernado, no de duración individual en DA; no se convierte nivel en duración. ANOINGRESO procede del corte DA, sin inventar fecha de extracción.
Se consultaron los índices individuales V3 y las5292 evidencias completas del procesamiento dirigido posterior, filtradas a estas personas. La fuente dirigida adicional fue catalogo_planes.json, con CODPESTUD, carreras_internas,sedes,fecha_vigencia_acreditada,version_sies_asignada y filas_fuente. Se examinó la regla manual vigente como documento explícito. No se repitieron barridos generales.

## Condiciones y decisiones restantes
1919 observaciones quedan PROPUESTA_CONDICIONADA:684 con código personal de otra fecha y1235 por perfil/cohorte.127 tienen alerta de ingreso. El privado conserva por fila pruebas, años MU, año DA, estado anterior/nuevo, fuente/hoja/fila o función/línea, regla y condición.
Para684: documentar aplicación temporal al expediente/plan o aprobar posteriormente una regla explícita de extrapolación con tratamiento de cambios/huecos. Para1235: acreditar relación del perfil y fecha efectiva al expediente, o aprobar regla de asignación interna por grupo/cohorte separada del envío. Para127: resolver discrepancias de ingreso antes de extrapolar. No se han aprobado esas reglas; ninguna reducción porcentual sustituye su validación.

## Conservación y QA
QA independiente:2165 pertenencias y119 aplicaciones exactas de regla2026; conciliación de personas completas/parciales; hashes de fuentes intactos. Libro V9 añade hojas45–46 aV8 y conserva13 gráficos y valores históricos. PrivadoV6 conserva detalle de pruebas y filas DA completas del foco. Mantiene discrepancia T3 preexistente. No commit,push,uploads ni cambio de rama. Estado general PENDIENTE_APROBACION_GOBERNANZA para propuestas no adoptadas.
