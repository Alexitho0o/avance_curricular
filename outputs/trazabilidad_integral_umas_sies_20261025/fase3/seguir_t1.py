"""Vista longitudinal de solo lectura: orígenes T1 y diccionario activo.

Identidades solo en memoria y en una salida privada nueva fuera de Git.
No modifica libros, bases, adjudicaciones ni reglas de vigencia/retención.
"""
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse, csv, hashlib, json, os, re, subprocess, sys
import openpyxl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento, sha256

P = Path('/Users/alexi/.local/share/ipss')
ORIG = P/'aplicacion_diccionario_intertrimestral_20261023_125556/ORIGENES_T1.json'
SLOTS = P/'destinos_calendario_v7_20261023/RANURAS_POR_ORIGEN_PERIODO.json'
CTXS = P/'destinos_calendario_v7_20261023/CONTEXTOS_POR_ORIGEN_PERIODO.json'
PATTERN = re.compile(r'I(\d+)S(\d+)C(\d+)J(\d+)V(\d+)')

def load(p): return json.loads(Path(p).read_text())
def text(v): return '' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip()
def git(*args): return subprocess.check_output(['git','-C',str(ROOT),*args],text=True).strip()
def parts(code): return PATTERN.fullmatch(code).groups()
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def table(counter,fields):
    return [dict(zip(fields,k),N=v) for k,v in sorted(counter.items(),key=lambda kv:tuple(map(str,kv[0])))]
def csvout(path,rows):
    if not rows: return
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=';');w.writeheader();w.writerows(rows)
def refs(values):
    keep={'fuente','hoja','fila','ANO','PERIODO','PLAN_DE_ESTUDIO','estado_ramo','convalidado','codigo','anio','ANIO_INFORMADO','codigo_SIES_observado','ingreso_actual','ingreso_origen'}
    return [{k:v for k,v in e.items() if k in keep} for e in values]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--salida',type=Path,default=Path(__file__).parent)
    ap.add_argument('--privada',type=Path,default=P/'trazabilidad_integral_fase3_20261025')
    args=ap.parse_args();out=args.salida.resolve();private=args.privada.resolve()
    out.mkdir(parents=True,exist_ok=True)
    assert not (out/'RESULTADOS_FASE3.json').exists(), 'Usar salida nueva'
    assert private.parent.is_dir() and not private.exists()
    assert not private.is_relative_to(ROOT)
    assert subprocess.run(['git','-C',str(private.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
    before_head=git('rev-parse','HEAD');before_tracked=git('status','--short','--untracked-files=no')
    assert git('branch','--show-current')=='feature/ire-2026'
    protected=load(out.parent/'fase1/CADENA_Y_FUENTES.json')['preservacion']
    assert all(sha256(Path(p))==h for p,h in protected.items())
    sources={}
    for p,h in [(ORIG,'9ba34a21ce89170f6343e068ba38ac1a546a927c1bd5ffcab9f4fd6ef48288a0'),(SLOTS,'2b6c4772818695af0d7473c9ed3998ebad6aba5c3f62fe7cce6559e4bab2f094'),(CTXS,'82a12e4dbbd9d3ea751f2601d6b4a2f4ffe6485cb7c1f53268015169dba585ca')]:
        assert sha256(p)==h;sources[str(p)]=h
    origins=load(ORIG);oldslots=load(SLOTS);oldctx=load(CTXS)
    byorigin={o['fila_foto']:o for o in origins}
    expectedslots={(s['fila_origen_foto'],str(s['periodo_nativo'])):s for s in oldslots}
    expectedctx={(c['fila_origen_foto'],str(c['periodo_nativo']),c['observacion_id']):c for c in oldctx}
    assert len(origins)==len(byorigin)==3179 and len(expectedslots)==6358
    api=DiccionarioSiesSeguimiento(root=ROOT)
    active=load(ROOT/'data/diccionario_sies_seguimiento/activo.json')
    descriptor=ROOT/active['descriptor'];sources[str(descriptor)]=sha256(descriptor)
    sources[str(ROOT/'common/diccionario_sies_seguimiento.py')]=sha256(ROOT/'common/diccionario_sies_seguimiento.py')
    raw=[json.loads(x[0]) for x in api.db.execute('SELECT payload FROM observaciones')]
    index=defaultdict(list)
    for r in raw:index[(r['persona'],str(r['ano']),str(r['periodo']))].append(r)
    cached={}
    def query(r):
        oid=r['observacion_id']
        if oid not in cached:
            q=api.consultar(persona=r['persona'],codcli=r['CODCLI'],plan=r['plan'],anio=r['ano'],periodo=r['periodo'],carrera=r['carrera'],sede=r['sede_dimension'],jornada=r['jornada_sies'])
            assert q.get('observacion_id')==oid
            assert q['codigo_sies']==(r['codigo_documental_atribuible'] or r['codigo_interno_adoptado'] or None)
            cached[oid]=q
        return cached[oid]
    summaries={};slots=[];contexts=[];exception_rows=[];yearstates=Counter();relations=Counter();plans=Counter();originapi=Counter()
    focus_states=Counter();deltas=[];source_checks=[]
    for o in origins:
        year=int(o['anio']);dy=2025 if year==2024 else year;person=o['persona'];code0=o['codigo_origen'];p0=parts(code0)
        try:backed=code0 in api.codigos_mu(persona=person,anio=year)['codigos']
        except ValueError:backed=False
        originapi[(year,'INDICE_API' if backed else 'FUENTE_MU_LITERAL_CONSERVADA')]+=1
        base_context=index.get((person,str(year),'1'),[])
        # No CODCLI is invented: multiple candidates remain separate.
        baseline_attributed=[b for b in base_context if query(b)['codigo_sies']==code0]
        for period in ['2','3']:
            key=(year,dy,period)
            if key not in summaries:summaries[key]=Counter()
            count=summaries[key];count['ORIGENES']+=1
            obs=index.get((person,str(dy),period),[])
            slotkey=(o['fila_foto'],period)
            assert expectedslots[slotkey]['contextos']==len(obs)
            children=[]
            count['CON_CONTEXTO' if obs else 'SIN_CONTEXTO']+=1
            for r in obs:
                q=query(r);code=q['codigo_sies'];state=q['nivel_respaldo']
                old=expectedctx[(o['fila_foto'],period,r['observacion_id'])]
                # Only v8's already-approved repairs may differ from the old snapshot.
                if code != old['codigo_destino']:
                    deltas.append({'old':old['estado_destino'],'new':state,'same_origin_code':code==code0})
                assert r['persona']==person and str(r['ano'])==str(dy) and str(r['periodo'])==period
                same_codcli=[b for b in base_context if b['CODCLI']==r['CODCLI']]
                ps={b['plan'] for b in same_codcli}
                cs={b['carrera'] for b in same_codcli}
                planstatus='SIN_CONTEXTO_T1_MISMO_CODCLI' if not ps else 'VARIOS_PLANES_T1' if len(ps)>1 else 'MISMO_PLAN_OBSERVADO' if r['plan'] in ps else 'PLAN_DISTINTO_OBSERVADO'
                careerstatus='SIN_CONTEXTO_T1_MISMO_CODCLI' if not cs else 'VARIAS_CARRERAS_T1' if len(cs)>1 else 'MISMA_CARRERA_UMAS_OBSERVADA' if r['carrera'] in cs else 'CARRERA_UMAS_DISTINTA_OBSERVADA'
                changes=[]
                if code:
                    changes=[label for label,a,b in zip(['institucion','sede','carrera','jornada','version'],p0,parts(code)) if a!=b]
                relation='CODIGO_PENDIENTE' if not code else 'MISMO_CODIGO' if not changes else 'CODIGO_DISTINTO_RESPALDADO'
                context_dims=[label for label,a,b in [('sede',p0[1],str(r['sede_dimension'])),('jornada',p0[3],str(r['jornada_sies']))] if a!=b]
                flags=[]
                if changes:flags.append('CODIGO_DISTINTO')
                if not code:flags.append('CODIGO_DESTINO_PENDIENTE')
                if context_dims:flags.append('DIMENSION_OBSERVADA_DISTINTA')
                if planstatus!='MISMO_PLAN_OBSERVADO':flags.append(planstatus)
                if careerstatus in ['CARRERA_UMAS_DISTINTA_OBSERVADA','VARIAS_CARRERAS_T1']:flags.append(careerstatus)
                lineage_refs=refs(r['fuentes_promedios'])
                record={
                    'observacion_id':r['observacion_id'],'persona':person,'CODCLI':r['CODCLI'],
                    'fila_origen_foto':o['fila_foto'],'anio_origen':year,'anio_observado':dy,'periodo_nativo':period,
                    'codigo_origen_T1':code0,'codigo_destino':code,'codigo_documental_destino':q.get('codigo_documental'),
                    'codigo_interno_destino':q.get('codigo_interno'),'respaldo_destino':state,
                    'carrera_umas':r['carrera'],'sede_contexto':r['sede_dimension'],'jornada_contexto':r['jornada_sies'],'plan_destino':r['plan'],
                    'planes_T1_mismo_CODCLI':sorted(ps),'comparacion_plan':planstatus,'comparacion_carrera_umas':careerstatus,
                    'codcli_T1_atribuidos_codigo_origen':sorted({b['CODCLI'] for b in baseline_attributed}),
                    'mismo_expediente_T1_atribuido':any(b['CODCLI']==r['CODCLI'] for b in baseline_attributed),
                    'codigo_origen_respaldado_api':backed,'relacion_codigo':relation,'componentes_distintos':changes,
                    'dimensiones_contexto_distintas_origen':context_dims,'excepciones':flags,
                    'regla_existente':q.get('regla'),'pendiente_existente':q.get('pendiente'),'aceptacion_sies':q.get('aceptacion_sies'),
                    'fecha_cambio':None,'limite_fecha':'No se infiere día ni fecha administrativa del cambio; períodos de observación separados.',
                    'fuentes_promedios':lineage_refs,'fuentes_matricula':refs(r['evidencias_matricula']),
                    'fuentes_DA':[{'fuente':d.get('fuente'),'hoja':d.get('hoja'),'fila':d.get('fila'),'ANOMATRICULA':d.get('ANOMATRICULA'),'PERIODOMATRICULA':d.get('PERIODOMATRICULA'),'FECHAMATRICULA':d.get('FECHAMATRICULA')} for d in r['contextos_DA']],
                    'multiversion_origen_heredado':o['multiple'],
                }
                children.append(record);contexts.append(record)
                if flags:exception_rows.append((record,r))
                count['CONTEXTOS']+=1;count['DOCUMENTALES' if state.startswith('B/C') else 'INTERNOS_APROBADOS' if state.startswith('D_') else 'CODIGO_PENDIENTE']+=1
                # CODIGO_PENDIENTE already counted as the evidence status above.
                if relation!='CODIGO_PENDIENTE':count[relation]+=1
                if flags:count['CONTEXTOS_REVISION_EXCEPCIONES']+=1
                yearstates[(year,dy,period,state)]+=1;relations[(relation,','.join(changes),state)]+=1;plans[(planstatus,careerstatus)]+=1
                if o['multiple']:focus_states[state]+=1
            slots.append({'fila_origen_foto':o['fila_foto'],'persona':person,'documento_original':o['documento_original'],'tipo_doc':o['tipo_doc'],
                'anio_origen':year,'anio_observado':dy,'periodo_nativo':period,'codigo_origen_T1':code0,'fuente_origen':o['fuente'],
                'respaldo_origen':o['respaldo'],'codigo_origen_respaldado_api':backed,'contextos':children,
                'estado_busqueda':'CON_CONTEXTO' if children else 'SIN_CONTEXTO_EN_DICCIONARIO',
                'sin_contexto_no_equivale_desercion':not bool(children)})

    assert len(slots)==6358 and len(contexts)==2854
    assert Counter(x['respaldo_destino'] for x in contexts)=={'B/C_DOCUMENTAL_ANUAL_ATRIBUIDO':2742,'D_CORRESPONDENCIA_INTERNA_APROBADA':13,'E_PENDIENTE':99}
    assert len(deltas)==5 and all(d['old']=='E_PENDIENTE' and d['new'].startswith('B/C') and d['same_origin_code'] for d in deltas)
    assert { (x['fila_origen_foto'],x['periodo_nativo'],x['observacion_id']) for x in contexts}==set(expectedctx)
    assert all(x['codigo_origen_T1']==byorigin[x['fila_origen_foto']]['codigo_origen'] for x in slots)

    # Directed source check: read only the rows cited by exception contexts.
    requested=defaultdict(lambda:defaultdict(list))
    for record,r in exception_rows:
        for e in r['fuentes_promedios']:requested[(e['fuente'],e['hoja'])][int(e['fila'])].append((record,r,e))
    raw_checks=[];validation_errors=Counter();raw_journeys=Counter()
    for (src,sheet),rowmap in requested.items():
        path=Path(src);sources[str(path)]=sha256(path)
        w=openpyxl.load_workbook(path,read_only=True,data_only=True);ws=w[sheet];it=ws.iter_rows(values_only=True);headers=[text(x).upper() for x in next(it)]
        required=['RUT','DIG','CODCLI','CODCARR','JORNADA','PLAN_DE_ESTUDIO','ANO','PERIODO'];assert all(h in headers for h in required)
        reached=set()
        for rn,row in enumerate(it,2):
            if rn>max(rowmap):break
            if rn not in rowmap:continue
            reached.add(rn);actual=dict(zip(headers,row))
            for rec,r,e in rowmap[rn]:
                checks={
                    'CODCLI':text(actual['CODCLI'])==text(r['CODCLI']),
                    'PLAN_DE_ESTUDIO':text(actual['PLAN_DE_ESTUDIO'])==text(r['plan']),
                    'ANO':text(actual['ANO'])==text(r['ano']),
                    'PERIODO':text(actual['PERIODO'])==text(r['periodo']),
                    'RUT_ORIGINAL_EVIDENCIA':text(actual['RUT'])==text(e['RUT_original']),
                    'DV_ORIGINAL_EVIDENCIA':text(actual['DIG']).upper()==text(e['DV_original']).upper(),
                }
                for k,ok in checks.items():
                    if not ok:validation_errors[k]+=1
                raw_checks.append({'observacion_id':r['observacion_id'],'fuente':src,'hoja':sheet,'fila':rn,'checks':checks,
                    'CODCARR_original':text(actual['CODCARR']),'JORNADA_original':text(actual['JORNADA']),
                    'PLAN_DE_ESTUDIO_original':text(actual['PLAN_DE_ESTUDIO']),'ANO':text(actual['ANO']),'PERIODO':text(actual['PERIODO']),
                    'REGIMEN':text(actual.get('REGIMEN')),'NIVEL':text(actual.get('NIVEL'))})
                raw_journeys[(r['carrera'],text(actual['CODCARR']),text(actual['JORNADA']),r['sede_dimension'],r['jornada_sies'])]+=1
        w.close();assert reached==set(rowmap)
    assert not validation_errors, 'Las filas de evidencia no reproducen el contexto. Detener, sin adjudicar.'

    # Compare the same expediente across native periods without inventing a change date.
    trajectories=[];trajectory_counts=Counter()
    for o in origins:
        y=int(o['anio']);dy=2025 if y==2024 else y;person=o['persona']
        bycod=defaultdict(lambda:defaultdict(list))
        for label,yr,period in [('ORIGEN_NATIVO1',y,'1'),('DESTINO_NATIVO2',dy,'2'),('DESTINO_NATIVO3',dy,'3')]:
            for r in index.get((person,str(yr),period),[]):bycod[r['CODCLI']][label].append(r)
        for cod,groups in bycod.items():
            if not any(k.startswith('DESTINO') for k in groups):continue
            ps={k:sorted({r['plan'] for r in rr}) for k,rr in groups.items()}
            c2=set(ps.get('DESTINO_NATIVO2',[]));c3=set(ps.get('DESTINO_NATIVO3',[]))
            status='SIN_AMBOS_PERIODOS' if not c2 or not c3 else 'MULTIPLES_PLANES' if len(c2)>1 or len(c3)>1 else 'MISMO_PLAN_T2_T3' if c2==c3 else 'PLAN_DISTINTO_T2_T3'
            trajectory_counts[(y,dy,status)]+=1
            trajectories.append({'fila_origen_foto':o['fila_foto'],'persona':person,'CODCLI':cod,'anio_origen':y,'anio_observado':dy,'planes_por_periodo':ps,'comparacion_T2_T3':status})

    annual=[]
    for (y,dy,p),c in sorted(summaries.items()):
        assert c['ORIGENES']==c['CON_CONTEXTO']+c['SIN_CONTEXTO']
        assert c['CONTEXTOS']==c['DOCUMENTALES']+c['INTERNOS_APROBADOS']+c['CODIGO_PENDIENTE']
        annual.append({'COHORTE_ORIGEN':y,'ANIO_OBSERVADO':dy,'PERIODO_NATIVO':p,**dict(c),'CLASE':'B/C; internos D; pendientes E'})
    # Fixed schema even when a category is zero.
    fields=['ORIGENES','CON_CONTEXTO','SIN_CONTEXTO','CONTEXTOS','DOCUMENTALES','INTERNOS_APROBADOS','CODIGO_PENDIENTE','MISMO_CODIGO','CODIGO_DISTINTO_RESPALDADO','CONTEXTOS_REVISION_EXCEPCIONES']
    annual=[{k:r.get(k,0) for k in ['COHORTE_ORIGEN','ANIO_OBSERVADO','PERIODO_NATIVO']+fields+['CLASE']} for r in annual]
    change_counter=Counter();exception_counter=Counter();follow_counter=Counter()
    for r in contexts:
        k=(r['anio_origen'],r['anio_observado'],r['periodo_nativo'],r['codigo_origen_T1'],r['codigo_destino'] or 'Pendiente',r['carrera_umas'],r['plan_destino'],r['respaldo_destino'],','.join(r['componentes_distintos']) or r['relacion_codigo'],r['comparacion_plan'],r['comparacion_carrera_umas'])
        follow_counter[k]+=1
        if r['componentes_distintos']:change_counter[k]+=1
        if r['excepciones']:
            exception_counter[(r['anio_origen'],r['anio_observado'],r['periodo_nativo'],r['codigo_origen_T1'],r['codigo_destino'] or 'Pendiente',r['carrera_umas'],r['plan_destino'],r['respaldo_destino'],';'.join(r['excepciones']),r['comparacion_plan'],r['regla_existente'] or '',r['pendiente_existente'] or '')]+=1
    cf=['COHORTE_ORIGEN','ANIO_OBSERVADO','PERIODO_NATIVO','CODIGO_ORIGEN','CODIGO_DESTINO','CARRERA_UMAS','PLAN_DESTINO','RESPALDO','DIFERENCIA_CODIGO','COMPARACION_PLAN','COMPARACION_CARRERA_UMAS']
    ef=['COHORTE_ORIGEN','ANIO_OBSERVADO','PERIODO_NATIVO','CODIGO_ORIGEN','CODIGO_DESTINO','CARRERA_UMAS','PLAN_DESTINO','RESPALDO','MOTIVOS_REVISION','COMPARACION_PLAN','REGLA_EXISTENTE','PENDIENTE_EXISTENTE']
    csvout(out/'RESUMEN_POR_PERIODO.csv',annual)
    csvout(out/'SEGUIMIENTO_POR_CODIGO.csv',table(follow_counter,cf))
    csvout(out/'CODIGOS_DISTINTOS_RESPALDADOS.csv',table(change_counter,cf))
    csvout(out/'EXCEPCIONES_AGREGADAS.csv',table(exception_counter,ef))
    csvout(out/'PLANES_T2_T3.csv',table(trajectory_counts,['COHORTE_ORIGEN','ANIO_OBSERVADO','COMPARACION_PLANES']))

    # Verify outputs contain no identity values before writing the private detail.
    identities={r['persona'] for r in raw}|{r['CODCLI'] for r in raw}|{text(o['documento_original']) for o in origins}
    for rows in [table(follow_counter,cf),table(change_counter,cf),table(exception_counter,ef)]:
        assert not any(text(v) in identities for row in rows for v in row.values() if isinstance(v,str) and len(v)>5)
    assert git('rev-parse','HEAD')==before_head
    assert git('status','--short','--untracked-files=no')==before_tracked
    assert all(sha256(Path(p))==h for p,h in protected.items())
    assert all(sha256(Path(p))==h for p,h in sources.items())
    private.mkdir(mode=0o700)
    for name,data in [('VISTA_T1_T2_T3.json',slots),('REVISION_FILAS_PROMEDIOS.json',raw_checks),('TRAYECTORIAS_PLANES.json',trajectories)]:
        with os.fdopen(os.open(private/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:json.dump(data,f,ensure_ascii=False,indent=2)
    api.close()
    result={
        'fecha':datetime.now(ZoneInfo('America/Santiago')).isoformat(),'fase':'3/6','clasificacion':'B/C/D/E','estado':'SEGUIMIENTO_REPRODUCIDO_CON_EXCEPCIONES_VISIBLES',
        'diccionario':{'edicion':api.edicion,'descriptor':active['descriptor'],'sha256':active['sha256']},
        'origenes':3179,'poblaciones_conservadas':dict(Counter(o['anio'] for o in origins)),
        'posiciones':len(slots),'con_contexto':sum(bool(x['contextos']) for x in slots),'sin_contexto':sum(not x['contextos'] for x in slots),
        'contextos':len(contexts),'contextos_estado':dict(Counter(x['respaldo_destino'] for x in contexts)),
        'relacion_codigo':dict(Counter(x['relacion_codigo'] for x in contexts)),
        'foco_multiversion_heredado':dict(focus_states),'resumen_periodo':annual,
        'comparacion_planes':table(plans,['PLAN_T1_DESTINO','CARRERA_UMAS_T1_DESTINO']),
        'planes_T2_T3':table(trajectory_counts,['COHORTE_ORIGEN','ANIO_OBSERVADO','RESULTADO']),
        'anclas_API':table(originapi,['COHORTE','RESPALDO']),
        'revision_excepciones':{'contextos':len(exception_rows),'filas_PM_distintas':sum(len(v) for v in requested.values()),'verificaciones_fila_contexto':len(raw_checks),'diferencias':dict(validation_errors),'codigos_distintos':sum(change_counter.values()),'codigos_distintos_respaldos':dict(Counter(r['respaldo_destino'] for r in contexts if r['componentes_distintos']))},
        'cambios_vs_instantanea_v7':{'contextos':len(deltas),'descripcion':'Cinco reparaciones documentales ya aprobadas en v8; no cierres nuevos de esta fase.'},
        'qa':{'estado':'PASA_TECNICO_CON_LIMITES','origenes_preservados':True,'posiciones_preservadas':True,'contextos_preservados':True,'fuentes_preservadas':True,'duplicados_posicion':0,'identidades_exportadas_agregados':False,'nuevas_adjudicaciones':0,'bases_y_denominadores_modificados':False,'recalculo_excel':False},
        'fuentes_sha256':sources,'privado':{'ruta':str(private),'fuera_git_verificado':True,'archivos':{p.name:sha256(p) for p in private.iterdir()}},
        'git':{'rama':git('branch','--show-current'),'HEAD_antes':before_head,'HEAD_despues':git('rev-parse','HEAD'),'tracked_preexistente':before_tracked,'commit':False,'push':False},
        'limites_E':['Ausencia de contexto no acredita abandono ni ausencia en foto de matrícula.','Comparación de plan requiere contexto nativo1 del mismo CODCLI; no se infiere cuando falta.','Otra carrera/CODCLI puede ser matrícula adicional; no se impone una transición personal.','Las dimensiones DA observadas pueden ser posteriores al período académico. Se conservan las adjudicaciones históricas delimitadas.','No se homologa automáticamente período nativo con trimestre/cierre. Calendario aprobado preservado.','No se acredita aceptación SIES ni fecha administrativa del cambio.'],
    }
    write(out/'RESULTADOS_FASE3.json',result)
    print(json.dumps({k:result[k] for k in ['estado','origenes','posiciones','con_contexto','sin_contexto','contextos_estado','relacion_codigo','revision_excepciones','anclas_API','planes_T2_T3']},ensure_ascii=False))

if __name__=='__main__':main()
