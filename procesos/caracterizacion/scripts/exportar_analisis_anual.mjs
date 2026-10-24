import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';
import {prepareDashboard, bindDashboardCharts, verifyDashboardLinks, rateFormat} from './renderizar_paneles_anual.mjs';

const [input, outputDir, flag] = process.argv.slice(2);
const payload = JSON.parse(await fs.readFile(input, 'utf8'));
const percentFormat = rateFormat;
const colors = {title:'#102B42',header:'#0E4273',input:'#EAF1F7',text:'#3A3A3A'};
const memoryStages=[];
function letter(n) {
  let value='';
  for(n++;n>0;n=Math.floor((n-1)/26)) value=String.fromCharCode(65+(n-1)%26)+value;
  return value;
}
function literal(v) { return typeof v==='string' && v.startsWith('=') ? "'"+v : v; }
function progress(message) {
  const heapMiB=Math.round(process.memoryUsage().heapUsed/1024/1024);
  memoryStages.push({stage:message,heapMiB});
  console.log(`[EXCEL] ${message}; memoria=${heapMiB} MiB`);
}
function releaseTemporaryMemory() {
  if(globalThis.gc) globalThis.gc();
}

function build(tables, linked) {
  const book=Workbook.create();
  for(const table of tables) book.worksheets.add(table.name);
  for(const [index,table] of tables.entries()) {
    progress(`Preparando ${table.name} (${table.dashboard?`${Object.keys(table.formulas).length} celdas calculadas`:table.rows.length+' filas'}${table.stream_source_literals?'; literales por escritura incremental':''})`);
    if(table.dashboard) {prepareDashboard(book,table,payload);continue;}
    const sheet=book.worksheets.getItem(table.name);
    const last=letter(table.headers.length-1);
    const end=Math.max(7,table.rows.length+6);
    sheet.showGridLines=false;
    // Wide source exports avoid unnecessary font/wrap formatting; alignment is shared.
    const raw=table.name.startsWith('Respuestas P');
    const streamed=Boolean(table.stream_source_literals);
    const visibleEnd=streamed?Math.min(end,11):end;
    sheet.getRange(`A1:${raw?'G11':`${last}${end}`}`).format.font={name:'Arial',size:11,color:colors.text};
    sheet.getRange('A1:G1').merge();
    sheet.getRange('A1').values=[[`${table.name} · ${payload.year}`]];
    sheet.getRange('A1:G1').format={fill:colors.title,font:{name:'Arial',size:14,bold:true,color:'#FFFFFF'},rowHeight:32};
    sheet.getRange('A3:G4').merge();
    sheet.getRange('A3').values=[[table.note || 'Control del corte anual, sin filtros de vista.']];
    sheet.getRange('A3:G4').format.wrapText=true;
    sheet.getRange('A3:G4').format.rowHeight=30;
    if(linked) {
      sheet.getRange('A2:C2').merge();
      sheet.getRange('A2').values=[['Selección común: hoja Filtros']];
      sheet.getRange('D2:G2').merge();
      const limit=tables.find(t=>t.name==='Filtros').rows.length+6;
      const selected=[1,2,3].map(p=>`IF(COUNTIFS('Filtros'!$A$7:$A$${limit},"Período",'Filtros'!$B$7:$B$${limit},"P${p}",'Filtros'!$C$7:$C$${limit},"Sí")=1,"P${p} ","")`);
      sheet.getRange('D2').formulas=[['="Períodos: "&'+selected.join('&')]];
    }
    sheet.getRangeByIndexes(5,0,1,table.headers.length).values=[table.headers];
    if(table.rows.length) {
      if(raw) {
        // Empty source cells need no stored cell objects in wide survey exports.
        for(let column=0;column<table.headers.length;column++) {
          let start=0;
          const rowsToWrite=streamed?Math.min(5,table.rows.length):table.rows.length;
          while(start<rowsToWrite) {
            if(table.rows[start][column]==null || table.rows[start][column]==='') {start++;continue;}
            let end=start+1;
            while(end<rowsToWrite && table.rows[end][column]!=null && table.rows[end][column]!=='') end++;
            sheet.getRangeByIndexes(start+6,column,end-start,1).values=table.rows.slice(start,end).map(row=>[literal(row[column])]);
            start=end;
          }
        }
      } else for(let start=0;start<table.rows.length;start+=500) {
        const rows=table.rows.slice(start,start+500);
        assert.ok(rows.every(r=>r.length===table.headers.length), `Columnas desalineadas: ${table.name}`);
        sheet.getRangeByIndexes(start+6,0,rows.length,table.headers.length).values=rows.map(r=>r.map(literal));
      }
      // Excel limits table column labels to 255 characters. Preserve raw headers intact.
      if(!streamed && table.headers.every(h=>h.length<=255) && new Set(table.headers).size===table.headers.length) {
        const nativeTable=sheet.tables.add(`A6:${last}${end}`,true,`Tabla${linked?'A':'Q'}${index+1}`);
        nativeTable.style='TableStyleMedium2';
        if(['Conteos personas','Perfiles selección'].includes(table.name)) nativeTable.showFilterButton=false;
      }
    } else sheet.getRange('A7').values=[['Sin registros']];
    sheet.getRange(`A6:${last}6`).format={fill:colors.header,font:{bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:44};
    sheet.getRange(`A7:A${visibleEnd}`).format.rowHeight=30;
    if(!raw) {
      sheet.getRange(`A7:${last}${end}`).format.wrapText=true;
    }
    sheet.getRange(`A6:${last}${visibleEnd}`).format.horizontalAlignment='center';
    sheet.getRange(`A6:${last}${visibleEnd}`).format.verticalAlignment='center';
    for(let c=0;c<table.headers.length;c++) {
      sheet.getRangeByIndexes(5,c,1,1).format.columnWidth=table.widths?.[c] ?? 24;
    }
    if(!table.name.startsWith('Respuestas P')) {
      let blockStart=0,blockHeight=30;
      function flushHeight(end) {
        if(blockHeight>30) sheet.getRange(`A${blockStart+7}:A${end+6}`).format.rowHeight=blockHeight;
      }
      for(let r=0;r<table.rows.length;r++) {
        const lines=Math.max(...table.rows[r].map((value,c)=>Math.ceil(String(value??'').length/((table.widths?.[c]??24)*.9))));
        const height=Math.max(30,Math.min(400,lines*15+8));
        if(height!==blockHeight) {flushHeight(r);blockStart=r;blockHeight=height;}
      }
      flushHeight(table.rows.length);
    }
    for(const c of table.percent_columns || []) sheet.getRange(`${letter(c)}7:${letter(c)}${end}`).setNumberFormat(percentFormat);
    for(const c of table.decimal_columns || []) sheet.getRange(`${letter(c)}7:${letter(c)}${end}`).setNumberFormat('0.0');
    for(const cell of table.percent_cells || []) sheet.getRange(cell).setNumberFormat(percentFormat);
    for(const validation of table.validations || []) {
      sheet.getRange(validation.range).dataValidation={rule:{type:'list',values:validation.values}};
      sheet.getRange(validation.range).format.fill=colors.input;
    }
    sheet.freezePanes.freezeRows(6);
    if(table.chart) {
      const chart=sheet.charts.add('bar',sheet.getRange(table.chart.range));
      chart.setPosition(table.chart.start,table.chart.end);
      chart.title=table.chart.title;
      chart.titleTextStyle.fontSize=12;
      chart.titleTextStyle.typeface='Arial';
      chart.hasLegend=false;
      chart.yAxis={numberFormatCode:'General',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};
      chart.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:10}};
    }
  }
  // The engine recalculates on each write: populate inputs first, then dependencies.
  const order=['Perfiles selección','Base anual','Conteos personas','Respuestas P1','Respuestas P2','Respuestas P3',
    'Participación','Preguntas','Financiamiento','Rendimiento','Respuestas abiertas','Resumen',
    'Ranking carreras','Selector preguntas','Opciones panel','Índices panel','Carreras sector',...tables.filter(t=>t.dashboard).map(t=>t.name)];
  for(const table of [...tables].sort((a,b)=>order.indexOf(a.name)-order.indexOf(b.name))) {
    const sheet=book.worksheets.getItem(table.name);
    progress(`Formulas ${table.name}`);
    const formulaColumns=new Map();
    for(const [address,formula] of Object.entries(table.formulas || {})) {
      assert.ok(formula.length<8192,`Fórmula demasiado larga: ${table.name}!${address}`);
      const [,column,row]=address.match(/^([A-Z]+)(\d+)$/);
      if(!formulaColumns.has(column)) formulaColumns.set(column,[]);
      formulaColumns.get(column).push([Number(row),formula]);
    }
    for(const [column,entries] of formulaColumns) {
      entries.sort((a,b)=>a[0]-b[0]);
      let group=[];
      function flush() {
        if(group.length) sheet.getRange(`${column}${group[0][0]}:${column}${group.at(-1)[0]}`).formulas=group.map(x=>[x[1]]);
        group=[];
      }
      for(const item of entries) {
        if(group.length && item[0]!==group.at(-1)[0]+1) flush();
        group.push(item);
      }
      flush();
      if(table.stream_source_literals) {
        sheet.getRange(`${column}${entries[0][0]}:${column}${entries.at(-1)[0]}`).format.horizontalAlignment='center';
        sheet.getRange(`${column}${entries[0][0]}:${column}${entries.at(-1)[0]}`).format.verticalAlignment='center';
      }
    }
  }
  progress('Recalculando');
  book.recalculate();
  // Bind after calculation so the first formula value is not mistaken for a header.
  for(const table of tables.filter(t=>t.chart)) {
    const sheet=book.worksheets.getItem(table.name);
    sheet.charts.items[0].setData(sheet.getRange(table.chart.range));
  }
  for(const table of tables.filter(t=>t.dashboard)) bindDashboardCharts(book,table);
  progress('Calculo terminado');
  return book;
}

function verifyHeadline(book,expected) {
  const values=book.worksheets.getItem('Resumen').getRange('B7:B11').values.map(r=>r[0]);
  assert.deepEqual(values,expected,'Conciliación de matrículas/personas/estados contra control independiente');
}

function verifyCells(book,checks) {
  for(const [sheet,cell,value] of checks || []) {
    const actual=book.worksheets.getItem(sheet).getRange(cell).values[0][0];
    if(typeof value==='number' && typeof actual==='number') {
      assert.ok(Math.abs(actual-value)<=1e-10,`${sheet}!${cell}: ${actual} != ${value}`);
    } else assert.equal(actual,value,`${sheet}!${cell}`);
  }
}

async function validate(book,tables,prefix) {
  const errors=[];
  for(const table of tables) {
    const sheet=book.worksheets.getItem(table.name);
    // Only computed cells: a verbatim open answer may itself contain an Excel error string.
    for(const cell of Object.keys(table.formulas || {})) {
      const value=sheet.getRange(cell).values[0][0];
      if(typeof value==='string' && /^#(REF!|DIV\/0!|VALUE!|NAME\?|N\/A|NUM!|NULL!|SPILL!|CALC!)/.test(value)) errors.push(`${table.name}!${cell}: ${value}`);
    }
    const range=table.dashboard?table.preview:table.name==='Resumen'?'A1:J21':['Preguntas','Financiamiento','Participación'].includes(table.name)?'A1:J11':'A1:G11';
    const preview=await book.render({sheetName:table.name,range,scale:1,format:'png'});
    await fs.writeFile(path.join(outputDir,'04_AUDITORIA',`${prefix}_${table.name.replaceAll('/','_')}.png`),new Uint8Array(await preview.arrayBuffer()));
    for(const extra of table.extra_previews || []) {
      const image=await book.render({sheetName:table.name,range:extra.range,scale:1,format:'png'});
      await fs.writeFile(path.join(outputDir,'04_AUDITORIA',`${prefix}_${table.name}_${extra.name}.png`),new Uint8Array(await image.arrayBuffer()));
    }
  }
  assert.deepEqual(errors,[],'Errores de cálculo');
}

await fs.mkdir(path.join(outputDir,'02_SALIDAS'),{recursive:true});
await fs.mkdir(path.join(outputDir,'04_AUDITORIA'),{recursive:true});
let main=build(payload.main,true);
verifyHeadline(main,payload.expected);
verifyCells(main,payload.expected_cells);
verifyDashboardLinks(main,payload);
let filterChecks=0;
let localChecks=0;
if(flag==='--verify-filters') {
  const table=payload.main.find(t=>t.name==='Filtros');
  const sheet=main.worksheets.getItem('Filtros');
  for(const test of payload.filter_tests) {
    const selection=new Map(test.selection);
    const dimensions=['Período','Sector','Modalidad','Sede','Carrera','Jornada'];
    const next=table.rows.map(r=> {
      const values=selection.get(dimensions.indexOf(r[0]));
      return [values===undefined || values.includes(r[1]) ? 'Sí':'No'];
    });
    const previous=sheet.getRange(`C7:C${table.rows.length+6}`).values;
    // Setting values already recalculates dependencies; avoid invalidating unchanged controls.
    let start=0;
    while(start<next.length) {
      if(next[start][0]===previous[start][0]) {start++;continue;}
      let end=start+1;
      while(end<next.length && next[end][0]!==previous[end][0]) end++;
      sheet.getRange(`C${start+7}:C${end+6}`).values=next.slice(start,end);
      start=end;
    }
    verifyHeadline(main,test.expected);
    verifyCells(main,test.expected_cells);
    verifyDashboardLinks(main,payload);
    filterChecks++;
    releaseTemporaryMemory();
    progress(`Filtro ${filterChecks}/${payload.filter_tests.length} verificado`);
  }
  sheet.getRange(`C7:C${table.rows.length+6}`).values=table.rows.map(()=>['Sí']);
  main.recalculate();
  verifyHeadline(main,payload.expected);
  verifyCells(main,payload.expected_cells);
  // Local selectors must refresh without expanding the common filter selection.
  const explorer=main.worksheets.getItem('Explorador preguntas');
  const options=payload.main.find(t=>t.name==='Opciones panel');
  const groupSelector=explorer.getRange('C6');
  const originalGroup=groupSelector.values;
  const selector=explorer.getRange('J6');
  const original=selector.values;
  const questionRows=payload.main.find(t=>t.name==='Selector preguntas').rows;
  const representativeQuestions=questionRows.length<=12?questionRows:
    [...new Map([...questionRows.filter((q,i)=>questionRows.findIndex(other=>other[1]===q[1])===i),questionRows.at(-1)].map(q=>[q[0],q])).values()];
  for(const question of representativeQuestions) {
    groupSelector.values=[[question[1]]];
    selector.values=[[question[0]]];
    const optionRows=options.rows.map((r,i)=>[r,i+7]).filter(([r])=>r[0]===question[0]);
    for(const [[row,r],i] of optionRows.map((row,i)=>[row,i])) {
      assert.equal(explorer.getRange(`A${i+31}`).values[0][0],row[1]);
      for(const [dest,source] of [['G','E'],['H','G'],['I','I'],['J','K'],['K','M'],['L','O']]) {
        assert.equal(explorer.getRange(`${dest}${i+31}`).values[0][0],main.worksheets.getItem('Opciones panel').getRange(`${source}${r}`).values[0][0]);
      }
    }
    verifyDashboardLinks(main,payload);
    localChecks++;
  }
  const anotherGroup=questionRows.find(q=>q[1]!==originalGroup[0][0]);
  if(anotherGroup) {
    selector.values=original;
    groupSelector.values=[[anotherGroup[1]]];
    assert.equal(explorer.getRange('A7').values[0][0],'Seleccione un código del grupo elegido');
    assert.equal(explorer.getRange('A31').values[0][0],'');
    localChecks++;
  }
  selector.values=original;
  groupSelector.values=originalGroup;
  const sector=main.worksheets.getItem('Panel sectorial');
  const sectorOriginal=sector.getRange('D6').values;
  for(const value of payload.main.find(t=>t.name==='Panel sectorial').selectors[0].values) {
    sector.getRange('D6').values=[[value]];
    const careerRows=payload.main.find(t=>t.name==='Carreras sector').rows;
    const selected=careerRows.map((r,i)=>[r,i+7]).filter(([r])=>r[0]===value);
    for(const [[row,sourceRow],i] of selected.map((row,i)=>[row,i])) {
      assert.equal(sector.getRange(`A${29+i}`).values[0][0],row[1]);
      for(const [dest,source] of [['E','C'],['G','D'],['I','E'],['K','F']]) {
        assert.equal(sector.getRange(`${dest}${29+i}`).values[0][0],main.worksheets.getItem('Carreras sector').getRange(`${source}${sourceRow}`).values[0][0]);
      }
    }
    verifyDashboardLinks(main,payload);
    localChecks++;
  }
  sector.getRange('D6').values=sectorOriginal;
  progress(`Selectores locales: ${localChecks} cambios verificados`);
  // Sort complete detail rows (including their formulas), not just part of a row.
  const baseTable=payload.main.find(t=>t.name==='Base anual');
  const base=main.worksheets.getItem('Base anual');
  if(baseTable.rows.length && baseTable.rows.length<=500) {
    progress('Verificando orden de filas');
    // Do not replace formulas with cached values: preserve their dependency graph.
    const sourceRange=base.getRange(`A7:Q${baseTable.rows.length+6}`);
    const sourceValues=sourceRange.values;
    sourceRange.values=[...sourceValues].reverse();
    const formulaRange=base.getRange(`R7:W${baseTable.rows.length+6}`);
    const originalFormulas=baseTable.rows.map((_,i)=>['R','S','T','U','V','W'].map(c=>baseTable.formulas[`${c}${i+7}`]));
    formulaRange.formulas=[...originalFormulas].reverse().map((row,i)=>row.map(formula=>
      formula.replace(/(?<![A-Z$])([A-W])\d+\b/g,(_,column)=>`${column}${i+7}`)));
    const filterRange=sheet.getRange(`A7:C${table.rows.length+6}`);
    const filterValues=filterRange.values;
    filterRange.values=[...filterValues].reverse();
    main.recalculate();
    verifyHeadline(main,payload.expected);
    verifyCells(main,payload.expected_cells);
    progress('Restaurando orden original');
    sourceRange.values=sourceValues;
    formulaRange.formulas=originalFormulas;
    filterRange.values=filterValues;
    main.recalculate();
    verifyHeadline(main,payload.expected);
    filterChecks++;
    progress('Orden restaurado y verificado');
  }
}
await validate(main,payload.main,'analisis');
releaseTemporaryMemory();
progress('Exportando libro principal');
await (await SpreadsheetFile.exportXlsx(main)).save(path.join(outputDir,'02_SALIDAS',`Caracterizacion_anual_${payload.year}.xlsx`));
progress('Libro calculado exportado; resta completar y validar literales fuente');
main=null;
releaseTemporaryMemory();
// Keep the exporter diagnostic beside the audit, not among user deliverables.
const inspection=path.join(outputDir,'02_SALIDAS',`Caracterizacion_anual_${payload.year}.xlsx.inspect.ndjson`);
try {
  await fs.rename(inspection,path.join(outputDir,'04_AUDITORIA',path.basename(inspection)));
} catch(error) { if(error.code!=='ENOENT') throw error; }
const audit=build(payload.audit,false);
await validate(audit,payload.audit,'auditoria');
await (await SpreadsheetFile.exportXlsx(audit)).save(path.join(outputDir,'04_AUDITORIA',`Auditoria_caracterizacion_anual_${payload.year}.xlsx`));
await fs.writeFile(path.join(outputDir,'04_AUDITORIA','validacion_excel.json'),JSON.stringify({policy:payload.policy,expected:payload.expected,formulaErrors:0,filterChecks,localSelectorChecks:localChecks,reorderTest:payload.main.find(t=>t.name==='Base anual').rows.length<=500?'ejecutado':'cubierto por fixture; fuente real de solo lectura',engine:'Artifact Tool',nativeExcelTested:false},null,2));
await fs.writeFile(path.join(outputDir,'04_AUDITORIA','recursos_generador.json'),JSON.stringify({
  heapLimitMiB:6144,observedHeapPeakMiB:Math.max(...memoryStages.map(s=>s.heapMiB)),
  processMaxRssKiB:process.resourceUsage().maxRSS,stages:memoryStages,
  sourceLiterals:'escritura incremental posterior; todos conservados en el XLSX final'
},null,2));
console.log(JSON.stringify({excel:'OK',filterChecks,expected:payload.expected}));
