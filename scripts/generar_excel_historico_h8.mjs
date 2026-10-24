/** Autoría H8 con Artifact Tool; consulta explícita y candidatos sin acreditar. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';

const [input,output,work]=process.argv.slice(2);
if(!input||!output||!work)throw new Error('Uso: builder libro.json salida.xlsx carpeta_qa');
const payload=JSON.parse(await fs.readFile(input,'utf8'));
const wb=Workbook.create(), query=wb.worksheets.add('Consulta');
const order=['Diccionario SIES','Ejemplos','Historia SIES','Planes UMAS','Programas UMAS','Candidatos','Claves UMAS','Guía'];
const metadata=new Map(payload.sheets.map(s=>[s.name,s]));
const col=n=>{let s='';for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const ink='#243746', navy='#173B55', amber='#FFF2CC', gray='#EEF2F5';
for(const name of order)wb.worksheets.add(name);
for(const [index,name] of order.entries()){
 const info=metadata.get(name),s=wb.worksheets.getItem(name),last=info.rows.length+5,end=col(info.headers.length-1);
 s.showGridLines=false;
 s.getRange(`A1:${end}${last}`).format={font:{name:'Arial',size:11,color:ink},verticalAlignment:'center',rowHeight:30};
 s.getRange('A2').values=[[info.title]];s.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:navy};
 s.getRange('A3').values=[[info.note]];s.getRange('A3').format.font={name:'Arial',size:11,italic:true,color:'#526778'};
 s.getRange(`A5:${end}5`).values=[info.headers];s.getRange(`A6:${end}${last}`).values=info.rows;
 s.getRange(`A5:${end}${last}`).format.wrapText=true;
 for(let i=0;i<info.headers.length;i++){
  const c=col(i);s.getRange(`${c}1:${c}${last}`).format.columnWidth=info.widths[i];
  const text=info.rows.every(row=>row[i]===null||row[i]===''||typeof row[i]==='string');
  const year=info.headers[i]==='Año'||info.headers[i].startsWith('Año ')||info.headers[i]==='Ámbito candidato';
  s.getRange(`${c}6:${c}${last}`).setNumberFormat(text?'@':year?'0':'#,##0');
  s.getRange(`${c}6:${c}${last}`).format.horizontalAlignment=text?'left':'right';
 }
 for(let i=0;i<info.rows.length;i++){
  const lines=Math.max(...info.rows[i].map((v,c)=>String(v??'').split('\n').reduce((n,l)=>n+Math.max(1,Math.ceil(l.length/Math.max(10,info.widths[c]-4))),0)));
  s.getRange(`A${i+6}:${end}${i+6}`).format.rowHeight=Math.min(390,Math.max(30,lines*14+8));
 }
 const t=s.tables.add(`A5:${end}${last}`,true,`HistoricoH8Tabla${index+1}`);t.style='TableStyleMedium2';t.showFilterButton=true;
 s.getRange(`A5:${end}5`).format={fill:navy,font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},rowHeight:48,wrapText:true,horizontalAlignment:'center'};
 s.freezePanes.freezeRows(5);s.freezePanes.freezeColumns(name==='Guía'?1:2);
}
wb.worksheets.getItem('Guía').tabColor='#83909B';query.tabColor=navy;
function ref(name,label){const m=metadata.get(name),i=m.headers.indexOf(label);if(i<0)throw new Error(label);return `'${name}'!$${col(i)}$6:$${col(i)}$${m.rows.length+5}`;}
function addMatches(name,sourceLabels,queryCells){
 const s=wb.worksheets.getItem(name),info=metadata.get(name),cols=[];
 for(let k=0;k<sourceLabels.length;k++){
  const c=col(info.headers.length+k),source=col(info.headers.indexOf(sourceLabels[k]));
  s.getRange(`${c}5`).values=[[k?'Posición contexto consultado':'Posición coincidencia consulta']];
  s.getRange(`${c}5`).format={fill:gray,font:{name:'Arial',size:11,color:ink,bold:true},wrapText:true,rowHeight:48};
  s.getRange(`${c}5:${c}${info.rows.length+5}`).format.columnWidth=25;
  s.getRange(`${c}6:${c}${info.rows.length+5}`).formulas=info.rows.map((_,i)=>[`=IF(EXACT(${source}${i+6},'Consulta'!${queryCells[k]}),${i+1},0)`]);
  s.getRange(`${c}6:${c}${info.rows.length+5}`).setNumberFormat('0');
  cols.push(`'${name}'!$${c}$6:$${c}$${info.rows.length+5}`);
 }
 return cols;
}
const matchD=addMatches('Diccionario SIES',['Código Único'],['$B$8'])[0];
const matchH=addMatches('Historia SIES',['Clave anual'],['$B$45'])[0];
const [matchU,matchContext]=addMatches('Claves UMAS',['Clave candidata','Clave contexto'],['$B$46','$B$47']);
const v=(a,x)=>query.getRange(a).values=[[x]], f=(a,x)=>query.getRange(a).formulas=[[x]];
query.showGridLines=false;
query.getRange('A1:C58').format={font:{name:'Arial',size:11,color:ink},verticalAlignment:'center',rowHeight:26};
query.getRange('A1:A58').format.columnWidth=34;query.getRange('B1:B58').format.columnWidth=76;query.getRange('C1:C58').format.columnWidth=26;
v('A2','Diccionario SIES y UMAS 2007–2026');query.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:navy};
v('A4','Edite las celdas amarillas. Los candidatos no acreditan una versión de malla.');
for(const [row,title] of [[6,'Consulta de oferta SIES'],[20,'Consulta de candidatos UMAS'],[44,'Claves y controles de búsqueda']]){
 v(`A${row}`,title);query.getRange(`A${row}:C${row}`).format={fill:gray,font:{bold:true,color:navy},rowHeight:30};
}
const labels={7:'Año de oferta',8:'Código Único',9:'Estado oferta',10:'Nombre en oferta del año',11:'Nombre oficial oferta 2026',12:'Jornada del año',13:'Modalidad del año',14:'Tipo de plan del año',15:'Versión SIES del año',16:'Sector IPSS referencia 2026',17:'Estado sector',18:'Registros MRUN del año',22:'Año de actividad UMAS',23:'Código carrera UMAS',24:'Nombre interno UMAS',25:'Plan UMAS',26:'Sede UMAS',27:'Jornada UMAS',28:'Período UMAS',29:'Régimen UMAS',31:'Estado equivalencia',32:'Motivo',33:'Código Único acreditado',34:'Códigos candidatos',35:'Destinos candidatos distintos',36:'Nombres oficiales 2026',37:'Asignación individual acreditada',38:'Reglas efectivas disponibles',40:'Alcance temporal',42:'Cobertura del diccionario',45:'Clave SIES año y código',46:'Clave candidata UMAS',47:'Contexto UMAS sin nombre',48:'Clave completa con período',50:'Coincidencias SIES anuales',51:'Posición SIES anual',52:'Posición Código Único',53:'Coincidencias clave candidata',54:'Posición clave candidata',55:'Coincidencias contexto UMAS',56:'Oferta disponible en año UMAS',57:'Entradas UMAS válidas'};
for(const [r,label] of Object.entries(labels))v(`A${r}`,label);
v('B7',2026);v('B8','I162S2C77J4V2');
const defaults=[2026,'CILOG','CONTINUIDAD INGENIERIA LOGISTICA','CILOG20241','RE','O','1','TRIMESTRAL'];
query.getRange('B22:B29').values=defaults.map(x=>[x]);
for(const range of ['B7:B8','B22:B29'])query.getRange(range).format={fill:amber,font:{bold:true,color:ink},borders:{preset:'outside',style:'thin',color:'#B79A4D'}};
query.getRange('B8').setNumberFormat('@');query.getRange('B23:B29').setNumberFormat('@');query.getRange('B7').setNumberFormat('0');query.getRange('B22').setNumberFormat('0');
for(const row of [7,22])f(`C${row}`,`=IF(ISNUMBER(B${row}),IF(B${row}=INT(B${row}),"OK","AÑO NO ENTERO"),"FALTA AÑO ENTERO")`);
for(const row of [8,23,24,25,26,27,28,29])f(`C${row}`,`=IF(OR(NOT(ISTEXT(B${row})),B${row}=""),"FALTA TEXTO",IF(OR(UPPER(B${row})="NULL",UPPER(B${row})="NONE",UPPER(B${row})="NAN"),"DATO FALTANTE",IF(OR(LEFT(B${row},1)=" ",RIGHT(B${row},1)=" "),"ESPACIO PERIFÉRICO","OK")))`);
const key=cells=>cells.map(c=>`LEN(${c})&":"&${c}`).join('&"|"&');
f('B45','='+key(['B7','B8']));f('B46','='+key(['B23','B25','B26','B27','B24']));
f('B47','='+key(['B23','B25','B26','B27']));f('B48','='+key(['B23','B25','B26','B27','B24','B22','B28','B29']));
f('B50',`=COUNTIFS(${matchH},">0")`);f('B51',`=SUM(${matchH})`);f('B52',`=SUM(${matchD})`);
f('B53',`=COUNTIFS(${matchU},">0")`);f('B54',`=SUM(${matchU})`);f('B55',`=COUNTIFS(${matchContext},">0")`);
f('B56',`=COUNTIFS(${ref('Historia SIES','Año')},B22,${ref('Historia SIES','Estado consulta')},"OFERTA_ANUAL_LOCALIZADA")`);
f('B57','=COUNTIFS(C22:C29,"OK")');
const lookup=(name,label,index)=>`INDEX(${ref(name,label)},${index})`;
const histGet=label=>`=IF(AND(C7="OK",C8="OK",B50=1),IF(${lookup('Historia SIES',label,'B51')}="","",${lookup('Historia SIES',label,'B51')}),"")`;
f('B9',`=IF(OR(C7<>"OK",C8<>"OK"),"ENTRADA_INCOMPLETA",IF(OR(B7<2007,B7>2026),"FUERA_AMBITO",IF(B50=1,${lookup('Historia SIES','Estado consulta','B51')},IF(B50>1,"ERROR_CLAVE_DUPLICADA","SIN_OFERTA_ANUAL"))))`);
for(const [row,label] of [[10,'Nombre anual oferta'],[12,'Jornada oferta'],[13,'Modalidad oferta'],[14,'Tipo plan oferta'],[15,'Versión SIES'],[18,'Registros MRUN']])f(`B${row}`,histGet(label));
for(const [row,label] of [[11,'Nombre oficial 2026'],[16,'Sector IPSS 2026'],[17,'Estado sector']])f(`B${row}`,`=IF(B52>0,IF(${lookup('Diccionario SIES',label,'B52')}="","",${lookup('Diccionario SIES',label,'B52')}),"")`);
f('B31',`=IF(B57<>8,"ENTRADA_INCOMPLETA",IF(OR(B22<2007,B22>2026),"FUERA_AMBITO",IF(B56=0,"SIN_OFERTA_ANUAL",IF(B22<>2026,"SIN_EQUIVALENCIA",IF(B53=1,${lookup('Claves UMAS','Estado H5','B54')},IF(B53>1,"ERROR_CLAVE_DUPLICADA","SIN_EQUIVALENCIA"))))))`);
f('B32',`=IF(B31="SIN_OFERTA_ANUAL",IF(B56=0,"SIN_COBERTURA_ANUAL","CODIGO_NO_OBSERVADO"),IF(AND(B31="SIN_EQUIVALENCIA",B22=2026,B53=0,B55>0),"NOMBRE_INTERNO_NO_COINCIDE",""))`);
f('B33','=""');
const candidateGet=label=>`=IF(AND(B57=8,B22=2026,B53=1),IF(${lookup('Claves UMAS',label,'B54')}="","",${lookup('Claves UMAS',label,'B54')}),"")`;
f('B34',candidateGet('Códigos candidatos'));f('B36',candidateGet('Nombres oficiales 2026'));
f('B35',`=IF(OR(B57<>8,B22<2007,B22>2026),"",IF(AND(B22=2026,B53=1),${lookup('Claves UMAS','Destinos distintos','B54')},0))`);
v('B37','No');v('B38',0);v('B40','Los candidatos corresponden a 2026. Período y régimen no tienen equivalencias temporales acreditadas.');
v('B42','141 códigos SIES y 236 planes UMAS. Consulte las tablas para ver los casos sin actividad.');
query.getRange('B9:B57').format.wrapText=true;
for(const row of [10,11,24,34,36,40,42,46,48])query.getRange(`A${row}:C${row}`).format.rowHeight=[34,46,48].includes(row)?66:44;
query.getRange('A45:C57').format.font={name:'Arial',size:11,color:'#526778'};
query.getRange('C7:C29').conditionalFormats.add('containsText',{text:'FALTA',format:{fill:'#FCE6E2',font:{color:'#9C3026'}}});
query.getRange('B31').conditionalFormats.add('containsText',{text:'PENDIENTE',format:{fill:'#FFF2CC',font:{bold:true,color:'#6B5100'}}});
query.getRange('B31').conditionalFormats.add('containsText',{text:'INCOMPLETA',format:{fill:'#FCE6E2',font:{color:'#9C3026'}}});

await fs.mkdir(work,{recursive:true});
const qa=[];
function check(cell,expected,label){const actual=query.getRange(cell).values[0][0];if(actual!==expected)throw new Error(`${label}: ${cell} ${JSON.stringify(actual)} != ${JSON.stringify(expected)}`);qa.push({label,cell,actual,expected});}
// Representative tests cover every distinct state/motive and the requested careers.
const selected=new Map();
for(const test of payload.tests_umas){const p=test.params;const id=[test.estado,test.motivo,test.candidatos.length,p.anio,p.codcarpr==='CILOG'?'CILOG':p.codcarpr==='ILOG'?'ILOG':p.codcarpr==='NATP'?'NATP':'general'].join('|');if(!selected.has(id))selected.set(id,test);}
for(const test of payload.tests_umas.slice(-10))selected.set(JSON.stringify(test.params),test);
for(const test of selected.values()){
 const p=test.params;query.getRange('B22:B29').values=[p.anio,p.codcarpr,p.nombre_interno,p.plan_umas,p.sede_umas,p.jornada_umas,p.periodo,p.regimen].map(x=>[x]);wb.recalculate();
 check('B31',test.estado,`Estado ${p.plan_umas} ${p.anio}`);check('B32',test.motivo,'Motivo H7');
 check('B34',test.candidatos.join('\n'),'Candidatos H7');check('B33','','Sin código acreditado');
}
const siesSelected=new Map();
for(const test of payload.tests_sies){const id=[test.anio,test.estado_consulta,test.presencia].join('|');if(!siesSelected.has(id))siesSelected.set(id,test);}
for(const test of siesSelected.values()){
 query.getRange('B7:B8').values=[[Number(test.anio)],[test.codigo_unico]];wb.recalculate();
 check('B9',test.estado_consulta,'Estado SIES');check('B10',test.nombre_anual_oferta,'Nombre anual literal');
 check('B13',test.modalidad_oferta,'Modalidad literal');
}
v('B8','INEXISTENTE');wb.recalculate();check('B9','SIN_OFERTA_ANUAL','Código desconocido');
v('B7',2027);wb.recalculate();check('B9','FUERA_AMBITO','SIES fuera de ámbito');
v('B7','2026');v('B8','I162S2C77J4V2');wb.recalculate();check('B9','ENTRADA_INCOMPLETA','Año texto no entero');check('B10','','Sin resultado anual con año inválido');
query.getRange('B22:B29').values=defaults.map(x=>[x]);v('B24',' CONTINUIDAD INGENIERIA LOGISTICA');wb.recalculate();check('B31','ENTRADA_INCOMPLETA','Espacio periférico visible');check('B34','','No completar entrada inválida');
v('B7',2026);v('B8','I162S2C77J4V2');query.getRange('B22:B29').values=defaults.map(x=>[x]);wb.recalculate();
check('B11','INGENIERIA EN LOGISTICA','Nombre oficial sin descriptor');check('B31','PENDIENTE_EVIDENCIA','Continuidad al abrir');
for(const info of payload.sheets){const actual=wb.worksheets.getItem(info.name).getRange(`A6:${col(info.headers.length-1)}${info.rows.length+5}`).values;if(JSON.stringify(actual)!==JSON.stringify(info.rows))throw new Error('Datos alterados: '+info.name);}
await fs.writeFile(path.join(work,'qa_formulas.json'),JSON.stringify({casos_umas:selected.size,casos_sies:siesSelected.size,aserciones:qa.length,resultados:qa},null,2));
const inspect=await wb.inspect({kind:'table',range:'Consulta!A22:C38',include:'values,formulas',maxChars:6000,tableMaxRows:17,tableMaxCols:3});await fs.writeFile(path.join(work,'consulta.ndjson'),inspect.ndjson);
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:50},summary:'Errores finales'});await fs.writeFile(path.join(work,'errores.ndjson'),errors.ndjson);
for(const [name,range] of (process.env.H8_SKIP_RENDER==='1'?[]:[['Consulta','A1:C42'],...order.map(name=>[name,`A1:${col(Math.min(metadata.get(name).headers.length-1,4))}9`])])){
 const blob=await wb.render({sheetName:name,range,scale:1,format:'png'});await fs.writeFile(path.join(work,name+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
if(process.env.H8_SKIP_RENDER!=='1'){
 const blob=await wb.render({sheetName:'Historia SIES',range:'S5:Y9',scale:1,format:'png'});
 await fs.writeFile(path.join(work,'Historia MRUN.png'),new Uint8Array(await blob.arrayBuffer()));
}
await fs.mkdir(path.dirname(output),{recursive:true});const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(output);
console.log(JSON.stringify({output,hojas:order.length+1,casos_umas:selected.size,casos_sies:siesSelected.size,aserciones:qa.length,errors:errors.ndjson}));
