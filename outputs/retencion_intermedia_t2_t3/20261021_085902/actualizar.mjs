import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const dir=path.dirname(fileURLToPath(import.meta.url));
const root='/Users/alexi/Documents/GitHub/avance_curricular';
const car='/Users/alexi/Documents/GitHub/CARACTERIZACIÓN';
const src=root+'/outputs/retencion_intermedia_t2_t3/20261021_013430/REVISION_RETENCION_INTERMEDIA_IPSS_2024_2025_20261021.xlsx';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(src));
const s=wb.worksheets.getItem('Resumen'),p=wb.worksheets.getItem('Por_carrera'),f=wb.worksheets.getItem('Fuentes_y_alcance');
async function render(name,range,file){const b=await wb.render({sheetName:name,range,scale:1,format:'png'});await fs.writeFile(path.join(dir,file),new Uint8Array(await b.arrayBuffer()));}
if(process.argv.includes('--preview')){await render('Resumen','A1:I15','antes.png');console.log((await wb.inspect({kind:'region',sheetId:'Resumen',range:'A7:I11',maxChars:2500})).ndjson);process.exit(0);}
const before=JSON.stringify(p.getRange('A7:K34').values);
const expected=[[558,1,1,0,557],[558,325,317,0,233],[1150,2,'Sin estado',20,1128],[1150,0,0,20,1130]];
const put=(sh,cell,text)=>sh.getRange(cell).values=[[text]];
put(s,'A5','E: cobertura al cierre no acreditada. Se muestran presencias comprobadas; las tasas intermedias siguen pendientes.');
const pending=[
'E: falta una base completa de 2025-T2 que incluya la cohorte 2024. La entrega solo contiene ingresos 2025-T2.',
'E: T3_2025 incluye varias cohortes. Falta acreditar completitud y fecha efectiva del estado. No se exige otro archivo si este se confirma.',
'E: DatosAlumnos_10246 está congelado para Caracterización P2. Falta acreditar que representa todo el cierre 2026-T2 y sus estados.',
'E: DatosAlumnos_11998 es una fuente común de P1/P2/P3. Falta acreditar fecha y cobertura del cierre 2026-T3.'
];
for(let i=0;i<4;i++){put(s,`I${8+i}`,pending[i]);put(s,`H${8+i}`,'Pendiente');}
s.getRange('A8:I11').format.rowHeight=94;
put(s,'A13','D/C: se conservan 558 y 1.150 estudiantes de referencia. No se cambian elegibilidad ni denominadores.');
put(s,'A14','B/E: presencia y estado describen el archivo recibido; no certifican vigencia al cierre sin evidencia temporal.');
put(s,'A27','Próximo paso: revisar Bases_por_confirmar. Usar fuentes existentes si se acredita fecha, cobertura y estados del cierre.');
put(s,'A29','C: MU2024 identifica la cohorte 2024; MU2025 permite observar su continuidad y definir la cohorte 2025.');
put(s,'A30','C: MU2026 permite observar continuidad de la cohorte 2025. Ninguna MU anual sustituye por sí sola un cierre T2/T3.');
put(s,'A31','E: que la MU siguiente incluya todos los ingresos T1/T2/T3 previos es una hipótesis a comprobar, no una cobertura demostrada.');
put(p,'A4','B/C: se conservan los conteos del cruce verificado. E: tasas pendientes hasta acreditar fecha y cobertura de los cierres.');
put(p,'A39','E: cobertura no acreditada no significa pérdida de datos demostrada. Los ceros indican ausencia en el archivo consultado.');
put(f,'A20','D/B: el usuario describió las entregas como parciales. Se revisaron respaldos existentes antes de solicitar más bases.');
put(f,'A22','E: verificar período de ingreso UMAS frente a semestre de origen SIES. No asumir equivalencia T1/T2/T3 = semestre 1/2.');
put(f,'A25','C: actualización de alcance y fuentes. Conteos originales y fórmulas de seguimiento conservados.');
const sources=[
['B','DatosAlumnos_10246 / Hoja1','14.204 registros; respaldo P2','b175d63bd9e3280c5757fb0d7292e45fb594d8f076e277f2e06bad2b15e9d869',car+'/.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/DATOSDEALUMNOS_10246.xlsx','Congelado 22-07-2026; no acredita cierre'],
['B','Fuentes congeladas 2026-P2','Corrida 21-07; congelamiento 22-07',null,car+'/docs/gobernanza/FUENTES_CONGELADAS_2026_P2.json','Metadatos de gobernanza'],
['B','DatosAlumnos_11998 / Hoja1','15.045 registros; mismo archivo P1/P2/P3','5d2df5e7998a4ec903e12d51b25114e8f1ff36da57cecaf623e90398b0828f35',car+'/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/DATOSDEALUMNOS_11998.xlsx','Usado 15-10-2026; extracción no acreditada'],
['B','Inventario histórico SIES/UMAS','Documenta ausencia de fecha de extracción',null,root+'/data/versiones_historicas_sies_umas/fase_1_20261015/inventario.json','No convertir años observados en cierres'],
['B','Manifest ejecución P3','Fecha de ejecución y fuente utilizada',null,car+'/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/04_AUDITORIA/manifest_ejecucion.json','15-10-2026; no certifica estado histórico'],
['B','Manifest BASE_RETENCION_MU','Fuentes anuales 2024, 2025 y 2026 disponibles',null,root+'/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/MANIFEST_BASE_RETENCION_MU_2022_2026.json','No falta la base anual 2024'],
['C','Libro de revisión previo','Presencias conservadas y procedencia',null,src,'No se recalcula el cruce individual']
];
for(const x of sources){const hash=crypto.createHash('sha256').update(await fs.readFile(x[4])).digest('hex');if(x[3]&&x[3]!==hash)throw Error('Hash cambiado '+x[1]);x[3]=hash;}
f.getRange('A34:F34').copyFrom(f.getRange('A6:F6'),'all');
f.getRange('A35:F41').values=sources;f.getRange('A35:F41').format={font:{name:'Arial',size:11,color:'#3A3A3A'},wrapText:true,rowHeight:90,verticalAlignment:'center'};
const b=wb.worksheets.add('Bases_por_confirmar');b.showGridLines=false;b.tabColor='#CFB47C';
b.getRange('A1:F18').format={font:{name:'Arial',size:11,color:'#3A3A3A'},rowHeight:28,verticalAlignment:'center'};
put(b,'A2','Bases de cierre: disponible y pendiente');b.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:'#102B42'};
put(b,'A4','B: fuentes revisadas. E: falta acreditar cobertura o fecha; esto no demuestra que falten estudiantes.');
const head=['Cierre','Cohorte','Base disponible (B)','Fecha acreditada (B)','Qué confirmar (E)','Qué falta resolver'];
b.getRange('A6:F6').values=[head];b.getRange('A6:F6').format={fill:'#102B42',font:{name:'Arial',size:11,color:'#FFFFFF',bold:true},wrapText:true,rowHeight:42,horizontalAlignment:'center'};
b.getRange('A7:F10').values=[
['2025-T2',2024,'Archivo recibido: 225 registros, todos ingresos 2025-T2.','No acredita fecha efectiva del cierre.','Matrícula de todas las cohortes y estados al cierre, incluida cohorte 2024.','Falta base completa acreditada.'],
['2025-T3',2024,'T3_2025: 3.081 registros de varias cohortes; 500 con ingreso 2024.','Propiedades: creado 13-10-2025; modificado 20-10-2026. No son prueba del corte.','Completitud de la hoja y fecha efectiva de sus estados académicos.','Puede bastar confirmar el archivo existente.'],
['2026-T2',2025,'DatosAlumnos_10246: 14.204 registros. Fuente congelada de Caracterización P2.','Corrida 21-07-2026; congelado 22-07-2026. Sin fecha de extracción acreditada.','Si incluye toda la matrícula del cierre y si el estado corresponde a ese cierre.','Candidato localizado; cobertura temporal pendiente.'],
['2026-T3',2025,'DatosAlumnos_11998: 15.045 registros. Mismo archivo usado en P1, P2 y P3.','Ejecución 15-10-2026; fecha de extracción no acreditada.','Cobertura completa al cierre T3, incluidos ingresos de períodos 1 y 2.','Candidato localizado; no son tres cierres históricos.']
];
b.getRange('A7:F10').format.wrapText=true;b.getRange('A7:F10').format.rowHeight=110;b.getRange('E7:F10').format.fill='#FFF2CC';
b.getRange('B7:B10').format.horizontalAlignment='center';
b.tables.add('A6:F10',true,'BasesCierrePorConfirmar').style='TableStyleLight1';
for(const [c,w] of [['A',14],['B',12],['C',47],['D',45],['E',45],['F',37]])b.getRange(`${c}1:${c}18`).format.columnWidth=w;
put(b,'A12','C: no reemplazar la cohorte 2024 por quienes aparecen en MU2025; eso cambiaría el denominador.');
put(b,'A13','B: la base consolidada ya contiene matrícula informada de 2024, 2025 y 2026.');
put(b,'A14','E: MU2027 es una comprobación futura. No dar por confirmada su cobertura de ingresos 2026.');
put(b,'A15','C: las bases candidatas no se han usado para sumar presencias nuevas ni para sustituir cierres.');
put(b,'A16','D: denominadores conservados: 558 / 1.150 y, en el ejercicio separado, 222 / 124.');
put(b,'A18','Referencias, rutas y hashes: Fuentes_y_alcance, filas 35 a 41.');
if(JSON.stringify(p.getRange('A7:K34').values)!==before)throw Error('Detalle alterado');
const detail=p.getRange('A7:I34').values,careers=['Todas',...new Set(detail.map(r=>r[1]))];
for(const career of careers){
 s.getRange('H4').values=[[career]];
 const exp=[[2024,2],[2024,3],[2025,2],[2025,3]].map(([year,term])=>{
  const rows=detail.filter(r=>r[0]===year&&(career==='Todas'||r[1]===career));
  const sum=i=>rows.reduce((a,r)=>a+r[i],0),den=sum(3),found=sum(term===2?5:7),noKey=sum(4);
  return [den,found,year===2025&&term===2?'Sin estado':sum(term===2?6:8),noKey,den-found-noKey];
 });
 if(JSON.stringify(s.getRange('C8:G11').values)!==JSON.stringify(exp))throw Error('Filtro cambió: '+career);
}
s.getRange('H4').values=[['Todas']];wb.recalculate();
if(JSON.stringify(s.getRange('C8:G11').values)!==JSON.stringify(expected))throw Error('Controles cambiaron');
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30}});
await fs.writeFile(path.join(dir,'qa_formulas.ndjson'),errors.ndjson);
await render('Resumen','A1:I15','Resumen.png');await render('Bases_por_confirmar','A1:F18','Bases_por_confirmar.png');await render('Fuentes_y_alcance','A34:F41','Fuentes_nuevas.png');
const file=path.join(dir,'RETENCION_INTERMEDIA_IPSS_PRESENCIAS_Y_PENDIENTES_20261021_085902.xlsx');await(await SpreadsheetFile.exportXlsx(wb)).save(file);
await fs.writeFile(path.join(dir,'evidencia_actualizacion.json'),JSON.stringify({fecha:new Date().toISOString(),fuentes:sources,origen:src,salida:file,controles:s.getRange('C8:H11').values,continuidad:s.getRange('B21:G22').values,denominadores:[558,1150,222,124],recalculo:'artifact-tool; Excel nativo no probado',clasificacion:'B/C/D/E',tasas_intermedias:'Pendientes',cruce_nuevo:false},null,2));
console.log(file);
