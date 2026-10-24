// Dashboard layout is separate from source-table formatting and calculation policy.
export const rateFormat = '[=0]0%;[=1]0%;0.0%';
const palette = {ink:'#193342', title:'#125B69', pale:'#EFF4F6', input:'#FFF2CF',
  line:'#DCE5EA', blue:'#247BA0', green:'#008577', muted:'#5A6E7B'};
const formats = {percent:rateFormat, decimal:'0.0', integer:'#,##0'};

export function prepareDashboard(book, table, payload) {
  const sheet=book.worksheets.getItem(table.name);
  sheet.showGridLines=false;
  sheet.tabColor=palette.title;
  const area=sheet.getRange(`A1:L${table.last_row}`);
  area.format={font:{name:'Arial',size:11,color:palette.ink},fill:'#FFFFFF',
    columnWidth:13,rowHeight:25,horizontalAlignment:'center',verticalAlignment:'center',wrapText:true};
  area.setNumberFormat('#,##0');
  function merged(address,value,formula=false) {
    const range=sheet.getRange(address);
    range.merge();
    if(formula) sheet.getRange(address.split(':')[0]).formulas=[[value]];
    else sheet.getRange(address.split(':')[0]).values=[[value]];
  }
  merged('A1:J1',`${table.title} · ${payload.year}`);
  // Native internal links are added to the exported OOXML. The engine does not
  // calculate HYPERLINK and otherwise exports its diagnostic as the visible label.
  merged('K1:L1','Filtros');
  sheet.getRange('A1:L1').format={fill:palette.title,font:{name:'Arial',size:18,bold:true,color:'#FFFFFF'},rowHeight:42};
  const controls=payload.main.find(t=>t.name==='Filtros');
  const n=controls.rows.length+6;
  const dims=['Período','Sector','Modalidad','Sede','Carrera','Jornada'];
  const positions=['A2:D2','E2:H2','I2:L2','A3:D3','E3:H3','I3:L3'];
  dims.forEach((dim,i)=>{
    const total=`COUNTIF('Filtros'!$A$7:$A$${n},"${dim}")`;
    const selected=`COUNTIFS('Filtros'!$A$7:$A$${n},"${dim}",'Filtros'!$C$7:$C$${n},"Sí")`;
    const values=controls.rows.filter(row=>row[0]===dim);
    const labels=values.map(row=>{
      const text=String(row[1]).replaceAll('"','""');
      return `IF(COUNTIFS('Filtros'!$A$7:$A$${n},"${dim}",'Filtros'!$B$7:$B$${n},"${text}",'Filtros'!$C$7:$C$${n},"Sí")=1,"${text} ","")`;
    }).join('&') || '""';
    let expression=`IF(${selected}=0,"Ninguno",IF(${selected}=${total},"Todos",${values.length<=8?labels:`${selected}&" de "&${total}`}))`;
    if(i===0) expression=`IF(${selected}=0,"Ninguno",${labels})`;
    merged(positions[i],`="${dim}: "&${expression}`,true);
  });
  sheet.getRange('A2:L3').format={fill:palette.pale,font:{size:10,color:palette.muted},rowHeight:32};
  const names=payload.main.filter(t=>t.dashboard).map(t=>t.name);
  const short=['Resumen','Cobertura','Preguntas','Financiamiento','Rendimiento','Sectores'];
  names.forEach((name,i)=>{
    const c=String.fromCharCode(65+i*2),end=String.fromCharCode(66+i*2);
    merged(`${c}4:${end}4`,short[i]);
    sheet.getRange(`${c}4:${end}4`).format={fill:name===table.name?'#D9EDEB':'#FFFFFF',font:{size:10,bold:true,color:palette.title},rowHeight:26};
  });
  for(const address of table.merges) sheet.getRange(address).merge();
  for(const [address,value] of Object.entries(table.cells)) sheet.getRange(address).values=[[value]];
  for(const [address,role] of table.styles) {
    const range=sheet.getRange(address);
    if(formats[role]) {range.setNumberFormat(formats[role]);continue;}
    if(role==='kpi_label') range.format={font:{size:11,bold:true,color:palette.muted},rowHeight:27};
    if(role==='kpi') range.format={font:{size:25,bold:true,color:palette.title}};
    if(role==='section') range.format={fill:palette.pale,font:{size:12,bold:true},rowHeight:30};
    if(role==='header') range.format={fill:palette.title,font:{size:11,bold:true,color:'#FFFFFF'},rowHeight:46};
    if(role==='stripe') range.format={fill:'#F0F5F7',rowHeight:44};
    if(role==='body') range.format={rowHeight:44};
    if(role==='question') range.format={font:{size:12,bold:true},rowHeight:26};
    if(role==='note') range.format={font:{size:10,color:palette.muted},rowHeight:24};
    if(role==='input') range.format={fill:palette.input,font:{size:12,bold:true},borders:{preset:'outside',style:'thin',color:'#D69B23'}};
  }
  for(const control of table.selectors) sheet.getRange(control.cell).dataValidation={rule:{type:'list',
    ...(control.source?{formula1:control.source}:{values:control.values})}};
  for(const range of table.heatmaps) sheet.getRange(range).conditionalFormats.add('colorScale',{
    colors:['#F0F5F7','#ACE0E4','#24879A'],thresholds:[{type:'num',value:0},{type:'num',value:.5},{type:'num',value:1}]});
  // A persistent methodological note lives after, not on top of, the analytical content.
  const noteRow=table.last_row+3;
  merged(`A${noteRow}:L${noteRow+1}`,table.note);
  sheet.getRange(`A${noteRow}:L${noteRow+1}`).format={font:{size:10,color:palette.muted},wrapText:true,
    horizontalAlignment:'center',verticalAlignment:'center',rowHeight:24};
  table.render_note_row=noteRow;
}

export function bindDashboardCharts(book,table) {
  const sheet=book.worksheets.getItem(table.name);
  const address=r=>`'${table.name.replaceAll("'","''")}'!`+r.split(':').map(c=>c.replace(/^([A-Z]+)(\d+)$/,'$$$1$$$2')).join(':');
  for(const item of table.charts) {
    const chart=sheet.charts.add('bar');
    chart.title=item.title;
    chart.titleTextStyle.fontSize=12;
    chart.titleTextStyle.typeface='Arial';
    chart.barOptions.direction='bar';
    chart.barOptions.grouping=item.stacked?'stacked':'clustered';
    chart.barOptions.gapWidth=65;
    if(item.stacked) chart.barOptions.overlap=100;
    chart.hasLegend=item.series.length>1;
    chart.legend={position:'bottom'};
    chart.dataLabels={showValue:item.format==='integer',position:'outEnd',textStyle:{fontSize:10}};
    chart.setPosition(item.start,item.end);
    chart.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:10}};
    chart.yAxis={numberFormatCode:formats[item.format],numberFormatSourceLinked:false,
      textStyle:{typeface:'Arial',fontSize:10},min:0,
      ...(item.format==='integer'?{deleted:true,majorGridlines:{fill:'#FFFFFF'}}:{}),
      ...(item.format==='percent'?{max:1}:item.format==='decimal'?{max:7}:{})};
    for(const [name,range,color] of item.series) {
      const series=chart.series.add(name);
      series.categoryFormula=address(item.labels);
      series.formula=address(range);
      series.fill=color;
    }
  }
}

export function verifyDashboardLinks(book, payload) {
  const get=(name,address)=>book.worksheets.getItem(name).getRange(address).values[0][0];
  for(const [panelCell,source] of [['A7','B8'],['D7','B9'],['G7','B12'],['J7','B11']]) {
    if(get('Panel ejecutivo',panelCell)!==get('Resumen',source)) throw new Error(`Panel ejecutivo desactualizado: ${panelCell}`);
  }
  for(const table of payload.main.filter(t=>t.dashboard)) {
    const sheet=book.worksheets.getItem(table.name);
    for(const [address,formula] of Object.entries(table.formulas)) {
      const value=sheet.getRange(address).values[0][0];
      if(typeof value==='string' && /^#(REF!|DIV\/0!|VALUE!|NAME\?|N\/A|NUM!|NULL!|SPILL!|CALC!)/.test(value)) {
        throw new Error(`${table.name}!${address}: ${value} (${formula})`);
      }
    }
  }
}
