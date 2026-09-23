"""Genera el Diccionario Maestro U+ -> SIES/PES 2026 (insumo del requerimiento a Bettersoft).

El libro resultante reúne, con trazabilidad por fila:
inventario de procesos, perfil del reporte U+ "Datos Alumnos", matriz maestra por campo SIES,
diccionario consolidado para Bettersoft, catálogos y homologaciones, brechas, campos no
resolubles desde U+, contradicciones, datos sensibles y resumen por proceso.

Se leen en ejecución (sin exportar datos personales):
- DATOSDEALUMNOS_*.xlsx: solo estadísticos y catálogos de columnas no personales.
- control/catalogos/PUENTE_SIES_COMPILADO.tsv: ambigüedad U+ -> CODIGO_UNICO.
- oferta_academica_2027/11_gobernanza/CONTRATO_CAMPOS_ETAPA1_OFERTA_ACADEMICA_2027.tsv.
- procesos/ire_2026/data/estructura/20260706_89535_Estructura_IRE_ID_16770.csv.
El resto del contenido está codificado abajo, cada fila con su fuente.

Uso:
    python3 generar_diccionario_maestro_uplus_sies.py \
        --datos-alumnos /ruta/DATOSDEALUMNOS_11283.xlsx \
        --salida ../resultados/DICCIONARIO_MAESTRO_UPLUS_SIES_2026.xlsx
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

REPO = Path(__file__).resolve().parents[2]
GH = REPO.parent
WT = "_worktrees/avance_curricular_personal_academico_siipa_v4"

# ---------------------------------------------------------------------------
# Fuentes (rutas relativas a /Users/alexi/Documents/GitHub salvo indicación)
# ---------------------------------------------------------------------------
S = {
    "MAN_MU": "avance_curricular/manual_matrícula_unificada.txt (Manual de Proceso MU 2026; Anexo 7 Cuadros N°1-N°6, Anexo N°7)",
    "MAN_MU_C1": "Manual MU 2026, Anexo 7, Cuadro N°1 (pregrado)",
    "MAN_MU_C2": "Manual MU 2026, Anexo 7, Cuadro N°2 (posgrado y postítulo)",
    "MAN_MU_C3": "Manual MU 2026, Cuadro N°3 (Forma de Ingreso)",
    "MAN_MU_C4": "Manual MU 2026, Cuadro N°4 (País de nacionalidad, códigos 1-197)",
    "MAN_MU_C6": "Manual MU 2026, Cuadro N°6 (mensajes de error plataforma)",
    "GOB_MU": "avance_curricular/gobernanza_columnas_mu/gob_mu_<campo>.tsv",
    "COD_MU": "avance_curricular/codigo_gobernanza_v2.py",
    "CFG_ING": "avance_curricular/control/config_campos_ing.json",
    "CFG_VIG": "avance_curricular/control/config_vig_fecha.json",
    "GOB_VIG": "avance_curricular/gobernanza_catalogos/gob_datosalumnos_estadoacademico_situacion.tsv",
    "GOB_SEDE": "avance_curricular/gobernanza_sede.tsv",
    "GOB_NAC": "avance_curricular/gobernanza_nac.tsv",
    "GOB_PAIS": "avance_curricular/gobernanza_pais_est_sec.tsv",
    "GOB_FOR": "avance_curricular/gobernanza_for_ing_act.tsv",
    "GOB_NOTAS": "avance_curricular/gobernanza_escala_notas.tsv",
    "GOB_NIV": "avance_curricular/gobernanza_niveles.tsv",
    "DUR": "avance_curricular/DURACION_ESTUDIOS.tsv",
    "PUENTE": "avance_curricular/control/catalogos/PUENTE_SIES_COMPILADO.tsv",
    "FINAL_MU": "avance_curricular/outputs/validacion_ultima_subida_real_mu2026/20260730_213725/FINAL_4105.csv",
    "FINAL_MU_POS": "avance_curricular/outputs/congelados_matricula_unificada_2026/posgrado_postitulo/20260730_172147/matricula_unificada_2026_postgrado_postitulo.csv",
    "BASE_RET": "avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/ (MU enviadas 2022-2026)",
    "DA": "DATOSDEALUMNOS_11283.xlsx (Escritorio/Caracterizacion_2026-09-22_2026_P3_083205/01_ENTRADAS); misma estructura en 9282 y 10246",
    "PROM": "PROMEDIOSDEALUMNOS_7804.xlsx (hojas Hoja1, DatosAlumnos, matriz, base_datos)",
    "PROM_DIC": f"{WT}/avance_curricular_2026/07_control/DICCIONARIO_PROMEDIOSDEALUMNOS.tsv",
    "AC_NORM": f"{WT}/avance_curricular_2026/07_control/MATRIZ_NORMATIVA.tsv (extracto de Instructivo_Avance Curricular SIES - 2026.txt)",
    "AC_GOB": f"{WT}/avance_curricular_2026/03_gobernanza_columnas/",
    "AC_CIERRE": f"{WT}/avance_curricular_2026/07_cierre_columnas_16_21_y_preparacion_siguientes/.../INFORME_CIERRE_COLUMNAS_16_21_2371_NO_CARGA.md",
    "AC_READY": f"{WT}/avance_curricular_2026/14_sies_ready_5809/SIES_READY_TECNICO_5809_22_COLUMNAS_20260704_151418/",
    "EXT_REGLAS": f"{WT}/estudiantes_extranjeros_2026/docs/REGLAS_VALIDACION_INSTRUCTIVO 2.md",
    "EXT_GOB": f"{WT}/estudiantes_extranjeros_2026/resultados/reportes/REPORTE_GOBERNANZA_COLUMNAS_EXTRANJEROS_2025 2.md",
    "EXT_SCRIPT": f"{WT}/estudiantes_extranjeros_2026/scripts/corregir_gobernanza_extranjeros_2025_v2 2.py",
    "EXT_CIERRE": f"{WT}/estudiantes_extranjeros_2026/resultados/ejecuciones/RECONSTRUCCION_FINAL_EXTRANJEROS_2025_20260625_235455/13_CIERRE_AUTOMATIZADO/PES_READY_20260626_130431/10_REPORTE_CIERRE.md",
    "EXT_INTER": f"{WT}/estudiantes_extranjeros_2026/resultados/reportes/DIAGNOSTICO_ESTUDIANTES_INTERCAMBIO_2025 2.md",
    "OA_INS": "avance_curricular/oferta_academica_2027/01_fuentes_oficiales/Instructivo_Oferta_Academica-Acceso_CFT-IP 2027.txt",
    "OA_CONTRATO": "avance_curricular/oferta_academica_2027/11_gobernanza/CONTRATO_CAMPOS_ETAPA1_OFERTA_ACADEMICA_2027.tsv",
    "OA_MAPA": "avance_curricular/oferta_academica_2027/11_gobernanza/MAPA_ETAPAS_CARGAS_REPORTES_OFERTA_ACADEMICA_2027.md",
    "FCU_MAN": "CARACTERIZACIÓN/docs/Manual_de_Aplicacion_FCU_2026.txt (6.2 Estructura de variables; Anexos 2, 4, 5)",
    "FCU_COD": "CARACTERIZACIÓN/caracterizacion.py (funciones _fcu2026_*)",
    "FCU_CIERRE": "CARACTERIZACIÓN/docs/cierre_fcu_2026_p1/MANIFIESTO_CIERRE_FCU_2026_P1.md",
    "CNED_MAN": "Escritorio/CNED/CNED/Manual_INDICES_2025.txt (secciones 10, 16, 19)",
    "CNED_REP": "avance_curricular/indices_2025/cned/resultados/CNED_ARTEFACTO_OPERATIVO_LIMPIO_20260603_132333.md",
    "IRE": "avance_curricular/procesos/ire_2026/ (data/estructura/20260706_89535_Estructura_IRE_ID_16770.csv; config/parametros_2026.yaml)",
    "PA": "avance_curricular/personal_academico_2026/ y ramas feature/personal-academico-*",
}

# Columnas de la matriz maestra (sección 21 del encargo) + extras de control
MATRIZ_COLS = [
    "PROCESO", "SUBPROCESO", "AÑO_PROCESO", "AÑO_DATOS", "ARCHIVO_DESTINO", "POSICION_SIES",
    "CAMPO_SIES", "NOMBRE_DESCRIPTIVO_SIES", "DEFINICION_OFICIAL", "CODIGOS_SIES", "FORMATO_SIES",
    "OBLIGATORIEDAD", "REGLA_TEMPORAL", "GRANULARIDAD", "CAMPO_U_PLUS", "DEFINICION_U_PLUS",
    "VALORES_U_PLUS", "MAPEO_U_PLUS_SIES", "TIPO_OBTENCION", "CAMPO_NUEVO_BETTERSOFT",
    "DEFINICION_CAMPO_BETTERSOFT", "LOGICA_CALCULO", "LLAVE", "VALIDACION", "EJEMPLO_ORIGEN",
    "EJEMPLO_DESTINO", "FUENTE_OFICIAL", "FUENTE_INSTITUCIONAL", "SCRIPT_O_EVIDENCIA",
    "NIVEL_RESPALDO", "ESTADO", "OBSERVACIONES",
    # extras
    "CLASIFICACION_BRECHA", "REQUERIMIENTO_HISTORICO", "DATO_SENSIBLE", "PRECARGADO_SIES",
    "MODIFICABLE", "ID_DICCIONARIO",
]

TIPO_DESC = {
    "A": "A - Directo U+",
    "B": "B - Homologación simple",
    "C": "C - Transformación determinística",
    "D": "D - Derivado de varios campos",
    "E": "E - Requiere nuevo dato en U+",
    "F": "F - Fuente externa a U+",
    "G": "G - Precargado por SIES",
    "H": "H - No determinado",
}


def fila(**kw) -> dict:
    row = {c: "" for c in MATRIZ_COLS}
    for k, v in kw.items():
        if k not in row:
            raise KeyError(k)
        row[k] = v
    if row["TIPO_OBTENCION"] in TIPO_DESC:
        row["TIPO_OBTENCION"] = TIPO_DESC[row["TIPO_OBTENCION"]]
    return row


# ---------------------------------------------------------------------------
# MATRÍCULA UNIFICADA 2026 - PREGRADO (Cuadro N°1, 32 campos)
# ---------------------------------------------------------------------------
MU_BASE = dict(
    PROCESO="Matrícula Unificada",
    SUBPROCESO="Pregrado (Cuadro N°1)",
    AÑO_PROCESO="2026",
    AÑO_DATOS="2026 (matrícula 1er semestre 2026, corte SIES 30-abr-2026); campos *_ANT = año 2025",
    ARCHIVO_DESTINO="matricula_unificada_2026_pregrado.csv (CSV sin encabezado, ';', 32 columnas) - final: " + S["FINAL_MU"],
    FUENTE_OFICIAL=S["MAN_MU_C1"],
    PRECARGADO_SIES="NO",
    MODIFICABLE="SI (carga completa acumulativa)",
)


def mu(**kw):
    base = dict(MU_BASE)
    base.update(kw)
    return fila(**base)


MU_ROWS = [
    mu(POSICION_SIES="A", CAMPO_SIES="TIPO_DOC", NOMBRE_DESCRIPTIVO_SIES="Tipo de Documento",
       DEFINICION_OFICIAL="Tipo de documento de identificación del matriculado.",
       CODIGOS_SIES="R: RUT; P: Pasaporte", FORMATO_SIES="Letras mayúsculas", OBLIGATORIEDAD="Sí",
       REGLA_TEMPORAL="Atributo de persona vigente a la carga", GRANULARIDAD="PERSONA",
       CAMPO_U_PLUS="(no existe)", DEFINICION_U_PLUS="U+ solo entrega RUT con guion; no informa tipo de documento.",
       VALORES_U_PLUS="-", MAPEO_U_PLUS_SIES="Pipeline 2026 asigna constante 'R' (implementación).",
       TIPO_OBTENCION="E", CAMPO_NUEVO_BETTERSOFT="TIPO_DOCUMENTO_UPLUS + TIPO_DOCUMENTO_SIES",
       DEFINICION_CAMPO_BETTERSOFT="Ver UP-03 / UP-04", LOGICA_CALCULO="Tipo de documento registrado en ficha de persona U+; homologar a R/P.",
       LLAVE="ID persona / CODCLI", VALIDACION="Si P: DV vacío, NAC<>38 y FOR_ING_ACT en {4,6} (Cuadro N°6).",
       EJEMPLO_ORIGEN="(RUN registrado)", EJEMPLO_DESTINO="R",
       FUENTE_INSTITUCIONAL="Ninguna en U+", SCRIPT_O_EVIDENCIA=S["GOB_MU"].replace("<campo>", "tipo_doc") + "; " + S["BASE_RET"],
       NIVEL_RESPALDO="Oficial (regla) / Implementado (constante R)", ESTADO="PENDIENTE_DEMOSTRAR",
       OBSERVACIONES="MU 2025 informó 25 registros P; MU 2026 informó 0 P (constante). En U+ hay 68 RUT con cuerpo de 9 dígitos (DV módulo 11 válido).",
       CLASIFICACION_BRECHA="NUEVO_CAMPO_REQUERIDO", REQUERIMIENTO_HISTORICO="NO", DATO_SENSIBLE="SI (identificación)", ID_DICCIONARIO="UP-03; UP-04"),
    mu(POSICION_SIES="B", CAMPO_SIES="N_DOC", NOMBRE_DESCRIPTIVO_SIES="Número de Documento",
       DEFINICION_OFICIAL="Número de documento de identificación del matriculado.", CODIGOS_SIES="No aplica",
       FORMATO_SIES="Mayúsculas y números; sin 0 inicial; sin letras si TIPO_DOC=R", OBLIGATORIEDAD="Sí",
       REGLA_TEMPORAL="Atributo de persona", GRANULARIDAD="PERSONA", CAMPO_U_PLUS="RUT",
       DEFINICION_U_PLUS="RUN con guion y DV, sin puntos (patrón 99999999-9).", VALORES_U_PLUS="100% poblado; 12.575 RUT distintos en 14.644 filas",
       MAPEO_U_PLUS_SIES="Tomar parte numérica antes del guion.", TIPO_OBTENCION="C",
       CAMPO_NUEVO_BETTERSOFT="NUM_DOCUMENTO", DEFINICION_CAMPO_BETTERSOFT="Ver UP-05",
       LOGICA_CALCULO="split('-')[0], sin puntos.", LLAVE="ID persona", VALIDACION="Numérico si R; no inicia en 0; largo permitido.",
       EJEMPLO_ORIGEN="12345678-5", EJEMPLO_DESTINO="12345678", FUENTE_INSTITUCIONAL=S["DA"],
       SCRIPT_O_EVIDENCIA=S["COD_MU"] + " (_rut_num_only)", NIVEL_RESPALDO="Oficial + Implementado", ESTADO="Confirmado",
       CLASIFICACION_BRECHA="YA_EXISTE_U_PLUS", REQUERIMIENTO_HISTORICO="NO", DATO_SENSIBLE="SI (identificación)", ID_DICCIONARIO="UP-05"),
    mu(POSICION_SIES="C", CAMPO_SIES="DV", NOMBRE_DESCRIPTIVO_SIES="Dígito Verificador",
       DEFINICION_OFICIAL="Dígito verificador del RUT.", CODIGOS_SIES="0-9 y K", FORMATO_SIES="Número o K mayúscula; vacío si Pasaporte",
       OBLIGATORIEDAD="Condicional (obligatorio si R; vacío si P)", REGLA_TEMPORAL="Atributo de persona", GRANULARIDAD="PERSONA",
       CAMPO_U_PLUS="RUT", DEFINICION_U_PLUS="DV incluido tras el guion.", VALORES_U_PLUS="0-9, K (1.355 filas con K); DV válido módulo 11 en 100%",
       MAPEO_U_PLUS_SIES="Tomar carácter tras el guion, mayúscula.", TIPO_OBTENCION="C", CAMPO_NUEVO_BETTERSOFT="DV",
       DEFINICION_CAMPO_BETTERSOFT="Ver UP-06", LOGICA_CALCULO="split('-')[1].upper()", LLAVE="ID persona",
       VALIDACION="Módulo 11 coincide; vacío si P.", EJEMPLO_ORIGEN="12345678-5", EJEMPLO_DESTINO="5",
       FUENTE_INSTITUCIONAL=S["DA"], SCRIPT_O_EVIDENCIA=S["GOB_MU"].replace("<campo>", "dv"), NIVEL_RESPALDO="Oficial + Implementado",
       ESTADO="Confirmado", CLASIFICACION_BRECHA="YA_EXISTE_U_PLUS", REQUERIMIENTO_HISTORICO="NO", DATO_SENSIBLE="SI (identificación)", ID_DICCIONARIO="UP-06"),
    mu(POSICION_SIES="D", CAMPO_SIES="PRIMER_APELLIDO", NOMBRE_DESCRIPTIVO_SIES="Primer Apellido", DEFINICION_OFICIAL="Primer apellido.",
       CODIGOS_SIES="No aplica", FORMATO_SIES="Mayúsculas A-Z sin acentos; acepta ÄËÏÖÜ, guion y comilla simple; sin espacios iniciales/finales/dobles",
       OBLIGATORIEDAD="Sí", REGLA_TEMPORAL="Atributo de persona", GRANULARIDAD="PERSONA", CAMPO_U_PLUS="APELLIDO PATERNO",
       DEFINICION_U_PLUS="Apellido paterno en U+ (con tildes/Ñ).", VALORES_U_PLUS="100% poblado",
       MAPEO_U_PLUS_SIES="Mayúsculas, quitar tildes (NFKD), colapsar espacios.", TIPO_OBTENCION="C",
       CAMPO_NUEVO_BETTERSOFT="APELLIDO_PATERNO (+ versión normalizada SIES)", DEFINICION_CAMPO_BETTERSOFT="Ver UP-08",
       LOGICA_CALCULO="_normalize_text", LLAVE="ID persona", VALIDACION="Caracteres permitidos Cuadro N°6.",
       EJEMPLO_ORIGEN="Muñoz", EJEMPLO_DESTINO="MUNOZ", FUENTE_INSTITUCIONAL=S["DA"],
       SCRIPT_O_EVIDENCIA=S["GOB_MU"].replace("<campo>", "primer_apellido") + "; " + S["COD_MU"] + " (_normalize_text)",
       NIVEL_RESPALDO="Oficial + Implementado", ESTADO="Confirmado",
       OBSERVACIONES="Tratamiento de Ñ -> N es implementación (NFKD); el manual no lista Ñ explícitamente: validar con SIES.",
       CLASIFICACION_BRECHA="YA_EXISTE_U_PLUS", REQUERIMIENTO_HISTORICO="NO", DATO_SENSIBLE="SI (identificación)", ID_DICCIONARIO="UP-08"),
    mu(POSICION_SIES="E", CAMPO_SIES="SEGUNDO_APELLIDO", NOMBRE_DESCRIPTIVO_SIES="Segundo Apellido", DEFINICION_OFICIAL="Segundo apellido.",
       CODIGOS_SIES="No aplica", FORMATO_SIES="Igual a PRIMER_APELLIDO; puede quedar vacío cuando corresponda",
       OBLIGATORIEDAD="Condicional (puede ir vacío)", REGLA_TEMPORAL="Atributo de persona", GRANULARIDAD="PERSONA", CAMPO_U_PLUS="APELLIDO MATERNO",
       DEFINICION_U_PLUS="Apellido materno en U+.", VALORES_U_PLUS="99,8% poblado (22 vacíos)", MAPEO_U_PLUS_SIES="Igual a PRIMER_APELLIDO.",
       TIPO_OBTENCION="C", CAMPO_NUEVO_BETTERSOFT="APELLIDO_MATERNO", DEFINICION_CAMPO_BETTERSOFT="Ver UP-09", LOGICA_CALCULO="_normalize_text",
       LLAVE="ID persona", VALIDACION="Caracteres permitidos.", EJEMPLO_ORIGEN="Peña", EJEMPLO_DESTINO="PENA", FUENTE_INSTITUCIONAL=S["DA"],
       SCRIPT_O_EVIDENCIA=S["GOB_MU"].replace("<campo>", "segundo_apellido"), NIVEL_RESPALDO="Oficial + Implementado", ESTADO="Confirmado",
       CLASIFICACION_BRECHA="YA_EXISTE_U_PLUS", REQUERIMIENTO_HISTORICO="NO", DATO_SENSIBLE="SI (identificación)", ID_DICCIONARIO="UP-09"),
    mu(POSICION_SIES="F", CAMPO_SIES="NOMBRE", NOMBRE_DESCRIPTIVO_SIES="Nombres", DEFINICION_OFICIAL="Nombres.", CODIGOS_SIES="No aplica",
       FORMATO_SIES="Igual a PRIMER_APELLIDO", OBLIGATORIEDAD="Sí", REGLA_TEMPORAL="Atributo de persona", GRANULARIDAD="PERSONA",
       CAMPO_U_PLUS="NOMBRES", DEFINICION_U_PLUS="Nombres de pila en U+ (la columna NOMBRE es el nombre completo concatenado).",
       VALORES_U_PLUS="100% poblado", MAPEO_U_PLUS_SIES="Igual a PRIMER_APELLIDO.", TIPO_OBTENCION="C", CAMPO_NUEVO_BETTERSOFT="NOMBRES",
       DEFINICION_CAMPO_BETTERSOFT="Ver UP-07", LOGICA_CALCULO="_normalize_text", LLAVE="ID persona", VALIDACION="No vacío; caracteres permitidos.",
       EJEMPLO_ORIGEN="José Ángel", EJEMPLO_DESTINO="JOSE ANGEL", FUENTE_INSTITUCIONAL=S["DA"],
       SCRIPT_O_EVIDENCIA=S["GOB_MU"].replace("<campo>", "nombre"), NIVEL_RESPALDO="Oficial + Implementado", ESTADO="Confirmado",
       OBSERVACIONES="No usar columna U+ 'NOMBRE' (concatenada; coincide con NOMBRES+APELLIDOS solo en 94,4%).",
       CLASIFICACION_BRECHA="YA_EXISTE_U_PLUS", REQUERIMIENTO_HISTORICO="NO", DATO_SENSIBLE="SI (identificación)", ID_DICCIONARIO="UP-07"),
    mu(POSICION_SIES="G", CAMPO_SIES="SEXO", NOMBRE_DESCRIPTIVO_SIES="Sexo",
       DEFINICION_OFICIAL="Corresponde a la condición de mujer, hombre o no binario de la persona reportada.",
       CODIGOS_SIES="H: Hombre; M: Mujer; NB: No Binario", FORMATO_SIES="Letras mayúsculas", OBLIGATORIEDAD="Sí",
       REGLA_TEMPORAL="Atributo de persona", GRANULARIDAD="PERSONA", CAMPO_U_PLUS="SEXO",
       DEFINICION_U_PLUS="Código institucional de sexo. M = masculino, F = femenino (equivalencia confirmada en MU y Extranjeros); S = sin significado documentado.",
       VALORES_U_PLUS="M: 10.853; F: 3.781; S: 10", MAPEO_U_PLUS_SIES="M -> H; F -> M; S -> NB (solo implementado MU, sin respaldo documental)",
       TIPO_OBTENCION="B", CAMPO_NUEVO_BETTERSOFT="SEXO_UPLUS + SEXO_SIES_MU", DEFINICION_CAMPO_BETTERSOFT="Ver UP-10 / UP-11",
       LOGICA_CALCULO="_normalize_sexo_mu", LLAVE="ID persona", VALIDACION="Catálogo H/M/NB.",
       EJEMPLO_ORIGEN="F", EJEMPLO_DESTINO="M", FUENTE_INSTITUCIONAL=S["DA"],
       SCRIPT_O_EVIDENCIA=S["COD_MU"] + " (_normalize_sexo_mu); " + S["EXT_SCRIPT"] + " ('F institucional -> M SIES; M institucional -> H SIES')",
       NIVEL_RESPALDO="Oficial (códigos SIES) + Implementado (M/F confirmado en 2 procesos) + Pendiente (S)",
       ESTADO="Confirmado para M y F; PENDIENTE_DEMOSTRAR para S",
       OBSERVACIONES="Riesgo alto de error: la letra M significa hombre en U+ y mujer en SIES. En Extranjeros, 12 casos quedaron pendientes por falta de equivalencia normativa.",
       CLASIFICACION_BRECHA="EXISTE_PERO_REQUIERE_HOMOLOGACION", REQUERIMIENTO_HISTORICO="NO", DATO_SENSIBLE="SI", ID_DICCIONARIO="UP-10; UP-11"),
    mu(POSICION_SIES="H", CAMPO_SIES="FECH_NAC", NOMBRE_DESCRIPTIVO_SIES="Fecha de Nacimiento", DEFINICION_OFICIAL="Fecha de nacimiento.",
       CODIGOS_SIES="No aplica", FORMATO_SIES="dd/mm/aaaa; no menor a 01/01/1900; no vacía; edad >= 15", OBLIGATORIEDAD="Sí",
       REGLA_TEMPORAL="Atributo de persona", GRANULARIDAD="PERSONA", CAMPO_U_PLUS="FECHANACIMIENTO",
       DEFINICION_U_PLUS="Fecha de nacimiento (texto dd-mm-aaaa).", VALORES_U_PLUS="100% poblado; patrón 99-99-9999",
       MAPEO_U_PLUS_SIES="Cambiar separador '-' por '/'.", TIPO_OBTENCION="C", CAMPO_NUEVO_BETTERSOFT="FECHA_NACIMIENTO",
       DEFINICION_CAMPO_BETTERSOFT="Ver UP-13", LOGICA_CALCULO="_to_ddmmyyyy", LLAVE="ID persona",
       VALIDACION="Fecha válida; >= 01/01/1900; edad >= 15 años al año de proceso.", EJEMPLO_ORIGEN="07-04-1995", EJEMPLO_DESTINO="07/04/1995",
       FUENTE_INSTITUCIONAL=S["DA"], SCRIPT_O_EVIDENCIA=S["GOB_MU"].replace("<campo>", "fech_nac"),
       NIVEL_RESPALDO="Oficial + Implementado", ESTADO="Confirmado",
       OBSERVACIONES="El fallback implementado 01/01/1900 contradice el Cuadro N°6 ('no puede estar vacía'); no aplicarlo como regla.",
       CLASIFICACION_BRECHA="YA_EXISTE_U_PLUS", REQUERIMIENTO_HISTORICO="NO", DATO_SENSIBLE="SI", ID_DICCIONARIO="UP-13"),
    mu(POSICION_SIES="I", CAMPO_SIES="NAC", NOMBRE_DESCRIPTIVO_SIES="Nacionalidad", DEFINICION_OFICIAL="País de nacionalidad.",
       CODIGOS_SIES="1 al 197 (Cuadro N°4; 38 = Chile)", FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí",
       REGLA_TEMPORAL="Atributo de persona", GRANULARIDAD="PERSONA", CAMPO_U_PLUS="NACIONALIDAD",
       DEFINICION_U_PLUS="Gentilicio en texto libre con variantes de mayúsculas.",
       VALORES_U_PLUS="27 variantes (Chilena 11.332; CHILENA 2.834; Venezolana 132; Peruana 103; ... ; Por definir 5)",
       MAPEO_U_PLUS_SIES="Normalizar texto y homologar con gobernanza_nac.tsv (p.ej. CHILENA->38, VENEZOLANA->192, PERUANA->142).",
       TIPO_OBTENCION="B", CAMPO_NUEVO_BETTERSOFT="NACIONALIDAD_UPLUS + COD_NACIONALIDAD_SIES", DEFINICION_CAMPO_BETTERSOFT="Ver UP-14 / UP-15",
       LOGICA_CALCULO="Tabla de homologación gentilicio -> código Cuadro N°4.", LLAVE="ID persona",
       VALIDACION="1..197; si TIPO_DOC=P no puede ser 38.", EJEMPLO_ORIGEN="Peruana", EJEMPLO_DESTINO="142",
       FUENTE_INSTITUCIONAL=S["DA"], SCRIPT_O_EVIDENCIA=S["GOB_NAC"] + "; " + S["GOB_MU"].replace("<campo>", "nac"),
       NIVEL_RESPALDO="Oficial (códigos) + Interno (tabla validada contra Cuadro N°4)", ESTADO="Confirmado (16 gentilicios); PENDIENTE 'Por definir'",
       OBSERVACIONES="Fallback implementado '38 si no mapea' no es regla oficial.",
       CLASIFICACION_BRECHA="EXISTE_PERO_REQUIERE_HOMOLOGACION", REQUERIMIENTO_HISTORICO="NO", DATO_SENSIBLE="SI", ID_DICCIONARIO="UP-14; UP-15"),
    mu(POSICION_SIES="J", CAMPO_SIES="PAIS_EST_SEC", NOMBRE_DESCRIPTIVO_SIES="País Estudios Secundarios",
       DEFINICION_OFICIAL="País donde completó sus estudios secundarios.", CODIGOS_SIES="1 al 197 (Cuadro N°4)", FORMATO_SIES="Solo números",
       OBLIGATORIEDAD="Sí", REGLA_TEMPORAL="Atributo de persona (hecho histórico)", GRANULARIDAD="PERSONA",
       CAMPO_U_PLUS="(no existe) - se usa COMUNACOLEGIO / CIUDADCOLEGIO", DEFINICION_U_PLUS="Comuna y ciudad del colegio de egreso; no hay país.",
       VALORES_U_PLUS="CIUDADCOLEGIO: 48 ciudades (47 chilenas + LA HABANA 1)",
       MAPEO_U_PLUS_SIES="Tabla comuna/ciudad -> país (gobernanza_pais_est_sec.tsv, todo Chile=38) y fallback 38.",
       TIPO_OBTENCION="E", CAMPO_NUEVO_BETTERSOFT="COD_PAIS_ESTUDIOS_SECUNDARIOS_SIES", DEFINICION_CAMPO_BETTERSOFT="Ver UP-16",
       LOGICA_CALCULO="Dato a registrar en U+ (país del establecimiento de egreso de enseñanza media).", LLAVE="ID persona",
       VALIDACION="1..197.", EJEMPLO_ORIGEN="(colegio en Venezuela)", EJEMPLO_DESTINO="192",
       FUENTE_INSTITUCIONAL=S["DA"], SCRIPT_O_EVIDENCIA=S["GOB_PAIS"] + "; " + S["BASE_RET"],
       NIVEL_RESPALDO="Oficial (regla) / Implementado (inferencia)", ESTADO="PENDIENTE_DEMOSTRAR",
       OBSERVACIONES="MU 2026 informó 38 en el 100% de las filas aunque 81 tienen NAC distinta de 38 (MU 2025 sí informó otros países). Indicio de inferencia por fallback.",
       CLASIFICACION_BRECHA="NUEVO_CAMPO_REQUERIDO", REQUERIMIENTO_HISTORICO="NO", DATO_SENSIBLE="NO", ID_DICCIONARIO="UP-16"),
    mu(POSICION_SIES="K", CAMPO_SIES="COD_SED", NOMBRE_DESCRIPTIVO_SIES="Código de Sede",
       DEFINICION_OFICIAL="Código de sede de la IES en la que se encuentra matriculado.", CODIGOS_SIES="Códigos correspondientes a la institución (Oferta Académica)",
       FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí", REGLA_TEMPORAL="Sede de la matrícula del período", GRANULARIDAD="MATRÍCULA / OFERTA",
       CAMPO_U_PLUS="SEDE", DEFINICION_U_PLUS="Sede U+: RE = Casa Central Santiago; CO = Concepción.", VALORES_U_PLUS="RE: 14.533; CO: 111",
       MAPEO_U_PLUS_SIES="RE -> 2; CO -> 3 (también se obtiene del componente S del CODIGO_UNICO)", TIPO_OBTENCION="B",
       CAMPO_NUEVO_BETTERSOFT="SEDE_UPLUS + COD_SEDE_SIES", DEFINICION_CAMPO_BETTERSOFT="Ver UP-23", LOGICA_CALCULO="gobernanza_sede.tsv",
       LLAVE="CODCLI", VALIDACION="Combinación sede-carrera-jornada-modalidad-versión existe en Oferta Académica 2026.",
       EJEMPLO_ORIGEN="CO", EJEMPLO_DESTINO="3", FUENTE_INSTITUCIONAL=S["DA"],
       SCRIPT_O_EVIDENCIA=S["GOB_SEDE"] + " ('Regla negocio validada contra oferta académica'); " + S["BASE_RET"] + " (2026: 2=4.032, 3=73)",
       NIVEL_RESPALDO="Interno + Observado en carga", ESTADO="Confirmado",
       CLASIFICACION_BRECHA="EXISTE_PERO_REQUIERE_HOMOLOGACION", REQUERIMIENTO_HISTORICO="SI (sede al período informado)", DATO_SENSIBLE="NO", ID_DICCIONARIO="UP-23"),
    mu(POSICION_SIES="L", CAMPO_SIES="COD_CAR", NOMBRE_DESCRIPTIVO_SIES="Código de Carrera",
       DEFINICION_OFICIAL="Código de carrera de la IES en la que se encuentra matriculado.", CODIGOS_SIES="Códigos de Oferta Académica (numéricos)",
       FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí", REGLA_TEMPORAL="Oferta del año de proceso", GRANULARIDAD="OFERTA",
       CAMPO_U_PLUS="CODCARPR (código interno alfanumérico) + JORNADA + NOMBRE_L",
       DEFINICION_U_PLUS="Código interno de carrera/programa U+ (p.ej. 'IINF'); no es el código SIES.", VALORES_U_PLUS="116 códigos distintos",
       MAPEO_U_PLUS_SIES="Llave JORNADA|CODCARPR|NOMBRE_L -> CODIGO_UNICO (PUENTE_SIES_COMPILADO) -> componente C.",
       TIPO_OBTENCION="E", CAMPO_NUEVO_BETTERSOFT="CODIGO_UNICO_SIES y COD_CARRERA_SIES", DEFINICION_CAMPO_BETTERSOFT="Ver UP-27",
       LOGICA_CALCULO="Parse regex I162S(sede)C(carrera)J(jornada)V(versión).", LLAVE="CODCLI + plan",
       VALIDACION="Existe en Oferta Académica del año.", EJEMPLO_ORIGEN="D|IINF|INGENIERIA EN INFORMATICA", EJEMPLO_DESTINO="1",
       FUENTE_INSTITUCIONAL=S["DUR"] + "; " + S["PUENTE"], SCRIPT_O_EVIDENCIA=S["COD_MU"] + " (_extract_cod_car_from_sies_code; merge SOURCE_KEY_3)",
       NIVEL_RESPALDO="Implementado + Interno", ESTADO="PENDIENTE_DEMOSTRAR (70 de 161 combinaciones U+ son ambiguas)",
       OBSERVACIONES="La ambigüedad se resuelve hoy con heurísticas (año de ingreso, plan). No es determinístico desde U+.",
       CLASIFICACION_BRECHA="NUEVO_CAMPO_REQUERIDO", REQUERIMIENTO_HISTORICO="SI (código vigente al período)", DATO_SENSIBLE="NO", ID_DICCIONARIO="UP-27"),
    mu(POSICION_SIES="M", CAMPO_SIES="MODALIDAD", NOMBRE_DESCRIPTIVO_SIES="Modalidad", DEFINICION_OFICIAL="Modalidad de la carrera o programa.",
       CODIGOS_SIES="Códigos de Oferta Académica: 1 Presencial; 2 Semipresencial; 3 No Presencial (Instructivo Oferta 2027)",
       FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí", REGLA_TEMPORAL="Atributo de la oferta del año", GRANULARIDAD="OFERTA",
       CAMPO_U_PLUS="(no existe). ATENCIÓN: la columna U+ 'MODALIDAD' es la modalidad de enseñanza media del estudiante.",
       DEFINICION_U_PLUS="U+ MODALIDAD = CIENTIFICO-HUMANISTA / TÉCNICO-PROFESIONAL (67,5% poblado). No representa la modalidad del programa.",
       VALORES_U_PLUS="-", MAPEO_U_PLUS_SIES="Desde Oferta por CODIGO_UNICO; si falta, inferido desde jornada (D/V->1, O->3).",
       TIPO_OBTENCION="E", CAMPO_NUEVO_BETTERSOFT="MODALIDAD_PROGRAMA_SIES", DEFINICION_CAMPO_BETTERSOFT="Ver UP-26",
       LOGICA_CALCULO="Atributo del CODIGO_UNICO en Oferta Académica.", LLAVE="CODIGO_UNICO",
       VALIDACION="Consistencia MODALIDAD-JORNADA (Instructivo Oferta: J1/J2 no pueden ser 3; J4 solo con 3).",
       EJEMPLO_ORIGEN="(programa online)", EJEMPLO_DESTINO="3", FUENTE_INSTITUCIONAL=S["DUR"],
       SCRIPT_O_EVIDENCIA=S["COD_MU"] + " (_map_jornada_to_mod_jor, _modalidad_from_jor); " + S["OA_INS"] + " p.7-9",
       NIVEL_RESPALDO="Oficial (códigos Oferta) + Implementado", ESTADO="PENDIENTE_DEMOSTRAR (sin dato en U+)",
       OBSERVACIONES="MU remite a 'códigos correspondientes a la institución'; el catálogo 1/2/3 proviene del Instructivo de Oferta Académica (año distinto: Oferta 2027, proceso 2026). Enviados 2026: 1=898; 3=3.207.",
       CLASIFICACION_BRECHA="NUEVO_CAMPO_REQUERIDO", REQUERIMIENTO_HISTORICO="SI", DATO_SENSIBLE="NO", ID_DICCIONARIO="UP-26"),
    mu(POSICION_SIES="N", CAMPO_SIES="JOR", NOMBRE_DESCRIPTIVO_SIES="Jornada", DEFINICION_OFICIAL="Jornada de la carrera o programa.",
       CODIGOS_SIES="Códigos de Oferta Académica: 1 Diurna; 2 Vespertina; 3 Semipresencial; 4 A Distancia; 5 Otra",
       FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí", REGLA_TEMPORAL="Jornada de la matrícula del período", GRANULARIDAD="MATRÍCULA / OFERTA",
       CAMPO_U_PLUS="JORNADA", DEFINICION_U_PLUS="Jornada U+: D, V, O (O = online según implementación).",
       VALORES_U_PLUS="O: 8.434; V: 4.867 (+221 'V '); D: 1.058 (+64 'D ')",
       MAPEO_U_PLUS_SIES="D -> 1 (22/22 combinaciones); V -> 2 (44/44); O -> 4 (94/95) y O -> 3 en 1 programa (DCBS Diplomado en Ciberseguridad Aplicada)",
       TIPO_OBTENCION="B", CAMPO_NUEVO_BETTERSOFT="JORNADA_UPLUS + COD_JORNADA_SIES", DEFINICION_CAMPO_BETTERSOFT="Ver UP-25",
       LOGICA_CALCULO="Valor final = componente J del CODIGO_UNICO.", LLAVE="CODCLI",
       VALIDACION="Sin espacios; consistencia con MODALIDAD.", EJEMPLO_ORIGEN="V", EJEMPLO_DESTINO="2",
       FUENTE_INSTITUCIONAL=S["DA"] + "; " + S["PUENTE"],
       SCRIPT_O_EVIDENCIA=S["COD_MU"] + " (_map_jornada_to_mod_jor); cruce PUENTE_SIES_COMPILADO JORNADA x J",
       NIVEL_RESPALDO="Oficial (códigos) + Implementado + Observado", ESTADO="Confirmado D y V; PENDIENTE_DEMOSTRAR O (no determinístico)",
       OBSERVACIONES="285 filas con espacio final en JORNADA ('V ', 'D ').",
       CLASIFICACION_BRECHA="EXISTE_PERO_REQUIERE_HOMOLOGACION", REQUERIMIENTO_HISTORICO="SI (cambios de jornada: SITUACION 49)", DATO_SENSIBLE="NO", ID_DICCIONARIO="UP-25"),
    mu(POSICION_SIES="O", CAMPO_SIES="VERSION", NOMBRE_DESCRIPTIVO_SIES="Versión", DEFINICION_OFICIAL="Versión de la carrera o programa.",
       CODIGOS_SIES="Códigos de Oferta Académica (correlativo)", FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí",
       REGLA_TEMPORAL="Versión del programa en que está matriculado", GRANULARIDAD="OFERTA / PLAN", CAMPO_U_PLUS="(no existe)",
       DEFINICION_U_PLUS="U+ no registra versión SIES; se aproxima por plan de estudio (Hoja1 PLAN_DE_ESTUDIO) y año de ingreso.",
       VALORES_U_PLUS="-", MAPEO_U_PLUS_SIES="Componente V del CODIGO_UNICO resuelto por el puente.", TIPO_OBTENCION="E",
       CAMPO_NUEVO_BETTERSOFT="CODIGO_UNICO_SIES (incluye versión)", DEFINICION_CAMPO_BETTERSOFT="Ver UP-27",
       LOGICA_CALCULO="Parse V del CODIGO_UNICO.", LLAVE="CODCLI + plan", VALIDACION="Existe en Oferta Académica.",
       EJEMPLO_ORIGEN="IINF (plan 2024)", EJEMPLO_DESTINO="2", FUENTE_INSTITUCIONAL=S["PUENTE"],
       SCRIPT_O_EVIDENCIA=S["GOB_MU"].replace("<campo>", "version") + "; " + S["COD_MU"] + " (resolver_ambiguedad_sies)",
       NIVEL_RESPALDO="Implementado", ESTADO="PENDIENTE_DEMOSTRAR", OBSERVACIONES="Enviados 2026: V1=2.786; V2=789; V3=489; V4=41.",
       CLASIFICACION_BRECHA="NUEVO_CAMPO_REQUERIDO", REQUERIMIENTO_HISTORICO="SI", DATO_SENSIBLE="NO", ID_DICCIONARIO="UP-27"),
    mu(POSICION_SIES="P", CAMPO_SIES="FOR_ING_ACT", NOMBRE_DESCRIPTIVO_SIES="Forma Ingreso Carrera Actual",
       DEFINICION_OFICIAL="Vía de admisión de la carrera o programa (Cuadro N°3).",
       CODIGOS_SIES="1 Ingreso Directo (regular); 2 Continuidad Plan Común/Bachillerato; 3 Cambio Interno; 4 Cambio Externo; 5 RAP; 6 Ingreso especial extranjeros; 7 PACE; 8 Programas de Inclusión; 9 Características especiales; 10 Otras formas; 11 Articulación TNS a profesional",
       FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí", REGLA_TEMPORAL="Vía efectiva por la que ingresó a la carrera actual (hecho del ingreso)",
       GRANULARIDAD="MATRÍCULA", CAMPO_U_PLUS="VIASDEADMISION; CATEGORIA; SITUACION; NOMBRE_L",
       DEFINICION_U_PLUS="U+ no tiene la vía SIES. VIASDEADMISION describe origen escolar; CATEGORIA describe tipo de matrícula.",
       VALORES_U_PLUS="VIASDEADMISION: ENSEÑANZA MEDIA NACIONAL 14.271; PROGRAMA DE EDUCACION CONTINUA 292; EXTRANJERO 64; MNP AA 3. CATEGORIA: NORMAL, PROCESO DE TITULO, INGRESO ESPECIAL, MATRICULA II SEM-CIISA TRAINING, DIPLOMADO, VÍA DE ADMISIÓN ESPECIAL IQ",
       MAPEO_U_PLUS_SIES="Implementado: ENSEÑANZA MEDIA NACIONAL->1; EXTRANJERO->6; PROGRAMA EDUCACION CONTINUA->11 si continuidad/articulación, si no 10; MNP AA->10; SITUACION 24/49/27->3; nombre con 'CONTINUIDAD'->2; traza de articulación->11",
       TIPO_OBTENCION="E", CAMPO_NUEVO_BETTERSOFT="FORMA_INGRESO_SIES (+ VIA_ADMISION_UPLUS raw)", DEFINICION_CAMPO_BETTERSOFT="Ver UP-33",
       LOGICA_CALCULO="Debe registrarse en U+ al matricular (vía efectiva de ingreso).", LLAVE="CODCLI",
       VALIDACION="Cuadro N°6: FOR 1,6-10 => ORI=ACT; FOR 2,3 => ASI_INS_HIS>0; P => FOR 4 o 6; continuidad => FOR en {2,3,4,5,11}.",
       EJEMPLO_ORIGEN="VIASDEADMISION='ENSEÑANZA MEDIA  NACIONAL'", EJEMPLO_DESTINO="1",
       FUENTE_INSTITUCIONAL=S["DA"], SCRIPT_O_EVIDENCIA=S["COD_MU"] + " (_resolve_for_ing_act_row; overrides L3934-3970); " + S["GOB_FOR"],
       NIVEL_RESPALDO="Oficial (catálogo) / Implementado (heurísticas)", ESTADO="PENDIENTE_DEMOSTRAR",
       OBSERVACIONES="Contradicciones CT-02 y CT-03. Enviados 2026: 1=3.593; 2=378; 3=95; 11=32; 6=7.",
       CLASIFICACION_BRECHA="NUEVO_CAMPO_REQUERIDO", REQUERIMIENTO_HISTORICO="NO (hecho fijo del ingreso)", DATO_SENSIBLE="NO", ID_DICCIONARIO="UP-33"),
    mu(POSICION_SIES="Q", CAMPO_SIES="ANIO_ING_ACT", NOMBRE_DESCRIPTIVO_SIES="Año de Ingreso Carrera Actual",
       DEFINICION_OFICIAL="Año de ingreso a la carrera actual.", CODIGOS_SIES="1990 a 2026", FORMATO_SIES="Solo números",
       OBLIGATORIEDAD="Sí", REGLA_TEMPORAL="Año calendario de ingreso al programa actual", GRANULARIDAD="MATRÍCULA", CAMPO_U_PLUS="ANOINGRESO",
       DEFINICION_U_PLUS="Año de ingreso de la matrícula (CODCLI); coincide con el prefijo del CODCLI en 96,9%.", VALORES_U_PLUS="1989-2026 (1 fila 1989 fuera de rango SIES)",
       MAPEO_U_PLUS_SIES="Copia directa.", TIPO_OBTENCION="A", CAMPO_NUEVO_BETTERSOFT="ANIO_INGRESO_CARRERA_ACTUAL", DEFINICION_CAMPO_BETTERSOFT="Ver UP-31",
       LOGICA_CALCULO="Directo.", LLAVE="CODCLI", VALIDACION="1990..año proceso; ORI <= ACT.", EJEMPLO_ORIGEN="2024", EJEMPLO_DESTINO="2024",
       FUENTE_INSTITUCIONAL=S["DA"], SCRIPT_O_EVIDENCIA=S["CFG_ING"] + "; " + S["GOB_MU"].replace("<campo>", "anio_ing_act"),
       NIVEL_RESPALDO="Oficial + Implementado", ESTADO="Confirmado",
       OBSERVACIONES="Fallbacks implementados (año desde CODCLI; 2026 por defecto) no son regla oficial.",
       CLASIFICACION_BRECHA="YA_EXISTE_U_PLUS", REQUERIMIENTO_HISTORICO="NO", DATO_SENSIBLE="NO", ID_DICCIONARIO="UP-31"),
    mu(POSICION_SIES="R", CAMPO_SIES="SEM_ING_ACT", NOMBRE_DESCRIPTIVO_SIES="Semestre de Ingreso Carrera Actual",
       DEFINICION_OFICIAL="Semestre de ingreso a la carrera actual.", CODIGOS_SIES="1 a 2", FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí",
       REGLA_TEMPORAL="Semestre del ingreso", GRANULARIDAD="MATRÍCULA", CAMPO_U_PLUS="PERIODOINGRESO",
       DEFINICION_U_PLUS="Período de ingreso U+: 1, 2 o 3. El 3 aparece solo en jornadas O y V (posible régimen trimestral; significado no documentado).",
       VALORES_U_PLUS="1: 11.899; 2: 1.998; 3: 747", MAPEO_U_PLUS_SIES="1 -> 1; 2 -> 2; 3 -> 2 (regla institucional)",
       TIPO_OBTENCION="B", CAMPO_NUEVO_BETTERSOFT="PERIODO_INGRESO_UPLUS + SEM_INGRESO_CARRERA_ACTUAL_SIES", DEFINICION_CAMPO_BETTERSOFT="Ver UP-32",
       LOGICA_CALCULO="config_campos_ing.json regla_institucional", LLAVE="CODCLI", VALIDACION="1/2.", EJEMPLO_ORIGEN="3", EJEMPLO_DESTINO="2",
       FUENTE_INSTITUCIONAL=S["DA"], SCRIPT_O_EVIDENCIA=S["CFG_ING"], NIVEL_RESPALDO="Oficial (códigos) + Decisión interna (3->2)",
       ESTADO="Confirmado 1 y 2; PENDIENTE_DEMOSTRAR 3", OBSERVACIONES="Ver CT-09.",
       CLASIFICACION_BRECHA="EXISTE_PERO_REQUIERE_HOMOLOGACION", REQUERIMIENTO_HISTORICO="NO", DATO_SENSIBLE="NO", ID_DICCIONARIO="UP-32"),
    mu(POSICION_SIES="S", CAMPO_SIES="ANIO_ING_ORI", NOMBRE_DESCRIPTIVO_SIES="Año de Ingreso Carrera de Origen",
       DEFINICION_OFICIAL="Año de ingreso a la carrera de origen (año de ingreso como estudiante de primer año a la carrera de origen o programa vinculante).",
       CODIGOS_SIES="1980 a 2026 y 1900 (imposible identificar)", FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí",
       REGLA_TEMPORAL="Hecho histórico de trayectoria", GRANULARIDAD="MATRÍCULA (trayectoria de la persona)",
       CAMPO_U_PLUS="(no existe) - se busca otro CODCLI del mismo RUT en DatosAlumnos o Hoja1",
       DEFINICION_U_PLUS="U+ no vincula la matrícula actual con la de origen.", VALORES_U_PLUS="-",
       MAPEO_U_PLUS_SIES="Por FOR_ING_ACT: 1,5-10 => = ANIO_ING_ACT; 3 => año del programa anterior (otro CODCLI) o 1900; 4 => 1900; 11 => año TNS previo o 1900",
       TIPO_OBTENCION="E", CAMPO_NUEVO_BETTERSOFT="CODCLI_ORIGEN; TIPO_ORIGEN; ANIO_INGRESO_ORIGEN", DEFINICION_CAMPO_BETTERSOFT="Ver UP-34 a UP-36",
       LOGICA_CALCULO="Vínculo explícito matrícula actual -> matrícula/programa de origen registrado en U+.", LLAVE="CODCLI -> CODCLI_ORIGEN",
       VALIDACION="ORI <= ACT; 1900 => SEM_ING_ORI=0; FOR 1,6-10 => ORI=ACT; FOR 1,2,3,6-10 => no 1900; continuidad => ORI<>2026.",
       EJEMPLO_ORIGEN="CODCLI actual 2024 + CODCLI origen 2021", EJEMPLO_DESTINO="2021",
       FUENTE_INSTITUCIONAL=S["DA"] + "; " + S["PROM"], SCRIPT_O_EVIDENCIA=S["CFG_ING"] + " (reglas_por_for_ing_act); " + S["MAN_MU"] + " (sección 4 y Anexo N°7)",
       NIVEL_RESPALDO="Oficial (reglas) / Implementado (búsqueda por RUT)", ESTADO="PENDIENTE_DEMOSTRAR",
       OBSERVACIONES="Manual: cambio externo => origen externo 1900; articulación => programa vinculante o 1900. config dice FOR=2 => 1900, pero en 2026 las 378 filas FOR=2 no tienen 1900 (implementación cambió).",
       CLASIFICACION_BRECHA="NUEVO_CAMPO_REQUERIDO", REQUERIMIENTO_HISTORICO="SI (trayectoria)", DATO_SENSIBLE="NO", ID_DICCIONARIO="UP-34; UP-35; UP-36"),
    mu(POSICION_SIES="T", CAMPO_SIES="SEM_ING_ORI", NOMBRE_DESCRIPTIVO_SIES="Semestre de Ingreso Carrera de Origen",
       DEFINICION_OFICIAL="Semestre de ingreso a la carrera de origen.", CODIGOS_SIES="1 a 2 y 0 (solo si ANIO_ING_ORI=1900)", FORMATO_SIES="Solo números",
       OBLIGATORIEDAD="Sí", REGLA_TEMPORAL="Hecho histórico", GRANULARIDAD="MATRÍCULA (trayectoria)", CAMPO_U_PLUS="(no existe)",
       DEFINICION_U_PLUS="Igual a ANIO_ING_ORI.", VALORES_U_PLUS="-", MAPEO_U_PLUS_SIES="Copia de SEM_ING_ACT o del período del CODCLI de origen; 0 si 1900.",
       TIPO_OBTENCION="E", CAMPO_NUEVO_BETTERSOFT="SEM_INGRESO_ORIGEN", DEFINICION_CAMPO_BETTERSOFT="Ver UP-37",
       LOGICA_CALCULO="Período de ingreso del CODCLI de origen homologado a 1/2.", LLAVE="CODCLI_ORIGEN",
       VALIDACION="0 <=> 1900; FOR 2,3,4,11 con mismo año => SEM_ORI < SEM_ACT.", EJEMPLO_ORIGEN="PERIODOINGRESO origen=1", EJEMPLO_DESTINO="1",
       FUENTE_INSTITUCIONAL=S["DA"], SCRIPT_O_EVIDENCIA=S["CFG_ING"], NIVEL_RESPALDO="Oficial + Implementado", ESTADO="PENDIENTE_DEMOSTRAR",
       CLASIFICACION_BRECHA="NUEVO_CAMPO_REQUERIDO", REQUERIMIENTO_HISTORICO="SI", DATO_SENSIBLE="NO", ID_DICCIONARIO="UP-37"),
    mu(POSICION_SIES="U", CAMPO_SIES="ASI_INS_ANT", NOMBRE_DESCRIPTIVO_SIES="Asignaturas Inscritas en el Año Anterior",
       DEFINICION_OFICIAL="Asignaturas inscritas en el último periodo (año). Considera aprobadas y reprobadas; no considera convalidadas u homologadas.",
       CODIGOS_SIES="0 a 99", FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí (pregrado nivel global 1)",
       REGLA_TEMPORAL="Año calendario anterior al proceso (2025 para MU 2026)", GRANULARIDAD="MATRÍCULA-AÑO",
       CAMPO_U_PLUS="Hoja1 (PROMEDIOSDEALUMNOS): CODRAMO, ANO, ESTADO/DESCRIPCION_ESTADO, CONVALIDADO",
       DEFINICION_U_PLUS="Detalle por asignatura (reporte U+ 7804).", VALORES_U_PLUS="ANO: 2 años; DESCRIPCION_ESTADO: APROBADO/REPROBADO/CONVALIDACION/HOMOLOGADO",
       MAPEO_U_PLUS_SIES="Contar CODRAMO distintos del año de referencia excluyendo convalidación/homologación/reconocimiento.",
       TIPO_OBTENCION="D", CAMPO_NUEVO_BETTERSOFT="ASIG_INSCRITAS_ANIO_REF", DEFINICION_CAMPO_BETTERSOFT="Ver UP-46",
       LOGICA_CALCULO="_build_mu_historico_summary: ASI_INS_ANT_HIST", LLAVE="RUT+DV+CODCARR (hoy); debe ser CODCLI",
       VALIDACION="0..99; >= ASI_APR_ANT; = 0 si ingreso año proceso con FOR 1,6-10.", EJEMPLO_ORIGEN="7 filas 2025 (5 aprob., 2 reprob.)", EJEMPLO_DESTINO="7",
       FUENTE_INSTITUCIONAL=S["PROM"], SCRIPT_O_EVIDENCIA=S["COD_MU"] + " (L669-754); " + S["GOB_MU"].replace("<campo>", "asi_ins_ant"),
       NIVEL_RESPALDO="Oficial (definición) + Implementado", ESTADO="Confirmado (lógica); cruce por RUT+CODCARR debe pasar a CODCLI",
       CLASIFICACION_BRECHA="EXISTE_PERO_REQUIERE_OTRA_GRANULARIDAD", REQUERIMIENTO_HISTORICO="SI (año de referencia parametrizable)", DATO_SENSIBLE="SI (rendimiento académico)", ID_DICCIONARIO="UP-46"),
    mu(POSICION_SIES="V", CAMPO_SIES="ASI_APR_ANT", NOMBRE_DESCRIPTIVO_SIES="Asignaturas Aprobadas en el Año Anterior",
       DEFINICION_OFICIAL="Asignaturas aprobadas en el último periodo (año); no considera convalidadas u homologadas.",
       CODIGOS_SIES="0 a 99", FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí (pregrado)", REGLA_TEMPORAL="Año anterior al proceso",
       GRANULARIDAD="MATRÍCULA-AÑO", CAMPO_U_PLUS="Hoja1: CODRAMO, ANO, DESCRIPCION_ESTADO", DEFINICION_U_PLUS="Detalle por asignatura.",
       VALORES_U_PLUS="APROBADO", MAPEO_U_PLUS_SIES="Contar CODRAMO distintos aprobados (sin convalidación) del año de referencia.",
       TIPO_OBTENCION="D", CAMPO_NUEVO_BETTERSOFT="ASIG_APROBADAS_ANIO_REF", DEFINICION_CAMPO_BETTERSOFT="Ver UP-47",
       LOGICA_CALCULO="ASI_APR_ANT_HIST", LLAVE="CODCLI", VALIDACION="0..99; <= ASI_INS_ANT.", EJEMPLO_ORIGEN="5 aprobadas", EJEMPLO_DESTINO="5",
       FUENTE_INSTITUCIONAL=S["PROM"], SCRIPT_O_EVIDENCIA=S["COD_MU"] + " (L669-754)", NIVEL_RESPALDO="Oficial + Implementado", ESTADO="Confirmado (lógica)",
       CLASIFICACION_BRECHA="EXISTE_PERO_REQUIERE_OTRA_GRANULARIDAD", REQUERIMIENTO_HISTORICO="SI", DATO_SENSIBLE="SI (rendimiento académico)", ID_DICCIONARIO="UP-47"),
    mu(POSICION_SIES="W", CAMPO_SIES="PROM_PRI_SEM", NOMBRE_DESCRIPTIVO_SIES="Nota Promedio Primer Semestre Año Anterior",
       DEFINICION_OFICIAL="Promedio de notas de asignaturas cursadas en el primer semestre del año anterior. Información utilizada por Junaeb.",
       CODIGOS_SIES="100 a 700 y 0", FORMATO_SIES="Solo números (nota x 100)", OBLIGATORIEDAD="Sí (pregrado)", REGLA_TEMPORAL="1er semestre del año anterior",
       GRANULARIDAD="MATRÍCULA-SEMESTRE", CAMPO_U_PLUS="Hoja1: NOTA_FINAL, ANO, PERIODO", DEFINICION_U_PLUS="Nota final por asignatura escala 1.0-7.0; PERIODO 1/2/3.",
       VALORES_U_PLUS="NOTA_FINAL 1.0-7.0 (70 valores)", MAPEO_U_PLUS_SIES="Promedio de notas calificadas del semestre 1 (sin convalidadas) x 100; 0 si no cursó.",
       TIPO_OBTENCION="D", CAMPO_NUEVO_BETTERSOFT="PROM_NOTAS_SEM1_ANIO_REF", DEFINICION_CAMPO_BETTERSOFT="Ver UP-48",
       LOGICA_CALCULO="_normalize_grade_to_mu_scale + _coerce_mu_average", LLAVE="CODCLI", VALIDACION="0 o 100..700.",
       EJEMPLO_ORIGEN="5,8 / 6,2", EJEMPLO_DESTINO="600", FUENTE_INSTITUCIONAL=S["PROM"],
       SCRIPT_O_EVIDENCIA=S["GOB_NOTAS"] + "; " + S["COD_MU"] + " (L645-666)", NIVEL_RESPALDO="Oficial + Interno (escala) + Implementado",
       ESTADO="Confirmado (lógica)", OBSERVACIONES="PERIODO 3 de Hoja1 se trata como 2º semestre (regla institucional; CT-09).",
       CLASIFICACION_BRECHA="EXISTE_PERO_REQUIERE_OTRA_GRANULARIDAD", REQUERIMIENTO_HISTORICO="SI", DATO_SENSIBLE="SI (rendimiento académico)", ID_DICCIONARIO="UP-48"),
    mu(POSICION_SIES="X", CAMPO_SIES="PROM_SEG_SEM", NOMBRE_DESCRIPTIVO_SIES="Nota Promedio Segundo Semestre Año Anterior",
       DEFINICION_OFICIAL="Promedio de notas de asignaturas cursadas en el segundo semestre del año anterior.", CODIGOS_SIES="100 a 700 y 0",
       FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí (pregrado)", REGLA_TEMPORAL="2º semestre del año anterior", GRANULARIDAD="MATRÍCULA-SEMESTRE",
       CAMPO_U_PLUS="Hoja1: NOTA_FINAL, ANO, PERIODO", DEFINICION_U_PLUS="Igual a PROM_PRI_SEM.", VALORES_U_PLUS="-",
       MAPEO_U_PLUS_SIES="Promedio semestre 2 (PERIODO 2 y 3) x 100.", TIPO_OBTENCION="D", CAMPO_NUEVO_BETTERSOFT="PROM_NOTAS_SEM2_ANIO_REF",
       DEFINICION_CAMPO_BETTERSOFT="Ver UP-49", LOGICA_CALCULO="Igual a W.", LLAVE="CODCLI", VALIDACION="0 o 100..700.",
       EJEMPLO_ORIGEN="6,0 / 6,6", EJEMPLO_DESTINO="630", FUENTE_INSTITUCIONAL=S["PROM"], SCRIPT_O_EVIDENCIA=S["COD_MU"] + " (L645-666)",
       NIVEL_RESPALDO="Oficial + Implementado", ESTADO="Confirmado (lógica)",
       CLASIFICACION_BRECHA="EXISTE_PERO_REQUIERE_OTRA_GRANULARIDAD", REQUERIMIENTO_HISTORICO="SI", DATO_SENSIBLE="SI (rendimiento académico)", ID_DICCIONARIO="UP-49"),
    mu(POSICION_SIES="Y", CAMPO_SIES="ASI_INS_HIS", NOMBRE_DESCRIPTIVO_SIES="Asignaturas Inscritas Históricas",
       DEFINICION_OFICIAL="Asignaturas inscritas desde el inicio de la carrera (aprobadas y reprobadas; reprobadas cuentan cada vez). Incorpora convalidadas u homologadas de la carrera actual.",
       CODIGOS_SIES="0 a 200", FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí (pregrado)", REGLA_TEMPORAL="Acumulado desde el inicio de la carrera hasta el cierre del año anterior",
       GRANULARIDAD="MATRÍCULA (acumulado)", CAMPO_U_PLUS="Hoja1: CODRAMO (todas las filas)", DEFINICION_U_PLUS="Detalle por asignatura.",
       VALORES_U_PLUS="Hoja1 contiene solo 2 años (ANO: 2 valores) => alcance histórico limitado",
       MAPEO_U_PLUS_SIES="Conteo de filas CODRAMO (inscripciones) del historial disponible.", TIPO_OBTENCION="D",
       CAMPO_NUEVO_BETTERSOFT="ASIG_INSCRITAS_HISTORICAS", DEFINICION_CAMPO_BETTERSOFT="Ver UP-50", LOGICA_CALCULO="ASI_INS_HIS_HIST",
       LLAVE="CODCLI", VALIDACION="0..200; >= ASI_APR_HIS; FOR 2 o 3 => > 0.", EJEMPLO_ORIGEN="28 inscripciones", EJEMPLO_DESTINO="28",
       FUENTE_INSTITUCIONAL=S["PROM"], SCRIPT_O_EVIDENCIA=S["COD_MU"] + " (L669-754); " + S["GOB_MU"].replace("<campo>", "asi_ins_his"),
       NIVEL_RESPALDO="Oficial + Implementado", ESTADO="PENDIENTE_DEMOSTRAR (historial incompleto en la fuente)",
       OBSERVACIONES="El reporte Hoja1 no cubre toda la carrera: el acumulado real requiere el historial completo en U+.",
       CLASIFICACION_BRECHA="EXISTE_PERO_REQUIERE_HISTORIZACION", REQUERIMIENTO_HISTORICO="SI", DATO_SENSIBLE="SI (rendimiento académico)", ID_DICCIONARIO="UP-50"),
    mu(POSICION_SIES="Z", CAMPO_SIES="ASI_APR_HIS", NOMBRE_DESCRIPTIVO_SIES="Asignaturas Aprobadas Históricas",
       DEFINICION_OFICIAL="Asignaturas aprobadas desde el inicio de la carrera. Incorpora convalidadas u homologadas de la carrera actual.",
       CODIGOS_SIES="0 a 200", FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí (pregrado)", REGLA_TEMPORAL="Acumulado hasta cierre año anterior",
       GRANULARIDAD="MATRÍCULA (acumulado)", CAMPO_U_PLUS="Hoja1: CODRAMO, DESCRIPCION_ESTADO", DEFINICION_U_PLUS="Detalle por asignatura.",
       VALORES_U_PLUS="APROBADO / CONVALIDACION / HOMOLOGADO", MAPEO_U_PLUS_SIES="CODRAMO distintos aprobados o reconocidos.", TIPO_OBTENCION="D",
       CAMPO_NUEVO_BETTERSOFT="ASIG_APROBADAS_HISTORICAS", DEFINICION_CAMPO_BETTERSOFT="Ver UP-51", LOGICA_CALCULO="ASI_APR_HIS_HIST",
       LLAVE="CODCLI", VALIDACION="0..200; <= ASI_INS_HIS.", EJEMPLO_ORIGEN="24 aprobadas", EJEMPLO_DESTINO="24", FUENTE_INSTITUCIONAL=S["PROM"],
       SCRIPT_O_EVIDENCIA=S["COD_MU"] + " (L669-754)", NIVEL_RESPALDO="Oficial + Implementado", ESTADO="PENDIENTE_DEMOSTRAR (historial incompleto)",
       CLASIFICACION_BRECHA="EXISTE_PERO_REQUIERE_HISTORIZACION", REQUERIMIENTO_HISTORICO="SI", DATO_SENSIBLE="SI (rendimiento académico)", ID_DICCIONARIO="UP-51"),
    mu(POSICION_SIES="AA", CAMPO_SIES="NIV_ACA", NOMBRE_DESCRIPTIVO_SIES="Nivel Académico",
       DEFINICION_OFICIAL="Semestre curricular que el matriculado se encuentra cursando: ubicación en la malla de la mayoría de las asignaturas que cursa.",
       CODIGOS_SIES="1 a duración de la carrera", FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí (pregrado)",
       REGLA_TEMPORAL="Nivel al período informado (1er semestre del año de proceso)", GRANULARIDAD="MATRÍCULA-PERÍODO", CAMPO_U_PLUS="NIVEL",
       DEFINICION_U_PLUS="Nivel administrativo U+ (en programas trimestrales está expresado en trimestres); valor 20 sin significado documentado.",
       VALORES_U_PLUS="1: 6.427; 2: 2.137; 5: 2.244; ...; 20: 425 (99,6% poblado)",
       MAPEO_U_PLUS_SIES="20 -> 8; si régimen trimestral: 1->1,2->2,3->2,4->3,5->4,6->4,7->5,8->6,9->6,10->7,11->8,12->8; acotar a duración y a 2 si cohorte 2026",
       TIPO_OBTENCION="D", CAMPO_NUEVO_BETTERSOFT="NIVEL_ACADEMICO_UPLUS + REGIMEN_PLAN + NIVEL_SEMESTRE_SIES", DEFINICION_CAMPO_BETTERSOFT="Ver UP-30 / UP-41",
       LOGICA_CALCULO="_trimester_level_to_semester; normalización 20->8", LLAVE="CODCLI + período",
       VALIDACION="<= DURACION_ESTUDIOS; <= 2 si ingreso año proceso con FOR 1,6-10 o ANIO_ING_ORI = año proceso.",
       EJEMPLO_ORIGEN="NIVEL=5 (régimen trimestral)", EJEMPLO_DESTINO="4", FUENTE_INSTITUCIONAL=S["DA"] + "; " + S["PROM"] + " (REGIMEN)",
       SCRIPT_O_EVIDENCIA=S["COD_MU"] + " (L625-642, L4123-4155); " + S["GOB_NIV"], NIVEL_RESPALDO="Oficial (regla) + Implementado + Decisión interna",
       ESTADO="PENDIENTE_DEMOSTRAR (significado de NIVEL=20 y regla trimestral sin documento oficial)",
       CLASIFICACION_BRECHA="EXISTE_PERO_REQUIERE_HISTORIZACION", REQUERIMIENTO_HISTORICO="SI (nivel a fecha de corte)", DATO_SENSIBLE="NO", ID_DICCIONARIO="UP-30; UP-41"),
    mu(POSICION_SIES="AB", CAMPO_SIES="SIT_FON_SOL", NOMBRE_DESCRIPTIVO_SIES="Situación Fondo Solidario",
       DEFINICION_OFICIAL="Indica si el estudiante mantiene o no la situación socioeconómica con la que obtuvo FSCU.",
       CODIGOS_SIES="0 No cumple / No aplica; 1 Sí cumple; 2 No presenta documentación", FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí (pregrado)",
       REGLA_TEMPORAL="Año de proceso", GRANULARIDAD="PERSONA-AÑO", CAMPO_U_PLUS="(no aplica)", DEFINICION_U_PLUS="-", VALORES_U_PLUS="-",
       MAPEO_U_PLUS_SIES="Enviados 2022-2026: 0 en el 100% de las filas.", TIPO_OBTENCION="F", CAMPO_NUEVO_BETTERSOFT="(no solicitar)",
       DEFINICION_CAMPO_BETTERSOFT="ORIGEN_NO_U_PLUS", LOGICA_CALCULO="Constante 0 (No aplica) observada.", LLAVE="-",
       VALIDACION="Cuadro N°6: 'no corresponde para el TIPO INSTITUCIÓN'.", EJEMPLO_ORIGEN="-", EJEMPLO_DESTINO="0",
       FUENTE_INSTITUCIONAL="-", SCRIPT_O_EVIDENCIA=S["BASE_RET"] + "; " + S["COD_MU"] + " (L4157 asigna 1: ver CT-10)",
       NIVEL_RESPALDO="Observado + Oficial (mensaje de error)", ESTADO="No aplica (U+)",
       OBSERVACIONES="FSCU es de universidades del CRUCH; para un IP se informa 0 según lo observado. El código asigna 1 y el archivo PES_READY corrige a 0 (CT-10).",
       CLASIFICACION_BRECHA="FUENTE_EXTERNA", REQUERIMIENTO_HISTORICO="NO", DATO_SENSIBLE="SI (socioeconómico)", ID_DICCIONARIO="-"),
    mu(POSICION_SIES="AC", CAMPO_SIES="SUS_PRE", NOMBRE_DESCRIPTIVO_SIES="Suspensiones Previas",
       DEFINICION_OFICIAL="Número de semestres de suspensiones que tiene el matriculado previo al año actual.", CODIGOS_SIES="0 a 99",
       FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí (pregrado)", REGLA_TEMPORAL="Acumulado previo al año de proceso",
       GRANULARIDAD="MATRÍCULA (historial)", CAMPO_U_PLUS="SITUACION ('2 - SUSPENSIÓN TEMPORAL') - solo estado actual",
       DEFINICION_U_PLUS="U+ muestra la situación vigente, no el historial de suspensiones.", VALORES_U_PLUS="SUSPENDIDO: 185 filas (estado actual)",
       MAPEO_U_PLUS_SIES="Pipeline asigna constante 0. Enviados: 0 en 100% desde 2024 (2022-2023 sí hubo valores > 0).", TIPO_OBTENCION="E",
       CAMPO_NUEVO_BETTERSOFT="SEMESTRES_SUSPENDIDOS_PREVIOS", DEFINICION_CAMPO_BETTERSOFT="Ver UP-44",
       LOGICA_CALCULO="Contar semestres con suspensión registrada antes del año de proceso (requiere historial de situaciones).", LLAVE="CODCLI",
       VALIDACION="0..99; <= semestres entre ANIO_ING_ACT y año actual; 0 si ANIO_ING_ACT = año proceso.", EJEMPLO_ORIGEN="Suspensión 2º sem 2024", EJEMPLO_DESTINO="1",
       FUENTE_INSTITUCIONAL=S["DA"], SCRIPT_O_EVIDENCIA=S["COD_MU"] + " (L4158); " + S["BASE_RET"], NIVEL_RESPALDO="Oficial + Implementado (constante)",
       ESTADO="PENDIENTE_DEMOSTRAR", CLASIFICACION_BRECHA="EXISTE_PERO_REQUIERE_HISTORIZACION", REQUERIMIENTO_HISTORICO="SI",
       DATO_SENSIBLE="NO", ID_DICCIONARIO="UP-44"),
    mu(POSICION_SIES="AD", CAMPO_SIES="FECHA_MATRICULA", NOMBRE_DESCRIPTIVO_SIES="Fecha de Matrícula",
       DEFINICION_OFICIAL="Fecha en que el estudiante ha sido inscrito en la matrícula de la institución. Solo aplica a cohorte 2026 (año de origen = 2026); si no, 01/01/1900.",
       CODIGOS_SIES="dd/mm/aaaa; 01/01/1900 si no se cuenta con el dato", FORMATO_SIES="dd/mm/aaaa; no posterior a la fecha de carga", OBLIGATORIEDAD="Sí",
       REGLA_TEMPORAL="Fecha de la matrícula del año de proceso (cohorte 2026)", GRANULARIDAD="MATRÍCULA-PERÍODO", CAMPO_U_PLUS="FECHAMATRICULA",
       DEFINICION_U_PLUS="Fecha de matrícula U+ (dd-mm-aaaa). Su año coincide con ANOMATRICULA solo en 76,3%: temporalidad no documentada.",
       VALORES_U_PLUS="100% poblado; 2.388 fechas distintas", MAPEO_U_PLUS_SIES="dd-mm-aaaa -> dd/mm/aaaa si ANIO_ING_ORI = año proceso; si no 01/01/1900.",
       TIPO_OBTENCION="D", CAMPO_NUEVO_BETTERSOFT="FECHA_MATRICULA_PERIODO", DEFINICION_CAMPO_BETTERSOFT="Ver UP-39",
       LOGICA_CALCULO="config_vig_fecha.json (FECHA_MATRICULA)", LLAVE="CODCLI + año/período", VALIDACION="No futura; formato; 1900 si no cohorte.",
       EJEMPLO_ORIGEN="26-01-2026", EJEMPLO_DESTINO="26/01/2026", FUENTE_INSTITUCIONAL=S["DA"],
       SCRIPT_O_EVIDENCIA=S["CFG_VIG"] + "; " + S["BASE_RET"] + " (2026: 2.082 con 01/01/1900)", NIVEL_RESPALDO="Oficial + Implementado",
       ESTADO="Confirmado (regla); PENDIENTE definición temporal de FECHAMATRICULA U+",
       OBSERVACIONES="Campo inexistente en archivos enviados 2022-2023.", CLASIFICACION_BRECHA="EXISTE_PERO_REQUIERE_HISTORIZACION",
       REQUERIMIENTO_HISTORICO="SI (fecha por año/período)", DATO_SENSIBLE="NO", ID_DICCIONARIO="UP-39"),
    mu(POSICION_SIES="AE", CAMPO_SIES="REINCORPORACION", NOMBRE_DESCRIPTIVO_SIES="Reincorporación",
       DEFINICION_OFICIAL="Indica si el estudiante se reincorpora a su carrera en 2º semestre luego de suspender el 1er semestre. Solo puede informarse 1 en la última carga del período.",
       CODIGOS_SIES="0 No se reincorpora / No aplica; 1 Sí se reincorpora", FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí",
       REGLA_TEMPORAL="Última carga del período (2º semestre)", GRANULARIDAD="MATRÍCULA-PERÍODO",
       CAMPO_U_PLUS="SITUACION ('38 - REINCORPORACION DE ACTIVIDADES')", DEFINICION_U_PLUS="Situación vigente; no indica semestre de la suspensión previa.",
       VALORES_U_PLUS="38 - REINCORPORACION DE ACTIVIDADES: 164 filas", MAPEO_U_PLUS_SIES="Pipeline: constante 0 (gobernanza documenta derivación desde SITUACION 38 como secundaria).",
       TIPO_OBTENCION="E", CAMPO_NUEVO_BETTERSOFT="REINCORPORACION_2DO_SEM", DEFINICION_CAMPO_BETTERSOFT="Ver UP-45",
       LOGICA_CALCULO="1 si existe suspensión informada en 1er semestre del año y reincorporación en 2º semestre del mismo año.", LLAVE="CODCLI + año",
       VALIDACION="Solo en última carga programada; 0/1.", EJEMPLO_ORIGEN="Suspensión 1S-2026 + reincorporación 2S-2026", EJEMPLO_DESTINO="1",
       FUENTE_INSTITUCIONAL=S["DA"], SCRIPT_O_EVIDENCIA=S["GOB_MU"].replace("<campo>", "reincorporacion") + "; " + S["COD_MU"] + " (L4159)",
       NIVEL_RESPALDO="Oficial + Implementado (constante)", ESTADO="PENDIENTE_DEMOSTRAR",
       OBSERVACIONES="Campo inexistente en enviados 2022-2023; 0 en 100% 2024-2026.", CLASIFICACION_BRECHA="EXISTE_PERO_REQUIERE_HISTORIZACION",
       REQUERIMIENTO_HISTORICO="SI", DATO_SENSIBLE="NO", ID_DICCIONARIO="UP-45"),
    mu(POSICION_SIES="AF", CAMPO_SIES="VIG", NOMBRE_DESCRIPTIVO_SIES="Vigencia",
       DEFINICION_OFICIAL="Estado de la vigencia de la matrícula informada, de acuerdo con la reglamentación interna de cada institución.",
       CODIGOS_SIES="0 Estudiante sin matrícula; 1 Estudiante con matrícula vigente; 2 Estudiante egresado con matrícula vigente",
       FORMATO_SIES="Solo números", OBLIGATORIEDAD="Sí", REGLA_TEMPORAL="Estado de la matrícula a la fecha de la carga (corte SIES 30-abr para estadística)",
       GRANULARIDAD="MATRÍCULA-PERÍODO", CAMPO_U_PLUS="ESTADOACADEMICO + SITUACION",
       DEFINICION_U_PLUS="Estado académico y situación vigentes al momento de la descarga (sin fecha de vigencia).",
       VALORES_U_PLUS="ESTADOACADEMICO: ELIMINADO 6.617; VIGENTE 4.682; TITULADO 3.014; SUSPENDIDO 185; EGRESADO 146. SITUACION: 25 códigos",
       MAPEO_U_PLUS_SIES="Dos tablas internas en conflicto: VIGENTE->1; EGRESADO->2; ELIMINADO/SUSPENDIDO->0; TITULADO->2 (gob_datosalumnos...) o ->0 (config_vig_fecha.json)",
       TIPO_OBTENCION="D", CAMPO_NUEVO_BETTERSOFT="ESTADO_ACADEMICO + SITUACION (código y descripción) + FECHA_INICIO_SITUACION",
       DEFINICION_CAMPO_BETTERSOFT="Ver UP-42 / UP-43", LOGICA_CALCULO="Tabla de homologación institucional aprobada (pendiente) aplicada al estado vigente a la fecha de corte.",
       LLAVE="CODCLI + fecha de corte", VALIDACION="0/1/2; VIG=0 => PROM y ASI_*_HIS en 0 (regla QA interna).",
       EJEMPLO_ORIGEN="VIGENTE / 1 - ALUMNO REGULAR", EJEMPLO_DESTINO="1",
       FUENTE_INSTITUCIONAL=S["DA"], SCRIPT_O_EVIDENCIA=S["GOB_VIG"] + "; " + S["CFG_VIG"] + "; " + S["BASE_RET"],
       NIVEL_RESPALDO="Oficial (códigos) + Decisión interna (en conflicto)", ESTADO="PENDIENTE_DEMOSTRAR (CT-01)",
       OBSERVACIONES="No crear equivalencia universal de VIGENCIA (difiere de AC, Extranjeros y Oferta). Enviados 2026: 1=3.145; 0=960; 2=0.",
       CLASIFICACION_BRECHA="EXISTE_PERO_REQUIERE_HISTORIZACION", REQUERIMIENTO_HISTORICO="SI (estado a fecha)", DATO_SENSIBLE="NO", ID_DICCIONARIO="UP-42; UP-43"),
]

# ---------------------------------------------------------------------------
# MU POSGRADO Y POSTÍTULO (Cuadro N°2, 21 campos): A-T iguales + U VIG
# ---------------------------------------------------------------------------
MU_POS_ROWS = []
for r in MU_ROWS[:20]:
    r2 = dict(r)
    r2["SUBPROCESO"] = "Posgrado y Postítulo (Cuadro N°2)"
    r2["AÑO_DATOS"] = "2026 (corte SIES 15-may-2026)"
    r2["ARCHIVO_DESTINO"] = "matricula_unificada_2026_postgrado_postitulo.csv (21 columnas) - " + S["FINAL_MU_POS"]
    r2["FUENTE_OFICIAL"] = S["MAN_MU_C2"]
    if r2["CAMPO_SIES"] == "SEM_ING_ORI":
        r2["CODIGOS_SIES"] = "1 a 2 (Cuadro N°2 no lista 0)"
        r2["OBSERVACIONES"] = "Diferencia con pregrado: Cuadro N°2 no contempla 0; revisar compatibilidad con ANIO_ING_ORI=1900."
    r2["OBSERVACIONES"] = (r2["OBSERVACIONES"] + " | Mismo origen U+ que pregrado; universo: CATEGORIA 'DIPLOMADO' y programas nivel global 2/3.").strip(" |")
    MU_POS_ROWS.append(r2)
_vig = dict(MU_ROWS[-1])
_vig.update(SUBPROCESO="Posgrado y Postítulo (Cuadro N°2)", POSICION_SIES="U", AÑO_DATOS="2026 (corte 15-may-2026)",
            ARCHIVO_DESTINO="matricula_unificada_2026_postgrado_postitulo.csv - " + S["FINAL_MU_POS"], FUENTE_OFICIAL=S["MAN_MU_C2"])
MU_POS_ROWS.append(_vig)

# ---------------------------------------------------------------------------
# AVANCE CURRICULAR SIES 2026
# ---------------------------------------------------------------------------
AC_BASE = dict(PROCESO="Avance Curricular", AÑO_PROCESO="2026",
               AÑO_DATOS="2025 (1er sem, 2º sem, anual 2025 y acumulado al cierre 2025; universo matrícula al 30-abr-2025)",
               FUENTE_OFICIAL="Instructivo_Avance Curricular SIES - 2026.txt (" + S["AC_NORM"] + ")")

AC_CAR = [
    ("1", "CODIGO_UNICO", "Código único SIES de la carrera", "Identificador único de la carrera o programa informado por SIES.", "Código único SIES", "G", "NO", "PRECARGADO_SIES"),
    ("2", "PLAN_ESTUDIOS", "Plan de estudios", "Correlativo del plan de estudios vigente; precargado con 1 y modificable cuando existan planes vigentes distintos (puede duplicar la carrera).", "Correlativo por CODIGO_UNICO", "E", "SI", "NUEVO_CAMPO_REQUERIDO"),
    ("3", "NOMBRE_SEDE", "Nombre de sede", "Sede en que se imparte la carrera.", "Dato precargado", "G", "NO", "PRECARGADO_SIES"),
    ("4", "NOMBRE_CARRERA", "Nombre de carrera", "Nombre completo de la carrera.", "Dato precargado", "G", "NO", "PRECARGADO_SIES"),
    ("5", "JORNADA", "Jornada", "Jornada en que se imparte.", "1 Diurna; 2 Vespertina; 3 Semipresencial; 4 A Distancia; 5 Otra", "G", "NO", "PRECARGADO_SIES"),
    ("6", "VERSION", "Versión", "Número de versión del programa.", "Dato precargado", "G", "NO", "PRECARGADO_SIES"),
    ("7", "DURACION_ESTUDIOS", "Duración de estudios", "Duración del plan en semestres sin titulación fuera de plan.", "Semestres", "G", "NO", "PRECARGADO_SIES"),
    ("8", "DURACION_TITULACION", "Duración titulación", "Duración normal estimada del proceso de titulación.", "Semestres", "G", "NO", "PRECARGADO_SIES"),
    ("9", "DURACION_TOTAL", "Duración total", "Duración teórica total hasta título o grado terminal.", "Semestres", "G", "NO", "PRECARGADO_SIES"),
    ("10", "NIVEL_CARRERA", "Nivel de carrera", "Nivel específico de los estudios.", "0 Bachillerato/Plan común; 1 TNS; 2 Profesional sin licenciatura; 3 Licenciatura no conducente; 4 Profesional con licenciatura", "G", "NO", "PRECARGADO_SIES"),
    ("11", "TIPO_UNIDAD_MEDIDA", "Tipo de unidad de medida", "Unidad usada para cuantificar el avance curricular.", "1 Asignaturas/cursos/módulos; 2 Créditos o SCT-Chile; 3 Otra", "E", "SI", "NUEVO_CAMPO_REQUERIDO"),
    ("12", "OTRA_UNIDAD_MEDIDA", "Otra unidad de medida", "Nombre de la unidad cuando TIPO_UNIDAD_MEDIDA = 3.", "Texto (solo si tipo 3)", "E", "SI", "NUEVO_CAMPO_REQUERIDO"),
    ("13", "TOTAL_UNIDADES_MEDIDA", "Total unidades del plan", "Total de unidades que componen el plan de estudios.", "Entero; obligatorio", "E", "SI", "NUEVO_CAMPO_REQUERIDO"),
] + [
    (str(13 + i), f"UNIDADES_{n}_ANIO", f"Unidades {n} año", f"Total de unidades que componen el {txt} año del plan.", "Entero", "E", "SI", "NUEVO_CAMPO_REQUERIDO")
    for i, (n, txt) in enumerate([("1ER", "primer"), ("2DO", "segundo"), ("3ER", "tercer"), ("4TO", "cuarto"), ("5TO", "quinto"), ("6TO", "sexto"), ("7MO", "séptimo")], start=1)
] + [
    ("21", "VIGENCIA", "Vigencia (Carreras AC)", "Variable para mantener o eliminar un registro cargado en este proceso.", "0 Eliminar registro; 1 Mantener registro", "D", "SI", "PENDIENTE_DEMOSTRAR"),
]

AC_ROWS = []
for pos, campo, nom, defi, cod, tipo, modif, brecha in AC_CAR:
    es_plan_unidades = campo.startswith("UNIDADES_") or campo in {"TIPO_UNIDAD_MEDIDA", "OTRA_UNIDAD_MEDIDA", "TOTAL_UNIDADES_MEDIDA"}
    AC_ROWS.append(fila(**AC_BASE, SUBPROCESO="Carreras Avance Curricular 2026 (ID carga 16769)",
        ARCHIVO_DESTINO="Carreras AC 2026 (CSV sin encabezado, sin columna CODIGO_IES_NUM) - carpeta 112d_cierre_gobernado_carga_aceptada_carreras_16769 (archivo no versionado)",
        POSICION_SIES=pos, CAMPO_SIES=campo, NOMBRE_DESCRIPTIVO_SIES=nom, DEFINICION_OFICIAL=defi, CODIGOS_SIES=cod,
        FORMATO_SIES="Según Anexo I", OBLIGATORIEDAD="Sí" if campo != "OTRA_UNIDAD_MEDIDA" else "Condicional (tipo 3)",
        REGLA_TEMPORAL="Plan vigente 2025", GRANULARIDAD="PLAN DE ESTUDIOS / OFERTA",
        CAMPO_U_PLUS=("Hoja1 PLAN_DE_ESTUDIO (código de plan)" if campo == "PLAN_ESTUDIOS" else ("(no expuesto) - malla/plan en U+" if es_plan_unidades else "(precarga PES)")),
        DEFINICION_U_PLUS=("Código de plan U+ (p.ej. 'IINF20241'), solo en reporte de notas" if campo == "PLAN_ESTUDIOS" else ("Estructura del plan (asignaturas/créditos por nivel) no expuesta en reportes U+ revisados" if es_plan_unidades else "No proviene de U+")),
        VALORES_U_PLUS="-", MAPEO_U_PLUS_SIES=("Correlativo por CODIGO_UNICO según planes vigentes (Listado_Planes_estudio_Sedes_RE_CO_20260701)" if campo == "PLAN_ESTUDIOS" else ("Desde mallas (04_gobernanza_mallas)" if es_plan_unidades else "Conservar precarga")),
        TIPO_OBTENCION=tipo, CAMPO_NUEVO_BETTERSOFT=("CATALOGO_PLANES: ver UP-28, UP-29, UP-58" if (es_plan_unidades or campo == "PLAN_ESTUDIOS") else "(no solicitar)"),
        DEFINICION_CAMPO_BETTERSOFT=("Ver UP-58" if es_plan_unidades else ("Ver UP-29" if campo == "PLAN_ESTUDIOS" else "ORIGEN_NO_U_PLUS")),
        LOGICA_CALCULO=("Conteo de unidades del plan por año curricular" if es_plan_unidades else ""), LLAVE="CODIGO_UNICO + PLAN_ESTUDIOS",
        VALIDACION=("No editar atributos no modificables (Anexo IV)" if tipo == "G" else ("Tipo 3 => OTRA_UNIDAD_MEDIDA obligatoria; solo si tipo 3" if campo in {"TIPO_UNIDAD_MEDIDA", "OTRA_UNIDAD_MEDIDA"} else "Enteros >= 0")),
        EJEMPLO_ORIGEN="-", EJEMPLO_DESTINO="-",
        FUENTE_INSTITUCIONAL=("Precarga PES Carreras AC 2026" if tipo == "G" else f"{WT}/avance_curricular_2026/01_fuentes_institucionales/planes_estudio; 04_gobernanza_mallas"),
        SCRIPT_O_EVIDENCIA=S["AC_GOB"] + "carreras/", NIVEL_RESPALDO=("Oficial" if tipo == "G" else "Oficial (regla) / Pendiente (fuente)"),
        ESTADO=("Confirmado (precarga)" if tipo == "G" else "PENDIENTE_DEMOSTRAR (fuente de plan/malla)"),
        OBSERVACIONES=("VIGENCIA en AC significa mantener/eliminar registro: no es la VIG de MU." if campo == "VIGENCIA" else ""),
        CLASIFICACION_BRECHA=brecha, REQUERIMIENTO_HISTORICO=("SI (plan vigente por año)" if tipo != "G" else "NO"), DATO_SENSIBLE="NO",
        PRECARGADO_SIES=("SI" if tipo == "G" or campo in {"PLAN_ESTUDIOS", "VIGENCIA"} else "NO"), MODIFICABLE=modif,
        ID_DICCIONARIO=("UP-58" if es_plan_unidades else ("UP-29" if campo == "PLAN_ESTUDIOS" else "-"))))

AC_MAT = [
    ("1", "TIPO_DOCUMENTO", "R RUN; P Pasaporte", "UP-03; UP-04"), ("2", "NUM_DOCUMENTO", "Dato precargado", "UP-05"), ("3", "DV", "0-9 o K", "UP-06"),
    ("4", "PRIMER_APELLIDO", "Dato precargado", "UP-08"), ("5", "SEGUNDO_APELLIDO", "Dato precargado", "UP-09"), ("6", "NOMBRES", "Dato precargado", "UP-07"),
    ("7", "SEXO", "M Mujer; H Hombre; X No Binario", "UP-10; UP-11"), ("8", "FECHA_NACIMIENTO", "Dato precargado", "UP-13"),
    ("9", "CODIGO_UNICO", "Código único SIES", "UP-27"), ("11", "ANIO_INGRESO_CARRERA_ACTUAL", "Año calendario <= 2025", "UP-31"),
    ("12", "SEM_INGRESO_CARRERA_ACTUAL", "1 Primer semestre; 2 Segundo semestre", "UP-32"), ("13", "ANIO_INGRESO_CARRERA_ORIGEN", "Año calendario <= 2025", "UP-36"),
    ("14", "SEM_INGRESO_CARRERA_ORIGEN", "1 Primer semestre; 2 Segundo semestre", "UP-37"),
]
for pos, campo, cod, up in AC_MAT:
    AC_ROWS.append(fila(**AC_BASE, SUBPROCESO="Matrícula Avance Curricular 2026 (ID carga 16768)",
        ARCHIVO_DESTINO="5809_MATRICULA_AVANCE_CURRICULAR_2026 (22 col. con CODIGO_IES_NUM; 2.371 filas) - " + S["AC_READY"],
        POSICION_SIES=pos, CAMPO_SIES=campo, NOMBRE_DESCRIPTIVO_SIES=campo.replace("_", " ").title(),
        DEFINICION_OFICIAL="Campo precargado desde matrícula 2025 (Anexo II); no modificable.", CODIGOS_SIES=cod, FORMATO_SIES="Según precarga",
        OBLIGATORIEDAD="Sí", REGLA_TEMPORAL="Valor informado en Matrícula 2025", GRANULARIDAD="MATRÍCULA 2025",
        CAMPO_U_PLUS="(solo para cruce) RUT / CODCLI", DEFINICION_U_PLUS="U+ se usa para vincular la precarga con la matrícula U+, no para completar el campo.",
        VALORES_U_PLUS="-", MAPEO_U_PLUS_SIES="Conservar precarga PES.", TIPO_OBTENCION="G", CAMPO_NUEVO_BETTERSOFT="(no solicitar como dato AC; llave de cruce)",
        DEFINICION_CAMPO_BETTERSOFT="Mismo dato que MU 2025: " + up, LOGICA_CALCULO="-", LLAVE="documento + CODIGO_UNICO",
        VALIDACION="No modificar respecto de precarga.", EJEMPLO_ORIGEN="-", EJEMPLO_DESTINO="-", FUENTE_INSTITUCIONAL="Precarga PES Matrícula AC 2026",
        SCRIPT_O_EVIDENCIA=S["AC_GOB"] + "matricula/", NIVEL_RESPALDO="Oficial", ESTADO="Confirmado (precarga)",
        OBSERVACIONES=("SEXO en AC usa 'X' para No Binario (MU usa 'NB')." if campo == "SEXO" else ""),
        CLASIFICACION_BRECHA="PRECARGADO_SIES", REQUERIMIENTO_HISTORICO="SI (valor 2025)", DATO_SENSIBLE=("SI" if pos in {"1", "2", "3", "4", "5", "6", "7", "8"} else "NO"),
        PRECARGADO_SIES="SI", MODIFICABLE="NO", ID_DICCIONARIO=up))

AC_MAT_CALC = [
    ("10", "PLAN_ESTUDIOS", "Correlativo del plan de estudios vigente del estudiante; precargado 1, modificable.", "Correlativo por CODIGO_UNICO", "Hoja1 PLAN_DE_ESTUDIO", "Código de plan del estudiante en U+ (reporte de notas)", "Plan del estudiante -> correlativo del catálogo Carreras AC", "E", "UP-28; UP-29", "Plan de la matrícula 2025"),
    ("15", "CURSO_1ER_SEM", "Indica si cursó actividades académicas durante el primer semestre 2025.", "SI; NO", "Hoja1: ANO, PERIODO, ESTADO", "Filas de asignaturas por año/período", "SI si existen asignaturas cursadas en 2025 período 1", "D", "UP-52", "1er semestre 2025"),
    ("16", "CURSO_2DO_SEM", "Indica si cursó actividades académicas durante el segundo semestre 2025.", "SI; NO", "Hoja1: ANO, PERIODO, ESTADO", "Filas de asignaturas por año/período", "SI si existen asignaturas cursadas en 2025 período 2 (o 3)", "D", "UP-53", "2º semestre 2025"),
    ("17", "UNIDADES_CURSADAS", "Unidades cursadas efectivamente durante 2025 del plan informado; excluye validación o reconocimiento.", "Números", "Hoja1: CODRAMO, ANO, DESCRIPCION_ESTADO, CONVALIDADO", "Detalle por asignatura", "Conteo de asignaturas/unidades 2025 no convalidadas", "D", "UP-54", "Año 2025"),
    ("18", "UNIDADES_APROBADAS", "Unidades aprobadas efectivamente durante 2025; excluye validación o reconocimiento.", "Números", "Hoja1: CODRAMO, ANO, DESCRIPCION_ESTADO", "Detalle por asignatura", "Conteo aprobadas 2025 no convalidadas", "D", "UP-55", "Año 2025"),
    ("19", "UNID_CURSADAS_TOTAL", "Unidades cursadas desde el ingreso hasta el cierre 2025; puede incluir validación o reconocimiento.", "Números", "Hoja1 (historial)", "Detalle por asignatura (historial limitado)", "Conteo acumulado", "D", "UP-56", "Acumulado al 31-dic-2025"),
    ("20", "UNID_APROBADAS_TOTAL", "Unidades aprobadas desde el ingreso hasta el cierre 2025; límite = total del plan con tolerancia 25%.", "Números", "Hoja1 (historial)", "Detalle por asignatura", "Conteo acumulado aprobadas + reconocidas", "D", "UP-57", "Acumulado al 31-dic-2025"),
    ("21", "VIGENCIA", "Variable para mantener o eliminar un registro cargado en este proceso; todos los registros se consideran vigentes (1) aunque se hayan retirado después del 30-abr-2025.", "0 Eliminar registro; 1 Mantener registro", "(no aplica)", "No depende del estado académico actual", "1 por defecto; 0 solo con evidencia de que el registro no corresponde", "D", "-", "Universo 30-abr-2025"),
]
for pos, campo, defi, cod, cu, du, mapeo, tipo, up, temp in AC_MAT_CALC:
    AC_ROWS.append(fila(**AC_BASE, SUBPROCESO="Matrícula Avance Curricular 2026 (ID carga 16768)",
        ARCHIVO_DESTINO="5809_MATRICULA_AVANCE_CURRICULAR_2026 - " + S["AC_READY"], POSICION_SIES=pos, CAMPO_SIES=campo,
        NOMBRE_DESCRIPTIVO_SIES=campo.replace("_", " ").title(), DEFINICION_OFICIAL=defi, CODIGOS_SIES=cod, FORMATO_SIES="Según Anexo II",
        OBLIGATORIEDAD="Sí", REGLA_TEMPORAL=temp, GRANULARIDAD="MATRÍCULA-AÑO 2025", CAMPO_U_PLUS=cu, DEFINICION_U_PLUS=du,
        VALORES_U_PLUS="-", MAPEO_U_PLUS_SIES=mapeo, TIPO_OBTENCION=tipo, CAMPO_NUEVO_BETTERSOFT=("(no solicitar)" if up == "-" else up),
        DEFINICION_CAMPO_BETTERSOFT=("Ver " + up if up != "-" else "Decisión de carga"), LOGICA_CALCULO=mapeo,
        LLAVE="CODCLI (hoy RUT+CODCARR)", VALIDACION=("UNID_APROBADAS_TOTAL <= TOTAL_UNIDADES_MEDIDA x 1,25; aprobadas <= cursadas" if "UNID" in campo else "Dominio"),
        EJEMPLO_ORIGEN="-", EJEMPLO_DESTINO="-", FUENTE_INSTITUCIONAL=S["PROM"],
        SCRIPT_O_EVIDENCIA=S["AC_GOB"] + "matricula/; " + S["AC_CIERRE"],
        NIVEL_RESPALDO="Oficial (definición) + Implementado + Decisión interna (51 casos 'ELIMINADO_SIN_ASIGNATURAS' => NO/0)",
        ESTADO=("PENDIENTE_DEMOSTRAR" if campo in {"PLAN_ESTUDIOS", "VIGENCIA"} else "Confirmado (lógica aplicada 2.371 filas)"),
        OBSERVACIONES=("VIGENCIA AC <> VIG MU (ver catálogo VIGENCIA)." if campo == "VIGENCIA" else ""),
        CLASIFICACION_BRECHA=("NUEVO_CAMPO_REQUERIDO" if tipo == "E" else ("PENDIENTE_DEMOSTRAR" if campo == "VIGENCIA" else "EXISTE_PERO_REQUIERE_OTRA_GRANULARIDAD")),
        REQUERIMIENTO_HISTORICO="SI", DATO_SENSIBLE=("SI (rendimiento académico)" if "UNID" in campo else "NO"),
        PRECARGADO_SIES=("SI" if campo in {"PLAN_ESTUDIOS", "VIGENCIA"} else "NO"), MODIFICABLE="SI", ID_DICCIONARIO=up))
AC_ROWS.sort(key=lambda r: (r["SUBPROCESO"], int(r["POSICION_SIES"])))

# ---------------------------------------------------------------------------
# ESTUDIANTES EXTRANJEROS 2026
# ---------------------------------------------------------------------------
EXT_BASE = dict(PROCESO="Estudiantes Extranjeros", SUBPROCESO="Extranjeros Regulares 2026 (ID carga 16765)", AÑO_PROCESO="2026",
                AÑO_DATOS="2025 (matriculados o con actividad académica 01-ene a 31-dic-2025)",
                ARCHIVO_DESTINO="02_EXTRANJEROS_REGULARES_2025_PES_READY.csv (81 registros; archivo no presente en repo) - " + S["EXT_CIERRE"],
                FUENTE_OFICIAL="Instructivo_Estudiantes_Extranjeros_SIES_2026.txt (no presente) - reglas trazadas en " + S["EXT_REGLAS"] + "; estructura 20260602_97636_Estructura_Extranjeros_Regulares_2025.csv (orden en " + S["EXT_GOB"] + ")",
                FUENTE_INSTITUCIONAL="BASE EXTRANJEROS.xlsx (62 filas, congelada) + " + S["DA"] + " + precarga PES", SCRIPT_O_EVIDENCIA=S["EXT_GOB"] + "; " + S["EXT_SCRIPT"],
                PRECARGADO_SIES="PARCIAL (precarga PES usada como fuente)", MODIFICABLE="SI")
EXT_DEF = [
    ("1", "TIPO_DOCUMENTO", "R de RUT o P de Pasaporte", "Sí", "(no existe)", "E", "UP-03; UP-04", "NUEVO_CAMPO_REQUERIDO", "3 conflictos de tipo de documento en la base 62.", "PENDIENTE_DEMOSTRAR"),
    ("2", "NUM_DOCUMENTO", "Sin letras si R; no inicia en 0", "Sí", "RUT", "C", "UP-05", "YA_EXISTE_U_PLUS", "", "Confirmado"),
    ("3", "DV", "0-9/K si R; nulo si P", "Condicional", "RUT", "C", "UP-06", "YA_EXISTE_U_PLUS", "", "Confirmado"),
    ("4", "PRIMER_APELLIDO", "Sin espacios iniciales/finales/dobles", "Sí", "APELLIDO PATERNO", "C", "UP-08", "YA_EXISTE_U_PLUS", "", "Confirmado"),
    ("5", "SEGUNDO_APELLIDO", "Idem", "Condicional", "APELLIDO MATERNO", "C", "UP-09", "YA_EXISTE_U_PLUS", "", "Confirmado"),
    ("6", "NOMBRES", "Idem", "Sí", "NOMBRES", "C", "UP-07", "YA_EXISTE_U_PLUS", "", "Confirmado"),
    ("7", "SEXO", "M, H o NB (validación de script)", "Sí", "SEXO (M/F/S)", "B", "UP-10; UP-11", "EXISTE_PERO_REQUIERE_HOMOLOGACION", "F->M y M->H 'transformación institucional confirmada'; 12 pendientes sin equivalencia normativa.", "Confirmado M/F; PENDIENTE resto"),
    ("8", "FECHA_NACIMIENTO", "Entre 01/01/1900 y 30/06/2010", "Sí", "FECHANACIMIENTO", "C", "UP-13", "YA_EXISTE_U_PLUS", "", "Confirmado"),
    ("9", "NACIONALIDAD", "1-197; no puede ser 38 (Chile)", "Sí", "NACIONALIDAD (texto)", "B", "UP-14; UP-15", "EXISTE_PERO_REQUIERE_HOMOLOGACION", "No inferir nacionalidad desde RUT ni país de origen. 1 caso ambiguo.", "Confirmado (61/62)"),
    ("10", "TIPO_RESIDENCIA_ESTUDIANTE", "Códigos 1, 2, 3 (significado no presente en repositorio)", "Sí", "(no existe)", "E", "UP-17", "NUEVO_CAMPO_REQUERIDO", "62/62 pendientes en la gobernanza; no inferir desde dirección ni modalidad online.", "PENDIENTE_DEMOSTRAR"),
    ("11", "PAIS_ORIGEN", "1-197, no 38; obligatorio si residencia 2 o 3; vacío si 1", "Condicional", "(no existe)", "E", "UP-18", "NUEVO_CAMPO_REQUERIDO", "62/62 pendientes; no inferir desde nacionalidad.", "PENDIENTE_DEMOSTRAR"),
    ("12", "PAIS_ESTUDIOS_SECUNDARIOS", "1-197", "Sí", "(no existe)", "E", "UP-16", "NUEVO_CAMPO_REQUERIDO", "12 pendientes.", "PENDIENTE_DEMOSTRAR"),
    ("13", "CODIGO_UNICO", "Código oficial SIES de oferta 2025 o código temporal solicitado en el proceso", "Sí", "CODCARPR + JORNADA (vía puente)", "E", "UP-27", "NUEVO_CAMPO_REQUERIDO", "26 pendientes (empates de coincidencia múltiple).", "PENDIENTE_DEMOSTRAR"),
    ("14", "ANIO_INGRESO_CARRERA_ACTUAL", "Año", "Sí", "ANOINGRESO", "A", "UP-31", "YA_EXISTE_U_PLUS", "", "Confirmado"),
    ("15", "SEM_INGRESO_CARRERA_ACTUAL", "1/2", "Sí", "PERIODOINGRESO", "B", "UP-32", "EXISTE_PERO_REQUIERE_HOMOLOGACION", "", "Confirmado 1/2"),
    ("16", "ANIO_INGRESO_CARRERA_ORIGEN", "Año", "Sí", "(no existe)", "E", "UP-36", "NUEVO_CAMPO_REQUERIDO", "14 pendientes.", "PENDIENTE_DEMOSTRAR"),
    ("17", "SEM_INGRESO_CARRERA_ORIGEN", "1/2", "Sí", "(no existe)", "E", "UP-37", "NUEVO_CAMPO_REQUERIDO", "12 pendientes.", "PENDIENTE_DEMOSTRAR"),
    ("18", "NOMBRE_UNIVERSIDAD_ORIGEN", "Texto; se completa junto con PAIS_UNIVERSIDAD_ORIGEN", "Condicional", "NOMBREUNIVERSIDAD (texto libre, 9,3% poblado)", "E", "UP-38", "EXISTE_PERO_REQUIERE_HOMOLOGACION", "U+ tiene institución anterior en texto libre, sin país.", "PENDIENTE_DEMOSTRAR"),
    ("19", "PAIS_UNIVERSIDAD_ORIGEN", "1-197; en conjunto con el nombre", "Condicional", "(no existe)", "E", "UP-38", "NUEVO_CAMPO_REQUERIDO", "", "PENDIENTE_DEMOSTRAR"),
    ("20", "VIGENCIA", "0 y 1 (significado no presente en repositorio)", "Sí", "ESTADOACADEMICO/SITUACION 2025", "D", "UP-42; UP-43", "EXISTE_PERO_REQUIERE_HISTORIZACION", "Vigencia no se define desde matrícula 2026; requiere estado 2025. Resultado: 0=16; 1=65.", "PENDIENTE_DEMOSTRAR (definición)"),
]
EXT_ROWS = []
for pos, campo, cod, obl, cu, tipo, up, brecha, obs, estado in EXT_DEF:
    EXT_ROWS.append(fila(**EXT_BASE, POSICION_SIES=pos, CAMPO_SIES=campo, NOMBRE_DESCRIPTIVO_SIES=campo.replace("_", " ").title(),
        DEFINICION_OFICIAL="Ver regla trazada del instructivo (texto oficial no presente en repositorio).", CODIGOS_SIES=cod,
        FORMATO_SIES="CSV ';' UTF-8", OBLIGATORIEDAD=obl, REGLA_TEMPORAL="Año 2025", GRANULARIDAD=("PERSONA" if int(pos) <= 12 else "MATRÍCULA"),
        CAMPO_U_PLUS=cu, DEFINICION_U_PLUS="Ver perfil U+", VALORES_U_PLUS="-", MAPEO_U_PLUS_SIES=("Ver MU" if tipo in "ABC" else "Sin mapeo U+"),
        TIPO_OBTENCION=tipo, CAMPO_NUEVO_BETTERSOFT=up, DEFINICION_CAMPO_BETTERSOFT="Ver " + up, LOGICA_CALCULO="-", LLAVE="documento + CODCLI",
        VALIDACION=cod, EJEMPLO_ORIGEN="-", EJEMPLO_DESTINO="-", NIVEL_RESPALDO="Oficial (regla trazada) + Implementado", ESTADO=estado,
        OBSERVACIONES=obs, CLASIFICACION_BRECHA=brecha, REQUERIMIENTO_HISTORICO=("SI (2025)" if campo == "VIGENCIA" else "NO"),
        DATO_SENSIBLE=("SI" if int(pos) <= 12 else "NO"), ID_DICCIONARIO=up))

INTER_CAMPOS = ["TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV", "SEXO", "NACIONALIDAD", "TIPO_RESIDENCIA_ESTUDIANTE", "PAIS_ORIGEN",
                "TIPO_PROGRAMA_INTERCAMBIO", "ESP_TIPO_PROGRAMA_INTERCAMBIO", "EXISTE_CONVENIO", "NOMBRE_UNIVERSIDAD_ORIGEN",
                "PAIS_UNIVERSIDAD_ORIGEN", "COMUNA_PROGRAMA", "FECHA_INICIO_PROGRAMA", "FECHA_TERMINO_PROGRAMA", "JORNADA_INTERCAMBIO"]
INTER_COD = {
    "SEXO": "M Mujer; H Hombre; NB No Binario", "TIPO_PROGRAMA_INTERCAMBIO": "1 Programa de Intercambio; 2 Pasantías Médicas; 3 Cursos Especiales; 4 Otro",
    "EXISTE_CONVENIO": "1 Sí; 2 No; 0 Sin información", "JORNADA_INTERCAMBIO": "1 Diurno; 2 Vespertino; 3 Otro (catálogo distinto al de Oferta)",
    "NACIONALIDAD": "1-197, no 38", "PAIS_ORIGEN": "No 38; obligatorio si residencia 2", "TIPO_DOCUMENTO": "R/P", "DV": "0-9/K si R; nulo si P",
    "COMUNA_PROGRAMA": "Comuna válida en mayúscula", "FECHA_TERMINO_PROGRAMA": ">= FECHA_INICIO_PROGRAMA", "FECHA_INICIO_PROGRAMA": "No posterior a 2025",
    "ESP_TIPO_PROGRAMA_INTERCAMBIO": "Obligatorio si tipo 4",
}
INTER_ROWS = [fila(PROCESO="Estudiantes Extranjeros", SUBPROCESO="Extranjeros de Intercambio 2026 (ID carga 16764)", AÑO_PROCESO="2026", AÑO_DATOS="2025",
                   ARCHIVO_DESTINO="Sin archivo (SIN_FUENTE_LOCAL)", POSICION_SIES="NO_DETERMINADA", CAMPO_SIES=c, NOMBRE_DESCRIPTIVO_SIES=c.replace("_", " ").title(),
                   DEFINICION_OFICIAL="Solo regla de validación trazada; estructura completa no presente.", CODIGOS_SIES=INTER_COD.get(c, "-"),
                   FORMATO_SIES="-", OBLIGATORIEDAD="Según instructivo (no presente)", REGLA_TEMPORAL="Programa de corta duración 2025", GRANULARIDAD="PERSONA-PROGRAMA",
                   CAMPO_U_PLUS="(no existe; estudiantes de intercambio no demostrados en U+)", DEFINICION_U_PLUS="-", VALORES_U_PLUS="-", MAPEO_U_PLUS_SIES="-",
                   TIPO_OBTENCION=("F" if c not in {"TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV", "SEXO", "NACIONALIDAD"} else "H"),
                   CAMPO_NUEVO_BETTERSOFT="(no solicitar hasta confirmar universo)", DEFINICION_CAMPO_BETTERSOFT="ORIGEN_NO_U_PLUS / PENDIENTE",
                   LOGICA_CALCULO="-", LLAVE="-", VALIDACION=INTER_COD.get(c, "-"), EJEMPLO_ORIGEN="-", EJEMPLO_DESTINO="-",
                   FUENTE_OFICIAL=S["EXT_REGLAS"], FUENTE_INSTITUCIONAL="Relaciones Internacionales / Docencia (consulta pendiente)",
                   SCRIPT_O_EVIDENCIA=S["EXT_INTER"], NIVEL_RESPALDO="Oficial (regla trazada)", ESTADO="PENDIENTE_DEMOSTRAR",
                   OBSERVACIONES="Diagnóstico: SIN_FUENTE_LOCAL; no confirma inexistencia de estudiantes de intercambio.",
                   CLASIFICACION_BRECHA="PENDIENTE_DEMOSTRAR", REQUERIMIENTO_HISTORICO="NO", DATO_SENSIBLE=("SI" if c in {"TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV", "SEXO", "NACIONALIDAD", "TIPO_RESIDENCIA_ESTUDIANTE", "PAIS_ORIGEN"} else "NO"),
                   PRECARGADO_SIES="NO", MODIFICABLE="-", ID_DICCIONARIO="-") for c in INTER_CAMPOS]

# ---------------------------------------------------------------------------
# FCU 2026 (identificación y programa; resto encuesta)
# ---------------------------------------------------------------------------
FCU_BASE = dict(PROCESO="FCU - Ficha de Caracterización Única", SUBPROCESO="FCU 2026 Período 1 (Admisión 2026)", AÑO_PROCESO="2026", AÑO_DATOS="Admisión 2026 (estudiantes de 1er año)",
                ARCHIVO_DESTINO="FCU_2026_CARGA_2026_P1_20260505_LISTO_SIN_TITULOS_PES_FINAL.csv (1.371 filas x 195 campos; no presente en repo) - " + S["FCU_CIERRE"],
                FUENTE_OFICIAL=S["FCU_MAN"], FUENTE_INSTITUCIONAL="Encuesta FCU (LimeSurvey) + precarga desde DatosAlumnos", SCRIPT_O_EVIDENCIA=S["FCU_COD"],
                PRECARGADO_SIES="NO", MODIFICABLE="-")
FCU_DEF = [
    ("A", "ANO_PRO", "Año Proceso", "4 dígitos", "(constante del proceso)", "F", "-", "Constante 2026."),
    ("B", "NOMBRE", "Nombre(s)", "Cadena 50", "NOMBRES / NOMBRE", "C", "UP-07", "_fcu2026_parse_name_parts"),
    ("C", "APELLIDO_1", "Primer apellido", "Cadena 50", "APELLIDO PATERNO", "C", "UP-08", ""),
    ("D", "APELLIDO_2", "Segundo apellido", "Cadena 50", "APELLIDO MATERNO", "C", "UP-09", ""),
    ("E", "TIPO_DOC", "Tipo documento", "1 Cédula de identidad; 2 Pasaporte; 3 IPE", "(no existe) - se asigna 1 si hay RUT", "E", "UP-03", "Catálogo distinto al de MU (R/P)."),
    ("F", "NRO_DOC", "N° de documento", "RUN 8 dígitos + DV, sin puntos, con guion", "RUT", "A", "UP-05; UP-06", "_fcu2026_normalize_rut_doc"),
    ("G", "FECHA_NAC", "Fecha de nacimiento", "DD/MM/AAAA", "FECHANACIMIENTO", "C", "UP-13", ""),
    ("H", "NAC", "Nacionalidad", "1-197 (Anexo N°2)", "NACIONALIDAD", "B", "UP-15", "NAC pendiente si no homologable con Anexo 2."),
    ("J", "ESTADO_CIVIL", "Estado civil", "1 Soltero/a; 2 Casado/a; 3 Conviviente civil; 4 Separado/a; 5 Divorciado/a; 6 Anulado/a; 7 Viudo/a", "ESTADOCIVIL", "B", "UP-19", "U+ 'CONVIVIENTE' (331) sin equivalencia demostrada con 'Conviviente civil'."),
    ("K", "SEXO", "Sexo", "H Hombre; M Mujer; X No binario", "SEXO (no usado en precarga; pregunta 8 de encuesta)", "F", "-", "Autodeclarado en encuesta; no se precarga desde U+."),
    ("Z", "CALLE", "Calle", "Cadena 50", "DIRECCIONACTUAL (texto único)", "D", "UP-20", "Parseo heurístico _fcu2026_parse_address_components."),
    ("AA", "NRO_CALLE", "Número calle", "Cadena 10", "DIRECCIONACTUAL", "D", "UP-20", ""),
    ("AB", "DEPTO_BLOCK", "Departamento/Block", "Cadena 10", "DIRECCIONACTUAL", "D", "UP-20", ""),
    ("AC", "REGION", "Región", "1-16 (Anexo N°4)", "COMUNAACTUAL", "B", "UP-21", "_fcu2026_map_region_comuna_precarga"),
    ("AD", "COMUNA", "Comuna", "1101-16305 (Anexo N°5)", "COMUNAACTUAL", "B", "UP-21", "Pendiente si la comuna U+ no coincide con Anexo 5."),
    ("AF", "CEL", "Teléfono celular", "11 dígitos 569XXXXXXXX", "FONOACTUAL", "C", "UP-22", "_fcu2026_map_cel_precarga"),
    ("AG", "CORREO", "Correo personal", "xxx@xxxx.xx", "MAIL", "A", "UP-22", ""),
    ("CN", "COD_INS", "Código SIES Institución", "3 dígitos", "(constante 162)", "F", "-", ""),
    ("CO", "COD_CAR", "Código SIES carrera", "Código asignado por SIES (hasta 25 caracteres)", "CODIGOCARRERA/CODCARPR (código local, no se fuerza)", "E", "UP-27", "Precarga deja vacío: 'COD_CAR institucional presente solo como código local'."),
]
FCU_ROWS = []
for pos, campo, nom, cod, cu, tipo, up, obs in FCU_DEF:
    FCU_ROWS.append(fila(**FCU_BASE, POSICION_SIES=pos, CAMPO_SIES=campo, NOMBRE_DESCRIPTIVO_SIES=nom, DEFINICION_OFICIAL=nom + " (6.2 Estructura de variables).",
        CODIGOS_SIES=cod, FORMATO_SIES=cod, OBLIGATORIEDAD="Según esquema condicional FCU", REGLA_TEMPORAL="Al momento de la aplicación (admisión 2026)",
        GRANULARIDAD="PERSONA (1er año)", CAMPO_U_PLUS=cu, DEFINICION_U_PLUS="Ver perfil U+", VALORES_U_PLUS="-", MAPEO_U_PLUS_SIES=obs or "Directo/normalizado",
        TIPO_OBTENCION=tipo, CAMPO_NUEVO_BETTERSOFT=up, DEFINICION_CAMPO_BETTERSOFT=("Ver " + up if up != "-" else "ORIGEN_NO_U_PLUS"), LOGICA_CALCULO=obs,
        LLAVE="RUT normalizado / token encuesta", VALIDACION=cod, EJEMPLO_ORIGEN="-", EJEMPLO_DESTINO="-",
        NIVEL_RESPALDO="Oficial + Implementado", ESTADO=("PENDIENTE_DEMOSTRAR" if tipo in {"E", "H"} or campo == "ESTADO_CIVIL" else "Confirmado"),
        OBSERVACIONES=obs, CLASIFICACION_BRECHA={"A": "YA_EXISTE_U_PLUS", "B": "EXISTE_PERO_REQUIERE_HOMOLOGACION", "C": "YA_EXISTE_U_PLUS", "D": "EXISTE_PERO_REQUIERE_HOMOLOGACION", "E": "NUEVO_CAMPO_REQUERIDO", "F": "FUENTE_EXTERNA"}[tipo],
        REQUERIMIENTO_HISTORICO="NO", DATO_SENSIBLE=("SI" if campo not in {"ANO_PRO", "COD_INS", "COD_CAR"} else "NO"), ID_DICCIONARIO=up))
FCU_ROWS.append(fila(**FCU_BASE, POSICION_SIES="I, L-Y, AE, AH-CM, CP-...", CAMPO_SIES="(~176 variables de encuesta)", NOMBRE_DESCRIPTIVO_SIES="Situación migratoria, género, pueblos originarios, discapacidad, hogar, educación, financiamiento, trabajo, RAP, razones de matrícula, etc.",
    DEFINICION_OFICIAL="Preguntas del cuestionario FCU (ver 6.2).", CODIGOS_SIES="Según manual", FORMATO_SIES="Según manual", OBLIGATORIEDAD="Condicional (esquema relacional 5.5)",
    REGLA_TEMPORAL="Respuesta del estudiante", GRANULARIDAD="PERSONA", CAMPO_U_PLUS="(no aplica)", DEFINICION_U_PLUS="-", VALORES_U_PLUS="-",
    MAPEO_U_PLUS_SIES="Encuesta", TIPO_OBTENCION="F", CAMPO_NUEVO_BETTERSOFT="(no solicitar)", DEFINICION_CAMPO_BETTERSOFT="ORIGEN_NO_U_PLUS",
    LOGICA_CALCULO="-", LLAVE="-", VALIDACION="Reglas condicionales (RAP P27, discapacidad P11)", EJEMPLO_ORIGEN="-", EJEMPLO_DESTINO="-",
    NIVEL_RESPALDO="Oficial", ESTADO="No aplica (U+)", OBSERVACIONES="Datos sensibles de encuesta: no deben incorporarse al reporte U+.",
    CLASIFICACION_BRECHA="FUENTE_EXTERNA", REQUERIMIENTO_HISTORICO="NO", DATO_SENSIBLE="SI (alta sensibilidad)", ID_DICCIONARIO="-"))

# ---------------------------------------------------------------------------
# Índices CNED, Personal Académico (resumen)
# ---------------------------------------------------------------------------
CNED_ROWS = [
    fila(PROCESO="Índices CNED", SUBPROCESO=sub, AÑO_PROCESO="2025 (calendario 2026 presente)", AÑO_DATOS=ad, ARCHIVO_DESTINO="Sistema INDICES (formularios / CSV)",
         POSICION_SIES="-", CAMPO_SIES=campo, NOMBRE_DESCRIPTIVO_SIES=campo, DEFINICION_OFICIAL=defi, CODIGOS_SIES="N° entero positivo",
         FORMATO_SIES="Agregado por sede/programa y sexo", OBLIGATORIEDAD="Según manual", REGLA_TEMPORAL=ad, GRANULARIDAD="AGREGADO (sede/programa x sexo)",
         CAMPO_U_PLUS=cu, DEFINICION_U_PLUS="-", VALORES_U_PLUS="-", MAPEO_U_PLUS_SIES="No ejecutado institucionalmente con U+ (sin evidencia)",
         TIPO_OBTENCION="H", CAMPO_NUEVO_BETTERSOFT=up, DEFINICION_CAMPO_BETTERSOFT=("Ver " + up if up != "-" else "-"), LOGICA_CALCULO="Conteo agregado",
         LLAVE="CODCLI -> programa CNED", VALIDACION="-", EJEMPLO_ORIGEN="-", EJEMPLO_DESTINO="-", FUENTE_OFICIAL=S["CNED_MAN"],
         FUENTE_INSTITUCIONAL="Sin fuente institucional gobernada para esta sección", SCRIPT_O_EVIDENCIA=S["CNED_REP"],
         NIVEL_RESPALDO="Oficial (definición) / Pendiente (fuente)", ESTADO="PENDIENTE_DEMOSTRAR",
         OBSERVACIONES="El trabajo gobernado CNED en el repositorio cubre la base de programas (59 registros), no estas secciones.",
         CLASIFICACION_BRECHA="PENDIENTE_DEMOSTRAR", REQUERIMIENTO_HISTORICO="SI", DATO_SENSIBLE="NO (agregado)", PRECARGADO_SIES="NO", MODIFICABLE="-", ID_DICCIONARIO=up)
    for sub, campo, defi, ad, cu, up in [
        ("Sección 10a Origen estudiantes", "N° estudiantes de primer año por tipo de establecimiento de EM (municipal, subvencionado, particular pagado, otra IES, otra carrera misma institución, extranjera, otros) x sexo",
         "Estudiantes de primer año desagregados por sede y sexo según origen inmediato.", "1er semestre del año en proceso", "DESCRIPCION (dependencia colegio), CODIGOCOLEGIO, NOMBREUNIVERSIDAD, SEXO", "UP-16; UP-35"),
        ("Sección 10b Residencia", "N° estudiantes de primer año de la región / otras regiones / extranjeros x sexo", "Residencia en el último año.", "1er semestre del año en proceso", "COMUNAPROCEDENCIA / COMUNAACTUAL / NACIONALIDAD", "UP-21"),
        ("Sección 16 / 19 Egresados y Titulados", "Hombres/Mujeres egresados y titulados en el año anterior por programa", "Egresados no titulados y titulados en el año anterior.", "Enero-diciembre del año anterior", "ESTADOACADEMICO (sin fecha de egreso/titulación)", "UP-59; UP-60"),
    ]
]
OTROS_ROWS = [
    fila(PROCESO="Personal Académico", SUBPROCESO="Personal Académico 2026 (SIIPA)", AÑO_PROCESO="2026", AÑO_DATOS="-", ARCHIVO_DESTINO="Carga Personal Académico",
         POSICION_SIES="-", CAMPO_SIES="(todas las variables)", NOMBRE_DESCRIPTIVO_SIES="Datos de docentes/académicos", DEFINICION_OFICIAL="-", CODIGOS_SIES="-",
         FORMATO_SIES="-", OBLIGATORIEDAD="-", REGLA_TEMPORAL="-", GRANULARIDAD="DOCENTE/PERSONAL", CAMPO_U_PLUS="(no aplica)", DEFINICION_U_PLUS="-",
         VALORES_U_PLUS="-", MAPEO_U_PLUS_SIES="-", TIPO_OBTENCION="F", CAMPO_NUEVO_BETTERSOFT="(no solicitar)", DEFINICION_CAMPO_BETTERSOFT="ORIGEN_NO_U_PLUS",
         LOGICA_CALCULO="-", LLAVE="-", VALIDACION="-", EJEMPLO_ORIGEN="-", EJEMPLO_DESTINO="-", FUENTE_OFICIAL="No revisada en detalle (fuera del alcance Datos Alumnos)",
         FUENTE_INSTITUCIONAL="RR.HH. / Docencia", SCRIPT_O_EVIDENCIA=S["PA"], NIVEL_RESPALDO="-", ESTADO="No aplica (Datos Alumnos)",
         OBSERVACIONES="Proceso de personal, no de estudiantes.", CLASIFICACION_BRECHA="FUENTE_EXTERNA", REQUERIMIENTO_HISTORICO="-", DATO_SENSIBLE="SI",
         PRECARGADO_SIES="-", MODIFICABLE="-", ID_DICCIONARIO="-"),
]


def filas_oferta() -> list[dict]:
    p = GH / S["OA_CONTRATO"]
    out = []
    try:
        df = pd.read_csv(p, sep="\t", dtype=str)
    except FileNotFoundError:
        return out
    for i, r in enumerate(df.itertuples(index=False), start=1):
        origen = r.origen
        tipo = "G" if origen == "precarga_sies" else "F"
        out.append(fila(PROCESO="Oferta Académica", SUBPROCESO="Oferta Académica 2027 - Etapas 1 (17449), 2 (17451), 3 (17454)", AÑO_PROCESO="2026",
            AÑO_DATOS="2027", ARCHIVO_DESTINO="CSV ';' sin encabezado (07_resultados/cargas_congeladas)", POSICION_SIES=str(i), CAMPO_SIES=r.campo,
            NOMBRE_DESCRIPTIVO_SIES=r.campo, DEFINICION_OFICIAL="Ver Instructivo Oferta 2027", CODIGOS_SIES="Ver instructivo", FORMATO_SIES="Ver instructivo",
            OBLIGATORIEDAD="Ver instructivo", REGLA_TEMPORAL="Oferta 2027", GRANULARIDAD="OFERTA (programa)", CAMPO_U_PLUS="(no aplica)",
            DEFINICION_U_PLUS="-", VALORES_U_PLUS="-", MAPEO_U_PLUS_SIES=r.regla_uso, TIPO_OBTENCION=tipo, CAMPO_NUEVO_BETTERSOFT="(no solicitar)",
            DEFINICION_CAMPO_BETTERSOFT="ORIGEN_NO_U_PLUS", LOGICA_CALCULO="-", LLAVE="CODIGO_UNICO", VALIDACION="Reglas Anexo instructivo",
            EJEMPLO_ORIGEN="-", EJEMPLO_DESTINO="-", FUENTE_OFICIAL=S["OA_INS"], FUENTE_INSTITUCIONAL=("Reporte 5913 (precarga)" if tipo == "G" else "Docencia (mallas/perfiles) / sin fuente activa"),
            SCRIPT_O_EVIDENCIA=S["OA_CONTRATO"], NIVEL_RESPALDO="Oficial", ESTADO=r.estado,
            OBSERVACIONES="Atributo de programa, no de estudiante. Catálogos MODALIDAD y COD_JORNADA de este instructivo son la referencia para MU.",
            CLASIFICACION_BRECHA=("PRECARGADO_SIES" if tipo == "G" else "FUENTE_EXTERNA"), REQUERIMIENTO_HISTORICO="NO", DATO_SENSIBLE="NO",
            PRECARGADO_SIES=("SI" if tipo == "G" else "NO"), MODIFICABLE=("SI" if "modificable" in r.regla_uso.lower() and "no modificable" not in r.regla_uso.lower() else "NO"),
            ID_DICCIONARIO="-"))
    return out


def filas_ire() -> list[dict]:
    p = GH / "avance_curricular/procesos/ire_2026/data/estructura/20260706_89535_Estructura_IRE_ID_16770.csv"
    out = []
    try:
        cols = p.read_text(encoding="utf-8-sig").splitlines()[0].split(";")
    except FileNotFoundError:
        return out
    for i, c in enumerate(cols, start=1):
        out.append(fila(PROCESO="Infraestructura y Recursos Educacionales", SUBPROCESO="IRE 2026 (ID carga 16770)", AÑO_PROCESO="2026", AÑO_DATOS="2026",
            ARCHIVO_DESTINO="procesos/ire_2026/data/cargas_congeladas/20260724_carga_exitosa", POSICION_SIES=str(i), CAMPO_SIES=c.strip(),
            NOMBRE_DESCRIPTIVO_SIES=c.strip(), DEFINICION_OFICIAL="Ver estructura/manual IRE", CODIGOS_SIES="-", FORMATO_SIES="-", OBLIGATORIEDAD="-",
            REGLA_TEMPORAL="2026", GRANULARIDAD="INFRAESTRUCTURA", CAMPO_U_PLUS="(no aplica)", DEFINICION_U_PLUS="-", VALORES_U_PLUS="-",
            MAPEO_U_PLUS_SIES="-", TIPO_OBTENCION="F", CAMPO_NUEVO_BETTERSOFT="(no solicitar)", DEFINICION_CAMPO_BETTERSOFT="ORIGEN_NO_U_PLUS",
            LOGICA_CALCULO="-", LLAVE="-", VALIDACION="-", EJEMPLO_ORIGEN="-", EJEMPLO_DESTINO="-", FUENTE_OFICIAL=S["IRE"],
            FUENTE_INSTITUCIONAL="Inmuebles, biblioteca, plataformas", SCRIPT_O_EVIDENCIA="avance_curricular/procesos/ire_2026/src/schema.py",
            NIVEL_RESPALDO="Oficial", ESTADO="No aplica (U+)",
            OBSERVACIONES="El indicador interno de uso (denominador 690 = MU 2026 VIG=1, MODALIDAD=1, JOR 1/2) se deriva del archivo MU, no es campo SIES.",
            CLASIFICACION_BRECHA="FUENTE_EXTERNA", REQUERIMIENTO_HISTORICO="NO", DATO_SENSIBLE="NO", PRECARGADO_SIES="PARCIAL", MODIFICABLE="-", ID_DICCIONARIO="-"))
    return out


# ---------------------------------------------------------------------------
# DICCIONARIO MAESTRO PARA BETTERSOFT (sección 22)
# ---------------------------------------------------------------------------
DIC_COLS = ["Nº", "ID", "BLOQUE", "CAMPO SOLICITADO", "DEFINICIÓN FUNCIONAL", "NIVEL", "TIPO", "PROCESOS QUE LO UTILIZAN", "CAMPO U+ ACTUAL",
            "TRANSFORMACIÓN", "EJEMPLO", "PRIORIDAD", "TIPO_OBTENCION", "TEMPORALIDAD", "REQUERIMIENTO_HISTORICO", "VALIDACION",
            "DATO_SENSIBLE", "ESTADO", "EVIDENCIA"]

DIC = [
    # id, bloque, campo, definicion, nivel, tipo_dato, procesos, campo_u, transf, ejemplo, prio, tipo_obt, temporal, hist, valid, sens, estado, evid
    ("UP-01", "Llaves", "CODCLI", "Código U+ que identifica una matrícula de una persona en una carrera/programa (plan). Una fila del reporte = un CODCLI. No debe cambiar en el tiempo.", "MATRÍCULA", "Texto", "MU; AC; Extranjeros; FCU", "CODCLI", "Ninguna", "20261ABCD001", "P1", "A", "Estable", "NO", "Único por fila; no nulo", "NO", "Confirmado", S["DA"]),
    ("UP-02", "Llaves", "ID_PERSONA_UPLUS", "Identificador interno estable de la persona en U+, independiente del número de documento, que agrupe todas sus matrículas (CODCLI).", "PERSONA", "Texto/Número", "MU; AC; Extranjeros", "(no observado)", "Exponer si existe en U+", "P000123", "P4", "E", "Estable", "NO", "Mismo valor para todos los CODCLI de la persona", "NO", "PENDIENTE_DEMOSTRAR (existencia en U+)", "1.754 RUT con más de un CODCLI en DatosAlumnos 11283"),
    ("UP-03", "Identificación", "TIPO_DOCUMENTO_UPLUS", "Tipo de documento con que la persona está registrada en U+, con el código original de U+ (por ejemplo RUN, pasaporte u otro).", "PERSONA", "Texto", "MU; AC; Extranjeros; FCU", "(no existe)", "Nuevo dato", "RUN", "P1", "E", "Vigente", "NO", "No nulo", "SI", "PENDIENTE_DEMOSTRAR", "MU 2025: 25 pasaportes; MU 2026: constante R"),
    ("UP-04", "Identificación", "TIPO_DOCUMENTO_SIES", "Tipo de documento en código SIES: R = RUN; P = Pasaporte. Derivado de TIPO_DOCUMENTO_UPLUS.", "PERSONA", "Texto(1)", "MU; AC; Extranjeros", "(no existe)", "RUN -> R; Pasaporte -> P", "R", "P1", "B", "Vigente", "NO", "Si P: DV vacío y NACIONALIDAD <> 38", "SI", "PENDIENTE_DEMOSTRAR (catálogo U+)", S["MAN_MU_C1"]),
    ("UP-05", "Identificación", "NUM_DOCUMENTO", "Número del documento sin puntos, sin guion y sin dígito verificador (cuerpo del RUN) o número de pasaporte tal como figura en el documento.", "PERSONA", "Texto", "MU; AC; Extranjeros; FCU", "RUT", "Parte antes del guion", "12345678", "P2", "C", "Vigente", "NO", "Si RUN: solo dígitos, sin 0 inicial", "SI", "Confirmado", S["COD_MU"]),
    ("UP-06", "Identificación", "DV", "Dígito verificador del RUN (0-9 o K mayúscula). Vacío si el documento es pasaporte.", "PERSONA", "Texto(1)", "MU; AC; Extranjeros; FCU", "RUT", "Carácter tras el guion", "K", "P2", "C", "Vigente", "NO", "Módulo 11 válido", "SI", "Confirmado", S["COD_MU"]),
    ("UP-07", "Identificación", "NOMBRES", "Nombres de pila de la persona, tal como están registrados. Entregar además la versión normalizada SIES (mayúsculas sin tildes, sin espacios dobles ni al inicio/fin).", "PERSONA", "Texto", "MU; AC; Extranjeros; FCU", "NOMBRES", "Normalización SIES", "JOSE ANGEL", "P3", "C", "Vigente", "NO", "Caracteres permitidos Cuadro N°6", "SI", "Confirmado", S["DA"]),
    ("UP-08", "Identificación", "APELLIDO_PATERNO", "Primer apellido (+ versión normalizada SIES).", "PERSONA", "Texto", "MU; AC; Extranjeros; FCU", "APELLIDO PATERNO", "Normalización SIES", "MUNOZ", "P3", "C", "Vigente", "NO", "Idem", "SI", "Confirmado", S["DA"]),
    ("UP-09", "Identificación", "APELLIDO_MATERNO", "Segundo apellido (+ versión normalizada SIES). Puede venir vacío.", "PERSONA", "Texto", "MU; AC; Extranjeros; FCU", "APELLIDO MATERNO", "Normalización SIES", "PENA", "P3", "C", "Vigente", "NO", "Idem", "SI", "Confirmado", S["DA"]),
    ("UP-10", "Identificación", "SEXO_UPLUS", "Código de sexo registrado en U+, sin transformar (valores actuales M, F, S). Bettersoft debe documentar el significado de cada código, en particular 'S'.", "PERSONA", "Texto(1)", "MU; AC; Extranjeros", "SEXO", "Ninguna", "F", "P2", "A", "Vigente", "NO", "Catálogo U+ documentado", "SI", "Confirmado M/F; PENDIENTE S", S["DA"]),
    ("UP-11", "Identificación", "SEXO_SIES_MU", "Sexo en código SIES de Matrícula Unificada: H = hombre, M = mujer, NB = no binario. Equivalencias confirmadas: U+ M -> H; U+ F -> M. Para U+ 'S' dejar vacío hasta que la institución confirme su significado.", "PERSONA", "Texto(2)", "MU; Extranjeros (AC y FCU usan X para no binario)", "SEXO", "M->H; F->M; S->(pendiente)", "M (desde U+ F)", "P2", "B", "Vigente", "NO", "H/M/NB", "SI", "Confirmado M/F; PENDIENTE S", S["COD_MU"] + "; " + S["EXT_SCRIPT"]),
    ("UP-13", "Identificación", "FECHA_NACIMIENTO", "Fecha de nacimiento en formato dd/mm/aaaa.", "PERSONA", "Fecha", "MU; AC; Extranjeros; FCU", "FECHANACIMIENTO", "dd-mm-aaaa -> dd/mm/aaaa", "07/04/1995", "P3", "C", "Vigente", "NO", ">= 01/01/1900; edad >= 15", "SI", "Confirmado", S["DA"]),
    ("UP-14", "Identificación", "NACIONALIDAD_UPLUS", "Nacionalidad registrada en U+ (texto original).", "PERSONA", "Texto", "MU; Extranjeros; FCU", "NACIONALIDAD", "Ninguna", "Peruana", "P2", "A", "Vigente", "NO", "Sin 'Por definir'", "SI", "Confirmado", S["DA"]),
    ("UP-15", "Identificación", "COD_NACIONALIDAD_SIES", "País de nacionalidad codificado según el Cuadro N°4 del Manual MU (1 a 197; 38 = Chile), que es la misma lista del Anexo N°2 de FCU. U+ debe registrar el país mediante catálogo, no texto libre.", "PERSONA", "Número", "MU; Extranjeros; FCU", "NACIONALIDAD", "Tabla gobernanza_nac.tsv", "142", "P2", "B", "Vigente", "NO", "1..197; P => <> 38", "SI", "Confirmado (16 gentilicios)", S["GOB_NAC"]),
    ("UP-16", "Identificación", "COD_PAIS_ESTUDIOS_SECUNDARIOS", "País donde la persona terminó la enseñanza media, codificado 1-197 (Cuadro N°4). Debe registrarse explícitamente; no debe deducirse de la comuna del colegio ni de la nacionalidad.", "PERSONA", "Número", "MU; Extranjeros; Índices (potencial)", "(no existe); COMUNACOLEGIO/CIUDADCOLEGIO", "Nuevo dato", "192", "P2", "E", "Hecho histórico", "NO", "1..197", "NO", "PENDIENTE_DEMOSTRAR", "MU 2026: 100% = 38 (fallback)"),
    ("UP-17", "Extranjeros", "TIPO_RESIDENCIA_ESTUDIANTE", "Tipo de residencia del estudiante extranjero según el catálogo del instructivo de Estudiantes Extranjeros (códigos 1, 2, 3). Solo para estudiantes con nacionalidad distinta de Chile.", "PERSONA-AÑO", "Número", "Extranjeros", "(no existe)", "Nuevo dato (catálogo oficial pendiente de incorporar al repositorio)", "1", "P2", "E", "Año de referencia (2025)", "SI", "Condicional con PAIS_ORIGEN", "SI (migratorio)", "PENDIENTE_DEMOSTRAR (significado de códigos)", S["EXT_REGLAS"]),
    ("UP-18", "Extranjeros", "COD_PAIS_ORIGEN", "País de origen del estudiante extranjero (1-197, distinto de 38). Obligatorio cuando TIPO_RESIDENCIA_ESTUDIANTE es 2 o 3; vacío cuando es 1.", "PERSONA-AÑO", "Número", "Extranjeros", "(no existe)", "Nuevo dato", "41", "P2", "E", "Año de referencia", "SI", "<> 38", "SI", "PENDIENTE_DEMOSTRAR", S["EXT_REGLAS"]),
    ("UP-19", "Caracterización", "ESTADO_CIVIL (UPLUS y código FCU)", "Estado civil registrado en U+ y su código FCU (1 Soltero/a ... 7 Viudo/a). El valor U+ 'CONVIVIENTE' requiere definición: FCU solo reconoce 'Conviviente civil'.", "PERSONA", "Texto + Número", "FCU", "ESTADOCIVIL", "Tabla _fcu2026_map_estado_civil_precarga", "1", "P3", "B", "Vigente", "NO", "1..7", "SI", "PENDIENTE (CONVIVIENTE)", S["FCU_COD"]),
    ("UP-20", "Caracterización", "DIRECCION_CALLE / DIRECCION_NUMERO / DIRECCION_DEPTO_BLOCK", "Dirección actual separada en calle, número y departamento/block (hoy es un texto único que se separa por heurística).", "PERSONA", "Texto", "FCU", "DIRECCIONACTUAL", "Nuevo desglose", "LOS ALERCES | 1234 | 502", "P3", "E", "Vigente", "NO", "Largo 50/10/10", "SI", "PENDIENTE_DEMOSTRAR", S["FCU_COD"]),
    ("UP-21", "Caracterización", "COMUNA_RESIDENCIA (UPLUS y códigos SIES)", "Comuna de residencia actual en texto U+ y su código oficial (Anexo N°5 FCU) con la región correspondiente (Anexo N°4).", "PERSONA", "Texto + Número", "FCU; Índices (potencial)", "COMUNAACTUAL", "Tabla comuna -> código", "13101 / 13", "P3", "B", "Vigente", "NO", "Comuna existe en Anexo 5", "SI", "Confirmado (si coincide nombre)", S["FCU_COD"]),
    ("UP-22", "Caracterización", "TELEFONO_CELULAR / CORREO_PERSONAL", "Celular en formato 569XXXXXXXX y correo personal vigentes.", "PERSONA", "Texto", "FCU (precarga)", "FONOACTUAL; MAIL", "Normalizar celular", "56912345678", "P4", "C", "Vigente", "NO", "Formato", "SI", "Confirmado", S["FCU_COD"]),
    ("UP-23", "Oferta de la matrícula", "SEDE_UPLUS + COD_SEDE_SIES", "Sede de la matrícula en código U+ (RE, CO) y su código SIES de sede (2 = Casa Central Santiago; 3 = Concepción).", "MATRÍCULA-PERÍODO", "Texto + Número", "MU; FCU", "SEDE", "RE -> 2; CO -> 3", "CO / 3", "P2", "B", "Al período informado", "SI", "Coherente con CODIGO_UNICO", "NO", "Confirmado", S["GOB_SEDE"]),
    ("UP-24", "Oferta de la matrícula", "CODCARPR + NOMBRE_CARRERA_UPLUS", "Código interno y nombre de la carrera/programa de la matrícula (hoy CODCARPR y NOMBRE_L; eliminar la columna duplicada CODIGOCARRERA).", "MATRÍCULA", "Texto", "MU; FCU; Extranjeros", "CODCARPR; NOMBRE_L", "Ninguna", "IINF / INGENIERIA EN INFORMATICA", "P2", "A", "Al período", "SI", "No nulo", "NO", "Confirmado", S["DA"]),
    ("UP-25", "Oferta de la matrícula", "JORNADA_UPLUS + COD_JORNADA_SIES", "Jornada de la matrícula en código U+ (D, V, O, sin espacios) y en código SIES de Oferta Académica (1 Diurna, 2 Vespertina, 3 Semipresencial, 4 A Distancia, 5 Otra). El código SIES debe tomarse del programa SIES asociado, no solo de la letra U+ (hay un programa 'O' que en SIES es 3).", "MATRÍCULA-PERÍODO", "Texto + Número", "MU; FCU", "JORNADA", "D->1; V->2; O->4 salvo excepción", "V / 2", "P2", "B", "Al período informado", "SI", "Consistencia con MODALIDAD", "NO", "Confirmado D/V; PENDIENTE O", S["PUENTE"]),
    ("UP-26", "Oferta de la matrícula", "MODALIDAD_PROGRAMA_SIES", "Modalidad del programa en que está matriculado según Oferta Académica: 1 Presencial, 2 Semipresencial, 3 No Presencial. No confundir con la columna U+ 'MODALIDAD' (tipo de enseñanza media).", "OFERTA", "Número", "MU; IRE (indicador interno)", "(no existe)", "Atributo del CODIGO_UNICO", "3", "P1", "E", "Al período", "SI", "Coherencia con jornada", "NO", "PENDIENTE_DEMOSTRAR", S["OA_INS"]),
    ("UP-27", "Oferta de la matrícula", "CODIGO_UNICO_SIES (+ COD_CARRERA_SIES, VERSION_SIES)", "Código único SIES del programa en que está matriculado el estudiante (formato I162S{sede}C{carrera}J{jornada}V{versión}) y sus componentes numéricos. Debe mantenerse en U+ como atributo de la oferta/plan con vigencia por año y exponerse en cada CODCLI.", "MATRÍCULA-PERÍODO (atributo de OFERTA/PLAN)", "Texto + Números", "MU; AC; Extranjeros; FCU; Índices", "(no existe) - hoy se infiere de CODCARPR+JORNADA+NOMBRE", "Nuevo dato mantenido en U+", "I162S2C1J1V2", "P1", "E", "Vigente al período informado", "SI", "Existe en Oferta Académica del año", "NO", "PENDIENTE_DEMOSTRAR", "PUENTE_SIES_COMPILADO: 70/161 combinaciones ambiguas"),
    ("UP-28", "Plan", "PLAN_ESTUDIO_UPLUS", "Código del plan de estudios U+ al que está adscrita la matrícula en el período (hoy solo aparece en el reporte de notas, columna PLAN_DE_ESTUDIO).", "MATRÍCULA-PERÍODO", "Texto", "AC; MU (resolución de versión)", "Hoja1 PLAN_DE_ESTUDIO", "Exponer en reporte de matrícula", "IINF20241", "P1", "D", "Al período", "SI", "Existe en catálogo de planes", "NO", "Confirmado (existe en U+)", S["PROM_DIC"]),
    ("UP-29", "Plan", "PLAN_ESTUDIOS_SIES", "Número correlativo del plan dentro del CODIGO_UNICO usado en Avance Curricular (1, 2, ...), según la tabla de planes vigentes acordada por la institución.", "PLAN", "Número", "AC", "(no existe)", "Tabla institucional plan U+ -> correlativo", "1", "P2", "E", "Plan vigente del año de datos", "SI", "Correlativo por CODIGO_UNICO", "NO", "PENDIENTE_DEMOSTRAR", S["AC_GOB"]),
    ("UP-30", "Plan", "REGIMEN_PLAN", "Régimen académico del plan (semestral, trimestral, anual) con catálogo documentado. Necesario para convertir el nivel U+ a semestre SIES.", "PLAN", "Texto", "MU (NIV_ACA)", "Hoja1 REGIMEN", "Exponer en reporte de matrícula", "TRIMESTRAL", "P2", "D", "Plan vigente", "NO", "Catálogo documentado", "NO", "PENDIENTE_DEMOSTRAR (catálogo REGIMEN)", S["COD_MU"] + " L4128"),
    ("UP-31", "Ingreso", "ANIO_INGRESO_CARRERA_ACTUAL", "Año calendario en que la persona ingresó a la carrera/programa de este CODCLI.", "MATRÍCULA", "Número", "MU; AC; Extranjeros", "ANOINGRESO", "Ninguna", "2024", "P2", "A", "Hecho fijo", "NO", "1990..año proceso", "NO", "Confirmado", S["CFG_ING"]),
    ("UP-32", "Ingreso", "PERIODO_INGRESO_UPLUS + SEM_INGRESO_CARRERA_ACTUAL_SIES", "Período de ingreso U+ (1, 2, 3) y semestre SIES (1 o 2). Bettersoft debe documentar qué significa el período 3.", "MATRÍCULA", "Número", "MU; AC; Extranjeros", "PERIODOINGRESO", "1->1; 2->2; 3->2 (decisión interna)", "3 / 2", "P2", "B", "Hecho fijo", "NO", "1/2", "NO", "Confirmado 1-2; PENDIENTE 3", S["CFG_ING"]),
    ("UP-33", "Ingreso", "FORMA_INGRESO_SIES (+ VIA_ADMISION_UPLUS)", "Vía efectiva por la que la persona ingresó a esta carrera, según el catálogo SIES del Cuadro N°3 (1 ingreso directo regular; 2 continuidad plan común/bachillerato; 3 cambio interno; 4 cambio externo; 5 RAP; 6 cupo extranjeros; 7 PACE; 8 inclusión; 9 características especiales; 10 otras; 11 articulación TNS a profesional). Registrar al matricular; conservar además la vía de admisión original U+.", "MATRÍCULA", "Número", "MU", "VIASDEADMISION; CATEGORIA; SITUACION (heurística)", "Nuevo dato", "11", "P1", "E", "Hecho fijo del ingreso", "NO", "Reglas Cuadro N°6", "NO", "PENDIENTE_DEMOSTRAR", S["MAN_MU_C3"]),
    ("UP-34", "Trayectoria", "CODCLI_ORIGEN", "CODCLI de la matrícula previa desde la que la persona llegó a esta carrera (cambio interno, continuidad, articulación dentro de la institución). Vacío si no existe.", "MATRÍCULA", "Texto", "MU; AC; Extranjeros", "(no existe)", "Nuevo vínculo", "20211WXYZ004", "P1", "E", "Hecho fijo", "SI", "CODCLI existe y es de la misma persona", "NO", "PENDIENTE_DEMOSTRAR", S["CFG_ING"]),
    ("UP-35", "Trayectoria", "TIPO_ORIGEN", "Indica de dónde proviene el estudiante: MISMA_INSTITUCION, OTRA_INSTITUCION, SIN_ORIGEN (ingreso directo) o NO_IDENTIFICABLE.", "MATRÍCULA", "Texto", "MU; Índices (potencial)", "(no existe)", "Nuevo dato", "OTRA_INSTITUCION", "P1", "E", "Hecho fijo", "NO", "Coherente con FORMA_INGRESO_SIES", "NO", "PENDIENTE_DEMOSTRAR", S["MAN_MU"]),
    ("UP-36", "Trayectoria", "ANIO_INGRESO_ORIGEN", "Año en que la persona ingresó como estudiante de primer año a la carrera de origen o programa vinculante. 1900 si es externa o no identificable (regla oficial MU).", "MATRÍCULA", "Número", "MU; AC; Extranjeros", "(no existe)", "Del CODCLI_ORIGEN o registro", "2021", "P1", "E", "Hecho fijo", "SI", "<= ANIO_INGRESO_CARRERA_ACTUAL", "NO", "PENDIENTE_DEMOSTRAR", S["MAN_MU"]),
    ("UP-37", "Trayectoria", "SEM_INGRESO_ORIGEN", "Semestre (1 o 2) de ingreso a la carrera de origen; 0 cuando el año de origen es 1900.", "MATRÍCULA", "Número", "MU; AC; Extranjeros", "(no existe)", "Del CODCLI_ORIGEN", "1", "P1", "E", "Hecho fijo", "SI", "0 <=> 1900", "NO", "PENDIENTE_DEMOSTRAR", S["MAN_MU"]),
    ("UP-38", "Trayectoria", "INSTITUCION_ORIGEN_NOMBRE + COD_PAIS_INSTITUCION_ORIGEN", "Nombre de la institución de educación superior de origen (desde catálogo, no texto libre) y su país (1-197).", "MATRÍCULA", "Texto + Número", "Extranjeros; Índices (potencial)", "NOMBREUNIVERSIDAD (texto libre, 9,3%)", "Catalogar", "UNIVERSIDAD X / 192", "P3", "E", "Hecho fijo", "NO", "Se informan juntos", "NO", "PENDIENTE_DEMOSTRAR", S["EXT_REGLAS"]),
    ("UP-39", "Matrícula del período", "FECHA_MATRICULA_PERIODO", "Fecha en que se formalizó la matrícula del año/período consultado (dd/mm/aaaa). Bettersoft debe documentar si la actual FECHAMATRICULA corresponde a la primera matrícula o a la última renovación.", "MATRÍCULA-PERÍODO", "Fecha", "MU", "FECHAMATRICULA (temporalidad no documentada)", "Por año/período", "26/01/2026", "P2", "D", "Por año/período", "SI", "No futura", "NO", "PENDIENTE (definición)", S["CFG_VIG"]),
    ("UP-40", "Matrícula del período", "ANIO_MATRICULA + PERIODO_MATRICULA", "Año y período de la matrícula informada en la fila (según parámetro de extracción).", "MATRÍCULA-PERÍODO", "Número", "MU; AC", "ANOMATRICULA; PERIODOMATRICULA", "Ninguna", "2026 / 1", "P2", "A", "Por año/período", "SI", "-", "NO", "Confirmado (existe)", S["DA"]),
    ("UP-41", "Matrícula del período", "NIVEL_ACADEMICO_UPLUS + NIVEL_SEMESTRE_SIES", "Nivel del estudiante en la fecha de corte, en unidad U+ y convertido a semestre curricular SIES (1..duración). Documentar el significado de NIVEL=20.", "MATRÍCULA-PERÍODO", "Número", "MU", "NIVEL", "Conversión trimestral->semestral; 20->8 (decisión interna)", "5 / 4", "P2", "D", "A fecha de corte", "SI", "<= duración; <= 2 cohorte nueva", "NO", "PENDIENTE (NIVEL 20)", S["COD_MU"]),
    ("UP-42", "Estado", "ESTADO_ACADEMICO + SITUACION_CODIGO + SITUACION_DESCRIPCION", "Estado académico y situación de la matrícula (situación separada en código numérico y descripción), sin homologar.", "MATRÍCULA-PERÍODO", "Texto + Número", "MU; AC; Extranjeros; Índices", "ESTADOACADEMICO; SITUACION", "Separar '1 - ALUMNO REGULAR'", "VIGENTE | 1 | ALUMNO REGULAR", "P1", "A", "A fecha de corte", "SI", "Catálogo U+", "NO", "Confirmado (existe)", S["DA"]),
    ("UP-43", "Estado", "FECHA_INICIO_SITUACION / FECHA_FIN_SITUACION (historial)", "Fechas desde/hasta en que rigió cada estado y situación, para poder reconstruir el estado a cualquier fecha (30 de abril, 31 de diciembre, cierre de semestre).", "MATRÍCULA (historial)", "Fecha", "MU; AC; Extranjeros; Índices", "(no existe)", "Nuevo historial", "01/03/2025 - 15/07/2025", "P1", "E", "Histórico", "SI", "Sin traslapes", "NO", "PENDIENTE_DEMOSTRAR", "Extranjeros: 'Vigencia no se define desde matrícula 2026'"),
    ("UP-44", "Estado", "SEMESTRES_SUSPENDIDOS_PREVIOS", "Cantidad de semestres con suspensión registrada antes del año de proceso para esta matrícula.", "MATRÍCULA", "Número", "MU", "(no existe) - SITUACION solo vigente", "Conteo desde historial", "1", "P2", "E", "Acumulado previo al año", "SI", "0..99", "NO", "PENDIENTE_DEMOSTRAR", S["BASE_RET"]),
    ("UP-45", "Estado", "REINCORPORACION_2DO_SEM", "Marca 1 cuando la persona suspendió el 1er semestre del año y se reincorporó en el 2º semestre del mismo año; 0 en otro caso.", "MATRÍCULA-AÑO", "Número", "MU", "SITUACION 38 (solo vigente)", "Desde historial", "1", "P2", "E", "Año de proceso", "SI", "0/1", "NO", "PENDIENTE_DEMOSTRAR", S["MAN_MU"]),
    ("UP-46", "Resumen académico", "ASIG_INSCRITAS_ANIO_REF", "N° de asignaturas inscritas por la matrícula en el año de referencia (aprobadas + reprobadas), sin contar convalidadas u homologadas.", "MATRÍCULA-AÑO", "Número", "MU", "Hoja1 (cálculo externo)", "Conteo", "7", "P1", "D", "Año de referencia parametrizable", "SI", "0..99; >= aprobadas", "SI", "Confirmado (lógica)", S["COD_MU"]),
    ("UP-47", "Resumen académico", "ASIG_APROBADAS_ANIO_REF", "N° de asignaturas aprobadas en el año de referencia, sin convalidadas u homologadas.", "MATRÍCULA-AÑO", "Número", "MU", "Hoja1", "Conteo", "5", "P1", "D", "Año de referencia", "SI", "<= inscritas", "SI", "Confirmado (lógica)", S["COD_MU"]),
    ("UP-48", "Resumen académico", "PROM_NOTAS_SEM1_ANIO_REF", "Promedio de notas finales (escala 1,0-7,0) de las asignaturas cursadas en el 1er semestre del año de referencia, sin convalidadas; entregar también x100 (100-700) y 0 si no cursó.", "MATRÍCULA-SEMESTRE", "Decimal + Número", "MU", "Hoja1 NOTA_FINAL", "Promedio x 100", "5,95 / 595", "P1", "D", "1er semestre año ref.", "SI", "0 o 100..700", "SI", "Confirmado (lógica)", S["GOB_NOTAS"]),
    ("UP-49", "Resumen académico", "PROM_NOTAS_SEM2_ANIO_REF", "Idem para el 2º semestre del año de referencia (documentar si el período U+ 3 pertenece al 2º semestre).", "MATRÍCULA-SEMESTRE", "Decimal + Número", "MU", "Hoja1 NOTA_FINAL", "Promedio x 100", "6,30 / 630", "P1", "D", "2º semestre año ref.", "SI", "0 o 100..700", "SI", "Confirmado (lógica)", S["GOB_NOTAS"]),
    ("UP-50", "Resumen académico", "ASIG_INSCRITAS_HISTORICAS", "N° total de inscripciones de asignaturas desde el inicio de la carrera hasta el cierre del año de referencia; las reprobadas cuentan cada vez; incluye convalidadas/homologadas de la carrera actual.", "MATRÍCULA (acumulado)", "Número", "MU", "Hoja1 (historial incompleto)", "Conteo sobre historial completo", "28", "P1", "D", "Acumulado", "SI", "0..200", "SI", "PENDIENTE (historial completo)", S["COD_MU"]),
    ("UP-51", "Resumen académico", "ASIG_APROBADAS_HISTORICAS", "N° de asignaturas aprobadas (incluye convalidadas/homologadas) desde el inicio de la carrera.", "MATRÍCULA (acumulado)", "Número", "MU", "Hoja1", "Conteo", "24", "P1", "D", "Acumulado", "SI", "<= inscritas históricas", "SI", "PENDIENTE (historial completo)", S["COD_MU"]),
    ("UP-52", "Avance curricular", "CURSO_1ER_SEM", "SI/NO: la matrícula cursó actividades académicas en el 1er semestre del año de referencia.", "MATRÍCULA-SEMESTRE", "Texto", "AC", "Hoja1 ANO/PERIODO", "Existencia de asignaturas cursadas", "SI", "P1", "D", "1er semestre año ref.", "SI", "SI/NO", "NO", "Confirmado (lógica)", S["AC_CIERRE"]),
    ("UP-53", "Avance curricular", "CURSO_2DO_SEM", "SI/NO: cursó actividades en el 2º semestre del año de referencia.", "MATRÍCULA-SEMESTRE", "Texto", "AC", "Hoja1 ANO/PERIODO", "Idem", "NO", "P1", "D", "2º semestre año ref.", "SI", "SI/NO", "NO", "Confirmado (lógica)", S["AC_CIERRE"]),
    ("UP-54", "Avance curricular", "UNIDADES_CURSADAS_ANIO_REF", "Unidades del plan (asignaturas o créditos, según TIPO_UNIDAD_MEDIDA del plan) cursadas en el año de referencia, sin convalidación ni reconocimiento.", "MATRÍCULA-AÑO", "Número", "AC", "Hoja1", "Conteo/suma", "10", "P1", "D", "Año ref.", "SI", ">= aprobadas", "SI", "Confirmado (lógica)", S["AC_CIERRE"]),
    ("UP-55", "Avance curricular", "UNIDADES_APROBADAS_ANIO_REF", "Unidades aprobadas en el año de referencia, sin convalidación ni reconocimiento.", "MATRÍCULA-AÑO", "Número", "AC", "Hoja1", "Conteo/suma", "8", "P1", "D", "Año ref.", "SI", "<= cursadas", "SI", "Confirmado (lógica)", S["AC_CIERRE"]),
    ("UP-56", "Avance curricular", "UNIDADES_CURSADAS_TOTAL", "Unidades cursadas desde el ingreso hasta el cierre del año de referencia (puede incluir convalidación/reconocimiento).", "MATRÍCULA (acumulado)", "Número", "AC", "Hoja1", "Conteo acumulado", "40", "P1", "D", "Acumulado", "SI", ">= aprobadas total", "SI", "Confirmado (lógica)", S["AC_CIERRE"]),
    ("UP-57", "Avance curricular", "UNIDADES_APROBADAS_TOTAL", "Unidades aprobadas acumuladas (incluye convalidación/reconocimiento) hasta el cierre del año de referencia.", "MATRÍCULA (acumulado)", "Número", "AC", "Hoja1", "Conteo acumulado", "36", "P1", "D", "Acumulado", "SI", "<= total plan x 1,25", "SI", "Confirmado (lógica)", S["AC_CIERRE"]),
    ("UP-58", "Plan", "CATALOGO_PLAN: TIPO_UNIDAD_MEDIDA, TOTAL_UNIDADES_PLAN, UNIDADES_ANIO_1..7", "Por cada plan U+: tipo de unidad (1 asignaturas, 2 créditos, 3 otra + nombre), total de unidades del plan y unidades de cada año curricular (1 a 7). Extracto separado a nivel de plan.", "PLAN", "Números", "AC (Carreras)", "(no expuesto)", "Nuevo extracto", "1 | 40 | 10,10,10,10", "P2", "E", "Plan vigente año ref.", "SI", "Suma años = total", "NO", "PENDIENTE_DEMOSTRAR", S["AC_GOB"] + "carreras/"),
    ("UP-59", "Estado", "FECHA_EGRESO", "Fecha en que la persona completó el plan de estudios (egreso) en esta matrícula.", "MATRÍCULA", "Fecha", "Índices (potencial); MU VIG=2 (apoyo)", "(no existe)", "Nuevo dato", "15/12/2025", "P4", "E", "Hecho fijo", "SI", "<= fecha titulación", "NO", "PENDIENTE_DEMOSTRAR", S["CNED_MAN"]),
    ("UP-60", "Estado", "FECHA_TITULACION", "Fecha de obtención del título/grado de esta matrícula.", "MATRÍCULA", "Fecha", "Índices (potencial)", "(no existe)", "Nuevo dato", "20/03/2026", "P4", "E", "Hecho fijo", "SI", ">= egreso", "NO", "PENDIENTE_DEMOSTRAR", S["CNED_MAN"]),
    ("UP-61", "Auditoría", "CON_FIRMA + FECHA_FIRMA + MATRICULA", "Marcas de firma de contrato y el indicador MATRICULA (1/2), con su catálogo documentado (hoy sin significado documentado).", "MATRÍCULA-PERÍODO", "Texto/Fecha", "MU (auxiliar)", "CON_FIRMA; FECHAFIRMA; MATRICULA", "Ninguna", "SI | 10-01-2026 | 2", "P4", "A", "Por período", "SI", "-", "NO", "PENDIENTE (significado MATRICULA)", S["COD_MU"]),
    ("UP-62", "Detalle académico", "EXTRACTO DETALLE POR ASIGNATURA", "Extracto complementario (ya existe como reporte 7804 'Hoja1'), con llave CODCLI + PLAN: CODRAMO, RAMOEQUIV, ANO, PERIODO (con régimen), NOTA_FINAL, ESTADO, DESCRIPCION_ESTADO, TIPO_RECONOCIMIENTO explícito (convalidación, homologación, RAP), unidades/créditos de la asignatura y nivel en malla.", "ASIGNATURA", "Varios", "MU; AC", "Hoja1 (PROMEDIOSDEALUMNOS)", "Agregar CODCLI obligatorio y tipo de reconocimiento", "-", "P2", "A", "Histórico completo", "SI", "Sin duplicados CODCLI+CODRAMO+ANO+PERIODO", "SI", "Confirmado (existe)", S["PROM_DIC"]),
]
DIC_ROWS = [dict(zip(DIC_COLS, [str(i)] + list(d[:2]) + [d[2], d[3], d[4], d[5], d[6], d[7], d[8], d[9], d[10], TIPO_DESC[d[11]], d[12], d[13], d[14], d[15], d[16], d[17]])) for i, d in enumerate(DIC, start=1)]

# ---------------------------------------------------------------------------
# CATÁLOGOS Y HOMOLOGACIONES (sección 23), formato largo
# ---------------------------------------------------------------------------
CAT_COLS = ["CATALOGO", "PROCESO", "LADO", "CODIGO", "SIGNIFICADO", "HOMOLOGA_A", "EVIDENCIA", "NIVEL_RESPALDO", "ESTADO"]
CAT = []


def cat(catalogo, proceso, lado, codigo, significado, homologa="", evidencia="", respaldo="", estado=""):
    CAT.append(dict(zip(CAT_COLS, [catalogo, proceso, lado, codigo, significado, homologa, evidencia, respaldo, estado])))


for c, s_, h, e in [("D", "Diurno", "1", "Confirmado (22/22 combinaciones)"), ("V", "Vespertino", "2", "Confirmado (44/44)"),
                    ("O", "Online (según implementación)", "4 (94 combinaciones) / 3 (1: DCBS)", "PENDIENTE_DEMOSTRAR (no determinístico)")]:
    cat("JORNADA", "MU", "U+", c, s_, h, S["PUENTE"] + "; " + S["COD_MU"], "Implementado + Observado", e)
for c, s_ in [("1", "Diurna"), ("2", "Vespertina"), ("3", "Semi Presencial (B-Learning)"), ("4", "A Distancia (E-Learning)"), ("5", "Otra (mixta; solo programas antiguos presenciales)")]:
    cat("JORNADA", "MU / Oferta / AC Carreras", "SIES", c, s_, "", S["OA_INS"] + " p.7-9; " + S["AC_NORM"], "Oficial", "Confirmado")
for c, s_ in [("1", "Diurno"), ("2", "Vespertino"), ("3", "Otro")]:
    cat("JORNADA_INTERCAMBIO", "Extranjeros Intercambio", "SIES", c, s_, "", S["EXT_REGLAS"], "Oficial (regla trazada)", "Confirmado - NO combinar con JORNADA de Oferta")
for c, s_ in [("1", "Presencial (único considerado para beneficios)"), ("2", "Semipresencial"), ("3", "No Presencial")]:
    cat("MODALIDAD_PROGRAMA", "MU / Oferta", "SIES", c, s_, "", S["OA_INS"], "Oficial", "Confirmado")
for c, s_ in [("CIENTIFICO-HUMANISTA", "Modalidad de enseñanza media (5.177)"), ("TÉCNICO-PROFESIONAL", "Modalidad de enseñanza media (4.711)"), ("(vacío)", "4.756 filas")]:
    cat("MODALIDAD (columna U+)", "-", "U+", c, s_, "NO homologa a MODALIDAD SIES", S["DA"], "Observado", "No usar para SIES")
for c, s_, h, e in [("M", "Masculino (confirmado por uso en 2 procesos)", "MU: H | AC/FCU: H", "Confirmado"), ("F", "Femenino", "MU: M | AC/FCU: M", "Confirmado"), ("S", "Sin significado documentado (10 personas)", "MU implementado: NB (sin respaldo)", "PENDIENTE_DEMOSTRAR")]:
    cat("SEXO", "MU / Extranjeros", "U+", c, s_, h, S["COD_MU"] + "; " + S["EXT_SCRIPT"], "Implementado", e)
for proc, cods in [("MU (Cuadro N°1/N°2) / Extranjeros intercambio", [("H", "Hombre"), ("M", "Mujer"), ("NB", "No Binario")]),
                   ("Avance Curricular (Anexo II) / FCU (variable K)", [("H", "Hombre"), ("M", "Mujer"), ("X", "No binario")])]:
    for c, s_ in cods:
        cat("SEXO", proc, "SIES", c, s_, "", S["MAN_MU_C1"] if proc.startswith("MU") else S["AC_NORM"] + "; " + S["FCU_MAN"], "Oficial", "Confirmado - códigos NB/X difieren por proceso")
for c, n in [("RE", "Casa Central (Santiago)"), ("CO", "Sede Concepción")]:
    cat("SEDE", "MU / FCU", "U+", c, n, "2" if c == "RE" else "3", S["GOB_SEDE"], "Interno + Observado", "Confirmado")
for c, s_ in [("R", "RUT/RUN"), ("P", "Pasaporte")]:
    cat("TIPO_DOCUMENTO", "MU / AC / Extranjeros", "SIES", c, s_, "", S["MAN_MU_C1"], "Oficial", "Confirmado")
for c, s_ in [("1", "Cédula de identidad (Carnet)"), ("2", "Pasaporte"), ("3", "Identificador provisorio escolar (IPE)")]:
    cat("TIPO_DOCUMENTO", "FCU", "SIES", c, s_, "", S["FCU_MAN"], "Oficial", "Confirmado - catálogo distinto a MU")
cat("TIPO_DOCUMENTO", "MU / FCU", "U+", "(no existe)", "U+ no informa tipo de documento", "", S["DA"], "Observado", "PENDIENTE_DEMOSTRAR")
for r in [("CHILENA", "38"), ("VENEZOLANA", "192"), ("PERUANA", "142"), ("COLOMBIANA", "41"), ("HAITIANA", "78"), ("ECUATORIANA", "52"), ("ALEMANA", "3"), ("BOLIVIANA", "23"),
          ("BRASILENA", "26"), ("DOMINICANA", "149"), ("ARGENTINA", "9"), ("CUBANA", "49"), ("URUGUAYA", "188"), ("CHINA", "39"), ("IRAQUI", "83")]:
    cat("NACIONALIDAD", "MU / Extranjeros / FCU", "HOMOLOGACION", r[0], "Gentilicio U+ normalizado", r[1], S["GOB_NAC"], "Interno (validado contra Cuadro N°4)", "Confirmado")
cat("NACIONALIDAD", "MU / Extranjeros / FCU", "HOMOLOGACION", "POR DEFINIR", "Valor U+ sin país (5 filas)", "(sin equivalencia)", S["GOB_NAC"], "Interno", "PENDIENTE_DEMOSTRAR")
cat("NACIONALIDAD", "MU", "SIES", "1..197", "Cuadro N°4 País de Nacionalidad (38 = Chile)", "", S["MAN_MU_C4"], "Oficial", "Confirmado")
for c, s_ in [("1", "Ingreso Directo (regular)"), ("2", "Continuidad de Plan Común o Bachillerato"), ("3", "Cambio Interno"), ("4", "Cambio Externo"), ("5", "Ingreso por Reconocimiento de Aprendizajes Previos"),
              ("6", "Ingreso especial para estudiantes extranjeros"), ("7", "Ingreso a través del Programa PACE"), ("8", "Ingreso a través de Programas de Inclusión"),
              ("9", "Acceso por características especiales"), ("10", "Otras formas de ingreso"), ("11", "Articulación de TNS a carrera profesional")]:
    cat("FOR_ING_ACT", "MU", "SIES", c, s_, "", S["MAN_MU_C3"], "Oficial", "Confirmado")
for c, h, e in [("ENSEÑANZA MEDIA  NACIONAL", "1", "Implementado (heurística)"), ("EXTRANJERO", "6", "Implementado (heurística)"),
                ("PROGRAMA DE EDUCACION CONTINUA", "11 si carrera de continuidad/articulación; si no 10", "Implementado (fallback)"), ("MNP AA", "10", "Implementado (fallback)")]:
    cat("FOR_ING_ACT", "MU", "U+ VIASDEADMISION", c, "Vía de admisión U+", h, S["COD_MU"] + " (_resolve_for_ing_act_row)", "Implementado", "PENDIENTE_DEMOSTRAR (no es la vía SIES)")
for c, h in [("24 - CAMBIO DE CARRERA", "3"), ("49 - CAMBIO DE JORNADA", "3 (contradice nota Cuadro N°3)"), ("27 - CAMBIO PLAN OTRA JORNADA", "3 (contradice nota Cuadro N°3)")]:
    cat("FOR_ING_ACT", "MU", "U+ SITUACION", c, "Situación U+", h, S["COD_MU"] + " L3934-3955", "Implementado", "PENDIENTE_DEMOSTRAR")
cat("FOR_ING_ACT", "MU", "U+ NOMBRE_L", "contiene 'CONTINUIDAD'", "Nombre de carrera", "2 (ver CT-03)", S["COD_MU"] + " L3949", "Implementado", "PENDIENTE_DEMOSTRAR")
for c, h, e in [("1", "1", "Confirmado"), ("2", "2", "Confirmado"), ("3", "2", "Decisión interna; significado de 3 PENDIENTE")]:
    cat("PERIODO_INGRESO -> SEMESTRE", "MU / AC / Extranjeros", "HOMOLOGACION", c, "Período U+", h, S["CFG_ING"], "Decisión interna" if c == "3" else "Oficial + Implementado", e)
for est, sit, v1, v2 in [("VIGENTE", "(cualquiera)", "1", "1"), ("EGRESADO", "14 - APRUEBA PROGRAMA EC", "2", "2"), ("ELIMINADO", "(cualquiera)", "0", "0"),
                         ("SUSPENDIDO", "2 - SUSPENSIÓN TEMPORAL", "0", "0"), ("TITULADO", "31 - TITULADO APROBADO", "2", "0")]:
    cat("VIG (MU)", "MU", "HOMOLOGACION", f"{est} / {sit}", "Estado U+", f"gob_datosalumnos...tsv: {v1} | config_vig_fecha.json: {v2}", S["GOB_VIG"] + "; " + S["CFG_VIG"], "Decisión interna",
        "CONTRADICCIÓN (CT-01)" if v1 != v2 else "Consistente entre tablas internas; sin regla oficial de mapeo")
for c, s_ in [("0", "Estudiante sin matrícula"), ("1", "Estudiante con matrícula vigente"), ("2", "Estudiante egresado con matrícula vigente")]:
    cat("VIG (MU)", "MU", "SIES", c, s_, "", S["MAN_MU_C1"], "Oficial", "Confirmado")
for c, s_ in [("0", "Eliminar registro"), ("1", "Mantener registro (todos vigentes aunque se retiren después del 30-abr-2025)")]:
    cat("VIGENCIA (AC)", "Avance Curricular", "SIES", c, s_, "", S["AC_NORM"], "Oficial", "Confirmado - NO equivale a VIG MU")
for c, s_ in [("0", "Significado no presente en repositorio"), ("1", "Significado no presente en repositorio")]:
    cat("VIGENCIA (Extranjeros)", "Extranjeros Regulares", "SIES", c, s_, "", S["EXT_REGLAS"], "Oficial (valores)", "PENDIENTE_DEMOSTRAR (definición)")
for c, s_ in [("1", "Vigente con estudiantes nuevos"), ("2", "Vigente sin estudiantes nuevos (solo antiguos)"), ("3", "No vigente")]:
    cat("VIGENCIA_CARRERA (Oferta)", "Oferta Académica", "SIES", c, s_, "", S["OA_INS"], "Oficial", "Confirmado - atributo de programa")
for c, s_ in [("0", "No cumple / No aplica"), ("1", "Sí cumple"), ("2", "No presenta documentación")]:
    cat("SIT_FON_SOL", "MU", "SIES", c, s_, "Enviado siempre 0" if c == "0" else "", S["MAN_MU_C1"] + "; " + S["BASE_RET"], "Oficial + Observado", "Confirmado")
for c, s_ in [("0", "No se reincorpora / No aplica"), ("1", "Sí se reincorpora (solo última carga)")]:
    cat("REINCORPORACION", "MU", "SIES", c, s_, "", S["MAN_MU_C1"], "Oficial", "Confirmado")
for c, s_ in [("SI", "Cursó actividades"), ("NO", "No cursó")]:
    cat("CURSO_1ER_SEM / CURSO_2DO_SEM", "Avance Curricular", "SIES", c, s_, "", S["AC_NORM"], "Oficial", "Confirmado")
for c, s_ in [("1", "Asignaturas/cursos/módulos"), ("2", "Créditos académicos o SCT-Chile"), ("3", "Otra unidad (especificar)")]:
    cat("TIPO_UNIDAD_MEDIDA", "Avance Curricular Carreras", "SIES", c, s_, "", S["AC_NORM"], "Oficial", "Confirmado")
for c, s_ in [("1", "Pregrado"), ("2", "Posgrado"), ("3", "Postítulo")]:
    cat("NIVEL_GLOBAL", "Oferta / MU", "SIES", c, s_, "", S["OA_INS"] + "; " + S["GOB_NIV"], "Oficial", "Confirmado")
for c, s_ in [("0", "Bachillerato, ciclo inicial o plan común"), ("1", "Técnico de Nivel Superior"), ("2", "Profesional sin licenciatura"), ("3", "Licenciatura no conducente a título"), ("4", "Profesional con licenciatura")]:
    cat("NIVEL_CARRERA", "Oferta / AC Carreras", "SIES", c, s_, "", S["AC_NORM"], "Oficial", "Confirmado")
for est, cod in [("SOLTERO", "1"), ("CASADO", "2"), ("CONVIVIENTE", "(sin equivalencia: FCU 3 = Conviviente civil)"), ("SEPARADO", "4"), ("DIVORCIADO", "5"), ("VIUDO", "7")]:
    cat("ESTADO_CIVIL", "FCU", "HOMOLOGACION", est, "Valor U+", cod, S["FCU_COD"], "Implementado", "PENDIENTE_DEMOSTRAR" if est == "CONVIVIENTE" else "Confirmado")
for n, s_ in [("1.0-7.0", "x100 (5,8 -> 580)"), ("0", "Sin calificación: se excluye del promedio"), ("Sin cursar", "Promedio = 0")]:
    cat("ESCALA_NOTAS", "MU", "HOMOLOGACION", n, "Nota U+ (NOTA_FINAL)", s_, S["GOB_NOTAS"], "Interno + Oficial (rango 100-700 y 0)", "Confirmado")
for c, h in [("1", "1"), ("2", "2"), ("3", "2"), ("4", "3"), ("5", "4"), ("6", "4"), ("7", "5"), ("8", "6"), ("9", "6"), ("10", "7"), ("11", "8"), ("12", "8"), ("20", "8 (normalización MU 2026)")]:
    cat("NIVEL (trimestral) -> NIV_ACA", "MU", "HOMOLOGACION", c, "NIVEL U+ en plan trimestral", h, S["COD_MU"] + " L625-642, L4124-4126", "Decisión interna", "PENDIENTE_DEMOSTRAR (sin documento oficial)")
for c in ["1 - ALUMNO REGULAR", "2 - SUSPENSIÓN TEMPORAL", "3 - ELIMINACION AUTOMATICA", "5 - RENUNCIA ENTRE PERIODOS", "7 - NO RENUEVA MATRICULA", "8 - ELIMINADO SIN ACTIVIDAD ACADÉMICA",
          "9 - RECHAZO ACTUALIZACION DE PLAN 2024", "10 - ACTUALIZACIÓN DE PLAN DE ESTUDIO 2024", "11 - RENUNCIA POST INICIO CLASES", "12 - ELIMINADO MATRICULA SIN FIRMA", "13 - EGRESO",
          "14 - APRUEBA PROGRAMA EC", "15 - REPRUEBA PROGRAMA EC", "20 - VIGENTE SIN ACTIVIDAD ACADEMICA", "23 - RETIRO - RETRACTO", "24 - CAMBIO DE CARRERA", "27 - CAMBIO PLAN OTRA JORNADA",
          "31 - TITULADO APROBADO", "38 - REINCORPORACION DE ACTIVIDADES", "41 - RETIRO SIN AVISO", "42 - TITULACIÓN PRÁCTICA PROFESIONAL", "49 - CAMBIO DE JORNADA", "95 - DEFUNCIÓN",
          "100 - TITULACIÓN INTERMEDIA", "101 - TITULO INTERMEDIO 2"]:
    cat("SITUACION (U+)", "MU / AC / Extranjeros", "U+", c.split(" - ")[0], c.split(" - ", 1)[1], "", S["DA"], "Observado", "Catálogo U+ observado (25 valores)")
for c in ["VIGENTE", "ELIMINADO", "TITULADO", "SUSPENDIDO", "EGRESADO"]:
    cat("ESTADOACADEMICO (U+)", "MU / AC / Extranjeros", "U+", c, "Estado académico U+", "", S["DA"], "Observado", "Catálogo U+ observado")

# ---------------------------------------------------------------------------
# BRECHAS (sección 24)
# ---------------------------------------------------------------------------
BR_COLS = ["ID", "CAMPO", "SITUACIÓN ACTUAL", "PROBLEMA", "CAMBIO SOLICITADO", "PROCESOS AFECTADOS", "PRIORIDAD", "CLASE DE SOLICITUD", "EVIDENCIA", "ID_DICCIONARIO"]
BR = [
    ("BR-01", "CODIGO_UNICO_SIES / VERSION / COD_CARRERA / MODALIDAD", "U+ no registra el programa SIES; se infiere por JORNADA+CODCARPR+NOMBRE.", "70 de 161 combinaciones U+ apuntan a más de un código SIES; se resuelven con heurísticas.", "Crear en U+ la relación oferta/plan -> CODIGO_UNICO SIES (con vigencia por año) y exponerla en cada CODCLI con sus componentes (sede, carrera, jornada, versión) y la modalidad.", "MU; AC; Extranjeros; FCU", "P1", "Agregar columna + mantenedor", S["PUENTE"], "UP-26; UP-27"),
    ("BR-02", "FORMA_INGRESO_SIES", "No existe; se deduce de VIASDEADMISION, SITUACION y nombre de carrera.", "Heurísticas con contradicciones frente al Cuadro N°3 (CT-02, CT-03).", "Registrar la vía efectiva de ingreso SIES (1-11) en la matrícula y exponerla, conservando la vía U+ original.", "MU", "P1", "Agregar columna", S["COD_MU"], "UP-33"),
    ("BR-03", "Trayectoria de origen", "No existe vínculo entre matrícula actual y la de origen.", "ANIO/SEM_ING_ORI se reconstruyen buscando otros CODCLI del mismo RUT; externos quedan en 1900.", "Agregar CODCLI_ORIGEN, TIPO_ORIGEN, ANIO_INGRESO_ORIGEN, SEM_INGRESO_ORIGEN e institución de origen catalogada.", "MU; AC; Extranjeros", "P1", "Agregar llave + trayectoria", S["CFG_ING"], "UP-34 a UP-38"),
    ("BR-04", "Historial de estado/situación", "DatosAlumnos solo muestra el estado vigente al descargar.", "VIG a una fecha (30-abr, 2025 para Extranjeros) no se puede reconstruir; dos tablas internas de VIG en conflicto.", "Historizar estado académico y situación con fecha desde/hasta y permitir extraer el estado a una fecha de corte parametrizable.", "MU; AC; Extranjeros; Índices", "P1", "Historizar atributo + parámetro de fecha", S["GOB_VIG"] + "; " + S["CFG_VIG"], "UP-42; UP-43"),
    ("BR-05", "Resumen académico MU (ASI_*, PROM_*)", "Se calcula fuera de U+ desde el reporte de notas (Hoja1) cruzando por RUT+DV+CODCARR.", "Cálculo manual; historial del reporte limitado a 2 años; cruce no usa CODCLI.", "Exponer por CODCLI y año de referencia: asignaturas inscritas/aprobadas del año, promedios por semestre (1,0-7,0 y x100), inscritas/aprobadas históricas.", "MU", "P1", "Campos calculados + parámetro de año", S["COD_MU"] + " L669-754", "UP-46 a UP-51"),
    ("BR-06", "Avance curricular (CURSO, UNIDADES)", "Se calcula fuera de U+ desde Hoja1; 51 casos cerrados por decisión interna.", "Sin unidades del plan ni tipo de reconocimiento explícito.", "Exponer por CODCLI y año: cursó 1er/2º semestre, unidades cursadas/aprobadas del año y acumuladas, según el tipo de unidad del plan.", "AC", "P1", "Campos calculados", S["AC_CIERRE"], "UP-52 a UP-57"),
    ("BR-07", "TIPO_DOCUMENTO", "No existe; se asume R.", "Pasaportes quedarían mal informados (MU 2025 tenía 25).", "Exponer tipo de documento U+ y su código SIES (R/P); separar NUM_DOCUMENTO y DV.", "MU; AC; Extranjeros; FCU", "P1", "Exponer dato existente / agregar columna", S["BASE_RET"], "UP-03 a UP-06"),
    ("BR-08", "PLAN_ESTUDIO en reporte de matrícula", "Solo aparece en el reporte de notas.", "Necesario para versión SIES y para Avance Curricular.", "Incluir el código de plan U+ vigente en cada CODCLI y el correlativo SIES del plan.", "AC; MU", "P1", "Exponer plan de estudios", S["PROM_DIC"], "UP-28; UP-29"),
    ("BR-09", "Parámetros de extracción", "El reporte entrega el universo completo con estado actual (años 2013-2026).", "No se puede pedir 'matriculados al 30-abr-2026' ni 'estado al 31-dic-2025'.", "Permitir filtrar por año/período de matrícula, fecha de corte y nivel global; una fila por CODCLI-período.", "MU; AC; Extranjeros", "P1", "Permitir seleccionar año/período", S["DA"], "UP-40; UP-43"),
    ("BR-10", "Nacionalidad codificada", "Texto libre con 27 variantes y 'Por definir'.", "Requiere tabla de homologación manual.", "Registrar país de nacionalidad con catálogo de países y exponer código SIES 1-197 además del texto.", "MU; Extranjeros; FCU", "P2", "Generar equivalencia SIES", S["GOB_NAC"], "UP-14; UP-15"),
    ("BR-11", "País de estudios secundarios", "No existe; se infiere Chile desde comuna del colegio.", "MU 2026 informó 38 para todos.", "Registrar el país de egreso de enseñanza media (código 1-197).", "MU; Extranjeros", "P2", "Agregar columna", S["BASE_RET"], "UP-16"),
    ("BR-12", "Residencia y país de origen (extranjeros)", "No existe.", "62/62 casos pendientes en la gobernanza de Extranjeros.", "Registrar tipo de residencia y país de origen según catálogo del instructivo de Extranjeros, solo para estudiantes extranjeros.", "Extranjeros", "P2", "Agregar columna (dato sensible)", S["EXT_GOB"], "UP-17; UP-18"),
    ("BR-13", "Sexo", "Códigos M/F/S con M = hombre.", "Riesgo de inversión M/M; 'S' sin significado.", "Documentar el catálogo U+ de sexo, exponer además el código SIES (H/M/NB) y definir 'S'.", "MU; AC; Extranjeros", "P2", "Incorporar descripción + equivalencia", S["COD_MU"], "UP-10; UP-11"),
    ("BR-14", "Jornada", "D/V/O con espacios finales en 285 filas.", "Requiere limpieza; O no determina el código SIES en 1 programa.", "Entregar jornada sin espacios y el código SIES tomado del programa SIES asociado.", "MU; FCU", "P2", "Incorporar código SIES", S["PUENTE"], "UP-25"),
    ("BR-15", "Nivel académico", "NIVEL administrativo (trimestres en algunos planes; 20 sin definición).", "Se convierte con reglas internas no documentadas oficialmente.", "Entregar nivel a la fecha de corte, régimen del plan y nivel en semestres; documentar el valor 20.", "MU", "P2", "Historizar + incorporar descripción", S["COD_MU"], "UP-30; UP-41"),
    ("BR-16", "Suspensiones y reincorporación", "Se informan constantes 0.", "Posible subinforme de SUS_PRE y REINCORPORACION.", "Calcular semestres suspendidos previos y la marca de reincorporación 2º semestre desde el historial de situaciones.", "MU", "P2", "Historizar atributo", S["BASE_RET"], "UP-44; UP-45"),
    ("BR-17", "Fecha de matrícula", "FECHAMATRICULA con temporalidad no documentada (coincide con ANOMATRICULA en 76,3%).", "Riesgo de informar una fecha que no corresponde al período.", "Entregar la fecha de matrícula de cada año/período y documentar su definición.", "MU", "P2", "Incorporar fecha de cambio", S["DA"], "UP-39"),
    ("BR-18", "Catálogo de planes (unidades)", "Estructura del plan no expuesta.", "Carreras AC se completa desde mallas fuera de U+.", "Extracto por plan: tipo de unidad, total de unidades y unidades por año curricular.", "AC", "P2", "Exponer plan de estudios", S["AC_GOB"], "UP-58"),
    ("BR-19", "Detalle académico (Hoja1)", "Reporte 7804 con llave RUT+CODCARR y convalidación como marca ambigua.", "Cálculos dependen de heurísticas sobre ESTADO/CONVALIDADO.", "Agregar CODCLI y plan, tipo de reconocimiento explícito (convalidación/homologación/RAP) y unidades de cada asignatura.", "MU; AC", "P2", "Agregar llave + incorporar código interno", S["PROM_DIC"], "UP-62"),
    ("BR-20", "Caracterización FCU (estado civil, dirección, comuna)", "Estado civil texto (CONVIVIENTE sin equivalencia); dirección en un solo texto.", "Parseo heurístico y valores sin homologar.", "Exponer estado civil con catálogo FCU, dirección desagregada y código de comuna/región oficial.", "FCU", "P3", "Incorporar código + desagregar", S["FCU_COD"], "UP-19 a UP-22"),
    ("BR-21", "Nombres normalizados", "Con tildes y espacios dobles en origen.", "Rechazos PES por caracteres.", "Entregar además versión normalizada SIES de nombres y apellidos.", "MU; AC; Extranjeros", "P3", "Campo derivado", S["MAN_MU_C6"], "UP-07 a UP-09"),
    ("BR-22", "Depuración del reporte", "Columnas redundantes o sin uso SIES demostrado (CODIGOCARRERA duplica CODCARPR; datos laborales, financieros, marketing).", "Exponen datos personales sin respaldo regulatorio.", "Excluir del reporte regulatorio las columnas marcadas EXCLUIR en la hoja 03_PERFIL_UPLUS.", "Todos", "P3", "Quitar columnas", S["DA"], "-"),
    ("BR-23", "Egreso y titulación", "Solo estado actual EGRESADO/TITULADO.", "Índices requiere egresados/titulados del año anterior.", "Agregar fecha de egreso y de titulación por CODCLI.", "Índices (potencial)", "P4", "Agregar columna", S["CNED_MAN"], "UP-59; UP-60"),
    ("BR-24", "Identificador de persona", "La persona se identifica por RUT.", "Pasaportes/cambios de documento rompen el cruce.", "Exponer identificador interno estable de persona, si existe en U+.", "Todos", "P4", "Agregar llave", S["DA"], "UP-02"),
]
BR_ROWS = [dict(zip(BR_COLS, b)) for b in BR]

# ---------------------------------------------------------------------------
# CONTRADICCIONES / HALLAZGOS (sección 5)
# ---------------------------------------------------------------------------
CT_COLS = ["ID", "TEMA", "FUENTE_1 (nivel)", "AFIRMA_1", "FUENTE_2 (nivel)", "AFIRMA_2", "PROCESO", "AÑO", "IMPACTO", "ESTADO"]
CT = [
    ("CT-01", "VIG de TITULADO", S["GOB_VIG"] + " (D)", "TITULADO / 31 -> VIG 2", S["CFG_VIG"] + " (C)", "TITULADO -> VIG 0", "MU", "2026", "VIG de titulados depende de la tabla usada.", "Pendiente decisión institucional; el manual no define mapeo desde estados internos"),
    ("CT-02", "Cambio de jornada como cambio interno", S["COD_MU"] + " L3937 (C)", "SITUACION 49/27 (cambio de jornada/plan otra jornada) -> FOR_ING_ACT 3", S["MAN_MU_C3"] + " (A)", "Para beneficios, cambio de sede, jornada o versión no es Cambio Interno si mantiene o disminuye la duración.", "MU", "2026", "Posible FOR_ING_ACT incorrecto.", "Pendiente revisión; manda la regla oficial"),
    ("CT-03", "Continuidad = FOR 2", S["COD_MU"] + " L3949 (C)", "Todo programa con 'CONTINUIDAD' en el nombre -> FOR_ING_ACT 2", S["MAN_MU_C3"] + " (A)", "FOR 2 = continuidad desde plan común/bachillerato; articulación TNS -> profesional = 11; continuidad admite 2,3,4,5,11.", "MU", "2026", "378 registros 2026 con FOR=2.", "Pendiente revisión"),
    ("CT-04", "Significado de SEXO 'S'", S["COD_MU"] + " (C)", "S -> NB", S["EXT_GOB"] + " (F)", "Sin equivalencia normativa suficiente desde la codificación local.", "MU / Extranjeros", "2026", "10 personas.", "Pendiente definición Bettersoft/institución"),
    ("CT-05", "País de estudios secundarios", S["COD_MU"] + " + " + S["GOB_PAIS"] + " (C)", "Fallback 38 si no mapea; tabla comuna -> Chile", S["MAN_MU_C1"] + " (A)", "País donde completó estudios secundarios (1-197).", "MU", "2026", "2026: 100% = 38 aunque 81 filas tienen NAC <> 38.", "Pendiente (dato inexistente en U+)"),
    ("CT-06", "Jornada O", S["COD_MU"] + " (C)", "O -> JOR 4", S["PUENTE"] + " (B)", "DCBS (jornada O) corresponde a I162S2C53J3V1 (J3).", "MU", "2026", "Homologación no determinística.", "Usar componente J del CODIGO_UNICO"),
    ("CT-07", "SIT_FON_SOL", S["COD_MU"] + " L4157 (C)", "Asigna 1", S["BASE_RET"] + " (B)", "Archivos enviados 2022-2026: 0 en 100%", "MU", "2026", "El PES_READY corrige a 0.", "Documentar como constante 0 (no U+)"),
    ("CT-08", "Fecha de nacimiento faltante", S["GOB_MU"].replace("<campo>", "fech_nac") + " (C)", "Fallback 01/01/1900", S["MAN_MU_C6"] + " (A)", "No puede ser menor a 01/01/1900 ni vacía.", "MU", "2026", "Riesgo de informar fecha ficticia.", "No usar fallback como regla"),
    ("CT-09", "Período 3", S["CFG_ING"] + " / " + S["COD_MU"] + " (D/C)", "PERIODO 3 -> semestre 2", "(sin documento U+)", "Significado del período 3 no documentado (aparece solo en jornadas O y V).", "MU / AC", "2026", "747 filas con PERIODOINGRESO 3.", "Pendiente definición Bettersoft"),
    ("CT-10", "ANIO_ING_ORI con FOR 2", S["CFG_ING"] + " (C)", "FOR=2 => 1900", S["BASE_RET"] + " (B)", "2026: 378 filas FOR=2 sin 1900", "MU", "2026", "Config y resultado difieren.", "Pendiente revisión de implementación"),
    ("CT-11", "Oferta: delimitador y fecha", S["OA_INS"] + " (A)", "CSV delimitado por comas; fecha DD/MM/AAAA", S["OA_MAPA"] + " (B)", "El sistema usa ';' y exporta DD-MM-AAAA", "Oferta Académica", "2026", "Formato de archivo.", "Documentado: manda comportamiento real del sistema"),
    ("CT-12", "Cantidad de columnas Oferta", S["OA_MAPA"] + " (D)", "48 columnas oficiales", S["OA_CONTRATO"] + " (D)", "Contrato lista 52 campos", "Oferta Académica", "2026", "Sin impacto en U+.", "Pendiente conciliación documental"),
    ("CT-13", "Estructura MU por año", S["BASE_RET"] + " (B)", "2022-2023 sin FECHA_MATRICULA ni REINCORPORACION (30 col.)", S["MAN_MU_C1"] + " 2026 (A)", "32 columnas en 2026", "MU", "2022-2026", "Cambio estructural entre años.", "Registrado; manuales 2022-2025 no presentes en repo"),
]
CT_ROWS = [dict(zip(CT_COLS, c)) for c in CT]

# ---------------------------------------------------------------------------
# DATOS SENSIBLES (sección 19)
# ---------------------------------------------------------------------------
SEN_COLS = ["DATO", "CAMPO U+", "PROCESO QUE LO REQUIERE", "¿NECESARIO?", "RECOMENDACIÓN"]
SEN = [
    ("Documento de identidad", "RUT", "MU; AC; Extranjeros; FCU", "Sí (identificación oficial)", "Incluir; acceso restringido"),
    ("Nombres y apellidos", "NOMBRES; APELLIDO PATERNO; APELLIDO MATERNO", "MU; AC; Extranjeros; FCU", "Sí", "Incluir; no incluir NOMBRE concatenado"),
    ("Fecha de nacimiento", "FECHANACIMIENTO", "MU; AC; Extranjeros; FCU", "Sí", "Incluir"),
    ("Sexo", "SEXO", "MU; AC; Extranjeros", "Sí", "Incluir raw + código SIES"),
    ("Nacionalidad / país", "NACIONALIDAD", "MU; Extranjeros; FCU", "Sí", "Incluir con código"),
    ("Tipo de residencia / país de origen", "(nuevo)", "Extranjeros", "Sí, solo extranjeros", "Solicitar solo para estudiantes extranjeros; no recopilar para chilenos"),
    ("Dirección, comuna, celular, correo", "DIRECCIONACTUAL; COMUNAACTUAL; FONOACTUAL; MAIL", "FCU (precarga)", "Sí para FCU", "Incluir solo en extracto FCU o con perfil restringido"),
    ("Estado civil", "ESTADOCIVIL", "FCU", "Sí para FCU", "Incluir con código FCU"),
    ("Rendimiento académico (notas, asignaturas)", "Hoja1", "MU; AC", "Sí", "Incluir agregados; detalle en extracto restringido"),
    ("Domicilio de procedencia y teléfono", "DIRECCIONPROCEDENCIA; CIUDADPROCEDENCIA; COMUNAPROCEDENCIA; FONOPROCEDENCIA", "Ninguno demostrado", "No", "Excluir"),
    ("Contacto de emergencia", "EMERGENCIA; FONOEMERGENCIA", "Ninguno", "No", "Excluir"),
    ("Responsable financiero", "RUTRESPONSABLEFINANCIERO; NOMBRERESPONSABLEFINANCIERO", "Ninguno", "No", "Excluir"),
    ("Datos laborales", "EMPRESA; ACTIVIDAD; DIRECCION_EMPRESA; CIUDAD_EMPRESA; COMUNA_EMPRESA; NOMBREEMPRESA", "Ninguno demostrado", "No", "Excluir"),
    ("Socioeconómicos y familiares", "TRAMODERENTA; CANTIDADDEHIJOS; ARANCELREAL", "Ninguno demostrado", "No", "Excluir"),
    ("Discapacidad, pueblos originarios, género, situación migratoria", "(encuesta FCU)", "FCU", "Sí, pero vía encuesta", "No incorporar a U+ por este requerimiento"),
    ("Datos de ejecutivo comercial", "RUT EJECUTIVO; NOMBRE EJECUTIVO", "Ninguno", "No", "Excluir"),
]
SEN_ROWS = [dict(zip(SEN_COLS, s)) for s in SEN]

# ---------------------------------------------------------------------------
# INVENTARIO DE PROCESOS (sección 4)
# ---------------------------------------------------------------------------
INV_COLS = ["PROCESO", "SUBPROCESO", "AÑO_PROCESO", "AÑO_DATOS", "ID_CARGA", "FUENTE_OFICIAL", "ARCHIVO_CARGA", "ARCHIVO_FUENTE", "USA_DATOS_ALUMNOS_UPLUS", "ESTADO_EVIDENCIA", "OBSERVACIONES"]
INV = [
    ("Matrícula Unificada", "Pregrado (Cuadro N°1)", "2026", "2026 (corte 30-abr); *_ANT = 2025", "-", S["MAN_MU"], S["FINAL_MU"] + " (4.105 filas, 32 col.)", S["PROM"] + "; " + S["DUR"] + "; " + S["PUENTE"], "SI (central)", "Confirmado", "Estado de cierre: CONGELADO_FINAL_MATERIALIZADO_LISTO_PARA_CARGA_SIN_COMPROBANTE_PES. CIERRE_PES_READY_MU2026.md: 3.402 filas cargadas el 2026-05-07."),
    ("Matrícula Unificada", "Posgrado y Postítulo (Cuadro N°2)", "2026", "2026 (corte 15-may)", "-", S["MAN_MU"], S["FINAL_MU_POS"] + " (54 filas, 21 col.)", "No determinado (scripts/localizar_pes_ready_posgrado_postitulo_2026.py)", "SI", "Parcial", ""),
    ("Matrícula Unificada", "Pregrado - archivos enviados históricos", "2022-2025", "Año de cada proceso", "-", "Manuales 2022-2025 no presentes en repositorio", S["BASE_RET"] + " (2022: 1.038; 2023: 1.145; 2024: 1.541; 2025: 2.371)", "OneDrive DAI 'Enviados/Matrícula Unificada/<año>'", "SI (inferido)", "Parcial", "2022-2023 sin FECHA_MATRICULA ni REINCORPORACION."),
    ("Avance Curricular", "Carreras Avance Curricular 2026", "2026", "2025", "16769 (ref. 5810)", S["AC_NORM"], "112d_cierre_gobernado_carga_aceptada_carreras_16769 (archivo no versionado)", "Precarga PES + planes de estudio + mallas", "NO (plan/malla)", "Parcial", "Instructivo TXT congelado referido pero no presente en la rama principal."),
    ("Avance Curricular", "Matrícula Avance Curricular 2026", "2026", "2025", "16768 (ref. 5809)", S["AC_NORM"], S["AC_READY"] + " (2.371 filas, 22 col.; archivo no versionado)", "Precarga PES + " + S["PROM"] + " (Hoja1)", "SI (Hoja1 y cruce)", "Parcial", "Carpetas 113h/113i documentan carga de matrícula 16768."),
    ("Estudiantes Extranjeros", "Extranjeros Regulares 2026", "2026", "2025", "16765", "Instructivo_Estudiantes_Extranjeros_SIES_2026.txt (no presente); " + S["EXT_REGLAS"], "02_EXTRANJEROS_REGULARES_2025_PES_READY.csv (81; no presente)", "BASE EXTRANJEROS.xlsx (62) + DatosAlumnos + precarga", "SI", "Parcial", S["EXT_CIERRE"]),
    ("Estudiantes Extranjeros", "Extranjeros de Intercambio 2026", "2026", "2025", "16764", S["EXT_REGLAS"], "Sin archivo", "SIN_FUENTE_LOCAL", "NO", "Pendiente", S["EXT_INTER"]),
    ("Oferta Académica", "Oferta 2027 Etapa 1 / 2 / 3", "2026", "2027", "17449 / 17451 / 17454", S["OA_INS"], "oferta_academica_2027/07_resultados/cargas_congeladas", "Reporte 5913 + Docencia + Rectoría", "NO", "Confirmado", "Fuente de catálogos oficiales MODALIDAD y COD_JORNADA."),
    ("Infraestructura y Recursos Educacionales", "IRE 2026", "2026", "2026", "16770", S["IRE"], "procesos/ire_2026/data/cargas_congeladas/20260724_carga_exitosa", "Inmuebles / biblioteca / plataformas", "NO (solo indicador derivado de MU)", "Confirmado", "Commit 6052616 'congelar carga IRE 2026 exitosa (PES Finalizado)'."),
    ("Personal Académico", "Personal Académico 2026 (SIIPA)", "2026", "No revisado", "-", "No revisada en detalle", "-", "RR.HH./Docencia", "NO", "Parcial", "Fuera del alcance de Datos Alumnos."),
    ("Índices CNED", "Programas / Mallas", "2025 (calendario 2026)", "2025", "-", S["CNED_MAN"], "Escritorio/CNED (bloques y carga parcial)", "Base INDICES 2005-2026, ReporteProgramas", "NO", "Parcial", S["CNED_REP"]),
    ("Índices CNED", "Origen estudiantes / Residencia / Egresados y Titulados", "2025", "Año en proceso / año anterior", "-", S["CNED_MAN"], "Sin evidencia", "Sin evidencia", "Potencial", "Pendiente", "Sin ejecución institucional demostrada con U+."),
    ("FCU", "FCU 2026 Período 1", "2026", "Admisión 2026", "-", S["FCU_MAN"], "FCU_2026_CARGA_2026_P1_..._PES_FINAL.csv (1.371 x 195; no presente)", "Encuesta + DatosAlumnos (precarga)", "SI (identificación)", "Confirmado", S["FCU_CIERRE"]),
    ("FCU", "FCU 2026 Período 2", "2026", "Admisión 2026", "-", S["FCU_MAN"], "No determinado", "Escritorio/EJECUTAR FCU PERIODO 2.docx", "SI (probable)", "Pendiente", "No revisado en detalle."),
    ("(No es carga SIES)", "Panorama Nacional Matrícula (PNM)", "-", "2007-2026", "-", "Glosarios SIES públicos", "-", "Bases públicas SIES", "NO", "No aplica", "Proyecto analítico (Power BI), no proceso de carga."),
]
INV_ROWS = [dict(zip(INV_COLS, i)) for i in INV]

# ---------------------------------------------------------------------------
# Perfil U+ (sección 8): anotaciones por columna
# ---------------------------------------------------------------------------
ANOT = {
    "Número": ("Correlativo de fila del reporte", "REPORTE", "-", "EXCLUIR"),
    "CODCLI": ("Identificador de matrícula en carrera; patrón AAAA+P+CODCARPR+NNN en 96,2% (el código infiere año/período/carrera desde él: no oficial)", "MATRÍCULA", "MU; AC; Extranjeros; FCU", "INCLUIR (llave)"),
    "CODCARPR": ("Código interno de carrera/programa; idéntico a CODIGOCARRERA en 100%", "OFERTA", "MU (llave puente SIES); FCU", "INCLUIR"),
    "NOMBRE_L": ("Nombre de carrera U+; parte de la llave del puente SIES", "OFERTA", "MU", "INCLUIR"),
    "ANOMATRICULA": ("Año de matrícula (definición temporal no documentada)", "MATRÍCULA-PERÍODO", "MU (auditoría)", "INCLUIR + definir"),
    "PERIODOMATRICULA": ("Período de matrícula 1/2/3 (3 sin definición)", "MATRÍCULA-PERÍODO", "MU (auditoría)", "INCLUIR + definir"),
    "ANOINGRESO": ("Año de ingreso a la carrera -> ANIO_ING_ACT", "MATRÍCULA", "MU; Extranjeros", "INCLUIR"),
    "PERIODOINGRESO": ("Período de ingreso -> SEM_ING_ACT (3->2 decisión interna)", "MATRÍCULA", "MU; Extranjeros", "INCLUIR"),
    "FECHAMATRICULA": ("Fecha de matrícula; año coincide con ANOMATRICULA en 76,3%", "MATRÍCULA-PERÍODO", "MU (FECHA_MATRICULA)", "INCLUIR + definir"),
    "JORNADA": ("Jornada U+ D/V/O -> JOR 1/2/4 (con excepción)", "MATRÍCULA / OFERTA", "MU; FCU", "INCLUIR (sin espacios)"),
    "RUT": ("RUN con guion y DV; DV válido 100%", "PERSONA", "MU; AC; Extranjeros; FCU", "INCLUIR (separar)"),
    "NOMBRE": ("Nombre completo concatenado", "PERSONA", "-", "EXCLUIR (redundante)"),
    "SEXO": ("M = masculino, F = femenino; S sin definición", "PERSONA", "MU; Extranjeros", "INCLUIR"),
    "ESTADOCIVIL": ("Estado civil texto (6 valores)", "PERSONA", "FCU", "INCLUIR"),
    "FECHANACIMIENTO": ("Fecha de nacimiento dd-mm-aaaa", "PERSONA", "MU; AC; Extranjeros; FCU", "INCLUIR"),
    "DIRECCIONPROCEDENCIA": ("Domicilio de procedencia", "PERSONA", "-", "EXCLUIR"),
    "CIUDADPROCEDENCIA": ("Ciudad de procedencia", "PERSONA", "Índices (potencial residencia)", "REVISAR"),
    "COMUNAPROCEDENCIA": ("Comuna de procedencia", "PERSONA", "Índices (potencial residencia)", "REVISAR"),
    "FONOPROCEDENCIA": ("Teléfono de procedencia", "PERSONA", "-", "EXCLUIR"),
    "DIRECCIONACTUAL": ("Dirección actual (texto único)", "PERSONA", "FCU", "INCLUIR (desagregar)"),
    "CIUDADACTUAL": ("Ciudad actual", "PERSONA", "-", "REVISAR"),
    "COMUNAACTUAL": ("Comuna actual -> COMUNA/REGION FCU", "PERSONA", "FCU", "INCLUIR (+código)"),
    "FONOACTUAL": ("Teléfono actual -> CEL FCU", "PERSONA", "FCU", "INCLUIR"),
    "MAIL": ("Correo personal -> CORREO FCU", "PERSONA", "FCU", "INCLUIR"),
    "Mail_Inst": ("Correo institucional", "PERSONA", "Encuestas internas (no SIES)", "EXCLUIR del reporte SIES"),
    "NACIONALIDAD": ("Gentilicio texto -> NAC (1-197)", "PERSONA", "MU; Extranjeros; FCU", "INCLUIR (+código)"),
    "EMERGENCIA": ("Contacto de emergencia", "PERSONA", "-", "EXCLUIR"),
    "FONOEMERGENCIA": ("Teléfono de emergencia", "PERSONA", "-", "EXCLUIR"),
    "CODIGOCOLEGIO": ("Código del establecimiento de EM (tipo de código no demostrado)", "PERSONA", "Índices (potencial)", "REVISAR"),
    "COLEGIO": ("Nombre del establecimiento de EM", "PERSONA", "-", "REVISAR"),
    "MODALIDAD": ("Modalidad de ENSEÑANZA MEDIA (no del programa)", "PERSONA", "-", "REVISAR (no usar como MODALIDAD SIES)"),
    "DESCRIPCION": ("Dependencia del establecimiento de EM (NO DEFINIDA 32%)", "PERSONA", "Índices (potencial)", "REVISAR"),
    "CIUDADCOLEGIO": ("Ciudad del colegio (usada para PAIS_EST_SEC)", "PERSONA", "MU", "REEMPLAZAR por país explícito"),
    "COMUNACOLEGIO": ("Comuna del colegio (usada para PAIS_EST_SEC)", "PERSONA", "MU", "REEMPLAZAR por país explícito"),
    "CATEGORIA": ("Categoría de matrícula (6 valores); relación con FOR_ING_ACT no demostrada", "MATRÍCULA", "MU (análisis)", "INCLUIR (raw)"),
    "VIASDEADMISION": ("Vía de admisión U+ (4 valores) -> FOR_ING_ACT por heurística", "MATRÍCULA", "MU", "INCLUIR (raw)"),
    "MOTIVODESELECCION": ("Marketing", "MATRÍCULA", "-", "EXCLUIR"),
    "MEDIOSDEINFORMACION": ("Marketing", "MATRÍCULA", "-", "EXCLUIR"),
    "VIACONSULTA": ("Marketing", "MATRÍCULA", "-", "EXCLUIR"),
    "NOMBREUNIVERSIDAD": ("Institución anterior (texto libre, 9,3%)", "MATRÍCULA", "Extranjeros (candidato)", "REVISAR -> catalogar"),
    "CARRERARANTERIOR": ("Carrera anterior (texto libre, 9,9%)", "MATRÍCULA", "MU/Extranjeros (candidato origen)", "REVISAR -> reemplazar por CODCLI_ORIGEN"),
    "RUTRESPONSABLEFINANCIERO": ("Responsable financiero", "MATRÍCULA", "-", "EXCLUIR"),
    "NOMBRERESPONSABLEFINANCIERO": ("Responsable financiero", "MATRÍCULA", "-", "EXCLUIR"),
    "CODIGOCARRERA": ("Duplicado de CODCARPR (100%)", "OFERTA", "FCU (lectura)", "EXCLUIR (redundante)"),
    "EMPRESA": ("Laboral", "PERSONA", "-", "EXCLUIR"),
    "ACTIVIDAD": ("Laboral", "PERSONA", "-", "EXCLUIR"),
    "DIRECCION_EMPRESA": ("Laboral", "PERSONA", "-", "EXCLUIR"),
    "CIUDAD_EMPRESA": ("Laboral", "PERSONA", "-", "EXCLUIR"),
    "COMUNA_EMPRESA": ("Laboral", "PERSONA", "-", "EXCLUIR"),
    "CANTIDADDEHIJOS": ("Familiar", "PERSONA", "-", "EXCLUIR"),
    "TRAMODERENTA": ("Socioeconómico", "PERSONA", "-", "EXCLUIR"),
    "NOMBREEMPRESA": ("Laboral", "PERSONA", "-", "EXCLUIR"),
    "ANOEGRESOENSENANZAMEDIA": ("Año egreso EM; valores inválidos (0, 4, 18, 99, 200, 1010)", "PERSONA", "Validación cohorte MU (potencial)", "REVISAR"),
    "NOTAENSENANZAMEDIA": ("NEM con formatos mixtos", "PERSONA", "-", "REVISAR"),
    "RUT EJECUTIVO": ("Ejecutivo comercial", "MATRÍCULA", "-", "EXCLUIR"),
    "NOMBRE EJECUTIVO": ("Ejecutivo comercial", "MATRÍCULA", "-", "EXCLUIR"),
    "ESTADOACADEMICO": ("Estado académico vigente (5 valores) -> VIG", "MATRÍCULA", "MU; AC; Extranjeros", "INCLUIR + historizar"),
    "SITUACION": ("Situación vigente 'código - descripción' (25) -> VIG, FOR 3, REINCORPORACION", "MATRÍCULA", "MU; AC; Extranjeros", "INCLUIR separado + historizar"),
    "MATRICULA": ("Indicador 1/2 sin definición documentada", "MATRÍCULA", "MU (auxiliar)", "REVISAR"),
    "NIVEL": ("Nivel administrativo 1-20 -> NIV_ACA (conversiones internas)", "MATRÍCULA-PERÍODO", "MU", "INCLUIR + definir"),
    "ARANCELREAL": ("Arancel efectivo", "MATRÍCULA", "-", "EXCLUIR"),
    "CON_FIRMA": ("Firma de contrato", "MATRÍCULA-PERÍODO", "MU (auxiliar)", "REVISAR"),
    "FECHAFIRMA": ("Fecha de firma", "MATRÍCULA-PERÍODO", "MU (auxiliar)", "REVISAR"),
    "SEDE": ("Sede RE/CO -> COD_SED 2/3", "MATRÍCULA", "MU; FCU", "INCLUIR"),
    "NOMBRES": ("Nombres de pila", "PERSONA", "MU; AC; Extranjeros; FCU", "INCLUIR"),
    "APELLIDO PATERNO": ("Primer apellido", "PERSONA", "MU; AC; Extranjeros; FCU", "INCLUIR"),
    "APELLIDO MATERNO": ("Segundo apellido", "PERSONA", "MU; AC; Extranjeros; FCU", "INCLUIR"),
}
PERSONALES = {"RUT", "NOMBRE", "DIRECCIONPROCEDENCIA", "FONOPROCEDENCIA", "DIRECCIONACTUAL", "FONOACTUAL", "MAIL", "Mail_Inst", "EMERGENCIA",
              "FONOEMERGENCIA", "RUTRESPONSABLEFINANCIERO", "NOMBRERESPONSABLEFINANCIERO", "DIRECCION_EMPRESA", "NOMBRES", "APELLIDO PATERNO",
              "APELLIDO MATERNO", "RUT EJECUTIVO", "NOMBRE EJECUTIVO", "EMPRESA", "NOMBREEMPRESA", "FECHANACIMIENTO", "FECHAMATRICULA",
              "FECHAFIRMA", "CODCLI", "COLEGIO", "ACTIVIDAD", "CARRERARANTERIOR", "CODIGOCOLEGIO", "NOTAENSENANZAMEDIA", "ARANCELREAL", "Número",
              "COMUNAPROCEDENCIA", "COMUNAACTUAL", "COMUNACOLEGIO", "COMUNA_EMPRESA", "NOMBREUNIVERSIDAD"}


def _patron(v: object) -> str:
    s = re.sub(r"\d", "9", str(v))
    s = re.sub(r"[a-záéíóúñü]", "a", s)
    return re.sub(r"[A-ZÁÉÍÓÚÑÜ]", "A", s)


def perfil_uplus(path: Path | None) -> list[dict]:
    rows = []
    if path is None or not path.exists():
        for c, (d, n, p, rec) in ANOT.items():
            rows.append({"POSICION": "", "CAMPO_U_PLUS": c, "DESCRIPCION (evidencia)": d, "TIPO_DATO": "", "VALORES_OBSERVADOS": "(archivo no disponible)",
                         "DOMINIO": "", "NIVEL": n, "DISPONIBILIDAD": "", "CALIDAD": "", "PROCESOS_USO": p, "RECOMENDACION_REPORTE_REGULATORIO": rec})
        return rows
    df = pd.read_excel(path, dtype=str)
    total = len(df)
    for i, c in enumerate(df.columns, start=1):
        s = df[c]
        nn = int(s.notna().sum())
        nun = int(s.nunique(dropna=True))
        if c in PERSONALES or nun > 60:
            pats = s.dropna().map(_patron).value_counts().head(4)
            vals = "Patrones: " + "; ".join(f"{k} ({v})" for k, v in pats.items())
            dominio = f"{nun} valores distintos (no se listan: dato personal o alta cardinalidad)"
        else:
            vc = s.value_counts().head(30)
            vals = "; ".join(f"{k} ({v})" for k, v in vc.items())
            dominio = f"{nun} valores"
        num = pd.to_numeric(s.dropna().str.replace(",", ".", regex=False), errors="coerce")
        tipo = "Numérico" if len(num) and num.notna().mean() > 0.98 else ("Fecha (texto dd-mm-aaaa)" if s.dropna().str.match(r"^\d{2}-\d{2}-\d{4}$").mean() > 0.98 else "Texto")
        disp = f"{nn}/{total} ({nn / total:.1%})"
        calidad = "Completo" if nn == total else ("Incompleto" if nn / total < 0.95 else "Casi completo")
        extra = []
        if c == "JORNADA":
            extra.append("Espacios finales en 285 filas")
        if c == "NACIONALIDAD":
            extra.append("Variantes de mayúsculas")
        if c == "ANOEGRESOENSENANZAMEDIA":
            extra.append("Valores fuera de rango")
        if extra:
            calidad += " / Inconsistente: " + ", ".join(extra)
        d, n, p, rec = ANOT.get(c, ("NO_DETERMINADO (solo nombre)", "-", "-", "REVISAR"))
        rows.append({"POSICION": i, "CAMPO_U_PLUS": c, "DESCRIPCION (evidencia)": d, "TIPO_DATO": tipo, "VALORES_OBSERVADOS": vals, "DOMINIO": dominio,
                     "NIVEL": n, "DISPONIBILIDAD": disp, "CALIDAD": calidad, "PROCESOS_USO": p, "RECOMENDACION_REPORTE_REGULATORIO": rec})
    return rows


def perfil_hoja1() -> list[dict]:
    p = GH / S["PROM_DIC"]
    out = []
    try:
        df = pd.read_csv(p, sep="\t", dtype=str)
    except FileNotFoundError:
        return out
    uso = {"CODRAMO": "MU (ASI_*); AC (UNIDADES)", "ANO": "MU; AC", "PERIODO": "MU (semestre); AC (CURSO_*)", "NOTA_FINAL": "MU (PROM_*)",
           "ESTADO": "MU; AC", "DESCRIPCION_ESTADO": "MU; AC (aprobado/reprobado/convalidación)", "CONVALIDADO": "MU; AC", "PLAN_DE_ESTUDIO": "AC; MU (versión)",
           "REGIMEN": "MU (NIV_ACA trimestral)", "NIVEL": "MU (fallback NIV_ACA)", "RUT": "Llave actual", "DIG": "Llave actual", "CODCARR": "Llave actual", "CODCLI": "Llave recomendada"}
    for r in df[df["HOJA"] == "Hoja1"].itertuples(index=False):
        out.append({"POSICION": r.POSICION, "CAMPO_U_PLUS": r.COLUMNA_ORIGINAL, "NULOS": r.NULOS, "NO_NULOS": r.NO_NULOS, "VALORES_DISTINTOS": r.VALORES_DISTINTOS,
                    "TIPO_OBSERVADO": r.TIPO_OBSERVADO, "NIVEL": "ASIGNATURA (persona-carrera-asignatura-período)", "USO_EN_PROCESOS": uso.get(r.COLUMNA_ORIGINAL, "-"),
                    "OBSERVACIONES": "Reporte U+ 7804 'Promedios de alumnos'; 41.106 filas; 2 años (ANO)."})
    return out


def ambiguedad_puente() -> str:
    try:
        p = pd.read_csv(GH / S["PUENTE"], sep="\t", dtype=str)
        return f"{len(p)} combinaciones U+; {int((p['RESOLUCION_STATUS'] == 'AMBIGUO').sum())} AMBIGUO; {int((p['RESOLUCION_STATUS'] == 'UNICO').sum())} UNICO"
    except Exception as exc:  # noqa: BLE001
        return f"No calculado ({exc})"


# ---------------------------------------------------------------------------
# Escritura
# ---------------------------------------------------------------------------
HEAD_FILL = PatternFill("solid", fgColor="1F3864")
HEAD_FONT = Font(bold=True, color="FFFFFF")
PRIO_FILL = {"P1": "F8CBAD", "P2": "FFE699", "P3": "C6E0B4", "P4": "D9E1F2"}


def hoja(wb, nombre, filas, columnas, anchos=None, prio_col=None):
    ws = wb.create_sheet(nombre)
    ws.append(columnas)
    for r in filas:
        ws.append([r.get(c, "") for c in columnas])
    for cell in ws[1]:
        cell.fill = HEAD_FILL
        cell.font = HEAD_FONT
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    for i, c in enumerate(columnas, start=1):
        w = (anchos or {}).get(c, 18 if len(c) < 14 else 28)
        ws.column_dimensions[get_column_letter(i)].width = w
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    if prio_col and prio_col in columnas:
        idx = columnas.index(prio_col) + 1
        for row in ws.iter_rows(min_row=2):
            v = row[idx - 1].value
            if v in PRIO_FILL:
                row[idx - 1].fill = PatternFill("solid", fgColor=PRIO_FILL[v])
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    return ws


def resumen_por_proceso(matriz: list[dict]) -> list[dict]:
    df = pd.DataFrame(matriz)
    df["TIPO1"] = df["TIPO_OBTENCION"].str[0]
    out = []
    for (proc, sub), g in df.groupby(["PROCESO", "SUBPROCESO"], sort=False):
        t = g["TIPO1"]
        pend = g["ESTADO"].str.contains("PENDIENTE", na=False)
        out.append({"PROCESO": proc, "SUBPROCESO": sub, "TOTAL_CAMPOS_SIES": len(g), "DIRECTOS_U+ (A)": int((t == "A").sum()),
                    "DERIVABLES_U+ (B+C+D)": int(t.isin(["B", "C", "D"]).sum()), "NUEVOS_REQUERIDOS (E)": int((t == "E").sum()),
                    "EXTERNOS (F)": int((t == "F").sum()), "PRECARGADOS_SIES (G)": int((t == "G").sum()), "NO_DETERMINADOS (H)": int((t == "H").sum()),
                    "CON_ESTADO_PENDIENTE": int(pend.sum())})
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--datos-alumnos", type=Path, default=None)
    ap.add_argument("--salida", type=Path, default=REPO / "requerimiento_bettersoft_uplus_2026/resultados/DICCIONARIO_MAESTRO_UPLUS_SIES_2026.xlsx")
    a = ap.parse_args()

    matriz = MU_ROWS + MU_POS_ROWS + AC_ROWS + EXT_ROWS + INTER_ROWS + FCU_ROWS + filas_oferta() + filas_ire() + CNED_ROWS + OTROS_ROWS
    for i, r in enumerate(matriz, start=1):
        r["ID_FILA"] = f"MM-{i:03d}"

    no_uplus = [{"PROCESO": r["PROCESO"], "SUBPROCESO": r["SUBPROCESO"], "CAMPO SIES": r["CAMPO_SIES"],
                 "MOTIVO": {"F": "Fuente externa a U+", "G": "Precargado por SIES (no modificable o tomado de precarga)", "H": "No determinado / sin evidencia"}[r["TIPO_OBTENCION"][0]],
                 "FUENTE REAL": r["FUENTE_INSTITUCIONAL"], "ACCIÓN": "No solicitar a Bettersoft" if r["TIPO_OBTENCION"][0] in "FG" else "Confirmar universo/fuente antes de solicitar",
                 "ORIGEN_NO_U_PLUS": "SI"}
                for r in matriz if r["TIPO_OBTENCION"][0] in "FGH"]

    fases = [
        {"FASE": "1 - Inventario del repositorio y procesos", "ESTADO": "CERRADA", "PROCESOS_ANALIZADOS": "8 procesos / 15 subprocesos (ver 01_INVENTARIO_PROCESOS)",
         "ARCHIVOS_REVISADOS": "Repos avance_curricular, worktrees siipa_v4/kpi_rotacion_v1, CARACTERIZACIÓN, Escritorio/CNED, DATOSDEALUMNOS 9282/10246/11283",
         "CAMPOS_IDENTIFICADOS": "-", "CRUCES_CONFIRMADOS": "-", "PENDIENTES": "Instructivos Extranjeros y AC (TXT) y archivos finales AC/Extranjeros/FCU no presentes en rama principal",
         "BLOQUEOS": "Ninguno", "SIGUIENTE_FASE": "2"},
        {"FASE": "2 - Reconstrucción proceso por proceso", "ESTADO": "CERRADA con pendientes", "PROCESOS_ANALIZADOS": "MU pre/pos; AC carreras/matrícula; Extranjeros reg./intercambio; FCU; Oferta; IRE; Índices; Personal Académico",
         "ARCHIVOS_REVISADOS": "manual MU 2026; MATRIZ_NORMATIVA AC; REGLAS_VALIDACION_INSTRUCTIVO; Instructivo Oferta 2027; Manual FCU 2026; Manual INDICES 2025; estructura IRE",
         "CAMPOS_IDENTIFICADOS": str(len(matriz)), "CRUCES_CONFIRMADOS": "-", "PENDIENTES": "Estructura completa Extranjeros Intercambio; significado VIGENCIA/TIPO_RESIDENCIA Extranjeros",
         "BLOQUEOS": "Ninguno", "SIGUIENTE_FASE": "3"},
        {"FASE": "3 - Inventario y perfilado U+", "ESTADO": "CERRADA", "PROCESOS_ANALIZADOS": "-", "ARCHIVOS_REVISADOS": "DATOSDEALUMNOS_11283 (67 col., 14.644 filas); PROMEDIOSDEALUMNOS Hoja1 (25 col.)",
         "CAMPOS_IDENTIFICADOS": "67 + 25", "CRUCES_CONFIRMADOS": "-", "PENDIENTES": "Significado S, período 3, NIVEL 20, MATRICULA 1/2, REGIMEN",
         "BLOQUEOS": "Ninguno", "SIGUIENTE_FASE": "4"},
        {"FASE": "4 - Crosswalk U+ <-> SIES", "ESTADO": "CERRADA con pendientes", "PROCESOS_ANALIZADOS": "MU; AC; Extranjeros; FCU", "ARCHIVOS_REVISADOS": "codigo_gobernanza_v2.py; gobernanza_*.tsv; config_*.json; PUENTE; caracterizacion.py; scripts Extranjeros",
         "CAMPOS_IDENTIFICADOS": "-", "CRUCES_CONFIRMADOS": "SEXO M/F; SEDE RE/CO; JORNADA D/V; NAC (16 gentilicios); SEM 1/2; escala notas", "PENDIENTES": "O->J; S; VIG; FOR_ING_ACT; período 3; NIVEL",
         "BLOQUEOS": "CT-01 a CT-13", "SIGUIENTE_FASE": "5"},
        {"FASE": "5 - Consolidación transversal", "ESTADO": "CERRADA", "PROCESOS_ANALIZADOS": "-", "ARCHIVOS_REVISADOS": "-", "CAMPOS_IDENTIFICADOS": f"{len(DIC_ROWS)} campos maestros",
         "CRUCES_CONFIRMADOS": "-", "PENDIENTES": "-", "BLOQUEOS": "-", "SIGUIENTE_FASE": "6"},
        {"FASE": "6 - Gap analysis", "ESTADO": "CERRADA", "PROCESOS_ANALIZADOS": "-", "ARCHIVOS_REVISADOS": "-", "CAMPOS_IDENTIFICADOS": f"{len(BR_ROWS)} brechas",
         "CRUCES_CONFIRMADOS": "-", "PENDIENTES": "-", "BLOQUEOS": "-", "SIGUIENTE_FASE": "7"},
        {"FASE": "7 - Diccionario Bettersoft", "ESTADO": "CERRADA", "PROCESOS_ANALIZADOS": "-", "ARCHIVOS_REVISADOS": "-", "CAMPOS_IDENTIFICADOS": f"{len(DIC_ROWS)}",
         "CRUCES_CONFIRMADOS": "-", "PENDIENTES": "Casos pendientes listados", "BLOQUEOS": "-", "SIGUIENTE_FASE": "8"},
        {"FASE": "8 - Documento final de solicitud", "ESTADO": "CERRADA (borrador para revisión institucional)", "PROCESOS_ANALIZADOS": "-", "ARCHIVOS_REVISADOS": "-",
         "CAMPOS_IDENTIFICADOS": "-", "CRUCES_CONFIRMADOS": "-", "PENDIENTES": "Validación institucional antes de envío", "BLOQUEOS": "-", "SIGUIENTE_FASE": "-"},
    ]

    leeme = [
        {"TEMA": "Objetivo", "DETALLE": "Diccionario Maestro U+ -> SIES/PES para especificar a Bettersoft el nuevo reporte regulatorio equivalente a 'Datos Alumnos'."},
        {"TEMA": "Alcance temporal", "DETALLE": "Procesos 2026 con trazabilidad histórica MU 2022-2025 (archivos enviados). Manuales de años anteriores no están en el repositorio."},
        {"TEMA": "Fuente U+ perfilada", "DETALLE": (str(a.datos_alumnos) if a.datos_alumnos else "(no entregada)") + " - solo estadísticos; sin datos personales."},
        {"TEMA": "Puente SIES", "DETALLE": ambiguedad_puente()},
        {"TEMA": "Tipos de obtención", "DETALLE": " | ".join(TIPO_DESC.values())},
        {"TEMA": "Niveles de respaldo", "DETALLE": "A Regla oficial | B Dato observado | C Implementación técnica | D Decisión interna | E Pendiente/Hipótesis. Solo A es regla oficial."},
        {"TEMA": "Prioridades", "DETALLE": "P1 crítico (obligatorio SIES obtenido manualmente o con cruces complejos) | P2 alto (existe pero requiere homologación/historia/exposición) | P3 medio (simplifica controles) | P4 bajo (auditoría)."},
        {"TEMA": "VIGENCIA", "DETALLE": "Se trata por proceso: VIG MU (0/1/2), VIGENCIA AC (mantener/eliminar), VIGENCIA Extranjeros (0/1, definición pendiente), VIGENCIA_CARRERA Oferta (1/2/3). No existe equivalencia universal."},
        {"TEMA": "Ejemplos", "DETALLE": "Todos los ejemplos son ficticios o enmascarados."},
    ]

    wb = Workbook()
    wb.remove(wb.active)
    hoja(wb, "00_LEEME", leeme, ["TEMA", "DETALLE"], {"TEMA": 22, "DETALLE": 140})
    hoja(wb, "00_ESTADO_FASES", fases, list(fases[0].keys()), {k: 30 for k in fases[0]})
    hoja(wb, "01_INVENTARIO_PROCESOS", INV_ROWS, INV_COLS, {c: 30 for c in INV_COLS})
    hoja(wb, "02_RESUMEN_POR_PROCESO", resumen_por_proceso(matriz), list(resumen_por_proceso(matriz)[0].keys()))
    per = perfil_uplus(a.datos_alumnos)
    hoja(wb, "03_PERFIL_UPLUS_DATOSALUMNOS", per, list(per[0].keys()), {"DESCRIPCION (evidencia)": 45, "VALORES_OBSERVADOS": 70, "RECOMENDACION_REPORTE_REGULATORIO": 26})
    h1 = perfil_hoja1()
    if h1:
        hoja(wb, "03b_PERFIL_UPLUS_HOJA1_NOTAS", h1, list(h1[0].keys()))
    cols_m = ["ID_FILA"] + MATRIZ_COLS
    hoja(wb, "04_MATRIZ_MAESTRA", matriz, cols_m, {"DEFINICION_OFICIAL": 45, "CODIGOS_SIES": 40, "MAPEO_U_PLUS_SIES": 45, "OBSERVACIONES": 45, "ARCHIVO_DESTINO": 40, "SCRIPT_O_EVIDENCIA": 45})
    hoja(wb, "05_DICCIONARIO_BETTERSOFT", DIC_ROWS, DIC_COLS, {"CAMPO SOLICITADO": 32, "DEFINICIÓN FUNCIONAL": 70, "TRANSFORMACIÓN": 30, "EVIDENCIA": 40}, prio_col="PRIORIDAD")
    hoja(wb, "06_CATALOGOS_HOMOLOGACIONES", CAT, CAT_COLS, {"SIGNIFICADO": 40, "HOMOLOGA_A": 36, "EVIDENCIA": 50, "ESTADO": 36})
    hoja(wb, "07_BRECHAS_BETTERSOFT", BR_ROWS, BR_COLS, {"SITUACIÓN ACTUAL": 40, "PROBLEMA": 40, "CAMBIO SOLICITADO": 60, "EVIDENCIA": 40}, prio_col="PRIORIDAD")
    hoja(wb, "08_NO_RESOLUBLE_DESDE_UPLUS", no_uplus, list(no_uplus[0].keys()), {"FUENTE REAL": 45})
    hoja(wb, "09_CONTRADICCIONES", CT_ROWS, CT_COLS, {"AFIRMA_1": 40, "AFIRMA_2": 50, "FUENTE_1 (nivel)": 40, "FUENTE_2 (nivel)": 40})
    hoja(wb, "10_DATOS_SENSIBLES", SEN_ROWS, SEN_COLS, {"CAMPO U+": 50, "RECOMENDACIÓN": 50})
    fuentes = [{"CLAVE": k, "RUTA_O_REFERENCIA": v} for k, v in S.items()]
    hoja(wb, "11_FUENTES_EVIDENCIA", fuentes, ["CLAVE", "RUTA_O_REFERENCIA"], {"CLAVE": 16, "RUTA_O_REFERENCIA": 150})
    a.salida.parent.mkdir(parents=True, exist_ok=True)
    wb.save(a.salida)
    print(f"OK {a.salida} | matriz={len(matriz)} dic={len(DIC_ROWS)} catalogos={len(CAT)} brechas={len(BR_ROWS)} no_uplus={len(no_uplus)}")


if __name__ == "__main__":
    main()
