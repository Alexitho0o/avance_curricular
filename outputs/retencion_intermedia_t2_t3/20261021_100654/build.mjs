import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const tmp='/tmp/ipss_escenario80_20261021_100204';
const root='/Users/alexi/Documents/GitHub/avance_curricular';
const base=`${root}/outputs/retencion_intermedia_t2_t3/20261021_085902/RETENCION_INTERMEDIA_IPSS_PRESENCIAS_Y_PENDIENTES_20261021_085902.xlsx`;
const jp=`${root}/outputs/retencion_intermedia_t2_t3/20261021_095123_escenario_80/RESULTADOS_ESCENARIO_AGREGADOS.json`;
const j=JSON.parse(await fs.readFile(jp,'utf8'));
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(base));
const s=w.worksheets.add('Escenario_80');
s.showGridLines=false; s.tabColor='#CFB47C';
s.getRange('A1:H88').format.font={name:'Arial',size:11,color:'#3A3A3A'};
s.getRange('A1:H88').format.verticalAlignment='center';
s.getRange('A1:H88').format.rowHeight=25;
const widths={A:32,B:19,C:19,D:20,E:20,F:20,G:20,H:20};
for(const [c,width] of Object.entries(widths))s.getRange(`${c}:${c}`).format.columnWidth=width;
function v(cell,x){s.getRange(cell).values=[[x]];}
function f(cell,x){s.getRange(cell).formulas=[[x]];}
function merged(range,text,fill=null,height=30){s.mergeCells(range);v(range.split(':')[0],text);s.getRange(range).format.wrapText=true;s.getRange(range).format.rowHeight=height;if(fill)s.getRange(range).format.fill=fill;}
function section(row,text){merged(`A${row}:H${row}`,text,'#102B42',28);s.getRange(`A${row}:H${row}`).format.font={name:'Arial',size:11,bold:true,color:'#FFFFFF'};}
function header(row,values){s.getRange(`A${row}:H${row}`).values=[values];s.getRange(`A${row}:H${row}`).format={fill:'#0E4273',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:44,horizontalAlignment:'center',verticalAlignment:'center'};}
function stripe(a,b){for(let r=a;r<=b;r++){if((r-a)%2===0)s.getRange(`A${r}:H${r}`).format.fill='#F2F2F2';}}
merged('A2:H2','Escenario de los 80 ingresos reclasificados',null,34);
s.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:'#102B42'};
merged('A3:H3','Institucional completo, cohortes 2024 y 2025. C/D: no responde al selector de carrera de Resumen. Resultados actuales conservados. Fecha: 21-10-2026.',null,28);
merged('A4:H4','E: hipótesis aislada: cambiar solo ANIO_ING_ACT y ANIO_ING_ORI de 2025 a 2024 en las 80 filas MU2025. Se conservan los semestres informados, VIG, programas, MU2024 y MU2026. No es una corrección aprobada.','#FFF2CC',52);
section(6,'Comparación anual: cálculo actual (C) y simulación separada (C/E)');
header(7,['Cohorte','Estudiantes actuales (C)','Retenidos actuales (C)','Tasa actual (C)','Estudiantes simulados (C/E)','Retenidos simulados (C/E)','Tasa simulada (C/E)','Cambio (pp, C/E)']);
for(let i=0;i<2;i++){
 const r=8+i;v(`A${r}`,j.resultados[i].cohorte);
 f(`B${r}`,`=SUMIFS('Por_carrera'!$D$7:$D$34,'Por_carrera'!$A$7:$A$34,A${r})`);
 f(`C${r}`,`=E${40+i}`);f(`D${r}`,`=IF(B${r}=0,"Pendiente",C${r}/B${r})`);
 f(`E${r}`,i===0?`=B${r}+E38`:`=B${r}-E33`);
 f(`F${r}`,i===0?`=C${r}+E39`:`=C${r}-E34`);
 f(`G${r}`,`=IF(E${r}=0,"Pendiente",F${r}/E${r})`);f(`H${r}`,`=(G${r}-D${r})*100`);
}
stripe(8,9);s.getRange('E8:H9').format.fill='#FFF2CC';
merged('A11:H11','D/E: 560 y 1.123 son universos hipotéticos de esta hoja. No sustituyen los denominadores actuales 558 y 1.150, ni los denominadores separados de ingresos T2=222 y T3=124.',null,40);
section(12,'Comparación con SIES: brecha = tasa propia menos tasa publicada');
header(13,['Cohorte','Tasa SIES observada (B)','Brecha actual (pp, C)','Brecha simulada (pp, C/E)','Lectura','','','']);
for(let i=0;i<2;i++){
 const r=14+i, a=8+i;v(`A${r}`,2024+i);v(`B${r}`,j.resultados[i].referencia_SIES_B);
 f(`C${r}`,`=(D${a}-B${r})*100`);f(`D${r}`,`=(G${a}-B${r})*100`);
 merged(`E${r}:H${r}`,i===0?'C/E: mejora solo una parte pequeña de la brecha. La causa restante sigue pendiente.':'C/E: la simulación queda por encima de SIES. Acercarse al dato no valida la hipótesis.',null,42);
}
section(17,'Control: seguimiento de la misma población actual, sin cambiar denominadores');
header(18,['Cohorte','Estudiantes actuales (C)','Retenidos actuales (C)','Tasa actual (C)','Tasa misma población (C/E)','Cambio (pp, C/E)','Estado (D)','',''].slice(0,8));
for(let i=0;i<2;i++){
 const r=19+i,a=8+i;v(`A${r}`,2024+i);f(`B${r}`,`=B${a}`);f(`C${r}`,`=C${a}`);f(`D${r}`,`=D${a}`);f(`E${r}`,`=C${r}/B${r}`);f(`F${r}`,`=(E${r}-D${r})*100`);merged(`G${r}:H${r}`,'Sin cambio de población',null,30);
}
merged('A22:H22','C/E: el escenario evalúa retención anual MU2024→MU2025 y MU2025→MU2026. Las tasas de los cierres T2/T3 siguen pendientes de acreditar fecha, cobertura y estados. Los 53 VIG=1 no se añaden automáticamente al numerador.','#FFF2CC',52);
section(24,'Cómo se construye: entradas agregadas del cruce ya verificado');
const inputs=[
 ['Marca 2+3 INGRESO',j.marcas['2+3 INGRESO'],'B · respaldo de preparación MU2025'],
 ['Marca CORRECCIÓN',j.marcas['CORRECCIÓN'],'B · respaldo de preparación MU2025'],
 ['Población del escenario',null,'C · suma de las dos marcas'],
 ['Con al menos una fila VIG=1 en MU2026',j.cruce_MU2026.CON_VIG1,'B · cruce exacto de persona'],
 ['En MU2026 solo con VIG=0',j.cruce_MU2026.SOLO_VIG0,'B · sin fila VIG=1'],
 ['Sin fila en MU2026',j.cruce_MU2026.AUSENTE_MU2026,'B · ausencia en esta extracción'],
 ['Total clasificado en MU2026',null,'C · suma de las tres situaciones'],
 ['De los 80, incluidos actualmente en cohorte 2025',j.aporte_actual_2025.N,'C · no se descuentan los 80'],
 ['Retenidos actuales aportados por esos incluidos',j.aporte_actual_2025.R,'C · cálculo actual'],
 ['Ya excluidos por COHORTE_INCONSISTENTE en 2025',j.estado_actual_2025.COHORTE_INCONSISTENTE,'C · proxy de exclusión D/E'],
 ['Con fila MU2024; pasarían a incluidos y retenidos',j.presencia_MU2024.CON_FILA_MU2024,'B: 2 filas · C/E: efecto simulado'],
 ['Sin fila en MU2024',j.presencia_MU2024.SIN_FILA_MU2024,'B · no se crean filas faltantes'],
 ['Estudiantes que se sumarían a cohorte 2024',null,'C/E · solo las dos filas existentes'],
 ['Retenidos que se sumarían a cohorte 2024',null,'C/E · transición simulada ya evaluada'],
 ['Retenidos actuales de la cohorte 2024',j.resultados[0].actual_C.R,'C · motor anual conservado'],
 ['Retenidos actuales de la cohorte 2025',j.resultados[1].actual_C.R,'C · motor anual conservado'],
];
for(let i=0;i<inputs.length;i++){const r=26+i;merged(`A${r}:D${r}`,inputs[i][0],i%2===0?'#F2F2F2':null,28);if(inputs[i][1]!==null)v(`E${r}`,inputs[i][1]);merged(`F${r}:H${r}`,inputs[i][2],null,28);}
f('E28','=SUM(E26:E27)');f('E32','=SUM(E29:E31)');f('E38','=E36');f('E39','=E36');
s.getRange('E26:E41').setNumberFormat('#,##0');
section(43,'Los 80 estudiantes por programa de MU2025 (B: observaciones agregadas)');
header(44,['Código único','Carrera','','','Estudiantes (B)','VIG 1 MU2026 (B)','Solo VIG 0 (B)','Ausentes MU2026 (B)']);
for(let i=0;i<j.por_programa.length;i++){
 const r=45+i,p=j.por_programa[i];v(`A${r}`,p.codigo_unico);merged(`B${r}:D${r}`,p.carrera,null,38);s.getRange(`E${r}:H${r}`).values=[[p.personas_reclasificadas,p.VIG1_MU2026,p.VIG0_MU2026,p.ausente_MU2026]];
}
stripe(45,51);v('A52','Total (C)');for(const c of ['E','F','G','H'])f(`${c}52`,`=SUM(${c}45:${c}51)`);s.getRange('A52:H52').format.fill='#F2F2F2';s.getRange('A52:H52').format.font.bold=true;
section(54,'Controles de conciliación (C): todos deben resultar 0');
const checks=[['Total programas menos población del escenario','=E52-E28'],['Suma estados MU2026 menos total programas','=SUM(F52:H52)-E52'],['Incluidos 2025 menos VIG0 y ausentes','=E33-SUM(E30:E31)'],['Excluidos 2025 más incluidos menos población','=SUM(E33,E35)-E28'],['Con y sin fila MU2024 menos población','=SUM(E36:E37)-E28']];
checks.forEach(([l,formula],i)=>{const r=55+i;merged(`A${r}:D${r}`,l);f(`E${r}`,formula);});
s.getRange('E55:E59').conditionalFormats.add('cellIs',{operator:'notEqual',formula:0,format:{fill:'#FCE4D6',font:{color:'#9C0006',bold:true}}});
section(61,'Pendientes que siguen abiertos (E)');
const pending=[
 'E: falta la regla o consulta original y su autorización para explicar por qué se asignó origen 2025 a estos ingresos 2024. El respaldo muestra el cambio, pero no acredita su causa.',
 'E: el semestre de origen correcto sigue sin resolverse. La simulación conserva el semestre informado en MU2025; no supone equivalencia entre T2/T3 y semestre SIES.',
 'B/E: 78 de los 80 no tienen fila en MU2024. No se pueden incorporar retrospectivamente a esa base sin una fuente individual verificable y una decisión separada.',
 'D/E: COHORTE_INCONSISTENTE es un proxy del motor interno. No reproduce necesariamente la selección de casos específicos que hace SIES.',
 'E: los cierres intermedios T2/T3 mantienen los pendientes de Bases_por_confirmar. Este escenario no acredita cobertura ni transforma ausencias en deserción.',
];
pending.forEach((t,i)=>merged(`A${62+i}:H${62+i}`,t,'#FFF2CC',44));
merged('A68:H68','Clases: A definición oficial · B dato observado · C cálculo/implementación · D decisión interna · E hipótesis o pendiente.',null,28);
section(70,'Fuentes y trazabilidad de esta hoja');
const sources=[
 ['C: insumos y transiciones del escenario',jp,'4a4f0f7183d4a1bcff507085399920cbaa3e37c5829bf2d11ced58ef38d0681c'],
 ['C: informe del escenario ya calculado',jp.replace('RESULTADOS_ESCENARIO_AGREGADOS.json','ESCENARIO_80_RECLASIFICACION_RETENCION.md'),'bf608c36bca663223a65ac29e5cbda11dd3a6111c202d5526f6ae184bc8c1f48'],
 ['C: motor anual; hojas BASE_RETENCION_MU y 02_COHORTE_ELEGIBILIDAD',j.fuentes[6].ruta,j.fuentes[6].sha256],
 ['B: referencia SIES; Retención 1er año x IES!T59:U59; IPSS=162',j.fuentes[7].ruta,j.fuentes[7].sha256],
 ['D/C: libro intermedio anterior; se conservan sus cuatro hojas',base,'340f9a2126973e0ab3a11172eaa525935ab5991c8ad10dcdb321cc721d0b8e69'],
];
sources.forEach(([label,path,hash],i)=>{const r=71+i*3;merged(`A${r}:H${r}`,label,'#F2F2F2',25);merged(`A${r+1}:H${r+1}`,path,null,36);merged(`A${r+2}:H${r+2}`,`SHA-256: ${hash}`,null,25);});
// Counts and codes remain typed; Excel applies the viewer's locale.
for(const range of ['B8:C9','E8:F9','B19:C20','E45:H52','E55:E59'])s.getRange(range).setNumberFormat('#,##0');
for(const range of ['D8:D9','G8:G9','B14:B15','D19:E20'])s.getRange(range).setNumberFormat('0.00%');
for(const range of ['H8:H9','C14:D15','F19:F20'])s.getRange(range).setNumberFormat('+0.00;-0.00;0.00');
s.getRange('A8:A20').setNumberFormat('0');
s.freezePanes.freezeRows(7);
// Disposable input checks; restore both aggregate inputs before final calculation.
v('E36',0);
if(s.getRange('E8').values[0][0]!==558||s.getRange('F8').values[0][0]!==326)throw new Error('2024 sensitivity does not update');
v('E36',j.presencia_MU2024.CON_FILA_MU2024);
v('E33',0);
if(s.getRange('E9').values[0][0]!==1150)throw new Error('2025 sensitivity does not update');
v('E33',j.aporte_actual_2025.N);
w.recalculate();
const result=await w.inspect({kind:'table',range:'Escenario_80!A7:H20',include:'values,formulas',tableMaxRows:14,tableMaxCols:8,maxChars:4500});
await fs.writeFile(`${tmp}/inspect.txt`,result.ndjson);
const err=await w.inspect({kind:'match',range:'Escenario_80!A1:H86',sheetId:'Escenario_80',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:50},maxChars:2500});
console.log(err.ndjson);
for(const [name,range] of [['resumen','A1:H22'],['entradas','A24:H59'],['pendientes','A61:H86']]){
 const img=await w.render({sheetName:'Escenario_80',range,scale:1,format:'png'});
 await fs.writeFile(`${tmp}/${name}.png`,new Uint8Array(await img.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(w)).save(`${tmp}/candidate.xlsx`);
console.log('Exported candidate; existing package parts will be preserved byte-for-byte.');
