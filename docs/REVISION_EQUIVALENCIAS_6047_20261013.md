# Revision de equivalencias con reporte 6047 y DatosAlumnos

Contrato de implementacion, 2026-10-13. No sustituye los congelados MU2026.

Antecedente conservado. La [revision modalidad_v2](RESOLUCION_MODALIDAD_INDEPENDIENTE_2027.md)
mantiene todas estas equivalencias, pero reemplaza la regla de exigir codigo
unico para informar modalidad: ahora informa la modalidad unanime entre los
candidatos respaldados. La cobertura de modalidad antigua de esta auditoria
no describe la version vigente; los conteos de codigos si se conservan.

## Evidencia y limites

- Reporte aportado: `reporte_dinamico_6047_2026-10-13_18:28:03.csv`.
  Clave construida literalmente con CODIGO_IES_NUM, COD_SEDE, COD_CARRERA,
  COD_JORNADA y VERSION. No trae CODCARPR. No atribuir validacion PES final.
- Contiene las 140 combinaciones 2027 de la fuente 5910 y 21 diplomados adicionales.
  Corroborar igualdad de los atributos usados; no ampliar el universo a diplomados.
- DatosAlumnos: `DATOSDEALUMNOS_11941.xlsx`, Hoja1. CODIGOCARRERA es un codigo
  interno, no el SIES. Leer solo dimensiones academicas; no guardar RUT, nombres
  de estudiantes, correos ni CODCLI en la evidencia versionada.
- Diccionario operativo: DURACION_ESTUDIOS y su puente. La especificacion
  Bettersoft UP-24/25/26/27 distingue codigo interno, jornada interna y codigo
  unico SIES; no demuestra una equivalencia inexistente ni autoriza elegir version.

## Regla de incorporacion

Coincidencia exacta tras normalizar mayusculas, tildes y espacios de NOMBRE_L con
NOMBRE_CARRERA, mas sede RE=2/CO=3/PTG=4 y jornada D=1/V=2/O=4. Debe existir un
solo codigo SIES candidato entre todas las versiones. No quitar palabras, SP,
CONTINUIDAD ni abreviaturas para forzar una coincidencia. Varios alias internos
pueden apuntar al mismo codigo si cada uno tiene esta evidencia exacta.

Las observaciones historicas de DatosAlumnos respaldan la identidad del programa,
no prueban matricula vigente 2027. Registrar anos observados y conteos de filas,
sin cambiar filtros de estado, firma o trayectoria de Caracterizacion.

Si una dimension observada tiene varios codigos candidatos, registrar un bloqueo
de ambiguedad en la nueva revision: una equivalencia heredada para una version
no prueba que esa sea la version de una matricula actual. No elegir V mayor,
primera coincidencia ni atribuir modalidad por mayoria.

## Versionado e integracion

- Preservar los snapshots 2026 y 2027 iniciales. Guardar otra revision 2027 con
  fuentes reducidas no personales, sus hashes, cruces, pendientes y controles.
- Promover solo la entrada 2027 de REGISTRO.json tras validacion; guardar copia
  del registro anterior. No modificar fuentes.json ni el generador historico.
- Caracterizacion recibe copia portable del snapshot y resolutor, ambos fijados
  por SHA-256. No depender de una ruta Mac al otro repositorio ni de Descargas.
- Enriquecer solo el analisis interno 2027. No escribir en la fuente, mutar
  elegibilidad, modificar el correo ni alterar CSV de incorporacion.
- Probar hashes, cardinalidad, ambiguedad, ausencia de datos y rechazo de 2026.
  Evaluar cobertura con la fuente actual sin ejecutar el pipeline productivo.

## Resultado comprobado

Revision activa: `5910_20260907_6047_20261013`.

| Revision de las 52 combinaciones SIES pendientes | Codigos |
|---|---:|
| Completadas con evidencia exacta | 17 |
| Pendientes por version ambigua | 6 |
| Pendientes sin cruce exacto | 29 |
| Total revisado | 52 |

La oferta conserva 140 codigos: 105 con alguna equivalencia interna y 35 sin
ella. Tener alguna equivalencia no garantiza que cada matricula resuelva una
version unica. Se agregaron 19 entradas de equivalencias, que completan 17
codigos antes vacios; no son 19 estudiantes ni 19 carreras distintas.

| Codigo SIES completado | CODCARPR respaldado |
|---|---|
| I162S2C10J1V1 | TPRRE |
| I162S2C10J2V1 | TPRRE |
| I162S2C114J1V1 | TEIQ |
| I162S2C11J1V1 | TMIRE |
| I162S2C131J4V1 | ICEX |
| I162S2C134J4V1 | IIART |
| I162S2C135J4V1 | IOPMI |
| I162S2C140J4V1 | TIART |
| I162S2C142J4V1 | TOPMI |
| I162S2C22J1V1 | IACI, IEMORE |
| I162S2C48J4V1 | TCIOL |
| I162S3C114J2V1 | COTEIQ |
| I162S3C115J2V1 | COTFAR |
| I162S3C91J2V1 | COTENS |
| I162S4C114J2V1 | PMTEIQ |
| I162S4C115J2V1 | PMTFAR |
| I162S4C91J2V1 | PMTENS |

Las seis pendientes por version son I162S2C47J4V2, I162S2C57J4V2,
I162S2C6J4V3, I162S2C78J2V2, I162S2C78J4V2 e I162S2C79J4V2.
El detalle individual de las 52 y los candidatos de todas las dimensiones
ambiguas esta en `data/catalogos_sies/2027/5910_20260907_6047_20261013/REVISION_EQUIVALENCIAS.json`.

## Lo que falta, no inferir

El reporte 6047 tiene los cinco componentes del codigo SIES. DatosAlumnos
contiene 14.995 registros historicos y CODIGOCARRERA coincide con CODCARPR en
todos: no contiene la clave completa SIES ni una version SIES de la matricula.
Para completar el puente falta evidencia de la relacion entre programa interno,
sede, jornada/plan y codigo SIES, particularmente version y semipresencialidad.
No se resuelve descargando otra vez la misma oferta. Los programas sin un alumno
observado no quedan demostrados por ausencia: requieren su diccionario oficial.

## Impacto en Caracterizacion, sin ejecutar el flujo diario

Lectura de `DATOSDEALUMNOS_11941.xlsx`, Hoja1, filtro ANOMATRICULA=2027 y
PERIODOMATRICULA=1. Se conserva cada fila y sus valores originales:

| Estado de cruce de registros | Registros |
|---|---:|
| RESUELTO | 88 |
| AMBIGUO | 131 |
| SIN_EQUIVALENCIA | 52 |
| Total | 271 |

Los 88 resueltos tienen 43 modalidad Presencial y 45 No presencial. Los otros
183 quedan como No determinada. Este control incluye todos los estados y
firmas: NO es el universo elegible ni un conteo de personas unicas. Los 52
registros sin equivalencia NO son las 52 combinaciones iniciales de oferta.

El paquete portable en Caracterizacion conserva copia exacta del catalogo,
resolutor y evidencia reducida con SHA-256. Su auditoria reproducible queda en
`docs/gobernanza/COBERTURA_CATALOGO_SIES_2027_P1_11941_20261013.json` de ese
repositorio. No modifica ni el correo ni las listas de incorporacion.

Los originales CSV/XLSX permanecen en su ubicacion y no se incorporan a Git.
La evidencia reducida permite reproducir el cruce sin datos personales; los
hashes identifican los originales, no prueban su respaldo remoto. Los cambios
de esta revision son locales, sin commit ni publicacion en GitHub.

## Validacion ejecutada

- 38 pruebas de catalogos, revision y conciliacion aprobadas en avance_curricular.
- 102 pruebas focalizadas 2027 aprobadas en Caracterizacion, incluyendo lectura
  del paquete portable, integridad, preservacion de filas y publicador real con
  datos sinteticos en carpetas temporales. No es una corrida de produccion.
- Cruce de las 52 reproducido desde evidencia reducida, sin los XLSX/CSV privados.
- Cinco referencias MU2026 verificadas contra fuentes.json y entrada 2026 del
  registro igual a REGISTRO_ANTERIOR.json. Catalogo y resolutor del consumidor
  identicos a los del repositorio de origen.
- 51 referencias congeladas FCU2026 verificadas, cero incidencias. Baseline
  `85e265f5d317ed6b1f2d595cc9ce415628c9c7aa94822152092052723a67e294`.
- `git diff --check` sin incidencias en ambos repositorios.
