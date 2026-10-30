"""QA acotado H007: sumas, preservación, privacidad y reproducción."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,subprocess,sys
sys.dont_write_bytecode=True
from reanclar import txt
OUT=Path(__file__).parent;ROOT=OUT.parents[2];BASE=OUT.parent;P=Path.home()/'.local/share/ipss'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],text=True)

def main():
    initial=read(P/'h007_20261030/ANTES.json');a=read(OUT/'POSICIONES_SIN_CONTEXTO.json');b=read(OUT/'REEVALUACION_99.json');c=read(OUT/'MRUN_AGREGADO.json');d=read(OUT/'ESCENARIO_131_H001.json')
    check={}
    check['documento_y_DV_cero_no_vacio']=txt(0)=='0' and txt(0.0)=='0' and txt(None)==''
    check['posiciones_particion_3520']=sum(x['n'] for x in a['clasificacion'])==3520
    old=read(BASE/'fase3/RESULTADOS_FASE3.json')['resumen_periodo'];sums=Counter()
    for x in a['clasificacion']:sums[(x['cohorte_T1'],x['anio_observado'],x['periodo_nativo'])]+=x['n']
    check['seis_totales_igual_fase3']=all(sums[(r['COHORTE_ORIGEN'],r['ANIO_OBSERVADO'],str(r['PERIODO_NATIVO']))]==r['SIN_CONTEXTO'] for r in old)
    check['99_particion_casos']=sum(x['n'] for x in b['casos_agrupados'])==99 and sum(x['n'] for x in b['resumen'])==99
    check['63_y_36_conservados']=sum(x['n'] for x in b['resumen'] if x['motivo_v24']=='JORNADA_DISTINTA')==63 and sum(x['n'] for x in b['resumen'] if x['motivo_v24']=='SIN_ENLACE_EXPEDIENTE_T1')==36
    check['sin_nueva_herencia']=b['pasan_a_respaldados_personales']==0 and not b['nueva_herencia']
    check['MRUN_diferencias_y_sin_par']=all((x['diferencia_observado_menos_referencia'] is None and x['estado']=='SIN_PAR') if x['referencia_personas_MRUN'] is None or x['observado_personas_MU_seleccionada'] is None else x['diferencia_observado_menos_referencia']==x['observado_personas_MU_seleccionada']-x['referencia_personas_MRUN'] for x in c['por_codigo'])
    check['H001_558_326_sin_recalculo']=d['H001_preservado']=={'casos':558,'retenidos':326,'personas_h001_localizadas_en_MU_2024':558,'personas_distintas_en_los_131':131}
    check['131_origen_explicado']=sum(x['n'] for x in d['cohorte_origen_131'])==131 and all(x['anio_origen']!=2024 for x in d['cohorte_origen_131']) and d['en_cohorte_H001']==0
    check['v1_conservada']=sha(BASE/'PLAN_FASES_HITOS_v1_20261025.md')==initial['hashes'][str((BASE/'PLAN_FASES_HITOS.md').relative_to(ROOT))]
    allowed={'docs/MAPA_RESULTADOS_GOBERNADOS.md','docs/MAPA_RESULTADOS_GOBERNADOS.json',str((BASE/'PLAN_FASES_HITOS.md').relative_to(ROOT))}
    altered=[p for p,h in initial['hashes'].items() if p not in allowed and sha(ROOT/p)!=h]
    check['otros_tracked_intactos']=not altered
    nowstatus=git('status','--porcelain').splitlines()
    check['cambios_preexistentes_fuera_stage']=all(s in nowstatus for s in initial['status'].splitlines())
    check['HEAD_intacto']=git('rev-parse','HEAD').strip()==initial['head']
    check['stage_vacio']=not git('diff','--cached','--name-only').strip()
    beforemap=json.loads(git('show',initial['head']+':docs/MAPA_RESULTADOS_GOBERNADOS.json'))
    aftermap=read(ROOT/'docs/MAPA_RESULTADOS_GOBERNADOS.json')
    check['R01_R24_iguales']=aftermap['resultados'][:24]==beforemap['resultados'] and len(aftermap['resultados'])==25
    src=read(OUT/'FUENTES_H007.json')['fuentes']
    check['fuentes_no_alteradas']=all(sha(Path(x['ruta']))==x['sha256'] for x in src)
    # Reproducción solo del diagnóstico nuevo; no pipelines cerrados.
    outputs=[p for p in OUT.iterdir() if p.suffix in ('.json','.md') and p.name not in ('QA_H007.json','MANIFEST_H007.json')]
    hashes={str(p):sha(p) for p in outputs}
    for script in ['reanclar.py','documentar.py']:
        run=subprocess.run([sys.executable,str(OUT/script)],cwd=ROOT,capture_output=True,text=True)
        if run.returncode:raise RuntimeError(run.stderr)
    check['reproduccion_identica']=all(sha(Path(p))==h for p,h in hashes.items())
    # Identificadores conocidos en memoria: búsqueda literal por token completo;
    # evita confundirlos con hashes y códigos de catálogo.
    slots=read(P/'trazabilidad_integral_fase3_20261025/VISTA_T1_T2_T3.json')
    ids=set()
    for slot in slots:
        ids.update([txt(slot['persona']),txt(slot['documento_original'])])
        for ctx in slot['contextos']:ids.update([txt(ctx['persona']),txt(ctx['CODCLI'])])
    ids={v for v in ids if len(v)>=6}
    known=re.compile(r'(?<![\w])(?:'+'|'.join(re.escape(v) for v in sorted(ids,key=len,reverse=True))+r')(?![\w])')
    patterns=[re.compile(r'(?<![\w])\d{7,8}-[0-9Kk](?![\w])'),re.compile(r'\b\d{1,2}\.\d{3}\.\d{3}-[0-9Kk]\b'),re.compile(r'(?i)"(?:mrun|rut|CODCLI|N_DOC)"\s*:\s*"?\d+'),re.compile(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}')]
    files=list(OUT.glob('*.py'))+list(OUT.glob('*.md'))+[p for p in OUT.glob('*.json') if p.name not in ('QA_H007.json','MANIFEST_H007.json')]+[BASE/'DELTA_H007.md',BASE/'PLAN_FASES_HITOS.md',BASE/'PLAN_FASES_HITOS_v1_20261025.md']+[ROOT/p for p in allowed if p.startswith('docs/')]
    findings=[]
    for p in files:
        text=p.read_text()
        if known.search(text) or any(q.search(text) for q in patterns):findings.append(str(p.relative_to(ROOT)))
    check['escaneo_identificadores_sin_hallazgos']=not findings
    result={'estado':'PASS' if all(check.values()) else 'FAIL','controles':check,'archivos_con_hallazgos_sin_valores':findings,'archivos_ajenos_alterados':altered,'head':initial['head'],'commit':False,'push':False,'clase':'C: QA de H007; no prueba nueva de tasas, vigencia ni identidad MRUN','limite_privacidad':'Patrones de documentos/contactos y cotejo literal contra identidades del universo privado; revisión de esquema agregado. No se incluyen valores individuales.'}
    (OUT/'QA_H007.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    paths=files+[OUT/'QA_H007.json']
    manifest={'hito':'H007','estado':result['estado'],'fuentes':'FUENTES_H007.json','salidas':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))},'version_plan':2,'version_anterior_sha256':sha(BASE/'PLAN_FASES_HITOS_v1_20261025.md'),'base_commit':initial['head'],'nuevas_adjudicaciones':0,'sin_commit_push':True}
    (OUT/'MANIFEST_H007.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    assert all(check.values())
if __name__=='__main__':main()
