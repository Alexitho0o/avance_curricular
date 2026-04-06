from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "gobernanza_columnas_mu"
TODAY = date.today().isoformat()
MANUAL_REF = "Manual Matricula Unificada 2026 - Anexo 7 Cuadro N1 (pregrado)"

MU_COLUMNS = [
    "TIPO_DOC",
    "N_DOC",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRE",
    "SEXO",
    "FECH_NAC",
    "NAC",
    "PAIS_EST_SEC",
    "COD_SED",
    "COD_CAR",
    "MODALIDAD",
    "JOR",
    "VERSION",
    "FOR_ING_ACT",
    "ANIO_ING_ACT",
    "SEM_ING_ACT",
    "ANIO_ING_ORI",
    "SEM_ING_ORI",
    "ASI_INS_ANT",
    "ASI_APR_ANT",
    "PROM_PRI_SEM",
    "PROM_SEG_SEM",
    "ASI_INS_HIS",
    "ASI_APR_HIS",
    "NIV_ACA",
    "SIT_FON_SOL",
    "SUS_PRE",
    "FECHA_MATRICULA",
    "REINCORPORACION",
    "VIG",
]

MANUAL_SPEC = {
    "TIPO_DOC": {
        "ORDEN_CUADRO_1": "A",
        "NOMBRE_MANUAL": "Tipo de Documento",
        "DESCRIPCION_MANUAL": "Tipo de documento de identificacion del matriculado.",
        "CODIGOS_MANUAL": "P: Pasaporte; R: RUT",
        "ESPECIFICACIONES_MANUAL": "Usar letras mayusculas.",
    },
    "N_DOC": {
        "ORDEN_CUADRO_1": "B",
        "NOMBRE_MANUAL": "Numero de Documento",
        "DESCRIPCION_MANUAL": "Numero de documento de identificacion del matriculado.",
        "CODIGOS_MANUAL": "No aplica",
        "ESPECIFICACIONES_MANUAL": "Usar letras mayusculas y numeros.",
    },
    "DV": {
        "ORDEN_CUADRO_1": "C",
        "NOMBRE_MANUAL": "Digito Verificador",
        "DESCRIPCION_MANUAL": "Digito verificador del RUT.",
        "CODIGOS_MANUAL": "No aplica",
        "ESPECIFICACIONES_MANUAL": "Usar 0..9 o K mayuscula.",
    },
    "PRIMER_APELLIDO": {
        "ORDEN_CUADRO_1": "D",
        "NOMBRE_MANUAL": "Primer Apellido",
        "DESCRIPCION_MANUAL": "Primer apellido.",
        "CODIGOS_MANUAL": "No aplica",
        "ESPECIFICACIONES_MANUAL": "Letras mayusculas A..Z, sin acentos. Permite dieresis y guion.",
    },
    "SEGUNDO_APELLIDO": {
        "ORDEN_CUADRO_1": "E",
        "NOMBRE_MANUAL": "Segundo Apellido",
        "DESCRIPCION_MANUAL": "Segundo apellido.",
        "CODIGOS_MANUAL": "No aplica",
        "ESPECIFICACIONES_MANUAL": "Letras mayusculas A..Z, sin acentos. Permite dieresis y guion.",
    },
    "NOMBRE": {
        "ORDEN_CUADRO_1": "F",
        "NOMBRE_MANUAL": "Nombres",
        "DESCRIPCION_MANUAL": "Nombres del matriculado.",
        "CODIGOS_MANUAL": "No aplica",
        "ESPECIFICACIONES_MANUAL": "Letras mayusculas A..Z, sin acentos. Permite dieresis y guion.",
    },
    "SEXO": {
        "ORDEN_CUADRO_1": "G",
        "NOMBRE_MANUAL": "Sexo",
        "DESCRIPCION_MANUAL": "Condicion de mujer, hombre o no binario.",
        "CODIGOS_MANUAL": "H: Hombre; M: Mujer; NB: No binario",
        "ESPECIFICACIONES_MANUAL": "Usar letras mayusculas.",
    },
    "FECH_NAC": {
        "ORDEN_CUADRO_1": "H",
        "NOMBRE_MANUAL": "Fecha de Nacimiento",
        "DESCRIPCION_MANUAL": "Fecha de nacimiento.",
        "CODIGOS_MANUAL": "No aplica",
        "ESPECIFICACIONES_MANUAL": "Usar formato dd/mm/aaaa.",
    },
    "NAC": {
        "ORDEN_CUADRO_1": "I",
        "NOMBRE_MANUAL": "Nacionalidad",
        "DESCRIPCION_MANUAL": "Pais de nacionalidad.",
        "CODIGOS_MANUAL": "1..197",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "PAIS_EST_SEC": {
        "ORDEN_CUADRO_1": "J",
        "NOMBRE_MANUAL": "Pais Estudios Secundarios",
        "DESCRIPCION_MANUAL": "Pais donde completo estudios secundarios.",
        "CODIGOS_MANUAL": "1..197",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "COD_SED": {
        "ORDEN_CUADRO_1": "K",
        "NOMBRE_MANUAL": "Codigo de Sede",
        "DESCRIPCION_MANUAL": "Codigo de sede de la IES en la que se encuentra matriculado.",
        "CODIGOS_MANUAL": "Codigos de la institucion",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "COD_CAR": {
        "ORDEN_CUADRO_1": "L",
        "NOMBRE_MANUAL": "Codigo de Carrera",
        "DESCRIPCION_MANUAL": "Codigo de carrera de la IES en la que se encuentra matriculado.",
        "CODIGOS_MANUAL": "Codigos de la institucion",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "MODALIDAD": {
        "ORDEN_CUADRO_1": "M",
        "NOMBRE_MANUAL": "Modalidad",
        "DESCRIPCION_MANUAL": "Modalidad de la carrera o programa.",
        "CODIGOS_MANUAL": "Codigos de la institucion",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "JOR": {
        "ORDEN_CUADRO_1": "N",
        "NOMBRE_MANUAL": "Jornada",
        "DESCRIPCION_MANUAL": "Jornada de la carrera o programa.",
        "CODIGOS_MANUAL": "Codigos de la institucion",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "VERSION": {
        "ORDEN_CUADRO_1": "O",
        "NOMBRE_MANUAL": "Version",
        "DESCRIPCION_MANUAL": "Version de la carrera o programa.",
        "CODIGOS_MANUAL": "Codigos de la institucion",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "FOR_ING_ACT": {
        "ORDEN_CUADRO_1": "P",
        "NOMBRE_MANUAL": "Forma Ingreso Carrera Actual",
        "DESCRIPCION_MANUAL": "Via de admision de la carrera o programa.",
        "CODIGOS_MANUAL": "1..11 segun catalogo manual",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "ANIO_ING_ACT": {
        "ORDEN_CUADRO_1": "Q",
        "NOMBRE_MANUAL": "Anio de Ingreso Carrera Actual",
        "DESCRIPCION_MANUAL": "Anio de ingreso a la carrera actual.",
        "CODIGOS_MANUAL": "1990..2026",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "SEM_ING_ACT": {
        "ORDEN_CUADRO_1": "R",
        "NOMBRE_MANUAL": "Semestre de Ingreso Carrera Actual",
        "DESCRIPCION_MANUAL": "Semestre de ingreso a la carrera actual.",
        "CODIGOS_MANUAL": "1..2",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "ANIO_ING_ORI": {
        "ORDEN_CUADRO_1": "S",
        "NOMBRE_MANUAL": "Anio de Ingreso Carrera de Origen",
        "DESCRIPCION_MANUAL": "Anio de ingreso a la carrera de origen.",
        "CODIGOS_MANUAL": "1980..2026 y 1900",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "SEM_ING_ORI": {
        "ORDEN_CUADRO_1": "T",
        "NOMBRE_MANUAL": "Semestre de Ingreso Carrera de Origen",
        "DESCRIPCION_MANUAL": "Semestre de ingreso a la carrera de origen.",
        "CODIGOS_MANUAL": "0,1,2",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "ASI_INS_ANT": {
        "ORDEN_CUADRO_1": "U",
        "NOMBRE_MANUAL": "Asignaturas Inscritas Anio Anterior",
        "DESCRIPCION_MANUAL": "Asignaturas inscritas en el ultimo periodo.",
        "CODIGOS_MANUAL": "0..99",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "ASI_APR_ANT": {
        "ORDEN_CUADRO_1": "V",
        "NOMBRE_MANUAL": "Asignaturas Aprobadas Anio Anterior",
        "DESCRIPCION_MANUAL": "Asignaturas aprobadas en el ultimo periodo.",
        "CODIGOS_MANUAL": "0..99",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "PROM_PRI_SEM": {
        "ORDEN_CUADRO_1": "W",
        "NOMBRE_MANUAL": "Nota Promedio Primer Semestre Anio Anterior",
        "DESCRIPCION_MANUAL": "Promedio de notas primer semestre del anio anterior.",
        "CODIGOS_MANUAL": "0 o 100..700",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "PROM_SEG_SEM": {
        "ORDEN_CUADRO_1": "X",
        "NOMBRE_MANUAL": "Nota Promedio Segundo Semestre Anio Anterior",
        "DESCRIPCION_MANUAL": "Promedio de notas segundo semestre del anio anterior.",
        "CODIGOS_MANUAL": "0 o 100..700",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "ASI_INS_HIS": {
        "ORDEN_CUADRO_1": "Y",
        "NOMBRE_MANUAL": "Asignaturas Inscritas Historicas",
        "DESCRIPCION_MANUAL": "Asignaturas inscritas desde inicio de la carrera.",
        "CODIGOS_MANUAL": "0..200",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "ASI_APR_HIS": {
        "ORDEN_CUADRO_1": "Z",
        "NOMBRE_MANUAL": "Asignaturas Aprobadas Historicas",
        "DESCRIPCION_MANUAL": "Asignaturas aprobadas desde inicio de la carrera.",
        "CODIGOS_MANUAL": "0..200",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "NIV_ACA": {
        "ORDEN_CUADRO_1": "AA",
        "NOMBRE_MANUAL": "Nivel Academico",
        "DESCRIPCION_MANUAL": "Semestre curricular que cursa el matriculado.",
        "CODIGOS_MANUAL": "1..duracion carrera",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "SIT_FON_SOL": {
        "ORDEN_CUADRO_1": "AB",
        "NOMBRE_MANUAL": "Situacion Fondo Solidario",
        "DESCRIPCION_MANUAL": "Si mantiene situacion socioeconomica FSCU.",
        "CODIGOS_MANUAL": "0: No cumple/no aplica; 1: Si cumple; 2: No presenta documentacion",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "SUS_PRE": {
        "ORDEN_CUADRO_1": "AC",
        "NOMBRE_MANUAL": "Suspensiones Previas",
        "DESCRIPCION_MANUAL": "Numero de semestres suspendidos previos al anio actual.",
        "CODIGOS_MANUAL": "0..99",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "FECHA_MATRICULA": {
        "ORDEN_CUADRO_1": "AD",
        "NOMBRE_MANUAL": "Fecha de Matricula",
        "DESCRIPCION_MANUAL": "Fecha de inscripcion en matricula. Solo aplica si anio origen=2026.",
        "CODIGOS_MANUAL": "No aplica (desconocido: 01/01/1900)",
        "ESPECIFICACIONES_MANUAL": "Usar formato dd/mm/aaaa.",
    },
    "REINCORPORACION": {
        "ORDEN_CUADRO_1": "AE",
        "NOMBRE_MANUAL": "Reincorporacion",
        "DESCRIPCION_MANUAL": "Si estudiante se reincorpora en segundo semestre.",
        "CODIGOS_MANUAL": "0: No/no aplica; 1: Si",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
    "VIG": {
        "ORDEN_CUADRO_1": "AF",
        "NOMBRE_MANUAL": "Vigencia",
        "DESCRIPCION_MANUAL": "Estado de vigencia de la matricula.",
        "CODIGOS_MANUAL": "0: sin matricula; 1: matricula vigente; 2: egresado con matricula vigente",
        "ESPECIFICACIONES_MANUAL": "Usar solo numeros.",
    },
}

PROJECT_SPEC = {
    "TIPO_DOC": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Constante pipeline",
        "FUENTE_AUTOMATICA_SECUNDARIA": "No aplica",
        "ARCHIVOS_GOBERNANZA": "gobernanza_columnas_mu/gob_mu_tipo_doc.tsv",
        "REGLA_IMPLEMENTADA_PROYECTO": "Se informa R en la version actual.",
        "VALIDACION_APLICADA": "Catalogo permitido R/P en QA.",
        "FALLBACK_OPERATIVO": "R",
        "REVISION_MANUAL_CUANDO": "Si se requiere pasaporte (P) por caso real.",
    },
    "N_DOC": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: RUT o NUM_DOCUMENTO o N_DOC",
        "FUENTE_AUTOMATICA_SECUNDARIA": "No aplica",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Copia directa desde columna detectada.",
        "VALIDACION_APLICADA": "No vacio y consistencia con DV.",
        "FALLBACK_OPERATIVO": "Sin fallback, caso excluido si falta.",
        "REVISION_MANUAL_CUANDO": "Documento vacio o mal formado.",
    },
    "DV": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: DIG o DV",
        "FUENTE_AUTOMATICA_SECUNDARIA": "No aplica",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Copia directa desde columna detectada.",
        "VALIDACION_APLICADA": "Formato 0..9 o K en QA.",
        "FALLBACK_OPERATIVO": "Sin fallback, caso excluido si falta.",
        "REVISION_MANUAL_CUANDO": "DV invalido o no consistente con documento.",
    },
    "PRIMER_APELLIDO": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: PATERNO o PRIMER_APELLIDO",
        "FUENTE_AUTOMATICA_SECUNDARIA": "DatosAlumnos: DA_APELLIDO_PATERNO",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Combine_first + normalizacion texto.",
        "VALIDACION_APLICADA": "No vacio en carga final.",
        "FALLBACK_OPERATIVO": "Se prioriza DatosAlumnos si fuente viene vacia.",
        "REVISION_MANUAL_CUANDO": "Caracteres invalidos o nulo.",
    },
    "SEGUNDO_APELLIDO": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: MATERNO o SEGUNDO_APELLIDO",
        "FUENTE_AUTOMATICA_SECUNDARIA": "DatosAlumnos: DA_APELLIDO_MATERNO",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Combine_first + normalizacion texto.",
        "VALIDACION_APLICADA": "Permite vacio segun manual cuando corresponda.",
        "FALLBACK_OPERATIVO": "Puede quedar vacio si no existe dato.",
        "REVISION_MANUAL_CUANDO": "Caracteres invalidos o inconsistencia identitaria.",
    },
    "NOMBRE": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: NOMBRE",
        "FUENTE_AUTOMATICA_SECUNDARIA": "DatosAlumnos: DA_NOMBRES",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Combine_first + normalizacion texto.",
        "VALIDACION_APLICADA": "No vacio en carga final.",
        "FALLBACK_OPERATIVO": "Se prioriza DatosAlumnos si fuente viene vacia.",
        "REVISION_MANUAL_CUANDO": "Caracteres invalidos o nulo.",
    },
    "SEXO": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: SEXO",
        "FUENTE_AUTOMATICA_SECUNDARIA": "DatosAlumnos: DA_SEXO",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Normalize a H/M/NB.",
        "VALIDACION_APLICADA": "Catalogo H,M,NB en QA.",
        "FALLBACK_OPERATIVO": "Sin fallback catalogado.",
        "REVISION_MANUAL_CUANDO": "Valor fuera de catalogo.",
    },
    "FECH_NAC": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: FECHANACIMIENTO o FECHA_NACIMIENTO",
        "FUENTE_AUTOMATICA_SECUNDARIA": "DatosAlumnos: DA_FECHANACIMIENTO",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Formato dd/mm/aaaa y clamp de fecha.",
        "VALIDACION_APLICADA": "No futura; formato fecha.",
        "FALLBACK_OPERATIVO": "01/01/1900 cuando no hay dato.",
        "REVISION_MANUAL_CUANDO": "Fecha invalida o inconsistente.",
    },
    "NAC": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: NACIONALIDAD o NAC",
        "FUENTE_AUTOMATICA_SECUNDARIA": "DatosAlumnos: DA_NACIONALIDAD",
        "ARCHIVOS_GOBERNANZA": "gobernanza_nac.tsv",
        "REGLA_IMPLEMENTADA_PROYECTO": "Mapea texto a codigo NAC (1..197).",
        "VALIDACION_APLICADA": "Rango 1..197.",
        "FALLBACK_OPERATIVO": "38 (Chile) si no mapea.",
        "REVISION_MANUAL_CUANDO": "Nacionalidad en REVISION_MANUAL o sin mapping.",
    },
    "PAIS_EST_SEC": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: PAIS_EST_SEC",
        "FUENTE_AUTOMATICA_SECUNDARIA": "DatosAlumnos: DA_COMUNACOLEGIO/DA_CIUDADCOLEGIO",
        "ARCHIVOS_GOBERNANZA": "gobernanza_pais_est_sec.tsv",
        "REGLA_IMPLEMENTADA_PROYECTO": "Mapeo por localidad (both > comuna > ciudad).",
        "VALIDACION_APLICADA": "Rango 1..197.",
        "FALLBACK_OPERATIVO": "38 (Chile) si no mapea.",
        "REVISION_MANUAL_CUANDO": "Localidad no mapeada o conflicto de tabla.",
    },
    "COD_SED": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: COD_SED",
        "FUENTE_AUTOMATICA_SECUNDARIA": "DatosAlumnos: DA_SEDE + parse de CODIGO_UNICO",
        "ARCHIVOS_GOBERNANZA": "gobernanza_sede.tsv",
        "REGLA_IMPLEMENTADA_PROYECTO": "Mapea RE->2, CO->3; parse SIES prevalece.",
        "VALIDACION_APLICADA": "Debe existir para carga.",
        "FALLBACK_OPERATIVO": "Sin fallback fuera de tabla.",
        "REVISION_MANUAL_CUANDO": "SEDE distinta de RE/CO o no mapeada.",
    },
    "COD_CAR": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: CODCARR/CODCARPR",
        "FUENTE_AUTOMATICA_SECUNDARIA": "Parse de CODIGO_CARRERA_SIES_FINAL",
        "ARCHIVOS_GOBERNANZA": "catalogo_manual.tsv, puente_sies.tsv, matriz_desambiguacion_sies_final.tsv",
        "REGLA_IMPLEMENTADA_PROYECTO": "Se normaliza al codigo parseado desde SIES final.",
        "VALIDACION_APLICADA": "Debe existir para carga.",
        "FALLBACK_OPERATIVO": "Sin match SIES => excluido carga.",
        "REVISION_MANUAL_CUANDO": "Ambiguedad o sin match SIES.",
    },
    "MODALIDAD": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Derivada desde JORNADA fuente",
        "FUENTE_AUTOMATICA_SECUNDARIA": "Oferta academica por CODIGO_UNICO",
        "ARCHIVOS_GOBERNANZA": "Oferta academica (dimensional)",
        "REGLA_IMPLEMENTADA_PROYECTO": "Oferta prevalece, luego parse SIES, luego inferencia por JOR.",
        "VALIDACION_APLICADA": "Debe existir para carga.",
        "FALLBACK_OPERATIVO": "Inferencia desde JOR.",
        "REVISION_MANUAL_CUANDO": "No resuelta para codigo carrera.",
    },
    "JOR": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: JORNADA",
        "FUENTE_AUTOMATICA_SECUNDARIA": "Oferta academica y parse SIES",
        "ARCHIVOS_GOBERNANZA": "Oferta academica (dimensional)",
        "REGLA_IMPLEMENTADA_PROYECTO": "Mapeo jornada fuente + override por oferta/SIES.",
        "VALIDACION_APLICADA": "Debe existir para carga.",
        "FALLBACK_OPERATIVO": "Mapeo directo de jornada fuente.",
        "REVISION_MANUAL_CUANDO": "No coincide con oferta para CODIGO_UNICO.",
    },
    "VERSION": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Parse de CODIGO_CARRERA_SIES_FINAL",
        "FUENTE_AUTOMATICA_SECUNDARIA": "No aplica",
        "ARCHIVOS_GOBERNANZA": "puente_sies.tsv",
        "REGLA_IMPLEMENTADA_PROYECTO": "Se obtiene desde sufijo Vn del codigo SIES.",
        "VALIDACION_APLICADA": "Debe existir para carga.",
        "FALLBACK_OPERATIVO": "Sin match SIES => excluido carga.",
        "REVISION_MANUAL_CUANDO": "Codigo SIES faltante o invalido.",
    },
    "FOR_ING_ACT": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: FOR_ING_ACT o FORMA_INGRESO*",
        "FUENTE_AUTOMATICA_SECUNDARIA": "No aplica",
        "ARCHIVOS_GOBERNANZA": "gobernanza_for_ing_act.tsv",
        "REGLA_IMPLEMENTADA_PROYECTO": "Numeric 1..11; fuera de rango se reemplaza por 10.",
        "VALIDACION_APLICADA": "Catalogo 1..11.",
        "FALLBACK_OPERATIVO": "10 (Otras formas de ingreso).",
        "REVISION_MANUAL_CUANDO": "Se requiere clasificacion distinta de 10.",
    },
    "ANIO_ING_ACT": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: ANOINGRESO/ANIO_INGRESO_CARRERA_ACTUAL",
        "FUENTE_AUTOMATICA_SECUNDARIA": "DatosAlumnos: DA_ANOINGRESO; inferencia CODCLI",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Clamp a 1990..2026.",
        "VALIDACION_APLICADA": "Rango 1990..2026.",
        "FALLBACK_OPERATIVO": "2026 si falta o invalido.",
        "REVISION_MANUAL_CUANDO": "Inconsistencia cronologica con origen o fecha nac.",
    },
    "SEM_ING_ACT": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: PERIODOINGRESO/SEM_INGRESO_CARRERA_ACTUAL",
        "FUENTE_AUTOMATICA_SECUNDARIA": "DatosAlumnos: DA_PERIODOINGRESO",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Normaliza 3->2; permite 1..2.",
        "VALIDACION_APLICADA": "Catalogo 1/2.",
        "FALLBACK_OPERATIVO": "1 si falta.",
        "REVISION_MANUAL_CUANDO": "Valor distinto de 1/2 en origen.",
    },
    "ANIO_ING_ORI": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Copia de ANIO_ING_ACT",
        "FUENTE_AUTOMATICA_SECUNDARIA": "Regla FOR_ING_ACT y rango manual",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Ajuste a 1980..2026 o 1900.",
        "VALIDACION_APLICADA": "Rango manual y coherencia con FOR_ING_ACT.",
        "FALLBACK_OPERATIVO": "ANIO_ING_ACT.",
        "REVISION_MANUAL_CUANDO": "Casos continuidad/cambio con cronologia dudosa.",
    },
    "SEM_ING_ORI": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Copia de SEM_ING_ACT",
        "FUENTE_AUTOMATICA_SECUNDARIA": "Regla FOR_ING_ACT y anio origen",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Normaliza 3->2; 0 obligatorio si ANIO_ING_ORI=1900.",
        "VALIDACION_APLICADA": "Catalogo 0/1/2 + regla 1900.",
        "FALLBACK_OPERATIVO": "SEM_ING_ACT.",
        "REVISION_MANUAL_CUANDO": "Origen 1900 con semestre distinto de 0.",
    },
    "ASI_INS_ANT": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: ASI_INS_ANT",
        "FUENTE_AUTOMATICA_SECUNDARIA": "No aplica",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Copia numerica.",
        "VALIDACION_APLICADA": "Rango 0..99.",
        "FALLBACK_OPERATIVO": "0 si falta.",
        "REVISION_MANUAL_CUANDO": "Fuera de rango.",
    },
    "ASI_APR_ANT": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: ASI_APR_ANT",
        "FUENTE_AUTOMATICA_SECUNDARIA": "No aplica",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Copia numerica.",
        "VALIDACION_APLICADA": "Rango 0..99 y APR<=INS.",
        "FALLBACK_OPERATIVO": "0 si falta.",
        "REVISION_MANUAL_CUANDO": "APR>INS o fuera de rango.",
    },
    "PROM_PRI_SEM": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: PROM_PRI_SEM",
        "FUENTE_AUTOMATICA_SECUNDARIA": "Historico Hoja1: NOTA_FINAL por semestre",
        "ARCHIVOS_GOBERNANZA": "gobernanza_escala_notas.tsv",
        "REGLA_IMPLEMENTADA_PROYECTO": "Conversion escala 1.0-7.0 x100 = 100-700; 0 o fuera de rango = sin nota (0 en salida).",
        "VALIDACION_APLICADA": "0 o 100..700.",
        "FALLBACK_OPERATIVO": "0 si falta.",
        "REVISION_MANUAL_CUANDO": "Fuera de rango.",
    },
    "PROM_SEG_SEM": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: PROM_SEG_SEM",
        "FUENTE_AUTOMATICA_SECUNDARIA": "Historico Hoja1: NOTA_FINAL por semestre",
        "ARCHIVOS_GOBERNANZA": "gobernanza_escala_notas.tsv",
        "REGLA_IMPLEMENTADA_PROYECTO": "Conversion escala 1.0-7.0 x100 = 100-700; 0 o fuera de rango = sin nota (0 en salida).",
        "VALIDACION_APLICADA": "0 o 100..700.",
        "FALLBACK_OPERATIVO": "0 si falta.",
        "REVISION_MANUAL_CUANDO": "Fuera de rango.",
    },
    "ASI_INS_HIS": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: ASI_INS_HIS",
        "FUENTE_AUTOMATICA_SECUNDARIA": "No aplica",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Copia numerica.",
        "VALIDACION_APLICADA": "Rango 0..200.",
        "FALLBACK_OPERATIVO": "0 si falta.",
        "REVISION_MANUAL_CUANDO": "Fuera de rango.",
    },
    "ASI_APR_HIS": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: ASI_APR_HIS",
        "FUENTE_AUTOMATICA_SECUNDARIA": "No aplica",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Copia numerica.",
        "VALIDACION_APLICADA": "Rango 0..200 y APR<=INS.",
        "FALLBACK_OPERATIVO": "0 si falta.",
        "REVISION_MANUAL_CUANDO": "APR>INS o fuera de rango.",
    },
    "NIV_ACA": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: NIV_ACA o NIVEL",
        "FUENTE_AUTOMATICA_SECUNDARIA": "DatosAlumnos: DA_NIVEL; oferta DURACION_ESTUDIOS_REF",
        "ARCHIVOS_GOBERNANZA": "gobernanza_niveles.tsv",
        "REGLA_IMPLEMENTADA_PROYECTO": "NIV_ACA>=1, acotado por duracion oferta y regla cohorte 2026.",
        "VALIDACION_APLICADA": ">=1 y <=duracion carrera.",
        "FALLBACK_OPERATIVO": "1 si falta.",
        "REVISION_MANUAL_CUANDO": "Excede duracion o inconsistente con cohorte.",
    },
    "SIT_FON_SOL": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: SIT_FON_SOL",
        "FUENTE_AUTOMATICA_SECUNDARIA": "No aplica",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Catalogo 0/1/2.",
        "VALIDACION_APLICADA": "0,1,2.",
        "FALLBACK_OPERATIVO": "0 si falta.",
        "REVISION_MANUAL_CUANDO": "Valor fuera de catalogo.",
    },
    "SUS_PRE": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: SUS_PRE",
        "FUENTE_AUTOMATICA_SECUNDARIA": "No aplica",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Rango 0..99, y forzado a 0 si anio actual 2026.",
        "VALIDACION_APLICADA": "0..99.",
        "FALLBACK_OPERATIVO": "0 si falta.",
        "REVISION_MANUAL_CUANDO": "Fuera de rango o inconsistente temporalmente.",
    },
    "FECHA_MATRICULA": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: FECHAMATRICULA/FECHA_MATRICULA",
        "FUENTE_AUTOMATICA_SECUNDARIA": "DatosAlumnos: DA_FECHAMATRICULA",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Formato dd/mm/aaaa; solo aplica si ANIO_ING_ORI=2026.",
        "VALIDACION_APLICADA": "No futura y formato fecha.",
        "FALLBACK_OPERATIVO": "01/01/1900.",
        "REVISION_MANUAL_CUANDO": "Fecha posterior a carga o fuera de rango.",
    },
    "REINCORPORACION": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: REINCORPORACION",
        "FUENTE_AUTOMATICA_SECUNDARIA": "Derivacion desde DA_SITUACION (38 - ... => 1)",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Catalogo binario 0/1.",
        "VALIDACION_APLICADA": "0/1 obligatorio.",
        "FALLBACK_OPERATIVO": "0 si falta.",
        "REVISION_MANUAL_CUANDO": "No binario o aplica en periodo no permitido.",
    },
    "VIG": {
        "FUENTE_AUTOMATICA_PRIMARIA": "Entrada: VIGENCIA o VIG",
        "FUENTE_AUTOMATICA_SECUNDARIA": "No aplica",
        "ARCHIVOS_GOBERNANZA": "No aplica",
        "REGLA_IMPLEMENTADA_PROYECTO": "Catalogo 0/1/2.",
        "VALIDACION_APLICADA": "0,1,2.",
        "FALLBACK_OPERATIVO": "1 si falta.",
        "REVISION_MANUAL_CUANDO": "Valor fuera de catalogo.",
    },
}

TSV_HEADERS = [
    "CAMPO_SALIDA",
    "ORDEN_CUADRO_1",
    "NOMBRE_MANUAL",
    "DESCRIPCION_MANUAL",
    "CODIGOS_MANUAL",
    "ESPECIFICACIONES_MANUAL",
    "FUENTE_AUTOMATICA_PRIMARIA",
    "FUENTE_AUTOMATICA_SECUNDARIA",
    "ARCHIVOS_GOBERNANZA",
    "REGLA_IMPLEMENTADA_PROYECTO",
    "VALIDACION_APLICADA",
    "FALLBACK_OPERATIVO",
    "REVISION_MANUAL_CUANDO",
    "MANUAL_REFERENCIA",
    "ULTIMA_ACTUALIZACION",
    "ESTADO_IMPLEMENTACION",
]


def _write_tsv(path: Path, rows: list[dict[str, str]], headers: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers, delimiter="\t")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def _build_for_ing_catalog() -> list[dict[str, str]]:
    catalog = [
        ("1", "Ingreso Directo (regular)"),
        ("2", "Continuidad de Plan Comun o Bachillerato"),
        ("3", "Cambio Interno"),
        ("4", "Cambio Externo"),
        ("5", "Ingreso por Reconocimiento de Aprendizajes Previos"),
        ("6", "Ingreso especial para estudiantes extranjeros"),
        ("7", "Ingreso a traves del Programa PACE"),
        ("8", "Ingreso a traves de Programas de Inclusion"),
        ("9", "Acceso por caracteristicas especiales"),
        ("10", "Otras formas de ingreso"),
        ("11", "Articulacion de TNS a carrera profesional"),
    ]
    return [
        {
            "FOR_ING_ACT": code,
            "DESCRIPCION_MANUAL": desc,
            "FUENTE_MANUAL": "Anexo 7 Cuadro N1 y Cuadro N3",
            "ESTADO_GOBERNANZA": "VALIDADO_MANUAL_2026",
            "ULTIMA_ACTUALIZACION": TODAY,
        }
        for code, desc in catalog
    ]


def main() -> None:
    missing_manual = sorted(set(MU_COLUMNS) - set(MANUAL_SPEC))
    missing_project = sorted(set(MU_COLUMNS) - set(PROJECT_SPEC))
    if missing_manual or missing_project:
        raise ValueError(
            f"Cobertura incompleta. missing_manual={missing_manual}, missing_project={missing_project}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    idx_rows: list[dict[str, str]] = []
    for col in MU_COLUMNS:
        data = {
            "CAMPO_SALIDA": col,
            **MANUAL_SPEC[col],
            **PROJECT_SPEC[col],
            "MANUAL_REFERENCIA": MANUAL_REF,
            "ULTIMA_ACTUALIZACION": TODAY,
            "ESTADO_IMPLEMENTACION": "OK_DOCUMENTADO",
        }
        out_file = OUTPUT_DIR / f"gob_mu_{col.lower()}.tsv"
        _write_tsv(out_file, [data], TSV_HEADERS)
        idx_rows.append(
            {
                "CAMPO_SALIDA": col,
                "ORDEN_CUADRO_1": MANUAL_SPEC[col]["ORDEN_CUADRO_1"],
                "ARCHIVO_TSV": str(out_file.relative_to(BASE_DIR)),
                "MANUAL_REFERENCIA": MANUAL_REF,
                "ESTADO": "OK",
                "ULTIMA_ACTUALIZACION": TODAY,
            }
        )

    _write_tsv(
        OUTPUT_DIR / "_INDICE_COLUMNAS.tsv",
        idx_rows,
        [
            "CAMPO_SALIDA",
            "ORDEN_CUADRO_1",
            "ARCHIVO_TSV",
            "MANUAL_REFERENCIA",
            "ESTADO",
            "ULTIMA_ACTUALIZACION",
        ],
    )

    # Catalogo explicito de FOR_ING_ACT solicitado por gobernanza.
    _write_tsv(
        BASE_DIR / "gobernanza_for_ing_act.tsv",
        _build_for_ing_catalog(),
        [
            "FOR_ING_ACT",
            "DESCRIPCION_MANUAL",
            "FUENTE_MANUAL",
            "ESTADO_GOBERNANZA",
            "ULTIMA_ACTUALIZACION",
        ],
    )

    summary = {
        "output_dir": str(OUTPUT_DIR),
        "columnas_documentadas": len(MU_COLUMNS),
        "indice": str((OUTPUT_DIR / "_INDICE_COLUMNAS.tsv").relative_to(BASE_DIR)),
        "for_ing_catalogo": "gobernanza_for_ing_act.tsv",
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
