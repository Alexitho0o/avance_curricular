import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const dir='/tmp/ipss_validacion_2165_20261023/';
const data=JSON.parse(await fs.readFile(dir+'payload.json','utf8'));
const wb=Workbook.create();
for(const full of data){
 const item=full.rows.length>500?{...full,rows:full.rows.slice(0,1)}:full;
 const s=wb.worksheets.add(item.name),m=item.headers.length,n=item.rows.length+1;
 s.getRangeByIndexes(0,0,n,m).values=[item.headers,...item.rows];
 s.showGridLines=false;s.freezePanes.freezeRows(1);
 s.getRangeByIndexes(0,0,n,m).format.font.name='Arial';
 s.getRangeByIndexes(0,0,n,m).format.columnWidth=22;
 s.getRangeByIndexes(0,0,1,m).format.fill='#17365D';
 s.getRangeByIndexes(0,0,1,m).format.font.color='#FFFFFF';
 s.getRangeByIndexes(0,0,1,m).format.font.bold=true;
 s.getRangeByIndexes(0,0,1,m).format.wrapText=true;
 s.getRangeByIndexes(0,0,1,m).format.rowHeight=45;
 for(const c of item.textcols??[])s.getRangeByIndexes(1,c,Math.max(1,n-1),1).setNumberFormat('@');
 for(const c of item.datecols??[])s.getRangeByIndexes(1,c,Math.max(1,n-1),1).setNumberFormat('dd/mm/yyyy hh:mm');
 if(item.name==='RESUMEN'){s.getRange('D:D').format.columnWidth=90;s.getRange('A:A').format.columnWidth=48;s.getRange('B:B').format.columnWidth=44;s.getRange('H:H').format.columnWidth=100;s.getUsedRange().format.wrapText=true;s.getUsedRange().format.rowHeight=65;}
 if(item.name==='LEEME'){s.getRange('B:B').format.columnWidth=120;s.getUsedRange().format.wrapText=true;s.getUsedRange().format.rowHeight=60;}
}
wb.recalculate();
await (await SpreadsheetFile.exportXlsx(wb)).save(dir+'REVISION_PRIVADA_VALIDACION_IPSS_20261023_V6.xlsx');
// Solo vista agregada, nunca renderizar identidades.
const img=await wb.render({sheetName:'RESUMEN',range:'A1:D8',scale:1,format:'png'});
await fs.writeFile(dir+'resumen.png',new Uint8Array(await img.arrayBuffer()));
console.log('Libro privado exportado; sin volcado de datos.');
