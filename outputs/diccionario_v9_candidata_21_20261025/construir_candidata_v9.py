"""Construye la edición CANDIDATA v9 del diccionario SIES de seguimiento (no la activa).

Integra como correspondencia interna (D) las 21 observaciones de TLOG/TAMD/TPAS/TCIB 2024
corroboradas en la revisión V3 (25-10-2026) y que en v8 figuran SIN_EVIDENCIA_ANUAL_APLICABLE.
Solo modifica los campos permitidos por common/diccionario_sies_seguimiento.aplicar_adjudicaciones.
La base v8 no se toca: se copia y se edita la copia, en carpeta privada fuera de Git.
Salidas del repositorio: solo agregados (sin RUT/CODCLI).
"""
import argparse, csv, datetime as dt, hashlib, json, shutil, sqlite3, sys
from collections import Counter
from pathlib import Path

PRIV = Path("/Users/alexi/.local/share/ipss")
V8 = PRIV / "fase3_candidata_20261025/DICCIONARIO_SIES_CANDIDATO.sqlite"
V8_SHA = "0f073554722a4c0ca9ffc11222aab2c83cd478a10f3bf31aefa8affeeae72c6b"
DESTINO = {"TLOG20241": "I162S2C79J4V1", "TAMD20241": "I162S2C78J4V1",
           "TPAS20241": "I162S2C57J4V1", "TCIB20241": "I162S2C47J4V1"}
PERMITIDOS = {"codigo_interno_adoptado", "estado_interno", "regla", "clasificacion", "requisito_pendiente"}
ESTADO = "CORRESPONDENCIA_INTERNA_CUATRO_PLANES_V3_APROBADA"
REGLA = "V3_TLOG_TAMD_TPAS_TCIB_2024_RE_O_J4V1_APROBADO_20261025"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--priv", type=Path, default=PRIV / "v9_candidata_21_20261025")
    ap.add_argument("--v8", type=Path, default=V8)
    ap.add_argument("--salida", type=Path, default=Path(__file__).resolve().parent)
    ap.add_argument("--trabajo", type=Path, default=None, help="carpeta local donde SQLite puede escribir su diario; por defecto --priv")
    a = ap.parse_args()
    if sha(a.v8) != V8_SHA:
        sys.exit("ALTO: la base v8 no coincide con el hash del descriptor activo.")
    ids = json.loads((a.priv / "OBSERVACIONES_21.json").read_text())
    oferta = {(r[0], r[1]): r for r in csv.reader(open(a.priv / "oferta_v5_hoja3.csv", encoding="utf-8")) if len(r) > 11}
    final = a.priv / "DICCIONARIO_SIES_CANDIDATO_V9.sqlite"
    if final.exists():
        sys.exit("ALTO: la candidata ya existe; no se sobrescribe.")
    trabajo = a.trabajo or a.priv
    trabajo.mkdir(parents=True, exist_ok=True)
    cand = trabajo / "DICCIONARIO_SIES_CANDIDATO_V9.sqlite"
    if cand.exists():
        sys.exit("ALTO: existe una candidata en la carpeta de trabajo.")
    shutil.copy2(a.v8, cand)
    db = sqlite3.connect(cand)
    ops, controles = [], Counter()
    for oid in ids:
        (payload,) = db.execute("SELECT payload FROM observaciones WHERE id=?", (oid,)).fetchone()
        p = json.loads(payload)
        plan, cod = p["plan"], DESTINO.get(p["plan"])
        # Requisitos de la revisión V3, verificados de nuevo sobre la propia observación
        ok = {
            "plan_foco": cod is not None,
            "pendiente_v8": p["estado_interno"] == "SIN_EVIDENCIA_ANUAL_APLICABLE" and not p["codigo_interno_adoptado"] and not p["codigo_documental_atribuible"],
            "candidato_unico_igual_destino": p["candidatos_calculados"] == [cod] and p["codigo_propuesto"] == cod,
            "sede_2_jornada_4": p["sede_dimension"] == "2" and p["jornada_sies"] == "4",
            "promedios_plan_anio_periodo": any(f["PLAN_DE_ESTUDIO"] == plan and f["ANO"] == p["ano"] and f["PERIODO"] == p["periodo"] for f in p["fuentes_promedios"]),
            "datos_alumnos_RE_O_carrera": any(c.get("SEDE") == "RE" and c.get("JORNADA") == "O" and c.get("CODCARPR") == p["carrera"] for c in p["contextos_DA"]),
            "oferta_del_anio": (p["ano"], cod) in oferta and str(oferta[(p["ano"], cod)][11]).startswith("Vigente"),
            "un_plan_en_expediente": p["planes_distintos_expediente"] == 1,
        }
        for k, v in ok.items():
            controles[k] += v
        if not all(ok.values()):
            db.close()
            sys.exit(f"ALTO: observación {oid} no cumple {[k for k, v in ok.items() if not v]}")
        antes = {k: p[k] for k in PERMITIDOS}
        despues = {
            "codigo_interno_adoptado": cod,
            "estado_interno": ESTADO,
            "regla": REGLA,
            "clasificacion": "D correspondencia interna aprobada; B/C PROMEDIOS, Datos Alumnos RE/O, sede 2/jornada 4 y oferta anual; E atribución documental",
            "requisito_pendiente": ("Atribución documental al expediente/período y aceptación SIES pendientes. Revisión V3 25-10-2026: "
                                    f"plan {plan} con actividad en PROMEDIOS para el período, Datos Alumnos RE/O, oferta {p['ano']} vigente para {cod}. "
                                    "No acredita fecha efectiva de migración ni envío T2/T3. Código T1 de cohorte conservado aparte; "
                                    "la discrepancia con el ancla T1 sigue siendo excepción (decisión opción A). Solo este contexto."),
        }
        p.update(despues)
        db.execute("UPDATE observaciones SET payload=? WHERE id=?", (json.dumps(p, ensure_ascii=False), oid))
        ops.append({"observacion_id": oid, "plan": plan, "anio": p["ano"], "periodo": p["periodo"],
                    "estado_antes": antes["estado_interno"], "estado_despues": ESTADO,
                    "codigo_antes": antes["codigo_interno_adoptado"], "codigo_despues": cod})
    db.commit(); db.close()
    (a.priv / "OPERACIONES_V9.json").write_text(json.dumps(ops, ensure_ascii=False, indent=1))

    # QA de conservación: v8 vs candidata, fila por fila
    d8 = sqlite3.connect(f"file:{a.v8}?mode=ro", uri=True); d9 = sqlite3.connect(f"file:{cand}?mode=ro", uri=True)
    r8 = dict(d8.execute("SELECT id, payload FROM observaciones")); r9 = dict(d9.execute("SELECT id, payload FROM observaciones"))
    cols8 = list(d8.execute("SELECT id,persona,codcli,plan,anio,periodo,carrera,sede,jornada FROM observaciones ORDER BY id"))
    cols9 = list(d9.execute("SELECT id,persona,codcli,plan,anio,periodo,carrera,sede,jornada FROM observaciones ORDER BY id"))
    mu8 = list(d8.execute("SELECT * FROM mu_anual ORDER BY rowid")); mu9 = list(d9.execute("SELECT * FROM mu_anual ORDER BY rowid"))
    cambiadas = [i for i in r8 if r8[i] != r9.get(i)]
    campos = Counter()
    for i in cambiadas:
        x, y = json.loads(r8[i]), json.loads(r9[i])
        campos.update(k for k in set(x) | set(y) if x.get(k) != y.get(k))
    est9 = Counter(json.loads(v)["estado_interno"] for v in r9.values())
    qa = {
        "observaciones_v8": len(r8), "observaciones_v9": len(r9),
        "cambiadas": len(cambiadas), "cambiadas_son_las_21": sorted(cambiadas) == sorted(ids),
        "campos_cambiados": dict(campos), "solo_campos_permitidos": set(campos) <= PERMITIDOS,
        "dimensiones_indexadas_identicas": cols8 == cols9, "mu_anual_identica": mu8 == mu9,
        "controles_requisitos_V3": dict(controles),
        "por_plan": dict(Counter(o["plan"] for o in ops)),
        "estado_SIN_EVIDENCIA_v8": Counter(json.loads(v)["estado_interno"] for v in r8.values())["SIN_EVIDENCIA_ANUAL_APLICABLE"],
        "estado_SIN_EVIDENCIA_v9": est9["SIN_EVIDENCIA_ANUAL_APLICABLE"],
    }
    qa["todos_ok"] = (qa["observaciones_v8"] == qa["observaciones_v9"] == 24774 and qa["cambiadas"] == 21
                      and qa["cambiadas_son_las_21"] and qa["solo_campos_permitidos"]
                      and qa["dimensiones_indexadas_identicas"] and qa["mu_anual_identica"]
                      and all(v == 21 for v in controles.values())
                      and qa["estado_SIN_EVIDENCIA_v8"] - qa["estado_SIN_EVIDENCIA_v9"] == 21)
    d8.close(); d9.close()
    if qa["todos_ok"] and cand != final:
        shutil.copyfile(cand, final)
    salida = a.salida; salida.mkdir(parents=True, exist_ok=True)
    (salida / "QA_CANDIDATA.json").write_text(json.dumps(qa, ensure_ascii=False, indent=1))
    man = {
        "fecha_hora": dt.datetime.now().astimezone().isoformat(),
        "estado": "CANDIDATA_NO_ACTIVA",
        "clasificacion": "D pendiente de autorización de promoción; C construcción y QA",
        "edicion_base": {"descriptor": "data/diccionario_sies_seguimiento/v8_20261025_ocho_p/descriptor.json",
                         "sha256": "701519d757779b3deaa618836bf862df29b9c0ef3e82dc45e5ec9c9b614764ef",
                         "base_privada": str(V8), "base_sha256": V8_SHA},
        "candidata": {"base_privada": str(PRIV / "v9_candidata_21_20261025/DICCIONARIO_SIES_CANDIDATO_V9.sqlite"), "sha256": sha(cand), "copia_final_identica": final.exists() and sha(final) == sha(cand)},
        "operaciones": {"ruta_privada": str(PRIV / "v9_candidata_21_20261025/OPERACIONES_V9.json"),
                        "sha256": sha(a.priv / "OPERACIONES_V9.json"), "n": len(ops), "regla": REGLA, "estado": ESTADO},
        "evidencia_revision_v3": "outputs/conciliacion_programas_cierres_20261025_v3 (LEEME, revisar_fuentes.py, evidencia_temporal_historica.json)",
        "script": {"ruta": "outputs/diccionario_v9_candidata_21_20261025/construir_candidata_v9.py", "sha256": sha(Path(__file__))},
        "qa": {"ruta": "QA_CANDIDATA.json", "sha256": sha(salida / "QA_CANDIDATA.json"), "todos_ok": qa["todos_ok"]},
        "activo_json_modificado": False, "commit_push": False, "denominadores_alterados": False,
    }
    (salida / "MANIFEST_CANDIDATA.json").write_text(json.dumps(man, ensure_ascii=False, indent=1))
    print(json.dumps(qa, ensure_ascii=False))
    sys.exit(0 if qa["todos_ok"] else 1)


if __name__ == "__main__":
    main()
