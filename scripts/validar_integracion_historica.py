#!/usr/bin/env python3
"""Contrasta ambos consumidores H7 con H5 y todas las consultas del piloto H6."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.consulta_sies_historica import ConsultaHistorica, DESCRIPTOR_SHA256, VERSION
from common.equivalencias_historicas import cargar_maestro, consultar_sies, resolver_umas
from scripts.exportar_consulta_historica import construir_entrega

H6_MANIFEST_SHA = '6d5ef5ccc04cbb28ae87d968a87bc329bb8993255b72ed73302a1e60264d4faa'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+'\n').encode()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validar(consumidor, salida):
    consumidor, salida = Path(consumidor).resolve(), Path(salida).resolve()
    h5 = ROOT/'data/versiones_historicas_sies_umas/fase_5_20261015'
    h6 = ROOT/'data/versiones_historicas_sies_umas/fase_6_20261015'
    require(sha((h6/'manifest.json').read_bytes())==H6_MANIFEST_SHA, 'Manifiesto H6 alterado')
    h6_manifest=json.loads((h6/'manifest.json').read_text())
    names=('consultas_umas.tsv','consultas_sies_anuales.tsv','resultados_contextos_umas.tsv')
    inputs={}
    for name in names:
        raw=(h6/name).read_bytes()
        require(sha(raw)==h6_manifest['outputs'][name], 'Fuente H6 alterada: '+name)
        inputs[name]=list(csv.DictReader(io.StringIO(raw.decode()),delimiter='\t'))
    delivery=construir_entrega()
    for rel,raw in delivery.items():
        for repo in (ROOT,consumidor):
            require((repo/rel).read_bytes()==raw, 'Consumidor no corresponde a la entrega: '+str(repo/rel))
    origin=ConsultaHistorica()
    spec=importlib.util.spec_from_file_location('consumidor_h7_independiente', consumidor/'common/consulta_sies_historica.py')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    destination=module.ConsultaHistorica()
    require(origin.trazabilidad()==destination.trazabilidad(), 'Trazabilidad distinta')
    maestro=cargar_maestro(h5/'maestro.json')
    h5_manifest=json.loads((h5/'manifest.json').read_text())
    require(sha((ROOT/'common/equivalencias_historicas.py').read_bytes())==h5_manifest['scripts_sha256']['common/equivalencias_historicas.py'], 'Resolvedor H5 alterado')
    rows=[]; states=Counter(); weights=Counter(); query_weights={}
    for index,row in enumerate(inputs['consultas_umas.tsv'],start=2):
        params={key:row[key] for key in ('periodo','regimen','codcarpr','nombre_interno','plan_umas','sede_umas','jornada_umas')}
        params['anio']=int(row['anio'])
        expected=resolver_umas(maestro,**params)
        left=origin.consultar_umas(**params); right=destination.consultar_umas(**params)
        require(left==right==expected, 'Resultado UMAS distinto: '+row['consulta_id'])
        require(left['estado']==row['estado_resolucion'], 'Estado UMAS distinto a H6')
        require((left.get('codigo_unico') or '')==row['codigo_unico_resuelto'], 'Código UMAS distinto a H6')
        require(left.get('motivo','')==row['motivo_h5'], 'Motivo UMAS distinto a H6')
        require(sorted({c['codigo_unico'] for c in left.get('candidatos',[])})==json.loads(row['codigos_candidatos']), 'Destinos distintos a H6')
        require(sorted({c['id'] for c in left.get('candidatos',[])})==json.loads(row['candidatos_ids']), 'Candidatos distintos a H6')
        require(left['acredita_asignacion_individual'] is False, 'Asignación individual indebida')
        weight=int(row['filas_reporte']); query_weights[row['consulta_id']]=weight
        states[left['estado']]+=1; weights[left['estado']]+=weight
        rows.append({'tipo':'UMAS','localizador_h6':'consultas_umas.tsv:'+str(index),
                     'consulta_id':row['consulta_id'],'parametros':json.dumps(params,ensure_ascii=False,sort_keys=True),
                     'estado':left['estado'],'resultado_sha256':sha(encoded(left)),
                     'igualdad_h5_avance_caracterizacion':True,'coincide_h6':True,
                     'filas_reporte_umas':weight})
    sies_states=Counter()
    for index,row in enumerate(inputs['consultas_sies_anuales.tsv'],start=2):
        params={'anio':int(row['anio']),'codigo_unico':row['codigo_unico']}
        expected=consultar_sies(maestro,**params)
        left=origin.consultar_sies(**params); right=destination.consultar_sies(**params)
        require(left==right==expected, 'Resultado SIES distinto: '+str(params))
        require(left['estado']==row['estado_consulta'], 'Estado SIES distinto a H6')
        require(left.get('motivo','')==row['motivo'], 'Motivo SIES distinto a H6')
        offer=left.get('oferta_anual',{})
        for source,target in (('nombre_carrera','nombre_anual_oferta'),('nombre_oferta_2026','nombre_oferta_2026'),
                              ('modalidad','modalidad_oferta'),('tipo_plan_sies','tipo_plan_oferta')):
            require((offer.get(source) or '')==row[target], 'Literal SIES distinto a H6: '+target)
        require(left['acredita_asignacion_individual'] is False, 'Asignación individual SIES indebida')
        sies_states[left['estado']]+=1
        rows.append({'tipo':'SIES','localizador_h6':'consultas_sies_anuales.tsv:'+str(index),
                     'consulta_id':str(params['anio'])+'|'+params['codigo_unico'],
                     'parametros':json.dumps(params,ensure_ascii=False,sort_keys=True),
                     'estado':left['estado'],'resultado_sha256':sha(encoded(left)),
                     'igualdad_h5_avance_caracterizacion':True,'coincide_h6':True,'filas_reporte_umas':''})
    contexts=inputs['resultados_contextos_umas.tsv']
    context_weights=Counter(); omitted=Counter()
    for row in contexts:
        if row['estado_adaptacion']=='CONSULTABLE':
            context_weights[row['consulta_id']]+=int(row['filas_reporte'])
        else:
            omitted[row['estado_adaptacion']]+=int(row['filas_reporte'])
    require(dict(context_weights)==query_weights, 'Pesos por consulta no concilian con contextos H6')
    summary={'fase':7,'estado':'INTEGRACION_CONSULTAS_VALIDADA_CON_LIMITES',
             'version':VERSION,'descriptor_sha256':DESCRIPTOR_SHA256,
             'paridad_objeto_completo':True,'consultas_umas':sum(states.values()),
             'consultas_sies':sum(sies_states.values()),'consultas_totales':len(rows),
             'estados_consultas_umas':dict(states),'estados_consultas_sies':dict(sies_states),
             'unidad_umas':'filas de PROMEDIOS representadas; no personas únicas',
             'filas_reporte_consultables':sum(weights.values()),'filas_reporte_por_estado':dict(weights),
             'contextos_h6_preservados':len(contexts),'filas_no_consultadas_h6':dict(omitted),
             'filas_reporte_total':sum(weights.values())+sum(omitted.values()),
             'codigos_sies':len(maestro['universo_sies']),'planes_umas':len(maestro['planes_umas']),
             'reglas_efectivas_acreditadas':len(maestro['reglas_efectivas']),
             'asignacion_historica_automatica_habilitada':False,
             'pipelines_operativos_ejecutados':False,'excel_modificado':False,
             'fuentes_h6':{name:h6_manifest['outputs'][name] for name in names},
             'h6_manifest_sha256':H6_MANIFEST_SHA,
             'archivos_instalados_identicos':{str(rel):sha(raw) for rel,raw in sorted(delivery.items())}}
    stream=io.StringIO(newline='')
    writer=csv.DictWriter(stream,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
    writer.writeheader(); writer.writerows(rows)
    files={'paridad_consultas.tsv':stream.getvalue().encode(),'resumen.json':encoded(summary)}
    manifest={'fase':7,'schema_version':1,'outputs':{n:sha(raw) for n,raw in files.items()},
              'scripts_sha256':{rel:sha((ROOT/rel).read_bytes()) for rel in
                  ('common/consulta_sies_historica.py','scripts/consultar_sies_historico.py',
                   'scripts/exportar_consulta_historica.py','scripts/validar_integracion_historica.py')}}
    files['manifest.json']=encoded(manifest)
    for name,raw in files.items():
        path=salida/name
        require(not path.exists() or path.read_bytes()==raw, 'Salida existente diferente: '+str(path))
    salida.mkdir(parents=True,exist_ok=True)
    for name,raw in files.items():
        if not (salida/name).exists():
            with (salida/name).open('xb') as stream: stream.write(raw)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--consumidor',type=Path,required=True)
    parser.add_argument('--salida',type=Path,required=True)
    args=parser.parse_args()
    try:
        print(json.dumps(validar(args.consumidor,args.salida),ensure_ascii=False,sort_keys=True,indent=2))
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'estado':'VALIDACION_RECHAZADA','motivo':str(exc)},ensure_ascii=False),file=sys.stderr)
        raise SystemExit(1)
