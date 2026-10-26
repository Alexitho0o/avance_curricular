import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {Workbook, SpreadsheetFile, FileBlob} from '@oai/artifact-tool';

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../..');
const tag='maqueta_etapa2_noviembre_20261023_v02';
const audit=path.join(root,'06_validaciones',tag);
const data=JSON.parse(await fs.readFile(path.join(audit,'INSUMOS.json'),'utf8'));
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(data.snapshot));
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const col=i=>i<26?String.fromCharCode(65+i):'A'+String.fromCharCode(65+i-26);
if(process.argv.includes('--preview')){
  for(const [s,r,n] of [['Programas','A8:E13','programas'],['Pendientes por campo','A8:F13','campos']]){
    const img=await wb.render({sheetName:s,range:r,scale:1,format:'png'});
    await fs.writeFile(path.join(here,`maqueta_antes_${n}.png`),new Uint8Array(await img.arrayBuffer()));
  }
  console.log('Maqueta original renderizada sin modificar.');
  process.exit(0);
}
const outdir=path.join(root,'10_entrega',tag);
const gov=path.join(root,'11_gobernanza',tag);
const name='DIPLOMADOS_ETAPA2_PARA_COMPLETAR_20261023_V02.xlsx';
const outputs=[path.join(outdir,name),path.join('/Users/alexi/Desktop',name)];
await fs.mkdir(outdir,{recursive:true});await fs.mkdir(gov,{recursive:true});
let previous=null;
try{previous=JSON.parse(await fs.readFile(path.join(gov,'MANIFIESTO.json'),'utf8'));}catch(e){if(e.code!=='ENOENT')throw e;}
for(const p of outputs){
  try{
    const content=await fs.readFile(p),known=previous?.salidas.find(x=>x.ruta===p);
    if(!known||hash(content)!==known.sha256)throw Error('No sobrescribir archivo externo '+p);
  }catch(e){if(e.code!=='ENOENT')throw e;}
}
for(const [p,info] of Object.entries(data.inputs))if(hash(await fs.readFile(p))!==info.sha256)throw Error('Fuente alterada '+p);

const fill={required:'#DDEBF7',blank:'#E7E6E6',missing:'#FFC7CE',review:'#FFF2CC',header:'#3D4C59'};
const s=wb.worksheets.add('Diplomados para completar');
s.showGridLines=false;
const all=s.getRange('A1:AV30');
all.format.font={name:'Arial',size:10,color:'#242424'};
all.format.verticalAlignment='center';all.format.columnWidth=30;
s.getRange('A1:A30').format.columnWidth=10;
s.getRange('B1:B30').format.columnWidth=30;
s.getRange('C1:C30').format.columnWidth=14;
s.getRange('D1:D30').format.columnWidth=59;
s.getRange('O1:O30').format.columnWidth=50;
s.getRange('A2').values=[['Diplomados 2027: completar antecedentes para Etapa 2']];
s.getRange('A2').format.font={name:'Arial',size:15,bold:true};
s.getRange('A3').values=[['Plantilla de 22 programas y 48 campos SIES. No cargar este Excel en PES; requiere completar, validar y convertir a CSV.']];
s.getRange('A4').values=[['Azul: obligatorio. Gris: debe quedar vacio. Rojo: falta dato. Amarillo: dato preparado para revisar. Ver regla abre el detalle del campo.']];
const grid=data.candidatos.map(p=>data.fields.map((field,i)=>{
  if(i===3)return p.nombre_sies_preparado;
  if(i===15)return 3;
  if(i===16)return 5;
  if(i>=22&&i<=31)return 0;
  if(i===42)return 1;
  if(i===43)return 0;
  return null;
}));
s.getRange('A8:AV8').values=[data.fields];
s.getRange('A9:AV30').values=grid;
for(let n=0;n<data.candidatos.length;n++){
  const r=n+9,p=data.candidatos[n],source=p.fila_maqueta;
  for(const c of ['AG','AH'])s.getRange(`${c}${r}`).formulas=[[`='Programas'!G${source}`]];
  s.getRange(`AS${r}`).formulas=[[`='Programas'!I${source}`]];
  s.getRange(`AT${r}`).formulas=[[`='Programas'!J${source}`]];
  s.getRange(`AU${r}`).formulas=[[`='Programas'!H${source}`]];
  wb.notes.add({id:`diploma-${r}`,target:{cell:{sheetName:s.name,sheetId:s.sheetId,address:`D${r}`}},authorId:'',createdAt:'',body:{plainText:`Fuente: Programas!A${source}. Nombre original: ${p.nombre_original}. Se prepararon mayusculas, acentos, puntuacion y espacios, sin corregir denominacion. ${p.observacion}`}});
}
s.tables.add('A8:AV30',true,'PlantillaDiplomadosEtapa2').style='TableStyleLight1';
s.getRange('A8:AV8').format={font:{name:'Arial',size:10,bold:true,color:'#242424'},wrapText:true,rowHeight:58,horizontalAlignment:'center'};
s.getRange('A9:AV30').format.rowHeight=66;s.getRange('A9:AV30').format.wrapText=true;
s.getRange('A5:AV6').format={wrapText:true,rowHeight:32,horizontalAlignment:'center'};
s.getRange('A7:AV7').format={font:{name:'Arial',size:10,color:'#0563C1',underline:'single'},rowHeight:24};
const texts=new Set([1,2,3,8,14]);
for(let i=0;i<48;i++){
  const c=col(i),blank=data.blank_indices.includes(i),rr=i+9;
  s.getRange(`${c}5`).values=[[blank?'DEJAR VACIO':'OBLIGATORIO']];
  s.getRange(`${c}6`).values=[[blank?'NO COMPLETAR':'MODIFICABLE SEGUN REGLA']];
  s.getRange(`${c}5:${c}6`).format.fill=blank?fill.blank:fill.required;
  s.getRange(`${c}8`).format.fill=blank?fill.blank:fill.required;
  s.getRange(`${c}7`).values=[[`Ver regla (${c})`]];
  if(blank){
    s.getRange(`${c}9:${c}30`).format.fill=fill.blank;
    s.getRange(`${c}9:${c}30`).conditionalFormats.addCustom(`LEN(${c}9&"")>0`,{fill:fill.missing});
  }else{
    s.getRange(`${c}9:${c}30`).conditionalFormats.addCustom(`LEN(${c}9&"")=0`,{fill:fill.missing});
  }
  if(!texts.has(i))s.getRange(`${c}9:${c}30`).setNumberFormat('0');
  wb.notes.add({id:`campo-${c}`,target:{cell:{sheetName:s.name,sheetId:s.sheetId,address:`${c}8`}},authorId:'',createdAt:'',body:{plainText:`${data.reglas[i][4]} Manual octubre 2026, paginas ${data.reglas[i][5]}. Campo ${data.fields[i]}.`}});
}
s.getRange('AR9:AU30').setNumberFormat('[>=1000000]"$"#"."000"."000;[>=1000]"$"#"."000;"$"0');
for(const r of ['D9:D30','P9:Q30','AG9:AH30','AQ9:AR30','AU9:AU30'])s.getRange(r).format.fill=fill.review;
for(const [c,values] of Object.entries({E:['1','2','3'],F:['1','2','3','4'],G:['1','2','3','4','5','6','7','8','9'],H:['1','2','3'],M:['1','2','3','4'],P:['3'],Q:['5'],S:['1','2','3'],T:['1','2','3','4','5','6'],V:['1','2','3','4','5','6','7','8','9','10'],AQ:['1','2'],AV:['1','2','3']}))s.getRange(`${c}9:${c}30`).dataValidation={rule:{type:'list',values}};
s.freezePanes.freezeRows(8);s.freezePanes.freezeColumns(4);

const ruleSheet=wb.worksheets.getItem('Pendientes por campo');
ruleSheet.tables.items[0].delete();
ruleSheet.getRange('G8:I8').values=[['Obligatoriedad','Modificacion en Etapa 2','Ir al campo']];
ruleSheet.getRange('D8').values=[['Celdas por completar o vaciar']];
ruleSheet.getRange('G1:H65').format.columnWidth=28;
ruleSheet.getRange('I1:I65').format.columnWidth=22;
ruleSheet.getRange('G8:I56').format.font={name:'Arial',size:10,color:'#242424'};
ruleSheet.getRange('G8:I56').format.wrapText=true;
ruleSheet.getRange('G8:I56').format.verticalAlignment='center';
ruleSheet.tables.add('A8:I56',true,'RevisionCampos').style='TableStyleLight1';
ruleSheet.getRange('A8:I8').format={fill:fill.header,font:{name:'Arial',size:10,color:'#FFFFFF',bold:true},wrapText:true,rowHeight:44,horizontalAlignment:'center'};
ruleSheet.getRange('A4').formulas=[['="Celdas obligatorias vacias: "&SUMIFS(D9:D56,G9:G56,"DATO OBLIGATORIO")&". Campos que deben quedar vacios: "&COUNTIFS(G9:G56,"DEBE QUEDAR VACIO")&"."']];
ruleSheet.getRange('A5').values=[['Las 48 columnas se conservan. Son 39 campos obligatorios con dato y 9 que deben quedar vacios para diplomados.']];
ruleSheet.getRange('A6').values=[['Rojo: dato ausente. Azul: obligatorio y modificable segun regla. Gris: no completar. Los enlaces llevan a la tercera hoja.']];
const customRules={
  3:'Nombre preparado en mayusculas sin acentos ni puntuacion. Revisar denominacion completa, siglas y errores del original; no inventar equivalencias. Ver nota en cada nombre.',
  15:'3 = Postitulo, precargado porque el usuario confirma diplomados. Confirmar coherencia con nivel especifico 5 y duracion desde un semestre.',
  16:'5 = Diplomado (desde un semestre), precargado segun clasificacion del usuario. Debe respaldarse con duracion del plan; si es menor, revisar elegibilidad.',
  17:'OBLIGATORIO. Ano real en que el programa inicio actividades. El periodo 2027 de la maqueta NO acredita que ANIO_INICIO sea 2027.',
  18:'OBLIGATORIO, incluso para diplomados. Acreditacion DEL PROGRAMA: 1 Si; 2 No; 3 En proceso. Si no esta acreditado corresponde 2, no vacio. Docencia confirma.',
  19:'OBLIGATORIO, incluso para diplomados. Nivel minimo de ingreso: 1 Media; 2 Tecnico Superior; 3 Bachillerato; 4 Ciclo Basico; 5 Plan Comun; 6 Titulo Profesional.',
  32:'Dato obligatorio numerico. Se enlaza 15 desde la columna G de la maqueta: Vacantes 1er y 2do semestre. Criterio usuario: 15 en cada semestre, 30 anuales. Revisar oferta.',
  33:'Dato obligatorio numerico. Se enlaza 15 desde la misma columna G. No se distribuye ni se divide la cifra entre semestres. Suma anual >0 para vigencia 1.',
  42:'1 CLP, precargado segun criterio monetario del usuario. 2 corresponde a UF. Revisar junto con los importes; numeros sin separadores en futuro CSV.',
  43:'0 precargado por instruccion anterior del usuario: matricula cero; los montos de la columna H de la maqueta corresponden al arancel. Revisar antes de devolver.',
  44:'0 informado por Docencia y enlazado desde Programas, columna I. Es dato disponible, no vacio ni imputacion.',
  45:'0 informado por Docencia y enlazado desde Programas, columna J. Es dato disponible, no vacio ni imputacion.',
  46:'Se enlaza monto de Programas, columna H: aunque su encabezado dice Matricula original, el usuario confirmo que es arancel. Revisar antes de devolver.',
  47:'Confirmar vigencia de cada candidato: 1 vigente con estudiantes nuevos; 2 vigente sin nuevos; 3 no vigente. No altera la Etapa 1 congelada.',
};
for(let i=0;i<48;i++){
  const c=col(i),r=i+9,blank=data.blank_indices.includes(i);
  ruleSheet.getRange(`G${r}:H${r}`).values=[[blank?'DEBE QUEDAR VACIO':'DATO OBLIGATORIO',blank?'NO COMPLETAR':'MODIFICABLE SEGUN REGLA']];
  ruleSheet.getRange(`G${r}:H${r}`).format.fill=blank?fill.blank:fill.required;
  ruleSheet.getRange(`D${r}`).formulas=[[blank?`=COUNTA('Diplomados para completar'!${c}9:${c}30)`:`=COUNTBLANK('Diplomados para completar'!${c}9:${c}30)`]];
  let status=blank?`=IF(D${r}>0,"BORRAR VALOR","VACIO EXIGIDO")`:`=IF(D${r}>0,"FALTA DATO","COMPLETO; VALIDAR")`;
  if(i===3)status='="REVISAR NOMBRES"';
  ruleSheet.getRange(`C${r}`).formulas=[[status]];
  if(customRules[i])ruleSheet.getRange(`E${r}`).values=[[customRules[i]]];
  ruleSheet.getRange(`I${r}`).values=[[`Completar ${c}`]];
  ruleSheet.getRange(`I${r}`).format.font={name:'Arial',size:10,color:'#0563C1',underline:'single'};
  wb.notes.add({id:`regla-preparada-${c}`,target:{cell:{sheetName:s.name,sheetId:s.sheetId,address:`${c}7`}},authorId:'',createdAt:'',body:{plainText:`${customRules[i]||data.reglas[i][4]} Manual: paginas ${data.reglas[i][5]}.`}});
}
ruleSheet.getRange('C9:C56').conditionalFormats.add('containsText',{text:'BORRAR',format:{fill:fill.missing}});
const base=wb.worksheets.getItem('Programas');
const baseChanges={A5:'22 candidatos trasladados a la tercera hoja para completar datos. Las sedes, jornadas y versiones definiran las filas finales de carga.',A6:'Importes H:K conservan los encabezados de esta maqueta. En la tercera hoja se prepara matricula 0 y el monto como arancel, para revisar.',A7:'V06 intacta. Conciliacion final con reporte 6048 pendiente. La tercera hoja contiene 15 vacantes por semestre segun la maqueta revisada.',A41:'Fuente de trabajo: maqueta revisada por el usuario el 23/10/2026. Datos institucionales en F:L; no confundir Periodo con ANIO_INICIO.'};
for(const [address,value] of Object.entries(baseChanges))base.getRange(address).values=[[value]];
wb.recalculate();
if(s.getRange('AG9:AH30').values.some(r=>r.some(v=>v!==15)))throw Error('Vacantes incorrectas');
if(ruleSheet.getRange('A4').values[0][0]!=='Celdas obligatorias vacias: 418. Campos que deben quedar vacios: 9.')throw Error('Conteo faltantes incorrecto');
for(const i of data.blank_indices)if(s.getRange(`${col(i)}9:${col(i)}30`).values.some(r=>r[0]!==null&&r[0]!==''))throw Error('Debe quedar vacio');
for(let i=0;i<22;i++)if(s.getRange(`AU${i+9}`).values[0][0]!==data.candidatos[i].importe)throw Error('Arancel distinto a fuente');
// Exercise a required input and restore it; completeness must never mask other gaps.
s.getRange('S9').values=[[2]];wb.recalculate();
if(ruleSheet.getRange('D27').values[0][0]!==21)throw Error('Contador no reacciona');
s.getRange('S9').clear({applyTo:'contents'});wb.recalculate();
if(ruleSheet.getRange('D27').values[0][0]!==22)throw Error('No restaura faltante');
await fs.writeFile(path.join(audit,'INSPECCION.json'),JSON.stringify(await wb.inspect({kind:'region',sheetId:s.name,range:'P8:U11',maxChars:3000}),null,2));
for(const [sheet,range,n] of [[base.name,'A8:E13','programas'],[ruleSheet.name,'F8:I15','reglas'],[s.name,'J5:U12','academicos'],[s.name,'AO5:AV12','montos']]){
  const img=await wb.render({sheetName:sheet,range,scale:1,format:'png'});
  await fs.writeFile(path.join(here,`maqueta_despues_${n}.png`),new Uint8Array(await img.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(outputs[0]);
// Artifact Tool does not evaluate HYPERLINK; add native internal links without touching cells.
execFileSync('/Users/alexi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',
  [path.join(root,'04_scripts/enlaces_nativos_maqueta_etapa2_20261023.py'),outputs[0]],{stdio:'pipe'});
await fs.copyFile(outputs[0],outputs[1]);
const manifest={fecha:new Date().toISOString(),estado:data.estado,fuentes:data.inputs,maqueta_original:data.snapshot,preferencia_correo:'Usar Estimados/as; no solicitar direccion para borradores',decisiones:data.decisiones,
  cambios_etapa1:0,programas:22,columnas_sies:48,obligatorios:39,vacios_exigidos:9,celdas_obligatorias_sin_dato:418,
  navegacion:'192 enlaces internos nativos: campo y Ver regla; campo y Completar de retorno. Sin formulas HYPERLINK.',ediciones_programas:baseChanges,pendientes:'Completar campos rojos, revisar amarillos y nombres, verificar 6048 y estructura PES 17469. No se genera CSV.',scripts:[],salidas:[]};
for(const p of [fileURLToPath(import.meta.url),path.join(root,'04_scripts/preparar_maqueta_etapa2_v02_20261023.py'),path.join(root,'04_scripts/enlaces_nativos_maqueta_etapa2_20261023.py')])manifest.scripts.push({ruta:p,sha256:hash(await fs.readFile(p))});
for(const p of outputs){const b=await fs.readFile(p);manifest.salidas.push({ruta:p,sha256:hash(b),bytes:b.length});}
for(const [p,info] of Object.entries(data.inputs)){
  if(hash(await fs.readFile(p))!==info.sha256)throw Error('Fuente cambiada '+p);
  if('0o'+((await fs.stat(p)).mode&0o777).toString(8)!==info.modo)throw Error('Permisos cambiados');
}
await fs.writeFile(path.join(gov,'MANIFIESTO.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({outputs,obligatorios:39,vacios_exigidos:9,faltantes:418}));
