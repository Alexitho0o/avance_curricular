# Plan de Implementación

| FASE | OBJETIVO | ENTRADAS | SALIDAS | DEPENDENCIAS | SCRIPT_PROPUESTO | PRUEBAS | GATES | BLOQUEOS | REANUDACION | ESTADO |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 00A-R | Validar carga rectificada | Manifiestos | Estado rectificado | Ninguna | validar_carga_congelada.py | hashes | 4 fuentes activas | B04 | revalidar hashes | COMPLETADA |
| 04 | Gobernanza por columna | Matriz normativa, contratos | TSV por columna | 00A-R | no aplica | conteo 42 campos | sin PDF activo | B03 | regenerar gobernanza | COMPLETADA |
| 04B | Catálogo de validaciones | Instructivo TXT | catálogos TSV | 04 | no aplica | conteo validaciones | reglas separadas | B03 | regenerar catálogos | COMPLETADA |
| 04D | Perfil institucional | PROMEDIOS congelado | perfiles TSV | 00A-R | perfilar_fuentes_institucionales.py | sin muestras reales | privacidad | B03/B04 | re perfilar | COMPLETADA |
| 05-CAR | Implementar Carreras | Precarga + fuentes planes | control Carreras | B03 cerrado | procesar_carreras.py; validar_carreras.py; congelar_catalogo_planes.py | sintéticas | unidad/total/distribución | B03/B05 | reanudar por manifest | PENDIENTE |
| 05-MAT | Implementar Matrícula | Precarga + catálogo Carreras + historial | control Matrícula | Carreras validada | procesar_matricula.py; validar_matricula.py; validar_cruces.py | sintéticas | cruces y acumulados | B03/B05 | reanudar por manifest | PENDIENTE |
| 11-12 | Control y PES | controles aprobados | control/PES | gates cero | generar_control.py; generar_pes.py; auditoria_final.py | end-to-end | cero bloqueos | B05 | manifest ejecución | PENDIENTE |

No se crean scripts productivos en esta fase.
