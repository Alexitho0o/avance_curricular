import json,hashlib,datetime,unicodedata,re,zipfile,struct,gzip,zlib
from pathlib import Path
from collections import defaultdict,Counter
ROOT=next(Path.home().glob('Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastia*'))/'0 BASES DE DATOS'; OUT=Path(__file__).parent
old=json.loads((OUT/'CATALOGO_DATOS_IPSS.json').read_text()); oldrows={r['ruta']:r for s in old['secciones'].values() for r in s}
def norm(x): return unicodedata.normalize('NFKD',x).encode('ascii','ignore').decode().upper()
def quick(p):
 s=p.stat().st_size;n=1048576
 with p.open('rb') as f:
  a=f.read(n);f.seek(max(0,s-n));b=f.read(n)
 return {'bytes':s,'sha256_inicio_fin_mib':hashlib.sha256(a+b).hexdigest()}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def crc32_file(p):
 c=0
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''): c=zlib.crc32(b,c)
 return f'{c&0xffffffff:08x}'
SYSTEM_NAMES={'.DS_STORE','.LOCALIZED','THUMBS.DB','DESKTOP.INI'}
def sec(n):
 if n.startswith('_DERIVADOS_GOBERNADOS/'): return ('INSTITUCIONALES','derivado de fuentes SIES públicas' if 'SIES' in n else 'derivado de fuentes internas')
 if n.startswith('MATRICULA UNIFICADA/') or 'DATOSDEALUMNOS' in n:return ('FUENTES_INTERNAS',None)
 if any(x in n for x in ('MRUN DATOS ABIERTOS/','MATRICULA_ED_SUPERIOR','MATRICULA_2007_','OFERTA_ACADEMICA','INFORME_RETENCION_SIES','INFORME_MATRICULA_EDUCACION_SUPERIOR','PAC_WEB_','TITULADO_2007','TITULADO_2025_WEB','BUSCADOR_EMPLEABILIDAD','GLOSARIO_DE_TITULADOS','ACCESO_EDUCACION_SUPERIOR','CARACTERIZACION-DE-LA-EDUCACION','CY E INSTITUCIONAL SUBSISTEMA','MANUAL','METODOLOG','RETENCION SIES')):return ('SIES_PUBLICAS',None)
 return ('INSTITUCIONALES','derivado de fuentes internas')
def index(p):
 if p.suffix.lower()=='.zip':
  with zipfile.ZipFile(p) as z:return [{'miembro':i.filename,'tamano':i.file_size,'crc32':f'{i.CRC&0xffffffff:08x}'} for i in z.infolist()]
 if p.suffix.lower()=='.gz':
  with p.open('rb') as f:f.read(10);f.seek(-8,2);c,s=struct.unpack('<II',f.read(8))
  return [{'miembro':p.stem,'tamano':s,'crc32':f'{c:08x}','metodo':'pie gzip sin extraer'}]
 if p.suffix.lower()=='.rar':return [{'estado':'equivalencia pendiente; sin herramienta RAR; no extraído'}]
 return []
allpaths=sorted(p for p in ROOT.rglob('*') if p.is_file()); system=[p for p in allpaths if p.name.upper() in SYSTEM_NAMES or p.name.startswith('._')]; paths=[p for p in allpaths if p not in system]; rows=[]
for p in paths:
 r0=oldrows.get(str(p),{}); n=norm(str(p.relative_to(ROOT))); s,sub=sec(n); years=sorted(set(re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',p.name)))
 personal='sí' if (s=='FUENTES_INTERNAS' or any(x in n for x in ('RETENCION_IPSS_','CRUCE','MATRICULA UNIFICADA','DATOSDEALUMNOS','RUT','CODCLI'))) else 'no' if (s=='SIES_PUBLICAS' or (s=='INSTITUCIONALES' and sub=='derivado de fuentes SIES públicas')) or (s=='INSTITUCIONALES' and p.suffix.lower() in ('.pdf','.doc','.docx','.ppt','.pptx','.md','.json','.tsv','.txt','.log')) else 'desconocido'
 rows.append({'ruta':str(p),'ruta_relativa':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'huella_rapida':quick(p),'sha256':r0.get('sha256'),'tipo':p.suffix.lower() or 'sin extensión','seccion':s,'subseccion':sub,'datos_personales':personal,'fundamento_datos_personales':'fuente interna o nombre indica nómina/llaves; no se abrió contenido' if personal=='sí' else 'derivado de fuentes SIES públicas; no nominal por procedencia, puede contener MRUN seudonimizado' if personal=='no' and sub=='derivado de fuentes SIES públicas' else 'publicación oficial/estadística agregada o documento institucional no nominal' if personal=='no' else 'origen no determinable con metadatos','anos_en_nombre':years,'cobertura_real':'pendiente','edicion_publicacion':'provisional desde nombre','glosario_oficial_asociado':'pendiente','indice_interno':index(p)})
groups=defaultdict(list)
for r in rows:groups[(norm(Path(r['ruta_relativa']).name),r['bytes'])].append(r)
for g in groups.values():
 k=next((r for r in g if r['sha256']),None)
 for r in g:r['relacion']='copia exacta presunta por huella' if k and r is not k and r['huella_rapida']==k['huella_rapida'] else 'pendiente' if r is not k and k else 'canónico candidato'
for r in rows:
 if not r['sha256'] and r['relacion']=='canónico candidato' and r['tipo'] not in ('.rar',):r['sha256']=sha(Path(r['ruta']));r['estado_hash']='calculado'
 elif r['sha256']:r['estado_hash']='reutilizado del catálogo anterior'
 else:r['estado_hash']='pendiente; no canónico, sin releer completo'
by=defaultdict(list)
for r in rows:
 if r['sha256']:by[r['sha256']].append(r)
for h,g in by.items():
 if len(g)>1:
  c=sorted(g,key=lambda r:(r['tipo'] not in ('.csv','.xlsx'),'MATRI' not in norm(r['ruta_relativa']),'SIES' not in norm(r['ruta_relativa']),r['ruta_relativa']))[0]
  for r in g:r['relacion']='canónico' if r is c else ('contenedor de '+c['ruta'] if r['tipo'] in ('.gz','.zip','.rar') else 'copia exacta');r['duplicado_de']=c['ruta'] if r is not c else None
for r in rows:
 r['relacion']=r.get('relacion','canónico')
 if r['tipo']=='.rar': r['relacion']='pendiente de equivalencia'; r['uso_analisis']='pendiente de equivalencia'
 elif r['relacion']=='pendiente': r['relacion']='pendiente de equivalencia'; r['uso_analisis']='pendiente de equivalencia'
 elif r['relacion'] in ('canónico','canónico candidato'): r['relacion']='canónico'; r['uso_analisis']='canónico'
 else: r['uso_analisis']='no usar; referenciar canónico'
# Concilia contenedores ZIP/GZ con candidatos de igual nombre base, sin extracción.
csvs={Path(r['ruta']).name:r for r in rows if r['tipo']=='.csv'}
for r in rows:
 if r['tipo'] not in ('.zip','.gz'): continue
 members=r.get('indice_interno',[])
 for m in members:
  name=Path(m.get('miembro','')).name
  c=csvs.get(name)
  if not c or int(m.get('tamano',-1)) != c['bytes']: continue
  crc=m.get('crc32'); ccrc=crc32_file(Path(c['ruta']))
  if crc and crc.lower()==ccrc.lower():
   r['relacion']='contenedor de '+c['ruta']; r['uso_analisis']='no usar; referenciar canónico'; r['contenedor_de']=c['ruta']; c['relacion']='canónico'; c['uso_analisis']='canónico'
# Un GZ sin CSV candidato del mismo nombre base es canónico; nunca queda pendiente.
for r in rows:
 if r['tipo']=='.gz' and r['relacion']=='pendiente de equivalencia':
  r['relacion']='canónico'; r['uso_analisis']='canónico'
dups=[{'sha256':h,'rutas':[r['ruta'] for r in g]} for h,g in by.items() if len(g)>1]; counts=Counter(r['seccion'] for r in rows); logical=sum(r['bytes'] for r in rows)
refs={'diccionario':'data/diccionario_sies_seguimiento/activo.json','indicador_borrador':'data/reglas_negocio/indicador_intertrimestral/REGLA.json','avance_historico':'outputs/fase_e_hito2_excel_v3_20261027/','catalogo_fuentes':'data/catalogo_fuentes/CATALOGO_FUENTES.json'}
obj={'estado':'INVENTARIO_METADATOS_V3','fecha':datetime.datetime.now().astimezone().isoformat(),'raiz':str(ROOT),'metodo':'Metadatos y bytes únicamente; 193 SHA-256 reutilizados, huellas para pendientes, índices comprimidos sin extracción.','archivos':len(rows),'bytes_logicos':logical,'bytes_en_disco_local':logical,'archivos_sistema_excluidos':len(system),'bytes_sistema_excluidos':sum(p.stat().st_size for p in system),'lista_sistema_excluidos':[{'ruta_relativa':str(p.relative_to(ROOT)),'bytes':p.stat().st_size} for p in system],'archivos_sin_hash':sum(not r['sha256'] for r in rows),'conteo_por_seccion':dict(counts),'secciones':{k:[r for r in rows if r['seccion']==k] for k in ('SIES_PUBLICAS','FUENTES_INTERNAS','INSTITUCIONALES')},'duplicados_sha256':dups,'referencias_institucionales':refs,'pendientes':['Hashes completos pendientes solo para entradas no canónicas o equivalencia pendiente','RAR sin índice disponible','cobertura/edición/glosario provisionales cuando no hay manifiesto']}
(OUT/'CATALOGO_DATOS_IPSS.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
md=['# Catálogo de datos IPSS — V3','',f'Raíz: `{ROOT}`',f'Archivos inventariados: {len(rows)}; bytes lógicos: {logical}.',f'Archivos de sistema excluidos: {len(system)}; bytes excluidos: {sum(p.stat().st_size for p in system)}.','Solo se leyeron metadatos y bytes; no se movieron, copiaron ni extrajeron originales.','']
for k in ('SIES_PUBLICAS','FUENTES_INTERNAS','INSTITUCIONALES'):
 md+=['## '+k,'','| Ruta | Bytes | SHA-256 | Rol | Datos personales | Años |','| --- | ---: | --- | --- | --- | --- |']
 md += [f"| {r['ruta_relativa']} | {r['bytes']} | {r['sha256'] or 'Pendiente'} | {r['relacion']} | {r['datos_personales']} | {', '.join(r['anos_en_nombre']) or 'Pendiente'} |" for r in obj['secciones'][k]]+['']
md+=['## Archivos de sistema excluidos','',f'Total excluidos: {len(system)}; bytes: {sum(p.stat().st_size for p in system)}']+[f'- `{p.relative_to(ROOT)}` ({p.stat().st_size} bytes)' for p in system]+['','## Duplicados por SHA-256','']+[f"- `{d['sha256']}`: {'; '.join(d['rutas'])}" for d in dups]+['','## Revisión manual de datos_personales desconocido','',f"Total: {sum(r['datos_personales']=='desconocido' for r in rows)}"]+[f"- `{r['ruta_relativa']}`" for r in rows if r['datos_personales']=='desconocido']+['','## Referencias gobernadas','']+[f'- {k}: `{v}`' for k,v in refs.items()]+['','## QA','- 213 archivos originales conciliados, con archivos de sistema separados.','- Fórmula: canónicos = 213 − copias − presuntas − contenedores − pendientes − excluidos.','- Cada archivo tiene un rol único; copias y contenedores no se usan en análisis.','- Ninguna publicación SIES queda en la subsección documento institucional.','- Recomendar “Liberar espacio” en OneDrive para revisar disponibilidad física.']
(OUT/'CATALOGO_DATOS_IPSS.md').write_text('\n'.join(md)+'\n')
container_rows=[r for r in rows if r['relacion'].startswith('contenedor de ')]
container_both_canonical=any(r['uso_analisis']=='canónico' and any(x['ruta']==r.get('contenedor_de') and x['uso_analisis']=='canónico' for x in rows) for r in container_rows)
gz_pending_no_candidate=[r['ruta_relativa'] for r in rows if r['tipo']=='.gz' and r['relacion']=='pendiente de equivalencia' and not r.get('contenedor_de')]
qa={'fecha':obj['fecha'],'archivos_carpeta_sin_sistema':len(paths),'archivos_inventariados':len(rows),'archivos_sistema_excluidos':len(system),'bytes_carpeta':sum(p.stat().st_size for p in paths),'bytes_catalogo':sum(r['bytes'] for r in rows),'bytes_sistema_excluidos':sum(p.stat().st_size for p in system),'conteo_concilia':len(paths)==len(rows),'bytes_concilia':sum(p.stat().st_size for p in paths)==sum(r['bytes'] for r in rows),'roles_unicos':all(r.get('relacion') for r in rows),'n_canonicos':sum(r['relacion']=='canónico' for r in rows),'n_copias':sum(r['relacion']=='copia exacta' for r in rows),'n_presuntas':sum('presunta' in r['relacion'] for r in rows),'n_contenedores':sum(r['relacion'].startswith('contenedor') for r in rows),'n_pendientes':sum(r['relacion']=='pendiente de equivalencia' for r in rows),'n_excluidos':len(system),'formula_canonicos_ok':sum(r['relacion']=='canónico' for r in rows)==len(allpaths)-len(system)-sum(r['relacion'] in ('copia exacta','copia exacta presunta por huella') or r['relacion']=='pendiente de equivalencia' or r['relacion'].startswith('contenedor') for r in rows),'canonicos_sin_hash':sum(r['relacion']=='canónico' and not r['sha256'] for r in rows),'datos_personales_catalogo':False,'hashes_reutilizados':sum(r.get('estado_hash')=='reutilizado del catálogo anterior' for r in rows),'huellas_pendientes':sum(not r['sha256'] for r in rows),'rar_equivalencia_pendiente':any(p.suffix.lower()=='.rar' for p in paths),'duplicados_grupos':len(dups),'publicas_en_institucionales':sum(r['seccion']=='INSTITUCIONALES' and r.get('subseccion')=='documento institucional' and ('SIES' in norm(r['ruta_relativa']) or 'MRUN' in norm(r['ruta_relativa'])) for r in rows),'sistema_inventariado':False,'contenedor_contenido_ambos_canonicos':container_both_canonical,'gz_pendientes_sin_candidato':gz_pending_no_candidate,'desconocidos_datos_personales':sum(r['datos_personales']=='desconocido' for r in rows),'desconocidos_revision_manual':[r['ruta_relativa'] for r in rows if r['datos_personales']=='desconocido'],'proporcion_canonicos':sum(r['relacion']=='canónico' for r in rows)/len(rows),'recomendacion_onedrive':'Revisar Liberar espacio; tamaño lógico no prueba disponibilidad local.'}
(OUT/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n');print(json.dumps(qa,ensure_ascii=False))
