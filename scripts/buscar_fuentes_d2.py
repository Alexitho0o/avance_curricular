#!/usr/bin/env python3
"""Búsqueda acotada por nombres; no confunde localización con lectura de evidencia."""
import json,re,subprocess,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/cierre_d2/20261016'
def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if not unicodedata.combining(c))
def main():
    cloud=next(p for p in Path('/Users/alexi/Library/CloudStorage').iterdir() if p.name.startswith('OneDrive-InstitutoProfesional'))
    dirs=[ROOT,ROOT.parent/'CARACTERIZACIÓN',Path('/Users/alexi/Downloads')]
    for pattern in ('0 BASES DE DATOS/OFERTA*','Datos DAI (RAW)*/1.2.1 Datos Institucionales/1.2.1.1 SIES','2025/SIES/AVANCE CURRICULAR'):
        dirs.extend(cloud.glob(pattern))
    candidates=[];logs=[]
    for d in dirs:
        proc=subprocess.run(['rg','--files','--hidden','-g','!.git','-g','!node_modules','-g','!.venv','-g','!venv',str(d)],capture_output=True,text=True)
        names=proc.stdout.splitlines();hits=0
        for path in names:
            p=Path(path);n=norm(p.name);cats=[]
            if 'oferta' in n and re.search(r'200[789]',n):cats.append('OFERTA_2007_2009_CANDIDATA')
            if re.search('datos.*alumno|promedio.*alumno',n) and p.suffix.lower() in ('.xlsx','.csv','.zip'):cats.append('EXTRACTO_UMAS_LOCALIZADO')
            if re.search('malla|plan.*estudio|resolucion|decreto|catalogo.*curricular',n) and p.suffix.lower() in ('.xlsx','.csv','.pdf','.docx','.json'):cats.append('DOCUMENTO_CURRICULAR_CANDIDATO')
            if re.search('202[3456]',n) and re.search('mat_ip|matricula|unificada|mu202',n) and p.suffix.lower() in ('.xlsx','.csv'):cats.append('MATRICULA_RECIENTE_CANDIDATA')
            if cats:
                hits+=1;candidates.append({'path':path,'categorias':cats,'estado':'LOCALIZADO_POR_NOMBRE_CONTENIDO_NO_VERIFICADO'})
        logs.append({'directorio':str(d),'archivos_listados':len(names),'candidatos':hits,'salida_rg':proc.returncode,'errores':proc.stderr[:2000]})
    unique={x['path']:x for x in candidates}
    out={'alcance':logs,'candidatos':list(unique.values()),'limite':'Solo búsqueda de nombres en directorios indicados; no acredita inexistencia en otras ubicaciones ni contenido de archivos nube.'}
    (OUT/'busqueda_fuentes.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'directorios':len(logs),'archivos':sum(x['archivos_listados'] for x in logs),'candidatos':len(unique)},ensure_ascii=False))
    for x in unique.values():
        if 'OFERTA_2007_2009_CANDIDATA' in x['categorias'] or ('DOCUMENTO_CURRICULAR_CANDIDATO' in x['categorias'] and '/data/' not in x['path']):print(x['path'])
if __name__=='__main__':main()
