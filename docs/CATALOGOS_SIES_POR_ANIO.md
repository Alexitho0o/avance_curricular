# Catalogos SIES por ano: contrato de implementacion

Fecha de decision: 2026-10-13. Alcance: oferta, equivalencias internas y consulta
de modalidad para Matricula Unificada y consumidores como Caracterizacion.

## Separacion obligatoria

- El motor MU2026, su comando oficial, DURACION_ESTUDIOS.tsv, el puente compilado,
  las reglas de sede y las entregas congeladas no se modifican con oferta 2027.
- La nueva capa vive en `data/catalogos_sies/` y se consulta indicando el ano.
  No existe ano predeterminado ni seleccion por archivo mas reciente.
- El reporte validado 5910 del 07-09-2026 respalda la oferta 2027 de etapas 1 y 2.
  No equivale al reporte final 5909 ni certifica aranceles de etapa 3.
- La aceptacion de la carga de etapa 3 esta documentada como confirmacion del
  usuario; no reemplaza un comprobante tecnico de plataforma.
- El Excel de enlaces IP SAN SEBASTIAN contiene 14 programas: es evidencia
  complementaria, no la fuente del universo completo de 140 combinaciones.

## Identidad y equivalencias

El codigo unico SIES identifica institucion, sede, carrera, jornada y version.
La modalidad se obtiene del campo explicito de oferta, nunca de MODALIDAD escolar.
La consulta interna requiere CODCARPR, sede y jornada; nombre y version permiten
restringir candidatos. Sin un candidato unico no se asigna codigo SIES. En 2026
se conserva la regla anterior tambien para modalidad. En 2027 modalidad_v2,
modalidad se informa si todos los candidatos respaldados coinciden; los estados
de codigo y modalidad se separan. Ver [contrato vigente](RESOLUCION_MODALIDAD_INDEPENDIENTE_2027.md).
No se elige la primera fila, la version maxima ni la modalidad mayoritaria.
Jornada 3 (semipresencial) y 4 (distancia) permanecen distintas. O representa 4,
no ambos valores. RE=2, CO=3; PTG=4 se registra solo para 2027, respaldado por
la sede Patagonia del reporte 5910 y la definicion institucional de PTG.

Las equivalencias 2026 solo se heredan a 2027 para el MISMO codigo unico presente
en la oferta 2027, conservando sus filas y fuente. Los codigos nuevos requieren
equivalencia explicita respaldada: nunca se inventa CODCARPR por semejanza de
nombre ni se transfiere una version o sede distinta. Las faltantes se publican
como pendientes, sin ocultar programas de la oferta.

La carga de una equivalencia nueva exige ano, CODIGO_UNICO, CODCARPR, nombre
interno y evidencia documental. La fuente debe existir y su SHA-256 coincidir.
Las equivalencias no resuelven por si solas la elegibilidad de estudiantes.

## Reproducibilidad y controles

Fuentes fijadas por SHA-256. Cada catalogo registra ano, fuente, filas de origen,
modalidad, sede, jornada, version, plan y equivalencias. El registro apunta a una
version explicita y a su hash. No se reemplazan snapshots diferentes en sitio.

Pruebas: aislamiento anual, claves completas, sedes, version ambigua, jornada
3/4, datos ausentes, conflictos, fuentes alteradas, equivalencias sin evidencia,
repetibilidad y preservacion de las referencias 2026.

## Matricula: conciliacion independiente

La verificacion de totales NO actualiza catalogos ni modifica estudiantes.
Pregrado usa VIG=1/2; VIG=0 se informa separado. Contar registros de matricula
y personas unicas por separado. Postitulo usa su esquema propio de 21 campos.
No sumar cargas parciales como si fueran universos disjuntos.

La conciliacion historica compara el consolidado institucional de julio 2026
con la copia adjunta del informe SIES 2026. Publicacion 3371 y consolidado
vigente 3145 dejan una diferencia de 226 en pregrado; postitulo 54/54.
Se verificaran nuevamente desde las fuentes. Una coincidencia agregada no
prueba identidad individual ni aceptacion de la carga. Sin cadena completa de
cargas aceptadas, estado `DISCREPANCIA_NO_EXPLICADA`, nunca `RESUELTO`.
Solo se versionan controles agregados y hashes, no RUT, nombres o correos.

## Limite operativo

Esta capa no habilita una carga MU2027 ni cambia automaticamente el pipeline
historico. Los consumidores nuevos deben usar el resolutor anual explicito y
conservar sus estados. Un catalogo completo de oferta con equivalencias
pendientes no se presenta como un puente completamente resuelto.

## Uso y reproduccion

Desde la raiz de `avance_curricular`, solo consulta (Mac; en Windows usar `python`):

```bash
python3 scripts/consultar_catalogo_sies.py --anio 2027 --codigo-unico I162S2C10J1V1
python3 scripts/consultar_catalogo_sies.py --anio 2027 --codcarpr CODIGO_INTERNO --sede RE --jornada O
python3 -m unittest discover -s tests -v
```

`CODIGO_INTERNO` es un marcador: sustituir por el CODCARPR real. Puede requerirse
`--version` o `--nombre` exacto para obtener una coincidencia unica. Salida 0:
codigo resuelto; salida 2: codigo sin equivalencia o ambiguo. En 2027 ese codigo
de salida no implica que la modalidad este pendiente: leer estado_modalidad.
No estimarla por mayoria. Las consultas requieren snapshots y REGISTRO.json.

Reproducir el snapshot INICIAL, con las fuentes originales locales y sus hashes,
en un destino nuevo (el registro activo ya contiene una revision posterior):

```bash
python3 scripts/generar_catalogos_sies_por_anio.py --salida /ruta/nueva/catalogos_iniciales
```

La misma entrada produce los mismos bytes. Un cambio de fuente, equivalencia o
salida existente diferente se bloquea. Para una revision, documentar evidencia,
actualizar la version 2027 en `fuentes.json` y generar en un destino nuevo con
`--salida`; revisar antes de promover el registro. Conservar el registro anterior,
su conciliacion y su snapshot. Nunca borrar snapshots para forzar regeneracion.
2028 requiere agregar un contrato de fuente y pruebas; no hay fallback a 2027.

La revision de equivalencias es `5910_20260907_6047_20261013`. Su
[contrato y resultados](REVISION_EQUIVALENCIAS_6047_20261013.md) conservan
fuentes.json y el snapshot inicial; reconstruyen el cruce con evidencia adicional:

```bash
python3 scripts/revisar_equivalencias_6047.py \
  --reporte "/ruta/reporte_dinamico_6047_2026-10-13_18:28:03.csv" \
  --alumnos "/ruta/DATOSDEALUMNOS_11941.xlsx"
python3 scripts/exportar_catalogo_caracterizacion.py --destino "/ruta/CARACTERIZACION"
```

Estos comandos no ejecutan Matricula ni Caracterizacion. La revision se promueve
con `--promover` solo desde el registro inicial esperado y conserva el registro
anterior; repetir la misma promocion es idempotente. El exportador copia el
catalogo activo 2027 y el resolutor con hashes, nunca datos personales. Bloquea
archivos existentes diferentes: para una futura revision se debe gobernar y
validar expresamente el cambio del descriptor del consumidor, sin borrar versiones.

La revision activa `5910_20260907_6047_20261013_modalidad_v2` conserva esas
equivalencias y separa la modalidad del codigo exacto. Reproduccion y resultados
en [resolucion independiente](RESOLUCION_MODALIDAD_INDEPENDIENTE_2027.md).

El reporte 5910 original y `control/catalogos/PUENTE_SIES_COMPILADO.tsv` estan
ignorados por Git. Conservarlos en su respaldo autorizado: son requisitos de
regeneracion, aunque la consulta de los snapshots no los necesita. No se cambiaron
las exclusiones de Git ni se publico material en remoto en esta implementacion.
En un clon sin originales se omite solo la prueba de regeneracion real; las
pruebas sinteticas y de consulta de snapshots siguen siendo obligatorias.

La conciliacion usa rutas explicitas, nunca el archivo mas reciente:

```bash
python3 scripts/conciliar_matricula_publicada.py --anio 2026 --fecha 2026-10-13 \
  --pregrado "/ruta/MATRICULA_UNIFICADA_PREGRADO_2026_CONSOLIDADA_FINAL_CON_ENCABEZADOS.xlsx" \
  --postitulo "/ruta/matricula_unificada_2026_postgrado_postitulo.csv" \
  --publicacion "/ruta/Informe_Matricula_Educacion_Superior_2026_SIES.xlsx" \
  --salida "/ruta/nueva/CONCILIACION_MATRICULA_2026.json"
```

Este comando retorna exito al producir una auditoria valida, incluso si su
`estado` es `DISCREPANCIA_NO_EXPLICADA`: no confundir ejecucion correcta con
conciliacion cerrada. Los totales y hashes son publicables; las fuentes con datos
personales permanecen fuera de esta carpeta. No autoriza reprocesar ni enviar MU.
