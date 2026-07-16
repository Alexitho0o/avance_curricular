"""Pruebas del calculo oficial de rotacion academica SIES."""

from pathlib import Path

import pandas as pd

from personal_academico_2026.kpi_rotacion.comparacion import compare_years
from personal_academico_2026.kpi_rotacion.historico_consolidacion import (
    build_duplicates,
    build_panel,
    build_reentries,
    compare_pair,
    desaggregate,
    historical_summary,
)
from personal_academico_2026.kpi_rotacion.kpis import build_kpi_tables
from personal_academico_2026.kpi_rotacion.lectura import AcademicDataset
from personal_academico_2026.kpi_rotacion.validacion import (
    build_identifier_series,
    validate_cross_year_consistency,
    validate_duplicates,
)


def official_headers() -> list[str]:
    """Entrega una estructura minima compatible con la comparacion."""

    return [
        "TIPO_DOCUMENTO",
        "NUM_DOCUMENTO",
        "DV",
        "PRIMER_APELLIDO",
        "SEGUNDO_APELLIDO",
        "NOMBRES",
        "SEXO",
        "FECHA_NACIMIENTO",
        "NIVEL_FORMACION_ACADEMICO",
        "PRINCIPAL_CARGO_ACADEMICO",
        "CARGO_NORMALIZADO",
        "NIVEL_SUPERIOR_ADSCRIPCION",
        "NIVEL_SECUNDARIO_ADSCRIPCION",
        "NOMBRE_PRINCIPAL_PROGRAMA",
        "TOTAL_HORAS_PRINCIPAL_PROGRAMA",
        "NUM_HORAS_PLANTA",
        "NUM_HORAS_CONTRATA",
        "NUM_HORAS_HONORARIOS",
        "JERARQUIA_ACADEMICA",
        "JERARQUIA_ACADEMICA_OCDE",
        "VIGENCIA",
    ]


def row(num_documento: str, nombre: str) -> dict[str, str]:
    """Construye una fila academica sintetica para pruebas."""

    values = {column: "" for column in official_headers()}
    values.update(
        {
            "TIPO_DOCUMENTO": "R",
            "NUM_DOCUMENTO": num_documento,
            "DV": "1",
            "PRIMER_APELLIDO": "PRUEBA",
            "SEGUNDO_APELLIDO": "SIES",
            "NOMBRES": nombre,
            "SEXO": "H",
            "FECHA_NACIMIENTO": "1980-01-01",
            "NIVEL_FORMACION_ACADEMICO": "3",
            "PRINCIPAL_CARGO_ACADEMICO": "DOCENTE",
            "CARGO_NORMALIZADO": "9",
            "NIVEL_SUPERIOR_ADSCRIPCION": "VICERRECTORIA ACADEMICA",
            "NIVEL_SECUNDARIO_ADSCRIPCION": "DIRECCION DE CARRERA",
            "NOMBRE_PRINCIPAL_PROGRAMA": "FORMACION GENERAL",
            "TOTAL_HORAS_PRINCIPAL_PROGRAMA": "10",
            "NUM_HORAS_PLANTA": "0",
            "NUM_HORAS_CONTRATA": "0",
            "NUM_HORAS_HONORARIOS": "10",
            "JERARQUIA_ACADEMICA": "NO APLICA",
            "JERARQUIA_ACADEMICA_OCDE": "5",
            "VIGENCIA": "1",
        }
    )
    return values


def run_pair(base_rows: list[dict[str, str]], comparison_rows: list[dict[str, str]]):
    """Ejecuta comparacion sintetica con estructura minima."""

    headers = official_headers()
    base = pd.DataFrame(base_rows, columns=headers)
    comparison = pd.DataFrame(comparison_rows, columns=headers)
    result = compare_years(base, comparison, 2025, 2026, headers)
    tables = build_kpi_tables(result, 2025, 2026, headers)
    return result, tables


def official_values(tables: dict[str, pd.DataFrame]) -> dict[str, float]:
    """Retorna valores oficiales por indicador."""

    official = tables["indicador_oficial"].set_index("INDICADOR")["VALOR"].to_dict()
    return official


def dataset(frame: pd.DataFrame, path: str = "memoria.csv") -> AcademicDataset:
    """Crea un dataset academico sintetico para validaciones."""

    return AcademicDataset(
        frame=frame,
        path=Path(path),
        delimiter=";",
        encoding="utf-8",
        has_header=True,
        rows=len(frame),
        columns=len(frame.columns),
        expected_columns=len(frame.columns),
        file_sha256="sha",
        field_count_errors=(),
    )


def test_tasa_oficial_excluye_nuevos_ingresos() -> None:
    """Verifica que nuevos ingresos no entren en la formula oficial SIES."""

    result, tables = run_pair(
        [row("10000001", "UNO"), row("10000002", "DOS")],
        [row("10000001", "UNO"), row("10000003", "TRES")],
    )
    official = official_values(tables)
    institutional = tables["kpi_institucional"].set_index("INDICADOR")["VALOR"].to_dict()

    assert official["TOTAL ACADEMICOS ANIO BASE"] == 2
    assert official["ACADEMICOS QUE PERMANECEN"] == 1
    assert official["ACADEMICOS QUE ROTAN"] == 1
    assert official["TASA OFICIAL DE ROTACION"] == 50.0
    assert institutional["INGRESOS"] == 1
    assert result.detail["NUEVO"].sum() == 1


def test_formula_basica_nadie_rota_y_todos_rotan() -> None:
    """Cubre formula basica, nadie rota y todos rotan."""

    _result, tables = run_pair(
        [row("10000001", "UNO"), row("10000002", "DOS")],
        [row("10000001", "UNO"), row("10000002", "DOS")],
    )
    assert official_values(tables)["TASA OFICIAL DE ROTACION"] == 0.0

    _result, tables = run_pair(
        [row("10000001", "UNO"), row("10000002", "DOS")],
        [row("10000003", "TRES")],
    )
    official = official_values(tables)
    assert official["ACADEMICOS QUE ROTAN"] == 2
    assert official["TASA OFICIAL DE ROTACION"] == 100.0


def test_universos_vacios_y_vigencia() -> None:
    """Valida base vacia, comparacion vacia y efecto de VIGENCIA."""

    _result, tables = run_pair([], [row("10000001", "UNO")])
    official = official_values(tables)
    assert official["TOTAL ACADEMICOS ANIO BASE"] == 0
    assert official["TASA OFICIAL DE ROTACION"] == 0.0

    _result, tables = run_pair([row("10000001", "UNO")], [])
    official = official_values(tables)
    assert official["ACADEMICOS QUE ROTAN"] == 1
    assert official["TASA OFICIAL DE ROTACION"] == 100.0

    inactive_comp = row("10000001", "UNO")
    inactive_comp["VIGENCIA"] = "0"
    _result, tables = run_pair([row("10000001", "UNO")], [inactive_comp])
    assert official_values(tables)["ACADEMICOS QUE ROTAN"] == 1

    inactive_base = row("10000001", "UNO")
    inactive_base["VIGENCIA"] = "0"
    _result, tables = run_pair([inactive_base], [row("10000001", "UNO")])
    assert official_values(tables)["TOTAL ACADEMICOS ANIO BASE"] == 0


def test_normalizacion_documental_rut_y_pasaporte() -> None:
    """Valida K minuscula, puntos, espacios y DV de pasaporte."""

    frame = pd.DataFrame(
        [
            row("12.345.678", "RUT"),
            row("10000002", "RUTK"),
            {
                **row("AB 123", "PASAPORTE"),
                "TIPO_DOCUMENTO": "P",
                "DV": "",
            },
            {
                **row("CD 456", "PASAPORTE_NAN"),
                "TIPO_DOCUMENTO": "P",
                "DV": float("nan"),
            },
        ],
        columns=official_headers(),
    )
    frame.loc[1, "DV"] = "k"

    identifiers = build_identifier_series(frame).tolist()

    assert identifiers[0] == "R|12345678|1"
    assert identifiers[1].endswith("|K")
    assert identifiers[2] == "P|AB123|"
    assert identifiers[3] == "P|CD456|"


def test_mismo_rut_nombre_diferente_permanece() -> None:
    """Los nombres no se usan como identificador principal."""

    _result, tables = run_pair([row("10000001", "UNO")], [row("10000001", "OTRO_NOMBRE")])

    official = official_values(tables)
    assert official["ACADEMICOS QUE PERMANECEN"] == 1
    assert official["ACADEMICOS QUE ROTAN"] == 0


def test_alertas_criticas_identidad_sexo_y_fecha() -> None:
    """Sexo y fecha de nacimiento distintos generan alerta critica."""

    base = pd.DataFrame([row("10000001", "UNO")], columns=official_headers())
    comparison = pd.DataFrame([row("10000001", "UNO")], columns=official_headers())
    comparison.loc[0, "SEXO"] = "M"
    comparison.loc[0, "FECHA_NACIMIENTO"] = "1981-01-01"

    issues = validate_cross_year_consistency(dataset(base), dataset(comparison), 2025, 2026)
    critical_codes = {issue.codigo for issue in issues if issue.severidad == "CRITICO"}

    assert "SEXO_DISTINTO_ENTRE_ANIOS" in critical_codes
    assert "FECHA_NACIMIENTO_DISTINTA_ENTRE_ANIOS" in critical_codes


def test_tipo_documental_distinto_no_fusiona() -> None:
    """Mismo numero con tipo documental distinto conserva identidades separadas."""

    passport = row("10000001", "PAS")
    passport["TIPO_DOCUMENTO"] = "P"
    passport["DV"] = ""
    result, tables = run_pair([row("10000001", "RUT")], [passport])

    official = official_values(tables)
    assert official["ACADEMICOS QUE ROTAN"] == 1
    assert int(result.detail["NUEVO"].sum()) == 1


def test_duplicado_exacto_y_conflictivo() -> None:
    """Valida duplicados exactos y conflictivos."""

    frame = pd.DataFrame([row("10000001", "UNO"), row("10000001", "UNO")], columns=official_headers())
    issues = validate_duplicates(dataset(frame), 2025)
    assert any(issue.codigo == "DUPLICADO_IDENTIFICADOR" for issue in issues)

    longitudinal = pd.DataFrame(
        [
            {"ANIO": 2025, "CLAVE_DOCUMENTAL": "R|1|1", "LINEA_ORIGEN": 1, "CARGO_NORMALIZADO": "A"},
            {"ANIO": 2025, "CLAVE_DOCUMENTAL": "R|1|1", "LINEA_ORIGEN": 2, "CARGO_NORMALIZADO": "B"},
        ]
    )
    duplicates = build_duplicates(longitudinal)
    assert duplicates.loc[0, "TIPO_DUPLICADO"] == "DUPLICADO_CONFLICTIVO"


def test_reingreso_y_anio_sin_fuente_na() -> None:
    """El reingreso se detecta y un anio sin fuente queda NA."""

    longitudinal = pd.DataFrame(
        [
            {"ANIO": 2022, "CLAVE_DOCUMENTAL": "R|1|1", "ES_VIGENTE": True},
            {"ANIO": 2024, "CLAVE_DOCUMENTAL": "R|1|1", "ES_VIGENTE": True},
        ]
    )
    panel = build_panel(longitudinal, [2022, 2023, 2024], {2022, 2024})
    reentries = build_reentries(panel)

    assert pd.isna(panel.loc[0, "2023"])
    assert reentries.empty

    panel = build_panel(longitudinal, [2022, 2023, 2024], {2022, 2023, 2024})
    reentries = build_reentries(panel)
    assert reentries.loc[0, "ANIO_REINGRESO"] == 2024


def test_comparacion_no_comparable_horas_y_tramo_base() -> None:
    """Comparacion conservadora, horas no afectan presencia y tramo usa anio base."""

    longitudinal = pd.DataFrame(
        [
            {
                "ANIO": 2025,
                "CLAVE_DOCUMENTAL": "R|1|1",
                "ES_VIGENTE": True,
                "TRAMO_HORAS": "MENOS_DE_11",
            },
            {
                "ANIO": 2026,
                "CLAVE_DOCUMENTAL": "R|1|1",
                "ES_VIGENTE": True,
                "TRAMO_HORAS": "39_O_MAS",
            },
        ]
    )
    decisions = pd.DataFrame(
        [
            {"anio": 2025, "archivo_seleccionado": "a", "hash": "1"},
            {"anio": 2026, "archivo_seleccionado": "b", "hash": "2"},
        ]
    )
    summary, detail = compare_pair(longitudinal, decisions, 2025, 2026)
    detail = detail.merge(longitudinal[["ANIO", "CLAVE_DOCUMENTAL", "TRAMO_HORAS"]].rename(columns={"ANIO": "ANIO_BASE"}), how="left")
    tramo = desaggregate(detail, "TRAMO_HORAS", "TRAMO_HORAS")

    assert summary["PERMANECEN"] == 1
    assert summary["ESTADO_APTITUD"] == "RESULTADO_EXPLORATORIO_NO_PUBLICABLE"
    assert tramo.loc[0, "CATEGORIA"] == "MENOS_DE_11"


def test_identidades_de_conjuntos_y_tasa_ponderada() -> None:
    """Verifica identidades de dotacion y tasa ponderada historica."""

    result, tables = run_pair(
        [row("10000001", "UNO"), row("10000002", "DOS")],
        [row("10000001", "UNO"), row("10000003", "TRES")],
    )
    base_rows = result.detail[result.detail["ESTADO_ROTACION"].isin(["PERMANECE", "ROTA"])]
    comp_rows = result.detail[result.detail["ESTADO_ROTACION"].isin(["PERMANECE", "NUEVO INGRESO"])]

    assert len(base_rows) == int(result.detail["PERMANECE"].sum() + result.detail["ROTA"].sum())
    assert len(comp_rows) == int(result.detail["PERMANECE"].sum() + result.detail["NUEVO"].sum())

    kpi = pd.DataFrame(
        [
            {"DOTACION_BASE": 10, "ROTAN": 2, "TASA_ROTACION_SIES": 20.0},
            {"DOTACION_BASE": 20, "ROTAN": 5, "TASA_ROTACION_SIES": 25.0},
        ]
    )
    summary = historical_summary(kpi, pd.DataFrame([{"x": 1}]), [2024, 2025, 2026])
    assert summary["promedio_simple_tasas_anuales"] == 22.5
    assert summary["tasa_ponderada_historica"] == (7 / 30) * 100
