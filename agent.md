# Reglas Agénticas para IA

## Repositorio único IPSS (2026-10-15)

El usuario eligió un solo repositorio con módulos separados. Caracterización se
integra en `procesos/caracterizacion`; sus reglas locales siguen aplicando.
Leer `docs/unificacion_proyectos_y_reglas_negocio_20261015.md` y
`PROYECTO_IPSS.json`. La consulta SIES histórica y los catálogos anuales activos
del módulo utilizan recursos comunes del contenedor. No exportar nuevas copias
al módulo ni confundir sus archivos heredados con fuentes activas.
Los originales externos quedan como respaldo; la integración no fusiona historias
Git ni autoriza borrar proyectos, publicar fuentes o ejecutar pipelines reales.

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

## 6. Separación anual SIES (2026-10-13)

- Leer `docs/CATALOGOS_SIES_POR_ANIO.md` antes de cambiar oferta, equivalencias o modalidad.
- MU2026 permanece congelado; no actualizar su catálogo raíz, puente o motor con oferta 2027.
- Nuevos consumidores: `common/catalogos_sies.py`, con año explícito. Código SIES
  solo con candidato único; en 2027 modalidad por unanimidad entre candidatos
  respaldados, con estados separados. No modificar el comportamiento 2026.
- `common/`, `scripts/` y `tests/` se usan justificadamente para esta capa: respetan
  el layout operativo existente y evitan mover o importar el motor congelado.
- `data/catalogos_sies/` contiene snapshots sin datos de estudiantes. No confundir
  oferta completa, equivalencias internas completas y autorización para una carga MU.
- Revisión activa 2027: `5910_20260907_6047_20261013_modalidad_v2`. Leer
  `docs/REVISION_EQUIVALENCIAS_6047_20261013.md`: 17 equivalencias completadas,
  35 pendientes. La oferta 6047 aporta componentes SIES, no CODCARPR; no quitar
  SP ni elegir versión para forzar cruces. Exportar con el empaquetador gobernado,
  sin modificar los congelados ni fuentes personales.
- Modalidad y código no son el mismo control: leer
  `docs/RESOLUCION_MODALIDAD_INDEPENDIENTE_2027.md`. Se conserva modalidad si todos
  los candidatos coinciden, sin rellenar código ni escoger versión. La promoción
  del paquete consumidor exige hash del descriptor anterior y conserva su copia.
- Aclaración del usuario 2026-10-13: validar MODALIDAD del reporte de oferta;
  no inferirla de SP ni jornada, ni pedir confirmación de ese supuesto. La
  columna homónima de DatosAlumnos es escolar. La existencia de modalidad en
  la oferta no prueba la equivalencia pendiente entre CODCARPR y esa fila.
- La revision de 52 registros (14 CODCARPR) esta en
  `docs/REVISION_52_REGISTROS_PENDIENTES_2027.md`. Las coincidencias nominales
  propuestas no son alias aprobados: no copiarlas a equivalencias ni quitar SP
  para promoverlas. El maestro U+ requerido corresponde a UP-26/UP-27.
- No declarar resuelta la diferencia de matrícula por lograr igualdad artificial
  de totales. Conservar conteos de matrículas y personas por separado.
- Diferenciar copia local, seguimiento Git y publicación remota. El hash de una
  fuente ignorada por Git no significa que esté respaldada en GitHub.

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

## Código SIES personal para seguimiento (2026-10-23)

- Consultar `PROYECTO_IPSS.json → recursos_comunes → diccionario_sies_seguimiento`
  y `docs/DICCIONARIO_SIES_SEGUIMIENTO.md` antes de reconstruir una versión para
  seguimiento T1/T2/T3. No copiar diccionarios ni elegir versiones por totales.
- Reutilizar el código documental anual atribuido o la correspondencia interna
  aprobada solo en su contexto; conservar ambos respaldos separados. Revisar
  únicamente las excepciones y cambios de contexto, sin extrapolar versiones.
- Este servicio no cambia motores de carga, vigencia, cohortes ni denominadores.
  Identificadores y respuestas individuales permanecen fuera de Git.

---
Última actualización: 2026-04-09
Responsable: Arquitectura Técnica

## Normalización de documentos y dígito verificador (2026-10-27)

- Nunca usar `x or ""` para normalizar un documento o dígito verificador:
  el valor numérico cero es válido y no debe convertirse en vacío. Distinguir
  explícitamente `None` de `0` y verificar variantes numéricas y de texto.
