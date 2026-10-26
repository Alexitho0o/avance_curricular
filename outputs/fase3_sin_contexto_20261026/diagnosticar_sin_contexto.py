"""Fase 3/5 · Hito 1/3: separa las causas de las posiciones T1 sin contexto en T2/T3 (solo lectura).

Jerarquía (cada posición en una sola causa, en este orden):
 1 ALCANCE: la carrera de T1 (familia C del código SIES) no tiene ninguna observación en el diccionario activo.
 2 PERSONA_FUERA_DEL_DICCIONARIO: carrera cubierta, pero la persona no tiene ninguna observación en el diccionario.
 3 ACTIVIDAD_NO_INDEXADA: la persona está en el diccionario y PROMEDIOS registra actividad en ese año-período.
 4 TITULADO_O_EGRESADO / 5 ELIMINADO_O_SUSPENDIDO / 6 VIGENTE_SIN_ACTIVIDAD / 7 SIN_EXPEDIENTE_DA:
   estado académico ACTUAL en DATOSDEALUMNOS (no fecha del evento).
Para 1 y 2 se informa además, como dato complementario, si hay actividad en el período y el estado en DA.
Fuentes de actividad: PROMEDIOS 7804, 12166 y 3233 (12166 y 3233 tienen exactamente 70.000 filas: extracciones
posiblemente truncadas). Ninguna causa se interpreta como deserción.
"""
import argparse, collections, datetime as dt, hashlib, json, re, sqlite3, unicodedata
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parents[2]
PRIV = Path("/Users/alexi/.local/share/ipss")
BASES = "/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES"
PROM = ["04_UMAS_PROMEDIOSDEALUMNOS/PROMEDIOSDEALUMNOS_7804.xlsx", "04_UMAS_PROMEDIOSDEALUMNOS/PROMEDIOSDEALUMNOS_12166.xlsx",
        "04_UMAS_PROMEDIOSDEALUMNOS/PROMEDIOSDEALUMNOS_3233.xlsx"]
DA = "03_UMAS_DATOSDEALUMNOS/DATOSDEALUMNOS_12159.xlsx"
fam = lambda x: (re.match(r"I162S\d+C(\d+)J", x or "") or [None, None])[1]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def norm(n, dv=None):
    s = str(n or "").upper().replace(".", "").replace(" ", "")
    if dv is None:
        if "-" not in s:
            return None
        s, dv = s.split("-", 1)
    s = s.split(".")[0]
    return (str(int(s)) + "-" + str(dv).strip().upper().split(".")[0]) if s.isdigit() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--priv-local", type=Path, default=PRIV)
    ap.add_argument("--bases-local", type=Path, default=Path(BASES))
    a = ap.parse_args()
    act_ = json.loads((ROOT / "data/diccionario_sies_seguimiento/activo.json").read_text())
    d = json.loads((ROOT / act_["descriptor"]).read_text())
    base = a.priv_local / Path(d["base_privada"]["ruta"]).relative_to(PRIV)
    vista_p = a.priv_local / "trazabilidad_integral_fase3_20261025/VISTA_T1_T2_T3.json"
    assert sha(base) == d["base_privada"]["sha256"] and sha(vista_p).startswith("72edecb9")
    vista = json.loads(vista_p.read_text()); obj = {v["persona"] for v in vista}
    db = sqlite3.connect(f"file:{base}?mode=ro", uri=True)
    en_dic, fam_dic = set(), set()
    for pe, p in db.execute("SELECT persona, payload FROM observaciones"):
        en_dic.add(pe); r = json.loads(p)
        for c in [r.get("codigo_documental_atribuible"), r.get("codigo_interno_adoptado"), r.get("codigo_propuesto")] + list(r.get("candidatos_calculados") or []):
            if fam(c): fam_dic.add(fam(c))
    obs_per = collections.defaultdict(set)
    for pe, an, pr in db.execute("SELECT persona, anio, periodo FROM observaciones"):
        obs_per[pe].add((an, pr))
    db.close()
    act = collections.defaultdict(set); fuentes = {}
    for rel in PROM:
        f = a.bases_local / rel; fuentes[rel] = sha(f)
        ws = openpyxl.load_workbook(f, read_only=True).worksheets[0]; it = ws.iter_rows(values_only=True)
        ix = {k: i for i, k in enumerate(str(c) for c in next(it))}
        for r in it:
            pe = norm(r[ix["RUT"]], r[ix["DIG"]])
            if pe in obj:
                act[pe].add((str(r[ix["ANO"]]), str(r[ix["PERIODO"]]), Path(rel).stem.split("_")[-1]))
    f = a.bases_local / DA; fuentes[DA] = sha(f)
    ws = openpyxl.load_workbook(f, read_only=True).worksheets[0]; it = ws.iter_rows(values_only=True)
    ix = {k: i for i, k in enumerate(str(c) for c in next(it))}
    est = collections.defaultdict(set)
    for r in it:
        pe = norm(r[ix["RUT"]])
        if pe in obj:
            est[pe].add(str(r[ix["ESTADOACADEMICO"]]))

    def estado(pe):
        e = est.get(pe, set())
        if not e: return "SIN_EXPEDIENTE_DA"
        if e & {"TITULADO", "EGRESADO"}: return "TITULADO_O_EGRESADO"
        if "VIGENTE" in e: return "VIGENTE"
        if e & {"ELIMINADO", "SUSPENDIDO"}: return "ELIMINADO_O_SUSPENDIDO"
        return "OTRO"

    det, filas = [], []
    for v in vista:
        if v["contextos"]:
            continue
        pe, an, pr = v["persona"], str(v["anio_observado"]), v["periodo_nativo"]
        activo = any(x[0] == an and x[1] == pr for x in act.get(pe, ()))
        e = estado(pe)
        if fam(v["codigo_origen_T1"]) not in fam_dic:
            causa = "1_CARRERA_FUERA_DEL_ALCANCE_DEL_DICCIONARIO"
        elif pe not in en_dic:
            causa = "2_PERSONA_FUERA_DEL_DICCIONARIO"
        elif activo:
            causa = "3_ACTIVIDAD_EN_PERIODO_NO_INDEXADA"
        else:
            causa = {"TITULADO_O_EGRESADO": "4_TITULADO_O_EGRESADO", "ELIMINADO_O_SUSPENDIDO": "5_ELIMINADO_O_SUSPENDIDO",
                     "VIGENTE": "6_VIGENTE_SIN_ACTIVIDAD_EN_PERIODO", "SIN_EXPEDIENTE_DA": "7_SIN_EXPEDIENTE_DA"}.get(e, "8_OTRO")
        det.append({"fila_origen_foto": v["fila_origen_foto"], "cohorte": v["anio_origen"], "anio": an, "periodo": pr,
                    "familia_T1": fam(v["codigo_origen_T1"]), "causa": causa, "actividad_en_periodo": activo, "estado_DA_actual": e})
    pd = a.priv_local / "fase3_sin_contexto_20261026/DETALLE_SIN_CONTEXTO.json"
    pd.write_text(json.dumps(det, ensure_ascii=False, indent=1)); pd.chmod(0o600)
    cnt = lambda *k: {"|".join(map(str, t)): n for t, n in sorted(collections.Counter(tuple(x[i] for i in k) for x in det).items())}
    out = {"clasificacion": "C diagnóstico; E causas por confirmar; no es deserción", "fecha_hora": dt.datetime.now().astimezone().isoformat(),
           "edicion_diccionario": d["edicion"], "posiciones_sin_contexto": len(det),
           "personas_vista": len(obj), "personas_vista_en_diccionario": len(obj & en_dic),
           "familias_carrera_en_diccionario": sorted(fam_dic, key=int),
           "por_causa": cnt("causa"), "por_causa_cohorte_periodo": cnt("causa", "cohorte", "anio", "periodo"),
           "por_causa_actividad_estado": cnt("causa", "actividad_en_periodo", "estado_DA_actual"),
           "por_causa_familia": cnt("causa", "familia_T1"),
           "fuentes_sha256": fuentes, "nota_truncamiento": "PROMEDIOS 12166 y 3233 tienen exactamente 70.000 filas (numeración 1–70.000).",
           "detalle_privado": {"ruta": str(PRIV / "fase3_sin_contexto_20261026/DETALLE_SIN_CONTEXTO.json"), "sha256": sha(pd)},
           "script_sha256": sha(Path(__file__))}
    (Path(__file__).parent / "DIAGNOSTICO_SIN_CONTEXTO.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps({k: out[k] for k in ("posiciones_sin_contexto", "personas_vista", "personas_vista_en_diccionario", "por_causa", "por_causa_actividad_estado")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
