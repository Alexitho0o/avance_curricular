import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const tmp=path.dirname(fileURLToPath(import.meta.url));
const d=JSON.parse(await fs.readFile(tmp+'/profile.json','utf8'));
const out=d.out;await fs.mkdir(out,{recursive:true});
const wb=Workbook.create();
const tabs=['Resumen','Por_carrera','Cruce_revision','Ingresos_2025','MU2026_coincidencias','Fuentes_y_pendientes'];
const sh=Object.fromEntries(tabs.map(x=>[x,wb.worksheets.add(x)]));
const navy='#102B42',gold='#CFB47C',gray='#F2F2F2';
const col=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const put=(s,r,c,a,f=false)=>{if(!a.length)return;const q=s.getRangeByIndexes(r-1,c-1,a.length,a[0].length);if(f)q.formulas=a;else q.values=a;};
function setup(s,last,end,title,desc){s.showGridLines=false;const a=s.getRange(`A1:${last}${end}`);a.format.font={name:'Arial',size:10,color:'#3A3A3A'};a.format.columnWidth=19;a.format.rowHeight=23;a.format.verticalAlignment='center';s.getRange('A2').values=[[title]];s.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:navy};s.getRange(`A3:${last}3`).format.borders={bottom:{style:'thin',color:gold}};s.getRange('A4').values=[[desc]];s.tabColor=navy;}
function header(s,r,a){put(s,r,1,[a]);s.getRange(`A${r}:${col(a.length)}${r}`).format={fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:47,horizontalAlignment:'center',verticalAlignment:'center'};}
function table(s,h,data,name){header(s,6,h);put(s,7,1,data);const end=6+data.length;s.tables.add(`A6:${col(h.length)}${end}`,true,name).style='TableStyleLight1';s.freezePanes.freezeRows(6);return end;}
function text(s,r,t){s.getRange(`A${r}`).values=[[t]];}
const origEnd=d.origin.length+6,muEnd=d.mu.length+6,n=d.people.length+6;
const o=sh.Ingresos_2025;
setup(o,'M',origEnd,'Ingresos 2025: filas de los archivos recibidos','B: T2/T3 del archivo correspondiente; todos los estados. C: identidad seudonimizada y fila original para trazabilidad.');
table(o,['Cohorte operacional','ID análisis','Fuente','Fila fuente','ANOINGRESO','PERIODOINGRESO','NOMBRE_L','CODIGOCARRERA','JORNADA','ESTADOACADEMICO','CATEGORIA','ANOMATRICULA','PERIODOMATRICULA'],d.origin,'Ingresos2025');
o.getRange(`G1:G${origEnd}`).format.columnWidth=59;o.getRange(`J1:K${origEnd}`).format.columnWidth=27;o.getRange(`D7:F${origEnd}`).setNumberFormat('0');o.getRange(`L7:M${origEnd}`).setNumberFormat('0');
const m=sh.MU2026_coincidencias;
setup(m,'N',muEnd,'Matrícula unificada 2026: coincidencias por identidad','B/C: 130 filas encontradas tras buscar en las 4.105 filas de 2026. No se filtra por carrera, jornada ni cohorte SIES.');
table(m,['ID análisis','Fila BASE_RETENCION_MU','ANIO_INFORMADO','VIG','COD_SED','COD_CAR','JOR','VERSION','MODALIDAD','ANIO_ING_ORI','SEM_ING_ORI','ANIO_ING_ACT','SEM_ING_ACT','Código único (C)'],d.mu,'CoincidenciasMU');
m.getRange(`N1:N${muEnd}`).format.columnWidth=24;m.getRange(`B7:M${muEnd}`).setNumberFormat('0');
const c=sh.Cruce_revision;
setup(c,'R',n,'Seguimiento por estudiante y cohorte','C: una fila por persona/cohorte. Continúa = al menos una fila MU2026 con VIG=1. E: ausencia no demuestra deserción.');
const ch=['Cohorte operacional','ID análisis','Carrera de origen (C)','Carreras fuente (B)','Estados fuente (B)','Filas origen','Filas MU2026','Filas VIG=1','Filas VIG=0','Continúa (C)','Solo VIG=0 (C)','No localizado (C/E)','Año origen distinto de 2025 (E)','Varias carreras origen (E)','Lectura del seguimiento','Otros VIG (E)','Clasificación','Semestres origen MU (B)'];
header(c,6,ch);
put(c,7,1,d.people.map(p=>[p.cohort,p.person,p.career,p.careers,p.orig_states]));
const mr=x=>`'MU2026_coincidencias'!$${x}$7:$${x}$${muEnd}`;
const or=x=>`'Ingresos_2025'!$${x}$7:$${x}$${origEnd}`;
for(let i=0;i<d.people.length;i++){
 const r=i+7,p=d.people[i];
 put(c,r,6,[[`=COUNTIFS(${or('A')},A${r},${or('B')},B${r})`,`=COUNTIFS(${mr('A')},B${r})`,`=COUNTIFS(${mr('A')},B${r},${mr('D')},1)`,`=COUNTIFS(${mr('A')},B${r},${mr('D')},0)`,`=IF(H${r}>0,1,0)`,`=IF(AND(G${r}>0,I${r}=G${r}),1,0)`,`=IF(G${r}=0,1,0)`,`=IF(COUNTIFS(${mr('A')},B${r},${mr('J')},"<>2025")>0,1,0)`]],true);
 put(c,r,14,[[p.multiple_careers]]);
 put(c,r,15,[[`=IF(J${r}=1,"C: continúa; VIG=1",IF(K${r}=1,"B: localizado solo VIG=0",IF(L${r}=1,"E: no localizado en MU2026","E: revisar estado MU")))`,`=G${r}-H${r}-I${r}`]],true);
 put(c,r,17,[['B/C; causas pendientes E',d.mu.filter(x=>x[0]===p.person).map(x=>x[10]).filter((x,i,a)=>a.indexOf(x)===i).join(' / ')||'No localizado']]);
}
c.tables.add(`A6:R${n}`,true,'Seguimiento').style='TableStyleLight1';c.freezePanes.freezeRows(6);c.getRange(`C1:D${n}`).format.columnWidth=57;c.getRange(`E1:E${n}`).format.columnWidth=27;c.getRange(`O1:O${n}`).format.columnWidth=37;c.getRange(`Q1:Q${n}`).format.columnWidth=28;c.getRange(`F7:N${n}`).setNumberFormat('#,##0');
const cr=x=>`'Cruce_revision'!$${x}$7:$${x}$${n}`;
const groups=[...new Set(d.people.map(p=>JSON.stringify([p.cohort,p.career])))].map(x=>JSON.parse(x)).sort((a,b)=>a[0].localeCompare(b[0])||a[1].localeCompare(b[1]));
const p=sh.Por_carrera;setup(p,'K',groups.length+7,'Continuidad por cohorte y carrera de origen','C: personas únicas; varias carreras en origen se separan para no duplicar estudiantes. Tasa = continúan / estudiantes.');
header(p,6,['Cohorte','Carrera de origen','Estudiantes','Continúan VIG=1','Solo VIG=0','No localizados','Tasa continuidad (C)','Año origen discrepante (E)','Varias carreras (E)','Umbral 10','Control población']);
for(let i=0;i<groups.length;i++){let r=i+7;put(p,r,1,[groups[i]]);const filt=`${cr('A')},A${r},${cr('C')},B${r}`;put(p,r,3,[[`=COUNTIFS(${filt})`,`=SUMIFS(${cr('J')},${filt})`,`=SUMIFS(${cr('K')},${filt})`,`=SUMIFS(${cr('L')},${filt})`,`=IF(C${r}=0,"n.a.",D${r}/C${r})`,`=SUMIFS(${cr('M')},${filt})`,`=SUMIFS(${cr('N')},${filt})`,`=IF(C${r}<10,"BAJO 10; DIAGNÓSTICO","DESDE 10")`,`=C${r}-SUM(D${r}:F${r})`]],true);}
p.tables.add(`A6:K${groups.length+6}`,true,'Carreras').style='TableStyleLight1';p.freezePanes.freezeRows(6);p.getRange(`B1:B${groups.length+7}`).format.columnWidth=59;p.getRange(`C7:F${groups.length+6}`).setNumberFormat('#,##0');p.getRange(`G7:G${groups.length+6}`).setNumberFormat('0.0%');p.getRange(`J1:J${groups.length+7}`).format.columnWidth=27;
const s=sh.Resumen;setup(s,'I',44,'Continuidad de los ingresos 2025-T2 y 2025-T3','C/D: seguimiento en matrícula unificada 2026; estudiantes únicos, incluidos los estados ELIMINADO del origen.');
s.getRange('A1:A44').format.columnWidth=17;s.getRange('B1:B44').format.columnWidth=31;s.getRange('C1:I44').format.columnWidth=20;
put(s,5,1,[['Carrera de origen','Todas']]);s.getRange('B5').format.fill='#FFF2CC';s.getRange('B5').format.font.bold=true;
header(s,7,['Cohorte de ingreso','Estudiantes','Continúan VIG=1','Tasa continuidad (C)','Solo VIG=0','No localizados','Año origen discrepante (E)','Varias carreras (E)','Control población']);
const filter=(r,column)=>{const f=`${cr('A')},A${r}`;const run=extra=>column?`SUMIFS(${cr(column)},${f}${extra})`:`COUNTIFS(${f}${extra})`;return `=IF($B$5="Todas",${run('')},${run(`,${cr('C')},$B$5`)})`;};
for(let r=8;r<=9;r++){put(s,r,1,[[`2025-T${r-6}`]]);put(s,r,2,[[filter(r,null),filter(r,'J'),`=IF(B${r}=0,"n.a.",C${r}/B${r})`,filter(r,'K'),filter(r,'L'),filter(r,'M'),filter(r,'N'),`=B${r}-C${r}-E${r}-F${r}`]],true);}
s.getRange('A8:I9').format.rowHeight=32;s.getRange('B8:C9').setNumberFormat('#,##0');s.getRange('D8:D9').setNumberFormat('0.0%');s.getRange('D8:D9').format.fill='#EAF1F5';s.getRange('E8:I9').setNumberFormat('#,##0');
text(s,11,'Cómo leerlo: la tasa divide estudiantes con VIG=1 en MU2026 por todos los ingresos del archivo de su cohorte.');
text(s,12,'No localizado no equivale a desertor. Solo VIG=0 significa que sí aparece, pero sin una fila vigente en esa fuente.');
text(s,13,'Este es un seguimiento institucional (C), no una tasa anual SIES certificada. T2/T3 no equivale a semestre SIES.');
text(s,14,'La fuente 2026 procede de REPORTE JULIO 2026. No se presenta como una foto exclusiva de 2026-1 ni del 30 de abril.');
const chart=s.charts.add('bar',[s.getRange('A7:A9'),s.getRange('D7:D9')]);chart.title='Continuidad observada en MU2026';chart.titleTextStyle.typeface='Arial';chart.titleTextStyle.fontSize=14;chart.hasLegend=false;chart.setPosition('A16','G30');chart.series.items[0].fill=navy;chart.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:11}};chart.yAxis={numberFormatCode:'0%',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:11}};
header(s,32,['Clase','Pendiente / decisión','Detalle']);s.getRange('C32:I32').merge();
const notes=[
 ['E','Ausencias en MU2026','La fuente no explica por qué faltan estas personas. No se asigna una causa ni se declara deserción.'],
 ['B/E','Cinco años de origen distintos','Dos personas de T2 y tres de T3 tienen ANIO_ING_ORI distinto de 2025. Se identifican en Cruce_revision.'],
 ['C/E','Seis personas con varias carreras','Tres por cohorte. Se cuentan una vez y se muestran en un grupo aparte; la asignación de carrera queda pendiente.'],
 ['D','Denominadores confirmados','T2: todos los ingresos del archivo T2 (222); T3: año 2025 / período 3 en T3_2025 (124). Incluye ELIMINADO.'],
 ['B/D','68 ingresos T2 adicionales','Aparecen en el archivo posterior T3. No se incorporan al denominador T2 por la decisión explícita del usuario.'],
 ['E','Alcance de las fechas','Falta confirmar la fecha efectiva de corte de vigencia. Los archivos recibidos fueron descritos como parciales.'],
 ['C','Navegación','El selector de carrera actualiza la tabla superior y el gráfico. Por_carrera y Cruce_revision permiten filtrar el detalle.']
];
for(let i=0;i<notes.length;i++){let r=33+i;put(s,r,1,[notes[i]]);s.getRange(`C${r}:I${r}`).merge();s.getRange(`A${r}:I${r}`).format.wrapText=true;s.getRange(`A${r}:I${r}`).format.rowHeight=40;if(i%2===0)s.getRange(`A${r}:I${r}`).format.fill=gray;}
text(s,41,'Los pendientes por año de origen o carrera pueden coincidir con estudiantes que continúan; no se suman como exclusiones.');
text(s,42,'Clasificación: A regla oficial · B dato observado · C cálculo técnico · D decisión interna · E pendiente.');
const f=sh.Fuentes_y_pendientes;setup(f,'H',65,'Fuentes, decisiones y trazabilidad','Las fuentes originales no se modifican. El libro muestra solo seudónimos y referencias de fila; no incluye RUT ni nombres personales.');
f.getRange('A1:A65').format.columnWidth=22;f.getRange('B1:B65').format.columnWidth=32;f.getRange('C1:C65').format.columnWidth=85;f.getRange('D1:D65').format.columnWidth=85;f.getRange('E1:E65').format.columnWidth=70;
header(f,6,['ID / clase','Hoja / tipo','Archivo','Ruta','SHA-256','Filas de origen','Bytes','Fecha modificación local']);
put(f,7,1,d.sources.map(x=>[x.id+' / B',x.sheet||'Manifiesto',path.basename(x.path),x.path,x.sha256,x.rows||null,x.bytes||null,x.mtime||null]));f.getRange('C7:H10').format.wrapText=true;f.getRange('A7:H10').format.rowHeight=90;
const rule='/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/gobernanza/sies/RETENCION/REGLA_RETENCION_1ER_ANIO_CORREO_20260909.txt';
const hash=async x=>crypto.createHash('sha256').update(await fs.readFile(x)).digest('hex');
put(f,11,1,[['REGLA / A','Correo congelado',path.basename(rule),rule,await hash(rule),null,null,null]]);f.getRange('C11:E11').format.wrapText=true;f.getRange('A11:H11').format.rowHeight=75;
header(f,14,['Clase','Concepto','Regla aplicada / alcance / pendiente']);
const decisions=[
 ['D','Unidad y denominador','Una persona por cohorte, con identidad RUT+DV válida. Usuario autorizó 222 personas de T2 y 124 de T3, incluidos ELIMINADO; no se usa el universo anual 558/1.150 del libro anterior.'],
 ['C','Cruce exacto','RUT de los listados se compara con N_DOC+DV en MU2026 solo para TIPO_DOC=R. Se quitan puntos/espacios y ceros iniciales y se normaliza K. Se verifica DV; ninguna llave del origen falló. Sin aproximación por nombre.'],
 ['C','Continuidad observada','Al menos una fila del mismo identificador en ANIO_INFORMADO=2026 con VIG=1, sin exigir misma carrera, jornada o semestre. Tasa = suma de indicadores continúa / estudiantes únicos de la cohorte.'],
 ['C/E','Cohorte institucional vs SIES','T2/T3 proviene de ANOINGRESO/PERIODOINGRESO. No se deriva una equivalencia con SEM_ING_ORI. Los cinco ANIO_ING_ORI distintos se marcan, sin eliminar al estudiante ni llamarlo retención oficial.'],
 ['A','Alcance de la regla SIES','Correo 09-09-2026: misma institución y cohorte de origen al año siguiente; regularidad, mínimos 4/6/8 semestres, exclusión de especiales e inconsistencias específicas, publicación desde 10 casos y referencia 30 de abril. No define esta continuidad T2/T3.'],
 ['C','Diferencia frente al motor anual','Este ejercicio sigue todos los ingresos autorizados, no vuelve a aplicar filtros de plan/duración del motor anual. Mide continuidad observada en MU2026; no se compara directamente con la retención publicada por SIES.'],
 ['B','MU2026 verificada','4.105 filas: 3.145 con VIG=1 y 960 con VIG=0. SHA-256 del consolidado coincide con su manifiesto. No tiene columna explícita de código institución; su alcance IPSS se toma del proyecto y de la fuente gobernada.'],
 ['B/C','Proyección de la fuente MU','Se buscó en las 4.105 filas; MU2026_coincidencias conserva las 130 filas encontradas, columnas pertinentes y posición original. Los no localizados permanecen en Cruce_revision. La fuente completa permanece intacta en su ruta.'],
 ['C','Desduplicación','T2: 225 filas / 222 personas; T3: 127 filas / 124 personas. Cada persona repetida tiene varias carreras de origen; se conserva el detalle, se cuenta una vez y se agrupa como MÚLTIPLES CARRERAS (PENDIENTE). No hay personas compartidas entre T2 y T3.'],
 ['B/D','Alcance del archivo T3','La hoja T3_2025 contiene 3.081 filas. Se toman solo ANOINGRESO=2025 y PERIODOINGRESO=3. No se usa la hoja T3 de 111 filas / 110 personas VIGENTE.'],
 ['B/D','Ingresos T2 del archivo posterior','El archivo T3 contiene 290 personas de ingreso 2025-T2: las 222 del archivo T2 y 68 adicionales. Se excluyen esas 68 del denominador solicitado; no se afirma que la lista de 222 represente todos los ingresos institucionales T2.'],
 ['E','Fecha de referencia','El manifiesto identifica REPORTE JULIO 2026 como fuente 2026. Eso no certifica vigencia al 30 de abril ni una instantánea 2026-1. Falta una confirmación del corte efectivo si se desea interpretar la tasa a una fecha exacta.'],
 ['E','Ausencias y VIG=0','Se muestran separadas. Ausencia en la extracción o VIG=0 no entrega por sí sola causa de abandono, retiro o error. No se completa la causa mediante supuestos.'],
 ['C','Fórmulas y actualización','Ingresos_2025 y MU2026_coincidencias son proyecciones trazables de entrada; Cruce_revision calcula presencia y vigencia con COUNTIFS; Por_carrera y Resumen agregan con SUMIFS y dividen retenidos por estudiantes. Para una fuente nueva debe regenerarse el cruce y sus rangos, no pegar filas fuera de tabla.'],
 ['C','Identificadores protegidos','Seudónimos locales asignados a llaves exactas, comunes entre hojas. No son anonimización irreversible: la fila fuente permite revisión autorizada. No se exportan RUT, nombres personales ni fechas de nacimiento.'],
 ['C','Presentación','Colores #102B42, #CFB47C y #F2F2F2 según paleta institucional; Arial disponible como sustitución tipográfica. Conteos #,##0 y porcentajes 0.0%; Excel con región Chile muestra punto de miles y coma decimal.'],
 ['C','Validaciones','Recalculo con artifact-tool; controles independientes por Python, selector de carreras y cambios de VIG. Inspección de ZIP, fórmulas y encabezados. No se declara prueba de apertura en Excel nativo.'],
 ['D','Versionado','Nueva copia que sustituye la interpretación del ejercicio previo, sin alterar ese libro ni los originales. Sin commit ni push; auxiliares locales para reproducibilidad.']
];
put(f,15,1,decisions);f.getRange('C15:C32').format.wrapText=true;f.getRange('A15:C32').format.rowHeight=82;
header(f,35,['Clase','Control independiente','Valor observado']);
put(f,36,1,[['B/C','Filas T2 seleccionadas',225],['B/C','Personas T2',222],['B/C','Filas T3 seleccionadas',127],['B/C','Personas T3',124],['B/C','MU2026: filas buscadas',4105],['B/C','MU2026: filas coincidentes',130],['B/C','Llaves inválidas en origen',0],['B/C','Personas en ambas cohortes',0]]);
const careers=['Todas',...new Set(d.people.map(p=>p.career))].sort((a,b)=>a==='Todas'?-1:b==='Todas'?1:a.localeCompare(b));put(f,6,10,[['Selector de carreras'],...careers.map(x=>[x])]);f.getRange('J1:J35').format.columnWidth=60;wb.names.add('ListaCarreras',`='Fuentes_y_pendientes'!$J$7:$J$${6+careers.length}`);s.getRange('B5').dataValidation={rule:{type:'list',formula1:'ListaCarreras'}};
wb.recalculate();
function expected(career){return ['2025-T2','2025-T3'].map(co=>{const a=d.people.filter(x=>x.cohort===co&&(career==='Todas'||x.career===career));const sum=k=>a.reduce((v,x)=>v+x[k],0);return [a.length,sum('continue'),a.length?sum('continue')/a.length:'n.a.',sum('onlyzero'),sum('absent'),sum('origin_discrepancy'),sum('multiple_careers'),0];});}
function assertMatch(a,b,label){if(JSON.stringify(a)!==JSON.stringify(b))throw new Error(label+JSON.stringify({a,b}));}
assertMatch(s.getRange('B8:I9').values,expected('Todas'),'Summary');
const checks=[];
for(const career of careers){s.getRange('B5').values=[[career]];wb.recalculate();const a=s.getRange('B8:I9').values;assertMatch(a,expected(career),'Selector '+career);checks.push({career,result:'OK'});}
s.getRange('B5').values=[['Todas']];wb.recalculate();
// Perturb an actual matched input, verify propagation and restore it.
const ti=d.mu.findIndex(x=>x[3]===1);const mid=d.mu[ti][0];const who=d.people.find(x=>x.person===mid);const rr=who.cohort==='2025-T2'?8:9;
const before=s.getRange(`C${rr}`).values[0][0];m.getRange(`D${ti+7}`).values=[[0]];wb.recalculate();if(s.getRange(`C${rr}`).values[0][0]!==before-1)throw new Error('VIG mutation did not propagate');m.getRange(`D${ti+7}`).values=[[1]];wb.recalculate();assertMatch(s.getRange('B8:I9').values,expected('Todas'),'Restored');
const err=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},summary:'Formula errors'});await fs.writeFile(out+'/formula_scan.ndjson',err.ndjson);
const dest=out+'/CONTINUIDAD_IPSS_INGRESOS_2025_T2_T3_EN_MU2026_20261020_221157.xlsx';
const x=await SpreadsheetFile.exportXlsx(wb);await x.save(dest);
for(const name of tabs){const range=name==='Resumen'?'A1:I42':name==='Por_carrera'?'A1:K12':name==='Cruce_revision'?'A1:C12':name==='Ingresos_2025'?'A1:H11':name==='MU2026_coincidencias'?'A1:N11':'A14:C18';const blob=await wb.render({sheetName:name,range,scale:1,format:'png'});await fs.writeFile(out+'/'+name+'.png',new Uint8Array(await blob.arrayBuffer()));}
await fs.writeFile(out+'/QA_CONTINUIDAD.json',JSON.stringify({status:'OK',summary:s.getRange('B8:I9').values,expected:expected('Todas'),selector_tests:checks,mutation_vig:'OK: reduce numerador en 1 y se restaura',engine:'artifact-tool; no Excel nativo',formula_scan:err.ndjson},null,2));
await fs.writeFile(out+'/MANIFEST_CONTINUIDAD.json',JSON.stringify({hito_referencia:'H001-RETENCION-IPSS162',proceso:'Seguimiento institucional de continuidad',cohortes:['2025-T2','2025-T3'],observacion:'MU2026; fuente REPORTE JULIO 2026',fecha:d.created,decision_D:'Todos los ingresos del archivo correspondiente: T2=222, T3=124; incluidos ELIMINADO. Confirmación explícita del usuario.',fuentes:d.sources,regla_anual_referencia:{path:rule,sha256:await hash(rule),alcance:'A: no define T2/T3 ni convierte este cálculo C en retención oficial'},llave_C:'RUT normalizado con DV exacto = N_DOC+DV cuando TIPO_DOC=R; búsqueda en ANIO_INFORMADO=2026, sin filtro por cohorte/carrera',numerador_C:'Personas de cada cohorte con al menos una fila VIG=1 en MU2026',denominador_D:'Personas únicas del año/período de ingreso del archivo correspondiente; todos los estados',resultados_C:d.totals,controles_B_C:d.additional,pendientes_E:notes.filter(x=>x[0].includes('E')),salida:{path:dest,sha256:await hash(dest)},originales_sin_modificar:true,git:{rama_antes:'feature/ire-2026',head_antes:'b8140dcba0f179865671cff75f98b9e1041eeb0a',commit:false,push:false},reproducir:'profile.py lee fuentes, valida y seudonimiza; build.mjs crea fórmulas, prueba filtros y exporta; verify.py valida salida y hashes. No identificadores directos en archivos derivados.'},null,2));
console.log(JSON.stringify({output:dest,sha256:await hash(dest),summary:s.getRange('B8:I9').values,formula_scan:err.ndjson}));
