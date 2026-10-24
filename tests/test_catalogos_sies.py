"""Controles aislados de catalogos; nunca importa el motor MU2026."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from common.catalogos_sies import (cargar_catalogo, componentes, escribir_inmutables,
                                   json_bytes, resolver, resolver_catalogo, sha256,
                                   verificar_fuente)
from scripts.generar_catalogos_sies_por_anio import (ROOT, aplicar_equivalencias,
                                                    construir, construir_oferta)


SOURCE = {"path": "fuente.tsv", "sha256": "prueba"}


def fuente(year=2026, sede="2", jornada="4", version="1", alias="TEST", **updates):
    row = {"CODIGO_IES_NUM": "162", "COD_SEDE": sede, "NOMBRE_SEDE": "Sede prueba",
           "NOMBRE_CARRERA": "Carrera prueba", "MODALIDAD": "3",
           "DURACION_ESTUDIOS": "8", "DURACION_TOTAL": "9"}
    if year == 2026:
        row.update(CODIGO_UNICO=f"I162S{sede}C99J{jornada}V{version}", JORNADA=jornada,
                   CODIGO_CARRERA="99", TIPO_PLAN_CARRERA="1", VIGENCIA="1",
                   CODCARPR_CANONICO=alias, CODCARPR_ALIAS_LIST="")
    else:
        row.update(COD_JORNADA=jornada, COD_CARRERA="99", VERSION=version,
                   COD_TIPO_PLAN_CARRERA="1", VIGENCIA_CARRERA="1")
    return dict(row, **updates)


def catalogo(*rows, year=2026):
    return {"anio": year, "version": "prueba", "fuente": SOURCE,
            "sedes_internas": {"RE": "2", "CO": "3", **({"PTG": "4"} if year == 2027 else {})},
            "oferta": list(construir_oferta(list(rows), year, SOURCE).values())}


class CatalogosTest(unittest.TestCase):
    def test_cruce_exige_sede_y_jornada(self):
        for kwargs in ({"codcarpr": "TEST"}, {"codcarpr": "TEST", "sede": "RE"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                resolver_catalogo(catalogo(fuente()), **kwargs)

    def test_no_cruza_sedes(self):
        cat = catalogo(fuente(), fuente(sede="3", MODALIDAD="1"))
        result = resolver_catalogo(cat, codcarpr=" test ", sede="CO", jornada="O")
        self.assertEqual(result["codigo_unico"], "I162S3C99J4V1")
        self.assertEqual(result["modalidad"], "Presencial")

    def test_no_elige_version_maxima(self):
        cat = catalogo(fuente(), fuente(version="2"))
        result = resolver_catalogo(cat, codcarpr="TEST", sede="RE", jornada="O")
        self.assertEqual(result["estado"], "AMBIGUO")
        self.assertEqual(result["codigo_unico"], "")
        self.assertEqual(result["modalidad"], "No determinada")
        explicit = resolver_catalogo(cat, codcarpr="TEST", sede="RE", jornada="O", version="1")
        self.assertEqual(explicit["codigo_unico"], "I162S2C99J4V1")

    def test_no_confunde_jornada_3_y_4(self):
        cat = catalogo(fuente(), fuente(jornada="3", MODALIDAD="2"))
        self.assertEqual(resolver_catalogo(cat, codcarpr="TEST", sede="RE", jornada="O")["modalidad"], "No presencial")
        self.assertEqual(resolver_catalogo(cat, codcarpr="TEST", sede="RE", jornada="3")["modalidad"], "Semipresencial")

    def test_nombre_restringe_sin_similitud(self):
        cat = catalogo(fuente(), fuente(version="2", NOMBRE_CARRERA="Continuidad prueba"))
        result = resolver_catalogo(cat, codcarpr="TEST", sede="RE", jornada="O", nombre="Carrera prueba")
        self.assertEqual(result["codigo_unico"], "I162S2C99J4V1")
        self.assertEqual(resolver_catalogo(cat, codcarpr="TEST", sede="RE", jornada="O", nombre="Carrera")["estado"], "SIN_EQUIVALENCIA")

    def test_codigo_directo_sin_alias_y_patagonia(self):
        cat = catalogo(fuente(2027, sede="4"), year=2027)
        result = resolver_catalogo(cat, codigo_unico="I162S4C99J4V1", sede="PTG")
        self.assertEqual(result["estado"], "RESUELTO")
        self.assertEqual(result["equivalencias"], [])
        self.assertEqual(resolver_catalogo(cat, codcarpr="TEST", sede="PTG", jornada="O")["estado"], "SIN_EQUIVALENCIA")

    def test_codigo_y_dimension_contradictoria(self):
        self.assertEqual(resolver_catalogo(catalogo(fuente()), codigo_unico="I162S2C99J4V1", sede="CO")["estado"], "SIN_EQUIVALENCIA")

    def test_codigo_o_carrera_exclusivos(self):
        for kwargs in ({}, {"codigo_unico": "I162S2C99J4V1", "codcarpr": "TEST"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                resolver_catalogo(catalogo(fuente()), **kwargs)

    def test_codigo_malformado_o_otra_ies(self):
        for code in ("162", "I99S2C99J4V1", "I162S2C99J4V1extra"):
            with self.subTest(code=code), self.assertRaises(ValueError):
                componentes(code)

    def test_duplicados_2026_conservan_alias_nombres_y_filas(self):
        offer = construir_oferta([fuente(), fuente(alias="CONT", NOMBRE_CARRERA="Continuidad")], 2026, SOURCE)
        row = offer["I162S2C99J4V1"]
        self.assertEqual(row["filas_fuente"], [2, 3])
        self.assertEqual(row["nombres_fuente"], ["Carrera prueba", "Continuidad"])
        self.assertEqual({a["codcarpr"] for a in row["equivalencias"]}, {"TEST", "CONT"})

    def test_conflicto_2026_no_elige_primero(self):
        with self.assertRaises(ValueError):
            construir_oferta([fuente(), fuente(MODALIDAD="2")], 2026, SOURCE)

    def test_duplicado_2027_es_error(self):
        with self.assertRaises(ValueError):
            construir_oferta([fuente(2027), fuente(2027)], 2027, SOURCE)

    def test_ano_no_gobernado_y_dominios_invalidos(self):
        for year, row in [(2028, fuente(2027)), (2026, fuente(MODALIDAD="9")),
                          (2026, fuente(CODIGO_IES_NUM="99")), (2026, fuente(COD_SEDE="3")),
                          (2026, fuente(DURACION_ESTUDIOS=""))]:
            with self.subTest(year=year, row=row), self.assertRaises(ValueError):
                construir_oferta([row], year, SOURCE)

    def test_alias_vacios_no_se_inventan(self):
        row = construir_oferta([fuente(alias="", CODCARPR_ALIAS_LIST="|nan|NONE|null")], 2026, SOURCE)
        self.assertFalse(next(iter(row.values()))["equivalencias"])

    def test_hash_y_salida_de_raiz(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "evidencia.txt"
            p.write_text("fuente", encoding="utf-8")
            self.assertEqual(verificar_fuente(root, {"path": p.name, "sha256": sha256(p)}), p.resolve())
            for path, digest in [(p.name, "incorrecto"), ("../afuera", "irrelevante")]:
                with self.subTest(path=path), self.assertRaises(ValueError):
                    verificar_fuente(root, {"path": path, "sha256": digest})

    def test_equivalencia_manual_exige_evidencia(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            proof = root / "evidencia.txt"
            proof.write_text("TEST corresponde a I162S2C99J4V1", encoding="utf-8")
            entry = {"codigo_unico": "I162S2C99J4V1", "codcarpr": "TEST", "nombre_interno": "Carrera prueba",
                     "evidencia_path": proof.name, "evidencia_sha256": sha256(proof), "localizador": "linea 1"}
            offer = construir_oferta([fuente(2027)], 2027, SOURCE)
            doc = {"anio": 2027, "schema_version": 1, "equivalencias": [entry]}
            aplicar_equivalencias(offer, doc, root)
            self.assertEqual(offer[entry["codigo_unico"]]["equivalencias"][0]["metodo"], "EQUIVALENCIA_EXPLICITA_2027")
            for change in ({"evidencia_sha256": "mal"}, {"localizador": ""}, {"codigo_unico": "I162S2C999J4V1"}):
                with self.subTest(change=change), self.assertRaises(ValueError):
                    aplicar_equivalencias(copy.deepcopy(offer), dict(doc, equivalencias=[dict(entry, **change)]), root)
            with self.assertRaises(ValueError):
                aplicar_equivalencias(offer, dict(doc, anio=2026), root)
            with self.assertRaises(ValueError):
                aplicar_equivalencias(offer, dict(doc, equivalencias=[entry, entry]), root)

    def test_inmutabilidad_y_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old, new = root / "old", root / "new"
            escribir_inmutables({old: b"original"})
            escribir_inmutables({old: b"original"})
            with self.assertRaises(ValueError):
                escribir_inmutables({new: b"nuevo", old: b"cambio"})
            self.assertFalse(new.exists())
            self.assertEqual(old.read_bytes(), b"original")

    def test_carga_anual_no_fallback_y_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cat = root / "2026.json"
            cat.write_bytes(json_bytes(catalogo(fuente())))
            reg = {"catalogos": {"2026": {"path": cat.name, "sha256": sha256(cat)}}}
            (root / "REGISTRO.json").write_bytes(json_bytes(reg))
            self.assertEqual(cargar_catalogo(2026, root)["anio"], 2026)
            with self.assertRaises(ValueError):
                resolver(2027, directory=root, codigo_unico="I162S2C99J4V1")
            cat.write_bytes(b"{}")
            with self.assertRaises(ValueError):
                cargar_catalogo(2026, root)

    def test_snapshot_ano_erroneo_y_duplicados(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for cat in (dict(catalogo(fuente()), anio=2027), catalogo(fuente())):
                if cat["anio"] == 2026:
                    cat["oferta"] *= 2
                path = root / "catalogo.json"
                path.write_bytes(json_bytes(cat))
                (root / "REGISTRO.json").write_bytes(json_bytes({"catalogos": {"2026": {"path": path.name, "sha256": sha256(path)}}}))
                with self.assertRaises(ValueError):
                    cargar_catalogo(2026, root)


class FuentesGobernadasTest(unittest.TestCase):
    def test_materializacion_real_aislada_sin_motor(self):
        contract = json.loads((ROOT / "data/catalogos_sies/fuentes.json").read_text(encoding="utf-8"))
        required = [contract["2026"]["path"], contract["2027"]["path"], *contract["referencias_2026"]]
        if any(not (ROOT / path).is_file() for path in required):
            self.skipTest("Regeneracion requiere fuentes originales locales indicadas en fuentes.json")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = construir(output=root)
            self.assertEqual(report["codigos_2027"], 140)
            self.assertEqual(report["codigos_comunes_2026_2027"], 103)
            self.assertEqual(len(report["codigos_nuevos_2027"]), 37)
            self.assertEqual(len(report["pendientes_equivalencia"]), 52)
            self.assertEqual(report["pendientes_por_origen"], {"CODIGO_NUEVO_2027": 37, "SIN_EQUIVALENCIA_DESDE_2026": 15})
            self.assertEqual(len(report["codigos_2026_ausentes_2027_no_eliminar_historicos"]), 34)
            first = {str(p): sha256(p) for p in root.rglob("*.json")}
            construir(output=root)
            self.assertEqual(first, {str(p): sha256(p) for p in root.rglob("*.json")})
            old, new = cargar_catalogo(2026, root), cargar_catalogo(2027, root)
            self.assertEqual(new["resumen"]["con_equivalencia"], 88)
            for row in new["oferta"]:
                if row["codigo_unico"] in report["codigos_nuevos_2027"]:
                    self.assertEqual(row["equivalencias"], [])
                    self.assertEqual(resolver_catalogo(old, codigo_unico=row["codigo_unico"])["estado"], "SIN_EQUIVALENCIA")
                self.assertEqual(resolver_catalogo(new, codigo_unico=row["codigo_unico"])["estado"], "RESUELTO")
            for path, digest in report["referencias_2026_verificadas"].items():
                self.assertEqual(sha256(ROOT / path), digest)

    def test_snapshots_consultables_sin_fuentes_originales(self):
        old, new = cargar_catalogo(2026), cargar_catalogo(2027)
        self.assertEqual(old["resumen"]["codigos"], 137)
        self.assertEqual(new["resumen"]["codigos"], 140)
        self.assertEqual(new["resumen"]["con_equivalencia"], 105)
        self.assertEqual(new["resumen"]["sin_equivalencia"], 35)
        initial = json.loads((ROOT / "data/catalogos_sies/2027/5910_20260907/catalogo.json").read_text())
        self.assertEqual(initial["resumen"]["sin_equivalencia"], 52)
        self.assertFalse(new["habilita_carga_mu"])


if __name__ == "__main__":
    unittest.main()
