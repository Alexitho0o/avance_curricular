import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../..');
const tag='preparacion_etapa2_noviembre_20261023';
const data=JSON.parse(await fs.readFile(path.join(root,'06_validaciones',tag,'ANALISIS.json'),'utf8'));
const name='REVISION_DIPLOMADOS_ETAPA2_NOVIEMBRE_20261023.xlsx';
const outputs=[path.join(data.out,name),path.join('/Users/alexi/Desktop',name)];
for(const p of outputs){try{await fs.access(p);throw Error('No sobrescribir '+p);}catch(e){if(e.code!=='ENOENT')throw e;}}
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
for(const [p,info] of Object.entries(data.fuentes)){
  if(hash(await fs.readFile(p))!==info.sha256)throw Error('Fuente modificada '+p);
}
const wb=Workbook.create();
const specs=[
  {name:'Programas',headers:data.encabezados,rows:data.programas,last:'M',widths:[63,24,13,55,65,11,16,16,19,17,17,17,70],preview:'A2:E14'},
  {name:'Pendientes por campo',headers:data.encabezados_reglas,rows:data.reglas,last:'F',widths:[11,42,29,16,94,15],preview:'A8:F15'},
];
for(const spec of specs){
  const s=wb.worksheets.add(spec.name);s.showGridLines=false;
  const end=8+spec.rows.length;
  const area=s.getRange(`A1:${spec.last}${end+9}`);
  area.format.font={name:'Arial',size:10,color:'#242424'};
  area.format.verticalAlignment='center';
  for(let c=0;c<spec.widths.length;c++)s.getRangeByIndexes(0,c,end+9,1).format.columnWidth=spec.widths[c];
  s.getRange('A2').values=[[spec.name==='Programas'?'Diplomados 2027: preparacion de Etapa 2':'Etapa 2: revision de las 48 columnas para postitulos']];
  s.getRange('A2').format.font={name:'Arial',size:15,bold:true};
  s.getRange('A3').values=[['Proceso 2026. Etapa 2 del 02 al 13 de noviembre. Revision al 23/10/2026. No es archivo de carga.']];
  s.getRange(`A8:${spec.last}${end}`).values=[spec.headers,...spec.rows];
  s.getRange(`A8:${spec.last}${end}`).format.wrapText=true;
  const table=s.tables.add(`A8:${spec.last}${end}`,true,spec.name==='Programas'?'RevisionProgramas':'RevisionCampos');
  table.style='TableStyleLight1';
  s.getRange(`A8:${spec.last}8`).format={fill:'#3D4C59',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:44,wrapText:true,horizontalAlignment:'center'};
  s.getRange(`A9:${spec.last}${end}`).format.rowHeight=76;
  s.freezePanes.freezeRows(8);s.freezePanes.freezeColumns(spec.name==='Programas'?1:2);
  if(spec.name==='Programas'){
    s.getRange('A4').formulas=[['="Docencia: "&COUNTA(A9:A37)&" programas. Candidatos Etapa 2: "&COUNTIFS(B9:B37,"CANDIDATO ETAPA 2")&". Ya en Etapa 1: "&COUNTIFS(B9:B37,"YA EN ETAPA 1")&"."']];
    s.getRange('A5').values=[['22 candidatos pendientes de antecedentes academicos; ver Pendientes por campo. No equivalen aun a 22 filas de carga.']];
    s.getRange('A6').values=[['Importes I:L conservan los encabezados originales de Docencia. La correccion matricula/arancel de V06 no se aplica aqui.']];
    s.getRange('A7').values=[['V06 intacta. Conciliacion final contra reporte 6048 pendiente. Criterios 15+15 y arancel: ratificar alcance a los nuevos.']];
    s.getRange('B9:B37').conditionalFormats.add('containsText',{text:'CANDIDATO',format:{fill:'#FFF2CC'}});
    s.getRange('F9:H37').setNumberFormat('0');
    s.getRange('I9:L37').setNumberFormat('[>=1000000]"$"#"."000"."000;[>=1000]"$"#"."000;"$"0');
    s.getRange('A40').values=[['Fuentes y alcance']];
    s.getRange('A40').format.font={name:'Arial',size:10,bold:true};
    s.getRange('A41').values=[['Docencia: Oferta Diplomados 2027 - SIES vf.xlsx, Hoja2 filas 5 a 33. Los datos originales se conservan en F:M.']];
    s.getRange('A42').values=[['Base: CARGA_OFERTA_2027_ETAPA1_17467_20261023_V06.csv y DECISIONES_21_DIPLOMADOS.tsv congelados.']];
    s.getRange('A43').values=[['Los cruces de codigos 68 y 99 provienen de decisiones del usuario, no de identidad literal de nombres.']];
    s.getRange('A44').values=[['Los 14 programas con vigencia 3 siguen intactos; no se asignan sus codigos ni se infieren equivalencias para las nuevas altas.']];
    s.getRange('A45').values=[['Fuente normativa: Instructivo_Oferta_Academica_2027_CFT_E_IP_DFE.pdf (octubre 2026), Anexo 2 pp.29-41 y Anexo 4 pp.56-58.']];
  }else{
    s.getRange('A4').formulas=[['="Campos sin dato directo por candidato: "&COUNTIFS(C9:C56,"FALTA DATO")&". Ausencias programa/campo: "&SUMIFS(D9:D56,C9:C56,"FALTA DATO")&"."']];
    s.getRange('A5').values=[['Los conteos son sobre 22 programas fuente; no son errores observados en PES. Falta confirmar clasificacion, oferta y criterios previos.']];
    s.getRange('A6').values=[['Rojo: dato academico ausente. Vacio exigido y cero segun nivel no son pendientes a solicitar a Docencia.']];
    s.getRange('A7').values=[['Fuente: manual octubre 2026, Anexo 2 pp.35-41. Paginas especificas en F. No se reutilizaron las reglas de agosto.']];
    s.getRange('C9:C56').conditionalFormats.add('containsText',{text:'FALTA DATO',format:{fill:'#FCE4D6',font:{color:'#9C0006',bold:true}}});
    s.getRange('D9:D56').setNumberFormat('0');
  }
}
wb.recalculate();
if(wb.worksheets.getItem('Programas').getRange('A4').values[0][0]!=='Docencia: 29 programas. Candidatos Etapa 2: 22. Ya en Etapa 1: 7.')throw Error('Conteos incorrectos');
if(wb.worksheets.getItem('Pendientes por campo').getRange('A4').values[0][0]!=='Campos sin dato directo por candidato: 17. Ausencias programa/campo: 374.')throw Error('Faltantes incorrectos');
for(const spec of specs){
  const s=wb.worksheets.getItem(spec.name);
  if(JSON.stringify(s.getRange(`A9:${spec.last}${8+spec.rows.length}`).values)!==JSON.stringify(spec.rows))throw Error('Datos alterados');
  const image=await wb.render({sheetName:spec.name,range:spec.preview,scale:1,format:'png'});
  await fs.writeFile(path.join(here,spec.name==='Programas'?'etapa2_programas.png':'etapa2_campos.png'),new Uint8Array(await image.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(outputs[0]);
await fs.copyFile(outputs[0],outputs[1],1);
const manifest={fecha:new Date().toISOString(),estado:'PREPARACION_NO_CARGA',proceso:2026,oferta:2027,etapa:'2 noviembre',fuentes:data.fuentes,controles:data.controles,cambios_etapa1:0,commit_push:false,
  scripts:[],salidas:[],pendientes:['Antecedentes academicos','Clasificacion y denominaciones','Alcance criterios vacantes y cobros','Oferta efectiva','Reporte 6048','Estructura descargada PES 17469'],
  reanudacion:'Completar pendientes, conciliar 6048, validar antes de producir CSV. No modificar V06.'};
for(const p of [fileURLToPath(import.meta.url),path.join(root,'04_scripts/preparar_diplomados_etapa2_noviembre_20261023.py')])manifest.scripts.push({ruta:p,sha256:hash(await fs.readFile(p))});
for(const p of [...outputs,path.join(data.out,'RESUMEN_Y_PENDIENTES.md'),path.join(data.gov,'REVISION_48_COLUMNAS.tsv'),path.join(root,'06_validaciones',tag,'ANALISIS.json'),path.join(root,'06_validaciones',tag,'CONCILIACION_29_PROGRAMAS.tsv'),path.join(root,'06_validaciones',tag,'FALTANTES_POR_PROGRAMA.tsv'),path.join(root,'06_validaciones',tag,'BAJAS_ETAPA1_SIN_REACTIVACION.tsv')]){
  const b=await fs.readFile(p);manifest.salidas.push({ruta:p,sha256:hash(b),bytes:b.length});
}
for(const [p,info] of Object.entries(data.fuentes)){
  if(hash(await fs.readFile(p))!==info.sha256)throw Error('Fuente modificada '+p);
  if(info.modo && '0o'+((await fs.stat(p)).mode&0o777).toString(8)!==info.modo)throw Error('Permiso congelado modificado');
}
await fs.writeFile(path.join(data.gov,'MANIFIESTO.json'),JSON.stringify(manifest,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({salidas:outputs,controles:data.controles}));
