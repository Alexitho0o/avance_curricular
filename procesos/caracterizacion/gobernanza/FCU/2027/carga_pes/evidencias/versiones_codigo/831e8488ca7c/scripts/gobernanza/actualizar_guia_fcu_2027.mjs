import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const [input, output, previewDir, mode = 'edit'] = process.argv.slice(2);
const data = JSON.parse(await fs.readFile(input, 'utf8'));
if (!['before','changes'].includes(mode) && data.visibility_normalizer && !process.env.FCU_PYTHON) {
  throw new Error('Set FCU_PYTHON to the loaded workspace Python executable');
}
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(data.source_workbook));
await fs.mkdir(previewDir, { recursive: true });
if (mode === 'before' || mode === 'changes') {
  workbook.recalculate();
  // Imported-formula previews use independently verified saved values; no XLSX is exported.
  for (const cell of data.preview_cells ?? []) {
    const range = workbook.worksheets.getItem(cell.sheet).getRange(cell.cell);
    range.clear({applyTo:'contents'});
    range.values = [[cell.value]];
  }
  if (mode === 'changes') {
    for (const [name, range] of [['Guía para editar','A123:C126'], ['Guía para editar','A263:C265'], ['Cruces','L138:N142']]) {
      const preview = await workbook.render({sheetName:name,range,scale:1,format:'png'});
      await fs.writeFile(path.join(previewDir, `${name}_${range.replace(':','_')}.png`),new Uint8Array(await preview.arrayBuffer()));
    }
    process.exit(0);
  }
  for (const name of ['Guía para editar', 'Cruces']) {
    const preview = await workbook.render({sheetName:name, range:name === 'Cruces' ? 'L1:N3' : 'A1:C3', scale:1, format:'png'});
    await fs.writeFile(path.join(previewDir, `${name}_before.png`), new Uint8Array(await preview.arrayBuffer()));
  }
  console.log((await workbook.inspect({kind:'sheet', include:'id,name', maxChars:1200})).ndjson);
  process.exit(0);
}
for (const patch of data.patches) {
  const range = workbook.worksheets.getItem(patch.sheet).getRange(patch.cell);
  if ('formula' in patch) range.formulas = [[patch.formula]];
  else range.values = [[patch.value]];
}
const cross = workbook.worksheets.getItem('Cruces');
const guide = workbook.worksheets.getItem('Guía para editar');
for (const [sheet, first, count] of [[cross, 17, 7], [guide, 9, 4]]) {
  const area = sheet.getRangeByIndexes(0, first, data.guide_row_count + 1, count);
  area.format.font = {name:'Arial', size:10, color:'#000000'};
  area.format.wrapText = true;
  area.format.verticalAlignment = 'top';
  sheet.getRangeByIndexes(0, first, 1, count).format.font.bold = true;
}
for (const [col, width] of [['R',28],['S',32],['T',24],['U',34],['V',90],['W',65],['X',30]]) {
  cross.getRange(`${col}1:${col}${data.guide_row_count+1}`).format.columnWidth = width;
}
for (const [col, width] of [['J',34],['K',28],['L',28],['M',25]]) {
  guide.getRange(`${col}1:${col}${data.guide_row_count+1}`).format.columnWidth = width;
}
for (let i=0; i<data.guide_row_count; i++) {
  const r=i+2;
  const textPatches=data.patches.filter(p=>p.sheet==='Cruces' && ['M','N'].some(c=>p.cell===`${c}${r}`));
  const longest=Math.max(...textPatches.map(p=>String(p.value??'').split('\n').reduce((n,line)=>n+Math.max(1,Math.ceil(line.length/75)),0)));
  guide.getRange(`A${r}:M${r}`).format.rowHeight = Math.max(76, (longest+5)*14);
}
const verificationRow = data.crosswalk.findIndex(r=>r.current.some(m=>m.question==='G07Q71' && m.subquestion==='SQ004'))+2;
const linkedCell = cross.getRange(`N${verificationRow}`);
const originalText = linkedCell.values[0][0];
linkedCell.values = [['PRUEBA DE REFERENCIA']];
workbook.recalculate();
if (!String(guide.getRange(`A${verificationRow}`).values[0][0]).includes('PRUEBA DE REFERENCIA')) {
  throw new Error('Guide formula did not update from the crosswalk');
}
linkedCell.values = [[originalText]];
workbook.recalculate();
const scan = await workbook.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},maxChars:2400});
console.log(scan.ndjson);
const row = data.crosswalk.findIndex(r=>r.current.some(m=>m.question==='G07Q71' && m.subquestion==='SQ004'))+2;
for (const [name, range] of [['Guía para editar', `A${row}:C${row+1}`], ['Cruces', `R${row}:V${row+1}`]]) {
  const preview = await workbook.render({sheetName:name, range, scale:1, format:'png'});
  await fs.writeFile(path.join(previewDir, `${name}_after.png`),new Uint8Array(await preview.arrayBuffer()));
}
await fs.mkdir(path.dirname(output), {recursive:true});
await (await SpreadsheetFile.exportXlsx(workbook)).save(output);
// Row visibility has no supported Artifact Tool setter. Normalize only this missing feature.
let visibility = null;
if (data.visibility_normalizer) {
  if (!process.env.FCU_PYTHON) throw new Error('Set FCU_PYTHON to the loaded workspace Python executable');
  visibility = JSON.parse(execFileSync(process.env.FCU_PYTHON,[data.visibility_normalizer,output],{encoding:'utf8'}));
}
const sha256=crypto.createHash('sha256').update(await fs.readFile(output)).digest('hex');
const manifest={date:'2026-10-07',output,sha256,source_workbook:data.source_workbook,
  visibility,
  source_sha256:data.source_sha256,sources:data.report.sources,
  status_counts:data.status_counts,origins:data.report.origins,
  mapping_scope:'15 disposition and 5 disability fields. Partial non-production PES mapping only.',
  schema_2027:'json/ESPECIFICACION_PES_2027.json: 172 fields. Separate draft-only adapter scripts/fcu_pes_2027.py.',
  settings_confirmed:data.report.checked_settings_ready,pes_ready:false,
  review_policy:data.report.review_policy,
  excluded_checks_count:data.report.excluded_checks?.length ?? 0,
  confirmed_by_user:data.report.checks.filter(c=>c.confirmed_by_user).map(c=>c.confirmation),
  review_scope:'Only active checks under the recorded policy produce editing recommendations. Excluded observations are not represented as corrected settings.',
  raw_sheets_preserved:data.raw_sheets_unchanged};
await fs.writeFile(output.replace(/\.xlsx$/,'.manifest.json'),JSON.stringify(manifest,null,2)+'\n');
await fs.writeFile(output+'.sha256',`${sha256}  ${path.basename(output)}\n`);
console.log(JSON.stringify({output,sha256,statuses:data.status_counts}));
