"""
fixture_validacion_cruzada_mu2026.py
Fixture paralelo de validacion cruzada end to end · Matricula Unificada 2026
Operacion completamente aislada. No modifica archivos productivos.
Toda salida queda en: control/fixtures/mu2026_validacion_cruzada/resultados/
"""

from pathlib import Path
import pandas as pd
import json
import re
from datetime import datetime

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = ROOT / "control" / "fixtures" / "mu2026_validacion_cruzada"
RESULTADOS_DIR = FIXTURE_DIR / "resultados"

# Archivo productivo protegido
ARCHIVO_PRODUCTIVO = ROOT / "resultados" / "matricula_unificada_2026_pregrado.csv"

# Archivos del fixture
ENTRADA = FIXTURE_DIR / "entrada_correcta_20.tsv"
SALIDA_ESPERADA = FIXTURE_DIR / "salida_esperada_mu32.tsv"
REGLAS = FIXTURE_DIR / "reglas_manual.tsv"
CASOS_ERROR = FIXTURE_DIR / "casos_error_controlados.tsv"

# Columnas oficiales MU32 (en orden)
COLUMNAS_MU32 = [
    "TIPO_DOC", "N_DOC", "DV", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO",
    "NOMBRE", "SEXO", "FECH_NAC", "NAC", "PAIS_EST_SEC", "COD_SED",
    "COD_CAR", "MODALIDAD", "JOR", "VERSION", "FOR_ING_ACT",
    "ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI", "SEM_ING_ORI",
    "ASI_INS_ANT", "ASI_APR_ANT", "PROM_PRI_SEM", "PROM_SEG_SEM",
    "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL",
    "SUS_PRE", "FECHA_MATRICULA", "REINCORPORACION", "VIG",
]

# Campos auxiliares que NO deben aparecer en MU32
CAMPOS_AUXILIARES_EXCLUIDOS = {"COD_NIV_GLO", "COD_IES", "FECH_CAR"}

# Columnas de control permitidas en salida_esperada_mu32.tsv
COLUMNAS_CONTROL = {"TEST_ID", "PERFIL_VALIDACION", "FILA_ORIGEN_XLSX"}

# FOR_ING_ACT que exigen ANIO_ING_ORI == ANIO_ING_ACT (R09)
FOR_IGUAL_ANIO = {"1", "6", "7", "8", "9", "10"}


# ---------------------------------------------------------------------------
# Guardia: verificar que no se escribira en el archivo productivo
# ---------------------------------------------------------------------------
def _verificar_no_toca_productivo():
    salidas_a_escribir = [
        RESULTADOS_DIR / "resultado_fixture_validos.tsv",
        RESULTADOS_DIR / "resultado_fixture_errores.tsv",
        RESULTADOS_DIR / "comparacion_esperado_vs_obtenido.tsv",
        RESULTADOS_DIR / "reporte_fixture_mu2026.md",
        RESULTADOS_DIR / "resumen_fixture_mu2026.json",
    ]
    for p in salidas_a_escribir:
        if p.resolve() == ARCHIVO_PRODUCTIVO.resolve():
            raise RuntimeError(
                f"SEGURIDAD: Se intentaria escribir en el archivo productivo: {ARCHIVO_PRODUCTIVO}"
            )


# ---------------------------------------------------------------------------
# Leer TSV como texto
# ---------------------------------------------------------------------------
def _leer_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        sep="\t",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Normalizar valor textual para comparacion
# ---------------------------------------------------------------------------
def _norm(v: str) -> str:
    return str(v).strip()


# ---------------------------------------------------------------------------
# Reglas de validacion
# ---------------------------------------------------------------------------
def _es_entero(v: str) -> bool:
    return bool(re.fullmatch(r"\d+", v.strip()))


def validar_reglas(df: pd.DataFrame, origen: str) -> list[dict]:
    """Ejecuta R01-R13 sobre el dataframe. Retorna lista de errores."""
    errores = []

    def add(idx, test_id, regla, campo, valor, mensaje):
        errores.append({
            "TEST_ID": test_id,
            "FILA": idx + 1,
            "REGLA": regla,
            "CAMPO": campo,
            "VALOR": valor,
            "MENSAJE": mensaje,
            "ORIGEN": origen,
        })

    def col(row, name):
        return _norm(row.get(name, ""))

    for idx, row in df.iterrows():
        tid = col(row, "TEST_ID") or str(idx + 1)

        tipo_doc = col(row, "TIPO_DOC")
        dv = col(row, "DV")
        n_doc = col(row, "N_DOC")
        anio_ori = col(row, "ANIO_ING_ORI")
        sem_ori = col(row, "SEM_ING_ORI")
        asi_ins_his = col(row, "ASI_INS_HIS")
        asi_apr_his = col(row, "ASI_APR_HIS")
        niv_aca = col(row, "NIV_ACA")
        for_ing = col(row, "FOR_ING_ACT")
        anio_act = col(row, "ANIO_ING_ACT")
        vig = col(row, "VIG")
        fech_nac = col(row, "FECH_NAC")
        asi_ins_ant = col(row, "ASI_INS_ANT")
        asi_apr_ant = col(row, "ASI_APR_ANT")

        # R01 TIPO_DOC
        if tipo_doc == "":
            add(idx, tid, "R01", "TIPO_DOC", tipo_doc,
                "Los valores permitidos para TIPO DOCUMENTO son R: RUT o P: Pasaporte.")
        elif tipo_doc not in {"R", "P"}:
            add(idx, tid, "R01", "TIPO_DOC", tipo_doc,
                "Los valores permitidos para TIPO DOCUMENTO son R: RUT o P: Pasaporte.")

        # R02 DV
        if tipo_doc == "R" and dv == "":
            add(idx, tid, "R02", "DV", dv,
                "Cuando el TIPO DOCUMENTO es 'R' se debe completar DV.")
        elif tipo_doc == "P" and dv != "":
            add(idx, tid, "R02", "DV", dv,
                "Cuando el TIPO DOCUMENTO es 'P' no se debe completar DV.")

        # R03 N_DOC
        if tipo_doc == "R" and n_doc != "" and not _es_entero(n_doc):
            add(idx, tid, "R03", "N_DOC", n_doc,
                "Cuando el TIPO DOCUMENTO es 'R' el NÚMERO DOCUMENTO no puede contener letras.")

        # R04 ANIO_ING_ORI / SEM_ING_ORI
        if anio_ori == "1900" and sem_ori != "0":
            add(idx, tid, "R04", "SEM_ING_ORI", sem_ori,
                "Cuando el AÑO INGRESO CARRERA ORIGEN es 1900, el SEMESTRE INGRESO CARRERA ORIGEN no puede ser distinto a 0.")

        # R05 ASI_INS_HIS
        if asi_ins_his == "":
            add(idx, tid, "R05", "ASI_INS_HIS", asi_ins_his,
                "ASIGNATURAS INSCRITAS HISTÓRICAS se encuentra fuera del rango permitido para programas de Pregrado.")
        elif not _es_entero(asi_ins_his):
            add(idx, tid, "R05", "ASI_INS_HIS", asi_ins_his,
                "ASIGNATURAS INSCRITAS HISTÓRICAS se encuentra fuera del rango permitido para programas de Pregrado.")
        elif not (0 <= int(asi_ins_his) <= 200):
            add(idx, tid, "R05", "ASI_INS_HIS", asi_ins_his,
                "ASIGNATURAS INSCRITAS HISTÓRICAS se encuentra fuera del rango permitido para programas de Pregrado.")

        # R06 ASI_APR_HIS
        if asi_apr_his == "":
            add(idx, tid, "R06", "ASI_APR_HIS", asi_apr_his,
                "Las ASIGNATURAS APROBADAS HISTÓRICAS se encuentra fuera del rango permitido.")
        elif not _es_entero(asi_apr_his):
            add(idx, tid, "R06", "ASI_APR_HIS", asi_apr_his,
                "Las ASIGNATURAS APROBADAS HISTÓRICAS se encuentra fuera del rango permitido.")
        elif not (0 <= int(asi_apr_his) <= 200):
            add(idx, tid, "R06", "ASI_APR_HIS", asi_apr_his,
                "Las ASIGNATURAS APROBADAS HISTÓRICAS se encuentra fuera del rango permitido.")

        # R07 cruce ASI
        if (_es_entero(asi_ins_his) and _es_entero(asi_apr_his)
                and int(asi_apr_his) > int(asi_ins_his)):
            add(idx, tid, "R07", "ASI_APR_HIS/ASI_INS_HIS",
                f"APR={asi_apr_his} INS={asi_ins_his}",
                "Las ASIGNATURAS APROBADAS HISTORICAS no pueden ser mayor a las ASIGNATURAS INCRITAS HISTÓRICAS.")

        # R08 NIV_ACA
        if (anio_ori == "2026" and _es_entero(niv_aca)
                and int(niv_aca) > 2):
            add(idx, tid, "R08", "NIV_ACA", niv_aca,
                "Cuando el AÑO INGRESO CARRERA ORIGEN es 2026, el NIVEL ACADÉMICO no puede ser mayor a 2.")

        # R09 FOR_ING_ACT / ANIO
        if for_ing in FOR_IGUAL_ANIO and anio_ori != anio_act:
            add(idx, tid, "R09", "ANIO_ING_ORI",
                f"ORI={anio_ori} ACT={anio_act}",
                "Cuando la FORMA INGRESO CARRERA ACTUAL es 1, 6, 7, 8, 9 o 10, el AÑO INGRESO CARRERA ORIGEN y AÑO INGRESO CARRERA ACTUAL deben ser iguales.")

        # R10 VIG
        if vig not in {"0", "1", "2"}:
            add(idx, tid, "R10", "VIG", vig,
                "La VIGENCIA considera valores 0, 1 o 2.")

        # R11 FECH_NAC
        if fech_nac == "":
            add(idx, tid, "R11", "FECH_NAC", fech_nac,
                "La FECHA DE NACIMIENTO no puede estar vacía.")

        # R12 cruce ANT
        if (_es_entero(asi_ins_ant) and _es_entero(asi_apr_ant)
                and int(asi_apr_ant) > int(asi_ins_ant)):
            add(idx, tid, "R12", "ASI_APR_ANT/ASI_INS_ANT",
                f"APR={asi_apr_ant} INS={asi_ins_ant}",
                "Las ASIGNATURAS INSCRITAS AÑO ANTERIOR no pueden ser menor a las ASIGNATURAS APROBADAS AÑO ANTERIOR.")

        # R12b ASI_INS_ANT debe ser 0 si FOR_ING_ACT en FOR_IGUAL_ANIO y ANIO_ING_ACT == ANIO_ING_ORI
        # (primer ingreso en año actual → no puede tener asignaturas del año anterior)
        if (for_ing in FOR_IGUAL_ANIO and anio_act == anio_ori
                and _es_entero(asi_ins_ant) and int(asi_ins_ant) > 0):
            add(idx, tid, "R12b", "ASI_INS_ANT",
                asi_ins_ant,
                "Según FORMA INGRESO CARRERA ACTUAL y AÑO INGRESO CARRERA ACTUAL informados, las ASIGNATURAS INSCRITAS AÑO ANTERIOR no puede ser mayor a 0.")

    return errores


# ---------------------------------------------------------------------------
# R13 estructura MU32
# ---------------------------------------------------------------------------
def validar_r13_estructura(df_salida: pd.DataFrame) -> list[dict]:
    errores = []
    cols_salida = set(df_salida.columns) - COLUMNAS_CONTROL
    # Verificar que no haya campos auxiliares excluidos
    indebidos = cols_salida & CAMPOS_AUXILIARES_EXCLUIDOS
    if indebidos:
        errores.append({
            "TEST_ID": "R13",
            "FILA": 0,
            "REGLA": "R13",
            "CAMPO": str(sorted(indebidos)),
            "VALOR": "",
            "MENSAJE": f"Campos auxiliares indebidos detectados en salida MU32: {sorted(indebidos)}",
            "ORIGEN": "salida_esperada_mu32",
        })
    # Verificar cantidad y orden de columnas MU32
    cols_mu32_en_salida = [c for c in df_salida.columns if c not in COLUMNAS_CONTROL]
    if cols_mu32_en_salida != COLUMNAS_MU32:
        errores.append({
            "TEST_ID": "R13",
            "FILA": 0,
            "REGLA": "R13",
            "CAMPO": "COLUMNAS_MU32",
            "VALOR": str(cols_mu32_en_salida),
            "MENSAJE": "La salida MU32 no tiene exactamente las 32 columnas oficiales en el orden esperado.",
            "ORIGEN": "salida_esperada_mu32",
        })
    return errores


# ---------------------------------------------------------------------------
# Comparacion entrada → proyeccion → salida_esperada
# ---------------------------------------------------------------------------
def comparar_proyeccion(df_entrada: pd.DataFrame, df_esperada: pd.DataFrame) -> list[dict]:
    """Proyecta entrada sobre MU32 y compara fila a fila con df_esperada."""
    diferencias = []

    # Proyectar: quitar campos auxiliares excluidos, mantener columnas de control + MU32
    cols_proyeccion = ["TEST_ID", "PERFIL_VALIDACION", "FILA_ORIGEN_XLSX"] + COLUMNAS_MU32
    # Verificar que todas existen en entrada
    faltantes = [c for c in cols_proyeccion if c not in df_entrada.columns]
    if faltantes:
        diferencias.append({
            "TEST_ID": "ESTRUCTURA",
            "COLUMNA": str(faltantes),
            "FILA": 0,
            "VALOR_ESPERADO": "columna presente",
            "VALOR_OBTENIDO": "columna ausente",
            "TIPO": "COLUMNA_FALTANTE",
        })
        return diferencias

    df_proyectada = df_entrada[cols_proyeccion].copy().reset_index(drop=True)
    df_esp = df_esperada[cols_proyeccion].copy().reset_index(drop=True)

    n_filas = min(len(df_proyectada), len(df_esp))
    if len(df_proyectada) != len(df_esp):
        diferencias.append({
            "TEST_ID": "ESTRUCTURA",
            "COLUMNA": "FILAS",
            "FILA": 0,
            "VALOR_ESPERADO": str(len(df_esp)),
            "VALOR_OBTENIDO": str(len(df_proyectada)),
            "TIPO": "CANTIDAD_FILAS",
        })

    for i in range(n_filas):
        tid = _norm(df_esp.iloc[i].get("TEST_ID", str(i + 1)))
        for col in cols_proyeccion:
            v_esp = _norm(df_esp.iloc[i][col])
            v_obt = _norm(df_proyectada.iloc[i][col])
            if v_esp != v_obt:
                diferencias.append({
                    "TEST_ID": tid,
                    "COLUMNA": col,
                    "FILA": i + 1,
                    "VALOR_ESPERADO": v_esp,
                    "VALOR_OBTENIDO": v_obt,
                    "TIPO": "DIFERENCIA_VALOR",
                })

    return diferencias


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("=" * 72)
    print("FIXTURE PARALELO · VALIDACION CRUZADA MU2026 · END TO END")
    print(f"Timestamp: {timestamp}")
    print("=" * 72)

    # Guardia de seguridad
    _verificar_no_toca_productivo()
    print("[OK] Guardia: no se escribira en el archivo productivo.")

    # Crear directorio de resultados
    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # Leer archivos del fixture
    # -----------------------------------------------------------------------
    df_entrada = _leer_tsv(ENTRADA)
    df_esperada = _leer_tsv(SALIDA_ESPERADA)
    df_casos_error = _leer_tsv(CASOS_ERROR)

    print(f"[OK] entrada_correcta_20.tsv leido: {len(df_entrada)} filas")
    print(f"[OK] salida_esperada_mu32.tsv leido: {len(df_esperada)} filas")
    print(f"[OK] casos_error_controlados.tsv leido: {len(df_casos_error)} filas")

    # -----------------------------------------------------------------------
    # Paso 1: Validar conteos
    # -----------------------------------------------------------------------
    errores_conteo = []
    if len(df_entrada) != 20:
        errores_conteo.append(f"entrada_correcta_20.tsv tiene {len(df_entrada)} filas, esperado 20.")
    if len(df_esperada) != 20:
        errores_conteo.append(f"salida_esperada_mu32.tsv tiene {len(df_esperada)} filas, esperado 20.")

    # -----------------------------------------------------------------------
    # Paso 2: Validar estructura R13 en salida esperada
    # -----------------------------------------------------------------------
    errores_r13 = validar_r13_estructura(df_esperada)

    # -----------------------------------------------------------------------
    # Paso 3: Verificar que campos auxiliares no esten en salida MU32
    # -----------------------------------------------------------------------
    campos_indebidos = [c for c in CAMPOS_AUXILIARES_EXCLUIDOS if c in df_esperada.columns]

    # -----------------------------------------------------------------------
    # Paso 4: Comparar proyeccion entrada → salida esperada
    # -----------------------------------------------------------------------
    diferencias = comparar_proyeccion(df_entrada, df_esperada)

    # -----------------------------------------------------------------------
    # Paso 5: Validar reglas sobre registros validos (salida_esperada)
    # -----------------------------------------------------------------------
    errores_validos = validar_reglas(df_esperada, "salida_esperada_mu32")

    # -----------------------------------------------------------------------
    # Paso 6: Validar reglas sobre casos de error
    # -----------------------------------------------------------------------
    errores_casos = validar_reglas(df_casos_error, "casos_error_controlados")

    # Determinar cuales ERR se detectaron
    ids_err_esperados = set(df_casos_error["TEST_ID"].str.strip().tolist())
    ids_err_detectados = {e["TEST_ID"] for e in errores_casos}
    err_detectados = ids_err_detectados & ids_err_esperados
    err_no_detectados = ids_err_esperados - ids_err_detectados

    # -----------------------------------------------------------------------
    # Dictamen
    # -----------------------------------------------------------------------
    dictamen = "OK"
    razones = []

    if errores_conteo:
        dictamen = "NO_LISTO"
        razones += errores_conteo

    if errores_r13:
        dictamen = "NO_LISTO"
        razones.append(f"R13 estructura fallida: {len(errores_r13)} errores")

    if campos_indebidos:
        dictamen = "NO_LISTO"
        razones.append(f"Campos auxiliares indebidos en MU32: {campos_indebidos}")

    if diferencias:
        dictamen = "NO_LISTO"
        razones.append(f"Diferencias en proyeccion entrada→salida: {len(diferencias)}")

    if errores_validos:
        dictamen = "NO_LISTO"
        razones.append(f"Errores en registros validos: {len(errores_validos)}")

    if err_no_detectados:
        dictamen = "NO_LISTO"
        razones.append(f"Errores controlados no detectados: {sorted(err_no_detectados)}")

    # -----------------------------------------------------------------------
    # Escribir salidas
    # -----------------------------------------------------------------------

    # resultado_fixture_validos.tsv
    cols_resultado = ["TEST_ID", "FILA", "REGLA", "CAMPO", "VALOR", "MENSAJE", "ORIGEN"]
    df_validos_ok = df_esperada[["TEST_ID", "PERFIL_VALIDACION"]].copy()
    df_validos_ok["ERRORES_DETECTADOS"] = df_validos_ok["TEST_ID"].apply(
        lambda tid: sum(1 for e in errores_validos if e["TEST_ID"] == tid.strip())
    )
    df_validos_ok["RESULTADO"] = df_validos_ok["ERRORES_DETECTADOS"].apply(
        lambda n: "OK" if n == 0 else "FALLO"
    )
    df_validos_ok.to_csv(
        RESULTADOS_DIR / "resultado_fixture_validos.tsv",
        sep="\t", index=False, encoding="utf-8"
    )

    # resultado_fixture_errores.tsv
    df_casos_result = df_casos_error[["TEST_ID", "CAMPO_MUTADO", "ERROR_ESPERADO_MANUAL"]].copy()
    df_casos_result["DETECTADO"] = df_casos_result["TEST_ID"].apply(
        lambda tid: "SI" if tid.strip() in ids_err_detectados else "NO"
    )
    df_casos_result.to_csv(
        RESULTADOS_DIR / "resultado_fixture_errores.tsv",
        sep="\t", index=False, encoding="utf-8"
    )

    # comparacion_esperado_vs_obtenido.tsv
    if diferencias:
        pd.DataFrame(diferencias).to_csv(
            RESULTADOS_DIR / "comparacion_esperado_vs_obtenido.tsv",
            sep="\t", index=False, encoding="utf-8"
        )
    else:
        pd.DataFrame(columns=["TEST_ID", "COLUMNA", "FILA", "VALOR_ESPERADO", "VALOR_OBTENIDO", "TIPO"]).to_csv(
            RESULTADOS_DIR / "comparacion_esperado_vs_obtenido.tsv",
            sep="\t", index=False, encoding="utf-8"
        )

    # resumen_fixture_mu2026.json
    resumen = {
        "timestamp": timestamp,
        "dictamen_fixture": dictamen,
        "registros_validos_evaluados": len(df_entrada),
        "registros_validos_sin_errores": len(df_esperada) - len({e["TEST_ID"] for e in errores_validos}),
        "errores_en_validos": len(errores_validos),
        "casos_error_controlados_evaluados": len(df_casos_error),
        "errores_controlados_detectados": len(err_detectados),
        "errores_controlados_no_detectados": len(err_no_detectados),
        "ids_no_detectados": sorted(err_no_detectados),
        "diferencias_proyeccion": len(diferencias),
        "campos_auxiliares_indebidos": campos_indebidos,
        "errores_r13": len(errores_r13),
        "razones": razones,
    }
    (RESULTADOS_DIR / "resumen_fixture_mu2026.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # reporte_fixture_mu2026.md
    md = []
    md.append("# Reporte fixture validacion cruzada MU2026")
    md.append("")
    md.append(f"Fecha: {timestamp}")
    md.append("")
    md.append(f"## Dictamen: **{dictamen}**")
    md.append("")
    md.append("## Resumen")
    md.append("")
    md.append(f"| Indicador | Valor |")
    md.append(f"|---|---:|")
    md.append(f"| Registros validos evaluados | {resumen['registros_validos_evaluados']} |")
    md.append(f"| Registros validos sin errores | {resumen['registros_validos_sin_errores']} |")
    md.append(f"| Errores en validos | {resumen['errores_en_validos']} |")
    md.append(f"| Casos error evaluados | {resumen['casos_error_controlados_evaluados']} |")
    md.append(f"| Errores controlados detectados | {resumen['errores_controlados_detectados']} |")
    md.append(f"| Errores controlados no detectados | {resumen['errores_controlados_no_detectados']} |")
    md.append(f"| Diferencias de proyeccion | {resumen['diferencias_proyeccion']} |")
    md.append(f"| Campos auxiliares indebidos | {len(campos_indebidos)} |")
    md.append(f"| Errores R13 estructura | {resumen['errores_r13']} |")
    md.append("")
    if razones:
        md.append("## Razones del dictamen")
        md.append("")
        for r in razones:
            md.append(f"- {r}")
        md.append("")
    if errores_validos:
        md.append("## Errores en registros validos (NO esperados)")
        md.append("")
        for e in errores_validos:
            md.append(f"- {e['TEST_ID']} | {e['REGLA']} | {e['CAMPO']} | {e['VALOR']} | {e['MENSAJE']}")
        md.append("")
    if err_no_detectados:
        md.append("## Errores controlados NO detectados")
        md.append("")
        for tid in sorted(err_no_detectados):
            md.append(f"- {tid}")
        md.append("")
    md.append("## Archivos generados")
    md.append("")
    for f in [
        "resultado_fixture_validos.tsv",
        "resultado_fixture_errores.tsv",
        "comparacion_esperado_vs_obtenido.tsv",
        "resumen_fixture_mu2026.json",
        "reporte_fixture_mu2026.md",
    ]:
        md.append(f"- `{RESULTADOS_DIR / f}`")
    md.append("")
    (RESULTADOS_DIR / "reporte_fixture_mu2026.md").write_text(
        "\n".join(md), encoding="utf-8"
    )

    # -----------------------------------------------------------------------
    # Imprimir resumen
    # -----------------------------------------------------------------------
    print("")
    print(f"  Registros validos evaluados      : {resumen['registros_validos_evaluados']}")
    print(f"  Registros validos sin errores    : {resumen['registros_validos_sin_errores']}")
    print(f"  Errores en validos               : {resumen['errores_en_validos']}")
    print(f"  Casos error evaluados            : {resumen['casos_error_controlados_evaluados']}")
    print(f"  Errores controlados detectados   : {resumen['errores_controlados_detectados']}")
    print(f"  Errores controlados no detectados: {resumen['errores_controlados_no_detectados']}")
    print(f"  Diferencias de proyeccion        : {resumen['diferencias_proyeccion']}")
    print(f"  Campos auxiliares indebidos      : {len(campos_indebidos)}")
    print(f"  Errores R13                      : {resumen['errores_r13']}")
    print("")
    print(f"  DICTAMEN FIXTURE: {dictamen}")
    if razones:
        print("")
        print("  Razones:")
        for r in razones:
            print(f"    - {r}")
    print("")
    print(f"  Resultados en: {RESULTADOS_DIR}")
    print("=" * 72)

    return 0 if dictamen == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
