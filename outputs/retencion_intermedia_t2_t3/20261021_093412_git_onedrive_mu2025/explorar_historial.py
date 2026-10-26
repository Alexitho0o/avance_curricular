from pathlib import Path
import subprocess,json,re,hashlib,datetime,os,unicodedata,collections
P=Path(__file__).resolve().parent
repos=[Path('/Users/alexi/Documents/GitHub/avance_curricular'),Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN')]
res=[]
for repo in repos:
 commits=int(subprocess.check_output(['git','-C',str(repo),'rev-list','--all','--count'],text=True))
 objects=subprocess.check_output(['git','-C',str(repo),'rev-list','--objects','--all'],text=True).splitlines();candidates=[]
 for obj in objects:
  if ' ' not in obj:continue
  oid,name=obj.split(' ',1);ext=Path(name).suffix.lower()
  if ext in {'.py','.sql','.ipynb','.pq','.m','.r','.bas','.ps1','.vbs'} or (ext in {'.json','.md','.txt'} and any(v in name.lower() for v in ['2025','matric','mu202','campos_ing','for_ing'])):candidates.append((oid,name))
 proc=subprocess.Popen(['git','-C',str(repo),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
 hits=[];scanned=0;bytesread=0
 for oid,name in candidates:
  proc.stdin.write((oid+'\n').encode());proc.stdin.flush();head=proc.stdout.readline().decode().strip().split()
  if len(head)!=3 or head[1]!='blob':continue
  n=int(head[2]);blob=proc.stdout.read(n);proc.stdout.read(1);scanned+=1;bytesread+=n
  content=blob.decode('utf-8',errors='replace')
  terms={term:len(re.findall(pattern,content,re.I)) for term,pattern in {'campo_origen':r'ANIO_ING_ORI','campo_ingreso':r'ANOINGRESO','archivo_MU2025':r'2025[/\\]2025\.xlsx|2025\.xlsx|08-05-2025_22-26-22','MU2025_explicito':r'MU[ _-]?2025|Matr[ií]cula Unificada 2025','conversion_2024_2025':r'2024.{0,80}2025|2025.{0,80}2024'}.items()}
  if not any(terms.values()):continue
  if terms['archivo_MU2025'] or terms['MU2025_explicito'] or terms['campo_origen']:
   anchors=[i for i,line in enumerate(content.splitlines(),1) if re.search(r'2025\.xlsx|08-05-2025_22|ANIO_ING_ORI|MU[ _-]?2025',line,re.I)]
   hits.append({'git_blob':oid,'ruta_historica':name,'sha256_contenido':hashlib.sha256(blob).hexdigest(),'bytes':n,'terminos':terms,'lineas_ancla':anchors[:60]})
 proc.stdin.close();proc.stdout.close();proc.wait()
 rr={'repositorio':str(repo),'commits_alcanzables':commits,'objetos_con_ruta':len(objects),'blobs_texto_revisados':scanned,'bytes_leidos':bytesread,'coincidencias':hits}
 res.append(rr)
 print(repo.name,commits,scanned,'coincidencias',len(hits),flush=True)
(P/'HISTORIAL_GIT_BUSQUEDA.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
print('GUARDADO',flush=True)
