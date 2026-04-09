from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/corregir_fase06_vigencia_extranjeros_2025.py"

spec = importlib.util.spec_from_file_location("corregir_fase06", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def _sample_row() -> dict[str, str]:
    return {
        "TIPO_DOCUMENTO": "P",
        "NUM_DOCUMENTO": "100000001",
        "DV": "",
        "PRIMER_APELLIDO": "APELLIDO",
        "SEGUNDO_APELLIDO": "",
        "NOMBRES": "NOMBRE",
        "SEXO": "H",
        "FECHA_NACIMIENTO": "12-06-2006",
        "NACIONALIDAD": "1",
        "TIPO_RESIDENCIA_ESTUDIANTE": "0",
        "PAIS_DE_ORIGEN": "",
        "PAIS_ESTUDIOS_SECUNDARIOS": "1",
        "CODIGO_UNICO": "I162S2C91J1V1",
        "ANIO_INGRESO_CARRERA_ACTUAL": "2025",
        "SEM_INGRESO_CARRERA_ACTUAL": "1",
        "ANIO_INGRESO_CARRERA_ORIGEN": "2025",
        "SEM_INGRESO_CARRERA_ORIGEN": "1",
        "NOMBRE_UNIVERSIDAD_ORIGEN": "",
        "PAIS_UNIVERSIDAD_ORIGEN": "",
        "VIGENCIA": "1",
    }


def test_delimitador_sies_simulado(tmp_path: Path) -> None:
    df = pd.DataFrame([_sample_row()], columns=mod.COLUMNAS_SIES_REGULARES)
    path = tmp_path / "sies.csv"
    mod.write_sies_csv_cp1252_no_final_newline(df, path)
    comma = pd.read_csv(path, sep=",", header=None, encoding="cp1252", dtype=str, keep_default_na=False)
    semicolon = pd.read_csv(path, sep=";", header=None, encoding="cp1252", dtype=str, keep_default_na=False)
    assert comma.shape[1] == 1
    assert semicolon.shape == (1, 20)


def test_fecha_normalizada_dd_mm_aaaa() -> None:
    assert mod.normalize_date("2006-06-12 00:00:00") == "12-06-2006"


def test_residencia_sin_informacion_codigo_0() -> None:
    row = pd.Series({"TIPO_RESIDENCIA_ESTUDIANTE": "", "PAIS_DE_ORIGEN": ""})
    out = mod.apply_residencia_sin_informacion(row)
    assert out["TIPO_RESIDENCIA_ESTUDIANTE"] == "0"
    assert out["PAIS_DE_ORIGEN"] == ""


def test_nacionalidad_chilena_y_no_demostrada_excluidas() -> None:
    base = pd.DataFrame([
        {"ID_REGISTRO": "PRECARGA_0001", **_sample_row()},
        {"ID_REGISTRO": "PRECARGA_0002", **_sample_row()},
    ])
    decision = pd.DataFrame([
        {
            "ID_REGISTRO": "PRECARGA_0001",
            "CLASIFICACION": "CHILENA_CONFIRMADA",
            "NACIONALIDAD_FUENTE_1": "Chilena",
            "FUENTE_1": "BASE EXTRANJEROS.xlsx:Hoja2:2",
        },
        {
            "ID_REGISTRO": "PRECARGA_0002",
            "CLASIFICACION": "SIN_FUENTE_CONCLUYENTE",
            "NACIONALIDAD_FUENTE_1": "",
            "FUENTE_1": "",
        },
    ])
    excluded = mod.build_excluidos_nacionalidad(base.drop(columns=["ID_REGISTRO"]), decision)
    assert len(excluded) == 2
    assert set(excluded["ACCION"]) == {
        "EXCLUIR_DE_CARGA_CONSERVAR_EN_AUDITORIA",
        "EXCLUIR_DE_CARGA_CONSERVAR_EN_PENDIENTES_Y_AUDITORIA",
    }


def test_csv_no_termina_con_salto(tmp_path: Path) -> None:
    df = pd.DataFrame([_sample_row()], columns=mod.COLUMNAS_SIES_REGULARES)
    path = tmp_path / "sies.csv"
    mod.write_sies_csv_cp1252_no_final_newline(df, path)
    data = path.read_bytes()
    assert not data.endswith((b"\n", b"\r", b"\r\n"))


def test_conteos_y_regresion_archivo_aprobado() -> None:
    run_dir = ROOT / "estudiantes_extranjeros_2026/resultados/ejecuciones/RECONSTRUCCION_FINAL_EXTRANJEROS_2025_20260625_235455"
    final_185 = pd.read_csv(run_dir / "09_PES/EXTRANJEROS_REGULARES_2025_FINAL_PES_HOJA2.csv", sep=";", dtype=str, keep_default_na=False).fillna("")
    decision = pd.read_csv(
        run_dir / "12_VALIDACION_FINAL_SIES/DIAGNOSTICO_103_CHILENAS_20260626_113142/08_DECISION_NACIONALIDAD_104.csv",
        dtype=str,
        keep_default_na=False,
    ).fillna("")
    sies, _ = mod.prepare_sies_loadable(final_185, decision)
    assert len(final_185) == 185
    assert len(decision) == 104
    assert len(sies) == 81
    assert int(sies["VIGENCIA"].eq("0").sum()) == 16
    assert int(sies["VIGENCIA"].eq("1").sum()) == 65
    reference = mod.regression_reference_frame(
        Path("/Users/alexi/Desktop/EXTRANJEROS_REGULARES_2025_PES_READY_RESIDENCIA_0_20260626_121728.csv")
    )
    assert mod.compare_frames(sies, reference, "sies", "reference").empty
