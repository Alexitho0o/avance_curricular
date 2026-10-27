"""Contrasta evidencia de expedientes con listado institucional de planes."""
import collections, hashlib, json
from pathlib import Path
import openpyxl

OUT = Path(__file__).resolve().parent
source = Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Avance Curricular/2026/Listado_Planes_estudio_Sedes RE+CO.xlsx')
expected = 'fb3a6847dca0745a197867090a9d7d12e8bb7e53e6b421f96826ea0c5657d049'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
    return h.hexdigest()
def clean(v):
    if v is None:return ''
    if isinstance(v,(float,int)) and v==int(v):return str(int(v))
    return str(v).strip().upper()
assert sha(source)==expected
wb=openpyxl.load_workbook(source,read_only=True,data_only=True);ws=wb['BBDD Bruta'];it=ws.iter_rows(values_only=True)
h={clean(v):i for i,v in enumerate(next(it)) if v is not None}
assert {'CODCARR','CODPESTUD','CODRAMO','NIVEL'}.issubset(h)
catalog=collections.defaultdict(lambda:collections.defaultdict(set))
for row in it:
    def get(k):return clean(row[h[k]])
    career,plan,code,level=(get(k) for k in ('CODCARR','CODPESTUD','CODRAMO','NIVEL'))
    if all((career,plan,code)):catalog[(career,plan)][code].add(level)
wb.close();assert sha(source)==expected
data=json.loads((OUT/'MALLAS_OBSERVADAS_TITULADO_CANDIDATA.json').read_text())
tot=collections.Counter();results=[]
for p in data['planes']:
    key=(p['carrera_umas'],p['plan_de_estudio']);observed={x['codramo']:x for x in p['asignaturas']};declared=catalog.get(key)
    if declared is None:
        tot['planes_sin_llave_en_listado']+=1
        results.append({'carrera_umas':key[0],'plan':key[1],'estado':'E: carrera y plan no encontrados en listado','observadas':len(observed)})
        continue
    tot['planes_con_llave_en_listado']+=1;common=set(observed)&set(declared);miss=set(observed)-set(declared);unseen=set(declared)-set(observed)
    states=collections.Counter()
    for code in common:
        a=set(observed[code]['niveles_observados']);b=declared[code]-{''}
        if len(a)==1 and a==b:states['nivel_coincidente_unico']+=1
        elif not a or not b:states['nivel_faltante']+=1
        else:states['nivel_distinto_o_multiple']+=1
    for k,v in states.items():tot[k]+=v
    tot['asignaturas_observadas_fuera_del_listado']+=len(miss);tot['asignaturas_listadas_no_observadas']+=len(unseen)
    results.append({'carrera_umas':key[0],'plan':key[1],'listadas':len(declared),'observadas':len(observed),'ambas':len(common),'solo_observadas':len(miss),'solo_listado':len(unseen),'comparacion_nivel':dict(states),'estado':'B/C coincidencia estructural; E vigencia y completitud por plan'})
out={'clasificacion':'B listado y actividad; C cruce; E vigencia, integridad y graduación','fuentes':{'listado':{'ruta':str(source),'hoja':'BBDD Bruta','sha256':expected},'observaciones':'MALLAS_OBSERVADAS_TITULADO_CANDIDATA.json'},'llave':'CODCARR + CODPESTUD/PLAN_DE_ESTUDIO + CODRAMO; NIVEL comparado sin conversión','totales':dict(tot),'planes':results,'limitaciones':'El listado no acredita por sí mismo su vigencia histórica ni completitud. Evidencia de titulados es estado del extracto. No asigna SIES, no determina equivalencias de ramos ni modifica bases.'}
(OUT/'CONTRASTE_PLANES_AGREGADO.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out['totales'],ensure_ascii=False))
