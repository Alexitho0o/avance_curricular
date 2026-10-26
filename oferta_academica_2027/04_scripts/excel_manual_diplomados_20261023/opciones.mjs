import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../..');
const data=JSON.parse(await fs.readFile(path.join(here,'opciones.json'),'utf8'));
const dir=path.join(root,'10_entrega/conciliacion_diplomados_opciones_20261023');
const gov=path.join(root,'11_gobernanza/conciliacion_diplomados_opciones_20261023');
await fs.mkdir(dir,{recursive:true});await fs.mkdir(gov,{recursive:true});
const name='CONCILIACION_DIPLOMADOS_OPCIONES_A_B_20261023.xlsx';
const outputs=[path.join(dir,name),path.join('/Users/alexi/Desktop',name)];
for(const p of outputs){try{await fs.access(p);throw Error('Ya existe '+p);}catch(e){if(e.code!=='ENOENT')throw e;}}
const wb=Workbook.create();
const clp='[>=1000000]"$"#"."000"."000;[>=1000]"$"#"."000;"$"0';
const specs=[
 {name:'Opcion A - SIES',title:'Opcion A | Conciliacion de los 21 diplomados SIES',note:'5 coinciden por nombre; 3 tienen candidatos ambiguos; 13 sin correspondencia nominal. No se modifican vigencias.',rows:data.a,headers:['Codigo SIES','Nombre original SIES','Nombre de Docencia / candidato','Resultado','Matricula Docencia','Decision del usuario','Observacion','Fila en Hoja2'],decision:'F',wide:'G',preview:'A6:E12'},
 {name:'Opcion B - Oferta Docencia',title:'Opcion B | Revisar continuidad o eventual incorporacion',note:'Los programas realmente nuevos o faltantes se presentan en Etapa 2 (02 al 13/11/2026); no se agregan en Etapa 1.',rows:data.b,headers:['Fila en Hoja2','Nombre original Docencia','Nombre SIES coincidente / candidato','Codigo SIES','Matricula Docencia','Situacion','Decision del usuario','Tratamiento propuesto'],decision:'G',wide:'H',preview:'A6:F10'},
];
for(const spec of specs){
 const s=wb.worksheets.add(spec.name);s.showGridLines=false;
 const last=6+spec.rows.length;
 const full=s.getRange(`A1:H${last}`);full.format.font={name:'Arial',size:10,color:'#222222'};full.format.verticalAlignment='center';full.format.columnWidth=20;
 s.getRange('A2').values=[[spec.title]];s.getRange('A2').format.font={name:'Arial',size:15,bold:true};
 s.getRange('A3').values=[[spec.note]];s.getRange('A3').format.font={name:'Arial',size:10,color:'#555555'};
 s.getRange('A4').values=[['Fuentes: reporte SIES 6047 (20/10/2026); Oferta Diplomados 2027 - SIES vf.xlsx, Hoja2; manual octubre 2026, pp. 15 y 29.']];
 s.getRange(`A6:H${last}`).values=[spec.headers,...spec.rows];
 s.getRange(`A6:H${last}`).format.wrapText=true;
 s.getRange('A6:H6').format={fill:'#264653',font:{name:'Arial',size:10,color:'#FFFFFF',bold:true},rowHeight:42,wrapText:true,horizontalAlignment:'center'};
 s.getRange(`A7:H${last}`).format.rowHeight=84;
 s.getRange(`A1:A${last}`).format.columnWidth=12;
 s.getRange(`B1:C${last}`).format.columnWidth=59;
 s.getRange(`D1:D${last}`).format.columnWidth=26;
 s.getRange(`E1:E${last}`).format.columnWidth=18;
 s.getRange(`${spec.wide}1:${spec.wide}${last}`).format.columnWidth=66;
 s.getRange(`E7:E${last}`).setNumberFormat(clp);
 const table=s.tables.add(`A6:H${last}`,true,spec.name.startsWith('Opcion A')?'ConciliacionSIES':'OfertaDocencia');table.style='TableStyleLight1';
 s.getRange(`${spec.decision}7:${spec.decision}${last}`).format.fill='#FFF2CC';
 s.getRange(`${spec.decision}7:${spec.decision}${last}`).format.columnWidth=28;
 s.freezePanes.freezeRows(6);s.freezePanes.freezeColumns(2);
 if(spec.name.startsWith('Opcion A'))s.getRange(`D7:D${last}`).conditionalFormats.add('containsText',{text:'POR CONFIRMAR',format:{fill:'#FFF2CC'}});
}
wb.recalculate();
for(const spec of specs){
 const s=wb.worksheets.getItem(spec.name);
 if(JSON.stringify(s.getRange(`A7:H${6+spec.rows.length}`).values)!==JSON.stringify(spec.rows))throw Error('Datos cambiados');
 const img=await wb.render({sheetName:spec.name,range:spec.preview,scale:1,format:'png'});
 await fs.writeFile(path.join(here,spec.name.startsWith('Opcion A')?'opcion_a.png':'opcion_b.png'),new Uint8Array(await img.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(outputs[0]);
await fs.copyFile(outputs[0],outputs[1],1);
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
for(const x of data.inputs)if(hash(await fs.readFile(x.ruta))!==x.sha256)throw Error('Fuente modificada');
const bytes=await fs.readFile(outputs[0]);
if(hash(bytes)!==hash(await fs.readFile(outputs[1])))throw Error('Copias diferentes');
await fs.writeFile(path.join(gov,'MANIFIESTO.json'),JSON.stringify({fecha:'2026-10-23',estado:'CUADROS_PARA_DECISION_NO_CARGA',fuentes:data.inputs,filas_opcion_a:21,filas_opcion_b:29,coincidencias_nominales:5,ambiguos:3,sin_correspondencia:13,cambios_csv:0,cambios_vigencia:0,vacantes:'15 por semestre, instruccion del usuario, no aplicada en estos cuadros',scripts:await Promise.all(['preparar_opciones.py','opciones.mjs'].map(async n=>({ruta:path.join(here,n),sha256:hash(await fs.readFile(path.join(here,n)))}))),salidas:outputs.map(p=>({ruta:p,sha256:hash(bytes),bytes:bytes.length})),reanudacion:'Recibir decisiones; no agregar programas nuevos a Etapa 1 ni inferir vigencia por ausencia; resolver los otros 16 antes de declarar la carga completa.',git:'Respaldo local, sin commit ni push'},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({outputs,bytes:bytes.length}));
