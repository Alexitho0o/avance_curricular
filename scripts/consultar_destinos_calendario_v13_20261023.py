"""Reproduce la consulta de destinos v7 usada por V13 (2026-10-23).

Entradas: ORIGENES_T1 de V12 y descriptor v7 congelado, ambos verificados.
Calendario explícito: 2024→2025; 2025→2025; 2026→2026; períodos nativos 2/3.
Salida individual únicamente en carpeta nueva privada fuera de Git. La salida
agregada no contiene identificadores. No modifica fuentes, diccionario, Excel,
vigencia ni denominadores y no atribuye automáticamente períodos a cierres.

Ejecutar con --salida-agregada ARCHIVO_NUEVO --salida-privada CARPETA_NUEVA.
--origenes permite reubicar la entrada privada conservando su hash; no se usa /tmp.
"""
import sys,json,collections,re,os,subprocess,datetime,argparse
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest-origen',type=Path,default=R/'outputs/aplicacion_diccionario_intertrimestral_20261023_125556/MANIFEST_APLICACION.json')
    parser.add_argument('--origenes',type=Path,help='Ubicación alternativa del mismo ORIGENES_T1.json, con hash verificado contra manifiesto.')
    parser.add_argument('--salida-agregada',type=Path,required=True,help='Archivo JSON nuevo; nunca incluye identificadores individuales.')
    parser.add_argument('--salida-privada',type=Path,required=True,help='Carpeta nueva fuera de Git, con padre existente; permisos 0700/0600.')
    args=parser.parse_args()
    manifest=json.loads(args.manifest_origen.read_text())
    source=(args.origenes or Path(manifest['privado'])/'ORIGENES_T1.json').resolve()
    assert sha256(source)==manifest['auditoria_privada_hashes']['ORIGENES_T1.json']
    aggregate=args.salida_agregada.resolve();private=args.salida_privada.resolve()
    assert not aggregate.exists() and aggregate.parent.is_dir(), 'La salida agregada debe ser nueva y su carpeta debe existir'
    assert not private.exists() and private.parent.is_dir(), 'La salida privada debe ser una carpeta nueva con padre existente'
    assert not private.is_relative_to(R), 'El detalle no puede quedar dentro del repositorio'
    assert subprocess.run(['git','-C',str(private.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0, 'El detalle debe quedar fuera de cualquier repositorio Git'
    orig=json.loads(source.read_text());assert len(orig)==3179
    # Snapshot aprobado que generó esta revisión. No depende de futuros cambios del puntero activo.
    descriptor=R/'data/diccionario_sies_seguimiento/v7_20261023_inf35_03_t3/descriptor.json'
    assert sha256(descriptor)=='9037a9a8eb324dafa6b0535b0e66bd50425a058be8295f0edd405339115ac1b8'
    s=DiccionarioSiesSeguimiento(root=R,descriptor=descriptor);assert s.edicion=='v7_20261023_inf35_03_t3';index=collections.defaultdict(list)
    for persona,year,period,payload in s.db.execute('select persona,anio,periodo,payload from observaciones'):
     index[(persona,int(year),str(period))].append(json.loads(payload))
    parse=lambda c:re.fullmatch(r'I(\d+)S(\d+)C(\d+)J(\d+)V(\d+)',str(c or ''));counters={k:collections.Counter() for k in ['ranuras','contextos_estado','relacion_codigo','pendientes_tipo','comparacion_plan','contraste_dimensiones','origen_respaldo_mu','contextos_por_ranura','identidad']};contexts=[];slots=[];cache={};reused=0
    for x in orig:
     y=int(x['anio']);dy=2025 if y==2024 else y;person=x['persona'];origin_code=x['codigo_origen'];parts=parse(origin_code).groups();backed=False
     if person:
      try:backed=origin_code in s.codigos_mu(persona=person,anio=y)['codigos']
      except ValueError:pass
     counters['origen_respaldo_mu'][(y,'API índice MU' if backed else 'Respaldo literal V12; API no atribuye este origen')]+=1
     for period in ['2','3']:
      key=(y,dy,period);obs=index.get((person,dy,period),[]) if person else [];slot={'fila_origen_foto':x['fila_foto'],'persona':person,'anio_origen':y,'anio_observado':dy,'periodo_nativo':period,'codigo_origen_T1':origin_code,'origen_respaldado_api':backed,'origen_respaldo_literal_V12':x['respaldo'],'contextos':len(obs),'sin_contexto':not bool(obs),'clasificacion_ausencia':'E: no prueba deserción ni falta de vigencia' if not obs else None};slots.append(slot)
      counters['ranuras'][(*key,'Con contexto' if obs else 'Sin contexto')]+=1;counters['contextos_por_ranura'][(*key,len(obs))]+=1
      for ob in obs:
       oid=ob['observacion_id'];qkey=(person,oid)
       if qkey in cache:q=cache[qkey];reused+=1
       else:
        q=s.consultar(persona=person,codcli=ob['CODCLI'],plan=ob['plan'],anio=dy,periodo=period,carrera=ob['carrera'],sede=ob['sede_dimension'],jornada=ob['jornada_sies']);assert q.get('observacion_id')==oid;cache[qkey]=q
       code=q['codigo_sies'];state=q['nivel_respaldo'];dest=parse(code);counters['contextos_estado'][(*key,state)]+=1
       if not code:rel='Destino sin código adoptado'
       elif code==origin_code:rel='Código destino igual a origen T1'
       elif dest.groups()[:4]==parts[:4]:rel='Misma familia SIES; versión distinta'
       else:
        ds=dest.groups();dd=[label for label,i in [('institución',0),('sede',1),('carrera',2),('jornada',3)] if ds[i]!=parts[i]];rel='Destino distinto en '+', '.join(dd)
       counters['relacion_codigo'][(*key,rel,state)]+=1
       cc=set(ob['codigos_anuales_documentados'])|set(ob['candidatos_calculados']);cc|={str(ob.get(k) or '') for k in ['codigo_documental_atribuible','codigo_interno_adoptado','codigo_propuesto','codigo_propuesto_inicial']};cp=[parse(c).groups() for c in cc if parse(c)];samec=[c for c in cp if c[:3]==parts[:3]];samej=[c for c in samec if c[3]==parts[3]];pending=None
       if not code:
        if not cp:pending='Sin código candidato/contexto de familia atribuido'
        elif not samec:pending='Candidatos en otra carrera/sede/institución; vínculo con origen pendiente'
        elif not samej:pending='Misma carrera/sede; jornada candidata distinta del origen'
        else:pending='Familia del origen entre candidatos; atribución de versión/plan pendiente'
        counters['pendientes_tipo'][(*key,pending)]+=1
       pp={z['plan'] for z in index.get((person,y,'1'),[]) if z['CODCLI']==ob['CODCLI']}
       if not pp:pl='Sin contexto nativo 1 del mismo CODCLI en año origen'
       elif len(pp)>1:pl='Varios planes en contexto nativo 1 de año origen'
       elif ob['plan'] in pp:pl='Mismo plan observado en contexto nativo 1 de año origen'
       else:pl='Plan observado distinto del contexto nativo 1 de año origen'
       counters['comparacion_plan'][(*key,pl)]+=1
       dd=[]
       if str(ob['sede_dimension'])!=parts[1]:dd.append('sede')
       if str(ob['jornada_sies'])!=parts[3]:dd.append('jornada')
       dim='Contexto observado difiere en '+', '.join(dd) if dd else 'Sede/jornada del contexto coinciden con código origen';counters['contraste_dimensiones'][(*key,dim,state)]+=1
       contexts.append({**slot,'observacion_id':oid,'codcli':ob['CODCLI'],'carrera_umas':ob['carrera'],'plan':ob['plan'],'sede_observada':ob['sede_dimension'],'jornada_observada':ob['jornada_sies'],'codigo_destino':code,'estado_destino':state,'codigo_documental':q.get('codigo_documental'),'codigo_interno':q.get('codigo_interno'),'regla':q.get('regla'),'pendiente':q.get('pendiente'),'relacion_codigo':rel,'tipo_pendiente':pending,'comparacion_plan':pl,'contraste_dimensiones':dim,'fuentes_promedios':ob.get('fuentes_promedios'),'contexto_no_es_foto_cierre':True})
    assert len(slots)==6358;assert len({(x['fila_origen_foto'],x['periodo_nativo']) for x in slots})==6358;assert len({(x['fila_origen_foto'],x['periodo_nativo'],x['observacion_id']) for x in contexts})==len(contexts)
    private.mkdir(mode=0o700);assert private.stat().st_mode & 0o777==0o700
    for name,data in [('RANURAS_POR_ORIGEN_PERIODO.json',slots),('CONTEXTOS_POR_ORIGEN_PERIODO.json',contexts)]:
     p=private/name
     with os.fdopen(os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:json.dump(data,f,ensure_ascii=False,indent=2)
     os.chmod(p,0o600)
    def table(c):return [{'clave':list(k) if isinstance(k,tuple) else k,'n':n} for k,n in sorted(c.items(),key=lambda x:str(x[0]))]
    out={'fecha':datetime.datetime.now().astimezone().isoformat(),'diccionario':s.edicion,'origenes':3179,'denominadores_origen':dict(collections.Counter(x['anio'] for x in orig)),'ingresos_nuevos_excluidos':1294,'calendario_explicito':{'2024':'2025 períodos nativos 2/3; proxy solicitado, sin equivalencia con cierre acreditada','2025':'2025 períodos nativos 2/3','2026':'2026 períodos nativos 2/3'},'ranuras_fila_origen_periodo':len(slots),'ranuras_con_contexto':sum(not x['sin_contexto'] for x in slots),'ranuras_sin_contexto':sum(x['sin_contexto'] for x in slots),'contextos_por_origen_periodo':len(contexts),'contextos_distintos':len({x['observacion_id'] for x in contexts}),'reconsultas_reutilizadas_sin_duplicar_consulta_api':reused,'tablas':{k:table(c) for k,c in counters.items()},'privado':str(private),'privado_hashes':{p.name:sha256(p) for p in private.iterdir()},'fuente_origen':{str(source):sha256(source)},'nuevos_cierres':0,'limites':['seguir_cohorte rechaza 2024→2025 por contrato; se usó consultar con contexto exacto y ambos años separados.','Períodos nativos no son automáticamente cierres trimestrales.','Una observación puede vincularse a dos cohortes; se conserva fila origen y no se suman como personas únicas.','Código origen se preserva; otras familias o carreras son contextos observados, no asignaciones a la carrera T1.','Sin contexto no equivale a deserción; no se recalculó vigencia, retención ni denominadores.','Código documental anual atribuido no acredita aceptación SIES ni jornada exacta al cierre.']}
    # Foco multiversión heredado de V12: no inventa una clasificación nueva.
    origen_por_fila={x['fila_foto']:x for x in orig}
    foco_estado=collections.Counter()
    foco_familia=collections.defaultdict(collections.Counter)
    foco_periodo=collections.defaultdict(collections.Counter)
    for contexto in contexts:
        origen=origen_por_fila[contexto['fila_origen_foto']]
        if not origen['multiple']:
            continue
        estado=contexto['estado_destino']
        foco_estado[estado]+=1
        foco_familia[origen['familia']][estado]+=1
        foco_periodo[(contexto['anio_origen'],contexto['anio_observado'],contexto['periodo_nativo'],origen['familia'])][estado]+=1
    out['foco_multiversion']={
        'definicion':'Bandera multiple heredada de ORIGENES_T1 V12; familia con más de una versión en su evidencia histórica, no catálogo actual.',
        'total':sum(foco_estado.values()),
        'estados':dict(foco_estado),
        'por_familia':[{'familia_origen':familia,'estados':dict(conteos),'total':sum(conteos.values())} for familia,conteos in sorted(foco_familia.items())],
        'por_anio_periodo_familia':[{'clave':list(clave),'estados':dict(conteos),'total':sum(conteos.values())} for clave,conteos in sorted(foco_periodo.items())]
    }
    out['reproduccion']={'script':str(Path(__file__).resolve()),'sha256_script':sha256(__file__),'manifest_origen':str(args.manifest_origen.resolve()),'manifest_origen_sha256':sha256(args.manifest_origen),'descriptor':str(descriptor),'descriptor_sha256':sha256(descriptor),'clasificacion':'C: consulta reproducible; B: conteos; D: calendario de presentación; E: límites conservados'}
    with aggregate.open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2)
    s.close()
    print(json.dumps({'salida_agregada':str(aggregate),'salida_privada':str(private),'origenes':len(orig),'ranuras':len(slots),'contextos':len(contexts),'nuevos_cierres':0},ensure_ascii=False))


if __name__ == "__main__":
    main()
