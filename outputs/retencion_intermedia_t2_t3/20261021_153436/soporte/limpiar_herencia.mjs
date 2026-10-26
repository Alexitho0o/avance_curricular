import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const R='/Users/alexi/Documents/GitHub/avance_curricular',O=R+'/outputs/retencion_intermedia_t2_t3/20261021_153436',P=R+'/.local_restricted/retencion_intermedia/20261021_153436';
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(P+'/public_candidate.xlsx'));
const model=JSON.parse(await fs.readFile(O+'/MODELO_AGREGADO.json','utf8')),last=model.groups.length+4,last9=model.groups.length+6;
const put=(sn,a,v)=>{const r=w.worksheets.getItem(sn).getRange(a);typeof v==='string'&&v.startsWith('=')?r.formulas=[[v]]:r.values=[[v]];};
const notes={
'4_Resultados_Sector':{
 B3:'C: sectores de la taxonomía IPSS conservados de la maqueta (hoja 8). La hoja 9 contiene agregados ponderados; las vistas suman estudiantes y registros documentados. El bloque B compara las presencias de la cohorte 2025 en los listados parciales de 2026-T2/T3, no cifras SIES.',
 H5:'B. Cohorte 2025 — presencia documentada en 2026-T2 y 2026-T3, por sector',
 I6:'Estudiantes base T2',J6:'Con registro 2026-T2',K6:'Presencia T2 (%)',L6:'Estudiantes base T3',M6:'Con registro 2026-T3',N6:'Presencia T3 (%)',O6:'Variación T3 − T2 (pp)',
 H11:'C/E: ambos porcentajes usan la misma cohorte 2025, con los filtros de la hoja 14. Son presencias en listados parciales; su diferencia no acredita pérdida de estudiantes entre cierres. No es una comparación con SIES.',
 H35:'E: la cobertura completa y el estado efectivo de cada cierre siguen pendientes. Una ausencia en estos listados no permite clasificar deserción ni certificar una tasa de retención intermedia.',
 B20:'B/C: se conservan las carreras y sectores de cada cohorte original. La composición y el tiempo de seguimiento difieren entre 2024 y 2025; compare siempre el mismo alcance y seguimiento.',
 B47:'C/E: el seguimiento seleccionado cambia numeradores documentados, manteniendo la cohorte original. Las diferencias entre sectores describen las fuentes disponibles; no prueban causas de permanencia o abandono.'},
'5_Evolucion':{B5:'Seguimiento seleccionado — cohortes 2024 y 2025; referencia SIES solo en T1 institucional',B12:'A/C/E: la referencia SIES es anual e institucional. Se muestra solo en T1 anual MU, sin filtro de sector/carrera. En T2/T3 o Último respaldo no se calcula una brecha contra SIES.'},
'10_Seguimiento_2025':{A2:'10. Presencia de la cohorte 2025 en listados 2026-T2/T3 — soporte técnico'},
'12_Desglose_Jornada_Edad_Sexo':{B6:'A. Seguimiento por carrera y jornada — cohortes 2024 y 2025 seleccionadas',B60:'B. Seguimiento por jornada y cohorte',B90:'D. Seguimiento por tramo de edad y cohorte',B113:'C/E: estas desagregaciones usan los mismos filtros y numeradores de la hoja 14. Un porcentaje resume registros documentados; los listados parciales no permiten inferir causas, fecha de baja ni deserción.'},
'13_Granular_Codigo_Unico':{H7:'Con registro elegido',B140:'C. Cohorte 2025 — presencia documentada T2/T3 por carrera',D141:'Estudiantes base T2',E141:'Con registro 2026-T2',F141:'Presencia T2 (%)',G141:'Estudiantes base T3',H141:'Con registro 2026-T3',I141:'Presencia T3 (%)',J141:'Variación T3 − T2 (pp)',B182:'C/E: C reúne solo la cohorte 2025 y contrasta listados parciales T2/T3 del año siguiente. B y la vista ejecutiva muestran las cohortes y el seguimiento elegidos. Iguale ambos criterios antes de comparar.'},
'15_Tablas_Ejecutivas':{B2:'C: las tablas responden a los filtros de la hoja 14. Los bloques T2/T3 de cohorte 2025 comparan presencias documentadas, con cobertura de cierre pendiente. Para reunir grupos divida suma de registros por suma de estudiantes; no promedie porcentajes.',H5:'4B. Cohorte 2025 — presencia T2/T3 por sector',I6:'Estudiantes base T2',J6:'Con registro 2026-T2',K6:'Presencia T2 (%)',L6:'Estudiantes base T3',M6:'Con registro 2026-T3',N6:'Presencia T3 (%)',O6:'Variación T3 − T2 (pp)',Q5:'5. Cohortes 2024/2025 — SIES solo en T1 institucional',X5:'12A. Seguimiento por carrera y jornada — selección de hoja 14'}
};
for(const[sn,items]of Object.entries(notes))for(const[a,v]of Object.entries(items))put(sn,a,v);
for(let r=7;r<=9;r++){
 const crit=`'11_Entradas_Agregadas'!$A$5:$A$${last},2025,'11_Entradas_Agregadas'!$E$5:$E$${last},H${r},'11_Entradas_Agregadas'!$E$5:$E$${last},'14_Vistas_Ejecutivas'!$BO$12,'11_Entradas_Agregadas'!$C$5:$C$${last},'14_Vistas_Ejecutivas'!$BO$13`;
 for(const[col,source]of [['I','N'],['J','P'],['L','N'],['M','Q']])put('4_Resultados_Sector',col+r,`=IF('14_Vistas_Ejecutivas'!$C$4="Cohorte 2024",0,SUMIFS('11_Entradas_Agregadas'!$${source}$5:$${source}$${last},${crit}))`);
 put('4_Resultados_Sector','K'+r,`=IF(I${r}=0,"",J${r}/I${r})`);put('4_Resultados_Sector','N'+r,`=IF(L${r}=0,"",M${r}/L${r})`);put('4_Resultados_Sector','O'+r,`=IF(OR(I${r}=0,L${r}=0),"",(N${r}-K${r})*100)`);
}
for(let r=24;r<=27;r++){put('4_Resultados_Sector','B'+r,r<26?2024+r-24:'');for(let j=0;j<3;j++)put('4_Resultados_Sector',['C','D','E'][j]+r,r<26?'=F'+(7+(r-24)*3+j):'=""');}
for(let r=142;r<=158;r++){
 put('13_Granular_Codigo_Unico','E'+r,`=SUMIFS($I$8:$I$43,$C$8:$C$43,$C${r})`);put('13_Granular_Codigo_Unico','G'+r,`=D${r}`);put('13_Granular_Codigo_Unico','H'+r,`=SUMIFS($J$8:$J$43,$C$8:$C$43,$C${r})`);put('13_Granular_Codigo_Unico','J'+r,`=IF(D${r}=0,"",(I${r}-F${r})*100)`);
}
put('13_Granular_Codigo_Unico','J159','=IF(D159=0,"",(I159-F159)*100)');
const v=w.worksheets.getItem('14_Vistas_Ejecutivas'),checks=[];
for(const cohort of ['Cohortes 2024 y 2025','Cohorte 2024','Cohorte 2025']){
 v.getRange('C4').values=[[cohort]];w.recalculate();
 const vals=w.worksheets.getItem('4_Resultados_Sector').getRange('I7:N9').values,total=j=>vals.reduce((a,r)=>a+Number(r[j]||0),0),t=w.worksheets.getItem('13_Granular_Codigo_Unico').getRange('D159:I159').values[0];
 const e=cohort==='Cohorte 2024'?[0,0,0]:[1150,2,0];
 if(total(0)!==e[0]||total(1)!==e[1]||total(4)!==e[2]||t[0]!==e[0]||t[1]!==e[1]||t[4]!==e[2])throw Error('T2/T3 block totals mismatch '+JSON.stringify({cohort,vals,t,e}));
 checks.push({cohort,denominator:total(0),T2:total(1),T3:total(4),sector_career_consistent:true});
}
v.getRange('C4').values=[['Cohortes 2024 y 2025']];w.recalculate();
await(await SpreadsheetFile.exportXlsx(w)).save(P+'/public_candidate.xlsx');
await fs.writeFile(O+'/QA_BLOQUES_T2_T3.json',JSON.stringify({status:'OK',checks,old_SIES_comparisons_replaced:true},null,2)+'\n');
console.log('Inherited comparison blocks corrected; 3 cohort controls passed.');
