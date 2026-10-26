import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const dir=process.argv[2],t=JSON.parse(await fs.readFile(dir+'/tablas.json','utf8')),res=JSON.parse(await fs.readFile(dir+'/RESULTADOS.json','utf8'));
const wb=Workbook.create(),names=['52_Codigos_SIES_Revision','53_Codigos_T1_Confirmados','54_Contextos_y_Pendientes'];
const sheets=names.map(n=>wb.worksheets.add(n)),forms=[];
const navy='#102B42',blue='#174977',muted='#F2F2F2',gold='#CFB47C';
function base(s,last,title,note,reading){
 s.showGridLines=false;s.freezePanes.freezeRows(5);s.tabColor=gold;
 s.getRange(`A1:${last}3`).merge();s.getRange('A1').values=[[title+'\n'+note+'\n'+reading]];
 const h=s.getRange(`A1:${last}3`);h.format.fill=navy;h.format.font.color='#FFFFFF';h.format.font.bold=true;h.format.font.size=12;h.format.wrapText=true;h.format.rowHeight=24;
}
function header(s,r,last){const z=s.getRange(`A${r}:${last}${r}`);z.format.fill=blue;z.format.font.color='#FFFFFF';z.format.font.bold=true;z.format.wrapText=true;z.format.rowHeight=44;}
function body(s,last,end){let z=s.getRange(`A4:${last}${end}`);z.format.font.name='Arial';z.format.font.size=10;z.format.font.color='#263B49';z.format.wrapText=true;z.format.rowHeight=37;s.getRange(`A:${last}`).format.columnWidth=21;}
function fx(s,cell,f){s.getRange(cell).formulas=[[f]];forms.push({sheet:s.name,cell,formula:f});}
const o=sheets[1],c=sheets[2],summary=sheets[0],on=t.origenes.length+5,cn=t.contextos.length+5;
body(o,'I',on);base(o,'I','53 · Código SIES de origen: grupos MU/T1','B/C · Código comprobado contra MU. Una fila agrupa estudiantes del mismo año, carrera y código.','Este código identifica la cohorte seguida. No se reemplaza por la versión de otro plan o período.');
o.getRange(`A5:I${on}`).values=[['Año MU','Carrera T1','Familia SIES','Código SIES T1 confirmado','Varias versiones en evidencias','Estudiantes T1','Con contexto en diccionario','Sin contexto localizado','Clasificación'],...t.origenes];
o.getRange('B:B').format.columnWidth=44;o.getRange('D:D').format.columnWidth=26;o.getRange(`F6:H${on}`).setNumberFormat('#,##0');
const ot=o.tables.add(`A5:I${on}`,true,'RevisionCodigosOrigenT1');ot.style='TableStyleMedium2';ot.showFilterButton=true;header(o,5,'I');
body(c,'O',cn);base(c,'O','54 · Versiones documentadas, internas y pendientes','B/C · Contextos del diccionario para las personas T1, en el mismo año. No son estudiantes adicionales.','El período es el valor nativo de PROMEDIOS; no se equipara automáticamente a T2/T3. La presencia de CODCLI en la foto T3 se informa aparte.');
c.getRange(`A5:O${cn}`).values=[['Año observado','Período nativo','Carrera T1','Carrera UMAS expediente','Plan observado','Familia SIES origen','Origen con varias versiones','Código cohorte T1','Código contexto adoptado','Respaldo','Expediente observado foto T3','Relación con familia T1','Observaciones','Candidatos NO adoptados','Pendiente o límite'],...t.contextos];
c.getRange('A:B').format.columnWidth=13;c.getRange('C:C').format.columnWidth=40;c.getRange('D:I').format.columnWidth=23;c.getRange('J:L').format.columnWidth=27;c.getRange('M:M').format.columnWidth=15;c.getRange('N:O').format.columnWidth=53;c.getRange(`M6:M${cn}`).setNumberFormat('#,##0');c.getRange(`A6:O${cn}`).format.rowHeight=48;
const ct=c.tables.add(`A5:O${cn}`,true,'RevisionVersionesContexto');ct.style='TableStyleMedium2';ct.showFilterButton=true;header(c,5,'O');
for(let n=0;n<t.contextos.length;n++){const r=n+6,st=t.contextos[n][9];if(st==='E Pendiente'){c.getRange(`I${r}:J${r}`).format.fill='#FFF2CC';}if(st==='D Interno aprobado')c.getRange(`I${r}:J${r}`).format.fill='#DDEBF7';}
const families=[...new Set(t.origenes.filter(r=>r[4]==='Sí').map(r=>r[2]))].sort();
const last=30+families.length;
body(summary,'I',last);base(summary,'I','52 · Diccionario SIES aplicado al seguimiento intertrimestral','B/C · Se conserva el código de la cohorte MU/T1; se revisa la versión del contexto académico por separado.','D · Ninguna base, tasa ni denominador cambia. E · Un código pendiente o un contexto no localizado no significa deserción.');
summary.getRange('A:A').format.columnWidth=24;summary.getRange('B:B').format.columnWidth=43;summary.getRange('C:H').format.columnWidth=18;summary.getRange('I:I').format.columnWidth=24;
summary.getRange('A5:I5').values=[['Año MU/T1','Alcance','Estudiantes T1','Con contexto','Sin contexto','Obs. documentales','Obs. internas','Obs. pendientes','Clasificación']];header(summary,5,'I');
for(let i=0;i<3;i++){const r=6+i,y=2024+i;summary.getRange(`A${r}:I${r}`).values=[[y,'Grupo 1 del libro',null,null,null,null,null,null,'B/C/D/E']];for(const [dest,col]of [['C','F'],['D','G'],['E','H']])fx(summary,`${dest}${r}`,`=SUMIF('53_Codigos_T1_Confirmados'!$A$6:$A$${on},A${r},'53_Codigos_T1_Confirmados'!$${col}$6:$${col}$${on})`);for(const [dest,st]of [['F','B/C Documental'],['G','D Interno aprobado'],['H','E Pendiente']])fx(summary,`${dest}${r}`,`=SUMIFS('54_Contextos_y_Pendientes'!$M$6:$M$${cn},'54_Contextos_y_Pendientes'!$A$6:$A$${cn},A${r},'54_Contextos_y_Pendientes'!$J$6:$J$${cn},"${st}")`);}
summary.getRange('A9:B9').values=[['Total registros','Personas-año / contextos, según columna']];for(const col of 'CDEFGH')fx(summary,`${col}9`,`=SUM(${col}6:${col}8)`);summary.getRange('A9:I9').format.fill='#DDEBF7';summary.getRange('A9:I9').format.font.bold=true;
summary.getRange('A11:B11').merge();summary.getRange('A11').values=[['Control población T1: debe ser 0']];fx(summary,'C11','=C9-D9-E9');summary.getRange('D11:F11').merge();summary.getRange('D11').values=[['Contextos consultados: no es denominador']];fx(summary,'G11','=SUM(F9:H9)');summary.getRange('H11:I11').merge();summary.getRange('H11').values=[['C · Sin adjudicaciones nuevas']];
summary.getRange('A13:I14').merge();summary.getRange('A13').values=[['Cómo revisar: en la hoja 53 filtre «Varias versiones» = Sí para ver los códigos de origen. En la hoja 54 filtre «Origen con varias versiones» = Sí y «Respaldo» para separar documental, interno aprobado y pendiente. La familia T1 y la del contexto pueden diferir: no se fuerza la continuidad de un plan.']];summary.getRange('A13:I14').format.fill=muted;
summary.getRange('A16:I16').values=[['Familia SIES T1','Carrera T1','Estudiantes T1','Obs. documentales','Obs. internas','Obs. pendientes','Sin contexto','Total contextos','Clasificación']];header(summary,16,'I');
for(let i=0;i<families.length;i++){let r=17+i,f=families[i],nm=[...new Set(t.origenes.filter(x=>x[2]===f).map(x=>x[1]))].join(' / ');summary.getRange(`A${r}:I${r}`).values=[[f,nm,null,null,null,null,null,null,'B/C/D/E']];for(const [dest,col]of [['C','F'],['G','H']])fx(summary,`${dest}${r}`,`=SUMIF('53_Codigos_T1_Confirmados'!$C$6:$C$${on},A${r},'53_Codigos_T1_Confirmados'!$${col}$6:$${col}$${on})`);for(const[dest,st]of [['D','B/C Documental'],['E','D Interno aprobado'],['F','E Pendiente']])fx(summary,`${dest}${r}`,`=SUMIFS('54_Contextos_y_Pendientes'!$M$6:$M$${cn},'54_Contextos_y_Pendientes'!$F$6:$F$${cn},A${r},'54_Contextos_y_Pendientes'!$J$6:$J$${cn},"${st}")`);fx(summary,`H${r}`,`=SUM(D${r}:F${r})`);if(i%2===0)summary.getRange(`A${r}:I${r}`).format.fill=muted;}
let end=17+families.length;summary.getRange(`A${end}:B${end}`).values=[['Total foco','Familias con versiones múltiples en la evidencia']];for(const col of 'CDEFGH')fx(summary,`${col}${end}`,`=SUM(${col}17:${col}${end-1})`);summary.getRange(`A${end}:I${end}`).format.fill='#DDEBF7';summary.getRange(`A${end}:I${end}`).format.font.bold=true;
const notes=[
'B/C · Los 3.179 códigos T1 están comprobados: 558 (2024), 1.150 (2025) y 1.471 (2026), como aparecen en esta versión del libro. Grupos de ingreso T2/T3 preservados, no reclasificados en esta aplicación.',
'B/C · Una observación es persona–expediente–plan–año–período nativo. Una persona puede aportar varias. El código anual documentado es reutilizable en el contexto ya atribuido; no demuestra aceptación SIES ni día exacto de cambio.',
'D/E · Dos correspondencias internas ya aprobadas siguen sin atribución documental. Los candidatos de las filas pendientes NO fueron adoptados. La ausencia de contexto en el diccionario no prueba ausencia de matrícula.',
'B/C · El puente explícito N_DOC–RUT de IPSS_Procesamiento.xlsx / 2025_carga se reutilizó para 20 documentos P; no se inventó una conversión ni se cambió el documento original.',
'Fuentes: V11, respaldo AUDITADO_ENTREGA (hojas 9, 11, 20, 24, 25), BASE_RETENCION_MU y diccionario activo v1_20261023. Rutas, hashes, consultas privadas y QA: MANIFEST_APLICACION.json junto al libro.',
'E · Las notas y resultados históricos de las hojas 1–51 se conservan. Esta aplicación no certifica sus tasas ni convierte los períodos nativos de PROMEDIOS en fotos completas de cierre.'];
for(let i=0;i<notes.length;i++){let r=end+2+i;summary.getRange(`A${r}:I${r}`).merge();summary.getRange(`A${r}`).values=[[notes[i]]];summary.getRange(`A${r}:I${r}`).format.rowHeight=42;if(i%2===0)summary.getRange(`A${r}:I${r}`).format.fill=muted;}
summary.getRange(`C6:H${end}`).setNumberFormat('#,##0');
wb.recalculate();
await(await SpreadsheetFile.exportXlsx(wb)).save(dir+'/suplemento.xlsx');
await fs.writeFile(dir+'/FORMULAS_NUEVAS.json',JSON.stringify(forms,null,2));
for(const[name,range,file]of [[names[0],'A1:I25','revision'],[names[1],'A1:I12','origenes'],[names[2],'F1:O12','contextos']])await fs.writeFile(dir+'/preview_'+file+'.png',new Uint8Array(await(await wb.render({sheetName:name,range,scale:1.15,format:'png'})).arrayBuffer()));
console.log(JSON.stringify({hojas:names,filas_origen:t.origenes.length,filas_contexto:t.contextos.length,formulas:forms.length}));
