# Manual gobernado 5809 Avance Curricular 2026

## CODIGO_IES_NUM
- Definicion: Codigo de la institucion; dato precargado no modificable.
- Regla oficial: Dato precargado no modificable; editarlo genera error por atributo no modificable.
- Fuente de dato: Precarga 5809
- Llave de cruce: Registro 5809
- Logica: Conservar valor de precarga; comparar hash/estructura si se genera derivado.
- Estado actual: NO_MODIFICABLE_PRECARGA
- Pendientes: 

## TIPO_DOCUMENTO
- Definicion: Tipo de documento del estudiante.
- Regla oficial: Valores permitidos: R: RUT y P: Pasaporte. Dato precargado no modificable.
- Fuente de dato: Precarga 5809; contraste identidad/CODCLI solo para auditoria.
- Llave de cruce: NUM_DOCUMENTO + DV
- Logica: Conservar valor de precarga; comparar hash/estructura si se genera derivado.
- Estado actual: NO_MODIFICABLE_PRECARGA
- Pendientes: 

## NUM_DOCUMENTO
- Definicion: Numero de documento informado en la precarga.
- Regla oficial: Dato precargado no modificable; para RUT no puede contener letras.
- Fuente de dato: Precarga 5809; DatosAlumnos para auditoria.
- Llave de cruce: NUM_DOCUMENTO + DV
- Logica: Conservar valor de precarga; comparar hash/estructura si se genera derivado.
- Estado actual: NO_MODIFICABLE_PRECARGA
- Pendientes: 

## DV
- Definicion: Digito verificador cuando TIPO_DOCUMENTO es R.
- Regla oficial: Si tipo R, completar DV; si tipo P, no completar. DV numerico o K.
- Fuente de dato: Precarga 5809; DatosAlumnos para auditoria.
- Llave de cruce: NUM_DOCUMENTO + DV
- Logica: Conservar valor de precarga; comparar hash/estructura si se genera derivado.
- Estado actual: NO_MODIFICABLE_PRECARGA
- Pendientes: 

## PRIMER_APELLIDO
- Definicion: Primer apellido del estudiante.
- Regla oficial: Dato precargado no modificable; valores permitidos con letras mayusculas y caracteres aceptados.
- Fuente de dato: Precarga 5809; DatosAlumnos solo auditoria.
- Llave de cruce: Documento, no nombre.
- Logica: Conservar valor de precarga; comparar hash/estructura si se genera derivado.
- Estado actual: NO_MODIFICABLE_PRECARGA
- Pendientes: 

## SEGUNDO_APELLIDO
- Definicion: Segundo apellido del estudiante.
- Regla oficial: Dato precargado no modificable; valores permitidos con letras mayusculas y caracteres aceptados.
- Fuente de dato: Precarga 5809; DatosAlumnos solo auditoria.
- Llave de cruce: Documento, no nombre.
- Logica: Conservar valor de precarga; comparar hash/estructura si se genera derivado.
- Estado actual: NO_MODIFICABLE_PRECARGA
- Pendientes: 

## NOMBRES
- Definicion: Nombres del estudiante.
- Regla oficial: Dato precargado no modificable; valores permitidos con letras mayusculas y caracteres aceptados.
- Fuente de dato: Precarga 5809; DatosAlumnos solo auditoria.
- Llave de cruce: Documento, no nombre.
- Logica: Conservar valor de precarga; comparar hash/estructura si se genera derivado.
- Estado actual: NO_MODIFICABLE_PRECARGA
- Pendientes: 

## SEXO
- Definicion: Sexo informado.
- Regla oficial: Valores permitidos: H, M, X. Dato precargado no modificable.
- Fuente de dato: Precarga 5809
- Llave de cruce: Registro 5809
- Logica: Conservar valor de precarga; comparar hash/estructura si se genera derivado.
- Estado actual: NO_MODIFICABLE_PRECARGA
- Pendientes: 

## FECHA_NACIMIENTO
- Definicion: Fecha de nacimiento del estudiante.
- Regla oficial: Dato precargado no modificable; error si inconsistente con edad minima.
- Fuente de dato: Precarga 5809
- Llave de cruce: Registro 5809
- Logica: Conservar valor de precarga; comparar hash/estructura si se genera derivado.
- Estado actual: NO_MODIFICABLE_PRECARGA
- Pendientes: 

## CODIGO_UNICO
- Definicion: Codigo unico de la carrera que esta estudiando.
- Regla oficial: Dato precargado no modificable; debe existir en Carreras 5810.
- Fuente de dato: Precarga 5809; Precarga Carreras 5810.
- Llave de cruce: CODIGO_UNICO
- Logica: Conservar valor de precarga; comparar hash/estructura si se genera derivado.
- Estado actual: NO_MODIFICABLE_PRECARGA
- Pendientes: 

## PLAN_ESTUDIOS
- Definicion: Correlativo del plan de estudios en que esta matriculado el estudiante.
- Regla oficial: Usar numeros de plan informados en Carreras para el CODIGO_UNICO; obligatorio.
- Fuente de dato: Carreras 5810, conciliacion planes, fuente planes institucional.
- Llave de cruce: CODIGO_UNICO + PLAN_ESTUDIOS
- Logica: Validar CODIGO_UNICO+PLAN contra 5810 y conciliacion planes; no materializar si Carreras sigue bloqueada.
- Estado actual: BLOQUEADO_POR_PLAN
- Pendientes: BLOQUEO_PLAN

## ANIO_INGRESO_CARRERA_ACTUAL
- Definicion: Ano de ingreso a la carrera actual.
- Regla oficial: Dato precargado no modificable; no puede ser mayor a 2025.
- Fuente de dato: Precarga 5809
- Llave de cruce: Registro 5809
- Logica: Conservar valor de precarga; comparar hash/estructura si se genera derivado.
- Estado actual: NO_MODIFICABLE_PRECARGA
- Pendientes: 

## SEM_INGRESO_CARRERA_ACTUAL
- Definicion: Semestre de ingreso a la carrera actual.
- Regla oficial: Dato precargado no modificable; valores 1 o 2.
- Fuente de dato: Precarga 5809
- Llave de cruce: Registro 5809
- Logica: Conservar valor de precarga; comparar hash/estructura si se genera derivado.
- Estado actual: NO_MODIFICABLE_PRECARGA
- Pendientes: 

## ANIO_INGRESO_CARRERA_ORIGEN
- Definicion: Ano de ingreso a la carrera de origen o primer ano.
- Regla oficial: Dato precargado no modificable; no puede ser mayor a 2025.
- Fuente de dato: Precarga 5809
- Llave de cruce: Registro 5809
- Logica: Conservar valor de precarga; comparar hash/estructura si se genera derivado.
- Estado actual: NO_MODIFICABLE_PRECARGA
- Pendientes: 

## SEM_INGRESO_CARRERA_ORIGEN
- Definicion: Semestre de ingreso a la carrera de origen o primer ano.
- Regla oficial: Dato precargado no modificable; valores 1 o 2.
- Fuente de dato: Precarga 5809
- Llave de cruce: Registro 5809
- Logica: Conservar valor de precarga; comparar hash/estructura si se genera derivado.
- Estado actual: NO_MODIFICABLE_PRECARGA
- Pendientes: 

## CURSO_1ER_SEM
- Definicion: Indica si curso actividades academicas exigidas en el plan durante el primer semestre de 2025.
- Regla oficial: Valores SI/NO; obligatorio; si SI, UNIDADES_CURSADAS debe ser mayor a 0.
- Fuente de dato: Fuente academica 2025 por estudiante/carrera/plan/periodo.
- Llave de cruce: Documento -> CODCLI -> carrera/plan -> periodo 2025-1.
- Logica: Derivar SI/NO desde actividad academica exigida en plan durante semestre 1 de 2025; no usar nivel como sustituto.
- Estado actual: BLOQUEADO_POR_FUENTE
- Pendientes: BLOQUEO_FUENTE_AVANCE

## CURSO_2DO_SEM
- Definicion: Indica si curso actividades academicas exigidas en el plan durante el segundo semestre de 2025.
- Regla oficial: Valores SI/NO; obligatorio; si SI, UNIDADES_CURSADAS debe ser mayor a 0.
- Fuente de dato: Fuente academica 2025 por estudiante/carrera/plan/periodo.
- Llave de cruce: Documento -> CODCLI -> carrera/plan -> periodo 2025-2.
- Logica: Derivar SI/NO desde actividad academica exigida en plan durante semestre 2 de 2025; no usar nivel como sustituto.
- Estado actual: BLOQUEADO_POR_FUENTE
- Pendientes: BLOQUEO_FUENTE_AVANCE

## UNIDADES_CURSADAS
- Definicion: Unidades de medida cursadas efectivamente durante 2025 y pertenecientes al plan informado.
- Regla oficial: Usar solo numeros; no incluir validacion de estudios ni reconocimiento de aprendizajes previos; obligatorio.
- Fuente de dato: Fuente academica 2025 con estados de actividad/asignatura.
- Llave de cruce: CODCLI + carrera/plan + anio 2025 + unidad academica.
- Logica: Sumar unidades cursadas efectivamente en 2025 del plan informado, excluyendo validaciones/reconocimientos.
- Estado actual: BLOQUEADO_POR_FUENTE
- Pendientes: BLOQUEO_FUENTE_AVANCE

## UNIDADES_APROBADAS
- Definicion: Unidades de medida aprobadas efectivamente durante 2025 y pertenecientes al plan informado.
- Regla oficial: Usar solo numeros; no incluir validacion de estudios ni reconocimiento de aprendizajes previos; obligatorio.
- Fuente de dato: Fuente academica 2025 con estados aprobatorios.
- Llave de cruce: CODCLI + carrera/plan + anio 2025 + unidad academica.
- Logica: Sumar unidades aprobadas efectivamente en 2025 del plan informado, excluyendo validaciones/reconocimientos.
- Estado actual: BLOQUEADO_POR_FUENTE
- Pendientes: BLOQUEO_FUENTE_AVANCE

## UNID_CURSADAS_TOTAL
- Definicion: Unidades cursadas desde ingreso a la carrera hasta fin de 2025.
- Regla oficial: Usar solo numeros; incluir validacion de estudios o reconocimiento de aprendizajes previos; obligatorio.
- Fuente de dato: Historico academico acumulado + fuente 2025 + plan/malla.
- Llave de cruce: CODCLI + carrera/plan + historia academica hasta 2025.
- Logica: Sumar historico cursado hasta fin 2025, incluyendo validaciones/reconocimientos segun instructivo.
- Estado actual: BLOQUEADO_POR_REGLA_NO_CONFIRMADA
- Pendientes: BLOQUEO_FUENTE_AVANCE_PLAN_MALLA

## UNID_APROBADAS_TOTAL
- Definicion: Unidades aprobadas desde ingreso a la carrera hasta fin de 2025.
- Regla oficial: Usar solo numeros; incluir validacion/reconocimiento; limite de referencia: total plan con tolerancia 25%.
- Fuente de dato: Historico academico acumulado + fuente 2025 + plan/malla.
- Llave de cruce: CODCLI + carrera/plan + historia academica hasta 2025.
- Logica: Sumar historico aprobado hasta fin 2025, incluyendo validaciones/reconocimientos y controlando total plan+tolerancia.
- Estado actual: BLOQUEADO_POR_REGLA_NO_CONFIRMADA
- Pendientes: BLOQUEO_FUENTE_AVANCE_PLAN_MALLA

## VIGENCIA
- Definicion: Variable para mantener o eliminar un registro cargado.
- Regla oficial: Valores permitidos 0 eliminar, 1 mantener; obligatorio; no mezclar con otros procesos.
- Fuente de dato: Instructivo oficial y precarga 5809.
- Llave de cruce: Registro 5809
- Logica: Mantener 1 si el registro se conserva; 0 solo para eliminar registro cargado por error con respaldo.
- Estado actual: LISTO_CON_ADVERTENCIA
- Pendientes: NO_MATERIALIZADO_POR_BLOQUEOS_INTEGRALES

