"""Contrasta el respaldo T3 original y verifica integridad del diagnóstico derivado."""
from pathlib import Path
import sys,json,collections
import openpyxl
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import sha256
O=Path(sys.argv[1]);m=json.loads((O/'MANIFEST.json').read_text());P=Path(m['privado'])
for k,h in m['salidas_sha256'].items():assert sha256(O/k)==h,k
for k,h in m['privados_hashes'].items():assert sha256(P/k)==h,k
ctxpath=Path('/Users/alexi/.local/share/ipss/cierre_14_jornadas_15_20261023_133759/JORNADAS_15_CONTEXTO_COMPLETO.json');ctx=json.loads(ctxpath.read_text())
rs=[r for r in ctx if r.get('caso') in ['INF35-03','INF35-04'] and 'PRUEBA CUMPLIMIENTO' in r['fuente'] and r['hoja']=='DATOS CRUDOS U+ 19-11-2024'];assert len(rs)==6
path=Path(rs[0]['fuente']);h=sha256(path);assert all(r['sha256']==h for r in rs)
w=openpyxl.load_workbook(path,read_only=True,data_only=True);it=iter(w[rs[0]['hoja']].values);headers=[str(x).upper() for x in next(it)];wanted={r['fila']:r for r in rs};done=0
v=lambda x:'' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
for n,row in enumerate(it,2):
 if n>max(wanted):break
 if n not in wanted:continue
 actual=dict(zip(headers,row));r=wanted[n]
 for k in ['CODCLI','RUT','CODIGO_PLAN_ESTUDIO','ANO','PERIODO','CODIGO_ASIGNATURA','SECCION','FECHAINICIO','FECHAFIN','FECHA MEDICION']:assert v(actual[k])==v(r[k]),k
 done+=1
w.close();assert done==6
out={'clasificacion':'B/C contraste del respaldo T3 primario','filas_releidas':6,'referencias':[{k:r[k] for k in ['caso','fuente','hoja','fila','sha256','CODIGO_PLAN_ESTUDIO','ANO','PERIODO','CODIGO_ASIGNATURA','SECCION','FECHAINICIO','FECHAFIN','FECHA MEDICION']} for r in rs]}
(O/'QA_RESPALDO_T3.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
m['fuentes_sha256'][str(path)]=h;m['codigo_sha256'][str(Path(__file__).relative_to(R))]=sha256(__file__);m['salidas_sha256']['QA_RESPALDO_T3.json']=sha256(O/'QA_RESPALDO_T3.json');m['QA']['respaldo_T3_primario_releido']=6
for p,h in m['fuentes_sha256'].items():assert sha256(p)==h,p
for p,h in m['codigo_sha256'].items():assert sha256(R/p)==h,p
(O/'MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'estado':'OK','manifest_sha256':sha256(O/'MANIFEST.json'),'respaldo_T3':6,'fuentes_verificadas':len(m['fuentes_sha256'])}))
