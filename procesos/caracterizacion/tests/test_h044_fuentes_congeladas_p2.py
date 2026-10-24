#!/usr/bin/env python3
"""
H044 — Pruebas de la resolución gobernada de fuentes congeladas 2026 P2.

Estas pruebas:
- no usan datos institucionales ni personales reales;
- usan archivos sintéticos temporales y un manifiesto sintético;
- no ejecutan el pipeline de caracterización;
- no escriben en el repositorio (todo ocurre en tempfile.TemporaryDirectory).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "gobernanza" / "resolver_fuentes_congeladas_2026_p2.py"
LAUNCHER_PATH = ROOT / "procesar_financiamiento_diario.sh"

SPEC = importlib.util.spec_from_file_location(
    "resolver_fuentes_congeladas_2026_p2", MODULE_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"No fue posible cargar el módulo: {MODULE_PATH}")
resolver_mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = resolver_mod
SPEC.loader.exec_module(resolver_mod)

FuentesCongeladasError = resolver_mod.FuentesCongeladasError
resolver_fuentes_congeladas = resolver_mod.resolver_fuentes_congeladas


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FixtureFuentesCongeladas:
    """Construye un repo sintético mínimo con manifiesto + cuaterna congelada."""

    def __init__(self, tmp_path: Path):
        self.repo_root = tmp_path
        self.version = "2026_P2_20260721_161905"
        self.rel_dir = Path(".local/fuentes_congeladas/2026/P2") / self.version
        self.dir_abs = self.repo_root / self.rel_dir
        self.dir_abs.mkdir(parents=True)

        self.nombre_matricula = "DATOSDEALUMNOS_10246.xlsx"
        self.nombre_tokens = "tokens_443299.csv"
        self.nombre_resultados = "results-survey443299.xlsx"
        self.nombre_promedios = "PROMEDIOSDEALUMNOS_7804.xlsx"

        self.bytes_matricula = b"contenido sintetico matricula"
        self.bytes_tokens = b"contenido sintetico tokens"
        self.bytes_resultados = b"contenido sintetico resultados"
        self.bytes_promedios = b"contenido sintetico promedios academicos"

        (self.dir_abs / self.nombre_matricula).write_bytes(self.bytes_matricula)
        (self.dir_abs / self.nombre_tokens).write_bytes(self.bytes_tokens)
        (self.dir_abs / self.nombre_resultados).write_bytes(self.bytes_resultados)
        (self.dir_abs / self.nombre_promedios).write_bytes(self.bytes_promedios)

        self.manifest_dir = self.repo_root / "docs" / "gobernanza"
        self.manifest_dir.mkdir(parents=True)
        self.manifest_path = self.manifest_dir / "FUENTES_CONGELADAS_2026_P2.json"
        self._write_manifest()

    def _archivo_entry(self, rol, nombre, ruta_rel, contenido, survey_id=None):
        entry = {
            "rol": rol,
            "nombre": nombre,
            "ruta_relativa_restringida": str(ruta_rel).replace("\\", "/"),
            "sha256": _sha256_bytes(contenido),
        }
        if survey_id is not None:
            entry["survey_id"] = survey_id
        return entry

    def _write_manifest(
        self,
        *,
        anio=2026,
        periodo=2,
        estado="CONGELADO",
        survey_id="443299",
        tokens_survey_id="443299",
        resultados_survey_id="443299",
        omitir_rol=None,
        sha_matricula=None,
        sha_tokens=None,
        sha_resultados=None,
        sha_promedios=None,
    ):
        archivos = []
        entry_m = self._archivo_entry(
            "matricula_oficial",
            self.nombre_matricula,
            self.rel_dir / self.nombre_matricula,
            self.bytes_matricula,
        )
        if sha_matricula is not None:
            entry_m["sha256"] = sha_matricula
        entry_t = self._archivo_entry(
            "inscritos_limesurvey",
            self.nombre_tokens,
            self.rel_dir / self.nombre_tokens,
            self.bytes_tokens,
            survey_id=tokens_survey_id,
        )
        if sha_tokens is not None:
            entry_t["sha256"] = sha_tokens
        entry_r = self._archivo_entry(
            "resultados_limesurvey",
            self.nombre_resultados,
            self.rel_dir / self.nombre_resultados,
            self.bytes_resultados,
            survey_id=resultados_survey_id,
        )
        if sha_resultados is not None:
            entry_r["sha256"] = sha_resultados

        entry_p = self._archivo_entry(
            "promedios_academicos_auxiliar",
            self.nombre_promedios,
            self.rel_dir / self.nombre_promedios,
            self.bytes_promedios,
        )
        if sha_promedios is not None:
            entry_p["sha256"] = sha_promedios

        for rol, entry in (
            ("matricula_oficial", entry_m),
            ("inscritos_limesurvey", entry_t),
            ("resultados_limesurvey", entry_r),
            ("promedios_academicos_auxiliar", entry_p),
        ):
            if rol != omitir_rol:
                archivos.append(entry)

        manifest = {
            "anio": anio,
            "periodo": periodo,
            "version_fuentes": self.version,
            "estado": estado,
            "survey_id": survey_id,
            "archivos": archivos,
        }
        self.manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def resolver(self, *, anio=2026, periodo=2, entorno=None):
        return resolver_fuentes_congeladas(
            self.manifest_path,
            self.repo_root,
            anio,
            periodo,
            entorno=entorno or {},
        )


class ResolucionFuentesCongeladasTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    # 1. Manifiesto valido + cuatro archivos + hashes correctos -> resolucion OK.
    def test_01_manifiesto_valido_resuelve_ok(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        resolucion = fx.resolver()
        self.assertEqual(resolucion.survey_id, "443299")
        self.assertEqual(resolucion.version_fuentes, fx.version)
        self.assertEqual(
            resolucion.rutas_por_rol["matricula_oficial"].name, fx.nombre_matricula
        )
        self.assertEqual(resolucion.rutas_por_rol["inscritos_limesurvey"].name, fx.nombre_tokens)
        self.assertEqual(
            resolucion.rutas_por_rol["resultados_limesurvey"].name, fx.nombre_resultados
        )
        self.assertEqual(
            resolucion.rutas_por_rol["promedios_academicos_auxiliar"].name,
            fx.nombre_promedios,
        )
        self.assertTrue(all(resolucion.exportar_por_rol.values()))
        self.assertTrue(
            any("RUTA_PROMEDIOS=" in linea for linea in resolucion.lineas_export())
        )
        self.assertIn(
            "[H044][FUENTES] Promedios académicos: PROMEDIOSDEALUMNOS_7804.xlsx",
            resolucion.trace_lines,
        )
        self.assertIn("[H044][FUENTES] SHA-256: OK", resolucion.trace_lines)
        self.assertIn("[H044][FUENTES] Downloads utilizados: NO", resolucion.trace_lines)

    # 2. Falta matricula -> bloqueo.
    def test_02_falta_matricula_bloquea(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        (fx.dir_abs / fx.nombre_matricula).unlink()
        with self.assertRaises(FuentesCongeladasError):
            fx.resolver()

    # 3. Falta tokens -> bloqueo.
    def test_03_falta_tokens_bloquea(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        (fx.dir_abs / fx.nombre_tokens).unlink()
        with self.assertRaises(FuentesCongeladasError):
            fx.resolver()

    # 4. Falta resultados -> bloqueo.
    def test_04_falta_resultados_bloquea(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        (fx.dir_abs / fx.nombre_resultados).unlink()
        with self.assertRaises(FuentesCongeladasError):
            fx.resolver()

    # 4B. Falta promedios académicos -> bloqueo.
    def test_04b_falta_promedios_bloquea(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        (fx.dir_abs / fx.nombre_promedios).unlink()
        with self.assertRaises(FuentesCongeladasError):
            fx.resolver()

    # 5. Hash de matricula alterado -> bloqueo.
    def test_05_hash_matricula_alterado_bloquea(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        fx._write_manifest(sha_matricula="0" * 64)
        with self.assertRaisesRegex(FuentesCongeladasError, "SHA-256"):
            fx.resolver()

    # 6. Hash de tokens alterado -> bloqueo.
    def test_06_hash_tokens_alterado_bloquea(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        fx._write_manifest(sha_tokens="0" * 64)
        with self.assertRaisesRegex(FuentesCongeladasError, "SHA-256"):
            fx.resolver()

    # 7. Hash de resultados alterado -> bloqueo.
    def test_07_hash_resultados_alterado_bloquea(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        fx._write_manifest(sha_resultados="0" * 64)
        with self.assertRaisesRegex(FuentesCongeladasError, "SHA-256"):
            fx.resolver()

    # 7B. Hash de promedios académicos alterado -> bloqueo.
    def test_07b_hash_promedios_alterado_bloquea(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        fx._write_manifest(sha_promedios="0" * 64)
        with self.assertRaisesRegex(FuentesCongeladasError, "SHA-256"):
            fx.resolver()

    # 8. Manifiesto con anio distinto -> bloqueo.
    def test_08_anio_distinto_bloquea(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        fx._write_manifest(anio=2025)
        with self.assertRaisesRegex(FuentesCongeladasError, "[Aa].o"):
            fx.resolver()

    # 9. Manifiesto con periodo distinto -> bloqueo.
    def test_09_periodo_distinto_bloquea(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        fx._write_manifest(periodo=1)
        with self.assertRaisesRegex(FuentesCongeladasError, "Periodo"):
            fx.resolver()

    # 10. Manifiesto no congelado -> bloqueo.
    def test_10_no_congelado_bloquea(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        fx._write_manifest(estado="BORRADOR")
        with self.assertRaisesRegex(FuentesCongeladasError, "CONGELADO"):
            fx.resolver()

    # 11. Survey ID de tokens/resultados inconsistente -> bloqueo.
    def test_11_survey_id_inconsistente_bloquea(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        fx._write_manifest(tokens_survey_id="999999")
        with self.assertRaisesRegex(FuentesCongeladasError, "survey_id"):
            fx.resolver()

    # 12/13. Ejecucion 2026 P1 y 2026 P3 mantienen comportamiento historico:
    # el lanzador solo activa la resolucion gobernada cuando ANIO=2026 y
    # PERIODO=2 (el guard se extrae y se prueba contra el propio archivo).
    def test_12_13_guard_launcher_solo_activa_para_2026_p2(self):
        contenido = LAUNCHER_PATH.read_text(encoding="utf-8")
        match = re.search(
            r'if \[\[ "\$ANIO" == "([^"]+)" && "\$PERIODO" == "([^"]+)" \]\]; then\n'
            r"\s*RESOLVER_FUENTES_P2=",
            contenido,
        )
        self.assertIsNotNone(
            match, "No se encontro el guard de activacion de fuentes congeladas en el lanzador."
        )
        anio_guard, periodo_guard = match.group(1), match.group(2)
        self.assertEqual(anio_guard, "2026")
        self.assertEqual(periodo_guard, "2")

        for anio, periodo, activa in (
            ("2026", "2", True),
            ("2026", "1", False),
            ("2026", "3", False),
            ("2025", "2", False),
        ):
            script = (
                f'ANIO="{anio}"; PERIODO="{periodo}"; '
                f'if [[ "$ANIO" == "{anio_guard}" && "$PERIODO" == "{periodo_guard}" ]]; then '
                'echo ACTIVADO; else echo NO_ACTIVADO; fi'
            )
            res = subprocess.run(
                ["bash", "-c", script], capture_output=True, text=True, check=True
            )
            esperado = "ACTIVADO" if activa else "NO_ACTIVADO"
            self.assertEqual(res.stdout.strip(), esperado, f"anio={anio} periodo={periodo}")

        # La linea de invocacion del pipeline python fuera del bloque de
        # fuentes congeladas permanece con las mismas variables historicas.
        self.assertIn("SOLO_GENERAR_FCU=0", contenido)
        self.assertIn("CARACTERIZACION_SKIP_FCU=1", contenido)
        self.assertIn("CARACTERIZACION_STOP_AFTER_FINANCIAMIENTO=1", contenido)
        self.assertIn('PIPELINE_SCRIPT="caracterizacion.py"', contenido)
        self.assertIn('"$PYTHON_BIN" "$PIPELINE_SCRIPT"', contenido)

    # 14. Variable de ruta explicita valida: prevalece sobre el manifiesto
    # para ese rol especifico (decision gobernada y documentada), y no
    # bloquea la validacion de los demas roles.
    def test_14_override_manual_prevalece_por_rol(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        override_path = "/ruta/manual/DATOSDEALUMNOS_override.xlsx"
        resolucion = fx.resolver(entorno={"RUTA_MATRICULA": override_path})
        self.assertFalse(resolucion.exportar_por_rol["matricula_oficial"])
        self.assertTrue(resolucion.exportar_por_rol["inscritos_limesurvey"])
        self.assertTrue(resolucion.exportar_por_rol["resultados_limesurvey"])
        self.assertTrue(
            resolucion.exportar_por_rol["promedios_academicos_auxiliar"]
        )
        lineas_export = resolucion.lineas_export()
        self.assertFalse(any("RUTA_MATRICULA=" in l for l in lineas_export))
        self.assertTrue(any("RUTA_INSCRITOS=" in l for l in lineas_export))
        self.assertTrue(any("RUTA_RESULTADOS=" in l for l in lineas_export))
        self.assertTrue(any("RUTA_PROMEDIOS=" in l for l in lineas_export))
        self.assertTrue(
            any("OVERRIDE_MANUAL" in l and "Matr" in l for l in resolucion.trace_lines)
        )

    # 15. Archivos 967488 presentes en "Downloads" para 2026 P2: ignorados.
    def test_15_archivos_recientes_en_downloads_son_ignorados(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        downloads = self.tmp_path / "Downloads"
        downloads.mkdir()
        (downloads / "tokens_967488.csv").write_bytes(b"debe ser ignorado")
        (downloads / "results-survey967488.xlsx").write_bytes(b"debe ser ignorado")
        (downloads / "PROMEDIOSDEALUMNOS_999999.xlsx").write_bytes(
            b"debe ser ignorado"
        )
        resolucion = fx.resolver()
        self.assertEqual(resolucion.rutas_por_rol["inscritos_limesurvey"].name, fx.nombre_tokens)
        self.assertEqual(
            resolucion.rutas_por_rol["resultados_limesurvey"].name, fx.nombre_resultados
        )
        self.assertEqual(
            resolucion.rutas_por_rol["promedios_academicos_auxiliar"].name,
            fx.nombre_promedios,
        )
        for path in resolucion.rutas_por_rol.values():
            self.assertNotIn("967488", path.name)
            self.assertNotIn(str(downloads), str(path))

    # Control adicional: override manual de promedios prevalece solo para ese rol.
    def test_override_manual_promedios_prevalece_por_rol(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        override_path = "/ruta/manual/PROMEDIOSDEALUMNOS_override.xlsx"
        resolucion = fx.resolver(entorno={"RUTA_PROMEDIOS": override_path})

        self.assertFalse(
            resolucion.exportar_por_rol["promedios_academicos_auxiliar"]
        )
        self.assertTrue(resolucion.exportar_por_rol["matricula_oficial"])
        self.assertTrue(resolucion.exportar_por_rol["inscritos_limesurvey"])
        self.assertTrue(resolucion.exportar_por_rol["resultados_limesurvey"])

        lineas_export = resolucion.lineas_export()
        self.assertFalse(any("RUTA_PROMEDIOS=" in linea for linea in lineas_export))
        self.assertTrue(any("RUTA_MATRICULA=" in linea for linea in lineas_export))
        self.assertTrue(any("RUTA_INSCRITOS=" in linea for linea in lineas_export))
        self.assertTrue(any("RUTA_RESULTADOS=" in linea for linea in lineas_export))
        self.assertTrue(
            any(
                "OVERRIDE_MANUAL" in linea and "Promedios académicos" in linea
                for linea in resolucion.trace_lines
            )
        )

    # Control adicional: ruta que intenta escapar de .local/fuentes_congeladas/.
    def test_ruta_fuera_de_zona_restringida_bloquea(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        manifest = json.loads(fx.manifest_path.read_text(encoding="utf-8"))
        fuera_dir = fx.repo_root / "fuera_de_zona"
        fuera_dir.mkdir()
        archivo_fuera = fuera_dir / fx.nombre_matricula
        archivo_fuera.write_bytes(fx.bytes_matricula)
        for entrada in manifest["archivos"]:
            if entrada["rol"] == "matricula_oficial":
                entrada["ruta_relativa_restringida"] = "fuera_de_zona/" + fx.nombre_matricula
        fx.manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        with self.assertRaisesRegex(FuentesCongeladasError, "fuentes_congeladas"):
            fx.resolver()

    # Control adicional: rol faltante por completo en la lista de archivos.
    def test_rol_faltante_en_manifiesto_bloquea(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        fx._write_manifest(omitir_rol="resultados_limesurvey")
        with self.assertRaisesRegex(FuentesCongeladasError, "resultados_limesurvey"):
            fx.resolver()

    def test_rol_promedios_faltante_en_manifiesto_bloquea(self):
        fx = FixtureFuentesCongeladas(self.tmp_path)
        fx._write_manifest(omitir_rol="promedios_academicos_auxiliar")
        with self.assertRaisesRegex(
            FuentesCongeladasError,
            "promedios_academicos_auxiliar",
        ):
            fx.resolver()


if __name__ == "__main__":
    unittest.main()
