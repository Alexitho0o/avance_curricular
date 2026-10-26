import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const d=new URL('.',import.meta.url).pathname;
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(d+'RETENCION_IPSS_PROVISIONAL_PUENTE_20261022.xlsx'));
for(const [sheet,range,file] of [['29_Actualizacion_Provisional','A1:H16','final_resumen.png'],['5_Evolucion','B5:H12','final_historico.png']]){
 const b=await w.render({sheetName:sheet,range,scale:1,format:'png'});await fs.writeFile(d+file,new Uint8Array(await b.arrayBuffer()));
}
