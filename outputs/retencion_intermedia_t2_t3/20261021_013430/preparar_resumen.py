"""Reutiliza resultados verificados sin recalcular ni cambiar los universos."""
from pathlib import Path
import hashlib, json
import openpyxl

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BASE=ROOT/'outputs/retencion_intermedia_t2_t3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rev=json.loads((BASE/'20261020_215248/MANIFEST_REVISION.json').read_text())
cont=json.loads((BASE/'20261020_221157/MANIFEST_CONTINUIDAD.json').read_text())
for m in (rev,cont):
    assert sha(m['salida']['path'])==m['salida']['sha256']
    for src in m['fuentes']:
        assert sha(src['path'])==src['sha256'],src['path']
p=Path(rev['salida']['path']); w=openpyxl.load_workbook(p,read_only=True,data_only=True)
career=[]
for r in w['Por_carrera'].iter_rows(min_row=7,max_row=34,values_only=True):
    assert len(r)==12
    career.append(list(r[:9]))
for year,expected in [(2024,[636,558,0,1,1,325,317]),(2025,[1255,1150,20,2,None,0,0])]:
    rows=[r for r in career if r[0]==year]
    for col,exp in enumerate(expected,2):
        if exp is not None: assert sum(r[col] for r in rows)==exp,(year,col)
w.close()
payload={'career':career,'review':rev,'continuity':cont,'source_workbook':{'path':str(p),'sha256':sha(p)},
         'classification':'B fuentes; C conteos y fórmulas; D alcance parcial y denominadores conservados; E tasas intermedias pendientes',
         'scope':'Agregados exclusivamente. No identificadores, seudónimos ni filas individuales.',
         'source_map':{'sheet':'Por_carrera','range':'A7:I34','meaning':'Insumos agregados desde fórmulas verificadas del libro de revisión; no recálculo del motor anual.'}}
(OUT/'insumos_agregados.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2))
print(json.dumps({'carreras_cohorte':len(career),'fuentes_hash':'OK','controles':'OK'}))
