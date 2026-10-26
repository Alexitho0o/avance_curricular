# Revisión por CODCLI de las 14 carreras discordantes

**B/C — Resultado:** el cruce exacto está bien: no se encontraron duplicaciones ni
discordancias de RUT, carrera o año/período de matrícula en los CODCLI localizados.
Los respaldos muestran cambios de estado y expedientes distintos. **E:** todavía no
permiten atribuir individualmente las 66 renuncias del resumen original.

Proceso: seguimiento interno de ingresos IPSS162 de 2026/P2. Universo conservado:
528 matrículas de 527 personas. La revisión no cambia la V16 ni sus indicadores.

## Comparación completa de las 14 carreras

**B/C:** agrupación por la carrera del listado T2 original; CODCLI es la llave del
cruce individual y RUT se usa para verificar identidad. La segunda columna proviene
de Hoja2!C32:C50. La tercera reúne lo que NO aparece como VIGENTE en el respaldo
12159: ELIMINADO o CODCLI no localizado. No equivale automáticamente a renuncias.

| Carrera | Renuncias del resumen T2 | Complemento de VIGENTE en 12159 | Diferencia C | Composición observada del complemento B |
|---|---:|---:|---:|---|
| Administración Pública | 2 | 1 | -1 | 1 renuncia post inicio |
| Auditoría | 2 | 1 | -1 | 1 renuncia post inicio |
| Ingeniería en Administración de Empresas | 6 | 4 | -2 | 4 renuncias post inicio |
| Técnico en Administración de Empresas | 4 | 3 | -1 | 3 renuncias post inicio |
| Ingeniería en Informática | 2 | 4 | +2 | 3 renuncias post inicio + 1 cambio de carrera |
| Técnico en Programación y Análisis de Sistemas | Vacío* | 3 | +3 | 1 renuncia post inicio + 1 retiro/retracto + 1 cambio de carrera |
| Técnico en Logística | 3 | 2 | -1 | 1 renuncia post inicio + 1 CODCLI no localizado |
| Ingeniería en Marketing Digital | 2 | 0 | -2 | Todos VIGENTE; dos con situación 38 |
| Técnico en Marketing Digital | 5 | 4 | -1 | 4 renuncias post inicio |
| Ingeniería en Recursos Humanos | Vacío* | 1 | + 1 | 1 CODCLI no localizado |
| Técnico en Recursos Humanos | Vacío* | 5 | +5 | 5 renuncias post inicio |
| Ingeniería Industrial | Vacío* | 1 | + 1 | 1 renuncia post inicio |
| Técnico en Enfermería | 11 | 12 | + 1 | 11 renuncias post inicio + 1 cambio de carrera |
| Técnico en Enfermería e Instrumentación Quirúrgica | 18 | 14 | -4 | 12 renuncias post inicio + 1 retiro/retracto + 1 cambio de carrera |
| **Total de las 14 carreras** | **55** | **55** | **0** | **47 renuncias post inicio +2 retiros/retractos +4 cambios de carrera +2 CODCLI no localizados** |

\* El original tiene celda vacía. La diferencia reproduce el tratamiento aritmético
como cero de su fórmula; no declara que se haya confirmado cero renuncias.
Los nombres llevan tildes solo para presentación. La tabla CSV conserva los textos
originales y los códigos UMAS, incluyendo COTENS/TENS y COTEIQ/TEIQ bajo sus grupos
originales. No se fusionaron programas ni se cambiaron códigos de las fuentes.

**C:** seis carreras tienen un exceso conjunto de 13 y ocho un déficit de 13. La
diferencia neta es cero, pero la suma de diferencias absolutas es 26. Este 26 es una
medida de discrepancia entre conteos, **no son 26 personas identificadas**.

## Qué cambió entre los respaldos

**B/C:** las 14 carreras contienen 420 matrículas. Se observan estas trayectorias
del mismo CODCLI entre 10246,11998 y 12159:

| Trayectoria observada | Matrículas |
|---|---:|
| VIGENTE en los tres respaldos | 365 |
| VIGENTE en 10246; ELIMINADO en 11998 y 12159 | 47 |
| ELIMINADO en los tres respaldos | 6 |
| CODCLI no localizado en ninguno de los tres | 1 |
| VIGENTE en 10246; CODCLI no localizado en 11998 y 12159 | 1 |
| **Total** | **420** |

**B/C:** las 47 transiciones a ELIMINADO se descomponen en 43 situación 11,
una situación 23 y tres situación 24. No hay transición ELIMINADO→VIGENTE entre
estos tres respaldos. En Ingeniería en Marketing Digital, dos matrículas permanecen
VIGENTE pero pasan de situación 1 a38. **E:** no demuestra que sean las mismas dos
renuncias del resumen ni acredita una eliminación intermedia no observada.

**B/C — Control de las 19 carreras:** las 528 matrículas se distribuyen al final en
462 VIGENTE,63 ELIMINADO, una SUSPENDIDO y dos sin CODCLI exacto. Los63 ELIMINADO
son 56 situación 11, tres situación 23 y cuatro situación 24. En Técnico en
Ciberseguridad, la suspensión es precisamente lo que hace que el complemento
llegue a 3 y coincida numéricamente con el resumen; no son tres renuncias probadas.

Etiquetas literales observadas B: `11 - RENUNCIA POST INICIO CLASES`,
`23 - RETIRO - RETRACTO`, `24 - CAMBIO DE CARRERA`,
`38 - REINCORPORACION DE ACTIVIDADES`, `2 - SUSPENSIÓN TEMPORAL`.
No se transformaron en códigos VIG SIES ni se aplicó una nueva regla funcional.

## Los dos CODCLI no localizados

**B:** la búsqueda complementaria por RUT exacto sí localiza otras matrículas.
Los identificadores permanecieron en memoria, fuera de estos entregables.

| Expediente original T2 | Otra matrícula observada por el mismo RUT | Qué permite concluir |
|---|---|---|
| IRHU, 2026/P2 | Otro CODCLI en TRHU, 2026/P2; VIGENTE/regular en 10246 y ELIMINADO/situación 11 en 11998 y 12159; misma jornada, fecha de matrícula distinta | B: la persona está localizada en otra carrera. E: no se ha acreditado reemplazo del expediente IRHU ni su condición al cierre T2. |
| TLOG, 2026/P2 | Mantiene el CODCLI original y VIGENTE en 10246; en 11998 y 12159 aparece otro CODCLI, TLOG, 2026/P3, VIGENTE/regular; misma jornada, fecha de matrícula distinta | B: existe matrícula posterior en la misma carrera. E: la desaparición del CODCLI P2 no demuestra renuncia, traslado ni la fecha efectiva del cambio. |

La matrícula alternativa IRHU/TRHU no se suma como un caso nuevo ni sustituye la
fila original. Tampoco se traslada el estado P3 de TLOG al expediente P2.

## Fechas, fuentes y trazabilidad

**B/E:**10246 tiene uso acreditado el 21-jul-2026 y congelamiento el 22-jul;
11998 tiene uso acreditado el 15-oct-2026 a las 14:18:42−03:00;12159 el 22-oct-2026
a las 08:41:06−03:00. Son fechas de uso de archivos, no días efectivos de cambio
académico. El manifiesto de 12159 corresponde a una ejecución 2027/P1, pero el archivo
contiene las matrículas 2026/P2 verificadas aquí. No se confundió el proceso de esa
ejecución con el período de las filas.

Fuentes B: T2, Hoja1 para matrícula e identidad y Hoja2!B32:D50 para resumen;
DatosAlumnos 10246/11998/12159, Hoja1, columnas CODCLI, RUT, CODCARPR, ANOMATRICULA,
PERIODOMATRICULA, ESTADOACADEMICO, SITUACION, JORNADA y FECHAMATRICULA. Rutas y hashes
completos en `EVIDENCIA_AGREGADA.json`. Los manifiestos de fecha se registran
adicionalmente en `MANIFEST.json`.

**E — Lo que no queda explicado:** no hay identificadores del agregado original 66,
ni constancia que vincule cada carrera de ese resumen con una nómina y fecha de
estados. Por ello se explican las transiciones entre los respaldos y la composición
de la diferencia, pero no se puede afirmar cuáles de las 66 renuncias originales
fueron reemplazadas, reincorporadas o contadas con otro criterio. Tampoco se atribuye
una causa de error al resumen ni se escoge una de las tasas por personas.

## QA y reanudación

**C:** uniones únicas; identidad y contexto concordantes; sumas 528/527 y 66;
14 carreras reproducidas; conciliación de las transiciones y comparación independiente
coincidentes. Se verificaron hashes antes/después de todas las entradas y de ambas
copias V16. No se exportaron identificadores. Ver `QA.json`.

**B/D:** rama feature/ire-2026; HEAD antes/después
80ca13a5a249a1a2bd53a699f5f73689b1f53040. Sin modificación de bases, denominadores,
reglas, V16, archivos de revisiones anteriores ni cambios previos. Sin commit/push.
El cálculo vigente 462/528 = 87,50% por matrículas se conserva.

Punto de reanudación E: obtener la nómina que alimentó Hoja2!C32:C50 o un registro
de cálculo que permita reconstruirla. Reutilizar estas uniones verificadas; no
clasificar los dos CODCLI ausentes como renuncias ni forzar la conciliación por total.
