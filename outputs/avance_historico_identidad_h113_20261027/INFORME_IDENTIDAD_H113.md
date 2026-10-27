# Identidad H113: efecto aislado y respaldo pendiente

## Contexto [B/C/D]

Proceso Avance Curricular SIES 2026, actividad anual 2025 y acumulada hasta 2025.
Universo preservado: 2.371 registros de precarga. Esta revisión continúa la Fase 1;
no recalcula retención ni cambia sus denominadores. No se generó un Excel.

## Hito 1/3 · Reutilización de evidencia [B/C]

Se reutilizaron las cuatro fuentes y los hashes de
`outputs/avance_historico_origen_h113_20261027/MANIFEST_ORIGEN_H113.json`, el
algoritmo H94D del commit 3067c97 y los resultados previos. No se ejecutaron motores
productivos. Se mantuvieron estados A/R, A, A/E/I/R y A/E/I; períodos; año;
expansión por CODCLI y conteos de filas históricos.

El único cambio del escenario es conservar el cuerpo documental completo en lugar
de quitar su último carácter. El DV se comprobó separadamente en Hoja1. Esto aísla
el efecto de la llave, **no establece un nuevo cálculo aprobado ni resuelve la
atribución multicarrera**. No se usaron nombres, sexo o nacimiento para enlazar.

## Hito 2/3 · Resultado del escenario [B/C/E]

Las seis columnas del algoritmo histórico, sin el mapeo externo faltante, vuelven
a coincidir con H113 en 2.370 registros. La diferencia restante corresponde a la
misma fila documentada previamente.

Conservar el documento completo cambia los conteos de **27 registros**. Los 27
tienen asignaturas localizadas por cuerpo y DV exactos en Hoja1 de PROMEDIOS 7804.
La existencia de ese enlace es una comprobación adicional: el escenario aún
conserva la expansión histórica por CODCLI y no filtra carrera/plan.

Las siete llaves compartidas dentro de la precarga afectan **14 registros**; los
otros **13 registros afectados** colisionan con documentos presentes en PROMEDIOS
que no forman otro par de la precarga. No deben sumarse 14 y 27.

| Clase | Campo (unidades, no estudiantes) | Reproducción anterior sin mapeo | Escenario cuerpo completo sin mapeo | Cambio aislado |
|---|---|---:|---:|---:|
| B/C | Cursadas 2025 | 21.377 | 21.232 | −145 |
| B/C | Aprobadas 2025 | 17.616 | 17.509 | −107 |
| B/C | Cursadas acumuladas | 47.193 | 46.667 | −526 |
| B/C | Aprobadas acumuladas | 41.615 | 41.138 | −477 |

[E] Estas diferencias no son todavía una rectificación de carga ni prueba de que
cada unidad eliminada sea académicamente improcedente. Confirman que la llave
histórica mezcla cuerpos documentales y altera los conteos. H113 conserva además
las 12 unidades del registro no recuperado: no deben confundirse con las
reducciones aisladas de esta tabla. El escenario difiere de H113 en 28 filas:
27 por la llave y una por falta de reproducción de su enlace.

### Registro pendiente: documento P [B/C/E]

- En H113: tipo P, DV vacío, I162S2C1J2V4, PLAN_ESTUDIOS=1, ambos semestres SI y
  12 unidades en cada uno de los cuatro conteos.
- En PROMEDIOS 7804: el número exacto no se localiza en Hoja1, DatosAlumnos,
  Matricula_2025 ni base_datos. No equivale a ausencia de actividad de la persona.
- En `IPSS_Procesamiento.xlsx`, hoja `2025_carga`: existe una fila con el mismo
  N_DOC (BU), un RUT interno (J), DV (BV) y el mismo código SIES, componentes
  CD:CI. El cuerpo del RUT es el mismo número buscado: no aporta otra identidad
  que permita llegar a PROMEDIOS. Se comprobó que no hay ceros iniciales que
  expliquen la falta de coincidencia.
- En `Final a carga`, el mismo número figura como **tipo R con DV**, a diferencia
  del P sin DV en H113. Se conserva la discrepancia; no se transforma P en R.
- La consulta común del diccionario exige RUT y DV. No se inventó un DV para
  consultar el documento P como si fuera RUT. No se modificó el diccionario.
- El maestro de KPI y el libro previo de Avance Curricular contienen el documento
  en hojas de salida/precarga, pero las coincidencias revisadas no entregan un
  campo CODCLI asociado en esas tablas. No constituyen recuperación del mapeo.

[E] Sigue faltando `MAPEO_IDENTIDAD_CODCLI.xlsx` (SHA esperado
`ed50755cd8d56270d79e5c422dfad88434082692cf865368faca6caf1af619b7`) o evidencia
explícita equivalente que enlace esa fila con el CODCLI y sus asignaturas de
origen. Las tres fuentes adicionales se buscaron por valor exacto; su cobertura
por hoja se registra en BUSQUEDA_PUENTE_FALTANTE.json. No se afirma ausencia
universal ni se atribuyen las 12 unidades mediante semejanza.

## Hito 3/3 · QA y preservación [B/C/D]

18 controles aprobados: hashes de fuentes, reproducción del resultado anterior,
encabezados del puente, fuente del catálogo, preservación de cambios ajenos,
rama y HEAD. El estado `PASS_CONTROLES_ESCENARIO_NO_ADOPTADO` se refiere a esta
auditoría: **no es PASS funcional integral de Avance Curricular**.

El hash del puente coincide con el catálogo gobernado:
`e2984ccdf22ecf35c46e1f77275fdd12cda47bd2d77a523860e2cd2cf90127f4`.
Se verificó el SHA de las tres fuentes complementarias antes y después de leerlas.
Los identificadores se procesaron exclusivamente en memoria. No se guardaron
nombres, RUT, números documentales ni CODCLI individuales en estas salidas.

Rama: `feature/ire-2026`; HEAD antes/después:
`262f445828f7e939fac59c3cc76d0bb20a101746`. Sin commit/push. Las fuentes, bases,
diccionario y denominadores permanecen intactos. No se tocaron las auditorías
anteriores ni sus decisiones.

## Checkpoint: continuar sin repetir [C/E]

1. La causa técnica de las colisiones documentales ya está aislada; no repetir
   el inventario completo ni las siete búsquedas. Mantener el escenario separado.
2. Revisar atribución carrera/plan de las filas multicarrera, reutilizando las
   equivalencias aprobadas y las llaves completas. Los 489 registros alertados
   anteriormente no equivalen automáticamente a 489 errores ni personas distintas.
3. La fila P permanece pendiente en paralelo; consultar únicamente un respaldo
   que aporte enlace explícito CODCLI o el mapeo histórico, no volver a buscar
   el mismo número en las tres fuentes ya agotadas.
4. No extender todavía el conteo histórico como regla validada ni adoptar el
   escenario sin comprobar atribución al programa. No reabrir mallas ni títulos.

## Reproducción [C]

Desde la raíz del repositorio, con pandas y openpyxl:

```sh
python3 outputs/avance_historico_identidad_h113_20261027/revisar_identidad.py
python3 outputs/avance_historico_identidad_h113_20261027/buscar_puente_faltante.py
```

El primer script consulta el diccionario mediante su servicio verificado en
solo lectura y escribe únicamente agregados de auditoría. El segundo busca el
documento exacto en tres libros identificados y publica solo cobertura, campos
y hashes. El informe y la especificación describen la revisión; el manifiesto
congela las huellas de esta entrega.
