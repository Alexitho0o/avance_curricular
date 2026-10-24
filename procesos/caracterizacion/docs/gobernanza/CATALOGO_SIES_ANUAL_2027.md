# Catalogo SIES anual en el analisis 2027

Decision 2026-10-13. Oferta y equivalencias son gobernadas en avance_curricular.
Caracterizacion consume una copia portable fijada por SHA-256, no consulta rutas
del computador ni busca archivos mas recientes en Descargas durante la ejecucion.

## Alcance

- Solo 2027: el adaptador rechaza 2026 y anos no gobernados. La conexion al
  flujo diario ocurre en `publish_trajectory_analysis`, exclusivo de 2027 P1.
- Se agregan columnas a `Trayectorias_institucionales` en `05_ANALISIS` y un
  resumen de cobertura en `04_AUDITORIA`. No alterar correo, archivos de
  participantes, reglas de firma, estado, primer ingreso ni exclusiones.
- La fuente cruda y sus columnas se conservan. MODALIDAD de DatosAlumnos es
  escolar: no se consume ni se reemplaza por la modalidad de carrera.
- Cada fila conserva su indice. La cobertura se cuenta en registros, no personas.

## Claves y reglas

Se exige CODCARPR + SEDE + JORNADA. El catalogo contiene equivalencias explicitas
heredadas y otras verificadas por nombre exacto + sede + jornada en reporte 6047
y DatosAlumnos. El nombre puede desambiguar una equivalencia, pero no se usa
semejanza, eliminacion del sufijo SP ni primera/version maxima como criterio.
Un alias explicito unico puede conservar su nombre institucional diferente del
nombre oficial SIES; no se exige reescribir la carrera de DatosAlumnos.

Para versiones multiples observadas se conservan todos los candidatos, aunque
una version sola tuviera alias heredado en 2026. Desde la revision modalidad_v2,
la modalidad se resuelve si TODOS los candidatos respaldados tienen el mismo
valor valido, aunque el codigo SIES siga ambiguo. Nunca elegir version, primera
fila ni mayoria. Si no hay match o las modalidades difieren, se muestra
`No determinada`, no se descarta a la persona ni se cambia su elegibilidad.
La falta de una dimension deja `DATOS_INSUFICIENTES` en esa fila. Un paquete
ausente, alterado o de otro ano es un error de integridad, no un cero de cobertura.

## Archivos y trazabilidad

- `gobernanza/sies/anual/ACTIVO_2027.json`: version y hashes autorizados.
- `2027/<version>/catalogo.json`: oferta, equivalencias y ambiguedades.
- `EVIDENCIA_DIMENSIONES.json`: dimensiones de programas sin RUT, nombres de
  estudiantes, CODCLI ni correos; fuentes originales identificadas por hash.
- `REVISION_EQUIVALENCIAS.json`: resultado individual de las 52 pendientes.
- `POLITICA_MODALIDAD.json`: decision versionada de separar modalidad y codigo.
- `resolutor.py`: copia exacta y verificada del modulo de avance_curricular.
- `caracterizacion_catalogo_sies_2027.py`: adaptador local, sin dependencia del
  otro repositorio instalado. No editar manualmente el resolutor copiado.

Actualizar mediante otra revision del catalogo, nueva exportacion controlada y
pruebas. No editar el snapshot, la evidencia ni los hashes para ocultar cambios.
Las 51 referencias FCU2026 y el analisis anual 2026 permanecen sin modificaciones.

## Resultado inicial conservado

Version anterior `5910_20260907_6047_20261013`: 140 codigos SIES de oferta 2027,
105 con alguna equivalencia interna y 35 sin ella. De las 52 pendientes iniciales,
17 se completaron, 6 siguen ambiguas por version y 29 sin cruce exacto respaldado.
Esto no equivale a cobertura del 100% de matriculas ni autoriza cargar PES.

El adaptador agrega CODIGO_UNICO_SIES, MODALIDAD_CARRERA, ESTADO_CRUCE_SIES,
CANDIDATOS_SIES, FUENTE_MODALIDAD y VERSION_CATALOGO_SIES a Matricula periodo;
agrega la hoja Cobertura SIES. Antecedentes historicos se conserva sin enriquecer.
En 04_AUDITORIA se registra AUDITORIA_CATALOGO_SIES_2027_P1_<fecha>.json y el
terminal informa conteos por estado, version y ausencia de cambio de elegibilidad.
Los manifiestos existentes recogen esos archivos en sus carpetas respectivas.

Auditoria de la fuente 11941: 271 registros con ANOMATRICULA=2027/PERIODO=1,
88 resueltos (43 Presencial, 45 No presencial), 131 ambiguos y 52 sin equivalencia.
Los 183 no resueltos conservan No determinada. Sin filtros de firma, estado ni
primer ingreso, estos totales NO representan personas unicas o elegibles.
Detalle reproducible sin RUT ni correos:
`COBERTURA_CATALOGO_SIES_2027_P1_11941_20261013.json`.

Comando de auditoria, independiente del proceso productivo:

```bash
python3 scripts/gobernanza/auditar_catalogo_sies_2027.py \
  --alumnos "/ruta/DATOSDEALUMNOS_11941.xlsx" --periodo 1 \
  --salida "/ruta/nueva/COBERTURA_SIES_2027_P1.json"
```

No se ejecutaron las corridas diarias ni el analisis anual completo para esta
integracion. La proxima corrida habitual 2027 P1 incluira los campos; las
entregas anteriores no fueron reescritas. Cambios locales, aun sin commit/push.

Validacion: 102 pruebas `*2027.py` aprobadas (7 especificas del catalogo),
38 pruebas de catalogos/conciliacion en avance_curricular y 51 referencias
congeladas FCU2026 verificadas, cero incidencias. Baseline FCU:
`85e265f5d317ed6b1f2d595cc9ce415628c9c7aa94822152092052723a67e294`.

## Revision vigente: modalidad_v2

Version activa `5910_20260907_6047_20261013_modalidad_v2`. No cambia la oferta ni
agrega equivalencias: conserva 140 codigos, 105 con alias y 35 sin alias. Cambia
solo la determinacion de modalidad y su trazabilidad, por autorizacion del usuario.
Reemplaza expresamente la instruccion anterior que ocultaba la modalidad ante
cualquier version ambigua. Una modalidad resuelta no acredita un codigo SIES.

- ESTADO_CODIGO_SIES: RESUELTO, AMBIGUO, SIN_EQUIVALENCIA o DATOS_INSUFICIENTES.
- ESTADO_CRUCE_SIES conserva el mismo valor, para compatibilidad.
- ESTADO_MODALIDAD: RESUELTA_CODIGO_UNICO, RESUELTA_COINCIDENCIA_CANDIDATOS,
  AMBIGUA, SIN_EQUIVALENCIA o DATOS_INSUFICIENTES.
- En Matricula periodo se agregan los dos estados. Cobertura SIES informa
  Control/Estado/Registros; cada control concilia por separado, no sumarlos
  como si fueran personas distintas. Terminal y JSON incluyen ambos controles.

Resultado verificado, misma fuente 11941 y mismo alcance de 271 registros:

| Modalidad | Registros |
|---|---:|
| Presencial | 57 |
| No presencial | 162 |
| No determinada | 52 |

219/271 registros tienen modalidad (80,8%). El codigo SIES permanece igual:
88 resueltos, 131 ambiguos, 52 sin equivalencia. No son personas unicas ni el
universo elegible. De los 52 sin cruce, 51 tienen sufijo SP y 1 es TGEIN.
No se homologaron SP/V a semipresencial sin respaldo. El usuario aclaro que se
debe validar contra la columna de modalidad, no confirmar supuestos por sufijo.
El catalogo ya consume MODALIDAD del reporte de oferta (6047: columna 6), no
COD_JORNADA. La columna homonima de DatosAlumnos (Hoja1!AE) es escolar y no es
intercambiable. Los pendientes corresponden a la equivalencia con CODCARPR:
disponer de modalidad en la oferta no identifica que fila corresponde al codigo
interno cuando hay varias modalidades o nombres distintos. No pedir una regla
SP -> semipresencial como reemplazo de evidencia de ese vinculo.
Tampoco se afirmo equivalencia de Tecnico Veterinario SP con el nombre SIES
extendido por mera similitud.

Auditoria vigente: `COBERTURA_CATALOGO_SIES_2027_P1_11941_20261013_MODALIDAD_V2.json`.
La anterior se conserva; mismo hash fuente, mismas claves/candidatos y registros.
Descriptor anterior respaldado en ACTIVO_ANTERIOR.json dentro de la nueva
revision. El exportador requiere --reemplazar-descriptor-sha256 para promover
otra version sobre una instalada. No editar hashes ni el resolutor copiado.

Verificacion final de modalidad_v2: 103 pruebas focalizadas `*2027.py`
(8 del catalogo), 47 de catalogos/conciliacion en avance_curricular; 150 aprobadas.
Las 51 referencias FCU2026 y las cinco referencias MU2026 conservan sus hashes.
Registro/catalogo 2026 y cuatro archivos del paquete consumidor anterior intactos;
cinco archivos del paquete actual verificados. Regeneracion y exportacion
idempotentes. No se ejecuto el reporte diario ni se reemplazaron entregas previas.

## Revision posterior de los 52 pendientes

El 2026-10-13 se revisaron los diccionarios, hoja matriz de Promedios, reporte
6047, entrega de Docencia etapa 2 y enlaces de programas. Resultado: 14 CODCARPR
representan los 52 registros; no aparecio un enlace explicito nuevo con SIES.
No se promovio otra version ni se alteraron las 219 modalidades determinadas.

Hay 21 registros con candidato nominal unico, 16 con varias modalidades posibles,
14 con nombre Veterinario distinto del oficial y 1 TGEIN sin coincidencia nominal.
Son propuestas NO_APLICADAS, no equivalencias. No eliminar SP ni transformar V
a jornada 3 usando esas propuestas. UP-26/UP-27 del diccionario maestro ya
documentan el maestro de oferta/codigo unico que falta en U+.

La evidencia se gobierna en el repositorio de origen avance_curricular:
`docs/REVISION_52_REGISTROS_PENDIENTES_2027.md` y
`data/catalogos_sies/auditorias/20261013_pendientes_52/REVISION_PENDIENTES.json`.
Dos documentos complementarios de OneDrive (planilla de aranceles y redisenyo
curricular) no pudieron leerse por timeout/dataless; no se presentan como revisados.
