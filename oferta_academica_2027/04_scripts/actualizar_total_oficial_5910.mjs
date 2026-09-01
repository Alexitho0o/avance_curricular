import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';
const p='/Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/06_validaciones/comparativo_oferta_2026_2027/RESUMEN_EJECUTIVO_OFERTA_2026_2027.xlsx';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(p));const s=wb.worksheets.getItem('Resumen ejecutivo');
s.getRange('A8:U8').values=[['Total oficial consolidado 5910', 'n.a.','n.a.','n.a.','n.a.','n.a.','n.a.','n.a.','n.a.','n.a.','n.a.',5461,'n.a.','n.a.','n.a.','n.a.','n.a.','n.a.','n.a.','Valor oficial para comparación anual','Reporte SIES validado; no sumar Etapa 3']];
s.getRange('A8:U8').format.fill='#E2F0D9';s.getRange('A8:U8').format.font.bold=true;s.getRange('L8').format.numberFormat='#,##0';s.getRange('A8:U8').format.borders={style:'continuous',color:'#B7C9D6'};await wb.recalculate();const b=await SpreadsheetFile.exportXlsx(wb);await b.save(p);console.log(p);
