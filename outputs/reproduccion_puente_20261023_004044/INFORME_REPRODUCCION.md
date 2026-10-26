# Reproducción de la conciliación UMAS–SIES · 23-oct-2026

## Resultado y alcance

**B/C. Se reprodujo V10 sin cambiar códigos adoptados, reglas, tasas o denominadores.** Universo: 5.901 personas, 6.622 expedientes y 24.774 observaciones. Las 24.774 claves y sus estados/códigos antes y después coinciden. No hay nuevos cierres respaldados; no se aplicó el escenario de 501 personas. QA técnico: OK_CON_ADVERTENCIAS. La investigación del ingreso original al plan queda pendiente, no resuelta por ausencia de cambios.

Proceso: conciliación histórica UMAS–SIES, vinculada al subproyecto retención IPSS 162. Ejecución: 23-oct-2026. Actividad observada PROMEDIOS: 2019–2026; matrícula individual releída: 2010–2026, sin inferir cobertura integral. La presencia de ANOMATRICULA=2027 en DATOSDEALUMNOS no demuestra matrícula SIES 2027 enviada. Principal: avance_curricular/feature/ire-2026. Las fuentes y huellas exactas están en FUENTES_HASHES_FINAL.json y el inventario.

| Personas (categorías excluyentes) | Documental | Interno vigente | Respaldo |
|---|---:|---:|---|
| Sin observaciones pendientes | 4.063 | 4.150 | C |
| Parcialmente resueltas | 699 | 699 | C |
| Ninguna observación resuelta | 1.139 | 1.052 | C |
| Total | 5.901 | 5.901 | B/C |

**C. Con algún pendiente**: documental 1.838/5.901 = 31,15%; interno 1.751/5.901 = 29,67%. Esta fila es subtotal (parcial + ninguna), no otra categoría sumable. Observaciones pendientes: 3.213 y 3.094. El 38,10% de 24/63 combinaciones pertenece a otra unidad; no es evolución comparable ni retención.

## Qué se releyó y cómo se atribuyó

- **B/C.** PROMEDIOSDEALUMNOS_12166.xlsx, Hoja1: 70.000 filas de asignaturas; 57.131 pertenecen a las dimensiones estudiadas, agrupadas en 24.774 observaciones. La unidad es persona + CODCLI/carrera + sede/jornada + plan + año/período; no una fila por asignatura. Se mantienen las filas de evidencia en listas, sin expandir uniones muchos-a-muchos.
- **B.** DATOSDEALUMNOS_12159 y 11248: 15.185 y 14.637 filas. No contienen una columna explícita PLAN_DE_ESTUDIO/CODPESTUD en sus encabezados efectivos. Tienen ANOINGRESO, PERIODOINGRESO, ANOMATRICULA, PERIODOMATRICULA, FECHAMATRICULA y FECHAFIRMA. Sus cortes efectivos no se acreditan por nombre, carpeta o docProps. El plan observado procede de PROMEDIOS y catálogos, no de una columna inexistente de estos dos DA.
- **B/C.** Relectura de 12 hojas MAT 2010–2021 y BASE_RETENCION_MU 2022–2026; esta última conserva su carácter derivado, sin convertirla en evidencia primaria de aceptación. El manifiesto de construcción original identifica sus RAW y selección. Se releen 16 hojas contando los dos DA y PROMEDIOS.
- **B/C.** Relectura adicional de 49.218 localizadores completos de 33 archivos multiproceso: 49.218 coinciden en identidad y código; cero discrepancias. Son evidencias, no personas. No se declara haber reexplorado exhaustivamente todas las fuentes posibles. La comprobación no da automáticamente vigencia temporal a una evidencia de titulados/avance curricular ni prueba aceptación SIES.
- **C.** Primero identidad exacta normalizada, luego familia carrera/sede/jornada, año, expediente y contexto DA. RUT original y normalizado se conservan por separado. No se usan nombres ni coincidencias aproximadas. Las 86 alertas de atribución no se rotulan automáticamente como códigos contradictorios.
- **D/C.** Se revalidan únicamente las 119 equivalencias internas FCU2026 ya vigentes (IMDI 99, IRHU 14, NATP 3, ISEP 2, IFIN 1), con alcance de año, plan, carrera, sede y ausencia de alternativas. Permiten 87 personas completamente resueltas adicionales y una parcialmente, pero no prueban envío individual. No se crean reglas nuevas.

## Mejora de la prueba retrospectiva

**C.** Se reproduce la prueba MU ingreso actual en 17.826 observaciones regulares: 15.029 coincidencias, 1.494 diferencias, 1.044 empates, 257 sin oferta compatible y 2 sin fecha única. El código objetivo no participa directamente de la selección del candidato; se compara después. Los perfiles heredados podrían contener información relacionada con el objetivo, por lo que esta reproducción por sí sola no elimina circularidad.

**C.** Prueba adicional en cinco particiones deterministas por persona: todas las observaciones de la misma persona quedan juntas y los perfiles se aprenden únicamente de las otras particiones. Resultado: 15.171 coincidencias, 1.387 diferencias, 1.228 empates, 34 sin oferta compatible, 4 sin perfil y 2 sin fecha única. Es evaluación retrospectiva, no pronóstico: no hay separación temporal y las familias se heredan del mapa existente. Las personas de cada resultado pueden solaparse; sus conteos por resultado no se suman. Las 1.387 diferencias impiden adoptar una regla universal. Tampoco refutan una hipótesis distinta basada en ingreso original al plan, pues esa fecha sigue sin acreditarse.

## Ingreso original, planes y reingreso

**B/C.** Cada uno de los 6.622 expedientes seleccionados tiene una sola etiqueta de plan en las observaciones de PROMEDIOS revisadas. Al ampliar a persona–familia, hay 374 personas con varios expedientes/planes, distribuidas en 377 relaciones persona–familia. La cronología privada conserva primer y último período observado de cada combinación. **E:** no prueba que hubiera migración administrativa ni fecha efectiva; tampoco excluye cambios anteriores no conservados en la exportación.

**B/C. Caso C3/J4:** 674 observaciones de 87 personas documentan I162S2C3J4V2 y ANIO_ING_ACT=2022. Incluyen planes IETMREOL20211 e ICRE20241 en años diferentes; el detalle agregado y las filas exactas están en QA_CRONOLOGIA.json y el registro privado. **E:** las etiquetas y el año de ingreso no autorizan a sustituir V2 por V1. Falta acto/evidencia de asignación del plan o migración con vigencia efectiva.

**A (alcance 2027).** Manual de Oferta/Acceso 2027, páginas físicas 65–66, conservado en data/reglas_negocio/20261015/fuentes/manual_oferta_acceso_2027_texto_completo.json: estructura del código y cambios relevantes para versión. No se aplica retroactivamente por supuesto. **E:** ordenar el debut en oferta o hacer coincidir totales no identifica por sí solo la versión individual ni elimina versiones anteriores.

## Pendientes exactos y decisiones no adoptadas

| Observaciones internas pendientes | Cantidad | Falta | Clasificación |
|---|---:|---|---|
| Candidato único condicionado | 2.695 | Fecha efectiva de asignación del plan al expediente, perfil individual y condiciones de continuidad/reingreso/migración | E |
| Fecha ausente o múltiple | 32 | Resolver qué campo acredita ingreso original a ese programa/plan | E |
| Sin perfil | 203 | Duración y tipo de plan aplicables, con fuente individual o equivalencia formal | E |
| Varios candidatos | 94 | Atributo discriminante o equivalencia vigente con fecha efectiva | E |
| Sin grupo | 51 | Correspondencia histórica de carrera/sede/jornada | E |
| Sin oferta compatible | 19 | Oferta histórica aplicable y alcance del perfil | E |
| Total | 3.094 | No se sustituye «pendiente» por cero ni se adopta el candidato por ser único | C |

**E/D.** No se pide una tabla inexistente como única salida: la trayectoria reconstruida deja lista la evidencia para formalizar una equivalencia institucional si se demuestra y aprueba su alcance. Hasta entonces, persona localizada, código anual, propuesta y equivalencia interna son estados diferentes. Ningún candidato nuevo fue promovido.

## Archivos y QA

- Libro agregado V11: conserva las 48 hojas de V10 byte a byte y sus 13 gráficos; agrega 49_Reproduccion_V10, 50_Prueba_Personas y 51_Evidencias_Releidas. Las nuevas hojas contienen 32 fórmulas con caché verificada y cero errores de celda. La copia de Escritorio es idéntica. Los porcentajes nuevos son pendientes/total, no tasas de retención. Diferencias entre porcentajes se expresan en puntos porcentuales.
- Privado local: REVISION_PRIVADA_PUENTE_REPRODUCIDO_20261023.xlsx, 24.774 observaciones comprobadas celda por celda contra el registro; identificadores como texto. JSON y CSV adyacentes conservan todos los campos y listas de procedencia. TRAYECTORIAS_MULTIPLES_PERSONA_FAMILIA.json agrega la investigación temporal. Directorio fuera de cualquier Git, permisos 0700; no hay copia individual en el repositorio.
- Fórmulas nuevas recalculadas con Artifact Tool y contrastadas mediante lectura independiente. No se ha abierto en Excel nativo. No se certifica cero error en todas las tasas heredadas.
- **B/C. Advertencia heredada:** hoja 31_Comparacion_Historica, MU1/T3 2026 conserva 1.360 y 1.471 junto a tasa 0,92706203135651 (compatible con 1.360/1.467). El cociente 1.360/1.471 es 0,9245411284840245. Está advertido; no se modificó ninguna cifra sin autorización.
- Las 59 huellas de fuentes verificadas se conservan. No se sobrescribieron fuentes, V10, V7 o el motor anual. No hubo commit, push, merge, PR ni cambio de rama; los cambios previos ajenos permanecen.

## Reproducción

Ejecutar scripts/reproducir_puente_20261023.py con --reanudacion apuntando al directorio privado reanudacion de esta entrega. Ese snapshot mínimo permite reanudar sin los temporales /tmp originales. Después ejecutar verificar_evidencias_puente_20261023.py, auditar_cronologia_reproduccion_20261023.py, preparar_entrega_reproduccion_20261023.py, crear_entrega_reproduccion_20261023.mjs, ensamblar_reproduccion_20261023.py y cerrar_reproduccion_20261023.py sobre la carpeta generada. Usar dependencias y rutas locales declaradas en el checkpoint. El creador JS requiere @oai/artifact-tool y puede necesitar memoria de proceso de 8 GB para el detalle. El primer intento con 2 GB no completó el privado; el reintento verificado sí lo completó.

Los scripts mantienen huellas y condiciones de detención. El aprendizaje por partición no cambia el canon. El siguiente avance sustantivo es evaluar las 374 trayectorias múltiples contra evidencia efectiva de plan y revisar los perfiles faltantes, no repetir la búsqueda universal por nombre ni imponer 0%.
