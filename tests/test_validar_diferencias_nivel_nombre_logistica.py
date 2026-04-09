import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts/validar_diferencias_nivel_nombre_logistica.py"
BASE = (
    REPO
    / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "AUDITORIA_MALLAS_COMPARTIDAS_END_TO_END_20260701_090314"
)


def load_module():
    spec = importlib.util.spec_from_file_location("validar_diferencias", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestValidarDiferenciasNivelNombreLogistica(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()
        cls.planes = cls.mod.Planes("TLOG20241", "ILOG20241", "CILOG20241")
        cls.tlog, cls.ilog, cls.cilog, cls.fuentes = cls.mod.cargar_tablas(BASE, cls.planes)
        cls.control, cls.observed = cls.mod.control_totales(cls.tlog, cls.ilog, cls.cilog)
        cls.outputs = cls.mod.build_outputs(cls.tlog, cls.ilog, cls.cilog, cls.fuentes)

    def test_01_reproduccion_totales(self):
        self.assertEqual(self.observed["TLOG_TOTAL"], 26)
        self.assertEqual(self.observed["ILOG_TOTAL"], 30)
        self.assertEqual(self.observed["CILOG_TOTAL"], 17)

    def test_02_conteo_solo_tlog(self):
        self.assertEqual(len(self.outputs["solo_tlog"]), 2)

    def test_03_conteo_solo_ilog(self):
        self.assertEqual(len(self.outputs["solo_ilog"]), 6)

    def test_04_conteo_ilog_cubiertas_por_cilog(self):
        self.assertEqual(len(self.outputs["cubiertas"]), 5)

    def test_05_conteo_ilog_no_cubierta(self):
        self.assertEqual(len(self.outputs["no_cubierta"]), 1)

    def test_06_conteo_solo_cilog(self):
        self.assertEqual(len(self.outputs["solo_cilog"]), 12)

    def test_07_preservacion_niveles(self):
        solo_tlog_levels = set(self.outputs["solo_tlog"]["NIVEL_ORIGINAL"])
        self.assertEqual(solo_tlog_levels, {"7"})
        self.assertEqual(set(self.outputs["solo_cilog"]["NIVEL_CILOG_ORIGINAL"]), {"2", "3", "4"})
        self.assertIn("1", set(self.outputs["niveles_cilog"]["NIVEL_ORIGINAL"]))

    def test_08_preservacion_nombres_originales(self):
        names = set(self.outputs["solo_tlog"]["NOMBRE_ASIGNATURA_ORIGINAL"])
        self.assertIn("PRÁCTICA PROFESIONAL", names)
        self.assertIn("TALLER DE INTEGRACIÓN PROFESIONAL", names)

    def test_09_preservacion_codigos(self):
        codes = set(self.outputs["no_cubierta"]["CODIGO_ILOG"])
        self.assertEqual(codes, {"LG312ILOG"})

    def test_10_no_equivalencia_por_nombre_solo(self):
        ilog = self.ilog[self.ilog["CLAVE_ASIGNATURA_CANONICA"] == "TITULO INTERMEDIO"].iloc[0]
        cilog = self.cilog.iloc[0].copy()
        cilog["CLAVE_ASIGNATURA_CANONICA"] = "TITULO INTERMEDIO"
        cilog["CODRAMO_OBSERVADO"] = "ZZ999CILOG"
        cilog["RAMOEQUIV_OBSERVADO"] = "ZZ999ILOG"
        self.assertFalse(self.mod.has_confirmed_relation(ilog, cilog))

    def test_11_mismo_nombre_distinto_nivel(self):
        rel = self.outputs["cubiertas"].set_index("NOMBRE_ILOG")
        self.assertEqual(rel.loc["LOGÍSTICA INTERNACIONAL"]["MISMO_NIVEL_ORIGINAL"], "NO")

    def test_12_cilog_separado_de_ilog(self):
        self.assertEqual(set(self.cilog["PLAN_DE_ESTUDIO"]), {"CILOG20241"})
        self.assertEqual(set(self.ilog["PLAN_DE_ESTUDIO"]), {"ILOG20241"})

    def test_13_nivel_relativo_no_convertido_automaticamente(self):
        levels = self.outputs["niveles_cilog"]
        self.assertIn("NIVEL_RELATIVO_CONTINUIDAD", set(levels["ESTADO"]))

    def test_14_tabla_nivel_por_nivel(self):
        niveles = set(self.outputs["nivel_por_nivel"]["NIVEL"])
        self.assertTrue({"1", "2", "3", "4", "5", "6", "7", "9"} <= niveles)

    def test_15_excel_generado(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "validacion.xlsx"
            self.mod.escribir_excel(path, self.outputs)
            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 0)

    def test_16_fuente_original_intacta(self):
        before = self.mod.sha256(Path(self.fuentes["TLOG"]))
        _ = self.mod.build_outputs(self.tlog, self.ilog, self.cilog, self.fuentes)
        after = self.mod.sha256(Path(self.fuentes["TLOG"]))
        self.assertEqual(before, after)

    def test_17_paquete_manual_intacto(self):
        manual = self.mod.MANUAL_EXCEL
        if manual.exists():
            before = self.mod.sha256(manual)
            _ = self.mod.build_outputs(self.tlog, self.ilog, self.cilog, self.fuentes)
            after = self.mod.sha256(manual)
            self.assertEqual(before, after)

    def test_18_conclusion_consistente(self):
        conclusion = self.outputs["conclusion"].iloc[-1]["RESPUESTA"]
        self.assertEqual(conclusion, "DIFERENCIAS_PRINCIPALMENTE_FINALES_CON_EXCEPCIONES")


if __name__ == "__main__":
    unittest.main()
