"""Gate 09: cierre funcional y resolución de pendientes del Diccionario Maestro U+ -> SIES.

Entradas (no se modifican):
- resultados/DICCIONARIO_MAESTRO_UPLUS_SIES_2026.xlsx (v0.9)
- resultados/gate09/METRICAS_EVIDENCIA_GATE09.json (gate09_metricas.py)
- 01_fuentes_oficiales/MANIFIESTO_FUENTES_GATE09.tsv (gate09_incorporar_fuentes.py)

Salidas (derivados versionados):
- resultados/AUDITORIA_GATE09_CONTRADICCIONES_UPLUS_SIES_2026.xlsx
- resultados/DICCIONARIO_MAESTRO_UPLUS_SIES_2026_v0.9.1_GATE09.xlsx
- resultados/gate09/req_gate09.json (insumo del Word para el proveedor)
"""
import csv
import json
from copy import copy
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

SUB = Path(__file__).resolve().parents[1]
RES = SUB / "resultados"
V09 = RES / "DICCIONARIO_MAESTRO_UPLUS_SIES_2026.xlsx"
V091 = RES / "DICCIONARIO_MAESTRO_UPLUS_SIES_2026_v0.9.1_GATE09.xlsx"
AUD = RES / "AUDITORIA_GATE09_CONTRADICCIONES_UPLUS_SIES_2026.xlsx"
M = json.loads((RES / "gate09/METRICAS_EVIDENCIA_GATE09.json").read_text(encoding="utf-8"))
MANIF = list(csv.DictReader((SUB / "01_fuentes_oficiales/MANIFIESTO_FUENTES_GATE09.tsv").open(encoding="utf-8"), delimiter="\t"))

# ---------------------------------------------------------------- fuentes citables
MAN_MU = "avance_curricular/manual_matrícula_unificada.txt (Manual de Procesos Matrícula Unificada 2026)"
INS_AC = "requerimiento_bettersoft_uplus_2026/01_fuentes_oficiales/avance_curricular_2026/Instructivo_Avance Curricular SIES - 2026.txt"
INS_EX = "requerimiento_bettersoft_uplus_2026/01_fuentes_oficiales/estudiantes_extranjeros_2026/Instructivo _Estudiantes_Extranjeros_SIES.txt"
INS_OA = "avance_curricular/oferta_academica_2027/01_fuentes_oficiales/Instructivo_Oferta_Academica-Acceso_CFT-IP 2027.txt"
R = ".local_restricted/requerimiento_bettersoft_uplus_2026/gate09_evidencia"
PES_MU = f"{R}/matricula_unificada_2026/08-05-2026_23-21-16_Matrícula-Pregrado-2026.csv_orig.zip + 11-05-2026_12-12-47_Matrícula-Pregrado-2026.csv_orig.zip"
PES_ERR = f"{R}/matricula_unificada_2026/07-05-2026_12-19-13_Matrícula-Pregrado-2026.csv.txt"
PES_ERR2 = f"{R}/matricula_unificada_2026/07-05-2026_12-26-55_Matrícula-Pregrado-2026.csv.txt"
UPLUS = "OneDrive …/Enviados/Matrícula Unificada/2026/QUINTA SUBIDA +95/PROMEDIOSDEALUMNOS_7804.xlsx (hoja DatosAlumnos, 08-05-2026; referenciado)"
HIST = "avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/ (MU informada 2022-2026)"
METR = "requerimiento_bettersoft_uplus_2026/resultados/gate09/METRICAS_EVIDENCIA_GATE09.json"
COD = "avance_curricular/codigo_gobernanza_v2.py"

pes = M["pes_mu2026"]
h = M["historico"]
vig_pes = {k: pes["VIG"].get(k, 0) for k in ("0", "1", "2")}
cr = M["cruces"]
c2 = M["ct02"]
c3 = M["ct03"]
f3 = c2["for3_2026_vs_mu2025"]
f2 = c3["for2_2026_vs_mu2025"]
ext = M["extranjeros_1a_carga"]
err = M["pes_errores_07_05"]
err_fsol = next(v for k, v in err.items() if "FONDO SOLIDARIO" in k)
err_1900 = next(v for k, v in err.items() if "1900" in k)
hist_for3 = ", ".join(f"{y}: {h[y]['FOR_ING_ACT'].get('3', 0)}" for y in sorted(h))
hist_for2 = ", ".join(f"{y}: {h[y]['FOR_ING_ACT'].get('2', 0)}" for y in sorted(h))
hist_for11 = ", ".join(f"{y}: {h[y]['FOR_ING_ACT'].get('11', 0)}" for y in sorted(h))
hist_vig2 = ", ".join(f"{y}: {h[y]['VIG'].get('2', 0)}" for y in sorted(h))
hist_pais = ", ".join(f"{y}: {h[y]['PAIS_igual_NAC_entre_extranjeros']}/{h[y]['NAC_distinta_38']}" for y in sorted(h))
hist_sus = ", ".join(f"{y}: {h[y]['SUS_PRE_distinto_0']}" for y in sorted(h))

# ---------------------------------------------------------------- registro de 13 contradicciones
CAMPOS_REG = ["ID_CONTRADICCION", "ID_V09", "PROCESO", "SUBPROCESO", "AÑO_PROCESO", "AÑO_DATOS", "CAMPO_SIES", "REGLA_OFICIAL",
              "FUENTE_OFICIAL", "DATO_U_PLUS", "IMPLEMENTACION_HISTORICA", "ARCHIVO_ENVIADO", "CONTRADICCION", "TIPO_CONTRADICCION",
              "EXISTE_CONTRADICCION", "RESOLUCION", "ACCION_DICCIONARIO", "ACCION_BETTERSOFT", "ESTADO", "ESTADO_GATE09", "NIVEL_RESPALDO",
              "EVIDENCIA", "FUENTE_REQUERIDA", "IMPACTO", "OBSERVACIONES"]

REG = [
    dict(ID_CONTRADICCION="C09-01", ID_V09="CT-01", PROCESO="Matrícula Unificada", SUBPROCESO="Pregrado (Cuadro N°1) y Posgrado (Cuadro N°2)",
         AÑO_PROCESO="2026", AÑO_DATOS="2026 (corte 30-04-2026 pregrado)", CAMPO_SIES="VIG (col. AF pregrado / U posgrado)",
         REGLA_OFICIAL="VIG 0 = Estudiante sin matrícula; 1 = Estudiante con matrícula vigente; 2 = Estudiante egresado con matrícula vigente, "
                       "equivalente a 'estudiante en proceso terminal': finalizó exitosamente el plan de estudios y realiza actividades "
                       "conducentes directamente al título. La vigencia se informa 'de acuerdo con la reglamentación interna de cada "
                       "institución'. Los suspendidos pueden informarse con 0, 1 o 2 según reglamentación interna. No existe regla oficial "
                       "que asigne VIG desde un estado académico interno.",
         FUENTE_OFICIAL=f"{MAN_MU}: definiciones §2.vi (p.7); Anexo 7 Cuadro N°1 col. AF (p.31); Cuadro N°2 col. U; texto sobre suspensiones (p.17); Cuadro N°5 fila 'Estudiante antiguo egresado con matrícula' (VIG 2); Cuadro N°6",
         DATO_U_PLUS=f"ESTADOACADEMICO=TITULADO / SITUACION 31 'TITULADO APROBADO': {M['uplus_0508']['ESTADOACADEMICO'].get('TITULADO', 0)} filas en el snapshot "
                     f"U+ del 08-05-2026; de ellas {M['ct01']['titulado_anomatricula'].get('2026', 0)} con ANOMATRICULA 2026. Es el estado vigente al descargar; sin fecha de inicio.",
         IMPLEMENTACION_HISTORICA="gobernanza_catalogos/gob_datosalumnos_estadoacademico_situacion.tsv (decisión interna): TITULADO -> VIG 2; "
                                  "control/config_vig_fecha.json (implementación): TITULADO -> VIG 0.",
         ARCHIVO_ENVIADO=f"Carga PES MU 2026 (08-05 + 11-05; {pes['filas_total']} filas): VIG 1 = {vig_pes['1']}, VIG 0 = {vig_pes['0']}, VIG 2 = {vig_pes['2']}. "
                         f"Filas cuyo RUT solo tiene matrículas TITULADO: {M['ct01']['filas_pes_rut_solo_titulado']}. Filas de RUT que además tienen otra matrícula "
                         f"titulada: {M['ct01']['filas_pes_rut_con_fila_titulado']} (VIG {M['ct01']['vig_pes_rut_con_fila_titulado']}). VIG 2 informado por año: {hist_vig2}.",
         CONTRADICCION="Dos tablas internas asignan VIG distinto al mismo estado U+ (2 vs 0). Ninguna se aplicó en el archivo cargado.",
         TIPO_CONTRADICCION="Regla / código", EXISTE_CONTRADICCION="SI (entre implementaciones; ninguna tiene respaldo oficial)",
         RESOLUCION="TITULADO_NO_DETERMINA_VIGENCIA_SIES. El estado vigente TITULADO no indica si la matrícula estaba vigente al corte ni si la persona "
                    "estaba en proceso terminal (VIG 2 exige plan finalizado + matrícula vigente del período + título aún no obtenido al corte). "
                    "Se extiende a todo mapeo estado U+ -> VIG (EGRESADO, SUSPENDIDO, ELIMINADO): ninguno tiene regla oficial.",
         ACCION_DICCIONARIO="Descartar como regla TITULADO->2 y TITULADO->0 (quedan auditables). VIG MU pasa a cálculo institucional desde datos elementales. "
                            "ESTADO_VIGENTE = PENDIENTE_DATOS_ELEMENTALES.",
         ACCION_BETTERSOFT="NO_CALCULAR VIG. Entregar: año/período y fecha de la matrícula; estado de matrícula a una fecha de corte parametrizable; "
                           "historial de estado y situación con fecha de inicio y término (UP-43); fecha de egreso (UP-59) y fecha de titulación (UP-60).",
         ESTADO="RESUELTA", ESTADO_GATE09="NO_DETERMINABLE_DESDE_U_PLUS", NIVEL_RESPALDO="OFICIAL",
         EVIDENCIA=f"{MAN_MU}; {PES_MU}; {UPLUS}; {HIST}; {METR}", FUENTE_REQUERIDA="",
         IMPACTO="MU pregrado y posgrado: VIG obligatorio. VIG 2 nunca informado 2022-2026.",
         OBSERVACIONES="La regla interna de vigencia (reglamentación institucional) debe documentarse como decisión interna, no como regla SIES."),
    dict(ID_CONTRADICCION="C09-02", ID_V09="CT-02", PROCESO="Matrícula Unificada", SUBPROCESO="Pregrado y posgrado", AÑO_PROCESO="2026", AÑO_DATOS="2026",
         CAMPO_SIES="FOR_ING_ACT (col. P) = 3 Cambio Interno",
         REGLA_OFICIAL="3 Cambio Interno: 'Estudiantes matriculados que ingresan a una nueva carrera en la misma institución en la que estuvieron "
                       "matriculados el año anterior'. 'El código de la carrera declarado en este periodo es distinto del anterior, lo que comprueba "
                       "la existencia de un cambio' y debe pertenecer a otra cohorte. Nota Cuadro N°3: para beneficios, un cambio de sede, jornada o "
                       "versión no es Cambio Interno si mantiene o disminuye la duración. Oferta: el cambio de jornada modifica el código unificado "
                       "(componente J), no el código de carrera (C).",
         FUENTE_OFICIAL=f"{MAN_MU}: §2.iv.a (p.6), §4 (p.8), Cuadro N°3 y nota (p.34); {INS_OA}: definición de Código unificado y Anexo 5 (p.65-66)",
         DATO_U_PLUS=f"SITUACION 49 'CAMBIO DE JORNADA' y 27 'CAMBIO PLAN OTRA JORNADA': {c2['uplus_sit_49_27']} filas en snapshot 08-05-2026.",
         IMPLEMENTACION_HISTORICA=f"{COD} (~L3937): SITUACION 49/27 -> FOR_ING_ACT 3.",
         ARCHIVO_ENVIADO=f"Carga PES 2026: {c2['pes_for3']} filas FOR 3; situaciones U+ de esos RUT: {c2['situaciones_uplus_de_for3']}. Contra MU 2025 enviada: "
                         f"mismo COD_CAR con distinta jornada {f3.get('mismo_COD_CAR_distinta_JOR', 0)}, mismo COD_CAR y misma jornada {f3.get('mismo_COD_CAR_misma_JOR', 0)}, "
                         f"COD_CAR distinto {f3.get('distinto_COD_CAR', 0)}, sin registro 2025 {f3.get('sin_registro_MU2025', 0)}; los de mismo COD_CAR tenían FOR "
                         f"{ {k[9:]: v for k, v in f3.items() if k.startswith('for_2025_')} } en 2025. FOR 3 por año: {hist_for3}.",
         CONTRADICCION="La implementación trata el cambio de jornada como cambio de carrera; la regla oficial exige un código de carrera distinto.",
         TIPO_CONTRADICCION="Regla / código / histórico", EXISTE_CONTRADICCION="SI",
         RESOLUCION="IMPLEMENTACION_NO_RESPALDADA_POR_REGLA_OFICIAL. El cambio de jornada por sí solo no prueba cambio de carrera. "
                    f"{f3.get('mismo_COD_CAR_distinta_JOR', 0) + f3.get('mismo_COD_CAR_misma_JOR', 0)} de {c2['pes_for3']} registros FOR 3 de 2026 mantenían el mismo código de carrera en 2025.",
         ACCION_DICCIONARIO="Eliminar SITUACION 49/27 -> 3 de todo mapeo automático (queda auditable). FOR_ING_ACT = cálculo institucional.",
         ACCION_BETTERSOFT="NO_CALCULAR FOR_ING_ACT. Entregar CODCLI_ORIGEN (UP-34), CODIGO_UNICO_SIES de la matrícula de origen y de la actual (UP-27 historizado, UP-66), "
                           "año/semestre de ingreso a ambas (UP-31, UP-36, UP-37) y el historial de movimientos con fecha y tipo (cambio de carrera, de jornada, de plan, de sede) (UP-43).",
         ESTADO="RESUELTA", ESTADO_GATE09="IMPLEMENTACION_HISTORICA_INCORRECTA", NIVEL_RESPALDO="OFICIAL",
         EVIDENCIA=f"{MAN_MU}; {INS_OA}; {PES_MU}; {HIST}; {UPLUS}; {METR}", FUENTE_REQUERIDA="",
         IMPACTO="Registros MU 2026 con FOR 3 no respaldado; posible efecto en beneficios.",
         OBSERVACIONES="La rectificación de registros ya informados es una decisión institucional fuera de este gate (el Instructivo AC 2026 indica que la corrección histórica se solicita a SIES y opera en 2027)."),
    dict(ID_CONTRADICCION="C09-03", ID_V09="CT-03", PROCESO="Matrícula Unificada", SUBPROCESO="Pregrado", AÑO_PROCESO="2026", AÑO_DATOS="2026",
         CAMPO_SIES="FOR_ING_ACT (col. P) = 2 Continuidad de Plan Común o Bachillerato",
         REGLA_OFICIAL="2 = 'Estudiantes que, habiendo cursado un bachillerato, plan común o similar, ingresan a una carrera profesional y/o técnica'; "
                       "año de origen = año de ingreso al plan común. 11 = articulación de TNS a carrera profesional. Los programas regulares de "
                       "continuidad admiten FOR 2, 3, 4, 5 y 11. 'Regular de continuidad' es un tipo de plan del programa (atributo de la oferta), no una vía de ingreso.",
         FUENTE_OFICIAL=f"{MAN_MU}: §4 (p.8-9), Cuadro N°3 (p.34), Anexo N°7 (p.41); {INS_OA}: tipos de plan y Anexo 5",
         DATO_U_PLUS=f"NOMBRE_L contiene 'CONTINUIDAD': {c3['uplus_filas_continuidad']} filas, {c3['programas_continuidad']} programas; CATEGORIA {c3['continuidad_categoria']}; "
                     f"CARRERARANTERIOR informada en {c3['continuidad_carrera_anterior_informada']:.1%} e institución anterior en {c3['continuidad_institucion_anterior_informada']:.1%} de esas filas (texto libre).",
         IMPLEMENTACION_HISTORICA=f"{COD} (~L3949): nombre con 'CONTINUIDAD' -> FOR_ING_ACT 2.",
         ARCHIVO_ENVIADO=f"Carga PES 2026: {c3['pes_for2']} filas FOR 2, el 100% en programas con 'CONTINUIDAD' ({c3['pes_for2_rut_con_programa_continuidad']}). FOR 2 por año: {hist_for2}; "
                         f"FOR 11 por año: {hist_for11}. De los FOR 2 de 2026 en el mismo programa en 2025: {f2}. "
                         f"{c3['cod_car_for2_2026_con_for11_2026']} de {c3['cod_car_for2_2026']} códigos de carrera con FOR 2 también tienen filas FOR 11 en 2026.",
         CONTRADICCION="El nombre del programa se usa como vía de ingreso; el mismo estudiante en el mismo programa pasó de FOR 11 (2025) a FOR 2 (2026) sin cambio de hecho.",
         TIPO_CONTRADICCION="Regla / código / temporalidad", EXISTE_CONTRADICCION="SI",
         RESOLUCION="NOMBRE_PROGRAMA_NO_DETERMINA_FORMA_INGRESO. 'Continuidad' en el nombre identifica a lo más el tipo de plan; la forma de ingreso "
                    "depende del programa de origen (plan común/bachillerato, TNS, misma u otra institución) o de un RAP.",
         ACCION_DICCIONARIO="Eliminar la regla por nombre (queda auditable). FOR_ING_ACT = cálculo institucional.",
         ACCION_BETTERSOFT="NO inferir por nombre. Entregar: TIPO_PLAN del programa como atributo de la oferta (UP-26); TIPO_ORIGEN (UP-35); "
                           "TIPO_PROGRAMA_ORIGEN (UP-64); CODCLI_ORIGEN o institución de origen (UP-34, UP-38); año/semestre de origen (UP-36, UP-37); "
                           "vía de admisión y cupo especial (UP-63); reconocimiento como condición de acceso (UP-65).",
         ESTADO="RESUELTA", ESTADO_GATE09="IMPLEMENTACION_HISTORICA_INCORRECTA", NIVEL_RESPALDO="OFICIAL",
         EVIDENCIA=f"{MAN_MU}; {INS_OA}; {PES_MU}; {HIST}; {UPLUS}; {METR}", FUENTE_REQUERIDA="",
         IMPACTO="Registros FOR 2 en 2026; inconsistencia temporal con MU 2025.", OBSERVACIONES="Misma observación de rectificación que C09-02."),
    dict(ID_CONTRADICCION="C09-04", ID_V09="CT-07", PROCESO="Matrícula Unificada", SUBPROCESO="Pregrado", AÑO_PROCESO="2026", AÑO_DATOS="2026",
         CAMPO_SIES="SIT_FON_SOL (col. AB)",
         REGLA_OFICIAL="'Indica si el estudiante mantiene o no la situación socioeconómica con la que obtuvo FSCU'. Códigos: 0 No cumple / No aplica; "
                       "1 Sí cumple; 2 No presenta documentación. Obligatorio en pregrado nivel global 1. Mensaje de plataforma: 'La SITUACIÓN "
                       "SOCIOECONÓMICA FONDO SOLIDARIO no corresponde para el TIPO INSTITUCIÓN'. El manual no enumera qué tipos de institución admiten 1 o 2.",
         FUENTE_OFICIAL=f"{MAN_MU}: Anexo 7 Cuadro N°1 col. AB (p.33); Cuadro N°5 fila 'Estudiante antiguo con FSCU'; Cuadro N°6 (p.38-39)",
         DATO_U_PLUS="No existe campo U+ asociado a FSCU.",
         IMPLEMENTACION_HISTORICA=f"{COD} L3027 y L4157: constante 1 (con parche posterior).",
         ARCHIVO_ENVIADO=f"Respuesta PES 07-05-2026 12:19: {err_fsol} líneas rechazadas con 'no corresponde para el TIPO INSTITUCIÓN'. Cargas aceptadas 08-05 y 11-05: "
                         f"SIT_FON_SOL {pes['SIT_FON_SOL']}. MU enviadas 2022-2025: 0 en el 100% de las filas.",
         CONTRADICCION="El código asigna 1; la plataforma rechaza valores que no corresponden al tipo de institución y los archivos aceptados llevan 0.",
         TIPO_CONTRADICCION="Código / dato", EXISTE_CONTRADICCION="SI",
         RESOLUCION="Para IPSS corresponde 0 = 'No aplica': definición oficial del código 0 más la respuesta de plataforma por tipo de institución. "
                    "El log de errores no permite ver el valor enviado en las líneas rechazadas; la conclusión se apoya en el mensaje y en las cargas aceptadas.",
         ACCION_DICCIONARIO="Constante institucional 0 documentada; la asignación 1 queda como implementación histórica incorrecta.",
         ACCION_BETTERSOFT="NO_CALCULAR. Campo fuera del reporte U+.",
         ESTADO="RESUELTA", ESTADO_GATE09="RESUELTA_DATO_REAL", NIVEL_RESPALDO="OFICIAL + OBSERVADO (respuesta de plataforma)",
         EVIDENCIA=f"{MAN_MU}; {PES_ERR}; {PES_MU}; {HIST}", FUENTE_REQUERIDA="", IMPACTO="Ninguno sobre U+.",
         OBSERVACIONES="El campo existe en la estructura IPSS, pero su único valor admitido por la plataforma para IPSS es 0."),
    dict(ID_CONTRADICCION="C09-05", ID_V09="CT-04", PROCESO="Matrícula Unificada / Estudiantes Extranjeros", SUBPROCESO="MU pregrado/posgrado; Extranjeros regulares",
         AÑO_PROCESO="2026", AÑO_DATOS="2026 (MU) / 2025 (Extranjeros)", CAMPO_SIES="SEXO",
         REGLA_OFICIAL="MU: M Mujer, H Hombre, NB No Binario. Extranjeros 2026: M, H, NB. Avance Curricular 2026: M, H, X (dato precargado no modificable). FCU: ver catálogo propio.",
         FUENTE_OFICIAL=f"{MAN_MU} Cuadro N°1 col. G y Cuadro N°6; {INS_EX} Anexo I campo G (p.10) y Anexo V; {INS_AC} Anexo II campo SEXO",
         DATO_U_PLUS=f"U+ SEXO {M['uplus_0508']['SEXO']}; 'S' en {M['ct04']['uplus_S_filas']} filas ({M['ct04']['uplus_S_rut']} RUT); significado no documentado por Bettersoft.",
         IMPLEMENTACION_HISTORICA=f"{COD} _normalize_sexo_mu: M->H, F->M, S->NB.",
         ARCHIVO_ENVIADO=f"Carga PES 2026: NB = {M['ct04']['pes_NB']} filas, todas con U+ 'S'. Pares inequívocos U+ x PES: {cr['SEXO_uplus_x_pes']}.",
         CONTRADICCION="La implementación asigna a 'S' un significado (No Binario) que no está documentado en U+.",
         TIPO_CONTRADICCION="Catálogo", EXISTE_CONTRADICCION="SI",
         RESOLUCION="S sin significado demostrado: PENDIENTE. S->NB se conserva solo como registro histórico. M->H y F->M quedan OBSERVADO (consistencia total en la carga aceptada) hasta que Bettersoft documente el catálogo U+.",
         ACCION_DICCIONARIO="Mantener SEXO_U_PLUS_RAW; SEXO_SIES por proceso (MU/Extranjeros H/M/NB; AC/FCU H/M/X) solo por transformación institucional documentada.",
         ACCION_BETTERSOFT="Entregar SEXO tal como está en U+ y documentar el significado de cada código (UP-10, UP-68). No entregar código SIES.",
         ESTADO="PENDIENTE", ESTADO_GATE09="PENDIENTE_FALTA_FUENTE", NIVEL_RESPALDO="OFICIAL (catálogos SIES) / IMPLEMENTADO (S->NB)",
         EVIDENCIA=f"{MAN_MU}; {INS_EX}; {INS_AC}; {PES_MU}; {UPLUS}", FUENTE_REQUERIDA="Catálogo oficial de SEXO de U+ (Bettersoft / Registro Académico) con el significado de 'S'.",
         IMPACTO="Pocas filas por año; no afecta un requerimiento P1.", OBSERVACIONES=""),
    dict(ID_CONTRADICCION="C09-06", ID_V09="CT-05", PROCESO="Matrícula Unificada / Estudiantes Extranjeros", SUBPROCESO="MU pregrado; Extranjeros regulares",
         AÑO_PROCESO="2026", AÑO_DATOS="2026 (MU) / 2025 (Extranjeros)", CAMPO_SIES="PAIS_EST_SEC (MU col. J) / PAIS_ESTUDIOS_SECUNDARIOS (Extranjeros campo L)",
         REGLA_OFICIAL="País donde la persona completó y aprobó la enseñanza media (licencia de EM), códigos 1-197, obligatorio. Extranjeros: 'es fundamental "
                       "que ... este dato se complete correctamente'; SIES puede pedir copia del certificado.",
         FUENTE_OFICIAL=f"{MAN_MU} Cuadro N°1 col. J (p.28) y Cuadro N°6; {INS_EX} §d (p.4-5), Anexo I campo L, Anexo V",
         DATO_U_PLUS="No existe. U+ tiene CODIGOCOLEGIO, COLEGIO, CIUDADCOLEGIO, COMUNACOLEGIO y VIASDEADMISION ('EXTRANJERO'), ninguno es país.",
         IMPLEMENTACION_HISTORICA="gobernanza_pais_est_sec.tsv (comuna -> Chile) + fallback 38 en el código.",
         ARCHIVO_ENVIADO=f"MU 2026 cargada: PAIS_EST_SEC {pes['PAIS_EST_SEC']} con {pes['NAC_distinta_38']} filas de nacionalidad extranjera. MU 2022-2025: PAIS = NAC en "
                         f"extranjeros ({hist_pais}). Extranjeros 2026 1ª carga: PAIS = NAC en {ext['PAIS_EST_SEC_igual_NAC']} y 38 en {ext['PAIS_EST_SEC_38']} de {ext['filas']}.",
         CONTRADICCION="Se informa un valor sin dato fuente: default 38 (2026) o copia de nacionalidad (2022-2025 y Extranjeros).",
         TIPO_CONTRADICCION="Dato / histórico", EXISTE_CONTRADICCION="SI",
         RESOLUCION="Clasificación: MU 2026 = DEFAULT_TECNICO; MU 2022-2025 y Extranjeros 2026 = SUPUESTO (nacionalidad no es país de estudios); "
                    "DATO_REAL = ninguno; U+ = DATO_FALTANTE. No se encontró otra fuente institucional en el repositorio.",
         ACCION_DICCIONARIO="PAIS_EST_SEC = NO_DETERMINABLE_DESDE_U_PLUS; el default y la copia de nacionalidad no son reglas.",
         ACCION_BETTERSOFT="Nuevo dato: país donde se obtuvo la licencia de enseñanza media (código 1-197 o país del establecimiento), registrado en la admisión (UP-16, P1).",
         ESTADO="RESUELTA", ESTADO_GATE09="NO_DETERMINABLE_DESDE_U_PLUS", NIVEL_RESPALDO="OFICIAL",
         EVIDENCIA=f"{MAN_MU}; {INS_EX}; {PES_MU}; {HIST}; {R}/estudiantes_extranjeros_2026/", FUENTE_REQUERIDA="",
         IMPACTO="Campo obligatorio en MU y Extranjeros informado sin dato fuente.", OBSERVACIONES="Ver hoja 08_PAIS_EST_SEC."),
    dict(ID_CONTRADICCION="C09-07", ID_V09="CT-06", PROCESO="Matrícula Unificada", SUBPROCESO="Pregrado y posgrado", AÑO_PROCESO="2026", AÑO_DATOS="2026",
         CAMPO_SIES="JOR (col. N)",
         REGLA_OFICIAL="COD_JORNADA 1 Diurna, 2 Vespertina, 3 Semipresencial, 4 A distancia, 5 Otra. La jornada es componente del código unificado (J); "
                       "reglas de combinación jornada-modalidad por tipo de oferta.",
         FUENTE_OFICIAL=f"{INS_OA} (jornada, modalidad, Condición 1, Anexo 5); {INS_AC} Anexo I campo JORNADA; {MAN_MU} Cuadro N°1 col. N",
         DATO_U_PLUS=f"JORNADA {M['uplus_0508']['JORNADA_raw']} (valores con espacio final). Significado de 'O' no documentado por Bettersoft.",
         IMPLEMENTACION_HISTORICA=f"{COD}: O -> 4; PUENTE_SIES_COMPILADO: O -> J4 en {M['puente']['J_por_jornada_uplus']['O'].get('4', 0)} combinaciones y J3 en {M['puente']['J_por_jornada_uplus']['O'].get('3', 0)} (DCBS).",
         ARCHIVO_ENVIADO=f"Pares inequívocos U+ x carga PES 2026: {cr['JORNADA_uplus_x_pes']}; los O -> 2 tienen SITUACION {cr['JORNADA_O_a_2_situacion']} (cambio de jornada: la jornada vigente en U+ no es la informada). JOR x MODALIDAD cargado: {pes['JOR_x_MODALIDAD']}.",
         CONTRADICCION="O no produce un único código SIES.", TIPO_CONTRADICCION="Catálogo / temporalidad", EXISTE_CONTRADICCION="SI",
         RESOLUCION="JORNADA_U_PLUS_NO_ES_SUFICIENTE_PARA_DETERMINAR_COD_JORNADA_SIES. D -> 1 y V -> 2 quedan OBSERVADO. El código SIES se obtiene del componente J del CODIGO_UNICO de la matrícula en el período.",
         ACCION_DICCIONARIO="COD_JORNADA_SIES deja de homologarse desde JORNADA U+; se deriva de CODIGO_UNICO.",
         ACCION_BETTERSOFT="Entregar JORNADA U+ sin transformar y su historial por período (UP-25, UP-66); CODIGO_UNICO_SIES almacenado (UP-27).",
         ESTADO="RESUELTA", ESTADO_GATE09="NO_DETERMINABLE_DESDE_U_PLUS", NIVEL_RESPALDO="OFICIAL",
         EVIDENCIA=f"{INS_OA}; {PES_MU}; {UPLUS}; avance_curricular/control/catalogos/PUENTE_SIES_COMPILADO.tsv; {METR}", FUENTE_REQUERIDA="",
         IMPACTO="Riesgo de jornada incorrecta cuando hay cambio de jornada o programas con J3.", OBSERVACIONES="Ver hoja 05_JORNADA."),
    dict(ID_CONTRADICCION="C09-08", ID_V09="CT-08", PROCESO="Matrícula Unificada", SUBPROCESO="Pregrado y posgrado", AÑO_PROCESO="2026", AÑO_DATOS="2026",
         CAMPO_SIES="FECH_NAC (col. H)",
         REGLA_OFICIAL="Fecha dd/mm/aaaa; no puede ser menor a 01/01/1900 ni vacía; se rechaza un registro que resulte menor de 15 años.",
         FUENTE_OFICIAL=f"{MAN_MU} Cuadro N°1 col. H; Cuadro N°6", DATO_U_PLUS="FECHANACIMIENTO: 0 nulos en el snapshot 08-05-2026.",
         IMPLEMENTACION_HISTORICA="gobernanza_columnas_mu/gob_mu_fech_nac.tsv: fallback 01/01/1900.",
         ARCHIVO_ENVIADO=f"Carga PES 2026: {pes['FECH_NAC_1900']} filas con año 1900. Respuesta PES 07-05-2026 12:26: 2 registros rechazados por fecha de nacimiento que implica menos de 15 años (dato de origen).",
         CONTRADICCION="El fallback no se aplicó; la inconsistencia observada es de calidad del dato en U+.", TIPO_CONTRADICCION="Código", EXISTE_CONTRADICCION="NO en el archivo enviado",
         RESOLUCION="El fallback 01/01/1900 no es regla y no se usa. Una fecha faltante o inconsistente se corrige en U+.",
         ACCION_DICCIONARIO="Marcar fallback como implementación descartada.", ACCION_BETTERSOFT="Entregar la fecha real; no rellenar (UP-13).",
         ESTADO="RESUELTA", ESTADO_GATE09="RESUELTA_DATO_REAL", NIVEL_RESPALDO="OFICIAL + OBSERVADO",
         EVIDENCIA=f"{MAN_MU}; {PES_MU}; {PES_ERR2}", FUENTE_REQUERIDA="", IMPACTO="Bajo.", OBSERVACIONES=""),
    dict(ID_CONTRADICCION="C09-09", ID_V09="CT-09", PROCESO="Matrícula Unificada / Avance Curricular", SUBPROCESO="MU; AC Matrícula", AÑO_PROCESO="2026",
         AÑO_DATOS="2026 (MU) / 2025 (AC)", CAMPO_SIES="SEM_ING_ACT, SEM_ING_ORI (MU); SEM_INGRESO_CARRERA_* y CURSO_1ER/2DO_SEM (AC)",
         REGLA_OFICIAL="Semestre de ingreso: 1 o 2. No existe regla oficial para períodos trimestrales.",
         FUENTE_OFICIAL=f"{MAN_MU} Cuadro N°6; {INS_AC} Anexo II",
         DATO_U_PLUS=f"PERIODOMATRICULA {M['uplus_0508']['PERIODOMATRICULA']}; PERIODOINGRESO incluye 3; significado de 3 no documentado.",
         IMPLEMENTACION_HISTORICA="control/config_campos_ing.json: 3 -> semestre 2 (decisión interna).",
         ARCHIVO_ENVIADO="Semestres cargados en {1, 2} (aceptados); no prueba el significado del período 3.",
         CONTRADICCION="Se asigna un semestre a un período cuyo significado no está documentado.", TIPO_CONTRADICCION="Catálogo / temporalidad", EXISTE_CONTRADICCION="SI",
         RESOLUCION="PENDIENTE. 3 -> 2 queda como decisión interna, no regla.",
         ACCION_DICCIONARIO="Período 3 marcado PENDIENTE_FALTA_FUENTE.", ACCION_BETTERSOFT="Entregar período tal como está en U+ y el catálogo de períodos con fechas de inicio y término por régimen (UP-32, UP-68).",
         ESTADO="PENDIENTE", ESTADO_GATE09="PENDIENTE_FALTA_FUENTE", NIVEL_RESPALDO="INTERNO",
         EVIDENCIA=f"{MAN_MU}; {INS_AC}; {UPLUS}", FUENTE_REQUERIDA="Catálogo U+ de períodos académicos con fechas de inicio y término por régimen (Bettersoft).",
         IMPACTO="Semestre de ingreso y avance por semestre de estudiantes con períodos trimestrales. No afecta un requerimiento P1 (se pide el dato sin transformar).", OBSERVACIONES=""),
    dict(ID_CONTRADICCION="C09-10", ID_V09="CT-10", PROCESO="Matrícula Unificada", SUBPROCESO="Pregrado", AÑO_PROCESO="2026", AÑO_DATOS="2026",
         CAMPO_SIES="ANIO_ING_ORI / SEM_ING_ORI (col. S, T)",
         REGLA_OFICIAL="'Cuando la FORMA INGRESO CARRERA ACTUAL es 1, 2, 3, 6, 7, 8, 9 o 10, el AÑO INGRESO CARRERA ORIGEN no puede ser 1900'. 1900 con semestre 0 "
                       "es opción solo si el origen es externo o no identificable (Anexo N°7); en cambio externo debe ser 1900.",
         FUENTE_OFICIAL=f"{MAN_MU} §4 (p.9), Cuadro N°6 (p.38), Anexo N°7 (p.41)", DATO_U_PLUS="No existe año de origen en U+.",
         IMPLEMENTACION_HISTORICA="control/config_campos_ing.json: FOR 2 => ANIO_ING_ORI 1900.",
         ARCHIVO_ENVIADO=f"Respuesta PES 07-05-2026 12:19: {err_1900} líneas rechazadas por esa regla. Carga aceptada: FOR 2 con 1900 = {pes['FOR2_ANIO_ORI_1900']}.",
         CONTRADICCION="La configuración contradice una regla oficial.", TIPO_CONTRADICCION="Regla / código", EXISTE_CONTRADICCION="SI",
         RESOLUCION="Manda la regla oficial; la configuración FOR 2 => 1900 queda descartada.",
         ACCION_DICCIONARIO="Descartar la configuración; ANIO_ING_ORI desde trayectoria (UP-34 a UP-37).",
         ACCION_BETTERSOFT="Entregar año y semestre reales de ingreso al programa de origen; vacío si U+ no lo conoce (la institución aplica 1900/0).",
         ESTADO="RESUELTA", ESTADO_GATE09="RESUELTA_REGLA_OFICIAL", NIVEL_RESPALDO="OFICIAL",
         EVIDENCIA=f"{MAN_MU}; {PES_ERR}; {PES_MU}", FUENTE_REQUERIDA="", IMPACTO="Ninguno sobre la carga aceptada.", OBSERVACIONES=""),
    dict(ID_CONTRADICCION="C09-11", ID_V09="CT-11", PROCESO="Oferta Académica", SUBPROCESO="Etapas 1-3", AÑO_PROCESO="2026", AÑO_DATOS="Oferta 2027",
         CAMPO_SIES="Formato de archivo (delimitador, fecha)",
         REGLA_OFICIAL="El instructivo describe CSV delimitado por comas y fechas DD/MM/AAAA; las plantillas PES descargadas usan ';'.",
         FUENTE_OFICIAL=f"{INS_OA}; plantillas PES en requerimiento_bettersoft_uplus_2026/01_fuentes_oficiales/oferta_academica_2027/",
         DATO_U_PLUS="No aplica (Oferta no se alimenta del reporte de estudiantes U+).", IMPLEMENTACION_HISTORICA="Cargas con ';' (MAPA_ETAPAS).",
         ARCHIVO_ENVIADO=f"Plantilla PES: delimitador '{M['oferta']['delimitador_plantilla']}'.", CONTRADICCION="Texto del instructivo vs plantilla de la plataforma.",
         TIPO_CONTRADICCION="Formato", EXISTE_CONTRADICCION="SI (documental, fuera del alcance U+)",
         RESOLUCION="No aplica al requerimiento U+; se gobierna en el subproyecto oferta_academica_2027.",
         ACCION_DICCIONARIO="Sin cambios en campos U+.", ACCION_BETTERSOFT="Ninguna.", ESTADO="NO_APLICA", ESTADO_GATE09="NO_APLICA_AL_PROCESO",
         NIVEL_RESPALDO="OFICIAL (plantilla PES)", EVIDENCIA=f"{INS_OA}; 01_fuentes_oficiales/oferta_academica_2027/", FUENTE_REQUERIDA="", IMPACTO="Ninguno sobre U+.", OBSERVACIONES=""),
    dict(ID_CONTRADICCION="C09-12", ID_V09="CT-12", PROCESO="Oferta Académica", SUBPROCESO="Etapa 1 (Vigente Editada) y Etapa 2 (Nueva)", AÑO_PROCESO="2026", AÑO_DATOS="Oferta 2027",
         CAMPO_SIES="Estructura de carga",
         REGLA_OFICIAL=f"Plantilla PES oficial: {M['oferta']['columnas_plantilla_pes']} columnas.",
         FUENTE_OFICIAL="01_fuentes_oficiales/oferta_academica_2027/20260810_34992_Estructura_OA_1_TP_VIGENTE_EDITADA.csv y 20260810_63945_Estructura_OA_1_TP_NUEVA.csv",
         DATO_U_PLUS="No aplica.", IMPLEMENTACION_HISTORICA=f"CONTRATO_CAMPOS_ETAPA1: {M['oferta']['campos_contrato']} campos.",
         ARCHIVO_ENVIADO="Plantillas de 48 columnas.", CONTRADICCION="El contrato interno incluye campos que no están en la plantilla.",
         TIPO_CONTRADICCION="Estructura", EXISTE_CONTRADICCION="SI (documental)",
         RESOLUCION=f"Rigen las 48 columnas de la plantilla PES. Los campos {', '.join(M['oferta']['campos_contrato_fuera_de_plantilla'])} son internos del contrato.",
         ACCION_DICCIONARIO="Marcar esas 4 filas de la matriz como NO_APLICA_ESTRUCTURA_PES.", ACCION_BETTERSOFT="Ninguna.",
         ESTADO="RESUELTA", ESTADO_GATE09="RESUELTA_REGLA_OFICIAL", NIVEL_RESPALDO="OFICIAL (plantilla PES)",
         EVIDENCIA="01_fuentes_oficiales/oferta_academica_2027/; avance_curricular/oferta_academica_2027/11_gobernanza/CONTRATO_CAMPOS_ETAPA1_OFERTA_ACADEMICA_2027.tsv",
         FUENTE_REQUERIDA="", IMPACTO="Ninguno sobre U+.", OBSERVACIONES=""),
    dict(ID_CONTRADICCION="C09-13", ID_V09="CT-13", PROCESO="Matrícula Unificada", SUBPROCESO="Pregrado", AÑO_PROCESO="2022-2026", AÑO_DATOS="2022-2026",
         CAMPO_SIES="Estructura (FECHA_MATRICULA, REINCORPORACION)",
         REGLA_OFICIAL="Manual MU 2026: 32 columnas. Manuales 2022-2023 no están en el repositorio.",
         FUENTE_OFICIAL=f"{MAN_MU} Anexo 7 Cuadro N°1", DATO_U_PLUS="No aplica.", IMPLEMENTACION_HISTORICA="Base de retención MU 2022-2026 mapea 30/32 columnas en 2022-2023.",
         ARCHIVO_ENVIADO=f"Archivos enviados 2022-2023 sin FECHA_MATRICULA ni REINCORPORACION; 2024-2026 con 32 columnas ({HIST}).",
         CONTRADICCION="La estructura cambió entre años.", TIPO_CONTRADICCION="Temporalidad", EXISTE_CONTRADICCION="NO (diferencia legítima entre años)",
         RESOLUCION="Diferencia estructural real entre procesos anuales. El requerimiento a Bettersoft pide hechos independientes del año; la estructura de cada año la aplica la institución.",
         ACCION_DICCIONARIO="Sin cambio; documentado.", ACCION_BETTERSOFT="Ninguna.", ESTADO="RESUELTA", ESTADO_GATE09="RESUELTA_DATO_REAL",
         NIVEL_RESPALDO="OBSERVADO (archivos enviados)", EVIDENCIA=HIST, FUENTE_REQUERIDA="Manuales MU 2022 y 2023 (solo para reconstrucción histórica; no bloquea).",
         IMPACTO="Solo reconstrucción histórica.", OBSERVACIONES=""),
]

CADENA = {
    r["ID_CONTRADICCION"]: [("1 REGLA OFICIAL", r["REGLA_OFICIAL"], r["FUENTE_OFICIAL"]), ("2 DATO U+", r["DATO_U_PLUS"], UPLUS),
                            ("3 IMPLEMENTACIÓN HISTÓRICA", r["IMPLEMENTACION_HISTORICA"], ""), ("4 ARCHIVO REALMENTE ENVIADO", r["ARCHIVO_ENVIADO"], ""),
                            ("5 RESULTADO", r["CONTRADICCION"], ""), ("6 CONCLUSIÓN", r["RESOLUCION"], r["ESTADO_GATE09"])]
    for r in REG}

# ---------------------------------------------------------------- 9.5 cruces
def sx(k):
    return cr["SEXO_uplus_x_pes"].get(k, 0)


def jr(k):
    return cr["JORNADA_uplus_x_pes"].get(k, 0)


def sd(k):
    return cr["SEDE_uplus_x_pes"].get(k, 0)


NO_DOC = "No documentado por Bettersoft (inferido)"
CRUCES = [
    ("SEXO", "M", NO_DOC + ": hombre", "MU/Ext: H · AC/FCU: H", "M -> H", f"Carga PES 2026: {sx('M|H')}/{sx('M|H')} pares", "OBSERVADO", "Falta significado U+ documentado."),
    ("SEXO", "F", NO_DOC + ": mujer", "MU/Ext: M · AC/FCU: M", "F -> M (inversión de letra)", f"Carga PES 2026: {sx('F|M')}/{sx('F|M')} pares", "OBSERVADO", "Riesgo de inversión: 'M' significa hombre en U+ y mujer en SIES."),
    ("SEXO", "S", "Sin significado documentado", "MU/Ext: NB · AC/FCU: X (implementado)", "S -> NB (implementación)", f"Carga PES 2026: {sx('S|NB')} pares; {M['ct04']['pes_NB']} NB en total", "PENDIENTE", "C09-05."),
    ("SEDE", "RE", NO_DOC + ": Casa Central (Santiago)", "2 (CASA CENTRAL (SANTIAGO), precarga 5810)", "RE -> 2", f"Carga PES 2026: {sd('RE|2')}/{sd('RE|2')} pares", "OBSERVADO", "El código SIES de sede es el componente S del CODIGO_UNICO."),
    ("SEDE", "CO", NO_DOC + ": Concepción", "3 (SEDE CONCEPCION, reporte 5769)", "CO -> 3", f"Carga PES 2026: {sd('CO|3')}/{sd('CO|3')} pares", "OBSERVADO", "Idem."),
    ("JORNADA", "D", NO_DOC + ": diurna", "1", "D -> 1", f"Carga PES 2026: {jr('D|1')}/{jr('D|1')}; PUENTE 22/22", "OBSERVADO", "Derivar de CODIGO_UNICO (J)."),
    ("JORNADA", "V", NO_DOC + ": vespertina", "2", "V -> 2", f"Carga PES 2026: {jr('V|2')}/{jr('V|2')}; PUENTE 44/44", "OBSERVADO", "Derivar de CODIGO_UNICO (J)."),
    ("JORNADA", "O", "Sin significado documentado", "4 / 3 / 2", "O -> 4 (implementación)", f"Carga PES 2026: O->4 {jr('O|4')}, O->2 {jr('O|2')}; PUENTE O->J3 1", "NO_DETERMINABLE", "C09-07."),
    ("NACIONALIDAD", f"{cr['NACIONALIDAD_valores'] - 1} valores de texto", "Gentilicio en texto libre", "Cuadro N°4 (1-197)", "gobernanza_nac.tsv",
     f"Carga PES 2026: {cr['NACIONALIDAD_valores_con_mas_de_un_codigo']} valores con más de un código", "OBSERVADO", "Sin catálogo de país en U+."),
    ("NACIONALIDAD", "Por definir", "Sin dato", "38 en la carga 2026", "Por definir -> 38 (default)", f"{cr['NACIONALIDAD_por_definir_a_38']} par(es); {M['uplus_0508']['NACIONALIDAD_por_definir']} filas U+", "DEFAULT_TECNICO", "No es regla: debe completarse en U+."),
    ("ESCALA_NOTAS", "1,0 a 7,0", NO_DOC + ": nota final", "0 o 100-700", "x100; 0 si no cursó",
     f"PROM_PRI_SEM fuera de rango: {M['escala_notas']['PROM_PRI_SEM']['fuera_rango']}; PROM_SEG_SEM: {M['escala_notas']['PROM_SEG_SEM']['fuera_rango']}", "OBSERVADO", "El rango es oficial; el factor x100 es implementación."),
    ("PERIODO", "1 / 2", NO_DOC, "Semestre 1 / 2", "1 -> 1; 2 -> 2", "Semestres cargados en {1, 2}", "OBSERVADO", "Requiere catálogo de períodos con fechas."),
    ("PERIODO", "3", "Sin significado documentado", "—", "3 -> 2 (decisión interna)", "No verificable en el archivo", "PENDIENTE", "C09-09."),
]
CRUCES_COLS = ["CATALOGO", "VALOR_U_PLUS", "SIGNIFICADO_U_PLUS", "VALOR_SIES", "REGLA_TRANSFORMACION", "ARCHIVO_FINAL_O_SCRIPT", "CLASIFICACION_GATE09", "MOTIVO"]

SEXO_PROC = [
    ("U+", "DatosAlumnos", "M / F / S", "M, F sin documentación; S sin significado", "Fuente", "SEXO_U_PLUS_RAW; S PENDIENTE"),
    ("Matrícula Unificada 2026", "Cuadro N°1 col. G / Cuadro N°2", "H / M / NB", "Oficial", MAN_MU, "Transformación institucional desde RAW"),
    ("Estudiantes Extranjeros 2026 (regulares e intercambio)", "Anexo I campo G; Anexo V", "H / M / NB", "Oficial", INS_EX, "Transformación institucional desde RAW"),
    ("Avance Curricular 2026 (Matrícula)", "Anexo II campo SEXO", "H / M / X", "Oficial; dato precargado no modificable", INS_AC, "No se obtiene de U+"),
    ("FCU 2026", "Variable SEXO", "H / M / X (según catálogo v0.9)", "Oficial", "Manual_de_Aplicacion_FCU_2026.txt (referenciado)", "Transformación institucional desde RAW"),
]
JORNADA = [
    ("D", jr("D|1"), "1", "22/22 combinaciones -> J1", "OBSERVADO", "CODIGO_UNICO (J)"),
    ("V", jr("V|2"), "2", "44/44 combinaciones -> J2", "OBSERVADO", "CODIGO_UNICO (J)"),
    ("O", jr("O|4") + jr("O|2"), f"4 ({jr('O|4')}), 2 ({jr('O|2')}, SITUACION 49)", "94 combinaciones -> J4; 1 -> J3 (DCBS)", "NO_DETERMINABLE", "CODIGO_UNICO (J) + historial de jornada por período"),
]
COD_UNICO = [
    ("Definición oficial", "Código unificado = institución + sede + carrera + jornada + versión (ISCJV). Usado por Mineduc en todos sus procesos.", f"{INS_OA} (definiciones; Anexo 5)"),
    ("Llave de validación MU", "'La combinación entre institución, sede, carrera, jornada, modalidad y versión no existe en Oferta Académica 2026' (Cuadro N°6).", MAN_MU),
    ("Hallazgo U+", f"{M['puente']['combinaciones']} combinaciones JORNADA+CODCARPR+NOMBRE_L; {M['puente']['ambiguas']} ambiguas. Las ambiguas difieren solo en: {M['puente']['ambiguas_difieren_en']} (S, C, J, V).", "control/catalogos/PUENTE_SIES_COMPILADO.tsv"),
    ("Conclusión", "CARRERA + SEDE + JORNADA no basta: falta la VERSIÓN, que U+ no registra. La modalidad, duración, tipo de plan y nivel se expresan en la versión.", ""),
    ("REQUERIMIENTO", "ALMACENAR_CODIGO_UNICO_SIES", ""),
    ("PRIORIDAD", "P1", ""), ("TIPO", "MAESTRO_REGULATORIO", ""), ("GRANULARIDAD", "OFERTA_ACADEMICA (atributo del programa/plan U+, asignado a cada matrícula por período)", ""),
    ("HISTORIZABLE", "SI (vigencia desde/hasta por año de oferta)", ""),
    ("Mantención: cambio de sede o de jornada", "Siempre cambia el código unificado (nuevo S o J): nuevo registro en el maestro; el anterior se cierra.", f"{INS_OA} Anexo 5"),
    ("Mantención: cambio de modalidad, duración, tipo de plan o nivel", "Cambia la versión (V) y por tanto el código: nuevo registro; el anterior se cierra.", f"{INS_OA} Anexo 5"),
    ("Mantención: cambio de plan de estudios sin cambio de atributos", "No cambia el código (cambio curricular); el plan U+ se asocia al mismo código.", f"{INS_OA} Anexo 5"),
    ("Mantención: cambio de nombre", "Sujeto a evaluación de SIES (oficio); U+ registra el código que resulte.", f"{INS_OA} Anexo 5"),
    ("Mantención: estado de la oferta", "El programa antiguo queda con vigencia 2 y el nuevo con vigencia 1 en Oferta; U+ debe conservar ambos códigos con sus fechas.", f"{INS_OA} Anexo 5"),
    ("Quién asigna el código", "La institución, desde la Oferta Académica aceptada por SIES. Bettersoft provee el campo y su historia; no calcula el código.", ""),
]
HISTORIAL = [
    ("VIG (MU)", "Estado de la matrícula al 30-04 (pregrado) o 15-05 (posgrado)", "ESTADOACADEMICO/SITUACION vigentes al descargar", "Sin fecha de inicio/fin del estado", "UP-43, UP-39, UP-40"),
    ("Estado académico y situación", "A la fecha de corte de cada proceso", "Solo estado vigente", "Sin historial", "UP-43"),
    ("Matrícula del período", "Año/período y fecha de matrícula del período informado", "ANOMATRICULA/PERIODOMATRICULA/FECHAMATRICULA (temporalidad no documentada)", "FECHAMATRICULA coincide con ANOMATRICULA en 76,3%", "UP-39, UP-40, UP-66"),
    ("SUS_PRE (MU)", "Semestres suspendidos antes del año del proceso", "Situación vigente", f"Constante 0 desde 2024 (≠0 por año: {hist_sus})", "UP-43"),
    ("REINCORPORACION (MU)", "Suspensión en 1er semestre y reincorporación en 2º del año", "Situación 38 vigente", "Sin fechas", "UP-43"),
    ("Jornada", "Jornada de la matrícula en el período informado", "Jornada vigente", f"{jr('O|2')} casos con jornada U+ distinta a la informada (SITUACION 49)", "UP-25, UP-66"),
    ("Carrera / código único", "Programa en que estaba matriculado en el período (y el año anterior para cambio interno)", "Programa vigente", "Sin código único ni historia", "UP-27, UP-66"),
    ("Sede", "Sede del período", "Sede vigente", "Sin historia", "UP-23, UP-66"),
    ("Plan de estudios", "Plan vigente en el año de referencia (AC)", "Solo en reporte de notas", "Sin historia en el reporte de matrícula", "UP-28, UP-66"),
    ("Forma de ingreso", "Hecho del ingreso al programa (fijo)", "No existe", "Se infería desde situación vigente y nombre", "UP-63, UP-64, UP-34 a UP-37"),
    ("Cambios de carrera", "Fecha y programas de origen/destino", "SITUACION 24 vigente", "Sin vínculo con la matrícula de origen", "UP-34, UP-43"),
    ("Cambios de jornada", "Fecha y jornadas de origen/destino", "SITUACION 49/27 vigente", "Sin fecha ni jornada anterior", "UP-43, UP-66"),
    ("Períodos cursados", "Semestres con actividad en el año de referencia (AC)", "Reporte de notas por año/período", "Período 3 sin significado", "UP-62, UP-68"),
    ("Nivel académico", "Nivel a la fecha de corte", "NIVEL vigente", "Sin historia; NIVEL 20 sin definición", "UP-41, UP-66"),
    ("Egreso y titulación", "Fecha de egreso y de titulación (VIG 2)", "Estado EGRESADO/TITULADO vigente", "Sin fechas", "UP-59, UP-60"),
]
PAIS = [
    ("MU 2026 (carga PES)", f"{pes['PAIS_EST_SEC']}", f"{pes['NAC_distinta_38']} filas con nacionalidad extranjera", "DEFAULT_TECNICO"),
    ("MU 2022-2025 (enviadas)", f"PAIS = NAC en extranjeros ({hist_pais})", "Copia de nacionalidad", "SUPUESTO"),
    ("Extranjeros 2026, 1ª carga", f"PAIS = NAC {ext['PAIS_EST_SEC_igual_NAC']}; 38 {ext['PAIS_EST_SEC_38']} de {ext['filas']}", "Copia de nacionalidad o Chile", "SUPUESTO"),
    ("U+ DatosAlumnos", "Sin campo de país; colegio y comuna del colegio en texto", "—", "DATO_FALTANTE"),
    ("Otro sistema institucional", "No se encontró en el repositorio", "—", "DATO_FALTANTE"),
]

# ---------------------------------------------------------------- matriz: filas afectadas
PEND = "PENDIENTE_DATOS_ELEMENTALES"
MAT = {}
for ids, v in [
    (("MM-032", "MM-053"), ("ESTADOACADEMICO/SITUACION -> VIG (tablas internas: TITULADO -> 2 / TITULADO -> 0)", "TITULADO_NO_DETERMINA_VIGENCIA_SIES; ningún estado vigente U+ determina VIG",
                            "Cálculo institucional: matrícula del período a la fecha de corte + historial de estado con fechas + fechas de egreso y titulación", PEND, "C09-01")),
    (("MM-016", "MM-048"), ("SITUACION 49/27 -> 3; nombre 'CONTINUIDAD' -> 2; VIASDEADMISION -> 1/6/10/11", "IMPLEMENTACION_NO_RESPALDADA_POR_REGLA_OFICIAL (C09-02); NOMBRE_PROGRAMA_NO_DETERMINA_FORMA_INGRESO (C09-03)",
                            "Cálculo institucional desde: vía de admisión y cupo, tipo de origen, tipo de programa de origen, CODCLI_ORIGEN y código de carrera de origen/actual, años de ingreso, reconocimiento de acceso", PEND, "C09-02; C09-03")),
    (("MM-019", "MM-051"), ("config: FOR 2 => 1900", "Descartado: Cuadro N°6 prohíbe 1900 con FOR 1, 2, 3, 6-10", "Año real de ingreso al programa de origen (trayectoria); 1900 solo con FOR 4, 5 u 11 y origen externo o no identificable", PEND, "C09-10")),
    (("MM-020", "MM-052"), ("config: FOR 2 => semestre 0; período 3 -> 2", "C09-10 (1900/0) y C09-09 (período 3 PENDIENTE)", "Semestre real de ingreso al programa de origen; 0 solo con 1900", PEND, "C09-09; C09-10")),
    (("MM-018", "MM-050"), ("PERIODOINGRESO 1->1, 2->2, 3->2", "1 y 2 OBSERVADO; 3 PENDIENTE_FALTA_FUENTE", "Período U+ + fechas del período; semestre por regla institucional", "OBSERVADO; 3 PENDIENTE", "C09-09")),
    (("MM-028",), ("Constante 1 (código)", "0 = No aplica para IPSS (código oficial 0 + rechazo PES por tipo de institución)", "Constante institucional 0; no se solicita a U+", "RESUELTA_DATO_REAL", "C09-04")),
    (("MM-007", "MM-039"), ("M->H; F->M; S->NB", "M->H y F->M OBSERVADO; S->NB descartado como regla", "SEXO_U_PLUS_RAW + transformación institucional documentada (H/M/NB); S PENDIENTE", "OBSERVADO; S PENDIENTE_FALTA_FUENTE", "C09-05")),
    (("MM-102", "MM-119"), ("M->H; F->M; S->NB", "Catálogo oficial Extranjeros 2026: H/M/NB (Instructivo Extranjeros 2026, Anexo I campo G)", "SEXO_U_PLUS_RAW + transformación institucional; S PENDIENTE", "OBSERVADO; S PENDIENTE_FALTA_FUENTE", "C09-05")),
    (("MM-081",), ("M->H; F->M", "Dato precargado no modificable (Instructivo AC 2026, Anexo II); códigos H/M/X", "No se obtiene de U+", "RESUELTA_REGLA_OFICIAL", "C09-05")),
    (("MM-141",), ("M->H; F->M; S->X", "S sin significado demostrado", "SEXO_U_PLUS_RAW + transformación institucional; S PENDIENTE", "OBSERVADO; S PENDIENTE_FALTA_FUENTE", "C09-05")),
    (("MM-010", "MM-042"), ("Comuna del colegio -> Chile; fallback 38", "2026 DEFAULT_TECNICO; 2022-2025 SUPUESTO (copia de NAC); U+ DATO_FALTANTE", "Nuevo dato U+: país de la licencia de enseñanza media", "NO_DETERMINABLE_DESDE_U_PLUS", "C09-06")),
    (("MM-107",), ("Copia de NACIONALIDAD o 38", "SUPUESTO; U+ DATO_FALTANTE", "Nuevo dato U+: país de la licencia de enseñanza media", "NO_DETERMINABLE_DESDE_U_PLUS", "C09-06")),
    (("MM-014", "MM-046"), ("D->1; V->2; O->4", "JORNADA_U_PLUS_NO_ES_SUFICIENTE_PARA_DETERMINAR_COD_JORNADA_SIES", "Componente J del CODIGO_UNICO de la matrícula en el período", "NO_DETERMINABLE_DESDE_U_PLUS", "C09-07")),
    (("MM-011", "MM-043"), ("RE->2; CO->3", "OBSERVADO (consistente en carga aceptada)", "Componente S del CODIGO_UNICO", "OBSERVADO", "9.5")),
    (("MM-012", "MM-044", "MM-015", "MM-047"), ("Inferencia por JORNADA+CODCARPR+NOMBRE_L (PUENTE)", "Ambigüedad solo en VERSIÓN (70/161); llave oficial ISCJV",
                                                "Desde CODIGO_UNICO_SIES almacenado en U+ (maestro de oferta historizable)", PEND, "9.8")),
    (("MM-013", "MM-045"), ("Inferencia desde jornada", "Modalidad es atributo de la versión del programa (Anexo 5)", "Atributo del maestro de oferta asociado al CODIGO_UNICO", PEND, "9.8")),
    (("MM-008", "MM-040"), ("Fallback 01/01/1900", "Fallback descartado; no usado en la carga aceptada", "Fecha real U+; faltante se corrige en U+", "RESUELTA_DATO_REAL", "C09-08")),
    (("MM-029",), ("Constante 0", "Requiere historial con fechas", "Cálculo institucional desde historial de estados", PEND, "9.9")),
    (("MM-031",), ("Constante 0", "Requiere historial con fechas", "Cálculo institucional desde historial de estados", PEND, "9.9")),
    (("MM-009", "MM-041"), ("gobernanza_nac.tsv; 'Por definir' -> 38", "Gentilicios OBSERVADO; 'Por definir' -> 38 DEFAULT_TECNICO", "NACIONALIDAD U+ + homologación institucional; 'Por definir' se corrige en U+", "OBSERVADO", "9.5")),
    (("MM-115",), ("Significado pendiente", "Oficial: 0 Eliminar registro / 1 Mantener registro; no es vigencia académica", "No se solicita a U+", "RESUELTA_REGLA_OFICIAL", "9.11")),
    (("MM-105", "MM-121"), ("Sin catálogo", "Oficial: 1 con residencia previa, 2 sin residencia previa, 3 no reside en Chile", "Nuevo dato U+ (UP-17)", "PENDIENTE_DATO_UPLUS", "9.11")),
    (("MM-074", "MM-095"), ("—", "Oficial: 0 Eliminar / 1 Mantener registro; todos los registros vigentes (1) aunque se retiren después del 30-04", "No se solicita a U+", "RESUELTA_REGLA_OFICIAL", "9.11")),
    (("MM-058",), ("—", "Dato precargado no modificable (Instructivo AC 2026, Anexo I)", "No se obtiene de U+", "RESUELTA_REGLA_OFICIAL", "9.11")),
    (("MM-188", "MM-189", "MM-190", "MM-196"), ("Contrato Etapa 1 (52 campos)", "No forma parte de la plantilla PES (48 columnas)", "—", "NO_APLICA_ESTRUCTURA_PES", "C09-12")),
]:
    for i in ids:
        MAT[i] = v

# ---------------------------------------------------------------- diccionario Bettersoft
SOL, MAE, NOC, NOS = "SOLICITAR_HECHO", "SOLICITAR_MAESTRO", "NO_CALCULAR_EN_UPLUS", "NO_SOLICITAR"
OF = "OFICIAL"
MU_C1 = "Manual MU 2026, Anexo 7 Cuadro N°1"
# ID: (accion, prioridad, respaldo, nivel, disponibilidad, resolucion, cambios)
DIC = {
    "UP-01": (SOL, "P1", f"{MU_C1}: un registro por estudiante y programa (duplicidad válida si cursa más de un programa, nota 2 p.17)", OF, "EXISTE", "Sin cambio", {}),
    "UP-02": (SOL, "P4", "Trazabilidad interna", "OBSERVADO", "POR_CONFIRMAR", "Sin cambio", {}),
    "UP-03": (SOL, "P1", f"{MU_C1} col. A (R/P); Instructivo Extranjeros 2026 Anexo I; Instructivo AC 2026 Anexo II", OF, "POR_CONFIRMAR", "Sin cambio", {}),
    "UP-04": (NOC, "NO_APLICA_BETTERSOFT", f"{MU_C1} col. A", OF, "—", "Código SIES derivado por la institución desde UP-03", {"TRANSFORMACIÓN": "Institucional: RUN -> R; Pasaporte -> P"}),
    "UP-05": (SOL, "P2", f"{MU_C1} col. B", OF, "EXISTE", "Sin cambio", {}),
    "UP-06": (SOL, "P2", f"{MU_C1} col. C", OF, "EXISTE", "Sin cambio", {}),
    "UP-07": (SOL, "P3", f"{MU_C1} col. F", OF, "EXISTE", "Sin cambio", {}),
    "UP-08": (SOL, "P3", f"{MU_C1} col. D", OF, "EXISTE", "Sin cambio", {}),
    "UP-09": (SOL, "P3", f"{MU_C1} col. E", OF, "EXISTE", "Sin cambio", {}),
    "UP-10": (SOL, "P2", f"{MU_C1} col. G; Instructivo Extranjeros 2026 Anexo I campo G", OF, "EXISTE", "C09-05: RAW obligatorio; significado de cada código a documentar (UP-68)",
              {"TRANSFORMACIÓN": "Ninguna: entregar el código U+ sin transformar", "ESTADO": "OBSERVADO M/F; PENDIENTE S"}),
    "UP-11": (NOC, "NO_APLICA_BETTERSOFT", f"{MU_C1} col. G", OF, "—", "C09-05: SEXO SIES se deriva por proceso en la institución (MU/Ext H/M/NB; AC/FCU H/M/X)",
              {"TRANSFORMACIÓN": "Institucional por proceso; S pendiente", "ESTADO": "OBSERVADO M/F; PENDIENTE S"}),
    "UP-13": (SOL, "P3", f"{MU_C1} col. H; Cuadro N°6", OF, "EXISTE", "C09-08: sin relleno 01/01/1900", {"TRANSFORMACIÓN": "Formato dd/mm/aaaa; sin relleno si falta"}),
    "UP-14": (SOL, "P2", f"{MU_C1} col. I", OF, "EXISTE", "'Por definir' debe corregirse en U+", {}),
    "UP-15": (NOC, "NO_APLICA_BETTERSOFT", f"{MU_C1} col. I; Cuadro N°4", OF, "—", "Homologación institucional (OBSERVADO); 'Por definir' -> 38 es default, no regla",
              {"ESTADO": "OBSERVADO"}),
    "UP-16": (SOL, "P1", f"{MU_C1} col. J; Instructivo Extranjeros 2026 §d y Anexo I campo L", OF, "NO_EXISTE", "C09-06: hoy default 38 o copia de nacionalidad",
              {"DEFINICIÓN FUNCIONAL": "País donde la persona completó y aprobó la enseñanza media (licencia de EM), registrado en la admisión. Código 1-197 (Cuadro N°4) o nombre del país.",
               "CAMPO U+ ACTUAL": "(no existe)", "TRANSFORMACIÓN": "Nuevo dato; sin valor por defecto", "ESTADO": "NO_DETERMINABLE_DESDE_U_PLUS"}),
    "UP-17": (SOL, "P2", "Instructivo Extranjeros 2026 Anexo I campo J (1 con residencia previa, 2 sin residencia previa, 3 no reside en Chile)", OF, "NO_EXISTE",
              "Catálogo oficial incorporado", {"TRANSFORMACIÓN": "Nuevo dato con catálogo oficial 1/2/3", "ESTADO": "Catálogo oficial confirmado"}),
    "UP-18": (SOL, "P2", "Instructivo Extranjeros 2026 Anexo I campo K", OF, "NO_EXISTE", "Sin cambio", {}),
    "UP-19": (SOL, "P3", "Manual FCU 2026", OF, "EXISTE", "Se entrega el valor U+; el código FCU es homologación institucional",
              {"CAMPO SOLICITADO": "ESTADO_CIVIL_UPLUS", "TRANSFORMACIÓN": "Ninguna", "TIPO_OBTENCION": "A - Directo U+"}),
    "UP-20": (SOL, "P3", "Manual FCU 2026", OF, "EXISTE (texto único)", "Sin cambio", {}),
    "UP-21": (SOL, "P3", "Manual FCU 2026", OF, "EXISTE", "Se entrega el valor U+; el código de comuna es homologación institucional",
              {"CAMPO SOLICITADO": "COMUNA_RESIDENCIA_UPLUS", "TRANSFORMACIÓN": "Ninguna", "TIPO_OBTENCION": "A - Directo U+"}),
    "UP-22": (SOL, "P4", "Manual FCU 2026 (precarga)", OF, "EXISTE", "Sin cambio", {}),
    "UP-23": (SOL, "P2", f"{MU_C1} col. K", OF, "EXISTE", "Sede SIES = componente S del CODIGO_UNICO; RE/CO OBSERVADO",
              {"CAMPO SOLICITADO": "SEDE_UPLUS", "TRANSFORMACIÓN": "Ninguna (el código SIES de sede sale del CODIGO_UNICO)", "TIPO_OBTENCION": "A - Directo U+", "ESTADO": "OBSERVADO"}),
    "UP-24": (SOL, "P2", f"{MU_C1} col. L (vía código único)", OF, "EXISTE", "Sin cambio", {}),
    "UP-25": (SOL, "P2", f"{MU_C1} col. N (vía código único)", OF, "EXISTE", "C09-07: JORNADA U+ no determina COD_JORNADA; se entrega sin transformar y con historia por período",
              {"CAMPO SOLICITADO": "JORNADA_UPLUS", "TRANSFORMACIÓN": "Ninguna (sin espacios); el código SIES sale del CODIGO_UNICO", "TIPO_OBTENCION": "A - Directo U+",
               "ESTADO": "D/V OBSERVADO; O NO_DETERMINABLE"}),
    "UP-26": (MAE, "P1", f"{MU_C1} col. M; Cuadro N°6 (combinación sede-carrera-jornada-modalidad-versión); Instructivo Oferta 2027 (modalidad, tipos de plan, Anexo 5)", OF, "NO_EXISTE",
              "9.8: atributos del programa según Oferta, parte del maestro del código único",
              {"CAMPO SOLICITADO": "ATRIBUTOS_OFERTA: MODALIDAD, TIPO_PLAN (regular / especial / regular de continuidad), NIVEL_CARRERA, DURACION_ESTUDIOS",
               "DEFINICIÓN FUNCIONAL": "Atributos oficiales del programa en la Oferta Académica aceptada por SIES, almacenados junto al CODIGO_UNICO_SIES y con su vigencia.",
               "TRANSFORMACIÓN": "Ninguna: dato maestro cargado por la institución", "ESTADO": "PENDIENTE_DATO_UPLUS"}),
    "UP-27": (MAE, "P1", f"Instructivo Oferta 2027: definición de código unificado y Anexo 5; {MU_C1} col. K-O; Instructivo AC 2026 y Extranjeros 2026 (CODIGO_UNICO)", OF, "NO_EXISTE",
              "9.8: ALMACENAR_CODIGO_UNICO_SIES; P1; MAESTRO_REGULATORIO; granularidad OFERTA_ACADEMICA; historizable",
              {"TRANSFORMACIÓN": "Ninguna: dato maestro asignado por la institución desde la Oferta Académica; historizado", "ESTADO": "PENDIENTE_DATO_UPLUS"}),
    "UP-28": (SOL, "P1", "Instructivo AC 2026 Anexo I-II (PLAN_ESTUDIOS)", OF, "EXISTE (reporte de notas)", "Dato U+ que debe exponerse en el reporte de matrícula",
              {"TRANSFORMACIÓN": "Ninguna", "TIPO_OBTENCION": "A - Directo U+"}),
    "UP-29": (MAE, "P2", "Instructivo AC 2026 Anexo I (PLAN_ESTUDIOS, filas por plan vigente)", OF, "NO_EXISTE", "Sin cambio", {}),
    "UP-30": (SOL, "P2", f"{MU_C1} col. AA (nivel en semestres)", OF, "EXISTE (reporte de notas)", "Catálogo de régimen a documentar (UP-68)",
              {"ESTADO": "Catálogo pendiente (UP-68)", "TRANSFORMACIÓN": "Ninguna", "TIPO_OBTENCION": "A - Directo U+"}),
    "UP-31": (SOL, "P2", f"{MU_C1} col. Q", OF, "EXISTE", "Sin cambio", {}),
    "UP-32": (SOL, "P2", f"{MU_C1} col. R", OF, "EXISTE", "C09-09: período 3 pendiente; se entrega el período sin transformar",
              {"CAMPO SOLICITADO": "PERIODO_INGRESO_UPLUS", "TRANSFORMACIÓN": "Ninguna; semestre SIES por regla institucional con el catálogo de períodos (UP-68)",
               "TIPO_OBTENCION": "A - Directo U+", "ESTADO": "1/2 OBSERVADO; 3 PENDIENTE"}),
    "UP-33": (NOC, "NO_APLICA_BETTERSOFT", f"{MU_C1} col. P; Cuadro N°3", OF, "—", "C09-02 y C09-03: FOR_ING_ACT no se calcula en U+; se reemplaza por hechos UP-63, UP-64, UP-65 y trayectoria",
              {"TRANSFORMACIÓN": "Institucional", "ESTADO": "Reemplazado por datos elementales"}),
    "UP-34": (SOL, "P1", f"{MU_C1} col. P y S-T; Manual MU §2.iv, §4, Cuadro N°3", OF, "NO_EXISTE", "Sin cambio", {}),
    "UP-35": (SOL, "P1", "Manual MU 2026 §4 y Cuadro N°3 (misma institución / otra institución)", OF, "NO_EXISTE", "Sin cambio", {}),
    "UP-36": (SOL, "P1", f"{MU_C1} col. S; Cuadro N°6; Anexo N°7", OF, "NO_EXISTE", "C09-10: sin 1900 por defecto",
              {"TRANSFORMACIÓN": "Año real; vacío si U+ no lo conoce (la institución aplica 1900)"}),
    "UP-37": (SOL, "P1", f"{MU_C1} col. T; Cuadro N°6", OF, "NO_EXISTE", "C09-10", {"TRANSFORMACIÓN": "Semestre real; vacío si U+ no lo conoce (la institución aplica 0)"}),
    "UP-38": (SOL, "P3", "Instructivo Extranjeros 2026 Anexo I (NOMBRE/PAIS_UNIVERSIDAD_ORIGEN)", OF, "EXISTE (texto libre parcial)", "Sin cambio", {}),
    "UP-39": (SOL, "P2", f"{MU_C1} col. AD", OF, "EXISTE (temporalidad no documentada)", "Dato U+ por período; definición temporal a documentar (UP-68)",
              {"TRANSFORMACIÓN": "Ninguna", "TIPO_OBTENCION": "A - Directo U+"}),
    "UP-40": (SOL, "P2", "Manual MU 2026 (fecha de corte 30 de abril)", OF, "EXISTE", "Sin cambio", {}),
    "UP-41": (SOL, "P2", f"{MU_C1} col. AA", OF, "EXISTE", "Conversión a semestres es cálculo institucional",
              {"CAMPO SOLICITADO": "NIVEL_ACADEMICO_UPLUS", "TRANSFORMACIÓN": "Ninguna; conversión institucional con régimen del plan", "TIPO_OBTENCION": "A - Directo U+"}),
    "UP-42": (SOL, "P1", f"{MU_C1} col. AF (VIG requiere estado); Instructivo AC 2026 (vigencia)", OF, "EXISTE", "Sin cambio", {}),
    "UP-43": (SOL, "P1", f"{MU_C1} cols. AC, AE, AF; texto de suspensiones (p.17); definición de estudiante en proceso terminal (p.7)", OF, "POR_CONFIRMAR", "9.9: base de VIG, SUS_PRE, REINCORPORACION y cambios", {}),
    "UP-44": (NOC, "NO_APLICA_BETTERSOFT", f"{MU_C1} col. AC", OF, "—", "9.9: cálculo institucional desde UP-43", {"TRANSFORMACIÓN": "Institucional desde UP-43"}),
    "UP-45": (NOC, "NO_APLICA_BETTERSOFT", f"{MU_C1} col. AE", OF, "—", "9.9: cálculo institucional desde UP-43", {"TRANSFORMACIÓN": "Institucional desde UP-43"}),
    **{f"UP-{n}": (NOC, "NO_APLICA_BETTERSOFT", f"{MU_C1} cols. U-Z", OF, "—", "Cálculo institucional desde el detalle por asignatura (UP-62)",
                   {"TRANSFORMACIÓN": "Institucional desde UP-62"}) for n in range(46, 52)},
    **{f"UP-{n}": (NOC, "NO_APLICA_BETTERSOFT", "Instructivo AC 2026 Anexo II", OF, "—", "Cálculo institucional desde UP-62 y UP-58 (período 3 pendiente)",
                   {"TRANSFORMACIÓN": "Institucional desde UP-62 y UP-58"}) for n in range(52, 58)},
    "UP-58": (MAE, "P1", "Instructivo AC 2026 Anexo I (TIPO_UNIDAD_MEDIDA, TOTAL_UNIDADES_MEDIDA, UNIDADES_1ER..7MO_ANIO)", OF, "POR_CONFIRMAR", "Sube a P1: campos oficiales de Carreras AC dependen solo del plan", {}),
    "UP-59": (SOL, "P2", "Manual MU 2026 §2.vi (VIG 2: plan finalizado)", OF, "NO_EXISTE", "C09-01: sube de P4 a P2", {}),
    "UP-60": (SOL, "P2", "Manual MU 2026 §2.vi (VIG 2: título aún no obtenido)", OF, "NO_EXISTE", "C09-01: sube de P4 a P2", {}),
    "UP-61": (SOL, "P4", "Auditoría interna", "INTERNO", "EXISTE", "Sin cambio", {}),
    "UP-62": (SOL, "P1", f"{MU_C1} cols. U-Z; Instructivo AC 2026 Anexo II (unidades cursadas/aprobadas)", OF, "EXISTE (llave RUT+carrera)",
              "Sube a P1: fuente única de resúmenes MU y AC",
              {"DEFINICIÓN FUNCIONAL": "Extracto por asignatura cursada o reconocida: CODCLI, plan, código de asignatura, año, período, nota final, estado (aprobada/reprobada/inscrita), tipo de registro (cursada / convalidada / homologada / reconocida) y unidades o créditos."}),
}
NUEVOS = [
    dict(ID="UP-63", BLOQUE="Ingreso", **{"CAMPO SOLICITADO": "VIA_ADMISION_UPLUS + CUPO_ESPECIAL_UTILIZADO",
         "DEFINICIÓN FUNCIONAL": "Vía de admisión registrada en U+ (código y descripción) y, si corresponde, el cupo especial efectivamente usado para ingresar: PACE, programa de inclusión, cupo para extranjeros, características especiales (deportista, artista, hijo de funcionario, pueblos originarios, diplomático) u otro.",
         "NIVEL": "MATRÍCULA", "TIPO": "Texto + código", "PROCESOS QUE LO UTILIZAN": "MU", "CAMPO U+ ACTUAL": "VIASDEADMISION; CATEGORIA (significado no documentado)",
         "TRANSFORMACIÓN": "Ninguna", "EJEMPLO": "ADMISION REGULAR / SIN CUPO", "TIPO_OBTENCION": "E - Requiere nuevo dato en U+", "TEMPORALIDAD": "Hecho fijo del ingreso",
         "REQUERIMIENTO_HISTORICO": "NO", "VALIDACION": "Catálogo documentado", "DATO_SENSIBLE": "SI (pueblos originarios, inclusión)", "ESTADO": "PENDIENTE_DATO_UPLUS"},
         _g=(SOL, "P1", "Manual MU 2026 §4 (vías especiales solo si se usó el cupo) y Cuadro N°3 (formas 1 y 5-10)", OF, "EXISTE PARCIAL", "Nuevo (Gate 09): reemplaza el cálculo de FOR_ING_ACT")),
    dict(ID="UP-64", BLOQUE="Trayectoria", **{"CAMPO SOLICITADO": "TIPO_PROGRAMA_ORIGEN",
         "DEFINICIÓN FUNCIONAL": "Nivel del programa desde el que la persona llega a esta carrera: plan común / bachillerato / ciclo inicial; técnico de nivel superior; profesional; otro; sin programa previo.",
         "NIVEL": "MATRÍCULA", "TIPO": "Texto (catálogo)", "PROCESOS QUE LO UTILIZAN": "MU", "CAMPO U+ ACTUAL": "CARRERARANTERIOR (texto libre, parcial)",
         "TRANSFORMACIÓN": "Ninguna", "EJEMPLO": "TECNICO_NIVEL_SUPERIOR", "TIPO_OBTENCION": "E - Requiere nuevo dato en U+", "TEMPORALIDAD": "Hecho fijo",
         "REQUERIMIENTO_HISTORICO": "NO", "VALIDACION": "Coherente con TIPO_ORIGEN", "DATO_SENSIBLE": "NO", "ESTADO": "PENDIENTE_DATO_UPLUS"},
         _g=(SOL, "P1", "Manual MU 2026 Cuadro N°3 (2 plan común/bachillerato; 11 articulación TNS) y Anexo N°7", OF, "NO_EXISTE", "Nuevo (Gate 09)")),
    dict(ID="UP-65", BLOQUE="Ingreso", **{"CAMPO SOLICITADO": "RECONOCIMIENTO_COMO_CONDICION_DE_ACCESO",
         "DEFINICIÓN FUNCIONAL": "Indica si el ingreso se produjo por reconocimiento de aprendizajes previos (RAP) o por reconocimiento de estudios como condición de acceso; distinto de la convalidación de asignaturas.",
         "NIVEL": "MATRÍCULA", "TIPO": "Texto (catálogo)", "PROCESOS QUE LO UTILIZAN": "MU", "CAMPO U+ ACTUAL": "(no observado)", "TRANSFORMACIÓN": "Ninguna", "EJEMPLO": "RAP",
         "TIPO_OBTENCION": "E - Requiere nuevo dato en U+", "TEMPORALIDAD": "Hecho fijo", "REQUERIMIENTO_HISTORICO": "NO", "VALIDACION": "—", "DATO_SENSIBLE": "NO",
         "ESTADO": "PENDIENTE_DATO_UPLUS"}, _g=(SOL, "P2", "Manual MU 2026 §5 y Cuadro N°3 (forma 5)", OF, "POR_CONFIRMAR", "Nuevo (Gate 09)")),
    dict(ID="UP-66", BLOQUE="Matrícula del período", **{"CAMPO SOLICITADO": "HISTORIAL_MATRICULA_POR_PERIODO",
         "DEFINICIÓN FUNCIONAL": "Una fila por CODCLI y año/período con: CODIGO_UNICO_SIES vigente en ese período, jornada U+, sede U+, plan de estudios, nivel, estado de matrícula y fecha de matrícula.",
         "NIVEL": "MATRÍCULA-PERÍODO (historial)", "TIPO": "Varios", "PROCESOS QUE LO UTILIZAN": "MU; AC; Extranjeros", "CAMPO U+ ACTUAL": "(solo valor vigente)", "TRANSFORMACIÓN": "Ninguna",
         "EJEMPLO": "2025-2 | I162S2C47J1V1 | D | RE | plan | 3 | VIGENTE | 10/01/2025", "TIPO_OBTENCION": "E - Requiere nuevo dato en U+", "TEMPORALIDAD": "Histórico por período",
         "REQUERIMIENTO_HISTORICO": "SI", "VALIDACION": "Sin traslapes por CODCLI", "DATO_SENSIBLE": "NO", "ESTADO": "PENDIENTE_DATO_UPLUS"},
         _g=(SOL, "P1", "Manual MU 2026 (corte 30-04; Cuadro N°3: carrera del año anterior); Instructivo AC 2026 y Extranjeros 2026 (matrícula del año 2025)", OF, "POR_CONFIRMAR", "Nuevo (Gate 09, 9.9)")),
    dict(ID="UP-68", BLOQUE="Llaves", **{"CAMPO SOLICITADO": "CATALOGOS_UPLUS_DOCUMENTADOS",
         "DEFINICIÓN FUNCIONAL": "Tabla entregada por Bettersoft con el significado de cada código de U+ usado en el reporte: SEXO, SEDE, JORNADA, PERIODO (con fechas de inicio y término por régimen), SITUACION, ESTADOACADEMICO, MATRICULA, NIVEL, REGIMEN, CATEGORIA y VIASDEADMISION.",
         "NIVEL": "CATÁLOGO", "TIPO": "Tabla", "PROCESOS QUE LO UTILIZAN": "MU; AC; Extranjeros; FCU", "CAMPO U+ ACTUAL": "(no documentado)", "TRANSFORMACIÓN": "Ninguna",
         "EJEMPLO": "SEXO | S | <significado>", "TIPO_OBTENCION": "E - Requiere nuevo dato en U+", "TEMPORALIDAD": "Vigente, con cambios fechados", "REQUERIMIENTO_HISTORICO": "SI",
         "VALIDACION": "Todo código del reporte existe en el catálogo", "DATO_SENSIBLE": "NO", "ESTADO": "PENDIENTE_DATO_UPLUS"},
         _g=(SOL, "P1", "Campos oficiales de destino (Manual MU 2026 Cuadro N°1; instructivos AC y Extranjeros 2026); ningún cruce puede pasar de OBSERVADO a CONFIRMADO sin significado U+ documentado", OF, "NO_EXISTE", "Nuevo (Gate 09, 9.5)")),
]

BR_UPD = {
    "BR-01": ("ACTUALIZADA", "Almacenar CODIGO_UNICO_SIES como maestro regulatorio historizable con atributos de oferta (UP-26, UP-27); reglas de mantención del Anexo 5 del Instructivo Oferta."),
    "BR-02": ("REFORMULADA", "Ya no se pide la forma de ingreso SIES: se piden hechos (UP-63, UP-64, UP-65 y trayectoria UP-34 a UP-37)."),
    "BR-04": ("AMPLIADA", "Historial de estado/situación con fechas (UP-43) e historial de matrícula por período (UP-66)."),
    "BR-05": ("REFORMULADA", "Los resúmenes MU se calculan en la institución desde el detalle por asignatura (UP-62, P1)."),
    "BR-06": ("REFORMULADA", "El avance AC se calcula en la institución desde UP-62 y el catálogo de planes UP-58 (P1)."),
    "BR-11": ("ACTUALIZADA", "País de estudios secundarios sube a P1: registrar el país donde se obtuvo la licencia de enseñanza media, sin valor por defecto."),
    "BR-13": ("REFORMULADA", "Entregar SEXO sin transformar + catálogo U+ documentado (UP-68); el código SIES lo asigna la institución por proceso."),
    "BR-14": ("REFORMULADA", "Entregar JORNADA sin transformar y con historia por período; el código SIES de jornada sale del CODIGO_UNICO."),
    "BR-16": ("REFORMULADA", "Suspensiones y reincorporación se calculan desde UP-43."),
    "BR-23": ("ACTUALIZADA", "Fechas de egreso y titulación suben a P2: se requieren para identificar egresados con matrícula vigente en Matrícula Unificada."),
}
BR_NEW = [
    dict(ID="BR-25", CAMPO="Catálogos U+", **{"SITUACIÓN ACTUAL": "Significado de códigos U+ inferido por uso (SEXO, SEDE, JORNADA, PERIODO, SITUACION, etc.).",
         "PROBLEMA": "Ningún cruce puede confirmarse; riesgo de inversión (SEXO 'M').", "CAMBIO SOLICITADO": "Entregar catálogo documentado de cada código (UP-68).",
         "PROCESOS AFECTADOS": "MU; AC; Extranjeros; FCU", "PRIORIDAD": "P1", "CLASE DE SOLICITUD": "Documentación", "EVIDENCIA": "Gate 09, 9.5", "ID_DICCIONARIO": "UP-68"}),
    dict(ID="BR-26", CAMPO="Vía de admisión, cupo y programa de origen", **{"SITUACIÓN ACTUAL": "VIASDEADMISION/CATEGORIA sin significado; programa anterior en texto libre.",
         "PROBLEMA": "La forma de ingreso se infería desde situación vigente y nombre del programa.", "CAMBIO SOLICITADO": "Registrar vía/cupo (UP-63), tipo de programa de origen (UP-64) y reconocimiento de acceso (UP-65).",
         "PROCESOS AFECTADOS": "MU", "PRIORIDAD": "P1", "CLASE DE SOLICITUD": "Nuevo dato", "EVIDENCIA": "C09-02, C09-03", "ID_DICCIONARIO": "UP-63; UP-64; UP-65"}),
    dict(ID="BR-27", CAMPO="Historial de matrícula por período", **{"SITUACIÓN ACTUAL": "Solo valor vigente de jornada, sede, plan, nivel y programa.",
         "PROBLEMA": "Jornada vigente distinta de la informada en cambios de jornada; no se reconstruye el año anterior.", "CAMBIO SOLICITADO": "Extracto por CODCLI y período (UP-66).",
         "PROCESOS AFECTADOS": "MU; AC; Extranjeros", "PRIORIDAD": "P1", "CLASE DE SOLICITUD": "Nuevo extracto", "EVIDENCIA": "C09-07; 9.9", "ID_DICCIONARIO": "UP-66"}),
]
CAT_NEW = [
    ("SEXO", "Estudiantes Extranjeros Regulares 2026", "SIES", "H / M / NB", "Hombre / Mujer / No Binario", "", f"{INS_EX} Anexo I campo G; Anexo V", "Oficial", "Confirmado"),
    ("VIGENCIA (Extranjeros)", "Estudiantes Extranjeros 2026", "SIES", "0", "Eliminar registro (no es vigencia académica)", "", f"{INS_EX} p.6 y Anexo I campo T", "Oficial", "Confirmado"),
    ("VIGENCIA (Extranjeros)", "Estudiantes Extranjeros 2026", "SIES", "1", "Mantener registro (estuvo matriculado en 2025)", "", f"{INS_EX} p.6 y Anexo I campo T", "Oficial", "Confirmado"),
    ("TIPO_RESIDENCIA", "Estudiantes Extranjeros Regulares 2026", "SIES", "1", "Extranjero con residencia previa en el país", "", f"{INS_EX} §e y Anexo I campo J", "Oficial", "Confirmado"),
    ("TIPO_RESIDENCIA", "Estudiantes Extranjeros Regulares 2026", "SIES", "2", "Extranjero sin residencia previa en el país", "", f"{INS_EX} §e y Anexo I campo J", "Oficial", "Confirmado"),
    ("TIPO_RESIDENCIA", "Estudiantes Extranjeros Regulares 2026", "SIES", "3", "Extranjero que no reside en Chile", "", f"{INS_EX} §e y Anexo I campo J", "Oficial", "Confirmado"),
    ("TIPO_PLAN", "Oferta Académica", "SIES", "Regular / Especial / Regular de continuidad", "Tipo de plan del programa (atributo de la versión)", "", f"{INS_OA} tipos de plan; Anexo 5", "Oficial", "Confirmado"),
]


def clasificar_cat(r):
    cat, lado, cod = r["CATALOGO"], r["LADO"], r["CODIGO"].strip().upper()
    if lado == "SIES":
        if cat == "SIT_FON_SOL":
            return ("OFICIAL", "Único valor aceptado por PES para IPSS (C09-04)" if cod == "0" else "Oficial, pero rechazado por PES para IPSS (C09-04)")
        if cat.startswith("VIGENCIA (Extranjeros)"):
            return ("OFICIAL", "Definición confirmada: 0 eliminar / 1 mantener registro (Instructivo Extranjeros 2026)")
        return ("OFICIAL", "")
    if cat == "SEXO":
        return ("PENDIENTE", "C09-05") if cod == "S" else ("OBSERVADO", "Significado U+ no documentado por Bettersoft")
    if cat == "SEDE":
        return ("OBSERVADO", "Consistente en carga aceptada; significado U+ no documentado")
    if cat == "JORNADA":
        return ("NO_DETERMINABLE", "C09-07") if cod == "O" else ("OBSERVADO", "Consistente en carga aceptada; derivar de CODIGO_UNICO")
    if cat == "NACIONALIDAD":
        return ("DEFAULT_TECNICO_NO_REGLA", "Carga 2026 informó 38") if "DEFINIR" in cod else ("OBSERVADO", "Homologación institucional")
    if cat == "VIG (MU)":
        return ("DESCARTADO_COMO_REGLA", "C09-01: ningún estado U+ determina VIG")
    if cat == "FOR_ING_ACT":
        return ("DESCARTADO_COMO_REGLA", "C09-02/C09-03: FOR_ING_ACT es cálculo institucional desde hechos")
    if cat.startswith("PERIODO"):
        return ("PENDIENTE", "C09-09") if cod == "3" else ("OBSERVADO", "Requiere catálogo de períodos con fechas")
    if cat == "ESCALA_NOTAS":
        return ("OBSERVADO", "Rango oficial; transformación implementada")
    if cat == "TIPO_DOCUMENTO":
        return ("PENDIENTE", "U+ no informa tipo de documento (UP-03)")
    return ("SIN_REVISION_GATE09", "")


# ---------------------------------------------------------------- utilidades openpyxl
HEAD_FILL = PatternFill("solid", fgColor="1F3864")
HEAD_FONT = Font(color="FFFFFF", bold=True)
NEW_FILL = PatternFill("solid", fgColor="7030A0")
PRIO_FILL = {"P1": "F8CBAD", "P2": "FFE699", "P3": "C6E0B4", "P4": "D9E1F2"}


def header_map(ws):
    return {c.value: c.column for c in ws[1] if c.value is not None}


def add_cols(ws, names):
    hm = header_map(ws)
    for n in names:
        if n not in hm:
            col = ws.max_column + 1
            c = ws.cell(row=1, column=col, value=n)
            c.fill, c.font = NEW_FILL, HEAD_FONT
            c.alignment = Alignment(wrap_text=True, vertical="top")
            ws.column_dimensions[get_column_letter(col)].width = 34
            hm[n] = col
    return hm


def append_row(ws, hm, data):
    r = ws.max_row + 1
    for k, v in data.items():
        if k in hm:
            ws.cell(row=r, column=hm[k], value=v).alignment = Alignment(wrap_text=True, vertical="top")
    return r


def sheet(wb, name, cols, rows, widths=None):
    ws = wb.create_sheet(name)
    ws.append(cols)
    for c in ws[1]:
        c.fill, c.font = HEAD_FILL, HEAD_FONT
        c.alignment = Alignment(wrap_text=True, vertical="top")
    for r in rows:
        ws.append([r.get(c, "") if isinstance(r, dict) else r[i] for i, c in enumerate(cols)])
    for i, c in enumerate(cols, 1):
        ws.column_dimensions[get_column_letter(i)].width = (widths or {}).get(c, 28)
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    return ws


# ---------------------------------------------------------------- diccionario v0.9.1
def construir_diccionario():
    wb = load_workbook(V09)
    # 04 matriz
    ws = wb["04_MATRIZ_MAESTRA"]
    hm = add_cols(ws, ["MAPEO_ANTERIOR", "ESTADO_ANTERIOR", "RESOLUCION_GATE09", "MAPEO_VIGENTE", "ESTADO_VIGENTE", "REF_GATE09"])
    n_mat = 0
    for row in range(2, ws.max_row + 1):
        fid = ws.cell(row=row, column=hm["ID_FILA"]).value
        if fid in MAT:
            ant, res, vig, est, ref = MAT[fid]
            vals = dict(MAPEO_ANTERIOR=ant, ESTADO_ANTERIOR=ws.cell(row=row, column=hm["ESTADO"]).value, RESOLUCION_GATE09=res,
                        MAPEO_VIGENTE=vig, ESTADO_VIGENTE=est, REF_GATE09=ref)
            for k, v in vals.items():
                ws.cell(row=row, column=hm[k], value=v).alignment = Alignment(wrap_text=True, vertical="top")
            n_mat += 1
    # 05 diccionario
    ws = wb["05_DICCIONARIO_BETTERSOFT"]
    hm = add_cols(ws, ["PRIORIDAD_ANTERIOR", "ESTADO_ANTERIOR", "RESOLUCION_GATE09", "ACCION_BETTERSOFT", "RESPALDO_NECESIDAD", "NIVEL_RESPALDO_NECESIDAD",
                       "DISPONIBILIDAD_UPLUS", "P1_DEMOSTRADO"])
    cambios = 0
    for row in range(2, ws.max_row + 1):
        uid = ws.cell(row=row, column=hm["ID"]).value
        if uid not in DIC:
            continue
        acc, pri, resp, niv, disp, reso, upd = DIC[uid]
        pri_ant = ws.cell(row=row, column=hm["PRIORIDAD"]).value
        est_ant = ws.cell(row=row, column=hm["ESTADO"]).value
        ws.cell(row=row, column=hm["PRIORIDAD_ANTERIOR"], value=pri_ant)
        ws.cell(row=row, column=hm["ESTADO_ANTERIOR"], value=est_ant)
        for k, v in {**upd, "PRIORIDAD": pri, "RESOLUCION_GATE09": reso, "ACCION_BETTERSOFT": acc, "RESPALDO_NECESIDAD": resp,
                     "NIVEL_RESPALDO_NECESIDAD": niv, "DISPONIBILIDAD_UPLUS": disp}.items():
            ws.cell(row=row, column=hm[k], value=v).alignment = Alignment(wrap_text=True, vertical="top")
        if pri != pri_ant or upd or acc != SOL:
            cambios += 1
    nro = ws.max_row - 1
    for d in NUEVOS:
        acc, pri, resp, niv, disp, reso = d["_g"]
        nro += 1
        data = {k: v for k, v in d.items() if k != "_g"}
        data.update({"Nº": nro, "PRIORIDAD": pri, "PRIORIDAD_ANTERIOR": "(nuevo)", "ESTADO_ANTERIOR": "(nuevo)", "RESOLUCION_GATE09": reso,
                     "ACCION_BETTERSOFT": acc, "RESPALDO_NECESIDAD": resp, "NIVEL_RESPALDO_NECESIDAD": niv, "DISPONIBILIDAD_UPLUS": disp,
                     "EVIDENCIA": resp})
        append_row(ws, hm, data)
    for row in range(2, ws.max_row + 1):
        pri = ws.cell(row=row, column=hm["PRIORIDAD"]).value
        acc = ws.cell(row=row, column=hm["ACCION_BETTERSOFT"]).value
        niv = ws.cell(row=row, column=hm["NIVEL_RESPALDO_NECESIDAD"]).value or ""
        dem = "NA" if pri != "P1" else ("SI" if niv.startswith(OF) and acc in (SOL, MAE) else "NO")
        ws.cell(row=row, column=hm["P1_DEMOSTRADO"], value=dem)
        c = ws.cell(row=row, column=hm["PRIORIDAD"])
        c.fill = PatternFill("solid", fgColor=PRIO_FILL.get(pri, "EDEDED"))
    # 06 catálogos
    ws = wb["06_CATALOGOS_HOMOLOGACIONES"]
    hm = add_cols(ws, ["CLASIFICACION_GATE09", "NOTA_GATE09"])
    for row in range(2, ws.max_row + 1):
        r = {k: (ws.cell(row=row, column=c).value or "") for k, c in hm.items()}
        cl, nota = clasificar_cat(r)
        ws.cell(row=row, column=hm["CLASIFICACION_GATE09"], value=cl)
        ws.cell(row=row, column=hm["NOTA_GATE09"], value=nota)
    for c in CAT_NEW:
        append_row(ws, hm, dict(zip(["CATALOGO", "PROCESO", "LADO", "CODIGO", "SIGNIFICADO", "HOMOLOGA_A", "EVIDENCIA", "NIVEL_RESPALDO", "ESTADO"], c),
                                CLASIFICACION_GATE09="OFICIAL", NOTA_GATE09="Incorporado en Gate 09"))
    # 07 brechas
    ws = wb["07_BRECHAS_BETTERSOFT"]
    hm = add_cols(ws, ["ESTADO_GATE09", "CAMBIO_GATE09"])
    for row in range(2, ws.max_row + 1):
        bid = ws.cell(row=row, column=hm["ID"]).value
        est, cam = BR_UPD.get(bid, ("SIN_CAMBIO", ""))
        ws.cell(row=row, column=hm["ESTADO_GATE09"], value=est)
        ws.cell(row=row, column=hm["CAMBIO_GATE09"], value=cam)
        if bid == "BR-11":
            ws.cell(row=row, column=hm["PRIORIDAD"], value="P1")
    for b in BR_NEW:
        append_row(ws, hm, {**b, "ESTADO_GATE09": "NUEVA", "CAMBIO_GATE09": "Nueva en Gate 09"})
    # 09 contradicciones
    ws = wb["09_CONTRADICCIONES"]
    hm = add_cols(ws, ["ID_GATE09", "ESTADO_GATE09", "RESOLUCION_GATE09"])
    by_v09 = {r["ID_V09"]: r for r in REG}
    for row in range(2, ws.max_row + 1):
        r = by_v09.get(ws.cell(row=row, column=hm["ID"]).value)
        if r:
            for k, v in (("ID_GATE09", r["ID_CONTRADICCION"]), ("ESTADO_GATE09", r["ESTADO_GATE09"]), ("RESOLUCION_GATE09", r["RESOLUCION"])):
                ws.cell(row=row, column=hm[k], value=v).alignment = Alignment(wrap_text=True, vertical="top")
    # 11 fuentes
    ws = wb["11_FUENTES_EVIDENCIA"]
    hm = header_map(ws)
    for f in MANIF:
        if f["datos_personales"] == "NO" or f["estado"] == "REFERENCIADO_SIN_COPIA":
            append_row(ws, hm, {"CLAVE": f"GATE09 · {f['rol']} ({f['proceso']})", "RUTA_O_REFERENCIA": f["ruta_destino"] or f["ruta_origen"]})
        else:
            append_row(ws, hm, {"CLAVE": f"GATE09 · {f['rol']} ({f['proceso']}) [datos personales, solo local]", "RUTA_O_REFERENCIA": f["ruta_destino"]})
    # 00 estado fases y leeme
    ws = wb["00_ESTADO_FASES"]
    hm = header_map(ws)
    append_row(ws, hm, {"FASE": "9 - Gate 09 cierre funcional", "ESTADO": "Ver 18_QA_GATE09 y REPORTE_CIERRE_GATE09",
                        "PROCESOS_ANALIZADOS": "MU; AC; Extranjeros; Oferta; FCU",
                        "ARCHIVOS_REVISADOS": "Cargas PES MU 2026 (_orig), respuestas PES, instructivos AC y Extranjeros 2026, plantillas PES Oferta, snapshot U+ 08-05-2026",
                        "CAMPOS_IDENTIFICADOS": f"{len(MAT)} filas de matriz y {len(DIC) + len(NUEVOS)} filas del diccionario revisadas",
                        "CRUCES_CONFIRMADOS": "Ninguno pasa a CONFIRMADO sin catálogo U+ documentado; ver 13_GATE09_CRUCES",
                        "PENDIENTES": "C09-05 (SEXO S), C09-09 (período 3)", "BLOQUEOS": "Ninguno sobre P1", "SIGUIENTE_FASE": "Congelar v1.0"})
    ws = wb["00_LEEME"]
    hm = header_map(ws)
    append_row(ws, hm, {"TEMA": "Versión", "DETALLE": "v0.9.1 (Gate 09). Derivado de DICCIONARIO_MAESTRO_UPLUS_SIES_2026.xlsx v0.9, que no se modifica. Columnas en morado = agregadas en Gate 09."})
    append_row(ws, hm, {"TEMA": "Principio Gate 09", "DETALLE": "Bettersoft entrega hechos; la institución gobierna las reglas regulatorias. ACCION_BETTERSOFT distingue SOLICITAR_HECHO, SOLICITAR_MAESTRO, NO_CALCULAR_EN_UPLUS y NO_SOLICITAR."})
    # hojas nuevas
    sheet(wb, "12_GATE09_RESOLUCION", CAMPOS_REG, REG, {c: 45 for c in CAMPOS_REG})
    sheet(wb, "13_GATE09_CRUCES", CRUCES_COLS, CRUCES)
    sheet(wb, "14_CAMPOS_REQUIEREN_HISTORIAL", ["CAMPO", "FECHA_CRITERIO_NECESARIO", "ESTADO_ACTUAL_U_PLUS", "BRECHA", "ID_DICCIONARIO"], HISTORIAL)
    sheet(wb, "15_CODIGO_UNICO_MANTENCION", ["ASPECTO", "DETALLE", "FUENTE"], COD_UNICO, {"DETALLE": 90, "FUENTE": 50})
    sheet(wb, "16_SEXO_POR_PROCESO", ["PROCESO", "CAMPO", "CODIGOS", "RESPALDO", "FUENTE", "TRATAMIENTO"], SEXO_PROC)
    sheet(wb, "17_JORNADA_U_PLUS", ["JORNADA_U_PLUS", "PARES_CARGA_2026", "COD_SIES_OBSERVADO", "PUENTE", "CLASIFICACION", "VARIABLE_NECESARIA"], JORNADA)
    return wb, n_mat, cambios


# ---------------------------------------------------------------- auditoría
def construir_auditoria():
    wb = Workbook()
    wb.remove(wb.active)
    sheet(wb, "01_REGISTRO_CONTRADICCIONES", CAMPOS_REG, REG, {c: 45 for c in CAMPOS_REG})
    sheet(wb, "02_CADENA_EVIDENCIA", ["ID_CONTRADICCION", "PASO", "CONTENIDO", "FUENTE_O_ESTADO"],
          [(k, p, t, f) for k, v in CADENA.items() for p, t, f in v], {"CONTENIDO": 100, "FUENTE_O_ESTADO": 50})
    sheet(wb, "03_CRUCES", CRUCES_COLS, CRUCES)
    sheet(wb, "04_SEXO", ["PROCESO", "CAMPO", "CODIGOS", "RESPALDO", "FUENTE", "TRATAMIENTO"], SEXO_PROC)
    sheet(wb, "05_JORNADA", ["JORNADA_U_PLUS", "PARES_CARGA_2026", "COD_SIES_OBSERVADO", "PUENTE", "CLASIFICACION", "VARIABLE_NECESARIA"], JORNADA)
    sheet(wb, "06_CODIGO_UNICO", ["ASPECTO", "DETALLE", "FUENTE"], COD_UNICO, {"DETALLE": 90, "FUENTE": 50})
    sheet(wb, "07_CAMPOS_REQUIEREN_HISTORIAL", ["CAMPO", "FECHA_CRITERIO_NECESARIO", "ESTADO_ACTUAL_U_PLUS", "BRECHA", "ID_DICCIONARIO"], HISTORIAL)
    sheet(wb, "08_PAIS_EST_SEC", ["FUENTE", "VALOR_INFORMADO", "ORIGEN", "CLASIFICACION"], PAIS)
    sheet(wb, "09_FUENTES_INCORPORADAS", list(MANIF[0].keys()), MANIF)

    def flat(d, p=""):
        for k, v in d.items():
            if isinstance(v, dict):
                yield from flat(v, f"{p}{k}.")
            else:
                yield (f"{p}{k}", json.dumps(v, ensure_ascii=False) if isinstance(v, list) else v)
    sheet(wb, "10_METRICAS", ["METRICA", "VALOR"], list(flat(M)), {"METRICA": 70, "VALOR": 40})
    return wb


# ---------------------------------------------------------------- JSON para el Word del proveedor
def json_word(wb):
    ws = wb["05_DICCIONARIO_BETTERSOFT"]
    cols = [c.value for c in ws[1]]
    rows = [dict(zip(cols, [c.value for c in r])) for r in ws.iter_rows(min_row=2)]
    dic = [r for r in rows if r["ACCION_BETTERSOFT"] in (SOL, MAE)]
    keep = ["ID", "BLOQUE", "CAMPO SOLICITADO", "DEFINICIÓN FUNCIONAL", "NIVEL", "TIPO", "PROCESOS QUE LO UTILIZAN", "CAMPO U+ ACTUAL", "EJEMPLO",
            "PRIORIDAD", "TEMPORALIDAD", "REQUERIMIENTO_HISTORICO", "VALIDACION", "DATO_SENSIBLE", "ACCION_BETTERSOFT", "DISPONIBILIDAD_UPLUS"]
    dic = [{k: ("" if r.get(k) is None else r.get(k)) for k in keep} for r in dic]
    ws = wb["07_BRECHAS_BETTERSOFT"]
    cols = [c.value for c in ws[1]]
    br = [dict(zip(cols, [c.value for c in r])) for r in ws.iter_rows(min_row=2)]
    br = [{k: ("" if b.get(k) is None else b.get(k)) for k in ["ID", "CAMPO", "SITUACIÓN ACTUAL", "CAMBIO SOLICITADO", "PROCESOS AFECTADOS", "PRIORIDAD"]} for b in br]
    for b in br:
        upd = BR_UPD.get(b["ID"])
        if upd:
            b["CAMBIO SOLICITADO"] = upd[1]
    no_calc = [r for r in rows if r["ACCION_BETTERSOFT"] == NOC]
    nombre = {"UP-33": "FORMA_INGRESO_SIES (código SIES de forma de ingreso; los hechos se piden en UP-63 a UP-65)"}
    extra = [{"ID": "", "CAMPO": t} for t in (
        "VIGENCIA de Matrícula Unificada (VIG 0/1/2): se calcula con UP-39, UP-40, UP-43, UP-59 y UP-60",
        "Códigos SIES de sede, carrera, jornada, modalidad y versión: se obtienen del código único (UP-26, UP-27)",
        "Semestre SIES de ingreso y nivel académico en semestres: se calculan con el período y el régimen documentados (UP-32, UP-41, UP-68)",
        "Situación socioeconómica Fondo Solidario: no se solicita a U+")]
    return {"dic": dic, "br": br, "no_calcular": [{"ID": r["ID"], "CAMPO": nombre.get(r["ID"], r["CAMPO SOLICITADO"])} for r in no_calc] + extra,
            "codigo_unico": [{"ASPECTO": a, "DETALLE": d} for a, d, _ in COD_UNICO if not a.startswith(("Hallazgo", "Llave"))],
            "historial": [{"CAMPO": c, "CRITERIO": f, "ID": i} for c, f, _, _, i in HISTORIAL]}


def main():
    wb, n_mat, cambios = construir_diccionario()
    wb.save(V091)
    construir_auditoria().save(AUD)
    wb2 = load_workbook(V091)
    req = json_word(wb2)
    (RES / "gate09/req_gate09.json").write_text(json.dumps(req, ensure_ascii=False, indent=1), encoding="utf-8")
    print("DICCIONARIO:", V091, "| filas matriz actualizadas:", n_mat, "| filas diccionario modificadas:", cambios, "| nuevas:", len(NUEVOS))
    print("AUDITORIA:", AUD)
    print("REQ JSON: campos proveedor", len(req["dic"]), "| no calcular", len(req["no_calcular"]))


if __name__ == "__main__":
    main()
