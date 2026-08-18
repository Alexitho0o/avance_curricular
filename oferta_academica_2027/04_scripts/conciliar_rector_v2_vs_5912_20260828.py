# -*- coding: utf-8 -*-
# Fase 4: Conciliacion Etapa 2 (archivo institucional) vs reporte 5912 (Etapa 1 validada)
import csv, json, os, re, unicodedata, difflib
import openpyxl

BASE = os.path.expanduser("~/mnt/avance_curricular/oferta_academica_2027")
INST = os.path.join(BASE, "03_fuentes_institucionales/entregas_docencia/20260828_etapa2_entrega_02/Oferta 2027 Etapa2_rector_v2.xlsx")
R5912 = os.path.join(BASE, "09_respaldo/reportes_pes_validados/20260824_reporte_5912_etapa1/5912 Oferta Académica Vigente Validada 2027 TP Adscritas.csv")
OUT = os.path.join(BASE, "06_validaciones")
STAMP = "20260828_rector_v2"

def norm(s):
    if s is None:
        return ""
    s = str(s).strip().upper()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"\s+", " ", s)
    return s

# --- cargar archivo institucional (filas reales 2-51) ---
wb = openpyxl.load_workbook(INST, data_only=True)
ws = wb["Hoja4"]
headers = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1)]
idx = {h: i for i, h in enumerate(headers)}

inst_rows = []
for r in range(2, ws.max_row + 1):  # filas reales 2-51 (52-55 vacias, confirmado en perfilamiento)
    vals = [ws.cell(row=r, column=c).value for c in range(1, ws.max_column + 1)]
    if all(v is None for v in vals):
        continue
    row = dict(zip(headers, vals))
    row["_fila_excel"] = r
    inst_rows.append(row)

# --- cargar 5912 ---
with open(R5912, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f, delimiter=";")
    rep_rows = list(reader)

def key_full(sede, carrera, modalidad, jornada, tipoplan, nivel, titulo):
    return (norm(sede), norm(carrera), str(modalidad), str(jornada), str(tipoplan), str(nivel), norm(titulo))

rep_index = {}
rep_by_sede_carrera = {}
sede_catalog = {}  # cod_sede -> set(nombre_sede)
for rr in rep_rows:
    k = key_full(rr.get("NOMBRE_SEDE"), rr.get("NOMBRE_CARRERA"), rr.get("MODALIDAD"), rr.get("COD_JORNADA"), rr.get("COD_TIPO_PLAN_CARRERA"), rr.get("COD_NIVEL_CARRERA"), rr.get("NOMBRE_TITULO"))
    rep_index.setdefault(k, []).append(rr)
    sc = (norm(rr.get("NOMBRE_SEDE")), norm(rr.get("NOMBRE_CARRERA")))
    rep_by_sede_carrera.setdefault(sc, []).append(rr)
    cs = str(rr.get("COD_SEDE"))
    sede_catalog.setdefault(cs, set()).add(norm(rr.get("NOMBRE_SEDE")))

detalle = []
resumen_counts = {}

for row in inst_rows:
    fila = row["_fila_excel"]
    sede = row.get("NOMBRE_SEDE"); cod_sede = row.get("COD_SEDE")
    carrera = row.get("NOMBRE_CARRERA"); modalidad = row.get("MODALIDAD")
    jornada = row.get("COD_JORNADA"); tipoplan = row.get("COD_TIPO_PLAN_CARRERA")
    nivel = row.get("COD_NIVEL_CARRERA"); titulo = row.get("NOMBRE_TITULO")

    k_full = key_full(sede, carrera, modalidad, jornada, tipoplan, nivel, titulo)
    exact = rep_index.get(k_full)

    clasificacion = None
    razon = None
    lado_5912 = ""

    if exact:
        clasificacion = "POSIBLE_DUPLICADO_ETAPA1"
        razon = "Coincidencia EXACTA de llave diagnostica (sede+carrera+modalidad+jornada+tipo_plan+nivel+titulo) con un registro de la Oferta Vigente Validada (reporte 5912). El instructivo (Anexo4, pag.63) advierte: 'La Carrera o Programa que esta ingresando como nueva, ya existe en la Oferta Vigente Validada.'"
        lado_5912 = "; ".join(f"{k}={v}" for k, v in exact[0].items() if k in ("COD_SEDE","NOMBRE_SEDE","COD_CARRERA","NOMBRE_CARRERA","MODALIDAD","COD_JORNADA","COD_TIPO_PLAN_CARRERA","COD_NIVEL_CARRERA","NOMBRE_TITULO","VIGENCIA_CARRERA"))
    else:
        # buscar variantes: mismo carrera+modalidad+jornada+tipoplan+nivel+titulo pero distinta sede
        found_dim = None
        candidatos = []
        for k2, recs in rep_index.items():
            same = 0
            diffs = []
            fields_inst = [norm(sede), norm(carrera), str(modalidad), str(jornada), str(tipoplan), str(nivel), norm(titulo)]
            for a, b, name in zip(k2, fields_inst, ["sede","carrera","modalidad","jornada","tipoplan","nivel","titulo"]):
                if a == b:
                    same += 1
                else:
                    diffs.append(name)
            if same == 6 and len(diffs) == 1:
                candidatos.append((diffs[0], k2, recs))

        if candidatos:
            diff_field, k2, recs = candidatos[0]
            mapping = {
                "sede": "NUEVA_SEDE",
                "modalidad": "NUEVA_MODALIDAD",
                "jornada": "NUEVA_JORNADA",
                "tipoplan": "NUEVO_TIPO_PLAN",
                "nivel": "NUEVA_VERSION_PENDIENTE_CONFIRMACION",
                "titulo": "NUEVA_VERSION_PENDIENTE_CONFIRMACION",
                "carrera": "REQUIERE_REVISION_MANUAL",
            }
            clasificacion = mapping.get(diff_field, "REQUIERE_REVISION_MANUAL")
            razon = f"Coincide en 6 de 7 componentes de la llave diagnostica con un registro de 5912; difiere unicamente en '{diff_field}'. Se registra como variante respecto de un programa ya vigente, no como duplicado exacto."
            lado_5912 = "; ".join(f"{k}={v}" for k, v in recs[0].items() if k in ("COD_SEDE","NOMBRE_SEDE","COD_CARRERA","NOMBRE_CARRERA","MODALIDAD","COD_JORNADA","COD_TIPO_PLAN_CARRERA","COD_NIVEL_CARRERA","NOMBRE_TITULO","VIGENCIA_CARRERA"))
        else:
            # similitud de nombre de carrera en la misma sede (posible variante mal escrita, sin normalizar automaticamente)
            sim_matches = []
            for (s2, c2), recs in rep_by_sede_carrera.items():
                if s2 == norm(sede) and c2 != norm(carrera):
                    ratio = difflib.SequenceMatcher(None, norm(carrera), c2).ratio()
                    if ratio >= 0.80:
                        sim_matches.append((ratio, c2, recs))
            if sim_matches:
                sim_matches.sort(reverse=True)
                ratio, c2, recs = sim_matches[0]
                clasificacion = "REQUIERE_REVISION_MANUAL"
                razon = f"NOMBRE_CARRERA no coincide exactamente pero tiene similitud textual alta ({ratio:.2f}) con '{recs[0].get('NOMBRE_CARRERA')}' en la misma sede segun 5912. NO se declara igualdad automatica por nombre; requiere confirmacion humana."
                lado_5912 = "; ".join(f"{k}={v}" for k, v in recs[0].items() if k in ("COD_SEDE","NOMBRE_SEDE","COD_CARRERA","NOMBRE_CARRERA","MODALIDAD","COD_JORNADA","COD_TIPO_PLAN_CARRERA","COD_NIVEL_CARRERA","NOMBRE_TITULO","VIGENCIA_CARRERA"))
            else:
                clasificacion = "NUEVO_NO_PRESENTE_EN_ETAPA1"
                razon = "No se encontro ningun registro en el reporte 5912 (Oferta Vigente Validada Etapa 1) que comparta sede y nombre de carrera, ni con coincidencia de 6/7 componentes de la llave diagnostica."
                lado_5912 = ""

    # validacion de catalogo de sede (COD_SEDE <-> NOMBRE_SEDE) contra lo observado en 5912, sin normalizar/corregir
    sede_obs = sede_catalog.get(str(cod_sede))
    if sede_obs is None:
        sede_flag = "COD_SEDE no aparece en ningun registro del reporte 5912 (no se puede confirmar contra la fuente disponible)."
    elif norm(sede) not in sede_obs:
        sede_flag = f"NOMBRE_SEDE ('{sede}') no coincide con el/los nombres observados en 5912 para COD_SEDE={cod_sede}: {sorted(sede_obs)}"
    else:
        sede_flag = "OK: COD_SEDE y NOMBRE_SEDE coinciden con lo observado en el reporte 5912."

    detalle.append({
        "fila_excel": fila,
        "cod_sede": cod_sede, "nombre_sede": sede,
        "nombre_carrera": carrera, "modalidad": modalidad, "cod_jornada": jornada,
        "cod_tipo_plan_carrera": tipoplan, "cod_nivel_carrera": nivel, "nombre_titulo": titulo,
        "vigencia_carrera": row.get("VIGENCIA_CARRERA"),
        "clasificacion": clasificacion, "razon": razon,
        "coincidencia_5912": lado_5912,
        "verificacion_sede_vs_5912": sede_flag,
    })
    resumen_counts[clasificacion] = resumen_counts.get(clasificacion, 0) + 1

# --- salidas ---
tsv_path = os.path.join(OUT, f"CONCILIACION_ETAPA2_VS_REPORTE_5912_{STAMP}.tsv")
cols = ["fila_excel","cod_sede","nombre_sede","nombre_carrera","modalidad","cod_jornada","cod_tipo_plan_carrera","cod_nivel_carrera","nombre_titulo","vigencia_carrera","clasificacion","razon","coincidencia_5912","verificacion_sede_vs_5912"]
with open(tsv_path, "w", encoding="utf-8") as f:
    f.write("\t".join(cols) + "\n")
    for d in detalle:
        f.write("\t".join(str(d.get(c,"")).replace("\t"," ").replace("\n"," ") for c in cols) + "\n")

json_path = os.path.join(OUT, f"CONCILIACION_ETAPA2_VS_REPORTE_5912_{STAMP}.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump({"resumen": resumen_counts, "total_registros_institucionales_evaluados": len(inst_rows), "total_registros_5912": len(rep_rows), "detalle": detalle}, f, ensure_ascii=False, indent=2, default=str)

print("Resumen clasificacion:", resumen_counts)
print("Total institucional evaluado:", len(inst_rows), "| Total 5912:", len(rep_rows))
print("TSV:", tsv_path)
print("JSON:", json_path)
