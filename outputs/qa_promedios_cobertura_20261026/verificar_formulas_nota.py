"""Cuenta fórmulas en NOTA_FINAL en 2026-P2/P3, sin leer identificadores."""
import json,openpyxl
from pathlib import Path
OUT=Path(__file__).parent
prior=json.loads((OUT/'DIFERENCIAS_ASIGNATURA_AGREGADO.json').read_text()); result={}
for name,source in prior['fuentes'].items():
 w=openpyxl.load_workbook(source['ruta'],read_only=True,data_only=False);it=w['Hoja1'].iter_rows();h={str(c.value).strip().upper():i for i,c in enumerate(next(it)) if c.value is not None};count={'2':0,'3':0}
 for row in it:
  per=str(row[h['PERIODO']].value)
  if str(row[h['ANO']].value)=='2026' and per in count and row[h['NOTA_FINAL']].data_type=='f':count[per]+=1
 w.close();result[name]=count
out={'clasificacion':'B dato observado; C conteo','formula_nota_final_por_periodo':result,'limite':'No define el significado de cero o vacío ni la fecha efectiva de datos.'};(OUT/'QA_FORMULAS_NOTA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
