from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path

import pandas as pd

from caracterizacion_longitudinal import calcular_retencion_longitudinal
from caracterizacion_sies_historico import (
    SIES_AGREGADOS_PATH,
    SIES_MANIFEST_PATH,
    SIES_REQUIRED_MANIFEST_FIELDS,
    cargar_repositorio_sies_versionado,
    preparar_indicadores_sies,
)


ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _bloque_10quater_source() -> str:
    text = (ROOT / "caracterizacion.py").read_text(encoding="utf-8")
    start = text.index("def _ejecutar_bloque_10quater():")
    end = text.index("\n_ejecutar_bloque_10quater()\n", start)
    return text[start:end]


class Hito4CSeparacionDominiosTests(unittest.TestCase):
    def test_pipeline_no_importa_retencion_longitudinal_en_top_level(self) -> None:
        source = (ROOT / "caracterizacion.py").read_text(encoding="utf-8")
        self.assertNotIn(
            "from caracterizacion_retencion import calcular_retencion_longitudinal",
            source,
        )
        self.assertIn("CARACTERIZACION_EJECUTAR_LONGITUDINAL", source)
        self.assertIn("NO_EJECUTADO_EN_CARACTERIZACION", source)
        self.assertIsNotNone(calcular_retencion_longitudinal)

    def test_sectorizado_recibe_universo_en_formato_tabular_estable(self) -> None:
        source = (ROOT / "caracterizacion.py").read_text(encoding="utf-8")
        self.assertIn('"universo_vigente.xlsx"', source)
        self.assertNotIn('"universo_vigente.pkl"', source)
        self.assertNotIn(".to_pickle(_ruta_universo_vigente)", source)

    def test_b10bis_longitudinal_queda_detras_de_opt_in(self) -> None:
        source = (ROOT / "caracterizacion.py").read_text(encoding="utf-8")
        self.assertIn("LONGITUDINAL_NO_EJECUTADO", source)
        self.assertIn("Continuidad/retención omitidas en Caracterización normal", source)
        self.assertIn("if _EJECUTAR_LONGITUDINAL_CARACTERIZACION:", source)

    def test_bloque_sies_no_contiene_cruces_individuales_ni_reconstruccion(self) -> None:
        body = _bloque_10quater_source()
        patrones_prohibidos = [
            r"\bMRUN\b",
            r"\bmrun\b",
            r"\bRUT\b",
            r"RUT_",
            r"_RUT",
            r"CRUCE_SIES_PERSONA",
            r"AUDITORIA_RUT",
            r"RUT_COMUNES",
            r"reporte_matricula_ip_san_sebastian",
            r"EXTRACCION_MATRICULA_SIES",
        ]
        for patron in patrones_prohibidos:
            with self.subTest(patron=patron):
                self.assertIsNone(re.search(patron, body))
        self.assertIn("cargar_repositorio_sies_versionado", body)
        self.assertIn("SIES_RECONSTRUIDA_EN_PIPELINE", body)
        self.assertIn("VERSIONADO_SOLO_LECTURA", body)

    def test_repositorio_sies_versionado_tiene_manifest_obligatorio_y_solo_agregado(self) -> None:
        repo = cargar_repositorio_sies_versionado()
        for field in SIES_REQUIRED_MANIFEST_FIELDS:
            self.assertIn(field, repo.manifest)
        self.assertEqual(repo.manifest["VERSION_HISTORICA"], "SIES_2007_2025_v1")
        self.assertEqual(int(repo.manifest["AÑO_INICIO_HISTORICO"]), 2007)
        self.assertEqual(int(repo.manifest["AÑO_FIN_HISTORICO"]), 2025)
        self.assertEqual(int(repo.manifest["TOTAL_REGISTROS"]), int(repo.agregados["REGISTROS_SIES"].sum()))
        columnas_identidad = [c for c in repo.agregados.columns if re.search(r"(MRUN|RUT|TOKEN|CODCLI)", c, re.I)]
        self.assertEqual(columnas_identidad, [])

    def test_repositorio_sies_permanece_inalterado_para_p1_p2_p3(self) -> None:
        antes = {
            "manifest": _sha256(SIES_MANIFEST_PATH),
            "agregados": _sha256(SIES_AGREGADOS_PATH),
        }
        for _periodo in (1, 2, 3):
            repo = cargar_repositorio_sies_versionado()
            indicadores = preparar_indicadores_sies(repo)
            self.assertIn("SIES_AGREGADO_ANUAL", indicadores)
        despues = {
            "manifest": _sha256(SIES_MANIFEST_PATH),
            "agregados": _sha256(SIES_AGREGADOS_PATH),
        }
        self.assertEqual(antes, despues)

    def test_indicadores_sies_son_agregados_y_reconcilian_total(self) -> None:
        repo = cargar_repositorio_sies_versionado()
        indicadores = preparar_indicadores_sies(repo)
        anual = indicadores["SIES_AGREGADO_ANUAL"]
        programa = indicadores["SIES_AGREGADO_PROGRAMA"]
        self.assertFalse(anual.empty)
        self.assertFalse(programa.empty)
        self.assertEqual(int(anual["REGISTROS_SIES"].sum()), int(repo.manifest["TOTAL_REGISTROS"]))
        self.assertEqual(int(programa["REGISTROS_SIES"].sum()), int(repo.manifest["TOTAL_REGISTROS"]))
        self.assertTrue(pd.api.types.is_integer_dtype(programa["REGISTROS_SIES"]))


if __name__ == "__main__":
    unittest.main()
