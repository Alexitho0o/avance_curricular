# CNED — Auditoría end to end por columna del artefacto operativo limpio

## Dictamen
CNED_DOCUMENTO_CREADO_Y_AUDITADO_POR_COLUMNA_SIN_ERRORES

## Baseline Git
- rama: clean/pes-ready-final
- HEAD local: 4caf70b
- HEAD remoto: 4caf70b
- estado limpio o no: no
- commit del script canónico: 4caf70b fix: canonicalize clean CNED materializer script

## Archivos auditados
- script canónico: indices_2025/cned/scripts/06_materializar_artefacto_operativo_cned_limpio.py
- Excel oficial 110249: indices_2025/cned/resultados/CNED_ARTEFACTO_OPERATIVO_LIMPIO_20260603_110249.xlsx
- último Excel generado: indices_2025/cned/resultados/CNED_ARTEFACTO_OPERATIVO_LIMPIO_20260603_132333.xlsx
- CSV operativo: indices_2025/cned/data/BASE_CNED_LIMPIA_OPERATIVA.csv
- TSV manual: indices_2025/cned/data/DATOS_VALIDACION_CNED_TSV_NUEVO_MANUAL.tsv

## Resultado de ejecución
- compiló: sí
- ejecutó: sí
- creó Excel: sí
- creó Markdown: sí
- mantuvo CSV: sí

## Auditoría por hoja
### OFICIAL_110249
- RESUMEN_LIMPIEZA: rows=61 cols=4
- BASE_CNED_LIMPIA: rows=59 cols=26
- SIN_CODIGO_SIES: rows=7 cols=64
- DUPLICADOS_CNED: rows=1 cols=4
- hojas encontradas: ['RESUMEN_LIMPIEZA', 'BASE_CNED_LIMPIA', 'SIN_CODIGO_SIES', 'DUPLICADOS_CNED']

### LATEST_GENERADO
- RESUMEN_LIMPIEZA: rows=61 cols=4
- BASE_CNED_LIMPIA: rows=59 cols=26
- SIN_CODIGO_SIES: rows=7 cols=64
- DUPLICADOS_CNED: rows=1 cols=4
- hojas encontradas: ['RESUMEN_LIMPIEZA', 'BASE_CNED_LIMPIA', 'SIN_CODIGO_SIES', 'DUPLICADOS_CNED']

## Auditoría por columna de BASE_CNED_LIMPIA
### Año
- cantidad de vacíos: 0
- cantidad de valores únicos: 7
- obligatoria: sí
- resultado: OK
- ejemplos: ['2025', '2024', '2022', '2021', '2019']

### Cód. Institución
- cantidad de vacíos: 0
- cantidad de valores únicos: 1
- obligatoria: sí
- resultado: OK
- ejemplos: ['2024']

### Nombre Institución
- cantidad de vacíos: 0
- cantidad de valores únicos: 1
- obligatoria: sí
- resultado: OK
- ejemplos: ['IP SAN SEBASTIÁN']

### Nombre de la Sede
- cantidad de vacíos: 0
- cantidad de valores únicos: 1
- obligatoria: sí
- resultado: OK
- ejemplos: ['Santiago']

### Comuna donde se imparte la carrera o programa
- cantidad de vacíos: 0
- cantidad de valores únicos: 1
- obligatoria: sí
- resultado: OK
- ejemplos: ['Santiago']

### Cód. Carrera
- cantidad de vacíos: 0
- cantidad de valores únicos: 59
- obligatoria: sí
- resultado: OK
- ejemplos: ['32513', '6677', '6678', '6680', '38816']

### Carrera Genérica
- cantidad de vacíos: 0
- cantidad de valores únicos: 21
- obligatoria: sí
- resultado: OK
- ejemplos: ['Técnico en Automatización, Control automático y similares', 'Ingeniería en Computación e Informática y similares', 'Ingeniería en Conectividad y Redes', 'Técnico en Análisis de Sistemas Informáticos', 'Técnico Programador Computacional']

### Nombre Programa
- cantidad de vacíos: 0
- cantidad de valores únicos: 30
- obligatoria: sí
- resultado: OK
- ejemplos: ['TNS en Automatización y Control Industrial', 'Ingeniería en Informática', 'Ingeniería en Conectividad y Redes', 'Ingeniería en Ciberseguridad', 'TNS en Ciberseguridad']

### Horario
- cantidad de vacíos: 0
- cantidad de valores únicos: 3
- obligatoria: sí
- resultado: OK
- ejemplos: ['Vespertino', 'Diurno', 'Otro']

### Tipo Programa
- cantidad de vacíos: 0
- cantidad de valores únicos: 2
- obligatoria: sí
- resultado: OK
- ejemplos: ['Programa Regular', 'Programa Especial']

### Tipo Carrera
- cantidad de vacíos: 0
- cantidad de valores únicos: 2
- obligatoria: sí
- resultado: OK
- ejemplos: ['Técnico Nivel Superior', 'Profesional']

### IngresoDirecto
- cantidad de vacíos: 0
- cantidad de valores únicos: 2
- obligatoria: sí
- resultado: OK
- ejemplos: ['Ingreso Directo', 'No es Ingreso Directo']

### Año Inicio Actividades
- cantidad de vacíos: 0
- cantidad de valores únicos: 12
- obligatoria: sí
- resultado: OK
- ejemplos: ['2015', '1990', '2002', '2018', '2019']

### Duración (en semestres)
- cantidad de vacíos: 0
- cantidad de valores únicos: 4
- obligatoria: sí
- resultado: OK
- ejemplos: ['5', '8', '4', '6']

### Cód. Campus
- cantidad de vacíos: 17
- cantidad de valores únicos: 2
- obligatoria: no
- resultado: REVISAR
- ejemplos: ['2024001001', '']

### Cód. Sede
- cantidad de vacíos: 0
- cantidad de valores únicos: 1
- obligatoria: sí
- resultado: OK
- ejemplos: ['2024001']

### Título
- cantidad de vacíos: 0
- cantidad de valores únicos: 33
- obligatoria: sí
- resultado: OK
- ejemplos: ['Técnico Nivel Sup. en Automatización y Control Industrial', 'Ingeniero en Informática', 'Ingeniero en Conectividad y Redes', 'Ingeniero en Ciberseguridad', 'Técnico Nivel Sup. en Ciberseguridad']

### Código SIES
- cantidad de vacíos: 0
- cantidad de valores únicos: 57
- obligatoria: sí
- resultado: OK
- ejemplos: ['I162S2C11J2V1', 'I162S2C1J1V2', 'I162S2C1J2V4', 'I162S2C3J2V4', 'I162S2C3J4V2']

### Pregrado/Posgrado
- cantidad de vacíos: 0
- cantidad de valores únicos: 1
- obligatoria: sí
- resultado: OK
- ejemplos: ['Pregrado']

### COD_SED_DERIVADO
- cantidad de vacíos: 0
- cantidad de valores únicos: 1
- obligatoria: sí
- resultado: OK
- ejemplos: ['2']

### COD_CAR_DERIVADO
- cantidad de vacíos: 0
- cantidad de valores únicos: 23
- obligatoria: sí
- resultado: OK
- ejemplos: ['11', '1', '3', '46', '47']

### JOR_DERIVADA
- cantidad de vacíos: 0
- cantidad de valores únicos: 3
- obligatoria: sí
- resultado: OK
- ejemplos: ['2', '1', '4']

### VERSION_DERIVADA
- cantidad de vacíos: 0
- cantidad de valores únicos: 4
- obligatoria: sí
- resultado: OK
- ejemplos: ['1', '2', '4', '3']

### CLAVE_OPERATIVA
- cantidad de vacíos: 0
- cantidad de valores únicos: 59
- obligatoria: sí
- resultado: OK
- ejemplos: ['I162S2C11J2V1|32513|TNS EN AUTOMATIZACIÓN Y CONTROL INDUSTRIAL|VESPERTINO', 'I162S2C1J1V2|6677|INGENIERÍA EN INFORMÁTICA|DIURNO', 'I162S2C1J2V4|6678|INGENIERÍA EN INFORMÁTICA|VESPERTINO', 'I162S2C3J2V4|6680|INGENIERÍA EN CONECTIVIDAD Y REDES|VESPERTINO', 'I162S2C3J4V2|38816|INGENIERÍA EN CONECTIVIDAD Y REDES|OTRO']

### VALIDACION_CODIGO_UNICO
- cantidad de vacíos: 0
- cantidad de valores únicos: 1
- obligatoria: sí
- resultado: OK
- ejemplos: ['OK']

### VALIDACION_COD_CARRERA
- cantidad de vacíos: 0
- cantidad de valores únicos: 1
- obligatoria: sí
- resultado: OK
- ejemplos: ['REVISAR_COD_CARRERA']

## Validaciones de negocio
- Código SIES: formato OK en 59 registros
- CLAVE_OPERATIVA: 59 valores únicos
- VALIDACION_CODIGO_UNICO: {'OK': 59}
- VALIDACION_COD_CARRERA: {'REVISAR_COD_CARRERA': 59}
- Pregrado/Posgrado: {'Pregrado': 59}
- Horario vs JOR: errores=0; Horario={'Vespertino': 23, 'Otro': 22, 'Diurno': 14}; JOR_DERIVADA={'2': 23, '4': 22, '1': 14}
- derivados: {'COD_SED_DERIVADO': 0, 'COD_CAR_DERIVADO': 0, 'JOR_DERIVADA': 0, 'VERSION_DERIVADA': 0}
- SIN_CODIGO_SIES: filas=7; Código SIES vacíos=7; MOTIVO_REVISION={'SIN_CODIGO_SIES': 7}; Pregrado/Posgrado={'Pregrado': 6, 'Posgrado': 1}
- CSV vs Excel: OK
- Excel oficial vs Excel generado: OK
- TSV manual no usado: filas=0 columnas=62

## Riesgos residuales
- VALIDACION_COD_CARRERA es advertencia no bloqueante porque Cód. Carrera CNED y COD_CAR_DERIVADO son códigos de naturaleza distinta.
- El TSV manual sigue con 0 filas y no debe usarse como insumo automático.
- Los Markdown timestamped generados en runtime pueden quedar como residuos locales si no están ignorados.

## Cierre
- no se tocaron artefactos de pregrado/PES_READY.
- no se actualizó TSV.
- no se mezcló SIN_CODIGO_SIES con BASE_CNED_LIMPIA.
- la base operativa queda lista para uso controlado.
