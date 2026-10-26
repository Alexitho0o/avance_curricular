"""Relee localizadores multiproceso. Verifica valores, no acepta su semántica temporal."""
import csv,json,re,hashlib,sys,unicodedata
from collections import defaultdict,Counter
from pathlib import Path
import openpyxl
O=Path(sys.argv[1]);P=Path(json.load(open(O/'MANIFEST.json'))['privado'])
data=json.load(open(P/'reanudacion/antecedentes_minimos.json'))
ev=next(s['rows'] for s in data if s['name']=='EVIDENCIAS_SIES')
need=defaultdict(lambda:defaultdict(lambda:defaultdict(list)))
for i,e in enumerate(ev):
    if e[4]=='COMPLETO':need[e[8]][e[9]][e[10]].append((i,e))
def val(v):return '' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip()
def norm(v):return unicodedata.normalize('NFKD',val(v)).encode('ascii','ignore').decode().upper().strip()
def ident(a,b):
    a=val(a).replace('.','').replace(' ','');b=val(b).upper()
    return str(int(a))+'-'+b if a.isdigit() and re.fullmatch('[0-9K]',b) else None
stats=[];bad=[];hashes={};verified=set()
for path,sheets in need.items():
    hashes[path]=hashlib.sha256(Path(path).read_bytes()).hexdigest();statsfile=Counter()
    if Path(path).suffix.lower()=='.xlsx':
        w=openpyxl.load_workbook(path,read_only=True,data_only=True);items=[(s,w[s].values) for s in sheets]
    else:
        raw=Path(path).read_bytes()
        try:txt=raw.decode('utf-8-sig')
        except UnicodeDecodeError:txt=raw.decode('latin1')
        try:delim=csv.Sniffer().sniff(txt[:12000],delimiters=';,\t|').delimiter
        except csv.Error:delim=';'
        items=[('CSV',csv.reader(txt.splitlines(),delimiter=delim))];w=None
    for sh,it in items:
        h=None
        for rn,row in enumerate(it,1):
            hh=[norm(v) for v in row]
            if h is None and any(z in hh for z in ['NUM_DOCUMENTO','TT_NUMERO_DOC','MM_N_DOCUMENTO','N_DOC']):h=hh;continue
            if rn not in sheets[sh]:continue
            d=dict(zip(h or [],row))
            def get(*ns):return next((d[n] for n in ns if n in d and d[n] is not None),None)
            k=ident(get('NUM_DOCUMENTO','TT_NUMERO_DOC','MM_N_DOCUMENTO','N_DOC'),get('DV','TT_DV','MM_DV'))
            for i,e in sheets[sh][rn]:
                code=val(d.get(norm(e[5]))).upper()
                if e[5]=='COMPONENTES_MU':code='I162S%sC%sJ%sV%s'%tuple(val(d.get(n)) for n in ['COD_SED','COD_CAR','JOR','VERSION'])
                ok=(k,code)==(e[0],e[3]);statsfile['localizadores']+=1;statsfile['verificados']+=ok
                if ok:verified.add(i)
                else:bad.append({'indice_evidencia':i,'archivo':path,'hoja':sh,'fila':rn,'identidad_coincide':k==e[0],'codigo_coincide':code==e[3]})
    if w:w.close()
    stats.append({'archivo':path,'sha256':hashes[path],**dict(statsfile)})
result={'estado':'OK' if len(verified)==sum(e[4]=='COMPLETO' for e in ev) else 'BLOQUEADO',
    'evidencias_completas_esperadas':sum(e[4]=='COMPLETO' for e in ev),'verificadas':len(verified),'discrepancias':len(bad),'archivos_releidos':len(need),
    'limite':'Verifica identidad y código en fila fuente; no prueba aceptación SIES ni atribución temporal de otros procesos', 'por_archivo':stats}
(O/'QA_RELECTURA_MULTIPROCESO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
(P/'DIFERENCIAS_LOCALIZADORES.json').write_text(json.dumps(bad,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='por_archivo'},ensure_ascii=False))
