# Reglas operativas CNED

1. CNED se trabaja como modulo separado bajo `cned/`.
2. No se debe modificar el flujo MU2026/PES_READY desde scripts CNED.
3. Todo archivo final debe tener auditoria asociada.
4. Toda salida debe generarse en `cned/resultados/`.
5. Todo insumo original debe conservarse en `cned/data/input/`.
6. No se deben sobrescribir resultados anteriores sin version o timestamp.
7. Los scripts CNED deben vivir en `cned/scripts/`.
8. Las validaciones CNED deben vivir en `cned/tests/` o en scripts `cned/scripts/validar_*.py`.
9. Si falta fuente oficial o instructivo de carga, no se debe inventar logica de completitud.
10. Si un archivo puede pertenecer a MU2026 o CNED y no hay certeza, no se mueve ni modifica; se documenta para revision manual.
