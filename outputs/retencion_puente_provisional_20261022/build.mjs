import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const dir=new URL('.',import.meta.url).pathname;
const data=JSON.parse(await fs.readFile(dir+'payload.json','utf8'));
const wb=Workbook.create();
for(const item of data){
 const s=wb.worksheets.add(item.name), n=item.rows.length, m=Math.max(...item.rows.map(r=>r.length));
 const rows=item.rows.map(r=>[...r,...Array(m-r.length).fill(null)]);
 s.getRangeByIndexes(0,0,n,m).values=rows;
 s.showGridLines=false;s.freezePanes.freezeRows(4);
 s.getRangeByIndexes(0,0,n,m).format.columnWidth=22;
 s.getRangeByIndexes(0,0,n,m).format.rowHeight=32;
 s.getRangeByIndexes(0,0,n,m).format.wrapText=true;
 s.getRangeByIndexes(0,0,n,m).format.font.name='Arial';
 s.getRangeByIndexes(0,0,1,m).format.fill='#17365D';s.getRangeByIndexes(0,0,1,m).format.font.color='#FFFFFF';s.getRangeByIndexes(0,0,1,m).format.font.bold=true;
 s.getRangeByIndexes(3,0,1,m).format.fill='#DCE6F1';s.getRangeByIndexes(3,0,1,m).format.font.bold=true;
 s.getRange('A:A').format.columnWidth=44;
 if(item.name.startsWith('29_')){s.getRange('A10:A16').format.font.bold=true;s.getRange('B10:H16').merge(true);s.getRange('A1:H1').merge();s.getRange('A2:H2').merge();s.getRange('A3:H3').merge();s.getRange('D5:D8').setNumberFormat('0.00%');s.getRange('G5:G8').setNumberFormat('0.00%');s.getRange('H5:H8').setNumberFormat('0.00');}
 if(item.name.startsWith('31_')){for(const col of ['E','H','J'])s.getRange(`${col}5:${col}${n}`).setNumberFormat('0.00%');s.getRange(`K5:K${n}`).setNumberFormat('0.0000');}
 for(const [cell,formula] of Object.entries(item.formulas??{}))s.getRange(cell).formulas=[[formula]];
}
wb.recalculate();
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:5},summary:'errores'})).ndjson);
const out=await SpreadsheetFile.exportXlsx(wb);await out.save(dir+'suplemento.xlsx');
const img=await wb.render({sheetName:'29_Actualizacion_Provisional',range:'A1:H16',scale:1,format:'png'});await fs.writeFile(dir+'preview.png',new Uint8Array(await img.arrayBuffer()));
