import pandas as pd

from scripts.sies_resolver import (
    apply_export_blockers,
    candidates_for_same_academic_components,
    parse_sies_code,
    regenerate_candidates_after_sede_adjustment,
)


def offer():
    return pd.DataFrame(
        {
            "CODIGO_UNICO": ["I162S2C91J2V1", "I162S3C91J2V1", "I162S2C3J2V1", "I162S2C3J2V4"],
            "MODALIDAD": ["1", "1", "1", "1"],
            "JORNADA": ["2", "2", "2", "2"],
            "TIPO_PLAN_CARRERA": ["1", "1", "1", "1"],
            "DURACION_ESTUDIOS": ["5", "5", "8", "8"],
            "DURACION_TOTAL": ["5", "5", "8", "8"],
        }
    )


def test_parse_codigo_unico():
    parsed = parse_sies_code("I162S3C91J2V1")
    assert parsed.valido
    assert parsed.sede == "3"
    assert parsed.carrera == "91"
    assert parsed.jornada == "2"
    assert parsed.version == "1"


def test_ajuste_sede_regenera_candidatos():
    df = pd.DataFrame(
        {
            "CODIGO_CARRERA_SIES_FINAL": ["I162S3C91J2V1"],
            "CODIGOS_SIES_POTENCIALES": ["I162S2C91J2V1"],
            "N_CODES_SIES": [1],
            "SIES_AJUSTE_SEDE_FLAG": ["SI"],
        }
    )
    out, stats = regenerate_candidates_after_sede_adjustment(df, offer())
    assert stats["ajustes_sede_regenerados"] == 1
    assert out.loc[0, "CODIGOS_SIES_POTENCIALES"] == "I162S3C91J2V1"
    assert out.loc[0, "N_CANDIDATOS_FINALES"] == 1


def test_candidatos_compatibles_icre_permanece_multiple():
    codes = candidates_for_same_academic_components("I162S2C3J2V1", offer())
    assert "I162S2C3J2V1" in codes
    assert "I162S2C3J2V4" not in codes


def test_bloquea_pendiente_gobernanza_y_version_sin_traza():
    df = pd.DataFrame(
        {
            "CODIGO_CARRERA_SIES_FINAL": [""],
            "CODIGOS_SIES_POTENCIALES": ["I162S2C3J2V1 | I162S2C3J2V4"],
            "SIES_RESOLUCION_HEURISTICA": ["PENDIENTE_GOBERNANZA"],
            "COD_SED": ["2"],
            "COD_CAR": ["3"],
            "JOR": ["2"],
            "VERSION": ["3"],
            "VERSION_FUENTE_FINAL": ["SIN_FUENTE_FINAL"],
            "VERSION_METODO_FINAL": ["SIN_METODO_FINAL"],
        }
    )
    state, audit = apply_export_blockers(df, pd.Series(["OK_CARGA_PREGRADO"]), offer())
    assert state.iloc[0] == "BLOQUEADO_PENDIENTE_GOBERNANZA"
    assert audit.loc[0, "ESTADO_EXPORTACION_SIES"] == "BLOQUEADO_PENDIENTE_GOBERNANZA"

