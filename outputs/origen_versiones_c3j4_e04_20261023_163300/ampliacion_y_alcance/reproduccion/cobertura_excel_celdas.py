from pathlib import Path
import json,openpyxl
R=Path('/Users/alexi/Documents/GitHub/avance_curricular');m=json.loads((R/'outputs/aplicacion_diccionario_intertrimestral_20261023_125556/MANIFEST_APLICACION.json').read_text());paths={'original':next(p for p in m['fuentes'] if p.endswith('AUDITADO_ENTREGA.xlsx')),'v11':m['origen_excel'],'v12':m['salida']};out={}
for label,path in paths.items():
 f=openpyxl.load_workbook(path,read_only=True,data_only=False);v=openpyxl.load_workbook(path,read_only=True,data_only=True);z={}
 tab='18_Foto_Intertrimestral';z[tab]={c:{'formula_o_literal':f[tab][c].value,'cache':v[tab][c].value} for c in ['D7','D8','D11','G11','H11','D12','E12','F12','D14','G14','H14']}
 tab='20_Foto_BBDD';z[tab]={'filas':f[tab].max_row,'columnas':f[tab].max_column,'encabezados':[[str(x) for x in row] for row in v[tab].iter_rows(min_row=4,max_row=5,values_only=True)]};out[label]=z;f.close();v.close()
print(json.dumps(out,ensure_ascii=False,indent=2));Path('/tmp/cobertura_excel_celdas_20261023.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
