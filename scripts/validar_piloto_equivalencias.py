#!/usr/bin/env python3
"""Ejecuta H6 sobre proyecciones académicas completas, sin asignar mallas.

Contrato: docs/fase_6_piloto_validacion_universo.md. Conserva pesos y
excepciones; nunca suma grupos como personas ni corrige contextos desde DA.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.equivalencias_historicas import cargar_maestro, consultar_sies, resolver_umas
from scripts.construir_maestro_equivalencias import (
    sha, json_bytes, key, identifier, read_tsv, tsv_bytes, verify_sources, write_immutable)

OBS_FIELDS = ('PLAN_DE_ESTUDIO','CODCARR','CARRERA','JORNADA','ANO','PERIODO',
              'REGIMEN','estado_observacion')
QUERY_FIELDS = ('codcarpr','plan_umas','sede_umas','jornada_umas','anio','periodo',
                'regimen','nombre_interno')
DA_FIELDS = ('estado_datos_alumnos','carrera_da_vs_promedios',
             'jornada_da_vs_promedios','sede_da_vs_plan','ambito_anio_matricula_da')
MISSING = {'','NULL','NONE','NAN'}


def token(value):
    s = '' if value is None else str(value).strip()
    return None if s.upper() in MISSING else s


def weight(row):
    text = str(row.get('filas_reporte',''))
    if not re.fullmatch(r'[1-9]\d*',text):
        raise ValueError('Peso de reporte inválido')
    return int(text)


def adaptar_contexto(row, planes_por_codigo):
    """Devuelve estado, motivos y consulta completa o None; no modifica row."""
    year = token(row.get('ANO'))
    if year is None or not re.fullmatch(r'\d{4}',year):
        return 'ANIO_NO_VALIDO', ['ANO ausente o no es año de cuatro dígitos'], None
    if not 2007 <= int(year) <= 2026:
        return 'FUERA_AMBITO', ['ANO fuera de 2007–2026'], None
    plan = planes_por_codigo.get(token(row.get('PLAN_DE_ESTUDIO')))
    contexts = [] if plan is None else plan.get('contextos_catalogo',[])
    if (row.get('estado_plan_catalogo') != 'PLAN_CONTEXTO_UNICO' or len(contexts)!=1
            or not token(contexts[0].get('Codcarr')) or not token(contexts[0].get('Sede'))):
        return 'PLAN_SIN_CONTEXTO_UNICO', ['Plan sin carrera y sede únicas corroboradas en catálogo'], None
    context = contexts[0]
    career = token(row.get('CODCARR'))
    if career and career != token(context['Codcarr']):
        return 'CARRERA_PLAN_DISCREPANTE', ['CODCARR del reporte difiere de Codcarr del plan'], None
    query = {'anio':int(year),'periodo':token(row.get('PERIODO')),
        'regimen':token(row.get('REGIMEN')),'codcarpr':career,
        'nombre_interno':token(row.get('CARRERA')),
        'plan_umas':token(row.get('PLAN_DE_ESTUDIO')),
        'sede_umas':token(row.get('SEDE_LISTADO')),'jornada_umas':token(row.get('JORNADA'))}
    missing = [f for f in QUERY_FIELDS if query[f] is None]
    if missing or row.get('carrera_plan_vs_promedios')!='IGUAL':
        return 'CLAVES_INCOMPLETAS', missing or ['Carrera no comparable en H4'], None
    if (query['sede_umas'] != token(context['Sede']) or
            token(row.get('CODCARR_LISTADO')) != token(context['Codcarr'])):
        raise ValueError('Contexto listado H4 contradice catálogo H5')
    return 'CONSULTABLE', [], query


def reconcile_projections(contextos, observaciones):
    """Contraste por grano, no solo por un total que pueda ocultar compensaciones."""
    def aggregate(rows):
        counts = Counter()
        for r in rows:counts[tuple(r[f] for f in OBS_FIELDS)] += weight(r)
        return counts
    left, right = aggregate(contextos), aggregate(observaciones)
    if left != right:
        raise ValueError('Proyecciones H4 difieren por dimensiones o peso')
    return {'grupos_observacion':len(right),'filas_reporte':sum(right.values()),
            'igualdad_por_grano_y_peso':True}


def diagnostic(result, year):
    state = result['estado']; n = len({c['codigo_unico'] for c in result.get('candidatos',[])})
    if state=='PENDIENTE_EVIDENCIA':
        return 'CANDIDATO_UNICO_SIN_ACREDITAR' if n==1 else 'MULTIPLES_CANDIDATOS_SIN_ACREDITAR'
    if result.get('motivo')=='NOMBRE_INTERNO_NO_COINCIDE':return 'NOMBRE_DISTINTO_SIN_ALIAS'
    if state=='SIN_EQUIVALENCIA':
        return 'SIN_REGLA_HISTORICA_ACREDITADA' if year<2026 else 'SIN_CANDIDATO_EXACTO_2026'
    return result.get('motivo',state)


def distribution(rows, fields):
    buckets = {}
    for row in rows:
        k = tuple(str(row.get(f,'')) for f in fields)
        if k not in buckets:buckets[k]={**dict(zip(fields,k)),'contextos':0,'filas_reporte':0}
        buckets[k]['contextos']+=1;buckets[k]['filas_reporte']+=weight(row)
    return [buckets[k] for k in sorted(buckets)]


def ejecutar_umas(master, contextos, observaciones):
    checks = reconcile_projections(contextos,observaciones)
    plans = {p['CODPESTUD']:p for p in master['planes_umas']}
    if len(plans)!=len(master['planes_umas']):raise ValueError('Planes duplicados en maestro')
    if not {r['PLAN_DE_ESTUDIO'] for r in contextos} <= set(plans):
        raise ValueError('Plan observado perdido en cobertura del maestro')
    cache = {}; results = []; query_groups = {}
    keep = (*OBS_FIELDS,'estado_plan_catalogo','carrera_plan_vs_promedios','estado_ramo',
            *DA_FIELDS,'CODCARPR_DA','JORNADA_DA','SEDE_DA','ANOMATRICULA_DA','ANOINGRESO_DA',
            'CODCARR_LISTADO','SEDE_LISTADO','fila_promedios_ejemplo','fila_alumnos_ejemplo','fila_plan_ejemplo')
    for line,row in enumerate(contextos,2):
        status,reasons,query = adaptar_contexto(row,plans)
        result = {'fila_contextos_h4':line,**{f:row.get(f,'') for f in keep},
            'filas_reporte':weight(row),'estado_adaptacion':status,'motivos_adaptacion':reasons,
            'consulta_id':None,'estado_resolucion':'NO_CONSULTADO','diagnostico':status,
            'codigo_unico_resuelto':None,'codigos_candidatos':[],
            'numero_destinos_candidatos':0,'acredita_asignacion_individual':False}
        if query is not None:
            k = key(*(query[f] for f in QUERY_FIELDS))
            if k not in cache:
                response = resolver_umas(master,**query)
                if response['estado']!='EQUIVALENCIA_ACREDITADA' and response['codigo_unico'] is not None:
                    raise ValueError('Resolvedor devolvió código sin acreditación')
                if response.get('acredita_asignacion_individual') is not False:
                    raise ValueError('Resolvedor atribuye asignación individual')
                cache[k] = response
                query_groups[k] = {'consulta_id':identifier('Q-',*([query[f] for f in QUERY_FIELDS])),
                    'clave':k,**query,'estado_resolucion':response['estado'],
                    'motivo_h5':response.get('motivo'), 'diagnostico':diagnostic(response,query['anio']),
                    'codigo_unico_resuelto':response['codigo_unico'],
                    'codigos_candidatos':sorted({c['codigo_unico'] for c in response.get('candidatos',[])}),
                    'candidatos_ids':sorted(c['id'] for c in response.get('candidatos',[])),
                    'nombres_en_equivalencias':response.get('nombres_en_equivalencias',[]),
                    'contextos':0,'filas_reporte':0,'filas_contextos_h4':[],
                    'acredita_asignacion_individual':False}
            group = query_groups[k]
            group['contextos']+=1;group['filas_reporte']+=weight(row);group['filas_contextos_h4'].append(line)
            result.update({f:group[f] for f in ('consulta_id','estado_resolucion','diagnostico',
                                               'codigo_unico_resuelto','codigos_candidatos')})
            result['numero_destinos_candidatos'] = len(group['codigos_candidatos'])
        results.append(result)
    queries = sorted(query_groups.values(),key=lambda r:r['clave'])
    if len({q['consulta_id'] for q in queries})!=len(queries):raise ValueError('Colisión de identificadores de consulta')
    coverage = []
    for code,p in sorted(plans.items()):
        rs = [r for r in results if r['PLAN_DE_ESTUDIO']==code]
        coverage.append({'plan_umas':code,'presencia_h4':p['presencia'],
            'contextos_catalogo':p['contextos_catalogo'],'anios_actividad_observada':p['anios_actividad_observada'],
            'contextos':len(rs),'filas_reporte':sum(weight(r) for r in rs),
            'filas_consultables':sum(weight(r) for r in rs if r['estado_adaptacion']=='CONSULTABLE'),
            'filas_con_codigo_acreditado':sum(weight(r) for r in rs if r['estado_resolucion']=='EQUIVALENCIA_ACREDITADA'),
            'consultas_unicas':len({r['consulta_id'] for r in rs if r['consulta_id']}),
            'estados_adaptacion':sorted({r['estado_adaptacion'] for r in rs}),
            'candidatos_en_maestro_2026':p['candidatos_plan_sies'],
            'estado_observacion':'OBSERVADO_EN_REPORTE' if rs else 'SIN_OBSERVACION_EN_REPORTE',
            'limite':'Ausencia de actividad no acredita cierre ni inactividad institucional'})
    adaptation = distribution(results,('estado_adaptacion',))
    resolution = distribution(results,('estado_resolucion','diagnostico','numero_destinos_candidatos'))
    annual = distribution(results,('ANO','estado_adaptacion','estado_resolucion','diagnostico'))
    controls = []
    for field in (*DA_FIELDS,'estado_ramo'):
        controls.extend({'eje':field,'valor':r[field],'contextos':r['contextos'],
                         'filas_reporte':r['filas_reporte']} for r in distribution(results,(field,)))
    total = sum(weight(r) for r in results)
    query_total = sum(weight(q) for q in queries)
    skipped = sum(weight(r) for r in results if r['estado_adaptacion']!='CONSULTABLE')
    if total!=checks['filas_reporte'] or total!=query_total+skipped:
        raise ValueError('Pérdida o expansión de filas UMAS')
    checks.update(filas_sin_expansion=True,universo_planes_preservado=len(coverage)==len(plans),
                  consultas_reintegradas_sin_expansion=True)
    summary = {'unidad':'filas de PROMEDIOS y contextos agregados; no personas ni matrículas',
        'contextos_entrada':len(contextos),'filas_reporte':total,'consultas_unicas':len(queries),
        'filas_consultables':query_total,'filas_no_consultadas':skipped,
        'filas_con_codigo_acreditado':sum(weight(r) for r in results if r['estado_resolucion']=='EQUIVALENCIA_ACREDITADA'),
        'planes_cubiertos':len(coverage),'planes_observados_reporte':sum(bool(p['contextos']) for p in coverage),
        'planes_sin_observacion_reporte':sum(not p['contextos'] for p in coverage),
        'particion_adaptacion':adaptation,'resolucion':resolution}
    return {'resultados_contextos':results,'consultas_unicas':queries,'distribucion':annual,
            'controles':controls,'cobertura_planes':coverage,'resumen':summary,'checks':checks}


def ejecutar_sies(master):
    offers={(r['anio'],r['codigo_unico']):r for r in master['oferta_anual']}
    mrun={(int(r['cat_periodo']),r['codigo_unico']):r for r in master['mrun_anual']}
    if len(offers)!=len(master['oferta_anual']) or len(mrun)!=len(master['mrun_anual']):
        raise ValueError('Clave anual repetida')
    rows=[]
    for year,code in sorted(offers.keys()|mrun.keys()):
        result=consultar_sies(master,anio=year,codigo_unico=code)
        o=offers.get((year,code));m=mrun.get((year,code))
        if o is not None and (result['estado']!='OFERTA_ANUAL_LOCALIZADA' or result['oferta_anual']!=o):
            raise ValueError('Oferta anual perdida o atributos modificados')
        if o is None and (result['estado']!='SIN_OFERTA_ANUAL' or result['codigo_unico'] is not None):
            raise ValueError('Oferta inventada')
        if result.get('observaciones_mrun',[]) != ([m] if m else []):
            raise ValueError('Observación MRUN perdida o modificada')
        rows.append({'anio':year,'codigo_unico':code,
            'presencia':'OFERTA_Y_MRUN' if o and m else 'SOLO_OFERTA' if o else 'SOLO_MRUN',
            'estado_consulta':result['estado'],'motivo':result.get('motivo'),
            'registros_mrun':int(m['filas_matricula']) if m else 0,
            'nombre_anual_oferta':o['nombre_carrera'] if o else None,
            'nombre_oferta_2026':o['nombre_oferta_2026'] if o else None,
            'nombre_mrun':m['nomb_carrera'] if m else None,
            'componentes_sies':o['componentes_sies'] if o else None,
            'modalidad_oferta':o['modalidad'] if o else None,
            'tipo_plan_oferta':o['tipo_plan_sies'] if o else None,
            'vigencia_oferta':o['vigencia'] if o else None,
            'fuente_oferta':o['fuente'] if o else None,
            'registro_mrun_ejemplo':m['registro_ejemplo'] if m else None,
            'acredita_equivalencia_umas':False,'acredita_asignacion_individual':False})
    by_state={}
    for r in rows:
        k=(r['presencia'],r['estado_consulta'],r['motivo'])
        if k not in by_state:by_state[k]={'presencia':k[0],'estado_consulta':k[1],
            'motivo':k[2],'claves_anuales':0,'registros_mrun':0}
        by_state[k]['claves_anuales']+=1;by_state[k]['registros_mrun']+=r['registros_mrun']
    coverage=[]
    for u in master['universo_sies']:
        rs=[r for r in rows if r['codigo_unico']==u['codigo_unico']]
        coverage.append({'codigo_unico':u['codigo_unico'],'presencia_fuentes':u['presencia'],
            'nombre_literal_oferta_2026':u['nombre_literal_oferta_2026'],
            'nombre_2026_estado':u['nombre_2026_estado'],'claves_anuales_consultadas':len(rs),
            'claves_con_oferta':sum(r['estado_consulta']=='OFERTA_ANUAL_LOCALIZADA' for r in rs),
            'claves_sin_oferta':sum(r['estado_consulta']=='SIN_OFERTA_ANUAL' for r in rs),
            'registros_mrun':sum(r['registros_mrun'] for r in rs)})
    if {r['codigo_unico'] for r in rows}!={r['codigo_unico'] for r in coverage}:
        raise ValueError('Cobertura SIES incompleta')
    return {'resultados':rows,'cobertura':coverage,'resumen':{'unidad':'claves anuales y registros observados MRUN; no personas únicas',
        'claves_consultadas':len(rows),'codigos_cubiertos':len(coverage),
        'filas_oferta_verificadas':len(offers),'registros_mrun':sum(r['registros_mrun'] for r in rows),
        'por_estado':sorted(by_state.values(),key=lambda r:r['presencia'])},
        'checks':{'atributos_oferta_literales_preservados':True,'observaciones_mrun_preservadas':True,
                  'universo_sies_preservado':True}}


def examples(umas,sies,master):
    selected=[];rs=umas['resultados_contextos']
    specs=[('Logística regular',lambda r:r['PLAN_DE_ESTUDIO']=='ILOG20241' and r['ANO']=='2026'),
           ('Logística continuidad',lambda r:r['PLAN_DE_ESTUDIO']=='CILOG20241' and r['ANO']=='2026'),
           ('Naturopatía',lambda r:r['PLAN_DE_ESTUDIO']=='NATP20251' and r['ANO']=='2026'),
           ('Plan con actividad anterior al año de su identificador',lambda r:r['PLAN_DE_ESTUDIO']=='IECIRE20211' and r['ANO']=='2019'),
           ('Plan sin catálogo',lambda r:r['estado_adaptacion']=='PLAN_SIN_CONTEXTO_UNICO'),
           ('Carrera del reporte distinta del plan',lambda r:r['estado_adaptacion']=='CARRERA_PLAN_DISCREPANTE'),
           ('Nombre distinto sin alias',lambda r:r['diagnostico']=='NOMBRE_DISTINTO_SIN_ALIAS'),
           ('Jornada distinta frente a DatosAlumnos',lambda r:r['jornada_da_vs_promedios']=='DIFERENTE'),
           ('Año ausente',lambda r:r['estado_adaptacion']=='ANIO_NO_VALIDO')]
    for label,predicate in specs:
        found=sorted((r for r in rs if predicate(r)),key=lambda r:r['fila_contextos_h4'])
        selected.append({'caso':label,'tipo':'CONTEXTO_REPORTE_UMAS',
            'ejemplo':found[0] if found else None,'estado':'OBSERVADO' if found else 'SIN_EJEMPLO_EN_FUENTES'})
    for label,year,code in [('Ciberseguridad histórica',2020,'I162S2C46J2V2'),
                             ('Naturopatía solo oferta',2026,'I162S2C90J2V1'),
                             ('Código heredado MRUN',2008,'I162M2008N1')]:
        found=[r for r in sies['resultados'] if r['anio']==year and r['codigo_unico']==code]
        selected.append({'caso':label,'tipo':'CONSULTA_SIES','ejemplo':found[0] if found else None})
    selected.append({'caso':'Jornada semipresencial sin correspondencia UMAS acreditada',
        'tipo':'INVENTARIO_CANDIDATOS_NO_ES_ACTIVIDAD',
        'ejemplos':[{'id':c['id'],'plan_umas':c['plan_umas'],'codigo_unico':c['codigo_unico'],
            'jornada_umas':c['jornada_umas'],'estado':c['estado']} for c in master['candidatos_plan_sies']
            if c['componentes_sies']['jornada']=='3']})
    return selected


def verify(config):
    if config['schema_version']!=1 or config['fase']!=6 or config['periodo_objetivo']!=[2007,2026]:
        raise ValueError('Contrato H6 inválido')
    sources=config['sources']
    for s in sources.values():
        if sha(s['path'])!=s['sha256']:raise ValueError('Fuente H6 alterada: '+s['path'])
    h5=json.loads(Path(sources['fuentes_h5']['path']).read_text())
    relocations=config.get('reubicaciones_fuentes',{})
    for original,replacement in relocations.items():
        descriptors=[x for x in [*h5['sources'].values(),*h5['referencias_congeladas']] if x['path']==original]
        if not descriptors or any(x['sha256']!=replacement['sha256'] for x in descriptors):
            raise ValueError('Reubicación no conserva el hash histórico')
        if not any(x['path']==replacement['path'] and x['sha256']==replacement['sha256'] for x in sources.values()):
            raise ValueError('Respaldo de reubicación no declarado como fuente H6')
        for descriptor in descriptors:descriptor['path']=replacement['path']
    verify_sources(h5)
    for phase,pairs in [(4,[('contextos_h4','conciliacion_contextos_umas.tsv'),('observaciones_h4','observaciones_plan_periodo.tsv')]),
                        (5,[('maestro_h5','maestro.json'),('fuentes_h5','fuentes.json')])]:
        manifest=json.loads(Path(sources[f'manifest_h{phase}']['path']).read_text())
        for sid,filename in pairs:
            if manifest['outputs'][filename]!=sources[sid]['sha256']:
                raise ValueError('Proyección fuera del manifiesto H'+str(phase))
        if phase==5:
            for p,h in manifest['scripts_sha256'].items():
                if sha(ROOT/p)!=h:raise ValueError('Código H5 modificado: '+p)


def run(config_path,output):
    config=json.loads(Path(config_path).read_text());verify(config);s=config['sources']
    master=cargar_maestro(s['maestro_h5']['path'],s['manifest_h5']['path'])
    umas=ejecutar_umas(master,read_tsv(s['contextos_h4']['path']),read_tsv(s['observaciones_h4']['path']))
    sies=ejecutar_sies(master)
    summary={'fase':6,'estado':'PILOTO_COMPLETADO_CON_EXCEPCIONES','umas':umas['resumen'],'sies':sies['resumen'],
        'reglas_efectivas_acreditadas':len(master['reglas_efectivas']),
        'limite':'Validación del universo disponible; no certificación de mallas históricas ni integración de consumidores.'}
    acceptance={'validacion_tecnica':'APROBADA','controles':{**umas['checks'],**sies['checks']},
        'asignacion_historica_automatica_habilitada':False,
        'motivo':'Faltan equivalencias plan/período acreditadas y evidencia individual de asignación histórica.',
        'integracion_h7':'Solo compatible conservando estados y bloqueos; no ejecutada en H6',
        'excel_h8':'No regenerado en H6'}
    gaps=[{'prioridad':1,'brecha':'EQUIVALENCIA_PLAN_SIES_POR_PERIODO',
        'evidencia_requerida':['CODCARPR','CODPESTUD','nombre interno aprobado','sede UMAS/SIES','jornada UMAS/SIES',
                               'Código Único SIES','año/período/régimen o intervalo efectivo documentado','fuente/hash/localizador'],
        'limite':'Un candidato único no acredita la equivalencia.'},
        {'prioridad':2,'brecha':'ASIGNACION_INDIVIDUAL_HISTORICA_PLAN',
        'evidencia_requerida':['Matrícula interna','plan asignado','inicio/fin efectivo o período garantizado','evento de cambio','linaje del campo PLAN_DE_ESTUDIO'],
        'limite':'No pedir ni publicar identidades en salidas académicas; tratamiento solo en fuente autorizada.'},
        {'prioridad':3,'brecha':'CONTEXTOS_Y_NOMBRES_PENDIENTES',
        'evidencia_requerida':['Catálogo para las etiquetas de plan faltantes','explicación documentada de discrepancias de carrera/jornada','alias nominal explícito si corresponde'],
        'limite':'No quitar espacios internos, prefijos o PASO para forzar coincidencias.'},
        {'prioridad':4,'brecha':'COBERTURA_OFERTA_2007_2009',
        'evidencia_requerida':['Oferta anual completa de esas ediciones o respaldo oficial equivalente'],
        'limite':'MRUN acredita observación de matrícula, no oferta completa ni vigencia de malla.'}]
    payloads={'resumen.json':json_bytes(summary),'aceptacion_h6.json':json_bytes(acceptance),
        'consultas_umas.tsv':tsv_bytes(umas['consultas_unicas']),
        'resultados_contextos_umas.tsv':tsv_bytes(umas['resultados_contextos']),
        'distribucion_anual_umas.tsv':tsv_bytes(umas['distribucion']),
        'controles_contextos_umas.tsv':tsv_bytes(umas['controles']),
        'cobertura_planes_piloto.tsv':tsv_bytes(umas['cobertura_planes']),
        'consultas_sies_anuales.tsv':tsv_bytes(sies['resultados']),
        'cobertura_codigos_piloto.tsv':tsv_bytes(sies['cobertura']),
        'ejemplos_piloto.json':json_bytes(examples(umas,sies,master)),
        'brechas_priorizadas.json':json_bytes(gaps),'fuentes.json':json_bytes(config)}
    verify(config)
    manifest={'schema_version':1,'fase':6,'outputs':{n:hashlib.sha256(b).hexdigest() for n,b in sorted(payloads.items())},
        'script_sha256':sha(__file__),'config_sha256':sha(config_path),
        'resolver_h5_sha256':s['resolver_h5']['sha256'],'maestro_h5_sha256':s['maestro_h5']['sha256'],
        'checks':acceptance['controles'],'privacidad':'Sin identidades, notas individuales ni conteos de personas deducidos de grupos.'}
    payloads['manifest.json']=json_bytes(manifest);write_immutable(output,payloads)
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fuentes',type=Path,required=True);parser.add_argument('--salida',type=Path,required=True)
    args=parser.parse_args()
    try:print(json.dumps(run(args.fuentes,args.salida),ensure_ascii=False,indent=2))
    except (ValueError,KeyError,OSError) as e:parser.exit(2,str(e)+'\n')


if __name__=='__main__':main()
