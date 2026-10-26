import fs from 'node:fs/promises';
import {Workbook,FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const R='/Users/alexi/Documents/GitHub/avance_curricular',O=`${R}/outputs/retencion_intermedia_t2_t3/20261021_153436`,P=`${R}/.local_restricted/retencion_intermedia/20261021_153436`;
process.umask(0o077);
const c=JSON.parse(await fs.readFile(`${O}/soporte/config.json`,'utf8')),d=JSON.parse(await fs.readFile(`${P}/datos.json`,'utf8'));
await fs.mkdir(`${P}/previews`,{recursive:true,mode:0o700});
try{await fs.access(`${P}/previews/maqueta_original.png`);}catch{let ref=await SpreadsheetFile.importXlsx(await FileBlob.load(`${P}/referencia_visual.xlsx`));const rimg=await ref.render({sheetName:'14_Vistas_Ejecutivas',range:'B3:V31',scale:1,format:'png'});await fs.writeFile(`${P}/previews/maqueta_original.png`,new Uint8Array(await rimg.arrayBuffer()));ref=null;}
let resume=false;try{await fs.access(`${P}/public_candidate.xlsx`);resume=true;}catch{}
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(resume?`${P}/public_candidate.xlsx`:c.scaffold));
const ncol=x=>[...x].reduce((a,z)=>a*26+z.charCodeAt(0)-64,0);
const acol=n=>{let z='';for(;n>0;n=Math.floor((n-1)/26))z=String.fromCharCode(65+(n-1)%26)+z;return z;};
for(const [name,ee]of Object.entries(resume?{}:c.edits)){
 const s=w.worksheets.getItem(name);
 const rr=new Map();for(const [addr,v]of Object.entries(ee)){const m=addr.match(/^([A-Z]+)(\d+)$/),r=+m[2];if(!rr.has(r))rr.set(r,[]);rr.get(r).push([ncol(m[1]),v,typeof v==='string'&&v.startsWith('=')?'formulas':'values']);}
 const runs=new Map();for(const [r,row]of [...rr].sort((a,b)=>a[0]-b[0])){row.sort((a,b)=>a[0]-b[0]);let current=[];function add(){if(!current.length)return;const key=`${current[0][0]}:${current.at(-1)[0]}:${current[0][2]}`;if(!runs.has(key))runs.set(key,[]);runs.get(key).push([r,current.map(x=>x[1])]);current=[];}for(const cell of row){if(current.length&&(cell[0]!==current.at(-1)[0]+1||cell[2]!==current[0][2]))add();current.push(cell);}add();}
 for(const [key,rows]of runs){const [a,b,kind]=key.split(':');let block=[];function flush(){if(!block.length)return;const range=s.getRange(`${acol(+a)}${block[0][0]}:${acol(+b)}${block.at(-1)[0]}`);range[kind]=block.map(x=>x[1]);block=[];}for(const row of rows){if(block.length&&row[0]!==block.at(-1)[0]+1)flush();block.push(row);}flush();}
 console.log('Applied',name);
 }
// ROWS of the current output cell is dimension-only in Excel, but the local engine
// treats it as a circular value dependency. ROW() keeps the same row index without that dependency.
for(const [name,ee]of Object.entries(c.edits)){const ss=w.worksheets.getItem(name);for(const [a,v]of Object.entries(ee))if(typeof v==='string'&&v.startsWith('=')&&v.includes('ROWS(')){ss.getRange(a).formulas=[[v.replace(/ROWS\(\$?[A-Z]+\$?(\d+):\$?[A-Z]+\$?\d+\)/g,(_,r)=>`(ROW()-${+r-1})`)]];}}
const s=w.worksheets.getItem('14_Vistas_Ejecutivas');
s.getRange('L4:P4').format={font:{name:'Calibri',size:11,color:'#102B42'},fill:'#F2F2F2',horizontalAlignment:'center',verticalAlignment:'center'};
s.getRange('L4').values=[['Último respaldo']];
// Input tables have new, aggregate meanings; keep their fonts/palette while fitting the headers.
const inp=w.worksheets.getItem('11_Entradas_Agregadas');inp.getRange(`A4:AA${c.last11}`).format.font={name:'Calibri',size:11,color:'#3A3A3A'};inp.getRange('A4:AA4').format={fill:'#0E4273',font:{name:'Calibri',size:11,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:65};inp.getRange('A3:AA3').format.rowHeight=37;inp.getRange('A3').format.wrapText=true;
for(const cc of ['A','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','AA'])inp.getRange(`${cc}:${cc}`).format.columnWidth=20;
inp.getRange('B:D').format.columnWidth=34;inp.getRange('E:E').format.columnWidth=30;inp.freezePanes.freezeRows(4);
w.recalculate();
console.log('PUBLIC_IMPORTED',JSON.stringify(s.getRange('C7:E7').values));
const err=await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!',options:{useRegex:true,maxResults:70},maxChars:12000});await fs.writeFile(`${O}/soporte/formula_scan.ndjson`,err.ndjson);
// Save calculated candidate; final transport preserves native charts/geometry/styles from the scaffold.
await(await SpreadsheetFile.exportXlsx(w)).save(`${P}/public_candidate.xlsx`);
const modes={'T1 anual MU':'T1','T2 observado':'T2_records_observed','T3 observado':'T3_records_observed','Último respaldo':'latest_snapshot_2026_VIGENTE'};
const controls=[];
for(const [mode,key]of Object.entries(modes))for(const co of ['Cohorte 2024','Cohorte 2025','Cohortes 2024 y 2025']){
 s.getRange('L4').values=[[mode]];s.getRange('C4').values=[[co]];w.recalculate();
 const years=co==='Cohortes 2024 y 2025'?['2024','2025']:[co.slice(-4)];
 const n=years.reduce((a,y)=>a+c.control[y].denominator,0),k=years.reduce((a,y)=>a+c.control[y][key],0);
 const v=s.getRange('C7:E7').values[0];if(v[0]!==n||v[1]!==k||Math.abs(v[2]-k/n)>1e-12)throw Error('Main summary controls: '+JSON.stringify({mode,co,expected:[n,k],actual:v}));
 controls.push({mode,cohort:co,denominator:n,numerator:k,rate:k/n,status:'PASS'});
}
// Complete connected-filter QA across every governed sector and career for all four modes.
const groups=JSON.parse(await fs.readFile(`${O}/MODELO_AGREGADO.json`,'utf8')).groups;
for(const [mode,key]of Object.entries(modes))for(const sec of ['Todos','Tecnologías','Administración y Comercio','Salud']){
 s.getRange('L4').values=[[mode]];s.getRange('C4').values=[['Cohortes 2024 y 2025']];s.getRange('H4').values=[[sec]];s.getRange('S4').values=[['Todas']];w.recalculate();
 const ix={'T1':14,'T2_records_observed':15,'T3_records_observed':16,'latest_snapshot_2026_VIGENTE':24}[key];
 const rows=groups.filter(r=>sec==='Todos'||r[4]===sec),n=rows.reduce((a,r)=>a+r[13],0),k=rows.reduce((a,r)=>a+r[ix],0);const val=s.getRange('C7:E7').values[0];
 if(val[0]!==n||val[1]!==k)throw Error('Sector selection mismatch '+JSON.stringify({sec,mode,n,k,val}));
 const sectorSum=s.getRange('H7:I9').values.reduce((a,r)=>[a[0]+(typeof r[0]==='number'?r[0]:0),a[1]+(typeof r[1]==='number'?r[1]:0)],[0,0]);
 if(sectorSum[0]!==n||sectorSum[1]!==k)throw Error('Level 2 disagrees');
 const careerSum=s.getRange('T7:U23').values.reduce((a,r)=>[a[0]+(typeof r[0]==='number'?r[0]:0),a[1]+(typeof r[1]==='number'?r[1]:0)],[0,0]);if(careerSum[0]!==n||careerSum[1]!==k)throw Error('Career view disagrees');
 controls.push({mode,sector:sec,denominator:n,numerator:k,connected:'PASS'});
 for(const career of [...new Set(rows.map(r=>r[2]))]){
  s.getRange('S4').values=[[career]];w.recalculate();const rr=rows.filter(r=>r[2]===career),nn=rr.reduce((a,r)=>a+r[13],0),kk=rr.reduce((a,r)=>a+r[ix],0),vv=s.getRange('C7:E7').values[0];if(vv[0]!==nn||vv[1]!==kk)throw Error('Career selection mismatch');
  controls.push({mode,sector:sec,career,denominator:nn,numerator:kk,connected:'PASS'});
 }
}
s.getRange('C4').values=[['Cohortes 2024 y 2025']];s.getRange('H4').values=[['Todos']];s.getRange('S4').values=[['Todas']];s.getRange('L4').values=[['Último respaldo']];w.recalculate();
await(await SpreadsheetFile.exportXlsx(w)).save(`${P}/public_candidate.xlsx`);
for(const [name,sheet,range]of [['ejecutiva','14_Vistas_Ejecutivas','B3:V31'],['desglose','12_Desglose_Jornada_Edad_Sexo','B3:H25'],['granular','13_Granular_Codigo_Unico','B3:L16'],['entradas','11_Entradas_Agregadas','A1:H12'],['portada','Portada','A1:F23']]){const img=await w.render({sheetName:sheet,range,scale:1,format:'png'});await fs.writeFile(`${P}/previews/${name}.png`,new Uint8Array(await img.arrayBuffer()));}
await fs.writeFile(`${O}/QA_FILTROS.json`,JSON.stringify({status:'OK',engine:'Artifact Tool local',controls},null,2)+'\n');
console.log('Public connected filters passed',controls.length);
// Private workbook: full trajectories, all enrolment observations and formula-backed aggregate bridge.
const p=Workbook.create();for(const name of ['Resumen','Trayectorias','Matriculas','Agregados','Fuentes'])p.worksheets.add(name);
function col(n){let z='';for(;n>0;n=Math.floor((n-1)/26))z=String.fromCharCode(65+(n-1)%26)+z;return z;}
function table(name,title,headers,rows,textcols=[]){const sh=p.worksheets.getItem(name);sh.showGridLines=false;const last=rows.length+5,cc=col(headers.length);sh.getRange(`A1:${cc}${last}`).format={font:{name:'Calibri',size:11,color:'#3A3A3A'},rowHeight:24,verticalAlignment:'center'};sh.mergeCells('A2:H2');sh.getRange('A2').values=[[title]];sh.getRange('A2').format.font={name:'Calibri',size:16,bold:true,color:'#102B42'};sh.getRange(`A5:${cc}5`).values=[headers];sh.getRange(`A6:${cc}${last}`).values=rows;const tt=sh.tables.add(`A5:${cc}${last}`,true,'T'+name);tt.showFilterButton=true;tt.style='TableStyleLight1';sh.getRange(`A5:${cc}5`).format={fill:'#0E4273',font:{name:'Calibri',size:11,bold:true,color:'#FFFFFF'},rowHeight:65,wrapText:true};sh.getRange(`A:${cc}`).format.columnWidth=22;for(const cc0 of textcols)sh.getRange(`${cc0}6:${cc0}${last}`).setNumberFormat('@');sh.freezePanes.freezeRows(5);return sh;}
const lastobs=d.observations.length+5,lp=d.persons.length+5;
const obs=table('Matriculas','Matrículas declaradas y respaldos observados B/C',['Persona C','ANOMATRICULA B','PERIODOMATRICULA B','RUT literal B','CODCLI literal B','CODCARPR B','Carrera B','ESTADOACADEMICO B','SITUACION B','FECHAMATRICULA literal B','NIVEL observado B','SEDE B','JORNADA B','FECH_CAR B','Fecha título disponible B','Fecha egreso disponible B','Referencias fuente/hoja/fila B','Fechas nominales B','Número respaldos C','Clasificación'],d.observations,['A','D','E','F','J','L','M','N','O','P']);obs.getRange('G:G').format.columnWidth=55;obs.getRange('Q:R').format.columnWidth=85;
const ph=['Persona C','Cohorte D','TIPO_DOC B','N_DOC original B','DV original B','CODCLI documentados B/C','Carrera de ingreso B','Código único B/C','Sector C','Semestre origen B','T1 control anual C','T2 listado C','T3 listado C','T2 VIGENTE observado B/C','T3 VIGENTE observado B/C','Última matrícula declarada C','Estados última matrícula B','Observaciones C','Llave pendiente E','2024-T1 declarado','2024-T2 declarado','2024-T3 declarado','2025-T1 declarado','2025-T2 declarado','2025-T3 declarado','2026-T1 declarado','2026-T2 declarado','2026-T3 declarado','Clasificación','Grupo agregado C','Listado 2025-T2 B','Listado 2025-T3 B','Listado 2026-T2 B','Listado 2026-T3 B','Localizado último respaldo B/C','2026 VIGENTE último respaldo B/C','Estados último respaldo B','Fecha nominal último respaldo B','Última observación nominal B','Última VIGENTE nominal B'];
const pp=table('Trayectorias','Trayectorias privadas de las cohortes 2024 y 2025',ph,d.persons,['A','C','D','E','F','H','AL','AM','AN']);pp.getRange('G:G').format.columnWidth=55;pp.getRange('P:Q').format.columnWidth=39;pp.getRange('AK:AN').format.columnWidth=40;
const pforms={};const addf=(cc,f)=>{if(!pforms[cc])pforms[cc]=[];pforms[cc].push([f]);};
for(let r=6;r<=lp;r++){
 addf('L',`=IF(B${r}=2024,AE${r},AG${r})`);addf('M',`=IF(B${r}=2024,AF${r},AH${r})`);addf('R',`=COUNTIFS('Matriculas'!$A$6:$A$${lastobs},A${r})`);
 for(const [j,[year,term]]of [[2024,1],[2024,2],[2024,3],[2025,1],[2025,2],[2025,3],[2026,1],[2026,2],[2026,3]].entries())addf(col(20+j),`=IF(COUNTIFS('Matriculas'!$A$6:$A$${lastobs},$A${r},'Matriculas'!$B$6:$B$${lastobs},${year},'Matriculas'!$C$6:$C$${lastobs},${term})>0,1,0)`);
 let formula='"Sin período UMAS localizado"';for(let j=0;j<9;j++){const year=2024+Math.floor(j/3),term=j%3+1;formula=`IF(${col(20+j)}${r}>0,"${year}-T${term}",${formula})`;}addf('P','='+formula);
}
for(const [cc,ff]of Object.entries(pforms))pp.getRange(`${cc}6:${cc}${lp}`).formulas=ff;
const gh=['Grupo C','Cohorte D','Código único B/C','Carrera B','Área B','Sector C','Sexo B','Modalidad B','Jornada B','Jornada real C','Tramo edad C','COD_CAR B','COD_SED B','VERSION B','Estudiantes C','T1 C','T2 C','T3 C','T2 VIGENTE observado C','T3 VIGENTE observado C','Llave pendiente E','Con matrícula declarada C','TITULADO última matrícula B/C','EGRESADO última matrícula B/C','Localizado último respaldo C','2026 VIGENTE último respaldo C','TITULADO último respaldo B/C','EGRESADO último respaldo B/C'];
const agg=table('Agregados','Puente de agregación sin doble conteo de personas',gh,d.groups.map((r,i)=>[d.group_ids[i],...r]),['A','C','L','M','N']);agg.getRange('D:D').format.columnWidth=55;
for(let i=0;i<d.groups.length;i++){const r=i+6;agg.getRange(`O${r}`).formulas=[[`=COUNTIFS('Trayectorias'!$AD$6:$AD$${lp},A${r})`]];for(const [dest,src]of [['P','K'],['Q','L'],['R','M'],['U','S'],['Y','AI'],['Z','AJ']])agg.getRange(`${dest}${r}`).formulas=[[`=SUMIFS('Trayectorias'!$${src}$6:$${src}$${lp},'Trayectorias'!$AD$6:$AD$${lp},A${r})`]];}
const src=table('Fuentes','Fuentes, procedencia y hashes B/C',['ID','Ruta','Hoja','SHA-256','Contexto','Bytes'],d.sources.map(s=>[s.id,s.path,s.sheet,s.sha256,s.context,s.bytes]),['A','D']);src.getRange('B:B').format.columnWidth=110;src.getRange('D:D').format.columnWidth=72;src.getRange('E:E').format.columnWidth=80;src.getRange(`B6:E${d.sources.length+5}`).format.wrapText=true;src.getRange(`A6:F${d.sources.length+5}`).format.rowHeight=65;
const summary=p.worksheets.getItem('Resumen');summary.showGridLines=false;summary.getRange('A1:H28').format={font:{name:'Calibri',size:11,color:'#3A3A3A'},rowHeight:29};summary.getRange('A:H').format.columnWidth=24;
function note(row,text){summary.mergeCells(`A${row}:H${row}`);summary.getRange(`A${row}`).values=[[text]];summary.getRange(`A${row}:H${row}`).format={wrapText:true,rowHeight:50};}
note(2,'Seguimiento privado: ingreso, matrículas declaradas y última observación');summary.getRange('A2').format.font={name:'Calibri',size:16,bold:true,color:'#102B42'};
note(3,'D: archivo privado con identificadores. No subir a Git ni a servicios externos. Filtre Persona para revisar todas sus matrículas y fuentes. No se modifican denominadores.');
summary.getRange('A5:H5').values=[['Cohorte D','Estudiantes C/D','T1 anual C','T2 listado C','T3 listado C','Último respaldo 2026 VIGENTE C','Tasa formal T2 E','Tasa formal T3 E']];summary.getRange('A5:H5').format={fill:'#0E4273',font:{name:'Calibri',size:11,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:65};
for(const [r,y]of [[6,2024],[7,2025]]){summary.getRange(`A${r}`).values=[[y]];summary.getRange(`B${r}`).formulas=[[`=COUNTIFS('Trayectorias'!$B$6:$B$${lp},A${r})`]];for(const [dest,ss]of [['C','K'],['D','L'],['E','M'],['F','AJ']])summary.getRange(`${dest}${r}`).formulas=[[`=SUMIFS('Trayectorias'!$${ss}$6:$${ss}$${lp},'Trayectorias'!$B$6:$B$${lp},A${r})`]];summary.getRange(`G${r}:H${r}`).values=[['Pendiente','Pendiente']];}
note(10,'B/C: PERIODOMATRICULA describe la matrícula declarada. No identifica por sí solo el último período cursado. La presencia en un cierre se obtiene del listado correspondiente; las fechas de extracción y el estado observado se conservan aparte.');
note(12,'C/E: Última matrícula declarada muestra el máximo año/período localizado, no avance académico ni abandono. Última observación nominal indica la fecha nominal del respaldo, no fecha efectiva de cambio del estado.');
note(14,'B/C: Último respaldo usa Base Maestra nominal 21-oct-2026. Su cobertura difiere de DatosAlumnos; solo cuenta VIGENTE con ANOMATRICULA=2026. No sustituye a los cierres T2/T3.');
note(16,'E: dos CODCLI pendientes. TITULADO/EGRESADO no se convierte automáticamente en desertor; falta acreditar programa y fecha para otra regla interna. Se mantienen 558 y 1.150.');
note(18,'C: los agregados se concilian con las fórmulas de Trayectorias y alimentan el libro de presentación. Las columnas AE:AN conservan evidencias observadas de fuentes y períodos; no son decisiones nuevas de elegibilidad.');
note(20,'A definición oficial; B observado; C implementación/cálculo; D decisión interna; E pendiente. Recálculo local con Artifact Tool; Excel nativo no certificado.');
p.recalculate();for(const [i,y]of [2024,2025].entries()){const actual=summary.getRange(`B${i+6}:F${i+6}`).values[0],v=c.control[String(y)],expected=[v.denominator,v.T1,v.T2_records_observed,v.T3_records_observed,v.latest_snapshot_2026_VIGENTE];if(JSON.stringify(actual)!==JSON.stringify(expected))throw Error('Private reconciliation failed '+JSON.stringify(actual));}
await(await SpreadsheetFile.exportXlsx(p)).save(`${P}/TRAYECTORIAS_PRIVADAS_IPSS_20261021_153436.xlsx`);
const img=await p.render({sheetName:'Resumen',range:'A1:H20',scale:1,format:'png'});await fs.writeFile(`${P}/previews/privado_resumen.png`,new Uint8Array(await img.arrayBuffer()));
console.log('Private and public candidates exported; formulas and controls passed.');
