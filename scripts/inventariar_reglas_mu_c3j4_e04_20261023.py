"""Inventario de búsqueda local de reglas; solo lectura de fuentes y Git."""
from pathlib import Path
import subprocess,json,re,hashlib,datetime
R=Path('/Users/alexi/Documents/GitHub/avance_curricular');O=R/'outputs/origen_versiones_c3j4_e04_20261023_163300'
repos=[R,Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN'),Path('/Users/alexi/Documents/GitHub/IPSS_Procesos_SIES')]
result=[]
def run(repo,*args):
 p=subprocess.run(['git','-C',str(repo),*args],text=True,capture_output=True);return {'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
for repo in repos:
 if not (repo/'.git').exists():result.append({'repo':str(repo),'estado':'Sin repositorio local accesible'});continue
 hist=run(repo,'log','--all','--reverse','--format=%H %aI %s');hs=hist['stdout'].splitlines()
 obj=run(repo,'rev-list','--objects','--all');entries=[line.split(' ',1) for line in obj['stdout'].splitlines() if ' ' in line]
 ext={'.py','.sql','.ipynb','.r','.R','.vba','.m','.ps1','.sh'}
 relevant=[{'objeto':a,'ruta':b} for a,b in entries if Path(b).suffix in ext and re.search(r'matric|\bmu\b|mu202[125]|202[125]|sies|umas',b,re.I)]
 specific=run(repo,'log','--all','--format=%H %aI %s','--name-only','-G','IETMREOL|IINF20241|I162S2C3J4','--','*.py','*.sql','*.ipynb','*.R','*.r')
 result.append({'repo':str(repo),'rama':run(repo,'branch','--show-current')['stdout'].strip(),'HEAD':run(repo,'rev-parse','HEAD')['stdout'].strip(),'remotos':run(repo,'remote','-v')['stdout'],'commits_locales':len(hs),'primer_commit':hs[0] if hs else None,'ultimo_commit':hs[-1] if hs else None,'objetos_codigo_rutas_candidatas':relevant,'historial_cadenas_especificas':specific,'alcance':'Objetos y refs locales; no fetch, no prueba de ausencia en repositorios remotos u otros respaldos.'})
(O/'BUSQUEDA_GIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps([{'repo':x['repo'],'commits':x.get('commits_locales'),'primer':x.get('primer_commit'),'objetos_codigo':len(x.get('objetos_codigo_rutas_candidatas',[])),'lineas_historial_especifico':len(x.get('historial_cadenas_especificas',{}).get('stdout','').splitlines())} for x in result],ensure_ascii=False))
