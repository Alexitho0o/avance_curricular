# Reglas de Validacion Trazadas al Instructivo

Fuente documental: `estudiantes_extranjeros_2026/docs/Instructivo_Estudiantes_Extranjeros_SIES_2026.txt`.

## Extranjeros Regulares 2026 - ID 16765

- Cuando el TIPO_RESIDENCIA_ESTUDIANTE es 2 o 3, el PAIS_ORIGEN se debe completar.
- Cuando no se tiene la informacion del TIPO_RESIDENCIA_ESTUDIANTE, no se debe completar el PAIS_ORIGEN.
- Cuando el TIPO_RESIDENCIA_ESTUDIANTE es 1, no se debe completar el PAIS_ORIGEN.
- En el campo PAIS_ORIGEN no puede ingresar el codigo 38 que corresponde a CHILE.
- La VIGENCIA considera valores 0 y 1.
- El PAIS_ESTUDIOS_SECUNDARIOS debe ser entre 1 y 197.
- El CODIGO_UNICO acepta codigos oficiales SIES de oferta 2025 o codigos temporales solicitados en este proceso.
- El DV debe ser nulo cuando el TIPO_DOCUMENTO es igual a P.
- El TIPO_DOCUMENTO debe ser R de RUT o P de Pasaporte.
- El DV debe completarse con valores de 0 a 9 y K cuando TIPO_DOCUMENTO es R.
- La NACIONALIDAD debe ser entre 1 y 197 y no puede ser 38 Chile.
- NUM_DOCUMENTO no puede contener letras/simbolos cuando TIPO_DOCUMENTO es R y no puede comenzar con 0.
- FECHA_NACIMIENTO no puede ser anterior a 01/01/1900 ni posterior a 30/06/2010.
- NOMBRE_UNIVERSIDAD_ORIGEN y PAIS_UNIVERSIDAD_ORIGEN se completan en conjunto.
- No se permiten espacios iniciales/finales ni dobles espacios en nombres/apellidos.

Reglas de no inferencia aplicadas en esta fase:

- No asumir nacionalidad = pais de origen.
- No asumir pais de origen = pais de estudios secundarios.
- No asumir pais de emision de pasaporte = nacionalidad.
- No asumir que nacionalidad extranjera implica ausencia de RUN.
- No usar domicilio actual para determinar tipo de residencia.
- No usar modalidad online para inferir residencia o no residencia en Chile.
- No usar IPE como tipo de documento.

## Extranjeros de Intercambio 2026 - ID 16764

- ESP_TIPO_PROGRAMA_INTERCAMBIO se debe completar cuando TIPO_PROGRAMA_INTERCAMBIO es 4.
- NUM_DOCUMENTO no debe estar vacio.
- Cuando TIPO_RESIDENCIA_ESTUDIANTE es 2, PAIS_ORIGEN se debe completar.
- PAIS_ORIGEN no puede ser 38 Chile.
- COMUNA_PROGRAMA debe ser valida y en mayuscula.
- Cuando EXISTE_CONVENIO es 1, se debe completar NOMBRE_UNIVERSIDAD_ORIGEN.
- NOMBRE_UNIVERSIDAD_ORIGEN y PAIS_UNIVERSIDAD_ORIGEN se completan en conjunto.
- FECHA_INICIO_PROGRAMA no puede ser posterior a 2025.
- FECHA_TERMINO_PROGRAMA no puede ser menor que FECHA_INICIO_PROGRAMA.
- EXISTE_CONVENIO admite 1 SI, 2 NO y 0 Sin Informacion segun mensajes de error.
- TIPO_PROGRAMA_INTERCAMBIO admite 1 Programa de Intercambio, 2 Pasantias Medicas, 3 Cursos Especiales, 4 Otro.
- NACIONALIDAD debe estar entre 1 y 197 y no puede ser 38 Chile.
- DV nulo si TIPO_DOCUMENTO es P; DV 0..9/K si TIPO_DOCUMENTO es R.
- TIPO_DOCUMENTO debe ser R o P.
- JORNADA_INTERCAMBIO admite 1 Diurno, 2 Vespertino, 3 Otro.
- SEXO debe ser M Mujer, H Hombre o NB No Binario.
- No se permiten espacios iniciales/finales ni dobles espacios en nombres/apellidos.

## Estrategia jerarquica propuesta de cruce

1. Identificador documental exacto normalizado: tipo documento, cuerpo del RUN/pasaporte y DV cuando corresponda.
2. CODCLI mediante tabla maestra de equivalencias; CODCLI no reemplaza NUM_DOCUMENTO.
3. Identificador institucional estable cuando exista en una fuente maestra.
4. Combinacion controlada de nombres y fecha de nacimiento solo para diagnostico, nunca para completar automaticamente sin validacion.

## Normalizaciones minimas

- Eliminar puntos, comas y guiones donde corresponda.
- Convertir a mayusculas.
- Limpiar espacios iniciales/finales y dobles espacios.
- Separar cuerpo RUN y DV.
- Conservar pasaporte como alfanumerico.
- DV vacio cuando TIPO_DOCUMENTO=P.
- Controlar caracteres validos.
