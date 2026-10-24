#!/usr/bin/env python3
"""Lee fuentes UMAS autorizadas; exporta solo agregados de continuidad."""
import ast
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
from common.continuidad_trayectoria import evaluar_trayectorias
from common.versiones_por_cohorte import clave_grupo, resolver_cohorte
from scripts.reconstruir_planes_umas import read_sheet, token

OUT = ROOT/'data/continuidad_trayectoria/20261016'


def digest(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    import pandas as pd
    source_manifest = ROOT/'data/versiones_historicas_sies_umas/fase_4_20261015/fuentes.json'
    metadata = json.loads(source_manifest.read_text())['sources']
    relocation=json.loads((ROOT/'data/versiones_historicas_sies_umas/fase_6_20261015/reubicacion_fuente_promedios.json').read_text())
    if relocation['sha256_historico']!=metadata['promedios']['sha256']:
        raise ValueError('Respaldo PROMEDIOS de otra edición')
    metadata['promedios']={**metadata['promedios'],'path':relocation['ruta_respaldo'],
                          'procedencia_reubicacion':'fase_6_20261015/reubicacion_fuente_promedios.json'}
    source_paths = {}
    for name in ('alumnos','promedios'):
        p=Path(metadata[name]['path'])
        if digest(p)!=metadata[name]['sha256']: raise ValueError('Fuente UMAS alterada: '+name)
        source_paths[name]=p
    # Reutilizar exactamente los helpers de normalización, sin ejecutar el motor.
    rule_path=ROOT/'procesos/caracterizacion/caracterizacion.py'
    tree=ast.parse(rule_path.read_text())
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'_clean_str','token_match_rut'}]
    if len(nodes)!=2: raise ValueError('No se localizó normalizador gobernado')
    scope={'pd':pd,'re':re}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(rule_path),'exec'),scope)
    fields=('RUT','CODCLI','CODCARPR','SEDE','JORNADA','ANOINGRESO','ANOMATRICULA')
    alumnos,_=read_sheet(source_paths['alumnos'],metadata['alumnos']['sheet'],fields)
    prom,_=read_sheet(source_paths['promedios'],metadata['promedios']['sheet'],
                       ('CODCLI','CODCARR','ANO','DESCRIPCION_ESTADO','CONVALIDADO'))
    package=ROOT/'data/versiones_por_cohorte/20261016'
    package_manifest=json.loads((package/'manifest.json').read_text())
    for name in ('grupos_existentes.json','historias_oferta.json'):
        if digest(package/name)!=package_manifest['salidas'][name]: raise ValueError('Paquete previo alterado')
    groups={g['clave']:g for g in json.loads((package/'grupos_existentes.json').read_text())}
    histories=json.loads((package/'historias_oferta.json').read_text())
    dur_path=ROOT/'DURACION_ESTUDIOS.tsv'
    if digest(dur_path)!='701025451acf2f84078cf185d6ae0be0d8483d37e3b3e9483f70070397aebc6e':
        raise ValueError('Catálogo de nivel alterado')
    levels=defaultdict(set)
    for row in csv.DictReader(io.StringIO(dur_path.read_text()),delimiter='\t'):
        levels[row['CODIGO_UNICO']].add(row['NIVEL_CARRERA'])
    academic=defaultdict(set)
    excluded=0
    for row in prom:
        state=token(row['DESCRIPCION_ESTADO']).upper()
        convalidated=token(row['CONVALIDADO']).upper()
        if state not in {'APROBADO','REPROBADO'} or convalidated in {'S','SI','SÍ','1','TRUE'}:
            excluded+=1;continue
        year=token(row['ANO'])
        if year.isdigit() and 2007<=int(year)<=2026:
            academic[(token(row['CODCLI']),token(row['CODCARR']))].add(int(year))
    records=[]; mapping={}; outside=0; ambiguous_profile=0
    for row in alumnos:
        key=clave_grupo(token(row['CODCARPR']),token(row['SEDE']),token(row['JORNADA']))
        g=groups.get(key)
        plan_types={p[1] for p in g['perfiles_duracion_tipo']} if g else set()
        if len(plan_types)>1: ambiguous_profile+=1
        level_set={level for code in (g['codigos_base'] if g else []) for level in levels[code]}
        years=set(academic[(token(row['CODCLI']),token(row['CODCARPR']))])
        matricula=token(row['ANOMATRICULA'])
        if matricula.isdigit() and 2007<=int(matricula)<=2026: years.add(int(matricula))
        if matricula.isdigit() and int(matricula)>2026:outside+=1
        # No evaluar como objetivo las filas del corte 2027, pero conservarlas como contexto.
        record={'indice':row['_fila'],'persona':scope['token_match_rut'](row['RUT']),
                'codcli':token(row['CODCLI']),'carrera':token(row['CODCARPR']),
                'continuidad':plan_types=={'3'},'tecnico':level_set=={'1'},
                'anios_observados':sorted(years),'anoingreso':token(row['ANOINGRESO'])}
        records.append(record);mapping[row['_fila']]={'grupo':g,'key':key,'matricula':matricula}
    evaluated=evaluar_trayectorias(records)
    aggregate=Counter();origins=Counter();states=Counter();changes=Counter()
    for item in evaluated:
        ref=mapping[item['indice']]
        if ref['matricula'].isdigit() and int(ref['matricula'])>2026:continue
        year=item['primer_anio_observado_carrera']
        proposal=resolver_cohorte(ref['grupo'],histories,anoingreso=year)
        original=item['anoingreso_original']
        old=resolver_cohorte(ref['grupo'],histories,anoingreso=int(original) if original.isdigit() else None)
        key=(ref['key'],original,year,item['origen'],item['estado_fecha'],proposal['estado'],
             proposal['codigo_propuesto'],old['estado'],old['codigo_propuesto'])
        aggregate[key]+=1;origins[item['origen']]+=1;states[proposal['estado']]+=1
        changes['fecha_observada_distinta_de_anoingreso' if year is not None and str(year)!=original
                else 'sin_cambio_observable_o_sin_fecha']+=1
    aggregated=[]
    for key,count in sorted(aggregate.items(),key=lambda kv:json.dumps(kv[0],ensure_ascii=False)):
        group,old_year,year,origin,date_state,state,code,old_state,old_code=key
        aggregated.append({'grupo':json.loads(group),'anoingreso_original':old_year,
                           'primer_anio_observado_continuidad':year,'origen':origin,
                           'estado_fecha':date_state,'estado_propuesta_observada':state,
                           'codigo_propuesto_observacion':code,'estado_ensayo_anterior':old_state,
                           'codigo_ensayo_anterior':old_code,'filas_datosalumnos':count})
    summary={'regla':'INT-CONTINUIDAD-INGRESO-002','filas_datosalumnos_leidas':len(alumnos),
             'filas_promedios_leidas':len(prom),'filas_notas_no_usadas_como_inicio':excluded,
             'filas_continuidad_evaluadas':sum(origins.values()),'clasificacion_origen':dict(origins),
             'ensayo_version_con_fecha_observada':dict(states),'comparacion_fechas':dict(changes),
             'filas_corte_posterior_2026_no_objetivo':outside,'filas_tipo_plan_ambiguo':ambiguous_profile,
             'ingresos_efectivos_certificados':0,'procedencias_externas_certificadas':0,
             'unidad':'Filas de DatosAlumnos; no personas únicas ni totales de matrícula SIES',
             'limite':'Primera observación disponible en carrera, no año cero efectivo confirmado. No se modifica ANOINGRESO ni se activa asignación oficial.'}
    for name,p in source_paths.items():
        if digest(p)!=metadata[name]['sha256']:raise ValueError('Fuente cambió durante lectura')
    outputs={'resumen.json':summary,'trayectorias_agregadas.json':aggregated,
             'fuentes.json':{'umas':{k:metadata[k] for k in source_paths},
                             'normalizador':{'path':str(rule_path.relative_to(ROOT)),'sha256':digest(rule_path)},
                             'catalogo_nivel_sha256':digest(dur_path),'paquete_cohortes_manifest_sha256':digest(package/'manifest.json'),
                             'identidades_exportadas':False}}
    encoded={name:(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode() for name,data in outputs.items()}
    for name,raw in encoded.items():
        if (OUT/name).exists() and (OUT/name).read_bytes()!=raw:raise ValueError('Salida distinta: '+name)
    OUT.mkdir(parents=True,exist_ok=True)
    for name,raw in encoded.items():(OUT/name).write_bytes(raw)
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':main()
