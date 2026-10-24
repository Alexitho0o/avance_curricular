#!/usr/bin/env python3
"""Audita candidatos de los pendientes 2027 sin convertir sugerencias en cruces."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import sys

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.catalogos_sies import (DATA, cargar_catalogo, escribir_inmutables,
                                   json_bytes, normalizar, sha256, verificar_fuente)
from scripts.generar_catalogos_sies_por_anio import construir_oferta, leer

FALTANTES = {
    "CANDIDATO_NOMINAL_UNICO_NO_APLICADO":
        "Equivalencia documentada del CODCARPR y sede con el candidato SIES. "
        "El nombre sin SP coincide, pero U+ indica V y la oferta jornada 3; no homologar sin respaldo.",
    "VARIAS_MODALIDADES_NO_APLICADAS":
        "Codigo SIES o modalidad de carrera vinculada explicitamente al CODCARPR, sede y plan. "
        "Hay oferta presencial y semipresencial; ni SP ni V permiten elegir.",
    "NOMBRE_AMPLIADO_NO_APLICADO":
        "Documento que vincule Tecnico Veterinario SP con Tecnico Veterinario en Clinica de Animales "
        "de Compania, por CODCARPR y sede, y aclare jornada U+ V frente a SIES 3.",
    "SIN_COINCIDENCIA_NOMINAL":
        "Nombre oficial/codigo SIES 2027 del programa TGEIN y su plan. No equiparar Gestion "
        "Industrial con Control Industrial, Automatizacion o Ingenieria por semejanza.",
}


def candidatos_para_revision(dimension, catalog):
    """La busqueda ampliada es solo diagnostica; nunca alimenta el resolutor."""
    name = normalizar(dimension["NOMBRE_L"])
    base = name.removesuffix(" SP")
    sede = catalog["sedes_internas"].get(dimension["SEDE"], dimension["SEDE"])
    rows = [r for r in catalog["oferta"] if r["sede"] == sede]
    candidates = [r for r in rows if base in {normalizar(n) for n in r["nombres_fuente"]}]
    expanded = False
    if not candidates and base == "TECNICO VETERINARIO":
        candidates = [r for r in rows if "TECNICO VETERINARIO EN CLINICA DE ANIMALES DE COMPANIA"
                      in {normalizar(n) for n in r["nombres_fuente"]}]
        expanded = bool(candidates)
    if expanded:
        state = "NOMBRE_AMPLIADO_NO_APLICADO"
    elif not candidates:
        state = "SIN_COINCIDENCIA_NOMINAL"
    elif len({r["modalidad_codigo"] for r in candidates}) > 1:
        state = "VARIAS_MODALIDADES_NO_APLICADAS"
    elif len(candidates) == 1:
        state = "CANDIDATO_NOMINAL_UNICO_NO_APLICADO"
    else:
        state = "VARIAS_VERSIONES_NO_APLICADAS"
    keys = ["codigo_unico", "nombres_fuente", "sede", "jornada", "version", "modalidad_codigo", "modalidad"]
    return state, [{k: r[k] for k in keys} for r in sorted(candidates, key=lambda r: r["codigo_unico"])]


def workbook_rows(path, sheet):
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        return list(workbook[sheet].values)
    finally:
        workbook.close()


def metadata(path, **detail):
    return {"archivo": path.name, "sha256": sha256(path), **detail}


def audit(args):
    contract = json.loads((DATA / "fuentes.json").read_text(encoding="utf-8"))
    for path, digest in contract["referencias_2026"].items():
        verificar_fuente(ROOT, {"path": path, "sha256": digest})
    catalog = cargar_catalogo(2027)
    coverage = json.loads(args.cobertura.read_text(encoding="utf-8"))
    if coverage["anio"] != 2027 or coverage["periodo"] != 1 or coverage["version"] != catalog["version"]:
        raise ValueError("La cobertura no corresponde al catalogo/periodo auditado")
    registry = json.loads((DATA / "REGISTRO.json").read_text(encoding="utf-8"))
    if coverage["paquete"]["archivos"]["catalogo.json"]["sha256"] != registry["catalogos"]["2027"]["sha256"]:
        raise ValueError("Catalogo distinto de la auditoria base")
    if sha256(args.alumnos) != coverage["fuente"]["sha256"]:
        raise ValueError("DatosAlumnos no coincide con el universo base")
    pending = [r for r in coverage["dimensiones"] if r["ESTADO_CODIGO_SIES"] == "SIN_EQUIVALENCIA"]
    if sum(r["registros"] for r in pending) != coverage["estados_codigo_sies"]["SIN_EQUIVALENCIA"]:
        raise ValueError("Los pendientes no concilian con la cobertura")
    codes = {r["CODCARPR"] for r in pending}
    sources, dictionaries = {}, {}
    for key, path, delimiter in [
        ("duracion", ROOT / "DURACION_ESTUDIOS.tsv", "\t"),
        ("puente", ROOT / "control/catalogos/PUENTE_SIES_COMPILADO.tsv", "\t"),
        ("dic_carreras", args.dic_carreras, ","),
    ]:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream, delimiter=delimiter))
        aliases = set()
        for row in rows:
            for field in ("CODCARPR", "CODCARPR_CANONICO", "CODCARPR_ALIAS_LIST"):
                aliases.update(normalizar(v) for v in row.get(field, "").split("|"))
        hits = sorted(codes & aliases)
        dictionaries[key] = hits
        sources[key] = metadata(path, filas=len(rows), codigos_pendientes_encontrados=hits)
    # Un nuevo respaldo requiere revision explicita, no aprobarlo por estar en un diccionario historico.
    if any(dictionaries.values()):
        raise ValueError("Hay codigos pendientes en los diccionarios: revisar evidencia antes de declarar ausencia")
    raw_report = leer(args.reporte, delimiter=";", encoding="latin-1")
    report_offer = construir_oferta(raw_report, 2027, {})
    for item in catalog["oferta"]:
        actual = report_offer[item["codigo_unico"]]
        if any(item[k] != actual[k] for k in ("nombres_fuente", "modalidad_codigo", "sede", "jornada", "version")):
            raise ValueError("La oferta actual no corrobora los candidatos del catalogo")
    sources["reporte_6047"] = metadata(args.reporte, filas=len(raw_report), columna_modalidad="F / MODALIDAD",
                                      contiene_codcarpr="CODCARPR" in raw_report[0])
    sources["datosalumnos"] = dict(coverage["fuente"], filas_periodo=coverage["registros"])
    sources["cobertura"] = metadata(args.cobertura)
    docencia = ROOT / "oferta_academica_2027/03_fuentes_institucionales/entregas_docencia/20260828_etapa2_entrega_02/Oferta 2027 Etapa2_rector_v2.xlsx"
    rows = workbook_rows(docencia, "Hoja4")
    header = rows[0]
    sources["docencia"] = metadata(docencia, hoja="Hoja4", rango_encabezados="A1:AX1",
                                   contiene_codcarpr="CODCARPR" in header)
    docencia_rows = [(i, dict(zip(header, row))) for i, row in enumerate(rows[1:], 2)]
    for key, path, sheet in [("promedios_matriz", args.promedios, "matriz"),
                              ("enlaces_programas", args.enlaces, "programas")]:
        rows = workbook_rows(path, sheet)
        sources[key] = metadata(path, hoja=sheet, filas=len(rows)-1,
                               encabezados=list(rows[0]), contiene_codcarpr="CODCARPR" in rows[0])
    master = ROOT / "requerimiento_bettersoft_uplus_2026/resultados/DICCIONARIO_MAESTRO_UPLUS_SIES_2026_v1.0.xlsx"
    master_rows = workbook_rows(master, "20_MATRIZ_SOLICITUD_BETTERSOFT")
    requerimientos = [{"fila": i, "id": r[1], "campo": r[2], "descripcion": r[3], "fuente": r[4]}
                      for i, r in enumerate(master_rows, 1) if r[1] in {"UP-26", "UP-27"}]
    if {r["id"] for r in requerimientos} != {"UP-26", "UP-27"}:
        raise ValueError("No se encontraron los requerimientos del diccionario maestro")
    sources["diccionario_maestro"] = metadata(master, hoja="20_MATRIZ_SOLICITUD_BETTERSOFT",
                                              requerimientos=requerimientos)
    result = []
    for dimension in pending:
        state, candidates = candidatos_para_revision(dimension, catalog)
        for candidate in candidates:
            code = candidate["codigo_unico"]
            candidate["filas_reporte_6047"] = report_offer[code]["filas_fuente"]
            candidate["filas_docencia"] = [i for i, r in docencia_rows
                if normalizar(r.get("NOMBRE_CARRERA")) in {normalizar(n) for n in candidate["nombres_fuente"]}
                and all(str(r.get(field, "")) == candidate[attr] for field, attr in
                        [("COD_SEDE", "sede"), ("MODALIDAD", "modalidad_codigo"),
                         ("COD_JORNADA", "jornada"), ("VERSION", "version")])]
        result.append({**{k: dimension[k] for k in ["CODCARPR", "NOMBRE_L", "SEDE", "JORNADA", "registros"]},
                       "estado_revision": state, "candidatos_no_aplicados": candidates,
                       "codigo_sies_asignado": "", "modalidad_asignada": "No determinada",
                       "falta": FALTANTES.get(state, "Vinculo de programa y version SIES documentado."),
                       "coincidencias_diccionarios_codcarpr": 0})
    counts = Counter()
    for row in result:
        counts[row["estado_revision"]] += row["registros"]
    return {"anio": 2027, "periodo": 1, "version_catalogo_sin_cambio": catalog["version"],
            "alcance": coverage["alcance"], "registros_periodo": coverage["registros"],
            "registros_revisados": sum(counts.values()), "codigos_internos_revisados": len(codes),
            "registros_resueltos_nuevos": 0, "equivalencias_aplicadas": [], "por_motivo": dict(counts),
            "cambia_catalogo_o_elegibilidad": False, "datos_personales_incluidos": False,
            "fuentes": sources, "casos": result,
            "referencias_2026_verificadas": contract["referencias_2026"]}


def markdown(report):
    lines = ["# Revision de pendientes SIES 2027 P1", "",
             f"{report['registros_revisados']} registros / {report['codigos_internos_revisados']} codigos internos. "
             "Nuevas equivalencias respaldadas: 0. Catalogo activo sin cambios.", "",
             "Los candidatos de esta tabla NO estan aprobados ni se asignaron. "
             "Su modalidad es la del registro de oferta, no una clasificacion del estudiante.", "",
             "| CODCARPR | Sede | Registros | NOMBRE_L (DatosAlumnos) | Resultado | Candidatos SIES no aplicados |",
             "|---|---|---:|---|---|---|"]
    for r in report["casos"]:
        candidates = "; ".join(c["codigo_unico"] for c in r["candidatos_no_aplicados"]) or "Sin coincidencia nominal"
        lines.append(f"| {r['CODCARPR']} | {r['SEDE']} | {r['registros']} | {r['NOMBRE_L']} | {r['estado_revision']} | {candidates} |")
    lines += ["", "## Que falta", ""]
    for state, n in report["por_motivo"].items():
        lines.append(f"- {n} registros, {state}: {FALTANTES.get(state, 'Version documentada.')}")
    lines += ["", "## Evidencia", "", "El JSON adjunto identifica hashes, hojas, filas y requerimientos UP-26/UP-27.",
              "Los diccionarios revisados no contienen estos 14 CODCARPR. Docencia y la oferta "
              "respaldan los atributos de los candidatos, pero no su enlace a los codigos internos.", "",
              "No se ejecutaron Matricula Unificada ni Caracterizacion. No se modificaron fuentes ni congelados 2026.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cobertura", "alumnos", "reporte", "dic-carreras", "promedios", "enlaces", "salida"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    report = audit(args)
    escribir_inmutables({args.salida / "REVISION_PENDIENTES.json": json_bytes(report),
                         args.salida / "REVISION_PENDIENTES.md": markdown(report).encode("utf-8")})
    print(json.dumps({k: report[k] for k in ["registros_revisados", "codigos_internos_revisados",
                                            "registros_resueltos_nuevos", "por_motivo"]}))


if __name__ == "__main__":
    main()
