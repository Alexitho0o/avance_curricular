import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const dir='/Users/alexi/Documents/GitHub/avance_curricular/outputs/auditoria_diccionario_sies_20261025/fase3_20261025';
const p='/Users/alexi/.local/share/ipss/fase3_candidata_20261025';
const d=JSON.parse(await fs.readFile(dir+'/ENTRADAS_EXCEL.json','utf8'));
const wb=Workbook.create();
for(const name of [...Object.keys(d.hojas),'18_Foto_Intertrimestral']) wb.worksheets.add(name);
wb.worksheets.getItem('18_Foto_Intertrimestral').getRange('E8').values=[[611]];
for(const [name,rows] of Object.entries(d.hojas)) {
 const s=wb.worksheets.getItem(name);const n=rows.length,m=Math.max(...rows.map(r=>r.length));
 const col=i=>String.fromCharCode(65+i);
 s.getRange(`A1:${col(m-1)}${n}`).values=rows.map(r=>Array.from({length:m},(_,i)=>typeof r[i]==='string'&&r[i].startsWith('=')?null:r[i]??null));
 for(let r=0;r<n;r++)for(let c=0;c<rows[r].length;c++)if(typeof rows[r][c]==='string'&&rows[r][c].startsWith('='))s.getRange(`${col(c)}${r+1}`).formulas=[[rows[r][c]]];
 s.showGridLines=false;s.getRange(`A1:${col(m-1)}${n}`).format.font.name='Arial';s.getRange(`A1:${col(m-1)}${n}`).format.font.size=10;s.getRange(`A1:${col(m-1)}${n}`).format.wrapText=true;
 s.getRange(`A:${col(m-1)}`).format.columnWidth=20;
 s.getRange(`A1:${col(m-1)}3`).merge();s.getRange(`A1:${col(m-1)}3`).format.fill='#102B42';s.getRange(`A1:${col(m-1)}3`).format.font.color='#FFFFFF';s.getRange(`A1:${col(m-1)}3`).format.rowHeight=24;
 s.getRange(`A5:${col(m-1)}5`).format.fill='#174977';s.getRange(`A5:${col(m-1)}5`).format.font.color='#FFFFFF';s.getRange(`A5:${col(m-1)}5`).format.rowHeight=42;
}
const s=wb.worksheets.getItem('54_Contextos_y_Pendientes');
s.getRange('A6:O228').values=Array.from({length:223},(_,i)=>d.tabla54_candidata[i]??Array(15).fill(null));
s.getRange('A1').values=[['54 · Códigos del contexto — edición candidata v8\nB/C · Cinco atribuciones anuales recuperadas por puente documental explícito. No cambia el código de origen ni la tasa.']];
s.getRange('A6:O228').format.rowHeight=48;s.getRange('D:F').format.columnWidth=27;s.getRange('G:M').format.columnWidth=25;s.getRange('O:O').format.columnWidth=53;
const a=wb.worksheets.getItem('52_Codigos_SIES_Revision');
const totalDoc=d.conteos_contextos.B_C??d.conteos_contextos['B/C_DOCUMENTAL_ANUAL_ATRIBUIDO'];
const notes={A1:'52 · Seguimiento de T1 en T2 y T3 hasta 2026\nC · Edición candidata v8. Cinco códigos recuperados en estos contextos; tasas, bases y denominadores conservados.',A27:`B/C/D/E · Edición candidata: ${totalDoc} contextos con código documental anual, 13 con correspondencia interna aprobada y 99 pendientes. Cinco atribuciones recuperadas; no cambia la retención.`,A28:`B/C/D/E · Foco multiversión: ${d.multiversion['B/C_DOCUMENTAL_ANUAL_ATRIBUIDO']??0} documentales, ${d.multiversion['D_CORRESPONDENCIA_INTERNA_APROBADA']??0} internos aprobados y ${d.multiversion.E_PENDIENTE??0} pendientes. Misma definición de V17.`,A32:'C · Candidata v8: ocho recuperaciones históricas; cinco afectan a estas hojas y tres a T1. El diccionario activo sigue en v7 hasta su promoción. V17 original conservada.',A33:'Fuentes, diferencias y QA: MANIFEST_FASE3.json. B = observado; C = implementación; D = decisión interna; E = pendiente. No acredita aceptación SIES.'};
for(const [cell,value] of Object.entries(notes))a.getRange(cell).values=[[value]];
a.getRange('A16:I16').format.fill='#174977';a.getRange('A16:I16').format.font.color='#FFFFFF';a.getRange('A16:I16').format.rowHeight=44;
for(let r=26;r<=33;r++){a.getRange(`A${r}:I${r}`).merge();a.getRange(`A${r}:I${r}`).format.rowHeight=46;}
wb.recalculate();
await (await SpreadsheetFile.exportXlsx(wb)).save(p+'/donante.xlsx');
await fs.writeFile(dir+'/NOTAS_EXCEL.json',JSON.stringify(notes,null,2));
await fs.writeFile(p+'/preview52.png',new Uint8Array(await(await wb.render({sheetName:a.name,range:'A16:I33',scale:1.3})).arrayBuffer()));
await fs.writeFile(p+'/preview54.png',new Uint8Array(await(await wb.render({sheetName:s.name,range:'G1:O12',scale:1.2})).arrayBuffer()));
console.log((await wb.inspect({kind:'table',range:`'${a.name}'!F24:I24`,include:'values,formulas',tableMaxRows:1,tableMaxCols:4})).ndjson);
