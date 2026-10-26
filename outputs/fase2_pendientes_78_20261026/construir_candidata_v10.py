"""Fase 2 · Hito 4/4: construye la candidata v10 (no la activa) con los 27 casos D1 aprobados (opción A corregida: control de año de ingreso).

Copia la base v9 activa y modifica solo los campos permitidos por aplicar_adjudicaciones en esas 27
observaciones. Verifica: v9 intacta; cada caso sigue siendo D1; 24.774 observaciones; cambian exactamente 27;
índice MU y dimensiones idénticos; aplicar_adjudicaciones(v9, ops) reproduce la candidata.
"""
import argparse, collections, datetime as dt, hashlib, json, shutil, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from common.diccionario_sies_seguimiento import aplicar_adjudicaciones  # noqa: E402

PRIV = Path("/Users/alexi/.local/share/ipss")
ESTADO = "CORRESPONDENCIA_INTERNA_MU2026_MISMO_CONTEXTO_APROBADA"
REGLA = "D1_MU2026_CODIGO_UNICO_INGRESO_HASTA_2025_CODCLI_CONTINUO_T2T3_2025_APROBADO_20261026"
PERMITIDOS = {"codigo_interno_adoptado", "estado_interno", "regla", "clasificacion", "requisito_pendiente"}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def filas(p):
    db = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    out = {i: json.loads(x) for i, x in db.execute("SELECT id, payload FROM observaciones")}
    otras = (list(db.execute("SELECT id,persona,codcli,plan,anio,periodo,carrera,sede,jornada FROM observaciones ORDER BY id")),
             list(db.execute("SELECT * FROM mu_anual ORDER BY rowid")))
    db.close(); return out, otras


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--priv-local", type=Path, default=PRIV)
    ap.add_argument("--trabajo", type=Path, default=None)
    a = ap.parse_args()
    act = json.loads((ROOT / "data/diccionario_sies_seguimiento/activo.json").read_text())
    d9 = json.loads((ROOT / act["descriptor"]).read_text())
    if d9["edicion"] != "v9_20261026_cuatro_planes_v3":
        sys.exit("ALTO: la edición activa no es v9.")
    v9 = a.priv_local / Path(d9["base_privada"]["ruta"]).relative_to(PRIV)
    if sha(v9) != d9["base_privada"]["sha256"]:
        sys.exit("ALTO: base v9 alterada.")
    prop = json.loads((a.priv_local / "fase2_pendientes_78_20261026/PROPUESTA_DECISION_78.json").read_text())
    d1 = [p for p in prop if p["nivel"] == "D1"]
    if len(d1) != 27:
        sys.exit(f"ALTO: se esperaban 27 D1 y hay {len(d1)}.")
    final = a.priv_local / "v10_candidata_27_20261026/DICCIONARIO_SIES_CANDIDATO_V10.sqlite"
    if final.exists():
        sys.exit("ALTO: la candidata ya existe.")
    trabajo = a.trabajo or final.parent; trabajo.mkdir(parents=True, exist_ok=True)
    cand = trabajo / final.name
    shutil.copy2(v9, cand)
    db = sqlite3.connect(cand)
    for p in d1:
        (payload,) = db.execute("SELECT payload FROM observaciones WHERE id=?", (p["observacion_id"],)).fetchone()
        r = json.loads(payload)
        if r["codigo_documental_atribuible"] or r["codigo_interno_adoptado"] or r["candidatos_calculados"] != [p["codigo_propuesto"]]:
            db.close(); sys.exit(f"ALTO: la observación {p['observacion_id']} ya no cumple las condiciones de D1.")
        r.update({
            "codigo_interno_adoptado": p["codigo_propuesto"], "estado_interno": ESTADO, "regla": REGLA,
            "clasificacion": "D correspondencia interna aprobada; B MU 2026 con el mismo código y CODCLI continuo; B/C PROMEDIOS, oferta 2025, candidato único; E atribución documental 2025",
            "requisito_pendiente": ("La matrícula SIES 2025 (anual) registra el contexto previo; el código del contexto T2/T3 2025 se respalda en la MU 2026 "
                                    "(mismo código, único, ingreso a la carrera ≤ 2025) y en el mismo CODCLI con ese código documental en 2026. No acredita fecha efectiva del cambio "
                                    "ni aceptación SIES para 2025. Código T1 de cohorte conservado aparte; la discrepancia con el ancla T1 sigue siendo excepción. Solo este contexto."),
        })
        db.execute("UPDATE observaciones SET payload=? WHERE id=?", (json.dumps(r, ensure_ascii=False), p["observacion_id"]))
    db.commit(); db.close()
    (r9, o9), (r10, o10) = filas(v9), filas(cand)
    cambiadas = sorted(i for i in r9 if r9[i] != r10[i])
    campos = collections.Counter(k for i in cambiadas for k in set(r9[i]) | set(r10[i]) if r9[i].get(k) != r10[i].get(k))
    ops = [{"observacion_id": r9[i]["observacion_id"], "estado_antes": r9[i], "estado_despues": r10[i]} for i in cambiadas]
    filas9 = [r9[i] for i in sorted(r9)]
    reproduce = aplicar_adjudicaciones(filas9, ops) == [r10[i] for i in sorted(r10)]
    qa = {"observaciones": len(r10), "cambiadas": len(cambiadas),
          "cambiadas_son_las_27": sorted(r10[i]["observacion_id"] for i in cambiadas) == sorted(p["observacion_id"] for p in d1),
          "campos": dict(campos), "solo_campos_permitidos": set(campos) <= PERMITIDOS,
          "dimensiones_identicas": o9[0] == o10[0], "mu_identica": o9[1] == o10[1],
          "aplicar_adjudicaciones_reproduce": reproduce, "v9_intacta": sha(v9) == d9["base_privada"]["sha256"],
          "por_codigo": dict(collections.Counter(p["codigo_propuesto"] for p in d1))}
    qa["todos_ok"] = (qa["observaciones"] == 24774 and qa["cambiadas"] == 27 and qa["cambiadas_son_las_27"] and qa["solo_campos_permitidos"]
                      and qa["dimensiones_identicas"] and qa["mu_identica"] and reproduce and qa["v9_intacta"])
    if not qa["todos_ok"]:
        sys.exit("ALTO: QA fallido " + json.dumps(qa, ensure_ascii=False))
    if cand != final:
        shutil.copyfile(cand, final)
    final.chmod(0o600)
    ops_p = final.parent / "ADJUDICACIONES_V10_FORMATO_MODULO.json"
    ops_p.write_text(json.dumps(ops, ensure_ascii=False, indent=1)); ops_p.chmod(0o600)
    sal = Path(__file__).parent
    (sal / "QA_CANDIDATA_V10.json").write_text(json.dumps(qa, ensure_ascii=False, indent=1))
    (sal / "MANIFEST_CANDIDATA_V10.json").write_text(json.dumps({
        "fecha_hora": dt.datetime.now().astimezone().isoformat(), "estado": "CANDIDATA_NO_ACTIVA",
        "edicion_base": {"descriptor": act["descriptor"], "sha256": act["sha256"], "base_sha256": d9["base_privada"]["sha256"]},
        "candidata": {"ruta": str(PRIV / "v10_candidata_27_20261026/DICCIONARIO_SIES_CANDIDATO_V10.sqlite"), "sha256": sha(final)},
        "adjudicaciones": {"ruta": str(PRIV / "v10_candidata_27_20261026/ADJUDICACIONES_V10_FORMATO_MODULO.json"), "sha256": sha(ops_p), "n": len(ops),
                           "estado": ESTADO, "regla": REGLA},
        "propuesta": {"ruta": str(PRIV / "fase2_pendientes_78_20261026/PROPUESTA_DECISION_78.json"),
                      "sha256": sha(a.priv_local / "fase2_pendientes_78_20261026/PROPUESTA_DECISION_78.json")},
        "script_sha256": sha(Path(__file__)), "qa_sha256": sha(sal / "QA_CANDIDATA_V10.json"),
        "activo_json_modificado": False, "commit_push": False}, ensure_ascii=False, indent=1))
    print(json.dumps(qa, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
