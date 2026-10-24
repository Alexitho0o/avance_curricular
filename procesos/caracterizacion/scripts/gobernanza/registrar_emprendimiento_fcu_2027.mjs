import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';

const [root, observationsPath, previewDir] = process.argv.slice(2);
if (!root || !observationsPath || !previewDir) throw new Error('Expected repository, observations workbook and preview directory');
const base = path.join(root, 'gobernanza/FCU/2027/preparacion');
const registryPath = path.join(base, 'json/PREGUNTAS_INSTITUCIONALES_2027.json');
const registry = JSON.parse(await fs.readFile(registryPath, 'utf8'));
if (registry.version !== 1) {
  throw new Error('Generador historico v1 retirado. El registro vigente identifica G02Q95/AO05; no regenerar instrucciones de pregunta independiente.');
}
const decision = registry.questions[0];
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
await fs.mkdir(previewDir, {recursive:true});

async function backup(file, label) {
  const bytes = await fs.readFile(file);
  const digest = sha(bytes);
  const dir = path.join(base, 'evidencias/historico', `${label}_${digest.slice(0,12)}`);
  await fs.mkdir(dir, {recursive:true});
  const target = path.join(dir, path.basename(file));
  try { assert.equal(sha(await fs.readFile(target)), digest); }
  catch (error) { if (error.code !== 'ENOENT') throw error; await fs.copyFile(file, target); }
  return {path:target,sha256:digest};
}

const guidePath = path.join(base, 'evidencias/Matriz_FCU_2027_GUIA_TRAZABLE_20261007.xlsx');
const previousGuide = await backup(guidePath, 'guia_antes_emprendimiento');
const manifestPath = guidePath.replace(/\.xlsx$/, '.manifest.json');
const previousManifest = JSON.parse(await fs.readFile(manifestPath, 'utf8'));
await fs.copyFile(manifestPath, path.join(path.dirname(previousGuide.path), path.basename(manifestPath)));
const guide = await SpreadsheetFile.importXlsx(await FileBlob.load(guidePath));
const cross = guide.worksheets.getItem('Cruces');
const display = guide.worksheets.getItem('Guía para editar');
const rawBefore = {};
for (const name of ['RAW FCU 2026','RAW FCU 2027','RAW Institucionales']) {
  rawBefore[name] = guide.worksheets.getItem(name).getUsedRange().values;
}
const originalCross = cross.getUsedRange().values;
const row = originalCross.findIndex(r => r[1] === 'G02Q95' && !r[2]) + 1;
if (!row) throw new Error('Missing G02Q95 crosswalk row');
const before = await guide.render({sheetName:'Cruces',range:`L${row}:N${row}`,scale:1,format:'png'});
await fs.writeFile(path.join(previewDir,'guia_antes.png'),new Uint8Array(await before.arrayBuffer()));
cross.getRange(`M${row}`).values = [[decision.decision + ' La respuesta institucional no modifica SIT_LAB. Consultar el registro de preguntas institucionales 2027.']];
cross.getRange(`W${row}`).values = [['Decision del usuario 2026-10-09: agregar pregunta independiente; codigo nuevo pendiente.']];
display.getRange(`A${row}:M${row}`).format.rowHeight = 200;

let additionRow = originalCross.findIndex(r => r[0] === decision.id) + 1;
if (!additionRow) additionRow = originalCross.length + 1;
cross.getRange(`A${additionRow}:X${additionRow}`).copyFrom(cross.getRange(`A${row}:X${row}`),'all');
const action = decision.decision + ' Su codigo y opciones quedan pendientes de identificar por exportacion. No convertir a SIT_LAB.';
const crossValues = [decision.id,'','','','Pregunta institucional nueva 2027','','','','',
  'Decision expresa del usuario 2026-10-09','','CONSERVAR INSTITUCIONAL',action,decision.text,
  decision.group,'','PREGUNTAS_INSTITUCIONALES_2027.json','','','INSTITUCIONAL',
  'CODIGO_LIME_PENDIENTE',decision.text,'Creacion de pregunta independiente; no agregar una alternativa a G02Q95.',''];
cross.getRange(`A${additionRow}:X${additionRow}`).values = [crossValues];
display.getRange(`A${additionRow}:M${additionRow}`).copyFrom(display.getRange(`A${row}:M${row}`),'all');
display.getRange(`A${additionRow}:M${additionRow}`).clear({applyTo:'contents'});
const formulas = {
  A:`=Cruces!L${additionRow}&CHAR(10)&"Qué hacer: "&Cruces!M${additionRow}&CHAR(10)&"Cómo queda: "&Cruces!N${additionRow}`,
  B:`=IF(Cruces!R${additionRow}="","",Cruces!R${additionRow})`,
  C:`=IF(Cruces!S${additionRow}="","",Cruces!S${additionRow})`,
  D:`=Cruces!O${additionRow}`, E:`=IF(Cruces!P${additionRow}="","",Cruces!P${additionRow})`,
  F:`=Cruces!V${additionRow}`,G:`=Cruces!L${additionRow}`,H:`=Cruces!A${additionRow}`,
  J:`=Cruces!U${additionRow}`,M:`=Cruces!T${additionRow}`
};
for (const [col, formula] of Object.entries(formulas)) display.getRange(`${col}${additionRow}`).formulas=[[formula]];
display.getRange(`I${additionRow}`).values=[[`Cruces!A${additionRow}:X${additionRow}`]];
display.getRange(`A${additionRow}:M${additionRow}`).format.rowHeight=220;
cross.getRange(`L${additionRow}:N${additionRow}`).format.rowHeight=160;
guide.recalculate();
for (const [name, values] of Object.entries(rawBefore)) assert.deepEqual(guide.worksheets.getItem(name).getUsedRange().values, values);
assert(String(display.getRange(`A${additionRow}`).values[0][0]).includes(decision.text));
assert.equal(display.getRange(`B${additionRow}`).values[0][0], '');
for (const [label, range] of [['guia_laboral',`A${row}:C${row}`],['guia_nueva',`A${additionRow}:C${additionRow}`]]) {
  const blob=await guide.render({sheetName:'Guía para editar',range,scale:1,format:'png'});
  await fs.writeFile(path.join(previewDir,`${label}.png`),new Uint8Array(await blob.arrayBuffer()));
}
const candidate = path.join(previewDir,path.basename(guidePath));
await (await SpreadsheetFile.exportXlsx(guide)).save(candidate);
await fs.copyFile(candidate,guidePath);
const guideHash=sha(await fs.readFile(guidePath));
const policyHash=sha(await fs.readFile(registryPath));
const guideManifest={...previousManifest,sha256:guideHash,updated_date:'2026-10-09',
  previous_version:previousGuide,institutional_questions:{path:registryPath,sha256:policyHash,
    id:decision.id,status:decision.status,code:null,decision:decision.decision},
  institutional_decision_rows:1,raw_sheets_preserved:Object.keys(rawBefore)};
await fs.writeFile(manifestPath,JSON.stringify(guideManifest,null,2)+'\n');
for (const target of [guidePath+'.sha256',path.join(base,'hashes',path.basename(guidePath)+'.sha256')]) {
  await fs.writeFile(target,`${guideHash}  ${path.basename(guidePath)}\n`);
}

const previousObservations=await backup(observationsPath,'observaciones_antes_emprendimiento');
const observations=await SpreadsheetFile.importXlsx(await FileBlob.load(observationsPath));
const sheet=observations.worksheets.getItem('Observaciones');
const original=sheet.getRange('A1:F100').values;
const observationRow=original.findIndex(r=>String(r[1] ?? '').startsWith('G02Q95'))+1;
if(!observationRow) throw new Error('Missing work-status observation');
const updates={
  [`B${observationRow}`]:'G02Q95 (referencia); nuevo codigo pendiente',
  [`C${observationRow}`]:'Situación laboral / pregunta institucional nueva',
  [`D${observationRow}`]:'Bloque FCU sin modificar; pregunta nueva INSTITUCIONAL',
  [`E${observationRow}`]:'Cambio por realizar: agregar una pregunta nueva e independiente «Tengo un emprendimiento formalizado». Mantener G02Q95 y G02Q20 sin agregar esta alternativa.',
  [`F${observationRow}`]:'PPT 9. Manual: pp. 21–22, P17. Categorías oficiales: no trabajo, tiempo completo, parcial y esporádico. Pregunta nueva institucional, sin campo PES ni conversión a SIT_LAB. Código pendiente. Decisión registrada el 09-10-2026.'
};
for(const [cell,value] of Object.entries(updates)) sheet.getRange(cell).values=[[value]];
sheet.getRange(`A${observationRow}:F${observationRow}`).format.rowHeight=100;
observations.recalculate();
const after=sheet.getRange('A1:F100').values;
for(let r=0;r<original.length;r++) for(let c=0;c<original[r].length;c++) {
  const cell=String.fromCharCode(65+c)+(r+1);
  if(!(cell in updates)) assert.deepEqual(after[r][c],original[r][c],cell);
}
const preview=await observations.render({sheetName:'Observaciones',range:`A${observationRow}:F${observationRow}`,scale:1,format:'png'});
await fs.writeFile(path.join(previewDir,'observaciones.png'),new Uint8Array(await preview.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(observations)).save(observationsPath);
const evidenceCopy=path.join(base,'evidencias',path.basename(observationsPath));
await fs.copyFile(observationsPath,evidenceCopy);
const observationHash=sha(await fs.readFile(evidenceCopy));
assert.equal(sha(await fs.readFile(observationsPath)),observationHash);
await fs.writeFile(path.join(base,'hashes',path.basename(evidenceCopy)+'.sha256'),`${observationHash}  ${path.basename(evidenceCopy)}\n`);
const manifest={date:'2026-10-09',decision_id:decision.id,registry:{path:registryPath,sha256:policyHash},
  guide:{path:guidePath,sha256:guideHash,previous:previousGuide,added_row:additionRow,changed_work_row:row},
  observations:{path:evidenceCopy,external_copy:observationsPath,sha256:observationHash,previous:previousObservations},
  authoring_script:{path:path.join(root,'scripts/gobernanza/registrar_emprendimiento_fcu_2027.mjs'),
    sha256:sha(await fs.readFile(path.join(root,'scripts/gobernanza/registrar_emprendimiento_fcu_2027.mjs')))},
  raw_sheets_preserved:true,limesurvey_code:null,official_pes_field:null,
  status:'DECISION_GOBERNADA_LOCALMENTE_CODIGO_PENDIENTE',git_publication:'NO_COMMIT_NO_PUSH'};
await fs.writeFile(path.join(base,'json/MANIFIESTO_EMPRENDIMIENTO_20261009.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({guide:guidePath,observations:observationsPath,evidenceCopy,guideHash,observationHash,additionRow}));
