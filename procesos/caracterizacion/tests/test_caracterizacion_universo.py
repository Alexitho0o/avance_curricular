from __future__ import annotations

import re
import unittest

import pandas as pd

from caracterizacion_universo import (
    TIPO_CATALOGO_EXCLUSION,
    TIPO_DIPLOMADO,
    TIPO_POSTITULO,
    TIPO_PREGRADO,
    TIPO_SIN_INFORMACION,
    clasificar_programa,
    mascara_programas_excluidos,
    normalizar_programa,
)


class ClasificadorProgramaTests(unittest.TestCase):
    def test_normaliza_acentos_caja_puntuacion_y_espacios(self):
        self.assertEqual(
            normalizar_programa("  Post-TÍTULO   en Gestión  "),
            "POST TITULO EN GESTION",
        )

    def test_detecta_diplomado_no_presente_en_catalogo_historico(self):
        nombre = "Diplomado en Seguridad Ofensiva y Ethical Hacking"
        self.assertEqual(clasificar_programa(nombre), TIPO_DIPLOMADO)

    def test_detecta_variantes_de_postitulo(self):
        variantes = (
            "POSTÍTULO EN DOCENCIA",
            "postitulo en docencia",
            "Post Título en Docencia",
            "post-titulo en docencia",
            "  POST   TÍTULO EN DOCENCIA  ",
        )
        for nombre in variantes:
            with self.subTest(nombre=nombre):
                self.assertEqual(clasificar_programa(nombre), TIPO_POSTITULO)

    def test_catalogo_explicito_excluye_nombre_sin_palabra_clave(self):
        catalogo = ["Programa Especial de Actualización Profesional"]
        self.assertEqual(
            clasificar_programa(
                " programa especial de actualización profesional ",
                catalogo_exclusion=catalogo,
            ),
            TIPO_CATALOGO_EXCLUSION,
        )

    def test_pregrado_y_continuidad_no_son_falsos_positivos(self):
        for nombre in (
            "Ingeniería en Ciberseguridad",
            "Continuidad Ingeniería en Administración",
            "Técnico de Nivel Superior en Educación",
            "TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA",
        ):
            with self.subTest(nombre=nombre):
                self.assertEqual(clasificar_programa(nombre), TIPO_PREGRADO)

    def test_sin_informacion_es_categoria_explicita(self):
        for nombre in (None, pd.NA, float("nan"), "   "):
            with self.subTest(nombre=nombre):
                self.assertEqual(clasificar_programa(nombre), TIPO_SIN_INFORMACION)

    def test_patrones_adicionales_son_parametrizables(self):
        self.assertEqual(
            clasificar_programa(
                "Certificado Profesional en Datos",
                patrones={"CERTIFICADO": re.compile(r"\bCERTIFICADO\b")},
            ),
            "CERTIFICADO",
        )

    def test_mascara_preserva_indice_y_combina_patrones_con_catalogo(self):
        programas = pd.Series(
            [
                "Ingeniería Comercial",
                "DIPLOMADO EN ANALÍTICA",
                "Post Título en Docencia",
                "Programa especial",
                None,
            ],
            index=[11, 13, 17, 19, 23],
            name="NOMBRE_L",
        )
        mascara = mascara_programas_excluidos(
            programas,
            catalogo_exclusion=["PROGRAMA ESPECIAL"],
        )

        self.assertEqual(mascara.index.tolist(), programas.index.tolist())
        self.assertEqual(mascara.name, "NOMBRE_L")
        self.assertEqual(mascara.tolist(), [False, True, True, True, False])
        self.assertEqual(mascara.dtype, bool)

    def test_mascara_acepta_serie_vacia(self):
        programas = pd.Series([], dtype=object, index=pd.Index([], name="idx"), name="CARRERA")
        mascara = mascara_programas_excluidos(programas)

        self.assertEqual(mascara.index.tolist(), [])
        self.assertEqual(mascara.name, "CARRERA")
        self.assertEqual(len(mascara), 0)
        self.assertEqual(mascara.dtype, bool)

    def test_mascara_funciona_con_columna_alternativa(self):
        programas = pd.Series(
            ["Diplomado en Gestión", "Técnico en Enfermería"],
            index=[101, 205],
            name="CARRERA",
        )
        mascara = mascara_programas_excluidos(programas)

        self.assertEqual(mascara.index.tolist(), [101, 205])
        self.assertEqual(mascara.name, "CARRERA")
        self.assertEqual(mascara.tolist(), [True, False])

    def test_tipos_excluidos_vacio_equivale_a_exclusion_desactivada(self):
        programas = pd.Series(
            ["Diplomado en Gestión", "Postítulo en Docencia", "Programa especial"],
            index=[3, 7, 9],
        )
        mascara = mascara_programas_excluidos(
            programas,
            catalogo_exclusion=["Programa especial"],
            tipos_excluidos=[],
        )

        self.assertEqual(mascara.tolist(), [False, False, False])
        self.assertEqual(mascara.index.tolist(), [3, 7, 9])

    def test_teiq_no_es_diplomado_ni_postitulo(self):
        programas = pd.Series(
            ["TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA"],
            index=[17676747],
            name="NOMBRE_L",
        )
        mascara = mascara_programas_excluidos(programas)

        self.assertEqual(mascara.tolist(), [False])

    def test_mascara_exige_serie_para_no_perder_alineacion(self):
        with self.assertRaisesRegex(TypeError, "pandas.Series"):
            mascara_programas_excluidos(["DIPLOMADO"])  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
