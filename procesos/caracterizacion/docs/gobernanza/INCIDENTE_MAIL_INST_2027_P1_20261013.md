# Bloqueo por Mail_Inst en 2027 P1

Actualizacion posterior autorizada el 2026-10-13: el bloqueo global descrito aqui es historico y fue reemplazado por seguimiento individual. La politica vigente esta en `POLITICA_INCORPORACION_CORREO_2027_P1.md`; no restablecer el bloqueo global durante una revision. Los diagnosticos originales se conservan intactos.

Fecha del diagnostico inicial: 2026-10-13. Estado historico: **BLOQUEADO POR DATO DE ORIGEN**. Se implemento y verifico la mejora de diagnostico; la ejecucion de financiamiento no esta resuelta mientras no se complete el correo institucional real en la fuente.

## Causa y recorrido

El comando vigente de `COMANDOS_MAC_WINDOWS.md` entra por `procesar_financiamiento_diario.sh`. El ejecutor crea una carpeta nueva y llama a `scripts/gobernanza/resolver_fuentes_operativas.py --anio 2027 --periodo 1`. `main()` usa `resolve_sources()` con encuesta 141234, lee resultados y, al encontrar registros, aplica el preflight del flujo con respuestas.

El resolutor llama a `eligible_students()` y `shared_operational_rules()` de `caracterizacion_sin_respuestas.py`, normaliza los tokens existentes y entrega los elegibles sin token a `token_import_frame()`. La condicion original era `invalid = ~result['email'].str.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', na=False)` y `if invalid.any(): raise ValueError(...)`. `main()` captura `ValueError`, imprime `[FUENTES][BLOQUEO]` y devuelve 3. El lanzador termina antes de ejecutar `caracterizacion.py`.

La validacion de correo ocurre **despues** de ano/periodo, ano de ingreso, firma, vigencia/situacion, programas excluidos, RUT administrativos y control de duplicados elegibles. Tambien ocurre despues de retirar los estudiantes que ya tienen token. No se encontro una exclusion omitida que explique este caso.

La auditoria del registro confirma: ANOMATRICULA=2027, PERIODOMATRICULA=1, ANOINGRESO=2027, ESTADOACADEMICO=VIGENTE, CON_FIRMA=SI, situacion regular, programa elegible y RUT no administrativo. Existe una sola fila de ese estudiante en la fuente; no existe otra fila con Mail_Inst valido. La columna seleccionada por nombre es `Mail_Inst`, posicion 24 desde cero (Y). La lectura directa con openpyxl confirma una celda realmente vacia, sin formula, espacios ni caracteres invisibles. El NaN observado en pandas representa esa ausencia, no el texto literal «nan».

El identificador, la fila y la coordenada exacta se conservan solo en la auditoria privada. No se sustituyo por MAIL personal, no se invento un correo y no se retiro al estudiante del universo.

## Fuentes seleccionadas realmente

No habia overrides RUTA_* en la sesion. Para matricula y promedios el selector usa el mayor `(st_mtime_ns, nombre)` entre archivos con prefijo y extension admitidos. Tokens/resultados se seleccionan exclusivamente por encuesta 141234. Habia una unica copia candidata por cada prefijo relevante en Descargas.

| Rol | Archivo en Downloads | SHA-256 |
| --- | --- | --- |
| Matricula | DATOSDEALUMNOS_11923.xlsx | 780b4085bf34176317146c50d8c17fb0938bbe102c65976d44ec2df7a85ebd39 |
| Participantes | tokens_141234.csv | 6683e415d1998e6ff51b0a73f81368ef73f8c43edd7021bd540141531463e777 |
| Resultados | results-survey141234.xlsx | dbeb187be26e41ffe964e2a8e8dc0917d7aa54d7e544740320b19a26665b8668 |
| Auxiliar opcional | PROMEDIOSDEALUMNOS_7804.xlsx | 83a0ba72b21d25dd0d151b75fb0182a1f55bbe3f5efba06d088c994067262fca |

Matricula contiene 266 registros de 2027 P1. Tokens/resultados corresponden al ID gobernado 141234; contienen 237 participantes y 15 filas de resultados, respectivamente. Hay 14 completed distintos de N. Por tanto, **no corresponde activar SIN_RESPUESTAS_CONFIRMADAS** con estas fuentes.

El auxiliar de promedios es la copia historica del 4 de julio, cuyo hash coincide con el auxiliar gobernado de 2026 P2. No se certifica como una exportacion propia de 2027 P1. Es opcional y no participa en este bloqueo; con el corte despues de financiamiento sus bloques de analisis academico quedan fuera de la ejecucion. No se modifico ni se sustituyo.

El log original `2026-10-13/2027_P1_082730/03_LOGS/run_financiamiento_2027_P1_20261013_082730.log` contiene solo el bloqueo. No tenia manifiesto ni hashes de seleccion; no permite demostrar retrospectivamente identidad binaria de las entradas. La reproduccion registra las fuentes actuales y sus hashes.

## Conciliacion real

| Concepto | Registros |
| --- | ---: |
| Fuente completa | 14990 |
| Fuera de 2027 P1 | 14724 |
| Matricula 2027 P1 | 266 |
| Excluidos unicos del periodo | 4 |
| Excluidos por estado/situacion | 3 |
| Excluidos por firma | 1 |
| Excluidos por ano de ingreso / programa / RUT administrativo | 0 / 0 / 0 |
| Elegibles | 262 |
| Elegibles ya con token | 235 |
| Elegibles pendientes de incorporacion | 27 |
| Mail_Inst validos entre todos los elegibles | 261 |
| Mail_Inst validos entre pendientes de incorporacion | 26 |
| Registros bloqueados por Mail_Inst | 1 |

Conciliaciones: 14990 = 14724 + 266; 266 = 4 + 262; 262 = 235 + 27; 27 = 26 + 1. En esta fuente las tres exclusiones por estado y la exclusion por firma son disjuntas. Los contadores diagnosticos por motivo pueden superponerse en otras fuentes: `EXCLUIDOS_UNICOS_PERIODO` conserva el conteo de union. No se aplico una deduplicacion destructiva ni se eligio otra trayectoria para obtener un correo.

## Cambios implementados

- `caracterizacion_sin_respuestas.py`: `InstitutionalEmailError` conserva los afectados para auditoria, sin identificadores en el mensaje publico. `institutional_email_valid()` mantiene el control de sintaxis y rechaza caracteres Unicode de control/formato incrustados; solo recorta espacios externos. `token_import_frame()` sigue leyendo exclusivamente Mail_Inst, sin fallback a MAIL.
- `write_private_email_audit()` conserva las filas del mismo estudiante, indices/filas, valor original, nulidad, puntos Unicode, filtros y existencia de otro correo institucional. Escribe archivos nuevos bajo `.local/auditoria_correos/<id>/`, ignorado por Git, con directorio privado y archivos con permisos 600. `MANIFIESTO_DIAGNOSTICO.json` guarda fuentes, hashes y conciliacion.
- El resolutor anuncia las fuentes antes de la validacion y, al bloquear, muestra elegibles, incorporaciones, correos validos/bloqueados, ruta privada y el campo de origen que debe corregirse. No emite exports para continuar despues del error.
- El modo sin respuestas valida todos los elegibles sin token antes de escribir cualquier salida operativa y registra el mismo diagnostico privado. No se usa ese modo en esta reproduccion real.
- `eligible_students()` añade conteos de fuente, fuera de periodo y excluidos unicos; no cambia sus filtros.

La mejora resuelve un diagnostico insuficiente y endurece el rechazo de caracteres invisibles. **La causa de este bloqueo concreto es la fuente vacia**, no esos caracteres ni un defecto en el orden de filtros. No se modificaron `caracterizacion.py`, el contrato de comandos ni las referencias congeladas de FCU 2026 durante esta intervencion. Se conservaron los cambios preexistentes del repositorio y no se realizo commit ni push.

## Pruebas y reproduccion

Pasaron 62 pruebas focalizadas: 10 nuevas en `tests/test_correos_institucionales.py`, 7 de modo sin respuestas, 9 de comandos operativos, 16 de seleccion LimeSurvey y 20 de fuentes congeladas P2. La suite nueva cubre el caso real con nulo y correo personal disponible, formatos validos/invalidos, espacios y Unicode, columnas reordenadas/ausentes, exclusiones, duplicados, correo en otra fila excluida, estudiantes ya inscritos, auditoria privada, preflight y bloqueo antes de exportar en modo sin respuestas. Las fuentes de prueba son sinteticas.

Comandos de prueba:

```bash
python3 -m unittest discover -s tests -p 'test_correos_institucionales.py' -v
python3 -m unittest discover -s tests -p 'test_sin_respuestas.py' -v
python3 -m unittest discover -s tests -p 'test_comandos_operativos.py' -v
python3 -m unittest discover -s tests -p 'test_limesurvey_selection.py'
python3 -m unittest discover -s tests -p 'test_h044_fuentes_congeladas_p2.py'
```

La ejecucion real repitio el **mismo comando del incidente**, sin overrides ni analisis anual, y termino correctamente bloqueada con codigo **3**. Carpeta nueva:

`/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/0_caracterizacion/2026-10-13/2027_P1_083639/`

Log: `03_LOGS/run_financiamiento_2027_P1_20261013_083639.log`. `02_SALIDAS` quedo vacia. No se generaron CSV parciales para los 26 casos validos, ni resultados financieros, ni carga FCU.

Auditoria privada de la reproduccion:

`.local/auditoria_correos/2588af156674496aa245a2472ae3cb7f/REGISTROS_BLOQUEADOS_PRIVADO.json`

Manifiesto en esa misma carpeta: `MANIFIESTO_DIAGNOSTICO.json`. Comprobacion directa del Excel y validacion real en `.local/incidentes/2027_P1_mail_20261013/`. Son datos locales ignorados por Git y no deben publicarse.

Se verifico en memoria que los 26 candidatos validos obtienen email exactamente de Mail_Inst recortado, sin generar un CSV importable. Los CSV anteriores quedan preservados: la advertencia ya existente sobre la primera corrida 20261009_133242 sigue vigente; esa version inicial no debe utilizarse para incorporacion. No se afirma que todos los CSV historicos sean seguros.

Se comprobaron los hashes de 38 archivos previos de corridas 2027 P1 y copias de Escritorio: ninguno cambio. Los 51 archivos congelados de FCU 2026 pasaron la verificacion antes y despues. Compilacion Python, sintaxis Bash y `git diff --check` correctos.

## Dato pendiente y reutilizacion del comando

Completar **Mail_Inst con el correo institucional real asignado al estudiante identificado en la auditoria privada**, en la fila de matricula afectada. Corregir el sistema de origen y obtener un nuevo DATOSDEALUMNOS, o corregir la fuente administrativa con evidencia; no rellenar MAIL personal ni retirar al estudiante elegible.

El mismo comando puede reutilizarse despues de esa correccion. Si se reexporta el archivo, confirmar en el terminal que el selector tomo esa version o proporcionar RUTA_MATRICULA explicita. La presente validacion acredita la mejora de diagnostico y la continuidad del control, no una ejecucion exitosa posterior a un dato que aun falta.
