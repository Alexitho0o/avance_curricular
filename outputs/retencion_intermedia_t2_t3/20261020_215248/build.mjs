import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const input=JSON.parse(await fs.readFile(path.join(path.dirname(fileURLToPath(import.meta.url)),'profile.json'),'utf8'));
const out='/Users/alexi/Documents/GitHub/avance_curricular/outputs/retencion_intermedia_t2_t3/20261020_215248';
await fs.mkdir(out,{recursive:true});
const wb=Workbook.create();
const names=['Resumen','Por_carrera','Cruce_revision','Cohortes_referencia','Listados_recibidos','Fuentes_y_pendientes'];
const sheets=Object.fromEntries(names.map(n=>[n,wb.worksheets.add(n)]));
const navy='#102B42',gold='#CFB47C',blue='#0E4273',gray='#F2F2F2';
const col=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
function put(s,r,c,data,formula=false){if(!data.length)return;const range=s.getRangeByIndexes(r-1,c-1,data.length,data[0].length);if(formula)range.formulas=data;else range.values=data;}
function setup(s,lastCol,rows){s.showGridLines=false;s.getRange(`A1:${lastCol}${rows}`).format.font={name:'Arial',size:10,color:'#3A3A3A'};s.getRange(`A1:${lastCol}${rows}`).format.rowHeight=22;s.getRange(`A1:${lastCol}${rows}`).format.columnWidth=18;s.getRange(`A1:${lastCol}${rows}`).format.verticalAlignment='center';}
function title(s,t,last='H'){s.getRange('A2').values=[[t]];s.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:navy};s.getRange(`A3:${last}3`).format.borders={bottom:{style:'thin',color:gold}};}
function header(s,row,labels){put(s,row,1,[labels]);const r=s.getRange(`A${row}:${col(labels.length)}${row}`);r.format={fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:42,horizontalAlignment:'center',verticalAlignment:'center'};r.format.borders={insideVertical:{style:'thin',color:'#FFFFFF'}};}
function table(s,row,data,labels,name){header(s,row,labels);put(s,row+1,1,data);const end=row+data.length;s.tables.add(`A${row}:${col(labels.length)}${end}`,true,name);s.freezePanes.freezeRows(row);s.getRange(`A${row+1}:${col(labels.length)}${end}`).format.rowHeight=23;return end;}
function note(s,cell,text){s.getRange(cell).values=[[text]];s.getRange(cell).format.font={name:'Arial',size:10,color:'#3A3A3A'};}

const origin=input.origin;
const targetKeys=new Set(origin.filter(r=>r.key_ok).map(r=>`${r.year}|${r.person}`));
const closures=input.closures.filter(r=>targetKeys.has(`${r.cohort}|${r.person}`));
const n=origin.length+6, m=closures.length+6;
const o=sheets.Cohortes_referencia;setup(o,'U',n);title(o,'Cohortes de referencia para la revisión','U');
note(o,'A4','B/C: candidatos de matrícula unificada 2024/2025 y elegibilidad del motor anual existente. No se aprueba aquí el denominador intermedio.');
const od=origin.map(r=>[r.person,r.source_row,r.year,r.origin_year,r.origin_term,r.vig,r.unique_code,r.career,r.area,r.type_doc,r.key_ok?1:0,r.annual_state,r.annual_eligible,r.level,r.plan,r.special,r.duration,r.min_semesters,r.duplicate_active,r.annual_next_any,r.annual_next_cohort]);
table(o,6,od,['ID análisis','Fila RAW','Año informado','Cohorte origen','Sem. origen','VIG origen','Código único origen','Carrera de origen','Área de conocimiento','Tipo documento','Llave comparable (C)','Estado anual heredado (C)','Incluido anual (C)','Nivel global','Tipo plan','Plan especial','Duración estudios','Mín. semestres','Duplicados activos (C)','Siguiente anual vigente (C)','Misma cohorte siguiente (C)'],'CohortesReferencia');
o.getRange(`B7:F${n}`).setNumberFormat('0');o.getRange('G1:G'+n).format.columnWidth=24;o.getRange('H1:H'+n).format.columnWidth=58;o.getRange('I1:I'+n).format.columnWidth=27;o.getRange('L1:L'+n).format.columnWidth=34;
o.getRange(`A7:A${n}`).format.font.color='#666666';

const l=sheets.Listados_recibidos;setup(l,'O',m);title(l,'Listados parciales recibidos','O');
note(l,'A4','B/C: solo filas con RUT coincidente en candidatos de la cohorte objetivo (358 filas). Se conservan repeticiones y filas fuente. El inventario completo está en Fuentes_y_pendientes.');
const ld=closures.map(r=>[r.source,r.sheet,r.row,r.person,r.year,r.term,r.entry_year,r.entry_term,r.enrol_year,r.enrol_term,r.state,r.career,r.career_code,r.dv_ok?1:0,null]);
table(l,6,ld,['Fuente cierre','Hoja original','Fila original','ID análisis','Año cierre solicitado','T solicitado','ANOINGRESO','PERIODOINGRESO','ANOMATRICULA','PERIODOMATRICULA','ESTADOACADEMICO','Carrera informada','Código interno','DV válido (C)','Primera persona/cierre (C)'],'ListadosParciales');
put(l,7,15,closures.map((r,i)=>{const row=i+7;return [`=IF(COUNTIFS($A$7:A${row},A${row},$D$7:D${row},D${row})=1,1,0)`];}),true);
l.getRange('B1:B'+m).format.columnWidth=24;l.getRange('K1:K'+m).format.columnWidth=24;l.getRange('L1:L'+m).format.columnWidth=60;l.getRange('M1:M'+m).format.columnWidth=25;

const c=sheets.Cruce_revision;setup(c,'W',n);title(c,'Cruce por persona: revisión de cobertura','W');
note(c,'A4','C: RUT exacto normalizado con DV, sin aproximación por nombre. E: ausencia de un listado parcial no prueba deserción. Pasaportes sin equivalencia quedan pendientes.');
const ch=['ID análisis','Cohorte','Fila RAW','Código único origen','Carrera de origen','Área','Estado anual referencia','Incluido anual (C)','Llave comparable (C)','Filas T2','Filas VIGENTE T2','Filas otro estado T2','Filas sin estado T2','Filas T3','Filas VIGENTE T3','Filas otro estado T3','Filas sin estado T3','Persona localizada T2','Persona VIGENTE T2','Persona localizada T3','Persona VIGENTE T3','Lectura T2','Lectura T3'];
header(c,6,ch);
const cr=origin.map((r,i)=>{const row=i+7;const q=x=>`'Cohortes_referencia'!${x}${row}`;const range=x=>`'Listados_recibidos'!$${x}$7:$${x}$${m}`;
 const cnt=(term,state)=>`COUNTIFS(${range('A')},"T${term}_"&(B${row}+1),${range('D')},A${row}${state?`,${range('K')},"${state}"`:''})`;
 return [`=${q('A')}`,`=${q('C')}`,`=${q('B')}`,`=${q('G')}`,`=${q('H')}`,`=${q('I')}`,`=${q('L')}`,`=${q('M')}`,`=${q('K')}`,
 `=IF(I${row}=1,${cnt(2)},0)`,`=IF(I${row}=1,${cnt(2,'VIGENTE')},0)`,`=J${row}-K${row}-M${row}`,`=IF(I${row}=1,${cnt(2,'NO INFORMADO')},0)`,
 `=IF(I${row}=1,${cnt(3)},0)`,`=IF(I${row}=1,${cnt(3,'VIGENTE')},0)`,`=N${row}-O${row}-Q${row}`,`=IF(I${row}=1,${cnt(3,'NO INFORMADO')},0)`,
 `=IF(J${row}>0,1,0)`,`=IF(K${row}>0,1,0)`,`=IF(N${row}>0,1,0)`,`=IF(O${row}>0,1,0)`,
 `=IF(I${row}=0,"E: sin llave comparable",IF(J${row}=0,"E: no localizado; lista parcial",IF(K${row}>0,"B: localizado VIGENTE",IF(M${row}>0,"E: localizado sin estado","B: localizado otro estado"))))`,
 `=IF(I${row}=0,"E: sin llave comparable",IF(N${row}=0,"E: no localizado; lista parcial",IF(O${row}>0,"B: localizado VIGENTE",IF(Q${row}>0,"E: localizado sin estado","B: localizado otro estado"))))`];});
put(c,7,1,cr,true);c.tables.add(`A6:W${n}`,true,'CrucesRevision');c.freezePanes.freezeRows(6);c.getRange('E1:E'+n).format.columnWidth=57;c.getRange('F1:F'+n).format.columnWidth=26;c.getRange('G1:G'+n).format.columnWidth=34;c.getRange('V1:W'+n).format.columnWidth=42;c.getRange(`B7:C${n}`).setNumberFormat('0');

const p=sheets.Por_carrera;const groups=[...new Set(origin.map(r=>JSON.stringify([r.year,r.career])))].map(x=>JSON.parse(x)).sort((a,b)=>a[0]-b[0]||a[1].localeCompare(b[1]));
setup(p,'L',groups.length+6);title(p,'Revisión por cohorte y carrera','L');note(p,'A4','C: conteos sobre el universo anual de referencia. E: los cierres son parciales; no se publican tasas ni se interpreta ausencia como deserción.');
header(p,6,['Cohorte','Carrera de origen','Candidatos MU','Universo anual ref.','Sin llave RUT','Localizados T2','VIGENTE T2','Localizados T3','VIGENTE T3','Tasa T2','Tasa T3','Clasificación']);
const range=x=>`'Cruce_revision'!$${x}$7:$${x}$${n}`;
const pd=groups.map(([y,car],i)=>{let r=i+7;return [y,car,null,null,null,null,null,null,null,'Pendiente','Pendiente','C / E'];});put(p,7,1,pd);
put(p,7,3,groups.map((g,i)=>{const r=i+7;const flt=`${range('B')},A${r},${range('E')},B${r}`;const ct=`${flt},${range('H')},1`;
return [`=COUNTIFS(${flt})`,`=COUNTIFS(${ct})`,`=COUNTIFS(${ct},${range('I')},0)`,`=SUMIFS(${range('R')},${ct})`,`=IF(A${r}=2025,"n.d.",SUMIFS(${range('S')},${ct}))`,`=SUMIFS(${range('T')},${ct})`,`=SUMIFS(${range('U')},${ct})`];}),true);
p.tables.add(`A6:L${groups.length+6}`,true,'CarrerasRevision');p.freezePanes.freezeRows(6);p.getRange('B1:B'+(groups.length+6)).format.columnWidth=59;p.getRange(`C7:I${groups.length+6}`).setNumberFormat('#,##0');

const f=sheets.Fuentes_y_pendientes;setup(f,'M',125);title(f,'Fuentes, alcance y pendientes','M');f.getRange('A1:A125').format.columnWidth=24;f.getRange('B1:B125').format.columnWidth=36;f.getRange('C1:C125').format.columnWidth=75;f.getRange('D1:D125').format.columnWidth=90;f.getRange('E1:E125').format.columnWidth=65;
header(f,6,['ID','Clasificación / tipo','Archivo o regla','Ruta / alcance','SHA-256 / evidencia','Hoja','Filas','Bytes','Modificación local','RUT distintos (C)','Filas VIGENTE (B/C)','Otros estados (B/C)','Sin estado (B/C)']);
const rule='/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/gobernanza/sies/RETENCION/REGLA_RETENCION_1ER_ANIO_CORREO_20260909.txt';
const sha=async path=>crypto.createHash('sha256').update(await fs.readFile(path)).digest('hex');
const sourceRows=input.sources.map(s=>[s.id,'B: fuente institucional parcial',s.path.split('/').at(-1),s.path,s.sha256,s.sheet,s.records,s.bytes,s.mtime,s.unique_keys,s.states.VIGENTE||0,s.records-(s.states.VIGENTE||0)-(s.states['NO INFORMADO']||0),s.states['NO INFORMADO']||0]);
sourceRows.push(['MU_ORIGEN','B: matrícula unificada informada',input.raw_source.path.split('/').at(-1),input.raw_source.path,input.raw_source.sha256,input.raw_source.sheet,input.raw_source.rows,null,null,null,null,null,null]);
sourceRows.push(['MOTOR_ANUAL','C: implementación de referencia',input.engine_source.path.split('/').at(-1),input.engine_source.path,input.engine_source.sha256,input.engine_source.sheet,10200,null,null,null,null,null,null]);
sourceRows.push(['REGLA_SIES','A: comunicación oficial anual','Correo Rodrigo Rolando Meneses, 09-09-2026',rule,await sha(rule),'Texto congelado',null,null,null,null,null,null,null]);
put(f,7,1,sourceRows);f.getRange('C7:E13').format.wrapText=true;f.getRange('A7:I13').format.rowHeight=65;
const decisions=[
 ['D','Alcance confirmado por Alexi','Los cuatro archivos son listados parciales. Preparar revisión y señalar bases faltantes; no cerrar tasas de retención.'],
 ['A','Regla anual SIES','Misma institución y cohorte de origen al año siguiente; programas regulares de duración mínima 4/6/8 semestres; excluye especiales e inconsistencias específicas; publicación desde 10 casos; referencia al 30 de abril. No define T2/T3.'],
 ['C','Universo de referencia','Se reproduce, solo para delimitar la revisión, la lógica observada en 02_COHORTE_ELEGIBILIDAD del motor existente. Candidatos: año origen = año informado y semestre 1 o 2. Universo anual de referencia: 558 (2024), 1.150 (2025). No es aprobación de un nuevo denominador intermedio.'],
 ['C','Fórmulas originales sin caché','El motor tiene fórmulas sin valores guardados. Se evaluaron en lectura su catálogo, filtros y conteos anuales; se reprodujeron los dos universos. El archivo original no se modificó. En este derivado, el estado anual es un insumo técnico C; los cruces y resúmenes son fórmulas vivas.'],
 ['C','Llave y privacidad','TIPO_DOC=R: N_DOC normalizado + DV se compara exactamente con RUT completo del cierre. Se quitan puntos/espacios, se normaliza K y ceros iniciales. DV validado; no se aproxima por nombre. Se sustituyen identificadores por ID de análisis, con hoja/fila original para auditoría local.'],
 ['E','Documentos P','20 estudiantes del universo anual 2025 tienen TIPO_DOC=P. No se establece equivalencia pasaporte-RUT. Se muestran como sin llave comparable, no como ausentes.'],
 ['C','Unidad de conteo','El resumen cuenta una vez cada persona del universo anual por cierre. Listados_recibidos conserva solo las 358 filas coincidentes con los candidatos de la cohorte objetivo; el perfil completo se conserva aquí. Repeticiones no multiplican personas. Una fila VIGENTE no prueba retención oficial.'],
 ['E','Cohorte en cierres','ANOINGRESO/PERIODOINGRESO son campos operacionales; no se equiparan automáticamente con ANIO_ING_ORI/SEM_ING_ORI SIES. Para una tasa intermedia deben confirmarse cobertura, fecha y tratamiento de la cohorte.'],
 ['E','Vigencia no informada','T2-2026 no tiene ESTADOACADEMICO ni VIG. Su ausencia se muestra como n.d.; no se transforma en VIGENTE ni en no vigente.'],
 ['B/C','Selección de hojas','T2-2025: T2_2025; T3-2025: T3_2025; T2-2026: Hoja1; T3-2026: Base. Las otras hojas se inventarían y no se concatenan: hay copias/subconjuntos y estados diferentes.'],
 ['E','Lectura de una ausencia','No localizado en estos listados parciales no equivale a desertor ni a no retenido. Los conteos de presencia no son tasas; no se divide por el universo para producir una tasa provisional.'],
 ['C','Filtros y carreras','Resumen: elegir carrera en B5. Los cuatro cruces y el gráfico responden juntos. Por_carrera contiene todas las carreras y ambas cohortes con autofiltros. La carrera pertenece al origen SIES, aunque el estudiante figure en otra carrera del cierre.'],
 ['C','Fuentes intactas','No se copian originales al repositorio. El XLSX derivado está ignorado por Git; los archivos auxiliares quedan locales sin agregar ni commitear. No se ejecuta push. ID de análisis es seudónimo local, no anonimización irreversible.'],
 ['C','Formato','Paleta IPSS: #102B42, #CFB47C, #0E4273, #F2F2F2. Arial como tipografía disponible; no se declara cumplimiento tipográfico íntegro del manual.'],
];
header(f,16,['Clase','Tema','Definición / decisión / pendiente']);put(f,17,1,decisions);f.getRange('C17:C30').format.wrapText=true;f.getRange('A17:C30').format.rowHeight=78;
header(f,33,['Cierre','Cohorte objetivo','Base faltante / condición para continuar']);
const missing=[['2025-T2',2024,'Matrícula completa vigente al cierre 2025-T2 de todas las cohortes (incluida 2024), con identidad exacta y fecha/estado del cierre. La entrega actual solo contiene ingresos 2025-T2.'],['2025-T3',2024,'Listado completo o certificación de completitud de T3_2025 y estados efectivos a ese cierre. El usuario confirmó que la entrega es parcial. Incluye varios años de ingreso, pero eso no prueba cobertura total.'],['2026-T2',2025,'Matrícula completa vigente al cierre 2026-T2, incluida cohorte 2025. Incorporar estado o certificación de que todas sus filas estaban vigentes a esa fecha. La entrega actual solo contiene ingresos 2026-T2.'],['2026-T3',2025,'Matrícula completa vigente al cierre 2026-T3 de todas las cohortes, incluida 2025. Base solo contiene PERIODOINGRESO=3 y la hoja 2026_3 solo ingresos 2026.'],['Todas',null,'Confirmar fecha exacta del corte, cobertura completa y vínculo de documentos pasaporte-RUT cuando corresponda. Mantener la cohorte de origen SIES; no reemplazarla por ingreso operacional sin validación.']];
put(f,34,1,missing);f.getRange('C34:C38').format.wrapText=true;f.getRange('A34:C38').format.rowHeight=75;
header(f,41,['Fuente','Hoja','Uso','Filas no vacías después de fila 1','Columnas declaradas']);put(f,42,1,input.inventory.map(v=>[v.source,v.sheet,v.role,v.rows_used,v.dimensions[1]]));f.getRange('C42:C54').format.wrapText=true;f.getRange('A42:E54').format.rowHeight=38;
note(f,'A57','B: los conteos de hojas auxiliares describen filas ocupadas, no personas.');
header(f,60,['Fuente','Campo observado','Distribución (B)']);
const profiles=input.sources.flatMap(s=>[['ANOINGRESO',s.entry_years],['PERIODOINGRESO',s.entry_terms],['ESTADOACADEMICO',s.states]].map(([field,counts])=>[s.id,field,Object.entries(counts).map(([k,v])=>`${k}: ${v}`).join('; ')]));put(f,61,1,profiles);f.getRange('C61:C72').format.wrapText=true;f.getRange('A61:C72').format.rowHeight=45;
const careers=['Todas',...new Set(origin.map(r=>r.career))].sort((a,b)=>a==='Todas'?-1:b==='Todas'?1:a.localeCompare(b));put(f,6,15,[['Carreras para selector'],...careers.map(x=>[x])]);f.getRange('O1:O25').format.columnWidth=60;

const s=sheets.Resumen;setup(s,'J',49);s.tabColor=navy;title(s,'Retención intermedia: revisión de bases','J');
note(s,'A4','D/E: listados parciales confirmados. Tasas pendientes; los cruces siguientes son observaciones de cobertura.');
put(s,5,1,[['Carrera','Todas']]);s.getRange('B5').format={fill:'#FFF2CC',font:{name:'Arial',size:10,bold:true,color:navy},columnWidth:54};wb.names.add('ListaCarreras',`='Fuentes_y_pendientes'!$O$7:$O$${6+careers.length}`);s.getRange('B5').dataValidation={rule:{type:'list',formula1:'ListaCarreras'}};
header(s,7,['Cohorte','Cierre revisado','Universo anual de referencia','Sin llave comparable','Personas localizadas','Con estado VIGENTE','No localizados*','Tasa intermedia','Clase']);
const sr=[];for(let i=0;i<4;i++){const src=input.sources[i],r=i+8;sr.push([src.cohort,`${src.year}-T${src.term}`,null,null,null,null,null,'Pendiente','C / E']);}put(s,8,1,sr);
const statFormula=(r,cohort,numCol,extra='')=>{const ct=`${range('B')},A${r},${range('H')},1${extra}`;return `=IF($B$5="Todas",${numCol?`SUMIFS(${range(numCol)},${ct})`:`COUNTIFS(${ct})`},${numCol?`SUMIFS(${range(numCol)},${ct},${range('E')},$B$5)`:`COUNTIFS(${ct},${range('E')},$B$5)`})`;};
for(let i=0;i<4;i++){const r=i+8,src=input.sources[i];put(s,r,3,[[statFormula(r,src.cohort,null),statFormula(r,src.cohort,null,`,${range('I')},0`),statFormula(r,src.cohort,src.term===2?'R':'T'),i===2?'="n.d."':statFormula(r,src.cohort,src.term===2?'S':'U'),`=C${r}-D${r}-E${r}`]],true);}
s.getRange('A1:A49').format.columnWidth=14;s.getRange('C1:G49').format.columnWidth=19;s.getRange('H1:I49').format.columnWidth=18;s.getRange('J1:J49').format.columnWidth=3;s.getRange('A8:I11').format.rowHeight=30;s.getRange('C8:G11').setNumberFormat('#,##0');s.getRange('H8:H11').format.fill='#FFF2CC';
note(s,'A13','* No localizado solo significa que el RUT no aparece en el listado parcial. No significa deserción.');
note(s,'A14','El universo anual es una referencia heredada del análisis previo; la tasa intermedia se definirá con bases completas.');
note(s,'A15','n.d.: T2-2026 no informa estado de vigencia. Las personas sin llave comparable se separan de las no localizadas.');
const chart=s.charts.add('bar',[s.getRange('B7:B11'),s.getRange('E7:E11')]);chart.title='Personas localizadas en los listados parciales';chart.titleTextStyle.typeface='Arial';chart.titleTextStyle.fontSize=14;chart.hasLegend=false;chart.setPosition('A17','F31');chart.series.items[0].fill=navy;chart.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:11}};chart.yAxis={numberFormatCode:'#,##0',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:11}};
header(s,33,['Cierre','Archivo / hoja recibida','Filas (B)','RUT distintos (C)','VIGENTE: filas (C)','Otros estados: filas (C)','Sin estado: filas (C)','Cobertura','Clase']);
for(let i=0;i<4;i++){const r=i+34,src=input.sources[i];put(s,r,1,[[`${src.year}-T${src.term}`,`${src.id} / ${src.sheet}`,null,null,null,null,null,'Parcial','B / D']]);
put(s,r,3,[[`='Fuentes_y_pendientes'!G${i+7}`,`='Fuentes_y_pendientes'!J${i+7}`,`='Fuentes_y_pendientes'!K${i+7}`,`='Fuentes_y_pendientes'!L${i+7}`,`='Fuentes_y_pendientes'!M${i+7}`]],true);}
note(s,'A39','Esta tabla describe todos los registros recibidos; no cambia con el selector de carrera.');
note(s,'A41','Falta la matrícula completa vigente de cada cierre, con fecha exacta, identificación y estado verificable.');
note(s,'A42','T3-2025 tiene varios años de ingreso; su amplitud no acredita cobertura completa.');
note(s,'A44','Cómo revisar: seleccione carrera arriba; abra Por_carrera para comparar y Cruce_revision para seguir cada coincidencia.');
note(s,'A45','Fuentes_y_pendientes conserva hashes, hojas elegidas, decisiones A/B/C/D/E y detalle de las cuatro bases faltantes.');
note(s,'A47','Retención oficial anual SIES y seguimiento intermedio T2/T3 tienen fechas de referencia distintas.');
for(const sh of Object.values(sheets)){for(const t of sh.tables.items)t.style='TableStyleLight1';}
s.getRange('A8:A11').format.horizontalAlignment='center';s.getRange('C8:G11').format.horizontalAlignment='right';
p.getRange(`A7:A${groups.length+6}`).format.horizontalAlignment='center';
c.getRange(`B7:C${n}`).format.horizontalAlignment='center';o.getRange(`B7:F${n}`).format.horizontalAlignment='center';l.getRange(`C7:J${m}`).format.horizontalAlignment='center';

// Independent numeric controls for the review. No invented rates are calculated.
wb.recalculate();
const actual=s.getRange('C8:G11').values;
const expected=input.sources.map((r,i)=>[r.included,origin.filter(x=>x.year===r.cohort&&x.annual_eligible&&!x.key_ok).length,r.match,i===2?'n.d.':r.match_vig,r.included-origin.filter(x=>x.year===r.cohort&&x.annual_eligible&&!x.key_ok).length-r.match]);
if(JSON.stringify(actual)!==JSON.stringify(expected))throw new Error('Summary mismatch '+JSON.stringify({actual,expected}));
const chosen='INGENIERIA EN INFORMATICA';s.getRange('B5').values=[[chosen]];wb.recalculate();
const selected=s.getRange('C8:G11').values;
const byId=new Map();for(const r of closures){const k=r.source+'|'+r.person;byId.set(k,[...(byId.get(k)||[]),r]);}
const checkSelected=input.sources.map((r,i)=>{const b=origin.filter(x=>x.year===r.cohort&&x.annual_eligible&&x.career===chosen);const key=b.filter(x=>x.key_ok);const match=key.filter(x=>byId.has(r.id+'|'+x.person));return [b.length,b.length-key.length,match.length,i===2?'n.d.':match.filter(x=>byId.get(r.id+'|'+x.person).some(y=>y.state==='VIGENTE')).length,key.length-match.length];});
if(JSON.stringify(selected)!==JSON.stringify(checkSelected))throw new Error('Selector mismatch');
s.getRange('B5').values=[['Todas']];wb.recalculate();
await fs.writeFile(out+'/QA_REVISION.json',JSON.stringify({summary:actual,expected,selector_test:{career:chosen,actual:selected,expected:checkSelected},status:'OK_REVISION; TASAS_PENDIENTES',scope:'Recalculo artifact-tool; Excel nativo pendiente de comprobación'},null,2));
const err=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},summary:'Error scan'});await fs.writeFile(out+'/formula_scan.ndjson',err.ndjson);
console.log('QA',JSON.stringify({actual,expected,errors:err.ndjson}));
const dest=out+'/REVISION_RETENCION_INTERMEDIA_IPSS_2024_2025_T2_T3_20261020.xlsx';const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(dest);console.log('EXPORTED',dest);
for(const name of names){const range=name==='Resumen'?'A1:I47':name==='Por_carrera'?'A1:L13':name==='Cruce_revision'?'A1:I11':name==='Cohortes_referencia'?'A1:L11':name==='Listados_recibidos'?'A1:K11':'A1:E10';const blob=await wb.render({sheetName:name,range,scale:1,format:'png'});await fs.writeFile(out+'/'+name+'.png',new Uint8Array(await blob.arrayBuffer()));}
await fs.writeFile(out+'/MANIFEST_REVISION.json',JSON.stringify({proceso:'Seguimiento intermedio de retención IPSS 162',cohortes:[2024,2025],cierres:['2025-T2','2025-T3','2026-T2','2026-T3'],fecha:'2026-10-20',estado:'REVISION_COMPLETA; TASAS_BLOQUEADAS_POR_COBERTURA_PARCIAL',decision_D:'Alexi confirmó listados parciales y solicitó preparar revisión y señalar bases faltantes.',fuentes:[...input.sources,input.raw_source,input.engine_source,{path:rule,sha256:await sha(rule)}],salida:{path:dest,sha256:await sha(dest)},pendientes_E:missing,fuentes_sin_modificar:true,git:{rama_antes:'feature/ire-2026',head_antes:'b8140dcba0f179865671cff75f98b9e1041eeb0a',commit:false,push:false},clasificacion:{A:'Regla SIES anual citada; no normativa T2/T3',B:'Contenido observado en fuentes',C:'Normalización exacta, evaluación técnica del motor anual, fórmulas y conteos',D:'Revisión de listados parciales confirmada por usuario',E:'Cobertura, fecha de cierre, denominador intermedio y documentos no comparables'},proteccion:'No RUT, N_DOC, nombres, apellidos, fecha de nacimiento ni contacto personal en el derivado. IDs locales seudonimizados y filas fuente para trazabilidad.'},null,2));
console.log('DONE');
