"""Promueve la candidata v10 (27 correspondencias internas respaldadas por la MU 2026) a edición activa.

Autorización: Alexi, «procede» del 26-10-2026 11:53 (America/Santiago), tras la decisión corregida de 11:47.
Escribe data/diccionario_sies_seguimiento/v10_20261026_mu2026_27/ y cambia activo.json.
Todas las rutas del descriptor se registran como rutas del Mac (corrige la errata de v9).
No modifica v1–v9, bases anteriores, fuentes, Excel ni denominadores. Sin commit/push.
Reversión: restituir activo.json desde ACTIVO_ANTERIOR.json.
"""
import argparse, collections, copy, datetime as dt, json, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from common.diccionario_sies_seguimiento import aplicar_adjudicaciones, sha256  # noqa: E402

ROOT_MAC = Path("/Users/alexi/Documents/GitHub/avance_curricular")
PRIV_MAC = Path("/Users/alexi/.local/share/ipss")
V9_DESC_REL = "data/diccionario_sies_seguimiento/v9_20261026_cuatro_planes_v3/descriptor.json"
V9_DESC_SHA = "6a0b3a1ef145505ce4959d135bcf863b822b9c70561a9f6f91166cc6afb6446d"
V10_SHA = "c6c4b5a43434d87146a97d1c81510c87e0f988a5e3c232852d3bbc4622d1051c"
EDICION = "v10_20261026_mu2026_27"
CAND = "v10_candidata_27_20261026"
OUT = "outputs/fase2_pendientes_78_20261026"


def filas(p):
    db = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    out = [json.loads(x) for (x,) in db.execute("SELECT payload FROM observaciones ORDER BY id")]
    db.close(); return out


def resumen(rows):
    doc = [r for r in rows if r["codigo_documental_atribuible"]]
    solo = [r for r in rows if not r["codigo_documental_atribuible"] and r["codigo_interno_adoptado"]]
    pi = [r for r in rows if not r["codigo_documental_atribuible"] and not r["codigo_interno_adoptado"]]
    pd = [r for r in rows if not r["codigo_documental_atribuible"]]
    return {"universo_observaciones": len(rows), "personas": len({r["persona"] for r in rows}),
            "expedientes_carrera_codcli": len({(r["CODCLI"], r["carrera"]) for r in rows}),
            "codigo_documental_reutilizado": len(doc), "solo_correspondencia_interna_aprobada": len(solo),
            "pendientes_internos": {"observaciones": len(pi), "personas": len({r["persona"] for r in pi})},
            "pendientes_documentales": {"observaciones": len(pd), "personas": len({r["persona"] for r in pd})},
            "excepciones_por_estado": dict(collections.Counter(r["estado_interno"] for r in pi))}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--priv-local", type=Path, default=PRIV_MAC); a = ap.parse_args()
    mac = lambda rel: str(ROOT_MAC / rel)
    fecha = dt.datetime.now().astimezone().isoformat()
    activo_p = ROOT / "data/diccionario_sies_seguimiento/activo.json"
    antes_txt = activo_p.read_text(); activo = json.loads(antes_txt)
    if activo != {"descriptor": V9_DESC_REL, "sha256": V9_DESC_SHA} or sha256(ROOT / V9_DESC_REL) != V9_DESC_SHA:
        sys.exit("ALTO: el puntero activo no es v9 verificado.")
    d9 = json.loads((ROOT / V9_DESC_REL).read_text())
    for rel, h in d9["componentes_sha256"].items():
        if sha256(ROOT / rel) != h:
            sys.exit(f"ALTO: componente alterado {rel}")
    v9_local = a.priv_local / Path(d9["base_privada"]["ruta"]).relative_to(PRIV_MAC)
    v10_local = a.priv_local / CAND / "DICCIONARIO_SIES_CANDIDATO_V10.sqlite"
    if sha256(v9_local) != d9["base_privada"]["sha256"] or sha256(v10_local) != V10_SHA:
        sys.exit("ALTO: base v9 o candidata v10 distinta de la verificada.")
    man = json.loads((ROOT / OUT / "MANIFEST_CANDIDATA_V10.json").read_text())
    qa_c = json.loads((ROOT / OUT / "QA_CANDIDATA_V10.json").read_text())
    if man["candidata"]["sha256"] != V10_SHA or not qa_c["todos_ok"] or qa_c["cambiadas"] != 27:
        sys.exit("ALTO: manifiesto o QA de la candidata no coinciden.")
    r9, r10 = filas(v9_local), filas(v10_local)
    s9 = resumen(r9)
    for k, v in s9.items():
        if d9["resumen"].get(k) != v:
            sys.exit(f"ALTO: el resumen no reproduce v9 en {k}.")
    ops = [{"observacion_id": x["observacion_id"], "estado_antes": x, "estado_despues": y} for x, y in zip(r9, r10) if x != y]
    if len(ops) != 27 or aplicar_adjudicaciones(r9, ops) != r10:
        sys.exit("ALTO: las adjudicaciones no reproducen la candidata.")
    ops_local = a.priv_local / CAND / "ADJUDICACIONES_V10_FORMATO_MODULO.json"
    if json.loads(ops_local.read_text()) != ops:
        sys.exit("ALTO: el archivo de adjudicaciones de la candidata no coincide.")
    s10 = resumen(r10)
    carpeta = ROOT / "data/diccionario_sies_seguimiento" / EDICION
    if carpeta.exists():
        sys.exit("ALTO: la carpeta de edición ya existe.")
    carpeta.mkdir()
    d10 = copy.deepcopy(d9)
    for k in ("adjudicaciones_D_v9", "heredado_de_v8"):
        d10.pop(k, None)
    privados = ["OBSERVACIONES_21.json"]  # no aplica; se listan explícitamente abajo
    d10.update({
        "edicion": EDICION, "fecha_hora": fecha,
        "clasificacion": "B fuentes; C integración; D decisiones aprobadas (incluye 27 correspondencias internas respaldadas por la MU 2026); E excepciones",
        "base_privada": {"ruta": str(PRIV_MAC / CAND / "DICCIONARIO_SIES_CANDIDATO_V10.sqlite"), "sha256": V10_SHA},
        "resumen": {**d9["resumen"], **s10,
                    "operaciones_aprobadas_integradas": d9["resumen"]["operaciones_aprobadas_integradas"] + len(ops),
                    "nuevas_asignaciones": len(ops)},
        "edicion_anterior": {"descriptor": V9_DESC_REL, "sha256": V9_DESC_SHA},
        "entradas_cierre_sha256": {
            mac(V9_DESC_REL): V9_DESC_SHA,
            d9["base_privada"]["ruta"]: d9["base_privada"]["sha256"],
            mac("data/diccionario_sies_seguimiento/activo.json"): sha256(activo_p),
            **{mac(f"{OUT}/{f}"): sha256(ROOT / OUT / f) for f in (
                "clasificar_pendientes.py", "CLASIFICACION_78.json", "HITO2_RESULTADO.json", "proponer_decision.py",
                "PROPUESTA_DECISION_78.json", "DIAGNOSTICO_D2_Y_CONTROL_INGRESO.json", "DECISION_APROBADA_D1.json",
                "DECISION_APROBADA_D1_CORREGIDA.json", "construir_candidata_v10.py", "QA_CANDIDATA_V10.json",
                "MANIFEST_CANDIDATA_V10.json", "promover_v10.py")},
            **{str(PRIV_MAC / p): sha256(a.priv_local / p) for p in (
                "fase2_pendientes_78_20261026/DETALLE_78.json", "fase2_pendientes_78_20261026/PROPUESTA_DECISION_78.json",
                f"{CAND}/ADJUDICACIONES_V10_FORMATO_MODULO.json", "trazabilidad_integral_fase3_20261025/VISTA_T1_T2_T3.json",
                "v9_candidata_21_20261025/oferta_v5_hoja3.csv")},
        },
        "estado": "ACTIVA",
        "adjudicaciones_D_v10": {"ruta": str(PRIV_MAC / CAND / "ADJUDICACIONES_V10_FORMATO_MODULO.json"), "sha256": sha256(ops_local),
                                 "operaciones": len(ops), "regla": "D1_MU2026_CODIGO_UNICO_INGRESO_HASTA_2025_CODCLI_CONTINUO_T2T3_2025_APROBADO_20261026",
                                 "por_codigo": dict(collections.Counter(o["estado_despues"]["codigo_interno_adoptado"] for o in ops))},
        "errata_corregida": "Rutas registradas como rutas del Mac; corrige ERRATA_RUTAS.json de v9.",
    })
    (carpeta / "descriptor.json").write_text(json.dumps(d10, ensure_ascii=False, indent=2) + "\n")
    d10_sha = sha256(carpeta / "descriptor.json")
    (carpeta / "ACTIVO_ANTERIOR.json").write_text(antes_txt)
    (carpeta / "DECISION_APROBADA.json").write_text((ROOT / OUT / "DECISION_APROBADA_D1_CORREGIDA.json").read_text())
    (carpeta / "ALERTA_PROMOCION.json").write_text(json.dumps({
        "clasificacion": "D autorización; C ejecución", "estado": "PROMOCION_AUTORIZADA_Y_APLICADA",
        "responsable_preparacion": "Claude; solicitud de Alexi", "responsable_aprobacion": "Alexi, usuario de este chat",
        "fecha_aprobacion": "2026-10-26T11:53:00-03:00", "fecha_ejecucion": fecha,
        "motivo": "27 contextos T2/T3 2025 respaldados por la MU 2026 (código único, ingreso a la carrera hasta 2025, CODCLI continuo)",
        "edicion_anterior": {"descriptor": V9_DESC_REL, "sha256": V9_DESC_SHA},
        "edicion_propuesta": {"descriptor": f"data/diccionario_sies_seguimiento/{EDICION}/descriptor.json", "sha256": d10_sha},
        "cambios": {"observaciones_modificadas": len(ops), "observaciones_identicas": len(r10) - len(ops),
                    "pendientes_internos_antes": s9["pendientes_internos"]["observaciones"],
                    "pendientes_internos_despues": s10["pendientes_internos"]["observaciones"]},
        "denominadores_alterados": False, "commit_push": False,
        "reversion": "Restituir activo.json con el contenido de ACTIVO_ANTERIOR.json; conservar ambas bases privadas."},
        ensure_ascii=False, indent=2) + "\n")
    (carpeta / "RESUMEN.json").write_text(json.dumps({"v9": s9, "v10": s10}, ensure_ascii=False, indent=2) + "\n")
    secretos = {r["persona"] for r in r10} | {r["CODCLI"] for r in r10}
    for f in carpeta.iterdir():
        t = f.read_text()
        if any(s and s in t for s in secretos):
            sys.exit(f"ALTO: identificador individual en {f.name}")
        if "/sessions/" in t:
            sys.exit(f"ALTO: ruta del entorno de ejecución en {f.name}")
    activo_p.write_text(json.dumps({"descriptor": f"data/diccionario_sies_seguimiento/{EDICION}/descriptor.json", "sha256": d10_sha}, indent=2) + "\n")
    print(json.dumps({"edicion": EDICION, "descriptor_sha256": d10_sha, "operaciones": len(ops), "resumen_v9": s9, "resumen_v10": s10}, ensure_ascii=False))


if __name__ == "__main__":
    main()
