"""Evalúa la regla de herencia del código T1 propuesta en §6, sin adoptarla.

Regla: heredar el código SIES de T1 solo si coinciden carrera, plan y expediente, sede, jornada,
modalidad y duración (oferta), contexto temporal (mismo año o siguiente) y no existe otra versión
de la familia sede-carrera-jornada en la oferta del año observado.
Variantes: 'estricta' (cualquier otra versión presente) y 'laxa' (solo otra versión abierta a nuevos).

1) Prueba retrospectiva: contextos con código documental (B/C) que cumplen la regla, ¿heredar acierta?
2) Impacto: cuántos pendientes E del diccionario activo resolvería.
No modifica diccionario, fuentes, Excel ni denominadores. Salidas agregadas, sin identificadores.
"""
import argparse, csv, datetime as dt, hashlib, json, re, sqlite3, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIV = Path("/Users/alexi/.local/share/ipss")
PAT = re.compile(r"I162S(\d+)C(\d+)J(\d+)V(\d+)$")
ESPERADO = {"vista": "72edecb9507f46985533d1c63b83735beb4db58d743c89c226ca6be1a2c8ef31"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def fam(c):
    m = PAT.match(c or "")
    return (m.group(1), m.group(2), m.group(3)) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--priv-local", type=Path, default=PRIV)
    a = ap.parse_args()
    vista_p = a.priv_local / "trazabilidad_integral_fase3_20261025/VISTA_T1_T2_T3.json"
    oferta_p = a.priv_local / "v9_candidata_21_20261025/oferta_v5_hoja3.csv"
    activo = json.loads((ROOT / "data/diccionario_sies_seguimiento/activo.json").read_text())
    desc = json.loads((ROOT / activo["descriptor"]).read_text())
    base_p = a.priv_local / Path(desc["base_privada"]["ruta"]).relative_to(PRIV)
    if sha(vista_p) != ESPERADO["vista"] or sha(ROOT / activo["descriptor"]) != activo["sha256"] or sha(base_p) != desc["base_privada"]["sha256"]:
        sys.exit("ALTO: hash de entrada distinto del verificado.")

    rows = list(csv.reader(open(oferta_p, encoding="utf-8")))
    hdr = next(r for r in rows if r and r[0] == "Año")
    of = {(r[0], r[1]): dict(zip(hdr, r)) for r in rows if len(r) > 11 and re.fullmatch(r"\d{4}", r[0] or "") and r[1].startswith("I162")}
    ctx = [c for p in json.loads(vista_p.read_text()) for c in (p.get("contextos") or [])]

    # Estado vigente del diccionario activo por observación (independiente de la vista)
    db = sqlite3.connect(f"file:{base_p}?mode=ro", uri=True)
    ids = [c["observacion_id"] for c in ctx]
    vigente = {}
    for i in range(0, len(ids), 900):
        q = ids[i:i + 900]
        for oid, p in db.execute(f"SELECT id, payload FROM observaciones WHERE id IN ({','.join('?' * len(q))})", q):
            r = json.loads(p)
            vigente[oid] = r["codigo_documental_atribuible"] or r["codigo_interno_adoptado"] or None
    db.close()

    def condiciones(c, variante):
        t = c["codigo_origen_T1"]; m = PAT.match(t or "")
        a0, a1 = str(c["anio_origen"]), str(c["anio_observado"])
        o0, o1 = of.get((a0, t)), of.get((a1, t))
        otras = [cc for (an, cc), v in of.items() if an == a1 and cc != t and fam(cc) == fam(t)
                 and (variante == "estricta" or v["Vigencia oferta"].startswith("Vigente con"))]
        return {
            "plan_carrera_expediente": c["comparacion_plan"] == "MISMO_PLAN_OBSERVADO" and c["comparacion_carrera_umas"].startswith("MISMA") and bool(c["mismo_expediente_T1_atribuido"]),
            "sede": bool(m) and m.group(1) == c["sede_contexto"],
            "jornada": bool(m) and m.group(3) == c["jornada_contexto"],
            "oferta_T1_en_anio_observado": o1 is not None,
            "modalidad_duracion": bool(o0 and o1) and all(o0[k] == o1[k] for k in ("Nivel global", "Tipo de plan", "Duración estudios (sem.)", "Duración total (sem.)")),
            "temporal_mismo_anio_o_siguiente": int(a1) - int(a0) in (0, 1),
            "sin_otra_version": bool(m) and not otras,
        }

    resultado, filas_csv = {}, []
    for variante in ("estricta", "laxa"):
        bt, err, imp, mot = Counter(), Counter(), Counter(), Counter()
        for c in ctx:
            ch = condiciones(c, variante); ok = all(ch.values())
            if c["respaldo_destino"].startswith("B"):
                doc = c["codigo_documental_destino"] or c["codigo_destino"]
                bt["cumple_acierta" if ok and doc == c["codigo_origen_T1"] else
                   "cumple_falla" if ok else "no_cumple"] += 1
                if ok and doc != c["codigo_origen_T1"]:
                    err[f"{c['plan_destino']}|T1 {c['codigo_origen_T1']}|documental {doc}"] += 1
            if vigente.get(c["observacion_id"]) is None:
                imp["resolveria" if ok else "no_resolveria"] += 1
                if not ok:
                    mot[" + ".join(k for k, v in ch.items() if not v)] += 1
        resultado[variante] = {"prueba_documental": dict(bt), "contraejemplos": dict(err),
                               "pendientes_diccionario_activo": sum(imp.values()), "impacto": dict(imp),
                               "condiciones_no_cumplidas_en_pendientes": dict(mot)}
        for k, v in mot.items():
            filas_csv.append({"VARIANTE": variante, "CONDICIONES_NO_CUMPLIDAS": k, "PENDIENTES": v})

    e, l = resultado["estricta"], resultado["laxa"]
    qa = [
        ("Universo contextos = 2.854", len(ctx) == 2854),
        ("Documentales en prueba = 2.742", sum(e["prueba_documental"].values()) == 2742),
        ("Pendientes con diccionario activo = 78", e["pendientes_diccionario_activo"] == 78),
        ("Pendientes activos = 99 de Fase 3 − 21 de v9", sum(1 for c in ctx if c["respaldo_destino"].startswith("E")) - 21 == 78),
        ("Edición activa v9", desc["edicion"] == "v9_20261026_cuatro_planes_v3"),
    ]
    ok = all(x for _, x in qa)
    with open(Path(__file__).parent / "PENDIENTES_POR_CONDICION.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["VARIANTE", "CONDICIONES_NO_CUMPLIDAS", "PENDIENTES"], delimiter=";")
        w.writeheader(); w.writerows(sorted(filas_csv, key=lambda r: (r["VARIANTE"], -r["PENDIENTES"])))
    out = Path(__file__).parent / "RESULTADO.json"
    out.write_text(json.dumps({"clasificacion": "C evaluación; E regla propuesta no adoptada", "resultado": resultado,
                               "qa": [{"control": c, "ok": x} for c, x in qa], "todos_ok": ok}, ensure_ascii=False, indent=1))
    (Path(__file__).parent / "MANIFEST.json").write_text(json.dumps({
        "fecha_hora": dt.datetime.now().astimezone().isoformat(),
        "entradas": {"vista_fase3": {"ruta": str(PRIV / "trazabilidad_integral_fase3_20261025/VISTA_T1_T2_T3.json"), "sha256": sha(vista_p)},
                     "oferta_v5_hoja3": {"ruta": str(PRIV / "v9_candidata_21_20261025/oferta_v5_hoja3.csv"), "sha256": sha(oferta_p)},
                     "diccionario_activo": {"descriptor": activo["descriptor"], "sha256": activo["sha256"], "base_sha256": desc["base_privada"]["sha256"]}},
        "script_sha256": sha(Path(__file__)),
        "salidas": {"RESULTADO.json": sha(out), "PENDIENTES_POR_CONDICION.csv": sha(Path(__file__).parent / "PENDIENTES_POR_CONDICION.csv")},
        "modifica_diccionario_fuentes_excel_denominadores": False, "commit_push": False,
        "identificadores_individuales_en_salidas": False}, ensure_ascii=False, indent=1))
    print(json.dumps(resultado, ensure_ascii=False, indent=1)); print("QA", ok)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
