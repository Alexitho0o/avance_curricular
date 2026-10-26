import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile}from '@oai/artifact-tool';
const R='/Users/alexi/Documents/GitHub/avance_curricular',O=`${R}/outputs/retencion_intermedia_t2_t3/20261021_153436`,P=`${R}/.local_restricted/retencion_intermedia/20261021_153436`;
const d=JSON.parse(await fs.readFile(`${P}/datos.json`,'utf8')),model=JSON.parse(await fs.readFile(`${O}/MODELO_AGREGADO.json`,'utf8'));
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(`${P}/public_candidate.xlsx`));
const granular=w.worksheets.getItem('13_Granular_Codigo_Unico');
for(let r=51+new Set(model.groups.map(x=>x[0]+'|'+x[1])).size;r<=135;r++){granular.getRange(`F${r}:G${r}`).formulas=[['=""','=""']];}
w.worksheets.getItem('5_Evolucion').getRange('B13:G13').clear({applyTo:'contents'});w.worksheets.getItem('5_Evolucion').getRange('B15:F35').clear({applyTo:'contents'});w.worksheets.getItem('5_Evolucion').getRange('B37:G40').clear({applyTo:'contents'});
for(const [sheet,addr,text]of [['Portada','B18','5. Evolución y última matrícula declarada'],['Portada','C8','2024: 558 estudiantes; 2025: 1.150. Seguimiento T1/T2/T3.'],['Portada','C10','NO. Solo agregados; detalle individual en el Excel privado.'],['Portada','C11','Uso interno IPSS. Cierres formales T2/T3 pendientes.'],['4_Resultados_Sector','A1','4. Continuidad documentada por sector — cohortes 2024 y 2025'],['12_Desglose_Jornada_Edad_Sexo','A1','12. Seguimiento por jornada, edad y sexo'],['14_Vistas_Ejecutivas','AS5','Vista — mayores y menores porcentajes documentados'],['5_Evolucion','B3','C: comparación de cohortes según el seguimiento de la hoja 14. Desde la fila 43, distribución de la última matrícula declarada localizada. E: no equivale al último período cursado ni a una fecha de retiro.']])w.worksheets.getItem(sheet).getRange(addr).values=[[text]];
for(const addr of ['M7','M12'])w.worksheets.getItem('14_Vistas_Ejecutivas').getRange(addr).formulas=[['=$C$4']];
const buckets=['2026-T3','2026-T2','2026-T1','2025-T3','2025-T2','2025-T1','2024-T3','2024-T2','2024-T1','Sin período UMAS localizado'];
const data=d.group_ids.map(group=>buckets.map(bucket=>d.persons.filter(p=>p[29]===group&&p[15]===bucket).length));
const inp=w.worksheets.getItem('11_Entradas_Agregadas'),last=d.groups.length+4;
inp.getRange(`AB4:AK${last}`).values=[buckets.map(x=>'Última matrícula '+x+' C'),...data];
inp.getRange(`AB4:AK${last}`).format={font:{name:'Calibri',size:11,color:'#3A3A3A'},verticalAlignment:'center'};inp.getRange('AB:AK').format.columnWidth=22;inp.getRange('AB4:AK4').format={fill:'#0E4273',font:{name:'Calibri',size:11,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:65};
const s=w.worksheets.getItem('5_Evolucion');s.mergeCells('B43:G43');s.getRange('B43').values=[['Última matrícula declarada localizada — selección de hoja 14']];s.getRange('B43:G43').format={font:{name:'Calibri',size:11,bold:true,color:'#102B42'},rowHeight:33};
for(const [r,rate]of [[7,0.675],[8,0.582115219260533]])s.getRange(`F${r}`).formulas=[[`=IF(AND('14_Vistas_Ejecutivas'!$L$4="T1 anual MU",'14_Vistas_Ejecutivas'!$H$4="Todos",'14_Vistas_Ejecutivas'!$S$4="Todas"),${rate},"")`]];
s.getRange('B45:F45').values=[['Cohorte','Matrícula declarada','Estudiantes','Cohorte seleccionada','Proporción (%)']];s.getRange('B45:F45').format={fill:'#0E4273',font:{name:'Calibri',size:11,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:47};
for(let i=0;i<20;i++){
 const r=i+46,y=i<10?2024:2025,j=i%10;
 // AB..AK are the ten source columns.
 const source=['AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK'][j];
 s.getRange(`B${r}:C${r}`).values=[[y,buckets[j]==='Sin período UMAS localizado'?'Sin período':buckets[j]]];
 const selection=`IF(OR('14_Vistas_Ejecutivas'!$C$4="Cohortes 2024 y 2025",'14_Vistas_Ejecutivas'!$C$4="Cohorte ${y}"),1,0)`;
 const crit=`'11_Entradas_Agregadas'!$A$5:$A$${last},B${r},'11_Entradas_Agregadas'!$E$5:$E$${last},'14_Vistas_Ejecutivas'!$BO$12,'11_Entradas_Agregadas'!$C$5:$C$${last},'14_Vistas_Ejecutivas'!$BO$13`;
 s.getRange(`D${r}`).formulas=[[`=${selection}*SUMIFS('11_Entradas_Agregadas'!$${source}$5:$${source}$${last},${crit})`]];
 s.getRange(`E${r}`).formulas=[[`=${selection}*SUMIFS('11_Entradas_Agregadas'!$N$5:$N$${last},${crit})`]];
 s.getRange(`F${r}`).formulas=[[`=IF(E${r}=0,"",D${r}/E${r})`]];
 s.getRange(`B${r}:F${r}`).format={font:{name:'Calibri',size:11,color:'#3A3A3A'},fill:i%2===0?'#F2F2F2':'#FFFFFF',rowHeight:24};
}
s.getRange('F46:F65').setNumberFormat('0.0%');s.mergeCells('B67:G70');s.getRange('B67').values=[['B/C: esta distribución responde a cohorte, sector y carrera. Es el último año/período de matrícula que aparece en las fuentes; no acredita último período cursado, fecha de retiro ni avance curricular. Un respaldo posterior puede conservar una matrícula anterior. El detalle privado muestra la secuencia y las fechas de observación por separado.']];s.getRange('B67:G70').format={font:{name:'Calibri',size:10,color:'#3A3A3A'},wrapText:true,verticalAlignment:'center'};
s.getRange('B46:C65').format.horizontalAlignment='center';s.getRange('D46:E65').setNumberFormat('#,##0');
w.recalculate();const n=s.getRange('D46:D65').values.reduce((a,r)=>a+(typeof r[0]==='number'?r[0]:0),0);if(n!==1708)throw Error('Latest declared enrolment does not reconcile');
for(const sec of ['Tecnologías','Administración y Comercio','Salud']){w.worksheets.getItem('14_Vistas_Ejecutivas').getRange('H4').values=[[sec]];w.recalculate();const n=s.getRange('D46:D65').values.reduce((a,r)=>a+(typeof r[0]==='number'?r[0]:0),0);const expected=model.groups.filter(r=>r[4]===sec).reduce((a,r)=>a+r[13],0);if(n!==expected)throw Error('Trajectory sector filter failed');}
w.worksheets.getItem('14_Vistas_Ejecutivas').getRange('H4').values=[['Todos']];w.recalculate();
await(await SpreadsheetFile.exportXlsx(w)).save(`${P}/public_candidate.xlsx`);
const img=await w.render({sheetName:'5_Evolucion',range:'B43:G70',scale:1,format:'png'});await fs.writeFile(`${P}/previews/trayectoria_agregada.png`,new Uint8Array(await img.arrayBuffer()));
await fs.writeFile(`${O}/QA_TRAYECTORIA.json`,JSON.stringify({status:'OK',people_reconciled:n,sector_filters:'PASS',source_fields:'11_Entradas_Agregadas!AB:AK',definition:'Última matrícula declarada, no último período cursado ni fecha de deserción.'},null,2)+'\n');
console.log('Trajectory summary added and reconciled',n);
