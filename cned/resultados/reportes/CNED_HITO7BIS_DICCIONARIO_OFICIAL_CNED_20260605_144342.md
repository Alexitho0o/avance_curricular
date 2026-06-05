# CNED Hito 7 BIS - Diccionario oficial aplicado

## Resumen

- Fecha de generación: 2026-06-05T14:43:44
- Manual/fuente principal: `indices_2025/docs/Manual_INDICES_2025 2.txt`
- Base real auditada: `cned/resultados/archivos_subida/CNED_BASE_SANEADA_PRELIMINAR_HITO5_20260605_135231.xlsx`
- Hoja real auditada: `CANDIDATO_CARGA_LIMPIO`
- Campos del diccionario manual: 36
- Columnas reales mapeadas: 81
- Campos confirmados oficiales: 15
- Campos confirmados de formulario: 21
- Campos no confirmados en manual: 36
- Campos auxiliares técnicos: 3
- Dictamen: **DICTAMEN_FINAL: HITO7BIS_DICCIONARIO_OFICIAL_CNED_GENERADO**

## Fuente usada

Se usó como fuente normativa principal el Manual INDICES local disponible en
`indices_2025/docs/Manual_INDICES_2025 2.txt`. La sección más relevante detectada es
**Tabla 21: Nuevos Programas**, complementada con **Tabla 22: Evolución Programas**
y **CSV Evolución Carreras** para campos de evolución/carga.

No se usó conocimiento externo ni búsqueda web. Cuando el manual no confirmó una
etiqueta o equivalencia, el campo quedó como `NO_CONFIRMADO_EN_MANUAL` o
`REQUIERE_REVISION_MANUAL`.

## Impacto sobre Hito 6

- Campos Hito 6 antes clasificados con bloqueo/marca: 57
- Campos Hito 6 confirmados por manual o equivalencia: 24
- Campos Hito 6 auxiliares excluibles de carga: 4
- Campos Hito 6 que siguen no confirmados: 24

### Campos bloqueantes confirmados

| campo             | tipo_campo       | CAMPO_MANUAL_MAPEADO            | RECLASIFICACION_HITO7BIS   | IMPACTO_HITO7BIS                           |
|:------------------|:-----------------|:--------------------------------|:---------------------------|:-------------------------------------------|
| Régimen           | OFICIAL_PROBABLE | Tipo Régimen                    | OFICIAL_CNED_CONFIRMADO    | CAMPO_CONFIRMADO_POR_MANUAL_O_EQUIVALENCIA |
| VIGENCIA_CARRERA  | OFICIAL_PROBABLE | Estado de la carrera o programa | OFICIAL_CNED_CONFIRMADO    | CAMPO_CONFIRMADO_POR_MANUAL_O_EQUIVALENCIA |
| ANIO_INICIO       | OFICIAL_PROBABLE | Año de Inicio de actividades    | OFICIAL_CNED_CONFIRMADO    | CAMPO_CONFIRMADO_POR_MANUAL_O_EQUIVALENCIA |
| AREA_ACTUAL       | OFICIAL_PROBABLE | Área actual                     | OFICIAL_CNED_CONFIRMADO    | CAMPO_CONFIRMADO_POR_MANUAL_O_EQUIVALENCIA |
| NOMBRE_TITULO     | OFICIAL_PROBABLE | Título                          | OFICIAL_CNED_CONFIRMADO    | CAMPO_CONFIRMADO_POR_MANUAL_O_EQUIVALENCIA |
| REGIMEN           | OFICIAL_PROBABLE | Tipo Régimen                    | OFICIAL_CNED_CONFIRMADO    | CAMPO_CONFIRMADO_POR_MANUAL_O_EQUIVALENCIA |
| REQUISITO_INGRESO | OFICIAL_PROBABLE | Requisito ingreso               | OFICIAL_CNED_CONFIRMADO    | CAMPO_CONFIRMADO_POR_MANUAL_O_EQUIVALENCIA |

### Campos que siguen sin confirmación suficiente

| campo                          | tipo_campo                  |   total_marcas | IMPACTO_HITO7BIS              |
|:-------------------------------|:----------------------------|---------------:|:------------------------------|
| EXPERIENCIA_LABORAL            | FORMULARIO_CNED_DESCONOCIDO |             71 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| FECHA_ADMISION_INICIAL         | FORMULARIO_CNED_DESCONOCIDO |             71 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| Ingreso Directo                | FORMULARIO_CNED_DESCONOCIDO |             71 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| LICENCIA_ENS_MEDIA             | FORMULARIO_CNED_DESCONOCIDO |             71 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| MAIL_DIFUSION_CARRERA          | FORMULARIO_CNED_DESCONOCIDO |             71 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| NOTAS_ENS_MEDIA                | FORMULARIO_CNED_DESCONOCIDO |             71 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| OTROS_REQUISITOS               | FORMULARIO_CNED_DESCONOCIDO |             71 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| Observaciones                  | FORMULARIO_CNED_DESCONOCIDO |             71 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| PERFIL_EGRESO                  | FORMULARIO_CNED_DESCONOCIDO |             71 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| PROMEDIO_MIN_ENS_MEDIA         | FORMULARIO_CNED_DESCONOCIDO |             71 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| RECONOCIMIENTOS_APREN_PREVIOS  | FORMULARIO_CNED_DESCONOCIDO |             71 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| VALOR_CERTIFICADO_DIPLOMA      | FORMULARIO_CNED_DESCONOCIDO |             71 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| Ingreso otro                   | FORMULARIO_CNED_DESCONOCIDO |             35 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| Otro Tipo de Ingreso           | FORMULARIO_CNED_DESCONOCIDO |             35 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| AREA_ADMIN_DERECHO             | FORMULARIO_CNED_DESCONOCIDO |             11 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| AREA_AGRI_SILVI_PESCA_VET      | FORMULARIO_CNED_DESCONOCIDO |             11 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| AREA_ARTES_HUMANIDADES         | FORMULARIO_CNED_DESCONOCIDO |             11 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| AREA_CIENCIAS_NAT_MAT_ESTAD    | FORMULARIO_CNED_DESCONOCIDO |             11 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| AREA_CS_SOCIAL_PERIODISMO_INFO | FORMULARIO_CNED_DESCONOCIDO |             11 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| AREA_EDUCACION                 | FORMULARIO_CNED_DESCONOCIDO |             11 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| AREA_INGE_INDUSTRIA_CONSTRUC   | FORMULARIO_CNED_DESCONOCIDO |             11 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| AREA_SALUD_BIENESTAR           | FORMULARIO_CNED_DESCONOCIDO |             11 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| AREA_SERVICIOS                 | FORMULARIO_CNED_DESCONOCIDO |             11 | SIGUE_NO_CONFIRMADO_EN_MANUAL |
| AREA_TECNO_INFO_COMUNICA       | FORMULARIO_CNED_DESCONOCIDO |             11 | SIGUE_NO_CONFIRMADO_EN_MANUAL |

## Recomendación

1. Ajustar Hito 5/Hito 6 para usar este diccionario y no tratar como desconocidos los campos confirmados por Manual INDICES.
2. Mantener fuera de la carga solo campos `AUXILIAR_TECNICA` claros, conservándolos en trazabilidad.
3. Resolver marcas técnicas en campos oficiales/formulario confirmados con fuente institucional; confirmar existencia del campo no equivale a completar su valor.
4. No generar archivo final CNED hasta reejecutar el saneamiento y validar contra instructivo/estructura oficial de carga.

## Advertencia

Este Hito 7 BIS no genera archivo final de subida CNED. Solo entrega diccionario,
mapeo, reclasificación e impacto metodológico.
