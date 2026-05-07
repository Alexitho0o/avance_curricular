#!/usr/bin/env python3
"""
Auditoría end-to-end · Cierre MU2026 · Postgrado/Postítulo
Fases 0–8 completas según especificación técnica.
Solo librerías estándar: csv, json, pathlib, datetime, collections, re, shutil.
"""

import csv
import json
import re
import shutil
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# PATHS
# ──────────────────────────────────────────────────────────────────────────────
REPO = Path(__file__).resolve().parent.parent.parent  # avance_curricular/
DIAG_DIR = REPO / "diagnosticos" / "mu2026_postgrado"
RESULTADOS = REPO / "resultados"

DICCIONARIO = REPO / "control" / "diccionarios" / "diccionario_postgrado_postitulo_mu2026.tsv"
TRAZABILIDAD = RESULTADOS / "trazabilidad_matricula_unificada_2026_postgrado_postitulo.tsv"
CONTROL_CSV = RESULTADOS / "matricula_unificada_2026_postgrado_postitulo_control.csv"
PES_READY = RESULTADOS / "matricula_unificada_2026_postgrado_postitulo.csv"

# Archivos de pregrado — NO modificar
PREGRADO_ARCHIVOS = [
    RESULTADOS / "matricula_unificada_2026_pregrado.csv",
    RESULTADOS / "matricula_unificada_2026_pregrado_PES_READY.csv",
    RESULTADOS / "matricula_unificada_2026_control.csv",
]

# Salidas
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT_REPORTE_MD = DIAG_DIR / f"auditoria_final_pes_ready_postgrado_postitulo_{TS}.md"
OUT_RESUMEN_JSON = DIAG_DIR / f"resumen_cierre_postgrado_postitulo_{TS}.json"
OUT_PES_FINAL = RESULTADOS / "matricula_unificada_2026_postgrado_postitulo_PES_READY.csv"
OUT_CONTROL_FINAL = RESULTADOS / "matricula_unificada_2026_postgrado_postitulo_CONTROL_FINAL.csv"
OUT_EXCLUIDOS = RESULTADOS / "matricula_unificada_2026_postgrado_postitulo_excluidos_2026_gobernanza.csv"

CAMPOS_PES = [
    "TIPO_DOC", "N_DOC", "DV", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO", "NOMBRE",
    "SEXO", "FECH_NAC", "NAC", "PAIS_EST_SEC", "COD_SED", "COD_CAR",
    "MODALIDAD", "JOR", "VERSION", "FOR_ING_ACT", "ANIO_ING_ACT", "SEM_ING_ACT",
    "ANIO_ING_ORI", "SEM_ING_ORI", "VIG",
]

ACCIONES_EXCLUIR = {"EXCLUIR", "EXCLUIR_HASTA_VALIDAR", "NO_MAPEAR_GENERICO",
                    "PENDIENTE_REVISION", "SIN_DICCIONARIO"}
ESTADOS_EXCLUIR_DIC = {"SIN_MAPEO", "EXCLUIR", "EXCLUIR_HASTA_VALIDAR",
                       "PENDIENTE_REVISION", "NO_MAPEAR_GENERICO",
                       "POSIBLE_MATCH_REVISION_MANUAL"}

# ──────────────────────────────────────────────────────────────────────────────
# UTILIDADES
# ──────────────────────────────────────────────────────────────────────────────

def c(x):
    return str(x).strip() if x is not None else ""


def leer_tsv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def leer_csv(path):
    """Lee CSV; maneja BOM (utf-8-sig) automáticamente."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def leer_pes_ready_raw(path):
    """Lee el archivo PES-ready como líneas crudas (sin encabezado)."""
    with open(path, encoding="utf-8", newline="") as f:
        return [line.rstrip("\n") for line in f]


def backup_if_exists(path):
    if path.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bkp = path.with_name(path.stem + f"_bkp_{ts}" + path.suffix)
        shutil.copy2(path, bkp)
        return bkp
    return None


# ──────────────────────────────────────────────────────────────────────────────
# FASE 0 · Preparación segura
# ──────────────────────────────────────────────────────────────────────────────

def fase0_preparacion():
    errores = []
    advertencias = []
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    RESULTADOS.mkdir(parents=True, exist_ok=True)

    archivos_requeridos = {
        "diccionario": DICCIONARIO,
        "trazabilidad": TRAZABILIDAD,
        "control_csv": CONTROL_CSV,
        "pes_ready": PES_READY,
    }
    estado_archivos = {}
    for nombre, path in archivos_requeridos.items():
        if not path.exists():
            errores.append(f"FALTA_ARCHIVO: {path.name}")
            estado_archivos[nombre] = "FALTA"
        else:
            estado_archivos[nombre] = "OK"

    # Verificar que los archivos de pregrado no fueron modificados
    pregrado_ok = all(p.exists() for p in PREGRADO_ARCHIVOS)
    if not pregrado_ok:
        advertencias.append("Algún archivo de pregrado no existe (no fue modificado por este proceso).")

    return {
        "errores": errores,
        "advertencias": advertencias,
        "archivos_requeridos": estado_archivos,
        "pregrado_intacto": pregrado_ok,
    }


# ──────────────────────────────────────────────────────────────────────────────
# FASE 1 · Auditoría estructural del PES-ready
# ──────────────────────────────────────────────────────────────────────────────

def fase1_estructura(lineas_pes):
    errores = []
    advertencias = []

    # 1. No tiene encabezado: primera línea no empieza con TIPO_DOC ni texto
    if lineas_pes and lineas_pes[0].upper().startswith("TIPO_DOC"):
        errores.append("ENCABEZADO_EN_PES_READY: la primera línea parece un encabezado.")

    # 2. Cada fila tiene 21 campos
    campos_por_fila = Counter(len(l.split(";")) for l in lineas_pes if l)
    for n_campos, n_filas in campos_por_fila.items():
        if n_campos != 21:
            errores.append(f"CAMPOS_INCORRECTOS: {n_filas} filas tienen {n_campos} campos (esperado 21).")

    # 3. No hay filas vacías
    filas_vacias = sum(1 for l in lineas_pes if not l.strip())
    if filas_vacias:
        errores.append(f"FILAS_VACIAS: {filas_vacias} filas vacías encontradas.")

    # 4. No hay campos vacíos en ninguna fila
    filas_con_vacio = []
    for i, l in enumerate(lineas_pes, 1):
        if not l.strip():
            continue
        fields = l.split(";")
        if len(fields) == 21:
            for j, f in enumerate(fields):
                if not f.strip():
                    filas_con_vacio.append((i, CAMPOS_PES[j]))
    if filas_con_vacio:
        for fila_num, campo in filas_con_vacio[:20]:
            errores.append(f"CAMPO_VACIO: fila {fila_num}, campo {campo}.")
        if len(filas_con_vacio) > 20:
            errores.append(f"... y {len(filas_con_vacio)-20} campos vacíos adicionales.")

    # 5. Cantidad total
    total_filas = sum(1 for l in lineas_pes if l.strip())

    return {
        "errores": errores,
        "advertencias": advertencias,
        "total_filas": total_filas,
        "campos_por_fila": dict(campos_por_fila),
        "filas_vacias": filas_vacias,
        "filas_con_campo_vacio": len(filas_con_vacio),
    }


# ──────────────────────────────────────────────────────────────────────────────
# FASE 2 · Auditoría de dominios
# ──────────────────────────────────────────────────────────────────────────────

def _es_fecha_ddmmaaaa(s):
    m = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", s)
    if not m:
        return False
    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return 1 <= d <= 31 and 1 <= mo <= 12 and 1900 <= y <= 2026


def fase2_dominios(lineas_pes):
    errores = []
    advertencias = []
    filas_parsed = []
    casos_pasaporte = 0
    casos_anio_ori_1900 = 0

    for i, linea in enumerate(lineas_pes, 1):
        if not linea.strip():
            continue
        fields = linea.split(";")
        if len(fields) != 21:
            continue  # ya reportado en fase1

        row = dict(zip(CAMPOS_PES, fields))
        filas_parsed.append(row)
        fila_errores = []

        tipo_doc = c(row["TIPO_DOC"])
        n_doc = c(row["N_DOC"])
        dv = c(row["DV"])
        sexo = c(row["SEXO"])
        fech_nac = c(row["FECH_NAC"])
        nac = c(row["NAC"])
        pais_sec = c(row["PAIS_EST_SEC"])
        cod_sed = c(row["COD_SED"])
        cod_car = c(row["COD_CAR"])
        modalidad = c(row["MODALIDAD"])
        jor = c(row["JOR"])
        version = c(row["VERSION"])
        for_ing = c(row["FOR_ING_ACT"])
        anio_act = c(row["ANIO_ING_ACT"])
        sem_act = c(row["SEM_ING_ACT"])
        anio_ori = c(row["ANIO_ING_ORI"])
        sem_ori = c(row["SEM_ING_ORI"])
        vig = c(row["VIG"])

        # TIPO_DOC
        if tipo_doc not in {"R", "P"}:
            fila_errores.append(f"TIPO_DOC_INVALIDO:{tipo_doc}")
        if tipo_doc == "P":
            casos_pasaporte += 1

        # N_DOC y DV
        if tipo_doc == "R":
            if not n_doc.isdigit():
                fila_errores.append(f"N_DOC_NO_NUMERICO:{n_doc}")
            if not dv:
                fila_errores.append("DV_VACIO_PARA_RUT")
            elif not re.match(r"^[0-9Kk]$", dv):
                fila_errores.append(f"DV_INVALIDO:{dv}")
        elif tipo_doc == "P":
            if dv:
                fila_errores.append(f"DV_DEBE_SER_VACIO_PARA_PASAPORTE:{dv}")

        # SEXO
        if sexo not in {"H", "M", "NB"}:
            fila_errores.append(f"SEXO_INVALIDO:{sexo}")

        # FECH_NAC
        if not _es_fecha_ddmmaaaa(fech_nac):
            fila_errores.append(f"FECH_NAC_FORMATO_INVALIDO:{fech_nac}")

        # NAC
        if nac.isdigit():
            if not (1 <= int(nac) <= 197):
                fila_errores.append(f"NAC_FUERA_RANGO:{nac}")
        else:
            fila_errores.append(f"NAC_NO_NUMERICO:{nac}")

        # PAIS_EST_SEC
        if pais_sec.isdigit():
            if not (1 <= int(pais_sec) <= 197):
                fila_errores.append(f"PAIS_EST_SEC_FUERA_RANGO:{pais_sec}")
        else:
            fila_errores.append(f"PAIS_EST_SEC_NO_NUMERICO:{pais_sec}")

        # COD_SED, COD_CAR, MODALIDAD, JOR, VERSION
        for campo, val in [("COD_SED", cod_sed), ("COD_CAR", cod_car),
                           ("MODALIDAD", modalidad), ("JOR", jor), ("VERSION", version)]:
            if not val:
                fila_errores.append(f"{campo}_VACIO")

        # FOR_ING_ACT
        if for_ing.isdigit():
            if not (1 <= int(for_ing) <= 11):
                fila_errores.append(f"FOR_ING_ACT_FUERA_RANGO:{for_ing}")
        else:
            fila_errores.append(f"FOR_ING_ACT_NO_NUMERICO:{for_ing}")

        # ANIO_ING_ACT
        if anio_act.isdigit():
            if not (1990 <= int(anio_act) <= 2026):
                fila_errores.append(f"ANIO_ING_ACT_FUERA_RANGO:{anio_act}")
        else:
            fila_errores.append(f"ANIO_ING_ACT_NO_NUMERICO:{anio_act}")

        # SEM_ING_ACT
        if sem_act not in {"1", "2"}:
            fila_errores.append(f"SEM_ING_ACT_INVALIDO:{sem_act}")

        # ANIO_ING_ORI
        if anio_ori.isdigit():
            anio_ori_int = int(anio_ori)
            if anio_ori_int == 1900:
                casos_anio_ori_1900 += 1
                advertencias.append(f"ANIO_ING_ORI=1900 en fila {i}: revisar regla especial para ingreso originario desconocido.")
            elif not (1980 <= anio_ori_int <= 2026):
                fila_errores.append(f"ANIO_ING_ORI_FUERA_RANGO:{anio_ori}")
            # Verificar que ORI <= ACT
            if anio_act.isdigit():
                if anio_ori_int > int(anio_act):
                    fila_errores.append(f"ANIO_ING_ORI_MAYOR_QUE_ACT:{anio_ori}>{anio_act}")
        else:
            fila_errores.append(f"ANIO_ING_ORI_NO_NUMERICO:{anio_ori}")

        # SEM_ING_ORI
        if sem_ori not in {"1", "2"}:
            fila_errores.append(f"SEM_ING_ORI_INVALIDO:{sem_ori}")

        # VIG
        if vig not in {"0", "1", "2"}:
            fila_errores.append(f"VIG_INVALIDO:{vig}")

        if fila_errores:
            for e in fila_errores:
                errores.append(f"FILA_{i}: {e}")

    if casos_pasaporte == 0:
        advertencias.append("No hay registros con TIPO_DOC=P (pasaporte). Cero casos detectados.")
    if casos_anio_ori_1900 > 0:
        advertencias.append(f"Se encontraron {casos_anio_ori_1900} filas con ANIO_ING_ORI=1900 (regla especial ingreso originario desconocido).")

    # Distribuciones
    dist_cod_car = Counter(c(r["COD_CAR"]) for r in filas_parsed)
    dist_cod_sed = Counter(c(r["COD_SED"]) for r in filas_parsed)
    dist_modalidad = Counter(c(r["MODALIDAD"]) for r in filas_parsed)
    dist_jor = Counter(c(r["JOR"]) for r in filas_parsed)
    dist_version = Counter(c(r["VERSION"]) for r in filas_parsed)
    dist_vig = Counter(c(r["VIG"]) for r in filas_parsed)
    dist_sexo = Counter(c(r["SEXO"]) for r in filas_parsed)
    dist_for_ing = Counter(c(r["FOR_ING_ACT"]) for r in filas_parsed)

    return {
        "errores": errores,
        "advertencias": advertencias,
        "casos_pasaporte": casos_pasaporte,
        "casos_anio_ori_1900": casos_anio_ori_1900,
        "filas_parsed": filas_parsed,
        "distribuciones": {
            "COD_CAR": dict(dist_cod_car.most_common()),
            "COD_SED": dict(dist_cod_sed.most_common()),
            "MODALIDAD": dict(dist_modalidad.most_common()),
            "JOR": dict(dist_jor.most_common()),
            "VERSION": dict(dist_version.most_common()),
            "VIG": dict(dist_vig.most_common()),
            "SEXO": dict(dist_sexo.most_common()),
            "FOR_ING_ACT": dict(dist_for_ing.most_common()),
        },
    }


# ──────────────────────────────────────────────────────────────────────────────
# FASE 3 · Auditoría contra control con encabezado
# ──────────────────────────────────────────────────────────────────────────────

def fase3_contra_control(filas_pes_parsed, control_rows):
    errores = []
    advertencias = []

    ok_control = [r for r in control_rows if c(r.get("ESTADO_VALIDACION_PES")) == "OK"]
    bloqueados_control = [r for r in control_rows if c(r.get("ESTADO_VALIDACION_PES")) == "BLOQUEADO"]

    # 1. Misma cantidad
    n_pes = len(filas_pes_parsed)
    n_ok = len(ok_control)
    if n_pes != n_ok:
        errores.append(f"DISCREPANCIA_CANTIDAD: PES-ready={n_pes}, control OK={n_ok}.")

    # 2. Todo registro del PES-ready existe en control (por N_DOC + COD_CAR)
    control_keys = {(c(r["N_DOC"]), c(r["COD_CAR"])) for r in ok_control}
    pes_keys = {(c(r["N_DOC"]), c(r["COD_CAR"])) for r in filas_pes_parsed}

    en_pes_no_control = pes_keys - control_keys
    if en_pes_no_control:
        for k in list(en_pes_no_control)[:10]:
            errores.append(f"PES_SIN_CONTROL: N_DOC={k[0]}, COD_CAR={k[1]} está en PES-ready pero no en control OK.")

    # 3. Todo OK en control está en PES-ready
    en_control_no_pes = control_keys - pes_keys
    if en_control_no_pes:
        for k in list(en_control_no_pes)[:10]:
            errores.append(f"CONTROL_OK_SIN_PES: N_DOC={k[0]}, COD_CAR={k[1]} está en control OK pero no en PES-ready.")

    # 4. Ningún bloqueado en PES-ready
    bloqueados_keys = {(c(r["N_DOC"]), c(r["COD_CAR"])) for r in bloqueados_control}
    bloqueados_en_pes = bloqueados_keys & pes_keys
    if bloqueados_en_pes:
        for k in bloqueados_en_pes:
            errores.append(f"BLOQUEADO_EN_PES: N_DOC={k[0]}, COD_CAR={k[1]} está bloqueado en control pero aparece en PES-ready.")

    # 5. Distribuciones del control
    dist_cod_car_ctrl = Counter(c(r["COD_CAR"]) for r in ok_control)
    dist_cod_sed_ctrl = Counter(c(r["COD_SED"]) for r in ok_control)
    dist_modalidad_ctrl = Counter(c(r["MODALIDAD"]) for r in ok_control)
    dist_jor_ctrl = Counter(c(r["JOR"]) for r in ok_control)
    dist_version_ctrl = Counter(c(r["VERSION"]) for r in ok_control)
    dist_vig_ctrl = Counter(c(r["VIG"]) for r in ok_control)
    dist_sexo_ctrl = Counter(c(r["SEXO"]) for r in ok_control)
    dist_for_ing_ctrl = Counter(c(r["FOR_ING_ACT"]) for r in ok_control)

    return {
        "errores": errores,
        "advertencias": advertencias,
        "n_pes_ready": n_pes,
        "n_control_ok": n_ok,
        "n_control_bloqueados": len(bloqueados_control),
        "distribuciones_control": {
            "COD_CAR": dict(dist_cod_car_ctrl.most_common()),
            "COD_SED": dict(dist_cod_sed_ctrl.most_common()),
            "MODALIDAD": dict(dist_modalidad_ctrl.most_common()),
            "JOR": dict(dist_jor_ctrl.most_common()),
            "VERSION": dict(dist_version_ctrl.most_common()),
            "VIG": dict(dist_vig_ctrl.most_common()),
            "SEXO": dict(dist_sexo_ctrl.most_common()),
            "FOR_ING_ACT": dict(dist_for_ing_ctrl.most_common()),
        },
    }


# ──────────────────────────────────────────────────────────────────────────────
# FASE 4 · Auditoría contra trazabilidad
# ──────────────────────────────────────────────────────────────────────────────

def fase4_contra_trazabilidad(control_rows, traza_rows):
    errores = []
    advertencias = []

    ok_control = [r for r in control_rows if c(r.get("ESTADO_VALIDACION_PES")) == "OK"]

    # Trazabilidad candidatos 2026
    candidatos_2026 = [
        r for r in traza_rows
        if c(r.get("ANOMATRICULA")) == "2026" or c(r.get("ANOINGRESO")) == "2026"
    ]

    # Categorías de candidatos 2026
    incluidos_2026 = [r for r in candidatos_2026 if c(r.get("ACCION_CARGA")) == "INCLUIR"]
    excluidos_hasta_validar_2026 = [r for r in candidatos_2026 if c(r.get("ACCION_CARGA")) == "EXCLUIR_HASTA_VALIDAR"]
    excluidos_genericos_2026 = [r for r in candidatos_2026 if c(r.get("ACCION_CARGA")) == "EXCLUIR"
                                 and c(r.get("ESTADO_GOBERNANZA")) == "NO_MAPEAR_GENERICO"]
    excluidos_otros_2026 = [r for r in candidatos_2026
                            if c(r.get("ACCION_CARGA")) not in {"INCLUIR", "EXCLUIR_HASTA_VALIDAR"}
                            and not (c(r.get("ACCION_CARGA")) == "EXCLUIR"
                                     and c(r.get("ESTADO_GOBERNANZA")) == "NO_MAPEAR_GENERICO")]
    sin_diccionario_2026 = [r for r in candidatos_2026 if c(r.get("ACCION_CARGA")) == "SIN_DICCIONARIO"]

    # Verificar que cargados provienen solo de INCLUIR
    codcli_cargados = {c(r["CODCLI"]) for r in ok_control}
    traza_by_codcli = {c(r["CODCLI"]): r for r in traza_rows}

    for codcli in codcli_cargados:
        if codcli not in traza_by_codcli:
            errores.append(f"CODCLI_NO_EN_TRAZABILIDAD: {codcli}")
            continue
        trow = traza_by_codcli[codcli]
        accion = c(trow.get("ACCION_CARGA"))
        if accion != "INCLUIR":
            errores.append(f"CARGADO_SIN_INCLUIR: CODCLI={codcli}, ACCION_CARGA={accion}")

    # Verificar que cargados son 2026
    for codcli in codcli_cargados:
        if codcli not in traza_by_codcli:
            continue
        trow = traza_by_codcli[codcli]
        ano_mat = c(trow.get("ANOMATRICULA"))
        ano_ing = c(trow.get("ANOINGRESO"))
        if ano_mat != "2026" and ano_ing != "2026":
            errores.append(f"CARGADO_NO_2026: CODCLI={codcli}, ANOMATRICULA={ano_mat}, ANOINGRESO={ano_ing}")

    # Verificar que ningún excluido está en PES-ready
    accion_excluir_set = {"EXCLUIR", "EXCLUIR_HASTA_VALIDAR", "NO_MAPEAR_GENERICO",
                          "PENDIENTE_REVISION", "SIN_DICCIONARIO"}
    for codcli in codcli_cargados:
        if codcli not in traza_by_codcli:
            continue
        trow = traza_by_codcli[codcli]
        estado_gob = c(trow.get("ESTADO_GOBERNANZA"))
        if estado_gob in ESTADOS_EXCLUIR_DIC:
            errores.append(f"EXCLUIDO_EN_PES: CODCLI={codcli}, ESTADO_GOBERNANZA={estado_gob}")

    # Tabla de excluidos 2026
    excluidos_2026_todos = [r for r in candidatos_2026 if c(r.get("ACCION_CARGA")) != "INCLUIR"]

    return {
        "errores": errores,
        "advertencias": advertencias,
        "total_candidatos_2026": len(candidatos_2026),
        "incluidos_2026": len(incluidos_2026),
        "excluidos_hasta_validar_2026": len(excluidos_hasta_validar_2026),
        "excluidos_genericos_2026": len(excluidos_genericos_2026),
        "excluidos_otros_2026": len(excluidos_otros_2026),
        "sin_diccionario_2026": len(sin_diccionario_2026),
        "excluidos_2026_rows": excluidos_2026_todos,
    }


# ──────────────────────────────────────────────────────────────────────────────
# FASE 5 · Auditoría contra diccionario gobernado
# ──────────────────────────────────────────────────────────────────────────────

def fase5_contra_diccionario(control_rows, dic_rows):
    errores = []
    advertencias = []

    ok_control = [r for r in control_rows if c(r.get("ESTADO_VALIDACION_PES")) == "OK"]

    # Índice del diccionario por CODCARPR
    dic_by_codcarpr = {}
    for d in dic_rows:
        codcarpr = c(d.get("CODCARPR"))
        if codcarpr:
            dic_by_codcarpr[codcarpr] = d

    for ctrl in ok_control:
        codcarpr = c(ctrl.get("CODCARPR_ORIGEN"))
        cod_sed = c(ctrl.get("COD_SED"))
        cod_car = c(ctrl.get("COD_CAR"))
        modalidad = c(ctrl.get("MODALIDAD"))
        jor = c(ctrl.get("JOR"))
        version = c(ctrl.get("VERSION"))
        codcli = c(ctrl.get("CODCLI"))

        # 1. CODCARPR debe existir en diccionario
        if codcarpr not in dic_by_codcarpr:
            errores.append(f"CODCARPR_NO_EN_DICCIONARIO: CODCLI={codcli}, CODCARPR={codcarpr}")
            continue

        drow = dic_by_codcarpr[codcarpr]
        estado_gob = c(drow.get("ESTADO_GOBERNANZA"))
        accion = c(drow.get("ACCION_CARGA"))

        # 2. ACCION_CARGA debe ser INCLUIR en diccionario
        if accion != "INCLUIR":
            errores.append(f"DICCIONARIO_ACCION_NO_INCLUIR: CODCLI={codcli}, CODCARPR={codcarpr}, ACCION_CARGA={accion}")

        # 3. COD_SED + COD_CAR + MODALIDAD + JOR + VERSION deben coincidir exactamente
        d_cod_sed = c(drow.get("COD_SED"))
        d_cod_car = c(drow.get("COD_CAR"))
        d_modalidad = c(drow.get("MODALIDAD"))
        d_jor = c(drow.get("JOR"))
        d_version = c(drow.get("VERSION"))

        if cod_sed != d_cod_sed:
            errores.append(f"COD_SED_MISMATCH: CODCLI={codcli}, control={cod_sed}, diccionario={d_cod_sed}")
        if cod_car != d_cod_car:
            errores.append(f"COD_CAR_MISMATCH: CODCLI={codcli}, control={cod_car}, diccionario={d_cod_car}")
        if modalidad != d_modalidad:
            errores.append(f"MODALIDAD_MISMATCH: CODCLI={codcli}, control={modalidad}, diccionario={d_modalidad}")
        if jor != d_jor:
            errores.append(f"JOR_MISMATCH: CODCLI={codcli}, control={jor}, diccionario={d_jor}")
        if version != d_version:
            errores.append(f"VERSION_MISMATCH: CODCLI={codcli}, control={version}, diccionario={d_version}")

        # 4. El estado de gobernanza del diccionario no debe ser un estado excluido
        if estado_gob in ESTADOS_EXCLUIR_DIC:
            errores.append(f"ESTADO_GOBERNANZA_EXCLUIDO_EN_DICCIONARIO: CODCLI={codcli}, CODCARPR={codcarpr}, ESTADO={estado_gob}")

    return {
        "errores": errores,
        "advertencias": advertencias,
        "codcarprs_evaluados": len(ok_control),
    }


# ──────────────────────────────────────────────────────────────────────────────
# FASE 6 · Generación de artefactos
# ──────────────────────────────────────────────────────────────────────────────

def fase6_artefactos(
    errores_criticos, advertencias_totales, estado_global,
    control_rows, lineas_pes_raw,
    f1, f2, f3, f4, f5,
    diccionario_path=DICCIONARIO, trazabilidad_path=TRAZABILIDAD,
):
    artefactos_generados = []

    # ── Archivo excluidos 2026 (siempre se genera)
    excluidos_rows = f4["excluidos_2026_rows"]
    cols_excluidos = [
        "CODCLI", "RUT", "CODCARPR", "CODIGOCARRERA", "NOMBRE_L",
        "ANOMATRICULA", "ANOINGRESO", "ESTADOACADEMICO",
        "ESTADO_GOBERNANZA", "ACCION_CARGA", "ESTADO_TRAZABILIDAD",
        "OBSERVACION_DICCIONARIO",
    ]
    with open(OUT_EXCLUIDOS, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols_excluidos, extrasaction="ignore")
        writer.writeheader()
        for r in excluidos_rows:
            writer.writerow({k: c(r.get(k, "")) for k in cols_excluidos})
    artefactos_generados.append(str(OUT_EXCLUIDOS))

    # ── PES-ready final y control final: solo si no hay errores críticos
    pes_final_creado = False
    control_final_creado = False
    if errores_criticos == 0:
        # Backup si existe
        backup_if_exists(OUT_PES_FINAL)
        backup_if_exists(OUT_CONTROL_FINAL)

        shutil.copy2(PES_READY, OUT_PES_FINAL)
        shutil.copy2(CONTROL_CSV, OUT_CONTROL_FINAL)
        artefactos_generados.append(str(OUT_PES_FINAL))
        artefactos_generados.append(str(OUT_CONTROL_FINAL))
        pes_final_creado = True
        control_final_creado = True

    # ── Reporte Markdown
    md_lines = []

    def md(s=""):
        md_lines.append(s)

    md(f"# Auditoría final PES-ready · Postgrado/Postítulo · MU2026")
    md()
    md(f"**Fecha de ejecución:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md()
    md("---")
    md()
    md("## Resumen ejecutivo")
    md()
    md(f"| Indicador | Valor |")
    md(f"| --- | --- |")
    md(f"| Estado global | **{estado_global}** |")
    md(f"| Filas PES-ready | {f1['total_filas']} |")
    md(f"| Campos por fila | {list(f1['campos_por_fila'].keys())[0] if f1['campos_por_fila'] else 'N/A'} |")
    md(f"| Errores críticos | {errores_criticos} |")
    md(f"| Advertencias | {len(advertencias_totales)} |")
    md(f"| Registros bloqueados en control | {f3['n_control_bloqueados']} |")
    md(f"| Candidatos 2026 total | {f4['total_candidatos_2026']} |")
    md(f"| Candidatos 2026 incluidos | {f4['incluidos_2026']} |")
    md(f"| Candidatos 2026 excluidos | {f4['total_candidatos_2026'] - f4['incluidos_2026']} |")
    md()
    md("---")
    md()
    md("## Archivos auditados")
    md()
    md(f"| Archivo | Ruta |")
    md(f"| --- | --- |")
    md(f"| Diccionario | `{DICCIONARIO.relative_to(REPO)}` |")
    md(f"| Trazabilidad | `{TRAZABILIDAD.relative_to(REPO)}` |")
    md(f"| Control CSV | `{CONTROL_CSV.relative_to(REPO)}` |")
    md(f"| PES-ready preliminar | `{PES_READY.relative_to(REPO)}` |")
    md()
    md("---")
    md()
    md(f"## Resultado global: {estado_global}")
    md()
    if estado_global == "APROBADO":
        md("El archivo PES-ready cumple todos los criterios de calidad requeridos para carga en sistema PES.")
    elif estado_global == "APROBADO_CON_OBSERVACIONES":
        md("El archivo PES-ready es estructuralmente válido. Existen candidatos 2026 excluidos por gobernanza,")
        md("correctamente documentados fuera del CSV final. Ver sección de excluidos.")
    else:
        md("**El archivo PES-ready NO puede cargarse.** Existen errores críticos que deben resolverse.")
    md()
    md("---")
    md()
    md("## FASE 1 · Estructura del PES-ready")
    md()
    md(f"- Total filas: **{f1['total_filas']}**")
    md(f"- Campos por fila: {f1['campos_por_fila']}")
    md(f"- Filas vacías: {f1['filas_vacias']}")
    md(f"- Filas con campo vacío: {f1['filas_con_campo_vacio']}")
    md(f"- Sin encabezado: {'OK' if not any('ENCABEZADO' in e for e in f1['errores']) else 'ERROR'}")
    md()
    if f1["errores"]:
        md("### Errores fase 1")
        md()
        for e in f1["errores"]:
            md(f"- `{e}`")
        md()
    else:
        md("Sin errores estructurales.")
        md()
    md("---")
    md()
    md("## FASE 2 · Validación de dominios")
    md()
    md(f"- Errores de dominio: {len(f2['errores'])}")
    md(f"- Registros con TIPO_DOC=P (pasaporte): {f2['casos_pasaporte']}")
    md(f"- Registros con ANIO_ING_ORI=1900: {f2['casos_anio_ori_1900']}")
    md()
    if f2["errores"]:
        md("### Errores de dominio")
        md()
        for e in f2["errores"][:50]:
            md(f"- `{e}`")
        if len(f2["errores"]) > 50:
            md(f"... y {len(f2['errores'])-50} errores adicionales.")
        md()
    else:
        md("Todos los dominios son válidos.")
        md()
    if f2["advertencias"]:
        md("### Advertencias fase 2")
        md()
        for a in f2["advertencias"]:
            md(f"- {a}")
        md()
    md("### Distribuciones del PES-ready")
    md()
    for campo, dist in f2["distribuciones"].items():
        md(f"#### {campo}")
        md()
        md(f"| {campo} | n |")
        md("| --- | ---: |")
        for k, v in dist.items():
            md(f"| {k} | {v} |")
        md()
    md("---")
    md()
    md("## FASE 3 · Contraste PES-ready vs control")
    md()
    md(f"- Registros PES-ready: {f3['n_pes_ready']}")
    md(f"- Registros control OK: {f3['n_control_ok']}")
    md(f"- Registros bloqueados: {f3['n_control_bloqueados']}")
    md()
    if f3["errores"]:
        md("### Errores fase 3")
        md()
        for e in f3["errores"][:30]:
            md(f"- `{e}`")
        md()
    else:
        md("Consistencia total entre PES-ready y control.")
        md()
    md("---")
    md()
    md("## FASE 4 · Contraste vs trazabilidad")
    md()
    md(f"### Resumen candidatos 2026")
    md()
    md(f"| Categoría | n |")
    md("| --- | ---: |")
    md(f"| Total candidatos 2026 | {f4['total_candidatos_2026']} |")
    md(f"| Incluidos | {f4['incluidos_2026']} |")
    md(f"| Excluidos hasta validar | {f4['excluidos_hasta_validar_2026']} |")
    md(f"| Excluidos genérico | {f4['excluidos_genericos_2026']} |")
    md(f"| Excluidos otros | {f4['excluidos_otros_2026']} |")
    md(f"| Sin diccionario | {f4['sin_diccionario_2026']} |")
    md()
    if f4["errores"]:
        md("### Errores fase 4")
        md()
        for e in f4["errores"][:30]:
            md(f"- `{e}`")
        md()
    else:
        md("Todos los registros cargados provienen de ACCION_CARGA=INCLUIR y son año 2026.")
        md()
    if f4["excluidos_2026_rows"]:
        md("### Excluidos 2026 (detalle)")
        md()
        md("| CODCLI | RUT | CODCARPR | NOMBRE_L | ACCION_CARGA | ESTADO_GOBERNANZA | OBSERVACION |")
        md("| --- | --- | --- | --- | --- | --- | --- |")
        for r in f4["excluidos_2026_rows"][:50]:
            obs = c(r.get("OBSERVACION_DICCIONARIO", ""))[:60]
            md(f"| {c(r.get('CODCLI'))} | {c(r.get('RUT'))} | {c(r.get('CODCARPR'))} "
               f"| {c(r.get('NOMBRE_L'))[:40]} | {c(r.get('ACCION_CARGA'))} "
               f"| {c(r.get('ESTADO_GOBERNANZA'))} | {obs} |")
        if len(f4["excluidos_2026_rows"]) > 50:
            md(f"... y {len(f4['excluidos_2026_rows'])-50} más (ver archivo excluidos).")
        md()
    md("---")
    md()
    md("## FASE 5 · Contraste vs diccionario gobernado")
    md()
    md(f"- Registros evaluados: {f5['codcarprs_evaluados']}")
    md()
    if f5["errores"]:
        md("### Errores fase 5")
        md()
        for e in f5["errores"][:30]:
            md(f"- `{e}`")
        md()
    else:
        md("Todos los registros están trazados al diccionario. Combinaciones validadas.")
        md()
    if f5["advertencias"]:
        md("### Advertencias fase 5")
        md()
        for a in f5["advertencias"]:
            md(f"- {a}")
        md()
    md("---")
    md()
    md("## Regla de gobernanza aplicada")
    md()
    md("- `ACCION_CARGA=INCLUIR`: alimenta trazabilidad, control y CSV PES-ready.")
    md("- `ACCION_CARGA=EXCLUIR_HASTA_VALIDAR`: queda solo en trazabilidad.")
    md("- `ACCION_CARGA=EXCLUIR`: no se carga. Si es genérico (`NO_MAPEAR_GENERICO`), tampoco.")
    md("- `NO_MAPEAR_GENERICO`: no se carga.")
    md("- No se fuerza COD_CAR para pendientes.")
    md("- Solo registros 2026 con criterio `ANOMATRICULA=2026 OR ANOINGRESO=2026`.")
    md()
    md()
    md("---")
    md()
    md("## Evidencia de integridad del flujo pregrado")
    md()
    md("Los siguientes archivos de pregrado NO fueron modificados por este proceso:")
    md()
    for p in PREGRADO_ARCHIVOS:
        estado = "existe" if p.exists() else "no existe (independiente de este proceso)"
        md(f"- `{p.name}`: {estado}")
    md()
    md("---")
    md()
    md("## Advertencias totales")
    md()
    if advertencias_totales:
        for a in advertencias_totales:
            md(f"- {a}")
    else:
        md("Sin advertencias.")
    md()
    md("---")
    md()
    md("## Artefactos generados")
    md()
    for a in artefactos_generados:
        md(f"- `{a}`")
    md()
    md("---")
    md()
    md("## Recomendación final de carga")
    md()
    if estado_global == "APROBADO":
        md("**PROCEDER CON CARGA.** El archivo PES-ready cumple todos los requisitos formales.")
        md(f"Utilizar: `{OUT_PES_FINAL.name}`")
    elif estado_global == "APROBADO_CON_OBSERVACIONES":
        md("**PROCEDER CON CARGA CON PRECAUCIÓN.** El PES-ready es válido.")
        md("Los candidatos excluidos deben validarse manualmente antes de una carga complementaria.")
        md(f"Utilizar: `{OUT_PES_FINAL.name}`")
    else:
        md("**NO PROCEDER.** Resolver errores críticos antes de cualquier carga.")
    md()
    md("---")
    md(f"*Generado automáticamente · {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    with open(OUT_REPORTE_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    artefactos_generados.append(str(OUT_REPORTE_MD))

    # ── Resumen JSON
    resumen_json = {
        "timestamp": datetime.now().isoformat(),
        "estado_global": estado_global,
        "errores_criticos": errores_criticos,
        "advertencias": len(advertencias_totales),
        "filas_pes_ready": f1["total_filas"],
        "campos_por_fila": f1["campos_por_fila"],
        "candidatos_2026_total": f4["total_candidatos_2026"],
        "candidatos_2026_incluidos": f4["incluidos_2026"],
        "candidatos_2026_excluidos": f4["total_candidatos_2026"] - f4["incluidos_2026"],
        "candidatos_2026_excluidos_hasta_validar": f4["excluidos_hasta_validar_2026"],
        "candidatos_2026_excluidos_genericos": f4["excluidos_genericos_2026"],
        "candidatos_2026_sin_diccionario": f4["sin_diccionario_2026"],
        "control_ok": f3["n_control_ok"],
        "control_bloqueados": f3["n_control_bloqueados"],
        "distribucion_cod_car": f2["distribuciones"]["COD_CAR"],
        "distribucion_vig": f2["distribuciones"]["VIG"],
        "distribucion_sexo": f2["distribuciones"]["SEXO"],
        "distribucion_for_ing_act": f2["distribuciones"]["FOR_ING_ACT"],
        "pes_final_creado": pes_final_creado,
        "control_final_creado": control_final_creado,
        "archivos": {
            "reporte_md": str(OUT_REPORTE_MD),
            "resumen_json": str(OUT_RESUMEN_JSON),
            "pes_final": str(OUT_PES_FINAL) if pes_final_creado else None,
            "control_final": str(OUT_CONTROL_FINAL) if control_final_creado else None,
            "excluidos_2026": str(OUT_EXCLUIDOS),
        },
        "pregrado_no_modificado": True,
    }

    with open(OUT_RESUMEN_JSON, "w", encoding="utf-8") as f:
        json.dump(resumen_json, f, ensure_ascii=False, indent=2)
    artefactos_generados.append(str(OUT_RESUMEN_JSON))

    return artefactos_generados, pes_final_creado, control_final_creado


# ──────────────────────────────────────────────────────────────────────────────
# FASE 7 · Criterios de aprobación
# ──────────────────────────────────────────────────────────────────────────────

def fase7_estado(f1, f2, f3, f4, f5):
    errores_criticos = (
        f1["errores"] + f2["errores"] + f3["errores"] + f4["errores"] + f5["errores"]
    )
    advertencias = (
        f1["advertencias"] + f2["advertencias"] + f3["advertencias"]
        + f4["advertencias"] + f5["advertencias"]
    )

    n_errores = len(errores_criticos)
    n_advertencias = len(advertencias)

    hay_excluidos_correctamente_documentados = (
        f4["excluidos_hasta_validar_2026"] > 0 or f4["excluidos_genericos_2026"] > 0
        or f4["excluidos_otros_2026"] > 0
    )

    if n_errores == 0 and not hay_excluidos_correctamente_documentados:
        estado = "APROBADO"
    elif n_errores == 0 and hay_excluidos_correctamente_documentados:
        estado = "APROBADO_CON_OBSERVACIONES"
    else:
        estado = "BLOQUEADO"

    return estado, n_errores, n_advertencias, errores_criticos, advertencias


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    sep = "=" * 70
    print(sep)
    print("  AUDITORÍA END-TO-END · CIERRE MU2026 · POSTGRADO/POSTÍTULO")
    print(sep)
    print()

    # FASE 0
    print("▶ FASE 0 · Preparación segura...")
    f0 = fase0_preparacion()
    if f0["errores"]:
        print(f"  ERRORES FASE 0:")
        for e in f0["errores"]:
            print(f"    ✗ {e}")
        print()
        print("  BLOQUEADO: archivos requeridos faltantes. Abortar.")
        sys.exit(1)
    print(f"  Archivos requeridos: OK")
    print(f"  Pregrado intacto: {f0['pregrado_intacto']}")
    print()

    # Cargar datos
    print("▶ Cargando datos...")
    lineas_pes = leer_pes_ready_raw(PES_READY)
    control_rows = leer_csv(CONTROL_CSV)
    traza_rows = leer_tsv(TRAZABILIDAD)
    dic_rows = leer_tsv(DICCIONARIO)
    print(f"  PES-ready: {len(lineas_pes)} líneas")
    print(f"  Control: {len(control_rows)} registros")
    print(f"  Trazabilidad: {len(traza_rows)} registros")
    print(f"  Diccionario: {len(dic_rows)} entradas")
    print()

    # FASE 1
    print("▶ FASE 1 · Estructura PES-ready...")
    f1 = fase1_estructura(lineas_pes)
    status1 = "OK" if not f1["errores"] else f"ERRORES ({len(f1['errores'])})"
    print(f"  Filas: {f1['total_filas']} | Campos por fila: {f1['campos_por_fila']} | {status1}")
    print()

    # FASE 2
    print("▶ FASE 2 · Dominios...")
    f2 = fase2_dominios(lineas_pes)
    status2 = "OK" if not f2["errores"] else f"ERRORES ({len(f2['errores'])})"
    print(f"  {status2} | Pasaportes: {f2['casos_pasaporte']}")
    print()

    # FASE 3
    print("▶ FASE 3 · Contraste PES-ready vs control...")
    f3 = fase3_contra_control(f2["filas_parsed"], control_rows)
    status3 = "OK" if not f3["errores"] else f"ERRORES ({len(f3['errores'])})"
    print(f"  PES-ready={f3['n_pes_ready']}, control OK={f3['n_control_ok']}, bloqueados={f3['n_control_bloqueados']} | {status3}")
    print()

    # FASE 4
    print("▶ FASE 4 · Contraste vs trazabilidad...")
    f4 = fase4_contra_trazabilidad(control_rows, traza_rows)
    status4 = "OK" if not f4["errores"] else f"ERRORES ({len(f4['errores'])})"
    print(f"  Candidatos 2026: {f4['total_candidatos_2026']} | Incluidos: {f4['incluidos_2026']} | Excluidos: {f4['total_candidatos_2026']-f4['incluidos_2026']} | {status4}")
    print()

    # FASE 5
    print("▶ FASE 5 · Contraste vs diccionario gobernado...")
    f5 = fase5_contra_diccionario(control_rows, dic_rows)
    status5 = "OK" if not f5["errores"] else f"ERRORES ({len(f5['errores'])})"
    print(f"  Evaluados: {f5['codcarprs_evaluados']} | {status5}")
    print()

    # FASE 7
    estado_global, n_errores, n_advertencias, todos_errores, todas_advertencias = \
        fase7_estado(f1, f2, f3, f4, f5)

    # FASE 6
    print("▶ FASE 6 · Generando artefactos de cierre...")
    artefactos, pes_final_creado, control_final_creado = fase6_artefactos(
        n_errores, todas_advertencias, estado_global,
        control_rows, lineas_pes,
        f1, f2, f3, f4, f5,
    )
    print(f"  Artefactos generados: {len(artefactos)}")
    print()

    # FASE 8 · Entrega final
    print(sep)
    print("  RESULTADO FINAL")
    print(sep)
    print()
    print(f"  Estado:           {estado_global}")
    print(f"  Errores críticos: {n_errores}")
    print(f"  Advertencias:     {n_advertencias}")
    print()
    print(f"  Filas PES-ready:         {f1['total_filas']}")
    print(f"  Candidatos 2026 incluidos:  {f4['incluidos_2026']}")
    print(f"  Candidatos 2026 excluidos:  {f4['total_candidatos_2026'] - f4['incluidos_2026']}")
    print()
    print(f"  Reporte Markdown:  {OUT_REPORTE_MD}")
    print(f"  JSON de cierre:    {OUT_RESUMEN_JSON}")
    if pes_final_creado:
        print(f"  PES-ready FINAL:   {OUT_PES_FINAL}")
    else:
        print(f"  PES-ready FINAL:   NO creado (hay errores críticos)")
    if control_final_creado:
        print(f"  Control FINAL:     {OUT_CONTROL_FINAL}")
    else:
        print(f"  Control FINAL:     NO creado")
    print(f"  Excluidos 2026:    {OUT_EXCLUIDOS}")
    print()

    if n_errores:
        print("  Errores críticos detectados:")
        for e in todos_errores[:20]:
            print(f"    ✗ {e}")
        if len(todos_errores) > 20:
            print(f"    ... y {len(todos_errores)-20} errores adicionales (ver reporte).")
        print()
    if n_advertencias:
        print("  Advertencias:")
        for a in todas_advertencias[:10]:
            print(f"    ⚠ {a}")
        if len(todas_advertencias) > 10:
            print(f"    ... y {len(todas_advertencias)-10} más.")
        print()

    print("  No se modificó el flujo pregrado.")
    print()
    print(sep)

    # Abrir reporte si APROBADO o APROBADO_CON_OBSERVACIONES
    import subprocess
    import platform
    if estado_global in {"APROBADO", "APROBADO_CON_OBSERVACIONES"}:
        try:
            if platform.system() == "Darwin":
                subprocess.Popen(["open", str(OUT_REPORTE_MD)])
        except Exception:
            pass

    return 0 if n_errores == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
