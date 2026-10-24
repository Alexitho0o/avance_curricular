import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const [input, output, previewDir] = process.argv.slice(2);
const payload = JSON.parse(await fs.readFile(input,'utf8'));
const workbook = Workbook.create();
for (const spec of payload.sheets) {
  const sheet = workbook.worksheets.add(spec.name);
  sheet.showGridLines = false;
  sheet.getRange('A1').values = [[payload.title]];
  sheet.getRange('A1').format.font = {name:'Arial',size:14,bold:true};
  sheet.getRange('A2').values = [['Corte '+payload.cutoff+'; Hoy por fecha de envio de encuesta.']];
  const data = [spec.headers,...spec.rows].map(row => row.map(value =>
    typeof value === 'string' && value.startsWith('=') ? "'"+value : value));
  sheet.getRangeByIndexes(3,0,data.length,spec.headers.length).values = data;
  const body = sheet.getRangeByIndexes(3,0,data.length,spec.headers.length);
  body.format.font = {name:'Arial',size:11,color:'#222222'};
  body.format.wrapText = true;
  body.format.verticalAlignment = 'top';
  const header = sheet.getRangeByIndexes(3,0,1,spec.headers.length);
  header.format.font.bold = true;
  header.format.rowHeight = 36;
  header.format.borders = {bottom:{style:'thin',color:'#777777'}};
  for (let col=0; col<spec.headers.length; col++) {
    sheet.getRangeByIndexes(3,col,data.length,1).format.columnWidth = spec.widths[col] ?? 28;
  }
  for (let index=0; index<spec.rows.length; index++) {
    const lines = Math.max(...spec.rows[index].map((value,col) => String(value ?? '').split('\n')
      .reduce((n,line) => n+Math.max(1,Math.ceil(line.length/((spec.widths[col] ?? 28)*.9))),0)));
    sheet.getRangeByIndexes(index+4,0,1,spec.headers.length).format.rowHeight = Math.max(28,lines*15+8);
  }
  for (const col of spec.date_columns ?? []) {
    for (let row=0; row<spec.rows.length; row++) {
      const value = spec.rows[row][col];
      if (value) {
        const localDate = new Date(value+'Z');
        assert(Number.isFinite(localDate.getTime()), 'Fecha local invalida en '+spec.name);
        sheet.getRangeByIndexes(row+4,col,1,1).values = [[localDate]];
      }
    }
    if (spec.rows.length) sheet.getRangeByIndexes(4,col,spec.rows.length,1).setNumberFormat('dd-mm-yyyy hh:mm:ss');
  }
  if (spec.name !== 'Resumen') {
    sheet.freezePanes.freezeRows(4);
    sheet.freezePanes.freezeColumns(spec.name === 'Mapa 2027' ? 2 : 3);
  }
  for (const [index, note] of (spec.source_notes ?? []).entries()) {
    const range = sheet.getRangeByIndexes(3+index,spec.headers.length+1,1,1);
    range.values = [[note]];
    range.format.columnWidth = 95;
    range.format.wrapText = true;
    range.format.font = {name:'Arial',size:11,color:'#222222'};
    range.format.verticalAlignment = 'top';
    range.format.rowHeight = Math.max(36,Math.ceil(note.length/80)*15+8);
  }
}
const summarySpec = payload.sheets[0];
const summary = workbook.worksheets.getItem('Resumen');
const detail = payload.sheets.find(sheet => sheet.name === payload.detail_sheet);
const last = Math.max(5,detail.rows.length+4);
for (let index=0; index<summarySpec.rows.length; index++) {
  const row = index+5;
  const sourceState = summarySpec.rows[index][8];
  if (sourceState === 'DISPONIBLE') {
    summary.getRange('G'+row).formulas = [["=COUNTIFS('"+payload.detail_sheet+"'!$H$5:$H$"+last+",$B"+row+")"]];
    summary.getRange('H'+row).formulas = [["=COUNTIFS('"+payload.detail_sheet+"'!$H$5:$H$"+last+",$B"+row+",'"+payload.detail_sheet+"'!$P$5:$P$"+last+",1)"]];
  } else {
    summary.getRange('G'+row+':H'+row).values = [['No disponible','No disponible']];
  }
}
summary.getRange('A'+(summarySpec.rows.length+7)).values = [[payload.source]];
workbook.recalculate();
for (let index=0; index<summarySpec.rows.length; index++) {
  if (summarySpec.rows[index][8] !== 'DISPONIBLE') continue;
  assert.equal(summary.getRange('G'+(index+5)).values[0][0],summarySpec.rows[index][6]);
  assert.equal(summary.getRange('H'+(index+5)).values[0][0],summarySpec.rows[index][7]);
}
const errors = await workbook.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!',
  options:{useRegex:true,maxResults:30},maxChars:1000});
await fs.mkdir(previewDir,{recursive:true});
await fs.writeFile(path.join(previewDir,'formula_check.ndjson'),errors.ndjson);
for (const spec of payload.sheets) {
  const columns = spec.name === 'Resumen' ? 'I' : (spec.name === 'Mapa 2027' ? 'D' : 'F');
  const preview = await workbook.render({sheetName:spec.name,range:'A1:'+columns+Math.min(10,spec.rows.length+4),scale:1,format:'png'});
  await fs.writeFile(path.join(previewDir,spec.name+'.png'),new Uint8Array(await preview.arrayBuffer()));
  for (const range of spec.preview_ranges ?? []) {
    const changed = await workbook.render({sheetName:spec.name,range,scale:1,format:'png'});
    await fs.writeFile(path.join(previewDir,spec.name+'_'+range.replace(':','_')+'.png'),new Uint8Array(await changed.arrayBuffer()));
  }
}
await (await SpreadsheetFile.exportXlsx(workbook)).save(output);
console.log(JSON.stringify({file:output,sheets:payload.sheets.map(s => ({name:s.name,rows:s.rows.length}))}));
