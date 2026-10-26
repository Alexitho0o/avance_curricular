import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const dir=path.dirname(fileURLToPath(import.meta.url));
const read=async n=>JSON.parse(await fs.readFile(path.join(dir,'insumos',n+'.json'),'utf8'));
const [hist,comb,capas,gov,names,req]=await Promise.all(['resumen','combinaciones','capas','gobierno','nombres_catalogo','requisitos'].map(read));
const qa=JSON.parse(await fs.readFile(path.join(dir,'QA_CONSULTA.json'),'utf8'));
const v=capas.v17;
const wb=Workbook.create();
const sheets=['Resumen','Carreras V17','Contextos V17','Historico','Gobierno y QA'].map(n=>wb.worksheets.add(n));
const [s,ca,cv,h,g]=sheets;
const navy='#102B42', blue='#0E4273', gold='#CFB47C', light='#F2F2F2', amber='#FFF1D6';
const count='#,##0', pct='0.00%';
function init(sh,widths,lastRow){
  sh.showGridLines=false;
  const end=String.fromCharCode(65+widths.length-1);
  sh.getRange(`A1:${end}${lastRow}`).format.font={name:'Arial',size:11,color:'#3A3A3A'};
  sh.getRange(`A1:${end}${lastRow}`).format.rowHeight=24;
  sh.getRange(`A1:${end}${lastRow}`).format.verticalAlignment='center';
  widths.forEach((w,i)=>sh.getRangeByIndexes(0,i,lastRow,1).format.columnWidth=w);
}
function title(sh,text){sh.getRange('B2').values=[[text]];sh.getRange('B2').format.font={size:17,bold:true,color:navy};}
function note(sh,cell,text){sh.getRange(cell).values=[[text]];sh.getRange(cell).format.font={size:10,color:'#555555'};}
function head(sh,range,values){let r=sh.getRange(range);r.values=[values];r.format={fill:navy,font:{color:'#FFFFFF',bold:true},wrapText:true,horizontalAlignment:'center',rowHeight:42};}
function table(sh,range,name){const t=sh.tables.add(range,true,name);t.showFilterButton=true;t.showBandedRows=false;return t;}
function formula(sh,cell,f){sh.getRange(cell).formulas=[[f]];}
function formatCounts(sh,range){sh.getRange(range).setNumberFormat(count);sh.getRange(range).format.horizontalAlignment='right';}
function warn(sh,range){sh.getRange(range).conditionalFormats.add('cellIs',{operator:'greaterThan',formula:0,format:{fill:amber,font:{color:'#7B4600'}}});}
const label=code=>(names.nombres_por_codigo[code]||[code]).join(' / ');

// Fuente agregada del Excel V17. Cada fila es un código de carrera UMAS.
init(ca,[3,14,65,13,14,13,13,13,15,16,18,65,12],42);title(ca,'Cobertura del código SIES en la V17');
note(ca,'B3','Las observaciones distinguen persona, expediente, plan y período. No son personas únicas ni tasas de retención.');
note(ca,'B4','Nombres orientativos del catálogo por código UMAS. No se usan para cruzar ni para asignar una versión.');
head(ca,'B7:M7',['Código UMAS','Nombres en catálogo','Observaciones','Documentales','Solo internas','Pendientes','Con código','Cobertura','Pendientes multiversión','Estado','Qué falta','Clase']);
const careers=[...v.por_carrera].sort((a,b)=>b.pendientes-a.pendientes||a.carrera_umas.localeCompare(b.carrera_umas));
const reasons=Object.fromEntries(v.planes_con_pendientes.map(r=>[r.carrera_umas,r.razones.join('. ')]));
const crows=careers.map(r=>[r.carrera_umas,label(r.carrera_umas),r.observaciones,r.documentales,r.internos,r.pendientes,null,null,r.pendientes_multiversion,null,reasons[r.carrera_umas]||'Sin excepciones en los contextos revisados.', 'B/C; D; E']);
ca.getRange('B8:M27').values=crows;
for(let row=8;row<=27;row++){
 formula(ca,`H${row}`,`=SUM(E${row}:F${row})`);formula(ca,`I${row}`,`=H${row}/D${row}`);
 formula(ca,`K${row}`,`=IF(G${row}=0,"Completo","Pendiente")`);
}
table(ca,'B7:M27','CarrerasV17');ca.getRange('C8:C27').format.wrapText=true;ca.getRange('L8:L27').format.wrapText=true;
ca.getRange('B8:M27').format.rowHeight=72;
formatCounts(ca,'D8:H28');formatCounts(ca,'J8:J28');ca.getRange('I8:I28').setNumberFormat(pct);warn(ca,'G8:G27');
ca.getRange('B28').values=[['TOTAL']];for(const col of ['D','E','F','G','H','J'])formula(ca,`${col}28`,`=SUM(${col}8:${col}27)`);formula(ca,'I28','=H28/D28');
ca.getRange('B28:M28').format.fill=light;ca.getRange('B28:M28').format.font.bold=true;
note(ca,'B31','Multiversión usa la familia del código T1 de origen; la carrera del contexto posterior puede ser distinta.');
note(ca,'B32','El pendiente de código no significa abandono. Los estados de matrícula y la retención se evalúan por separado.');
note(ca,'B34','Fuente S02: V17, hojas 52–54, manifiesto de seguimiento v13 y reconsulta actual al servicio v7.');
ca.freezePanes.freezeRows(7);

// Todos los grupos temporales de la V17, no solamente los pendientes.
init(cv,[3,14,23,9,11,10,11,13,13,13,13,14,15,42,48,72,12],108);title(cv,'Combinaciones por año y período en la V17');
note(cv,'B3','Una fila = carrera UMAS + plan + sede + jornada + año observado + período nativo. Se conservan todos los grupos.');
note(cv,'B4','Período nativo 2/3 es el contexto del análisis ya construido; este reporte no crea conversiones de calendario.');
head(cv,'B7:Q7',['Código UMAS','Plan UMAS','Sede','Jornada SIES','Año','Período','Observaciones','Documentales','Solo internas','Pendientes','Con código','Cobertura','Códigos T1 de origen','Códigos destino respaldados','Pendiente del cruce','Clase']);
const contexts=[...v.combinaciones_contextuales].sort((a,b)=>b.pendientes-a.pendientes||a.carrera_umas.localeCompare(b.carrera_umas)||a.anio_observado-b.anio_observado||a.periodo_nativo.localeCompare(b.periodo_nativo));
cv.getRange(`B8:Q${7+contexts.length}`).values=contexts.map(r=>[r.carrera_umas,r.plan,r.sede_observada,r.jornada_sies_observada,r.anio_observado,r.periodo_nativo,r.observaciones,r.documentales,r.internos,r.pendientes,null,null,r.codigos_origen.join('\n'),r.codigos_destino.join('\n')||'Pendiente',r.motivos_pendientes.join('. ')||'Sin excepción en este grupo.', 'B/C; D; E']);
for(let row=8;row<=7+contexts.length;row++){formula(cv,`L${row}`,`=SUM(I${row}:J${row})`);formula(cv,`M${row}`,`=L${row}/H${row}`);}
table(cv,`B7:Q${7+contexts.length}`,'ContextosV17');cv.getRange(`N8:P${7+contexts.length}`).format.wrapText=true;cv.getRange(`B8:Q${7+contexts.length}`).format.rowHeight=80;
formatCounts(cv,`H8:L${7+contexts.length}`);cv.getRange(`M8:M${7+contexts.length}`).setNumberFormat(pct);cv.getRange(`F8:F${7+contexts.length}`).setNumberFormat('0');warn(cv,`K8:K${7+contexts.length}`);cv.freezePanes.freezeRows(7);
note(cv,'B97','Fuente S02. Los códigos enumerados pertenecen a observaciones resueltas; no son asignables a todas las personas del grupo.');

// Auditoría histórica: 93 grupos, con todos sus códigos y excepciones.
init(h,[3,14,24,9,11,15,14,14,14,14,15,18,45,72,12],144);title(h,'Diccionario histórico completo: 2019–2026');
note(h,'B3','Combinación = carrera UMAS + plan + sede + jornada. Completa significa que sus observaciones revisadas tienen código.');
note(h,'B4','No significa una equivalencia universal: 17 combinaciones tienen varios códigos en un mismo año/período.');
head(h,'B7:O7',['Código UMAS','Plan UMAS','Sede','Jornada SIES','Observaciones','Documentales','Solo internas','Pendientes','Con código','Cobertura','Estado del grupo','Códigos respaldados','Qué falta','Clase']);
const hc=[...comb].sort((a,b)=>b.pendientes-a.pendientes||a.carrera.localeCompare(b.carrera)||a.plan.localeCompare(b.plan));
h.getRange('B8:O100').values=hc.map(r=>[r.carrera,r.plan,r.sede_dimension,r.jornada_sies,r.observaciones,r.documentadas,r.solo_internas,r.pendientes,null,null,null,r.codigos_respaldados.join('\n')||'Pendiente',r.pendiente_concreto,'B/C; D; E']);
for(let row=8;row<=100;row++){formula(h,`J${row}`,`=SUM(G${row}:H${row})`);formula(h,`K${row}`,`=J${row}/F${row}`);formula(h,`L${row}`,`=IF(I${row}=0,"Completa",IF(J${row}=0,"Sin resolver","Parcial"))`);}
table(h,'B7:O100','CombinacionesHistoricas');h.getRange('M8:N100').format.wrapText=true;h.getRange('B8:O100').format.rowHeight=76;
formatCounts(h,'F8:J101');h.getRange('K8:K101').setNumberFormat(pct);warn(h,'I8:I100');
h.getRange('B101').values=[['TOTAL']];for(const col of ['F','G','H','I','J'])formula(h,`${col}101`,`=SUM(${col}8:${col}100)`);formula(h,'K101','=J101/F101');h.getRange('B101:O101').format.fill=light;h.getRange('B101:O101').format.font.bold=true;
const requirements=[['Plan aplicable al período',2650,'Asignación del plan y continuidad, migración o reingreso. El perfil del grupo por sí solo no lo acredita.','B/C; E'],['Perfil de programa/plan',202,'Completar duración, tipo de plan y contexto que usa el método.','B/C; E'],['Versiones coexistentes',94,'Atributo o equivalencia que distingue las versiones aplicables.','B/C; E'],['Grupo/programa',51,'Identificar el grupo con evidencia del programa y período.','B/C; E'],['Fecha ausente o múltiple',32,'Acreditar la fecha pertinente, sin inferirla del nombre del plan.','B/C; E'],['Oferta de nuevos compatible',19,'Aclarar compatibilidad de oferta, plan y contexto.','B/C; E'],['Homologación en plan rechazado',1,'Acreditar el plan realmente cursado; no forzar una versión.','B/C; E']];
note(h,'B104','Los motivos detallados están en Gobierno y QA. Una decisión interna acotada requiere aprobación.');
note(h,'B105','2.651 pendientes tienen candidato único calculado, pero no adoptado. Candidato único no equivale a vínculo probado.');
note(h,'B106','Fuente S01. Las 63 combinaciones pendientes actuales no son las 63 dimensiones de la prueba histórica de dominancia.');
h.freezePanes.freezeRows(7);

// Gobierno, fuentes y controles. Es un área terminal, sin alimentar cálculos.
init(g,[3,39,35,69,69,13],84);title(g,'Dónde está gobernado y qué falta conectar');
note(g,'B3','Verificación del 25-10-2026. Tener un archivo local o su hash no demuestra que esté publicado ni sincronizado.');
head(g,'B6:F6',['Capa','Estado observado','Qué se verificó','Qué falta','Clase']);
g.getRange('B7:F12').values=gov.executive_rows.map(r=>[r.capa,r.estado,r.evidencia,r.falta,r.clasificacion]);g.getRange('B7:E12').format.wrapText=true;g.getRange('B7:F12').format.rowHeight=104;table(g,'B6:F12','Gobernanza');
head(g,'B15:E15',['Control ejecutado','Resultado','Alcance o límite','Clase']);
const qarows=[['Consultas del histórico','24.774; 0 diferencias','Contra el contenido activo. No es una prueba independiente de aceptación SIES.','B/C'],['Consultas del seguimiento V17','2.854; 0 diferencias','La hoja 54 y los contextos privados reproducen el servicio v7.','B/C'],['Tres consumidores locales',qa.paridad_consumidores?'MISMA RESPUESTA':'DIFERENCIA','Se probaron documental, interno y pendiente en los tres consumidores.','C'],['Pruebas sintéticas',qa.pruebas_sinteticas_codigo_salida===0?'12 correctas':'FALLO','No extrapolación, conflictos, identidad, temporalidad y adjudicación.','C'],['Fuentes fijadas en descriptor',`${qa.fuentes_coincidentes} coinciden; ${qa.fuentes_con_diferencia} difieren; ${qa.fuentes_no_leibles} no leíbles`,'Hash actual contra el registrado. No acredita cobertura universal de las fuentes.','B/C'],['V17 del Escritorio','SIN CAMBIOS','SHA-256 8b461d53f75ac26e2e38aa46d0aae921736d21ac2a64034cfd26c08495756a52','B/C'],['Aceptación SIES','NO ACREDITADA EN ESTE SERVICIO','No significa rechazo. Código documental observado no es prueba de aceptación del envío.','B/E'],['Plan frente a versión','NO ES UNIVERSALMENTE UNO A UNO','Incluso 3 combinaciones completas necesitan contexto individual dentro del mismo período.','B/C'],['Complementos GPT heredados','REMOTO PENDIENTE','Se verificaron cachés KPI, Gestor Académico y Matrícula. No sus versiones remotas actuales.','B/E'],['Tipografía y visualización','Arial; paleta IPSS','Paleta del Manual de Marca, pág. 10. Arial como alternativa legible. Recálculo Artifact Tool; no apertura nativa Excel.','C']];
g.getRange('B16:E25').values=qarows;g.getRange('B16:D25').format.wrapText=true;g.getRange('B16:E25').format.rowHeight=62;
head(g,'B28:E28',['Conciliación matemática','Diferencia esperada 0','Interpretación','Clase']);
g.getRange('B29:B32').values=[['Histórico: partes versus total'],['V17: partes versus total'],['V17: contextos versus carreras'],['Histórico: motivos versus pendientes']];
formula(g,'C29',"=SUM('Historico'!G101:I101)-'Historico'!F101");formula(g,'C30',"=SUM('Carreras V17'!E28:G28)-'Carreras V17'!D28");formula(g,'C31',"=SUM('Contextos V17'!H8:H93)-'Carreras V17'!D28");formula(g,'C32',"=SUM(C53:C59)-'Historico'!I101");
g.getRange('D29:E32').values=Array.from({length:4},()=>['Sin diferencia entre los agregados comparados.','C']);
g.getRange('C29:C32').conditionalFormats.add('cellIs',{operator:'notEqual',formula:0,format:{fill:'#FCE3E3',font:{color:'#A00000'}}});
head(g,'B35:E35',['Referencia','Archivo o recurso','Huella / versión','Clase']);
const refs=[
 ['S01. Servicio activo','data/diccionario_sies_seguimiento/activo.json',hist.edicion,'B/C/D'],
 ['S01. Descriptor',hist.descriptor,'9037a9a8eb324dafa6b0535b0e66bd50425a058be8295f0edd405339115ac1b8','B/C'],
 ['S01. Base privada','DICCIONARIO_SIES.sqlite; ruta fijada en descriptor',hist.base_privada_sha256,'B'],
 ['S02. V17','/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261024_V17.xlsx',v.sha256,'B'],
 ['S02. Seguimiento','outputs/seguimiento_t1_hasta_2026_20261023_v13/MANIFEST_SEGUIMIENTO.json',capas.fuentes[Object.keys(capas.fuentes).find(k=>k.endsWith('MANIFEST_SEGUIMIENTO.json'))],'B/C'],
 ['S03. Git','avance_curricular / feature/ire-2026',gov.main_head,'B'],
 ['S04. Complemento remoto','Análisis institucional de Alexi',`v${gov.remote_plugin.version}; 21-10-2026; ${gov.remote_plugin.text_files_checked} archivos de texto`,'B'],
 ['S05. Nombres de catálogo',names.fuente,names.sha256,'B'],
 ['S06. Marca','Manual de Marca IP San Sebastián, página 10','78b3ec0c8b1a55276ee00d961bf8e6800757de8ac5b3903c15ae93294d513a47','A visual'],
];
g.getRange(`B36:E${35+refs.length}`).values=refs;g.getRange(`B36:D${35+refs.length}`).format.wrapText=true;g.getRange(`B36:E${35+refs.length}`).format.rowHeight=70;
note(g,'B47','A: oficial. B: observado. C: cálculo/implementación. D: decisión interna. E: pendiente.');
note(g,'B48','No se cambiaron asignaciones, bases, motores, denominadores ni la V17. Este informe queda local, sin commit/push.');
head(g,'B52:E52',['Pendiente histórico registrado','Observaciones','Qué evidencia falta','Clase']);
g.getRange('B53:E59').values=requirements;g.getRange('B53:D59').format.wrapText=true;g.getRange('B53:E59').format.rowHeight=68;
formula(g,'C60','=SUM(C53:C59)');g.getRange('B60').values=[['TOTAL PENDIENTE HISTÓRICO']];formatCounts(g,'C53:C60');
note(g,'B62','Se muestran requisitos guardados; no se exige un día exacto cuando la evidencia o una decisión aprobada permite resolver el período.');
note(g,'B64','Origen T1: 3.179 registros con código. Existen 6.358 posiciones origen×T2/T3: 2.838 tienen contexto y 3.520 no.');
note(g,'B65','Esas posiciones dan 2.854 contextos de expediente. Sin contexto no equivale a deserción ni a los 104 códigos pendientes.');

// Resumen de salida. Lee las tablas agregadas, no depende de controles de QA.
init(s,[3,48,15,15,15,15,15,16,14],59);title(s,'UMAS a código único SIES: resultado verificado');s.tabColor=navy;
s.getRange('B4').values=[['La relación está construida, pero el objetivo aún no está al 100%.']];s.getRange('B4').format.font={bold:true,size:13,color:blue};
note(s,'B5','La V17 usa el diccionario v7. Falta cerrar excepciones y publicar/conectar esa edición en GitHub, complementos y skills.');
head(s,'B7:I7',['Alcance revisado','Total','Documentales','Solo internos','Con código','Pendientes','Cobertura','Clase']);
s.getRange('B8').values=[['Seguimiento del Excel V17']];for(const [dest,source] of [['C8','D28'],['D8','E28'],['E8','F28'],['F8','H28'],['G8','G28'],['H8','I28']])formula(s,dest,`='Carreras V17'!${source}`);
s.getRange('B9:E9').values=[['V17: orígenes con varias versiones',1077,1040,13]];formula(s,'F9','=SUM(D9:E9)');formula(s,'G9','=C9-F9');formula(s,'H9','=F9/C9');
s.getRange('B10').values=[['Histórico completo del diccionario']];for(const [dest,source] of [['C10','F101'],['D10','G101'],['E10','H101'],['F10','J101'],['G10','I101'],['H10','K101']])formula(s,dest,`='Historico'!${source}`);
s.getRange('I8:I10').values=[['B/C; D; E']];formatCounts(s,'C8:G10');s.getRange('H8:H10').setNumberFormat(pct);warn(s,'G8:G10');s.getRange('B8:I10').format.rowHeight=38;
note(s,'B12','Son porcentajes de cobertura del código, no tasas de retención. La fila multiversión es parte de V17: no se suma.');
note(s,'B13','Observación = una persona en un expediente, plan y período. Una persona puede tener varias observaciones.');
note(s,'B14','La cobertura considera solo contextos localizados. Los 3.179 orígenes T1 ya tienen código; ausencia de contexto no prueba abandono.');
head(s,'B16:G16',['Combinaciones revisadas','Total','Completas','Parciales','Sin resolver','Con pendiente']);
s.getRange('B17:F17').values=[['En el Excel V17',26,10,16,0]];formula(s,'G17','=SUM(E17:F17)');
s.getRange('B18').values=[['En el histórico completo']];formula(s,'C18',"=COUNTA('Historico'!B8:B100)");formula(s,'D18',"=COUNTIFS('Historico'!L8:L100,\"Completa\")");formula(s,'E18',"=COUNTIFS('Historico'!L8:L100,\"Parcial\")");formula(s,'F18',"=COUNTIFS('Historico'!L8:L100,\"Sin resolver\")");formula(s,'G18','=SUM(E18:F18)');formatCounts(s,'C17:G18');warn(s,'G17:G18');
note(s,'B20','Combinación = carrera UMAS + plan + sede + jornada. Al separar año/período, V17 tiene 86 grupos y 42 con pendientes.');
note(s,'B21','V17: 12 de 20 códigos de carrera UMAS tienen pendientes. Histórico: 33 de 46. No son nombres de carreras deduplicados.');
note(s,'B22','Completa = todas las observaciones revisadas tienen código. No autoriza asignar una versión única a cualquier persona del plan.');
head(s,'B25:D25',['Por qué quedan pendientes en V17','Observaciones','Clase']);
s.getRange('B26:D29').values=[['Jornada candidata distinta del origen',63,'B/C; E'],['Otra carrera, sede o institución candidata',34,'B/C; E'],['Versión o plan aún sin atribuir',5,'B/C; E'],['Sin candidato/contexto de familia',2,'B/C; E']];s.getRange('B30').values=[['TOTAL PENDIENTE V17']];formula(s,'C30','=SUM(C26:C29)');formatCounts(s,'C26:C30');
note(s,'B32','En el histórico, 2.650 pendientes requieren acreditar el plan aplicable al período; vea el desglose en Gobierno y QA.');
head(s,'B35:D35',['¿Está disponible para todos?','Estado','Clase']);
s.getRange('B36:D39').values=[['Diccionario local y sus tres consumidores','Funciona','B/C'],['Diccionario personal v7 en GitHub','No publicado','B'],['Complemento remoto y skills','Conexión pendiente','B/E'],['V17: hojas 52–54 con diccionario vigente','Confirmado','B/C']];s.getRange('C36:C39').format.columnWidth=22;
note(s,'B41','C2 y los catálogos publicados son capas distintas. No sustituyen al servicio personal v7.');
note(s,'B42','Las hojas 30–51 de V17 conservan cifras históricas. El antiguo 24/63 no mide el pendiente actual.');
note(s,'B43','Los códigos documentados no prueban por sí solos aceptación SIES. Las correspondencias internas conservan su clasificación D.');
note(s,'B45','Verificación: 24.774 consultas históricas y 2.854 de V17 sin diferencias; 79 fuentes conservan su hash.');
note(s,'B46','Fuentes y límites detallados en Gobierno y QA. Corte de esta auditoría: 25-10-2026.');
note(s,'B48','No se alteraron las bases, los denominadores ni la V17. No se hizo commit ni push.');

// Prueba funcional reversible de las fórmulas de detalle y resumen.
const original=ca.getRange('E8').values[0][0];
const originalSum=s.getRange('F8').values[0][0];
ca.getRange('E8').values=[[original+1]];wb.recalculate();
const dependencyPass=s.getRange('F8').values[0][0]===originalSum+1;
ca.getRange('E8').values=[[original]];wb.recalculate();
if(!dependencyPass||s.getRange('F8').values[0][0]!==originalSum)throw new Error('No se propaga el cambio de entrada al resumen');
const summary=await wb.inspect({kind:'table',range:'Resumen!B7:I18',include:'values,formulas',tableMaxRows:12,tableMaxCols:8,maxChars:5500});
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'Errores de fórmula'});
await fs.writeFile(path.join(dir,'QA_FORMULAS.json'),JSON.stringify({summary:summary.ndjson,errors:errors.ndjson,dependencyPass},null,2));
for(const [sheet,range,name] of [['Resumen','B2:I46','resumen'],['Carreras V17','B7:M13','carreras'],['Contextos V17','B7:Q12','contextos'],['Historico','B7:O12','historico'],['Gobierno y QA','B6:F12','gobierno']]){
 const image=await wb.render({sheetName:sheet,range,scale:1,format:'png'});
 await fs.writeFile(path.join(dir,`${name}.png`),new Uint8Array(await image.arrayBuffer()));
}
const output=await SpreadsheetFile.exportXlsx(wb);
await output.save(path.join(dir,'DICCIONARIO_UMAS_SIES_RESUMEN_VERIFICADO_20261025.xlsx'));
console.log(summary.ndjson);console.log(errors.ndjson);
