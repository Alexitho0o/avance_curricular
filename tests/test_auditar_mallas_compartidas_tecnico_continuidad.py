from pathlib import Path
import sys
import warnings

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import auditar_mallas_compartidas_tecnico_continuidad as audit  # noqa: E402


def test_01_normalizacion_de_acentos():
    assert audit.normalize_text("Técnico en Logística") == "TECNICO EN LOGISTICA"


def test_02_lectura_utf8(tmp_path):
    path = tmp_path / "utf8.csv"
    path.write_text("A;B\n1;Logística\n", encoding="utf-8")
    df, meta = audit.read_table(path)
    assert meta["encoding"] in {"utf-8", "utf-8-sig"}
    assert df.loc[0, "B"] == "Logística"


def test_03_lectura_cp1252(tmp_path):
    path = tmp_path / "cp.csv"
    path.write_bytes("A;B\n1;Log\xedstica\n".encode("cp1252"))
    df, meta = audit.read_table(path)
    assert meta["encoding"] == "cp1252"
    assert df.loc[0, "B"] == "Logística"


def test_04_csv_punto_y_coma(tmp_path):
    path = tmp_path / "semi.csv"
    path.write_text("A;B\n1;2\n", encoding="utf-8")
    _, meta = audit.read_table(path)
    assert meta["delimiter"] == ";"


def test_05_tsv(tmp_path):
    path = tmp_path / "datos.tsv"
    path.write_text("A\tB\n1\tTLOG\n", encoding="utf-8")
    df, meta = audit.read_table(path)
    assert meta["delimiter"] == "\t"
    assert df.loc[0, "B"] == "TLOG"


def test_06_excel(tmp_path):
    path = tmp_path / "datos.xlsx"
    pd.DataFrame([{"PLAN": "ILOG"}]).to_excel(path, sheet_name="Hoja1", index=False)
    sheets = audit.read_excel(path)
    assert sheets["Hoja1"].loc[0, "PLAN"] == "ILOG"


def test_07_encabezados_duplicados():
    duplicates = audit.duplicate_header_positions(["A", "B", "A", "A"])
    assert duplicates["A"] == [0, 2, 3]


def test_08_conservacion_columnas_duplicadas(tmp_path):
    path = tmp_path / "dup.tsv"
    path.write_text("A\tA\tB\n1\t2\t3\n", encoding="utf-8")
    df, meta = audit.read_table(path)
    assert list(df.columns) == ["A__POS_0", "A__POS_1", "B"]
    assert meta["duplicate_headers"]["A"] == [0, 1]
    assert df.loc[0, "A__POS_1"] == "2"


def test_09_mascaras_booleanas_estrictas():
    mask = audit.strict_boolean_mask(pd.Series(["SI", None, "NO", 1, 0]))
    assert mask.dtype == bool
    assert mask.tolist() == [True, False, False, True, False]


def test_10_ausencia_pandas4warning():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        audit.strict_boolean_mask(pd.Series(["SI", "NO"]))
    assert not [w for w in caught if "Pandas4" in str(w.message)]


def test_11_separacion_ilog_tlog():
    assert audit.classify_program_type({"PLAN_DE_ESTUDIO_INSTITUCIONAL": "TLOG"}) == ("TECNICO", "SI")
    assert audit.classify_program_type({"PLAN_DE_ESTUDIO_INSTITUCIONAL": "ILOG"}) == ("PROFESIONAL", "SI")


def test_12_separacion_plan_estudios_plan_de_estudio():
    row = {"PLAN_ESTUDIOS": "1234", "PLAN_DE_ESTUDIO": "ILOG"}
    assert audit.pick(row, ["PLAN_ESTUDIOS"]) == "1234"
    assert audit.pick(row, ["PLAN_DE_ESTUDIO"]) == "ILOG"


def test_13_separacion_codigo_unico_final():
    row = {"CODIGO_UNICO": "11", "CODIGO_UNICO_FINAL": "22"}
    assert audit.pick(row, ["CODIGO_UNICO"]) == "11"
    assert audit.pick(row, ["CODIGO_UNICO_FINAL"]) == "22"


def test_14_mismo_pdf():
    assert audit.compare_pdf("Malla Logistica.pdf", "malla_logistica.pdf") == "SI"


def test_15_pdf_distintos():
    assert audit.compare_pdf("tec.pdf", "ing.pdf") == "NO"


def test_16_mismo_plan():
    assert audit.compare_plan("ILOG", "ilog") == "SI"


def test_17_planes_distintos():
    assert audit.compare_plan("ILOG", "TLOG") == "NO"


def test_18_calculo_cobertura():
    result = audit.calculate_coverage(["A", "B"], ["B", "C"])
    assert result["COBERTURA_TECNICO_EN_PROFESIONAL"] == 0.5


def test_19_calculo_jaccard():
    result = audit.calculate_coverage(["A", "B"], ["B", "C"])
    assert result["JACCARD"] == 1 / 3


def test_20_preservacion_filas():
    df = pd.DataFrame({"x": [1, 2, 3], "flag": ["SI", "NO", None]})
    filtered = df.loc[audit.strict_boolean_mask(df["flag"])]
    assert len(df) == 3
    assert filtered["x"].tolist() == [1]


def test_21_exclusion_git(tmp_path):
    assert audit.should_exclude_path(tmp_path / ".git" / "x")


def test_22_exclusion_venv(tmp_path):
    assert audit.should_exclude_path(tmp_path / ".venv" / "x")


def test_23_exclusion_carpeta_activa(tmp_path):
    run = tmp_path / "run"
    path = run / "salida.tsv"
    assert audit.should_exclude_path(path, run)


def test_24_no_modificacion_originales_al_leer(tmp_path):
    path = tmp_path / "fuente.tsv"
    path.write_text("A\tB\n1\t2\n", encoding="utf-8")
    before = audit.sha256_file(path)
    audit.read_table(path)
    assert audit.sha256_file(path) == before


def test_25_reanudacion_valida(tmp_path):
    args = audit.parse_args(["--ejecutar-completo", "--reanudar", "--carpeta-ejecucion", str(tmp_path)])
    ctx = audit.ExecutionContext(audit.REPO_ROOT, tmp_path, args)
    audit.ensure_run_structure(tmp_path)
    out = tmp_path / "x.tsv"
    audit.write_tsv(out, [{"A": "1"}], ["A"])
    spec = audit.StageSpec("S", "B", lambda c: None, ["x.tsv"], {"x.tsv": ["A"]})
    audit.write_json(audit.state_path(ctx), {"estado_general": "EN_EJECUCION", "etapas": {"S": {"estado": "COMPLETADA", "hashes": {"x.tsv": audit.sha256_file(out)}}}})
    ok, _ = audit.can_resume_stage(ctx, spec)
    assert ok


def test_26_reanudacion_salida_invalida(tmp_path):
    args = audit.parse_args(["--ejecutar-completo", "--reanudar", "--carpeta-ejecucion", str(tmp_path)])
    ctx = audit.ExecutionContext(audit.REPO_ROOT, tmp_path, args)
    audit.ensure_run_structure(tmp_path)
    spec = audit.StageSpec("S", "B", lambda c: None, ["x.tsv"], {"x.tsv": ["A"]})
    audit.write_json(audit.state_path(ctx), {"estado_general": "EN_EJECUCION", "etapas": {"S": {"estado": "COMPLETADA", "hashes": {}}}})
    ok, reason = audit.can_resume_stage(ctx, spec)
    assert not ok
    assert "salidas invalidas" in reason


def test_27_sobrescritura_bloqueada(tmp_path):
    args = audit.parse_args(["--ejecutar-completo", "--reanudar", "--carpeta-ejecucion", str(tmp_path)])
    ctx = audit.ExecutionContext(audit.REPO_ROOT, tmp_path, args)
    audit.ensure_run_structure(tmp_path)
    spec = audit.StageSpec("S", "B", lambda c: None, ["x.tsv"], {"x.tsv": ["A"]})
    audit.write_json(audit.state_path(ctx), {"estado_general": "EN_EJECUCION", "etapas": {"S": {"estado": "COMPLETADA", "hashes": {}}}})
    try:
        audit.run_stage(ctx, spec)
    except RuntimeError:
        assert True
    else:
        assert False


def test_28_forzar_con_respaldo(tmp_path):
    args = audit.parse_args(["--ejecutar-completo", "--forzar", "--carpeta-ejecucion", str(tmp_path)])
    ctx = audit.ExecutionContext(audit.REPO_ROOT, tmp_path, args)
    audit.ensure_run_structure(tmp_path)
    out = tmp_path / "x.tsv"
    audit.write_tsv(out, [{"A": "1"}], ["A"])
    spec = audit.StageSpec("S", "B", lambda c: None, ["x.tsv"], {"x.tsv": ["A"]})
    audit.backup_existing_outputs(ctx, spec)
    backups = list((tmp_path / "07_RESPALDOS").rglob("x.tsv"))
    assert backups


def test_29_conclusion_con_evidencia_suficiente():
    conclusion, respaldo, rec = audit.decide_conclusion({"carreras_tecnicas_identificadas": 1, "carreras_profesionales_identificadas": 1, "MISMO_PDF": "SI", "COBERTURA_TECNICO_EN_PROFESIONAL": 1})
    assert conclusion == "MISMO_PDF_Y_MISMA_MALLA_OBSERVADA"
    assert respaldo == "DATO_OBSERVADO"
    assert rec == "A"


def test_30_conclusion_sin_evidencia_suficiente():
    conclusion, respaldo, rec = audit.decide_conclusion({"carreras_tecnicas_identificadas": 0, "carreras_profesionales_identificadas": 1})
    assert conclusion == "SIN_EVIDENCIA_SUFICIENTE"
    assert respaldo == "HIPOTESIS_O_PENDIENTE"
    assert rec == "E"


def test_31_no_equivalencia_por_nombre_solamente():
    assert not audit.has_non_name_evidence({"NOMBRE": "Logística"})
    assert audit.has_non_name_evidence({"MISMO_PDF": "SI"})


def test_32_no_aplicacion_decisiones_humanas():
    args = audit.parse_args(["--ejecutar-completo"])
    cfg = audit.default_config(args)
    assert cfg["restricciones"]["precarga"] == "NO_GENERAR"
    assert cfg["restricciones"]["pes"] == "NO_GENERAR"
    assert cfg["restricciones"]["apto_para_carga"] == "NO"


def test_33_clasificacion_respaldo_oficial_restringida():
    assert audit.classify_evidence_level(Path("Instructivo_Avance Curricular SIES - 2026.txt")) == "REGLA_OFICIAL"
    assert audit.classify_evidence_level(Path("manual_matrícula_unificada.txt")) != "REGLA_OFICIAL"


def test_34_clave_asignatura_por_codigo():
    assert audit.extract_subject_key({"CODIGO_ASIGNATURA_CANONICO": "MAT101", "NOMBRE_ASIGNATURA_CANONICO": "X"}).startswith("COD::")


def test_35_clave_asignatura_por_nombre_nivel():
    key = audit.extract_subject_key({"NOMBRE_ASIGNATURA_CANONICO": "Costos", "NIVEL_CANONICO": "1"})
    assert key == "NOM::COSTOS::NIV::1"
