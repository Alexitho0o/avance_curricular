import json,collections,pandas as pd,re,sys
from pathlib import Path
r=Path('/Users/alexi/Documents/GitHub/avance_curricular');sys.path.insert(0,str(r));from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento
props=json.load(open('/Users/alexi/.local/share/ipss/revision_42_20261027/REVISION_42.json'))['propuestas'];sv=DiccionarioSiesSeguimiento();rem=[]
for p in props:
 x=p['contexto'];v=sv.consultar(persona=x['persona'],codcli=x['CODCLI'],plan=x['plan'],anio=x['ano'],periodo=x['periodo_UMAS'],carrera=x['carrera']);
 if not v.get('codigo_sies'):rem.append(p)
base=Path('/Users/alexi/Library/CloudStorage');frames=[]
for path in base.glob('OneDrive*/IPSS_CONCILIACION_UMAS_SIES_BASES/03_UMAS_DATOSDEALUMNOS/DATOSDEALUMNOS_*.xlsx'):
 if path.name in ['DATOSDEALUMNOS_11248.xlsx','DATOSDEALUMNOS_12159.xlsx']:
  f=pd.read_excel(path,usecols=['RUT','CODCLI','CODCARPR','JORNADA','SEDE','ESTADOACADEMICO','SITUACION','ANOMATRICULA','PERIODOMATRICULA'],dtype=str,keep_default_na=False);f['_FUENTE']=path.name;frames.append(f)
df=pd.concat(frames,ignore_index=True)
def norm(x):return re.sub('[^0-9K]','',str(x).upper())
summary=collections.Counter()
for p in rem:
 x=p['contexto'];f=df[df['RUT'].map(norm)==norm(x['persona'])];own=f[f['CODCLI'].str.upper().str.strip()==x['CODCLI']];others=f[f['CODCLI'].str.upper().str.strip()!=x['CODCLI']];summary['propio_codcli_en_datosalumnos']+=not own.empty;summary['otro_codcli_en_datosalumnos']+=not others.empty;summary['TPAS_con_otro_TPAREOL']+=x['carrera']=='TPAS' and any(others['CODCARPR'].str.upper().str.strip()=='TPAREOL')
print(json.dumps(summary));sv.close()
