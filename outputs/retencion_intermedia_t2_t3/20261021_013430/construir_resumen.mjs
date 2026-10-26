import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const dir=path.dirname(fileURLToPath(import.meta.url));
const input=JSON.parse(await fs.readFile(path.join(dir,'insumos_agregados.json'),'utf8'));
const wb=Workbook.create();
const s=wb.worksheets.add('Resumen'), p=wb.worksheets.add('Por_carrera'), f=wb.worksheets.add('Fuentes_y_alcance');
const navy='#102B42',gold='#CFB47C';
function write(sh,row,col,data,formulas=false){const r=sh.getRangeByIndexes(row-1,col-1,data.length,data[0].length);if(formulas)r.formulas=data;else r.values=data;}
function setup(sh,cols,rows){sh.showGridLines=false;sh.getRange(`A1:${cols}${rows}`).format={font:{name:'Arial',size:11,color:'#3A3A3A'},rowHeight:26,columnWidth:17,verticalAlignment:'center'};}
function title(sh,text,last){sh.getRange('A2').values=[[text]];sh.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:navy};sh.getRange(`A3:${last}3`).format.borders={bottom:{style:'thin',color:gold}};}
function header(sh,row,labels,name,end){write(sh,row,1,[labels]);const r=sh.getRangeByIndexes(row-1,0,1,labels.length);r.format={fill:navy,font:{name:'Arial',size:11,color:'#FFFFFF',bold:true},wrapText:true,rowHeight:52,horizontalAlignment:'center',verticalAlignment:'center'};if(name){const t=sh.tables.add(`A${row}:${String.fromCharCode(64+labels.length)}${end}`,true,name);t.style='TableStyleLight1';}}
function note(sh,cell,text){sh.getRange(cell).values=[[text]];}
setup(s,'I',37);setup(p,'K',45);setup(f,'F',40);
title(s,'Retención intermedia: revisión de cohortes 2024 y 2025','I');s.tabColor=navy;
note(s,'A4','C: seleccione una carrera en H4 para revisar los cuatro cierres.');
note(s,'H4','Todas');s.getRange('H4').format.fill='#FFF2CC';
const careers=['Todas',...new Set(input.career.map(r=>r[1]))];
write(f,6,8,[['Carreras disponibles']]);write(f,7,8,careers.map(x=>[x]));f.getRange(`H6:H${6+careers.length}`).format.columnWidth=58;
wb.names.add('CarrerasRevisionIntermedia',`='Fuentes_y_alcance'!$H$7:$H$${careers.length+6}`);
s.getRange('H4').dataValidation={rule:{type:'list',formula1:'CarrerasRevisionIntermedia'}};
note(s,'A5','E: listados parciales. Los localizados no permiten calcular una tasa de retención del cierre.');
header(s,7,['Cohorte','Cierre observado','Estudiantes de referencia anual','Localizados en el listado','Con estado VIGENTE','Sin llave comparable','Sin localizar con llave','Tasa intermedia','Qué falta (E)'],'RevisionIntermedia',11);
const periods=[[2024,'2025-T2',2],[2024,'2025-T3',3],[2025,'2026-T2',2],[2025,'2026-T3',3]];
const range=c=>`'Por_carrera'!$${c}$7:$${c}$34`;
const sum=(c,r)=>`IF($H$4="Todas",SUMIFS(${range(c)},${range('A')},A${r}),SUMIFS(${range(c)},${range('A')},A${r},${range('B')},$H$4))`;
for(let i=0;i<4;i++){
 const r=8+i,[year,label,term]=periods[i];
 write(s,r,1,[[year,label,null,null,null,null,null,'Pendiente',input.review.pendientes_E[i][2]]]);
 write(s,r,3,[[`=${sum('D',r)}`,`=${sum(term===2?'F':'H',r)}`,year===2025&&term===2?'="Sin estado"':`=${sum(term===2?'G':'I',r)}`,`=${sum('E',r)}`,`=C${r}-D${r}-F${r}`]],true);
}
s.getRange('A8:B11').format.horizontalAlignment='center';s.getRange('C8:G11').setNumberFormat('#,##0');
s.getRange('I8:I11').format.wrapText=true;s.getRange('A8:I11').format.rowHeight=79;
s.getRange('H8:I11').format.fill='#FFF2CC';
s.getRange('H8:H11').format.horizontalAlignment='center';s.getRange('E10').format.horizontalAlignment='center';
note(s,'A13','C/E: 558 y 1.150 son referencias del motor anual existente, no una nueva aprobación del denominador intermedio.');
note(s,'A14','B/E: VIGENTE describe el archivo recibido. Falta confirmar cobertura completa y estado efectivo a la fecha de cada cierre.');
note(s,'A15','E: sin localizar no equivale a desertor. T2-2026 carece de estado académico; no se rellena como 0 ni como 1.');
note(s,'A17','Seguimiento distinto ya solicitado: ingresos 2025 T2/T3 buscados en MU2026');s.getRange('A17').format.font.bold=true;
note(s,'A18','D/C: conserva 222 y 124 estudiantes, incluidos ELIMINADO. Esta sección no cambia con el selector de carrera.');
header(s,20,['Ingreso','Estudiantes (D)','Localizados (C)','Con VIG 1 (C)','Solo VIG 0 (C)','Ausentes (C)','Continuidad (C)','Clase','Observación'],'ContinuidadYaCalculada',22);
for(let i=0;i<2;i++){
 const r=21+i,rr=30+i;write(s,r,1,[[`2025-T${i+2}`,null,null,null,null,null,null,'C / D / E','Continuidad institucional, no tasa SIES oficial. No explica las ausencias.']]);
 write(s,r,2,[['B','C','D','E','F'].map(c=>`='Fuentes_y_alcance'!${c}${rr}`).concat([`=IF(B${r}=0,"Sin denominador",D${r}/B${r})`])],true);
}
s.getRange('G21:G22').setNumberFormat('0.00%');s.getRange('I21:I22').format.wrapText=true;s.getRange('A21:I22').format.rowHeight=52;
s.getRange('H21:H22').format.horizontalAlignment='center';
note(s,'A24','D: las decisiones VIG para MU2027 no se aplican retroactivamente a estas bases ni a estos denominadores.');
note(s,'A25','B/E: el estudio 2026 documentó cambios por nómina; su fundamento académico individual sigue pendiente.');
note(s,'A27','Siguiente paso: incorporar las matrículas completas al cierre de cada período, con fecha y estado verificable.');
for(const [c,w] of [['A',11],['B',18],['C',19],['D',18],['E',20],['F',18],['G',21],['H',19],['I',56]])s.getRange(`${c}1:${c}37`).format.columnWidth=w;

title(p,'Detalle por carrera de origen y cohorte','K');
note(p,'A4','B/C: insumos agregados del cruce ya verificado, sin recalcular elegibilidad. Las tasas T2/T3 siguen pendientes (E).');
header(p,6,['Cohorte','Carrera de origen','Candidatos MU','Referencia anual','Sin llave comparable','Localizados T2','VIGENTE T2','Localizados T3','VIGENTE T3','Tasa T2 (E)','Tasa T3 (E)'],'DetalleCarreras',34);
write(p,7,1,input.career.map(r=>[...r,'Pendiente','Pendiente']));p.freezePanes.freezeRows(6);
p.getRange('A7:A34').format.horizontalAlignment='center';p.getRange('J7:K34').format.horizontalAlignment='center';
p.getRange('A7:A34').setNumberFormat('0');p.getRange('C7:I34').setNumberFormat('#,##0');p.getRange('B1:B40').format.columnWidth=61;p.getRange('A7:K34').format.rowHeight=28;
note(p,'A37','C: procedencia única: libro de revisión 20-10-2026, Por_carrera!A7:I34. Ruta y SHA-256 en Fuentes_y_alcance.');
note(p,'A38','E: los 20 documentos sin llave comparable de la cohorte 2025 no se cuentan como ausencia.');
note(p,'A39','C: las tasas no se calculan porque los archivos de cierre son parciales; los ceros de presencia sí son observaciones.');

title(f,'Fuentes y alcance de los resultados','F');
header(f,6,['Clase','Fuente / hoja','Uso','SHA-256','Ruta','Estado de fuente'],'FuentesConsulta',15);
const sources=input.review.fuentes.map((x,i)=>[i<5?'B':i===5?'C':'A',`${path.basename(x.path)} / ${x.sheet||'Texto'}`,i<4?'Cierre parcial recibido':i===4?'MU informada; origen':i===5?'Motor anual de referencia':'Regla anual; no define T2/T3',x.sha256,x.path,'Íntegra por SHA-256']);
sources.push(['C','Revisión previa / Por_carrera!A7:I34','Conteos usados en este resumen',input.source_workbook.sha256,input.source_workbook.path,'Cachés y controles verificados']);
sources.push(['C','Continuidad previa / manifiesto resultados_C','Insumos del seguimiento separado',input.continuity.salida.sha256,input.continuity.salida.path,'222 / 124 conservados']);
write(f,7,1,sources);f.getRange('A7:F15').format.wrapText=true;f.getRange('A7:F15').format.rowHeight=82;
note(f,'A18','A: regla SIES anual. B: dato observado. C: cálculo o implementación. D: decisión interna. E: pendiente.');
note(f,'A20','D: Alexi confirmó que los cuatro archivos son parciales; preparar revisión y señalar las bases faltantes.');
note(f,'A21','C: la carrera corresponde al origen de la cohorte, aunque la presencia posterior ocurra en otro programa.');
note(f,'A22','E: no equiparar ANOINGRESO/PERIODOINGRESO de UMAS con cohorte de origen SIES sin verificar.');
note(f,'A23','D: revisión MU2027 por versión 20261021_v1. No cambia esta revisión ni constituye norma SIES.');
note(f,'A24','C: este resumen contiene solo agregados. El cruce detallado anterior se conserva localmente y no se replica aquí.');
note(f,'A25','C: formatos numéricos nativos de Excel; Arial conserva la legibilidad del libro de referencia.');
note(f,'A27','Insumos de la continuidad ya calculada (fuente: MANIFEST_CONTINUIDAD.json, resultados_C)');
header(f,29,['Ingreso (D)','Estudiantes (D)','Localizados (C)','VIG 1 (C)','Solo VIG 0 (C)','Ausentes (C)'],'InsumosContinuidad',31);
write(f,30,1,Object.entries(input.continuity.resultados_C).map(([k,v])=>[k,v.students,v.found,v.continue,v.onlyzero,v.absent]));
for(const [c,w] of [['A',13],['B',47],['C',36],['D',73],['E',70],['F',30]])f.getRange(`${c}1:${c}40`).format.columnWidth=w;
f.freezePanes.freezeRows(6);

// Cada carrera y total se contrasta con las entradas agregadas originales.
const checks=[];
for(const car of careers){
 s.getRange('H4').values=[[car]];
 const actual=s.getRange('C8:G11').values;
 const exp=periods.map(([y,,t])=>{const rows=input.career.filter(r=>r[0]===y&&(car==='Todas'||r[1]===car));const sum=c=>rows.reduce((n,r)=>n+r[c],0);const n=sum(3),found=sum(t===2?5:7),noKey=sum(4);return[n,found,y===2025&&t===2?'Sin estado':sum(t===2?6:8),noKey,n-found-noKey];});
 if(JSON.stringify(actual)!==JSON.stringify(exp))throw Error('Filtro no coincide: '+car+' '+JSON.stringify({actual,exp}));
 checks.push({carrera:car,resultado:'OK'});
}
s.getRange('H4').values=[['Todas']];
// Perturbación descartada: se comprueba propagación a resumen sin cambiar insumos finales.
const old=p.getRange('F7').values[0][0];p.getRange('F7').values=[[old+1]];
const changed=s.getRange('D8').values[0][0];if(changed!==2)throw Error('Dependencia de resumen no recalcula');p.getRange('F7').values=[[old]];
wb.recalculate();
const errs=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:50}});
await fs.writeFile(path.join(dir,'formula_scan.ndjson'),errs.ndjson);
for(const sh of [s,p,f]){const blob=await wb.render({sheetName:sh.name,range:sh===s?'A1:I27':sh===p?'A1:K14':'A1:D15',scale:1,format:'png'});await fs.writeFile(path.join(dir,sh.name+'.png'),new Uint8Array(await blob.arrayBuffer()));}
const file=path.join(dir,'REVISION_RETENCION_INTERMEDIA_IPSS_2024_2025_20261021.xlsx');
await (await SpreadsheetFile.exportXlsx(wb)).save(file);
const qa={clasificacion:'C',filtros:checks.length,controles:s.getRange('C8:H11').values,continuidad:s.getRange('B21:G22').values,prueba_dependencia:'OK restaurada',recalculo:'artifact-tool',excel_nativo:'No probado',errors:errs.ndjson};
await fs.writeFile(path.join(dir,'qa_excel.json'),JSON.stringify(qa,null,2));
console.log(JSON.stringify({file,sha256:crypto.createHash('sha256').update(await fs.readFile(file)).digest('hex'),qa}));
