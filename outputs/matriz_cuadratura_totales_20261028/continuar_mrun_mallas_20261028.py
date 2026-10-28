"""Hitos 2–3: agregados reproducibles, sin vínculos RUT–MRUN persistidos."""
import collections,csv,datetime,hashlib,json,re,sqlite3,sys
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(OUT))
from metodo_mu2026 import diagnosticar_inverso_mrun,codigos_con_diferencia,_text

def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def verify(p,h):
    assert sha(p)==h,'Fuente modificada';return Path(p)
def rows(p,sheet=None):
    w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=(w[sheet] if sheet else w.worksheets[0]).iter_rows(values_only=True);h=next(it);rr=[dict(zip(h,r)) for r in it if any(v is not None for v in r)];w.close();return rr
def write(name,x):
    (OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
    cat=read(ROOT/'data/catalogo_fuentes/CATALOGO_FUENTES.json');source=read(OUT/'FUENTE_MRUN2026_Y_LIMPIEZA.json');mref=source['fuente_consolidada']
    mr=verify(mref['ruta_consolidada'],mref['sha256'])
    bref=next(x for x in cat['catalogo'] if x['sha256']=='19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd');base=verify(bref['ruta_consolidada'],bref['sha256'])
    gp=verify(ROOT/'data/versiones_por_cohorte/20261028/grupos_existentes.json','fe8837a760d4ed132505bf92138145e08adb3ce0a2486c9e3f26f08ca11babfc');groups=read(gp)
    mu=[r for r in rows(base,'BASE_RETENCION_MU') if _text(r['ANIO_INFORMADO'])=='2026']
    with mr.open(newline='') as f:mrun=list(csv.DictReader(f))
    focus=codigos_con_diferencia();inv=diagnosticar_inverso_mrun(mrun,mu,groups,focus);s=inv['resumen'];assert s['vig1_foco']==2747 and s['sin_candidato_C']==240
    # SQL independiente: normalización de fechas explícita y JOIN existencial;
    # índices efímeros, ninguna relación personal se escribe a disco.
    db=sqlite3.connect(':memory:');db.execute('PRAGMA temp_store=MEMORY');db.execute('CREATE TABLE mu(i,ym,sx,fam,vig,c)');db.execute('CREATE TABLE mr(i,ym,sx,fam,typ,expected,c)')
    types=collections.defaultdict(set);missing=set();names={'1':'PLAN REGULAR','2':'PLAN ESPECIAL','3':'PLAN REGULAR DE CONTINUIDAD'}
    for g in groups:
        for f in g['familias']:
            ts={_text(p[1]) for p in g.get('perfiles_duracion_tipo',[])};types[f].update(ts)
            if not ts:missing.add(f)
    expected={f:names[next(iter(v))] for f,v in types.items() if len(v)==1 and f not in missing and next(iter(v)) in names}
    for i,r in enumerate(mu):
        try:d=datetime.datetime.strptime(_text(r['FECH_NAC']),'%d/%m/%Y');ym=d.strftime('%Y%m') if d.year>1900 else None
        except ValueError:ym=None
        c='I162S{}C{}J{}V{}'.format(*(_text(r[k]) for k in ('COD_SED','COD_CAR','JOR','VERSION')))
        sx=_text(r['SEXO']);db.execute('INSERT INTO mu VALUES(?,?,?,?,?,?)',(i,ym if sx in ('H','M') else None,sx,c.rsplit('V',1)[0],_text(r['VIG']),c))
    for i,r in enumerate(mrun):
        ym=_text(r['fec_nac_alu']);ym=ym if re.fullmatch(r'\d{6}',ym) and 1900<int(ym[:4])<=2026 and 1<=int(ym[4:])<=12 else None
        c=_text(r['codigo_unico']);fam=c.rsplit('V',1)[0];db.execute('INSERT INTO mr VALUES(?,?,?,?,?,?,?)',(i,ym,{'1':'H','2':'M'}.get(_text(r['gen_alu'])),fam,_text(r['tipo_plan_carr']),expected.get(fam),c))
    cond='mr.ym=mu.ym AND mr.sx=mu.sx AND mr.fam=mu.fam AND (mr.expected IS NULL OR mr.expected=mr.typ)'
    sql={c:(n,covered) for c,n,covered in db.execute('SELECT mu.c,COUNT(*),SUM(EXISTS(SELECT 1 FROM mr WHERE '+cond+')) FROM mu WHERE mu.vig="1" GROUP BY mu.c')}
    for r in inv['inversa_por_codigo']:
        n,covered=sql.get(r['codigo_sies'],(0,0));assert n==r['vig1_nuestra'] and covered==r['todo_IPSS']['C']['con_candidato']
    residual=db.execute('SELECT mr.c,EXISTS(SELECT 1 FROM mu WHERE mr.ym=mu.ym AND mr.sx=mu.sx),EXISTS(SELECT 1 FROM mu WHERE mr.ym=mu.ym AND mr.sx=mu.sx AND mr.fam=mu.fam) FROM mr WHERE NOT EXISTS(SELECT 1 FROM mu WHERE '+cond+')').fetchall()
    cnt=collections.Counter()
    for c,has_a,has_b in residual:
        if c in focus:cnt['sin_candidato_C']+=1;cnt['con_candidato_A' if has_a else 'sin_candidato_A']+=1
    assert all(cnt[k]==s[k] for k in ('sin_candidato_C','con_candidato_A','sin_candidato_A'));db.close()
    inv['fuentes']=[{'ruta':str(p),'sha256':sha(p)} for p in (base,mr,gp,OUT/'metodo_mu2026.py',Path(__file__))];inv['qa_sql_independiente']={'diferencias':0,'inversa_codigos':48,'residual_registros':240}
    write('PRUEBA_INVERSA_MRUN2026.json',inv)
    lines=['# Prueba inversa de la brecha MU2026 [C/E]','','Se reutilizan los bloqueos A/B/C del 16-10. No se certifican identidades ni se guardan vínculos RUT–MRUN.','','## Resultados','','| Universo | Con candidato C | Sin candidato C |','|---|---:|---:|']
    for scope in ('todo_IPSS','solo_48_codigos'):
        v=s['inversa'][scope]['C'];lines.append(f"| 2.747 VIG1 contra {scope} | {v['con_candidato']} | {v['sin_candidato']} |")
    lines+=['',f"De los 240 MRUN sin candidato C: {s['con_candidato_A']} encuentran perfil A en nuestra MU y {s['sin_candidato_A']} no. Con perfil A: {s['A_solo_otra_familia']} sólo otra familia, {s['A_misma_y_otra_familia']} misma y otra, {s['A_solo_misma_familia']} sólo la misma. VIG de candidatos: {s['A_solo_vig1']} sólo VIG1; {s['A_solo_vig0']} sólo VIG0; {s['A_mixto_vig0_vig1']} mixtos.",'',inv['dictamen'],'','Los soportes origen/destino del JSON no son sumables entre destinos: un registro puede tener varios perfiles candidatos.','', '## Inversa por código','','| Código | VIG1 nuestra | Sin candidato C en todo IPSS | Sin candidato C en foco |','|---|---:|---:|---:|']
    for v in inv['inversa_por_codigo']:lines.append(f"| {v['codigo_sies']} | {v['vig1_nuestra']} | {v['todo_IPSS']['C']['sin_candidato']} | {v['solo_48_codigos']['C']['sin_candidato']} |")
    lines+=['','QA: SQL independiente, cero diferencias. Desglose completo de los 240 y sus soportes por código/VIG en el JSON. Bases, tasas y denominadores intactos.']
    (OUT/'PRUEBA_INVERSA_MRUN2026.md').write_text('\n'.join(lines)+'\n')
    # Mallas: verificar fuentes existentes; no atribuir un plan individual.
    refs=read(ROOT/'outputs/avance_historico_fase3_20261027/MANIFEST.json')['fuentes'];per=next(v for v in cat['catalogo'] if v['archivo']=='Permanencia.xlsx');pp=verify(per['ruta_consolidada'],per['sha256']);pr=rows(pp)
    lr=rows(verify(refs['listado']['ruta'],refs['listado']['sha256']),'BBDD Bruta')
    hr=rows(verify(refs['h112a']['ruta'],refs['h112a']['sha256']),'05_FUENTE_DETALLE_ASIGNATURAS')
    h112b=verify(refs['h112b_excel']['ruta'],refs['h112b_excel']['sha256']);loads=rows(h112b,'03_CARGA_SIES_16769_21C');maps={_text(r['CODIGO_UNICO']):r for r in rows(h112b,'02_H112A_HOJA10')}
    result=[]
    for career in ('ADMP','AUDT','ICDA'):
        pe=[r for r in pr if r['CARRERA_ALUM']==career];plan=career+'20251';catalog={_text(r['CODRAMO']) for r in lr if _text(r['CODPESTUD'])==plan};detail={_text(r['CODRAMO']) for r in hr if _text(r['CODPESTUD'])==plan}
        names_title=collections.Counter();outside=collections.Counter();covered=0
        for r in pe:
            items={m[1]:m[2].strip() for part in str(r['LISTA_RAMOS_PEND']).split(' / ') if (m:=re.match(r'^\s*([A-Za-z0-9_]+)-(.+)',part))}
            title={c:n for c,n in items.items() if 'TITULO INTERMEDIO' in n.upper() or 'TÍTULO INTERMEDIO' in n.upper()}
            for c,n in title.items():names_title[c,n]+=1
            for c in items.keys()-catalog:outside[c]+=1
            covered+=len(title)==2
        codes=[_text(r['CODIGO_UNICO']) for r in loads if _text(maps[_text(r['CODIGO_UNICO'])]['CODPESTUD'])==plan]
        totals={int(r['TOTAL_UNIDADES_MEDIDA']) for r in loads if _text(r['CODIGO_UNICO']) in codes};pt={int(r['TOTAL_RAMOS_MALLA']) for r in pe};title_codes={c for c,n in names_title}
        consistent=(len(title_codes)==2 and covered==len(pe) and len(catalog)==next(iter(totals)) and pt=={next(iter(totals))+2} and not title_codes & catalog and not title_codes & detail and set(outside)==title_codes)
        result.append({'carrera_umas':career,'plan_referencia':plan,'codigos_sies_referencia':codes,'expedientes':len(pe),'total_permanencia':sorted(pt),'total_5810':sorted(totals),'ramos_catalogo':len(catalog),'ramos_detalle_H112':len(detail),'titulos_intermedios':[{'codigo':c,'nombre':n,'expedientes_con_codigo':nobs} for (c,n),nobs in sorted(names_title.items())],'codigos_pendientes_fuera_catalogo':[{'codigo':c,'expedientes':n} for c,n in sorted(outside.items())],'expedientes_con_ambos_items':covered,'criterio_contable_compatible':consistent,'clase':'B/C compatibilidad contable; E fórmula exportadora y plan individual no acreditados','dictamen':'Los dos ítems TITLE INTERMEDIO observados en todas las listas son los únicos códigos de esas listas fuera de la malla; el total de Permanencia coincide con 5810 más esos dos. No se acredita la consulta exportadora ni plan personal.' if consistent else 'E: la diferencia no queda explicada íntegramente por los ítems de título intermedio.'})
    mallas={'fecha':'2026-10-28','clase':'B/C/E','por_carrera':result,'fuentes':[{'ruta':str(p),'sha256':sha(p)} for p in (pp,Path(refs['listado']['ruta']),Path(refs['h112a']['ruta']),h112b)],'limites':['Permanencia no contiene plan; no se atribuye el plan de cada expediente.','5810 proceso2026 datos2025 frente a foto Permanencia octubre2026; no se corrige ninguna unidad ni base.','LISTA_RAMOS_PEND tiene límite800; su ausencia no prueba exclusión. Aquí sólo se usa presencia positiva de códigos.','La fórmula de TOTAL_RAMOS_MALLA no se ha localizado: compatibilidad contable, no prueba del algoritmo exportador.']}
    write('MALLAS_TITULO_INTERMEDIO_MRUN2026.json',mallas)
    ll=['# Mallas y título intermedio [B/C/E]','','| Carrera | Expedientes | Permanencia | 5810 | Dos ítems presentes | Compatibilidad contable |','|---|---:|---:|---:|---:|---|']
    for v in result:ll.append(f"| {v['carrera_umas']} | {v['expedientes']} | {v['total_permanencia']} | {v['total_5810']} | {v['expedientes_con_ambos_items']} | {v['criterio_contable_compatible']} |")
    for v in result:ll+=['',v['carrera_umas']+': '+', '.join(t['codigo']+' — '+t['nombre'] for t in v['titulos_intermedios'])+'. '+v['dictamen']]
    ll+=['',*mallas['limites']];(OUT/'MALLAS_TITULO_INTERMEDIO_MRUN2026.md').write_text('\n'.join(ll)+'\n')
    write('QA_HITOS_1_A_3_MRUN2026.json',{'estado':'PASS_CON_PENDIENTES_E','inversa_SQL_diferencias':0,'vig1_foco':2747,'residual':240,'mallas_carreras':3,'mallas_compatibles':sum(v['criterio_contable_compatible'] for v in result),'bases_verificadas_por_hash':True,'vinculos_personales_persistidos':False,'borrado_externo_confirmado':not Path('/Users/alexi/.local/share/ipss/v10_candidata_31_20261026').exists(),'salidas':[{'archivo':n,'sha256':sha(OUT/n)} for n in ('PRUEBA_INVERSA_MRUN2026.json','PRUEBA_INVERSA_MRUN2026.md','MALLAS_TITULO_INTERMEDIO_MRUN2026.json','MALLAS_TITULO_INTERMEDIO_MRUN2026.md')]})
    print(json.dumps({'inversa':s,'mallas':[{'carrera':v['carrera_umas'],'compatible':v['criterio_contable_compatible'],'fuera_catalogo':v['codigos_pendientes_fuera_catalogo']} for v in result]},ensure_ascii=False))
if __name__=='__main__':main()
