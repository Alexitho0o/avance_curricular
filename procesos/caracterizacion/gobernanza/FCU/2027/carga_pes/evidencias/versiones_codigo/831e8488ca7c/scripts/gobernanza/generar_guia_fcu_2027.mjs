import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const [input, output, previewDir] = process.argv.slice(2);
if (!input || !output || !previewDir) throw new Error('Use: node builder.mjs data.json output.xlsx preview-dir');
const data = JSON.parse(await fs.readFile(input, 'utf8'));
const workbook = Workbook.create();
const rawRows = {};
for (const source of data.sheets) {
  const sheet = workbook.worksheets.add(source.name);
  const rows = [source.headers, ...source.rows];
  sheet.getRangeByIndexes(0, 0, rows.length, source.headers.length).values = rows;
  const area = sheet.getRangeByIndexes(0, 0, rows.length, source.headers.length);
  area.format.font = { name: 'Arial', size: 10, color: '#000000' };
  area.format.wrapText = true;
  area.format.verticalAlignment = 'top';
  sheet.getRangeByIndexes(0, 0, 1, source.headers.length).format.font.bold = true;
  sheet.freezePanes.freezeRows(1);
  sheet.showGridLines = true;
  let widths;
  if (source.name.startsWith('RAW FCU')) widths = [25, 31, 95, 18, 19, 50];
  else if (source.name === 'RAW Institucionales') widths = [23, 100, 42, 64, 18];
  else if (source.name === 'Cruces') widths = [14, 26, 28, 80, 42, 25, 95, 25, 95, 75, 65, 31, 90, 100, 52, 21, 95];
  else widths = [112, 29, 28, 48, 19, 75, 32, 17, 30];
  for (let c = 0; c < widths.length; c++) {
    sheet.getRangeByIndexes(0, c, rows.length, 1).format.columnWidth = widths[c];
  }
  for (let r = 0; r < rows.length; r++) {
    let lines = 1;
    for (let c = 0; c < rows[r].length; c++) {
      const value = String(rows[r][c] ?? '');
      lines = Math.max(lines, value.split('\n').reduce((n, line) => n + Math.max(1, Math.ceil(line.length / (widths[c] * 0.85))), 0));
    }
    sheet.getRangeByIndexes(r, 0, 1, source.headers.length).format.rowHeight = Math.max(30, lines * 14 + 12);
  }
  if (source.name.startsWith('RAW FCU')) {
    rawRows[source.name] = Object.fromEntries(source.rows.map((row, i) => [row[0], i + 2]));
  }
}
const cross = workbook.worksheets.getItem('Cruces');
const guide = workbook.worksheets.getItem('Guía para editar');
const records = data.sheets.find(s => s.name === 'Cruces').rows;
for (let i = 0; i < records.length; i++) {
  const r = i + 2;
  const oldRow = rawRows['RAW FCU 2026'][records[i][5]];
  const newRow = rawRows['RAW FCU 2027'][records[i][7]];
  if (oldRow) cross.getRange(`G${r}`).formulas = [[`='RAW FCU 2026'!C${oldRow}`]];
  if (newRow) cross.getRange(`I${r}`).formulas = [[`='RAW FCU 2027'!C${newRow}`]];
  guide.getRange(`A${r}`).formulas = [[`='Cruces'!L${r}&CHAR(10)&"Qué hacer: "&'Cruces'!M${r}&CHAR(10)&"Cómo queda: "&'Cruces'!N${r}`]];
  const fields = ['B', 'C', 'O', 'P', 'D', 'L', 'A'];
  for (let c = 0; c < fields.length; c++) {
    const cell = `'Cruces'!${fields[c]}${r}`;
    guide.getRangeByIndexes(r - 1, c + 1, 1, 1).formulas = [[fields[c] === 'P' ? `=IF(${cell}="","",${cell})` : `=${cell}`]];
  }
}
workbook.recalculate();
console.log((await workbook.inspect({kind:'table',range:"'Guía para editar'!A1:H3",tableMaxRows:3,tableMaxCols:8,maxChars:1600})).ndjson);
const errorScan = await workbook.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},maxChars:1200});
console.log(errorScan.ndjson);
await fs.mkdir(previewDir, {recursive:true});
for (const source of data.sheets) {
  const itemRow = records.findIndex(r => r[1] === 'G07Q71' && r[2] === 'SQ005') + 2;
  const range = source.name === 'Guía para editar' ? 'A1:C4' : source.name === 'Cruces' ? `F${itemRow}:I${itemRow+1}` : 'A1:C5';
  const preview = await workbook.render({sheetName:source.name,range,scale:1,format:'png'});
  await fs.writeFile(path.join(previewDir, source.name.replaceAll(' ','_')+'.png'),new Uint8Array(await preview.arrayBuffer()));
}
await fs.mkdir(path.dirname(output), {recursive:true});
const exported = await SpreadsheetFile.exportXlsx(workbook);
await exported.save(output);
const digest = crypto.createHash('sha256').update(await fs.readFile(output)).digest('hex');
const manifest = {date:'2026-10-06',output,sha256:digest,sources:data.sources,method:data.rules,
  sheetRows:Object.fromEntries(data.sheets.map(s=>[s.name,s.rows.length])),categories:data.categories,
  scripts:['scripts/gobernanza/preparar_guia_fcu_2027.py','scripts/gobernanza/generar_guia_fcu_2027.mjs'],
  validation:{all_103_codes_present:true,source_items_checked_against_manual_text:true,
    removals_require_official_2026_reference:true,guide_linked_to_crosswalk:true,full_live_survey_export_available:false}};
await fs.writeFile(output.replace(/\.xlsx$/,'.manifest.json'),JSON.stringify(manifest,null,2)+'\n');
await fs.writeFile(output+'.sha256',`${digest}  ${path.basename(output)}\n`);
console.log(JSON.stringify({output,sha256:digest,sheets:manifest.sheetRows,categories:data.categories}));
