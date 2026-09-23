// Requerimiento Bettersoft v1.0 (Gate 10). Uso:
//   NODE_PATH=../../oferta_academica_2027/node_modules node generar_requerimiento_bettersoft_docx_v1.js ../resultados/gate10/req_v1.json <salida.docx>
// Documento para el proveedor: qué se necesita, definición, entidad, granularidad, historia, catálogos,
// datos sin transformar, códigos SIES seguros, qué no calcular y qué aclarar. Sin lenguaje de trabajo interno.
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  HeadingLevel, AlignmentType, PageOrientation, LevelFormat, TableOfContents, Footer, PageNumber, BorderStyle,
} = require("docx");

const data = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const OUT = process.argv[3];
const TW = 15398;

const clean = (t) => String(t ?? "")
  .replace(/\s*\((?:ver )?C09-\d+[^)]*\)/g, "")
  .replace(/Hoja1 \(PROMEDIOSDEALUMNOS\)/g, "reporte de notas 7804")
  .replace(/Hoja1 /g, "reporte de notas 7804: ").replace(/Hoja1/g, "reporte de notas 7804")
  .replace(/\s{2,}/g, " ").trim();

const P = (t, o = {}) => new Paragraph({ spacing: { after: 100 }, ...o, children: [new TextRun({ text: t, size: 20, ...(o.run || {}) })] });
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 240, after: 120 }, children: [new TextRun(t)] });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 180, after: 80 }, children: [new TextRun(t)] });
const B = (t, bold) => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 60 },
  children: bold ? [new TextRun({ text: bold, bold: true, size: 20 }), new TextRun({ text: t, size: 20 })] : [new TextRun({ text: t, size: 20 })] });

const PRIO = { P1: "F8CBAD", P2: "FFE699", P3: "C6E0B4", P4: "D9E1F2" };
function table(headers, rows, weights, prioIdx, size = 16) {
  const tot = weights.reduce((a, b) => a + b, 0);
  const w = weights.map((x) => Math.floor((x / tot) * TW));
  w[w.length - 1] += TW - w.reduce((a, b) => a + b, 0);
  const cell = (t, i, head, fill) => new TableCell({
    width: { size: w[i], type: WidthType.DXA },
    shading: head ? { type: ShadingType.CLEAR, color: "auto", fill: "1F3864" } : (fill ? { type: ShadingType.CLEAR, color: "auto", fill } : undefined),
    margins: { top: 40, bottom: 40, left: 70, right: 70 },
    children: [new Paragraph({ children: [new TextRun({ text: head ? String(t) : clean(t), size: head ? size + 1 : size, bold: head, color: head ? "FFFFFF" : "000000" })] })],
  });
  return new Table({
    width: { size: TW, type: WidthType.DXA }, columnWidths: w,
    rows: [new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, i, true)) }),
      ...rows.map((r) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, i, false, i === prioIdx ? PRIO[c] : undefined)) }))],
  });
}

const mx = data.matriz;
const n = (p) => mx.filter((m) => m.Prioridad === p).length;
const ch = [];
ch.push(new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: "Requerimiento funcional", size: 24, color: "1F3864" })] }));
ch.push(new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: "Reporte Regulatorio Maestro de Estudiantes en U+ para procesos SIES/PES", bold: true, size: 40, color: "1F3864" })] }));
ch.push(new Paragraph({ spacing: { after: 200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: "1F3864", space: 4 } },
  children: [new TextRun({ text: "Instituto Profesional San Sebastián (código IES 162) · Proveedor: Bettersoft · Versión 1.0 · 23-09-2026", size: 18, color: "555555" })] }));
ch.push(new TableOfContents("Contenido", { hyperlink: true, headingStyleRange: "1-2" }));

ch.push(H1("1. Objetivo y principio"));
ch.push(P("Crear en U+ un reporte institucional con los datos de estudiantes que la institución informa a la Subsecretaría de Educación Superior (SIES) mediante la Plataforma de Educación Superior (PES), de modo que los archivos oficiales se construyan sin planillas intermedias y con trazabilidad hasta el dato registrado en U+. El documento describe qué datos se necesitan; no define la solución técnica dentro de U+."));
ch.push(P("Principio del requerimiento:", { run: { bold: true } }));
ch.push(B("Bettersoft entrega hechos y atributos registrados en el ERP."));
ch.push(B("La institución aplica la transformación a códigos SIES cuando esta depende de reglas funcionales, de fechas de corte o de la trayectoria del estudiante."));
ch.push(B("Cuando un dato no existe en U+ se entrega vacío; no se rellena con valores por defecto."));

ch.push(H1("2. Alcance"));
[["Matrícula Unificada (pregrado y posgrado/postítulo). ", "Corte al 30 de abril (pregrado) y 15 de mayo (posgrado)."],
 ["Avance Curricular. ", "Presencia por semestre y unidades del plan cursadas y aprobadas en el año anterior; catálogo de planes."],
 ["Estudiantes Extranjeros (regulares). ", "Estudiantes con nacionalidad extranjera matriculados en el año anterior."],
 ["Ficha de Caracterización Única (FCU). ", "Solo datos de identificación y contacto que se precargan."]].forEach(([b, t]) => ch.push(B(t, b)));
ch.push(P("Quedan fuera de alcance los procesos cuyos datos no provienen de estudiantes en U+ (Oferta Académica, Infraestructura, Personal Académico) y las variables de encuesta de la FCU."));

ch.push(H1("3. Entidades y extractos"));
ch.push(P("Cada campo pertenece a una entidad de U+ y se entrega con la granularidad de esa entidad. No se deben mezclar atributos de la persona con atributos de la matrícula."));
ch.push(table(["Extracto", "Entidad U+", "Una fila por"], [
  ["Reporte principal", "Persona y matrícula", "CODCLI y período consultado"],
  ["Historial de estado y situación", "Historial de la matrícula", "Cambio de estado o situación de cada CODCLI, con fechas de inicio y término"],
  ["Historial de matrícula por período", "Matrícula por año/período", "CODCLI y año/período (programa, jornada, sede, plan, nivel y estado de ese período)"],
  ["Detalle por asignatura", "Registro académico", "Asignatura cursada o reconocida, con CODCLI"],
  ["Catálogo de planes", "Plan de estudios", "Plan de estudios"],
  ["Maestro de programas SIES", "Programa (oferta)", "Programa y vigencia"],
  ["Catálogos U+", "Tablas de parámetros", "Código de cada tabla"]], [25, 25, 50]));

ch.push(H1("4. Matriz de solicitud"));
ch.push(P(`Se solicitan ${mx.length} campos o grupos de campos: ${n("P1")} de prioridad P1 (crítica), ${n("P2")} P2 (alta), ${n("P3")} P3 (media) y ${n("P4")} P4 (baja). P1 = dato obligatorio para los procesos sin alternativa hoy; P2 = dato que existe pero requiere exposición o historia; P3 = simplifica controles; P4 = control y trazabilidad.`));
ch.push(table(["Nº", "Campo solicitado", "Descripción funcional", "Fuente / entidad U+", "Granularidad", "Histórico", "Formato", "Catálogo", "Prioridad", "Procesos", "Observaciones"],
  mx.map((m) => [m["Nº"], `${m.ID} ${m["Campo solicitado"]}`, m["Descripción funcional"], m["Fuente/entidad U+"], m.Granularidad, m["Histórico"], m.Formato, m["Catálogo"], m.Prioridad, m["Procesos SIES"], m.Observaciones]),
  [3, 11, 22, 12, 9, 5, 6, 11, 5, 6, 12], 8, 14));
ch.push(H2("Ejemplos ficticios"));
ch.push(table(["ID", "Campo", "Ejemplo"], data.dic.map((d) => [d.ID, d["CAMPO SOLICITADO"], d.EJEMPLO]), [8, 42, 50]));

ch.push(H1("5. Datos que deben conservar historia"));
ch.push(P("Los procesos se refieren a una fecha de corte o a un año anterior. U+ debe poder entregar estos datos respecto de una fecha o período, no solo el valor vigente al descargar:"));
ch.push(table(["Dato", "Fecha o criterio requerido", "Campos"], data.historial.map((x) => [x.CAMPO.replace(" (MU)", ""), x.CRITERIO, x.ID]), [25, 55, 20]));

ch.push(H1("6. Datos sin transformar y catálogos"));
ch.push(P("Los códigos propios de U+ se entregan tal como están registrados, sin convertirlos a códigos SIES. En particular: tipo de documento, sexo, nacionalidad, sede, carrera, jornada, período, nivel, régimen, estado académico, situación, vía de admisión, categoría, estado civil y comuna."));
ch.push(P("Para cada código que aparezca en los extractos, Bettersoft debe entregar un catálogo con su significado (campo UP-68):"));
["SEXO", "SEDE", "JORNADA", "PERÍODO, con fechas de inicio y término por régimen", "SITUACION y ESTADOACADEMICO", "MATRICULA", "NIVEL", "RÉGIMEN del plan",
 "CATEGORIA y VIASDEADMISION", "Definición temporal de FECHAMATRICULA y ANOMATRICULA"].forEach((t) => ch.push(B(t)));

ch.push(H1("7. Códigos SIES que U+ puede entregar"));
ch.push(P("Solo se piden a U+ códigos SIES que no requieren reglas de cálculo: datos maestros que la institución asigna y U+ almacena, o datos que se registran directamente con una tabla oficial."));
ch.push(table(["Código", "Cómo se obtiene", "Campos"], [
  ["Código único SIES del programa y sus atributos de oferta (modalidad, tipo de plan, nivel, duración)", "Dato maestro asignado por la institución desde la Oferta Académica aceptada por SIES", "UP-26, UP-27"],
  ["Correlativo del plan de estudios dentro del código único", "Dato maestro asignado por la institución", "UP-29"],
  ["Tipo de residencia del estudiante extranjero (1, 2, 3)", "Se registra con la tabla oficial de tres valores", "UP-17"],
  ["País de estudios secundarios y país de origen (1 a 197)", "Se registran con la tabla oficial de países, o por nombre del país", "UP-16, UP-18"]], [40, 45, 15]));
ch.push(H2("Maestro del código único SIES"));
ch.push(P("SIES identifica cada programa con un código que concatena institución, sede, carrera, jornada y versión (por ejemplo I162S2C91J1V1). U+ no registra la versión, por lo que se solicita almacenar el código como dato maestro:"));
ch.push(table(["Aspecto", "Requerimiento"], data.codigo_unico.filter((c) => c.ASPECTO !== "Conclusión").map((c) => [c.ASPECTO, c.DETALLE]), [25, 75]));
ch.push(P("Las reglas de mantención provienen del Instructivo de Oferta Académica 2027 (Anexo 5, sobre modificación del código unificado).", { run: { italics: true, size: 18 } }));

ch.push(H1("8. Variables que U+ no debe calcular"));
ch.push(P("Estos valores dependen de reglas regulatorias y los calculará la institución con los datos solicitados. El reporte no debe incluirlos:"));
data.no_calcular.forEach((x) => ch.push(B(clean(x.CAMPO), x.ID ? `${x.ID} ` : undefined)));

ch.push(H1("9. Reglas de extracción"));
[["Parámetros: ", "año y período de matrícula, fecha de corte y año de referencia académico. Filtros opcionales por nivel global y sede."],
 ["Universo: ", "una fila por CODCLI con matrícula en el período, incluidos retirados y eliminados, con su estado a la fecha de corte."],
 ["Formato: ", "UTF-8 o Excel con encabezados; fechas dd/mm/aaaa; códigos sin espacios al inicio o al final; situación separada en código y descripción."],
 ["Sin valores por defecto: ", "si un dato no existe en U+ se entrega vacío; no se rellena con valores ficticios."],
 ["Datos personales: ", "no incluir columnas sin uso en estos procesos (responsable financiero, datos laborales, tramo de renta, número de hijos, contactos de emergencia, ejecutivo comercial, arancel)."]].forEach(([b, t]) => ch.push(B(t, b)));

ch.push(H1("10. Validaciones mínimas del reporte"));
["CODCLI único y no nulo en el reporte principal; presente en todos los extractos.",
 "Mismo documento y fecha de nacimiento en todos los CODCLI de una persona.",
 "Dígito verificador válido (módulo 11) cuando el documento es RUN; vacío si es pasaporte.",
 "Todo código de U+ entregado existe en el catálogo documentado.",
 "Historiales sin traslapes de fechas para un mismo CODCLI.",
 "Código único SIES existente en el maestro y vigente en el período de la matrícula.",
 "Nombres y apellidos sin espacios dobles ni al inicio o al final."].forEach((t) => ch.push(B(t)));

ch.push(H1("11. Aclaraciones que Bettersoft debe devolver"));
ch.push(H2("Significado de códigos"));
ch.push(table(["Código U+", "Aclaración solicitada"], [
  ["SEXO = S", "Qué significa. No se asignará ninguna equivalencia hasta contar con la definición documentada."],
  ["PERÍODO = 3 (PERIODOINGRESO, PERIODOMATRICULA)", "Qué período representa y sus fechas de inicio y término por régimen. No se asignará semestre hasta contar con la definición."],
  ["JORNADA = O", "Qué significa en U+."],
  ["NIVEL = 20", "Qué representa."],
  ["MATRICULA = 1 / 2", "Qué distingue cada valor."],
  ["FECHAMATRICULA y ANOMATRICULA", "A qué matrícula y período se refieren."]], [30, 70]));
ch.push(H2("Existencia de datos en U+"));
ch.push(P("Para cada campo que no existe o cuya existencia no se pudo verificar, confirmar si U+ lo registra y, si no, proponer cómo incorporarlo:"));
ch.push(table(["ID", "Campo", "Situación", "Prioridad"],
  mx.filter((m) => !m.Observaciones.startsWith("Existe en U+")).map((m) => [m.ID, m["Campo solicitado"], m.Observaciones.split(";")[0], m.Prioridad]), [8, 57, 23, 12], 3));

ch.push(H1("Anexo. Cambios solicitados en U+"));
ch.push(table(["ID", "Tema", "Cambio solicitado", "Procesos", "Prioridad"],
  data.br.map((b) => [b.ID, b.CAMPO, b.CAMBIO, b.PROCESOS, b.PRIORIDAD]), [6, 20, 52, 14, 8], 4));

const doc = new Document({
  creator: "IPSS", title: "Requerimiento Reporte Regulatorio Maestro U+ v1.0",
  styles: { default: { document: { run: { font: "Calibri", size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 30, bold: true, color: "1F3864" }, paragraph: { outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 24, bold: true, color: "2E5597" }, paragraph: { outlineLevel: 1 } }] },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838, orientation: PageOrientation.LANDSCAPE }, margin: { top: 720, bottom: 720, left: 720, right: 720 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Requerimiento Reporte Regulatorio Maestro U+ · v1.0 · página ", size: 16, color: "777777" }), new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "777777" })] })] }) },
    children: ch,
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log("OK", OUT); });
