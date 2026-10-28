"""Nueva edición aditiva de tres familias CO; no modifica el diccionario personal."""
import hashlib,json
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'data/versiones_por_cohorte/20261016/grupos_existentes.json'
NEW=ROOT/'data/versiones_por_cohorte/20261028'
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(OLD)=='80ce832f8d230551cac18b043e6715023f34ec42fb007313f1b17051c98463aa'
cat=json.loads((ROOT/'data/catalogo_fuentes/CATALOGO_FUENTES.json').read_text())
offer=next(x for x in cat['catalogo'] if x['sha256']=='94d51a6752b40adb45c8eba65786ee8aad9f6667d15b3d07273a969ec4faed77')
p=Path(offer['ruta_consolidada']);assert sha(p)==offer['sha256']
old=json.loads(OLD.read_text()); new=list(old)
targets={'I162S3C114J2':('COTEIQ','TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA'),'I162S3C115J2':('COTFAR','TECNICO EN FARMACIA'),'I162S3C91J2':('COTENS','TECNICO EN ENFERMERIA')}
w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=w['in'].iter_rows(values_only=True);heads=next(it);evidence={}
for i,r in enumerate(it,2):
    d=dict(zip(heads,r));code=str(d.get('Código Único','')).strip();family=code.rsplit('V',1)[0]
    if family in targets and str(d.get('Año')) in ('2026','OFE_2026'):
        evidence[family]={'codigo':code,'fila':i,'nombre':str(d.get('Nombre Carrera','')),'anio':'2026'}
    if len(evidence)==3:break
w.close();assert len(evidence)==3
for f,(c,n) in targets.items():
    assert not any(f in x['familias'] for x in old)
    new.append({'clave':json.dumps([c,'CO','V'],separators=(',',':')),'codcarpr':c,'codigos_base':[evidence[f]['codigo']],'familias':[f],'sede':'CO','jornada':'V','equivalencias_h5':[],'evidencia_perfil':[],'fuente_perfil':'D_MAPEO_FAMILIA_CO_APROBADO_20261028','perfiles_duracion_tipo':[],'alcance_temporal':[2026],'nombre_referencia':n,'evidencia_oferta':evidence[f],'nota':'Equivalencia de familia para cobertura; no adjudica versión ni código personal.'})
NEW.mkdir(parents=True,exist_ok=True)
content=json.dumps(new,ensure_ascii=False,indent=2)+'\n'; out=NEW/'grupos_existentes.json'
if out.exists() and out.read_text()!=content:raise ValueError('La nueva edición ya existe y difiere')
out.write_text(content)
manifest={'clase':'B oferta SIES; C integración; D autorización Alexi en esta conversación; E C35J4 pendiente','anterior':{'ruta':str(OLD),'sha256':sha(OLD)},'nuevo':{'ruta':str(out),'sha256':sha(out)},'motivo':'Agregar sólo tres familias de Concepción para cobertura DA frente a MU; edición histórica y diccionario personal intactos','oferta':{'ruta':str(p),'sha256':sha(p),'hoja':'in','evidencia':evidence},'gobernanza_sede':{'ruta':'gobernanza_sede.tsv','sha256':sha(ROOT/'gobernanza_sede.tsv'),'regla':'CO → S3; V → J2 según oferta y equivalencias previamente aprobadas'},'grupos_antes':len(old),'grupos_despues':len(new),'familias_nuevas':list(targets),'c35j4':'Sólo se revisa; no se añade equivalencia por nombre. Mantener pendiente hasta evidencia suficiente.'}
(NEW/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'grupos':len(new),'sha256':sha(out)},ensure_ascii=False))
