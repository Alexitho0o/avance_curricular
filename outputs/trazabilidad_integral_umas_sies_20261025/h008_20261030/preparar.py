"""H008: complementos de contexto; no cambia vigencia, herencia ni denominadores.

Las rutas sensibles se reciben en un JSON privado. Solo el suplemento y la
auditoría individual se escriben en el directorio privado proporcionado.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse, hashlib, json, sqlite3
import openpyxl

def sha(p):
    with Path(p).open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def load(p): return json.loads(Path(p).read_text())
def write(p, obj): Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def txt(v):
    return '' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip()
def table(rows, cols):
    return '\n'.join(['| '+' | '.join(cols)+' |','|'+'|'.join(['---']*len(cols))+'|']+['| '+' | '.join(str(r.get(c,'')) for c in cols)+' |' for r in rows])
def prepare(config, private, out):
    cfg=load(config); private=Path(private);out=Path(out)
    private.mkdir(parents=True,exist_ok=True,mode=0o700);out.mkdir(parents=True,exist_ok=True)
    for key,e in cfg['entradas'].items():
        assert sha(e['ruta'])==e['sha256'], 'Fuente alterada: '+key
    source=lambda key:cfg['entradas'][key]['ruta']
    slots=load(source('slots'));old=load(source('posiciones_h007'))
    c1={(r['fila_vista_origen'],r['periodo']) for r in old if r['causa']=='CONTEXTO_PRESENTE_EN_V20_AUSENTE_EN_INSTANTANEA_V8'}
    assert len(c1)==1135
    db=sqlite3.connect('file:'+source('base_v20')+'?mode=ro',uri=True);idx=defaultdict(list)
    for (payload,) in db.execute('select payload from observaciones'):
        r=json.loads(payload);idx[(r['persona'],txt(r['ano']),txt(r['periodo']))].append(r)
    db.close()
    rows=[];keys=[];details=[];counts=Counter();groups=Counter()
    for s in slots:
        for c in s['contextos'] if s['contextos'] else [None]:
            keys.append([int(s['anio_origen']),int(s['anio_observado']),int(s['periodo_nativo'])])
            eligible=c is None and (s['fila_origen_foto'],s['periodo_nativo']) in c1
            rr=idx[(s['persona'],txt(s['anio_observado']),s['periodo_nativo'])] if eligible else []
            doc=sorted({x['codigo_documental_atribuible'] for x in rr if x['codigo_documental_atribuible']})
            internal=sorted({x['codigo_interno_adoptado'] for x in rr if x['codigo_interno_adoptado']})
            rows.append([int(eligible),len(rr),'; '.join(doc),'; '.join(internal),'; '.join(sorted({x['plan'] for x in rr})),
                'B/C contexto v20; no acredita expediente T1 ni vigencia' if eligible else 'Sin integración C1 en esta fila',
                'NO ACREDITADO' if eligible else 'NO MODIFICADO',
                'Sin efecto en Q/R de la foto ni en tasas R19',
                '; '.join(sorted({str(x['observacion_id']) for x in rr}))])
            if eligible:
                assert rr
                counts[(s['anio_origen'],s['anio_observado'],s['periodo_nativo'])]+=1
                details.append({'fila_v25':len(rows)+5,'fila_foto':s['fila_origen_foto'],'observaciones':rr})
                for x in rr:groups[(txt(s['anio_observado']),s['periodo_nativo'],x['clasificacion'])]+=1
    assert len(rows)==6374 and sum(r[0] for r in rows)==1135
    headers=['Posición C1 integrada v20 (1/0)','Contextos v20 de la posición','Código documental v20 (contexto)','Correspondencia interna v20 (contexto)','Planes observados v20','Respaldo de contexto','Mismo expediente T1','Límite para vigencia y tasa','Referencias de observación v20']
    write(private/'payload.json',{'headers':headers,'rows':rows,'keys':keys,'resumen':[list(k)+[v] for k,v in sorted(counts.items())]})
    write(private/'DETALLE_C1_PRIVADO.json',details)
    write(out/'INTEGRACION_C1.json',{'clase':'B/C; aprobación de contexto interno D previa, no nueva adjudicación','posiciones':1135,'contextos':sum(r[1] for r in rows),'filas_vista':6374,'por_periodo':[{'cohorte':k[0],'anio_observado':k[1],'periodo':k[2],'posiciones':v} for k,v in sorted(counts.items())],'por_clase_contexto':[{'anio':k[0],'periodo':k[1],'clase_v20':k[2],'contextos':v} for k,v in sorted(groups.items())],'efecto_tasas_R19':0,'nuevas_atribuciones':0,'limite':'AG:AO complementa las posiciones sin contexto de la instantánea v8; no reemplaza N/AC, no presume expediente T1 y no cambia la foto de vigencia. Los conteos originales siguen identificados como instantánea v8.'})
    # Cobertura de los candidatos contra el padrón ya congelado; no crea una foto.
    def norm(v): return txt(v).replace('.','').replace(' ','').upper()
    def key_r19(v):
        body=norm(v).split('-')[0]
        return str(int(body)) if body.isdigit() else body
    cohorts=defaultdict(set)
    for s in slots:cohorts[s['anio_origen']].add(norm(s['documento_original']))
    inventories=[];photo_index={}
    equivalents=load(source('reglas_estado'))['equivalencias']
    states_rule={(txt(x['estado_umas']).upper(),txt(x['situacion_umas']).upper()):txt(x['resultado']) for x in equivalents}
    for e in cfg['fotos']:
        p=Path(e['ruta']);h=sha(p);w=openpyxl.load_workbook(p,read_only=True,data_only=True);ws=w[e['hoja']]
        it=ws.iter_rows(values_only=True);hd=[txt(v).upper() for v in next(it)];n=0;keys=set();years=Counter();states=Counter();lookup=defaultdict(list)
        for row in it:
            if not any(v is not None for v in row):continue
            n+=1
            def g(k):return row[hd.index(k)] if k in hd and hd.index(k)<len(row) else None
            if 'RUT' in hd:keys.add(norm(g('RUT')))
            years[txt(g('ANOINGRESO'))]+=1
            states[txt(g('ESTADOACADEMICO'))]+=1
            if 'RUT' in hd:
                value=states_rule.get((txt(g('ESTADOACADEMICO')).upper(),txt(g('SITUACION')).upper()),'SIN REGLA')
                lookup[(key_r19(g('RUT')),txt(g('ANOINGRESO')))].append(value)
        w.close()
        inventories.append({**e,'sha256':h,'filas':n,'columnas':len(hd),'cobertura_documento_literal_T1':[{'cohorte':y,'coincidencias':len(v&keys),'universo':len(v)} for y,v in sorted(cohorts.items())],
            'anios_ingreso':[{'anio':y,'filas':v} for y,v in sorted(years.items())], 'estado_academico_disponible':'ESTADOACADEMICO' in hd,
            'limite_cobertura':'Igualdad literal normalizada del documento; ausencia no significa no matrícula. No se usa para adjudicar ni calcular tasas.'})
        if e.get('completa_para'):
            photo_index[tuple(e['completa_para'])]=(lookup,p.name,h)
    write(out/'FUENTES_FOTOS_H008.json',inventories)
    # Fotos completas: misma selección de ingreso/prioridad de R19, como respaldo
    # separado. Los proxies aprobados no se sustituyen por una foto sin decisión.
    payload=load(private/'payload.json');photo_counts=Counter();photo_rows=[]
    rank={'1':1,'NO APLICA':2,'PENDIENTE':3,'0':4,'SIN REGLA':5}
    labels={'1':'VIG 1','0':'VIG 0','NO APLICA':'NO APLICA','PENDIENTE':'PENDIENTE','SIN REGLA':'SIN REGLA'}
    for s in slots:
        key=(int(s['anio_observado']),int(s['periodo_nativo']));photo=photo_index.get(key)
        vals=photo[0].get((key_r19(s['documento_original']),txt(s['anio_origen'])),[]) if photo else []
        state=labels[min(vals,key=lambda v:rank[v])] if vals else 'Sin matrícula de ingreso en el corte' if photo else 'Sin foto completa'
        row=[state,photo[1] if photo else 'E: falta foto completa',f"Cierre {key[0]} período {key[1]} (D)", 'Ingreso coincidente; expediente T1 no acreditado' if vals else 'No acreditado', 'B/C foto; no reemplaza proxy R19']
        photo_counts[(s['anio_origen'],key[0],key[1],state)]+=1
        for c in s['contextos'] if s['contextos'] else [None]:photo_rows.append(row)
    for row,photo in zip(payload['rows'],photo_rows):row.extend(photo)
    payload['headers']+=['Foto completa del período (R19)','Fuente de foto','Corte declarado','Respaldo de expediente en foto','Límite del complemento de foto']
    write(private/'payload.json',payload)
    write(out/'FOTOS_INTEGRADAS.json',{'clase':'B/C, cortes D Alexi 30-10-2026','estado':'RESPALDO_SEPARADO_SIN_REEMPLAZAR_PROXIES','por_periodo_estado':[{'cohorte':k[0],'anio':k[1],'periodo':k[2],'estado':k[3],'posiciones':v} for k,v in sorted(photo_counts.items())],'no_modifica_R19':True,'regla':'Llave corporal y año de ingreso ya usados por R19 (docs/SEGUIMIENTO_RUT_Y_CONVERSION_PERIODOS_20261023.md); prioridad VIG1 > NO APLICA > PENDIENTE > VIG0. No se certifica DV ni expediente T1; ausencia no significa no matrícula.'})
    # Propuesta delimitada: el código de contexto no alimenta las tasas de foto.
    p99=load(source('reevaluacion_99'));groups99=p99['casos_agrupados']
    md=['# Propuesta de adjudicación de los 99 · NO APLICADA','C/E · Catálogo y tipo de plan respaldan una opción; no prueban su atribución al expediente y período. La aprobación debe ser D explícita.',
        'B/C · 95 contextos con candidato único (63 de jornada distinta y 32 sin enlace al expediente T1); 4 contextos IINF20241 con alternativas. Fuente: H007/REEVALUACION_99.json; H002 y TIPO_PLAN v2 allí fijados.',
        'C · Efecto si solo se aprueba el código: 0 cambios de numerador/denominador y 0,00 pp en R19/V25. Las fórmulas de tasas usan las fotos y proxies, no el código adjudicado de la vista. No se simula nueva vigencia ni herencia automática.']
    for i,g in enumerate(groups99,1):
        md+=['',f"## Grupo {i} · {g['plan']} · {g['anio_observado']}-{g['periodo_nativo']} · {g['n']} contextos",f"- Motivo: {g['motivo_v24']}; sede {g['sede']}, jornada {g['jornada']}; tipo {g['tipo_v2']}.",f"- Opciones: {g['candidatos_H002_2026']}. Estado C/E: {g['estado']}.",f"- Evidencia: catálogo H002 2026, perfil v2 y coherencia agregada; contexto congelado de H007. No acredita atribución personal ni retrotrae automáticamente el catálogo a 2025.",f"- Requisito: {g['requisito']}",'- Efecto acotado: estos contextos pasarían a correspondencia interna D si se aprueba una opción; 0,00 pp en tasas.','- Decisión Alexi: aprobar / rechazar / pedir evidencia: ____']
        if g['estado']=='CATALOGO_MULTIPLE_E':md+=['- Para decidir entre versiones: carga aceptada del expediente en el año/período o historia de ingreso y versión con procedencia verificable. El mismo tipo REGULAR y el nombre IINF20241 no desempatan.']
    (out/'PROPUESTA_ADJUDICACION_99.md').write_text('\n'.join(md)+'\n')
    write(out/'PROPUESTA_ADJUDICACION_99.json',{'aplicada':False,'clase':'C/E; decisión D pendiente','grupos':groups99,'efecto_exclusivo_codigo_pp':0,'evidencia':cfg['entradas']['reevaluacion_99'],'limite':'Efecto de adjudicación de código; no de vigencia, expediente o matrícula.'})
    write(out/'FUENTES_H008.json',{'entradas':cfg['entradas'],'fotos':inventories,'clase':'B rutas y hashes; C tratamiento; E cortes no acreditados'})
    print(json.dumps({'posiciones_C1':1135,'contextos_v20':sum(r[1] for r in rows),'fotos_inventariadas':len(inventories),'grupos_99':len(groups99)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--privado',required=True);p.add_argument('--salida',required=True);a=p.parse_args();prepare(a.config,a.privado,a.salida)
