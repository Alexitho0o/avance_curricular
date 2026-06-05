# Bitacora Fase 2 - Validador Base

Fecha/hora: 2026-06-08 17:15:54 -04.

## Verificacion Corta

| Elemento | Resultado |
|---|---|
| Modulo `personal_academico_2026/` | Existe. |
| Carpetas base | Existen `docs/`, `insumos/`, `catalogos/`, `scripts/`, `tests/`, `resultados/`, `auditorias/` y `bitacoras/`. |
| Insumo estructura en institucion | Existe en `insumos/`. Leido con `;`: 34 columnas. Leido con `,`: 1 columna. |
| Insumo estructura fuera institucion | Existe en `insumos/`. Leido con `;`: 27 columnas. Leido con `,`: 1 columna. |
| Instructivo 2026 | Existe en `insumos/`. |
| Intervencion fuera del modulo | No se modifica nada fuera de `personal_academico_2026/`. |

## Riesgos Confirmados

- **PENDIENTE DE CONFIRMACION**: las estructuras oficiales observadas usan separador `;`, pero el instructivo menciona CSV delimitado por comas.
- **PENDIENTE DE CONFIRMACION**: las estructuras observadas tienen encabezado, pero el instructivo indica eliminar encabezados antes de subir a PES.
- **PENDIENTE DE CONFIRMACION**: existe inconsistencia documentada sobre `TIPO_ESPECIALIDAD` entre anexos y mensajes de error.
- Los CSV en `insumos/` pueden aparecer ignorados por la regla global `*.csv`, aunque existen localmente y ya fueron verificados por hash en la fase anterior.

## Proximos Pasos De Esta Fase

1. Crear configuracion centralizada del modulo.
2. Implementar utilidades puras de normalizacion y validacion.
3. Crear script CLI de validacion con auditoria.
4. Crear exportador controlado, bloqueado por auditoria por defecto.
5. Agregar fixtures sinteticos y pruebas minimas.
6. Actualizar documentacion y reporte final de fase.
