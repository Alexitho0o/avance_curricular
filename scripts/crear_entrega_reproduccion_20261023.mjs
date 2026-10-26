import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const dir=process.argv[2];
const manifest=JSON.parse(await fs.readFile(dir+'/MANIFEST.json','utf8'));
const payload=JSON.parse(await fs.readFile(dir+'/payload_agregado.json','utf8'));
if(!process.argv.includes('--private-only')){
const wb=Workbook.create();
for(const p of payload){
 const s=wb.worksheets.add(p.name),n=p.rows.length;
 s.getRangeByIndexes(0,0,n,5).values=p.rows.map(r=>[...r,...Array(5-r.length).fill(null)]);
 s.showGridLines=false;s.freezePanes.freezeRows(4);s.tabColor='#CFB47C';
 const u=s.getRangeByIndexes(0,0,n,5);u.format.font.name='Arial';u.format.font.size=11;u.format.font.color='#3A3A3A';u.format.wrapText=true;u.format.rowHeight=34;
 s.getRange('A:A').format.columnWidth=p.name.startsWith('51')?65:46;
 s.getRange('B:D').format.columnWidth=23;s.getRange('E:E').format.columnWidth=40;
 for(const r of p.merged)s.getRange(`A${r}:E${r}`).merge();
 for(const r of [1,4]){const z=s.getRange(`A${r}:E${r}`);z.format.fill='#102B42';z.format.font.color='#FFFFFF';z.format.font.bold=true;z.format.rowHeight=40;}
 s.getRange('A2:E3').format.fill='#F2F2F2';s.getRange('A2:E3').format.rowHeight=44;
 if(p.name.startsWith('51')){s.getRange(`A5:E${n}`).format.rowHeight=96;s.getRange('D:D').format.columnWidth=42;}
 else for(let r=5;r<=n;r++)if(r%2===0&&!p.merged.includes(r))s.getRange(`A${r}:E${r}`).format.fill='#F2F2F2';
 for(const [cell,formula] of Object.entries(p.formulas))s.getRange(cell).formulas=[[formula]];
 s.getRange(`B5:D${n}`).setNumberFormat('#,##0;[Red](#,##0);0');
 for(const r of p.percent){s.getRange(`B${r}:C${r}`).setNumberFormat('0.00%;[Red](0.00%);0.00%');s.getRange(`D${r}`).setNumberFormat('0.00" pp";[Red](0.00" pp");0.00" pp"');}
 if(p.name.startsWith('49')){s.getRange('A9:E10').format.fill='#CFB47C';s.getRange('A12:E12').format.fill='#0E4273';s.getRange('A12:E12').format.font.color='#FFFFFF';s.getRange('A19:E25').format.rowHeight=48;}
}
wb.recalculate();
await (await SpreadsheetFile.exportXlsx(wb)).save(dir+'/suplemento.xlsx');
await fs.writeFile(dir+'/preview_auditoria.png',new Uint8Array(await (await wb.render({sheetName:'49_Reproduccion_V10',range:'A1:E16',scale:1.4,format:'png'})).arrayBuffer()));
console.log('Suplemento agregado creado y recalculado');
}
if(process.argv.includes('--aggregate-only'))process.exit(0);
// The private file is deliberately outside the repositories. No personal values are logged.
const pd=JSON.parse(await fs.readFile(manifest.privado+'/payload_excel.json','utf8'));
const pw=Workbook.create(),note=pw.worksheets.add('Leer_primero'),s=pw.worksheets.add('Observaciones');
note.getRange('A1:B8').values=[['Revisión privada UMAS–SIES','24.774 observaciones; identificadores solo locales'],
 ['Grano','Persona × expediente/carrera × sede/jornada × plan × año/período observado.'],
 ['Lectura','Código documental atribuible y código interno vigente están separados de la propuesta. Ninguno acredita aceptación SIES.'],
 ['Fuentes y fechas','Columnas JSON conservan todas las filas de origen sin expandir las observaciones. Archivo, hoja, fila y claves originales están dentro de esas celdas.'],
 ['Pendientes','Fecha efectiva de asignación del plan no acreditada. No trasladar códigos entre años sin respaldo.'],
 ['Identidad','Originales en fuentes_promedios/contextos_DA/evidencias_matricula; persona normalizada y CODCLI como texto.'],
 ['Reproducción','OBSERVACIONES_PRIVADAS.json y .csv conservan el registro completo y los campos adicionales.'],
 ['Antes/después','Transiciones comparadas por clave contra V10, no inferidas por diferencia de totales.']];
note.getRange('A:A').format.columnWidth=30;note.getRange('B:B').format.columnWidth=105;note.getRange('A1:B8').format.wrapText=true;note.getRange('A1:B8').format.rowHeight=52;note.showGridLines=false;
s.getRangeByIndexes(0,0,1,pd.columns.length).values=[pd.columns];
for(let n=0;n<pd.rows.length;n+=1000)s.getRangeByIndexes(n+1,0,Math.min(1000,pd.rows.length-n),pd.columns.length).values=pd.rows.slice(n,n+1000);
s.getRange('A:AC').format.columnWidth=24;
s.getRange('S:S').format.columnWidth=65;s.showGridLines=false;s.freezePanes.freezeRows(1);
const hh=s.getRangeByIndexes(0,0,1,pd.columns.length);hh.format.fill='#102B42';hh.format.font.color='#FFFFFF';hh.format.font.bold=true;hh.format.wrapText=true;hh.format.rowHeight=56;
pw.recalculate();
await (await SpreadsheetFile.exportXlsx(pw)).save(manifest.privado+'/REVISION_PRIVADA_PUENTE_REPRODUCIDO_20261023.xlsx');
console.log('Excel privado creado: '+pd.rows.length+' observaciones');
