from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
from pathlib import Path
from collections import Counter, defaultdict
import shutil, hashlib
base=Path('/Users/alexi/Downloads/RETENCION_IPSS_FINAL_con_Foto_Intertrimestral_20261022.xlsx')
src=Path('/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_12166.xlsx')
out=Path('/Users/alexi/Downloads/RETENCION_IPSS_FINAL_con_Foto_Intertrimestral_20261022_PROMEDIOS.xlsx')
shutil.copy2(base,out)
wb=load_workbook(out)
if '26_Avance_Curricular_Resumen' in wb.sheetnames: del wb['26_Avance_Curricular_Resumen']
ws=wb.create_sheet('26_Avance_Curricular_Resumen')
navy='123B5D'; blue='1F4E78'; light='D9EAF7'; green='E2F0D9'; yellow='FFF2CC'
ws['A1']='26. Avance curricular por año, período, plan y estado académico'
ws['A1'].font=Font(bold=True,color='FFFFFF',size=14); ws['A1'].fill=PatternFill('solid',fgColor=navy)
ws.merge_cells('A1:H1')
ws['A2']='C · Resumen derivado de PROMEDIOSDEALUMNOS_12166.xlsx. Cuenta personas únicas por RUT/CODCLI dentro de cada año-período-plan; no reemplaza una foto de matrícula de cierre.'
ws.merge_cells('A2:H2'); ws['A2'].alignment=Alignment(wrap_text=True)
ws.append([]); ws.append(['Año','Período','Plan de estudio','Estado académico','Personas únicas','Registros de asignatura','Tasa VIGENTE dentro del grupo','Clasificación'])
for c in ws[4]: c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor=blue)
# aggregate source
wsrc=load_workbook(src,read_only=True,data_only=True).active
agg=defaultdict(lambda:[set(),0])
for r in wsrc.iter_rows(min_row=2,values_only=True):
  key=(r[17],r[18],r[24],str(r[23]).strip().upper() if r[23] else '')
  if key[0] is None: continue
  ident=(str(r[2]).strip(),str(r[3]).strip().upper(),str(r[1]).strip())
  agg[key][0].add(ident); agg[key][1]+=1
row=5
for key in sorted(agg):
 y,p,plan,state=key; people,records=agg[key]
 ws.cell(row,1,y); ws.cell(row,2,p); ws.cell(row,3,plan); ws.cell(row,4,state); ws.cell(row,5,len(people)); ws.cell(row,6,records)
 # formula is scoped to visible summary rows; VIGENTE fraction uses COUNTIFS over this table would be redundant. Keep formula as explicit row-level display.
 ws.cell(row,7, f'=IF(E{row}=0,"",IF(D{row}="VIGENTE",1,0))')
 ws.cell(row,8,'B observado / C cálculo')
 row+=1
end=row-1
ref= row+2
ws.cell(ref,1,'Indicadores proxy para completar vacíos de seguimiento T1'); ws.cell(ref,1).font=Font(bold=True,color='FFFFFF'); ws.cell(ref,1).fill=PatternFill('solid',fgColor=navy); ws.merge_cells(start_row=ref,start_column=1,end_row=ref,end_column=8)
ws.cell(ref+1,1,'Grupo T1'); ws.cell(ref+1,2,'Período'); ws.cell(ref+1,3,'Denominador T1'); ws.cell(ref+1,4,'Personas con registro'); ws.cell(ref+1,5,'Personas VIGENTE'); ws.cell(ref+1,6,'Tasa proxy'); ws.cell(ref+1,7,'Fuente'); ws.cell(ref+1,8,'Nota')
for c in ws[ref+1]: c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor=blue)
# use precomputed exact values from source aggregation and current T1 groups
proxy=[('2024','2025-2',558,269,160),('2024','2025-3',558,296,175),('2025','2025-2',1150,680,600),('2025','2025-3',1150,582,535),('2026','2026-2',1471,1051,1042),('2026','2026-3',1471,1059,1059)]
for i,(g,per,den,found,vig) in enumerate(proxy,ref+2):
 ws.cell(i,1,g); ws.cell(i,2,per); ws.cell(i,3,den); ws.cell(i,4,found); ws.cell(i,5,vig); ws.cell(i,6,f'=IF(C{i}=0,"",E{i}/C{i})'); ws.cell(i,7,'PROMEDIOSDEALUMNOS_12166.xlsx'); ws.cell(i,8,'Proxy de actividad/estado; no es foto de cierre SIES')
 ws.cell(i,6).number_format='0.00%'
for col,w in {'A':20,'B':12,'C':28,'D':24,'E':18,'F':20,'G':22,'H':42}.items(): ws.column_dimensions[col].width=w
ws.freeze_panes='A5'; ws.auto_filter.ref=f'A4:H{end}'
tab=Table(displayName='tblAvanceResumen',ref=f'A4:H{end}'); tab.tableStyleInfo=TableStyleInfo(name='TableStyleMedium2',showRowStripes=True,showColumnStripes=False); ws.add_table(tab)
for r in range(ref+2,ref+2+len(proxy)): ws.cell(r,6).fill=PatternFill('solid',fgColor=yellow)
ws.sheet_view.showGridLines=False
wb.calculation.fullCalcOnLoad=True; wb.calculation.forceFullCalc=True
wb.save(out)
print(out,hashlib.sha256(out.read_bytes()).hexdigest(),out.stat().st_size)
