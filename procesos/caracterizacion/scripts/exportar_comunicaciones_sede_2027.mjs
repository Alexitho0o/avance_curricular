import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const [input, output, previewDir] = process.argv.slice(2);
const payload = JSON.parse(await fs.readFile(input,'utf8'));
assert(payload.rows.length > 0, 'No generar comunicaciones vacias.');
assert.equal(payload.headers.length,11);
const workbook = Workbook.create();
const sheet = workbook.worksheets.add('BD');
sheet.showGridLines = false;
sheet.getRange('A1').values = [[payload.title]];
sheet.getRange('A1').format.font = {name:'Arial',size:14,bold:true};
const data = [payload.headers,...payload.rows].map(row => row.map(value =>
  typeof value === 'string' && value.startsWith('=') ? "'"+value : value));
sheet.getRangeByIndexes(2,0,data.length,11).values = data;
const body = sheet.getRangeByIndexes(2,0,data.length,11);
body.format.font = {name:'Arial',size:11,color:'#222222'};
body.format.wrapText = true;
body.format.verticalAlignment = 'center';
const table = sheet.tables.add('A3:K'+(payload.rows.length+3),true,'BDPatagonia');
table.style = 'TableStyleMedium2';
table.showFilterButton = true;
for (let col=0; col<11; col++) {
  sheet.getRangeByIndexes(2,col,data.length,1).format.columnWidth = payload.widths[col];
}
const header = sheet.getRange('A3:K3');
header.format.fill = '#1F4E78';
header.format.font = {name:'Arial',size:11,color:'#FFFFFF',bold:true};
header.format.rowHeight = 30;
for (let index=0; index<payload.rows.length; index++) {
  const values = payload.rows[index];
  const lines = Math.max(...values.map((v,col) => Math.max(1,Math.ceil(String(v ?? '').length/(payload.widths[col]*.9)))));
  const row = sheet.getRangeByIndexes(index+3,0,1,11);
  row.format.rowHeight = Math.max(24,lines*15+8);
  if (values[8] === 'NUEVO') {
    row.format.fill = '#E2F0D9';
    row.format.font.bold = true;
  }
}
sheet.freezePanes.freezeRows(1);
workbook.recalculate();
assert.deepEqual(sheet.getRangeByIndexes(3,0,payload.rows.length,11).values,data.slice(1));
const errors = await workbook.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!',
  options:{useRegex:true,maxResults:30},maxChars:1000});
await fs.mkdir(previewDir,{recursive:true});
await fs.writeFile(path.join(previewDir,'formula_check.ndjson'),errors.ndjson);
for (const [name,range] of [['contactos','A1:F'+(payload.rows.length+3)],['estado_sede','G1:K'+(payload.rows.length+3)]]) {
  const preview = await workbook.render({sheetName:'BD',range,scale:1,format:'png'});
  await fs.writeFile(path.join(previewDir,name+'.png'),new Uint8Array(await preview.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(workbook)).save(output);
console.log(JSON.stringify({file:output,sede:'PATAGONIA',rows:payload.rows.length}));
