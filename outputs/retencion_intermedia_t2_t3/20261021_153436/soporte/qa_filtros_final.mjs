import fs from "node:fs/promises"; import {FileBlob,SpreadsheetFile}from "@oai/artifact-tool";
const O="/Users/alexi/Documents/GitHub/avance_curricular/outputs/retencion_intermedia_t2_t3/20261021_153436",P="/Users/alexi/Documents/GitHub/avance_curricular/.local_restricted/retencion_intermedia/20261021_153436";const c=JSON.parse(await fs.readFile(O+"/soporte/config.json","utf8"));const w=await SpreadsheetFile.importXlsx(await FileBlob.load(P+"/public_candidate.xlsx"));const s=w.worksheets.getItem("14_Vistas_Ejecutivas");s.getRange("H4").values=[["Todos"]];s.getRange("S4").values=[["Todas"]];
const modes={'T1 anual MU':'T1','T2 observado':'T2_records_observed','T3 observado':'T3_records_observed','Último respaldo':'latest_snapshot_2026_VIGENTE'};
const controls=[];
for(const [mode,key]of Object.entries(modes))for(const co of ['Cohorte 2024','Cohorte 2025','Cohortes 2024 y 2025']){
 s.getRange('L4').values=[[mode]];s.getRange('C4').values=[[co]];w.recalculate();
 const years=co==='Cohortes 2024 y 2025'?['2024','2025']:[co.slice(-4)];
 const n=years.reduce((a,y)=>a+c.control[y].denominator,0),k=years.reduce((a,y)=>a+c.control[y][key],0);
 const v=s.getRange('C7:E7').values[0];if(v[0]!==n||v[1]!==k||Math.abs(v[2]-k/n)>1e-12)throw Error('Main summary controls: '+JSON.stringify({mode,co,expected:[n,k],actual:v}));
 controls.push({mode,cohort:co,denominator:n,numerator:k,rate:k/n,status:'PASS'});
}
// Complete connected-filter QA across every governed sector and career for all four modes.
const groups=JSON.parse(await fs.readFile(`${O}/MODELO_AGREGADO.json`,'utf8')).groups;
for(const [mode,key]of Object.entries(modes))for(const sec of ['Todos','Tecnologías','Administración y Comercio','Salud']){
 s.getRange('L4').values=[[mode]];s.getRange('C4').values=[['Cohortes 2024 y 2025']];s.getRange('H4').values=[[sec]];s.getRange('S4').values=[['Todas']];w.recalculate();
 const ix={'T1':14,'T2_records_observed':15,'T3_records_observed':16,'latest_snapshot_2026_VIGENTE':24}[key];
 const rows=groups.filter(r=>sec==='Todos'||r[4]===sec),n=rows.reduce((a,r)=>a+r[13],0),k=rows.reduce((a,r)=>a+r[ix],0);const val=s.getRange('C7:E7').values[0];
 if(val[0]!==n||val[1]!==k)throw Error('Sector selection mismatch '+JSON.stringify({sec,mode,n,k,val}));
 const sectorSum=s.getRange('H7:I9').values.reduce((a,r)=>[a[0]+(typeof r[0]==='number'?r[0]:0),a[1]+(typeof r[1]==='number'?r[1]:0)],[0,0]);
 if(sectorSum[0]!==n||sectorSum[1]!==k)throw Error('Level 2 disagrees');
 const careerSum=s.getRange('T7:U23').values.reduce((a,r)=>[a[0]+(typeof r[0]==='number'?r[0]:0),a[1]+(typeof r[1]==='number'?r[1]:0)],[0,0]);if(careerSum[0]!==n||careerSum[1]!==k)throw Error('Career view disagrees');
 controls.push({mode,sector:sec,denominator:n,numerator:k,connected:'PASS'});
 for(const career of [...new Set(rows.map(r=>r[2]))]){
  s.getRange('S4').values=[[career]];w.recalculate();const rr=rows.filter(r=>r[2]===career),nn=rr.reduce((a,r)=>a+r[13],0),kk=rr.reduce((a,r)=>a+r[ix],0),vv=s.getRange('C7:E7').values[0];if(vv[0]!==nn||vv[1]!==kk)throw Error('Career selection mismatch');
  controls.push({mode,sector:sec,career,denominator:nn,numerator:kk,connected:'PASS'});
 }
}
s.getRange('C4').values=[['Cohortes 2024 y 2025']];s.getRange('H4').values=[['Todos']];s.getRange('S4').values=[['Todas']];s.getRange('L4').values=[['Último respaldo']];w.recalculate();

await fs.writeFile(O+"/QA_FILTROS_FINAL.json",JSON.stringify({status:"OK",engine:"Artifact Tool local",controls},null,2)+"\n");console.log("Final controls passed: ",controls.length);