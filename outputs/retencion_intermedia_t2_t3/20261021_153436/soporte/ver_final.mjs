import fs from'node:fs/promises';import{FileBlob,SpreadsheetFile}from'@oai/artifact-tool';
const R='/Users/alexi/Documents/GitHub/avance_curricular',O=R+'/outputs/retencion_intermedia_t2_t3/20261021_153436',P=R+'/.local_restricted/retencion_intermedia/20261021_153436';
const q=JSON.parse(await fs.readFile(O+'/QA_FINAL.json','utf8')),w=await SpreadsheetFile.importXlsx(await FileBlob.load(q.public.path));
for(const[name,sheet,range]of[['final_ejecutiva','14_Vistas_Ejecutivas','B3:V31'],['final_trayectoria','5_Evolucion','B43:G70'],['final_portada','Portada','A1:F23']]){const blob=await w.render({sheetName:sheet,range,scale:1,format:'png'});await fs.writeFile(`${P}/previews/${name}.png`,new Uint8Array(await blob.arrayBuffer()));}
console.log('Final package rendered without saving changes.');
