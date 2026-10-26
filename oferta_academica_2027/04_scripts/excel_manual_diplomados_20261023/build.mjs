import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../..');
const data = JSON.parse(await fs.readFile(path.join(here, 'input.json'), 'utf8'));
const outputDir = path.join(root, '10_entrega/completado_manual_diplomados_20261023');
const gov = path.join(root, '11_gobernanza/completado_manual_diplomados_20261023');
await fs.mkdir(outputDir, {recursive:true});
await fs.mkdir(gov, {recursive:true});
const name = 'OFERTA_2027_ETAPA1_PARA_COMPLETAR_DIPLOMADOS_20261023.xlsx';
const outputPath = path.join(outputDir, name);
const desktop = path.join('/Users/alexi/Desktop', name);
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
let previousManifest;
try { previousManifest = JSON.parse(await fs.readFile(path.join(gov,'MANIFIESTO.json'),'utf8')); } catch (e) { if (e.code !== 'ENOENT') throw e; }
for (const p of [outputPath, desktop]) {
  try {
    const existing = await fs.readFile(p);
    const authorized = previousManifest?.salidas.find(s=>s.ruta === p);
    if (!authorized || hash(existing) !== authorized.sha256) throw new Error(`Archivo existente modificado: ${p}`);
  }
  catch (e) { if (e.code !== 'ENOENT') throw e; }
}
const wb = Workbook.create();
const sheet = wb.worksheets.add('Etapa 1 con encabezados');
sheet.getRange('A1:AV162').values = [data.headers, ...data.rows];
sheet.showGridLines = false;
const all = sheet.getRange('A1:AV162');
all.format.font = {name:'Arial', size:10, color:'#222222'};
all.format.columnWidth = 23;
all.format.rowHeight = 30;
all.format.verticalAlignment = 'center';
sheet.getRange('A1:AV1').format = {fill:'#264653', font:{name:'Arial', size:10, bold:true, color:'#FFFFFF'}, wrapText:true, rowHeight:90, horizontalAlignment:'center'};
sheet.getRange('A2:AV162').setNumberFormat('@');
for (const col of ['B','D','I','O']) {
  sheet.getRange(`${col}1:${col}162`).format.columnWidth = col === 'D' ? 60 : 38;
  sheet.getRange(`${col}2:${col}162`).format.wrapText = true;
}
sheet.getRange('D2:D162').format.rowHeight = 46;
for (const col of ['AG','AH']) sheet.getRange(`${col}2:${col}162`).setNumberFormat('#,##0');
sheet.getRange('R2:R162').setNumberFormat('0');
const clp = '[>=1000000]"$"#"."000"."000;[>=1000]"$"#"."000;"$"0';
sheet.getRange('AR2:AU162').setNumberFormat(clp);
sheet.getRange('AT1:AT162').format.columnWidth = 31;
sheet.getRange('AV2:AV162').format.horizontalAlignment = 'center';
const table = sheet.tables.add('A1:AV162', true, 'OfertaEtapa1');
table.style = 'TableStyleLight1';
sheet.freezePanes.freezeRows(1);
sheet.freezePanes.freezeColumns(4);
for (const row of data.diploma_rows) {
  sheet.getRange(`A${row}:D${row}`).format.fill = '#E7EFF2';
  for (const field of data.blank_fields) {
    const col = data.headers.indexOf(field);
    const cell = sheet.getRangeByIndexes(row-1, col, 1, 1);
    cell.format.fill = '#FFF2CC';
    cell.setNumberFormat(field === 'VIGENCIA_CARRERA' ? '0' : field.startsWith('VACANTES') ? '#,##0' : clp);
    if (field === 'VIGENCIA_CARRERA') cell.dataValidation = {rule:{type:'list', values:['1','2','3']}};
  }
}
wb.recalculate();
console.log((await wb.inspect({kind:'region',sheetId:sheet.name,range:'AR46:AV46',maxChars:600,tableMaxRows:1,tableMaxCols:5})).ndjson);
for (const [label, range] of [['encabezados','AQ1:AV4'], ['diplomado','AQ44:AV48']]) {
  const preview = await wb.render({sheetName:sheet.name,range,scale:1.3,format:'png'});
  await fs.writeFile(path.join(here,`${label}.png`), new Uint8Array(await preview.arrayBuffer()));
}
const file = await SpreadsheetFile.exportXlsx(wb);
await file.save(outputPath);
await fs.copyFile(outputPath, desktop);
const payload = await fs.readFile(outputPath);
if (hash(payload) !== hash(await fs.readFile(desktop))) throw new Error('Copias diferentes');
if (data.source_sha256 !== hash(await fs.readFile(data.source))) throw new Error('Fuente modificada');
const manifest = {fecha:'2026-10-23',estado:'PLANTILLA_MANUAL_NO_CARGAR_XLSX_EN_PES',fuente:{ruta:data.source,sha256:data.source_sha256},filas:161,columnas:48,diplomados:21,campos_en_blanco:data.blank_fields,celdas_para_completar:147,nombres_y_codigos_preservados:true,otros_programas:140,decision:'La instruccion mas reciente pide completar manualmente: no se prellenan 15/15 ni se incorporan montos por coincidencias de nombres.',scripts:await Promise.all(['preparar.py','build.mjs'].map(async n=>({ruta:path.join(here,n),sha256:hash(await fs.readFile(path.join(here,n)))}))),salidas:[outputPath,desktop].map(p=>({ruta:p,sha256:hash(payload),bytes:payload.length})),reanudacion:'Recibir Excel completado; verificar cambios por clave contra V04; validar e integrar; exportar CSV UTF-8 delimitado por punto y coma, sin encabezado ni salto final. No cambiar vigencias sin decision del usuario.',git:'Respaldo local, sin commit ni push'};
await fs.writeFile(path.join(gov,'MANIFIESTO.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({outputPath,desktop,bytes:payload.length,blankCells:147}));
