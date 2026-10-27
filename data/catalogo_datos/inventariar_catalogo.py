import os, re, json, hashlib, unicodedata, collections, datetime, subprocess
from pathlib import Path
root=next(Path.home().glob('Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastia*'))/'0 BASES DE DATOS'
files=sorted(p for p in root.rglob('*') if p.is_file()); rows=[]
for i,p in enumerate(files):
 rel=str(p.relative_to(root)); n=unicodedata.normalize('NFKD',rel).encode('ascii','ignore').decode().upper(); sz=p.stat().st_size
 if n.startswith('_DERIVADOS_GOBERNADOS/') or any(t in n for t in ['RETENCION_IPSS','RETENCION IPSS','TITULADOS_IPSS','PLAN TRABAJO','PROYECTO-EDUCATIVO','POLITICA-','ESTRATEGIA-','CATALOGO DE REPORTES','CALENDARIO-ACADEMICO','RES.-ACREDIT']): category='INSTITUCIONALES'; confidence='B/E'
 elif 'DATOSDEALUMNOS' in n or n.startswith('MATRICULA UNIFICADA/'): category='FUENTES_INTERNAS'; confidence='B/E'
 elif any(t in n for t in ['MRUN DATOS ABIERTOS/','MATRICULA_ED_SUPERIOR','TITULADOS_ED_SUPERIOR','MATRICULA_2007_202','OFERTA_ACADEMICA_2010','OFERTA_ACADEMICA_2026_SIES','INFORME_RETENCION_SIES','INFORME_MATRICULA_EDUCACION_SUPERIOR','PAC_WEB_','TITULADO_2007','TITULADO_2025_WEB','BUSCADOR_EMPLEABILIDAD','GLOSARIO_DE_TITULADOS']): category='SIES_PUBLICAS'; confidence='B/E'
 else: category='INSTITUCIONALES'; confidence='E: clasificación provisional por ubicación/nombre, origen no confirmado'
 years=sorted(set(re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',p.name))); h=hashlib.sha256(); error=None
 try:
  result=subprocess.run(['/usr/bin/openssl','dgst','-sha256',str(p)],capture_output=True,text=True,timeout=5)
  digest=result.stdout.split()[-1] if result.returncode==0 and result.stdout else None
  if not digest: error='archivo no legible o no disponible'
 except (OSError,subprocess.TimeoutExpired) as e: digest=None; error='lectura excede 5 segundos o no disponible'
 rows.append({'ruta':str(p),'bytes':sz,'sha256':digest,'estado_hash':'calculado' if digest else 'pendiente: '+error,'tipo':p.suffix.lower() or 'sin extensión','clasificacion':category,'nivel_respaldo':confidence,'anos_en_nombre':years,'cobertura_real':'Pendiente de confirmar en fuente o manifiesto','edicion_publicacion':'Pendiente de confirmar; nombre no acredita fecha de publicación','glosario_oficial_asociado':'Pendiente de vincular con evidencia'})
 if i%25==0: print(i+1,'/',len(files),flush=True)
counts=collections.Counter(r['clasificacion'] for r in rows); hashes=collections.defaultdict(list)
for r in rows:
 if r['sha256']: hashes[r['sha256']].append(r['ruta'])
dup=[{'sha256':k,'rutas':v} for k,v in hashes.items() if len(v)>1]
out=Path('data/catalogo_datos');out.mkdir(parents=True,exist_ok=True)
obj={'estado':'INVENTARIO_METADATOS_PRELIMINAR','fecha':datetime.datetime.now().astimezone().isoformat(),'raiz':str(root),'metodo':'Metadatos y lectura binaria para SHA-256; no se interpretó contenido de fuentes internas. La clasificación por nombre/ubicación es provisional salvo respaldo identificado.','archivos':len(rows),'bytes_logicos':sum(r['bytes'] for r in rows),'conteo_por_seccion':dict(counts),'archivos_sin_hash':sum(r['sha256'] is None for r in rows),'secciones':{k:[r for r in rows if r['clasificacion']==k] for k in ['SIES_PUBLICAS','FUENTES_INTERNAS','INSTITUCIONALES']},'duplicados_sha256':dup,'referencias_institucionales':{'diccionario':'data/diccionario_sies_seguimiento/activo.json','indicador_borrador':'data/reglas_negocio/indicador_intertrimestral/REGLA.json','avance_historico':'outputs/fase_e_hito2_excel_v3_20261027/','catalogo_fuentes':'data/catalogo_fuentes/CATALOGO_FUENTES.json'},'pendientes':['Origen, cobertura real, edición y glosario por archivo sujetos a evidencia.','Los nombres no certifican carácter público u oficial.']}
(out/'CATALOGO_DATOS_IPSS.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
md=['# Catálogo de datos IPSS — inventario preliminar','',f'Raíz: `{root}`',f'Archivos: {len(rows)}; bytes lógicos: {obj["bytes_logicos"]}; sin hash: {obj["archivos_sin_hash"]}.','Las fechas y años extraídos del nombre no prueban cobertura ni publicación. Las fuentes internas solo se leyeron como bytes para hash, sin interpretar su contenido.','']
for k in ['SIES_PUBLICAS','FUENTES_INTERNAS','INSTITUCIONALES']:
 md += ['## '+k,'',f'{counts[k]} archivos. La clasificación por nombre o ubicación debe verificarse.', '', '| Ruta relativa | Bytes | SHA-256 | Años en nombre |', '| --- | ---: | --- | --- |']
 for r in obj['secciones'][k]: md.append('| '+str(Path(r['ruta']).relative_to(root)).replace('|','\\|')+' | '+str(r['bytes'])+' | '+str(r['sha256'] or 'Pendiente')+' | '+(', '.join(r['anos_en_nombre']) or 'Pendiente')+' |')
 md.append('')
md+=['## Duplicados por hash','']
for d in dup: md+=['- `'+d['sha256']+'`: '+ '; '.join('`'+str(Path(x).relative_to(root))+'`' for x in d['rutas'])]
md+=['','## Referencias gobernadas','']+[f'- {k}: `{v}`' for k,v in obj['referencias_institucionales'].items()]+['','Cobertura real, edición, fecha de publicación y glosario: pendientes cuando no existe respaldo comprobado.']
(out/'CATALOGO_DATOS_IPSS.md').write_text('\n'.join(md)+'\n')
proj=Path('PROYECTO_IPSS.json'); a=json.loads(proj.read_text());a['recursos_comunes']['catalogo_datos_ipss']='data/catalogo_datos/CATALOGO_DATOS_IPSS.json';proj.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'archivos':len(rows),'bytes':obj['bytes_logicos'],'sin_hash':obj['archivos_sin_hash'],'duplicados_grupos':len(dup),'secciones':counts},ensure_ascii=False),flush=True)
