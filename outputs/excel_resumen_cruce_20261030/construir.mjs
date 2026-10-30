import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const out=path.dirname(fileURLToPath(import.meta.url));
const model=JSON.parse(await fs.readFile(path.join(out,'MODELO_AGREGADO.json'),'utf8'));
const wb=Workbook.create(),blue='#102B42',dark='#0E4273';
const col=n=>{let s='';while(n){let m=(n-1)%26;s=String.fromCharCode(65+m)+s;n=Math.floor((n-1)/26);}return s;};
for(const s of model.sheets)wb.worksheets.add(s.name);
const layout=[];
for(const s of model.sheets){
 const sh=wb.worksheets.getItem(s.name),last=Math.max(...s.blocks.map(b=>b.row+b.rows.length));
 sh.showGridLines=false;sh.tabColor=blue;
 const all=sh.getRange(`A1:${col(s.widths.length)}${last}`);all.format.font={name:model.font,size:11,color:'#3A3A3A'};all.format.verticalAlignment='center';all.format.rowHeight=25;
 s.widths.forEach((w,j)=>{sh.getRange(`${col(j+1)}1:${col(j+1)}${last}`).format.columnWidth=w;});
 const titleEnd=s.titleEnd||(s.name.startsWith('1_')?'H':s.name.startsWith('2_')?'E':'G');
 sh.mergeCells(`A2:${titleEnd}2`);sh.getRange('A2').values=[[s.title]];sh.getRange(`A2:${titleEnd}2`).format.font={name:model.font,size:16,bold:true,color:blue};sh.getRange(`A2:${titleEnd}2`).format.rowHeight=32;
 for(const [r,t]of s.notes){sh.mergeCells(`A${r}:${titleEnd}${r}`);const rg=sh.getRange(`A${r}:${titleEnd}${r}`);rg.values=[[t]];rg.format.font={name:model.font,size:11,color:blue};rg.format.wrapText=true;rg.format.rowHeight=s.noteHeights?.[r]??44;}
 const heights=new Map();
 for(const b of s.blocks){
  const start=col(b.column+1),end=col(b.column+b.headers.length),bottom=b.row+b.rows.length;
  const rr=`${start}${b.row}:${end}${bottom}`;
  sh.getRange(rr).values=[b.headers,...b.rows];
  const tab=sh.tables.add(rr,true,'H005_'+b.id);tab.showFilterButton=true;tab.showBandedColumns=false;
  sh.getRange(rr).format.wrapText=true;
  const hr=sh.getRange(`${start}${b.row}:${end}${b.row}`);hr.format.fill=dark;hr.format.font={name:model.font,size:11,bold:true,color:'#FFFFFF'};hr.format.horizontalAlignment='center';hr.format.rowHeight=48;
  for(let i=0;i<b.rows.length;i++){
   const row=sh.getRange(`${start}${b.row+i+1}:${end}${b.row+i+1}`);
   if(i%2===0)row.format.fill='#F2F2F2';
   const lines=Math.max(...b.rows[i].map((v,j)=>Math.ceil(String(v??'').length/Math.max(8,s.widths[j+b.column]*0.9))));
   const rh=Math.max(27,Math.min(150,lines*14+8));heights.set(b.row+i+1,Math.max(heights.get(b.row+i+1)||0,rh));
  }
  for(const [j,fmt]of Object.entries(b.formats))sh.getRange(`${col(b.column+Number(j)+1)}${b.row+1}:${col(b.column+Number(j)+1)}${bottom}`).setNumberFormat(fmt);
  for(const [a,f]of Object.entries(b.formulas))sh.getRange(a).formulas=[[f]];
 }
 for(const n of s.customNotes||[]){sh.mergeCells(n.range);const rg=sh.getRange(n.range);rg.values=[[n.text]];rg.format.wrapText=true;rg.format.font={name:model.font,size:11,color:blue};rg.format.rowHeight=30;}
 for(const [r,h]of heights)sh.getRange(`A${r}:${col(s.widths.length)}${r}`).format.rowHeight=h;
 for(const spec of s.charts||(s.chart?[s.chart]:[])){const chart=sh.charts.add('bar',sh.getRange(spec.range));chart.title=spec.title||'Códigos SIES con matrícula por año';chart.hasLegend=!!spec.legend;if(spec.legend)chart.legend={position:'top',textStyle:{typeface:model.font,fontSize:11}};chart.setPosition(spec.from,spec.to);chart.series.items[0].fill=dark;if(chart.series.items[1])chart.series.items[1].fill='#CFB47C';chart.xAxis={axisType:'textAxis',textStyle:{typeface:model.font,fontSize:10}};chart.yAxis={numberFormatCode:'0',numberFormatSourceLinked:false,textStyle:{typeface:model.font,fontSize:10}};chart.titleTextStyle.typeface=model.font;chart.titleTextStyle.fontSize=14;}
 for(const selector of s.selectors||[]){sh.getRange(selector.labelCell).values=[[selector.label]];sh.getRange(selector.labelCell).format.fill=dark;sh.getRange(selector.labelCell).format.font.color='#FFFFFF';sh.getRange(selector.cell).values=[['Todas']];sh.getRange(selector.cell).dataValidation={rule:{type:'list',values:selector.values}};sh.getRange(selector.cell).format.fill='#FFF2CC';sh.getRange(selector.cell).format.font={name:model.font,size:11,bold:true,color:'#0000FF'};sh.getRange(selector.cell).format.rowHeight=38;}
 for(const cf of s.conditional||[])sh.getRange(cf.range).conditionalFormats.addCustom(cf.formula,{fill:cf.fill});
 all.format.horizontalAlignment='center';all.format.verticalAlignment='center';all.format.wrapText=true;
 sh.freezePanes.freezeRows(s.freeze);sh.freezePanes.freezeColumns(1);
 layout.push({name:s.name,lastRow:last,lastCol:col(s.widths.length),ranges:s.renders});
}
wb.recalculate();
await fs.writeFile(path.join(out,'QA_ARTIFACT.ndjson'),(await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:40},summary:'H005 errores de fórmula'})).ndjson);
await fs.writeFile(path.join(out,'INSPECCION.ndjson'),(await wb.inspect({kind:'table',range:'5_Cruce_SIES_UMAS!A5:G11',include:'values,formulas',tableMaxRows:7,tableMaxCols:7,maxChars:3500})).ndjson);
await fs.mkdir(path.join(out,'renders'),{recursive:true});
for(const s of model.sheets){for(let i=0;i<s.renders.length;i++){const b=await wb.render({sheetName:s.name,range:s.renders[i],scale:1,format:'png'});await fs.writeFile(path.join(out,'renders',s.name+(i?'_'+(i+1):'')+'.png'),new Uint8Array(await b.arrayBuffer()));}}
const file=await SpreadsheetFile.exportXlsx(wb);await file.save(path.join(out,model.book));
await fs.writeFile(path.join(out,'DISENO.json'),JSON.stringify(layout,null,2)+'\n');
console.log('Libro exportado: '+model.book);
