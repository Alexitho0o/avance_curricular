from __future__ import annotations

import os
import json
import subprocess
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

import caracterizacion_runtime as rt


class RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.desktop_path = self.tmp_path / "Desktop"
        self.env_patch = patch.dict(
            os.environ,
            {
                "CARACTERIZACION_ARCHIVO_BASE": str(self.tmp_path),
                "CARACTERIZACION_DESKTOP_BASE": str(self.desktop_path),
            },
            clear=False,
        )
        self.env_patch.start()
        self.old_ctx = rt.ACTIVE_CONTEXT
        rt.ACTIVE_CONTEXT = None

    def tearDown(self) -> None:
        ctx = rt.ACTIVE_CONTEXT
        if ctx is not None and not ctx._finalized:
            rt.finalize({})
        rt.ACTIVE_CONTEXT = self.old_ctx
        self.env_patch.stop()
        self.tmp.cleanup()

    def ctx(self, *, external_tee: bool = True):
        return rt.prepare_run_context(2026, 2, external_tee=external_tee)

    def test_crea_carpeta_diaria(self):
        ctx = self.ctx()
        self.assertEqual(ctx.run_dir.parent.name, ctx.inicio.strftime("%Y-%m-%d"))
        self.assertTrue(ctx.input_dir.is_dir())
        self.assertTrue(ctx.output_dir.is_dir())
        self.assertTrue(ctx.log_dir.is_dir())
        self.assertTrue(ctx.audit_dir.is_dir())

    def test_dos_ejecuciones_mismo_dia_crean_carpetas_distintas(self):
        tz = ZoneInfo(rt.TZ_NAME)
        with patch.dict(os.environ, {"CARACTERIZACION_ARCHIVO_BASE": str(self.tmp_path)}, clear=False):
            first = rt.build_run_dir(2026, 2, datetime(2026, 6, 16, 14, 52, 30, tzinfo=tz))
            second = rt.build_run_dir(2026, 2, datetime(2026, 6, 16, 14, 52, 31, tzinfo=tz))
        self.assertNotEqual(first, second)
        self.assertEqual(first.name, "2026_P2_145230")
        self.assertEqual(second.name, "2026_P2_145231")

    def test_copia_integra_entradas_y_sha256(self):
        self.ctx()
        src = self.tmp_path / "Downloads" / "DATOSDEALUMNOS Prueba (á).xlsx"
        src.parent.mkdir()
        src.write_bytes("contenido unicode".encode("utf-8"))
        item = rt.archive_input(src, "matricula")
        archived = Path(item["ruta_archivada"])
        self.assertTrue(archived.exists())
        self.assertEqual(archived.read_bytes(), src.read_bytes())
        self.assertEqual(item["tamano_bytes"], src.stat().st_size)
        self.assertEqual(item["sha256_original"], item["sha256_copia"])
        self.assertEqual(item["sha256_original"], rt.sha256_file(src))

    def test_salida_no_usa_desktop_y_evita_sobrescritura(self):
        ctx = self.ctx()
        first = rt.output_path("reporte.xlsx")
        first.write_text("uno", encoding="utf-8")
        second = rt.output_path("reporte.xlsx")
        self.assertIn(ctx.output_dir.resolve(), first.parents)
        self.assertNotIn("Desktop", str(first))
        self.assertEqual(second.name, "reporte_001.xlsx")

    def test_auditoria_va_a_directorio_auditoria(self):
        ctx = self.ctx()
        path = rt.output_path("AUDITORIA_DE_LOS_CUALES_NUEVOS_2026_P2.xlsx")
        self.assertIn(ctx.audit_dir.resolve(), path.parents)

    def test_crea_log_manifest_y_resumen(self):
        ctx = self.ctx(external_tee=False)
        out = rt.output_path("salida.csv")
        out.write_text("a,b\n1,2\n", encoding="utf-8")
        rt.finalize({"total_si": 3, "total_no": 4})
        self.assertTrue(ctx.log_path.exists())
        self.assertTrue((ctx.audit_dir / "manifest_ejecucion.json").exists())
        resumen = ctx.audit_dir / "RESUMEN_EJECUCION.txt"
        self.assertTrue(resumen.exists())
        self.assertIn("respondieron: 3", resumen.read_text(encoding="utf-8"))

    def test_manifest_incluye_salidas_hash_y_totales(self):
        ctx = self.ctx()
        out = rt.output_path("datos.json")
        out.write_text('{"ok": true}', encoding="utf-8")
        manifest = rt.manifest_dict(ctx, {"n_nuevos": 7})
        self.assertEqual(manifest["zona_horaria"], "America/Santiago")
        self.assertEqual(manifest["totales"]["nuevos_inscritos"], 7)
        self.assertEqual(manifest["salidas"][0]["sha256"], rt.sha256_file(out))

    def test_manejo_entrada_faltante(self):
        self.ctx()
        with self.assertRaises(FileNotFoundError):
            rt.archive_input(self.tmp_path / "Downloads" / "no_existe.xlsx", "matricula")

    def test_pipe_tee_preserva_codigo_python(self):
        log = self.tmp_path / "tee.log"
        script = (
            "set +e; "
            "printf 'x' | python3 -c 'import sys; sys.exit(7)' 2>&1 | tee \"$1\" >/dev/null; "
            "status=${PIPESTATUS[1]}; exit \"$status\""
        )
        res = subprocess.run(["bash", "-c", script, "bash", str(log)], check=False)
        self.assertEqual(res.returncode, 7)
        self.assertTrue(log.exists())

    def test_nombres_unicode_espacios_parentesis(self):
        self.ctx()
        src = self.tmp_path / "Downloads" / "tokens prueba (mañana áéíóú).csv"
        src.parent.mkdir()
        src.write_text("token\n123\n", encoding="utf-8")
        item = rt.archive_input(src, "inscritos_limesurvey")
        self.assertEqual(Path(item["ruta_archivada"]).name, src.name)

    def test_no_modifica_ni_elimina_downloads(self):
        self.ctx()
        src = self.tmp_path / "Downloads" / "results-survey prueba.xlsx"
        src.parent.mkdir()
        src.write_bytes(b"abc")
        before = src.read_bytes()
        rt.archive_input(src, "resultados")
        self.assertTrue(src.exists())
        self.assertEqual(src.read_bytes(), before)

    def test_run_dir_env_se_usa_exactamente(self):
        forced = self.tmp_path / "controlado con espacios"
        with patch.dict(os.environ, {"CARACTERIZACION_RUN_DIR": str(forced)}, clear=False):
            ctx = rt.prepare_run_context(2026, 2, external_tee=True)
        self.assertEqual(ctx.run_dir, forced)
        self.assertTrue((forced / "02_SALIDAS").is_dir())

    def test_copia_escritorio_post_ok_y_sha256(self):
        ctx = self.ctx(external_tee=False)
        out = rt.output_path("salida_controlada.txt")
        out.write_text("contenido final\n", encoding="utf-8")
        rt.finalize({"n_nuevos": 0})

        manifest_path = ctx.audit_dir / "manifest_ejecucion.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        desktop_dir = Path(manifest["directorio_escritorio"])

        self.assertEqual(manifest["copia_escritorio_estado"], "OK")
        self.assertTrue(desktop_dir.is_dir())
        for folder in ("01_ENTRADAS", "02_SALIDAS", "03_LOGS", "04_AUDITORIA"):
            self.assertTrue((desktop_dir / folder).is_dir())

        stats = rt.validate_directory_copy(ctx.run_dir, desktop_dir)
        self.assertGreaterEqual(stats["archivos_verificados"], 3)
        self.assertEqual(
            rt.sha256_file(ctx.output_dir / "salida_controlada.txt"),
            rt.sha256_file(desktop_dir / "02_SALIDAS" / "salida_controlada.txt"),
        )


if __name__ == "__main__":
    unittest.main()
