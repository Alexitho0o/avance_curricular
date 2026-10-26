import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const tmp='/tmp/retencion_revision_20261021';
const c=JSON.parse(await fs.readFile(`${tmp}/config.json`,'utf8'));
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(c.base));
const s=w.worksheets.add('Revision_agregada');
for(const [name,edits] of Object.entries(c.edits)){
 const s=w.worksheets.getItem(name);
 for(const [cell,value] of Object.entries(edits)){
  if(typeof value==='string'&&value.startsWith('='))s.getRange(cell).formulas=[[value]];
  else s.getRange(cell).values=[[value]];
 }
}
s.showGridLines=false;s.tabColor='#CFB47C';
s.getRange('A1:I70').format={font:{name:'Arial',size:11,color:'#3A3A3A'},verticalAlignment:'center',rowHeight:27};
for(const [col,width] of Object.entries({A:12,B:16,C:17,D:18,E:21,F:21,G:46,H:18,I:16}))s.getRange(`${col}:${col}`).format.columnWidth=width;
function v(cell,x){s.getRange(cell).values=[[x]];}
function f(cell,x){s.getRange(cell).formulas=[[x]];}
function merge(range,text,fill=null,height=35){s.mergeCells(range);v(range.split(':')[0],text);s.getRange(range).format.wrapText=true;s.getRange(range).format.rowHeight=height;if(fill)s.getRange(range).format.fill=fill;}
function section(row,text){merge(`A${row}:I${row}`,text,'#102B42',29);s.getRange(`A${row}:I${row}`).format.font={name:'Arial',size:11,bold:true,color:'#FFFFFF'};}
function header(row,items){s.getRange(`A${row}:I${row}`).values=[items];s.getRange(`A${row}:I${row}`).format={fill:'#0E4273',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:55,horizontalAlignment:'center',verticalAlignment:'center'};}
function band(r){if(r%2===0)s.getRange(`A${r}:I${r}`).format.fill='#F2F2F2';}
merge('A2:I2','Retención intermedia: revisión de cierres, llaves y reglas',null,36);s.getRange('A2').format.font={name:'Arial',size:17,bold:true,color:'#102B42'};
merge('A3:I3',`IPSS 162 · Revisión ${c.date} · Institucional completo; esta hoja no responde al selector de carrera.`,null,28);
merge('A4:I4','E: los cuatro cierres conservan tasa Pendiente. Las presencias y los estados en respaldos son observaciones; falta acreditar población, fecha efectiva y regla de cada cierre.','#FFF2CC',44);
section(6,'Cuatro cierres: población fija y evidencia disponible');
header(7,['Cohorte','Cierre','Denominador fijo','Presencias en listado','VIGENTE observado','Vigentes acreditados al cierre','Motivo pendiente y fuente','Cierre acreditado','Tasa intermedia']);
c.closures.forEach((x,i)=>{
 const r=8+i;v(`A${r}`,x.cohort);v(`B${r}`,x.closure);
 f(`C${r}`,`=SUMIFS('Por_carrera'!$D$7:$D$34,'Por_carrera'!$A$7:$A$34,A${r})`);
 const found=i%2===0?'F':'H',state=i%2===0?'G':'I';
 f(`D${r}`,`=SUMIFS('Por_carrera'!$${found}$7:$${found}$34,'Por_carrera'!$A$7:$A$34,A${r})`);
 if(x.state_field)f(`E${r}`,`=SUMIFS('Por_carrera'!$${state}$7:$${state}$34,'Por_carrera'!$A$7:$A$34,A${r})`);else v(`E${r}`,'Sin campo');
 v(`F${r}`,'Pendiente');v(`G${r}`,c.closure_notes[i]);v(`H${r}`,'Pendiente');
 f(`I${r}`,`=IF(AND(H${r}="Acreditado",ISNUMBER(F${r}),C${r}>0),F${r}/C${r},"Pendiente")`);
 s.getRange(`A${r}:I${r}`).format.wrapText=true;s.getRange(`A${r}:I${r}`).format.rowHeight=115;band(r);s.getRange(`F${r}:I${r}`).format.fill='#FFF2CC';
});
s.getRange('C8:E11').setNumberFormat('#,##0');s.getRange('A8:A11').setNumberFormat('0');s.getRange('I8:I11').setNumberFormat('0.00%');
merge('A13:I13','B/C: conteos reproducidos desde los cuatro listados. T3-2025: 325 personas y 328 matrículas. El cero de T3-2026 describe el listado; no representa vigencia acreditada ni deserción.',null,43);
section(15,'Revisión de las 20 personas incluidas en la cohorte 2025');
merge('A16:I16','B/C: puente explícito N_DOC–RUT en IPSS_Procesamiento.xlsx, 2025_carga, columnas BU–J; seguimiento por CODCLI exacto. Se preservan todas las matrículas. Detalle de fuentes y hashes en REVISION_LLAVES.json.',null,45);
header(18,['Carrera de origen','','','Revisadas','CODCLI identificado','Pendientes','Continuidad al cierre','','']);s.mergeCells('A18:C18');s.mergeCells('G18:I18');
c.careers.forEach((p,i)=>{const r=19+i;merge(`A${r}:C${r}`,p.career,null,42);v(`D${r}`,p.people);v(`E${r}`,p.identified);f(`F${r}`,`=D${r}-E${r}`);merge(`G${r}:I${r}`,'Pendiente; la identificación no acredita retención',null,42);band(r);});
merge('A25:C25','Total de personas (C)','#F2F2F2',30);for(const col of ['D','E','F'])f(`${col}25`,`=SUM(${col}19:${col}24)`);merge('G25:I25',c.identity_total_note,'#F2F2F2',30);
merge('A27:I27',c.identity_note,'#FFF2CC',45);
section(29,'Seguimiento de las mismas 14 personas con alguna matrícula VIGENTE en 12112');
merge('A30:I30','B/C: estados de cada extracción. Llave de matrícula: CODCLI, CODCARPR, ANOMATRICULA y PERIODOMATRICULA; no se elige una única matrícula por persona.',null,40);
header(31,['Fuente','','Personas','Matrículas','Alguna VIGENTE','Sin VIGENTE','Observación temporal','','']);s.mergeCells('A31:B31');s.mergeCells('G31:I31');
c.traces.forEach((x,i)=>{const r=32+i;merge(`A${r}:B${r}`,x.source,null,58);v(`C${r}`,x.people);v(`D${r}`,x.enrolments);v(`E${r}`,x.active);f(`F${r}`,`=C${r}-E${r}`);merge(`G${r}:I${r}`,x.note,null,58);band(r);});
merge('A36:I36',c.trace_note,'#FFF2CC',50);
merge('A37:I37',c.master_note,null,48);
section(38,'Presencias en respaldos candidatos: no sustituyen los cierres');
merge('A39:I39','B/C: cohorte fija 2025. La búsqueda por documento y el puente de las 20 personas son grupos disjuntos. Solo se suman personas encontradas; ninguna se añade al denominador.',null,42);
header(40,['Respaldo','','Denominador','Por documento','Por puente explícito','Total en respaldo','Alcance','','']);s.mergeCells('A40:B40');s.mergeCells('G40:I40');
c.snapshots.forEach((x,i)=>{const r=41+i;merge(`A${r}:B${r}`,x.source,null,55);f(`C${r}`,`=C10`);v(`D${r}`,x.document);v(`E${r}`,x.bridge);f(`F${r}`,`=SUM(D${r}:E${r})`);merge(`G${r}:I${r}`,x.note,null,55);band(r);});
merge('A44:C44','Diferencias vs. denominadores autorizados',null,37);f('D44','=C8-558');f('E44','=C10-1150');f('F44',"='Resumen'!B21-222");f('G44',"='Resumen'!B22-124");merge('H44:I44','C: deben ser cero',null,37);
section(46,'Retención interna IPSS, SIES, duración y titulación');
c.rules.forEach((x,i)=>{const r=47+i;merge(`A${r}:C${r}`,x.label,'#F2F2F2',76);merge(`D${r}:I${r}`,x.text,null,76);});
section(53,'Pendientes exactos y decisiones que no se aplicaron');
c.pending.forEach((x,i)=>merge(`A${54+i}:I${54+i}`,x,'#FFF2CC',49));
section(60,'Trazabilidad y alcance');
c.provenance.forEach((x,i)=>merge(`A${61+i}:I${61+i}`,x,null,44));
merge('A67:I67','A: definición oficial · B: dato observado · C: implementación/cálculo · D: decisión interna · E: hipótesis o pendiente. Las propuestas D/E no son reglas aprobadas.',null,36);
merge('A68:I68','D: originales, motor anual y Escenario_80 preservados. Las tasas del seguimiento anual separado siguen siendo 74/222 y 48/124. No hay identificadores individuales en esta entrega.',null,38);
s.getRange('C19:F44').setNumberFormat('#,##0');s.freezePanes.freezeRows(7);
for(const range of ['A8:F11','H8:I11','D19:F25','C32:F34','C41:F42','D44:G44'])s.getRange(range).format.horizontalAlignment='center';
// Check prerequisites independently, restoring all inputs before export.
v('H8','Acreditado');if(s.getRange('I8').values[0][0]!=='Pendiente')throw Error('Missing state must remain pending');
v('F8',1);if(Math.abs(s.getRange('I8').values[0][0]-1/558)>1e-12)throw Error('Rate sensitivity failed');
v('H8','Pendiente');if(s.getRange('I8').values[0][0]!=='Pendiente')throw Error('Missing coverage must remain pending');v('F8','Pendiente');
const summary=w.worksheets.getItem('Resumen');summary.getRange('H4').values=[['INGENIERIA EN INFORMATICA']];
if(summary.getRange('F10').values[0][0]!==c.careers.find(x=>x.career==='INGENIERIA EN INFORMATICA').pending)throw Error('Career key selector failed');
summary.getRange('H4').values=[['Todas']];
w.recalculate();
const scan=await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},maxChars:5000});
await fs.writeFile(`${tmp}/formula_scan.ndjson`,scan.ndjson);
await fs.writeFile(`${tmp}/inspect.ndjson`,(await w.inspect({kind:'table',range:'Revision_agregada!A7:I11',include:'values,formulas',tableMaxRows:5,tableMaxCols:9,maxChars:9000})).ndjson);
for(const [name,sheetName,range] of [['resumen','Resumen','A1:I23'],['llaves','Revision_agregada','A15:I27'],['seguimiento','Revision_agregada','A29:I44'],['reglas','Revision_agregada','A46:I68'],['cierres','Revision_agregada','A1:I13'],['carreras','Por_carrera','A18:K39'],['bases','Bases_por_confirmar','A1:F18'],['fuentes','Fuentes_y_alcance','A18:F25']]){
 const img=await w.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(`${tmp}/${name}.png`,new Uint8Array(await img.arrayBuffer()));
}
await(await SpreadsheetFile.exportXlsx(w)).save(`${tmp}/candidate.xlsx`);
console.log('Artifact authoring and recalculation complete.');
