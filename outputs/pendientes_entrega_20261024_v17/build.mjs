import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const w=Workbook.create(),s=w.worksheets.add('55_Pendientes_entrega');
s.showGridLines=false;s.tabColor='#123047';
s.getRange('A1:D18').format.font.name='Calibri';
s.getRange('A1:D18').format.font.size=11;
s.getRange('A1:D18').format.wrapText=true;
s.getRange('A1:D18').format.verticalAlignment='center';
for(const [c,width] of [['A',25],['B',49],['C',54],['D',25]])s.getRange(`${c}1:${c}18`).format.columnWidth=width;
s.mergeCells('A1:D1');s.getRange('A1').values=[['Retención intertrimestral · aclaraciones para la entrega']];
s.getRange('A1:D1').format.fill='#123047';s.getRange('A1:D1').format.font.color='#FFFFFF';s.getRange('A1:D1').format.font.size=16;s.getRange('A1:D1').format.rowHeight=34;
s.mergeCells('A2:D2');s.getRange('A2').values=[['Versión 17 · 24 de octubre de 2026. Análisis interno con pendientes explícitos. Las bases, fórmulas y denominadores anteriores se conservan.']];s.getRange('A2:D2').format.rowHeight=36;
s.getRange('A4:D4').values=[['Tema / respaldo','Qué sabemos','Qué falta o cómo leerlo','Dónde revisar']];
s.getRange('A4:D4').format.fill='#164875';s.getRange('A4:D4').format.font.color='#FFFFFF';s.getRange('A4:D4').format.font.bold=true;s.getRange('A4:D4').format.rowHeight=28;
const rows=[
['66 renuncias T2-2026\nB / C / E','El resumen recibido resta 66 a 528 matrículas: 462/528 = 87,50 %. Hay 527 personas.','Pendiente: nómina o consulta con CODCLI, criterio y fecha que originó las 66. El 87,50 % mide matrículas; no es una tasa de personas validada.','Hojas 18 y 23\n18!B97'],
['Correo de origen\nB / E','María Paz Sandoval, 20-oct-2026, 20:18. Asunto: Análisis para Comité de Rectoría / JD. Incluye los cuatro archivos T2/T3.','El correo describe bases vigentes al cierre, pero no explica las 66 renuncias ni adjunta una nómina adicional específica.','Outlook\nCorreo del 20-oct-2026'],
['Contraste por CODCLI\nB / C / E','En el respaldo 12159: 462 VIGENTE, 63 ELIMINADO, 1 SUSPENDIDO y 2 CODCLI no localizados.','63 + 1 + 2 = 66 no demuestra que sean las mismas renuncias. Difieren 14 carreras. No clasificar ausentes o suspendidos como renuncias.','Conciliación de las 14 carreras\n24-oct-2026'],
['Actividad y matrícula\nC / D','PROMEDIOS sigue actividad del período y estado VIGENTE. La foto de matrícula mide otra evidencia.','No comparar ambas tasas como si fueran el mismo indicador. Para el auxiliar interno aprobado no se exige acreditar la fecha exacta histórica del estado.','Hojas 18 y 26'],
['Fotografías faltantes\nE','Se conservan las celdas «Sin foto completa» y «Sin foto».','Falta la evidencia de matrícula del grupo y cierre indicado. La actividad académica no convierte esas celdas en una foto de matrícula.','Hoja 18'],
['Tasa anual de tres períodos\nE','El libro mantiene pendiente el seguimiento anual comparable de T1, T2 y T3.','Se requiere la misma medida un año después para cada grupo. No completar con el promedio simple de porcentajes.','18!B84'],
['Excepciones SIES\nB / E','El libro registra 104 contextos pendientes; 24 pertenecen al foco multiversión. Hay 13 correspondencias internas aprobadas.','Falta resolver las excepciones y la atribución documental de esas correspondencias. No excluir estudiantes del seguimiento interno por código pendiente.','Hojas 52 y 54'],
['Titulados en tasas 2026\nB / C / D','Las tasas T3 conservan cuatro exclusiones internas documentadas: 1.360/1.467 y 2.290/2.519.','Es una decisión interna conservada, no una regla oficial SIES nueva. No cambiar denominadores para comparar porcentajes.','Hoja 21\n18!B91:I97'],
['Cómo comparar tasas\nC','La tasa conjunta es suma de retenidos dividida por suma de estudiantes de los grupos comparables.','El promedio simple de tasas da el mismo peso a grupos de distinto tamaño. Compare población, período, unidad y fuente antes de comparar resultados.','Hojas de análisis y resumen'],
['Alcance del control\nB / C / E','El QA de V16 registró apertura sin reparación y comprobó las tres tasas 2026 revisadas.','Esta entrega añade solo esta hoja. No convierte los pendientes en resueltos ni certifica nuevamente todos los cruces históricos.','Registro de entrega V17']
];
s.getRange('A5:D14').values=rows;s.getRange('A5:D14').format.rowHeight=78;
for(let r=5;r<=14;r++)if(r%2===1)s.getRange(`A${r}:D${r}`).format.fill='#EEF2F5';
s.mergeCells('A16:D16');s.getRange('A16').values=[['Respaldo: A = regla oficial; B = dato observado; C = cálculo o implementación; D = decisión interna; E = pendiente. Los antecedentes del correo son B, no una regla oficial A.']];s.getRange('A16:D16').format.rowHeight=35;
s.mergeCells('A18:D18');s.getRange('A18').values=[['Fuente del registro: CIERRE_REVISION_CORREO_RENUNCIAS_T2_20261024.md; conciliación de 14 carreras; documentación y QA de V15/V16. No se añadieron identificadores individuales a esta hoja.']];s.getRange('A18:D18').format.rowHeight=35;
w.recalculate();
await (await SpreadsheetFile.exportXlsx(w)).save('/tmp/retencion_v17/hoja.xlsx');
const img=await w.render({sheetName:s.name,range:'A1:D18',scale:1.5});await fs.writeFile('/tmp/retencion_v17/preview.png',new Uint8Array(await img.arrayBuffer()));
console.log('Hoja de aclaraciones creada y renderizada.');
