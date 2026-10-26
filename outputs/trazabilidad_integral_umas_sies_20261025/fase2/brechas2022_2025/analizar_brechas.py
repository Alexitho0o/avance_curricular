#!/usr/bin/env python3
"""Audita agregados ya gobernados; no lee personas ni adjudica códigos SIES.

Alcance: publicación histórica contra MU 2022–2025. Reproduce diferencias
por código completo y carrera, conservando el sentido publicación menos MU.
"""
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
G = ROOT / "procesos/caracterizacion/gobernanza/sies"
SOURCES = {
    "puente": G / "TABLA_PUENTE_CSV_BASE_RETENCION_MU.csv",
    "resumen_carrera": G / "TABLA_PUENTE_CSV_BASE_RETENCION_MU_RESUMEN_POR_CARRERA.csv",
    "manifest_puente": G / "TABLA_PUENTE_CSV_BASE_RETENCION_MU.manifest.json",
    "manifest_publicacion": G / "MATRICULA_2007_2026.manifest.json",
    "manifest_mu": ROOT / "outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/MANIFEST_BASE_RETENCION_MU_2022_2026.json",
    "auditoria_vig_agregada": ROOT / "data/reglas_negocio/mu2027/estudio/RESULTADOS_AGREGADOS.json",
    "auditoria_vig_informe": ROOT / "data/reglas_negocio/mu2027/estudio/AUDITORIA_VIG_ENVIOS_RETENCION.md",
    "readme_hito": ROOT / "manifests/milestones/H001-RETENCION-IPSS162/README.md",
    "conciliacion_actual": OUT.parent / "conciliacion/RESULTADOS.json",
    "detalle_conciliacion_actual": OUT.parent / "conciliacion/DETALLE_CONCILIACION.csv",
}


def fingerprint(path):
    return sha256(path.read_bytes()).hexdigest()


def read_csv(path, delimiter=","):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=delimiter))


def dump(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def number(value):
    n = float(value)
    assert n.is_integer()
    return int(n)


def table(headers, rows):
    return "| " + " | ".join(headers) + " |\n| " + " | ".join(["---"] * len(headers)) + " |\n" + "\n".join("| " + " | ".join(str(v) for v in row) + " |" for row in rows)


before = {k: fingerprint(p) for k, p in SOURCES.items()}
raw = read_csv(SOURCES["puente"])
summaries = read_csv(SOURCES["resumen_carrera"])
manifest = json.loads(SOURCES["manifest_puente"].read_text())
vig_audit = json.loads(SOURCES["auditoria_vig_agregada"].read_text())
current = {(int(r["ANIO"]), r["CODIGO_COMPLETO"]): r for r in read_csv(SOURCES["detalle_conciliacion_actual"], ";")}
assert len(raw) == 198 and len(summaries) == 79
assert before["puente"] == manifest["salidas"]["csv_sha256"]
assert before["resumen_carrera"] == manifest["salidas"]["csv_resumen_carrera_sha256"]
numeric = ["TOTAL_MATRICULA_CSV", "BASE_TOTAL_FILAS", "BASE_VIG1", "DIFERENCIA_VS_TOTAL", "DIFERENCIA_VS_VIG1"]
rows, outside = [], []
for line, r in enumerate(raw, 2):
    y = int(r["ANIO"])
    if y not in range(2022, 2026):
        continue
    z = {**r, **{k: number(r[k]) for k in numeric}}
    z.update(ANIO=y, COD_CAR=int(r["COD_CAR"]), JOR=int(r["JOR"]), VERSION=int(r["VERSION"]), COD_SED=int(r["COD_SED"]), fila_csv=line)
    fresh = current[y, r["CODIGO_CARRERA_CSV"]]
    for previous, actual in [("TOTAL_MATRICULA_CSV", "CSV_TOTAL_ESTRUCTURAL_UNION"), ("BASE_TOTAL_FILAS", "MU_TOTAL_ESTRUCTURAL_UNION"), ("BASE_VIG1", "MU_VIG1_ESTRUCTURAL_UNION"), ("DIFERENCIA_VS_TOTAL", "DIF_CSV_MU_TOTAL_UNION"), ("DIFERENCIA_VS_VIG1", "DIF_CSV_VIG1_UNION")]:
        assert z[previous] == number(fresh[actual])
    # Cero estructural solo cuando la fuente declara ausencia de filas MU;
    # un campo ausente dentro de una fila MU presente sigue siendo un error.
    state_counts = {dest: number(fresh[src]) if fresh["MU_PRESENTE"] == "True" else 0 for dest, src in [("MU_VIG0", "MU_VIG0_FILAS"), ("MU_VIG2", "MU_VIG2_FILAS"), ("MU_VIG_OTROS", "MU_VIG_OTROS_FILAS")]}
    z.update(**state_counts, alcance_actual=fresh["ALCANCE"], PRESENCIA=fresh["PRESENCIA"], CSV_PRESENTE=fresh["CSV_PRESENTE"] == "True")
    z["TOTAL_MATRICULA_CSV_PUBLICADO"] = z["TOTAL_MATRICULA_CSV"] if z["CSV_PRESENTE"] else None
    assert z["DIFERENCIA_VS_TOTAL"] == z["TOTAL_MATRICULA_CSV"] - z["BASE_TOTAL_FILAS"]
    assert z["DIFERENCIA_VS_VIG1"] == z["TOTAL_MATRICULA_CSV"] - z["BASE_VIG1"]
    (outside if r["NIVEL_GLOBAL"] == "Postítulo" else rows).append(z)
assert len({(r["ANIO"], r["CODIGO_CARRERA_CSV"]) for r in rows}) == len(rows)
groups = defaultdict(list)
for r in rows:
    groups[r["ANIO"], r["COD_CAR"]].append(r)
career_results = []
for key, group in sorted(groups.items()):
    y, career = key
    totals = {k: sum(r[k] for r in group) for k in numeric}
    reference = next(r for r in summaries if int(r["ANIO"]) == y and int(r["COD_CAR"]) == career)
    assert all(totals[k] == number(reference[k]) for k in numeric)
    d = [r["DIFERENCIA_VS_VIG1"] for r in group]
    career_results.append({"anio": y, "cod_car": career, "nombre": reference["NOMBRE_CARRERA"], **totals,
        "codigos_union": len(group), "codigos_diferentes_vig1": sum(x != 0 for x in d),
        "diferencia_positiva_vig1": sum(max(0, x) for x in d), "diferencia_negativa_vig1": sum(min(0, x) for x in d),
        "compensacion_aritmetica": bool(any(x > 0 for x in d) and any(x < 0 for x in d)),
        "clasificacion": "B/C", "causa_reclasificacion_confirmada": False})

annual = []
for y in range(2022, 2026):
    group = [r for r in rows if r["ANIO"] == y]
    totals = {k: sum(r[k] for r in group) for k in numeric}
    audit = vig_audit["base_por_anio"][str(y)]
    assert totals["BASE_TOTAL_FILAS"] == audit["registros"]
    assert totals["BASE_VIG1"] == audit["VIG"]["1"]
    assert sum(r["MU_VIG0"] for r in group) == audit["VIG"].get("0", 0)
    assert sum(r["MU_VIG2"] for r in group) == audit["VIG"].get("2", 0)
    assert sum(r["MU_VIG_OTROS"] for r in group) == 0
    v2 = audit["VIG"].get("2", 0)
    annual.append({"anio": y, "codigos_union_pregrado_o_solo_mu": len(group), **totals,
        "codigos_diferentes_total": sum(r["DIFERENCIA_VS_TOTAL"] != 0 for r in group),
        "codigos_diferentes_vig1": sum(r["DIFERENCIA_VS_VIG1"] != 0 for r in group),
        "filas_vig0_auditoria_previa": audit["VIG"].get("0", 0), "filas_vig2_auditoria_previa": v2,
        "base_vig1_o_2_auditoria_previa": totals["BASE_VIG1"] + v2,
        "fuente_vig0_y_vig2": "auditoria_vig_agregada#base_por_anio y nueva conciliacion_actual/DETALLE_CONCILIACION.csv; sin lectura individual en este subestudio",
        "postitulo_excluido_csv": sum(r["TOTAL_MATRICULA_CSV"] for r in outside if r["ANIO"] == y),
        "clasificacion": "B/C"})

exceptions = []
for r in rows:
    if not (r["DIFERENCIA_VS_TOTAL"] or r["DIFERENCIA_VS_VIG1"]):
        continue
    if r["ANIO"] == 2023 and r["DIFERENCIA_VS_VIG1"]:
        state, pending = "COMPENSACION_ARITMETICA_C46_CAUSA_E", "Falta respaldo que explique el -1/+1; no se identificó una transferencia individual de jornada/version."
    elif r["ANIO"] == 2025:
        state, pending = "COINCIDE_TOTAL_DIFIERE_VIG1", "Igualdad con total MU observada; falta acreditar por qué publicación y VIG difieren. No prueba que las mismas personas VIG0 fueran publicadas."
    else:
        state, pending = "COINCIDE_VIG1_DIFIERE_TOTAL", "La diferencia aritmética se asocia al filtro VIG. No acredita causa académica ni reclasificación individual."
    exceptions.append({k: r[k] for k in ["ANIO", "CODIGO_CARRERA_CSV", "COD_SED", "COD_CAR", "JOR", "VERSION", "NOMBRE_CARRERA", "NIVEL_GLOBAL", "PRESENCIA", "CSV_PRESENTE", "TOTAL_MATRICULA_CSV_PUBLICADO", *numeric, "MU_VIG0", "MU_VIG2", "MU_VIG_OTROS", "alcance_actual", "fila_csv"]} |
        {"estado": state, "clasificacion_conteos": "B", "clasificacion_metodo": "C", "clasificacion_causa": "E", "pendiente": pending})

assert sum(r["DIFERENCIA_VS_VIG1"] for r in exceptions if r["ANIO"] == 2025) == 73
assert len([r for r in exceptions if r["ANIO"] == 2025]) == 11
assert len({r["COD_CAR"] for r in exceptions if r["ANIO"] == 2025}) == 8
assert [(x["anio"], x["cod_car"]) for x in career_results if x["compensacion_aritmetica"]] == [(2023, 46)]
source_index = [{"id": k, "ruta": str(p), "sha256": before[k], "tipo": "auditoria_agregada_previa" if k.startswith("auditoria") else "fuente_documental_agregada"} for k, p in SOURCES.items()]
original_check = []
for key in ["puente", "resumen_carrera", "manifest_puente", "manifest_publicacion"]:
    original = Path("/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/gobernanza/sies") / SOURCES[key].name
    if original.exists():
        match = fingerprint(original) == before[key]
        assert match
        original_check.append({"id": key, "ruta_origen": str(original), "sha256": before[key], "identico_a_copia_integrada": match})
after = {k: fingerprint(p) for k, p in SOURCES.items()}
assert before == after
result = {"fase": "2/6", "clasificacion": "B/C/E", "alcance": "Matrícula agregada IPSS162, años2022–2025; no retención ni personas individuales",
    "metodo": "Diferencia=publicación−MU; código completo y luego ANIO+COD_CAR; Postítulo visible fuera de alcance",
    "ceros_estructurales": "TOTAL_MATRICULA_CSV conserva el cero de la unión si no existe fila publicada. CSV_PRESENTE=false y TOTAL_MATRICULA_CSV_PUBLICADO=null distinguen ausencia de un cero publicado. Las diferencias usan el cero estructural sin afirmar una matrícula publicada de cero.",
    "fecha_ejecucion": datetime.now(timezone.utc).isoformat(), "regla_fuente": "Se conserva VIG1 del puente; VIG1o2 se informa separado. VIG2=0 solo según auditoría de estas fuentes/años.",
    "anual": annual, "carreras": career_results, "excepciones_por_codigo": exceptions,
    "postitulo_fuera_alcance": [{k: r[k] for k in ["ANIO", "CODIGO_CARRERA_CSV", "TOTAL_MATRICULA_CSV", "BASE_TOTAL_FILAS", "fila_csv"]} for r in outside],
    "compensaciones": [r for r in career_results if r["compensacion_aritmetica"]],
    "fuentes": source_index, "copias_integradas": original_check,
    "pendientes": ["E: causa del -1/+1 de C46 en2023.", "E: procedencia/metodología de las73 diferencias de2025; igualdad agregada no acredita publicación de filas VIG0 concretas.", "E: fecha efectiva y alcance de las extracciones históricas; fechas de nombre/FECH_CAR no prueban corte de matrícula.", "E: no nueva decisión de códigos/versiones ni cierre documental individual por esta conciliación."],
    "qa": {"filas_puente": len(raw), "filas_resumen_carrera": len(summaries), "filas_analizadas": len(rows), "carreras_anio_analizadas": len(career_results),
        "excepciones": len(exceptions), "formulas_diferencia_reproducidas": len(rows) * 2,
        "comparaciones_resumen_carrera": len(career_results) * len(numeric), "comparaciones_con_reconstruccion_actual": (len(rows) + len(outside)) * len(numeric), "fuentes_sin_cambios": before == after,
        "identificadores_personales_exportados": False, "denominadores_modificados": False, "estado": "OK_TECNICO_CAUSAS_E"}}
dump("EXCEPCIONES_Y_FUENTES.json", result)
dump("QA.json", result["qa"])

lines = ["# Brechas agregadas de matrícula 2022–2025", "", "B/C — Fase 2/6, diagnóstico de fuentes agregadas. No modifica Excel, fuentes, códigos ni denominadores. Diferencias expresadas como publicación menos MU. Los conteos son registros de matrícula agregados, no personas deduplicadas ni tasas de retención.", "", "## Resultado por año", "", table(["Año", "Códigos", "Publicación pregrado", "MU total", "MU VIG1", "Δ total", "Δ VIG1", "Códigos Δ VIG1", "Clase"], [[r["anio"], r["codigos_union_pregrado_o_solo_mu"], r["TOTAL_MATRICULA_CSV"], r["BASE_TOTAL_FILAS"], r["BASE_VIG1"], r["DIFERENCIA_VS_TOTAL"], r["DIFERENCIA_VS_VIG1"], r["codigos_diferentes_vig1"], "B/C"] for r in annual]), "", "B/C — En 2022 y 2024 los códigos publicados coinciden contra VIG1; los códigos solo MU tienen cero filas VIG1. No hay compensación entre códigos bajo ese filtro y esto no acredita una equivalencia individual del 100%. En 2023 solo C46 presenta -1 y +1 entre dos códigos: se compensan al agregar carrera. En 2025 los43 códigos de pregrado coinciden contra MU total;11 códigos de8 carreras difieren contra VIG1 en73 registros.", "", "## Compensación exacta 2023", "", table(["Código", "Publicación", "MU total", "MU VIG1", "Δ total", "Δ VIG1", "Clase"], [[r["CODIGO_CARRERA_CSV"], r["TOTAL_MATRICULA_CSV"], r["BASE_TOTAL_FILAS"], r["BASE_VIG1"], r["DIFERENCIA_VS_TOTAL"], r["DIFERENCIA_VS_VIG1"], "B/C; causa E"] for r in rows if r["ANIO"] == 2023 and r["COD_CAR"] == 46]), "", "E — La coincidencia de C46 a nivel carrera no demuestra qué matrícula cambió de código ni que ocurrió una reclasificación. Cambian a la vez jornada y versión entre los dos códigos con diferencia; no se asigna una causa por ese patrón.", "", "## Diferencia de73 en2025 por carrera", "", table(["COD_CAR", "Carrera", "Publicación", "MU total", "MU VIG1", "Δ VIG1", "Clase"], [[r["cod_car"], r["nombre"], r["TOTAL_MATRICULA_CSV"], r["BASE_TOTAL_FILAS"], r["BASE_VIG1"], r["DIFERENCIA_VS_VIG1"], "B/C; causa E"] for r in career_results if r["anio"] == 2025 and r["DIFERENCIA_VS_VIG1"]]), "", "B — La auditoría agregada preservada en data/reglas_negocio/mu2027/estudio/RESULTADOS_AGREGADOS.json registra VIG0=5,3,86,73 para2022–2025 y ningún VIG2. También documenta0 cambios VIG entre fuentes anuales y base consolidada, incluido alias2025 VIGENCIA→VIG. Son resultados de esa auditoría previa; este subestudio no relee personas. C — Por esas fuentes concretas, VIG1 y VIG1o2 dan el mismo conteo; no son una regla universal intercambiable.", "", "E — Que publicación2025 coincida con totalMU no permite afirmar que SIES publicó exactamente a las73 personas/filas VIG0. Falta una trazabilidad de carga/publicación o criterio que lo explique; tampoco son automáticamente errores de vigencia. El estudio de nóminas2026 no se extrapola retrospectivamente a2025.", "", "## Todas las diferencias por código", "", table(["Año", "Código", "Presencia", "Publicación", "MU total", "MU VIG1", "Δ total", "Δ VIG1", "Clase"], [[r["ANIO"], r["CODIGO_CARRERA_CSV"], r["PRESENCIA"], r["TOTAL_MATRICULA_CSV_PUBLICADO"] if r["CSV_PRESENTE"] else "Ausente", r["BASE_TOTAL_FILAS"], r["BASE_VIG1"], r["DIFERENCIA_VS_TOTAL"], r["DIFERENCIA_VS_VIG1"], "B/C; causa E"] for r in exceptions]), "", "C — Ausente significa que no existe fila de ese código/año en el CSV publicado. Para calcular la diferencia de la unión se usa un cero estructural, no una matrícula publicada igual a cero. El JSON conserva ambos conceptos por separado. AMBAS indica presencia en las dos fuentes; SOLO_MU, presencia únicamente en MU.", "", "## Alcance y documentación previa", "", "B/C — Los códigos presentes solo enMU de2022/2024 tienen cero VIG1, de modo que la diferencia corresponde al filtro observado; no se necesita afirmar una reclasificación para reconciliar los conteos. Postítulo se conserva aparte y no se suma a MU pregrado. El detalle está en EXCEPCIONES_Y_FUENTES.json.", "", "B/E — El manifiesto del puente, su resumen por carrera y README H001 de30-sep afirman que las diferencias eran reclasificación jornada/versión y que todas las causas salvo2025 estaban explicadas. La reproducción confirma sus números pero no esa causalidad: para2022/2024 no hay diferencias frente aVIG1 entre los códigos publicados y los solo MU tienen cero VIG1; para2023 hay compensación aritmética cuya causa sigue pendiente. Se conserva íntegra la evidencia anterior y se documenta aquí su límite, sin reescribirla.", "", "B/E — El manifiesto de consolidación registra FECHA_MATRICULA ausente en2022/2023, FECH_CAR descartada en2022/2024/2025 y columnas distintas por edición. No convierte la fecha de generación/exportación en fecha efectiva de matrícula. Este subestudio no acredita nuevos cortes temporales.", "", "## QA y fuentes", "", f"C — QA técnico: {len(rows)} códigos/año; {len(exceptions)} excepciones; {len(career_results)} agregados carrera/año reproducen las cinco columnas numéricas del resumen gobernado. No se exportaron identificadores. Hashes antes/después idénticos. Fuentes y copia integrada/original verificadas en el JSON.", ""]
for source in source_index:
    lines.extend([f"- B — `{source['id']}`: `{source['ruta']}`; SHA-256 `{source['sha256']}`."])
lines.extend(["", "B/C — Contraste adicional con la nueva reconstrucción de esta Fase 2: DETALLE_CONCILIACION.csv confirma las cinco columnas numéricas en 132 códigos/año de 2022–2025 (660 comparaciones, incluidos 9 códigos Postítulo). También confirma VIG0 y ausencia de VIG2/otros por año. Este subestudio consume sus agregados y no vuelve a leer datos individuales.", "", "B — Localizadores: puente CSV, filas originales indicadas en cada excepción JSON; manifiesto del puente, cierre_carrera_2026_09_30 y qa.detalle; README H001 líneas 99–117; auditoría de vigencia, RESULTADOS_AGREGADOS.json → base_por_anio/fuentes_anuales_vig y AUDITORIA_VIG_ENVIOS_RETENCION.md líneas 53–66. E — La causa se declara no acreditada en este conjunto específico de evidencias, no inexistente universalmente.", "", "C — Reproducción: ejecutar analizar_brechas.py desde cualquier directorio con Python 3. Usa únicamente CSV/JSON/Markdown agregados ya disponibles; no modifica entradas. No ejecuta commit ni push.", ""])
report = "\n".join(lines)
for old, new in {
    "los43": "los 43", ";11": "; 11", "de8": "de 8", "en73": "en 73", "de73": "de 73", "en2025": "en 2025", "para2022": "para 2022", "documenta0": "documenta 0", "alias2025": "alias 2025", "VIG1o2": "VIG1 o 2", "publicación2025": "publicación 2025", "totalMU": "total MU", "las73": "las 73", "nóminas2026": "nóminas 2026", "a2025": "a 2025", "enMU": "en MU", "de2022": "de 2022", "de30-sep": "de 30-sep", "salvo2025": "salvo 2025", "para2023": "para 2023", "aVIG1": "a VIG1", "en2022": "en 2022", "en2024": "en 2024"
}.items():
    report = report.replace(old, new)
(OUT / "INFORME_BRECHAS.md").write_text(report, encoding="utf-8")
print(json.dumps(result["qa"], ensure_ascii=False))
