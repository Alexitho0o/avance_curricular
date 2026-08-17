import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const source = "/Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/06_validaciones/VALIDACION_REGLAS_MANUAL_ETAPA1_DOCENCIA02_20260817_104928.json";
const output = "/Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/10_entrega/REPORTE_PENDIENTES_REALES_ETAPA1_OFERTA_ACADEMICA_20260817.xlsx";
const previewDir = "/tmp/reporte-pendientes-etapa1-preview";

const data = JSON.parse(await fs.readFile(source, "utf8"));
const blockers = data.hallazgos.filter((x) => x.severidad === "BLOQUEANTE");
const reviews = data.hallazgos.filter((x) => x.severidad !== "BLOQUEANTE");
const counts = new Map();
for (const item of blockers) {
  const key = item.campo;
  if (!counts.has(key)) counts.set(key, { count: 0, rule: item.regla_id, detail: item.detalle });
  counts.get(key).count += 1;
}

const wb = Workbook.create();
const summary = wb.worksheets.add("Resumen");
summary.showGridLines = false;
summary.getRange("A1:F1").merge();
summary.getRange("A1").values = [["Oferta Académica 2027 - Reporte de pendientes Etapa 1"]];
summary.getRange("A1:F1").format = { fill: "#1F4E78", font: { bold: true, color: "#FFFFFF", size: 16 }, rowHeight: 30 };
summary.getRange("A3:B8").values = [
  ["Control", "Resultado"],
  ["Registros validados", data.resumen.total_registros],
  ["Columnas de carga", data.resumen.total_columnas],
  ["Reglas catalogadas", data.resumen.reglas_catalogadas],
  ["Pendientes bloqueantes", blockers.length],
  ["Estado", blockers.length ? "NO CARGAR A SIES" : "VALIDACIÓN OK"],
];
summary.getRange("A3:B3").format = { fill: "#D9EAF7", font: { bold: true, color: "#1F1F1F" } };
summary.getRange("A4:A8").format.font = { bold: true };
summary.getRange("B8").format = { fill: blockers.length ? "#F4CCCC" : "#D9EAD3", font: { bold: true, color: blockers.length ? "#9C0006" : "#274E13" } };

const grouped = [["Campo o control", "Casos", "Regla", "Condición incumplida"]];
for (const [field, item] of counts) grouped.push([field, item.count, item.rule, item.detail]);
summary.getRangeByIndexes(10, 0, grouped.length, 4).values = grouped;
summary.getRange(`A11:D11`).format = { fill: "#1F4E78", font: { bold: true, color: "#FFFFFF" } };
summary.getRange(`A12:D${10 + grouped.length}`).format.borders = { preset: "inside", style: "thin", color: "#D9E2F3" };

summary.getRange("A18:F18").merge();
summary.getRange("A18").values = [["Criterio de integración confirmado"]];
summary.getRange("A18:F18").format = { fill: "#D9EAF7", font: { bold: true, color: "#1F1F1F" } };
summary.getRange("A19:F23").values = [
  ["El Excel fuente contiene 50 columnas de trabajo; no es directamente el archivo de carga.", "", "", "", "", ""],
  ["VERSION se repuso desde la precarga SIES y se verificó fila por fila.", "", "", "", "", ""],
  ["CODIGO_IES_NUM y los dos controles DFE se conservan como trazabilidad, pero se excluyen de la carga.", "", "", "", "", ""],
  ["Las etiquetas SI/NO fueron convertidas a sus códigos PES antes de validar.", "", "", "", "", ""],
  ["MALLA_CURRICULAR y PERFIL_EGRESO no integran la estructura oficial de 48 columnas; se registran como observación, no como faltante de carga.", "", "", "", "", ""],
];
for (let r = 19; r <= 23; r += 1) summary.getRange(`A${r}:F${r}`).merge();
summary.getRange("A19:F23").format = { wrapText: true, font: { size: 10 }, rowHeight: 28 };
summary.freezePanes.freezeRows(3);
summary.getRange("A1:F23").format.font.name = "Aptos";
summary.getRange("A1:A23").format.columnWidth = 34;
summary.getRange("B1:B23").format.columnWidth = 18;
summary.getRange("C1:C23").format.columnWidth = 14;
summary.getRange("D1:F23").format.columnWidth = 27;

const detail = wb.worksheets.add("Detalle bloqueantes");
detail.showGridLines = false;
const headers = ["Regla", "Fila Excel", "Código carrera", "Carrera", "Modalidad", "Jornada", "Versión", "Campo", "Valor observado", "Pendiente / condición"];
const rows = blockers.map((x) => [x.regla_id, x.fila, x.cod_carrera, x.nombre_carrera, x.modalidad, x.cod_jornada, x.version, x.campo, x.valor, x.detalle]);
detail.getRangeByIndexes(0, 0, rows.length + 1, headers.length).values = [headers, ...rows];
detail.getRange("A1:J1").format = { fill: "#1F4E78", font: { bold: true, color: "#FFFFFF" }, wrapText: true, rowHeight: 30 };
detail.getRange(`A2:J${rows.length + 1}`).format = { font: { name: "Aptos", size: 10 }, wrapText: true, borders: { preset: "inside", style: "thin", color: "#E7E6E6" } };
detail.getRange(`H2:J${rows.length + 1}`).format.fill = "#FCE8E6";
detail.getRange(`A1:J${rows.length + 1}`).format.autofitColumns();
detail.getRange("A:A").format.columnWidth = 11;
detail.getRange("B:B").format.columnWidth = 12;
detail.getRange("C:C").format.columnWidth = 14;
detail.getRange("D:D").format.columnWidth = 38;
detail.getRange("E:G").format.columnWidth = 12;
detail.getRange("H:H").format.columnWidth = 32;
detail.getRange("I:I").format.columnWidth = 18;
detail.getRange("J:J").format.columnWidth = 52;
detail.freezePanes.freezeRows(1);
detail.freezePanes.freezeColumns(3);
detail.tables.add(`A1:J${rows.length + 1}`, true, "PendientesEtapa1");

const notes = wb.worksheets.add("Observaciones estructura");
notes.showGridLines = false;
notes.getRange("A1:E1").merge();
notes.getRange("A1").values = [["Observaciones que no son columnas faltantes del archivo de carga"]];
notes.getRange("A1:E1").format = { fill: "#5B9BD5", font: { bold: true, color: "#FFFFFF", size: 14 }, rowHeight: 28 };
notes.getRange("A3:E3").values = [["Regla", "Campo", "Estado", "Motivo", "Tratamiento"]];
notes.getRange("A3:E3").format = { fill: "#D9EAF7", font: { bold: true } };
const noteRows = reviews.map((x) => [x.regla_id, x.campo, "OBSERVACIÓN", x.detalle, "No bloquear por ausencia en la estructura oficial de 48 columnas"]);
notes.getRangeByIndexes(3, 0, noteRows.length, 5).values = noteRows;
notes.getRange(`A4:E${3 + noteRows.length}`).format = { wrapText: true, borders: { preset: "inside", style: "thin", color: "#D9E2F3" } };
notes.getRange("A:A").format.columnWidth = 12;
notes.getRange("B:B").format.columnWidth = 24;
notes.getRange("C:C").format.columnWidth = 18;
notes.getRange("D:E").format.columnWidth = 50;
notes.getRange("A1:E6").format.font.name = "Aptos";

await fs.mkdir(previewDir, { recursive: true });
for (const sheetName of ["Resumen", "Detalle bloqueantes", "Observaciones estructura"]) {
  const image = await wb.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(`${previewDir}/${sheetName.replaceAll(" ", "_")}.png`, new Uint8Array(await image.arrayBuffer()));
}

const check = await wb.inspect({ kind: "table", range: "Resumen!A1:F23", include: "values,formulas", tableMaxRows: 23, tableMaxCols: 6, maxChars: 5000 });
await fs.writeFile(`${previewDir}/inspection.ndjson`, check.ndjson);
const errors = await wb.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula error scan" });
await fs.writeFile(`${previewDir}/errors.ndjson`, errors.ndjson);

await fs.mkdir(new URL(".", `file://${output}`).pathname, { recursive: true });
const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(output);
console.log(JSON.stringify({ output, bytes: (await fs.stat(output)).size, blockers: blockers.length, reviews: reviews.length, rows: data.resumen.total_registros, columns: data.resumen.total_columnas }));
