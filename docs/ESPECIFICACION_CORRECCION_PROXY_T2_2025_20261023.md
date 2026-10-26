# Corrección acotada del proxy T2-2025

## Alcance autorizado

D · El usuario pidió revisar las fórmulas y el script que produjeron 600, comprobar las once personas con documento P y corregir un error de cruce sin cambiar denominadores. No autoriza cambios al motor anual, diccionario SIES, otras cohortes, otras tasas ni fuentes. Sin commit ni push.

## Evidencia y método

B/C · El libro AUDITADO tiene 600 literal en `26_Avance_Curricular_Resumen!E1852`; la tasa divide por C1852=1150 y la hoja18 recibe ese resultado. El constructor recuperado en `/tmp/add_promedios_sheet.py:43-46` contiene una lista precalculada. No calcula ese cruce ni contiene exclusión P/R. La causa exacta del cálculo original permanece E.

C · Reconstruir el indicador declarado con la misma población T1-2025 y registros PROMEDIOS de ANO=2025, PERIODO=2, contando una persona una sola vez si tiene al menos un registro con ESTADO_ACADEMICO=VIGENTE. Resolver documentos P únicamente mediante la equivalencia explícita de `IPSS_Procesamiento.xlsx`, hoja2025_carga, J RUT y BU N_DOC/BV DV. Validar identidad completa y colisiones; no usar nombres, códigos SIES de destino ni inferencias.

C · Solo si los controles confirman población1150, identidades únicas y los once adicionales, reemplazar el conteo incompleto en una versión V14. Mantener disponible la diferencia antes/después en documentación agregada y enlazar las fórmulas de las vistas afectadas. Conservar el resto de las partes del libro y sus13 gráficos.

E · El resultado mide actividad del período y estado del extracto PROMEDIOS. La corrección de identidad no acredita matrícula vigente en el cierre histórico ni transforma el proxy en tasa oficial SIES. No se infiere por qué se produjo la lista original600.

## QA

C · Comparación independiente R/P, RUT+DV, personas vs. registros, denominadores y agregación por códigoT1. Recalcular fórmulas modificadas con Artifact Tool, contrastar resultados y preservar partes OOXML no afectadas; verificar tablas, XML y cachés. Exportar únicamente agregados al proyecto y copia idéntica al Escritorio; detalles personales solo en memoria. Registrar fuentes y hashes, cambios exactos, límites y Git antes/después.
