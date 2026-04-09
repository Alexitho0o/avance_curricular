# Reporte Conciliacion Precarga PES

Fecha: 2026-06-18 11:18:24

## Precarga

- Estado: PRECARGA_OFICIAL_ENCONTRADA
- Archivo original: `estudiantes_extranjeros_2026/Reporte Precarga del Proceso Extranjeros Regulares 2026.csv`
- Copia raw: `estudiantes_extranjeros_2026/data/raw/REPORTE_PRECARGA_EXTRANJEROS_REGULARES_2026_ORIGINAL.csv`
- SHA-256 original: `6d0fe6a9a9357ec6e0efc7e5866c512de5ba708f80a2100c39ee9a283da2bff3`
- Registros: 185
- Columnas: 21
- Delimitador: `;`
- Codificacion: `cp1252`

## Conciliacion

- Estados conciliacion: {'SOLO_PRECARGA': 134, 'COINCIDE_PERSONA_DATOS_CONFLICTIVOS': 8, 'COINCIDE_PRECARGA_Y_LOCAL': 32, 'COINCIDE_PERSONA_DIFIERE_CODIGO_UNICO': 33, 'SOLO_MATRICULA_LOCAL_2025': 50}
- Clasificaciones universo: {'PRECARGA_PENDIENTE_CONFIRMACION': 134, 'CONFLICTO_DOCUMENTO': 8, 'PRECARGA_CONFIRMADA': 32, 'CONFLICTO_CARRERA': 33, 'AGREGADO_MATRICULA_2025': 48, 'NACIONALIDAD_PENDIENTE': 2}
- Decisiones propuestas: {'MANTENER_PENDIENTE_CONFIRMACION_2025': 134, 'MANTENER_PENDIENTE_RESOLVER_DOCUMENTO': 4, 'MANTENER_VIGENCIA_1': 32, 'MANTENER_PENDIENTE_RESOLVER_CARRERA': 15, 'AGREGAR_PENDIENTE_RESOLVER_CARRERA': 18, 'AGREGAR_PENDIENTE_RESOLVER_DOCUMENTO': 4, 'AGREGAR_CANDIDATO_INSTITUCIONAL': 50}
- Revision 104 locales: {'COINCIDENCIA_SOLO_PERSONA': 22, 'SOLO_LOCAL_2025': 50, 'COINCIDENCIA_EXACTA': 32}
- Validacion: {'PENDIENTE': 361, 'ADVERTENCIA': 12}
- Respaldo previo: `estudiantes_extranjeros_2026/backups/pre_conciliacion_precarga_20260618_111824`

## Tabla de cierre

| Indicador | Cantidad |
|---|---:|
| Registros precarga | 185 |
| Personas unicas precarga | 185 |
| Registros locales 2025 | 104 |
| Coincidencias exactas | 32 |
| Coincidencias por persona | 41 |
| Solo precarga | 134 |
| Solo matricula local 2025 | 50 |
| Agregados propuestos | 72 |
| Eliminaciones propuestas | 0 |
| Pendientes | 257 |
| Conflictos | 12 |
| Universo conciliado | 257 |

## Decision

No se genero archivo final PES. La base conciliada requiere resolver brechas de residencia, origen, codigos unicos y registros sin evidencia local antes de una carga definitiva.
