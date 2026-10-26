import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const p=JSON.parse(await fs.readFile(new URL('./entrada_agregada.json',import.meta.url),'utf8'));
const ev=JSON.parse(await fs.readFile(new URL('./evidencia_nombres.json',import.meta.url),'utf8'));
const v3=JSON.parse(await fs.readFile(new URL('./evidencia_temporal_historica.json',import.meta.url),'utf8'));
p.sources.push(...v3.sources);
const targets=new Map(p.foco.map(r=>[r[0],r]));
for(const x of p.cross){const f=targets.get(x[1]);if(f && x[6]===f[2] && x[0]===f[0].slice(0,4)) x[14]='B/C: nombre, sede/jornada y perfil SIES corroborados; E: vigencia del vínculo plan–período';}
for(const x of p.plans){if(targets.has(x[0]))x[8]='B: NOMBRE_L corroborado y perfil SIES disponible. E: vigencia del vínculo con este plan UMAS';}
p.sources.push(...ev.schemas.map(x=>[x.archivo,x.sha256]),...ev.fuentes_adicionales);
const w=Workbook.create(), c=w.worksheets.add('1_Conciliacion'),u=w.worksheets.add('2_Catalogo_UMAS'),s=w.worksheets.add('3_Oferta_y_Matricula_SIES');
const navy='#15354B', blue='#174C78';
function base(sh,title,note){sh.showGridLines=false;sh.getRange('A2').values=[[title]];sh.getRange('A2').format.font={name:'Calibri',size:16,bold:true,color:navy};sh.getRange('A4').values=[[note]];sh.getRange('A4').format.font={name:'Calibri',size:10,color:'#555555'};sh.freezePanes.freezeRows(6);}
function table(sh,range,name){const t=sh.tables.add(range,true,name);t.showBandedRows=true;const head=sh.getRange(range.split(':')[0]+':'+range.split(':')[1].replace(/[0-9]+/,range.split(':')[0].match(/[0-9]+/)[0]));head.format={fill:blue,font:{name:'Calibri',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:42};}
base(c,'UMAS y SIES · conciliación de programas','B/C · Catálogo ≠ asignación individual. Sin cambios de códigos adoptados, bases o denominadores.');
c.getRange('A6:F6').values=[['Plan UMAS','Nombre del programa','Código SIES — correspondencia interna','Contextos revisados','Resultado de la revisión','Pendiente para atribuir']];
c.getRange('A7:F10').values=p.foco.map(r=>[...r,'B/C: correspondencia interna corroborada','E: atribución documental y fecha de migración']);
c.getRange('C12').values=[['Total de contextos del foco']];c.getRange('D12').formulas=[['=SUM(D7:D10)']];
c.getRange('A14').values=[['B · 236 planes en el catálogo; 513 relaciones candidatas de plan/sede/jornada/código para 2026. No son 513 equivalencias cerradas.']];
c.getRange('A15').values=[['B · Los cuatro nombres coinciden con NOMBRE_L de Datos Alumnos 12159 y 11248. Precarga 2026: NIVEL_CARRERA=1; duración=5 sem.']];
c.getRange('A16').values=[['E · TPAS20241 registra actividad bajo TPAS, IINF y NULL. No fusionar automáticamente. Regular y continuidad se revisan por separado.']];
c.getRange('A18:P18').values=[['Carrera UMAS','Plan UMAS','Nombre UMAS del catálogo','Sede UMAS','Jornada UMAS','Año candidato','Código SIES candidato','Nombre SIES anual','Tipo plan SIES','Duración total SIES (sem.)','Nombre literal coincide','Matrícula SIES','Filas MU','Brecha SIES − MU','Estado de equivalencia','Referencia maestro']];
c.getRange(`A19:P${18+p.cross.length}`).values=p.cross;
for(let i=0;i<p.cross.length;i++){const row=i+19,x=p.cross[i],sr=p.oi[x[5]+'|'+x[6]]; if(sr){c.getRange(`H${row}:N${row}`).formulas=[[`='3_Oferta_y_Matricula_SIES'!C${sr}`,`='3_Oferta_y_Matricula_SIES'!I${sr}`,`=IF('3_Oferta_y_Matricula_SIES'!K${sr}="","Pendiente",'3_Oferta_y_Matricula_SIES'!K${sr})`,`=IF(C${row}=H${row},"Sí","Revisar nombre")`,`=IF('3_Oferta_y_Matricula_SIES'!M${sr}="","Sin cobertura",'3_Oferta_y_Matricula_SIES'!M${sr})`,`=IF('3_Oferta_y_Matricula_SIES'!N${sr}="","Sin cobertura",'3_Oferta_y_Matricula_SIES'!N${sr})`,`=IF(AND(ISNUMBER(L${row}),ISNUMBER(M${row})),L${row}-M${row},"Pendiente")`]];}else c.getRange(`H${row}:N${row}`).values=[['Sin oferta anual','Pendiente','Pendiente','Pendiente','Sin cobertura','Sin cobertura','Pendiente']];}
base(u,'Catálogo histórico de planes UMAS','B/C · Conteos de actividad y expedientes del maestro; no matrícula anual. No sumar expedientes de planes distintos como personas únicas.');
u.getRange('A6:K6').values=[['Plan de estudio','Nombre original del catálogo','Carreras en PROMEDIOS','Años con actividad','Jornadas observadas','Filas de asignaturas','Identificadores internos distintos','Códigos SIES candidatos','Equivalencia temporal','Fila ejemplo catálogo','Clase']];u.getRange(`A7:K${6+p.plans.length}`).values=p.plans;
base(s,'Oferta histórica y matrícula por código SIES','B/C · Oferta disponible 2010–2026; conciliación de matrícula 2022–2026. Vacío = sin cobertura, no cero. Totales de matrícula no son retención.');
s.getRange('A6:R6').values=[['Año','Código completo','Nombre SIES original','Sede','Carrera','Jornada','Versión','Nivel global','Tipo de plan','Duración estudios (sem.)','Duración total (sem.)','Vigencia oferta','Matrícula CSV SIES','Filas MU','MU VIG=1','Brecha SIES − MU','Fila fuente','Clase']];s.getRange(`A7:R${6+p.offers.length}`).values=p.offers;
s.getRange(`P7:P${6+p.offers.length}`).formulas=p.offers.map((x,i)=>[`=IF(AND(ISNUMBER(M${i+7}),ISNUMBER(N${i+7})),M${i+7}-N${i+7},"Pendiente")`]);
table(c,'A6:F10','Foco21');table(c,`A18:P${18+p.cross.length}`,'CruceProgramas');table(u,`A6:K${6+p.plans.length}`,'CatalogoUMAS');table(s,`A6:R${6+p.offers.length}`,'OfertaSIES');
for(const sh of [c,u,s]){sh.getUsedRange().format.font.name='Calibri';sh.getUsedRange().format.columnWidth=19;sh.getUsedRange().format.rowHeight=24;sh.getUsedRange().format.verticalAlignment='center';}
c.getRange('B:B').format.columnWidth=52;c.getRange('C:C').format.columnWidth=46;c.getRange('E:F').format.columnWidth=38;c.getRange('H:I').format.columnWidth=48;c.getRange('O:P').format.columnWidth=50;c.getRange('A6:F6').format.rowHeight=42;c.getRange('A18:P18').format.rowHeight=42;
u.getRange('B:B').format.columnWidth=62;u.getRange('H:I').format.columnWidth=62;u.getRange('A6:K6').format.rowHeight=42;
s.getRange('B:B').format.columnWidth=24;s.getRange('C:C').format.columnWidth=65;s.getRange('I:L').format.columnWidth=24;s.getRange('A6:R6').format.rowHeight=42;
c.freezePanes.freezeRows(6);
let r=20+p.cross.length;c.getRange(`A${r}`).values=[['Fuentes y huellas SHA-256 (B/C)']];for(const x of p.sources){r+=2;c.getRange(`A${r}`).values=[[x[0]]];c.getRange(`A${r+1}`).values=[[x[1]]];}
c.getRange(`A${r+3}`).values=[['C · Los totales de L/M se repiten entre candidatos del mismo código: NO sumarlos. Conciliar en hoja 3, una fila por año y código.']];
c.getRange(`A${r+4}`).values=[['D/C · 21 correspondencias contextuales corroboradas en períodos explícitos (hoja 2); no se promueve el diccionario activo ni se modifica retención.']];
u.getRange('L6:Q6').values=[['NOMBRE_L verificado (B)','Sede/jornada observadas (B)','NIVEL alumno observado (B)','Perfil SIES corroborado (B)','Respaldo exacto','Límite de equivalencia (E)']];
for(let i=0;i<p.plans.length;i++){const f=targets.get(p.plans[i][0]);if(!f)continue;const code=f[0].slice(0,4),da=ev.datos_alumnos[code],pr=ev.precarga.find(x=>x.CODIGO_UNICO===f[2]),du=ev.duracion.find(x=>x.CODIGO_UNICO===f[2]);u.getRange(`L${i+7}:Q${i+7}`).values=[[[...new Set(da.map(x=>x.nombre))].join(' |'),'RE / O presentes', [...new Set(da.map(x=>x.nivel_observado))].join(', '),`Nivel carrera ${pr.NIVEL_CARRERA}; tipo plan ${du.TIPO_PLAN_CARRERA}; duración total ${pr.DURACION_TOTAL} sem.`,`Datos Alumnos Hoja1; precarga fila ${pr.fila}; DURACION_ESTUDIOS fila ${du.fila}`,'DA no contiene PLAN_ESTUDIOS; no acredita por sí solo fecha de asignación del plan']];}
u.getRange('L:Q').format.columnWidth=45;u.getRange('L6:Q242').format.wrapText=true;
u.getRange('L6:Q6').format.fill=blue;u.getRange('L6:Q6').format.font.color='#FFFFFF';
c.getRange('E7:F10').format.wrapText=true;c.getRange('A7:F10').format.rowHeight=48;
c.getRange(`A${r+5}`).values=[['B/C · NIVEL del alumno no equivale a NIVEL_CARRERA ni a duración. La precarga acredita datos precargados, no envío/aceptación de una carga.']];
c.getRange(`A${r+6}`).values=[['E · No se usó el estado TITULADO ni el máximo NIVEL observado para inferir duración. Los cuatro perfiles se vinculan solo a los períodos respaldados en la hoja 2; no se extrapolan a otros años o jornadas.']];
// Temporal evidence remains aggregated and limited to reviewed periods.
for(let i=0;i<p.plans.length;i++){const plan=p.plans[i][0],ts=v3.temporal.filter(x=>x[0]===plan);if(!ts.length)continue;u.getRange(`I${i+7}`).values=[['B/C: cerrada internamente en '+ts.map(x=>x[1]+'-P'+x[2]).join(', ')]];u.getRange(`Q${i+7}`).values=[['E: envío individual y fecha de migración; no extrapolar a otros períodos']];}
for(let i=0;i<p.cross.length;i++){const x=p.cross[i],f=targets.get(x[1]);if(f&&x[0]===f[0].slice(0,4)&&x[6]===f[2])c.getRange(`O${i+19}`).values=[['B/C: correspondencia contextual en períodos de hoja 2; E: atribución documental']];}
u.getRange('A246').values=[['Cierre temporal de los cuatro planes — solo períodos observados (B/C; autorización D)']];
u.getRange('A248:J248').values=[['Plan','Año observado','Período nativo','Código SIES','Contextos revisados','Contextos corroborados','Resultado','Referencia exacta','Estado de asignaturas observado','Límite']];
u.getRange(`A249:J${248+v3.temporal.length}`).values=v3.temporal;table(u,`A248:J${248+v3.temporal.length}`,'TemporalPlanes');u.getRange(`A249:J${248+v3.temporal.length}`).format.wrapText=true;u.getRange(`A249:J${248+v3.temporal.length}`).format.rowHeight=70;
const h=w.worksheets.add('4_Historico_y_Cierres');base(h,'Códigos SIES · oferta, matrícula, titulaciones y avance','B/C · 2007–2026. Sin oferta ≠ cierre. Se conserva el histórico y se separa el año académico del año de carga.');
h.getRange('A6:Q6').values=[['Año de datos','Código completo','Nombre SIES de referencia','Oferta del año / situación observada','Primera oferta observada','Última oferta observada','Cierre formal','Matrícula publicada SIES','MU filas observadas','MU VIG=1','Brecha SIES−MU','Titulados distintos por código/año','Avance curricular: filas informadas','Envío / aceptación acreditados','Fuente titulados / año','Fuente avance / año','Clasificación']];
h.getRange(`A7:Q${6+v3.detail.length}`).values=v3.detail;
h.getRange(`K7:K${6+v3.detail.length}`).formulas=v3.detail.map((_,i)=>[`=IF(AND(ISNUMBER(H${i+7}),ISNUMBER(I${i+7})),H${i+7}-I${i+7},"Pendiente")`]);
table(h,`A6:Q${6+v3.detail.length}`,'HistoricoCodigo');h.getUsedRange().format.columnWidth=23;h.getUsedRange().format.font.name='Calibri';h.getRange('C:D').format.columnWidth=48;h.getRange('G:G').format.columnWidth=42;h.getRange('N:P').format.columnWidth=55;h.getUsedRange().format.wrapText=true;h.getUsedRange().format.rowHeight=48;h.getRange('A6:Q6').format.rowHeight=65;
let hr=10+v3.detail.length;h.getRange(`A${hr}`).values=[['C · Titulados: personas distintas dentro de cada código/año, no personas únicas al sumar carreras. MU y avance: filas, no estudiantes únicos.']];h.getRange(`A${hr+1}`).values=[['E · Cero en titulados/avance significa sin registro para ese código en la fuente revisada; no certifica cobertura institucional completa. Sin cobertura no es cero.']];h.getRange(`A${hr+2}`).values=[['E · Avance anual comparable confirmado aquí: 2016–2018. Los archivos de proceso 2020–2022 requieren acreditar su año académico antes de agregarlos.']];h.getRange(`A${hr+3}`).values=[['B/C · Oferta: 2010–2026; matrícula pública: 2007–2026; MU conciliada: 2022–2026. No se atribuye un cierre por última aparición.']];
for(const a of v3.audit){hr+=5;h.getRange(`A${hr}`).values=[[a[0]]];h.getRange(`A${hr+1}`).values=[[a[1]]];}
w.recalculate();
console.log((await w.inspect({kind:'table',range:'1_Conciliacion!C12:D12',include:'values,formulas',tableMaxRows:1,tableMaxCols:2})).ndjson);
const png=await w.render({sheetName:'1_Conciliacion',range:'A6:F12',scale:1.3});await fs.writeFile('/tmp/ipss_catalogo_20261025/vista.png',new Uint8Array(await png.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(w)).save('/Users/alexi/Desktop/IPSS_CONCILIACION_CARRERAS_UMAS_SIES_20261025_V3.xlsx');
console.log('Exportado');
