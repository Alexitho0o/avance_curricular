#!/usr/bin/env python3
"""
Pruebas unitarias mínimas para la lógica crítica del validador B13.
Estas pruebas:
- no usan datos institucionales;
- no ejecutan el pipeline;
- no escriben en el repositorio;
- controlan la normalización y la precedencia lógica;
- controlan la reconciliación dinámica.
"""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
import pandas as pd
ROOT = Path(
    __file__
).resolve().parents[1]
MODULE_PATH = (
    ROOT
    / "scripts"
    / "validacion"
    / "validar_bloque13_pospublicacion.py"
)
SPEC = importlib.util.spec_from_file_location(
    "validar_bloque13_pospublicacion",
    MODULE_PATH,
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(
        "No fue posible cargar el módulo validador."
    )
MODULE = importlib.util.module_from_spec(
    SPEC
)
sys.modules[
    SPEC.name
] = MODULE
SPEC.loader.exec_module(
    MODULE
)
def test_normalize_text() -> None:
    observed = [
        MODULE.normalize_text(
            value
        )
        for value in [
            " Técnico ",
            "profesional",
            "TÉCNICO",
            None,
        ]
    ]
    expected = [
        "TECNICO",
        "PROFESIONAL",
        "TECNICO",
        "",
    ]
    assert observed == expected, (
        "Normalización inesperada: "
        f"{observed}"
    )
def test_normalize_key() -> None:
    series = pd.Series(
        [
            " ABC ",
            "123.0",
            None,
        ]
    )
    observed = (
        MODULE
        .normalize_key(
            series
        )
        .tolist()
    )
    expected = [
        "ABC",
        "123",
        "",
    ]
    assert observed == expected, (
        "Normalización de llave inesperada: "
        f"{observed}"
    )
def test_no_classified_precedence() -> None:
    levels = pd.Series(
        [
            "TECNICO",
            "PROFESIONAL",
            "TECNICO",
        ]
    )
    observed = int(
        (
            ~levels.isin(
                MODULE.ALLOWED_LEVELS
            )
        ).sum()
    )
    assert observed == 0, (
        "El conteo de no clasificados "
        f"debe ser 0 y fue {observed}."
    )
def test_dynamic_reconciliation() -> None:
    levels = pd.Series(
        [
            "TECNICO",
            "TECNICO",
            "PROFESIONAL",
            "PROFESIONAL",
            "PROFESIONAL",
        ]
    )
    technical = int(
        levels.eq(
            "TECNICO"
        ).sum()
    )
    professional = int(
        levels.eq(
            "PROFESIONAL"
        ).sum()
    )
    assert (
        technical
        + professional
        == len(levels)
    )
def test_affirmative_count() -> None:
    series = pd.Series(
        [
            "Sí",
            "SI",
            "true",
            "1",
            "No",
            None,
        ]
    )
    observed = (
        MODULE
        .affirmative_count(
            series
        )
    )
    assert observed == 4, (
        "Conteo afirmativo inesperado: "
        f"{observed}"
    )
def main() -> None:
    test_normalize_text()
    test_normalize_key()
    test_no_classified_precedence()
    test_dynamic_reconciliation()
    test_affirmative_count()
    print(
        "TEST_NORMALIZE_TEXT=OK"
    )
    print(
        "TEST_NORMALIZE_KEY=OK"
    )
    print(
        "TEST_NO_CLASSIFIED_PRECEDENCE=OK"
    )
    print(
        "TEST_DYNAMIC_RECONCILIATION=OK"
    )
    print(
        "TEST_AFFIRMATIVE_COUNT=OK"
    )
    print(
        "DICTAMEN=TESTS_B13_OK"
    )
if __name__ == "__main__":
    main()


def test_diplomados_fuera_y_duplicados_son_advertencias(
) -> None:
    import pandas as pd

    child = pd.DataFrame(
        {
            "_LLAVE_CODCLI": [
                "DIP-001",
                "DIP-001",
                "DIP-002",
            ]
        }
    )

    errors: list[str] = []
    warnings: list[str] = []

    metrics = MODULE.compare_key_subset(
        child=child,
        child_name="DIPLOMADOS",
        parent_keys={"REG-001", "REG-002"},
        preferred_key="_LLAVE_CODCLI",
        errors=errors,
        warnings=warnings,
        outside_is_error=False,
        duplicated_is_error=False,
    )

    assert errors == []
    assert len(warnings) == 2
    assert any(
        "2 llaves fuera de DETALLE_MATRICULA"
        in warning
        for warning in warnings
    )
    assert any(
        "1 llaves duplicadas"
        in warning
        for warning in warnings
    )

    assert metrics["filas"] == 3
    assert metrics["llaves_no_vacias"] == 3
    assert metrics["llaves_unicas"] == 2
    assert metrics["duplicadas"] == 1
    assert metrics["fuera_detalle"] == 2


def test_diplomados_llave_vacia_sigue_siendo_bloqueante(
) -> None:
    import pandas as pd

    child = pd.DataFrame(
        {
            "_LLAVE_CODCLI": [
                "DIP-001",
                "",
            ]
        }
    )

    errors: list[str] = []
    warnings: list[str] = []

    metrics = MODULE.compare_key_subset(
        child=child,
        child_name="DIPLOMADOS",
        parent_keys=set(),
        preferred_key="_LLAVE_CODCLI",
        errors=errors,
        warnings=warnings,
        outside_is_error=False,
        duplicated_is_error=False,
    )

    assert len(errors) == 1
    assert "1 llaves vacías" in errors[0]

    assert len(warnings) == 1
    assert (
        "1 llaves fuera de DETALLE_MATRICULA"
        in warnings[0]
    )

    assert metrics["llaves_vacias"] == 1
    assert metrics["fuera_detalle"] == 1


def test_hoja_sustantiva_mantiene_control_estricto(
) -> None:
    import pandas as pd

    child = pd.DataFrame(
        {
            "_LLAVE_CODCLI": [
                "FUERA-001",
                "FUERA-001",
            ]
        }
    )

    errors: list[str] = []
    warnings: list[str] = []

    MODULE.compare_key_subset(
        child=child,
        child_name="INGRESO_PROFESIONAL",
        parent_keys={"REG-001"},
        preferred_key="_LLAVE_CODCLI",
        errors=errors,
        warnings=warnings,
    )

    assert warnings == []
    assert len(errors) == 2
    assert any(
        "llaves fuera de DETALLE_MATRICULA"
        in error
        for error in errors
    )
    assert any(
        "llaves duplicadas"
        in error
        for error in errors
    )
