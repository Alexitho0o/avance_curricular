"""Separate 2027 P1 communication, internal analysis, and ordered evidence.

``Informe_Categorias`` retains the accepted letter and monitored options.
Acumulado/Hoy refer to recorded answers and submitdate, not enrollment dates.
Detailed incorporation controls remain in the separate internal report.

Builders receive aggregates only. They do not read matrícula, tokens, or
responses, change eligibility, publish files, or affect the closed 2026 flow.
"""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Mapping

from docx import Document
from docx.document import Document as DocumentObject
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from docx.table import Table
from docx.text.paragraph import Paragraph

from caracterizacion_financiamiento import (
    CODIGOS_FINANCIAMIENTO_G01Q19,
    DETALLES_FINANCIAMIENTO_G01Q19,
    validar_cobertura_financiamiento,
)

POLICY = "COMUNICACION_ANALISIS_AUDITORIA_2027_P1-v1"


def _number(value, label="total"):
    number = int(value)
    if number < 0 or float(value) != number:
        raise ValueError(f"{label} debe ser un entero no negativo.")
    return number


def percentage(numerator, denominator):
    """A zero denominator is undefined, including the alleged 0/0 total."""
    denominator = _number(denominator, "denominador")
    numerator = _number(numerator, "numerador")
    if not denominator:
        return "No aplica"
    if numerator == denominator:
        return "100%"
    value = 100 * numerator / denominator
    return f"{value:.1f}".replace(".", ",") + "%"


def _date_label(value):
    if isinstance(value, (date, datetime)):
        return value.strftime("%d-%m-%Y")
    try:
        return date.fromisoformat(str(value)).strftime("%d-%m-%Y")
    except ValueError:
        return str(value)


def _validate_scope(context):
    if (int(context.get("year", 2027)), int(context.get("period", 1))) != (2027, 1):
        raise ValueError("La separacion de reportes es exclusiva de 2027 P1.")


def _document(context):
    """Reuse a retained reference's styles without rewriting that reference."""
    reference = context.get("reference_path", context.get("template_path"))
    doc = Document(str(reference)) if reference else Document()
    for child in list(doc.element.body):
        if child.tag != qn("w:sectPr"):
            doc.element.body.remove(child)
    if not reference:
        for section in doc.sections:
            # Letter and margins of the retained operational Word reference.
            section.page_width = Inches(8.5)
            section.page_height = Inches(11)
            section.top_margin = section.bottom_margin = Inches(1)
            section.left_margin = section.right_margin = Inches(1.25)
    if not reference:
        doc.styles["Normal"].font.name = "Times New Roman"
        doc.styles["Normal"].font.size = Pt(11)
        doc.styles["Normal"].paragraph_format.space_after = Pt(6)
        doc.styles["Normal"].paragraph_format.line_spacing = 1.05
    for name in ("Normal", "Title", "Heading 1", "Heading 2"):
        style = doc.styles[name]
        style.font.color.rgb = RGBColor(0, 0, 0)
    doc.styles["Title"].font.size = Pt(14)
    doc.styles["Title"].font.bold = True
    doc.styles["Heading 1"].font.size = Pt(12)
    doc.styles["Heading 2"].font.size = Pt(11)
    for name in ("Title", "Heading 1", "Heading 2"):
        doc.styles[name].paragraph_format.keep_with_next = True
        properties = doc.styles[name].element.find(qn("w:pPr"))
        if properties is not None:
            border = properties.find(qn("w:pBdr"))
            if border is not None:
                properties.remove(border)
    doc.core_properties.author = ""
    doc.core_properties.last_modified_by = ""
    doc.core_properties.subject = "Caracterizacion 2027 P1"
    return doc


def _table(doc, headers, rows, widths=None, keep_together=False):
    rows = list(rows)
    if not rows:
        return None
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.autofit = False
    if widths:
        for column, width in zip(table.columns, widths):
            column.width = Inches(width)
    for cell, value in zip(table.rows[0].cells, headers):
        cell.text = str(value)
    for values in rows:
        cells = table.add_row().cells
        for cell, value in zip(cells, values):
            cell.text = str(value)
    for index, row in enumerate(table.rows):
        properties = row._tr.get_or_add_trPr()
        properties.append(OxmlElement("w:cantSplit"))
        if index == 0:
            properties.append(OxmlElement("w:tblHeader"))
        for column_index, cell in enumerate(row.cells):
            if widths:
                cell.width = Inches(widths[column_index])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            props = cell._tc.get_or_add_tcPr()
            border = OxmlElement("w:tcBorders")
            for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
                item = OxmlElement("w:" + edge)
                item.set(qn("w:val"), "single")
                item.set(qn("w:sz"), "4")
                item.set(qn("w:color"), "D9D9D9")
                border.append(item)
            props.append(border)
            if index == 0:
                shade = OxmlElement("w:shd")
                shade.set(qn("w:fill"), "E7E6E6")
                props.append(shade)
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(3)
                paragraph.paragraph_format.space_before = Pt(3)
                if index == 0 or (keep_together and index < len(table.rows) - 1):
                    paragraph.paragraph_format.keep_with_next = True
                if column_index > 0 and all(str(v).replace(",", "").replace(".", "").isdigit() for v in [cell.text]):
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in paragraph.runs:
                    # Inherit the retained reference's font instead of changing
                    # its typography or shrinking content to force pagination.
                    run.font.size = doc.styles["Normal"].font.size or Pt(11)
                    run.font.color.rgb = RGBColor(0, 0, 0)
                    run.bold = index == 0
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def _eligible(context):
    return _number(context.get("participation", {}).get("eligible",
        context.get("counts", {}).get("VIGENTES_ELEGIBLES", 0)), "elegibles")


def _distribution(context, key, denominator):
    rows = context.get(key, [])
    if hasattr(rows, "to_dict"):
        rows = rows.to_dict("records")
    rows = list(rows)
    if sum(_number(item.get("total", 0)) for item in rows) != denominator:
        raise ValueError(f"La distribucion de {key} no concilia con {denominator} elegibles.")
    return rows


def _financing_rows(context):
    items = list(context.get("financing", []))
    codes = [str(item["codigo"]).strip().upper() for item in items]
    validar_cobertura_financiamiento(codes)
    if len(codes) != len(set(codes)):
        raise ValueError("Financiamiento contiene alternativas duplicadas.")
    indexed = dict(zip(codes, items))
    rows = []
    for code in CODIGOS_FINANCIAMIENTO_G01Q19:
        # Labels have one authority, not response-provided variants.
        label = DETALLES_FINANCIAMIENTO_G01Q19[code].split("[", 1)[1].rsplit("]", 1)[0]
        value = indexed[code].get('total')
        today = indexed[code].get('today',0)
        rows.append((label, 'No disponible' if value is None else _number(value),
                     'No disponible' if today is None else _number(today)))
    return rows


def _category_rows(context):
    rows, seen = [], {}
    for item in context.get("categories", []):
        category = str(item.get("categoria", "")).strip()
        code = str(item.get("codigo", "")).strip().upper()
        if category.upper() == "FINANCIAMIENTO" or code in CODIGOS_FINANCIAMIENTO_G01Q19:
            continue
        value = item.get('total')
        total = 'No disponible' if value is None else _number(value)
        value_today = item.get('today',0)
        today = 'No disponible' if value_today is None else _number(value_today)
        detail = str(item.get("detalle", "")).strip()
        key = (category, str(item.get('codigo','')), detail)
        if key in seen:
            if seen[key] != (total,today):
                raise ValueError("Una condicion reportada contiene totales contradictorios.")
            continue
        seen[key] = (total,today)
        rows.append((category, detail, total, today))
    return rows


def build_email_report(context: Mapping) -> DocumentObject:
    """Short mail communication about true institutional first-entry students.

    Internal incorporation status, previous enrollment windows, and operational
    directions are deliberately not part of this document. Results denominators
    are the caller's newly governed target, never the previous cohort total.
    """
    _validate_scope(context)
    eligible = _eligible(context)
    doc = _document(context)
    count = context.get('counts',{})
    daily = _number(count.get('NUEVOS_DIARIOS',0))
    eliminated = _number(count.get('ELIMINADOS_PERIODO',0))
    multiple = _number(count.get('RUT_MULTIMATRICULA', 0))
    new_students = 'se incorporó 1 nuevo estudiante' if daily == 1 else f'se incorporaron {daily} nuevos estudiantes'
    people = 'persona' if eliminated == 1 else 'personas'
    intro = (f"Estimados/as:\n\nJunto con saludar, informo que {new_students}. "
        f"El total acumulado de eliminaciones es de {eliminated} {people}.")
    if multiple:
        conflicts = 'se detecta 1 conflicto' if multiple == 1 else f'se detectan {multiple} conflictos'
        intro += f' A la fecha {conflicts} de RUT matriculado en más de una carrera.'
    intro += (f' La matrícula vigente del periodo asciende a {eligible} estudiantes '
              f'para el periodo {context["period"]}.')
    trajectory = context.get("trajectory", {})
    previous = _number(trajectory.get("prior_trajectory", 0))
    responses = bool(context.get("source_flags", {}).get("responses_available", False))
    if responses:
        participation = context.get("participation", {})
        complete = _number(participation.get("complete", 0))
        incomplete = _number(participation.get("incomplete", 0))
        not_started = _number(participation.get("not_started", 0))
        if complete + incomplete + not_started != eligible:
            raise ValueError("Los estados de respuesta no concilian con el universo objetivo.")
        intro += (f"\n\nEn cuanto a la encuesta, el índice de respuesta es {percentage(complete,eligible)}. "
            f"De {eligible} estudiantes vigentes, {complete} ya respondieron, {not_started} aún no responden "
            f"y {incomplete} " + ('presenta respuesta incompleta.' if incomplete==1 else 'presentan respuesta incompleta.'))
        if not eligible:
            intro += ' El índice de respuesta no aplica porque el universo objetivo es cero.'
    else:
        intro += '\n\nA la fecha de corte todavía no hay respuestas disponibles.'
    intro += '\n\nDetalle numérico:'
    doc.add_paragraph(intro)
    summary_rows = [('Nuevos identificados para incorporar a la encuesta',daily),
                    ('Eliminados acumulados',eliminated),('Vigentes elegibles 2027 P1',eligible)]
    if responses:
        summary_rows.extend([('Encuestas completas',complete),('Respuestas incompletas',incomplete),
                             ('Estudiantes sin respuesta',not_started)])
    if previous:
        summary_rows.append(('Con trayectoria académica previa, fuera del objetivo',previous))
    _table(doc,('CONCEPTO','TOTAL'),summary_rows,(4.9,1.1))

    jornadas = _distribution(context, "jornadas", eligible)
    sedes = _distribution(context, "sedes", eligible)
    if eligible:
        doc.add_heading("Distribución por jornada", level=1)
        _table(doc, ("Jornada", "Estudiantes", "% del universo"),
               [(str(item.get("jornada", "SIN DATO")), _number(item["total"]),
                 percentage(item["total"], eligible)) for item in jornadas], (3.0, 1.0, 2.0))
        doc.add_heading("Distribución por código institucional de sede", level=1)
        seat_rows = []
        for item in sedes:
            code = str(item.get("codigo", "SIN DATO"))
            name = str(item.get("nombre", "")).strip()
            known = bool(item.get("known", bool(name)))
            label = f"{code} · {name}" if known and name else f"{code} · Sin denominación validada"
            seat_rows.append((label, _number(item["total"])))
        _table(doc, ("Código y denominación", "Estudiantes"), seat_rows, (4.7, 1.3))
    if responses:
        conditions = _category_rows(context)
        if conditions:
            doc.add_heading("Seguimiento de condiciones y opciones reportadas", level=1)
            doc.add_paragraph(f"Acumulado incluye las opciones registradas en esta encuesta. Hoy corresponde a envíos del {_date_label(context.get('cutoff',''))}, no a la fecha de matrícula.")
            _table(doc, ("Categoría", "Detalle", "Acumulado", "Hoy"), conditions, (1.2, 2.9, 1.2, .7))
        financing = _financing_rows(context)
        doc.add_heading("Alternativas de financiamiento", level=1)
        explanation = doc.add_paragraph("La pregunta permite seleccionar más de una alternativa. "
                                        "Los valores cuentan selecciones afirmativas y no se suman como personas únicas.")
        explanation.paragraph_format.keep_with_next = True
        total = sum(row[1] for row in financing if isinstance(row[1],int))
        today = sum(row[2] for row in financing if isinstance(row[2],int))
        _table(doc, ("Alternativa", "Acumulado", "Hoy"),
               financing + [("Total de selecciones", total, today)], (4.1, 1.2, .7))
    return doc


def build_internal_report(context: Mapping, plan) -> DocumentObject:
    """Aggregate internal monitoring with explicit, separate denominators."""
    _validate_scope(context)
    c = plan.counts
    eligible = _number(c["VIGENTES_ELEGIBLES"])
    registered = _number(c["VIGENTES_CON_TOKEN"])
    current_tokens = _number(c.get("PARTICIPANTES_LIMESURVEY", context.get("current_tokens", registered)))
    outside_target = current_tokens - registered
    if outside_target < 0:
        raise ValueError("Los inscritos del objetivo exceden los tokens actuales exportados.")
    missing = _number(c["VIGENTES_SIN_TOKEN"])
    valid = _number(c["CORREOS_VALIDOS_INCORPORACION"])
    email_pending = _number(c["PENDIENTES_CORREO_INSTITUCIONAL"])
    daily = len(plan.daily)
    backlog = len(plan.backlog)
    temporal = len(plan.temporal)
    pending_dates = (int(plan.missing["PENDIENTE_FECHA"].sum())
                     if "PENDIENTE_FECHA" in plan.missing else temporal)
    email_and_date = (int(plan.pending_email["PENDIENTE_FECHA"].sum())
                      if "PENDIENTE_FECHA" in plan.pending_email else 0)
    if eligible != registered + missing or missing != valid + email_pending or valid != daily + backlog + temporal:
        raise ValueError("El estado de incorporacion no concilia con sus denominadores.")
    doc = _document(context)
    doc.add_paragraph("Estado de incorporación a LimeSurvey 2027 P1", style="Title")
    doc.add_paragraph(f"Corte al {_date_label(context.get('cutoff', plan.today))}")
    doc.add_paragraph(
        f"El universo objetivo reúne {eligible} estudiantes de primer ingreso institucional. "
        "Generar un archivo de participantes no acredita su incorporación efectiva."
        + (f" La fuente del período contiene {_number(c['MATRICULA_PERIODO'])} registros de matrícula."
           if "MATRICULA_PERIODO" in c else ""))
    doc.add_heading("Participantes actuales de LimeSurvey", level=1)
    doc.add_paragraph(
        f"Unidad de encuesta: {eligible} personas únicas. Matrículas elegibles conservadas: "
        f"{_number(c.get('MATRICULAS_ELEGIBLES', eligible))}. "
        f"Personas con varias matrículas elegibles: {_number(c.get('RUT_MULTIMATRICULA', 0))}. "
        "No se elige una carrera principal. La menor fecha válida de sus matrículas elegibles "
        "determina la ventana de incorporación; los valores originales permanecen en el seguimiento.")
    _table(doc, ("Participantes exportados", "Personas", "Base", "%"), [
        ("Total de tokens actuales", current_tokens, current_tokens, percentage(current_tokens, current_tokens)),
        ("Pertenecen al universo objetivo", registered, current_tokens, percentage(registered, current_tokens)),
        ("Fuera del universo objetivo", outside_target, current_tokens, percentage(outside_target, current_tokens)),
    ], (3.2, 0.8, 1.1, 0.9), keep_together=True)
    doc.add_paragraph(
        f"La base de {current_tokens} tokens es distinta de los {eligible} elegibles; no se suman. "
        "Los tokens existentes se conservan.")
    doc.add_heading("Estado de incorporación a LimeSurvey", level=1)
    doc.add_paragraph(
        f"De los {missing} estudiantes elegibles aún no incorporados a LimeSurvey, "
        f"{valid} " + ("cuenta" if valid == 1 else "cuentan")
        + f" con correo institucional válido y {daily + backlog} "
        + ("está disponible" if daily + backlog == 1 else "están disponibles")
        + f" para incorporación según su fecha de matrícula; {email_pending} "
        + ("permanece pendiente" if email_pending == 1 else "permanecen pendientes")
        + " por correo institucional ausente, inválido o contradictorio entre matrículas. "
        "Estos casos se revisarán nuevamente en la siguiente ejecución.")
    _table(doc, ("Concepto", "Personas", "Base", "%"), [
        ("Universo objetivo elegible", eligible, eligible, percentage(eligible, eligible)),
        ("Inscritos en los tokens actuales", registered, eligible, percentage(registered, eligible)),
        ("Elegibles aún no incorporados", missing, eligible, percentage(missing, eligible)),
        ("Sin token y con correo institucional válido", valid, missing, percentage(valid, missing)),
        ("Sin token y pendientes de correo institucional", email_pending, missing, percentage(email_pending, missing)),
        ("Listos para incorporar por CSV diario", daily, missing, percentage(daily, missing)),
        ("Listos para incorporar por CSV acumulado", backlog, missing, percentage(backlog, missing)),
        ("Con correo válido y pendientes de fecha", temporal, valid, percentage(temporal, valid)),
        ("Pendientes de fecha en cualquier estado de correo", pending_dates, missing, percentage(pending_dates, missing)),
    ], (3.2, 0.8, 1.1, 0.9))
    doc.add_paragraph(
        f"Ventana diaria cerrada: {_date_label(plan.window[0])} al {_date_label(plan.window[1])}, "
        "con fines de semana y feriados gobernados; excluye el día de ejecución. "
        "Las matrículas anteriores sin token pasan al acumulado cuando su correo es válido. "
        "La matrícula de hoy no es atrasada.")
    if email_pending:
        doc.add_paragraph(
            f"Correo y fecha pendientes simultáneamente: {email_and_date} "
            + ("persona" if email_and_date == 1 else "personas") + ". "
            "Los indicadores no se suman como personas distintas. "
            "El estudiante sigue en seguimiento; solo se exporta Mail_Inst válido, sin sustituirlo por correo personal.")
    doc.add_heading("Pendientes de firma", level=1)
    signature_people = _number(c.get("PENDIENTES_FIRMA_PERSONAS", 0))
    signature_outside = _number(c.get("PENDIENTES_FIRMA_FUERA_ELEGIBLES", 0))
    signature_overlap = _number(c.get("PENDIENTES_FIRMA_TAMBIEN_ELEGIBLES", 0))
    _table(doc, ("Concepto", "Total"), [
        ("Registros de matrícula con firma pendiente", _number(c.get("VIGENTES_SIN_FIRMA", len(plan.signature)))),
        ("Personas únicas con firma pendiente", signature_people),
        ("Personas con firma pendiente fuera de los elegibles", signature_outside),
        ("Personas con otra matrícula elegible", signature_overlap),
        ("Fuera de elegibles con firma y correo pendientes", _number(c.get("PENDIENTES_FIRMA_Y_CORREO", 0))),
    ], (4.9, 1.1), keep_together=True)
    doc.add_paragraph(
        "Firma pendiente usa la matrícula gobernada y distingue registros de personas únicas. "
        "Otra matrícula elegible o motivos simultáneos conservan sus indicadores; "
        "esta población no se suma a los pendientes elegibles.")
    doc.add_heading("Trayectoria institucional y alcance", level=1)
    t = context.get("trajectory", {})
    before = _number(t.get("candidates_before", eligible + _number(t.get("prior_trajectory", 0))))
    previous = _number(t.get("prior_trajectory", 0))
    first_entry = _number(t.get("first_entry", eligible))
    if first_entry != eligible or before != first_entry + previous:
        raise ValueError("La clasificacion de trayectoria no concilia con el universo objetivo.")
    _table(doc, ("Clasificación", "Personas"), [
        ("Candidatos tras filtros operativos y antes del histórico", before),
        ("Primer ingreso institucional del universo objetivo", first_entry),
        ("Trayectoria académica previa excluida del objetivo", previous),
    ], (4.9, 1.1))
    if "registered_excluded" in t and "unregistered_excluded" in t:
        registered_excluded = _number(t["registered_excluded"])
        unregistered_excluded = _number(t["unregistered_excluded"])
        if registered_excluded + unregistered_excluded != previous or registered_excluded > outside_target:
            raise ValueError("Los excluidos por trayectoria no concilian con los tokens actuales.")
        doc.add_paragraph(
            f"Trayectoria previa: {previous} personas = {registered_excluded} con token actual + "
            f"{unregistered_excluded} sin token. "
            + (f"{unregistered_excluded} no figura" if unregistered_excluded == 1 else f"{unregistered_excluded} no figuran")
            + f" en la exportación actual. Fuera del objetivo: {outside_target} tokens = "
            f"{registered_excluded} por trayectoria previa + {outside_target - registered_excluded} por otros criterios.")
    details = context.get("trajectory_summary", [])
    if details:
        _table(doc, ("Antecedente académico", "Personas"),
               [(str(item["clasificacion"]), _number(item["total"])) for item in details], (4.9, 1.1))
        indicator_sum = sum(_number(item["total"]) for item in details)
        doc.add_paragraph(
            f"Base de indicadores: la unión de {previous} personas únicas. "
            f"La suma de los indicadores es {indicator_sum}; "
            + ("los antecedentes se superponen y esa suma no equivale a personas distintas. "
               if indicator_sum > previous else "cada indicador se conserva con su propio antecedente. ")
            + "Se conservan todos los motivos.")
    doc.add_paragraph(
        "Se revisa el histórico completo del RUT para detectar trayectorias válidas en otra carrera; "
        "ANOINGRESO actual no basta. La propia fila y los duplicados técnicos no son antecedentes. "
        "Se conservan matrícula, tokens y respuestas históricas.")
    if "technical_duplicates" in t:
        technical = _number(t['technical_duplicates'])
        doc.add_paragraph(
            f"Se " + ("identificó" if technical == 1 else "identificaron")
            + f" {technical} " + ("registro duplicado técnico" if technical == 1 else "registros duplicados técnicos")
            + ". Los duplicados se depuran con trazabilidad y no se consideran trayectorias previas.")
    participation_before = context.get("participation_before")
    if participation_before and context.get("source_flags", {}).get("responses_available", False):
        participation_after = context.get("participation", {})
        values = []
        for states in (participation_before, participation_after):
            base = _number(states.get("eligible", 0))
            complete = _number(states.get("complete", 0))
            incomplete = _number(states.get("incomplete", 0))
            not_started = _number(states.get("not_started", 0))
            if complete + incomplete + not_started != base:
                raise ValueError("La comparacion de participacion no concilia con sus denominadores.")
            values.append((base, complete, incomplete, not_started, percentage(complete, base)))
        if values[0][0] != before or values[1][0] != eligible:
            raise ValueError("La comparacion de participacion no coincide con los universos de trayectoria.")
        doc.add_heading("Participación antes y después de revisar las trayectorias", level=1)
        labels = ("Universo objetivo", "Encuestas completas", "Respuestas incompletas", "Sin respuesta",
                  "Índice de respuesta completa")
        _table(doc, ("Concepto", "Antes", "Después"),
               [(label, values[0][index], values[1][index]) for index, label in enumerate(labels)],
               (4.0, 1.0, 1.0), keep_together=True)
        doc.add_paragraph(
            "Índice = encuestas completas / universo objetivo de cada columna. "
            "Los resultados se recalculan sobre el objetivo vigente; las respuestas históricas se conservan.")
    doc.add_heading("Conciliaciones", level=1)
    doc.add_paragraph(f"{eligible} elegibles = {registered} con token actual + {missing} sin token actual.")
    doc.add_paragraph(f"{missing} sin token actual = {valid} con correo válido + {email_pending} "
                      + ("pendiente de correo." if email_pending == 1 else "pendientes de correo."))
    doc.add_paragraph(f"{valid} con correo válido = {daily} diarios + {backlog} acumulados + {temporal} pendientes de fecha.")
    doc.add_paragraph(
        "Las categorías de estas identidades no se duplican. El indicador de fecha de quien "
        "también carece de correo se conserva; su persona se cuenta en correo pendiente. "
        "Fecha pendiente en la última identidad incluye solo correo válido.")
    sources = context.get("sources", {})
    if sources:
        doc.add_heading("Fuentes del corte", level=1)
        source_rows = []
        for role, value in sources.items():
            if isinstance(value, Mapping):
                value = value.get("path", value.get("archivo", ""))
            source_rows.append((str(role), Path(str(value)).name))
        _table(doc, ("Fuente", "Archivo"), source_rows, (1.4, 4.6), keep_together=True)
    return doc


def extract_ordered_document(doc_or_path):
    """Return body paragraphs and tables in actual reading order once each."""
    doc = doc_or_path if isinstance(doc_or_path, DocumentObject) else Document(str(doc_or_path))
    blocks = []
    for element in doc.element.body.iterchildren():
        if element.tag == qn("w:p"):
            paragraph = Paragraph(element, doc)
            if paragraph.text.strip():
                blocks.append({"type": "paragraph", "style": paragraph.style.name, "text": paragraph.text})
        elif element.tag == qn("w:tbl"):
            table = Table(element, doc)
            blocks.append({"type": "table", "rows": [[cell.text for cell in row.cells] for row in table.rows]})
    return blocks


def ordered_document_text(doc_or_path):
    """Readable text paired with the machine-readable ordered extraction."""
    return "\n\n".join(
        block["text"] if block["type"] == "paragraph" else
        "\n".join(" | ".join(row) for row in block["rows"])
        for block in extract_ordered_document(doc_or_path)) + "\n"
