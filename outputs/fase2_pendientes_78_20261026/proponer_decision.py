"""Fase 2 · Hito 3/4: propuesta de decisión D para los pendientes 2025 respaldados por la MU del año siguiente.

No modifica el diccionario. Clasifica cada uno de los 78 pendientes:
  D1 propuesto: todas las verificaciones + MU 2026 con un solo código (=propuesto) + mismo CODCLI en 2026 con ese código documental.
  D2 propuesto con revisión: como D1, pero la MU 2026 trae además otro código o no hay observación 2026 del mismo CODCLI.
  E: sin evidencia coherente (motivo explícito).
Verificaciones comunes: código propuesto = único candidato calculado; sede 2; jornada del código = jornada del contexto;
oferta 2025 vigente para el código; actividad del plan en PROMEDIOS para el período; un solo plan en el expediente;
año de ingreso a la carrera en la MU 2026 no posterior al año del contexto (control agregado el 26-10-2026).
"""
import argparse, collections, csv, datetime as dt, hashlib, json, re, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIV = Path("/Users/alexi/.local/share/ipss")
PAT = re.compile(r"I162S(\d+)C(\d+)J(\d+)V(\d+)$")
g = lambda x, i: (lambda m: m.group(i) if m else None)(PAT.match(x or ""))
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--priv-local", type=Path, default=PRIV); a = ap.parse_args()
    act = json.loads((ROOT / "data/diccionario_sies_seguimiento/activo.json").read_text())
    d = json.loads((ROOT / act["descriptor"]).read_text())
    base = a.priv_local / Path(d["base_privada"]["ruta"]).relative_to(PRIV)
    assert sha(base) == d["base_privada"]["sha256"]
    det_p = a.priv_local / "fase2_pendientes_78_20261026/DETALLE_78.json"
    oferta_p = a.priv_local / "v9_candidata_21_20261025/oferta_v5_hoja3.csv"
    of = {(r[0], r[1]): r for r in csv.reader(open(oferta_p, encoding="utf-8")) if len(r) > 11}
    db = sqlite3.connect(f"file:{base}?mode=ro", uri=True)
    salida = []
    for x in json.loads(det_p.read_text()):
        r = json.loads(db.execute("SELECT payload FROM observaciones WHERE id=?", (x["observacion_id"],)).fetchone()[0])
        prop = x["codigo_propuesto"]
        e = {"observacion_id": x["observacion_id"], "clase_hito1": x["clase"], "plan": x["plan"], "anio": x["anio"],
             "periodo": x["periodo"], "codigo_propuesto": prop}
        if x["anio"] != "2025":
            e.update(nivel="E", motivo="2026: no existe aún MU 2027 ni carga T2/T3 2026"); salida.append(e); continue
        mu26 = sorted({c for (c,) in db.execute("SELECT codigo FROM mu_anual WHERE persona=? AND anio='2026'", (r["persona"],))})
        if prop not in mu26:
            mot = ("sin MU 2026" if not mu26 else "MU 2026 en la misma carrera pero otra jornada" if any(g(c, 2) == g(prop, 2) for c in mu26)
                   else "MU 2026 en otra carrera")
            e.update(nivel="E", motivo=mot); salida.append(e); continue
        o26 = [json.loads(p) for (p,) in db.execute("SELECT payload FROM observaciones WHERE persona=? AND anio='2026'", (r["persona"],))]
        chk = {
            "candidato_unico": (r.get("candidatos_calculados") or []) == [prop],
            "sede_2": g(prop, 1) == "2" and r["sede_dimension"] == "2",
            "jornada_contexto": g(prop, 3) == r["jornada_sies"],
            "oferta_2025_vigente": ("2025", prop) in of and of[("2025", prop)][11].startswith("Vigente"),
            "promedios_periodo": any(f.get("PLAN_DE_ESTUDIO") == r["plan"] and f.get("ANO") == r["ano"] and f.get("PERIODO") == r["periodo"] for f in r["fuentes_promedios"]),
            "un_plan_expediente": r["planes_distintos_expediente"] == 1,
        }
        filas26 = [json.loads(x) for (x,) in db.execute("SELECT payload FROM mu_anual WHERE persona=? AND anio='2026'", (r["persona"],))]
        ingresos = {str(f.get("ingreso_actual")) for f in filas26 if f.get("codigo") == prop}
        # Control obligatorio (26-10-2026): el año de ingreso a la carrera según la MU 2026 no puede ser posterior al año del contexto
        chk["ingreso_carrera_mu2026_hasta_2025"] = bool(ingresos) and all(i.isdigit() and int(i) <= int(x["anio"]) for i in ingresos)
        extra = {"mu2026_codigo_unico": len(mu26) == 1,
                 "mismo_codcli_2026_documental": any(o["CODCLI"] == r["CODCLI"] and o["codigo_documental_atribuible"] == prop for o in o26)}
        if not all(chk.values()):
            e.update(nivel="E", motivo="falla verificación: " + ", ".join(k for k, v in chk.items() if not v))
        else:
            e.update(nivel="D1" if all(extra.values()) else "D2",
                     motivo="todas las verificaciones" if all(extra.values()) else "revisar: " + ", ".join(k for k, v in extra.items() if not v))
        e.update(verificaciones=chk, complementarias=extra, codigos_mu_2026=mu26)
        salida.append(e)
    db.close()
    priv = a.priv_local / "fase2_pendientes_78_20261026/PROPUESTA_DECISION_78.json"
    priv.write_text(json.dumps(salida, ensure_ascii=False, indent=1)); priv.chmod(0o600)
    cnt = lambda *k: {"|".join(map(str, t)): n for t, n in sorted(collections.Counter(tuple(s[i] for i in k) for s in salida).items())}
    out = {"clasificacion": "C propuesta; D pendiente de aprobación; E pendientes",
           "fecha_hora": dt.datetime.now().astimezone().isoformat(), "edicion_diccionario": d["edicion"],
           "total": len(salida), "por_nivel": cnt("nivel"), "por_nivel_plan_codigo": cnt("nivel", "plan", "codigo_propuesto"),
           "motivos_E": cnt("nivel", "motivo"), "por_nivel_clase": cnt("nivel", "clase_hito1"),
           "detalle_privado": {"ruta": str(PRIV / "fase2_pendientes_78_20261026/PROPUESTA_DECISION_78.json"), "sha256": sha(priv)},
           "script_sha256": sha(Path(__file__)), "modifica_diccionario": False}
    (Path(__file__).parent / "PROPUESTA_DECISION_78.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps({k: out[k] for k in ("por_nivel", "por_nivel_plan_codigo", "motivos_E")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
