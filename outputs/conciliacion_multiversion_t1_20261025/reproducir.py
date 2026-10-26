"""Reproduce y concilia la revisión multiversión T1 del Excel V5 contra la vista gobernada Fase 3.

Clasificación: B fuentes; C cálculo; D decisiones ya aprobadas en el diccionario v8; E pendientes.
No modifica fuentes, diccionario, Excel ni denominadores. Salidas solo agregadas (sin RUT/CODCLI).

Uso (Mac):
    python3 reproducir.py
Rutas alternativas: --vista, --v5, --manifest-fase3, --salida
"""
import argparse, csv, datetime as dt, hashlib, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl

GIT = Path("/Users/alexi/Documents/GitHub/avance_curricular")
DEF_VISTA = Path("/Users/alexi/.local/share/ipss/trazabilidad_integral_fase3_20261025/VISTA_T1_T2_T3.json")
DEF_V5 = Path("/Users/alexi/Desktop/IPSS_CONCILIACION_CARRERAS_UMAS_SIES_20261025_V5.xlsx")
DEF_MAN3 = GIT / "outputs/trazabilidad_integral_umas_sies_20261025/fase3/MANIFEST_FASE3.json"
ESPERADO = {  # hashes fijados en la auditoría del 25-10-2026
    "vista": "72edecb9507f46985533d1c63b83735beb4db58d743c89c226ca6be1a2c8ef31",
    "v5": "7b994d5596dcfc526da79811a17a81344c64c82011c7507c656e66f1fd23fb88",
}
PAT = re.compile(r"I162S(\d+)C(\d+)J(\d+)V(\d+)$")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def leer_v5(path):
    """Lee la tabla 'Revisión de planes con varias versiones' de la hoja 2_Catalogo_UMAS."""
    ws = openpyxl.load_workbook(path, read_only=True, data_only=False)["2_Catalogo_UMAS"]
    filas = list(ws.iter_rows(values_only=True))
    ini = next(i for i, r in enumerate(filas) if r and r[0] == "Plan UMAS" and r[5] == "Contextos")
    tabla = {}
    for r in filas[ini + 1:]:
        if not r or not r[0] or not PAT.match(str(r[3]).split("|")[0].strip() or "x"):
            break
        tabla[r[0]] = {
            "nombre": r[1], "candidatos": [x.strip() for x in str(r[3]).split("|")],
            "t1_listados": [x.strip() for x in str(r[4]).split("|")],
            "contextos": int(r[5]), "concordantes": int(r[6]), "pendientes": int(r[7]),
            "motivos": {k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", str(r[11] or ""))},
            "regla": str(r[12]),
        }
    return tabla


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vista", type=Path, default=DEF_VISTA)
    ap.add_argument("--v5", type=Path, default=DEF_V5)
    ap.add_argument("--manifest-fase3", type=Path, default=DEF_MAN3)
    ap.add_argument("--salida", type=Path, default=Path(__file__).resolve().parent)
    a = ap.parse_args()

    h = {"vista": sha256(a.vista), "v5": sha256(a.v5), "manifest_fase3": sha256(a.manifest_fase3)}
    for k in ESPERADO:
        if h[k] != ESPERADO[k]:
            sys.exit(f"ALTO: hash de {k} distinto del fijado ({h[k][:12]}); no se calcula.")
    man3 = json.loads(Path(a.manifest_fase3).read_text(encoding="utf-8"))
    vista_en_man3 = ESPERADO["vista"] in json.dumps(man3)

    vista = json.loads(Path(a.vista).read_text(encoding="utf-8"))
    ctx = [c for p in vista for c in (p.get("contextos") or [])]
    v5 = leer_v5(a.v5)

    J = lambda c: PAT.match(c).group(3) if PAT.match(c) else None
    por = defaultdict(Counter)
    for c in ctx:
        plan = c["plan_destino"]
        v = v5.get(plan)
        k = por[plan]
        k["contextos"] += 1
        rel, resp = c["relacion_codigo"], c["respaldo_destino"]
        # Medida gobernada (diccionario v8, Fase 3)
        k["gob_mismo_codigo_T1"] += rel == "MISMO_CODIGO"
        k["gob_otro_codigo_documental"] += rel == "CODIGO_DISTINTO_RESPALDADO" and resp.startswith("B")
        k["gob_otro_codigo_interno_D"] += rel == "CODIGO_DISTINTO_RESPALDADO" and resp.startswith("D")
        k["gob_pendiente_codigo_E"] += rel == "CODIGO_PENDIENTE"
        exc = bool(c["excepciones"])
        k["fase3_con_excepcion"] += exc
        k["fase3_excepcion_con_codigo"] += exc and rel != "CODIGO_PENDIENTE"
        if v is None:
            k["sin_fila_v5"] += 1
            continue
        en_cand = c["codigo_origen_T1"] in v["candidatos"]
        jornada_ok = J(c["codigo_origen_T1"]) == c["jornada_contexto"]
        exp_ok = bool(c["mismo_expediente_T1_atribuido"])
        # Motivos tal como los nombra V5
        k["mot_T1_fuera_de_candidatos"] += not en_cand
        k["mot_jornada_no_concordante"] += not jornada_ok
        k["mot_sin_atribucion_expediente"] += not exp_ok
        base = en_cand and jornada_ok and exp_ok
        # Regla uniforme: T1 + carrera + sede + jornada + plan (mismo código completo)
        unif = base and rel == "MISMO_CODIGO"
        k["uniforme_concordante"] += unif
        # Variante: además acepta cambio documentado solo de versión (contradice la regla declarada)
        var = base and (rel == "MISMO_CODIGO" or (rel == "CODIGO_DISTINTO_RESPALDADO" and set(c["componentes_distintos"]) <= {"version"}))
        k["variante_concordante"] += var
        k["solo_version_aceptada_variante"] += var and not unif

    filas, qa = [], []
    for plan in sorted(por):
        k, v = por[plan], v5.get(plan, {})
        n = k["contextos"]
        f = {
            "PLAN_UMAS": plan, "NOMBRE": v.get("nombre", ""), "REGLA_V5": v.get("regla", ""),
            "CONTEXTOS": n,
            "GOB_MISMO_CODIGO_T1": k["gob_mismo_codigo_T1"],
            "GOB_OTRO_CODIGO_DOCUMENTAL": k["gob_otro_codigo_documental"],
            "GOB_OTRO_CODIGO_INTERNO_D": k["gob_otro_codigo_interno_D"],
            "GOB_PENDIENTE_CODIGO_E": k["gob_pendiente_codigo_E"],
            "FASE3_CON_EXCEPCION": k["fase3_con_excepcion"],
            "FASE3_EXCEPCION_CON_CODIGO": k["fase3_excepcion_con_codigo"],
            "UNIFORME_CONCORDANTE": k["uniforme_concordante"],
            "UNIFORME_NO_CONCORDANTE": n - k["uniforme_concordante"],
            "V5_PUBLICADO_CONCORDANTE": v.get("concordantes"), "V5_PUBLICADO_PENDIENTE": v.get("pendientes"),
            "VARIANTE_SOLO_VERSION_CONCORDANTE": k["variante_concordante"],
            "SOLO_VERSION_ACEPTADA_VARIANTE": k["solo_version_aceptada_variante"],
            "V5_COINCIDE_CON": ("UNIFORME" if v.get("concordantes") == k["uniforme_concordante"] else
                                "VARIANTE_SOLO_VERSION" if v.get("concordantes") == k["variante_concordante"] else "NINGUNA"),
            "MOT_T1_FUERA_DE_CANDIDATOS": k["mot_T1_fuera_de_candidatos"],
            "MOT_JORNADA_NO_CONCORDANTE": k["mot_jornada_no_concordante"],
            "MOT_SIN_ATRIBUCION_EXPEDIENTE": k["mot_sin_atribucion_expediente"],
        }
        filas.append(f)
        mot = v.get("motivos", {})
        qa += [
            (f"{plan}: V5 publicado reproducido por una regla explícita", f["V5_COINCIDE_CON"] != "NINGUNA"),
            (f"{plan}: regla declarada en V5 coincide con la aplicada", f["V5_COINCIDE_CON"] == "UNIFORME" or "+ plan" not in f["REGLA_V5"]),
            (f"{plan}: V5 contextos", n == v.get("contextos")),
            (f"{plan}: motivos V5 reproducidos", all(mot.get(m, 0) == f["MOT_" + m.upper()] for m in ("T1_fuera_de_candidatos", "jornada_no_concordante", "sin_atribucion_expediente"))),
            (f"{plan}: uniforme = sin excepción Fase 3", f["UNIFORME_NO_CONCORDANTE"] == f["FASE3_CON_EXCEPCION"]),
            (f"{plan}: puente V5 = E + excepción con código − solo versión", f["V5_PUBLICADO_PENDIENTE"] == f["GOB_PENDIENTE_CODIGO_E"] + f["FASE3_EXCEPCION_CON_CODIGO"] - (f["SOLO_VERSION_ACEPTADA_VARIANTE"] if f["V5_COINCIDE_CON"] == "VARIANTE_SOLO_VERSION" else 0)),
        ]
    tot = Counter()
    for f in filas:
        for c, val in f.items():
            if isinstance(val, int):
                tot[c] += val
    qa += [
        ("Total contextos = 2.854", tot["CONTEXTOS"] == 2854),
        ("Gobernado 2.718 + 37 + 99 = 2.854", (tot["GOB_MISMO_CODIGO_T1"], tot["GOB_OTRO_CODIGO_DOCUMENTAL"] + tot["GOB_OTRO_CODIGO_INTERNO_D"], tot["GOB_PENDIENTE_CODIGO_E"]) == (2718, 37, 99)),
        ("20 planes V5 cubiertos", len(v5) == 20 and all(p in por for p in v5)),
        ("Sin contextos fuera de V5", tot["sin_fila_v5"] == 0 if "sin_fila_v5" in tot else True),
        ("Hash VISTA citado en MANIFEST_FASE3", vista_en_man3),
    ]
    informativos = [c for c, x in qa if "regla declarada" in c and not x]
    ok = all(x for c, x in qa if "regla declarada" not in c)

    sal = a.salida
    sal.mkdir(parents=True, exist_ok=True)
    out_csv = sal / "RESULTADO_POR_PLAN.csv"
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]), delimiter=";")
        w.writeheader(); w.writerows(filas)
        w.writerow({**{c: "" for c in filas[0]}, "PLAN_UMAS": "TOTAL", **{c: tot[c] for c in filas[0] if c in tot}})
    out_qa = sal / "QA.json"
    out_qa.write_text(json.dumps({"controles": [{"control": c, "ok": x} for c, x in qa], "todos_ok": ok, "hallazgos_informativos": informativos,
                                  "n_controles": len(qa), "n_ok": sum(1 for _, x in qa if x)}, ensure_ascii=False, indent=1), encoding="utf-8")
    manifest = {
        "fecha_hora": dt.datetime.now().astimezone().isoformat(),
        "clasificacion": "B fuentes; C reproducción y conciliación; D aprobaciones previas v8; E pendientes",
        "script": {"ruta": "outputs/conciliacion_multiversion_t1_20261025/reproducir.py", "sha256": sha256(Path(__file__))},
        "entradas": {"vista_fase3_privada": {"ruta": str(DEF_VISTA), "sha256": h["vista"]},
                      "excel_v5": {"ruta": str(DEF_V5), "hoja": "2_Catalogo_UMAS", "sha256": h["v5"]},
                      "manifest_fase3": {"ruta": str(DEF_MAN3), "sha256": h["manifest_fase3"]},
                      "diccionario": "v8_20261025_ocho_p (vía Fase 3)"},
        "salidas": {"RESULTADO_POR_PLAN.csv": sha256(out_csv), "QA.json": sha256(out_qa)},
        "identificadores_individuales_en_salidas": False,
        "modifica_fuentes_diccionario_excel_denominadores": False,
        "commit_push": False,
        "todos_ok": ok,
        "hallazgos_informativos": informativos,
    }
    (sal / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: tot[k] for k in tot}, ensure_ascii=False))
    print("QA", sum(1 for _, x in qa if x), "/", len(qa))
    for c, x in qa:
        if not x:
            print("FALLA:", c)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
