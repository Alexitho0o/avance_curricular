import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const dir='/Users/alexi/Documents/GitHub/avance_curricular/.local_restricted/retencion_intermedia/20261021_144031';
process.umask(0o077);
const d=JSON.parse(await fs.readFile(`${dir}/payload.json`,'utf8'));
const w=Workbook.create();
const names=['Resumen_privado','Cohortes_MU','Identidad_20','Cierres_observados','Matriculas_20','MU_anual_20','Fuentes'];
for(const n of names)w.worksheets.add(n);
const col=n=>{let s='';for(;n>0;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const sheets={};
function table(name,title,note,headers,rows,textcols=[],widths={}){
 const s=w.worksheets.getItem(name);sheets[name]=s;s.showGridLines=false;
 const end=rows.length+6,last=col(headers.length);
 s.getRange(`A1:${last}${end}`).format={font:{name:'Arial',size:11,color:'#3A3A3A'},rowHeight:23,verticalAlignment:'center'};
 s.getRange(`A1:${last}${end}`).setNumberFormat('0');
 for(let c=1;c<=headers.length;c++)s.getRange(`${col(c)}:${col(c)}`).format.columnWidth=widths[c]||18;
 s.mergeCells(`A2:${col(Math.min(headers.length,6))}2`);s.getRange('A2').values=[[title]];
 s.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:'#102B42'};
 s.getRange('A2').format.rowHeight=35;
 s.mergeCells(`A3:${col(Math.min(headers.length,6))}4`);s.getRange('A3').values=[[note]];
 s.getRange(`A3:${col(Math.min(headers.length,6))}4`).format={wrapText:true,fill:'#FFF2CC',font:{name:'Arial',size:11,color:'#3A3A3A'},rowHeight:32};
 s.getRange(`A6:${last}6`).values=[headers];
 if(rows.length)s.getRange(`A7:${last}${end}`).values=rows;
 const t=s.tables.add(`A6:${last}${end}`,true,'Tbl'+name.replace(/_/g,''));t.showFilterButton=true;t.style='TableStyleLight1';
 s.getRange(`A6:${last}6`).format={fill:'#0E4273',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:58,horizontalAlignment:'center',verticalAlignment:'center'};
 for(const c of textcols)s.getRange(`${col(c)}7:${col(c)}${end}`).setNumberFormat('@');
 s.freezePanes.freezeRows(6);
 return s;
}
const nr=d.people.length+6,nc=d.closures.length+6,no=d.observations.length+6,ni=d.identity.length+6;
const peopleHeaders=['Persona C','Cohorte D','TIPO_DOC original B','N_DOC original B','DV original B','FILA_RAW B','Código único C','Carrera B','COD_SED B','COD_CAR B','JOR B','VERSION B','ANIO_ING_ORI B','SEM_ING_ORI B','VIG informado B','CODCLI documentados B/C','Llave disponible C/E','Clasificación','Registros T2 C','Registros T3 C','Presencia T2 C/E','Presencia T3 C/E','Estado T2 observado B/C','Estado T3 observado B/C'];
const p=table('Cohortes_MU','Cohortes fijas y búsqueda en los cuatro listados','D: 558 personas de cohorte 2024 y 1.150 de 2025. Las presencias son C; ausencia de un listado parcial no prueba deserción (E). La elegibilidad anual se reutiliza sin modificar su motor.',peopleHeaders,d.people.map(r=>[...r,null,null,null,null,null,null]),[1,3,4,5,7,9,10,11,12,15,16],{1:21,4:23,7:26,8:52,16:28,17:32,18:30,21:40,22:40,23:29,24:29});
for(let r=7;r<=nr;r++){
 for(const [dest,term] of [['S','T2'],['T','T3']])p.getRange(`${dest}${r}`).formulas=[[`=COUNTIFS('Cierres_observados'!$A$7:$A$${nc},$A${r},'Cierres_observados'!$C$7:$C$${nc},($B${r}+1)&"-${term}")`]];
 for(const [dest,number] of [['U','S'],['V','T']])p.getRange(`${dest}${r}`).formulas=[[`=IF(${number}${r}>0,"Presencia observada",IF(Q${r}="Pendiente CODCLI","Pendiente llave","No localizado en listado parcial"))`]];
 p.getRange(`W${r}`).formulas=[[`=IF(B${r}=2025,"Sin campo",IF(S${r}=0,"Sin presencia",IF(COUNTIFS('Cierres_observados'!$A$7:$A$${nc},$A${r},'Cierres_observados'!$C$7:$C$${nc},($B${r}+1)&"-T2",'Cierres_observados'!$L$7:$L$${nc},"VIGENTE")>0,"VIGENTE observado","Otro estado observado")))`]];
 p.getRange(`X${r}`).formulas=[[`=IF(T${r}=0,"Sin presencia",IF(COUNTIFS('Cierres_observados'!$A$7:$A$${nc},$A${r},'Cierres_observados'!$C$7:$C$${nc},($B${r}+1)&"-T3",'Cierres_observados'!$L$7:$L$${nc},"VIGENTE")>0,"VIGENTE observado","Otro estado observado"))`]];
}
table('Cierres_observados','Matrículas localizadas en listados de cierre','B/C: todas las 331 filas coincidentes, incluidas varias matrículas de una persona. La cohorte se cuenta una vez en Cohortes_MU. No se incorporan personas ajenas a las cohortes aprobadas.',
 ['Persona C','Cohorte D','Cierre','RUT literal B','CODCLI literal B','Código carrera UMAS B','Carrera B','ANOMATRICULA B','PERIODOMATRICULA B','ANOINGRESO B','PERIODOINGRESO B','ESTADOACADEMICO B','FECHAMATRICULA literal B','Fuente ID','Hoja','Fila Excel B','Método C','Clasificación'],d.closures,[1,3,4,5,6,8,9,10,11,13,14],{1:21,4:25,7:52,12:27,13:29,15:28,17:32,18:36});
const obs=table('Matriculas_20','Todas las matrículas observadas del grupo de 20','B/C: cada fila mantiene fuente, hoja y fila Excel. Filtrar Grupo 14 = 1 para el seguimiento. Las fechas del archivo y FECHAMATRICULA no certifican fecha efectiva del estado ni cierre (E).',
 ['Persona C','Respaldo','RUT literal B','CODCLI literal B','CODCARPR B','Carrera B','ANOMATRICULA B','PERIODOMATRICULA B','ANOINGRESO B','PERIODOINGRESO B','ESTADOACADEMICO B','SITUACION B','SEDE B','JORNADA B','NIVEL observado B','FECHAMATRICULA literal B','FECH_CAR literal B','Fecha título disponible B','Fecha egreso disponible B','Fuente ID','Hoja','Fila Excel B','Fecha nominal archivo B','Método C','Grupo 14 C','Clasificación','Fecha matrícula legible C','Fecha carga legible C'],d.observations.map(r=>[...r,null,null]),[1,2,3,4,5,7,8,9,10,12,13,14,15,16,17,18,19,20,23],{1:21,2:36,3:24,6:52,11:26,12:38,16:29,17:29,18:29,19:29,21:28,23:29,24:29,26:36,27:29,28:29});
for(let r=7;r<=no;r++){
 obs.getRange(`AA${r}`).formulas=[[`=IF(P${r}="","No disponible",IFERROR(VALUE(P${r}),P${r}))`]];
 obs.getRange(`AB${r}`).formulas=[[`=IF(Q${r}="","No disponible",IFERROR(VALUE(Q${r}),Q${r}))`]];
}
obs.getRange(`AA7:AB${no}`).setNumberFormat('yyyy-mm-dd hh:mm');
const id=table('Identidad_20','Correspondencia documental y CODCLI','B/C: relación observada en la misma fila de IPSS_Procesamiento, J=RUT y BU/BV=N_DOC/DV. No certifica el documento definitivo. Las 20 personas ya están en 1.150 (D). Dos conservan CODCLI pendiente (E).',
 ['Persona C','Cohorte D','TIPO_DOC B','N_DOC original B','DV original B','RUT preparación literal B','Filas preparación B','CODCLI 1 B','CODCLI 2 B','N CODCLI C','Resolución C/E','Carrera de cohorte B','Grupo 14 C','Fuente ID','Referencia puente','Clasificación','Filas 10246 C','Filas 11998 C','Filas 12112 C','VIGENTE 10246 C','VIGENTE 11998 C','VIGENTE 12112 C'],d.identity.map(r=>[...r,null,null,null,null,null,null]),[1,3,4,5,6,7,8,9,14],{1:21,4:24,6:28,7:27,8:22,9:22,11:24,12:52,15:32,16:37});
for(let r=7;r<=ni;r++){
 id.getRange(`J${r}`).formulas=[[`=IF(H${r}="Pendiente",0,IF(I${r}="",1,2))`]];
 id.getRange(`K${r}`).formulas=[[`=IF(J${r}=0,"Pendiente","Identificado")`]];
 for(const [cc,label] of [['Q','10246'],['R','11998'],['S','12112']])id.getRange(`${cc}${r}`).formulas=[[`=COUNTIFS('Matriculas_20'!$A$7:$A$${no},$A${r},'Matriculas_20'!$B$7:$B$${no},"${label}")`]];
 for(const [cc,label] of [['T','10246'],['U','11998'],['V','12112']])id.getRange(`${cc}${r}`).formulas=[[`=COUNTIFS('Matriculas_20'!$A$7:$A$${no},$A${r},'Matriculas_20'!$B$7:$B$${no},"${label}",'Matriculas_20'!$K$7:$K$${no},"VIGENTE")`]];
}
table('MU_anual_20','Observaciones en la base anual del grupo de 20','B/C: búsqueda exacta por documento original P o por su correspondencia explícita. Una fila anual no acredita presencia en T2/T3. Se conserva el VIG informado; no se reasigna desde UMAS.',
 ['Persona C','ANIO_INFORMADO B','TIPO_DOC original B','N_DOC original B','DV original B','COD_SED B','COD_CAR B','JOR B','VERSION B','ANIO_ING_ORI B','SEM_ING_ORI B','VIG informado B','FILA_RAW B','Fuente ID','Método C','Clasificación'],d.annual20,[1,3,4,5,6,7,8,9,12,14],{1:21,4:24,15:44,16:49});
table('Fuentes','Fuentes consultadas y localización exacta','B/C: hashes recalculados, rutas de procedencia y hoja. Los identificadores permanecen en este libro privado. Los cuatro respaldos sin pareja RUT/CODCLI se registran como no comparables, no como cero hallazgos.',
 ['Fuente ID','Ruta','Hoja','SHA-256','Bytes','Contexto y alcance','Clasificación','Modificación archivo B'],d.sources.map(s=>[s.id,s.path,s.sheet,s.sha256,s.bytes,s.context,s.clasificacion,s.mtime]),[1,4],{1:17,2:100,3:38,4:72,5:18,6:85,7:22,8:35});
sheets.Fuentes.getRange(`B7:C${d.sources.length+6}`).format.wrapText=true;
sheets.Fuentes.getRange(`F7:H${d.sources.length+6}`).format.wrapText=true;
sheets.Fuentes.getRange(`A7:H${d.sources.length+6}`).format.rowHeight=72;
const s=w.worksheets.getItem('Resumen_privado');sheets.Resumen_privado=s;s.showGridLines=false;s.tabColor='#102B42';
s.getRange('A1:I47').format={font:{name:'Arial',size:11,color:'#3A3A3A'},verticalAlignment:'center',rowHeight:27};
for(const [c,ww]of Object.entries({A:15,B:18,C:18,D:19,E:24,F:25,G:24,H:24,I:36}))s.getRange(`${c}:${c}`).format.columnWidth=ww;
function merged(row,text,fill=null,height=37){s.mergeCells(`A${row}:I${row}`);s.getRange(`A${row}`).values=[[text]];s.getRange(`A${row}:I${row}`).format.wrapText=true;s.getRange(`A${row}:I${row}`).format.rowHeight=height;if(fill)s.getRange(`A${row}:I${row}`).format.fill=fill;}
merged(2,'Retención intermedia IPSS 162: revisión privada');s.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:'#102B42'};
merged(3,'D: uso privado autorizado. Incluye identificadores individuales. Carpeta excluida de Git; no adjuntar a repositorios ni servicios externos.','#FFF2CC',39);
merged(4,'C: las fórmulas cuentan personas únicas desde Cohortes_MU; los listados conservan todas sus filas. Filtre Persona C para seguir una trayectoria y Fuente ID para encontrar el archivo, hoja y fila originales.',null,42);
const head=(row,a)=>{s.getRange(`A${row}:I${row}`).values=[a];s.getRange(`A${row}:I${row}`).format={fill:'#0E4273',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:52,horizontalAlignment:'center'};};
head(6,['Cohorte D','Cierre','Denominador C/D','Presencias C','VIGENTE observado B/C','Registros C','Cobertura E','Vigencia al cierre E','Tasa E']);
for(let i=0;i<4;i++){
 const r=7+i,x=d.control[i],term=i%2===0?'U':'V',state=i%2===0?'W':'X';
 s.getRange(`A${r}:I${r}`).values=[[x.cohort,x.closure,null,null,null,null,'Pendiente','Pendiente','Pendiente']];
 s.getRange(`C${r}`).formulas=[[`=COUNTIFS('Cohortes_MU'!$B$7:$B$${nr},A${r})`]];
 s.getRange(`D${r}`).formulas=[[`=COUNTIFS('Cohortes_MU'!$B$7:$B$${nr},A${r},'Cohortes_MU'!$${term}$7:$${term}$${nr},"Presencia observada")`]];
 s.getRange(`E${r}`).formulas=[[i===2?'="Sin campo"':`=COUNTIFS('Cohortes_MU'!$B$7:$B$${nr},A${r},'Cohortes_MU'!$${state}$7:$${state}$${nr},"VIGENTE observado")`]];
 s.getRange(`F${r}`).formulas=[[`=COUNTIFS('Cierres_observados'!$C$7:$C$${nc},B${r})`]];
}
s.getRange('G7:I10').format.fill='#FFF2CC';s.getRange('C7:F10').setNumberFormat('#,##0');s.getRange('A7:A10').setNumberFormat('0');
s.getRange('A7:B10').format.horizontalAlignment='center';
merged(12,'E: 0 presencias en el listado parcial 2026-T3 no significa 0 retenidos. Sin cobertura y fecha efectiva acreditadas no se calcula tasa intermedia.', '#FFF2CC',41);
head(14,['Grupo','Personas C','Con CODCLI C','Pendientes E','CODCLI C','Incluidas en cohorte D','Fuentes B','', '']);
s.getRange('A15').values=[['Grupo de 20']];s.getRange('B15').formulas=[[`=COUNTA('Identidad_20'!A7:A${ni})`]];
s.getRange('C15').formulas=[[`=COUNTIFS('Identidad_20'!J7:J${ni},">0")`]];s.getRange('D15').formulas=[['=B15-C15']];s.getRange('E15').formulas=[[`=SUM('Identidad_20'!J7:J${ni})`]];s.getRange('F15').values=[['Ya incluidas en 1.150']];s.mergeCells('G15:I15');s.getRange('G15').values=[['Puente documental explícito, sin identificación aproximada']];s.getRange('F15:I15').format.wrapText=true;s.getRange('A15:I15').format.rowHeight=48;
head(17,['Respaldo B','Grupo 14 C','Matrículas C','Alguna VIGENTE C','Sin VIGENTE C','Estado efectivo al cierre E','','','']);
for(const [i,label]of ['10246','11998','12112'].entries()){
 const r=18+i,cc=['T','U','V'][i];s.getRange(`A${r}`).values=[[label]];
 s.getRange(`B${r}`).formulas=[[`=COUNTIFS('Identidad_20'!$M$7:$M$${ni},1)`]];
 s.getRange(`C${r}`).formulas=[[`=COUNTIFS('Matriculas_20'!$B$7:$B$${no},A${r},'Matriculas_20'!$Y$7:$Y$${no},1)`]];
 s.getRange(`D${r}`).formulas=[[`=COUNTIFS('Identidad_20'!$M$7:$M$${ni},1,'Identidad_20'!$${cc}$7:$${cc}$${ni},">0")`]];
 s.getRange(`E${r}`).formulas=[[`=B${r}-D${r}`]];s.mergeCells(`F${r}:I${r}`);s.getRange(`F${r}`).values=[['Pendiente. La fotografía no acredita el cierre.']];
}
merged(22,'B/C: los 58 respaldos de Base Maestra conservan el seguimiento nominal. Hasta 08-sep hay 13 de las 14 personas con alguna VIGENTE; desde 09-sep hay 14. La fecha nominal no prueba el momento efectivo del cambio ni una renovación.',null,49);
merged(24,'Cómo revisar: Cohortes_MU muestra las dos cohortes y las cuatro búsquedas. Identidad_20 conserva el puente y los dos pendientes. Matriculas_20 conserva todas las matrículas observadas y permite filtrar Grupo 14 = 1. Fuentes permite verificar cada registro por ruta, hoja, fila y hash.',null,50);
merged(26,'A: la regla SIES anual usa la misma institución y cohorte de origen, programas regulares de duración mínima 4/6/8 según nivel, excluye especiales y ciertas inconsistencias; su referencia es 30 de abril. Fuente: correo SIES 09-sep-2026, congelado en el proyecto.',null,50);
merged(28,'C: el módulo longitudinal opcional excluye TITULADO en el período base, pero en destino solo reconoce VIGENTE/SUSPENDIDO como retenidos. Un destino TITULADO/EGRESADO puede quedar NO_RETENIDO sin evaluar fecha de título. Código verificado; no se modificó.',null,50);
merged(30,'D/E: propuesta solicitada: distinguir término de estudios acreditado de falta de rematrícula cuando debía continuar. Falta aprobar regla intermedia y disponer de título del programa seguido con fecha; no inferir título por duración cumplida ni por un título intermedio.', '#FFF2CC',50);
merged(32,'B/C: se separan duración formal del plan, nivel teórico esperado, NIVEL observado, avance curricular, egreso y titulación con fecha. Ninguna de estas variables sustituye automáticamente a otra. Una matrícula posterior en otra carrera se conserva como matrícula distinta.',null,46);
merged(34,'D: se mantienen 558 y 1.150. El seguimiento anual separado conserva 74/222 = 33,33% y 48/124 = 38,71%. No se presenta como retención intermedia ni se altera Escenario_80 del agregado.',null,46);
merged(36,'E: pendientes: correspondencia explícita de dos CODCLI; cobertura y fecha efectiva de cuatro cierres; semántica de FECHAMATRICULA y fecha de estado; tratamiento interno aprobado de egreso/titulación. No se interpretan ausencias como deserción.', '#FFF2CC',46);
merged(38,'C: fechas legibles convierten únicamente seriales Excel presentes en la fuente; se conserva al lado el literal original. FECHAMATRICULA no es fecha efectiva de estado. Si la fuente no informa una fecha, se muestra No disponible.',null,43);
merged(40,'A: definición oficial. B: dato observado. C: cruce, fórmula o implementación. D: decisión interna. E: hipótesis o pendiente. El cálculo propio y las propuestas no son definiciones SIES.',null,42);
merged(42,'C: Arial se conserva como fuente legible de trabajo; paleta institucional #102B42, #0E4273 y #CFB47C. No se certifica tipografía oficial ni validación en Microsoft Excel nativo.',null,39);
merged(44,`Fecha de preparación: ${d.created}. Fuentes y hashes en Fuentes. El agregado aprobado se conserva byte a byte.`,null,34);
// Formula sensitivity on real input fields, always restore before final calculation.
w.recalculate();
const sr=d.identity.findIndex(x=>x[9]>0)+7;
const before=id.getRange(`J${sr}`).values[0][0],h=id.getRange(`H${sr}`).values[0][0],iv=id.getRange(`I${sr}`).values[0][0];
if(!(before>0))throw Error('Sensitivity requires an identified person');
id.getRange(`H${sr}`).values=[['Pendiente']];id.getRange(`I${sr}`).values=[['']];
if(id.getRange(`J${sr}`).values[0][0]!==0)throw Error('CODCLI sensitivity not recalculated');
id.getRange(`H${sr}`).values=[[h]];id.getRange(`I${sr}`).values=[[iv]];
w.recalculate();
if(id.getRange(`J${sr}`).values[0][0]!==before)throw Error('CODCLI restore failed');
const actual=s.getRange('C7:F10').values;
const expected=d.control.map(x=>[x.denominator,x.found,x.vigente===null?'Sin campo':x.vigente,x.rows]);
if(JSON.stringify(actual)!==JSON.stringify(expected))throw Error('Closure formulas disagree with direct source control');
if(JSON.stringify(s.getRange('B15:E15').values[0])!==JSON.stringify([20,18,2,19]))throw Error('20 reconciliation failed');
if(JSON.stringify(s.getRange('B18:E20').values)!==JSON.stringify([[14,15,13,1],[14,15,14,0],[14,15,14,0]]))throw Error('14 follow-up failed');
const scan=await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},maxChars:3000});
await fs.writeFile(`${dir}/formula_scan.ndjson`,scan.ndjson);
if(scan.ndjson.includes('"address"'))throw Error('Formula errors found');
const out=`${dir}/DETALLE_PRIVADO_RETENCION_INTERMEDIA_20261021_144031.xlsx`;
await(await SpreadsheetFile.exportXlsx(w)).save(out);await fs.chmod(out,0o600);
// Render every tab with identifiers masked temporarily. Never export the masked workbook.
await fs.mkdir(`${dir}/previews`,{recursive:true,mode:0o700});
const overview=await w.render({sheetName:'Resumen_privado',range:'A1:I20',scale:1,format:'png'});await fs.writeFile(`${dir}/previews/Resumen_privado.png`,new Uint8Array(await overview.arrayBuffer()));
const masks={Cohortes_MU:['A','C','D','E','P'],Identidad_20:['A','C','D','E','F','H','I'],Cierres_observados:['A','D','E'],Matriculas_20:['A','C','D'],MU_anual_20:['A','C','D','E']};
for(const [name,cols]of Object.entries(masks))for(const c of cols){const sh=sheets[name];const end=sh.getUsedRange().address;sh.getRange(`${c}7:${c}${name==='Cohortes_MU'?nr:name==='Identidad_20'?ni:name==='Cierres_observados'?nc:name==='Matriculas_20'?no:d.annual20.length+6}`).values=[['RESERVADO']];}
for(const name of names.filter(n=>n!=='Resumen_privado')){const range=name==='Fuentes'?'A1:F9':'A1:H10';const img=await w.render({sheetName:name,range,scale:1,format:'png'});await fs.writeFile(`${dir}/previews/${name}.png`,new Uint8Array(await img.arrayBuffer()));}
console.log(JSON.stringify({status:'exportado_recalculado',path:out,closure_controls:actual,identity:[20,18,2,19],focus:[[14,15,13],[14,15,14],[14,15,14]],sensitivity:'PASS',preview_tabs:names.length}));
