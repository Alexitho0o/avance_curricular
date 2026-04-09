# Diseño Pipeline Matrícula Avance Curricular 2026

No implementado productivamente.

1. Cargar precarga congelada.
2. Validar hash contra manifiesto.
3. Validar estructura y primera columna institucional.
4. Preservar campos no modificables.
5. Cargar catálogo validado de Carreras.
6. Asignar PLAN_ESTUDIOS solo con evidencia.
7. Cargar actividad 2025-1.
8. Cargar actividad 2025-2.
9. Calcular anual cursado.
10. Calcular anual aprobado.
11. Calcular acumulado cursado.
12. Calcular acumulado aprobado.
13. Tratar convalidaciones, validación de estudios y RAP explícitamente.
14. Validar unidad de medida.
15. Validar contra total del plan.
16. Aplicar control de tolerancia 25%.
17. Resolver vigencia con evidencia.
18. Clasificar duplicados.
19. Generar auditoría.
20. Generar archivo de control con encabezado.
21. Gate de aprobación.

Gates: Carreras validada, plan existente, unidad consistente, anual/acumulado separado, no se reemplazan desconocidos por cero.
