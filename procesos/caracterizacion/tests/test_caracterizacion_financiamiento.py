from __future__ import annotations

import unittest
from pathlib import Path

from caracterizacion_financiamiento import (
    CODIGOS_FINANCIAMIENTO_G01Q19,
    DETALLES_FINANCIAMIENTO_G01Q19,
    codigos_financiamiento_en_headers,
    validar_cobertura_financiamiento,
)


ROOT = Path(__file__).resolve().parents[1]


def _headers_completos() -> list[str]:
    return [
        f"{codigo}. Pregunta de financiamiento [{indice}]"
        for indice, codigo in enumerate(CODIGOS_FINANCIAMIENTO_G01Q19, start=1)
    ]


class FinanciamientoG01Q19Tests(unittest.TestCase):
    def test_contrato_contiene_las_once_alternativas(self):
        self.assertEqual(len(CODIGOS_FINANCIAMIENTO_G01Q19), 11)
        self.assertEqual(CODIGOS_FINANCIAMIENTO_G01Q19[0], "G01Q19[SQ002]")
        self.assertEqual(CODIGOS_FINANCIAMIENTO_G01Q19[-1], "G01Q19[SQ012]")
        self.assertEqual(
            set(DETALLES_FINANCIAMIENTO_G01Q19),
            set(CODIGOS_FINANCIAMIENTO_G01Q19),
        )

    def test_temporizacion_no_es_alternativa(self):
        headers = _headers_completos() + ["G01Q19Time. Temporizacion"]

        detectados = codigos_financiamiento_en_headers(headers)

        self.assertEqual(detectados, tuple(sorted(CODIGOS_FINANCIAMIENTO_G01Q19)))
        self.assertNotIn("G01Q19TIME", detectados)

    def test_instrumento_completo_supera_validacion(self):
        self.assertEqual(
            validar_cobertura_financiamiento(_headers_completos()),
            CODIGOS_FINANCIAMIENTO_G01Q19,
        )

    def test_alternativa_faltante_bloquea(self):
        with self.assertRaisesRegex(ValueError, r"faltantes=.*SQ012"):
            validar_cobertura_financiamiento(_headers_completos()[:-1])

    def test_alternativa_nueva_no_gobernada_bloquea(self):
        headers = _headers_completos() + ["G01Q19[SQ013]. Nueva alternativa"]

        with self.assertRaisesRegex(ValueError, r"inesperadas=.*SQ013"):
            validar_cobertura_financiamiento(headers)

    def test_word_y_excel_consumen_el_contrato_compartido(self):
        source = (ROOT / "caracterizacion.py").read_text(encoding="utf-8")

        self.assertGreaterEqual(source.count("list(CODIGOS_FINANCIAMIENTO_G01Q19)"), 2)
        self.assertIn("TOTAL SELECCIONES FINANCIAMIENTO", source)
        self.assertIn('hoja="Financiamiento"', source)
        self.assertIn("suma_por_codigo=", source)
        self.assertNotIn('hoja="Financiamiento_Gratuidad"', source)


if __name__ == "__main__":
    unittest.main()
