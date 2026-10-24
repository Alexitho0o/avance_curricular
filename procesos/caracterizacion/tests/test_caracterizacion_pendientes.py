from __future__ import annotations

import unittest

import pandas as pd

from caracterizacion_pendientes import (
    normalizar_estado_respuesta,
    seleccionar_pendientes_encuesta,
)


class PendientesEncuestaTests(unittest.TestCase):
    def test_conserva_si_no_e_incompleto(self):
        df = pd.DataFrame({"Responden": ["SI", "NO", "INCOMPLETO"], "id": [1, 2, 3]})

        out = seleccionar_pendientes_encuesta(df)

        self.assertEqual(out["id"].tolist(), [1, 2, 3])

    def test_cinco_vigentes_conserva_los_cinco(self):
        df = pd.DataFrame(
            {
                "Responden": ["SI", "SI", "INCOMPLETO", "NO", "NO"],
                "_token_match": ["1", "2", "3", "4", "5"],
            }
        )

        out, auditoria = seleccionar_pendientes_encuesta(
            df,
            columna_llave="_token_match",
            devolver_auditoria=True,
        )

        self.assertEqual(len(out), 5)
        self.assertEqual(out["_token_match"].tolist(), ["1", "2", "3", "4", "5"])
        self.assertEqual(auditoria["VIGENTES_ELEGIBLES"], 5)
        self.assertEqual(auditoria["RESPUESTAS_COMPLETAS"], 2)
        self.assertEqual(auditoria["RESPUESTAS_INCOMPLETAS"], 1)
        self.assertEqual(auditoria["SIN_RESPUESTA"], 2)
        self.assertEqual(auditoria["PENDIENTES_EXPORTADOS"], 5)

    def test_conserva_columna_responden_sin_modificar_clasificacion(self):
        df = pd.DataFrame(
            {
                "Responden": [" Sí ", "si", "SI", "NO", "INCOMPLETO"],
                "id": [1, 2, 3, 4, 5],
            }
        )

        out = seleccionar_pendientes_encuesta(df)

        self.assertEqual(
            out["Responden"].tolist(),
            [" Sí ", "si", "SI", "NO", "INCOMPLETO"],
        )
        self.assertEqual(normalizar_estado_respuesta(" Sí "), "SI")

    def test_no_modifica_dataframe_original(self):
        df = pd.DataFrame({"Responden": ["SI", "NO"], "id": [1, 2]})
        original = df.copy(deep=True)

        out = seleccionar_pendientes_encuesta(df)
        out.loc[out.index[0], "id"] = 999

        pd.testing.assert_frame_equal(df, original)

    def test_ningun_vigente_desaparece_de_estudiantes_pendientes(self):
        df = pd.DataFrame(
            {
                "Responden": ["SI", "NO", "", None, float("nan"), "DESCONOCIDO"],
                "id": [1, 2, 3, 4, 5, 6],
            }
        )

        out = seleccionar_pendientes_encuesta(df)

        self.assertEqual(out["id"].tolist(), df["id"].tolist())


if __name__ == "__main__":
    unittest.main()
