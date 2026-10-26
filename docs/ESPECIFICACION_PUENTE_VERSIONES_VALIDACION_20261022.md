# Validación local del puente UMAS–SIES

D: Encargo del usuario de 2026-10-22. Estado PENDIENTE_APROBACION_GOBERNANZA.
C: Ejecución aislada en data/reglas_negocio/20261022_puente_versiones/validacion_local_v1.
Lectura de fuentes originales, hashes antes/después, cruce exacto RUT/DV exclusivamente en memoria local. Distinguir evidencia histórica de evidencia del mismo año. No resolver identidad mediante nombres, sexo o nacimiento. Contar personas distintas por celda; las celdas de distintos años o códigos no son aditivas.
D: Umbral propuesto 90% y tres personas no basta sin validación de tipo de plan y conciliación MU. La ausencia de atributos acreditados bloquea promoción.
C: Segunda lectura e implementación SQL SQLite en memoria para QA. Ninguna base individual persistida. No editar motores, catálogos, tasas, denominadores ni fuentes. Fase 7 solo borradores, sin commit ni push.
E: Si hay diferencias contra derivados previos, documentarlas y no promover el diccionario. Preservación por hash no acredita por sí sola conciliación semántica de retención.
