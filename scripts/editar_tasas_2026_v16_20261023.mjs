/** C: autoría Artifact Tool de tres tasas y sus bases; sin modificar fuentes. */
import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const dir=process.argv[2],mode=process.argv[3]||'edit';
const m=JSON.parse(await fs.readFile(`${dir}/EDICION.json`,'utf8'));
const source=mode==='qa'?`${dir}/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261023_V16.xlsx`:m.source;
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(source));
const sn='18_Foto_Intertrimestral',s=wb.worksheets.getItem(sn);
await fs.mkdir(m.scratch,{recursive:true});
if(mode==='before'){
  const img=await wb.render({sheetName:sn,range:'B6:I14',scale:1.5});
  await fs.writeFile(`${m.scratch}/antes.png`,new Uint8Array(await img.arrayBuffer()));
  console.log('Vista previa de la referencia lista.');process.exit(0);
}
const checks=[];
function check(cell,want){
  const got=s.getRange(cell).values[0][0];
  if(typeof want==='number'?Math.abs(got-want)>1e-12:got!==want)throw Error(`${cell}: ${got} != ${want}`);
  checks.push({celda:cell,esperado:want,observado:got});
}
if(mode==='qa'){
  for(const [cell,value,target,want] of [['G11',1359,'H11',1359/1467],['G11',1360,'H11',1360/1467],['E12',461,'F12',461/528],['E12',462,'F12',462/528],['E95',5,'H14',2290/2518],['E95',2523,'H14','—'],['E95',4,'H14',2290/2519]]){
    s.getRange(cell).values=[[value]];wb.recalculate();check(target,want);
    for(const [c,x] of [['D11',1471],['D12',527],['D14',2523],['D8',1150],['G8',1023],['E8',611]])check(c,x);
  }
  const other=wb.worksheets.getItem('53_Codigos_T1_Confirmados'),old=other.getRange('H127').values[0][0];
  other.getRange('H127').values=[[old+1]];wb.recalculate();check('F93',1468);check('H11',1360/1468);
  other.getRange('H127').values=[[old]];wb.recalculate();check('F93',1467);check('H11',1360/1467);
  await fs.writeFile(`${dir}/QA_DINAMICA.json`,JSON.stringify({estado:'OK',solo_memoria:true,controles:checks},null,2));
  const img=await wb.render({sheetName:sn,range:'B91:I97',scale:1.5});
  await fs.writeFile(`${dir}/preview_bases_v16.png`,new Uint8Array(await img.arrayBuffer()));
  console.log(`${checks.length} controles dinámicos OK. Archivo final intacto.`);process.exit(0);
}
for(const e of m.edits){
  const c=s.getRange(e.cell);
  if(e.style_from)c.copyFrom(s.getRange(e.style_from),'all');
  if(e.formula!==undefined)c.formulas=[[e.formula]];else c.values=[[e.value]];
}
for(const merge of m.merges)s.mergeCells(merge);
for(const [row,height] of Object.entries(m.heights))s.getRange(`B${row}:I${row}`).format.rowHeight=height;
wb.recalculate();
for(const e of m.edits)check(e.cell,e.expected);
const audit=await wb.inspect({kind:'table',range:`${sn}!B91:I97`,include:'values,formulas',tableMaxRows:7,tableMaxCols:8,maxChars:8000});
await fs.writeFile(`${m.scratch}/inspeccion.txt`,audit.ndjson);
await (await SpreadsheetFile.exportXlsx(wb)).save(`${m.scratch}/artifact_recalculado.xlsx`);
console.log(`${checks.length} celdas verificadas y exportación de trabajo lista.`);
