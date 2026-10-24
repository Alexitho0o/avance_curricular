#!/usr/bin/env python3
"""Prepara descriptores JSON sin datos personales para el diccionario SIES–UMAS.

No crea Excel ni modifica fuentes o catálogos. Contrato documental:
docs/DICCIONARIO_HISTORICO_SIES_UMAS_2007_2026.md.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import unicodedata

CODE = re.compile(r"I(?P<ies>\d+)S(?P<sede>\d+)C(?P<carrera>\d+)J(?P<jornada>\d+)V(?P<version>\d+)")
SEDE = {"2": "RE", "3": "CO"}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def norm(value):
    text = unicodedata.normalize("NFKD", str(value or "").strip().upper())
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).split())


def year(value):
    if value in (None, ""):
        return None
    match = re.fullmatch(r"(?:OFE_)?(\d{4})", str(value))
    check(match is not None, "Año inválido en evidencia")
    return int(match[1])


def joined(values):
    return " | ".join(str(v) for v in sorted(set(values), key=str) if v not in (None, ""))


def key_umas(codcarpr, jornada, sede, nombre):
    return "|".join(map(norm, (codcarpr, jornada, sede, nombre)))


def state(candidates):
    return "RESUELTO" if len(candidates) == 1 else "AMBIGUO" if candidates else "SIN_EQUIVALENCIA"


def descriptor(name, title, subtitle, headers, rows, widths):
    check(len(headers) == len(widths), f"Anchos incorrectos: {name}")
    check(all(len(r) == len(headers) for r in rows), f"Filas irregulares: {name}")
    return {"name": name, "title": title, "subtitle": subtitle, "headers": headers, "rows": rows, "widths": widths}


def prepare(directory):
    input_names = ("oferta2026", "oferta_historica", "mrun_programas", "puente_expandido", "ejemplos_umas", "reglas_version", "caracterizacion_reglas_y_fuentes")
    data = {name: json.loads((directory / f"{name}.json").read_text(encoding="utf-8")) for name in input_names}
    offer, hist, mrun, bridge, examples, rules, caracterizacion = (data[k] for k in input_names)
    current = offer["por_codigo_unico"]
    historical = hist["registros"]
    observed = mrun["registros_programa"]
    equivalences = bridge["filas_equivalencias"]
    catalog = {r["codigo_unico"]: r for r in bridge["catalogo_sies"]}
    sources, source_keys = [], {}

    def source(path, digest, scope):
        identity = (str(path), digest)
        if identity in source_keys:
            return source_keys[identity]
        sid = f"F{len(sources) + 1:02d}"
        source_keys[identity] = sid
        sources.append([sid, Path(path).name, str(path), digest, scope])
        return sid

    f_offer = source(offer["fuente"]["path"], offer["fuente"]["sha256"], "Nombres literales y oferta 2026: 124 códigos; fuente indicada por el usuario.")
    f_hist = source(hist["fuente"], hist["sha256"], "Oferta histórica SIES 2010–2026; 747 registros del código institucional 162 verificados en el original.")
    source(hist["derivado"], hist["sha256_derivado"], "Extracción institucional reproducible del histórico de oferta; conserva hoja y fila original.")
    f_mrun = source(mrun["fuente"], mrun["sha256"], "Proyección de dimensiones de programa observadas en matrícula 2007–2026; sin identificadores personales. No prueba oferta sin matrícula.")
    f_bridge = source(bridge["fuentes"]["puente"]["path"], bridge["fuentes"]["puente"]["sha256"], "161 llaves UMAS; 257 candidatos; equivalencia operativa 2026 sin vigencia histórica documentada.")
    source(bridge["fuentes"]["catalogo"]["path"], bridge["fuentes"]["catalogo"]["sha256"], "Catálogo anual 2026: 137 códigos; 103 con alguna equivalencia UMAS y 34 sin ella.")
    f_dur = source(bridge["fuentes"]["duracion"]["path"], bridge["fuentes"]["duracion"]["sha256"], "Fuente operativa de equivalencias; nombres internos separados del nombre literal de oferta.")
    f_da = source(examples["fuente"]["path"], examples["fuente"]["sha256"], "Solo combinaciones académicas sin identidades; año de matrícula, cohorte y período de ingreso se conservan separados.")
    source(examples["resolutor"]["path"], examples["resolutor"]["sha256"], "Resolutor anual con coincidencia única; no elige versión máxima ni primera coincidencia.")
    g = rules["hallazgo_gobernanza_anoingreso"]
    source(g["path"], g["sha256"], "Frecuencias históricas de 109 CODCARPR; no contiene versión SIES, código SIES, sede ni período.")
    for item in caracterizacion["fuentes"]:
        source(item["path"], item["sha256"], "Gobernanza de Caracterización; evidencia complementaria de reglas, no autorización retroactiva de equivalencias.")

    h_by, m_by, eq_by, exact_candidates, bridge_candidates = (defaultdict(list) for _ in range(5))
    for row in historical:
        h_by[row["CODIGO_UNICO"]].append(row)
    for row in observed:
        m_by[row["codigo_unico"]].append(row)
    # Correspondencias verificadas por la misma clave SIES en las dos fuentes;
    # no se deduce la modalidad a partir de jornada, nombre ni año.
    domains = {"modalidad": {}, "tipo_plan": {}, "vigencia": {}, "jornada": {}}
    for code, r in current.items():
        same_year = [h for h in h_by[code] if year(h["ANO"]) == 2026]
        check(len(same_year) == 1, "Oferta actual sin contraparte histórica única para interpretar códigos")
        h = same_year[0]
        for domain, current_field, historic_field in (("modalidad", "MODALIDAD", "MODALIDAD"), ("tipo_plan", "CODIGO_TIPO_CARRERA", "TIPO_CARRERA"), ("vigencia", "VIGENCIA", "VIGENCIA")):
            token, label = str(r["campos_originales"][current_field]), h[historic_field]
            check(token not in domains[domain] or domains[domain][token] == label, "Codificación contradictoria entre fuentes")
            domains[domain][token] = label
    for h in historical:
        match = CODE.fullmatch(h["CODIGO_UNICO"])
        if match and h.get("JORNADA"):
            token, label = match["jornada"], h["JORNADA"]
            check(token not in domains["jornada"] or domains["jornada"][token] == label, "Jornada histórica contradictoria")
            domains["jornada"][token] = label
    check(domains["modalidad"] == {"1": "Presencial", "2": "Semipresencial", "3": "No Presencial"}, "Cambió el dominio de modalidad")
    check(domains["tipo_plan"] == {"1": "Plan Regular", "3": "Plan Regular de Continuidad"}, "Cambió el dominio observado de tipo de plan")

    def standardized(value, domain):
        if value in (None, ""):
            return None
        raw = str(value)
        if raw in domains[domain]:
            return raw
        candidates = [token for token, label in domains[domain].items() if norm(label) == norm(raw)]
        return candidates[0] if len(candidates) == 1 else None

    unique_equivalences = set()
    for row in equivalences:
        code = row["CODIGO_UNICO_SIES"]
        sede = SEDE.get(row["COD_SED"], row["COD_SED"])
        key = key_umas(row["CODCARPR"], row["JORNADA_UMAS"], sede, row["NOMBRE_L_UMAS"])
        check((key, code) not in unique_equivalences, "Equivalencia candidata duplicada")
        unique_equivalences.add((key, code))
        eq_by[code].append(row)
        exact_candidates[key].append(code)
        bridge_candidates[row["SOURCE_KEY_3"]].append(code)
    exact_candidates = {k: sorted(set(v)) for k, v in exact_candidates.items()}
    bridge_candidates = {k: sorted(set(v)) for k, v in bridge_candidates.items()}
    all_codes = sorted(set(current) | set(h_by) | set(m_by) | set(catalog))
    check(len(all_codes) == 141, "La unión no coincide con los 141 identificadores del corte")
    check(len(historical) == 747 and len(observed) == 472 and len(equivalences) == 257, "Cambió el corte de evidencia declarado")
    reference, dictionary_rows = {}, []
    for code in all_codes:
        match = CODE.fullmatch(code)
        components = match.groupdict() if match else {}
        check(not match or components["ies"] == "162", "Institución diferente de IPSS")
        if code in current:
            row = current[code]; original = row["campos_originales"]
            name, ref_year, sid = row["nombre_literal"], 2026, f_offer
            locator = f"{sid} · {row['hoja']} fila {row['fila_excel']}"
            modality, plan = original.get("MODALIDAD") or None, original.get("CODIGO_TIPO_CARRERA") or None
            check(all(str(original.get(k)) == components[v] for k, v in (("CODIGO_CARRERA", "carrera"), ("CODIGO_JORNADA", "jornada"), ("VERSION_CARRERA", "version"))), "Oferta 2026 contradice componentes SIES")
        elif h_by[code]:
            row = max(h_by[code], key=lambda r: year(r["ANO"]))
            name, ref_year, sid = row["NOMBRE_CARRERA"], year(row["ANO"]), f_hist
            locator = f"{sid} · {row['hoja_origen']} fila {row['fila_origen']}"
            modality, plan = row.get("MODALIDAD") or None, row.get("TIPO_CARRERA") or None
        else:
            row = max(m_by[code], key=lambda r: year(r["cat_periodo"]))
            name, ref_year, sid = row["nomb_carrera"], year(row["cat_periodo"]), f_mrun
            locator = f"{sid} · {row['ARCHIVO_ORIGEN']} · fila proyección {row['fila_ejemplo_fuente']}"
            modality, plan = row.get("modalidad") or None, row.get("tipo_plan_carr") or None
        reference[code] = {"name": name, "year": ref_year, "source": sid, "locator": locator, "modalidad_literal_fuente": modality, "tipo_plan_literal_fuente": plan}
        modality = standardized(modality, "modalidad")
        plan = standardized(plan, "tipo_plan")
        candidates = eq_by[code]
        ambiguous = any(len(exact_candidates[key_umas(e['CODCARPR'], e['JORNADA_UMAS'], SEDE.get(e['COD_SED'], e['COD_SED']), e['NOMBRE_L_UMAS'])]) > 1 for e in candidates)
        eq_state = "Sin equivalencia UMAS" if not candidates else "Incluye llaves ambiguas" if ambiguous else "Llaves con candidato único"
        dictionary_rows.append([code, name, sid, ref_year, components.get("carrera"), components.get("sede"), components.get("jornada"), modality, components.get("version"), plan, "Sí" if code in current else "No", current[code]["campos_originales"].get("VIGENCIA") if code in current else None, "Sí" if code in catalog else "No", "Sí" if m_by[code] else "No", joined(year(r["cat_periodo"]) for r in m_by[code]), joined(year(r["ANO"]) for r in h_by[code]), len(candidates), joined(r["CODCARPR"] for r in candidates), joined(r["NOMBRE_L_UMAS"] for r in candidates), eq_state, locator])
    dictionary_headers = ["Código Único", "Nombre literal referencia", "Fuente nombre", "Año fuente nombre", "Código carrera", "Sede SIES", "Jornada SIES", "Modalidad SIES", "Versión SIES", "Tipo plan", "En oferta2026", "Vigencia oferta2026", "En catálogo2026", "Observado MRUN", "Años MRUN", "Años oferta", "Equivalencias UMAS", "CODCARPR asociados", "NOMBRE_L asociados", "Estado cruce UMAS", "Ejemplo fuente/fila"]

    equivalence_rows = []
    for r in equivalences:
        code = r["CODIGO_UNICO_SIES"]; sede = SEDE.get(r["COD_SED"], r["COD_SED"])
        key = key_umas(r["CODCARPR"], r["JORNADA_UMAS"], sede, r["NOMBRE_L_UMAS"])
        candidates = exact_candidates[key]
        check(not r["ANIO_INGRESO_MIN"] and not r["ANIO_INGRESO_MAX"] and not r["CONDICION_ANIO_INGRESO"], "Se detectaron condiciones nuevas de año: revisar contrato")
        equivalence_rows.append([key, 2026, r["CODCARPR"], r["NOMBRE_L_UMAS"], r["JORNADA_UMAS"], sede, code, reference[code]["name"], r["COD_CAR"], r["COD_SED"], r["JOR_SIES"], r["MODALIDAD_CODIGO"], r["VERSION_SIES"], r["TIPO_PLAN_CARRERA"], state(candidates), len(candidates), r["ESTADO_PUENTE"], joined(bridge_candidates[r["SOURCE_KEY_3"]]), None, None, "No documentada", f"{f_bridge} · " + joined(e['fila'] for e in r['evidencia_puente']), f"{f_dur} · " + joined(e['fuente_original_fila'] for e in r['evidencia_catalogo']), key + "|" + r["VERSION_SIES"]])
    eq_headers = ["Clave UMAS", "Año catálogo", "CODCARPR", "NOMBRE_L", "Jornada UMAS", "Sede UMAS", "Código Único", "Nombre literal referencia", "Código carrera", "Sede SIES", "Jornada SIES", "Modalidad SIES", "Versión SIES", "Tipo plan", "Estado llave con sede", "Número candidatos llave con sede", "Estado puente", "Candidatos puente", "Año ingreso mínimo", "Año ingreso máximo", "Vigencia temporal", "Fuente puente fila", "Fuente DURACION fila", "Clave con versión"]

    annual_rows = []
    for r in historical:
        match = CODE.fullmatch(r["CODIGO_UNICO"]); comp = match.groupdict() if match else {}
        annual_rows.append(["Oferta", year(r["ANO"]), r["CODIGO_UNICO"], r["NOMBRE_CARRERA"], r.get("CODIGO_CARRERA") or None, r.get("CODIGO_SEDE") or None, r.get("JORNADA") or None, comp.get("jornada"), r.get("MODALIDAD") or None, r.get("VERSION") or None, r.get("TIPO_CARRERA") or None, r.get("VIGENCIA") or None, f_hist, r.get("hoja_origen"), int(r["fila_origen"])])
    for r in observed:
        match = CODE.fullmatch(r["codigo_unico"]); comp = match.groupdict() if match else {}
        annual_rows.append(["Matrícula MRUN", year(r["cat_periodo"]), r["codigo_unico"], r["nomb_carrera"], r.get("cod_carrera") or None, r.get("cod_sede") or None, r.get("jornada") or None, comp.get("jornada"), r.get("modalidad") or None, r.get("version") or None, r.get("tipo_plan_carr") or None, r.get("vigencia_carrera") or None, f_mrun, r["ARCHIVO_ORIGEN"], r["fila_ejemplo_fuente"]])
    annual_rows.sort(key=lambda r: (r[1], r[2], r[0], str(r[3])))
    annual_headers = ["Tipo evidencia", "Año", "Código Único", "Nombre literal informado", "Código carrera informado", "Sede informada", "Jornada literal", "Jornada código SIES", "Modalidad literal/código", "Versión informada", "Tipo plan informado", "Vigencia informada", "Fuente", "Hoja/archivo origen", "Fila ejemplo fuente"]

    grouped = defaultdict(list)
    for r in examples["combinaciones_unicas"]:
        observed_year = year(r["ANOMATRICULA"])
        if observed_year is not None and 2007 <= observed_year <= 2026:
            grouped[tuple(r[k] for k in ("CODCARPR", "NOMBRE_L", "JORNADA", "SEDE"))].append(r)
    example_rows = []
    for group, rows in sorted(grouped.items()):
        chosen_year = 2026 if any(year(r["ANOMATRICULA"]) == 2026 for r in rows) else max(year(r["ANOMATRICULA"]) for r in rows)
        r = min((r for r in rows if year(r["ANOMATRICULA"]) == chosen_year), key=lambda r: int(r["fila_fuente"]))
        key = key_umas(r["CODCARPR"], r["JORNADA"], r["SEDE"], r["NOMBRE_L"])
        exact = exact_candidates.get(key, []) if chosen_year == 2026 else []
        query = r["consulta_sies_2026"]
        if chosen_year == 2026:
            resolver_state, resolver_candidates = query["estado"], query["candidatos"]
            exact_state = state(exact)
            note = "Consulta registrada y llave exacta concuerdan" if sorted(resolver_candidates) == exact else "La consulta registrada no restringió el nombre; conservar diferencia respecto de la llave exacta"
        else:
            resolver_state, resolver_candidates = "Sin catálogo anual verificado", []
            exact_state, note = "Sin catálogo anual verificado", "Observación histórica; no aplicar catálogo 2026 retroactivamente"
        example_rows.append([key, *group, chosen_year, year(r["ANOINGRESO"]), str(r["PERIODOINGRESO"]) if r["PERIODOINGRESO"] not in (None, "") else None, joined(year(v["ANOMATRICULA"]) for v in rows), joined(year(v["ANOINGRESO"]) for v in rows), joined(v["PERIODOINGRESO"] for v in rows), resolver_state, joined(resolver_candidates), exact_state, joined(exact), len(exact) if chosen_year == 2026 else None, f_da, int(r["fila_fuente"]), note])
    example_headers = ["Clave UMAS", "CODCARPR", "NOMBRE_L", "Jornada UMAS", "Sede UMAS", "Año matrícula ejemplo", "Año ingreso ejemplo", "Período ingreso ejemplo", "Años matrícula observados", "Años ingreso observados", "Períodos ingreso observados", "Estado resolver 2026", "Candidatos resolver 2026", "Estado llave exacta 2026", "Candidatos exactos 2026", "Número candidatos exactos", "Fuente", "Fila ejemplo fuente", "Observación"]
    example_keys = {row[0] for row in example_rows}
    codes_with_example = {code for key in example_keys for code in exact_candidates.get(key, [])}
    codes_without_example = sorted({r["CODIGO_UNICO_SIES"] for r in equivalences} - codes_with_example)
    check(codes_without_example == ["I162S2C53J3V1", "I162S2C66J4V1", "I162S2C69J4V1", "I162S2C70J4V1"], "Cambió la cobertura de ejemplos UMAS; revisar antes de construir")
    dictionary_headers.extend(["Estado ejemplo UMAS", "Modalidad literal fuente", "Tipo plan literal fuente"])
    for row in dictionary_rows:
        if row[0] in codes_without_example:
            label = "Sin ejemplo de matrícula UMAS observado en corte"
        elif row[0] in codes_with_example:
            label = "Hay ejemplo de llave UMAS; candidato, no asignación de versión"
        else:
            label = "Sin equivalencia UMAS para vincular ejemplo"
        row.extend([label, reference[row[0]]["modalidad_literal_fuente"], reference[row[0]]["tipo_plan_literal_fuente"]])

    rule_rows = []
    for r in rules["reglas"]:
        sid = source(r["path"], r["sha256"], "Código inspeccionado; la existencia de lógica no acredita reglas pobladas en los datos.")
        rule_rows.append([r["id"], r["descripcion"], r["estado_evidencia"], joined(r["entradas"]), r["salida"], r["limite"], sid, f"{r['linea_inicio']}–{r['linea_fin']}"])
    for i, r in enumerate(caracterizacion["reglas_confirmadas"], 1):
        rule_rows.append([f"C{i:02d}", r["regla"], "GOBERNANZA_COMPLEMENTARIA", None, None, "No convierte excepciones operativas en equivalencias históricas universales.", "CARACTERIZACIÓN", r["fuente"]])
    log_codes = ["I162S2C77J4V1", "I162S2C77J4V2"]
    check(all(any(year(r["ANO"]) == 2026 for r in h_by[c]) for c in log_codes), "Falta coexistencia de Logística V1/V2 en oferta 2026")
    historical_v2 = ["I162S2C46J2V2", "I162S2C46J4V2"]
    check(all(c in h_by and c not in catalog for c in historical_v2), "Cambió la brecha histórica de Ciberseguridad V2")
    rule_rows.extend([
        ["B01", "Año de ingreso no determina versión SIES", "BRECHA_DOCUMENTADA", "109 CODCARPR en libro de cohortes", "Sin regla temporal de versión", "El libro no contiene código SIES, versión, sede o período; las condiciones temporales del puente están vacías.", "F10", "Hoja1"],
        ["B02", "Logística V1 y V2 coexisten en oferta 2026", "EVIDENCIA_CONTRA_VERSION_POR_ANIO", joined(log_codes), "Ambas versiones observadas en el mismo año", "CILOG tiene candidatos V1/V2; ILOG tiene V1 en el puente actual. No agregar un candidato a ILOG por compartir nombre.", f_hist, "Año 2026; localizar códigos en Historico anual"],
        ["B03", "Ciberseguridad V2 permanece en el histórico", "COBERTURA_HISTORICA", joined(historical_v2), "Conservar ambos códigos históricos", "Ausentes del catálogo operativo 2026. La ausencia actual no elimina su evidencia histórica ni aporta una equivalencia UMAS.", f_hist, "Historico anual; localizar códigos"],
        ["B04", "Identificadores históricos sin estructura SIES moderna", "COMPONENTES_NO_INFERIDOS", "I162M2008N1 | I162M2008N3", "Conservar identificador y nombre literal", "En Diccionario SIES se dejan vacíos los componentes que no pueden parsearse; los campos explícitamente informados se conservan en Historico anual.", f_mrun, "Año 2008"],
        ["B05", "Sede UMAS de equivalencias expresa sede compatible del candidato", "TRADUCCION_DE_COMPONENTE", "S2→RE; S3→CO", "Clave UMAS con sede", "No constituye una nueva observación de sede del alias. Por ejemplo COTEIQ de sede CO no se resuelve trasladando su candidato S2 a S3.", f_bridge, "Componente S del código candidato"],
        ["B06", "Fuentes de oferta y matrícula cubren universos distintos", "COBERTURA_POR_FUENTE", "Oferta 2010–2026; MRUN 2007–2026", "Unión de 141 identificadores", "La oferta incluye programas sin matrícula observada. MRUN no prueba exhaustividad de oferta sin alumnos en 2007–2009.", f_hist + " | " + f_mrun, None],
        ["B07", "Nombres literales y tipo de plan se mantienen separados", "CONTRATO_USUARIO", "oferta 2026.xlsx", "Nombre literal sin adiciones", "No añadir Continuidad, acentos ni sufijos de jornada al nombre. Para códigos ausentes se conserva nombre literal histórico más reciente.", f_offer, None],
        ["B08", "Cómo leer Modalidad SIES", "CODIFICACION_VERIFICADA", "1 = Presencial; 2 = Semipresencial; 3 = No Presencial", "Modalidad SIES contiene códigos de texto comparables", "Se traduce únicamente el valor explícito de modalidad. Modalidad literal fuente conserva su valor original. Vacío significa no informado o sin correspondencia verificada; no significa cero ni se infiere de jornada.", f_offer + " | " + f_hist, "Mismo código SIES, año 2026; campos MODALIDAD"],
        ["B09", "Cómo leer Jornada SIES", "CODIFICACION_VERIFICADA", "1 = Diurna; 2 = Vespertina; 3 = Semipresencial; 4 = A Distancia", "Jornada y modalidad se consultan por separado", "Son los códigos observados y contrastados en este corte. D/V/O son letras UMAS; O del puente no distingue por sí sola J3 de J4. Los identificadores históricos sin estructura SIES no reciben componentes inventados.", f_hist, "Componente J y campo JORNADA, 2010–2026"],
        ["B10", "Cómo leer Vigencia oferta2026", "CODIFICACION_VERIFICADA", "1 = Vigente con estudiantes nuevos; 2 = Vigente sin estudiantes nuevos", "Estado de la oferta académica", "No equivale al estado vigente de una persona ni implica ausencia total de estudiantes. Se muestran los códigos presentes en oferta2026; un campo vacío indica que el código no aparece en esa fuente.", f_offer + " | " + f_hist, "Mismo código SIES, año 2026; campos VIGENCIA"],
        ["B11", "Cómo leer Tipo plan", "CODIFICACION_VERIFICADA", "1 = Plan Regular; 3 = Plan Regular de Continuidad", "Tipo plan contiene códigos de texto comparables", "Son los tipos observados en las fuentes del corte. Tipo plan literal fuente conserva el valor original. El plan no se incorpora al nombre de carrera y no sustituye la versión SIES.", f_offer + " | " + f_hist, "Mismo código SIES, año 2026; CODIGO_TIPO_CARRERA y TIPO_CARRERA"],
    ])
    rules_headers = ["ID", "Regla o hallazgo", "Estado de evidencia", "Entradas o caso", "Resultado documentado", "Límite o interpretación", "Fuente", "Líneas/localizador"]

    default_key = "CILOG|O|RE|INGENIERIA EN LOGISTICA"
    ilog_key = "ILOG|O|RE|INGENIERIA EN LOGISTICA"
    check(len(exact_candidates.get(default_key, [])) == 2, "El ejemplo CILOG no tiene dos candidatos")
    check(exact_candidates.get(ilog_key) == ["I162S2C77J4V1"], "Cambió la equivalencia ILOG; revisar antes de construir")
    check(len({r[0] for r in dictionary_rows}) == len(dictionary_rows), "Diccionario repetido")
    check(all(reference[c]["name"] == current[c]["nombre_literal"] for c in current), "Se alteró nombre literal de oferta 2026")
    synthetic = [c for c in all_codes if not CODE.fullmatch(c)]
    check(len(synthetic) == 2, "Cantidad inesperada de identificadores históricos sin componentes")
    check(all(row[i] is None for row in dictionary_rows if row[0] in synthetic for i in (4, 5, 6, 8)), "Se inventaron componentes de identificador histórico")
    sheets = [
        descriptor("Diccionario SIES", "Diccionario histórico SIES ↔ UMAS", "141 identificadores · Nombres literales de oferta 2026 cuando existen · La ausencia de alumnos no excluye una oferta", dictionary_headers, dictionary_rows, [24, 66, 14, 16, 14, 12, 14, 20, 14, 28, 14, 17, 16, 15, 45, 45, 19, 45, 75, 30, 62, 65, 28, 38]),
        descriptor("Equivalencias UMAS", "Equivalencias y candidatos UMAS", "257 relaciones documentadas en catálogo 2026 · Conservar candidatos ambiguos · Sin vigencia temporal documentada", eq_headers, equivalence_rows, [86, 14, 17, 65, 16, 14, 24, 65, 14, 12, 14, 16, 14, 14, 26, 25, 19, 84, 20, 20, 23, 24, 26, 90]),
        descriptor("Historico anual", "Evidencia anual por programa", "747 observaciones de oferta + 472 proyecciones de matrícula · Nombres y discrepancias se conservan por fuente y año", annual_headers, annual_rows, [21, 12, 24, 70, 23, 18, 22, 22, 25, 21, 32, 35, 14, 63, 22]),
        descriptor("Ejemplos UMAS", "Ejemplos académicos sin identidad", "Una combinación por código interno, nombre, jornada y sede; se prefiere 2026 y, en su ausencia, el año más reciente hasta 2026", example_headers, example_rows, [86, 17, 66, 16, 14, 21, 21, 24, 45, 45, 28, 34, 85, 34, 85, 25, 13, 22, 88]),
        descriptor("Fuentes", "Fuentes y huellas de integridad", "Las rutas y filas permiten revisar cada relación; no se incluyen identificadores de personas", ["ID fuente", "Archivo", "Ruta", "SHA-256", "Alcance"], sources, [14, 65, 110, 68, 105]),
        descriptor("Reglas", "Reglas verificadas y brechas", "Año de matrícula, cohorte, período y versión son campos distintos; una regla codificada no demuestra que sus datos existan", rules_headers, rule_rows, [12, 72, 52, 70, 65, 100, 25, 68]),
    ]
    return {
        "schema_version": 1, "fecha": "2026-10-15", "sheets": sheets,
        "summary": {
            "codigos": len(all_codes), "codigos_sies_parseables": len(all_codes) - len(synthetic),
            "identificadores_historicos_sin_componentes": synthetic, "oferta_2026": len(current),
            "catalogo_2026": len(catalog), "codigos_observados_mrun": sum(bool(rows) for rows in m_by.values()),
            "equivalencias": len(equivalence_rows), "historico_oferta": len(historical),
            "historico_mrun": len(observed), "historico_anual": len(annual_rows),
            "ejemplos_umas": len(example_rows), "estados_ejemplos": dict(Counter(r[11] for r in example_rows)),
            "codigos_con_equivalencia_sin_ejemplo_umas": codes_without_example,
            "fuentes": len(sources), "reglas": len(rule_rows),
        },
        "validation": {
            "union_completa": True, "codigos_unicos": True, "nombres_literales_oferta_preservados": True,
            "equivalencias_sin_duplicados": True, "componentes_historicos_no_inventados": True,
            "anios_ejemplos_2007_2026": True, "sin_identificadores_personales_en_esquema": True,
            "condiciones_ingreso_vacias_reales": True, "sin_ejemplos_inventados": True,
            "modalidad_y_tipo_plan_codificados_desde_campos_explicitos": True,
            "consulta_ambigua_CILOG": exact_candidates[default_key], "consulta_unica_ILOG": exact_candidates[ilog_key],
        },
        "consulta_default": {
            "clave_umas": default_key, "version": "", "candidatos": exact_candidates[default_key],
            "codigo_para_inspeccion_independiente": "I162S2C77J4V1", "resultado_equivalencia": None,
        },
        "codificaciones_verificadas": domains,
        "evidencia_json": [{"archivo": f"{name}.json", "sha256": hashlib.sha256((directory / f"{name}.json").read_bytes()).hexdigest()} for name in input_names],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidencia", type=Path, required=True)
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()
    payload = prepare(args.evidencia.expanduser().resolve())
    destination = args.salida.expanduser().resolve()
    check(destination not in {(args.evidencia / e["archivo"]).resolve() for e in payload["evidencia_json"]}, "Salida coincide con evidencia")
    raw = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if destination.exists():
        check(destination.read_bytes() == raw, "Salida existente diferente; elegir otra ruta")
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(raw)
    print(json.dumps({"salida": str(destination), "summary": payload["summary"], "validation": payload["validation"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
