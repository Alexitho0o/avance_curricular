import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const output = "/Users/alexi/Desktop/ESTRUCTURA_ETAPA3_ARANCELES_2027_CON_TITULOS.xlsx";
const previewDir = "/tmp/estructura-etapa3-aranceles-preview";
const headers = [
  "COD_SEDE", "NOMBRE_SEDE", "COD_CARRERA", "NOMBRE_CARRERA", "MODALIDAD",
  "COD_JORNADA", "VERSION", "FORMATO_VALOR", "VALOR_MATRICULA_ANUAL",
  "COSTO_TITULACION", "VALOR_CERTIFICADO_DIPLOMA", "ARANCEL_ANUAL", "VIGENCIA_CARRERA",
];
const dictionary = [
  ["A", "COD_SEDE", "NO", "Código SIES de la sede", "Numérico; conservar desde reporte 5910"],
  ["B", "NOMBRE_SEDE", "NO", "Nombre oficial de la sede", "Texto oficial; no abreviar"],
  ["C", "COD_CARRERA", "NO", "Código SIES de la carrera o programa", "Numérico; conservar"],
  ["D", "NOMBRE_CARRERA", "NO", "Nombre oficial de la carrera o programa", "Texto oficial; conservar"],
  ["E", "MODALIDAD", "NO", "Modalidad del programa", "1=Presencial; 2=Semipresencial; 3=No presencial"],
  ["F", "COD_JORNADA", "NO", "Jornada del programa", "1=Diurna; 2=Vespertina; 3=Semipresencial; 4=A distancia; 5=Otra"],
  ["G", "VERSION", "NO", "Versión del programa", "Numérico; conservar"],
  ["H", "FORMATO_VALOR", "SÍ", "Formato de los valores monetarios", "1=Pesos chilenos; 2=UF"],
  ["I", "VALOR_MATRICULA_ANUAL", "SÍ", "Valor anual de matrícula", "Numérico sin separadores; -1 solo cuando corresponda"],
  ["J", "COSTO_TITULACION", "SÍ", "Costo del proceso de titulación", "Numérico sin separadores; 0 si no corresponde"],
  ["K", "VALOR_CERTIFICADO_DIPLOMA", "SÍ", "Costo de certificado o diploma", "Numérico sin separadores; 0 si no corresponde"],
  ["L", "ARANCEL_ANUAL", "SÍ", "Valor del arancel anual", "Numérico sin separadores; -1 solo cuando corresponda"],
  ["M", "VIGENCIA_CARRERA", "NO", "Estado de vigencia del registro", "Conservar desde reporte consolidado"],
];

const wb = Workbook.create();
const structure = wb.worksheets.add("Etapa 3 - Aranceles");
structure.showGridLines = false;
structure.getRange("A1:M1").values = [headers];
structure.getRange("A1:M1").format = {
  fill: "#17365D", font: { bold: true, color: "#FFFFFF", size: 10 },
  wrapText: true, rowHeight: 42, verticalAlignment: "center", horizontalAlignment: "center",
  borders: { preset: "all", style: "thin", color: "#D9E2F3" },
};
structure.getRange("A2:G2").format.fill = "#E7E6E6";
structure.getRange("H2:L2").format.fill = "#FFF2CC";
structure.getRange("M2").format.fill = "#E7E6E6";
structure.getRange("A2:M2").format.rowHeight = 24;
structure.getRange("A1:M2").format.font.name = "Aptos";
structure.getRange("A:A").format.columnWidth = 13;
structure.getRange("B:B").format.columnWidth = 28;
structure.getRange("C:C").format.columnWidth = 15;
structure.getRange("D:D").format.columnWidth = 36;
structure.getRange("E:G").format.columnWidth = 14;
structure.getRange("H:H").format.columnWidth = 17;
structure.getRange("I:L").format.columnWidth = 24;
structure.getRange("M:M").format.columnWidth = 19;
structure.freezePanes.freezeRows(1);
structure.tables.add("A1:M2", true, "EstructuraEtapa3");

const dict = wb.worksheets.add("Diccionario");
dict.showGridLines = false;
dict.getRange("A1:E1").values = [["Columna", "Campo", "Modificable", "Descripción", "Regla base"]];
dict.getRangeByIndexes(1, 0, dictionary.length, 5).values = dictionary;
dict.getRange("A1:E1").format = { fill: "#17365D", font: { bold: true, color: "#FFFFFF" }, rowHeight: 26 };
dict.getRange("A2:E14").format = { wrapText: true, font: { name: "Aptos", size: 10 }, borders: { preset: "inside", style: "thin", color: "#D9E2F3" } };
dict.getRange("C2:C14").conditionalFormats.add("containsText", { text: "SÍ", format: { fill: "#FFF2CC", font: { bold: true, color: "#7F6000" } } });
dict.getRange("A:A").format.columnWidth = 11;
dict.getRange("B:B").format.columnWidth = 31;
dict.getRange("C:C").format.columnWidth = 15;
dict.getRange("D:D").format.columnWidth = 38;
dict.getRange("E:E").format.columnWidth = 58;
dict.freezePanes.freezeRows(1);

const notes = wb.worksheets.add("Instrucciones");
notes.showGridLines = false;
notes.getRange("A1:F1").merge();
notes.getRange("A1").values = [["Etapa 3 - Definición de Arancel TP 2027"]];
notes.getRange("A1:F1").format = { fill: "#17365D", font: { bold: true, color: "#FFFFFF", size: 16 }, rowHeight: 32 };
notes.getRange("A3:B10").values = [
  ["Proceso", "Oferta Académica-Acceso 2027, Proceso 2026"],
  ["Ventana", "07 al 11 de septiembre de 2026"],
  ["Carga PES", "ID 17454 - Oferta Académica Aranceles"],
  ["Fuente normativa", "Instructivo Oferta Académica-Acceso CFT-IP 2027, Anexo 3, páginas 42 a 49"],
  ["Base obligatoria", "Descargar el reporte 5910 Oferta Académica Vigente y Nueva Validada 2027 TP Adscritas"],
  ["Campos editables", "FORMATO_VALOR, VALOR_MATRICULA_ANUAL, COSTO_TITULACION, VALOR_CERTIFICADO_DIPLOMA y ARANCEL_ANUAL"],
  ["Campos protegidos", "COD_SEDE, NOMBRE_SEDE, COD_CARRERA, NOMBRE_CARRERA, MODALIDAD, COD_JORNADA, VERSION y VIGENCIA_CARRERA"],
  ["Advertencia", "Esta estructura contiene títulos para trabajo en Excel. El archivo final de carga debe ajustarse al formato real descargado de PES y cargarse sin encabezados."],
];
notes.getRange("A3:A10").format = { fill: "#D9EAF7", font: { bold: true }, wrapText: true };
notes.getRange("B3:B10").format = { wrapText: true };
notes.getRange("A3:B10").format.borders = { preset: "inside", style: "thin", color: "#D9E2F3" };
notes.getRange("A:A").format.columnWidth = 25;
notes.getRange("B:B").format.columnWidth = 95;
notes.getRange("A1:F10").format.font.name = "Aptos";

await fs.mkdir(previewDir, { recursive: true });
for (const sheetName of ["Etapa 3 - Aranceles", "Diccionario", "Instrucciones"]) {
  const png = await wb.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(`${previewDir}/${sheetName.replaceAll(" ", "_")}.png`, new Uint8Array(await png.arrayBuffer()));
}
const errors = await wb.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula error scan" });
await fs.writeFile(`${previewDir}/errors.ndjson`, errors.ndjson);
const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(output);
console.log(JSON.stringify({ output, bytes: (await fs.stat(output)).size, sheets: 3, columns: headers.length }));
