#!/usr/bin/env python3
"""Construye H5 con candidatos separados de reglas plan/período acreditadas.

Contrato: docs/fase_5_maestro_equivalencias.md. Solo dimensiones académicas;
no importa motores oficiales ni asigna mallas a personas.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)+'\n').encode()


def key(*parts):
    """Clave sin colisiones de separadores; sin alias ni normalización nominal."""
    return json.dumps(list(parts), ensure_ascii=False, separators=(',', ':'))


def identifier(prefix, *parts):
    return prefix + hashlib.sha256(key(*parts).encode()).hexdigest()[:24]


def components(code):
    m = re.fullmatch(r'I(\d+)S(\d+)C(\d+)J(\d+)V(\d+)', code)
    if not m:
        raise ValueError('Código moderno inválido: '+code)
    return dict(zip(('institucion','sede','carrera','jornada','version'), m.groups()))


def read_tsv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError('Encabezados inválidos: '+str(path))
        rows = list(reader)
    if any(None in row or None in row.values() for row in rows):
        raise ValueError('Fila irregular: '+str(path))
    return rows


def tsv_bytes(rows, empty_fields=()):
    fields = list(dict.fromkeys(k for row in rows for k in row)) or list(empty_fields)
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=fields, delimiter='\t', lineterminator='\n')
    writer.writeheader()
    for row in rows:
        writer.writerow({k:json.dumps(v,ensure_ascii=False,sort_keys=True)
                         if isinstance(v,(dict,list)) else v for k,v in row.items()})
    return out.getvalue().encode()


def verify_sources(config):
    if config['schema_version'] != 1 or config['periodo_objetivo'] != [2007,2026]:
        raise ValueError('Contrato de fuente fuera del ámbito H5')
    for source in [*config['sources'].values(), *config['referencias_congeladas']]:
        if sha(source['path']) != source['sha256']:
            raise ValueError('SHA-256 distinto: '+source['path'])
    # Las proyecciones deben pertenecer a sus manifiestos de cierre previos.
    for phase, ids in ((2,('mrun_anual',)),
                       (3,('oferta_anual','cobertura_sies')),
                       (4,('catalogo_planes','cobertura_planes','observaciones_planes'))):
        manifest = json.loads(Path(config['sources'][f'manifest_fase{phase}']['path']).read_text())
        for source_id in ids:
            source = config['sources'][source_id]
            if manifest['outputs'].get(Path(source['path']).name) != source['sha256']:
                raise ValueError('Proyección no pertenece al manifiesto: '+source_id)


def make_offers(rows):
    offers = []
    current = {r['CODIGO_UNICO']:r['NOMBRE_CARRERA'] for r in rows if r['ANO']=='OFE_2026'}
    seen = set()
    for n, r in enumerate(rows,2):
        if not re.fullmatch(r'OFE_20\d\d',r['ANO']):
            raise ValueError('Año SIES inválido')
        year = int(r['ANO'][4:]); code = r['CODIGO_UNICO']; c = components(code)
        if not 2010 <= year <= 2026 or c['institucion']!='162':
            raise ValueError('Oferta fuera del ámbito')
        if (year,code) in seen:
            raise ValueError('Oferta anual repetida')
        seen.add((year,code))
        for target,source in [('institucion','CODIGO_IES'),('sede','CODIGO_SEDE'),
                              ('carrera','CODIGO_CARRERA'),('version','VERSION')]:
            if c[target] != r[source]:
                raise ValueError('Componentes SIES contradictorios')
        offers.append({'anio':year,'codigo_unico':code,'componentes_sies':c,
            'nombre_carrera':r['NOMBRE_CARRERA'],'nombre_oferta_2026':current.get(code),
            'jornada':r['JORNADA'],'modalidad':r['MODALIDAD'] or None,
            'modalidad_literal':r['MODALIDAD'],
            'tipo_plan_sies':r['TIPO_CARRERA'],'plan_especial':r['PLAN_ESPECIAL'],
            'duracion_estudios':r['DURACION_ESTUDIOS'],'duracion_total':r['DURACION_TOTAL'],
            'vigencia':r['VIGENCIA'],'nivel_global':r['NIVEL_GLOBAL'],
            'fuente':{'id':'oferta_anual','localizador':f'fila TSV {n}',
                      'original_id':'historico_xlsx','hoja':r['hoja_origen'],
                      'fila_original':int(r['fila_origen'])}})
    return sorted(offers,key=lambda r:(r['anio'],r['codigo_unico']))


def program_relations(snapshot, sources, current_codes):
    if snapshot['anio'] != 2026 or snapshot['sedes_internas'] != {'RE':'2','CO':'3'}:
        raise ValueError('Snapshot ajeno al contrato 2026')
    sedes = {v:k for k,v in snapshot['sedes_internas'].items()}
    jornadas = {'1':'D','2':'V','4':'O'}  # J3 no se equipara a O.
    groups = {}
    for offer in snapshot['oferta']:
        code = offer['codigo_unico']; c = components(code)
        for field in ('sede','carrera','jornada','version'):
            if c[field] != offer[field]:
                raise ValueError('Snapshot inconsistente')
        for e in offer['equivalencias']:
            expected = sources['duracion']
            p = Path(e['fuente']['path'])
            if not p.is_absolute(): p = ROOT / p
            if str(p) != expected['path'] or e['fuente']['sha256'] != expected['sha256']:
                raise ValueError('Equivalencia no respaldada por fuente congelada')
            if e['metodo'] != 'CATALOGO_MU2026':
                raise ValueError('Método fuera del contrato H5')
            internal, name = e['codcarpr'].strip(), e['nombre_interno'].strip()
            if not internal or not name or internal.upper() in {'NULL','NONE','NAN'}:
                raise ValueError('Equivalencia incompleta')
            k = (internal,name,code)
            if k not in groups:
                groups[k] = {'id':identifier('EP-',*k),'codcarpr':internal,
                    'nombre_interno':name,
                    'semantica_nombre':'NOMBRE_CARRERA del catálogo operativo; no acreditación de nombre DatosAlumnos',
                    'codigo_unico':code,'componentes_sies':c,
                    'sede_umas':sedes.get(c['sede']), 'jornada_umas':jornadas.get(c['jornada']),
                    'tipo_plan_sies_operativo':offer['plan'],'ambito_candidato':2026,
                    'presencia_oferta_2026':code in current_codes,
                    'estado':'RELACION_OPERATIVA_SIN_PLAN_NI_VIGENCIA',
                    'fuentes':[{'id':'snapshot_2026',
                        'localizador':f"oferta[codigo_unico={code}].equivalencias[codcarpr={internal},nombre_interno={name}]"}],
                    'filas_duracion':[]}
            groups[k]['filas_duracion'].append(e['fila_fuente'])
    for r in groups.values():
        r['filas_duracion'] = sorted(set(r['filas_duracion']))
        r['fuentes'].append({'id':'duracion','localizador':{'filas':r['filas_duracion']}})
    return sorted(groups.values(),key=lambda r:r['id'])


def plan_candidates(catalog, relations, observations):
    by_career = defaultdict(list)
    for r in relations: by_career[(r['codcarpr'],r['sede_umas'])].append(r)
    by_plan = defaultdict(list)
    for n, row in enumerate(observations,2):
        by_plan[row['PLAN_DE_ESTUDIO']].append((n,row))
    candidates = []
    for p in catalog:
        if len(p['carreras_internas']) != 1 or len(p['sedes']) != 1:
            # No escoger un contexto entre varios. Cobertura conserva el plan.
            continue
        career, sede = p['carreras_internas'][0],p['sedes'][0]
        names = sorted({x.strip() for x in p['nombres_carrera']})
        for relation in by_career[(career,sede)]:
            jornada = relation['jornada_umas']
            obs = [(n,r) for n,r in by_plan[p['CODPESTUD']]
                   if r['CODCARR']==career and jornada is not None and r['JORNADA']==jornada
                   and r['estado_observacion']=='OBSERVACION_CON_ANIO']
            fields = [career,p['CODPESTUD'],sede,jornada,relation['nombre_interno'],relation['codigo_unico']]
            candidates.append({'id':identifier('CP-',*fields),
                'clave_candidata':key(*fields),'codcarpr':career,'plan_umas':p['CODPESTUD'],
                'sede_umas':sede,'jornada_umas':jornada,
                'nombre_interno':relation['nombre_interno'],'nombre_plan_catalogo':names,
                'estado_nombre_catalogo':'IGUAL_LITERAL' if relation['nombre_interno'] in names else 'DIFERENTE_SIN_ALIAS',
                'codigo_unico':relation['codigo_unico'],
                'componentes_sies':relation['componentes_sies'],
                'ambito_candidato':2026,'presencia_oferta_2026':relation['presencia_oferta_2026'],
                'estado':'PENDIENTE_EQUIVALENCIA_PLAN_Y_AMBITO_TEMPORAL',
                'habilitada_para_resolver':False,'periodos_acreditados':[],
                'anios_actividad_observada_jornada':sorted({int(r['ANO']) for _,r in obs}),
                'filas_actividad_observada_jornada':sum(int(r['filas_reporte']) for _,r in obs),
                'limite_observacion':'Actividad del reporte; no asignación efectiva ni vigencia de equivalencia',
                'equivalencias_ids':[relation['id']],
                'fuentes':[{'id':'catalogo_planes','localizador':{'CODPESTUD':p['CODPESTUD'],
                           'filas_originales':p['filas_fuente']}},
                          {'id':'observaciones_planes','localizador':{'filas_tsv':[n for n,_ in obs]}}]})
    if len({r['id'] for r in candidates}) != len(candidates):
        raise ValueError('Candidatos repetidos')
    return sorted(candidates,key=lambda r:r['id'])


def operational_differences(snapshot, offers):
    current = {r['codigo_unico']:r for r in offers if r['anio']==2026}
    vigencia = {'1':'Vigente con estudiantes nuevos','2':'Vigente sin estudiantes nuevos','3':'No vigente'}
    plans = {'1':'Plan Regular','3':'Plan Regular de Continuidad'}
    modalidades = {'1':'Presencial','2':'Semipresencial','3':'No Presencial'}
    rows = []
    for o in snapshot['oferta']:
        if o['codigo_unico'] not in current: continue
        h = current[o['codigo_unico']]
        for field, value in [('vigencia',vigencia[o['vigencia']]),
                             ('modalidad',modalidades[o['modalidad_codigo']]),
                             ('tipo_plan_sies',plans.get(o['plan'],o['plan'])),
                             ('duracion_estudios',o['duracion_estudios']),
                             ('duracion_total',o['duracion_total'])]:
            if value != h[field]:
                rows.append({'codigo_unico':o['codigo_unico'],'campo':field,
                    'valor_operativo':value,'valor_oferta_anual':h[field],
                    'fuente_operativa':'snapshot_2026','fuente_oferta':h['fuente'],
                    'criterio':'Maestro usa atributo de oferta anual; congelado no se modifica'})
    return rows


def build(config):
    source = config['sources']
    def read(name):return json.loads(Path(source[name]['path']).read_text())
    def tsv(name):return read_tsv(source[name]['path'])
    offers = make_offers(tsv('oferta_anual')); current = {o['codigo_unico'] for o in offers if o['anio']==2026}
    snapshot = read('snapshot_2026'); catalog = read('catalogo_planes')
    relations = program_relations(snapshot,source,current)
    candidates = plan_candidates(catalog,relations,tsv('observaciones_planes'))
    rules_document = read('registro_reglas')
    if rules_document['schema_version'] != 1:
        raise ValueError('Registro efectivo desconocido')
    rules = rules_document['reglas_efectivas']
    sies = []
    for row in tsv('cobertura_sies'):
        code = row['codigo_unico']
        sies.append({**row,'nombre_literal_oferta_2026':row['nombre_literal_oferta_2026'] or None,
            'nombre_2026_estado':'OFERTA_2026_LITERAL' if code in current else 'SIN_OFERTA_2026_OBSERVADA',
            'equivalencias_programa_2026':sum(r['codigo_unico']==code for r in relations),
            'candidatos_plan':sum(r['codigo_unico']==code for r in candidates),
            'reglas_efectivas':sum(r['codigo_unico']==code for r in rules),
            'sector_ipss':None,'estado_sector_ipss':'NO_EVALUADO_EN_H5'})
    plans = []
    json_fields = ('contextos_catalogo','nombres_internos_catalogo','carreras_promedios',
                   'jornadas_promedios','anios_actividad_observada')
    for row in tsv('cobertura_planes'):
        p = {**row,**{f:json.loads(row[f]) for f in json_fields}}
        cs = [c for c in candidates if c['plan_umas']==row['CODPESTUD']]
        p.update({'candidatos_plan_sies':len(cs),
            'codigos_sies_candidatos':sorted({c['codigo_unico'] for c in cs}),
            'reglas_efectivas':sum(r['plan_umas']==row['CODPESTUD'] for r in rules),
            'estado_equivalencia':'PENDIENTE_EVIDENCIA' if cs else 'SIN_CANDIDATO_EN_FUENTE_2026',
            'asignacion_temporal_acreditada':False})
        plans.append(p)
    if {x['codigo_unico'] for x in sies} != ({x['codigo_unico'] for x in offers} | {x['codigo_unico'] for x in tsv('mrun_anual')}):
        raise ValueError('Pérdida de cobertura SIES')
    if not {r['CODPESTUD'] for r in catalog} <= {r['CODPESTUD'] for r in plans}:
        raise ValueError('Pérdida de cobertura UMAS')
    master = {'schema_version':1,'periodo_objetivo':[2007,2026],
        'fuentes':source,'oferta_anual':offers,'mrun_anual':tsv('mrun_anual'),
        'universo_sies':sies,'planes_umas':plans,'equivalencias_programa_2026':relations,
        'candidatos_plan_sies':candidates,'reglas_efectivas':rules,
        'asignacion_individual':'NO_ACREDITADA_POR_ESTE_MAESTRO',
        'sector_ipss':'NO_EVALUADO_EN_H5; no es selector de versión',
        'mapas_lectura_candidato_2026':{'sedes':{'RE':'2','CO':'3'},'jornadas':{'D':'1','V':'2','O':'4'}}}
    from common.equivalencias_historicas import validar_maestro
    validar_maestro(master)
    summary = {'fase':5,'estado':'IMPLEMENTADA_CON_EQUIVALENCIAS_PENDIENTES',
        'codigos_sies':len(sies),'filas_oferta_anual':len(offers),'filas_mrun_anual':len(master['mrun_anual']),
        'planes_umas':len(plans),'planes_catalogo':len(catalog),
        'relaciones_operativas_2026':len(relations),'candidatos_plan_sies':len(candidates),
        'planes_con_candidatos':len({c['plan_umas'] for c in candidates}),
        'planes_sin_candidatos':sum(not p['candidatos_plan_sies'] for p in plans),
        'reglas_efectivas_acreditadas':len(rules),
        'candidatos_por_estado_nombre':dict(Counter(c['estado_nombre_catalogo'] for c in candidates)),
        'candidatos_sin_jornada_umas_acreditada':sum(c['jornada_umas'] is None for c in candidates),
        'candidatos_sin_oferta_2026':sum(not c['presencia_oferta_2026'] for c in candidates),
        'limite':'Candidato único no acredita malla ni período. No se ha ejecutado el piloto H6 ni integrado consumidores.'}
    return master, summary, operational_differences(snapshot,offers)


def examples(master):
    from common.equivalencias_historicas import consultar_sies, resolver_umas
    rows = []
    cases = [('ILOG','ILOG20241','INGENIERIA EN LOGISTICA','O',2026),
             ('CILOG','CILOG20241','INGENIERIA EN LOGISTICA','O',2026),
             ('NATP','NATP20251','NATUROPATIA','V',2026),
             ('IECIRE','IECIRE20211','INGENIERIA DE EJECUCION EN COMPUTACION E INFORMATICA','V',2019),
             ('ASREOL','ASREOL','TECNICO EN ANALISIS DE SISTEMA','O',2026)]
    observations = read_tsv(master['fuentes']['observaciones_planes']['path'])
    for career,plan,name,jornada,year in cases:
        regime = 'TRIMESTRAL' if plan in {'ILOG20241','CILOG20241','NATP20251'} else 'SEMESTRAL'
        query = dict(anio=year,periodo='1',regimen=regime,codcarpr=career,
            nombre_interno=name,plan_umas=plan,sede_umas='RE',jornada_umas=jornada)
        locators = [n for n,r in enumerate(observations,2) if r['PLAN_DE_ESTUDIO']==plan
                    and r['CODCARR']==career and r['JORNADA']==jornada and r['ANO']==str(year)
                    and r['PERIODO']=='1' and r['REGIMEN']==regime]
        rows.append({'tipo':'CONSULTA_ACADEMICA_ILUSTRATIVA','entrada':query,
            'limite':'Sin identidad; período/régimen de consulta no acredita asignación del plan',
            'observacion_periodo':{'fuente':'observaciones_planes','filas_tsv':locators,
                'estado':'OBSERVADA_EN_REPORTE' if locators else 'CONSULTA_SIN_OBSERVACION_EN_ESE_PERIODO'},
            'resultado':resolver_umas(master,**query)})
    for year,code in [(2026,'I162S2C77J4V2'),(2026,'I162S2C90J2V1'),
                      (2020,'I162S2C46J2V2'),(2008,'I162M2008N1')]:
        rows.append({'tipo':'CONSULTA_SIES_EXACTA','entrada':{'anio':year,'codigo_unico':code},
            'resultado':consultar_sies(master,anio=year,codigo_unico=code)})
    return rows


def write_immutable(output, payloads):
    output = Path(output)
    for name, data in payloads.items():
        path = output/name
        if path.exists() and path.read_bytes()!=data:
            raise ValueError('Salida existente diferente; usar destino nuevo: '+str(path))
    output.mkdir(parents=True, exist_ok=True)
    for name,data in payloads.items():
        if not (output/name).exists(): (output/name).write_bytes(data)


def run(config_path, output):
    config_path = Path(config_path); config = json.loads(config_path.read_text())
    verify_sources(config)
    master,summary,differences = build(config)
    payloads = {'maestro.json':json_bytes(master),'resumen.json':json_bytes(summary),
        'fuentes.json':json_bytes(config),
        'equivalencias_programa_2026.tsv':tsv_bytes(master['equivalencias_programa_2026']),
        'candidatos_plan_sies.tsv':tsv_bytes(master['candidatos_plan_sies']),
        'cobertura_sies.tsv':tsv_bytes(master['universo_sies']),
        'cobertura_planes.tsv':tsv_bytes(master['planes_umas']),
        'reglas_efectivas.json':json_bytes(master['reglas_efectivas']),
        'ejemplos_consulta.json':json_bytes(examples(master)),
        'diferencias_catalogo_operativo.tsv':tsv_bytes(differences,('codigo_unico','campo','valor_operativo','valor_oferta_anual')),
        'excepciones.json':json_bytes({'planes_sin_candidatos':[p['CODPESTUD'] for p in master['planes_umas'] if not p['candidatos_plan_sies']],
            'candidatos_nombre_diferente':[c['id'] for c in master['candidatos_plan_sies'] if c['estado_nombre_catalogo']!='IGUAL_LITERAL'],
            'candidatos_jornada_sin_mapa':[c['id'] for c in master['candidatos_plan_sies'] if c['jornada_umas'] is None],
            'candidatos_sin_oferta_2026':[c['id'] for c in master['candidatos_plan_sies'] if not c['presencia_oferta_2026']],
            'oferta_sin_cobertura_anual':[2007,2008,2009],
            'plan_sies_y_periodo':'SIN_REGLAS_ACREDITADAS' if not master['reglas_efectivas'] else 'VER_REGISTRO',
            'asignacion_individual':'PENDIENTE_HISTORIA_EFECTIVA'})}
    verify_sources(config)
    manifest = {'schema_version':1,'fase':5,
        'outputs':{n:hashlib.sha256(b).hexdigest() for n,b in sorted(payloads.items())},
        'config_sha256':sha(config_path),
        'scripts_sha256':{str(p.relative_to(ROOT)):sha(p) for p in
            [Path(__file__).resolve(),ROOT/'common/equivalencias_historicas.py',ROOT/'scripts/consultar_equivalencias_historicas.py']},
        'checks':{'fuentes_sin_cambios':True,'cobertura_sies_preservada':True,'catalogo_planes_preservado':True},
        'privacidad':'Dimensiones académicas; sin identidades ni notas individuales.'}
    payloads['manifest.json'] = json_bytes(manifest)
    write_immutable(output,payloads)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fuentes',type=Path,required=True)
    parser.add_argument('--salida',type=Path,required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.fuentes,args.salida),ensure_ascii=False,indent=2))
    except (ValueError,KeyError,OSError) as error:
        parser.exit(2,str(error)+'\n')


if __name__ == '__main__':
    main()
