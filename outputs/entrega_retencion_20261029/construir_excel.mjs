// Autoría H003 con Artifact Tool; datos preparados y verificados por Python.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';
const out=path.dirname(fileURLToPath(import.meta.url));
const model=JSON.parse(await fs.readFile(path.join(out,'MODELO_AGREGADO.json'),'utf8'));
const wb=Workbook.create();
const colors=model.palette.principal;
const col=n=>String.fromCharCode(65+n);
const formats={count:'[>=1000000]#"."000"."000;[>=1000]#"."000;0',year:'0',pct:'0.0%',pp:'+0.00;-0.00;0.00'};
const layout=[];
for(const spec of model.sheets){
  const sh=wb.worksheets.add(spec.name); sh.showGridLines=false; sh.tabColor=colors.azul_institucional;
  const last=Math.max(...spec.blocks.map(b=>b.row+b.rows.length),...spec.notes.map(n=>n.row+1))+1;
  const end=col(spec.widths.length-1);
  const all=sh.getRange(`A1:${end}${last}`);
  all.format.font={name:model.font,size:11,color:'#3A3A3A'};
  all.format.verticalAlignment='center';all.format.rowHeight=23;
  for(let j=0;j<spec.widths.length;j++)sh.getRange(`${col(j)}1:${col(j)}${last}`).format.columnWidth=spec.widths[j];
  sh.mergeCells(`A2:${end}2`);sh.getRange('A2').values=[[spec.title]];
  sh.getRange(`A2:${end}2`).format.font={name:model.font,size:16,bold:true,color:colors.azul_institucional};
  sh.getRange(`A2:${end}2`).format.rowHeight=32;
  for(const note of spec.notes){
    sh.mergeCells(`A${note.row}:${end}${note.row+1}`);
    const rg=sh.getRange(`A${note.row}:${end}${note.row+1}`);rg.values=[[note.text]];rg.format.wrapText=true;
    rg.format.font={name:model.font,size:11,color:colors.azul_institucional};
    if(note.text.startsWith('BORRADOR')){rg.format.fill='#FFF2CC';rg.format.font.bold=true;}
  }
  for(let k=0;k<spec.blocks.length;k++){
    const b=spec.blocks[k], be=col(b.headers.length-1), bottom=b.row+b.rows.length;
    sh.mergeCells(`A${b.row-1}:${be}${b.row-1}`);
    const title=sh.getRange(`A${b.row-1}:${be}${b.row-1}`); title.values=[[b.title]];
    title.format.fill=colors.azul_institucional;title.format.font={name:model.font,size:12,bold:true,color:'#FFFFFF'};title.format.rowHeight=29;
    const range=`A${b.row}:${be}${bottom}`;
    sh.getRange(range).values=[b.headers,...b.rows];
    const table=sh.tables.add(range,true,`H003_${spec.name[0]}_${k}`);
    table.showFilterButton=true;table.showBandedColumns=false;
    sh.getRange(range).format.wrapText=true;
    const head=sh.getRange(`A${b.row}:${be}${b.row}`);
    head.format.fill=colors.azul_oscuro;head.format.font={name:model.font,bold:true,size:11,color:'#FFFFFF'};
    head.format.horizontalAlignment='center';head.format.rowHeight=45;
    for(let i=0;i<b.rows.length;i++){
      const row=sh.getRange(`A${b.row+1+i}:${be}${b.row+1+i}`);
      if(i%2===0)row.format.fill='#F2F2F2';
      const lines=Math.max(...b.rows[i].map((v,j)=>Math.ceil(String(v??'').length/Math.max(10,spec.widths[j]*0.85))));
      row.format.rowHeight=Math.max(27,lines*15+10);
      for(let j=0;j<b.rows[i].length;j++)if(typeof b.rows[i][j]==='number')sh.getCell(b.row+i,j).format.horizontalAlignment='right';
    }
    for(const [c,fmt] of Object.entries(b.formats))sh.getRange(`${c}${b.row+1}:${c}${bottom}`).setNumberFormat(formats[fmt]);
    for(let i=0;i<b.rows.length;i++)for(let j=0;j<b.rows[i].length;j++)if(typeof b.rows[i][j]==='number' && b.rows[i][j]<0)sh.getCell(b.row+i,j).setNumberFormat('0;-0;0');
    for(const [a,f]of Object.entries(b.formulas))sh.getRange(a).formulas=[[f]];
  }
  sh.freezePanes.freezeRows(spec.freeze);
  layout.push({name:spec.name,lastRow:last,lastCol:end,blocks:spec.blocks.map(b=>({row:b.row,bottom:b.row+b.rows.length}))});
}
wb.recalculate();
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'H003 errores de fórmula'});
await fs.writeFile(path.join(out,'QA_ARTIFACT.ndjson'),errors.ndjson);
const inspect=await wb.inspect({kind:'table',range:'1_Retencion_1er_anio!A6:H10',include:'values,formulas',tableMaxRows:5,tableMaxCols:8,maxChars:3000});
await fs.writeFile(path.join(out,'INSPECCION_FORMULAS.ndjson'),inspect.ndjson);
await fs.mkdir(path.join(out,'renders_artifact'),{recursive:true});
for(const s of layout){
  const blob=await wb.render({sheetName:s.name,range:`A1:${s.lastCol}${Math.min(18,s.lastRow)}`,scale:1,format:'png'});
  await fs.writeFile(path.join(out,'renders_artifact',s.name+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
const x=await SpreadsheetFile.exportXlsx(wb);await x.save(path.join(out,model.book));
await fs.writeFile(path.join(out,'DISENO.json'),JSON.stringify(layout,null,2)+'\n');
console.log('Exportado: '+model.book);
