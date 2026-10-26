import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const dir='/Users/alexi/.local/share/ipss/trazabilidad_integral_fase4_20261025';
const d=JSON.parse(await fs.readFile(dir+'/payload.json','utf8'));
const wb=Workbook.create();
for(const n of ['27_Guia_Hojas','56_Vista_T1_T2_T3','57_Trazabilidad_Actual','53_Codigos_T1_Confirmados','54_Contextos_y_Pendientes'])wb.worksheets.add(n);
const view=wb.worksheets.getItem('56_Vista_T1_T2_T3');
const summary=wb.worksheets.getItem('57_Trazabilidad_Actual');
const guide=wb.worksheets.getItem('27_Guia_Hojas');
const n=d.rows.length+5;
function title(s,text,last){s.getRange(`A1:${last}2`).merge();s.getRange('A1').values=[[text]];s.getRange(`A1:${last}2`).format={fill:'#102B42',font:{name:'Arial',size:14,bold:true,color:'#FFFFFF'},rowHeight:25};s.showGridLines=false;}
function header(s,range){s.getRange(range).format={fill:'#174977',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:42};}
title(view,'56 · T1 en T2/T3 — detalle local y fuentes','N');
view.getRange('A3:AB3').merge();view.getRange('A3').values=[['B/C/D/E · Todas las posiciones T1, incluidos pendientes. Filtre cohorte, período, código o CODCLI. No sumar filas como estudiantes: use Cuenta posición / Cuenta contexto.']];
view.getRange(`A5:AB${n}`).values=[d.headers,...d.rows];
view.getRange(`E6:J${n}`).setNumberFormat('@');view.getRange(`M6:P${n}`).setNumberFormat('@');
view.getRange(`A5:AB${n}`).format.font={name:'Arial',size:10};view.getRange(`A5:AB${n}`).format.rowHeight=21;
view.getRange('A:AB').format.columnWidth=23;view.getRange('M:P').format.columnWidth=31;view.getRange('U:Z').format.columnWidth=46;
header(view,'A5:AB5');view.freezePanes.freezeRows(5);
view.tables.add(`A5:AB${n}`,true,'VistaT1T2T3V19');
// Native internal hyperlinks are added by the preserving assembler.
view.getRange(`AA6:AA${n}`).values=d.rows.map(()=>['Ver origen']);
view.getRange(`O6:O${n}`).conditionalFormats.add('containsText',{text:'Pendiente',format:{fill:'#FFF2CC',font:{color:'#9C6500'}}});
const vr=c=>`'56_Vista_T1_T2_T3'!$${c}$6:$${c}$${n}`;
title(summary,'57 · Trazabilidad actual y pendientes','I');
summary.getRange('A3:I3').merge();summary.getRange('A3').values=[['C · Diccionario v8 activo. Conteos de contexto; no son tasas de retención. Los resultados anteriores y sus denominadores se conservan.']];summary.getRange('A3:I3').format.wrapText=true;summary.getRange('A3:I3').format.rowHeight=35;
summary.getRange('A5:I5').values=[['Cohorte T1','Año observado','Período nativo','Padrón T1','Con contexto','Sin contexto','Documentales','Internos aprobados','Código pendiente']];
for(let i=0;i<6;i++){
 const r=i+6,x=d.resumen[i];summary.getRange(`A${r}:C${r}`).values=[[x.COHORTE_ORIGEN,x.ANIO_OBSERVADO,Number(x.PERIODO_NATIVO)]];
 const cond=`${vr('B')},A${r},${vr('C')},B${r},${vr('D')},C${r}`;
 summary.getRange(`D${r}:I${r}`).formulas=[[
 `=SUMIFS(${vr('Q')},${cond})`,`=SUMIFS(${vr('Q')},${cond},${vr('R')},1)`,`=SUMIFS(${vr('Q')},${cond},${vr('R')},0)`,
 `=COUNTIFS(${cond},${vr('O')},"B/C Documental anual")`,`=COUNTIFS(${cond},${vr('O')},"D Interno aprobado")`,`=COUNTIFS(${cond},${vr('O')},"E Pendiente")`]];
}
summary.getRange('A13:C13').merge();summary.getRange('A13').values=[['Total posiciones / contextos']];summary.getRange('D13:I13').formulas=[['=SUM(D6:D11)','=SUM(E6:E11)','=SUM(F6:F11)','=SUM(G6:G11)','=SUM(H6:H11)','=SUM(I6:I11)']];
summary.getRange('A16:C16').values=[['Situación del código','Contextos','Lectura']];
const rel=[['Mismo código','MISMO_CODIGO','Código T1 conservado'],['Otro código respaldado','CODIGO_DISTINTO_RESPALDADO','Cambio de componentes ya documentado/aprobado'],['Código pendiente','CODIGO_PENDIENTE','No se adjudica una versión nueva']];
for(let i=0;i<3;i++){let r=17+i;summary.getRange(`A${r}`).values=[[rel[i][0]]];summary.getRange(`B${r}`).formulas=[[`=COUNTIF(${vr('P')},"${rel[i][1]}")`]];summary.getRange(`C${r}:I${r}`).merge();summary.getRange(`C${r}`).values=[[rel[i][2]]];}
const notes=[
 ['Pendientes multiversión',`=COUNTIFS(${vr('O')},"E Pendiente",${vr('S')},"Sí")`,'E · Incluidos en los 99; no sumarlos de nuevo.'],
 ['Detalle y evidencia',`=HYPERLINK("#'56_Vista_T1_T2_T3'!A5","Abrir detalle")`,'Filtrar por código o expediente; columnas X–Z conservan fuente, hoja y fila.'],
 ['Resultados vigentes',`=HYPERLINK("#'18_Foto_Intertrimestral'!B5","Ver resultados")`,'Actividad académica y matrícula son indicadores diferentes.'],
 ['Guía del libro',`=HYPERLINK("#'27_Guia_Hojas'!A4","Ver guía")`,'57 hojas clasificadas; auditorías históricas separadas del estado actual.'],
 ['Renuncias T2-2026','66 sin nómina','E · 462/528 se conserva como tasa de matrículas, no como tasa de personas.'],
 ['Alcance 2026-T3','545 personas','E · Listado completo; no exclusivo de ingresos 2026-3. Denominador conservado.'],
 ['Recálculo completo','Pendiente fase 5','C/E · Suplemento recalculado y estructura controlada; apertura/recálculo nativo integral pendiente.'],
 ['Conteos materializados','53 G/H; fuentes','C · Numeradores/denominadores vigentes tienen script y evidencia. No se presentan como fórmulas individuales.']];
for(let i=0;i<notes.length;i++){let r=22+i;const link=notes[i][1].startsWith('=HYPERLINK');const v=link?['Abrir detalle','Ver resultados','Ver guía'][i-1]:notes[i][1];summary.getRange(`A${r}:B${r}`).values=[[notes[i][0],v.startsWith('=')?null:v]];if(v.startsWith('='))summary.getRange(`B${r}`).formulas=[[v]];summary.getRange(`C${r}:I${r}`).merge();summary.getRange(`C${r}`).values=[[notes[i][2]]];}
summary.getRange('A5:I29').format.font={name:'Arial',size:10};summary.getRange('A:I').format.columnWidth=20;summary.getRange('A:A').format.columnWidth=28;summary.getRange('A5:I29').format.rowHeight=29;summary.getRange('A22:I29').format.wrapText=true;summary.getRange('A22:I29').format.rowHeight=43;header(summary,'A5:I5');header(summary,'A16:C16');summary.getRange('D6:I13').setNumberFormat('#,##0');summary.freezePanes.freezeRows(5);
title(guide,'27 · Qué contiene cada hoja y cómo se calcula','G');
guide.getRange('A3:G3').merge();guide.getRange('A3').values=[['C · Inventario V19. Las hojas 29–51 son antecedentes de sus ediciones. Para el estado actual consulte 52–57. Libro completo de uso local restringido.']];guide.getRange('A3:G3').format.wrapText=true;guide.getRange('A3:G3').format.rowHeight=38;
guide.getRange('A4:G61').values=[['Hoja','Rol','Contenido','Entrada principal','Navegación','Fórmulas / cruce','Privacidad'],...d.guide];
guide.getRange('E5:E61').values=d.guide.map(()=>['Abrir hoja']);
guide.getRange('A:G').format.columnWidth=31;guide.getRange('C:D').format.columnWidth=46;guide.getRange('F:F').format.columnWidth=61;guide.getRange('A4:G61').format.font={name:'Arial',size:10};guide.getRange('A4:G61').format.wrapText=true;guide.getRange('A4:G61').format.rowHeight=60;header(guide,'A4:G4');guide.freezePanes.freezeRows(4);guide.tables.add('A4:G61',true,'GuiaHojasV19');
const s53=wb.worksheets.getItem('53_Codigos_T1_Confirmados');s53.getRange('A6:M223').values=d.rows53;
for(let r=6;r<=223;r++){
 const cond=`${vr('B')},A${r},${vr('C')},B${r},${vr('D')},C${r},${vr('M')},E${r}`;
 s53.getRange(`F${r}`).formulas=[[`=SUMIFS(${vr('Q')},${cond})`]];
 s53.getRange(`K${r}`).formulas=[[`=SUMIFS(${vr('Q')},${cond},${vr('R')},0)`]];
 s53.getRange(`M${r}`).formulas=[[`=SUMIFS(${vr('Q')},${cond},${vr('R')},1)`]];
}
const s54=wb.worksheets.getItem('54_Contextos_y_Pendientes');
for(let r=6;r<=226;r++)s54.getRange(`N${r}`).formulas=[[`=COUNTIF(${vr('AB')},${r})`]];
wb.recalculate();
assert.deepEqual(summary.getRange('D13:I13').values[0],[6358,2838,3520,2742,13,99]);
assert.deepEqual(summary.getRange('B17:B19').values.flat(),[2718,37,99]);
assert.equal(summary.getRange('B22').values[0][0],24);
for(let r=6;r<=223;r++)for(const col of ['F','K','M'])assert.equal(s53.getRange(`${col}${r}`).values[0][0],d.rows53[r-6][{F:5,K:10,M:12}[col]]);
for(let r=6;r<=226;r++)assert.equal(s54.getRange(`N${r}`).values[0][0],d.expected54[r]);
// Dependency test in memory only; restore before export.
const idx=d.rows.findIndex(r=>r[14]==='E Pendiente');const addr=`O${idx+6}`;
view.getRange(addr).values=[['D Interno aprobado']];wb.recalculate();assert.deepEqual(summary.getRange('H13:I13').values[0],[14,98]);
view.getRange(addr).values=[['E Pendiente']];wb.recalculate();assert.deepEqual(summary.getRange('H13:I13').values[0],[13,99]);
await(await SpreadsheetFile.exportXlsx(wb)).save(dir+'/suplemento.xlsx');
for(const [sheet,range,file] of [[summary.name,'A1:I29','resumen.png'],[guide.name,'A1:G10','guia.png'],[view.name,'M1:T10','vista.png']])await fs.writeFile(dir+'/'+file,new Uint8Array(await(await wb.render({sheetName:sheet,range,scale:1.4})).arrayBuffer()));
await fs.writeFile(dir+'/QA_SUPLEMENTO.json',JSON.stringify({recalculo:'Artifact Tool',resumen:summary.getRange('D13:I13').values[0],grupos54:221,controles53:654,prueba_dependencia:'13/99 ->14/98 ->13/99; restaurado',limite:'No es recálculo integral ni prueba de Excel nativo'},null,2));
console.log('Suplemento recalculado: resumen, 221 grupos, 654 conteos y prueba de dependencia correctos.');
