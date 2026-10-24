// Edición D4 aditiva: conserva C1; lectura/autoría con Artifact Tool.
import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';
const base = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const p = JSON.parse(await fs.readFile(path.join(base, 'libro_d4.json'), 'utf8'));
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(process.argv.includes('--review') ? p.output : p.source));
const navy = '#173B55', ink = '#243746';
const col = n => {let s=''; for(n++; n; n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s; return s;};
const previewName = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replaceAll(' ','_')+'.png';
async function render(name, range, file) {
 const b = await wb.render({sheetName:name, range, scale:1, format:'png'});
 await fs.writeFile(path.join(base, file), new Uint8Array(await b.arrayBuffer()));
}
if (process.argv.includes('--review')) {
 await render('Códigos D3', 'N38:Q40', 'revision_ids_codigos.png');
 await render('Planes D3', 'F101:I103', 'revision_ids_planes.png');
 await render('Dictámenes D3', 'J359:O360', 'revision_evidencia.png');
 console.log('Revisión visual del XLSX exportado completada, sin cambios.');
 process.exit(0);
}
if (process.argv.includes('--preview')) {
 await render('Consulta', 'A1:C18', 'antes_consulta.png');
 await render('Diccionario SIES', 'R5:U9', 'antes_sectores.png');
 console.log('Vistas previas C1 conservadas.');
 process.exit(0);
}
const q = wb.worksheets.add('Cierre D4');
for (const [i, info] of p.sheets.entries()) {
 const s=wb.worksheets.add(info.name), n=info.rows.length+5, end=col(info.headers.length-1);
 s.showGridLines=false;
 s.getRange(`A1:${end}${n}`).format={font:{name:'Arial',size:11,color:ink},rowHeight:32,verticalAlignment:'center'};
 s.getRange('A2').values=[[info.name]];
 s.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:navy};
 s.getRange('A3').values=[[info.note]];
 s.getRange(`A5:${end}5`).values=[info.headers];
 s.getRange(`A6:${end}${n}`).values=info.rows;
 s.getRange(`A5:${end}${n}`).format.wrapText=true;
 info.headers.forEach((h,j)=>{
  s.getRange(`${col(j)}1:${col(j)}${n}`).format.columnWidth=info.widths[j];
  s.getRange(`${col(j)}6:${col(j)}${n}`).setNumberFormat(info.rows.every(r=>r[j]===null||typeof r[j]==='string')?'@':'0');
 });
 for (let j=0;j<info.rows.length;j++) {
  const ln=Math.max(...info.rows[j].map((v,k)=>String(v??'').split('\n').reduce((a,t)=>a+Math.max(1,Math.ceil(t.length/(info.widths[k]-4))),0)));
  s.getRange(`A${j+6}:${end}${j+6}`).format.rowHeight=Math.min(409,Math.max(34,ln*15+10));
 }
 s.tables.add(`A5:${end}${n}`,true,`D4Tabla${i+1}`).style='TableStyleMedium2';
 s.getRange(`A5:${end}5`).format={fill:navy,font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},rowHeight:54,wrapText:true,horizontalAlignment:'center'};
 s.freezePanes.freezeRows(5); s.freezePanes.freezeColumns(2);
}
q.showGridLines=false; q.tabColor=navy;
q.getRange('A1:C40').format={font:{name:'Arial',size:11,color:ink},rowHeight:30,verticalAlignment:'center',wrapText:true};
q.getRange('A1:A40').format.columnWidth=48;
q.getRange('B1:B40').format.columnWidth=66;
q.getRange('C1:C40').format.columnWidth=36;
const v=(a,x)=>q.getRange(a).values=[[x]], f=(a,x)=>q.getRange(a).formulas=[[x]];
v('A2','Cierre del análisis · D4'); q.getRange('A2:B2').format.font={name:'Arial',size:16,bold:true,color:navy};
v('A4','Conclusión'); v('B4','Análisis cerrado con brechas. Las relaciones observadas no acreditan por sí solas la vigencia de una malla.');
q.getRange('A4:C4').format.rowHeight=64;
v('A6','Consulta por contexto B4'); v('B6','B4-00001'); q.getRange('B6').format.fill='#FFF2CC'; q.getRange('B6').setNumberFormat('@');
v('C6','Copie el ID de Dictámenes D3.');
const n=p.sheets.find(x=>x.name==='Dictámenes D3').rows.length+5;
v('A7','Coincidencias'); f('B7',`=COUNTIFS('Dictámenes D3'!$A$6:$A$${n},B6)`);
v('A8','Posición'); f('B8',`=IF(B7=1,MATCH(B6,'Dictámenes D3'!$A$6:$A$${n},0),0)`);
const lookup=c=>`INDEX('Dictámenes D3'!$${c}$6:$${c}$${n},B8)`;
v('A10','Dictamen'); f('B10',`=IF(B6="","ENTRADA_INCOMPLETA",IF(B7=0,"CONTEXTO_NO_ENCONTRADO",IF(B7>1,"CLAVE_DUPLICADA",${lookup('B')})))`);
for (const [row, label, c] of [[11,'Carrera UMAS','C'],[12,'Año observado','F'],[13,'Planes observados','I'],[14,'Códigos observados','K'],[15,'Alcance de la evidencia','J'],[16,'Causas de abstención','N'],[17,'Agenda de brechas','R']]) {
 v('A'+row,label); f('B'+row,`=IF(AND(B6<>"",B7=1),${lookup(c)},"")`);
}
q.getRange('A10:C10').format.rowHeight=48;
q.getRange('A15:C15').format.rowHeight=60;
q.getRange('A16:C17').format.rowHeight=160;
v('A18','Asignación productiva'); v('B18','No habilitada en todos los contextos de esta edición.');
v('A20','Balance por contexto'); q.getRange('A20:C20').format={fill:navy,font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'}};
const states=Object.keys(p.resumen.dictamen_contextos);
states.forEach((state,i)=>{v('A'+(i+21),state);f('B'+(i+21),`=COUNTIFS('Dictámenes D3'!$B$6:$B$${n},A${i+21})`);});
q.getRange('A21:C26').format.rowHeight=43;
v('A27','Total de contextos'); f('B27','=SUM(B21:B26)');
v('A28','Códigos SIES / planes UMAS'); v('B28','141 códigos / 236 planes. Universos separados.');
v('A30','Cómo continuar'); v('B30','Priorizar los 16 conflictos y la admisión CILOG; obtener historial de ingreso/plan y vigencias curriculares. Ver Agenda D4.');
v('A31','Conclusiones y ejemplos'); v('B31','Hipótesis D4 y Ejemplos D4 explican qué se sostiene, qué no y qué falta.');
v('A32','Qué se conserva'); v('B32','Las 14 hojas C1 y tus sectores editados. Consulta y Consulta B5 mantienen su contrato anterior.');
v('A33','Límite'); v('B33','Sin validación independiente nueva. Estado académico actual no acredita el estado histórico.');
v('A34','Portabilidad'); v('B34','Consulta gobernada en el proyecto. La reconstrucción completa todavía tiene fuentes personales externas. Sin publicación remota.');
v('A35','Fuente del cierre'); v('B35','data/cierre_d4/20261016/matriz_resultados.json y docs/d4_conclusiones_cierre_20261016.md');
q.getRange('A30:C35').format.rowHeight=65;
q.freezePanes.freezeRows(6);
const old=wb.worksheets.getItem('Consulta');
old.getRange('A63').values=[['Edición D4: abra «Cierre D4» para dictámenes, conclusiones y agenda.']];
old.getRange('A64').values=[['Las hojas previas se conservan como antecedente. D4 no habilita asignaciones.']];
old.getRange('A63:C64').format.font={name:'Arial',size:11,color:navy};
const guide=wb.worksheets.getItem('Guía');
guide.getRange('A60:C62').values=[['D4 · cierre analítico','Conclusiones y agenda; versiones no acreditadas conservan brechas.','docs/d4_conclusiones_cierre_20261016.md'],['D3 incorporado','1.986 dictámenes, 141 códigos y 236 planes; no sustituye B5.','data/validacion_d3/20261016/descriptor.json'],['Matriz íntegra','Registros D3 completos más referencias a agenda. Fuentes originales preservadas.','data/cierre_d4/20261016/matriz_resultados.json']];
guide.getRange('A60:C62').format.wrapText=true; guide.getRange('A60:C62').format.rowHeight=75;
const tests=[];
for (const state of states) {
 const r=p.sheets[0].rows.find(r=>r[1]===state); v('B6',r[0]); wb.recalculate();
 if(q.getRange('B10').values[0][0]!==state||q.getRange('B14').values[0][0]!==r[10])throw Error('Consulta '+state);
 tests.push({contexto:r[0],estado:state});
}
for (const [input,expected] of [['','ENTRADA_INCOMPLETA'],['B4-INEXISTENTE','CONTEXTO_NO_ENCONTRADO']]) {
 v('B6',input);wb.recalculate();if(q.getRange('B10').values[0][0]!==expected)throw Error(expected);
}
v('B6',tests.find(t=>t.estado==='USO_ANALITICO_CORROBORADO').contexto);wb.recalculate();
if(q.getRange('B27').values[0][0]!==1986)throw Error('Total');
for(let i=0;i<states.length;i++)if(q.getRange('B'+(i+21)).values[0][0]!==p.resumen.dictamen_contextos[states[i]])throw Error('Conteo');
await fs.writeFile(path.join(base,'qa_formulas.json'),JSON.stringify({consultas:tests,fronteras:2,total:1986,recalculo_nativo:false},null,2));
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},summary:'Errores D4'});
await fs.writeFile(path.join(base,'errores.ndjson'),errors.ndjson);
for(const [name,range,file] of [['Cierre D4','A1:C18','cierre_consulta.png'],['Cierre D4','A20:C35','cierre_balance.png'],...p.sheets.map(s=>[s.name,`A1:${col(Math.min(4,s.headers.length-1))}9`,previewName(s.name)]),['Hipótesis D4','D5:F8','hipotesis_limites.png'],['Agenda D4','G5:K8','agenda_acciones.png'],['Ejemplos D4','E5:G9','ejemplos_limites.png'],['Consulta','A63:C64','navegacion_d4.png'],['Guía','A60:C62','guia_d4.png'],['Códigos D3','G5:I10','sectores_d4.png']])await render(name,range,file);
await fs.mkdir(path.dirname(p.output),{recursive:true});
await (await SpreadsheetFile.exportXlsx(wb)).save(p.output);
console.log(JSON.stringify({output:p.output,consultas:tests.length,errores:errors.ndjson}));
