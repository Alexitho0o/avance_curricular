# Fase B — Evaluación histórica de equivalencias

Autorización: «procede», 2026-10-15, sobre el plan de tres fases que complementa
H1–H8. Esta especificación precede a la implementación.

## Alcance

Evaluar sin perder registros los 141 códigos SIES, 236 planes UMAS y 513
candidatos H5. Reutilizar la agrupación y las equivalencias de programa existentes.
Agregar la oferta nacional íntegra gobernada y comparar oferta/MRUN por año y
Código Único. El año de primera oferta se calcula por código completo, separado
de matrícula, Año Inicio formal y fechas de asignación de plan.

La salida es una evaluación versionada; no cambia H5, los paquetes activos,
el Excel ni los motores congelados. `common/`, `scripts/` y `tests/` siguen el
layout auxiliar autorizado en agent.md. No se leen identidades de estudiantes.

## Reglas ejecutables

1. La clave de candidato es una lista JSON ordenada con CODCARPR, CODPESTUD,
   sede, jornada y nombre interno; el destino SIES se registra por separado.
   Se preservan espacios interiores, sufijos, valores ausentes y nombres literales.
2. RE→2, CO→3 y D→1, V→2, O→4 se usan exclusivamente como lectura del candidato
   2026, según H5. No constituyen una tabla histórica de equivalencias aprobada.
3. Toda fila del CSV institucional conserva sus 69 campos y su número de registro
   lógico. El archivo nacional original permanece completo en su gzip gobernado.
4. Comparar oferta y MRUN solo con el mismo código y año. Igualdad literal,
   diferencia y desconocido son estados distintos. La ausencia de MRUN nunca
   elimina oferta; la ausencia de oferta nunca elimina un código MRUN.
5. Comparar nombre interno del candidato con nombre del catálogo de planes;
   una diferencia requiere revisar el alias y no autoriza a reemplazarlo. El
   nombre formal proviene de oferta, con modalidad y tipo de plan separados.
6. Régimen UMAS se toma de observaciones coincidentes por plan, carrera, jornada
   y año 2026. Solo SEMESTRAL/TRIMESTRAL se traducen a etiquetas de unidad; no
   son conversiones de duración ni prueba de vigencia de la malla en ese año.
   La observación no contiene sede: la sede procede del catálogo, no de la nota.
7. Niveles de asignaturas no equivalen automáticamente a duración formal.
   Mostrar niveles, régimen y duraciones originales con estado no comparable
   hasta acreditar definición y conversión. Tipo de plan, modalidad y nivel UMAS
   ausentes permanecen desconocidos; no se extraen de prefijos ni del nombre.
8. Primera actividad anterior a primera oferta es una alerta entre observaciones,
   no una contradicción temporal definitiva ni una razón automática de descarte.
9. Una candidatura única sigue pendiente si falta relación explícita plan↔SIES
   y ámbito temporal. No se habilitan reglas nuevas con estos insumos. La
   asignación individual por período es un contrato adicional, distinto de la
   equivalencia entre programas y planes.
10. Los cambios de atributos dentro de un mismo código se registran entre años
    observados; no se adjudican causas ni se aplica el manual 2027 retroactivamente.

## Entregables y aceptación

`data/versiones_historicas_sies_umas/fase_b_20261015/`: perfiles SIES anuales,
conciliación oferta/MRUN, cambios de atributos, evaluación de cada candidato,
cobertura completa SIES y UMAS, brechas con evidencia requerida y resumen.
Las salidas incluyen referencias a fuentes y localizadores, sin RUT ni CODCLI.
El generador verifica hashes, rechaza entradas duplicadas o ediciones distintas,
no sobrescribe resultados diferentes y permite verificar reproducción sin escribir.

Pruebas: vacío distinto de coincidencia, jornada 3 distinta de 4, no inferir
modalidad, no convertir niveles, no asignar por año/sufijo, no unir años diferentes,
claves sin colisiones, universo íntegro, determinismo e integridad de fuentes.
La aceptación técnica no equivale a acreditar los vínculos: se publicarán por
separado cobertura evaluada, relaciones acreditadas y evidencia pendiente.
