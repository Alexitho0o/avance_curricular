"""Inventario de sólo lectura. Distingue archivos usados, referencias y usos no acreditados."""
import collections as C
import hashlib
import json
import re
import unicodedata
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
P=Path.home()/'.local/share/ipss/h015_20261030'
CLOUD=next(Path.home().glob('Library/CloudStorage/OneDrive-Instituto*/IPSS_CONCILIACION_UMAS_SIES_BASES'))
TR=ROOT/'outputs/trazabilidad_integral_umas_sies_20261025'
H8=TR/'h008_20261030'
H14=ROOT/'outputs/primer_t1_h014_20261030'
load=lambda p:json.loads(Path(p).read_text())
def dump(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def table(h,rows):return '\n'.join(['| '+' | '.join(h)+' |','|'+'---|'*len(h)]+['| '+' | '.join(str(v).replace('|','/').replace('\n',' ') for v in row)+' |' for row in rows])
def directories():
    yield from [(f'H00{i}',TR/f'h00{i}_20261030') for i in (7,8,9)]
    for i,name in [(10,'regla_t1_h010'),(11,'regla_reol_h011'),(12,'versiones_mu_h012'),(13,'activacion_v21_h013'),(14,'primer_t1_h014')]:
        yield f'H{i:03}',ROOT/'outputs'/f'{name}_20261030'
def periods(cat,name):
    if cat=='01':return '2007–2026, publicación de matrícula'
    if cat=='11':return '2026' if '2026' in name else '2007–2025'
    if cat=='05' and 'Oferta' in name:return '2010–2026; edición en nombre'
    if cat=='13':return 'Foto de extracción 27-10-2026'
    if cat=='07':return 'Edición archivada; cobertura de la edición según descriptor'
    if cat=='08':return 'Histórico de retención; edición según índice de archivo'
    if cat=='10':return 'Plan 20121; cobertura anual no acreditada por el nombre'
    yrs=re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',name)
    return ', '.join(dict.fromkeys(yrs))+' (nombre, provisional)' if yrs else 'E: consultar contenido o manifiesto'
def main():
    catalog=load(CLOUD/'CATALOGO_FUENTES.json');meta={}
    for r in catalog['catalogo']+catalog['catalogo_privadas']+catalog['ampliacion_matriz_20261028']['operaciones']:
        path=r.get('ruta_consolidada',r.get('destino'))
        if path:meta[unicodedata.normalize('NFC',path.split('/'+CLOUD.name+'/',1)[1])]=r
    ix=next(CLOUD.rglob('INDICE_ARCHIVO_20261026.json'))
    for item in load(ix)['archivos']:
        rel=(ix.parent/item['archivo']).relative_to(CLOUD)
        meta[unicodedata.normalize('NFC',str(rel))]=item
    evidence={}
    for tag,folder in directories():
        paths=[p for p in folder.rglob('*') if p.is_file() and p.suffix in ('.md','.py','.json') and p.stat().st_size<5_000_000]
        evidence[tag]=[(str(p.relative_to(ROOT)),p.read_text()) for p in paths]
    types={'01':'Matrícula pública agregada','02':'MU/carga institucional','03':'DATOSDEALUMNOS','04':'PROMEDIOS','05':'Oferta/duración','06':'Indicadores académicos','07':'Diccionario/capa/seguimiento privado','08':'Retención histórica','09':'Titulación','10':'Planes/homologación','11':'MRUN IPSS','12':'Titulación/carga/instructivo','13':'Permanencia'}
    rows=[];excluded=[]
    for p in sorted(CLOUD.rglob('*')):
        if not p.is_file():continue
        relative=p.relative_to(CLOUD);cat=relative.parts[0][:2]
        if p.name=='.DS_Store' or p.name.startswith('~$'):
            excluded.append(str(relative));continue
        h=sha(p);m=meta.get(unicodedata.normalize('NFC',str(relative)),{})
        if m and m.get('sha256'):assert h==m['sha256'],p.name
        typ=types.get(cat,'Catálogo/guía')
        if 'intake' in p.name.lower() or p.name.lower().startswith(('2025-2','matricula 2 y')):typ='Intake/DA'
        if p.name.startswith('5809'):typ='Precarga AC, MU 2025'
        if p.suffix=='.json' and cat not in ('07','10'):typ='Manifiesto/índice'
        direct={};mentions={}
        for tag,files in evidence.items():
            direct_refs=[f for f,s in files if h in s and any(t in Path(f).name.upper() for t in ('FUENTE','MANIFEST','INVENTARIO','PERIODOS','QA_ACTIVACION','REPRODUCCION','CANDIDATA','EVIDENCIA','CONSTRUIR'))]
            cites=[f for f,s in files if p.name in s or h in s]
            if direct_refs:direct[tag]=direct_refs
            elif cites:mentions[tag]=cites
        t2='Revisar período/corte' if cat in ('03','04') or typ.startswith('Intake') else 'No como foto'
        residual='Revisar individuo/año/expediente' if cat in ('02','03','04') else 'Apoyo de perfil' if cat in ('05','10') else 'Referencia histórica' if cat=='07' else 'Sin enlace individual admisible'
        rows.append({'ruta':str(relative),'categoria':relative.parts[0] if len(relative.parts)>1 else 'RAÍZ','tipo':typ,'bytes':p.stat().st_size,'sha256':h,'cobertura':periods(cat,p.name),'en_catalogo':bool(m),'hitos_con_hash':direct,'otras_menciones':mentions,'T2_2025':t2,'para_59':residual})
    dump(OUT/'INVENTARIO.json',{'archivos':rows,'excluidos_sistema':excluded,'metodo':'Por archivo físico. Mismo hash detecta otros emplazamientos. Referencia por hash en evidencia auditada; menciones aparte. Ausencia de referencia no demuestra que jamás se leyó.'})
    print('Inventario',len(rows),'archivos; sistema',len(excluded))
if __name__=='__main__':main()
