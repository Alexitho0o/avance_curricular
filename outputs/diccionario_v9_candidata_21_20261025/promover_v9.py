"""Promueve la candidata v9 (21 correspondencias internas V3) a edición activa del diccionario.

Autorización: Alexi, «procede» del 26-10-2026 09:45 (America/Santiago), tras revisar la candidata.
Escribe data/diccionario_sies_seguimiento/v9_20261026_cuatro_planes_v3/ y cambia activo.json.
No modifica v1–v8, bases privadas anteriores, fuentes, Excel ni denominadores. Sin commit/push.
Reversión: restituir activo.json desde ACTIVO_ANTERIOR.json.
"""
import argparse, collections, copy, datetime as dt, json, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from common.diccionario_sies_seguimiento import aplicar_adjudicaciones, sha256  # noqa: E402

PRIV_MAC = Path("/Users/alexi/.local/share/ipss")
V8_DESC_REL = "data/diccionario_sies_seguimiento/v8_20261025_ocho_p/descriptor.json"
V8_DESC_SHA = "701519d757779b3deaa618836bf862df29b9c0ef3e82dc45e5ec9c9b614764ef"
V9_SQL_SHA = "ca1db3627b631f0e"  # prefijo verificado en la candidata
EDICION = "v9_20261026_cuatro_planes_v3"
CARPETA_CAND = "v9_candidata_21_20261025"


def filas(db_path):
    db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    out = [json.loads(p) for (p,) in db.execute("SELECT payload FROM observaciones ORDER BY id")]
    db.close()
    return out


def resumen(rows):
    doc = [r for r in rows if r["codigo_documental_atribuible"]]
    solo_int = [r for r in rows if not r["codigo_documental_atribuible"] and r["codigo_interno_adoptado"]]
    pend_int = [r for r in rows if not r["codigo_documental_atribuible"] and not r["codigo_interno_adoptado"]]
    pend_doc = [r for r in rows if not r["codigo_documental_atribuible"]]
    exc = collections.Counter(r["estado_interno"] for r in pend_int)
    return {
        "universo_observaciones": len(rows),
        "personas": len({r["persona"] for r in rows}),
        "expedientes_carrera_codcli": len({(r["CODCLI"], r["carrera"]) for r in rows}),
        "codigo_documental_reutilizado": len(doc),
        "solo_correspondencia_interna_aprobada": len(solo_int),
        "pendientes_internos": {"observaciones": len(pend_int), "personas": len({r["persona"] for r in pend_int})},
        "pendientes_documentales": {"observaciones": len(pend_doc), "personas": len({r["persona"] for r in pend_doc})},
        "excepciones_por_estado": dict(exc),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--priv-local", type=Path, default=PRIV_MAC, help="ruta local de ~/.local/share/ipss")
    a = ap.parse_args()
    fecha = dt.datetime.now().astimezone().isoformat()
    activo_p = ROOT / "data/diccionario_sies_seguimiento/activo.json"
    activo_antes_txt = activo_p.read_text()
    activo = json.loads(activo_antes_txt)
    if activo != {"descriptor": V8_DESC_REL, "sha256": V8_DESC_SHA} or sha256(ROOT / V8_DESC_REL) != V8_DESC_SHA:
        sys.exit("ALTO: el puntero activo no es v8 verificado.")
    d8 = json.loads((ROOT / V8_DESC_REL).read_text())
    for rel, h in d8["componentes_sha256"].items():
        if sha256(ROOT / rel) != h:
            sys.exit(f"ALTO: componente alterado {rel}")
    v8_local = a.priv_local / Path(d8["base_privada"]["ruta"]).relative_to(PRIV_MAC)
    v9_local = a.priv_local / CARPETA_CAND / "DICCIONARIO_SIES_CANDIDATO_V9.sqlite"
    if sha256(v8_local) != d8["base_privada"]["sha256"]:
        sys.exit("ALTO: base v8 alterada.")
    v9_sha = sha256(v9_local)
    if not v9_sha.startswith(V9_SQL_SHA):
        sys.exit("ALTO: base candidata v9 distinta de la verificada.")
    man_cand = json.loads((Path(__file__).parent / "MANIFEST_CANDIDATA.json").read_text())
    if man_cand["candidata"]["sha256"] != v9_sha or not man_cand["qa"]["todos_ok"]:
        sys.exit("ALTO: manifiesto de candidata no coincide.")

    r8, r9 = filas(v8_local), filas(v9_local)
    s8 = resumen(r8)
    for k in ("universo_observaciones", "personas", "expedientes_carrera_codcli", "codigo_documental_reutilizado",
              "solo_correspondencia_interna_aprobada", "pendientes_internos", "pendientes_documentales", "excepciones_por_estado"):
        if s8[k] != d8["resumen"][k]:
            sys.exit(f"ALTO: definición de resumen no reproduce v8 en {k}: {s8[k]} vs {d8['resumen'][k]}")
    # Operaciones en el formato oficial del módulo y prueba de aplicación sobre v8
    ops = [{"observacion_id": x["observacion_id"], "estado_antes": x, "estado_despues": y}
           for x, y in zip(r8, r9) if x != y]
    aplicado = aplicar_adjudicaciones(r8, ops)
    if aplicado != r9 or len(ops) != 21:
        sys.exit("ALTO: aplicar_adjudicaciones(v8, ops) no reproduce la candidata.")
    ops_local = a.priv_local / CARPETA_CAND / "ADJUDICACIONES_V9_FORMATO_MODULO.json"
    if ops_local.exists():
        sys.exit("ALTO: el archivo de adjudicaciones ya existe.")
    ops_local.write_text(json.dumps(ops, ensure_ascii=False, indent=1))
    ops_local.chmod(0o600)
    s9 = resumen(r9)

    carpeta = ROOT / "data/diccionario_sies_seguimiento" / EDICION
    if carpeta.exists():
        sys.exit("ALTO: la carpeta de edición ya existe.")
    carpeta.mkdir()
    d9 = copy.deepcopy(d8)
    d9.pop("reparaciones_C", None)
    d9.update({
        "edicion": EDICION,
        "fecha_hora": fecha,
        "clasificacion": "B fuentes; C integración; D decisiones aprobadas (incluye 21 correspondencias internas V3); E excepciones",
        "base_privada": {"ruta": str(PRIV_MAC / CARPETA_CAND / "DICCIONARIO_SIES_CANDIDATO_V9.sqlite"), "sha256": v9_sha},
        "resumen": {**d8["resumen"], **s9,
                    "operaciones_aprobadas_integradas": d8["resumen"]["operaciones_aprobadas_integradas"] + len(ops),
                    "nuevas_asignaciones": len(ops)},
        "edicion_anterior": {"descriptor": V8_DESC_REL, "sha256": V8_DESC_SHA},
        "entradas_cierre_sha256": {
            str(ROOT / V8_DESC_REL): V8_DESC_SHA,
            d8["base_privada"]["ruta"]: d8["base_privada"]["sha256"],
            str(ROOT / "data/diccionario_sies_seguimiento/activo.json"): sha256(activo_p),
            **{str(ROOT / "outputs/diccionario_v9_candidata_21_20261025" / f): sha256(Path(__file__).parent / f)
               for f in ("construir_candidata_v9.py", "QA_CANDIDATA.json", "MANIFEST_CANDIDATA.json", "LEEME.md", "promover_v9.py")},
            **{str(PRIV_MAC / CARPETA_CAND / f): sha256(a.priv_local / CARPETA_CAND / f)
               for f in ("OBSERVACIONES_21.json", "OPERACIONES_V9.json", "oferta_v5_hoja3.csv", "ADJUDICACIONES_V9_FORMATO_MODULO.json")},
            **{str(ROOT / "outputs/conciliacion_programas_cierres_20261025_v3" / f): sha256(ROOT / "outputs/conciliacion_programas_cierres_20261025_v3" / f)
               for f in ("LEEME.md", "revisar_fuentes.py", "evidencia_temporal_historica.json", "QA_MANIFEST.json")},
            str(ROOT / "outputs/conciliacion_multiversion_t1_20261025/DECISION_APROBADA.json"):
                sha256(ROOT / "outputs/conciliacion_multiversion_t1_20261025/DECISION_APROBADA.json"),
            "/Users/alexi/Desktop/IPSS_CONCILIACION_CARRERAS_UMAS_SIES_20261025_V5.xlsx":
                "7b994d5596dcfc526da79811a17a81344c64c82011c7507c656e66f1fd23fb88",
        },
        "estado": "ACTIVA",
        "adjudicaciones_D_v9": {"ruta": str(PRIV_MAC / CARPETA_CAND / "ADJUDICACIONES_V9_FORMATO_MODULO.json"),
                                "sha256": sha256(ops_local), "operaciones": len(ops),
                                "regla": "V3_TLOG_TAMD_TPAS_TCIB_2024_RE_O_J4V1_APROBADO_20261025",
                                "planes": {"TLOG20241": "I162S2C79J4V1", "TAMD20241": "I162S2C78J4V1",
                                           "TPAS20241": "I162S2C57J4V1", "TCIB20241": "I162S2C47J4V1"}},
        "heredado_de_v8": {"reparaciones_C": d8.get("reparaciones_C")},
    })
    (carpeta / "descriptor.json").write_text(json.dumps(d9, ensure_ascii=False, indent=2) + "\n")
    d9_sha = sha256(carpeta / "descriptor.json")
    (carpeta / "ACTIVO_ANTERIOR.json").write_text(activo_antes_txt)
    decision = {
        "clasificacion": "D decisión del usuario",
        "estado": "APROBADA",
        "responsable_aprobacion": "Alexi, usuario de este chat",
        "responsable_preparacion": "Claude",
        "autorizaciones": ["«procede» 25-10-2026 23:50: integrar al diccionario las 21 correspondencias internas de V5 hoja 1",
                           "«procede» 26-10-2026 09:45: promover la candidata v9 verificada"],
        "fecha_hora_registro": fecha,
        "alcance": "Exactamente 21 observaciones de TLOG20241, TAMD20241, TPAS20241 y TCIB20241 (T2/T3 2025–2026), sede 2 jornada 4.",
        "no_extiende": "No se extiende a otros contextos, planes ni períodos; no acredita fecha de migración, atribución documental ni aceptación SIES.",
        "relacion_decision_A": "El código T1 de cohorte se conserva aparte; las 149 excepciones respecto del ancla T1 no cambian.",
    }
    (carpeta / "DECISION_APROBADA.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n")
    alerta = {
        "clasificacion": "D autorización; C ejecución",
        "estado": "PROMOCION_AUTORIZADA_Y_APLICADA",
        "responsable_preparacion": "Claude; solicitud de Alexi",
        "responsable_aprobacion": "Alexi, usuario de este chat",
        "fecha_aprobacion": "2026-10-26T09:45:00-03:00",
        "fecha_ejecucion": fecha,
        "motivo": "21 correspondencias internas corroboradas en la revisión V3 (PROMEDIOS, Datos Alumnos RE/O, sede 2/jornada 4, oferta anual)",
        "edicion_anterior": {"descriptor": V8_DESC_REL, "sha256": V8_DESC_SHA},
        "edicion_propuesta": {"descriptor": f"data/diccionario_sies_seguimiento/{EDICION}/descriptor.json", "sha256": d9_sha},
        "cambios": {"observaciones_modificadas": len(ops), "observaciones_identicas": len(r9) - len(ops),
                    "pendientes_internos_antes": s8["pendientes_internos"]["observaciones"],
                    "pendientes_internos_despues": s9["pendientes_internos"]["observaciones"]},
        "denominadores_alterados": False,
        "commit_push": False,
        "reversion": "Restituir activo.json con el contenido de ACTIVO_ANTERIOR.json; conservar ambas bases privadas.",
    }
    (carpeta / "ALERTA_PROMOCION.json").write_text(json.dumps(alerta, ensure_ascii=False, indent=2) + "\n")
    (carpeta / "RESUMEN.json").write_text(json.dumps({"v8": s8, "v9": s9}, ensure_ascii=False, indent=2) + "\n")
    secretos = {r["persona"] for r in r9} | {r["CODCLI"] for r in r9}
    for f in carpeta.iterdir():
        t = f.read_text()
        if any(s and s in t for s in secretos):
            sys.exit(f"ALTO: identificador individual en {f.name}")
    activo_p.write_text(json.dumps({"descriptor": f"data/diccionario_sies_seguimiento/{EDICION}/descriptor.json",
                                    "sha256": d9_sha}, indent=2) + "\n")
    print(json.dumps({"edicion": EDICION, "descriptor_sha256": d9_sha, "base_sha256": v9_sha,
                      "operaciones": len(ops), "resumen_v8": s8, "resumen_v9": s9}, ensure_ascii=False))


if __name__ == "__main__":
    main()
