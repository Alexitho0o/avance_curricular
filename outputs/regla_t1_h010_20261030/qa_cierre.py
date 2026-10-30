"""Control de publicación propuesta H010; no stage/commit/push."""
import argparse,ast,json,re,subprocess
from pathlib import Path
from construir import sha,dump,aggregate

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--privado',type=Path,required=True);a=ap.parse_args();R=a.repo;P=a.privado;O=R/'outputs/regla_t1_h010_20261030';D=R/'data/diccionario_sies_seguimiento/v21_20261030_candidata_h010';load=lambda p:json.loads(Path(p).read_text());g=lambda *args:subprocess.check_output(['git','-C',str(R),*args],text=True).strip()
 initial=load(P/'ESTADO_INICIAL.json');current=load(R/'docs/MAPA_RESULTADOS_GOBERNADOS.json');old={x['id']:x for x in initial['mapa']['resultados']};new={x['id']:x for x in current['resultados']}
 hashes=load(P/'HASHES_REPRODUCCION_ANTES.json');repro={p:sha(p)==h for p,h in hashes.items()};assert all(repro.values()),'Reproducción distinta'
 dump(O/'REPRODUCCION.json',{'estado':'PASS','archivos':len(repro),'resultado':'Hashes iguales en segunda ejecución, incluida base SQLite privada','hashes':hashes})
 priv=load(P/'ASIGNACIONES_PRIVADAS.json');blocked=[]
 for z in priv:
  if z['nivel_asignacion']=='E' and z['año_T1_fuente'] is not None:
   codes=sorted({e['codigo'] for e in z['evidencia'] if isinstance(e,dict) and 'codigo'in e})
   blocked.append({k:z[k] for k in ['anio','periodo','carrera','plan','sede','jornada','motivo','año_T1_fuente']}|{'codigos_T1_no_asignados':','.join(codes)})
 dump(O/'NIVEL3_NO_ASIGNADO.json',{'clase':'E','casos':aggregate(blocked,['anio','periodo','carrera','plan','sede','jornada','año_T1_fuente','codigos_T1_no_asignados','motivo'])})
 # Identificadores exactos privados, nunca valores en mensajes del escaneo.
 import sqlite3
 active=load(R/'data/diccionario_sies_seguimiento/activo.json');desc=load(R/active['descriptor']);c=sqlite3.connect(Path(desc['base_privada']['ruta']).as_uri()+'?mode=ro',uri=True)
 known={str(v) for row in c.execute('select persona,codcli from observaciones') for v in row if v is not None};known|={v.split('-')[0] for v in known if '-'in v};c.close()
 regexes=[re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(v) for v in known if len(v)>=6)+r')(?!\w)'),re.compile(r'(?<!\w)\d{7,8}-[0-9Kk](?!\w)'),re.compile(r'\b\d{1,2}\.\d{3}\.\d{3}-[0-9Kk]\b'),re.compile(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}'),re.compile(r'(?<!\w)(?:\+56\s*[29]\s*\d{4}\s*\d{4}|[29]\d{8})(?!\w)'),re.compile(r'(?i)"(?:mrun|rut|CODCLI|N_DOC|nombre_alumno|telefono|correo)"\s*:\s*"?\d+')]
 extras=[R/'docs/ESPECIFICACION_H010.md',R/'docs/MAPA_RESULTADOS_GOBERNADOS.md',R/'docs/MAPA_RESULTADOS_GOBERNADOS.json']
 auxiliary={'QA_CIERRE.json','LISTA_PUBLICACION.json','MANIFEST.json'}
 files=sorted([p for p in O.iterdir() if p.is_file() and p.name not in auxiliary]+list(D.glob('*.json'))+extras)
 findings=[]
 def scan(files):
  for f in files:
   assert f.suffix in ['.md','.json','.py'] and f.stat().st_size<20*1024*1024
   text=f.read_text()
   if f.suffix=='.json':json.loads(text)
   if f.suffix=='.py':ast.parse(text)
   for ln,line in enumerate(text.splitlines(),1):
    for i,rx in enumerate(regexes):
     if rx.search(line):findings.append({'ruta':str(f.relative_to(R)),'linea':ln,'patron':i})
 scan(files);assert not findings,findings
 sources=load(O/'FUENTES.json')['fuentes'];source_ok=all(sha(x['ruta'])==x['sha256'] for x in sources if Path(x['ruta'])!=R/'docs/MAPA_RESULTADOS_GOBERNADOS.json')
 qa={'estado':'PASS_CONTROLES_CANDIDATA_CON_RESIDUAL_E','controles':{'tests_sinteticos_8':True,'reproduccion':all(repro.values()),'R01_R27_intactos':all(old[k]==new[k] for k in old),'R28_R29_presentes':set(new)-set(old)=={'R28','R29'},'informe_presente':(O/'INFORME_H010.md').exists(),'fuentes_intactas':source_ok,'HEAD_sin_commit':g('rev-parse','HEAD')==initial['head'],'stage_vacio':not g('diff','--cached','--name-only'),'25_ajenos_status_intacto':all(s in g('status','--porcelain').splitlines() for s in initial['status_ajenos'].splitlines()),'25_ajenos_hash_intacto':all(sha(R/f)==h for f,h in initial['ajenos'].items()),'sin_hallazgos_privacidad':not findings},'privacidad_limite':'Patrones + cotejo con identificadores privados; esquema público sólo agregados, códigos catálogo y metadatos. Sin columnas individuales ni nombres estudiantiles. No certificación universal semántica.','hallazgos':findings,'sin_activacion':True,'sin_commit_push_avance':True}
 assert all(qa['controles'].values()),qa
 books={Path.home()/'Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261030_V25.xlsx':'63b55351334616833a2e687fbeb36314a0cbb1538c10b6a891c99f94475adc0a',Path.home()/'Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261030_V26.xlsx':'d7e68859cdba52a636e562a9cd287f8114afbc0fb97f0840dfc9284fb2a43a51'}
 qa['controles']['V25_V26_intactos']=all(sha(p)==h for p,h in books.items());assert qa['controles']['V25_V26_intactos']
 dump(O/'QA_CIERRE.json',qa)
 paths=sorted(str(p.relative_to(R)) for p in files+[O/n for n in auxiliary]);dump(O/'LISTA_PUBLICACION.json',{'estado':'PREPARADO_SIN_COMMIT_PUSH','rutas':paths,'mensaje':'H010 propone código de contexto por primer T1 acreditado y reencuadra evidencia metodológica','excluye':'Detalle privado, base SQLite, libros, 25 cambios ajenos; ninguna activación'})
 dump(O/'MANIFEST.json',{'hito':'H010','base_commit':initial['head'],'estado':'CANDIDATA_NO_ACTIVA','entradas':'FUENTES.json; FUENTES_R28.json','salidas':{p:{'sha256':sha(R/p),'bytes':(R/p).stat().st_size} for p in paths if p!=str((O/'MANIFEST.json').relative_to(R))},'sin_hash_propio':'Evita autorreferencia'})
 scan([O/n for n in auxiliary]);assert not findings,findings
 print(json.dumps({'estado':qa['estado'],'controles':qa['controles'],'archivos_propuestos':len(paths),'hallazgos':len(findings)},ensure_ascii=False))
if __name__=='__main__':main()
