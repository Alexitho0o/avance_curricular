const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  HeadingLevel, AlignmentType, PageOrientation, LevelFormat, TableOfContents, Footer, PageNumber, BorderStyle,
} = require("docx");

const data = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const OUT = process.argv[3];
const TW = 15398; // A4 landscape content width (16838 - 2*720)

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
    children: [new Paragraph({ children: [new TextRun({ text: String(t ?? ""), size: head ? 17 : 16, bold: head, color: head ? "FFFFFF" : "000000" })] })],
  });
  return new Table({
    width: { size: TW, type: WidthType.DXA }, columnWidths: w,
    rows: [new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, i, true)) }),
      ...rows.map((r) => new TableRow({ children: r.map((c, i) => cell(c, i, false, i === prioIdx ? PRIO[c] : undefined)) }))],
  });
}
const gap = () => new Paragraph({ spacing: { after: 80 }, children: [] });

const dic = data.dic;
const up = (id) => dic.find((d) => d.ID === id);
const byPrio = (p) => dic.filter((d) => d["PRIORIDAD"] === p).length;

const children = [];
children.push(new Paragraph({ alignment: AlignmentType.LEFT, spacing: { after: 60 }, children: [new TextRun({ text: "Requerimiento funcional", size: 24, color: "1F3864" })] }));
children.push(new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: "Reporte Regulatorio Maestro de Estudiantes en U+ para procesos SIES/PES", bold: true, size: 40, color: "1F3864" })] }));
children.push(new Paragraph({ spacing: { after: 200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: "1F3864", space: 4 } },
  children: [new TextRun({ text: "Instituto Profesional San Sebastián (código IES 162) · Proveedor: Bettersoft · Versión borrador para revisión institucional · 22-09-2026", size: 18, color: "555555" })] }));
children.push(new TableOfContents("Contenido", { hyperlink: true, headingStyleRange: "1-2" }));

// 1
children.push(H1("1. Objetivo"));
children.push(P("Crear en U+ un reporte institucional que concentre los datos de estudiantes que la institución debe informar a la Subsecretaría de Educación Superior (SIES) mediante la Plataforma de Educación Superior (PES). El reporte debe conservar la trazabilidad entre el dato registrado en U+ y el dato que finalmente se informa, entregando ambos cuando exista una codificación distinta."));
children.push(P("Hoy los archivos SIES se construyen descargando el reporte \"Datos Alumnos\" y el reporte de notas por asignatura, y aplicando fuera de U+ cruces, homologaciones y cálculos. El resultado buscado es: U+ → reporte regulatorio → validación → archivo SIES, sin planillas intermedias."));
children.push(P("Este documento no diseña la solución técnica en U+. Describe qué dato se necesita, con qué definición, a qué nivel de detalle y con qué reglas de extracción."));

// 2
children.push(H1("2. Alcance"));
children.push(P("Procesos que usan datos de estudiantes de U+ y que quedan dentro del alcance:"));
[["Matrícula Unificada (pregrado y posgrado/postítulo). ", "Carga anual con corte estadístico al 30 de abril (pregrado) y 15 de mayo (posgrado). Es el proceso que más depende de U+ (32 campos)."],
 ["Avance Curricular. ", "Informa, por matrícula del año anterior, si el estudiante cursó cada semestre y cuántas unidades del plan cursó y aprobó (año y acumulado). Incluye un catálogo de planes."],
 ["Estudiantes Extranjeros (regulares). ", "Estudiantes con nacionalidad extranjera matriculados o con actividad en el año anterior."],
 ["Ficha de Caracterización Única (FCU). ", "Encuesta a estudiantes de primer año; U+ aporta solo los datos de identificación y contacto que se precargan."]].forEach(([b, t]) => children.push(B(t, b)));
children.push(P("Fuera de alcance, porque sus datos no provienen de estudiantes en U+: Oferta Académica (atributos de programa), Infraestructura y Recursos Educacionales, Personal Académico y las variables de encuesta de la FCU. Las secciones de estudiantes de Índices CNED (origen, residencia, egresados y titulados) quedan como potencial futuro sin requerimiento confirmado."));

// 3
children.push(H1("3. Estructura requerida"));
children.push(P(`El reporte principal tiene una fila por matrícula (CODCLI) y período consultado. Se solicitan ${dic.length} columnas o grupos de columnas: ${byPrio("P1")} de prioridad P1 (crítica), ${byPrio("P2")} P2 (alta), ${byPrio("P3")} P3 (media) y ${byPrio("P4")} P4 (baja). Dos extractos complementarios usan otro nivel de detalle: el catálogo de planes (una fila por plan) y el detalle académico por asignatura (una fila por asignatura cursada).`));
children.push(P("Prioridades: P1 = dato obligatorio para SIES que hoy se obtiene manualmente o con cruces complejos; P2 = el dato existe en U+ pero requiere codificación SIES, historia o nueva exposición; P3 = simplifica controles; P4 = útil para auditoría, no bloquea cargas."));
children.push(table(["Nº", "ID", "Bloque", "Columna solicitada", "Nivel", "Tipo", "Procesos", "Prioridad"],
  dic.map((d) => [d["Nº"], d.ID, d.BLOQUE, d["CAMPO SOLICITADO"], d.NIVEL, d.TIPO, d["PROCESOS QUE LO UTILIZAN"], d.PRIORIDAD]), [4, 6, 12, 26, 14, 10, 18, 7], 7));

// 4
children.push(H1("4. Definición funcional de cada columna"));
children.push(P("\"Campo U+ actual\" indica dónde está hoy el dato (o si no existe). \"Transformación\" describe cómo se obtiene el valor SIES. Los ejemplos son ficticios."));
const bloques = [...new Set(dic.map((d) => d.BLOQUE))];
for (const b of bloques) {
  children.push(H2(b));
  children.push(table(["ID", "Columna", "Definición funcional", "Campo U+ actual", "Transformación", "Ejemplo", "Temporalidad"],
    dic.filter((d) => d.BLOQUE === b).map((d) => [d.ID, d["CAMPO SOLICITADO"], d["DEFINICIÓN FUNCIONAL"], d["CAMPO U+ ACTUAL"], d["TRANSFORMACIÓN"], d.EJEMPLO, d.TEMPORALIDAD]),
    [6, 16, 40, 14, 14, 10, 12]));
}

// 5
children.push(H1("5. Catálogos"));
children.push(P("Regla general: cuando U+ usa un código propio, el reporte debe entregar el código original de U+ y, en otra columna, el código SIES. El código SIES solo se calcula en U+ cuando la equivalencia está confirmada; los casos marcados como pendientes deben quedar vacíos o marcados hasta que la institución los resuelva."));
const catSel = [
  ["SEXO", "Sexo"], ["JORNADA", "Jornada"], ["MODALIDAD_PROGRAMA", "Modalidad del programa (SIES)"], ["SEDE", "Sede"], ["TIPO_DOCUMENTO", "Tipo de documento"],
  ["NACIONALIDAD", "Nacionalidad"], ["FOR_ING_ACT", "Forma de ingreso a la carrera actual"], ["PERIODO_INGRESO -> SEMESTRE", "Período de ingreso → semestre"],
  ["ESTADO_CIVIL", "Estado civil (FCU)"], ["TIPO_UNIDAD_MEDIDA", "Tipo de unidad de medida del plan (Avance Curricular)"],
];
for (const [k, t] of catSel) {
  const rows = data.cat.filter((c) => c.CATALOGO === k);
  if (!rows.length) continue;
  children.push(H2(t));
  children.push(table(["Proceso", "Lado", "Código", "Significado", "Equivale a", "Estado"],
    rows.map((c) => [c.PROCESO, c.LADO, c.CODIGO, c.SIGNIFICADO, c.HOMOLOGA_A, c.ESTADO]), [18, 12, 16, 26, 16, 18]));
}
children.push(H2("Vigencia: cuatro significados distintos"));
children.push(P("La palabra \"vigencia\" no significa lo mismo en cada proceso y no debe calcularse una equivalencia única en U+. U+ debe entregar estado académico y situación con sus fechas (columnas UP-42 y UP-43); la institución aplica la regla de cada proceso."));
children.push(table(["Proceso", "Código", "Significado"],
  data.cat.filter((c) => c.CATALOGO.startsWith("VIG") && c.LADO === "SIES").map((c) => [c.CATALOGO + " · " + c.PROCESO, c.CODIGO, c.SIGNIFICADO]), [30, 8, 62]));

// 6
children.push(H1("6. Requerimientos históricos"));
children.push(P("Varios datos SIES se refieren a una fecha o a un año anterior, pero el reporte actual solo muestra el valor vigente al momento de descargar. U+ debe poder entregar estos datos a una fecha de corte o para un año de referencia:"));
dic.filter((d) => d.REQUERIMIENTO_HISTORICO === "SI").forEach((d) => children.push(B(` — ${d.TEMPORALIDAD}.`, `${d.ID} ${d["CAMPO SOLICITADO"]}`)));

// 7
children.push(H1("7. Llaves"));
[["CODCLI: ", "llave de la fila; identifica la matrícula de una persona en una carrera/plan. Debe estar presente en todos los extractos, incluido el detalle por asignatura (hoy ese reporte se cruza por RUT + código de carrera)."],
 ["ID_PERSONA_UPLUS (si existe) y documento: ", "agrupan todas las matrículas de una persona. Hoy 1.754 personas tienen más de un CODCLI."],
 ["CODCLI_ORIGEN: ", "vincula la matrícula actual con la matrícula desde la que la persona llegó (cambio de carrera, continuidad, articulación)."],
 ["CODIGO_UNICO_SIES: ", "vincula la matrícula con el programa oficial SIES (sede, carrera, jornada, versión). Debe administrarse en U+ como atributo de la oferta/plan, con vigencia por año."],
 ["PLAN_ESTUDIO_UPLUS: ", "vincula la matrícula con el catálogo de planes y con el detalle por asignatura."]].forEach(([b, t]) => children.push(B(t, b)));

// 8
children.push(H1("8. Reglas de extracción"));
[["Parámetros: ", "año y período de matrícula, fecha de corte (por ejemplo 30-04 o 31-12) y año de referencia académico (para promedios, asignaturas y avance). Filtro opcional por nivel global (pregrado, posgrado, postítulo) y sede."],
 ["Universo: ", "una fila por CODCLI con matrícula en el período seleccionado, incluyendo retirados y eliminados con su estado a la fecha de corte (SIES exige informarlos con la vigencia que corresponda)."],
 ["Granularidad: ", "no mezclar atributos de persona con atributos de matrícula: sede, jornada, plan, nivel y estado pertenecen a la matrícula y al período."],
 ["Formato: ", "texto UTF-8 o Excel con encabezados; fechas dd/mm/aaaa; códigos sin espacios al inicio o al final; situación separada en código y descripción."],
 ["Datos personales: ", "el reporte regulatorio no debe incluir columnas sin uso SIES demostrado (responsable financiero, datos laborales, tramo de renta, número de hijos, contactos de emergencia, ejecutivo comercial, marketing, arancel)."]].forEach(([b, t]) => children.push(B(t, b)));

// 9
children.push(H1("9. Validaciones mínimas"));
["CODCLI único y no nulo; mismo documento y fecha de nacimiento en todos los CODCLI de una persona.",
 "Dígito verificador válido (módulo 11); si el documento es pasaporte, DV vacío y nacionalidad distinta de Chile (38).",
 "CODIGO_UNICO_SIES existente en la oferta del año; jornada y modalidad coherentes (jornada 1 o 2 no puede tener modalidad 3; jornada 4 solo con modalidad 3).",
 "Año de ingreso de origen menor o igual al de la carrera actual; año 1900 solo con semestre 0; ingreso directo (forma 1, 6-10) implica origen igual a actual.",
 "Asignaturas aprobadas ≤ inscritas (año e histórico); promedios 0 o entre 100 y 700; unidades aprobadas totales ≤ total del plan × 1,25.",
 "Nivel académico entre 1 y la duración de la carrera; máximo 2 si ingresó en el año de proceso.",
 "Semestres suspendidos previos ≤ semestres transcurridos desde el ingreso; 0 si ingresó en el año de proceso.",
 "Nombres y apellidos normalizados sin tildes, sin espacios dobles ni al inicio/fin."].forEach((t) => children.push(B(t)));

// 10
children.push(H1("10. Casos pendientes"));
children.push(P("Estos puntos no tienen respaldo suficiente y deben resolverse (Bettersoft documentando U+ o la institución decidiendo) antes de fijar la codificación SIES en el reporte:"));
children.push(table(["ID", "Tema", "Situación", "Qué se requiere"],
  data.ct.map((c) => [c.ID, c.TEMA, c.AFIRMA_1 + " / " + c.AFIRMA_2, c.ESTADO]), [6, 18, 50, 26]));
children.push(gap());
children.push(P("Además, Bettersoft debe documentar el significado en U+ de: SEXO = S; PERIODOINGRESO y PERIODOMATRICULA = 3; NIVEL = 20; MATRICULA = 1/2; el régimen del plan; y la definición temporal de FECHAMATRICULA y ANOMATRICULA."));

children.push(H1("Anexo. Brechas y cambios solicitados"));
children.push(table(["ID", "Campo", "Situación actual", "Cambio solicitado", "Procesos", "Prioridad"],
  data.br.map((b) => [b.ID, b.CAMPO, b["SITUACIÓN ACTUAL"], b["CAMBIO SOLICITADO"], b["PROCESOS AFECTADOS"], b.PRIORIDAD]), [6, 16, 24, 36, 11, 7], 5));

const doc = new Document({
  creator: "IPSS", title: "Requerimiento Reporte Regulatorio Maestro U+",
  styles: { default: { document: { run: { font: "Calibri", size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 30, bold: true, color: "1F3864" }, paragraph: { outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 24, bold: true, color: "2E5597" }, paragraph: { outlineLevel: 1 } }] },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838, orientation: PageOrientation.LANDSCAPE }, margin: { top: 720, bottom: 720, left: 720, right: 720 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Requerimiento Reporte Regulatorio Maestro U+ · página ", size: 16, color: "777777" }), new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "777777" })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log("OK", OUT); });
