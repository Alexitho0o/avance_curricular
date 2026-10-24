/** Autoría aislada de columnas MU2026. El payload no contiene estudiantes. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const [input, output, previews] = process.argv.slice(2);
if (!input || !output) {
  throw new Error('Uso: node generar_columnas_mu2026.mjs payload.json columnas.xlsx [directorio_previews]');
}
const payload = JSON.parse(await fs.readFile(input, 'utf8'));
const wb = Workbook.create();
for (const info of payload.sheets) {
  const s = wb.worksheets.add(info.name);
  const last = info.matrix.length;
  const target = s.getRange(`Q1:${info.end}${last}`);
  target.values = info.matrix;
  target.format.font = { name: 'Calibri', size: 11 };
  target.format.rowHeight = 15;
  target.setNumberFormat('@');
  const isTotal = info.name === '06_DETALLE_TOTAL';
  const nameColumn = isTotal ? 'R' : 'Q';
  const sectorColumn = isTotal ? 'S' : 'R';
  if (isTotal) s.getRange(`Q1:Q${last}`).format.columnWidth = 24;
  s.getRange(`${nameColumn}1:${nameColumn}${last}`).format.columnWidth = 100;
  s.getRange(`${sectorColumn}1:${sectorColumn}${last}`).format.columnWidth = 29;
  s.getRange(`${info.end}1:${info.end}${last}`).format.columnWidth = 24;
}
wb.recalculate();
if (previews) await fs.mkdir(previews, { recursive: true });
for (const info of payload.sheets) {
  const actual = wb.worksheets.getItem(info.name).getRange(`Q1:${info.end}${info.matrix.length}`).values;
  if (JSON.stringify(actual) !== JSON.stringify(info.matrix)) {
    throw new Error(`Valores de autoría distintos en ${info.name}`);
  }
  if (previews) {
    const blob = await wb.render({sheetName:info.name,range:`Q1:${info.end}9`,scale:1.5,format:'png'});
    await fs.writeFile(path.join(previews, `${info.name}.png`), new Uint8Array(await blob.arrayBuffer()));
  }
}
await fs.mkdir(path.dirname(output), { recursive: true });
const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(output);
console.log(JSON.stringify({output,filas:payload.sheets.map(s=>[s.name,s.matrix.length-1])}));
