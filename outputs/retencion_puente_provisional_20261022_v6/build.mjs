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
 if(item.name.startsWith('29_')){s.getRange('A12:A20').format.font.bold=true;s.getRange('B12:H20').merge(true);s.getRange('A1:H1').merge();s.getRange('A2:H2').merge();s.getRange('A3:H3').merge();s.getRange('D5:D10').setNumberFormat('0.00%');s.getRange('G5:G10').setNumberFormat('0.00%');s.getRange('H5:H10').setNumberFormat('0.00');}
 if(item.name.startsWith('34_')){s.getRange('D:E').format.columnWidth=42;s.getRange('K:L').format.columnWidth=65;s.getUsedRange().format.rowHeight=62;}
 if(item.name.startsWith('35_')){s.getRange('F:F').format.columnWidth=100;s.getUsedRange().format.rowHeight=70;}
 if(item.name.startsWith('36_')){s.getRange('F5:F12').setNumberFormat('0.00%');s.getRange('A1:H1').merge();s.getRange('A2:H2').merge();s.getRange('A3:H3').merge();s.getRange('B14:H24').merge(true);s.getRange('H:H').format.columnWidth=70;s.getUsedRange().format.rowHeight=50;}
 if(item.name.startsWith('37_')){s.getRange('B:B').format.columnWidth=100;s.getRange('F:I').format.columnWidth=45;s.getUsedRange().format.rowHeight=70;}
 if(item.name.startsWith('38_')){s.getRange('A1:E1').merge();s.getRange('A2:E2').merge();s.getRange('A3:E3').merge();s.getRange('B19:E26').merge(true);s.getRange('D5:D17').setNumberFormat('0.00%');s.getRange('E:E').format.columnWidth=95;s.getUsedRange().format.rowHeight=55;}
 if(item.name.startsWith('39_')){s.getRange('D:E').format.columnWidth=44;s.getUsedRange().format.rowHeight=55;}
 if(item.name.startsWith('31_')){for(const col of ['E','H','J'])s.getRange(`${col}5:${col}${n}`).setNumberFormat('0.00%');s.getRange(`K5:K${n}`).setNumberFormat('0.0000');}
 if(item.name.startsWith('32_')){s.getRange('B:B').format.columnWidth=110;s.getUsedRange().format.rowHeight=60;}
 if(item.name.startsWith('33_')){s.getRange('B:C').format.columnWidth=65;s.getUsedRange().format.rowHeight=62;}
 for(const [cell,formula] of Object.entries(item.formulas??{}))s.getRange(cell).formulas=[[formula]];
}
wb.recalculate();
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:5},summary:'errores'})).ndjson);
const out=await SpreadsheetFile.exportXlsx(wb);await out.save(dir+'suplemento.xlsx');
const img=await wb.render({sheetName:'29_Actualizacion_Provisional',range:'A1:H20',scale:1,format:'png'});await fs.writeFile(dir+'preview.png',new Uint8Array(await img.arrayBuffer()));
