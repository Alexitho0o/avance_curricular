# -*- coding: utf-8 -*-
# Comparacion de hallazgos de validacion: v1 (20260827) vs v2/rector_v2 (20260828)
import json, os
from collections import Counter, defaultdict

BASE = os.path.expanduser("~/mnt/avance_curricular/oferta_academica_2027")
VAL_DIR = os.path.join(BASE, "06_validaciones")

v1 = json.load(open(os.path.join(VAL_DIR, "VALIDACION_COMPLETA_ETAPA2_20260827.json"), encoding="utf-8"))
v2 = json.load(open(os.path.join(VAL_DIR, "VALIDACION_COMPLETA_ETAPA2_20260828_rector_v2.json"), encoding="utf-8"))

def agg(hallazgos):
    d = defaultdict(lambda: Counter())
    for h in hallazgos:
        d[h["campo"]][h["severidad"]] += 1
    return d

a1 = agg(v1["hallazgos"])
a2 = agg(v2["hallazgos"])

campos = sorted(set(a1.keys()) | set(a2.keys()))
comparacion = []
for c in campos:
    c1 = a1.get(c, Counter())
    c2 = a2.get(c, Counter())
    n1 = sum(c1.values())
    n2 = sum(c2.values())
    if n1 > 0 and n2 == 0:
        estado = "RESUELTO"
    elif n1 == 0 and n2 > 0:
        estado = "NUEVO"
    elif n1 > 0 and n2 > 0 and n2 < n1:
        estado = "PARCIALMENTE_RESUELTO"
    elif n1 > 0 and n2 > 0 and n2 == n1:
        estado = "PERSISTENTE_SIN_CAMBIO"
    elif n1 > 0 and n2 > n1:
        estado = "EMPEORO"
    else:
        estado = "SIN_HALLAZGOS"
    comparacion.append({
        "campo": c,
        "v1_bloqueante": c1.get("BLOQUEANTE",0), "v1_revision_manual": c1.get("REVISION_MANUAL",0), "v1_informativo": c1.get("INFORMATIVO",0), "v1_advertencia": c1.get("ADVERTENCIA",0), "v1_total": n1,
        "v2_bloqueante": c2.get("BLOQUEANTE",0), "v2_revision_manual": c2.get("REVISION_MANUAL",0), "v2_informativo": c2.get("INFORMATIVO",0), "v2_advertencia": c2.get("ADVERTENCIA",0), "v2_total": n2,
        "estado": estado,
    })

out = {
    "resumen_severidad_v1": v1["resumen"], "resumen_severidad_v2": v2["resumen"],
    "total_hallazgos_v1": len(v1["hallazgos"]), "total_hallazgos_v2": len(v2["hallazgos"]),
    "filas_evaluadas_v1": v1["total_filas_evaluadas"], "filas_evaluadas_v2": v2["total_filas_evaluadas"],
    "filas_con_bloqueante_v1": len(set(h["fila_excel"] for h in v1["hallazgos"] if h["severidad"]=="BLOQUEANTE")),
    "filas_con_bloqueante_v2": len(set(h["fila_excel"] for h in v2["hallazgos"] if h["severidad"]=="BLOQUEANTE")),
    "comparacion_por_campo": comparacion,
}
json_path = os.path.join(VAL_DIR, "COMPARACION_HALLAZGOS_V1_VS_V2_20260828.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

tsv_path = os.path.join(VAL_DIR, "COMPARACION_HALLAZGOS_V1_VS_V2_20260828.tsv")
cols = ["campo","v1_bloqueante","v1_revision_manual","v1_informativo","v1_advertencia","v1_total","v2_bloqueante","v2_revision_manual","v2_informativo","v2_advertencia","v2_total","estado"]
with open(tsv_path, "w", encoding="utf-8") as f:
    f.write("\t".join(cols) + "\n")
    for r in comparacion:
        f.write("\t".join(str(r.get(c,"")) for c in cols) + "\n")

print("Resumen v1:", v1["resumen"], "| filas c/bloqueante:", out["filas_con_bloqueante_v1"], "/", v1["total_filas_evaluadas"])
print("Resumen v2:", v2["resumen"], "| filas c/bloqueante:", out["filas_con_bloqueante_v2"], "/", v2["total_filas_evaluadas"])
print()
for r in comparacion:
    if r["estado"] != "SIN_HALLAZGOS":
        print(f"{r['campo']:35s} v1={r['v1_total']:3d} v2={r['v2_total']:3d}  {r['estado']}")
print("JSON:", json_path)
print("TSV:", tsv_path)
