# Modalidad independiente del codigo SIES, 2027

Decision del usuario 2026-10-13: proceder con la separacion de estados propuesta
tras revisar reporte 6047 y DatosAlumnos 11941. Sustituye para 2027 la regla de
exigir un codigo unico antes de informar modalidad. No cambia el contrato 2026.

## Reglas

- Conservar el cruce por equivalencias de nombre documentadas, sede y jornada;
  no usar MODALIDAD escolar de DatosAlumnos ni inferir version por alumno nuevo.
- CODIGO_UNICO_SIES solo se completa con un candidato. ESTADO_CODIGO_SIES
  mantiene RESUELTO, AMBIGUO o SIN_EQUIVALENCIA. ESTADO_CRUCE_SIES permanece
  como alias compatible de ese estado, no del estado de modalidad.
- ESTADO_MODALIDAD es RESUELTA_CODIGO_UNICO si hay un candidato valido;
  RESUELTA_COINCIDENCIA_CANDIDATOS si varios candidatos respaldados tienen
  exactamente la misma modalidad valida. No usar mayoria, primera coincidencia
  ni seleccionar una version. Con modalidades diferentes: AMBIGUA.
- Sin candidato: SIN_EQUIVALENCIA. Datos de cruce ausentes: DATOS_INSUFICIENTES.
  Un valor de modalidad desconocido o inconsistente en el catalogo es un error
  de integridad, no se cuenta como modalidad resuelta.
- Preservar la lista de candidatos y la version del catalogo. No modificar
  elegibilidad, estados academicos, firma, historial ni columnas fuente.

## SP y diferencias de nombre

La revision documental anterior no demostro una equivalencia institucional de
los nuevos CODCARPR con sufijo SP. Aclaracion del usuario 2026-10-13: la modalidad
debe validarse con la columna fuente existente; no suponerla por el sufijo ni
solicitar que confirme su significado como sustituto del dato.

En reporte 6047, MODALIDAD es la sexta columna y el constructor consume ese
encabezado literalmente: 1 Presencial, 2 Semipresencial, 3 No presencial.
COD_JORNADA y VERSION son campos diferentes. En DatosAlumnos 11941, Hoja1!AE
tambien se llama MODALIDAD, pero contiene modalidad escolar (por ejemplo,
TECNICO-PROFESIONAL), no modalidad de carrera. No intercambiar esos campos.

Que la oferta declare modalidad no resuelve por si solo el vinculo con CODCARPR.
Ejemplo comprobado: Enfermeria en sede 2 tiene MODALIDAD=1/JORNADA=1 o 2 y
MODALIDAD=2/JORNADA=3; TENSSP en DatosAlumnos tiene JORNADA=V y carece de una
columna de modalidad de carrera. No elegir la fila semipresencial por SP ni la
presencial solo por V. El pendiente es la equivalencia interna, no la existencia
del atributo en la oferta. Tampoco equiparar Tecnico Veterinario SP con el nombre
mas especifico SIES sin respaldo. Conservar esos casos pendientes y sus fuentes.

## Publicacion y pruebas

Crear otra revision 2027, conservar snapshots/registro anteriores y publicar
una copia portable en Caracterizacion. El cambio de descriptor requiere el
SHA-256 del anterior; no sobrescribir silenciosamente una revision distinta.
El consumidor entrega las dos distribuciones en Excel, JSON y terminal.
Las auditorias previas de cobertura permanecen inmutables.

Probar unanimidad de modalidad, conflicto, ausencia, valores invalidos, codigo
sin resolver, equivalencias por nombre, integridad, cardinalidad, repetibilidad,
portabilidad y aislamiento 2026. No ejecutar el pipeline diario completo.

## Resultado implementado

Revision `5910_20260907_6047_20261013_modalidad_v2`. Oferta y equivalencias
permanecen identicas a la revision previa: 140 codigos, 105 con equivalencia,
35 pendientes. No se asignaron versiones nuevas ni se reclasifico SP.

La auditoria de DatosAlumnos 11941 para matricula 2027 P1 conserva 271 registros:
88 codigos resueltos, 131 ambiguos, 52 sin equivalencia. Ahora la modalidad se
resuelve en 219 (57 Presencial, 162 No presencial); 52 quedan No determinada.
Estos conteos no son personas unicas ni el universo elegible de la encuesta.
Las 51 filas con sufijo SP y la de TGEIN permanecen sin cruce respaldado.

Estado/modalidad/candidatos y fuente se entregan separadamente. No se debe sumar
el control de codigo con el control de modalidad: ambos cuentan las mismas filas.
Detalle en Caracterizacion: `docs/gobernanza/COBERTURA_CATALOGO_SIES_2027_P1_11941_20261013_MODALIDAD_V2.json`.
Ninguna auditoria previa se sobrescribe. El registro anual previo y descriptor
del consumidor se respaldan dentro de la nueva revision; fuentes 2026 intactas.

Reproduccion sin datos personales:

```bash
python3 scripts/revisar_modalidad_catalogo_2027.py --promover
python3 scripts/exportar_catalogo_caracterizacion.py --destino /ruta/CARACTERIZACION
```

Para reemplazar un descriptor de version anterior, agregar al segundo comando
`--reemplazar-descriptor-sha256 HASH_ANTERIOR_VERIFICADO`. El valor debe calcularse
sobre ACTIVO_2027.json antes de la promocion. La misma version es idempotente;
otra version distinta sin hash esperado se bloquea. Nunca borrar snapshots para
eludir el control. No se hicieron commits ni publicacion remota.

## Verificacion final

- 47 pruebas de catalogos/conciliacion en avance_curricular y 103 pruebas
  focalizadas `*2027.py` en Caracterizacion: todas aprobadas (150 en total).
- Dos pruebas explicitas impiden deducir modalidad desde sufijo o jornada y
  crear una equivalencia SP sin evidencia.
- Cinco referencias MU2026 verificadas por SHA-256; catalogo y entrada 2026
  del registro anual intactos. Las 51 referencias congeladas FCU2026 pasaron
  su verificador, sin incidencias.
- Los cuatro archivos del paquete consumidor anterior conservan sus hashes;
  los cinco del actual coinciden con el descriptor. Catalogo y resolutor son
  identicos a los del repositorio de origen.
- Regeneracion/promocion y exportacion repetidas sin cambios de contenido.
  No se ejecuto el pipeline diario ni se regeneraron entregas del Escritorio.
