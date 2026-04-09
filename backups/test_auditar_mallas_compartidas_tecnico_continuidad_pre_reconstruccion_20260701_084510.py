from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import auditar_mallas_compartidas_tecnico_continuidad as audit  # noqa: E402


def test_normalizacion_logistica_y_acentos():
    assert audit.normalize_text("Ingeniería en Logística") == "INGENIERIA EN LOGISTICA"
    assert audit.is_logistica("Técnico en Logística")


def test_encabezados_duplicados_por_posicion():
    headers = ["CODIGO_UNICO", "PLAN", "PLAN", "CODIGO_UNICO"]
    duplicates = audit.duplicate_header_positions(headers)
    assert duplicates["PLAN"] == [1, 2]
    assert duplicates["CODIGO_UNICO"] == [0, 3]


def test_mascaras_booleanas_estrictas():
    series = pd.Series([True, None, "SI", "NO", 0, 1])
    mask = audit.strict_boolean_mask(series)
    assert mask.dtype == bool
    assert mask.tolist() == [True, False, True, False, False, True]


def test_lectura_csv_con_punto_y_coma(tmp_path):
    path = tmp_path / "datos.csv"
    path.write_text("A;B\n1;Logística\n", encoding="utf-8")
    dataframe, metadata = audit.read_table(path)
    assert metadata["delimiter"] == ";"
    assert dataframe.loc[0, "B"] == "Logística"


def test_lectura_tsv(tmp_path):
    path = tmp_path / "datos.tsv"
    path.write_text("A\tB\n1\tTLOG\n", encoding="utf-8")
    dataframe, metadata = audit.read_table(path)
    assert metadata["delimiter"] == "\t"
    assert dataframe.loc[0, "B"] == "TLOG"


def test_lectura_cp1252(tmp_path):
    path = tmp_path / "datos.csv"
    path.write_bytes("A;B\n1;Log\xedstica\n".encode("cp1252"))
    dataframe, metadata = audit.read_table(path)
    assert metadata["encoding"] == "cp1252"
    assert dataframe.loc[0, "B"] == "Logística"


def test_lectura_excel(tmp_path):
    path = tmp_path / "datos.xlsx"
    pd.DataFrame([{"A": "ILOG", "B": "Ingeniería"}]).to_excel(
        path, sheet_name="Hoja1", index=False
    )
    sheets = audit.read_excel(path)
    assert sheets["Hoja1"].loc[0, "A"] == "ILOG"


def test_separacion_ilog_tlog():
    assert audit.classify_program_type({"PLAN": "ILOG", "NOMBRE": "Ingeniería"}) == "PROFESIONAL"
    assert audit.classify_program_type({"PLAN": "TLOG", "NOMBRE": "Técnico"}) == "TECNICO"


def test_separacion_plan_estudios_y_plan_de_estudio():
    row = {
        "PLAN_ESTUDIOS": "SIES-01",
        "PLAN_DE_ESTUDIO": "ILOG",
        "CODIGO_UNICO": "CU1",
    }
    json_row = audit.serialize_row(row)
    fields = audit.extract_known_fields(json_row)
    assert fields["PLAN_ESTUDIOS"] == "SIES-01"
    assert fields["PLAN_DE_ESTUDIO"] == "ILOG"


def test_separacion_codigo_unico_y_codigo_unico_final():
    row = {"CODIGO_UNICO": "123", "CODIGO_UNICO_FINAL": "456"}
    fields = audit.extract_known_fields(audit.serialize_row(row))
    assert fields["CODIGO_UNICO"] == "123"
    assert fields["CODIGO_UNICO_FINAL"] == "456"


def test_deteccion_mismo_pdf():
    assert audit.compare_pdf("malla_logistica.pdf", "MALLA LOGISTICA.pdf") == "SI"
    assert audit.compare_pdf("tecnico.pdf", "ingenieria.pdf") == "NO"


def test_deteccion_planes_distintos():
    assert audit.compare_plan("ILOG", "TLOG") == "PLANES_DISTINTOS"
    assert audit.compare_plan("ILOG", "ilog") == "MISMO_PLAN"


def test_calculo_cobertura():
    result = audit.calculate_coverage(["A", "B", "C"], ["B", "C", "D"])
    assert result["ASIGNATURAS_TECNICAS"] == 3
    assert result["COMUNES_TOTAL_VALIDADO"] == 2
    assert result["COBERTURA_TECNICO_EN_PROFESIONAL"] == 2 / 3
    assert result["JACCARD"] == 0.5


def test_no_agrupacion_por_nombre_solamente():
    assert not audit.has_non_name_evidence({"NOMBRE": "Logística"})
    assert audit.has_non_name_evidence({"NOMBRE": "Logística", "MISMO_PDF": "SI"})


def test_preservacion_de_filas_con_mascara_estricta():
    dataframe = pd.DataFrame({"valor": [1, 2, 3], "usar": ["SI", None, "NO"]})
    mask = audit.strict_boolean_mask(dataframe["usar"])
    filtered = dataframe.loc[mask]
    assert len(dataframe) == 3
    assert filtered["valor"].tolist() == [1]


def test_exclusion_de_venv_y_respaldos(tmp_path):
    venv_path = tmp_path / ".venv" / "archivo.py"
    backup_path = tmp_path / "scripts" / "algo_respaldo_antes_fix.py"
    assert audit.should_exclude_path(venv_path)
    assert audit.classify_backup(backup_path) == "SI"


def test_no_modificacion_de_fuentes_al_leer(tmp_path):
    path = tmp_path / "fuente.tsv"
    path.write_text("A\tB\n1\tLogística\n", encoding="utf-8")
    before = audit.sha256_file(path)
    dataframe, _ = audit.read_table(path)
    after = audit.sha256_file(path)
    assert dataframe.shape == (1, 2)
    assert before == after


def test_clasificacion_de_respaldo():
    assert (
        audit.classify_evidence_level(Path("docs/Instructivo_Avance Curricular SIES - 2026.txt"))
        == "REGLA_OFICIAL"
    )
    assert audit.classify_evidence_level(Path("scripts/proceso.py")) == "IMPLEMENTACION_TECNICA"
    assert audit.classify_evidence_level(Path("salida.tsv")) == "DATO_OBSERVADO"
