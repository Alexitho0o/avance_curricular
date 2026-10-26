import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const dir=process.argv[2],t=JSON.parse(await fs.readFile(dir+'/TABLAS_SEGUIMIENTO.json','utf8'));
const wb=Workbook.create(),names=['52_Codigos_SIES_Revision','53_Codigos_T1_Confirmados','54_Contextos_y_Pendientes'];
const [s,o,c]=names.map(n=>wb.worksheets.add(n)),forms=[];
// Temporary read-only source supplies the inherited numerator during recalculation.
// Register before writing cross-sheet formulas; it is never grafted into the final book.
const stub=wb.worksheets.add('18_Foto_Intertrimestral');stub.getRange('E8').values=[[600]];
const navy='#102B42',blue='#174977',grey='#F2F2F2';
function style(sh,last,end,title,note){
 sh.showGridLines=false;sh.freezePanes.freezeRows(5);sh.tabColor='#CFB47C';
 sh.getRange(`A1:${last}${end}`).format.font.name='Arial';sh.getRange(`A1:${last}${end}`).format.font.size=10;
 sh.getRange(`A1:${last}${end}`).format.font.color='#263B49';sh.getRange(`A1:${last}${end}`).format.wrapText=true;sh.getRange(`A1:${last}${end}`).format.rowHeight=42;
 sh.getRange(`A:${last}`).format.columnWidth=22;sh.getRange(`A1:${last}3`).merge();sh.getRange('A1').values=[[title+'\n'+note]];
 const h=sh.getRange(`A1:${last}3`);h.format.fill=navy;h.format.font.color='#FFFFFF';h.format.font.bold=true;h.format.font.size=12;h.format.rowHeight=26;
}
function head(sh,row,last){let h=sh.getRange(`A${row}:${last}${row}`);h.format.fill=blue;h.format.font.color='#FFFFFF';h.format.font.bold=true;h.format.rowHeight=48;}
function formula(sh,cell,f){sh.getRange(cell).formulas=[[f]];forms.push({sheet:sh.name,cell,formula:f});}
function note(row,text){s.getRange(`A${row}:I${row}`).merge();s.getRange(`A${row}`).values=[[text]];s.getRange(`A${row}:I${row}`).format.fill=grey;s.getRange(`A${row}:I${row}`).format.rowHeight=43;}
const on=t.origen_periodo.length+5,cn=t.contextos.length+5;
style(o,'M',on,'53 · Seguimiento por código SIES de origen T1','B/C · Un grupo por código T1 y período. El código de origen se conserva aunque después cambie carrera, jornada o plan. E · Sin contexto no significa deserción.');
o.getRange(`A5:M${on}`).values=[['Año cohorte T1','Año observado','Período nativo','Carrera de origen T1','Código SIES de origen T1','Estudiantes de origen','Numerador existente','Denominador de la tasa','Resultado existente','Fuente y alcance','Sin contexto en diccionario','Origen multiversión','Con contexto en diccionario'],...t.origen_periodo];
o.getRange('A:C').format.columnWidth=14;o.getRange('D:D').format.columnWidth=42;o.getRange('E:E').format.columnWidth=25;o.getRange('F:I').format.columnWidth=19;o.getRange('J:J').format.columnWidth=51;o.getRange('K:M').format.columnWidth=23;
const ot=o.tables.add(`A5:M${on}`,true,'RevisionCodigosOrigenT1');ot.style='TableStyleMedium2';ot.showFilterButton=true;head(o,5,'M');
for(let r=6;r<=on;r++){formula(o,`I${r}`,`=IF(ISNUMBER(G${r}),IF(H${r}>0,G${r}/H${r},"No aplica"),"Pendiente")`);if(t.origen_periodo[r-6][6]==='Pendiente')o.getRange(`G${r}:I${r}`).format.fill='#FFF2CC';}
o.getRange(`F6:H${on}`).setNumberFormat('#,##0');o.getRange(`I6:I${on}`).setNumberFormat('0.00%');
style(c,'O',cn,'54 · Código de origen y excepciones por período','B/C · Código documental anual atribuido. D · Correspondencia interna ya aprobada. E · Versión o atribución pendiente. Una observación es un expediente/plan/período; no equivale a una persona adicional ni a matrícula vigente.');
c.getRange(`A5:O${cn}`).values=[['Año cohorte T1','Año observado','Período nativo','Carrera de origen T1','Carrera UMAS observada','Plan observado','Código SIES de origen T1','Código del contexto','Respaldo del contexto','Relación o excepción','Comparación de plan','Contraste de dimensiones','Origen multiversión','Observaciones','Pendiente o límite'],...t.contextos];
c.getRange('A:C').format.columnWidth=14;c.getRange('D:D').format.columnWidth=40;c.getRange('E:I').format.columnWidth=25;c.getRange('J:L').format.columnWidth=45;c.getRange('M:N').format.columnWidth=17;c.getRange('O:O').format.columnWidth=55;c.getRange(`A6:O${cn}`).format.rowHeight=58;c.getRange(`N6:N${cn}`).setNumberFormat('#,##0');
const ct=c.tables.add(`A5:O${cn}`,true,'RevisionVersionesContexto');ct.style='TableStyleMedium2';ct.showFilterButton=true;head(c,5,'O');
for(let r=6;r<=cn;r++){let st=t.contextos[r-6][8];if(st==='E Pendiente')c.getRange(`H${r}:J${r}`).format.fill='#FFF2CC';else if(st==='D Interno aprobado')c.getRange(`H${r}:J${r}`).format.fill='#DDEBF7';}
style(s,'I',50,'52 · Seguimiento de T1 en T2 y T3 hasta 2026','C/D · Se reutiliza el código T1 documentado. Bases, población, numeradores y denominadores existentes se conservan. Este resumen separa seguimiento académico de revisión del código SIES.');
s.getRange('A:C').format.columnWidth=15;s.getRange('D:G').format.columnWidth=21;s.getRange('H:H').format.columnWidth=35;s.getRange('I:I').format.columnWidth=50;
s.getRange('A5:I5').values=[['Cohorte T1','Año observado','Período','Estudiantes de origen','Numerador existente','Denominador de la tasa','Resultado existente','Tipo de evidencia','Estado / fuente original']];head(s,5,'I');
let rr=6;
for(const sum of t.resumen)for(const p of [2,3]){
 let y=sum.cohorte_T1,yy=Number(sum[`periodo_T${p}`].split('-')[0]),r=rr++,photo=y>2024&&p===3,prior=y===2024?7:y===2025?8:11;
 s.getRange(`A${r}:I${r}`).values=[[y,yy,p,null,null,null,null,photo?'B/C · Foto de matrícula T3':'C/E · Proxy de actividad y estado',y===2025&&p===2?'E · Desglose por código pendiente; total conservado de hoja 18 E8':`B/C · Conciliado con hoja 18 ${p===2?'E':'G'}${prior}`]];
 for(const [out,col]of [['D','F'],['E','G'],['F','H']])formula(s,`${out}${r}`,y===2025&&p===2&&out==='E'?"='18_Foto_Intertrimestral'!E8":`=SUMIFS('53_Codigos_T1_Confirmados'!$${col}$6:$${col}$${on},'53_Codigos_T1_Confirmados'!$A$6:$A$${on},A${r},'53_Codigos_T1_Confirmados'!$C$6:$C$${on},C${r})`);
 formula(s,`G${r}`,`=IF(F${r}>0,E${r}/F${r},"Pendiente")`);if(r%2===0)s.getRange(`A${r}:I${r}`).format.fill=grey;
}
s.getRange('D6:F11').setNumberFormat('#,##0');s.getRange('G6:G11').setNumberFormat('0.00%');s.getRange('I8').format.fill='#FFF2CC';
note(13,'Cómo leer: la tasa total es numerador ÷ denominador; no promedie porcentajes por carrera. La fila 2024 conserva el seguimiento en 2025. En 2026-T3 hay 1.471 integrantes y 1.467 incluidos en la tasa, según la regla heredada.');
note(14,'E · El proxy usa actividad y estado académico del extracto PROMEDIOS; no acredita vigencia histórica al cierre. T2-2025 conserva 600/1.150: la reproducción con documentos R y P obtiene 611. Falta justificar los 11 de diferencia antes de desglosar ese total.');
s.getRange('A16:I16').values=[['Cohorte T1','Año observado','Período nativo','Con contexto','Sin contexto localizado','Código documental anual','Código interno aprobado','Código pendiente','Total observaciones']];head(s,16,'I');
for(let i=0;i<6;i++){
 let r=17+i,src=6+i;for(const col of 'ABC')formula(s,`${col}${r}`,`=${col}${src}`);
 for(const [out,col]of [['D','M'],['E','K']])formula(s,`${out}${r}`,`=SUMIFS('53_Codigos_T1_Confirmados'!$${col}$6:$${col}$${on},'53_Codigos_T1_Confirmados'!$A$6:$A$${on},A${r},'53_Codigos_T1_Confirmados'!$C$6:$C$${on},C${r})`);
 for(const [out,st]of [['F','B/C Documental anual'],['G','D Interno aprobado'],['H','E Pendiente']])formula(s,`${out}${r}`,`=SUMIFS('54_Contextos_y_Pendientes'!$N$6:$N$${cn},'54_Contextos_y_Pendientes'!$A$6:$A$${cn},A${r},'54_Contextos_y_Pendientes'!$C$6:$C$${cn},C${r},'54_Contextos_y_Pendientes'!$I$6:$I$${cn},"${st}")`);
 formula(s,`I${r}`,`=SUM(F${r}:H${r})`);if(i%2===0)s.getRange(`A${r}:I${r}`).format.fill=grey;
}
s.getRange('A24:C24').merge();s.getRange('A24').values=[['C · Total registros origen×período / observaciones']];for(const col of 'DEFGHI')formula(s,`${col}24`,`=SUM(${col}17:${col}22)`);s.getRange('A24:I24').format.fill='#DDEBF7';s.getRange('D17:I24').setNumberFormat('#,##0');
note(26,'Los 3.179 registros T1 conservan su código documentado (558 de 2024; 1.150 de 2025; 1.471 de 2026). Los controles anteriores cuentan 6.358 registros origen×período y 2.854 observaciones: no son personas únicas ni tasas de retención.');
note(27,'B/C/D/E · En los períodos consultados: 2.713 contextos conservan el código T1, 37 tienen un código distinto respaldado y 104 siguen pendientes. No se adjudicó ninguna versión nueva. Las 13 correspondencias internas conservan su atribución documental pendiente.');
note(28,'B/C/D/E · Foco de carreras multiversión: 1.077 contextos, de los cuales 1.040 tienen código documental anual, 13 correspondencia interna aprobada y 24 quedan pendientes. La condición multiversión conserva la bandera de V12; no se cambió su definición.');
note(29,'Para revisar solo excepciones, abra la hoja 54 y filtre «Relación o excepción»; para concentrarse en carreras con varias versiones, filtre «Origen multiversión» = Sí. El código de origen nunca se sustituye por un candidato ni se usa el pendiente como causa de deserción.');
note(30,'B/C · 2.828 contextos muestran el mismo plan que el contexto nativo 1 del año de origen; en 26 no se localizó ese contexto del mismo expediente. Esto no acredita una fecha de migración. El período nativo de PROMEDIOS no equivale automáticamente a una foto de cierre.');
note(32,'C · Esta edición consulta el diccionario v7 y limita la revisión a los períodos 2 y 3 del calendario indicado. V12 revisaba el mismo año de origen y todos los períodos: sus pendientes no son directamente comparables. Las hojas 1–51 y sus 13 gráficos se conservan exactamente.');
note(33,'Fuentes y reproducción: MANIFEST_SEGUIMIENTO.json, INDICADORES_AGREGADOS.json y QA_EXCEL.json junto al libro. A = oficial; B = observado; C = cálculo; D = decisión interna; E = pendiente. Este resumen no declara aceptación individual SIES.');
wb.recalculate();await(await SpreadsheetFile.exportXlsx(wb)).save(dir+'/SUPLEMENTO_QA.xlsx');
await fs.writeFile(dir+'/FORMULAS.json',JSON.stringify(forms,null,2));
for(const [name,range,file]of [[names[0],'A1:I14','resumen'],[names[0],'A16:I33','controles'],[names[1],'A1:M11','origen'],[names[2],'G1:O11','excepciones']]){
 await fs.writeFile(dir+'/preview_'+file+'.png',new Uint8Array(await(await wb.render({sheetName:name,range,scale:1.2,format:'png'})).arrayBuffer()));
}
console.log(JSON.stringify({filas_origen_periodo:t.origen_periodo.length,grupos_contexto:t.contextos.length,formulas:forms.length}));
