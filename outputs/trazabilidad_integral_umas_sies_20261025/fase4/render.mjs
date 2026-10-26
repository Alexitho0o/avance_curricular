import fs from 'node:fs/promises';
import {SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const p='/Users/alexi/.local/share/ipss/trazabilidad_integral_fase4_20261025';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(p+'/preview.xlsx'));
for(const [sheet,range,file] of [['57_Trazabilidad_Actual','A1:I29','resumen.png'],['27_Guia_Hojas','A1:G10','guia.png'],['56_Vista_T1_T2_T3','M1:T10','vista.png']])await fs.writeFile(p+'/'+file,new Uint8Array(await(await wb.render({sheetName:sheet,range,scale:1.4})).arrayBuffer()));
console.log('Vistas de celdas guardadas renderizadas; no recálculo integral.');
