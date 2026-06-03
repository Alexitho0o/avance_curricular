# CNED Programas Faltantes para Crear en INDICES

## Dictamen

REQUIERE_REVISION_MANUAL

## Fuentes usadas

- Fuente principal: PROMEDIOSDEALUMNOS_7804.xlsx / hoja matriz
- Archivo físico: /Users/alexi/Documents/GitHub/avance_curricular/input/PROMEDIOSDEALUMNOS_7804.xlsx
- Fuente existentes INDICES: /Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/data/listado_referencia_cned.tsv
- Script ejecutado: /Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/scripts/07_generar_programas_faltantes_desde_promedios.py

## Conteos

- TOTAL_OFERTA_MATRIZ: 139
- TOTAL_VIGENTES: 139
- TOTAL_YA_EXISTE_EN_INDICES: 64
- TOTAL_FALTA_CREAR_EN_INDICES: 71
- TOTAL_DUDOSO_REVISAR_MANUAL: 4
- TOTAL_NO_CREAR: 0

## Reglas de cruce

- Prioridad 1: coincidencia exacta por CODIGO_UNICO.
- Prioridad 2: coincidencia auxiliar fuerte por nombre normalizado, sede, horario, modalidad, tipo de programa, tipo de carrera, duración y bucket de nivel cuando hay evidencia suficiente.
- Regla conservadora: coincidencia auxiliar fuerte se clasifica como DUDOSO_REVISAR_MANUAL, no como YA_EXISTE_EN_INDICES.
- Regla operativa: si no existe match exacto ni auxiliar fuerte y el registro está vigente, queda como FALTA_CREAR_EN_INDICES.

## Validaciones

- PROMEDIOSDEALUMNOS_7804.xlsx existe
- La hoja matriz existe en PROMEDIOSDEALUMNOS_7804.xlsx
- La hoja matriz contiene filas: 139
- CODIGO_UNICO existe y no contiene vacíos en matriz
- Todo CODIGO_UNICO no vacío cumple formato esperado
- No hay duplicados inesperados por CODIGO_UNICO en matriz
- Los derivados de CODIGO_UNICO son coherentes con COD_SEDE
- Existe base de programas ya existentes en INDICES/SIES
- El cruce por CODIGO_UNICO se ejecutó
- PROGRAMAS_FALTANTES_PARA_CREAR contiene solo FALTA_CREAR_EN_INDICES
- PROGRAMAS_FALTANTES_PARA_CREAR no tiene CODIGO_UNICO vacío
- PROGRAMAS_FALTANTES_PARA_CREAR no tiene duplicados por CODIGO_UNICO
- Todos los campos de pantalla están presentes en la hoja principal
- Las clasificaciones finales cubren todo el universo matriz
- Todos los códigos esperados del usuario existen en OFERTA_MATRIZ_NORMALIZADA
- El Excel final contiene todas las hojas obligatorias
- El CSV tiene la misma cantidad de filas que PROGRAMAS_FALTANTES_PARA_CREAR
- El JSON coincide con el conteo de PROGRAMAS_FALTANTES_PARA_CREAR
- El Markdown instruye usar la hoja PROGRAMAS_FALTANTES_PARA_CREAR

## Programas faltantes

- Hoja principal: PROGRAMAS_FALTANTES_PARA_CREAR
- Muestra: [{"CODIGO_UNICO": "I162S2C101J4V1", "Nombre": "DIPLOMADO EN SALUD FAMILIAR CON ENFOQUE COMUNITARIO", "Sede": "Santiago"}, {"CODIGO_UNICO": "I162S2C102J4V1", "Nombre": "DIPLOMADO SALUD CON FOCO EN MIGRACION", "Sede": "Santiago"}, {"CODIGO_UNICO": "I162S2C103J4V1", "Nombre": "DIPLOMADO ABORDAJE INTEGRAL DE LA VIOLENCIA DE GENERO EN ATENCION PRIMARIA DE SALUD", "Sede": "Santiago"}, {"CODIGO_UNICO": "I162S2C104J4V1", "Nombre": "DIPLOMADO EN INNOVACION PARA LA DOCENCIA", "Sede": "Santiago"}, {"CODIGO_UNICO": "I162S2C105J4V1", "Nombre": "DIPLOMADO EN HUMANIZACION EN SALUD", "Sede": "Santiago"}, {"CODIGO_UNICO": "I162S2C10J1V1", "Nombre": "TECNICO EN PREVENCION DE RIESGOS", "Sede": "Santiago"}, {"CODIGO_UNICO": "I162S2C10J4V1", "Nombre": "TECNICO EN PREVENCION DE RIESGOS", "Sede": "Santiago"}, {"CODIGO_UNICO": "I162S2C111J4V1", "Nombre": "INGENIERIA EN FINANZAS", "Sede": "Santiago"}, {"CODIGO_UNICO": "I162S2C111J4V2", "Nombre": "INGENIERIA EN FINANZAS", "Sede": "Santiago"}, {"CODIGO_UNICO": "I162S2C112J4V1", "Nombre": "INGENIERIA EN MARKETING DIGITAL", "Sede": "Santiago"}, {"CODIGO_UNICO": "I162S2C112J4V2", "Nombre": "INGENIERIA EN MARKETING DIGITAL", "Sede": "Santiago"}, {"CODIGO_UNICO": "I162S2C113J4V1", "Nombre": "INGENIERIA EN RECURSOS HUMANOS", "Sede": "Santiago"}, {"CODIGO_UNICO": "I162S2C113J4V2", "Nombre": "INGENIERIA EN RECURSOS HUMANOS", "Sede": "Santiago"}, {"CODIGO_UNICO": "I162S2C114J2V1", "Nombre": "TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA", "Sede": "Santiago"}, {"CODIGO_UNICO": "I162S2C115J2V1", "Nombre": "TECNICO EN FARMACIA", "Sede": "Santiago"}]

## Dudosos

- Total: 4
- Muestra: [{"CODIGO_UNICO": "I162S2C1J4V1", "NOMBRE_CARRERA": "INGENIERIA EN INFORMATICA", "OBSERVACION_AUDITORIA": "Coincidencias auxiliares=1; Cod.Carr. existente=['38817']; Codigo SIES existente=['I162S2C46J4V2']"}, {"CODIGO_UNICO": "I162S2C3J1V1", "NOMBRE_CARRERA": "INGENIERIA EN CONECTIVIDAD Y REDES", "OBSERVACION_AUDITORIA": "Coincidencias auxiliares=1; Cod.Carr. existente=['6679']; Codigo SIES existente=['I162S2C3J1V2']"}, {"CODIGO_UNICO": "I162S2C3J2V1", "NOMBRE_CARRERA": "INGENIERIA EN CONECTIVIDAD Y REDES", "OBSERVACION_AUDITORIA": "Coincidencias auxiliares=1; Cod.Carr. existente=['6680']; Codigo SIES existente=['I162S2C3J2V4']"}, {"CODIGO_UNICO": "I162S2C3J4V1", "NOMBRE_CARRERA": "INGENIERIA EN CONECTIVIDAD Y REDES", "OBSERVACION_AUDITORIA": "Coincidencias auxiliares=1; Cod.Carr. existente=['38816']; Codigo SIES existente=['I162S2C3J4V2']"}]

## No crear

- Total: 0

## Auditoría de códigos esperados

- Códigos esperados ausentes en oferta matriz: ninguno

## Advertencias

- El nombre solicitado PROGRAMAS_EXISTENTES_NORMALIZADOS se exportó como PROGRAMAS_EXIST_NORMALIZADOS por límite de 31 caracteres de Excel.
- TIPO_PLAN_CARRERA se mapeó con regla empírica mayoritaria 1→Programa Regular y 3→Programa Especial; existen outliers históricos en la referencia.
- MODALIDAD=2 y JORNADA=3 quedan en REVISAR por ausencia de solape exacto suficiente en la base existente.

## Próximos pasos

- Abrir el Excel final /Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_PROGRAMAS_FALTANTES_CREAR_INDICES_DESDE_PROMEDIOS_20260604_082355.xlsx.
- Usar la hoja PROGRAMAS_FALTANTES_PARA_CREAR para completar pantalla Crear Programa.
- Revisar primero la hoja DUDOSOS_REVISAR_MANUAL antes de crear cualquier programa ambiguo.
