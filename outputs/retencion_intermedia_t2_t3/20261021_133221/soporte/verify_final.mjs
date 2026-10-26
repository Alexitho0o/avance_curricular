import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const t='/tmp/retencion_revision_20261021';
const c=JSON.parse(await fs.readFile(`${t}/config.json`,'utf8'));
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(c.output));
for(const [sheet,cells] of Object.entries(c.expected))for(const [address,value] of Object.entries(cells)){
 const got=w.worksheets.getItem(sheet).getRange(address).values[0][0];
 if(typeof value==='number'?Math.abs(got-value)>1e-11:got!==value)throw Error(`${sheet}!${address}: ${got} != ${value}`);
}
for(const [name,sheetName,range] of [['final_resumen','Resumen','A1:I15'],['final_cierres','Revision_agregada','A1:I13'],['final_seguimiento','Revision_agregada','A29:I44']]){
 const image=await w.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(`${t}/${name}.png`,new Uint8Array(await image.arrayBuffer()));
}
console.log('Final import: all expected values pass; rendered without rewriting file.');
