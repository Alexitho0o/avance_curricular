import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const d=new URL('.',import.meta.url).pathname;
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(d+'RETENCION_IPSS_PROVISIONAL_PUENTE_20261022_V2.xlsx'));
for(const [sheet,range,file] of [['29_Actualizacion_Provisional','A1:H20','final_resumen.png'],['30_Puente_63_Dimensiones','A1:G7','final_dimensiones.png'],['32_Fuentes_y_Exclusiones','A1:B8','final_fuentes.png'],['33_Ejecucion_y_Pendientes','A1:C8','final_fases.png']]){
 const b=await w.render({sheetName:sheet,range,scale:1,format:'png'});await fs.writeFile(d+file,new Uint8Array(await b.arrayBuffer()));
}
