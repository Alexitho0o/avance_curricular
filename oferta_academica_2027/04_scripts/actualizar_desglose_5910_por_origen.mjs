import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';
const p='/Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/06_validaciones/comparativo_oferta_2026_2027/RESUMEN_EJECUTIVO_OFERTA_2026_2027.xlsx';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(p));const s=wb.worksheets.getItem('Resumen ejecutivo');
s.getRange('L5:O6').values=[[3477,952,2154074,2119903],[1984,1732,2005000,'n.a.']];
s.getRange('L5:M6').format.numberFormat='#,##0';s.getRange('A8:U8').values=[['Total oficial consolidado 5910','n.a.','n.a.','n.a.','n.a.','n.a.','n.a.','n.a.','n.a.','n.a.','n.a.',5461,'n.a.','n.a.','n.a.','n.a.','n.a.','n.a.','n.a.','Desglose ratificado por origen: Etapa 1 3.477 + Etapa 2 1.984','Reporte SIES 5910; no sumar Etapa 3']];s.getRange('L8').format.numberFormat='#,##0';await wb.recalculate();const b=await SpreadsheetFile.exportXlsx(wb);await b.save(p);console.log(p);
