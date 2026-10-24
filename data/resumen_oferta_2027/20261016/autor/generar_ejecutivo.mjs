import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile,Workbook} from '@oai/artifact-tool';
process.on('uncaughtException',error=>{console.error(error.stack);process.exit(1);});
const base=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..');
if(process.argv.includes('--help-position')){
 const w=Workbook.create();
 console.log(w.help('worksheet',{search:'position|activate|index|move',include:'index,notes,examples',maxChars:5000}).ndjson);
 process.exit(0);
}
const p=JSON.parse(await fs.readFile(path.join(base,'libro.json'),'utf8'));
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(p.source));
async function render(sheetName,range,file){const b=await wb.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(path.join(base,file),new Uint8Array(await b.arrayBuffer()));}
if(process.argv.includes('--preview')){await render('Cierre D4','A1:C18','antes_d4.png');process.exit(0);}
const navy='#173B55',teal='#147D92',orange='#CC741D',ink='#243746';
const col=n=>{let s='';for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const q=wb.worksheets.add('Resumen ejecutivo');
for(const [idx,info] of p.sheets.entries()){
 const s=wb.worksheets.add(info.name),n=info.rows.length+5,end=col(info.headers.length-1);
 s.showGridLines=false;s.getRange(`A1:${end}${n}`).format={font:{name:'Arial',size:11,color:ink},rowHeight:36,verticalAlignment:'center'};
 s.getRange('A2').values=[[info.name]];s.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:navy};s.getRange('A3').values=[[info.note]];
 s.getRange(`A5:${end}5`).values=[info.headers];s.getRange(`A6:${end}${n}`).values=info.rows;
 s.tables.add(`A5:${end}${n}`,true,`EjecutivoTabla${idx+1}`).style='TableStyleMedium2';
 s.getRange(`A5:${end}5`).format={fill:navy,font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},rowHeight:64,wrapText:true,horizontalAlignment:'center'};
 s.getRange(`A6:${end}${n}`).format.wrapText=true;
 info.headers.forEach((h,j)=>{s.getRange(`${col(j)}1:${col(j)}${n}`).format.columnWidth=info.widths[j];s.getRange(`${col(j)}6:${col(j)}${n}`).setNumberFormat(info.rows.every(r=>r[j]===null||typeof r[j]==='string')?'@':'0');});
 for(let i=0;i<info.rows.length;i++){const ln=Math.max(...info.rows[i].map((v,j)=>String(v??'').split('\n').reduce((a,t)=>a+Math.max(1,Math.ceil(t.length/(info.widths[j]-4))),0)));s.getRange(`A${i+6}:${end}${i+6}`).format.rowHeight=Math.max(36,Math.min(400,ln*16+10));}
 s.freezePanes.freezeRows(5);s.freezePanes.freezeColumns(2);
}
const of=wb.worksheets.getItem('Preparación oferta 2027'),um=wb.worksheets.getItem('Preparación UMAS 2027');
of.getRange('Q6:Q166').format.fill='#FFF2CC';of.getRange('T6:W166').format.fill='#FFF2CC';
um.getRange('K6:O77').format.fill='#FFF2CC';um.getRange('Q6:Q77').format.fill='#FFF2CC';
of.getRange('Z5').values=[['Código confirmado distinto']];of.getRange('Z5:Z166').format.columnWidth=28;
of.getRange('Z6:Z166').formulas=p.sheets[1].rows.map((_,i)=>[`=IF(Q${i+6}="",0,IF(COUNTIF($Q$6:Q${i+6},Q${i+6})=1,1,0))`]);
um.getRange('R5').values=[['Plan confirmado distinto']];um.getRange('R5:R77').format.columnWidth=28;
um.getRange('R6:R77').formulas=p.sheets[2].rows.map((_,i)=>[`=IF(L${i+6}="",0,IF(COUNTIF($L$6:L${i+6},L${i+6})=1,1,0))`]);
q.showGridLines=false;q.tabColor=navy;
q.getRange('A1:M39').format={font:{name:'Arial',size:11,color:ink},rowHeight:26,verticalAlignment:'center',wrapText:true};
for(const [c,w] of [['A',10],['B',15],['C',18],['D',16],['E',16],['F',16],['G',17],['H',12],['I',12],['J',12],['K',12],['L',12],['M',12]])q.getRange(`${c}1:${c}39`).format.columnWidth=w;
const value=(a,x)=>q.getRange(a).values=[[x]],formula=(a,x)=>q.getRange(a).formulas=[[x]],merge=(a)=>q.getRange(a).merge();
merge('A1:M2');value('A1','Oferta SIES · evolución anual y preparación 2027');q.getRange('A1:M2').format={fill:navy,font:{name:'Arial',size:20,bold:true,color:'#FFFFFF'}};
merge('A3:M3');value('A3','Instituto Profesional San Sebastián · 2027 es una proyección del reporte 6047; Código Único definitivo pendiente.');
for(const [range,label] of [['A5:C5','Oferta publicada 2026'],['D5:F5','Oferta esperada 2027'],['G5:I5','Aumento esperado'],['J5:M5','Mallas UMAS 2027']]){merge(range);value(range.split(':')[0],label);q.getRange(range).format={fill:'#E7EFF4',font:{name:'Arial',size:11,bold:true,color:navy}};}
for(const range of ['A6:C7','D6:F7','G6:I7','J6:M7']){merge(range);q.getRange(range).format={font:{name:'Arial',size:24,bold:true,color:navy},fill:'#F2F6F9',horizontalAlignment:'center'};}
const n=p.sheets[0].rows.length+5,series="'Serie oferta'";
formula('A6',`=COUNTIFS(${series}!$A$6:$A$${n},2026)`);
formula('D6',`=COUNTIFS(${series}!$A$6:$A$${n},2027)`);
formula('G6','=D6-A6');q.getRange('G6:I7').setNumberFormat('+0;-0;0');
formula('J6',`=IF(SUM('Preparación UMAS 2027'!R6:R77)=0,"Por confirmar",SUM('Preparación UMAS 2027'!R6:R77))`);
merge('A8:C8');value('A8','Incluye pregrado y diplomados');merge('D8:F8');value('D8','Claves compuestas, no definitivas');merge('G8:I8');formula('G8','=G6/A6');q.getRange('G8:I8').setNumberFormat('0.0%');merge('J8:M8');value('J8','El extracto no contiene CODPESTUD');
q.getRange('A10:G10').values=[['Año','Total oferta','Primera aparición¹','Entradas²','Ausencias²','Cambio neto','Variación %']];
q.getRange('A10:G10').format={fill:navy,font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:52};
for(const [i,m] of p.metrics.entries()){
 const row=11+i,y=m[0];value('A'+row,y);
 if(y<2010){value('B'+row,'Sin cobertura');q.getRange(`A${row}:G${row}`).format.fill='#EEF0F2';continue;}
 formula('B'+row,`=COUNTIFS(${series}!$A$6:$A$${n},A${row})`);
 if(y>2010){formula('C'+row,`=SUMIFS(${series}!$N$6:$N$${n},${series}!$A$6:$A$${n},A${row})`);formula('D'+row,`=SUMIFS(${series}!$O$6:$O$${n},${series}!$A$6:$A$${n},A${row})`);formula('E'+row,`=SUMIFS(${series}!$Q$6:$Q$${n},${series}!$A$6:$A$${n},A${row}-1)`);formula('F'+row,`=B${row}-B${row-1}`);formula('G'+row,`=F${row}/B${row-1}`);}
 else value('C'+row,'Base observada');
 q.getRange(`B${row}:F${row}`).setNumberFormat('0');q.getRange(`G${row}`).setNumberFormat('0.0%');
 if(y==2027){q.getRange(`A${row}:G${row}`).format={fill:'#FFF0D9',font:{name:'Arial',size:11,bold:true,color:'#8C4A0C'}};}
 else if(i%2===0)q.getRange(`A${row}:G${row}`).format.fill='#F0F5F8';
}
const chart=q.charts.add('bar',{barOptions:{direction:'column',grouping:'clustered'},hasLegend:false});
chart.setData(q.getRange('A14:B31'));
chart.setPosition('H10','M23');chart.title='Códigos por año · 2027 esperado';chart.series.items[0].fill=teal;
chart.series.items[0].name='Oferta observada / 2027 esperado';
chart.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:9}};chart.yAxis={numberFormatCode:'0',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};
merge('H24:M24');value('H24','2027 esperado · composición y planes');q.getRange('H24:M24').format={fill:navy,font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'}};
const side=[['Pregrado regular',`=COUNTIFS('Preparación oferta 2027'!C6:C166,"Pregrado",'Preparación oferta 2027'!J6:J166,"Plan Regular")`],['Pregrado continuidad',`=COUNTIFS('Preparación oferta 2027'!C6:C166,"Pregrado",'Preparación oferta 2027'!J6:J166,"Plan Regular de Continuidad")`],['Diplomados',`=COUNTIFS('Preparación oferta 2027'!C6:C166,"Postítulo")`],['Planes UMAS históricos',`=COUNTA('Planes D3'!A6:A241)`],['Códigos 2027 confirmados',`=SUM('Preparación oferta 2027'!Z6:Z166)`],['Mallas 2027 documentadas',`=SUM('Preparación UMAS 2027'!R6:R77)`]];
side.forEach(([label,f],i)=>{const row=25+i;merge(`H${row}:L${row}`);value('H'+row,label);formula('M'+row,f);});
merge('H31:M31');value('H31','67 códigos UMAS · 72 combinaciones · 346 registros');q.getRange('H31:M31').format.rowHeight=34;
const notes=[['A33:M33','Proyección: pregrado 103 → 140 (+37; +35,9 %). Diplomados 21 → 21. No se suman mallas a códigos SIES.'],['A34:M34','¹ Primera aparición en la fuente disponible. 2010 es base; 2007–2009 no tienen cobertura de oferta.'],['A35:M35','² Entradas y ausencias respecto del año anterior. Una ausencia no acredita cierre; cambio neto = entradas − ausencias.'],['A36:M36','2027: las 37 claves adicionales son nuevas frente a toda la oferta observada 2010–2026. Confirmación definitiva pendiente.'],['A37:M37','Completar columnas amarillas en Preparación oferta 2027 y Preparación UMAS 2027 con su respaldo. No inferir malla desde año de matrícula.'],['A38:M38','Las hojas anteriores conservan su edición D4. «Resuelto» en el catálogo previo no significa Código Único 2027 confirmado.'],['A39:M39','Fuentes y detalle: Serie oferta; reporte 6047; auditoría 12023 2027 P1; Planes D3. Método y huellas gobernados en el proyecto.']];
notes.forEach(([r,t])=>{merge(r);value(r.split(':')[0],t);q.getRange(r).format.rowHeight=30;});
q.freezePanes.freezeRows(10);
wb.recalculate();
const checks={total2026:q.getRange('A6').values[0][0],esperado2027:q.getRange('D6').values[0][0],delta:q.getRange('G6').values[0][0],planes:q.getRange('J6').values[0][0],composicion:q.getRange('M25:M30').values.flat()};
if(JSON.stringify(checks)!==JSON.stringify({total2026:124,esperado2027:161,delta:37,planes:'Por confirmar',composicion:[118,22,21,236,0,0]}))throw Error(JSON.stringify(checks));
for(let i=3;i<p.metrics.length;i++){const m=p.metrics[i],a=q.getRange(`B${11+i}:G${11+i}`).values[0];if(a[0]!==m[1])throw Error('Total anual '+m[0]);if(i>3)for(let j=1;j<6;j++)if(Math.abs(a[j]-m[j+1])>1e-10)throw Error('Métrica anual '+m[0]);}
// Probar entradas, duplicados y limpieza de columnas preparadas, sin conservar datos ficticios.
um.getRange('L6:L7').values=[['PRUEBA_QA'],['PRUEBA_QA']];of.getRange('Q6:Q7').values=[['PRUEBA_QA'],['PRUEBA_QA']];wb.recalculate();
if(q.getRange('M29').values[0][0]!==1||q.getRange('M30').values[0][0]!==1)throw Error('Conteo distinto');
um.getRange('L6:L7').clear({applyTo:'contents'});of.getRange('Q6:Q7').clear({applyTo:'contents'});wb.recalculate();
if(q.getRange('M29').values[0][0]!==0||q.getRange('J6').values[0][0]!=='Por confirmar')throw Error('Restauración');
await fs.writeFile(path.join(base,'qa_formulas.json'),JSON.stringify({checks,serie_anual_verificada:18,contadores_distintos_probados:true,entradas_2027_finales_vacias:true},null,2));
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},summary:'Errores ejecutivo'});await fs.writeFile(path.join(base,'errores.ndjson'),errors.ndjson);
for(const [s,r,f] of [['Resumen ejecutivo','A1:M39','resumen.png'],['Resumen ejecutivo','H10:M31','grafico_planes.png'],['Serie oferta','A5:F10','serie.png'],['Preparación oferta 2027','A5:J9','oferta.png'],['Preparación oferta 2027','N5:Y9','columnas_oferta.png'],['Preparación UMAS 2027','A5:J9','umas.png'],['Preparación UMAS 2027','K5:R9','columnas_umas.png']])await render(s,r,f);
await fs.mkdir(path.dirname(p.output),{recursive:true});await (await SpreadsheetFile.exportXlsx(wb)).save(p.output);
console.log(JSON.stringify({output:p.output,checks,errors:errors.ndjson}));
