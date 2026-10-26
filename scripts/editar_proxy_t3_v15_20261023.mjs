/** C: modifica únicamente el auxiliar T3 y notas autorizadas; exporta celdas para preservación. */
import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const dir=process.argv[2];
const m=JSON.parse(await fs.readFile(`${dir}/EDICION.json`,'utf8'));
const qa=process.argv[3]==='--qa';
const path=qa?`${dir}/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261023_V15.xlsx`:m.source;
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path));
await fs.mkdir(m.scratch,{recursive:true});
const s26=wb.worksheets.getItem('26_Avance_Curricular_Resumen');
if(qa){
  const checks=[];
  for(const [v,n] of [[12,547],[11,546]]){
    s26.getRange('E1860').values=[[v]];wb.recalculate();
    for(const [sn,c,x] of [['26_Avance_Curricular_Resumen','E1853',n],['26_Avance_Curricular_Resumen','F1853',n/1150],['26_Avance_Curricular_Resumen','C1853',1150],['18_Foto_Intertrimestral','G8',1023],['18_Foto_Intertrimestral','E8',611]]){
      const got=wb.worksheets.getItem(sn).getRange(c).values[0][0];
      if(Math.abs(got-x)>1e-12)throw Error(`QA ${sn}!${c}: ${got} / ${x}`);
      checks.push({entradaP:v,hoja:sn,celda:c,esperado:x,observado:got});
    }
  }
  await fs.writeFile(`${dir}/QA_DINAMICA.json`,JSON.stringify({estado:'OK',solo_memoria:true,controles:checks},null,2));
  console.log('10 controles dinámicos OK; archivo final intacto.');process.exit(0);
}
const before=await wb.render({sheetName:s26.name,range:'A1848:H1855',scale:1});
await fs.writeFile(`${m.scratch}/antes.png`,new Uint8Array(await before.arrayBuffer()));
for(const e of m.edits){
  const sheet=wb.worksheets.getItem(e.sheet),c=sheet.getRange(e.cell);
  if(e.style_from)c.copyFrom(sheet.getRange(e.style_from),'all');
  if(e.formula!==undefined)c.formulas=[[e.formula]];else c.values=[[e.value]];
}
wb.recalculate();
for(const e of m.edits){
  const v=wb.worksheets.getItem(e.sheet).getRange(e.cell).values[0][0];
  if(typeof e.expected==='number'?Math.abs(v-e.expected)>1e-12:v!==e.expected)throw Error(`Cálculo ${e.sheet}!${e.cell}: ${v}`);
}
for(const [sheetName,range,file] of [[s26.name,'A1848:H1861','calculo'],['52_Codigos_SIES_Revision','A1:I14','resumen']]){
  const image=await wb.render({sheetName,range,scale:1.2});await fs.writeFile(`${dir}/preview_${file}.png`,new Uint8Array(await image.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(`${m.scratch}/artifact_recalculado.xlsx`);
console.log('40 celdas y fórmulas verificadas; exportación de trabajo lista.');
