"""Consolida evidencia agregada de la Fase 2; no escribe fuentes ni diccionario."""
from pathlib import Path
import csv
import hashlib
import json
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
EXPECTED_HEAD = "8e2fb85bb8703758d6878681c9e2a29016e60c63"

def sha(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for block in iter(lambda: f.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()

def load(relative):
    return json.loads((OUT / relative).read_text())

def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()

def put(name, value):
    (OUT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n")

def main():
    now = datetime.now(ZoneInfo("America/Santiago")).isoformat()
    core = load("conciliacion/RESULTADOS.json")
    lineage = load("QA_LINEAJE_MU.json")
    early = load("brechas2022_2025/QA.json")
    late = load("brechas2026/QA_Y_MANIFEST.json")
    assert lineage["qa"] == "PASA"
    assert core["qa"]["diferencias_legacy"] == 0
    assert early["estado"] == "OK_TECNICO_CAUSAS_E"
    assert late["estado"] == "PASS_CON_CAUSAS_PENDIENTES"
    assert git("rev-parse", "HEAD") == EXPECTED_HEAD
    assert git("branch", "--show-current") == "feature/ire-2026"
    assert git("diff", "--cached", "--name-only") == ""

    # Controles de integridad sobre fuentes, productos anteriores y canon.
    prior = json.loads((OUT.parent/"fase1/CADENA_Y_FUENTES.json").read_text())
    preservation = []
    for p, expected in prior["preservacion"].items():
        actual = sha(p)
        preservation.append({"ruta": p, "sha256_antes": expected, "sha256_despues": actual, "sin_cambios": actual == expected})
    assert all(x["sin_cambios"] for x in preservation)
    for p, expected in core["fuentes_sha256"].items():
        assert sha(p) == expected
    child_hash_checks = []
    for folder, manifest, key in [("conciliacion", "MANIFEST.json", "salidas_sha256"), ("brechas2026", "QA_Y_MANIFEST.json", "archivos")]:
        for name, expected in load(f"{folder}/{manifest}")[key].items():
            actual = sha(OUT/folder/name)
            child_hash_checks.append({"archivo": f"{folder}/{name}", "coincide": actual == expected})
    assert all(x["coincide"] for x in child_hash_checks)

    with (OUT/"conciliacion/DETALLE_CONCILIACION.csv").open(encoding="utf-8-sig", newline="") as f:
        detail = list(csv.DictReader(f, delimiter=";"))
    assert len(detail) == 198
    forbidden = {"RUT", "N_DOC", "DV", "CODCLI", "NOMBRE", "PRIMER_APELLIDO", "FECH_NAC", "MRUN"}
    assert not (set(detail[0]) & forbidden)
    assert sum(int(r["MU_TOTAL_ESTRUCTURAL_UNION"]) for r in detail) == 10200
    assert sum(int(r["MU_IDENTIDAD_INCOMPLETA_FILAS"] or 0) for r in detail) == 0
    assert sum(int(r["MU_EXCESO_FILAS_SOBRE_PERSONAS"] or 0) for r in detail) == 0

    annual = []
    notes = {
        2022: "26 códigos publicados coinciden con VIG1; 1 código solo MU contiene 2 filas VIG0.",
        2023: "Dos códigos de C46 difieren -1 y +1; el neto cero no elimina la discrepancia por código.",
        2024: "27 códigos pregrado publicados coinciden con VIG1; 5 códigos solo MU contienen 6 filas VIG0.",
        2025: "43 códigos coinciden con MU total. Los 73 VIG0 explican aritméticamente la diferencia frente a VIG1, no el criterio de publicación aplicado por SIES.",
        2026: "48 códigos pregrado difieren: +228 y -2. Reproduce el cierre de julio; no se han acreditado las causas individuales.",
    }
    for year in range(2022, 2027):
        total = next(s for s in core["resumen_anual"] if s["ANIO"] == year and s["ALCANCE"] == "TOTAL_UNION")
        pre = next(s for s in core["resumen_anual"] if s["ANIO"] == year and s["ALCANCE"] == "Pregrado")
        relevant = [r for r in detail if int(r["ANIO"]) == year and r["ALCANCE"] == "Pregrado"]
        annual.append({
            "ANIO": year, "PUBLICACION_PREGRADO": pre["CSV_TOTAL"],
            "MU_TODAS_FILAS_BASE_SELECCIONADA": total["MU_TOTAL_FILAS"],
            "MU_VIG0": total["MU_VIG0"], "MU_VIG1": total["MU_VIG1"], "MU_VIG2": total["MU_VIG2"],
            "DIF_PREGRADO_MENOS_MU_VIG1": pre["CSV_TOTAL"]-total["MU_VIG1"],
            "CODIGOS_PREGRADO_CON_DIFERENCIA_VIG1": sum(int(r["DIF_CSV_VIG1_UNION"]) != 0 for r in relevant),
            "DIF_ABSOLUTA_CODIGOS_PREGRADO_VIG1": sum(abs(int(r["DIF_CSV_VIG1_UNION"])) for r in relevant),
            "POSTITULO_PUBLICACION_FUERA_BASE": total["CSV_TOTAL"]-pre["CSV_TOTAL"],
            "PERSONAS_DISTINTAS_MU_TIPO_DOC_DV": total["MU_PERSONAS_DISTINTAS_EN_ALCANCE"],
            "HALLAZGO": notes[year], "CLASE": "B/C; causa no acreditada E cuando corresponde",
        })
    with (OUT/"RESUMEN_EJECUTIVO.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(annual[0]), delimiter=";")
        writer.writeheader(); writer.writerows(annual)

    qa = {
        "clasificacion": "B/C", "fecha": now, "estado": "PASA_TECNICO_CON_BRECHAS_E_ABIERTAS",
        "lineaje_filas_8_campos": lineage["filas_totales"], "diferencias_lineaje": 0,
        "union_anio_codigo_completo": 198, "celdas_puente_previo_coincidentes": 990,
        "cotejo2026_publicacion": 66, "cotejo2026_institucional_pregrado": 63,
        "identidades_incompletas_en_MU": 0, "duplicados_identidad_dentro_mismo_anio_codigo": 0,
        "codigos_anio_pregrado_diferentes_vig1": sum(x["CODIGOS_PREGRADO_CON_DIFERENCIA_VIG1"] for x in annual),
        "preservacion": preservation, "hashes_subentregas": child_hash_checks,
        "exportacion": "Solo agregados, metadatos de fuentes y código; sin filas de identidad personal.",
        "git": {"rama": git("branch", "--show-current"), "HEAD_antes": EXPECTED_HEAD, "HEAD_despues": git("rev-parse", "HEAD"), "staged": [], "tracked_pendiente_preexistente": git("status", "--short", "--untracked-files=no"), "commit": False, "push": False},
        "limites": ["No se recalculó Excel ni retención; no cambió el filtro vigente de ningún indicador.", "No se acredita aceptación SIES ni atribución personal desde publicación agregada.", "No se actualizó la relación UMAS/CODCLI ni el diccionario: se conservan los cierres y pendientes anteriores.", "Linaje audita 8 campos clave, no los 32 campos de consolidación."]
    }
    put("QA_FASE2.json", qa)
    lines = [
        "# Fase 2/6 — Códigos individuales y conciliación anual", "",
        f"**B/C — Ejecutada:** {now}. IPSS 162, matrícula seleccionada 2022–2026; rama feature/ire-2026, HEAD `{EXPECTED_HEAD}`.",
        "**D — Alcance autorizado:** reutilizar códigos individuales y conciliar por año+código completo; revisar diferencias. Bases, diccionario, Excel, tasas y denominadores se conservan. Sin commit ni push.", "",
        "## Resultado ejecutivo", "",
        "**B/C:** se revisaron las 10.200 matrículas de la base seleccionada. Identidad, sede, carrera, jornada, versión y vigencia coinciden con sus fuentes primarias, en orden y como multiconjunto. La versión procede de cada registro individual; no se asignó distribuyendo los totales del CSV.",
        "**C:** código = I162S{COD_SED}C{COD_CAR}J{JOR}V{VERSION}; llave de conciliación = año informado + código completo. Se conserva la separación entre matrícula, personas únicas, primer año publicado y cohortes elegibles para retención.", "",
        "| Año | CSV SIES Pregrado | MU todas las filas | MU VIG=1 | Δ CSV−VIG1 | Códigos pregrado con Δ | Clase |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for r in annual:
        lines.append(f"| {r['ANIO']} | {r['PUBLICACION_PREGRADO']:,} | {r['MU_TODAS_FILAS_BASE_SELECCIONADA']:,} | {r['MU_VIG1']:,} | {r['DIF_PREGRADO_MENOS_MU_VIG1']:+,} | {r['CODIGOS_PREGRADO_CON_DIFERENCIA_VIG1']} | B/C |".replace(",", "."))
    lines += ["",
        "**C — Comparación uniforme:** la tabla mantiene VIG=1 en todos los años; no cambia de filtro para igualar cifras. MU todas incluye los seis códigos/año sin fila en el CSV (dos matrículas 2022 y seis 2024, todas VIG0); su nivel no se infiere del CSV. VIG=2 y otros valores suman cero en estas fuentes: por eso VIG=1 y VIG∈{1,2} coinciden numéricamente aquí, sin convertirlos en una regla universal.",
        "**B/C — Alcance separado:** Postítulo publicado suma 19 en 2023, 13 en 2024, 151 en 2025 y 54 en 2026. Está visible en el detalle, fuera de la base seleccionada de Pregrado. Ausente no se reemplaza por cero fuente: solo las columnas de unión usan un cero estructural explícito.", "",
        "## Diferencias revisadas", "",
        "- **B/C, 2022 y 2024:** los 26 y 27 códigos publicados de Pregrado coinciden exactamente con VIG1. Las diferencias frente a todas las filas son 5 y 86 VIG0, respectivamente. Los seis códigos/año exclusivos de MU tienen cero VIG1. Esto no demuestra una reasignación de versiones ni una aceptación individual por SIES.",
        "- **B/C, 2023:** `I162S2C46J1V1` tiene publicación 6 y MU VIG1 7; `I162S2C46J4V3`, publicación 173 y MU VIG1 172. Diferencias −1/+1, neto cero. **E:** falta el antecedente que identifique por qué difieren estos códigos; la compensación no prueba un traslado de una persona.",
        "- **B/C, 2025:** los 43 códigos de Pregrado coinciden contra MU total. Frente a VIG1 hay +73 en 11 códigos de ocho carreras. **E:** la igualdad con 73 VIG0 no prueba que la publicación incluyera esas mismas identidades ni explica el criterio aplicado. Se conserva el filtro actual de retención.",
        "- **B/C, 2026:** la brecha Pregrado sigue en +226, distribuida en 48 códigos (+228/−2); incluye dos códigos solo en CSV: `I162S2C77J1V1` con 1 e `I162S2C87J4V1` con 5. C6 y C79 tienen diferencias +1/−1 compensadas por carrera. **E:** no se acredita con estos agregados la causa individual ni una regla nueva para asignar versiones.",
        "- **B/C, cotejo del cierre de julio:** 66/66 totales publicados y 63/63 comparadores institucionales de Pregrado coinciden por código. Publicación 3.425 = 3.371 Pregrado + 54 Postítulo; institucional comparable 3.199 = 3.145 + 54. Por tanto 226 es la brecha ya conocida. Los 280 al comparar todo el CSV contra esta base Pregrado son 226 + 54 de distinto alcance; no se añade una nueva brecha de 54.",
        "- **B/E, documentación histórica:** se reproducen 990/990 números del puente previo. Su afirmación de que igualar totales por carrera explica una reclasificación jornada/versión excede esa evidencia. Se documenta aquí el límite y se conservan los archivos anteriores intactos.", "",
        "## Linaje de las fuentes individuales", "",
        "**B/C:** `QA_LINEAJE_MU.json` conserva ruta, hoja, hash y rango de filas por año. No exporta identificadores. En cada año las filas aparecen en el mismo orden y sin pérdidas: fila primaria = fila BASE − primera fila BASE del año + 2. El auditor comprueba también los multiconjuntos de claves y valores.",
        "| Año | Filas | Filas BASE | Filas fuente | Clase |", "|---|---:|---|---|---|",
    ]
    for c in lineage["controles"]:
        lines.append(f"| {c['anio']} | {c['filas_base']} | {c['rango_filas_base']} | {c['rango_filas_fuente']} | B/C |")
    lines += ["",
        "**C:** en 2025 se reproduce la transformación existente VIGENCIA ‘Vigente’→1 y ‘No vigente’→0: 2.298 y 73. La primera comprobación textual detectó esa diferencia de representación; la prueba corregida por la transformación documentada pasa sin cambios en los datos.",
        "**E:** el CSV público no contiene RUT ni CODCLI; no permite comparar conjuntos de personas con la publicación. La atribución UMAS por expediente y el estado de aceptación no se certifican mediante este control agregado. Se conservan el diccionario v8 y los resultados de la Fase 1; no se vuelven a adjudicar casos cerrados.", "",
        "## Archivos, QA y reanudación", "",
        "- **C:** `conciliacion/DETALLE_CONCILIACION.csv`: 198 combinaciones año+código, totales, vigencias, personas distintas, presencias y localizadores.",
        "- **C:** `conciliacion/SOLO_DIFERENCIAS.csv`: 118 filas con diferencia en al menos un comparador o presencia exclusiva; no equivale a 118 códigos de versión pendientes ni a 118 personas.",
        "- **C:** `RESUMEN_EJECUTIVO.csv`: cinco filas con lectura ejecutiva; `brechas2022_2025/` y `brechas2026/`: detalle y evidencia de las excepciones.",
        "- **C:** `QA_FASE2.json` y `MANIFEST_FASE2.json`: controles, rutas, hashes, scripts y preservación. No se creó otro Excel ni se recalculó el libro existente.",
        f"**B/C — QA:** linaje de 10.200 filas correcto en los ocho campos; 990/990 valores contra puente anterior; cero duplicados de identidad dentro de un mismo año+código. Una persona puede tener varios códigos, por lo que los totales anuales de matrícula no se sustituyen por personas únicas. Los {len(preservation)} archivos protegidos conservan hash, incluido el cambio previo de PROYECTO_IPSS.json; también se verificaron los hashes del CSV SIES y del puente anterior. No hubo commit/push; HEAD permanece igual.",
        "**E — Estado:** conciliación pedida ejecutada y técnicamente validada, con causas aún abiertas. No equivale a 100% de atribución UMAS↔SIES ni al cierre de las brechas. Para la siguiente fase, reutilizar el ancla individual preservada y el diccionario actual; revisar solo cambios de carrera/sede/jornada/plan T2/T3. No reasignar versiones para anular las diferencias ni reabrir la búsqueda completa por nombre.", "",
        "## Fuentes y hashes", "",
    ]
    for p, h in core["fuentes_sha256"].items():
        lines.append(f"- **B:** `{p}` — SHA-256 `{h}`.")
    lines += ["", "**B/C:** hashes de las cinco fuentes primarias, del libro y del diccionario en QA_LINEAJE_MU.json y QA_FASE2.json. Los roles de las fuentes se conservan: institucional granular seleccionada, derivado, publicación agregada y auditoría. Ninguno se transforma en prueba de aceptación SIES por su nombre de archivo."]
    (OUT/"INFORME_FASE2.md").write_text("\n".join(lines)+"\n")
    checkpoint = {
        "fecha": now, "clasificacion": "C/D/E", "fase": "2/6",
        "estado": "CONCILIACION_SOLICITADA_EJECUTADA_CON_CAUSAS_PENDIENTES",
        "hitos": [
            {"hito": "1/3", "accion": "Reutilizar códigos individuales y verificar linaje fuente→base", "resultado": "10200 filas, 8 campos, 0 diferencias", "evidencia": "QA_LINEAJE_MU.json", "pendiente": "No cambia atribuciones CODCLI ni acredita recepción SIES"},
            {"hito": "2/3", "accion": "Conciliar año+código completo contra publicación", "resultado": "198 combinaciones;990/990 valores previos reproducidos", "evidencia": "conciliacion/RESULTADOS.json", "pendiente": "Publicación agregada no ofrece identidad individual"},
            {"hito": "3/3", "accion": "Revisar diferencias preservando alcances", "resultado": "2023:2 códigos compensados;2025:11 códigos +73 vsVIG1;2026:48 códigos +226", "evidencia": "INFORME_FASE2.md", "pendiente": "Causas documentales individuales no acreditadas"},
        ],
        "no_repetir": ["Lectura completa histórica2007–2027", "Reasignación de versiones por totales", "Pruebas de retención anual ya cerradas", "Búsqueda de identidad aproximada"],
        "siguiente": "Fase3/6, según autorización: vista longitudinal y excepciones T2/T3 conservando los códigos de origen. No se ejecutó en esta entrega.",
        "prohibiciones_conservadas": ["Sin modificación de bases/denominadores/reglas", "Sin publicación de identificadores", "Sin commit/push"],
    }
    put("CHECKPOINT_FASE2.json", checkpoint)
    files = [p for p in OUT.rglob("*") if p.is_file() and p.name != "MANIFEST_FASE2.json" and "__pycache__" not in p.parts]
    put("MANIFEST_FASE2.json", {
        "clasificacion": "C", "fecha": now, "proceso": "Matrícula individual y publicación SIES; control para trazabilidad de retención IPSS162",
        "periodo_datos": "2022–2026", "fuentes_sha256": core["fuentes_sha256"],
        "constructor_anual_observado": {"ruta": str(ROOT/"scripts/construir_base_retencion_mu_2022_2026.py"), "sha256": sha(ROOT/"scripts/construir_base_retencion_mu_2022_2026.py")},
        "lineaje": "QA_LINEAJE_MU.json", "git": qa["git"],
        "archivos": {str(p.relative_to(OUT)): {"sha256": sha(p), "bytes": p.stat().st_size} for p in sorted(files)},
        "reglas": {"A": "No se agrega regla oficial", "B": "Conteos y campos observados", "C": "Lectura, normalización, composición y suma", "D": "Conservar bases y denominadores", "E": "Causas/aceptación/atribución personal no demostradas"},
        "privacidad": "Solo resultados agregados y código; identidad procesada únicamente en memoria.",
        "reproduccion": ["verificar_lineaje_mu.py", "conciliacion/conciliar_mu_csv.py --salida <carpeta nueva>", "brechas2022_2025/analizar_brechas.py", "brechas2026/conciliar_brecha_2026.py", "cerrar_fase2.py"],
        "estado": qa["estado"], "publicado": False,
    })
    print(json.dumps({"qa": qa["estado"], "anios": annual, "protegidos": len(preservation), "hash_informe": sha(OUT/"INFORME_FASE2.md"), "hash_manifest": sha(OUT/"MANIFEST_FASE2.json")}, ensure_ascii=False))

if __name__ == "__main__":
    main()
