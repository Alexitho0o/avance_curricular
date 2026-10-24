import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const base=path.resolve(import.meta.dirname,'..');
const p=JSON.parse(await fs.readFile(path.join(base,'libro_c1.json'),'utf8'));
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(p.source));
const col=i=>{let s='';for(i++;i;i=Math.floor((i-1)/26))s=String.fromCharCode(65+(i-1)%26)+s;return s;};
async function render(name,range,file){const b=await wb.render({sheetName:name,range,scale:1,format:'png'});await fs.writeFile(path.join(base,file),new Uint8Array(await b.arrayBuffer()));}
if(process.argv.includes('--preview')){
 await render('Consulta','A1:C18','antes_consulta.png');
 await render('Diccionario SIES','R5:V9','antes_sectores.png');
 console.log((await wb.inspect({kind:'sheet',include:'id,name',maxChars:2000})).ndjson);
 process.exit(0);
}
const navy='#173B55',ink='#243746';
const query=wb.worksheets.add('Consulta B5');
for(const [idx,info] of p.sheets.entries()){
 const s=wb.worksheets.add(info.name),n=info.rows.length+5,end=col(info.headers.length-1);
 s.showGridLines=false;
 s.getRange(`A1:${end}${n}`).format={font:{name:'Arial',size:11,color:ink},rowHeight:32,verticalAlignment:'center'};
 s.getRange('A2').values=[[info.name+' · edición C1']];s.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:navy};
 s.getRange('A3').values=[[info.note]];
 s.getRange(`A5:${end}5`).values=[info.headers];s.getRange(`A6:${end}${n}`).values=info.rows;
 s.getRange(`A5:${end}${n}`).format.wrapText=true;
 info.headers.forEach((h,i)=>{s.getRange(`${col(i)}1:${col(i)}${n}`).format.columnWidth=info.widths[i];s.getRange(`${col(i)}6:${col(i)}${n}`).setNumberFormat(info.rows.every(r=>r[i]===null||typeof r[i]==='string')?'@':'0');});
 for(let i=0;i<info.rows.length;i++){
  const lines=Math.max(...info.rows[i].map((v,j)=>String(v??'').split('\n').reduce((a,t)=>a+Math.max(1,Math.ceil(t.length/(info.widths[j]-3))),0)));
  s.getRange(`A${i+6}:${end}${i+6}`).format.rowHeight=Math.max(32,Math.min(330,lines*14+6));
 }
 s.tables.add(`A5:${end}${n}`,true,`C1Tabla${idx+1}`).style='TableStyleMedium2';
 s.getRange(`A5:${end}5`).format={fill:navy,font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},rowHeight:52,wrapText:true,horizontalAlignment:'center'};
 s.freezePanes.freezeRows(5);s.freezePanes.freezeColumns(2);
}
query.showGridLines=false;query.tabColor=navy;
query.getRange('A1:C39').format={font:{name:'Arial',size:11,color:ink},rowHeight:29,verticalAlignment:'center'};
query.getRange('A1:A39').format.columnWidth=34;query.getRange('B1:B39').format.columnWidth=65;query.getRange('C1:C39').format.columnWidth=34;
const v=(a,x)=>query.getRange(a).values=[[x]],f=(a,x)=>query.getRange(a).formulas=[[x]];
v('A2','Consulta de reglas históricas B5');query.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:navy};
v('A4','Edite las celdas amarillas. El resultado es evidencia observada, no equivalencia acreditada.');
const labels=['Modelo','Carrera UMAS','Sede UMAS','Jornada UMAS','Año observado','Ingreso original','Primera observación en carrera','Planes observados','Período de ingreso UMAS','Año de matrícula UMAS','Período de matrícula UMAS'];
labels.forEach((x,i)=>v(`A${i+7}`,x));
query.getRange('B7:B17').format.fill='#FFF2CC';query.getRange('B7:B10').setNumberFormat('@');query.getRange('B12').setNumberFormat('@');query.getRange('B14:B17').setNumberFormat('@');
query.getRange('B7').dataValidation={rule:{type:'list',values:['K0','K1','K2','K3']}};
v('C14','Sin plan: PLAN_NO_OBSERVADO. Varios planes: uno por línea, ordenados.');query.getRange('C14:C17').format.wrapText=true;query.getRange('A14:C14').format.rowHeight=68;
v('C15','K1 y K3');v('C16','K2 y K3');v('C17','K2 y K3');
const labelRows={20:'Estado de la evidencia',21:'Códigos candidatos',22:'Regla observada',23:'Personas de construcción',24:'Coincidencias en reserva',25:'Contradicciones en reserva',26:'Asignación productiva',29:'Clave de búsqueda',30:'Coincidencias exactas',31:'Posición de la regla',32:'Entrada completa',35:'Reglas K0 corroboradas',36:'Reglas K0 sin reserva',37:'Reglas K0 conflictivas',38:'Reglas K0 contradictorias'};
Object.entries(labelRows).forEach(([r,l])=>v('A'+r,l));
query.getRange('B20:B29').format.wrapText=true;query.getRange('A20:C22').format.rowHeight=48;query.getRange('A29:C29').format.rowHeight=90;
const key=cells=>cells.map(c=>`LEN(${c})&":"&${c}`).join('&"|"&');
const stem=key(['B7','B8','B9','B10','B11','B12','B13','B14']);
f('B29','='+stem+'&IF(OR(B7="K1",B7="K3"),"|"&LEN(B15)&":"&B15,"")&IF(OR(B7="K2",B7="K3"),"|"&LEN(B16)&":"&B16&"|"&LEN(B17)&":"&B17,"")');
const n=p.rules.length+5,rs=wb.worksheets.getItem('Reglas B5');
rs.getRange('T5').values=[['Posición consulta B5']];rs.getRange(`T6:T${n}`).formulas=p.rules.map((_,i)=>[`=IF(EXACT(S${i+6},'Consulta B5'!B29),${i+1},0)`]);rs.getRange(`T5:T${n}`).format.columnWidth=24;
f('B30',`=COUNTIFS('Reglas B5'!$T$6:$T$${n},">0")`);f('B31',`=SUM('Reglas B5'!$T$6:$T$${n})`);
f('B32','=AND(OR(B7="K0",B7="K1",B7="K2",B7="K3"),B8<>"",B9<>"",B10<>"",ISNUMBER(B11),B12<>"",ISNUMBER(B13),B14<>"",IF(OR(B7="K1",B7="K3"),B15<>"",TRUE),IF(OR(B7="K2",B7="K3"),AND(B16<>"",B17<>""),TRUE))');
const lookup=c=>`INDEX('Reglas B5'!$${c}$6:$${c}$${n},B31)`;
f('B20',`=IF(NOT(B32),"ENTRADA_INCOMPLETA",IF(B30=0,"SIN_REGLA_OBSERVADA",IF(B30>1,"CONFLICTO_CLAVE_DUPLICADA",${lookup('M')})))`);
for(const [row,c] of [[21,'N'],[22,'A'],[23,'O'],[24,'P'],[25,'Q']])f('B'+row,`=IF(AND(B32,B30=1),${lookup(c)},"")`);
v('B26','No habilitada');
for(const [row,state] of [[35,'CORROBORADA_EN_RESERVA'],[36,'OBSERVADA_SIN_RESERVA'],[37,'CONFLICTO_CONSTRUCCION'],[38,'CONTRADICCION_EN_RESERVA']])f('B'+row,`=COUNTIFS('Reglas B5'!$B$6:$B$${n},"K0",'Reglas B5'!$M$6:$M$${n},"${state}")`);
query.getRange('B20').conditionalFormats.add('containsText',{text:'CONTRADICCION',format:{fill:'#FCE6E2',font:{color:'#9C3026'}}});
const old=wb.worksheets.getItem('Consulta');old.getRange('A60').values=[['Edición C1: consulte «Consulta B5» para reglas observadas y «Matriz B4» para evidencia.']];old.getRange('A61').values=[['La consulta anterior conserva el contrato H5. Sector IPSS y Estado sector mantienen su edición.']];
old.getRange('A60:C61').format.font={name:'Arial',size:11,color:navy};
const guide=wb.worksheets.getItem('Guía');
guide.getRange('A51:C57').values=[['Edición C1','B4 y B5 incorporados','2026-10-16'],['Reglas observadas','197 reglas K0 corroboradas en reserva; no acreditación formal.','data/reglas_historicas_b5/20261016/manifest.json'],['Matriz académica','1.986 contextos. No sumar personas entre contextos.','data/matriz_academica_b4/20261016/manifest.json'],['Sectores','Valores preservados por Código Único desde el libro editado por Alexi.','data/diccionario_c1/20261016/fuente_usuario.xlsx'],['Fuentes y reproducción','Instantáneas gobernadas; consultar no reconstruye el análisis de alumnos.','docs/c1_edicion_diccionario_20261016.md'],['Datos posteriores','ANOMATRICULA posterior al año observado no acredita una regla histórica.','DATO_POSTERIOR_AL_CONTEXTO'],['Modelos','K0 base; K1 agrega período ingreso; K2 agrega año/período matrícula; K3 ambos.','No elegir un modelo distinto en cada caso para forzar un código.']];
guide.getRange('A51:C57').format.wrapText=true;guide.getRange('A51:C57').format.rowHeight=65;
const qa=[];
function setRule(r){const e=r.entrada;query.getRange('B7:B17').values=[r.modelo,e.codcarpr,e.sede,e.jornada,e.anio,e.ingreso_original,e.primera_observacion,e.planes.join('\n'),e.periodo_ingreso??'',e.anomatricula??'',e.periodo_matricula??''].map(x=>[x]);}
const tests=new Map();for(const r of p.rules){const k=r.modelo+'|'+r.estado;if(!tests.has(k))tests.set(k,r);}
for(const r of tests.values()){setRule(r);wb.recalculate();const actual=query.getRange('B20').values[0][0];if(actual!==r.estado)throw new Error('Consulta '+r.id+': '+actual);const codes=query.getRange('B21').values[0][0];if(codes!==r.codigos_construccion.join('\n'))throw new Error('Códigos '+r.id);qa.push({regla:r.id,estado:actual});}
const first=p.rules.find(r=>r.modelo==='K0'&&r.estado==='CORROBORADA_EN_RESERVA');setRule(first);v('B8','INEXISTENTE');wb.recalculate();if(query.getRange('B20').values[0][0]!=='SIN_REGLA_OBSERVADA')throw new Error('Desconocido');
v('B8','');wb.recalculate();if(query.getRange('B20').values[0][0]!=='ENTRADA_INCOMPLETA')throw new Error('Incompleto');setRule(first);wb.recalculate();
if(query.getRange('B35:B38').values.flat().join(',')!=='197,211,15,1')throw new Error('Resumen K0');
await fs.writeFile(path.join(base,'qa_formulas.json'),JSON.stringify({consultas:qa,fronteras:2,resumen_k0:[197,211,15,1]},null,2));
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},summary:'Errores C1'});await fs.writeFile(path.join(base,'errores.ndjson'),errors.ndjson);
for(const [name,range,file] of [['Consulta B5','A1:C26','consulta_b5.png'],['Consulta B5','A29:C38','resumen_b5.png'],...p.sheets.map(s=>[s.name,`A1:${col(Math.min(4,s.headers.length-1))}9`,s.name+'.png']),['Reglas B5','M5:Q10','estados_b5.png'],['Consulta','A58:C61','navegacion_c1.png'],['Guía','A51:C57','guia_c1.png'],['Diccionario SIES','R5:V9','sectores_c1.png']])await render(name,range,file);
const output=path.resolve(base,'../../../outputs/diccionario_c1_20261016/DICCIONARIO_CRUCE_SIES_UMAS_2007_2026_C1.xlsx');
await (await SpreadsheetFile.exportXlsx(wb)).save(output);
console.log(JSON.stringify({output,consultasProbadas:qa.length,errors:errors.ndjson}));
