import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const [input, output, previewDir] = process.argv.slice(2);
const payload = JSON.parse(await fs.readFile(input,'utf8'));
const workbook = Workbook.create();
const widths = {
  Preguntas:[8,32,18,74,28,54,54,16,32],
  Detalle:[10,32,18,55,24,20,76,10,32,32]
};
function literal(value) {
  return typeof value==='string' && value.startsWith('=') ? "'"+value : value;
}
function lineCount(value,width) {
  return String(value ?? '').split('\n').reduce((count,line)=>count+Math.max(1,Math.ceil(line.length/(width*.9))),0);
}
for(const [name,table] of Object.entries(payload.tables)) {
  const sheet=workbook.worksheets.add(name);
  sheet.showGridLines=false;
  sheet.getRange('A2').values=[['Instrumento '+payload.instrument.year+' P'+payload.instrument.period+' · Encuesta '+payload.instrument.survey_id]];
  sheet.getRange('A2').format.font={name:'Arial',size:14,bold:true};
  const data=[table.headers,...table.rows].map(row=>row.map(literal));
  const last=String.fromCharCode(64+table.headers.length);
  sheet.getRange('A4:'+last+(data.length+3)).values=data;
  const body=sheet.getRange('A4:'+last+(data.length+3));
  body.format.font={name:'Arial',size:11,color:'#222222'};
  body.format.wrapText=true;
  body.format.verticalAlignment='top';
  sheet.getRange('A4:'+last+'4').format.font.bold=true;
  sheet.getRange('A4:'+last+'4').format.rowHeight=34;
  sheet.getRange('A4:'+last+'4').format.borders={bottom:{style:'thin',color:'#777777'}};
  for(let col=0;col<table.headers.length;col++) {
    sheet.getRangeByIndexes(3,col,data.length,1).format.columnWidth=widths[name][col];
  }
  for(let index=0;index<table.rows.length;index++) {
    const lines=Math.max(...table.rows[index].map((value,col)=>lineCount(value,widths[name][col])));
    sheet.getRangeByIndexes(index+4,0,1,table.headers.length).format.rowHeight=Math.max(44,lines*15+10);
  }
  sheet.freezePanes.freezeRows(4);
  sheet.freezePanes.freezeColumns(3);
}
workbook.recalculate();
assert.equal(workbook.worksheets.getItem('Preguntas').getRange('C5').values[0][0],payload.tables.Preguntas.rows[0][2]);
assert.equal(workbook.worksheets.getItem('Detalle').getRange('C5').values[0][0],payload.tables.Detalle.rows[0][2]);
await fs.mkdir(previewDir,{recursive:true});
for(const [sheetName,range] of [['Preguntas','A4:G8'],['Detalle','A4:H11']]) {
  const image=await workbook.render({sheetName,range,scale:1,format:'png'});
  await fs.writeFile(path.join(previewDir,sheetName+'.png'),new Uint8Array(await image.arrayBuffer()));
}
console.log((await workbook.inspect({kind:'sheet',include:'id,name',maxChars:1000})).ndjson);
await (await SpreadsheetFile.exportXlsx(workbook)).save(output);
