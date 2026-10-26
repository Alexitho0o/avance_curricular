"""Valida cuatro códigos candidatos en el archivo de oferta 2025."""
import hashlib,json
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
p=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/05_OFERTA_ACADEMICA_Y_DURACION/Oferta_Academica_2010_al_2026_SIES_05_06_2026_WEB_E.xlsx')
expected={'I162S2C91J1V1','I162S2C91J2V1','I162S2C57J1V1','I162S2C57J2V1'}
h=hashlib.sha256()
with p.open('rb') as f:
 for b in iter(lambda:f.read(1048576),b''):h.update(b)
w=openpyxl.load_workbook(p,read_only=True,data_only=True);s=w['in'];it=s.iter_rows(values_only=True);headers={v:i for i,v in enumerate(next(it))}; found=[]
for n,row in enumerate(it,2):
 if row[headers['Año']]!='OFE_2025' or row[headers['Código Único']] not in expected:continue
 found.append({'fila':n,'codigo':row[headers['Código Único']],'vigencia':row[headers['Vigencia']],'nombre':row[headers['Nombre Carrera']],'jornada':row[headers['Jornada']],'tipo_plan':row[headers['Plan Especial']]})
w.close();assert len(found)==4 and {r['codigo'] for r in found}==expected and all(r['vigencia']=='Vigente con estudiantes nuevos' for r in found)
out={'clasificacion':'B dato observado; C verificacion','ruta':str(p),'sha256':h.hexdigest(),'hoja':'in','anio_fuente':'OFE_2025','registros':found,'limite':'La oferta acredita disponibilidad del código, no su atribución individual al expediente ni al trimestre.'};(OUT/'QA_OFERTA_TRECE_2025.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
