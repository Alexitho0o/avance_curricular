# Retención intertrimestral IPSS 162

Subproyecto reproducible para incorporar las hojas 18–25 de seguimiento intertrimestral al libro anual de retención IPSS 162.

## Alcance

- El libro anual existente se conserva como plantilla y sus hojas 1–17 no se recalculan ni se reemplazan.
- Las hojas nuevas se construyen desde la Matrícula Unificada del período 1 y los cortes T2/T3 entregados para 2025 y 2026.
- La unidad de análisis es la persona identificada por la llave documental disponible; cada persona cuenta una vez por corte.
- La tasa intertrimestral es un cálculo interno: personas del grupo T1 observadas como vigentes en el corte dividido por el grupo T1 seleccionado.
- No se interpreta ausencia como deserción y no se presenta como tasa oficial SIES.

## Artefacto de referencia

El libro integrado se mantiene fuera de Git porque contiene RUT y otras columnas de uso restringido en las hojas 20, 24 y 25. Su ruta, hash y estructura están en `MANIFEST_RETENCION_FOTO_INTERTRIMESTRAL_20261022.json`.

## Flujo reproducible

La copia integrada del 22 de octubre fue construida fuera de este repositorio y su constructor original no está disponible aquí. Por eso este subproyecto no declara una reconstrucción automática del libro: el script versionado valida las entradas, sus hashes y la estructura antes de una futura ejecución del autor de hojas. Esta limitación queda clasificada como E hasta incorporar el constructor de hojas aprobado.

1. Verificar hashes y estructura de las fuentes declaradas en el manifiesto.
2. Seleccionar el grupo T1 desde la Matrícula Unificada del año correspondiente, sin usar el estado de filtro visual de Excel.
3. Normalizar la llave documental sin eliminar DV ni inventar equivalencias.
4. Cruzar contra cada corte T2/T3 del mismo año y registrar presencia, estado y pendientes por separado.
5. Agregar por institución, sector y carrera; conservar denominadores y fuentes visibles.
6. Inyectar únicamente las hojas nuevas en una copia del libro plantilla y recalcular con LibreOffice.
7. Ejecutar los controles de integridad, fórmulas, duplicados y ausencia de identificadores en salidas agregadas.

## Clasificación

- A: regla SIES o manual citado en las hojas gobernadas.
- B: dato observado en una fuente.
- C: cálculo o transformación reproducible.
- D: decisión interna sobre grupo, corte o presentación.
- E: pendiente, falta de cobertura o equivalencia no demostrada.

## Restricción de datos

Las fuentes individuales y las hojas con identificadores se mantienen fuera de Git. Solo se versionan scripts, manifiestos, documentación y resultados agregados sin identificadores.

## Códigos SIES: consumidor común integrado (2026-10-23)

C: usar `scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py` desde la raíz del repositorio. Lee `PROYECTO_IPSS.json → recursos_comunes → diccionario_sies_seguimiento`; no mantiene equivalencias propias. Contrato: [consulta común](../../docs/DICCIONARIO_SIES_SEGUIMIENTO.md). Conserva código de cohorte de origen separado del código de destino y registra excepciones. Esta integración no regenera el Excel ni acredita que su constructor histórico esté incorporado.
