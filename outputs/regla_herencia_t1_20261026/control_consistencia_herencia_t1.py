"""Control de consistencia T1 (decisión D opción A, 26-10-2026). No asigna códigos.

Para cada contexto del seguimiento que cumple la variante ESTRICTA de la regla §6 y tiene código
documental en el diccionario ACTIVO, exige que ese código sea el de T1. Cualquier diferencia se
informa para revisión humana (no se corrige). Salida agregada; exit 1 si hay diferencias.
Reutilizable tras cada nueva edición del diccionario o nueva vista de seguimiento.
"""
import argparse, csv, datetime as dt, hashlib, json, re, sqlite3, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIV = Path("/Users/alexi/.local/share/ipss")
PAT = re.compile(r"I162S(\d+)C(\d+)J(\d+)V(\d+)$")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def fam(c):
    m = PAT.match(c or "")
    return (m.group(1), m.group(2), m.group(3)) if m else None


def cumple_estricta(c, of):
    t = c["codigo_origen_T1"]; m = PAT.match(t or "")
    if not m:
        return False
    a0, a1 = str(c["anio_origen"]), str(c["anio_observado"])
    o0, o1 = of.get((a0, t)), of.get((a1, t))
    return (c["comparacion_plan"] == "MISMO_PLAN_OBSERVADO" and c["comparacion_carrera_umas"].startswith("MISMA")
            and bool(c["mismo_expediente_T1_atribuido"]) and m.group(1) == c["sede_contexto"]
            and m.group(3) == c["jornada_contexto"] and o1 is not None and o0 is not None
            and all(o0[k] == o1[k] for k in ("Nivel global", "Tipo de plan", "Duración estudios (sem.)", "Duración total (sem.)"))
            and int(a1) - int(a0) in (0, 1)
            and not any(an == a1 and cc != t and fam(cc) == fam(t) for (an, cc) in of))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--priv-local", type=Path, default=PRIV)
    ap.add_argument("--vista", default="trazabilidad_integral_fase3_20261025/VISTA_T1_T2_T3.json")
    ap.add_argument("--oferta", default="v9_candidata_21_20261025/oferta_v5_hoja3.csv")
    a = ap.parse_args()
    activo = json.loads((ROOT / "data/diccionario_sies_seguimiento/activo.json").read_text())
    if sha(ROOT / activo["descriptor"]) != activo["sha256"]:
        sys.exit("ALTO: descriptor activo alterado.")
    desc = json.loads((ROOT / activo["descriptor"]).read_text())
    base = a.priv_local / Path(desc["base_privada"]["ruta"]).relative_to(PRIV)
    if sha(base) != desc["base_privada"]["sha256"]:
        sys.exit("ALTO: base activa alterada.")
    vista_p, oferta_p = a.priv_local / a.vista, a.priv_local / a.oferta
    rows = list(csv.reader(open(oferta_p, encoding="utf-8")))
    hdr = next(r for r in rows if r and r[0] == "Año")
    of = {(r[0], r[1]): dict(zip(hdr, r)) for r in rows if len(r) > 11 and re.fullmatch(r"\d{4}", r[0] or "") and r[1].startswith("I162")}
    ctx = [c for p in json.loads(vista_p.read_text()) for c in (p.get("contextos") or [])]
    db = sqlite3.connect(f"file:{base}?mode=ro", uri=True)
    doc = {}
    ids = [c["observacion_id"] for c in ctx]
    for i in range(0, len(ids), 900):
        q = ids[i:i + 900]
        for oid, p in db.execute(f"SELECT id, payload FROM observaciones WHERE id IN ({','.join('?' * len(q))})", q):
            doc[oid] = json.loads(p)["codigo_documental_atribuible"] or None
    db.close()
    n = Counter(); difs = Counter()
    for c in ctx:
        d = doc.get(c["observacion_id"])
        if not d:
            n["sin_documental_no_aplica"] += 1
        elif not cumple_estricta(c, of):
            n["documental_no_cumple_condiciones"] += 1
        elif d == c["codigo_origen_T1"]:
            n["consistente"] += 1
        else:
            n["DIFERENCIA_PARA_REVISION"] += 1
            difs[f"{c['plan_destino']}|T1 {c['codigo_origen_T1']}|documental {d}|{c['anio_observado']}-{c['periodo_nativo']}"] += 1
    out = {"clasificacion": "C control; D regla aprobada como control (opción A); no asigna códigos",
           "fecha_hora": dt.datetime.now().astimezone().isoformat(),
           "edicion_diccionario": desc["edicion"], "descriptor_sha256": activo["sha256"],
           "vista_sha256": sha(vista_p), "oferta_sha256": sha(oferta_p), "script_sha256": sha(Path(__file__)),
           "contextos": len(ctx), "resultado": dict(n), "diferencias_agregadas": dict(difs),
           "estado": "OK" if not difs else "REVISAR"}
    destino = Path(__file__).parent / f"CONTROL_{desc['edicion']}.json"
    destino.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(0 if not difs else 1)


if __name__ == "__main__":
    main()
