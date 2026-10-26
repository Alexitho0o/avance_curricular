/** C: edición localizada y recálculo; el ensamblador conserva el OOXML original. */
import fs from 'node:fs/promises';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';
const directory = process.argv[2];
if (!directory) throw new Error('Falta carpeta de salida');
const m = JSON.parse(await fs.readFile(`${directory}/EDICION.json`, 'utf8'));
const dynamicQa = process.argv[3] === '--qa';
const input = dynamicQa ? `${directory}/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261023_V14.xlsx` : m.source;
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(input));
if (dynamicQa) {
  const cell = wb.worksheets.getItem('53_Codigos_T1_Confirmados').getRange('G54');
  const before = cell.values[0][0];
  if (before !== 3) throw new Error('Entrada QA distinta de la esperada');
  const checks = [];
  for (const [value,total,status] of [[4,612,'FALLIDO'],[3,611,'OK']]) {
    cell.values = [[value]]; wb.recalculate();
    for (const [sheet,address,expected] of [
      ['26_Avance_Curricular_Resumen','E1852',total],
      ['18_Foto_Intertrimestral','E8',total],
      ['52_Codigos_SIES_Revision','E8',total],
      ['52_Codigos_SIES_Revision','F8',1150],
      ['52_Codigos_SIES_Revision','G8',total/1150],
      ['28_QA_Matematica','F11',status],
      ['28_QA_Matematica','F12',status],
    ]) {
      const actual = wb.worksheets.getItem(sheet).getRange(address).values[0][0];
      if (typeof expected==='number' ? Math.abs(actual-expected)>1e-12 : actual!==expected) throw new Error(`QA dinámica: ${sheet}!${address}`);
      checks.push({entrada:value,hoja:sheet,celda:address,esperado:expected,observado:actual});
    }
  }
  await fs.writeFile(`${directory}/QA_DINAMICA.json`,JSON.stringify({estado:'OK',solo_memoria:true,archivo_final_no_modificado:true,controles:checks},null,2));
  console.log('14 controles dinámicos correctos; modificación y restauración solo en memoria.');
  process.exit(0);
}
await fs.mkdir(m.scratch, {recursive:true});
const before = await wb.render({sheetName:'52_Codigos_SIES_Revision', range:'A1:I14', scale:1, format:'png'});
await fs.writeFile(`${m.scratch}/antes.png`, new Uint8Array(await before.arrayBuffer()));
for (const e of m.edits) {
  const range = wb.worksheets.getItem(e.sheet).getRange(e.cell);
  if (e.formula !== undefined) range.formulas = [[e.formula]];
  else range.values = [[e.value]];
}
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'52_Codigos_SIES_Revision!A8:I8',include:'values,formulas',tableMaxRows:1,tableMaxCols:9,maxChars:2500})).ndjson);
for (const [sheetName,range,file] of [
  ['52_Codigos_SIES_Revision','A1:I14','resumen'],
  ['26_Avance_Curricular_Resumen','A1848:H1853','calculo'],
  ['18_Foto_Intertrimestral','A5:I12','foto'],
  ['53_Codigos_T1_Confirmados','A52:J59','desglose'],
  ['28_QA_Matematica','A10:H12','qa'],
]) {
  const image = await wb.render({sheetName,range,scale:1.2,format:'png'});
  await fs.writeFile(`${directory}/preview_${file}.png`,new Uint8Array(await image.arrayBuffer()));
}
const exported = await SpreadsheetFile.exportXlsx(wb);
await exported.save(`${m.scratch}/artifact_recalculado.xlsx`);
console.log('Edición y recálculo terminados; pendiente ensamblaje conservador y QA independiente.');
