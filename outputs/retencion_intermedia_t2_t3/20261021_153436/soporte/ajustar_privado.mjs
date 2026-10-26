import fs from 'node:fs/promises';
import{FileBlob,SpreadsheetFile}from'@oai/artifact-tool';
const p='/Users/alexi/Documents/GitHub/avance_curricular/.local_restricted/retencion_intermedia/20261021_153436',file=`${p}/TRAYECTORIAS_PRIVADAS_IPSS_20261021_153436.xlsx`;
const d=JSON.parse(await fs.readFile(`${p}/datos.json`,'utf8')),w=await SpreadsheetFile.importXlsx(await FileBlob.load(file)),s=w.worksheets.getItem('Agregados');
for(let i=0;i<d.groups.length;i++)if(d.groups[i][0]===2025)s.getRange(`S${i+6}`).values=[['Sin campo']];
w.worksheets.getItem('Resumen').getRange('A5:H5').format.verticalAlignment='center';w.worksheets.getItem('Resumen').getRange('B6:F7').setNumberFormat('#,##0');w.recalculate();
await(await SpreadsheetFile.exportXlsx(w)).save(file);
console.log('Private missing-state presentation corrected; no denominator or identity edits.');
