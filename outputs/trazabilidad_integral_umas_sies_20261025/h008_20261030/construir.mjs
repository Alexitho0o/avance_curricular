// Autoría del complemento con Artifact Tool; no importa ni reescribe la maqueta.
import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';
const dir=process.argv[2]; if(!dir)throw Error('Directorio privado requerido');
const d=JSON.parse(await fs.readFile(path.join(dir,'payload.json'),'utf8'));
const wb=Workbook.create(),v=wb.worksheets.add('56_Vista_T1_T2_T3'),s=wb.worksheets.add('57_Trazabilidad_Actual');
const end=d.rows.length+5;
v.getRange(`AG5:AT${end}`).values=[d.headers,...d.rows];
s.getRange('L1:Q2').merge();s.getRange('L1').values=[['V25 · complemento v20 · CANDIDATA']];
s.getRange('L3:Q3').merge();s.getRange('L3').values=[['C · Contexto no acredita mismo expediente T1 ni vigencia. La instantánea v8 permanece a la izquierda.']];
s.getRange('L5:Q5').values=[['Cohorte T1','Año observado','Período nativo','Posiciones C1','Contextos v20','Efecto tasa (pp)']];
// Las seis combinaciones incluyen las de cero: no se desaparecen del resumen.
for(let i=0;i<d.resumen.length;i++){
 const r=i+6,[coh,year,period]=d.resumen[i];s.getRange(`L${r}:N${r}`).values=[[Number(coh),Number(year),Number(period)]];
 const cond=`'56_Vista_T1_T2_T3'!$B$6:$B$${end},L${r},'56_Vista_T1_T2_T3'!$C$6:$C$${end},M${r},'56_Vista_T1_T2_T3'!$D$6:$D$${end},N${r}`;
 s.getRange(`O${r}:Q${r}`).formulas=[[`=SUMIFS('56_Vista_T1_T2_T3'!$AG$6:$AG$${end},${cond})`,`=SUMIFS('56_Vista_T1_T2_T3'!$AH$6:$AH$${end},${cond})`,'=0']];
}
// Condiciones se incluyen en el fragmento solo para el recálculo previo al trasplante.
v.getRange(`B6:D${end}`).values=d.keys;
s.getRange('L13:N13').merge();s.getRange('L13').values=[['Totales (posiciones / contextos)']];s.getRange('O13:Q13').formulas=[['=SUM(O6:O11)','=SUM(P6:P11)','=0']];
s.getRange('L16:Q18').merge();s.getRange('L16').values=[['E · No se convierte contexto académico en matrícula vigente. Las 99 adjudicaciones siguen pendientes. Las fotos parciales y los cortes sin acreditación no reemplazan las tasas de R19.']];
for(const [sh,rg] of [[v,`AG5:AT${end}`],[s,'L1:Q18']])sh.getRange(rg).format={font:{name:'Arial',size:10},horizontalAlignment:'center',verticalAlignment:'center',wrapText:true,rowHeight:42};
for(const [sh,rg] of [[v,'AG5:AT5'],[s,'L5:Q5'],[s,'L1:Q2']])sh.getRange(rg).format={fill:'#003B71',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'}};
s.getRange('L:Q').format.columnWidth=23;v.getRange('AG:AH').format.columnWidth=18;v.getRange('AI:AT').format.columnWidth=35;
s.getRange('O6:P13').setNumberFormat('[>=1000000]#"."000"."000;[>=1000]#"."000;0');
wb.recalculate();
if(s.getRange('O13').values[0][0]!==1135)throw Error('Total C1 distinto');
await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(dir,'fragment.xlsx'));
await fs.writeFile(path.join(dir,'resumen_v20.png'),new Uint8Array(await(await wb.render({sheetName:s.name,range:'L1:Q18',scale:1.5})).arrayBuffer()));
console.log('Complemento v20 recalculado; posiciones C1 = 1135.');
