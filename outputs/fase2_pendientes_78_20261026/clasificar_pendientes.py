"""Fase 2 · Hito 1/4: clasifica los pendientes de código del seguimiento según la evidencia que falta.

Universo: contextos de la vista Fase 3 sin código documental ni interno en el diccionario ACTIVO.
Clases:  A = la MU del año registra la misma carrera, pero otra jornada o versión que el contexto T2/T3;
         B = la MU del año registra otra carrera (la de T1): cambio de carrera posterior a la MU;
         C = la persona no aparece en la MU de ese año.
Solo lectura. Detalle por observación en carpeta privada; salida del repositorio agregada.
"""
import argparse, collections, datetime as dt, hashlib, json, re, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIV = Path("/Users/alexi/.local/share/ipss")
PAT = re.compile(r"I162S(\d+)C(\d+)J(\d+)V(\d+)$")
fam = lambda x: (lambda m: m.group(2) if m else None)(PAT.match(x or ""))
jor = lambda x: (lambda m: m.group(3) if m else None)(PAT.match(x or ""))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--priv-local", type=Path, default=PRIV); a = ap.parse_args()
    act = json.loads((ROOT / "data/diccionario_sies_seguimiento/activo.json").read_text())
    d = json.loads((ROOT / act["descriptor"]).read_text())
    base = a.priv_local / Path(d["base_privada"]["ruta"]).relative_to(PRIV)
    vista_p = a.priv_local / "trazabilidad_integral_fase3_20261025/VISTA_T1_T2_T3.json"
    assert sha(base) == d["base_privada"]["sha256"] and sha(vista_p).startswith("72edecb9")
    db = sqlite3.connect(f"file:{base}?mode=ro", uri=True)
    det = []
    for c in (c for p in json.loads(vista_p.read_text()) for c in (p.get("contextos") or [])):
        r = json.loads(db.execute("SELECT payload FROM observaciones WHERE id=?", (c["observacion_id"],)).fetchone()[0])
        if r["codigo_documental_atribuible"] or r["codigo_interno_adoptado"]:
            continue
        mu = sorted({x for (x,) in db.execute("SELECT codigo FROM mu_anual WHERE persona=? AND anio=?", (r["persona"], str(c["anio_observado"])))})
        f = fam(r["codigo_propuesto"] or c["codigo_origen_T1"]); muf = [x for x in mu if fam(x) == f]
        if muf:
            clase = "A_MU_MISMA_CARRERA_OTRA_JORNADA" if jor(muf[0]) != r["jornada_sies"] else "A_MU_MISMA_CARRERA_OTRA_VERSION"
        elif mu:
            clase = "B_MU_OTRA_CARRERA_CAMBIO_POSTERIOR"
        else:
            clase = "C_SIN_MU_DEL_ANIO"
        det.append({"observacion_id": c["observacion_id"], "clase": clase, "plan": c["plan_destino"],
                    "anio": str(c["anio_observado"]), "periodo": c["periodo_nativo"], "jornada_contexto": r["jornada_sies"],
                    "codigo_propuesto": r["codigo_propuesto"], "codigos_mu_anio": mu, "codigo_T1": c["codigo_origen_T1"],
                    "mismo_expediente_T1": c["mismo_expediente_T1_atribuido"],
                    "fuente_a_revisar": ("cargas SIES 2.º/3.er intake 2025" if str(c["anio_observado"]) == "2025" else "sin carga T2/T3 2026 conocida")})
    db.close()
    priv = a.priv_local / "fase2_pendientes_78_20261026/DETALLE_78.json"
    priv.write_text(json.dumps(det, ensure_ascii=False, indent=1)); priv.chmod(0o600)
    agg = lambda *k: {"|".join(x): n for x, n in sorted(collections.Counter(tuple(str(r[i]) for i in k) for r in det).items())}
    out = {"clasificacion": "C clasificación; E pendientes", "fecha_hora": dt.datetime.now().astimezone().isoformat(),
           "edicion": d["edicion"], "pendientes": len(det), "por_clase": agg("clase"), "por_clase_anio": agg("clase", "anio"),
           "por_clase_plan": agg("clase", "plan"), "por_fuente_a_revisar": agg("fuente_a_revisar"),
           "detalle_privado": {"ruta": str(PRIV / "fase2_pendientes_78_20261026/DETALLE_78.json"), "sha256": sha(priv)},
           "script_sha256": sha(Path(__file__))}
    (Path(__file__).parent / "CLASIFICACION_78.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps({k: out[k] for k in ("pendientes", "por_clase", "por_clase_anio", "por_fuente_a_revisar")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
