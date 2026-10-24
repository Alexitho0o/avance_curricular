/** Libro de consulta y trazabilidad; no contiene identificadores de personas. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const [input, output, previews] = process.argv.slice(2);
if (!input || !output || !previews) throw new Error('Uso: node generar_diccionario_sies_umas.mjs libro.json salida.xlsx previews');
const payload = JSON.parse(await fs.readFile(input, 'utf8'));
const wb = Workbook.create();
const query = wb.worksheets.add('Consulta');
const navy = '#173B55', teal = '#176B70', ink = '#20384A', pale = '#EAF4FA';
const col = n => { let s=''; for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s; };
const meta = new Map(payload.sheets.map(s=>[s.name,s]));
for (const info of payload.sheets) wb.worksheets.add(info.name);
for (const [i, info] of payload.sheets.entries()) {
  const s = wb.worksheets.getItem(info.name), end = col(info.headers.length-1), last = info.rows.length+4;
  const used = s.getRange(`A1:${end}${last}`);
  used.format.font = {name:'Calibri',size:11,color:ink};
  used.format.verticalAlignment = 'center';
  used.format.rowHeight = 34;
  s.showGridLines = false;
  s.tabColor = i < 2 ? teal : '#6D8799';
  const titleEnd=col(Math.min(info.headers.length,6)-1);
  s.mergeCells(`A1:${titleEnd}1`); s.getRange('A1').values = [[info.title]];
  s.getRange(`A1:${titleEnd}1`).format = {fill:navy,font:{name:'Calibri',size:18,bold:true,color:'#FFFFFF'},rowHeight:38};
  s.mergeCells(`A2:${titleEnd}2`); s.getRange('A2').values = [[info.subtitle]];
  s.getRange(`A2:${titleEnd}2`).format.wrapText = true; s.getRange(`A2:${titleEnd}2`).format.rowHeight = 46;
  s.getRange(`A4:${end}4`).values = [info.headers];
  s.getRange(`A5:${end}${last}`).values = info.rows;
  s.getRange(`A4:${end}${last}`).format.wrapText = true;
  info.headers.forEach((h,j)=>{
    const c=col(j), r=s.getRange(`${c}5:${c}${last}`);
    s.getRange(`${c}1:${c}${last}`).format.columnWidth = info.widths[j] || 24;
    // Identifiers remain strings; numeric years/counts retain numeric types.
    const isText=info.rows.every(row=>row[j]===null||row[j]===''||typeof row[j]==='string');
    r.setNumberFormat(isText?'@':'0');
    if(!isText) r.format.horizontalAlignment='center';
  });
  const table = s.tables.add(`A4:${end}${last}`,true,`DiccionarioTabla${i+1}`);
  table.style='TableStyleMedium2'; table.showFilterButton=true;
  s.getRange(`A4:${end}4`).format = {fill:navy,font:{name:'Calibri',bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:48};
  // Estimate wrapping from the actual content; no truncation of source evidence.
  for (let ri=0;ri<info.rows.length;ri++) {
    const lines = Math.max(...info.rows[ri].map((v,ci)=>String(v??'').split('\n').reduce((n,x)=>n+Math.max(1,Math.ceil(x.length/Math.max(8,(info.widths[ci]||24)-3))),0)));
    s.getRange(`A${ri+5}:${end}${ri+5}`).format.rowHeight = Math.min(360,Math.max(34,lines*15+8));
  }
  s.freezePanes.freezeRows(4); s.freezePanes.freezeColumns(2);
}
function ref(sheet, header) {
  const m=meta.get(sheet), i=m.headers.indexOf(header);
  if(i<0) throw new Error(`Falta ${header} en ${sheet}`);
  return `'${sheet}'!$${col(i)}$5:$${col(i)}$${m.rows.length+4}`;
}
const dc=ref('Diccionario SIES','Código Único');
const ek=ref('Equivalencias UMAS','Clave UMAS');
const ev=ref('Equivalencias UMAS','Clave con versión');
const ec=ref('Equivalencias UMAS','Código Único');
const qv=(cell,v)=>{query.getRange(cell).values=[[v]];};
const qf=(cell,f)=>{query.getRange(cell).formulas=[[f]];};
query.showGridLines=false; query.tabColor=navy;
query.getRange('A1:B44').format={font:{name:'Calibri',size:11,color:ink},verticalAlignment:'center',rowHeight:25};
query.getRange('B5:B43').format.horizontalAlignment='left';
query.getRange('A1:A44').format.columnWidth=32;
query.getRange('B1:B44').format.columnWidth=91;
for(const [r,title] of [[1,'Diccionario SIES ↔ UMAS · 2007–2026'],[4,'1 · Buscar un Código Único'],[21,'2 · Consultar una equivalencia UMAS del catálogo 2026']]) {
  query.mergeCells(`A${r}:B${r}`); qv(`A${r}`,title);
  query.getRange(`A${r}:B${r}`).format={fill:navy,font:{name:'Calibri',size:r===1?18:12,bold:true,color:'#FFFFFF'},rowHeight:r===1?38:30};
}
query.mergeCells('A2:B2'); qv('A2','Edite las celdas celestes. Las tablas permiten filtrar por carrera, sede, jornada, modalidad, versión y año.');
query.getRange('A2:B2').format.wrapText=true; query.getRange('A2:B2').format.rowHeight=36;
qv('A5','Código Único');qv('B5','I162S2C77J4V1');
qv('A6','Coincidencias exactas');qf('B6',`=IF(B5="","",COUNTIF(${dc},B5))`);
const outputs=[['Nombre literal referencia','Nombre carrera'],['Código carrera','Código carrera SIES'],['Sede SIES','Sede SIES'],['Jornada SIES','Jornada SIES'],['Modalidad SIES','Modalidad SIES'],['Versión SIES','Versión SIES'],['Tipo plan','Tipo plan'],['En oferta2026','Incluido en oferta 2026'],['Años MRUN','Años observados en MRUN'],['CODCARPR asociados','CODCARPR asociados'],['Estado cruce UMAS','Estado equivalencia UMAS'],['Fuente nombre','Fuente del nombre'],['Año fuente nombre','Año de la fuente del nombre']];
outputs.forEach(([h,label],i)=>{const row=i+7,lookup=`INDEX(${ref('Diccionario SIES',h)},MATCH(B5,${dc},0))`;qv(`A${row}`,label);qf(`B${row}`,`=IF(B6=1,IF(${lookup}="","",${lookup}),IF(B5="","","Sin coincidencia única"))`);});
const fields=[[22,'Año del catálogo',2026],[23,'CODCARPR','CILOG'],[24,'NOMBRE_L','INGENIERIA EN LOGISTICA'],[25,'Jornada UMAS','O'],[26,'Sede UMAS','RE'],[27,'Versión SIES (opcional)',null]];
fields.forEach(([r,label,v])=>{qv(`A${r}`,label);qv(`B${r}`,v);});
qv('A28','Clave normalizada');
let normalized='UPPER(TRIM(B24))';
for (const [a,b] of [['Á','A'],['É','E'],['Í','I'],['Ó','O'],['Ú','U'],['Ü','U'],['Ñ','N']]) normalized=`SUBSTITUTE(${normalized},"${a}","${b}")`;
qf('B28',`=UPPER(TRIM(B23))&"|"&UPPER(TRIM(B25))&"|"&UPPER(TRIM(B26))&"|"&${normalized}`);
qv('A29','Candidatos de la llave');
qf('B29',`=IF(OR(B22<>2026,B23="",B24="",B25="",B26=""),"",IF(B27="",COUNTIF(${ek},B28),COUNTIF(${ev},B34)))`);
qv('A30','Resultado de la búsqueda');
qf('B30','=IF(B22<>2026,"Sin catálogo anual verificado",IF(OR(B23="",B24="",B25="",B26=""),"Complete los cuatro campos UMAS",IF(B29=0,"Sin equivalencia exacta",IF(B29=1,"Candidato único del catálogo 2026","Ambiguo: requiere versión acreditada"))))');
qv('A31','Código Único candidato');
qf('B31',`=IF(AND(B22=2026,B29=1),IF(B27="",_xlfn.XLOOKUP(B28,${ek},${ec},"",0),_xlfn.XLOOKUP(B34,${ev},${ec},"",0)),"")`);
qv('A32','Nombre carrera');
qf('B32',`=IF(B31="","",INDEX(${ref('Diccionario SIES','Nombre literal referencia')},MATCH(B31,${dc},0)))`);
qv('A33','Alcance temporal');qv('B33','El año de ingreso no determina la versión con las reglas disponibles. Una versión digitada debe tener respaldo curricular.');
qv('A34','Clave con versión');qf('B34','=IF(B27="","",B28&"|"&B27)');
qv('A35','Cómo revisar candidatos');qv('B35','Copie la clave de B28 y filtre «Clave UMAS» en Equivalencias UMAS. No se selecciona la primera coincidencia ni la versión máxima.');
qv('A37','Cobertura histórica');qv('B37','Incluye toda la unión disponible: oferta 2010–2026 y MRUN 2007–2026. Las ofertas no observadas en MRUN de 2007–2009 no se pueden acreditar con estas fuentes.');
qv('A39','Nombres oficiales');qv('B39','Para códigos presentes en oferta 2026 se conserva su NOMBRE_CARRERA literal. Los restantes conservan el último nombre histórico disponible, con fuente y año.');
qv('A41','Campos distintos');qv('B41','Año de matrícula, año de ingreso y versión son campos diferentes. Jornada, modalidad y tipo de plan se conservan separados del nombre de la carrera.');
qv('A43','Ejemplos sin datos personales');qv('B43','Cada código tiene un localizador de ejemplo en Diccionario SIES. Ejemplos UMAS muestra combinaciones reales y su fila de origen, sin identificar estudiantes.');
query.getRange('A5:B43').format.wrapText=true;
for(const r of [19,24,28,30,33,35,37,39,41,43])query.getRange(`A${r}:B${r}`).format.rowHeight=r>=33?46:34;
for(const r of [7,15,16])query.getRange(`A${r}:B${r}`).format.rowHeight=46;
for(const a of ['B5','B22:B27'])query.getRange(a).format={fill:pale,font:{color:'#14588C',bold:true},borders:{preset:'outside',style:'thin',color:'#7FAFCA'}};
query.getRange('B5').setNumberFormat('@');query.getRange('B23:B27').setNumberFormat('@');query.getRange('B22').setNumberFormat('0');
query.getRange('B30').conditionalFormats.add('containsText',{text:'Ambiguo',format:{fill:'#FFF0CD',font:{color:'#8A5100',bold:true}}});
query.getRange('B30').conditionalFormats.add('containsText',{text:'Sin ',format:{fill:'#FCE3DF',font:{color:'#922F27'}}});
query.freezePanes.freezeRows(4);

// Recalculation tests exercise exact, ambiguous, missing and historical paths.
const qa=[];
function assertValue(cell,expected,test){const actual=query.getRange(cell).values[0][0];if(actual!==expected){console.log(JSON.stringify({debug:query.getRange('B22:B32').values,formulas:query.getRange('B28:B32').formulas}));throw new Error(`${test}: ${cell} ${JSON.stringify(actual)} != ${JSON.stringify(expected)}`);}qa.push({test,cell,expected,actual});}
wb.recalculate();
assertValue('B7','INGENIERIA EN LOGISTICA','Nombre literal oferta');
assertValue('B29',2,'CILOG ambiguo sin versión');assertValue('B31','','No seleccionar ambiguo');
qv('B27','1');wb.recalculate();assertValue('B31','I162S2C77J4V1','Versión explícita 1');
qv('B27','2');wb.recalculate();assertValue('B31','I162S2C77J4V2','Versión explícita 2');
qv('B27',null);qv('B23','ILOG');wb.recalculate();assertValue('B29',1,'ILOG candidato único');assertValue('B31','I162S2C77J4V1','ILOG versión del puente');
qv('B22',2025);wb.recalculate();assertValue('B31','','No extrapolar a 2025');
qv('B22',2026);qv('B23','INEXISTENTE');wb.recalculate();assertValue('B29',0,'Llave inexistente');assertValue('B31','','No inventar equivalencia');
qv('B23','');wb.recalculate();assertValue('B30','Complete los cuatro campos UMAS','Campo pendiente');
qv('B23','CILOG');qv('B5','I162S2C46J4V2');wb.recalculate();assertValue('B6',1,'Código histórico fuera catálogo actual');
qv('B5','INEXISTENTE');wb.recalculate();assertValue('B6',0,'Código SIES inexistente');
qv('B5','I162S2C77J4V1');wb.recalculate();
for(const info of payload.sheets){const actual=wb.worksheets.getItem(info.name).getRange(`A5:${col(info.headers.length-1)}${info.rows.length+4}`).values;if(JSON.stringify(actual)!==JSON.stringify(info.rows))throw new Error(`Datos alterados en ${info.name}`);}
await fs.mkdir(previews,{recursive:true});
const inspection=await wb.inspect({kind:'table',range:'Consulta!A22:B32',include:'values,formulas',tableMaxRows:11,tableMaxCols:2,maxChars:6000});
await fs.writeFile(path.join(previews,'inspeccion_consulta.ndjson'),inspection.ndjson);
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:50},summary:'Errores de fórmulas'});
await fs.writeFile(path.join(previews,'errores_formula.ndjson'),errors.ndjson);
for(const [name,range] of [['Consulta','A1:B43'],...payload.sheets.map(s=>[s.name,`A1:${col(Math.min(s.headers.length-1,5))}9`])]){
 const blob=await wb.render({sheetName:name,range,scale:1.3,format:'png'});await fs.writeFile(path.join(previews,`${name}.png`),new Uint8Array(await blob.arrayBuffer()));
}
await fs.mkdir(path.dirname(output),{recursive:true});
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(output);
await fs.writeFile(path.join(previews,'qa_formulas.json'),JSON.stringify(qa,null,2));
console.log(JSON.stringify({output,sheets:payload.sheets.map(s=>({name:s.name,rows:s.rows.length})),formula_tests:qa.length,errors:errors.ndjson}));
