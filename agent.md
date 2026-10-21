# Reglas Agénticas para IA

Este archivo define las reglas y convenciones que deben seguir los agentes de IA que operen en este repositorio, bajo la metodología Spec-Driven Development (SDD).

## 1. Estructura del Repositorio
- **core/**: Lógica de negocio, scripts y configuración.
- **data/**: Datos de entrada, catálogos, resultados y auditorías.
- **docs/**: Documentación técnica, manuales y especificaciones.
- **archive/**: Históricos y respaldos.

## 2. Convenciones de Nombres
- Usar snake_case o kebab-case para archivos y carpetas.
- Evitar duplicados y nombres vagos.
- Los archivos de datos deben indicar claramente su propósito y versión.

## 3. Documentación
- Todo módulo debe estar documentado en docs/README.md y/o docs/DOCUMENTACION_TECNICA.md.
- Los scripts deben tener docstrings y comentarios claros.

## 4. Comportamiento de Agentes
- Respetar la jerarquía y no modificar archivos fuera de core/, data/ o docs/ sin justificación.
- Mantener la trazabilidad de cambios y registrar decisiones relevantes en docs/ o en este archivo.
- Validar la integridad de la estructura antes de ejecutar refactorizaciones masivas.

## 5. SDD y Mantenibilidad
- Toda nueva funcionalidad debe estar precedida por una especificación en docs/.
- Los cambios deben ser atómicos y fácilmente reversibles.
- Priorizar la legibilidad y mantenibilidad para humanos y agentes.

## Control de reglas VIG MU2027 (2026-10-21)

- Leer `docs/control_cambios_vig_mu2027.md` y el descriptor común
  `data/reglas_negocio/mu2027/activo.json` antes de implementar un consumidor MU2027.
- Consultar mediante `core/mu2027.py` / `common/control_reglas_mu2027.py`.
  No editar versiones congeladas ni recuperar nóminas de excepción MU2026 como
  reglas automáticas. Toda nueva versión requiere autorización, responsable,
  motivo, fecha/hora, hash anterior y alerta. Fijar versión/hash en cada ejecución.
- Las equivalencias actuales son decisiones D de revisión interna; la pendiente
  permanece E. No habilitan carga SIES2027 sin su manual y un consumidor validado.
- Mantener históricos y denominadores intactos. El estudio de envíos 2026 está
  preservado en `data/reglas_negocio/mu2027/estudio/`; no declara errores académicos.


---
Última actualización: 2026-04-09
Responsable: Arquitectura Técnica
