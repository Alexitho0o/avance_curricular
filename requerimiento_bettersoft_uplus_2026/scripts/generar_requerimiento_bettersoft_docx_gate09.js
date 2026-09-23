// Requerimiento Bettersoft v0.9.1 (Gate 09). Uso:
//   NODE_PATH=../../oferta_academica_2027/node_modules node generar_requerimiento_bettersoft_docx_gate09.js ../resultados/gate09/req_gate09.json <salida.docx>
// Documento para el proveedor: solo requerimientos confirmados, sin referencias a auditorías, scripts ni discusiones internas.
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  HeadingLevel, AlignmentType, PageOrientation, LevelFormat, TableOfContents, Footer, PageNumber, BorderStyle,
} = require("docx");

const data = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const OUT = process.argv[3];
const TW = 15398; // A4 horizontal, márgenes de 720

// Quita referencias internas que no deben llegar al proveedor
const clean = (t) => String(t ?? "")
  .replace(/\s*\((?:ver )?C09-\d+[^)]*\)/g, "")
  .replace(/\s*\((?:Gate 09|9\.\d+)[^)]*\)/g, "")
  .replace(/Hoja1 /g, "reporte de notas 7804: ")
  .replace(/Hoja1/g, "reporte de notas 7804")
  .replace(/\s{2,}/g, " ").trim();

const P = (t, o = {}) => new Paragraph({ spacing: { after: 100 }, ...o, children: [new TextRun({ text: t, size: 20, ...(o.run || {}) })] });
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 240, after: 120 }, children: [new TextRun(t)] });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 180, after: 80 }, children: [new TextRun(t)] });
const B = (t, bold) => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 60 },
  children: bold ? [new TextRun({ text: bold, bold: true, size: 20 }), new TextRun({ text: t, size: 20 })] : [new TextRun({ text: t, size: 20 })] });

const PRIO = { P1: "F8CBAD", P2: "FFE699", P3: "C6E0B4", P4: "D9E1F2" };
function table(headers, rows, weights, prioIdx) {
  const tot = weights.reduce((a, b) => a + b, 0);
  const w = weights.map((x) => Math.floor((x / tot) * TW));
  w[w.length - 1] += TW - w.reduce((a, b) => a + b, 0);
  const cell = (t, i, head, fill) => new TableCell({
    width: { size: w[i], type: WidthType.DXA },
    shading: head ? { type: ShadingType.CLEAR, color: "auto", fill: "1F3864" } : (fill ? { type: ShadingType.CLEAR, color: "auto", fill } : undefined),
    margins: { top: 40, bottom: 40, left: 80, right: 80 },
    children: [new Paragraph({ children: [new TextRun({ text: head ? String(t) : clean(t), size: head ? 17 : 16, bold: head, color: head ? "FFFFFF" : "000000" })] })],
  });
  return new Table({
    width: { size: TW, type: WidthType.DXA }, columnWidths: w,
    rows: [new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, i, true)) }),
      ...rows.map((r) => new TableRow({ children: r.map((c, i) => cell(c, i, false, i === prioIdx ? PRIO[c] : undefined)) }))],
  });
}

const dic = data.dic;
const n = (p) => dic.filter((d) => d.PRIORIDAD === p).length;
const DISP = { "EXISTE": "Existe", "NO_EXISTE": "No existe", "POR_CONFIRMAR": "Por confirmar por Bettersoft", "EXISTE PARCIAL": "Existe en parte" };
const disp = (v) => DISP[v] || String(v).replace("EXISTE", "Existe");
const ACC = { SOLICITAR_HECHO: "Dato U+", SOLICITAR_MAESTRO: "Dato maestro" };

const ch = [];
ch.push(new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: "Requerimiento funcional", size: 24, color: "1F3864" })] }));
ch.push(new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: "Reporte Regulatorio Maestro de Estudiantes en U+ para procesos SIES/PES", bold: true, size: 40, color: "1F3864" })] }));
ch.push(new Paragraph({ spacing: { after: 200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: "1F3864", space: 4 } },
  children: [new TextRun({ text: "Instituto Profesional San Sebastián (código IES 162) · Proveedor: Bettersoft · Versión 0.9.1 para revisión institucional", size: 18, color: "555555" })] }));
ch.push(new TableOfContents("Contenido", { hyperlink: true, headingStyleRange: "1-2" }));

ch.push(H1("1. Objetivo"));
ch.push(P("Crear en U+ un reporte institucional con los datos de estudiantes que la institución informa a la Subsecretaría de Educación Superior (SIES) mediante la Plataforma de Educación Superior (PES). El reporte debe permitir construir los archivos SIES sin planillas intermedias y con trazabilidad desde el dato registrado en U+."));
ch.push(P("Este documento describe qué datos se necesitan, con qué definición, a qué nivel de detalle y con qué reglas de extracción. No define la solución técnica dentro de U+."));

ch.push(H1("2. Alcance"));
[["Matrícula Unificada (pregrado y posgrado/postítulo). ", "Corte al 30 de abril (pregrado) y 15 de mayo (posgrado)."],
 ["Avance Curricular. ", "Presencia por semestre y unidades del plan cursadas y aprobadas en el año anterior; catálogo de planes."],
 ["Estudiantes Extranjeros (regulares). ", "Estudiantes con nacionalidad extranjera matriculados en el año anterior."],
 ["Ficha de Caracterización Única (FCU). ", "Solo datos de identificación y contacto que se precargan."]].forEach(([b, t]) => ch.push(B(t, b)));
ch.push(P("Quedan fuera de alcance los procesos cuyos datos no provienen de estudiantes en U+ (Oferta Académica, Infraestructura, Personal Académico) y las variables de encuesta de la FCU."));

ch.push(H1("3. Principio del requerimiento"));
ch.push(P("U+ entrega hechos; la institución aplica las reglas SIES. Por eso este requerimiento pide datos tal como están registrados en U+, datos nuevos que hoy no existen y datos maestros que la institución mantendrá en U+. No pide que U+ calcule códigos SIES que dependen de reglas regulatorias."));
[["Dato U+: ", "valor registrado en U+, entregado sin transformar (solo limpieza de formato, por ejemplo sin espacios al final)."],
 ["Dato maestro: ", "valor oficial que la institución asigna y mantiene en U+ (por ejemplo, el código único SIES de cada programa)."],
 ["Códigos propios de U+: ", "se entregan tal cual, junto con un catálogo que documente el significado de cada código (sección 8)."]].forEach(([b, t]) => ch.push(B(t, b)));

ch.push(H1("4. Extractos solicitados"));
[["Reporte principal: ", "una fila por matrícula (CODCLI) y período consultado."],
 ["Historial de estado y situación: ", "una fila por cambio de estado o situación de cada CODCLI, con fechas de inicio y término."],
 ["Historial de matrícula por período: ", "una fila por CODCLI y año/período, con el programa, jornada, sede, plan, nivel y estado de ese período."],
 ["Detalle por asignatura: ", "una fila por asignatura cursada o reconocida, con CODCLI."],
 ["Catálogo de planes: ", "una fila por plan de estudios, con su unidad de medida y unidades por año."],
 ["Maestro de programas SIES: ", "código único SIES y atributos de la oferta, con vigencia."],
 ["Catálogos U+: ", "significado de cada código usado en los extractos."]].forEach(([b, t]) => ch.push(B(t, b)));

ch.push(H1("5. Campos solicitados"));
ch.push(P(`Se solicitan ${dic.length} campos o grupos de campos: ${n("P1")} de prioridad P1 (crítica), ${n("P2")} P2 (alta), ${n("P3")} P3 (media) y ${n("P4")} P4 (baja). P1 = dato obligatorio para SIES sin alternativa hoy; P2 = dato existente que requiere exposición o historia; P3 = simplifica controles; P4 = control y trazabilidad.`));
ch.push(table(["ID", "Bloque", "Campo", "Nivel", "Tipo de dato", "Procesos", "Situación en U+", "Prioridad"],
  dic.map((d) => [d.ID, d.BLOQUE, d["CAMPO SOLICITADO"], d.NIVEL, ACC[d.ACCION_BETTERSOFT] || "", d["PROCESOS QUE LO UTILIZAN"], disp(d.DISPONIBILIDAD_UPLUS), d.PRIORIDAD]),
  [6, 12, 28, 14, 8, 14, 12, 7], 7));
for (const b of [...new Set(dic.map((d) => d.BLOQUE))]) {
  ch.push(H2(b));
  ch.push(table(["ID", "Campo", "Definición", "Dónde está hoy en U+", "Ejemplo (ficticio)", "Temporalidad", "Validación"],
    dic.filter((d) => d.BLOQUE === b).map((d) => [d.ID, d["CAMPO SOLICITADO"], d["DEFINICIÓN FUNCIONAL"], d["CAMPO U+ ACTUAL"], d.EJEMPLO, d.TEMPORALIDAD, d.VALIDACION]),
    [6, 15, 38, 14, 11, 10, 12]));
}

ch.push(H1("6. Maestro del código único SIES"));
ch.push(P("SIES identifica cada programa con un código único que concatena institución, sede, carrera, jornada y versión (por ejemplo I162S2C91J1V1). U+ no registra la versión, por lo que hoy no puede determinar el código de todas las matrículas. Se solicita almacenarlo en U+ como dato maestro:"));
ch.push(table(["Aspecto", "Requerimiento"], data.codigo_unico.map((c) => [c.ASPECTO, c.DETALLE]), [25, 75]));
ch.push(P("Las reglas de mantención provienen del Instructivo de Oferta Académica 2027 (Anexo 5, sobre modificación del código unificado).", { run: { italics: true, size: 18 } }));

ch.push(H1("7. Datos históricos"));
ch.push(P("Los procesos SIES se refieren a una fecha de corte o a un año anterior, pero el reporte actual solo muestra el valor vigente al descargar. U+ debe poder entregar estos datos respecto de una fecha o período:"));
ch.push(table(["Dato", "Fecha o criterio requerido", "Campos"], data.historial.map((x) => [x.CAMPO, x.CRITERIO, x.ID]), [25, 55, 20]));

ch.push(H1("8. Catálogos de U+"));
ch.push(P("Para cada código de U+ que aparezca en los extractos, Bettersoft debe documentar su significado. Los códigos se entregan sin transformar; la institución asigna el código SIES según el proceso."));
["SEXO (incluido el código S)", "SEDE", "JORNADA (incluido el código O)", "PERÍODO (incluido el 3), con fechas de inicio y término por régimen", "SITUACION y ESTADOACADEMICO",
 "MATRICULA", "NIVEL (incluido el 20)", "RÉGIMEN del plan", "CATEGORIA y VIASDEADMISION", "Definición temporal de FECHAMATRICULA y ANOMATRICULA"].forEach((t) => ch.push(B(t)));

ch.push(H1("9. Datos que U+ no debe calcular"));
ch.push(P("Los siguientes valores SIES dependen de reglas regulatorias y los calculará la institución con los datos de este requerimiento. El reporte no debe incluir estos cálculos:"));
data.no_calcular.forEach((x) => ch.push(B(clean(x.CAMPO), `${x.ID} `)));

ch.push(H1("10. Reglas de extracción"));
[["Parámetros: ", "año y período de matrícula, fecha de corte y año de referencia académico. Filtros opcionales por nivel global y sede."],
 ["Universo: ", "una fila por CODCLI con matrícula en el período, incluidos retirados y eliminados, con su estado a la fecha de corte."],
 ["Granularidad: ", "sede, jornada, plan, nivel y estado pertenecen a la matrícula y al período, no a la persona."],
 ["Formato: ", "UTF-8 o Excel con encabezados; fechas dd/mm/aaaa; códigos sin espacios al inicio o al final; situación separada en código y descripción."],
 ["Sin valores por defecto: ", "si un dato no existe en U+ se entrega vacío; no se rellena con valores ficticios (por ejemplo, fechas 01/01/1900 o país Chile)."],
 ["Datos personales: ", "no incluir columnas sin uso SIES (responsable financiero, datos laborales, tramo de renta, número de hijos, contactos de emergencia, ejecutivo comercial, arancel)."]].forEach(([b, t]) => ch.push(B(t, b)));

ch.push(H1("11. Validaciones mínimas del reporte"));
["CODCLI único y no nulo en el reporte principal; presente en todos los extractos.",
 "Mismo documento y fecha de nacimiento en todos los CODCLI de una persona.",
 "Dígito verificador válido (módulo 11) cuando el documento es RUN; vacío si es pasaporte.",
 "Todo código de U+ entregado existe en el catálogo documentado.",
 "Historiales sin traslapes de fechas para un mismo CODCLI.",
 "Código único SIES existente en el maestro y vigente en el período de la matrícula.",
 "Nombres y apellidos sin espacios dobles ni al inicio o al final."].forEach((t) => ch.push(B(t)));

ch.push(H1("12. Consultas a Bettersoft"));
ch.push(P("Para los campos que no existen o cuya existencia no se pudo verificar, se solicita confirmar si U+ los registra hoy y, si no, proponer cómo incorporarlos:"));
ch.push(table(["ID", "Campo", "Situación en U+", "Prioridad"],
  dic.filter((d) => d.DISPONIBILIDAD_UPLUS !== "EXISTE").map((d) => [d.ID, d["CAMPO SOLICITADO"], disp(d.DISPONIBILIDAD_UPLUS), d.PRIORIDAD]), [8, 60, 20, 12], 3));

ch.push(H1("Anexo. Cambios solicitados"));
ch.push(table(["ID", "Tema", "Cambio solicitado", "Procesos", "Prioridad"],
  data.br.map((b) => [b.ID, b.CAMPO, b["CAMBIO SOLICITADO"], b["PROCESOS AFECTADOS"], b.PRIORIDAD]), [6, 20, 52, 14, 8], 4));

const doc = new Document({
  creator: "IPSS", title: "Requerimiento Reporte Regulatorio Maestro U+ v0.9.1",
  styles: { default: { document: { run: { font: "Calibri", size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 30, bold: true, color: "1F3864" }, paragraph: { outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 24, bold: true, color: "2E5597" }, paragraph: { outlineLevel: 1 } }] },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838, orientation: PageOrientation.LANDSCAPE }, margin: { top: 720, bottom: 720, left: 720, right: 720 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Requerimiento Reporte Regulatorio Maestro U+ · v0.9.1 · página ", size: 16, color: "777777" }), new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "777777" })] })] }) },
    children: ch,
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log("OK", OUT); });
