import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,'../..');
const dir=path.join(root,'06_validaciones/maqueta_etapa2_noviembre_20261023_v03');
const data=JSON.parse(await fs.readFile(path.join(dir,'INSUMOS.json'),'utf8'));
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(data.snapshot));
for(const x of data.referencias_resueltas)w.worksheets.getItem(x.hoja).getRange(x.celda).values=[[x.valor]];
const s=w.worksheets.getItem('Pendientes por campo');
s.getRange('A7').values=[['Manual octubre 2026, pp.35-41; paginas por campo en F. Datos fuente resguardados en V02; los enlaces llevan a la hoja de diplomados.']];
for(const [addr,text] of Object.entries({
  E41:'Dato obligatorio numerico. 15 por semestre segun maqueta del usuario e instruccion 15+15. Son 30 anuales por programa; revisar oferta efectiva.',
  E42:'Dato obligatorio numerico. 15 en segundo semestre, segun criterio del usuario. No dividir la cifra entre semestres; suma anual >0 para vigencia 1.',
  E53:'0 informado por Docencia, conservado desde la maqueta V02. Dato disponible, no vacio ni imputacion.',
  E54:'0 informado por Docencia, conservado desde la maqueta V02. Dato disponible, no vacio ni imputacion.',
  E55:'Monto conservado desde la maqueta V02. La fuente lo etiquetaba Matricula, pero el usuario confirmo que corresponde a arancel. Revisar antes de devolver.'
}))s.getRange(addr).values=[[text]];
w.recalculate();
if(s.getRange('A4').values[0][0]!=='Celdas obligatorias vacias: 418. Campos que deben quedar vacios: 9.')throw Error('Faltantes alterados');
await(await SpreadsheetFile.exportXlsx(w)).save(path.join(dir,'INTERMEDIO_TRES_HOJAS.xlsx'));
console.log('Valores conservados; referencias a Programas resueltas.');
