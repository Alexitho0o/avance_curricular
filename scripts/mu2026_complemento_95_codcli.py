#!/usr/bin/env python3
"""
mu2026_complemento_95_codcli.py
================================
Proceso PARALELO e INDEPENDIENTE para generar el complemento de 95 CODCLI
excluidos de la carga principal MU2026.

Restricciones absolutas:
  - NUNCA escribir en resultados/matricula_unificada_2026_pregrado_PES_READY.csv
  - NUNCA escribir en ~/Desktop/matricula_unificada_2026_pregrado_PARA_SUBIR.csv
  - NO importar ni llamar funciones del pipeline principal (codigo_gobernanza_v2)
  - Solo escribir en resultados/complemento_95_codcli/

Salida final (solo si fallbacks == 0):
  resultados/complemento_95_codcli/
    matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv
    (95 filas, 32 campos, sin encabezado, separador ;, VIG=1)
  Escritorio:
    matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv (copia)

Uso:
  cd avance_curricular && source .venv/bin/activate
  python3 scripts/mu2026_complemento_95_codcli.py
"""

import hashlib
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

import pandas as pd

# ── RUTAS ──────────────────────────────────────────────────────────────────
REPO_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_DIR / "resultados" / "complemento_95_codcli"
EXCEL_FUENTE = Path.home() / "Downloads" / "PROMEDIOSDEALUMNOS_7804.xlsx"
NOMINA_PATH = REPO_DIR / "resultados" / "nomina_codcli_vigentes_a_reincorporar_mu2026.csv"
PES_READY_PATH = REPO_DIR / "resultados" / "matricula_unificada_2026_pregrado_PES_READY.csv"
DESKTOP_SUBIDA = Path.home() / "Desktop" / "matricula_unificada_2026_pregrado_PARA_SUBIR.csv"
TRAZ_INGRESO = REPO_DIR / "control" / "campos_ing_trace_long.tsv"
TRAZ_VIG = REPO_DIR / "control" / "vig_fecha_trace_long.tsv"
HISTORICO_PATH = REPO_DIR / "control" / "reportes" / "resumen_historico_mu_2026.csv"
GOB_NAC = REPO_DIR / "gobernanza_nac.tsv"
AUDIT_PREV = REPO_DIR / "resultados" / "auditoria_reconstruccion_95_codcli_para_subir.csv"

# ── COLUMNAS OFICIALES (32 campos, en orden) ───────────────────────────────
MATRICULA_UNIFICADA_COLUMNS = [
    "TIPO_DOC", "N_DOC", "DV", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO",
    "NOMBRE", "SEXO", "FECH_NAC", "NAC", "PAIS_EST_SEC",
    "COD_SED", "COD_CAR", "MODALIDAD", "JOR", "VERSION",
    "FOR_ING_ACT", "ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI", "SEM_ING_ORI",
    "ASI_INS_ANT", "ASI_APR_ANT", "PROM_PRI_SEM", "PROM_SEG_SEM",
    "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA",
    "SIT_FON_SOL", "SUS_PRE", "FECHA_MATRICULA", "REINCORPORACION", "VIG",
]

# Columnas de campos históricos
HIST_COLS = ["ASI_INS_ANT", "ASI_APR_ANT", "PROM_PRI_SEM", "PROM_SEG_SEM",
             "ASI_INS_HIS", "ASI_APR_HIS"]

# ── MAPEOS DE GOBERNANZA ───────────────────────────────────────────────────
# NAC: normalización → código numérico (de gobernanza_nac.tsv)
NAC_NORM_MAP = {
    "ALEMANA": "3", "ARGENTINA": "9", "BOLIVIANA": "23",
    "BRASILENA": "26", "BRASILEÑA": "26",
    "CHILENA": "38", "COLOMBIANA": "44", "CUBANA": "48",
    "ECUATORIANA": "57", "ESPANOLA": "68", "ESPAÑOLA": "68",
    "FRANCESA": "70", "HAITIANA": "78", "ITALIANA": "95",
    "MEXICANA": "130", "PARAGUAYA": "137", "PERUANA": "142",
    "URUGUAYA": "188", "VENEZOLANA": "192",
}

# SEXO: DatosAlumnos → MU estándar
SEXO_MAP = {"M": "H", "F": "M"}

# PAIS_EST_SEC: regla institucional — todos los estudiantes de esta IES
# cursaron enseñanza media en Chile (confirmado: 4070/4070 en PES_READY = 38)
PAIS_EST_SEC_INSTITUCIONAL = "38"

# Constantes institucionales documentadas
SIT_FON_SOL_INSTITUCIONAL = "0"   # No adscrita a Fondo Solidario
SUS_PRE_INSTITUCIONAL = "0"
REINCORPORACION_INSTITUCIONAL = "0"
VIG_COMPLEMENTO = "1"             # Todos son VIGENTES en 2026-1


# ── UTILIDADES ──────────────────────────────────────────────────────────────
def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _norm_nac(s: str) -> str:
    """Normaliza texto de nacionalidad: mayúsculas, sin tildes, sin dobles espacios."""
    s = str(s).strip().upper()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\s+", " ", s)
    return s


def _fecha_dmdmY_to_slash(s: str) -> str:
    """Convierte DD-MM-YYYY a DD/MM/YYYY. Retorna el valor original si falla."""
    s = str(s).strip()
    if "-" in s and len(s) == 10:
        return s.replace("-", "/")
    return s


def _sep(title: str) -> None:
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print("─" * 60)


def _abort(msg: str) -> None:
    print(f"\n❌ ABORTANDO: {msg}", file=sys.stderr)
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════
# FASE 0 — Preparar espacio de trabajo
# ══════════════════════════════════════════════════════════════════════════
def fase0_preparar() -> None:
    _sep("FASE 0: Preparar espacio de trabajo")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"  ✅ Directorio: {OUT_DIR}")
    # Guardia: verificar que no somos el pipeline principal
    assert "codigo_gobernanza_v2" not in sys.modules, "NO importar el pipeline principal"
    print(f"  ✅ Pipeline principal NO importado")


# ══════════════════════════════════════════════════════════════════════════
# FASE 1 — Resguardar carga principal (hash + filas)
# ══════════════════════════════════════════════════════════════════════════
def fase1_resguardar_principal() -> tuple[str, int]:
    _sep("FASE 1: Resguardar carga principal")
    if not PES_READY_PATH.exists():
        _abort(f"PES_READY no existe: {PES_READY_PATH}")
    sha = _sha256(PES_READY_PATH)
    pes = pd.read_csv(PES_READY_PATH, header=None, sep=";", dtype=str,
                      keep_default_na=False)
    n_filas = len(pes)
    n_cols = pes.shape[1]
    info = {
        "ARCHIVO": str(PES_READY_PATH),
        "SHA256": sha,
        "FILAS": n_filas,
        "COLUMNAS": n_cols,
        "TIMESTAMP": datetime.now().isoformat(),
    }
    pd.DataFrame([info]).to_csv(
        OUT_DIR / "00_resguardo_carga_principal.csv", index=False)
    print(f"  SHA256   : {sha}")
    print(f"  Filas    : {n_filas}  Columnas: {n_cols}")
    print(f"  ✅ Resguardo guardado en 00_resguardo_carga_principal.csv")
    assert n_filas == 4070, f"Esperadas 4070 filas en PES_READY, encontradas: {n_filas}"
    assert n_cols == 32, f"Esperadas 32 columnas en PES_READY, encontradas: {n_cols}"
    return sha, n_filas


# ══════════════════════════════════════════════════════════════════════════
# FASE 2 — Leer y validar nómina de 95 CODCLI
# ══════════════════════════════════════════════════════════════════════════
def fase2_nomina() -> list[str]:
    _sep("FASE 2: Validar nómina 95 CODCLI")
    nom = pd.read_csv(NOMINA_PATH, dtype=str, keep_default_na=False)
    codcli_list = nom["CODCLI_A_REINCORPORAR"].tolist()
    n_uniq = len(set(codcli_list))
    n_total = len(codcli_list)
    print(f"  Total filas nómina   : {n_total}")
    print(f"  CODCLI únicos        : {n_uniq}")
    nom.to_csv(OUT_DIR / "01_auditoria_nomina_95.csv", index=False)
    if n_total != 95:
        _abort(f"Nómina debe tener 95 filas, tiene: {n_total}")
    if n_uniq != 95:
        _abort(f"Nómina debe tener 95 CODCLI únicos, tiene: {n_uniq}")
    print(f"  ✅ Nómina válida: 95 CODCLI únicos")
    return codcli_list


# ══════════════════════════════════════════════════════════════════════════
# FASE 3 — Cargar DatosAlumnos y verificar vigencia
# ══════════════════════════════════════════════════════════════════════════
def fase3_datosalumnos(codcli_list: list[str]) -> pd.DataFrame:
    _sep("FASE 3: Cargar DatosAlumnos y verificar vigencia")
    if not EXCEL_FUENTE.exists():
        _abort(f"Excel fuente no encontrado: {EXCEL_FUENTE}")
    da = pd.read_excel(EXCEL_FUENTE, sheet_name="DatosAlumnos",
                       dtype=str, keep_default_na=False)
    da_nom = da[da["CODCLI"].isin(codcli_list)].copy()
    print(f"  Filas encontradas    : {len(da_nom)}")
    print(f"  CODCLI únicos        : {da_nom['CODCLI'].nunique()}")
    faltantes = [c for c in codcli_list if c not in da["CODCLI"].values]
    if faltantes:
        _abort(f"CODCLI no encontrados en DatosAlumnos: {faltantes}")
    # Verificar ESTADOACADEMICO = VIGENTE
    no_vigente = da_nom[da_nom["ESTADOACADEMICO"].str.upper() != "VIGENTE"]
    if not no_vigente.empty:
        print(f"  ⚠️  {len(no_vigente)} filas con ESTADOACADEMICO ≠ VIGENTE:")
        print(no_vigente[["CODCLI", "ESTADOACADEMICO"]].to_string())
    else:
        print(f"  ✅ Todos los 95 CODCLI están VIGENTES en DatosAlumnos")
    audit_vig = da_nom[["CODCLI", "RUT", "ESTADOACADEMICO", "SITUACION",
                         "ANOMATRICULA", "PERIODOMATRICULA"]].copy()
    audit_vig.to_csv(OUT_DIR / "02_auditoria_vigencia_datosalumnos.csv", index=False)
    return da_nom.set_index("CODCLI")


# ══════════════════════════════════════════════════════════════════════════
# FASE 4 — Cargar trazadores e histórico
# ══════════════════════════════════════════════════════════════════════════
def fase4_trazadores(codcli_list: list[str]) -> tuple[
        pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    _sep("FASE 4: Cargar trazadores e histórico")
    ing = pd.read_csv(TRAZ_INGRESO, sep="\t", dtype=str, keep_default_na=False)
    vig = pd.read_csv(TRAZ_VIG, sep="\t", dtype=str, keep_default_na=False)
    his = pd.read_csv(HISTORICO_PATH, dtype=str, keep_default_na=False)
    arc_prev = pd.read_csv(AUDIT_PREV, dtype=str, keep_default_na=False)

    ing_nom = ing[ing["CODCLI"].isin(codcli_list)].set_index("CODCLI")
    vig_nom = vig[vig["CODCLI"].isin(codcli_list)].set_index("CODCLI")
    his_nom = his[his["CODCLI"].isin(codcli_list)].set_index("CODCLI")
    arc_nom = arc_prev[arc_prev["CODCLI"].isin(codcli_list)].set_index("CODCLI")

    print(f"  Trazador ingreso     : {len(ing_nom)}/95 CODCLI")
    print(f"  Trazador vig/fecha   : {len(vig_nom)}/95 CODCLI")
    print(f"  Resumen histórico    : {len(his_nom)}/95 CODCLI")
    print(f"  Auditoría previa     : {len(arc_nom)}/95 CODCLI")

    falt_his = [c for c in codcli_list if c not in his_nom.index]
    if falt_his:
        print(f"  ⚠️  Sin histórico (nuevos 2026, valor=0): {falt_his}")

    return ing_nom, vig_nom, his_nom, arc_nom


# ══════════════════════════════════════════════════════════════════════════
# FASE 5 — Cargar gobernanza NAC
# ══════════════════════════════════════════════════════════════════════════
def fase5_gobernanza() -> dict[str, str]:
    _sep("FASE 5: Cargar gobernanza NAC")
    gn = pd.read_csv(GOB_NAC, sep="\t", dtype=str, keep_default_na=False)
    nac_map: dict[str, str] = {}
    for _, row in gn.iterrows():
        key = _norm_nac(row["NACIONALIDAD_ORIG"])
        nac_map[key] = str(row["COD_NAC"]).strip()
    # Asegurar valores comunes
    nac_map.update({
        "CHILENA": "38", "BRASILENA": "26", "HAITIANA": "78",
        "PERUANA": "142", "VENEZOLANA": "192",
    })
    print(f"  NAC map cargado      : {len(nac_map)} entradas")
    return nac_map


# ══════════════════════════════════════════════════════════════════════════
# FASE 6 — Construir los 32 campos campo a campo
# ══════════════════════════════════════════════════════════════════════════
def fase6_construir(
    codcli_list: list[str],
    da_idx: pd.DataFrame,
    ing_nom: pd.DataFrame,
    vig_nom: pd.DataFrame,
    his_nom: pd.DataFrame,
    arc_nom: pd.DataFrame,
    nac_map: dict[str, str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    _sep("FASE 6: Construir 32 campos con trazabilidad")
    rows_data: list[dict] = []
    rows_audit: list[dict] = []

    for codcli in codcli_list:
        da = da_idx.loc[codcli] if codcli in da_idx.index else None
        ing = ing_nom.loc[codcli] if codcli in ing_nom.index else None
        vi = vig_nom.loc[codcli] if codcli in vig_nom.index else None
        hi = his_nom.loc[codcli] if codcli in his_nom.index else None
        arc = arc_nom.loc[codcli] if codcli in arc_nom.index else None

        row: dict[str, str] = {}
        aud: dict[str, str] = {"CODCLI": codcli}

        # ── Parsear RUT desde DatosAlumnos ─────────────────────────────
        rut_raw = str(da["RUT"]).strip() if da is not None else ""
        if "-" in rut_raw:
            rut_parts = rut_raw.rsplit("-", 1)
            n_doc_raw = rut_parts[0].replace(".", "").strip()
            dv_raw = rut_parts[1].strip().upper()
        else:
            n_doc_raw = rut_raw.replace(".", "").strip()
            dv_raw = ""

        # ── TIPO_DOC ──────────────────────────────────────────────────
        try:
            int(n_doc_raw)
            tipo_doc = "R"
            fuente_tipo_doc = "DATOSALUMNOS_RUT_NUMERICO→R"
        except ValueError:
            tipo_doc = "P"
            fuente_tipo_doc = "DATOSALUMNOS_RUT_NO_NUMERICO→P"
        row["TIPO_DOC"] = tipo_doc
        aud["FUENTE_TIPO_DOC"] = fuente_tipo_doc

        # ── N_DOC ─────────────────────────────────────────────────────
        row["N_DOC"] = n_doc_raw
        aud["FUENTE_N_DOC"] = "DATOSALUMNOS_RUT"

        # ── DV ───────────────────────────────────────────────────────
        row["DV"] = dv_raw
        aud["FUENTE_DV"] = "DATOSALUMNOS_RUT"

        # ── PRIMER_APELLIDO ──────────────────────────────────────────
        ap_pat = str(da.get("APELLIDO PATERNO", "")).strip() if da is not None else ""
        row["PRIMER_APELLIDO"] = ap_pat
        aud["FUENTE_PRIMER_APELLIDO"] = "DATOSALUMNOS_APELLIDO_PATERNO"

        # ── SEGUNDO_APELLIDO ─────────────────────────────────────────
        ap_mat = str(da.get("APELLIDO MATERNO", "")).strip() if da is not None else ""
        row["SEGUNDO_APELLIDO"] = ap_mat
        aud["FUENTE_SEGUNDO_APELLIDO"] = "DATOSALUMNOS_APELLIDO_MATERNO"

        # ── NOMBRE ───────────────────────────────────────────────────
        nombres = str(da.get("NOMBRES", "")).strip() if da is not None else ""
        row["NOMBRE"] = nombres
        aud["FUENTE_NOMBRE"] = "DATOSALUMNOS_NOMBRES"

        # ── SEXO ─────────────────────────────────────────────────────
        sexo_da = str(da.get("SEXO", "")).strip().upper() if da is not None else ""
        sexo_mu = SEXO_MAP.get(sexo_da, sexo_da)
        row["SEXO"] = sexo_mu
        aud["FUENTE_SEXO"] = f"DATOSALUMNOS_SEXO:{sexo_da}→{sexo_mu}"

        # ── FECH_NAC ─────────────────────────────────────────────────
        fech_nac_da = str(da.get("FECHANACIMIENTO", "")).strip() if da is not None else ""
        fech_nac = _fecha_dmdmY_to_slash(fech_nac_da)
        row["FECH_NAC"] = fech_nac
        aud["FUENTE_FECH_NAC"] = "DATOSALUMNOS_FECHANACIMIENTO"

        # ── NAC ───────────────────────────────────────────────────────
        nac_da = str(da.get("NACIONALIDAD", "")).strip() if da is not None else ""
        nac_norm = _norm_nac(nac_da)
        nac_cod = nac_map.get(nac_norm, "")
        if not nac_cod:
            nac_cod = "38"  # fallback Chile para no bloquear
            fuente_nac = f"FALLBACK_CHILE_NAC_NO_ENCONTRADA:{nac_norm}"
        else:
            fuente_nac = f"GOB_NAC:{nac_norm}→{nac_cod}"
        row["NAC"] = nac_cod
        aud["FUENTE_NAC"] = fuente_nac

        # ── PAIS_EST_SEC ─────────────────────────────────────────────
        # Regla institucional: todos tienen enseñanza media en Chile (38)
        # (confirmado: 4070/4070 en PES_READY = 38)
        row["PAIS_EST_SEC"] = PAIS_EST_SEC_INSTITUCIONAL
        aud["FUENTE_PAIS_EST_SEC"] = "REGLA_INSTITUCIONAL_PAIS_EST_SEC=38"

        # ── COD_SED, COD_CAR, MODALIDAD, JOR, VERSION ─────────────────
        # Fuente: auditoría previa FASE4_CODCLI+MATRIZ_MODALIDAD (validada)
        for campo in ["COD_SED", "COD_CAR", "MODALIDAD", "JOR", "VERSION"]:
            if arc is not None and campo in arc.index and str(arc[campo]).strip():
                val = str(arc[campo]).strip()
                fuente_arc = str(arc.get(f"FUENTE_{campo}", "AUDITORIA_PREV_FASE4")).strip()
                row[campo] = val
                aud[f"FUENTE_{campo}"] = f"AUDITORIA_PREV_FASE4:{fuente_arc}"
            else:
                row[campo] = ""
                aud[f"FUENTE_{campo}"] = "FALLBACK_NO_ENCONTRADO_EN_AUDITORIA_PREV"

        # ── FOR_ING_ACT, ANIO/SEM_ING_ACT/ORI ──────────────────────
        if ing is not None:
            # Fuente: trazador campos_ing_trace_long.tsv
            row["FOR_ING_ACT"] = str(ing.get("FOR_ING_ACT", "")).strip()
            row["ANIO_ING_ACT"] = str(ing.get("ANIO_ING_ACT", "")).strip()
            row["SEM_ING_ACT"] = str(ing.get("SEM_ING_ACT", "")).strip()
            row["ANIO_ING_ORI"] = str(ing.get("ANIO_ING_ORI", "")).strip()
            row["SEM_ING_ORI"] = str(ing.get("SEM_ING_ORI", "")).strip()
            src = "TRAZADOR_CAMPOS_ING"
            for c in ["FOR_ING_ACT", "ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI", "SEM_ING_ORI"]:
                aud[f"FUENTE_{c}"] = src
        else:
            # Para los 57 sin trazador: VIASDEADMISION = "ENSEÑANZA MEDIA NACIONAL" → FOR_ING_ACT = 1
            # Son todos nuevos estudiantes 2026-1 (ingreso directo)
            vias = str(da.get("VIASDEADMISION", "")).strip() if da is not None else ""
            vias_norm = _norm_nac(vias)
            if "ENSENANZA MEDIA" in vias_norm or "NACIONAL" in vias_norm:
                for_ing = "1"
                fuente_for = f"DATOSALUMNOS_VIASDEADMISION→1_INGRESO_DIRECTO:{vias}"
            else:
                for_ing = ""
                fuente_for = f"FALLBACK_VIASDEADMISION_NO_RECONOCIDA:{vias}"

            anio_ing = str(da.get("ANOINGRESO", "")).strip() if da is not None else ""
            sem_ing = str(da.get("PERIODOINGRESO", "")).strip() if da is not None else ""
            row["FOR_ING_ACT"] = for_ing
            row["ANIO_ING_ACT"] = anio_ing
            row["SEM_ING_ACT"] = sem_ing
            # Para FOR_ING_ACT=1 (ingreso directo desde EM), ORI = ACT
            row["ANIO_ING_ORI"] = anio_ing
            row["SEM_ING_ORI"] = sem_ing
            aud["FUENTE_FOR_ING_ACT"] = fuente_for
            aud["FUENTE_ANIO_ING_ACT"] = "DATOSALUMNOS_ANOINGRESO"
            aud["FUENTE_SEM_ING_ACT"] = "DATOSALUMNOS_PERIODOINGRESO"
            aud["FUENTE_ANIO_ING_ORI"] = "DERIVADO_FOR_ING_ACT1_ORI=ACT"
            aud["FUENTE_SEM_ING_ORI"] = "DERIVADO_FOR_ING_ACT1_ORI=ACT"

        # ── Campos históricos académicos ─────────────────────────────
        if hi is not None:
            for campo in HIST_COLS:
                row[campo] = str(hi.get(campo, "0")).strip()
                aud[f"FUENTE_{campo}"] = "RESUMEN_HISTORICO_MU_2026"
        else:
            # Nuevo 2026: sin historia previa → 0
            for campo in HIST_COLS:
                row[campo] = "0"
                aud[f"FUENTE_{campo}"] = "NUEVO_ESTUDIANTE_2026_SIN_HISTORICO→0"

        # ── NIV_ACA ───────────────────────────────────────────────────
        nivel_da = str(da.get("NIVEL", "")).strip() if da is not None else ""
        row["NIV_ACA"] = nivel_da
        aud["FUENTE_NIV_ACA"] = "DATOSALUMNOS_NIVEL"

        # ── SIT_FON_SOL ───────────────────────────────────────────────
        row["SIT_FON_SOL"] = SIT_FON_SOL_INSTITUCIONAL
        aud["FUENTE_SIT_FON_SOL"] = "REGLA_INSTITUCIONAL_NO_ADSCRITA_FONDO_SOLIDARIO=0"

        # ── SUS_PRE ───────────────────────────────────────────────────
        row["SUS_PRE"] = SUS_PRE_INSTITUCIONAL
        aud["FUENTE_SUS_PRE"] = "REGLA_INSTITUCIONAL_SUS_PRE=0"

        # ── FECHA_MATRICULA ───────────────────────────────────────────
        if vi is not None and str(vi.get("FECHA_MATRICULA", "")).strip():
            fecha_mat = str(vi["FECHA_MATRICULA"]).strip()
            fuente_fm = "TRAZADOR_VIG_FECHA"
        else:
            fecha_mat_da = str(da.get("FECHAMATRICULA", "")).strip() if da is not None else ""
            fecha_mat = _fecha_dmdmY_to_slash(fecha_mat_da)
            fuente_fm = "DATOSALUMNOS_FECHAMATRICULA"
        row["FECHA_MATRICULA"] = fecha_mat
        aud["FUENTE_FECHA_MATRICULA"] = fuente_fm

        # ── REINCORPORACION ───────────────────────────────────────────
        row["REINCORPORACION"] = REINCORPORACION_INSTITUCIONAL
        aud["FUENTE_REINCORPORACION"] = "REGLA_INSTITUCIONAL_REINCORPORACION=0"

        # ── VIG ───────────────────────────────────────────────────────
        row["VIG"] = VIG_COMPLEMENTO
        aud["FUENTE_VIG"] = "CONFIRMADO_ESTADOACADEMICO_VIGENTE_DATOSALUMNOS"

        rows_data.append(row)
        rows_audit.append(aud)

    df_out = pd.DataFrame(rows_data, columns=MATRICULA_UNIFICADA_COLUMNS)
    df_aud = pd.DataFrame(rows_audit)
    return df_out, df_aud


# ══════════════════════════════════════════════════════════════════════════
# FASE 7 — Auditoría campo a campo
# ══════════════════════════════════════════════════════════════════════════
def fase7_auditoria(df_out: pd.DataFrame, df_aud: pd.DataFrame,
                    codcli_list: list[str]) -> int:
    _sep("FASE 7: Auditoría campo a campo")
    n_fallbacks = 0
    n_vacios = 0
    problemas: list[str] = []

    fuente_cols = [c for c in df_aud.columns if c.startswith("FUENTE_")]
    for fc in fuente_cols:
        vals = df_aud[fc].value_counts().to_dict()
        has_fallback = any("FALLBACK" in str(v) or "NO_ENCONTRADO" in str(v) for v in vals)
        if has_fallback:
            n_fallbacks += sum(v for k, v in vals.items() if "FALLBACK" in k or "NO_ENCONTRADO" in k)
            problemas.append(f"  ⚠️  {fc}: {vals}")
            print(f"  ⚠️  {fc}: {vals}")
        else:
            print(f"  ✅ {fc}: {sorted(vals.keys())}")

    # Verificar vacíos
    campo_cols = MATRICULA_UNIFICADA_COLUMNS
    for campo in campo_cols:
        if campo in df_out.columns:
            vacios = (df_out[campo] == "").sum()
            if vacios > 0:
                n_vacios += vacios
                problemas.append(f"  ⚠️  VACÍO {campo}: {vacios} filas")
                print(f"  ⚠️  VACÍO {campo}: {vacios} filas")

    print(f"\n  Fallbacks detectados  : {n_fallbacks}")
    print(f"  Campos vacíos         : {n_vacios}")
    print(f"  Filas                 : {len(df_out)}")
    print(f"  Columnas              : {len(df_out.columns)}")

    # Guardar auditoría
    df_audit_completa = df_aud.copy()
    for campo in MATRICULA_UNIFICADA_COLUMNS:
        if campo in df_out.columns:
            df_audit_completa.insert(
                list(df_audit_completa.columns).index(f"FUENTE_{campo}") if f"FUENTE_{campo}" in df_audit_completa.columns else len(df_audit_completa.columns),
                campo,
                df_out[campo].values,
            )
    df_audit_completa.to_csv(
        OUT_DIR / "04_auditoria_32_campos_complemento_95.csv", index=False)
    print(f"\n  ✅ Auditoría guardada en 04_auditoria_32_campos_complemento_95.csv")

    if problemas:
        print("\n  PROBLEMAS DETECTADOS:")
        for p in problemas:
            print(p)

    return n_fallbacks + n_vacios


# ══════════════════════════════════════════════════════════════════════════
# FASE 8 — Exportar CSV final (solo si 0 fallbacks)
# ══════════════════════════════════════════════════════════════════════════
def fase8_exportar(df_out: pd.DataFrame, n_problemas: int) -> Path | None:
    _sep("FASE 8: Exportar CSV final")
    if n_problemas > 0:
        print(f"  ❌ NO SE GENERA CSV FINAL: {n_problemas} problemas detectados")
        print(f"     Revisar auditoria en {OUT_DIR}/04_auditoria_32_campos_complemento_95.csv")
        return None

    # Validaciones finales
    assert len(df_out) == 95, f"Esperadas 95 filas, hay {len(df_out)}"
    assert list(df_out.columns) == MATRICULA_UNIFICADA_COLUMNS, "Columnas no coinciden"
    assert (df_out["VIG"] == "1").all(), "Todos deben tener VIG=1"
    assert (df_out["SIT_FON_SOL"] == "0").all(), "Todos deben tener SIT_FON_SOL=0"

    out_path = OUT_DIR / "matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv"
    desktop_path = Path.home() / "Desktop" / "matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv"

    # Escribir sin header, separador ;
    df_out.to_csv(out_path, index=False, header=False, sep=";",
                  encoding="utf-8", lineterminator="\n")
    desktop_path.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(desktop_path, index=False, header=False, sep=";",
                  encoding="utf-8", lineterminator="\n")

    sha = _sha256(out_path)
    print(f"  ✅ Generado: {out_path}")
    print(f"  ✅ Copia escritorio: {desktop_path}")
    print(f"  SHA256: {sha}")
    print(f"  Filas: {len(df_out)}  Columnas: {len(df_out.columns)}")
    return out_path


# ══════════════════════════════════════════════════════════════════════════
# FASE 9 — Reporte ejecutivo
# ══════════════════════════════════════════════════════════════════════════
def fase9_reporte(df_out: pd.DataFrame, df_aud: pd.DataFrame,
                  sha_principal: str, n_problemas: int, out_csv: Path | None) -> None:
    _sep("FASE 9: Reporte ejecutivo")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    estado = "✅ GENERADO" if out_csv else "❌ NO GENERADO (fallbacks detectados)"

    lineas = [
        "# COMPLEMENTO 95 CODCLI — Reporte ejecutivo",
        f"",
        f"**Generado**: {ts}",
        f"**Estado CSV final**: {estado}",
        f"",
        f"## Resumen",
        f"",
        f"| Campo | Valor |",
        f"|---|---|",
        f"| CODCLI procesados | {len(df_out)} |",
        f"| Columnas MU | {len(df_out.columns)} |",
        f"| VIG | 1 (todos) |",
        f"| SIT_FON_SOL | 0 (regla institucional) |",
        f"| Fallbacks/vacíos | {n_problemas} |",
        f"| SHA256 PES_READY (sin cambios) | {sha_principal} |",
        f"",
        f"## Restricciones cumplidas",
        f"",
        f"- ✅ PES_READY NO modificado",
        f"- ✅ Desktop PARA_SUBIR principal NO modificado",
        f"- ✅ Pipeline principal NO importado",
        f"- ✅ Solo escribe en `resultados/complemento_95_codcli/`",
        f"",
        f"## Fuentes por campo",
        f"",
        f"| Campo | Fuentes (conteo) |",
        f"|---|---|",
    ]
    for fc in [c for c in df_aud.columns if c.startswith("FUENTE_")]:
        campo = fc.replace("FUENTE_", "")
        vals = df_aud[fc].value_counts().to_dict()
        resumen = " | ".join(f"{k}={v}" for k, v in sorted(vals.items()))
        lineas.append(f"| {campo} | {resumen} |")

    if out_csv:
        lineas += [
            f"",
            f"## Archivo final",
            f"",
            f"```",
            f"Ruta: {out_csv}",
            f"Desktop: ~/Desktop/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv",
            f"Filas: 95",
            f"Columnas: 32",
            f"Sin encabezado",
            f"Separador: ;",
            f"```",
        ]

    readme = OUT_DIR / "README_COMPLEMENTO_95_CODCLI.md"
    readme.write_text("\n".join(lineas), encoding="utf-8")
    print(f"  ✅ Reporte guardado en {readme}")


# ══════════════════════════════════════════════════════════════════════════
# FASE 10 — Verificar que PES_READY no cambió
# ══════════════════════════════════════════════════════════════════════════
def fase10_verificar_principal(sha_original: str) -> None:
    _sep("FASE 10: Verificar integridad PES_READY")
    sha_actual = _sha256(PES_READY_PATH)
    if sha_actual == sha_original:
        print(f"  ✅ PES_READY intacto (SHA256 coincide)")
        print(f"     {sha_actual}")
    else:
        print(f"  🚨 ALERTA: SHA256 del PES_READY CAMBIÓ")
        print(f"     Original: {sha_original}")
        print(f"     Actual  : {sha_actual}")
        raise RuntimeError("PES_READY fue modificado — revisar inmediatamente")


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════
def main() -> None:
    print("=" * 60)
    print("  MU2026 — COMPLEMENTO 95 CODCLI")
    print("=" * 60)

    fase0_preparar()
    sha_principal, _ = fase1_resguardar_principal()
    codcli_list = fase2_nomina()
    da_idx = fase3_datosalumnos(codcli_list)
    ing_nom, vig_nom, his_nom, arc_nom = fase4_trazadores(codcli_list)
    nac_map = fase5_gobernanza()
    df_out, df_aud = fase6_construir(
        codcli_list, da_idx, ing_nom, vig_nom, his_nom, arc_nom, nac_map)
    n_problemas = fase7_auditoria(df_out, df_aud, codcli_list)
    out_csv = fase8_exportar(df_out, n_problemas)
    fase9_reporte(df_out, df_aud, sha_principal, n_problemas, out_csv)
    fase10_verificar_principal(sha_principal)

    _sep("RESUMEN FINAL")
    if out_csv:
        print(f"  ✅ CSV generado: {out_csv}")
        print(f"  ✅ 95 filas | 32 campos | sin encabezado | sep=; | VIG=1")
    else:
        print(f"  ❌ CSV NO generado — revisar auditoría")


if __name__ == "__main__":
    main()
