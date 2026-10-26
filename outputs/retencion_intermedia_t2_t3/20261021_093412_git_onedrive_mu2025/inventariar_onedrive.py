from pathlib import Path
import unicodedata,os,json,datetime
P=Path(__file__).resolve().parent
root=next(p for p in Path('/Users/alexi/Library/CloudStorage').iterdir() if p.name.startswith('OneDrive-InstitutoProfesional'))
def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if not unicodedata.combining(c))
roots=[]
for base in [root/'0 BASES DE DATOS',root/'RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9']:
 if base==root/'0 BASES DE DATOS':
  roots.extend(p for p in base.iterdir() if p.is_dir() and norm(p.name) in ['matricula unificada','matricula','_derivados_gobernados'])
 else:
  roots.extend(p for p in base.iterdir() if p.is_dir() and (norm(p.name) in ['2025','matricula','modificacion datos historicos','2026']))
rawroot=next(p for p in root.iterdir() if p.name.startswith('Datos DAI'))
for base,dirs,files in os.walk(rawroot):
 if Path(base).name.startswith('1.2.1.1 SIES'):
  roots.append(Path(base));dirs[:]=[]
# Metadata only; no contents of student data are copied.
files=[];errors=[]
for source_root in roots:
 for base,dirs,names in os.walk(source_root,onerror=lambda e:errors.append(str(e))):
  dirs[:]=[x for x in dirs if x not in ['.git','node_modules','__pycache__']]
  for n in names:
   p=Path(base)/n
   if p.name=='.DS_Store':continue
   try:s=p.stat()
   except OSError as e:errors.append(str(e));continue
   files.append({'ruta':str(p),'raiz':str(source_root),'bytes':s.st_size,'mtime_metadato':datetime.datetime.fromtimestamp(s.st_mtime).astimezone().isoformat(),'extension':p.suffix.lower()})
# Duplicate sources may be under nested roots; deduplicate paths.
files=list({r['ruta']:r for r in files}.values())
codes=[f for f in files if f['extension'] in ['.py','.sql','.ipynb','.pq','.m','.r','.bas','.ps1','.vbs']]
archives=[f for f in files if f['extension'] in ['.zip','.rar','.7z'] and ('2025' in f['ruta'] or any(s in norm(Path(f['ruta']).name) for s in ['codig','script','respaldo','backup']))]
relevant25=[f for f in files if '2025' in f['ruta'] and any(v in norm(f['ruta']) for v in ['matric','sies','codigo','script'])]
d={'fecha':datetime.datetime.now().astimezone().isoformat(),'raices':[str(p) for p in roots],'archivos':files,'scripts_consultas':codes,'archivos_comprimidos_candidatos':archives,'candidatos_2025':relevant25,'errores_metadatos':errors}
(P/'INVENTARIO_ONEDRIVE.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('ARCHIVOS',len(files),'CODIGOS',len(codes),'ARCHIVOS_2025',len(relevant25),'COMPRIMIDOS',len(archives),'ERRORES',len(errors))
for f in codes:print('CODIGO',f['ruta'],f['bytes'])
for f in archives:print('ARCHIVO',f['ruta'],f['bytes'])
for f in relevant25:
 if '/2025/' in f['ruta'] and 'CARLOS' in f['ruta']:print('RESPALDO_2025',f['ruta'],f['bytes'])
